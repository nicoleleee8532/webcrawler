# metacritic_scraper.py
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHROMEDRIVER_PATH = "/opt/homebrew/bin/chromedriver"
INPUT_CSV = "data/metacritic_scraped.csv"
OUTPUT_CSV = "data/metacritic_scraped.csv"

# ==========================
# Selenium setup
# ==========================
def get_driver():
    options = Options()
    options.add_argument("--headless")  # run in background
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    )
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# ==========================
# Scraper for movies
# ==========================
def scrape_movie(driver, url):
    driver.get(url)
    time.sleep(2)  # give JS a moment to render

    # wait for metascore to appear
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.c-siteReviewScore span"))
        )
    except:
        print(f"⚠️ Timeout waiting for score on {url}")

    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1, h3.c-globalProductCard_title").text.strip()
    except:
        title = ""

    try:
        metascore = driver.find_element(By.CSS_SELECTOR, "div.c-siteReviewScore span").text.strip()
    except:
        metascore = ""

    try:
        user_score = driver.find_element(By.CSS_SELECTOR, "div.c-userScore span").text.strip()
    except:
        user_score = ""

    try:
        desc = driver.find_element(By.CSS_SELECTOR, "span[data-v-2cb8068e]").text.strip()
    except:
        desc = ""

    return {
        "type": "movie",
        "title": title,
        "metascore": metascore,
        "user_score": user_score,
        "description": desc,
        "link": url,
    }

# ==========================
# Main loop
# ==========================
if __name__ == "__main__":
    df_links = pd.read_csv(INPUT_CSV)
    urls = df_links["link"].dropna().tolist()

    driver = get_driver()
    results = []

    for url in urls:
        print("🎬 Scraping:", url)
        try:
            result = scrape_movie(driver, url)
            results.append(result)
        except Exception as e:
            print(f"❌ Failed to scrape {url}: {e}")

    driver.quit()

    df_out = pd.DataFrame(results)
    df_out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"✅ Done! Scraped {len(results)} movies → {OUTPUT_CSV}")
