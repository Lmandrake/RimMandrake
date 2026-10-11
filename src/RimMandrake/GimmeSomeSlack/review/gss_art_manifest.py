#!/usr/bin/env python3
"""Every texture Gimme Some Slack ships (plus the hose art that moved to FlowWorks), as review-sheet rows.

Most GSS art is drawn by C# (cords, junctions, plugs, wall holes, the tap clamp, span wires), so no ThingDef names it
and a def-driven art sheet cannot see it (the 2026-10-11 owner-walk sheet showed 4 rows for that reason). This walks the
Textures folders and gives each picture its PART, its LOOK (Scrapper / Industrial / Modern / Futuristic) and the size the
game draws it at, each size citing the source line that sets it. A texture no rule covers is an ERROR, never dropped.

    python3 src/RimMandrake/GimmeSomeSlack/review/gss_art_manifest.py            # writes gss_art_manifest.json beside it
    python3 src/RimMandrake/Utils/art/art_sheet.py --textures <that json> --name gss_all_art --label "..."
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
GSS_TEX = REPO / "src/RimMandrake/GimmeSomeSlack/Textures"
FW_TEX = REPO / "src/RimMandrake/FlowWorks/Textures"
OUT = HERE / "gss_art_manifest.json"

LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
# the ground-cord families behind each look (GimmeSomeSlackMod.StyleLabel, CordMaterials.Family)
FAMILY_LOOK = {"StarWars": "Industrial", "ExtCord": "Modern", "Cybertek": "Futuristic"}

AER = "Source/Aerial/RM_MapComponent_Aerial.cs"
CORDS = "Source/SectionLayer_RM_MessyCords.cs"
CB = "Source/Core/CordBuilder.cs"

# part -> (label, drawSize [w, h] in cells, footprint, source)
STRAND = ([0.32, 0.08], "SectionLayer_RM_MessyCords.StrandWidth 0.08 cells across; RibbonInto tiles one texture every width*4 = 0.32 cells along the cord")
PARTS = {
    "TapClamp":        ("power-tap clamp", [1.5, 1.5], f"{AER}:128 TapSize = 1.5 (drawn over the tap node, jaws at TapBiteX -0.40)"),
    "AerialMast":      ("power mast", [2.0, 4.0], "Defs/Aerial/RM_AerialAnchors.xml + RM_AerialStyles.xml drawSize (2,4)"),
    "AerialMastTop":   ("power mast head (drawn above pawns)", [2.0, 4.0], "AerialMaterials mast-head overlay, same quad as the mast drawSize (2,4)"),
    "AerialLampMast":  ("lamp mast", [2.0, 4.0], "Defs/Aerial drawSize (2,4)"),
    "AerialLampMastTop": ("lamp mast head (drawn above pawns)", [2.0, 4.0], "AerialMaterials mast-head overlay, same quad as the mast drawSize (2,4)"),
    "WallBracket":     ("wall bracket", [1.0, 1.0], "Defs/Aerial drawSize (1,1), Graphic_Multi per facing"),
    "Insulator":       ("insulator", [0.25, 0.25], "AerialMaterials insulator overlay — size NOT located in source; 0.25 cells is an estimate"),
    "PoleTopDown":     ("pole seen from above", [1.0, 1.0], "AerialMaterials pole overlay — size NOT located in source; 1 cell is an estimate"),
    "SpanWire":        ("overhead span wire", [0.40, 0.10], "AerialMaterials.SpanWidth 0.10 cells across; tiled at width*4 along the span"),
    "SpanShadow":      ("span wire shadow", [1.68, 0.42], "SectionLayer_RM_AerialGround.ShadowWidth 0.42 cells across, tiled at width*4"),
    "Strand":          ("ground cord", *STRAND),
    "StrandShadow":    ("ground cord shadow", [0.52, 0.13], "SectionLayer_RM_MessyCords.ShadowWidth 0.13 cells across, tiled at width*4"),
    "Junction_T":      ("cord junction (T, taped)", [1.15, 1.15], f"{CB}:501 JunctionScale 1.15"),
    "Junction_X":      ("cord junction (X, tin)", [1.15, 1.15], f"{CB}:501 JunctionScale 1.15 (pile junctions 0.6-1.05)"),
    "Plug":            ("plug", [0.55, 0.55], f"{CB}:502 PlugScale 0.55"),
    "StubWall":        ("wall hole (cord enters a wall)", [1.0, 1.0], "Source/Core/WallMount.cs PlateAcross, cropped to the plate; shown as the whole 1-cell art"),
    "StubRock":        ("rock hole (cord enters rock)", [1.0, 1.0], "Source/Core/WallMount.cs PlateAcross, cropped to the hole; shown as the whole 1-cell art"),
    "EndFrayed_Dead":  ("cut cord end, dead", [0.5, 0.5], f"{CB}:755 fray decal scale 0.5"),
    "EndFrayed_Live":  ("cut cord end, live (sparking)", [0.5, 0.5], f"{CB}:755 fray decal scale 0.5"),
    "PowerStrip":      ("power strip, lit", [0.8, 0.4], f"{CB}:782 scale 0.8, DecalAspect 0.5"),
    "PowerStrip_Off":  ("power strip, dark", [0.8, 0.4], f"{CB}:782 scale 0.8, DecalAspect 0.5"),
    "PowerSwitch":     ("power switch, on", [1.0, 1.0], "Defs/RM_ConduitStyles.xml: inherits vanilla PowerSwitch graphic (1x1)"),
    "PowerSwitch_Off": ("power switch, off", [1.0, 1.0], "Defs/RM_ConduitStyles.xml: inherits vanilla PowerSwitch graphic (1x1)"),
    "StandingLamp":    ("standing lamp", [1.0, 1.0], "Defs/RM_ConduitStyles.xml: inherits vanilla StandingLamp graphic (1x1)"),
    "SparkGlow":       ("spark glow", [0.5, 0.5], "CordMaterials.SparkGlow mote — size NOT located in source; 0.5 cells is an estimate"),
}
# FlowWorks hoses (moved there 2026-10-11): HoseMath / RM_MapComponent_Hoses constants
HOSE_W = 0.38
HOSE = {
    "Strand_Flat":     ("hose, flat", [HOSE_W * 4, HOSE_W], "FlowWorks HoseMath.FlatVisible 0.38 cells across; tiled at width*4 (tile length estimated)"),
    "Strand_Plump":    ("hose, full", [HOSE_W * 4, HOSE_W], "FlowWorks HoseMath.FlatVisible 0.38 (+PlumpExtra 0.085) across; tile length estimated"),
    "Strand_Shadow":   ("hose shadow", [HOSE_W * 4, HOSE_W], "FlowWorks hose shadow at hose width; tile length estimated"),
    "Reel_PumpHookup": ("hose reel, stored", [2.8, 2.8], "FlowWorks Defs/Hose/RM_HoseReel*.xml drawSize (2.8,2.8)"),
    "Reel_Deployed":   ("hose reel, laid out", [2.8, 2.8], "FlowWorks reel drawSize (2.8,2.8)"),
}
for _p in ("Coupling_Brass", "Coupling_Bare", "Nozzle", "Nozzle_Bare", "EndCap", "EndCap_Bare", "Mouth", "Binding"):
    HOSE[_p] = (("hose " + _p.replace("_", " ").lower()), [round(HOSE_W / 0.25, 2)] * 2,
                "FlowWorks RM_MapComponent_Hoses.PieceBand: the 128 px canvas is scaled so its 0.25 hose band = hose width 0.38 -> 1.52 cells")
LOOK_ORDER = {l: i for i, l in enumerate(LOOKS)}


def classify_gss(rel: str):
    """rel under Textures/ -> (part, look, variant, res) or None."""
    res = re.sub(r"\.png$", "", rel)
    p = res.split("/")[2:]                       # drop RimMandrake/GimmeSomeSlack
    variant = ""
    if p[0] == "Aerial":
        if len(p) >= 4 and p[1] == "Styles":
            look, name = p[2], p[3]
        else:
            look, name = ({"TapClamp": "Scrapper", "Insulator": "shared", "PoleTopDown": "shared", "SpanWire": "shared",
                           "SpanShadow": "shared"}.get(p[1], "base")), p[1]
        name = re.sub(r"_(north|east|south|west)$", "", name)
        res = re.sub(r"_(north|east|south|west)$", "", res)
        return name, look, variant, res
    if p[0] == "Styles":
        fam = p[1]
        if fam in LOOKS:
            look, name = fam, p[2]
        elif fam == "ExtCord" and len(p) == 4:      # ExtCord/<Colour>/<slot>
            look, variant, name = "Modern", p[2], p[3]
        else:
            look, name = FAMILY_LOOK[fam], p[2]
        if name.startswith("Strand_"):
            variant, name = name[len("Strand_"):], "Strand"
        return name, look, variant, res
    name = p[0]
    alias = {"Strand_Jawa": ("Strand", "Jawa"), "Junction_Tape": ("Junction_T", ""), "Junction_Tin": ("Junction_X", "")}
    if name in alias:
        name, variant = alias[name]
    if name == "ConduitTransparent":
        return None                               # an invisible 1-px placeholder the clamp def carries; nothing to judge
    return name, "Scrapper" if name in PARTS and name not in ("StrandShadow", "SparkGlow") else "shared", variant, res


def classify_hose(rel: str):
    res = re.sub(r"\.png$", "", rel)
    p = res.split("/")[3:]                       # drop RimMandrake/FlowWorks/Hose
    if p[0] == "Styles":
        return p[2], p[1], "", res
    return p[0], ("shared" if p[0] == "Strand_Shadow" else "Scrapper"), "", res


def row(part, look, variant, res_list, table, section, rk):
    label, ds, src = table[part]
    lk = look if look in LOOKS else ("all looks" if look == "shared" else "base def art (when no look is set)")
    li = LOOK_ORDER.get(look, 9 if look == "base" else 8)
    key = f"{section}_{rk:02d}_{part}_{li}{look}" + (f"_{variant}" if variant else "")
    return {"key": key, "part": part, "look": look, "variant": variant, "section": section,
            "label": f"{label} — {lk}" + (f" ({variant})" if variant else ""),
            "resources": sorted(set(res_list)),
            "size": {"drawSize": ds, "footprint": [max(1, round(ds[0])), max(1, round(ds[1]))] if max(ds) >= 1 else [1, 1],
                     "source": src}}


def main():
    rows, unknown = {}, []
    part_rank = {p: i for i, p in enumerate(PARTS)}
    for f in sorted(GSS_TEX.rglob("*.png")):
        rel = f.relative_to(GSS_TEX).as_posix()
        c = classify_gss(rel)
        if c is None:
            continue
        part, look, variant, res = c
        if part not in PARTS:
            unknown.append(rel)
            continue
        k = ("GSS", part, look, variant)
        rows.setdefault(k, set()).add(res)
    hose_rank = {p: i for i, p in enumerate(HOSE)}
    for f in sorted((FW_TEX / "RimMandrake/FlowWorks/Hose").rglob("*.png")):
        rel = f.relative_to(FW_TEX).as_posix()
        part, look, variant, res = classify_hose(rel)
        if part not in HOSE:
            unknown.append(rel)
            continue
        rows.setdefault(("ZFW", part, look, variant), set()).add(res)
    if unknown:
        print("UNCLASSIFIED textures (add a rule):\n  " + "\n  ".join(unknown), file=sys.stderr)
        return 2
    out = []
    for (sec, part, look, variant), res in rows.items():
        if sec == "GSS":
            out.append(row(part, look, variant, res, PARTS, "GSS", part_rank[part]))
        else:
            r = row(part, look, variant, res, HOSE, "ZFW", hose_rank[part])
            r["label"] = "MOVED TO FLOWWORKS — " + r["label"]
            out.append(r)
    # the clamp's former texture path (MessyConduit, before the 2026-10-05 rename) so its older pictures show on the row
    for r in out:
        if r["part"] in PARTS and r["section"] == "GSS":
            r["former"] = [x.replace("RimMandrake/GimmeSomeSlack/", "RimMandrake/MessyConduit/") for x in r["resources"]]
    # a row keeps only renders of its own look (a render joined by the bare part name, e.g. "Strand", fits every look)
    fam = {"Scrapper": "Jawa|scrapper", "Industrial": "StarWars|industrial", "Modern": "ExtCord|modern",
           "Futuristic": "Cybertek|futuristic"}
    for r in out:
        if r["look"] in fam:
            r["render_match"] = fam[r["look"]] + ("|Hose" if r["section"] == "ZFW" and r["look"] == "Scrapper" else "")
        elif r["section"] == "ZFW":
            r["render_match"] = "Hose"
    # the clamp rows keep only renders meant for their own look (new candidates; the Scrapper row also the 10-03 render)
    for r in out:
        if r["part"] == "TapClamp" and r["section"] == "GSS":
            lk = r["look"].lower()
            r["render_match"] = f"tapclamp_v3_{lk}" + ("|Jawa_TapClamp" if lk == "scrapper" else "")
            r["jobs"] = [f"gss_tapclamp_v3_{lk}_c{n}" for n in (1, 2)] + (["RM_MessyConduit_Jawa_TapClamp"] if lk == "scrapper" else [])
        if r["part"] == "SpanShadow":     # the shipped span shadow is script-drawn; its render (queued 2026-10-11)
            r["jobs"] = ["gss_spanshadow_v2"]
    out.sort(key=lambda r: r["key"])
    n_tex = sum(1 for _ in GSS_TEX.rglob("*.png")) + sum(1 for _ in (FW_TEX / "RimMandrake/FlowWorks/Hose").rglob("*.png"))
    n_fw = sum(1 for r in out if r["section"] == "ZFW")
    lead = (f"<div style='border:2px solid #c9a227;padding:10px 14px;margin:0 0 12px;font-size:15px;line-height:1.5'>"
            f"<b>1. What this is:</b> every picture Gimme Some Slack draws in the game — {len(out) - n_fw} rows, one per part per look "
            f"(Scrapper, Industrial, Modern, Futuristic; Modern cords also per colour), each at its true in-game size beside a human, "
            f"the same part's looks banded together. The power-tap clamp is first; the last {n_fw} rows are hose art that "
            f"<b>moved to FlowWorks</b>.<br>"
            f"<b>2. What you rule on:</b> for each picture in each look, keep it or redo it (say why in the note). "
            f"The clamp rows also hold the new clamp candidates — pick one per look.<br>"
            f"<b>3. Your clicks save automatically.</b> The blue IN GAME frame is only the agent's starting point (a prefill, "
            f"counted separately), never your choice; nothing installs until you say the sheet is done.</div>")
    comp = "img/gss_tapclamp_v3"
    if (REPO / "Transient/biome_ffar" / comp).is_dir():
        cells = "".join(
            f"<figure style='margin:4px;display:inline-block;text-align:center'><img src='{comp}/{l}_cand{n}_on_wire_128.png' "
            f"style='width:288px;image-rendering:auto;border:1px solid #555'><figcaption>{l} — candidate {n}</figcaption></figure>"
            for l in LOOKS for n in (1, 2))
        lead += ("<details open style='margin:0 0 12px'><summary><b>New clamp candidates, in place:</b> each one biting its own look's "
                 "real ground cord, 128 px per cell (grid lines = cells; the clamp draws 1.5 cells wide). Pick on the clamp rows "
                 "below.</summary>" + cells + "</details>")
    OUT.write_text(json.dumps({"schema": 1, "rows": out, "textures_seen": n_tex, "lead_html": lead}, indent=1))
    print(f"{len(out)} rows from {n_tex} textures -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
