#!/usr/bin/env python3
"""Every texture Gimme Some Slack draws is classed by how a cord joins it (RIMMANDRAKE_BIND_SLACK_STUB_ANGLE_RULE_FOURTH_ASK).

Owner 2026-11-16: "It should be true for every art piece that has stubs/connectors at particular angles that need to be matched." The
position-and-slope check (Source/Core/StubJoinAudit.cs, StubArt.Census) reads one table; this test fails when a PNG under Textures/ is not
in it, so a new connector cannot ship unclassed and silently outside the check. It also proves it can fail, on a planted unknown name.

    python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_stub_art_census.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, "Source", "Core", "StubJoinAudit.cs")
TEX = os.path.join(HERE, "Textures")
ROW = re.compile(r'\("([A-Za-z0-9_]+)",\s*Join\.(\w+),')


def census(src):
    return {m.group(1): m.group(2) for m in ROW.finditer(src)}


def textures(root):
    return sorted({os.path.splitext(f)[0] for _d, _s, fs in os.walk(root) for f in fs if f.lower().endswith(".png")})


def unclassed(names, table):
    return [n for n in names if n not in table]


def main():
    with open(TABLE, encoding="utf-8") as f:
        table = census(f.read())
    names = textures(TEX)
    fails = []
    if len(names) < 20:
        fails.append("instrument: only %d textures found under %s" % (len(names), TEX))
    if len(table) < 20:
        fails.append("instrument: only %d census rows parsed from %s" % (len(table), TABLE))
    miss = unclassed(names, table)
    if miss:
        fails.append("unclassed textures (add each to StubArt.Census with how a cord joins it): " + ", ".join(miss))
    stale = sorted(set(table) - set(names))
    if stale:
        fails.append("census rows naming no texture: " + ", ".join(stale))
    stubbed = sorted(n for n, k in table.items() if k == "Stubs")
    for must in ("Junction_X", "Junction_T", "PowerSwitch", "Plug", "PlugTop", "PowerStrip", "StubWall", "StubRock", "WallOutlet"):
        if table.get(must) != "Stubs":
            fails.append("%s must be classed Stubs, is %s" % (must, table.get(must)))
    for must in ("WallBracket", "AerialMastTop", "StandingLamp"):
        if table.get(must) != "PositionOnly":
            fails.append("%s is stubless (owner 2026-11-16), must be PositionOnly, is %s" % (must, table.get(must)))
    # the guard can fail: a planted unknown texture is caught
    if unclassed(names + ["Junction_Y_Planted"], table) != miss + ["Junction_Y_Planted"]:
        fails.append("guard: a planted unclassed texture was not caught")
    print("stub art census: %d textures, %d census rows, %d stubbed (%s)" % (len(names), len(table), len(stubbed), " ".join(stubbed)))
    for f in fails:
        print("FAIL " + f)
    print("%s" % ("PASS" if not fails else "FAIL"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
