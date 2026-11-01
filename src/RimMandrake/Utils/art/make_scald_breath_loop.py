#!/usr/bin/env python3
"""The boil's breath: synthesise RUT_ScaldBreath's loop (SCALD_STEAM_WEATHER_DESIGN_1 step 9).

Deterministic (fixed seed). Everything is built circularly (shaped noise by FFT, modulators on whole
cycles of the loop, bubbles wrapped round the end), so the clip's last sample meets its first and the
sustainer loops with no seam. Three layers: a low boil roll, a slow hiss that swells like breathing, and
sparse deep bubbles.

    python3 src/RimMandrake/Utils/art/make_scald_breath_loop.py <out.ogg>     (needs ffmpeg with libvorbis)
"""
import subprocess
import sys

import numpy as np

SR, SECONDS = 44100, 32
N = SR * SECONDS


def shaped(rng, lo, hi, tilt=0.0):
    """Stereo-independent periodic noise, band lo..hi Hz with soft skirts, tilted by f^tilt."""
    f = np.fft.rfftfreq(N, 1 / SR)
    gain = np.exp(-((np.log(np.maximum(f, 1) / np.sqrt(lo * hi)) / np.log(hi / lo)) ** 2) * 4)
    gain *= np.maximum(f, 1) ** tilt
    x = np.fft.irfft(gain * np.exp(2j * np.pi * rng.random(f.size)), N)
    return x / np.abs(x).max()


def swell(cycles, phase):
    """A 0..1 modulator with a whole number of cycles in the loop."""
    t = np.arange(N) / N
    return 0.5 + 0.5 * np.sin(2 * np.pi * cycles * t + phase)


def bubbles(rng, count):
    out = np.zeros(N)
    for _ in range(count):
        n = int(SR * rng.uniform(0.05, 0.16))
        at = rng.integers(N)
        f0 = rng.uniform(110, 340)
        t = np.arange(n) / SR
        b = np.sin(2 * np.pi * (f0 * t + 0.5 * f0 * 1.4 * t * t)) * np.exp(-t * rng.uniform(25, 55)) * rng.uniform(0.3, 1)
        out[(at + np.arange(n)) % N] += b
    return out / np.abs(out).max()


def channel(rng):
    roll = shaped(rng, 35, 180, -0.4) * (0.65 + 0.35 * swell(3, rng.uniform(0, 6)))
    breath = 0.45 + 0.55 * swell(4, rng.uniform(0, 1)) ** 2
    hiss = shaped(rng, 1800, 7000, -0.3) * breath * (0.8 + 0.2 * swell(23, rng.uniform(0, 6)))
    mid = shaped(rng, 300, 1200, -0.5) * breath
    return 0.62 * roll + 0.20 * hiss + 0.16 * mid + 0.16 * bubbles(rng, 26)


def main(out):
    rng = np.random.default_rng(20260925)
    common, left, right = channel(rng), channel(rng), channel(rng)
    st = np.stack([common + 0.55 * left, common + 0.55 * right], 1)
    st = st / np.abs(st).max() * 0.71  # -3 dBFS
    pcm = (st * 32767).astype("<i2").tobytes()
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", "-c:a", "libvorbis", "-q:a", "4", out], input=pcm, check=True)
    rms = float(np.sqrt((st ** 2).mean()))
    print(f"{out}: {SECONDS}s stereo, rms {rms:.3f}, seam jump {np.abs(st[0] - st[-1]).max():.4f}")


if __name__ == "__main__":
    main(sys.argv[1])
