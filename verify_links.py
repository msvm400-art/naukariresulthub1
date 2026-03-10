import json, re, os

BASE_DIR = r"C:\Users\ALOK\Desktop\sarkarinaukari"
POSTS_DIR = os.path.join(BASE_DIR, "posts")

c = open('js/data.js', encoding='utf-8').read()
m = re.search(r'const siteData\s*=\s*(\{.*?\});', c, re.DOTALL)
d = json.loads(m.group(1))

total = 0
correct = 0
broken = []

for cat, items in d.items():
    if not isinstance(items, list): continue
    for it in items:
        lnk = it.get("link", "")
        if lnk.startswith("http"):
            correct += 1; total += 1; continue
        fn = lnk.replace("posts/", "")
        total += 1
        fp = os.path.join(POSTS_DIR, fn)
        if os.path.exists(fp):
            correct += 1
        else:
            broken.append((cat, it['title'][:50], lnk))

print(f"Total: {total}, Correct: {correct}, Broken: {len(broken)}")
if broken:
    for b in broken[:15]:
        print(f"  BROKEN [{b[0]}] {b[1]} -> {b[2]}")

# Check sample - first 5 in each cat
for cat in ['latestJobs','results','admitCards']:
    items = d.get(cat, [])
    print(f"\n{cat}:")
    for it in items[:5]:
        slug = it['link'].replace('posts/','')
        title_slug = it['title'].lower()[:20]
        print(f"  {it['link'][:55]}  | title starts: {it['title'][:40]}")
