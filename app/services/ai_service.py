import os
import json
import time
import re
from urllib import request
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(override=True)

# --- Gemini Config ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Configure classic developer GenerativeAI SDK
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY, transport="rest")

# --- Ollama Config (Local Offline LLM) ---
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
OLLAMA_API_PATH = os.getenv("OLLAMA_API_PATH", "/v1/chat/completions")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
OLLAMA_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", "2"))


def sanitize_dental_data(products):
    """Clean baseline raw strings/numbers and fix inverted prices before AI parsing."""
    cleaned_products = []
    for p in products:
        # Create a clean dictionary copy supporting SQLAlchemy Row mappings and dictionaries
        if hasattr(p, "_mapping"):
            item = dict(p._mapping)
        elif isinstance(p, dict):
            item = p.copy()
        else:
            try:
                item = dict(p)
            except Exception:
                item = {}

        # Handle mapping key variations between your raw dictionary entries and DB tuples
        old_price_key = "old_price" if "old_price" in item else "base_price"
        new_price_key = "new_price" if "new_price" in item else "promo_price"

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

        # Auto-correct flipped data-entry entry errors
        if base < promo and base > 0:
            base, promo = promo, base

        item["name"] = item.get("name", "Unknown Product")
        item["website"] = (
            item.get("website") or item.get("site") or item.get("source_site") or "N/A"
        )
        item["old_price"] = base
        item["promo_price"] = promo
        item["discount_percent"] = (
            round(((base - promo) / base) * 100, 1) if base > 0 else 0.0
        )
        item["category"] = item.get("category") or "Други"
        cleaned_products.append(item)
    return cleaned_products


def build_unified_prompt(raw_products_list) -> str:
    """Sanitizes raw products data and builds a clean structured single prompt injection."""
    if isinstance(raw_products_list, str):
        return raw_products_list

    sanitized_data = sanitize_dental_data(raw_products_list)
    valid_items = [p for p in sanitized_data if p.get("discount_percent", 0) >= 15.0]

    # Calculate exact total savings directly in Python for 100% mathematical accuracy
    total_savings = sum(max(p.get("old_price", 0) - p.get("promo_price", 0), 0) for p in valid_items)

    data_lines = []
    for p in valid_items:
        line = f"- {p.get('name')} | {p.get('website')} | {p.get('promo_price', 0):.2f} лв. | Отстъпка: {p.get('discount_percent', 0)}% (Стара цена: {p.get('old_price', 0):.2f} лв.) | Категория: {p.get('category')}"
        data_lines.append(line)

    data_block = "\n".join(data_lines)

    return f"""[SYSTEM INSTRUCTIONS]
You are an expert dental supply analyst. Analyze the verified product data provided below.
Task: Organize these items into a clean markdown report written in Bulgarian.

At the very top of the report, you MUST output this exact heading with the calculated sum of savings:
## 🎁 **Общо спестена сума от текущите отстъпки: {total_savings:.2f} лв.**
*(Посочете, че това е сумата, спестена при закупуване на един брой от всеки намален продукт спрямо редовните цени).*

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
    """Accepts either a raw database list or a string prompt and synthesizes the report using Gemini or Ollama."""
    # Default to local Ollama if no Gemini Key is set, or if explicitly requested
    if not provider:
        provider = "ollama" if not GEMINI_API_KEY else "gemini"
    else:
        provider = provider.lower().strip()

    prompt_text = build_unified_prompt(products_raw_data)

    if provider == "gemini":
        try:
            if GEMINI_API_KEY:
                return _generate_gemini_report(prompt_text)
            else:
                raise RuntimeError("Gemini API key is unconfigured.")
        except Exception as e:
            print(f"Gemini analysis failed, falling back to local Ollama: {e}")
            try:
                return _generate_ollama_report(prompt_text)
            except Exception:
                pass
            raise e

    # Default to local offline Ollama
    try:
        return _generate_ollama_report(prompt_text)
    except Exception as e:
        print(f"Local Ollama analysis failed, falling back to Gemini: {e}")
        if GEMINI_API_KEY:
            try:
                return _generate_gemini_report(prompt_text)
            except Exception:
                pass
        raise e


def _generate_gemini_report(prompt_text: str):
    print(f"Using Classic GenerativeAI SDK ({GEMINI_MODEL}) for analysis...")

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "Gemini API key is unconfigured. Verify your GEMINI_API_KEY."
        )

    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt_text)
    
    if response and response.text:
        return response.text.strip(), "gemini"
    raise RuntimeError("Empty response from Gemini")


def _generate_ollama_report(prompt_text: str):
    print(f"Connecting to Local Offline Ollama ({OLLAMA_MODEL}) on {OLLAMA_HOST}...")

    # Build standard OpenAI-compatible payload structure for local completion
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.2
    }
    
    url = f"{OLLAMA_HOST}{OLLAMA_API_PATH}"
    data = json.dumps(payload).encode("utf-8")
    
    headers = {"Content-Type": "application/json"}
    req = request.Request(url, data=data, headers=headers, method="POST")

    last_exc = None
    for attempt in range(OLLAMA_MAX_RETRIES + 1):
        try:
            start_time = time.time()
            with request.urlopen(req, timeout=OLLAMA_TIMEOUT_SECONDS) as resp:
                elapsed = time.time() - start_time
                if resp.status == 200:
                    body = json.loads(resp.read().decode("utf-8"))
                    choices = body.get("choices", [])
                    if choices and len(choices) > 0:
                        content = choices[0].get("message", {}).get("content", "")
                        return content.strip(), "ollama"
                    raise RuntimeError("Empty completion returned from Ollama")
        except Exception as e:
            last_exc = e
            elapsed = time.time() - start_time
            print(
                f"Ollama attempt {attempt + 1}/{OLLAMA_MAX_RETRIES + 1} elapsed={elapsed:.2f}s url={url}"
            )
            
    if last_exc:
        raise last_exc
    raise RuntimeError("Ollama request failed without exception")
