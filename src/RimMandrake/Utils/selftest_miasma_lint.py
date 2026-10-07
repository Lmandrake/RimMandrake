#!/usr/bin/env python3
"""Static cross-check of the Miasma: XML defs <-> C# classes/fields, csproj <-> source files, string lookups, Scribe labels, the Mod Settings
class, the by-name REFLECTION this mod does into the shared EnvironmentalHazards assembly (a rename there silently turns a feature off here),
plus Miasma-specific agreements. No game, no build. Generic machinery: moddefs_lint.py.

    python3 src/RimMandrake/Utils/selftest_miasma_lint.py

Miasma extras:
  - RM_MiasmaKernel.cs stays free of Verse/UnityEngine (the MiasmaFuzz project compiles it on plain net8.0)
  - the creche ledger's Scribe labels are the ones saves already use (renaming one silently resets that creche), one per ledger field
  - helper-style reflection (`Get(comp, "Betrayed")`, `Call(comp, "RevokeForever")`) names members that exist in src/
  - the defs the components look up by name exist (stranded hediff, creche marker, warden mother kind, meter, loam, ...)
Then it PLANTS a break of each kind into the in-memory inputs and proves each is caught.
"""
import copy
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import moddefs_lint as ml  # noqa: E402

MOD = os.path.join(ml.SRC, "RimMandrake", "Miasma")
LEDGER_LABELS = {"young": "registeredYoung", "recordClean": "recordClean", "heir": "heirPawn", "successionDone": "successionDone", "betrayed": "betrayed", "returnedCount": "returnedCount"}
HELPER_CALL = re.compile(r'\b(?:Get|Call)\(\s*[^;"]*?,\s*"(\w+)"\s*\)')
NAMED_DEFS = ["RUT_StrandedDeformation", "RUT_CrecheMarker", "RM_WardenMother", "RM_OldCurrentMeter", "RM_DeltaLoam", "RM_Bones", "RM_Attar", "RM_GlazeArtwork",
              "RM_BalmScar", "RM_MakeAttar", "RM_AttarStill", "RM_Bozzuga", "RM_Thessamor", "RM_Brelloch", "RM_Thrannock", "RM_Quennath"]


def extra(ctx, findings, counts):
    inp = ctx.inp
    # 1. kernel purity
    kp, kt = ctx.cs_text("RM_MiasmaKernel.cs")
    if kt is None:
        findings.append(("KERNEL_PURE", MOD, 0, "RM_MiasmaKernel.cs not found"))
    else:
        for bad in ("using Verse", "using UnityEngine", "using RimWorld"):
            if bad in ml.mask(kt, True):
                findings.append(("KERNEL_PURE", kp, 0, "contains '%s': the MiasmaFuzz project compiles this file on plain net8.0" % bad))
    counts["kernel files"] = 1 if kt else 0
    # 2. ledger Scribe labels
    cp, ct = ctx.cs_text("RM_WardenMotherSuccession.cs")
    body = ml.mask(ct or "", True)
    n = 0
    for field, label in LEDGER_LABELS.items():
        n += 1
        if not re.search(r'Scribe_\w+\.Look\(\s*ref\s+ledger\.%s\s*,\s*"%s"' % (field, label), body):
            findings.append(("LEDGER_SCRIBE", cp or MOD, 0, 'the creche comp does not Scribe ledger.%s under the label "%s" (saves would silently reset it)' % (field, label)))
    counts["ledger scribe fields"] = n
    # 3. helper-style reflection names
    mp, mt = ctx.cs_text("RM_MothersPrice.cs")
    m_nocom = ml.mask(mt or "", True)
    names = set(HELPER_CALL.findall(m_nocom))
    for name in sorted(names):
        if name not in inp.identifiers:
            findings.append(("REFLECTION_NAME", mp or MOD, 0, '"%s" is called by name on the territorial anchor but no identifier of that name exists in src/ C#' % name))
    counts["helper reflection names"] = len(names)
    # 4. defs looked up by name
    for needed in NAMED_DEFS:
        if needed not in inp.defnames:
            findings.append(("LOOKUP_DEF", MOD, 0, "%s is looked up by name in the components but no def of that name exists" % needed))
    counts["named lookups"] = len(NAMED_DEFS)


def config():
    return ml.Cfg(
        "Miasma", MOD, ["RimMandrake.Miasma"],
        [(os.path.join(MOD, "Source"), os.path.join(MOD, "Source", "RM_Miasma.csproj"))],
        settings_classes=["RM_MiasmaSettings"],
        min_probe={"classes": 25, "xml class refs": 10, "Class= nodes": 8, "settings fields": 15, "Scribe labels": 20, "reflection names": 5},
        extra=extra, reflection=True, reflection_engine_names=["allRecipesCached"])


def planted(cfg, inp):
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

    def sub(store, basename, old, new):
        def m(i2):
            d = getattr(i2, store)
            for p in d:
                if os.path.basename(p) == basename and old in d[p]:
                    d[p] = d[p].replace(old, new, 1)
                    return
            raise AssertionError("fixture pattern %r not found in %s" % (old, basename))
        return m

    def any_xml_sub(token, old, new):
        def m(i2):
            for p, t in i2.xml.items():
                if token in t and old in t:
                    i2.xml[p] = t.replace(old, new, 1)
                    return
            raise AssertionError("no XML with %r and %r" % (token, old))
        return m

    trial("misspelt Class", "UNRESOLVED_CLASS", any_xml_sub('Class="RimMandrake.Miasma.RM_RottingBedExtension"', "RimMandrake.Miasma.RM_RottingBedExtension", "RimMandrake.Miasma.RM_RottingBedExtensoin"))
    trial("misspelt field child", "UNKNOWN_FIELD", any_xml_sub('Class="RimMandrake.Miasma.RM_RottingBedExtension"', "<bonesPerBodySize>", "<bonesPerBodySise>") if False else _field(inp))
    trial("csproj drops the kernel", "CSPROJ_MISSING", lambda i2: i2.csproj.update({p: t.replace('<Compile Include="RM_MiasmaKernel.cs" />', "", 1) for p, t in i2.csproj.items()}))
    trial("bogus def literal", "STRING_LITERAL", sub("cs", "RM_RottingBed.cs", '"RM_Bones"', '"RM_Bonez"'))
    trial("duplicate Scribe label", "SCRIBE_DUP", sub("cs", "RM_Attar.cs", 'Scribe_Collections.Look(ref ids, "glazedArtworkIds", LookMode.Value);', 'Scribe_Collections.Look(ref ids, "glazedArtworkIds", LookMode.Value); Scribe_Collections.Look(ref ids, "glazedArtworkIds", LookMode.Value);'))
    trial("settings default drift", "SETTINGS_DRIFT", sub("cs", "RM_MiasmaMod.cs", 'Scribe_Values.Look(ref rottingBedRotDays, "rottingBedRotDays", 3f, true);', 'Scribe_Values.Look(ref rottingBedRotDays, "rottingBedRotDays", 5f, true);'))
    trial("setting out of its slider", "SETTINGS_DRIFT", sub("cs", "RM_MiasmaMod.cs", "public static float rottingBedRotDays = 3f;", "public static float rottingBedRotDays = 30f;"))
    trial("reflection name typo", "REFLECTION_NAME", sub("cs", "RM_MapComponent_FlotsamYard.cs", '"LastRecedeCompletedTick"', '"LastRecedeCompletedTik"'))
    trial("helper reflection typo", "REFLECTION_NAME", sub("cs", "RM_MothersPrice.cs", '"RevokeForever"', '"RevokeForevr"'))
    trial("ledger label renamed", "LEDGER_SCRIBE", sub("cs", "RM_WardenMotherSuccession.cs", '"registeredYoung"', '"young"'))
    trial("kernel imports Verse", "KERNEL_PURE", sub("cs", "RM_MiasmaKernel.cs", "using System;", "using System;\nusing Verse;"))
    trial("def looked up by name gone", "LOOKUP_DEF", lambda i2: i2.defnames.discard("RM_DeltaLoam"))
    return fails


def _field(inp):
    def m(i2):
        for p, t in i2.xml.items():
            if 'Class="RimMandrake.Miasma.RM_RottingBedExtension"' in t and "<bonesPerBodySize>" in t:
                i2.xml[p] = re.sub(r"<bonesPerBodySize>([^<]*)</bonesPerBodySize>", r"<bonesPerBodySise>\1</bonesPerBodySise>", t, count=1)
                return
        raise AssertionError("no RM_RottingBedExtension node with bonesPerBodySize")
    return m


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
        print("miasma lint self-proof: %d planted break(s) NOT caught: %s" % (len(pf), ", ".join(pf)))
        return 1
    print("miasma lint self-proof: every planted break caught")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
