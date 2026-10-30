#!/usr/bin/env python3
"""Fill template.html from a content folder and write one self-contained HTML file.

usage: build_report.py <content_dir> <output.html>

<content_dir> holds:
  meta.json   {"title", "eyebrow", "h1", "lede", "private_tag", "footer"}   (lede and footer may contain HTML)
  toc.html    the <li><a href="#id">...</a></li> items (sub items: <li class="sub">)
  body.html   the <section id="..."> blocks, glossary last
"""
import json
import pathlib
import sys

here = pathlib.Path(__file__).parent
content = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])

template = (here / "template.html").read_text(encoding="utf-8")
meta = json.loads((content / "meta.json").read_text(encoding="utf-8"))

values = {
    "TITLE": meta["title"],
    "EYEBROW": meta["eyebrow"],
    "H1": meta["h1"],
    "LEDE": meta["lede"],
    "PRIVATE_TAG": meta.get("private_tag", "Private notes · not for the repository"),
    "FOOTER": meta["footer"],
    "TOC": (content / "toc.html").read_text(encoding="utf-8").rstrip(),
    "BODY": (content / "body.html").read_text(encoding="utf-8").rstrip(),
}
html = template
for key, value in values.items():
    marker = "{{" + key + "}}"
    assert html.count(marker) == 1, f"template must hold {marker} exactly once"
    html = html.replace(marker, value)

out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html.encode('utf-8')) // 1024} KB)")
