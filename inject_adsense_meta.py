import os
from bs4 import BeautifulSoup

base_dir = r"C:\Users\ALOK\Desktop\sarkarinaukari"

adsense_meta = """<meta name="google-adsense-account" content="ca-pub-8244601197032455">"""

# Injection logic
for filename in os.listdir(base_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(base_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # Check if already injected
        head = soup.find('head')
        if head:
            # Check to avoid duplicate injection
            existing_meta = head.find('meta', attrs={"name": "google-adsense-account"})
            if not existing_meta:
                import bs4
                meta_soup = bs4.BeautifulSoup(adsense_meta, 'html.parser')
                # insert it before the closing head tag
                head.append(meta_soup)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(soup.prettify(formatter="html5"))
                print(f"Added AdSense meta tag to {filename}")
            else:
                print(f"AdSense meta tag already in {filename}")
