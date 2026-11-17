#!/usr/bin/env python3
"""The situation map of Explosive Knockback as a permanent check (RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX).

Source/SelfTest/KnockbackMap.cs runs the SHIPPED throw decision (Source/RM_KnockbackPlan.cs over RM_KnockbackMath.cs) on a model
map and reads the mod's bars off where every thing ends, over situations it enumerates: 121,920 lanes (thing x direction x
distance x obstacle x obstacle distance x width x blast), 2,496 spared cases, 20,000 seeded storerooms each with both tie
orders of the game's "place near" search, the mod's own scenes and the cases that used to fail, and each plan-side Mod
Settings switch flipped alone. What the model assumes and what the range leaves out is the header of KnockbackMap.cs.

This script:
  1. runs the whole map: every bar must hold (exit 1 with the breaking readings otherwise);
  2. plants faults in a staged copy of the decision, one at a time, and requires the map to go red on each: a map that
     stays green over a broken decision is blind (a guard is untested until it has rejected a broken input).

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_map.py            the map and the planted faults
    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_map.py --map-only  the map alone (about 15 s)
    ... --examples                                                                           print breaking examples drawn
"""
# selftest-timeout: 1500
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_str  # noqa: E402  (data root: rmpaths.py)
from winbuild import run_interop_captured  # noqa: E402  (WSL lost-launch retry)
import fcntl
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE = os.environ.get("WINBUILD_ROOT", rm_str("build")) + "/ExplosiveKnockbackMapSelfTest"
DOTNET = ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]
SOURCE = ("RM_KnockbackMath.cs", "RM_KnockbackPlan.cs", "RM_KnockbackVerdicts.cs")
SELFTEST = ("Program.cs", "KnockbackFuzz.cs", "KnockbackSweep.cs", "KnockbackMap.cs", "RimMandrakeExplosiveKnockback.SelfTest.csproj")

# (label, file, old text, new text): each breaks one rule of the decision; the map must see every one.
# The first block are the rules that lived in Verse code until 2026-11-17, where blind cycle 5 planted ten faults and every
# offline suite stayed green.
FAULTS = [
    ("a pawn in bed is thrown", "RM_KnockbackPlan.cs", 'if (f.inBed) return "in_bed";', ""),
    ("a pawn carrying a pawn is thrown", "RM_KnockbackPlan.cs", 'if (f.carryingPawn) return "carrying_pawn";', ""),
    ("an airborne pawn is thrown", "RM_KnockbackPlan.cs", 'if (f.flying) return "flying";', ""),
    ("a pawn in a pit is thrown", "RM_KnockbackPlan.cs", 'if (f.onSuperdeep) return "in_pit"; // GPT', "// GPT"),
    ("goods on a pit floor are thrown", "RM_KnockbackPlan.cs", "if (!pawn && f.onSuperdeep)", "if (false && f.onSuperdeep)"),
    ("a recovering pawn is thrown again", "RM_KnockbackPlan.cs", "if (pawn && f.recovering)", "if (false && f.recovering)"),
    ("a closed container keeps nothing", "RM_KnockbackPlan.cs", "bool closed = q.closedContainerGuard && f.onClosed;", "bool closed = false;"),
    ("every shelf keeps its goods", "RM_KnockbackPlan.cs", "GoodsHeld(storage, closed, q.openStorageProtects)", "GoodsHeld(storage, closed, true)"),
    ("a gas shove keeps the full throw", "RM_KnockbackPlan.cs", "s.maxCells = Math.Min(s.maxCells, 1);", ""),
    ("a gas shove has no cooldown", "RM_KnockbackPlan.cs", "if (f.gasShovedAgo < q.gasPawnCooldownTicks)", "if (false)"),
    ("a shield belt holds nobody", "RM_KnockbackPlan.cs", "if (pawn && f.shieldAbsorbed && q.shieldsAbsorbThrow)", "if (false)"),
    ("the wild factor lifts a rim good", "RM_KnockbackPlan.cs", "if (p.kernelCells <= 0 || p.cells <= 0)", "if (p.cells <= 0 && p.kernelCells <= 0)"),
    ("people fly wild too", "RM_KnockbackPlan.cs", "p.cells = pawn ? p.kernelCells : ", "p.cells = false ? p.kernelCells : "),
    ("a stack against a wall sits still", "RM_KnockbackPlan.cs", "p.wallFirst = true;", ""),
    ("a short throw onto sandbags is undone", "RM_KnockbackPlan.cs", "p.res = r;\n                        p.hopped = true;", "p.hopped = true;"),
    ("a full pit cell sends the stack anywhere near", "RM_KnockbackPlan.cs",
     "? new[] { KbPlace.PitFloor, KbPlace.NearRim, KbPlace.NearOrigin, KbPlace.Fallback }", "? new[] { KbPlace.NearCell, KbPlace.NearOrigin, KbPlace.Fallback }"),
    ("a full pit sets the stack down on any side", "RM_KnockbackPlan.cs", "return cell == KbCell.Open && d2 <= RimSpread * RimSpread && a <= b;",
     "return cell == KbCell.Open && d2 <= RimSpread * RimSpread;"),
    ("a container flies through a person", "RM_KnockbackPlan.cs", "break; // it does not fly through a person", "// it does not fly through a person"),
    ("a container lands on an occupied cell", "RM_KnockbackPlan.cs", "RM_KnockbackMath.ShoveCellFree(w.Grid(true).At(x, z), w.Occupied(x, z))",
     "RM_KnockbackMath.ShoveCellFree(w.Grid(true).At(x, z), false)"),
    ("a container's rest is read off a shorter line", "RM_KnockbackPlan.cs", "RM_KnockbackMath.Line(f.x, f.z, p.dx, p.dz, p.planned);\n",
     "RM_KnockbackMath.Line(f.x, f.z, p.dx, p.dz, p.res.cellsTravelled);\n"),
    ("a big container is thrown", "RM_KnockbackMath.cs", "if (!oneByOne || mass > containerMassLimit)", "if (mass > containerMassLimit)"),
    ("a flying good never bounces", "RM_KnockbackPlan.cs", "if (!solid || cellsLeft <= 0 || !q.goodsRebound || bounces >= q.maxBounces)", "if (true)"),
    ("a landing never breaks a cover", "RM_KnockbackMath.cs", "return covered && !container && explosionId >= 0;", "return false;"),
    ("a gas shove breaks a cover", "RM_KnockbackMath.cs", "return covered && !container && explosionId >= 0;", "return covered && !container;"),
    ("a pawn on a cover's deck blocks nobody", "RM_KnockbackMath.cs", "if (forPawn && pawnThere)\n            {\n                return KbCell.Pawn;\n            }", ""),
    ("a throw crosses a pit", "RM_KnockbackMath.cs", "if (pit)\n                {", "if (false)\n                {"),
    ("a corpse is weighed by the creature limit", "RM_KnockbackMath.cs", "if ((kind == KbKind.Item || kind == KbKind.Corpse) && mass > s.lightMassLimit)",
     "if (kind == KbKind.Item && mass > s.lightMassLimit)"),
    ("flying goods off falls back to a throw", "RM_KnockbackPlan.cs", "if (!pawn && !q.flyingGoods)", "if (false)"),
    ("the container shove cannot be switched off", "RM_KnockbackPlan.cs", "if (!q.shoveClosedContainers)", "if (false)"),
    ("downed pawns cannot be switched off", "RM_KnockbackPlan.cs", "if (f.downed && !q.throwDowned)", "if (false)"),
]


def stage(fault=None):
    os.makedirs(os.path.join(STAGE, "SelfTest"), exist_ok=True)
    for f in SOURCE:
        shutil.copy2(os.path.join(HERE, "Source", f), os.path.join(STAGE, f))
    for f in SELFTEST:
        shutil.copy2(os.path.join(HERE, "Source", "SelfTest", f), os.path.join(STAGE, "SelfTest", f))
    if fault is None:
        return True
    _, name, old, new = fault
    p = os.path.join(STAGE, name)
    text = open(p, encoding="utf-8").read()
    if old not in text:
        return False
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text.replace(old, new, 1))
    return True


def win(p):
    p = os.path.abspath(p)
    return "%s:\\%s" % (p[5].upper(), p[7:].replace("/", "\\"))


def run(dotnet, extra):
    r = run_interop_captured([dotnet, "run", "--project", win(os.path.join(STAGE, "SelfTest", "RimMandrakeExplosiveKnockback.SelfTest.csproj")),
                              "-c", "Release", "--"] + list(extra), capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return r.returncode, (r.stdout or "").replace("\r", "") + (r.stderr or "")


def main(argv):
    dotnet = next((d for d in DOTNET if os.path.isfile(d)), None)
    if dotnet is None or not os.path.isdir(os.path.dirname(STAGE)):
        print("UNMEASURED: no Windows dotnet.exe / D: staging root on this machine")
        return 1
    with open(os.path.join(tempfile.gettempdir(), "explosiveknockback_map_selftest.lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        stage()
        rc, out = run(dotnet, ["--map"] + (["--map-examples"] if "--examples" in argv else []))
        lines = [l for l in out.splitlines() if l.startswith(("KNOCKBACK MAP", "HOLDS", "BREAKS", "CASE", "knockback map"))]
        if "--examples" in argv:
            print(out)
        else:
            print("\n".join(lines))
        if rc != 0 or not lines or "every bar holds" not in lines[-1]:
            if not lines:
                print(out[-3000:])
            print("explosive knockback map: FAIL (the map is red on the shipped decision)")
            return 1
        if "--map-only" in argv:
            print("explosive knockback map: PASS (map only; planted faults not run)")
            return 0
        missed = []
        for fault in FAULTS:
            if not stage(fault):
                print("FAIL planted fault '%s' could not be planted (its line is gone from %s)" % (fault[0], fault[1]))
                missed.append(fault[0])
                continue
            frc, fout = run(dotnet, ["--map", "--map-rooms", "1500"])
            red = [l for l in fout.splitlines() if l.startswith(("BREAKS", "CASE FAILED"))]
            if frc == 0 or not red:
                print("FAIL planted fault NOT SEEN by the map: %s%s" % (fault[0], "" if "knockback map" in fout else " (did not run: %s)" % fout[-300:]))
                missed.append(fault[0])
            else:
                print("seen  %-48s %s" % (fault[0], red[0][:110]))
        stage()
    ok = not missed
    print("explosive knockback map: %s (every bar holds; %d of %d planted faults seen)" % ("PASS" if ok else "FAIL", len(FAULTS) - len(missed), len(FAULTS)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
