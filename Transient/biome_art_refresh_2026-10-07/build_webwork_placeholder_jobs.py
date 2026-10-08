#!/usr/bin/env python3
"""Rows for the three Webwork plants that ship as geometric circles (Brennoth, Ruddreth, Sorrivel).

Decision taken by question card 2026-10-07: "Queue real art now". He had picked column A (the circle) on the
2026-10-05 Webwork sheet with no note; a placeholder can never be a pick (owner rule typed 2026-10-07 22:33 PDT), so
each plant gets three real candidate paintings (a/b/c) to pick from and keep as variants. Prompts are the def
descriptions; style matches the Webwork plants he kept (fellome, grennick, threllick, sellith, tavrosk, vessark,
norrveth). Run: python3 <this> > webwork_placeholder_regen_jobs.json; fill_queue.py --input that file.
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFS = REPO / "src/RimMandrake/Webwork/Defs/ThingDefs_Plants/RM_WebworkFlora.xml"
REGISTER = ("webwork register: a dense nightmare thicket in green gloom, pale dust-lit shafts, silk and tangled "
            "vegetation; dim greens, bruise purples, bone-white silk")
STYLE = ("Same hand as the kept Webwork flora set (fellome, grennick, threllick): matte painterly vanilla-RimWorld plant "
         "sprite, seen from above at a slight angle, realistic and botanically believable, never cartoonish, never a "
         "flat shape or icon; one centred mature specimen on a fully transparent background, no ground, no shadow.")
ANGLE = {"a": "", "b": " A second, clearly different individual of the same species (different branching and posture).",
         "c": " A third individual of the same species, older and more weathered than the others."}


def rows():
    root = ET.parse(DEFS).getroot()
    out = []
    for d in root:
        dn = d.findtext("defName")
        if dn not in ("RM_Brennoth", "RM_Ruddreth", "RM_Sorrivel"):
            continue
        desc = " ".join((d.findtext("description") or "").split())
        name = (d.findtext("label") or dn[3:]).lower()
        for v, extra in ANGLE.items():
            out.append({
                "id": f"webwork_{name}_real_v1{v}", "rimflow_item_id": "BIOME_FLORAFAUNA_ART_REVIEW_1",
                "target_def": dn, "target_texpath": f"Things/Plant/{dn}/{dn}_a",
                "prompt": f"RimWorld plant sprite, the {name}: {desc}{extra}",
                "style_notes": STYLE, "biome_register": REGISTER,
                "canvas_w": 256, "canvas_h": 256, "facings": [], "priority": 0, "background": "transparent",
                "channel": "codex",
            })
    return out


if __name__ == "__main__":
    print(json.dumps(rows(), indent=1))
