#!/usr/bin/env python3
"""Offline proof for RIMMANDRAKE_MAKE_GRATH_ELDER_CLICKABLE_ROOT_CELL_BELOW_ITS_PICTURE: a click on a Rot giant's
body selects it, in every mod list that loads the Rot.

Owner, 2026-11-23: "I think it is this giant mushroom thing, but I can't tell you what it is because it's root cell
is somewhere strange. Without the HugeThings mod, it's kind of unclickable."

The engine gives a plant one cell. A Rot giant (drawn 6+ cells wide, e.g. RM_AgariluxPrime, the grath elder, 20
wide) is drawn far from that cell. Huge Things (mandrake.rm.hugethings) widens the selection rect to the whole
picture, through the RM_HugePlantExtension that Patches/RotGiants_HugeFootprint.xml adds under
MayRequire="mandrake.rm.hugethings". Without Huge Things in the list, that extension is dropped and the body is
not clickable. So the promise holds only if Huge Things is ALWAYS in a list that loads the Rot:

  1. every Rot giant is selectable and carries the guarded extension (the picture rect itself is
     selftest_hugethings_footprint.py's promise, not re-proved here);
  2. the Rot's About.xml hard-depends on mandrake.rm.hugethings;
  3. the Rot is composed into mandrake.rm.biomes, whose About.xml is GENERATED (biomes_compose.union_about):
     the generated About carries that dependency, and no composed member declares Huge Things incompatible;
  4. Huge Things loads before the mod that ships the Rot (its CustomRectForSelector patch must exist when the
     giants' defs resolve their extension type).

A sanity probe strips the dependency from a copy of the Rot's About and confirms check 2/3 go red.
"""
import copy
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SRC = REPO / "src"
sys.path.insert(0, str(SRC / "RimMandrake" / "Utils"))
sys.path.insert(0, str(SRC / "RimMandrake" / "HugeThings"))

import biomes_compose as bc  # noqa: E402
import measure_huge_plant_masks as mhpm  # noqa: E402

HUGE = "mandrake.rm.hugethings"
ROT_ABOUT = HERE / "About" / "About.xml"
HUGE_ABOUT = SRC / "RimMandrake" / "HugeThings" / "About" / "About.xml"
PATCH = HERE / "Patches" / "RotGiants_HugeFootprint.xml"


def ids(about, field):
    node = about.find(field)
    if node is None:
        return set()
    return {bc._li_id(field, li) for li in node.findall("li")}


def composed_about(rot_about=None):
    """The generated mandrake.rm.biomes About, built the way build() builds it. rot_about replaces the Rot's."""
    m = bc.load_manifest(str(SRC))
    abouts, drop = [], {m["about"]["packageId"].lower()}
    rot_key = None
    for e in bc.composed_entries(m):
        ab = ET.parse(SRC / "RimMandrake" / e["source"] / "About" / "About.xml").getroot()
        if e["source"] == "TheRot":
            rot_key = e["key"]
            if rot_about is not None:
                ab = rot_about
        drop.add((ab.findtext("packageId") or "").strip().lower())
        abouts.append((e["key"], ab))
    drop |= {(p or "").strip().lower() for p in m.get("absorbed", ())} - {""}
    root, _ = bc.union_about(abouts, drop, m)
    return root, rot_key, drop, m["about"]["packageId"].lower()


def about_fails(rot_about):
    fails = []
    if HUGE not in ids(rot_about, "modDependencies"):
        fails.append(f"TheRot About.xml: {HUGE} is not in <modDependencies>; a list without it loads the Rot's "
                     f"giants with a one-cell click target")
    root, rot_key, drop, target = composed_about(rot_about)
    if rot_key is None:
        return fails  # the Rot ships standalone: check 2 is the whole requirement
    if HUGE in drop:
        fails.append(f"{HUGE} is folded into {target}; its packageId is dropped from every list")
    if HUGE not in ids(root, "modDependencies"):
        fails.append(f"generated {target} About.xml: {HUGE} is not in <modDependencies>")
    if HUGE in ids(root, "incompatibleWith"):
        fails.append(f"generated {target} About.xml lists {HUGE} as incompatible")
    return fails


def main():
    fails = []
    # 1. every Rot giant is selectable and carries the guarded extension
    giants = sorted(p["def"] for p in mhpm.giants())
    if "RM_AgariluxPrime" not in giants:
        fails.append(f"sanity: RM_AgariluxPrime not among the giants the generator sees ({giants})")
    patched = {}
    for op in ET.parse(PATCH).getroot().iter("Operation"):
        xp = op.findtext("xpath") or ""
        for li in op.iter("li"):
            if li.get("Class") == "RimMandrake.HugeThings.RM_HugePlantExtension":
                dn = xp.split('defName="')[1].split('"')[0]
                patched[dn] = li.get("MayRequire")
    defs = {}
    for p in (HERE / "Defs").rglob("*.xml"):
        for d in ET.parse(p).getroot().iter("ThingDef"):
            dn = (d.findtext("defName") or "").strip()
            if dn:
                defs[dn] = d
    for g in giants:
        if g not in patched:
            fails.append(f"{g}: no RM_HugePlantExtension in {PATCH.name}")
        sel = (defs[g].findtext("selectable") or "").strip().lower() if g in defs else ""
        if sel != "true":
            fails.append(f"{g}: own <selectable> is {sel or 'unset'}, want true")
    print(f"giants: {len(giants)} ({', '.join(giants)}); extension on {len(patched)}")

    # 2 + 3. Huge Things is in every list that loads the Rot
    rot_about = ET.parse(ROT_ABOUT).getroot()
    fails += about_fails(rot_about)

    # 4. Huge Things loads before the mod that ships the Rot
    root, rot_key, _, target = composed_about()
    shipper = target if rot_key else (rot_about.findtext("packageId") or "").strip().lower()
    huge_about = ET.parse(HUGE_ABOUT).getroot()
    shipper_about = root if rot_key else rot_about
    if shipper not in ids(huge_about, "loadBefore") and HUGE not in ids(shipper_about, "loadAfter"):
        fails.append(f"no load order puts {HUGE} before {shipper}")

    # sanity: the instrument goes red with the dependency stripped
    broken = copy.deepcopy(rot_about)
    md = broken.find("modDependencies")
    if md is not None:
        for li in list(md.findall("li")):
            if bc._li_id("modDependencies", li) == HUGE:
                md.remove(li)
    if not about_fails(broken):
        fails.append("sanity: the About check stayed green with the Huge Things dependency stripped")

    for f in fails:
        print("FAIL:", f)
    print("PASS" if not fails else f"{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
