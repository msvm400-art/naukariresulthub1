import os
from bs4 import BeautifulSoup

base_dir = r"C:\Users\ALOK\Desktop\sarkarinaukari"

keywords = "Sarkari Result 2026, Latest Government Jobs 2026, Govt Jobs Notification, Sarkari Naukri 2026, Free Job Alert 2026, 10th Pass Govt Jobs, 12th Pass Govt Jobs, Graduate Govt Jobs, Central Government Jobs, State Government Jobs, Government Job Vacancy 2026, SSC CGL 2026 Notification, SSC CHSL 2026 Apply Online, UPSC Civil Services 2026, Railway RRB NTPC 2026, Railway Group D Recruitment 2026, IBPS PO 2026 Notification, SBI Clerk 2026 Apply Online, UP Police Constable 2026, Bihar Police Vacancy 2026"

# SEO text for homepage
homepage_seo_text = """
<section class="seo-section" style="margin: 2rem 0; padding: 2rem; background: var(--surface); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); border-top: 4px solid var(--primary);">
    <h2 style="color: var(--primary); margin-bottom: 1rem; font-size: 1.5rem;">Welcome to Sarkari Naukari Infos - Your #1 Source for Government Jobs</h2>
    <p style="color: var(--text-main); line-height: 1.6; margin-bottom: 1rem;">
        Are you searching for the <strong>Latest Government Jobs 2026</strong>? Look no further! At Sarkari Naukari Infos, we provide the fastest updates on <strong>Sarkari Result 2026</strong>, <strong>Govt Jobs Notification</strong>, and <strong>Sarkari Naukri 2026</strong>. Whether you are looking for <strong>10th Pass Govt Jobs</strong>, <strong>12th Pass Govt Jobs</strong>, or <strong>Graduate Govt Jobs</strong>, our platform offers a comprehensive <strong>Free Job Alert 2026</strong> service.
    </p>
    <p style="color: var(--text-main); line-height: 1.6; margin-bottom: 1rem;">
        We cover all major sectors including <strong>Central Government Jobs</strong> and <strong>State Government Jobs</strong>. Stay updated with the latest <strong>Government Job Vacancy 2026</strong> for top exams like <strong>SSC CGL 2026 Notification</strong>, <strong>SSC CHSL 2026 Apply Online</strong>, and <strong>UPSC Civil Services 2026</strong>. 
    </p>
    <p style="color: var(--text-main); line-height: 1.6;">
        Our dedicated sections ensure you never miss out on massive recruitment drives such as <strong>Railway RRB NTPC 2026</strong>, <strong>Railway Group D Recruitment 2026</strong>, <strong>IBPS PO 2026 Notification</strong>, <strong>SBI Clerk 2026 Apply Online</strong>. We also provide timely updates for state-level exams including <strong>UP Police Constable 2026</strong> and <strong>Bihar Police Vacancy 2026</strong>. Bookmark us today for the most reliable Sarkari job updates in India!
    </p>
</section>
"""

for filename in os.listdir(base_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(base_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # update or add keywords meta tag
        meta_kw = soup.find('meta', attrs={'name': 'keywords'})
        if meta_kw:
            meta_kw['content'] = keywords
        else:
            new_kw = soup.new_tag('meta', attrs={'name': 'keywords', 'content': keywords})
            if soup.head:
                soup.head.append(new_kw)

        # Update description to be very SEO rich if it's index.html
        if filename == "index.html":
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            desc_text = "Sarkari Naukari Infos: Find Sarkari Result 2026, Latest Government Jobs 2026, Free Job Alert, SSC CGL 2026 Notification, Railway RRB NTPC 2026, UPSC, and State Govt Jobs."
            if meta_desc:
                meta_desc['content'] = desc_text
            else:
                new_desc = soup.new_tag('meta', attrs={'name': 'description', 'content': desc_text})
                if soup.head:
                    soup.head.append(new_desc)
            
            # Inject SEO text
            main_tag = soup.find('main')
            if main_tag and not main_tag.find('section', class_='seo-section'):
                import bs4
                seo_soup = bs4.BeautifulSoup(homepage_seo_text, 'html.parser')
                # insert at the very bottom of main
                main_tag.append(seo_soup)
                
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"Added SEO keywords to {filename}")
