using System.Collections.Generic;
using Verse;

namespace RimMandrake.Miasma
{
    // MIASMA_FLOTSAM_YARD_1: "everything the rivers carry that doesn't rot washes into the roots" (sheet §7).
    // Free-tier: only vanilla goods and our own plants. A MapComponent (the engine instantiates every subclass on
    // every map, so no GenStepDef/patch is needed and old saves pick it up):
    //  - seeds a first scattering on the first tick of a Miasma map;
    //  - restocks whenever the shared gradient axis reports a NEW surge recede finished
    //    (RM_MapComponent_GradientAxis.LastRecedeCompletedTick, read by reflection: the shared
    //    EnvironmentalHazards assembly is not referenced from here).
    // Placement: standable, empty cells within 2 of a root-line plant (mangals / thrannock), so never dry inland ground.
    public class RM_MapComponent_FlotsamYard : MapComponent
    {
        private static readonly string[] RootPlants = { "RM_Thessamor", "RM_Brelloch", "RM_Thrannock" };
        // def, weight, stack range
        private static readonly object[][] Table =
        {
            new object[] { "Steel", 4f, 8, 25 },
            new object[] { "WoodLog", 4f, 10, 30 },
            new object[] { "Cloth", 3f, 10, 25 },
            new object[] { "ComponentIndustrial", 1f, 1, 2 },
        };

        private bool seeded;
        private int lastRecedeSeen = -1;
        private List<Thing> placed = new List<Thing>();

        public RM_MapComponent_FlotsamYard(Map map) : base(map) { }

        public bool IsMiasma => map.Biome != null && map.Biome.defName == "RM_Miasma";
        public int PlacedCount { get { Prune(); return placed.Count; } }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % 250 != 0 || !IsMiasma || !RM_MiasmaSettings.flotsamEnabled) return;
            // seed once, then restock after each recede: RM_MiasmaKernel.FlotsamStep (offline-fuzzed)
            int stacks = RM_MiasmaKernel.FlotsamStep(ref seeded, ref lastRecedeSeen, ReadRecedeTick());
            if (stacks > 0) Place(stacks);
        }

        private int ReadRecedeTick()
        {
            foreach (MapComponent mc in map.components)
            {
                if (mc.GetType().Name != "RM_MapComponent_GradientAxis") continue;
                System.Reflection.PropertyInfo p = mc.GetType().GetProperty("LastRecedeCompletedTick");
                if (p != null) return (int)p.GetValue(mc, null);
            }
            return -1;
        }

        private void Prune()
        {
            placed.RemoveAll(t => t == null || t.Destroyed || !t.Spawned);
        }

        // Returns the number of stacks spawned.
        public int Place(int baseStacks)
        {
            Prune();
            int want = RM_MiasmaKernel.FlotsamWant(baseStacks, RM_MiasmaSettings.flotsamAmount, placed.Count);
            if (want <= 0) return 0;
            List<IntVec3> cells = RootLineCells();
            if (cells.Count == 0) return 0;
            cells.Shuffle();
            int made = 0;
            for (int i = 0; i < cells.Count && made < want; i++)
            {
                object[] row = Pick();
                ThingDef def = row != null ? DefDatabase<ThingDef>.GetNamedSilentFail((string)row[0]) : null;
                if (def == null) continue;
                Thing t = ThingMaker.MakeThing(def);
                t.stackCount = UnityEngine.Mathf.Min(def.stackLimit, Rand.RangeInclusive((int)row[2], (int)row[3]));
                if (GenPlace.TryPlaceThing(t, cells[i], map, ThingPlaceMode.Direct))
                {
                    placed.Add(t);
                    made++;
                }
                else t.Destroy();
            }
            return made;
        }

        private static object[] Pick()
        {
            var weights = new List<float>();
            foreach (object[] r in Table) weights.Add((float)r[1]);
            return Table[RM_MiasmaKernel.FlotsamPick(weights, Rand.Value)];
        }

        public List<IntVec3> RootLineCells()
        {
            HashSet<IntVec3> set = new HashSet<IntVec3>();
            foreach (string name in RootPlants)
            {
                ThingDef pd = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (pd == null) continue;
                foreach (Thing plant in map.listerThings.ThingsOfDef(pd))
                {
                    foreach (IntVec3 c in GenRadial.RadialCellsAround(plant.Position, 2f, true))
                    {
                        if (c.InBounds(map) && c.Walkable(map) && c.GetEdifice(map) == null && c.GetFirstItem(map) == null)
                            set.Add(c);
                    }
                }
            }
            return new List<IntVec3>(set);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref seeded, "seeded", false);
            Scribe_Values.Look(ref lastRecedeSeen, "lastRecedeSeen", -1);
            Scribe_Collections.Look(ref placed, "placed", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (placed == null) placed = new List<Thing>();
                placed.RemoveAll(t => t == null);
            }
        }
    }
}
