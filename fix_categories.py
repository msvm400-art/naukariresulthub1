#!/usr/bin/env python3
"""
fix_categories.py — Recategorizes data.js entries more accurately
using title-based heuristics and removes duplicates.
Also re-runs category page generation with paginated lists.
"""
import os, json, re

BASE_DIR = r"C:\Users\ALOK\Desktop\sarkarinaukari"
DATA_JS  = os.path.join(BASE_DIR, "js", "data.js")

CAT_LABELS = {
    "latestJobs": "Latest Jobs", "results": "Results", "admitCards": "Admit Card",
    "answerKeys": "Answer Key", "syllabus": "Syllabus", "admissions": "Admission", "important": "Important"
}
CAT_PAGE_MAP = {
    "latestJobs": "jobs.html", "results": "results.html", "admitCards": "admitcard.html",
    "answerKeys": "answerkey.html", "syllabus": "syllabus.html", "admissions": "admission.html", "important": "important.html"
}
CAT_ICONS = {
    "latestJobs": "fas fa-briefcase", "results": "fas fa-trophy", "admitCards": "fas fa-id-card",
    "answerKeys": "fas fa-key", "syllabus": "fas fa-book-open", "admissions": "fas fa-graduation-cap", "important": "fas fa-link"
}
CAT_HERO  = {
    "latestJobs": "Apply online for the latest government job vacancies. Updated daily with central and state government notifications.",
    "results":    "Check the latest government exam results for SSC, Railway, UPSC, Banking, Police, and State exams.",
    "admitCards": "Download hall tickets and admit cards for government examinations. Check your exam city and schedule.",
    "answerKeys": "Download official answer keys for government exams. Raise objections and check your score.",
    "syllabus":   "Download subject-wise syllabus and exam patterns to plan your preparation effectively.",
    "admissions": "Apply for medical, engineering, and other college/university admissions. NEET, CUET, JEE and more.",
    "important":  "Access important government portals, certificate verification links, and essential online services.",
}

def classify(title, current_cat):
    t = title.lower()
    # Hard rules take priority
    if any(w in t for w in ["admit card","hall ticket","exam city","call letter","roll number slip"]):
        return "admitCards"
    if any(w in t for w in ["answer key","answer sheet","official key","provisional key"]):
        return "answerKeys"
    if any(w in t for w in ["syllabus","exam pattern","curriculum","selection process","paper pattern"]):
        return "syllabus"
    if any(w in t for w in ["admission","counselling","seat allotment","cuet","neet","jee","merit list admission"]):
        return "admissions"
    if any(w in t for w in ["certificate","voter id","aadhaar","pan card","caste","scholarship form","domicile"]):
        return "important"
    if any(w in t for w in ["result","merit list","scorecard","cut off","final answer","selected candidates"]):
        return "results"
    if any(w in t for w in ["online form","apply online","recruitment","vacancy","notification","advt","jobs","naukri",
                             "bharti","bharati","recruitment","registration","otr","application"]):
        return "latestJobs"
    # If still ambiguous, keep existing unless it was "results" with no result keyword
    if current_cat == "results" and "result" not in t and "merit" not in t:
        return "latestJobs"
    return current_cat

# Load data.js
with open(DATA_JS, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r"const siteData\s*=\s*(\{.*?\});", content, re.DOTALL)
if not match:
    print("❌ Cannot parse data.js"); exit()

data = json.loads(match.group(1))

# Reclassify and deduplicate
new_data = {k: [] for k in ["latestJobs","results","admitCards","answerKeys","syllabus","admissions","important"]}
seen_links = set()
moved = 0

for cat, items in data.items():
    if cat not in new_data or not isinstance(items, list):
        continue
    for it in items:
        link = it.get("link","")
        title= it.get("title","")
        if link in seen_links or not title:
            continue
        seen_links.add(link)
        new_cat = classify(title, cat)
        if new_cat != cat:
            moved += 1
        new_data[new_cat].append({"title": title, "link": link})

# Print stats
total = sum(len(v) for v in new_data.values())
print("Reclassification results:")
for k,v in new_data.items():
    print(f"  {k}: {len(v)}")
print(f"  TOTAL: {total}, moved: {moved}")

# Write back
new_json = json.dumps(new_data, ensure_ascii=False, indent=2)
new_content = re.sub(
    r"const siteData\s*=\s*\{.*?\};",
    f"const siteData = {new_json};",
    content, count=1, flags=re.DOTALL
)
with open(DATA_JS, "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ data.js updated with reclassified categories\n")

# ── Regenerate category pages with pagination ─────────────────────────────────
PER_PAGE = 50

for cat_key, items in new_data.items():
    h1       = {"latestJobs":"Latest Government Jobs 2026","results":"Sarkari Result 2026",
                "admitCards":"Admit Card 2026","answerKeys":"Answer Key 2026",
                "syllabus":"Syllabus 2026","admissions":"Admission 2026","important":"Important Links 2026"}.get(cat_key, "Government Jobs")
    filename = CAT_PAGE_MAP[cat_key]
    icon     = CAT_ICONS[cat_key]
    hero_desc= CAT_HERO[cat_key]

    items_json = json.dumps([{"t": it["title"], "l": it["link"]} for it in items], ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{h1} – Sarkari Naukari Infos</title>
  <meta name="description" content="{hero_desc} Sarkari Naukari Infos – Total {len(items)} posts.">
  <meta name="keywords" content="{h1}, Sarkari Naukari, Government Jobs 2026">
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8244601197032455" crossorigin="anonymous"></script>
</head>
<body>
  <div class="header-top">Sarkari Naukari Infos – Your Trusted Source for Government Job Updates</div>
  <header class="site-header">
    <div class="container nav-container">
      <a class="logo" href="index.html"><div class="logo-main">Sarkari<span>Naukari</span></div><div class="logo-sub">Infos .Net</div></a>
      <button class="menu-toggle" aria-label="Toggle menu"><i class="fas fa-bars"></i></button>
      <nav class="main-nav">
        <a class="nav-link" href="index.html">Home</a>
        <a class="nav-link{"  active" if filename=="jobs.html" else ""}" href="jobs.html">Latest Jobs</a>
        <a class="nav-link{"  active" if filename=="results.html" else ""}" href="results.html">Results</a>
        <a class="nav-link{"  active" if filename=="admitcard.html" else ""}" href="admitcard.html">Admit Card</a>
        <a class="nav-link{"  active" if filename=="answerkey.html" else ""}" href="answerkey.html">Answer Key</a>
        <a class="nav-link{"  active" if filename=="syllabus.html" else ""}" href="syllabus.html">Syllabus</a>
        <a class="nav-link{"  active" if filename=="admission.html" else ""}" href="admission.html">Admission</a>
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
      <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap;">
        <input id="cat-filter" type="text" placeholder="Filter {h1.lower()}..."
               style="flex:1;min-width:200px;padding:.65rem 1rem;border:1.5px solid #e2e8f0;border-radius:8px;font-size:.95rem;outline:none;transition:border-color .2s"
               onfocus="this.style.borderColor='#2563eb'" onblur="this.style.borderColor='#e2e8f0'">
        <span id="count-badge" style="font-size:.85rem;color:var(--text-muted);"></span>
      </div>
      <div id="list-container"></div>
      <div id="pagination" style="display:flex;gap:.5rem;justify-content:center;flex-wrap:wrap;margin-top:1.5rem;padding-top:1rem;border-top:1px solid #e2e8f0;"></div>
      <div class="category-count" id="page-info"></div>
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
            <a href="posts/contact-us.html">About Us</a>
            <a href="posts/privacy-policy.html">Privacy Policy</a>
            <a href="#">Disclaimer</a>
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
    var allItems = {items_json};
    var PER_PAGE = {PER_PAGE};
    var filtered = allItems.slice();
    var currentPage = 1;

    function renderPage() {{
      var start = (currentPage-1)*PER_PAGE, end = start+PER_PAGE;
      var slice = filtered.slice(start, end);
      var html = slice.map(function(it){{
        return '<a class="search-result-item" href="'+it.l+'" style="text-decoration:none">'+
               '<span class="result-title">'+it.t+'</span>'+
               '<i class="fas fa-chevron-right" style="color:var(--text-light);font-size:.8rem"></i></a>';
      }}).join('');
      document.getElementById('list-container').innerHTML = html || '<p style="text-align:center;color:var(--text-muted);padding:3rem">No results found.</p>';
      document.getElementById('page-info').textContent = 'Showing '+(start+1)+'–'+Math.min(end,filtered.length)+' of '+filtered.length+' entries';
      renderPagination();
      window.scrollTo(0,0);
    }}

    function renderPagination() {{
      var total = Math.ceil(filtered.length/PER_PAGE);
      var pg = document.getElementById('pagination');
      if(total<=1){{pg.innerHTML='';return;}}
      var b = 'display:inline-flex;align-items:center;padding:.4rem .85rem;border-radius:6px;border:1.5px solid #e2e8f0;background:var(--surface);cursor:pointer;font-size:.9rem;transition:all .2s;font-family:inherit;';
      var ba = 'background:var(--primary);color:white;border-color:var(--primary);';
      var html = '';
      if(currentPage>1) html += '<button style="'+b+'" onclick="goPage('+(currentPage-1)+')">&#8249; Prev</button>';
      var start = Math.max(1,currentPage-3), end = Math.min(total,currentPage+3);
      if(start>1) html += '<button style="'+b+'" onclick="goPage(1)">1</button>'+(start>2?'<span style="padding:.4rem">…</span>':'');
      for(var i=start;i<=end;i++) html += '<button style="'+b+(i===currentPage?ba:'')+'" onclick="goPage('+i+')">'+i+'</button>';
      if(end<total) html += (end<total-1?'<span style="padding:.4rem">…</span>':'')+'<button style="'+b+'" onclick="goPage('+total+')">'+total+'</button>';
      if(currentPage<total) html += '<button style="'+b+'" onclick="goPage('+(currentPage+1)+')">Next &#8250;</button>';
      pg.innerHTML = html;
    }}

    window.goPage = function(n) {{ currentPage=n; renderPage(); }};

    document.getElementById('cat-filter').addEventListener('input', function() {{
      var q = this.value.toLowerCase().trim();
      filtered = q ? allItems.filter(function(it){{return it.t.toLowerCase().includes(q);}}) : allItems.slice();
      document.getElementById('count-badge').textContent = q ? '('+filtered.length+' results)' : '';
      currentPage = 1; renderPage();
    }});

    document.getElementById('header-search-btn').addEventListener('click', function() {{
      var q = document.getElementById('header-search-input').value.trim();
      if(q) window.location.href = 'search.html?q='+encodeURIComponent(q);
    }});
    document.getElementById('header-search-input').addEventListener('keydown', function(e){{
      if(e.key==='Enter') document.getElementById('header-search-btn').click();
    }});
    var toggle = document.querySelector('.menu-toggle');
    var nav = document.querySelector('.main-nav');
    if(toggle) toggle.addEventListener('click',function(){{nav.classList.toggle('active');}});

    renderPage();
  }})();
  </script>
</body>
</html>'''

    page_path = os.path.join(BASE_DIR, filename)
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ {filename:20s} ({len(items)} items)")

print("\n✅ All category pages regenerated with pagination!")
