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
  sprinkler head, every look x nine stations (SPRINKLER_SEAT_FIX_HEAD_BESIDE_ELBOW, then
  SPRINKLER_HEAD_REDRAW_SEEN_FROM_ABOVE: "shown as viewed from above ... Like the pump is viewed"):
    head_centroid_on_axis, head_squat   FAIL on the tall heads (art_source/Sprinkler/raw at their shipped drawOffsets),
                                        PASS on the installed top-down heads, at two scales (px 40, 64)
    head_top_down                       FAIL on the squat side-view heads that shipped before, PASS installed; can-fail:
                                        the head shifted 0.05 cell north or east, a blank head
    head_seat_on_pipe                   PASS installed; can-fail: the elbow seat put back at the cell centre
    head_seat_on_centreline             PASS installed; can-fail: the cell-centre elbow seat, every seat 0.05 cell east
    centroid, top-down and squat checks can-fail on a blank head, the seat checks on a board with no head; every check passes
    for every head look on every pipe look (the seat follows the pipe's look in game)
  parity: fw_scenes_sprinkler.seat == RM_PipeSeatMath.Seat for all 16 masks x every look (k, r and the stub read from the
          C# source via selftest_pipe_seat's parser); the installed head PNGs == top_heads.head(look) pixel for pixel,
          and every RM_SprinklerHead drawSize == (1,1) and drawOffset z (the four styles and the base ThingDef) == 0
          -- together: the centred head lands on the seat.
  Modern waterworks blue, every recoloured piece + the Modern head (MODERN_PIPE_REDRAW_FIRETRUCK_RED_RETIRED):
    no saturated red          FAIL on the red originals (ModernStyle/red), PASS installed (and on the top-down Modern head)
    alpha unchanged           installed alpha == the red original's byte for byte: every fit (atlas, joins, seat, ports) holds
    pinned                    installed == waterworks_blue.recolour(red original) pixel for pixel (the reels: see below)
  Modern hose reel, the drum's hose a red canvas firehose (HOSE_REEL_REDRAW_FIREHOSE_ON_THE_DRUM), the six reel textures:
    no saturated red          as above, but outside firehose_reel.region only (the drum hose is red on purpose)
    frame unchanged           outside the region installed == waterworks_blue.recolour(red original) pixel for pixel
    drum_hose_reads_as_firehose   FAIL on the all-blue recolour and on the glossy red original, PASS installed
    pinned                    installed == firehose_reel.build(name) pixel for pixel
  portable ladder, north + south from the ground sprite (LADDER_PORTABLE_REDRAW_NORTH_FROM_GROUND):
    ladder_north_not_compressed   FAIL on the shipped north (art_source/Ladder/v6/before), PASS installed; can-fail: the
                                  installed north moved 60 px down or 20 px sideways (shape alone would pass), or squeezed 0.8x across
    ladder_south_footprint        FAIL on the shipped south stub, PASS installed; can-fail: one nub only
    both can-fail on a blank image
    pinned                        installed N/S == portable_from_ground.north()/south() pixel for pixel
  portable ladder east/west, panel 3 = the ground ladder raised 30 deg (LADDER_PORTABLE_DECIDE_EAST_WEST_FACING):
    ladder_east_leans_on_wall     FAIL on the shipped GPT v4 east (v6/before), PASS installed; can-fail: blank, the 55 deg
                                  candidate (tilt), east mirrored (leans away from its wall), squeezed 0.8x along
    ladder_west_mirrors_east      PASS installed; can-fail: the shipped v4 west against the installed east, east as west
    pinned                        installed E/W == portable_from_ground east_a / west_a pixel for pixel
  wooden rail ladder RM_Ladder / RM_LadderRaised in the ground ladder's pale wood (RAIL_LADDER_REDRAW_FAT_RUNG_FENCE):
    ladder_wood_matches_ground    PASS on the 7 installed facings that show timber (the lowered south is iron hooks only:
                                  it REFUSES, no wood); FAIL on the deprecated yellow v5 wood (art_source/Ladder/v5/out);
                                  refuses the steel set (no wood)
    geometry kept                 installed alpha == v5 draw.py's WOOD alpha, every facing (approved perspectives untouched)
    iron kept                     every pixel that is neither timber nor outline == v5's RGBA (hooks, brackets, bolts)
    pinned                        installed == art_source/Ladder/v7/rail_pale.build() pixel for pixel; west == east mirrored
  pit spikes, a 4 m pit with a 2 m shelf and a 0..2 m water series (PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE, fw_scenes_spikes):
    spikes_over_wall    FAIL on the shipped whole-cell sprite, PASS on Building_RM_Spikes' layout; also PASS with the
                        outline off; with the faces off it REFUSES (no wall mask), the no-walls can-fail; can-fail: no spikes
    spikes_submerged    FAIL shipped (full strength under 2 m), PASS after; can-fail: a scene with no deep cell, deep
                        cells with no stakes at all, a linear fade over 2 m
    (spikes_over_wall also FAILS when the Python mirror's floor_rect forgets the outline: the mask and the rect share
    tables, so this is the check that a floor_rect drift from the walls is visible; the C# FloorRect is held by
    SpikeDrawChecks, not here)
    parity              the Python layout/hash mirror == SpikeDrawChecks' fixture numbers
    approved kept       owner on 4f12810a3e: "spikes look great!" -- per variant the stakes' (w, h) and pitch == the pinned
                        approved library; every atlas box == its approved sprite window with only the slivers' alpha cleared;
                        the approved UV boxes == the windows cut now, the shipped sprites == their pinned sha256; on
                        compare_pit (every stake drawn) the AFTER render == the approved render with the slivers' alpha
                        cleared, exactly, and that differs from the approved render only inside the slivers
                        (fw_scenes_spikes.same_as_approved); can-fail: the sliver pixels themselves, one stake pixel beside
                        a sliver recoloured, a 10% wider pitch, a scene that skips a stake
    stakes.check()      RM_SpikeStakes.cs, art_source/Spikes/atlas/ and the installed stake atlases are current and every
                        stake box holds one stake at every mip up to MIP_CHECK; can-fail: the approved boxes sampled straight
                        from the shipped sprites (review s2c: neighbours' slivers), one texel in a box's bilinear ring, cells
                        too small for the lower mips (review s3)
  concealed pit cover, the owner's shot = one lid on a 3x3 pit's centre (PLANK_COVER_REDRAW_READS_AS_EMPTY_PIT, fw_scenes_covers):
    cover_reads_as_material   FAIL on the shipped ground print, PASS on the tier texture drawn (planks), laid on ground,
                              cropped edge to edge (planks_full), every tier, every scene; can-fail: the texture dusted to
                              15% alpha, a cell with no cover
    deck_matches_ground       PASS on the shipped print of a deck over the whole pit (why it was ruled: pit_covered_invisible),
                              FAIL on the drawn lattice (the trade the owner is shown)
  Modern bottle and bucket (MODERN_BOTTLE_REDRAW_SODA_AND_ORANGE_PAIL: "Modern bottle should look soda-like. Modern bucket
  should be orange."), art_source/LiquidContainers/modern_soda_pail.py on the v1 pilot sprites:
    bottle_reads_as_soda      FAIL on the pilot's swirl label, PASS installed; can-fail: the label greyed out
    pail_is_orange            FAIL on the blue pilot pail, PASS installed; can-fail: the installed pail hue-turned to blue
    liquid + trim untouched   installed == the pilot on every liquid (mask R) and trim (mask G) pixel, alpha and the
                              CutoutComplex masks byte for byte (the tinting works as before)
    pinned                    installed == modern_soda_pail.build pixel for pixel
"""
# selftest-timeout: 400
import hashlib
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
import fw_scenes_covers as cov  # noqa: E402
import selftest_pipe_seat as ps  # noqa: E402
sys.path.insert(0, str(HERE.parent / "art_source" / "Sprinkler"))
import top_heads  # noqa: E402
import squat_heads  # noqa: E402,F401  (puts art_source/ModernStyle on the path; fw_scenes_sprinkler's "squat" mode uses it)
import waterworks_blue as wb  # noqa: E402
import firehose_reel as fr  # noqa: E402
sys.path.insert(0, str(HERE.parent / "art_source" / "LiquidContainers"))
import modern_soda_pail as msp  # noqa: E402

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
        made = top_heads.head(look)
        shipped = Image.open(fc.FW / "Textures/RimMandrake/FlowWorks/Sprinkler" / look / "RM_SprinklerHead.png").convert("RGBA")
        same = made.size == shipped.size and np.array_equal(np.asarray(made), np.asarray(shipped))
        want(same, "parity: installed %s head == top_heads.head(%s) pixel for pixel" % (look, look))
    try:
        oz = ss.def_offsets(base=True)
        ss.def_draw_sizes(base=True)
    except ValueError as e:
        want(False, "parity: sprinkler head drawOffsets readable (%s)" % e)
        return
    sizes = ss.def_draw_sizes(base=True)
    want(all(v == (1.0, 1.0) for v in sizes.values()),
         "parity: RM_SprinklerHead (+ each style) drawSize %s == (1,1), which the seat formula below assumes" % sizes)
    want(all(abs(v) < 1e-9 for v in oz.values()),
         "parity: RM_SprinklerHead (+ each style) drawOffset z %s == 0 (the top-down head is drawn centred)" % oz)


def sprinkler():
    for px in (PX, 64):
        for look in fc.LOOKS:
            before, after = ss.board(look, "before", px), ss.board(look, "after", px)
            for f in (ck.head_centroid_on_axis, ck.head_squat):
                okb, db = f(before)
                oka, da = f(after)
                want(not okb, "px%d %s %s FAILS on the tall head (%s)" % (px, look, f.__name__, db))
                want(oka, "px%d %s %s passes on the top-down head (%s)" % (px, look, f.__name__, da))
            ok, d = ck.head_top_down(ss.board(look, "squat", px))
            want(not ok, "px%d %s head_top_down FAILS on the squat side-view head (%s)" % (px, look, d))
            ok, d = ck.head_top_down(after)
            want(ok, "px%d %s head_top_down passes on the top-down head (%s)" % (px, look, d))
    from PIL import Image
    blank = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    for look in fc.LOOKS:
        for pl in fc.LOOKS:
            sc = ss.board(look, "after", PX, pipe_look=pl)
            for f in ck.SPRINKLER_CHECKS:
                ok, d = f(sc)
                want(ok, "%s head on %s pipe: %s passes (%s)" % (look, pl, f.__name__, d))
        for what, kw in (("north 0.05", {"offset_z": 0.05}), ("east 0.05", {"shift_x": 0.05})):
            ok, d = ck.head_top_down(ss.board(look, "after", PX, **kw))
            want(not ok, "%s can-fail: head_top_down sees the head shifted %s (%s)" % (look, what, d))
        for f in (ck.head_centroid_on_axis, ck.head_top_down, ck.head_squat):
            ok, d = f(ss.board(look, "after", PX, head=blank))
            want(not ok, "%s can-fail: %s refuses a blank head (%s)" % (look, f.__name__, d))
        headless = ss.board(look, "after", PX)
        headless.draws = [dr for dr in headless.draws if not (dr[3] and dr[3].get("kind") == "head")]
        for f in (ck.head_seat_on_pipe, ck.head_seat_on_centreline):
            ok, d = f(headless)
            want(not ok and d == "no head drawn", "%s can-fail: %s refuses a board with no head (%s)" % (look, f.__name__, d))
    real = ss.seat
    try:
        ss.seat = lambda mask, look: (0.0, 0.0)          # the cell-centre seat SPRINKLER_HEAD_FIX_FLOATS_OFF_CURVE fixed
        for look in fc.LOOKS:
            sc = ss.board(look, "after", PX)
            for f in (ck.head_seat_on_pipe, ck.head_seat_on_centreline):
                ok, d = f(sc)
                want(not ok, "%s can-fail: %s sees a cell-centre seat on the elbows (%s)" % (look, f.__name__, d))
        ss.seat = lambda mask, look: (real(mask, look)[0] + 0.05, real(mask, look)[1])
        for look in fc.LOOKS:
            ok, d = ck.head_seat_on_centreline(ss.board(look, "after", PX))
            want(not ok, "%s can-fail: head_seat_on_centreline sees every seat 0.05 cell east (%s)" % (look, d))
    finally:
        ss.seat = real


def modern_blue():
    import numpy as np
    from PIL import Image
    pairs = [(rel, Image.open(wb.RED / rel).convert("RGBA"), wb.TEX / rel) for rel in wb.PIECES]
    head = wb.saturated_red_share(Image.open(wb.TEX / wb.SPRINKLER).convert("RGBA"))
    want(head < 0.002, "modern blue: %s installed (top-down, cut from the Modern pump) has no saturated red (%.4f < 0.002)"
         % (wb.SPRINKLER, head))
    reels = {fr.REL % n: n for n in fr.MASKS}
    for rel, red, path in pairs:
        live = Image.open(path).convert("RGBA")
        a, b = np.asarray(red), np.asarray(live)
        made, _ = wb.recolour(red, rel)
        name = reels.get(rel)
        if name:   # the reel: blue frame, red firehose on the drum
            keep = ~fr.region(name, b.shape[:2])
            sub = Image.fromarray(np.where(keep[..., None], b, 0).astype(np.uint8), "RGBA")
            before, after = wb.saturated_red_share(red), wb.saturated_red_share(sub)
            want(np.array_equal(np.asarray(made)[keep], b[keep]),
                 "modern reel: %s outside the drum hose == recolour(red original) (frame unchanged)" % rel)
            for lab, im, exp in (("all-blue recolour", made, False), ("glossy red original", red, False), ("installed", live, True)):
                ok, canvas, weave, gloss = fr.drum_hose_reads_as_firehose(im, name)
                want(ok == exp, "modern reel: %s drum_hose_reads_as_firehose %s on the %s (canvas %.2f weave %.3f gloss %.3f)"
                     % (rel, "PASS" if exp else "FAIL", lab, canvas, weave, gloss))
            want(np.array_equal(np.asarray(fr.build(name)), b), "modern reel: %s installed == firehose_reel.build" % rel)
        else:
            before, after = wb.saturated_red_share(red), wb.saturated_red_share(live)
            want(np.array_equal(np.asarray(made), b), "modern blue: %s installed == recolour(red original)" % rel)
        want(before > 0.3, "modern blue: %s red original is saturated red (%.3f > 0.3): the check can fail" % (rel, before))
        want(after < 0.002, "modern blue: %s installed has no saturated red%s (%.4f < 0.002)"
             % (rel, " outside the drum hose" if name else "", after))
        want(a.shape == b.shape and np.array_equal(a[..., 3], b[..., 3]),
             "modern blue: %s alpha == red original's byte for byte (fits unchanged)" % rel)


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
    # east/west (LADDER_PORTABLE_DECIDE_EAST_WEST_FACING): panel 3, the ground ladder raised 30 deg; west mirrors east
    flat = pg.flat()
    east = Image.open(pg.CANALS / "RM_LadderPortable_east.png").convert("RGBA")
    west = Image.open(pg.CANALS / "RM_LadderPortable_west.png").convert("RGBA")
    old_e = Image.open(HERE.parent / "art_source/Ladder/v6/before/RM_LadderPortable_east.png").convert("RGBA")
    old_w = Image.open(HERE.parent / "art_source/Ladder/v6/before/RM_LadderPortable_west.png").convert("RGBA")
    ok, d = ck.ladder_east_leans_on_wall(east, flat)
    want(ok, "ladder east: installed leans on its wall (%s)" % d)
    ok, d = ck.ladder_east_leans_on_wall(old_e, flat)
    want(not ok, "ladder east: shipped v4 BEFORE fails (%s)" % d)
    want(not ck.ladder_east_leans_on_wall(blank, flat)[0], "ladder east can-fail: blank image")
    ok, d = ck.ladder_east_leans_on_wall(pg.east(pg.TILTS["b"]), flat)
    want(not ok and "tilt +5" in d, "ladder east can-fail: the 55 deg candidate, the tilt is what fails (%s)" % d)
    ok, d = ck.ladder_east_leans_on_wall(east.transpose(Image.FLIP_LEFT_RIGHT), flat)
    want(not ok and "tilt -" in d, "ladder east can-fail: mirrored, leaning away from its wall (%s)" % d)
    eb = east.getchannel("A").getbbox()
    short = Image.new("RGBA", blank.size)
    sq = east.crop(eb).resize((round((eb[2] - eb[0]) * 0.8), round((eb[3] - eb[1]) * 0.8)), Image.LANCZOS)
    short.alpha_composite(sq, (eb[2] - sq.width, eb[1]))                   # same wall end, 0.8x along and across
    ok, d = ck.ladder_east_leans_on_wall(short, flat)
    want(not ok, "ladder east can-fail: squeezed 0.8x (%s)" % d)
    ok, d = ck.ladder_west_mirrors_east(west, east)
    want(ok, "ladder west: installed mirrors east (%s)" % d)
    want(not ck.ladder_west_mirrors_east(old_w, east)[0], "ladder west can-fail: shipped v4 west vs installed east")
    want(not ck.ladder_west_mirrors_east(east, east)[0], "ladder west can-fail: east used as west unflipped")
    e_made = pg.east(pg.TILTS[pg.PICK])
    for f, live, m in (("east", east, e_made), ("west", west, e_made.transpose(Image.FLIP_LEFT_RIGHT))):
        want(np.array_equal(np.asarray(live), np.asarray(m)), "ladder %s: installed == portable_from_ground %s_%s" % (f, f, pg.PICK))


def rail_ladder():
    import importlib.util
    import numpy as np
    from PIL import Image
    spec = importlib.util.spec_from_file_location("rail_pale", HERE.parent / "art_source/Ladder/v7/rail_pale.py")
    rp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rp)
    canals = HERE.parent / "Textures/Things/Building/FlowWorks/Canals"
    flat = Image.open(rp.FLAT).convert("RGBA")
    made = rp.build(None)
    for raised, tag in ((False, "RM_Ladder"), (True, "RM_LadderRaised")):
        ref = {"north": rp.v5.rail_north(rp.v5.WOOD, raised), "east": rp.v5.rail_east(rp.v5.WOOD, raised),
               "south": rp.v5.rail_south(rp.v5.WOOD, raised)}
        ref["west"] = ref["east"].transpose(Image.FLIP_LEFT_RIGHT)
        for f in rp.FACINGS:
            name = "%s_%s" % (tag, f)
            live = Image.open(canals / (name + ".png")).convert("RGBA")
            a, r = np.asarray(live), np.asarray(ref[f].convert("RGBA"))
            want(np.array_equal(a, np.asarray(made[name])), "rail ladder %s: installed == rail_pale.build()" % name)
            want(np.array_equal(a[..., 3], r[..., 3]), "rail ladder %s: alpha == v5 WOOD (geometry kept)" % name)
            rf = r.astype(np.float64)
            iron = ~rp.timber_mask(rf) & ~rp.outline_mask(rf) & (r[..., 3] > 0)
            want(np.array_equal(a[iron], r[iron]), "rail ladder %s: iron unchanged (%d px)" % (name, int(iron.sum())))
            tm = rp.timber_mask(rf)
            if tm.any():  # masks come from v5's colours: the pale ramp's darkest shades must not be re-read as outline
                edge = np.round(np.clip(rp._dark_edge(), 0, 255)).astype(np.uint8)
                flat_n = int((a[tm][:, :3] == edge).all(-1).sum())
                want(flat_n <= 0.01 * tm.sum(), "rail ladder %s: timber keeps its shading (%d of %d px flattened to the edge colour)"
                     % (name, flat_n, int(tm.sum())))
            ok, d = ck.ladder_wood_matches_ground(live, flat)
            if name == "RM_Ladder_south":
                want(not ok and d == "no wood pixels", "rail ladder %s: hooks only, refuses (%s)" % (name, d))
                continue
            want(ok, "rail ladder %s: pale ground wood (%s)" % (name, d))
            yellow = HERE.parent / "art_source/Ladder/v5/out" / (name + ".png")
            ok, d = ck.ladder_wood_matches_ground(Image.open(yellow), flat)
            want(not ok, "rail ladder %s can-fail: the deprecated yellow v5 wood (%s)" % (name, d))
        e, w = (np.asarray(Image.open(canals / ("%s_%s.png" % (tag, f))).convert("RGBA")) for f in ("east", "west"))
        want(np.array_equal(w, e[:, ::-1]), "rail ladder %s: west == east mirrored" % tag)
    ok, d = ck.ladder_wood_matches_ground(Image.open(canals / "RM_LadderSteel_east.png"), flat)
    want(not ok and d == "no wood pixels", "rail ladder can-fail: the steel set has no wood (%s)" % d)


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
    fx = ((0.461250, 0.321039, 0.046875, 0.152344, 0.550781, 0.675781, 0.574219, 0.828125),
          (0.803641, 0.075, 0.050781, 0.175781, 0.298828, 0.164062, 0.324219, 0.339844))
    want(n == 24 and all(abs(a - b) < 1e-4 for q, f in zip((first, last), fx) for a, b in zip(q, f)),
         "spikes parity: layout fixture (24 stakes, first/last quad) == SpikeDrawChecks")
    st = spk.STAKES
    # the owner approved the 4f12810a3e render ("spikes look great!"): its selection, sizes and pitch stay, pinned
    for i, v in enumerate(st.VARIANTS):
        (lib, pitch), (alib, apitch) = spk.library(i), spk.approved_library(i)
        want(pitch == apitch and [q[:2] for q in lib] == [q[:2] for q in alib],
             "variant %s: stakes (w, h) and pitch == the approved library (%d vs %d stakes, pitch %s vs %s)"
             % (v, len(lib), len(alib), pitch, apitch))
        img, lib_uv, _ = st.atlas(v)
        H, W = img.shape[:2]
        same = 0
        for (u0, v0, u1, v1), (X0, Y0, X1, Y1, win, foreign) in zip([q[2:] for q in lib_uv], st._cut(v)[0]):
            crop = img[int(round((1 - v1) * H)):int(round((1 - v0) * H)), int(round(u0 * W)):int(round(u1 * W))]
            keep = ~foreign
            same += crop.shape == win.shape and (crop[keep] == win[keep]).all() and not crop[foreign][:, 3].any()
        want(same == len(lib_uv) == len(alib), "variant %s: every atlas box == its approved sprite window, only the"
             " slivers' alpha cleared (%d of %d, approved %d)" % (v, same, len(lib_uv), len(alib)))
        try:
            n_sl = sum(bool(m.any()) for m in spk.approved_foreign(i).values())
            want(n_sl > 0, "variant %s: the approved UV boxes == the windows cut now, in order (%d with slivers)" % (v, n_sl))
        except ValueError as e:
            want(False, "variant %s: the approved UV boxes == the windows cut now (%s)" % (v, e))
    pinned = dict(ln.split()[::-1] for ln in spk.APPROVED_PNG.read_text().split("\n") if ln.strip())
    now = {f: hashlib.sha256((st.TEX / f).read_bytes()).hexdigest() for f in pinned}
    want(len(pinned) == 3 and now == pinned, "the shipped RM_Spikes sprites == the ones the approved render sampled (%s)"
         % sorted(f for f in pinned if now[f] != pinned[f]))
    # the owner's render vs the fix, on a pit that lays out every stake of every variant (check_pit misses one)
    cmp = {m: spk.render(spk.compare_pit(), m, P=PX) for m in ("after", "approved_clean", "approved")}
    ok, d = spk.same_as_approved(cmp["after"], cmp["approved_clean"], cmp["approved"])
    want(ok, "after == the approved render with only the slivers cleared (%s)" % d)
    ok, d = spk.same_as_approved(after, spk.render(spk.check_pit(), "approved_clean", P=PX),
                                 spk.render(spk.check_pit(), "approved", P=PX))
    want(not ok and "every stake" in d, "same_as_approved can-fail: a scene that skips a stake is refused (%s)" % d)
    cut = dict(cmp["approved"], sliver=np.zeros_like(cmp["approved"]["sliver"]))
    cut["sliver"][0, 0] = True
    ok, d = spk.same_as_approved(cmp["after"], cmp["approved_clean"], cut)
    want(not ok, "same_as_approved can-fail: the sliver pixels themselves differ (%s)" % d)
    # can-fail: the most opaque stake pixel within 3 px of a sliver, over all variants, recoloured in its atlas
    best = None
    for name in st.VARIANTS:
        img, lib_uv, _ = st.atlas(name)
        H, W = img.shape[:2]
        for (u0, v0, u1, v1), (X0, Y0, X1, Y1, win, foreign) in zip([q[2:] for q in lib_uv], st._cut(name)[0]):
            near = spk._dilate(foreign, 3)      # own pixels never 8-touch a foreign one (another component): within 3 px
            for y, x in np.argwhere(near & ~foreign & (win[..., 3] > 0)):
                if best is None or win[y, x, 3] > best[0]:
                    best = (int(win[y, x, 3]), name, img, int(round((1 - v1) * H)) + y, int(round(u0 * W)) + x)
    want(best is not None and best[0] >= 128, "a stake pixel (alpha >= 128) within 3 px of a sliver to recolour (%s)"
         % (best and best[:2],))
    _, name, img, y, x = best
    img = img.copy()
    img[y, x, :3] = 255 - img[y, x, :3]
    moved = spk.render(spk.compare_pit(), "after", P=PX, atlases={name: Image.fromarray(img, "RGBA")})
    ok, d = spk.same_as_approved(moved, cmp["approved_clean"], cmp["approved"])
    want(not ok, "same_as_approved can-fail: one stake pixel beside a sliver recoloured (%s)" % d)
    real_lib = dict(spk._LIB)
    try:     # can-fail, the r3 drift: a different pitch moves every stake
        spk._LIB.update({i: (lib, (p[0] * 1.1, p[1] * 1.1)) for i, (lib, p) in real_lib.items()})
        ok, d = spk.same_as_approved(spk.render(spk.compare_pit(), "after", P=PX), cmp["approved_clean"], cmp["approved"])
        want(not ok, "same_as_approved can-fail: a 10%% wider pitch (%s)" % d)
    finally:
        spk._LIB.clear()
        spk._LIB.update(real_lib)
    bad = st.check()
    want(not bad, "stakes.py --check: .cs, atlas sources and installed atlases current, every box one stake (%s)" % bad)
    # can-fail, the review s2c defect: the approved boxes, sampled straight from the shipped sprite, hold neighbours' slivers
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
    tight, tlib, _ = st.atlas("b", 24, 64, 256)       # review s3: cells too small for the lower mips
    n = st.dirty_boxes(tight[..., 3], [q[2:] for q in tlib])
    want(n > 0, "dirty_boxes can-fail: 24x64 cells mix stakes by mip %d (%d boxes)" % (st.MIP_CHECK, n))
    n = st.dirty_boxes(tight[..., 3], [q[2:] for q in tlib], levels=0)
    want(n == 0, "dirty_boxes: the same 24x64 atlas is clean at full resolution (the mip levels are what fail it)")

def covers():
    for name, mk in cov.SCENES:
        for tier in cov.TIERS:
            for mode in ("before", "planks", "planks_ground", "planks_full", "dusted"):
                pit, cs = mk()
                res = cov.render(pit, cs, mode, tier, P=PX)
                ok = [cov.cover_reads_as_material(res, c)[0] for c in sorted(cs)]
                if mode in ("before", "dusted"):
                    want(not any(ok), "cover_reads_as_material FAILS %s (%s, %s): %d/%d cells" % (mode, name, tier, sum(ok), len(ok)))
                else:
                    want(all(ok), "cover_reads_as_material %s (%s, %s): %d/%d cells" % (mode, name, tier, sum(ok), len(ok)))
    pit, cs = cov.SCENES[1][1]()
    want(cov.deck_matches_ground(cov.render(pit, cs, "before", P=PX))[0], "deck_matches_ground: shipped print of a whole-pit deck")
    want(not cov.deck_matches_ground(cov.render(pit, cs, "planks", P=PX))[0], "deck_matches_ground FAILS the drawn lattice (B)")
    blank = cov.render(pit, set(), "planks", P=PX)
    want(not cov.cover_reads_as_material(blank, (2, 2))[0], "cover_reads_as_material can-fail: a cell with no cover")


def soda_pail():
    import numpy as np
    from PIL import Image
    tex = HERE.parent / "Textures"
    for size, check in (("Bottle", msp.bottle_reads_as_soda), ("Bucket", msp.pail_is_orange)):
        rel = msp.REL[size]
        inst = Image.open(tex / rel).convert("RGBA")
        pilot = Image.open(msp.SRC / size / "Modern" / ("RM_%s.png" % size)).convert("RGBA")
        res = check(inst)
        want(res[0], "%s check PASSES installed: %s" % (size, ", ".join("%.3g" % x for x in res[1:])))
        res = check(pilot)
        want(not res[0], "%s check FAILS the pilot: %s" % (size, ", ".join("%.3g" % x for x in res[1:])))
        a, b = np.asarray(inst), np.asarray(pilot)
        if size == "Bottle":
            grey = a.copy()
            lab = msp.label_region()
            grey[lab, :3] = a[lab, :3].max(-1, keepdims=True)
            want(not check(Image.fromarray(grey, "RGBA"))[0], "Bottle check can-fail: the label greyed out")
        else:
            blue = a.astype(float) / 255.0
            _, s, v = msp.hsv(blue[..., :3])
            body = (msp.blue_weight(b[..., :3].astype(float) / 255.0) > 0.5)
            blue[body, :3] = msp.hsv_to_rgb(np.full(v.shape, msp.BLUE_H), s, v)[body]
            want(not check(Image.fromarray(np.round(blue * 255).astype(np.uint8), "RGBA"))[0],
                 "Bucket check can-fail: the installed pail hue-turned to blue")
        mk_inst = np.asarray(Image.open(tex / rel.replace(".png", "_m.png")).convert("RGBA"))
        mk_pilot = np.asarray(Image.open(msp.SRC / size / "Modern" / ("RM_%s_m.png" % size)).convert("RGBA"))
        want((mk_inst == mk_pilot).all(), "%s mask unchanged (liquid R, trim G)" % size)
        want((a[..., 3] == b[..., 3]).all(), "%s alpha unchanged" % size)
        keep = (mk_pilot[..., 0] > 127) | (mk_pilot[..., 1] > 127)
        want((a[keep] == b[keep]).all(), "%s liquid and trim pixels untouched (%d px)" % (size, int(keep.sum())))
        want((a == np.asarray(msp.BUILD[size]())).all(), "%s installed == modern_soda_pail.build" % size)


if __name__ == "__main__":
    parity()
    pipe_joins()
    sprinkler_parity()
    sprinkler()
    modern_blue()
    ladder()
    rail_ladder()
    spikes()
    covers()
    soda_pail()
    print("%d FAIL" % len(fails) if fails else "ALL OK")
    sys.exit(1 if fails else 0)
