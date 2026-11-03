#!/usr/bin/env python3
"""EGROWTH_BURST_FIX_NEVERDOWNS_AVERAGES: the Burst's hit cap, executed WITHOUT dotnet.

The kernel's `BurstHitAmount(float rolled, ...)` body is read from source, comment-stripped and transliterated to
Python (it is straight-line float arithmetic: if/return, Math.Min, IsNaN/IsInfinity), then swept against bounds written
here as LITERALS, never the kernel's own constants:
  * a hit never leaves its part under 1 hp:      a*df < hp  and  hp - a*df >= 1
  * a hit never exceeds the roll, never under 1:   0 or 1 <= a <= rolled
  * a hit adds at most 0.05 pain and stays 0.10 under the pain-shock line
  * a pawn with Consciousness or Moving within 0.15 of min-for-capable is never hit
Then the same sweep is run on five in-memory mutants of the source (reserve 1f->0f, part cap removed, damageFactor
dropped from the cap, pain cap removed, capacity guard removed); each must go red, so the instrument is shown to see.
A blind checker whose sandbox cannot build the C# fuzz (wslpath UNC trap) still gets this proof.

    python3 src/RimMandrake/ExplosiveGrowth/selftest_explosivegrowth_burst_cap.py
"""
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KERNEL = os.path.join(HERE, "Source", "Kernel", "RM_ExplosiveGrowthKernel.cs")
FUZZ = os.path.join(HERE, "Source", "SelfTest", "ExplosiveGrowthFuzz.cs")
SIG = "public static float BurstHitAmount(float rolled"
fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def strip_comments(src):
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    return re.sub(r"//[^\n]*", "", src)


def body_of(src, sig):
    i = src.find(sig)
    if i < 0:
        return None
    j = src.find("{", i)
    depth = 0
    for k in range(j, len(src)):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j + 1:k]
    return None


def py_expr(e):
    e = re.sub(r"\b(\d+(?:\.\d+)?)f\b", r"\1", e)
    e = e.replace("Math.Min", "min").replace("Math.Max", "max")
    e = e.replace("float.IsNaN", "math.isnan").replace("float.IsInfinity", "math.isinf")
    e = e.replace("||", " or ").replace("&&", " and ")
    e = re.sub(r"!(?!=)", " not ", e)
    return e


def split_if(stmt):
    """'if (cond) rest' -> (cond, rest); balanced parentheses."""
    i = stmt.index("(")
    depth = 0
    for k in range(i, len(stmt)):
        depth += {"(": 1, ")": -1}.get(stmt[k], 0)
        if depth == 0:
            return stmt[i + 1:k], stmt[k + 1:].strip()
    raise ValueError("unbalanced if: " + stmt)


def compile_kernel(src):
    """-> a Python function equal to the C# BurstHitAmount in src. Raises on any statement it does not understand."""
    code = strip_comments(src)
    consts = {m.group(1): float(m.group(2)) for m in
              re.finditer(r"public const float (\w+) = (-?[0-9.]+)f;", code)}
    body = body_of(code, SIG)
    if body is None:
        raise ValueError("BurstHitAmount(float rolled, ...) not found")
    lines = ["def f(rolled, partHealth, damageFactor, painNow, painShock, painPerDamage, consciousMargin, movingMargin):"]
    for raw in body.split(";"):
        s = re.sub(r"\s+", " ", raw).strip()
        if not s:
            continue
        cond = None
        if s.startswith("if "):
            cond, s = split_if(s)
        if s.startswith("return "):
            py = "return " + py_expr(s[len("return "):])
        elif re.match(r"(float )?\w+ = ", s):
            py = py_expr(re.sub(r"^float ", "", s))
        else:
            raise ValueError("untranslated statement: " + s)
        lines.append("    " + ("if %s: %s" % (py_expr(cond), py) if cond is not None else py))
    ns = {"math": math, "min": min, "max": max}
    ns.update(consts)
    exec("\n".join(lines), ns)
    return ns["f"], consts, "\n".join(lines)


def violations(f, cases=40000, seed=7):
    """-> list of (inputs, a, why) for every bound the hit breaks; bounds are literals."""
    rnd = random.Random(seed)
    bad = []
    for n in range(cases):
        rolled = rnd.choice([2.0, 3.0, 4.0, 5.0, rnd.uniform(0.1, 6.0)])
        hp = rnd.choice([0.5, 1.0, 1.9, 2.0, 2.5, 3.0, 4.0, 5.0, 10.0, 30.0, rnd.uniform(0.0, 40.0)])
        df = rnd.choice([1.0, 1.0, 1.5, 2.0, 3.0, rnd.uniform(1.0, 4.0)])
        shock = rnd.choice([0.8, 0.8, 0.5, 0.95, rnd.uniform(0.05, 1.0)])
        pnow = rnd.choice([0.0, 0.1, shock - 0.2, shock - 0.12, shock - 0.05, rnd.uniform(0.0, 1.0)])
        pnow = max(0.0, pnow)
        ppd = rnd.choice([0.0, 0.025, 0.05, 0.25, 2.5, rnd.uniform(0.0, 1.0)])
        cm = rnd.choice([0.7, 0.2, 0.15, 0.149, 0.05, 0.0, rnd.uniform(-0.2, 0.9)])
        mm = rnd.choice([0.85, 0.2, 0.15, 0.149, 0.05, 0.0, rnd.uniform(-0.2, 0.9)])
        args = (rolled, hp, df, pnow, shock, ppd, cm, mm)
        a = f(*args)
        why = None
        if a != 0:
            if not (1.0 - 1e-6 <= a <= rolled + 1e-6):
                why = "amount outside [1, rolled]"
            elif not (a * df < hp and hp - a * df >= 1.0 - 1e-4):
                why = "part left under 1 hp"
            elif a * ppd * df > 0.05 + 1e-5:
                why = "adds more than 0.05 pain"
            elif pnow + a * ppd * df > shock - 0.10 + 1e-5:
                why = "pain within 0.10 of shock"
            elif cm < 0.15 - 1e-9 or mm < 0.15 - 1e-9:
                why = "hit a pawn near a downing line"
        if why:
            bad.append((args, a, why))
    return bad


PINS = [  # (args, predicate on the amount, label) - literal expectations
    ((4.0, 3.0, 1.0, 0.0, 0.8, 0.0, 0.7, 0.85), lambda a: 1.0 <= a <= 2.0 + 1e-6, "3-hp part, x1: hit, at most 2"),
    ((5.0, 4.0, 2.0, 0.0, 0.8, 0.0, 0.7, 0.85), lambda a: a <= 1.5 + 1e-6, "4-hp part, x2 damage: at most 1.5"),
    ((5.0, 1.9, 1.0, 0.0, 0.8, 0.0, 0.7, 0.85), lambda a: a == 0, "1.9-hp part: skipped"),
    ((3.0, 30.0, 1.0, 0.0, 0.8, 0.0, 0.7, 0.85), lambda a: abs(a - 3.0) < 1e-6, "healthy big part: full roll lands"),
    ((3.0, 30.0, 1.0, 0.75, 0.8, 0.0, 0.7, 0.85), lambda a: a == 0, "pawn past the pain line: skipped (ppd 0)"),
    ((5.0, 30.0, 1.0, 0.0, 0.8, 0.025, 0.7, 0.85), lambda a: a * 0.025 <= 0.05 + 1e-6, "pain per hit at most 0.05"),
    ((3.0, 30.0, 1.0, 0.0, 0.8, 0.0, 0.1, 0.85), lambda a: a == 0, "consciousness near downing: skipped"),
    ((3.0, 30.0, 1.0, 0.0, 0.8, 0.0, 0.7, 0.1), lambda a: a == 0, "moving near downing: skipped"),
]

MUTANTS = [  # (label, old, new) applied to the kernel source; each must turn the sweep or a pin red
    ("reserve 1f->0f", "BurstPartReserve = 1f;", "BurstPartReserve = 0f;"),
    ("no part-health cap", "float a = Math.Min(rolled, (partHealth - BurstPartReserve) / damageFactor);",
     "float a = rolled;"),
    ("cap ignores damageFactor", "(partHealth - BurstPartReserve) / damageFactor)", "(partHealth - BurstPartReserve))"),
    ("no pain cap", "if (painPerDamage > 0f) a = Math.Min(a, painRoom / (painPerDamage * damageFactor));", ""),
    ("near-downed hit", "|| !(consciousMargin >= BurstCapacityMargin) || !(movingMargin >= BurstCapacityMargin)", ""),
]


def red(src):
    """-> (is_red, why) for one kernel source."""
    try:
        f, _, _ = compile_kernel(src)
    except Exception as e:  # an untranslatable mutant is not a caught one
        return False, "untranslatable: %s" % e
    for args, ok, label in PINS:
        if not ok(f(*args)):
            return True, "pin: " + label
    bad = violations(f)
    return (True, "sweep: %d, first %s" % (len(bad), bad[0][2])) if bad else (False, "")


def main():
    with open(KERNEL, encoding="utf-8") as fh:
        src = fh.read()
    f, consts, py = compile_kernel(src)
    check("sanity: transliterated body has the part cap and the pain cap",
          "partHealth - BurstPartReserve" in py and "painRoom" in py, py)
    check("sanity: transliteration sees the kernel constants", "BurstPartReserve" in consts, consts)
    for args, ok, label in PINS:
        a = f(*args)
        check("pin: " + label, ok(a), "BurstHitAmount%s = %r" % (args, a))
    bad = violations(f)
    check("sweep: 40000 cases inside every literal bound", not bad, bad[:3])
    check("sanity: a healthy pawn is hit (the function is not all skips)", f(4.0, 30.0, 1.0, 0.0, 0.8, 0.01, 0.7, 0.85) > 0)
    for label, old, new in MUTANTS:
        present = old in src
        check("mutant applies: " + label, present, old)
        if present:
            r, why = red(src.replace(old, new, 1))
            check("mutant caught: " + label, r, why)
    with open(FUZZ, encoding="utf-8") as fh:
        fz = re.sub(r"\s+", " ", strip_comments(fh.read()))
    for lit in ("a * df < hp && hp - a * df >= 1f - 1e-4f",
                "RM_ExplosiveGrowthKernel.BurstHitAmount(4f, 3f, 1f, 0f, 0.8f, 0f, 0.7f, 0.85f) <= 2f + 1e-5f",
                "RM_ExplosiveGrowthKernel.BurstHitAmount(5f, 1.9f, 1f, 0f, 0.8f, 0f, 0.7f, 0.85f) == 0f"):
        check("C# fuzz keeps literal check: " + lit, lit in fz)
    if fails:
        print("FAIL: %d failed" % len(fails))
        return 1
    print("PASS: 0 failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
