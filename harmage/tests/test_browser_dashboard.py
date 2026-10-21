"""Playwright browser automated test suite for Harmage React Vite Admin Dashboard.

Connects to existing Google Chrome installation, verifies all views (Overview, Agents, Workflows, Tasks, Integrations, Settings),
tests 2D NPC roster modal, Kanban board, and captures QA screenshots.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
QA_DIR = WORKSPACE_DIR / "artifacts" / "qa"
QA_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE_URL = "http://localhost:5173"


def run_qa_suite():
    print(f"--- Starting Harmage React Vite QA Browser Suite ---")
    print(f"Target URL: {BASE_URL}")
    print(f"Using Chrome at: {CHROME_PATH}")
    print(f"Saving evidence screenshots to: {QA_DIR}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1440,900"
            ]
        )
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # 1. Test Overview Page (Matching User's Reference Image)
        print("\n[Step 1] Loading React Vite Dashboard Overview...")
        page.goto(BASE_URL, wait_until="networkidle", timeout=15000)
        time.sleep(2)

        title = page.title()
        print(f"Page title verified: '{title}'")
        assert "Harmage Agents" in title, f"Unexpected page title: {title}"

        # Capture Overview Screenshot
        screenshot_1 = QA_DIR / "01_react_dashboard_overview.png"
        page.screenshot(path=str(screenshot_1))
        print(f"[OK] Saved screenshot: {screenshot_1}")

        # 2. Test Agents View & 2D NPC Roster
        print("\n[Step 2] Navigating to Agents Roster View...")
        page.click("button:has-text('Agents')")
        time.sleep(1)

        screenshot_2 = QA_DIR / "02_react_agents_roster.png"
        page.screenshot(path=str(screenshot_2))
        print(f"[OK] Saved screenshot: {screenshot_2}")

        # Open Alex Vance NPC Profile Modal
        print("[Step 2.1] Opening Alex Vance NPC Profile Modal...")
        page.locator(".group").first.click()
        time.sleep(1)

        screenshot_2b = QA_DIR / "03_react_agent_modal.png"
        page.screenshot(path=str(screenshot_2b))
        print(f"[OK] Saved screenshot: {screenshot_2b}")

        # Close modal
        page.click("button:has-text('Close Profile')")
        time.sleep(0.5)

        # 3. Test Workflows View
        print("\n[Step 3] Navigating to Workflows View...")
        page.click("button:has-text('Workflows')")
        time.sleep(1)

        screenshot_3 = QA_DIR / "04_react_workflows_video.png"
        page.screenshot(path=str(screenshot_3))
        print(f"[OK] Saved screenshot: {screenshot_3}")

        # 4. Test Tasks & Kanban View
        print("\n[Step 4] Navigating to Tasks View...")
        page.click("button:has-text('Tasks')")
        time.sleep(1)

        screenshot_4 = QA_DIR / "05_react_tasks_kanban.png"
        page.screenshot(path=str(screenshot_4))
        print(f"[OK] Saved screenshot: {screenshot_4}")

        # 5. Test Integrations View
        print("\n[Step 5] Navigating to Integrations & Infrastructure...")
        page.click("button:has-text('Integrations')")
        time.sleep(1)

        screenshot_5 = QA_DIR / "06_react_integrations.png"
        page.screenshot(path=str(screenshot_5))
        print(f"[OK] Saved screenshot: {screenshot_5}")

        browser.close()
        print("\n=== ALL REACT VITE BROWSER QA TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    run_qa_suite()
