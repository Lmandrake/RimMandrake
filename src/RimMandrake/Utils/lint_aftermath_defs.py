#!/usr/bin/env python3
"""Offline lint of Aftermath (mandrake.rm.aftermath): the engine has no Defs of its own, so this checks the engine's source structure and
the rule data it executes (mandrake.rut.aftermath: RM_AftermathRuleDef / RM_AlliancePairDef). Generic lint via lint_mod_defs.py, plus:

  af-rule       every RM_AftermathRuleDef: triggerKind / triggerOutcomes / payloadFactionMode are real enum names (a bad value discards the
                def), a payload incident that exists (vanilla RaidEnemy / ShortCircuit or defined by a mod), 0 <= delayDaysMin <= delayDaysMax,
                minSurvivors >= 0, minHeldDays > 0 for PrisonerHeldDuration, BattleOutcome rules list outcomes, HeldPrisonerHome only with
                PrisonerHeldDuration and PrisonerHeldDuration only with HeldPrisonerHome, a wired trigger (BattleOutcome, MentalBreakNearBattle,
                PrisonerHeldDuration) never uses HuttClaimant
  af-format     telegraphText only uses {0}, letterText only {0} and {1}, no lone braces: both go through string.Format, and a stray {1}
                in the telegraph (one argument) or a lone brace throws FormatException when the rule fires
  af-pairs      alliance pairs name factions that exist (vanilla Pirate / Empire or defined by a mod) and no two pairs share an `a`
                (the runner takes the FIRST pair for a defeated faction and never reads `weight`)
  af-settings   slider ranges contain their defaults and the kernel's tick constants match the engine's (60000 per day)
  af-kernel     Kernel/*.cs names no Verse / RimWorld / UnityEngine / HarmonyLib; the Harmony id equals the About packageId
  sanity probe  the sweep sees the 8 shipped rules and >= 3 alliance pairs

    python3 src/RimMandrake/Utils/lint_aftermath_defs.py [--quiet] [--mod-dir D]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RULE = "RimMandrake.Aftermath.RM_AftermathRuleDef"
PAIR = "RimMandrake.Aftermath.RM_AlliancePairDef"
VANILLA_INCIDENTS = {"RaidEnemy", "ShortCircuit"}
VANILLA_FACTIONS = {"Pirate", "Empire", "Outlander", "Tribe"}
WIRED = {"BattleOutcome", "MentalBreakNearBattle", "PrisonerHeldDuration"}


def enum_names(path, enum):
    txt = re.sub(r"//[^\n]*", "", open(path, encoding="utf-8-sig").read())
    body = re.search(r"enum %s\s*\{(.*?)\}" % enum, txt, re.S).group(1)
    return [x.strip() for x in body.split(",") if x.strip()]


def format_args(text):
    """Argument indexes a .NET composite format string uses; None when it is malformed (FormatException)."""
    used, i = set(), 0
    while i < len(text):
        c = text[i]
        if c == "{":
            if text[i + 1:i + 2] == "{":
                i += 2
                continue
            m = re.match(r"\{(\d+)(?:,-?\d+)?(?::[^{}]*)?\}", text[i:])
            if not m:
                return None
            used.add(int(m.group(1)))
            i += m.end()
        elif c == "}":
            if text[i + 1:i + 2] == "}":
                i += 2
                continue
            return None
        else:
            i += 1
    return used


def main(argv):
    rc = lint_mod_defs.run("Aftermath", argv, require_xml=False)
    if rc == 2:
        return 2
    mod = os.path.join(REPO, "src", "RimMandrake", "Aftermath")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    errs = []
    E = lambda c, m: errs.append("ERROR %s: %s" % (c, m))
    src = lambda *p: open(os.path.join(mod, "Source", *p), encoding="utf-8-sig").read()
    kinds = enum_names(os.path.join(mod, "Source", "AftermathTriggerKind.cs"), "AftermathTriggerKind")
    modes = enum_names(os.path.join(mod, "Source", "AftermathPayloadFactionMode.cs"), "AftermathPayloadFactionMode")
    outcomes = enum_names(os.path.join(mod, "Source", "BattleOutcome.cs"), "BattleOutcome")

    # rule data: the consumer mod's defs, or a planted copy handed in through --rules-dir
    rules_dir = argv[argv.index("--rules-dir") + 1] if "--rules-dir" in argv else os.path.join(REPO, "src", "RimUtinni", "AftermathRites", "Defs")
    defined_inc, defined_fac = set(), set()
    for p in glob.glob(os.path.join(REPO, "src", "*", "*", "Defs", "**", "*.xml"), recursive=True):
        txt = re.sub(r"<!--.*?-->", "", open(p, encoding="utf-8-sig", errors="replace").read(), flags=re.S)
        for m in re.finditer(r"<(IncidentDef|FactionDef)(?:\s[^>]*)?>\s*<defName>([^<]+)</defName>", txt):
            (defined_inc if m.group(1) == "IncidentDef" else defined_fac).add(m.group(2).strip())
    n_rules = n_pairs = 0
    pair_a = {}
    for p in glob.glob(os.path.join(rules_dir, "*.xml")):
        rel = os.path.basename(p)
        for d in ET.parse(p).getroot():
            name = (d.findtext("defName") or "?").strip()
            tag = "%s %s" % (rel, name)
            if d.tag == RULE:
                n_rules += 1
                kind = (d.findtext("triggerKind") or "BattleOutcome").strip()
                mode = (d.findtext("payloadFactionMode") or "SameAsTrigger").strip()
                outs = [li.text.strip() for li in d.findall("triggerOutcomes/li") if li.text]
                if kind not in kinds:
                    E("af-rule", "%s: triggerKind %r is not one of %s" % (tag, kind, kinds))
                if mode not in modes:
                    E("af-rule", "%s: payloadFactionMode %r is not one of %s" % (tag, mode, modes))
                for o in outs:
                    if o not in outcomes:
                        E("af-rule", "%s: triggerOutcomes names %r, not one of %s" % (tag, o, outcomes))
                if kind == "BattleOutcome" and not outs:
                    E("af-rule", "%s: BattleOutcome rule lists no outcomes" % tag)
                inc = (d.findtext("payloadIncidentDefName") or "").strip()
                if not inc or (inc not in VANILLA_INCIDENTS and inc not in defined_inc):
                    E("af-rule", "%s: payload incident %r does not exist" % (tag, inc))
                try:
                    lo, hi = float(d.findtext("delayDaysMin") or 0.5), float(d.findtext("delayDaysMax") or 2)
                    if lo < 0 or hi < lo:
                        E("af-rule", "%s: delay %s..%s days is negative or inverted" % (tag, lo, hi))
                    if int(d.findtext("minSurvivors") or 0) < 0:
                        E("af-rule", "%s: negative minSurvivors" % tag)
                    held = float(d.findtext("minHeldDays") or 3)
                    if kind == "PrisonerHeldDuration" and held <= 0:
                        E("af-rule", "%s: PrisonerHeldDuration with minHeldDays %s" % (tag, held))
                except ValueError as e:
                    E("af-rule", "%s: a number field is not a number (%s)" % (tag, e))
                if (mode == "HeldPrisonerHome") != (kind == "PrisonerHeldDuration"):
                    E("af-rule", "%s: HeldPrisonerHome and PrisonerHeldDuration go together (the runner resolves rule 4's faction off the prisoner), got %s / %s" % (tag, kind, mode))
                if kind in WIRED and mode == "HuttClaimant":
                    E("af-rule", "%s: a wired trigger uses HuttClaimant, which ResolveTargetFaction returns null for" % tag)
                tg, lt = d.findtext("telegraphText"), d.findtext("letterText")
                for field, text, allowed in (("telegraphText", tg, {0}), ("letterText", lt, {0, 1})):
                    if text is None:
                        continue
                    used = format_args(text)
                    if used is None:
                        E("af-format", "%s: %s has a lone brace or a malformed placeholder (FormatException when it fires)" % (tag, field))
                    elif not used <= allowed:
                        E("af-format", "%s: %s uses {%s} but the call passes only %d argument(s)" % (tag, field, sorted(used - allowed)[0], len(allowed)))
            elif d.tag == PAIR:
                n_pairs += 1
                a, b = (d.findtext("a") or "").strip(), (d.findtext("b") or "").strip()
                for side, f in (("a", a), ("b", b)):
                    if f not in VANILLA_FACTIONS and f not in defined_fac:
                        E("af-pairs", "%s: %s faction %r does not exist" % (tag, side, f))
                if a in pair_a:
                    E("af-pairs", "%s and %s share a=%s: the runner takes the first and never reads weight" % (pair_a[a], name, a))
                pair_a[a] = name
    if n_rules < 8 or n_pairs < 3:
        E("af-rule", "sanity probe: saw %d rules and %d alliance pairs (want >= 8 and >= 3)" % (n_rules, n_pairs))

    # af-settings
    modcs = src("RM_AftermathMod.cs")
    decl = dict(re.findall(r"public static (?:bool|int|float) (\w+) = ([^;]+);", modcs))
    for m in re.finditer(r"(\w+) = (?:System\.Convert\.ToInt32\()?list\.Slider\(\1, ([\d.]+)f?, ([\d.]+)f?\)", modcs):
        fld, lo, hi = m.group(1), float(m.group(2)), float(m.group(3))
        v = decl.get(fld)
        if v is None or not lo <= float(v.rstrip("f")) <= hi:
            E("af-settings", "%s default %s lies outside its slider %s..%s" % (fld, v, lo, hi))
    kern = src("Kernel", "RM_AftermathKernel.cs")
    if not re.search(r"TicksPerDay = 60000;", kern):
        E("af-settings", "kernel TicksPerDay is not 60000 (GenDate.TicksPerDay)")
    # af-kernel
    for n, line in enumerate(kern.splitlines(), 1):
        if re.match(r"\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)\b", line):
            E("af-kernel", "RM_AftermathKernel.cs:%d `%s`" % (n, line.strip()))
    about = os.path.join(mod, "About", "About.xml")
    if not os.path.exists(about):
        about = os.path.join(REPO, "src", "RimMandrake", "Aftermath", "About", "About.xml")
    pkg = ET.parse(about).getroot().findtext("packageId")
    hid = re.search(r'HarmonyId = "([^"]+)"', src("AftermathMod.cs"))
    if not hid or hid.group(1) != pkg:
        E("af-kernel", "Harmony id %r differs from the About packageId %r" % (hid.group(1) if hid else None, pkg))
    print("aftermath data: %d rules, %d alliance pairs checked" % (n_rules, n_pairs))
    for e in errs:
        print(e)
    return 1 if (errs or rc) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
