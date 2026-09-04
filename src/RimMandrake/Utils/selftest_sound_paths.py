#!/usr/bin/env python3
"""Selftest: every declared SoundDef clipPath resolves to a real asset.

ARMOURY_SOUND_PATHS_RSW_PREFIX_1 (criterion 2): this class of defect is
invisible to validate_patch.py and to a def dump -- RimWorld resolves an
AudioClip lazily, on first play, so a wrong clipPath logs nothing until a
player fires that one gun. 18 of the Armoury's 19 clipPaths carried the
RSW_ naming-migration prefix that belongs on the defName, not the path;
this guard is what stops that recurring silently on any future migration
(criterion 3) -- every texPath the game reads has the same shape of risk,
but this file covers only clipPath per the item's own scope.

    python3 src/RimMandrake/Utils/selftest_sound_paths.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
EXT = (".ogg", ".wav", ".mp3")

CLIP_RE = re.compile(r"<clipPath>\s*([^<\s][^<]*?)\s*</clipPath>")


def mod_roots():
    for tier in TIERS:
        tier_dir = os.path.join(REPO_ROOT, "src", tier)
        if not os.path.isdir(tier_dir):
            continue
        for name in sorted(os.listdir(tier_dir)):
            mod_dir = os.path.join(tier_dir, name)
            if os.path.isdir(os.path.join(mod_dir, "Defs")):
                yield mod_dir


def clip_paths_in(defs_dir):
    for root, _dirs, files in os.walk(defs_dir):
        for fn in files:
            if not fn.endswith(".xml"):
                continue
            p = os.path.join(root, fn)
            with open(p, encoding="utf-8-sig", errors="replace") as fh:
                text = fh.read()
            for m in CLIP_RE.finditer(text):
                yield p, m.group(1)


def resolves(sounds_dir, clip_path):
    rel = clip_path.replace("/", os.sep)
    return any(os.path.isfile(os.path.join(sounds_dir, rel + ext)) for ext in EXT)


def main():
    total = 0
    bad = []
    for mod_dir in mod_roots():
        defs_dir = os.path.join(mod_dir, "Defs")
        sounds_dir = os.path.join(mod_dir, "Sounds")
        for src_file, clip_path in clip_paths_in(defs_dir):
            total += 1
            if not resolves(sounds_dir, clip_path):
                bad.append((os.path.relpath(src_file, REPO_ROOT), clip_path))

    print("%d clipPath declaration(s) checked across %s" % (total, ", ".join(TIERS)))
    for src_file, clip_path in bad:
        print("FAIL  %s: clipPath %r resolves to no .ogg/.wav/.mp3" % (src_file, clip_path))

    if bad:
        print("\n%d/%d unresolved" % (len(bad), total))
        return 1
    print("0/%d unresolved" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
