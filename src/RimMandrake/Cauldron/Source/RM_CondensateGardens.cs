using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Cauldron
{
    // ════════════════════════════════════════════════════════════════════
    // CAULDRON_GPT_ENRICHMENT_1 part 5 — Condensate Gardens, the slice with
    // a real anchor today: "nettles colonize poisoned shorelines".
    //
    // A plant def opts in with RM_CondensateHabitatExtension naming the
    // terrains whose SHORE it colonizes (land cells 8-adjacent to one of
    // them). Only plants on the map biome's own wild-plant roster
    // (CommonalityOfPlant > 0) take part, so this keys off the roster, never
    // a hard-coded biome defName — the campaign twin inherits it for free if
    // its roster carries the plant.
    //
    // Two passes, one rule:
    //   - MapGenerated(): every qualifying shore cell rolls mapgenChance once.
    //   - Ongoing: every intervalTicks, samplesPerInterval random cells are
    //     tried at colonizeChance — so a shore the vexxiss poisons later
    //     (RM_CompVexxissBehaviour) is colonized over the following days.
    //
    // The other three microhabitats (crystal flowers at stable taps, blood
    // bouquets at chronic leaks, giant toxic flowers at recent blowouts) are
    // keyed to vents/taps, which do not exist until CAULDRON_MECHANICS_BUILD_1
    // part 3 lands. NOT BUILT here: CAULDRON_VENT_ENRICHMENT_HOOKS_1.
    //
    // Gated by RM_CauldronSettings.condensateGardensEnabled.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CondensateHabitatExtension : DefModExtension
    {
        public List<TerrainDef> shoreOf = new List<TerrainDef>();
        public float mapgenChance = 0.25f;
        public float colonizeChance = 0.5f;
        public float spawnGrowthMin = 0.05f;
        public float spawnGrowthMax = 0.3f;

        // CAULDRON_VENT_ENRICHMENT_HOOKS_1: vent-keyed habitat. A plant with ventHabitat != None grows in a ring
        // ventMinRadius..ventRadius cells from every vent whose state matches (see RM_Building_CauldronVent.Matches).
        public RM_VentHabitat ventHabitat = RM_VentHabitat.None;
        public float ventMinRadius = 2.5f;
        public float ventRadius = 8f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if ((shoreOf == null || shoreOf.Count == 0) && ventHabitat == RM_VentHabitat.None)
                yield return "RM_CondensateHabitatExtension has neither shoreOf terrains nor a ventHabitat";
            if (ventHabitat != RM_VentHabitat.None && ventRadius <= ventMinRadius)
                yield return "RM_CondensateHabitatExtension ventRadius must exceed ventMinRadius";
        }
    }

    public class RM_MapComponent_CondensateGardens : MapComponent
    {
        // TUNED: one sweep of 40 random cells per in-game hour (2500 ticks).
        // On a 250x250 map a given shore cell is tried about once every
        // ~65 days, so a fresh poisoned shoreline greens over weeks, not hours.
        private const int IntervalTicks = 2500;
        private const int SamplesPerInterval = 40;
        private const int VentSamplesPerInterval = 12;

        private List<(ThingDef plant, RM_CondensateHabitatExtension ext)> cached;
        private BiomeDef cachedFor;

        public RM_MapComponent_CondensateGardens(Map map) : base(map) { }

        private List<(ThingDef, RM_CondensateHabitatExtension)> Participants()
        {
            if (cached != null && cachedFor == map.Biome) return cached;
            cachedFor = map.Biome;
            cached = new List<(ThingDef, RM_CondensateHabitatExtension)>();
            if (map.Biome == null) return cached;
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d.plant == null) continue;
                var ext = d.GetModExtension<RM_CondensateHabitatExtension>();
                if (ext == null) continue;
                if (map.Biome.CommonalityOfPlant(d) <= 0f) continue;
                cached.Add((d, ext));
            }
            return cached;
        }

        public override void MapGenerated()
        {
            if (!RM_CauldronSettings.condensateGardensEnabled) return;
            var parts = Participants();
            if (parts.Count == 0) return;
            foreach (IntVec3 c in map.AllCells)
                foreach (var (plant, ext) in parts)
                    if (TryColonize(c, plant, ext, ext.mapgenChance)) break;

            // Vents come first (one idempotent call: MapComponent order is not guaranteed), then their flowers.
            var ventComp = map.GetComponent<RM_MapComponent_CauldronVents>();
            if (ventComp == null || !RM_CauldronSettings.ventGardensEnabled) return;
            ventComp.EnsureGenerated();
            foreach (Thing t in ventComp.Vents())
            {
                var vent = t as RM_Building_CauldronVent;
                if (vent == null) continue;
                foreach (var (plant, ext) in parts)
                {
                    if (ext.ventHabitat == RM_VentHabitat.None || !vent.Matches(ext.ventHabitat)) continue;
                    foreach (IntVec3 c in GenRadial.RadialCellsAround(vent.Position, ext.ventRadius, false))
                        if (InVentRing(vent, c, ext)) TryPlant(c, plant, ext, ext.mapgenChance);
                }
            }
        }

        private static bool InVentRing(RM_Building_CauldronVent vent, IntVec3 c, RM_CondensateHabitatExtension ext)
        {
            return RM_VentKernel.InRing((c - vent.Position).LengthHorizontal, ext.ventMinRadius, ext.ventRadius);
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % IntervalTicks != 0) return;
            if (!RM_CauldronSettings.condensateGardensEnabled) return;
            var parts = Participants();
            if (parts.Count == 0) return;
            for (int i = 0; i < SamplesPerInterval; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                var (plant, ext) = parts.RandomElement();
                TryColonize(c, plant, ext, ext.colonizeChance);
            }

            // Vent flowers: a few samples per interval around a random vent, so a vent that has just blown
            // out (or a new leak) fills in over days.
            if (!RM_CauldronSettings.ventGardensEnabled) return;
            var ventComp = map.GetComponent<RM_MapComponent_CauldronVents>();
            if (ventComp == null) return;
            List<Thing> vents = ventComp.Vents();
            if (vents.Count == 0) return;
            for (int i = 0; i < VentSamplesPerInterval; i++)
            {
                var vent = vents.RandomElement() as RM_Building_CauldronVent;
                var (vplant, vext) = parts.RandomElement();
                if (vent == null || vext.ventHabitat == RM_VentHabitat.None || !vent.Matches(vext.ventHabitat)) continue;
                Vector2 off = Rand.InsideUnitCircle * vext.ventRadius;
                IntVec3 c = vent.Position + new IntVec3(Mathf.RoundToInt(off.x), 0, Mathf.RoundToInt(off.y));
                if (!c.InBounds(map) || !InVentRing(vent, c, vext)) continue;
                TryPlant(c, vplant, vext, vext.colonizeChance);
            }
        }

        private bool TryColonize(IntVec3 c, ThingDef plant, RM_CondensateHabitatExtension ext, float chance)
        {
            if (!IsShoreOf(c, ext)) return false;
            return TryPlant(c, plant, ext, chance);
        }

        private bool TryPlant(IntVec3 c, ThingDef plant, RM_CondensateHabitatExtension ext, float chance)
        {
            if (c.GetPlant(map) != null) return false;
            if (map.zoneManager.ZoneAt(c) != null) return false;
            if (!plant.CanEverPlantAt(c, map)) return false;   // PlantAllowed in Kernel/RM_YieldKernel.cs: no plant, no zone, plantable
            if (!Rand.Chance(chance)) return false;
            Plant p = (Plant)ThingMaker.MakeThing(plant);
            p.Growth = Rand.Range(ext.spawnGrowthMin, ext.spawnGrowthMax);
            GenSpawn.Spawn(p, c, map);
            return true;
        }

        private bool IsShoreOf(IntVec3 c, RM_CondensateHabitatExtension ext)
        {
            bool onNamed = ext.shoreOf.Contains(c.GetTerrain(map)); // in the water, not on its shore
            bool neighbour = false;
            if (!onNamed)
            {
                for (int i = 0; i < 8 && !neighbour; i++)
                {
                    IntVec3 n = c + GenAdj.AdjacentCells[i];
                    neighbour = n.InBounds(map) && ext.shoreOf.Contains(n.GetTerrain(map));
                }
            }
            return RM_YieldKernel.IsShore(onNamed, neighbour);
        }
    }
}
