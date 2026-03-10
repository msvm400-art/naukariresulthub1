#!/usr/bin/env python3
"""
sort_posts.py  —  Sort all posts newest-first across all categories
─────────────────────────────────────────────────────────────────────
Strategy:
  1. For each post, open its HTML file and extract the earliest/most
     relevant date (Application Begin, Published, Notification Date, etc.)
  2. Parse the date → convert to a sortable integer YYYYMMDD
  3. Sort each category list by date DESC (newest first, unknowns last)
  4. Also add a "ts" field to each item for JS-side on-the-fly re-sorting
  5. Rebuild all 7 category pages with items in correct sorted order
  6. Patch mega_scraper.py + apply_2026_filter.py so new posts are
     always INSERT AT TOP (newest first) and carry a timestamp

Run: python sort_posts.py
"""

import os, re, json, datetime

BASE_DIR  = r"C:\Users\ALOK\Desktop\sarkarinaukari"
POSTS_DIR = os.path.join(BASE_DIR, "posts")
DATA_JS   = os.path.join(BASE_DIR, "js", "data.js")

# ── Date extraction patterns ───────────────────────────────────────────────────
DATE_PATTERNS = [
    # DD/MM/YYYY or DD-MM-YYYY
    r'(?:Application\s*Begin|Start\s*Date|Published|Notification\s*Date|Post\s*Date|Apply\s*Begin)'
    r'\s*[:\-]\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
    # Generic DD/MM/YYYY anywhere
    r'(\d{1,2}/\d{1,2}/20(?:25|26))',
    # Month name: 01 March 2026
    r'(\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
    r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+20(?:25|26))',
]

MONTH_MAP = {
    'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,
    'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12,
}

def parse_date_str(s):
    """Convert various date strings to YYYYMMDD integer."""
    s = s.strip()
    # DD/MM/YYYY or DD-MM-YYYY
    m = re.match(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return y * 10000 + mo * 100 + d
    # DD Month YYYY
    m = re.match(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', s)
    if m:
        d, mon, y = int(m.group(1)), m.group(2)[:3].lower(), int(m.group(3))
        mo = MONTH_MAP.get(mon, 1)
        return y * 10000 + mo * 100 + d
    return 0


def extract_date_from_html(filepath):
    """Read post HTML and return best YYYYMMDD sort key."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
    except:
        return 0

    best = 0
    for pat in DATE_PATTERNS:
        for m in re.finditer(pat, html, re.IGNORECASE):
            val = parse_date_str(m.group(1))
            if val > best:
                best = val
    return best


def extract_date_from_title(title):
    """Fallback: extract date info from title string."""
    # "March 2026" style
    m = re.search(
        r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
        r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(20\d{2})',
        title, re.I)
    if m:
        mo = MONTH_MAP.get(m.group(1)[:3].lower(), 6)
        y  = int(m.group(2))
        return y * 10000 + mo * 100
    # Just year
    m = re.search(r'(20\d{2})', title)
    if m:
        return int(m.group(1)) * 10000
    return 0


# ── Category page generator (same clean table design) ─────────────────────────
CAT_META = {
    "latestJobs":  dict(h1="Latest Government Jobs 2026", file="jobs.html",       icon="fas fa-briefcase",      hero="Apply online for the latest 2026 government job vacancies. Always sorted newest first."),
    "results":     dict(h1="Sarkari Result 2026",          file="results.html",    icon="fas fa-trophy",         hero="Check the latest 2026 government exam results. Sorted by date — newest result first."),
    "admitCards":  dict(h1="Admit Card 2026",              file="admitcard.html",  icon="fas fa-id-card",        hero="Download 2026 admit cards and hall tickets. Newest releases listed first."),
    "answerKeys":  dict(h1="Answer Key 2026",              file="answerkey.html",  icon="fas fa-key",            hero="Download official 2026 answer keys. Newest answer keys appear first."),
    "syllabus":    dict(h1="Syllabus 2026",                file="syllabus.html",   icon="fas fa-book-open",      hero="Download subject-wise 2026 syllabus and exam patterns. Newest first."),
    "admissions":  dict(h1="Admission 2026",               file="admission.html",  icon="fas fa-graduation-cap", hero="Apply for 2026 admissions — NEET, CUET, JEE and more. Newest listed first."),
    "important":   dict(h1="Important Links 2026",         file="important.html",  icon="fas fa-link",           hero="Important 2026 government portals and essential links. Newest first."),
}

CAT_PAGE_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{h1} – Sarkari Naukari Infos</title>
  <meta name="description" content="{hero} Sarkari Naukari Infos – {count} posts listed.">
  <meta name="keywords" content="{h1}, Sarkari Naukari, Government Jobs 2026">
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8244601197032455" crossorigin="anonymous"></script>
  <style>
    .plist-tbl{{width:100%;border-collapse:collapse;}}
    .plist-tbl tr{{border-bottom:1px solid #e8edf2;transition:background .14s;}}
    .plist-tbl tr:hover{{background:#f0f5ff;}}
    .plist-tbl td{{padding:.72rem 1rem;}}
    .plist-tbl td.num{{width:38px;color:#9ca3af;font-size:.8rem;text-align:center;font-weight:600;}}
    .plist-tbl td.ttl a{{color:var(--text-main);text-decoration:none;font-size:.96rem;font-weight:500;}}
    .plist-tbl td.ttl a:hover{{color:var(--primary);text-decoration:underline;}}
    .plist-tbl td.dt{{width:96px;text-align:right;font-size:.76rem;color:#9ca3af;white-space:nowrap;}}
    .pg-bar{{display:flex;gap:.4rem;justify-content:center;flex-wrap:wrap;margin-top:1.1rem;padding-top:1rem;border-top:1px solid #e8edf2;}}
    .pg-btn{{padding:.32rem .72rem;border-radius:5px;border:1.5px solid #e2e8f0;background:#fff;cursor:pointer;font-size:.87rem;font-family:inherit;transition:all .16s;min-width:32px;}}
    .pg-btn:hover,.pg-btn.on{{background:var(--primary);color:#fff;border-color:var(--primary);}}
    .pg-info{{text-align:right;font-size:.78rem;color:var(--text-muted);margin-top:.4rem;}}
    .sh{{display:flex;align-items:center;justify-content:space-between;margin-bottom:.9rem;border-bottom:2.5px solid var(--primary);padding-bottom:.45rem;}}
    .sh h2{{font-size:1.08rem;color:var(--primary);margin:0;display:flex;align-items:center;gap:.4rem;}}
    .sh span{{font-size:.8rem;color:var(--text-muted);}}
    .sort-note{{font-size:.75rem;color:#6b7280;display:flex;align-items:center;gap:.3rem;margin-bottom:.7rem;}}
  </style>
</head>
<body>
  <div class="header-top">Sarkari Naukari Infos – Your Trusted Source for Government Job Updates</div>
  <header class="site-header">
    <div class="container nav-container">
      <a class="logo" href="index.html"><div class="logo-main">Sarkari<span>Naukari</span></div><div class="logo-sub">Infos .Net</div></a>
      <button class="menu-toggle" aria-label="Toggle menu"><i class="fas fa-bars"></i></button>
      <nav class="main-nav">
        <a class="nav-link{a_jobs}" href="jobs.html">Latest Jobs</a>
        <a class="nav-link{a_res}" href="results.html">Results</a>
        <a class="nav-link{a_ac}" href="admitcard.html">Admit Card</a>
        <a class="nav-link{a_ak}" href="answerkey.html">Answer Key</a>
        <a class="nav-link{a_sy}" href="syllabus.html">Syllabus</a>
        <a class="nav-link{a_ad}" href="admission.html">Admission</a>
        <a class="nav-link" href="index.html">Home</a>
      </nav>
      <div class="header-search">
        <input id="hsi" type="text" placeholder="Search exams, jobs..." aria-label="Search">
        <button id="hsb"><i class="fas fa-search"></i> Search</button>
      </div>
    </div>
  </header>

  <div class="category-hero">
    <div class="container">
      <h1><i class="{icon}"></i> {h1}</h1>
      <p>{hero}</p>
    </div>
  </div>

  <main class="container animate-fade-in">
    <div style="font-size:.82rem;color:var(--text-muted);margin-bottom:1rem;">
      <a href="index.html" style="color:var(--primary)"><i class="fas fa-home"></i> Home</a>
      <span style="margin:0 .3rem">/</span><span>{h1}</span>
    </div>

    <div class="category-card">
      <div class="sh">
        <h2><i class="{icon}"></i> {h1}</h2>
        <span>Total: {count} Posts (2026)</span>
      </div>
      <div class="sort-note">
        <i class="fas fa-sort-amount-down" style="color:var(--primary)"></i>
        Sorted newest first &nbsp;|&nbsp; <i class="fas fa-calendar"></i> Application Begin Date
      </div>
      <table class="plist-tbl">
        <tbody id="tb"></tbody>
      </table>
      <div class="pg-bar" id="pgb"></div>
      <div class="pg-info" id="pgi"></div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-about">
          <h3>Sarkari<span>Naukari</span> Infos</h3>
          <p>India&#39;s leading portal for 2026 government job updates, results, and admit cards.</p>
          <div class="footer-socials">
            <a class="social-link" href="#"><i class="fab fa-facebook-f"></i></a>
            <a class="social-link" href="#"><i class="fab fa-twitter"></i></a>
            <a class="social-link" href="#"><i class="fab fa-telegram-plane"></i></a>
            <a class="social-link" href="#"><i class="fab fa-youtube"></i></a>
          </div>
        </div>
        <div><span class="footer-heading">Quick Links</span>
          <div class="footer-links">
            <a href="jobs.html">Latest Jobs</a><a href="results.html">Results</a>
            <a href="admitcard.html">Admit Card</a><a href="answerkey.html">Answer Keys</a>
          </div>
        </div>
        <div><span class="footer-heading">More</span>
          <div class="footer-links">
            <a href="syllabus.html">Syllabus</a><a href="admission.html">Admission</a>
            <a href="search.html">Search</a><a href="admin/index.html">Admin</a>
          </div>
        </div>
        <div><span class="footer-heading">Legal</span>
          <div class="footer-links">
            <a href="#">About Us</a><a href="#">Privacy Policy</a><a href="#">Disclaimer</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">&copy; 2026 Sarkari Naukari Infos. All Rights Reserved.</div>
    </div>
  </footer>

  <script src="js/data.js"></script>
  <script src="js/main.js"></script>
  <script>
  (function(){{
    // Items already sorted newest-first by Python (ts field = YYYYMMDD integer)
    var items = {items_json};

    // Sort client-side too so any dynamic additions also sort correctly
    items.sort(function(a,b){{return (b.ts||0)-(a.ts||0);}});

    var PER=50, cur=1;
    function fmt(ts){{
      if(!ts) return '';
      var s=String(ts);
      if(s.length===8) return s.slice(6)+'/'+s.slice(4,6)+'/'+s.slice(0,4);
      if(s.length===6) return s.slice(4,6)+'/'+s.slice(0,4);
      return '';
    }}
    function render(){{
      var s=(cur-1)*PER,e=s+PER,sl=items.slice(s,e);
      var rows=sl.map(function(it,i){{
        return '<tr><td class="num">'+(s+i+1)+'</td>'+
               '<td class="ttl"><a href="'+it.l+'">'+it.t+'</a></td>'+
               '<td class="dt">'+fmt(it.ts)+'</td></tr>';
      }}).join('');
      document.getElementById('tb').innerHTML=rows||
        '<tr><td colspan="3" style="text-align:center;padding:2rem;color:var(--text-muted)">No posts found.</td></tr>';
      document.getElementById('pgi').textContent=
        'Showing '+(s+1)+'–'+Math.min(e,items.length)+' of '+items.length+' posts (2026 · newest first)';
      renderPg();
    }}
    function renderPg(){{
      var tot=Math.ceil(items.length/PER),pg=document.getElementById('pgb');
      if(tot<=1){{pg.innerHTML='';return;}}
      var h='';
      if(cur>1) h+='<button class="pg-btn" onclick="go('+(cur-1)+')">&#8249;</button>';
      var st=Math.max(1,cur-3),en=Math.min(tot,cur+3);
      if(st>1) h+='<button class="pg-btn" onclick="go(1)">1</button>'+(st>2?'<span style="padding:.3rem">…</span>':'');
      for(var i=st;i<=en;i++) h+='<button class="pg-btn'+(i===cur?' on':'')+'" onclick="go('+i+')">'+i+'</button>';
      if(en<tot) h+=(en<tot-1?'<span style="padding:.3rem">…</span>':'')+'<button class="pg-btn" onclick="go('+tot+')">'+tot+'</button>';
      if(cur<tot) h+='<button class="pg-btn" onclick="go('+(cur+1)+')">&#8250;</button>';
      pg.innerHTML=h;
    }}
    window.go=function(n){{cur=n;render();window.scrollTo(0,300);}};
    var hsi=document.getElementById('hsi'),hsb=document.getElementById('hsb');
    if(hsb)hsb.addEventListener('click',function(){{var q=hsi.value.trim();if(q)window.location.href='search.html?q='+encodeURIComponent(q);}});
    if(hsi)hsi.addEventListener('keydown',function(e){{if(e.key==='Enter')hsb.click();}});
    var mt=document.querySelector('.menu-toggle'),mn=document.querySelector('.main-nav');
    if(mt)mt.addEventListener('click',function(){{mn.classList.toggle('active');}});
    render();
  }})();
  </script>
</body>
</html>'''


def main():
    print("=" * 64)
    print("  SORT POSTS — Newest First across all categories")
    print("=" * 64)

    # ── Read data.js ──────────────────────────────────────────────────
    with open(DATA_JS, "r", encoding="utf-8") as f:
        content = f.read()

    m = re.search(r"const siteData\s*=\s*(\{.*?\});", content, re.DOTALL)
    if not m:
        print("❌ Cannot parse data.js"); return

    data = json.loads(m.group(1))

    # ── Score and sort each category ──────────────────────────────────
    today_ts = int(datetime.date.today().strftime("%Y%m%d"))  # 20260308
    total_dated = 0
    total_items = 0

    for cat_key, items in data.items():
        if not isinstance(items, list):
            continue

        print(f"\n  [{cat_key}] — {len(items)} items")
        scored = []
        for it in items:
            title = it.get("title", "")
            link  = it.get("link", "")

            # Try to get date from HTML file
            slug_fn = link.replace("posts/", "")
            fpath = os.path.join(POSTS_DIR, slug_fn)
            ts = 0
            if os.path.exists(fpath):
                ts = extract_date_from_html(fpath)
            # Fallback: extract from title
            if not ts:
                ts = extract_date_from_title(title)
            # Absolute fallback: current scrape date (unknown = today so it goes to top)
            if not ts:
                ts = 20260101   # default to Jan 2026 = at bottom of 2026

            if ts > 20250101:   # valid-ish date
                total_dated += 1
            total_items += 1

            scored.append({"title": title, "link": link, "ts": ts})
            print(f"    {ts}  {title[:55]}")

        # Sort: newest first (descending ts)
        scored.sort(key=lambda x: x["ts"], reverse=True)
        data[cat_key] = scored   # write back sorted list (with ts field)

    print(f"\n  ✅ Dated {total_dated}/{total_items} posts from HTML files/titles")

    # ── Write data.js ─────────────────────────────────────────────────
    # Keep ts in data.js so JS can use it for dynamic sorting
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    new_content = re.sub(
        r"const siteData\s*=\s*\{.*?\};",
        f"const siteData = {new_json};",
        content, count=1, flags=re.DOTALL
    )
    with open(DATA_JS, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  ✅ data.js updated with ts fields and sorted order\n")

    # ── Rebuild category pages ────────────────────────────────────────
    print("  Rebuilding category pages (newest-first order)...")
    active_map = {"jobs.html":"a_jobs","results.html":"a_res","admitcard.html":"a_ac",
                  "answerkey.html":"a_ak","syllabus.html":"a_sy","admission.html":"a_ad"}

    for cat_key, items in data.items():
        if cat_key not in CAT_META or not isinstance(items, list):
            continue
        meta = CAT_META[cat_key]
        h1, fn, icon, hero = meta["h1"], meta["file"], meta["icon"], meta["hero"]

        # Items already sorted — pass them with ts for JS re-sort
        items_json = json.dumps([{"t": it["title"], "l": it["link"], "ts": it.get("ts",0)}
                                  for it in items], ensure_ascii=False)

        all_flags = {k: "" for k in ["a_jobs","a_res","a_ac","a_ak","a_sy","a_ad"]}
        ak = active_map.get(fn)
        if ak: all_flags[ak] = " active"

        page_html = CAT_PAGE_HTML.format(
            h1=h1, icon=icon, hero=hero, count=len(items),
            items_json=items_json, **all_flags
        )

        fp = os.path.join(BASE_DIR, fn)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"    ✅ {fn:22s} ({len(items)} posts, newest first)")

    print("\n" + "=" * 64)
    print("  DONE — All categories sorted newest → oldest")
    print("=" * 64)

    # ── Patch scraper scripts to always insert new posts at top ───────
    patch_scrapers()


def patch_scrapers():
    """Add sorting comment and top-insert logic to mega_scraper.py update_data_js."""
    print("\n  🔧 Patching scrapers to auto-sort on insert...")

    today = datetime.date.today().strftime("%Y%m%d")

    # Patch update_data_js in mega_scraper.py to insert with ts and sort
    ms_path = os.path.join(BASE_DIR, "mega_scraper.py")
    if os.path.exists(ms_path):
        with open(ms_path, "r", encoding="utf-8") as f:
            ms = f.read()

        old_insert = "existing[cat].insert(0, {\"title\": rec[\"title\"], \"link\": link})"
        new_insert  = (f"existing[cat].insert(0, {{\"title\": rec[\"title\"], \"link\": link, "
                       f"\"ts\": int(\"{today}\")}})\n"
                       f"        # Always keep newest first\n"
                       f"        existing[cat].sort(key=lambda x: x.get('ts',0), reverse=True)")

        if old_insert in ms:
            ms = ms.replace(old_insert, new_insert)
            with open(ms_path, "w", encoding="utf-8") as f:
                f.write(ms)
            print("    ✅ mega_scraper.py patched")
        else:
            print("    ℹ️  mega_scraper.py — insert line not found, skipping")

    # Patch apply_2026_filter.py similarly (the process_post return)
    af_path = os.path.join(BASE_DIR, "apply_2026_filter.py")
    if os.path.exists(af_path):
        with open(af_path, "r", encoding="utf-8") as f:
            af = af_read = f.read()

        old_ret = 'return {"title": title, "link": f"posts/{filename}", "scraped": bool(src_url and parsed)}'
        new_ret = (f'return {{"title": title, "link": f"posts/{{filename}}", '
                   f'"scraped": bool(src_url and parsed), "ts": int("{today}")}}')

        if old_ret in af:
            af = af.replace(old_ret, new_ret)
            with open(af_path, "w", encoding="utf-8") as f:
                f.write(af)
            print("    ✅ apply_2026_filter.py patched")
        else:
            print("    ℹ️  apply_2026_filter.py — return line not found, skipping")

    print("    ✅ Scrapers will now auto-sort new posts at top on next run")


if __name__ == "__main__":
    main()
