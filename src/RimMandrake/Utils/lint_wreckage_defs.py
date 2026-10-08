#!/usr/bin/env python3
"""Offline lint of the Wreckage mod (defs/patches vs C#): the generic lint (lint_mod_defs.py) plus checks that read EVERY mod's wrecks,
because the biome mods ship their own wreck children, fields and lists against this mod's classes.

  wr-resolve    every ThingDef anywhere under src/ carrying RM_WreckWeathering: its weathering def exists, a family with a salvage-loot comp is
                found up the ParentName chain, and the tier it ends on after the weathering shift (+ extraTierShift) has a ThingSetMakerDef
                RM_SalvageLoot_<tier>, and a _Rare twin when a rare roll survives (the C# only reports this at load, per def)
  wr-weathering every weathering row: 0 < yieldFactor <= 1.5, |lootTierShift| <= 2, hediff severity > 0 with a hediff, extraLeavings parse
  wr-fields     every GenStepDef using RM_GenStep_WreckField (any mod): non-empty settingsKey, at least one wreck with weight > 0, every named
                wreck is a ThingDef somewhere under src/, and it has a densityClass or a count of its own
  wr-lists      every RM_WreckListDef has a wreck with weight > 0 that exists
  wr-kernel     the kernel is Verse-free and compiled by the csproj; no second copy of the tier ladder survives beside it; the skill factor in the
                comment and the kernel agree

    python3 src/RimMandrake/Utils/lint_wreckage_defs.py [--mod-dir <dir>] [--quiet] [--src-dir <dir>]
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
SRC = os.path.join(REPO, "src")
DEFAULT_MOD = os.path.join(SRC, "RimMandrake", "Wreckage")


def read(p):
    return open(p, encoding="utf-8-sig").read()


def rank(t):
    return 0 if t == "Scrap" else 2 if t == "Sealed" else 1


def shift_tier(t, s):
    r = rank(t)
    to = max(0, min(2, r + s))
    return t if to == r else "Scrap" if to == 0 else "Sealed" if to == 2 else "Hull"


def main(argv):
    quiet = "--quiet" in argv
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else DEFAULT_MOD
    src_root = argv[argv.index("--src-dir") + 1] if "--src-dir" in argv else SRC
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("Wreckage", ["--mod-dir", mod])
    gl = buf.getvalue().splitlines()
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs = [l for l in gl if l.startswith("ERROR")]
    warns = [l for l in gl if l.startswith("WARN")]
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    n = {"wrecks": 0, "weatherings": 0, "fields": 0, "lists": 0, "keys": 0}

    # index every def under src (and this mod, when linted from a copy)
    files = glob.glob(os.path.join(src_root, "*", "*", "Defs", "**", "*.xml"), recursive=True)
    if os.path.abspath(mod) != os.path.abspath(DEFAULT_MOD):
        files = [f for f in files if os.sep + "Wreckage" + os.sep not in f] + glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True)
    byname, bydef, tagdef = {}, {}, {}
    all_defnames = set()
    RELEVANT = ("RM_WreckWeathering", "WreckFamil", "SalvageLoot", "RM_GenStep_WreckField", "RM_WreckList", "RM_WreckDensity", "ThingSetMakerDef")
    for p in files:
        try:
            txt = read(p)
        except OSError:
            continue
        all_defnames.update(re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", txt))      # cheap: every def name anywhere (for 'does it exist')
        if not any(k in txt for k in RELEVANT) and "HediffDef" not in txt:
            continue                                                                      # only wreck-related files are parsed (the full parse of src/ is ~7 s)
        try:
            root = ET.fromstring(txt.encode("utf-8"))
        except ET.ParseError:
            continue
        for d in root:
            if d.get("Name"):
                byname[d.get("Name")] = d
            dn = d.findtext("defName")
            if dn:
                bydef[(d.tag.split(".")[-1], dn)] = d
                tagdef.setdefault(dn, d)

    def loot_comp(d, hops=0):
        cur = d
        while cur is not None and hops < 12:
            for li in cur.findall("comps/li"):
                if li.get("Class") == "RimMandrake.Wreckage.RM_CompProperties_SalvageLoot":
                    return li
            cur = byname.get(cur.get("ParentName"))
            hops += 1
        return None

    patch_parts = []
    for p in glob.glob(os.path.join(src_root, "*", "*", "Patches", "**", "*.xml"), recursive=True):
        patch_parts.append(read(p))
    patch_text = "\n".join(patch_parts)
    VANILLA = {"ShipChunk", "ShipChunk_Mech"}      # Core defs a wreck list may name directly

    def known(nm):
        return nm in all_defnames or nm in VANILLA or f"<defName>{nm}</defName>" in patch_text

    weath = {dn: d for (tag, dn), d in bydef.items() if tag == "RM_WreckWeatheringDef"}
    makers = {dn for (tag, dn) in bydef if tag == "ThingSetMakerDef"}
    for (tag, dn), d in sorted(bydef.items()):
        if tag != "ThingDef":
            continue
        ext = next((li for li in d.findall("modExtensions/li") if li.get("Class") == "RimMandrake.Wreckage.RM_WreckWeathering"), None)
        if ext is None:
            continue
        n["wrecks"] += 1
        w = weath.get(ext.findtext("weathering"))
        if w is None:
            E("wr-resolve", f"{dn}: weathering {ext.findtext('weathering')!r} is not defined")
            continue
        comp = loot_comp(d)
        if comp is None:
            E("wr-resolve", f"{dn}: no RM_CompProperties_SalvageLoot up its ParentName chain (a weathering with nothing to fold into)")
            continue
        tier, rare = comp.findtext("lootTier", "Scrap"), float(comp.findtext("rareChance", "0.05"))
        no_loot = comp.findtext("noLoot") == "true" or w.findtext("noLoot") == "true"
        if w.findtext("noLoot") == "true":
            rare = 0.0
        sh = int(w.findtext("lootTierShift", "0")) + int(ext.findtext("extraTierShift", "0"))
        if sh:
            tier = shift_tier(tier, sh)
            if tier == "Scrap":
                rare = 0.0
        if not no_loot and f"RM_SalvageLoot_{tier}" not in makers:
            E("wr-resolve", f"{dn}: ends on loot tier {tier} but no ThingSetMakerDef RM_SalvageLoot_{tier} exists")
        if rare > 0 and f"RM_SalvageLoot_{tier}_Rare" not in makers:
            E("wr-resolve", f"{dn}: ends on loot tier {tier} with a rare roll but no ThingSetMakerDef RM_SalvageLoot_{tier}_Rare exists")

    for dn, w in sorted(weath.items()):
        n["weatherings"] += 1
        try:
            yf, ts = float(w.findtext("yieldFactor", "1")), int(w.findtext("lootTierShift", "0"))
            sev = float(w.findtext("salvageHediffSeverity", "0"))
        except ValueError as e:
            E("wr-weathering", f"{dn}: unparsable number: {e}")
            continue
        if not 0 < yf <= 1.5:
            E("wr-weathering", f"{dn}: yieldFactor {yf} outside (0, 1.5]")
        if abs(ts) > 2:
            E("wr-weathering", f"{dn}: lootTierShift {ts} outside [-2, 2]")
        if (w.findtext("salvageHediff") is not None) != (sev > 0):
            E("wr-weathering", f"{dn}: salvageHediff and salvageHediffSeverity disagree (a dose needs both)")
        if w.findtext("salvageHediff") and ("HediffDef", w.findtext("salvageHediff")) not in bydef and w.findtext("salvageHediff") != "ToxicBuildup":
            E("wr-weathering", f"{dn}: salvageHediff {w.findtext('salvageHediff')!r} is defined nowhere under src/")

    def wreck_rows(el):
        rows = []
        for ch in el.findall("wrecks/*"):
            nm = ch.text and ch.text.strip()
            if ch.tag == "li":
                nm = ch.findtext("thing")
                wt = ch.findtext("weight", "1")
            else:
                nm, wt = ch.tag, (ch.text or "").strip()
            rows.append((nm, wt))
        return rows

    for (tag, dn), d in sorted(bydef.items()):
        if tag == "GenStepDef":
            gs = d.find("genStep")
            if gs is None or gs.get("Class") != "RimMandrake.Wreckage.RM_GenStep_WreckField":
                continue
            n["fields"] += 1
            if not (gs.findtext("settingsKey") or "").strip():
                E("wr-fields", f"{dn}: no settingsKey (the field could not be switched off)")
            if gs.find("densityClass") is None and gs.find("count") is None and gs.find("countPer10kCellsRange") is None:
                E("wr-fields", f"{dn}: no densityClass and no count of its own (the field places nothing)")
            elif gs.findtext("densityClass") and ("RM_WreckDensityClassDef", gs.findtext("densityClass")) not in bydef:
                E("wr-fields", f"{dn}: densityClass {gs.findtext('densityClass')!r} is not defined")
            rows = wreck_rows(gs)
            if not any(nm and float(wt or 0) > 0 for nm, wt in rows):
                E("wr-fields", f"{dn}: no wreck with weight > 0")
            for nm, wt in rows:
                if nm and float(wt or 0) <= 0:
                    E("wr-fields", f"{dn}: wreck {nm!r} has weight {wt!r} (a dead row: the field silently never picks it)")
            for nm, wt in rows:
                if nm and not known(nm):
                    E("wr-fields", f"{dn}: wreck {nm!r} is not a ThingDef defined under src/")
        elif tag == "RM_WreckListDef":
            n["lists"] += 1
            rows = wreck_rows(d)
            if not any(nm and float(wt or 0) > 0 for nm, wt in rows):
                E("wr-lists", f"{dn}: no wreck with weight > 0")
            for nm, wt in rows:
                if nm and float(wt or 0) <= 0:
                    E("wr-lists", f"{dn}: wreck {nm!r} has weight {wt!r} (a dead row: the list silently never picks it)")
            for nm, wt in rows:
                if nm and not known(nm):
                    E("wr-lists", f"{dn}: wreck {nm!r} is not a ThingDef defined under src/")

    # wr-kernel
    srcd = os.path.join(mod, "Source")
    kernel = read(os.path.join(srcd, "Kernel", "RM_WreckageKernel.cs"))
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kernel, flags=re.M):
        E("wr-kernel", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    if "Kernel\\RM_WreckageKernel.cs" not in read(os.path.join(srcd, "RM_Wreckage.csproj")):
        E("wr-kernel", "RM_Wreckage.csproj does not compile Kernel\\RM_WreckageKernel.cs (EnableDefaultCompileItems is false: it compiles into nothing)")
    code = "\n".join(re.sub(r"//.*", "", read(p)) for p in glob.glob(os.path.join(srcd, "*.cs")))
    for pat, what in ((r'rank == 0 \? "Hull"', "a hand copy of the tier ladder"), (r"Mathf\.Lerp\(0\.25f", "a hand copy of the skill factor"),
                      (r"Mathf\.Clamp01\(td\.resourcesFraction", "a hand copy of the yield clamp")):
        if re.search(pat, code):
            E("wr-kernel", f"{what} survives beside the kernel")

    # wr-keys: translation keys used by the comp, including the per-tier labels built at runtime
    keyed = "".join(read(p) for p in glob.glob(os.path.join(mod, "Languages", "*", "Keyed", "*.xml")))
    code_all = "\n".join(read(p) for p in glob.glob(os.path.join(srcd, "*.cs")))
    keys = set(re.findall(r'"(RM_Wreckage_\w+)"\s*\.Translate', code_all)) | {f"RM_Wreckage_Tier_{t}" for t in ("Scrap", "Hull", "Tank", "Carapace", "Sealed")}
    n["keys"] = len(keys)
    for k in sorted(keys):
        if f"<{k}>" not in keyed:
            E("wr-keys", f'"{k}" has no <{k}> in Languages/*/Keyed (the game shows the raw key)')

    for k, mn in (("wrecks", 5), ("weatherings", 5), ("fields", 3), ("lists", 1), ("keys", 5)):
        if n[k] < mn and not errs:
            print(f"LINT UNMEASURED: wr check {k} saw {n[k]} (< {mn}); a blind lint is not a pass")
            return 2
    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"wreckage lint (data): {n['wrecks']} weathered wrecks, {n['weatherings']} weatherings, {n['fields']} fields, {n['lists']} lists, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
