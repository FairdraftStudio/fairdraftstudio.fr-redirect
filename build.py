"""Build the forwarding pages that keep every fairdraftstudio.fr address working after the name switch.

    python build.py NEW_DOMAIN             # e.g. python build.py nouveau-nom.fr  (test build, no CNAME)
    python build.py NEW_DOMAIN --cname     # switch day: also writes docs/CNAME = fairdraftstudio.fr

Writes docs/ (GitHub Pages serves this repo from main /docs):
- one page per address in the main site's sitemap.xml (../fairdraftstudio.fr/sitemap.xml), plus 404.html,
  which GitHub Pages serves for any other address;
- each page sends the visitor at once to the same address on the new domain: a script that keeps the
  ?query and the #anchor, an instant meta refresh for browsers without JavaScript (Google reads an
  instant refresh as a permanent move), and a canonical link;
- .nojekyll, so the files are served exactly as written.
"""
import re
import shutil
import sys
from pathlib import Path
from xml.etree import ElementTree

HERE = Path(__file__).resolve().parent
OUT = HERE / "docs"
SITEMAP = HERE.parent / "fairdraftstudio.fr" / "sitemap.xml"
OLD_DOMAIN = "fairdraftstudio.fr"

PAGE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace("https://{domain}" + location.pathname + location.search + location.hash);</script>
</head>
<body>
<p>{text} <a href="{target}">{target}</a></p>
</body>
</html>
"""


def paths_from_sitemap():
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [loc.text.strip() for loc in ElementTree.parse(SITEMAP).getroot().findall("s:url/s:loc", ns)]
    paths = []
    for loc in locs:
        match = re.fullmatch(r"https://[^/]+(/.*)", loc)
        if not match:
            sys.exit("Unexpected sitemap entry: " + loc)
        paths.append(match.group(1))
    return paths


def page(domain, path):
    english = path.startswith("/en/")
    return PAGE.format(
        lang="en" if english else "fr",
        title="This site has moved" if english else "Ce site a changé d'adresse",
        text="This site has moved:" if english else "Ce site a changé d'adresse&nbsp;:",
        target="https://" + domain + path,
        domain=domain,
    )


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1 or not re.fullmatch(r"[a-z0-9-]+(\.[a-z0-9-]+)+", args[0]):
        sys.exit(__doc__)
    domain = args[0]
    if domain == OLD_DOMAIN and "--cname" in sys.argv:
        sys.exit("The new domain can't be the old one.")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    paths = paths_from_sitemap()
    for path in paths:
        rel = path.lstrip("/")
        target = OUT / (rel + "index.html" if rel == "" or rel.endswith("/") else rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page(domain, path), encoding="utf-8", newline="\n")
    (OUT / "404.html").write_text(page(domain, "/"), encoding="utf-8", newline="\n")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    if "--cname" in sys.argv:
        (OUT / "CNAME").write_text(OLD_DOMAIN + "\n", encoding="utf-8", newline="\n")
    print(f"{len(paths)} pages + 404.html -> https://{domain}" + (" (CNAME written)" if "--cname" in sys.argv else " (no CNAME: test build)"))


if __name__ == "__main__":
    main()
