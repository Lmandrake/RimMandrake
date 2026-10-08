"""Long Shade sheet (desert_sheet_2026-10-04) — plan/apply the owner's 2026-10-08 primary picks through the art ledger.
Usage: python3 longshade_install_plan.py [--apply]"""
import json, sys
from pathlib import Path
R = Path("/home/mandrake/rm/bench")
sys.path.insert(0, str(R / "src/RimMandrake/Utils/art"))
import artledger as L

DEC = R / "Transient/biome_ffar/desert_sheet_2026-10-04.decisions.json"
SNAP = R / "infrastructure/state/art/sheets/desert_sheet_2026-10-04.snapshot.json"
VIA = "Transient/biome_ffar/desert_sheet_2026-10-04.decisions.json"
# rows whose decision column is a full new set to install over the in-game art (owner 2026-10-08)
ROWS = ["RM_Dunejelly", "RM_Gennok", "RM_Gloomcast", "RSW_Bantha", "RSW_Bolotaur", "RSW_FeralGrazer",
        "RSW_Gutkurr", "RSW_Horax", "RSW_Hrumph", "RSW_IridonianReek", "RSW_Jakobeast", "RSW_Jamel", "RSW_Jimvu",
        "RSW_Krykna", "RSW_Kwi", "RSW_LongtailGorg", "RSW_Runyip", "RSW_Shaak", "RSW_Shyrack", "RSW_Uvak",
        "RSW_Varactyl", "RSW_Voorpak", "RSW_Wraid", "RSW_Zeer", "RM_Shadespire", "RM_Vorrel",
        "RSW_Plant_Chakroot_Wild"]

REDIRECT = {"RM_Dunejelly": ("src/RimMandrake/LongShade", "Things/Pawn/Animal/RM_Dunejelly/RM_Dunejelly"),
            "RSW_Bantha": ("src/RimStarWars/SWBestiary", "swanimals/Bantha/BanthaR")}

def main(apply):
    d = json.loads(DEC.read_text())["decisions"]; s = json.loads(SNAP.read_text())["rows"]
    idx = L.Index()
    rul = {}
    for e in idx.rulings:
        t = e.get("target") or {}
        if e.get("via") == VIA and (e.get("at") or "").startswith("2026-10-08") and t.get("column") and not t.get("variant_of"):
            rul[(t["row"], t["column"])] = e["id"]
    out = []
    for row in ROWS:
        v, sr = d[row], s[row]
        dec = v["decision"]; cols, gof, lab = sr["columns"], sr["graphic_of"], sr["labels"]
        g = gof[dec]
        if g == "_byname":  # the row's default graphic
            g = sr.get("res")
        ing = [c for c in cols if lab[c].startswith("IN GAME") and gof[c] == g]
        if not ing:
            out.append((row, "NO IN-GAME COLUMN for " + g)); continue
        ic = ing[0]
        for facing, newsha in sorted(cols[dec].items()):
            old = cols[ic].get(facing)
            base = g.split("/")[-1] + ("" if facing == "single" else "_" + facing) + ".png"
            slots = [(m, r) for (m, r), ev in idx.live.items() if ev.get("sha") == old and r.endswith("/" + base) and r.startswith(g.rsplit("/", 1)[0] + "/")]
            if not slots:
                out.append((row, f"{facing}: old {old[:10]} has no live slot at {g}")); continue
            if row in REDIRECT:  # donor path carries a colour mask (CutoutComplex): install at our own path, def repointed
                m0, stem = REDIRECT[row]; slots = [(m0, f"{stem}_{facing}.png")]
            for m, r in slots:
                rid = rul.get((row, dec))
                rec = {"row": row, "col": dec, "mod": m, "rel": r, "sha": newsha, "ruling": rid}
                if apply:
                    try:
                        res = L.install(m, r, newsha, ruling_id=rid)
                        rec["result"] = res.get("status") if isinstance(res, dict) else str(res)
                    except L.Refused as e:
                        rec["result"] = "REFUSED " + str(e)
                out.append(rec)
    for o in out:
        print(json.dumps(o))

main("--apply" in sys.argv)
