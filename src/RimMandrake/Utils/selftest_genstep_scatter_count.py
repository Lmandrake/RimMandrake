#!/usr/bin/env python3
"""Lint: every GenStepDef whose genStep is a GenStep_Scatterer subclass must set <count> or
<countPer10kCellsRange>. Scatterer defaults are count=-1 and countPer10kCellsRange=Zero, so CalculateFinalCount
is 0 and the step runs zero times, silently (decomp rw16 Verse/GenStep_Scatterer.cs; lesson
20261026T060425Z-FOUNDRY-scattergroup-needs-count; Lantern Deeps 80c122a7b3).
Custom C# classes deriving GenStep directly (own logic) are exempt. FlowWorks/GSS are out of scope.
    python3 src/RimMandrake/Utils/selftest_genstep_scatter_count.py
"""
import os, re, sys
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


def main():
    bases = cs_bases()
    bad, n = [], 0
    for p in walk(".xml"):
        t = open(p, encoding="utf-8-sig", errors="replace").read()
        if "<genStep" not in t:
            continue
        try:
            root = ET.fromstring(t.encode("utf-8"))
        except ET.ParseError:
            continue
        for d in root.iter("GenStepDef"):
            g = d.find("genStep")
            if g is None or not g.get("Class") or not is_scatterer(g.get("Class"), bases):
                continue
            n += 1
            if g.find("count") is None and g.find("countPer10kCellsRange") is None:
                bad.append("%s: %s (%s) has no <count>/<countPer10kCellsRange> -> scatters zero times"
                           % (os.path.relpath(p, ROOT), d.findtext("defName"), g.get("Class")))
    for b in bad:
        print("FAIL " + b)
    print("%d scatterer GenStepDefs checked, %d bad" % (n, len(bad)))
    if n == 0:
        print("FAIL instrument blind: 0 scatterer defs found")
        return 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
