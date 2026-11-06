"""Offline price check for the dig_finds chain (QUARRY_DIG_FIX_VALIDATED_BUT_NEVER_FINISHES). No bridge, no game.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_dig_finds_budget.py

The rows finds_off_none / cut_turns_up_local_find failed on every run since DIG_FILL_TUNE_HOURS_OF_SHOVEL_WORK (x4 labour,
card 2026-10-25) with "the dig job never finished": each hand cut on the one cell is priced by JobDriver_DigCanal
(WorkToCut(notch) x digLabourMultiplier, x digRockWorkMultiplier on rock ground) and paid at 1.7 x MiningSpeed a tick,
and the shipped x4 made cut 1 alone cost more ticks than _dig_by_hand waits. This reads the prices from the C# and the
harness constants from extensions.py (AST, nothing imported) and checks that:
  - every _dig_by_hand call in dig_finds sits inside `_setting_in(..., "digLabourMultiplier", DIG_FINDS_LABOUR, ...)`;
  - DIG_FINDS_LABOUR is a value the mod accepts, SHIPPED_LABOUR is the mod's default (the restore value);
  - every cut, worst case (rock ground on), fits DIG_WAIT_TICKS for a MiningSpeed-1.0 colonist plus walk/shovel overhead.
Can-fail: the same budget at the shipped labour must NOT fit (the instance that failed live).
"""
import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "Source")
EXT = os.path.join(HERE, "extensions.py")
FAILS = []

MINING_SPEED = 1.0       # pessimistic: vanilla MiningSpeed at Mining 10 is above 1 (0.04 + 0.12 x level)
OVERHEAD_TICKS = 1500    # walk to the cell, take the shovel, the first 500-tick poll


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def cs_const(path, name, cast):
    text = open(os.path.join(SRC, path), encoding="utf-8").read()
    m = re.search(r"\b%s\s*=\s*([0-9.]+)f?\s*;" % re.escape(name), text)
    if not m:
        raise SystemExit("FAIL cannot read %s from %s" % (name, path))
    return cast(m.group(1))


def module_consts(tree):
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return out


def dig_calls_under_labour(fn):
    """(calls to _dig_by_hand, how many sit inside the labour _setting_in block)."""
    total, covered = [0], [0]

    def is_labour(item):
        c = item.context_expr
        return (isinstance(c, ast.Call) and getattr(c.func, "id", None) == "_setting_in" and len(c.args) >= 4
                and isinstance(c.args[2], ast.Constant) and c.args[2].value == "digLabourMultiplier"
                and getattr(c.args[3], "id", None) == "DIG_FINDS_LABOUR")

    def walk(node, under):
        if isinstance(node, ast.With) and any(is_labour(i) for i in node.items):
            under = True
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "_dig_by_hand":
            total[0] += 1
            covered[0] += 1 if under else 0
        for ch in ast.iter_child_nodes(node):
            walk(ch, under)

    walk(fn, False)
    return total[0], covered[0]


def ticks(notch, labour, rock_mult, per_tick):
    work = round(max(1, work_per_notch * notch) * labour) * rock_mult
    return work / (per_tick * MINING_SPEED) + OVERHEAD_TICKS


tree = ast.parse(open(EXT, encoding="utf-8").read())
K = module_consts(tree)
fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "dig_finds"), None)
check(fn is not None, "dig_finds chain found in extensions.py")
work_per_notch = cs_const("RM_DigDepthMath.cs", "WorkPerNotch", int)
per_tick = cs_const("RM_DigDepthMath.cs", "WorkPerTickAtSpeedOne", float)
lab_min = cs_const("RM_DigDepthMath.cs", "MinLabourMultiplier", float)
lab_max = cs_const("RM_DigDepthMath.cs", "MaxLabourMultiplier", float)
lab_default = cs_const("RM_DigDepthMath.cs", "DefaultLabourMultiplier", float)
rock = cs_const("RimMandrakeFlowWorksMod.cs", "digRockWorkMultiplier", float)
wait, labour, shipped = K.get("DIG_WAIT_TICKS"), K.get("DIG_FINDS_LABOUR"), K.get("SHIPPED_LABOUR")
check(None not in (wait, labour, shipped), "harness constants DIG_WAIT_TICKS=%s DIG_FINDS_LABOUR=%s SHIPPED_LABOUR=%s"
      % (wait, labour, shipped))
if fn is not None and None not in (wait, labour, shipped):
    n, covered = dig_calls_under_labour(fn)
    check(n >= 1 and covered == n, "every _dig_by_hand in dig_finds runs under the labour setting (%d of %d)" % (covered, n))
    check(lab_min <= labour <= lab_max, "DIG_FINDS_LABOUR %s within the mod's %s..%s" % (labour, lab_min, lab_max))
    check(shipped == lab_default, "SHIPPED_LABOUR %s is the mod's default %s (the value restored)" % (shipped, lab_default))
    for notch in range(1, n + 1):
        need = ticks(notch, labour, rock, per_tick)
        check(need <= wait, "cut %d (rock ground x%s) needs %.0f ticks <= wait %d" % (notch, rock, need, wait))
    # can-fail: the instance that failed live -- the shipped labour, plain soil, the old 8,000-tick wait
    old = ticks(1, lab_default, 1, per_tick)
    check(old > 8000, "can-fail: shipped x%s labour, cut 1 on soil needs %.0f ticks > the old 8,000 wait" % (lab_default, old))
    check(ticks(n, lab_default, 1, per_tick) > wait,
          "can-fail: at the shipped labour cut %d would still overrun the new wait %d" % (n, wait))

print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
