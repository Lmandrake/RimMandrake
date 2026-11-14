#!/usr/bin/env python3
"""Offline hook-scope selftest for Explosive Knockback (bar only_explosions_throw, test T_ONLY_EXPLOSIONS_STATIC).

Only explosions throw: the one Harmony patch that queues a throw is on the explosion's damage step
(DamageWorker.ExplosionDamageThing); the only other queue site is the gas-clump burst (GasBurst), reached only from a gas
ignition. No melee, bullet, projectile-impact or generic damage method is patched to queue a throw. Static read of
Source/*.cs (the release sources; the proof file is skipped, it is not in the release DLL). Planted faults are run on
copies and must go red.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_hook_scope.py
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
QUEUE_TARGET = ("DamageWorker", "ExplosionDamageThing")
BANNED_TYPES = re.compile(r"Verb_Melee|Verb_Shoot|Bullet|Projectile|DamageWorker_AddInjury|DamageWorker_Blunt|DamageWorker_Cut|"
                          r"DamageWorker_Stab|Pawn_HealthTracker|MeleeAttack", re.I)
GAS_CALLERS = {"VentGasIgnitePostfix"}   # the Cauldron vent-gas ignition postfix (RM_KnockbackCompat)


def read_sources(files=None):
    files = files or [f for f in glob.glob(os.path.join(SRC, "*.cs")) if not f.endswith("RM_KnockbackProof.cs")]
    return {os.path.basename(f): open(f, encoding="utf-8", errors="replace").read() for f in files}


def classes(text):
    """(attribute block, class name, body) for every top-level class, by brace matching."""
    out = []
    for m in re.finditer(r"((?:\s*\[[^\]]*\]\s*)*)\s*(?:public|internal)\s+(?:static\s+|sealed\s+)*class\s+(\w+)[^{]*\{", text):
        i, depth = m.end(), 1
        while depth and i < len(text):
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        out.append((m.group(1), m.group(2), text[m.end():i]))
    return out


def methods_calling(body, needle):
    """Names of methods in a class body whose own text contains needle."""
    names = []
    for m in re.finditer(r"(?:public|private|internal|protected)\s+(?:static\s+)?[\w<>\[\],. ]+\s+(\w+)\s*\([^)]*\)\s*\{", body):
        i, depth = m.end(), 1
        while depth and i < len(body):
            depth += {"{": 1, "}": -1}.get(body[i], 0)
            i += 1
        if needle in body[m.end():i]:
            names.append(m.group(1))
    return names


def judge(srcs):
    """Return a list of faults (empty = pass)."""
    faults, queue_classes, burst_callers, explosion_patch = [], [], set(), False
    for fname, text in srcs.items():
        for attrs, name, body in classes(text):
            target = re.search(r"HarmonyPatch\(typeof\((\w+)\),\s*(?:\"(\w+)\"|nameof\([\w.]*?(\w+)\))", attrs)
            ttype, tmeth = (target.group(1), target.group(2) or target.group(3)) if target else (None, None)
            if ttype and BANNED_TYPES.search(ttype):
                faults.append("%s: %s patches %s.%s, a melee/bullet/damage step" % (fname, name, ttype, tmeth))
            if (ttype, tmeth) == QUEUE_TARGET:
                explosion_patch = True
            enq = methods_calling(body, ".Enqueue(new KnockbackRequest")
            if enq:
                queue_classes.append((fname, name, ttype, tmeth, enq))
            burst_callers |= {(fname, name, mth) for mth in methods_calling(body, "GasBurst(")}
        for m in re.finditer(r"\.Patch\(\s*(\w+)", text):  # manual Harmony.Patch(original, ...): name the original's lookup
            decl = re.search(r"%s\s*=\s*[^;]*AccessTools\.Method\(\s*(\w+)\s*,\s*\"(\w+)\"" % re.escape(m.group(1)), text)
            if decl and BANNED_TYPES.search(decl.group(1)):
                faults.append("%s: manual Patch of %s.%s, a melee/bullet/damage step" % (fname, decl.group(1), decl.group(2)))
    for fname, name, ttype, tmeth, enq in queue_classes:
        if (ttype, tmeth) == QUEUE_TARGET:
            continue
        if name == "RM_MapComponent_Knockback" and set(enq) <= {"GasBurst"}:
            continue
        faults.append("%s: %s queues a throw from %s but is not the explosion damage-step patch (target %s.%s)"
                      % (fname, name, ",".join(enq), ttype, tmeth))
    for fname, name, mth in burst_callers:
        if mth not in GAS_CALLERS and mth != "GasBurst":
            faults.append("%s: %s.%s calls GasBurst; only a gas ignition may" % (fname, name, mth))
    if not explosion_patch:
        faults.append("no patch on DamageWorker.ExplosionDamageThing: the explosion hook is gone")
    if not queue_classes:
        faults.append("no throw is queued anywhere: the reader is blind")
    return faults


def main():
    srcs = read_sources()
    faults = judge(srcs)
    for f in faults:
        print("FAIL", f)
    # planted faults: each must go red
    patch = "RM_Patch_DamageWorker_ExplosionKnockback.cs"
    mutants = {
        "hook moved to the generic injury step": (patch, '[HarmonyPatch(typeof(DamageWorker), "ExplosionDamageThing")]',
                                                  '[HarmonyPatch(typeof(DamageWorker_AddInjury), "Apply")]'),
        "a bullet impact patch that queues a throw": (patch, "namespace RimMandrake.ExplosiveKnockback\n{",
            "namespace RimMandrake.ExplosiveKnockback\n{\n    [HarmonyPatch(typeof(Bullet), \"Impact\")]\n    public static class RM_Patch_Bullet_Throw\n"
            "    {\n        public static void Postfix(Bullet __instance)\n        {\n            comp.Enqueue(new KnockbackRequest { });\n        }\n    }\n"),
        "a melee verb calling the gas burst": (patch, "namespace RimMandrake.ExplosiveKnockback\n{",
            "namespace RimMandrake.ExplosiveKnockback\n{\n    public static class RM_MeleeShove\n    {\n        public static void Hit(Map m)\n"
            "        {\n            RM_MapComponent_Knockback.GasBurst(m, IntVec3.Zero, null, \"melee\");\n        }\n    }\n"),
    }
    missed = 0
    for label, (f, old, new) in mutants.items():
        if old not in srcs.get(f, ""):
            print("FAIL planted fault '%s' could not be planted (anchor gone)" % label)
            missed += 1
            continue
        m = dict(srcs)
        m[f] = m[f].replace(old, new, 1)
        if not judge(m):
            print("FAIL planted fault NOT CAUGHT:", label)
            missed += 1
    ok = not faults and not missed
    print("explosive knockback hook scope: %s (%d faults, %d/%d planted faults caught)"
          % ("PASS" if ok else "FAIL", len(faults), len(mutants) - missed, len(mutants)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
