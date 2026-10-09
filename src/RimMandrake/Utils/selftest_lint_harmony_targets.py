#!/usr/bin/env python3
"""selftest_lint_harmony_targets.py - the Harmony target lint must be able to fail (HARMONY_PATCH_RESILIENCE_1).

Part 1 (always): a synthetic assembly index and synthetic C# prove each verdict both ways: a present member is OK, a
renamed one is MISSING_MEMBER, a wrong argument count is ARITY, an unknown type is MISSING_TYPE (or UNRESOLVED when the
file imports a foreign namespace), inherited members resolve, getters need get_X, TargetMethod classes are DYNAMIC,
stacked and method-level attributes merge, reflection hooks are read.
Part 2 (when the game DLL is reachable): a sanity probe against the REAL index - FlowWorks' Fire.SpawnSetup patch
resolves OK and a mutated copy naming Fire.SpawnSetupX comes back MISSING_MEMBER. UNMEASURED (exit 0, said so) when
the game is not installed where the lint looks.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_harmony_targets as L  # noqa: E402

FAILS = []


def check(name, cond, got=None):
    print("%s  %s%s" % ("ok  " if cond else "FAIL", name, "" if cond else "  got %r" % (got,)))
    if not cond:
        FAILS.append(name)


def synthetic_index():
    types = {
        "Verse.Thing": {"ns": "Verse", "name": "Thing", "base": None,
                        "methods": {"SpawnSetup": [2], "get_Position": [0], ".ctor": [0]}, "fields": ["mapIndexOrState"]},
        "RimWorld.Fire": {"ns": "RimWorld", "name": "Fire", "base": "Verse.Thing",
                          "methods": {"Tick": [0], "TrySpread": [0, 1]}, "fields": ["fireSize"]},
        "Verse.AI.Reachability": {"ns": "Verse.AI", "name": "Reachability", "base": None,
                                  "methods": {"CanReach": [4, 5]}, "fields": ["map"]},
    }
    by_simple = {}
    for k, v in types.items():
        by_simple.setdefault(v["name"], []).append(k)
    return {"types": types, "by_simple": by_simple, "namespaces": {v["ns"] for v in types.values()}, "missing": []}


SRC = '''
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;
namespace X {
    [HarmonyPatch(typeof(Fire), nameof(Fire.SpawnSetup))]          // inherited from Thing: OK
    public static class P1 { public static void Postfix() {} }

    [HarmonyPatch(typeof(Fire), "Ignite")]                           // renamed: MISSING_MEMBER
    public static class P2 { public static void Postfix() {} }

    [HarmonyPatch(typeof(Reachability), nameof(Reachability.CanReach),
        new[] { typeof(IntVec3), typeof(LocalTargetInfo), typeof(PathEndMode) })]   // 3 params: ARITY
    public static class P3 { public static void Postfix() {} }

    [HarmonyPatch(typeof(Reachability), nameof(Reachability.CanReach),
        new[] { typeof(IntVec3), typeof(LocalTargetInfo), typeof(PathEndMode), typeof(TraverseParms) })]
    public static class P4 { public static void Postfix() {} }      // 4 params: OK

    [HarmonyPatch(typeof(Fire), nameof(Fire.Position), MethodType.Getter)]   // get_Position on Thing: OK
    public static class P5 { public static void Postfix() {} }

    [HarmonyPatch(typeof(Fire), nameof(Fire.fireSize), MethodType.Getter)]   // a FIELD, not a property: MISSING
    public static class P6 { public static void Postfix() {} }

    [HarmonyPatch(typeof(Gone), "Anything")]                         // no such type, no foreign usings: MISSING_TYPE
    public static class P7 { public static void Postfix() {} }

    [HarmonyPatch]
    public static class P8 { static System.Reflection.MethodBase TargetMethod() => null; public static void Postfix() {} }

    [HarmonyPatch(typeof(Fire))]
    [HarmonyPatch("Tick")]                                           // stacked: OK
    public static class P9 { public static void Postfix() {} }

    [HarmonyPatch(typeof(Fire))]
    public static class P10 {
        [HarmonyPatch("TrySpread")] [HarmonyPostfix] public static void A() {}      // method-level: OK
        [HarmonyPatch("Spread2")] [HarmonyPostfix] public static void B() {}        // method-level: MISSING
    }

    public static class Uses {
        static object a = AccessTools.Method(typeof(Fire), "Tick");                  // OK
        static object b = AccessTools.Field(typeof(Fire), "fireSizeOld");            // MISSING (field)
        static object c = AccessTools.FieldRefAccess<Reachability, Map>("map");      // OK (field)
    }
}
'''

FOREIGN = '''
using HarmonyLib;
using Vehicles;
namespace Y {
    [HarmonyPatch(typeof(VehiclePawn), "Tick")]
    public static class Q1 { public static void Postfix() {} }
}
'''


def verdicts(src, path="t.cs"):
    idx = synthetic_index()
    usings = set(L._USING.findall(src))
    return [(t.get("cls"), t["kind"], t.get("member"), L.judge(idx, t, usings)[0]) for t in L.scan_text(src, path)]


def part1():
    v = verdicts(SRC)
    by = {}
    for cls, kind, member, verdict in v:
        by.setdefault((cls, member), verdict)
    check("inherited method resolves (Fire.SpawnSetup on Thing)", by.get(("P1", "SpawnSetup")) == "OK", by.get(("P1", "SpawnSetup")))
    check("renamed method is MISSING_MEMBER", by.get(("P2", "Ignite")) == "MISSING_MEMBER", by.get(("P2", "Ignite")))
    check("wrong argument count is ARITY", by.get(("P3", "CanReach")) == "ARITY", v)
    check("right argument count is OK", ("P4", "attr", "CanReach", "OK") in v, v)
    check("getter resolves through get_X", by.get(("P5", "Position")) == "OK", by.get(("P5", "Position")))
    check("a field named as a getter is MISSING_MEMBER", by.get(("P6", "fireSize")) == "MISSING_MEMBER", by.get(("P6", "fireSize")))
    check("unknown type with no foreign using is MISSING_TYPE", by.get(("P7", "Anything")) == "MISSING_TYPE", by.get(("P7", "Anything")))
    check("TargetMethod class is DYNAMIC", any(c == "P8" and k == "dynamic" for c, k, _, _ in v), v)
    check("stacked class attributes merge", by.get(("P9", "Tick")) == "OK", by.get(("P9", "Tick")))
    check("method-level attribute supplies the member (OK)", by.get(("P10", "TrySpread")) == "OK", v)
    check("method-level attribute supplies the member (MISSING)", by.get(("P10", "Spread2")) == "MISSING_MEMBER", v)
    refl = [x for x in v if x[1] == "reflect"]
    check("three reflection hooks read", len(refl) == 3, refl)
    check("AccessTools.Method OK", (None, "reflect", "Tick", "OK") in v, refl)
    check("AccessTools.Field renamed is MISSING_MEMBER", (None, "reflect", "fireSizeOld", "MISSING_MEMBER") in v, refl)
    check("FieldRefAccess OK", (None, "reflect", "map", "OK") in v, refl)
    f = verdicts(FOREIGN)
    check("a donor-mod type is UNRESOLVED, never OK or a FAIL", [x[3] for x in f] == ["UNRESOLVED"], f)
    # every class-level patch in SRC was found exactly once per target (no double counting of stacked attributes)
    attr_classes = sorted({c for c, k, _, _ in v if k in ("attr", "dynamic")})
    check("ten patch classes found", attr_classes == ["P%d" % i for i in (1, 10, 2, 3, 4, 5, 6, 7, 8, 9)], attr_classes)


FEAT = {
    "a.cs": '''
public static class Boot { static Boot() { RimMandrake.Shared.PatchApplier.Apply(h, asm, "X"); } }
public static class Settings { public static bool fireEnabled = true; }
/// <summary>Mentions [HarmonyPatch] in a doc comment: must not be read as a patch class.</summary>
[RimMandrake.Shared.PatchFeature("Fire", typeof(Settings), "fireEnabled")]
[HarmonyPatch(typeof(Fire), "Tick")]
public static class Good { }
[HarmonyPatch(typeof(Fire), "Tick")]
public static class Bare { }
[HarmonyPatch(typeof(Fire), "Tick")]
[RimMandrake.Shared.PatchFeature("Ghost", typeof(Settings), "ghostEnabled")]
public static class BadField { }
[HarmonyPatch(typeof(Fire), "Tick")]
[RimMandrake.Shared.PatchFeature("Swim only")]
public static class NoSetting { }
'''}


def part1b():
    texts = {k: L.strip_comments(v) for k, v in FEAT.items()}
    f = L.feature_findings(texts)
    kinds = sorted((v, d.split()[1]) for v, _, d in f)
    check("feature coverage: a bare patch class is NO_FEATURE, a missing field BAD_FEATURE, nothing else",
          kinds == [("BAD_FEATURE", "BadField"), ("NO_FEATURE", "Bare")], f)
    check("a mod that does not use PatchApplier is not judged",
          L.feature_findings({"b.cs": FEAT["a.cs"].replace("PatchApplier.Apply(", "PatchAll(")}) == [], None)
    raw = L.scan_text(FEAT["a.cs"])
    clean = L.scan_text(L.strip_comments(FEAT["a.cs"]))
    check("a [HarmonyPatch] inside a doc comment is never a target (once comments are stripped)",
          len(clean) == 4 and len(raw) >= len(clean), (len(raw), len(clean)))
    check("strip_comments keeps line numbers and string literals",
          L.strip_comments('a // x\n"// y" /* z\n */ b').count("\n") == 2
          and '"// y"' in L.strip_comments('"// y" // gone'), None)


def part2():
    dll = os.path.join(L.GAME_MANAGED, "Assembly-CSharp.dll")
    if not os.path.exists(dll):
        print("UNMEASURED  part 2: %s not reachable from here" % dll)
        return
    try:
        import dnfile  # noqa: F401
    except ImportError:
        print("UNMEASURED  part 2: python module dnfile is not installed")
        return
    idx = L.load_index([dll])
    real = '[HarmonyPatch(typeof(Fire), nameof(Fire.SpawnSetup))]\npublic static class A { }\n'
    bad = real.replace("Fire.SpawnSetup", "Fire.SpawnSetupX")
    u = {"Verse", "RimWorld", "HarmonyLib"}
    t_ok = L.scan_text(real)[0]
    t_bad = L.scan_text(bad)[0]
    check("sanity probe: the real index resolves Fire.SpawnSetup", L.judge(idx, t_ok, u)[0] == "OK", L.judge(idx, t_ok, u))
    check("mutated Fire.SpawnSetupX comes back MISSING_MEMBER", L.judge(idx, t_bad, u)[0] == "MISSING_MEMBER",
          L.judge(idx, t_bad, u))
    out = io.StringIO()
    rows, code = L.run(L.REPO, "FlowWorks", index=L.load_index(L.default_dlls(L.REPO)), out=out)
    attrs = [r for r in rows if r[1]["kind"] in ("attr", "dynamic")]
    check("FlowWorks: at least 28 patch targets read (sanity: a scan that finds none proves nothing)", len(attrs) >= 28,
          len(attrs))
    check("FlowWorks lint is clean", code == 0, out.getvalue()[-400:])
    # mutation on the real tree, in memory: strip one [PatchFeature] from FlowWorks and it must come back NO_FEATURE
    texts = {}
    for p in L.source_files(L.REPO, "FlowWorks"):
        texts[p] = L.strip_comments(open(p, encoding="utf-8").read())
    check("FlowWorks: every patch class carries a valid [PatchFeature]", L.feature_findings(texts) == [],
          L.feature_findings(texts)[:3])
    victim = next(p for p, t in texts.items() if "PatchFeature(" in t)
    import re as _re
    texts[victim] = _re.sub(r"\[RimMandrake\.Shared\.PatchFeature\([^\]]*\)\]", "", texts[victim], count=1)
    check("FlowWorks with one [PatchFeature] removed comes back NO_FEATURE",
          [v for v, _, _ in L.feature_findings(texts)] == ["NO_FEATURE"], L.feature_findings(texts))


if __name__ == "__main__":
    part1()
    part1b()
    part2()
    print("%s: %d failure(s)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    sys.exit(1 if FAILS else 0)
