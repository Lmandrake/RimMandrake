#!/usr/bin/env python3
"""MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY: register compose.py's drafts as kind=artpipe variants in the art ledger and
write the texture manifest the gated sheet is built from. NOT installed (each replaces art the owner kept: §2.3).
  cand/Pump_Modern_<X>.png      -> res RimMandrake/FlowWorks/Pump/Modern/RM_LiquidPump         (fam modernpump_<x>_v1)
  cand/Sprinkler_Modern_<X>.png -> res RimMandrake/FlowWorks/Sprinkler/Modern/RM_SprinklerHead (fam modernsprinkler_<x>_v1)
    python3 register.py -> textures_manifest.json
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
ITEM = "MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY"
DESC = {
    "Pump": {"A": "thermoplastic jet pump: charcoal motor with fan cowl and pressure-switch box on a grey composite body, grey PVC true-union ports",
             "B": "pool/booster pump: slate-grey moulded housing, ribbed motor cowl, small clear strainer window, white PVC union ports",
             "C": "stainless booster pump: brushed casing, smooth blue powder-coated motor, gauge, tri-clamp sanitary ports"},
    "Sprinkler": {"A": "black pop-up gear-drive rotor with green cap on a grey PVC riser and saddle",
                  "B": "brass impact sprinkler with black swing arm on a black poly riser and saddle",
                  "C": "blue/white micro spinner under a clear dome on a black riser and grey saddle"},
}
RES = {"Pump": "RimMandrake/FlowWorks/Pump/Modern/RM_LiquidPump",
       "Sprinkler": "RimMandrake/FlowWorks/Sprinkler/Modern/RM_SprinklerHead"}
LIVE = {"Pump": "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Pump/Modern/RM_LiquidPump.png",
        "Sprinkler": "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Sprinkler/Modern/RM_SprinklerHead.png"}
SIZE = {"Pump": {"drawSize": [1, 1], "footprint": [1, 1], "source": "RM_LiquidPump.xml / RM_LiquidPumpStyles.xml: Graphic_Single drawSize (1,1), size (1,1), not rotatable"},
        "Sprinkler": {"drawSize": [1, 1], "footprint": [1, 1], "source": "RM_Sprinklers.xml: Graphic_Single drawSize (1,1), drawOffset z 0.18 (Modern)"}}
w = L.Writer()
rows = []


def add(png, fam, res, prompt):
    d = ART / fam
    d.mkdir(parents=True, exist_ok=True)
    b = png.read_bytes()
    sha = L.store_put_bytes(b)
    (d / f"{fam}.png").write_bytes(b)
    ph, wd, ht = L.dhash(b)
    w.add({"type": "variant", "id": L.det_id("variant", "foundrydraw", sha, fam), "sha": sha, "ph": ph, "w": wd, "h": ht,
           "kind": "artpipe", "loc": f"_artsrc/{fam}/{fam}.png", "date": L.now(), "job": fam, "res": res,
           "facing": "single", "mask": False, "item": ITEM, "prompt": prompt})


for subject in ("Pump", "Sprinkler"):
    for x in "ABC":
        p = HERE / "cand" / f"{subject}_Modern_{x}.png"
        if not p.is_file():
            continue
        fam = f"modern{subject.lower()}_{x.lower()}_v1"
        add(p, fam, RES[subject], f"Modern {subject.lower()} option {x}: {DESC[subject][x]} (Codex edit over the live layout, "
            f"Transient/pile_2026-10-23/modern_pump/gen.py; fitted by compose.py; brief flowworks_modern_art_brief.md M1-M4)")
    rows.append({"key": f"Modern{subject}", "label": f"{subject.lower()}, modern look (A = today; B, C, D = candidates)",
                 "part": subject.lower(), "look": "Modern", "variant": "A", "section": f"modern {subject.lower()}",
                 "resources": [RES[subject]], "render_match": f"modern{subject.lower()}_",
                 "reference_textures": [{"path": LIVE[subject], "size": dict(SIZE[subject], source="TODAY's Modern art (red repaint, kept)")}],
                 "size": SIZE[subject]})
w.flush()
lead = ("<p>Owner 2026-10-22: <i>\"The 'modern' tank and reel art isn't supposed to be just painted with the primary colors ... "
        "Modern water tanks. Modern hose reels. Like you would buy in home depot\"</i>. The tanks and reel are done; the Modern "
        "<b>pump</b> and <b>sprinkler head</b> are still the red repaint. Column A is today's picture; columns B, C, D are three "
        "candidate real modern products (pump B jet pump, C pool/booster pump, D stainless booster; sprinkler B pop-up rotor, "
        "C brass impact head, D micro spinner). Keep the one you like per subject, or note what to change. Nothing is installed until you "
        "pick (it replaces art you kept). Containers and hose ends were left alone (not red repaints); the small Modern join "
        "fittings are still red. Item MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY; brief design/RimMandrake/flowworks_modern_art_brief.md.</p>")
(HERE / "textures_manifest.json").write_text(json.dumps({"rows": rows, "lead_html": lead}, indent=1))
print(len(rows), "rows")
