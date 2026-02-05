import asyncio
from playwright.async_api import async_playwright
import json
import os
import time

# Configuration
USER_DATA_DIR = '../chrome_data'
OUTPUT_FILE = '../data/sdot_bridges_tweets.json' # Same output as original scraper to merge data
TARGET_URL = 'https://x.com/SDOTbridges'
HEADLESS = False # Default to False for local testing/auth, can be overridden by env var

async def save_data(new_tweets):
    if not os.path.exists(OUTPUT_FILE):
        existing_data = []
    else:
        try:
            with open(OUTPUT_FILE, 'r') as f:
                existing_data = json.load(f)
        except:
            existing_data = []

    # Simple deduplication by timestamp + text
    # (Using a set of signatures)
    seen = set()
    for t in existing_data:
        # Create a signature
        sig = f"{t.get('timestamp')}|{t.get('text')}"
        seen.add(sig)
        
    count = 0
    for t in new_tweets:
        sig = f"{t.get('timestamp')}|{t.get('text')}"
        if sig not in seen:
            existing_data.append(t)
            seen.add(sig)
            count += 1
            
    # Sort by timestamp descending
    try:
        existing_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    except:
        pass
        
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(existing_data, f, indent=2)
        
    print(f"Saved {count} new tweets. Total: {len(existing_data)}")

async def scrape():
    print(f"Launching browser (Headless: {HEADLESS})...")
    async with async_playwright() as p:
        # Launch with persistent context to save login state
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=HEADLESS,
            args=["--disable-blink-features=AutomationControlled"] # Attempt to hide automation
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        print(f"Navigating to {TARGET_URL}...")
        await page.goto(TARGET_URL)
        
        # Check login state
        # A good indicator of being logged out is the "Sign in to X" dialog or "Log in" button
        # A good indicator of being logged in is the "Home" icon or profile picture
        
        try:
            # Wait a bit for page load
            await page.wait_for_timeout(5000)
            
            # Check for generic "Sign in" text which often appears in a modal for logged-out users
            # Or check for the "Post" composer area
            
            # Strategy: If we see a login prompt, pause and ask user to login (if headed)
            # If headless, we just have to fail or screenshot.
            
            title = await page.title()
            print(f"Page Title: {title}")
            
            title = await page.title()
            print(f"Page Title: {title}")
            
            # Wait for Login
            print("Checking login status...")
            try:
                # Check if we are already logged in (look for account switcher or home nav)
                # This selector is common for the account menu at bottom left
                await page.wait_for_selector('[data-testid="SideNav_AccountSwitcher_Button"]', timeout=5000)
                print("Already logged in!")
            except:
                print("\n" + "="*50)
                print("Action Required: Check the browser window.")
                print("Please LOG IN manually now.")
                print("Script is waiting for you to complete login...")
                print("="*50 + "\n")
                
                # Wait up to 300 seconds (5 minutes) for the user to log in
                try:
                    await page.wait_for_selector('[data-testid="SideNav_AccountSwitcher_Button"]', timeout=300000)
                    print("\nLogin detected! Proceeding...")
                except:
                    print("Timed out waiting for login. Continuing anyway (might fail)...")

            print("Continuing...")
            
            # Inject Scraper Script
            # This is the same logic as scrape_tweets.js but adapted for Playwright execution
            # We will scroll a few times and collect data
            
            tweets_collected = []
            
            for i in range(5): # Scroll 5 times for the test
                print(f"Scrolling ({i+1}/5)...")
                
                # Execute extraction in browser context
                new_batch = await page.evaluate("""() => {
                    const tweets = [];
                    const articles = document.querySelectorAll('article');
                    articles.forEach(article => {
                        const timeElement = article.querySelector('time');
                        if (!timeElement) return;
                        
                        const timestamp = timeElement.getAttribute('datetime');
                        const textElement = article.querySelector('div[lang]');
                        const text = textElement ? textElement.innerText : '';
                        
                        tweets.push({
                            timestamp: timestamp,
                            text: text,
                            created_at: timestamp // Compat with API format
                        });
                    });
                    window.scrollTo(0, document.body.scrollHeight);
                    return tweets;
                }""")
                
                if new_batch:
                    tweets_collected.extend(new_batch)
                    print(f"Found {len(new_batch)} items (raw) on page.")
                
                await page.wait_for_timeout(3000) # Wait for load
            
            await save_data(tweets_collected)
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            # Screenshot for debugging
            await page.screenshot(path="debug_screenshot.png")
            
        finally:
            await context.close()

if __name__ == "__main__":
    if os.environ.get("HEADLESS") == "true":
        HEADLESS = True
    asyncio.run(scrape())
