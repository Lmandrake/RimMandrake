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


def pond_scene(seed):
    """POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD (D2 head rule): a scene whose source cells carry beds (2/4 like vanilla water,
    deeper like a lake middle) and whose limited bodies hold LESS than their beds, so the pond stands below its brim and
    the head rule decides which ditches still draw. Returned as a scene tuple plus the bed map."""
    r = random.Random(1_000_003 + seed)
    w, h, pulses, band, bodies, src, digs = scene(1_000_003 + seed)
    beds = {c: r.choice([2, 2, 4, 4, 5, 6]) for c in src}
    for b, d in bodies.items():
        total = sum(beds[c] for c, i in src.items() if i == b)
        d["limitless"] = r.random() < 0.15
        d["stock"] = float(r.randint(0, total))
    digs = [(c, r.randint(1, 4)) for c, _ in digs]
    return (w, h, pulses, band, bodies, src, digs, beds)


def oracle(sc, surface=False, level_set=False, creep=False, head_rule=False):
    w, h, pulses, band, bodies, src, digs = sc[:7]
    beds = sc[7] if len(sc) > 7 else None
    o = v.PulseOracle(w, h, dict(src), {b: dict(d) for b, d in bodies.items()}, per=1, budget=True,
                      sink_band=band or None, algo="fixed", level_surface=surface, level_set=level_set,
                      creep_water=creep, creep_thick=creep, head_rule=head_rule, beds=beds)
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
    w, h, pulses, band, bodies, src, digs = sc[:7]
    out = [w, h, pulses, band, len(bodies)]
    for b in range(len(bodies)):
        out += [1 if bodies[b]["limitless"] else 0, int(bodies[b]["stock"])]
    out.append(len(src))
    for (x, z), b in src.items():
        out += [z * w + x, b]
    out.append(len(digs))
    for (x, z), d in digs:
        out += [z * w + x, d]
    if len(sc) > 7:
        out.append(len(sc[7]))
        for (x, z), b in sc[7].items():
            out += [z * w + x, b]
    return " ".join(map(str, out))


def norm(s):
    return " ".join(s.split())


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    dotnet = stock_wrapper._find_dotnet()
    if dotnet is None:
        sys.exit("dotnet.exe not found; UNMEASURED, not a pass or a fail")
    plain = [scene(s) for s in range(n)]
    ponds = [pond_scene(s) for s in range(n)]
    with stock_wrapper.dotnet_lock():
        proj = stock_wrapper._to_windows_path(stock_wrapper.CSPROJ)
        # `dotnet run` does not forward a piped stdin here (it hangs), so build, then run the dll directly.
        b = subprocess.run([dotnet, "build", proj, "-c", "Release", "-nologo", "-v", "q", "-nodeReuse:false", "-p:UseSharedCompilation=false"], capture_output=True, text=True)
        if b.returncode != 0:
            print(b.stdout[-2000:], b.stderr[-2000:])
            sys.exit("selftest build failed")
        dll = stock_wrapper._to_windows_path(os.path.join(HERE, "bin", "Release", "net8.0", "RimMandrakeFlowWorks.SelfTest.dll"))
        failed = []
        # Three engines: the pre-surface rule, levelBySurfaceEnabled (WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND), and that plus
        # levelSetEnabled (WATER_LEVELSET_SOLVE, shipped ON); "shipped" adds both creeps (and with them the mouth top-up,
        # CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME).
        # "pond" (POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD, D2): shipped plus the head rule, on scenes whose source cells carry
        # beds and whose ponds stand below their brims.
        for mode in ("depth", "surface", "levelset", "shipped", "pond"):
            scenes = ponds if mode == "pond" else plain
            scene_file = os.path.join(HERE, "bin", "oracle_scenes_%s.txt" % mode)   # bin/ is gitignored
            with open(scene_file, "w") as f:
                f.write("\n".join(encode(sc) for sc in scenes) + "\n")
            t0 = time.time()
            want = [oracle(sc, mode != "depth", mode in ("levelset", "shipped", "pond"), mode in ("shipped", "pond"),
                           mode == "pond") for sc in scenes]
            t1 = time.time()
            args = [dotnet, dll, "--oracle-scenes", stock_wrapper._to_windows_path(scene_file)] + ([mode] if mode != "depth" else [])
            res = subprocess.run(args, capture_output=True, text=True, timeout=300)
            t2 = time.time()
            if res.returncode != 0:
                print(res.stdout[-2000:], res.stderr[-2000:])
                sys.exit("kernel run failed (%s)" % mode)
            got = [ln for ln in res.stdout.replace("\r", "").split("\n") if ln.strip()]
            if len(got) != n:
                sys.exit("kernel answered %d scenes of %d (%s)" % (len(got), n, mode))
            bad = [i for i in range(n) if norm(got[i]) != norm(want[i])]
            pulses = sum(sc[2] for sc in scenes)
            print("[%s] %d scenes, %d pulses: oracle %.2f s, kernel %.2f s" % (mode, n, pulses, t1 - t0, t2 - t1))
            for i in bad[:5]:
                print("DISAGREE [%s] seed %d: %s\n  oracle %s\n  kernel %s" % (mode, i, encode(scenes[i]), want[i][:300], got[i][:300]))
            if bad:
                failed.append("%s: %d/%d scenes disagree" % (mode, len(bad), n))
            else:
                print("PASS [%s]: kernel == PulseOracle on %d/%d scenes" % (mode, n, n))
    if failed:
        sys.exit("; ".join(failed))


if __name__ == "__main__":
    main()
