import os
import json
import time
import re
from urllib import request, error as urllib_error
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

# --- Gemini Config ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Initialize the new Gemini Client
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

# --- Ollama Config (Optimized for Intel i5 Shared-GPU Laptop) ---
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
OLLAMA_API_PATH = os.getenv("OLLAMA_API_PATH", "/v1/chat/completions")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
OLLAMA_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", "2"))


def sanitize_dental_data(products):
    """Clean baseline raw strings/numbers and fix inverted prices before AI parsing."""
    cleaned_products = []
    for p in products:
        # Create a clean dictionary copy so we don't accidentally mutate immutable db row types
        item = dict(p) if not isinstance(p, dict) else p.copy()

        # Handle mapping key variations between your raw dictionary entries and DB tuples
        old_price_key = "old_price" if "old_price" in item else "base_price"
        new_price_key = "new_price" if "new_price" in item else "promo_price"

        # Strip currency symbols, replace commas, extract floating point numbers safely
        base = (
            float(
                re.sub(r"[^\d.]", "", str(item.get(old_price_key, 0)).replace(",", "."))
            )
            if item.get(old_price_key)
            else 0.0
        )
        promo = (
            float(
                re.sub(r"[^\d.]", "", str(item.get(new_price_key, 0)).replace(",", "."))
            )
            if item.get(new_price_key)
            else 0.0
        )

        # Auto-correct flipped data-entry entry errors (base price less than promo price)
        if base < promo and base > 0:
            base, promo = promo, base

        item["name"] = item.get("name", "Unknown Product")
        item["website"] = (
            item.get("website") or item.get("site") or item.get("source_site") or "N/A"
        )
        item["promo_price"] = promo
        item["discount_percent"] = (
            round(((base - promo) / base) * 100, 1) if base > 0 else 0.0
        )
        item["category"] = item.get("category") or "Други"
        cleaned_products.append(item)
    return cleaned_products


def build_unified_prompt(raw_products_list) -> str:
    """Sanitizes raw products data and builds a clean structured single prompt injection."""
    # Runtime Guard: If a pre-constructed string prompt is provided by the endpoint, return it directly
    if isinstance(raw_products_list, str):
        return raw_products_list

    # 1. Clear baseline mathematical errors out of the data payload
    sanitized_data = sanitize_dental_data(raw_products_list)

    # 2. Strict Filter: Drop any items that don't meet a real 15% threshold
    valid_items = [p for p in sanitized_data if p.get("discount_percent", 0) >= 15.0]

    # 3. Serialize raw items array into clean readable markdown layout items
    data_lines = []
    for p in valid_items:
        line = f"- {p.get('name')} | {p.get('website')} | {p.get('promo_price', 0):.2f} лв. | Отстъпка: {p.get('discount_percent', 0)}% | Категория: {p.get('category')}"
        data_lines.append(line)

    data_block = "\n".join(data_lines)

    # 4. Return structural instruction block
    return f"""[SYSTEM INSTRUCTIONS]
You are an expert dental supply analyst. Analyze the verified product data provided below.
Task: Organize these items into a clean markdown report written in Bulgarian.

Group the items accurately under these exact headings based on their category:
### **Композити и Бондинг агенти**
### **Глас-йономери**
### **Ендодонтия и Биокерамика**
### **CAD-CAM Материали**
### **Инструменти и Консумативи за полиране**

Formatting per product line: * [Product Name] | [Website] | [Promo Price] лв. | [Discount]%
If a category has no items, output: *В текущата селекция няма налични продукти с отстъпка > 15%.*

At the end, append a section named "### **ТОП 3 препоръки за най-изгодни покупки:**" listing the 3 highest discounts with a short professional/economic justification in Bulgarian.

[VERIFIED DATA]
{data_block}"""


def generate_ai_report(products_raw_data, provider: str = None):
    """Accepts either a raw database list or a string prompt, sanitizes data errors, and constructs the report."""

    # Default to gemini in 100% cloud environments
    if not provider:
        provider = "gemini"
    else:
        provider = provider.lower().strip()

    # Dynamically builds prompt strings or directly passes input strings through
    prompt_text = build_unified_prompt(products_raw_data)

    if provider == "gemini":
        try:
            if client:
                return _generate_gemini_report(prompt_text)
            else:
                raise RuntimeError("Gemini client is not configured (missing API key).")
        except Exception as e:
            # Fallback to Ollama only if specifically running on local with Ollama active
            print(f"Gemini failed, falling back to Ollama: {e}")
            try:
                return _generate_ollama_report(prompt_text)
            except Exception:
                pass
            raise e

    # Ollama priority (when provider is "ollama")
    try:
        return _generate_ollama_report(prompt_text)
    except Exception as e:
        print(f"Ollama failed, falling back to Gemini: {e}")
        if client:
            try:
                return _generate_gemini_report(prompt_text)
            except Exception:
                pass
        raise e


def _generate_gemini_report(prompt_text: str):
    print(f"Using New Gemini SDK ({GEMINI_MODEL}) for analysis...")

    if client is None:
        raise RuntimeError(
            "Gemini client is uninitialized. Verify your GEMINI_API_KEY."
        )

    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt_text)
    if response and response.text:
        return response.text.strip(), "gemini"
    raise RuntimeError("Empty response from Gemini")


def _generate_ollama_report(prompt_text: str):
    """Internal helper for Ollama generation optimized for Qwen 1.5B."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.2,
        "options": {
            "num_ctx": 8192,  # Give it an 8k context window so text fits safely
            "num_predict": 1000,  # High limit to allow complete Bulgarian summaries
        },
    }
    data = json.dumps(payload).encode("utf-8")
    url = f"{OLLAMA_HOST}{OLLAMA_API_PATH}"

    last_exc = None
    for attempt in range(OLLAMA_MAX_RETRIES + 1):
        req = request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        start = time.time()
        try:
            with request.urlopen(req, timeout=OLLAMA_TIMEOUT_SECONDS) as resp:
                body = resp.read().decode("utf-8")
                response = json.loads(body)
                if "choices" in response and len(response["choices"]) > 0:
                    choice = response["choices"][0]
                    content = choice.get("message", {}).get("content")
                    if content:
                        return content.strip(), "ollama"
                    return choice.get("text", "").strip(), "ollama"
                raise RuntimeError(
                    f"Ollama returned unexpected response (status={resp.getcode()}): {response}"
                )
        except urllib_error.HTTPError as e:
            body = (
                e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else ""
            )
            code = getattr(e, "code", None)
            last_exc = RuntimeError(f"Ollama HTTP error {code}: {body}")
            if code and 400 <= code < 500:
                break
        except Exception as e:
            last_exc = RuntimeError(f"Ollama request failed: {type(e).__name__}: {e}")
            if attempt < OLLAMA_MAX_RETRIES:
                time.sleep(1 + attempt)
                continue
        finally:
            elapsed = time.time() - start
            print(
                f"Ollama attempt {attempt + 1}/{OLLAMA_MAX_RETRIES + 1} elapsed={elapsed:.2f}s url={url}"
            )
    if last_exc:
        raise last_exc
    raise RuntimeError("Ollama request failed without exception")
