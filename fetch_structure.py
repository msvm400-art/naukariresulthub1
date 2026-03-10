import urllib.request
from bs4 import BeautifulSoup
import gzip

url = "https://www.sarkariresult.com/"
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0'
})

response = urllib.request.urlopen(req)
if response.info().get('Content-Encoding') == 'gzip':
    html = gzip.decompress(response.read()).decode('utf-8', 'ignore')
else:
    html = response.read().decode('utf-8', 'ignore')

soup = BeautifulSoup(html, 'html.parser')

with open("sarkari_dump.html", "w", encoding='utf-8') as f:
    f.write(soup.prettify())
