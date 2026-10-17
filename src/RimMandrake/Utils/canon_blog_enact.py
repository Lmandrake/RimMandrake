#!/usr/bin/env python3
"""Apply the owner's rulings on the canon-blog-disputes review sheet (2026-10-17).

Reads Transient/canon_blog_disputes/canon_blog_disputes_sheet_2026-10-17.decisions.json and, per entry in
design/RimStarWars/canon_references/<slug>/:
  keep      nothing
  noncanon  keep the file; label the `### Bloggathehutt` section, the visual-brief bullet and the candidate line
            "NOT CANON" (a blog image is never a Must show source)
  cut       delete bloggathehutt_* files, the `### Bloggathehutt` section, every line naming the blog image
            (visual-brief bullet, candidate-images line) and the blog post URL line in Source URLs

Dry run by default; --apply writes. --apply refuses unless reviewStatus.state == "ruled".
    python3 src/RimMandrake/Utils/canon_blog_enact.py [--apply] [--decisions FILE]
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CR = ROOT / "design/RimStarWars/canon_references"
DEFAULT = ROOT / "Transient/canon_blog_disputes/canon_blog_disputes_sheet_2026-10-17.decisions.json"
LABEL = ("**NOT CANON (owner ruling: keep as noncanon, canon_blog_disputes sheet): fan-blog material; "
         "never a Must show source.**")
TAG = "NOT CANON (fan blog) - "


def plan(slug, decision):
    d = CR / slug
    desc = d / "description.md"
    files = sorted(d.glob("bloggathehutt_*"))
    if decision == "keep" or not desc.exists():
        return [], None
    lines = desc.read_text(encoding="utf-8").split("\n")
    names = [f.name for f in files]
    out, acts, i = [], [], 0
    url = None
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("### Bloggathehutt"):
            m = re.search(r"https?://\S+", ln)
            url = m.group(0) if m else url
            j = i + 1
            while j < len(lines) and not lines[j].startswith("#"):
                j += 1
            if decision == "cut":
                acts.append(f"remove section {ln[:70]!r} ({j - i} lines)")
                i = j
                continue
            out.append(ln)
            if LABEL not in lines[i + 1:j]:
                out.append(LABEL)
                acts.append("label section NOT CANON")
            i += 1
            continue
        if any(n in ln for n in names):
            if decision == "cut":
                acts.append(f"delete line {ln[:60]!r}")
                i += 1
                continue
            if TAG not in ln:
                ln = re.sub(r"^(- )", r"\1" + TAG, ln, count=1)
                acts.append(f"tag line {ln[:60]!r}")
        out.append(ln)
        i += 1
    if decision == "cut" and url:   # blog post URL line in Source URLs
        keep = [x for x in out if not (x.lstrip().startswith("- ") and url.rstrip("/") in x)]
        if len(keep) != len(out):
            acts.append("delete Source URLs line for the blog post")
        out = keep
    if decision == "cut":
        acts += [f"delete file {f.name}" for f in files]
    return acts, (desc, "\n".join(out), files if decision == "cut" else [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--decisions", default=str(DEFAULT))
    a = ap.parse_args()
    doc = json.loads(Path(a.decisions).read_text(encoding="utf-8"))
    state = (doc.get("reviewStatus") or {}).get("state")
    if a.apply and state != "ruled":
        sys.exit(f"REFUSED: reviewStatus.state is {state!r}, not 'ruled' - these are agent pre-fills, not the owner's rulings")
    counts = {}
    for slug, row in sorted((doc.get("decisions") or {}).items()):
        dec = row.get("decision")
        counts[dec] = counts.get(dec, 0) + 1
        acts, p = plan(slug, dec)
        for x in acts:
            print(f"{'APPLY' if a.apply else 'would'} {slug}: {x}")
        if a.apply and p:
            desc, text, files = p
            desc.write_text(text, encoding="utf-8")
            for f in files:
                f.unlink()
    print("decisions:", counts, "(dry run, pass --apply to act)" if not a.apply else "(applied)")


if __name__ == "__main__":
    main()
