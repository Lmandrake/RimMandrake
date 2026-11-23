#!/usr/bin/env python3
"""RIMMANDRAKE_INSTALL_TANK_SPRINKLER_PICKS_REDO_MODERN_PIPE_TOO_REPETITIVE: Modern pipe wear that does not repeat per cell.

Owner 2026-11-22: "The modern pipe mods look too repetitive, they need to be more organic and non-repeating."
The earlier repaints (LookOptions_2026-11-22/repaint_options.py pipe_atlas) painted wear INTO the linked atlas, so every
straight cell of a run carried the same marks. FlowWorks already draws a per-cell variant for straight cells when a look
ships a sheet beside its atlas (Machinery/PipeStraightVariants.cs: <look>/UniversalPipe_Straights, 4 columns, row 0
east-west, row 1 north-south, picked by a stable cell hash: atlas 3/8, v1 2/8, v2 1/8, v3 1/8, v4 1/8). So the fix is art
only: keep the atlas as shipped (clean) and put each kind of wear on ONE variant, at a different place along the cell.
Most cells stay clean; no mark recurs at a fixed period.

Every mark is painted inside the shown cell, MARGIN px clear of both ends, so each variant's ends equal the atlas straight
byte for byte and any mix joins exactly. The north-south row is built from the atlas's own north-south straight with the
coordinates transposed and its own seeds (so it is not a rotated copy of the east-west wear).

Generator-free (procedural on the shipped pixels): colour, tone and, for hardware, a small opaque band around the tube.

Usage: compose_modern_straights.py OUTDIR   writes pipe_modern_straights_{A,B,C}.png (704 x 352, the atlas's tile size)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ATLAS = HERE.parents[1] / "Textures/RimMandrake/FlowWorks/Pipe/Modern/UniversalPipe_Atlas.png"
NV = 4          # PipeStraightVariants.Count
MARGIN = 20     # px of each shown cell end left exactly as the atlas straight


def load_tiles():
    a = np.asarray(Image.open(ATLAS).convert("RGBA")).astype(np.float32) / 255
    T = a.shape[1] // 4

    def tile(i):                       # Graphic_Linked index i = link mask; atlas row 0 is the image's top
        col, r = i % 4, 3 - i // 4
        return a[r * T:(r + 1) * T, col * T:(col + 1) * T].copy()
    return tile(10), tile(5), T


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def noise1(n, sigma, rng):
    """A smooth 1-D noise in [-1, 1]."""
    v = rng.standard_normal(n + 8 * int(sigma) + 8)
    k = np.exp(-0.5 * (np.arange(-3 * sigma, 3 * sigma + 1) / max(sigma, 0.5)) ** 2)
    v = np.convolve(v, k / k.sum(), "same")[4 * int(sigma) + 4:][:n]
    return v / (np.abs(v).max() + 1e-9)


def noise2(shape, sigma, rng):
    from numpy.fft import fft2, ifft2, fftfreq
    w = rng.standard_normal(shape)
    fy, fx = fftfreq(shape[0])[:, None], fftfreq(shape[1])[None, :]
    g = np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2))
    f = np.real(ifft2(fft2(w) * g))
    f = (f - f.min()) / (f.max() - f.min() + 1e-9)
    return f


class Tile:
    """A straight tile in RUN coordinates: u along the pipe, v across it (-1..1 over the tube, |v|>1 off it).
    For the north-south tile the arrays are transposed in and out, so one painter serves both."""

    def __init__(self, base, T, ns):
        self.ns = ns
        b = base.transpose(1, 0, 2) if ns else base
        self.rgb = b[..., :3].copy()
        self.al = b[..., 3].copy()
        self.T = T
        self.P = T // 8
        rows = np.where(self.al[:, T // 2] > 0.5)[0]
        self.c0, self.c1 = rows[0], rows[-1]                       # tube rows
        self.mid = (self.c0 + self.c1) / 2
        self.rad = (self.c1 - self.c0 + 1) / 2
        yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
        self.u = xx
        self.v = (yy - self.mid) / self.rad
        self.tube = (np.abs(self.v) <= 1.0).astype(np.float32) * (self.al > 0.5)
        self.L = self.rgb @ np.array([0.299, 0.587, 0.114], np.float32)
        self.lo, self.hi = self.P + MARGIN, self.T - self.P - MARGIN      # where a mark may live

    def out(self):
        a = np.concatenate([np.clip(self.rgb, 0, 1), np.clip(self.al, 0, 1)[..., None]], -1)
        return a.transpose(1, 0, 2) if self.ns else a

    def guard(self, m):
        """Zero a mask outside the paintable span, softly over 4 px."""
        return m * smooth(self.u, self.lo, self.lo + 4) * (1 - smooth(self.u, self.hi - 4, self.hi))

    # ------------------------------------------------------------------ marks
    def drift(self, rng, amp=0.05):
        """A slow value/hue wander along the cell (within the paintable span): paint never reads perfectly even."""
        n = noise1(self.T, 14, rng)
        g = self.guard(np.ones_like(self.u)) * self.tube
        k = 1 + amp * n[self.u.astype(int)] * g
        self.rgb = self.rgb * k[..., None]

    def touchup(self, c, length, rng, paint=(0.30, 0.52, 0.66)):
        """A band of newer paint round the tube: a slightly different blue, ragged brush ends."""
        rows = np.clip(np.round((self.v + 1.5) * self.rad), 0, 63).astype(int)       # one brush-end offset per tube row
        left, right = noise1(64, 0.8, rng)[rows] * 1.2, noise1(64, 0.8, rng)[rows] * 1.2   # each end its own
        d = np.where(self.u < c, c - self.u + left, self.u - c + right)
        m = smooth(length / 2 - d, -0.8, 0.8) * self.tube
        m = self.guard(m)
        shade = (self.L / (np.median(self.L[self.tube > 0]) + 1e-6))[..., None]
        fresh = np.array(paint, np.float32) * shade
        m = m * 0.85
        self.rgb = self.rgb * (1 - m[..., None]) + fresh * m[..., None]

    def chips(self, c, span, n, rng, rust=0.0):
        """A cluster of paint chips showing grey galvanised steel, a dark rim; optional rust in the larger ones."""
        for _ in range(n):
            cu = c + rng.uniform(-span / 2, span / 2)
            cv = rng.uniform(-0.85, 0.85)
            ru, rv = rng.uniform(1.2, 4.5), rng.uniform(0.10, 0.22)
            d = np.sqrt(((self.u - cu) / ru) ** 2 + ((self.v - cv) / rv) ** 2)
            core = smooth(1.0 - d, 0, 0.5) * self.tube * 0.85
            rim = smooth(1.5 - d, 0, 0.5) * (1 - core) * self.tube
            core, rim = self.guard(core), self.guard(rim)
            metal = (0.30 + 0.55 * self.L)[..., None] * np.array([0.78, 0.79, 0.80], np.float32)
            if rust and ru > 2.4:
                metal = metal * (1 - rust) + rust * np.array([0.55, 0.33, 0.18], np.float32) * (0.6 + 0.6 * self.L)[..., None]
            self.rgb = self.rgb * (1 - rim[..., None] * 0.18)
            self.rgb = self.rgb * (1 - core[..., None]) + metal * core[..., None]

    def grime(self, c, length, rng, side=1, strength=0.6, col=(0.60, 0.50, 0.38)):
        """Dust and dirt banked on one side of the tube, soft along the run, mottled."""
        wob = noise1(64, 1.5, rng)[np.clip(np.round((self.v + 1.5) * self.rad), 0, 63).astype(int)] * length * 0.18
        along = smooth(length / 2 + wob - np.abs(self.u - c), 0, length * 0.3)
        across = smooth(side * self.v, -0.7, 0.6)
        mott = noise2((self.T, self.T), 1.6, rng)
        m = self.guard(along * across * (0.45 + 0.75 * mott) * self.tube) * strength
        dirt = np.array(col, np.float32) * (0.80 + 0.35 * self.L)[..., None]
        self.rgb = self.rgb * (1 - m[..., None]) + dirt * m[..., None]

    def fade(self, c, length, strength=0.5):
        """A sun-faded stretch: lighter, greyer paint on the lit (north) half, soft ends."""
        along = smooth(length / 2 - np.abs(self.u - c), 0, length * 0.4)
        m = self.guard(along * smooth(-self.v, -0.6, 0.7) * self.tube) * strength
        grey = (self.L * 0.9 + 0.12)[..., None] * np.array([0.93, 0.97, 1.0], np.float32)
        self.rgb = self.rgb * (1 - m[..., None]) + grey * m[..., None]

    def rust(self, c, rng, r=3.5, col=(0.47, 0.29, 0.16)):
        """A small rust bloom where the paint broke: an irregular brown blot, darker at its heart, soft edge."""
        cv = rng.uniform(-0.5, 0.5)
        d = np.sqrt((self.u - c) ** 2 + ((self.v - cv) * self.rad * 1.3) ** 2)
        wob = noise2((self.T, self.T), 1.2, rng) * 2.0
        m = smooth(r + wob - d, 0, 1.8) * self.tube
        heart = smooth(r * 0.45 + wob * 0.5 - d, 0, 1.2) * self.tube
        m, heart = self.guard(m) * 0.8, self.guard(heart)
        stain = np.array(col, np.float32) * (0.65 + 0.5 * self.L)[..., None]
        self.rgb = self.rgb * (1 - m[..., None]) + stain * m[..., None]
        self.rgb = self.rgb * (1 - 0.3 * heart[..., None])

    def clamp(self, c, width=6, ear=4, bolts=True):
        """A galvanised strap clamp holding the pipe down: a band round the tube with a bolted foot on each side."""
        band = (np.abs(self.u - c) <= width / 2)
        reach = 1 + ear / self.rad
        body = band & (np.abs(self.v) <= reach)
        foot = (np.abs(self.u - c) <= width / 2 + 2) & (np.abs(self.v) > 1.0) & (np.abs(self.v) <= reach)
        m = (body | foot).astype(np.float32)
        m = self.guard(m)
        # shading: the band is a cylinder over the tube (lit from the north), flat on the feet
        cyl = np.where(np.abs(self.v) <= 1.0, 0.62 + 0.34 * np.cos(np.clip(self.v + 0.35, -1.6, 1.6)), 0.58)
        edge = (np.abs(np.abs(self.u - c) - width / 2) < 0.8).astype(np.float32) * 0.22
        steel = (cyl - edge)[..., None] * np.array([0.60, 0.62, 0.64], np.float32)
        if bolts:
            for s in (-1, 1):
                bv = s * (1 + ear / 2 / self.rad)
                d = np.sqrt((self.u - c) ** 2 + ((self.v - bv) * self.rad) ** 2)
                b = smooth(1.6 - d, 0, 0.6)
                steel = steel * (1 - b[..., None] * 0.55)
        self.rgb = self.rgb * (1 - m[..., None]) + steel * m[..., None]
        self.al = np.maximum(self.al, m)

    def coupling(self, c, width=9, lip=2):
        """A pipe coupling: a slightly wider collar in the pipe's blue, two raised ridges."""
        reach = 1 + lip / self.rad
        m = ((np.abs(self.u - c) <= width / 2) & (np.abs(self.v) <= reach)).astype(np.float32)
        m = self.guard(m)
        cyl = 0.55 + 0.38 * np.cos(np.clip(self.v / reach + 0.35, -1.6, 1.6))
        ridge = (np.abs(np.abs(self.u - c) - (width / 2 - 1.5)) < 0.9).astype(np.float32) * 0.18
        col = (cyl + ridge)[..., None] * np.array([0.42, 0.62, 0.80], np.float32)
        self.rgb = self.rgb * (1 - m[..., None]) + col * m[..., None]
        self.al = np.maximum(self.al, m)


def build(option, seed=0):
    ew, ns, T = load_tiles()
    sheet = np.zeros((2 * T, NV * T, 4), np.float32)
    for row, (base, is_ns) in enumerate(((ew, False), (ns, True))):
        for k in range(1, NV + 1):
            rng = np.random.default_rng(1000 * (ord(option) - 64) + 100 * row + k + seed)
            t = Tile(base, T, is_ns)
            span = (t.lo + 6, t.hi - 6)
            pos = lambda: rng.uniform(*span)                                # noqa: E731
            side = rng.choice([-1, 1])
            t.drift(rng)
            if option == "A":        # dusty, mostly clean: v1 (2/8) a faint dust bank; v2-v4 (3/8) one mark each
                if k == 1: t.grime(pos(), rng.uniform(60, 90), rng, side=side, strength=0.35)
                if k == 2: t.chips(pos(), rng.uniform(8, 16), int(rng.integers(3, 6)), rng)
                if k == 3: t.touchup(pos(), rng.uniform(12, 20), rng)
                if k == 4:
                    t.fade(pos(), rng.uniform(50, 80), strength=0.45); t.grime(pos(), rng.uniform(30, 50), rng, side=side, strength=0.6)
            elif option == "B":      # sun and grime: every variant marked, each differently; the atlas straight stays clean (3/8)
                if k == 1:
                    t.fade(pos(), rng.uniform(60, 90), strength=0.7); t.grime(pos(), 60, rng, side=side, strength=0.7)
                if k == 2:
                    t.touchup(pos(), rng.uniform(16, 26), rng); t.grime(pos(), 70, rng, side=side, strength=0.75)
                if k == 3:
                    c = pos(); t.chips(c, 14, 5, rng, rust=0.6); t.rust(c + rng.uniform(-4, 4), rng)
                    t.grime(pos(), 60, rng, side=side, strength=0.6)
                if k == 4:
                    t.grime(pos(), rng.uniform(70, 90), rng, side=side, strength=0.95); t.chips(pos(), 8, 3, rng)
            elif option == "C":      # fittings: a strap clamp (1/8) and a coupling (1/8) among light wear
                if k == 1: t.grime(pos(), rng.uniform(60, 90), rng, side=side, strength=0.35)
                if k == 2: t.chips(pos(), rng.uniform(8, 14), int(rng.integers(3, 5)), rng)
                if k == 3:
                    c = pos(); t.clamp(c); t.grime(c + 8 * side, 30, rng, side=side, strength=0.5)
                if k == 4: t.coupling(pos())
            sheet[row * T:(row + 1) * T, (k - 1) * T:k * T] = t.out()
    return sheet, ew, ns, T


def seam_report(sheet, ew, ns, T):
    """Max abs difference between each variant's end strips and the atlas straight's (must be 0)."""
    P = T // 8
    worst = 0.0
    for row, base in enumerate((ew, ns)):
        for k in range(NV):
            v = sheet[row * T:(row + 1) * T, k * T:(k + 1) * T]
            if row == 0:
                ends = [np.s_[:, :P + MARGIN], np.s_[:, T - P - MARGIN:]]
            else:
                ends = [np.s_[:P + MARGIN, :], np.s_[T - P - MARGIN:, :]]
            for e in ends:
                worst = max(worst, float(np.abs(v[e] - base[e]).max()))
    return worst


def main(argv):
    out = Path(argv[1]); out.mkdir(parents=True, exist_ok=True)
    for opt in "ABC":
        sheet, ew, ns, T = build(opt)
        w = seam_report(sheet, ew, ns, T)
        assert w < 1e-6, f"option {opt}: variant ends differ from the atlas straight by {w}"
        p = out / f"pipe_modern_straights_{opt}.png"
        Image.fromarray((np.clip(sheet, 0, 1) * 255 + 0.5).astype(np.uint8)).save(p)
        print("wrote", p, "seam max diff", w)


if __name__ == "__main__":
    main(sys.argv)
