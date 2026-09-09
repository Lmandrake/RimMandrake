using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.MovingDunes
{
    /// <summary>
    /// Bootstrap. Four small Harmony patches plus one def-database pass, each armed
    /// independently with the FireEcology loud-failure pattern: if a target method is
    /// gone (a game update renamed it), THAT rule logs an error and stays off while the
    /// others keep working. Nothing here fails silently — MOVING_DUNES_DESIGN.md §2
    /// asks for exactly that, because two of the patches ride exact vanilla constants.
    ///
    /// The whole mod is inert without Odyssey: <c>SandGrid</c>'s NativeArray is never
    /// created (<c>ModLister.CheckOdyssey("sand")</c>), every grid call no-ops, and
    /// <see cref="MapComponent_DuneField"/> refuses to arm. That is the honest price of
    /// riding Odyssey's channel instead of building a parallel grid (design §2).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class MovingDunesMod
    {
        public const string HarmonyId = "mandrake.rm.movingdunes";
        internal const string LogPrefix = "[RimMandrake.MovingDunes] ";

        /// <summary>Vanilla's ambient sand decay, one cell-visit's worth, from
        /// <c>SteadyEnvironmentEffects.DoCellSteadyEffects</c>: <c>-1f/180f</c>, applied
        /// both outdoors in clear weather and always indoors. The AddDepth prefix
        /// recognises the decay call by this exact value; see
        /// <c>selftest_moving_dunes_constants.py</c>, which fails the moment the
        /// decompiled source stops saying it.</summary>
        internal const float VanillaAmbientSandDecay = -1f / 180f;

        /// <summary>Tolerance for recognising the decay constant through float
        /// round-tripping. Far tighter than any deliberate caller's step.</summary>
        internal const float AmbientDecayEpsilon = 1e-7f;

        /// <summary>True once the CanHaveSand prefix is armed. If it is not, a desert
        /// map's sand terrain refuses to hold sand and the whole engine is decorative —
        /// the transport component says so once, loudly, rather than drifting nothing
        /// in silence.</summary>
        internal static bool CanHaveSandPatchArmed;

        /// <summary>True once the ambient-decay suppression is armed. Without it a
        /// full-depth drift evaporates in about five clear-weather days.</summary>
        internal static bool DecaySuppressionArmed;

        /// <summary>True once the vanilla sand layer is suppressed on skinned maps.
        /// Without it the vanilla and skinned layers double-draw.</summary>
        internal static bool VanillaLayerSuppressionArmed;

        static MovingDunesMod()
        {
            Harmony h = new Harmony(HarmonyId);

            CanHaveSandPatchArmed = Apply(
                h,
                AccessTools.Method(typeof(SandGrid), "CanHaveSand", new[] { typeof(int) }),
                typeof(Patch_SandGrid_CanHaveSand), prefix: true,
                rule: "sand-holds-on-sand",
                detail: "armed; on a dune-field map, Sand and SoftSand terrain hold depth "
                        + "(water, space and full-fillage buildings still refuse it)");

            DecaySuppressionArmed = Apply(
                h,
                AccessTools.Method(typeof(SandGrid), "AddDepth",
                                   new[] { typeof(IntVec3), typeof(float) }),
                typeof(Patch_SandGrid_AddDepth), prefix: true,
                rule: "ambient-decay-suppression",
                detail: "armed; vanilla's -1/180 per-cell-visit sand decay is scaled by the "
                        + "map material's ambientDecayFactor (0 = drifts persist)");

            VanillaLayerSuppressionArmed = Apply(
                h,
                AccessTools.Method(typeof(SectionLayer_Sand), "Regenerate"),
                typeof(Patch_SectionLayerSand_Regenerate), prefix: true,
                rule: "vanilla-sand-layer-suppression",
                detail: "armed; the vanilla sand submesh is disabled on skinned maps so the "
                        + "tinted layer never double-draws");

            ApplyHideDepths();
        }

        private static bool Apply(Harmony h, MethodBase target, Type patchClass, bool prefix,
                                  string rule, string detail)
        {
            if (target == null)
            {
                Log.Error(LogPrefix + rule + ": TARGET METHOD NOT FOUND — this rule is NOT in "
                          + "effect. A game update renamed or resigned it. Every other rule in "
                          + "this assembly is unaffected.");
                return false;
            }
            try
            {
                HarmonyMethod m = new HarmonyMethod(patchClass, prefix ? "Prefix" : "Postfix");
                h.Patch(target, prefix: prefix ? m : null, postfix: prefix ? null : m);
                Log.Message(LogPrefix + rule + ": " + detail);
                return true;
            }
            catch (Exception e)
            {
                Log.Error(LogPrefix + rule + ": patch FAILED, rule NOT in effect — " + e.Message);
                return false;
            }
        }

        /// <summary>
        /// Sets <c>ThingDef.hideAtSnowOrSandDepth</c> across the def database so buried
        /// things stop being drawn. Vanilla honours the field in all three drawers
        /// (<c>SectionLayer_Things</c>, <c>DynamicDrawManager</c>, <c>Plant.Draw</c>),
        /// so the whole visual-burial behaviour is a field, not code.
        ///
        /// DEVIATION from MOVING_DUNES_DESIGN.md §2, recorded deliberately: the design
        /// says "we set it by XML patch on the categories we bury". An xpath cannot see
        /// <c>category</c> on the great majority of item defs, because they inherit it
        /// from an abstract parent and PatchOperations run BEFORE inheritance resolves —
        /// a patch that matches nothing logs nothing, which is the exact silent failure
        /// this mod's loud-failure discipline exists to avoid. A startup pass over
        /// <c>DefDatabase</c> reads post-inheritance truth and reports its own count.
        ///
        /// Only defs still carrying vanilla's 99999 default are touched, so any def that
        /// states its own opinion (vanilla's or another mod's) keeps it.
        /// </summary>
        private static void ApplyHideDepths()
        {
            RM_DuneGlobalsDef globals = DefDatabase<RM_DuneGlobalsDef>.GetNamedSilentFail("RM_Dunes_Globals");
            if (globals == null)
            {
                Log.Error(LogPrefix + "hide-depths: RM_Dunes_Globals is missing — buried things "
                          + "will keep drawing on top of the sand that swallowed them. The rest of "
                          + "the engine is unaffected.");
                return;
            }
            if (!globals.applyHideDepths)
            {
                Log.Message(LogPrefix + "hide-depths: disabled by RM_Dunes_Globals.applyHideDepths.");
                return;
            }

            const float VanillaDefault = 99999f;
            int items = 0, plants = 0, filth = 0;
            List<ThingDef> all = DefDatabase<ThingDef>.AllDefsListForReading;
            for (int i = 0; i < all.Count; i++)
            {
                ThingDef d = all[i];
                if (d.hideAtSnowOrSandDepth < VanillaDefault)
                {
                    continue;
                }
                if (d.category == ThingCategory.Plant)
                {
                    d.hideAtSnowOrSandDepth = globals.plantHideDepth;
                    plants++;
                }
                else if (d.category == ThingCategory.Filth)
                {
                    d.hideAtSnowOrSandDepth = globals.filthHideDepth;
                    filth++;
                }
                else if (d.category == ThingCategory.Item)
                {
                    d.hideAtSnowOrSandDepth = globals.itemHideDepth;
                    items++;
                }
            }

            if (items + plants + filth == 0)
            {
                Log.Error(LogPrefix + "hide-depths: MEASURED ZERO defs updated out of " + all.Count
                          + " ThingDefs. Either every def already states its own depth, or the "
                          + "category test is wrong. Nothing will visually bury.");
                return;
            }
            Log.Message(LogPrefix + "hide-depths: " + items + " items @" + globals.itemHideDepth
                        + ", " + plants + " plants @" + globals.plantHideDepth
                        + ", " + filth + " filth @" + globals.filthHideDepth
                        + " (of " + all.Count + " ThingDefs; defs with their own value untouched).");
        }
    }

    [DefOf]
    public static class MovingDunesDefOf
    {
        /// <summary>The container a buried stack becomes. Not a building: it must sit on
        /// a cell without zeroing that cell's sand depth, which any full-fillage edifice
        /// would do.</summary>
        public static ThingDef RM_Dunes_BuriedCache;

        /// <summary>The engine's own default material: plain desert sand, untinted.</summary>
        public static RM_DuneMaterialDef RM_Dunes_Sand;

        static MovingDunesDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(MovingDunesDefOf));
        }
    }
}
