#!/usr/bin/env python3
"""
apply_2026_filter.py
────────────────────
1. Filters data.js to keep ONLY posts with "2026" in the title.
2. Rebuilds all 7 category pages with a clean table design (no boxes, no filter bar).
3. Scrapes sarkariresult.com to get proper SEO content for each 2026 post page
   and rewrites the HTML file in posts/.

Run: python apply_2026_filter.py
"""

import os, re, json, time, gzip, urllib.request
import concurrent.futures
from bs4 import BeautifulSoup

BASE_DIR  = r"C:\Users\ALOK\Desktop\sarkarinaukari"
POSTS_DIR = os.path.join(BASE_DIR, "posts")
DATA_JS   = os.path.join(BASE_DIR, "js", "data.js")
SOURCE    = "https://www.sarkariresult.com"
DELAY     = 0.35

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# ── Category meta ──────────────────────────────────────────────────────────────
CAT_META = {
    "latestJobs":  dict(h1="Latest Government Jobs 2026", file="jobs.html",       icon="fas fa-briefcase",      hero="Apply online for the latest 2026 government job vacancies. Updated daily with central and state notifications."),
    "results":     dict(h1="Sarkari Result 2026",          file="results.html",    icon="fas fa-trophy",         hero="Check the latest 2026 government exam results — SSC, Railway, UPSC, Banking, Police and State exams."),
    "admitCards":  dict(h1="Admit Card 2026",              file="admitcard.html",  icon="fas fa-id-card",        hero="Download 2026 admit cards and hall tickets for government examinations. Find exam city and schedule."),
    "answerKeys":  dict(h1="Answer Key 2026",              file="answerkey.html",  icon="fas fa-key",            hero="Download official 2026 answer keys. Raise objections and estimate your score before result."),
    "syllabus":    dict(h1="Syllabus 2026",                file="syllabus.html",   icon="fas fa-book-open",      hero="Download subject-wise 2026 syllabus and exam patterns for government exam preparation."),
    "admissions":  dict(h1="Admission 2026",               file="admission.html",  icon="fas fa-graduation-cap", hero="Apply for 2026 admissions — NEET, CUET, JEE, and university counselling portals."),
    "important":   dict(h1="Important Links 2026",         file="important.html",  icon="fas fa-link",           hero="Access important 2026 government portals, certificate verification links, and essential services."),
}

# ── POST PAGE TEMPLATE ─────────────────────────────────────────────────────────
POST_TPL = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{seo_title}</title>
  <meta name="description" content="{meta_desc}">
  <meta name="keywords" content="{meta_kw}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{seo_title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary">
  <script type="application/ld+json">{schema}</script>
  <link rel="stylesheet" href="../css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8244601197032455" crossorigin="anonymous"></script>
  <style>
    .ibox{{border:1px solid var(--border);border-radius:var(--radius-md);padding:1.4rem;margin-bottom:1.8rem;background:rgba(67,97,238,.02);}}
    .ibox h2{{font-size:1.25rem;text-align:center;margin-bottom:.9rem;border-bottom:2px solid var(--primary-light);padding-bottom:.4rem;}}
    .hl-m{{color:#d63384;font-weight:700;}} .hl-g{{color:#198754;font-weight:700;}} .hl-b{{color:#0d6efd;font-weight:700;}}
    .ptbl{{width:100%;border-collapse:collapse;border:2px solid var(--border);margin-bottom:2rem;}}
    .ptbl th,.ptbl td{{padding:.95rem 1rem;border:1px solid var(--border);vertical-align:top;}}
    .ptbl th{{background:rgba(67,97,238,.08);font-size:1rem;}}
    .ptbl td{{font-size:.95rem;}}
    .ptbl a{{color:#0d6efd;text-decoration:none;font-weight:600;}}
    .ptbl a:hover{{text-decoration:underline;}}
    ul.plist{{list-style:none;padding-left:0;margin:0;}}
    ul.plist li{{position:relative;padding-left:20px;margin-bottom:.6rem;line-height:1.6;}}
    ul.plist li::before{{content:"\\f0da";font-family:"Font Awesome 6 Free";font-weight:900;position:absolute;left:0;color:var(--primary);font-size:.85rem;top:.1rem;}}
    .bc{{font-size:.82rem;color:var(--text-muted);margin-bottom:1.4rem;display:flex;flex-wrap:wrap;align-items:center;gap:.35rem;}}
    .bc a{{color:var(--primary);}} .bc a:hover{{text-decoration:underline;}}
  </style>
</head>
<body>
  <div class="header-top">Sarkari Naukari Infos – Your Trusted Source for Government Job Updates</div>
  <header class="site-header">
    <div class="container nav-container">
      <a href="../index.html" class="logo"><div class="logo-main">Sarkari<span>Naukari</span></div><div class="logo-sub">Infos .Net</div></a>
      <button class="menu-toggle" aria-label="Toggle menu"><i class="fas fa-bars"></i></button>
      <nav class="main-nav">
        <a href="../index.html" class="nav-link">Home</a>
        <a href="../jobs.html" class="nav-link">Latest Jobs</a>
        <a href="../results.html" class="nav-link">Results</a>
        <a href="../admitcard.html" class="nav-link">Admit Card</a>
        <a href="../answerkey.html" class="nav-link">Answer Key</a>
        <a href="../syllabus.html" class="nav-link">Syllabus</a>
        <a href="../admission.html" class="nav-link">Admission</a>
      </nav>
      <div class="header-search">
        <input id="hsi" type="text" placeholder="Search exams, jobs..." aria-label="Search">
        <button id="hsb"><i class="fas fa-search"></i> Search</button>
      </div>
    </div>
  </header>

  <div style="background:linear-gradient(to right,var(--primary),#60a5fa);padding:2.5rem 0 2rem;margin-bottom:2rem;">
    <div class="container">
      <h1 style="font-size:2rem;margin-bottom:.4rem;color:#fff;">{h1}</h1>
      <div style="color:rgba(255,255,255,.82);font-size:.9rem;">
        <i class="fas fa-building"></i> {org} &nbsp;|&nbsp; <i class="fas fa-tag"></i> {cat_label}
      </div>
    </div>
  </div>

  <main class="container animate-fade-in" style="max-width:940px;margin:0 auto;background:var(--surface);padding:2.2rem;border-radius:var(--radius-lg);box-shadow:var(--shadow-md);">
    <div class="bc">
      <a href="../index.html"><i class="fas fa-home"></i> Home</a><span>/</span>
      <a href="../{cat_page}">{cat_label}</a><span>/</span>
      <span>{short_t}</span>
    </div>

    <div style="text-align:center;margin-bottom:1.8rem;">
      <p style="font-size:1.05rem;color:var(--primary);font-weight:700;">Short Details of Notification</p>
      <p style="color:var(--text-muted);line-height:1.7;max-width:760px;margin:0 auto;">{description}</p>
    </div>

    {body_html}

  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-about">
          <h3>Sarkari<span>Naukari</span> Infos</h3>
          <p>India&#39;s leading portal for government job updates, results, admit cards, and more.</p>
          <div class="footer-socials">
            <a class="social-link" href="#"><i class="fab fa-facebook-f"></i></a>
            <a class="social-link" href="#"><i class="fab fa-twitter"></i></a>
            <a class="social-link" href="#"><i class="fab fa-telegram-plane"></i></a>
            <a class="social-link" href="#"><i class="fab fa-youtube"></i></a>
          </div>
        </div>
        <div><span class="footer-heading">Quick Links</span>
          <div class="footer-links">
            <a href="../jobs.html">Latest Jobs</a><a href="../results.html">Results</a>
            <a href="../admitcard.html">Admit Card</a><a href="../answerkey.html">Answer Keys</a>
          </div>
        </div>
        <div><span class="footer-heading">More</span>
          <div class="footer-links">
            <a href="../syllabus.html">Syllabus</a><a href="../admission.html">Admission</a>
            <a href="../search.html">Search</a><a href="../admin/index.html">Admin</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">&copy; 2026 Sarkari Naukari Infos. All Rights Reserved.</div>
    </div>
  </footer>

  <script src="../js/data.js"></script>
  <script src="../js/main.js"></script>
  <script>
    var btn=document.getElementById('hsb'), inp=document.getElementById('hsi');
    if(btn)btn.addEventListener('click',function(){{var q=inp.value.trim();if(q)window.location.href='../search.html?q='+encodeURIComponent(q);}});
    if(inp)inp.addEventListener('keydown',function(e){{if(e.key==='Enter')btn.click();}});
    var t=document.querySelector('.menu-toggle'),n=document.querySelector('.main-nav');
    if(t)t.addEventListener('click',function(){{n.classList.toggle('active');}});
  </script>
</body>
</html>'''

# ── CATEGORY PAGE TEMPLATE (clean table, no boxes, no filter bar) ─────────────
CAT_TPL = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{h1} – Sarkari Naukari Infos</title>
  <meta name="description" content="{hero} Sarkari Naukari Infos – {count} posts listed.">
  <meta name="keywords" content="{h1}, Sarkari Naukari, Government Jobs 2026, Sarkari Result 2026">
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8244601197032455" crossorigin="anonymous"></script>
  <style>
    .post-list-table{{width:100%;border-collapse:collapse;}}
    .post-list-table tr{{border-bottom:1px solid #e8edf2;transition:background .15s;}}
    .post-list-table tr:hover{{background:#f0f5ff;}}
    .post-list-table td{{padding:.75rem 1rem;}}
    .post-list-table td:first-child{{width:30px;color:var(--text-light);font-size:.8rem;text-align:center;}}
    .post-list-table td.title-cell a{{color:var(--text-main);text-decoration:none;font-size:.97rem;font-weight:500;display:block;}}
    .post-list-table td.title-cell a:hover{{color:var(--primary);}}
    .post-list-table td.badge-cell{{width:90px;text-align:right;white-space:nowrap;}}
    .new-badge{{background:#e0e7ff;color:#3730a3;padding:.15rem .55rem;border-radius:20px;font-size:.72rem;font-weight:700;}}
    .hot-badge{{background:#fff3cd;color:#92400e;padding:.15rem .55rem;border-radius:20px;font-size:.72rem;font-weight:700;}}
    .pg-bar{{display:flex;gap:.4rem;justify-content:center;flex-wrap:wrap;margin-top:1.2rem;padding-top:1rem;border-top:1px solid #e8edf2;}}
    .pg-btn{{padding:.35rem .75rem;border-radius:5px;border:1.5px solid #e2e8f0;background:#fff;cursor:pointer;font-size:.88rem;font-family:inherit;transition:all .18s;min-width:34px;}}
    .pg-btn:hover{{border-color:var(--primary);color:var(--primary);}}
    .pg-btn.active{{background:var(--primary);color:#fff;border-color:var(--primary);}}
    .pg-info{{text-align:right;font-size:.8rem;color:var(--text-muted);margin-top:.5rem;}}
    .section-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;border-bottom:2px solid var(--primary);padding-bottom:.5rem;}}
    .section-header h2{{font-size:1.1rem;color:var(--primary);margin:0;}}
    .section-header span{{font-size:.82rem;color:var(--text-muted);}}
  </style>
</head>
<body>
  <div class="header-top">Sarkari Naukari Infos – Your Trusted Source for Government Job Updates</div>
  <header class="site-header">
    <div class="container nav-container">
      <a class="logo" href="index.html"><div class="logo-main">Sarkari<span>Naukari</span></div><div class="logo-sub">Infos .Net</div></a>
      <button class="menu-toggle" aria-label="Toggle menu"><i class="fas fa-bars"></i></button>
      <nav class="main-nav">
        <a class="nav-link" href="index.html">Home</a>
        <a class="nav-link{a_jobs}" href="jobs.html">Latest Jobs</a>
        <a class="nav-link{a_res}" href="results.html">Results</a>
        <a class="nav-link{a_ac}" href="admitcard.html">Admit Card</a>
        <a class="nav-link{a_ak}" href="answerkey.html">Answer Key</a>
        <a class="nav-link{a_sy}" href="syllabus.html">Syllabus</a>
        <a class="nav-link{a_ad}" href="admission.html">Admission</a>
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
    <div style="font-size:.82rem;color:var(--text-muted);margin-bottom:1.2rem;">
      <a href="index.html" style="color:var(--primary);"><i class="fas fa-home"></i> Home</a>
      <span style="margin:0 .3rem">/</span><span>{h1}</span>
    </div>

    <div class="category-card">
      <div class="section-header">
        <h2><i class="{icon}"></i> {h1}</h2>
        <span>Total: {count} Posts (2026)</span>
      </div>
      <table class="post-list-table">
        <tbody id="post-body"></tbody>
      </table>
      <div class="pg-bar" id="pg-bar"></div>
      <div class="pg-info" id="pg-info"></div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-about">
          <h3>Sarkari<span>Naukari</span> Infos</h3>
          <p>India&#39;s leading portal for government job updates, results, admit cards, and more.</p>
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
    var items = {items_json};
    var PER = 50, cur = 1;
    function render(){{
      var s=(cur-1)*PER, e=s+PER, sl=items.slice(s,e);
      var rows=sl.map(function(it,i){{
        var badge='';
        var t=it.t.toLowerCase();
        var idx=s+i+1;
        return '<tr><td>'+idx+'</td><td class="title-cell"><a href="'+it.l+'">'+it.t+'</a></td><td class="badge-cell">'+badge+'</td></tr>';
      }}).join('');
      document.getElementById('post-body').innerHTML=rows||'<tr><td colspan="3" style="text-align:center;padding:2rem;color:var(--text-muted)">No posts found.</td></tr>';
      document.getElementById('pg-info').textContent='Showing '+(s+1)+'–'+Math.min(e,items.length)+' of '+items.length+' posts (2026)';
      renderPg();
    }}
    function renderPg(){{
      var total=Math.ceil(items.length/PER), pg=document.getElementById('pg-bar');
      if(total<=1){{pg.innerHTML='';return;}}
      var h='';
      if(cur>1) h+='<button class="pg-btn" onclick="go('+(cur-1)+')">&#8249;</button>';
      var st=Math.max(1,cur-3),en=Math.min(total,cur+3);
      if(st>1) h+='<button class="pg-btn" onclick="go(1)">1</button>'+(st>2?'<span style="padding:.3rem">…</span>':'');
      for(var i=st;i<=en;i++) h+='<button class="pg-btn'+(i===cur?' active':'')+'" onclick="go('+i+')">'+i+'</button>';
      if(en<total) h+=(en<total-1?'<span style="padding:.3rem">…</span>':'')+'<button class="pg-btn" onclick="go('+total+')">'+total+'</button>';
      if(cur<total) h+='<button class="pg-btn" onclick="go('+(cur+1)+')">&#8250;</button>';
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


# ── UTILITIES ──────────────────────────────────────────────────────────────────

def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    import gzip as gz; data = gz.decompress(data)
                return data.decode("utf-8", "ignore")
        except Exception:
            if attempt < retries - 1: time.sleep(1)
    return None


def slugify(t):
    s = re.sub(r'[^a-z0-9\s\-]', '', t.lower())
    return re.sub(r'[\s\-]+', '-', s).strip('-')[:80]


def detect_org(title):
    for o in ["SSC","UPSC","RRB","RBI","IBPS","SBI","NTA","BPSC","UPPSC","RPSC",
              "MPPSC","Railway","Police","Army","Navy","Airforce","DRDO","Bihar",
              "HPSC","CGPSC","UKPSC","Haryana","Punjab","Rajasthan"]:
        if o.lower() in title.lower(): return o
    return "Government of India"


def detect_cat_label(cat_key):
    return {"latestJobs":"Latest Jobs","results":"Results","admitCards":"Admit Card",
            "answerKeys":"Answer Key","syllabus":"Syllabus","admissions":"Admission",
            "important":"Important"}.get(cat_key,"Jobs")


def detect_cat_page(cat_key):
    return {"latestJobs":"jobs.html","results":"results.html","admitCards":"admitcard.html",
            "answerKeys":"answerkey.html","syllabus":"syllabus.html","admissions":"admission.html",
            "important":"important.html"}.get(cat_key,"jobs.html")


def replace_brand(text):
    return re.sub(r'Sarkari\s*Result(\.com)?', 'Sarkari Naukari Infos', text, flags=re.I)


def build_seo_content(title, cat_key):
    """Produce basic fallback SEO content when we can't scrape."""
    desc = f"Complete details of {title} including Important Dates, Application Fee, Vacancy Details, Eligibility, Selection Process, and Apply Online Links."
    kw   = f"{title}, Sarkari Naukari 2026, Government Jobs 2026, {detect_cat_label(cat_key)} 2026, Sarkari Result 2026"
    return {"seo_title": f"{title} – Sarkari Naukari Infos", "meta_desc": desc, "meta_kw": kw,
            "h1": title, "description": desc, "body_html": build_fallback_body(title)}


def build_fallback_body(title):
    return f'''
    <div style="overflow-x:auto;margin-bottom:2rem;">
      <table class="ptbl">
        <tbody>
          <tr><td class="hl-g" colspan="2" style="font-size:1.15rem;background:rgba(25,135,84,.05);padding:1.2rem;">
            <i class="fas fa-link"></i> Some Useful Important Links
          </td></tr>
          <tr><td class="hl-m" style="font-weight:700;">Official Website</td>
              <td><a href="https://www.sarkari-naukari.in" target="_blank" rel="noopener"><i class="fas fa-globe"></i> Click Here</a></td></tr>
          <tr><td class="hl-m" style="font-weight:700;">Join Telegram</td>
              <td><a href="https://t.me/sarkarinaukariinfos" target="_blank" style="color:#0088cc"><i class="fab fa-telegram"></i> Click Here</a></td></tr>
          <tr><td class="hl-m" style="font-weight:700;">Apply Online</td>
              <td><a href="#" onclick="alert('Link will be updated soon');return false"><i class="fas fa-external-link-alt"></i> Link Available Soon</a></td></tr>
        </tbody>
      </table>
    </div>
    <div class="ibox" style="background:#fffbeb;border-color:#fde68a;">
      <p style="text-align:center;color:#92400e;margin:0;">
        <i class="fas fa-info-circle"></i>
        Full details for <strong>{title}</strong> will be updated shortly.
        Join our <a href="https://t.me/sarkarinaukariinfos" style="color:#0d6efd">Telegram Channel</a> for instant notifications.
      </p>
    </div>'''


def parse_source_page(html, title):
    """Parse sarkariresult.com page and extract all SEO content + body."""
    soup = BeautifulSoup(html, "html.parser")

    # SEO title
    pt = soup.find("title")
    seo_title = replace_brand(pt.get_text(strip=True)) if pt else f"{title} – Sarkari Naukari Infos"

    # Meta description
    md = soup.find("meta", attrs={"name": re.compile("description", re.I)})
    meta_desc = replace_brand(md["content"].strip()) if md and md.get("content") else \
        f"Complete information for {title} 2026 including dates, fee, vacancies, and apply links."

    # Meta keywords
    mk = soup.find("meta", attrs={"name": re.compile("keywords", re.I)})
    meta_kw = mk["content"].strip() if mk and mk.get("content") else \
        f"{title}, Sarkari Naukari 2026, Government Jobs 2026"

    # H1
    h1t = soup.find("h1")
    h1  = replace_brand(h1t.get_text(strip=True)) if h1t else title

    # Short description paragraph
    desc = ""
    for p in soup.find_all("p"):
        txt = p.get_text(strip=True)
        if len(txt) > 60:
            desc = replace_brand(txt); break
    if not desc: desc = meta_desc

    # All tables
    tables = soup.find_all("table")
    date_tbl = fee_tbl = links_tbl = ""
    other_tbls = []

    for tbl in tables:
        txt = tbl.get_text(" ", strip=True).lower()
        tbl_s = replace_brand(str(tbl))
        # apply class
        s2 = BeautifulSoup(tbl_s, "html.parser")
        t2 = s2.find("table")
        if t2:
            t2["class"] = ["ptbl"]
            for a in t2.find_all("a", href=True):
                a["target"] = "_blank"; a["rel"] = "noopener"
            tbl_s = str(t2)

        has_links = any(w in txt for w in ["apply", "notification", "official", "download", "click here"])
        links_count = len(BeautifulSoup(tbl_s, "html.parser").find_all("a", href=True))

        if has_links and links_count >= 2 and not links_tbl:
            links_tbl = tbl_s
        elif any(w in txt for w in ["application begin", "last date", "exam date", "apply online"]) and not date_tbl:
            date_tbl = tbl_s
        elif any(w in txt for w in ["general", "fee", "₹", "rs."]) and "obc" in txt and not fee_tbl:
            fee_tbl = tbl_s
        else:
            other_tbls.append(tbl_s)

    # Build body HTML
    parts = []

    if date_tbl or fee_tbl:
        cols = []
        if date_tbl:
            cols.append(f'<div class="ibox" style="margin-bottom:0"><h2 class="hl-b"><i class="fas fa-calendar-check"></i> Important Dates</h2><div style="overflow-x:auto">{date_tbl}</div></div>')
        if fee_tbl:
            cols.append(f'<div class="ibox" style="margin-bottom:0"><h2 class="hl-b"><i class="fas fa-money-bill-wave"></i> Application Fee</h2><div style="overflow-x:auto">{fee_tbl}</div></div>')
        gs = "display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:1.8rem;" if len(cols)==2 else "margin-bottom:1.8rem;"
        parts.append(f'<div style="{gs}">{"".join(cols)}</div>')

    for t in other_tbls:
        parts.append(f'<div style="overflow-x:auto;margin-bottom:1.8rem;">{t}</div>')

    if links_tbl:
        parts.append(f'''
    <h2 class="hl-m" style="text-align:center;margin-bottom:1.2rem;font-size:1.2rem;">
      Interested Candidates Can Read the Full Notification Before Apply Online
    </h2>
    <div style="overflow-x:auto;margin-bottom:1.5rem;">{links_tbl}</div>
    <div style="overflow-x:auto;">
      <table class="ptbl">
        <tbody>
          <tr><td class="hl-g" colspan="2" style="font-size:1.1rem;background:rgba(25,135,84,.05);padding:1rem;">
            <i class="fab fa-telegram"></i> Join Our Channels for Instant 2026 Updates</td></tr>
          <tr><td class="hl-m" style="font-weight:700;">Telegram Channel</td>
              <td><a href="https://t.me/sarkarinaukariinfos" target="_blank" style="color:#0088cc"><i class="fab fa-telegram"></i> Click Here</a></td></tr>
          <tr><td class="hl-m" style="font-weight:700;">WhatsApp Channel</td>
              <td><a href="#" target="_blank" style="color:#25d366"><i class="fab fa-whatsapp"></i> Click Here</a></td></tr>
        </tbody>
      </table>
    </div>''')
    else:
        parts.append(build_fallback_body(title).replace('{title}', title))

    body = "\n".join(parts) if parts else build_fallback_body(title)
    return {"seo_title": seo_title, "meta_desc": meta_desc, "meta_kw": meta_kw,
            "h1": h1, "description": desc, "body_html": body}


def find_source_url_for(title, all_source_links):
    """Find the best matching link on sarkariresult.com for a given title."""
    tl = title.lower()
    slug = slugify(title)
    # 1. Exact title match
    if title in all_source_links: return all_source_links[title]
    # 2. Slug contains match
    for text, url in all_source_links.items():
        if slug in url.lower() or slugify(text) == slug:
            return url
    # 3. First-20-chars substring match
    prefix = tl[:22]
    for text, url in all_source_links.items():
        if prefix in text.lower():
            return url
    return None


def process_post(item, cat_key, all_source_links):
    """Scrape + render one post. Returns entry dict."""
    title = item["title"]
    link  = item["link"]

    slug     = slugify(title)
    filename = slug + ".html"
    filepath = os.path.join(POSTS_DIR, filename)

    # Get source URL
    src_url = find_source_url_for(title, all_source_links)

    parsed = None
    if src_url:
        time.sleep(DELAY)
        html = fetch(src_url)
        if html:
            try: parsed = parse_source_page(html, title)
            except: pass

    if not parsed:
        parsed = build_seo_content(title, cat_key)

    schema = json.dumps({
        "@context":"https://schema.org","@type":"Article",
        "headline": parsed["h1"],
        "description": parsed["meta_desc"],
        "author": {"@type":"Organization","name":"Sarkari Naukari Infos"},
        "publisher": {"@type":"Organization","name":"Sarkari Naukari Infos"},
        "datePublished":"2026-03-08",
    })

    page_html = POST_TPL.format(
        seo_title=parsed["seo_title"],
        meta_desc=parsed["meta_desc"],
        meta_kw=parsed["meta_kw"],
        canonical=f"https://sarkarinaukariinfos.net/posts/{filename}",
        schema=schema,
        h1=parsed["h1"],
        org=detect_org(title),
        cat_label=detect_cat_label(cat_key),
        cat_page=detect_cat_page(cat_key),
        short_t=title[:55],
        description=parsed["description"],
        body_html=parsed["body_html"],
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(page_html)

    return {"title": title, "link": f"posts/{filename}", "scraped": bool(src_url and parsed), "ts": int("20260308")}


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 62)
    print("  STEP 1 — Filter data.js to 2026-only posts")
    print("=" * 62)

    with open(DATA_JS, "r", encoding="utf-8") as f:
        content = f.read()

    m = re.search(r"const siteData\s*=\s*(\{.*?\});", content, re.DOTALL)
    data = json.loads(m.group(1))

    new_data = {}
    total_kept = 0
    total_removed = 0

    for cat, items in data.items():
        if not isinstance(items, list):
            new_data[cat] = items
            continue
        kept = [it for it in items if "2026" in it.get("title","")]
        removed = len(items) - len(kept)
        new_data[cat] = kept
        total_kept += len(kept)
        total_removed += removed
        print(f"  {cat:16s}: kept {len(kept):3d}, removed {removed:3d}")

    print(f"\n  Total kept: {total_kept}, removed: {total_removed}")

    new_json = json.dumps(new_data, ensure_ascii=False, indent=2)
    new_content = re.sub(r"const siteData\s*=\s*\{.*?\};", f"const siteData = {new_json};",
                         content, count=1, flags=re.DOTALL)
    with open(DATA_JS, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  ✅ data.js updated\n")

    # ── STEP 2: Collect source URLs from sarkariresult.com homepage ────────────
    print("=" * 62)
    print("  STEP 2 — Collecting source URLs from sarkariresult.com")
    print("=" * 62)

    all_source_links = {}
    home_html = fetch(SOURCE + "/")
    if home_html:
        soup = BeautifulSoup(home_html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            t = a.get_text(strip=True)
            if not t or len(t) < 5: continue
            if href.startswith("/"): href = SOURCE + href
            if "sarkariresult.com" not in href: continue
            all_source_links[t] = href
        print(f"  Collected {len(all_source_links)} links from homepage.")

    # Also fetch category pages for more matches
    for cp in ["/latestjob/", "/result/", "/admit/"]:
        ch = fetch(SOURCE + cp)
        if not ch: continue
        csoup = BeautifulSoup(ch, "html.parser")
        for a in csoup.find_all("a", href=True):
            href = a["href"]; t = a.get_text(strip=True)
            if not t or len(t) < 5: continue
            if href.startswith("/"): href = SOURCE + href
            if "sarkariresult.com" not in href: continue
            if t not in all_source_links:
                all_source_links[t] = href
        time.sleep(0.4)
    print(f"  Total source links: {len(all_source_links)}\n")

    # ── STEP 3: Scrape + build post pages for all 2026 items ──────────────────
    print("=" * 62)
    print("  STEP 3 — Building 2026 post pages with SEO content")
    print("=" * 62)

    tasks = []
    for cat_key, items in new_data.items():
        if isinstance(items, list):
            for it in items:
                tasks.append((it, cat_key))

    done = 0
    results_by_cat = {k: [] for k in new_data if isinstance(new_data[k], list)}

    def worker(task):
        it, cat_key = task
        try:
            return cat_key, process_post(it, cat_key, all_source_links)
        except Exception as e:
            return cat_key, {"title": it["title"], "link": it["link"], "error": str(e)}

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(worker, t): t for t in tasks}
        for fut in concurrent.futures.as_completed(futures):
            done += 1
            cat_key, result = fut.result()
            status = "🌐" if result.get("scraped") else "📝"
            print(f"  [{done:3d}/{len(tasks)}] {status} {result['title'][:62]}")
            if cat_key in results_by_cat:
                results_by_cat[cat_key].append({"title": result["title"], "link": result["link"]})

    print(f"\n  ✅ {done} post pages built.\n")

    # ── STEP 4: Regenerate category pages (clean table design, no filter bar) ──
    print("=" * 62)
    print("  STEP 4 — Rebuilding category pages (clean list design)")
    print("=" * 62)

    active_flags = {"jobs.html": "a_jobs", "results.html": "a_res", "admitcard.html": "a_ac",
                    "answerkey.html": "a_ak", "syllabus.html": "a_sy", "admission.html": "a_ad"}

    for cat_key, items in new_data.items():
        if cat_key not in CAT_META: continue
        meta = CAT_META[cat_key]
        h1   = meta["h1"]
        fn   = meta["file"]
        icon = meta["icon"]
        hero = meta["hero"]

        # Build items_json from updated links in results_by_cat
        cat_items = results_by_cat.get(cat_key, [])
        # Fallback to new_data if results_by_cat empty for this category
        if not cat_items:
            cat_items = [{"title": it["title"], "link": it["link"]} for it in items]

        items_json = json.dumps([{"t": it["title"], "l": it["link"]} for it in cat_items], ensure_ascii=False)

        # Active class flags
        all_flags = {k: "" for k in ["a_jobs","a_res","a_ac","a_ak","a_sy","a_ad"]}
        af = active_flags.get(fn)
        if af: all_flags[af] = " active"

        page_html = CAT_TPL.format(
            h1=h1, icon=icon, hero=hero,
            count=len(cat_items),
            items_json=items_json,
            **all_flags
        )

        fp = os.path.join(BASE_DIR, fn)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"  ✅ {fn:22s} ({len(cat_items)} posts, 2026 only)")

    print("\n" + "=" * 62)
    print(f"  ALL DONE! Kept {total_kept} 2026 posts, removed {total_removed}.")
    print("=" * 62)


if __name__ == "__main__":
    main()
