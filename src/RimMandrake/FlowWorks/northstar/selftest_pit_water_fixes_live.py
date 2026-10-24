"""Offline checks for pit_water_fixes_live.py verdicts. No bridge.
Each owner finding of 2026-10-24 is fed the reading the OLD build gave (must FAIL), the fixed reading (must PASS),
and a could-not-ask reading (must be UNMEASURED, never PASS)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pit_water_fixes_live as W  # noqa: E402

fails = []


def check(name, got, want):
    ok = got == want
    print("%-4s  %-58s got %s" % ("ok" if ok else "FAIL", name, got))
    if not ok:
        fails.append(name)


def H(kind, *names):
    return {"success": True, "methods": [{kind: [{"patchMethod": n} for n in names]}]}


SW = "RimMandrake.FlowWorks.Swimming.RM_Patch_Pawn_SwimPose.Postfix"
CL = "RimMandrake.FlowWorks.RM_Patch_PitClickDrawnRow.Prefix"
# swim getter
check("getter: fixed build has the postfix", W.v_patched(H("postfixes", "Other.Postfix", SW), "postfixes", "RM_Patch_Pawn_SwimPose.Postfix")[0], "PASS")
check("getter: old build, no postfix", W.v_patched(H("postfixes", "Other.Postfix"), "postfixes", "RM_Patch_Pawn_SwimPose.Postfix")[0], "FAIL")
check("getter: tool refused", W.v_patched({"success": False}, "postfixes", "x")[0], "UNMEASURED")
# 2 m
check("2m: fixed (2 m swims, 1 m walks)", W.v_swim_2m(True, False)[0], "PASS")
check("2m: old (2 m walked)", W.v_swim_2m(False, False)[0], "FAIL")
check("2m: wrong rule (1 m swims too)", W.v_swim_2m(True, True)[0], "FAIL")
check("2m: no answer", W.v_swim_2m(None, False)[0], "UNMEASURED")
# 5 m surface
check("5m: fixed (swims, sink 0)", W.v_float(True, 0.0)[0], "PASS")
check("5m: old (walks on the floor, sink at cap 2.4)", W.v_float(False, 2.4)[0], "FAIL")
check("5m: swims but drawn on the floor", W.v_float(True, 2.4)[0], "FAIL")
check("5m: no answer", W.v_float(True, None)[0], "UNMEASURED")
# drafted swimmer every square
good = [{"cell": (i, j), "mode": m, "arrived": True, "swims": True, "sink": 0.0} for m in ("drafted", "undrafted") for i in range(3) for j in range(4)]
check("cells: fixed (all swim at the surface)", W.v_all_cells(good)[0], "PASS")
old = [dict(c, swims=(c["mode"] == "undrafted"), sink=(0.0 if c["mode"] == "undrafted" else 1.8)) for c in good]
check("cells: old (drafted not swimming)", W.v_all_cells(old)[0], "FAIL")
bottom = [dict(c, arrived=(c["cell"][1] == 0)) for c in good]
check("cells: old (floaters clamped to the bottom row)", W.v_all_cells(bottom)[0], "FAIL")
check("cells: nothing ordered", W.v_all_cells([])[0], "UNMEASURED")
# wet pit enterable
check("enter: fixed", W.v_enter(True, True)[0], "PASS")
check("enter: old (no way in)", W.v_enter(False, False)[0], "FAIL")
check("enter: no answer", W.v_enter(None, True)[0], "UNMEASURED")
# ladder / ramp in the wet pit
check("build: fixed", W.v_build({"RM_Ladder": True, "RM_PitRamp": True}, {"RM_Ladder": True, "RM_PitRamp": True})[0], "PASS")
check("build: old (refused in water)", W.v_build({"RM_Ladder": False, "RM_PitRamp": False}, {"RM_Ladder": True, "RM_PitRamp": True})[0], "FAIL")
check("build: dry control refused -> site", W.v_build({"RM_Ladder": False, "RM_PitRamp": True}, {"RM_Ladder": False, "RM_PitRamp": True})[0], "UNMEASURED")
check("accepted(): reads nested accepted", W.accepted({"success": True, "cells": [{"accepted": True}]}), True)
check("accepted(): unknown shape -> None", W.accepted({"success": True, "foo": 1}), None)
# click
sinks = {10: 0.6, 11: 0.6, 12: 0.6, 13: 0.6, 14: 0.6}
check("pick replica: 1 m pit click on row 12 -> 13", W.pick_row(12, 12.5, lambda z: {12: .6, 13: .6, 14: .6}.get(z, 0.0)), 13)
check("pick replica: last row stays", W.pick_row(14, 14.5, lambda z: {12: .6, 13: .6, 14: .6}.get(z, 0.0)), 14)
check("click wired: fixed", W.v_click_wired(H("prefixes", CL), sinks, 10)[0], "PASS")
check("click wired: old (no prefix)", W.v_click_wired(H("prefixes"), sinks, 10)[0], "FAIL")
check("click wired: dry rim (no sink) not discriminating", W.v_click_wired(H("prefixes", CL), {10: 0.0, 11: 0.0}, 10)[0], "FAIL")
check("click wired: sink unread", W.v_click_wired(H("prefixes", CL), {10: None}, 10)[0], "UNMEASURED")
check("click e2e: fixed (walks to the drawn row)", W.v_click_e2e(10, 11, 11, True)[0], "PASS")
check("click e2e: old (walks to the clicked row)", W.v_click_e2e(10, 11, 10, True)[0], "FAIL")
check("click e2e: no move issued -> harness", W.v_click_e2e(10, 11, None, False)[0], "UNMEASURED")
# shallow shader
check("shader: fixed", W.v_shader({"RM_WaterThin": "Map/WaterDepth", "RM_WaterVeryShallow": "Map/WaterDepth"}, "Map/WaterDepth")[0], "PASS")
check("shader: old (none)", W.v_shader({"RM_WaterThin": None, "RM_WaterVeryShallow": None}, "Map/WaterDepth")[0], "FAIL")
check("shader: control unreadable", W.v_shader({"RM_WaterThin": "x", "RM_WaterVeryShallow": "x"}, None)[0], "UNMEASURED")
# god-mode ladder
check("godmode: fixed (finished ladder)", W.v_godmode(["RM_LadderPortable", "Human"])[0], "PASS")
check("godmode: old (blueprint waiting on wood)", W.v_godmode(["Blueprint_RM_LadderPortable"])[0], "FAIL")
check("godmode: nothing placed", W.v_godmode([])[0], "FAIL")
# sluice
check("sluice: fixed (closed blocks)", W.v_sluice(False, True)[0], "PASS")
check("sluice: old (walks through like a door)", W.v_sluice(True, True)[0], "FAIL")
check("sluice: door control failed -> site", W.v_sluice(False, False)[0], "UNMEASURED")
# every row is mapped to an item
check("every row names an item", sorted(k for k, v in W.ITEMS.items() if not v), [])

print("%d failure(s)" % len(fails))
sys.exit(1 if fails else 0)
