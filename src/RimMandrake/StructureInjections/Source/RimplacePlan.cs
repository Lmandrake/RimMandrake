using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace RimMandrake.StructureInjections
{
    // Reads the flat runtime format `rimplace.plan.compile_flat()` emits
    // (src/RimMandrake/Utils/rimplace/plan.py). Deliberately NOT JSON:
    // RimWorldWin64_Data/Managed ships no JSON library, so this is plain
    // StreamReader + string.Split, matching the format's own design intent.
    //
    // One directive per line, TAB-separated, "#" lines ignored:
    //   FOOTPRINT   x  z  w  h
    //   FOUNDATION  x  z  defName
    //   TERRAIN     x  z  defName
    //   THING       defName  x  z  rot  stuff-or-dash
    //   ROOF        x  z  defName
    //   PAINT       x  z  colorDefName
    //   FLOORCOLOR  x  z  colorDefName
    //
    // Sections are already ordered by the compiler (foundation, terrain,
    // things, roof, paint, floor color) to match the order the live bridge
    // path (rimplace.plan.compile_calls) proved necessary — this reader
    // preserves that order and does not re-sort.
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
                    case "ROOF":
                        plan.Roof.Add(new PlanCell { X = int.Parse(f[1]), Z = int.Parse(f[2]), DefName = f[3] });
                        break;
                    case "PAINT":
                        plan.Paint.Add(new PlanCell { X = int.Parse(f[1]), Z = int.Parse(f[2]), DefName = f[3] });
                        break;
                    case "FLOORCOLOR":
                        plan.FloorColor.Add(new PlanCell { X = int.Parse(f[1]), Z = int.Parse(f[2]), DefName = f[3] });
                        break;
                    // an unknown directive is a forward-compat no-op, not a
                    // parse failure — the compiler's own header is versioned
                    // ("# rimplace flat plan v1") for exactly this reason.
                }
            }
            return plan;
        }

        public IEnumerable<string> DefNames()
        {
            foreach (var c in Foundation) yield return c.DefName;
            foreach (var c in Terrain) yield return c.DefName;
            foreach (var t in Things)
            {
                yield return t.DefName;
                if (t.Stuff != null) yield return t.Stuff;
            }
            foreach (var c in Roof) yield return c.DefName;
        }
    }
}
