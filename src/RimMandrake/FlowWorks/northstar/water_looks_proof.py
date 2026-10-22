"""WATER LOOKS live proof: WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED A1-A3 (L1), the two approved water looks (owner by card
2026-10-22, "Pick for me: shadow band + navy"): the deep-water navy tint and the wet-wall shadow band (RM_WaterLooks.cs).
Runbook 2026-10-22 rows P2 (this script) and 1.9 (its run). Written OFFLINE 2026-10-22: every row is OWED to its first live run.

  python.exe src/RimMandrake/FlowWorks/northstar/water_looks_proof.py [out.json] [--origin X,Z] [--fresh-map] [--only a,b]
             [--skip-offline]
  python3    src/RimMandrake/FlowWorks/northstar/water_looks_proof.py --offline-gate     # WSL: the offline tier (seconds)
  python3    src/RimMandrake/FlowWorks/northstar/water_looks_proof.py --mock [--mock-faults a,b] [--only a,b]
             offline against FakeBridge (a small world model, NOT the mod); every row is written SKIP with the verdict it
             would have reached kept under detail.mock (proves the script, never the game)

Run from the repo root with python.exe on the minimal list or the walk tier; the bridge must be held, and the deployed FlowWorks
must carry RimMandrake.FlowWorks.RM_WaterLookProofs (DLL 195c2fe9b or later): without it every row is UNMEASURED/HARNESS.
Exit 0 = every row PASS; 1 = a FAIL; 2 = a row could not be measured.

The instrument (RM_WaterLookProofs.ProofWaterLook, one square of the current map):
  "x,z"        WATERLOOK ... terrain still dug hollow waterM dlPerMetre tint tn tw key watchKey tintOn bandOn facesOn
               tintVisible bandVisible lookDirty -- tint/tn/tw/key are RM_WaterLookDraw's own reads (what the layers draw);
               tintVisible/bandVisible are the section's own layers' Visible (what a setting hides); watchKey is the key
               RM_WaterLookWatcher last noted (the one its mesh was dirtied for).
  "set:tint=0|1;band=0|1"   the two RM_WaterLookSettings (read back); restored at the end of the run, whatever happened.
  "take:x;z;w;h;dl"         dL off every dug square through the engine's TryTakeDl (the pump's leg; it sets no terrain).
Staging: RM_NorthstarProofs.ProofStageBasin "x;z;w;h;levels;fill;RM_Fluid_Water" (the engine's own Deepen + TrySetDriverFill).

Plots (3x3 pits from --origin, default 40,40; z 0..2; 3 dry squares between pits; site rect origin-(2,2) .. +46 x 9):
  T5   x0    12 notches, brim-full (6 m)     T10  x6    22 notches, brim-full (11 m)     CTRL x12   6 notches, brim-full (3 m)
  B1   x18   10 notches, fill 8 (gap 1 m)    B2   x24   10 notches, fill 6 (gap 2 m)     BRIM x30   10 notches, brim-full
  DD   x36   22 notches, brim-full (11 m), drawn down for A3
  The tint is read on a pit's centre square, the band on its north-west corner square (north and west neighbours are dry
  ground, so both band sides have a wall: RM_WaterLookDraw.Side reads dry ground as depth 0).

Rows (item WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED):
  A1_FIVE_METRES_NAVY        A1. T5 centre tint == 1 AND the CTRL (3 m) centre tint == 0 (the can-fail control: the
                             instrument tells 3 m from 6 m). LIES: a pit that never filled (waterM below the staged depth)
                             tints nothing for a SITE reason -> UNMEASURED/SITE, never FAIL.
  A1_TEN_METRES_DARKER       A1. T10 centre tint == 2 and T5's == 1 (darker than the 5 m step, not merely tinted).
  A1_TERRAIN_STILL_WATERDEEP A1. T5 and T10 centres read terrain WaterDeep and still=True: the tint is a picture, never a
                             terrain (the card: "every such square stays WaterDeep").
  A1_OFF_HIDES_TINT          A1. With the setting ON, T10's tint layer Visible=True (the control: visibility can read True;
                             False here = drawTerrain off or a blind read -> UNMEASURED/HARNESS); set tint=0 -> Visible=False
                             while the tint strength is unchanged (only the picture hides); restored.
  A2_BAND_WIDENS_WITH_GAP    A2. B1 and B2 corners both show tn>0 and tw>0, and B2's are wider than B1's (gap 2 m > 1 m).
  A2_BRIM_FULL_NO_BAND       A2. BRIM corner tn == tw == 0, scored only when B1 shows a band (the instrument can read one).
  A2_OFF_HIDES_BAND          A2. ON: B2's band layer Visible=True (control; the band also hides with wall faces off:
                             facesOn=False -> UNMEASURED/SITE); band=0 -> Visible=False, tn unchanged; restored.
  A3_DRAWDOWN_NO_TERRAIN_WRITE  A3. DD drawn down through TryTakeDl: 11 m -> 7.5 m -> 4 m (across 10 m, then 5 m). EXPECT
                             terrain identical at every step (WaterDeep: no terrain write happened), the water fell by the
                             take, and the tint STATE follows: 2 -> 1 -> 0.
  A3_TINT_FRESH_AFTER_DRAWDOWN  A3, "record whether the tint goes stale" (either answer is data). Baseline: 260 ticks after
                             staging the watcher's key equals the square's key (the sanity probe: the watch read can see; else
                             UNMEASURED/HARNESS). After each draw-down and 260 ticks (RM_WaterLookWatcher.IntervalTicks 250):
                             watchKey == key = the watcher noticed and dirtied the mesh (fresh: PASS); watchKey != key =
                             STALE: FAIL/MOD, which files a bug (runbook 1.9). lookDirty is recorded (a dirtied section the
                             paused game has not redrawn yet is pending, not stale).

ANTI-GUESSING NOTES
- TintStrength is computed whatever the setting; the setting hides through the layer's Visible. An OFF row that read the
  strength alone would pass with the setting broken, so OFF reads Visible.
- TintStrength is per square; the drawn corners blend over one square (Corner), so a pit edge is not a clean read: centres only.
- ProofStageBasin answers "dug" against the levels asked; a maxDepth below it (a refused Deepen) is SITE.
"""
import argparse
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
import validation_core as V  # noqa: E402

WLP = "RimMandrake.FlowWorks.RM_WaterLookProofs"
NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
WATER_FLUID = "RM_Fluid_Water"
ITEM = "WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED"
ROW_IDS = ["A1_FIVE_METRES_NAVY", "A1_TEN_METRES_DARKER", "A1_TERRAIN_STILL_WATERDEEP", "A1_OFF_HIDES_TINT",
           "A2_BAND_WIDENS_WITH_GAP", "A2_BRIM_FULL_NO_BAND", "A2_OFF_HIDES_BAND",
           "A3_DRAWDOWN_NO_TERRAIN_WRITE", "A3_TINT_FRESH_AFTER_DRAWDOWN"]
# plot -> (x offset, notches, fill notches)
PITS = {"T5": (0, 12, 12), "T10": (6, 22, 22), "CTRL": (12, 6, 6), "B1": (18, 10, 8), "B2": (24, 10, 6), "BRIM": (30, 10, 10),
        "DD": (36, 22, 22)}
METRES_PER_NOTCH = 0.5                 # RM_Volume.CentimetresPerNotch 50
DRAWDOWN_TO = [7.5, 4.0]               # metres of water left after each A3 take (across 10 m, then 5 m)
WATCH_WAIT = 260                       # > RM_WaterLookWatcher.IntervalTicks (250)
STAGE_SLACK_M = 0.25                   # a staged pit reads at least its staged water less this


def parse(txt):
    kv = {}
    for tok in str(txt).split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def fnum(kv, k):
    try:
        f = float((kv or {}).get(k))
    except (TypeError, ValueError):
        return None
    return None if f != f else f


def staged_m(plot):
    return PITS[plot][2] * METRES_PER_NOTCH


def filled(kv, plot):
    """The pit holds the water it was staged with (the read can see it)."""
    w = fnum(kv, "waterM")
    return w is not None and w >= staged_m(plot) - STAGE_SLACK_M


# ---------------------------------------------------------------- pure verdicts (selftest_water_looks_proof.py proves them)
def five_verdict(t5, ctrl):
    if not t5 or not ctrl or fnum(t5, "tint") is None or fnum(ctrl, "tint") is None:
        return "UNMEASURED", "HARNESS"
    if not filled(t5, "T5") or not filled(ctrl, "CTRL"):
        return "UNMEASURED", "SITE"
    return ("PASS" if fnum(t5, "tint") == 1 and fnum(ctrl, "tint") == 0 else "FAIL"), "MOD"


def ten_verdict(t10, t5):
    if not t10 or not t5 or fnum(t10, "tint") is None or fnum(t5, "tint") is None:
        return "UNMEASURED", "HARNESS"
    if not filled(t10, "T10") or not filled(t5, "T5"):
        return "UNMEASURED", "SITE"
    return ("PASS" if fnum(t10, "tint") == 2 and fnum(t5, "tint") == 1 else "FAIL"), "MOD"


def terrain_verdict(reads):
    """reads: {plot: kv} of the deep pits."""
    if not reads or any(not kv or "terrain" not in kv for kv in reads.values()):
        return "UNMEASURED", "HARNESS"
    if not all(filled(kv, p) for p, kv in reads.items()):
        return "UNMEASURED", "SITE"
    ok = all(kv.get("terrain") == "WaterDeep" and kv.get("still") == "True" for kv in reads.values())
    return ("PASS" if ok else "FAIL"), "MOD"


def off_verdict(on, off, vis, strength, needs=None):
    """on/off: reads with the setting on / off; vis: 'tintVisible'|'bandVisible'; strength: the field that must not move.
    needs: (field, value) that must hold for the layer to be visible at all (the band hides with wall faces off too)."""
    if not on or not off or on.get(vis) in (None, "unread") or off.get(vis) in (None, "unread"):
        return "UNMEASURED", "HARNESS"
    if needs and on.get(needs[0]) != needs[1]:
        return "UNMEASURED", "SITE"
    if on.get(vis) != "True":
        return "UNMEASURED", "HARNESS"          # the control: visibility never read True, so a False proves nothing
    ok = off.get(vis) == "False" and fnum(on, strength) == fnum(off, strength) and (fnum(on, strength) or 0) > 0
    return ("PASS" if ok else "FAIL"), "MOD"


def widen_verdict(b1, b2):
    vals = [fnum(r, k) for r in (b1, b2) for k in ("tn", "tw")]
    if not b1 or not b2 or None in vals:
        return "UNMEASURED", "HARNESS"
    if fnum(b1, "hollow") is not None and fnum(b1, "hollow") < PITS["B1"][1]:
        return "UNMEASURED", "SITE"
    if not filled(b1, "B1") or not filled(b2, "B2"):
        return "UNMEASURED", "SITE"
    n1, w1, n2, w2 = vals
    return ("PASS" if n1 > 0 and w1 > 0 and n2 > n1 and w2 > w1 else "FAIL"), "MOD"


def brim_verdict(brim, b1):
    if not brim or fnum(brim, "tn") is None or fnum(brim, "tw") is None or not b1 or fnum(b1, "tn") is None:
        return "UNMEASURED", "HARNESS"
    if not filled(brim, "BRIM"):
        return "UNMEASURED", "SITE"
    if not (fnum(b1, "tn") > 0):
        return "UNMEASURED", "HARNESS"          # the instrument never read a band: a 0 here proves nothing
    return ("PASS" if fnum(brim, "tn") == 0 and fnum(brim, "tw") == 0 else "FAIL"), "MOD"


def drawdown_verdict(steps):
    """steps: [kv before, kv after take 1, kv after take 2]."""
    if len(steps) != 3 or any(not s or "terrain" not in s or fnum(s, "waterM") is None for s in steps):
        return "UNMEASURED", "HARNESS"
    if not filled(steps[0], "DD"):
        return "UNMEASURED", "SITE"
    w = [fnum(s, "waterM") for s in steps]
    if not all(abs(w[i + 1] - DRAWDOWN_TO[i]) <= STAGE_SLACK_M for i in range(2)):
        return "UNMEASURED", "SITE"             # the take did not land where asked: the crossing was never made
    same = len({s.get("terrain") for s in steps}) == 1 and steps[0].get("terrain") == "WaterDeep"
    tints = [fnum(s, "tint") for s in steps]
    return ("PASS" if same and tints == [2, 1, 0] else "FAIL"), "MOD"


def fresh_verdict(baseline, after):
    """baseline: the kv read WATCH_WAIT ticks after staging; after: the kvs read WATCH_WAIT ticks after each take.
    -> (status, cls, stale) with stale True/False/None (None = not asked)."""
    reads = [baseline] + list(after or [])
    if not baseline or len(reads) != 3 or any(not r or r.get("watchKey") in (None, "unread") or r.get("key") is None for r in reads):
        return "UNMEASURED", "HARNESS", None
    if baseline["watchKey"] != baseline["key"]:
        return "UNMEASURED", "HARNESS", None     # the watch read does not match the staged picture: blind or unready
    if len({r["key"] for r in reads}) != 3:
        return "UNMEASURED", "SITE", None        # the key never changed: no crossing to go stale over
    stale = any(r["watchKey"] != r["key"] for r in after)
    return ("FAIL" if stale else "PASS"), "MOD", stale


# ---------------------------------------------------------------- offline gate
def offline_gate():
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(HERE, "selftest_water_looks_proof.py")], capture_output=True, text=True,
                       timeout=600)
    steps = {"selftest_water_looks_proof": {"exit": r.returncode, "tail": r.stdout.strip().splitlines()[-1:]}}
    return {"red": [k for k, v in steps.items() if v["exit"]], "steps": steps}


def offline_gate_from_windows():
    import subprocess
    import proof_hose as PH          # noqa: E402  (the wsl path helper)
    r = subprocess.run(["wsl.exe", "python3", PH._posix(os.path.abspath(__file__)), "--offline-gate"], capture_output=True,
                       text=True, timeout=900)
    for ln in reversed((r.stdout or "").splitlines()):
        if ln.startswith("GATE_JSON "):
            return json.loads(ln[len("GATE_JSON "):])
    return {"red": ["gate:no GATE_JSON (exit %s)" % r.returncode], "steps": {}}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,40")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--only", default="", help="comma list of rows: " + ",".join(ROW_IDS))
    ap.add_argument("--skip-offline", action="store_true", help="live: do not run the offline gate first")
    ap.add_argument("--offline-gate", action="store_true")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-faults", default="", help="comma list: " + ",".join(FakeBridge.FAULTS))
    a = ap.parse_args(argv)
    if a.offline_gate:
        g = offline_gate()
        print("GATE_JSON " + json.dumps(g))
        return 1 if g["red"] else 0
    only = [x.strip().upper() for x in a.only.split(",") if x.strip()] or list(ROW_IDS)
    if set(only) - set(ROW_IDS):
        ap.error("unknown --only row(s) %s" % ",".join(sorted(set(only) - set(ROW_IDS))))
    faults = [f for f in a.mock_faults.split(",") if f]
    if set(faults) - set(FakeBridge.FAULTS):
        ap.error("unknown --mock-faults %s" % ",".join(sorted(set(faults) - set(FakeBridge.FAULTS))))
    if a.mock:
        raw = FakeBridge(faults)
    else:
        import proof_hose as PH          # noqa: E402  (bridge-side imports only on a live run)
        raw = PH.PB()
    B = V.guard(raw)
    out = a.out or (os.path.join(tempfile.gettempdir(), "water_looks_mock_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
                    if a.mock else os.path.join(HERE, "water_looks_result_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    rows = []
    res = {"script": "water_looks_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    if a.mock:
        res["mode"] = "mock"
    else:
        import driver_stamp
        driver_stamp.stamp(res, raw.call)

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        try:
            os.replace(out + ".tmp", out)
        except OSError:
            with open(out, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1, default=str)

    def row(rid, st, det, cls="MOD"):
        if rid not in only:
            return
        st, cls, det = V.PRE.judge(st, cls, det)
        if st == "FAIL" and cls != "MOD":
            st = "UNMEASURED"
        if a.mock:
            det = dict(det, mock=st)
            st = "SKIP"
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "criterion": rid.split("_")[0], "detail": det})
        print("%-30s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def all_rows(why, cls):
        for rid in only:
            row(rid, "UNMEASURED", {"why": why}, cls=cls)
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        return 2

    def look(arg):
        r = B.call("jawa/static_call", type=WLP, method="ProofWaterLook", args=arg, _answer=True) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        ok = r.get("success") is True and not txt.startswith("REFUSED")
        return (parse(txt) if ok else {}), txt

    def ticks(n):
        r = B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}
        return V.require(r.get("success") is not False, "the clock moved %d ticks" % n, r, cls="HARNESS")

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)        # noqa: E731
    centre = lambda p: P(PITS[p][0] + 1, 1)      # noqa: E731
    corner = lambda p: P(PITS[p][0], 2)          # noqa: E731  (north-west square of the 3x3)
    xz = lambda c: "%d,%d" % c                   # noqa: E731

    # ------------------------------------------------------------------ preflight
    if not a.mock and not a.skip_offline:
        g = offline_gate_from_windows()
        res["offlineGate"] = g
        if g["red"]:
            return all_rows("offline gate red: %s" % g["red"], "HARNESS")
    if a.fresh_map and not a.mock:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok = True if a.mock else V._wait_playing(B, leave_s=0)[0]
    if not ok:
        return all_rows("no game in Playing", "HARNESS")
    k0, t0 = look(xz(P(0, 0)))
    if not k0.get("cell"):
        return all_rows("%s.ProofWaterLook is not in the loaded FlowWorks (deploy DLL 195c2fe9b+): %s" % (WLP, t0[:160]), "HARNESS")
    res["settingsBefore"] = {"tintOn": k0.get("tintOn"), "bandOn": k0.get("bandOn"), "facesOn": k0.get("facesOn")}
    if not a.mock:
        rect = (max(ox - 2, 1), max(oz - 2, 1), 46, 9)
        res["site_calm"] = V.site_calm(B)
        B.call("jawa/kill_hostiles")
        site_rows = []
        with V.scope("site"):
            V.prepare_site(B, rect, site_rows, "water_looks_site")
        bad = [r for r in site_rows if r.get("status") not in (None, "PASS")]
        if bad:
            return all_rows("site not prepared: %s" % json.dumps(bad[:3], default=str)[:300], "SITE")
    look("set:tint=1;band=1")
    try:
        _run(a, B, row, look, ticks, P, centre, corner, xz, res)
    finally:
        look("set:tint=%s;band=%s" % ("0" if k0.get("tintOn") == "False" else "1", "0" if k0.get("bandOn") == "False" else "1"))
        res["settingsAfter"] = look(xz(P(0, 0)))[1][:400]
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    if a.mock:
        bad = [r["id"] for r in rows if r["detail"].get("mock") != "PASS"]
        print("MOCK: water looks: %d rows, mock verdicts not PASS: %s -> %s" % (len(rows), bad or "none", out))
        return 1 if any(r["detail"].get("mock") == "FAIL" for r in rows) else (2 if bad else 0)
    fails = [r for r in rows if r["status"] == "FAIL"]
    print("water looks: %d rows, %d FAIL, %d not PASS -> %s" % (len(rows), len(fails), sum(r["status"] != "PASS" for r in rows), out))
    return 1 if fails else (2 if any(r["status"] != "PASS" for r in rows) else 0)


def _run(a, B, row, look, ticks, P, centre, corner, xz, res):
    staged = {}
    with V.scope("stage"):
        for plot, (dx, levels, fill) in PITS.items():
            x, z = P(dx, 0)
            r = B.call("jawa/static_call", type=NPROOF, method="ProofStageBasin",
                       args="%d;%d;3;3;%d;%d;%s" % (x, z, levels, fill, WATER_FLUID), _answer=True) or {}
            kv = parse(r.get("result") or "")
            staged[plot] = kv
            V.require(kv.get("dug") == "9" and kv.get("maxDepth") == str(levels), "pit %s dug 9 squares to %d" % (plot, levels),
                      r, cls="SITE")
        ticks(2)
        stage_faults = list(V.PRE.pending())
    res["staged"] = staged
    rd = {p: look(xz(centre(p)))[0] for p in ("T5", "T10", "CTRL", "DD")}
    bd = {p: look(xz(corner(p)))[0] for p in ("B1", "B2", "BRIM")}
    res["reads"] = {"centre": rd, "corner": bd}
    sd = {"stageFaults": stage_faults} if stage_faults else {}

    def site(st, cls):          # a refused stage is SITE whatever the verdict read
        return ("UNMEASURED", "SITE") if stage_faults and st in ("PASS", "FAIL") else (st, cls)

    st, cls = site(*five_verdict(rd["T5"], rd["CTRL"]))
    row("A1_FIVE_METRES_NAVY", st, dict(sd, t5=rd["T5"], control3m=rd["CTRL"]), cls=cls)
    st, cls = site(*ten_verdict(rd["T10"], rd["T5"]))
    row("A1_TEN_METRES_DARKER", st, dict(sd, t10=rd["T10"], t5=rd["T5"]), cls=cls)
    st, cls = site(*terrain_verdict({"T5": rd["T5"], "T10": rd["T10"]}))
    row("A1_TERRAIN_STILL_WATERDEEP", st, dict(sd, t5=rd["T5"].get("terrain"), t10=rd["T10"].get("terrain")), cls=cls)
    # OFF hides: the tint on T10, the band on B2 (both read ON first: the visibility control)
    on_t = look(xz(centre("T10")))[0]
    look("set:tint=0")
    off_t = look(xz(centre("T10")))[0]
    look("set:tint=1")
    st, cls = site(*off_verdict(on_t, off_t, "tintVisible", "tint"))
    row("A1_OFF_HIDES_TINT", st, dict(sd, on=on_t, off=off_t), cls=cls)
    st, cls = site(*widen_verdict(bd["B1"], bd["B2"]))
    row("A2_BAND_WIDENS_WITH_GAP", st, dict(sd, gap1m=bd["B1"], gap2m=bd["B2"]), cls=cls)
    st, cls = site(*brim_verdict(bd["BRIM"], bd["B1"]))
    row("A2_BRIM_FULL_NO_BAND", st, dict(sd, brim=bd["BRIM"], control=bd["B1"].get("tn")), cls=cls)
    on_b = look(xz(corner("B2")))[0]
    look("set:band=0")
    off_b = look(xz(corner("B2")))[0]
    look("set:band=1")
    st, cls = site(*off_verdict(on_b, off_b, "bandVisible", "tn", needs=("facesOn", "True")))
    row("A2_OFF_HIDES_BAND", st, dict(sd, on=on_b, off=off_b), cls=cls)
    # A3: draw DD down across 10 m and 5 m through the engine's own take; terrain and the watcher read at every step
    dd = centre("DD")
    x0, z0 = P(PITS["DD"][0], 0)
    ticks(WATCH_WAIT)
    base = look(xz(dd))[0]
    steps, after, takes = [base], [], []
    for target in DRAWDOWN_TO:
        cur = look(xz(dd))[0]
        w, per = fnum(cur, "waterM"), fnum(cur, "dlPerMetre")
        if w is None or not per or w <= target:
            takes.append({"why": "no water reading to take from", "read": cur})
            break
        tk, tt = look("take:%d;%d;3;3;%d" % (x0, z0, int(round((w - target) * per))))
        takes.append(tt[:200])
        steps.append(look(xz(dd))[0])            # the state, at once (no tick): terrain and tint strength
        ticks(WATCH_WAIT)
        after.append(look(xz(dd))[0])            # the watcher has run at least once since the take
    st, cls = site(*drawdown_verdict(steps))
    row("A3_DRAWDOWN_NO_TERRAIN_WRITE", st, dict(sd, steps=steps, takes=takes, targetsM=DRAWDOWN_TO), cls=cls)
    st, cls, stale = fresh_verdict(base, after)
    st, cls = site(st, cls)
    row("A3_TINT_FRESH_AFTER_DRAWDOWN", st, dict(sd, baseline=base, after=after, stale=stale,
                                                 note="stale=True files a bug; stale=False is the answer A3 asked for"), cls=cls)


# ====================================================================== offline stand-in
class FakeBridge(object):
    """A small world model answering in ProofWaterLook / ProofStageBasin's line formats. It knows nothing about the game: a
    mock verdict proves the script's control flow and its MOD/SITE/HARNESS split only. Faults, one wrong thing each:
      old_deploy     RM_WaterLookProofs missing                     -> every row UNMEASURED/HARNESS
      no_dig         one pit refuses to deepen (T10)                -> every row UNMEASURED/SITE
      tint_shallow   MOD: 3 m water tints too (control)             -> A1_FIVE_METRES_NAVY FAIL, A3_DRAWDOWN FAIL (4 m tints)
      tint_flat      MOD: 10 m reads the 5 m step                   -> A1_TEN_METRES_DARKER FAIL, A3_DRAWDOWN FAIL (and
                                                                     A3_TINT_FRESH SITE: no key change to go stale over)
      terrain_write  MOD: deep water is written as a new terrain    -> A1_TERRAIN_STILL_WATERDEEP FAIL, A3_DRAWDOWN FAIL
      off_shows      MOD: the tint setting off leaves it visible    -> A1_OFF_HIDES_TINT FAIL
      no_draw        drawTerrain off: no layer ever reads visible   -> both OFF rows UNMEASURED/HARNESS
      faces_off      wall faces off (the band hides with them)      -> A2_OFF_HIDES_BAND UNMEASURED/SITE
      band_flat      MOD: the band is one width whatever the gap    -> A2_BAND_WIDENS_WITH_GAP FAIL
      band_brim      MOD: a brim-full pit shows a band              -> A2_BRIM_FULL_NO_BAND FAIL
      band_off_shows MOD: the band setting off leaves it visible    -> A2_OFF_HIDES_BAND FAIL
      take_terrain   MOD: the draw-down writes terrain              -> A3_DRAWDOWN_NO_TERRAIN_WRITE FAIL
      stale          MOD: the watcher never re-keys after a take    -> A3_TINT_FRESH_AFTER_DRAWDOWN FAIL (stale=True)
      blind_watch    the watcher's key cannot be read               -> A3_TINT_FRESH_AFTER_DRAWDOWN UNMEASURED/HARNESS"""
    FAULTS = ("old_deploy", "no_dig", "tint_shallow", "tint_flat", "terrain_write", "off_shows", "no_draw", "faces_off",
              "band_flat", "band_brim", "band_off_shows", "take_terrain", "stale", "blind_watch")
    DL_PER_M = 2000                        # any positive number: the script only uses the read-back value

    def __init__(self, faults=()):
        self.f = set(faults)
        self.cells = {}                    # (x, z) -> [hollow notches, water metres, terrain]
        self.tint_on, self.band_on = True, True
        self.watch = {}                    # (x, z) -> last noted key

    def _tint(self, w):
        if "tint_shallow" in self.f and w >= 2.5:
            return 1 if w < 10 or "tint_flat" in self.f else 2
        if w >= 10:
            return 1 if "tint_flat" in self.f else 2
        return 1 if w >= 5 else 0

    def _band(self, c):
        cell = self.cells.get(c)
        if not cell or cell[1] <= 0:
            return 0.0, 0.0
        out = []
        for n in ((c[0], c[1] + 1), (c[0] - 1, c[1])):
            nh = self.cells[n][0] if n in self.cells else 0
            gap = max(0.0, (cell[0] - nh) * METRES_PER_NOTCH - cell[1])
            if "band_brim" in self.f and gap == 0 and nh == 0:
                gap = 0.5
            if "band_flat" in self.f and gap > 0:
                gap = 1.0
            out.append(0.0 if gap <= 0 else max(1 / 16.0, min(0.5, 0.34 * gap / 2)))
        return out[0], out[1]

    def _key(self, c):
        cell = self.cells.get(c)
        tn, tw = self._band(c)
        t = self._tint(cell[1]) if cell else 0
        return t | int(round(tn * 32)) << 2 | int(round(tw * 32)) << 8

    def _tick(self, n):
        if n >= 250 and "stale" not in self.f:
            self.watch = {c: self._key(c) for c in self.cells}
        elif n >= 250 and not self.watch:
            self.watch = {c: self._key(c) for c in self.cells}     # the baseline is seen; later changes are not

    def look(self, arg):
        if arg.startswith("set:"):
            for part in arg[4:].split(";"):
                k, v = part.split("=")
                if k == "tint":
                    self.tint_on = v == "1"
                else:
                    self.band_on = v == "1"
            return "WATERLOOKSET tintOn=%s bandOn=%s" % (self.tint_on, self.band_on)
        if arg.startswith("take:"):
            x, z, w, h, dl = (int(v) for v in arg[5:].split(";"))
            n = 0
            for i in range(w):
                for j in range(h):
                    cell = self.cells.get((x + i, z + j))
                    if cell:
                        n += 1
                        cell[1] = max(0.0, cell[1] - dl / float(self.DL_PER_M))
                        if "take_terrain" in self.f:
                            cell[2] = "RM_WaterChestDeepStill"
            return "WATERTAKE cells=%d took=%d" % (n, n * dl)
        x, z = (int(v) for v in arg.split(","))
        c = (x, z)
        cell = self.cells.get(c)
        hollow, w, terr = cell if cell else (0, 0.0, "Soil")
        tn, tw = self._band(c)
        tint = self._tint(w) if cell else 0
        draw = "no_draw" not in self.f
        faces = "faces_off" not in self.f
        wk = "unread" if "blind_watch" in self.f or not self.watch else str(self.watch.get(c, 0))
        return ("WATERLOOK cell=%d,%d terrain=%s still=%s dug=%s hollow=%d waterM=%.4f dlPerMetre=%d tint=%d tn=%.4f tw=%.4f key=%d "
                "watchKey=%s tintOn=%s bandOn=%s facesOn=%s tintVisible=%s bandVisible=%s lookDirty=False") % (
            x, z, terr, bool(cell and w > 0), bool(cell), hollow, w, self.DL_PER_M, tint, tn, tw, self._key(c), wk, self.tint_on,
            self.band_on, faces, draw and (self.tint_on or "off_shows" in self.f),
            draw and faces and (self.band_on or "band_off_shows" in self.f))

    def stage(self, arg):
        x, z, w, h, levels, fill, _fl = arg.split(";")
        x, z, w, h, levels, fill = (int(v) for v in (x, z, w, h, levels, fill))
        depth = levels - 2 if "no_dig" in self.f and levels == 22 and x % 10 == 6 else levels
        for i in range(w):
            for j in range(h):
                wm = min(fill, depth) * METRES_PER_NOTCH
                terr = "RM_DeepNavyWater" if "terrain_write" in self.f and wm >= 5 else ("WaterDeep" if wm >= 2 else "WaterShallow")
                self.cells[(x + i, z + j)] = [depth, wm, terr]
        return "BASIN cells=%d dug=%d filled=%d refused=0 maxDepth=%d" % (w * h, w * h if depth >= levels else 0, w * h, depth)

    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            if kw.get("type") == WLP:
                if "old_deploy" in self.f:
                    return {"success": False, "error": "Type not found: " + WLP}
                return {"success": True, "result": self.look(kw.get("args") or "")}
            if kw.get("method") == "ProofStageBasin":
                return {"success": True, "result": self.stage(kw.get("args") or "")}
            return {"success": False, "error": "unknown"}
        if tool == "rimworld/step_game_ticks":
            self._tick(int(kw.get("ticks") or 0))
            return {"success": True}
        return {"success": True}


if __name__ == "__main__":
    sys.exit(main())
