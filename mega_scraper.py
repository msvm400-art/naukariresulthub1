#!/usr/bin/env python3
"""
mega_scraper.py — Comprehensive scraper for Sarkari Naukari website
Crawls sarkariresult.com, extracts full post content + SEO metadata,
generates properly-styled HTML pages, and updates data.js.

Run: python mega_scraper.py
"""

import os, re, json, time, gzip, hashlib, sys
import concurrent.futures
import urllib.request
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
BASE_DIR   = r"C:\Users\ALOK\Desktop\sarkarinaukari"
POSTS_DIR  = os.path.join(BASE_DIR, "posts")
JS_DIR     = os.path.join(BASE_DIR, "js")
DATA_JS    = os.path.join(JS_DIR, "data.js")
SOURCE     = "https://www.sarkariresult.com/"
MAX_WORKERS = 8
DELAY       = 0.4           # seconds between requests per thread
MAX_POSTS   = 600           # max pages to scrape
SKIP_SMALL  = False         # if True skip posts that already have large HTML

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Category mapping from URL keywords
CAT_MAP = {
    "latest-job":       "latestJobs",
    "latestjob":        "latestJobs",
    "latest_job":       "latestJobs",
    "admit":            "admitCards",
    "admit-card":       "admitCards",
    "result":           "results",
    "answer-key":       "answerKeys",
    "answerkey":        "answerKeys",
    "syllabus":         "syllabus",
    "admission":        "admissions",
    "certificate":      "important",
    "important":        "important",
    "rojgar":           "latestJobs",
}

CAT_PAGE_MAP = {
    "latestJobs":  "jobs.html",
    "results":     "results.html",
    "admitCards":  "admitcard.html",
    "answerKeys":  "answerkey.html",
    "syllabus":    "syllabus.html",
    "admissions":  "admission.html",
    "important":   "important.html",
}

# ─── HTML TEMPLATE (matches existing site layout) ─────────────────────────────
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{seo_title}</title>
  <meta name="description" content="{meta_desc}">
  <meta name="keywords" content="{meta_keywords}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{seo_title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{seo_title}">
  <meta name="twitter:description" content="{meta_desc}">
  <script type="application/ld+json">{schema}</script>
  <link rel="stylesheet" href="../css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8244601197032455" crossorigin="anonymous"></script>
  <style>
    .post-box{{border:1px solid var(--border);border-radius:var(--radius-md);padding:1.5rem;margin-bottom:2rem;background:rgba(67,97,238,.02);box-shadow:var(--shadow-sm);}}
    .post-box h2{{font-size:1.35rem;text-align:center;margin-bottom:1rem;border-bottom:2px solid var(--primary-light);padding-bottom:.5rem;}}
    .hl-m{{color:#d63384;font-weight:bold;}} .hl-g{{color:#198754;font-weight:bold;}} .hl-b{{color:#0d6efd;font-weight:bold;}}
    .ptable{{width:100%;border-collapse:collapse;text-align:center;border:2px solid var(--border);margin-bottom:2.5rem;box-shadow:var(--shadow-sm);}}
    .ptable th,.ptable td{{padding:1rem;border:1px solid var(--border);vertical-align:top;}}
    .ptable th{{background:rgba(67,97,238,.08);font-size:1.05rem;}}
    .ptable a{{color:#0d6efd;text-decoration:none;font-weight:600;}}
    .ptable a:hover{{text-decoration:underline;}}
    .plist{{list-style:none;padding-left:0;}}
    .plist li{{position:relative;padding-left:22px;margin-bottom:.7rem;line-height:1.6;}}
    .plist li::before{{content:"\\f0da";font-family:"Font Awesome 6 Free";font-weight:900;position:absolute;left:0;color:var(--primary);}}
    .breadcrumb{{font-size:.85rem;color:var(--text-muted);margin-bottom:1.5rem;display:flex;align-items:center;gap:.4rem;flex-wrap:wrap;}}
    .breadcrumb a{{color:var(--primary);}} .breadcrumb a:hover{{text-decoration:underline;}}
  </style>
</head>
<body>
  <div class="header-top">Sarkari Naukari Infos - Your Trusted Source for Government Job Updates</div>
  <header class="site-header">
    <div class="container nav-container">
      <a href="../index.html" class="logo">
        <div class="logo-main">Sarkari<span>Naukari</span></div>
        <div class="logo-sub">Infos .Net</div>
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
      <div class="header-search">
        <input id="header-search-input" type="text" placeholder="Search exams, jobs..." aria-label="Search">
        <button id="header-search-btn"><i class="fas fa-search"></i> Search</button>
      </div>
    </div>
  </header>

  <div class="post-header" style="background:linear-gradient(to right,var(--primary),#60a5fa);padding:3rem 0;margin-bottom:2rem;">
    <div class="container">
      <h1 class="post-title" style="font-size:2.2rem;margin-bottom:.5rem;">{h1}</h1>
      <div style="color:rgba(255,255,255,.85);font-size:.95rem;margin-top:.5rem;">
        <i class="fas fa-building"></i> {org} &nbsp;|&nbsp;
        <i class="fas fa-tag"></i> {cat_label}
      </div>
    </div>
  </div>

  <main class="container animate-fade-in" style="max-width:960px;margin:0 auto;background:var(--surface);padding:2.5rem;border-radius:var(--radius-lg);box-shadow:var(--shadow-md);">

    <div class="breadcrumb">
      <a href="../index.html"><i class="fas fa-home"></i> Home</a>
      <span>/</span>
      <a href="../{cat_page}">{cat_label}</a>
      <span>/</span>
      <span>{short_title}</span>
    </div>

    <div style="text-align:center;margin-bottom:2rem;">
      <p style="font-size:1.1rem;color:var(--primary);font-weight:700;">Short Details of Notification</p>
      <p style="color:var(--text-muted);line-height:1.6;">{description}</p>
    </div>

    {body_html}

  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-about">
          <h3>Sarkari<span>Naukari</span> Infos</h3>
          <p>India&apos;s leading portal for government job updates, results, admit cards, and more.</p>
          <div class="footer-socials">
            <a class="social-link" href="#"><i class="fab fa-facebook-f"></i></a>
            <a class="social-link" href="#"><i class="fab fa-twitter"></i></a>
            <a class="social-link" href="#"><i class="fab fa-telegram-plane"></i></a>
            <a class="social-link" href="#"><i class="fab fa-youtube"></i></a>
          </div>
        </div>
        <div>
          <span class="footer-heading">Quick Links</span>
          <div class="footer-links">
            <a href="../jobs.html">Latest Jobs</a>
            <a href="../results.html">Sarkari Results</a>
            <a href="../admitcard.html">Admit Card</a>
            <a href="../answerkey.html">Answer Keys</a>
          </div>
        </div>
        <div>
          <span class="footer-heading">Resources</span>
          <div class="footer-links">
            <a href="../syllabus.html">Syllabus</a>
            <a href="../admission.html">Admission</a>
            <a href="../important.html">Important</a>
            <a href="../admin/index.html">Admin Panel</a>
          </div>
        </div>
        <div>
          <span class="footer-heading">Legal</span>
          <div class="footer-links">
            <a href="contact-us.html">About Us</a>
            <a href="contact-us.html">Contact Us</a>
            <a href="privacy-policy.html">Privacy Policy</a>
            <a href="#">Disclaimer</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">&copy; 2026 Sarkari Naukari Infos. All Rights Reserved.</div>
    </div>
  </footer>

  <script src="../js/data.js"></script>
  <script src="../js/main.js"></script>
  <script>
    // Search bar (posts folder)
    document.addEventListener('DOMContentLoaded', function() {{
      var btn = document.getElementById('header-search-btn');
      var inp = document.getElementById('header-search-input');
      if(btn) btn.addEventListener('click', function() {{
        var q = inp.value.trim();
        if(q) window.location.href = '../search.html?q=' + encodeURIComponent(q);
      }});
      if(inp) inp.addEventListener('keydown', function(e) {{
        if(e.key==='Enter') btn.click();
      }});
      // Mobile menu
      var toggle = document.querySelector('.menu-toggle');
      var nav = document.querySelector('.main-nav');
      if(toggle) toggle.addEventListener('click', function() {{ nav.classList.toggle('active'); }});
    }});
  </script>
</body>
</html>'''


# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────

def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                enc = resp.headers.get("Content-Encoding", "")
                if enc == "gzip":
                    data = gzip.decompress(data)
                return data.decode("utf-8", "ignore")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1.5)
            else:
                return None


def slugify(title):
    s = title.lower()
    s = re.sub(r'[^a-z0-9\s\-]', '', s)
    s = re.sub(r'[\s\-]+', '-', s).strip('-')
    return s[:80]


def detect_category(url, title=""):
    url_l = url.lower()
    title_l = title.lower()
    for kw, cat in CAT_MAP.items():
        if kw in url_l or kw in title_l:
            return cat
    # fallback heuristics on title
    if any(w in title_l for w in ["result", " cut off", "merit list"]):
        return "results"
    if any(w in title_l for w in ["admit", "hall ticket", "exam city"]):
        return "admitCards"
    if any(w in title_l for w in ["syllabus", "exam pattern", "curriculum"]):
        return "syllabus"
    if any(w in title_l for w in ["answer key", "answer sheet"]):
        return "answerKeys"
    if any(w in title_l for w in ["admission", "counselling", "seat allot"]):
        return "admissions"
    return "latestJobs"


def extract_org(title):
    """Extract organization name from post title."""
    orgs = ["SSC","UPSC","RRB","RBI","IBPS","SBI","NTA","BPSC","UPPSC","RPSC",
            "MPPSC","Railway","Police","Army","Navy","Airforce","DRDO","ISRO",
            "Bihar","UP","Rajasthan","MP","CG","Uttarakhand","Haryana","Punjab"]
    for org in orgs:
        if org.lower() in title.lower():
            return org
    return "Government of India"


def parse_post_page(html, source_url, title):
    """Extract all content from a sarkariresult.com post page."""
    soup = BeautifulSoup(html, "html.parser")

    # ── SEO metadata ──────────────────────────────────────────
    page_title_tag = soup.find("title")
    seo_title = page_title_tag.get_text(strip=True) if page_title_tag else title
    # Replace "Sarkari Result" with our brand
    seo_title = re.sub(r'Sarkari\s*Result', 'Sarkari Naukari Infos', seo_title, flags=re.I)

    meta_desc_tag = soup.find("meta", attrs={"name": re.compile("description", re.I)})
    meta_desc = ""
    if meta_desc_tag:
        meta_desc = meta_desc_tag.get("content", "").strip()
        meta_desc = re.sub(r'Sarkari\s*Result', 'Sarkari Naukari Infos', meta_desc, flags=re.I)
    if not meta_desc:
        meta_desc = f"Complete details of {title} including Important Dates, Application Fee, Vacancy Details, and Apply Online Links – Sarkari Naukari Infos."

    meta_kw_tag = soup.find("meta", attrs={"name": re.compile("keywords", re.I)})
    meta_keywords = ""
    if meta_kw_tag:
        meta_keywords = meta_kw_tag.get("content", "").strip()
    if not meta_keywords:
        meta_keywords = f"{title}, Sarkari Naukari, Government Jobs 2026, Sarkari Result"

    # ── H1 / headings ─────────────────────────────────────────
    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(strip=True) if h1_tag else title
    h1 = re.sub(r'Sarkari\s*Result', 'Sarkari Naukari Infos', h1, flags=re.I)

    # ── Description paragraph ─────────────────────────────────
    desc_p = ""
    for p in soup.find_all("p"):
        txt = p.get_text(strip=True)
        if len(txt) > 60:
            desc_p = re.sub(r'Sarkari\s*Result', 'Sarkari Naukari Infos', txt, flags=re.I)
            break
    if not desc_p:
        desc_p = meta_desc

    # ── Main content area: find post content div ───────────────
    content_div = (
        soup.find("div", id="posterContent") or
        soup.find("div", class_=re.compile(r"post.content|entry.content|article.content", re.I)) or
        soup.find("article") or
        soup.find("div", id=re.compile(r"content|main", re.I))
    )
    if not content_div:
        content_div = soup

    # ── Extract all tables ────────────────────────────────────
    tables = content_div.find_all("table")

    body_parts = []

    # Info-grid: dates + fee (first 2 small tables often)
    info_tables = []
    links_table_html = ""
    main_tables = []

    for tbl in tables:
        txt = tbl.get_text(" ", strip=True).lower()
        tbl_html = str(tbl)
        # Cleanup: replace sarkariresult brand
        tbl_html = re.sub(r'sarkari\s*result\.com', 'sarkarinaukariinfos.net', tbl_html, flags=re.I)
        tbl_html = re.sub(r'Sarkari\s*Result', 'Sarkari Naukari Infos', tbl_html, flags=re.I)

        links = tbl.find_all("a", href=True)
        has_apply = any(w in txt for w in ["apply", "notification", "official", "download", "click"])

        if has_apply and len(links) >= 2:
            # This is the important links table — keep as-is but style it
            soup_t = BeautifulSoup(tbl_html, "html.parser")
            t2 = soup_t.find("table")
            if t2:
                t2["class"] = ["ptable"]
                # Fix external links to open in new tab
                for a in t2.find_all("a", href=True):
                    a["target"] = "_blank"
                    a["rel"] = "noopener"
                tbl_html = str(t2)
            links_table_html = tbl_html
        else:
            # Regular content table
            soup_t = BeautifulSoup(tbl_html, "html.parser")
            t2 = soup_t.find("table")
            if t2:
                t2["class"] = ["ptable"]
                for a in t2.find_all("a", href=True):
                    a["target"] = "_blank"
                tbl_html = str(t2)
            main_tables.append(tbl_html)

    # Collect h2/h3 headings that are inside content
    headings_seen = set()
    for tag in (content_div or soup).find_all(["h2", "h3"]):
        txt = tag.get_text(strip=True)
        if txt and txt not in headings_seen and len(txt) > 4:
            headings_seen.add(txt)

    # Build body HTML
    # First: important dates + fee boxes from first main table if it has those keywords
    dates_html = ""
    fee_html = ""
    remaining_tables = []

    for i, tbl_str in enumerate(main_tables):
        tl = tbl_str.lower()
        if ("application begin" in tl or "last date" in tl or "exam date" in tl) and not dates_html:
            dates_html = tbl_str
        elif ("general" in tl and ("fee" in tl or "₹" in tl or "rs." in tl)) and not fee_html:
            fee_html = tbl_str
        else:
            remaining_tables.append(tbl_str)

    # Build dates+fee grid
    if dates_html or fee_html:
        cols = []
        if dates_html:
            cols.append(f'<div class="post-box" style="margin-bottom:0"><h2 class="hl-b"><i class="fas fa-calendar-check"></i> Important Dates</h2>{dates_html}</div>')
        if fee_html:
            cols.append(f'<div class="post-box" style="margin-bottom:0"><h2 class="hl-b"><i class="fas fa-money-bill-wave"></i> Application Fee</h2>{fee_html}</div>')
        grid_style = "display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:2rem;" if len(cols) == 2 else "margin-bottom:2rem;"
        body_parts.append(f'<div style="{grid_style}">{"".join(cols)}</div>')

    # Remaining content tables
    for tbl_str in remaining_tables:
        body_parts.append(f'<div style="overflow-x:auto;margin-bottom:2rem;">{tbl_str}</div>')

    # Important links at bottom
    if links_table_html:
        body_parts.append(f'''
      <h2 class="hl-m" style="text-align:center;margin-bottom:1.5rem;font-size:1.3rem;">
        Interested Candidates Can Read the Full Notification Before Apply Online
      </h2>
      <div style="overflow-x:auto;">
        {links_table_html}
        <table class="ptable" style="margin-top:0;border-top:none;">
          <tbody>
            <tr>
              <td class="hl-g" colspan="2" style="font-size:1.2rem;background:rgba(25,135,84,.05);padding:1rem;">
                <i class="fab fa-telegram"></i> Join Our Telegram for Instant Updates
              </td>
            </tr>
            <tr>
              <td>Join Telegram Channel</td>
              <td><a href="https://t.me/sarkarinaukariinfos" target="_blank" style="color:#0088cc;"><i class="fab fa-telegram"></i> Click Here</a></td>
            </tr>
            <tr>
              <td>Download Android App</td>
              <td><a href="https://play.google.com/store" target="_blank"><i class="fab fa-android" style="color:#3ddc84"></i> Google Play</a></td>
            </tr>
          </tbody>
        </table>
      </div>''')
    else:
        # Generic links table
        body_parts.append(f'''
      <div style="overflow-x:auto;margin-top:2rem;">
        <table class="ptable">
          <tbody>
            <tr><td class="hl-g" colspan="2" style="font-size:1.2rem;background:rgba(25,135,84,.05);padding:1rem;">Some Useful Important Links</td></tr>
            <tr><td class="hl-m" style="font-weight:bold;">Official Website</td>
                <td><a href="{source_url}" target="_blank" rel="noopener"><i class="fas fa-globe"></i> Click Here</a></td></tr>
            <tr><td class="hl-m" style="font-weight:bold;">Join Telegram</td>
                <td><a href="https://t.me/sarkarinaukariinfos" target="_blank" style="color:#0088cc;"><i class="fab fa-telegram"></i> Click Here</a></td></tr>
          </tbody>
        </table>
      </div>''')

    return {
        "seo_title": seo_title,
        "meta_desc": meta_desc,
        "meta_keywords": meta_keywords,
        "h1": h1,
        "description": desc_p,
        "body_html": "\n".join(body_parts),
    }


def generate_html(title, cat, source_url, parsed):
    cat_labels = {
        "latestJobs": "Latest Jobs", "results": "Results", "admitCards": "Admit Card",
        "answerKeys": "Answer Key", "syllabus": "Syllabus", "admissions": "Admission",
        "important": "Important"
    }
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": parsed["h1"],
        "description": parsed["meta_desc"],
        "author": {"@type": "Organization", "name": "Sarkari Naukari Infos"},
        "publisher": {"@type": "Organization", "name": "Sarkari Naukari Infos"},
        "datePublished": "2026-03-07",
        "url": f"https://sarkarinaukariinfos.net/posts/{slugify(title)}.html"
    })
    return HTML_TEMPLATE.format(
        seo_title=parsed["seo_title"],
        meta_desc=parsed["meta_desc"],
        meta_keywords=parsed["meta_keywords"],
        canonical=f"https://sarkarinaukariinfos.net/posts/{slugify(title)}.html",
        schema=schema,
        h1=parsed["h1"],
        org=extract_org(title),
        cat_label=cat_labels.get(cat, "Government Jobs"),
        cat_page=CAT_PAGE_MAP.get(cat, "jobs.html"),
        short_title=title[:60],
        description=parsed["description"],
        body_html=parsed["body_html"],
    )


# ─── MAIN CRAWL LOGIC ─────────────────────────────────────────────────────────

def crawl_source_links():
    """Collect all post URLs from the sarkariresult.com homepage + section pages."""
    print("🌐 Fetching homepage...")
    html = fetch(SOURCE)
    if not html:
        print("❌ Failed to fetch homepage.")
        return []

    soup = BeautifulSoup(html, "html.parser")

    # Find ALL links that look like individual post pages
    seen = set()
    items = []  # (url, title, category)

    # ── Parse link tables on homepage ────────────────────────
    for a in soup.find_all("a", href=True):
        href = a["href"]
        title = a.get_text(strip=True)
        if not title or len(title) < 6:
            continue
        # Full URL
        if href.startswith("/"):
            href = "https://www.sarkariresult.com" + href
        elif not href.startswith("http"):
            continue
        # Only sarkariresult.com links that are post pages
        if "sarkariresult.com" not in href:
            continue
        if href in seen:
            continue
        # Exclude pagination/about pages
        skip_kws = ["facebook", "twitter", "youtube", "telegram", "instagram",
                    "play.google", "apps.apple", "privacy", "about", "contact",
                    "disclaimer", "whatsapp", "sitemap"]
        if any(kw in href.lower() for kw in skip_kws):
            continue
        # Must look like a post URL (has a path segment beyond just /)
        path = urlparse(href).path
        if path in ["/", "", "/index.html"]:
            continue

        cat = detect_category(href, title)
        seen.add(href)
        items.append({"url": href, "title": title, "cat": cat})

    print(f"✅ Found {len(items)} links on homepage.")

    # ── Fetch category listing pages for more posts ────────────
    cat_pages = [
        "https://www.sarkariresult.com/latestjob/",
        "https://www.sarkariresult.com/result/",
        "https://www.sarkariresult.com/admit/",
        "https://www.sarkariresult.com/answerkey/",
        "https://www.sarkariresult.com/syllabus/",
        "https://www.sarkariresult.com/admission/",
    ]

    for cat_url in cat_pages:
        print(f"  📂 Fetching category: {cat_url}")
        chtml = fetch(cat_url)
        if not chtml:
            continue
        csoup = BeautifulSoup(chtml, "html.parser")
        for a in csoup.find_all("a", href=True):
            href = a["href"]
            title = a.get_text(strip=True)
            if not title or len(title) < 6:
                continue
            if href.startswith("/"):
                href = "https://www.sarkariresult.com" + href
            elif not href.startswith("http"):
                href = urljoin(cat_url, href)
            if "sarkariresult.com" not in href:
                continue
            if href in seen:
                continue
            path = urlparse(href).path
            if path in ["/", "", "/index.html"]:
                continue
            cat = detect_category(href, title)
            seen.add(href)
            items.append({"url": href, "title": title, "cat": cat})
        time.sleep(DELAY)

    print(f"✅ Total post URLs collected: {len(items)}")
    return items[:MAX_POSTS]


def process_one(item):
    """Fetch, parse, and write one post page. Returns data-js entry or None."""
    url   = item["url"]
    title = item["title"]
    cat   = item["cat"]

    slug     = slugify(title)
    filename = slug + ".html"
    filepath = os.path.join(POSTS_DIR, filename)
    rel_link = f"posts/{filename}"

    # Skip if file already exists and is large (has content)
    if SKIP_SMALL and os.path.exists(filepath) and os.path.getsize(filepath) > 8000:
        return {"title": title, "link": rel_link, "cat": cat, "skipped": True}

    time.sleep(DELAY)
    html = fetch(url)
    if not html:
        return None

    try:
        parsed = parse_post_page(html, url, title)
        final_html = generate_html(title, cat, url, parsed)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_html)

        return {"title": title, "link": rel_link, "cat": cat, "seo_title": parsed["seo_title"]}
    except Exception as e:
        print(f"  ⚠️  Error processing [{title}]: {e}")
        return None


# ─── DATA.JS UPDATER ──────────────────────────────────────────────────────────

def update_data_js(all_results):
    """Merge newly scraped posts into data.js."""
    with open(DATA_JS, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse existing data
    match = re.search(r"const siteData\s*=\s*(\{.*?\});", content, re.DOTALL)
    if not match:
        print("❌ Cannot parse data.js")
        return 0

    existing = json.loads(match.group(1))

    # Build lookup of existing links to avoid duplicates
    existing_links = set()
    for cat_items in existing.values():
        if isinstance(cat_items, list):
            for it in cat_items:
                existing_links.add(it.get("link", ""))

    added = 0
    for rec in all_results:
        if not rec or rec.get("skipped"):
            continue
        cat = rec["cat"]
        link = rec["link"]
        if link in existing_links:
            continue
        if cat not in existing:
            existing[cat] = []
        existing[cat].insert(0, {"title": rec["title"], "link": link, "ts": int("20260308")})
        # Always keep newest first
        existing[cat].sort(key=lambda x: x.get('ts',0), reverse=True)
        existing_links.add(link)
        added += 1

    # Write back
    new_json = json.dumps(existing, ensure_ascii=False, indent=2)
    # Rebuild data.js preserving the localStorage merge code
    new_content = re.sub(
        r"const siteData\s*=\s*\{.*?\};",
        f"const siteData = {new_json};",
        content,
        count=1,
        flags=re.DOTALL
    )
    with open(DATA_JS, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ Added {added} new entries to data.js")
    return added


# ─── CATEGORY PAGE PAGER ──────────────────────────────────────────────────────

CATEGORY_META = {
    "latestJobs":  ("Latest Government Jobs 2026", "jobs.html",      "fas fa-briefcase",    "Apply online for the latest government job vacancies. Updated daily."),
    "results":     ("Sarkari Result 2026",          "results.html",   "fas fa-trophy",       "Check latest government exam results for SSC, Railway, UPSC, Banking, Police."),
    "admitCards":  ("Admit Card 2026",              "admitcard.html", "fas fa-id-card",      "Download hall tickets and admit cards for government examinations."),
    "answerKeys":  ("Answer Key 2026",              "answerkey.html", "fas fa-key",          "Download official answer keys. Raise objections and check your score."),
    "syllabus":    ("Syllabus 2026",                "syllabus.html",  "fas fa-book-open",    "Download subject-wise syllabus and exam patterns."),
    "admissions":  ("Admission 2026",               "admission.html", "fas fa-graduation-cap","Apply for college and university admissions – NEET, CUET, JEE and more."),
    "important":   ("Important Links 2026",         "important.html", "fas fa-link",         "Access important government portals and certificate verification links."),
}

def generate_category_page_with_pagination(cat_key, items, per_page=50):
    """Regenerate a category page with paginated listing."""
    meta = CATEGORY_META.get(cat_key, ("Government Jobs", "jobs.html", "fas fa-list", ""))
    h1, filename, icon, hero_desc = meta

    # Simple: dump all items into one page with JS pagination
    items_json = json.dumps([{"t": it["title"], "l": it["link"]} for it in items], ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{h1} – Sarkari Naukari Infos</title>
  <meta name="description" content="{hero_desc} Sarkari Naukari Infos.">
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8244601197032455" crossorigin="anonymous"></script>
</head>
<body>
  <div class="header-top">Sarkari Naukari Infos – Your Trusted Source for Government Job Updates</div>
  <header class="site-header">
    <div class="container nav-container">
      <a class="logo" href="index.html">
        <div class="logo-main">Sarkari<span>Naukari</span></div>
        <div class="logo-sub">Infos .Net</div>
      </a>
      <button class="menu-toggle"><i class="fas fa-bars"></i></button>
      <nav class="main-nav">
        <a class="nav-link" href="index.html">Home</a>
        <a class="nav-link" href="jobs.html">Latest Jobs</a>
        <a class="nav-link" href="results.html">Results</a>
        <a class="nav-link" href="admitcard.html">Admit Card</a>
        <a class="nav-link" href="answerkey.html">Answer Key</a>
        <a class="nav-link" href="syllabus.html">Syllabus</a>
        <a class="nav-link" href="admission.html">Admission</a>
      </nav>
      <div class="header-search">
        <input id="header-search-input" type="text" placeholder="Search exams, jobs..." aria-label="Search">
        <button id="header-search-btn"><i class="fas fa-search"></i> Search</button>
      </div>
    </div>
  </header>

  <div class="category-hero">
    <div class="container">
      <h1><i class="{icon}"></i> {h1}</h1>
      <p>{hero_desc}</p>
    </div>
  </div>

  <main class="container animate-fade-in">
    <div class="breadcrumb">
      <a href="index.html"><i class="fas fa-home"></i> Home</a>
      <span>/</span><span>{h1}</span>
    </div>

    <div class="category-card">
      <div id="cat-search-bar" style="margin-bottom:1.5rem;display:flex;gap:.5rem;">
        <input id="cat-filter" type="text" placeholder="Filter {h1}..." style="flex:1;padding:.65rem 1rem;border:1.5px solid #e2e8f0;border-radius:8px;font-size:.95rem;outline:none;">
        <span id="count-badge" style="align-self:center;font-size:.85rem;color:var(--text-muted);white-space:nowrap;"></span>
      </div>
      <div id="list-container"></div>
      <!-- Pagination -->
      <div id="pagination" style="display:flex;gap:.5rem;justify-content:center;flex-wrap:wrap;margin-top:1.5rem;"></div>
      <div class="category-count" id="page-info"></div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-about">
          <h3>Sarkari<span>Naukari</span> Infos</h3>
          <p>India's leading portal for government job updates.</p>
          <div class="footer-socials">
            <a class="social-link" href="#"><i class="fab fa-telegram-plane"></i></a>
            <a class="social-link" href="#"><i class="fab fa-facebook-f"></i></a>
            <a class="social-link" href="#"><i class="fab fa-youtube"></i></a>
          </div>
        </div>
        <div><span class="footer-heading">Quick Links</span>
          <div class="footer-links">
            <a href="jobs.html">Latest Jobs</a>
            <a href="results.html">Results</a>
            <a href="admitcard.html">Admit Card</a>
            <a href="answerkey.html">Answer Keys</a>
          </div>
        </div>
        <div><span class="footer-heading">More</span>
          <div class="footer-links">
            <a href="syllabus.html">Syllabus</a>
            <a href="admission.html">Admission</a>
            <a href="search.html">Search</a>
            <a href="admin/index.html">Admin</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">&copy; 2026 Sarkari Naukari Infos. All Rights Reserved.</div>
    </div>
  </footer>

  <script src="js/data.js"></script>
  <script src="js/main.js"></script>
  <script>
  (function() {{
    // Static items from scraper + dynamic from data.js
    var staticItems = {items_json};

    // Merge with data.js at runtime
    var allItems = [];
    var seen = {{}};
    staticItems.forEach(function(it) {{ if(!seen[it.l]){{ seen[it.l]=1; allItems.push(it); }} }});
    (siteData['{cat_key}']||[]).forEach(function(it) {{
      if(!seen[it.link]){{ seen[it.link]=1; allItems.push({{t:it.title,l:it.link}}); }}
    }});

    var filtered = allItems.slice();
    var PER_PAGE = {per_page};
    var currentPage = 1;

    function renderPage() {{
      var start = (currentPage-1)*PER_PAGE;
      var end   = start + PER_PAGE;
      var slice = filtered.slice(start, end);
      var html  = slice.map(function(it){{
        return '<a class="search-result-item" href="' + it.l + '">' +
               '<span class="result-title">' + it.t + '</span>' +
               '<i class="fas fa-chevron-right" style="color:var(--text-light)"></i></a>';
      }}).join('');
      document.getElementById('list-container').innerHTML = html || '<p style="text-align:center;color:var(--text-muted);padding:2rem">No results found.</p>';
      document.getElementById('page-info').textContent = 'Showing ' + (start+1) + '–' + Math.min(end,filtered.length) + ' of ' + filtered.length + ' entries';
      renderPagination();
    }}

    function renderPagination() {{
      var total = Math.ceil(filtered.length / PER_PAGE);
      var pg = document.getElementById('pagination');
      if(total <= 1){{ pg.innerHTML=''; return; }}
      var html = '';
      var btnStyle = 'padding:.4rem .85rem;border-radius:6px;border:1.5px solid #e2e8f0;background:var(--surface);cursor:pointer;font-size:.9rem;transition:all .2s;';
      var activeStyle = 'background:var(--primary);color:white;border-color:var(--primary);';
      if(currentPage > 1) html += '<button style="' + btnStyle + '" onclick="goPage(' + (currentPage-1) + ')">&#8249; Prev</button>';
      for(var i=Math.max(1,currentPage-2); i<=Math.min(total,currentPage+2); i++){{
        html += '<button style="' + btnStyle + (i===currentPage ? activeStyle : '') + '" onclick="goPage('+i+')">'+i+'</button>';
      }}
      if(currentPage < total) html += '<button style="' + btnStyle + '" onclick="goPage(' + (currentPage+1) + ')">Next &#8250;</button>';
      pg.innerHTML = html;
    }}

    window.goPage = function(n) {{ currentPage=n; renderPage(); window.scrollTo(0,300); }};

    document.getElementById('cat-filter').addEventListener('input', function() {{
      var q = this.value.toLowerCase().trim();
      filtered = q ? allItems.filter(function(it){{ return it.t.toLowerCase().includes(q); }}) : allItems.slice();
      currentPage = 1;
      document.getElementById('count-badge').textContent = q ? filtered.length + ' found' : '';
      renderPage();
    }});

    // Search bar
    document.getElementById('header-search-btn').addEventListener('click', function() {{
      var q = document.getElementById('header-search-input').value.trim();
      if(q) window.location.href = 'search.html?q=' + encodeURIComponent(q);
    }});
    document.getElementById('header-search-input').addEventListener('keydown', function(e) {{
      if(e.key==='Enter') document.getElementById('header-search-btn').click();
    }});

    // Mobile menu
    var toggle = document.querySelector('.menu-toggle');
    var nav = document.querySelector('.main-nav');
    if(toggle) toggle.addEventListener('click', function() {{ nav.classList.toggle('active'); }});

    renderPage();
  }})();
  </script>
</body>
</html>'''
    return html


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

def main():
    os.makedirs(POSTS_DIR, exist_ok=True)
    print("="*60)
    print("  SARKARI NAUKARI MEGA SCRAPER")
    print("="*60)

    # Step 1: Collect links
    items = crawl_source_links()
    if not items:
        print("No items found. Exiting.")
        return

    # Step 2: Scrape each post concurrently
    print(f"\n📥 Scraping {len(items)} posts with {MAX_WORKERS} workers...")
    results = []
    done = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_map = {executor.submit(process_one, it): it for it in items}
        for future in concurrent.futures.as_completed(future_map):
            done += 1
            result = future.result()
            if result:
                results.append(result)
                status = "⏭ SKIP" if result.get("skipped") else "✅"
                print(f"  [{done:3d}/{len(items)}] {status} {result['title'][:65]}")
            else:
                item = future_map[future]
                print(f"  [{done:3d}/{len(items)}] ❌ FAILED: {item['title'][:65]}")

    print(f"\n✅ Scraped {len([r for r in results if r and not r.get('skipped')])} posts.")

    # Step 3: Update data.js
    print("\n📝 Updating data.js...")
    added = update_data_js(results)

    # Step 4: Regenerate category pages with pagination
    print("\n🔄 Regenerating category pages with pagination...")
    with open(DATA_JS, "r", encoding="utf-8") as f:
        data_content = f.read()
    match = re.search(r"const siteData\s*=\s*(\{.*?\});", data_content, re.DOTALL)
    if match:
        site_data = json.loads(match.group(1))
        for cat_key, cat_items in site_data.items():
            if cat_key not in CATEGORY_META:
                continue
            _, filename, _, _ = CATEGORY_META[cat_key]
            page_html = generate_category_page_with_pagination(cat_key, cat_items)
            page_path = os.path.join(BASE_DIR, filename)
            with open(page_path, "w", encoding="utf-8", newline="") as f:
                f.write(page_html)
            print(f"  ✅ {filename} ({len(cat_items)} items)")

    print("\n" + "="*60)
    print(f"  DONE! {len(results)} posts generated, {added} new entries in data.js")
    print("  Open index.html in your browser to see the updated site.")
    print("="*60)


if __name__ == "__main__":
    main()
