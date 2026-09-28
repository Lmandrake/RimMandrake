using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.LongShade
{
    // LONGSHADE_RULED_CONTENT_1, Q6 — the dew-line rim plant's growth gate.
    //
    // §3 of long_shade_bedazzle_2026-09-27.md: "a thin pale band-plant that
    // grows ONLY on shade-boundary cells — the rim, not the area." Q10 binds
    // it to the ultracactus's own hard ceiling: pale, rim-only, never green
    // in quantity.
    //
    // Same choke point as mandrake.rm.environmentalhazards'
    // RM_Patch_LeachmossWildSpawnGate (its own header explains why
    // WildPlantSpawner.CalculatePlantsWhichCanGrowAt is the one call site
    // that covers both initial map-gen seeding and every later regrowth
    // roll) — MEASURED signature (RimSage, 2026-09-27):
    //   private void CalculatePlantsWhichCanGrowAt(IntVec3 c,
    //       List<ThingDef> outPlants, bool cavePlants, float plantDensityFactor)
    // Leachmoss's gate is a global on/off (drop the whole def from the list
    // by Mod Settings bool); this one is PER-CELL — Harmony binds the
    // original method's own `c` and `outPlants` parameters by name, plus the
    // private `map` field via `___map`, to read RM_MapComponent_ShadeGrid.
    //
    // The rim test: RM_MapComponent_ShadeGrid.ShadeAt returns 0f (full sun)
    // .. 1f (full shade — roofed, or the shade-caster's own cell). A cell
    // strictly between those two bounds only exists in the falloff band
    // around a shade-caster, which IS the boundary/rim the design calls for
    // — full sun and full shade are both explicitly the area, not the line.
    public static class RM_Patch_DewfringeWildSpawnGate
    {
        private const string DewfringeDefName = "RM_Dewfringe";

        // The fringe band: strictly above "no shade influence at all" and
        // strictly below "this cell casts or is fully under shade itself".
        // Kept generous rather than a single ring so the visible halo reads
        // as a rim a few cells wide, not a one-tile hairline no player would
        // ever notice — still excludes both the open crossing (0f) and the
        // shaded patch interior (1f, or close to it).
        private const float MinRimShade = 0.05f;

        private const float MaxRimShade = 0.85f;

        static RM_Patch_DewfringeWildSpawnGate()
        {
            var target = AccessTools.Method(typeof(WildPlantSpawner), "CalculatePlantsWhichCanGrowAt");
            if (target == null)
            {
                Log.Error("[RM LongShade] dewfringe-wild-spawn-gate: WildPlantSpawner."
                    + "CalculatePlantsWhichCanGrowAt not found — rule NOT armed. The engine "
                    + "signature this patch was written against has moved.");
                return;
            }

            try
            {
                Harmony harmony = new Harmony("mandrake.rm.longshade");
                harmony.Patch(target, postfix: new HarmonyMethod(
                    typeof(RM_Patch_DewfringeWildSpawnGate), nameof(CalculatePlantsWhichCanGrowAt_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM LongShade] dewfringe-wild-spawn-gate: patch failed, rule NOT armed. " + e);
            }
        }

        // outPlants is mutated in place by the original method; a postfix
        // receives the same List<ThingDef> reference, so removing from it
        // here is visible to the caller with no return-value dance.
        public static void CalculatePlantsWhichCanGrowAt_Postfix(IntVec3 c, List<ThingDef> outPlants, Map ___map)
        {
            if (outPlants == null || outPlants.Count == 0)
            {
                return;
            }
            if (!RM_LongShadeSettings.modEnabled || !RM_LongShadeSettings.dewfringeShadeLineGateEnabled)
            {
                return; // mod option off: dewfringe follows plain fertility/terrain rules like anything else
            }

            int index = -1;
            for (int i = 0; i < outPlants.Count; i++)
            {
                if (outPlants[i]?.defName == DewfringeDefName)
                {
                    index = i;
                    break;
                }
            }
            if (index < 0)
            {
                return;
            }

            try
            {
                Map map = ___map;
                RM_MapComponent_ShadeGridLookup lookup = RM_MapComponent_ShadeGridLookup.For(map);
                if (!lookup.OnRim(c))
                {
                    outPlants.RemoveAt(index);
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RM LongShade] dewfringe-wild-spawn-gate: " + e.Message, 0x52444C);
            }
        }

        // Thin wrapper so this file has exactly one place that knows the
        // shade-grid assembly is a soft (loadAfter, no hard modDependency)
        // reference — if mandrake.rm.creaturebehaviors is ever absent this
        // throws inside the try/catch above and the gate degrades to "never
        // restrict" (Dewfringe grows by fertility/terrain alone), never a
        // hard failure of the whole postfix chain.
        private readonly struct RM_MapComponent_ShadeGridLookup
        {
            private readonly RimMandrake.CreatureBehaviors.RM_MapComponent_ShadeGrid grid;

            private RM_MapComponent_ShadeGridLookup(RimMandrake.CreatureBehaviors.RM_MapComponent_ShadeGrid grid)
            {
                this.grid = grid;
            }

            public static RM_MapComponent_ShadeGridLookup For(Map map)
            {
                return new RM_MapComponent_ShadeGridLookup(map?.GetComponent<RimMandrake.CreatureBehaviors.RM_MapComponent_ShadeGrid>());
            }

            public bool OnRim(IntVec3 c)
            {
                if (grid == null)
                {
                    return false; // no grid on this map (e.g. mandrake.rm.creaturebehaviors not loaded) — no rim, dewfringe never grows rather than growing everywhere
                }
                float shade = grid.ShadeAt(c);
                return shade > MinRimShade && shade < MaxRimShade;
            }
        }
    }
}
