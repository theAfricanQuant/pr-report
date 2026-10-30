---
name: pr-report
description: Use when the user asks for an HTML report, walkthrough or "notes" about a pull request, a fix, a ticket, or someone else's change (issues, code changes, diagrams, glossary). Produces a private, self-contained, designed HTML file for the user's own reading. Trigger words: "pr-report", "html for the PR", "html report", "explain the fix in html".
---

# PR report: a private HTML walkthrough

The user (Ricky) wants a classy HTML page that explains **what was wrong, what was changed in the code, and why**, with diagrams, written for him alone. The reference example is `~/Documents/Speedykom/audit-trail-notes/audit-trail-field-notes.html` (Windows: `C:\Users\User1\Documents\Speedykom\audit-trail-notes\`). Match it.

## Hard rules

1. **Off the record.** These files are for his viewing only. Do not add them to `GLOBAL_DAILY_RECORDS`, memory, a repo, a PR or a comment, and do not publish them with the Artifact tool or any hosted service. Save them locally outside every git repo.
2. **Where:** `/mnt/c/Users/User1/Documents/Speedykom/pr-reports/<short-slug>.html` (create the folder if needed). Never inside `SpeedyMesh/`.
3. **Writing level:** 12th-grade English. Plain, direct sentences. No asides set off by em dashes, no "not X, but Y" framing, no scare quotes, no stock phrases. Say what happened and why.
4. **Explain every technical term at the end** in a Glossary section. Each term is explained in plain English, and **every glossary entry is linked from where the term first appears** in the text (`<a class="t" href="#g-term">term</a>`). The validator enforces this.
5. **Facts only from what you checked.** Read the PR, its diff, reviews and comments with read-only `gh` commands. Do not state a number, a name or a quote you did not see. Say when something is an estimate. If a reviewer raised a point that was not applied, say so plainly.
6. **Git and gh:** the user runs every mutating command. Reading is fine. Never add Claude attribution anywhere.

## Contents of a report (the TL;DR comes first, then the in-depth version)

0. **TL;DR for dummies** (always first, `<section id="tldr" class="tldr">`, first item in the contents list). The whole story in everyday words, before any depth. One `li.tldr-item` per problem: a short title, "What was wrong" (red side) and "What we did" (green side). Use a simple comparison from daily life when it helps (a waiter, a locked door, mail sorted by colour). No jargon here. If a technical word is unavoidable, link it to the glossary. End with one `.tldr-close` line saying where things stand and anything left open. Keep each side to two or three sentences.
1. **The short version:** a table (PR, ticket, what it does, state) and the problems in one line each.
2. **How the thing works** (only as much as the reader needs), with one diagram.
3. **One section per problem:** the symptom, the cause, the fix, a code before/after, and the tests. A diagram where a picture shows the mechanism faster than a sentence.
4. **The review:** what each reviewer found or tested, what was fixed, and what was left (and why).
5. **How we worked / mistakes caught** (only if there is something real to say).
6. **Where things stand:** state, who we wait on, what comes next, known gaps.
7. **Glossary** (alphabetical groups, one `<dl>` per group, entries `id="g-..."`).

Diagrams: draw the mechanism, not the name. Before/after comparisons are drawn side by side. Label arrows. One figure, one claim, with a `figcaption` and `role="img"` plus an `aria-label` on the `<svg>`. Use the CSS classes already in the template (`d-box`, `d-key`, `d-ghost`, `d-bad`, `d-good`, `d-band`, `d-line`, `d-dash`, `d-t`, `d-s`, `d-m`, `d-h`, `d-crit-t`, `d-ok-t`, `d-badge`). Unique marker ids per svg (`a1`, `a2` ...). Text 11 to 13 px, keep it inside its box (a 12 px label fits about 6 px per character). Anchor SVG `<pattern>` tiles with `x`/`y` at their grid's origin.

Reusable pieces in the template CSS: `.table-scroll > table`, `.pill.ok|wait|info|crit|mute`, `.note` (`.warn`, `.good`, `.crit`), `.split > div`, `.codeblock` with `.file` and `<pre>` made of `<span class="l">` lines (`.add`, `.del`, `.c` for comments; no newlines between spans), `figure.diagram`, `.t` term links, `h3 > span.tag` for "Problem 1 · commit abc1234".

## Steps

1. Identify the target (PR number, or "my last merged PR": `gh pr list --author theAfricanQuant --state merged --limit 5`). Confirm its state.
2. Read: `gh pr view N --json title,state,mergedAt,mergedBy,additions,deletions,files,commits,body,reviews,comments`, `gh pr diff N` (save it to the scratchpad), the linked issue, and CI with `gh pr checks N`.
3. Write the content into a scratch folder (outside the repo): `meta.json`, `toc.html`, `body.html` (see `build_report.py` for the shape).
4. Build: `python3 ~/.claude/skills/pr-report/build_report.py <content_dir> <output.html>`
5. Validate: `python3 -I ~/.claude/skills/pr-report/validate_report.py <output.html>`; fix every problem it lists.
6. Look once (optional but worth it): render each diagram with Chrome headless and read the PNG. Headless Chrome ignores `#fragment` scroll, so show one figure per temporary page (script that moves one `figure.diagram` into an empty body) and delete the temporary files afterwards. In zsh, arrays start at 1.
   `"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --hide-scrollbars --window-size=1060,<h> --virtual-time-budget=3000 --screenshot="C:\...\fig.png" "file:///C:/.../tmp.html"`
7. Re-read the text against the facts you gathered and soften anything you did not verify.
8. Tell the user the file path, the PowerShell command, and the one-line summary. Mention anything the reviewers raised that stayed open.

PowerShell to open it: `Start-Process "C:\Users\User1\Documents\Speedykom\pr-reports\<slug>.html"` (check the folder spelling in the path from the file you wrote).
