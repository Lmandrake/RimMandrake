#!/usr/bin/env python3
"""T_FRAMES_SUBJECT (RIMMANDRAKE_FRAME_PYRE_CHAIN_SHOTS_ON_THEIR_SUBJECT): every capture in Pyrelands' validation.py frames
a named rect, so the picture the judge reads for a bar holds that bar's subject.

The fault (visit 2, 2026-11-20): a bare `t.screenshot()` jumps the camera to the suite anchor at whatever zoom the last
call left. Every chain anchors on PAD_PROBE (225, 225), so 20 captures showed one east-edge frame (a grass field and a
concrete pad, the right fifth off the map): no furnace-beast in giant_furnace_beast, no herd in herd_follows_two_day_old_burn,
and the skies of cinderfall / three_skies on that same frame. northstar_driver/judge_cli.py judges a component's LAST
capture as the picture of each bar its `shows=` claims.

Static, offline. Checks:
  1 every `.screenshot(...)` / `.capture_frames(...)` call in validation.py names a rect (keyword `rect=`);
  2 every component that claims a bar (`_comp(t, NAME, shows=[...])`, non-empty) still takes a capture inside its block,
    directly or through a validation.py function it calls (a claim with no capture is UNMEASURED by construction);
  3 the pure framing helpers (frame_rect, densest_cluster, inside_map) on worked inputs: empty, None coordinates, one
    cell, a cluster, a subject on the map edge, a map smaller than the minimum side, ties.

  python3 <this file>          exit 0 = every check PASS, 1 = any FAIL
  python3 <this file> --old F  run checks 1-2 on another copy of validation.py (a planted fault, or the parent's file)
"""
import ast
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATION = os.path.join(HERE, "validation.py")
NAME = "selftest_pyrelands_frames_subject"
CAPTURES = ("screenshot", "capture_frames")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -- " + detail) if detail else ""))


def _is_capture(node):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in CAPTURES)


def _names_rect(call):
    return any(k.arg == "rect" and not (isinstance(k.value, ast.Constant) and k.value.value is None)
               for k in call.keywords)


def captures_without_rect(tree):
    """-> ([(line, source-ish)] of captures that name no rect, number of captures read)."""
    bad, n = [], 0
    for node in ast.walk(tree):
        if _is_capture(node):
            n += 1
            if not _names_rect(node):
                bad.append(node.lineno)
    return bad, n


def _comp_claim(item):
    """A `with _comp(t, "name", shows=[...])` item -> (name, [bar ids]) or None."""
    c = item.context_expr
    if not (isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == "_comp"):
        return None
    name = c.args[1].value if len(c.args) > 1 and isinstance(c.args[1], ast.Constant) else "?"
    for k in c.keywords:
        if k.arg == "shows" and isinstance(k.value, (ast.List, ast.Tuple)):
            return name, [e.value for e in k.value.elts if isinstance(e, ast.Constant)]
    return name, []


# A component whose subject is a flyer in flight takes no capture: a flyer is read by its Pawn_FlightTracker state,
# never captured in flight (owner: "For the third time, do not do live testing of flyers without a human present.").
FLYER_NO_CAPTURE = frozenset(("firehawk_carries_ember",))


def claims_without_capture(tree):
    """-> ([component names that claim a bar but take no capture in their block], number of claiming components)."""
    funcs = dict((f.name, f) for f in tree.body if isinstance(f, ast.FunctionDef))
    captures_in = {}

    def takes(fn_name, seen):
        if fn_name in captures_in:
            return captures_in[fn_name]
        if fn_name in seen or fn_name not in funcs:
            return False
        seen = seen | {fn_name}
        got = any(_is_capture(n) for n in ast.walk(funcs[fn_name])) or any(
            isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and takes(n.func.id, seen)
            for n in ast.walk(funcs[fn_name]))
        captures_in[fn_name] = got
        return got

    bad, n = [], 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.With):
            continue
        for item in node.items:
            cl = _comp_claim(item)
            if not cl or not cl[1]:
                continue
            n += 1
            body = ast.Module(body=node.body, type_ignores=[])
            direct = any(_is_capture(x) for x in ast.walk(body))
            via = any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and takes(x.func.id, frozenset())
                      for x in ast.walk(body))
            if not (direct or via) and cl[0] not in FLYER_NO_CAPTURE:
                bad.append("%s (line %d)" % (cl[0], node.lineno))
    return bad, n


def static_checks(path):
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), path)
    bad, n = captures_without_rect(tree)
    check("every capture names a rect (%d captures read, %d without)" % (n, len(bad)), n > 0 and not bad,
          "lines %s" % bad if bad else "")
    bad2, n2 = claims_without_capture(tree)
    check("every bar-claiming component takes a capture (%d components read, %d without)" % (n2, len(bad2)),
          n2 > 0 and not bad2, ", ".join(bad2))


def _load_validation():
    utils = os.path.join(HERE, "..", "Utils")
    for p in (utils, os.path.join(utils, "modcheck"), HERE):
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location("pyre_validation_frames", VALIDATION)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pure_checks():
    v = _load_validation()
    fr, dc, im = v.frame_rect, v.densest_cluster, v.inside_map
    M = (250, 250)
    check("frame_rect: no cells -> None (a subject that is not on the map is never framed)", fr([], M) is None)
    check("frame_rect: only None coordinates -> None", fr([(None, 3), (4, None), None], M) is None)
    one = fr([(100, 100)], M, pad=3, min_side=12)
    check("frame_rect: one cell -> a min_side square that holds it", one == (95, 95, 12, 12), repr(one))
    big = fr([(10, 20), (60, 40)], M, pad=3, min_side=12)
    check("frame_rect: a spread -> its bounding box grown by pad on every side", big == (7, 17, 57, 27), repr(big))
    worst = []
    for cells in ([(0, 0)], [(249, 249)], [(0, 249)], [(249, 0)], [(-5, 300)], [(1, 1), (248, 248)]):
        r = fr(cells, M, pad=3, min_side=12)
        x, z, w, h = r
        inside = 0 <= x and 0 <= z and x + w <= M[0] and z + h <= M[1]
        holds = all(x <= min(max(c[0], 0), 249) < x + w and z <= min(max(c[1], 0), 249) < z + h for c in cells)
        if not (inside and holds and w >= 12 and h >= 12):
            worst.append((cells, r))
    check("frame_rect: edge and off-map subjects stay inside the map and in frame (6 cases)", not worst, repr(worst))
    small = fr([(3, 3)], (8, 6), pad=3, min_side=12)
    check("frame_rect: a map smaller than min_side -> the whole map", small == (0, 0, 8, 6), repr(small))
    fl = fr([(10.6, 20.4)], M, pad=0, min_side=1)
    check("frame_rect: float cells round to their cell", fl == (11, 20, 1, 1), repr(fl))
    check("densest_cluster: no cells -> []", dc([], 24) == [])
    pts = [(5, 5), (6, 7), (8, 9), (200, 200), (30, 30)]
    got = dc(pts, 24)
    check("densest_cluster: the busiest window wins", sorted(got) == [(5, 5), (6, 7), (8, 9)], repr(got))
    tie = dc([(100, 100), (5, 5)], 24)
    check("densest_cluster: a tie picks the lowest window, deterministically", tie == [(5, 5)], repr(tie))
    nn = dc([(None, 1), (3, 4)], 24)
    check("densest_cluster: None coordinates are skipped", nn == [(3, 4)], repr(nn))
    # front_crop (HARNESS, visit 6): a burn front plus two stray fires far off (the run read 12-21 fires off the front)
    import math
    fc = getattr(v, "front_crop", None)
    arc = [(int(round(100 + 40 * math.cos(a / 20.0))), int(round(150 + 40 * math.sin(a / 20.0)))) for a in range(0, 63)]
    held = []
    for k in range(0, len(arc) - 8, 4):
        part = arc[k:k + 30] + [(30, 30), (31, 30)]   # a front segment of 30 fires and two stray fires far off
        r = fc(part) if fc else None
        inside = sum(1 for c in part[:-2] if r and r[0] <= c[0] < r[0] + r[2] and r[1] <= c[1] < r[1] + r[3])
        held.append(inside)
    def old_corner(cells, crop=30):   # the parent's rule, kept here as the planted fault this check must see
        x0, z0 = min(c[0] for c in cells), min(c[1] for c in cells)
        return x0, z0, max(min(crop, max(c[0] for c in cells) - x0 + 1), 4), max(min(crop, max(c[1] for c in cells) - z0 + 1), 4)
    old_held = []
    for k in range(0, len(arc) - 8, 4):
        part = arc[k:k + 30] + [(30, 30), (31, 30)]
        r = old_corner(part)
        old_held.append(sum(1 for c in part[:-2] if r[0] <= c[0] < r[0] + r[2] and r[1] <= c[1] < r[1] + r[3]))
    check("front_crop: the parent's min-corner rule leaves a crop with no front fire (the check can see the "
          "fault: fires inside %r)" % old_held, min(old_held) == 0, repr(old_held))
    check("front_crop: every crop holds front fire (%d segments, fires inside %r)" % (len(held), held),
          bool(held) and min(held) > 0, repr(held))
    check("front_crop: no cells -> None", fc is not None and fc([]) is None)
    one = fc([(10, 20)]) if fc else None
    check("front_crop: one fire -> a 4x4 rect on it", one == (10, 20, 4, 4), repr(one))
    check("inside_map: a rect over the edge slides back inside", im((230, 230, 48, 48), M) == (202, 202, 48, 48),
          repr(im((230, 230, 48, 48), M)))
    check("inside_map: a rect wider than the map -> the whole width", im((-10, 5, 400, 20), M) == (0, 5, 250, 20),
          repr(im((-10, 5, 400, 20), M)))


def main(argv):
    path = VALIDATION
    if "--old" in argv:
        path = argv[argv.index("--old") + 1]
    static_checks(path)
    if path == VALIDATION:
        try:
            pure_checks()
        except AttributeError as e:
            check("pure framing helpers exist in validation.py", False, str(e))
    fails = [r for r in RESULTS if not r[1]]
    print("%s: %d checks, %d FAIL" % (NAME, len(RESULTS), len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
