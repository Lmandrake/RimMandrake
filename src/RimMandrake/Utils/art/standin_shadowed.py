#!/usr/bin/env python3
"""standin_shadowed.py: find donor stand-ins left behind after a render of ours took their place.

`donor_standins.py` copied borrowed art to `<mod>/Textures/StandIn/<rel>` and pointed the XML at `StandIn/<rel>`;
`art install` / `bulk_accept_renders.py` later put our render at `<mod>/Textures/<rel>` and pointed the XML back.
The StandIn copy is then SHADOWED: its twin exists and, when no XML or C# names `StandIn/<rel>` (stem, facing set,
Graphic_Random folder or C# folder literal, the same reader test `retire_orphan_art.py` applies), nothing draws it.
RimWorld has no texture fallback, so such a copy is dead weight that still loads. Ruling
(STANDIN_AUDIT_SHADOWED_COPIES_LEFT): retire it through `retire_orphan_art.py`, never keep it as a "fallback".

    python3 src/RimMandrake/Utils/art/standin_shadowed.py list    # every shadowed stand-in: DEAD (unread) or READ
    python3 src/RimMandrake/Utils/art/standin_shadowed.py check   # exit 1 while any DEAD shadowed stand-in remains

A READ shadowed stand-in (XML still draws StandIn/<rel> although our render sits at <rel>) is listed, not failed:
which picture should be drawn is an art call, not a mechanical one.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as A  # noqa: E402
import retire_orphan_art as R  # noqa: E402

PREFIX = "StandIn/"


def shadowed(src: Path) -> list[tuple[Path, str]]:
    """(stand-in png, 'StandIn/<rel>.png' as a texPath sees it) for every Textures/StandIn/<rel>.png whose mod also holds Textures/<rel>.png."""
    out = []
    for f in sorted(src.rglob("Textures/StandIn/**/*")):
        if not f.is_file() or f.suffix.lower() != ".png":
            continue
        parts = f.parts
        i = max(k for k in range(len(parts) - 1) if parts[k] == "Textures" and parts[k + 1] == "StandIn")
        twin = Path(*parts[:i + 1], *parts[i + 2:])
        if twin.is_file():
            out.append((f, "/".join(parts[i + 1:])))
    return out


def classify(src: Path) -> list[tuple[str, Path, list[str]]]:
    texts = [(r, t) for r, t in R.corpus(src) if PREFIX in t]   # every needle starts with StandIn/
    rows = []
    for f, rel in shadowed(src):
        hits = R.readers(src, R.needles_for(rel), texts, R.folder_of(rel))
        rows.append(("READ" if hits else "DEAD", f, hits))
    return rows


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("list", "check"):
        print(__doc__)
        return 2
    src = A.src_root()
    rows = classify(src)
    root = src.parent
    dead = [r for r in rows if r[0] == "DEAD"]
    for kind, f, hits in rows:
        if argv[0] == "list" or kind == "DEAD":
            print("%-4s %s%s" % (kind, f.relative_to(root), ("  <- " + ", ".join(hits[:2])) if hits else ""))
    print("shadowed stand-ins: %d (dead %d, read %d) under %s" % (len(rows), len(dead), len(rows) - len(dead), src))
    return 1 if (argv[0] == "check" and dead) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
