"""Procedural distribution maths — the part that makes placed things look real.

WHY THIS IS A SEPARATE MODULE AND THE MOST REUSABLE THING HERE

Placing objects is trivial. Placing them so they look *found rather than
authored* is the whole craft, and it is pure geometry — no bridge, no RimWorld,
no mod list. Everything here is deterministic and testable offline, and it
serves craters, ruins, ship graveyards, cavern floors, refinery sprawl and
forest clearings equally.

The 2026-08-11 crater failed visually not because the maths was wrong but
because the ground under it never changed. The maths is here so the next attempt
starts from something proven.

FOUR IDEAS DO ALMOST ALL THE WORK

1. **Deterministic noise.** A hash of (x, z, seed) gives repeatable randomness.
   Same seed, same result — so a layout can be reviewed, tweaked and re-run
   rather than re-rolled and lost.
2. **Dithered thresholds.** Comparing `density + noise` against a cutoff makes
   boundaries interlock instead of drawing a hard circle. This single trick is
   the difference between "a disc of rubble" and "a blast zone".
3. **Anisotropy.** Real formations are rarely round. Squash an axis, rotate it,
   add directional lobes, and the eye stops reading a template.
4. **Clustering.** Natural debris is clumpy, not uniform. Poisson-ish rejection
   or seeded clumps beat independent per-cell rolls every time.

Everything returns plain `[(x, z, weight)]` or a predicate, so callers decide
what to place. Nothing here knows what a Filth_Ash is.
"""
import math


# ------------------------------------------------------------------- noise
def noise(x, z, seed=0):
    """Deterministic hash noise in [0,1). Cheap, stable, no dependencies."""
    h = (int(x) * 73856093) ^ (int(z) * 19349663) ^ (int(seed) * 83492791)
    h &= 0x7FFFFFFF
    h = (h ^ (h >> 13)) * 1274126177
    h &= 0x7FFFFFFF
    return (h % 10007) / 10007.0


def fbm(x, z, seed=0, octaves=3, scale=8.0):
    """Fractal value noise: smoother, blobbier fields for terrain and caverns.

    Samples `noise` on a coarse lattice and blends, so nearby cells correlate.
    Use this for anything that should look geological rather than sprinkled.
    """
    total, amp, norm, s = 0.0, 1.0, 0.0, float(scale)
    for o in range(octaves):
        gx, gz = x / s, z / s
        x0, z0 = math.floor(gx), math.floor(gz)
        fx, fz = gx - x0, gz - z0
        # smoothstep for continuity
        fx = fx * fx * (3 - 2 * fx)
        fz = fz * fz * (3 - 2 * fz)
        n00 = noise(x0, z0, seed + o)
        n10 = noise(x0 + 1, z0, seed + o)
        n01 = noise(x0, z0 + 1, seed + o)
        n11 = noise(x0 + 1, z0 + 1, seed + o)
        nx0 = n00 + (n10 - n00) * fx
        nx1 = n01 + (n11 - n01) * fx
        total += (nx0 + (nx1 - nx0) * fz) * amp
        norm += amp
        amp *= 0.5
        s *= 0.5
    return total / norm


# --------------------------------------------------------------- geometry
def elliptical_radius(dx, dz, squash=1.0, rotation=0.0):
    """Distance from centre in a squashed, rotated frame.

    `squash` < 1 flattens the z axis. `rotation` is radians. Together they stop
    a formation reading as a stamped circle.
    """
    c, s = math.cos(-rotation), math.sin(-rotation)
    rx = dx * c - dz * s
    rz = dx * s + dz * c
    return math.hypot(rx, rz / (squash or 1.0))


def lobes(dx, dz, count=3, direction=0.0, strength=0.5):
    """Directional multiplier in [1-strength, 1+strength].

    Ejecta rays, root systems, spill patterns, corridor branches. `count` lobes
    arranged around `direction`.
    """
    ang = math.atan2(dz, dx)
    return 1.0 + strength * math.cos((ang - direction) * count)


# ----------------------------------------------------------------- fields
def radial_field(cx, cz, radius, falloff=1.0, squash=1.0, rotation=0.0,
                 lobe_count=0, lobe_dir=0.0, lobe_strength=0.4, reach=1.0):
    """Yield (x, z, density) over a disc, density 1 at centre → 0 at the edge.

    `falloff` shapes the curve: 1 is linear, 2 concentrates toward the middle,
    0.5 spreads it outward. `reach` extends iteration past the radius so ejecta
    and haloes can trail off naturally.
    """
    span = int(radius * reach) + 1
    for dx in range(-span, span + 1):
        for dz in range(-span, span + 1):
            r = elliptical_radius(dx, dz, squash, rotation) / float(radius)
            if lobe_count:
                r /= lobes(dx, dz, lobe_count, lobe_dir, lobe_strength)
            if r > reach:
                continue
            d = max(0.0, 1.0 - r) ** falloff
            yield cx + dx, cz + dz, d


def dither(density, x, z, seed=0, amount=0.35):
    """Fuzz a density with per-cell noise so edges interlock.

    This is the single most important function in the module. Hard thresholds
    look stamped; dithered ones look eroded.
    """
    return density + (noise(x, z, seed) - 0.5) * amount


def pick(cells, chance, seed=0, jitter=0.35):
    """Filter (x,z,density) → cells that pass a dithered probability test.

    `chance` scales density into a hit rate: chance=0.5 means a cell at full
    density is picked about half the time.
    """
    out = []
    for x, z, d in cells:
        if noise(x, z, seed + 991) < dither(d, x, z, seed, jitter) * chance:
            out.append((x, z, d))
    return out


def clumps(cells, seed=0, clump_scale=4.0, threshold=0.5):
    """Keep cells falling inside smooth noise blobs — clustered, not sprinkled.

    Debris, mineral seams, moss, wreck scatter. Independent per-cell rolls look
    like static; this looks like geology.
    """
    return [(x, z, d) for x, z, d in cells
            if fbm(x, z, seed, octaves=2, scale=clump_scale) > threshold]


def ring(cells, inner, outer):
    """Keep only cells whose density falls in a band — crater rims, walls."""
    return [(x, z, d) for x, z, d in cells if inner <= d <= outer]


def rim_band(cx, cz, radius, width=0.15, **kw):
    """Convenience: the raised rim of a crater or the wall line of a cavern."""
    lo = max(0.0, 1.0 - (radius * (1.0 + width)) / radius)
    return ring(radial_field(cx, cz, radius, **kw), 0.001, width)


# ----------------------------------------------------------------- paths
def walk(x0, z0, x1, z1, wander=0.35, seed=0, width=1):
    """A wandering line from A to B — rivers, corridors, pipe runs, cracks.

    Not a Bresenham line: each step is nudged by noise, so the result reads as
    carved or grown rather than drawn. `width` dilates it.
    """
    cells = set()
    x, z = float(x0), float(z0)
    steps = int(math.hypot(x1 - x0, z1 - z0) * 1.6) + 1
    for i in range(steps + 1):
        t = i / float(steps)
        tx = x0 + (x1 - x0) * t
        tz = z0 + (z1 - z0) * t
        n = noise(int(tx), int(tz), seed) - 0.5
        m = noise(int(tz), int(tx), seed + 17) - 0.5
        px = tx + n * wander * 6
        pz = tz + m * wander * 6
        for ox in range(-width, width + 1):
            for oz in range(-width, width + 1):
                if ox * ox + oz * oz <= width * width:
                    cells.add((int(round(px)) + ox, int(round(pz)) + oz))
    return sorted(cells)


def blob(cx, cz, radius, seed=0, roughness=0.45):
    """An irregular closed area — cavern chambers, ponds, clearings, rooms.

    A radial field whose edge is pushed in and out by smooth noise, so the
    outline is organic but the interior stays solid.
    """
    out = []
    span = int(radius * 1.6) + 1
    for dx in range(-span, span + 1):
        for dz in range(-span, span + 1):
            r = math.hypot(dx, dz)
            wobble = (fbm(cx + dx, cz + dz, seed, octaves=2,
                          scale=max(2.0, radius / 2.0)) - 0.5) * 2.0
            if r <= radius * (1.0 + wobble * roughness):
                out.append((cx + dx, cz + dz, 1.0 - r / (radius + 1e-6)))
    return out


def zones(cells, bands):
    """Split (x,z,density) cells into named bands by density.

    bands = [("core",0.75,1.01), ("mid",0.35,0.75), ("edge",0.0,0.35)]
    Returns {name: [(x,z,d)]}. This is how a crater gets a melt sheet, a bowl
    and a rim without writing the loop three times.
    """
    out = {name: [] for name, _lo, _hi in bands}
    for x, z, d in cells:
        for name, lo, hi in bands:
            if lo <= d < hi:
                out[name].append((x, z, d))
                break
    return out
