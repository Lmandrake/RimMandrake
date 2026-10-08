"""Venomvine rescue (2026-10-08): take every venomvine off the pillar-arm picture (9e0e6c1d33b1, RM_PillarArmB_east's
bytes, wired as 'rmvenomvine_v1' at bbe171ebc) and install the owner's venomvine picks + kept variants via the ledger.
Usage: python3 leaningscrub_venomvine_install.py [--apply]"""
import json, sys
from pathlib import Path
R = Path("/home/mandrake/rm/bench")
sys.path.insert(0, str(R / "src/RimMandrake/Utils/art"))
import artledger as L
SNAP = json.loads((R / "infrastructure/state/art/sheets/leaningscrub_sheet_2026-10-05.snapshot.json").read_text())["rows"]
EH, LS = "src/RimMandrake/EnvironmentalHazards", "src/RimMandrake/LeaningScrub"
ME = "script:Transient/biome_art_refresh_2026-10-07/leaningscrub_venomvine_install.py"
THICKET = "29ae79060e162f6fc7259a748839739ae3472935fbd61ae52058afa4ab11ff96"   # his C (_byname) keep, 2026-10-06
TANGLE = "acfe6b7ec16b"   # leaningscrub_venomvinethicket_c render: the low matted tangle the RM_Venomvine brief describes

idx = L.Index()


def full(p):
    return next(e for e in [p] if len(p) == 64) if len(p) == 64 else next(
        s for s in (x.stem for x in L.store_dir().glob(f"{p[:2]}/{p}*.png")))


def ruling(row, col):
    for e in idx.rulings:
        t = e.get("target") or {}
        if t.get("row") == row and t.get("column") == col and L.normalise_verdict(e.get("verdict")) == "keep" \
                and "leaningscrub_sheet_2026-10-05" in (e.get("via") or ""):
            return e["id"]
    return None


PLAN = []  # (mod, rel, sha, ruling or None, reason)
PLAN.append((EH, "Things/Plant/RM_VenomvineThicket/RM_VenomvineThicket_a.png", THICKET, ruling("RM_VenomvineThicket", "C"), None))
# interim, until the queued 0vv_* renders land: no venomvine keeps the pillar-arm bytes
PLAN.append((EH, "Things/Plant/RM_Venomvine/RM_Venomvine_a.png", full(TANGLE), None, ME + " (interim: pillar-arm bytes off)"))
for d in ["RM_RearingVenomvine", "RM_WalkingVenomvine", "RM_HoardVenomvine", "RM_QuenchVenomvine",
          "RM_SwornVenomvine", "RM_SheddingVenomvine"]:
    PLAN.append((LS, f"Things/Plant/{d}/{d}_a.png", THICKET, None, ME + " (interim: his kept thicket until own render)"))
# picks + kept variants (Graphic_Random: _a stays column A, the rest get _b/_c/_d by letter)
for d, letters in [("RM_CrownVenomvine", "BCD"), ("RM_DrippingVenomvine", "BCD"), ("RM_HollowVenomvine", "BCD")]:
    for c in letters:
        PLAN.append((LS, f"Things/Plant/{d}/{d}_{c.lower()}.png", SNAP[d]["columns"][c]["single"], ruling(d, c), None))

for mod, rel, sha, rid, reason in PLAN:
    rec = {"rel": rel, "sha": sha[:12], "ruling": rid, "reason": reason}
    if "--apply" in sys.argv:
        try:
            res = L.install(mod, rel, sha, ruling_id=rid) if rid else L.install(mod, rel, sha, reason=reason)
            rec["result"] = res.get("status") if isinstance(res, dict) else str(res)
        except L.Refused as e:
            rec["result"] = "REFUSED " + str(e)
    print(json.dumps(rec))
