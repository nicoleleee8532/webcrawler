from flask import Flask, render_template, request
import pandas as pd
import json
import re

# Load keyword map
with open("keywords.json", "r") as f:
    keyword_map = json.load(f)

def expand_keywords(user_input):
    words = re.findall(r'\w+', user_input.lower())  # extract words
    expanded = []
    for w in words:
        expanded.append(w)
        expanded.extend(keyword_map.get(w, []))  # add synonyms if exist
    return list(set(expanded))  # remove duplicates

app = Flask(__name__)

# Load your cleaned CSV
df = pd.read_csv('combined_movies_cleaned.csv')

# Remove "Back to top" from genres
df['genres'] = df['genres'].str.replace('Back to top', '', regex=False)

# Split genres into lists for filtering
df['genre_list'] = df['genres'].str.split(',')

# Helper function: simple recommendation by genre and rating
def recommend_movies(keyword=None, selected_genre=None, top_n=10, sort_by='rating'):
    temp_df = df.copy()

    # Filter by genre
    if selected_genre:
        temp_df = temp_df[temp_df['genre_list'].apply(
            lambda x: selected_genre in [g.strip() for g in x]
        )]

    # Filter by keyword(s)
    if keyword:
        expanded_keywords = expand_keywords(keyword)
        regex_pattern = '|'.join(map(re.escape, expanded_keywords))  # safe regex
        temp_df = temp_df[
            temp_df['title'].str.contains(regex_pattern, case=False, na=False) |
            temp_df['description'].str.contains(regex_pattern, case=False, na=False) |
            temp_df['genres'].str.contains(regex_pattern, case=False, na=False)
        ]

    temp_df = temp_df.sort_values(by=sort_by, ascending=False)
    return temp_df.head(top_n).to_dict(orient='records')

@app.route('/', methods=['GET', 'POST'])
def index():
    genres = sorted(set(g.strip() for sublist in df['genre_list'].dropna() for g in sublist))
    recommendations = []

    if request.method == 'POST':
        selected_genre = request.form.get('genre')
        search_query = request.form.get('search')
        recommendations = recommend_movies(keyword=search_query, selected_genre=selected_genre)

    
    return render_template('index.html', genres=genres, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
