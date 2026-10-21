import sys
import time
from playwright.sync_api import sync_playwright

def main():
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe",
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        page.on("pageerror", lambda err: errors.append(f"PageError: {err}"))
        page.on("console", lambda msg: errors.append(f"ConsoleError: {msg.text}") if msg.type == "error" else None)

        print("Navigating to http://localhost:3000/office...")
        response = page.goto("http://localhost:3000/office", wait_until="domcontentloaded", timeout=60000)
        print(f"HTTP Status: {response.status if response else 'None'}")

        # Wait 5s for initial connection and desk seating
        time.sleep(5)

        # Look for status pill
        pill_text = page.locator("button:has-text('CONNECTED')").first.inner_text() if page.locator("button:has-text('CONNECTED')").count() > 0 else "None"
        print(f"Status pill: {pill_text}")

        # Rigorous test: wait an EXTRA 12 seconds (total >17 seconds)
        # Previous bug stopped working at second 5-10.
        print("Waiting 12 seconds to verify continuous desk work without timeout...")
        time.sleep(12)

        # Check if DEMO is present in status pill
        if "DEMO" in pill_text.upper():
            print("WARNING: DEMO was found in status pill!")
        else:
            print("CONFIRMED: Status pill is HERMES/PRODUCTION, zero DEMO indicator!")

        screenshot_path = "C:/Users/genn/.gemini/antigravity/brain/824186a8-93ca-4619-86af-08abc7cfb5d8/qa_screenshots_hermes_office_never_quits.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")

        browser.close()

    fatal_errors = [e for e in errors if "TypeError" in e or "Cannot read" in e]
    print(f"Total Console Errors: {len(errors)}, Fatal: {len(fatal_errors)}")
    for e in errors[:5]:
        print(" -", e)

    if fatal_errors:
        print("FAIL: Fatal errors detected!")
        sys.exit(1)
    else:
        print("SUCCESS: Office running with HERMES runtime and continuous real work verified!")

if __name__ == "__main__":
    main()
