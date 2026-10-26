#!/usr/bin/env python3
"""retire_orphan_art.py: retire Textures files that nothing draws, through the art ledger.

A texture is an orphan when no Defs/Patches XML and no C# under any mod in src/ names its texPath: not the
file's stem (Things/X/Y for Things/X/Y.png, facing suffixes _north/_east/_south/_west/_side/_front/_back stripped),
and not its folder (a Graphic_Random / Graphic_Collection texPath names the folder). This script re-checks that
before every retire and refuses a file that anything still names, so the reason it writes is a verifiable
mechanical tag. artledger.retire archives the bytes in the art store, deletes the file and appends a `live` event
with sha None, so `art.py install <mod> <rel> <sha>` puts it back. An owner-KEPT picture is refused by the ledger
(retiring it needs his words) and is reported, never forced.

    python3 src/RimMandrake/Utils/art/retire_orphan_art.py --item <ITEM_ID> <Textures png path>...          # dry run
    python3 src/RimMandrake/Utils/art/retire_orphan_art.py --item <ITEM_ID> --apply <Textures png path>...  # retire
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as A  # noqa: E402

FACING = re.compile(r"_(north|east|south|west|side|front|back)$")
SCAN_DIRS = ("Defs", "Patches", "Source")
SCAN_EXT = {".xml", ".cs"}


def readers(src: Path, needles: list[str]) -> list[str]:
    """Every Defs/Patches XML or C# file under src/*/*/ that contains one of `needles` as a whole texPath."""
    pats = [re.compile(r"(?<![\w/])" + re.escape(n) + r"(?![\w/])") for n in needles]
    hits = []
    for mod in sorted(p for p in src.glob("*/*") if p.is_dir()):
        for d in SCAN_DIRS:
            root = mod / d
            if not root.is_dir():
                continue
            for f in root.rglob("*"):
                if f.suffix not in SCAN_EXT or "/obj/" in f.as_posix() or "/bin/" in f.as_posix():
                    continue
                text = f.read_text(encoding="utf-8", errors="replace")
                if any(p.search(text) for p in pats):
                    hits.append(str(f.relative_to(src.parent)))
    return hits


def needles_for(rel: str) -> list[str]:
    stem = rel[:-4] if rel.lower().endswith(".png") else rel
    out = [FACING.sub("", stem)]
    if "/" in stem:
        out.append(stem.rsplit("/", 1)[0])
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--item", required=True, help="the rimflow item that found the orphans (goes in the reason)")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    if not re.fullmatch(r"[A-Z0-9_]+", a.item):
        print("--item must be a rimflow id (A-Z, 0-9, _)")
        return 2
    reason = "script:src/RimMandrake/Utils/art/retire_orphan_art.py orphan " + a.item
    src = A.src_root()
    bad = 0
    for p in a.paths:
        path = Path(p).resolve()
        if not path.is_file():
            print("ABSENT  %s" % p)
            continue
        try:
            _mod, rel = A.locate(path)
        except A.Refused as e:
            bad += 1
            print("REFUSED %s  %s" % (p, e))
            continue
        hits = readers(src, needles_for(rel))
        if hits:
            bad += 1
            print("READ    %s  still named by %s" % (p, ", ".join(hits[:3])))
            continue
        if not a.apply:
            sha = A.sha256_file(path)
            kept = A.cached_index().protected(sha)
            print("%s %s  %s" % ("KEPT   " if kept else "WOULD  ", sha[:12], p))
            continue
        try:
            r = A.retire(path, reason=reason)
            print("%-7s %s  %s" % (r["status"].upper(), (r.get("old") or "")[:12], p))
        except A.Refused as e:
            bad += 1
            print("REFUSED %s  %s" % (p, e))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
