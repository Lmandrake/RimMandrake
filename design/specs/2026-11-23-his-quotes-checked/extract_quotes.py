#!/usr/bin/env python3
"""List every quote of the owner in guiding prose. Page: boundary.md beside this file.

Three shapes are recognised:
  ITALIC  *"..."*  (also curly quotes); an italic quote is his by this repo's convention.
  PLAIN   "..." of 3 words or more, in a paragraph (or under a heading) that names him as the speaker.
  CARD    a PLAIN quote in a paragraph that says "card", or an arrow form "question -> option".
PLAIN and CARD are CANDIDATES: the reader marks the ones that are not his NOT-HIS. The extractor never drops a
candidate by meaning, so it over-lists on purpose.

Exit 0: listed (a count of 0 is a measured 0). Exit 2: could not look (a file is missing or unreadable).
"""
import argparse, json, re, sys

HIM = re.compile(r"\b(owner|owner's|his words?|he said|he typed|he wrote|he asked|he ruled|he answered|mandrake|lukas|by card|card)\b", re.I)
CARD = re.compile(r"\bcards?\b", re.I)
DATE = re.compile(r"20\d\d-\d\d-\d\d")
ITAL = re.compile(r'(?<!\*)\*["“](.+?)["”][.,;:]?\*(?:\*\*)?(?!\*)', re.S)
PLAIN = re.compile(r'["“]([^"“”]+)["”]', re.S)


def quotes(text):
    lines = text.split("\n")
    out, head, hl = [], "", 0
    # paragraphs: blank-line or heading separated; a list item opens a new paragraph
    paras, cur, start = [], [], 0
    code = False
    for n, l in enumerate(lines + [""], 1):
        if l.lstrip().startswith("```"):
            code = not code
        is_head = l.startswith("#") and not code
        if not l.strip() or is_head:
            if cur:
                paras.append((start, "\n".join(cur), head))
                cur = []
            if is_head:
                head = l.strip("# ")
                paras.append((n, l, head))
            continue
        if not cur:
            start = n
        cur.append(l)
    if cur:
        paras.append((start, "\n".join(cur), head))
    for start, p, h in paras:
        spans = []
        for m in ITAL.finditer(p):
            spans.append((m.start(), m.end(), "ITALIC", m.group(1)))
        masked = p
        for a, b, _, _ in spans:
            masked = masked[:a] + re.sub(r"[^\n]", " ", masked[a:b]) + masked[b:]
        for m in PLAIN.finditer(masked):
            t = m.group(1)
            if len(t.split()) < 3:
                continue
            near = masked[max(0, m.start() - 400):m.end() + 300]
            arrow = "→" in t
            if not (arrow or HIM.search(near) or HIM.search(h)):
                continue
            spans.append((m.start(), m.end(), "CARD" if arrow or CARD.search(near) else "PLAIN", t))
        for a, b, shape, t in sorted(spans):
            near = p[max(0, a - 300):b + 160]
            d = DATE.findall(p[max(0, a - 300):a]) or DATE.findall(p[b:b + 160]) or DATE.findall(h)
            out.append({"line": start + p[:a].count("\n"), "shape": shape, "head": h,
                        "date": d[-1] if d else "", "text": re.sub(r"\s+", " ", t.strip()), "raw": p[a:b]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rows = []
    for f in a.files:
        try:
            t = open(f, encoding="utf-8").read()
        except OSError as e:
            print(f"COULD NOT LOOK: {f}: {e}", file=sys.stderr)
            return 2
        for q in quotes(t):
            q["file"] = f
            rows.append(q)
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=0))
    else:
        for q in rows:
            print(f"{q['file']}:{q['line']}\t{q['shape']}\t{q['date'] or 'no date'}\t{q['text']}")
        print(f"# {len(rows)} listed in {len(a.files)} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
