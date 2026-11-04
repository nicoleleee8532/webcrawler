import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://www.imdb.com"
TV_METER_URL = f"{BASE_URL}/chart/tvmeter/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# --------------------------
# Step 1: Get trending TV shows
# --------------------------
def scrape_imdb_tv_shows():
    print("🔍 Loading IMDb TV Shows page...")
    response = requests.get(TV_METER_URL, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Failed to fetch page, status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    shows = []

    # Find all title tags
    for title_tag in soup.select("h3.ipc-title__text--reduced"):
        try:
            link_tag = title_tag.find_parent("a")
            if not link_tag:
                continue
            title = title_tag.get_text(strip=True)
            href = link_tag.get("href")
            full_link = BASE_URL + href
            shows.append({"title": title, "link": full_link})
        except Exception as e:
            print("⚠️ Error scraping a show:", e)
            continue

    print(f"✅ Found {len(shows)} TV shows.")
    return shows

# --------------------------
# Step 2: Get details for each show
# --------------------------
def scrape_show_details(show):
    """Scrape genres, rating, and description from a show page"""
    try:
        response = requests.get(show["link"], headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Failed to fetch {show['link']}, status code: {response.status_code}")
            return show

        soup = BeautifulSoup(response.text, "html.parser")

        # Genres
        genres = [g.get_text(strip=True) for g in soup.select("a[data-testid='genres']")]
        show["genres"] = ", ".join(genres) if genres else "N/A"

        # Description / Plot
        desc_tag = soup.select_one("span[data-testid='plot-xl']")
        if not desc_tag:
            desc_tag = soup.select_one("span.sc-16ede01-2")  # fallback
        show["description"] = desc_tag.get_text(strip=True) if desc_tag else "N/A"

        # Rating
        rating_tag = soup.select_one("span.ipc-rating-star--rating")
        show["rating"] = rating_tag.get_text(strip=True) if rating_tag else "N/A"

    except Exception as e:
        print(f"⚠️ Error scraping {show['title']}: {e}")

    return show

# --------------------------
# Step 3: Save to CSV
# --------------------------
def save_to_csv(shows, filename="data/trending_tv_shows.csv"):
    if not shows:
        print("❌ No shows to save.")
        return
    df = pd.DataFrame(shows)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"💾 Saved {len(shows)} TV shows to {filename}")

# --------------------------
# Main workflow
# --------------------------
if __name__ == "__main__":
    shows = scrape_imdb_tv_shows()

    detailed_shows = []
    for i, show in enumerate(shows[:25], start=1):  # Limit to top 25 for polite scraping
        print(f"Scraping details for {i}: {show['title']}")
        detailed_shows.append(scrape_show_details(show))
        time.sleep(1)  # polite scraping

    save_to_csv(detailed_shows)
