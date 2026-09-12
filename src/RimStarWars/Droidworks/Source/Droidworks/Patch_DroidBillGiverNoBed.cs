using System;
using HarmonyLib;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_WIPE_SEVERITY_1 (packet B10) - root cause of "the memory-wipe
    /// bill never completes." Not a WorkGiver_DoBill patient-selection quirk at
    /// all: read from source (RimSage), `Verse.Pawn.CurrentlyUsableForBills()` is
    ///
    ///     if (!this.InBed()) { JobFailReason.Is(NotSurgeryReadyTrans); return false; }
    ///     if (!InteractionCell.IsValid) { ...; return false; }
    ///     return true;
    ///
    /// and `Pawn.UsableForBillsAfterFueling()` (which `WorkGiver_DoBill.JobOnThing`
    /// checks before it will ever build a DoBill job) is a bare call to that same
    /// method. Every Droidworks surgery recipe (memory wipe, restraining bolt
    /// install/remove, reboot) is `targetsBodyPart false`, whole-pawn, and NONE of
    /// them require anesthesia or bed rest by design - but vanilla's own gate
    /// requires `InBed()` regardless, for every Pawn billGiver, no exceptions.
    ///
    /// And nothing ever puts a droid in a bed: Races_Base.xml sets
    /// `needsRest=false` (no organic drive to seek one), and
    /// `WorkGiver_TakeToBedToOperate.HasJobOnThing` (RimSage) refuses outright on
    /// `!pawn2.RaceProps.IsFlesh` - droids are `RSW_DW_FleshType_Droid`,
    /// `isOrganic:false` (Races_Base.xml), so `RaceProps.IsFlesh` is false and no
    /// colonist will ever haul one to a bed either. A droid patient is therefore
    /// permanently `!InBed()`, `CurrentlyUsableForBills()` permanently false, and
    /// `WorkGiver_DoBill.JobOnThing` returns null forever - matching exactly the
    /// symptom this session's live-verify passes hit twice (bill accepted onto
    /// the droid's BillStack, never once picked up by a doctor, no error, no
    /// JobFailReason visible because the WorkGiver bails out before reaching any
    /// of the reason-setting branches in `StartOrResumeBillJob`).
    ///
    /// Fix: skip only the `InBed()` half of vanilla's check for droid-fleshtype
    /// pawns - they don't need one - and keep the `InteractionCell.IsValid` half,
    /// which is a real reachability requirement (an unspawned or wall-embedded
    /// droid should still fail cleanly, not be picked). Same "is this pawn a
    /// droid" signal (`RaceProps.FleshType == RSW_DW_FleshType_Droid`) already
    /// used by `Patch_ShouldHaveNeed_Power`/`HediffComp_IonOverloadsDroid`. Every
    /// flesh/Humanlike pawn (real colonists, prisoners, animals) is untouched -
    /// the prefix returns true (run vanilla) for anything that isn't a droid.
    ///
    /// Live proof owed: this pass has no bridge access (another window is mid
    /// verification marathon). Owed - spawn a roaming, un-bedded droid with a
    /// pending RSW_DW_MemoryWipe bill next to an idle, skilled colonist and
    /// confirm the doctor actually starts and finishes the operation.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class DroidworksBillGiverBedGateMod
    {
        static DroidworksBillGiverBedGateMod()
        {
            var harmony = new Harmony("mandrake.rsw.droidworks.billgiverbed");
            try
            {
                Patch_DroidBillGiverNoBed.Apply(harmony);
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] Failed to apply the droid no-bed-required "
                    + "bill-giver fix - every droid surgery recipe (memory wipe, restraining bolt, reboot) "
                    + "will silently never be picked up by any doctor. " + ex);
            }
        }
    }

    public static class Patch_DroidBillGiverNoBed
    {
        public static void Apply(Harmony harmony)
        {
            var target = AccessTools.Method(typeof(Pawn), nameof(Pawn.CurrentlyUsableForBills));
            if (target == null)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] Pawn.CurrentlyUsableForBills not found by "
                    + "reflection - vanilla API has moved. Droid bed requirement NOT lifted; every "
                    + "Droidworks surgery recipe will silently never be picked up by any doctor.");
                return;
            }
            harmony.Patch(target,
                prefix: new HarmonyMethod(typeof(Patch_DroidBillGiverNoBed), nameof(Prefix)));
        }

        /// <summary>
        /// Returning false supplies our own <paramref name="__result"/> and skips
        /// vanilla entirely - only for droid-fleshtype pawns. Everything else
        /// (real colonists, prisoners, animals) returns true and runs vanilla
        /// unchanged, InBed() requirement intact.
        /// </summary>
        public static bool Prefix(Pawn __instance, ref bool __result)
        {
            if (__instance?.RaceProps?.FleshType != DroidworksDefOf.RSW_DW_FleshType_Droid)
                return true;

            if (!__instance.InteractionCell.IsValid)
            {
                JobFailReason.Is("CannotReach".Translate());
                __result = false;
                return false;
            }

            __result = true;
            return false;
        }
    }
}
