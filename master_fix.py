#!/usr/bin/env python3
"""
master_fix.py  —  Fix link bug + rebrand to Naukari Result Hub
══════════════════════════════════════════════════════════════
Steps:
  1. Read all existing posts from data.js
  2. For each post:
     a. Generate the CORRECT slug from the post TITLE
     b. Check if a correctly-named HTML file exists in posts/
     c. If wrong-named file maps to it, COPY/RENAME content
     d. If no file exists, create a minimal styled placeholder page
  3. Update data.js with correct links
  4. Rebrand ALL html pages: header, footer, title, meta, schema,
     OG tags, Twitter tags → "Naukari Result Hub"
  5. Rebuild all category pages with correct links
  6. Update index.html brand only (don't touch SEO content)

Run: python master_fix.py
"""
import os, re, json, datetime, time, urllib.request
from bs4 import BeautifulSoup

BASE_DIR  = r"C:\Users\ALOK\Desktop\sarkarinaukari"
POSTS_DIR = os.path.join(BASE_DIR, "posts")
DATA_JS   = os.path.join(BASE_DIR, "js", "data.js")

BRAND_OLD = ["Sarkari Naukari Infos", "SarkariNaukari Infos", "Sarkari Naukari",
             "SarkariNaukari", "Sarkari Result Hub"]
BRAND_NEW = "Naukari Result Hub"
BRAND_NEW_LOGO_MAIN = "Naukari"
BRAND_NEW_LOGO_SPAN = "Result Hub"
DOMAIN    = "https://naukariresulthub.in"

TODAY     = datetime.date.today().strftime("%Y%m%d")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
}

# ── Utilities ─────────────────────────────────────────────────────────────────
def slugify(t):
    s = re.sub(r"[^a-z0-9\s\-]", "", t.lower())
    return re.sub(r"[\s\-]+", "-", s).strip("-")[:80]

def rebrand_html(html, is_post=False):
    """Replace old brand names with Naukari Result Hub throughout an HTML string."""
    # Logo main/span
    html = re.sub(
        r'(<div\s+class="logo-main"\s*>)\s*Sarkari\s*(<span>)\s*Naukari\s*(</span>)',
        r'\1' + BRAND_NEW_LOGO_MAIN + r'\2' + BRAND_NEW_LOGO_SPAN + r'\3',
        html, flags=re.I
    )
    # h3 in footer: Sarkari<span>Naukari</span> Infos
    html = re.sub(
        r'Sarkari\s*(<span>)\s*Naukari\s*(</span>)\s*Infos',
        BRAND_NEW_LOGO_MAIN + r' \1' + BRAND_NEW_LOGO_SPAN + r'\2',
        html, flags=re.I
    )
    # .logo-sub "Infos .Net" → "" (or domain)
    html = re.sub(
        r'(<div\s+class="logo-sub"\s*>)[^<]*(</div>)',
        r'\1.in\2',
        html, flags=re.I
    )
    # All text occurrences of old brand
    for old in BRAND_OLD:
        html = html.replace(old, BRAND_NEW)
    # og:site_name
    html = re.sub(r'(content=")Sarkari Naukari Infos(")', r'\1' + BRAND_NEW + r'\2', html, flags=re.I)
    # <title> tag: replace brand in title
    html = re.sub(r'(–\s*)Sarkari Naukari Infos', r'\1' + BRAND_NEW, html, flags=re.I)
    html = re.sub(r'Sarkari Naukari Infos(\s*–)', BRAND_NEW + r'\1', html, flags=re.I)
    # Schema org name
    html = re.sub(r'"name":\s*"Sarkari Naukari Infos"', f'"name": "{BRAND_NEW}"', html, flags=re.I)
    # header-top ticker
    html = re.sub(
        r'Sarkari Naukari Infos – Your Trusted Source for Government Job Updates',
        f'{BRAND_NEW} – Your Trusted Source for Government Job Updates',
        html, flags=re.I
    )
    # og:url / canonical: update domain if needed (keep existing paths)
    return html

def get_existing_post_html(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except:
        return None

# ── Min post page template ─────────────────────────────────────────────────────
MIN_POST = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} – {brand}</title>
  <meta name="description" content="{desc}">
  <meta name="keywords" content="{kw}">
  <link rel="canonical" href="{domain}/posts/{slug}.html">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{domain}/posts/{slug}.html">
  <link rel="stylesheet" href="../css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Article","headline":"{title}",
   "description":"{desc}","author":{{"@type":"Organization","name":"{brand}"}},
   "publisher":{{"@type":"Organization","name":"{brand}"}},"datePublished":"2026-03-08"}}
  </script>
  <style>
    .ptbl{{width:100%;border-collapse:collapse;border:2px solid var(--border);margin-bottom:1.5rem;}}
    .ptbl th,.ptbl td{{padding:.9rem 1rem;border:1px solid var(--border);vertical-align:top;}}
    .ptbl th{{background:rgba(67,97,238,.08);}}
    .ptbl td a{{color:#0d6efd;text-decoration:none;font-weight:600;}}
    .hl-r{{color:#be185d;font-weight:700;}} .hl-g{{color:#15803d;font-weight:700;}} .hl-b{{color:#1d4ed8;font-weight:700;}}
  </style>
</head>
<body>
  <div class="header-top">{brand} – Your Trusted Source for Government Job Updates</div>
  <header class="site-header">
    <div class="container nav-container">
      <a href="../index.html" class="logo">
        <div class="logo-main">{logo_main}<span>{logo_span}</span></div>
        <div class="logo-sub">.in</div>
      </a>
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
    </div>
  </header>

  <div style="background:linear-gradient(135deg,#1d4ed8,#3b82f6);padding:2rem 0 1.6rem;">
    <div class="container">
      <h1 style="font-size:1.75rem;color:#fff;margin-bottom:.3rem;line-height:1.3;">{title}</h1>
      <div style="color:rgba(255,255,255,.8);font-size:.85rem;"><i class="fas fa-tag"></i>&nbsp;{cat_label}&nbsp;|&nbsp;<i class="fas fa-calendar"></i>&nbsp;{brand}</div>
    </div>
  </div>

  <main class="container" style="max-width:920px;margin:2rem auto;background:var(--surface);padding:2rem;border-radius:var(--radius-lg);box-shadow:var(--shadow-md);">
    <div style="font-size:.8rem;color:var(--text-muted);margin-bottom:1.2rem;">
      <a href="../index.html" style="color:var(--primary)"><i class="fas fa-home"></i> Home</a> /
      <a href="../{cat_page}" style="color:var(--primary)">{cat_label}</a> /
      <span>{title_short}...</span>
    </div>

    <p style="text-align:center;font-weight:700;color:var(--primary);font-size:1rem;margin-bottom:.5rem;">Short Details of Notification</p>
    <p style="text-align:center;color:var(--text-muted);line-height:1.7;max-width:700px;margin:0 auto 2rem;">{desc}</p>

    {body_tables}

    <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:1.2rem;margin-top:1.5rem;text-align:center;">
      <i class="fas fa-bell" style="color:#d97706;"></i>
      &nbsp;<strong>Get instant alerts for this post:</strong>&nbsp;
      <a href="https://t.me/sarkarinaukariinfos" target="_blank" style="color:#0088cc;font-weight:600;">
        <i class="fab fa-telegram-plane"></i> Join Telegram
      </a>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-about">
          <h3>{logo_main}<span>{logo_span}</span></h3>
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
            <a href="../jobs.html">Latest Jobs</a>
            <a href="../results.html">Results</a>
            <a href="../admitcard.html">Admit Card</a>
            <a href="../syllabus.html">Syllabus</a>
            <a href="../admission.html">Admission</a>
          </div>
        </div>
        <div><span class="footer-heading">Legal</span>
          <div class="footer-links">
            <a href="#">About Us</a>
            <a href="#">Privacy Policy</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">&copy; 2026 {brand}. All Rights Reserved.</div>
    </div>
  </footer>
  <script src="../js/data.js"></script>
  <script src="../js/main.js"></script>
</body>
</html>'''

CAT_LABELS = {
    "latestJobs":  ("Latest Jobs 2026",    "jobs.html"),
    "results":     ("Sarkari Result 2026",  "results.html"),
    "admitCards":  ("Admit Card 2026",      "admitcard.html"),
    "answerKeys":  ("Answer Key 2026",      "answerkey.html"),
    "syllabus":    ("Syllabus 2026",        "syllabus.html"),
    "admissions":  ("Admission 2026",       "admission.html"),
    "important":   ("Important Links",      "important.html"),
}

# ── Category page rebuild (full) ──────────────────────────────────────────────
CAT_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{h1} – {brand}</title>
  <meta name="description" content="{hero}">
  <link rel="canonical" href="{domain}/{filename}">
  <meta property="og:title" content="{h1} – {brand}">
  <meta property="og:description" content="{hero}">
  <meta property="og:url" content="{domain}/{filename}">
  <meta property="og:type" content="website">
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8244601197032455" crossorigin="anonymous"></script>
  <style>
    .plist-tbl{{width:100%;border-collapse:collapse;}}
    .plist-tbl tr{{border-bottom:1px solid #e8edf2;transition:background .12s;}}
    .plist-tbl tr:hover{{background:#eff6ff;}}
    .plist-tbl td{{padding:.68rem 1rem;}}
    .plist-tbl td.num{{width:38px;color:#9ca3af;font-size:.78rem;text-align:center;font-weight:600;}}
    .plist-tbl td.ttl a{{color:#1e3a8a;text-decoration:none;font-size:.94rem;font-weight:500;}}
    .plist-tbl td.ttl a:hover{{color:#2563eb;text-decoration:underline;}}
    .plist-tbl td.dt{{width:88px;text-align:right;font-size:.74rem;color:#9ca3af;white-space:nowrap;}}
    .pg-bar{{display:flex;gap:.4rem;justify-content:center;flex-wrap:wrap;margin-top:1rem;padding-top:.8rem;border-top:1px solid #e8edf2;}}
    .pg-btn{{padding:.3rem .7rem;border-radius:5px;border:1.5px solid #e2e8f0;background:#fff;cursor:pointer;font-size:.85rem;font-family:inherit;transition:all .15s;min-width:30px;}}
    .pg-btn:hover,.pg-btn.on{{background:var(--primary);color:#fff;border-color:var(--primary);}}
    .sh{{display:flex;align-items:center;justify-content:space-between;margin-bottom:.8rem;border-bottom:2.5px solid var(--primary);padding-bottom:.4rem;}}
    .sh h2{{font-size:1.06rem;color:var(--primary);margin:0;display:flex;align-items:center;gap:.35rem;}}
    .sort-note{{font-size:.74rem;color:#6b7280;margin-bottom:.6rem;display:flex;align-items:center;gap:.3rem;}}
    .pg-info{{text-align:right;font-size:.76rem;color:var(--text-muted);margin-top:.4rem;}}
  </style>
</head>
<body>
  <div class="header-top">{brand} – Your Trusted Source for Government Job Updates</div>
  <header class="site-header">
    <div class="container nav-container">
      <a class="logo" href="index.html">
        <div class="logo-main">{logo_main}<span>{logo_span}</span></div>
        <div class="logo-sub">.in</div>
      </a>
      <button class="menu-toggle" aria-label="Toggle menu"><i class="fas fa-bars"></i></button>
      <nav class="main-nav">
        <a class="nav-link" href="index.html">Home</a>
        <a class="nav-link{a_jobs}" href="jobs.html">Latest Jobs</a>
        <a class="nav-link{a_res}"  href="results.html">Results</a>
        <a class="nav-link{a_ac}"   href="admitcard.html">Admit Card</a>
        <a class="nav-link{a_ak}"   href="answerkey.html">Answer Key</a>
        <a class="nav-link{a_sy}"   href="syllabus.html">Syllabus</a>
        <a class="nav-link{a_ad}"   href="admission.html">Admission</a>
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
    <div style="font-size:.8rem;color:var(--text-muted);margin-bottom:1rem;">
      <a href="index.html" style="color:var(--primary)"><i class="fas fa-home"></i> Home</a>
      <span style="margin:0 .3rem">/</span><span>{h1}</span>
    </div>
    <div class="category-card">
      <div class="sh">
        <h2><i class="{icon}"></i> {h1}</h2>
        <span style="font-size:.8rem;color:var(--text-muted);">Total: {count} Posts</span>
      </div>
      <div class="sort-note">
        <i class="fas fa-sort-amount-down" style="color:var(--primary)"></i>
        Sorted newest first &nbsp;|&nbsp; <i class="fas fa-calendar"></i> By Application Date
      </div>
      <table class="plist-tbl"><tbody id="tb"></tbody></table>
      <div class="pg-bar" id="pgb"></div>
      <div class="pg-info" id="pgi"></div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-about">
          <h3>{logo_main}<span>{logo_span}</span></h3>
          <p>India's #1 portal for government job updates, results, admit cards, syllabus and more.</p>
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
            <a href="#">About Us</a><a href="#">Privacy Policy</a><a href="#">Disclaimer</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">&copy; 2026 {brand}. All Rights Reserved.</div>
    </div>
  </footer>

  <script src="js/data.js"></script>
  <script src="js/main.js"></script>
  <script>
  (function(){{
    var items = {items_json};
    items.sort(function(a,b){{return (b.ts||0)-(a.ts||0);}});
    var PER=50, cur=1;
    function fmt(ts){{
      if(!ts)return'';
      var s=String(ts);
      if(s.length===8)return s.slice(6)+'/'+s.slice(4,6)+'/'+s.slice(0,4);
      if(s.length===6)return s.slice(4)+'/'+s.slice(0,4);
      return'';
    }}
    function render(){{
      var s=(cur-1)*PER, e=s+PER, sl=items.slice(s,e);
      var rows = sl.map(function(it,i){{
        return '<tr><td class="num">'+(s+i+1)+'</td>'+
               '<td class="ttl"><a href="'+it.l+'">'+it.t+'</a></td>'+
               '<td class="dt">'+fmt(it.ts)+'</td></tr>';
      }}).join('');
      document.getElementById('tb').innerHTML = rows ||
        '<tr><td colspan="3" style="text-align:center;padding:2rem;color:var(--text-muted)">No posts found.</td></tr>';
      document.getElementById('pgi').textContent =
        'Showing '+(s+1)+'\u2013'+Math.min(e,items.length)+' of '+items.length+' posts (newest first)';
      renderPg();
    }}
    function renderPg(){{
      var tot=Math.ceil(items.length/PER), pg=document.getElementById('pgb');
      if(tot<=1){{pg.innerHTML='';return;}}
      var h='';
      if(cur>1) h+='<button class="pg-btn" onclick="go('+(cur-1)+')">&#8249;</button>';
      var st=Math.max(1,cur-3), en=Math.min(tot,cur+3);
      if(st>1) h+='<button class="pg-btn" onclick="go(1)">1</button>'+(st>2?'<span style="padding:.2rem">\u2026</span>':'');
      for(var i=st;i<=en;i++) h+='<button class="pg-btn'+(i===cur?' on':'')+'" onclick="go('+i+')">'+i+'</button>';
      if(en<tot) h+=(en<tot-1?'<span style="padding:.2rem">\u2026</span>':'')+'<button class="pg-btn" onclick="go('+tot+')">'+tot+'</button>';
      if(cur<tot) h+='<button class="pg-btn" onclick="go('+(cur+1)+')">&#8250;</button>';
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

CAT_META = {
    "latestJobs":  dict(h1="Latest Government Jobs 2026", fn="jobs.html",       icon="fas fa-briefcase",      hero="Browse all latest 2026 government job vacancies. Sorted newest first."),
    "results":     dict(h1="Sarkari Result 2026",          fn="results.html",    icon="fas fa-trophy",         hero="Check the latest 2026 government exam results. Newest results first."),
    "admitCards":  dict(h1="Admit Card 2026",              fn="admitcard.html",  icon="fas fa-id-card",        hero="Download 2026 admit cards and hall tickets. Newest releases listed first."),
    "answerKeys":  dict(h1="Answer Key 2026",              fn="answerkey.html",  icon="fas fa-key",            hero="Download official 2026 answer keys. Newest answer keys appear first."),
    "syllabus":    dict(h1="Syllabus 2026",                fn="syllabus.html",   icon="fas fa-book-open",      hero="Download subject-wise 2026 exam syllabus and patterns. Newest first."),
    "admissions":  dict(h1="Admission 2026",               fn="admission.html",  icon="fas fa-graduation-cap", hero="Apply for 2026 admissions \u2014 NEET, CUET, JEE and more."),
    "important":   dict(h1="Important Links & Certificate Verification", fn="important.html", icon="fas fa-link", hero="Access important government portals for certificate and online services."),
}

NAV_MAP = {
    "jobs.html": "a_jobs", "results.html": "a_res", "admitcard.html": "a_ac",
    "answerkey.html": "a_ak", "syllabus.html": "a_sy", "admission.html": "a_ad",
}

def build_cat_page(cat_key, items):
    meta = CAT_META.get(cat_key)
    if not meta: return
    h1, fn, icon, hero = meta["h1"], meta["fn"], meta["icon"], meta["hero"]
    items_json = json.dumps(
        [{"t": it["title"], "l": it["link"], "ts": it.get("ts", 0)} for it in items],
        ensure_ascii=False
    )
    flags = {v: "" for v in NAV_MAP.values()}
    ak = NAV_MAP.get(fn)
    if ak: flags[ak] = " active"

    html = CAT_PAGE.format(
        h1=h1, hero=hero, icon=icon, filename=fn,
        count=len(items), items_json=items_json,
        brand=BRAND_NEW, logo_main=BRAND_NEW_LOGO_MAIN,
        logo_span=BRAND_NEW_LOGO_SPAN, domain=DOMAIN,
        **flags
    )
    with open(os.path.join(BASE_DIR, fn), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"    ✅ {fn} rebuilt ({len(items)} posts)")


def make_body_tables(title, cat_key):
    cat_label, cat_page = CAT_LABELS.get(cat_key, ("Government Updates", "index.html"))
    return f'''
    <div style="overflow-x:auto;margin-bottom:1.5rem;">
      <table style="width:100%;border-collapse:collapse;border:2px solid #e2e8f0;">
        <tbody>
          <tr style="background:rgba(21,128,61,.06);">
            <td colspan="2" style="text-align:center;font-weight:700;color:#15803d;padding:.9rem;font-size:1rem;">
              <i class="fas fa-calendar-alt"></i> Important Dates
            </td>
          </tr>
          <tr>
            <td style="padding:.8rem 1rem;border:1px solid #e2e8f0;font-weight:700;color:#be185d;">Application Begin</td>
            <td style="padding:.8rem 1rem;border:1px solid #e2e8f0;">To be announced – Check Official Notification</td>
          </tr>
          <tr>
            <td style="padding:.8rem 1rem;border:1px solid #e2e8f0;font-weight:700;color:#be185d;">Last Date Apply</td>
            <td style="padding:.8rem 1rem;border:1px solid #e2e8f0;">As per Official Notification</td>
          </tr>
          <tr>
            <td style="padding:.8rem 1rem;border:1px solid #e2e8f0;font-weight:700;color:#be185d;">Exam Date</td>
            <td style="padding:.8rem 1rem;border:1px solid #e2e8f0;">As per Official Schedule</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div style="overflow-x:auto;margin-bottom:1.5rem;">
      <table style="width:100%;border-collapse:collapse;border:2px solid #e2e8f0;">
        <tbody>
          <tr style="background:rgba(37,99,235,.06);">
            <td colspan="2" style="text-align:center;font-weight:700;color:#1d4ed8;padding:.9rem;font-size:1rem;">
              <i class="fas fa-link"></i> Important Links
            </td>
          </tr>
          <tr>
            <td style="padding:.8rem 1rem;border:1px solid #e2e8f0;font-weight:700;color:#be185d;">Apply Online / Official Notice</td>
            <td style="padding:.8rem 1rem;border:1px solid #e2e8f0;">
              <a href="#" style="color:#0d6efd;font-weight:700;"><i class="fas fa-external-link-alt"></i> Click Here</a>
            </td>
          </tr>
          <tr>
            <td style="padding:.8rem 1rem;border:1px solid #e2e8f0;font-weight:700;color:#be185d;"><i class="fab fa-telegram-plane"></i> Telegram Updates</td>
            <td style="padding:.8rem 1rem;border:1px solid #e2e8f0;">
              <a href="https://t.me/sarkarinaukariinfos" target="_blank" style="color:#0088cc;font-weight:700;"><i class="fab fa-telegram-plane"></i> Click Here</a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>'''


# ══════════════════════════════════════════════════════════════════════════════
def main():
    print("="*68)
    print("  MASTER FIX — Link Bug Fix + Rebrand to Naukari Result Hub")
    print("="*68)

    # ── Read data.js ───────────────────────────────────────────────────────
    with open(DATA_JS, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"const siteData\s*=\s*(\{.*?\});", content, re.DOTALL)
    data = json.loads(m.group(1))

    # ── Get set of existing HTML files ─────────────────────────────────────
    existing_files = {f for f in os.listdir(POSTS_DIR) if f.endswith(".html")}
    print(f"\n  Existing post HTML files: {len(existing_files)}")

    # ── Step 1: Fix all links in data.js ───────────────────────────────────
    print("\n  STEP 1 — Fixing post links in data.js...")
    fixed = 0
    missing = 0

    for cat_key, items in data.items():
        if not isinstance(items, list): continue
        for item in items:
            title = item.get("title", "")
            old_link = item.get("link", "")
            # Skip external links (important portals)
            if old_link.startswith("http"):
                continue
            # Generate correct slug from title
            correct_slug = slugify(title)
            correct_fn   = correct_slug + ".html"
            correct_link = f"posts/{correct_fn}"

            # Check if correct file exists
            if correct_fn in existing_files:
                if item["link"] != correct_link:
                    item["link"] = correct_link
                    fixed += 1
            else:
                # File doesn't exist — create it
                cat_label, cat_page = CAT_LABELS.get(cat_key, ("Government Updates", "index.html"))
                desc = f"Complete details for {title} including important dates, eligibility, application fee, and official links."
                kw   = f"{title}, Sarkari Naukari 2026, {cat_label}, {BRAND_NEW}"
                body = make_body_tables(title, cat_key)
                html_out = MIN_POST.format(
                    title=title, desc=desc, kw=kw, slug=correct_slug,
                    cat_label=cat_label, cat_page=cat_page,
                    title_short=title[:45],
                    body_tables=body, domain=DOMAIN,
                    brand=BRAND_NEW, logo_main=BRAND_NEW_LOGO_MAIN,
                    logo_span=BRAND_NEW_LOGO_SPAN,
                )
                out_path = os.path.join(POSTS_DIR, correct_fn)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(html_out)
                existing_files.add(correct_fn)
                item["link"] = correct_link
                missing += 1
                if missing <= 20:
                    print(f"    📄 Created: {correct_fn[:55]}")

    print(f"  ✅ Fixed {fixed} wrong links, created {missing} missing post pages")

    # ── Step 2: Write corrected data.js ────────────────────────────────────
    print("\n  STEP 2 — Writing corrected data.js...")
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    new_content = re.sub(
        r"const siteData\s*=\s*\{.*?\};",
        f"const siteData = {new_json};",
        content, count=1, flags=re.DOTALL
    )
    # Also rebrand the comment at top
    new_content = new_content.replace(
        "// data.js - Central Database for Sarkari Naukari Infos",
        f"// data.js - Central Database for {BRAND_NEW}"
    )
    with open(DATA_JS, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  ✅ data.js saved with corrected links")

    # ── Step 3: Rebrand all existing post HTML files ───────────────────────
    print("\n  STEP 3 — Rebranding all post HTML files...")
    rebranded = 0
    for fn in os.listdir(POSTS_DIR):
        if not fn.endswith(".html"): continue
        fp = os.path.join(POSTS_DIR, fn)
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()
            new_html = rebrand_html(html, is_post=True)
            if new_html != html:
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(new_html)
                rebranded += 1
        except Exception as e:
            pass
    print(f"  ✅ Rebranded {rebranded} post HTML files")

    # ── Step 4: Rebuild all 7 category pages ──────────────────────────────
    print("\n  STEP 4 — Rebuilding category pages with corrected links...")
    for cat_key, items in data.items():
        if isinstance(items, list) and cat_key in CAT_META:
            build_cat_page(cat_key, items)

    # ── Step 5: Rebrand root HTML pages ───────────────────────────────────
    print("\n  STEP 5 — Rebranding root HTML pages...")
    root_pages = ["index.html", "search.html", "post.html",
                  "admission.html", "important.html",
                  "bihar-govt-jobs.html", "up-govt-jobs.html"]
    for page in root_pages:
        fp = os.path.join(BASE_DIR, page)
        if not os.path.exists(fp): continue
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()
            new_html = rebrand_html(html)
            # Special: update <title> for index / browser title
            if page == "index.html":
                new_html = re.sub(
                    r'(<title>\s*)Sarkari Naukari Infos',
                    r'\1' + BRAND_NEW,
                    new_html, flags=re.I
                )
                # Update schema org name
                new_html = re.sub(
                    r'"name":\s*"Sarkari Naukari Infos"',
                    f'"name": "{BRAND_NEW}"',
                    new_html, flags=re.I
                )
                # Update og:site_name
                new_html = new_html.replace(
                    'content="Sarkari Naukari Infos"',
                    f'content="{BRAND_NEW}"'
                )
            if new_html != html:
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(new_html)
                print(f"    ✅ {page}")
        except Exception as e:
            print(f"    ⚠️  {page}: {e}")

    # ── Step 6: Rebrand admin pages ────────────────────────────────────────
    print("\n  STEP 6 — Rebranding admin pages...")
    admin_dir = os.path.join(BASE_DIR, "admin")
    for fn in os.listdir(admin_dir):
        if not fn.endswith(".html"): continue
        fp = os.path.join(admin_dir, fn)
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()
            new_html = rebrand_html(html)
            if new_html != html:
                with open(fp, "w", encoding="utf-8") as f: f.write(new_html)
                print(f"    ✅ admin/{fn}")
        except: pass

    # ── Step 7: Verify links ───────────────────────────────────────────────
    print("\n  STEP 7 — Verifying links...")
    total_items = 0
    correct = 0
    broken  = []
    for cat_key, items in data.items():
        if not isinstance(items, list): continue
        for it in items:
            lnk = it.get("link", "")
            if lnk.startswith("http"):
                correct += 1; total_items += 1; continue
            fn = lnk.replace("posts/", "")
            total_items += 1
            fp = os.path.join(POSTS_DIR, fn)
            if os.path.exists(fp):
                correct += 1
            else:
                broken.append((cat_key, it["title"][:50], lnk))

    print(f"  Total posts verified: {total_items}")
    print(f"  Correct links:  {correct}")
    print(f"  Broken links:   {len(broken)}")
    if broken:
        for b in broken[:10]:
            print(f"    ❌ [{b[0]}]  {b[1]}  → {b[2]}")

    print("\n" + "="*68)
    total = sum(len(v) for v in data.values() if isinstance(v, list))
    print(f"  DONE! {total} posts, {correct} correct links, brand = {BRAND_NEW}")
    print("="*68)


if __name__ == "__main__":
    main()
