import os
import json
import re
import difflib

base_dir = r"C:\Users\ALOK\Desktop\sarkarinaukari"
data_path = os.path.join(base_dir, 'js', 'data.js')
posts_dir = os.path.join(base_dir, 'posts')

with open(data_path, 'r', encoding='utf-8') as f:
    existing_content = f.read()

json_str_match = re.search(r"const siteData = (\{.*?\});", existing_content, re.DOTALL)
if json_str_match:
    data = json.loads(json_str_match.group(1))
else:
    print("Cannot parse data.js")
    exit()

available_files = set(os.listdir(posts_dir))

def slugify(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    if len(slug) > 50:
        slug = slug[:50].strip('-')
    return slug + '.html'

matched = 0
total = 0

for key, items in data.items():
    for item in items:
        total += 1
        predicted = slugify(item['title'])
        if predicted in available_files:
            item['link'] = f"posts/{predicted}"
            matched += 1
        else:
            # Try finding the closest match using difflib
            matches = difflib.get_close_matches(predicted, available_files, n=1, cutoff=0.7)
            if matches:
                item['link'] = f"posts/{matches[0]}"
                matched += 1
            else:
                # If no match is found, just point to the predicted file path anyway
                item['link'] = f"posts/{predicted}"

new_js = f"// data.js - Central Database for Sarkari Naukari Infos\n// Pure dedicated page data\n\nconst siteData = {json.dumps(data, indent=4)};\n"

with open(data_path, 'w', encoding='utf-8') as f:
    f.write(new_js)

print(f"data.js successfully updated! Matched {matched} out of {total} items with actual files in posts/")
