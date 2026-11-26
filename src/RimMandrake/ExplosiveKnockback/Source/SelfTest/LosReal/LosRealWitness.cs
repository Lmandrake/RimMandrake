// The real-game witness of the situation map's assumption A5 (RIMMANDRAKE_REPLAY_ENUMERATED_SITUATIONS_IN_HEADLESS_REAL_GAME).
// It links the game's own Assembly-CSharp and asks Verse.GenSight.LineOfSight(start, end, map, skipFirstCell: true), the
// overload DamageWorker.ExplosionCellsToHit and RM_MapComponent_Knockback.GasBurst call, of every sight line the map asks.
// The Map is a hand-built shell (design/specs/2026-11-25-offline-real-game-code-probe): info.Size, CellIndices and an
// EdificeGrid; a model wall is a Building of a Fillage.Full def, a model closed door a Building_Door of that def (its Open
// reads false). Both are uninitialized objects: a def constructor and ThingMaker reach Unity ECalls offline.
// Run by selftest_explosiveknockback_los_real.py, never by hand.
using System;
using System.Runtime.CompilerServices;
using RimMandrake.ExplosiveKnockback;
using RimWorld;
using Verse;

internal static class LosRealWitness
{
    private static Map map;
    private static int size;
    private static KbCell[,] mirror;
    private static Building[,] walls, doors;
    private static ThingDef full;

    private static T Raw<T>() => (T)RuntimeHelpers.GetUninitializedObject(typeof(T));

    private static void Shell(int need)
    {
        size = Math.Max(need, 64);
        map = new Map();
        map.info.Size = new IntVec3(size, 1, size);
        map.cellIndices = new CellIndices(map);
        map.edificeGrid = new EdificeGrid(map);
        mirror = new KbCell[size, size];
        walls = new Building[size, size];
        doors = new Building[size, size];
        if (full == null)
        {
            full = Raw<ThingDef>();
            full.defName = "RM_LosWitnessWall";
            full.category = ThingCategory.Building;
            full.fillPercent = 1f;
            full.size = new IntVec2(1, 1);
            full.thingClass = typeof(Building);
        }
    }

    private static Building Made(int x, int z, bool door)
    {
        Building[,] pool = door ? doors : walls;
        if (pool[x, z] == null)
        {
            Building b = door ? Raw<Building_Door>() : Raw<Building>();
            b.def = full;
            b.Position = new IntVec3(x, 0, z);
            pool[x, z] = b;
        }
        return pool[x, z];
    }

    private static void Sync(MWorld w, int x, int z)
    {
        KbCell want = w.terr[x, z] == KbCell.Wall || w.terr[x, z] == KbCell.Door ? w.terr[x, z] : KbCell.Open;
        KbCell have = mirror[x, z];
        if (want == have) return;
        if (have != KbCell.Open) map.edificeGrid.DeRegister(Made(x, z, have == KbCell.Door));
        if (want != KbCell.Open) map.edificeGrid.Register(Made(x, z, want == KbCell.Door));
        mirror[x, z] = want;
    }

    public static bool Ask(MWorld w, int cx, int cz, int x, int z)
    {
        if (map == null || w.W > size || w.H > size) Shell(Math.Max(w.W, w.H));
        // the line visits only cells of its bounding box: mirror those
        for (int i = Math.Min(cx, x); i <= Math.Max(cx, x); i++)
            for (int j = Math.Min(cz, z); j <= Math.Max(cz, z); j++)
                Sync(w, i, j);
        return GenSight.LineOfSight(new IntVec3(cx, 0, cz), new IntVec3(x, 0, z), map, skipFirstCell: true);
    }

    /// <summary>The witness's own sanity, before the map: a wall and a closed door block the real line; open ground does not.</summary>
    private static string Calibrate()
    {
        var w = new MWorld(9, 9);
        if (!Ask(w, 1, 4, 7, 4)) return "open ground blocks the real line";
        w.terr[4, 4] = KbCell.Wall;
        if (Ask(w, 1, 4, 7, 4)) return "a wall does not block the real line";
        w.terr[4, 4] = KbCell.Door;
        if (Ask(w, 1, 4, 7, 4)) return "a closed door does not block the real line";
        w.terr[4, 4] = KbCell.Open;
        if (!Ask(w, 1, 4, 7, 4)) return "a removed wall still blocks the real line";
        return null;
    }

    /// <summary>The copy against the game, densely: seeded layouts of walls and closed doors, every line from the centre to each cell
    /// within a blast radius. The map's own situations seldom put a door or a diagonal tie on a sight line (a closed door left out
    /// of the copy changes 14 of its ~1e6 lines), so this sweep is what makes a geometry fault in the copy visible.</summary>
    private static (long asked, long differ, string example) Sweep(int layouts, int seed)
    {
        const int N = 25, C = 12;
        const double R = 9.9;
        var rnd = new Random(seed);
        long asked = 0, differ = 0;
        string example = null;
        for (int l = 0; l < layouts; l++)
        {
            var w = new MWorld(N, N);
            double density = 0.05 + 0.35 * rnd.NextDouble();
            for (int x = 0; x < N; x++)
                for (int z = 0; z < N; z++)
                {
                    double r = rnd.NextDouble();
                    w.terr[x, z] = r < density * 0.7 ? KbCell.Wall : r < density ? KbCell.Door : KbCell.Open;
                }
            if (rnd.Next(3) == 0) w.terr[C, C] = rnd.Next(2) == 0 ? KbCell.Wall : KbCell.Door; // a blast in a wall or door cell
            for (int x = 0; x < N; x++)
                for (int z = 0; z < N; z++)
                {
                    if ((x - C) * (x - C) + (z - C) * (z - C) > R * R) continue;
                    asked++;
                    bool copied = KnockbackMap.LosCopied(w, C, C, x, z), real = Ask(w, C, C, x, z);
                    if (copied != real && differ++ == 0)
                        example = "layout " + l + ": (" + C + "," + C + ") -> (" + x + "," + z + "): model " + copied + ", game " + real;
                }
        }
        return (asked, differ, example);
    }

    private static int Main(string[] args)
    {
        string bad = Calibrate();
        if (bad != null)
        {
            Console.WriteLine("LOS WITNESS CALIBRATION FAILED: " + bad);
            return 2;
        }
        Console.WriteLine("LOS WITNESS CALIBRATED: wall and closed door block Verse.GenSight.LineOfSight, open ground does not");
        var s = Sweep(2000, 20261126);
        Console.WriteLine("LOS SWEEP: " + s.differ + " of " + s.asked + " sight lines differ from Verse.GenSight.LineOfSight (2000 seeded layouts)");
        if (s.example != null) Console.WriteLine("    e.g. " + s.example);
        KnockbackMap.LosWitness = Ask;
        int rc = KnockbackMap.RunMap(args);
        return rc != 0 || s.differ != 0 ? 1 : 0;
    }
}
