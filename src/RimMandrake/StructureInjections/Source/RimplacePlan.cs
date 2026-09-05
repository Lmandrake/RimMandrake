using System.Collections.Generic;
using System.IO;

namespace RimMandrake.StructureInjections
{
    // Reads the flat runtime format `rimplace.plan.compile_flat()` emits
    // (src/RimMandrake/Utils/rimplace/plan.py). Deliberately NOT JSON:
    // RimWorldWin64_Data/Managed ships no JSON library, so this is plain
    // StreamReader + string.Split, matching the format's own design intent.
    //
    // One directive per line, TAB-separated, "#" lines ignored:
    //   FOOTPRINT   x  z  w  h
    //   CLEAR       x  z  w  h  mode(all|soft)
    //   FOUNDATION  x  z  defName
    //   TERRAIN     x  z  defName
    //   THING       defName  x  z  rot  stuff-or-dash
    //   RUN         x  z  dir(N|E|S|W)  defName  stuff-or-dash
    //   ROOF        x  z  defName
    //   PAINT       x  z  colorDefName
    //   FLOORCOLOR  x  z  colorDefName
    //   PAWN        kindDef  x  z  faction  state(alive|dead|dessicated|skeleton)
    //
    // Sections are already ordered by the compiler (CLEAR first - E1 - then
    // foundation, terrain, things, RUN, roof, paint, floor color, PAWN last)
    // to match the order the live bridge path (rimplace.plan.compile_calls)
    // proved necessary — this reader preserves that order and does not re-sort.
    public sealed class PlanThing
    {
        public string DefName;
        public int X;
        public int Z;
        public int Rot;
        public string Stuff; // null if the plan wrote "-"
    }

    public sealed class PlanCell
    {
        public int X;
        public int Z;
        public string DefName;
    }

    // RIMPLACE_ENGINE_DELTAS_1 E1.
    public sealed class PlanClear
    {
        public int X, Z, W, H;
        public string Mode;   // "all" | "soft"
    }

    // E2.
    public sealed class PlanRun
    {
        public int X, Z;
        public string Dir;    // "N" | "E" | "S" | "W"
        public string DefName;
        public string Stuff;  // null if the plan wrote "-"
    }

    // E3.
    public sealed class PlanPawn
    {
        public string KindDef;
        public int X, Z;
        public string Faction;  // "wild" | a FactionDef defName | "player" (refused upstream, never authored)
        public string State;    // "alive" | "dead" | "dessicated" | "skeleton"
    }

    public sealed class RimplacePlan
    {
        public int FootprintX, FootprintZ, FootprintW, FootprintH;
        public bool HasFootprint;

        public readonly List<PlanCell> Foundation = new List<PlanCell>();
        public readonly List<PlanCell> Terrain = new List<PlanCell>();
        public readonly List<PlanThing> Things = new List<PlanThing>();
        public readonly List<PlanCell> Roof = new List<PlanCell>();
        public readonly List<PlanCell> Paint = new List<PlanCell>();
        public readonly List<PlanCell> FloorColor = new List<PlanCell>();
        public readonly List<PlanClear> Clears = new List<PlanClear>();
        public readonly List<PlanRun> Runs = new List<PlanRun>();
        public readonly List<PlanPawn> Pawns = new List<PlanPawn>();

        // E6: "make the GenStep Log.Warning once per unknown directive it
        // skips (currently a silent no-op)". The parser has no Log access of
        // its own reason to reach for (kept dependency-free of Verse on
        // purpose - it is plain StreamReader/string.Split), so it records
        // what it could not read and the CALLER (which already imports
        // Verse) does the warning - one entry per distinct unknown verb,
        // with a count, not one line per line.
        public readonly Dictionary<string, int> UnknownDirectives = new Dictionary<string, int>();

        public static RimplacePlan Parse(string path)
        {
            var plan = new RimplacePlan();
            foreach (var raw in File.ReadAllLines(path))
            {
                var line = raw.TrimEnd();
                if (line.Length == 0 || line[0] == '#') continue;
                var f = line.Split('\t');
                switch (f[0])
                {
                    case "FOOTPRINT":
                        plan.FootprintX = int.Parse(f[1]);
                        plan.FootprintZ = int.Parse(f[2]);
                        plan.FootprintW = int.Parse(f[3]);
                        plan.FootprintH = int.Parse(f[4]);
                        plan.HasFootprint = true;
                        break;
                    case "CLEAR":
                        plan.Clears.Add(new PlanClear
                        {
                            X = int.Parse(f[1]),
                            Z = int.Parse(f[2]),
                            W = int.Parse(f[3]),
                            H = int.Parse(f[4]),
                            Mode = f[5],
                        });
                        break;
                    case "FOUNDATION":
                        plan.Foundation.Add(new PlanCell { X = int.Parse(f[1]), Z = int.Parse(f[2]), DefName = f[3] });
                        break;
                    case "TERRAIN":
                        plan.Terrain.Add(new PlanCell { X = int.Parse(f[1]), Z = int.Parse(f[2]), DefName = f[3] });
                        break;
                    case "THING":
                        plan.Things.Add(new PlanThing
                        {
                            DefName = f[1],
                            X = int.Parse(f[2]),
                            Z = int.Parse(f[3]),
                            Rot = int.Parse(f[4]),
                            Stuff = f[5] == "-" ? null : f[5],
                        });
                        break;
                    case "RUN":
                        plan.Runs.Add(new PlanRun
                        {
                            X = int.Parse(f[1]),
                            Z = int.Parse(f[2]),
                            Dir = f[3],
                            DefName = f[4],
                            Stuff = f[5] == "-" ? null : f[5],
                        });
                        break;
                    case "ROOF":
                        plan.Roof.Add(new PlanCell { X = int.Parse(f[1]), Z = int.Parse(f[2]), DefName = f[3] });
                        break;
                    case "PAINT":
                        plan.Paint.Add(new PlanCell { X = int.Parse(f[1]), Z = int.Parse(f[2]), DefName = f[3] });
                        break;
                    case "FLOORCOLOR":
                        plan.FloorColor.Add(new PlanCell { X = int.Parse(f[1]), Z = int.Parse(f[2]), DefName = f[3] });
                        break;
                    case "PAWN":
                        plan.Pawns.Add(new PlanPawn
                        {
                            KindDef = f[1],
                            X = int.Parse(f[2]),
                            Z = int.Parse(f[3]),
                            Faction = f[4],
                            State = f[5],
                        });
                        break;
                    default:
                        // An unknown directive is recorded, not silently
                        // dropped - RIMPLACE_ENGINE_DELTAS_1 E6: an old DLL
                        // replaying a v2 plan must fail LOUD (the caller logs
                        // this), never skip a CLEAR/RUN/PAWN with no trace.
                        plan.UnknownDirectives.TryGetValue(f[0], out var n);
                        plan.UnknownDirectives[f[0]] = n + 1;
                        break;
                }
            }
            return plan;
        }
    }
}
