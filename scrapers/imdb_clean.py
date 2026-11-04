import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Input CSV with IMDb links (replace with your file)
input_csv = "data/all_media_data.csv"
output_csv = "imdb_clean.csv"

# Load CSV
df_input = pd.read_csv(input_csv)

# Function to scrape IMDb page
def scrape_imdb(url):
    data = {
        "title": None,
        "link": url,
        "genres": None,
        "rating": None,
        "description": None,
        "type": "movie"  # default, can be adjusted later
    }
    
    if pd.isna(url):
        return data
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/140.0.0.0 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return data
        
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Title
        title_tag = soup.find("h1")
        if title_tag:
            data["title"] = title_tag.text.strip()
        
        # Rating
        rating_tag = soup.find("span", class_="ipc-rating-star--rating")
        if rating_tag:
            try:
                data["rating"] = float(rating_tag.text.strip())
            except:
                data["rating"] = None
        
        # Genres
        genres_tag = soup.find_all("a", attrs={"href": lambda x: x and "/search/title?genres=" in x})
        if genres_tag:
            genres = [g.text.strip() for g in genres_tag]
            data["genres"] = ", ".join(genres)
        
        # Description / Plot
        desc_tag = soup.find("span", {"data-testid": "plot-l"})
        if not desc_tag:
            desc_tag = soup.find("span", {"data-testid": "plot-xl"})
        if desc_tag:
            data["description"] = desc_tag.text.strip()
        
        # Type
        if "/tv/" in url:
            data["type"] = "tv"
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    
    # Be polite
    time.sleep(0.5)
    return data

# Iterate through all IMDb links
scraped_data = []
for link in df_input['link']:
    scraped_data.append(scrape_imdb(link))

# Save to DataFrame
df_scraped = pd.DataFrame(scraped_data)

# Save to CSV
df_scraped.to_csv(output_csv, index=False)
print(f"Scraping complete! Data saved to {output_csv}")
