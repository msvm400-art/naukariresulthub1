import os
from bs4 import BeautifulSoup

base_dir = r"C:\Users\ALOK\Desktop\sarkarinaukari"

new_seo_html = """
<section class="seo-section" style="margin: 2rem 0; padding: 2rem; background: var(--surface); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); border-top: 4px solid var(--primary);">
    <h1 style="color: var(--primary); margin-bottom: 1rem; font-size: 1.8rem; text-align: center;">Welcome to Sarkari Naukari Infos – India's #1 Sarkari Naukari Portal</h1>
    <p style="color: var(--text-main); line-height: 1.6; margin-bottom: 1rem;">
        Are you searching for the Latest Sarkari Naukari 2026? Look no further! At <strong>Sarkari Naukari Infos</strong>, we provide the fastest and most accurate updates on <strong>Sarkari Result 2026</strong>, Government Job Notifications, and free job alerts across India. Whether you are a 10th pass, 12th pass, or graduate candidate, our platform is your one-stop destination for every sarkari naukari opportunity in the country.
    </p>
    <p style="color: var(--text-main); line-height: 1.6; margin-bottom: 1rem;">
        We track thousands of vacancies every day — from central government departments to state-level recruitment boards — so you never miss a single sarkari naukari opening. Bookmark this page and get ahead of millions of other job seekers!
    </p>
    <div style="background-color: rgba(67, 97, 238, 0.1); padding: 15px; border-left: 4px solid var(--secondary); margin-bottom: 2rem; border-radius: 4px;">
        <strong>🔔 Free Job Alert:</strong> New Sarkari Naukari vacancies added daily. Check the Latest Government Job Vacancy 2026 and apply before the deadline!
    </div>

    <h2 style="color: var(--primary); margin-top: 2rem; margin-bottom: 1rem; font-size: 1.5rem;">🏛️ What Is Sarkari Naukari? – Complete Guide 2026</h2>
    <p style="color: var(--text-main); line-height: 1.6; margin-bottom: 1rem;">
        Sarkari Naukari (सरकारी नौकरी) literally means "Government Job" in Hindi. A sarkari naukari offers unmatched job security, regular pay revisions under the Pay Commission, pension benefits, medical coverage, and social prestige.
    </p>
    
    <h3 style="color: var(--text-main); font-weight: 600; margin-bottom: 0.5rem; font-size: 1.2rem;">Why Is Sarkari Naukari So Popular?</h3>
    <ul style="color: var(--text-main); line-height: 1.6; margin-bottom: 1.5rem; padding-left: 20px; list-style-type: disc;">
        <li><strong>Job Security:</strong> Government employees enjoy permanent employment and cannot be easily dismissed.</li>
        <li><strong>Attractive Salary:</strong> Salaries are determined by the Central Pay Commission and revised every 10 years.</li>
        <li><strong>Pension & Benefits:</strong> Old Pension Scheme (OPS) and NPS ensure financial security after retirement.</li>
        <li><strong>Medical & Housing:</strong> CGHS medical cards, HRA, and government housing are key perks.</li>
        <li><strong>Leaves & Holidays:</strong> Gazetted holidays, earned leave, casual leave, and maternity/paternity leave.</li>
    </ul>

    <h2 style="color: var(--primary); margin-top: 2rem; margin-bottom: 1rem; font-size: 1.5rem;">📝 SSC Sarkari Naukari 2026</h2>
    <p style="color: var(--text-main); line-height: 1.6; margin-bottom: 1rem;">
        The Staff Selection Commission (SSC) is the largest recruiter for central government jobs in India. Key SSC examinations include <strong>SSC CGL 2026</strong>, <strong>SSC CHSL 2026</strong>, and <strong>SSC MTS 2026</strong>. Check Sarkari Result.com daily for SSC admit card downloads, answer key releases, and result declarations.
    </p>

    <h2 style="color: var(--primary); margin-top: 2rem; margin-bottom: 1rem; font-size: 1.5rem;">🚆 Railway Sarkari Naukari 2026 – RRB & RRC</h2>
    <p style="color: var(--text-main); line-height: 1.6; margin-bottom: 1rem;">
        Indian Railways is one of the largest employers in the world. Important recruitment includes <strong>RRB NTPC 2026</strong> and <strong>RRB Group D 2026</strong>. Apply online for Track Maintainer, Helper, Porter, and Technical categories.
    </p>

    <h2 style="color: var(--primary); margin-top: 2rem; margin-bottom: 1rem; font-size: 1.5rem;">🏦 Bank & Police Sarkari Naukari 2026</h2>
    <p style="color: var(--text-main); line-height: 1.6; margin-bottom: 1rem;">
        Banking is highly prestigious with exams like <strong>IBPS PO 2026</strong> and <strong>SBI Clerk 2026</strong>. Similarly, Police recruitment across Central Armed Police Forces and state police (like <strong>UP Police Constable 2026</strong> and <strong>Bihar Police Vacancy 2026</strong>) provide fantastic career opportunities for 10th and 12th pass applicants.
    </p>

    <h2 style="color: var(--primary); margin-top: 2rem; margin-bottom: 1rem; font-size: 1.5rem;">🎓 Sarkari Naukari by Qualification</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
        <div style="background: rgba(67, 97, 238, 0.03); padding: 15px; border-radius: 8px; border: 1px solid var(--border);">
            <h3 style="color: var(--primary); margin-bottom: 0.5rem; font-size: 1.1rem;">10th Pass Jobs</h3>
            <p style="color: var(--text-main); font-size: 0.9rem; margin:0;">Railway Group D, India Post GDS, SSC MTS, Army Tradesman.</p>
        </div>
        <div style="background: rgba(67, 97, 238, 0.03); padding: 15px; border-radius: 8px; border: 1px solid var(--border);">
            <h3 style="color: var(--primary); margin-bottom: 0.5rem; font-size: 1.1rem;">12th Pass Jobs</h3>
            <p style="color: var(--text-main); font-size: 0.9rem; margin:0;">SSC CHSL, UP Police, Bihar Police, NDA, IBPS Clerk.</p>
        </div>
        <div style="background: rgba(67, 97, 238, 0.03); padding: 15px; border-radius: 8px; border: 1px solid var(--border);">
            <h3 style="color: var(--primary); margin-bottom: 0.5rem; font-size: 1.1rem;">Graduate Jobs</h3>
            <p style="color: var(--text-main); font-size: 0.9rem; margin:0;">SSC CGL, UPSC Civil Services, IBPS PO, State PSC.</p>
        </div>
    </div>

    <h2 style="color: var(--primary); margin-top: 2rem; margin-bottom: 1rem; font-size: 1.5rem;">📌 How to Apply for Sarkari Naukari 2026</h2>
    <ol style="color: var(--text-main); line-height: 1.6; padding-left: 20px; margin-bottom: 2rem;">
        <li><strong>Find the Job:</strong> Visit naukariresulthub.in for the latest vacancy notification.</li>
        <li><strong>Read the Notification:</strong> Check eligibility carefully.</li>
        <li><strong>Register & Apply:</strong> Fill the online form on the official portal and pay the fee.</li>
        <li><strong>Download Admit Card:</strong> Grab your <em>Sarkari Naukari Admit Card 2026</em> before the exam.</li>
        <li><strong>Check Result:</strong> Verify your <em>Sarkari Result 2026</em> and answer keys on our site.</li>
    </ol>
    
    <div style="font-size: 0.85rem; color: var(--text-muted); border-top: 1px solid var(--border); padding-top: 15px; margin-top: 2rem; line-height: 1.6;">
        <strong>Popular Searches:</strong> sarkari naukari, sarkari result.com 2026, sarkari naukari 2026, sarkari result.com admit card, sarkari result.com answer key, www sarkari result.com, bihar sarkari naukari, sarkari result.com up police, sarkari result.com ssc cgl, sarkari result.com 10th pass job, sarkari naukari update, sarkari naukari ki bharti.
    </div>
</section>
"""

# Replace in HTML files
for filename in os.listdir(base_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(base_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple string replacement for domain
        content = content.replace("sarkarinaukarinfo.net", "naukariresulthub.in")
        
        # Write back for Beautiful Soup
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Now do the BeautifulSoup injection for index.html only
        if filename == "index.html":
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            
            old_seo = soup.find('section', class_='seo-section')
            if old_seo:
                old_seo.decompose()
            
            # create new
            main_tag = soup.find('main')
            if main_tag:
                import bs4
                new_seo_soup = bs4.BeautifulSoup(new_seo_html, 'html.parser')
                main_tag.append(new_seo_soup)
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(soup.prettify(formatter="html5"))
            print(f"Updated index.html SEO content.")

# Also update sitemap.xml and robots.txt
for meta_file in ["sitemap.xml", "robots.txt"]:
    filepath = os.path.join(base_dir, meta_file)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        content = content.replace("sarkarinaukarinfo.net", "naukariresulthub.in")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {meta_file}")
