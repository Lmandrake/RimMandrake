using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
    /// <summary>The hole is the prison (owner card 2026-11-05). Keep vanilla food selection,
    /// reservations, diets, feeding and tending; supply the missing bedless-room/lip seams.</summary>
    public static class RM_PitPrisonCare
    {
        public static bool PrisonRoom(Room room) => RM_PitRooms.RoomsOn && room != null
            && room.ProperRoom && RM_PitRooms.IsPitRoom(room);

        public static bool Kept(Pawn p) => p != null && p.Spawned && p.IsPrisonerOfColony
            && p.guest.PrisonerIsSecure && PrisonRoom(p.GetRoom()) && RM_SuperdeepTrap.IsHeld(p)
            && RM_PitRooms.HoldsBySize(p);

        public static bool LipCare(Pawn p) => RimMandrakeFlowWorksSettings.wardenFromLipEnabled && Kept(p);

        public static bool TryFindMealLip(Pawn worker, Pawn patient, out IntVec3 lip)
        {
            return RM_PitRooms.TryFindLipCell(worker, patient.Position, RM_PitRoomMath.LipKind.Touch, out lip)
                || RM_PitRooms.TryFindLipCell(worker, patient.Position, RM_PitRoomMath.LipKind.Interact, out lip, rimOnly: true);
        }
    }

    [HarmonyPatch(typeof(Room), nameof(Room.IsPrisonCell), MethodType.Getter)]
    [RimMandrake.Shared.PatchFeature("Enclosed pits are bedless prisons", typeof(RimMandrakeFlowWorksSettings), "superdeepRoomsEnabled")]
    public static class RM_Patch_PitPrisonRoom
    {
        [HarmonyPostfix]
        public static void Postfix(Room __instance, ref bool __result)
        {
            if (!__result && RM_PitPrisonCare.PrisonRoom(__instance)) __result = true;
        }
    }

    [HarmonyPatch(typeof(WorkGiver_Warden_TakeToBed), nameof(WorkGiver_Warden_TakeToBed.TryMakeJob))]
    [RimMandrake.Shared.PatchFeature("Pit prisoners stay in their hole", typeof(RimMandrakeFlowWorksSettings), "superdeepRoomsEnabled")]
    public static class RM_Patch_PitPrisonStay
    {
        [HarmonyPrefix]
        public static bool Prefix(Thing t, ref Job __result)
        {
            if (!RM_PitPrisonCare.Kept(t as Pawn)) return true;
            __result = null;
            return false;
        }
    }

    [HarmonyPatch(typeof(WardenFeedUtility), nameof(WardenFeedUtility.ShouldBeFed))]
    [RimMandrake.Shared.PatchFeature("Feed downed pit prisoners without beds", typeof(RimMandrakeFlowWorksSettings), "wardenFromLipEnabled")]
    public static class RM_Patch_PitPrisonFeed
    {
        [HarmonyPostfix]
        public static void Postfix(Pawn p, ref bool __result)
        {
            // RIMMANDRAKE_TRACE_FLOWWORKS_AWAKE_PRISONER_MEAL_SKIPPED_ONE_RUN_IN_TWO: never a standing prisoner (vanilla's first
            // rule), who then gets food brought; LipCare first, so a pawn with no guest tracker never reads it
            if (!__result && RM_PitPrisonCare.LipCare(p) && RM_PitRoomMath.HandFedInPit(true, p.guest.CanBeBroughtFood, p.Downed,
                p.GetPosture() == PawnPosture.Standing, HealthAIUtility.ShouldSeekMedicalRest(p))) __result = true;
        }
    }

    [HarmonyPatch(typeof(WorkGiver_Tend), nameof(WorkGiver_Tend.GoodLayingStatusForTend))]
    [RimMandrake.Shared.PatchFeature("Tend pit prisoners without beds", typeof(RimMandrakeFlowWorksSettings), "wardenFromLipEnabled")]
    public static class RM_Patch_PitPrisonTend
    {
        [HarmonyPostfix]
        public static void Postfix(Pawn patient, ref bool __result)
        {
            if (!__result && RM_PitPrisonCare.LipCare(patient) && patient.Downed) __result = true;
        }
    }

    // The food work givers already check CanReserveAndReach in JobOnThing. Let them do that check
    // even when the prisoner's region is outside the scanner's reachable regions.
    [HarmonyPatch(typeof(WorkGiver_Scanner), nameof(WorkGiver_Scanner.AllowUnreachable), MethodType.Getter)]
    [RimMandrake.Shared.PatchFeature("Scan for prisoner meals from the rim", typeof(RimMandrakeFlowWorksSettings), "wardenFromLipEnabled")]
    public static class RM_Patch_PitPrisonMealScanner
    {
        [HarmonyPostfix]
        public static void Postfix(WorkGiver_Scanner __instance, ref bool __result)
        {
            if (RimMandrakeFlowWorksSettings.wardenFromLipEnabled && RM_PitRooms.RoomsOn
                && (__instance is WorkGiver_Warden_Feed || __instance is WorkGiver_Warden_DeliverFood)) __result = true;
        }
    }

    // Scope the longer reach to the food work giver's query for its prisoner.
    [HarmonyPatch]
    [RimMandrake.Shared.PatchFeature("Find a rim for prisoner meals", typeof(RimMandrakeFlowWorksSettings), "wardenFromLipEnabled")]
    public static class RM_Patch_PitPrisonMealScan
    {
        [ThreadStatic]
        private static Thing prisoner;

        public static bool IsScanning(Thing target) => target == prisoner;

        private static IEnumerable<MethodBase> TargetMethods()
        {
            yield return AccessTools.Method(typeof(WorkGiver_Warden_Feed), nameof(WorkGiver_Warden_Feed.JobOnThing));
            yield return AccessTools.Method(typeof(WorkGiver_Warden_DeliverFood), nameof(WorkGiver_Warden_DeliverFood.JobOnThing));
        }

        [HarmonyPrefix]
        public static void Prefix(Thing t, out Thing __state)
        {
            __state = prisoner;
            prisoner = t;
        }

        [HarmonyFinalizer]
        public static void Finalizer(Thing __state) => prisoner = __state;
    }

    // Redirect the reach check so vanilla and the cliff/wall vetoes can evaluate the real route to the rim.
    [HarmonyPatch(typeof(Reachability), nameof(Reachability.CanReach),
        new[] { typeof(IntVec3), typeof(LocalTargetInfo), typeof(PathEndMode), typeof(TraverseParms) })]
    [RimMandrake.Shared.PatchFeature("Prisoner care reaches the rim", typeof(RimMandrakeFlowWorksSettings), "wardenFromLipEnabled")]
    public static class RM_Patch_PitPrisonReach
    {
        [HarmonyPrefix]
        public static void Prefix(ref LocalTargetInfo dest, ref PathEndMode peMode, TraverseParms traverseParams)
        {
            Pawn worker = traverseParams.pawn;
            if (worker == null || !worker.Spawned || worker.Faction != Faction.OfPlayer
                || !dest.HasThing || !(dest.Thing is Pawn patient) || worker.Map != patient.Map
                || !RM_PitPrisonCare.LipCare(patient)) return;
            IntVec3 lip;
            if (peMode == PathEndMode.OnCell && RM_Patch_PitPrisonMealScan.IsScanning(patient)
                ? RM_PitPrisonCare.TryFindMealLip(worker, patient, out lip)
                : RM_PitRooms.TryFindLipCell(worker, patient.Position, RM_PitRoomMath.LipKind.Touch, out lip))
            {
                dest = lip;
                peMode = PathEndMode.OnCell;
            }
        }
    }

    [HarmonyPatch(typeof(ReachabilityImmediate), nameof(ReachabilityImmediate.CanReachImmediate),
        new[] { typeof(IntVec3), typeof(LocalTargetInfo), typeof(Map), typeof(PathEndMode), typeof(Pawn) })]
    [RimMandrake.Shared.PatchFeature("Feed pit prisoners within sight of the rim", typeof(RimMandrakeFlowWorksSettings), "wardenFromLipEnabled")]
    public static class RM_Patch_PitPrisonMealTouch
    {
        [HarmonyPostfix]
        public static void Postfix(IntVec3 start, LocalTargetInfo target, Map map, PathEndMode peMode, Pawn pawn, ref bool __result)
        {
            // FeedPatient's chew toil rechecks Touch even after the warden walked to the selected rim.
            if (!__result && peMode == PathEndMode.Touch && target.Thing is Pawn patient && patient.Map == map
                && pawn?.CurJob is Job job && job.def == JobDefOf.FeedPatient && job.targetB.Thing == patient && pawn.Faction == Faction.OfPlayer
                && start == pawn.Position && !start.AdjacentTo8WayOrInside(patient.Position) && RM_PitPrisonCare.LipCare(patient)
                && RM_PitRooms.InReachFromRim(map, start, patient.Position)) __result = true;
        }
    }

    [HarmonyPatch(typeof(WorkGiver_Warden_DeliverFood), nameof(WorkGiver_Warden_DeliverFood.JobOnThing))]
    [RimMandrake.Shared.PatchFeature("Drop prisoner food into the hole", typeof(RimMandrakeFlowWorksSettings), "wardenFromLipEnabled")]
    public static class RM_Patch_PitPrisonFoodDrop
    {
        [HarmonyPostfix]
        public static void Postfix(Thing t, Job __result)
        {
            // Vanilla delivers to target C, which can otherwise be a chewing spot OUTSIDE the pit.
            if (__result != null && RM_PitPrisonCare.LipCare(t as Pawn)) __result.targetC = t.Position;
        }
    }
}
