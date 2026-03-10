import json, re
c = open('js/data.js', encoding='utf-8').read()
m = re.search(r'const siteData\s*=\s*(\{.*?\});', c, re.DOTALL)
d = json.loads(m.group(1))
for cat in ['latestJobs', 'results', 'admitCards']:
    items = d.get(cat, [])
    print(f'\n=== {cat} (top 8) ===')
    for it in items[:8]:
        ts = it.get('ts', 0)
        s = str(ts)
        if len(s)==8:
            fmt = s[6:]+'/'+s[4:6]+'/'+s[:4]
        elif len(s)==6:
            fmt = s[4:]+'/'+s[:4]
        else:
            fmt = str(ts)
        print(f'  {fmt}  {it["title"][:55]}')
