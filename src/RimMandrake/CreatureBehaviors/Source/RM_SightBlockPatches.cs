using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1 — make an opted-in Thing (a tall
    // plant) block a pawn's SIGHT.
    //
    // Why not just postfix IntVec3.CanBeSeenOverFast (the item's first guess):
    //   - it is a tiny static the Mono JIT may inline into GenSight, so a patch
    //     on it can silently never run;
    //   - it is also read by GenExplosion, Verb_ShootBeam, the Burner ability
    //     and ExitMapGrid — a bush would start stopping blast waves and beams;
    //   - it knows nothing about the line's endpoints, so a pawn standing IN a
    //     thicket cell would go blind and invisible to everyone.
    //
    // So instead (RimSage-verified against the 1.6 decompile):
    //   1. Postfix BOTH real GenSight.LineOfSight overloads. The 3-arg overload
    //      only forwards to the rect overload; LineOfSightToEdges and
    //      LineOfSightToThing forward to these two. The postfix replays the
    //      exact vanilla cell walk against RM_MapComponent_SightBlockGrid and
    //      can only turn a TRUE into FALSE.
    //   2. The postfix is inert unless a "someone is LOOKING" call site is on
    //      the stack — a [ThreadStatic] depth counter raised by prefix/finalizer
    //      pairs on a short whitelist. Every other LineOfSight caller (fire
    //      spread, explosions' cell set, short circuits, facility linking, foam
    //      turrets, spawn-cell finders, GenSteps, social chat range) keeps
    //      vanilla behaviour byte for byte.
    //
    // Whitelist — COMBAT (gated by the "blocks ranged fire" setting):
    //   Verb.CanHitCellFromCellIgnoringRange   every ranged shot, AI or player-ordered
    //   AttackTargetFinder.CanSee              target acquisition's LOS test
    //   ShootLeanUtility.CellCanSeeCell        cell-to-cell sight with leaning
    // Whitelist — PERCEPTION (always, when the mechanism is on):
    //   PawnLocalAwareness.AnimalAwareOf       a wild animal noticing a thing
    //   ThoughtUtility.Witnessed               witnessing a death/injury
    //   PawnObserver.PossibleToObserve         mood from things seen nearby
    //   FleeUtility.ShouldFleeFrom (checkLOS)  fleeing a threat you can see
    //
    // Deliberately NOT touched (decisions recorded on the item):
    //   pathing — nothing here changes passability or pathCost; AvoidGrid reads
    //     the Building overload of CanBeSeenOver, never this grid.
    //   the player's camera — RimWorld has no LOS-driven rendering; FogGrid
    //     unfogs by region flood, not LineOfSight. The player always sees
    //     every pawn on unfogged ground, their own or not.
    //   leaning — a shooter never "leans around" a plant as if it were a wall
    //     corner (ShootLeanUtility reads CanBeSeenOver directly).
    // ════════════════════════════════════════════════════════════════════
    public static class RM_SightContext
    {
        [ThreadStatic]
        public static int depth;
    }

    [StaticConstructorOnStartup]
    public static class RM_SightBlockPatches
    {
        public static int patchedCount;

        static RM_SightBlockPatches()
        {
            Harmony harmony = new Harmony("mandrake.rm.creaturebehaviors.sightblock");

            MethodInfo losA = AccessTools.Method(typeof(GenSight), nameof(GenSight.LineOfSight),
                new[] { typeof(IntVec3), typeof(IntVec3), typeof(Map), typeof(bool), typeof(Func<IntVec3, bool>), typeof(int), typeof(int) });
            MethodInfo losB = AccessTools.Method(typeof(GenSight), nameof(GenSight.LineOfSight),
                new[] { typeof(IntVec3), typeof(IntVec3), typeof(Map), typeof(CellRect), typeof(CellRect), typeof(Func<IntVec3, bool>), typeof(bool) });
            Patch(harmony, losA, postfix: nameof(Postfix_LineOfSightCells));
            Patch(harmony, losB, postfix: nameof(Postfix_LineOfSightRects));

            PatchScope(harmony, AccessTools.Method(typeof(Verb), "CanHitCellFromCellIgnoringRange"), combat: true);
            PatchScope(harmony, AccessTools.Method(typeof(AttackTargetFinder), nameof(AttackTargetFinder.CanSee)), combat: true);
            PatchScope(harmony, AccessTools.Method(typeof(ShootLeanUtility), nameof(ShootLeanUtility.CellCanSeeCell)), combat: true);

            PatchScope(harmony, AccessTools.Method(typeof(PawnLocalAwareness), nameof(PawnLocalAwareness.AnimalAwareOf)), combat: false);
            PatchScope(harmony, AccessTools.Method(typeof(ThoughtUtility), nameof(ThoughtUtility.Witnessed)), combat: false);
            PatchScope(harmony, AccessTools.Method(typeof(PawnObserver), "PossibleToObserve"), combat: false);
            PatchScope(harmony, AccessTools.Method(typeof(FleeUtility), nameof(FleeUtility.ShouldFleeFrom)), combat: false);
        }

        private static void Patch(Harmony harmony, MethodInfo target, string prefix = null, string postfix = null, string finalizer = null)
        {
            if (target == null)
            {
                Log.Warning("[RM CreatureBehaviors] sight-block: a target method was not found; that hook is skipped (vanilla behaviour there).");
                return;
            }
            try
            {
                harmony.Patch(target,
                    prefix: prefix == null ? null : new HarmonyMethod(typeof(RM_SightBlockPatches), prefix),
                    postfix: postfix == null ? null : new HarmonyMethod(typeof(RM_SightBlockPatches), postfix),
                    finalizer: finalizer == null ? null : new HarmonyMethod(typeof(RM_SightBlockPatches), finalizer));
                patchedCount++;
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] sight-block: patching " + target.DeclaringType?.Name + "." + target.Name
                    + " failed; that hook is skipped (vanilla behaviour there): " + e);
            }
        }

        private static void PatchScope(Harmony harmony, MethodInfo target, bool combat)
        {
            Patch(harmony, target,
                prefix: combat ? nameof(Prefix_EnterCombatSight) : nameof(Prefix_EnterSight),
                finalizer: nameof(Finalizer_ExitSight));
        }

        public static void Prefix_EnterSight(out bool __state)
        {
            __state = RM_CreatureBehaviorsSettings.sightBlockEnabled;
            if (__state)
            {
                RM_SightContext.depth++;
            }
        }

        public static void Prefix_EnterCombatSight(out bool __state)
        {
            __state = RM_CreatureBehaviorsSettings.sightBlockEnabled && RM_CreatureBehaviorsSettings.sightBlockRangedFire;
            if (__state)
            {
                RM_SightContext.depth++;
            }
        }

        public static void Finalizer_ExitSight(bool __state)
        {
            if (__state && RM_SightContext.depth > 0)
            {
                RM_SightContext.depth--;
            }
        }

        public static void Postfix_LineOfSightCells(ref bool __result, IntVec3 start, IntVec3 end, Map map, int halfXOffset, int halfZOffset)
        {
            if (!__result || RM_SightContext.depth == 0)
            {
                return;
            }
            RM_MapComponent_SightBlockGrid grid = RM_MapComponent_SightBlockGrid.For(map);
            if (grid != null && grid.BlockedCellCount != 0
                && grid.WalkBlocks(start, end, halfXOffset, halfZOffset, RM_CreatureBehaviorsSettings.sightBlockCellsNeeded))
            {
                __result = false;
            }
        }

        public static void Postfix_LineOfSightRects(ref bool __result, IntVec3 start, IntVec3 end, Map map, CellRect startRect, CellRect endRect)
        {
            if (!__result || RM_SightContext.depth == 0)
            {
                return;
            }
            RM_MapComponent_SightBlockGrid grid = RM_MapComponent_SightBlockGrid.For(map);
            if (grid != null && grid.BlockedCellCount != 0
                && grid.WalkBlocks(start, end, startRect, endRect, RM_CreatureBehaviorsSettings.sightBlockCellsNeeded))
            {
                __result = false;
            }
        }
    }
}
