#!/usr/bin/env python3
"""Offline proof of "Planet: drawn rivers" / "Planet: worn roads" (RIVERS_ROADS_REDESIGN_WORTH_LOOKING_AT).

The river graph (Source/RM_RiverGraph.cs) decides every width the planet draws: taper from the heads, a fan at the
mouths, a thinning dry trace where a system dies inland. Vanilla's WorldDrawLayer_Paths.GeneratePaths draws each
tile's half of a link out to the shared hex-edge midpoint, so a link must get ONE factor from both tiles or the river
steps at every edge.

  1. EXECUTION: Source/RM_RiverGraph.cs itself is compiled (dotnet.exe, net8.0 console) and run on hand-made and
     swept random river forests (trees, cycles, duplicated and one-way links, water tiles, dry systems); its output
     must equal this file's Python mirror. A mutant mirror (TaperTiles + 1) must DISagree, or the comparison is blind.
  2. PROPERTIES of the mirror on the same sweep: factors in [HeadMin*DryMin, MouthFan]; every leaf is exactly one of
     head / mouth / dry end; a system has a dry end iff it has leaves and no mouth; along a head-to-mouth chain the
     factor never falls before the mouth; the narrowest river's water strip (widthOnWorld - 0.2) stays >= 0.
  3. ROAD WEAR: LinkHash is symmetric and its gap / worn shares land within 2 points of AncientGapShare / DirtWornShare.
  4. WIRING: RM_WorldPaths calls into RM_WorldPathsDrawn; both settings are scribed and drawn; the highlight queue
     stays between the water (3530) and the roads (3540).
  5. SHIPPED: the committed DLL is the one its .srchash stamped, built from these sources.
Constants are parsed from the C#, so this cannot drift from it.
"""
import hashlib
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(RM, "Utils"))
import winbuild  # noqa: E402

SRC = os.path.join(HERE, "Source")
GRAPH_CS = os.path.join(SRC, "RM_RiverGraph.cs")
DRAWN_CS = os.path.join(SRC, "RM_WorldPathsDrawn.cs")
PATHS_CS = os.path.join(SRC, "RM_WorldPaths.cs")
MOD_CS = os.path.join(SRC, "RM_BiomesMod.cs")
DLL = os.path.join(HERE, "Assemblies", "RimMandrake.Biomes.dll")
EXEC_SCRATCH = "/mnt/d/ClaudeWork/rimmandrake/selftest_tmp"     # dotnet.exe needs a Windows drive
WATER_QUEUE, ROADS_QUEUE = 3530, 3540                               # WorldMaterials.Rivers / .Roads (decompiled 1.6)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def const(text, name):
    m = re.search(r"public const float " + name + r"\s*=\s*([0-9.]+)f;", text)
    if not m:
        sys.exit("cannot parse %s" % name)
    return float(m.group(1))


G = read(GRAPH_CS)
D = read(DRAWN_CS)
K = {n: const(G, n) for n in ("HeadMin", "TaperTiles", "MouthFan", "DryMin", "DryTiles")}
W = {n: const(D, n) for n in ("AncientGapShare", "DirtWornShare", "DirtWornWidth", "HighlightWidth")}


def f32(x):
    import struct
    return struct.unpack("f", struct.pack("f", x))[0]


# ---- the mirror (same steps as RM_RiverGraph.Analyse) -----------------------------------------------------------
def analyse(links, water, touches, k=K):
    adj, width = {}, {}
    for a, b, w in links:
        if a == b:
            continue
        key = (min(a, b), max(a, b))
        if key in width:
            width[key] = max(width[key], w)
            continue
        width[key] = w
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    seen, head_d, dry_d, mouth = set(), {}, {}, set()
    stats = {"links": len(width), "systems": 0, "heads": 0, "mouths": 0, "dry": 0}
    for start in sorted(adj):
        if start in seen:
            continue
        seen.add(start)
        comp, q = [], deque([start])
        while q:
            t = q.popleft()
            comp.append(t)
            for n in adj[t]:
                if n not in seen:
                    seen.add(n)
                    q.append(n)
        comp.sort()
        stats["systems"] += 1
        leaves = []
        for t in comp:
            if t in water:
                mouth.add(t)
            elif len(adj[t]) == 1:
                leaves.append(t)
                if t in touches:
                    mouth.add(t)
        root = -1
        if not any(t in mouth for t in comp) and leaves:
            best = -1.0
            for t in leaves:
                w = width[(min(t, adj[t][0]), max(t, adj[t][0]))]
                if w > best:
                    best, root = w, t
            stats["dry"] += 1
        heads = [t for t in leaves if t not in mouth and t != root]
        stats["heads"] += len(heads)
        stats["mouths"] += sum(1 for t in comp if t in mouth)
        bfs(heads, adj, head_d)
        if root >= 0:
            bfs([root], adj, dry_d)
    factor = {}
    for (a, b) in width:
        f = 1.0
        if a in head_d and b in head_d:
            f = k["HeadMin"] + (1 - k["HeadMin"]) * min(1.0, max(0.0, (head_d[a] + head_d[b]) * 0.5 / k["TaperTiles"]))
        if a in mouth or b in mouth:
            f *= k["MouthFan"]
        if a in dry_d and b in dry_d:
            dm = (dry_d[a] + dry_d[b]) * 0.5
            if dm < k["DryTiles"]:
                f *= k["DryMin"] + (1 - k["DryMin"]) * dm / k["DryTiles"]
        factor[(a, b)] = f
    dryness = {t: 1 - d / k["DryTiles"] for t, d in dry_d.items() if d < k["DryTiles"]}
    return stats, factor, dryness, mouth, head_d, dry_d, adj


def bfs(sources, adj, dist):
    q = deque()
    for s in sources:
        if s not in dist:
            dist[s] = 0
            q.append(s)
    while q:
        t = q.popleft()
        for n in adj[t]:
            if n not in dist:
                dist[n] = dist[t] + 1
                q.append(n)


def link_hash(a, b):
    M = 0xFFFFFFFF
    x = ((min(a, b) * 73856093) & M) ^ ((max(a, b) * 19349663) & M)
    x ^= x >> 13
    x = (x * 0x5BD1E995) & M
    x ^= x >> 15
    return (x & 0xFFFFFF) / 16777216.0


# ---- graphs ----------------------------------------------------------------------------------------------------
def hand_cases():
    # Y: heads 1 and 2 -> 3 -> 4 -> 5 (next to the sea)
    y = ([(1, 3, .32), (2, 3, .32), (3, 4, .46), (4, 5, .46)], set(), {5})
    # inland: 10 -> 11 -> 12 -> 13 -> 14 -> 15, widest leaf 15 dies dry
    dry = ([(10, 11, .32), (11, 12, .46), (12, 13, .46), (13, 14, .62), (14, 15, .62)], set(), set())
    # a river running into a water tile (30), given both ways
    sea = ([(20, 21, .32), (21, 20, .32), (21, 30, .46), (30, 21, .62)], {30}, set())
    ring = ([(40, 41, .46), (41, 42, .46), (42, 40, .46)], set(), set())
    return [y, dry, sea, ring]


def random_case(rng):
    n = rng.randint(2, 60)
    base = rng.randint(0, 100000)
    ids = rng.sample(range(base, base + 4 * n), n)
    links = []
    for i in range(1, n):
        a, b = ids[i], ids[rng.randrange(i)]
        w = rng.choice([.32, .46, .62, .82])
        links.append((a, b, w))
        if rng.random() < .3:
            links.append((b, a, rng.choice([.32, .46, .62, .82])))
    for _ in range(rng.choice([0, 0, 0, 1, 2])):   # some cycles
        a, b = rng.sample(ids, 2)
        links.append((a, b, .46))
    if rng.random() < .1:
        links.append((ids[0], ids[0], .32))          # a self-link is ignored
    water = set(rng.sample(ids, rng.choice([0, 0, 0, 1])))
    touches = set(t for t in ids if rng.random() < (.0 if rng.random() < .4 else .15)) | water
    rng.shuffle(links)
    return links, water, touches


# ---- the C# side -------------------------------------------------------------------------------------------------
HARNESS = r'''
using System; using System.Collections.Generic; using System.IO; using System.Globalization; using RimMandrake.Biomes;
static class P {
  static void Main(string[] a) {
    var inv = CultureInfo.InvariantCulture; var o = new System.Text.StringBuilder();
    List<RM_RiverGraph.Link> links = null; HashSet<int> water = null, touch = null; string id = null;
    foreach (string raw in File.ReadAllLines(a[0])) {
      string[] p = raw.Split(' ');
      if (p[0] == "G") { id = p[1]; links = new List<RM_RiverGraph.Link>(); water = new HashSet<int>(); touch = new HashSet<int>(); }
      else if (p[0] == "L") links.Add(new RM_RiverGraph.Link { a = int.Parse(p[1]), b = int.Parse(p[2]), width = float.Parse(p[3], inv) });
      else if (p[0] == "W") water.Add(int.Parse(p[1]));
      else if (p[0] == "T") touch.Add(int.Parse(p[1]));
      else if (p[0] == "H") o.Append("H " + p[1] + " " + p[2] + " " + RM_RiverGraph.LinkHash(int.Parse(p[1]), int.Parse(p[2])).ToString("R", inv) + "\n");
      else if (p[0] == "E") {
        var w = water; var t = touch;
        var r = RM_RiverGraph.Analyse(links, x => w.Contains(x), x => t.Contains(x));
        o.Append("R " + id + " " + r.links + " " + r.systems + " " + r.heads + " " + r.mouths + " " + r.dryEnds + "\n");
        foreach (var kv in r.linkFactor) o.Append("F " + id + " " + (int)(kv.Key >> 32) + " " + (int)(uint)kv.Key + " " + kv.Value.ToString("R", inv) + "\n");
        foreach (var kv in r.dryness) o.Append("D " + id + " " + kv.Key + " " + kv.Value.ToString("R", inv) + "\n");
      }
    }
    Console.Write(o.ToString());
  }
}
'''
CSPROJ = '''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><Nullable>disable</Nullable>
  <EnableDefaultCompileItems>false</EnableDefaultCompileItems><ImplicitUsings>disable</ImplicitUsings></PropertyGroup>
  <ItemGroup><Compile Include="Harness.cs" /><Compile Include="RM_RiverGraph.cs" /></ItemGroup>
</Project>
'''


def run_csharp(cases, hashes, bad):
    os.makedirs(EXEC_SCRATCH, exist_ok=True)
    where = tempfile.mkdtemp(prefix="rivergraph_", dir=EXEC_SCRATCH)
    try:
        shutil.copy(GRAPH_CS, os.path.join(where, "RM_RiverGraph.cs"))
        with open(os.path.join(where, "Harness.cs"), "w") as f:
            f.write(HARNESS)
        with open(os.path.join(where, "RiverGraphExec.csproj"), "w") as f:
            f.write(CSPROJ)
        lines = []
        for i, (links, water, touches) in enumerate(cases):
            lines.append("G %d" % i)
            lines += ["L %d %d %r" % (a, b, w) for a, b, w in links]
            lines += ["W %d" % t for t in sorted(water)]
            lines += ["T %d" % t for t in sorted(touches)]
            lines.append("E")
        lines += ["H %d %d" % h for h in hashes]
        with open(os.path.join(where, "in.txt"), "w") as f:
            f.write("\n".join(lines) + "\n")
        dotnet = winbuild.dotnet_exe()
        built = subprocess.run([dotnet, "build", winbuild.win(os.path.join(where, "RiverGraphExec.csproj")), "-c", "Release",
                                "--nologo", "-v", "quiet"], cwd=where, capture_output=True, text=True, timeout=300)
        if built.returncode != 0:
            bad.append("execution: harness build failed: " + built.stdout[-1500:])
            return None
        ran = subprocess.run([dotnet, winbuild.win(os.path.join(where, "bin", "Release", "net8.0", "RiverGraphExec.dll")),
                              winbuild.win(os.path.join(where, "in.txt"))], cwd=where, capture_output=True, text=True, timeout=200)
        if ran.returncode != 0:
            bad.append("execution: harness exited %d: %s" % (ran.returncode, (ran.stdout + ran.stderr)[-600:]))
            return None
        return ran.stdout.replace("\r", "")
    finally:
        shutil.rmtree(where, ignore_errors=True)


def mirror_lines(cases, hashes, k=K):
    """{key: value}: R rows carry a tuple of counts, F/D/H rows a float."""
    out = {}
    for i, (links, water, touches) in enumerate(cases):
        st, fac, dry, *_ = analyse(links, water, touches, k)
        out[("R", str(i))] = (st["links"], st["systems"], st["heads"], st["mouths"], st["dry"])
        for (a, b), f in fac.items():
            out[("F", str(i), a, b)] = f32(f)
        for t, d in dry.items():
            out[("D", str(i), t)] = f32(d)
    for a, b in hashes:
        out[("H", a, b)] = link_hash(a, b)
    return out


def csharp_lines(text):
    out = {}
    for line in text.splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == "R":
            out[("R", p[1])] = tuple(map(int, p[2:]))
        elif p[0] == "F":
            out[("F", p[1], int(p[2]), int(p[3]))] = float(p[4])
        elif p[0] == "D":
            out[("D", p[1], int(p[2]))] = float(p[3])
        elif p[0] == "H":
            out[("H", int(p[1]), int(p[2]))] = float(p[3])
    return out


def disagree(cs, py):
    """Keys present on one side only, or values apart (counts exactly; floats by 1e-5, float32 vs double)."""
    out = sorted(set(cs) ^ set(py), key=str)
    for key in set(cs) & set(py):
        a, b = cs[key], py[key]
        if (a != b) if isinstance(a, tuple) else abs(a - b) > 1e-5:
            out.append(key)
    return out


# ---- checks ------------------------------------------------------------------------------------------------------
def check_hand(bad):
    (y, dry, sea, ring) = hand_cases()
    st, fac, _, mouth, *_ = analyse(*y)
    if (st["heads"], st["mouths"], st["dry"]) != (2, 1, 0) or mouth != {5}:
        bad.append("Y river: want 2 heads, mouth {5}, no dry end; got %s %s" % (st, mouth))
    if not (fac[(1, 3)] < fac[(3, 4)] < 1.0 and abs(fac[(4, 5)] - K["MouthFan"] * (K["HeadMin"] + (1 - K["HeadMin"]) * 2.5 / K["TaperTiles"])) < 1e-9):
        bad.append("Y river: taper/mouth factors wrong: %s" % fac)
    st, fac, dryness, mouth, *_ = analyse(*dry)
    if st["dry"] != 1 or st["heads"] != 1 or mouth or abs(dryness.get(15, 0) - 1) > 1e-9 or not fac[(14, 15)] < fac[(12, 13)]:
        bad.append("inland river: want leaf 15 the dry end (dryness 1) thinning toward it; got %s %s %s" % (st, dryness, fac))
    st, fac, *_ = analyse(*sea)
    if st["links"] != 2 or st["mouths"] != 1 or st["heads"] != 1:
        bad.append("river into a water tile: want 2 links, 1 mouth, 1 head; got %s" % st)
    st, fac, *_ = analyse(*ring)
    if any(abs(f - 1) > 1e-9 for f in fac.values()) or st["dry"] or st["heads"]:
        bad.append("ring with no leaves: every factor should be 1; got %s %s" % (st, fac))


def check_properties(cases, bad):
    lo, hi = K["HeadMin"] * K["DryMin"], K["MouthFan"]
    n_dry = n_mouth = n_head = 0
    for links, water, touches in cases:
        st, fac, dryness, mouth, head_d, dry_d, adj = analyse(links, water, touches)
        for key, f in fac.items():
            if not (lo - 1e-9 <= f <= hi + 1e-9):
                bad.append("factor %.4f out of [%.3f, %.3f] on %s" % (f, lo, hi, key))
                return
        leaves = [t for t in adj if len(adj[t]) == 1 and t not in water]
        roots = [t for t in dry_d if dry_d[t] == 0]
        for t in leaves:
            kinds = (t in mouth) + (t in roots) + (head_d.get(t) == 0)
            if kinds != 1:
                bad.append("leaf %d is %d kinds at once (mouth/dry/head)" % (t, kinds))
                return
        n_dry += st["dry"]
        n_mouth += st["mouths"]
        n_head += st["heads"]
    if min(n_dry, n_mouth, n_head) < 20:
        bad.append("sanity: the sweep saw too few of a kind (dry %d, mouths %d, heads %d)" % (n_dry, n_mouth, n_head))
    # a chain head -> mouth: the factor never falls before the mouth link
    chain = [(i, i + 1, .46) for i in range(12)]
    _, fac, *_ = analyse(chain, set(), {12})
    fs = [fac[(i, i + 1)] for i in range(12)]
    if any(fs[i] > fs[i + 1] + 1e-12 for i in range(11)):
        bad.append("chain: the taper falls downstream: %s" % fs)
    widths = [float(x) for x in re.findall(r'\{ "(?:Creek|River|LargeRiver|HugeRiver)", ([0-9.]+)f \}', read(PATHS_CS))]
    if len(widths) != 4:
        bad.append("sanity: parsed %d river widths from RM_WorldPaths.cs, want 4" % len(widths))
    elif min(widths) - 0.2 < 0:
        bad.append("the narrowest river has a negative water strip")


def check_hash(bad):
    rng = random.Random(7)
    pairs = [(rng.randrange(1, 600000), rng.randrange(1, 600000)) for _ in range(20000)]
    if any(link_hash(a, b) != link_hash(b, a) for a, b in pairs[:500]):
        bad.append("LinkHash is not symmetric")
    hs = [link_hash(a, b) for a, b in pairs]
    for name in ("AncientGapShare", "DirtWornShare"):
        share = sum(1 for h in hs if h < W[name]) / len(hs)
        if abs(share - W[name]) > .02:
            bad.append("%s: measured share %.3f of links" % (name, share))
    return pairs[:300]


def check_wiring(bad):
    p, m = read(PATHS_CS), read(MOD_CS)
    for pin, where, text in (
            ("RM_WorldPathsDrawn.Patch(", "RM_WorldPaths.cs", p), ("RM_WorldPathsDrawn.River(", "RM_WorldPaths.cs", p),
            ('"worldDrawnRivers"', "RM_BiomesMod.cs", m), ('"worldWornRoads"', "RM_BiomesMod.cs", m),
            ('"Planet: drawn rivers [now]"', "RM_BiomesMod.cs", m), ('"Planet: worn roads [now]"', "RM_BiomesMod.cs", m),
            ("RM_WorldPaths.drawnRivers != RM_BiomesSettings.worldDrawnRivers", "RM_BiomesMod.cs", m)):
        if pin not in text:
            bad.append("wiring: %s has no %s" % (where, pin))
    # a gapped link must also turn off vanilla's two-link smooth branch, which joins both endpoints whatever their width
    if not re.search(r"ref bool allowSmoothTransition\)", D) or "if (gap) allowSmoothTransition = false;" not in D:
        bad.append("wiring: RoadPrefix does not turn off the smooth transition on a gap (it would draw a wedge into it)")
    q = re.search(r"renderQueue = waterQueue \+ (\d+)", D)
    if not q or not (WATER_QUEUE < WATER_QUEUE + int(q.group(1)) < ROADS_QUEUE):
        bad.append("highlight queue is not between the water (3530) and the roads (3540)")


def check_shipped(bad):
    with open(DLL + ".srchash", encoding="utf-8") as f:
        lines = [l.split() for l in f if l.strip()]
    with open(DLL, "rb") as f:
        binary = f.read()
    if [l[2] for l in lines if l[:2] == ["#", "dll:"]] != [hashlib.sha256(binary).hexdigest()]:
        bad.append("the committed DLL is not the one its .srchash stamped")
    sources = [l for l in lines if l[0] != "#"]
    listed = {os.path.basename(l[1]) for l in sources}
    for needed in ("RM_RiverGraph.cs", "RM_WorldPathsDrawn.cs", "RM_WorldPaths.cs", "RM_BiomesMod.cs"):
        if needed not in listed:
            bad.append("the .srchash does not list %s" % needed)
    for digest, rel in sources:
        with open(os.path.join(SRC, rel), "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != digest:
                bad.append("the DLL was not built from this %s: rebuild it" % rel)
    for name in (b"RM_RiverGraph", b"RM_WorldPathsDrawn", b"HighlightPostfix", b"RoadPrefix"):   # metadata names, UTF-8
        if name + b"\0" not in binary:
            bad.append("the committed DLL has no %s" % name.decode())


def main():
    bad = []
    rng = random.Random(20261102)
    cases = hand_cases() + [random_case(rng) for _ in range(400)]
    check_hand(bad)
    check_properties(cases, bad)
    hashes = check_hash(bad)
    check_wiring(bad)
    check_shipped(bad)
    out = run_csharp(cases, hashes, bad)
    if out is not None:
        cs, py = csharp_lines(out), mirror_lines(cases, hashes)
        if len(cs) < 2000:
            bad.append("sanity: only %d result lines from the C# harness" % len(cs))
        diff = disagree(cs, py)
        if diff:
            bad.append("execution: C# and mirror disagree on %d lines, e.g. %s" % (len(diff), diff[:6]))
        mutant = dict(K, TaperTiles=K["TaperTiles"] + 1)
        if not disagree(cs, mirror_lines(cases, hashes, mutant)):
            bad.append("sanity: a mutant mirror (TaperTiles+1) still matches the C#: the comparison is blind")
        print("executed RM_RiverGraph.cs on %d river forests: %d result lines" % (len(cases), len(cs)))
    for b in bad:
        print("FAIL:", b)
    print("RESULT:", "PASS" if not bad else "FAIL (%d)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
