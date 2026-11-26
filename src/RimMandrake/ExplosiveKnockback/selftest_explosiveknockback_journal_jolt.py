#!/usr/bin/env python3
"""Offline checks of Explosive Knockback's journal lines and drawn jolt (blind cycle 2; steward's decisions 4, 6 and 7).

1. item_move: every goods move line carries kernelCells (the person kernel's throw) and wildCells (the cells it flew), so the
   live scenes can read both off the move line; kernelCells comes from ThrowCells, the goods' cells from WildCells x GoodsThrowWild.
2. container: ThrowContainer plans its throw with the kernel's ContainerThrowCells (the dead slide kernel ContainerShove / KbShove
   is gone from Source/), and a container that does not fly is drawn jolting: StartJolt on the jolt path, MapComponentUpdate
   draws each jolt through RM_KnockbackMath.JoltOffset (the bound is kernel-tested, K-14), StartJolt keeps at most MaxJolts.
3. flying goods off: Execute skips goods with reason flying_off before any move.
4. the rim (inv_too_weak_skip, every_good_moves' "reached"): a thing whose KERNEL throw rounds to 0 is skipped too_weak, goods
   included, so a rim good never flies one cell on its wild factor alone (Execute and the prefix's ItemWillBeThrown agree).
5. wiring the offline deciders could not see (blind cycle 2's planted faults): GoodsThrowWild is the sheet's 1.6; a gas burst's
   goods cap is exact (scaleOwnCap false); every proof goods expectation plans through RM_KnockbackVerdicts.GoodCells with GoodsThrowWild; every validation.py scene is a proof
   SceneName; the Stage-3 sweep's closedGuard and fireHalf lanes read their own observation; storeroom_pit_proof.py reads the
   player's settings before its first reset and puts them back in its finally.
Since ffc3937ee7 the throw rules of 1, 2 (the plan half), 3 and 4 are read in RM_KnockbackPlan.cs (KbPlanner), and the map
component is checked to hand that plan RimMandrakeExplosiveKnockbackSettings.Rules().
Each check is shown to fail on a planted break of the source it reads.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_journal_jolt.py [--source DIR]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SELFTEST_MARK = "\n// ---- Source/SelfTest ----\n"   # load() puts the mod's sources before it, the SelfTest's after


def body(src, head):
    """The text of the method whose signature starts with `head`, to its closing brace at 8 spaces."""
    i = src.find(head)
    if i < 0:
        return ""
    j = src.find("\n        }\n", i)
    return src[i:j if j > 0 else len(src)]


def checks(mc, math_cs, all_src, plan):
    """`plan` is RM_KnockbackPlan.cs: since ffc3937ee7 the throw rules live in that Verse-free plan (KbPlanner), and the map
    component hands it the facts and RimMandrakeExplosiveKnockbackSettings.Rules() (wiring() checks Rules())."""
    f = []
    moves = re.findall(r'RM_KnockbackJournal\.Add\("item_move",(.*?)\);', mc, re.S)
    if len(moves) < 2:
        f.append("item_move: %d journal calls found, want the flying and the instant line" % len(moves))
    for n, m in enumerate(moves, 1):
        if not re.search(r'"kernelCells",\s*kernelCells\b', m) or not re.search(r'"wildCells",\s*cells\b', m):
            f.append("item_move line %d lacks kernelCells/wildCells" % n)
    if not re.search(r"p\.kernelCells = RM_KnockbackMath\.ThrowCells\(", plan):
        f.append("kernelCells is not the kernel's ThrowCells")
    if not re.search(r"p\.cells = pawn \? p\.kernelCells\s*:\s*RM_KnockbackMath\.WildCells\([^;]*q\.wild\)", plan):
        f.append("goods' cells are not WildCells x the rules' wild factor (people the kernel)")
    tc = body(mc, "private bool ThrowContainer(")
    if "KbPlanner.Decide(" not in tc or "RM_KnockbackMath.ContainerThrowCells(" not in body(plan, "private static KbPlan Container("):
        f.append("ThrowContainer does not plan with ContainerThrowCells")
    if re.search(r"\bContainerShove\b|\bKbShove\b", all_src):
        f.append("the dead slide kernel (ContainerShove / KbShove) is still in Source/")
    if not re.search(r"if \(!flew\)\s*\{[^}]*StartJolt\(b,", tc, re.S):
        f.append("a container that does not fly is not drawn jolting (no StartJolt on the jolt path)")
    up = body(mc, "public override void MapComponentUpdate(")
    if "RM_KnockbackMath.JoltOffset(" not in up or ".Draw(" not in up:
        f.append("MapComponentUpdate does not draw the jolt through JoltOffset")
    sj = body(mc, "private void StartJolt(")
    if not re.search(r"Count >= MaxJolts", sj):
        f.append("StartJolt is not bounded by MaxJolts")
    m = re.search(r"public const int JoltTicks = (\d+);", mc)
    a = re.search(r"public const float JoltAmplitude = ([\d.]+)f;", mc)
    k = re.search(r"public const int MaxJolts = (\d+);", mc)
    if not (m and 0 < int(m.group(1)) <= 120):
        f.append("JoltTicks missing or not 1..120")
    if not (a and 0 < float(a.group(1)) <= 0.5):
        f.append("JoltAmplitude missing or not in (0, 0.5] cells")
    if not (k and 0 < int(k.group(1)) <= 256):
        f.append("MaxJolts missing or not 1..256")
    if "public static void JoltOffset(" not in math_cs:
        f.append("RM_KnockbackMath.JoltOffset is missing")
    if not re.search(r'if \(!pawn && !q\.flyingGoods\)\s*\{\s*return Skip\(p, "flying_off"\);', plan):
        f.append("flying goods off does not skip goods with reason flying_off")
    if not re.search(r'if \(p\.kernelCells <= 0 \|\| p\.cells <= 0\)\s*\{\s*return Skip\(p, "too_weak"\);', plan):
        f.append("the rim: a good whose kernel throw is 0 is not skipped too_weak in Execute")
    iw = body(mc, "public static bool ItemWillBeThrown(")
    gw = body(plan, "public static bool GoodWillBeThrown(")
    if ("KbPlanner.GoodWillBeThrown(f, blast, RimMandrakeExplosiveKnockbackSettings.Rules()," not in iw
            or not re.search(r"RM_KnockbackMath\.ThrowCells\(dist, b\.radius, b\.force, f\.mass, s\) > 0\s*&&", gw)):
        f.append("the rim: ItemWillBeThrown does not require a kernel throw of a cell")
    # the proof's goods plans go through RM_KnockbackVerdicts.GoodCells (kernel-tested, V-02) with the real wild factor
    # (RIMMANDRAKE_LIFT_PROOF_VERDICTS_INTO_TESTED_CODE_NINE_SLIPPED: a plan passing 1f there is the plain kernel again)
    src = all_src.split(SELFTEST_MARK)[0]
    calls = list(re.finditer(r"RM_KnockbackVerdicts\.GoodCells\(([^;]*)\);", src))
    if len(calls) < 4:
        f.append("proof goods plans: %d RM_KnockbackVerdicts.GoodCells calls, want WantCells, WantCellsFrom, the items want and PlanGood" % len(calls))
    for m in calls:
        last = m.group(1).split(",")[-1].strip()
        if last == "RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild":
            continue
        # a local that holds GoodsThrowWild (WantCells keeps it to print it, bedd128cf7): its last declaration before the call,
        # within the method, is the constant, and nothing assigns it again before the call
        decl = list(re.finditer(r"\b(?:float|var)\s+%s\s*=\s*([^;]+);" % re.escape(last), src[:m.start()])) if re.fullmatch(r"\w+", last) else []
        if decl and decl[-1].group(1).strip() == "RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild" and m.start() - decl[-1].end() < 600 \
                and not re.search(r"\b%s\s*=(?!=)" % re.escape(last), src[decl[-1].end():m.start()]):
            continue
        f.append("a proof goods plan passes %r, not GoodsThrowWild, as the wild factor" % last)
    return f


def wiring(mod, mc, proof, three, val, store):
    f = []
    if not re.search(r"public const float GoodsThrowWild = 1\.6f;", mod):
        f.append("GoodsThrowWild is not the sheet's 1.6")
    rules = body(mod, "public static KbRules Rules(")
    if not re.search(r"\bwild = GoodsThrowWild\b", rules) or not re.search(r"\bflyingGoods = flyingGoods\b", rules):
        f.append("Rules() does not hand the plan GoodsThrowWild and the flyingGoods switch")
    if not re.search(r'source = "gas",\s*scaleOwnCap = false \}', mc):
        f.append("the gas burst's goods cap is rescaled (scaleOwnCap not false)")
    if re.search(r"lightMassLimit \? 0 : RM_KnockbackMath\.(ThrowCells|WildCells)\(", proof):
        f.append("a proof goods expectation plans inline (the plain kernel or an untested copy), not through RM_KnockbackVerdicts.GoodCells")
    names = re.search(r"SceneNames\s*=\s*\{(.*?)\};", proof, re.S)
    listed = set(re.findall(r'"(\w+)"', names.group(1))) if names else set()
    want = set(re.findall(r'^\s*\("(\w+)", "\w+", "\w+",', val, re.M))
    if not want or want - listed:
        f.append("validation.py scenes missing from SceneNames: %s" % sorted(want - listed)[:5])
    if not re.search(r'case "closedGuard": own = obs\["lockerGoods"\] == "lost";', three):
        f.append("the closedGuard lane does not read lockerGoods")
    if not re.search(r"ConfigOf\(null, DamageDefOf\.Flame\)\.force;\s*own = ff <= 0f;", three):
        f.append("the fireHalf lane does not read the Flame force")
    i, j = store.find("PLAYER = player_settings()"), store.find('arm("A", [])')
    fin = store[store.find("finally:", max(i, 0)):]
    if not (0 <= i < j) or "unset = restore_player_settings(PLAYER)" not in fin:
        f.append("storeroom_pit_proof.py does not snapshot the player's settings first and restore them in its finally")
    return f


def load(src_dir):
    rd = lambda n: open(os.path.join(src_dir, n), encoding="utf-8").read()
    mc, km, plan = rd("RM_MapComponent_Knockback.cs"), rd("RM_KnockbackMath.cs"), rd("RM_KnockbackPlan.cs")
    every = "".join(open(os.path.join(src_dir, n), encoding="utf-8").read() for n in sorted(os.listdir(src_dir)) if n.endswith(".cs"))
    every += SELFTEST_MARK + "".join(open(os.path.join(src_dir, "SelfTest", n), encoding="utf-8").read()
                     for n in sorted(os.listdir(os.path.join(src_dir, "SelfTest"))) if n.endswith(".cs")) if os.path.isdir(os.path.join(src_dir, "SelfTest")) else ""
    return mc, km, every, plan


def main(argv):
    src_dir = argv[argv.index("--source") + 1] if "--source" in argv else os.path.join(HERE, "Source")
    mc, km, every, plan = load(src_dir)
    faults = checks(mc, km, every, plan)
    rd = lambda *p: open(os.path.join(src_dir, *p), encoding="utf-8").read()
    mod, proof, three = rd("RM_KnockbackMod.cs"), rd("RM_KnockbackProof.cs"), rd("RM_KnockbackProof_StageThree.cs")
    val = open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()
    store = open(os.path.join(HERE, "proof", "storeroom_pit_proof.py"), encoding="utf-8").read()
    W = (mod, mc, proof, three, val, store)
    faults += wiring(*W)
    for x in faults:
        print("FAIL", x)
    P = lambda old, new: (mc, km, every, plan.replace(old, new, 1))
    planted = {
        "wildCells dropped from a move line": (mc.replace('"kernelCells", kernelCells, "wildCells", cells,', '"kernelCells", kernelCells,', 1), km, every, plan),
        "goods thrown by the plain kernel": P("RM_KnockbackMath.WildCells(p.dist, b.radius, b.force, f.mass, s, q.wild);", "RM_KnockbackMath.WildCells(p.dist, b.radius, b.force, f.mass, s, 1f);"),
        "the jolt not drawn": (mc.replace("StartJolt(b, p.dx, p.dz);", "", 1), km, every, plan),
        "jolts unbounded": (mc.replace("Count >= MaxJolts", "Count >= int.MaxValue", 1), km, every, plan),
        "the dead shove back": (mc, km, every + " public static KbShove ContainerShove(", plan),
        "container planned without the kernel": P("RM_KnockbackMath.ContainerThrowCells(f.oneByOne,", "ThrowCellsLocal(f.oneByOne,"),
        "container not planned at all": (mc.replace("KbPlan p = KbPlanner.Decide(f, BlastOf(r), RimMandrakeExplosiveKnockbackSettings.Rules(), s, new RM_MapKbWorld(map, b));",
                                                    "KbPlan p = LocalPlan(f);", 1), km, every, plan),
        "flying off falls through": P('return Skip(p, "flying_off");', 'return Skip(p, "flying");'),
        "rim good flies on wild alone": P("if (p.kernelCells <= 0 || p.cells <= 0)", "if (p.cells <= 0)"),
        "item prediction skips the kernel": P("return RM_KnockbackMath.ThrowCells(dist, b.radius, b.force, f.mass, s) > 0\n                && ", "return "),
        "item prediction on default rules": (mc.replace("KbPlanner.GoodWillBeThrown(f, blast, RimMandrakeExplosiveKnockbackSettings.Rules(),", "KbPlanner.GoodWillBeThrown(f, blast, new KbRules(),", 1), km, every, plan),
        "proof plan wild 1": (mc, km, every.replace("mass, k, RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild);\n            if (cells <= 0)", "mass, k, 1f);\n            if (cells <= 0)", 1), plan),
        "WantCells' local wild 1": (mc, km, every.replace("float wild = RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild;", "float wild = 1f;", 1), plan),
        "WantCells' local wild reassigned": (mc, km, every.replace("float wild = RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild;", "float wild = RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild; wild = 1f;", 1), plan),
    }
    base = (mc, km, every, plan)
    missed = [n for n, x in planted.items() if x == base or not checks(*x)]
    def w(i, old, new):
        x = list(W); x[i] = x[i].replace(old, new, 1); return tuple(x)
    wired = {
        "wild constant 1.0": w(0, "GoodsThrowWild = 1.6f;", "GoodsThrowWild = 1.0f;"),
        "Rules() hands the plan wild 1": w(0, "wild = GoodsThrowWild,", "wild = 1f,"),
        "Rules() drops the flying-goods switch": w(0, "flyingGoods = flyingGoods,", "flyingGoods = true,"),
        "gas cap rescaled": w(1, "scaleOwnCap = false };", "scaleOwnCap = true };"),
        "goods want by the plain kernel": w(2, "int want = RM_KnockbackVerdicts.GoodCells((sc.starts[key] - sc.o).LengthHorizontal, 2.9f, mass, k, RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild);",
                                            "int want = mass > k.lightMassLimit ? 0 : RM_KnockbackMath.ThrowCells((sc.starts[key] - sc.o).LengthHorizontal, 2.9f, 1f, mass, k);"),
        "a scene name dropped": w(2, '"goods_fly_rebound", "goods_fly_off",', '"goods_fly_rebound",'),
        "closedGuard lane always own": w(3, 'own = obs["lockerGoods"] == "lost";', "own = true;"),
        "fireHalf lane always own": w(3, "own = ff <= 0f;", "own = true;"),
        "storeroom restore dropped": w(5, "        unset = restore_player_settings(PLAYER)", "        unset = []"),
    }
    for n, x in wired.items():
        if x == W or not wiring(*x):
            missed.append(n)
    planted.update(wired)
    for n in missed:
        print("FAIL planted break NOT CAUGHT:", n)
    ok = not faults and not missed
    print("explosive knockback journal and jolt: %s (%d faults, %d/%d planted breaks caught)"
          % ("PASS" if ok else "FAIL", len(faults), len(planted) - len(missed), len(planted)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
