import json, re, os

dat_path = r'js/data.js'
with open(dat_path, encoding='utf-8') as f:
    content = f.read()

m = re.search(r'const siteData\s*=\s*(\{.*?\});', content, re.DOTALL)
if not m:
    print("Could not find siteData in data.js")
    exit(1)

siteData = json.loads(m.group(1))

print("Checking links in data.js...")
all_unique = True
seen_links = set()
total_links = 0

for cat, items in siteData.items():
    if not isinstance(items, list): continue
    for item in items:
        link = item.get('link')
        title = item.get('title')
        total_links += 1
        if link in seen_links and not link.startswith('http'):
            print(f"DUPLICATE LINK FOUND: {link} (Title: {title})")
            all_unique = False
        seen_links.add(link)

print(f"Total links checked: {total_links}")
print(f"Unique links: {len(seen_links)}")
if all_unique:
    print("SUCCESS: All post links are unique.")
else:
    print("WARNING: Some links are duplicated.")

print("\nSample check:")
for it in siteData.get('latestJobs', [])[:5]:
    print(f" - {it['title'][:40]} -> {it['link']}")
