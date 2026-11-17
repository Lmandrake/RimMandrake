#!/usr/bin/env python3
"""Acceptance checks for the Pyrelands round-9 coverage gaps (filed by
RIMMANDRAKE_RETAKE_PYRELANDS_EXAM_AFTER_LOCKED_CHANGE_RUN_TWO). Usage: accept_round9_gaps.py <check> [repo]. rc 0 = pass."""
import json
import os
import re
import sys

REPO = sys.argv[2] if len(sys.argv) > 2 else "."
C = os.path.join(REPO, "design/concepts/Pyrelands")


def scenes():
    s = json.load(open(os.path.join(C, "scenes.json")))
    return s["scenes"] if isinstance(s, dict) else s


def scene(i):
    return next(x for x in scenes() if x.get("id") == i)


def burned_share():
    # sc_burn_line_walks (or a scene naming burn_line_walks) reads the map's burned share per day, and a
    # windCarriesFireEnabled-off control on the same seed must read a larger share
    s = [x for x in scenes()
         if x.get("id") == "sc_burn_line_walks" or "burn_line_walks" in json.dumps(x.get("requirement"))]
    for x in s:
        ex = json.dumps(x.get("expect")).lower()
        ctl = json.dumps(x.get("control")).lower()
        if re.search(r"burn(ed|t) share|share of .{0,40}(ground|map)", ex) and "windcarriesfireenabled" in ctl:
            return True
    return False


def wind_bearings():
    p = os.path.join(REPO, "src/RimMandrake/Pyrelands/wind_burn_live.py")
    src = open(p).read()
    bearings = set(re.findall(r'"SetWindForTest",\s*"args":\s*"?(\d+)', src))
    sc = json.dumps(scene("sc_fire_walks_with_wind")).lower()
    # the verdict rows read the bearing the game returned, not only the burn
    m = re.search(r"def verdict_rows\(.*?(?=\ndef |\Z)", src, re.S)
    rows_read_wind = bool(m) and re.search(r"bearing|wind_set", m.group(0)) is not None
    return len(bearings) >= 2 and rows_read_wind and ("opposite" in sc or "reversed" in sc or "both bearings" in sc)


def text_fixes():
    sheet = open(os.path.join(C, "sheet.md")).read()
    tree = open(os.path.join(C, "tree.json")).read()
    rec = open(os.path.join(C, "record.json")).read()
    giant = json.dumps(scene("sc_furnace_giant").get("expect")) + json.dumps(scene("sc_furnace_giant").get("control"))
    return ("5 of 5 PASS live" not in sheet and "lights inside the colony" not in tree
            and "far from buildings after" not in rec and not re.search(r"\b(1\.8|7\.5|3\.2)\b", giant))


CHECKS = {"burned_share": burned_share, "wind_bearings": wind_bearings, "text_fixes": text_fixes}

if __name__ == "__main__":
    ok = CHECKS[sys.argv[1]]()
    print("%s %s" % ("PASS" if ok else "FAIL", sys.argv[1]))
    sys.exit(0 if ok else 1)
