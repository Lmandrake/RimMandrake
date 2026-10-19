using HarmonyLib;
using Verse;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// BIG_CREATURES_DESIGN_WALLS_AND_SLOTS §6 "caches must be cleared when a wall breaks": a building leaving the map drops every
    /// held crossing containing it the same tick, so a creature that held at a wall re-judges it as soon as part of it is gone
    /// (destroyed by anyone, deconstructed, minified). Off or with nothing held: one static read per despawn.
    /// </summary>
    [HarmonyPatch(typeof(Building), nameof(Building.DeSpawn))]
    internal static class Patch_Building_DeSpawn_WallsSlots
    {
        private static void Prefix(Building __instance)
        {
            if (!WallsSlotsUtility.AnyHeld || __instance == null || !__instance.Spawned) return;
            WallsSlotsUtility.NotifyDespawned(__instance.Map, __instance.OccupiedRect());
        }
    }

    /// <summary>
    /// §5.9: a built wall's inspect panel says how wide a creature its run of wall holds back ("Holds big creatures up to breadth
    /// 3 (3 thick here)"). Inspect-only, never a ground marker (his 2026-10-12 Q4 is about markers). Only impassable, non-rock
    /// buildings, only while the rule is on.
    /// </summary>
    [HarmonyPatch(typeof(ThingWithComps), nameof(ThingWithComps.GetInspectString))]
    internal static class Patch_WallInspect_WallsSlots
    {
        private static void Postfix(ThingWithComps __instance, ref string __result)
        {
            if (!RM_HugeThingsSettings.WallsSlotsActive) return;
            if (!(__instance is Building b) || !b.Spawned || b.def.passability != Traversability.Impassable) return;
            if (b.def.building == null || b.def.building.isNaturalRock || b is Building_TrunkBlocker || !b.def.destroyable) return;
            string line = WallsSlotsUtility.WallLine(b);
            __result = __result.NullOrEmpty() ? line : __result + "\n" + line;
        }
    }
}
