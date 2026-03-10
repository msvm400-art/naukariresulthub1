import urllib.request
from bs4 import BeautifulSoup
import re
import gzip

def extract_data(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        html = gzip.decompress(response.read()).decode('utf-8') if response.info().get('Content-Encoding') == 'gzip' else response.read().decode('utf-8', 'ignore')
    except Exception as e:
        print(e)
        return
        
    soup = BeautifulSoup(html, 'html.parser')
    
    dates_html = ""
    fee_html = ""
    age_html = ""
    vacancy_html = ""
    links_html = ""
    
    # 1. Important Dates & Fees
    for td in soup.find_all('td'):
        text = td.get_text().lower()
        if 'important date' in text and 'application begin' in text:
            # Found dates cell
            ul = td.find('ul')
            if ul:
                # Copy list items but without styles
                for li in ul.find_all('li'):
                    dates_html += f"<li>{li.get_text(' ', strip=True)}</li>\n"
        elif 'application fee' in text and ('general' in text or 'obc' in text):
            # Found fee cell
            ul = td.find('ul')
            if ul:
                for li in ul.find_all('li'):
                    fee_html += f"<li>{li.get_text(' ', strip=True)}</li>\n"
        elif 'age limit' in text and 'minimum' in text:
            ul = td.find('ul')
            if ul:
                for li in ul.find_all('li'):
                    age_html += f"<li>{li.get_text(' ', strip=True)}</li>\n"

    # 2. Vacancy Details
    # Usually a table with th containing 'Post Name'
    for table in soup.find_all('table'):
        text = table.get_text().lower()
        if 'post name' in text and 'total' in text and 'eligibility' in text:
            # This is the vacancy table
            # Exclude the outermost table if multiple nested
            if not table.find('table'):
                # Strip all inline styles and classes
                for tag in table.find_all(True):
                    tag.attrs = {}
                vacancy_html = str(table)
                break
                
    # 3. Links
    links_table = ""
    for table in soup.find_all('table'):
        if 'apply online' in table.get_text().lower() and not table.find('table'):
            for tr in table.find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) >= 2:
                    label = tds[0].get_text(strip=True)
                    a_tags = tds[1].find_all('a')
                    if a_tags:
                        links_html += f"<tr><td>{label}</td><td>"
                        for a in a_tags:
                            links_html += f"<a href='{a.get('href')}'>{a.get_text(strip=True) or 'Click Here'}</a> "
                        links_html += "</td></tr>\n"

    print("--- DATES ---")
    print(dates_html)
    print("--- FEES ---")
    print(fee_html)
    print("--- AGE ---")
    print(age_html)
    print("--- VACANCY ---")
    print(vacancy_html[:200], "...")
    print("--- LINKS ---")
    print(links_html)

extract_data('https://www.sarkariresult.com/ssc/ssc-cgl-2024/')
