#!/usr/bin/env python3
"""Differential test: the production pulse kernel (FlowWorks/Source/RM_FlowKernel.cs) against the independent
Python PulseOracle (FlowWorks/northstar/validation_v2.py), which was validated once against live data.

Approach B phase 2 (design/RimMandrake/flowworks_offline_kernel_B.md). Generates seeded random water scenes
(declared bodies, limited or limitless; digs in order, so seed order = dig order; optional sink band), runs both,
and compares every dug cell's F after every pulse plus each body's final stock. Disagreement prints the seed.

    python3 src/RimMandrake/FlowWorks/Source/SelfTest/selftest_flowworks_kernel_oracle.py [N]
"""
from __future__ import annotations

import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(MOD, "northstar"))
sys.path.insert(0, os.path.join(os.path.dirname(MOD), "Utils"))

import validation_v2 as v  # noqa: E402
import selftest_flowworks_stock as stock_wrapper  # noqa: E402  (dotnet discovery + path conversion)


def scene(seed):
    r = random.Random(seed)
    w, h = r.randint(3, 12), r.randint(3, 12)
    pulses = r.randint(1, 60)
    band = r.choice([0, 0, 0, 1, 2])
    nb = r.randint(1, 3)
    bodies = {b: {"limitless": r.random() < 0.3, "stock": float(r.randint(0, 30))} for b in range(nb)}
    src = {}
    for b in range(nb):
        x0, z0 = r.randrange(w), r.randrange(h)
        for x in range(x0, min(w, x0 + r.randint(1, 3))):
            for z in range(z0, min(h, z0 + r.randint(1, 3))):
                src.setdefault((x, z), b)
    digs = []
    for _ in range(r.randint(1, w * h // 2)):
        c = (r.randrange(w), r.randrange(h))
        if c not in src:
            digs.append((c, r.randint(1, 4)))
    return w, h, pulses, band, bodies, src, digs


def oracle(sc):
    w, h, pulses, band, bodies, src, digs = sc
    o = v.PulseOracle(w, h, dict(src), {b: dict(d) for b, d in bodies.items()}, per=1, budget=True,
                      sink_band=band or None, algo="fixed")
    order = []
    for c, d in digs:
        o.dig(c, d)
        if c not in order:
            order.append(c)
    parts = []
    for _ in range(pulses):
        o.pulse()
        parts.append(" ".join(str(o.F[c]) for c in order))
    tail = " ".join("L" if o.bodies[b]["limitless"] else "%.0f" % o.bodies[b]["stock"] for b in sorted(o.bodies))
    return " | ".join(p for p in parts) + " | " + tail if parts else tail


def encode(sc):
    w, h, pulses, band, bodies, src, digs = sc
    out = [w, h, pulses, band, len(bodies)]
    for b in range(len(bodies)):
        out += [1 if bodies[b]["limitless"] else 0, int(bodies[b]["stock"])]
    out.append(len(src))
    for (x, z), b in src.items():
        out += [z * w + x, b]
    out.append(len(digs))
    for (x, z), d in digs:
        out += [z * w + x, d]
    return " ".join(map(str, out))


def norm(s):
    return " ".join(s.split())


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    dotnet = stock_wrapper._find_dotnet()
    if dotnet is None:
        sys.exit("dotnet.exe not found; UNMEASURED, not a pass or a fail")
    t0 = time.time()
    scenes = [scene(s) for s in range(n)]
    want = [oracle(sc) for sc in scenes]
    t1 = time.time()
    proj = stock_wrapper._to_windows_path(stock_wrapper.CSPROJ)
    # `dotnet run` does not forward a piped stdin here (it hangs), so build, then run the dll directly.
    b = subprocess.run([dotnet, "build", proj, "-c", "Release", "-nologo", "-v", "q", "-nodeReuse:false", "-p:UseSharedCompilation=false"], capture_output=True, text=True)
    if b.returncode != 0:
        print(b.stdout[-2000:], b.stderr[-2000:])
        sys.exit("selftest build failed")
    dll = stock_wrapper._to_windows_path(os.path.join(HERE, "bin", "Release", "net8.0", "RimMandrakeFlowWorks.SelfTest.dll"))
    scene_file = os.path.join(HERE, "bin", "oracle_scenes.txt")   # bin/ is gitignored
    with open(scene_file, "w") as f:
        f.write("\n".join(encode(sc) for sc in scenes) + "\n")
    res = subprocess.run([dotnet, dll, "--oracle-scenes", stock_wrapper._to_windows_path(scene_file)],
                         capture_output=True, text=True, timeout=300)
    t2 = time.time()
    if res.returncode != 0:
        print(res.stdout[-2000:], res.stderr[-2000:])
        sys.exit("kernel run failed")
    got = [ln for ln in res.stdout.replace("\r", "").split("\n") if ln.strip()]
    if len(got) != n:
        sys.exit("kernel answered %d scenes of %d" % (len(got), n))
    bad = [i for i in range(n) if norm(got[i]) != norm(want[i])]
    pulses = sum(sc[2] for sc in scenes)
    print("%d scenes, %d pulses: oracle %.2f s, kernel (incl. dotnet build check) %.2f s" % (n, pulses, t1 - t0, t2 - t1))
    for i in bad[:5]:
        print("DISAGREE seed %d: %s\n  oracle %s\n  kernel %s" % (i, encode(scenes[i]), want[i][:300], got[i][:300]))
    if bad:
        sys.exit("%d/%d scenes disagree" % (len(bad), n))
    print("PASS: kernel == PulseOracle on %d/%d scenes" % (n, n))


if __name__ == "__main__":
    main()
