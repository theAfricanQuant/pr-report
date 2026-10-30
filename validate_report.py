#!/usr/bin/env python3
"""Check a finished report: valid nesting, unique ids, working links, and a glossary that is complete.

usage: validate_report.py <report.html>      (exit code 1 when something is wrong)
"""
import re
import sys
from html.parser import HTMLParser

src = open(sys.argv[1], encoding="utf-8").read()
VOID = {"meta", "link", "br", "hr", "img", "input", "line", "rect", "circle", "path", "polygon", "polyline", "stop"}


class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.ids, self.hrefs, self.errors = [], [], [], []
        self.svgs, self.svgs_labelled, self.figs_with_caption = 0, 0, 0
        self.scripts = []
        self._fig_has_caption = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a" and a.get("href", "").startswith("#"):
            self.hrefs.append(a["href"][1:])
        if tag == "svg":
            self.svgs += 1
            if a.get("role") == "img" and a.get("aria-label"):
                self.svgs_labelled += 1
        if tag == "script":
            self.scripts.append(a.get("src", "inline"))
        if tag == "figcaption":
            self.figs_with_caption += 1
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}> near line {self.getpos()[0]}")
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i] == tag:
                    del self.stack[i:]
                    break
        else:
            self.stack.pop()


c = Checker()
c.feed(src)
problems = []
if c.stack:
    problems.append(f"unclosed tags: {c.stack}")
problems += c.errors[:10]
dups = sorted({i for i in c.ids if c.ids.count(i) > 1})
if dups:
    problems.append(f"duplicate ids: {dups}")
broken = sorted({h for h in c.hrefs if h not in c.ids})
if broken:
    problems.append(f"links with no target: {broken}")
glossary = [i for i in c.ids if i.startswith("g-")]
unlinked = sorted(set(glossary) - set(c.hrefs))
if unlinked:
    problems.append(f"glossary entries never linked from the text: {unlinked}")
if not glossary:
    problems.append("no glossary: every technical term must be explained at the end")
if c.svgs != c.svgs_labelled:
    problems.append(f"{c.svgs - c.svgs_labelled} svg(s) without role=img and aria-label")
if c.svgs != c.figs_with_caption:
    problems.append(f"{c.svgs} svg(s) but {c.figs_with_caption} figcaption(s): one claim, one caption per figure")
main_start = src.find("<main>")
first_section = re.search(r'<section id="([^"]+)"', src[main_start:]) if main_start >= 0 else None
if not first_section or first_section.group(1) != "tldr":
    problems.append('the first section must be <section id="tldr"> (TL;DR for dummies, in everyday words)')
elif src.count('class="tldr-item"') < 1:
    problems.append("the TL;DR section needs at least one problem/fix pair (li.tldr-item)")
if "{{" in src:
    problems.append("an unfilled {{placeholder}} is left in the page")
external = [s for s in c.scripts if s != "inline"]
if external:
    problems.append(f"external scripts found (the report must be self-contained): {external}")
if not re.search(r"<title>[^<]{3,}</title>", src):
    problems.append("missing <title>")

print(f"{len(src.encode()) // 1024} KB | svgs: {c.svgs} | glossary entries: {len(glossary)}")
if problems:
    print("PROBLEMS:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("OK: well-formed, ids unique, every link resolves, every glossary entry is linked, every figure labelled")
