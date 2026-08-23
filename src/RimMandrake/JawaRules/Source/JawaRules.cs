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

            Apply(h, AccessTools.Method(typeof(Pawn), "GenerateNecessaryName"),
                  typeof(Patch_GenerateNecessaryName), "pet-names",
                  "armed; tamed and newborn animals will draw from their race namer");
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

    // STAR_WARS_PET_NAMES_1, part 3 of 3. The corpus is a RulePackDef and the patch
    // points the races at it - but BOTH moments the owner named would ignore it.
    //
    // 🔴 WHY DEF XML ALONE CANNOT DELIVER THIS. Read from the 1.6 source:
    //   TAMED  -> InteractionWorker_RecruitAttempt.DoRecruit -> RecruitUtility.Recruit
    //             -> Pawn.SetFaction -> Pawn.GenerateNecessaryName()
    //   BORN   -> PawnGenerator.GeneratePawn -> the same GenerateNecessaryName()
    // and that method hard-codes NameStyle.Numeric - literally "Dromedary 1". The
    // race's nameGenerator is NEVER consulted on either path. The only routine
    // vanilla route that reads it is the BOND relation, which is rare and already
    // works with no code at all.
    //
    // ⚠️ GenerateNecessaryName is a short non-virtual method and the JIT MAY INLINE
    // it into SetFaction. Harmony does not error when its target was inlined - it
    // silently does nothing, which is this project's most-paid-for failure class.
    // If the next load still shows "Dromedary 1", that is the cause, and the fallback
    // is a postfix on PawnBioAndNameGenerator.GeneratePawnName guarded on
    // style == NameStyle.Numeric - a much larger method and far less inline-prone.
    // The Apply() line above will still say "armed", because being patched and being
    // REACHED are different claims. Only the in-game name settles it.
    public static class Patch_GenerateNecessaryName
    {
        public static void Postfix(Pawn __instance)
        {
            try
            {
                var p = __instance;
                if (p == null || p.RaceProps == null) return;

                // ⛔ Animals only. GenerateNecessaryName also fires for Biotech MECHS,
                // and a mechanoid called "Warranty Void" is a different feature.
                if (!p.RaceProps.Animal) return;
                if (p.Faction == null || p.Faction != Faction.OfPlayer) return;

                // Only replace a name nobody chose. A bonded animal already has a real
                // name from the Full path, and a player rename must never be clobbered.
                if (p.Name != null && !p.Name.Numerical) return;

                var namer = p.RaceProps.GetNameGenerator(p.gender);
                if (namer == null) return;

                string n = NameGenerator.GenerateName(
                    namer, x => !new NameSingle(x).UsedThisGame);
                if (!string.IsNullOrEmpty(n))
                    p.Name = new NameSingle(n);
            }
            catch (Exception e)
            {
                // Naming is cosmetic; taming and birth are not. Never throw here.
                Log.WarningOnce("[JawaRules] pet-names: " + e.Message, 0x4A57A2);
            }
        }
    }
}
