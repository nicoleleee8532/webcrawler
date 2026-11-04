# Movie Recommendation Website (Web Crawler)

A full-stack movie and TV recommendation website. Scrapers collect titles, ratings, genres and descriptions from IMDb, Metacritic, Rotten Tomatoes and Netflix; the data is cleaned and merged; and a Flask app recommends titles from a search like "something funny" or a chosen genre. Built as Computer Science coursework at Beijing Institute of Technology.

- ▶️ [Live demo](https://nicoleleee8532.github.io/movie-recommender/)
- 🎨 [Project presentation on Canva](https://canva.link/ivfg70r43d0arwk)

**Tech:** Python · Flask · pandas · requests · BeautifulSoup · Selenium · HTML/CSS (Bootstrap) · JavaScript

## How it works

1. **Collect.** `scrapers/` holds one scraper per source (IMDb top 250 and trending, Metacritic, Rotten Tomatoes, Netflix). Raw results are saved in `data/`.
2. **Clean and combine.** `others/combine.py` merges the sources into `combined_movies.csv`, and `scrapers/imdb_clean.py` cleans them into `combined_movies_cleaned.csv`. `others/analysis.py` explores the data.
3. **Recommend.** `app.py` expands the search with synonyms from `keywords.json` (so "sad" also matches "tragic", "heartbreaking" and so on), filters by genre and keywords across titles, descriptions and genres, and returns the 10 highest-rated matches.
4. **Front end.** `templates/index.html` and `static/` give a playful interface with recommendation cards, hover and click sounds, background music and popcorn and confetti animations.

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000. The recommender runs on the included CSV, so no scraping is needed to try it.

## Live demo

The live demo is a static build hosted on my GitHub Pages site: `tools/build_static.py` turns the CSV into `data.json` and runs the same recommendation logic as `app.py` in the browser, so it gives the same results without a server. Rebuild it after changing the data with `python tools/build_static.py`.

## My contribution

- Designed and implemented parts of the crawler and the recommendation logic
- Development, testing and debugging across the prototype, milestone and final versions
- Processing and organising the collected data
- The final presentation and documentation

## Repository layout

```
app.py                       Flask app and recommendation logic
keywords.json                synonym map used to widen searches
combined_movies_cleaned.csv  dataset the app recommends from
scrapers/                    one scraper per source
others/                      merging and analysis scripts
data/                        raw scraped data
templates/, static/          front end
archives/                    earlier versions: prototype, prototype2, milestone1, final
```

## What I learned

Web data collection across sites with different structures, cleaning messy real-world data, building a small recommender, and taking a project from prototype to a finished, presented product as part of a team.
