"""g8_depth.py -- batch A of the pass-8 gallery: the depth ladder, pit occupants and the graded walks, on RM_FW_Gallery8.

  python.exe ralph/live/g8_depth.py [--save RM_FW_Gallery8] [--no-load] [--parts empty,occupied,walk3,walk4]
                                    [--k 0.3,0.375 --hold 0,0.4 [--grid]] [--settle-ms 500] [--tag t]

parts (default all, in this order):
  empty     A1..A4 with nobody in them, root 7.2 and root 20 (Steve's window holds ~42 x 14 cells at 7.2).
  occupied  the same KIND colonist (male, same body/head/hair, drafted, facing south, locked) on the north row centre
            of each A1 hole and on the undug control west of the row; occupants on the south (west column), middle
            (centre column) and north (east column) rows of A2's 4 m and 8 m holes. Shots of A1 and A2 at 7.2 and 20 for
            each setting, the state of every occupant read, and the asserts:
              A1_sink_nondecreasing   sink never smaller in a deeper hole (control, 0.5 .. 8 m)
              A1_sink_4m_eq_8m        the 4 m and 8 m occupants sink the same
              A2_<row>_4m_eq_8m       the same row of the 4 m and 8 m holes sinks the same
  walk3     one colonist walks A3 (north-south graded trench) south -> north -> south, one cell per order; at each stop:
            cell, dug depth, drawn position and the state read, and one shot with the camera FIXED (root 7.2).
  walk4     the same along A4 (east-west) west -> east -> west.
            Asserts per step: A3/A4_step_<i>  sink strictly UP onto a deeper cell, strictly DOWN onto a shallower one.

Settings (--k sink per level, --hold sink hold above): the lists are zipped into settings (or crossed with --grid);
the occupied part runs once per setting, with every shot name tagged k<k>_h<hold>. No --k/--hold: one pass at the
build's own settings. Setters are the pass-8 RM_PitDepthDraw.SetSinkPerLevel / SetSinkHoldAbove when present; k falls
back to the pitSinkPerLevel field, hold is UNMEASURED without its setter. Settings are put back at the end.

State read: RM_PitDepthDraw.DepthDrawState(thingIDNumber) when the build has it, else UNMEASURED; the old build's
RM_PromotionProofs.ProofPawnSink(ThingID) is read beside it and carries the asserts (source "legacy") when the new read
is missing. Output: Transient/ralph_fw/g8/depth_<tag>_<HHMMSS>/ (log.txt, results.jsonl, shots/).
"""
import argparse
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g8_common as C  # noqa: E402
from g8_common import j  # noqa: E402

EPS = 1e-3


def shoot_A(B, R, L, tag, which=("A1", "A2")):
    if "A1" in which:
        C.shot(B, R, "%s_A1" % tag, L["A1_rects"]["all"], C.ROOT_PLAY)
        C.shot(B, R, "%s_A1" % tag, L["A1_rects"]["all"], C.ROOT_WIDE)
    if "A2" in which:
        C.shot(B, R, "%s_A2" % tag, L["A2_rect"], C.ROOT_PLAY)
        C.shot(B, R, "%s_A2" % tag, L["A2_rect"], C.ROOT_WIDE)
    if "A3" in which:
        C.shot(B, R, "%s_A3" % tag, L["A3"]["rect"], C.ROOT_PLAY)
        C.shot(B, R, "%s_A3" % tag, L["A3"]["rect"], C.ROOT_WIDE)
    if "A4" in which:
        C.shot(B, R, "%s_A4" % tag, L["A4"]["rect"], C.ROOT_PLAY)
        C.shot(B, R, "%s_A4" % tag, L["A4"]["rect"], C.ROOT_WIDE)


def check_fixture(B, R, L):
    """The gallery is what the layout says (a wrong origin or a stale save would shoot the wrong ground)."""
    bad = []
    for h in L["A1"]:
        d = C.depth_at(B, (h["x0"] + 1, h["z0"] + 1))
        if d != h["levels"]:
            bad.append(("A1", h["k"], d, h["levels"]))
    for h in L["A2"]:
        d = C.depth_at(B, (h["x0"] + 1, h["z0"] + 1))
        if d != h["levels"]:
            bad.append(("A2", h["levels"], d))
    for c, r in zip(L["A3"]["walk"], L["A3"]["rows"]):
        if C.depth_at(B, c) != r["levels"]:
            bad.append(("A3", c, C.depth_at(B, c), r["levels"]))
    for c, col in zip(L["A4"]["walk"], L["A4"]["cols"]):
        if C.depth_at(B, c) != col["levels"]:
            bad.append(("A4", c, C.depth_at(B, c), col["levels"]))
    R.result("fixture_A", bad, expected=[], ok=not bad, source="flowworks_excavation_rect")
    return not bad


def settings_list(a):
    ks = [float(v) for v in a.k.split(",")] if a.k else [None]
    hs = [float(v) for v in a.hold.split(",")] if a.hold else [None]
    if a.grid:
        return list(itertools.product(ks, hs))
    n = max(len(ks), len(hs))
    ks += [ks[-1]] * (n - len(ks))
    hs += [hs[-1]] * (n - len(hs))
    return list(zip(ks, hs))


def stag(k, h):
    return "k%s_h%s" % ("-" if k is None else ("%g" % k), "-" if h is None else ("%g" % h))


def occupy(B, R, L):
    """-> {'A1': [(label, levels, pid)], 'A2': [(label, levels, row, pid)]}"""
    occ = {"A1": [], "A2": []}
    pid = C.subject(B, R, L["A1_control"], "A1 control")
    occ["A1"].append(("control", 0, pid))
    for h in L["A1"]:
        pid = C.subject(B, R, h["subject"], "A1 %gm" % h["metres"])
        occ["A1"].append(("%gm" % h["metres"], h["levels"], pid))
    for h in L["A2"]:
        for row in ("south", "middle", "north"):
            pid = C.subject(B, R, h["subjects"][row], "A2 %gm %s" % (h["metres"], row))
            occ["A2"].append(("%gm_%s" % (h["metres"], row), h["levels"], row, pid))
    return occ


def read_occupants(B, R, occ, st):
    a1, a2 = [], []
    for label, lv, pid in occ["A1"]:
        if not pid:
            continue
        rd = C.read_pawn(B, R, pid, "A1 " + label)
        a1.append((lv, rd["sink"], rd["src"], label))
        R.result("A1_occupant_%s" % label, {"levels": lv, "pid": pid, "sink": rd["sink"], "state": rd["state"],
                                             "legacy": rd["legacy"]}, ok=None if rd["sink"] is not None else "UNMEASURED",
                 source=rd["src"], setting=st)
        if rd["stateStatus"] != "OK":
            R.result("A1_state_%s" % label, rd["stateStatus"], expected="DepthDrawState read", ok="UNMEASURED",
                     source="DepthDrawState", setting=st)
    for label, lv, row, pid in occ["A2"]:
        if not pid:
            continue
        rd = C.read_pawn(B, R, pid, "A2 " + label)
        a2.append((lv, row, rd["sink"], rd["src"], label))
        R.result("A2_occupant_%s" % label, {"levels": lv, "row": row, "pid": pid, "sink": rd["sink"],
                                             "state": rd["state"], "legacy": rd["legacy"]},
                 ok=None if rd["sink"] is not None else "UNMEASURED", source=rd["src"], setting=st)
    return a1, a2


def assert_A(R, a1, a2, st):
    seq = sorted(a1, key=lambda r: r[0])
    sinks = [r[1] for r in seq]
    src = ",".join(sorted({r[2] for r in seq if r[2]})) or None
    if any(s is None for s in sinks) or not sinks:
        R.result("A1_sink_nondecreasing", [(r[0], r[1]) for r in seq], expected="non-decreasing", ok="UNMEASURED",
                 source=src, setting=st)
    else:
        good = all(b >= a - EPS for a, b in zip(sinks, sinks[1:]))
        R.result("A1_sink_nondecreasing", [(r[0], r[1]) for r in seq], expected="non-decreasing by depth", ok=good,
                 source=src, setting=st)
    s8 = [r[1] for r in a1 if r[0] == 8]
    s16 = [r[1] for r in a1 if r[0] == 16]
    if s8 and s16 and s8[0] is not None and s16[0] is not None:
        R.result("A1_sink_4m_eq_8m", {"4m": s8[0], "8m": s16[0]}, expected="equal", ok=abs(s8[0] - s16[0]) < EPS,
                 source=src, setting=st)
    else:
        R.result("A1_sink_4m_eq_8m", {"4m": s8, "8m": s16}, expected="equal", ok="UNMEASURED", source=src, setting=st)
    for row in ("south", "middle", "north"):
        x = [r for r in a2 if r[1] == row]
        s4 = [r[2] for r in x if r[0] == 8]
        s8_ = [r[2] for r in x if r[0] == 16]
        if s4 and s8_ and s4[0] is not None and s8_[0] is not None:
            R.result("A2_%s_4m_eq_8m" % row, {"4m": s4[0], "8m": s8_[0]}, expected="equal", ok=abs(s4[0] - s8_[0]) < EPS,
                     source=x[0][3], setting=st)
        else:
            R.result("A2_%s_4m_eq_8m" % row, {"4m": s4, "8m": s8_}, expected="equal", ok="UNMEASURED", setting=st)


def occupied(B, R, L, a):
    occ = occupy(B, R, L)
    C.settle(B, a.settle_ms)
    k0, h0 = C.setting(B, "pitSinkPerLevel"), C.setting(B, "pitSinkHoldAbove")
    R.log("settings before", "pitSinkPerLevel", k0, "pitSinkHoldAbove", h0)
    for k, h in settings_list(a):
        st = stag(k, h)
        if k is not None or h is not None:
            how = C.set_sink(B, R, k, h)
            R.result("setting_%s" % st, how, source="setters/fields", setting=st)
            if h is not None and str(how.get("hold", "")).startswith("UNMEASURED"):
                R.result("hold_%s" % st, how.get("hold"), expected="SetSinkHoldAbove applied", ok="UNMEASURED",
                         source="RM_PitDepthDraw.SetSinkHoldAbove", setting=st)
        C.settle(B, a.settle_ms)
        a1, a2 = read_occupants(B, R, occ, st)
        assert_A(R, a1, a2, st)
        shoot_A(B, R, L, "occ_" + st)
    if any(k is not None or h is not None for k, h in settings_list(a)):
        C.set_sink(B, R, float(k0) if k0 is not None else None, float(h0) if h0 is not None else None)
        R.log("settings restored", C.setting(B, "pitSinkPerLevel"), C.setting(B, "pitSinkHoldAbove"))
    return occ


def walk(B, R, L, a, key):
    F = L[key]
    path = F["walk"]
    stops = list(path) + list(reversed(path[:-1]))
    legs = ["out"] * len(path) + ["back"] * (len(path) - 1)
    pid = C.subject(B, R, F["start"], "%s walker" % key, face=None)
    if not pid:
        return
    C.settle(B, a.settle_ms)
    C.shot(B, R, "%s_walk_start" % key, F["rect"], C.ROOT_PLAY, frame=True, wait=1.5)   # frames the FIXED camera
    rows = []
    for i, (cell, leg) in enumerate(zip(stops, legs)):
        arrived, at = C.walk_to(B, R, pid, cell)
        if not arrived:
            R.harness_error("%s stop %d: walker at %s, never reached %s" % (key, i, at, cell))
        C.settle(B, a.settle_ms)
        d = C.depth_at(B, at or cell)
        rd = C.read_pawn(B, R, pid, "%s stop %d" % (key, i))
        lg = rd["legacy"] or {}
        stt = rd["state"] or {}
        drawn = C.fnum(stt.get("drawnZ"))
        if drawn is None and C.fnum(lg.get("drawDz")) is not None and at:
            drawn = at[1] + 0.5 + C.fnum(lg.get("drawDz"))
        row = {"i": i, "leg": leg, "cell": at, "want": cell, "depth": d, "sink": rd["sink"], "drawnZ": drawn,
               "src": rd["src"], "state": stt or rd["stateStatus"], "moving": lg.get("moving")}
        rows.append(row)
        R.result("%s_stop_%02d" % (key, i), row, ok=None if rd["sink"] is not None else "UNMEASURED", source=rd["src"])
        C.shot(B, R, "%s_%02d_%s_d%d" % (key, i, leg, d), F["rect"], C.ROOT_PLAY, frame=False)
    for p, q in zip(rows, rows[1:]):
        name = "%s_step_%02d_%02d" % (key, p["i"], q["i"])
        v = {"from": (p["cell"], p["depth"], p["sink"]), "to": (q["cell"], q["depth"], q["sink"])}
        if p["sink"] is None or q["sink"] is None:
            R.result(name, v, expected="sink read", ok="UNMEASURED", source=q["src"])
        elif q["depth"] > p["depth"]:
            R.result(name, v, expected="sink strictly up (deeper)", ok=q["sink"] > p["sink"] + EPS, source=q["src"])
        elif q["depth"] < p["depth"]:
            R.result(name, v, expected="sink strictly down (shallower)", ok=q["sink"] < p["sink"] - EPS, source=q["src"])
        else:
            R.result(name, v, expected="same depth", ok=None, source=q["src"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", default=C.SAVE)
    ap.add_argument("--no-load", action="store_true", help="run on the map already loaded (it must be the gallery)")
    ap.add_argument("--origin", default=None)
    ap.add_argument("--parts", default="empty,occupied,walk3,walk4")
    ap.add_argument("--k", default=None, help="sink per level values, comma-separated")
    ap.add_argument("--hold", default=None, help="sink hold-above values, comma-separated")
    ap.add_argument("--grid", action="store_true", help="every k with every hold (default: zip the two lists)")
    ap.add_argument("--settle-ms", type=int, default=500)
    ap.add_argument("--tag", default="a")
    a = ap.parse_args()
    parts = a.parts.split(",")
    L = C.layout(tuple(int(v) for v in a.origin.split(",")) if a.origin else None)
    B = C.bridge()
    R = C.Run("depth", a.tag)
    try:
        if not a.no_load and not C.load_gallery(B, R, a.save):
            return
        C.pause(B, R)
        C.draft_all(B, R)
        if not check_fixture(B, R, L):
            R.harness_error("the A fixtures do not read as built: wrong map, origin or save")
        R.result("build_reads", {"DepthDrawState": C.scall(B, C.T_DRAW, C.M_STATE, "0")[0],
                                 "settings": {f: C.setting(B, f) for f in ("pitSinkPerLevel", "pitSinkHoldAbove",
                                                                           "pitSinkClampEnabled", "pitLookMode",
                                                                           "pitDepthDrawOffsetEnabled")}},
                 source="static_call probe + settings")
        if "empty" in parts:
            shoot_A(B, R, L, "empty", ("A1", "A2", "A3", "A4"))
        if "occupied" in parts:
            occupied(B, R, L, a)
        if "walk3" in parts:
            walk(B, R, L, a, "A3")
        if "walk4" in parts:
            walk(B, R, L, a, "A4")
        C.finish_shots(R)
    except Exception as e:  # noqa: BLE001
        import traceback
        R.harness_error("UNCAUGHT %s: %s | %s" % (type(e).__name__, e, traceback.format_exc()[-900:]))
    finally:
        try:
            C.pause(B)
        except Exception:  # noqa: BLE001
            pass
        R.close()


if __name__ == "__main__":
    main()
