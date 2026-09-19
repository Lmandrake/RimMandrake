using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>
    /// WORLDMAP_LIQUID_TAGS_1, half (2) — MAPGEN. When a colony lands on a
    /// tile whose body is TYPED (see
    /// <see cref="RM_WorldComponent_LiquidTags"/>), repaint the standing
    /// water the vanilla terrain step just generated to that liquid's own
    /// terrain suite. This is what makes "fly to that tar lake" true: the
    /// lake is tar when you get there, not generic blue water.
    ///
    /// 🔑 UNTYPED IS VANILLA, BYTE FOR BYTE. Every early return below exists
    /// to make that literally true rather than approximately true: on an
    /// untagged tile this step reads the tag, gets null, and returns without
    /// touching the terrain grid, the rand state or anything else. That is
    /// the property the item's own `## verify` names, and it is why this
    /// step can be added to the shared MapCommonBase generator (the same
    /// self-gating shape RUT_FungalSoilScatter already uses) instead of
    /// needing a per-biome generator.
    ///
    /// WHAT IT REPAINTS, and what it deliberately does not:
    ///   • REPAINTED — the four STANDING-water terrains the map's own biome
    ///     would have produced: fresh deep/shallow and ocean deep/shallow.
    ///     They are resolved from the biome exactly the way
    ///     <c>MapGenUtility</c> resolves them (field, else the Core default),
    ///     so this recognises a modded biome's custom water without a
    ///     hardcoded defName list.
    ///   • NOT REPAINTED — MOVING water (river shallow / chest-deep). A river
    ///     flows in from inland and is not part of the body the tile is
    ///     tagged for; a brine sea does not make the river feeding it brine.
    ///   • NOT REPAINTED — ice, marsh, mud, beach sand or any other terrain.
    ///     Shore SAND staying sand is deliberate: recolouring a beach needs
    ///     terrain that does not exist yet, and inventing it here would be
    ///     scope this item did not ask for.
    ///
    /// ⚠️ A row whose <c>terrainSuite</c> is null, or whose suite has no
    /// slot for the depth in hand, leaves that cell alone rather than
    /// falling back to something arbitrary. Chest-deep falls back to
    /// <c>deep</c> because it IS the deep form of moving water and the suite
    /// only carries an explicit chestDeep on rows that need one — but deep
    /// never falls back to shallow, and shallow never falls back to deep,
    /// because depth is a gameplay property (what a pawn can wade) and
    /// silently changing it would be a real regression wearing a cosmetic
    /// hat.
    /// </summary>
    public class RM_GenStep_LiquidShores : GenStep
    {
        /// <summary>Distinct from every vanilla step's SeedPart. The value
        /// only has to be stable and unshared; it seeds nothing here because
        /// this step draws no random numbers at all.</summary>
        public override int SeedPart => 1774203911;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RimMandrakeFlowWorksSettings.typedLiquidShoresEnabled)
            {
                return;
            }

            LiquidDef liquid = RM_WorldComponent_LiquidTags.TagForMap(map);
            if (liquid == null || liquid.terrainSuite == null)
            {
                // UNTYPED: vanilla, untouched. The whole point.
                return;
            }

            BiomeDef biome = map.Biome;
            if (biome == null)
            {
                return;
            }

            // Resolve the biome's own standing-water terrains the same way
            // MapGenUtility does — biome field first, Core default second —
            // so a modded water biome is recognised without naming it.
            TerrainDef freshDeep = biome.waterDeepTerrain ?? TerrainDefOf.WaterDeep;
            TerrainDef freshShallow = biome.waterShallowTerrain ?? TerrainDefOf.WaterShallow;
            TerrainDef oceanDeep = biome.oceanDeepTerrain ?? TerrainDefOf.WaterOceanDeep;
            TerrainDef oceanShallow = biome.oceanShallowTerrain ?? TerrainDefOf.WaterOceanShallow;

            TerrainDef newDeep = liquid.terrainSuite.deep;
            TerrainDef newShallow = liquid.terrainSuite.shallow;

            // Build the replacement table once. A null replacement means
            // "this row does not ship that depth" and the cell is skipped.
            Dictionary<TerrainDef, TerrainDef> replace = new Dictionary<TerrainDef, TerrainDef>();
            AddReplacement(replace, freshDeep, newDeep);
            AddReplacement(replace, oceanDeep, newDeep);
            AddReplacement(replace, freshShallow, newShallow);
            AddReplacement(replace, oceanShallow, newShallow);

            if (replace.Count == 0)
            {
                return;
            }

            TerrainGrid grid = map.terrainGrid;
            int repainted = 0;

            foreach (IntVec3 cell in map.AllCells)
            {
                TerrainDef current = grid.TerrainAt(cell);
                if (current == null)
                {
                    continue;
                }

                TerrainDef replacement;
                if (!replace.TryGetValue(current, out replacement))
                {
                    continue;
                }

                grid.SetTerrain(cell, replacement);
                repainted++;
            }

            if (repainted > 0)
            {
                Log.Message("[FlowWorks] Typed liquid shores: repainted " + repainted
                    + " water cells to " + liquid.defName + " on a "
                    + biome.defName + " map (tile " + map.Tile.tileId + ").");
            }
        }

        /// <summary>Records one old -> new pair, skipping the no-op and the
        /// "row ships no such depth" cases. Guards against a biome whose
        /// deep and shallow slots resolve to the SAME terrain: first write
        /// wins, so a degenerate biome cannot make deep water shallow.</summary>
        private static void AddReplacement(
            Dictionary<TerrainDef, TerrainDef> table, TerrainDef from, TerrainDef to)
        {
            if (from == null || to == null || from == to)
            {
                return;
            }
            if (!table.ContainsKey(from))
            {
                table.Add(from, to);
            }
        }
    }
}
