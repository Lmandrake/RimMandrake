"""Offline selftest of walls_slots_live.py: the kernel mirror equals design section 3/4, --dry-run and --table exit 0, a clean
--mock run has no FAIL row, and every --mock-fault turns the rows it is meant to turn into FAIL (the proof that the rows can fail).
python3 src/RimMandrake/HugeThings/northstar/selftest_walls_slots_live.py"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import walls_slots_live as W  # noqa: E402

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def run(*extra):
    out = tempfile.mkdtemp(prefix="wsl_selftest_")
    p = subprocess.run([sys.executable, os.path.join(HERE, "walls_slots_live.py"), "--out-dir", out] + list(extra),
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    rows = []
    try:
        rows = json.load(open(os.path.join(out, "session.json")))["rows"]
    except (OSError, ValueError):
        pass
    return p.returncode, rows, p.stdout


check(W.selftest() == [], "kernel mirror equals design section 3 (blows per cell) and section 4 (squeeze costs)")
check(W.ladder_ts(3, 510.0, False) == [1, 2, 3], "ladder_ts B3 granite: 1, B-1, B")
check(W.ladder_ts(6, 195.0, False, full=True) == [1, 2, 3, 4, 5, 6], "full ladder is 1..6")
check(W.stops_up_to(3) == 3 and W.stops_up_to(1) == 1 and W.stops_up_to(0) == 0, "wall inspect: StopsUpTo")
check(W.creature_line(4, 4, dict(hold_line=1.0, per=100.0), True).startswith("Breadth 4 (needs 4-wide gaps) · squeezes gaps of 2+ · breaks walls up to 400 HP"),
      "creature line for B4 (design 5.9 example)")
check(W.parse_cell({"x": 3, "z": 9}) == (3, 9) and W.parse_cell("(3, 0, 9)") == (3, 9) and W.parse_cell([3, 0, 9]) == (3, 9), "cell parsing")
check(W.interp_cross([(0, 5, 0), (10, 7, 0)], 6) == 5.0, "interp_cross is linear between samples")
z = W.shelf_pack([("a", 30, 41), ("b", 30, 41), ("c", 30, 41)], (15, 15, 100, 120))
check(all(not W.overlaps(z[a], z[b], 2) for a in z for b in z if a < b), "shelf_pack zones do not overlap")
# pass 3 (2026-10-19): the lanes are sealed. Pass 2's open-ended lanes let the creature walk round (the decider breaks toward
# a REACHABLE goal only past a 2.5x detour), so a plan that leaks is refused before it is staged.
zone = (20, 20, W.LEAD + 6 + W.LEAD, W.LANE_H)
lanes = [W.build_ladder_lane("t%d" % t, "B4", "wood", False, t, zone) for t in range(1, 7)]
lanes += [W.build_canyon_lane("S%d" % sl, "B6", sl, (20, 20, W.LEAD + W.CANYON_LEN + W.LEAD, W.CANYON_H)) for sl in range(1, 7)]
check(all(not W.lane_leaks(ln, ln.meta.get("gap_cells") or ()) for ln in lanes), "every sealed ladder/canyon plan: no way to the goal round the structure")
check(all(W.lane_leaks(ln) for ln in lanes if ln.kind == "canyon"), "a canyon's gap IS a way through (the flood fill sees the gap)")
open_lane = W.build_ladder_lane("open", "B4", "wood", False, 1, zone, sealed=False)
check(W.lane_leaks(open_lane), "the same wall without its moat leaks (pass 2's layout)")
ln = lanes[0]
check(all(zone[1] < c[1] < zone[1] + zone[3] - 1 for c in ln.walls) and len(ln.walls) == W.LANE_H - 2, "a ladder wall spans the interior moat to moat")
check(ln.start not in W.moat_cells(zone) and ln.goal not in W.moat_cells(zone), "start and goal inside the moat")
for b_ in (2, 3, 4, 6):
    line = W.creature_line(b_, b_, dict(hold_line=1.0, per=100.0), True).lower()
    check(W.REPORT_SMASH not in line and W.REPORT_SQUEEZE not in line,
          "B%d creature line never reads as a smash/squeeze job report (pass 2 matched 'smash'/'squeez' in it)" % b_)
rc, rows, out = run("--dry-run")
check(rc == 0 and "DRY RUN" in out, "--dry-run exits 0")
rc, rows, out = run("--mock")
check(rc == 0 and rows and not [r for r in rows if r["status"] == "FAIL"], "clean --mock: no FAIL row (%d rows)" % len(rows))
check(len([r for r in rows if r["status"] == "PASS"]) > 80, "clean --mock exercises > 80 PASS rows")
# review wave 6 (2026-10-19): a mock run wrote seven ledger-ready `rimflow verify --result pass` lines against the fake game.
check("verify lines 0 " in out, "a --mock run writes no ledger-ready verify line (a mock proves paths, never the game)")
rc, rows, out = run("--mock", "--only", "A3")
check("verify lines 0 " in out, "a partial (--only) run writes no ledger-ready verify line (never recordable)")
for fault, prefix in (("hold", "A3_"), ("squeeze", "A2_cost"), ("roof", "A3_"), ("rock", "A2_"), ("scrape", "A6_scrape"),
                      ("defaults", "A8_defaults"), ("label", "A8_dialog_group")):
    rc, rows, out = run("--mock", "--mock-fault", fault)
    check(any(r["status"] == "FAIL" and r["id"].startswith(prefix) for r in rows), "--mock-fault %s turns a %s row to FAIL" % (fault, prefix))
rc, rows, out = run("--mock", "--mock-fault", "unsealed")
a3 = [r for r in rows if r["criterion"] == "A3"]
check(a3 and all(r["status"] == "UNMEASURED" and r["cls"] == "SITE" for r in a3),
      "--mock-fault unsealed (no moat): every A3 row is SITE/UNMEASURED (the creature walked round), never PASS")
rc, rows, out = run("--mock", "--mock-fault", "norock")
check(any(r["id"] == "A2_canyons" and r["status"] == "UNMEASURED" for r in rows) and not [r for r in rows if r["status"] == "FAIL"],
      "no placeable rock = A2 UNMEASURED, never PASS or FAIL")
print("FAILS: %d" % len(FAILS))
sys.exit(1 if FAILS else 0)
