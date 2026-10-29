"""Offline selftest of wakes_checks.py's verdict logic (WSL python3; no bridge). Each bar must be able to go red.
LIQUID_WAKES_FIX_FOOTPRINTS_GONE_QUIET: a colonist never on the liquid, or a counter that could not be read, is UNMEASURED,
never PASS; a wake with the setting OFF is FAIL; dug fresh water reads as RM_WaterThin since P14 and counts as water."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wakes_checks as WC  # noqa: E402

cases = []


def case(got, want, why):
    cases.append((got, want, why))


def X(on=12, base=0, delta=5, read=True):
    return {"onLiquid": on, "baseline": base, "delta": delta, "settingRead": read}


def OFF(on=12, base=0, delta=0, read=False):
    return X(on, base, delta, read)


ALL_ON = {k: X() for k in WC.LIQUID_TERRAINS}
ALL_OFF = {k: OFF() for k in WC.LIQUID_TERRAINS}

# terrain reads
case(WC.terrain_name("RM_WaterThin:60,44,1,1"), "RM_WaterThin", "get_terrain_batch ops parse")
case(WC.terrain_name("Soil:1,2,1,1;Sand:2,2,1,1"), "Soil", "first run only")
case(WC.terrain_name(""), None, "empty ops is unread, not a terrain")
case(WC.is_liquid("water", "RM_WaterThin"), True, "P14 dug fresh water is water")
case(WC.is_liquid("water", "RM_Fill_Water_Brim"), True, "fill tier still counts")
case(WC.is_liquid("water", "Soil"), False, "soil is not water")
case(WC.is_liquid("water", "WaterShallow"), False, "vanilla shallows are not our staged strip")
case(WC.is_liquid("slime", "RM_Fill_SlimeGreen_Half"), True, "slime fill tier")
case(WC.is_liquid("tar", "RM_SlimeGreenShallow"), False, "slime is not tar")
case(WC.is_liquid("tar", None), False, "unread terrain is not tar")

# crossing summary: only in-transit squares on this liquid count
S = [((58, 44), "Soil"), ((60, 44), "RM_WaterThin"), ((61, 44), "RM_WaterThin"), ((66, 44), "RM_WaterThin"), ((None, None), None)]
cs = WC.crossing_summary("water", S, (66, 44))
case((cs["onLiquid"], cs["arrived"], cs["terrains"]), (2, True, ["RM_WaterThin"]), "target square and soil excluded")
case(WC.crossing_summary("water", [((58, 44), "Soil")] * 30, (66, 44))["onLiquid"], 0, "walked around the strip: 0 on liquid")

# counter reads
case(WC.parse_render({"success": True, "result": "RM_TarShallow=1;RM_WaterThin=2"}), {"RM_TarShallow": 1, "RM_WaterThin": 2}, "render parse")
case(WC.parse_render({"success": True, "result": ""}), {}, "nothing noted yet is a real empty map")
case(WC.parse_render({"success": False, "message": "type not found"}), None, "failed call is unread")
case(WC.parse_render({"success": True}), {}, "successful reply with no result field == zero counts (first water crossing)")
case(WC.parse_render({"success": True, "result": None}), {}, "successful reply with null result == zeros")
case(WC.parse_render({}), None, "reply with neither success nor result is malformed")
case(WC.parse_render({"message": "x"}), None, "no success flag and no result: malformed")
case(WC.parse_render({"success": False}), None, "failed call without result stays unread")
case(WC.parse_render({"success": True, "error": "boom"}), None, "error field stays unread")
case(WC.parse_render("junk"), None, "non-dict reply is unread")
case(WC.count_delta("water", WC.parse_render({"success": True}), {"RM_WaterThin": 3}), 3, "empty-reply start gives a real delta")
case(WC.count_delta("water", WC.parse_render({"success": False}), {"RM_WaterThin": 3}), None, "failed start read stays UNMEASURED")
case(WC.crossing_verdict(X(delta=None), True)[0], "UNMEASURED", "undeltaable crossing is UNMEASURED")
# budget grows with path cost
case(WC.max_samples("water") >= 80, True, "water keeps the base budget")
case(WC.max_samples("slime") > WC.max_samples("water"), True, "slime budget grows with +200 cost")
case(WC.max_samples("tar") > WC.max_samples("slime"), True, "tar budget grows with +300 cost")
case(WC.max_samples("tar") >= 250, True, "tar budget >= 250 samples")
case(WC.max_samples("slime") * WC.SAMPLE_TICKS > 213 + WC.MIN_ON_SAMPLES * WC.SAMPLE_TICKS, True, "slime covers the 213-tick first step seen live")
case(WC.parse_render({"success": True, "result": "RM_WaterThin=x"}), None, "garbage is unread, not 0")
case(WC.count_delta("water", {"RM_WaterThin": 2}, {"RM_WaterThin": 5, "RM_TarShallow": 9}), 3, "delta only over this liquid")
case(WC.count_delta("water", {}, {"RM_Fill_Water_Half": 2}), 2, "terrain first noted mid-walk counts from 0")
case(WC.count_delta("water", None, {"RM_WaterThin": 5}), None, "unread before is not 0")
case(WC.parse_count({"success": True, "result": "7"}), 7, "Total parse")
case(WC.parse_count({"success": True, "result": "Error"}), None, "non-int Total is unread")

# one crossing
case(WC.crossing_verdict(X(), True)[0], "PASS", "on: waded, woke")
case(WC.crossing_verdict(X(delta=0), True)[0], "FAIL", "on: waded 12 samples, 0 wakes")
case(WC.crossing_verdict(X(on=0, delta=0), True)[0], "UNMEASURED", "never on the liquid is UNMEASURED, never PASS or FAIL")
case(WC.crossing_verdict(X(on=0, delta=0), False)[0], "UNMEASURED", "off: never on the liquid proves no silence")
case(WC.crossing_verdict(X(delta=None), True)[0], "UNMEASURED", "counter unreadable")
case(WC.crossing_verdict(X(base=None), True)[0], "UNMEASURED", "baseline unreadable")
case(WC.crossing_verdict(X(base=2), True)[0], "UNMEASURED", "something else waded during the baseline")
case(WC.crossing_verdict(X(read=False), True)[0], "UNMEASURED", "setting did not read back on")
case(WC.crossing_verdict(X(read=None), True)[0], "UNMEASURED", "setting unread")
case(WC.crossing_verdict(OFF(), False)[0], "PASS", "off: waded, 0 wakes")
case(WC.crossing_verdict(OFF(delta=3), False)[0], "FAIL", "off: any wake is FAIL")
case(WC.crossing_verdict(OFF(read=True), False)[0], "UNMEASURED", "off asked, read back on")
case(WC.crossing_verdict(X(on=WC.MIN_ON_SAMPLES - 1, delta=0), True)[0], "UNMEASURED", "below the bar's sample count")
case(WC.crossing_verdict(X(on=WC.MIN_ON_SAMPLES), True)[0], "PASS", "at the bar's sample count")
case(WC.MIN_ON_SAMPLES * WC.SAMPLE_TICKS >= 2 * WC.WAKE_CADENCE, True, "bar spans two wake cadences")

# the row
case(WC.w1_verdict(ALL_ON, ALL_OFF)[0], "PASS", "all three liquids both ways")
case(WC.w1_verdict(dict(ALL_ON, water=X(delta=0)), ALL_OFF)[0], "FAIL", "dug water silent: the defect this item fixes")
case(WC.w1_verdict(dict(ALL_ON, tar=X(on=0, delta=0)), ALL_OFF)[0], "UNMEASURED", "tar never waded")
case(WC.w1_verdict(dict(ALL_ON, tar=X(on=0, delta=0), water=X(delta=0)), ALL_OFF)[0], "FAIL", "a FAIL beats an UNMEASURED")
case(WC.w1_verdict(ALL_ON, {})[0], "UNMEASURED", "off never walked (e.g. aborted) is not PASS")
case(WC.w1_verdict({}, {})[0], "UNMEASURED", "nothing walked")
case(WC.w1_verdict(ALL_ON, dict(ALL_OFF, slime=OFF(delta=1)))[0], "FAIL", "slime woke with the setting off")
case(sorted(WC.w1_verdict(ALL_ON, ALL_OFF)[1]), sorted("%s_%s" % (k, t) for k in WC.LIQUID_TERRAINS for t in ("on", "off")), "six sub-verdicts")

bad = [(g, w, y) for g, w, y in cases if g != w]
for g, w, y in bad:
    print("FAIL", y, "got", g, "want", w)
print("selftest_wakes_checks: %d/%d" % (len(cases) - len(bad), len(cases)))
sys.exit(1 if bad else 0)
