#!/usr/bin/env python3
"""REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED: register the 16 north/south reel renders (artpipe reelns_*_v1) as kind=artpipe
variants bound to Hose/[Styles/<Look>/]Reel_<State>_<facing>. NOT installed. Re-runnable (deterministic ids)."""
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/artpipe"))
import artledger as L  # noqa: E402
import state_dir  # noqa: E402
ART = state_dir.resolve() / "_artsrc"
ITEM = "REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED"
LOOKS = {"Scrapper": "", "Industrial": "Styles/Industrial/", "Modern": "Styles/Modern/", "Futuristic": "Styles/Futuristic/"}
ST = {"stored": "PumpHookup", "laid": "Deployed"}
w = L.Writer()
n = 0
for look, sub in LOOKS.items():
    for st, tex in ST.items():
        for face in ("north", "south"):
            fam = f"reelns_{look.lower()}_{st}_{face}_v1"
            b = (ART / fam / f"{fam}.png").read_bytes()
            sha = L.store_put_bytes(b)
            ph, wd, ht = L.dhash(b)
            w.add({"type": "variant", "id": L.det_id("variant", "benchdraw", sha, fam), "sha": sha, "ph": ph, "w": wd, "h": ht,
                   "kind": "artpipe", "loc": f"_artsrc/{fam}/{fam}.png", "date": L.now(), "job": fam,
                   "res": f"RimMandrake/FlowWorks/Hose/{sub}Reel_{tex}", "facing": face, "mask": False, "item": ITEM,
                   "prompt": f"{look} hose reel, {st}, facing {face}: artpipe job {fam} drawn from the installed west picture "
                             f"(Transient/pile_2026-10-22/reelns/make_jobs.py)"})
            n += 1
w.flush()
print(n, "registered")
