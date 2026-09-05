using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// `RSW_DW_Power` (NeedDefs_Droidworks.xml) carries no gating field of
    /// its own - no minIntelligence, hediffRequiredAny, colonistsOnly,
    /// requiredComps. Verified against Pawn_NeedsTracker.ShouldHaveNeed
    /// (RimSage): with every gate left at default, the method falls through
    /// to `return true;` for every pawn in the game - human, animal,
    /// mechanoid alike. Left ungated, every pawn would get RSW_DW_Power,
    /// drain it in about 1.5 in-game days (Need_Power's fallback rate for a
    /// pawn with no DroidworksExtension), and never recover, since
    /// Recipe_RebootDroid is wired only onto Droidworks race ThingDefs' own
    /// `<recipes>` list.
    ///
    /// Rather than retrofit every existing/future Droidworks race def with
    /// a new gating hediff or NeedDef field, this postfixes the one method
    /// that decides need eligibility and narrows RSW_DW_Power specifically
    /// to FleshType == RSW_DW_FleshType_Droid - the same "is this pawn a
    /// droid" signal HediffComp_IonOverloadsDroid already uses.
    ///
    /// This same bootstrap also carries the Humanlike-and-non-flesh
    /// pawn.relations fix (see Patch_RelationsForNonFleshHumanlike below) -
    /// same reasoning RimUtinni.Doctrine's identical fix documents for the
    /// already-shipped OuterRim/KotOR droids, applied locally so Droidworks
    /// does not depend on that mod being active. The postfix there is
    /// idempotent (a no-op once pawn.relations is non-null), so both mods
    /// patching it if both are active is harmless.
    ///
    /// Same bootstrap shape as BoltCorePatches.cs (a static Apply(Harmony)
    /// called from a [StaticConstructorOnStartup] wrapper, try/catch'd) -
    /// a separate Harmony instance rather than reusing BoltCore's, since
    /// that lives in a different sub-project (net48, Source/BoltCore/) and
    /// this fix belongs with Need_Power.cs in the main net472 assembly.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class DroidworksNeedGateMod
    {
        static DroidworksNeedGateMod()
        {
            var harmony = new Harmony("mandrake.rsw.droidworks.needgate");
            try
            {
                Patch_ShouldHaveNeed_Power.Apply(harmony);
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] Failed to apply RSW_DW_Power need gate - "
                    + "EVERY PAWN may get this need with no way to clear it. " + ex);
            }

            try
            {
                Patch_RelationsForNonFleshHumanlike.Apply(harmony);
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] Failed to apply the non-flesh-Humanlike "
                    + "relations fix - droid pawns may NRE the first time anything touches pawn.relations. " + ex);
            }
        }
    }

    public static class Patch_ShouldHaveNeed_Power
    {
        public static void Apply(Harmony harmony)
        {
            var target = AccessTools.Method(typeof(Pawn_NeedsTracker), "ShouldHaveNeed");
            if (target == null)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] Pawn_NeedsTracker.ShouldHaveNeed not found "
                    + "by reflection - vanilla API has moved. RSW_DW_Power need gate NOT applied.");
                return;
            }
            harmony.Patch(target, postfix: new HarmonyMethod(typeof(Patch_ShouldHaveNeed_Power), nameof(Postfix)));
        }

        public static void Postfix(NeedDef nd, Pawn ___pawn, ref bool __result)
        {
            if (!__result) return;
            if (nd != DroidworksDefOf.RSW_DW_Power) return;
            if (___pawn?.RaceProps?.FleshType != DroidworksDefOf.RSW_DW_FleshType_Droid)
            {
                __result = false;
            }
        }
    }

    /// <summary>
    /// Vanilla `PawnComponentsUtility.CreateInitialComponents` only
    /// allocates `pawn.relations` `if (pawn.RaceProps.IsFlesh)`, but
    /// Humanlike-intelligence pawn generation assumes every Humanlike has
    /// one regardless of fleshtype. DW_Race_Base is Humanlike AND
    /// isOrganic:false (Races_Base.xml), so without this postfix every
    /// Droidworks pawn's `pawn.relations` is permanently null and NREs the
    /// first time anything touches it (LovePartnerRelationUtility,
    /// AlienRace's own gender-generation patches, etc).
    ///
    /// DROID_PSYCHICENTROPY_NULL_GAP_1: `pawn.psychicEntropy` is allocated in
    /// the SAME `IsFlesh` block (also gated on `ModsConfig.RoyaltyActive` -
    /// mirrored exactly below, so this stays a no-op without Royalty, same as
    /// vanilla) and was not backfilled here. Droids are Humanlike, so vanilla
    /// Royalty allocates `pawn.royalty` for them regardless of fleshtype; if
    /// a droid ever receives a title/psycast (quest reward, a mod), every
    /// caller that dereferences `pawn.psychicEntropy.*` (Verb_CastPsycast,
    /// Command_Psycast, CompAbilityEffect_TransferEntropy) NREs on a droid
    /// with Royalty active, the same class of gap the relations fix closes.
    /// </summary>
    public static class Patch_RelationsForNonFleshHumanlike
    {
        public static void Apply(Harmony harmony)
        {
            var target = AccessTools.Method(typeof(PawnComponentsUtility),
                nameof(PawnComponentsUtility.CreateInitialComponents));
            if (target == null)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] PawnComponentsUtility.CreateInitialComponents "
                    + "not found by reflection - vanilla API has moved. Non-flesh-Humanlike relations fix NOT applied.");
                return;
            }
            harmony.Patch(target,
                postfix: new HarmonyMethod(typeof(Patch_RelationsForNonFleshHumanlike), nameof(Postfix)));
        }

        public static void Postfix(Pawn pawn)
        {
            if (pawn?.RaceProps == null) return;
            if (!pawn.RaceProps.Humanlike) return;
            if (pawn.RaceProps.IsFlesh) return;   // vanilla's own branch already allocated it

            if (pawn.relations == null)
                pawn.relations = new Pawn_RelationsTracker(pawn);

            // DROID_PSYCHICENTROPY_NULL_GAP_1: same RoyaltyActive gate vanilla
            // itself uses for flesh pawns, so this is still a no-op without
            // Royalty active - exactly matching what a flesh pawn would have.
            if (ModsConfig.RoyaltyActive && pawn.psychicEntropy == null)
                pawn.psychicEntropy = new Pawn_PsychicEntropyTracker(pawn);
        }
    }
}
