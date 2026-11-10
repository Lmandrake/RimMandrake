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
            if (!__result && RM_PitPrisonCare.LipCare(p) && p.guest.CanBeBroughtFood
                && (p.Downed || HealthAIUtility.ShouldSeekMedicalRest(p))) __result = true;
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

    // Both the work scanner and the driver's path validation ask this seam. Redirect the target,
    // then let vanilla and the existing cliff/wall vetoes evaluate the actual route to the rim.
    // No blanket reachability override: an inaccessible rim still refuses, as does a prisoner
    // in the middle of a hole too wide for an adjacent lip.
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
            if (RM_PitRooms.TryFindLipCell(worker, patient.Position, RM_PitRoomMath.LipKind.Touch, out IntVec3 lip))
            {
                dest = lip;
                peMode = PathEndMode.OnCell;
            }
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
