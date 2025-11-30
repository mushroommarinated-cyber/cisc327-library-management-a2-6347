from playwright.sync_api import sync_playwright
import time

def test_verify_book_in_catalog_and_borrow_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("http://127.0.0.1:5000")
        page.wait_for_load_state("networkidle")

        page.wait_for_selector("table tbody tr", timeout=60000)

        assert page.inner_text("table tbody")
        assert "Test Book" in page.inner_text("table tbody"), "Book not found in catalog"

        page.wait_for_selector("form button[type='submit']", timeout=60000)

        page.click("form button[type='submit']")
        page.wait_for_selector(".status-available", timeout=60000)

        browser.close()
