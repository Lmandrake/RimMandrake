"""pit_water_fixes_live.py -- permanent live proof rows for the owner's 2026-10-24 FlowWorks review
(infrastructure/state/evidence/owner_review_FW_20261024.md), one row per live-observable finding. Each row is a deterministic
state read that FAILS on the behaviour the owner saw and PASSES on the fix (the verdict functions below are pure; the
selftest selftest_pit_water_fixes_live.py feeds them old-shaped and fixed readings).

    python.exe src/RimMandrake/FlowWorks/northstar/pit_water_fixes_live.py [--fresh-map] [out.json]

Run from the repo root with python.exe while holding the bridge, on the flowworks tier. God mode and the storyteller are
restored in `finally`. "Could not ask" is UNMEASURED, never FAIL (a refused call, a pawn that never got onto its square).

Rows (item -> PROVE / EXPECT / LIES):
  PWF_swim_getter_patched        SWIM_DEPTH_FIX_TWO_METRES_WALKED / DEEP_PIT_SWIM_FIX_FIVE_METRES_WALKS / DRAFTED_SWIMMER...
                                 jawa/harmony_patches Verse.Pawn get_Swimming. EXPECT a postfix
                                 RM_Patch_Pawn_SwimPose.Postfix (old build: none, Swimming came from the joy-swim job only).
                                 LIES: a patch present but never true -> the next rows read its answer on real squares.
  PWF_swim_2m                    SWIM_DEPTH_FIX_TWO_METRES_WALKED. A colonist standing in 2.0 m dug water (dig 4, fill 4):
                                 SwimsAt True; the same colonist in 1.0 m (dig 2, fill 2) SwimsAt False (control: the
                                 rule is not "any water"). Old: 2.0 m walked (False).
  PWF_swim_5m_surface            DEEP_PIT_SWIM_FIX_FIVE_METRES_WALKS. A colonist in a brim-full 5 m pit (dig 10, fill 10):
                                 SwimsAt True and ProofPawnSink sink <= 0.15 (drawn at the surface). Old: walking on the
                                 floor, sink at the cap (2.4 = 8 x 0.3, "jump in").
  PWF_drafted_swimmer_all_cells  DRAFTED_SWIMMER_FIX_PIT_BOTTOM_ROW. A 3x4 pit, 3 m water (dig 6, fill 6): the colonist is
                                 ordered to EVERY square drafted, then every square undrafted; each order arrives, SwimsAt
                                 is True there and the sink <= 0.15 (floating at the surface on every row). Old: drafted
                                 not swimming; floaters clamped on the floor, the bottom row only.
  PWF_wet_pit_enterable          WATERED_PIT_FIX_NO_WAY_IN. A 1.5 m pit holding 1.5 m (dig 3, fill 3): a colonist on the
                                 rim walks to the middle square and back out. Old: "no way in" (not traversable).
  PWF_wet_pit_ladder_ramp        WATERED_PIT_FIX_NO_WAY_IN. jawa/build_check RM_Ladder (north edge square, facing the rim)
                                 and RM_PitRamp (same, facing uphill) in the WET pits; control: the same in a DRY pit of the
                                 same depth must be accepted, else UNMEASURED. Old: refused in water ("needs a pit").
  PWF_click_patch_wired          PIT_CLICK_FIX_SHIFTED_ONE_DOWN. harmony_patches FloatMenuOptionProvider_DraftedMove
                                 GetSingleOption carries RM_Patch_PitClickDrawnRow.Prefix, AND on the live sinks of a dry
                                 1 m pit (RestingSinkAt per row) the drawn-click pick of a middle row is the row NORTH of it
                                 (the Python replica of PickRowForDrawnClick). Old: no prefix; the clicked row.
  PWF_click_end_to_end           PIT_CLICK_FIX_SHIFTED_ONE_DOWN. select_things + rimworld/right_click_cell on that middle
                                 row with the drafted colonist; EXPECT it walks to the picked row. If the synthetic click
                                 issues no order at all (known trap) the row is UNMEASURED HARNESS.
  PWF_shallow_depth_shader       SHALLOW_RIPPLE_FIX_DARK_RING_STATIC. get_defs RM_WaterThin, RM_WaterVeryShallow
                                 waterDepthShader non-empty (control WaterShallow non-empty). Old: none (dark, ring static).
  PWF_godmode_ladder_free        GODMODE_LADDER_FIX_ASKS_FOR_WOOD. God mode on; a colonist downed in a sheer 2 m pit (dig 4)
                                 with every other colonist drafted (no rescuer); within 750 ticks a FINISHED RM_LadderPortable
                                 or RM_Ladder stands in the pit and no Blueprint_/Frame_. Old: a blueprint waiting on wood.
  PWF_sluice_closed_blocks       SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS (owner: "When closed, it is not traversible").
                                 A colonist boxed in walls with a closed RM_Sluice in the south wall is ordered outside;
                                 EXPECT it does NOT arrive. Control: the same box with a vanilla Door -> it arrives (else
                                 UNMEASURED). Old (and until that item lands): walks through like a door -> FAIL MOD.
Not state-readable here (art; owned by the offline art checks, items filed): spike draw over walls/submerged, plank cover,
sprinkler seat, pipe joins, gate/grate open art, portable ladder north art.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

SWIM = "RimMandrake.FlowWorks.Swimming.RM_Patch_Pawn_SwimPose"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
SINKP = "RimMandrake.FlowWorks.RM_Patch_PitDepthDrawOffset"
LADDERS = ("RM_LadderPortable", "RM_Ladder")
FLOAT_SINK_MAX = 0.15
MAX_ROWS = 4            # RM_PitDrawMath.SinkCapLevels / 2

ITEMS = {
    "PWF_swim_getter_patched": "SWIM_DEPTH_FIX_TWO_METRES_WALKED",
    "PWF_swim_2m": "SWIM_DEPTH_FIX_TWO_METRES_WALKED",
    "PWF_swim_5m_surface": "DEEP_PIT_SWIM_FIX_FIVE_METRES_WALKS",
    "PWF_drafted_swimmer_all_cells": "DRAFTED_SWIMMER_FIX_PIT_BOTTOM_ROW",
    "PWF_wet_pit_enterable": "WATERED_PIT_FIX_NO_WAY_IN",
    "PWF_wet_pit_ladder_ramp": "WATERED_PIT_FIX_NO_WAY_IN",
    "PWF_click_patch_wired": "PIT_CLICK_FIX_SHIFTED_ONE_DOWN",
    "PWF_click_end_to_end": "PIT_CLICK_FIX_SHIFTED_ONE_DOWN",
    "PWF_shallow_depth_shader": "SHALLOW_RIPPLE_FIX_DARK_RING_STATIC",
    "PWF_godmode_ladder_free": "GODMODE_LADDER_FIX_ASKS_FOR_WOOD",
    "PWF_sluice_closed_blocks": "SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS",
}


# ---------------------------------------------------------------- pure verdicts (selftested offline)
def kv(txt):
    out = {}
    for tok in (txt or "").replace("|", " ").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def tbool(v):
    s = str(v).strip().lower()
    return True if s == "true" else (False if s == "false" else None)


def patch_names(harmony, kind):
    """Every patchMethod of `kind` ('postfixes'/'prefixes') in a jawa/harmony_patches answer; None if it did not answer."""
    if not isinstance(harmony, dict) or not harmony.get("success"):
        return None
    out = []
    for m in harmony.get("methods") or []:
        out += [str(p.get("patchMethod")) for p in (m.get(kind) or [])]
    return out


def v_patched(harmony, kind, suffix):
    names = patch_names(harmony, kind)
    if names is None:
        return "UNMEASURED", {"why": "harmony_patches did not answer"}
    return ("PASS" if any(n.endswith(suffix) for n in names) else "FAIL"), {kind: names}


def pick_row(z_click, click_z, sink, max_rows=MAX_ROWS):
    """Python replica of RM_PitDrawMath.PickRowForDrawnClick (the C# selftest pins the C# side)."""
    s0 = sink(z_click)
    if s0 is None or s0 != s0 or not s0 > 0:
        return z_click
    best, best_err = z_click, abs(z_click + 0.5 - s0 - click_z)
    for k in range(1, max_rows + 1):
        z = z_click + k
        s = sink(z)
        if s is None or s != s or not s > 0:
            break
        err = abs(z + 0.5 - s - click_z)
        if err < best_err - 1e-4:
            best, best_err = z, err
    return best


def v_click_wired(harmony, sinks, z_click):
    """sinks: {z: RestingSinkAt} for the clicked column. PASS = prefix present AND the live pick is not the clicked row."""
    st, det = v_patched(harmony, "prefixes", "RM_Patch_PitClickDrawnRow.Prefix")
    if not sinks or any(v is None for v in sinks.values()):
        return "UNMEASURED", dict(det, why="RestingSinkAt did not answer", sinks=sinks)
    picked = pick_row(z_click, z_click + 0.5, lambda z: sinks.get(z, 0.0))
    det = dict(det, sinks=sinks, clicked=z_click, picked=picked)
    if st != "PASS":
        return st, det
    return ("PASS" if picked != z_click else "FAIL"), det


def v_click_e2e(z_click, picked, end_z, moved):
    if picked == z_click:
        return "UNMEASURED", {"why": "not discriminating: the pick is the clicked row"}
    if not moved or end_z is None:
        return "UNMEASURED", {"why": "the synthetic click issued no move (HARNESS)", "endZ": end_z}
    return ("PASS" if end_z == picked else "FAIL"), {"clicked": z_click, "picked": picked, "endZ": end_z}


def v_swim_2m(swims_2m, swims_1m):
    if swims_2m is None or swims_1m is None:
        return "UNMEASURED", {"why": "SwimsAt did not answer"}
    det = {"swims2m": swims_2m, "swims1m": swims_1m}
    if swims_1m:
        return "FAIL", dict(det, why="1 m water swims: the rule is not head-under")
    return ("PASS" if swims_2m else "FAIL"), det


def v_float(swims, sink):
    if swims is None or sink is None:
        return "UNMEASURED", {"why": "SwimsAt/ProofPawnSink did not answer"}
    return ("PASS" if swims and abs(sink) <= FLOAT_SINK_MAX else "FAIL"), {"swims": swims, "sink": sink}


def v_all_cells(cells):
    """cells: [{'cell','mode','arrived','swims','sink'}]. Every square, both modes, arrived + swimming + at the surface."""
    if not cells:
        return "UNMEASURED", {"why": "no cell ordered"}
    if any(c.get("swims") is None or c.get("sink") is None for c in cells if c.get("arrived")):
        return "UNMEASURED", {"why": "SwimsAt/ProofPawnSink did not answer", "cells": cells}
    bad = [c for c in cells if not (c.get("arrived") and c.get("swims") and abs(c.get("sink")) <= FLOAT_SINK_MAX)]
    return ("PASS" if not bad else "FAIL"), {"n": len(cells), "bad": bad[:8]}


def v_enter(in_arrived, out_arrived):
    if in_arrived is None or out_arrived is None:
        return "UNMEASURED", {"why": "order_pawn did not answer"}
    return ("PASS" if in_arrived and out_arrived else "FAIL"), {"in": in_arrived, "out": out_arrived}


def find_key(o, key):
    if isinstance(o, dict):
        if key in o:
            return o[key]
        for v in o.values():
            r = find_key(v, key)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find_key(v, key)
            if r is not None:
                return r
    return None


def accepted(r):
    """jawa/build_check -> True/False/None (None = could not read)."""
    if not isinstance(r, dict) or r.get("success") is False:
        return None
    for k in ("accepted", "allAccepted", "canPlace"):
        v = find_key(r, k)
        if isinstance(v, bool):
            return v
        if tbool(v) is not None:
            return tbool(v)
    return None


def v_build(wet, dry):
    """wet/dry: {'RM_Ladder': bool|None, 'RM_PitRamp': bool|None}."""
    det = {"wet": wet, "dryControl": dry}
    if any(dry.get(k) is not True for k in wet):
        return "UNMEASURED", dict(det, why="dry control not accepted: the placement itself is wrong (SITE)")
    if any(v is None for v in wet.values()):
        return "UNMEASURED", dict(det, why="build_check did not answer")
    return ("PASS" if all(wet.values()) else "FAIL"), det


def v_shader(values, control):
    if not control:
        return "UNMEASURED", {"why": "control WaterShallow reads no shader: the field is not readable", "values": values}
    bad = [k for k, v in values.items() if not v or str(v).lower() in ("null", "none")]
    return ("PASS" if not bad else "FAIL"), {"values": values, "control": control, "missing": bad}


def v_godmode(defs_in_pit):
    """defs_in_pit: def names of things on the pit squares after the wait."""
    built = [d for d in defs_in_pit if d in LADDERS]
    pending = [d for d in defs_in_pit if d.startswith("Blueprint") or d.startswith("Frame")]
    st = "PASS" if built and not pending else "FAIL"
    return st, {"built": built, "blueprintsOrFrames": pending}


def v_sluice(sluice_arrived, door_arrived):
    if door_arrived is not True:
        return "UNMEASURED", {"why": "control: the colonist did not leave through a vanilla door (SITE)", "door": door_arrived}
    if sluice_arrived is None:
        return "UNMEASURED", {"why": "order_pawn did not answer"}
    return ("PASS" if not sluice_arrived else "FAIL"), {"throughSluice": sluice_arrived, "throughDoor": door_arrived}


# ---------------------------------------------------------------- live driver
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--origin", default="140,100")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(r"D:\ClaudeWork\rimmandrake\scratch", "pit_water_fixes_live_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "pit_water_fixes_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    could_not = []

    def row(rid, st, det):
        if st == "FAIL" and (could_not or res.get("siteDig")):     # a refused call or a refused site dig: could not ask
            det = dict(det, couldNotAsk=list(could_not) + list(res.get("siteDig") or []))
            st = "UNMEASURED"
        del could_not[:]
        rows.append({"id": rid, "item": ITEMS.get(rid), "status": st, "detail": det})
        print("%-30s %-10s %s" % (rid, st, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def sc(typ, method, arg=""):
        r = B.call("jawa/static_call", type=typ, method=method, args=arg) or {}
        if not r.get("success"):
            could_not.append("%s(%s) refused: %s" % (method, arg[:30], str(r.get("message") or r.get("error"))[:80]))
            return None
        return str(r.get("result"))

    def dig(c, n, fill=-1):
        r = B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=fill) or {}
        if r.get("success") is False:
            could_not.append("dig %s refused" % (c,))

    def pit(o, w, h, n, fill):
        for i in range(w):
            for j in range(h):
                dig((o[0] + i, o[1] + j), n, fill)

    def spawn(c):
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=c[0], z=c[1], faction="player", count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if not pid:
            could_not.append("spawn at %s failed" % (c,))
        return pid

    def order(pid, c, draft=True, wait=400):
        r = B.call("jawa/order_pawn", pawnId=pid, x=c[0], z=c[1], waitTicks=wait, draft=draft, unpause=True) or {}
        p = (r.get("pawns") or [{}])[0]
        if not r.get("pawns"):
            could_not.append("order %s -> %s no answer" % (pid, c))
            return None, None
        return bool(p.get("arrived")), p

    def swims(pid, c):
        return tbool(sc(SWIM, "SwimsAt", "%s|%d,%d" % (pid, c[0], c[1])))

    def sink(pid):
        return fnum(kv(sc(PROMO, "ProofPawnSink", pid) or "").get("sink"))

    def things_in(rect):
        lt = B.call("jawa/list_things", rect="%d,%d,%d,%d" % rect, limit=80) or {}
        return [str(t.get("def") or t.get("defName") or "") for t in lt.get("things") or []]

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    save()
    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    try:
        if not ok:
            for rid in ITEMS:
                row(rid, "UNMEASURED", {"why": "not playing", "class": "HARNESS"})
            return 2
        B.call("jawa/kill_hostiles")
        B.call("jawa/quiet_site", action="apply", clearThreats=True, proximityLetters=True)
        B.call("jawa/debug_settings", action="set", field="enableStoryteller", value=False)
        B.call("rimworld/set_god_mode", enabled=False)
        rect = (ox, oz, 40, 26)
        site_rows = []
        if not V.prepare_site(B, rect, site_rows, "PWF_site"):
            for rid in ITEMS:
                row(rid, "UNMEASURED", {"why": "site not ready", "class": "SITE", "site": site_rows[:2]})
            return 2
        # map colonists: drafted where they stand (no wandering into sites, no rescuer for the god-mode row)
        res["mapColonists"] = []
        for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
            if p.get("isPlayer") and not p.get("dead") and p.get("x") is not None:
                B.call("jawa/order_pawn", pawnId=p.get("id"), x=p.get("x"), z=p.get("z"), waitTicks=1, draft=True)
                res["mapColonists"].append(p.get("id"))
        rspan = fnum((B.call("jawa/mod_settings_field", typeName="RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings",
                              action="get", field="pitRampMaxSpan") or {}).get("value")) or 2
        rd = int(max(1, min(3, rspan)))
        W, R, C, CR = P(2, 2), P(7, 2), P(11, 2), P(30, 2)   # wet 1.5 m pit 3x4; wet ramp pit 3x3; dry controls
        S2, S1, S5 = P(16, 2), P(20, 2), P(24, 2)      # 2 m, 1 m (control), 5 m brim-full 3x3
        DS, CK, GM, SL = P(2, 11), P(8, 11), P(14, 11), P(22, 11)
        pit(W, 3, 4, 3, 3)
        pit(R, 3, 3, rd, rd)
        pit(C, 3, 4, 3, -1)
        pit(CR, 3, 3, rd, -1)
        pit(S2, 3, 3, 4, 4)
        pit(S1, 3, 3, 2, 2)
        pit(S5, 3, 3, 10, 10)
        pit(DS, 3, 4, 6, 6)
        pit(CK, 3, 5, 2, -1)
        pit(GM, 3, 3, 4, -1)
        B.ticks(70)
        res["siteDig"] = list(could_not)
        del could_not[:]
        # ---- swim getter patched
        hs = B.call("jawa/harmony_patches", typeName="Verse.Pawn", methodName="get_Swimming") or {}
        row("PWF_swim_getter_patched", *v_patched(hs, "postfixes", "RM_Patch_Pawn_SwimPose.Postfix"))
        # ---- 2 m vs 1 m
        sw = spawn(P(18, 6))
        c2, c1 = (S2[0] + 1, S2[1] + 1), (S1[0] + 1, S1[1] + 1)
        a2, _ = order(sw, c2)
        s2 = swims(sw, c2) if a2 else None
        a1, _ = order(sw, c1)
        s1 = swims(sw, c1) if a1 else None
        st, det = v_swim_2m(s2, s1)
        row("PWF_swim_2m", st, dict(det, arrived2m=a2, arrived1m=a1))
        # ---- 5 m brim-full
        c5 = (S5[0] + 1, S5[1] + 1)
        a5, p5 = order(sw, c5, wait=600)
        B.ticks(30)
        st, det = v_float(swims(sw, c5) if a5 else None, sink(sw) if a5 else None)
        row("PWF_swim_5m_surface", st, dict(det, arrived=a5, proof=sc(PROMO, "ProofPawnSink", sw) if a5 else None))
        # ---- drafted + undrafted swimmer, every square
        ds = spawn(P(6, 16))
        cells = []
        for draft in (True, False):
            for j in range(4):
                for i in range(3):
                    c = (DS[0] + i, DS[1] + j)
                    arr, _ = order(ds, c, draft=draft, wait=300)
                    if arr:
                        B.ticks(20)
                    cells.append({"cell": c, "mode": "drafted" if draft else "undrafted", "arrived": arr,
                                  "swims": swims(ds, c) if arr else None, "sink": sink(ds) if arr else None})
        row("PWF_drafted_swimmer_all_cells", *v_all_cells(cells))
        # ---- wet pit enterable
        wp = spawn((W[0] + 1, W[1] + 5))
        a_in, _ = order(wp, (W[0] + 1, W[1] + 1), wait=600)
        a_out, _ = order(wp, (W[0] + 1, W[1] + 5), wait=600)
        st, det = v_enter(a_in, a_out)
        row("PWF_wet_pit_enterable", st, dict(det, report=str(B.call("jawa/flowworks_pit_report", x=W[0] + 1, z=W[1] + 1))[:300]))
        # ---- ladder + ramp in the wet pits, dry control
        def chk(defn, c):
            kw = {"def": defn, "rect": "%d,%d,1,1" % c, "rot": "0", "godMode": False}
            if defn == "RM_PitRamp":
                kw["stuff"] = "WoodLog"
            r = B.call("jawa/build_check", **kw) or {}
            return accepted(r), str(r)[:240]
        wl, wl_raw = chk("RM_Ladder", (W[0] + 1, W[1] + 3))
        wr, wr_raw = chk("RM_PitRamp", (R[0] + 1, R[1] + 2))
        dl, dl_raw = chk("RM_Ladder", (C[0] + 1, C[1] + 3))
        dr, dr_raw = chk("RM_PitRamp", (CR[0] + 1, CR[1] + 2))
        st, det = v_build({"RM_Ladder": wl, "RM_PitRamp": wr}, {"RM_Ladder": dl, "RM_PitRamp": dr})
        row("PWF_wet_pit_ladder_ramp", st, dict(det, rampSpan=rd, raw=[wl_raw, wr_raw, dl_raw, dr_raw]))
        # ---- click: patch + live pick
        hc = B.call("jawa/harmony_patches", typeName="RimWorld.FloatMenuOptionProvider_DraftedMove", methodName="GetSingleOption") or {}
        ck = spawn((CK[0] + 1, CK[1] + 6))
        ac, _ = order(ck, (CK[0] + 1, CK[1] + 4), wait=500)
        zc = CK[1] + 1
        sinks = {}
        for z in range(zc, zc + MAX_ROWS + 1):
            sinks[z] = fnum(sc(SINKP, "RestingSinkAt", "%s|%d,%d" % (ck, CK[0] + 1, z)))
        st, det = v_click_wired(hc, sinks, zc)
        row("PWF_click_patch_wired", st, dict(det, pawnInPit=ac))
        picked = det.get("picked", zc)
        B.call("jawa/select_things", ids=ck, action="select")
        rc = B.call("rimworld/right_click_cell", targetPawnName="", targetPawnId="", x=CK[0] + 1, z=zc, button="right",
                    holdDurationMs=0) or {}
        B.call("rimworld/step_game_ticks", ticks=300, pauseFirst=True, timeoutMs=60000)
        pg = ((B.call("jawa/pawn_get", pawn=ck, limit=1) or {}).get("pawns") or [{}])[0].get("position") or {}
        end_z = pg.get("z")
        moved = end_z is not None and end_z != CK[1] + 4
        st, det = v_click_e2e(zc, picked, end_z if moved else None, moved)
        row("PWF_click_end_to_end", st, dict(det, click=str(rc)[:200], class_="HARNESS" if st == "UNMEASURED" else "MOD"))
        # ---- shallow shaders
        gd = B.call("jawa/get_defs", defs="TerrainDef/RM_WaterThin;TerrainDef/RM_WaterVeryShallow;TerrainDef/WaterShallow",
                    fields="waterDepthShader", limit=5) or {}
        vals = {}
        for d in gd.get("defs") or gd.get("results") or []:
            vals[str(d.get("defName"))] = find_key(d, "waterDepthShader")
        st, det = v_shader({k: vals.get(k) for k in ("RM_WaterThin", "RM_WaterVeryShallow")}, vals.get("WaterShallow"))
        row("PWF_shallow_depth_shader", st, dict(det, raw=str(gd)[:300] if not vals else None))
        # ---- sluice closed blocks (box of walls, door in the south wall) + vanilla Door control
        def box(o, door):
            ops = []
            for i in range(5):
                for j in range(5):
                    if i in (0, 4) or j in (0, 4):
                        ops.append("%s:%d,%d" % ("Wall", o[0] + i, o[1] + j))
            ops = [op for op in ops if op != "Wall:%d,%d" % (o[0] + 2, o[1])]
            B.call("jawa/build_batch", ops=";".join(ops), stuff="Steel", faction="player", wipeExisting=True)
            r = B.call("jawa/build_batch", ops="%s:%d,%d" % (door, o[0] + 2, o[1]), stuff="Steel", faction="player",
                       wipeExisting=True) or {}
            return str(r)[:160]
        bs = box(SL, "RM_Sluice")
        bd = box((SL[0] + 7, SL[1]), "Door")
        p_s = spawn((SL[0] + 2, SL[1] + 2))
        p_d = spawn((SL[0] + 9, SL[1] + 2))
        sa, _ = order(p_s, (SL[0] + 2, SL[1] - 2), wait=500)
        da, _ = order(p_d, (SL[0] + 9, SL[1] - 2), wait=500)
        st, det = v_sluice(sa, da)
        row("PWF_sluice_closed_blocks", st, dict(det, built=[bs, bd]))
        # ---- god mode rescue ladder (last: every test colonist drafted, then a downed one in the sheer pit)
        for pid in (sw, ds, wp, ck, p_s, p_d):
            if pid:
                pp = ((B.call("jawa/pawn_get", pawn=pid, limit=1) or {}).get("pawns") or [{}])[0].get("position") or {}
                if pp.get("x") is not None:
                    B.call("jawa/order_pawn", pawnId=pid, x=pp["x"], z=pp["z"], waitTicks=1, draft=True)
        B.call("rimworld/set_god_mode", enabled=True)
        vic = spawn((GM[0] + 1, GM[1] + 1))
        inc = B.call("jawa/pawn_force_incapacitate", pawn=vic, action="downed", allowBleedingWounds=False) or {} if vic else {}
        found, trail = [], []
        for k in range(3):
            B.call("rimworld/step_game_ticks", ticks=250, pauseFirst=True, timeoutMs=60000)
            found = things_in((GM[0], GM[1], 3, 3))
            trail.append([d for d in found if d in LADDERS or d.startswith("Blueprint") or d.startswith("Frame")])
            if any(d in LADDERS for d in found):
                break
        st, det = v_godmode([d for d in found])
        row("PWF_godmode_ladder_free", st, dict(det, trail=trail, incap=str(inc)[:160]))
    finally:
        B.call("rimworld/set_god_mode", enabled=False)
        B.call("jawa/debug_settings", action="set", field="enableStoryteller", value=True)
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        res["summary"] = {s: sum(1 for r in rows if r["status"] == s) for s in ("PASS", "FAIL", "UNMEASURED")}
        save()
        print("result ->", out, res["summary"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
