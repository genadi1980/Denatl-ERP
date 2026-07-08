import os
import json
import time
import re
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


def generate_ai_report(products_raw_data, provider: str = "gemini"):
    """Accepts either a raw database list or a string prompt and synthesizes the report using Google Gemini."""
    # Dynamically builds prompt strings or directly passes input strings through
    prompt_text = build_unified_prompt(products_raw_data)

    try:
        if client:
            return _generate_gemini_report(prompt_text)
        else:
            raise RuntimeError("Gemini client is not configured (missing API key).")
    except Exception as e:
        print(f"Gemini analysis failed: {e}")
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
