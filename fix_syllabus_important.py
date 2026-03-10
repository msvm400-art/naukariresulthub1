#!/usr/bin/env python3
"""
fix_syllabus_important.py
─────────────────────────
Scrapes sarkariresult.com for syllabus and important-link posts,
generates styled HTML pages, and rebuilds syllabus.html + important.html
with the new content. Does NOT touch other categories.

Run: python fix_syllabus_important.py
"""
import os, re, json, time, datetime, urllib.request
from bs4 import BeautifulSoup
import concurrent.futures

BASE_DIR  = r"C:\Users\ALOK\Desktop\sarkarinaukari"
POSTS_DIR = os.path.join(BASE_DIR, "posts")
DATA_JS   = os.path.join(BASE_DIR, "js", "data.js")
SOURCE    = "https://www.sarkariresult.com"
DELAY     = 0.4

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}

TODAY_TS = int(datetime.date.today().strftime("%Y%m%d"))

# ── Source pages to scrape ─────────────────────────────────────────────────────
# Each tuple: (category_key, url_path, anchor_text_filter)
SCRAPE_TARGETS = [
    # Syllabus pages
    ("syllabus", "/syllabus/", None),
    ("syllabus", "/latestjob/", "syllabus"),
    ("syllabus", "/latestjob/", "exam pattern"),
    ("syllabus", "/latestjob/", "curriculum"),
    # Important links
    ("important", "/important/", None),
    ("important", "/", "certificate"),
    ("important", "/", "voter id"),
    ("important", "/", "pan card"),
    ("important", "/", "ration card"),
    ("important", "/", "aadhar"),
    ("important", "/", "income certificate"),
    ("important", "/", "domicile"),
    ("important", "/", "scholarship"),
]

# Hardcoded important links (evergreen government portals)
HARDCODED_IMPORTANT = [
    {"title": "DigiLocker – Digital Documents Portal", "link": "https://www.digilocker.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "UMANG App – Unified Mobile Application", "link": "https://web.umang.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "MyGov – India Government Portal", "link": "https://www.mygov.in/", "ts": TODAY_TS, "external": True},
    {"title": "National Career Service Portal", "link": "https://www.ncs.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "Income Tax e-Filing Portal", "link": "https://www.incometax.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "EPFO – Employee Provident Fund Portal", "link": "https://www.epfindia.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "Voter ID – National Voter Service Portal", "link": "https://www.nvsp.in/", "ts": TODAY_TS, "external": True},
    {"title": "Aadhaar Card – UIDAI Official Portal", "link": "https://uidai.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "PAN Card – NSDL Portal Apply Online", "link": "https://www.onlineservices.nsdl.com/", "ts": TODAY_TS, "external": True},
    {"title": "Passport Seva – Apply Passport Online 2026", "link": "https://www.passportindia.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "PM Kisan Samman Nidhi – Beneficiary Status 2026", "link": "https://pmkisan.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "Ayushman Bharat – PM-JAY Health Card Portal", "link": "https://pmjay.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "Caste Certificate – State Revenue Portal (UP)", "link": "https://edistrict.up.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "Birth / Death Certificate – Civil Registration", "link": "https://crsorgi.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "RTI Online – File Right to Information Request", "link": "https://rtionline.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "National Scholarship Portal 2026", "link": "https://scholarships.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "eSanad – Academic Certificate Verification", "link": "https://esanad.in/", "ts": TODAY_TS, "external": True},
    {"title": "ABC – Academic Bank of Credits (DigiLocker)", "link": "https://www.abc.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "National Informatics Centre – India.gov.in", "link": "https://www.india.gov.in/", "ts": TODAY_TS, "external": True},
    {"title": "NICSI – Government IT Services Portal", "link": "https://www.nicsi.nic.in/", "ts": TODAY_TS, "external": True},
]

# ── Helpers ────────────────────────────────────────────────────────────────────
def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                data = r.read()
                enc  = r.headers.get("Content-Encoding","")
                if enc == "gzip":
                    import gzip; data = gzip.decompress(data)
            return data.decode("utf-8","ignore")
        except Exception as e:
            if attempt < retries-1: time.sleep(1.2)
    return None

def slugify(t):
    s = re.sub(r'[^a-z0-9\s\-]','', t.lower())
    return re.sub(r'[\s\-]+','-',s).strip('-')[:80]

def replace_brand(txt):
    return re.sub(r'Sarkari\s*Result(\.com)?', 'Sarkari Naukari Infos', txt, flags=re.I)

MONTH_MAP = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,
             'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}

def extract_ts(html_text, title):
    patterns = [
        r'(\d{1,2})[/\-](\d{1,2})[/\-](20\d{2})',
        r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(20\d{2})',
    ]
    best = 0
    for pat in patterns:
        for m in re.finditer(pat, html_text, re.I):
            try:
                if len(m.groups()) == 3 and m.group(3).isdigit():
                    d,mo,y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    ts = y*10000+mo*100+d
                elif len(m.groups()) == 3:
                    d = int(m.group(1))
                    mo = MONTH_MAP.get(m.group(2)[:3].lower(), 1)
                    y  = int(m.group(3))
                    ts = y*10000+mo*100+d
                else:
                    continue
                if ts > best: best = ts
            except: pass
    if not best:
        # Title date
        m = re.search(r'(20\d{2})', title)
        if m: best = int(m.group(1))*10000
    if not best: best = 20260101
    return best

# ── Post HTML template ─────────────────────────────────────────────────────────
POST_TPL = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} – Sarkari Naukari Infos</title>
  <meta name="description" content="{desc}">
  <meta name="keywords" content="{kw}">
  <link rel="canonical" href="https://naukariresulthub.in/posts/{slug}.html">
  <link rel="stylesheet" href="../css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Article","headline":"{title}",
   "description":"{desc}","author":{{"@type":"Organization","name":"Sarkari Naukari Infos"}},
   "publisher":{{"@type":"Organization","name":"Sarkari Naukari Infos"}},"datePublished":"2026-03-08"}}
  </script>
  <style>
    .ptbl{{width:100%;border-collapse:collapse;border:2px solid var(--border);margin-bottom:1.5rem;}}
    .ptbl th,.ptbl td{{padding:.9rem 1rem;border:1px solid var(--border);vertical-align:top;font-size:.95rem;}}
    .ptbl th{{background:rgba(67,97,238,.08);}}
    .ptbl a{{color:#0d6efd;text-decoration:none;font-weight:600;}}
    .ptbl a:hover{{text-decoration:underline;}}
    .hl-b{{color:#1d4ed8;font-weight:700;}} .hl-g{{color:#15803d;font-weight:700;}} .hl-m{{color:#be185d;font-weight:700;}}
  </style>
</head>
<body>
  <div class="header-top">Sarkari Naukari Infos – Your Trusted Source for Government Job Updates</div>
  <header class="site-header">
    <div class="container nav-container">
      <a href="../index.html" class="logo"><div class="logo-main">Sarkari<span>Naukari</span></div><div class="logo-sub">Infos .Net</div></a>
      <button class="menu-toggle"><i class="fas fa-bars"></i></button>
      <nav class="main-nav">
        <a href="../index.html" class="nav-link">Home</a>
        <a href="../jobs.html" class="nav-link">Latest Jobs</a>
        <a href="../results.html" class="nav-link">Results</a>
        <a href="../admitcard.html" class="nav-link">Admit Card</a>
        <a href="../answerkey.html" class="nav-link">Answer Key</a>
        <a href="../syllabus.html" class="nav-link">Syllabus</a>
        <a href="../admission.html" class="nav-link">Admission</a>
      </nav>
    </div>
  </header>

  <div style="background:linear-gradient(to right,var(--primary),#60a5fa);padding:2.2rem 0 1.8rem;">
    <div class="container">
      <h1 style="font-size:1.9rem;color:#fff;margin-bottom:.3rem;">{title}</h1>
      <div style="color:rgba(255,255,255,.8);font-size:.88rem;"><i class="fas fa-tag"></i> {cat_label}</div>
    </div>
  </div>

  <main class="container" style="max-width:920px;margin:2rem auto;background:var(--surface);padding:2rem;border-radius:var(--radius-lg);box-shadow:var(--shadow-md);">
    <div style="font-size:.8rem;color:var(--text-muted);margin-bottom:1.2rem;">
      <a href="../index.html" style="color:var(--primary)"><i class="fas fa-home"></i> Home</a>
      <span style="margin:0 .3rem">/</span>
      <a href="../{cat_page}" style="color:var(--primary)">{cat_label}</a>
      <span style="margin:0 .3rem">/</span><span>{title_short}</span>
    </div>

    <p style="text-align:center;color:var(--primary);font-weight:700;margin-bottom:.5rem;">Short Details of Notification</p>
    <p style="text-align:center;color:var(--text-muted);line-height:1.7;max-width:720px;margin:0 auto 1.8rem;">{desc}</p>

    {body_html}
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-about">
          <h3>Sarkari<span>Naukari</span> Infos</h3>
          <p>India's leading portal for government job updates, results, admit cards, and more.</p>
        </div>
        <div><span class="footer-heading">Quick Links</span>
          <div class="footer-links">
            <a href="../jobs.html">Latest Jobs</a><a href="../results.html">Results</a>
            <a href="../admitcard.html">Admit Card</a><a href="../syllabus.html">Syllabus</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">&copy; 2026 Sarkari Naukari Infos. All Rights Reserved.</div>
    </div>
  </footer>
  <script src="../js/data.js"></script><script src="../js/main.js"></script>
</body>
</html>'''

# ── Category page template ─────────────────────────────────────────────────────
CAT_TPL = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{h1} – Sarkari Naukari Infos</title>
  <meta name="description" content="{hero}">
  <meta name="keywords" content="{h1}, Sarkari Naukari 2026, Government Exams 2026">
  <link rel="canonical" href="https://naukariresulthub.in/{filename}">
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8244601197032455" crossorigin="anonymous"></script>
  <style>
    .plist-tbl{{width:100%;border-collapse:collapse;}}
    .plist-tbl tr{{border-bottom:1px solid #e8edf2;transition:background .14s;}}
    .plist-tbl tr:hover{{background:#f0f5ff;}}
    .plist-tbl td{{padding:.7rem 1rem;}}
    .plist-tbl td.num{{width:38px;color:#9ca3af;font-size:.8rem;text-align:center;font-weight:600;}}
    .plist-tbl td.ttl a{{color:var(--text-main);text-decoration:none;font-size:.95rem;font-weight:500;}}
    .plist-tbl td.ttl a:hover{{color:var(--primary);text-decoration:underline;}}
    .plist-tbl td.ttl a.ext-link::after{{content:" ↗";font-size:.7rem;color:#9ca3af;}}
    .plist-tbl td.dt{{width:90px;text-align:right;font-size:.75rem;color:#9ca3af;white-space:nowrap;}}
    .pg-bar{{display:flex;gap:.4rem;justify-content:center;flex-wrap:wrap;margin-top:1rem;padding-top:.8rem;border-top:1px solid #e8edf2;}}
    .pg-btn{{padding:.3rem .7rem;border-radius:5px;border:1.5px solid #e2e8f0;background:#fff;cursor:pointer;font-size:.87rem;font-family:inherit;transition:all .15s;min-width:30px;}}
    .pg-btn:hover,.pg-btn.on{{background:var(--primary);color:#fff;border-color:var(--primary);}}
    .sh{{display:flex;align-items:center;justify-content:space-between;margin-bottom:.8rem;border-bottom:2.5px solid var(--primary);padding-bottom:.4rem;}}
    .sh h2{{font-size:1.08rem;color:var(--primary);margin:0;}}
    .sort-note{{font-size:.74rem;color:#6b7280;margin-bottom:.6rem;}}
    .pg-info{{text-align:right;font-size:.78rem;color:var(--text-muted);margin-top:.4rem;}}
    .sect-badge{{display:inline-block;background:#eff6ff;color:#1d4ed8;border-radius:20px;padding:.1rem .6rem;font-size:.72rem;font-weight:600;margin-left:.4rem;}}
  </style>
</head>
<body>
  <div class="header-top">Sarkari Naukari Infos – Your Trusted Source for Government Job Updates</div>
  <header class="site-header">
    <div class="container nav-container">
      <a class="logo" href="index.html"><div class="logo-main">Sarkari<span>Naukari</span></div><div class="logo-sub">Infos .Net</div></a>
      <button class="menu-toggle"><i class="fas fa-bars"></i></button>
      <nav class="main-nav">
        <a class="nav-link" href="index.html">Home</a>
        <a class="nav-link" href="jobs.html">Latest Jobs</a>
        <a class="nav-link" href="results.html">Results</a>
        <a class="nav-link" href="admitcard.html">Admit Card</a>
        <a class="nav-link" href="answerkey.html">Answer Key</a>
        <a class="nav-link{a_sy}" href="syllabus.html">Syllabus</a>
        <a class="nav-link" href="admission.html">Admission</a>
      </nav>
      <div class="header-search">
        <input id="hsi" type="text" placeholder="Search..." aria-label="Search">
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
        <span>Total: {count} Posts</span>
      </div>
      <div class="sort-note"><i class="fas fa-sort-amount-down" style="color:var(--primary)"></i> Sorted newest first</div>
      <table class="plist-tbl"><tbody id="tb"></tbody></table>
      <div class="pg-bar" id="pgb"></div>
      <div class="pg-info" id="pgi"></div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-about">
          <h3>Sarkari<span>Naukari</span> Infos</h3>
          <p>India's leading portal for government job updates, results, admit cards, and more.</p>
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
            <a href="syllabus.html">Syllabus</a><a href="admission.html">Admission</a>
          </div>
        </div>
        <div><span class="footer-heading">Legal</span>
          <div class="footer-links">
            <a href="#">About Us</a><a href="#">Privacy Policy</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">&copy; 2026 Sarkari Naukari Infos. All Rights Reserved.</div>
    </div>
  </footer>

  <script src="js/data.js"></script><script src="js/main.js"></script>
  <script>
  (function(){{
    var items = {items_json};
    items.sort(function(a,b){{return (b.ts||0)-(a.ts||0);}});
    var PER=50, cur=1;
    function fmt(ts){{if(!ts)return'';var s=String(ts);return s.length===8?s.slice(6)+'/'+s.slice(4,6)+'/'+s.slice(0,4):s.length===6?s.slice(4)+'/'+s.slice(0,4):'';}}
    function render(){{
      var s=(cur-1)*PER,e=s+PER,sl=items.slice(s,e);
      var rows=sl.map(function(it,i){{
        var ext=it.ext?'ext-link':'',tgt=it.ext?' target="_blank" rel="noopener"':'';
        return '<tr><td class="num">'+(s+i+1)+'</td><td class="ttl"><a href="'+it.l+'" class="'+ext+'"'+tgt+'>'+it.t+'</a></td><td class="dt">'+fmt(it.ts)+'</td></tr>';
      }}).join('');
      document.getElementById('tb').innerHTML=rows||'<tr><td colspan="3" style="text-align:center;padding:2rem;color:var(--text-muted)">No posts found.</td></tr>';
      document.getElementById('pgi').textContent='Showing '+(s+1)+'–'+Math.min(e,items.length)+' of '+items.length;
      renderPg();
    }}
    function renderPg(){{
      var tot=Math.ceil(items.length/PER),pg=document.getElementById('pgb');
      if(tot<=1){{pg.innerHTML='';return;}}
      var h='';
      if(cur>1)h+='<button class="pg-btn" onclick="go('+(cur-1)+')">&#8249;</button>';
      var st=Math.max(1,cur-3),en=Math.min(tot,cur+3);
      if(st>1)h+='<button class="pg-btn" onclick="go(1)">1</button>'+(st>2?'<span style="padding:.3rem">…</span>':'');
      for(var i=st;i<=en;i++)h+='<button class="pg-btn'+(i===cur?' on':'')+'" onclick="go('+i+')">'+i+'</button>';
      if(en<tot)h+=(en<tot-1?'<span style="padding:.3rem">…</span>':'')+'<button class="pg-btn" onclick="go('+tot+')">'+tot+'</button>';
      if(cur<tot)h+='<button class="pg-btn" onclick="go('+(cur+1)+')">&#8250;</button>';
      pg.innerHTML=h;
    }}
    window.go=function(n){{cur=n;render();window.scrollTo(0,260);}};
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


# ── Scrape links from a listing page ──────────────────────────────────────────
def scrape_links(path, keyword_filter=None):
    """Return list of {title, url} dicts from a sarkariresult.com listing page."""
    html = fetch(SOURCE + path)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    results = []
    seen = set()
    for a in soup.find_all("a", href=True):
        t = a.get_text(strip=True)
        href = a["href"]
        if not t or len(t) < 8:
            continue
        if keyword_filter and keyword_filter.lower() not in t.lower():
            continue
        if href.startswith("/"):
            href = SOURCE + href
        if "sarkariresult.com" not in href:
            continue
        # Skip homepage itself, category listing pages
        if href.rstrip("/") == SOURCE or "/page/" in href:
            continue
        key = href.rstrip("/")
        if key not in seen:
            seen.add(key)
            results.append({"title": replace_brand(t), "url": href})
    return results


def scrape_and_build_post(item_url, title, cat_key):
    """Fetch a post page, parse its content, write HTML file, return data entry."""
    slug = slugify(title)
    out_path = os.path.join(POSTS_DIR, slug + ".html")

    # Fetch source page for content
    time.sleep(DELAY)
    html = fetch(item_url)

    ts = TODAY_TS
    body_html = ""
    desc = f"Complete details for {title} including important dates, eligibility, and useful links."

    if html:
        soup = BeautifulSoup(html, "html.parser")
        # Description
        for p in soup.find_all("p"):
            txt = p.get_text(strip=True)
            if len(txt) > 60:
                desc = replace_brand(txt); break
        # Timestamp
        ts = extract_ts(soup.get_text(" "), title)
        # Tables
        parts = []
        for tbl in soup.find_all("table"):
            t2 = BeautifulSoup(str(tbl), "html.parser").find("table")
            if t2:
                t2["class"] = ["ptbl"]
                for aa in t2.find_all("a", href=True):
                    aa["target"] = "_blank"; aa["rel"] = "noopener"
                tbl_s = replace_brand(str(t2))
                parts.append(f'<div style="overflow-x:auto;margin-bottom:1.5rem;">{tbl_s}</div>')
        if not parts:
            parts.append(f'''
            <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:1.2rem;text-align:center;color:#92400e;">
              <i class="fas fa-info-circle"></i>
              Content for <strong>{title}</strong> is being updated.
              Join our <a href="https://t.me/sarkarinaukariinfos" style="color:#0d6efd">Telegram Channel</a> for instant updates.
            </div>''')
        # Important links table at end
        parts.append(f'''
        <table class="ptbl"><tbody>
          <tr><td class="hl-g" colspan="2" style="text-align:center;font-size:1rem;background:rgba(21,128,61,.05);">
            <i class="fab fa-telegram"></i> Join Telegram for Instant Alerts</td></tr>
          <tr><td class="hl-m"><strong>Telegram</strong></td>
              <td><a href="https://t.me/sarkarinaukariinfos" target="_blank" style="color:#0088cc">
                <i class="fab fa-telegram-plane"></i> Click Here</a></td></tr>
          <tr><td class="hl-m"><strong>Official Site</strong></td>
              <td><a href="{item_url}" target="_blank" style="color:#0d6efd">
                <i class="fas fa-external-link-alt"></i> View Official Notice</a></td></tr>
        </tbody></table>''')
        body_html = "\n".join(parts)

    cat_labels = {"syllabus":"Syllabus", "important":"Important Links"}
    cat_pages  = {"syllabus":"syllabus.html", "important":"important.html"}
    cat_label  = cat_labels.get(cat_key, "Government Updates")
    cat_page   = cat_pages.get(cat_key, "index.html")
    kw = f"{title}, Sarkari Naukari 2026, {cat_label} 2026, Sarkari Result 2026"
    desc_safe = desc[:150].replace('"','')

    html_out = POST_TPL.format(
        title=title, desc=desc, kw=kw,
        slug=slug, cat_label=cat_label, cat_page=cat_page,
        title_short=title[:50], body_html=body_html
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    return {"title": title, "link": f"posts/{slug}.html", "ts": ts}


def build_cat_page(cat_key, items, h1, filename, icon, hero):
    items_sorted = sorted(items, key=lambda x: x.get("ts",0), reverse=True)
    # For important, some are external links
    items_json = json.dumps([
        {"t": it["title"], "l": it["link"], "ts": it.get("ts",TODAY_TS),
         "ext": it.get("external", False)}
        for it in items_sorted
    ], ensure_ascii=False)

    a_sy = " active" if filename == "syllabus.html" else ""
    page_html = CAT_TPL.format(
        h1=h1, hero=hero, icon=icon,
        filename=filename, count=len(items),
        items_json=items_json, a_sy=a_sy
    )
    with open(os.path.join(BASE_DIR, filename), "w", encoding="utf-8") as f:
        f.write(page_html)
    print(f"  ✅ {filename} rebuilt with {len(items)} posts")


# ── Syllabus data (extra hardcoded 2026 syllabus posts most likely to exist) ───
HARDCODED_SYLLABUS = [
    "SSC CGL 2026 Syllabus PDF Download – Tier 1 Tier 2 Exam Pattern",
    "SSC CHSL 2026 Syllabus PDF Download – Tier 1 Tier 2 Pattern",
    "SSC MTS 2026 Syllabus PDF – Paper 1 Paper 2 Exam Pattern",
    "UPSC Civil Services IAS 2026 Syllabus PDF – Prelims Mains Pattern",
    "RRB NTPC 2026 Syllabus PDF Download – CBT 1 CBT 2 Exam Pattern",
    "Railway Group D 2026 Syllabus PDF – RRC Exam Pattern",
    "IBPS PO 2026 Syllabus PDF – Prelims Mains Interview Pattern",
    "SBI PO 2026 Syllabus PDF Download – Prelims Mains Pattern",
    "SBI Clerk 2026 Syllabus PDF – Junior Associate Prelims Mains",
    "IBPS Clerk 2026 Syllabus PDF – Prelims Mains Exam Pattern",
    "UP Police Constable 2026 Syllabus PDF – Written Exam Pattern",
    "Bihar Police Constable 2026 Syllabus PDF – SI Constable Pattern",
    "BPSC 2026 Syllabus PDF – 70th CCE Prelims Mains Pattern",
    "UPPSC PCS 2026 Syllabus PDF – Combined State Services Exam Pattern",
    "NDA 2026 Syllabus PDF – Written Exam Mathematics GAT Pattern",
    "CDS 2026 Syllabus PDF – Combined Defence Services Exam Pattern",
    "CRPF SI 2026 Syllabus PDF – Sub Inspector Technical/Ministerial",
    "KVS TGT PGT 2026 Syllabus PDF – Teacher Exam Pattern",
    "DSSSB 2026 Syllabus PDF – Various Post Exam Pattern",
    "NVS TGT 2026 Syllabus PDF – Exam Pattern & Selection Process",
    "CTET 2026 Syllabus PDF – Paper 1 Paper 2 Latest Exam Pattern",
    "UPTET 2026 Syllabus PDF – Paper 1 Paper 2 New Exam Pattern",
    "RPSC RAS 2026 Syllabus PDF – Prelims Mains Exam Pattern",
    "Haryana Police Constable 2026 Syllabus PDF – HSSC Exam Pattern",
    "Rajasthan Police Constable 2026 Syllabus PDF – Exam Pattern",
    "SSC GD Constable 2026 Syllabus PDF – CAPF Exam Pattern Download",
    "ITBP Constable 2026 Syllabus PDF – Exam Pattern Selection Process",
    "Army Agniveer 2026 Syllabus PDF – Common Entrance Exam Pattern",
    "Navy Agniveer MR 2026 Syllabus PDF – Written Exam Pattern",
    "Airforce Agniveer 2026 Syllabus PDF – Phase 1 Phase 2 Pattern",
    "RBI Assistant 2026 Syllabus PDF – Prelims Mains Exam Pattern",
    "RBI Grade B 2026 Syllabus PDF – Phase 1 Phase 2 Interview",
    "NABARD Grade A 2026 Syllabus PDF – Exam Pattern Selection Process",
    "LIC AAO 2026 Syllabus PDF – Prelims Mains Exam Pattern",
    "ESIC SSO 2026 Syllabus PDF – Exam Pattern Selection Process",
    "DRDO CEPTAM 2026 Syllabus PDF – Exam Pattern & Selection Process",
    "HAL Technical Manager 2026 Syllabus PDF – Exam Pattern",
    "ISRO Scientist 2026 Syllabus PDF – Written Test Pattern",
    "BHEL Apprentice 2026 Syllabus PDF – Written Test Pattern",
    "AAI Junior Executive 2026 Syllabus PDF – Exam Pattern",
    "MPSC Rajyaseva 2026 Syllabus PDF – Prelims Mains Pattern",
    "MPPSC 2026 Syllabus PDF – State Services Exam Pattern",
    "HPSC HCS 2026 Syllabus PDF – Prelims Mains Exam Pattern",
    "UKPSC PCS 2026 Syllabus PDF – Combined State Services Pattern",
    "CGPSC 2026 Syllabus PDF – State Service Exam Prelims Mains",
    "JPSC 2026 Syllabus PDF – Combined Civil Services Pattern",
    "WBPSC Clerkship 2026 Syllabus PDF – Exam Pattern",
    "Karnataka PSC 2026 Syllabus PDF – KAS Exam Pattern",
    "TNPSC Group 1 2026 Syllabus PDF – Prelims Mains Pattern",
    "RPSC 2nd Grade Teacher 2026 Syllabus PDF – Exam Pattern",
]


def main():
    print("="*64)
    print("  FIX SYLLABUS & IMPORTANT COLUMNS")
    print("="*64)

    # ── Step 1: Read existing data.js ────────────────────
    with open(DATA_JS, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"const siteData\s*=\s*(\{.*?\});", content, re.DOTALL)
    data = json.loads(m.group(1))

    existing_links_syl = {it["link"] for it in data.get("syllabus",[])}
    existing_links_imp = {it["link"] for it in data.get("important",[])}

    # ── Step 2: Scrape sarkariresult.com for new syllabus posts ─────
    print("\n  [SYLLABUS] Scraping source site...")
    scraped_syllabus = []
    seen_titles = {it["title"].lower() for it in data.get("syllabus",[])}

    all_raw_links = []
    for (cat, path, kf) in SCRAPE_TARGETS:
        if cat != "syllabus": continue
        links = scrape_links(path, kf)
        all_raw_links.extend(links)
        time.sleep(0.3)

    # Filter: keep syllabus-relevant ones
    syl_kw = ["syllabus","exam pattern","curriculum","paper pattern","selection process","subject"]
    for item in all_raw_links:
        t = item["title"].lower()
        if not any(k in t for k in syl_kw): continue
        if item["title"].lower() in seen_titles: continue
        all_raw_links_filtered_item = item
        scraped_syllabus.append(item)
        seen_titles.add(item["title"].lower())

    print(f"  Scraped {len(scraped_syllabus)} new syllabus links from source")

    # ── Step 3: Add hardcoded syllabus posts (quick HTML generation) ─
    print("  Adding hardcoded syllabus posts...")
    hardcoded_entries = []
    for title in HARDCODED_SYLLABUS:
        if title.lower() in seen_titles: continue
        slug = slugify(title)
        fpath = os.path.join(POSTS_DIR, slug + ".html")
        ts = extract_ts("", title)
        # Create a simple post page
        desc = f"Download {title}. Check the complete subject-wise syllabus, exam pattern, and selection process for 2026 examination preparation."
        body = f'''
        <div style="background:#eff6ff;border-radius:12px;padding:1.5rem;margin-bottom:1.5rem;">
          <h2 style="color:#1d4ed8;margin-bottom:1rem;font-size:1.2rem;"><i class="fas fa-book-open"></i> {title}</h2>
          <p style="color:#374151;line-height:1.7;margin-bottom:1rem;">{desc}</p>
          <p style="color:#374151;line-height:1.7;">The syllabus covers all important topics including General Knowledge, Mathematics, Reasoning, English Language, and subject-specific topics. Candidates are advised to download the official syllabus PDF and plan their preparation accordingly.</p>
        </div>
        <table class="ptbl"><tbody>
          <tr><td class="hl-g" colspan="2" style="text-align:center;font-size:1rem;background:rgba(21,128,61,.05);padding:1rem;">
            <i class="fas fa-link"></i> Important Links</td></tr>
          <tr><td style="font-weight:700;color:#be185d;">Official Notification</td>
              <td><a href="#" onclick="alert('Link to be updated soon');return false"><i class="fas fa-external-link-alt"></i> Click Here</a></td></tr>
          <tr><td style="font-weight:700;color:#be185d;">Telegram Updates</td>
              <td><a href="https://t.me/sarkarinaukariinfos" target="_blank" style="color:#0088cc"><i class="fab fa-telegram-plane"></i> Click Here</a></td></tr>
        </tbody></table>'''
        html_out = POST_TPL.format(
            title=title, desc=desc, kw=f"{title}, Sarkari Naukari 2026, Syllabus 2026",
            slug=slug, cat_label="Syllabus", cat_page="syllabus.html",
            title_short=title[:50], body_html=body
        )
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html_out)
        hardcoded_entries.append({"title": title, "link": f"posts/{slug}.html", "ts": ts})
        seen_titles.add(title.lower())

    print(f"  Generated {len(hardcoded_entries)} hardcoded syllabus pages")

    # ── Step 4: Scrape source links for scraped_syllabus items ──────
    new_syllabus = list(data.get("syllabus", []))  # keep existing

    def worker_syl(item):
        return scrape_and_build_post(item["url"], item["title"], "syllabus")

    if scraped_syllabus:
        print(f"  Scraping {len(scraped_syllabus)} syllabus post pages...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            futs = {ex.submit(worker_syl, it): it for it in scraped_syllabus[:30]}
            for fut in concurrent.futures.as_completed(futs):
                res = fut.result()
                if res and res["link"] not in existing_links_syl:
                    new_syllabus.append(res)
                    existing_links_syl.add(res["link"])
                    print(f"    ✅ {res['title'][:60]}")

    # Merge hardcoded
    for e in hardcoded_entries:
        if e["link"] not in existing_links_syl:
            new_syllabus.append(e)
            existing_links_syl.add(e["link"])

    # Sort newest first
    new_syllabus.sort(key=lambda x: x.get("ts",0), reverse=True)
    data["syllabus"] = new_syllabus
    print(f"  SYLLABUS total: {len(new_syllabus)} posts")

    # ── Step 5: Build important entries ─────────────────────────────
    print("\n  [IMPORTANT] Building important links section...")
    new_important = list(data.get("important", []))

    # Add hardcoded important links
    for it in HARDCODED_IMPORTANT:
        if it["link"] not in existing_links_imp:
            new_important.append(it)
            existing_links_imp.add(it["link"])

    # Also try scraping important page from source
    imp_scraped = scrape_links("/important/", None)
    time.sleep(0.4)
    imp_scraped += scrape_links("/", "certificate")

    seen_imp_t = {x["title"].lower() for x in new_important}
    imp_kw = ["certificate","voter","aadhaar","aadhar","pan","passport","ration","scholarship","domicile","income","birth","death","caste","obc","sc","st","ews","income tax","epfo","pf","digi","rti","portal","online service"]

    for item in imp_scraped:
        t = item["title"]
        if t.lower() in seen_imp_t: continue
        if not any(k in t.lower() for k in imp_kw): continue
        slug = slugify(t)
        fpath = os.path.join(POSTS_DIR, slug + ".html")
        ts = extract_ts("", t)
        desc = f"Complete information about {t} — how to apply, check status, and download certificate online."
        body = f'''
        <div style="background:#eff6ff;border-radius:12px;padding:1.5rem;margin-bottom:1.5rem;">
          <h2 style="color:#1d4ed8;font-size:1.1rem;margin-bottom:.8rem;">{t}</h2>
          <p style="color:#374151;line-height:1.7;">{desc}</p>
        </div>
        <table class="ptbl"><tbody>
          <tr><td class="hl-g" colspan="2" style="text-align:center;background:rgba(21,128,61,.05);padding:.9rem;">Important Links</td></tr>
          <tr><td style="font-weight:700;color:#be185d;">Official Link</td>
              <td><a href="{item['url']}" target="_blank"><i class="fas fa-external-link-alt"></i> Click Here</a></td></tr>
        </tbody></table>'''
        html_out = POST_TPL.format(
            title=t, desc=desc, kw=f"{t}, Sarkari Naukari 2026, Important Links",
            slug=slug, cat_label="Important Links", cat_page="important.html",
            title_short=t[:50], body_html=body
        )
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html_out)
        new_important.append({"title": t, "link": f"posts/{slug}.html", "ts": ts})
        seen_imp_t.add(t.lower())
        existing_links_imp.add(f"posts/{slug}.html")
        print(f"    ✅ [IMP] {t[:60]}")

    new_important.sort(key=lambda x: x.get("ts",0), reverse=True)
    data["important"] = new_important
    print(f"  IMPORTANT total: {len(new_important)} posts")

    # ── Step 6: Write data.js ────────────────────────────────────────
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    new_content = re.sub(
        r"const siteData\s*=\s*\{.*?\};",
        f"const siteData = {new_json};",
        content, count=1, flags=re.DOTALL
    )
    with open(DATA_JS, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("\n  ✅ data.js updated")

    # ── Step 7: Rebuild category pages ──────────────────────────────
    build_cat_page("syllabus", data["syllabus"],
        "Syllabus 2026", "syllabus.html", "fas fa-book-open",
        "Download subject-wise 2026 syllabus and exam patterns for SSC, Railway, UPSC, Banking, Police and State Government exams.")
    build_cat_page("important", data["important"],
        "Important Links & Certificate Verification", "important.html", "fas fa-link",
        "Access important government portals for certificate verification, voter ID, Aadhaar, PAN card, passport, scholarship, and other online services.")

    print("\n" + "="*64)
    print(f"  DONE! Syllabus: {len(data['syllabus'])} posts | Important: {len(data['important'])} posts")
    print("="*64)


if __name__ == "__main__":
    main()
