#!/usr/bin/env python3
"""HOSE_REEL_COUPLING_REDRAW_QUIT_STARING_BACK: register the BENCH-drawn coupling candidates (cand/<Look>_<A|B>_<state>.png,
made by compose.py from the codex edits in raw2/) as kind=artpipe variants bound to each reel texture, so art_sheet.py
shows them as columns, and write the texture manifest the sheet is built from (one row per look x state).
NOT installed. Re-runnable: ids are deterministic and the store is content-addressed.
    python3 register.py  -> textures_manifest.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src/RimMandrake/Utils/art"))
import artledger as L  # noqa: E402

HERE = Path(__file__).resolve().parent
ART = Path("/mnt/d/Luke/dev/_artpipe/_artsrc")
ITEM = "HOSE_REEL_COUPLING_REDRAW_QUIT_STARING_BACK"
SUB = {"Scrapper": "", "Industrial": "Styles/Industrial/", "Modern": "Styles/Modern/", "Futuristic": "Styles/Futuristic/"}
STATE = {"Deployed": "laid (hose out)", "PumpHookup": "stored (hose reeled in)"}
STYLE = {"A": "plain sleeve with two ring bands", "B": "hex coupling nut at the body, smooth sleeve"}

w = L.Writer()
rows, out = [], []
for look, sub in SUB.items():
    for state, slab in STATE.items():
        res = f"RimMandrake/FlowWorks/Hose/{sub}Reel_{state}"
        for cand in "AB":
            png = HERE / "cand" / f"{look}_{cand}_{state}.png"
            if not png.exists():
                continue
            fam = f"hosereel_coupling_{look.lower()}_{state.lower()}_{cand.lower()}"
            d = ART / fam
            d.mkdir(parents=True, exist_ok=True)
            b = png.read_bytes()
            sha = L.store_put_bytes(b)
            (d / f"{fam}.png").write_bytes(b)
            ph, wd, ht = L.dhash(b)
            w.add({"type": "variant", "id": L.det_id("variant", "benchdraw", sha, fam), "sha": sha, "ph": ph, "w": wd,
                   "h": ht, "kind": "artpipe", "loc": f"_artsrc/{fam}/{fam}.png", "date": L.now(), "job": fam, "res": res,
                   "facing": "single", "mask": False, "item": ITEM,
                   "prompt": f"straight side-on outlet coupling, {STYLE[cand]}: codex edit of the {look} laid art over a grey "
                             f"blockout (flat end u 9, centre v 135, 42 px = the laid hose), pasted onto the original "
                             f"left of the pump body only (compose.py)"})
            out.append((fam, sha[:12]))
        rows.append({"key": f"HoseReel_{look}_{state}", "label": f"hose reel, {look.lower()} look, {slab}",
                     "part": f"reel {state}", "look": look, "variant": state, "section": "hose reel",
                     "resources": [res], "render_match": f"hosereel_coupling_{look.lower()}_{state.lower()}_",
                     "size": {"drawSize": [2.8, 2.8], "footprint": [2, 2],
                              "source": "RM_HoseReel.xml / RM_HoseReelStyles.xml graphicData drawSize (2.8,2.8), size (2,2)"}})
w.flush()
lead = ("Owner 2026-10-15, looking at the reel in game: <i>“I do wish the perspective of the hose connection for the reel "
        "were straight to the left without the perspective of seeing into the pipe. It makes the pipe look “bent towards the "
        "screen” and doesn't let it join properly with the hose, as shown.”</i> Each row is one reel texture (4 looks × stored/"
        "laid). <b>A</b> = plain sleeve with ring bands, <b>B</b> = hex coupling nut at the body. Only the coupling changed: the "
        "body, drum, wheel and valve are the original pixels. The new coupling ends flat at the spot the code draws the hose's "
        "end coupling (u 9/256, v 135/256) and is 42 px tall, the laid hose's own width. A mock of the hose joined to it, "
        "old | A | B: <a href=\"img/hosereel_coupling_mock.png\">img/hosereel_coupling_mock.png</a>. Nothing is installed "
        "until you pick.")
(HERE / "textures_manifest.json").write_text(json.dumps({"rows": rows, "lead_html": lead}, indent=1))
print(*out, sep="\n")
