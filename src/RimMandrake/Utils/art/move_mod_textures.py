#!/usr/bin/env python3
"""move_mod_textures.py — move a mod's Textures/ tree to a new place THROUGH the art ledger.

A mod rename moves every texture PNG; a plain `git mv` reads to the texture guard as N
deletes plus N unexplained adds and the push is refused. This copies each PNG into the new
tree with `TextureWriter.copy` (a `live` event at the new path) and then retires the old tree
with `TextureWriter.sync` (a `live` event with sha None at each old path). Owner-kept pictures
are never retired by sync: they stay put and are reported, so check the report.

    move_mod_textures.py <old Textures dir> <new Textures dir> [--rel-from A --rel-to B] [--dry-run]

--rel-from/--rel-to rewrite a leading sub-path under Textures/ (a texPath folder rename),
e.g. --rel-from RimMandrake/MessyConduit --rel-to RimMandrake/GimmeSomeSlack.
Commit infrastructure/state/art/events/<SEAT>.jsonl with the moved files.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from artwrite import TextureWriter  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--rel-from", default="")
    ap.add_argument("--rel-to", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    old, new = Path(a.old).resolve(), Path(a.new).resolve()
    if old.name != "Textures" or new.name != "Textures":
        ap.error("both arguments must be Textures/ directories")
    if not old.is_dir():
        ap.error(f"{old} does not exist")
    tw = TextureWriter(__file__, dry_run=a.dry_run, quiet=False)
    moved = 0
    for f in sorted(old.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(old).as_posix()
        if a.rel_from and (rel == a.rel_from or rel.startswith(a.rel_from + "/")):
            rel = a.rel_to + rel[len(a.rel_from):]
        dest = new / rel
        if f.suffix.lower() == ".png":
            tw.copy(f, dest)
        elif not a.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
        moved += 1
    retired = tw.sync(old)
    if not a.dry_run:
        for d in sorted((p for p in old.rglob("*") if p.is_dir()), key=lambda p: -len(p.parts)):
            if not any(d.iterdir()):
                d.rmdir()
        if old.is_dir() and not any(old.iterdir()):
            old.rmdir()
    print(f"moved {moved} file(s), retired {retired} old PNG(s)")
    return tw.report()


if __name__ == "__main__":
    sys.exit(main())
