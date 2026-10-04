#!/usr/bin/env python3
"""Selftest: every declared SoundDef clipFolderPath resolves to a real clip folder.

selftest_sound_paths.py covers only single-clip <clipPath> grains; an
AudioGrain_Folder's <clipFolderPath> had no guard at all (gap seen in belt
round 36). Like clipPath, a wrong folder logs nothing until the sound first
plays, so the defect is invisible to validate_patch.py and the def dump.

A folder resolves when ANY of these holds:
  1. src/<tier>/<Mod>/Sounds/<path>/ (any of our mods -- ContentFinder searches
     every active mod) holds at least one .ogg/.wav/.mp3;
  2. an installed vanilla/DLC SoundDef (Data/<Core|DLC>/Defs/**.xml) declares
     the identical clipFolderPath -- i.e. a verbatim reuse of a packed vanilla
     folder, measured from the install, never from a hand-written list.

The vanilla half needs the Windows install; if it is unreachable every
folder that is not one of ours is UNMEASURED (not a pass). A sanity probe
(Core's Buildings/GestatorGlassShattering) proves the vanilla index can see
before any miss is trusted.

    python3 src/RimMandrake/Utils/selftest_sound_folder_paths.py
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
EXT = (".ogg", ".wav", ".mp3")
GAME_DATA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
SANITY = "Buildings/GestatorGlassShattering"
UNMEASURED_PHRASE = "UNMEASURED, not a pass or a fail"

FOLDER_RE = re.compile(r"<clipFolderPath>\s*([^<\s][^<]*?)\s*</clipFolderPath>")


def mod_roots(repo_root):
    for tier in TIERS:
        tier_dir = os.path.join(repo_root, "src", tier)
        if not os.path.isdir(tier_dir):
            continue
        for name in sorted(os.listdir(tier_dir)):
            mod_dir = os.path.join(tier_dir, name)
            if os.path.isdir(mod_dir):
                yield mod_dir


def folders_in(defs_dir):
    for root, _dirs, files in os.walk(defs_dir):
        for fn in files:
            if fn.endswith(".xml"):
                p = os.path.join(root, fn)
                with open(p, encoding="utf-8-sig", errors="replace") as fh:
                    for m in FOLDER_RE.finditer(fh.read()):
                        yield p, m.group(1)


def has_clips(folder):
    if not os.path.isdir(folder):
        return False
    return any(fn.lower().endswith(EXT) for fn in os.listdir(folder))


def vanilla_folders(game_data):
    """Every clipFolderPath an installed Core/DLC def declares, or None if unreachable."""
    if not os.path.isdir(game_data):
        return None
    out = set()
    for p in glob.glob(os.path.join(game_data, "*", "Defs", "**", "*.xml"), recursive=True):
        with open(p, encoding="utf-8-sig", errors="replace") as fh:
            out.update(m.group(1) for m in FOLDER_RE.finditer(fh.read()))
    return out


def check(repo_root, game_data):
    mods = list(mod_roots(repo_root))
    vanilla = vanilla_folders(game_data)
    if vanilla is not None and SANITY not in vanilla:
        vanilla = None  # index cannot see a folder known to exist: do not trust its misses
    declared, ok, bad, unmeasured = 0, 0, [], []
    for mod_dir in mods:
        defs_dir = os.path.join(mod_dir, "Defs")
        if not os.path.isdir(defs_dir):
            continue
        for src_file, path in folders_in(defs_dir):
            declared += 1
            rel = path.replace("/", os.sep)
            if any(has_clips(os.path.join(m, "Sounds", rel)) for m in mods):
                ok += 1
            elif vanilla is None:
                unmeasured.append((os.path.relpath(src_file, repo_root), path))
            elif path in vanilla:
                ok += 1
            else:
                bad.append((os.path.relpath(src_file, repo_root), path))
    return declared, ok, bad, unmeasured, vanilla


def selfcheck():
    """Prove the checker can go red: a fake mod with one good and one bad folder."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        mod = os.path.join(tmp, "src", "RimMandrake", "Fake")
        os.makedirs(os.path.join(mod, "Defs"))
        os.makedirs(os.path.join(mod, "Sounds", "Mine", "Clips"))
        open(os.path.join(mod, "Sounds", "Mine", "Clips", "a.ogg"), "w").close()
        os.makedirs(os.path.join(mod, "Sounds", "Empty"))
        data = os.path.join(tmp, "Data", "Core", "Defs")
        os.makedirs(data)
        with open(os.path.join(data, "s.xml"), "w") as fh:
            fh.write("<Defs><clipFolderPath>%s</clipFolderPath>"
                     "<clipFolderPath>Ambience/Thunder/OffMap</clipFolderPath></Defs>" % SANITY)
        with open(os.path.join(mod, "Defs", "d.xml"), "w") as fh:
            fh.write("<Defs><clipFolderPath>Mine/Clips</clipFolderPath>"
                     "<clipFolderPath>Ambience/Thunder/OffMap</clipFolderPath>"
                     "<clipFolderPath>Empty</clipFolderPath>"
                     "<clipFolderPath>Ambience/Thunder/OffMapp</clipFolderPath></Defs>")
        d, ok, bad, un, _ = check(tmp, os.path.join(tmp, "Data"))
        assert (d, ok) == (4, 2), (d, ok)
        assert sorted(p for _, p in bad) == ["Ambience/Thunder/OffMapp", "Empty"], bad
        assert not un
        # vanilla index that cannot see the sanity folder -> UNMEASURED, never PASS
        with open(os.path.join(data, "s.xml"), "w") as fh:
            fh.write("<Defs><clipFolderPath>Ambience/Thunder/OffMap</clipFolderPath></Defs>")
        d, ok, bad, un, _ = check(tmp, os.path.join(tmp, "Data"))
        assert ok == 1 and not bad and len(un) == 3, (ok, bad, un)
    print("selfcheck: good/vanilla resolve, empty folder + typo red, blind index UNMEASURED")


def main():
    selfcheck()
    declared, ok, bad, unmeasured, vanilla = check(REPO_ROOT, GAME_DATA)
    if vanilla is not None:
        print("vanilla index: %d clipFolderPaths from installed Data (sanity %s seen)" % (len(vanilla), SANITY))
    print("%d clipFolderPath declaration(s) checked, %d resolve" % (declared, ok))
    for src_file, path in bad:
        print("FAIL  %s: clipFolderPath %r is neither a clip folder in our Sounds/ nor a verbatim vanilla folder"
              % (src_file, path))
    if bad:
        print("\n%d/%d unresolved" % (len(bad), declared))
        return 1
    if unmeasured:
        print("%d folder(s) %s (installed game Data unreachable or blind)" % (len(unmeasured), UNMEASURED_PHRASE))
        return 0
    print("0/%d unresolved" % declared)
    return 0


if __name__ == "__main__":
    sys.exit(main())
