#!/usr/bin/env python3
"""selftest_fw_offline_art.py -- the owner's art defects as permanent offline checks (fw_offline_checks.py on
fw_compositor renders). Owner 2026-10-24: "Please find ways to test for those defects in your own offline and in-game
testing from now on, so we don't repeat mistakes."

Each check must FAIL on the art he rejected (the shipped code, emulated as BEFORE) and PASS on the fix (AFTER):
  pipe joins, every look (PIPE_JOINS_REDRAW_RISER_ELBOW_AND_COLLAR):
    collar_on_riser, end_cap_on_riser, riser_kinks   FAIL before, PASS after
    riser_gaps                                       PASS both; can-fail: the scene with its riser strips removed
    all five riser checks                            can-fail: a scene with no risers (never pass vacuously)
    riser_rims_north                                 PASS after; can-fail: the review's west-going rim flip re-created
  parity: the emulation's constants are the C#'s (LiquidJoinRule ElbowRadius/BoreHalf/UnderNozzle, TankPortGeometry PortDz).
  sprinkler head, every look x nine stations (SPRINKLER_SEAT_FIX_HEAD_BESIDE_ELBOW):
    head_centroid_on_axis, head_squat   FAIL on the tall heads (art_source/Sprinkler/raw at their shipped drawOffsets),
                                        PASS on the installed squat heads at the Defs' drawOffset, at two scales (px 40, 64)
    head_clamp_straddles_pipe           PASS on the squat heads; can-fail: the head shifted 0.1 cell north, south or east
    head_seat_on_pipe                   PASS on the squat heads; can-fail: the elbow seat put back at the cell centre
    centroid, clamp and squat checks can-fail on a blank head, the seat check on a board with no head; every check passes for every head look on every pipe
    look (the seat follows the pipe's look in game)
  parity: fw_scenes_sprinkler.seat == RM_PipeSeatMath.Seat for all 16 masks x every look (k, r and the stub read from the
          C# source via selftest_pipe_seat's parser); the installed head PNGs == squat_heads.shipped(raw) pixel for pixel,
          and every RM_SprinklerHead drawSize == (1,1) and drawOffset z (the four styles and the base ThingDef) == (SEAT_Y - 128) / 256 to 3 dp
          -- together: the art's seat row lands on the pipe axis.
  Modern waterworks blue, every recoloured piece + the Modern head (MODERN_PIPE_REDRAW_FIRETRUCK_RED_RETIRED):
    no saturated red          FAIL on the red originals (ModernStyle/red, the squat red head), PASS installed
    alpha unchanged           installed alpha == the red original's byte for byte: every fit (atlas, joins, seat, ports) holds
    pinned                    installed == waterworks_blue.recolour(red original) pixel for pixel
  portable ladder, north + south from the ground sprite (LADDER_PORTABLE_REDRAW_NORTH_FROM_GROUND):
    ladder_north_not_compressed   FAIL on the shipped north (art_source/Ladder/v6/before), PASS installed; can-fail: the
                                  installed north moved 60 px down or 20 px sideways (shape alone would pass), or squeezed 0.8x across
    ladder_south_footprint        FAIL on the shipped south stub, PASS installed; can-fail: one nub only
    both can-fail on a blank image
    pinned                        installed N/S == portable_from_ground.north()/south() pixel for pixel
  pit spikes, a 4 m pit with a 2 m shelf and a 0..2 m water series (PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE, fw_scenes_spikes):
    spikes_over_wall    FAIL on the shipped whole-cell sprite, PASS on Building_RM_Spikes' layout; also PASS with the
                        outline off; with the faces off it REFUSES (no wall mask), the no-walls can-fail; can-fail: no spikes
    spikes_submerged    FAIL shipped (full strength under 2 m), PASS after; can-fail: a scene with no deep cell, deep
                        cells with no stakes at all, a linear fade over 2 m
    (spikes_over_wall also FAILS when the Python mirror's floor_rect forgets the outline: the mask and the rect share
    tables, so this is the check that a floor_rect drift from the walls is visible; the C# FloorRect is held by
    SpikeDrawChecks, not here)
    parity              the Python layout/hash mirror == SpikeDrawChecks' fixture numbers
    stakes.check()      RM_SpikeStakes.cs, art_source/Spikes/atlas/ and the installed stake atlases are current and every
                        stake box holds one stake; can-fail: boxes cut straight from the shipped sprites (review s2c:
                        neighbours' slivers) and one texel in a box's bilinear ring
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
import fw_scenes_spikes as spk  # noqa: E402
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
        for tag, sc in (("shipped", before), ("fix", after)):
            ok, d = ck.riser_gaps(sc)
            want(ok, "%s riser_gaps passes on the %s (%s)" % (look, tag, d))
        holed = sp.look_scene(look, "after", PX)
        holed.draws = [dr for dr in holed.draws if not (dr[3] and dr[3].get("kind") == "strip")]
        ok, d = ck.riser_gaps(holed)
        want(not ok, "%s can-fail: riser_gaps sees a riser with its strip missing (%s)" % (look, d))
        ok, d = ck.riser_rims_north(after)
        want(ok, "%s riser_rims_north passes on the fix (%s)" % (look, d))
        bare = sp.look_scene(look, "after", PX)
        bare.risers = []
        for f in (ck.collar_on_riser, ck.end_cap_on_riser, ck.riser_kinks, ck.riser_gaps, ck.riser_rims_north):
            ok, d = f(bare)
            want(not ok, "%s can-fail: %s refuses a scene with no risers (%s)" % (look, f.__name__, d))
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
        ss.def_draw_sizes(base=True)
    except ValueError as e:
        want(False, "parity: sprinkler head drawOffsets readable (%s)" % e)
        return
    sizes = ss.def_draw_sizes(base=True)
    want(all(v == (1.0, 1.0) for v in sizes.values()),
         "parity: RM_SprinklerHead (+ each style) drawSize %s == (1,1), which the seat formula below assumes" % sizes)
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
        for f in (ck.head_centroid_on_axis, ck.head_clamp_straddles_pipe, ck.head_squat):
            ok, d = f(ss.board(look, "after", PX, head=blank))
            want(not ok, "%s can-fail: %s refuses a blank head (%s)" % (look, f.__name__, d))
        headless = ss.board(look, "after", PX)
        headless.draws = [dr for dr in headless.draws if not (dr[3] and dr[3].get("kind") == "head")]
        ok, d = ck.head_seat_on_pipe(headless)
        want(not ok and d == "no head drawn", "%s can-fail: head_seat_on_pipe refuses a board with no head (%s)" % (look, d))
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


def ladder():
    import numpy as np
    from PIL import Image
    sys.path.insert(0, str(HERE.parent / "art_source" / "Ladder" / "v6"))
    import portable_from_ground as pg
    up = pg.upright()
    blank = Image.new("RGBA", (pg.CANVAS, pg.CANVAS))
    made = {"north": pg.north(), "south": pg.south()}
    checks = {"north": lambda im: ck.ladder_north_not_compressed(im, up), "south": ck.ladder_south_footprint}
    for f, chk in checks.items():
        name = "RM_LadderPortable_%s.png" % f
        old = Image.open(HERE.parent / "art_source/Ladder/v6/before" / name).convert("RGBA")
        live = Image.open(pg.CANALS / name).convert("RGBA")
        ok, d = chk(old)
        want(not ok, "ladder %s: shipped BEFORE fails (%s)" % (f, d))
        ok, d = chk(live)
        want(ok, "ladder %s: installed passes (%s)" % (f, d))
        want(not chk(blank)[0], "ladder %s can-fail: blank image" % f)
        want(np.array_equal(np.asarray(live), np.asarray(made[f])), "ladder %s: installed == portable_from_ground.%s()" % (f, f))
    moved = Image.new("RGBA", blank.size)
    moved.alpha_composite(made["north"].crop((0, 0, pg.CANVAS, pg.CANVAS - 60)), (0, 60))
    ok, d = ck.ladder_north_not_compressed(moved, up)
    want(not ok, "ladder north can-fail: moved 60 px down off the far rim (%s)" % d)
    narrow = Image.new("RGBA", blank.size)
    nb = made["north"].getchannel("A").getbbox()
    thin = made["north"].crop(nb).resize((round((nb[2] - nb[0]) * 0.8), nb[3] - nb[1]), Image.LANCZOS)
    narrow.alpha_composite(thin, ((pg.CANVAS - thin.width) // 2, nb[1]))
    ok, d = ck.ladder_north_not_compressed(narrow, up)
    want(not ok, "ladder north can-fail: squeezed to 0.8x across (%s)" % d)
    side = Image.new("RGBA", blank.size)
    side.alpha_composite(made["north"].crop(nb), (nb[0] + 20, nb[1]))       # the whole sprite, 20 px east
    ok, d = ck.ladder_north_not_compressed(side, up)
    want(not ok and "centre +20 px" in d, "ladder north can-fail: moved 20 px off the cell centre, centring is what fails (%s)" % d)
    sb = made["south"].getchannel("A").getbbox()
    nub = made["south"].crop((sb[0], sb[1], (sb[0] + sb[2]) // 2, sb[3]))
    nub = nub.crop(nub.getchannel("A").getbbox())
    one = Image.new("RGBA", blank.size)
    one.alpha_composite(nub, ((pg.CANVAS - nub.width) // 2, sb[3] - nub.height))   # one nub, centred, on the rim
    ok, d = ck.ladder_south_footprint(one)
    want(not ok and d.startswith("1 nubs"), "ladder south can-fail: one centred nub, the nub count is what fails (%s)" % d)


def spikes():
    import numpy as np
    from PIL import Image
    before = spk.render(spk.check_pit(), "before", P=PX)
    after = spk.render(spk.check_pit(), "after", P=PX)
    for name, check in (("spikes_over_wall", spk.spikes_over_wall), ("spikes_submerged", spk.spikes_submerged)):
        ok, d = check(before)
        want(not ok, "%s FAILS on the shipped sprite (%s)" % (name, d))
        ok, d = check(after)
        want(ok, "%s passes after (%s)" % (name, d))
    for faces, outline in ((True, False), (False, False)):
        ok, d = spk.spikes_over_wall(spk.render(spk.check_pit(), "after", P=PX, faces=faces, outline=outline))
        # faces off: the walls layer draws nothing, so no mask; the check must refuse rather than pass vacuously
        want(ok if faces else (not ok and "no wall" in d), "spikes_over_wall faces=%s outline=%s (%s)" % (faces, outline, d))
    flat = spk.Pit([[0, 0, 0], [0, 8, 0], [0, 0, 0]], spikes=[])
    ok, d = spk.spikes_over_wall(spk.render(flat, "after", P=PX))
    want(not ok and d == "no spikes in the scene", "spikes_over_wall can-fail: no spikes (%s)" % d)
    dry = spk.Pit([[0, 0, 0], [0, 8, 0], [0, 0, 0]], [[0] * 3, [0, 1, 0], [0] * 3], spikes=[(1, 1)])
    ok, d = spk.spikes_submerged(spk.render(dry, "after", P=PX))
    want(not ok and "needs" in d, "spikes_submerged can-fail: no dry or deep cell (%s)" % d)
    # can-fail, a floor rect that drifts from the walls: ignore the outline while the scene draws it
    real_rect, real_alpha = spk.floor_rect, spk.submerged_alpha
    try:
        spk.floor_rect = lambda d, n, s, w, e, faces=True, outline=True: real_rect(d, n, s, w, e, faces, False)
        ok, d = spk.spikes_over_wall(spk.render(spk.check_pit(), "after", P=PX))
        want(not ok, "spikes_over_wall can-fail: a floor rect that forgets the outline (%s)" % d)
        spk.floor_rect = lambda d, n, s, w, e, faces=True, outline=True: (0.3, 0.3, 0.3, 0.3)
        ok, d = spk.spikes_submerged(spk.render(spk.check_pit(), "after", P=PX))
        want(not ok and "nothing to submerge" in d, "spikes_submerged can-fail: deep cells with no stakes at all (%s)" % d)
        spk.floor_rect = real_rect
        spk.submerged_alpha = lambda f: max(0.0, 1 - f * 0.25)   # a linear fade over 2 m: still half drawn at 1 m
        ok, d = spk.spikes_submerged(spk.render(spk.check_pit(), "after", P=PX))
        want(not ok and "still drawn under 1.0 m" in d, "spikes_submerged can-fail: a fade too slow (%s)" % d)
    finally:
        spk.floor_rect, spk.submerged_alpha = real_rect, real_alpha
    hashes, (n, first, last) = spk.parity()
    want(hashes == [0, 2836592880, 1249282371], "spikes parity: hash fixture %s" % hashes)
    fx = ((0.343608, 0.317331, 0.046875, 0.152344, 0.375000, 0.632812, 0.421875, 0.937500),
          (0.890793, 0.075, 0.050781, 0.164062, 0.281250, 0.609375, 0.332031, 0.937500))
    want(n == 26 and all(abs(a - b) < 1e-4 for q, f in zip((first, last), fx) for a, b in zip(q, f)),
         "spikes parity: layout fixture (26 stakes, first/last quad) == SpikeDrawChecks")
    st = spk.STAKES
    bad = st.check()
    want(not bad, "stakes.py --check: .cs, atlas sources and installed atlases current, every box one stake (%s)" % bad)
    # can-fail, the review s2c defect: stakes cut as padded bboxes straight out of the shipped sprite hold neighbours' pixels
    dirty = 0
    for v in st.VARIANTS:
        a = np.asarray(Image.open(st.TEX / ("RM_Spikes_%s.png" % v)).convert("RGBA"))[..., 3]
        S = a.shape[0]
        uvs = [(x0 / S, 1 - (y1 + 1) / S, (x1 + 1) / S, 1 - y0 / S) for x0, y0, x1, y1, _, _ in st._cut(v)[0]]
        dirty += st.dirty_boxes(a, uvs)
    want(dirty > 0, "dirty_boxes can-fail: boxes cut from the shipped sprites hold foreign stakes (%d)" % dirty)
    img, lib, _ = st.atlas("b")
    smear = img.copy()
    x1 = int(round(lib[0][4] * img.shape[1]))
    smear[int(round((1 - lib[0][5]) * img.shape[0])) + 2, x1, 3] = 200      # one opaque texel in stake 0's bilinear ring
    want(st.dirty_boxes(smear[..., 3], [q[2:] for q in lib]) == 1, "dirty_boxes can-fail: a texel in the bilinear ring")


if __name__ == "__main__":
    parity()
    pipe_joins()
    sprinkler_parity()
    sprinkler()
    modern_blue()
    ladder()
    spikes()
    print("%d FAIL" % len(fails) if fails else "ALL OK")
    sys.exit(1 if fails else 0)
