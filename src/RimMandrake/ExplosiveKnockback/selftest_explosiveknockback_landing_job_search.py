#!/usr/bin/env python3
"""Offline selftest: a pawn our knockback throws lands without vanilla's full job search
(RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES, Test Pilot sitting 2026-11-16).

Live, SteveDesktop, the Explosive Knockback tier (34 mods), the walk storeroom rebuilt on a quicktest: the mod-on frame arms
read p99 +17.4% over mod off across 9 cold pairs (43.2 / 36.8 ms), and +1.2% with the storeroom's five colonists removed.
Proof timers put 19-25 ms of a landing frame inside PawnFlyer.RespawnPawn, whose last act is
pawn.jobs.CheckForJobOverride(): a full think-tree job search. Our RespawnPawn postfix then starts the job suspended at
takeoff (or the remembered haul) anyway, so for a pawn we threw that search is spent and thrown away; a pawn with nothing to
resume finds its job on its next tick (Pawn_JobTracker: curJob == null -> TryFindAndStartJob), as any idle pawn does.

So, read statically from Source/RM_PawnFlyerPatches.cs:
  LJ1 a Harmony prefix on Pawn_JobTracker.CheckForJobOverride returns false only for the pawn our landing holds
  LJ2 that pawn is set in the RespawnPawn prefix only after the RM_PawnFlyer_Knockback def check (vanilla jumps and other
      mods' flyers keep their job search)
  LJ3 it is cleared by a Harmony Finalizer on RespawnPawn (runs even when RespawnPawn throws: no pawn is left unable to
      re-think)
  LJ4 the RespawnPawn postfix still resumes the suspended job (Resume) for the landed pawn
Planted faults on copies (each must go red): the skip for every pawn, the flag set before the def check, no Finalizer,
the Resume call removed.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_landing_job_search.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source", "RM_PawnFlyerPatches.cs")


def _block(text, start_pat):
    """The brace block of the first class or method whose header matches start_pat, or ''."""
    m = re.search(start_pat, text)
    if not m:
        return ""
    i = text.find("{", m.end())
    if i < 0:
        return ""
    depth = 0
    for j in range(i, len(text)):
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        if depth == 0:
            return text[m.start():j + 1]
    return ""


def check(text):
    """-> list of (id, ok, what)."""
    out = []
    skip_cls = _block(text, r'\[HarmonyPatch\(typeof\(Pawn_JobTracker\),\s*(?:nameof\(Pawn_JobTracker\.CheckForJobOverride\)|"CheckForJobOverride")\)\]\s*public static class \w+')
    skip_pre = _block(skip_cls, r"public static bool Prefix\([^)]*\)")
    m = re.search(r"return\s+(.+?);", skip_pre, re.S)
    ret = m.group(1) if m else ""
    lj1 = bool(skip_cls) and "Pawn ___pawn" in skip_pre and re.search(r"___pawn\s*!=\s*\w+\.LandingPawn|\w+\.LandingPawn\s*!=\s*___pawn", ret) is not None \
        and ret.count("return") == 0 and skip_pre.count("return") == 1
    out.append(("LJ1", lj1, "CheckForJobOverride prefix skips only the landing pawn (return %r)" % ret.strip()[:80]))
    land_cls = _block(text, r'\[HarmonyPatch\(typeof\(PawnFlyer\),\s*"RespawnPawn"\)\]\s*public static class \w+')
    land_pre = _block(land_cls, r"public static void Prefix\([^)]*\)")
    guard = re.search(r"if \(__instance\.def != RM_KnockbackDefOf\.RM_PawnFlyer_Knockback\)\s*\{\s*return;\s*\}", land_pre)
    sets = [mm.start() for mm in re.finditer(r"LandingPawn\s*=\s*(?!null)", land_pre)]
    out.append(("LJ2", bool(guard) and bool(sets) and all(s > guard.end() for s in sets),
                "LandingPawn set in the RespawnPawn prefix only after our def check (guard %s, sets %d)" % (bool(guard), len(sets))))
    fin = _block(land_cls, r"public static void Finalizer\([^)]*\)")
    out.append(("LJ3", re.search(r"LandingPawn\s*=\s*null", fin) is not None, "a RespawnPawn Finalizer clears LandingPawn"))
    post = _block(land_cls, r"public static void Postfix\([^)]*\)")
    out.append(("LJ4", re.search(r"Resume\(__state\.pawn,\s*__state\.resume\)", post) is not None, "the postfix still resumes the suspended job"))
    return out


def main():
    text = open(SRC, encoding="utf-8").read()
    fails = []
    for cid, ok, what in check(text):
        print("%s %-4s %s" % ("PASS" if ok else "FAIL", cid, what))
        if not ok:
            fails.append(cid)
    mutants = {
        "skip_every_pawn": (re.sub(r"return\s+___pawn\s*!=\s*\w+\.LandingPawn;", "return false;", text), "LJ1"),
        "flag_before_def_check": (text.replace("            if (__instance.def != RM_KnockbackDefOf.RM_PawnFlyer_Knockback)\n            {\n                return;\n            }\n",
                                               "            LandingPawn = __instance.FlyingPawn;\n            if (__instance.def != RM_KnockbackDefOf.RM_PawnFlyer_Knockback)\n            {\n                return;\n            }\n", 1), "LJ2"),
        "no_finalizer": (re.sub(r"public static void Finalizer\(", "public static void NotAFinalizer(", text), "LJ3"),
        "no_resume": (re.sub(r"Resume\(__state\.pawn,\s*__state\.resume\);", ";", text), "LJ4"),
    }
    for name, (mt, want) in mutants.items():
        got = dict((c, ok) for c, ok, _ in check(mt))
        red = mt != text and got.get(want) is False
        print("%s M:%-22s planted fault turns %s red" % ("PASS" if red else "FAIL", name, want))
        if not red:
            fails.append("M:" + name)
    print("%s landing job search: %d failed" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
