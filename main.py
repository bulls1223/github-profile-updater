import os
import re
from github import Github
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GITHUB_PAT = os.getenv("GITHUB_PAT")
OUTPUT_FILE = "GENERATED_PROFILE.md"

def get_repo_summary(repo):
    """
    Extracts the title and a brief description from the repository's README.md.
    Returns a dictionary with 'name', 'url', 'description'.
    """
import re

def clean_readme_content(content):
    """
    Cleans README content:
    1. Removes H1 tags (since we use them as headers)
    2. Replace Markdown images with text placeholders to avoid broken links
       EXCEPT for public badges (like shields.io)
    """
    # Remove all lines starting with # (H1)
    lines = content.split('\n')
    cleaned_lines = [line for line in lines if not line.strip().startswith("# ")]
    content = '\n'.join(cleaned_lines)

    def replace_markdown_image(match):
        alt_text = match.group(1)
        url = match.group(2)
        if "shields.io" in url:
            return match.group(0) # Keep public badges
        return f'📷 *[Image: {alt_text}]*'

    def replace_html_image(match):
        tag = match.group(0)
        if "shields.io" in tag:
            return tag # Keep public badges
        return '📷 *[Image]*'

    # Replace markdown images ![alt](url)
    content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_markdown_image, content)
    
    # Replace HTML img tags <img src="...">
    content = re.sub(r'<img[^>]*>', replace_html_image, content)

    return content

def get_repo_summary(repo):
    summary = {
        "name": repo.name,
        "url": repo.html_url,
        "description": repo.description or "No description provided.",
        "language": repo.language,
        "languages": [],
        "topics": [],
        "owner": repo.owner.login,
        "private": repo.private,
        "readme_content": ""
    }

    try:
        # Get Topics
        summary["topics"] = repo.get_topics()
        
        # Get Languages (top 3)
        langs = repo.get_languages()
        # Sort by size (value) in descending order
        sorted_langs = sorted(langs.items(), key=lambda item: item[1], reverse=True)
        summary["languages"] = [l[0] for l in sorted_langs[:3]]
        
        # Get README content
        readme_file = repo.get_readme()
        content = readme_file.decoded_content.decode("utf-8")
        
        # Parse display name if available
        lines = content.split('\n')
        for line in lines:
            if line.startswith("# "):
                summary["display_name"] = line[2:].strip()
                break
        
        summary["readme_content"] = clean_readme_content(content)
        
    except Exception as e:
        print(f"Warning: Could not fetch data for {repo.name}. {e}")

    return summary

# Tech Stack Color & Logo Mapping
TECH_CONFIG = {
    "PHP": {"color": "777BB4", "logo": "php"},
    "Java": {"color": "007396", "logo": "openjdk"},
    "JavaScript": {"color": "F7DF1E", "logo": "javascript", "logoColor": "black", "textColor": "black"},
    "HTML": {"color": "E34F26", "logo": "html5"},
    "CSS": {"color": "1572B6", "logo": "css3"},
    "TypeScript": {"color": "3178C6", "logo": "typescript"},
    "MySQL": {"color": "4479A1", "logo": "mysql"},
    "Apache": {"color": "D22128", "logo": "apache"},
    "jQuery": {"color": "0769AD", "logo": "jquery"},
    "Bootstrap": {"color": "7952B3", "logo": "bootstrap"},
    "Spring Boot": {"color": "6DB33F", "logo": "springboot"},
    "Oracle": {"color": "F80000", "logo": "oracle"},
    "Gradle": {"color": "02303A", "logo": "gradle"},
    "React": {"color": "61DAFB", "logo": "react", "logoColor": "black", "textColor": "black"},
    "Vue.js": {"color": "4FC08D", "logo": "vuedotjs"},
    "Node.js": {"color": "339933", "logo": "nodedotjs"},
    "Python": {"color": "3776AB", "logo": "python"},
    "AWS": {"color": "232F3E", "logo": "amazonaws"},
    "MyBatis": {"color": "C70000", "logo": "apache"}, # Approx
    "Thymeleaf": {"color": "005F0F", "logo": "thymeleaf"},
    "Fastify": {"color": "000000", "logo": "fastify"},
    "Vite": {"color": "646CFF", "logo": "vite"},
    "Gnuboard": {"color": "333333", "logo": "codio"},
    "AdminLTE": {"color": "F012BE", "logo": "adminlte"},
    "W2UI": {"color": "0078D7", "logo": "css3"},
    "Shell": {"color": "89E051", "logo": "gnu-bash"}, 
    "EJS": {"color": "B4CA65", "logo": "ejs"},
    "PLSQL": {"color": "F80000", "logo": "oracle"},
}

# Manual Tech Stack Enrichment
# keys: 'repo_name' OR 'owner/repo_name'
# values: list of additional tech to display
EXTRA_REPO_TECH = {
    # Project: ValueLinkU Platform (VLU)
    "valuelinku-platform/vlu-platform": ["HTML", "JavaScript", "Java"],
    
    # Project: vlu-scheduler
    "valuelinku-platform/vlu-scheduler": ["Spring Boot", "Java", "Shell", "Oracle"],
    
    # Project: ValueLinkU Platform API
    "valuelinku-platform/vlu-platform-api": ["Spring Boot", "Java", "Oracle"],

    # Project: OptiStow Solution
    "valueonsys-youngyeon/optistowage": ["React", "Fastify", "Node.js", "Vite", "TypeScript", "JavaScript", "CSS"],
    
    # Project: Opti-Stow (homepage)
    "valueonsys-youngyeon/homepage": ["JavaScript", "HTML", "PHP", "CSS"],
    
    # Project: VOS-OOG
    "valueonsys-solution/vos-oog": ["TypeScript", "JavaScript", "EJS", "Node.js", "React"],
    
    # Project: VOS-NME
    "valueonsys-solution/vos-nme": ["TypeScript", "HTML", "CSS", "React", "Node.js"],
    
    # Project: AK Partners Homepage
    "axecoder-works/homepage": ["JavaScript", "HTML", "CSS"],
    
    # Project: GLOVEW
    "axecoder-works/glovew-frontend": ["Bootstrap", "jQuery", "HTML", "CSS", "JavaScript"],
    
    # Project: Glovew API Server
    "axecoder-works/glovew-api": ["Spring Boot", "MyBatis", "Gradle", "Java"],
    
    # Project: Future F Biotech
    "axecoder-works/futurefbiotech": ["Gnuboard", "MySQL", "Apache", "jQuery", "PHP", "JavaScript", "CSS"],
    
    # Project: Narmi Logistics Dashboard
    "axecoder-works/narmi": ["AdminLTE", "W2UI", "jQuery", "CSS", "HTML", "JavaScript"],
    
    # Project: WebSquare to React Converter
    "vos-websquare-converter": ["TypeScript", "React", "Node.js"]
}

def get_badge(name):
    """Generates a colored badge HTML img tag."""
    if not name:
        return ""
    
    # Normalize name for lookup
    lookup_name = name
    if name.lower() == "html": lookup_name = "HTML"
    if name.lower() == "css": lookup_name = "CSS"
    if name.lower() == "javascript": lookup_name = "JavaScript"
    
    config = TECH_CONFIG.get(lookup_name, TECH_CONFIG.get(name, None))
    
    # Default if not found
    if not config:
        config = TECH_CONFIG.get("Unknown")
        color = config.get("color")
        logo = name.lower().replace(" ", "")
        logo_color = "white"
    else:
        color = config.get("color", "555555")
        logo = config.get("logo", name.lower())
        logo_color = config.get("logoColor", "white")

    # Encode Text
    text_encoded = name.replace(" ", "%20")
    if name == "Gnuboard 5": text_encoded = "Gnuboard%205"

    url = f"https://img.shields.io/badge/{text_encoded}-{color}?style=flat-square&logo={logo}&logoColor={logo_color}"
    
    # User requested "smaller", adjusting height to 18px (standard is often 20px)
    return f'<img src="{url}" alt="{name}" height="18" />'

def get_language_badge(language):
    return get_badge(language)

def generate_markdown(projects):
    """
    Generates a Portfolio Style Markdown:
    1. Professional History & Stats (New)
    2. Highlights Table (Name, Stack, Desc)
    3. Detailed collapsible sections
    """
    md_output = "# 👨‍💻 Private Projects Portfolio\n\n"
    
    # --- New Section: Knowledge Sharing --- (Moved to bottom)
    # md_output += "## 🏆 Knowledge Sharing (Naver 지식iN)\n\n"


    # --- New Section: Professional History ---
    # md_output += "## 📜 Professional History\n\n"
    # md_output += "<details>\n<summary>Click to view <b>Past Projects & Experience (Detailed)</b></summary>\n\n"
    
    # # Table Header
    # md_output += "| Period | Project Name | Company |\n"
    # md_output += "| :--- | :--- | :--- |\n"
    
    # # New data from image (Reverse Chronological)
    history_table = [
        ("2018.01 ~", "해운물류 플랫폼", "밸류링크유"),
        ("2017.09 ~ 2017.12", "ONE Domestic", "Ocean Network Express"),
        ("2015.08 ~ 2017.08", "PIL 프로젝트", "Pacific International Lines"),
        ("2013.12 ~ 2015.07", "흥아해운 차세대 수행 및 운영", "흥아해운"),
        ("2012.09 ~ 2013.11", "videocooki.com", "(주)아던트컨설팅"),
        ("2012.05 ~ 2012.08", "보안(반출입)관리, IT-VOC", "삼성바이오로직스"),
        ("2012.04", "코오롱 헬스케어", "코오롱베니트(주)"),
        ("2011.08 ~ 2012.03", "GAUS", "현대상선"),
        ("2009.09 ~ 2011.07", "ALPS (한진해운)", "한진해운"),
        ("2009.07 ~ 2009.08", "인터넷 교보문고", "(주)교보문고"),
        ("2009.01 ~ 2009.06", "SDS 차세대 ITSM", "삼성SDS(주)"),
        ("2007.11 ~ 2008.12", "NHN장애관리시스템,도서정보시스템", "NHN Corp."),
        ("2007.03 ~ 2007.10", "SDS 차세대 ITSM", "삼성SDS(주)"),
        ("2004.07 ~ 2007.02", "PRISM", "삼성SDS(주)"),
        ("2003.12 ~ 2004.06", "신계약청약시스템", "녹십자생명"),
        ("2003.11", "수치지도관리시스템", "국토지리정보원"),
        ("2002.08 ~ 2003.10", "한국도로공사통합정보시스템", "한국도로공사"),
        ("2002.05 ~ 2002.07", "CJ39(인터넷쇼핑몰)", "CJ"),
        ("2001.10 ~ 2002.04", "ebs자재관리/고객관리 시스템", "이비에스(주)"),
        ("2001.05 ~ 2001.09", "도서정보시스템", "산업자원부"),
        ("2000.10 ~ 2001.04", "디지털산업단지", "중소기업청"),
        ("2000.03 ~ 2000.09", "한전채용관리", "한국전력"),
        ("1994.04 ~ 1999.10", "인사, 생산 관리", "(주)새한인터내쇼날"),
        # Additional items from previous list with unknown exact dates
        ("-", "외교통상부 (사이버기업서비스)", "외교통상부"),
        ("-", "티켓링크 (선사관람제, 티오비보)", "티켓링크"),
    ]
    
    # for period, project, company in history_table:
    #     md_output += f"| {period} | {project} | {company} |\n"
        
    # md_output += "\n</details>\n\n---\n\n"

    md_output += "> Here is a collection of my private projects. Detailed information is collapsed below.\n\n"
    
    # 1. Summary Table
    md_output += "## 🚀 Project Highlights\n\n"
    md_output += "| Project | Tech Stack (Languages & Tools) |\n"
    md_output += "| :--- | :--- |\n"
    
    for project in projects:
        display_name = project.get("display_name", project["name"])
        url = project["url"]
        
        # Build Rich Tech Stack Badges
        badges = []
        
        # 0. Manual Enrichment (Prepend)
        # Try full key (owner/name) first, then short name
        full_key = f"{project['owner']}/{project['name']}"
        manual_techs = EXTRA_REPO_TECH.get(full_key, EXTRA_REPO_TECH.get(project["name"], []))
        
        repo_techs = set() # Track to avoid duplicates
        
        for tech in manual_techs:
             if tech not in repo_techs:
                badges.append(get_badge(tech))
                repo_techs.add(tech)

        # 1. Languages (Top 3)
        for lang in project.get("languages", []):
            if lang not in repo_techs:
                badges.append(get_badge(lang))
                repo_techs.add(lang)
            
        # 2. Topics (if not redundant)
        existing_langs_lower = [l.lower() for l in repo_techs]
        for topic in project.get("topics", []):
            # Cleanup topic name
            clean_topic = topic.capitalize()
            if topic.lower() == "reactjs": clean_topic = "React"
            
            # Skip project names or weird topics
            if topic.lower() in ["glovew", "stowage", "logistics"]: continue 
            
            if clean_topic.lower() not in existing_langs_lower:
                badges.append(get_badge(clean_topic))
                existing_langs_lower.append(clean_topic.lower())

        # Fallback
        if not badges and project.get("language"):
             badges.append(get_badge(project.get("language")))
             
        tech_stack_html = " ".join(badges)

        if project.get("private", True):
            project_cell = f"🔒 **{display_name}**"
        else:
            project_cell = f"**[{display_name}]({url})**"
        md_output += f"| {project_cell} | {tech_stack_html} |\n"
    
    md_output += "\n---\n\n"
    
    # 2. Detailed Sections
    md_output += "## 📂 Project Details\n\n"
    
    for project in projects:
        display_name = project.get("display_name", project["name"])
        readme = project.get("readme_content", "")
        if not readme:
            readme = "*No detailed README available.*"
            
        if project.get("private", True):
            md_output += f"<details>\n"
            md_output += f"<summary>🔒 <b>{display_name}</b> — <i>Private Repository</i></summary>\n\n"
        else:
            md_output += f"<details>\n"
            md_output += f"<summary>🔍 <b><a href=\"{project['url']}\">{display_name}</a></b> — Click to expand</summary>\n\n"
        md_output += f"{readme}\n"
        md_output += f"\n</details>\n<br/>\n\n"

    md_output += "---\n\n"

    # --- Section: Knowledge Sharing (Moved to Bottom) ---
    md_output += "## 🏆 Knowledge Sharing (Naver 지식iN)\n\n"
    md_output += "> **Rank**: 지존 (Grand Master) | **Answers**: 1,068+ | **Adopted**: 935+\n\n"
    md_output += "I have been actively sharing knowledge in the developer community.\n"
    md_output += "![JavaScript](https://img.shields.io/badge/JavaScript-Top_Expert-yellow?style=flat-square&logo=javascript&logoColor=white) "
    md_output += "![Java](https://img.shields.io/badge/Java-Expert-orange?style=flat-square&logo=java&logoColor=white) "
    md_output += "![JSP](https://img.shields.io/badge/JSP-Expert-red?style=flat-square&logo=java&logoColor=white) "
    md_output += "![HTML](https://img.shields.io/badge/HTML-Expert-blue?style=flat-square&logo=html5&logoColor=white) "
    md_output += "\n\n"

    return md_output

def main():
    if not GITHUB_PAT:
        print("Error: GITHUB_PAT is not set in .env file.")
        return

    g = Github(GITHUB_PAT)
    user = g.get_user()
    print(f"Authenticated as: {user.login}")

    print("Fetching private repositories...")
    # Fetch only private repositories
    private_repos = user.get_repos(type='private')
    
    projects = []
    
    target_repos = [
        "akpartners", "futurefbiotech", "glovew-api", "glovew-frontend", 
        "kimgloves", "narmi", "vos-nme", "vos-oog", "vos-websquare-converter", 
        "vlu-platform", "vlu-platform-api", "vlu-scheduler", "homepage", "optistowage"
    ]
    
    additional_targets = [
        "vos-nme", "vos-oog", "vos-websquare-converter", 
        "vlu-platform", "vlu-platform-api", "vlu-scheduler", 
        "homepage", "optistowage"
    ]

    excluded_owners = [
        "VOS-SOLUTION", "valuelinkU", "VOS-YoungYeon", 
        "ValueOnSys", "VOS-AKPartners"
    ]

    for repo in private_repos:
        # 1. Exclude specific unwanted repo
        if repo.name in ["futurefbiotech-old", "kimgloves"]:
            continue

        # 2. Exclude specific owners
        if repo.owner.login in excluded_owners:
            continue

        # 3. Include if owner is axecoder-works OR name is in watchlist
        if repo.owner.login == "axecoder-works" or repo.name in additional_targets:
            print(f"Processing {repo.name} ({repo.owner.login})...")
            project_summary = get_repo_summary(repo)
            projects.append(project_summary)
        else:
            continue

    print(f"Found {len(projects)} private repositories. Generating report...")
    
    # Sort Projects by User Defined Order
    # Format: (repo_name, owner_login) - owner is needed for duplicate names like 'homepage'
    project_order = [
        ("vlu-platform", "valuelinku-platform"),
        ("vlu-scheduler", "valuelinku-platform"),
        ("vlu-platform-api", "valuelinku-platform"),
        ("optistowage", "valueonsys-youngyeon"),
        ("homepage", "valueonsys-youngyeon"), # Opti-Stow
        ("vos-oog", "valueonsys-solution"),
        ("vos-nme", "valueonsys-solution"),
        ("homepage", "axecoder-works"), # AK Partners
        ("glovew-frontend", "axecoder-works"),
        ("glovew-api", "axecoder-works"),
        ("futurefbiotech", "axecoder-works"),
        ("narmi", "axecoder-works"),
        ("vos-websquare-converter", "valueonsys-solution")
    ]
    
    def get_sort_key(p):
        key = (p["name"], p["owner"])
        if key in project_order:
            return project_order.index(key)
        return 999 # Put unknown projects at the end

    projects.sort(key=get_sort_key)

    markdown_content = generate_markdown(projects)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"Successfully generated profile summary to {OUTPUT_FILE}")

    # Push to GitHub Integration
    target_repo_name = os.getenv("TARGET_REPO")
    if target_repo_name:
        try:
            print(f"Attempting to update {target_repo_name}...")
            repo = g.get_repo(target_repo_name)
            
            # Try to get existing README
            try:
                contents = repo.get_contents("README.md")
                # Update existing file
                if contents.decoded_content.decode("utf-8") != markdown_content:
                    repo.update_file(contents.path, "Update profile README via auto-script", markdown_content, contents.sha)
                    print(f"Successfully updated README.md in {target_repo_name}")
                else:
                    print("No changes detected. Skipping commit.")
            except:
                # Create new file if it doesn't exist
                repo.create_file("README.md", "Initial profile README via auto-script", markdown_content)
                print(f"Successfully created README.md in {target_repo_name}")
                
        except Exception as e:
            print(f"Error updating GitHub repository: {e}")
    else:
        print("TARGET_REPO not set in .env. Skipping GitHub push.")

if __name__ == "__main__":
    main()
