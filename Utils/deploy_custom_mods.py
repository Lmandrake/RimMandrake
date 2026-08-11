#!/usr/bin/env python3
"""
deploy_custom_mods.py — push our authored mods from the repo into RimWorld.

THE PROBLEM THIS SOLVES
=======================
`custom_patches/` in this repo is the SOURCE of our four authored mods. It is
NOT what the game reads. RimWorld loads a separate copy from its own Mods
folder, which `Player.log` states plainly on every launch:

    Adding mandrake.jawa.patches(C:\\...\\RimWorld\\Mods\\Jawa_Patches)

Nothing kept the two in sync. Editing only the repo copy meant the change
silently never reached the game — no error, no warning, the def just was not
there. That cost a full test cycle on 2026-08-11 (a Gamorrean xenotype authored
into the repo, reported ready, invisible in game because the deployed copy was
untouched).

So: "the file is written" and "the game can see it" are two different claims.
This script is what turns the first into the second, and what proves it.

USAGE
  python Utils/deploy_custom_mods.py                  # plan only; changes NOTHING (default)
  python Utils/deploy_custom_mods.py --apply          # repo -> game, then verify
  python Utils/deploy_custom_mods.py --apply --mod Jawa_Patches
  python Utils/deploy_custom_mods.py --apply --prune  # also delete deployed files no longer in repo
  python Utils/deploy_custom_mods.py --pull Jawa_Patches   # game -> repo, rescue a hand-edit

Runs from WSL or native Windows; the game paths are auto-detected.
Exit code is 0 when repo and game agree, 1 when they do not — so it doubles as a
pre-flight check ("am I about to test what I think I am testing?").

WHAT IS NOT SHIPPED
===================
Authoring-side files are excluded: `Source/` trees, `*.py`, `README.md`,
`__pycache__/`, `.gitignore`. RimWorld ignores them anyway; keeping them out
means a deployed mod is only the files the game actually reads.

AFTER DEPLOYING
===============
**Restart RimWorld.** Defs are parsed once at startup — a running game will not
pick up a new XML no matter how many times you reload the save. Adding brand new
defs (a new xenotype, a new pawnkind) is safe for an existing save; CHANGING or
REMOVING a def that a save already references is not.
"""

import argparse
import filecmp
import os
import shutil
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_ROOT = os.path.join(ROOT, "custom_patches")

# The game side. Native-Windows form first, WSL form second; first one that
# exists wins, so the same script serves both ways of running it.
_MODS = [r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods",
         "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"]
_CONFIG = [r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios"
           r"\RimWorld by Ludeon Studios\Config\ModsConfig.xml",
           "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios"
           "/RimWorld by Ludeon Studios/Config/ModsConfig.xml"]


def first_existing(paths, what):
    for p in paths:
        if os.path.exists(p):
            return p
    sys.exit("could not find %s; tried:\n  %s" % (what, "\n  ".join(paths)))


EXCLUDE_DIRS = {"Source", "__pycache__", ".git", "art_candidates"}
EXCLUDE_FILES = {"README.md", ".gitignore", ".DS_Store", "Thumbs.db"}
EXCLUDE_EXTS = {".py", ".pyc"}


def shippable(rel):
    parts = rel.split(os.sep)
    if any(p in EXCLUDE_DIRS for p in parts[:-1]):
        return False
    name = parts[-1]
    if name in EXCLUDE_FILES:
        return False
    return os.path.splitext(name)[1].lower() not in EXCLUDE_EXTS


def tree(root):
    """relative paths of every shippable file under root"""
    if not os.path.isdir(root):
        return set()
    out = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for f in filenames:
            rel = os.path.relpath(os.path.join(dirpath, f), root)
            if shippable(rel):
                out.add(rel)
    return out


def package_id(mod_dir):
    about = os.path.join(mod_dir, "About", "About.xml")
    try:
        node = ET.parse(about).getroot().find("packageId")
        return (node.text or "").strip() if node is not None else None
    except Exception:
        return None


def active_ids(config):
    try:
        root = ET.parse(config).getroot()
        return {(li.text or "").strip().lower()
                for li in root.find("activeMods").findall("li")}
    except Exception:
        return set()


def compare(src, dst):
    s, d = tree(src), tree(dst)
    new = sorted(s - d)
    gone = sorted(d - s)                       # deployed but no longer in repo
    changed = sorted(r for r in (s & d)
                     if not filecmp.cmp(os.path.join(src, r),
                                        os.path.join(dst, r), shallow=False))
    same = len(s & d) - len(changed)
    return new, changed, gone, same


def copy(src, dst, rels):
    for rel in rels:
        target = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(os.path.join(src, rel), target)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="actually copy repo -> game (default is plan only)")
    ap.add_argument("--prune", action="store_true",
                    help="with --apply, delete deployed files no longer in the repo")
    ap.add_argument("--mod", action="append",
                    help="limit to this mod folder (repeatable)")
    ap.add_argument("--pull", metavar="MOD",
                    help="reverse direction: copy the DEPLOYED copy back into the "
                         "repo, to rescue an edit made directly in the game folder")
    args = ap.parse_args()

    mods_dir = first_existing(_MODS, "the RimWorld Mods folder")
    config = first_existing(_CONFIG, "ModsConfig.xml")
    active = active_ids(config)

    if args.pull:
        src = os.path.join(mods_dir, args.pull)
        dst = os.path.join(SRC_ROOT, args.pull)
        if not os.path.isdir(src):
            sys.exit("not deployed: %s" % src)
        new, changed, _, _ = compare(src, dst)
        if not (new or changed):
            print("nothing to pull; %s already matches the repo" % args.pull)
            return 0
        print("pulling %d file(s) from the game copy into the repo:" % len(new + changed))
        for r in new + changed:
            print("   ", r)
        copy(src, dst, new + changed)
        print("done — review with `git diff` before committing")
        return 0

    names = args.mod or sorted(d for d in os.listdir(SRC_ROOT)
                               if os.path.isdir(os.path.join(SRC_ROOT, d)))
    print("repo : %s" % SRC_ROOT)
    print("game : %s" % mods_dir)
    print("mode : %s\n" % ("APPLY" if args.apply else "plan only (use --apply to write)"))

    drift = False
    wrote = 0
    for name in names:
        src = os.path.join(SRC_ROOT, name)
        dst = os.path.join(mods_dir, name)
        pid = package_id(src)
        new, changed, gone, same = compare(src, dst)

        flags = []
        if not os.path.isdir(dst):
            flags.append("NOT DEPLOYED")
        if pid and pid.lower() not in active:
            flags.append("not enabled in ModsConfig")
        if pid is None:
            flags.append("no packageId in About.xml")

        head = "%-16s %-26s %s" % (name, pid or "?", " · ".join(flags))
        print(head.rstrip())

        if not (new or changed or gone):
            print("    in sync (%d files)\n" % same)
            continue

        drift = True
        for r in new:
            print("    +  %s" % r)
        for r in changed:
            print("    ~  %s" % r)
        for r in gone:
            print("    -  %s   (in game, not in repo%s)"
                  % (r, "; will be deleted" if (args.apply and args.prune) else
                     "; kept — use --prune to delete, or --pull to rescue"))

        if args.apply:
            copy(src, dst, new + changed)
            wrote += len(new) + len(changed)
            if args.prune:
                wrote += len(gone)
                for r in gone:
                    os.remove(os.path.join(dst, r))
            n2, c2, g2, _ = compare(src, dst)
            leftover = n2 + c2 + (g2 if args.prune else [])
            print("    -> %s" % ("VERIFIED in sync" if not leftover
                                 else "STILL DIFFERS: %s" % leftover))
            if not leftover:
                drift = False
        print()

    if args.apply and wrote:
        print("Deployed %d file(s). RESTART RIMWORLD — defs are only parsed at "
              "startup, so reloading a save will not pick these up." % wrote)
    elif args.apply:
        print("Nothing to do; already in sync. No restart needed.")
    elif drift:
        print("Drift found. Re-run with --apply to deploy.")
    else:
        print("Everything in sync.")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
