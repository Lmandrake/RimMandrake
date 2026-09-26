using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Cuisine glow-hediff families (spec §6.3) each carry one of these. The
    // STAT/mood effects on the hediff's own HediffStages are the real
    // mechanism and need nothing here; this comp owns only the "glows"
    // half -- registering a light with the shared proxy-light system that
    // piece 1 (painting, RM_MapComponent_DeepfireLights) will ship.
    //
    // That component does not exist yet (DEEPFIRE_PAINT_STATUS_CUISINE_1
    // defers painting/worn-glow to DEEPFIRE_PAINT_LIVE_VERIFY_1 -- it needs
    // the spec's own live proxy-glower quicktest before anything may depend
    // on its shape). So this binds to it the same soft, no-op-until-present
    // way this codebase already binds to Ninefold/FlowWorks
    // (NinefoldDeltaBridge.cs, this file's sibling): resolve by reflection,
    // cache once, and do nothing at all while the type is absent. When
    // piece 1 ships RM_MapComponent_DeepfireLights with a matching
    // RegisterHediffGlow/DeregisterHediffGlow pair, every hediff here lights
    // up with no further code change.
    public class HediffCompProperties_DeepfireGlow : HediffCompProperties
    {
        // Ignored when useHairColor/useSkinColor is set.
        public Color glowColor = Color.white;

        // One radius per hediff stage (index 0..2 = tier I..III). 0 = no
        // light at that tier (several families are "none visible" until a
        // later tier, spec §6.3).
        public List<float> glowRadiusByStage = new List<float> { 0f, 0f, 0f };

        public bool useHairColor;
        public bool useSkinColor;

        // Blood-glow only: light this hediff exclusively while the pawn has
        // an actual bleeding wound (spec: "any bleeding wound").
        public bool onlyWhileBleeding;

        // Pulse-glow only: read by RM_MapComponent_DeepfireLights once it
        // exists, to reuse RM_Comp_WarblingGlow's value-pulse parameters on
        // the proxy (spec §6.3 row 12). No effect until then.
        public bool pulsesWithHeartRate;

        // Hair-glow (1.5x) and the vermilion (1.5x) override the darkness-
        // targeting multiplier piece 2's (deferred) combat hook will read.
        // 1 = no override. Harmless data field until that hook ships.
        public float glowTargetFactorOverride = 1f;

        // The vermilion only (spec §6.3 row 14): "cannot be hidden -- Ishko
        // -Medium on reaching III". Fires once per hediff instance via
        // NinefoldDeltaBridge when CurStageIndex first reaches 2.
        public bool ishkoPenaltyOnStage3;

        public HediffCompProperties_DeepfireGlow()
        {
            compClass = typeof(HediffComp_DeepfireGlow);
        }
    }

    public class HediffComp_DeepfireGlow : HediffComp
    {
        private bool firedIshkoPenalty;

        public HediffCompProperties_DeepfireGlow Props => (HediffCompProperties_DeepfireGlow)props;

        public override void CompPostTick(ref float severityAdjustment)
        {
            base.CompPostTick(ref severityAdjustment);
            if (Pawn?.IsHashIntervalTick(250) != true) return;
            Apply();
        }

        public override void CompPostPostAdd(DamageInfo? dinfo)
        {
            base.CompPostPostAdd(dinfo);
            Apply();
        }

        public override void CompPostPostRemoved()
        {
            base.CompPostPostRemoved();
            DeepfireLightsBridge.DeregisterHediffGlow(Pawn, Def);
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref firedIshkoPenalty, "firedIshkoPenalty", false);
        }

        private void Apply()
        {
            if (!LuminousPigmentSettings.hediffGlowEnabled)
            {
                DeepfireLightsBridge.DeregisterHediffGlow(Pawn, Def);
            }
            else
            {
                int stage = parent.CurStageIndex;
                float radius = 0f;
                if (Props.glowRadiusByStage != null && stage >= 0 && stage < Props.glowRadiusByStage.Count)
                {
                    radius = Props.glowRadiusByStage[stage];
                }

                if (Props.onlyWhileBleeding && Pawn?.health?.hediffSet?.BleedRateTotal <= 0f)
                {
                    radius = 0f;
                }

                Color color = Props.glowColor;
                if (Props.useHairColor && Pawn?.story != null) color = Pawn.story.HairColor;
                if (Props.useSkinColor && Pawn?.story != null) color = Pawn.story.SkinColor;

                if (radius > 0f)
                {
                    DeepfireLightsBridge.RegisterHediffGlow(Pawn, Def, color, radius);
                }
                else
                {
                    DeepfireLightsBridge.DeregisterHediffGlow(Pawn, Def);
                }

                if (Props.ishkoPenaltyOnStage3 && stage >= 2 && !firedIshkoPenalty)
                {
                    firedIshkoPenalty = true;
                    // "Medium" magnitude (spec §5.2's own vocabulary) -- reuses
                    // the trio's Medium constant rather than adding a settings
                    // field for one specific event.
                    NinefoldDeltaBridge.ApplyDelta("Ishko", -LuminousPigmentSettings.godDeltaAdore, "deepfire.vermilion.cannotBeHidden");
                }
            }
        }
    }

    // Soft reflection binding to the future RM_MapComponent_DeepfireLights
    // (piece 1, painting -- deferred). No warning while the type is simply
    // absent, since that is the expected state of this build; only warns if
    // the type is found but its shape has changed (would only ever fire
    // once piece 1 ships and something later reshapes it).
    internal static class DeepfireLightsBridge
    {
        private const string TypeName = "RimMandrake.LuminousPigment.MapComponent_DeepfireLights";

        private static bool resolved;
        private static bool warned;
        private static MethodInfo registerMethod;
        private static MethodInfo deregisterMethod;

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;

            System.Type t = HarmonyLib.AccessTools.TypeByName(TypeName);
            if (t == null) return; // piece 1 not shipped yet -- normal for this build.

            registerMethod = HarmonyLib.AccessTools.Method(t, "RegisterHediffGlow",
                new[] { typeof(Pawn), typeof(HediffDef), typeof(Color), typeof(float) });
            deregisterMethod = HarmonyLib.AccessTools.Method(t, "DeregisterHediffGlow",
                new[] { typeof(Pawn), typeof(HediffDef) });

            if (registerMethod == null || deregisterMethod == null)
            {
                if (!warned)
                {
                    warned = true;
                    Log.Warning("[RimMandrake.LuminousPigment] found MapComponent_DeepfireLights but " +
                        "RegisterHediffGlow/DeregisterHediffGlow changed shape -- hediff glow lights are OFF.");
                }
                registerMethod = null;
                deregisterMethod = null;
            }
        }

        public static void RegisterHediffGlow(Pawn pawn, HediffDef def, Color color, float radius)
        {
            Resolve();
            if (registerMethod == null || pawn?.Map == null) return;
            registerMethod.Invoke(null, new object[] { pawn, def, color, radius });
        }

        public static void DeregisterHediffGlow(Pawn pawn, HediffDef def)
        {
            Resolve();
            if (deregisterMethod == null || pawn == null) return;
            deregisterMethod.Invoke(null, new object[] { pawn, def });
        }
    }
}
