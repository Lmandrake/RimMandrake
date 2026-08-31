using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.JawaRules
{
    [StaticConstructorOnStartup]
    public static class JawaRulesMod
    {
        // The player's Jawa. Both Jawa_Colonist and the three Jawa_Tribal_* kinds
        // roll RSW_MandrakeJawa at 1.0; RSW_RimMandrakeJawa is the generated species-catalogue
        // twin and is NOT what our pawnkinds field. Keyed by name so a missing def is
        // a quiet no-op rather than a type-load failure.
        public const string JawaXenotype = "RSW_MandrakeJawa";

        static JawaRulesMod()
        {
            // 🔑 PATCHED BY HAND, NOT BY PatchAll, and the reason is the point.
            // A [HarmonyPatch] target is a STRING and the compiler never checks it. With
            // PatchAll a wrong name throws inside a static constructor, the CLR caches
            // that failure, and the WHOLE MOD is dead for the session - silently, in a
            // batched load, looking exactly like a mod that simply did nothing.
            // Resolving each target explicitly turns that into one named warning and
            // leaves the other rule working.
            var h = new Harmony("mandrake.rsw.jawarules");

            Apply(h, AccessTools.Method(typeof(WorkGiver_GrowerSow), "ExtraRequirements"),
                  typeof(Patch_GrowerSow_ExtraRequirements), "no-sow",
                  "armed for xenotype " + JawaXenotype);

            Apply(h, AccessTools.Method(typeof(PawnComponentsUtility), "CreateInitialComponents"),
                  typeof(Patch_CreateInitialComponents), "droid-relations",
                  "armed for humanlike pawns with no relations tracker");

            Apply(h, AccessTools.Method(typeof(Pawn), "GenerateNecessaryName"),
                  typeof(Patch_GenerateNecessaryName), "pet-names",
                  "armed; tamed and newborn animals will draw from their race namer");

            ApplyTranspiler(h, AccessTools.Method(typeof(WorldFeatures), "UpdateAlpha"),
                  typeof(Patch_WorldFeatures_UpdateAlpha), "world-labels",
                  "armed; world feature names peak at "
                  + Patch_WorldFeatures_UpdateAlpha.WantedAlpha.ToString("0.00")
                  + " alpha instead of "
                  + Patch_WorldFeatures_UpdateAlpha.VanillaAlpha.ToString("0.00"));

            ApplyTranspiler(h, AccessTools.Method(typeof(WorldFeatureTextMesh_TextMeshPro),
                                                  "WrapAroundPlanetSurface"),
                  typeof(Patch_WorldFeatureText_Lift), "world-label-lift",
                  "armed; world feature names sit "
                  + Patch_WorldFeatureText_Lift.WantedLift.ToString("0.00")
                  + " above the surface instead of "
                  + Patch_WorldFeatureText_Lift.VanillaLift.ToString("0.00"));
        }

        // Two separate log lines on purpose: this assembly carries two unrelated rules
        // and a batched load has to be able to blame exactly one of them.
        private static void Apply(Harmony h, MethodBase target, Type patchClass,
                                  string rule, string detail)
        {
            if (target == null)
            {
                Log.Error("[RimMandrake.StarWars.JawaRules] " + rule + ": TARGET METHOD NOT FOUND — this rule is "
                          + "NOT in effect. A game update renamed it. The other rule in this "
                          + "assembly is unaffected.");
                return;
            }
            try
            {
                h.Patch(target, postfix: new HarmonyMethod(patchClass, "Postfix"));
                Log.Message("[RimMandrake.StarWars.JawaRules] " + rule + ": " + detail);
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.StarWars.JawaRules] " + rule + ": patch FAILED, rule NOT in effect — "
                          + e.Message);
            }
        }

        // ⚠️ Apply() above hardcodes a POSTFIX. This one exists because world-labels
        // needs a TRANSPILER and nothing else does - see that patch class for why a
        // postfix is the wrong instrument there rather than merely a different one.
        // Same contract: a missing target is one named error, not a dead assembly.
        private static void ApplyTranspiler(Harmony h, MethodBase target, Type patchClass,
                                            string rule, string detail)
        {
            if (target == null)
            {
                Log.Error("[RimMandrake.StarWars.JawaRules] " + rule + ": TARGET METHOD NOT FOUND — this rule is "
                          + "NOT in effect. A game update renamed it. The other rules in "
                          + "this assembly are unaffected.");
                return;
            }
            try
            {
                h.Patch(target, transpiler: new HarmonyMethod(patchClass, "Transpiler"));
                Log.Message("[RimMandrake.StarWars.JawaRules] " + rule + ": " + detail);
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.StarWars.JawaRules] " + rule + ": patch FAILED, rule NOT in effect — "
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
                Log.WarningOnce("[RimMandrake.StarWars.JawaRules] could not add a relations tracker to "
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
                Log.WarningOnce("[RimMandrake.StarWars.JawaRules] pet-names: " + e.Message, 0x4A57A2);
            }
        }
    }

    // 🔴 Owner, 2026-08-23: "make the world labels twice as opaque."
    //
    // The world labels are the italic names printed across the planet - the regions,
    // seas and ranges from `WorldFeature`. They peak at THIRTY PERCENT alpha:
    //
    //     WorldFeatures.cs:17   private const float BaseAlpha = 0.3f;
    //     WorldFeatures.cs:102  float num = 0.3f * feature.alpha;
    //
    // `feature.alpha` is the 0..1 FADE PROGRESS driven by camera altitude, not the
    // opacity - it reaches 1 and the text still draws at 0.3. So 0.3 is the ceiling
    // and it is the only number worth changing. Doubled: 0.60.
    //
    // ⛔ A POSTFIX IS THE WRONG INSTRUMENT HERE, AND NOT MERELY A DIFFERENT ONE.
    // The original writes the colour only when it has drifted:
    //     if (!Mathf.Approximately(text.Color.a, num)) { text.Color = …; text.WrapAroundPlanetSurface(…); }
    // A postfix that raised the alpha afterwards would leave `text.Color.a` at 0.6·a
    // while the original keeps computing 0.3·a, so that guard would MISS ON EVERY
    // FRAME - and `WrapAroundPlanetSurface` rebuilds the text mesh geometry. Two mesh
    // rebuilds per named feature per frame, for 71 features, to change one constant.
    //
    // ⇒ Transpile the constant instead. The guard keeps working, the cost is zero, and
    // there is exactly one `ldc.r4 0.3` in the method to hit. `BaseAlpha` being a const
    // means the compiler has already inlined it, so the literal is what is in the IL.
    //
    // ⚠️ IT COUNTS ITS OWN HITS AND SAYS SO. A transpiler that matches nothing returns
    // the method unchanged and Harmony reports SUCCESS - the silent-failure shape this
    // project keeps paying for. Anything other than exactly one substitution is a named
    // error in the log, and the IL is still returned intact so the game runs either way.
    public static class Patch_WorldFeatures_UpdateAlpha
    {
        public const float VanillaAlpha = 0.3f;
        public const float WantedAlpha = 0.6f;

        public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> src)
        {
            int hits = 0;
            foreach (var ins in src)
            {
                if (ins.opcode == OpCodes.Ldc_R4
                    && ins.operand is float f
                    && Mathf.Approximately(f, VanillaAlpha))
                {
                    hits++;
                    // Carry the labels and exception blocks across, or a branch target
                    // that pointed at this instruction lands nowhere.
                    var rep = new CodeInstruction(OpCodes.Ldc_R4, WantedAlpha);
                    rep.labels.AddRange(ins.labels);
                    rep.blocks.AddRange(ins.blocks);
                    yield return rep;
                    continue;
                }
                yield return ins;
            }

            if (hits != 1)
            {
                Log.Error("[RimMandrake.StarWars.JawaRules] world-labels: expected exactly ONE "
                          + VanillaAlpha.ToString("0.00") + " constant in "
                          + "WorldFeatures.UpdateAlpha and found " + hits
                          + ". The label opacity is NOT what was asked for. A game "
                          + "update changed the method; re-read it before trusting "
                          + "the 'armed' line above.");
            }
        }
    }

    // 🔴 Owner, 2026-08-24: "the labels for the world continue to intersect the surface …
    // They need to be slightly farther out from the planet."
    //
    // Every glyph of a world feature name is re-projected onto a shell just above the
    // planet, and the shell's height is one literal, written four times:
    //
    //     WorldFeatureTextMesh_TextMeshPro.cs:146-149
    //         …MultiplyPoint(…).normalized * (layer.Radius + 0.4f)
    //
    // For scale, the game's own shells around the same sphere are clouds at +0.2 and the
    // atmospheric glow at +16.1. So 0.4 is hard against the surface, and lifting it to
    // 1.5 leaves the text an order of magnitude clear of the terrain while staying ten
    // times below the glow.
    //
    // ⚠️ WHAT THIS DOES NOT CLAIM. A perfect sphere at +0.4 should not intersect a
    // terrain mesh whose vertices sit at exactly Radius - each glyph quad's four corners
    // are individually normalised onto the shell, so the chord sag inside one glyph is
    // ~0.1 at most. The observed intersection therefore has a cause this patch does not
    // identify, and raising the shell treats the symptom the owner reported rather than
    // that cause. ⇒ **If 1.5 does not clear it, the number is not the problem** - do not
    // simply keep raising it, because the labels will detach from the limb long before
    // an unrelated cause is fixed by brute force.
    //
    // ⛔ A POSTFIX CANNOT DO THIS, for the same structural reason as the alpha patch but
    // worse: WrapAroundPlanetSurface has already written the vertex buffer and called
    // UpdateVertexData by the time a postfix runs, so a postfix would have to walk and
    // rewrite every vertex of every glyph a second time, per rebuild.
    //
    // ⚠️ FOUR hits, not one - the literal appears once per quad corner. A count of
    // anything else means the method changed shape and is a named error, and the IL is
    // returned intact so the game still runs.
    //
    // ⭐ WorldFeatureTextMesh_Legacy.WrapAroundPlanetSurface is an EMPTY method body, so
    // there is deliberately nothing to patch on the legacy path. Its labels are not
    // wrapped onto the sphere at all and never were.
    public static class Patch_WorldFeatureText_Lift
    {
        public const float VanillaLift = 0.4f;
        public const float WantedLift = 1.5f;
        private const int ExpectedHits = 4;

        public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> src)
        {
            int hits = 0;
            foreach (var ins in src)
            {
                if (ins.opcode == OpCodes.Ldc_R4
                    && ins.operand is float f
                    && Mathf.Approximately(f, VanillaLift))
                {
                    hits++;
                    var rep = new CodeInstruction(OpCodes.Ldc_R4, WantedLift);
                    rep.labels.AddRange(ins.labels);
                    rep.blocks.AddRange(ins.blocks);
                    yield return rep;
                    continue;
                }
                yield return ins;
            }

            if (hits != ExpectedHits)
            {
                Log.Error("[RimMandrake.StarWars.JawaRules] world-label-lift: expected exactly " + ExpectedHits
                          + " " + VanillaLift.ToString("0.00") + " constants in "
                          + "WorldFeatureTextMesh_TextMeshPro.WrapAroundPlanetSurface and "
                          + "found " + hits + ". The labels are NOT lifted, or are lifted "
                          + "on only some corners, which would SHEAR the glyphs. Re-read "
                          + "the method before trusting the 'armed' line above.");
            }
        }
    }
}
