import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Load the combined CSV
combined = pd.read_csv('combined_movies.csv', index_col=False)

# Remove 'Back to top' from genres
combined['genres'] = combined['genres'].str.replace('Back to top', '', regex=False)

# Split genres by comma, strip whitespace, and explode into separate rows
all_genres = combined['genres'].str.split(',').explode().str.strip()

# Count occurrences of each genre
genre_counts = all_genres.value_counts()

# ------------------- BAR CHART -------------------
# Keep top 20 genres for readability
top_genres = genre_counts.head(20)

plt.figure(figsize=(14,7))
top_genres.plot(kind='bar', color='skyblue')
plt.title('Top 20 Movie Genres', fontsize=16)
plt.xlabel('Genre', fontsize=12)
plt.ylabel('Number of Movies', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# ------------------- WORD CLOUD -------------------
# Create a dictionary for word cloud
genre_dict = genre_counts.to_dict()

wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='tab10')
wordcloud.generate_from_frequencies(genre_dict)

plt.figure(figsize=(15,7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Movie Genres Word Cloud', fontsize=18)
plt.show()
