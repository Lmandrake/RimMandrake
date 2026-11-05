#!/usr/bin/env python3
"""Regenerate spike_parity_golden.json (SPIKES_PARITY_FIX_FLOAT32_MIRROR): the C# RM_SpikeDrawMath outputs, as float32
bits, over a sweep of FloorRect / SubmergedAlpha / Layout cases, for selftest_spike_float32_parity.py to hold the Python
mirror (fw_scenes_spikes.py) to bit for bit.

Needs Windows dotnet.exe (WSL on archmagi): the cases are written here, Harness/ plus the production sources are
copied to <agent storage>/rimmandrake/build/spike_parity (dotnet.exe cannot build from a \\\\wsl path), built and run
there. Re-run whenever RM_SpikeDrawMath.cs, RM_SpikeStakes.cs, RM_WallFaceMath.cs, RM_Volume.cs or RM_StockMath.cs changes: the selftest
refuses a golden whose source hash no longer matches.

The Layout sweep holds: every distinct FloorRect rect x 3 variants x 2 seeds; rects on the wall-table values and their
float32 neighbours; random rects; and every rect of a seeded search where the pre-fix double mirror (f64_mirror.py)
and the float32 mirror disagree on WHICH stakes are kept (a threshold decision: cap, lo/hi, bot, cellTop).

    python3 gen_golden.py            # writes ../spike_parity_golden.json
"""
import hashlib
import itertools
import json
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
FW = TOOLS.parent
REPO = FW.parents[2]
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(HERE))
import fw_scenes_spikes as spk  # noqa: E402
from f64_mirror import layout_f64  # noqa: E402

SOURCES = ("Source/Superdeep/RM_SpikeDrawMath.cs", "Source/Superdeep/RM_SpikeStakes.cs", "Source/RM_WallFaceMath.cs",
           "Source/RM_Volume.cs", "Source/RM_StockMath.cs")
GOLDEN = TOOLS / "spike_parity_golden.json"
SEEDS = (0, 1, 7, 42, 12345, -3)


def source_sha():
    h = hashlib.sha256()
    for s in SOURCES:
        h.update(s.encode() + b"\0" + (FW / s).read_bytes().replace(b"\r\n", b"\n") + b"\0")   # CRLF-proof
    return h.hexdigest()


def bits(f):
    return "%08x" % int(np.float32(f).view(np.uint32))


def unbits(hx):
    return float(np.uint32(int(hx, 16)).view(np.float32))


def floor_cases():
    for d in range(1, 7):
        for n, s, w, e in itertools.product(range(0, 8), repeat=4):
            for faces, outline in ((1, 1), (1, 0), (0, 0)):
                yield d, n, s, w, e, faces, outline


def decision_key(q):
    """Which stakes a layout keeps, independent of low-bit position noise: the count and each stake's UV box."""
    return len(q), sorted(tuple(round(v, 4) for v in st[4:8]) for st in q)


def slots(v, seed):
    """(r, zb, xc, w) of every grid slot of variant v at scale 1, in float32 as Layout computes them."""
    F = np.float32
    lib, (ppx, ppz) = spk.library(v)
    hmax = max(F(s[1]) for s in lib)
    span = max(F(0), F(1) - hmax * F(0.5))
    nrow = max(1, int(np.floor(float(span / F(ppz)))) + 1)
    q = float(F(1) / F(ppx))
    ncol = max(1, int(np.floor(q)) + (1 if q - np.floor(q) >= 0.5 else 0))
    rpz, rpx = (span / F(nrow - 1) if nrow > 1 else F(0)), F(1) / F(ncol)
    for r in range(nrow):
        for col in range(ncol + 1 if r & 1 else ncol):
            k = r * (ncol + 1) + col
            h = spk.hash32(seed, k)
            w = F(lib[h % len(lib)][0])
            jz = (F((h >> 16) & 0xFF) / F(255) - F(0.5)) * F(0.5) * rpz
            yield r, F(r) * rpz + jz, (F(col) if r & 1 else F(col) + F(0.5)) * rpx, w, hmax, rpz


def boundary_rects():
    F, M = np.float32, np.float32(spk.MARGIN)

    def around(f, n=3):
        out, lo, hi = [f], f, f
        for _ in range(n):
            lo, hi = np.nextafter(lo, F(-9)), np.nextafter(hi, F(9))
            out += [lo, hi]
        return out
    base = (F(0.04), F(0.045), F(0.96), F(0.62))
    for v in range(3):
        for seed in SEEDS:
            for r, zb, xc, w, hmax, rpz in slots(v, seed):
                x0, z0, x1, z1 = base
                for z1c in around(zb + M + hmax * F(0.5) - F(0.5) * rpz):          # cap
                    if F(0.3) < z1c < F(1):
                        yield v, seed, [float(x0), float(z0), float(x1), float(z1c)]
                if r > 0:
                    for z0c in around(zb - M):                                          # bot
                        if F(0) <= z0c < F(0.45):
                            yield v, seed, [float(x0), float(z0c), float(x1), float(z1)]
                for x0c in around(xc + w * F(0.5) - M):                                 # lo
                    if F(0) <= x0c < F(0.45):
                        yield v, seed, [float(x0c), float(z0), float(x1), float(z1)]
                for x1c in around(xc - w * F(0.5) + M):                                 # hi
                    if F(0.55) < x1c <= F(1):
                        yield v, seed, [float(x0), float(z0), float(x1c), float(z1)]
            for z1c in around(F(1) - F(1e-4), 6):                                       # cellTop
                yield v, seed, [float(x0), float(z0), float(x1), float(z1c)]


def layout_cases():
    rects = set()
    for d, n, s, w, e, faces, outline in floor_cases():
        rects.add(tuple(bits(v) for v in spk.floor_rect(d, n, s, w, e, bool(faces), bool(outline))))
    cases = [(v, seed) + r for r in sorted(rects) for v in range(3) for seed in SEEDS[2:4]]
    # the wall-table values (FloorRect's edges) and their float32 neighbours, one ulp either side
    edges = sorted({0.0, 0.04, 0.045, 0.055, 0.065, 0.08, 0.06, 0.11, 0.17, 0.23, 0.29, 0.12, 0.35, 0.5, 0.62})
    near = []
    for e in edges:
        f = np.float32(e)
        near += [np.nextafter(f, np.float32(-1)), f, np.nextafter(f, np.float32(2))]
    near = [f for f in near if f >= 0]
    rnd = random.Random(20261105)
    for _ in range(600):
        a, b = rnd.choice(near), rnd.choice(near)
        c, d = np.float32(1) - rnd.choice(near), np.float32(1) - rnd.choice(near)
        cases.append((rnd.randrange(3), rnd.choice(SEEDS), bits(a), bits(b), bits(c), bits(d)))
    for _ in range(600):
        x0, z0 = rnd.uniform(0, 0.45), rnd.uniform(0, 0.45)
        cases.append((rnd.randrange(3), rnd.randrange(-50, 50000), bits(x0), bits(z0), bits(rnd.uniform(0.5, 1)),
                      bits(rnd.uniform(0.5, 1))))
    # the threshold search: rects built so a stake's base or edge lands within a few ulps of cap / bot / lo / hi, and
    # the rect top within a few ulps of cellTop's 1 - Margin - 1e-4; kept where doubles and float32 keep different stakes
    split = 0
    for v, seed, r in boundary_rects():
        a = spk.layout(v, seed, *r)
        b = layout_f64(v, seed, *r, spk.library(v), spk.MARGIN, spk.hash32)
        if decision_key(a) != decision_key(b):
            cases.append((v, seed) + tuple(bits(x) for x in r))
            split += 1
    return cases, split


def run_harness(lines):
    storage = subprocess.run([sys.executable, str(Path.home() / "dev/Lodestar/bin/lib/agent_storage.py")],
                             capture_output=True, text=True, check=True).stdout.strip()
    build = Path(storage) / "rimmandrake" / "build" / "spike_parity"
    if build.exists():
        shutil.rmtree(build)
    (build / "src").mkdir(parents=True)
    for f in ("Harness.cs", "Harness.csproj"):
        shutil.copy(HERE / f, build / f)
    for s in SOURCES:
        shutil.copy(FW / s, build / "src" / Path(s).name)
    (build / "cases.txt").write_text("\n".join(lines) + "\n")
    dotnet = os.environ.get("WINBUILD_DOTNET") or next(iter(sorted(Path("/mnt/c/Users").glob("*/.dotnet/dotnet.exe"))), None)
    if not dotnet:
        raise SystemExit("gen_golden: no dotnet.exe (set WINBUILD_DOTNET)")
    win = subprocess.run(["wslpath", "-w", str(build)], capture_output=True, text=True, check=True).stdout.strip()
    r = subprocess.run([str(dotnet), "run", "-c", "Release", "--project", win + "\\Harness.csproj", "--",
                        win + "\\cases.txt", win + "\\out.txt"], capture_output=True, text=True, timeout=500)
    if r.returncode:
        raise SystemExit("gen_golden: harness failed (%d)\n%s\n%s" % (r.returncode, r.stdout[-3000:], r.stderr[-3000:]))
    return (build / "out.txt").read_text().splitlines()


def main():
    fcases = list(floor_cases())
    lcases, split = layout_cases()
    alpha = list(range(-1, 7))
    lines = (["F %d %d %d %d %d %d %d" % c for c in fcases] + ["A %d" % f for f in alpha]
             + ["L %d %d %s %s %s %s" % c for c in lcases])
    out = run_harness(lines)
    if len(out) != len(lines):
        raise SystemExit("gen_golden: %d outputs for %d cases" % (len(out), len(lines)))
    fo, ao, lo = out[:len(fcases)], out[len(fcases):len(fcases) + len(alpha)], out[len(fcases) + len(alpha):]
    golden = {
        "item": "SPIKES_PARITY_FIX_FLOAT32_MIRROR",
        "made_by": "src/RimMandrake/FlowWorks/Tools/spike_parity/gen_golden.py (dotnet.exe net8 x64, Release)",
        "source_sha256": source_sha(),
        "floor_rect": {"cases": len(fcases), "sha256": hashlib.sha256("\n".join(fo).encode()).hexdigest()},
        "submerged_alpha": [[f, o] for f, o in zip(alpha, ao)],
        "threshold_split_cases": split,
        # per case: variant, seed, x0 z0 x1 z1 (float32 bits), C# count, sha256[:16] of the C#'s output line
        "layout": [list(c) + [int(o.split(" ")[0]), hashlib.sha256(o.encode()).hexdigest()[:16]] for c, o in zip(lcases, lo)],
        "layout_full": [list(c) + [o] for c, o in list(zip(lcases, lo))[:12]],
    }
    GOLDEN.write_text(json.dumps(golden, separators=(",", ":")) + "\n")
    print("wrote %s: %d floor rects, %d layouts (%d threshold splits)" % (GOLDEN, len(fcases), len(lcases), split))


if __name__ == "__main__":
    main()
