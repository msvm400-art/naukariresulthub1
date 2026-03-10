import urllib.request
import gzip
from bs4 import BeautifulSoup

url = 'https://www.sarkariresult.com/admitcard/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = urllib.request.urlopen(req)
if response.info().get('Content-Encoding') == 'gzip':
    html = gzip.decompress(response.read()).decode('utf-8', 'ignore')
else:
    html = response.read().decode('utf-8', 'ignore')
    
soup = BeautifulSoup(html, 'html.parser')

print(soup.title)
print(html[:500])
