import json, re, os
c = open('js/data.js', encoding='utf-8').read()
m = re.search(r'const siteData\s*=\s*(\{.*?\});', c, re.DOTALL)
d = json.loads(m.group(1))
for cat in ['latestJobs','results','admitCards']:
    items = d.get(cat,[])
    print(f'-- {cat}:')
    for it in items[:5]:
        print(f'  link={it.get("link","")}  title={it["title"][:45]}')
