#!/usr/bin/env python3
"""Step 1+2 of the causal repaint: ONE continuous elevation field, then sea level.

🔴 WHY THIS EXISTS. `paint_ashkarr.py` set elevation from a per-region table -
`("scald_rim", 2150, +/-620)` - so two neighbouring tiles differed by a coin flip.
There was no slope anywhere on the planet, which means "downhill" was UNDEFINED,
which means rivers could not be derived and were left as fossils of vanilla's
worldgen. It also means every landform was a CIRCLE, because a region defined by a
radius renders as a disc.

Here elevation is a single continuous field over the tile graph, built from
AUTHORED FEATURES - the fiction already fixes where the Scald Spine and the Fall
Line are, so their positions are an input, not noise. What is NOT authored is their
SHAPE: a range is the contour of a field falling off from a ridge line, plus
multi-octave noise on the sphere. Sea level is then a threshold on that same field,
so coastlines are a consequence and `Coast` mutators become computable.

Everything downstream - rainfall, rivers, biomes, roads - reads `world/relief.npz`
and nothing re-derives elevation for itself.

    python3 src/RimMandrake/Utils/world_relief.py            # build + render
    python3 src/RimMandrake/Utils/world_relief.py --stats    # numbers only

Writes  world/relief.npz     elev metres float32, water bool, arc/bear float32
        world/relief.png     two azimuthal-equidistant discs, day and night
"""
import os
import struct
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world_graph
import world_shape

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT_NPZ = os.path.join(REPO, "world", "relief.npz")
OUT_PNG = os.path.join(REPO, "world", "relief.png")

SEED = 20260817
SEA_LEVEL = 0.0          # metres; the field is authored around this
OCEAN_FLOOR = -350.0     # what the save's water tiles hold today

# ---------------------------------------------------------------- geometry
# arc  = degrees from the substellar point (long 0, lat 0)
# bear = degrees around it; 0 -> the GRAY flank (downwind), 180 -> the TWILIGHT flank
# Identical convention to paint_ashkarr.py. Do not diverge from it.


def arc_bear(lat_deg, lon_deg):
    lat, lon = np.radians(lat_deg), np.radians(lon_deg)
    arc = np.degrees(np.arccos(np.clip(np.cos(lon) * np.cos(lat), -1, 1)))
    bear = np.degrees(np.arctan2(np.sin(lat), np.cos(lat) * np.sin(lon))) % 360.0
    return arc.astype(np.float32), bear.astype(np.float32)


def to_vec(arc, bear):
    """(arc, bearing) in degrees -> unit vectors in the same frame as world_graph."""
    a, b = np.radians(np.atleast_1d(arc)), np.radians(np.atleast_1d(bear))
    lat = np.arcsin(np.sin(a) * np.sin(b))
    lon = np.arctan2(np.sin(a) * np.cos(b), np.cos(a))
    return np.stack([np.cos(lat) * np.cos(lon),
                     np.cos(lat) * np.sin(lon),
                     np.sin(lat)], axis=1)


def ang(V, pts):
    """Angular distance in degrees from every tile to every point: (n, m)."""
    return np.degrees(np.arccos(np.clip(V @ pts.T, -1, 1)))


def dist_to_polyline(V, anchors, samples=24):
    """Degrees from every tile to the nearest point of a chain of anchors.

    A ridge is a LINE, not a disc. This is the whole reason the Scald Spine stops
    being an annulus: uplift falls off from a path, so the range inherits the
    path's shape and the noise breaks its edge.
    """
    pts = []
    for (a0, b0), (a1, b1) in zip(anchors[:-1], anchors[1:]):
        v0, v1 = to_vec(a0, b0)[0], to_vec(a1, b1)[0]
        for t in np.linspace(0, 1, samples, endpoint=False):
            v = v0 * (1 - t) + v1 * t
            pts.append(v / np.linalg.norm(v))
    v = to_vec(anchors[-1][0], anchors[-1][1])[0]
    pts.append(v / np.linalg.norm(v))
    return ang(V, np.array(pts)).min(axis=1)


# ---------------------------------------------------------------- the features
# Authored: WHERE. Emergent: what shape it ends up. Amplitudes are metres.
#
# ring  gaps: a crater rim with no passes is a wall nothing can cross and no river
#       can leave. Every ring here is notched.

RIDGES = [
    # The Scald Spine - the crater rim. A ring, because the Scald IS a crater and
    # that is the one shape ruled round; but notched by passes and frayed by noise.
    dict(name="scald_spine", kind="ring", centre=(35.0, 185.0), radius=18.0,
         amp=1450, sigma=3.2, notch=(3, 0.55, 0.9)),

    # The volcanic range cradling the sunward side of the Scald, joining the rim.
    dict(name="volcanic_range", kind="line", amp=1450, sigma=4.0,
         anchors=[(21.5, 116.0), (23.5, 142.0), (24.5, 168.0),
                  (24.0, 203.0), (22.0, 230.0), (19.5, 254.0)]),

    # The Fall Line - the escarpment where the substellar plateau breaks down on the
    # Gray flank. Radial, not circumferential: it runs sunward-to-antisunward.
    dict(name="fall_line", kind="line", amp=780, sigma=3.2,
         anchors=[(26.0, 352.0), (34.0, 357.0), (43.0, 2.0),
                  (52.0, 6.0), (61.0, 9.0)]),

    # The Twilight Crags / Gray Crags - the nightside rim highlands, a broken chain
    # around the terminator rather than a smooth belt.
    dict(name="twilight_crags", kind="line", amp=900, sigma=5.0,
         anchors=[(104.0, 210.0), (110.0, 186.0), (108.0, 160.0), (114.0, 134.0)]),
    dict(name="gray_crags", kind="line", amp=820, sigma=5.0,
         anchors=[(106.0, 340.0), (112.0, 12.0), (109.0, 42.0), (116.0, 68.0)]),
    dict(name="south_crags", kind="line", amp=760, sigma=6.0,
         anchors=[(118.0, 250.0), (127.0, 272.0), (131.0, 300.0), (124.0, 322.0)]),
]

DOMES = [
    # The substellar plateau: HIGH and FLAT. A flat top is what makes it a plateau
    # instead of a hill, so the falloff is quartic, not gaussian.
    dict(name="plateau", centre=(0.0, 0.0), radius=23.0, amp=1150, flat=True),
    # The nightside is heavy, old crust: a broad rise under the crags.
    dict(name="nightside_rise", centre=(180.0, 0.0), radius=95.0, amp=300, flat=False),
]

BASINS = [
    # The seas. Depth is authored so that thresholding the field at zero reproduces
    # water where the fiction already named it - and NOWHERE ELSE, which is the point.
    dict(name="the_scald", centre=(35.0, 185.0), radius=14.0, amp=-1500, flat=True),
    dict(name="twilight_sea", centre=(91.0, 170.0), radius=19.5, amp=-980, flat=True),
    dict(name="gray_sea", centre=(92.0, 8.0), radius=13.6, amp=-980, flat=True),
    # The antistellar cold trap: the frozen sea and the propane lakes sit in it.
    dict(name="antistellar_trap", centre=(171.0, 44.0), radius=31.0, amp=-1150, flat=True),
]

TROUGHS = [
    # The Dew Belt - a low rift running sunward from the Twilight terminator. It is
    # a TROUGH, which is why moisture collects there; being low is the cause.
    dict(name="dew_belt", amp=-255, sigma=7.5,
         anchors=[(38.0, 184.0), (45.0, 181.0), (52.0, 178.0),
                  (64.0, 178.0), (76.0, 179.0), (89.0, 180.0)]),
    # the pass through the Scald Spine that the Dew Belt drains through. A crater rim
    # with no breach is a wall, and a wall makes the sea inside it unreachable.
    dict(name="scald_gate", amp=-1250, sigma=3.0,
         anchors=[(49.0, 180.0), (44.0, 182.0), (39.0, 184.0)]),
]

# multi-octave noise on the sphere: sum of plane waves in random directions.
# Band-limited and seamless by construction - no projection, no poles, no seams.
# 🔴 The first cut stopped at frequency 50 - wavelength ~7 deg against a 1.5 deg
# tile spacing - so the field had NO energy at tile scale and rendered as blurred
# paint. Terrain must be rough at the scale you look at it. Amplitude falls as 1/f
# (pink), which is what real topography measures.
NOISE_OCTAVES = [(2.2, 105.0), (4.5, 95.0), (9.0, 110.0), (18.0, 90.0),
                 (36.0, 62.0), (72.0, 43.0), (144.0, 29.0), (288.0, 19.0)]
NOISE_WAVES = 32
LAND_BASE = 300.0        # continental freeboard: noise alone must not dig a sea


def sphere_noise(V, rng, octaves=NOISE_OCTAVES, waves=NOISE_WAVES):
    out = np.zeros(len(V), dtype=np.float64)
    for freq, amp in octaves:
        d = rng.normal(size=(waves, 3))
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        ph = rng.uniform(0, 2 * np.pi, size=waves)
        out += amp * (np.sin(freq * (V @ d.T) + ph).sum(axis=1) / np.sqrt(waves / 2))
    return out


def build(verbose=True):
    nb, lat, lon, V = world_graph.load()
    V = np.asarray(V, dtype=np.float64)
    n = len(V)
    arc, bear = arc_bear(lat, lon)
    rng = np.random.default_rng(SEED)

    # domain warp: a coastline or a ridge crest traced from a radius is a circle no
    # matter how good the noise inside it is. Displacing the DISTANCE FIELD by noise
    # makes every authored feature wander around its anchor while still going where
    # the fiction says it goes.
    warp = sphere_noise(V, np.random.default_rng(SEED + 77),
                        octaves=[(3.0, 1.0), (7.0, 0.55), (15.0, 0.3), (31.0, 0.16)],
                        waves=24)
    warp = 3.1 * warp / (np.abs(warp).max() + 1e-9)          # degrees

    elev = np.full(n, LAND_BASE, dtype=np.float64)

    for d in DOMES + BASINS:
        c = to_vec(*d["centre"])
        r = (ang(V, c)[:, 0] + warp * (0.45 if d["flat"] else 0.9)) / d["radius"]
        if d["flat"]:
            f = np.clip(1.0 - r ** 4, 0.0, 1.0)          # flat top / flat floor
        else:
            f = np.exp(-0.5 * r ** 2)
        elev += d["amp"] * f

    for t in TROUGHS:
        dd = np.abs(dist_to_polyline(V, t["anchors"]) + warp)
        elev += t["amp"] * np.exp(-0.5 * (dd / t["sigma"]) ** 2)

    for r in RIDGES:
        if r["kind"] == "ring":
            c = to_vec(*r["centre"])
            dd = np.abs(ang(V, c)[:, 0] - r["radius"] - warp)
            amp = np.full(n, float(r["amp"]))
            if r.get("notch"):
                k, depth, phase = r["notch"]
                # the passes. Without them the rim is a sealed wall and the crater
                # can neither drain nor be crossed.
                th = np.arctan2(V[:, 2] - c[0, 2], V[:, 1] - c[0, 1])
                amp *= 1.0 - depth * np.clip(np.cos(k * th + phase), 0, 1) ** 3
        else:
            dd = np.abs(dist_to_polyline(V, r["anchors"]) + warp)
            amp = np.full(n, float(r["amp"]))
        elev += amp * np.exp(-0.5 * (dd / r["sigma"]) ** 2)

    # 🔑 basin field computed HERE, before the noise, because it does two jobs: it
    # damps roughness on sea floors, and it is the mask that stops noise inventing a
    # sea nobody authored.
    basin = np.zeros(n)
    for d in BASINS:
        c = to_vec(*d["centre"])
        basin = np.maximum(basin, np.clip(
            1.0 - ((ang(V, c)[:, 0] + warp * 0.45) / (d["radius"] * 1.45)) ** 4,
            0.0, 1.0))

    # noise last, and scaled UP on rugged ground: a plain is smooth, a crag is not.
    rough = 0.45 + 0.9 * np.clip(elev / 1600.0, 0.0, 1.0)
    rough += 0.6 * np.clip((arc - 100.0) / 40.0, 0.0, 1.0)     # the nightside crags
    rough *= 1.0 - 0.78 * basin                                # flat sea floors
    rough *= 1.0 - 0.45 * np.clip((21.0 - arc) / 21.0, 0.0, 1.0)   # the plateau top
    elev += sphere_noise(V, rng) * rough

    # two rounds of graph smoothing: kills salt-and-pepper without touching landforms
    # ONE pass. Two smoothed away the tile-scale detail the octaves just added.
    elev = 0.72 * elev + 0.28 * np.array([elev[x].mean() for x in nb])

    # 🔑 Water only where a basin was authored. Noise dipping below zero in the open
    # desert produced four seas nobody named. Endorheic LAKES are legitimate but they
    # are step 3's job - they come from where water actually collects, not from a
    # low noise sample.
    water = (elev < SEA_LEVEL) & (basin > 0.02)
    # a one-tile lake or a one-tile island is a defect at this scale, not detail
    lab, moved = world_shape.despeckle(list(water.astype(np.int8)), nb, min_size=4)
    water = np.array(lab, dtype=bool)
    elev = np.where(water, np.minimum(elev, OCEAN_FLOOR * 0.35), np.maximum(elev, 1.0))

    if verbose:
        land = ~water
        print("tiles %d | water %d (%.1f%%) | land %d" % (n, water.sum(),
              100.0 * water.sum() / n, land.sum()))
        print("land elevation: min %.0f  median %.0f  p95 %.0f  max %.0f m"
              % (elev[land].min(), np.median(elev[land]),
                 np.percentile(elev[land], 95), elev[land].max()))
        bodies = world_shape.components(list(water.astype(np.int8)), nb, wanted={1})
        sizes = sorted((len(c) for _, c in bodies), reverse=True)[:6]
        print("water bodies: %d, largest %s" % (len(bodies), sizes))
        # the check that matters for step 3: is there a downhill path off every peak?
        sinks = 0
        for i in range(n):
            if not water[i] and elev[i] <= elev[nb[i]].min():
                sinks += 1
        print("closed depressions on land: %d (step 3 fills these before routing)" % sinks)
    return elev.astype(np.float32), water, arc, bear, V, nb


# ---------------------------------------------------------------- the viewer
# No PIL and no matplotlib on this machine, and neither is worth installing for a
# picture. A PNG is four chunks and a zlib stream.

def write_png(path, rgb):
    h, w, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[y].tobytes() for y in range(h))

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c))

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 6))
           + chunk(b"IEND", b""))
    open(path, "wb").write(png)


# hypsometric ramp: metres -> rgb. Water reads as water, rock reads as rock.
RAMP = [(-400, (18, 34, 74)), (-120, (32, 62, 118)), (-1, (74, 118, 168)),
        (1, (206, 190, 140)), (250, (196, 172, 112)), (600, (176, 148, 92)),
        (1100, (154, 122, 78)), (1600, (140, 108, 84)), (2100, (128, 118, 112)),
        (2600, (150, 146, 144)), (3200, (180, 178, 178)), (4200, (208, 206, 206))]


def ramp(v):
    for (a, ca), (b, cb) in zip(RAMP[:-1], RAMP[1:]):
        if v < b:
            t = (v - a) / (b - a)
            t = max(0.0, min(1.0, t))
            return tuple(int(ca[k] + t * (cb[k] - ca[k])) for k in range(3))
    return RAMP[-1][1]


RENDER_ARC = 112.0        # past the terminator, so a sea on it is not cut in half
DISC_CACHE = os.path.join(REPO, "world", "discmap_%d.npz")


def disc_maps(V, size=520, pad=14):
    """The pixel -> tile index map for both hemispheres, cached.

    Split out so every later stage - rivers, rainfall, biomes - draws onto exactly
    the same projection without recomputing the nearest-tile search, which is the
    slow part of making a picture.
    """
    path = DISC_CACHE % size
    if os.path.exists(path):
        z = np.load(path)
        return (int(z["W"]), int(z["H"]),
                [(int(z["x0_%d" % k]), int(z["y0_%d" % k]),
                  z["inside_%d" % k], z["near_%d" % k]) for k in (0, 1)])
    W, H, R = size * 2 + pad * 3, size + pad * 2, size / 2.0
    out, store = [], {"W": W, "H": H}
    for k, sign in enumerate((1.0, -1.0)):
        ys, xs = np.mgrid[0:size, 0:size]
        dx, dy = (xs - R + 0.5) / R, (ys - R + 0.5) / R
        rr = np.hypot(dx, dy)
        inside = rr <= 1.0
        a = rr[inside] * RENDER_ARC
        b = np.degrees(np.arctan2(dy[inside], sign * dx[inside])) % 360.0
        if sign < 0:
            a = 180.0 - a
        P = to_vec(a, b)
        near = np.zeros(len(P), dtype=np.int32)
        for t in range(0, len(P), 4096):
            near[t:t + 4096] = np.argmax(P[t:t + 4096] @ V.T, axis=1)
        x0 = pad + k * (size + pad)
        out.append((x0, pad, inside, near))
        store["x0_%d" % k], store["y0_%d" % k] = x0, pad
        store["inside_%d" % k], store["near_%d" % k] = inside, near
    np.savez_compressed(path, **store)
    return W, H, out


def blank(W, H):
    img = np.zeros((H, W, 3), dtype=np.uint8)
    img[:, :] = (10, 10, 14)
    return img


def render(elev, water, V, nb, size=520, pad=14):
    """Two azimuthal-equidistant discs: dayside centred on the substellar point,
    nightside on the antistellar. Radius == arc angle, so the terminator is the rim
    of each disc - the only projection that tells the truth about a locked planet."""
    lut = np.array([ramp(v) for v in np.arange(-450, 4300, 5)], dtype=np.uint8)

    def col(v):
        return lut[np.clip(((v + 450) / 5).astype(int), 0, len(lut) - 1)]

    # relief shading from the graph: a tile above its neighbours catches the light
    mean_nb = np.array([elev[x].mean() for x in nb])
    # gain set for a DESERT: on a plain the whole relief signal is tens of metres,
    # and at 190 m/unit the plains rendered as flat paint.
    shade = np.clip((elev - mean_nb) / 62.0, -1.0, 1.0)

    W, H, discs = disc_maps(V, size, pad)
    img = blank(W, H)
    for x0, y0, inside, near in discs:
        c = col(elev[near]).astype(np.int16)
        c = np.clip(c + (shade[near] * 30).astype(np.int16)[:, None], 0, 255)
        c[water[near]] = col(elev[near][water[near]])   # no fake relief on water
        tile = np.zeros((size, size, 3), dtype=np.uint8)
        tile[:, :] = (10, 10, 14)
        tile[inside] = c.astype(np.uint8)
        img[y0:y0 + size, x0:x0 + size] = tile
    return img


def main():
    elev, water, arc, bear, V, nb = build()
    np.savez_compressed(OUT_NPZ, elev=elev, water=water, arc=arc, bear=bear)
    print("wrote", OUT_NPZ)
    if "--stats" not in sys.argv:
        write_png(OUT_PNG, render(elev, water, V, nb))
        print("wrote", OUT_PNG, "(left: dayside, centred on the substellar point;"
              " right: nightside. Disc rim == the terminator.)")


if __name__ == "__main__":
    main()
