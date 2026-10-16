#!/usr/bin/env python3
"""FLYER_NORTH_REDRAW_WINGS_LEFT_AT_HOME: register the BENCH-drawn candidates (codex edits, prompts beside this file)
as kind=artpipe variants in the art ledger (the tint_candidates.py pattern) so art_sheet.py shows them as columns.
NOT installed. Re-runnable: ids are deterministic and the store is content-addressed."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src/RimMandrake/Utils/art"))
import artledger as L

HERE = Path(__file__).resolve().parent
ART = Path("/mnt/d/Luke/dev/_artpipe/_artsrc")
ITEM = "FLYER_NORTH_REDRAW_WINGS_LEFT_AT_HOME"
FF = {"RM_FleetFlier": "Things/Pawn/Animal/RM_FleetFlier/RM_FleetFlier",
      "RUT_FleetFlier": "Things/Pawn/Animal/RUT_FleetFlier/RUT_FleetFlier"}
SETS = []  # (job family, res, {facing: png}, prompt)
for v, what in (("a", "wings folded along the back"), ("b", "wings spread, mirror of the south"),
                ("c", "wings half-folded, drooped at the sides")):
    for kind, res in FF.items():
        SETS.append((f"{kind.lower()}_northredraw_{v}", res, {"north": HERE / f"fleet/RM_FleetFlier_north_{v.upper()}.png"},
                     f"north redraw ({what}) from south+east: " + (HERE / f"fleet/prompt_{v.upper()}.txt").read_text()[:600]))
SETS.append(("rm_murrelith_redraw_b", "Things/Pawn/Animal/RM_FeverWoodBirds/RM_Murrelith",
             {f: HERE / f"murr/RM_Murrelith_{f}_B.png" for f in ("south", "east", "north")},
             "S from regen_fw_murrelith_v2_south (margin, rainbow ribbons), E and N derived from that S: "
             + (HERE / "murr/prompt_S.txt").read_text()[:500]))

w = L.Writer(); out = []
for fam, res, faces, prompt in SETS:
    d = ART / fam; d.mkdir(parents=True, exist_ok=True)
    for fac, png in faces.items():
        b = png.read_bytes(); sha = L.store_put_bytes(b); job = f"{fam}_{fac}"
        (d / f"{job}.png").write_bytes(b)
        ph, wd, ht = L.dhash(b)
        w.add({"type": "variant", "id": L.det_id("variant", "benchdraw", sha, job), "sha": sha, "ph": ph, "w": wd, "h": ht,
               "kind": "artpipe", "loc": f"_artsrc/{fam}/{job}.png", "date": L.now(), "job": job, "res": res,
               "facing": fac, "mask": False, "item": ITEM, "prompt": prompt})
        out.append((job, sha[:12]))
w.flush(); print(*out, sep="\n")
