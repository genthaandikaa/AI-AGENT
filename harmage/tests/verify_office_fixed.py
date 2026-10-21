import asyncio
from playwright.async_api import async_playwright

async def verify_office():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe",
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        async def handle_console(msg):
            print(f"BROWSER CONSOLE [{msg.type}]: {msg.text}")
            for arg in msg.args:
                try:
                    val = await arg.json_value()
                    print(f"   ARG: {val}")
                except Exception:
                    pass

        page.on("console", lambda msg: asyncio.create_task(handle_console(msg)))
        page.on("pageerror", lambda err: print(f"PAGE ERROR STACK:\n{err}"))

        print("Navigating to http://localhost:3000/office...")
        await page.goto("http://localhost:3000/office", wait_until="load", timeout=30000)
        await page.wait_for_timeout(4000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_office())
