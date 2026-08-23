using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace JawaRules
{
    [StaticConstructorOnStartup]
    public static class JawaRulesMod
    {
        // The player's Jawa. Both Jawa_Colonist and the three Jawa_Tribal_* kinds
        // roll MandrakeJawa at 1.0; RimMandrakeJawa is the generated species-catalogue
        // twin and is NOT what our pawnkinds field. Keyed by name so a missing def is
        // a quiet no-op rather than a type-load failure.
        public const string JawaXenotype = "MandrakeJawa";

        static JawaRulesMod()
        {
            // 🔑 PATCHED BY HAND, NOT BY PatchAll, and the reason is the point.
            // A [HarmonyPatch] target is a STRING and the compiler never checks it. With
            // PatchAll a wrong name throws inside a static constructor, the CLR caches
            // that failure, and the WHOLE MOD is dead for the session - silently, in a
            // batched load, looking exactly like a mod that simply did nothing.
            // Resolving each target explicitly turns that into one named warning and
            // leaves the other rule working.
            var h = new Harmony("mandrake.jawarules");

            Apply(h, AccessTools.Method(typeof(WorkGiver_GrowerSow), "ExtraRequirements"),
                  typeof(Patch_GrowerSow_ExtraRequirements), "no-sow",
                  "armed for xenotype " + JawaXenotype);

            Apply(h, AccessTools.Method(typeof(PawnComponentsUtility), "CreateInitialComponents"),
                  typeof(Patch_CreateInitialComponents), "droid-relations",
                  "armed for humanlike pawns with no relations tracker");
        }

        // Two separate log lines on purpose: this assembly carries two unrelated rules
        // and a batched load has to be able to blame exactly one of them.
        private static void Apply(Harmony h, MethodBase target, Type patchClass,
                                  string rule, string detail)
        {
            if (target == null)
            {
                Log.Error("[JawaRules] " + rule + ": TARGET METHOD NOT FOUND — this rule is "
                          + "NOT in effect. A game update renamed it. The other rule in this "
                          + "assembly is unaffected.");
                return;
            }
            try
            {
                h.Patch(target, postfix: new HarmonyMethod(patchClass, "Postfix"));
                Log.Message("[JawaRules] " + rule + ": " + detail);
            }
            catch (Exception e)
            {
                Log.Error("[JawaRules] " + rule + ": patch FAILED, rule NOT in effect — "
                          + e.Message);
            }
        }

        public static bool IsJawa(Pawn pawn)
        {
            return pawn != null
                && pawn.genes != null
                && pawn.genes.Xenotype != null
                && pawn.genes.Xenotype.defName == JawaXenotype;
        }
    }

    // ⛔ NOT a postfix on WorkGiver_GrowerSow.ShouldSkip, which is what the item
    // specified. That class DOES NOT DECLARE ShouldSkip - only WorkGiver_GrowerHarvest
    // and WorkGiver_PlantsCut override it. Harmony resolving that name would have
    // walked up to WorkGiver.ShouldSkip and patched the BASE, which every work giver
    // in the game inherits: a Jawa would have stopped doing ALL WORK. Checked against
    // the 1.6 source before writing a line.
    //
    // ExtraRequirements IS declared on WorkGiver_GrowerSow, takes the pawn, and gates
    // the whole IPlantToGrowSettable - so one hook covers the growing zone AND the
    // hydroponics basin, because both arrive here as the same interface.
    //
    // ⚠️ What this deliberately does NOT touch: WorkGiver_GrowerHarvest and
    // WorkGiver_PlantsCut are separate classes, so harvesting, plant cutting and tree
    // chopping all survive. That was the explicit requirement and it is the failure
    // mode a work-tag ban would have hit.
    public static class Patch_GrowerSow_ExtraRequirements
    {
        public static void Postfix(Pawn pawn, ref bool __result)
        {
            if (__result && JawaRulesMod.IsJawa(pawn))
                __result = false;
        }
    }

    // PawnComponentsUtility.CreateInitialComponents creates pawn.relations only inside
    // `if (pawn.RaceProps.IsFlesh)`, and IsFlesh is FleshType.isOrganic
    // (RaceProperties.cs:340). MEASURED 2026-08-23: all four OuterRim droid races we
    // field report intelligence Humanlike and fleshType Asimov_Automaton, whose
    // isOrganic is FALSE - so every humanlike droid was generated with relations null.
    //
    // 🔑 The guard is Humanlike, not "is a droid". Vanilla mechanoids are Animal
    // intelligence, so they are untouched and keep having no relations, which is
    // correct for them. Anything humanlike enough to raid, be captured or hold a
    // social tab is humanlike enough to need the tracker.
    public static class Patch_CreateInitialComponents
    {
        public static void Postfix(Pawn pawn)
        {
            try
            {
                if (pawn != null
                    && pawn.RaceProps != null
                    && pawn.RaceProps.Humanlike
                    && pawn.relations == null)
                {
                    pawn.relations = new Pawn_RelationsTracker(pawn);
                }
            }
            catch (Exception e)
            {
                // Pawn generation is not a place to throw: a failure here would abort
                // the whole pawn and take a raid or a colonist with it.
                Log.WarningOnce("[JawaRules] could not add a relations tracker to "
                                + (pawn == null ? "a null pawn" : pawn.def?.defName)
                                + ": " + e.Message, 0x4A57A1);
            }
        }
    }
}
