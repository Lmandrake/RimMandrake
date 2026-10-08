"""Rulings 2-4 of morning_rulings_enact_2026-10-08.md. Authorised by the owner's sheet keep rulings (ledger) naming each sha;
the 2026-10-08 question-card rulings decide WHERE they go. Usage: python3 morning_rulings_install.py [--apply]"""
import json, sys
sys.path.insert(0, "/home/mandrake/rm/bench/src/RimMandrake/Utils/art")
import artledger as L
apply = "--apply" in sys.argv
S = json.load(open("/home/mandrake/rm/bench/infrastructure/state/art/sheets/leaningscrub_sheet_2026-10-05.snapshot.json"))["rows"]
idx = L.Index()

def keep(sha):
    for e in idx.rulings:
        t = e.get("target") or {}
        if sha in (t.get("shas") or []) + [t.get("sha")] and e.get("by") == "owner" and e.get("trust") == "ruled" \
                and L.normalise_verdict(e.get("verdict")) == "keep" and "leaningscrub_sheet" in (e.get("via") or ""):
            return e["id"]
    raise SystemExit("no keep for " + sha)

def go(mod, rel, sha):
    r = L.install(mod, rel, sha, ruling_id=keep(sha), dry_run=not apply)
    print(json.dumps({"rel": rel, "sha": sha[:12], "status": r["status"], "old": (r.get("old") or "")[:12]}))

# ruling 2: Scurrier E for both sexes
for sex in ("f", "m"):
    for f in ("east", "north", "south"):
        go("src/RimStarWars/SWBestiary", f"swanimals/Scurrier/Scurrier_{sex}_{f}.png", S["RSW_Scurrier"]["columns"]["E"][f])
# ruling 3: donor plants, every variant file of the donor folder, planet-wide via the campaign layer (UtinniPatches)
PL = [("Plant_Brambles", "B", "RG_Brambles", "Brambles", "AB"), ("RG_Plant_CreepStern", "B", "RG_CreepStern", "CreepStern", "ABC"),
      ("RG_Plant_CrimsonCushion", "B", "RG_TundraScrubsRed", "TundraScrubsRed", "ABCDE"), ("RG_Plant_Dervish", "C", "RG_Dervish", "Dervish", "ABC")]
for row, col, folder, stem, letters in PL:
    sha = S[row]["columns"][col]["single"]
    for l in letters:
        go("src/RimUtinni/UtinniPatches", f"Things/Plant/{folder}/{stem}{l}.png", sha)
