import json
import re
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# -------------------
# Configuration Zone
# -------------------

KEY_PHRASES = [
    "nationwide protest", "nationwide revolt", "nationwide riots", "civil unrest",
    "june 14 protest", "june 14 riots", "take back the country", "the 14th uprising",
    "revolution june 14", "organizing for june 14", "coordinated action",
    "the people rise", "day of action", "mass protest", "mobilizing june 14",
    "riot", "riots"
]

# Twitter search URL template
SEARCH_URL_TEMPLATE = "https://twitter.com/search?q={}&src=typed_query&f=live"

# Output file
OUTPUT_FILE = "x_osint_feed.json"

# Search frequency (seconds)
LOOP_DELAY = 120  # 2 minutes between pulls

# Max tweets per cycle
MAX_TWEETS_PER_CYCLE = 25

# Headless Browser Config
def build_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Clean and normalize text
def normalize(text):
    return re.sub(r'\s+', ' ', text.strip()).lower()

# Main Scraper Logic
def scrape():
    driver = build_driver()
    results = []

    for phrase in KEY_PHRASES:
        search_phrase = phrase.replace(" ", "%20")
        url = SEARCH_URL_TEMPLATE.format(search_phrase)
        driver.get(url)
        time.sleep(random.randint(5, 9))  # mimic human behavior

        tweets = driver.find_elements(By.XPATH, '//article')
        count = 0

        for tweet in tweets:
            try:
                content = tweet.text
                normalized = normalize(content)
                if any(k in normalized for k in KEY_PHRASES):
                    data = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "keyword": phrase,
                        "content": content,
                        "url": url
                    }
                    results.append(data)
                    count += 1
            except Exception as e:
                pass

            if count >= MAX_TWEETS_PER_CYCLE:
                break

        time.sleep(random.randint(3, 5))  # avoid bans

    driver.quit()

    if results:
        try:
            with open(OUTPUT_FILE, "r") as f:
                old_data = json.load(f)
        except FileNotFoundError:
            old_data = []

        full_data = old_data + results
        with open(OUTPUT_FILE, "w") as f:
            json.dump(full_data, f, indent=4)

    print(f"[{datetime.utcnow()}] Cycle complete. {len(results)} new entries saved.")

# Continuous loop
if __name__ == "__main__":
    while True:
        scrape()
        time.sleep(LOOP_DELAY)
