"""selftest_hugethings_footprint.py -- offline proof of Huge Things' footprint arithmetic and the Rot table.

    python3 src/RimMandrake/HugeThings/selftest_hugethings_footprint.py      -> "N/N PASS", exit 0

Mirrors Source/Kernel/RM_FootprintKernel.cs function for function (the C# fuzz selftest_hugethings_fuzz.py now runs the production kernel itself; this mirror remains for the species table), in float32 like the C#, and pins:
  * the rounding (half UP, never banker's), the growth scale, the trunk and click rects;
  * that a young plant blocks nothing and the trunk grows with the drawn size;
  * that the plant's own cell is on the trunk's SOUTH edge, so it stays reachable for cutting;
  * the per-species table in TheRot/Patches/RotGiants_HugeFootprint.xml (owner ruling 2026-10-07: trunks
    "~2x2 to 4x4 by species"), and that EVERY Rot plant drawn >= 6 cells wide is in it (coverage sweep, with a
    sanity probe that it can see the giants at all);
  * that the C# still carries the expressions this file mirrors (a drift guard, not a compiler).
"""
import math
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.join(HERE, "..", "TheRot")
GIANT_MIN_WIDTH = 6.0

# defName -> (label, trunkWidth, trunkDepth, stemHeight). The design note's table; the patch must match.
EXPECTED = {
    "AB_AgariluxPrime": ("grath elder", 4, 4, 8),
    "AB_DribblingCap": ("ruvvak weeper", 3, 3, 5),
    "RM_Nogtyl": ("brommok timber", 3, 3, 5),
    "RM_Arpeau": ("churrun mast", 2, 2, 5),
    "AB_ArbuscularMycorrhiza": ("bollusk trunk", 3, 3, 4),
    "AB_AgaricusDomeCap": ("skarrow dome", 3, 2, 3),
    "AB_GiantAgarilux": ("vokkun pillar", 2, 2, 3),
    "RM_PaleTree": ("quellan tree", 2, 2, 3),
    "AB_WitchesOyster": ("turrok shelf", 2, 1, 2),
}


def f32(x):
    return struct.unpack("f", struct.pack("f", x))[0]


# ---- the mirror of FootprintMath.cs ------------------------------------------------------------------------
def round_half_up(v):
    return int(math.floor(f32(f32(v) + 0.5)))


def growth_scale(vmin, vmax, growth):
    if vmax <= 0:
        return 1.0
    g = min(1.0, max(0.0, growth))
    now = f32(vmin + f32(f32(vmax - vmin) * g))
    return min(1.0, max(0.0, f32(now / vmax)))


def scaled(full, scale):
    if full <= 0:
        return 0
    return max(1, round_half_up(f32(full * scale)))


def north_rect(root, w, d):
    """(minX, minZ, width, height)"""
    return (root[0] - (w - 1) // 2, root[1], w, d)


def centred_rect(c, w, h):
    return (c[0] - (w - 1) // 2, c[1] - (h - 1) // 2, w, h)


def trunk_rect(root, ext, gscale, growth, mult=1.0):
    if growth < ext.get("minGrowthToBlock", 0.25):
        return None
    s = f32(gscale * mult)
    w, d = scaled(ext["w"], s), scaled(ext["d"] or ext["w"], s)
    if w * d < 2:
        return None
    return north_rect(root, w, d)


def select_rect(root, ext, gscale, mult=1.0):
    s = f32(gscale * mult)
    depth = ext["d"] or ext["w"]
    stem = ext["stem"] or depth
    w = scaled(ext["w"], s)
    h = max(scaled(depth, s), scaled(stem, s))
    if w * h < 2:
        return None
    return north_rect(root, w, h)


def hitbox_side(drawn, fraction, mult):
    return max(1, round_half_up(f32(f32(drawn * fraction) * mult)))


def cells(r):
    x, z, w, h = r
    return set((x + i, z + j) for i in range(w) for j in range(h))


# ---- reading the repo -------------------------------------------------------------------------------------
def patch_table():
    out = {}
    root = ET.parse(os.path.join(ROT, "Patches", "RotGiants_HugeFootprint.xml")).getroot()
    for op in root:
        m = op.find("match")
        dn = re.search(r'defName="([^"]+)"', op.findtext("xpath")).group(1)
        li = m.find("value/li")
        assert li.get("Class") == "RimMandrake.HugeThings.RM_HugePlantExtension", li.get("Class")
        assert li.get("MayRequire") == "mandrake.rm.hugethings", "extension li must be MayRequire-guarded"
        out[dn] = (int(li.findtext("trunkWidth")), int(li.findtext("trunkDepth") or 0), int(li.findtext("stemHeight") or 0))
    return out


def rot_visual_ranges():
    """{defName: (min, max)} for every Rot plant: own defs, then the resizes of NamesAndSizes on donor defs."""
    out = {}
    for dp, _d, files in os.walk(os.path.join(ROT, "Defs")):
        for fn in files:
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    v = el.findtext("plant/visualSizeRange") if isinstance(el.tag, str) else None
                    if v and el.findtext("defName"):
                        a, b = v.split("~")
                        out[el.findtext("defName").strip()] = (float(a), float(b))
    src = open(os.path.join(ROT, "Patches", "RotSpecies_NamesAndSizes.xml"), encoding="utf-8").read()
    for dn, a, b in re.findall(r'defName="(\w+)"\]/plant/visualSizeRange</xpath>\s*<value><visualSizeRange>([\d.]+)~([\d.]+)', src):
        out[dn] = (float(a), float(b))
    return out


# ---- the tests ---------------------------------------------------------------------------------------------
TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


@test
def rounding_is_half_up():
    assert [round_half_up(x) for x in (0.5, 1.5, 2.5, 2.49, 3.5)] == [1, 2, 3, 2, 4]


@test
def scaled_never_zero_for_real_dimension():
    assert scaled(3, 0.01) == 1 and scaled(0, 1.0) == 0 and scaled(4, 1.0) == 4 and scaled(3, 0.5) == 2


@test
def growth_scale_follows_drawn_size():
    assert abs(growth_scale(5.14, 9, 1.0) - 1.0) < 1e-6
    assert abs(growth_scale(5.14, 9, 0.0) - 5.14 / 9) < 1e-5
    assert growth_scale(0, 0, 0.5) == 1.0


@test
def young_plant_blocks_nothing():
    ext = {"w": 3, "d": 3, "stem": 4}
    assert trunk_rect((10, 10), ext, growth_scale(5.14, 9, 0.15), 0.15) is None


@test
def trunk_grows_with_the_plant():
    ext = {"w": 3, "d": 3, "stem": 4}
    half = trunk_rect((10, 10), ext, growth_scale(5.14, 9, 0.5), 0.5)
    full = trunk_rect((10, 10), ext, growth_scale(5.14, 9, 1.0), 1.0)
    assert half == (10, 10, 2, 2), half
    assert full == (9, 10, 3, 3), full


@test
def root_is_on_the_south_edge_and_reachable():
    for dn, (_l, w, d, st) in EXPECTED.items():
        r = trunk_rect((50, 50), {"w": w, "d": d, "stem": st}, 1.0, 1.0)
        assert r is not None, dn
        x, z, rw, rh = r
        assert z == 50 and x <= 50 < x + rw, (dn, r)
        assert (50, 49) not in cells(r), dn            # the cell south of the root is never trunk
        assert len(cells(r) - {(50, 50)}) == w * d - 1  # blockers = rect minus the plant's own cell


@test
def click_area_covers_trunk_and_stem():
    r = select_rect((50, 50), {"w": 4, "d": 4, "stem": 8}, 1.0)
    assert r == (49, 50, 4, 8), r
    t = trunk_rect((50, 50), {"w": 4, "d": 4, "stem": 8}, 1.0, 1.0)
    assert cells(t) <= cells(r)
    assert select_rect((0, 0), {"w": 1, "d": 1, "stem": 1}, 1.0) is None   # one cell = vanilla


@test
def settings_scale_moves_the_trunk():
    ext = {"w": 4, "d": 4, "stem": 8}
    assert trunk_rect((0, 0), ext, 1.0, 1.0, 1.5)[2:] == (6, 6)
    assert trunk_rect((0, 0), ext, 1.0, 1.0, 0.5)[2:] == (2, 2)


@test
def pawn_hitbox_side():
    assert hitbox_side(10, 0.6, 1.0) == 6 and hitbox_side(1, 0.6, 1.0) == 1 and hitbox_side(2.5, 0.6, 1.0) == 2
    assert centred_rect((10, 10), 3, 3) == (9, 9, 3, 3) and centred_rect((10, 10), 4, 4) == (9, 9, 4, 4)


@test
def rot_patch_matches_the_design_table():
    got = patch_table()
    want = dict((k, v[1:]) for k, v in EXPECTED.items())
    assert got == want, "patch vs table differ: %r" % sorted(set(got.items()) ^ set(want.items()))
    for dn, (w, d, _s) in got.items():
        assert 1 <= w <= 4 and 1 <= d <= 4, "%s trunk %dx%d is outside the ruled ~2x2..4x4" % (dn, w, d)


@test
def every_rot_giant_is_covered():
    vr = rot_visual_ranges()
    giants = sorted(dn for dn, (_a, b) in vr.items() if b >= GIANT_MIN_WIDTH)
    probe = [g for g in ("AB_AgariluxPrime", "RM_Nogtyl", "AB_DribblingCap") if g in giants]
    assert len(probe) == 3, "sanity probe: the sweep cannot see known giants (%r of %d ranges)" % (probe, len(vr))
    missing = [g for g in giants if g not in EXPECTED]
    assert not missing, "Rot plants drawn >= %s wide with no trunk: %r" % (GIANT_MIN_WIDTH, missing)
    stale = [g for g in EXPECTED if g not in giants]
    assert not stale, "table rows no longer giants (resized?): %r" % stale


@test
def csharp_still_matches_this_mirror():
    src = open(os.path.join(HERE, "Source", "Kernel", "RM_FootprintKernel.cs"), encoding="utf-8").read()
    for needle in ("(int)Math.Floor(v + 0.5f)", "rootX - (w - 1) / 2, rootZ, w, d", "cx - (w - 1) / 2, cz - (h - 1) / 2",
                   "growth < minGrowthToBlock", "w * d < 2", "w * h < 2", "Math.Max(1, RoundHalfUp(full * scale))"):
        assert needle in src, "RM_FootprintKernel.cs lost `%s` -- update the mirror" % needle
    ext = open(os.path.join(HERE, "Source", "Extensions.cs"), encoding="utf-8").read()
    assert "minGrowthToBlock = 0.25f" in ext and "hitboxFraction = 0.6f" in ext


def main():
    ok = 0
    for fn in TESTS:
        try:
            fn()
            ok += 1
        except AssertionError as e:
            print("FAIL %s: %s" % (fn.__name__, e))
    print("%d/%d PASS" % (ok, len(TESTS)))
    return 0 if ok == len(TESTS) else 1


if __name__ == "__main__":
    sys.exit(main())
