import os
import re
from decimal import Decimal
from playwright.sync_api import sync_playwright

def parse_decimal(raw_text: str) -> Decimal:
    if not raw_text: return Decimal("0")
    raw_text = raw_text.replace('\u00a0', ' ').replace('\xa0', ' ')
    numbers = re.findall(r"\d+[.,]\d+|\d+", raw_text)
    if not numbers: return Decimal("0")
    value = numbers[0].replace(",", ".")
    return Decimal(value)

def test_belvezar():
    print("Testing Belvezar...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.belvezar.com", wait_until="networkidle")
        
        # Check if products are visible
        cards = page.query_selector_all(".gs-grid-item")
        print(f"Found {len(cards)} cards")
        for card in cards[:3]:
            title = card.query_selector(".gs-item-title")
            price = card.query_selector(".gs-new-price")
            print(f"Title: {title.inner_text() if title else 'N/A'}")
            print(f"Price: {price.inner_text() if price else 'N/A'}")
        browser.close()

def test_patricia():
    print("\nTesting Patricia...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://patricia.bg", wait_until="networkidle")
        
        # Check if products are visible
        cards = page.query_selector_all(".product-item")
        print(f"Found {len(cards)} cards")
        for card in cards[:3]:
            title = card.query_selector(".product-item-name")
            price = card.query_selector(".price-wrapper .price")
            print(f"Title: {title.inner_text() if title else 'N/A'}")
            print(f"Price: {price.inner_text() if price else 'N/A'}")
        browser.close()

if __name__ == "__main__":
    test_belvezar()
    test_patricia()
