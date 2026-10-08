#!/usr/bin/env python3
"""Offline lint of TitanicCreatures (mandrake.rm.titaniccreatures): the generic mod lint (lint_mod_defs.py) plus data checks it cannot see.

  tc-ladder     exactly one RM_TitanicTierDef, 0 < t1 < t2 < t3, and the C# field initialisers (the hardcoded fallback used when the
                XML fails to load) agree with the shipped XML
  tc-crush      every RM_CrushRuleDef row names exactly one of thing / category, minTier is T1|T2|T3, no two rows share a target, and
                the Chunks row still protects (crushable false): chunks are a named "needs individual ruling" case
  tc-keys       every "RM_TitanicCorpseSite_*".Translate() key in C# exists in Languages/*/Keyed
  tc-kernel     the kernel is Verse-free, the csproj keeps SelfTest out of the mod assembly, the kernel's day length is GenDate's 60000
                and its crush damage numbers are the ones the settings text promises (light < heavy)
  tc-defof      every [DefOf] field of the mod names a def its XML defines

    python3 src/RimMandrake/Utils/lint_titaniccreatures_defs.py [--quiet] [--mod-dir D]
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
DEFAULT_MOD = os.path.join(REPO, "src", "RimMandrake", "TitanicCreatures")


def read(p):
    return open(p, encoding="utf-8-sig").read()


def main(argv):
    quiet = "--quiet" in argv
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else DEFAULT_MOD
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("TitanicCreatures", ["--mod-dir", mod])
    gl = buf.getvalue().splitlines()
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs = [l for l in gl if l.startswith("ERROR")]
    warns = [l for l in gl if l.startswith("WARN")]
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    src = os.path.join(mod, "Source")
    n = {"tiers": 0, "rules": 0, "keys": 0, "defof": 0}

    # tc-ladder
    tiers = []
    for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True):
        for d in ET.parse(p).getroot():
            if d.tag.endswith("RM_TitanicTierDef"):
                tiers.append(d)
    n["tiers"] = len(tiers)
    if len(tiers) != 1:
        E("tc-ladder", f"{len(tiers)} RM_TitanicTierDef defs (exactly one is the size-ladder authority; the mod reads whichever loads first)")
    else:
        v = [float(tiers[0].findtext(k, "nan")) for k in ("t1MinBodySize", "t2MinBodySize", "t3MinBodySize")]
        if not (0 < v[0] < v[1] < v[2]):
            E("tc-ladder", f"tier floors {v} are not 0 < t1 < t2 < t3")
        td = read(os.path.join(src, "Tiering", "RM_TitanicTierDef.cs"))
        cs = [float(x) for x in re.findall(r"public float t[123]MinBodySize = ([0-9.]+)f;", td)]
        if cs != v:
            E("tc-ladder", f"C# fallback floors {cs} differ from the shipped XML {v} (the XML-missing fallback would tier differently)")

    # tc-crush
    seen = {}
    rows = []
    for p in glob.glob(os.path.join(mod, "Defs", "CrushRuleDefs", "*.xml")):
        for d in ET.parse(p).getroot():
            rows.append(d)
    for d in rows:
        n["rules"] += 1
        dn = d.findtext("defName")
        th, ca = d.findtext("thing"), d.findtext("category")
        if bool(th) == bool(ca):
            E("tc-crush", f"{dn}: needs exactly one of <thing>/<category>, has thing={th!r} category={ca!r}")
        key = ("thing", th) if th else ("category", ca)
        if key in seen:
            E("tc-crush", f"{dn} and {seen[key]} target the same {key[0]} {key[1]} (last loaded wins silently)")
        seen[key] = dn
        if d.findtext("minTier") not in ("T1", "T2", "T3"):
            E("tc-crush", f"{dn}: minTier {d.findtext('minTier')!r} is not T1/T2/T3")
        if d.findtext("crushable") not in ("true", "false"):
            E("tc-crush", f"{dn}: crushable {d.findtext('crushable')!r} is not true/false")
    chunks = [d for d in rows if d.findtext("category") == "Chunks"]
    if not chunks or chunks[0].findtext("crushable") != "false":
        E("tc-crush", "the Chunks row is missing or crushable (chunks are deliberately protected until individually ruled)")

    # tc-keys
    keyed = ""
    for p in glob.glob(os.path.join(mod, "Languages", "*", "Keyed", "*.xml")):
        keyed += read(p)
    code = "\n".join(read(p) for p in glob.glob(os.path.join(src, "**", "*.cs"), recursive=True) if os.sep + "SelfTest" + os.sep not in p)
    for k in sorted(set(re.findall(r'"(RM_Titanic\w+)"\s*\.Translate', code))):
        n["keys"] += 1
        if f"<{k}>" not in keyed:
            E("tc-keys", f'"{k}".Translate() has no <{k}> in Languages/*/Keyed (the game shows the raw key)')

    # tc-kernel
    kp = os.path.join(src, "Kernel", "RM_TitanicKernel.cs")
    kernel = read(kp)
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kernel, flags=re.M):
        E("tc-kernel", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    csproj = read(os.path.join(src, "RM_TitanicCreatures.csproj"))
    if 'Compile Remove="SelfTest' not in csproj and 'EnableDefaultCompileItems>false' not in csproj:
        E("tc-kernel", "the csproj does not keep Source/SelfTest out of the mod assembly (a second Main and the fuzz would compile into the mod)")
    m = re.search(r"public const int TicksPerDay = (\d+);", kernel)
    if not m or m.group(1) != "60000":
        E("tc-kernel", f"kernel TicksPerDay is {m.group(1) if m else '(missing)'}, GenDate.TicksPerDay is 60000")
    lh = re.findall(r"public const float CrushDamage(Light|Heavy) = ([0-9.]+)f;", kernel)
    d = dict(lh)
    if set(d) != {"Light", "Heavy"} or not float(d["Light"]) < float(d["Heavy"]):
        E("tc-kernel", f"kernel crush damages {d} are not light < heavy")

    # tc-defof
    defs_text = "\n".join(read(p) for p in glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True))
    for f in glob.glob(os.path.join(src, "*DefOf.cs")):
        for dn in re.findall(r"public static \w+ (RM_\w+);", read(f)):
            n["defof"] += 1
            if f"<defName>{dn}</defName>" not in defs_text:
                E("tc-defof", f"[DefOf] field {dn} names no def in this mod's XML (silently null at runtime)")

    for k, mn in (("tiers", 1), ("rules", 4), ("keys", 2), ("defof", 2)):
        if n[k] < mn and not errs:
            print(f"LINT UNMEASURED: tc check {k} saw {n[k]} (< {mn}); a blind lint is not a pass")
            return 2
    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"titaniccreatures lint (data): {n['tiers']} tier def, {n['rules']} crush rows, {n['keys']} keys, {n['defof']} DefOf fields, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
