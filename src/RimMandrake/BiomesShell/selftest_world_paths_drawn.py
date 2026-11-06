#!/usr/bin/env python3
# selftest-timeout: 600   (lost WSL launches winbuild.run_interop repeats: up to 3 at ~2 min each, INTEROP_RETRY_FIX_EIGHTY_SCRIPTS_LEFT)
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
  5. DRAWING: Source/RM_WorldPathsDrawn.cs itself is compiled against stand-in engine types
     (selftest_world_paths_drawn_stubs.cs) and RoadPrefix, River and HighlightPostfix are RUN: every ancient-highway
     link with LinkHash < AncientGapShare is drawn at width 0 (and only those), worn dirt links at DirtWornWidth on
     the Dirt layer, stone untouched; river link widths x their graph factor, the bank pale (lighter than the water
     and than the dark bank), the dry fade toward DryTan; a highlight strip of HighlightWidth on its own material,
     coloured toward white, on wet water tiles only. Named mutants of that file (the blind checker's three plus more)
     must each turn this red, or the check is blind.
  6. SHIPPED: the committed DLL is the one its .srchash stamped, built from these sources.
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
STUBS_CS = os.path.join(HERE, "selftest_world_paths_drawn_stubs.cs")
# dotnet.exe needs a Windows drive; a sandbox where D: is not visible to Windows may point this elsewhere.
EXEC_SCRATCH = os.environ.get("RM_SELFTEST_EXEC_SCRATCH", "/mnt/d/ClaudeWork/rimmandrake/selftest_tmp")
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
W = {n: const(D, n) for n in ("AncientGapShare", "DirtWornShare", "DirtWornWidth", "HighlightWidth", "BankPale",
                              "HighlightMix", "HighlightAlpha")}


def colour(text, name):
    m = re.search(r"static readonly Color " + name + r" = new Color\(([0-9.]+)f, ([0-9.]+)f, ([0-9.]+)f\);", text)
    if not m:
        sys.exit("cannot parse %s" % name)
    return tuple(float(x) for x in m.groups())


PALE_BANK, DRY_TAN = colour(D, "PaleBank"), colour(D, "DryTan")


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
        built = winbuild.run_interop_captured([dotnet, "build", winbuild.win(os.path.join(where, "RiverGraphExec.csproj")), "-c", "Release",
                                "--nologo", "-v", "quiet"], cwd=where, capture_output=True, text=True, timeout=300)
        if built.returncode != 0:
            bad.append("execution: harness build failed: " + built.stdout[-1500:])
            return None
        ran = winbuild.run_interop_captured([dotnet, winbuild.win(os.path.join(where, "bin", "Release", "net8.0", "RiverGraphExec.dll")),
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
        if (a != b) if isinstance(a, tuple) else not abs(a - b) <= 1e-5:   # NaN never matches
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


# ---- 5. drawing: RM_WorldPathsDrawn.cs run against stand-in engine types ------------------------------------------
DRAWN_CSPROJ = '''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><Nullable>disable</Nullable>
  <EnableDefaultCompileItems>false</EnableDefaultCompileItems><ImplicitUsings>disable</ImplicitUsings>
  <NoWarn>CS0162;CS0649;CS0169;CS0414</NoWarn><StartupObject>DrawnHarness.P</StartupObject></PropertyGroup>
  <ItemGroup><Compile Include="Stubs.cs" /><Compile Include="RM_WorldPathsDrawn.cs" /><Compile Include="RM_RiverGraph.cs" /></ItemGroup>
</Project>
'''
# (name, what breaks, text in RM_WorldPathsDrawn.cs, its replacement). Each must occur exactly once and must turn
# check_drawing red. A, C, D are the blind checker's (2026-11-03, at 3a54a06d).
DRAWN_MUTANTS = (
    ("A", "ancient highway not broken", "{ m.width = 0f; gap = true; }", "{ gap = true; }"),
    ("C", "no mid highlight", "if (dry > 0f) return;", "return;"),
    ("D", "dirt not worn", "m.width = n.width * DirtWornWidth", "m.width = n.width"),
    ("E", "dark bank", "Color32 baseCol = bank ? Mix(water, PaleBank, BankPale) : water;", "Color32 baseCol = bank ? darkBank : water;"),
    ("F", "no dry fade", "return Mix(baseCol, DryTan, dry * 0.8f);", "return baseCol;"),
    ("G", "no taper/fan width", "m.width = Mathf.Max(0f, n.width * f);", "m.width = n.width;"),
    ("H", "highlight full width", "m.width = n.width * HighlightWidth;", "m.width = n.width;"),
    ("I", "highlight left in the foreign colour", "hiMesh.colors[i] = c;", "{ }"),
    ("J", "wedge into a gap", "if (gap) allowSmoothTransition = false;", ""),
    ("K", "all-gap tile still draws its centre", "return any;", "return true;"),
    ("L", "highlight on a dry trace", "if (dry > 0f) return;", "if (dry > 1f) return;"),
    # GPT review of this check, 2026-11-03:
    ("M", "highlight recolours earlier tiles", "int from = hiMesh.colors.Count;", "int from = 0;"),
    ("N", "highlight postfix not registered",
     ",\n                postfix: new HarmonyMethod(typeof(RM_WorldPathsDrawn), nameof(HighlightPostfix))", ""),
    ("O", "road kind not looked up per link", "if (rl.neighbor.tileId == n.neighbor.tileId) { road = rl.road; break; }",
     "{ road = rl.road; break; }"),
    ("P", "rivers ignore their setting", "public static bool Rivers => RM_WorldPaths.applied && RM_WorldPaths.drawnRivers;",
     "public static bool Rivers => RM_WorldPaths.applied;"),
    ("Q", "roads ignore their setting", "public static bool Roads => RM_WorldPaths.applied && RM_WorldPaths.wornRoads;",
     "public static bool Roads => RM_WorldPaths.applied;"),
)
ROAD_LAYERS = {"Dirt": (120, 90, 60, 255), "Outline": (40, 30, 20, 255), "Stone": (150, 140, 120, 255)}
ROAD_KINDS = ("AncientAsphaltRoad", "AncientAsphaltHighway", "DirtPath", "DirtRoad", "StoneRoad")
HI_MAT = "RM_RiverHighlight"


def mix(a, b, t):
    """RM_WorldPathsDrawn.Mix: lerp the bytes toward a float colour, truncate, keep a's alpha."""
    t = min(1.0, max(0.0, t))
    return tuple(int(f32((x / 255.0 + (y - x / 255.0) * t) * 255.0)) for x, y in zip(a[:3], b[:3])) + (a[3],)


def cstr(c):
    return ",".join(str(int(x)) for x in c)


def drawn_cases(rng):
    """Commands for the harness, each with the Python expectation of its output line."""
    cmds, want = [], {}
    for name, c in ROAD_LAYERS.items():
        cmds.append("LAYER %s %s" % (name, cstr(c)))

    def road(on, worn, layer, kinds, tile, nbrs, colour=None):
        """kinds: one road kind per link (a junction may join different roads)."""
        cid = "r%d" % len(want)
        ws = [f32(rng.uniform(.1, 1.2)) for _ in nbrs]
        cmds.append("SET %d %d %d" % (on, rng.randint(0, 1), worn))
        cmds.append("ROAD %s %s - %d %s" % (cid, cstr(colour or ROAD_LAYERS[layer]), tile,
                                           " ".join("%d:%r:%s" % (n, w, k) for n, w, k in zip(nbrs, ws, kinds))))
        out, gap = [], False
        for n, w, kind in zip(nbrs, ws, kinds):
            h = link_hash(tile, n)
            if not (on and worn and colour is None):
                out.append(w)
            elif kind.startswith("AncientAsphalt") and h < f32(W["AncientGapShare"]):
                out.append(0.0)
                gap = True
            elif kind.startswith("Dirt") and layer == "Dirt" and h < f32(W["DirtWornShare"]):
                out.append(f32(w * f32(W["DirtWornWidth"])))
            else:
                out.append(w)
        active = on and worn and colour is None
        want[("ROAD", cid)] = (int(any(x > 0 for x in out)) if active else 1, 0 if gap else 1, list(zip(nbrs, out)), kinds, layer)

    for i in range(500):
        tile = rng.randrange(1, 400000)
        nbrs = rng.sample(range(tile + 1, tile + 60), rng.randint(1, 6))
        one = rng.choice(ROAD_KINDS)
        road(1, 1, rng.choice(list(ROAD_LAYERS)), [one] * len(nbrs) if i % 2 else [rng.choice(ROAD_KINDS) for _ in nbrs], tile, nbrs)
    # a tile whose every link is a gap: the prefix must skip it whole (no centre hexagon)
    tile = next(t for t in range(1000, 10 ** 6) if link_hash(t, t + 1) < W["AncientGapShare"] and link_hash(t, t + 2) < W["AncientGapShare"])
    road(1, 1, "Outline", ["AncientAsphaltHighway"] * 2, tile, [tile + 1, tile + 2])
    for _ in range(30):   # switched off, or a colour no road layer has: nothing changes
        tile = rng.randrange(1, 400000)
        road(0, 1, "Dirt", [rng.choice(ROAD_KINDS)] * 3, tile, [tile + 1, tile + 2, tile + 3])
        road(1, 0, "Dirt", [rng.choice(ROAD_KINDS)] * 3, tile, [tile + 1, tile + 2, tile + 3])
        road(1, 1, "Dirt", ["AncientAsphaltRoad"] * 3, tile, [tile + 1, tile + 2, tile + 3], colour=(9, 9, 9, 255))

    def river(applied, drawn, bank, graph, dry, with_f=True):
        on = applied and drawn
        cid = "v%d" % len(want)
        tile = rng.randrange(1, 400000)
        water = (rng.randrange(40, 160), rng.randrange(60, 170), rng.randrange(80, 200), 255)
        dark = tuple(int(x * .22) for x in water[:3]) + (255,)
        nbrs = [tile + 1 + i for i in range(rng.randint(1, 4))]
        ws = [f32(rng.uniform(.2, 1.0)) for _ in nbrs]
        fs = [f32(rng.uniform(.3, 1.6)) if with_f else None for _ in nbrs]
        cmds.append("SET %d %d %d" % (applied, drawn, rng.randint(0, 1)))
        cmds.append("RIVER %s %d %d %d %r %s %s %s" % (cid, bank, graph, tile, dry, cstr(water), cstr(dark), " ".join(
            "%d:%r" % (n, w) + (":%r" % f if f is not None else "") for n, w, f in zip(nbrs, ws, fs))))
        if on and graph:
            base = mix(water, PALE_BANK, W["BankPale"]) if bank else water
            col = mix(base, DRY_TAN, f32(f32(dry) * f32(.8)))
            out = [max(0.0, f32(w * f)) if f is not None else w for w, f in zip(ws, fs)]
        else:
            col, out = (dark if bank else water), ws
        want[("RIVER", cid)] = (col, list(zip(nbrs, out)), water, dark, bank, dry, on and graph)

    for _ in range(150):
        river(1, 1, rng.randint(0, 1), 1, rng.choice((0.0, 0.0, 0.0, f32(rng.uniform(.05, 1.0)))), with_f=rng.random() < .8)
    for _ in range(20):
        river(0, 1, rng.randint(0, 1), 1, 0.0)
        river(1, 0, rng.randint(0, 1), 1, 0.0)
        river(1, 1, rng.randint(0, 1), 0, 0.0)

    def hi(applied, drawn, mat, graph, dry):
        on = applied and drawn
        cid = "h%d" % len(want)
        tile = rng.randrange(1, 400000)
        c = (rng.randrange(40, 160), rng.randrange(60, 170), rng.randrange(80, 200), 255)
        nbrs = [tile + 1 + i for i in range(rng.randint(1, 4))]
        ws = [f32(rng.uniform(.2, 1.0)) for _ in nbrs]
        cmds.append("SET %d %d %d" % (applied, drawn, rng.randint(0, 1)))
        cmds.append("HI %s %s %d %d %r %s %s" % (cid, mat, graph, tile, dry, cstr(c), " ".join("%d:%r" % (n, w) for n, w in zip(nbrs, ws))))
        if on and graph and mat == "water" and dry == 0:
            h = mix(c, (1.0, 1.0, 1.0), W["HighlightMix"])[:3] + (int(f32(255.0 * f32(W["HighlightAlpha"]))),)
            want[("HI", cid)] = (h, tile, [(n, f32(w * f32(W["HighlightWidth"]))) for n, w in zip(nbrs, ws)], c)
        else:
            want[("HI", cid)] = None

    for i in range(150):   # interleaved, so the shared highlight mesh holds earlier tiles when a later one draws
        hi(1, 1, "water", 1, 0.0)
        if i % 5 == 0:
            hi(1, 1, "water", 1, f32(rng.uniform(.05, 1.0)))
            hi(1, 1, "bank", 1, 0.0)
            hi(1, 1, "water", 0, 0.0)
            hi(0, 1, "water", 1, 0.0)
            hi(1, 0, "water", 1, 0.0)
    return cmds, want


def run_drawn(source, cmds, bad):
    """Compile `source` (RM_WorldPathsDrawn.cs text) with the stubs and RM_RiverGraph.cs; run `cmds`; raw stdout or None."""
    os.makedirs(EXEC_SCRATCH, exist_ok=True)
    where = tempfile.mkdtemp(prefix="pathsdrawn_", dir=EXEC_SCRATCH)
    try:
        shutil.copy(STUBS_CS, os.path.join(where, "Stubs.cs"))
        shutil.copy(GRAPH_CS, os.path.join(where, "RM_RiverGraph.cs"))
        for name, text in (("RM_WorldPathsDrawn.cs", source), ("PathsDrawnExec.csproj", DRAWN_CSPROJ), ("in.txt", "\n".join(cmds) + "\n")):
            with open(os.path.join(where, name), "w") as f:
                f.write(text)
        dotnet = winbuild.dotnet_exe()
        for _ in range(2):   # one retry: a dotnet.exe build on a fresh temp dir has failed once with no output (2026-11-03)
            built = winbuild.run_interop_captured([dotnet, "build", winbuild.win(os.path.join(where, "PathsDrawnExec.csproj")), "-c", "Release",
                                    "--nologo", "-v", "quiet"], cwd=where, capture_output=True, text=True, timeout=300)
            if built.returncode == 0:
                break
        if built.returncode != 0:
            bad.append("drawing: harness build failed: " + (built.stdout + built.stderr)[-1500:])
            return None
        ran = winbuild.run_interop_captured([dotnet, winbuild.win(os.path.join(where, "bin", "Release", "net8.0", "PathsDrawnExec.dll")),
                              winbuild.win(os.path.join(where, "in.txt"))], cwd=where, capture_output=True, text=True, timeout=200)
        if ran.returncode != 0:
            bad.append("drawing: harness exited %d: %s" % (ran.returncode, (ran.stdout + ran.stderr)[-600:]))
            return None
        return ran.stdout.replace("\r", "")
    finally:
        shutil.rmtree(where, ignore_errors=True)


def pairs(tokens):
    return [(int(n), float(w)) for n, w in (t.split(":") for t in tokens)]


def close(a, b):
    return len(a) == len(b) and all(x[0] == y[0] and abs(x[1] - y[1]) <= 1e-6 for x, y in zip(a, b))


def near(a, b):
    return all(abs(int(x) - int(y)) <= 1 for x, y in zip(a, b)) and a[3] == b[3]


def lum(c):
    return sum(c[:3])


def check_drawing(out, want):
    """Failures of one harness run against the expectations (an empty list is a pass)."""
    fails, seen, n_gap, n_hi, n_dry = [], set(), 0, 0, 0
    lines = out.splitlines()
    if not lines or not lines[0].startswith("PATCHED ") or sorted(lines[0][8:].split(",")) != sorted(
            ["WorldDrawLayer_Rivers.Regenerate pre=RegeneratePrefix post=-",
             "WorldDrawLayer_Paths.GeneratePaths pre=RoadPrefix post=HighlightPostfix"]):
        fails.append("Patch() did not patch Regenerate and GeneratePaths: %r" % (lines[:1],))
    for line in lines[1:]:
        p = line.split(" ")
        key = (p[0], p[1])
        if key not in want:
            fails.append("unexpected harness line %r" % line[:80])
            continue
        seen.add(key)
        w = want[key]
        if p[0] == "ROAD":
            ret, smooth, links, kind, layer = w
            got = pairs(p[4:])
            if (int(p[2]), int(p[3])) != (ret, smooth) or not close(got, links):
                fails.append("road %s on %s: want ret %d smooth %d %s, got %s" % (kind, layer, ret, smooth, links, line))
            n_gap += sum(1 for _, x in links if x == 0)
        elif p[0] == "RIVER":
            col, links, water, dark, bank, dry, active = w
            got = tuple(int(x) for x in p[2].split(","))
            if not near(got, col) or not close(pairs(p[3:]), links):
                fails.append("river (bank %d, dry %s, drawn %s): want %s %s, got %s" % (bank, dry, active, col, links, line))
            elif active and bank and dry == 0 and not (lum(got) > lum(water) and lum(got) > lum(dark)):
                fails.append("river bank is not pale (lighter than water and dark bank): %s" % line)
            elif active and dry > .5 and lum(got) == lum(mix(water, PALE_BANK, W["BankPale"]) if bank else water):
                fails.append("dry river tile did not fade: %s" % line)
            n_dry += 1 if active and dry > 0 else 0
        elif p[0] == "HI":
            body = line.split(" | ")
            calls = int(p[2])
            if w is None:
                if calls or len(body) < 2 or not body[-1].startswith("prior 1 "):
                    fails.append("highlight drawn (or earlier ones touched) where it must not be: %s" % line[:160])
                continue
            h, tile, links, c = w
            n_hi += 1
            if calls != 1 or len(body) != 3 or not body[2].startswith("prior 1 "):
                fails.append("highlight: want one strip, got %s" % line[:160])
                continue
            call = body[1].split(" ")
            got_c = tuple(int(x) for x in call[2].split(","))
            if call[0] != HI_MAT or int(call[1]) != tile or not near(got_c, h) or call[3] != "1" or not close(pairs(call[4:]), links):
                fails.append("highlight strip: want %s tile %d colour %s widths %s, got %s" % (HI_MAT, tile, h, links, body[1]))
            if not (lum(got_c) > lum(c) and 0 < got_c[3] < 255):
                fails.append("highlight is not a faint lighter line: %s" % body[1])
            verts = body[2].split(" ")[3:]
            want_v = []
            for _ in links:
                want_v += [HI_MAT + "=" + cstr(got_c), HI_MAT + "=" + cstr(got_c[:3] + (0,))]
            if verts != want_v:
                fails.append("highlight vertices not rewritten to its colour (FlowWorks recolours): %s" % body[2][:160])
    missing = set(want) - seen
    if missing:
        fails.append("%d commands produced no line, e.g. %s" % (len(missing), sorted(missing)[:3]))
    road_links = [x for k, v in want.items() if k[0] == "ROAD" for x in v[2]]
    if n_gap < 50 or n_hi < 100 or n_dry < 20 or len(road_links) < 1500:
        fails.append("sanity: too few cases seen (gaps %d, highlights %d, dry %d, road links %d)" % (n_gap, n_hi, n_dry, len(road_links)))
    return fails


def check_drawn(bad):
    rng = random.Random(20261103)
    cmds, want = drawn_cases(rng)
    worn = sum(1 for k, v in want.items() if k[0] == "ROAD" and v[4] == "Dirt"
               for kind in v[3] if kind.startswith("Dirt"))
    if worn < 50:
        bad.append("sanity: only %d dirt links on the Dirt layer in the sweep" % worn)
    out = run_drawn(D, cmds, bad)
    if out is None:
        return
    fails = check_drawing(out, want)
    for f in fails[:8]:
        bad.append("drawing: " + f)
    if len(fails) > 8:
        bad.append("drawing: ... %d failures in all" % len(fails))
    blind = []
    for name, what, old, new in DRAWN_MUTANTS:
        if D.count(old) != 1:
            bad.append("sanity: mutant %s (%s): its text occurs %d times in RM_WorldPathsDrawn.cs, want 1" % (name, what, D.count(old)))
            continue
        mb = []
        mout = run_drawn(D.replace(old, new), cmds, mb)
        if mout is None:
            bad.append("sanity: mutant %s (%s) did not build or run, so it proves nothing: %s" % (name, what, mb[:1]))
        elif not check_drawing(mout, want):
            blind.append("%s (%s)" % (name, what))
    if blind:
        bad.append("sanity: the drawing check stays green on mutants %s: it is blind there" % ", ".join(blind))
    print("ran RM_WorldPathsDrawn.cs on %d drawing cases; %d mutants all caught" % (len(want), len(DRAWN_MUTANTS) - len(blind)))


def main():
    bad = []
    rng = random.Random(20261102)
    cases = hand_cases() + [random_case(rng) for _ in range(400)]
    check_hand(bad)
    check_properties(cases, bad)
    hashes = check_hash(bad)
    check_wiring(bad)
    check_shipped(bad)
    check_drawn(bad)
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
