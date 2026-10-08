#!/usr/bin/env python3
"""Offline lint of RimProperty (the ownership fabric): the generic mod lint (lint_mod_defs.py) plus data checks the generic lint cannot see:

  rp-enums       the kernel's restated constants equal the enums they stand for (ClaimantKind, TakingAct), so a reordered enum cannot
                 silently change who outranks whom or which act steals
  rp-tuning      PropertyTuning stays coherent: lifetime min < max, situational claim stronger than territorial and below 1 (a stored
                 full-strength claim must beat a possessor), suspicion half-life and rates positive; every setting default (a tuning
                 constant or a literal) lies inside its slider range; no slider reaches a value that breaks the kernel's domain
                 (lifetime multiplier 0, half-life 0, fee below one silver, markup <= 0)
  rp-money       every silver-taking menu delegate pays through TryPaySilver (the fee is re-checked at click time, so a pawn who dropped
                 silver after the menu was built cannot buy the claim for less); WARN when the markup slider can go below 1 (buying under
                 market value); the salvage fee, price and configured fees printed at the slider extremes
  rp-decay       how long a stolen claim holds against the thief: the situational claim (0.9) overtakes a full-strength record after 10% of
                 the lifetime, printed in days for the least and most recognizable things at the default multiplier
  rp-wiring      the kernel is Verse-free and listed in the mod csproj and in the older net472 selftest's compile list (ClaimDecay and
                 ClaimWipe call it); the Fuzz project is not compiled into the mod; the mod's recognizability weights alias the kernel's

    python3 src/RimMandrake/Utils/lint_property_defs.py [--quiet] [--mod-dir D] [--plant-check]
"""
import contextlib
import glob
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(REPO, "src")
DEFAULT_MOD = os.path.join(SRC, "RimMandrake", "RimProperty")


def read(p):
    return open(p, encoding="utf-8-sig").read()


def num(expr, tuning):
    expr = expr.strip().rstrip(";")
    m = re.fullmatch(r"PropertyTuning\.(\w+)", expr)
    if m:
        return tuning.get(m.group(1))
    try:
        return float(eval(re.sub(r"(\d)f\b", r"\1", expr), {"__builtins__": {}}, {}))
    except Exception:
        return None


def enum_values(text, name):
    m = re.search(r"enum " + name + r"[^{]*\{(.*?)\}", text, flags=re.S)
    if not m:
        return None
    vals, nxt = {}, 0
    for line in re.sub(r"//[^\n]*", "", m.group(1)).split(","):
        line = line.strip()
        if not line:
            continue
        mm = re.fullmatch(r"(\w+)(?:\s*=\s*(\d+))?", line)
        if not mm:
            continue
        nxt = int(mm.group(2)) if mm.group(2) is not None else nxt
        vals[mm.group(1)] = nxt
        nxt += 1
    return vals


def main(argv):
    quiet = "--quiet" in argv
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else DEFAULT_MOD
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("RimProperty", ["--mod-dir", mod])
    gl = buf.getvalue().splitlines()
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs = [l for l in gl if l.startswith("ERROR")]
    warns = [l for l in gl if l.startswith("WARN")]
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    W = lambda c, m: warns.append(f"WARN  {c}: {m}")
    src = os.path.join(mod, "Source")
    kernel = read(os.path.join(src, "Kernel", "RM_PropertyKernel.cs"))
    n = {"consts": 0, "sliders": 0, "delegates": 0}

    # ---- enums ----
    kinds = enum_values(read(os.path.join(src, "ClaimantKind.cs")), "ClaimantKind")
    acts = enum_values(read(os.path.join(src, "TakingAct.cs")), "TakingAct")
    bases = enum_values(read(os.path.join(src, "ClaimBasis.cs")), "ClaimBasis")
    if not kinds or not acts or not bases:
        print("LINT UNMEASURED: ClaimantKind / TakingAct / ClaimBasis not parsed")
        return 2
    kc = dict((m.group(1), int(m.group(2))) for m in re.finditer(r"\b(Kind\w+) = (\d+)", kernel))
    ac = dict((m.group(1), int(m.group(2))) for m in re.finditer(r"\b(Act\w+) = (\d+)", kernel))
    for nm, want in (("KindNone", kinds["None"]), ("KindPawn", kinds["Pawn"]), ("KindCommons", kinds["Commons"])):
        n["consts"] += 1
        if kc.get(nm) != want:
            E("rp-enums", f"kernel {nm} = {kc.get(nm)} but ClaimantKind says {want}")
    for nm, want in (("ActTake", acts["Take"]), ("ActUse", acts["Use"]), ("ActStrip", acts["Strip"]), ("ActSabotage", acts["Sabotage"]), ("ActBuy", acts["Buy"]), ("ActClaim", acts["Claim"])):
        n["consts"] += 1
        if ac.get(nm) != want:
            E("rp-enums", f"kernel {nm} = {ac.get(nm)} but TakingAct says {want}")
    # the fuzz and the engine write basis ints 2..8 for the stored bases
    for nm, want in (("Stolen", 2), ("Purchased", 3), ("ClaimFeePaid", 4), ("Gifted", 5), ("Inherited", 6), ("Looted", 7), ("BattleLootOrigin", 8)):
        if bases.get(nm) != want:
            E("rp-enums", f"ClaimBasis.{nm} = {bases.get(nm)} but the fuzz's ledger model assumes {want}")
    if bases.get("Territorial") != 0 or bases.get("Situational") != 1:
        E("rp-enums", "the virtual bases are no longer 0 / 1")

    # ---- tuning and sliders ----
    tuning = {}
    tsrc = read(os.path.join(src, "PropertyTuning.cs"))
    for m in re.finditer(r"public const (?:float|int) (\w+) = ([^;]+);", tsrc):
        v = num(m.group(2), {})
        if v is not None:
            tuning[m.group(1)] = v
    if len(tuning) < 10:
        print("LINT UNMEASURED: PropertyTuning constants not parsed")
        return 2
    t = tuning.get
    if not t("MinClaimLifetimeDays") < t("MaxClaimLifetimeDays"):
        E("rp-tuning", "claim lifetime min is not below max")
    if not (0 < t("TerritorialClaimStrength") < t("SituationalClaimStrength") < 1):
        E("rp-tuning", f"territorial {t('TerritorialClaimStrength')} / situational {t('SituationalClaimStrength')} must satisfy 0 < territorial < situational < 1")
    if t("SuspicionHalfLifeDays") <= 0 or t("DefaultPropagationRatePerDay") <= 0:
        E("rp-tuning", "suspicion half-life or propagation rate not positive")
    ssrc = read(os.path.join(src, "PropertySettings.cs"))
    fields = {}
    for m in re.finditer(r"public static (?:float|int) (\w+) = ([^;]+);", ssrc):
        fields[m.group(1)] = num(m.group(2), tuning)
    sliders = {}
    for m in re.finditer(r"(\w+) = (?:Mathf\.RoundToInt\()?list\.Slider\(\1, ([0-9.]+)f, ([0-9.]+)f\)", ssrc):
        sliders[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    if not sliders:
        print("LINT UNMEASURED: no sliders parsed from PropertySettings.cs")
        return 2
    for nm, (lo, hi) in sliders.items():
        n["sliders"] += 1
        d = fields.get(nm)
        if d is None:
            W("rp-tuning", f"slider {nm} has no parsable default")
        elif not (lo <= d <= hi):
            E("rp-tuning", f"{nm} default {d} lies outside its slider {lo}..{hi}")
    lo = lambda k: sliders.get(k, (None, None))[0]
    if lo("claimLifetimeMultiplier") is not None and lo("claimLifetimeMultiplier") <= 0:
        E("rp-tuning", "claimLifetimeMultiplier can reach 0: every claim would be dead the moment it is born")
    if lo("suspicionHalfLifeDays") is not None and lo("suspicionHalfLifeDays") <= 0:
        E("rp-tuning", "suspicionHalfLifeDays can reach 0: the decay divides by zero")
    if lo("walkableCommerceMarkup") is not None and lo("walkableCommerceMarkup") <= 0:
        E("rp-tuning", "walkableCommerceMarkup can reach 0 or below")
    if lo("salvageClaimFeeMultiplier") is not None and lo("salvageClaimFeeMultiplier") <= 0:
        E("rp-tuning", "salvageClaimFeeMultiplier can reach 0 or below")
    hi = lambda k: sliders.get(k, (None, None))[1]
    for k in ("witnessConfidence", "bribeDampenFraction", "animalTheftFrequencyMultiplier"):
        if k in sliders and not (sliders[k][0] >= 0 and sliders[k][1] <= 1):
            E("rp-tuning", f"{k} slider leaves 0..1")
    if "walkableCommerceMarkup" in sliders and sliders["walkableCommerceMarkup"][0] < 1:
        W("rp-money", f"walkableCommerceMarkup can go down to {sliders['walkableCommerceMarkup'][0]}: a thing bought below its market value")

    # ---- money: every paying delegate re-checks at click ----
    for fn in glob.glob(os.path.join(src, "**", "FloatMenuOptionProvider_*.cs"), recursive=True):
        txt = read(fn)
        if "RemoveSilverFromInventory" in txt:
            n["delegates"] += 1
            E("rp-money", f"{os.path.relpath(fn, src)} takes silver with RemoveSilverFromInventory in its delegate: the fee is not re-checked at click time (use TryPaySilver)")
        elif "TryPaySilver" in txt:
            n["delegates"] += 1
            if not re.search(r"if \(!\w+\.TryPaySilver\(actor, \w+\)\)\s*\{[^}]*return;", txt, flags=re.S):
                E("rp-money", f"{os.path.relpath(fn, src)} calls TryPaySilver but does not stop when it fails")
    if n["delegates"] < 4:
        E("rp-money", f"only {n['delegates']} paying delegates found; expected the salvage claim, buy, bribe and hire menus (sanity probe)")
    util = read(os.path.join(src, "SalvageClaim", "SalvageClaimFeeUtility.cs"))
    if "CanPay(" not in util or "TakeFromStack(" not in util:
        E("rp-money", "SalvageClaimFeeUtility no longer pays through the kernel's CanPay / TakeFromStack")

    # ---- decay horizon ----
    sit, mn, mx = t("SituationalClaimStrength"), t("MinClaimLifetimeDays"), t("MaxClaimLifetimeDays")
    lo_d, hi_d = mn * (1 - sit), mx * (1 - sit)
    n["flip_days"] = (round(lo_d, 2), round(hi_d, 1))
    W("rp-decay", f"a stolen claim (full strength) is overtaken by the thief's situational {sit} claim after {lo_d:.2f} days for the least recognizable thing "
                  f"and {hi_d:.0f} days for the most, at the default lifetime multiplier: the holder's own claim then outranks the victim's: ownership by possession after 10% of the claim's life")

    # ---- wiring ----
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kernel, flags=re.M):
        E("rp-wiring", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    proj = read(os.path.join(src, "RM_Property.csproj"))
    if 'Compile Include="Kernel\\RM_PropertyKernel.cs"' not in proj:
        E("rp-wiring", "the kernel is not listed in RM_Property.csproj (it compiles into nothing, silently)")
    if "SelfTest" in proj:
        E("rp-wiring", "the SelfTest / Fuzz folder is compiled into the mod assembly")
    old = os.path.join(src, "SelfTest", "RimMandrakeProperty.SelfTest.csproj")
    if os.path.exists(old) and "RM_PropertyKernel.cs" not in read(old):
        E("rp-wiring", "the net472 selftest compiles ClaimDecay / ClaimWipe but not the kernel they call")
    for fn, need in (("ClaimDecay.cs", "RM_PropertyKernel.LifetimeTicks"), ("ClaimEngine.cs", "RM_PropertyKernel.Order"), ("PropertyEngine.cs", "RM_PropertyKernel.SpineWrite"),
                     ("FactionRecord.cs", "RM_PropertyKernel.Contribution"), ("ClaimWipe.cs", "RM_PropertyKernel.IsKept"), ("RecognizabilityUtility.cs", "RM_PropertyKernel.Recognizability")):
        if need not in read(os.path.join(src, fn)):
            E("rp-wiring", f"{fn} no longer calls {need}")
    rec = read(os.path.join(src, "RecognizabilityUtility.cs"))
    for nm in ("QualityWeight", "MarketValueWeight", "NamedWeight", "MechanoidWeight", "NonStackableWeight", "MarketValueSaturation"):
        if not re.search(nm + r" = RM_PropertyKernel\." + nm, rec):
            E("rp-wiring", f"RecognizabilityUtility.{nm} is no longer an alias of the kernel's")

    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"property lint (data): {n['consts']} enum constants, {len(tuning)} tuning constants, {n['sliders']} slider ranges, "
          f"{n['delegates']} paying delegates, stolen claims hold {n.get('flip_days', ('?', '?'))[0]}..{n.get('flip_days', ('?', '?'))[1]} days, "
          f"{len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


PLANTS = [
    ("enum reordered", "Source/TakingAct.cs", "Take,\n        Use,", "Use,\n        Take,"),
    ("claimant kinds reordered", "Source/ClaimantKind.cs", "Pawn = 1,\n        Commons = 2,", "Pawn = 2,\n        Commons = 1,"),
    ("situational above one", "Source/PropertyTuning.cs", "SituationalClaimStrength = 0.9f;", "SituationalClaimStrength = 1.2f;"),
    ("territorial above situational", "Source/PropertyTuning.cs", "TerritorialClaimStrength = 0.5f;", "TerritorialClaimStrength = 0.95f;"),
    ("lifetime multiplier slider reaches zero", "Source/PropertySettings.cs", "claimLifetimeMultiplier = list.Slider(claimLifetimeMultiplier, 0.25f, 4f)", "claimLifetimeMultiplier = list.Slider(claimLifetimeMultiplier, 0f, 4f)"),
    ("half-life slider reaches zero", "Source/PropertySettings.cs", "suspicionHalfLifeDays = list.Slider(suspicionHalfLifeDays, 5f, 180f)", "suspicionHalfLifeDays = list.Slider(suspicionHalfLifeDays, 0f, 180f)"),
    ("default outside its slider", "Source/PropertySettings.cs", "witnessRadius = list.Slider(witnessRadius, 5f, 40f)", "witnessRadius = list.Slider(witnessRadius, 20f, 40f)"),
    ("bribe pays at menu time", "Source/Bribe/FloatMenuOptionProvider_Bribe.cs", "if (!BribeUtility.TryPaySilver(actor, fee))", "BribeUtility.RemoveSilverFromInventory(actor, fee);\n                    if (false)"),
    ("buy does not stop on failure", "Source/WalkableCommerce/FloatMenuOptionProvider_BuyMerchandise.cs", "MessageTypeDefOf.RejectInput, false);\n                        return;", "MessageTypeDefOf.RejectInput, false);"),
    ("kernel imports Verse", "Source/Kernel/RM_PropertyKernel.cs", "using System;", "using System;\nusing Verse;"),
    ("kernel missing from csproj", "Source/RM_Property.csproj", '<Compile Include="Kernel\\RM_PropertyKernel.cs" />', ""),
    ("old selftest loses the kernel", "Source/SelfTest/RimMandrakeProperty.SelfTest.csproj", '<Compile Include="..\\Kernel\\RM_PropertyKernel.cs" />', ""),
    ("decay stops calling the kernel", "Source/ClaimDecay.cs", "RM_PropertyKernel.LifetimeTicks(", "LifetimeTicksX("),
    ("recognizability weight forked", "Source/RecognizabilityUtility.cs", "NamedWeight = RM_PropertyKernel.NamedWeight", "NamedWeight = 0.30f"),
]


def plant_check():
    import shutil
    import subprocess
    import tempfile
    caught = 0
    for name, rel, old, new in PLANTS:
        with tempfile.TemporaryDirectory() as td:
            dst = os.path.join(td, "RimProperty")
            shutil.copytree(DEFAULT_MOD, dst, ignore=shutil.ignore_patterns("__pycache__", "Assemblies", "bin", "obj", "Textures", "Fuzz"))
            f = os.path.join(dst, rel)
            t = open(f, encoding="utf-8").read()
            if old not in t:
                print("PLANT TARGET NOT FOUND:", name)
                continue
            open(f, "w", encoding="utf-8").write(t.replace(old, new, 1))
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--quiet", "--mod-dir", dst], capture_output=True, text=True)
            hit = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("ERROR") or "Traceback" in l]
            print(("CAUGHT  " if hit else "MISSED  ") + name + ("  " + hit[0][:110] if hit else ""))
            caught += bool(hit)
    print(f"{caught}/{len(PLANTS)} planted defects caught")
    return 0 if caught == len(PLANTS) else 1


if __name__ == "__main__":
    if "--plant-check" in sys.argv:
        sys.exit(plant_check())
    sys.exit(main(sys.argv[1:]))
