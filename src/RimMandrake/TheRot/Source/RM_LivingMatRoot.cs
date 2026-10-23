using System.Collections.Generic;
using System.Linq;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TheRot
{
    // ════════════════════════════════════════════════════════════════════
    // ROT_WARM_MAT_BUILD_WORKS_FOR_FOOD — the Rot's warm mat, made portable.
    // Spec: design/RimMandrake/rot_warm_mat_portable_2026-10-22.md.
    //
    // OWNER RULING 2026-10-22 (card write-in, verbatim): "Make it work anywhere but it not naturally occurs in the
    // rot. Can be installed on the gravship to help with heating in cold places as a reward. Needs food. Would grow
    // in other biomes if tended with food. Rot doesn't require feeding due to sharing lore."
    // This is an owner-ordered exception to "biome mechanics are promised inside OUR biomes only" (2026-10-15).
    //
    // The root is a HEART, not a heater: it warms nothing itself. It feeds the mat floor around it, and a proper
    // room whose cells are >= requiredFloorFraction mat warms exactly like a Rot mat room — same target
    // min(outdoor + offset, maxRoomTemperature = 21 C), same ramp offset / ThermalPowerDivisor per 250 ticks x cells
    // (numbers and their calibration: RM_MapComponent_WarmGround's header). "Helps a lot, not trivialises" is
    // inherited unchanged, never re-tuned here.
    //
    //   off the Rot  eats upkeepPerDay food (vanilla CompRefuelable, consumeFuelOnlyWhenUsed, so the ordinary refuel
    //                work feeds it); fed and >= spreadMinFuelPercent full, lays one cell of matTerrain per
    //                spreadIntervalTicks at spreadCost food; empty: heat stops at once, and after starveGraceTicks the
    //                mat it GREW dies back one cell per dieBackIntervalTicks (RemoveTopLayer: the ground beneath
    //                returns). It never removes mat it did not grow, and never lays mat over a built floor.
    //   in the Rot   eats nothing and spreads free ("joined to the Rot's network" — the shared-body lore of
    //                RM_KinMendingNetwork). Heating there is the biome's own RM_MapComponent_WarmGround's job.
    //   double heat  the root pushes no heat where RM_MapComponent_WarmGround already runs (the Rot, or a cross-biome
    //                opt-in map), and only one root heats any one room per sweep.
    //
    // The clocks (eat / spread / die back) and the heat step are RM_TheRotKernel.MatRootStep / MatHeatStep, fuzzed offline
    // (selftest_therot_fuzz.py --fuzz-only mat); this comp only reads the game and applies the decisions.
    //
    // Grown cells are saved as absolute cells and CLEARED on any non-load respawn (reinstall, gravship landing): the
    // mat that travelled stays and still counts toward a room, but no longer dies back. Rotating a landing ship would
    // otherwise point the list at the wrong cells, and dying back the wrong cells would eat a floor the root never
    // grew.
    // ════════════════════════════════════════════════════════════════════

    public class CompProperties_RM_LivingMatRoot : CompProperties
    {
        /// <summary>What the root lays when it spreads (a layerable floor, so dying back uncovers the ground).</summary>
        public TerrainDef matTerrain;
        /// <summary>Terrains that count as mat for the room fraction (matTerrain always counts too).</summary>
        public List<TerrainDef> warmTerrains = new List<TerrainDef>();
        public float requiredFloorFraction = 0.6f;
        public float maxRoomTemperature = 21f;
        public float spreadRadius = 6f;
        // PROVISIONAL tuning (FOUNDRY provisional-numbers rule, 2026-10-03); the appetite setting scales the two costs.
        public float upkeepPerDay = 3f;
        public float spreadCost = 1f;
        public int spreadIntervalTicks = 2500;
        public float spreadMinFuelPercent = 0.5f;
        public int starveGraceTicks = 120000;
        public int dieBackIntervalTicks = 5000;

        public CompProperties_RM_LivingMatRoot()
        {
            compClass = typeof(RM_CompLivingMatRoot);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (matTerrain == null)
            {
                yield return "CompProperties_RM_LivingMatRoot has no matTerrain: the root can never spread.";
            }
            else if (!matTerrain.layerable)
            {
                yield return "CompProperties_RM_LivingMatRoot.matTerrain " + matTerrain.defName + " is not layerable: dying back could not uncover the ground.";
            }
            if (requiredFloorFraction <= 0f || requiredFloorFraction > 1f)
            {
                yield return "CompProperties_RM_LivingMatRoot.requiredFloorFraction must be >0 and <=1.";
            }
            if (parentDef.tickerType != TickerType.Rare)
            {
                yield return "CompProperties_RM_LivingMatRoot needs tickerType Rare (it sweeps on CompTickRare).";
            }
            if (parentDef.GetCompProperties<CompProperties_Refuelable>() == null)
            {
                yield return "CompProperties_RM_LivingMatRoot needs a CompProperties_Refuelable to hold its food.";
            }
        }
    }

    public class RM_CompLivingMatRoot : ThingComp
    {
        private const int Sweep = 250;                  // CompTickRare cadence == RM_MapComponent_WarmGround's interval
        private const float ThermalPowerDivisor = 36f;  // == RM_MapComponent_WarmGround.ThermalPowerDivisor

        private static readonly Dictionary<Room, int> heatedAt = new Dictionary<Room, int>();

        public List<IntVec3> grown = new List<IntVec3>();
        public RM_TheRotKernel.MatRootState clocks;
        public string lastStatus = "";

        public CompProperties_RM_LivingMatRoot Props => (CompProperties_RM_LivingMatRoot)props;
        private CompRefuelable Food => parent.TryGetComp<CompRefuelable>();

        public bool InRot => parent.Spawned && RM_TheRotFront.IsRotBiome(parent.Map.Biome);

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!respawningAfterLoad)
            {
                grown.Clear();
                clocks = new RM_TheRotKernel.MatRootState();
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Collections.Look(ref grown, "grown", LookMode.Value);
            Scribe_Values.Look(ref clocks.starvingTicks, "starvingTicks", 0);
            Scribe_Values.Look(ref clocks.spreadTimer, "spreadTimer", 0);
            Scribe_Values.Look(ref clocks.dieBackTimer, "dieBackTimer", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && grown == null)
            {
                grown = new List<IntVec3>();
            }
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            DoSweep(false);
        }

        /// <summary>One 250-tick sweep. <paramref name="hurry"/> treats every timer as elapsed (proof calls only).</summary>
        public void DoSweep(bool hurry)
        {
            if (!parent.Spawned)
            {
                return;
            }
            if (!RM_TheRotSettings.theRotEnabled || !RM_TheRotSettings.portableWarmMat)
            {
                lastStatus = "dormant (switched off in Mod Settings)";
                return;
            }

            bool inRot = InRot;
            CompRefuelable food = Food;
            float appetite = Mathf.Max(0f, RM_TheRotSettings.portableWarmMatAppetite);
            RM_TheRotKernel.MatRootSweep d = RM_TheRotKernel.MatRootStep(ref clocks, Sweep, hurry, inRot,
                food?.Fuel ?? 0f, food?.Props.fuelCapacity ?? 0f, Props.upkeepPerDay, appetite, Props.spreadMinFuelPercent,
                Props.spreadIntervalTicks, Props.starveGraceTicks, Props.dieBackIntervalTicks,
                RM_TheRotSettings.portableWarmMatSpread, RM_TheRotSettings.portableWarmMatDieBack);
            if (d.eat > 0f && food != null)
            {
                food.ConsumeFuel(d.eat);
            }
            bool fed = d.fed;
            if (d.spread && TrySpreadOne() && !inRot && food != null)
            {
                food.ConsumeFuel(Props.spreadCost * appetite);
            }
            if (d.dieBack)
            {
                DieBackOne();
            }

            lastStatus = fed ? Heat(inRot, hurry) : "starving: not heating";
        }

        private bool IsMat(TerrainDef t)
        {
            return t != null && (t == Props.matTerrain || (Props.warmTerrains != null && Props.warmTerrains.Contains(t)));
        }

        /// <summary>True when the map's own warm-ground mechanism already heats mat rooms here.</summary>
        private bool BiomeHeatsMat(Map map)
        {
            return RM_EnvironmentalHazardsSettings.warmGroundEnabled
                && RM_KitFronts.Extension<RM_WarmGroundExtension>(map.Biome) != null
                && RM_KitFronts.Enabled("warmGround", map.Biome);
        }

        private string Heat(bool inRot, bool hurry)
        {
            Map map = parent.Map;
            if (inRot || BiomeHeatsMat(map))
            {
                return inRot ? "joined to the Rot's network: the living ground feeds it" : "fed; this ground's own warmth heats the room";
            }
            Room room = parent.GetRoom();
            if (room == null || room.Dereferenced || room.UsesOutdoorTemperature || !room.ProperRoom || room.IsDoorway)
            {
                return "fed; not heating (outdoors or not a proper room)";
            }
            int cells = room.CellCount;
            if (cells <= 0)
            {
                return "fed; not heating (empty room)";
            }
            int mat = 0;
            foreach (IntVec3 c in room.Cells)
            {
                if (IsMat(map.terrainGrid.TerrainAt(c)))
                {
                    mat++;
                }
            }
            if (!RM_TheRotKernel.MatRoomQualifies(mat, cells, Props.requiredFloorFraction))
            {
                return "fed; mat covers " + mat + " of " + cells + " cells (" + Mathf.CeilToInt(cells * Props.requiredFloorFraction) + " needed to heat)";
            }

            float offset = RM_EnvironmentalHazardsSettings.warmGroundOffsetCelsius * Mathf.Max(0f, RM_TheRotSettings.portableWarmMatWarmth);
            float outdoor = map.mapTemperature.OutdoorTemp;
            float target = RM_TheRotKernel.MatTarget(outdoor, offset, Props.maxRoomTemperature);
            float step = RM_TheRotKernel.MatHeatStep(outdoor, room.Temperature, offset, Props.maxRoomTemperature, ThermalPowerDivisor);
            if (step <= 0f)
            {
                return "fed; room already at the mat's " + target.ToStringTemperature("F0");
            }
            int now = Find.TickManager.TicksGame;
            // A proof sweep runs many sweeps inside one tick; the one-root-per-room-per-tick guard would stop all but the first.
            // GPT deep review 2026-10-22 #8: roots tick on their own rare-tick phases, so "same tick" let two roots in one room
            // both push (twice the warming rate); one push per room per sweep interval
            if (!hurry && heatedAt.TryGetValue(room, out int at) && now - at < Sweep)
            {
                return "fed; another root already warms this room";
            }
            heatedAt[room] = now;
            if (heatedAt.Count > 64)
            {
                // Only this tick's entries mean anything; dropping the rest also releases rooms of an unloaded game.
                foreach (Room stale in heatedAt.Where(kv => now - kv.Value >= Sweep).Select(kv => kv.Key).ToList())
                {
                    heatedAt.Remove(stale);
                }
            }
            room.PushHeat(step * cells);
            return "fed; warming this room toward " + target.ToStringTemperature("F0");
        }

        private bool CanTake(Map map, IntVec3 c, Room room)
        {
            if (!c.InBounds(map) || c.Fogged(map) || c.GetRoom(map) != room)
            {
                return false;
            }
            TerrainGrid g = map.terrainGrid;
            TerrainDef t = g.TerrainAt(c);
            if (t == null || IsMat(t) || t.IsWater || t.passability == Traversability.Impassable || g.TempTerrainAt(c) != null)
            {
                return false;
            }
            // Bare ground (not a built floor), or bare gravship substructure (foundation with nothing layered on it).
            bool bareSubstructure = g.FoundationAt(c) != null && g.UnderTerrainAt(c) == null;
            bool bareGround = g.FoundationAt(c) == null && !t.layerable;
            if (!bareSubstructure && !bareGround)
            {
                return false;
            }
            Building edifice = c.GetEdifice(map);
            return edifice == null || edifice == parent || edifice.def.passability != Traversability.Impassable;
        }

        private bool Touches(Map map, IntVec3 c)
        {
            for (int i = 0; i < 4; i++)
            {
                IntVec3 n = c + GenAdj.CardinalDirections[i];
                if (n == parent.Position || (n.InBounds(map) && IsMat(map.terrainGrid.TerrainAt(n))))
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>Lays one mat cell next to the root or its mat, inside its room and radius.</summary>
        public bool TrySpreadOne()
        {
            Map map = parent.Map;
            if (Props.matTerrain == null)
            {
                return false;
            }
            Room room = parent.GetRoom();
            if (room == null)
            {
                return false;
            }
            List<IntVec3> options = new List<IntVec3>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(parent.Position, Props.spreadRadius, true))
            {
                if (CanTake(map, c, room) && (c == parent.Position || Touches(map, c)))
                {
                    options.Add(c);
                }
            }
            if (options.Count == 0)
            {
                return false;
            }
            // Nearest first keeps the mat a solid patch around its root rather than a scatter.
            IntVec3 pick = options.MinBy(c => c.DistanceToSquared(parent.Position));
            map.terrainGrid.SetTerrain(pick, Props.matTerrain);
            grown.Add(pick);
            return true;
        }

        /// <summary>Uncovers one cell of mat this root grew (newest first). Never touches mat it did not grow.</summary>
        public bool DieBackOne()
        {
            Map map = parent.Map;
            while (grown.Count > 0)
            {
                IntVec3 c = grown[grown.Count - 1];
                grown.RemoveAt(grown.Count - 1);
                if (c.InBounds(map) && map.terrainGrid.TopTerrainAt(c) == Props.matTerrain && map.terrainGrid.UnderTerrainAt(c) != null)
                {
                    map.terrainGrid.RemoveTopLayer(c, false);
                    return true;
                }
            }
            return false;
        }

        public override string CompInspectStringExtra()
        {
            if (!parent.Spawned)
            {
                return null;
            }
            string s = "Living mat: " + (lastStatus.NullOrEmpty() ? "settling in" : lastStatus) + ". Grown here: " + grown.Count + " cells.";
            if (!InRot && Food != null && !Food.HasFuel && RM_TheRotSettings.portableWarmMatDieBack)
            {
                int left = Props.starveGraceTicks - clocks.starvingTicks;
                s += left > 0 ? "\nStarving: its mat starts dying back in " + left.ToStringTicksToPeriod() + "." : "\nStarving: its mat is dying back.";
            }
            return s;
        }
    }

    /// <summary>Deterministic reads/triggers for jawa/static_call (ROT_WARM_MAT_BUILD_WORKS_FOR_FOOD).</summary>
    public static class RM_LivingMatRootProof
    {
        private static ThingDef RootDef => DefDatabase<ThingDef>.GetNamedSilentFail("RM_LivingMatRoot");

        private static List<RM_CompLivingMatRoot> Roots(Map map)
        {
            return RootDef == null ? new List<RM_CompLivingMatRoot>()
                : map.listerThings.ThingsOfDef(RootDef).Select(t => t.TryGetComp<RM_CompLivingMatRoot>()).Where(c => c != null).ToList();
        }

        /// <summary>Builds a sealed, roofed 5x5 wooden room on open ground and sets a full root at its centre.
        /// "STAGED at x,z | rot R | food F" or "REFUSED: why".</summary>
        public static string ProofStage()
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no map";
            if (RootDef == null) return "REFUSED: no ThingDef RM_LivingMatRoot";
            for (int attempt = 0; attempt < 300; attempt++)
            {
                IntVec3 centre = CellFinder.RandomClosewalkCellNear(map.Center, map, 40);
                CellRect outer = CellRect.CenteredOn(centre, 3);
                if (!outer.InBounds(map) || outer.Cells.Any(c => !c.Standable(map) || c.Fogged(map) || c.GetEdifice(map) != null
                        || map.terrainGrid.TerrainAt(c).IsWater || map.terrainGrid.TerrainAt(c).layerable || c.Roofed(map)
                        || c.GetThingList(map).Any(t => t is Pawn)))
                {
                    continue;
                }
                foreach (IntVec3 c in outer.Cells)
                {
                    foreach (Thing t in c.GetThingList(map).ToList())
                    {
                        if (t.def.category == ThingCategory.Plant || t.def.category == ThingCategory.Item || t.def.category == ThingCategory.Filth)
                        {
                            t.Destroy(DestroyMode.Vanish);
                        }
                    }
                    if (outer.IsOnEdge(c))
                    {
                        GenSpawn.Spawn(ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.WoodLog), c, map).SetFaction(Faction.OfPlayer);
                    }
                    map.roofGrid.SetRoof(c, RoofDefOf.RoofConstructed);
                }
                Thing root = ThingMaker.MakeThing(RootDef);
                GenSpawn.Spawn(root, centre, map).SetFaction(Faction.OfPlayer);
                CompRefuelable food = root.TryGetComp<CompRefuelable>();
                food?.Refuel(food.Props.fuelCapacity);
                return "STAGED at " + centre.x + "," + centre.z + " | rot " + RM_TheRotFront.IsRotBiome(map.Biome) + " | food " + (food?.Fuel ?? -1f).ToString("0.0");
            }
            return "REFUSED: no open 7x7 patch of bare ground near the map centre";
        }

        /// <summary>Runs <paramref name="sweeps"/> hurried sweeps on every root on the current map. <paramref name="mode"/> "fed":
        /// topped up to full before every sweep (a tended root), "empty": drained first and left empty. Reports per root
        /// "ROOT i | rot R | food a->b ate E | grown g0->g1 | room T0->T1 (mat m/n) | outdoor O | status".</summary>
        public static string ProofSweeps(int sweeps, string mode)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no map";
            List<RM_CompLivingMatRoot> roots = Roots(map);
            if (roots.Count == 0) return "REFUSED: no RM_LivingMatRoot on the current map (ProofStage first)";
            List<string> rows = new List<string>();
            for (int i = 0; i < roots.Count; i++)
            {
                RM_CompLivingMatRoot r = roots[i];
                CompRefuelable food = r.parent.TryGetComp<CompRefuelable>();
                if (mode == "empty" && food != null && food.HasFuel)
                {
                    food.ConsumeFuel(food.Fuel);
                }
                Room room = r.parent.GetRoom();
                float f0 = food?.Fuel ?? -1f;
                int g0 = r.grown.Count;
                float t0 = room?.Temperature ?? float.NaN;
                float ate = 0f;
                for (int s = 0; s < sweeps; s++)
                {
                    if (mode == "fed" && food != null)
                    {
                        food.Refuel(food.Props.fuelCapacity - food.Fuel);
                    }
                    float before = food?.Fuel ?? 0f;
                    r.DoSweep(true);
                    ate += before - (food?.Fuel ?? 0f);
                }
                room = r.parent.GetRoom();
                int mat = 0, cells = 0;
                if (room != null && !room.UsesOutdoorTemperature)
                {
                    foreach (IntVec3 c in room.Cells)
                    {
                        cells++;
                        TerrainDef t = map.terrainGrid.TerrainAt(c);
                        if (t == r.Props.matTerrain || r.Props.warmTerrains.Contains(t)) mat++;
                    }
                }
                rows.Add("ROOT " + i + " | rot " + r.InRot + " | food " + f0.ToString("0.00") + "->" + (food?.Fuel ?? -1f).ToString("0.00") + " ate " + ate.ToString("0.000")
                    + " | grown " + g0 + "->" + r.grown.Count + " | room " + t0.ToString("0.0") + "->" + (room?.Temperature ?? float.NaN).ToString("0.0")
                    + " (mat " + mat + "/" + cells + ") | outdoor " + map.mapTemperature.OutdoorTemp.ToString("0.0") + " | " + r.lastStatus);
            }
            return string.Join(" || ", rows);
        }
    }
}
