import os
import json
import re
import urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import gzip
import time
import concurrent.futures

base_dir = r"C:\Users\ALOK\Desktop\sarkarinaukari"
data_path = os.path.join(base_dir, 'js', 'data.js')
posts_dir = os.path.join(base_dir, 'posts')

# Template string with placeholders
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Sarkari Naukari Infos</title>
    <meta name="description" content="Complete details of {title} including Important Dates, Application Fee, Vacancy Details, and Apply Online Links.">
    <link rel="stylesheet" href="../css/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .detailed-info-box {{
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1.5rem;
            margin-bottom: 2rem;
            background: rgba(67, 97, 238, 0.02);
            box-shadow: var(--shadow-sm);
        }}
        .detailed-info-box h2 {{
            font-size: 1.4rem;
            text-align: center;
            margin-bottom: 1rem;
            border-bottom: 2px solid var(--primary-light);
            padding-bottom: 0.5rem;
        }}
        .highlight-magenta {{ color: #d63384; font-weight: bold; }}
        .highlight-green {{ color: #198754; font-weight: bold; }}
        .highlight-blue {{ color: #0d6efd; font-weight: bold; }}

        .custom-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: center;
            border: 2px solid var(--border);
            margin-bottom: 2.5rem;
            box-shadow: var(--shadow-sm);
        }}
        .custom-table th {{
            padding: 1.2rem;
            border: 1px solid var(--border);
            background: rgba(67, 97, 238, 0.08);
            color: var(--text-main);
            font-size: 1.1rem;
        }}
        .custom-table td {{
            padding: 1.2rem;
            border: 1px solid var(--border);
            color: var(--text-main);
            vertical-align: top;
        }}
        .custom-table a {{
            color: #0d6efd;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s;
        }}
        .custom-table a:hover {{
            color: #0a58ca;
            text-decoration: underline;
        }}
        ul.custom-list {{
            list-style: none;
            padding-left: 0;
        }}
        ul.custom-list li {{
            position: relative;
            padding-left: 25px;
            margin-bottom: 0.8rem;
            line-height: 1.6;
        }}
        ul.custom-list li::before {{
            content: "\\f0da"; /* FontAwesome caret right */
            font-family: "Font Awesome 6 Free";
            font-weight: 900;
            position: absolute;
            left: 0;
            color: var(--primary);
        }}
    </style>
</head>
<body>
    <div class="header-top">Sarkari Naukari Infos - Your Trusted Source for Government Job Updates</div>
    <header class="site-header">
        <div class="container nav-container">
            <a href="../index.html" class="logo">
                <div class="logo-main">Sarkari<span>Naukari</span></div>
                <div class="logo-sub">Infos .Net</div>
            </a>
            <nav class="main-nav">
                <a href="../index.html" class="nav-link">Home</a>
                <a href="../jobs.html" class="nav-link">Latest Jobs</a>
                <a href="../results.html" class="nav-link">Results</a>
                <a href="../admitcard.html" class="nav-link">Admit Card</a>
            </nav>
        </div>
    </header>

    <div class="post-header" style="background: linear-gradient(to right, var(--primary), #60a5fa); padding: 3rem 0; margin-bottom: 2rem;">
        <div class="container">
            <h1 class="post-title" style="font-size: 2.2rem; margin-bottom: 0;">{title}</h1>
        </div>
    </div>

    <main class="container animate-fade-in" style="max-width: 900px; margin: 0 auto; background: var(--surface); padding: 2.5rem; border-radius: var(--radius-lg); box-shadow: var(--shadow-md);">
        
        <div style="text-align:center; margin-bottom: 2rem;">
            <p style="font-size: 1.1rem; color: var(--primary); font-weight: 700;">Short Details of Notification</p>
            <p style="color: var(--text-muted); line-height: 1.6;">Sarkari Naukari Infos is providing the exact latest updates for {title}. Candidate can read the official notification before applying or checking status.</p>
        </div>

        {content}

        <!-- Important Links Table -->
        <h2 class="highlight-magenta" style="text-align: center; margin-bottom: 1.5rem; font-size: 1.4rem; line-height:1.4;">Interested Candidates Can Read the Full Notification Before Apply Online</h2>
        <div style="overflow-x: auto;">
            <table class="custom-table" style="font-size: 1.1rem;">
                <tbody>
                    <!-- Apps Header -->
                    <tr>
                        <td colspan="2" class="highlight-green" style="font-size: 1.4rem; background: rgba(25, 135, 84, 0.05); padding: 1.5rem;">Download Mobile Apps for the Latest Updates</td>
                    </tr>
                    <tr>
                        <td style="width: 50%;"><a href="https://play.google.com/store/apps/details?id=com.app.sarkariresult" target="_blank"><i class="fab fa-android highlight-green"></i> Android Apps</a></td>
                        <td style="width: 50%;"><a href="https://apps.apple.com/in/app/sarkari-result/id1051363935" target="_blank"><i class="fab fa-apple highlight-magenta"></i> Apple IOS Apps</a></td>
                    </tr>
                    
                    <!-- Links Header -->
                    <tr>
                        <td colspan="2" class="highlight-green" style="font-size: 1.4rem; background: rgba(25, 135, 84, 0.05); padding: 1.5rem;">Some Useful Important Links</td>
                    </tr>
                    {links_html}
                </tbody>
            </table>
        </div>
    </main>
</body>
</html>
"""

def fetch_page(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36'
    })
    try:
        response = urllib.request.urlopen(req, timeout=10)
        if response.info().get('Content-Encoding') == 'gzip':
            html = gzip.decompress(response.read()).decode('utf-8', 'ignore')
        else:
            html = response.read().decode('utf-8', 'ignore')
        return html
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def process_item(item):
    title = item['title']
    target_link = item['link']
    
    # Check if this link exists and corresponds to a file in posts/
    if not target_link.startswith('posts/'):
        return
        
    filename = target_link.split('posts/')[1]
    filepath = os.path.join(posts_dir, filename)
    
    # We will search the real sarkariresult site for the URL
    search_slug = filename.replace('.html', '')
    
    # Let's search inside the main page for this exact title or a very close approximation
    return filepath, title, search_slug

def run_scraper():
    with open(data_path, 'r', encoding='utf-8') as f:
        existing_content = f.read()

    json_str_match = re.search(r"const siteData = (\{.*?\});", existing_content, re.DOTALL)
    if not json_str_match:
        print("Cannot parse data.js")
        return

    data = json.loads(json_str_match.group(1))
    
    # We will grab the homepage of target site to find URLs for everything
    print("Fetching master list from original site...")
    master_html = fetch_page("https://www.sarkariresult.com/")
    if not master_html:
        return
        
    master_soup = BeautifulSoup(master_html, 'html.parser')
    all_links = master_soup.find_all('a', href=True)
    
    link_map = {}
    for a in all_links:
        t = a.text.strip()
        href = a['href']
        if t and len(t) > 5 and 'youtube' not in href and 'facebook' not in href:
            link_map[t] = href

    missing_urls = 0
    generated = 0
    
    # Because scraping 150+ pages sequentially is slow, we will gather items first
    tasks = []
    
    for category in ['results', 'admitCards', 'latestJobs']:
        for item in data[category]:
            t = item['title']
            # Find the match in the scraped links
            target_url = None
            if t in link_map:
                target_url = link_map[t]
            else:
                # Try finding a partial match
                for original_title, url in link_map.items():
                    if t[:20].lower() in original_title.lower() or original_title[:20].lower() in t.lower():
                        target_url = url
                        break
                        
            if target_url:
                if not target_url.startswith('http'):
                    continue # Ignore relative weird things just in case
                tasks.append((item, target_url))
            else:
                missing_urls += 1
                
    print(f"Found URLs for {len(tasks)} items. Missing {missing_urls}.")
    print("Starting concurrent scrape & build...")
    
    def process_task(task):
        item, url = task
        title = item['title']
        if not item['link'].startswith('posts/'):
            return False
            
        filepath = os.path.join(posts_dir, item['link'].split('posts/')[1])
        
        post_html = fetch_page(url)
        if not post_html:
            return False
            
        soup = BeautifulSoup(post_html, 'html.parser')
        
        # Extract tables from post content
        content_tables = soup.find_all('table')
        
        extracted_content = ""
        links_html = ""
        
        for table in content_tables:
            # Check if this table has links
            links_in_table = table.find_all('a')
            if len(links_in_table) > 0 and 'apply' in table.text.lower():
                # This is likely the links table
                for tr in table.find_all('tr'):
                    tds = tr.find_all('td')
                    if len(tds) >= 2:
                        label = tds[0].text.strip()
                        link_tags = tds[1].find_all('a')
                        
                        link_parts = []
                        for a_tag in link_tags:
                            href = a_tag.get('href', '#')
                            text = a_tag.text.strip() or 'Click Here'
                            
                            # Determine icon
                            icon = '<i class="fas fa-external-link-alt"></i>'
                            if 'Notification' in label:
                                icon = '<i class="fas fa-file-pdf"></i>'
                            elif 'Telegram' in label:
                                icon = '<i class="fab fa-telegram"></i>'
                            elif 'Official' in label:
                                icon = '<i class="fas fa-globe"></i>'
                                
                            link_parts.append(f'<a href="{href}" target="_blank" class="btn btn-outline" style="display:inline-block; padding:0.5rem 1rem; margin:0.2rem;"><span style="margin-right:0.4rem">{icon}</span> {text}</a>')
                        
                        if link_parts:
                            links_html += f'''
                    <tr>
                        <td class="highlight-magenta" style="font-weight:bold; vertical-align:middle;">{label}</td>
                        <td style="vertical-align:middle;">{' '.join(link_parts)}</td>
                    </tr>'''
            else:
                # Formatting regular data tables to blend into our premium layout
                # Just keep raw HTML but apply our classes
                table['class'] = ['custom-table']
                table['border'] = '1'
                table['cellpadding'] = '5'
                # Wrap it to match styling
                extracted_content += f'<div style="overflow-x: auto; margin-bottom: 2rem;">{str(table)}</div>'
        
        if not links_html:
             links_html = '''
                    <tr>
                        <td class="highlight-magenta" style="font-weight:bold; vertical-align:middle;">Apply Online</td>
                        <td style="vertical-align:middle;"><a href="#" class="btn btn-outline" style="display:inline-block; padding:0.5rem 1.5rem; margin:0;"><i class="fas fa-external-link-alt"></i> Link Available Soon</a></td>
                    </tr>'''
                    
        final_html = HTML_TEMPLATE.format(
            title=title,
            content=extracted_content,
            links_html=links_html
        )
        
        try:
            with open(filepath, 'w', encoding='utf-8') as pf:
                pf.write(final_html)
            return True
        except Exception as e:
            return False

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_task, tasks))
        
    print(f"Successfully generated {sum(1 for r in results if r)} deep posts.")

if __name__ == '__main__':
    run_scraper()
