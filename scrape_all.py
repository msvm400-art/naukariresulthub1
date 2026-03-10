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
    
    data = {
        "results": [],
        "admitCards": [],
        "latestJobs": [],
        "answerKeys": [],
        "syllabus": [],
        "admissions": [],
        "important": []
    }

    def extract_links(heading_text, data_key, limit=20):
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

    # Top columns
    extract_links("Result", "results", 20)
    extract_links("Admit Card", "admitCards", 20)
    extract_links("Latest Jobs", "latestJobs", 20)
    
    # Bottom columns
    extract_links("Answer Key", "answerKeys", 15)
    extract_links("Syllabus", "syllabus", 15)
    extract_links("Admission", "admissions", 15)
    extract_links("Important", "important", 15)

    js_code = f"// data.js - Central Database for Sarkari Naukari Infos\n// Auto-generated from scraping\n\nconst siteData = {json.dumps(data, indent=4)};\n"
    
    with open('js/data.js', 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print("Successfully populated js/data.js with real data.")

except Exception as e:
    print("Error:", e)
