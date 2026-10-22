#!/usr/bin/env python3
"""PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS ("Draft all of it", owner card 2026-10-22): register compose.py's output as
kind=artpipe variants in the art ledger and write the texture manifest the gated sheet is built from. NOT installed.
  * draft/<Look>/UniversalPipe_Atlas.png -> res RimMandrake/FlowWorks/Pipe/<Look>/UniversalPipe_Atlas (fam pipefit_atlas_<look>_v1)
  * cand/<Look>_<Piece>.png              -> res RimMandrake/FlowWorks/Pipe/<Look>/Draft/<Piece> (fam pipefit_<piece>_<look>_v1)
  * cand/<Look>_Pump.png                 -> res RimMandrake/FlowWorks/Pump/<Look>/RM_LiquidPump (fam pumplook_<look>_v1c)
Re-runnable: ids deterministic, store content-addressed.   python3 register.py -> textures_manifest.json
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/artpipe"))
import artledger as L  # noqa: E402
import state_dir  # noqa: E402

ART = state_dir.resolve() / "_artsrc"
ITEM = "PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS"
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
w = L.Writer()
rows = []


def add(png, fam, res, prompt):
    d = ART / fam
    d.mkdir(parents=True, exist_ok=True)
    b = png.read_bytes()
    sha = L.store_put_bytes(b)
    (d / f"{fam}.png").write_bytes(b)
    ph, wd, ht = L.dhash(b)
    w.add({"type": "variant", "id": L.det_id("variant", "benchdraw", sha, fam), "sha": sha, "ph": ph, "w": wd, "h": ht,
           "kind": "artpipe", "loc": f"_artsrc/{fam}/{fam}.png", "date": L.now(), "job": fam, "res": res,
           "facing": "single", "mask": False, "item": ITEM, "prompt": prompt})


for look in LOOKS:
    for piece in ("Cross", "Tee", "Coupling", "EndCap"):
        p = HERE / "cand" / f"{look}_{piece}.png"
        add(p, f"pipefit_{piece.lower()}_{look.lower()}_v1", f"RimMandrake/FlowWorks/Pipe/{look}/Draft/{piece}",
            f"{piece} for the {look} pipe atlas: artpipe master pipefitraw_{piece.lower()}_{look.lower()}_v1 (1024, top-down), "
            f"scaled to the 18 px (0.10 cell) pipe of the 176 px/cell atlas by Transient/pile_2026-10-22/pipefit/compose.py")
    res = f"RimMandrake/FlowWorks/Pipe/{look}/UniversalPipe_Atlas"
    add(HERE / "draft" / look / "UniversalPipe_Atlas.png", f"pipefit_atlas_{look.lower()}_v1", res,
        f"DRAFT {look} pipe atlas composed by compose.py: the live body with its bands painted out, one coupling per joint "
        f"(half at each linked tile edge), Tee/Cross hubs, matched end cap, elbows bent from the body profile; pieces "
        f"pipefit_<piece>_{look.lower()}_v1")
    refs = [{"path": str((HERE / "comp" / f"{look}_layout.png").relative_to(REPO)),
             "size": {"drawSize": [9, 7], "footprint": [9, 7], "source": "a 9x7-cell test layout drawn from the DRAFT atlas the way Graphic_Linked tiles it"}},
            {"path": str((HERE / "comp" / f"{look}_live_layout.png").relative_to(REPO)),
             "size": {"drawSize": [9, 7], "footprint": [9, 7], "source": "the same layout from the LIVE atlas (today's look, for comparison)"}}]
    rows.append({"key": f"PipeAtlas_{look}", "label": f"pipe atlas, {look.lower()} look (tees, crosses, couplings, end caps)",
                 "part": "atlas", "look": look, "variant": "A", "section": "pipe atlas", "resources": [res],
                 "render_match": f"pipefit_atlas_{look.lower()}_", "reference_textures": refs,
                 "size": {"drawSize": [4, 4], "footprint": [4, 4],
                          "source": "linked pipe atlas (Graphic_Linked): 4x4 tiles of 176 px, each tile one cell"}})
for look in ["Industrial", "Modern", "Futuristic"]:
    res = f"RimMandrake/FlowWorks/Pump/{look}/RM_LiquidPump"
    add(HERE / "cand" / f"{look}_Pump.png", f"pumplook_{look.lower()}_v1c", res,
        f"{look} look of the live 4-port hub pump: artpipe pumplook_{look.lower()}_v1 (512, canon_reference = live "
        f"RM_LiquidPump.png), trimmed and re-centred to the live pump's fill box by compose.py")
    rows.append({"key": f"PumpLook_{look}", "label": f"liquid pump, {look.lower()} look", "part": "pump", "look": look,
                 "variant": "A", "section": "pump looks", "resources": [res], "render_match": f"pumplook_{look.lower()}_v1c",
                 "reference_textures": [{"path": "src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Machinery/RM_LiquidPump.png",
                                         "size": {"drawSize": [1, 1], "footprint": [1, 1], "source": "the LIVE pump (Scrapper look), every look today"}}],
                 "size": {"drawSize": [1, 1], "footprint": [1, 1],
                          "source": "RM_LiquidPump.xml: Graphic_Single drawSize (1,1), size (1,1)"}})
w.flush()
lead = ("<p>Owner, by card 2026-10-22 (<i>May we draft replacements for FlowWorks pipe art?</i> &rarr; <b>Draft all of it</b>): "
        "a DRAFT pipe atlas per look with real 3-way (tee) and 4-way (cross) fittings, ONE coupling per joint (where two "
        "cells meet) instead of three or four bands per cell, and an end cap matched to each look; plus Industrial, Modern "
        "and Futuristic looks of the live 4-port pump (today every look shows the rusty one). The REFERENCE pictures beside "
        "each atlas row show a test layout drawn from the draft and the same layout from today's atlas. Pick a column or note "
        "what to change. Nothing is installed; a pump look also needs a small def/C# change after your pick. "
        "Item PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS; study Transient/pile_2026-10-22/joints_study.md (D9, D10, D11). "
        "The joint fittings (flange, coupler, saddle) are on their own sheet, joint_fittings_sheet_2026-10-22.</p>")
(HERE / "textures_manifest.json").write_text(json.dumps({"rows": rows, "lead_html": lead}, indent=1))
print(len(rows), "rows")
