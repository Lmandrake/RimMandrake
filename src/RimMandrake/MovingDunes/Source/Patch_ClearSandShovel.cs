using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.MovingDunes
{
    /// <summary>
    /// SHOVELS_BUILD_NO_DIGGING_BARE_HANDED (owner 2026-10-25, Q2: drift shovelling needs a shovel too). Vanilla's
    /// <c>WorkGiver_ClearSnowOrSand</c> on a cell holding sand (sandGrid depth &gt; 0) asks FlowWorks' shovel rule,
    /// reflection-soft (_Shared/FlowWorksShovels): no shovel in the pack and none free, no job; one free, the colonist fetches
    /// it first. Snow-only cells are vanilla's. FlowWorks absent or its setting off: nothing changes.
    /// </summary>
    public static class Patch_ClearSand_Shovel
    {
        internal static bool Sandy(Map map, IntVec3 c)
        {
            return map?.sandGrid != null && c.IsValid && c.InBounds(map) && map.sandGrid.GetDepth(c) > 0f;
        }
    }

    /// <summary>WorkGiver_ClearSnowOrSand.HasJobOnCell(pawn, c, forced): a sandy cell needs a shovel, or one to fetch.</summary>
    public static class Patch_ClearSand_Shovel_HasJob
    {
        public static void Postfix(Pawn __0, IntVec3 __1, bool __2, ref bool __result)
        {
            if (__result && __0 != null && Patch_ClearSand_Shovel.Sandy(__0.Map, __1)
                && !RimMandrake.Shared.FlowWorksShovelRead.CanWorkOrFetch(__0, __2))
            {
                __result = false;
            }
        }
    }

    /// <summary>WorkGiver_ClearSnowOrSand.JobOnCell(pawn, c, forced): no shovel in the pack, the fetch job instead.</summary>
    public static class Patch_ClearSand_Shovel_JobOn
    {
        public static void Postfix(Pawn __0, IntVec3 __1, bool __2, ref Job __result)
        {
            if (__result != null && __0 != null && Patch_ClearSand_Shovel.Sandy(__0.Map, __1)
                && !RimMandrake.Shared.FlowWorksShovelRead.Ready(__0))
            {
                __result = RimMandrake.Shared.FlowWorksShovelRead.FetchJobFor(__0, __2);
            }
        }
    }

    /// <summary>JobDriver_ClearSnowAndSand.MakeNewToils: a running clear on a sandy cell stops when the shovel leaves the
    /// pack (or the job predates the setting).</summary>
    public static class Patch_ClearSand_Shovel_Driver
    {
        public static void Postfix(JobDriver_ClearSnowAndSand __instance)
        {
            JobDriver_ClearSnowAndSand d = __instance;
            d.FailOn(() => d.job != null && Patch_ClearSand_Shovel.Sandy(d.pawn?.Map, d.job.targetA.Cell)
                && !RimMandrake.Shared.FlowWorksShovelRead.Ready(d.pawn));
        }
    }
}
