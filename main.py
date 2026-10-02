import os
import re
import sys
import struct
import html as html_lib
import urllib.request
from urllib.parse import urljoin, urlparse, quote
from github import Github
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Windows consoles often default to cp949/cp1252; don't crash when printing non-ASCII titles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

# Configuration
GITHUB_PAT = os.getenv("GITHUB_PAT")
OUTPUT_FILE = "GENERATED_PROFILE.md"
STATS_CARD_URL = os.getenv("STATS_CARD_URL", "https://github-readme-stats.vercel.app")
if STATS_CARD_URL and not STATS_CARD_URL.startswith(("http://", "https://")):
    STATS_CARD_URL = "https://" + STATS_CARD_URL

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
                raw_name = line[2:].strip()
                # Remove Korean characters and any resulting empty parentheses
                clean_name = re.sub(r'[가-힣ㄱ-ㅎㅏ-ㅣ]', '', raw_name)
                clean_name = re.sub(r'\s*\(\s*\)', '', clean_name).strip()
                summary["display_name"] = clean_name
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
    "Next.js": {"color": "000000", "logo": "nextdotjs"},
    "PostgreSQL": {"color": "4169E1", "logo": "postgresql"},
    "Prisma": {"color": "2D3748", "logo": "prisma"},
    "AG Grid": {"color": "1B73BA", "logo": "aggrid"},
    "Three.js": {"color": "000000", "logo": "threedotjs"},
    "MUI": {"color": "007FFF", "logo": "mui"},
    "Tailwind CSS": {"color": "06B6D4", "logo": "tailwindcss"},
    "Supabase": {"color": "3FCF8E", "logo": "supabase"},
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

# Live Services / Recent Work
# Public web services showcased at the top of the profile as preview cards.
# Title, description and image are fetched from each page's Open Graph tags
# (falling back to <title> / <meta name="description">) when the profile is generated.
# Any of "name", "description", "image" set here overrides the fetched value.
# "image_mode": "cover" (1200x630 style banner) or "logo" (square icon); auto-detected if omitted.
# "disabled": True renders a locked card for client/confidential work: no OG fetch, no image,
# no link. Such entries take "name"/"description" from here only and must not set "url".
# "group": cards are laid out in list order; consecutive entries sharing a group are placed
# together under a heading row, and each group starts on a new row. Keep related cards adjacent
# (they fill rows left to right, LIVE_PROJECT_COLUMNS per row).
GROUP_MARITIME = "🚢 Maritime & Logistics"
GROUP_CORPORATE = "🏢 Corporate Websites"
GROUP_TOOLS = "🛠️ Tools & Side Projects"

LIVE_PROJECTS = [
    # --- Maritime & Logistics ---
    # Row 1: cargo stowage / lashing
    {
        "group": GROUP_MARITIME,
        "url": "https://stowmate3d.vercel.app",
        "tech": ["Next.js", "React", "Three.js"],
    },
    {
        # The site has no OG tags: name and description come from the project README
        "group": GROUP_MARITIME,
        "url": "https://oog.valueonsys.com",
        "name": "VOS-OOG (ValueOnSys Out of Gauge System)",
        "description": "특수 화물(OOG)의 안전한 운송을 위한 웹 기반 래싱(Lashing) 시뮬레이션 및 적재 관리 솔루션.",
        "tech": ["React", "Vite", "TypeScript", "MUI", "AG Grid"],
    },
    # Row 2: business operation systems
    {
        "group": GROUP_MARITIME,
        "url": "https://tugmate.youngyeon.com",
        "name": "TugMate · 예선사",
        "description": "예선사(Tug Operator) 업무 관리 SaaS. Multi-tenant · PostgreSQL · Prisma · AG Grid.",
        "tech": ["Next.js", "React", "PostgreSQL", "Prisma", "AG Grid"],
    },
    {
        # Confidential client project: shown disabled, client name and URL are not exposed
        "group": GROUP_MARITIME,
        "name": "MDM · 기준정보 관리 시스템",
        "description": "Business Partner · 계정코드 · Freight · Expense · 조직 기준정보를 신청 → 합의 → 승인 → 반영 → 배포(EAI)까지 한 곳에서 관리하는 전사 기준정보 관리 시스템.",
        "tech": ["React", "Vite"],
        "disabled": True,
    },

    # --- Corporate Websites ---
    # Row 1: bio / healthcare
    {
        "group": GROUP_CORPORATE,
        "url": "https://ffb.co.kr",
        "name": "Future F Biotech",
        "tech": ["Gnuboard", "PHP", "MySQL", "jQuery", "Bootstrap"],
    },
    {
        "group": GROUP_CORPORATE,
        "url": "https://www.medibric.com",
        "tech": ["Next.js", "React", "TypeScript", "Tailwind CSS", "Prisma", "Supabase"],
    },
    # Row 2: consulting
    {
        "group": GROUP_CORPORATE,
        "url": "https://www.akpartnersinc.com",
        "tech": ["JavaScript", "HTML", "CSS"],
    },

    # --- Tools & Side Projects ---
    # Row 1: same site (tabmate.valueonsys.com)
    {
        "group": GROUP_TOOLS,
        "url": "https://tabmate.valueonsys.com",
        "tech": ["Next.js", "React"],
    },
    {
        "group": GROUP_TOOLS,
        "url": "https://tabmate.valueonsys.com/holiday-run.html",
        "tech": ["HTML", "CSS", "JavaScript"],
    },
    # Row 2: developer tool
    {
        "group": GROUP_TOOLS,
        "url": "https://ws2react.valueonsys.com/",
        "tech": ["TypeScript", "React", "Vite", "Node.js"],
    },
]

LIVE_PROJECT_COLUMNS = 2       # cards per row
LIVE_PROJECT_DESC_MAX = 140    # truncate long OG descriptions
OG_FETCH_TIMEOUT = 10          # seconds
OG_USER_AGENT = "Mozilla/5.0 (compatible; github-profile-updater)"

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
        color = "555555"
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

def fetch_og_metadata(url):
    """
    Fetches Open Graph metadata (title, description, image, site_name) from a URL.
    Falls back to <title> and <meta name="description">. Returns {} on failure.
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": OG_USER_AGENT})
        with urllib.request.urlopen(req, timeout=OG_FETCH_TIMEOUT) as resp:
            final_url = resp.geturl()
            raw = resp.read(512 * 1024)
        text = raw.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"Warning: Could not fetch OG metadata for {url}. {e}")
        return {}

    meta = {}
    for tag in re.findall(r'<meta\b[^>]*>', text, flags=re.I):
        key_match = re.search(r'(?:property|name)\s*=\s*["\']([^"\']+)["\']', tag, flags=re.I)
        content_match = re.search(r'content\s*=\s*["\']([^"\']*)["\']', tag, flags=re.I)
        if key_match and content_match:
            key = key_match.group(1).strip().lower()
            if key not in meta:  # first occurrence wins
                meta[key] = html_lib.unescape(content_match.group(1).strip())

    title_match = re.search(r'<title[^>]*>(.*?)</title>', text, flags=re.I | re.S)
    page_title = html_lib.unescape(title_match.group(1).strip()) if title_match else ""

    image = meta.get("og:image") or meta.get("twitter:image") or ""
    if image:
        image = urljoin(final_url, image)

    return {
        "title": meta.get("og:title") or page_title,
        "description": meta.get("og:description") or meta.get("description") or "",
        "image": image,
        "site_name": meta.get("og:site_name", ""),
    }

def get_image_size(url):
    """Returns (width, height) for a PNG/GIF/JPEG image URL, or None if unknown."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": OG_USER_AGENT})
        with urllib.request.urlopen(req, timeout=OG_FETCH_TIMEOUT) as resp:
            data = resp.read(256 * 1024)
    except Exception:
        return None

    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data[:6] in (b"GIF87a", b"GIF89a") and len(data) >= 10:
        return struct.unpack("<HH", data[6:10])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                height, width = struct.unpack(">HH", data[i + 5:i + 9])
                return (width, height)
            i += 2 + seg_len
    return None

def truncate_text(text, limit):
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"

def resolve_live_project(cfg):
    """Merges LIVE_PROJECTS config with fetched OG metadata into a render-ready dict."""
    if cfg.get("disabled"):
        # Disabled entries never hit the network and never carry a URL or image
        return {
            "url": "",
            "name": cfg.get("name") or "Private Project",
            "description": cfg.get("description", ""),
            "image": "",
            "image_mode": "cover",
            "tech": cfg.get("tech", []),
            "group": cfg.get("group", ""),
            "disabled": True,
        }

    url = cfg["url"]
    og = fetch_og_metadata(url)

    name = cfg.get("name") or og.get("title") or urlparse(url).netloc
    description = cfg.get("description") or og.get("description") or ""
    image = cfg.get("image") or og.get("image") or ""

    image_mode = cfg.get("image_mode")
    if image and not image_mode:
        size = get_image_size(image)
        # Square-ish images (logos) should not be stretched to card width
        if size and size[1] > 0 and (size[0] / size[1]) < 1.3:
            image_mode = "logo"
        else:
            image_mode = "cover"

    return {
        "url": url,
        "name": name,
        "description": description,
        "image": image,
        "image_mode": image_mode or "cover",
        "tech": cfg.get("tech", []),
        "group": cfg.get("group", ""),
        "disabled": False,
    }

def shields_text(text):
    """Escapes text for a shields.io static badge path segment."""
    return quote(text.replace("-", "--").replace("_", "__"))

def render_live_project_card(project):
    """Renders one project as HTML for use inside a <td> (no Markdown inside HTML blocks)."""
    url = project["url"]
    name = html_lib.escape(project["name"])
    description = html_lib.escape(truncate_text(project["description"], LIVE_PROJECT_DESC_MAX))
    badges = " ".join(get_badge(t) for t in project["tech"])

    if project.get("disabled"):
        # Locked card: grey badge, plain (unlinked) title, no URL
        placeholder = f"https://img.shields.io/badge/{shields_text(project['name'])}-Private-9CA3AF?style=for-the-badge"
        parts = [f'<img src="{placeholder}" alt="{name}" height="32" />', f'<br/><br/><b>🔒 {name}</b>']
        if description:
            parts.append(f'<br/><sub>{description}</sub>')
        if badges:
            parts.append(f'<br/><br/>{badges}')
        parts.append('<br/><br/><sub><i>Private service · link disabled</i></sub>')
        return "\n".join(parts)

    display_url = re.sub(r"^https?://", "", url).rstrip("/")

    if project["image"]:
        if project["image_mode"] == "logo":
            img_tag = f'<a href="{url}"><img src="{project["image"]}" alt="{name}" height="120" /></a>'
        else:
            img_tag = f'<a href="{url}"><img src="{project["image"]}" alt="{name}" width="100%" /></a>'
    else:
        # No OG image: fall back to a large badge so the card still has a visual anchor
        placeholder = f"https://img.shields.io/badge/{shields_text(project['name'])}-Live%20Service-0EA5E9?style=for-the-badge"
        img_tag = f'<a href="{url}"><img src="{placeholder}" alt="{name}" height="32" /></a>'

    parts = [img_tag, f'<br/><br/><b><a href="{url}">{name}</a></b>']
    if description:
        parts.append(f'<br/><sub>{description}</sub>')
    if badges:
        parts.append(f'<br/><br/>{badges}')
    parts.append(f'<br/><br/>🔗 <a href="{url}">{display_url}</a>')
    return "\n".join(parts)

def generate_live_projects_section(live_projects):
    """Generates the 'Recent Work · Live Services' card grid as an HTML table."""
    if not live_projects:
        return ""

    md = "## 🌐 Recent Work · Live Services\n\n"
    md += "> Public web services I built recently. Preview cards are generated from each site's Open Graph metadata.\n\n"

    # No blank lines inside the table: GitHub treats them as the end of the HTML block.
    cell_width = f"{100 // LIVE_PROJECT_COLUMNS}%"
    # Split into runs of consecutive cards sharing the same group
    groups = []
    for project in live_projects:
        group = project.get("group", "")
        if groups and groups[-1][0] == group:
            groups[-1][1].append(project)
        else:
            groups.append((group, [project]))

    md += "<table>\n"
    for group, members in groups:
        if group:
            md += f'  <tr><th colspan="{LIVE_PROJECT_COLUMNS}" align="left">{html_lib.escape(group)}</th></tr>\n'
        # Each group starts on a new row so unrelated cards never share one
        for i in range(0, len(members), LIVE_PROJECT_COLUMNS):
            row = members[i:i + LIVE_PROJECT_COLUMNS]
            md += "  <tr>\n"
            for project in row:
                md += f'    <td width="{cell_width}" valign="top" align="center">\n'
                for line in render_live_project_card(project).split("\n"):
                    md += f"      {line}\n"
                md += "    </td>\n"
            for _ in range(LIVE_PROJECT_COLUMNS - len(row)):
                md += f'    <td width="{cell_width}" valign="top"></td>\n'
            md += "  </tr>\n"
    md += "</table>\n\n"
    md += "---\n\n"
    return md

def generate_markdown(projects, username, stats_url, live_projects=None):
    """
    Generates a Portfolio Style Markdown:
    1. Professional History & Stats (New)
    2. Recent Work · Live Services (OG preview cards)
    3. Highlights Table (Name, Stack, Desc)
    4. Detailed collapsible sections
    """
    md_output = "# 👨‍💻 Private Projects Portfolio\n\n"
    
    # --- New Section: GitHub Live Stats ---
    md_output += "## 📊 GitHub Live Stats\n\n"
    md_output += f"[![GitHub Stats]({stats_url}/api?username={username}&show_icons=true&theme=default&count_private=true)](https://github.com/anuraghazra/github-readme-stats) "
    md_output += f"[![GitHub Streak](https://streak-stats.demolab.com/?user={username}&theme=default)](https://git.io/streak-stats)\n\n"
    md_output += f"[![Top Langs]({stats_url}/api/top-langs/?username={username}&layout=compact&theme=default&count_private=true)](https://github.com/anuraghazra/github-readme-stats)\n\n"
    md_output += "---\n\n"
    
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

    # --- Section: Recent Work · Live Services ---
    md_output += generate_live_projects_section(live_projects or [])

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

    # `python main.py --dry-run` generates the file locally without pushing to GitHub
    dry_run = "--dry-run" in sys.argv[1:]

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

    # Fetch Open Graph metadata for public live services
    print(f"Fetching OG metadata for {len(LIVE_PROJECTS)} live services...")
    live_projects = []
    for cfg in LIVE_PROJECTS:
        resolved = resolve_live_project(cfg)
        print(f"  {resolved['name']} ({resolved['url'] or 'disabled'}) image={'yes' if resolved['image'] else 'no'}")
        live_projects.append(resolved)

    markdown_content = generate_markdown(projects, user.login, STATS_CARD_URL, live_projects)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Successfully generated profile summary to {OUTPUT_FILE}")

    # Push to GitHub Integration
    target_repo_name = os.getenv("TARGET_REPO")
    if dry_run:
        print("Dry run: skipping GitHub push.")
    elif target_repo_name:
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
