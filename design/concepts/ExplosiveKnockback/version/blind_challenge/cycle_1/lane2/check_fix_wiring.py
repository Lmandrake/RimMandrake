#!/usr/bin/env python3
"""Static wiring check for the two Problems blind cycle 1 fixed (lane2/faults.json). Red on the code before the fix.
    python3 check_fix_wiring.py            exit 0 = every check holds
RIMMANDRAKE_FLING_GOODS_WILD_FACTOR_NEVER_SHIPPED: goods and corpses are thrown by RM_KnockbackMath.WildCells with the
  GoodsThrowWild constant (1.6; a Mod Setting would need locked scene text changed: written up), both where the throw is made (Execute) and where the blast decides
  whether a stack will be thrown (ItemWillBeThrown); pawns and containers keep the plain kernel.
RIMMANDRAKE_UNCOUPLE_GAS_GOODS_CAP_FROM_WEAPON_SCALE: the gas burst's config sets scaleOwnCap = false and the kernel's
  Apply honours it. The kernel arithmetic itself is lane 1 (L1_goods_fly_wild, L1_gas_goods_cap_ignores_weapon_scale)."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
SRC = os.environ.get("EK_SRC") or os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback/Source")
read = lambda f: open(os.path.join(SRC, f), encoding="utf-8").read()
comp, mod, math = read("RM_MapComponent_Knockback.cs"), read("RM_KnockbackMod.cs"), read("RM_KnockbackMath.cs")

def body(text, signature):
    i = text.find(signature)
    if i < 0:
        return ""
    j = text.index("{", i); depth = 0
    for k in range(j, len(text)):
        depth += {"{": 1, "}": -1}.get(text[k], 0)
        if depth == 0:
            return text[j:k + 1]
    return ""

execute, will, gas, cont = body(comp, "private bool Execute("), body(comp, "ItemWillBeThrown("), body(comp, "public static void GasBurst("), body(comp, "private bool ThrowContainer(")
checks = [
    ("kernel has WildCells", "public static int WildCells(" in math),
    ("Execute throws goods by WildCells with GoodsThrowWild", re.search(r"WildCells\([^;]*GoodsThrowWild", execute) is not None),
    ("Execute keeps the plain kernel for pawns", re.search(r"kind == KbKind\.Pawn\s*\?\s*kernelCells", execute) is not None),
    ("Execute journals kernel and wild cells", '"kernelCells"' in execute and '"wildCells"' in execute),
    ("ItemWillBeThrown decides by WildCells", re.search(r"WildCells\([^;]*GoodsThrowWild", will) is not None),
    ("a container is not thrown wild", "WildCells" not in cont and cont != ""),
    ("GoodsThrowWild ships at 1.6", re.search(r"public const float GoodsThrowWild = 1\.6f;", mod) is not None),
    # the plans moved into RM_KnockbackVerdicts.GoodCells (RIMMANDRAKE_LIFT_PROOF_VERDICTS_INTO_TESTED_CODE_NINE_SLIPPED)
    ("the proof's goods expectations fly wild", read("RM_KnockbackProof.cs").count("WildCells(")
     + len(re.findall(r"RM_KnockbackVerdicts\.GoodCells\([^;]*GoodsThrowWild\)", read("RM_KnockbackProof.cs"))) >= 3
     and "RM_KnockbackMath.WildCells(dist, radius, 1f, mass, k, wild)" in read("RM_KnockbackVerdicts.cs")),
    ("KbConfig has scaleOwnCap", re.search(r"public bool scaleOwnCap = true;", math) is not None),
    ("Apply honours scaleOwnCap", re.search(r"scaleOwnCap \? ownCapScale : 1f", math) is not None),
    ("GasBurst sets scaleOwnCap = false", "scaleOwnCap = false" in gas),
]
bad = [n for n, ok in checks if not ok]
for n, ok in checks:
    print(("ok   " if ok else "FAIL ") + n)
print("blind cycle 1 fix wiring: %d/%d %s" % (len(checks) - len(bad), len(checks), "PASS" if not bad else "FAIL"))
sys.exit(1 if bad else 0)
