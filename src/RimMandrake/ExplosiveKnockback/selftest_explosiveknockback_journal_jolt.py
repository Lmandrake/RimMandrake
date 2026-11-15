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
   goods cap is exact (scaleOwnCap false); every proof goods expectation uses WildCells; every validation.py scene is a proof
   SceneName; the Stage-3 sweep's closedGuard and fireHalf lanes read their own observation; storeroom_pit_proof.py reads the
   player's settings before its first reset and puts them back in its finally.
Each check is shown to fail on a planted break of the source it reads.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_journal_jolt.py [--source DIR]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def body(src, head):
    """The text of the method whose signature starts with `head`, to its closing brace at 8 spaces."""
    i = src.find(head)
    if i < 0:
        return ""
    j = src.find("\n        }\n", i)
    return src[i:j if j > 0 else len(src)]


def checks(mc, math_cs, all_src):
    f = []
    moves = re.findall(r'RM_KnockbackJournal\.Add\("item_move",(.*?)\);', mc, re.S)
    if len(moves) < 2:
        f.append("item_move: %d journal calls found, want the flying and the instant line" % len(moves))
    for n, m in enumerate(moves, 1):
        if not re.search(r'"kernelCells",\s*kernelCells\b', m) or not re.search(r'"wildCells",\s*cells\b', m):
            f.append("item_move line %d lacks kernelCells/wildCells" % n)
    if not re.search(r"int kernelCells = RM_KnockbackMath\.ThrowCells\(", mc):
        f.append("kernelCells is not the kernel's ThrowCells")
    if not re.search(r"kind == KbKind\.Pawn \? kernelCells\s*:\s*RM_KnockbackMath\.WildCells\([^;]*GoodsThrowWild\)", mc):
        f.append("goods' cells are not WildCells x GoodsThrowWild (people the kernel)")
    tc = body(mc, "private bool ThrowContainer(")
    if "RM_KnockbackMath.ContainerThrowCells(" not in tc:
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
    if not re.search(r'if \(kind != KbKind\.Pawn && !RimMandrakeExplosiveKnockbackSettings\.flyingGoods\)\s*\{\s*RM_KnockbackJournal\.Add\("skip"[^;]*"flying_off"', mc):
        f.append("flying goods off does not skip goods with reason flying_off")
    if not re.search(r"if \(kernelCells <= 0 \|\| cells <= 0\)\s*\{\s*RM_KnockbackJournal\.Add\(\"skip\"[^;]*\"too_weak\"", mc):
        f.append("the rim: a good whose kernel throw is 0 is not skipped too_weak in Execute")
    iw = body(mc, "public static bool ItemWillBeThrown(")
    if not re.search(r"RM_KnockbackMath\.ThrowCells\(dist, explosion\.radius, cfg\.force, mass, s\) > 0\s*&&", iw):
        f.append("the rim: ItemWillBeThrown does not require a kernel throw of a cell")
    return f


def wiring(mod, mc, proof, three, val, store):
    f = []
    if not re.search(r"public const float GoodsThrowWild = 1\.6f;", mod):
        f.append("GoodsThrowWild is not the sheet's 1.6")
    if not re.search(r'source = "gas",\s*scaleOwnCap = false \}', mc):
        f.append("the gas burst's goods cap is rescaled (scaleOwnCap not false)")
    if re.search(r"lightMassLimit \? 0 : RM_KnockbackMath\.ThrowCells\(", proof):
        f.append("a proof goods expectation uses the plain kernel, not WildCells")
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
    mc, km = rd("RM_MapComponent_Knockback.cs"), rd("RM_KnockbackMath.cs")
    every = "".join(open(os.path.join(src_dir, n), encoding="utf-8").read() for n in sorted(os.listdir(src_dir)) if n.endswith(".cs"))
    every += "".join(open(os.path.join(src_dir, "SelfTest", n), encoding="utf-8").read()
                     for n in sorted(os.listdir(os.path.join(src_dir, "SelfTest"))) if n.endswith(".cs")) if os.path.isdir(os.path.join(src_dir, "SelfTest")) else ""
    return mc, km, every


def main(argv):
    src_dir = argv[argv.index("--source") + 1] if "--source" in argv else os.path.join(HERE, "Source")
    mc, km, every = load(src_dir)
    faults = checks(mc, km, every)
    rd = lambda *p: open(os.path.join(src_dir, *p), encoding="utf-8").read()
    mod, proof, three = rd("RM_KnockbackMod.cs"), rd("RM_KnockbackProof.cs"), rd("RM_KnockbackProof_StageThree.cs")
    val = open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()
    store = open(os.path.join(HERE, "proof", "storeroom_pit_proof.py"), encoding="utf-8").read()
    W = (mod, mc, proof, three, val, store)
    faults += wiring(*W)
    for x in faults:
        print("FAIL", x)
    planted = {
        "wildCells dropped from a move line": (mc.replace('"kernelCells", kernelCells, "wildCells", cells,', '"kernelCells", kernelCells,', 1), km, every),
        "goods thrown by the plain kernel": (mc.replace("RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild);\n            // the rim", "1f);\n            // the rim", 1), km, every),
        "the jolt not drawn": (mc.replace("StartJolt(b, dx, dz);", "", 1), km, every),
        "jolts unbounded": (mc.replace("Count >= MaxJolts", "Count >= int.MaxValue", 1), km, every),
        "the dead shove back": (mc, km, every + " public static KbShove ContainerShove("),
        "container planned without the kernel": (mc.replace("RM_KnockbackMath.ContainerThrowCells(one,", "ThrowCellsLocal(one,", 1), km, every),
        "flying off falls through": (mc.replace('"reason", "flying_off"', '"reason", "flying"', 1), km, every),
        "rim good flies on wild alone": (mc.replace("if (kernelCells <= 0 || cells <= 0)", "if (cells <= 0)", 1), km, every),
    }
    missed = [n for n, (a, b, c) in planted.items() if (a, b, c) == (mc, km, every) or not checks(a, b, c)]
    def w(i, old, new):
        x = list(W); x[i] = x[i].replace(old, new, 1); return tuple(x)
    wired = {
        "wild constant 1.0": w(0, "GoodsThrowWild = 1.6f;", "GoodsThrowWild = 1.0f;"),
        "gas cap rescaled": w(1, "scaleOwnCap = false };", "scaleOwnCap = true };"),
        "goods want by the plain kernel": w(2, "int want = mass > k.lightMassLimit ? 0 : RM_KnockbackMath.WildCells((sc.starts[key] - sc.o).LengthHorizontal, 2.9f, 1f, mass, k, RimMandrakeExplosiveKnockbackSettings.GoodsThrowWild);",
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
