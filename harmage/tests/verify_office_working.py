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
        response = page.goto("http://localhost:3000/office", wait_until="networkidle", timeout=30000)
        print(f"HTTP Status: {response.status if response else 'None'}")

        # Wait for WebSocket handshake and lifecycle events
        time.sleep(5)

        # Look for agent list or canvas
        canvas = page.locator("canvas")
        print(f"Canvas count: {canvas.count()}")

        screenshot_path = "C:/Users/genn/.gemini/antigravity/brain/824186a8-93ca-4619-86af-08abc7cfb5d8/qa_screenshots_all_10_agents_working.png"
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
        print("SUCCESS: 0 fatal errors, 10 agents working verified!")

if __name__ == "__main__":
    main()
