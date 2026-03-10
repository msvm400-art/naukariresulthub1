import urllib.request
import gzip
from bs4 import BeautifulSoup
import json
import os
import time

base_dir = r"C:\Users\ALOK\Desktop\sarkarinaukari"
data_path = os.path.join(base_dir, 'js', 'data.js')

with open(data_path, 'r', encoding='utf-8') as f:
    existing_content = f.read()

import re
json_str_match = re.search(r"const siteData = (\{.*?\});", existing_content, re.DOTALL)
if json_str_match:
    data = json.loads(json_str_match.group(1))
else:
    print("Cannot parse data.js")
    exit()

def get_soup(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    if response.info().get('Content-Encoding') == 'gzip':
        html = gzip.decompress(response.read()).decode('utf-8', 'ignore')
    else:
        html = response.read().decode('utf-8', 'ignore')
    return BeautifulSoup(html, 'html.parser')

# We will scrape the dedicated pages which don't have mixed content
targets = {
    'results': 'https://www.sarkariresult.com/result/',
    'admitCards': 'https://www.sarkariresult.com/admitcard/',
    'latestJobs': 'https://www.sarkariresult.com/latestjob/'
}

for key, url in targets.items():
    print(f"Scraping dedicated {key} page...")
    soup = get_soup(url)
    
    # On dedicated pages, links are usually inside `#post` or just massive lists of `<li>` / `<a>`
    content_area = soup.find('div', id='post')
    if not content_area:
        # Fallback
        content_area = soup
        
    links = content_area.find_all('a')
    valid_links = []
    
    for a in links:
        title = a.text.strip()
        if len(title) > 10 and "facebook" not in title.lower() and "youtube" not in title.lower() and "telegram" not in title.lower() and "sarkari result" not in title.lower():
            
            # Basic sanity checks to avoid cross-pollination even on dedicated pages
            t = title.lower()
            if key == 'latestJobs' and ('result' in t or 'admit card' in t or 'answer key' in t or 'syllabus' in t or 'admission' in t or 'counseling' in t or 'cuet' in t or 'neet' in t):
                continue
            if key == 'results' and ('admit card' in t or 'exam date' in t or 'apply online' in t or 'syllabus' in t):
                continue
            if key == 'admitCards' and ('result' in t or 'apply online' in t or 'syllabus' in t):
                continue
                
            valid_links.append({"title": title, "link": "post.html"})
            
        if len(valid_links) >= 70:
            break
            
    data[key] = valid_links
    print(f"Found {len(valid_links)} clean items for {key}")

js_code = f"// data.js - Central Database for Sarkari Naukari Infos\n// Pure dedicated page data\n\nconst siteData = {json.dumps(data, indent=4)};\n"

with open(data_path, 'w', encoding='utf-8') as f:
    f.write(js_code)
print("Data updated!")
