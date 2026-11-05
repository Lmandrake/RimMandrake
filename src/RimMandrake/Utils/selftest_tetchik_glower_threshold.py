#!/usr/bin/env python3
"""TETCHIK_GLOWER_THRESHOLD_MEASURE_SPARSE: the tetchik edge-arrival gate asks for ANY glower on the map.

The wild spawner grows RM_Glower as sparse strays (~12 on 200x200, ~19 on 250x250 from the defs), so a bar of 10
sat at the expected count and starved arrivals on small, mountainous or harvested maps. This reads the kernel and
the fuzz spec (Python only, no dotnet: the full fuzz is selftest_scarlands_fuzz.py) and checks:
  - RM_TetchikGateKernel.MinMapGlower == 1;
  - Allow still gates edge arrivals on `mapGlower >= MinMapGlower` (0 glower still refuses);
  - the fuzz's TetchikSpec bar and its constant assertion agree with the kernel;
  - the comments no longer promise a "stand" the spawner never grows.
A sanity probe runs the same checks on the pre-fix text (bar 10) and must see them fail.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src", "RimMandrake", "Scarlands", "Source")
KERNEL = os.path.join(SRC, "Kernel", "RM_TetchikGateKernel.cs")
FUZZ = os.path.join(SRC, "SelfTest", "ScarlandsFuzz.cs")


def problems(kernel, fuzz):
    out = []
    m = re.findall(r"public\s+const\s+int\s+MinMapGlower\s*=\s*(\d+)\s*;", kernel)
    if len(m) != 1:
        out.append("MinMapGlower declaration not found exactly once (%d)" % len(m))
    elif int(m[0]) != 1:
        out.append("MinMapGlower = %s, want 1" % m[0])
    if not re.search(r"return\s+entryCell\s*&&\s*mapGlower\s*>=\s*MinMapGlower\s*;", kernel):
        out.append("Allow no longer gates edge arrivals on mapGlower >= MinMapGlower")
    if re.search(r"glower stand|A stand, not a stray", kernel):
        out.append("kernel comment still promises a glower stand")
    spec = re.search(r"static bool TetchikSpec\(.*?\{(.*?)\n\s*\}", fuzz, re.S)
    bar = re.search(r"return\s+mapGlower\s*>=\s*(\d+)\s*;", spec.group(1)) if spec else None
    if not bar:
        out.append("fuzz TetchikSpec bar not found")
    elif int(bar.group(1)) != 1:
        out.append("fuzz TetchikSpec bar = %s, want 1" % bar.group(1))
    if not re.search(r"RM_TetchikGateKernel\.MinMapGlower\s*==\s*1\s*,", fuzz):
        out.append("fuzz does not assert MinMapGlower == 1")
    if not re.search(r"!RM_TetchikGateKernel\.Allow\(true,\s*false,\s*0\)", fuzz):
        out.append("fuzz lost the glowerless-map refusal row")
    return out


def main():
    kernel = open(KERNEL, encoding="utf-8").read()
    fuzz = open(FUZZ, encoding="utf-8").read()
    fails = problems(kernel, fuzz)
    # sanity probe: the instrument must see the pre-fix bar of 10
    old_k = re.sub(r"(MinMapGlower\s*=\s*)\d+", r"\g<1>10", kernel)
    old_f = re.sub(r"(return\s+mapGlower\s*>=\s*)1(\s*;)", r"\g<1>10\2", fuzz)
    probe = problems(old_k, old_f)
    if not any("want 1" in p for p in probe):
        fails.append("instrument: a bar of 10 was not detected")
    for f in fails:
        print("FAIL " + f)
    if fails:
        print("RESULT FAIL tetchik glower threshold (%d)" % len(fails))
        return 1
    print("ok tetchik MinMapGlower == 1, edge gate mapGlower >= MinMapGlower, fuzz spec agrees, probe sees bar 10")
    print("RESULT OK tetchik glower threshold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
