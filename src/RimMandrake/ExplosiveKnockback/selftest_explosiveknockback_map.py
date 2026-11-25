#!/usr/bin/env python3
"""The situation map of Explosive Knockback as a permanent check (RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX).

Source/SelfTest/KnockbackMap.cs runs the SHIPPED throw decision (Source/RM_KnockbackPlan.cs over RM_KnockbackMath.cs) on a model
map and reads the mod's bars off where every thing ends, over situations it enumerates: 121,920 lanes (thing x direction x
distance x obstacle x obstacle distance x width x blast), 2,496 spared cases, 20,000 seeded storerooms each with both tie
orders of the game's "place near" search, the mod's own scenes and the cases that used to fail, and each plan-side Mod
Settings switch flipped alone. What the model assumes and what the range leaves out is the header of KnockbackMap.cs.
The carrier probes compile its ground-path and corpse-pose code with stand-ins for Unity and Verse.

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
from winbuild import run_interop_captured, win  # noqa: E402  (WSL lost-launch retry and paths)
import fcntl
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE_ROOT = os.path.abspath(os.environ.get("WINBUILD_ROOT", rm_str("build")))
STAGE = os.path.join(STAGE_ROOT, "ExplosiveKnockbackMapSelfTest")
DOTNET = ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]
SOURCE = ("RM_KnockbackMath.cs", "RM_KnockbackPlan.cs", "RM_KnockbackVerdicts.cs")
SELFTEST = ("Program.cs", "KnockbackFuzz.cs", "KnockbackSweep.cs", "KnockbackMap.cs", "RimMandrakeExplosiveKnockback.SelfTest.csproj")

# (label, file, old text, new text): each breaks one rule of the decision; the map must see every one.
# The first block are the rules that lived in Verse code until 2026-11-17, where blind cycle 5 planted ten faults and every
# offline suite stayed green.
FAULTS = [
    ("a stack whose pit cell is taken settles only beside it", "RM_KnockbackPlan.cs", "pit != null && pit.Contains(Key(x, z));", "d2 <= 2.25f;"),
    ("a stack jumps from its full pit into another", "RM_KnockbackPlan.cs", "pit != null && pit.Contains(Key(x, z));", "true;"),
    ("a pawn in bed is thrown", "RM_KnockbackPlan.cs", 'if (f.inBed) return "in_bed";', ""),
    ("a pawn carrying a pawn is thrown", "RM_KnockbackPlan.cs", 'if (f.carryingPawn) return "carrying_pawn";', ""),
    ("an airborne pawn is thrown", "RM_KnockbackPlan.cs", 'if (f.flying) return "flying";', ""),
    ("a pawn in a pit is thrown", "RM_KnockbackPlan.cs", 'if (f.onSuperdeep && !(gas && f.onCover)) return "in_pit";', ""),
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
    # blind cycle 6 (RIMMANDRAKE_MOVE_KNOCKBACK_GOODS_PINNED_AGAINST_WALLS_SHELVES): the tumble that moves a good its throw, hop
    # and bounce leave in place (a one-cell throw into a wall, a blocked bounce, a deep shelf row)
    ("a good pinned by a wall or a shelf row sits still", "RM_KnockbackPlan.cs", "            Tumble(p, f, s, grid, maxCells);\n", ""),
    ("a gas hop can exceed the burst cap", "RM_KnockbackPlan.cs", "n = p.cells + 1; n <= maxCells;", "n = p.cells + 1; n <= p.cells + HopExtraCells;"),
    ("a gas tumble can exceed the burst cap", "RM_KnockbackPlan.cs", "Tumble(p, f, s, grid, maxCells);", "Tumble(p, f, s, grid, p.cells + HopExtraCells);"),
    ("a gas-thrown heavy stack hits a pawn", "RM_KnockbackMath.cs", "if (explosionId < 0 || !enabled", "if (!enabled"),
    ("a diagonal goods leg crosses an open pit", "RM_KnockbackPlan.cs", "p.res = StopAtCrossedPit(grid, f.x, f.z, p.res);", ""),
    ("a diagonal pit flight aims at the pit centre", "RM_KnockbackPlan.cs",
     "pitEntryOffsetX = dx * entry - x * stepX, pitEntryOffsetZ = dz * entry - z * stepZ", "pitEntryOffsetX = 0f, pitEntryOffsetZ = 0f"),
    ("a gas landing ignores the burst cap", "RM_KnockbackPlan.cs",
     "return cap <= 0 || Math.Max(Math.Abs(x - originX), Math.Abs(z - originZ)) <= cap;", "return true;"),
]


GAS_REACH = "GenSight.LineOfSight(c, cell, map, skipFirstCell: true)"


def gas_reach_is_the_explosions(source):
    """GasBurst's body asks the sight line DamageWorker.ExplosionCellsToHit asks, and skips a cell it refuses."""
    body = source.split("public static void GasBurst(", 1)[-1].split("private bool ThrowPawn(", 1)[0]
    code = "\n".join(l.split("//", 1)[0] for l in body.splitlines())
    return "!" + GAS_REACH in code


def stage(fault=None):
    os.makedirs(os.path.join(STAGE, "SelfTest"), exist_ok=True)
    # shutil.copy, never copy2: a fresh mtime makes dotnet rebuild; an old one ran a stale binary, the last planted
    # fault or another clone's build (RIMMANDRAKE_RESTAGE_CSHARP_SUITES_FRESH_MTIME_STALE_FAULT_BINARY)
    for f in SOURCE:
        shutil.copy(os.path.join(HERE, "Source", f), os.path.join(STAGE, f))
    for f in SELFTEST:
        shutil.copy(os.path.join(HERE, "Source", "SelfTest", f), os.path.join(STAGE, "SelfTest", f))
    map_test = Path(STAGE, "SelfTest", "KnockbackMap.cs")
    original = map_test.read_text(encoding="utf-8")
    map_test.write_text("#define RM_KB_CARRIER_TEST\n" + original + carrier_probes(), encoding="utf-8")
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


def carrier_probes():
    """Compile the carrier's ground interpolation and pose writes with stand-ins for Unity and Verse."""
    source = Path(HERE, "Source", "RM_ThingFlyer_Knockback.cs").read_text(encoding="utf-8")
    launch = "\n".join(re.findall(r"^ +f\.spin[^\n]+", source.split("LaunchContainer(", 1)[0], re.M))
    spin_angle = re.search(r"private float SpinAngle => [^;]+;", source)[0]
    save_fields = "\n".join(re.findall(r"Scribe_Values\.Look\(ref spin[^;]+;", source))
    writes = [re.search(r"if \([^\n]*inner is Corpse [^\n]+\)\s+\{\s+TurnCorpse\([^)]+\);[^\n]*\n\s+\}", source[source.index(start):])[0]
              for start in ("protected override void Tick()", "private void Land(")]
    start = source.split("private void StartLeg(", 1)[1].split("private Vector3 DestinationPos", 1)[0]
    setup = "\n".join(re.findall(r"^\s*(?:startVec|destCell|destinationOffset|float dist|float speed|ticksFlightTime) =[^;]+;", start, re.M))
    endpoint = re.search(r"private Vector3 DestinationPos => [^;]+;", source)[0]
    sample = re.search(r"groundPos = Vector3.Lerp\([^;]+;", source)[0]
    cell = re.search(r"IntVec3 cell = [^;]+groundPos.ToIntVec3\(\);", source)[0]
    return """
internal sealed class GoodsFlightProbe
{
    private struct IntVec3
    {
        public int x, z;
        public IntVec3(int x, int y, int z) { this.x = x; this.z = z; }
        public Vector3 ToVector3ShiftedWithAltitude(float altitude) => new Vector3(x + 0.5f, altitude, z + 0.5f);
    }
    private struct Vector3
    {
        public float x, y, z;
        public Vector3(float x, float y, float z) { this.x = x; this.y = y; this.z = z; }
        public IntVec3 ToIntVec3() => new IntVec3((int)x, 0, (int)z);
        public static Vector3 operator +(Vector3 a, Vector3 b) => new Vector3(a.x + b.x, a.y + b.y, a.z + b.z);
        public static float Distance(Vector3 a, Vector3 b)
        {
            float x = a.x - b.x, y = a.y - b.y, z = a.z - b.z;
            return MathF.Sqrt(x * x + y * y + z * z);
        }
        public static Vector3 Lerp(Vector3 a, Vector3 b, float t) =>
            new Vector3(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t);
    }
    private static class Mathf
    {
        public static int Max(int a, int b) => Math.Max(a, b);
        public static float Max(float a, float b) => Math.Max(a, b);
        public static int CeilToInt(float f) => (int)MathF.Ceiling(f);
    }
    private static class RimMandrakeExplosiveKnockbackSettings { public const float goodsFlightSpeed = 14f; }
    private sealed class FlightDef { public readonly float Altitude = 0f; }
    private readonly FlightDef def = new FlightDef();
    private Vector3 startVec, destinationOffset;
    private IntVec3 destCell;
    private int ticksFlightTime;
""" + endpoint + """
    public IEnumerable<((int x, int z) cell, float x, float z)> Samples(KbLeg leg)
    {
        var from = new IntVec3(leg.fromX, 0, leg.fromZ);
        KbResult res = leg.res;
""" + setup + """
        for (int ticksFlying = 1; ticksFlying <= ticksFlightTime; ticksFlying++)
        {
            float t = (float)ticksFlying / ticksFlightTime;
            Vector3 """ + sample + """
            """ + cell + """
            yield return ((cell.x, cell.z), groundPos.x, groundPos.z);
        }
    }
}

internal sealed class CorpsePoseProbe
{
    internal sealed class Corpse { public float angle = 90f; }
    private static float CorpseAngle(Corpse body) => body.angle;
    private static void TurnCorpse(Corpse body, float angle) => body.angle = angle;
    private static class Mathf { public static float Repeat(float value, float length) => value - MathF.Floor(value / length) * length; }
    private static class Rand { public const float Sign = 1f; public static float Range(float min, float max) => 1f; }
    private static class RimMandrakeExplosiveKnockbackSettings { public const float goodsSpinDegPerTick = 20f; }
    private sealed class Scribe_Values
    {
        public Dictionary<string, object> fields;
        public bool loading;
        public void Look<T>(ref T value, string label, T fallback)
        {
            if (loading) value = fields.TryGetValue(label, out object saved) ? (T)saved : fallback;
            else if (!Equals(value, fallback)) fields[label] = value;
        }
    }
    private readonly Scribe_Values scribe = new Scribe_Values();
    private float spin0, spinRate;
    private bool spin0IsCorpsePose;
    private int ticksTotal;
    private object Inner;
""" + spin_angle + """
    public void Launch(Corpse body)
    {
        var f = this;
        Inner = body;
""" + launch + """
    }
    public void Tick(object inner)
    {
        ticksTotal++;
""" + writes[0] + """
    }
    public void Land(object inner)
    {
""" + writes[1] + """
    }
    public void Expose(Dictionary<string, object> fields, bool loading)
    {
        scribe.fields = fields;
        scribe.loading = loading;
""" + save_fields.replace("Scribe_Values.Look", "scribe.Look") + """
    }
}
"""


def run(dotnet, extra):
    r = run_interop_captured([dotnet, "run", "--project", win(os.path.join(STAGE, "SelfTest", "RimMandrakeExplosiveKnockback.SelfTest.csproj")),
                              "-c", "Release", "--"] + list(extra), capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return r.returncode, (r.stdout or "").replace("\r", "") + (r.stderr or "")


def main(argv):
    dotnet = next((d for d in DOTNET if os.path.isfile(d)), None)
    if dotnet is None or not os.path.isdir(os.path.dirname(STAGE)):
        print("UNMEASURED: no Windows dotnet.exe / staging root on this machine")
        return 1
    # the model's A5 and the game must reach by one rule: the sight line an explosion uses (RIMMANDRAKE_STOP_GAS_SHOVE_PAST_WALL_CORNER_UNSEEN)
    if not gas_reach_is_the_explosions(open(os.path.join(HERE, "Source", "RM_MapComponent_Knockback.cs"), encoding="utf-8").read()):
        print("explosive knockback map: FAIL (GasBurst queues things without the explosion's sight line: %s)" % GAS_REACH)
        return 1
    with open(os.path.join(HERE, "Source", "RM_ThingFlyer_Knockback.cs"), encoding="utf-8") as f:
        if not re.search(r"RM_KnockbackMath\.HeavyKnock\([^;]*out int stun, explosionId\)\)", f.read()):
            print("explosive knockback map: FAIL (the carrier drops the burst ID before testing for a heavy hit)")
            return 1
    lock_path = "/tmp/explosiveknockback_map_selftest.lock" if STAGE_ROOT == rm_str("build") else STAGE + ".lock"
    with open(lock_path, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        for d in ("obj", "bin"):     # retained outputs can look newer than fresh sources (a clock step back): build clean
            shutil.rmtree(os.path.join(STAGE, "SelfTest", d), ignore_errors=True)
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
