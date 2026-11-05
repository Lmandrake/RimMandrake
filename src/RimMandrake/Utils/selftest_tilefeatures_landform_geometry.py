#!/usr/bin/env python3
"""Wrapper for the C# selftest of mandrake.rm.tilefeatures' landform geometry
(VEE_LANDFORMS_BUILD_CRATERS_AND_COMPANY: src/RimMandrake/TileFeatures/Source/SelfTest/).

Compiles production RM_LandformGeometry.cs (no game types) with Program.cs and runs it: crater zones and breaches,
meanders and distances, the ridge band with a gap, disc placement and the tide, with two raster walkability checks that
each carry a planted negative. See SelfTest/Program.cs's header for what is and is not covered.

Before the DLL runs, a SOURCE-PARITY check pins the production worker RM_TileMutatorWorker_LoneMountain (which needs a Map
and so cannot be compiled here) to the raster the DLL sweeps (LANDFORMS_PROBE_REPLACE_OR_KEEP_EXPERIMENT): Init computes
`room` from the centre minus EdgeMargin and its LAST write to `radius` is LoneMountainFit(radius, amps, room); EdgeMargin
equals the sweep margin; the centre jitter, harmonics, wobble and elevation calls are the swept ones; the def's
radiusFraction lies inside the swept radii. Each clause carries a planted negative (the source mutated in memory, the
check must go red), so the check is shown able to see the mutant that once stayed green (the fit line deleted).

dotnet is WINDOWS-NATIVE and cannot take an ext4 path, so the project is staged with selftest_winstage
(whole_src=False: it reads no shipped file beyond its own two sources).

    python3 selftest_tilefeatures_landform_geometry.py
"""
from __future__ import annotations

import os
import re
import sys

from selftest_winstage import windows_project_path
from winbuild import run_interop_captured  # noqa: E402  (WSL lost-launch retry)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(REPO, "src", "RimMandrake", "TileFeatures", "Source", "SelfTest",
                      "RimMandrakeTileFeatures.SelfTest.csproj")

SOURCE = os.path.join(REPO, "src", "RimMandrake", "TileFeatures", "Source")
WORKERS_CS = os.path.join(SOURCE, "RM_LandformWorkers.cs")
PROGRAM_CS = os.path.join(SOURCE, "SelfTest", "Program.cs")
LANDFORMS_XML = os.path.join(REPO, "src", "RimMandrake", "TileFeatures", "Defs", "TileMutatorDefs",
                             "RM_TileFeatures_Landforms.xml")

DOTNET_CANDIDATES = [
    "/mnt/c/Users/Mandrake/.dotnet/dotnet.exe",
    "/mnt/c/Program Files/dotnet/dotnet.exe",
]


def _norm(text):
    """C# text without comments, whitespace collapsed to single spaces."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _block(text, header_regex):
    """The {...} body following the first match of header_regex (brace-matched), or None."""
    m = re.search(header_regex, text)
    if not m:
        return None
    i = text.find("{", m.end())
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j]
    return None


def _statements(body):
    return [st.strip() for st in body.split(";") if st.strip()]


ROOM = ("int room = Math.Min(Math.Min(center.x, map.Size.x - 1 - center.x), "
        "Math.Min(center.z, map.Size.z - 1 - center.z)) - EdgeMargin")
FIT = "radius = RM_LandformGeometry.LoneMountainFit(radius, amps, room)"
BASE = "radius = size * ext.radiusFraction.RandomInRange"
AMPS = "amps = RM_LandformUtil.Harmonics(3, 0.12f)"
SIZE = "int size = Math.Min(map.Size.x, map.Size.z)"
JITTER = "Rand.RangeInclusive(-size / 10, size / 10)"
WOBBLE = "float r = RM_LandformGeometry.WobbledRadius(radius, (float)Math.Atan2(dz, dx), amps, phases)"
DXDZ = "float dx = c.x - center.x, dz = c.z - center.z"
ELEV = "elevation[c] = RM_LandformGeometry.LoneMountainElevation((float)Math.Sqrt(dx * dx + dz * dz), r,"
WRITES_RADIUS = re.compile(r"(?<![\w.])radius\s*(?:[-+*/]?=(?!=)|\+\+|--)")


def parity_fails(workers, program, landforms_xml):
    """Failures of the production lone-mountain worker against the raster the DLL sweeps (empty list = parity holds)."""
    fails = []
    cls = _block(workers, r"class\s+RM_TileMutatorWorker_LoneMountain\b")
    if cls is None:
        return ["RM_TileMutatorWorker_LoneMountain not found in RM_LandformWorkers.cs"]
    init = _block(cls, r"override\s+void\s+Init\s*\(\s*Map\s+map\s*\)")
    gen = _block(cls, r"override\s+void\s+GeneratePostElevationFertility\s*\(\s*Map\s+map\s*\)")
    if init is None or gen is None:
        return ["lone mountain worker: Init(Map) or GeneratePostElevationFertility(Map) not found"]
    sts = _statements(_norm(init))

    def at(stmt):
        return sts.index(stmt) if stmt in sts else -1

    i_size, i_amps, i_base, i_room, i_fit = at(SIZE), at(AMPS), at(BASE), at(ROOM), at(FIT)
    for name, i in (("size", i_size), ("harmonics", i_amps), ("base radius", i_base), ("room minus EdgeMargin", i_room),
                    ("LoneMountainFit", i_fit)):
        if i < 0:
            fails.append("lone mountain Init: no '%s' statement (%s)" % (name, {"size": SIZE, "harmonics": AMPS,
                         "base radius": BASE, "room minus EdgeMargin": ROOM, "LoneMountainFit": FIT}[name]))
    if min(i_size, i_amps, i_base, i_room, i_fit) >= 0 and not (i_size < i_base < i_room < i_fit and i_amps < i_fit):
        fails.append("lone mountain Init: order must be size < base radius < room < fit, harmonics before the fit")
    radius_writes = [k for k, st in enumerate(sts) if WRITES_RADIUS.search(st)]
    if i_fit >= 0 and radius_writes and radius_writes[-1] != i_fit:
        fails.append("lone mountain Init: radius is written after LoneMountainFit (statement %r)" % sts[radius_writes[-1]])
    for k, st in enumerate(sts):
        if i_fit >= 0 and k > i_fit and (re.search(r"(?<![\w.])(amps|center)\s*=(?!=)", st)):
            fails.append("lone mountain Init: %r rewrites what the fit was computed from" % st)
    centre = [st for st in sts if re.match(r"center\s*=", st)]
    if len(centre) != 1 or _norm(centre[0]).count(JITTER) != 2 or "map.Center.x +" not in centre[0] \
            or "map.Center.z +" not in centre[0]:
        fails.append("lone mountain Init: centre is not map.Center jittered by %s on both axes" % JITTER)
    if i_room >= 0 and centre and sts.index(centre[0]) > i_room:
        fails.append("lone mountain Init: centre is set after room")
    # outside Init, nothing writes radius, amps or center
    rest = _norm(cls.replace(init, ""))
    if WRITES_RADIUS.search(rest.replace("private float radius;", "")) or \
            re.search(r"(?<![\w.])(amps|center)\s*=(?!=)", rest.replace("private float[] amps, phases;", "")):
        fails.append("lone mountain worker: radius, amps or center is written outside Init")
    g = _norm(gen)
    for need, what in ((DXDZ, "offset from the fitted centre"), (WOBBLE, "wobbled fitted radius"),
                       (ELEV, "LoneMountainElevation of distance and wobbled radius"),
                       ("foreach (IntVec3 c in map.AllCells)", "every cell")):
        if need not in g:
            fails.append("lone mountain GeneratePostElevationFertility: no %s (%s)" % (what, need))
    if not re.search(r"elevation\s*\[\s*c\s*\]\s*=", g) or len(re.findall(r"elevation\s*\[[^\]]*\]\s*[-+*/]?=(?!=)", g)) != 1:
        fails.append("lone mountain GeneratePostElevationFertility: elevation must be written exactly once, at c")
    # margin, jitter, amplitude and radius range against the sweep in Program.cs
    m = re.search(r"public\s+const\s+int\s+EdgeMargin\s*=\s*(\d+)\s*;", cls)
    pm = re.search(r"const\s+int\s+margin\s*=\s*(\d+)\s*;", program)
    if not m or not pm or int(m.group(1)) != int(pm.group(1)):
        fails.append("EdgeMargin (%s) differs from the sweep's margin (%s)" % (m and m.group(1), pm and pm.group(1)))
    p = _norm(program)
    if "foreach (int o in new[] { -size / 10, 0, size / 10 })" not in p:
        fails.append("sweep does not cover the worker's centre jitter extremes (-size/10, 0, size/10)")
    if "if (fit) baseR = RM_LandformGeometry.LoneMountainFit(baseR, amps, room)" not in p or \
            "int room = Math.Min(Math.Min(cx, w - 1 - cx), Math.Min(cz, h - 1 - cz)) - margin" not in p:
        fails.append("sweep raster does not fit the radius to the room minus margin as the worker does")
    pa = re.search(r"amps\[k\]\s*=\s*([0-9.]+)f", program)
    harm = _block(workers, r"static\s+float\[\]\s+Harmonics\s*\(\s*int\s+n\s*,\s*float\s+maxAmp\s*\)")
    if not pa or harm is None or "Rand.Range(0f, maxAmp / n)" not in _norm(harm) or abs(float(pa.group(1)) - 0.12 / 3) > 1e-6:
        fails.append("sweep amplitude is not the worst case of Harmonics(3, 0.12f) (0.12/3 per harmonic)")
    rf = re.search(r"foreach\s*\(\s*float\s+rf\s+in\s+new\[\]\s*\{([^}]*)\}", program)
    d = re.search(r"<defName>RM_LoneMountain</defName>.*?</TileMutatorDef>", landforms_xml, flags=re.S)
    dr = d and re.search(r"<radiusFraction>\s*([0-9.]+)\s*~\s*([0-9.]+)\s*</radiusFraction>", d.group(0))
    wc = d and re.search(r"<workerClass>\s*RimMandrake\.TileFeatures\.RM_TileMutatorWorker_LoneMountain\s*</workerClass>",
                          d.group(0))
    if not rf or not dr or not wc:
        fails.append("RM_LoneMountain def, its workerClass or radiusFraction, or the sweep's radii not found")
    else:
        swept = [float(x.strip().rstrip("f")) for x in rf.group(1).split(",")]
        lo, hi = float(dr.group(1)), float(dr.group(2))
        if lo < min(swept) - 1e-6 or hi > max(swept) + 1e-6:
            fails.append("RM_LoneMountain radiusFraction %s~%s lies outside the swept radii %s" % (lo, hi, swept))
    return fails


def _in_lone(workers, old, new):
    """workers with the first `old` AFTER the lone mountain class header replaced (other workers share some lines)."""
    k = workers.find("class RM_TileMutatorWorker_LoneMountain")
    return workers[:k] + workers[k:].replace(old, new, 1) if k >= 0 else workers


def parity_check():
    """Runs the parity check on the shipped sources and its planted negatives; True when all hold."""
    workers, program, xml = (open(f, encoding="utf-8").read() for f in (WORKERS_CS, PROGRAM_CS, LANDFORMS_XML))
    ok = True
    fails = parity_fails(workers, program, xml)
    for f in fails:
        print("FAIL parity: " + f)
    ok &= not fails
    print("%s parity: production RM_TileMutatorWorker_LoneMountain matches the swept raster" % ("PASS" if not fails else "FAIL"))
    fit_line = "radius = RM_LandformGeometry.LoneMountainFit(radius, amps, room);"
    mutants = [
        ("fit line deleted (the mutant that once stayed green)", lambda w, p, x: (w.replace(fit_line, ""), p, x)),
        ("room ignores EdgeMargin", lambda w, p, x: (w.replace(") - EdgeMargin;", ");"), p, x)),
        ("EdgeMargin shrunk to 2", lambda w, p, x: (w.replace("EdgeMargin = 6;", "EdgeMargin = 2;"), p, x)),
        ("radius rewritten after the fit",
         lambda w, p, x: (w.replace(fit_line, fit_line + " radius = size * ext.radiusFraction.RandomInRange;"), p, x)),
        ("fit computed before room",
         lambda w, p, x: (w.replace(fit_line, "").replace("int room = Math.Min(Math.Min(center.x",
                                                          fit_line + " int room = Math.Min(Math.Min(center.x"), p, x)),
        ("generation scales the radius",
         lambda w, p, x: (_in_lone(w, "WobbledRadius(radius, (float)Math.Atan2", "WobbledRadius(radius * 1.5f, (float)Math.Atan2"), p, x)),
        ("bigger centre jitter",
         lambda w, p, x: (_in_lone(w, "Rand.RangeInclusive(-size / 10, size / 10)", "Rand.RangeInclusive(-size / 4, size / 4)"), p, x)),
        ("def radiusFraction past the sweep",
         lambda w, p, x: (w, p, x.replace("<radiusFraction>0.18~0.26</radiusFraction>", "<radiusFraction>0.18~0.40</radiusFraction>"))),
        ("stronger harmonics", lambda w, p, x: (_in_lone(w, "Harmonics(3, 0.12f)", "Harmonics(3, 0.3f)"), p, x)),
    ]
    for name, mutate in mutants:
        mw, mp, mx = mutate(workers, program, xml)
        if (mw, mp, mx) == (workers, program, xml):
            print("FAIL parity planted negative '%s': the mutation did not apply (source changed shape?)" % name)
            ok = False
            continue
        caught = bool(parity_fails(mw, mp, mx))
        print("%s parity planted negative caught: %s" % ("PASS" if caught else "FAIL", name))
        ok &= caught
    return ok


def main():
    if not parity_check():
        sys.exit("lone mountain source parity failed: the shipped worker is not the swept geometry")
    if not os.path.isfile(CSPROJ):
        sys.exit("RimMandrakeTileFeatures.SelfTest.csproj not found at %s" % CSPROJ)
    dotnet = next((c for c in DOTNET_CANDIDATES if os.path.isfile(c)), None)
    if dotnet is None:
        sys.exit("dotnet.exe not found at any of %r; UNMEASURED, not a pass or a fail" % DOTNET_CANDIDATES)
    win_csproj = windows_project_path(CSPROJ, whole_src=False)
    result = run_interop_captured([dotnet, "run", "--project", win_csproj, "-c", "Release"], capture_output=True, text=True)
    print(result.stdout, end="")
    if result.stderr.strip():
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode == 0 and "0 failed" not in result.stdout:
        sys.exit("dotnet exited 0 but printed no '0 failed' summary: the test program did not run to its end")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
