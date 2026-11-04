import pandas as pd

# Load CSVs
top250 = pd.read_csv('data/top250_movies.csv', index_col=False)
trending = pd.read_csv('data/trending_movies.csv', index_col=False)

# Remove pandas auto-index column if it exists
if 'Unnamed: 0' in top250.columns:
    top250 = top250.drop(columns=['Unnamed: 0'])

# Combine DataFrames
combined = pd.concat([top250, trending], ignore_index=True)

# Remove duplicates based on title
combined_clean = combined.drop_duplicates(subset='title', keep='first')

# Clean leading numbers from titles
combined_clean['title'] = combined_clean['title'].str.replace(r'^\d+\.\s*', '', regex=True)

# Optional: reset index
combined_clean.reset_index(drop=True, inplace=True)

# Save to new CSV
combined_clean.to_csv('combined_movies_cleaned.csv', index=False, encoding='utf-8-sig')

print(f"Combined CSV saved! Total movies: {len(combined_clean)}")
