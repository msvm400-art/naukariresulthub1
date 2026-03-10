import re
import urllib.request
import gzip
from bs4 import BeautifulSoup

url = "https://www.sarkariresult.com/ssc/ssc-cgl-2024/"
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
    
    # Extract Title
    title_h1 = soup.find('h1')
    print("====== TITLE ======")
    if title_h1: print(title_h1.text.strip())

    # Extract all tables
    tables = soup.find_all('table')
    print(f"====== FOUND {len(tables)} TABLES ======")
    for table in tables:
        # Just print headers or some text to see structure
        print("TABLE START")
        for tr in table.find_all('tr')[:5]: # print first few rows
            row_data = [td.text.strip() for td in tr.find_all(['td', 'th'])]
            print(" | ".join(row_data))
        print("TABLE END\n")

except Exception as e:
    print(e)
