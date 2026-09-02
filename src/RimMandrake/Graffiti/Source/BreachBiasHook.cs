using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_FRAMEWORK_BUILD_1 family Taunt, "Come And Take It": raiders
    // bias toward breaching AT a taunt mark - the lure-layer funnel into a
    // prepared kill zone. Mechanism only; no taunt ThingDef/content ships
    // here (owner-voice work, reserved elsewhere) - a content pack marks a
    // mark's ModExtension_Graffiti.breachLure = true and this hook does
    // the rest generically.
    //
    // Real hook point (RimSage-verified, not guessed):
    // Verse.AI.BreachingGrid.FindBuildingToBreach() is the sole place a
    // raid's LordToil_AssaultColonyBreaching.UpdateCurrentBreachTarget()
    // picks WHICH building to breach - a pure nearest-with-most-
    // reachable-sides flood-fill from the raid's own breach start, with no
    // existing scoring hook to bias into. Postfixed rather than
    // transpiled: cheapest, safest way to override a single Thing result
    // without reimplementing the flood fill BreachingGrid itself owns.
    [StaticConstructorOnStartup]
    public static class BreachBiasHookMod
    {
        static BreachBiasHookMod()
        {
            var harmony = new Harmony("mandrake.rm.graffiti.breachbias");
            harmony.Patch(
                AccessTools.Method(typeof(BreachingGrid), nameof(BreachingGrid.FindBuildingToBreach)),
                postfix: new HarmonyMethod(typeof(BreachBiasHookMod), nameof(Postfix)));
        }

        public static void Postfix(BreachingGrid __instance, ref Thing __result)
        {
            if (__result == null)
            {
                // No breachable building found at all - nothing to bias.
                return;
            }
            Map map = __instance.Map;
            if (map == null)
            {
                return;
            }
            Building lured = FindLuredBuilding(__instance, map, __result);
            if (lured != null)
            {
                __result = lured;
            }
        }

        // Any breach-eligible building adjacent to (or itself carrying,
        // for a mark placed directly on a door/wall) a breachLure mark
        // wins over the plain-nearest pick, provided it passes the SAME
        // eligibility gates the original flood-fill used
        // (BreachingUtility.ShouldBreachBuilding /
        // IsWorthBreachingBuilding / at least one reachable adjacent
        // side) - this hook never sends raiders at a building the
        // original algorithm would have rejected outright.
        private static Building FindLuredBuilding(BreachingGrid grid, Map map, Thing fallback)
        {
            foreach (Thing markThing in map.listerThings.AllThings)
            {
                ModExtension_Graffiti ext = markThing.def.GetModExtension<ModExtension_Graffiti>();
                if (ext == null || !ext.breachLure)
                {
                    continue;
                }
                Building candidate = FindEligibleBuildingNear(grid, map, markThing.Position);
                if (candidate != null)
                {
                    return candidate;
                }
            }
            return null;
        }

        private static Building FindEligibleBuildingNear(BreachingGrid grid, Map map, IntVec3 markCell)
        {
            for (int i = 0; i < 9; i++)
            {
                IntVec3 c = markCell + GenAdj.AdjacentCellsAndInside[i];
                if (!c.InBounds(map))
                {
                    continue;
                }
                List<Thing> thingList = c.GetThingList(map);
                for (int j = 0; j < thingList.Count; j++)
                {
                    if (thingList[j] is Building building
                        && BreachingUtility.ShouldBreachBuilding(building)
                        && BreachingUtility.IsWorthBreachingBuilding(grid, building)
                        && BreachingUtility.CountReachableAdjacentCells(grid, building) > 0)
                    {
                        return building;
                    }
                }
            }
            return null;
        }
    }
}
