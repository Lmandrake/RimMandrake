"""DEEP LAKE live proof (POND_ELEVATION_BUILD_LAKES_RUN_DEEP; design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md
§9, the debug_process rule: the proof script is written with the build item).

  python.exe src/RimMandrake/FlowWorks/northstar/deep_lake_proof.py [out.json] [--origin X,Z] [--size N] [--fresh-map]

Run from the repo root with python.exe; the bridge must be held. Exit 0 = every MEASURED row PASS (owed rows are UNMEASURED
and say why). NEVER RUN BY THE BUILD ITEM ITSELF: written offline 2026-10-15 (no bridge in that session).

Owner words this proves: (2026-10-12) "There's nothing wrong with saying the center of ponds or especially large rivers and
lakes and oceans might go down way past 4." · ruling 4 "Natural ponds and lakes when pumped dry would leave just such gradual
terrain so no chance to fall in and get stuck." · ruling 7 a refilled pond returns to its exact shape. Card 2026-10-15:
"Deeper ponds (lakes deeper than 4) ... Today? -> Build it today".

Scene: a SIZE x SIZE rectangular lake (default 72 = 5,184 squares, past the old 4,000-square ocean cap) painted at --origin
(default 60,60) by RM_NorthstarProofs.ProofDeepLake "paint" (WaterShallow 3 squares deep at the edge, WaterDeep inside), the
site cleared first by validation_core.prepare_site. For the run lakeDepthScale = 2 (a deep floor whatever the debug
map's hilliness; LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP replaced the radial slope) and deepBedMaxDepth = 20; restored after. Every read is jawa/static_call
RM_NorthstarProofs.ProofDeepLake ("BODY ..." / "STOCK ..." / "SHAPE ...", key=value tokens) or ProofClimb "pawn:<id>".
The stock is SET by the proof (a stand-in for pumps); conservation of real pumping is the offline selftests'
(DeepBed_drawdown_sheds_shallowest_first_and_refills_lifo_exact, northstar/selftest_conservation_roundtrip.py).

Rows (MEASURED): DL_lake_over_4000_is_limited, DL_drained_reads_gradual_hollow, DL_shallow_dries_first,
DL_colonist_free_in_bowl, DL_colonist_walks_out, DL_refill_restores_exact_shape.  OWED: DL_save_reload_bowl_identical.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PROOF_TYPE = "RimMandrake.FlowWorks.RM_NorthstarProofs"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
RIM = 3
DRAIN_TO = 0.25        # of capacity: dries the rim and the shelves, leaves the deep middle wet
WAIT_OUT = 4000        # lakebed walking is slow (pathCost 300); a bed-5 square is ~7 squares from dry land
OLD_CAP = 4000         # RM_BedMath.OceanWalkCells

OWED = {
    "DL_save_reload_bowl_identical": "needs a save + reload cycle on the bridge: the bed record (RM_bedDepthRecord) and a "
                                     "packed footprint must read back the same SHAPE hash",
}


# ============================================================================ verdicts (pure; selftest_deep_lake_proof.py)
def parse(txt):
    """'BODY a=1 b=x ...' -> dict; '' / REFUSED -> {}."""
    txt = txt or ""
    if not txt or txt.startswith("REFUSED"):
        return {}
    kv = {}
    for tok in txt.replace("|", " ").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def _int(kv, k, default=None):
    try:
        return int(kv[k])
    except (KeyError, ValueError, TypeError):
        return default


def body_verdict(kv, size):
    """DL_lake_over_4000_is_limited: the whole painted lake is ONE limited body past the old cap, with beds past 4."""
    cells, deepest = _int(kv, "cells"), _int(kv, "deepest")
    if cells is None or deepest is None:
        return "UNMEASURED", {"why": "no BODY line", "kv": kv}
    ok = cells == size * size and cells > OLD_CAP and kv.get("limitless") == "False" and kv.get("truncated") == "False" and deepest > 4
    return ("PASS" if ok else "FAIL"), {"kv": kv, "want": {"cells": size * size, "limitless": "False", "deepest>": 4}}


def hollow_verdict(kv):
    """DL_drained_reads_gradual_hollow: part drained, the dry floor deeper than 4, the abyss bed laid, hollows on.
    LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP (owner R11): floors are irregular and may be chasm-like, so the old "every step <= 1"
    bowl rule is gone (stepDeep / stepAll are recorded, not judged); that nobody is trapped is DL_colonist_walks_out's row
    (the way-out pass: no step over lakeWayOutMetres on a route to land)."""
    need = ("wet", "dry", "deepestDry", "stepDeep", "stepAll", "lakebedAbyss")
    if any(_int(kv, k) is None for k in need) or kv.get("hollows") != "True":
        return "UNMEASURED", {"why": "no SHAPE line, or hollows are off", "kv": kv}
    ok = _int(kv, "dry") > 0 and _int(kv, "wet") > 0 and _int(kv, "deepestDry") > 4 and _int(kv, "lakebedAbyss") > 0
    return ("PASS" if ok else "FAIL"), {"kv": kv}


def drawdown_verdict(kv):
    """DL_shallow_dries_first: no dry bed deeper than the shallowest wet one (the lake drops off its rim and shelves)."""
    a, b = _int(kv, "maxDryBed"), _int(kv, "minWetBed")
    if a is None or b is None or _int(kv, "wet", 0) == 0:
        return "UNMEASURED", {"why": "no SHAPE line with wet squares", "kv": kv}
    return ("PASS" if a <= b else "FAIL"), {"maxDryBed": a, "minWetBed": b}


def refill_verdict(full_before, full_after):
    """DL_refill_restores_exact_shape: back to full, every square wet, nothing on the stack, the same terrain hash."""
    if not full_before or not full_after or "hash" not in full_before or "hash" not in full_after:
        return "UNMEASURED", {"why": "missing a SHAPE read", "before": full_before, "after": full_after}
    ok = (full_after["hash"] == full_before["hash"] and _int(full_after, "dry") == 0 and _int(full_after, "receded") == 0
          and _int(full_after, "wet") == _int(full_before, "wet"))
    return ("PASS" if ok else "FAIL"), {"before": full_before.get("hash"), "after": full_after.get("hash"),
                                        "dryAfter": full_after.get("dry"), "recededAfter": full_after.get("receded")}


def free_verdict(kv):
    """DL_colonist_free_in_bowl: ProofClimb pawn line on a drained bed square past 4: not held, not trapped, not a pocket."""
    if not kv or "held" not in kv:
        return "UNMEASURED", {"why": "ProofClimb gave no pawn line", "kv": kv}
    if kv.get("gen") is None or kv.get("gen") != kv.get("built"):
        return "UNMEASURED", {"why": "pocket grid stale (gen != built)", "kv": kv}
    ok = kv.get("held") == "False" and kv.get("trapped") == "False" and kv.get("pocket") == "False"
    return ("PASS" if ok else "FAIL"), {"kv": kv}


def out_of(rect, xz):
    x0, z0, w, h = rect
    return not (x0 <= xz[0] < x0 + w and z0 <= xz[1] < z0 + h)


def walk_verdict(order_row, rect):
    """DL_colonist_walks_out: a drafted order to dry land outside the lake ends outside it."""
    if not order_row or order_row.get("orderAccepted") is not True or not (order_row.get("ticksElapsed") or 0) > 0:
        return "UNMEASURED", {"why": "order not accepted or the game never ticked", "order": order_row}
    pos = order_row.get("position") or order_row.get("end") or order_row.get("cell")
    if isinstance(pos, dict):
        pos = (pos.get("x"), pos.get("z"))
    if not pos or pos[0] is None:
        return "UNMEASURED", {"why": "no end position in the order row", "order": order_row}
    return ("PASS" if out_of(rect, pos) else "FAIL"), {"end": pos, "rect": rect}


def cell_of(kv, key):
    v = (kv or {}).get(key) or "none"
    if v == "none":
        return None
    x, z = v.split(",")
    return int(x), int(z)


# ============================================================================ live run
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="60,60")
    ap.add_argument("--size", type=int, default=72)
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "deep_lake_proof_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "deep_lake_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-36s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def lake(arg):
        r = B.call("jawa/static_call", type=PROOF_TYPE, method="ProofDeepLake", args=arg) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return (parse(txt) if r.get("success") is True else {}), txt

    def climb(arg):
        r = B.call("jawa/static_call", type=PROOF_TYPE, method="ProofClimb", args=arg) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return (parse(txt) if r.get("success") is True else {}), txt

    def sget(f):
        return (B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f) or {}).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v)) or {"success": False}

    ox, oz = (int(v) for v in a.origin.split(","))
    n = a.size
    rect = (ox, oz, n, n)
    mid = "%d,%d" % (ox + n // 2, oz + n // 2)
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if ok:
        res["site_calm"] = V.site_calm(B)   # TESTENV_PREFLIGHT_HARDEN_TRISPIKE_AT_ARM: map-gen hostiles/hives stop safe_advance at arm
    # HARNESS (belt live 2026-10-22): LAKE_GROUNDWATER_REFILL (392300ef0d) makes an inland lake limitless past a rainfall-keyed
    # cell cutoff (600 wet / 5000 temperate): on a wet fresh map the 5,184-square lake read limitless=True deepest=0 and every
    # row judged a lake that cannot drain. The proof turns the wetness cut off for its run (restored with the rest).
    # HARNESS (fixer G 2026-10-22, DL_refill_restores_exact_shape FAIL x2 after the shelfCell fix): the colonist rows tick the
    # game ~4,000 ticks between drain and refill, and with pondDepthEnabled (default ON) every live pulse runs StagePond on this
    # limited still-water body instead of Recede/Restore: it re-lays the wet squares as part-depth stage water (recorded
    # original, NOT on the receded stack), so the proof's LIFO refill (SettleRecession) left them staged and the terrain hash
    # differed. Before the shelfCell fix those rows were UNMEASURED and nothing ticked (PASS). The proof drives the
    # full-or-empty recession, so the live pulses must run that same model: pondDepthEnabled off for the run, restored after.
    FIELDS = ("wetnessCutoffEnabled", "deepBedsEnabled", "lakeDepthScale", "deepBedMaxDepth", "drainableLakeMaxCells", "pondBedHollowEnabled",
              "recessionEnabled", "refillWaitsForOccupants", "pondDepthEnabled")
    before = {f: sget(f) for f in FIELDS}
    res["settings_before"] = before
    try:
        if not ok or not V.prepare_site(B, (ox - 4, oz - 4, n + 8, n + 8), rows, "DL_site_ready"):
            row("DL_site", "UNMEASURED", "SITE", {"why": "site not ready / not playing"})
            return 2
        for f, v in (("deepBedsEnabled", True), ("lakeDepthScale", 2.0), ("deepBedMaxDepth", 20),
                     ("drainableLakeMaxCells", 40000), ("pondBedHollowEnabled", True), ("recessionEnabled", True),
                     ("refillWaitsForOccupants", False), ("wetnessCutoffEnabled", False), ("pondDepthEnabled", False)):
            if sset(f, v).get("success") is False:   # an unset knob = the owner's value, not the proof's: every row below is suspect
                row("DL_site", "UNMEASURED", "HARNESS", {"why": "mod_settings_field set refused", "field": f})
                return 2
        _, painted = lake("paint;%d;%d;%d;%d;%d" % (ox, oz, n, n, RIM))
        kv, txt = lake("form;" + mid)
        st, det = body_verdict(kv, n)
        row("DL_lake_over_4000_is_limited", st, "MOD", dict(det, painted=painted, txt=txt))
        full_before, t0 = lake("shape;" + mid)
        _, ts = lake("stock;%s;%s" % (mid, DRAIN_TO))
        drained, t1 = lake("shape;" + mid)
        drain_ok = not ts.startswith("REFUSED") and bool(ts) and (_int(drained, "dry") or 0) > 0
        st, det = hollow_verdict(drained)
        row("DL_drained_reads_gradual_hollow", st, "MOD", dict(det, stock=ts))
        st, det = drawdown_verdict(drained)
        row("DL_shallow_dries_first", st, "MOD", det)
        shelf = cell_of(drained, "shelfCell")
        if shelf is None:
            row("DL_colonist_free_in_bowl", "UNMEASURED", "MOD", {"why": "no dry square past bed 4", "shape": t1})
            row("DL_colonist_walks_out", "UNMEASURED", "MOD", {"why": "no dry square past bed 4"})
        else:
            r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=shelf[0], z=shelf[1], faction="player", count=1) or {}
            pid = ((r.get("pawns") or [{}])[0]).get("id")
            B.ticks(70)
            kv, txt = climb("pawn:%s" % pid)
            st, det = free_verdict(kv)
            row("DL_colonist_free_in_bowl", st, "MOD", dict(det, txt=txt, cell=shelf))
            target = (ox - 2, shelf[1])
            o = B.call("jawa/order_pawn", pawnId=pid, x=target[0], z=target[1], waitTicks=WAIT_OUT, draft=True) or {}
            prow = {}
            for p in o.get("pawns") or []:
                if p.get("id") == pid:
                    prow = dict(p, ticksElapsed=o.get("ticksElapsed"))
            st, det = walk_verdict(prow, rect)
            row("DL_colonist_walks_out", st, "MOD", det)
        _, ts2 = lake("stock;%s;1" % mid)
        full_after, t2 = lake("shape;" + mid)
        st, det = refill_verdict(full_before, full_after)
        if not drain_ok:   # nothing was drained, so "back to the same shape" is true of a lake that never moved: not a pass
            st, det = "UNMEASURED", dict(det, why="the drain-down did not happen (stock refused or no dry square)", stockRead=ts[:120])
        row("DL_refill_restores_exact_shape", st, "MOD", dict(det, stock=ts2, txt=[t0, t2]))
        for rid, why in OWED.items():
            row(rid, "UNMEASURED", "OWED", {"why": why})
    finally:
        for f, v in before.items():
            if v is not None:
                sset(f, v)
        res["settings_restored"] = {f: sget(f) for f in FIELDS}
        save()
    measured = [r for r in rows if r["class"] != "OWED" and r["id"] != "DL_site_ready"]
    return 0 if measured and all(r["status"] == "PASS" for r in measured) else 1


if __name__ == "__main__":
    sys.exit(main())
