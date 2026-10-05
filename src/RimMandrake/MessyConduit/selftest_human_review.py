"""selftest_human_review.py -- offline checks of the Messy Conduit review map's LAYOUT (no bridge, no game).

    python3 src/RimMandrake/MessyConduit/selftest_human_review.py

Round 4 (owner 2026-10-04, station 26: "battery having no connection to local power pole for some reason, perhaps only
graphically. Do devices connect to power poles when not touching over some distance (as usual)?"): a Battery is a power
TRANSMITTER, and vanilla joins transmitters only by touching; the 6-cell reach (PowerConnectionMaker.ConnectMaxDist) is for
consumers. Four stations (19, 20, 26, 28) had batteries standing off their pole or conduit: separate, unwired nets.
  1. layout_check(station_list()) is clean (every station inside its region, spacing, links in range, batteries touching)
  2. can fail: the round-3 station 26 battery (x 1, a one-cell gap to the mast at x 3) is reported
  3. sanity probe: a battery touching only ANOTHER battery that touches the conduit counts as joined
  4. station 21 is the round-4 "over the unknown" layout: two masts in range, a solid fogged, mountain-roofed block between
     them that the straight line between the masts crosses, and no conduit through it
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import human_review as HR  # noqa: E402

fails = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        fails.append(msg)


S = HR.station_list()
probs = HR.layout_check(S)
check(not probs, "layout_check clean over %d stations%s" % (len(S), (": " + "; ".join(probs[:4])) if probs else ""))

s26 = next(s for s in S if s["n"] == 26)
old = dict(s26, devs=[("Battery", (1, 9), 0, 1.0)] + [d for d in s26["devs"] if d[0] != "Battery"])
bad = HR.battery_touch([old])
check(len(bad) == 1 and "station 26" in bad[0], "can fail: the round-3 station-26 battery (one cell off the mast) is reported: %s" % bad)

probe = dict(n=99, conduit=[(5, 5)], wconduit=[], masts=[],
             devs=[("Battery", (4, 4), 0, 1.0), ("Battery", (3, 4), 0, 1.0), ("Battery", (0, 0), 0, 1.0)])
pb = HR.battery_touch([probe])
check(len(pb) == 1 and "(0, 0)" in pb[0], "sanity probe: chained batteries join, a lone one is reported (%s)" % pb)

s21 = next(s for s in S if s["n"] == 21)
(ax, az), (bx, bz) = s21["masts"][0][1], s21["masts"][1][1]
rock = set(s21["rock"])
line = [(round(ax + (bx - ax) * t / 100.0), round(az + (bz - az) * t / 100.0)) for t in range(101)]
crosses = sum(1 for c in set(line) if c in rock)
in_range = (ax - bx) ** 2 + (az - bz) ** 2 <= HR.SPAN_RANGE ** 2
fogged = s21.get("fog", {}).get("refog") and not s21["fog"].get("unfog")
roofed = any(rd == "RoofRockThick" for rd, _ in s21.get("roof", []))
through = [c for c in s21["conduit"] if c in rock]
check(in_range and crosses >= 10 and fogged and roofed and not through and (ax, az) not in rock and (bx, bz) not in rock,
      "station 21: masts %s-%s in range %s, the line crosses %d block cells, fogged %s, mountain roof %s, conduit through it %d"
      % ((ax, az), (bx, bz), in_range, crosses, bool(fogged), roofed, len(through)))

print("%d/%d checks passed" % (4 - len(fails), 4))
sys.exit(1 if fails else 0)
