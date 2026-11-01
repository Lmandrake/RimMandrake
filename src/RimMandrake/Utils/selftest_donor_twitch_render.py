#!/usr/bin/env python3
"""Offline check: the three creatures the owner picked "rebuild" for keep their limb motion in our own code
(DONOR_CODE_SHAPE_REBUILD_1; design/RimMandrake/tentacle_twitch_design_2026-10-15.md).

Static, no game. Goes red when:
  * RM_ColossalAerofleet or RM_OcularJelly stops naming its Spastic tree, or that tree stops being loaded from Defs/;
  * a life stage's body stops being the bell (the feelers would double up with the whole-body picture);
  * a tree's piece or bell lacks a south, east or north picture (Graphic_Multi draws pink), or a root leaves the
    top centre of its canvas (the art contract the pivot relies on);
  * a bell carries a detached piece beyond what its case allows, or one the whole-body picture does not have there
    (the bulloo's free-floating islands are its escort bulloos, named in the design table and the race description;
    an island off that silhouette is a stray or a split leftover);
  * a piece names a body-part group the creature lacks (CanDrawNow would hide it for good);
  * the zhool's life-stage subworker leaves its tree or the committed DLL;
  * RM_Mantrap stops using the RM_Lastvine rearing tree, or the Staged wiring comes back;
  * any def of ours uses the donor's SpasticScaled class.
The rules run on mutated copies too, so a blind parser cannot pass.

    python3 src/RimMandrake/Utils/selftest_donor_twitch_render.py
"""
import glob
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
RM = os.path.join(ROOT, "src", "RimMandrake")
FACES = ("south", "east", "north")
SUBWORKER = "RimMandrake.EnvironmentalHazards.PawnRenderSubWorker_KindLifeStageScale"
# A piece may start this far down its canvas: the root sits behind the bell (layer -5/-6), so the bell hides the gap.
TOP_SLACK = 0.16
# A bell island: at most this many opaque pixels of the 256 canvas, at least this share on the whole-body silhouette
# (the bell is a re-render of the whole picture, so the two never register exactly; measured low 0.73).
ALPHA_SOLID = 40
ISLAND_MAX_PX = 1500
ISLAND_MIN_COVER = 0.7
HAZARD_DLL = "EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll"

CASES = [
    {"mod": "TheForge", "race_file": "Defs/ThingDefs_Races/RM_ColossalAerofleet.xml", "race": "RM_ColossalAerofleet",
     "tree": "RM_ColossalAerofleet_Twitch", "bell": "Things/Pawn/Animal/RM_ColossalAerofleet/RM_ColossalAerofleet_Bell",
     "body_file": "Defs/ThingDefs_Races/RM_Bulloo.xml", "body": "RM_JellyfishBody", "stages": 1, "subworker": False,
     "whole": "Things/Pawn/Animal/RM_ColossalAerofleet/RM_ColossalAerofleet", "islands": {"south": 0, "east": 2, "north": 3}},
    {"mod": "Contagion", "race_file": "Defs/ThingDefs_Races/RM_ContagionBulloos.xml", "race": "RM_OcularJelly",
     "tree": "RM_OcularJelly_Twitch", "bell": "Things/Pawn/Animal/RM_OcularJelly/RM_OcularJelly_Bell",
     "body_file": "Defs/Bodies/RM_BullooBodies.xml", "body": "RM_ZhoolBody", "stages": 3, "subworker": True,
     "whole": "Things/Pawn/Animal/RM_OcularJelly/RM_OcularJelly", "islands": {"south": 0, "east": 0, "north": 0}},
]


def by_name(root, tag, name):
    for d in root.iter(tag):
        if d.findtext("defName") == name:
            return d
    return None


def islands(mask):
    """Every 8-connected piece of a boolean mask but the largest, as boolean masks."""
    seen = np.zeros(mask.shape, bool)
    pieces = []
    for start in zip(*np.nonzero(mask)):
        if seen[start]:
            continue
        seen[start] = True
        stack, cells = [start], []
        while stack:
            y, x = stack.pop()
            cells.append((y, x))
            for ny in range(max(y - 1, 0), min(y + 2, mask.shape[0])):
                for nx in range(max(x - 1, 0), min(x + 2, mask.shape[1])):
                    if mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        pieces.append(cells)
    pieces.sort(key=len, reverse=True)
    out = []
    for cells in pieces[1:]:
        m = np.zeros(mask.shape, bool)
        m[tuple(zip(*cells))] = True
        out.append(m)
    return out


def check_bell_alpha(case, face, bell, whole):
    """Rules over one facing's bell and whole-body alpha channels (uint8 arrays); returns findings."""
    out = []
    found = islands(bell > ALPHA_SOLID)
    allowed = case["islands"][face]
    if len(found) != allowed:
        out.append(f"{case['bell']}_{face}: {len(found)} detached pieces, want {allowed}")
    on_whole = whole > ALPHA_SOLID
    for m in found:
        ys, xs = np.nonzero(m)
        where = f"at x{xs.min()}-{xs.max()} y{ys.min()}-{ys.max()}"
        if m.sum() > ISLAND_MAX_PX:
            out.append(f"{case['bell']}_{face}: detached piece {where} has {m.sum()} px")
        if (m & on_whole).sum() < ISLAND_MIN_COVER * m.sum():
            out.append(f"{case['bell']}_{face}: detached piece {where} is off the whole-body silhouette")
    return out


def alpha(path):
    return np.array(Image.open(path).convert("RGBA").getchannel("A"))


def check_race(case, race_root):
    """Rules over the race file's text; returns findings."""
    out = []
    race = by_name(race_root, "ThingDef", case["race"])
    if race is None or race.findtext("race/renderTree") != case["tree"]:
        out.append(f"{case['race']}: race/renderTree is not {case['tree']}")
    kind = by_name(race_root, "PawnKindDef", case["race"])
    bodies = [] if kind is None else [li.findtext("bodyGraphicData/texPath") for li in kind.findall("lifeStages/li")]
    if len(bodies) != case["stages"] or any(b != case["bell"] for b in bodies):
        out.append(f"{case['race']}: life-stage bodies are {bodies}, want {case['stages']} × bell")
    return out


def check_tree(case, tree_root, groups, tex_root, dll_bytes):
    out = []
    tree = by_name(tree_root, "PawnRenderTreeDef", case["tree"])
    if tree is None:
        return [f"{case['tree']}: no such tree"]
    pieces = [li for li in tree.iter("li") if li.get("Class") == "PawnRenderNodeProperties_Spastic"]
    if len(pieces) < 4:
        out.append(f"{case['tree']}: {len(pieces)} Spastic nodes")
    paths = {case["bell"]}
    for li in pieces:
        paths.add(li.findtext("texPath") or "")
        group = li.findtext("linkedBodyPartsGroup")
        if group not in groups:
            out.append(f"{li.findtext('debugLabel')}: group {group} is not on {case['body']} {sorted(groups)}")
    for p in sorted(paths):
        for face in FACES:
            png = os.path.join(tex_root, f"{p}_{face}.png")
            if not os.path.isfile(png):
                out.append(f"missing picture {p}_{face}.png")
            elif p != case["bell"]:
                box = Image.open(png).convert("RGBA").getchannel("A").getbbox()
                w = Image.open(png).width
                if box is None or box[1] > TOP_SLACK * w or not box[0] < w / 2 < box[2]:
                    out.append(f"{p}_{face}: root off the top centre, alpha box {box}")
    if case["subworker"]:
        named = [e.text for e in tree.iter("li") if (e.text or "").strip() == SUBWORKER]
        if not named:
            out.append(f"{case['tree']}: subworker {SUBWORKER} is gone")
        if SUBWORKER.rsplit(".", 1)[1].encode() not in dll_bytes:
            out.append(f"{HAZARD_DLL}: no {SUBWORKER}")
    return out


def body_groups(path, name):
    body = by_name(ET.parse(path).getroot(), "BodyDef", name)
    return {li.text for g in body.iter("groups") for li in g.findall("li")} if body is not None else set()


def main():
    fails = []
    with open(os.path.join(RM, HAZARD_DLL), "rb") as f:
        dll = f.read()
    for case in CASES:
        mod = os.path.join(RM, case["mod"])
        race_root = ET.parse(os.path.join(mod, case["race_file"])).getroot()
        tree_path = os.path.join(mod, "Defs", "PawnRenderTreeDefs", case["tree"] + ".xml")
        if not os.path.isfile(tree_path):
            fails.append(f"{case['tree']} is not in Defs/PawnRenderTreeDefs")
            continue
        tree_root = ET.parse(tree_path).getroot()
        groups = body_groups(os.path.join(mod, case["body_file"]), case["body"])
        tex = os.path.join(mod, "Textures")
        fails += check_race(case, race_root)
        fails += check_tree(case, tree_root, groups, tex, dll)
        pairs = {}
        for face in FACES:
            bell, whole = (os.path.join(tex, f"{case[k]}_{face}.png") for k in ("bell", "whole"))
            if os.path.isfile(bell) and os.path.isfile(whole):
                pairs[face] = alpha(bell), alpha(whole)
                fails += check_bell_alpha(case, face, *pairs[face])
            else:
                fails.append(f"{case['race']}: no bell or whole-body picture on {face}")
        if os.path.isdir(os.path.join(mod, "Staged", "TentacleTwitch")):
            fails.append(f"{case['mod']}/Staged/TentacleTwitch came back")

        # Mutations: each rule must fire on a broken copy.
        ms = []
        m = ET.fromstring(ET.tostring(race_root))
        by_name(m, "ThingDef", case["race"]).find("race/renderTree").text = "Animal"
        ms.append(("renderTree", check_race(case, m)))
        m = ET.fromstring(ET.tostring(race_root))
        by_name(m, "PawnKindDef", case["race"]).find("lifeStages/li/bodyGraphicData/texPath").text = "x"
        ms.append(("body texPath", check_race(case, m)))
        ms.append(("group", check_tree(case, tree_root, set(), tex, dll)))
        ms.append(("pictures", check_tree(case, tree_root, groups, tex + "_nowhere", dll)))
        for face, (bell, whole) in pairs.items():
            stray = bell.copy()
            stray[:12, :12] = 255  # a corner blob: off every creature's silhouette
            ms.append((f"stray {face}", check_bell_alpha(case, face, stray, whole)))
            big = bell.copy()
            big[-44:, -44:] = 255  # bigger than any escort
            found = check_bell_alpha(case, face, big, np.full(bell.shape, 255, np.uint8))
            ms.append((f"big {face}", [f for f in found if " px" in f]))
            if case["islands"][face]:
                found = check_bell_alpha(case, face, bell, np.zeros(bell.shape, np.uint8))
                ms.append((f"off silhouette {face}", [f for f in found if "off the whole" in f]))
        if case["subworker"]:
            ms.append(("dll", check_tree(case, tree_root, groups, tex, b"")))
        for name, found in ms:
            if not found:
                fails.append(f"{case['race']}: mutation {name} went unseen, the rule is blind")

    lastvine = ET.parse(os.path.join(RM, "Miasma", "Defs", "ThingDefs_Races", "RM_Lastvine.xml")).getroot()
    if by_name(lastvine, "ThingDef", "RM_Mantrap") is None or by_name(lastvine, "ThingDef", "RM_Mantrap").findtext("race/renderTree") != "RM_Lastvine":
        fails.append("RM_Mantrap no longer uses RM_Lastvine")
    tree = by_name(lastvine, "PawnRenderTreeDef", "RM_Lastvine")
    if tree is None or "RM_PawnRenderNodeProperties_Rearing" not in ET.tostring(tree, encoding="unicode"):
        fails.append("RM_Lastvine lost its rearing body node")
    if not any(b"RM_PawnRenderNodeProperties_Rearing" in open(p, "rb").read() for p in glob.glob(os.path.join(RM, "Miasma", "Assemblies", "*.dll"))):
        fails.append("Miasma's DLL has no RM_PawnRenderNodeProperties_Rearing")

    donor = 0
    for path in glob.glob(os.path.join(ROOT, "src", "**", "*.xml"), recursive=True):
        if "/Defs/" in path or "/Patches/" in path:
            root_text = open(path, encoding="utf-8", errors="ignore").read()
            if "SpasticScaled" in root_text:
                try:
                    root = ET.fromstring(root_text.encode("utf-8"))
                except ET.ParseError:
                    continue
                if any("SpasticScaled" in " ".join(filter(None, [e.get("Class"), e.text, e.tag])) for e in root.iter()):
                    donor += 1
                    fails.append(f"donor class in {os.path.relpath(path, ROOT)}")
    for f in fails:
        print("FAIL", f)
    print(f"selftest_donor_twitch_render: {'FAIL' if fails else 'PASS'} ({len(CASES)} twitch trees, lastvine, {donor} donor uses)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
