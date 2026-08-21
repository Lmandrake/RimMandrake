#!/usr/bin/env python3
"""
deploy_custom_mods.py — push our authored mods from the repo into RimWorld.

THE PROBLEM THIS SOLVES
=======================
`src/` in this repo is the SOURCE of our four authored mods. It is
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
  python src/RimMandrake/Utils/deploy_custom_mods.py                  # plan only; changes NOTHING (default)
  python src/RimMandrake/Utils/deploy_custom_mods.py --apply          # repo -> game, then verify
  python src/RimMandrake/Utils/deploy_custom_mods.py --apply --mod Jawa_Patches
  python src/RimMandrake/Utils/deploy_custom_mods.py --apply --prune  # also delete deployed files no longer in repo
  python src/RimMandrake/Utils/deploy_custom_mods.py --pull Jawa_Patches   # game -> repo, rescue a hand-edit

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
import fnmatch
import os
import shutil
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC_ROOT = os.path.join(ROOT, "src")
# plan §4 dep 2. `custom_patches/` was flat; the two-tier split puts mods under
# src/Jawa/ AND src/RimMandrake/, so discovery gains one level. The deployed
# folder name is still the bare mod name — the game never sees the tier.
SRC_TIERS = ("Jawa", "RimMandrake")


def mod_dirs():
    """-> {mod name: source dir}. A mod is a dir carrying About/About.xml."""
    out = {}
    for tier in SRC_TIERS:
        d = os.path.join(SRC_ROOT, tier)
        if not os.path.isdir(d):
            continue
        for n in sorted(os.listdir(d)):
            p = os.path.join(d, n)
            if os.path.isfile(os.path.join(p, "About", "About.xml")):
                out[n] = p
    return out


def mod_dir(name):
    """Source dir for a mod name, whichever tier holds it."""
    return mod_dirs().get(name, os.path.join(SRC_ROOT, SRC_TIERS[0], name))

# The game side. Native-Windows form first, WSL form second; first one that
# exists wins, so the same script serves both ways of running it.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import LOCAL_MODS, MODS_CONFIG            # noqa: E402

_MODS = [LOCAL_MODS]
_CONFIG = [MODS_CONFIG]


def first_existing(paths, what):
    for p in paths:
        if os.path.exists(p):
            return p
    sys.exit("could not find %s; tried:\n  %s" % (what, "\n  ".join(paths)))


EXCLUDE_DIRS = {"Source", "__pycache__", ".git", "art_candidates", "art_source"}
EXCLUDE_FILES = {".gitignore", ".DS_Store", "Thumbs.db"}
# .md is excluded wholesale rather than just README.md: WreckedMachines carries
# DESIGN.md, MACHINES.md and PLACEHOLDER.md files that are authoring notes, not
# game data. RimWorld ignores them either way, but a deployed mod should be only
# the files the game actually reads — that is what makes the deploy diff
# meaningful. `art_source/` is likewise a workshop, not a payload.
EXCLUDE_EXTS = {".py", ".pyc", ".md"}


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


HOLD_FILE = os.path.join(SRC_ROOT, "DEPLOY_HOLD.txt")


def pretty(path, start=None):
    """Path relative to the repo when possible, absolute when not.

    `os.path.relpath` RAISES on Windows when the two paths are on different
    drives — "path is on mount 'C:', start on mount 'D:'". That is the standard
    layout here (repo on D:, game install on C:), and this is display code:
    a cosmetic shortening must never be able to abort a deploy. Reported by
    A retired seat, 2026-08-13, who hit it running the selftest under python.exe while
    python3 passed, because a temp dir landed on the other drive.
    """
    try:
        return os.path.relpath(path, start or ROOT)
    except ValueError:
        return path


def load_holds():
    """Parse DEPLOY_HOLD.txt -> [{pattern, reason, lineno, hits}].

    WHY A DECLARED LIST AND NOT AN INFERENCE. The plan used to report every
    difference as drift and end with "re-run with --apply", so a tree parked on
    purpose and a tree half-finished rendered identically. Two Jawa_Armoury
    files the owner ruled SHIP NEITHER sat in that plan looking exactly like
    work someone had forgotten to deploy.

    Reading it off ModsConfig instead was considered and is not sufficient: a
    disabled mod is INERT, which is not the same claim as INTENDED, and the hint
    evaporates the moment the mod is enabled.
    """
    holds = []
    try:
        with open(HOLD_FILE, "r", encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                body, _, comment = line.partition("#")
                pattern = body.strip()
                if not pattern:
                    continue
                holds.append({"pattern": pattern.replace(os.sep, "/"),
                              "reason": comment.strip(),
                              "lineno": n, "hits": 0})
    except OSError:
        pass                                   # no hold file is a valid state
    return holds


def hold_for(holds, key):
    """Return the hold entry covering this 'Mod/rel/path', or None."""
    for h in holds:
        if fnmatch.fnmatch(key, h["pattern"]):
            h["hits"] += 1
            return h
    return None


def split_held(holds, name, rels):
    """Partition a rel-path list into (deployable, [(rel, hold), ...])."""
    free, held = [], []
    for rel in rels:
        h = hold_for(holds, "%s/%s" % (name, rel.replace(os.sep, "/")))
        (held.append((rel, h)) if h else free.append(rel))
    return free, held


def compare(src, dst):
    s, d = tree(src), tree(dst)
    new = sorted(s - d)
    gone = sorted(d - s)                       # deployed but no longer in repo
    changed = sorted(r for r in (s & d)
                     if not filecmp.cmp(os.path.join(src, r),
                                        os.path.join(dst, r), shallow=False))
    same = len(s & d) - len(changed)
    return new, changed, gone, same


def wellformed(src, rels):
    """Refuse to deploy XML that does not parse. Returns a list of failures.

    WHY THIS IS IN THE DEPLOY SCRIPT AND NOT LEFT TO DISCIPLINE. Twice on
    2026-08-11 a malformed patch reached the game's Mods folder because the
    validator was run *alongside* the deploy rather than *before* it, and the
    shell ran both regardless of the first one's exit status:

      * DroidsAreMachines.xml   -- '--' inside an XML comment
      * MegafaunaYield.xml      -- a raw '&' from the mod name
                                   "Big and Small - Genes & More"

    A patch file that does not parse is not a partial failure. RimWorld drops
    the WHOLE file, so all 1311 operations in the second one would have gone
    missing silently. This check is cheap, needs no game knowledge, and makes
    the failure impossible rather than merely unlikely. Deeper checks stay in
    skills/rimworld-modding/scripts/validate_patch.py; this is the floor.
    """
    bad = []
    for rel in rels:
        if not rel.lower().endswith(".xml"):
            continue
        path = os.path.join(src, rel)
        try:
            ET.parse(path)
        except ET.ParseError as e:
            bad.append((rel, str(e)))
    return bad


def copy(src, dst, rels):
    bad = wellformed(src, rels)
    if bad:
        print("  ! REFUSING TO DEPLOY: malformed XML")
        for rel, err in bad:
            print("  !   %s: %s" % (rel, err))
        print("  ! fix the file, then re-run. Nothing was copied for this mod.")
        return 0
    for rel in rels:
        target = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(os.path.join(src, rel), target)
    return len(rels)


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
        dst = mod_dir(args.pull)
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

    names = args.mod or sorted(mod_dirs())
    holds = load_holds()
    print("repo : %s" % SRC_ROOT)
    print("game : %s" % mods_dir)
    print("mode : %s" % ("APPLY" if args.apply else "plan only (use --apply to write)"))
    print("holds: %d pattern(s) from %s\n"
          % (len(holds), pretty(HOLD_FILE)))

    drift = False
    wrote = 0
    for name in names:
        src = mod_dir(name)
        dst = os.path.join(mods_dir, name)
        pid = package_id(src)
        new, changed, gone, same = compare(src, dst)
        new, held_new = split_held(holds, name, new)
        changed, held_changed = split_held(holds, name, changed)
        # `gone` is filtered too, and that is not symmetry for its own sake.
        # A hold means "do not change the game's copy of this path" — writing
        # and deleting are both changes. Without this, --apply --prune would
        # DELETE a held file that exists in the game but not the repo, which is
        # a plausible way to park something. Found by a retired seat reviewing this code
        # before it landed; the write path was filtered and the delete path was
        # not, so the hold protected against writing only.
        gone, held_gone = split_held(holds, name, gone)
        held = held_new + held_changed + held_gone

        flags = []
        if not os.path.isdir(dst):
            flags.append("NOT DEPLOYED")
        if pid and pid.lower() not in active:
            flags.append("not enabled in ModsConfig")
        if pid is None:
            flags.append("no packageId in About.xml")

        if held:
            flags.append("%d file(s) HELD" % len(held))

        head = "%-16s %-26s %s" % (name, pid or "?", " · ".join(flags))
        print(head.rstrip())

        # Held files are printed even when nothing else differs. Silently
        # omitting them would recreate the original bug in mirror image: the
        # plan would read "in sync" while the repo and the game genuinely
        # differ, and the next person would trust it.
        for rel, h in held:
            # A held file that is ALREADY deployed in some other state is worth
            # saying out loud: holding stops us updating the game copy, it does
            # not remove what is already there. Left as a note rather than an
            # action — deleting a deployed file is the owner's call, not this
            # script's.
            # Say WHICH state it is in. "game holds an older copy" was wrong for
            # a held path that exists only in the game — the two cases need
            # different words or the note misleads on the case it exists for.
            in_game = os.path.exists(os.path.join(dst, rel))
            in_repo = os.path.exists(os.path.join(src, rel))
            note = ("   (game copy left as-is)" if in_game and in_repo else
                    "   (game-only; kept, not pruned)" if in_game else
                    "   (repo-only; not deployed)")
            print("    H  %s%s" % (rel, note))
            print("           held: %s" % (h["reason"] or
                                           "NO REASON GIVEN — see DEPLOY_HOLD.txt:%d"
                                           % h["lineno"]))

        if not (new or changed or gone):
            print("    in sync (%d files%s)\n"
                  % (same, ", %d held" % len(held) if held else ""))
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
            # Held files legitimately still differ after a deploy — that is the
            # whole point of holding them. Without this filter the verify step
            # reports "STILL DIFFERS" on a correct run, which trains people to
            # ignore the one line that proves the deploy worked.
            n2, _ = split_held(holds, name, n2)
            c2, _ = split_held(holds, name, c2)
            g2, _ = split_held(holds, name, g2)
            leftover = n2 + c2 + (g2 if args.prune else [])
            print("    -> %s" % ("VERIFIED in sync" if not leftover
                                 else "STILL DIFFERS: %s" % leftover))
            if not leftover:
                drift = False
        print()

    # A hold that no longer matches anything is the same failure shape as a
    # stale instruction in a doc: still present, still read, no longer true —
    # and it silently stops protecting whatever it was written for. Only
    # meaningful on a full run; with --mod most patterns legitimately miss.
    if not args.mod:
        # Staleness is "does this pattern name a file that EXISTS", not "did it
        # fire this run". A hold on an in-sync file never appears in the drift
        # lists and would otherwise be reported stale on every clean run —
        # a warning that cries wolf until nobody reads it.
        # Both sides, because a hold may legitimately name a path that exists
        # only in the GAME — that is exactly the parked-by-removal case the
        # `gone` filter above protects. Walking the repo alone would report
        # such a hold as stale while it was actively doing its job.
        for name in names:
            for root in (mod_dir(name),
                         os.path.join(mods_dir, name)):
                for rel in tree(root):
                    key = "%s/%s" % (name, rel.replace(os.sep, "/"))
                    for h in holds:
                        if fnmatch.fnmatch(key, h["pattern"]):
                            h["hits"] += 1
        stale = [h for h in holds if not h["hits"]]
        if stale:
            print("⚠️  %d hold pattern(s) matched NOTHING — stale, or the file "
                  "moved:" % len(stale))
            for h in stale:
                print("      %s:%d  %s" % (pretty(HOLD_FILE),
                                           h["lineno"], h["pattern"]))
            print("    A hold that matches nothing protects nothing. Fix the "
                  "pattern or delete the line.\n")

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
