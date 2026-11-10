"""test_titan_footprint_live.py -- A2's whole live proof for TITANIC_BODYSIZE_TEST_RACE_1: the five rows of
titan_test_races_live.py, then the sixth row the item's spec names and that runner does not drive, the Large Pawns footprint.

  python.exe src/RimMandrake/HugeThings/northstar/test_titan_footprint_live.py [--site X,Z] [--out FILE]

LIST: Huge Things + Huge Things Test Races + Large Pawns (neku.largepawns, workshop 3777700657) + Harmony, all five DLC.
Exit 0 only when every one of ROWS (the runner's five plus large_pawns_footprint_bridge) is PASS; 2 (no verdict)
when the bridge cannot be reached; 1 else.

R6 large_pawns_footprint_bridge, existing bridge tools only (no new C#):
  * jawa/mod_settings_field LargePawns.Settings size2Min/size3Min/size4Min -- LargePawnsBridge.TryReconcile must have pushed our
    RM_TitanicTierDef ladder 4/8/20 into it. Type not found = Large Pawns not on the list = UNMEASURED SITE (never a PASS).
  * our largePawnsFootprintEnabled + giantAnimalsEnabled are startup-read: either off = UNMEASURED SITE.
  * jawa/spawn_pawn an adult (jawa/set_pawn_age) RM_TestTitanT2, RM_TestTitanT3 and RM_TestTitanT2Control, wild, then
    jawa/static_call Verse.GenAdj.OccupiedRect(<ThingID>) -- the read Large Pawns Prefix-patches and our wake iterates. The edge
    must be RM_TitanicKernel.FootprintSize: T2 3, T3 4; the forced-out control 1 (PushOverrideRows' size-1 row; Large Pawns' own
    default ladder 2.5/4.5/10 would give it 3, so the control is what tells a pushed override from an untouched mod).
The three spawned test titans are left alive on the map (wild, manhunterOnDamageChance 0): throwaway quicktest maps only.
"""
import argparse
from live_results import aggregate
import json
import math
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import titan_test_races_live as L  # noqa: E402

FOOT = "large_pawns_footprint_bridge"
ROWS = tuple(L.ROWS) + (FOOT,)
LP_SETTINGS = "LargePawns.Settings"
LADDER = {"size2Min": 4.0, "size3Min": 8.0, "size4Min": 20.0}      # RM_TitanicTierDef t1/t2/t3 floors
EDGE = {L.T2: 3, L.T3: 4, L.CTL: 1}                                  # RM_TitanicKernel.FootprintSize / OverrideFootprint(force out)
OURS = ("largePawnsFootprintEnabled", "giantAnimalsEnabled")


def rect_edge(txt):
    """static_call's render of a CellRect (an IEnumerable<IntVec3>: up to 12 '(x, y, z)' cells, then ' (N total)') -> the square's
    edge, or None when the text is no square of cells."""
    txt = txt or ""
    m = re.search(r"\((\d+) total\)\s*$", txt)
    cells = [(int(x), int(z)) for x, _, z in re.findall(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", txt)]
    n = int(m.group(1)) if m else len(cells)
    e = int(round(math.sqrt(n))) if n > 0 else 0
    if e <= 0 or e * e != n or not cells or len(set(cells)) != len(cells) or len(cells) != min(n, 12):
        return None
    x0, z0 = min(c[0] for c in cells), min(c[1] for c in cells)
    if any(not (0 <= x - x0 < e and 0 <= z - z0 < e) for x, z in cells):
        return None                                             # a listed cell outside one e x e square
    if n <= 12 and set(cells) != set((x0 + i, z0 + j) for i in range(e) for j in range(e)):
        return None                                             # every cell is listed, so they must BE the square
    return e


def judge_footprint(ladder, edges):
    """(status, detail): ladder {field: float} read off LargePawns.Settings, edges {kind: int|None} from OccupiedRect."""
    badl = [k for k, v in LADDER.items()
            if ladder.get(k) is None or not math.isfinite(float(ladder[k])) or abs(float(ladder[k]) - v) > 1e-4]
    bade = [k for k, v in EDGE.items() if edges.get(k) != v]
    d = "ladder %s (want 4/8/20); edges %s (want T2 3, T3 4, control 1)" % (
        "/".join(str(ladder.get(k)) for k in ("size2Min", "size3Min", "size4Min")),
        ", ".join("%s=%s" % (k, edges.get(k)) for k in EDGE))
    if badl or bade:
        return "FAIL", "wrong: %s; %s" % (badl + bade, d)
    return "PASS", d


def classification_verdict(rows):
    return 0 if aggregate(rows, ROWS)["all_rows_classified"] else 1


def verdict(rows):
    return 0 if aggregate(rows, ROWS)["gameplay_pass"] else 1


def footprint(R, cells):
    ours = dict((f, R.call("jawa/mod_settings_field", typeName=L.SETTINGS, action="get", field=f).get("value")) for f in OURS)
    if any(str(v).lower() != "true" for v in ours.values()):
        return R.row(FOOT, "UNMEASURED", "SITE", "startup-read settings not on: %r" % ours)
    ladder = {}
    for f in LADDER:
        r = R.call("jawa/mod_settings_field", typeName=LP_SETTINGS, action="get", field=f)
        if r.get("success") is not True:
            return R.row(FOOT, "UNMEASURED", "SITE", "LargePawns.Settings.%s unreadable (is neku.largepawns on the list?): %s"
                         % (f, str(r.get("error") or r.get("message") or r)[:200]))
        try:
            ladder[f] = float(r.get("value"))
        except (TypeError, ValueError):
            return R.row(FOOT, "UNMEASURED", "HARNESS", "LargePawns.Settings.%s=%r" % (f, r.get("value")))
    edges, notes = {}, []
    for kind, (x, z) in zip(EDGE, cells):
        s = R.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction="none")
        pid = ((s.get("pawns") or [{}])[0] or {}).get("id") if s.get("success") is True else None
        if not pid:
            return R.row(FOOT, "UNMEASURED", "HARNESS", "spawn %s at %d,%d failed: %s" % (kind, x, z, str(s)[:200]))
        # spawned pawns come in at any age (23 seen live) and DebugSetAge only ages FORWARD: the raw setter puts every one at
        # 3 years, past the test races' AnimalAdult floor 0.666 (gen 7, 2026-11-03: the forward-only call left the row UNMEASURED)
        a = R.call("jawa/set_pawn_age", pawn=pid, biologicalYears=3.0, allowBackwards=True)
        stage = (a.get("after") or {}).get("lifeStage") or (a.get("before") or {}).get("lifeStage")
        if stage != "AnimalAdult":
            return R.row(FOOT, "UNMEASURED", "HARNESS", "%s %s not adult (lifeStage %r): %s" % (kind, pid, stage, str(a)[:200]))
        R.ticks(1)
        # the bare thingIDNumber, never the ThingID: static_call's resolver splits trailing digits off a ThingID, so a defName
        # ending in a digit (RM_TestTitanT2 + 53196) parses as #253196 and finds nothing (STATIC_CALL_THINGID_FIX_DIGIT_EATS_ITSELF)
        num = pid[len(kind):] if pid.startswith(kind) else ""
        if not num.isdigit():
            return R.row(FOOT, "UNMEASURED", "HARNESS", "%s id %r is not <defName><thingIDNumber>" % (kind, pid))
        o = R.call("jawa/static_call", type="Verse.GenAdj", method="OccupiedRect", args=num)
        txt = str(o.get("result") if o.get("success") is True else o.get("error") or o.get("message") or o)
        print("    OccupiedRect(%s %s) -> %s" % (kind, pid, txt[:300]), flush=True)
        if o.get("success") is not True:
            return R.row(FOOT, "UNMEASURED", "HARNESS", "OccupiedRect(%s) failed: %s" % (pid, txt[:200]))
        edges[kind] = rect_edge(txt)
        notes.append("%s=%s" % (pid, txt[:80]))
    st, d = judge_footprint(ladder, edges)
    R.row(FOOT, st, "MOD", d + "; " + "; ".join(notes))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="", help="first probe cell X,Z for the five-row runner (default: map centre)")
    ap.add_argument("--out", default=os.path.join(REPO, "Transient", "modcheck",
                                                  "titan_test_races_a2_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    a = ap.parse_args()
    a.out = os.path.abspath(a.out)
    five = a.out[:-5] + "_five.json" if a.out.endswith(".json") else a.out + "_five.json"
    cmd = [sys.executable, os.path.join(HERE, "titan_test_races_live.py"), "--out", five] + (["--site", a.site] if a.site else [])
    if os.path.exists(five):
        os.remove(five)                                         # never judge a previous run's rows
    try:
        rc = subprocess.call(cmd, timeout=520)
    except subprocess.TimeoutExpired:
        rc = None
        print("five-row runner timed out and was killed: its settings restore may not have run", flush=True)
    if rc == L.NO_VERDICT:                                      # the runner never reached the game: its five rows are not FAILs
        print("five-row runner exit %d: no verdict for A2" % rc, flush=True)
        return L.NO_VERDICT
    prior = []
    if rc in (0, 1):
        try:
            with open(five, encoding="utf-8") as fh:
                prior = json.load(fh).get("rows") or []
        except (OSError, ValueError):
            prior = []
    rb = L.open_bridge()
    if rb is None:
        return L.NO_VERDICT
    with rb:
        R = L.Run(rb, a.out)
        R.required_rows = ROWS
        R.rows = list(prior)
        mi = R.call("jawa/map_info")
        size = mi.get("size") or mi.get("mapSize") or {}
        try:
            cx, cz = int(size.get("x")) // 2, int(size.get("z")) // 2
        except (TypeError, ValueError, AttributeError):
            cx = cz = 125
        # away from the runner's probe cells (centre +-20) and its two corpses
        footprint(R, [(cx - 30, cz + 30), (cx, cz + 30), (cx + 30, cz + 30)])
        R.save()
    v = verdict(R.rows)
    print("rows -> %s (five-row runner exit %r)" % (a.out, rc))
    print("ALL ROWS CLASSIFIED: %s" % (classification_verdict(R.rows) == 0))
    print("GAMEPLAY VERDICT: %s (%d rows, %d wanted)" % ("PASS" if v == 0 else "FAIL", len(R.rows), len(ROWS)))
    return v


if __name__ == "__main__":
    sys.exit(main())
