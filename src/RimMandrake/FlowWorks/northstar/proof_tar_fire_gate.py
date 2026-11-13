#!/usr/bin/env python3
"""Live proof: a shut sluice is a firebreak on a burning tar canal (SUMP_TAR_FIRE_NETWORK_1).

SUMP_TAR_HYDROLOGY_1 ruling 5: "Lit tar propagates along connected liquid -- a lit canal burns to its gate ... a belch during a
moat-burn is a genuine catastrophe." Offline, GateFirebreakChecks (selftest_flowworks_stock.py --only GateFirebreak_*) proves
the rule RM_LiquidFire.BurnableFluidAt now reads (RM_FireMath.CarriesFront + RM_FlowDoorRules.SealsLiquid); this script proves
the running fire obeys it on a real map. Scene, relative to --origin (ox, oz):

  canal   a 1x12 run at z=oz, x=ox..ox+11, dug 1 notch and filled with RM_Fluid_Tar (F=1 each square)
  sluice  a WoodLog RM_Sluice on the canal at x=ox+6 (spawned after the fill, shut)
  arm     a dry 1x4 arm dug 1 notch south of x=ox+2 (z=oz-1..oz-4), the belch's landing

Clauses (each reads RM_LiquidFireProof.ProofCell "FIRECELL x,z burning=.. pending=.."):

  A1  light x=ox; after 2,000 ticks squares ox..ox+5 burn and ox+6..ox+11 are neither burning nor pending (the gate holds);
  A2  then lift the sluice (RM_FlowDoorRules.ProofSetGate); after 2,000 more ticks ox+6..ox+11 burn (an open gate lets it on);
  A3  a belch mid-burn: a tar Flood_FlowWorks (jawa/flowworks_spawn_flood, the same three calls RM_IncidentWorker_TarPitBelch
      makes) seeded in the dry arm while the canal burns; after 3,000 ticks the canal squares that burned still burn and at
      least one arm square that took tar is burning (the belch neither puts the fire out nor floods in unlit).

    python3 proof_tar_fire_gate.py --clause A1|A2|A3|all [--origin 120,150]

Exit 0 when every asked clause holds, 1 when one fails, 2 when it could not measure. A2 needs A1's burn, so asking for A2
runs A1's steps too. Settings it touches are restored.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)

FIRE = "RimMandrake.FlowWorks.RM_LiquidFireProof"
DOORS = "RimMandrake.FlowWorks.RM_FlowDoorRules"
FILL = "RimMandrake.FlowWorks.RM_FluidIdentityProof"
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
# The live proof runs under Windows python.exe (WSL cannot reach the bridge on Windows loopback); same folder either way.
OUT = (("D:/" if os.name == "nt" else "/mnt/d/") + "ClaudeWork/rimmandrake/scratch/sump_tar_fire_network/live")
TAR = "RM_Fluid_Tar"
LEN, GATE, ARM_AT, ARM_LEN = 12, 6, 2, 4
SETTINGS = {"canalFireEnabled": True, "rainDousesLiquidFireEnabled": False}


# ============================================================================ pure (selftest_proof_tar_fire_gate.py)
def parse_cell(txt):
    """ "FIRECELL x,z burning=True pending=False ..." -> {"burning": bool, "pending": bool} or None."""
    m = re.search(r"FIRECELL (-?\d+),(-?\d+) burning=(True|False) pending=(True|False)", txt or "")
    if not m:
        return None
    return {"x": int(m.group(1)), "z": int(m.group(2)), "burning": m.group(3) == "True", "pending": m.group(4) == "True"}


def v_gate_holds(near, far):
    """A1: every near square burning, every far square neither burning nor pending. Can-see: the near side lit at all."""
    if any(c is None for c in near + far):
        return "UNMEASURED", {"why": "a ProofCell read failed"}
    if not any(c["burning"] for c in near):
        return "UNMEASURED", {"why": "the near side never lit: no front to stop", "near": near}
    ok = all(c["burning"] for c in near) and not any(c["burning"] or c["pending"] for c in far)
    return ("PASS" if ok else "FAIL"), {"nearBurning": sum(c["burning"] for c in near),
                                        "farLitOrPending": [c for c in far if c["burning"] or c["pending"]]}


def v_gate_passes(far):
    """A2: after the lift, every far square burns."""
    if any(c is None for c in far):
        return "UNMEASURED", {"why": "a ProofCell read failed"}
    ok = all(c["burning"] for c in far)
    return ("PASS" if ok else "FAIL"), {"farBurning": sum(c["burning"] for c in far), "of": len(far)}


def v_belch(canal_before, canal_after, arm, arm_fill):
    """A3: the canal squares burning before the belch still burn; at least one arm square that took tar burns.
    Can-see: the belch put tar in the arm at all (otherwise UNMEASURED: a flood that never arrived proves nothing)."""
    if any(c is None for c in canal_before + canal_after + arm):
        return "UNMEASURED", {"why": "a ProofCell read failed"}
    wet = [i for i, f in enumerate(arm_fill) if f]
    was = [i for i, c in enumerate(canal_before) if c["burning"]]
    if not was:
        return "UNMEASURED", {"why": "the canal was not burning before the belch"}
    if not wet and not any(c["burning"] for c in arm):
        return "UNMEASURED", {"why": "the belch put no tar in the arm", "armFill": arm_fill}
    still = all(canal_after[i]["burning"] for i in was)
    caught = any(c["burning"] for c in arm)
    return ("PASS" if still and caught else "FAIL"), {"canalStillBurning": still, "armBurning": [c["burning"] for c in arm],
                                                      "armFill": arm_fill}


# ============================================================================ live
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--clause", default="all", help="A1, A2, A3 or all")
    ap.add_argument("--origin", default="120,150")
    ap.add_argument("--out-dir", default=OUT)
    a = ap.parse_args(argv)
    want = {"A1", "A2", "A3"} if a.clause == "all" else {c.strip() for c in a.clause.split(",")}
    import validation_core as V
    B = V.Bridge()
    os.makedirs(a.out_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    res = {"script": "proof_tar_fire_gate.py", "clauses": sorted(want), "started": stamp, "rows": {}, "log": []}

    def save():
        with open(os.path.join(a.out_dir, "result_%s.json" % stamp), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def sc(typ, method, arg=""):
        r = B.call("jawa/static_call", type=typ, method=method, args=arg) or {}
        txt = str(r.get("result") if r.get("result") is not None else "")
        res["log"].append([method, arg, txt[:200]])
        return txt if r.get("success") and not txt.startswith("REFUSED") else None

    def sget(f):
        return (B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f) or {}).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))

    def cell(x, z):
        return parse_cell(sc(FIRE, "ProofCell", "%d,%d" % (x, z)))

    def fill_at(x, z):
        r = B.call("jawa/flowworks_excavation_report", x=x, z=z) or {}
        return r.get("fill") or 0

    def unmeasured(why):
        res["rows"]["site"] = {"status": "UNMEASURED", "why": why}
        save()
        print("UNMEASURED: %s" % why)
        return 2

    ox, oz = (int(v) for v in a.origin.split(","))
    canal = [(ox + i, oz) for i in range(LEN)]
    arm = [(ox + ARM_AT, oz - 1 - j) for j in range(ARM_LEN)]
    site = (ox - 2, oz - ARM_LEN - 2, LEN + 4, ARM_LEN + 5)
    saved = {}
    if (B.call("rimworld/get_ui_state") or {}).get("programState") != "Playing":
        print("UNMEASURED: the game is not Playing")
        return 2
    try:
        B.call("rimworld/pause_game", pause=True)
        B.call("jawa/kill_hostiles")
        for f, v in SETTINGS.items():
            saved[f] = sget(f)
            sset(f, v)
        res["settingsBefore"] = saved
        sc(NSP, "ProofResetRect", "%d;%d;%d;%d" % site)
        rows = []
        if not V.prepare_site(B, site, rows, "TFG_site"):
            return unmeasured("site not ready: %s" % rows[:2])
        B.call("rimworld/pause_game", pause=True)
        for x, z in canal + arm:
            r = B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=1, setBodyWaterM=0.0) or {}
            if not r.get("success"):
                return unmeasured("dig (%d,%d) refused: %r" % (x, z, str(r)[:160]))
        for x, z in canal:
            if not (sc(FILL, "ProofFillWithFluid", "%d,%d,1,%s" % (x, z, TAR)) or "").startswith("FILLED"):
                return unmeasured("tar fill (%d,%d) refused" % (x, z))
        gx, gz = canal[GATE]
        r = B.call("jawa/spawn_batch", ops="RM_Sluice:%d,%d" % (gx, gz), stuff="WoodLog") or {}
        shut = sc(DOORS, "ProofSetGate", "current|%d,%d|false" % (gx, gz))
        if not shut or "open=False" not in shut:
            return unmeasured("no shut sluice at the gate square: spawn %r set %r" % (str(r)[:160], shut))
        lit = sc(FIRE, "ProofIgnite", "%d,%d" % canal[0])
        if not lit or not lit.startswith("LIT"):
            return unmeasured("the canal mouth did not light: %r" % res["log"][-1])
        B.ticks(2000)
        near, far = [cell(*c) for c in canal[:GATE]], [cell(*c) for c in canal[GATE:]]
        verdicts = {}
        if want & {"A1", "A2"}:
            verdicts["A1"] = v_gate_holds(near, far)
        if "A3" in want:
            before = near
            fl = B.call("jawa/flowworks_spawn_flood", x=arm[0][0], z=arm[0][1], fluidDefName=TAR, volume=10) or {}
            res["belch"] = fl
            B.ticks(3000)
            verdicts["A3"] = v_belch(before, [cell(*c) for c in canal[:GATE]], [cell(*c) for c in arm],
                                     [fill_at(*c) for c in arm])
        if "A2" in want:
            up = sc(DOORS, "ProofSetGate", "current|%d,%d|true" % (gx, gz))
            if not up or "open=True" not in up:
                verdicts["A2"] = ("UNMEASURED", {"why": "the sluice did not lift: %r" % up})
            else:
                B.ticks(2000)
                verdicts["A2"] = v_gate_passes([cell(*c) for c in canal[GATE:]])
        verdicts = {k: v for k, v in verdicts.items() if k in want}
        for k, (st, det) in sorted(verdicts.items()):
            res["rows"][k] = {"status": st, "detail": det}
            print("%s %s %s" % (k, st, json.dumps(det, default=str)[:400]))
        save()
        sts = [st for st, _ in verdicts.values()]
        return 0 if sts and all(s == "PASS" for s in sts) else (1 if "FAIL" in sts else 2)
    finally:
        for f, v in saved.items():
            if v is not None:
                sset(f, v)
        save()
        print("result: %s" % os.path.join(a.out_dir, "result_%s.json" % stamp))


if __name__ == "__main__":
    sys.exit(main())
