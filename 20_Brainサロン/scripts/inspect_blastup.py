import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    print("🚀 Starting inspection script...")
    async with async_playwright() as p:
        # Launch browser in visible mode so you can see what's happening
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        url = "https://blastup.com/instagram-follower-count?tobutoptours_official"
        print(f"🌐 Navigating to: {url}")
        
        try:
            await page.goto(url, timeout=60000)
            
            print("⏳ Waiting 15 seconds for the page to fully load and API requests to finish...")
            await asyncio.sleep(15)
            
            # Save screenshot
            screenshot_path = "blastup_debug.png"
            await page.screenshot(path=screenshot_path)
            print(f"📸 Screenshot saved to: {os.path.abspath(screenshot_path)}")
            
            # Save HTML
            html_content = await page.content()
            html_path = "blastup_debug.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"📝 HTML saved to: {os.path.abspath(html_path)}")
            
            print("\n✅ Inspection complete!")
            print("Please share the 'blastup_debug.html' file or let me know if an error occurred.")
            
        except Exception as e:
            print(f"❌ Error occurred: {e}")
            await page.screenshot(path="blastup_error.png")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
