"""FLOWWORKS water-fix live check, rows A1 of FLOWWORKS_PUMP_FIX_D1_CANAL_STALLS and FLOWWORKS_SLUICE_FIX_BELOW_SOURCE_LUCK (2026-10-16).

  python.exe src/RimMandrake/FlowWorks/northstar/live_probes/fw_water_pump_sluice.py OUT_DIR [pump|sluice|all] [PUMP_ORIGIN x,z]
  (bridge held; the `river` test site loaded, no colonists needed; time only through jawa/safe_advance, 250-tick chunks)

PUMP: a dry 8-cell D=1 canal (no natural source anywhere near: plot far from the river) with a powered RM_LiquidPump on its
  north side pouring from a Dump tank filled to 100%. Bar: every canal cell reaches F=1 (far end included).
  Old kernel: wet-first inlet held a driver-fed D=1 run at 1,0,0,0 for ever.
SLUICE: a canal dug from the river's east bank (head cell touches river water) east along z=14 then south into the south-edge
  sink band (edge distance <= 9). RM_Sluice (shut) at the middle of the east leg. Bar: every cell ABOVE the gate fills (F=1).
  Control: reading the cells below the gate is recorded, not scored.
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import proof_hose as PH  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)
B = PH.PB()
V = PH.V
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
NS_PROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
res = {"script": "fw_water_pump_sluice.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": []}
rows = res["rows"]


def call(t, **k):
    return B.call(t, **k)


def row(rid, st, det):
    rows.append({"id": rid, "status": st, "detail": det})
    print(rid, st, json.dumps(det, default=str)[:300], flush=True)


def adv(n):
    r = call("jawa/safe_advance", ticks=n)
    return bool(r.get("success") and r.get("executed") == n and not r.get("triggers"))


def tick():
    return call("rimworld/get_game_info").get("ticksGame")


def fill_row(cells):
    xs, zs = [c[0] for c in cells], [c[1] for c in cells]
    r = call("jawa/static_call", type=PROMO, method="ProofFluidRow",
             args="%d,%d,%d,%d" % (min(xs), min(zs), max(xs) - min(xs) + 1, max(zs) - min(zs) + 1))
    txt = str(r.get("result") or "")
    out = {}
    for tok in (txt.split(" ", 3)[3] if txt.count(" ") >= 3 else "").split(";"):
        if ":" in tok:
            xz, rest = tok.split(":", 1)
            x, z = map(int, xz.split(","))
            d, f, fl, ter = rest.split("/", 3)
            out[(x, z)] = (int(d), int(f))
    return [out.get(tuple(c), (None, None))[1] for c in cells], [out.get(tuple(c), (None, None))[0] for c in cells]


def shot(name, rect, root=9.0):
    call("jawa/clear_ui", all=True)
    cx, cz = rect[0] + rect[2] // 2, rect[1] + rect[3] // 2
    call("rimworld/jump_camera_to_cell", x=cx, z=cz)
    call("rimworld/set_camera_zoom", rootSize=root)
    call("rimworld/jump_camera_to_cell", x=cx, z=cz)
    time.sleep(2.0)
    r = call("jawa/take_screenshot", fileName=name)
    src = r.get("filePath")
    for _ in range(20):
        if src and os.path.exists(src):
            break
        time.sleep(0.5)
    dst = os.path.join(OUT, name + ".png")
    shutil.copyfile(src, dst)
    res.setdefault("shots", []).append(dst)


def watch(cells, label, n=14, stop_full=True):
    seq = []
    for i in range(n):
        ok = adv(250)
        f, _ = fill_row(cells)
        seq.append({"tick": tick(), "fills": f, "ok": ok})
        print(label, i, seq[-1]["tick"], f, flush=True)
        if stop_full and all(v == 1 for v in f):
            break
    return seq


def dump():
    with open(os.path.join(OUT, "pump_sluice_result_%s.json" % (ONLY or "all")), "w") as f:
        json.dump(res, f, indent=1, default=str)


# ============================================================ PUMP
ox, oz = (int(v) for v in ((sys.argv[3] if len(sys.argv) > 3 else "30,150")).split(","))
ONLY = (sys.argv[2] if len(sys.argv) > 2 else "")
canal = [(ox + 2 + k, oz + 6) for k in range(8)]
pump, battery = (ox + 3, oz + 7), (ox + 4, oz + 7)
pipes, tank = [(ox + 3, oz + 8), (ox + 3, oz + 9)], (ox + 3, oz + 10)
rect = (ox - 2, oz, 16, 14)
if ONLY == "sluice":
    pass
elif not V.prepare_site(B, rect, rows, "PUMP_site_ready"):
    row("PUMP_canal_fills", "UNMEASURED", {"why": "site not ready"})
else:
    for c in canal:
        call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=1, setFill=-1)
    ops = ["RM_LiquidPump:%d,%d" % pump, "Battery:%d,%d" % battery] + ["RM_UniversalPipe:%d,%d" % p for p in pipes] + \
          ["RM_LiquidTank:%d,%d" % tank]
    bb = call("jawa/build_batch", ops=";".join(ops), faction="player", wipeExisting=False)
    adv(2)
    lt = call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % battery, limit=2) or {}
    bid = ((lt.get("things") or [{}])[0]).get("id")
    if bid is not None:
        call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
    pw = PH._powered(B, pump)
    ft = call("jawa/hose_probe", **{}) if False else B.hp("filltank:%d,%d=%s,120000" % (tank + (PH.LIQUID_WATER,)))   # UNITS (10,000 = one world level), not percent: 8 levels needed
    # set the tank to Dump through the real gizmo (as fw_live_checks.set_job)
    import re

    def gizmo_to(cell, prefix, want):
        call("rimworld/set_god_mode", enabled=True)
        try:
            call("rimworld/clear_selection")
            call("rimworld/click_cell", x=cell[0], z=cell[1])
            for _ in range(6):
                gz = (call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
                g = next((q for q in gz if str(q.get("label") or "").startswith(prefix)), None)
                if g is None:
                    return False
                if g.get("label") == want:
                    return True
                call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
            return False
        finally:
            call("rimworld/set_god_mode", enabled=False)
            call("rimworld/clear_selection")
    job_ok = gizmo_to(tank, "Job:", "Job: Dump")
    pr = call("jawa/static_call", type=NS_PROOF, method="ProofPump", args="%d,%d;pour" % pump)
    res["pump_setup"] = {"build": {k: bb.get(k) for k in ("success", "built", "failed")}, "powered_after": pw,
                         "filltank": ft.get("units"), "job_dump": job_ok, "proof_pour": pr.get("result")}
    f0, d0 = fill_row(canal)
    shot("pump_before", (ox - 2, oz + 2, 16, 10))
    seq = watch(canal, "PUMP", 16)
    shot("pump_after", (ox - 2, oz + 2, 16, 10))
    units = PH._tank(B, tank).get("units")
    res["pump_seq"] = seq
    pre = None if (pw is not None and job_ok and ft.get("success") and all(d == 1 for d in d0)) else \
        "precondition: powered %s job %s filltank %s depth %s" % (pw, job_ok, ft.get("success"), d0)
    full = bool(seq) and all(v == 1 for v in seq[-1]["fills"])
    row("PUMP_D1_canal_fills_far_end", "UNMEASURED" if pre else ("PASS" if full else "FAIL"),
        {"pre": pre, "start": f0, "end": seq[-1]["fills"] if seq else None, "ticks": len(seq) * 250,
         "tankUnitsAfter": units, "setup": res["pump_setup"]})
dump()

if ONLY == "pump":
    dump()
    sys.exit(0)
# ============================================================ SLUICE
sx, sz = 28, 4
srect = (28, 2, 20, 16)
head = [(30 + k, 14) for k in range(15)]            # x=30..44 along z=14 (river water at x=29)
leg = [(44, z) for z in range(13, 5, -1)]           # south leg into the edge band (z<=9 is a sink)
canal2 = head + leg
GATE = (36, 14)
call("jawa/clear_area", rect="%d,%d,%d,%d" % srect, dryRun=False)
call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % srect)
call("jawa/set_terrain_batch", ops="Soil:30,2,18,16")
for c in canal2:
    call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=1, setFill=-1)
cls = call("jawa/flowworks_body_report", x=29, z=14, classify=True)
res["sluice_body"] = cls.get("body")
sb = call("jawa/build_batch", ops="RM_Sluice:%d,%d" % GATE, faction="player", stuff="WoodLog", wipeExisting=False)
adv(2)
lt = call("jawa/list_things", rect="%d,%d,1,1" % GATE, limit=10, includePawns=False) or {}
res["sluice_build"] = {"success": sb.get("success"), "failed": sb.get("failed"),
                       "things": [t.get("def") or t.get("defName") for t in lt.get("things") or []]}
ex = call("jawa/flowworks_excavation_report", x=GATE[0], z=GATE[1])
res["gate_report"] = ex
shot("sluice_before", (28, 6, 20, 12), 10.0)
seq = watch(canal2, "SLUICE", 24, stop_full=False)
shot("sluice_after", (28, 6, 20, 12), 10.0)
res["sluice_seq"] = seq
above = [i for i, c in enumerate(canal2) if c[0] < GATE[0] and c[1] == 14]
below = [i for i, c in enumerate(canal2) if i not in above and c != GATE]
last = seq[-1]["fills"]
has_gate = "RM_Sluice" in str(res["sluice_build"]["things"]) or "Sluice" in str(res["sluice_build"]["things"])
ok = bool(last) and all(last[i] == 1 for i in above)
row("SLUICE_above_shut_gate_fills", "UNMEASURED" if not has_gate else ("PASS" if ok else "FAIL"),
    {"above_cells": [canal2[i] for i in above], "above_fills": [last[i] for i in above],
     "below_fills_not_scored": [last[i] for i in below], "gate_fill": last[canal2.index(GATE)], "ticks": len(seq) * 250,
     "build": res["sluice_build"]})
res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
dump()
