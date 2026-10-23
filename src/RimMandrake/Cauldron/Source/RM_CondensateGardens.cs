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
    // The other three microhabitats (crystal flowers at stable vents, blood
    // bouquets at chronic leaks, giant toxic flowers at recent blowouts) ring
    // RM_Building_CauldronVent (CAULDRON_VENT_ENRICHMENT_HOOKS_1): a mapgen
    // pass that may replace wild non-tree plants in the ring (RM_VentKernel.
    // RingPlantAction), then a slow ongoing fill of empty ring cells.
    // ProofVentRings reads ring vs control density for validation.py.
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

        // What the mapgen vent-ring pass did on this map (read by ProofVentRings): 0 the map predates the ring fix (or no
        // mapgen ran), 1 the ring pass ran, 2 it was skipped (a gardens toggle off or no participant flowers).
        private int ringPassAtMapgen;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ringPassAtMapgen, "rmRingPassAtMapgen", 0);
        }

        public override void MapGenerated()
        {
            ringPassAtMapgen = 2;
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
            ringPassAtMapgen = 1;
            foreach (Thing t in ventComp.Vents())
            {
                var vent = t as RM_Building_CauldronVent;
                if (vent == null) continue;
                foreach (var (plant, ext) in parts)
                {
                    if (ext.ventHabitat == RM_VentHabitat.None || !vent.Matches(ext.ventHabitat)) continue;
                    foreach (IntVec3 c in GenRadial.RadialCellsAround(vent.Position, ext.ventRadius, false))
                        if (InVentRing(vent, c, ext)) TryPlant(c, plant, ext, ext.mapgenChance, mapgen: true);
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

        private bool TryPlant(IntVec3 c, ThingDef plant, RM_CondensateHabitatExtension ext, float chance, bool mapgen = false)
        {
            if (!c.InBounds(map)) return false;   // mapgen walks RadialCellsAround a vent near the edge (ventRadius 9 > 8-cell margin)
            Plant occupant = c.GetPlant(map);
            bool occupantIsVentFlower = occupant != null &&
                (occupant.def.GetModExtension<RM_CondensateHabitatExtension>()?.ventHabitat ?? RM_VentHabitat.None) != RM_VentHabitat.None;
            int act = RM_VentKernel.RingPlantAction(mapgen && ext.ventHabitat != RM_VentHabitat.None, occupant != null,
                occupant != null && occupant.def.plant.IsTree, occupantIsVentFlower);
            if (act == 0) return false;
            if (map.zoneManager.ZoneAt(c) != null) return false;
            // PlantAllowed in Kernel/RM_YieldKernel.cs: no plant, no zone, plantable. A wipe asks with the occupant ignored.
            if (!plant.CanEverPlantAt(c, map, canWipePlantsExceptTree: act == 2)) return false;
            if (!Rand.Chance(chance)) return false;
            if (act == 2) occupant.Destroy();
            Plant p = (Plant)ThingMaker.MakeThing(plant);
            p.Growth = Rand.Range(ext.spawnGrowthMin, ext.spawnGrowthMax);
            GenSpawn.Spawn(p, c, map);
            return true;
        }

        // validation.py vent_gardens.vent_flowers_ring_vs_control: per vent flower, how many of its cells stand in the ring
        // of a matching vent versus far from every vent (> ControlGap cells), over fertile cells only. One line per flower:
        // "ringPass=<0|1|2>; <def> vents=<n> ring=<count>/<cells> ctrl=<count>/<cells>; ..."; "no vents" / "no flowers"
        // when there is nothing to read.
        private const float ControlGap = 20f;

        public static string ProofVentRings(Map map)
        {
            if (map == null) return "no map";
            var comp = map.GetComponent<RM_MapComponent_CondensateGardens>();
            var ventComp = map.GetComponent<RM_MapComponent_CauldronVents>();
            List<Thing> vents = ventComp?.Vents();
            if (comp == null || vents == null || vents.Count == 0) return "no vents";
            var lines = new List<string> { "ringPass=" + comp.ringPassAtMapgen };
            foreach (var (plant, ext) in comp.Participants())
            {
                if (ext.ventHabitat == RM_VentHabitat.None) continue;
                var matching = new List<RM_Building_CauldronVent>();
                foreach (Thing t in vents)
                    if (t is RM_Building_CauldronVent v && v.Matches(ext.ventHabitat)) matching.Add(v);
                int ringCells = 0, ringCount = 0, ctrlCells = 0, ctrlCount = 0;
                foreach (IntVec3 c in map.AllCells)
                {
                    TerrainDef td = c.GetTerrain(map);
                    if (td == null || td.fertility <= 0f) continue;
                    bool ring = false, far = true;
                    foreach (Thing t in vents)
                        if ((c - t.Position).LengthHorizontal <= ext.ventRadius + ControlGap) { far = false; break; }
                    foreach (var v in matching)
                        if (InVentRing(v, c, ext)) { ring = true; break; }
                    bool has = c.GetPlant(map)?.def == plant;
                    if (ring) { ringCells++; if (has) ringCount++; }
                    else if (far) { ctrlCells++; if (has) ctrlCount++; }
                }
                lines.Add(plant.defName + " vents=" + matching.Count + " ring=" + ringCount + "/" + ringCells +
                          " ctrl=" + ctrlCount + "/" + ctrlCells);
            }
            return lines.Count == 1 ? "no flowers" : string.Join("; ", lines);
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
