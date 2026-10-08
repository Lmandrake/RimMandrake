"""selftest_hugethings_footprint.py -- offline proof of Huge Things' footprint arithmetic and the Rot giants' data.

    python3 src/RimMandrake/HugeThings/selftest_hugethings_footprint.py      -> "N/N PASS", exit 0

Mirrors Source/FootprintMath.cs function for function, in float32 like the C#, and pins (HUGE_THINGS_FOOTPRINT_1,
decision taken by question card 2026-10-07 20:05 PDT: select the whole drawn picture; block only where the art
touches the ground):
  * the draw transform Plant.Print uses (square quad, bottom-anchored on the root cell, centre column on the root);
  * that at full growth the blocked cells ARE the measured contact cells, mirrored exactly by the engine's flipUv,
    unmoved by its +-0.05 jitter, never the root cell and never south of it;
  * that the selection rect holds every blocked cell AND the whole drawn picture, for every giant, variant,
    flip, growth and Mod Settings scale;
  * the measured masks themselves (per-variant contact counts) and that the patch is exactly what
    measure_huge_plant_masks.py produces from the current art (a stale patch fails here, not in game);
  * that EVERY Rot plant drawn >= 6 cells wide is in the patch (coverage sweep with a sanity probe);
  * that the C# still carries the expressions this file mirrors (a drift guard, not a compiler).
"""
import math
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure_huge_plant_masks as tool  # noqa: E402

PATCH = tool.PATCH

# defName -> {variant texture: measured contact cells at full growth}. Pinned from a tool run 2026-10-07; a change
# in the art or the method shows here first. Rerun the tool, LOOK at --preview, then update this table.
EXPECTED = {
    "AB_AgariluxPrime": {"AgariluxPrime": 118},
    "AB_DribblingCap": {"DribblingCap_A": 28},
    "RM_Nogtyl": {"Nogtyl_A": 17, "Nogtyl_B": 13, "Nogtyl_C": 10},
    "RM_Arpeau": {"Arpeau_A": 4, "Arpeau_B": 3},
    "AB_ArbuscularMycorrhiza": {"ArbuscularMycorrhiza_A": 16},
    "AB_AgaricusDomeCap": {"AgaricusDomeCap": 10},
    "AB_GiantAgarilux": {"GiantAgarilux_A": 0},   # its art touches the ground only in its own (root) cell,
    "AB_WitchesOyster": {"WitchesOyster": 9},
    "RM_PaleTree": {"PaleTree_A": 3},
}
# Before this rework every giant blocked a trunkWidth x trunkDepth column north of its root (minus the root):
BEFORE = {"AB_AgariluxPrime": 15, "AB_DribblingCap": 8, "RM_Nogtyl": 8, "RM_Arpeau": 3, "AB_ArbuscularMycorrhiza": 8,
          "AB_AgaricusDomeCap": 5, "AB_GiantAgarilux": 3, "RM_PaleTree": 3, "AB_WitchesOyster": 1}


def f32(x):
    return struct.unpack("f", struct.pack("f", x))[0]


# ---- the mirror of FootprintMath.cs ------------------------------------------------------------------------
def round_half_up(v):
    return int(math.floor(f32(f32(v) + 0.5)))


def quad(root, draw_x, visual, jx, jz):
    """(minX, minZ, size) -- FootprintMath.Quad."""
    cx = f32(root[0] + 0.5 + jx)
    cz = f32(root[1] + 0.5 + jz)
    if f32(cz - visual / 2.0) < root[1]:
        cz = f32(root[1] + visual / 2.0)
    side = f32(draw_x * visual)
    return (f32(cx - side / 2.0), f32(cz - side / 2.0), side)


def picture_bounds(q, omin, omax, flip):
    """RM_HugeFootprintKernel.PictureBounds."""
    mx, mz, s = q
    u0 = 1.0 - omax[0] if flip else omin[0]
    u1 = 1.0 - omin[0] if flip else omax[0]
    return f32(mx + u0 * s), f32(mz + omin[1] * s), f32(mx + u1 * s), f32(mz + omax[1] * s)


def picture_rect(q, omin, omax, flip):
    """(minX, minZ, maxX, maxZ) inclusive -- RM_HugeFootprintKernel.PictureBox."""
    x0, z0, x1, z1 = picture_bounds(q, omin, omax, flip)
    minx, minz = int(math.floor(x0)), int(math.floor(z0))
    return (minx, minz, max(minx, int(math.ceil(x1)) - 1), max(minz, int(math.ceil(z1)) - 1))


def contact_cells(root, q, block_scale, flip, measured, contact, omin=(0.0, 0.0), omax=(1.0, 1.0)):
    """RM_HugeFootprintKernel.ContactCells."""
    out = []
    if not contact or measured <= 0 or q[2] <= 0 or block_scale <= 0:
        return out
    px0, pz0, px1, pz1 = picture_bounds(q, omin, omax, flip)
    bs = f32(q[2] * block_scale)
    left, bottom = f32(f32(q[0] + q[2] * 0.5) - bs / 2.0), q[1]
    for z in range(int(math.floor(bottom)), int(math.ceil(bottom + bs))):
        for x in range(int(math.floor(left)), int(math.ceil(left + bs))):
            if (x, z) == tuple(root):
                continue
            if x + 0.5 < px0 or x + 0.5 > px1 or z + 0.5 < pz0 or z + 0.5 > pz1:
                continue
            u, v = f32((x + 0.5 - left) / bs), f32((z + 0.5 - bottom) / bs)
            if u < 0 or u > 1 or v < 0 or v > 1:
                continue
            if flip:
                u = f32(1.0 - u)
            dx = int(math.floor(f32(0.5 + f32(u - 0.5) * measured)))
            dz = int(math.floor(f32(v * measured)))
            if (dx, dz) in contact:
                out.append((x, z))
    return out


def select_rect(root, pic, blocked):
    xs = [pic[0], pic[2], root[0]] + [c[0] for c in blocked]
    zs = [pic[1], pic[3], root[1]] + [c[1] for c in blocked]
    return (min(xs), min(zs), max(xs), max(zs))


def centred_rect(c, w, h):
    return (c[0] - (w - 1) // 2, c[1] - (h - 1) // 2, w, h)


def hitbox_side(drawn, fraction, mult):
    return max(1, round_half_up(f32(f32(drawn * fraction) * mult)))


def lerp(r, g):
    return f32(r[0] + f32(f32(r[1] - r[0]) * g))


def inside(r, c):
    return r[0] <= c[0] <= r[2] and r[1] <= c[1] <= r[3]


# ---- reading the patch --------------------------------------------------------------------------------------
def patch_table():
    out = {}
    for op in ET.parse(PATCH).getroot():
        dn = re.search(r'defName="([^"]+)"', op.findtext("xpath")).group(1)
        li = op.find("match/value/li")
        assert li.get("Class") == "RimMandrake.HugeThings.RM_HugePlantExtension", li.get("Class")
        assert li.get("MayRequire") == "mandrake.rm.hugethings", "extension li must be MayRequire-guarded"
        vs = {}
        for v in li.findall("variants/li"):
            omin = tuple(float(x) for x in v.findtext("opaqueMin").strip("()").split(","))
            omax = tuple(float(x) for x in v.findtext("opaqueMax").strip("()").split(","))
            cells = set(tuple(int(x) for x in c.text.strip("()").split(",")) for c in v.findall("contact/li"))
            vs[v.findtext("texture")] = (omin, omax, cells)
        out[dn] = (float(li.findtext("measuredSize")), vs)
    return out


_GIANTS = None


def giants():
    global _GIANTS
    if _GIANTS is None:
        _GIANTS = dict((p["def"], p) for p in tool.giants())
    return _GIANTS


# ---- the tests ---------------------------------------------------------------------------------------------
TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


@test
def rounding_is_half_up():
    assert [round_half_up(x) for x in (0.5, 1.5, 2.5, 2.49, 3.5)] == [1, 2, 3, 2, 4]


@test
def quad_is_bottom_anchored_on_the_root():
    assert quad((10, 10), 1.0, 12.0, 0.0, 0.0) == (4.5, 10.0, 12.0)
    q = quad((10, 10), 1.0, 12.0, 0.04, -0.05)       # z jitter is erased by the anchoring, x jitter is kept
    assert abs(q[0] - 4.54) < 1e-5 and q[1] == 10.0, q
    q = quad((10, 10), 1.0, 0.5, 0.0, 0.03)          # a small plant is not anchored (num2/2 < 0.5)
    assert abs(q[1] - 10.28) < 1e-5, q


@test
def picture_rect_places_and_mirrors_the_box():
    q = (4.5, 10.0, 12.0)
    assert picture_rect(q, (0.0, 0.0), (1.0, 1.0), False) == (4, 10, 16, 21)
    a = picture_rect(q, (0.1, 0.05), (0.4, 0.9), False)
    b = picture_rect(q, (0.1, 0.05), (0.4, 0.9), True)
    assert a == (5, 10, 9, 20) and b == (11, 10, 15, 20), (a, b)


@test
def full_growth_blocks_exactly_the_measured_cells_mirrored_by_flip():
    for dn, (size, vs) in patch_table().items():
        for tex, (_mn, _mx, cells) in vs.items():
            for jx in (-0.05, 0.0, 0.049):
                q = quad((50, 50), 1.0, size, jx, 0.0)
                got = set((x - 50, z - 50) for x, z in contact_cells((50, 50), q, 1.0, False, size, cells, _mn, _mx))
                assert got == cells, "%s/%s jx=%s: %r" % (dn, tex, jx, sorted(got ^ cells)[:6])
                got = set((x - 50, z - 50) for x, z in contact_cells((50, 50), q, 1.0, True, size, cells, _mn, _mx))
                want = set((-dx, dz) for dx, dz in cells)
                assert got == want, "%s/%s flipped: %r" % (dn, tex, sorted(got ^ want)[:6])


@test
def root_is_never_blocked_nor_the_cell_south_of_it():
    for dn, (size, vs) in patch_table().items():
        for tex, (_mn, _mx, cells) in vs.items():
            assert (0, 0) not in cells, "%s/%s blocks its own cell (the blocker would wipe the plant)" % (dn, tex)
            assert all(dz >= 0 for _dx, dz in cells), "%s/%s blocks south of the root" % (dn, tex)


@test
def selection_holds_every_blocked_cell_and_the_whole_picture():
    root = (50, 50)
    n = 0
    for dn, (size, vs) in patch_table().items():
        vr = giants()[dn]["visual"]
        for tex, (omin, omax, cells) in vs.items():
            for g in (0.25, 0.5, 0.8, 1.0):
                for flip in (False, True):
                    for scale in (0.5, 1.0, 1.5):
                        q = quad(root, 1.0, lerp(vr, g), 0.03, 0.0)
                        pic = picture_rect(q, omin, omax, flip)
                        blocked = contact_cells(root, q, scale, flip, size, cells, omin, omax)
                        sel = select_rect(root, pic, blocked)
                        assert all(inside(sel, c) for c in blocked), (dn, tex, g, flip, scale)
                        assert all(inside(pic, c) for c in blocked), ("blocked outside the picture", dn, tex, g, flip, scale)
                        assert sel[0] <= pic[0] and sel[1] <= pic[1] and sel[2] >= pic[2] and sel[3] >= pic[3]
                        # the picture box really is the drawn picture: its float edges fall inside the cell rect
                        u0 = 1 - omax[0] if flip else omin[0]
                        u1 = 1 - omin[0] if flip else omax[0]
                        assert sel[0] <= q[0] + u0 * q[2] and q[0] + u1 * q[2] <= sel[2] + 1 + 1e-4
                        assert sel[1] <= q[1] + omin[1] * q[2] and q[1] + omax[1] * q[2] <= sel[3] + 1 + 1e-4
                        n += 1
    assert n > 200, n


@test
def blocking_follows_growth_and_settings():
    size, vs = patch_table()["RM_Nogtyl"]
    mn, mx, cells = vs["Nogtyl_A"]
    vr = giants()["RM_Nogtyl"]["visual"]
    counts = [len(contact_cells((50, 50), quad((50, 50), 1.0, lerp(vr, g), 0, 0), 1.0, False, size, cells, mn, mx))
              for g in (0.0, 0.5, 1.0)]
    assert counts[0] < counts[1] < counts[2] == len(cells), counts
    big = len(contact_cells((50, 50), quad((50, 50), 1.0, size, 0, 0), 1.5, False, size, cells, mn, mx))
    small = len(contact_cells((50, 50), quad((50, 50), 1.0, size, 0, 0), 0.5, False, size, cells, mn, mx))
    assert small < len(cells) < big, (small, big)


@test
def blocked_cells_stay_inside_the_drawn_quad():
    for dn, (size, vs) in patch_table().items():
        for tex, (omin, omax, cells) in vs.items():
            q = quad((50, 50), 1.0, size, 0, 0)
            for x, z in contact_cells((50, 50), q, 1.0, False, size, cells, omin, omax):
                assert q[0] - 1 < x < q[0] + q[2] and q[1] <= z < q[1] + q[2], (dn, tex, x, z)


@test
def pawn_hitbox_side():
    assert hitbox_side(10, 0.6, 1.0) == 6 and hitbox_side(1, 0.6, 1.0) == 1 and hitbox_side(2.5, 0.6, 1.0) == 2
    assert centred_rect((10, 10), 3, 3) == (9, 9, 3, 3) and centred_rect((10, 10), 4, 4) == (9, 9, 4, 4)


@test
def measured_masks_are_pinned():
    got = dict((dn, dict((t, len(v[2])) for t, v in vs.items())) for dn, (_s, vs) in patch_table().items())
    assert got == EXPECTED, "masks moved: %r" % sorted(set((k, str(v)) for k, v in got.items()) ^ set((k, str(v)) for k, v in EXPECTED.items()))
    assert set(BEFORE) == set(EXPECTED)


@test
def measured_size_is_the_full_growth_quad():
    for dn, (size, _vs) in patch_table().items():
        p = giants()[dn]
        assert abs(size - p["drawSizeX"] * p["visual"][1]) < 1e-6, (dn, size, p["visual"])


@test
def every_rot_giant_is_covered():
    gs = sorted(giants())
    probe = [g for g in ("AB_AgariluxPrime", "RM_Nogtyl", "AB_DribblingCap") if g in gs]
    assert len(probe) == 3, "sanity probe: the sweep cannot see known giants (%r of %d)" % (probe, len(gs))
    table = patch_table()
    assert sorted(table) == gs, "patch vs giants differ: %r" % sorted(set(table) ^ set(gs))


@test
def patch_is_what_the_tool_measures_from_the_current_art():
    rc = tool.main(["--check"])
    assert rc == 0, "RotGiants_HugeFootprint.xml is stale: rerun %s" % tool.TOOL_CMD


@test
def csharp_still_matches_this_mirror():
    src = open(os.path.join(HERE, "Source", "Kernel", "RM_HugeFootprintKernel.cs"), encoding="utf-8").read()
    for needle in ("(int)Math.Floor(v + 0.5f)", "if (cz - visual / 2f < rootZ) cz = rootZ + visual / 2f;",
                   "float side = drawSizeX * visual;", "float u0 = flip ? 1f - m.U1 : m.U0;",
                   "float left = q.CentreX - bs / 2f, bottom = q.MinZ;", "if (flip) u = 1f - u;",
                   "int dx = (int)Math.Floor(0.5f + (u - 0.5f) * m.MeasuredSize);",
                   "int dz = (int)Math.Floor(v * m.MeasuredSize);", "if (x == rootX && z == rootZ) continue;",
                   "if (cx < px0 || cx > px1 || cz < pz0 || cz > pz1) continue;"):
        assert needle in src, "RM_HugeFootprintKernel.cs lost `%s` -- update the mirror" % needle
    comp = open(os.path.join(HERE, "Source", "CompHugeFootprint.cs"), encoding="utf-8").read()
    for needle in ("Rand.Seed = p.Position.GetHashCode();", "Gen.RandomHorizontalVector(0.05f);", "bool f = Rand.Bool;",
                   "Rand.Range(0, n)", "p.Growth < ext.minGrowthToBlock", "LerpThroughRange(p.Growth)"):
        assert needle in comp, "CompHugeFootprint.cs lost `%s` (Plant.Print replay)" % needle
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
