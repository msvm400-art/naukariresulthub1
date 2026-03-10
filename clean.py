from bs4 import BeautifulSoup

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    
    # Map column headers to JSON keys
    mapping = {
        'Result': 'results',
        'Admit Card': 'admitCards',
        'Latest Jobs': 'latestJobs',
        'Answer Key': 'answerKeys',
        'Syllabus': 'syllabus',
        'Admission': 'admissions',
        'Important': 'important',
        'Important Links List': 'important'
    }

    modified = False
    for column in soup.find_all('div', class_='job-column'):
        header = column.find('h2') or column.find('h3')
        if header:
            text = header.text.strip()
            # Match text to mapping
            for key, json_key in mapping.items():
                if key in text:
                    job_list = column.find('div', class_='job-list')
                    if job_list:
                        job_list['id'] = f'list-{json_key}'
                        job_list.clear() # removes all hardcoded items
                        comment = soup.new_string(" Data will be loaded dynamically from js/data.js ")
                        from bs4 import Comment
                        job_list.append(Comment(comment))
                        modified = True
                        break

    # Also make sure data.js is loaded
    if modified:
        body = soup.find('body')
        if body:
            # check if data.js already exists
            scripts = [s.get('src') for s in body.find_all('script')]
            if 'js/data.js' not in scripts:
                # Find main.js and insert before it
                main_js = body.find('script', src='js/main.js')
                new_script = soup.new_tag('script', src='js/data.js')
                if main_js:
                    main_js.insert_before(new_script)
                else:
                    body.append(new_script)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"Processed {filepath}")

# Process all relevant HTML files
files = ['index.html', 'results.html', 'admitcard.html', 'jobs.html', 'answerkey.html', 'syllabus.html', 'admission.html', 'important.html']
import os
for f in files:
    path = os.path.join(r'C:\Users\ALOK\Desktop\sarkarinaukari', f)
    if os.path.exists(path):
        process_file(path)
