#!/usr/bin/env python3
"""Static cross-check of Droidworks: XML defs <-> C# classes/fields, csproj <-> source files, string lookups, Scribe labels, [DefOf]
fields, the Mod Settings triple (static default / Scribe default / ResetToDefaults / slider range) and a few Droidworks-specific
agreements. No game, no build. Generic machinery: moddefs_lint.py (reuses the CreatureBehaviors defs checker's parser).

    python3 src/RimMandrake/Utils/selftest_droidworks_lint.py

Droidworks extras:
  - the RSW_DW_FormatTier hediff stages cut at 0 / 1.5 / 2.5 / 3.5 and its min/initial/max severities agree with the kernel ladder
  - nothing may call GetModExtension<DroidworksExtension>() (first-wins: it returns the FAMILY's copy and ignores a race override);
    use DroidworksExtension.OfRace
  - every DroidworksExtension carries a chassisClass in 0..7 and every race resolves one
  - DroidworksKernel.cs stays free of Verse/UnityEngine (the SelfTest project compiles it on plain net8.0)
Then it PLANTS a break of each kind into the in-memory inputs and proves each is caught (a lint that cannot fail proves nothing).
"""
import copy
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import moddefs_lint as ml  # noqa: E402

MOD = os.path.join(ml.SRC, "RimStarWars", "Droidworks")
CFG_NAME = "Droidworks"


def extra(ctx, findings, counts):
    inp = ctx.inp
    # 1. format-tier hediff stage cuts
    path = os.path.join(MOD, "Defs", "HediffDefs", "HediffDefs_Droidworks.xml")
    root = ET.fromstring(inp.xml.get(path, ml._read(path)).encode("utf-8"))
    cuts = None
    for d in root.iter("HediffDef"):
        if d.findtext("defName") == "RSW_DW_FormatTier":
            cuts = [float(s.findtext("minSeverity")) for s in d.find("stages")]
            mn, mx, ini = float(d.findtext("minSeverity")), float(d.findtext("maxSeverity")), float(d.findtext("initialSeverity"))
            if cuts != [0.0, 1.5, 2.5, 3.5]:
                findings.append(("FORMAT_LADDER", path, 0, "RSW_DW_FormatTier stage cuts are %s, the kernel ladder (TierForSeverity) assumes [0, 1.5, 2.5, 3.5]" % cuts))
            if (mn, mx) != (1.0, 4.0):
                findings.append(("FORMAT_LADDER", path, 0, "RSW_DW_FormatTier severity range is %s..%s, SeverityFor yields 1..4" % (mn, mx)))
            if int(round(ini)) - 1 != 2:
                findings.append(("FORMAT_LADDER", path, 0, "initialSeverity %s is not the kernel DefaultTier (Programmable = severity 3)" % ini))
    counts["format tier stages"] = len(cuts or [])
    # 2. GetModExtension<DroidworksExtension> is first-wins
    n = 0
    for p, raw in inp.cs.items():
        nocom = ml.mask(raw, True)
        for m in re.finditer(r"GetModExtension\s*<\s*DroidworksExtension\s*>", nocom):
            n += 1
            findings.append(("FIRST_WINS_EXTENSION", p, ml._line(nocom, m.start()),
                             "GetModExtension<DroidworksExtension>() returns the family abstract's inherited copy, not the race's own; use DroidworksExtension.OfRace"))
    counts["GetModExtension<DroidworksExtension> (want 0)"] = n
    # 3. chassisClass range on every DroidworksExtension in every Defs file
    n_ext = 0
    for p, t in inp.xml.items():
        try:
            r = ET.fromstring(t.encode("utf-8"))
        except ET.ParseError:
            continue
        for el in r.iter("li"):
            if (el.get("Class") or "").endswith(".DroidworksExtension"):
                n_ext += 1
                cc = el.findtext("chassisClass")
                if cc is not None and not (cc.strip().isdigit() and 0 <= int(cc) <= 7):
                    findings.append(("CHASSIS_CLASS", p, 0, "chassisClass '%s' is outside 0..7" % cc))
    counts["DroidworksExtension nodes"] = n_ext
    # 4. kernel purity
    kp, kt = ctx.cs_text("DroidworksKernel.cs")
    if kt is None:
        findings.append(("KERNEL_PURE", MOD, 0, "DroidworksKernel.cs not found"))
    else:
        for bad in ("using Verse", "using UnityEngine", "using RimWorld"):
            if bad in ml.mask(kt, True):
                findings.append(("KERNEL_PURE", kp, 0, "contains '%s': the SelfTest project compiles this file on plain net8.0" % bad))
        counts["kernel purity"] = 1


def config():
    return ml.Cfg(
        CFG_NAME, MOD, ["RimMandrake.StarWars.Droidworks"],
        [(os.path.join(MOD, "Source", "Droidworks"), os.path.join(MOD, "Source", "Droidworks", "Droidworks.csproj")),
         (os.path.join(MOD, "Source", "BoltCore"), os.path.join(MOD, "Source", "BoltCore", "DroidworksBoltCore.csproj"))],
        settings_classes=["RSW_DroidworksSettings"],
        min_probe={"classes": 60, "xml class refs": 100, "Class= nodes": 60, "settings fields": 30, "DefOf fields": 20, "Scribe labels": 30},
        extra=extra)


def planted(cfg, inp):
    """plant one break per kind into copies of the inputs; each must raise exactly its kind"""
    fails = []

    def trial(label, want, mutate):
        i2 = copy.copy(inp)
        i2.cs, i2.xml, i2.csproj = dict(inp.cs), dict(inp.xml), dict(inp.csproj)
        i2.defnames, i2.keys = set(inp.defnames), set(inp.keys)
        mutate(i2)
        f, _c = ml.check(cfg, i2)
        got = ml.kinds(f)
        ok = want in got
        print("%s planted %-26s -> %s" % ("ok  " if ok else "FAIL", label, ", ".join(sorted(got)) or "nothing"))
        if not ok:
            fails.append(label)

    def xml_sub(basename, old, new):
        def m(i2):
            for p in i2.xml:
                if os.path.basename(p) == basename and old in i2.xml[p]:
                    i2.xml[p] = i2.xml[p].replace(old, new, 1)
                    return
            raise AssertionError("fixture pattern %r not found in %s" % (old, basename))
        return m

    def cs_sub(basename, old, new):
        def m(i2):
            for p in i2.cs:
                if os.path.basename(p) == basename and old in i2.cs[p]:
                    i2.cs[p] = i2.cs[p].replace(old, new, 1)
                    return
            raise AssertionError("fixture pattern %r not found in %s" % (old, basename))
        return m

    trial("misspelt Class", "UNRESOLVED_CLASS", xml_sub("Races_Families.xml", "Droidworks.DroidworksExtension", "Droidworks.DroidworksExtensoin"))
    trial("misspelt field child", "UNKNOWN_FIELD", xml_sub("Races_Families.xml", "<powerFallPerDay>0.33</powerFallPerDay>", "<powerFalPerDay>0.33</powerFalPerDay>"))
    trial("enum value typo (nested li)", "BAD_VALUE", xml_sub("TraitDefs_Droidworks_Idiosyncrasies.xml", "<chassis>Protocol</chassis>", "<chassis>Protokol</chassis>"))
    trial("non-numeric int", "BAD_VALUE", xml_sub("Races_Families.xml", "<chassisClass>1</chassisClass>", "<chassisClass>one</chassisClass>"))

    def drop_compile(i2):
        for p in i2.csproj:
            if p.endswith("Droidworks.csproj") and "BoltCore" not in p:
                i2.csproj[p] = i2.csproj[p].replace('<Compile Include="DroidworksKernel.cs" />', "", 1)
    trial("csproj drops the kernel", "CSPROJ_MISSING", drop_compile)
    trial("bogus def literal", "STRING_LITERAL", cs_sub("DroidAssembly.cs", '"RSW_DW_Head_Labour"', '"RSW_DW_Head_Labor"'))
    trial("duplicate Scribe label", "SCRIBE_DUP", cs_sub("CompDWServiceRecord.cs", 'Scribe_Values.Look(ref lastResetTick, "lastResetTick", -1);',
                                                       'Scribe_Values.Look(ref lastResetTick, "lastResetTick", -1); Scribe_Values.Look(ref lastResetTick, "lastResetTick", -1);'))
    trial("settings default drift", "SETTINGS_DRIFT", cs_sub("RSW_DroidworksSettings.cs", 'Scribe_Values.Look(ref driftTime, "driftTime", 1f, true);',
                                                          'Scribe_Values.Look(ref driftTime, "driftTime", 2f, true);'))
    trial("settings reset drift", "SETTINGS_DRIFT", cs_sub("RSW_DroidworksSettings.cs", "personalityDrift = true;\n            driftTime = 1f;", "personalityDrift = true;\n            driftTime = 1.5f;"))
    trial("DefOf names no def", "DEFOF_MISSING", cs_sub("DroidworksDefOf.cs", "RSW_DW_Part_Leg;", "RSW_DW_Part_Legg;"))
    trial("first-wins extension", "FIRST_WINS_EXTENSION", cs_sub("Need_Power.cs", "DroidworksExtension.OfRace(pawn.def)", "pawn.def.GetModExtension<DroidworksExtension>()"))
    trial("hediff ladder moved", "FORMAT_LADDER", xml_sub("HediffDefs_Droidworks.xml", "<minSeverity>2.5</minSeverity>", "<minSeverity>2.6</minSeverity>"))
    trial("kernel imports Unity", "KERNEL_PURE", cs_sub("DroidworksKernel.cs", "using System;", "using System;\nusing UnityEngine;"))
    return fails


def main(argv):
    cfg = config()
    inp = ml.collect(cfg)
    findings, counts = ml.check(cfg, inp)
    rc = ml.report(cfg, findings, counts, quiet="--quiet" in argv)
    if rc:
        return rc
    print("-- planted breaks")
    pf = planted(cfg, inp)
    if pf:
        print("droidworks lint self-proof: %d planted break(s) NOT caught: %s" % (len(pf), ", ".join(pf)))
        return 1
    print("droidworks lint self-proof: every planted break caught")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
