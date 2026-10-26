#!/usr/bin/env python3
"""retire_orphan_art.py: retire Textures files that nothing draws, through the art ledger.

A texture is an orphan when no XML and no C# anywhere under src/ (Defs, Patches, Source, LoadFolders/version
folders such as `1.6/Defs`, Staged/ trees — every .xml/.cs outside obj/, bin/ and Textures/) names its texPath: not
the file's stem (Things/X/Y for Things/X/Y.png, facing suffixes _north/_east/_south/_west/_side/_front/_back
stripped), not its folder (a Graphic_Random / Graphic_Collection texPath names the folder), and not its folder as a
string-literal prefix (`"Things/X/" + name` in C#). This script re-checks that before every retire and refuses a
file that anything still names, so the reason it writes is a verifiable mechanical tag.

Owner-KEPT pictures are refused (dry run and --apply alike) and reported, never forced: retiring one needs his words.
--apply MOVES, never just deletes: a byte-identical copy goes to the retired-trees root
(`D:\\ClaudeWork\\rimmandrake\\retired-trees\\<ITEM>_<YYYYMMDD>\\<mod>\\Textures\\<rel>`, env RETIRED_TREES_DIR
overrides the root) and is verified first; then artledger.retire archives the bytes in the art store, deletes the
repo file and appends a `live` event with sha None, so `art.py install <mod> <rel> <sha>` puts it back.

    python3 src/RimMandrake/Utils/art/retire_orphan_art.py --item <ITEM_ID> <Textures png path>...          # dry run
    python3 src/RimMandrake/Utils/art/retire_orphan_art.py --item <ITEM_ID> --apply <Textures png path>...  # retire
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as A  # noqa: E402
from rmpaths import rm_path  # noqa: E402

FACING = re.compile(r"_(north|east|south|west|side|front|back)$")
SCAN_EXT = {".xml", ".cs"}
SKIP_PARTS = {"obj", "bin", "Textures", ".git", "node_modules"}


def corpus(src: Path) -> list[tuple[str, str]]:
    """(path relative to src's parent, text) for every .xml/.cs under src/ outside obj/, bin/ and Textures/:
    LoadFolders (`1.6/Defs`, `VehicleTier/Defs`), Staged/ trees and tool sources all count as readers — a miss here
    retires art something still draws."""
    out = []
    for f in sorted(src.rglob("*")):
        if f.suffix not in SCAN_EXT or SKIP_PARTS.intersection(f.relative_to(src).parts[:-1]) or not f.is_file():
            continue
        out.append((str(f.relative_to(src.parent)), f.read_text(encoding="utf-8", errors="replace")))
    return out


def readers(src: Path, needles: list[str], texts: list[tuple[str, str]] | None = None,
            prefixes: list[str] = ()) -> list[str]:
    """Every scanned file that contains one of `needles` as a whole texPath, or one of `prefixes` as a string
    literal ending in `/"` (a path built at runtime from that folder)."""
    pats = [re.compile(r"(?<![\w/])" + re.escape(n) + r"(?![\w/])") for n in needles]
    pats += [re.compile(r'"' + re.escape(p) + r'/"') for p in prefixes]
    return [rel for rel, text in (texts if texts is not None else corpus(src)) if any(p.search(text) for p in pats)]


def folder_of(rel: str) -> list[str]:
    return [rel.rsplit("/", 1)[0]] if "/" in rel else []


def retired_root(item: str) -> Path:
    base = Path(os.environ["RETIRED_TREES_DIR"]) if os.environ.get("RETIRED_TREES_DIR") else rm_path("retired-trees")
    return base / ("%s_%s" % (item, time.strftime("%Y%m%d")))


def copy_out(path: Path, mod: str, rel: str, item: str) -> Path:
    """Byte-identical copy of `path` under the retired-trees root, verified; raises A.Refused on any mismatch."""
    dst = retired_root(item) / (mod[len("src/"):] if mod.startswith("src/") else mod) / "Textures" / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and A.sha256_file(dst) != A.sha256_file(path):
        raise A.Refused("retired-trees already holds different bytes at %s — nothing removed" % dst)
    shutil.copy2(path, dst)
    if A.sha256_file(dst) != A.sha256_file(path):
        raise A.Refused("retired-trees copy did not verify — nothing removed")
    return dst


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
    texts = corpus(src)
    bad = 0
    for p in a.paths:
        path = Path(p).resolve()
        if not path.is_file():
            print("ABSENT  %s" % p)
            continue
        try:
            mod, rel = A.locate(path)
        except A.Refused as e:
            bad += 1
            print("REFUSED %s  %s" % (p, e))
            continue
        hits = readers(src, needles_for(rel), texts, folder_of(rel))
        if hits:
            bad += 1
            print("READ    %s  still named by %s" % (p, ", ".join(hits[:3])))
            continue
        sha = A.sha256_file(path)
        idx = A.cached_index()
        if idx.protected(sha) and not A.held_elsewhere(idx, sha, (mod, rel)):
            bad += 1
            print("KEPT    %s  %s  owner-kept; retiring it needs his words" % (sha[:12], p))
            continue
        if not a.apply:
            print("WOULD   %s  %s" % (sha[:12], p))
            continue
        try:
            dst = copy_out(path, mod, rel, a.item)
            r = A.retire(path, reason=reason)
            print("%-7s %s  %s  -> %s" % (r["status"].upper(), (r.get("old") or "")[:12], p, dst))
        except A.Refused as e:
            bad += 1
            print("REFUSED %s  %s" % (p, e))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
