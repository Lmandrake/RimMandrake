#!/usr/bin/env python3
"""CATHEDRALPASS_DECIDE_RETALIATION: source contract. Offline, no game.

A pass holder who deliberately strikes a faction-13 machine on Cathedral ground loses THEIR pass (the pass's own
Revoke verb), after which vanilla hostility lets the machines answer. Withdrawal, not vengeance
(cathedral_concealment_arc_spec.md §0/§6.2): no goodwill change, no clan-wide revoke, no raid. Checks the C#:

  * a Harmony PREFIX on Thing.TakeDamage, gated by the cathedralPassEnabled setting;
  * gates in place: player-faction instigator, faction-13 victim (Faction.OfMechanoids only), same Cathedral map,
    holder holds the pass, not in a mental state, not Extinguish, Amount > 0;
  * a deliberate strike only: IntendedTarget == victim, else the holder's current job target;
  * it calls CathedralPass.Revoke(holder) (one pawn) and never RevokeFromAll / goodwill / incidents;
  * the built DLL carries the patch class and its .srchash matches the source.

Sanity probe: each check must MISS on a mutated copy, or the instrument could not see a regression.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source", "Patch_CathedralPassHostility.cs")
DLL = os.path.join(HERE, "Assemblies", "RimMandrake.Utinni.CathedralPass.dll")
SRCHASH = DLL + ".srchash"


def retaliation_block(text):
    i = text.find("public static class Patch_CathedralPassRetaliation")
    return text[i - 400:] if i >= 0 else ""


CHECKS = [
    ("setting-gated feature", r'PatchFeature\("Patch_CathedralPassRetaliation", typeof\(CathedralPassSettings\), "cathedralPassEnabled"\)'),
    ("targets Thing.TakeDamage", r'\[HarmonyPatch\(typeof\(Thing\), nameof\(Thing\.TakeDamage\)\)\]'),
    ("is a prefix (victim still spawned)", r'public static void Prefix\(Thing __instance, DamageInfo dinfo\)'),
    ("setting checked at runtime", r'!CathedralPassSettings\.cathedralPassEnabled'),
    ("instigator is a pawn", r'!\(dinfo\.Instigator is Pawn holder\)'),
    ("positive damage only", r'dinfo\.Amount <= 0f'),
    ("player-faction striker", r'holder\.Faction != Faction\.OfPlayer'),
    ("faction-13 victim only", r'__instance\.Faction != mechs'),
    ("extinguish and mental state excluded", r'dinfo\.Def == DamageDefOf\.Extinguish \|\| holder\.InMentalState'),
    ("Cathedral map, same map", r'holder\.MapHeld != map \|\| !CathedralPass\.IsCathedralMap\(map\)'),
    ("holder must hold the pass, strike deliberate", r'!CathedralPass\.Holds\(holder\) \|\| !IsDeliberateStrike\(holder, __instance, dinfo\)'),
    ("intended target decides when set", r'if \(intended != null\)\s*\{\s*return intended == victim;'),
    ("else the current job target", r'holder\.CurJob\.targetA\.Thing == victim'),
    ("revokes the striker only", r'CathedralPass\.Revoke\(holder\)'),
    ("revoke message in behaviour register", r'Messages\.Message\(\s*"The old sentinels no longer look away from "'),
]
FORBIDDEN = [
    ("no clan-wide revoke here (that is the GM layer's verb)", r'RevokeFromAll'),
    ("no goodwill change (withdrawal, not vengeance)", r'TryAffectGoodwillWith|Goodwill'),
    ("no incident or raid", r'IncidentDef|TryExecute|Raid'),
    ("revoke message names no agency/recognition/mercy pre-reveal (arc ban 2, knowledge gate)",
     r'(?i)Messages\.Message\(\s*"[^"]*(cathedral|machine|droid|\bknow|recogni|mercy|spare|forgiv|\bdecid)'),
]


def check(text):
    block = retaliation_block(text)
    if not block:
        return ["missing: Patch_CathedralPassRetaliation class"]
    bad = []
    for label, rx in CHECKS:
        if not re.search(rx, block):
            bad.append("missing: " + label)
    for label, rx in FORBIDDEN:
        if re.search(rx, block):
            bad.append("forbidden: " + label)
    return bad


def srchash_ok():
    if not os.path.exists(SRCHASH):
        return "no .srchash beside the DLL"
    with open(SRC, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    with open(SRCHASH, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2 and parts[1] == "Patch_CathedralPassHostility.cs":
                return None if parts[0] == h else "DLL built from a different Patch_CathedralPassHostility.cs (rebuild)"
    return "Patch_CathedralPassHostility.cs not listed in .srchash"


def main():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()
    fails = check(text)

    mutants = [
        text.replace("public static class Patch_CathedralPassRetaliation", "public static class X"),
        text.replace("nameof(Thing.TakeDamage)", "nameof(Thing.Kill)"),
        text.replace("__instance.Faction != mechs", "__instance.Faction == null"),
        text.replace("|| holder.InMentalState", ""),
        text.replace("return intended == victim;", "return true;"),
        text.replace("CathedralPass.Revoke(holder)", "CathedralPass.RevokeFromAll() > 0"),
        text.replace("!CathedralPass.IsCathedralMap(map)", "false"),
    ]
    for i, m in enumerate(mutants):
        if m == text or not check(m):
            fails.append("sanity: mutant %d not detected (instrument blind)" % i)

    with open(DLL, "rb") as f:
        if b"Patch_CathedralPassRetaliation" not in f.read():
            fails.append("built DLL lacks Patch_CathedralPassRetaliation (not rebuilt)")
    err = srchash_ok()
    if err:
        fails.append(err)

    for x in fails:
        print("FAIL", x)
    if fails:
        return 1
    print("PASS selftest_cathedralpass_retaliation: %d contract checks, %d mutants caught, DLL current" % (len(CHECKS) + len(FORBIDDEN), len(mutants)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
