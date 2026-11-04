import requests
from bs4 import BeautifulSoup
import time
import csv
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================
# Part 1: Scraper
# ==========================
BASE_URL = "https://www.imdb.com"
START_URL = f"{BASE_URL}/chart/moviemeter/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_movie_links():
    """Get trending movie titles and their IMDb links."""
    try:
        response = requests.get(START_URL, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch {START_URL}, status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        movies = []

        for card in soup.select("a.ipc-title-link-wrapper"):
            try:
                title_tag = card.select_one("h3.ipc-title__text")
                href = card.get("href")
                if title_tag and href:
                    title = title_tag.get_text(strip=True)
                    link = BASE_URL + href
                    movies.append({"title": title, "link": link})
            except Exception as e:
                print("Skipping a card due to error:", e)

        return movies

    except Exception as e:
        print("Error fetching movie links:", e)
        return []

def scrape_movie_details(movie):
    """Scrape genres, rating, and description from a movie page."""
    try:
        response = requests.get(movie["link"], headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch {movie['link']}, status code: {response.status_code}")
            return movie

        soup = BeautifulSoup(response.content, "html.parser")

        # Genres
        genres = [g.get_text(strip=True) for g in soup.select("span.ipc-chip__text")]

        # IMDb Rating
        rating_tag = soup.select_one("span.ipc-rating-star--rating")
        rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

        # Description
        desc_tag = soup.select_one("span.sc-16ede01-2")
        if not desc_tag:
            desc_tag = soup.select_one('span[data-testid="plot-xl"]')
        description = desc_tag.get_text(strip=True) if desc_tag else "N/A"

        movie.update({
            "genres": genres,
            "rating": rating,
            "description": description
        })

    except Exception as e:
        print(f"Error scraping {movie['title']}: {e}")

    return movie

def save_to_csv(movies, filename="data/trending_movies.csv"):
    """Save movie data to a CSV file."""
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["title", "genres", "rating", "description", "link"])
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

# ==========================
# Part 2: Recommender
# ==========================
def load_data(csv_path="data/trending_movies.csv"):
    df = pd.read_csv(csv_path)
    df['description'] = df['description'].fillna("")
    df['genres'] = df['genres'].fillna("")
    df['features'] = df['genres'] + " " + df['description']
    return df

def build_similarity_matrix(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['features'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def recommend_movie(df, cosine_sim, title, top_n=5):
    if title not in df['title'].values:
        print(f"Movie '{title}' not found in dataset.")
        return []

    idx = df.index[df['title'] == title][0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    recommended_titles = [df.iloc[i[0]]['title'] for i in sim_scores]

    print(f"\nMovies similar to '{title}':")
    for t in recommended_titles:
        print("-", t)
    return recommended_titles

# ==========================
# Main Workflow
# ==========================
def main():
    # 1️⃣ Scrape IMDb trending movies
    print("Fetching trending movie links...")
    movies = get_movie_links()
    print(f"Found {len(movies)} movies. Scraping details...\n")

    detailed_movies = []
    for i, movie in enumerate(movies[:25], start=1):
        print(f"Scraping {i}: {movie['title']}")
        detailed_movies.append(scrape_movie_details(movie))
        time.sleep(1)  # polite scraping

    save_to_csv(detailed_movies)

    # 2️⃣ Build recommender
    df = load_data()
    cosine_sim = build_similarity_matrix(df)

    # 3️⃣ Interactive recommendation
    print("\nTrending Movies Recommender Ready!")
    print("Sample trending movies:")
    print(df['title'].head(10).to_list())

    while True:
        movie_name = input("\nEnter a movie title to get recommendations (or 'exit' to quit): ")
        if movie_name.lower() == "exit":
            break
        recommend_movie(df, cosine_sim, movie_name, top_n=5)

if __name__ == "__main__":
    main()
