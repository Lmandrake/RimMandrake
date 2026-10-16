#!/usr/bin/env python3
"""HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY: register the mockup candidates (cand/<Look>_{pump,flange,saddle}.png from conform.py,
mock/<join>_<Look>.png from mock.py) as kind=artpipe variants bound to the texture each would become, and write the
texture manifest the gated sheet is built from. NOT installed. Re-runnable: ids are deterministic, the store content-addressed.
    python3 register.py  -> textures_manifest.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src/RimMandrake/Utils/art"))
import artledger as L  # noqa: E402

HERE = Path(__file__).resolve().parent
ART = Path("/mnt/d/Luke/dev/_artpipe/_artsrc")
ITEM = "HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY"
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
JOINS = ["hose_to_pump", "hose_to_tank", "hose_to_reel", "hose_to_pipe", "pipe_to_tank", "pipe_to_pump", "pump_to_tank",
         "reel_to_tank", "pipe_to_pipe"]
PIECES = {
    "pump": ("RimMandrake/FlowWorks/Pump/{look}/RM_LiquidPump", [2, 2], [2, 1], "liquid pump (hefty), {l} look",
             "proposed: footprint 2x1 (today 1x1), drawSize (2,2) with drawOffset z +0.5 (today drawSize 1)"),
    "flange": ("RimMandrake/FlowWorks/Joins/{look}/Flange", [0.5, 0.5], [1, 1], "pipe-end flange, {l} look",
               "drawn by RM_LiquidJoins at 0.5 x 0.5 cell, its face on the edge a pipe shares with a tank or machine"),
    "saddle": ("RimMandrake/FlowWorks/Joins/{look}/Saddle", [1, 1], [1, 1], "hose saddle on a pipe, {l} look",
               "drawn by RM_LiquidJoins at 1 x 1 cell across the pipe cell a hose end couples onto"),
}

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


for piece, (resf, ds, fp, labf, src) in PIECES.items():
    for look in LOOKS:
        png = HERE / "cand" / f"{look}_{piece}.png"
        if not png.exists():
            continue
        res = resf.format(look=look)
        fam = f"liqjoin_{piece}_{look.lower()}_a"
        add(png, fam, res, f"mockup {piece} in the {look} look: codex edit from that look's tank+reel reference (gen.py), "
                           f"conformed by conform.py")
        rows.append({"key": f"LiqJoin_{piece}_{look}", "label": labf.format(l=look.lower()), "part": piece, "look": look,
                     "variant": "A", "section": "liquid joins", "resources": [res],
                     "render_match": f"liqjoin_{piece}_{look.lower()}_",
                     "size": {"drawSize": ds, "footprint": fp, "source": src}})

for join in JOINS:
    res = f"Mockups/LiquidJoins/{join}"
    for look in LOOKS:
        png = HERE / "mock" / f"{join}_{look}.png"
        if png.exists():
            add(png, f"liqjoin_mock_{join}_{look.lower()}", res,
                f"composite mock (mock.py): {join} in the {look} look, today (top) vs proposed (bottom), 128 px per cell")
    rows.append({"key": f"LiqJoinMock_{join}", "label": f"mock: {join.replace('_', ' ')} (top today, bottom proposed)",
                 "part": "mock " + join, "look": "all", "variant": "mock", "section": "join mockups", "resources": [res],
                 "render_match": f"liqjoin_mock_{join}_",
                 "size": {"drawSize": [6, 6], "footprint": [6, 6],
                          "source": "mock.py: a 6 x 6 cell frame at 128 px per cell (two 6 x 3 cell scenes stacked)"}})
w.flush()

lead = (
    "<p>Owner 2026-10-16: <i>“the flexible hose seems absolutely enormous when attached to things like pumps … The pump needs to "
    "be made to be commensurate with such a thick tube. And we might need to shrink the tube diameter a bit … anything the hoses "
    "can connect to (pumps, tanks, reels) as well as when you place a tank, reel, or pump next to each other some kind of "
    "connection should be visually apparent … The pipe needs connectors that show where it's connecting.”</i></p>"
    "<p><b>Numbers.</b> Hose today: 0.38 cell flat / 0.465 plump. Rigid pipe: 0.23. Pump today: 1 x 1 cell. "
    "<b>Proposed:</b> hose 0.65x = <b>0.25 flat / 0.30 plump</b> (still a little thicker than the pipe); "
    "pump <b>footprint 2 x 1, drawn 2 x 2</b> (about 1.9 x 1.1 cells of machine), its two port flanges sized to the 0.30 hose.</p>"
    "<p><b>Rows.</b> Pump, flange and saddle, one row per look (A = the only candidate; pick it, or note what to change). "
    "Then one mockup per join type, each column a look: <b>top half today, bottom half proposed</b> (pipe arm running to the "
    "tank or pump edge plus a flange; a flange pair where a pump or reel touches a tank; a saddle where a hose couples onto a "
    "pipe). Nothing is installed; the hose stays at today's width and the fittings stay switched off until you rule. "
    "Design note: design/RimMandrake/liquid_connections_visuals_2026-10-16.md.</p>")
(HERE / "textures_manifest.json").write_text(json.dumps({"rows": rows, "lead_html": lead}, indent=1))
print(len(rows), "rows")
