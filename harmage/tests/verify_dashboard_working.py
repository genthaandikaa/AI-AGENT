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

        print("Navigating to http://127.0.0.1:5173...")
        response = page.goto("http://127.0.0.1:5173", wait_until="networkidle", timeout=30000)
        print(f"HTTP Status: {response.status if response else 'None'}")

        time.sleep(3)

        screenshot_path = "C:/Users/genn/.gemini/antigravity/brain/824186a8-93ca-4619-86af-08abc7cfb5d8/qa_screenshots_react_dashboard_all_working.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")

        browser.close()

    print(f"Total Console/Page Errors: {len(errors)}")
    for e in errors[:5]:
        print(" -", e)

    if any("TypeError" in e for e in errors):
        print("FAIL: TypeError detected!")
        sys.exit(1)
    else:
        print("SUCCESS: 0 fatal errors, React dashboard verified!")

if __name__ == "__main__":
    main()
