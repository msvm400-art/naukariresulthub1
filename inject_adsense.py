import os
from bs4 import BeautifulSoup

base_dir = r"C:\Users\ALOK\Desktop\sarkarinaukari"

adsense_code = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8244601197032455"
     crossorigin="anonymous"></script>
"""

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
            existing_script = head.find('script', src=lambda s: s and "adsbygoogle.js" in s)
            if not existing_script:
                import bs4
                adsense_soup = bs4.BeautifulSoup(adsense_code, 'html.parser')
                # insert it before the closing head tag (or append)
                head.append(adsense_soup)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(soup.prettify())
                print(f"Added AdSense to {filename}")
            else:
                print(f"AdSense already in {filename}")
