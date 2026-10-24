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
    head_clamp_straddles_pipe           PASS on the squat heads; can-fail: the head shifted 0.1 cell north, south or east
    head_seat_on_pipe                   PASS on the squat heads; can-fail: the elbow seat put back at the cell centre
    both centroid and clamp checks can-fail on a blank head; every check passes for every head look on every pipe
    look (the seat follows the pipe's look in game)
  parity: fw_scenes_sprinkler.seat == RM_PipeSeatMath.Seat for all 16 masks x every look (k, r and the stub read from the
          C# source via selftest_pipe_seat's parser); the installed head PNGs == squat_heads.shipped(raw) pixel for pixel,
          and every RM_SprinklerHead drawOffset z (the four styles and the base ThingDef) == (SEAT_Y - 128) / 256 to 3 dp
          -- together: the art's seat row lands on the pipe axis.
  Modern waterworks blue, every recoloured piece + the Modern head (MODERN_PIPE_REDRAW_FIRETRUCK_RED_RETIRED):
    no saturated red          FAIL on the red originals (ModernStyle/red, the squat red head), PASS installed
    alpha unchanged           installed alpha == the red original's byte for byte: every fit (atlas, joins, seat, ports) holds
    pinned                    installed == waterworks_blue.recolour(red original) pixel for pixel
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
import waterworks_blue as wb  # noqa: E402  (squat_heads put art_source/ModernStyle on the path)

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
        made, _ = squat_heads.shipped(look, Image.open(ss.RAW / look / "RM_SprinklerHead.png").convert("RGBA"))
        shipped = Image.open(fc.FW / "Textures/RimMandrake/FlowWorks/Sprinkler" / look / "RM_SprinklerHead.png").convert("RGBA")
        same = made.size == shipped.size and np.array_equal(np.asarray(made), np.asarray(shipped))
        want(same, "parity: installed %s head == squat_heads.shipped(raw/%s) pixel for pixel" % (look, look))
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
    from PIL import Image
    blank = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    for look in fc.LOOKS:
        oz = ss.def_offsets()[look]
        for pl in fc.LOOKS:
            sc = ss.board(look, "after", PX, pipe_look=pl)
            for f in (ck.head_centroid_on_axis, ck.head_clamp_straddles_pipe, ck.head_seat_on_pipe):
                ok, d = f(sc)
                want(ok, "%s head on %s pipe: %s passes (%s)" % (look, pl, f.__name__, d))
        for what, kw in (("north 0.1", {"offset_z": oz + 0.1}), ("south 0.1", {"offset_z": oz - 0.1}),
                         ("east 0.1", {"shift_x": 0.1})):
            ok, d = ck.head_clamp_straddles_pipe(ss.board(look, "after", PX, **kw))
            want(not ok, "%s can-fail: head_clamp_straddles_pipe sees the head shifted %s (%s)" % (look, what, d))
        for f in (ck.head_centroid_on_axis, ck.head_clamp_straddles_pipe):
            ok, d = f(ss.board(look, "after", PX, head=blank))
            want(not ok, "%s can-fail: %s refuses a blank head (%s)" % (look, f.__name__, d))
    real = ss.seat
    try:
        ss.seat = lambda mask, look: (0.0, 0.0)          # the cell-centre seat SPRINKLER_HEAD_FIX_FLOATS_OFF_CURVE fixed
        for look in fc.LOOKS:
            ok, d = ck.head_seat_on_pipe(ss.board(look, "after", PX))
            want(not ok, "%s can-fail: head_seat_on_pipe sees a cell-centre seat on the elbows (%s)" % (look, d))
    finally:
        ss.seat = real


def modern_blue():
    import numpy as np
    from PIL import Image
    red_head, _ = squat_heads.squat(Image.open(ss.RAW / "Modern" / "RM_SprinklerHead.png").convert("RGBA"))
    pairs = [(rel, Image.open(wb.RED / rel).convert("RGBA"), wb.TEX / rel) for rel in wb.PIECES]
    pairs.append((wb.SPRINKLER, red_head, wb.TEX / wb.SPRINKLER))
    for rel, red, path in pairs:
        live = Image.open(path).convert("RGBA")
        before, after = wb.saturated_red_share(red), wb.saturated_red_share(live)
        want(before > 0.3, "modern blue: %s red original is saturated red (%.3f > 0.3): the check can fail" % (rel, before))
        want(after < 0.002, "modern blue: %s installed has no saturated red (%.4f < 0.002)" % (rel, after))
        a, b = np.asarray(red), np.asarray(live)
        want(a.shape == b.shape and np.array_equal(a[..., 3], b[..., 3]),
             "modern blue: %s alpha == red original's byte for byte (fits unchanged)" % rel)
        made, _ = wb.recolour(red, rel)
        want(np.array_equal(np.asarray(made), b), "modern blue: %s installed == recolour(red original)" % rel)


if __name__ == "__main__":
    parity()
    pipe_joins()
    sprinkler_parity()
    sprinkler()
    modern_blue()
    print("%d FAIL" % len(fails) if fails else "ALL OK")
    sys.exit(1 if fails else 0)
