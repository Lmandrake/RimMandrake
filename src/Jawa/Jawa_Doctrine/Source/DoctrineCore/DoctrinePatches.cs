using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace JawaDoctrineCore
{
    /// <summary>
    /// Harmony bootstrap for Jawa_Doctrine's own C# fixes.
    /// [StaticConstructorOnStartup], same pattern as
    /// Droidworks/Source/BoltCore/BoltCorePatches.cs.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class JawaDoctrineCoreMod
    {
        static JawaDoctrineCoreMod()
        {
            var harmony = new Harmony("mandrake.jawadoctrine.core");
            try
            {
                DoctrinePatches.Apply(harmony);
            }
            catch (Exception ex)
            {
                Log.Error("[JawaDoctrineCore] Failed to apply patches: " + ex);
            }

            try
            {
                // COLONY_VISIBILITY_STAT_1 - safe-core GameComponent needs no
                // patch to register (see ColonyVisibility.cs), but the F12
                // raid-point replacement and Ta'Baa launch-reset hook do.
                ColonyVisibilityRaidPatch.Apply(harmony);
            }
            catch (Exception ex)
            {
                Log.Error("[JawaDoctrineCore] Failed to apply Colony Visibility patches: " + ex);
            }
        }
    }

    /// <summary>
    /// DROIDWORKS_ISFLESH_RELATIONS_CRASH_1. Vanilla PawnComponentsUtility.
    /// CreateInitialComponents only allocates pawn.relations
    /// "if (pawn.RaceProps.IsFlesh)". Jawa_Doctrine/Patches/DroidsAreMachines.xml
    /// sets isOrganic:false on every droid race project-wide (the ion capture
    /// pipeline needs IsFlesh==false to reach them) - but Humanlike-intelligence
    /// pawns go through full relation generation regardless of fleshtype
    /// (PawnGenerator.GeneratePawnRelations et al assume every Humanlike has a
    /// relations tracker), so a Humanlike + isOrganic:false pawn leaves
    /// pawn.relations permanently null and NREs the moment anything touches it -
    /// LovePartnerRelationUtility.HasAnyLovePartnerOfTheOppositeGender,
    /// AlienRace.HarmonyPatches.GenerationChanceGenderless, etc. Confirmed
    /// 10/10 in a batch test on the already-shipped OuterRim_BattleDroid
    /// (2026-08-30), so this is a live bug in the current campaign, not just
    /// future Droidworks content.
    ///
    /// Fix: a postfix that allocates pawn.relations for exactly the
    /// complementary case vanilla leaves uncovered - Humanlike AND !IsFlesh.
    /// The vanilla IsFlesh branch is never touched, so every flesh pawn and
    /// every true mechanoid keeps its existing (correct) behavior unchanged.
    /// </summary>
    public static class DoctrinePatches
    {
        public static void Apply(Harmony harmony)
        {
            var target = AccessTools.Method(typeof(PawnComponentsUtility),
                nameof(PawnComponentsUtility.CreateInitialComponents));
            if (target == null)
            {
                Log.Error("[JawaDoctrineCore] PawnComponentsUtility.CreateInitialComponents not found by "
                    + "reflection - vanilla API has moved. Non-flesh-Humanlike relations fix not applied.");
                return;
            }

            harmony.Patch(target,
                postfix: new HarmonyMethod(typeof(DoctrinePatches), nameof(Postfix)));
        }

        public static void Postfix(Pawn pawn)
        {
            if (pawn?.RaceProps == null) return;
            if (!pawn.RaceProps.Humanlike) return;
            if (pawn.RaceProps.IsFlesh) return;   // vanilla's own branch already allocated it
            if (pawn.relations != null) return;

            pawn.relations = new Pawn_RelationsTracker(pawn);
        }
    }
}
