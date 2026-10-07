#!/usr/bin/env python3
"""Offline lint of the FeverWood mod: XML defs/patches against its C# source (see lint_modpack_defs.py for the generic
checks) plus FeverWood-specific data checks:

  feverwood-gift     RM_DeepGiftLoot: every entry names a thing, weights are >= 0 with at least one > 0, count ranges are
                     ordered, no thing listed twice; an RM_/RUT_/RSW_ thing must exist in some RimMandrake mod's Defs
  feverwood-tank     every RM_CompProperties_CapturedSpecimen: damage threshold in (0,1], per-hit chance in [0,1], neglect
                     days >= 0, neglect MTB > 0, giftRolls >= 1, each product's mtbDays > 0 and countRange ordered
  feverwood-trader   RM_StockGenerator_DeepYoung: stockChance is -1 (use settings) or in [0,1]; onlyFactions are named
  feverwood-foul     the Uranium suppression chain is whole: designation, job (driver RM_JobDriver_FoulPool), work giver
                     (RM_WorkGiver_FoulPool), the charge item and a recipe producing it
  feverwood-campaign every <li Class="RimMandrake.FeverWood.X"> in src/RimUtinni's brood-ransom patch carries only fields
                     X (and its bases) declares

    python3 src/RimMandrake/Utils/lint_feverwood_defs.py [--mod-dir <dir>] [--quiet]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_modpack_defs as L  # noqa: E402


def _num(el, tag, default=None):
    t = el.findtext(tag)
    if t is None:
        return default
    try:
        return float(t.strip())
    except ValueError:
        return None


def _range(text):
    m = re.match(r"^\s*(-?\d+)\s*~\s*(-?\d+)\s*$", text or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def extra(mod, E, W, defs_xml, patch_xml, defnames, ctx):
    all_defnames = set()
    for xp in glob.glob(os.path.join(ctx["src"], "*", "Defs", "**", "*.xml"), recursive=True):
        all_defnames |= set(re.findall(r"<defName>([^<]+)</defName>", open(xp, encoding="utf-8-sig", errors="replace").read()))
    n = {"gift": 0, "tank": 0, "trader": 0, "foul": 0, "campaign": 0}
    docs = []
    for p in defs_xml + patch_xml:
        try:
            docs.append((p, ET.parse(p).getroot()))
        except ET.ParseError:
            pass
    for p, root in docs:
        rel = os.path.relpath(p, mod)
        for el in root.iter():
            tag, cls = el.tag, el.get("Class", "")
            if tag.endswith("RM_DeepGiftTableDef"):
                n["gift"] += 1
                seen, positive = set(), 0
                for li in el.findall("entries/li"):
                    thing = (li.findtext("thing") or "").strip()
                    w = _num(li, "weight", 1.0)
                    if not thing:
                        E("feverwood-gift", f"{rel}: an entry names no thing")
                        continue
                    if thing in seen:
                        E("feverwood-gift", f"{rel}: {thing} listed twice")
                    seen.add(thing)
                    if w is None or w < 0:
                        E("feverwood-gift", f"{rel}: {thing} has weight {li.findtext('weight')}")
                    elif w > 0:
                        positive += 1
                    if thing.startswith(L.OUR_PREFIX) and thing not in all_defnames:
                        E("feverwood-gift", f"{rel}: {thing} is defined by no RimMandrake mod")
                    c = li.findtext("count")
                    if c and (_range(c) is None or _range(c)[0] > _range(c)[1] or _range(c)[0] < 1):
                        E("feverwood-gift", f"{rel}: {thing} count {c} is not a positive ordered range")
                if positive == 0:
                    E("feverwood-gift", f"{rel}: the gift table has no entry with a positive weight")
            if cls.endswith("RM_CompProperties_CapturedSpecimen"):
                n["tank"] += 1
                chk = [("damageEscapeThresholdFraction", 1e-9, 1.0), ("damageEscapeChancePerHit", 0.0, 1.0),
                       ("neglectDaysBeforeEscapeRisk", 0.0, 1e9), ("neglectEscapeMtbDays", 1e-9, 1e9), ("giftRolls", 1, 1e3)]
                for f, lo, hi in chk:
                    v = _num(el, f)
                    if v is not None and not (lo <= v <= hi):
                        E("feverwood-tank", f"{rel}: {f} = {v} outside [{lo}, {hi}]")
                for li in el.findall("products/li"):
                    mtb = _num(li, "mtbDays")
                    if mtb is not None and mtb <= 0:
                        E("feverwood-tank", f"{rel}: product {li.findtext('thing')} mtbDays {mtb} <= 0 (Rand.MTBEventOccurs treats that as always)")
                    cr = _range(li.findtext("countRange"))
                    if li.findtext("countRange") and (cr is None or cr[0] > cr[1] or cr[0] < 1):
                        E("feverwood-tank", f"{rel}: product {li.findtext('thing')} countRange {li.findtext('countRange')} not a positive ordered range")
            if cls.endswith("RM_StockGenerator_DeepYoung"):
                n["trader"] += 1
                sc = _num(el, "stockChance", -1.0)
                if sc is None or not (sc == -1.0 or 0.0 <= sc <= 1.0):
                    E("feverwood-trader", f"{rel}: stockChance {el.findtext('stockChance')} is neither -1 nor in [0,1]")
                for of in el.findall("onlyFactions/li"):
                    if (of.text or "").strip() and of.text.strip().startswith(L.OUR_PREFIX) and of.text.strip() not in all_defnames:
                        E("feverwood-trader", f"{rel}: onlyFactions {of.text.strip()} is defined by no RimMandrake mod")
    # the foul-pool chain
    need = {("DesignationDef", "RM_Designation_FoulPool"), ("JobDef", "RM_FoulPool"), ("ThingDef", "RM_RadioactiveSuppressant")}
    for t, d in sorted(need):
        n["foul"] += 1
        if (t, d) not in defnames:
            E("feverwood-foul", f"{t} {d} is not defined in this mod")
    drivers = {}
    for p, root in docs:
        for d in root:
            if d.tag == "JobDef" and d.findtext("defName") == "RM_FoulPool":
                drivers["job"] = (d.findtext("driverClass") or "").strip()
            if d.tag == "WorkGiverDef" and (d.findtext("giverClass") or "").strip().endswith("RM_WorkGiver_FoulPool"):
                drivers["giver"] = True
    if drivers.get("job") and not drivers["job"].endswith("RM_JobDriver_FoulPool"):
        E("feverwood-foul", f"JobDef RM_FoulPool uses driver {drivers['job']}, not RM_JobDriver_FoulPool")
    if not drivers.get("giver"):
        E("feverwood-foul", "no WorkGiverDef names RM_WorkGiver_FoulPool")
    if not any(re.search(r"RM_RadioactiveSuppressant", open(p, encoding="utf-8-sig", errors="replace").read()) and root.find(".//RecipeDef") is not None
               for p, root in docs):
        E("feverwood-foul", "no RecipeDef produces RM_RadioactiveSuppressant")
    # the campaign file that configures these classes from outside
    cp = os.path.join(ctx["repo"], "src", "RimUtinni", "UtinniPatches", "Patches", "RUT_BroodRansom_Campaign.xml")
    if os.path.exists(cp):
        classes = ctx["classes"]
        root = ET.parse(cp).getroot()
        for el in root.iter():
            cls = el.get("Class", "")
            if cls.startswith("RimMandrake.FeverWood."):
                c = classes.get(cls) or classes.get(cls.split(".")[-1])
                if c is None:
                    E("feverwood-campaign", f"{cls} named by the campaign patch does not exist")
                    continue
                fields, root_base = set(), None
                for x in ctx["chain"](classes, c):
                    if isinstance(x, ctx["Cls"]):
                        fields |= x.fields
                    elif isinstance(x, str):
                        root_base = x
                if root_base is not None and root_base not in L.STRICT_ROOTS:
                    continue   # a vanilla base (StockGenerator, LordJob...) declares fields we cannot see from here
                n["campaign"] += 1
                for ch in el:
                    if ch.tag not in fields and ch.tag != "li" and not (ch.tag in ("compClass", "genStepDef")):
                        E("feverwood-campaign", f"RUT_BroodRansom_Campaign.xml: <{el.tag} Class=\"{cls}\"> has <{ch.tag}>, which {c.name} does not declare")
    print(f"feverwood data: {n['gift']} gift tables, {n['tank']} tank comps, {n['trader']} stock generators, "
          f"{n['foul']} foul-chain defs, {n['campaign']} campaign nodes checked")


if __name__ == "__main__":
    sys.exit(L.run(sys.argv[1:], "FeverWood", "RM_FeverWoodSettings", "RM_FeverWoodMod.cs", "RM_FeverWood.csproj", "feverwood", extra=extra))
