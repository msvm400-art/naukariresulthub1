import os
from bs4 import BeautifulSoup

base_dir = r"C:\Users\ALOK\Desktop\sarkarinaukari"

# SEO Data mapped to filenames
seo_data = {
    "results.html": {
        "title": "Sarkari Result 2026 - Latest Exam Results, Merit Lists & Cut Off",
        "desc": "Check the latest Sarkari Result 2026 for all government exams including SSC, Railway, UPSC, Banking, and State Govt jobs. Fast & accurate updates.",
        "h1": "Latest Sarkari Results 2026",
        "seo_text": "Welcome to the ultimate hub for the <strong>Latest Sarkari Result 2026</strong>. Whether you have appeared for SSC CGL, Railway RRB NTPC, UPSC, or State Police exams, find your results, merit lists, and cut-off marks here instantly. Bookmark this page for the fastest updates on all government exam outcomes."
    },
    "admitcard.html": {
        "title": "Admit Card 2026 - Download Call Letters for Government Exams",
        "desc": "Download your Admit Card 2026 for SSC, Bank, Railway, UP Police, and other Govt job exams. Get direct links for call letters and hall tickets.",
        "h1": "Download Admit Card 2026",
        "seo_text": "Before you step into the examination hall, ensure you have your proper <strong>Admit Card 2026</strong>. From this dedicated portal, you can download call letters for all major competitive exams including Banking, SSC, Railway Group D, and Defense. Stay ahead and download your hall ticket without any server errors."
    },
    "jobs.html": {
        "title": "Latest Government Jobs 2026 - Sarkari Naukri, Free Job Alert",
        "desc": "Find the Latest Government Jobs 2026. Get Free Job Alerts for 10th pass, 12th pass, Graduate, Bank, Railway, and Police Vacancies across India.",
        "h1": "Latest Government Jobs 2026",
        "seo_text": "Are you searching for a stable career in the government sector? Browse through our comprehensive listing of <strong>Latest Government Jobs 2026</strong>. We provide instant **Free Job Alerts** for 10th pass, 12th pass, and graduate candidates. Apply online for upcoming Central and State Government vacancies today."
    },
    "answerkey.html": {
        "title": "Exam Answer Key 2026 - Download Official Question Paper Solutions",
        "desc": "Download official Answer Keys 2026 for UP Police, SSC, CTET, and Railway exams. Calculate your score before the final Sarkari Result.",
        "h1": "Official Exam Answer Key 2026",
        "seo_text": "Curious about your exam performance? Download the official <strong>Answer Key 2026</strong> for all recent tests including SSC CHSL, UPSC Civil Services, and State Board exams. Cross-check your responses, calculate your estimated score, and prepare for the next stage of selection."
    },
    "syllabus.html": {
        "title": "Latest Exam Syllabus 2026 & Exam Pattern - Sarkari Naukari Infos",
        "desc": "Get the latest exam Syllabus 2026 and exam pattern for UPSC, SSC, Bank PO, UPSSSC, and Railway. Start your preparation with the right strategy.",
        "h1": "Latest Exam Syllabus 2026",
        "seo_text": "A solid preparation begins with a clear understanding of the <strong>Exam Syllabus 2026</strong> and the test pattern. Access detailed, official topic-wise syllabi for UP Police, SSC CGL, RRB NTPC, and other government recruitment exams. Download PDF syllabi right here to strategize your study plan effectively."
    },
    "admission.html": {
        "title": "Online Admissions 2026 - University & Entrance Exam Forms",
        "desc": "Apply online for University Admissions 2026, ITI, B.Ed, JEE Main, NEET, and other top entrance exams across India.",
        "h1": "University & Entrance Admission 2026",
        "seo_text": "Ready to advance your education? Keep track of all major <strong>Online Admissions 2026</strong> including Central Universities (CUET), Engineering (JEE Main), Medical (NEET UG), and State-level B.Ed forms. Find application links, important dates, and eligibility criteria to secure your seat in top institutions."
    },
    "important.html": {
        "title": "Important Links, Certificates & Scholarship Forms 2026",
        "desc": "Find Important links for UP Scholarship, Pan Card, Aadhar Card updates, CCC Online Form, and other essential government services.",
        "h1": "Important Services & Scholarship Forms",
        "seo_text": "Beyond job testing, you need proper documentation. Utilize our <strong>Important Links</strong> section to easily access UP Scholarship forms 2026, apply for NIELIT CCC, update your Voter ID, or download essential government certificates. Your one-stop destination for digital India services."
    }
}

for filename, data in seo_data.items():
    filepath = os.path.join(base_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Update title
        if soup.title:
            soup.title.string = data["title"]
        else:
            title_tag = soup.new_tag("title")
            title_tag.string = data["title"]
            soup.head.append(title_tag)
            
        # Update Meta Description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            meta_desc['content'] = data["desc"]
        else:
            new_meta = soup.new_tag('meta', attrs={'name': 'description', 'content': data["desc"]})
            soup.head.append(new_meta)
            
        # Inject SEO Content block at the top of <main>
        main_tag = soup.find('main')
        if main_tag:
            # Check if we already injected SEO block
            if not main_tag.find('div', class_='seo-content-block'):
                seo_div = soup.new_tag('div', attrs={'class': 'seo-content-block', 'style': 'background: var(--surface); padding: 2rem; border-radius: var(--radius-lg); box-shadow: var(--shadow-md); margin-bottom: 2.5rem; border-top: 4px solid var(--primary);'})
                
                h1_tag = soup.new_tag('h1', style='font-size: 1.8rem; color: var(--primary); margin-bottom: 1rem;')
                h1_tag.string = data["h1"]
                
                p_tag = soup.new_tag('p', style='font-size: 1.05rem; line-height: 1.7; color: var(--text-main); margin: 0;')
                import bs4
                p_tag.append(bs4.BeautifulSoup(data["seo_text"], 'html.parser')) # to parse <strong> tags securely

                seo_div.append(h1_tag)
                seo_div.append(p_tag)
                
                # Insert at index 0 of main
                main_tag.insert(0, seo_div)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"Updated {filename}")

# Now build a solid static data.js so the columns look appropriately full
js_content = """// data.js - Central Database for Sarkari Naukari Infos

const siteData = {
    "results": [
        { "title": "UP BTC DELED 2018,2021,2023 First and Third Semester Result", "link": "post.html" },
        { "title": "UP BTC DELED 2024 First Semester Result", "link": "post.html" },
        { "title": "UP Police SI / ASI 2023 Result / Candidate List", "link": "post.html" },
        { "title": "UPSSSC Junior Assistant 2022 Typing Test Result", "link": "post.html" },
        { "title": "UPSSSC Assistant Store Keeper, AG III 2024 Result", "link": "post.html" },
        { "title": "MPPSC Mining Inspector Result 2026", "link": "post.html" },
        { "title": "LIC AAO / Assistant Engineer Phase II Mains Result", "link": "post.html" },
        { "title": "Delhi DDA Junior Secretariat Assistant JSA 2025 Stage I", "link": "post.html" },
        { "title": "Delhi DDA Stenographer 2025 Result", "link": "post.html" },
        { "title": "UPSC Forest Services IFS 2025 Mains Result", "link": "post.html" },
        { "title": "UPPSC LT Grade Assistant Teacher Result 2026 Updated", "link": "post.html" },
        { "title": "RPSC Assistant Statistical Officer ASO 2024 Result", "link": "post.html" },
        { "title": "RPF Constable 2024 Zone Wise Result, Attestation Form", "link": "post.html" },
        { "title": "IBPS RRB 14th Final Result 2026", "link": "post.html" },
        { "title": "RBI Officer Grade B Phase II Result 2026", "link": "post.html" }
    ],
    "admitCards": [
        { "title": "NTA CUET PG 2026 Admit Card", "link": "post.html" },
        { "title": "EMRS Teaching, Non Teaching Post Tier II Exam City", "link": "post.html" },
        { "title": "Railway RRB Paramedical Post Exam City Details 2026", "link": "post.html" },
        { "title": "BPSC AEDO 2025 Exam Schedule", "link": "post.html" },
        { "title": "UPSSSC Exam Calendar 2026", "link": "post.html" },
        { "title": "CBSE KVS / NVS Teaching & Non Teaching Post", "link": "post.html" },
        { "title": "CTET February 2026 Re Exam Admit Card", "link": "post.html" },
        { "title": "RRB Technician CEN 02/2025 Exam City Details", "link": "post.html" },
        { "title": "Railway RRB Paramedical Post Revised Exam Date 2026", "link": "post.html" },
        { "title": "DFCCIL MTS PET Exam Admit Card 2026", "link": "post.html" },
        { "title": "UPPSC Computer Assistant Typing Test Font Notice", "link": "post.html" },
        { "title": "UP Police SI / ASI 2023 Steno Test Admit Card 2026", "link": "post.html" },
        { "title": "UPPSC 2025 Main Exam Schedule", "link": "post.html" },
        { "title": "Bihar Civil Court Peon 2022 Exam Date", "link": "post.html" },
        { "title": "RBI Office Attendant Admit Card 2026", "link": "post.html" }
    ],
    "latestJobs": [
        { "title": "RBI Assistant Online Form 2026", "link": "post.html" },
        { "title": "BTSC Dairy Field Officer / Technical Officer", "link": "post.html" },
        { "title": "Indian Army Agniveer Rally Recruitment", "link": "post.html" },
        { "title": "BPSC School Teacher TRE 4.0 OTR Registration 2026", "link": "post.html" },
        { "title": "Bihar Police BPSSC ASI Operation Online Form 2026", "link": "post.html" },
        { "title": "Yantra India Ltd YIL Ordnance Factory Apprentices", "link": "post.html" },
        { "title": "NTA NSSNET 2026 Online Form", "link": "post.html" },
        { "title": "NTA CUET UG 2026 Online Form Re Open", "link": "post.html" },
        { "title": "BHU School Admissions SET / CHS Online Form 2026", "link": "post.html" },
        { "title": "All India Bar Exam AIBE XXI Online Form 2026", "link": "post.html" },
        { "title": "NTA NCET 2026 Online Form", "link": "post.html" },
        { "title": "MP CPCT Online Form 2026", "link": "post.html" },
        { "title": "UPBED 2026 Online Form", "link": "post.html" },
        { "title": "IMU CET Admissions Online Form 2026", "link": "post.html" },
        { "title": "NTA NEET UG 2026 Online Form", "link": "post.html" }
    ],
    "answerKeys": [
        { "title": "SSC MTS 2025 Answer Key", "link": "post.html" },
        { "title": "Railway RRB Section Controller Answer Key 2026", "link": "post.html" },
        { "title": "Bihar BPSC Special School Teacher Subject Answer Key", "link": "post.html" },
        { "title": "CGPSC Pre 2026 Answer Key", "link": "post.html" },
        { "title": "Delhi DSSSB Answer Key 2026", "link": "post.html" },
        { "title": "UPSC CDS I 2026 Answer Key", "link": "post.html" },
        { "title": "UPSC NDA I 2026 Answer Key", "link": "post.html" },
        { "title": "UPPSC RO ARO 2025 Official Answer Key", "link": "post.html" },
        { "title": "RSMSSB Supervisor Women Empowerment Answer Key", "link": "post.html" },
        { "title": "Haryana HSSC Group C Answer Key 2026", "link": "post.html" },
        { "title": "NTA UGC NET Exam Official Answer Key 2026", "link": "post.html" },
        { "title": "Rajasthan RPSC Assistant Professor Answer Key", "link": "post.html" },
        { "title": "SBI Clerk Prelims Answer Key / Question Paper", "link": "post.html" },
        { "title": "Indian Navy Agniveer SSR / MR Answer Key 2026", "link": "post.html" },
        { "title": "SSC CPO SI 2026 Paper 1 Answer Key", "link": "post.html" }
    ],
    "syllabus": [
        { "title": "NTA NEET UG 2026 Syllabus", "link": "post.html" },
        { "title": "SSC GD Constable Syllabus 2026", "link": "post.html" },
        { "title": "DRDO CEPTAM 11 Exam Syllabus", "link": "post.html" },
        { "title": "UP Super TET Assistant Teacher Syllabus", "link": "post.html" },
        { "title": "UPTET 2026 Primary / Junior Level Syllabus", "link": "post.html" },
        { "title": "UPSC Civil Services Prelims Syllabus 2026", "link": "post.html" },
        { "title": "IBPS PO 2026 Exam Pattern & Syllabus", "link": "post.html" },
        { "title": "Railway RRB Group D Detailed Syllabus PDF", "link": "post.html" },
        { "title": "UP Police Constable Exam Syllabus 2026", "link": "post.html" },
        { "title": "SSC CHSL Tier 1 & 2 Revised Syllabus", "link": "post.html" },
        { "title": "BPSC 70th Pre Exam Syllabus in Hindi / English", "link": "post.html" },
        { "title": "CTET Exam Syllabus Paper 1 & 2 Download", "link": "post.html" },
        { "title": "Delhi Police Constable Executive Syllabus 2026", "link": "post.html" },
        { "title": "SBI PO Exam Pattern and detailed Syllabus", "link": "post.html" },
        { "title": "UPPSC PCS Prelims & Mains Syllabus 2026", "link": "post.html" }
    ],
    "admissions": [
        { "title": "NTA NCET 2026 Online Form", "link": "post.html" },
        { "title": "BHU School Admissions SET / CHS", "link": "post.html" },
        { "title": "UPBED 2026 Online Form", "link": "post.html" },
        { "title": "IMU CET Admissions Online Form 2026", "link": "post.html" },
        { "title": "IERT Admission 2026 Online Form", "link": "post.html" },
        { "title": "CUET UG 2026 Online Admission Form", "link": "post.html" },
        { "title": "UP ITI Admissions 2026 Registration Form", "link": "post.html" },
        { "title": "Delhi University DU PG Admissions Form", "link": "post.html" },
        { "title": "RTE UP 2026 Free Admission Form Apply Online", "link": "post.html" },
        { "title": "Navodaya Vidyalaya NVS Class 6 Admission 2026", "link": "post.html" },
        { "title": "UP D.El.Ed (BTC) 2026 Admission Form", "link": "post.html" },
        { "title": "IGNOU July 2026 Cycle Admission Form", "link": "post.html" },
        { "title": "MP B.Ed / M.Ed Admission Counseling 2026", "link": "post.html" },
        { "title": "JHU Admissions Form 2026 UG / PG Link", "link": "post.html" },
        { "title": "BCECEB Bihar UGEAC Engineering Admission 2026", "link": "post.html" }
    ],
    "important": [
        { "title": "NIELIT CCC Online Form 2026", "link": "post.html" },
        { "title": "MP CPCT Online Form 2026", "link": "post.html" },
        { "title": "MP Rojgar Panjiyan 2025", "link": "post.html" },
        { "title": "UP Scholarship Online Form 2024", "link": "post.html" },
        { "title": "SSC OTR Online Form 2024", "link": "post.html" },
        { "title": "UPSC OTR Registration Portal Link", "link": "post.html" },
        { "title": "Pan Card Apply Online / Status Update", "link": "post.html" },
        { "title": "Aadhar Card Download / Update Online", "link": "post.html" },
        { "title": "Voter ID Card Online Apply / Correction 2026", "link": "post.html" },
        { "title": "Delhi EWS / DG Admission Result 2026", "link": "post.html" },
        { "title": "UP Family ID Registration Online 2026", "link": "post.html" },
        { "title": "UP Income, Caste, Domicile Certificate Online", "link": "post.html" },
        { "title": "Ayushman Bharat Card Apply Online Download", "link": "post.html" },
        { "title": "Udyam Registration MSME Online Form", "link": "post.html" },
        { "title": "Indian Post Payment Bank IPPB Scheme 2026", "link": "post.html" }
    ]
};
"""

with open(os.path.join(base_dir, 'js', 'data.js'), 'w', encoding='utf-8') as f:
    f.write(js_content)
print("Updated data.js with long lists.")
