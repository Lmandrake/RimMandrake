using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // WAR_LAB_CRATER_HOOK_1 -- the worldmap-tile half of the ignition-to-crater
    // ending (design/Jawa/worldbuilding/biomes/wasteland.md §10 option 4: a
    // bleeding reactor core dropped into the propane lake ignites it, breaching
    // ANCIENT_WAR_LAB_1). Local-map spectacle (fire, terrain swap, roof breach at
    // the lab itself) is that dungeon's own build -- this class does ONLY the
    // permanent worldmap-tile mutation, replicating jawa/world_tile_set +
    // jawa/world_commit in-process (JawaBenchWorldTools.cs) because the bridge
    // cannot fire itself from an in-game trigger.
    //
    // The tile set is derived at fire time -- every SurfaceTile currently on the
    // frozen RUT_PropaneLake biome -- never a hardcoded list. The footprint was
    // owner-ruled and painted 2026-09-08 (commit a5020486e, "RUT_PropaneLake
    // paint recorded DONE"), but this class must track wherever that def
    // currently sits on the live world, not a snapshot of it.
    public static class WarLabCraterMutation
    {
        private const string SourceBiomeDefName = "RUT_PropaneLake";
        private const string CraterBiomeDefName = "RUT_Wasteland";

        /// <summary>
        /// Fires the ignition once per save. Returns true only if it actually
        /// mutated tiles this call -- false on a missing world/game, a missing
        /// biome def, an empty footprint, or a repeat call (idempotent).
        /// </summary>
        public static bool Ignite()
        {
            if (!StructureInjectionsRUTSettings.warLabCraterEnabled)
                return false;

            if (Current.Game == null)
                return false;

            var comp = Current.Game.GetComponent<GameComponent_WarLabCrater>();
            if (comp == null || comp.Triggered)
                return false;

            if (Find.World == null || Find.WorldGrid == null)
                return false;

            var sourceBiome = DefDatabase<BiomeDef>.GetNamedSilentFail(SourceBiomeDefName);
            var craterBiome = DefDatabase<BiomeDef>.GetNamedSilentFail(CraterBiomeDefName);
            if (sourceBiome == null || craterBiome == null)
            {
                Log.Error("[WAR_LAB_CRATER_HOOK_1] Missing biome def(s): " +
                    SourceBiomeDefName + "=" + (sourceBiome != null) + ", " +
                    CraterBiomeDefName + "=" + (craterBiome != null) + ". Ignition aborted.");
                return false;
            }

            var grid = Find.WorldGrid;
            var touched = new List<int>();
            for (int i = 0; i < grid.TilesCount; i++)
            {
                var tile = grid[i] as SurfaceTile;
                if (tile == null || tile.PrimaryBiome != sourceBiome)
                    continue;
                tile.PrimaryBiome = craterBiome;
                touched.Add(i);
            }

            if (touched.Count == 0)
            {
                Log.Warning("[WAR_LAB_CRATER_HOOK_1] Ignite() fired but found zero " +
                    SourceBiomeDefName + " tiles -- footprint may already be gone. No commit run.");
                return false;
            }

            Commit();

            comp.Triggered = true;
            comp.CrateredTileIds = touched;
            Log.Message("[WAR_LAB_CRATER_HOOK_1] Ignition complete: " + touched.Count +
                " tile(s) " + SourceBiomeDefName + " -> " + CraterBiomeDefName + ".");
            return true;
        }

        // Mirrors jawa/world_commit's step order exactly (JawaBenchWorldTools.cs
        // WorldCommit) -- RimWorld has no per-tile visual invalidation except
        // pollution, so a full mesh regen + cache clear is the only route to a
        // planet that is consistent with what was just written.
        private static void Commit()
        {
            var grid = Find.WorldGrid;
            var surface = grid.Surface;
            var renderer = Find.World.renderer;

            void Step(Action act)
            {
                try { act(); }
                catch (Exception e)
                {
                    Log.Warning("[WAR_LAB_CRATER_HOOK_1] Commit step failed: " + e);
                }
            }

            if (renderer != null)
            {
                Step(() => renderer.GetLayer<WorldDrawLayer_Terrain>(surface).RegenerateNow());
                Step(() => renderer.GetLayer<WorldDrawLayer_Hills>(surface).RegenerateNow());
                Step(() => renderer.GetLayer<WorldDrawLayer_Landmarks>(surface).RegenerateNow());
                Step(() => renderer.GetLayer<WorldDrawLayer_Roads>(surface).RegenerateNow());
                Step(() => renderer.GetLayer<WorldDrawLayer_Rivers>(surface).RegenerateNow());
            }

            Step(() => surface.FastTileFinder.DirtyCache());
            Step(() => Find.WorldReachability.ClearCache());
            Step(() => Find.WorldPathGrid.RecalculateLayerPerceivedPathCosts(surface));
        }
    }
}
