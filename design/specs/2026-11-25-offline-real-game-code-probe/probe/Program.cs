using System; using System.Linq; using Verse; using RimWorld;
static class P {
  static int ok, bad; static ThingDef wallDef;
  static void T(string name, Func<string> f) {
    try { Console.WriteLine("RUNS   " + name + " -> " + f()); ok++; }
    catch (Exception e) { var x = e; while (x.InnerException != null) x = x.InnerException;
      Console.WriteLine("THROWS " + name + " -> " + x.GetType().Name + ": " + (x.Message ?? "").Split('\n')[0]); bad++; }
  }
  static void Main() {
    T("IntVec3 arithmetic", () => (new IntVec3(3,0,4) + new IntVec3(1,0,1)).ToString());
    T("GenSight.PointsOnLineOfSight", () => GenSight.PointsOnLineOfSight(new IntVec3(0,0,0), new IntVec3(7,0,3)).Count().ToString());
    T("GenRadial.RadialCellsAround r=5", () => GenRadial.RadialCellsAround(new IntVec3(10,0,10), 5f, true).Count().ToString());
    T("Rand seeded", () => { Rand.PushState(42); var v = Rand.Range(0, 1000); Rand.PopState(); return v.ToString(); });
    T("CellRect.ExpandedBy", () => CellRect.CenteredOn(new IntVec3(5,0,5), 2).ExpandedBy(1).Area.ToString());
    T("GenMath.LerpDouble", () => GenMath.LerpDouble(0, 10, 0, 100, 2.5f).ToString());
    T("UnityEngine.Mathf.Sqrt", () => UnityEngine.Mathf.Sqrt(2f).ToString());
    T("UnityEngine.Vector3 ops", () => (new UnityEngine.Vector3(1,2,3) * 2f).magnitude.ToString());
    T("UnityEngine.Mathf.PerlinNoise (native)", () => UnityEngine.Mathf.PerlinNoise(0.3f, 0.7f).ToString());
    T("UnityEngine.Time.realtimeSinceStartup (native)", () => UnityEngine.Time.realtimeSinceStartup.ToString());
    Map map = null;
    T("new Map()", () => { map = new Map(); return "made"; });
    T("map.info.Size = 50x50", () => { map.info.Size = new IntVec3(50,1,50); return map.Size.ToString(); });
    T("map.cellIndices", () => { map.cellIndices = new CellIndices(map); return map.cellIndices.NumGridCells.ToString(); });
    T("new EdificeGrid(map)", () => { map.edificeGrid = new EdificeGrid(map); return "made"; });
    T("GenSight.LineOfSight on an empty 50x50 shell", () => GenSight.LineOfSight(new IntVec3(2,0,2), new IntVec3(40,0,30), map).ToString());
    T("hand-made wall ThingDef, uninitialized object (fillPercent 1)", () => { wallDef = (ThingDef)System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(typeof(ThingDef)); wallDef.defName = "ProbeWall"; wallDef.category = ThingCategory.Building; wallDef.fillPercent = 1f; wallDef.size = new IntVec2(1,1); wallDef.thingClass = typeof(Building); return wallDef.Fillage.ToString(); });
    T("new Building { def }, Position, edificeGrid.Register", () => { var b = (Building)System.Runtime.CompilerServices.RuntimeHelpers.GetUninitializedObject(typeof(Building)); b.def = wallDef; b.Position = new IntVec3(20,0,15); map.edificeGrid.Register(b); return (map.edificeGrid[new IntVec3(20,0,15)] != null).ToString(); });
    T("GenSight.LineOfSight through the wall (want False)", () => GenSight.LineOfSight(new IntVec3(10,0,15), new IntVec3(30,0,15), map).ToString());
    T("GenSight.LineOfSight beside the wall (want True)", () => GenSight.LineOfSight(new IntVec3(10,0,18), new IntVec3(30,0,18), map).ToString());
    T("map.ConstructComponents()", () => { map.ConstructComponents(); return "made"; });
    T("DefDatabase<ThingDef>.AllDefsListForReading.Count (no load)", () => DefDatabase<ThingDef>.AllDefsListForReading.Count.ToString());
    T("ThingMaker.MakeThing(null def)", () => ThingMaker.MakeThing(ThingDefOf.Wall).ToString());
    T("Find.TickManager (no game)", () => Find.TickManager.TicksGame.ToString());
    Console.WriteLine("SUMMARY runs " + ok + " throws " + bad);
  }
}
