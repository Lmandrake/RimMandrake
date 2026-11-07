#!/usr/bin/env python3
"""GPT's checkable statements in late_NN.md: every non-empty line of an ERRORS, ENRICHMENT or cross-entry section, by
batch line number, with the entry it was said about (None for a cross-entry line). BETTER CITATIONS are reading pointers
and MUST-SHOW lines are edit proposals (LATE_MUSTSHOW_PROPOSALS.md), so neither is a claim to check here.
usage: late_bullets.py   prints counts per section"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
HEAD = re.compile(r"^(?:#+\s*|\*\*)(?:\d+\.\s*)?(ERRORS|ENRICHMENT|BETTER|MUST|Cross)", re.I)
VERDICT = re.compile(r"^\W*VERDICT", re.I)


def bullets(n, late):
    """[{id: 'NN:line', entry, section, text}] for batch n; a section heading or VERDICT line is never a bullet"""
    ents = late[(n - 1) * 5:n * 5]
    seen, sec, out = -1, None, []
    for i, ln in enumerate(open(os.path.join(HERE, f"late_{n:02d}.md"), encoding="utf-8"), 1):
        s = ln.strip()
        if VERDICT.match(s):
            seen, sec = seen + 1, None
            continue
        m = HEAD.match(s)
        if m:
            sec = m.group(1).upper()
            continue
        if re.match(r"^(#+ |\*\*\d+\.|---+$|\|[-: |]+\|$)", s):  # an entry's own title line or a rule ends nothing but is no claim
            continue
        if s and sec in ("ERRORS", "ENRICHMENT", "CROSS"):
            out.append({"id": f"{n:02d}:{i}", "entry": None if sec == "CROSS" else ents[seen], "section": sec, "text": s})
    return out


if __name__ == "__main__":
    from collections import Counter
    late = open(os.path.join(HERE, "LATE_SLUGS.txt")).read().split()
    c = Counter(b["section"] for n in range(1, 12) for b in bullets(n, late))
    print(dict(c), sum(c.values()))
