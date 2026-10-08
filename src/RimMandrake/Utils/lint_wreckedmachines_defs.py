#!/usr/bin/env python3
"""Offline lint of WreckedMachines (mandrake.rm.wreckedmachines): the generic mod lint (lint_mod_defs.py) plus data checks it cannot see.

  wm-ladder   every def carrying WreckedMachineGrade names a known grade and a line; each line has Wrecked, Kludged and Refurbished exactly
              once (the ladder's only way in is a Wrecked base), every def's replaceTags contains its line (stepping up is vanilla replaceTags),
              and all defs of a line agree on the donor `original`
  wm-thought  the salvaged-emanator thought has one stage per emanating grade, and its shipped stage moods equal vanilla's soothe (5) x the
              default ratios (the patcher rewrites them at startup; a different shipped number would flash wrong until then)
  wm-kernel   the kernel is Verse-free and compiled by the csproj; the slider ranges in the settings window equal the kernel's caps; the
              default ratios are inside them and ordered; no hand copy of the ladder survives beside the kernel

    python3 src/RimMandrake/Utils/lint_wreckedmachines_defs.py [--mod-dir <dir>] [--quiet]
"""
import contextlib
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DEFAULT_MOD = os.path.join(REPO, "src", "RimMandrake", "WreckedMachines")
GRADES = ("Wrecked", "Kludged", "Refurbished", "Original")


def read(p):
    return open(p, encoding="utf-8-sig").read()


def main(argv):
    quiet = "--quiet" in argv
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else DEFAULT_MOD
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("WreckedMachines", ["--mod-dir", mod])
    gl = buf.getvalue().splitlines()
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs = [l for l in gl if l.startswith("ERROR")]
    warns = [l for l in gl if l.startswith("WARN")]
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    src = os.path.join(mod, "Source")
    n = {"graded": 0, "lines": 0, "stages": 0, "sliders": 0}

    lines = {}
    thought = None
    names = {}
    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        for d in ET.parse(p).getroot():
            if d.get("Name"):
                names[d.get("Name")] = d

    def tags_of(d):
        cur, hops = d, 0
        while cur is not None and hops < 8:
            ts = [t.text for t in cur.findall("replaceTags/li")]
            if ts:
                return ts
            cur, hops = names.get(cur.get("ParentName")), hops + 1
        return []

    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        for d in ET.parse(p).getroot():
            dn = d.findtext("defName")
            if d.tag == "ThoughtDef" and dn == "RM_WM_SalvagedEmanatorSoothe":
                thought = d
            for li in d.findall("modExtensions/li"):
                if li.get("Class") != "RimMandrake.WreckedMachines.WreckedMachineGrade":
                    continue
                n["graded"] += 1
                grade, line, orig = li.findtext("grade", "Wrecked"), li.findtext("line"), li.findtext("original")
                if grade not in GRADES:
                    E("wm-ladder", f"{dn}: unknown grade {grade!r}")
                if not line:
                    E("wm-ladder", f"{dn}: no line (the ladder cannot find what is underneath)")
                    continue
                tags = tags_of(d)
                if line not in tags:
                    E("wm-ladder", f"{dn}: replaceTags {tags} does not contain its line {line!r} (the step-up would not replace the lower grade)")
                lines.setdefault(line, []).append((grade, dn, orig, li.findtext("emanates") == "true"))
    for line, rows in sorted(lines.items()):
        n["lines"] += 1
        grades = [g for g, _, _, _ in rows]
        for need in ("Wrecked", "Kludged", "Refurbished"):
            if grades.count(need) != 1:
                E("wm-ladder", f"line {line}: grade {need} appears {grades.count(need)} times (needs exactly one)")
        if len({o for _, _, o, _ in rows}) > 1:
            E("wm-ladder", f"line {line}: its defs name different donor originals {sorted({o or '-' for _, _, o, _ in rows})}")
    emanating = sorted({g for rows in lines.values() for g, _, _, em in rows if em})
    if thought is None:
        E("wm-thought", "RM_WM_SalvagedEmanatorSoothe is not defined")
    else:
        moods = [float(s.findtext("baseMoodEffect", "0")) for s in thought.findall("stages/li")]
        n["stages"] = len(moods)
        want_grades = [g for g in emanating if g != "Wrecked"]
        if len(moods) != len(want_grades):
            E("wm-thought", f"the thought has {len(moods)} stages for emanating grades {want_grades}")
        dflt = {"Kludged": 0.2, "Refurbished": 0.75}
        for i, g in enumerate(want_grades[: len(moods)]):
            if g in dflt and abs(moods[i] - 5.0 * dflt[g]) > 1e-3:
                E("wm-thought", f"stage {i} ({g}) ships mood {moods[i]}, vanilla soothe 5 x default ratio {dflt[g]} = {5.0 * dflt[g]}")

    kernel = read(os.path.join(src, "Kernel", "RM_WreckedMachinesKernel.cs"))
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kernel, flags=re.M):
        E("wm-kernel", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    if "Kernel\\RM_WreckedMachinesKernel.cs" not in read(os.path.join(src, "RM_WreckedMachines.csproj")):
        E("wm-kernel", "RM_WreckedMachines.csproj does not compile Kernel\\RM_WreckedMachinesKernel.cs (EnableDefaultCompileItems is false: it compiles into nothing)")
    mod_cs = read(os.path.join(src, "WreckedMachinesMod.cs"))
    caps = {k: float(v) for k, v in re.findall(r"\b(WreckedMax|KludgedMax|RefurbishedMax) = ([0-9.]+)f", kernel)}
    for fld, cap in (("wreckedRatio", "WreckedMax"), ("kludgedRatio", "KludgedMax"), ("refurbishedRatio", "RefurbishedMax")):
        n["sliders"] += 1
        m = re.search(fld + r" = list\.Slider\(" + fld + r", ([0-9.]+)f, ([0-9.]+)f\)", mod_cs)
        d = re.search(r"public static float " + fld + r" = ([0-9.]+)f;", mod_cs)
        if not m or not d or cap not in caps:
            E("wm-kernel", f"cannot read the {fld} slider / default / kernel cap")
            continue
        if float(m.group(2)) != caps[cap]:
            E("wm-kernel", f"{fld} slider tops out at {m.group(2)}, the kernel's {cap} is {caps[cap]} (the slider would promise a ratio the ladder refuses)")
        if not float(m.group(1)) <= float(d.group(1)) <= float(m.group(2)):
            E("wm-kernel", f"{fld} default {d.group(1)} is outside its slider {m.group(1)}..{m.group(2)}")
    dv = [float(re.search(r"public static float " + f + r" = ([0-9.]+)f;", mod_cs).group(1)) for f in ("wreckedRatio", "kludgedRatio", "refurbishedRatio")]
    if not (dv[0] <= dv[1] <= dv[2] < 1):
        E("wm-kernel", f"default ratios {dv} are not ordered below the original")
    code = "\n".join(re.sub(r"//.*", "", read(p)) for p in glob.glob(os.path.join(src, "*.cs")))
    for pat, what in ((r"case MachineGrade\.Kludged: return WreckedMachinesSettings", "a hand copy of the ratio ladder"),
                      (r"Mathf\.RoundToInt\(entry\.count", "a hand copy of the material scaler"), (r"originalBase >= 0f\) return;", "a hand copy of the producer test")):
        if re.search(pat, code):
            E("wm-kernel", f"{what} survives beside the kernel")

    for k, mn in (("graded", 6), ("lines", 3), ("stages", 2), ("sliders", 3)):
        if n[k] < mn and not errs:
            print(f"LINT UNMEASURED: wm check {k} saw {n[k]} (< {mn}); a blind lint is not a pass")
            return 2
    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"wreckedmachines lint (data): {n['graded']} graded defs, {n['lines']} lines, {n['stages']} thought stages, {n['sliders']} sliders, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
