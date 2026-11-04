"""Build the static GitHub Pages version of the site.

Turns combined_movies_cleaned.csv into data.json (same cleaning as app.py),
and turns templates/index.html into index.html, with the recommendation
logic from app.py running in the browser instead of on Flask.

Run from the repo root: python tools/build_static.py
"""
import json, re
import pandas as pd

df = pd.read_csv('combined_movies_cleaned.csv')
df['genres'] = df['genres'].str.replace('Back to top', '', regex=False)
rows = df[['title', 'genres', 'rating', 'description', 'link']].to_dict(orient='records')
rows = [{k: (None if (isinstance(v, float) and v != v) else v) for k, v in r.items()} for r in rows]
with open('keywords.json') as f:
    keywords = json.load(f)
json.dump({'movies': rows, 'keywords': keywords}, open('data.json', 'w'), ensure_ascii=False)

html = open('templates/index.html').read()
html = re.sub(r"\{\{ url_for\('static', filename='([^']+)'\) \}\}", r'static/\1', html)
html = html.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1">')
html = re.sub(r'\s*\{% for genre in genres %\}.*?\{% endfor %\}', '', html, flags=re.S)
html = re.sub(r'\{% if recommendations %\}.*?\{% endif %\}', '', html, flags=re.S)

engine = r'''
// Static version: the recommendation logic from app.py, running in the browser.
let MOVIES = [], KEYWORDS = {};
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const genreList = m => (m.genres || '').split(',').map(g => g.trim());

function expandKeywords(input) {
    const words = input.toLowerCase().match(/\w+/g) || [];
    const out = new Set();
    for (const w of words) { out.add(w); (KEYWORDS[w] || []).forEach(s => out.add(s)); }
    return [...out];
}

function recommendMovies(keyword, genre, topN = 10) {
    let list = MOVIES.slice();
    if (genre) list = list.filter(m => genreList(m).includes(genre));
    if (keyword && keyword.trim()) {
        const kws = expandKeywords(keyword);
        if (kws.length) {
            const re = new RegExp(kws.map(k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'), 'i');
            list = list.filter(m => re.test(m.title || '') || re.test(m.description || '') || re.test(m.genres || ''));
        }
    }
    list.sort((a, b) => (b.rating ?? -Infinity) - (a.rating ?? -Infinity));
    return list.slice(0, topN);
}

function render(recs) {
    const box = document.querySelector('#recommendations-container');
    if (!recs.length) { box.innerHTML = '<h3>No matches — try another word or genre!</h3>'; return; }
    box.innerHTML = '<h3>Top Recommendations</h3><div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">' +
        recs.map(m => `<div class="col"><div class="card card-custom h-100"><div class="card-body">
            <h5 class="card-title">${esc(m.title)}</h5>
            <p class="card-text"><strong>Genres:</strong> ${esc(m.genres)}</p>
            <p class="card-text"><strong>Rating:</strong> ${esc(m.rating)}</p>
            <p class="card-text">${esc((m.description || '').slice(0, 120))}...</p>
            <a href="${esc(m.link)}" target="_blank" rel="noopener" class="btn btn-sm">View</a>
        </div></div></div>`).join('') + '</div>';
    box.querySelectorAll('.card-custom, a.btn').forEach(el => {
        el.addEventListener('mouseenter', () => { hoverSound.currentTime = 0; hoverSound.play().catch(() => {}); });
        el.addEventListener('click', () => { clickSound.currentTime = 0; clickSound.play().catch(() => {}); });
    });
}

fetch('data.json').then(r => r.json()).then(d => {
    MOVIES = d.movies; KEYWORDS = d.keywords;
    const genres = [...new Set(MOVIES.flatMap(genreList))].filter(Boolean).sort();
    const sel = document.querySelector('select[name="genre"]');
    genres.forEach(g => { const o = document.createElement('option'); o.value = o.textContent = g; sel.appendChild(o); });
});

const form = document.getElementById('recommendation-form');
form.addEventListener('submit', function(e) {
    e.preventDefault();
    const fd = new FormData(form);
    render(recommendMovies(fd.get('search') || '', fd.get('genre') || ''));
});
'''
html = re.sub(r'// AJAX form submission.*?(?=</script>)', lambda m: engine.lstrip('\n'), html, flags=re.S)
open('index.html', 'w').write(html)
print('built index.html and data.json:', len(rows), 'titles')
