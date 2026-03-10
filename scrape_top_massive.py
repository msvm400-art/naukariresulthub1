import re
import urllib.request
import gzip
from bs4 import BeautifulSoup
import json
import os

url = "https://www.sarkariresult.com/"
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive'
})

try:
    response = urllib.request.urlopen(req)
    if response.info().get('Content-Encoding') == 'gzip':
        html = gzip.decompress(response.read()).decode('utf-8')
    else:
        html = response.read().decode('utf-8')

    soup = BeautifulSoup(html, 'html.parser')
    
    # We will only overwrite the top 3 columns, the bottom 4 will remain from our curated static list
    # Because those bottom 4 were specifically generated with high-quality SEO content by us earlier.
    
    data = {
        "results": [],
        "admitCards": [],
        "latestJobs": []
    }

    def extract_links(heading_text, data_key, limit=50):
        headings = soup.find_all('div', id='heading')
        target_heading = None
        for h in headings:
            if heading_text.lower() in h.text.lower():
                target_heading = h
                break
                
        if target_heading:
            parent = target_heading.parent
            if parent:
                links = parent.find_all('a')
                count = 0
                for a in links:
                    title = a.text.strip()
                    if title and title.lower() not in ['view more', 'home', 'latest jobs', 'results', 'admit card', 'answer key', 'syllabus', 'search', 'contact us']:
                        if "facebook" not in title.lower() and "youtube" not in title.lower() and "instagram" not in title.lower() and "telegram" not in title.lower() and "whatsapp" not in title.lower() and "apple" not in title.lower() and "android" not in title.lower() and "twitter" not in title.lower() and title.lower() != heading_text.lower():
                            data[data_key].append({'title': title, 'link': 'post.html'})
                            count += 1
                            if count >= limit:
                                break

    extract_links("Result", "results", 50)
    extract_links("Admit Card", "admitCards", 50)
    extract_links("Latest Jobs", "latestJobs", 80) # More jobs since it's the primary column

    # Now we need to read the existing data.js, parse out the bottom 4 columns, and stitch them together
    base_dir = r"C:\Users\ALOK\Desktop\sarkarinaukari"
    data_path = os.path.join(base_dir, 'js', 'data.js')
    
    with open(data_path, 'r', encoding='utf-8') as f:
        existing_content = f.read()
        
    # Hacky but reliable way to extract JSON from the JS file since it's statically formatted
    json_str_match = re.search(r"const siteData = (\{.*?\});", existing_content, re.DOTALL)
    
    if json_str_match:
        existing_data = json.loads(json_str_match.group(1))
        
        # Merge our newly scraped real 50+ items in
        existing_data['results'] = data['results']
        existing_data['admitCards'] = data['admitCards']
        existing_data['latestJobs'] = data['latestJobs']
        
        js_code = f"// data.js - Central Database for Sarkari Naukari Infos\n// Top 3 columns auto-updated with 50+ records\n\nconst siteData = {json.dumps(existing_data, indent=4)};\n"
        
        with open(data_path, 'w', encoding='utf-8') as f:
            f.write(js_code)
        
        print(f"Successfully populated js/data.js with {len(data['results'])} results, {len(data['admitCards'])} admit cards, and {len(data['latestJobs'])} latest jobs.")
    else:
        print("Could not find json in data.js")

except Exception as e:
    print("Error:", e)
