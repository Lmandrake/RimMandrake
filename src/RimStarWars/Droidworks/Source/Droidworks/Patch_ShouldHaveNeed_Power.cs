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

            try
            {
                Patch_ApparelForDroids.Apply(harmony);
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] Failed to apply the droid apparel gate lift - "
                    + "every Droidworks pawn will spawn with no apparel regardless of apparelTags/apparelMoney. " + ex);
            }

            try
            {
                Patch_SkipRelationGenerationForDroids.Apply(harmony);
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] Failed to apply the droid sibling-relation NRE "
                    + "guard - droid pawn generation may intermittently NRE in "
                    + "PawnRelationWorker_Sibling.CreateRelation (DROID_SIBLING_RELATION_GEN_CRASH_1). " + ex);
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

    /// <summary>
    /// DROID_SIBLING_RELATION_GEN_CRASH_1.
    ///
    /// `PawnRelationWorker_Sibling.CreateRelation` (RimWorld/PawnRelationWorker_Sibling.cs)
    /// never null-checks what its own `GenerateParent` helper returns:
    ///
    ///     Pawn newMother = GenerateParent(generated, other, Gender.Female, request, flag2);
    ///     other.SetMother(newMother);   // NRE if newMother is null
    ///
    /// `GenerateParent` fixes the requested parent's gender explicitly on a nested
    /// `PawnGenerationRequest` (`fixedGender: genderToGenerate`), so
    /// `RaceProperties.hasGenders` is never even consulted on this path - a `hasGenders`
    /// fix was tried and confirmed not to help. Every Droidworks race restricts
    /// `<bodyTypes Inherit="False">`/`<headTypes Inherit="False">` to a single gender
    /// (Defs/Races_Base.xml), so nested generation for the opposite-gender parent fails
    /// after RimWorld's internal retry cap and `PawnGenerator.GeneratePawn` returns null
    /// - which `CreateRelation` then dereferences.
    ///
    /// `PawnGenerator.GeneratePawnRelations` (Verse/PawnGenerator.cs:2049) gates the
    /// entire relations pass on `RaceProps.Humanlike` alone, and every Droidworks race
    /// keeps `Humanlike=true` (needed for the mood/personality system), so every droid
    /// pawn attempts family-relation generation exactly like a human despite having no
    /// biological family. Other `PawnRelationWorker_*` subtypes reached from the same
    /// method share the identical "trust GenerateParent's/other lookup's return value"
    /// shape, so this prefixes the one shared gate rather than patching
    /// `PawnRelationWorker_Sibling` (and every sibling class) individually - the same
    /// "is this pawn a droid" signal `Patch_ShouldHaveNeed_Power` and
    /// `HediffComp_IonOverloadsDroid` already use. `GeneratePawnRelations` is `private`;
    /// other mods already prefix this exact method (VEF's `DisableRelations`, AlienRace's
    /// `GeneratePawnRelationsPrefix` - both visible in this bug's own log stack trace),
    /// confirming it is a stable, reachable Harmony target.
    /// </summary>
    public static class Patch_SkipRelationGenerationForDroids
    {
        public static void Apply(Harmony harmony)
        {
            var target = AccessTools.Method(typeof(PawnGenerator), "GeneratePawnRelations",
                new[] { typeof(Pawn), typeof(PawnGenerationRequest).MakeByRefType() });
            if (target == null)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] PawnGenerator.GeneratePawnRelations not found "
                    + "by reflection - vanilla API has moved. Droid sibling-relation NRE guard NOT applied.");
                return;
            }
            harmony.Patch(target,
                prefix: new HarmonyMethod(typeof(Patch_SkipRelationGenerationForDroids), nameof(Prefix)));
        }

        /// <summary>
        /// Returning false skips vanilla's relation-generation pass entirely for
        /// droid-fleshtype pawns - no siblings, no non-family relations, no NRE. Every
        /// other Humanlike race (and any droid race not yet retagged) is untouched.
        /// </summary>
        public static bool Prefix(Pawn pawn)
        {
            if (pawn?.RaceProps?.FleshType == DroidworksDefOf.RSW_DW_FleshType_Droid)
                return false;
            return true;
        }
    }
}
