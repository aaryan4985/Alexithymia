import json
import os
import requests
from bs4 import BeautifulSoup
import cloudscraper
import time
import random
import re
from playwright.sync_api import sync_playwright

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def load_last_chapter(name):
    STATE_FILE= os.path.join(DATA_DIR, f"{name}.jsonl")
    if not os.path.exists(STATE_FILE):
        return 0
    
    with open(STATE_FILE, "r") as f:
        data = list(f)[-1]
        chapter = json.loads(data)['chapter'].split()[1]
        return int(chapter)
        
def get_chapter_list(name, scraper, headers):
    print(f"Getting chapter list for {name}...")
    r = scraper.get(f"https://novelbin.me/b/{name}", headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    match = re.search(r"novelId\s*=\s*['\"]([^'\"]+)", r.text)
    if not match:
        print(f"Could not find novel ID for {name}. Might be blocked by Cloudflare or invalid name.")
        return []
    novel_id = match.group(1)
    ajax = scraper.get(
        f"https://novelbin.me/ajax/chapter-archive?novelId={novel_id}",
        headers=headers
    )
    soup = BeautifulSoup(ajax.text, "html.parser")
    chapters = soup.select("span.nchr-text.chapter-title")
    return [
    {
        "title": c.text.strip(),
        "url": c.find_parent("a")["href"]
    }
    for c in chapters
    ]

def scrap_chapters(name):
    scraper = cloudscraper.create_scraper(delay=10)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml"
    }

    links = get_chapter_list(name, scraper, headers)
    if not links:
        return

    os.makedirs(DATA_DIR, exist_ok=True)
    latest = load_last_chapter(name)
    links = links[latest:]
    
    for item in links:
        print(f"Fetching chapter: {item['title']}...")
        success = False
        for attempt in range(3):
            try:
                res = scraper.get(item['url'], headers=headers)
                text = res.text
                if res.status_code == 200 and "Just a moment..." not in text:
                    soup = BeautifulSoup(text, "html.parser")
                    body = soup.find(id="chr-content")
                    if body:
                        chcontent = [p.get_text(strip=True) for p in body.find_all("p")] 
                        with open(os.path.join(DATA_DIR, f"{name}.jsonl"),"a",encoding="utf-8") as f:
                            data = {
                                "chapter":item['title'],
                                "data":chcontent
                            }
                            f.write(json.dumps(data, ensure_ascii=False) + "\n")
                            print(" -> Saved", item['title'])
                            f.flush()
                            success = True
                            break
                    else:
                        print(" -> Failed to find chapter content in HTML.")
                        break
                else:
                    print(f" -> Blocked by Cloudflare (Attempt {attempt+1}/3). Waiting...")
            except Exception as e:
                print(f" -> Request error: {e}")
            
            time.sleep(2 ** attempt)
        
        if not success:
            print(" -> Cloudscraper failed. Switching to Playwright fallback...")
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page(user_agent=headers["User-Agent"])
                    page.goto(item['url'])
                    page.wait_for_selector("#chr-content", timeout=15000)
                    html = page.content()
                    browser.close()
                    
                    soup = BeautifulSoup(html, "html.parser")
                    body = soup.find(id="chr-content")
                    if body:
                        chcontent = [p.get_text(strip=True) for p in body.find_all("p")] 
                        with open(os.path.join(DATA_DIR, f"{name}.jsonl"),"a",encoding="utf-8") as f:
                            data = {
                                "chapter":item['title'],
                                "data":chcontent
                            }
                            f.write(json.dumps(data, ensure_ascii=False) + "\n")
                            print(" -> Saved via Playwright", item['title'])
                            f.flush()
                            success = True
                    else:
                        print(" -> Failed to find chapter content with Playwright.")
            except Exception as e:
                print(f" -> Playwright fallback failed: {e}")

        if not success:
            print(f" -> Skipping {item['title']} after all attempts failed.")

        time.sleep(random.uniform(2, 6))

if __name__ == "__main__":
    name = str(input("enter the novel to scrap, use dashes '-' instead of space, ex - 'shadow-slave' : "))
    scrap_chapters(name)
