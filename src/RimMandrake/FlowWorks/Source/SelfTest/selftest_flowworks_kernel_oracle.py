#!/usr/bin/env python3
# selftest-timeout: 600   (130-200 s alone, over the 240 s default under the 6-worker nightly sweep: CRASH [timeout] 2026-10-26)
"""Differential test: the production pulse kernel (FlowWorks/Source/RM_FlowKernel.cs) against the independent
Python PulseOracle (FlowWorks/northstar/validation_v2.py), which was validated once against live data.

Approach B phase 2 (design/RimMandrake/flowworks_offline_kernel_B.md). Generates seeded random water scenes
(declared bodies, limited or limitless; digs in order, so seed order = dig order; optional sink band), runs both,
and compares every dug cell's F after every pulse plus each body's final stock. Disagreement prints the seed.

    python3 src/RimMandrake/FlowWorks/Source/SelfTest/selftest_flowworks_kernel_oracle.py [N] [mode,mode,...]
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
import level_water as lw  # noqa: E402
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


def ops_scene(seed):
    """PUMP_CANAL_FEED / HOSE_LEFTOVER / CANAL_FILLIN fixes: a plain scene plus 1..4 events after random pulses: a pour of
    1..2 notches (a pump level, a hose leftover) at a dug square, or a fill-in of a dug square (thin sheets included: the
    pulses before it have usually spread the water thin)."""
    sc = scene(seed)
    w, h, pulses, band, bodies, src, digs = sc
    r = random.Random(7_000_001 + seed)
    cells = [c for c, _ in digs]
    events = []
    for _ in range(r.randint(1, 4)):
        p = r.randrange(pulses)
        c = r.choice(cells) if cells else (0, 0)
        if r.random() < 0.5:
            events.append((p, 0, c, r.randint(1, 2 * v.level_water.U)))
        else:
            events.append((p, 1, c, 0))
    return sc + ({}, events)


def oracle(sc, surface=False, level_set=False, creep=False, head_rule=False, exact=False):
    w, h, pulses, band, bodies, src, digs = sc[:7]
    beds = (sc[7] or None) if len(sc) > 7 else None
    events = sc[8] if len(sc) > 8 else []
    o = v.PulseOracle(w, h, dict(src), {b: dict(d) for b, d in bodies.items()}, per=1, budget=True,
                      sink_band=band or None, algo="fixed", level_surface=surface, level_set=level_set,
                      creep_water=creep, creep_thick=creep, head_rule=head_rule, beds=beds, level_exact=exact)
    order = []
    for c, d in digs:
        o.dig(c, d)
        if c not in order:
            order.append(c)
    parts = []
    for _ in range(pulses):
        o.pulse()
        line = [str(o.W[c] if exact else o.F[c]) for c in order]
        for (p, kind, c, dl) in events:
            if p == len(parts):
                line.append("e%d" % (v.level_water.pour(o, c, dl) if kind == 0 else v.level_water.fill_in(o, c)))
        parts.append(" ".join(line))
    if exact:
        tail = " ".join("L" if o.bodies[b]["limitless"] else str(v.level_water.pond_dl(o, b)) for b in sorted(o.bodies))
    else:
        tail = " ".join("L" if o.bodies[b]["limitless"] else "%.0f" % o.bodies[b]["stock"] for b in sorted(o.bodies))
    return " | ".join(p for p in parts) + " | " + tail if parts else tail


def bodies_scene(seed):
    """FISH_ROLL_MEND_PONDS_BORN_BARREN (trap c): a grid of water squares at map start, then squares drying and refilling at
    random (ponds splitting, merging, vanishing and coming back). Returns (w, h, initial wet cells, [(cell, wet), ...])."""
    r = random.Random(2_000_003 + seed)
    w, h = r.randint(2, 14), r.randint(2, 14)
    p = 0.35 + r.random() * 0.6
    wet = [c for c in range(w * h) if r.random() < p]
    ops = [(r.randrange(w * h), 1 if r.random() < 0.45 else 0) for _ in range(r.randint(1, 3 * w * h))]
    return w, h, wet, ops


def encode_bodies(sc):
    w, h, wet, ops = sc
    return " ".join(map(str, [w, h] + wet)) + " | " + " ".join("%d %d" % o for o in ops)


def oracle_bodies(sc):
    """The water bodies a correct tracker holds after every toggle: the 4-connected pieces of the wet squares (union-find),
    their sizes sorted. Independent of the C# port: no flood fill, no tracker state carried between steps."""
    w, h, wet, ops = sc
    state = [False] * (w * h)
    for c in wet:
        state[c] = True
    out = []
    for c, on in ops:
        state[c] = bool(on)
        parent = list(range(w * h))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for i in range(w * h):
            if not state[i]:
                continue
            if i % w < w - 1 and state[i + 1]:
                parent[find(i)] = find(i + 1)
            if i + w < w * h and state[i + w]:
                parent[find(i)] = find(i + w)
        sizes = {}
        for i in range(w * h):
            if state[i]:
                sizes[find(i)] = sizes.get(find(i), 0) + 1
        out.append(",".join(str(v) for v in sorted(sizes.values())))
    return ";".join(out)


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
    if len(sc) > 8:
        out.append(len(sc[8]))
        for p, kind, (x, z), dl in sc[8]:
            out += [p, kind, z * w + x, dl]
    return " ".join(map(str, out))


# ── SURFACEGAP_PARITY_FIX_TIES_ARE_UNSORTED: RM_SurfaceGap.Measure against level_water.surface_gaps ──

GAP_FLUIDS = (None, "w", "m")      # encoded 0, 1, 2 (C#: null, ArrayWorld.Water, an oil object)


def gaps_scene(seed):
    """Dug squares of either fluid (or none), ponds of 1-4 shore squares, limitless sources, shut sluices on squares and
    sources, sources of either fluid or none; a third of the scenes measured over a rect, a fifth a field of level
    one-square bodies (ties past List.Sort's 16-item insertion sort)."""
    rng = random.Random(41000 + seed)
    w, h = 8, 6
    cells, srcs, lim = {}, {}, []
    sq = [(x, z) for x in range(w) for z in range(h)]
    if rng.random() < 0.2:
        for (x, z) in sq:
            if (x + z) % 2 == 0:
                cells[(x, z)] = (2, rng.choice([lw.U, lw.U, lw.U, 2 * lw.U]), "w")
    else:
        nb = rng.randint(0, 3)
        beds_of = {b: [rng.choice([1, 2, 3, 4]) for _ in range(rng.randint(1, 4))] for b in range(nb)}
        srcs = {b: {} for b in beds_of}
        rng.shuffle(sq)
        for c in sq:
            r = rng.random()
            if r < 0.55:
                D = rng.randint(1, 4)
                cells[c] = (D, rng.choice([0, rng.randint(0, D * lw.U), D * lw.U, D * lw.U - 190]), rng.choice(["w"] * 8 + ["m", None]))
            elif r < 0.8 and beds_of:
                b = rng.choice(list(beds_of))
                if len(srcs[b]) < len(beds_of[b]):
                    srcs[b][c] = beds_of[b][len(srcs[b])]
            elif r < 0.85:
                lim.append(c)
    ponds = {b: (lw.histogram(list(ss.values())), rng.randint(0, sum(ss.values()) * lw.U), ss) for b, ss in srcs.items() if ss}
    sealed = {c for c in list(cells) + lim + [s for ss in srcs.values() for s in ss] if rng.random() < 0.08}
    sf = {s: rng.choice(["w", "w", "m", None]) for ss in srcs.values() for s in ss}
    sf.update({s: rng.choice(["w", "m", None]) for s in lim})
    domain = sorted(cells)
    if rng.random() < 0.33:
        x0, z0 = rng.randint(0, w - 1), rng.randint(0, h - 1)
        x1, z1 = rng.randint(x0, w - 1), rng.randint(z0, h - 1)
        domain = [c for c in domain if x0 <= c[0] <= x1 and z0 <= c[1] <= z1]
    return w, h, cells, ponds, lim, sealed, sf, domain


def encode_gaps(sc):
    w, h, cells, ponds, lim, sealed, sf, domain = sc
    idx = lambda c: c[1] * w + c[0]          # noqa: E731
    fcode = lambda f: GAP_FLUIDS.index(f)    # noqa: E731
    out = [w, h, len(cells)]
    for c, (D, W, f) in cells.items():
        out += [idx(c), D, W, fcode(f)]
    src = [(s, b, bed) for b, (_, _, ss) in ponds.items() for s, bed in ss.items()] + [(s, -2, 0) for s in lim]
    out.append(len(src))
    for s, b, bed in src:
        out += [idx(s), b, bed, fcode(sf.get(s))]
    out.append(len(ponds))
    for b, (H, dl, _) in ponds.items():
        out += [b, repr(float(lw.pond_surface_height(H, dl)))]
    out.append(len(sealed))
    out += [idx(c) for c in sorted(sealed)]
    out.append(len(domain))
    out += [idx(c) for c in domain]
    return " ".join(map(str, out))


def oracle_surface_gaps(sc):
    w, h, cells, ponds, lim, sealed, sf, domain = sc
    return lw.surface_gaps({c: cells[c] for c in domain}, ponds, lim, sealed=sealed, src_fluid=sf)


def gaps_agree(got_line, want):
    """Same bodies in the same order (the tie order too); squares exact, metres to 1e-12."""
    got = [] if got_line.strip() == "-" else [b.split(":") for b in got_line.split(";")]
    if len(got) != len(want):
        return False
    for g, (gap, n, lo, hi) in zip(got, want):
        if int(g[0]) != n or any(abs(float(a) - b) > 1e-12 for a, b in zip(g[1:], (gap, lo, hi))):
            return False
    return True


def norm(s):
    return " ".join(s.split())


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    dotnet = stock_wrapper._find_dotnet()
    if dotnet is None:
        sys.exit("dotnet.exe not found; UNMEASURED, not a pass or a fail")
    plain = [scene(s) for s in range(n)]
    ponds = [pond_scene(s) for s in range(n)]
    opsc = [ops_scene(s) for s in range(n)]
    bodysc = [bodies_scene(s) for s in range(n)]
    gapsc = [gaps_scene(s) for s in range(n)]
    # An ext4 clone cannot hand dotnet.exe its own path (\home\... is invalid): stage it on D: (selftest_winstage), and keep
    # the scene files and the dll inside the stage, where a /mnt/d path converts.
    from selftest_winstage import windows_project_path, stage_name_for
    import winbuild
    real = os.path.realpath(stock_wrapper.CSPROJ)
    if real.startswith("/mnt/"):
        stage_dir = os.path.dirname(real)
    else:
        stage_dir = os.path.join(winbuild.BUILD_ROOT, stage_name_for(real, winbuild.ROOT),
                                 os.path.relpath(os.path.dirname(real), winbuild.ROOT))
    with stock_wrapper.dotnet_lock():
        proj = windows_project_path(stock_wrapper.CSPROJ)
        # `dotnet run` does not forward a piped stdin here (it hangs), so build, then run the dll directly.
        b = subprocess.run([dotnet, "build", proj, "-c", "Release", "-nologo", "-v", "q", "-nodeReuse:false", "-p:UseSharedCompilation=false"], capture_output=True, text=True)
        if b.returncode != 0:
            print(b.stdout[-2000:], b.stderr[-2000:])
            sys.exit("selftest build failed")
        dll = stock_wrapper._to_windows_path(os.path.join(stage_dir, "bin", "Release", "net8.0", "RimMandrakeFlowWorks.SelfTest.dll"))
        failed = []
        # Three engines: the pre-surface rule, levelBySurfaceEnabled (WATER_SURFACE_REWIRE_PUDDLES_LEFT_BEHIND), and that plus
        # levelSetEnabled (WATER_LEVELSET_SOLVE, shipped ON); "shipped" adds both creeps (and with them the mouth top-up,
        # CANAL_MOUTH_DIAGNOSE_BLINKS_DRY_HALF_TIME).
        # "pond" (POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD, D2): shipped plus the head rule, on scenes whose source cells carry
        # beds and whose ponds stand below their brims.
        # "exact" / "exactpond" (WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES): levelExactEnabled against northstar/level_water.py,
        # every dug cell's water in dL after every pulse and each pond's dL at the end; on the plain scenes (beds read 4) and
        # on the pond scenes (beds 2..6, ponds below their brims).
        # "exactops" (PUMP_CANAL_FEED / HOSE_LEFTOVER / CANAL_FILLIN fixes): exact, plus pours and fill-ins between pulses
        # (LevelOps over the production RM_LevelPour against level_water.pour / fill_in), each event's dL in the line.
        # "bodies" (FISH_ROLL_MEND_PONDS_BORN_BARREN, trap c): the vanilla water-body tracker port with the production split mend
        # (SelfTest/WaterBodyMendChecks.cs over RM_WaterBodyMath.cs) against union-find pieces, body sizes after every toggle.
        # "gaps" (SURFACEGAP_PARITY_FIX_TIES_ARE_UNSORTED): RM_SurfaceGap.Measure (LevelExactChecks.SurfaceGapScenes) against
        # level_water.surface_gaps on random scenes with mixed fluids, shut sluices, rects and fields of tied bodies.
        modes = sys.argv[2].split(",") if len(sys.argv) > 2 else ("depth", "surface", "levelset", "shipped", "pond", "exact", "exactpond", "exactops", "bodies", "gaps")
        known = ("depth", "surface", "levelset", "shipped", "pond", "exact", "exactpond", "exactops", "bodies", "gaps")
        if n < 1 or [m for m in modes if m not in known]:
            sys.exit("N must be >= 1 and every mode one of %s (a typo ran an unlabelled engine; N=0 compared nothing)" % ",".join(known))
        for mode in modes:
            scenes = ponds if mode in ("pond", "exactpond") else opsc if mode == "exactops" else bodysc if mode == "bodies" else gapsc if mode == "gaps" else plain
            enc = encode_bodies if mode == "bodies" else encode_gaps if mode == "gaps" else encode
            os.makedirs(os.path.join(stage_dir, "bin"), exist_ok=True)
            scene_file = os.path.join(stage_dir, "bin", "oracle_scenes_%s.txt" % mode)   # in the stage, never the clone
            with open(scene_file, "w") as f:
                f.write("\n".join(enc(sc) for sc in scenes) + "\n")
            t0 = time.time()
            exact = mode in ("exact", "exactpond", "exactops")
            want = [oracle_bodies(sc) for sc in scenes] if mode == "bodies" else [oracle_surface_gaps(sc) for sc in scenes] if mode == "gaps" else [oracle(sc, mode != "depth", mode in ("levelset", "shipped", "pond"), mode in ("shipped", "pond"),
                           mode == "pond", exact) for sc in scenes]
            t1 = time.time()
            cs_mode = "exact" if exact else mode
            args = [dotnet, dll, "--oracle-scenes", stock_wrapper._to_windows_path(scene_file)] + ([cs_mode] if mode != "depth" else [])
            if mode == "gaps":
                args = [dotnet, dll, "--surface-gaps", stock_wrapper._to_windows_path(scene_file)]
            res = subprocess.run(args, capture_output=True, text=True, timeout=300)
            t2 = time.time()
            if res.returncode != 0:
                print(res.stdout[-2000:], res.stderr[-2000:])
                sys.exit("kernel run failed (%s)" % mode)
            got = [ln for ln in res.stdout.replace("\r", "").split("\n") if ln.strip()]
            if len(got) != n:
                sys.exit("kernel answered %d scenes of %d (%s)" % (len(got), n, mode))
            if mode == "gaps":
                bad = [i for i in range(n) if not gaps_agree(got[i], want[i])]
            else:
                bad = [i for i in range(n) if norm(got[i]) != norm(want[i])]
            pulses = (sum(len(sc[3]) for sc in scenes) if mode == "bodies" else 0 if mode == "gaps"
                      else sum(sc[2] for sc in scenes))
            print("[%s] %d scenes, %d pulses: oracle %.2f s, kernel %.2f s" % (mode, n, pulses, t1 - t0, t2 - t1))
            for i in bad[:5]:
                print("DISAGREE [%s] seed %d: %s\n  oracle %s\n  kernel %s" % (mode, i, enc(scenes[i]), want[i][:300], got[i][:300]))
            if bad:
                failed.append("%s: %d/%d scenes disagree" % (mode, len(bad), n))
            else:
                print("PASS [%s]: kernel == PulseOracle on %d/%d scenes" % (mode, n, n))
    if failed:
        sys.exit("; ".join(failed))


if __name__ == "__main__":
    main()
