// SEASHORES_COVERAGE_GAPS_1 -- live proof hook for the north-star script (jawa/static_call).
// ProofShore runs the SHIPPED rules against the live world without changing it: the real CoastDirectionAt result
// beside a modded sea with seasCountAsCoast on and off, the real TryAddMutator prefix, the shore-suppression
// switch, the healer's plan (Heal with apply=false), FishBiomeFor's off arm, and the PATCHED IL of
// FishingUtility.GetCatchesFor (via Harmony) for the rare-catch redirect. Settings restored in finally.
// Tile-dependent bars read "-" when the planet has no land tile beside a modded sea.
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.SeaShores
{
    public static class RM_SeaShoresProof
    {
        private static string B(bool v) => v ? "True" : "False";

        public static string ProofShore(string args)
        {
            RM_SeaShoresSettings cur = RM_SeaShoresSettings.Cur;
            bool wasCoast = cur.seasCountAsCoast, wasGen = cur.generateSeaShores, wasCatch = cur.seaCatchTables, wasHeal = cur.healFrozenWorldOnLoad;
            try
            {
                string s = "seas=" + DefDatabase<BiomeDef>.AllDefsListForReading.Count(b => RM_SeaShoreUtility.IsSea(b))
                    + " heal_setting=" + B(cur.healFrozenWorldOnLoad) + " coast_def=" + B(RM_SeaShoresDefOf.RM_SeaCoast != null);

                // --- the patched IL of GetCatchesFor
                MethodInfo getBiome = AccessTools.PropertyGetter(typeof(Map), nameof(Map.Biome));
                MethodInfo redirect = AccessTools.Method(typeof(RM_SeaShoreUtility), nameof(RM_SeaShoreUtility.FishBiomeFor));
                MethodBase target = AccessTools.Method(typeof(FishingUtility), nameof(FishingUtility.GetCatchesFor));
                int origLoads = PatchProcessor.GetOriginalInstructions(target).Count(ci => ci.Calls(getBiome));
                List<CodeInstruction> now = PatchProcessor.GetCurrentInstructions(target);
                s += " rare_orig_biome_loads=" + origLoads + " rare_redirects=" + now.Count(ci => ci.Calls(redirect))
                    + " rare_biome_loads_left=" + now.Count(ci => ci.Calls(getBiome));

                // --- generateSeaShores switch (mapSea is null on a bare worker, so only the setting speaks)
                RM_TileMutatorWorker_SeaCoast worker = RM_SeaShoresDefOf.RM_SeaCoast?.Worker as RM_TileMutatorWorker_SeaCoast;
                if (worker == null) s += " shore_on=- shore_off=-";
                else
                {
                    cur.generateSeaShores = true;
                    bool on = worker.ShoreSuppressed;
                    cur.generateSeaShores = false;
                    bool off = worker.ShoreSuppressed;
                    cur.generateSeaShores = wasGen;
                    s += " shore_suppressed_when_on=" + B(on) + " shore_suppressed_when_off=" + B(off);
                }

                // --- seaCatchTables off arm of the cell resolver, on the current map
                Map map = Find.CurrentMap;
                if (map == null) s += " fish_off_is_land=- fish_land_cell_is_land=-";
                else
                {
                    IntVec3 c = map.Center;
                    cur.seaCatchTables = false;
                    BiomeDef offB = RM_SeaShoreUtility.FishBiomeFor(map, c);
                    cur.seaCatchTables = true;
                    BiomeDef onB = RM_SeaShoreUtility.FishBiomeFor(map, c);
                    cur.seaCatchTables = wasCatch;
                    bool seaCell = RM_SeaShoreUtility.SeaForCell(map, c) != null;
                    s += " fish_off_is_land=" + B(offB == map.Biome) + " fish_centre_is_sea_water=" + B(seaCell)
                        + " fish_on_is_land_when_not_sea=" + B(seaCell || onB == map.Biome);
                }

                // --- tile-dependent rules: a buildable land tile beside a coasting sea
                WorldGrid grid = Find.WorldGrid;
                PlanetLayer layer = grid?.Surface;
                if (layer == null) return s + " tiles=-";
                PlanetTile seaTile = PlanetTile.Invalid, vanillaTile = PlanetTile.Invalid;
                int beside = 0;
                foreach (Tile tile in layer.Tiles)
                {
                    if (tile?.PrimaryBiome == null || !tile.PrimaryBiome.canBuildBase) continue;
                    if (RM_SeaShoreUtility.PrimarySeaFor(tile.tile) == null) continue;
                    beside++;
                    bool vanilla = RM_Patch_TryAddMutator.HasVanillaOceanNeighbour(tile.tile, layer);
                    if (vanilla) { if (!vanillaTile.Valid) vanillaTile = tile.tile; }
                    else if (!seaTile.Valid && RM_SeaShoreUtility.HasCoastingSeaNeighbour(tile.tile)) seaTile = tile.tile;
                }
                s += " tiles_beside_sea=" + beside;
                if (!seaTile.Valid) s += " coast_on=- coast_off=- sub_sea=- sub_other_mutator=- sub_vanilla=-";
                else
                {
                    cur.seasCountAsCoast = true;
                    bool on = Find.World.CoastDirectionAt(seaTile).IsValid;
                    cur.seasCountAsCoast = false;
                    bool off = Find.World.CoastDirectionAt(seaTile).IsValid;
                    cur.seasCountAsCoast = wasCoast;
                    s += " coast_on=" + B(on) + " coast_off=" + B(off);
                    TileMutatorDef m = TileMutatorDefOf.Coast;
                    RM_Patch_TryAddMutator.Prefix(layer[seaTile], layer, ref m);
                    s += " sub_sea=" + B(m == RM_SeaShoresDefOf.RM_SeaCoast);
                    TileMutatorDef other = TileMutatorDefOf.River;
                    RM_Patch_TryAddMutator.Prefix(layer[seaTile], layer, ref other);
                    s += " sub_other_mutator=" + B(other == TileMutatorDefOf.River);
                    if (vanillaTile.Valid)
                    {
                        TileMutatorDef v = TileMutatorDefOf.Coast;
                        RM_Patch_TryAddMutator.Prefix(layer[vanillaTile], layer, ref v);
                        s += " sub_vanilla=" + B(v == TileMutatorDefOf.Coast);
                    }
                    else s += " sub_vanilla=-";
                }

                int healed, replaced, already;
                RM_WorldComponent_SeaShoreHealer.Heal(layer, false, out healed, out replaced, out already);
                s += " heal_left=" + healed + " heal_stale_left=" + replaced + " heal_already=" + already;
                return s;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
            finally
            {
                cur.seasCountAsCoast = wasCoast;
                cur.generateSeaShores = wasGen;
                cur.seaCatchTables = wasCatch;
                cur.healFrozenWorldOnLoad = wasHeal;
            }
        }
    }
}
