#!/usr/bin/env python3
# selftest-timeout: 60
"""PUMP_DRAW_FIX_LOSES_A_LEVEL: offline proof that a pump's channel draw conserves liquid, and that the live bar which
once read "channel lost 4 levels for 3 draws" (modcheck run4, 2026-10-25) now measures conservation exactly.

Verdict on the run4 report: HARNESS, not MOD. The bar summed excavation_report's integer `fill`, which floors part levels:
three conserved levels spread 1.5 + 1.5 + 0 read 1 + 1 + 0 = 2 (R1 replays it). PUMP_TANK_FIX_DRAWS_TOO_LITTLE
(47dddf7fd7) moved the bar to exact ProofPitWater decilitres; run5's "unpowered pump moved liquid" was toggle_recession's
pond feeding the channel, fixed by PUMP_DX (FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS). No game, no bridge, no dotnet.
Every pin reads comment-stripped source, so a comment cannot satisfy it.

  H1  liquid_pump's level() sums _water(t, ch) (exact dL) and never reads an excavation `fill`
  H2  pump_draws_into_tank demands abs(lv - (6 - moved)) < PUMP_LEVEL_TOL and tank == UNITS_PER_LEVEL * moved, tol <= 0.02
  H3  the channel sits at PUMP_DX >= 8 (east of every plot-D pond ring) and pump_unpowered_idle demands level 6 held
  P1  the channel draw's world leg takes exactly k (`ex.TryTakeDl(cell, k, out _) == k`, guarded by WaterDlAt >= k), and
      the same `take` goes to RM_LiquidTransfer.Move, must come back whole, and is what Stamp counts
  P2  Move runs the reversible leg first, refuses two irreversible legs, and puts back what the second leg did not take
  P3  TakeDlCore takes min(maxDl, w); TryTakeDl is TakeDlCore (no whole-notch floor: that mode is deleted)
  S1  sweep of the Python model of P1-P3 (cell dL x tank room): channel loss == tank gain on every cycle
  R1  the run4 reading: 30,000 conserved dL over three cells can read 2 by floored fill, and reads 3.00 by exact water

  python3 selftest_pump_draw_conserves.py [--root <dir>] [--no-mutants]
A run with no --root also runs every mutant against a temporary copy and fails unless each turns its expected pin red.
"""
import argparse
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = "src/RimMandrake/FlowWorks/Source/"
EXT = "src/RimMandrake/FlowWorks/northstar/extensions.py"
PUMP = SRC + "LiquidTypes/Building_LiquidPump.cs"
XFER = SRC + "Machinery/RM_LiquidTransfer.cs"
EXC = SRC + "RM_MapComponent_Excavation.cs"
FILES = [EXT, PUMP, XFER, EXC]
U = 10000   # RM_LevelSolve.U / RM_PumpMath.TankUnitsPerLevel: decilitres in one level of one square


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as f:
        return f.read()


def strip_cs(s):
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    s = re.sub(r"//[^\n]*", " ", s)
    return re.sub(r"\s+", " ", s)


def strip_py(s):
    out = []
    for line in s.splitlines():
        out.append(re.sub(r"\s+#.*$", "", line) if not line.lstrip().startswith("#") else "")
    return "\n".join(out)


def body(src, start, end_marker):
    i = src.find(start)
    if i < 0:
        return ""
    j = src.find(end_marker, i + len(start))
    return src[i:j if j > 0 else len(src)]


def pins(root):
    fails = []

    def pin(name, ok, msg):
        if not ok:
            fails.append("%s: %s" % (name, msg))

    ext = strip_py(read(root, EXT))
    chain = body(ext, 'def liquid_pump(t):', '\n@suite.chain(')
    lvl = body(chain, "def level():", "with t.component(")
    pin("H1", "sum(_water(t, ch))" in lvl and "fill" not in re.sub(r"_water", "", lvl).replace("fills", ""),
        "level() must sum _water(t, ch) and read no excavation fill")
    draw = body(chain, 'with t.component("pump_draws_into_tank"', "with t.component(")
    m = re.search(r"^PUMP_LEVEL_TOL\s*=\s*([0-9.]+)", ext, re.M)
    tol = float(m.group(1)) if m else 99.0
    pin("H2", "abs(lv - (6 - moved)) < PUMP_LEVEL_TOL" in draw and "== UNITS_PER_LEVEL * moved" in draw
        and "lv = rd(), level()" in draw and tol <= 0.02,
        "the draw bar must demand channel == 6 - moved (tol %.3g <= 0.02) and tank == UNITS_PER_LEVEL * moved" % tol)
    m = re.search(r"^PUMP_DX\s*=\s*(\d+)", ext, re.M)
    idle = body(chain, 'with t.component("pump_unpowered_idle")', "_stage(")
    pin("H3", m is not None and int(m.group(1)) >= 8 and "ch = _line(x0 + PUMP_DX" in chain
        and "abs(lv - 6) < PUMP_LEVEL_TOL" in idle and 'k.get("moved") == "0"' in idle,
        "channel at PUMP_DX >= 8 and the unpowered bar holding level 6")

    pump = strip_cs(read(root, PUMP))
    tryd = body(pump, "private string TryDraw()", "private string TryPour()")
    ch = body(tryd, "if (s.channel) {", "else {")
    pin("P1", "int take = TankTake(ex, s, l);" in tryd
        and "RM_TransferLeg world = RM_TransferLeg.World(k => ex.IsExcavated(cell) && ex.WaterDlAt(cell) >= k, k => ex.TryTakeDl(cell, k, out _) == k);" in ch
        and re.search(r"RM_LiquidTransfer\.Move\(take, world, RM_TransferLeg\.Split\(plan\.Count, i => plan\[i\]\.units, .*?\) == take\)", ch) is not None
        and "plan[i].tank.TryAddLiquid(l, k)" in ch and "plan[i].tank.TryRemoveLiquid(k)" in ch and "Stamp(take);" in ch,
        "the channel draw must take exactly k from the cell and move the same `take` whole into the tank plan")

    xfer = strip_cs(read(root, XFER))
    mv = body(xfer, "public static int Move(int units, RM_TransferLeg source, RM_TransferLeg dest, out RM_MoveOutcome o)", "private static void PutBack")
    pin("P2", "if (!source.Reversible && !dest.Reversible)" in mv and "bool sourceFirst = source.Reversible;" in mv
        and "if (a > 0) PutBack(first, a, ref o);" in mv and "if (b < units) PutBack(first, units - b, ref o);" in mv
        and "if (b > units) b = units;" in mv,
        "Move must run the reversible leg first and put back what the second leg refused")

    exc = strip_cs(read(root, EXC))
    core = body(exc, "private long TakeDlCore(IntVec3 c, long maxDl, out FluidDef fluid)", "public long TryTakeDl")
    tt = body(exc, "public long TryTakeDl(IntVec3 c, long maxDl, out FluidDef fluid)", "internal long BurnOffDl")
    pin("P3", "long take = maxDl < w ? maxDl : w;" in core and "long left = w - take;" in core
        and "LevelExact" not in tt and "maxDl -=" not in tt and "return TakeDlCore(c, maxDl, out fluid);" in tt,
        "TakeDlCore takes min(maxDl, w); TryTakeDl is TakeDlCore, never floored to whole notches")
    return fails


# ---- S1: the Python model of P1-P3 (what the pins hold the C# to) ----
def channel_take(units, cell):          # RM_PumpMath.ChannelTakeUnits
    return 0 if units <= 0 or cell <= 0 else min(cell, units)


def tank_take(give, room):              # RM_PumpMath.TankTakeUnits, a dug channel (partialOk)
    return 0 if give <= 0 or room <= 0 else (give if room >= give else room)


def draw(cell, stored, cap, exact):
    take = tank_take(channel_take(U, cell), cap - stored)
    if take <= 0:
        return cell, stored
    # Move(take, world, tank): the tank is reversible, so it goes first
    if cap - stored < take:
        return cell, stored
    stored += take
    maxdl = take if exact else take - take % U         # TryTakeDl
    got = min(maxdl, cell) if (cell >= take and maxdl > 0) else 0   # Can guards WaterDlAt >= k; TakeDlCore takes min
    ok = got == take                                   # world leg: TryTakeDl(...) == k
    if ok:
        cell -= got
    else:
        cell -= got                                    # a partial take would be lost here; P3 + Can make got 0 or take
        stored -= take                                 # PutBack(first, take)
    return cell, stored


def sweep():
    bad = []
    n = full = part = 0
    for exact in (True,):
        for cell in list(range(0, 3 * U + 1, 250)) + [1, U - 1, U + 1, 2 * U - 1]:
            for cap in (U, 2 * U, 3 * U, 50000):
                for stored in sorted({0, 250, U // 2, U - 1, U, cap - 1, cap - U // 3, cap}):
                    if not 0 <= stored <= cap:
                        continue
                    c1, s1 = draw(cell, stored, cap, exact)
                    n += 1
                    loss, gain = cell - c1, s1 - stored
                    if loss != gain or loss < 0 or s1 > cap:
                        bad.append((exact, cell, cap, stored, loss, gain))
                    full += gain == U
                    part += 0 < gain < U
    if not full or not part:
        bad.append(("vacuous sweep", full, part))
    return n, bad


def replay_run4():
    """30,000 dL, three cells, the drawn cell emptied before the channel relevels: floored fill reads 2, exact reads 3."""
    cells = [15000, 15000, 0]
    floored = sum(c // U for c in cells)
    exact = sum(cells) / float(U)
    return floored, exact


MUTANTS = {
    "M1": (EXT, "return sum(_water(t, ch))", "return sum(int(w) for w in _water(t, ch))  # fill", "H1"),
    "M2": (EXT, "PUMP_LEVEL_TOL = 0.02", "PUMP_LEVEL_TOL = 1.5", "H2"),
    "M3": (PUMP, "k => ex.TryTakeDl(cell, k, out _) == k);\n\t\t\t\t\tif (RM_LiquidTransfer.Move(take, world",
           "k => ex.TryTakeDl(cell, k, out _) > 0);\n\t\t\t\t\tif (RM_LiquidTransfer.Move(take, world", "P1"),
    "M4": (XFER, "if (b < units) PutBack(first, units - b, ref o);", "if (b < 0) PutBack(first, units - b, ref o);", "P2"),
    "M5": (EXC, "long take = maxDl < w ? maxDl : w;", "long take = w;", "P3"),
}


def run_mutants():
    fails = []
    for name, (rel, old, new, want) in MUTANTS.items():
        tmp = tempfile.mkdtemp(prefix="pumpcons_")
        try:
            for f in FILES:
                os.makedirs(os.path.dirname(os.path.join(tmp, f)), exist_ok=True)
                shutil.copy(os.path.join(REPO, f), os.path.join(tmp, f))
            p = os.path.join(tmp, rel)
            txt = read(tmp, rel)
            if old not in txt:
                fails.append("%s: anchor gone from %s" % (name, rel))
                continue
            with open(p, "w", encoding="utf-8") as f:
                f.write(txt.replace(old, new, 1))
            red = [x.split(":")[0] for x in pins(tmp)]
            if want not in red:
                fails.append("%s: expected %s red, got %s" % (name, want, red or "all green"))
            else:
                print("  mutant %s -> %s red" % (name, ",".join(red)))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--no-mutants", action="store_true")
    a = ap.parse_args()
    root = a.root or REPO
    fails = pins(root)
    n, bad = sweep()
    if bad:
        fails.append("S1: %d of %d cycles break conservation, first %s" % (len(bad), n, bad[0]))
    floored, exact = replay_run4()
    if not (floored == 2 and abs(exact - 3.0) < 1e-9):
        fails.append("R1: run4 replay floored=%s exact=%s" % (floored, exact))
    print("pins H1-H3 P1-P3: %s" % ("ok" if not [f for f in fails if f[0] in "HP"] else "RED"))
    print("S1 sweep: %d cycles, %d conservation breaks" % (n, len(bad)))
    print("R1 run4 replay: 30000 dL reads %d by floored fill, %.2f by exact water" % (floored, exact))
    if a.root is None and not a.no_mutants:
        fails += run_mutants()
    for f in fails:
        print("FAIL " + f)
    print("PASS" if not fails else "FAIL (%d)" % len(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
