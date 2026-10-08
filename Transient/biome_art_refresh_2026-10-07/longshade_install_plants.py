"""Long Shade sheet — plant picks and the owner's explicit plant variants, installed into each Graphic_Random folder via the art ledger.
Usage: python3 longshade_install_plants.py [--apply]"""
import json, sys
from pathlib import Path
R = Path("/home/mandrake/rm/bench")
sys.path.insert(0, str(R / "src/RimMandrake/Utils/art"))
import artledger as L
VIA = "Transient/biome_ffar/desert_sheet_2026-10-04.decisions.json"
SNAP = R / "infrastructure/state/art/sheets/desert_sheet_2026-10-04.snapshot.json"
LS, SWB = "src/RimMandrake/LongShade", "src/RimStarWars/SWBestiary"
# (row, column, mod, rel) — replacements of the single live picture, then added variants
PLAN = [("RM_Shadespire", "D", LS, "Things/Plant/RM_Shadespire/RM_Shadespire_a.png"),
        ("RM_Vorrel", "B", LS, "Things/Plant/RM_Vorrel/RM_Vorrel_a.png"),
        ("RSW_Plant_Chakroot_Wild", "C", SWB, "Things/Plant/RSW_Plant_Chakroot_Wild/RSW_Plant_Chakroot_WildA.png")]
for row, mod, stem, letters in [("RM_Dewfringe", LS, "Things/Plant/RM_Dewfringe/RM_Dewfringe_", "BCDEF"),
                                ("RM_Pavecrust", LS, "Things/Plant/RM_Pavecrust/RM_Pavecrust_", "BCDEF"),
                                ("RSW_SurraGrass", SWB, "Things/Plant/RSW_SurraGrass/RSW_SurraGrass_", "BCD"),
                                ("RSW_VellaraBloom", SWB, "Things/Plant/RSW_VellaraBloom/RSW_VellaraBloom", "BCD"),
                                ("RM_Maidenbloom", LS, "Things/Plant/RM_Maidenbloom/RM_Maidenbloom_", "B")]:
    for c in letters:
        PLAN.append((row, c, mod, stem + (c if stem.endswith("Bloom") else c.lower()) + ".png"))

snap = json.loads(SNAP.read_text())["rows"]
idx = L.Index()
for row, col, mod, rel in PLAN:
    sha = snap[row]["columns"][col]["single"]
    rid = next((e["id"] for e in idx.rulings if e.get("via") == VIA and (e.get("target") or {}).get("row") == row
                and (e.get("target") or {}).get("column") == col and L.normalise_verdict(e.get("verdict")) == "keep"), None)
    rec = {"row": row, "col": col, "rel": rel, "ruling": rid}
    if "--apply" in sys.argv:
        try:
            rec["result"] = L.install(mod, rel, sha, ruling_id=rid).get("status")
        except L.Refused as e:
            rec["result"] = "REFUSED " + str(e)
    print(json.dumps(rec))
