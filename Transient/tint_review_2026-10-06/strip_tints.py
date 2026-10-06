#!/usr/bin/env python3
"""Strip the <color> tint from TINT_ON_COLOUR_ART_1's defs (full-colour art multiplied by a tint in game).

Dry run by default: prints each edit. --apply writes. --only A,B / --except A,B narrow the set (his per-def ruling).
Defs whose tint is a RESKIN over another creature's shared art (the comment says "reskin" / "shared ... art") are
skipped unless --include-reskins: stripping them makes the creature look exactly like the one whose art it borrows.
Edits only the <color> element (and its trailing comment) inside that def's graphicData / bodyGraphicData blocks, as a text edit so comments
and layout survive. Run from the repo root."""
import argparse, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
item = (ROOT / "infrastructure/state/items/TINT_ON_COLOUR_ART_1.md").read_text()
ROWS = re.findall(r"^\| (R[MSU]\w*_\w+) \| \w+ \| `\(([\d ,]+)\)` \|.*`([^`]+\.xml)` \|$", item, re.M)


PAT = r"(<(?:graphicData|bodyGraphicData)>.*?)\n?[ \t]*<color>[^<]*</color>[ \t]*(?:<!--.*?-->)?(.*?</(?:graphicData|bodyGraphicData)>)"
RESKIN = re.compile(r"<color>[^<]*</color>[ \t]*<!--[^>]*(reskin|shared [A-Za-z]+ art)", re.I)


def def_spans(text, name):
    """(start, end) of every <ThingDef>/<PawnKindDef> block whose defName is `name`."""
    out = []
    for m in re.finditer(r"<(ThingDef|PawnKindDef)\b[^>]*>(.*?)</\1>", text, re.S):
        if re.search(r"<defName>\s*%s\s*</defName>" % re.escape(name), m.group(2)):
            out.append((m.start(), m.end()))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--except", dest="exc")
    ap.add_argument("--include-reskins", action="store_true")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    exc = set(a.exc.split(",")) if a.exc else set()
    edits, files = 0, {}
    for name, col, xml in ROWS:
        if (only and name not in only) or name in exc:
            continue
        p = ROOT / xml
        text = files.get(p) or p.read_text(encoding="utf-8")
        n_here = 0
        spans = def_spans(text, name)
        if not a.include_reskins and any(RESKIN.search(text[s:e]) for s, e in spans):
            print("%-28s (%s) SKIPPED: reskin over shared art  %s" % (name, col, xml))
            continue
        for s, e in reversed(spans):
            block = text[s:e]
            new, n = re.subn(PAT,
                             r"\1\2", block, flags=re.S)
            while n:
                block, (new, n) = new, re.subn(PAT,
                                               r"\1\2", new, flags=re.S)
                n_here += 1
            text = text[:s] + block + text[e:]
        files[p] = text
        print("%-28s (%s) %d <color> removed  %s" % (name, col, n_here, xml))
        edits += n_here
    print("TOTAL %d edits in %d files%s" % (edits, len(files), "" if a.apply else "  (dry run: --apply to write)"))
    if a.apply:
        for p, t in files.items():
            p.write_text(t, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
