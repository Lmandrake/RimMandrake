using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// FURNACEBEAST_WORLD_MIGRATION_1 — seeds the initial herd(s) once, so the
    /// world leg has something to drive from the first tick instead of
    /// waiting on a debug action or a beast wandering off some map's edge
    /// (which this build does not attempt — WorldObject_RM_FurnaceHerd's
    /// header explains the boundary).
    ///
    /// 🔴 THIS IS NOT WORLDGEN. Ash'karr's terrain and biome placement are
    /// frozen and this component never touches either (CLAUDE.md: no
    /// worldgen feature, in any version). It places a mobile WorldObject on
    /// the ALREADY-FIXED planet — the same category of act as a quest site
    /// appearing, a raid landing, or WorldObject_Inhabited's own settlement
    /// compose step, all of which already run after world generation in this
    /// campaign.
    ///
    /// 🔑 SPECIES-AGNOSTIC BY CONSTRUCTION. This assembly is
    /// mandrake.rm.pyrelands (the franchise-free, standalone biome mod);
    /// RUT_FurnaceBeast is campaign content one tier up, in RimUtinni, and
    /// this file must not hard-depend on it — same rule
    /// JobGiver_RUT_FurnaceThermalCycle and Patch_FurnaceHerdMapRemoval both
    /// already follow: gate on the COMP (CompProperties_FurnaceThermalCharge),
    /// never on a defName. If no loaded PawnKindDef carries that comp (the
    /// creature layer absent), nothing is seeded and nothing errors.
    /// </summary>
    public class WorldComponent_RM_FurnaceHerdSeeder : WorldComponent
    {
        private bool seeded;

        public WorldComponent_RM_FurnaceHerdSeeder(World world) : base(world)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref seeded, "rm_furnaceHerdSeeded", false);
        }

        public override void FinalizeInit(bool fromLoad)
        {
            base.FinalizeInit(fromLoad);

            // Latched regardless of outcome (settings off, no candidate
            // species, no Deep Desert tile) so a world that genuinely has
            // none of these is not re-scanned every load. Flipping the
            // setting back on later re-seeds nothing automatically — same
            // "no retroactive change to an existing save" shape every other
            // worldgen-adjacent toggle in this mod already uses.
            if (seeded)
            {
                return;
            }
            seeded = true;

            if (!RM_PyrelandsSettings.pyrelandsEnabled
                || !RM_PyrelandsSettings.furnaceThermalEnabled
                || !RM_PyrelandsSettings.furnaceWorldMigrationEnabled)
            {
                return;
            }

            SeedHerds();
        }

        private void SeedHerds()
        {
            PawnKindDef kind = DefDatabase<PawnKindDef>.AllDefsListForReading
                .FirstOrDefault(k => k?.race?.comps != null
                    && k.race.comps.Any(c => c is CompProperties_FurnaceThermalCharge));
            if (kind == null)
            {
                Log.Message("[RimMandrake.Pyrelands] no PawnKindDef carries CompFurnaceThermalCharge "
                    + "(the creature layer is not in this mod list) — no furnace-beast herd seeded.");
                return;
            }

            List<PlanetTile> candidates = FindTilesWithBiome(PyrelandsTuning.DeepDesertBiomeDefNames);
            if (candidates.Count == 0)
            {
                Log.Warning("[RimMandrake.Pyrelands] no Deep Desert tile (Desert/ExtremeDesert) found "
                    + "on this world — no furnace-beast herd seeded.");
                return;
            }

            int wanted = System.Math.Max(0, System.Math.Min(RM_PyrelandsSettings.furnaceHerdCount, candidates.Count));
            for (int i = 0; i < wanted; i++)
            {
                PlanetTile tile = candidates[Rand.Range(0, candidates.Count)];
                SeedOneHerd(tile, kind);
            }
        }

        private static void SeedOneHerd(PlanetTile tile, PawnKindDef kind)
        {
            // Members are populated BEFORE the herd is registered with
            // Find.WorldObjects, so a world-tick landing between the two
            // calls can never observe (and self-destroy) an empty herd —
            // see WorldObject_RM_FurnaceHerd.TryDeliverToSettledMap's
            // "empty herd" early-out.
            var herd = (WorldObject_RM_FurnaceHerd)WorldObjectMaker.MakeWorldObject(PyrelandsMechanicsDefOf.RM_FurnaceHerd);
            herd.Tile = tile;
            herd.leg = FurnaceHerdLeg.DeepDesert;

            int size = Rand.RangeInclusive(PyrelandsTuning.WorldHerdMinSize, PyrelandsTuning.WorldHerdMaxSize);
            int made = 0;
            for (int i = 0; i < size; i++)
            {
                Pawn beast = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
                    kind, null, PawnGenerationContext.NonPlayer, tile, forceGenerateNewPawn: true));
                if (beast == null)
                {
                    continue;
                }
                if (herd.members.TryAdd(beast, canMergeWithExistingStacks: false))
                {
                    made++;
                }
                else
                {
                    beast.Destroy();
                }
            }

            if (made == 0)
            {
                // Nothing to carry — do not register a hollow herd that would
                // just self-destroy on its own first tick anyway.
                Log.Warning("[RimMandrake.Pyrelands] furnace-beast herd seed on tile " + tile
                    + " generated 0 of " + size + " pawns; no herd placed.");
                return;
            }

            Find.WorldObjects.Add(herd);
            Log.Message("[RimMandrake.Pyrelands] seeded a furnace-beast herd (" + made + " of " + size
                + ") on tile " + tile + ".");
        }

        private static List<PlanetTile> FindTilesWithBiome(IReadOnlyList<string> biomeNames)
        {
            var result = new List<PlanetTile>();
            WorldGrid grid = Find.WorldGrid;
            int count = grid.TilesCount;
            for (int i = 0; i < count; i++)
            {
                PlanetTile t = new PlanetTile(i);
                BiomeDef biome = grid[t]?.PrimaryBiome;
                if (biome != null && WorldObject_RM_FurnaceHerd.MatchesAny(biome.defName, biomeNames))
                {
                    result.Add(t);
                }
            }
            return result;
        }
    }
}
