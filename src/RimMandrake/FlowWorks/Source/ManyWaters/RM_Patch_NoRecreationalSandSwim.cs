using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.ManyWaters
{
    // ════════════════════════════════════════════════════════════════════
    // DEEP_SAND_WALKABLE_TERRAIN_1 — no recreational "go swimming" in deep sand.
    //
    // MEASURED (RimSage, decompiled 1.6+Odyssey), the one path to a colonist
    // swimming that does NOT depend on WaterBase/traversedThought and does NOT
    // depend on passability, because it is the one system that CHECKS
    // standability instead of assuming Impassable:
    //   - Verse/Pawn.cs: `Swimming => CurJob?.swimming ?? false` — a JOB flag,
    //     not a terrain read.
    //   - RimWorld/JobDriver_GoSwimming.cs `CheckForSwimmingPose()` sets
    //     `job.swimming = true` whenever the pawn's cell `IsWater` — no depth
    //     check, no WaterBase requirement.
    //   - RimWorld/JoyGiver_GoSwimming.cs is the only place that JOB gets
    //     created, and its cell validator requires `IsWater` AND
    //     `x.Standable(pawn.Map)`. While RM_DeepSand was Impassable, Standable
    //     was false and this joy activity could never target it. Flipping
    //     passability to Standable (this item's whole point) makes it
    //     Standable too, so without this patch a bored colonist could be
    //     offered "go swimming" in a sand pit that is supposed to be a
    //     punishing crawl, not a pool — the exact "some OTHER path than
    //     WaterBase" failure mode the item asked to rule out.
    //   - SwimPathFinder.TryFindSwimPath (the only thing that plots the swim
    //     route) is called from nowhere else in production code (verified:
    //     its only other caller is a debug tool), so gating this one JoyGiver
    //     closes the whole hole — no need to touch SwimPathFinder itself,
    //     which the terrain's own sand-swimming predator may want intact.
    //
    // SCOPE: any TerrainDef carrying RM_NoRecreationalSwimExtension is excluded
    // from JoyGiver_GoSwimming's result, whether it is the immediate cell or
    // anywhere in the swim path's cell queue (SwimPathFinder can chain a
    // mixed run of Water-tagged cells, so checking only the first cell is not
    // enough). This is a restriction only — it changes nothing about real
    // water, and nothing about the predator's own movement, which does not
    // route through JoyGiver_GoSwimming at all.
    //
    // Harmony bootstrap: RM_FlowWorksHarmony's PatchAll() in
    // RM_Patch_SuperdeepShooting.cs already scans this whole assembly — no
    // second [StaticConstructorOnStartup] needed here.
    // ════════════════════════════════════════════════════════════════════
    [HarmonyPatch(typeof(JoyGiver_GoSwimming), nameof(JoyGiver_GoSwimming.TryGiveJob))]
    public static class RM_Patch_JoyGiver_GoSwimming_NoSandSwim
    {
        [HarmonyPostfix]
        public static void Postfix(Pawn pawn, ref Job __result)
        {
            if (__result == null || pawn == null || pawn.Map == null)
            {
                return;
            }
            Map map = pawn.Map;
            if (CellIsMarkedNoSwim(__result.targetA.Cell, map))
            {
                __result = null;
                return;
            }
            if (__result.targetQueueA != null)
            {
                for (int i = 0; i < __result.targetQueueA.Count; i++)
                {
                    if (CellIsMarkedNoSwim(__result.targetQueueA[i].Cell, map))
                    {
                        __result = null;
                        return;
                    }
                }
            }
        }

        private static bool CellIsMarkedNoSwim(IntVec3 cell, Map map)
        {
            if (!cell.IsValid)
            {
                return false;
            }
            TerrainDef terrain = cell.GetTerrain(map);
            return terrain != null && terrain.HasModExtension<RM_NoRecreationalSwimExtension>();
        }
    }
}
