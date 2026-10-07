#!/usr/bin/env python3
"""Static cross-check of the Abyss: XML defs <-> C# classes/fields, csproj <-> source files, string lookups, Scribe labels, the Mod Settings
class (Scribed with the declared default), plus Abyss-specific agreements. No game, no build. Generic machinery: moddefs_lint.py.

    python3 src/RimMandrake/Utils/selftest_abyss_lint.py

Abyss extras:
  - RM_AbyssKernel.cs / RM_AbyssStateKernel.cs stay free of Verse/UnityEngine (the AbyssFuzz project compiles them on plain net8.0)
  - every field of the four kernel state structs (GustState, StormState, CoverState, SoundState) is Scribed by its component under the
    SAME label the saves already use (renaming a label silently resets saved state), except the two scheduler timers that were never saved
  - the three weather names the kernel keys on are WeatherDefs; the RM_Murk hediff and the sound defs the components look up exist
  - the per-biome probe extension and the brood/wreck extensions point at classes that exist (via the generic class checks)
Then it PLANTS a break of each kind into the in-memory inputs and proves each is caught.
"""
import copy
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import moddefs_lint as ml  # noqa: E402

MOD = os.path.join(ml.SRC, "RimMandrake", "Abyss")

# kernel struct -> (component file, {field: expected Scribe label}) ; fields not listed are intentionally not saved
STATE_SCRIBES = {
    "GustState": ("RM_GustController.cs", {"average": "average", "startTick": "gustStartTick", "endTick": "gustEndTick", "count": "gustCount"}),
    "StormState": ("RM_MapComponentDark.cs", {"nextRumbleTick": "nextRumbleTick", "pendingFlashTick": "pendingFlashTick", "pendingSumm": "pendingSummCome"}),
    "CoverState": ("RM_MapComponentShipCover.cs", {"cover": "cover", "coveredTicks": "coveredTicks", "cooldownUntil": "cooldownUntil", "nextProbeTick": "nextProbeTick"}),
    "SoundState": ("RM_AbyssSoundscape.cs", {"lastGustCount": "lastGustCount"}),
}
NOT_SAVED = {"SoundState": {"pendingRustleTick", "nextGrainTick"}}
WEATHERS = ["RM_AbyssDark", "RM_AbyssUnveiling", "RM_AbyssWitchfire"]


def extra(ctx, findings, counts):
    inp = ctx.inp
    # 1. kernel purity
    n = 0
    for name in ("RM_AbyssKernel.cs", "RM_AbyssStateKernel.cs"):
        kp, kt = ctx.cs_text(name)
        if kt is None:
            findings.append(("KERNEL_PURE", MOD, 0, "%s not found" % name))
            continue
        n += 1
        for bad in ("using Verse", "using UnityEngine", "using RimWorld"):
            if bad in ml.mask(kt, True):
                findings.append(("KERNEL_PURE", kp, 0, "contains '%s': the AbyssFuzz project compiles this file on plain net8.0" % bad))
    counts["kernel files"] = n
    # 2. state structs <-> Scribe labels
    _kp, kt = ctx.cs_text("RM_AbyssStateKernel.cs")
    n_fields = 0
    for struct, (comp, labels) in STATE_SCRIBES.items():
        m = re.search(r"public struct %s\s*\{(.*?)public static %s Fresh" % (struct, struct), kt or "", re.S)
        if not m:
            findings.append(("STATE_SCRIBE", MOD, 0, "kernel struct %s not found" % struct))
            continue
        fields = []
        for fm in re.finditer(r"public\s+(?:float|int|bool)\s+([^;]+);", m.group(1)):
            fields += [x.strip() for x in fm.group(1).split(",")]
        cp, ct = ctx.cs_text(comp)
        body = ml.mask(ct or "", True)
        for f in fields:
            n_fields += 1
            if f in NOT_SAVED.get(struct, ()):
                continue
            want = labels.get(f)
            if want is None:
                findings.append(("STATE_SCRIBE", cp or comp, 0, "%s.%s has no expected Scribe label recorded in the lint (new field? decide if it is saved)" % (struct, f)))
                continue
            if not re.search(r'Scribe_Values\.Look\(\s*ref\s+\w+\.%s\s*,\s*"%s"' % (re.escape(f), re.escape(want)), body):
                findings.append(("STATE_SCRIBE", cp or comp, 0, 'component does not Scribe %s.%s under the label "%s" (saves would silently reset it)' % (struct, f, want)))
    counts["kernel state fields"] = n_fields
    # 3. defs the kernel and components key on
    weather_names = set()
    for p, t in ctx.xml_files(os.path.join(MOD, "Defs", "WeatherDefs")).items():
        weather_names.update(re.findall(r"<defName>\s*(\w+)\s*</defName>", t))
    for w in WEATHERS:
        if w not in weather_names:
            findings.append(("WEATHER_DEF", os.path.join(MOD, "Defs", "WeatherDefs"), 0, "WeatherDef %s (keyed on by RM_DarkKernel) does not exist" % w))
    counts["weather defs"] = len(WEATHERS)
    for needed in ("RM_Murk", "RM_AbyssGustImpact", "RM_AbyssGillRustle", "RM_AbyssGrainTick", "RM_AbyssLampClatter", "RM_DurrgakCairn", "RM_FoldLamp", "RM_Gharrek", "RM_Tholin", "RM_Wickwood"):
        if needed not in inp.defnames:
            findings.append(("LOOKUP_DEF", MOD, 0, "%s is looked up by name in the components but no def of that name exists" % needed))
    counts["named lookups"] = 10


def config():
    return ml.Cfg(
        "Abyss", MOD, ["RimMandrake.Abyss"],
        [(os.path.join(MOD, "Source"), os.path.join(MOD, "Source", "RM_Abyss.csproj"))],
        settings_classes=["RM_AbyssSettings"],
        min_probe={"classes": 30, "xml class refs": 20, "Class= nodes": 10, "settings fields": 25, "Scribe labels": 25},
        extra=extra)


def planted(cfg, inp):
    fails = []

    def trial(label, want, mutate):
        i2 = copy.copy(inp)
        i2.cs, i2.xml, i2.csproj = dict(inp.cs), dict(inp.xml), dict(inp.csproj)
        i2.defnames, i2.keys = set(inp.defnames), set(inp.keys)
        mutate(i2)
        f, _c = ml.check(cfg, i2)
        if getattr(i2, "cleanup", None):
            i2.cleanup()
        got = ml.kinds(f)
        ok = want in got
        print("%s planted %-26s -> %s" % ("ok  " if ok else "FAIL", label, ", ".join(sorted(got)) or "nothing"))
        if not ok:
            fails.append(label)

    def sub(store, basename, old, new):
        def m(i2):
            d = getattr(i2, store)
            for p in d:
                if os.path.basename(p) == basename and old in d[p]:
                    d[p] = d[p].replace(old, new, 1)
                    return
            raise AssertionError("fixture pattern %r not found in %s" % (old, basename))
        return m

    trial("misspelt Class", "UNRESOLVED_CLASS", _first_class_sub(inp, "Krizzak"))
    trial("misspelt field child", "UNKNOWN_FIELD", _field_sub(inp))
    trial("csproj drops a kernel", "CSPROJ_MISSING", lambda i2: i2.csproj.update({p: t.replace('<Compile Include="RM_AbyssStateKernel.cs" />', "", 1) for p, t in i2.csproj.items()}))
    trial("bogus def literal", "STRING_LITERAL", sub("cs", "RM_AbyssKernel.cs", '"RM_AbyssDark"', '"RM_AbyssDarkk"'))
    trial("duplicate Scribe label", "SCRIBE_DUP", sub("cs", "RM_GustController.cs", 'Scribe_Values.Look(ref gust.count, "gustCount", 0);', 'Scribe_Values.Look(ref gust.count, "gustCount", 0); Scribe_Values.Look(ref gust.count, "gustCount", 0);'))
    trial("settings default drift", "SETTINGS_DRIFT", sub("cs", "RM_AbyssMod.cs", 'Scribe_Values.Look(ref darkStrength, "darkStrength", 1f, true);', 'Scribe_Values.Look(ref darkStrength, "darkStrength", 2f, true);'))
    trial("setting never Scribed", "SETTINGS_DRIFT", sub("cs", "RM_AbyssMod.cs", '            Scribe_Values.Look(ref cryptidSignsEnabled, "cryptidSignsEnabled", true, true);\n', ''))
    trial("save label renamed", "STATE_SCRIBE", sub("cs", "RM_MapComponentShipCover.cs", '"cooldownUntil"', '"cooldown"'))
    trial("kernel imports Unity", "KERNEL_PURE", sub("cs", "RM_AbyssKernel.cs", "using System;", "using System;\nusing UnityEngine;"))
    trial("keyed-on weather missing", "WEATHER_DEF", _drop_weather)
    return fails


def _first_class_sub(inp, token):
    def m(i2):
        for p, t in i2.xml.items():
            if 'Class="RimMandrake.Abyss.CompProperties_%s"' % token in t:
                i2.xml[p] = t.replace('RimMandrake.Abyss.CompProperties_%s' % token, 'RimMandrake.Abyss.CompProperties_%sX' % token, 1)
                return
        raise AssertionError("no XML uses CompProperties_%s" % token)
    return m


def _field_sub(inp):
    def m(i2):
        for p, t in i2.xml.items():
            if 'Class="RimMandrake.Abyss.CompProperties_Krizzak"' in t and "<searchRadius>" in t:
                i2.xml[p] = re.sub(r"<searchRadius>([^<]*)</searchRadius>", r"<searchRadus>\1</searchRadus>", t, count=1)
                return
        raise AssertionError("no CompProperties_Krizzak node with searchRadius")
    return m


def _drop_weather(i2):
    """the weather check reads WeatherDefs from disk, so plant by asking it for a weather the kernel supposedly keys on that has no def"""
    WEATHERS.append("RM_AbyssNoSuchWeather")
    i2.cleanup = lambda: WEATHERS.remove("RM_AbyssNoSuchWeather")


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
        print("abyss lint self-proof: %d planted break(s) NOT caught: %s" % (len(pf), ", ".join(pf)))
        return 1
    print("abyss lint self-proof: every planted break caught")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
