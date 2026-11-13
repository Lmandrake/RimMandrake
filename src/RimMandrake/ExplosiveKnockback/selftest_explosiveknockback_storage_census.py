#!/usr/bin/env python3
"""Storage census: every storage building def is CLOSED exactly when it hides its contents (RIMMANDRAKE_CENSUS_KNOCKBACK_STORAGE_OPEN_CLOSED).

Owner 2026-11-12 (OWNER:1794529787425697771): "Anything that draws its contents is open ... a shelf should be ruled as
open, period." Scene sc_closed_containers start[5] asserts this census passed.

Inputs: the owner's full def dump (defs.sqlite, read through its tables, never a text scan) for every def body, and
this repo's XML for the opt-in tag RM_KnockbackClosedStorage (the dump can predate a patch; the repo is what deploys).

  READ   the mirror of RM_KnockbackCompat.IsClosedContainer: closed = the tag, or a comp/extension with a bool
         `showContents` false, or a RimWorld.Building_Crate (vanillaCratesClosed ships on).
  HIDES  independent of the tag: `showContents` false (LWM's Deep Storage), an AdaptiveStorage.GraphicsDef with
         showContainedItems false naming the def, or a sealed crate (contents in a ThingOwner, never drawn).
  DRAWS  a storage class that lays its goods out on its cells (Building_Storage, RimFridge, AdaptiveStorage) that
         does not hide.
  C1  every def that HIDES reads closed          C2  every def that DRAWS reads open
  C3  Shelf, ShelfSmall, Hopper, Cold Storage's three stasis lockers and the crock read open
  C4  LWM_WeaponsLocker and SealedCrate read closed
  C5  the C# rule is the one mirrored here (a fingerprint of IsClosedContainer + AnyHides; edit both together)
Sanity first: under 40 drawing defs, or a named def missing, is UNMEASURED, never a pass.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_storage_census.py
        [--at <sha>]           read the repo's tags as of that commit (watch it fail on 6485aafec2^, the closed-tagged lockers)
        [--plant-tag <def>]    mutant: tag one more def; a drawing def must go red
        [--table <path>]       write every storage def's reading
"""
import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
import game_paths  # noqa: E402

UNMEASURED = "UNMEASURED, not a pass or a fail"
TAG = "RM_KnockbackClosedStorage"
COMPAT = os.path.join(HERE, "Source", "RM_KnockbackCompat.cs")
RULE_FINGERPRINT = "d94c5ac06238"  # IsClosedContainer, IsClosedDef + AnyHides as reviewed 2026-11-13; see C5
DRAWING_CLASSES = {"RimWorld.Building_Storage", "RimFridge.RimFridge_Building",
                   "RimFridge.RimFridge_MultiSidedWallBuilding", "AdaptiveStorage.ThingClass"}
CRATE = "RimWorld.Building_Crate"
MUST_OPEN = ["Shelf", "ShelfSmall", "Hopper", "RM_AncientStasisLocker_Kludged", "RM_AncientStasisLocker_Refurbished",
             "RM_AncientStasisLocker_Original", "RM_EvaporativeCrock"]
MUST_CLOSED = ["LWM_WeaponsLocker", "SealedCrate"]


def rule_fingerprint():
    src = open(COMPAT, encoding="utf-8").read()
    a = src.index("public static bool IsClosedContainer")
    b = src.index("/// <summary>Dig a cell to superdeep")
    body = re.sub(r"#if RM_PROOFS.*?#endif", "", src[a:b], flags=re.S)
    body = re.sub(r"//[^\n]*", "", body)
    return hashlib.sha256(re.sub(r"\s+", "", body).encode()).hexdigest()[:12]


def repo_xml(at):
    """(path, text) of every src XML that names the tag, at a commit or in the worktree."""
    if at:
        out = subprocess.run(["git", "-C", REPO, "grep", "-l", TAG, at, "--", "src/*.xml"],
                             capture_output=True, text=True).stdout.split()
        for ref in out:
            yield ref, subprocess.run(["git", "-C", REPO, "show", ref], capture_output=True, text=True).stdout
        return
    for root, _dirs, files in os.walk(os.path.join(REPO, "src")):
        for f in files:
            if f.endswith(".xml"):
                p = os.path.join(root, f)
                try:
                    t = open(p, encoding="utf-8-sig").read()
                except (UnicodeDecodeError, OSError):
                    continue
                if TAG in t:
                    yield p, t


def tagged_defs(at):
    """defName -> source file, for every def the repo tags. An xpath with no defName literal is an error, not a skip."""
    tagged, errors = {}, []
    for path, text in repo_xml(at):
        root = ET.fromstring(text)
        for el in root.iter():
            cls = el.get("Class", "")
            if cls.endswith("RM_KnockbackClosedStorage"):
                continue
            if "AddModExtension" in cls and TAG in ET.tostring(el, encoding="unicode"):
                xp = el.findtext("xpath") or ""
                names = re.findall(r'defName\s*=\s*"([^"]+)"', xp)
                if not names:
                    errors.append(f"{path}: an AddModExtension of the tag has no defName literal in its xpath: {xp!r}")
                for n in names:
                    tagged[n] = path
            if el.tag == "ThingDef" and el.findtext("defName"):
                for li in el.findall("./modExtensions/li"):
                    if li.get("Class", "").endswith(TAG):
                        tagged[el.findtext("defName")] = path
    return tagged, errors


def census(db, tagged):
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    hidden_by_graphics = set()
    for (js,) in c.execute("select json from defs where full_name='AdaptiveStorage.GraphicsDef'"):
        f = json.loads(js)["fields"]
        if f.get("showContainedItems") is False:
            hidden_by_graphics.update(f.get("targetDefs") or [])
    rows = {}
    for name, mod, js in c.execute("select def_name, mod_name, json from defs where def_type='ThingDef'"):
        f = json.loads(js)["fields"]
        if f.get("category") != "Building":
            continue
        tc = f.get("thingClass") or ""
        storage = (f.get("building") or {}).get("fixedStorageSettings") is not None or tc in DRAWING_CLASSES or tc == CRATE
        if not storage:
            continue
        exts = [x for x in (f.get("comps") or []) + (f.get("modExtensions") or []) if isinstance(x, dict)]
        show_false = any(x.get("showContents") is False for x in exts)
        dump_tag = any(str(x.get("$type", "")).endswith(TAG) for x in exts)
        tag = name in tagged or dump_tag
        closed = tag or show_false or tc == CRATE
        hides = show_false or name in hidden_by_graphics or tc == CRATE
        draws = tc in DRAWING_CLASSES and not hides
        why = ("tag " if tag else "") + ("showContents=false " if show_false else "") + \
              ("showContainedItems=false " if name in hidden_by_graphics else "") + ("sealed crate" if tc == CRATE else "")
        rows[name] = dict(mod=mod, cls=tc, closed=closed, hides=hides, draws=draws, why=why.strip())
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--at")
    ap.add_argument("--plant-tag", action="append", default=[])
    ap.add_argument("--table")
    a = ap.parse_args()
    db = os.path.join(game_paths.DUMP_ROOT, "defs.sqlite")
    if not os.path.exists(db):
        print(f"{UNMEASURED}: no def dump database at {db}")
        return 0
    tagged, errors = tagged_defs(a.at)
    for n in a.plant_tag:
        tagged[n] = "planted"
    rows = census(db, tagged)
    draws = [n for n, r in rows.items() if r["draws"]]
    missing = [n for n in MUST_OPEN + MUST_CLOSED if n not in rows]
    if len(draws) < 40 or missing:
        print(f"{UNMEASURED}: blind census ({len(rows)} storage defs, {len(draws)} drawing; missing {missing})")
        return 0
    fails = list(errors)
    fails += [f"C1 {n} hides its contents ({r['why']}) but reads OPEN" for n, r in sorted(rows.items()) if r["hides"] and not r["closed"]]
    fails += [f"C2 {n} draws its contents ({r['cls']}) but reads CLOSED ({r['why']})" for n, r in sorted(rows.items()) if r["draws"] and r["closed"]]
    fails += [f"C3 {n} must read open, reads CLOSED ({rows[n]['why']})" for n in MUST_OPEN if rows[n]["closed"]]
    fails += [f"C4 {n} must read closed, reads OPEN" for n in MUST_CLOSED if not rows[n]["closed"]]
    fp = rule_fingerprint()
    if fp != RULE_FINGERPRINT:
        fails.append(f"C5 RM_KnockbackCompat.IsClosedContainer changed (fingerprint {fp}, mirrored {RULE_FINGERPRINT}): "
                     "update this census's READ rule, then the constant")
    for n in sorted(set(tagged) - set(rows)):
        if tagged[n] != "planted":
            print(f"note: tagged def {n} ({tagged[n]}) is not a storage building in the dump")
    if a.table:
        with open(a.table, "w", encoding="utf-8") as fh:
            fh.write("defName\tmod\tthingClass\treads\thides\tdraws\twhy\n")
            for n, r in sorted(rows.items()):
                fh.write(f"{n}\t{r['mod']}\t{r['cls']}\t{'closed' if r['closed'] else 'open'}\t{r['hides']}\t{r['draws']}\t{r['why']}\n")
    closed = sum(r["closed"] for r in rows.values())
    print(f"census: {len(rows)} storage defs, {closed} closed, {len(draws)} drawing, {len(tagged)} tagged in repo"
          + (f" at {a.at}" if a.at else ""))
    for f in fails:
        print("FAIL", f)
    if fails:
        return 1
    print("PASS storage census: closed exactly when hidden")
    return 0


if __name__ == "__main__":
    sys.exit(main())
