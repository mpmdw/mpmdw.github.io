#!/usr/bin/env python3
"""Build the static site from the design artboards.

Source of truth: design/project/*.dc.html and design/project/site.css
(the same files the design canvas shows). Run from anywhere:

    python3 website/build.py

Writes index.html, research.html, projects.html, podcast.html, work.html
and style.css next to this script.
"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "design" / "project"

PAGES = {
    "Main.dc.html": ("index.html", "Jon Rocha",
                     "Jon Rocha: computer science at Sonoma State University, AI energy research, projects and podcast."),
    "Research.dc.html": ("research.html", "Research · Jon Rocha",
                         "JouleWise: measuring the energy of each phase of an AI model's response."),
    "Projects.dc.html": ("projects.html", "Projects · Jon Rocha",
                         "JouleWise, BookScout, TravelScout and TestCube."),
    "Podcast.dc.html": ("podcast.html", "Podcast and talks · Jon Rocha",
                        "Two Minds, One Model, a research podcast on AI, plus talks and radio."),
    "Work.dc.html": ("work.html", "Work · Jon Rocha",
                     "Experience, education, certifications and tools."),
}

# Lists the artboards repeat over with <sc-for>; one square per measurement run.
LISTS = {"alpha": 125, "beta": 125, "gamma": 107}

FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800"
         "&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap")

ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
        "%3Crect width='64' height='64' rx='16' fill='%23F6A821'/%3E"
        "%3Ccircle cx='40' cy='24' r='10' fill='%230E1A36'/%3E"
        "%3Cpath d='M8 52c10-15 20-18 28-10 5 5 12 5 20-3v13H8z' fill='%230E1A36'/%3E%3C/svg%3E")

# Set to False once the content is approved, so search engines may index the site.
NOINDEX = True

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
{robots}<link rel="icon" href="{icon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{fonts}">
<link rel="stylesheet" href="style.css">
</head>
<body>
{body}
</body>
</html>
"""


def expand_loops(html: str) -> str:
    def repl(m: re.Match) -> str:
        return m.group(2) * LISTS[m.group(1)]
    return re.sub(r'<sc-for list="\{\{\s*(\w+)\s*\}\}"[^>]*>(.*?)</sc-for>', repl, html, flags=re.S)


def build() -> None:
    for src_name, (out_name, title, description) in PAGES.items():
        text = (SRC / src_name).read_text(encoding="utf-8")
        body = text.split("</helmet>", 1)[1].split("</x-dc>", 1)[0].strip()
        body = expand_loops(body)
        for other, (target, _, _) in PAGES.items():
            body = body.replace(f'href="{other}"', f'href="{target}"')
        if "sc-for" in body or ".dc.html" in body or "{{" in body:
            raise SystemExit(f"{src_name}: unconverted design markup left in the page")
        page = TEMPLATE.format(
            title=title,
            description=description.replace('"', "&quot;"),
            robots='<meta name="robots" content="noindex">\n' if NOINDEX else "",
            icon=ICON,
            fonts=FONTS.replace("&", "&amp;"),
            body=body,
        )
        (ROOT / out_name).write_text(page, encoding="utf-8")
        print(f"wrote {out_name}")
    shutil.copyfile(SRC / "site.css", ROOT / "style.css")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print("wrote style.css")


if __name__ == "__main__":
    build()
