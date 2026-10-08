#!/usr/bin/env python3
"""Static cross-check of The Rot: XML defs <-> C# classes/fields (including the two custom Def types written as <RimMandrake.TheRot.X> tags),
csproj <-> source files, string lookups, Scribe labels, the Mod Settings class, the by-name reflection, plus The Rot-specific agreements.
No game, no build. Generic machinery: moddefs_lint.py.

    python3 src/RimMandrake/Utils/selftest_therot_lint.py

The Rot extras:
  - RM_TheRotKernel.cs stays free of Verse/UnityEngine (the TheRotFuzz project compiles it on plain net8.0)
  - the swallow clock's Scribe labels are the ones saves already use (renaming one silently resets a belly mid-digestion)
  - RM_NavigatorLog: every siteEntries index names an entry (1..entries), entries are non-empty, and the log has at least one site entry
  - RM_UnjoiningTargets: every RM_ hediff it names exists; the organs it names are body-part defNames the C# can match
  - the defs the components look up by name exist (sheen casting, drive cores, husk, gut-mother vat, quest script, ...)
  - every setting with a slider is read by something other than its own screen (a setting nothing reads is a lie in the UI)
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

MOD = os.path.join(ml.SRC, "RimMandrake", "TheRot")
SWALLOW_LABELS = {"ticksInside": "ticksInside", "ticksToDigest": "ticksToDigest", "damageSinceSwallow": "damageSinceSwallow", "nextKnockTick": "nextKnockTick"}
NAMED_DEFS = ["RM_Hwelgrue", "RM_SheenCasting", "RM_SwallowedDriveCore", "RM_RuinedDriveCore", "RM_GutMotherSac", "RM_GutMotherStarter", "RM_GutMotherVat", "RM_GutMotherCulture",
              "RM_SplitGutMother", "RM_SheenCoating", "RM_GutKnocking", "RM_GutKnocking_Weak", "RM_GutKnocking_Failing", "RM_GutScrabbling", "RM_CorePing", "RM_CoreChirp",
              "RM_GutGraze", "RM_GutSwallow", "RM_SymbiontHusk", "RM_UnjoiningPurge", "RM_UnjoiningDraught", "RM_NavigatorSalvageSite", "RM_NavigatorLog", "RM_UnjoiningTargets"]
# body parts the C# matches by defName string through the targets def (vanilla names; checked only for shape)
VANILLA_HEDIFFS = {"MuscleParasites", "GutWorms"}


def _kids(el, name):
    child = el.find(name)
    return list(child) if child is not None else []


def _tag_nodes(ctx, tag):
    for p, t in ctx.inp.xml.items():
        try:
            root = ET.fromstring(t.encode("utf-8"))
        except ET.ParseError:
            continue
        for el in root.iter(tag):
            yield p, el


def extra(ctx, findings, counts):
    inp = ctx.inp
    # 1. kernel purity
    kp, kt = ctx.cs_text("RM_TheRotKernel.cs")
    if kt is None:
        findings.append(("KERNEL_PURE", MOD, 0, "RM_TheRotKernel.cs not found"))
    else:
        for bad in ("using Verse", "using UnityEngine", "using RimWorld"):
            if bad in ml.mask(kt, True):
                findings.append(("KERNEL_PURE", kp, 0, "contains '%s': the TheRotFuzz project compiles this file on plain net8.0" % bad))
    counts["kernel files"] = 1 if kt else 0
    # 2. swallow clock labels
    cp, ct = ctx.cs_text("RM_HwelgrueSwallow.cs")
    body = ml.mask(ct or "", True)
    n = 0
    for field, label in SWALLOW_LABELS.items():
        n += 1
        if not re.search(r'Scribe_Values\.Look\(\s*ref\s+sw\.%s\s*,\s*"%s"' % (field, label), body):
            findings.append(("SWALLOW_SCRIBE", cp or MOD, 0, 'the swallow comp does not Scribe sw.%s under the label "%s" (saves would silently reset it)' % (field, label)))
    counts["swallow scribe fields"] = n
    # 3. navigator log def
    log_nodes = list(_tag_nodes(ctx, "RimMandrake.TheRot.RM_NavigatorLogDef"))
    for p, el in log_nodes:
        entries = [li.text for li in _kids(el, "entries")]
        sites = []
        for li in _kids(el, "siteEntries"):
            try:
                sites.append(int((li.text or "").strip()))
            except ValueError:
                findings.append(("NAV_LOG", p, 0, "siteEntries item %r is not an integer" % li.text))
        if not entries or any(not (e or "").strip() for e in entries):
            findings.append(("NAV_LOG", p, 0, "the log has no entries or an empty one"))
        for s in sites:
            if s < 1 or s > len(entries):
                findings.append(("NAV_LOG", p, 0, "siteEntries names entry %d of %d" % (s, len(entries))))
        if not sites:
            findings.append(("NAV_LOG", p, 0, "the log reveals no site at all"))
        if len(set(sites)) != len(sites):
            findings.append(("NAV_LOG", p, 0, "siteEntries lists an entry twice"))
        counts["log entries"] = len(entries)
        counts["log site entries"] = len(sites)
    counts["navigator log defs"] = len(log_nodes)
    # 4. unjoining targets
    tgt = list(_tag_nodes(ctx, "RimMandrake.TheRot.RM_UnjoiningTargetsDef"))
    n_h = 0
    for p, el in tgt:
        for group in ("parasites", "symbionts"):
            for li in _kids(el, group):
                name = (li.text or "").strip()
                n_h += 1
                if name.startswith(("RM_", "RUT_", "RSW_")):
                    if name not in inp.defnames:
                        findings.append(("UNJOIN_TARGET", p, 0, "%s names hediff %s, which no def defines" % (group, name)))
                elif name not in VANILLA_HEDIFFS:
                    findings.append(("UNJOIN_TARGET", p, 0, "%s names %s, which is neither ours nor a recorded vanilla hediff" % (group, name)))
        both = {(li.text or "").strip() for li in _kids(el, "parasites")} & {(li.text or "").strip() for li in _kids(el, "symbionts")}
        if both:
            findings.append(("UNJOIN_TARGET", p, 0, "%s is both a parasite and a symbiont" % ", ".join(sorted(both))))
    counts["unjoin targets"] = n_h
    # 5. defs looked up by name
    for needed in NAMED_DEFS:
        if needed not in inp.defnames:
            findings.append(("LOOKUP_DEF", MOD, 0, "%s is looked up by name or DefOf in the components but no def of that name exists" % needed))
    counts["named lookups"] = len(NAMED_DEFS)
    # 5b. comp order on the hwelgrue: the map-cap kill (RM_CompGutDigest) must tick BEFORE the one-shot core claim (RM_CompSwallowedCore),
    #     because the claim refuses a hwelgrue that is over the cap and then never looks again (claimChecked is saved)
    order_ok = False
    n_def = 0
    for p, tx in inp.xml.items():
        if "<defName>RM_Hwelgrue</defName>" in tx:
            n_def += 1
            a = tx.find("CompProperties_RM_GutDigest")
            b = tx.find("CompProperties_RM_SwallowedCore")
            if a < 0 or b < 0 or a > b:
                findings.append(("COMP_ORDER", p, 0, "RM_Hwelgrue lists CompProperties_RM_SwallowedCore before CompProperties_RM_GutDigest: an over-cap hwelgrue could be refused the core "
                                 "and then survive, leaving the world with no carrier for good"))
            else:
                order_ok = True
    if n_def == 0:
        findings.append(("COMP_ORDER", MOD, 0, "RM_Hwelgrue def not found"))
    counts["hwelgrue comp order checked"] = 1 if order_ok else 0

    # 6. a slider setting nobody reads
    sp, st = ctx.cs_text("RM_TheRotMod.cs")
    sliders = set(re.findall(r"(\w+)\s*=\s*(?:Mathf\.RoundToInt\()?list\.Slider\(", ml.mask(st or "", True)))
    unread = []
    all_src = "\n".join(ml.mask(t, False) for p, t in inp.cs.items() if os.path.basename(p) != "RM_TheRotMod.cs")
    for name in sorted(sliders):
        if not re.search(r"\b%s\b" % re.escape(name), all_src):
            # read from RM_TheRotMod.cs itself (the front) counts too, but only outside the slider line
            own = [l for l in ml.mask(st or "", False).split("\n") if re.search(r"\b%s\b" % re.escape(name), l) and "list.Slider" not in l and "Scribe_Values" not in l
                   and not re.search(r"public\s+static", l) and "Label(" not in l and "ToString" not in l]
            if not own:
                unread.append(name)
    for name in unread:
        findings.append(("SETTING_UNREAD", sp or MOD, 0, "slider setting %s is read by nothing but its own screen" % name))
    counts["slider settings"] = len(sliders)


def config():
    return ml.Cfg(
        "TheRot", MOD, ["RimMandrake.TheRot"],
        [(os.path.join(MOD, "Source"), os.path.join(MOD, "Source", "RM_TheRot.csproj"))],
        settings_classes=["RM_TheRotSettings"],
        min_probe={"classes": 30, "xml class refs": 15, "Class= nodes": 8, "settings fields": 30, "Scribe labels": 20, "navigator log defs": 1, "slider settings": 15},
        extra=extra)


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

    def xml_has(token, old, new):
        def m(i2):
            for p, t in i2.xml.items():
                if token in t and old in t:
                    i2.xml[p] = t.replace(old, new, 1)
                    return
            raise AssertionError("no XML with %r and %r" % (token, old))
        return m

    trial("misspelt Class", "UNRESOLVED_CLASS", xml_has('Class="RimMandrake.TheRot.CompProperties_RM_GutSwallow"', "RimMandrake.TheRot.CompProperties_RM_GutSwallow", "RimMandrake.TheRot.CompProperties_RM_GutSwalow"))
    trial("misspelt Def type tag", "UNRESOLVED_CLASS", lambda i2: i2.xml.update({p: x.replace("RimMandrake.TheRot.RM_NavigatorLogDef>", "RimMandrake.TheRot.RM_NavigatorLogDeff>") for p, x in i2.xml.items()}))
    trial("misspelt field child", "UNKNOWN_FIELD", _field_sub())
    trial("non-numeric site entry", "BAD_VALUE", xml_has("RM_NavigatorLogDef", "<li>4</li>", "<li>four</li>"))
    trial("site entry past the log", "NAV_LOG", xml_has("RM_NavigatorLogDef", "<li>8</li>\n    </siteEntries>", "<li>9</li>\n    </siteEntries>"))
    trial("csproj drops the kernel", "CSPROJ_MISSING", lambda i2: i2.csproj.update({p: t.replace('<Compile Include="RM_TheRotKernel.cs" />', "", 1) for p, t in i2.csproj.items()}))
    trial("bogus def literal", "STRING_LITERAL", sub("cs", "RM_Unjoining.cs", '"RM_SymbiontHusk"', '"RM_SymbiontHuskk"'))
    trial("duplicate Scribe label", "SCRIBE_DUP", sub("cs", "RM_SwallowedCore.cs", 'Scribe_Values.Look(ref carrier, "carrier", false);', 'Scribe_Values.Look(ref carrier, "carrier", false); Scribe_Values.Look(ref carrier, "carrier", false);'))
    trial("settings default drift", "SETTINGS_DRIFT", sub("cs", "RM_TheRotMod.cs", 'Scribe_Values.Look(ref hwelgrueCastingDays, "hwelgrueCastingDays", 2f);', 'Scribe_Values.Look(ref hwelgrueCastingDays, "hwelgrueCastingDays", 4f);'))
    trial("swallow label renamed", "SWALLOW_SCRIBE", sub("cs", "RM_HwelgrueSwallow.cs", '"ticksToDigest"', '"digestLength"'))
    trial("kernel imports Unity", "KERNEL_PURE", sub("cs", "RM_TheRotKernel.cs", "using System;", "using System;\nusing UnityEngine;"))
    trial("unjoin target gone", "UNJOIN_TARGET", xml_has("RM_UnjoiningTargetsDef", "<li>RM_Sym_Mycoid</li>", "<li>RM_Sym_Mycoidd</li>"))
    trial("def looked up by name gone", "LOOKUP_DEF", lambda i2: i2.defnames.discard("RM_SheenCasting"))
    trial("slider setting unread", "SETTING_UNREAD", _unread())
    trial("claim ticks before the cap kill", "COMP_ORDER", lambda i2: i2.xml.update({p: x.replace("CompProperties_RM_GutDigest", "CompProperties_TMP").replace("CompProperties_RM_SwallowedCore", "CompProperties_RM_GutDigest").replace("CompProperties_TMP", "CompProperties_RM_SwallowedCore") if "<defName>RM_Hwelgrue</defName>" in x else x for p, x in i2.xml.items()}))
    return fails


def _field_sub():
    def m(i2):
        for p, t in i2.xml.items():
            if 'Class="RimMandrake.TheRot.CompProperties_RM_GutDigest"' in t and "<grazeRadius>" in t:
                i2.xml[p] = re.sub(r"<grazeRadius>([^<]*)</grazeRadius>", r"<grazeRadus>\1</grazeRadus>", t, count=1)
                return
        raise AssertionError("no CompProperties_RM_GutDigest node with grazeRadius")
    return m


def _unread():
    def m(i2):
        for p in list(i2.cs):
            if os.path.basename(p) != "RM_TheRotMod.cs":
                i2.cs[p] = re.sub(r"RM_TheRotSettings\.swallowLoudness", "1f", i2.cs[p])
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
        print("therot lint self-proof: %d planted break(s) NOT caught: %s" % (len(pf), ", ".join(pf)))
        return 1
    print("therot lint self-proof: every planted break caught")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
