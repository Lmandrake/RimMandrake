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
  python src/RimMandrake/Utils/deploy_custom_mods.py --apply --prune  # also delete ALL game-only files (repo-deleted ones are pruned by --apply alone)
  python src/RimMandrake/Utils/deploy_custom_mods.py --pull Jawa_Patches   # game -> repo, rescue a hand-edit
  python src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes       # plan the composed Baroque Biomes mod
  python src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes --apply

COMPOSED MODS (BAROQUE_BIOMES_COMPOSE_1)
========================================
`--compose biomes` builds the one player-facing 'RimMandrake: Baroque Biomes'
folder from the per-biome dev folders listed in src/RimMandrake/Biomes.compose.json
(biomes_compose.py does the building), then runs it through the SAME
compare/copy/verify/hold path as any other mod. Every source folder the
manifest's current compose_wave folds in is REMOVED from ordinary discovery:
`--mod Contagion` refuses and points here, so a folded biome is never
redeployed standalone by habit.

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
SRC_TIERS = ("RimMandrake", "RimStarWars", "RimUtinni", "SPLIT_Phase3")


def folded():
    """-> {source folder: (composed target, key)} for folders a compose manifest
    folds in. Read from SRC_ROOT at call time (the deploy-hold selftest rebinds
    SRC_ROOT to a synthetic tree that has no manifest)."""
    try:
        return biomes_compose.folded_sources(SRC_ROOT)
    except Exception as e:                    # a broken manifest must not hide mods
        print("deploy_custom_mods.py: could not read the compose manifest (%s: %s); "
              "treating nothing as folded" % (type(e).__name__, e), file=sys.stderr)
        return {}


def folded_refusal(names):
    """Exit with a pointer if any requested name is folded into a composed mod."""
    f = folded()
    hit = [n for n in names if n in f]
    if hit:
        sys.exit("deploy_custom_mods.py: %s %s folded into %s (src/RimMandrake/"
                 "Biomes.compose.json) and is no longer deployed standalone.\n"
                 "  deploy it with: python3 src/RimMandrake/Utils/deploy_custom_mods.py "
                 "--compose biomes [--apply]"
                 % (", ".join(hit), "is" if len(hit) == 1 else "are",
                    f[hit[0]][0]))


def mod_dirs():
    """-> {mod name: source dir}. A mod is a dir carrying About/About.xml.
    Folders folded into a composed mod are excluded (see folded())."""
    out = {}
    skip = folded()
    for tier in SRC_TIERS:
        d = os.path.join(SRC_ROOT, tier)
        if not os.path.isdir(d):
            continue
        for n in sorted(os.listdir(d)):
            p = os.path.join(d, n)
            if os.path.isfile(os.path.join(p, "About", "About.xml")):
                if tier == SRC_TIERS[0] and n in skip:
                    continue
                if n in out:
                    # Two tiers using the same bare folder name collide silently
                    # here otherwise — the second tier scanned wins with no
                    # warning, and the loser is never deployed and never
                    # appears in the plan. This has bitten before (two mods
                    # both named FireEcology in different tiers).
                    sys.exit("deploy_custom_mods.py: duplicate mod folder name "
                             "%r in both %s and %s — rename one." % (n, out[n], p))
                out[n] = p
    return out


def mod_dir(name):
    """Source dir for a mod name, whichever tier holds it."""
    return mod_dirs().get(name, os.path.join(SRC_ROOT, SRC_TIERS[0], name))

# The game side. Native-Windows form first, WSL form second; first one that
# exists wins, so the same script serves both ways of running it.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import LOCAL_MODS, MODS_CONFIG            # noqa: E402
import biomes_compose                                      # noqa: E402

_MODS = [LOCAL_MODS]
_CONFIG = [MODS_CONFIG]


def first_existing(paths, what):
    for p in paths:
        if os.path.exists(p):
            return p
    sys.exit("could not find %s; tried:\n  %s" % (what, "\n  ".join(paths)))


EXCLUDE_DIRS = {"Source", "__pycache__", ".git", "art_candidates", "art_source",
                "_artsrc", "obj", "bin", ".vs"}
EXCLUDE_FILES = {".gitignore", ".DS_Store", "Thumbs.db"}
# .md is excluded wholesale rather than just README.md: WreckedMachines carries
# DESIGN.md, MACHINES.md and PLACEHOLDER.md files that are authoring notes, not
# game data. RimWorld ignores them either way, but a deployed mod should be only
# the files the game actually reads — that is what makes the deploy diff
# meaningful. `art_source/` and `_artsrc/` are likewise workshops, not payloads
# (review 2026-09-06: `_artsrc/raw/*.png`, 28 MB, was about to deploy); `obj/`,
# `bin/`, `.csproj` are build residue — the game reads Assemblies/*.dll only.
EXCLUDE_EXTS = {".py", ".pyc", ".md", ".csproj", ".sln", ".user"}


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
            # A dangling symlink is not a file: a staged (MayRequire-rewritten)
            # copy is a symlink farm over src/, and a source file deleted after
            # staging -- another helper's move, mid-run -- left a link whose
            # filecmp raised FileNotFoundError and killed the whole plan
            # (DEPLOY_PLANNER_FIX_CRASH_ON_DELETED, SWBestiary Karrask.png).
            if shippable(rel) and os.path.exists(os.path.join(dirpath, f)):
                out.add(rel)
    return out


def repo_deleted(src, gone):
    """Subset of `gone` (game-only files) that the repo once TRACKED and later
    deleted -- as opposed to files that only ever existed in the game (hand
    edits, which --pull exists to rescue). One git call per mod. Returns an
    empty set when src is not in a git work tree (composed temp dirs, tests)."""
    import subprocess
    if not gone or not os.path.isdir(src):
        return set()
    try:
        out = subprocess.run(
            ["git", "-C", src, "log", "--diff-filter=D", "--name-only",
             "--pretty=format:", "--", "."],
            capture_output=True, text=True, timeout=120)
        top = subprocess.run(["git", "-C", src, "rev-parse", "--show-prefix"],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return set()
    if out.returncode or top.returncode:
        return set()
    prefix = top.stdout.strip()          # e.g. src/RimMandrake/Pyrelands/
    deleted = set()
    for line in out.stdout.splitlines():
        line = line.strip()
        if line.startswith(prefix):
            deleted.add(line[len(prefix):].replace("/", os.sep))
    return {g for g in gone if g.replace("/", os.sep) in deleted
            and not os.path.exists(os.path.join(src, g))}


def composed_repo_deleted(gone, man=None):
    """repo_deleted() for the COMPOSED target (COMPOSE_PLAN_FIX_COMMITTED_DELETES):
    its temp folder has no git history, so map each game-only path under
    Biomes/<key>/ back through the manifest entry to its source folder and ask
    that folder's history. Paths outside every current entry stay hand edits."""
    if not gone:
        return set()
    man = man if man is not None else biomes_compose.load_manifest(SRC_ROOT)
    if not man:
        return set()
    out = set()
    for e in biomes_compose.composed_entries(man):
        sdir = os.path.join(SRC_ROOT, biomes_compose.TIER_DIR, e["source"])
        pre = biomes_compose.dest_rel(e).replace("/", os.sep) + os.sep
        sub = [g.replace("/", os.sep)[len(pre):] for g in gone
               if g.replace("/", os.sep).startswith(pre)]
        out |= {pre + r for r in repo_deleted(sdir, sub)}
    return {g for g in gone if g.replace("/", os.sep) in out}


def worktree_deleted(src, gone):
    """Subset of `gone` that HEAD still TRACKS but the working tree no longer
    has: a delete, `git rm` or `git mv` not yet committed (often another helper's move in
    progress). It is a repo-side removal, so the plan says so instead of
    calling it a hand edit to --pull -- but it is UNCOMMITTED, so a plain
    --apply does not prune it (only --prune does). Empty outside a git tree."""
    import subprocess
    if not gone or not os.path.isdir(src):
        return set()
    # `ls-files --deleted` sees only deletes still in the index; a `git rm`
    # (staged delete) is gone from the index, so ask the index-vs-HEAD diff too.
    # --no-renames: a staged `git mv` must read as a delete here, not a rename.
    try:
        outs = [subprocess.run(cmd, capture_output=True, text=True, timeout=120) for cmd in (
            ["git", "-C", src, "ls-files", "--deleted", "--", "."],
            ["git", "-C", src, "diff", "--cached", "--no-renames", "--relative",
             "--name-only", "--diff-filter=D", "--", "."])]
    except (OSError, subprocess.SubprocessError):
        return set()
    if any(o.returncode for o in outs):
        return set()
    missing = {ln.strip().replace("/", os.sep) for o in outs
               for ln in o.stdout.splitlines() if ln.strip()}
    return {g for g in gone if g.replace("/", os.sep) in missing
            and not os.path.exists(os.path.join(src, g))}


def inside(dst, rel):
    """True only if dst/rel resolves to a path strictly inside dst."""
    base = os.path.realpath(dst)
    p = os.path.realpath(os.path.join(dst, rel))
    return p.startswith(base + os.sep)


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
# The owner's real full list (what modlist_swap.py --restore restores): a game
# folder with no repo source and not on this list never loads, so the def guard
# leaves it out of scope. Missing file -> nothing is left out.
FULL_LIST = os.path.join(ROOT, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")


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
    changed = []
    for r in sorted(s & d):
        try:
            if not filecmp.cmp(os.path.join(src, r), os.path.join(dst, r), shallow=False):
                changed.append(r)
        except OSError:
            # vanished between the walk and the compare (a concurrent delete):
            # classify by what is there NOW instead of crashing the plan.
            if not os.path.exists(os.path.join(src, r)):
                s.discard(r)
                gone.append(r)
            elif not os.path.exists(os.path.join(dst, r)):
                d.discard(r)
                new.append(r)
            else:
                raise
    new.sort()
    gone.sort()
    # A list, not a count: DEPLOY_HOLD_SAME_BUCKET_BLIND_1 — a file that was
    # deployed byte-identical BEFORE it was added to DEPLOY_HOLD.txt never
    # shows up in new/changed/gone again, so a hold added after the fact was
    # silently invisible (not reported, not removed) forever. The caller
    # still needs len(same) for the "in sync (N files)" count.
    same = sorted((s & d) - set(changed))
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
    """Returns (copied, refused, failed). `refused` is True when the mod's XML
    is malformed and NOTHING was copied; `failed` lists (rel, error) for files
    the OS would not write (a DLL locked by the running game, a permission
    error on the Program Files tree). One bad file must not abort the run —
    every later mod in the list still deploys and the summary still prints
    (review 2026-09-06)."""
    bad = wellformed(src, rels)
    if bad:
        print("  ! REFUSING TO DEPLOY: malformed XML")
        for rel, err in bad:
            print("  !   %s: %s" % (rel, err))
        print("  ! fix the file, then re-run. Nothing was copied for this mod.")
        return 0, True, []
    copied, failed = 0, []
    for rel in rels:
        target = os.path.join(dst, rel)
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(os.path.join(src, rel), target)
            copied += 1
        except OSError as e:
            failed.append((rel, str(e)))
            print("  ! FAILED to write %s: %s" % (rel, e))
    if failed:
        print("  ! %d file(s) NOT written for this mod (locked by the running "
              "game, or permissions). Nothing here is deployed until they are."
              % len(failed))
    return copied, False, failed


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
    ap.add_argument("--compose", choices=["biomes"],
                    help="build the composed 'RimMandrake: Baroque Biomes' mod from "
                         "src/RimMandrake/Biomes.compose.json into a temp dir and "
                         "plan/deploy THAT (instead of the per-mod folders)")
    ap.add_argument("--with", dest="with_mods", action="append", metavar="MOD",
                    help="with --compose: also plan/deploy this ordinary mod in the SAME "
                         "run, so the def guard judges both together (e.g. --compose "
                         "biomes --with SWBestiary after a creature moved between them)")
    args = ap.parse_args()
    if args.compose and (args.mod or args.pull):
        ap.error("--compose builds one target; it does not combine with --mod/--pull "
                 "(use --with MOD to deploy an ordinary mod alongside it)")
    if args.with_mods and not args.compose:
        ap.error("--with only combines with --compose; use --mod for ordinary mods")
    for n in (args.mod or []) + (args.with_mods or []) + ([args.pull] if args.pull else []):
        folded_refusal([n])

    mods_dir = first_existing(_MODS, "the RimWorld Mods folder")
    config = first_existing(_CONFIG, "ModsConfig.xml")
    active = active_ids(config)

    known_mods = mod_dirs()
    if args.pull:
        # Same guard --mod has: mod_dir() GUESSES a path for an unknown name,
        # so `--pull Core` or a typo would import an entire game folder into
        # the repo as a brand-new tree (review 2026-09-06).
        if args.pull not in known_mods:
            sys.exit("deploy_custom_mods.py: no such mod in the repo: %s\n"
                     "  known mods: %s" % (args.pull, ", ".join(sorted(known_mods))))
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
        pulled, refused, failed = copy(src, dst, new + changed)
        if refused or failed or pulled == 0:
            # copy() already printed its own "REFUSING TO DEPLOY: malformed
            # XML" — the likely case for --pull specifically, since its whole
            # purpose is rescuing a hand-edit made directly in the Mods
            # folder. Without this check nothing was actually copied and the
            # command still printed "done" and exited 0.
            print("nothing was pulled — fix the malformed file in the game copy and re-run.")
            return 1
        print("done — review with `git diff` before committing")
        return 0

    asked = (args.mod or []) + (args.with_mods or [])
    if asked:
        # mod_dir() falls back to a guessed path for an unknown name rather
        # than raising, so a typo'd --mod used to sail through: tree() on the
        # nonexistent guessed dir returns an empty set, `gone` becomes EVERY
        # deployed file for that name, and --apply --prune would delete the
        # entire deployed mod folder. Refuse before any of that can happen.
        unknown = [n for n in asked if n not in known_mods]
        if unknown:
            sys.exit("deploy_custom_mods.py: no such mod in the repo: %s\n"
                     "  known mods: %s" % (", ".join(unknown), ", ".join(sorted(known_mods))))
    holds = load_holds()
    compose_tmp = None
    if args.compose:
        print("compose: %s  (manifest %s)" % (args.compose, pretty(
            biomes_compose.manifest_path(SRC_ROOT))))
        try:
            cname, csrc, extra = biomes_compose.build(SRC_ROOT, tree, holds)
        except biomes_compose.ComposeError as e:
            sys.exit("deploy_custom_mods.py: REFUSING TO COMPOSE: %s" % e)
        compose_tmp = os.path.dirname(csrc)
        holds = holds + extra
        targets = [(cname, csrc)] + [(n, mod_dir(n)) for n in (args.with_mods or [])]
        args.compose_target = cname
        # A folded member's OWN packageId still active in ModsConfig loads that member a second time beside the
        # composed copy (its defs and types twice). EXPLOSIVE_GROWTH_MERGE_COMES_HOME folded a mod that was live
        # standalone; say so on every compose plan until the list is fixed. Never edits ModsConfig itself.
        twice = sorted(set(biomes_compose.folded_ids(SRC_ROOT)) & active)
        if twice:
            print("WARNING: folded into %s but STILL ACTIVE standalone in ModsConfig.xml: %s\n"
                  "  remove them from the mod list (and their old deployed folders) before the next load, or their "
                  "defs and types load twice." % (cname, ", ".join(twice)))
    else:
        names = args.mod or sorted(known_mods)
        targets = [(n, mod_dir(n)) for n in names]
    try:
        return _run(args, targets, holds, mods_dir, active)
    finally:
        for d in _STAGED:
            shutil.rmtree(d, ignore_errors=True)
        if compose_tmp:
            shutil.rmtree(compose_tmp, ignore_errors=True)


_STAGED = []


def _run(args, targets, holds, mods_dir, active):
    names = [n for n, _ in targets]
    print("repo : %s" % SRC_ROOT)
    print("game : %s" % mods_dir)
    print("mode : %s" % ("APPLY" if args.apply else "plan only (use --apply to write)"))
    print("holds: %d pattern(s) from %s"
          % (len(holds), pretty(HOLD_FILE)))
    print("skip : dirs %s · exts %s\n"
          % (" ".join(sorted(EXCLUDE_DIRS)), " ".join(sorted(EXCLUDE_EXTS))))

    # SWB_BIOMES_DEPLOY_GUARD_DUPLICATE_DEFS: judge the RESULTING game-copy mod
    # set before anything is written. --apply refuses; a plan says it would.
    guard_block = _def_guard(args, targets, holds, mods_dir)
    if guard_block and args.apply:
        print("REFUSING --apply: the game copy would carry %d def conflict(s) "
              "listed above. NOTHING WAS WRITTEN." % len(guard_block))
        return 1

    drift = False
    any_leftover = False   # apply-mode exit code; unlike `drift`, NEVER reset by a
                           # later mod's clean verify — see the return statement below.
    wrote = 0
    deployed = []          # (mod, files copied) for the telemetry `deploy` event
    for name, src in targets:
        dst = os.path.join(mods_dir, name)
        real_src = src
        # the composed temp folder is not a git tree and is never re-staged;
        # ordinary mods riding along with --compose (--with) are both.
        composed = name == getattr(args, "compose_target", None)
        if not composed:
            # ghost guards: MayRequire naming a folded packageId (see biomes_compose)
            fmap = biomes_compose.folded_ids(SRC_ROOT)
            nmap = biomes_compose.folded_names(SRC_ROOT)
            staged = biomes_compose.stage_rewritten(src, fmap, names=nmap) if (fmap or nmap) else None
            if staged:
                _STAGED.append(os.path.dirname(staged))
                src = staged
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
        # `same` too (DEPLOY_HOLD_SAME_BUCKET_BLIND_1): a file already deployed
        # byte-identical to the repo copy, deployed BEFORE a hold on it was
        # written, otherwise never appears in any of the three drift lists —
        # the plan reads "in sync" forever with no sign it is held at all.
        same, held_same = split_held(holds, name, same)
        held = held_new + held_changed + held_gone + held_same
        # Files the REPO deleted (git history) are stale deploys, not hand
        # edits: --apply prunes them without --prune. Hand-edits stay kept.
        stale = repo_deleted(real_src, gone) if not composed else composed_repo_deleted(gone)
        stale = {r for r in stale if inside(dst, r)}
        wt_gone = worktree_deleted(real_src, gone) if not composed else set()

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
                  % (len(same), ", %d held" % len(held) if held else ""))
            continue

        drift = True
        for r in new:
            print("    +  %s" % r)
        for r in changed:
            print("    ~  %s" % r)
        for r in gone:
            if r in stale:
                why = ("; deleted in repo -- %s" % ("will be pruned" if args.apply
                       else "--apply prunes it"))
            elif r in wt_gone:
                why = ("; deleted in repo working tree, UNCOMMITTED -- %s"
                       % ("will be deleted" if args.apply and args.prune
                          else "kept; commit the delete, or --prune"))
            elif args.apply and args.prune:
                why = "; will be deleted"
            else:
                why = "; kept — use --prune to delete, or --pull to rescue"
            print("    -  %s   (in game, not in repo%s)" % (r, why))

        if args.apply:
            # copy() returns 0 (having already printed its own refusal) rather
            # than the requested count when the source XML is malformed —
            # `wrote` must reflect what actually happened, not what was asked
            # for, or a refused deploy still prints "Deployed N file(s)."
            if pid is None:
                # SKILL §6: no About.xml packageId means not deployable — it
                # was a flag only and --apply deployed anyway (review 2026-09-06).
                print("  ! REFUSING TO DEPLOY: no packageId in About.xml. "
                      "Nothing was copied for this mod.")
                copied, refused, failed = 0, True, []
            else:
                copied, refused, failed = copy(src, dst, new + changed)
            wrote += copied
            if copied:
                deployed.append((name, copied))
            if refused or failed:
                any_leftover = True
            # Never prune after a refusal or a failed write: `gone` files are
            # by definition the hand-edits --pull exists to rescue, and a
            # refused copy is not a deploy to prune behind (review 2026-09-06).
            if (args.prune or stale) and not refused and not failed:
                # Mirrors copy()'s per-file OSError handling: a locked DLL or a
                # permissions error on os.remove() must not crash the whole run
                # mid-loop (which would skip every later mod's deploy and print
                # a raw traceback instead of this script's own "STILL DIFFERS"
                # report). The leftover file still shows up in g2 below, which
                # already sets any_leftover — this only stops the exception.
                pruned = 0
                for r in gone:
                    if not (args.prune or r in stale):
                        continue
                    if not inside(dst, r):
                        print("  ! REFUSING to delete %s: outside %s" % (r, dst))
                        continue
                    try:
                        os.remove(os.path.join(dst, r))
                        pruned += 1
                    except OSError as e:
                        print("  ! FAILED to delete %s: %s" % (r, e))
                wrote += pruned
            n2, c2, g2, _ = compare(src, dst)
            # Held files legitimately still differ after a deploy — that is the
            # whole point of holding them. Without this filter the verify step
            # reports "STILL DIFFERS" on a correct run, which trains people to
            # ignore the one line that proves the deploy worked.
            n2, _ = split_held(holds, name, n2)
            c2, _ = split_held(holds, name, c2)
            g2, _ = split_held(holds, name, g2)
            leftover = n2 + c2 + (g2 if args.prune else [r for r in g2 if r in stale])
            print("    -> %s" % ("VERIFIED in sync" if not leftover
                                 else "STILL DIFFERS: %s" % leftover))
            if not leftover:
                drift = False
            else:
                any_leftover = True
        print()

    # A hold that no longer matches anything is the same failure shape as a
    # stale instruction in a doc: still present, still read, no longer true —
    # and it silently stops protecting whatever it was written for. Only
    # meaningful on a full run; with --mod most patterns legitimately miss.
    if not args.mod and not args.compose:
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

    if guard_block:
        print("DEF GUARD: --apply of this plan would be REFUSED (%d conflict(s); "
              "see the top of this plan)." % len(guard_block))
    if args.apply and deployed:
        _emit_deploy(deployed, any_leftover)
    if args.apply and wrote:
        print("Deployed %d file(s). RESTART RIMWORLD — defs are only parsed at "
              "startup, so reloading a save will not pick these up." % wrote)
    elif args.apply and any_leftover:
        # wrote == 0 does NOT mean "nothing needed doing". copy() returns 0 after
        # printing its own malformed-XML refusal, so the old unconditional
        # "already in sync" printed a flat lie directly under the refusal — the
        # exact false-deployed shape this script exists to prevent.
        print("NOTHING WAS WRITTEN, and the repo and game still DIFFER — see the "
              "refusal(s) above. Fix them and re-run.")
    elif args.apply:
        print("Nothing to do; already in sync. No restart needed.")
    elif drift:
        print("Drift found. Re-run with --apply to deploy.")
    else:
        print("Everything in sync.")
    # `drift` is a single accumulator across every mod in the loop and gets
    # RESET by a later mod's clean verify (`drift = False` above) — reused
    # here for the plan-mode message, which is a per-run summary and fine as
    # a single flag, but wrong for the apply-mode exit code, which promises
    # "0 when repo and game agree" per this module's own docstring. Use the
    # accumulator that is never reset once any mod's post-deploy verify fails.
    return 1 if (any_leftover if args.apply else drift) else 0


def _fix_cmd(mods, prune, ctarget):
    """The one command that deploys `mods` together (composed target via --compose)."""
    base = "python3 src/RimMandrake/Utils/deploy_custom_mods.py"
    fold = folded()
    names = sorted({fold[m][0] if m in fold else m for m in mods})
    others = [m for m in names if m != ctarget]
    if ctarget in names:
        s = base + " --compose biomes" + "".join(" --with %s" % m for m in others)
    else:
        s = base + "".join(" --mod %s" % m for m in others)
    return s + " --apply" + (" --prune" if prune else "")


def _def_guard(args, targets, holds, mods_dir):
    """Cross-mod def check of the post-plan game copy (deploy_def_guard.py).
    Prints its findings; returns the BLOCKING ones (findings touching a target)."""
    import deploy_def_guard as G
    tnames = {n for n, _ in targets}
    try:
        man = biomes_compose.load_manifest(SRC_ROOT)
    except Exception:                                    # noqa: BLE001
        man = None
    ctarget = man["target"] if man else None
    post, pre, repo = {}, {}, {}
    known = set(mod_dirs()) | ({ctarget} if ctarget else set())
    full = (active_ids(FULL_LIST) or None) if os.path.isfile(FULL_LIST) else None
    dead = []
    if os.path.isdir(mods_dir):
        for n in sorted(os.listdir(mods_dir)):
            p = os.path.join(mods_dir, n)
            if n in tnames or not os.path.isdir(p):
                continue
            pid = (package_id(p) or "").lower()
            if pid.startswith("mandrake."):
                if full is not None and n not in known and pid not in full:
                    dead.append(n)              # orphan, never loads: out of scope
                    continue
                post[n] = G.xml_files(p)
    for n, src in targets:
        dst = os.path.join(mods_dir, n)
        s, d = G.xml_files(src), G.xml_files(dst)
        pre[n] = d
        held = G.held_fn(holds, n)
        gone = [r for r in d if r not in s and not held(r)]
        if args.prune:
            pruned = set(gone)
        elif n == getattr(args, "compose_target", None):
            pruned = {r.replace(os.sep, "/") for r in
                      composed_repo_deleted([g.replace("/", os.sep) for g in gone], man or {})}
        else:
            pruned = {r.replace(os.sep, "/") for r in
                      repo_deleted(src, [g.replace("/", os.sep) for g in gone])}
        post[n] = G.post_files(s, d, held, pruned)
    for n, p in mod_dirs().items():
        repo[n] = dict(G.def_files(G.xml_files(p)))
    if man:
        for e in biomes_compose.composed_entries(man):
            sdir = os.path.join(SRC_ROOT, biomes_compose.TIER_DIR, e["source"])
            pre_rel = biomes_compose.dest_rel(e) + "/"
            bucket = repo.setdefault(ctarget, {})
            for rel, p in G.def_files(G.xml_files(sdir)):
                bucket[pre_rel + rel] = p
    block, old = G.check(post, pre, tnames, repo,
                         lambda mods, prune: _fix_cmd(mods, prune, ctarget))
    print("def guard: %d mod(s) in the resulting game copy (mandrake.*), %d target(s): "
          "%s" % (len(post), len(tnames), "%d BLOCKING" % len(block) if block else "clean"))
    if dead:
        print("  (out of scope: %d orphan game folder(s) with no repo source, not on the "
              "owner's full list -- never load: %s)" % (len(dead), ", ".join(dead)))
    for m in block:
        print("  ! %s" % m)
    if old:
        print("  (%d PRE-EXISTING conflict(s) not touching this plan's mods; not blocking)"
              % len(old))
        for m in old[:20]:
            print("    . %s" % m)
        if len(old) > 20:
            print("    . ... %d more" % (len(old) - 20))
    print()
    return block


def _emit_deploy(deployed, leftover):
    """Telemetry change event (TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED); never fails the deploy."""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "telemetry"))
        from telemetry_emit import emit_change, git_head
        emit_change("deploy", ",".join(m for m, _ in deployed)[:200], sha=git_head(os.path.dirname(os.path.abspath(__file__))),
                    detail={"mods": dict(deployed), "leftover": bool(leftover), "tool": "deploy_custom_mods.py"})
    except Exception:  # noqa: BLE001
        pass


if __name__ == "__main__":
    sys.exit(main())
