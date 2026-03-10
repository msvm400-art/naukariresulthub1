#!/usr/bin/env python3
"""Generate all 7 category pages for sarkarinaukari site."""

import os

BASE = r"c:\Users\ALOK\Desktop\sarkarinaukari"

CATEGORIES = [
    {
        "file": "results.html",
        "title": "Sarkari Result 2026 – Latest Government Exam Results",
        "h1": "Sarkari Result 2026",
        "description": "Check latest Sarkari Result 2026 for SSC, Railway, UPSC, Bank, Police and all government exam results.",
        "keywords": "Sarkari Result 2026, Government Exam Result, SSC Result 2026, Railway Result 2026, UPSC Result, Bank Result 2026",
        "icon": "fas fa-trophy",
        "hero_desc": "Check the latest government exam results for SSC, Railway, UPSC, Banking, Police, and State exams.",
        "cat_key": "results",
        "nav_active": "results.html",
        "color": "secondary"
    },
    {
        "file": "admitcard.html",
        "title": "Admit Card 2026 – Download Sarkari Exam Hall Ticket",
        "h1": "Admit Card 2026",
        "description": "Download Sarkari Admit Card 2026 for SSC, Railway, UPSC, IBPS, Police and all government exams.",
        "keywords": "Admit Card 2026, Hall Ticket Download, Sarkari Exam Admit Card, SSC Admit Card, Railway Admit Card 2026",
        "icon": "fas fa-id-card",
        "hero_desc": "Download hall tickets and admit cards for government examinations. Check your exam city and schedule.",
        "cat_key": "admitCards",
        "nav_active": "admitcard.html",
        "color": "success"
    },
    {
        "file": "jobs.html",
        "title": "Latest Government Jobs 2026 – Sarkari Naukari Vacancy",
        "h1": "Latest Government Jobs 2026",
        "description": "Apply online for the latest Sarkari Naukari 2026. Get free job alerts for SSC, Railway, Bank, Police, UPSC, and State Govt jobs.",
        "keywords": "Latest Government Jobs 2026, Sarkari Naukari 2026, Government Job Vacancy, Free Job Alert, Sarkari Job 2026",
        "icon": "fas fa-briefcase",
        "hero_desc": "Apply online for the latest government job vacancies. Updated daily with central and state government notifications.",
        "cat_key": "latestJobs",
        "nav_active": "jobs.html",
        "color": "primary"
    },
    {
        "file": "answerkey.html",
        "title": "Answer Key 2026 – Download Sarkari Exam Answer Keys",
        "h1": "Answer Key 2026",
        "description": "Download official Answer Keys for SSC, Railway, UPSC, IBPS, Police and all government exams 2026.",
        "keywords": "Answer Key 2026, Official Answer Key, SSC Answer Key, Railway Answer Key, UPSC Answer Key",
        "icon": "fas fa-key",
        "hero_desc": "Download official answer keys for government exams. Raise objections and check your score.",
        "cat_key": "answerKeys",
        "nav_active": "answerkey.html",
        "color": "primary"
    },
    {
        "file": "syllabus.html",
        "title": "Syllabus 2026 – Government Exam Syllabus & Exam Pattern",
        "h1": "Syllabus 2026",
        "description": "Download detailed syllabus and exam pattern for SSC, Railway, UPSC, Bank, Police and all Sarkari exams 2026.",
        "keywords": "Syllabus 2026, Exam Pattern, SSC Syllabus 2026, Railway Exam Syllabus, UPSC Syllabus 2026",
        "icon": "fas fa-book-open",
        "hero_desc": "Download subject-wise syllabus and exam patterns to plan your preparation effectively.",
        "cat_key": "syllabus",
        "nav_active": "syllabus.html",
        "color": "primary"
    },
    {
        "file": "admission.html",
        "title": "Admission 2026 – Online Form for College & University Admissions",
        "h1": "Admission 2026",
        "description": "Apply online for college and university admissions 2026. Get updates on NEET, CUET, JEE, State entrance exams.",
        "keywords": "Admission 2026, NEET 2026, CUET 2026, College Admission Form, University Admission 2026",
        "icon": "fas fa-graduation-cap",
        "hero_desc": "Apply for medical, engineering, and other college/university admissions. NEET, CUET, JEE and more.",
        "cat_key": "admissions",
        "nav_active": "admission.html",
        "color": "primary"
    },
    {
        "file": "important.html",
        "title": "Important Links 2026 – Certificate Verification & Key Updates",
        "h1": "Important Links 2026",
        "description": "Get important links including certificate verification, voter ID, Aadhaar linking, scholarships, and more.",
        "keywords": "Important Links 2026, Certificate Verification, Voter ID Form, Aadhaar PAN Link, Scholarship Form",
        "icon": "fas fa-link",
        "hero_desc": "Access important government portals, certificate verification links, and essential online services.",
        "cat_key": "important",
        "nav_active": "important.html",
        "color": "primary"
    },
]

NAV_LINKS = [
    ("index.html", "Home"),
    ("jobs.html", "Latest Jobs"),
    ("results.html", "Results"),
    ("admitcard.html", "Admit Card"),
    ("answerkey.html", "Answer Key"),
    ("syllabus.html", "Syllabus"),
    ("admission.html", "Admission"),
]

FOOTER = """
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
        <div>
          <span class="footer-heading">Quick Links</span>
          <div class="footer-links">
            <a href="jobs.html">Latest Jobs</a>
            <a href="results.html">Sarkari Results</a>
            <a href="admitcard.html">Admit Card</a>
            <a href="answerkey.html">Answer Keys</a>
          </div>
        </div>
        <div>
          <span class="footer-heading">Resources</span>
          <div class="footer-links">
            <a href="syllabus.html">Syllabus</a>
            <a href="admission.html">Admission</a>
            <a href="important.html">Important</a>
            <a href="admin/index.html">Admin Panel</a>
          </div>
        </div>
        <div>
          <span class="footer-heading">Legal</span>
          <div class="footer-links">
            <a href="posts/contact-us.html">About Us</a>
            <a href="posts/contact-us.html">Contact Us</a>
            <a href="posts/privacy-policy.html">Privacy Policy</a>
            <a href="#">Disclaimer</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">&copy; 2026 Sarkari Naukari Infos. All Rights Reserved.</div>
    </div>
  </footer>
"""

def generate_nav(active_file):
    links = []
    for href, label in NAV_LINKS:
        cls = "nav-link active" if href == active_file else "nav-link"
        links.append(f'        <a class="{cls}" href="{href}">{label}</a>')
    return "\n".join(links)


def generate_page(cat):
    nav = generate_nav(cat["nav_active"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{cat["title"]}</title>
  <meta name="description" content="{cat["description"]}">
  <meta name="keywords" content="{cat["keywords"]}">
  <link rel="canonical" href="{cat["file"]}">
  <meta property="og:title" content="{cat["title"]}">
  <meta property="og:description" content="{cat["description"]}">
  <meta property="og:type" content="website">
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
      <button class="menu-toggle" aria-label="Toggle menu"><i class="fas fa-bars"></i></button>
      <nav class="main-nav">
{nav}
      </nav>
      <div class="header-search">
        <input id="header-search-input" type="text" placeholder="Search exams, jobs..." aria-label="Search">
        <button id="header-search-btn"><i class="fas fa-search"></i> Search</button>
      </div>
    </div>
  </header>

  <!-- Category Hero -->
  <div class="category-hero">
    <div class="container">
      <h1><i class="{cat["icon"]}"></i> {cat["h1"]}</h1>
      <p>{cat["hero_desc"]}</p>
    </div>
  </div>

  <main class="container animate-fade-in">
    <div class="breadcrumb">
      <a href="index.html"><i class="fas fa-home"></i> Home</a>
      <span>/</span>
      <span>{cat["h1"]}</span>
    </div>
    <div class="category-card">
      <div id="category-list" data-category="{cat["cat_key"]}" class="job-list" style="max-height:none; overflow:visible;"></div>
      <div class="category-count" id="cat-count"></div>
    </div>
  </main>

  {FOOTER}

  <script src="js/data.js"></script>
  <script src="js/postData.js"></script>
  <script src="js/main.js"></script>
  <script>
    document.addEventListener('DOMContentLoaded', () => {{
      const el = document.getElementById('category-list');
      if (el) {{
        const count = el.querySelectorAll('.job-link').length;
        document.getElementById('cat-count').textContent = `Showing ${{count}} total entries`;
      }}
    }});
  </script>
</body>
</html>
"""


for cat in CATEGORIES:
    path = os.path.join(BASE, cat["file"])
    content = generate_page(cat)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Generated: {cat['file']}")

print("\n🎉 All 7 category pages generated successfully!")
