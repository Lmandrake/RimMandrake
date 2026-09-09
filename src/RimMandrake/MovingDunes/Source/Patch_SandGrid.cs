using System;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.MovingDunes
{
    /// <summary>Shared reflection handles into <c>SandGrid</c>'s private state.
    /// Both prefixes need the grid's owning map, which the class keeps private.</summary>
    internal static class SandGridAccess
    {
        private static AccessTools.FieldRef<SandGrid, Map> mapRef;
        private static bool resolved;
        private static bool warned;

        internal static Map MapOf(SandGrid grid)
        {
            if (grid == null)
            {
                return null;
            }
            if (!resolved)
            {
                resolved = true;
                try
                {
                    mapRef = AccessTools.FieldRefAccess<SandGrid, Map>("map");
                }
                catch (Exception e)
                {
                    mapRef = null;
                    Log.Error(MovingDunesMod.LogPrefix + "SandGrid.map field not found — both sand "
                              + "grid rules are inert (they cannot tell which map they are on). "
                              + e.Message);
                }
            }
            if (mapRef == null)
            {
                return null;
            }
            try
            {
                return mapRef(grid);
            }
            catch (Exception e)
            {
                if (!warned)
                {
                    warned = true;
                    Log.Error(MovingDunesMod.LogPrefix + "reading SandGrid.map threw; sand grid "
                              + "rules are inert from here on. " + e.Message);
                }
                return null;
            }
        }
    }

    /// <summary>
    /// RULE 1 of MOVING_DUNES_DESIGN.md §2: sand refuses sand terrain.
    ///
    /// Vanilla's private <c>SandGrid.CanHaveSand(int)</c> returns false for
    /// <c>TerrainDefOf.Sand</c> and <c>TerrainDefOf.SoftSand</c> — on a desert map that
    /// is most of the map, so a dune field could never hold anything. On a dune-field
    /// map this prefix re-runs the vanilla test with THAT one clause removed.
    ///
    /// Deliberately NOT a blanket true: the <c>holdSnowOrSand</c> test (water, space)
    /// and the full-fillage-edifice test both still apply, so sand does not drift onto
    /// open water and walls still zero their own cells — which is what makes buildings
    /// free windbreaks (design §3).
    /// </summary>
    public static class Patch_SandGrid_CanHaveSand
    {
        public static bool Prefix(SandGrid __instance, int ind, ref bool __result)
        {
            try
            {
                Map map = SandGridAccess.MapOf(__instance);
                if (map == null || !DuneFieldRegistry.IsActive(map))
                {
                    return true; // ordinary map: vanilla decides
                }

                Building building = map.edificeGrid[ind];
                if (building != null && !SandGrid.CanCoexistWithSand(building.def))
                {
                    __result = false;
                    return false;
                }

                TerrainDef terrain = map.terrainGrid.TerrainAt(ind);
                // Vanilla's clause is: !holdSnowOrSand || terrain == Sand || terrain == SoftSand.
                // We drop the two sand-terrain comparisons and keep the rest.
                __result = terrain == null || terrain.holdSnowOrSand;
                return false;
            }
            catch (Exception e)
            {
                Log.ErrorOnce(MovingDunesMod.LogPrefix + "CanHaveSand prefix threw, falling back to "
                              + "vanilla for the rest of this session: " + e, 0x5D07E1);
                return true;
            }
        }
    }

    /// <summary>
    /// RULE 2 of MOVING_DUNES_DESIGN.md §2: ambient decay.
    ///
    /// <c>SteadyEnvironmentEffects.DoCellSteadyEffects</c> removes exactly
    /// <c>-1f/180f</c> of sand depth per cell visit whenever no sand-bearing weather is
    /// running, and unconditionally indoors. At the vanilla visit cadence (~1 visit per
    /// cell per 1,667 ticks) a full-depth drift evaporates in about five clear days,
    /// which is fatal to persistent dunes.
    ///
    /// The recognition is by exact constant — the fragile part, and the reason this
    /// assembly logs loudly and ships <c>selftest_moving_dunes_constants.py</c> to fail
    /// the moment the decompiled source stops saying <c>-1f / 180f</c>. Nothing else in
    /// the game passes that value to AddDepth: every deliberate caller uses a weather
    /// rate, a radial falloff, or this mod's own slab size.
    ///
    /// The decay is SCALED by the material's <c>ambientDecayFactor</c>, not deleted, so
    /// a material may keep partial decay (a damp coastal sand that packs down) without
    /// a second mechanism.
    /// </summary>
    public static class Patch_SandGrid_AddDepth
    {
        public static bool Prefix(SandGrid __instance, ref float depthToAdd)
        {
            try
            {
                if (Mathf.Abs(depthToAdd - MovingDunesMod.VanillaAmbientSandDecay)
                    > MovingDunesMod.AmbientDecayEpsilon)
                {
                    return true; // not the ambient decay call
                }

                Map map = SandGridAccess.MapOf(__instance);
                RM_DuneMaterialDef material = DuneFieldRegistry.MaterialOn(map);
                if (material == null)
                {
                    return true; // ordinary map: decay as vanilla
                }

                if (material.ambientDecayFactor <= 0f)
                {
                    return false; // fully suppressed — skip the original entirely
                }
                depthToAdd *= material.ambientDecayFactor;
                return true;
            }
            catch (Exception e)
            {
                Log.ErrorOnce(MovingDunesMod.LogPrefix + "AddDepth prefix threw, falling back to "
                              + "vanilla for the rest of this session: " + e, 0x5D07E2);
                return true;
            }
        }
    }
}
