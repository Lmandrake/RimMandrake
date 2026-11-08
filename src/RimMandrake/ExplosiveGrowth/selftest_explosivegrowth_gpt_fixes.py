#!/usr/bin/env python3
"""Source pins for the ExplosiveGrowth fixes from the GPT edge-case consult
(design/RimMandrake/gpt_consults/ExplosiveGrowth_edge_cases_2026-10-16.md). Each check names its rimflow item; each
fails on the pre-fix source (control run by reverting the line by hand, 2026-10-16).

    python3 src/RimMandrake/ExplosiveGrowth/selftest_explosivegrowth_gpt_fixes.py
"""
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source")
fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def read(rel):
    with open(os.path.join(SRC, rel), encoding="utf-8") as f:
        return f.read()


def method_body(src, signature):
    i = src.find(signature)
    if i < 0:
        return ""
    j = src.find("{", i)
    depth, k = 0, j
    while k < len(src):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j:k + 1]
        k += 1
    return ""


def code_only(src):
    """C# with // and /* */ comments removed (string and char literals kept), whitespace collapsed, so a pin
    matches statements the compiler sees, never a commented-out line."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c in "\"'":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            out.append(src[i:j + 1])
            i = j + 1
        elif src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            out.append(" ")
            i = n if j < 0 else j + 2
        else:
            out.append(c)
            i += 1
    return re.sub(r"\s+", " ", "".join(out))


def main():
    mc = read("RM_MapComponent_ExplosiveGrowth.cs")
    expose = method_body(mc, "public override void ExposeData()")
    check("sanity: map component ExposeData found", "Scribe_Collections.Look(ref ruptures" in expose)
    # EGROWTH_RELOAD_FIX_FREE_CHARGE_PASS
    for f in ("nextPassTick", "lastPassTick"):
        check("EGROWTH_RELOAD_FIX_FREE_CHARGE_PASS: %s scribed with default -1" % f,
              re.search(r'Scribe_Values\.Look\(ref %s, "%s", -1\);' % (f, f), expose) is not None)
    # EGROWTH_RUPTURE_FIX_ROLLS_TWICE: clouds tick before the charge pass that may fire (and pulse) a new rupture
    body = method_body(mc, "private void Pass(int now)")
    scope_end = body.find("RM_SoakSources.Pulse(this, now);")
    tick_at = body.find("TickRuptures(now)", scope_end)
    check("sanity: Pass body has the in-scope rupture tick", scope_end > 0 and tick_at > 0)
    tick = method_body(mc, "public override void MapComponentTick()")
    check("EGROWTH_RUPTURE_FIX_ROLLS_TWICE: ruptures tick (Pass) before the plants are stepped",
          0 < tick.find("Pass(now)") < tick.find("StepPlants(now)"), (tick.find("Pass(now)"), tick.find("StepPlants(now)")))
    tr = read("RM_TopResolver.cs")
    check("sanity: Rupture still pulses its new cloud once itself", "RuptureExposurePulse(map, new RM_RuptureZone" in tr)
    # EGROWTH_BLOOMBURST_FIX_STALE_FOOTPRINT
    check("EGROWTH_BLOOMBURST_FIX_STALE_FOOTPRINT: SoakedCells yields live soaks only",
          re.search(r"SoakedCells\s*=>\s*ledger\.soakUntil\.Keys\.Where\(IsSoaked\)", mc) is not None)
    # EGROWTH_SOAK_FIX_DURATION_INT_WRAP (behaviour is fuzzed in SelfTest/ExplosiveGrowthFuzz.cs scope family)
    k = read(os.path.join("Kernel", "RM_ExplosiveGrowthKernel.cs"))
    check("EGROWTH_SOAK_FIX_DURATION_INT_WRAP: no raw now + ticks deadline left",
          re.search(r"int until = now \+", k) is None and k.count("Deadline(now, ticks)") == 2)
    # EGROWTH_BURST_FIX_NEVERDOWNS_AVERAGES (behaviour is fuzzed in SelfTest/ExplosiveGrowthFuzz.cs burst family)
    hurt = method_body(tr, "private static void HurtPawnsNear(")
    check("sanity: HurtPawnsNear found", "TakeDamage" in hurt)
    check("EGROWTH_BURST_FIX_NEVERDOWNS_AVERAGES: no summary-health guard left", "SummaryHealthPercent" not in hurt)
    check("EGROWTH_BURST_FIX_NEVERDOWNS_AVERAGES: the hit names its part and its capped amount",
          re.search(r"new DamageInfo\(DamageDefOf\.Blunt, amount, hitPart: part\)", hurt) is not None
          and "amount = BurstHitAmount(p, part, amount);" in hurt and "if (amount > 0f)" in hurt)
    pick = method_body(tr, "public static BodyPartRecord BurstHitPart(Pawn p)")
    check("EGROWTH_BURST_FIX_NEVERDOWNS_AVERAGES: part is an Outside leaf, no vital or spared tag",
          "BodyPartDepth.Outside" in pick and "r.parts.Count == 0" in pick and "t.vital" in pick and "BurstSparedTags" in pick)
    for tag in ("ConsciousnessSource", "MovingLimbDigit", "BloodPumpingSource", "BreathingSource"):
        check("EGROWTH_BURST_FIX_NEVERDOWNS_AVERAGES: %s spared" % tag, '"%s"' % tag in tr)
    m = re.search(r"public const float BurstPartReserve = ([0-9.]+)f;", k)
    check("EGROWTH_BURST_FIX_NEVERDOWNS_AVERAGES: part reserve is at least 1 hp (never destroyed)",
          m is not None and float(m.group(1)) >= 1.0, m and m.group(1))
    check("EGROWTH_BURST_FIX_NEVERDOWNS_AVERAGES: amount is capped by part health less the reserve",
          "(partHealth - BurstPartReserve) / damageFactor" in method_body(k, "public static float BurstHitAmount(float rolled"))
    check("EGROWTH_BURST_FIX_NEVERDOWNS_AVERAGES: cap delegates to the fuzzed kernel",
          "RM_ExplosiveGrowthKernel.BurstHitAmount(" in method_body(tr, "public static float BurstHitAmount(Pawn p")
          and "public static float BurstHitAmount(float rolled" in k)
    mcs = read("RM_MapComponent_ExplosiveGrowth.cs")
    upd = method_body(mcs, "public override void MapComponentUpdate()")
    pat = read("RM_ExplosiveGrowthPatches.cs")
    check("sanity: Print reads maxOvergrowthScale via VisualScaleFor, Graphic reads hueShiftEnabled",
          "comp.VisualScaleFor(__instance)" in pat and "ExplosiveGrowthSettings.hueShiftEnabled" in pat
          and "ExplosiveGrowthSettings.maxOvergrowthScale" in method_body(mcs, "public float VisualScaleFor(Plant plant)"))
    check("EGROWTH_DISABLE_FIX_BLOATED_PLANTS_STAY: a per-frame look check exists", bool(upd))
    for key in ("ExplosiveGrowthSettings.On", "ExplosiveGrowthSettings.hueShiftEnabled",
                "ExplosiveGrowthSettings.maxOvergrowthScale"):
        check("EGROWTH_DISABLE_FIX_BLOATED_PLANTS_STAY: the look check reads %s" % key, key in upd)
    check("EGROWTH_DISABLE_FIX_BLOATED_PLANTS_STAY: a changed look remeshes Things on the whole map",
          "map.mapDrawer.WholeMapChanged(MapMeshFlagDefOf.Things);" in upd
          and re.search(r"if \(lookKnown && \(on != lookOn \|\| hue != lookHue \|\| scale != lookScale\)\)", upd) is not None)
    check("EGROWTH_DISABLE_FIX_BLOATED_PLANTS_STAY: the last look is recorded every frame",
          all(x in upd for x in ("lookKnown = true;", "lookOn = on;", "lookHue = hue;", "lookScale = scale;")))
    pas = method_body(mcs, "private void Pass(int now)")
    cl = pas.find("ledger.charges.Clear();")
    check("EGROWTH_DISABLE_FIX_BLOATED_PLANTS_STAY: out-of-scope dropped charges are dirtied before the clear",
          cl > 0 and "foreach (IntVec3 c in ledger.charges.Keys) Dirty(c);" in pas[:cl])
    # The pins above are text; these match comment-stripped code, so a remesh or Dirty commented out, emptied
    # or moved out of its branch goes red (blind-check mutant 2026-11-02: '{ } // map.mapDrawer.WholeMapChanged(...)').
    updc = code_only(upd)
    check("sanity: code_only strips comments and keeps code",
          code_only("a(); // b();\n/* c(); */ d(\"//x\");") == "a(); d(\"//x\");", code_only("a(); // b();\n/* c(); */ d(\"//x\");"))
    check("EGROWTH_DISABLE_FIX_BLOATED_PLANTS_STAY: (code) the look-change branch's body is the Things remesh",
          re.search(r"if \(lookKnown && \(on != lookOn \|\| hue != lookHue \|\| scale != lookScale\)\) "
                    r"(\{ )?map\.mapDrawer\.WholeMapChanged\(MapMeshFlagDefOf\.Things\);", updc) is not None, updc)
    check("EGROWTH_DISABLE_FIX_BLOATED_PLANTS_STAY: (code) the look reads the three live settings",
          all(x in updc for x in ("bool on = ExplosiveGrowthSettings.On;", "bool hue = ExplosiveGrowthSettings.hueShiftEnabled;",
                                  "float scale = ExplosiveGrowthSettings.maxOvergrowthScale;")), updc)
    check("EGROWTH_DISABLE_FIX_BLOATED_PLANTS_STAY: (code) the last look is recorded after the check, unconditionally",
          re.search(r"WholeMapChanged\(MapMeshFlagDefOf\.Things\); (\} )?lookKnown = true; lookOn = on; lookHue = hue; "
                    r"lookScale = scale; \}$", updc) is not None, updc)
    pasc = code_only(pas)
    check("EGROWTH_DISABLE_FIX_BLOATED_PLANTS_STAY: (code) dropped charges are dirtied right before the clear",
          "foreach (IntVec3 c in ledger.charges.Keys) Dirty(c); ledger.charges.Clear();" in pasc)
    if fails:
        print("FAIL: %d failed" % len(fails))
        return 1
    print("PASS: 0 failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
