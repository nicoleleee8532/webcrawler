import requests
from bs4 import BeautifulSoup
import csv
import time

# ==========================
# IMDb Scraper for Top 250 TV Shows
# ==========================

BASE_URL = "https://www.imdb.com"
START_URL = f"{BASE_URL}/chart/toptv/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_show_links():
    """Fetch show titles and links from IMDb Top 250 TV page."""
    try:
        response = requests.get(START_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        shows = []
        for card in soup.select("li.ipc-metadata-list-summary-item"):
            try:
                # Title
                title_tag = card.select_one("h3.ipc-title__text")
                href_tag = card.select_one("a.ipc-title-link-wrapper")

                if title_tag and href_tag:
                    title = title_tag.get_text(strip=True)
                    # Remove ranking number like "1. Breaking Bad"
                    if "." in title:
                        title = title.split(".", 1)[1].strip()
                    link = BASE_URL + href_tag.get("href").split("?")[0]
                    shows.append({"title": title, "link": link})
            except Exception as e:
                print("Skipping show due to error:", e)

        return shows
    except Exception as e:
        print("Error fetching Top TV page:", e)
        return []


def scrape_show_details(show):
    """Scrape genres, rating, and description from each show page."""
    try:
        response = requests.get(show["link"], headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Genres
        genres = [g.get_text(strip=True) for g in soup.select("span.ipc-chip__text")]

        # IMDb Rating
        rating_tag = soup.select_one("span.ipc-rating-star--rating")
        rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

        # Description
        desc_tag = soup.select_one('span[data-testid="plot-xl"]')
        if not desc_tag:
            desc_tag = soup.select_one("span.sc-16ede01-2")
        description = desc_tag.get_text(strip=True) if desc_tag else "N/A"

        show.update({
            "genres": genres,
            "rating": rating,
            "description": description
        })

    except Exception as e:
        print(f"Error scraping {show['title']}: {e}")

    return show


def save_to_csv(shows, filename="data/top250_shows.csv"):
    """Save scraped show data to CSV file."""
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["title", "genres", "rating", "description", "link"]
            )
            writer.writeheader()
            for show in shows:
                writer.writerow({
                    "title": show["title"],
                    "genres": ", ".join(show.get("genres", [])),
                    "rating": show.get("rating", "N/A"),
                    "description": show.get("description", "N/A"),
                    "link": show["link"]
                })
        print(f"\n✅ Saved {len(shows)} shows to {filename}")
    except Exception as e:
        print("Error saving CSV:", e)


def main():
    print("Fetching IMDb Top 250 TV Shows...")
    shows = get_show_links()
    print(f"Found {len(shows)} shows. Scraping details...\n")

    detailed_shows = []
    for i, show in enumerate(shows, start=1):
        print(f"Scraping {i}: {show['title']}")
        detailed_shows.append(scrape_show_details(show))
        time.sleep(1)  # polite scraping

    save_to_csv(detailed_shows)


if __name__ == "__main__":
    main()
