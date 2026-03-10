import os
from bs4 import BeautifulSoup

base_dir = r"C:\Users\ALOK\Desktop\sarkarinaukari"
pages = ["results.html", "admitcard.html", "jobs.html", "answerkey.html", "syllabus.html", "admission.html", "important.html"]

for page in pages:
    filepath = os.path.join(base_dir, page)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
        script_data = soup.find('script', src='js/data.js')
        script_main = soup.find('script', src='js/main.js')
        
        # If there are old trailing spaces, find them
        if not script_main:
            for script in soup.find_all('script'):
                if script.get('src') and 'main.js' in script.get('src'):
                    script_main = script
        
        modified = False
        if not script_main:
            script_main = soup.new_tag('script', src='js/main.js')
            soup.body.append(script_main)
            modified = True
            
        if not script_data:
            script_data = soup.new_tag('script', src='js/data.js')
            # Insert before main.js
            script_main.insert_before(script_data)
            modified = True

        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print(f"Fixed scripts in {page}")
    else:
        print(f"File {page} not found.")

