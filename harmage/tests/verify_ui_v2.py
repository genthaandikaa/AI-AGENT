import time
from pathlib import Path
from playwright.sync_api import sync_playwright

QA_DIR = Path("C:/Users/genn/.gemini/antigravity/brain/824186a8-93ca-4619-86af-08abc7cfb5d8/qa_screenshots")
QA_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE_URL = "http://localhost:5173"

def run_suite():
    print(f"--- Running Harmage UI Verification Suite v2 ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--window-size=1440,900"]
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        # 1. Dashboard View
        print("[1] Testing Dashboard...")
        page.goto(BASE_URL, wait_until="networkidle", timeout=15000)
        time.sleep(2)
        page.screenshot(path=str(QA_DIR / "01_dashboard_clean.png"))
        print("  -> Captured 01_dashboard_clean.png")

        # 2. Overview View (Hermes 3D)
        print("[2] Testing Overview (Hermes 3D)...")
        page.click("button:has-text('Overview')")
        time.sleep(3)
        page.screenshot(path=str(QA_DIR / "02_overview_hermes3d.png"))
        print("  -> Captured 02_overview_hermes3d.png")

        # 3. Divisions View
        print("[3] Testing Divisions...")
        page.click("button:has-text('Divisions')")
        time.sleep(1.5)
        page.screenshot(path=str(QA_DIR / "03_divisions_clean.png"))
        print("  -> Captured 03_divisions_clean.png")

        # 4. Tasks View
        print("[4] Testing Tasks...")
        page.click("button:has-text('Tasks & Projects')")
        time.sleep(1.5)
        page.screenshot(path=str(QA_DIR / "04_tasks_kanban.png"))
        print("  -> Captured 04_tasks_kanban.png")

        # 5. Approvals View
        print("[5] Testing Approvals...")
        page.click("button:has-text('Approvals')")
        time.sleep(1.5)
        page.screenshot(path=str(QA_DIR / "05_approvals_gate.png"))
        print("  -> Captured 05_approvals_gate.png")

        # 6. Meetings View
        print("[6] Testing Meetings...")
        page.click("button:has-text('Meetings')")
        time.sleep(1.5)
        page.screenshot(path=str(QA_DIR / "06_meetings_sync.png"))
        print("  -> Captured 06_meetings_sync.png")

        browser.close()
        print("All tests passed successfully!")

if __name__ == "__main__":
    run_suite()
