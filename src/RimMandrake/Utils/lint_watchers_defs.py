#!/usr/bin/env python3
"""Offline lint of the Watchers mod (defs/patches vs C#): the generic lint (lint_mod_defs.py) plus data checks it cannot see.

  wk-extension  every race carrying RM_WatcherExtension satisfies the kernel's ConfigErrors rules (0 < flinch <= watch, hide range valid,
                positive watch/bolt ticks, wanderChance and emergeWhenFoodBelow are probabilities), its hiddenHediff and signDef are defined in
                this mod, the sign is a RM_WatcherSign thing, and the medium list has no empty entries
  wk-keys       every "RM_Watchers_*".Translate() key used in C# exists in Languages/*/Keyed (the game shows the raw key)
  wk-kernel     the kernel is Verse-free, is listed in the csproj, and the step/check intervals the comp and driver use are the kernel's
  wk-patch      the Orders-menu patch adds a designator class that exists, and the flush job/work giver/designation names agree with [DefOf]

    python3 src/RimMandrake/Utils/lint_watchers_defs.py [--mod-dir <dir>] [--quiet]
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
DEFAULT_MOD = os.path.join(REPO, "src", "RimMandrake", "Watchers")


def read(p):
    return open(p, encoding="utf-8-sig").read()


def main(argv):
    quiet = "--quiet" in argv
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else DEFAULT_MOD
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("Watchers", ["--mod-dir", mod])
    gl = buf.getvalue().splitlines()
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs = [l for l in gl if l.startswith("ERROR")]
    warns = [l for l in gl if l.startswith("WARN")]
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    src = os.path.join(mod, "Source")
    n = {"extensions": 0, "keys": 0, "defof": 0}

    # wk-extension
    defs = {}
    every = []
    names = {}
    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        for d in ET.parse(p).getroot():
            if d.get("Name"):
                names[d.get("Name")] = d
            dn = d.findtext("defName")
            if dn:
                every.append((dn, d))
                if d.tag in ("ThingDef", "HediffDef") or dn not in defs:   # a PawnKindDef shares its ThingDef's defName
                    defs[dn] = d
    for dn, d in sorted(every, key=lambda x: x[0]):
        for li in d.iter("li"):
            if li.get("Class") != "RimMandrake.Watchers.RM_WatcherExtension":
                continue
            n["extensions"] += 1
            f = lambda k, default: li.findtext(k, default)
            try:
                fl, wr = float(f("flinchRadius", "6")), float(f("watchRadius", "14"))
                hmin, hmax = [int(x) for x in f("hideTicks", "2500~7500").split("~")]
                mw, bt = int(f("maxWatchTicks", "2500")), int(f("boltTicks", "1200"))
                wc, em, geo = float(f("wanderChance", "0.15")), float(f("emergeWhenFoodBelow", "0.25")), float(f("geophoneMinBodySize", "0"))
            except ValueError as e:
                E("wk-extension", f"{dn}: unparsable number in the watcher extension: {e}")
                continue
            if fl <= 0 or wr < fl:
                E("wk-extension", f"{dn}: need 0 < flinchRadius <= watchRadius, has {fl} / {wr}")
            if hmin <= 0 or hmax < hmin:
                E("wk-extension", f"{dn}: hideTicks {hmin}~{hmax} invalid")
            if mw <= 0 or bt <= 0:
                E("wk-extension", f"{dn}: maxWatchTicks {mw} and boltTicks {bt} must be positive")
            if not 0 <= wc <= 1:
                E("wk-extension", f"{dn}: wanderChance {wc} is not a probability")
            if not 0 <= em <= 1:
                E("wk-extension", f"{dn}: emergeWhenFoodBelow {em} is not a food fraction (above 1 it would never watch)")
            if geo < 0:
                E("wk-extension", f"{dn}: geophoneMinBodySize {geo} is negative")
            hh, sd = f("hiddenHediff", ""), f("signDef", "")
            if hh not in defs:
                E("wk-extension", f"{dn}: hiddenHediff {hh!r} is not defined by this mod")
            sdef = defs.get(sd)
            if sdef is None:
                E("wk-extension", f"{dn}: signDef {sd!r} is not defined by this mod")
            else:
                cls, cur, hops = sdef.findtext("thingClass"), sdef, 0
                while cls is None and cur.get("ParentName") in names and hops < 8:
                    cur = names[cur.get("ParentName")]
                    cls, hops = cur.findtext("thingClass"), hops + 1
                if cls != "RimMandrake.Watchers.RM_WatcherSign":
                    E("wk-extension", f"{dn}: signDef {sd} thingClass is {cls!r}, not RimMandrake.Watchers.RM_WatcherSign")
            for t in li.findall("mediumTerrains/li"):
                if not (t.text or "").strip():
                    E("wk-extension", f"{dn}: an empty <li> in mediumTerrains")
    # wk-keys
    keyed = ""
    for p in glob.glob(os.path.join(mod, "Languages", "*", "Keyed", "*.xml")):
        keyed += read(p)
    code = "\n".join(read(p) for p in glob.glob(os.path.join(src, "**", "*.cs"), recursive=True) if os.sep + "SelfTest" + os.sep not in p)
    for k in sorted(set(re.findall(r'"(RM_Watchers_\w+)"\s*\.Translate', code))):
        n["keys"] += 1
        if f"<{k}>" not in keyed and f"<{k}>" not in keyed.replace(" ", ""):
            E("wk-keys", f'"{k}".Translate() has no <{k}> in Languages/*/Keyed (the game shows the raw key)')

    # wk-kernel
    kernel = read(os.path.join(src, "Kernel", "RM_WatcherKernel.cs"))
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kernel, flags=re.M):
        E("wk-kernel", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    csproj = read(os.path.join(src, "RM_Watchers.csproj"))
    if "Kernel\\RM_WatcherKernel.cs" not in csproj:
        E("wk-kernel", "RM_Watchers.csproj does not compile Kernel\\RM_WatcherKernel.cs (EnableDefaultCompileItems is false: it compiles into nothing)")
    for fn, const, want in (("RM_JobDriver_Watch.cs", "StepInterval", "RM_WatcherKernel.StepInterval"), ("RM_CompWatcher.cs", "CheckInterval", "RM_WatcherKernel.CheckInterval"),
                            ("RM_CompWatcher.cs", "NoMediumRecheckTicks", "RM_WatcherKernel.NoMediumRecheckTicks")):
        m = re.search(r"const int " + const + r" = ([^;]+);", read(os.path.join(src, fn)))
        if not m or m.group(1).strip() != want:
            E("wk-kernel", f"{fn} {const} = {m.group(1) if m else '(missing)'} is not an alias of {want}")
    for pat, what in ((r"CurLevelPercentage < ext\.emergeWhenFoodBelow\)\s*\{\s*return null", "a hand copy of the giver's hunger gate"),
                      (r"\.TicksGame \+ 7500", "a literal 7500 recheck instead of the kernel constant")):
        if re.search(pat, code):
            E("wk-kernel", f"{what} survives beside the kernel")

    # wk-patch
    for p in glob.glob(os.path.join(mod, "Patches", "*.xml")):
        for li in ET.parse(p).getroot().iter("li"):
            cls = (li.text or "").strip()
            if cls.startswith("RimMandrake.Watchers.") and not re.search(r"class " + re.escape(cls.split(".")[-1]) + r"\b", code):
                E("wk-patch", f"the Orders patch adds {cls}, which no source file declares")
    for fld in re.findall(r"public static \w+ (RM_\w+);", read(os.path.join(src, "RM_WatchersDefOf.cs"))):
        n["defof"] += 1
        if fld not in defs:
            E("wk-patch", f"[DefOf] field {fld} names no def in this mod")

    for k, mn in (("extensions", 1), ("keys", 3), ("defof", 4)):
        if n[k] < mn and not errs:
            print(f"LINT UNMEASURED: wk check {k} saw {n[k]} (< {mn}); a blind lint is not a pass")
            return 2
    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"watchers lint (data): {n['extensions']} watcher extension(s), {n['keys']} keys, {n['defof']} DefOf fields, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
