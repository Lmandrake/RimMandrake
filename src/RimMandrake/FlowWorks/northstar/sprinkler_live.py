"""FlowWorks sprinkler LIVE rows (validation.py SPRINKLER_LIVE) and the two thirst rows that need a sprinkler net (T21, T22):
the first live driver for them, written on the 2026-10-17 review walk. Rows {id, status, class, detail}; "could not ask" is
UNMEASURED.

  python.exe src/RimMandrake/FlowWorks/northstar/sprinkler_live.py [out.json] [--only draws,dries,...] [--origin X,Z]
  python3    src/RimMandrake/FlowWorks/northstar/sprinkler_live.py --dry-run [--only ...]   plan only, no bridge
  python3    src/RimMandrake/FlowWorks/northstar/sprinkler_live.py --mock [--mock-faults a,b] [--only ...]
             every row's control flow against sprinkler_fake.SprinklerFakeBridge (pump / pipe / tank / pulse / power-switch
             timing, NOT the mod). Result says mode "mock", written to the temp dir. Faults: sprinkler_fake.py docstring;
             selftest: selftest_sprinkler_live.py.

Bridge held, a Playing disposable map (the calm test site). Settings flipped are restored in a finally.

THE NET (LAYOUT, MEASURED LIVE 2026-10-17): a 2x2 RM_LiquidTank at (ox,oz), RM_UniversalPipe on ox+2..ox+5 (one unbroken run),
the RM_LiquidPump built OVER the pipe at ox+3, the head on the pipe at ox+5, power conduit + battery south of the pump.
A pump standing IN the run with no pipe under it splits the run into two components: the head then sees the pump
(pressure) but not the tank ("Dry: nothing in the tanks on this network"); a pump beside the run is not on it at all
("No pressure"). Both false layouts were tried first (Transient/review_walk_2026-10-17/probes/sprk_layout*.py).

THE READS: the head's inspect line (jawa/inspect_string); the tank's units (the hose probe's tank:x,z, decilitres);
RM_MapComponent_Sprinklers.Pulses / SprayedUnits (static counters, read with jawa/mod_settings_field) to see a pulse land;
ExplosiveGrowthAPI.IsSoaked(current, x,z) for "the cell reads wet" (the wet registry the sprinkler writes into).

Rows: sprinkler.draws_and_wets, .dries_when_starved, .no_pressure, .thick_clogs, .walls_stop_spray, .acid_hurts_fuel_puddles,
sprinkler_switch_flips.flip_sprinklersEnabled, T22_no_brine_spray, T21_drinking_reserve. Not driven here: .liquid_key (the
key lives behind an out parameter no bridge call reads), the two VFE rows (no VFE Farming on the walk list).
"""
import argparse
import json
import os
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.dirname(HERE)
for _p in (HERE, FW, os.path.join(os.path.dirname(FW), "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

S_SP = "RimMandrake.FlowWorks.Sprinklers.RM_SprinklerSettings"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
S_TH = "RimMandrake.FlowWorks.Thirst.RM_ThirstSettings"
MC = "RimMandrake.FlowWorks.Sprinklers.RM_MapComponent_Sprinklers"
PULSE = 2500
COLD_WAIT = 250       # net(): ticks let go before the first fill (see net()); the selftest sets 0 to prove the mock goes red
# --only key -> the row ids it emits (--dry-run prints it; selftest_sprinkler_live.py checks every emitted id is declared)
PLAN = (
    ("draws", ("sprinkler.draws_and_wets",)),
    ("pressure", ("sprinkler.no_pressure",)),
    ("switch", ("sprinkler_switch_flips.flip_sprinklersEnabled",)),
    ("dries", ("sprinkler.dries_when_starved",)),
    ("thick", ("sprinkler.thick_clogs",)),
    ("walls", ("sprinkler.walls_stop_spray",)),
    ("brine", ("T22_no_brine_spray",)),
    ("effects", ("sprinkler.acid_hurts_fuel_puddles",)),
    ("reserve", ("T21_drinking_reserve",)),
)
UNITS_PER_CELL = 5          # 12.5 L/h over 25 cells = 0.5 L = 5 dL a cell a pulse (sprinklerLitresPerCellHour 0.5)


def main(argv=None, bridge=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--only", default="")
    ap.add_argument("--dry-run", action="store_true", help="print the plan and exit; no bridge")
    ap.add_argument("--mock", action="store_true", help="run against sprinkler_fake.SprinklerFakeBridge (offline; mode 'mock')")
    ap.add_argument("--mock-faults", default="", help="comma list of sprinkler_fake faults to inject")
    ap.add_argument("--origin", default="120,140", help="first net's tank corner; nets are 14 cells apart in z")
    a = ap.parse_args(argv)
    only = [x.strip().lower() for x in a.only.split(",") if x.strip()]
    if a.dry_run:
        keys = tuple(k for k, _ in PLAN)
        bad = [o for o in only if o not in keys]
        print("sprinkler_live plan (dry run, no bridge): first net at %s, nets 14 cells apart in z" % a.origin)
        for k in keys:
            print("  %-9s %s" % (k, "RUN" if not only or k in only else "skip"))
        if bad:
            print("  UNKNOWN --only keys: %s" % bad)
            return 2
        return 0
    if bridge is not None:
        B = bridge
    elif a.mock:
        import sprinkler_fake
        B = sprinkler_fake.SprinklerFakeBridge(faults=[f for f in a.mock_faults.split(",") if f])
    else:
        import validation_hose as VH
        B = VH.H()
    mock = bridge is not None or a.mock
    OX, OZ = map(int, a.origin.split(","))
    out = a.out or os.path.join(tempfile.gettempdir() if mock else HERE,
                                "sprinkler_live_%sresult_%s.json" % ("mock_" if mock else "", time.strftime("%Y%m%dT%H%M%S")))
    rows = []
    res = {"script": "sprinkler_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    import driver_stamp
    driver_stamp.stamp(res, B.call)      # validation.py reads a result only at the current mod hash AND deployed DLL
    if mock:
        res["mode"] = "mock"             # never 'live': validation.py must refuse a result no game produced
    # 2026-10-18 (SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING): ExplosiveGrowthAPI.IsSoaked is in the composed mandrake.rm.biomes
    # mod; the 11-mod flowworks tier does not load it, so soaked() reads None there: SITE, not HARNESS.
    _run = (res.get("env") or {}).get("running")
    EG_CLS = "SITE" if _run is not None and "mandrake.rm.biomes" not in _run else "HARNESS"

    def save():
        txt = json.dumps(res, indent=1, default=str)
        try:
            with open(out + ".tmp", "w", encoding="utf-8") as f:
                f.write(txt)
            os.replace(out + ".tmp", out)
        except OSError:
            with open(out, "w", encoding="utf-8") as f:
                f.write(txt)

    ctx = {"broken": [], "setfail": []}   # net layout not built / a bool setting that did not read back: rows below could not ask

    def row(rid, st, cls, det):
        if st == "FAIL" and (ctx["broken"] or ctx["setfail"]):    # "could not ask" is UNMEASURED, never a MOD FAIL
            det = dict(det, couldNotAsk=ctx["broken"] + ctx["setfail"])
            st, cls = "UNMEASURED", "SITE" if ctx["broken"] else "HARNESS"
        ctx["setfail"] = []
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-44s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:420]), flush=True)
        save()

    def want(key):
        return not only or key in only

    def tg():
        g = B.call("rimworld/get_game_info") or {}
        return g.get("ticksGame") or (g.get("state") or {}).get("tick")

    def ticks(n):
        t0 = tg()
        left = n
        while left > 0:
            k = min(1250, left)
            B.ticks(k)
            left -= k
        t1 = tg()
        if None not in (t0, t1) and t1 - t0 < n:
            B.ticks(n - (t1 - t0))

    def sfield(typ, field, value=None):
        if value is not None:
            B.call("jawa/mod_settings_field", typeName=typ, action="set", field=field, value=str(value))
        got = (B.call("jawa/mod_settings_field", typeName=typ, action="get", field=field) or {}).get("value")
        if isinstance(value, bool) and str(got).lower() != str(value).lower():
            ctx["setfail"].append("%s set to %s but reads %r" % (field, value, got))
        return got

    def pulses():
        try:
            return int(sfield(MC, "Pulses")), int(sfield(MC, "SprayedUnits"))
        except (TypeError, ValueError):
            return None, None

    def build(ops):
        r = B.call("jawa/build_batch", ops=";".join(ops), faction="player", wipeExisting=False) or {}
        return r.get("survived"), r.get("failed")

    def thing_at(defn, x, z):
        th = (B.call("jawa/list_things", defName=defn, rect="%d,%d,1,1" % (x, z), limit=3) or {}).get("things") or []
        return th[0]["id"] if th else None

    def inspect(tid):
        for t in (B.call("jawa/inspect_string", thingIds=tid) or {}).get("things") or []:
            return " | ".join(t.get("inspect") or [])
        return None

    def fill(x, z, liquid, units):
        r = B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
                   args="%d,%d;Store;%s;%d" % (x, z, liquid, units)) or {}
        if r.get("success") is False:
            ctx["broken"].append("ProofTank Store %s refused" % liquid)
        return str(r.get("result"))

    def units(x, z):
        r = B.hp("tank:%d,%d" % (x, z))
        return r.get("units") if r.get("success") else None

    def soaked(x, z):
        r = B.call("jawa/static_call", type="RimMandrake.ExplosiveGrowth.ExplosiveGrowthAPI", method="IsSoaked",
                   args="current|%d,%d" % (x, z)) or {}
        v = str(r.get("result"))
        return True if v == "True" else False if v == "False" else None

    def net(i):
        """Build net i (layout in the docstring); returns its cells dict."""
        ox, oz = OX, OZ + 14 * i
        B.call("jawa/destroy_batch", rects="%d,%d,14,12" % (ox - 3, oz - 5), categories="Building,Plant,Item,Filth")
        B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,14,12" % (ox - 3, oz - 5))
        B.call("jawa/set_roof_batch", ops="None:%d,%d,14,12" % (ox - 3, oz - 5))
        s1 = build(["RM_LiquidTank:%d,%d" % (ox, oz)] + ["RM_UniversalPipe:%d,%d" % (x, oz) for x in range(ox + 2, ox + 6)])
        s2 = build(["RM_LiquidPump:%d,%d" % (ox + 3, oz), "RM_SprinklerHead:%d,%d" % (ox + 5, oz),
                    "PowerConduit:%d,%d" % (ox + 3, oz - 1), "PowerConduit:%d,%d" % (ox + 3, oz - 2), "Battery:%d,%d,0" % (ox + 3, oz - 4)])
        B.call("jawa/gss_stage", ops="kind=gss_charge|x=%d|z=%d" % (ox + 3, oz - 4))
        n = {"tank": (ox, oz), "pump": (ox + 3, oz), "head": (ox + 5, oz), "covered": (ox + 6, oz + 1), "far": (ox + 10, oz + 4),
             "build": [s1, s2]}
        n["headId"] = thing_at("RM_SprinklerHead", ox + 5, oz)
        n["pumpId"] = thing_at("RM_LiquidPump", ox + 3, oz)
        ctx["broken"] = [w_ for w_, v in (("head", n["headId"]), ("pump", n["pumpId"]), ("tank", thing_at("RM_LiquidTank", ox, oz))) if not v]
        ctx["broken"] = ["net %d: %s not built" % (i, w_) for w_ in ctx["broken"]]
        # HARNESS (T22, 2026-10-18 rerun: brine-only read "No pressure"): the COLD pulse. A new head pulses at its first
        # rare tick (nextPulseTick -1; CompRM_SprinklerHead.RareTick, phase (tick + thingIDNumber) % 250), but vanilla
        # PowerNet.PowerNetTick switches a new consumer on only when TicksGame % (200 / wanting) == 0, so the pump can be
        # unpowered for up to 200 ticks after the build. A pulse landing in that gap reads NoPressure and holds for 2,500
        # ticks; whenever the phase put it after +130 the T22 read (fill, 2,500 + 130) WAS that cold pulse (the fresh tank
        # then paid two pulses, 180 dL, against one, 90 dL, in the PASS runs). Let the cold pulse go before the fill.
        ticks(COLD_WAIT)
        return n

    def until_pulse():
        """One full pulse interval: every head on the map pulses exactly once in any PULSE consecutive ticks.
        HARNESS (walk 2026-10-17): the first version waited on RM_MapComponent_Sprinklers.Pulses, a MAP-GLOBAL counter, so
        with several nets on the map it returned on ANOTHER head's pulse and read this head 60-130 ticks early (T21, T22 and
        the acid arm read stale)."""
        ticks(PULSE)
        return PULSE

    saved = {}
    try:
        for k in ("sprinklersEnabled", "sprinklerNonWaterEffects"):
            saved[(S_SP, k)] = sfield(S_SP, k)
        saved[(S_FW, "liquidPumpEnabled")] = sfield(S_FW, "liquidPumpEnabled")
        saved[(S_TH, "drinkingReserveLitres")] = sfield(S_TH, "drinkingReserveLitres")

        # ---------------------------------------------------------------- draws / dries / pressure / switch: net 0
        if any(want(k) for k in ("draws", "dries", "pressure", "switch")):
            n = net(0)
            res["net0"] = n
            hx, hz = n["head"]
            print(fill(n["tank"][0], n["tank"][1], "RM_Liquid_FreshWater", 100000))
            if want("draws"):
                until_pulse()          # let the first (cold) pulse land, then measure one clean pulse
                u0, (p0, s0) = units(*n["tank"]), pulses()
                spent = until_pulse()
                u1, (p1, s1) = units(*n["tank"]), pulses()
                line = inspect(n["headId"])
                m = re.search(r"(\d+) cells", line or "")
                cells = int(m.group(1)) if m else None
                wet_c, wet_f = soaked(*n["covered"]), soaked(*n["far"])
                det = {"units": [u0, u1], "drop": (u0 - u1) if None not in (u0, u1) else None, "cells": cells, "inspect": line,
                       "pulseAfterTicks": spent, "sprayedUnits": [s0, s1], "soakedCovered": wet_c, "soakedFar": wet_f}
                if spent is None or None in (u0, u1, cells, wet_c):
                    row("sprinkler.draws_and_wets", "UNMEASURED", EG_CLS if wet_c is None else "HARNESS", det)
                else:
                    bad = []
                    if (u0 - u1) != cells * UNITS_PER_CELL:
                        bad.append("tank lost %s, want cells x %d = %s" % (u0 - u1, UNITS_PER_CELL, cells * UNITS_PER_CELL))
                    if "Spraying" not in (line or ""):
                        bad.append("head does not read Spraying")
                    if not wet_c:
                        bad.append("a covered cell does not read soaked")
                    if wet_f:
                        bad.append("a cell outside the radius reads soaked")
                    row("sprinkler.draws_and_wets", "FAIL" if bad else "PASS", "MOD", dict(det, bad=bad))
            if want("pressure"):
                sfield(S_FW, "liquidPumpEnabled", False)
                try:
                    u0 = units(*n["tank"])
                    until_pulse()
                    line = inspect(n["headId"])
                    u1 = units(*n["tank"])
                finally:
                    sfield(S_FW, "liquidPumpEnabled", saved[(S_FW, "liquidPumpEnabled")])
                until_pulse()
                ticks(130)
                line2 = inspect(n["headId"])
                bad = []
                if None in (u0, u1):
                    bad.append("tank units unreadable (%s, %s)" % (u0, u1))
                if not (line or "").startswith("No pressure"):
                    bad.append("pump off but the head reads %r" % line)
                if u0 != u1:
                    bad.append("tank moved %s -> %s with no pressure" % (u0, u1))
                if "Spraying" not in (line2 or ""):
                    bad.append("pump back on but the next pulse reads %r" % line2)
                row("sprinkler.no_pressure", "FAIL" if bad else "PASS", "MOD",
                    {"pumpOff": line, "units": [u0, u1], "pumpBackOn": line2, "bad": bad,
                     "how": "the pump stops through liquidPumpEnabled (Building_LiquidPump.Running), not a despawn: a despawn "
                            "by cell also destroys the pipe under it"})
            if want("switch"):
                sfield(S_SP, "sprinklersEnabled", False)
                try:
                    u0 = units(*n["tank"])
                    until_pulse()
                    line = inspect(n["headId"])
                    u1 = units(*n["tank"])
                finally:
                    sfield(S_SP, "sprinklersEnabled", saved[(S_SP, "sprinklersEnabled")])
                ok = (line or "").startswith("Sprinklers are off in Mod Settings") and u0 == u1 and u0 is not None
                row("sprinkler_switch_flips.flip_sprinklersEnabled", "PASS" if ok else "FAIL", "MOD",
                    {"inspect": line, "units": [u0, u1]})
            if want("dries"):
                # HARNESS (found by the 2026-10-18 mock): the row dried cells that were never wet. Alone, or after the
                # pressure/switch rows (their last spray is >2,750 ticks old), the covered cell already read dry and the
                # row PASSed without the head ever being starved of anything. Wet the cell first.
                wet_before = soaked(*n["covered"])
                if wet_before is False:
                    until_pulse()
                    wet_before = soaked(*n["covered"])
                if wet_before is False:
                    row("sprinkler.dries_when_starved", "UNMEASURED", "HARNESS",
                        {"why": "the covered cell never read wet before the tank was emptied", "inspect": inspect(n["headId"])})
                    wet_before = "reported"
                print(fill(n["tank"][0], n["tank"][1], "RM_Liquid_FreshWater", 0))
                trace = []
                for _ in range(22):
                    ticks(125)
                    trace.append([inspect(n["headId"]), soaked(*n["covered"])])
                    if (trace[-1][0] or "").startswith("Dry") and trace[-1][1] is False:
                        break
                line, wet = trace[-1]
                ok = (line or "").startswith("Dry") and wet is False
                if wet_before != "reported":
                    row("sprinkler.dries_when_starved", "PASS" if ok else ("UNMEASURED" if wet is None else "FAIL"),
                        "MOD" if wet is not None else EG_CLS, {"last": [line, wet], "ticks": 125 * len(trace),
                                                                "wetBefore": wet_before})

        # ---------------------------------------------------------------- thick / brine / walls / effects: net 1..
        if want("thick"):
            n = net(1)
            res["net1"] = n
            print(fill(n["tank"][0], n["tank"][1], "RM_Liquid_Tar", 50000))
            u0 = units(*n["tank"])
            until_pulse()
            ticks(130)
            line, u1 = inspect(n["headId"]), units(*n["tank"])
            ok = (line or "").startswith("Clogged") and u0 == u1 and u0 is not None
            row("sprinkler.thick_clogs", "PASS" if ok else "FAIL", "MOD", {"inspect": line, "units": [u0, u1]})

        if want("walls"):
            n = net(2)
            res["net2"] = n
            hx, hz = n["head"]
            build(["Wall:%d,%d" % (hx + 1, hz + 2), "Wall:%d,%d" % (hx, hz + 2), "Wall:%d,%d" % (hx - 1, hz + 2)])
            behind = (hx, hz + 3)
            open_c = (hx, hz - 2)
            print(fill(n["tank"][0], n["tank"][1], "RM_Liquid_FreshWater", 100000))
            until_pulse()
            ticks(130)
            wb, wo = soaked(*behind), soaked(*open_c)
            line = inspect(n["headId"])
            if None in (wb, wo) or "Spraying" not in (line or ""):
                row("sprinkler.walls_stop_spray", "UNMEASURED", EG_CLS if None in (wb, wo) else "HARNESS",
                    {"behindWall": wb, "openSide": wo, "inspect": line})
            else:
                row("sprinkler.walls_stop_spray", "PASS" if (wo and not wb) else "FAIL", "MOD",
                    {"behindWall": [behind, wb], "openSide": [open_c, wo], "inspect": line})

        if want("brine"):
            n = net(3)
            res["net3"] = n
            tx, tz = n["tank"]
            print(fill(tx, tz, "RM_Liquid_Brine", 50000))
            until_pulse()
            ticks(130)
            line1 = inspect(n["headId"])
            u_b0 = units(tx, tz)
            # a second tank holding a little fresh water, cardinal to pipe ox+4 (north side)
            build(["RM_LiquidTank:%d,%d" % (tx + 4, tz + 1)])   # covers tx+4..5, tz+1..2: cardinal to the pipe at (tx+4, tz)
            print(fill(tx + 4, tz + 1, "RM_Liquid_FreshWater", 20000))
            until_pulse()
            ticks(130)
            line2 = inspect(n["headId"])
            u_b1, u_f = units(tx, tz), units(tx + 4, tz + 1)
            bad = []
            if not re.match(r"(Dry|No liquid)", line1 or ""):
                bad.append("brine-only net reads %r" % line1)
            if "fresh" not in (line2 or "").lower() or "Spraying" not in (line2 or ""):
                bad.append("brine + fresh reads %r (want spraying fresh)" % line2)
            if u_b0 is None or u_b0 != u_b1:
                bad.append("brine tank moved %s -> %s" % (u_b0, u_b1))
            row("T22_no_brine_spray", "FAIL" if bad else "PASS", "MOD",
                {"brineOnly": line1, "withFresh": line2, "brineUnits": [u_b0, u_b1], "freshUnits": u_f, "bad": bad})

        if want("effects"):
            n = net(4)
            res["net4"] = n
            hx, hz = n["head"]
            tx, tz = n["tank"]
            sfield(S_SP, "sprinklerNonWaterEffects", True)
            print(fill(tx, tz, "RM_Liquid_AcidWater", 50000))
            r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=hx + 1, z=hz + 1, count=1, faction="PlayerColony") or {}
            pid = ((r.get("pawns") or [{}])[0]).get("id")
            if not pid:          # review 2026-10-17: a failed spawn read as "a pawn in the acid spray took no harm" (MOD)
                raise RuntimeError("effects: jawa/spawn_pawn gave no pawn id: %s" % str(r)[:200])
            B.call("jawa/set_draft", pawnId=pid, drafted=True)
            B.call("rimworld/select_pawn", pawnId="Thing_" + str(pid))
            ea = B.call("rimworld/execute_debug_action", path="Actions\\Wear apparel (selected)...\\*Remove all apparel") or {}
            if ea.get("success") is False:     # a clothed pawn takes less acid harm: a FAIL would be the harness's
                raise RuntimeError("effects: remove-all-apparel debug action refused: %s" % str(ea)[:200])
            B.call("rimworld/clear_selection")

            def harm(p):
                ps = (B.call("jawa/pawn_get", pawn=p) or {}).get("pawns") or []
                return round(sum(float(h.get("severity") or 0) for h in (ps[0].get("hediffs") if ps else []) or []
                                 if not str(h.get("def") or "").startswith("RM_")), 3)
            h0 = harm(pid)
            until_pulse()
            ticks(60)
            h1 = harm(pid)
            line_acid = inspect(n["headId"])
            sfield(S_SP, "sprinklerNonWaterEffects", False)
            try:
                until_pulse()
                ticks(60)
                h2 = harm(pid)
            finally:
                sfield(S_SP, "sprinklerNonWaterEffects", saved[(S_SP, "sprinklerNonWaterEffects")])
            # chemfuel: spill filth on covered cells
            print(fill(tx, tz, "RM_Liquid_Chemfuel", 50000))
            rect = "%d,%d,7,7" % (hx - 3, hz - 3)

            def filth():
                lt = (B.call("jawa/list_things", rect=rect, limit=200) or {}).get("things") or []
                return sum(1 for t in lt if str(t.get("def") or "").startswith(("Filth", "RM_Filth")) and t.get("def") != "Filth_Water")
            f0 = filth()
            until_pulse()
            ticks(60)
            f1 = filth()
            line_fuel = inspect(n["headId"])
            bad = []
            if "Spraying" not in (line_acid or ""):
                bad.append("acid head did not spray: %r" % line_acid)
            elif not h1 > h0:
                bad.append("a pawn in the acid spray took no harm (%s -> %s)" % (h0, h1))
            if h2 > h1:          # burns heal between reads (0.928 -> 0.64 live), so only a RISE is a fault
                bad.append("effects OFF but harm still rose (%s -> %s)" % (h1, h2))
            if "Spraying" not in (line_fuel or ""):
                bad.append("chemfuel head did not spray: %r" % line_fuel)
            elif not f1 > f0:
                bad.append("chemfuel spray left no filth (%s -> %s)" % (f0, f1))
            row("sprinkler.acid_hurts_fuel_puddles", "FAIL" if bad else "PASS", "MOD",
                {"acid": line_acid, "harm": [h0, h1, h2], "fuel": line_fuel, "filth": [f0, f1], "bad": bad,
                 "notRun": "the chemfuel arm with the setting off"})

        if want("reserve"):
            n = net(5)
            res["net5"] = n
            tx, tz = n["tank"]
            reserve = float(saved[(S_TH, "drinkingReserveLitres")] or 200)
            start = int(reserve * 10) + 200            # 20 L over the reserve: one 12.5 L pulse fits, the second does not
            print(fill(tx, tz, "RM_Liquid_FreshWater", start))
            trace = []
            for _ in range(3):
                until_pulse()
                ticks(130)
                trace.append([units(tx, tz), inspect(n["headId"])])
            low = min(u for u, _ in trace if u is not None) if trace else None
            last = trace[-1][1] if trace else None
            r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=tx - 2, z=tz + 3, count=1, faction="PlayerColony") or {}
            pid = ((r.get("pawns") or [{}])[0]).get("id")
            if not pid:          # review 2026-10-17: a failed spawn read as "did not drink at the reserved tank" (MOD)
                raise RuntimeError("reserve: jawa/spawn_pawn gave no pawn id: %s" % str(r)[:200])
            for nd in ("Food", "Rest", "Joy", "Mood"):
                B.call("jawa/pawn_need", pawn=pid, action="need", need=nd, level=1.0)
            pn = B.call("jawa/pawn_need", pawn=pid, action="need", need="RM_Thirst", level=0.2) or {}
            if pn.get("success") is False:     # a pawn that was never thirsty "did not drink at the reserved tank"
                raise RuntimeError("reserve: RM_Thirst need not set: %s" % str(pn)[:200])
            B.call("jawa/stop_job", pawnId=pid)
            seen = []
            for _ in range(15):
                ticks(60)
                cs = (B.call("rimworld/list_colonists", currentMapOnly=True) or {}).get("colonists") or []
                j = next((c.get("job") for c in cs if c.get("pawnId") == "Thing_" + str(pid)), None)
                if j and (not seen or seen[-1] != j):
                    seen.append(j)
                if j == "RM_DrinkFromTank":
                    break
            bad = []
            if low is None or low < reserve * 10:
                bad.append("the tank went below the reserve (%s < %s units)" % (low, reserve * 10))
            if not (last or "").startswith("Dry"):
                bad.append("at the reserve the head reads %r, want Dry" % last)
            if "RM_DrinkFromTank" not in seen:
                bad.append("a thirsty colonist did not drink at the reserved tank (jobs %s)" % seen)
            row("T21_drinking_reserve", "FAIL" if bad else "PASS", "MOD",
                {"reserveL": reserve, "startUnits": start, "trace": trace, "drinkJobs": seen, "bad": bad,
                 "notRun": "the salt tank on a still draining to 0"})
    finally:
        for (typ, k), v in saved.items():
            if v is not None:
                try:
                    sfield(typ, k, v)
                except Exception:  # noqa: BLE001
                    pass
        res["ended"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
    return 0 if rows and all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
