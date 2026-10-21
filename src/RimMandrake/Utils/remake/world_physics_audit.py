#!/usr/bin/env python3
"""world_physics_audit.py — what the sun and the temperature SHOULD be on each Ash'karr tile.

Offline half of WORLD_PHYSICS_AUDIT_LOCKED_SUN_TEMPS_RINGS (2026-10-20). Live reads are
compared against these numbers; this file does not touch the game.

Per tile it computes, from engine-truth lat/long (`world/world_tiles_sub7b.csv`, a
`jawa/world_tile_export` dump) and the save's own tile arrays:

  arc        great-circle angle from the substellar point (lat 0, long 0)
  elev_geo   90 - arc: the geometric sun height. Our Direct Sun uses exactly this
             (RM_MapComponent_ShadeGrid -> RM_MapComponent_PinnedSun.SunGeometry, clamped
             per biome by min/maxElevationDegrees).
  glow_mod   CelestialSunGlow as 7f.alienworlds.tidallylocked's SunGlowPatch computes it
             when TidallyLocked is the ACTIVE planet type: a line-for-line port of that
             prefix plus vanilla GenCelestial.SunPosition / SunPositionUnmodified /
             SurfaceNormal (1.6). Time-independent by construction (dayOfYear 0,
             dayPercent 0.5 pinned). 🔴 It is NOT a clean cos(arc): vanilla's
             "sun peeks around" fudges are evaluated at signed LONGITUDE, so the west
             terminator (long -90) reads lit and the east one (+90) nearly dark.
  glow_geo   OUR replacement (RimMandrake.CreatureBehaviors RM_TidalSunGlowPatch, owner by card
             2026-10-20 "Light follows the sun"): a line-for-line port of RM_TidalSunGlowMath —
             0.6 + 0.4*min(1, sin(e)/sin 30°) for e > 0, a 12° smoothstep dusk band to 0.6 below
             the horizon, 0 beyond. What the game reads while the lock is active and the setting on.
  t_save     the tile's stored average temperature (what the game reads; daily swing is
             off under the tidal lock, the seasonal swing is NOT — see season_amp)
  t_intent   the owner's ruled curve on arc, [70,58,38,14,-22,-58,-80] at arc 0..180,
             minus 5.5 C/km above sea level (ashkarr_paint.temperature_curve)
  season_amp vanilla GenTemperature.SeasonalShiftAmplitudeAt under the tidal-lock def's
             seasonalTempVariationCurve (0:15, 1:15, 2:5) evaluated at
             DistanceFromEquatorNormalized (|lat|/90): 15 C on EVERY tile, sign by
             hemisphere. Under the Default planet it is vanilla's latitude curve.

    python3 src/RimMandrake/Utils/remake/world_physics_audit.py <save.rws> [--json out.json]
"""
import argparse
import csv
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(UTILS)))
sys.path.insert(0, UTILS)

D2R = math.pi / 180.0


# ---- minimal Unity vector maths -------------------------------------------------------
def norm(v):
    m = math.sqrt(sum(c * c for c in v))
    return tuple(c / m for c in v) if m else v


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def rot_axis(v, deg, axis):
    """Quaternion.AngleAxis(deg, axis) * v for axis 'y' (Vector3.up) or 'z'."""
    c, s = math.cos(deg * D2R), math.sin(deg * D2R)
    x, y, z = v
    if axis == "y":      # Unity left-handed: rotate about up
        return (c * x + s * z, y, -s * x + c * z)
    return (c * x - s * y, s * x + c * y, z)


def rotate_towards(cur, target, max_rad):
    """Vector3.RotateTowards for unit vectors with an unlimited magnitude delta."""
    cur, target = norm(cur), norm(target)
    ang = math.acos(max(-1.0, min(1.0, dot(cur, target))))
    if ang <= max_rad or ang < 1e-9:
        return target
    t = max_rad / ang
    s = math.sin(ang)
    a = math.sin((1 - t) * ang) / s
    b = math.sin(t * ang) / s
    return norm(tuple(a * c + b * d for c, d in zip(cur, target)))


def curve(x, pts):
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


PEEK = [(70.0, 1.0), (75.0, 0.05)]           # SunPeekAroundDegreesFactorCurve
OFFSET = [(70.0, 0.2), (75.0, 1.5)]          # SunOffsetFractionFromLatitudeCurve


def surface_normal(lat):
    return rot_axis((1.0, 0.0, 0.0), lat, "z")


def sun_position(lat):
    """GenCelestial.SunPosition(lat, dayOfYear 0, dayPercent 0.5) with the tidal-lock
    SunPositionPatch prefix pinning both."""
    v = [100.0, 0.0, 0.0]
    v[1] += -math.cos(0.0) * 100.0 * curve(lat, OFFSET)
    cur = norm(tuple(v))                          # AngleAxis(0) at dayPercent 0.5
    tgt = surface_normal(lat)
    cur = rotate_towards(cur, tgt, math.pi * 19 / 180 * curve(lat, PEEK))
    n2 = max(0.0, min(1.0, (60.0 - abs(lat)) / 60.0))
    if n2 > 0:
        cur = rotate_towards(cur, tgt, math.pi * 2 * (17 * n2 / 360))
    return norm(cur)


def glow_tidal(lat, lon):
    """SunGlowPatch.Prefix: longitude goes in where vanilla puts latitude, then the sun is
    rotated about up by latitude."""
    n = surface_normal(lon)
    rhs = norm(rot_axis(sun_position(lon), lat, "y"))
    return max(0.0, min(1.0, dot(norm(n), rhs) / 0.7))


DAY_THRESHOLD = 0.6        # GenCelestial.IsDaytime: glow > 0.6
FULL_DAY_ELEV = 30.0       # RM_TidalSunGlowMath.FullDayElevationDegrees
TWILIGHT_BAND = 12.0       # RM_TidalSunGlowMath.DefaultTwilightBandDegrees (owner, by card 2026-10-20: 12°)


def glow_geo(lat, lon, band=TWILIGHT_BAND):
    """RM_TidalSunGlowMath.GlowAt, ported line for line."""
    e = 90.0 - arc_deg(lat, lon)
    if e > 0:
        f = min(1.0, math.sin(e * D2R) / math.sin(FULL_DAY_ELEV * D2R))
        return DAY_THRESHOLD + (1 - DAY_THRESHOLD) * f
    if band <= 0 or e <= -band:
        return 0.0
    t = (e + band) / band
    return DAY_THRESHOLD * t * t * (3 - 2 * t)


def day_night_mismatch(tiles, glow):
    """(night-side tiles reading daytime, day-side tiles reading night) for a glow(lat, lon) function, over
    (lat, lon) pairs. Day side = arc < 90; daytime = glow > 0.6 (vanilla IsDaytime)."""
    lit_night = dark_day = 0
    for lat, lon in tiles:
        arc = arc_deg(lat, lon)
        g = glow(lat, lon)
        if arc > 90 and g > DAY_THRESHOLD:
            lit_night += 1
        elif arc < 90 and g <= DAY_THRESHOLD:
            dark_day += 1
    return lit_night, dark_day


def arc_deg(lat, lon):
    return math.degrees(math.acos(max(-1, min(1, math.cos(lon * D2R) * math.cos(lat * D2R)))))


def t_intent(arc, elev_m):
    pts = list(zip([0, 30, 60, 90, 120, 150, 180], [70.0, 58.0, 38.0, 14.0, -22.0, -58.0, -80.0]))
    return curve(arc, pts) - max(0.0, elev_m) / 1000.0 * 5.5


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("save")
    ap.add_argument("--tiles", default=os.path.join(REPO, "world", "world_tiles_sub7b.csv"))
    ap.add_argument("--json")
    a = ap.parse_args(argv)

    from worldmap import WorldGrid
    g = WorldGrid(a.save)
    unresolved = g.unresolved()
    names = g.biome_names()
    rows = list(csv.DictReader(open(a.tiles, encoding="utf-8")))
    if len(rows) != len(names):
        print(f"REFUSED: {len(rows)} geometry rows vs {len(names)} save tiles")
        return 2
    out = []
    for r in rows:
        t = int(r["tile"])
        lat, lon = float(r["lat"]), float(r["long"])
        arc = arc_deg(lat, lon)
        el = g.get("tileElevation", t)
        ts = g.get("tileTemperature", t)
        out.append(dict(tile=t, lat=lat, lon=lon, arc=round(arc, 2), elev_geo=round(90 - arc, 2),
                        glow_mod=round(glow_tidal(lat, lon), 3), glow_geo=round(glow_geo(lat, lon), 3), t_save=ts,
                        t_intent=round(t_intent(arc, el), 1), elev_m=el, biome=names[t]))
    for o in out:
        o["dT"] = round(o["t_save"] - o["t_intent"], 1)

    def nearest(lat, lon):
        return min(out, key=lambda o: math.acos(max(-1, min(1,
            math.sin(lat * D2R) * math.sin(o["lat"] * D2R) +
            math.cos(lat * D2R) * math.cos(o["lat"] * D2R) * math.cos((lon - o["lon"]) * D2R)))))

    probes = [("substellar", 0, 0), ("arc30 E", 0, 30), ("arc60 E", 0, 60), ("arc80 E", 0, 80),
              ("terminator E", 0, 90), ("terminator W", 0, -90), ("arc60 W", 0, -60),
              ("arc100 W", 0, -100), ("arc120 W", 0, -120), ("arc120 E", 0, 120),
              ("arc150", 0, 150), ("antistellar", 0, 180), ("N pole", 90, 0), ("S pole", -90, 0),
              ("lat45 lon45", 45, 45), ("lat-45 lon-135", -45, -135)]
    sample = []
    for label, la, lo in probes:
        o = dict(nearest(la, lo))
        o["probe"] = label
        sample.append(o)
    st = [o for o in out if o["tile"] == 17011]   # by tile id, never by row position
    if not st:
        print("REFUSED: start tile 17011 not in the geometry CSV")
        return 2
    start = dict(st[0]); start["probe"] = "start 17011"; sample.append(start)

    print(f"save tiles {len(out)}  unresolved biome hashes {len(unresolved)}")
    hdr = "probe          tile   lat    lon    arc  elevGeo glowMod glowGeo  tSave tIntent   dT biome"
    print(hdr)
    for o in sample:
        print(f"{o['probe']:<14}{o['tile']:>5} {o['lat']:6.1f} {o['lon']:6.1f} {o['arc']:6.1f} {o['elev_geo']:6.1f}"
              f"  {o['glow_mod']:5.2f}   {o['glow_geo']:5.2f} {o['t_save']:6.1f} {o['t_intent']:6.1f} {o['dT']:5.1f} {o['biome']}")

    # glow vs geometry, planet-wide
    lit_night = [o for o in out if o["arc"] > 90 and o["glow_mod"] > 0.6]
    dark_day = [o for o in out if o["arc"] < 90 and o["glow_mod"] <= 0.6]
    print(f"\nnight-side tiles (arc>90) the game calls DAYTIME (glow>0.6): {len(lit_night)}"
          f"  | day-side tiles (arc<90) it calls night: {len(dark_day)}")
    gn, gd = day_night_mismatch([(o["lat"], o["lon"]) for o in out], glow_geo)
    print(f"with RM_TidalSunGlowPatch (glowGeo): night-side reading DAYTIME {gn} | day-side reading night {gd}")

    # per-biome temperature vs intent
    by = {}
    for o in out:
        by.setdefault(o["biome"], []).append(o)
    print("\nbiome                      n   tSave med [min..max]   dT med  |dT|>5")
    flagged = []
    for b, L in sorted(by.items(), key=lambda kv: -len(kv[1])):
        ts = [o["t_save"] for o in L]
        dts = [o["dT"] for o in L]
        big = sum(1 for d in dts if abs(d) > 5)
        line = (f"{b:<25}{len(L):>5} {statistics.median(ts):7.1f} [{min(ts):6.1f}..{max(ts):6.1f}] "
                f"{statistics.median(dts):6.1f} {big:5d}")
        print(line)
        if big:
            flagged.append((b, len(L), big))
    if a.json:
        json.dump(dict(sample=sample, unresolved=unresolved, flagged=flagged,
                       lit_night=len(lit_night), dark_day=len(dark_day),
                       geo_lit_night=gn, geo_dark_day=gd), open(a.json, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
