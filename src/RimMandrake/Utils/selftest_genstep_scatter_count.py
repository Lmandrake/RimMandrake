#!/usr/bin/env python3
"""Lint: every GenStepDef whose genStep is a GenStep_Scatterer subclass must set <count> or
<countPer10kCellsRange>. Scatterer defaults are count=-1 and countPer10kCellsRange=Zero, so CalculateFinalCount
is 0 and the step runs zero times, silently (decomp rw16 Verse/GenStep_Scatterer.cs; lesson
20261026T060425Z-FOUNDRY-scattergroup-needs-count; Lantern Deeps 80c122a7b3).
Custom C# classes deriving GenStep directly (own logic) are exempt. FlowWorks/GSS are out of scope.

Second check, density truncation (SCATTER_AUDIT_DENSITY_TRUNCATES_ZERO; lesson
20261026T101908Z-FOUNDRY-scatter-density-int-truncation). A count that rounds to 0 also places nothing:
  * countPer10kCellsRange: CountFromPer10kCells = RoundToInt(size^2 / RoundToInt(10000/c))
    (GenStep_Scatterer.cs 266-274). FAIL if the range MIDPOINT on a 250x250 map rounds to 0 -- or, for a
    genstep listed in a pocket map's MapGeneratorDef (directly or via a patch), on the smallest
    pocketMapSize that generator is opened with (Lantern Deeps is 66x66: 1 per 10k there is 0.44 -> 0).
  * ScatterGroup groups: a cluster covers (int)(validCells/10 * coveredCellsPer10Cells) cells
    (GenStep_ScatterGroup.cs 240-243), validCells <= (2r+1)^2. FAIL if the MIDPOINT density at the
    SMALLEST clusterRectRadius truncates to 0 even with every rect cell valid (an upper bound, so a
    FAIL is certain, a pass is not). Things are assumed 1x1 (a bigger footprint only makes it worse).
    A group with <spawnAtCenter> always places that one thing, so its coverage is not checked.
    python3 src/RimMandrake/Utils/selftest_genstep_scatter_count.py [--table]
"""
import os, re, struct, sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SKIP = ("FlowWorks", "GSS")


OVERRIDES = set()  # classes that compute their own count (e.g. RM_GenStep_WreckField via densityClass)


def walk(ext):
    for r, d, fs in os.walk(os.path.join(ROOT, "src")):
        if any(s in r.split(os.sep) or s in r for s in SKIP):
            continue
        for f in fs:
            if f.endswith(ext):
                yield os.path.join(r, f)


def cs_bases():
    """class -> base name; also fills OVERRIDES with classes declaring `override ... CalculateFinalCount`."""
    out = {}
    pat = re.compile(r"\bclass\s+(\w+)\s*:\s*([\w.]+)")
    for p in walk(".cs"):
        try:
            src = open(p, encoding="utf-8-sig", errors="replace").read()
            ms = list(pat.finditer(src))
            for i, m in enumerate(ms):
                out[m.group(1)] = m.group(2).split(".")[-1]
                body = src[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(src)]
                if re.search(r"override\s+int\s+CalculateFinalCount", body):
                    OVERRIDES.add(m.group(1))
        except OSError:
            pass
    return out


def is_scatterer(cls, bases):
    name = cls.split(".")[-1]
    seen = set()
    while name and name not in seen:
        seen.add(name)
        if name in OVERRIDES:
            return False
        if name == "GenStep":
            return False
        if name == "GenStep_Scatterer":
            return True
        if name not in bases:
            return name.startswith("GenStep_Scatter")  # vanilla subclass
        name = bases[name]
    return False


def f32(x):
    """Round to IEEE single precision, as the C# float arithmetic does."""
    return struct.unpack("f", struct.pack("f", x))[0]


def rng(el, conv=float):
    """Parse a FloatRange/IntRange element: 'a~b', 'a', or <min>/<max> children. None if unparsable."""
    if el is None:
        return None
    if el.find("min") is not None or el.find("max") is not None:
        a, b = el.findtext("min"), el.findtext("max")
        a = b if a is None else a
        b = a if b is None else b
    else:
        txt = (el.text or "").strip()
        a, _, b = txt.partition("~")
        b = b or a
    try:
        return conv(a.strip()), conv(b.strip())
    except (ValueError, AttributeError):
        return None


def count_per10k(c, size):
    """Verse.GenStep_Scatterer.CountFromPer10kCells (Mathf.RoundToInt is banker's rounding, as is round())."""
    if c <= 0:
        return 0
    return round(f32(size * size) / f32(round(f32(10000.0 / c))))


def covered(cells, dens):
    """(int)((float)num / 10f * dens) from GenStep_ScatterGroup.CalculateScatterInformation."""
    return int(f32(f32(f32(cells) / 10.0) * f32(dens)))


GEN_XPATH = re.compile(r'MapGeneratorDef\[defName\s*=\s*["\']([^"\']+)["\']\]')


def pocket_sizes(roots):
    """GenStepDef defName -> smallest pocketMapSize of any pocket-map generator that lists it."""
    gen_size, members = {}, {}
    for root in roots:
        for el in root.iter():
            gen, size = el.findtext("pocketMapGenerator"), el.findtext("pocketMapSize")
            if gen and size and size.strip().isdigit():
                gen_size[gen.strip()] = min(int(size), gen_size.get(gen.strip(), 10 ** 6))
            if el.tag == "MapGeneratorDef" and el.findtext("defName"):
                for li in el.findall("genSteps/li"):
                    members.setdefault((li.text or "").strip(), set()).add(el.findtext("defName").strip())
            xp = el.findtext("xpath")
            m = GEN_XPATH.search(xp or "")
            if m and el.find("value") is not None:
                for li in el.find("value").iter("li"):
                    members.setdefault((li.text or "").strip(), set()).add(m.group(1))
    out = {}
    for step, gens in members.items():
        sizes = [gen_size[g] for g in gens if g in gen_size]
        if sizes:
            out[step] = min(sizes)
    return out


def density_problems(g, size=250):
    """Truncation-to-zero findings for one scatterer <genStep> on a size x size map, plus table rows."""
    probs, rows = [], []
    if g.find("count") is None:
        r = rng(g.find("countPer10kCellsRange"))
        if r is not None:
            mid = (r[0] + r[1]) / 2.0
            got = {sz: count_per10k(mid, sz) for sz in sorted({200, 250, 300, size})}
            rows.append("countPer10k %g~%g mid %g -> %s" % (r[0], r[1], mid,
                        " ".join("%d:%d" % kv for kv in sorted(got.items()))))
            if got[size] < 1:
                probs.append("countPer10kCellsRange %g~%g: midpoint scatters %d times on a %d map"
                             % (r[0], r[1], got[size], size))
    groups = g.find("groups")
    for i, li in enumerate(groups.findall("li") if groups is not None else []):
        things = li.find("things")
        if things is None or len(things) == 0 or li.find("spawnAtCenter") is not None:
            continue  # spawnAtCenter places its one thing whatever the coverage count says
        d, rr = rng(li.find("coveredCellsPer10Cells")), rng(li.find("clusterRectRadius"), int)
        d = d or (0.0, 0.0)
        rr = rr or (0, 0)
        mid = (d[0] + d[1]) / 2.0
        cmin, cmax = (2 * rr[0] + 1) ** 2, (2 * rr[1] + 1) ** 2
        lo, hi = covered(cmin, mid), covered(cmax, d[1])
        rows.append("group %d: covered %g~%g r%d~%d -> min-radius mid %d, max-radius max %d"
                    % (i, d[0], d[1], rr[0], rr[1], lo, hi))
        if lo < 1:
            probs.append("group %d coveredCellsPer10Cells %g~%g clusterRectRadius %d~%d: a radius-%d cluster "
                         "(%d cells) at midpoint %g covers %d cells -> places nothing"
                         % (i, d[0], d[1], rr[0], rr[1], rr[0], cmin, mid, lo))
    return probs, rows


def main():
    table = "--table" in sys.argv
    bases = cs_bases()
    bad, n = [], 0
    parsed = []
    for p in walk(".xml"):
        t = open(p, encoding="utf-8-sig", errors="replace").read()
        if "<genStep" not in t and "pocketMapGenerator" not in t and "MapGeneratorDef" not in t:
            continue
        try:
            parsed.append((p, ET.fromstring(t.encode("utf-8"))))
        except ET.ParseError:
            continue
    pocket = pocket_sizes(r for _, r in parsed)
    if not pocket:
        print("FAIL instrument blind: no pocket-map generator membership found (Lantern Deeps should be)")
        return 1
    for p, root in parsed:
        for d in root.iter("GenStepDef"):
            g = d.find("genStep")
            if g is None or not g.get("Class") or not is_scatterer(g.get("Class"), bases):
                continue
            n += 1
            if g.find("count") is None and g.find("countPer10kCellsRange") is None:
                bad.append("%s: %s (%s) has no <count>/<countPer10kCellsRange> -> scatters zero times"
                           % (os.path.relpath(p, ROOT), d.findtext("defName"), g.get("Class")))
            probs, rows = density_problems(g, pocket.get((d.findtext("defName") or "").strip(), 250))
            for pr in probs:
                bad.append("%s: %s %s" % (os.path.relpath(p, ROOT), d.findtext("defName"), pr))
            if table:
                for r in rows:
                    print("  %s %s" % (d.findtext("defName"), r))
    for b in bad:
        print("FAIL " + b)
    print("%d scatterer GenStepDefs checked, %d bad" % (n, len(bad)))
    if n == 0:
        print("FAIL instrument blind: 0 scatterer defs found")
        return 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
