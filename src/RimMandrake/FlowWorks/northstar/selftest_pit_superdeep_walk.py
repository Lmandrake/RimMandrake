"""selftest_pit_superdeep_walk.py -- offline proof of pit_superdeep_walk.py: the pure verdicts read good, old/bad and
could-not-ask shapes correctly, the --mock walk runs end to end all PASS (exit 0) with captures, map and index, and each
model fault turns its own row red (a row never seen red proves nothing)."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "Utils"))
import pit_superdeep_walk as W  # noqa: E402

fails = []


def check(name, got, want):
    if got != want:
        fails.append("%s: got %r want %r" % (name, got, want))


CLIMB_T = W.kv("CLIMB k=2 held=True trapped=True cell=1,1 | POCKET k=2 comp=1 pocket=True size=9 depth=3 gen=4 built=4")
CLIMB_F = W.kv("CLIMB k=2 held=False trapped=False cell=1,1 | POCKET k=2 comp=1 pocket=False size=9 depth=3 gen=4 built=4")
WALK_IN, WALK_OUT = ("PASS", {}), ("PASS", {})

# width
check("width ok", W.v_width({"held": True, "requiredWidth": 1}, {"held": False, "requiredWidth": 2})[0], "PASS")
check("width muffalo held", W.v_width({"held": True, "requiredWidth": 1}, {"held": True, "requiredWidth": 2})[0], "FAIL")
check("width calf", W.v_width({"held": True, "requiredWidth": 1}, {"held": True, "requiredWidth": 1})[0], "UNMEASURED")
check("width missing", W.v_width(None, {"held": False, "requiredWidth": 2})[0], "UNMEASURED")
# ladder
up, dn = {"present": "True", "raised": "True"}, {"present": "True", "raised": "False"}
check("ladder ok", W.v_ladder(up, CLIMB_T, WALK_IN, dn, CLIMB_F, WALK_OUT)[0], "PASS")
check("ladder ignored", W.v_ladder(up, CLIMB_T, WALK_IN, dn, CLIMB_T, ("FAIL", {}))[0], "FAIL")
check("ladder absent", W.v_ladder({"present": "False"}, CLIMB_T, WALK_IN, dn, CLIMB_F, WALK_OUT)[0], "UNMEASURED")
# jump
t0 = W.kv("TRAP descents=3 lastCell=none pos=5,5 held=False last=-")
t1 = W.kv("TRAP descents=4 lastCell=10,10 pos=10,10 held=True last=-")
check("jump ok", W.v_jump("(10, 0, 10)", "True", t0, t1, (9, 9, 3, 3))[0], "PASS")
check("jump refused", W.v_jump("(10, 0, 10)", "False", t0, t0, (9, 9, 3, 3))[0], "FAIL")
check("jump no target", W.v_jump("(-1000, -1000, -1000)", "False", t0, t0, (9, 9, 3, 3))[0], "UNMEASURED")
# careless
o = {"orderAccepted": True, "ticksElapsed": 600, "arrived": False, "end": {"x": 3, "z": 6}}
check("careless ok", W.v_careless(o, (3, 3), 2, 2)[0], "PASS")
check("careless fell", W.v_careless(dict(o, arrived=True, end={"x": 3, "z": 3}), (3, 3), 2, 3)[0], "FAIL")
check("careless no end", W.v_careless(dict(o, end=None), (3, 3), 2, 2)[0], "UNMEASURED")
check("careless not ordered", W.v_careless({"orderAccepted": False}, (3, 3), 2, 2)[0], "UNMEASURED")
# cover
c0, c1 = {"covered": "True", "sprung": "False"}, {"covered": "False", "sprung": "True"}
check("cover ok", W.v_cover_fall(c0, c1, t0, t1)[0], "PASS")
check("cover held up", W.v_cover_fall(c0, c0, t0, t0)[0], "FAIL")
check("cover not laid", W.v_cover_fall({"covered": "False"}, c1, t0, t1)[0], "UNMEASURED")
# room
r0 = {"split": "True", "pitRoom": "True", "prison": "False"}
check("room ok", W.v_room(r0, dict(r0, prison="True"), "Thing_Bed1")[0], "PASS")
check("room bedless prison", W.v_room(dict(r0, prison="True"), dict(r0, prison="True"), "b")[0], "FAIL")
check("room no bed built", W.v_room(r0, r0, None)[0], "UNMEASURED")
# capture / convert
check("capture ok", W.v_capture("VERDICT Allowed held=True", {"prisoner": "True"}, (1, 1), (5, 5, 3, 3))[0], "PASS")
check("capture warden in pit", W.v_capture("VERDICT Allowed", {"prisoner": "True"}, (6, 6), (5, 5, 3, 3))[0], "FAIL")
check("capture unread", W.v_capture("", {}, (1, 1), (5, 5, 3, 3))[0], "UNMEASURED")
check("convert ok", W.v_convert({"serve": "True", "kind": "Interact", "lipInPit": "False", "dist": "1.4"})[0], "PASS")
check("convert far", W.v_convert({"serve": "True", "kind": "Interact", "lipInPit": "False", "dist": "9"})[0], "FAIL")
# doors
line = "DOOR RM_Sluice | P1 SHUT | M1 SHUT | H1 SHUT"
check("door verdict", W.door_verdict(line, "M1"), "SHUT")
check("sluice ok", W.v_sluice_shut(line, ["P1", "M1", "H1"])[0], "PASS")
check("sluice opens", W.v_sluice_shut(line.replace("M1 SHUT", "M1 OPEN"), ["P1", "M1", "H1"])[0], "FAIL")
check("sluice pawn missing", W.v_sluice_shut(line, ["P1", "X9"])[0], "UNMEASURED")
check("lift ok", W.v_sluice_lift("DOOR RM_Sluice lifted=True open=True", "DOOR RM_Sluice lifted=False open=False")[0],
      "PASS")
check("lift refused", W.v_sluice_lift("", "")[0], "UNMEASURED")
check("grate ok", W.v_grate("DOOR g | P1 SHUT", "P1", True)[0], "PASS")
check("grate opens", W.v_grate("DOOR g | P1 OPEN", "P1", True)[0], "FAIL")
check("grate not held", W.v_grate("DOOR g | P1 SHUT", "P1", False)[0], "UNMEASURED")
# flood
sw, dr = {"headUp": "True"}, {"exit": "False"}
check("flood ok", W.v_flood(True, sw, dr, CLIMB_T)[0], "PASS")
check("flood exit", W.v_flood(True, sw, {"exit": "True"}, CLIMB_F)[0], "FAIL")
check("flood unread", W.v_flood(None, {}, {}, CLIMB_T)[0], "UNMEASURED")
check("brim ok", W.v_near_brim({"exit": "True"}, CLIMB_F)[0], "PASS")
check("brim trapped", W.v_near_brim({"exit": "False"}, CLIMB_T)[0], "FAIL")
trail = [(60, 0.3, (6, 6), False, True), (120, 0.65, (6, 6), False, True)]
warn = ["x " + W.WARN_TEXT + " y"]
check("warned ok", W.v_warned(trail, 0.6, [], warn, (5, 5, 3, 3))[0], "PASS")
check("warned silent", W.v_warned(trail, 0.6, [], [], (5, 5, 3, 3))[0], "FAIL")
check("warned old only", W.v_warned(trail, 0.6, warn, warn, (5, 5, 3, 3))[0], "FAIL")
check("warned out of pit", W.v_warned([(60, 0.7, (1, 1), False, True)], 0.6, [], warn, (5, 5, 3, 3))[0], "FAIL")
check("warned never", W.v_warned(trail[:1], 0.6, [], warn, (5, 5, 3, 3))[0], "FAIL")
check("warned unreadable", W.v_warned(trail, 0.6, None, warn, (5, 5, 3, 3))[0], "UNMEASURED")
# children
check("exposure ok", W.v_exposure({"hediffs": [{"def": "RM_PitExposure"}]})[0], "PASS")
check("exposure none", W.v_exposure({"hediffs": []})[0], "FAIL")
check("exposure no pawn", W.v_exposure(None)[0], "UNMEASURED")
check("wallart ok", W.v_wallart("WALLS visible=True verts=96")[0], "PASS")
check("wallart blank", W.v_wallart("WALLS visible=True verts=0")[0], "FAIL")
check("wallart refused", W.v_wallart("")[0], "UNMEASURED")
check("parse_xz", (W.parse_xz("4,-2"), W.parse_xz({"x": 1, "z": 2}), W.parse_xz("x")), ((4, -2), (1, 2), None))
check("flat strings", sorted(W.flat_strings({"a": ["x", {"b": "y"}], "n": 3})), ["x", "y"])


def mock_run(tmp, fault=""):
    out = os.path.join(tmp, fault or "clean")
    argv = ["--mock", "--out-dir", out] + (["--mock-fault", fault] if fault else [])
    rc = W.main(argv)
    with open(os.path.join(out, "result.json"), encoding="utf-8") as f:
        res = json.load(f)
    return rc, {r["id"]: r["status"] for r in res["rows"]}, res, out


with tempfile.TemporaryDirectory() as tmp:
    rc, st, res, out = mock_run(tmp)
    check("mock exit", rc, 0)
    check("mock rows", len(st), 20)
    check("mock all PASS", sorted(k for k, v in st.items() if v != "PASS"), [])
    check("mock settings restored", res.get("swimEnduranceRestored"), "3")
    for f in ("walk_map.png", "index.html", "S1.png", "S9.png", "S10.png"):
        check("mock wrote " + f, os.path.exists(os.path.join(out, f)), True)
    check("mock no picture error", res.get("pictureError"), None)
    for fault, rid in (("sluice_opens", "PSW_sluice_shut_holds_all"), ("no_warning", "PSW_flood_warned_before_under"),
                       ("ladder_ignored", "PSW_ladder_prison_door"), ("slope_traps", "PSW_climb_slope_never_traps"),
                       ("bed_ignored", "PSW_room_prison_only_with_bed"), ("jump_refused", "PSW_jump_into_pit"),
                       ("no_exposure", "PSW_child_pit_exposure"), ("no_walls", "PSW_child_wall_art")):
        rc, st, _, _ = mock_run(tmp, fault)
        check("fault %s -> %s" % (fault, rid), st.get(rid), "FAIL")
        check("fault %s exit" % fault, rc, 1)
        check("fault %s only its row" % fault, sorted(k for k, v in st.items() if v != "PASS"), [rid])
    rc2 = W.main(["--mock", "--out-dir", os.path.join(tmp, "only9"), "--only", "S9"])
    with open(os.path.join(tmp, "only9", "result.json"), encoding="utf-8") as f:
        st9 = {r["id"] for r in json.load(f)["rows"]}
    check("only S9", sorted(st9), ["PSW_flood_near_brim_exit", "PSW_flood_swims_cannot_climb",
                                   "PSW_flood_warned_before_under"])

if fails:
    print("FAIL %d" % len(fails))
    for f in fails:
        print("  " + f)
    sys.exit(1)
print("OK selftest_pit_superdeep_walk")
