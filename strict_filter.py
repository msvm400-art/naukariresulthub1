import json
import re
import os

base_dir = r"C:\Users\ALOK\Desktop\sarkarinaukari"
data_path = os.path.join(base_dir, 'js', 'data.js')

with open(data_path, 'r', encoding='utf-8') as f:
    existing_content = f.read()
    
# Extract JSON
json_str_match = re.search(r"const siteData = (\{.*?\});", existing_content, re.DOTALL)

if json_str_match:
    data = json.loads(json_str_match.group(1))
    
    # 1. Clean Latest Jobs
    # Remove anything that looks like an Admission, Result, Admit Card, Answer Key, Syllabus
    def is_job(title):
        t = title.lower()
        bad_words = [
            'admission', 'admissions', 'entrance', 'counseling', 'cuet', 'neet', 'jee ', 'bhu set', 'iert ',
            'result', 'score card', 'merit list', 'cut off',
            'admit card', 'exam city', 'exam date', 'exam schedule',
            'answer key', 'syllabus', 'certificate', 'online form re open' # re open is usually admission or late form, but cuet/neet mostly
        ]
        
        # Specifically target the admission ones you noticed:
        if 'cuet' in t or 'neet' in t or 'bhu set' in t or 'iert' in t or 'cpct' in t or 'imu cet' in t:
            return False
            
        for w in bad_words:
            if w in t:
                return False
        return True
        
    original_jobs = data['latestJobs']
    data['latestJobs'] = [item for item in original_jobs if is_job(item['title'])]
    
    # Let's also clean Results to ensure no Admit Cards snuck in
    def is_result(title):
        t = title.lower()
        if 'admit card' in t or 'exam city' in t or 'exam date' in t or 'answer key' in t or 'syllabus' in t or 'apply online' in t or 'online form' in t:
            return False
        return True
        
    original_results = data['results']
    data['results'] = [item for item in original_results if is_result(item['title'])]
    
    # Let's clean Admit Cards to ensure no Results snuck in
    def is_admit_card(title):
        t = title.lower()
        if 'result' in t or 'answer key' in t or 'syllabus' in t or 'apply online' in t or 'online form' in t: # Except maybe exam city/date which are related to admit cards
            return False
        return True
        
    original_ac = data['admitCards']
    data['admitCards'] = [item for item in original_ac if is_admit_card(item['title'])]
    
    
    js_code = f"// data.js - Central Database for Sarkari Naukari Infos\n// Strictly Filtered\n\nconst siteData = {json.dumps(data, indent=4)};\n"
    
    with open(data_path, 'w', encoding='utf-8') as f:
        f.write(js_code)
        
    print(f"Cleaned Jobs: {len(original_jobs)} -> {len(data['latestJobs'])}")
    print(f"Cleaned Results: {len(original_results)} -> {len(data['results'])}")
    print(f"Cleaned Admit Cards: {len(original_ac)} -> {len(data['admitCards'])}")
else:
    print("Could not parse JSON")
