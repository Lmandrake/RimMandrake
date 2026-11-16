#!/usr/bin/env python3
"""Offline sweep of pole-wire wind sway (RIMMANDRAKE_CLEAN_SLACK_SWAY_POLE_WIRES_ONLY_NOT_CONDUIT, owner 2026-11-16:
"They look like they're swaying, though it's not a great effect. They're too stiff.").

Top-down RimWorld fakes height as +z on screen, so a span hanging sag S below its chord is drawn S x Droop(t) screen-down
(AerialMath.SpanCurve). A hanging wire in wind swings like a pendulum about its chord: at swing angle theta its belly is
d sin(theta) to the side (ground-plane normal n) and d cos(theta) below the chord, d = S x Droop(t). Families:

  today     AerialMath.Sway as shipped: one shape (Droop) x one scalar, 0.12 cells whatever the span, w 1.1-1.6 rad/s,
            each strand its own random frequency and phase.
  pendulum  the sag swings about the chord (side AND rise), theta = A(wind) x gust x sin(w t + phase), w from the sag
            (longer, slacker spans swing slower), strands of a span share w, each lagging the last by a fixed phase.
  rope      pendulum plus a second, S-shaped lateral mode (twice the frequency, a quarter of the swing), so the belly
            wanders along the span instead of the whole sag moving as one rigid shape.
  gust      pendulum whose swing travels along the span (phase grows with t), plus a steady lean downwind that grows
            with the wind, so a storm holds the wires blown out and they shiver about that lean.

Every family is 0 at both attachment points (Droop(0) = Droop(1) = 0, ends written exactly). Gusts: amplitude follows the
game's wind speed (clamped 0..2.5) times a map-wide gust envelope that drifts across the map (span midpoint x, z).

    python3 tools/pole_sway_sweep.py --out <dir>      # metrics.json, sheet_<wind>.png, strip_<cand>_<span>_<wind>.gif
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw

SAG = 0.06                       # AerialSettings.sag default
SPANS = {"short": 5.0, "medium": 10.0, "long": 18.0}
WINDS = {"calm": 0.15, "breezy": 0.9, "storm": 2.2}
STRANDS = (-0.22, 0.0, 0.22)     # insulator offsets across the span (three-insulator crossarm), cells
SAGMUL = (0.95, 1.05, 1.12)      # AerialMath.SpanStrands: SagMul = 0.9 + 0.25 U


def droop(t):
    s = np.sin(np.pi * t)
    return np.where((t <= 0) | (t >= 1), 0.0, s * s)


def gust(time, mx, mz):
    """Map-wide gust envelope 0.6..1.0, a slow front drifting across the map (two incommensurate sines)."""
    u = 0.21 * time - 0.015 * mx - 0.011 * mz
    return 0.8 + 0.12 * math.sin(2 * math.pi * u) + 0.08 * math.sin(2 * math.pi * 1.7 * u + 1.3)


def wind_amp(wind, deg_breezy):
    """Swing amplitude (rad) for a wind speed: 0 at calm 0, deg_breezy at 0.9, sub-linear above (storm ~1.6x breezy)."""
    w = min(max(wind, 0.0), 2.5)
    return math.radians(deg_breezy) * (w / 0.9) ** 0.6 if w > 0 else 0.0


def omega(sag, t0):
    """Pendulum: period grows with sqrt(sag); t0 = period of a 10-cell span at default sag (0.6 cells)."""
    return 2 * math.pi / (t0 * math.sqrt(max(sag, 0.05) / 0.6))


def offsets(fam, t, time, wind, sag, si, seed, mid, p):
    """(lateral, rise) per sample t for one strand; lateral along the span normal, rise toward the chord (screen +z)."""
    d = sag * droop(t)
    if fam == "today":
        rng = np.random.default_rng(seed + si * 977)
        w = 1.1 + 0.5 * rng.random()
        ph, ph2 = 2 * math.pi * rng.random(), 2 * math.pi * rng.random()
        wave = math.sin(w * time + ph) + 0.3 * math.sin(2.3 * w * time + ph2)
        return 0.12 * min(wind, 1.5) / 1.5 * droop(t) * wave, np.zeros_like(t)
    a = wind_amp(wind, p["deg"]) * gust(time, *mid)
    w = omega(sag, p["t0"])
    ph = (seed % 628) / 100.0 + si * p["lag"]
    if fam == "pendulum":
        th = a * math.sin(w * time + ph) * np.ones_like(t)
        lat2 = 0.0
    elif fam == "rope":
        th = a * math.sin(w * time + ph) * np.ones_like(t)
        mode2 = np.sin(2 * np.pi * t) * np.sin(np.pi * t)          # S-shape, 0 with zero slope at both ends
        lat2 = 0.25 * a * sag * 1.3 * mode2 * math.sin(2.1 * w * time + 1.7 * ph + 0.9)
    else:  # gust
        lean = 0.55 * wind_amp(wind, p["deg"]) * min(wind, 2.5) / 2.5 * 2.0
        th = lean + 0.7 * a * np.sin(w * time + ph - p["k"] * t)
        lat2 = 0.0
    return d * np.sin(th) + lat2, d * (1 - np.cos(th))


def strand_points_diag(fam, L, wind, time, si, p, ang=math.radians(35), seed=12345, mid=(60.0, 60.0)):
    """The same strand on a span at angle ang: lateral along the ground normal n, sag and rise along screen z."""
    n = max(9, int(L / 0.5) + 1)
    t = np.linspace(0, 1, n)
    sag = SAG * L * SAGMUL[si]
    lat, rise = offsets(fam, t, time, wind, sag, si, seed, mid, p)
    dx, dz = math.cos(ang), math.sin(ang)
    nx, nz = -dz, dx
    x = t * L * dx + nx * (STRANDS[si] + lat)
    z = t * L * dz + nz * (STRANDS[si] + lat) - sag * droop(t) + rise
    return x, z


def filmstrip(cands, L, wind, path, frames=8, scale=34):
    pw, ph = int(L * 0.82 * scale) + 40, int(L * 0.57 * scale) + 50
    img = Image.new("RGB", (pw * frames + 170, ph * len(cands) + 20), (214, 196, 160))
    d = ImageDraw.Draw(img)
    for r, (name, fam, q) in enumerate(cands):
        d.text((5, 20 + r * ph + ph // 2), name, fill="black")
        T = 2 * math.pi / omega(SAG * L, q.get("t0", 2.4)) if fam != "today" else 4.5
        for f in range(frames):
            ox, oy = 170 + f * pw + 20, 20 + r * ph + ph - 25
            for si in range(3):
                x, z = strand_points_diag(fam, L, 0.0, 0.0, si, q)
                d.line([(ox + a * scale, oy - b * scale) for a, b in zip(x, z)], fill=(185, 170, 140), width=1)
            for si in range(3):
                x, z = strand_points_diag(fam, L, wind, 3.0 + f * T / frames, si, q)
                d.line([(ox + a * scale, oy - b * scale) for a, b in zip(x, z)], fill=(25, 25, 25), width=2)
    img.save(path)


def strand_points(fam, L, wind, time, si, p, seed=12345, mid=(60.0, 60.0)):
    n = max(9, int(L / 0.5) + 1)
    t = np.linspace(0, 1, n)
    sag = SAG * L * SAGMUL[si]
    lat, rise = offsets(fam, t, time, wind, sag, si, seed, mid, p)
    x = t * L
    z = STRANDS[si] - sag * droop(t) + rise
    z = z + lat          # an east-west span: its ground normal n is +z on screen
    x[0], z[0], x[-1], z[-1] = 0.0, STRANDS[si], L, STRANDS[si]
    return x, z, sag


def metrics(fam, p):
    out = {}
    for sn, L in SPANS.items():
        for wn, wv in WINDS.items():
            ts = np.arange(0, 20, 1 / 30)
            mids, ends, lags, cross = [], 0.0, [], 0
            for time in ts:
                pts = [strand_points(fam, L, wv, time, si, p) for si in range(3)]
                for si, (x, z, sag) in enumerate(pts):
                    ends = max(ends, abs(z[0] - STRANDS[si]), abs(z[-1] - STRANDS[si]), abs(x[0]), abs(x[-1] - L))
                x0, z0, sag0 = strand_points(fam, L, 0.0, time, 1, p)
                zb = pts[1][1][len(pts[1][1]) // 2]
                mids.append(zb - z0[len(z0) // 2])
                cross += int(np.any(pts[0][1] > pts[1][1]) or np.any(pts[1][1] > pts[2][1]))
            m = np.array(mids)
            # dominant period of the belly motion (zero crossings of its mean-removed series)
            mm = m - m.mean()
            zc = np.where(np.diff(np.sign(mm)) != 0)[0]
            period = 2 * 20 / len(zc) if len(zc) > 1 else None
            out[f"{sn}/{wn}"] = {"belly_peak": round(float(np.abs(m).max()), 3), "belly_range": round(float(m.max() - m.min()), 3),
                                 "period_s": round(period, 2) if period else None, "end_error": float(ends),
                                 "strand_crossing_frames": cross, "sag": round(SAG * L, 3)}
    return out


def draw_panel(img, ox, oy, fam, L, wind, p, scale, frames=10):
    d = ImageDraw.Draw(img)
    T = 2 * math.pi / omega(SAG * L, p.get("t0", 2.4)) if fam != "today" else 4.5
    for si in range(3):
        x, z, _ = strand_points(fam, L, 0.0, 0.0, si, p)
        d.line([(ox + xx * scale, oy - zz * scale) for xx, zz in zip(x, z)], fill=(200, 200, 200), width=1)
    for f in range(frames):
        time = 3.0 + f * T / frames
        c = (int(40 + 200 * f / frames), 60, int(240 - 200 * f / frames))
        for si in range(3):
            x, z, _ = strand_points(fam, L, wind, time, si, p)
            d.line([(ox + xx * scale, oy - zz * scale) for xx, zz in zip(x, z)], fill=c, width=1)
    d.ellipse([ox - 3, oy - 3, ox + 3, oy + 3], fill=(0, 0, 0)); d.ellipse([ox + L * scale - 3, oy - 3, ox + L * scale + 3, oy + 3], fill=(0, 0, 0))


def sheet(cands, wind, path, scale=26):
    cw, ch = int(19 * scale) + 40, int(3.0 * scale) + 30
    img = Image.new("RGB", (cw * len(SPANS) // 2 + 200, ch * len(cands) + 30), "white")
    img = Image.new("RGB", (int(sum(SPANS.values()) * scale) + 200, ch * len(cands) + 30), "white")
    d = ImageDraw.Draw(img)
    d.text((5, 5), f"wind {wind} ({path.split('_')[-1][:-4]}): grey = rest, blue->red = one period", fill="black")
    for r, (name, fam, p) in enumerate(cands):
        y = 30 + r * ch + int(1.6 * scale)
        d.text((5, y - 10), name[:24], fill="black")
        x = 190
        for L in SPANS.values():
            draw_panel(img, x, y, fam, L, wind, p, scale)
            x += int(L * scale) + 10
    img.save(path)


def strip(fam, p, L, wind, path, scale=30, fps=20, secs=6):
    frames = []
    for f in range(fps * secs):
        im = Image.new("RGB", (int(L * scale) + 30, int(2.6 * scale) + 20), (214, 196, 160))
        d = ImageDraw.Draw(im)
        oy = int(1.0 * scale) + 10
        for si in range(3):
            x, z, _ = strand_points(fam, L, wind, f / fps, si, p)
            d.line([(15 + xx * scale, oy - zz * scale) for xx, zz in zip(x, z)], fill=(30, 30, 30), width=2)
        d.rectangle([12, oy - 9, 18, oy + 9], fill=(90, 60, 30)); d.rectangle([12 + L * scale, oy - 9, 18 + L * scale, oy + 9], fill=(90, 60, 30))
        frames.append(im)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0)


CANDIDATES = [("today", "today", {})]
for fam in ("pendulum", "rope", "gust"):
    for deg in (14, 22, 32):
        for t0 in (1.8, 2.6):
            CANDIDATES.append((f"{fam} {deg}deg T{t0}", fam, {"deg": deg, "t0": t0, "lag": 0.15, "k": 2.2}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pick", nargs="*", default=[], help="candidate names to render as gifs")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {name: metrics(fam, p) for name, fam, p in CANDIDATES}
    json.dump(res, open(os.path.join(a.out, "metrics.json"), "w"), indent=1)
    for wn, wv in WINDS.items():
        sheet(CANDIDATES, wv, os.path.join(a.out, f"sheet_{wn}.png"))
    picks = [c for c in CANDIDATES if c[0] in a.pick or c[0] == "today"]
    for sn, L in SPANS.items():
        for wn, wv in WINDS.items():
            filmstrip(picks, L, wv, os.path.join(a.out, f"film_{sn}_{wn}.png"))
    for name in a.pick:
        fam, p = next((f, q) for n, f, q in CANDIDATES if n == name)
        for sn, L in SPANS.items():
            for wn, wv in WINDS.items():
                strip(fam, p, L, wv, os.path.join(a.out, f"strip_{name.replace(' ', '_')}_{sn}_{wn}.gif"))
    print(os.path.join(a.out, "metrics.json"))


if __name__ == "__main__":
    main()
