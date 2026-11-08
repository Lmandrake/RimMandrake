using HarmonyLib;
using Verse;

namespace RimMandrake.Graffiti
{
    // A mark is drawn on its wall's own cell, so a wall that is mined, deconstructed or blown up takes its paint with it; the mark
    // would otherwise hang in the air over the gap. Prefix, while the building's Position and Map still answer.
    [StaticConstructorOnStartup]
    public static class WallLossPatch
    {
        static WallLossPatch()
        {
            new Harmony("mandrake.rm.graffiti.wallloss").Patch(
                AccessTools.Method(typeof(Building), nameof(Building.DeSpawn)),
                prefix: new HarmonyMethod(typeof(WallLossPatch), nameof(Prefix)));
        }

        public static void Prefix(Building __instance)
        {
            if (__instance.Spawned && GraffitiJobUtility.IsPaintableWall(__instance.def))
            {
                Filth_Mark.Notify_WallGone(__instance.Position, __instance.Map);
            }
        }
    }
}
