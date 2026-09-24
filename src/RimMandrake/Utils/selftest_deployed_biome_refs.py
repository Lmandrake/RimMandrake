#!/usr/bin/env python3
# selftest-timeout: 720   # walks every deployed mod on the drvfs mount; 367 s measured 2026-09-23
"""
selftest_deployed_biome_refs.py

Invariant under test: a biome table and the species it names can never ship
apart. UtinniPatches' BiomeDefs list wildAnimals/wildPlants defNames; every
one of those defNames must resolve to a concrete ThingDef that is ACTUALLY
DEPLOYED under the Steam Mods folder (or shipped in vanilla Core/DLC Data),
not merely present in this repo.

Why: a biome table was deployed naming species defs that were NOT deployed
alongside it. 18 refs dangled in the live game. Every existing check resolved
refs against the REPO, where everything is consistent, so it was invisible.

Note on shape: wildAnimals/wildPlants are XML dictionaries, not <li> lists --
each entry is <SomeDefName MayRequire="...">commonality</SomeDefName>, and
the TAG NAME is the defName. MayRequire="<packageId>" on an entry does NOT
save it from this check -- that attribute only tests whether the MOD IS
ACTIVE, not whether the DEF IS PRESENT in the deployed copy of that mod. A
stale deployed build of an active mod passes every existing guard and still
dangles at runtime. So MayRequire is never treated as a reason to skip an
entry here.

PRIMARY assertion (fails the test): every wildAnimals/wildPlants defName in
the DEPLOYED UtinniPatches BiomeDefs must resolve to a defName defined
somewhere under the deployed Mods root, or under vanilla Core/DLC Data.

SECONDARY (warning only, never fails the test): the same resolution run
against the REPO's BiomeDefs, checked against the same deployed defName
universe. Printed as WOULD-FAIL-ON-DEPLOY lines. This is a warning because
the repo currently and intentionally names ~18 RSW_* defs belonging to a mod
(SWBestiary) that is deliberately held from deploy -- a red suite here would
block every commit in a shared tree.

If the deployed Mods root does not exist (this repo is also used from a Mac),
prints exactly:
    UNMEASURED, not a pass or a fail
with a one-line reason, and exits 0.

Run: bare `python3 selftest_deployed_biome_refs.py`, stdlib only, no args.
"""

import glob
import json
import os
import subprocess
import tempfile
import re
import sys
import time

STEAM_MODS_ROOT = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
STEAM_DATA_ROOT = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
# 🔴 The owner's stack is ~618 mods and only ~120 of them sit in Mods/. The rest
# are Steam Workshop subscriptions, which the game loads from a completely
# separate root. Resolving against Mods+Data alone reports ~339 dangling refs,
# 100% of them false -- MEASURED 2026-09-20, the first run of this file.
STEAM_WORKSHOP_ROOT = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
REPO_UTINNI_PATCHES_ABOUT = "/mnt/d/Luke/dev/Rimworld/src/RimUtinni/UtinniPatches/About/About.xml"
REPO_BIOME_DEFS_GLOB = "/mnt/d/Luke/dev/Rimworld/src/RimUtinni/UtinniPatches/Defs/BiomeDefs/*.xml"

class WorkshopScanFailed(Exception):
    """Raised when the Workshop root cannot be scanned at all (grep timed out
    or errored, or the root could not be listed) -- as opposed to scanning it
    cleanly and finding zero defNames. The two used to be indistinguishable:
    both returned an empty set from _scan_workshop_fast(), silently shrinking
    the whole defName universe by ~75k names and turning every real reference
    into every mod under Workshop into an UNRESOLVED false positive. MEASURED
    2026-09-24: one grep timeout produced a confident "FAIL: 304 deployed
    reference(s) dangle" against a universe of 17280 defNames; a clean rerun
    (same content, cache warm) found universe 90054 and 0 unresolved -- a
    silent-empty-set instrument lying with a number, the exact class this
    project's CLAUDE.md exists to catch."""


DEFNAME_RE = re.compile(r"<defName>\s*([^<\s]+)\s*</defName>")
PACKAGEID_RE = re.compile(r"<packageId>\s*([^<\s]+)\s*</packageId>")
# Matches one opening XML element tag, capturing (tagName, rawAttrs).
# Closing tags (</x>) never match -- '/' is not in the tag-name class.
ELEMENT_OPEN_RE = re.compile(r"<([A-Za-z_][\w.]*)\b([^>]*)>")


def find_deployed_mod_dir(mods_root, want_package_id):
    """Return the deployed mod folder under mods_root whose About.xml
    packageId matches want_package_id, or None. Never hardcode a folder
    name -- packageId is the only identity that survives a rename."""
    try:
        entries = sorted(os.scandir(mods_root), key=lambda e: e.name)
    except OSError:
        return None
    for entry in entries:
        if not entry.is_dir():
            continue
        about = os.path.join(entry.path, "About", "About.xml")
        if not os.path.isfile(about):
            continue
        try:
            with open(about, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        m = PACKAGEID_RE.search(text)
        if m and m.group(1) == want_package_id:
            return entry.path
    return None


def _scan_root_careful(root):
    """Per-file read with comments stripped, so a commented-out <defName>
    cannot falsely resolve a dangling reference. Used for the Mods and Data
    roots -- ~120 folders, where OUR content lives and where this test's
    whole bug class (our biome table naming our undeployed def) occurs.
    """
    names = set()
    pattern = os.path.join(root, "**", "Defs", "**", "*.xml")
    for path in glob.iglob(pattern, recursive=True):
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
        for m in DEFNAME_RE.finditer(text):
            names.add(m.group(1))
    return names


def _scan_workshop_fast(root):
    """One `grep -r` subprocess over the Workshop root instead of ~75k
    per-file opens.

    🔴 Why this is a different function from the careful scan above.
    MEASURED 2026-09-20 on drvfs: the per-file Python scan of this root did
    not finish inside 600s; a single grep does it in ~146s. The trade is that
    comments are NOT stripped, so a commented-out <defName> in a third-party
    mod can falsely satisfy a reference. That is accepted HERE and only here:
    this root holds donor content we did not write, it is consulted only to
    answer "does this donor def exist at all", and a false PRESENT merely
    fails to flag a donor mod's own problem. A false present in OUR content
    would hide the actual bug, which is why Mods/Data keep the careful path.

    Cached in /tmp (a program reads it, not a human -- never the repo) keyed
    by entry count + newest top-level mtime, so only a Workshop change pays
    the scan again.
    """
    try:
        entries = list(os.scandir(root))
        key = "%d:%d" % (len(entries), int(max((e.stat().st_mtime for e in entries), default=0)))
    except OSError as exc:
        raise WorkshopScanFailed("could not list %s: %r" % (root, exc)) from exc

    cache = os.path.join(tempfile.gettempdir(), "rimworld_workshop_defnames.json")
    try:
        with open(cache, encoding="utf-8") as fh:
            blob = json.load(fh)
        if blob.get("key") == key:
            return set(blob["names"])
    except (OSError, ValueError, KeyError):
        pass

    try:
        out = subprocess.run(
            ["grep", "-rhoE", "<defName>[^<]+</defName>", root, "--include=*.xml"],
            capture_output=True, text=True, timeout=400,
        ).stdout
    except subprocess.TimeoutExpired as exc:
        raise WorkshopScanFailed(
            "grep over %s did not finish inside 400s -- the universe cannot "
            "be trusted incomplete, this must not silently read as zero "
            "Workshop defNames" % root) from exc
    except OSError as exc:
        raise WorkshopScanFailed("grep over %s failed: %r" % (root, exc)) from exc

    names = {line[len("<defName>"):-len("</defName>")]
             for line in out.splitlines() if line.startswith("<defName>")}
    try:
        with open(cache, "w", encoding="utf-8") as fh:
            json.dump({"key": key, "names": sorted(names)}, fh)
    except OSError:
        pass
    return names


def build_defname_universe(roots):
    """The set of every concrete <defName> reachable by the running game.

    🔴 Three roots, not two. The owner's stack is ~618 mods and only ~120 of
    them sit in Mods/; the rest are Steam Workshop subscriptions under a
    wholly separate root. Resolving against Mods+Data alone reported 339
    dangling refs, 100% of them false -- MEASURED 2026-09-20 on this file's
    own first run, against an item whose real figure was 18.
    """
    names = set()
    for root in roots:
        if root == STEAM_WORKSHOP_ROOT:
            names |= _scan_workshop_fast(root)
        else:
            names |= _scan_root_careful(root)
    return names


def extract_species_refs(xml_path):
    """Return [(defName, section, mayrequire_or_None), ...] for every
    child element found inside a <wildAnimals> or <wildPlants> block in
    xml_path. The tag name itself IS the defName -- BiomeDef's
    wildAnimals/wildPlants are XML dictionaries (<RSW_Bantha>0.8</...>),
    not <li> lists.

    🔴 Comments are stripped from the WHOLE FILE before the block regex runs,
    not from inside each matched block. Stripping inside the block is not
    enough and was a real defect: RUT_PropaneLake.xml carries a 92-line
    comment that mentions `<wildAnimals />`, the block regex matched from
    that mention to the REAL closing tag 55 lines later, and the per-block
    strip found no opening `<!--` to anchor on. Every tag in between --
    `defName`, `label`, `texture` -- was then reported as a dangling animal.
    17 false failures, MEASURED 2026-09-20."""
    try:
        with open(xml_path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return []
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    refs = []
    for section in ("wildAnimals", "wildPlants"):
        block_re = re.compile(
            r"<" + section + r"\b[^>]*>(.*?)</" + section + r">", re.DOTALL)
        for block_match in block_re.finditer(text):
            for m in ELEMENT_OPEN_RE.finditer(block_match.group(1)):
                name, attrs = m.group(1), m.group(2)
                mr = re.search(r'MayRequire\s*=\s*"([^"]*)"', attrs)
                refs.append((name, section, mr.group(1) if mr else None))
    return refs


def check_refs(biome_files, universe):
    """Return (total_entries, unresolved) where unresolved is a list of
    (defName, section, mayrequire, basename)."""
    total = 0
    unresolved = []
    for path in biome_files:
        base = os.path.basename(path)
        for name, section, mayrequire in extract_species_refs(path):
            total += 1
            if name not in universe:
                unresolved.append((name, section, mayrequire, base))
    return total, unresolved


def main():
    start = time.time()

    if not os.path.isdir(STEAM_MODS_ROOT):
        print("UNMEASURED, not a pass or a fail")
        print("reason: deployed Mods root not found (%s) -- this checkout "
              "is not on the machine that runs the game." % STEAM_MODS_ROOT)
        return 0

    with open(REPO_UTINNI_PATCHES_ABOUT, encoding="utf-8", errors="replace") as fh:
        repo_about = fh.read()
    m = PACKAGEID_RE.search(repo_about)
    if not m:
        print("UNMEASURED, not a pass or a fail")
        print("reason: could not read packageId out of %s" % REPO_UTINNI_PATCHES_ABOUT)
        return 0
    want_package_id = m.group(1)

    deployed_mod_dir = find_deployed_mod_dir(STEAM_MODS_ROOT, want_package_id)
    if deployed_mod_dir is None:
        print("UNMEASURED, not a pass or a fail")
        print("reason: no deployed mod under %s carries packageId %s"
              % (STEAM_MODS_ROOT, want_package_id))
        return 0

    deployed_biome_dir = os.path.join(deployed_mod_dir, "Defs", "BiomeDefs")
    deployed_biome_files = sorted(glob.glob(os.path.join(deployed_biome_dir, "*.xml")))
    if not deployed_biome_files:
        print("UNMEASURED, not a pass or a fail")
        print("reason: no BiomeDefs XML found under deployed %s" % deployed_biome_dir)
        return 0

    resolution_roots = [STEAM_MODS_ROOT, STEAM_DATA_ROOT]
    if os.path.isdir(STEAM_WORKSHOP_ROOT):
        resolution_roots.append(STEAM_WORKSHOP_ROOT)
    else:
        print("UNMEASURED, not a pass or a fail")
        print("reason: Steam Workshop root %s is absent, so ~500 of the active\n         mods cannot be resolved and every ref into them would read as dangling."
              % STEAM_WORKSHOP_ROOT)
        return 0
    try:
        universe = build_defname_universe(resolution_roots)
    except WorkshopScanFailed as exc:
        print("UNMEASURED, not a pass or a fail")
        print("reason: Workshop defName scan failed (%s) -- refusing to "
              "resolve against a silently-shrunk universe, which would read "
              "every reference into an unscanned Workshop mod as dangling. "
              "Re-run once the scan can complete (a warm /tmp cache makes "
              "this instant)." % exc)
        return 0

    # PRIMARY: deployed biome files against the deployed defName universe.
    total, unresolved = check_refs(deployed_biome_files, universe)

    print("--- PRIMARY: deployed UtinniPatches BiomeDefs vs deployed defName universe ---")
    print("deployed mod dir: %s" % deployed_mod_dir)
    print("defName universe size: %d (from %d roots: %s)"
          % (len(universe), len(resolution_roots), ", ".join(resolution_roots)))
    print("deployed wildAnimals/wildPlants entries checked: %d" % total)
    print("unresolved: %d" % len(unresolved))
    for name, section, mayrequire, base in unresolved:
        tag = " (MayRequire=%s)" % mayrequire if mayrequire else ""
        print("  %s <- %s%s" % (name, base, tag))

    # SECONDARY, warning only: repo biome files against the SAME deployed
    # universe. Never affects the exit code -- see module docstring.
    repo_biome_files = sorted(glob.glob(REPO_BIOME_DEFS_GLOB))
    repo_total, repo_unresolved = check_refs(repo_biome_files, universe)
    print("\n--- SECONDARY (warning only): repo BiomeDefs vs deployed defName universe ---")
    print("repo wildAnimals/wildPlants entries checked: %d" % repo_total)
    print("WOULD-FAIL-ON-DEPLOY: %d" % len(repo_unresolved))
    # A bare count is not actionable and is how a warning gets ignored --
    # name every row, the same way the primary failure does.
    for name, section, mayrequire, base in repo_unresolved:
        tag = " (MayRequire=%s)" % mayrequire if mayrequire else ""
        print("  %s <- %s [%s]%s" % (name, base, section, tag))

    elapsed = time.time() - start
    print("\nruntime: %.1fs" % elapsed)

    if unresolved:
        print("\nFAIL: %d deployed reference(s) dangle -- named by the biome "
              "table but not present in any deployed mod folder or vanilla "
              "Data folder." % len(unresolved))
        return 1

    print("\nPASS: every deployed wildAnimals/wildPlants reference resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
