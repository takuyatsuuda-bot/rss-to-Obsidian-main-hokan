import asyncio
from playwright.async_api import async_playwright
import datetime
import os
import csv

# Configuration
URL = "https://blastup.com/instagram-follower-count?tobutoptours_official"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_CSV = os.path.join(SCRIPT_DIR, "follower_log.csv")
LOG_FILE_MD = os.path.join(SCRIPT_DIR, "follower_log.md")

async def run():
    print(f"[{datetime.datetime.now()}] 🚀 Starting follower check (Debug Mode)...")
    
    async with async_playwright() as p:
        # Launch browser with anti-detection args
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Add init script to hide webdriver property
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()

        try:
            print(f"🌐 Navigating to: {URL}")
            await page.goto(URL, timeout=60000)
            
            # Wait for the odometer to appear
            print("⏳ Waiting for counter to load...")
            try:
                await page.wait_for_selector("#odometer .odometer-value", state="visible", timeout=30000)
            except:
                print("⚠️ Selector timeout, taking snapshot...")
            
            # Wait longer for animation
            await asyncio.sleep(10)
            
            # Debug: Screenshot
            await page.screenshot(path=os.path.join(SCRIPT_DIR, "debug_monitor.png"))
            print("📸 Debug screenshot saved.")

            # extraction strategy 1: digits
            digit_elements = await page.locator("#odometer .odometer-value").all()
            digits = [await d.inner_text() for d in digit_elements]
            print(f"🔍 Raw Digits found: {digits}")
            
            follower_count_str = "".join(digits)
            
            # extraction strategy 2: full text
            if not follower_count_str or follower_count_str == "0":
                print("⚠️ Digits empty or 0, trying full text...")
                full_text = await page.inner_text("#odometer")
                print(f"🔍 Full Odometer Text: {full_text}")
                # clean up (odometer often puts line breaks)
                follower_count_str = "".join([c for c in full_text if c.isdigit()])

            print(f"✅ Final Follower Count: {follower_count_str}")
            
            if follower_count_str and follower_count_str != "0":
                # Get current timestamp
                now = datetime.datetime.now()
                timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
                date_str = now.strftime("%Y-%m-%d")
                
                # Save to CSV
                with open(LOG_FILE_CSV, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp_str, date_str, follower_count_str])
                print(f"💾 Saved to CSV: {LOG_FILE_CSV}")

                # Save to Markdown
                if not os.path.exists(LOG_FILE_MD):
                     with open(LOG_FILE_MD, "w", encoding="utf-8") as f:
                        f.write(f"# Instagram Follower Log\n\n| Date | Time | Followers |\n|---|---|---|\n")
                
                with open(LOG_FILE_MD, "a", encoding="utf-8") as f:
                    time_str = now.strftime("%H:%M")
                    f.write(f"| {date_str} | {time_str} | {follower_count_str} |\n")
                print(f"💾 Saved to MD: {LOG_FILE_MD}")
            else:
                 print("❌ Retrieved 0 or empty, not saving.")

        except Exception as e:
            print(f"❌ Error occurred: {e}")
            await page.screenshot(path=os.path.join(SCRIPT_DIR, "error_screenshot.png"))
        
        finally:
            await browser.close()
            print("🏁 Done.")

if __name__ == "__main__":
    asyncio.run(run())
