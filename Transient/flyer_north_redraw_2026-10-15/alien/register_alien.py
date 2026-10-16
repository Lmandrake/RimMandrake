#!/usr/bin/env python3
"""Owner 2026-10-15 on the flyer sheet: "I like your Fleet Flier, but alas it must be much more alien. Longer wings,
strange colors, elongated face, to look less avian." Register the three redesigned S/E/N sets (X/Y/Z; prompts beside
this file) as kind=artpipe variants for RM_ and RUT_ so art_sheet.py shows them. NOT installed. Re-runnable."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src/RimMandrake/Utils/art"))
import artledger as L

HERE = Path(__file__).resolve().parent
ART = Path("/mnt/d/Luke/dev/_artpipe/_artsrc")
RES = {"rm": "Things/Pawn/Animal/RM_FleetFlier/RM_FleetFlier", "rut": "Things/Pawn/Animal/RUT_FleetFlier/RUT_FleetFlier"}
w = L.Writer(); out = []
for k in "XYZ":
    for t, res in RES.items():
        fam = f"{t}_fleetflier_alien_{k.lower()}"; d = ART / fam; d.mkdir(parents=True, exist_ok=True)
        for fac in ("south", "east", "north"):
            b = (HERE / f"RM_FleetFlier_{fac}_{k}.png").read_bytes(); sha = L.store_put_bytes(b); job = f"{fam}_{fac}"
            (d / f"{job}.png").write_bytes(b); ph, wd, ht = L.dhash(b)
            w.add({"type": "variant", "id": L.det_id("variant", "benchdraw", sha, job), "sha": sha, "ph": ph, "w": wd,
                   "h": ht, "kind": "artpipe", "loc": f"_artsrc/{fam}/{job}.png", "date": L.now(), "job": job,
                   "res": res, "facing": fac, "mask": False, "item": "FLYER_NORTH_REDRAW_WINGS_LEFT_AT_HOME",
                   "prompt": "alien redesign (owner: longer wings, strange colors, elongated face): "
                             + (HERE / f"prompt_{k}_{fac}.txt").read_text()[:600]})
            out.append((job, sha[:12]))
w.flush(); print(len(out), "variants")
