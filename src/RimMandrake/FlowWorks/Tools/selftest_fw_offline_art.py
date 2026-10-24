#!/usr/bin/env python3
"""selftest_fw_offline_art.py -- the owner's art defects as permanent offline checks (fw_offline_checks.py on
fw_compositor renders). Owner 2026-10-24: "Please find ways to test for those defects in your own offline and in-game
testing from now on, so we don't repeat mistakes."

Each check must FAIL on the art he rejected (the shipped code, emulated as BEFORE) and PASS on the fix (AFTER):
  pipe joins, every look (PIPE_JOINS_REDRAW_RISER_ELBOW_AND_COLLAR):
    collar_on_riser, end_cap_on_riser, riser_kinks   FAIL before, PASS after
    riser_gaps                                       PASS both; can-fail: the scene with its riser strips removed
    riser_rims_north                                 PASS after; can-fail: the review's west-going rim flip re-created
  parity: the emulation's constants are the C#'s (LiquidJoinRule ElbowRadius/BoreHalf/UnderNozzle, TankPortGeometry PortDz).
  sprinkler head, every look x nine stations (SPRINKLER_SEAT_FIX_HEAD_BESIDE_ELBOW):
    head_centroid_on_axis, head_squat   FAIL on the tall heads (art_source/Sprinkler/raw at their shipped drawOffsets),
                                        PASS on the installed squat heads at the Defs' drawOffset, at two scales (px 40, 64)
    head_seat_on_pipe                   PASS on the squat heads; can-fail: the elbow seat put back at the cell centre
  parity: fw_scenes_sprinkler.seat == RM_PipeSeatMath.Seat for all 16 masks x every look (k, r and the stub read from the
          C# source via selftest_pipe_seat's parser); the installed head PNGs == squat_heads.squat(raw) pixel for pixel,
          and every RM_SprinklerHead drawOffset z (the four styles and the base ThingDef) == (SEAT_Y - 128) / 256 to 3 dp
          -- together: the art's seat row lands on the pipe axis.
"""
# selftest-timeout: 400
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fw_compositor as fc  # noqa: E402
import fw_offline_checks as ck  # noqa: E402
import fw_scenes_pipejoins as sp  # noqa: E402
import fw_scenes_sprinkler as ss  # noqa: E402
import selftest_pipe_seat as ps  # noqa: E402
sys.path.insert(0, str(HERE.parent / "art_source" / "Sprinkler"))
import squat_heads  # noqa: E402

PX = 40
fails = []


def want(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


def parity():
    rule = (fc.FW / "Source/Machinery/LiquidJoinRule.cs").read_text()
    for name, py in (("ElbowRadius", sp.ELBOW_R), ("BoreHalf", sp.BORE_HALF), ("UnderNozzle", sp.UNDER_NOZZLE)):
        m = re.search(r"const double %s = ([-\d.]+);" % name, rule)
        want(m is not None and abs(float(m.group(1)) - py) < 1e-9, "parity: %s C# %s == python %s" % (name, m and m.group(1), py))
    hm = (fc.FW / "Source/Hose/HoseMath.cs").read_text()
    looks = re.search(r"string\[\] Looks = \{([^}]*)\}", hm)
    dz = re.search(r"double\[\] PortDz = \{([^}]*)\}", hm)
    if looks and dz:
        table = dict(zip(re.findall(r'"(\w+)"', looks.group(1)), [float(v) for v in dz.group(1).split(",")]))
        want(table == fc.TANK_PORT_DZ, "parity: TANK_PORT_DZ is TankPortGeometry.PortDz %s" % table)
    else:
        want(False, "parity: TankPortGeometry Looks/PortDz not found in HoseMath.cs")


def pipe_joins():
    for look in fc.LOOKS:
        before, after = sp.look_scene(look, "before", PX), sp.look_scene(look, "after", PX)
        for f in (ck.collar_on_riser, ck.end_cap_on_riser, ck.riser_kinks):
            okb, db = f(before)
            oka, da = f(after)
            want(not okb, "%s %s FAILS on the shipped joins (%s)" % (look, f.__name__, db))
            want(oka, "%s %s passes on the fix (%s)" % (look, f.__name__, da))
        ok, d = ck.riser_gaps(after)
        want(ok, "%s riser_gaps passes on the fix (%s)" % (look, d))
        holed = sp.look_scene(look, "after", PX)
        holed.draws = [dr for dr in holed.draws if not (dr[3] and dr[3].get("kind") == "strip")]
        ok, d = ck.riser_gaps(holed)
        want(not ok, "%s can-fail: riser_gaps sees a riser with its strip missing (%s)" % (look, d))
        ok, d = ck.riser_rims_north(after)
        want(ok, "%s riser_rims_north passes on the fix (%s)" % (look, d))
        ok, d = ck.riser_rims_north(sp.look_scene(look, "after", PX, flip_bug=True))
        want(not ok, "%s can-fail: riser_rims_north sees the west-going flip (%s)" % (look, d))


def sprinkler_parity():
    src = (fc.FW / "Source/Sprinklers/RM_PipeSeatMath.cs").read_text()
    for name, py in (("LoneStubScrapperPx", ss.LONE_STUB_SCRAPPER_PX), ("ShownCellPx", ss.SHOWN_CELL_PX)):
        m = re.search(r"const float %s = ([-\d.]+)f;" % name, src)
        want(m is not None and abs(float(m.group(1)) - py) < 1e-9, "parity: %s C# %s == python %s" % (name, m and m.group(1), py))
    arcs = ps.arcs_from_source()
    bad = [(look, mask) for look in fc.LOOKS + ("NoSuchLook",) for mask in range(16)
           if max(abs(a - b) for a, b in zip(ss.seat(mask, look), ps.seat(mask, look, arcs))) > 1e-6]
    want(not bad, "parity: fw_scenes_sprinkler.seat == RM_PipeSeatMath.Seat, 16 masks x 5 looks (mismatch %s)" % bad)
    want(abs(ss.elbow_arc("Scrapper")[0] - arcs["Scrapper"][0]) < 1e-9, "parity: elbow_arc reads as ElbowArc")
    import numpy as np
    from PIL import Image
    for look in fc.LOOKS:
        made, _ = squat_heads.squat(Image.open(ss.RAW / look / "RM_SprinklerHead.png").convert("RGBA"))
        shipped = Image.open(fc.FW / "Textures/RimMandrake/FlowWorks/Sprinkler" / look / "RM_SprinklerHead.png").convert("RGBA")
        same = made.size == shipped.size and np.array_equal(np.asarray(made), np.asarray(shipped))
        want(same, "parity: installed %s head == squat_heads.squat(raw/%s) pixel for pixel" % (look, look))
    try:
        oz = ss.def_offsets(base=True)
    except ValueError as e:
        want(False, "parity: sprinkler head drawOffsets readable (%s)" % e)
        return
    need = round((squat_heads.SEAT_Y - 128) / 256, 3)
    want(all(abs(v - need) < 1e-9 for v in oz.values()),
         "parity: RM_SprinklerHead (+ each style) drawOffset z %s == (SEAT_Y %d - 128)/256 = %s" % (oz, squat_heads.SEAT_Y, need))


def sprinkler():
    for px in (PX, 64):
        for look in fc.LOOKS:
            before, after = ss.board(look, "before", px), ss.board(look, "after", px)
            for f in (ck.head_centroid_on_axis, ck.head_squat):
                okb, db = f(before)
                oka, da = f(after)
                want(not okb, "px%d %s %s FAILS on the tall head (%s)" % (px, look, f.__name__, db))
                want(oka, "px%d %s %s passes on the squat head (%s)" % (px, look, f.__name__, da))
    for look in fc.LOOKS:
        ok, d = ck.head_seat_on_pipe(ss.board(look, "after", PX))
        want(ok, "%s head_seat_on_pipe passes (%s)" % (look, d))
    real = ss.seat
    try:
        ss.seat = lambda mask, look: (0.0, 0.0)          # the cell-centre seat SPRINKLER_HEAD_FIX_FLOATS_OFF_CURVE fixed
        for look in fc.LOOKS:
            ok, d = ck.head_seat_on_pipe(ss.board(look, "after", PX))
            want(not ok, "%s can-fail: head_seat_on_pipe sees a cell-centre seat on the elbows (%s)" % (look, d))
    finally:
        ss.seat = real


if __name__ == "__main__":
    parity()
    pipe_joins()
    sprinkler_parity()
    sprinkler()
    print("%d FAIL" % len(fails) if fails else "ALL OK")
    sys.exit(1 if fails else 0)
