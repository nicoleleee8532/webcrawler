import requests
from bs4 import BeautifulSoup
import csv
import time

# ==========================
# IMDb Scraper for Top 250 Movies
# ==========================

BASE_URL = "https://www.imdb.com"
START_URL = f"{BASE_URL}/chart/top/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_movie_links():
    """Fetch movie titles and links from IMDb Top 250 chart."""
    try:
        response = requests.get(START_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        movies = []
        # Movie containers
        for card in soup.select("li.ipc-metadata-list-summary-item"):
            try:
                title_tag = card.select_one("h3.ipc-title__text")
                href_tag = card.select_one("a.ipc-title-link-wrapper")

                if title_tag and href_tag:
                    title = title_tag.get_text(strip=True)
                    link = BASE_URL + href_tag.get("href").split("?")[0]
                    movies.append({"title": title, "link": link})
            except Exception as e:
                print("Skipping movie due to error:", e)

        return movies
    except Exception as e:
        print("Error fetching Top 250 page:", e)
        return []


def scrape_movie_details(movie):
    """Scrape genres, rating, and description from each movie page."""
    try:
        response = requests.get(movie["link"], headers=HEADERS)
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

        movie.update({
            "genres": genres,
            "rating": rating,
            "description": description
        })

    except Exception as e:
        print(f"Error scraping {movie['title']}: {e}")

    return movie


def save_to_csv(movies, filename="top250_movies.csv"):
    """Save scraped movie data to CSV file."""
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["title", "genres", "rating", "description", "link"]
            )
            writer.writeheader()
            for movie in movies:
                writer.writerow({
                    "title": movie["title"],
                    "genres": ", ".join(movie.get("genres", [])),
                    "rating": movie.get("rating", "N/A"),
                    "description": movie.get("description", "N/A"),
                    "link": movie["link"]
                })
        print(f"\n✅ Saved {len(movies)} movies to {filename}")
    except Exception as e:
        print("Error saving CSV:", e)


def main():
    print("Fetching IMDb Top 250 movies...")
    movies = get_movie_links()
    print(f"Found {len(movies)} movies. Scraping details...\n")

    detailed_movies = []
    for i, movie in enumerate(movies, start=1):
        print(f"Scraping {i}: {movie['title']}")
        detailed_movies.append(scrape_movie_details(movie))
        time.sleep(1)  # polite scraping

    save_to_csv(detailed_movies)


if __name__ == "__main__":
    main()
