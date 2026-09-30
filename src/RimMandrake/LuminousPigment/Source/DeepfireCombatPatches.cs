using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_WORN_GLOW_1, spec §3.4 "Easier to hit in the dark" -- ranged.
    // ShotReport is a struct whose factors are private fields (RimSage
    // Verse/ShotReport.cs); HitReportFor is static and returns it by value,
    // so the postfix edits __result by ref through a struct field ref.
    // factorFromTargetSize feeds AimOnTargetChance_IgnoringPosture and so
    // TotalEstimatedHitChance -- the number the shot actually rolls on
    // (Yayo's Combat 3 still calls HitReportFor, per the spec's §8).
    [HarmonyPatch(typeof(ShotReport), nameof(ShotReport.HitReportFor))]
    public static class Patch_ShotReport_HitReportFor
    {
        internal static readonly AccessTools.StructFieldRef<ShotReport, float> FactorFromTargetSize =
            AccessTools.StructFieldRefAccess<ShotReport, float>("factorFromTargetSize");

        public static void Postfix(LocalTargetInfo target, ref ShotReport __result)
        {
            if (!LuminousPigmentSettings.combatPenaltiesEnabled) return;
            if (!(target.Thing is Pawn pawn)) return;
            if (!DeepfireDarkness.IsGlowingInDark(pawn)) return;
            ref float f = ref FactorFromTargetSize(ref __result);
            f = Mathf.Clamp(f * LuminousPigmentSettings.glowTargetFactor,
                DeepfirePaintDefaults.TargetSizeFactorMin, DeepfirePaintDefaults.TargetSizeFactorMax);
        }
    }

    // The labelled readout line. Vanilla already prints the changed
    // "Target size" line; this adds the named reason under it.
    [HarmonyPatch(typeof(ShotReport), nameof(ShotReport.GetTextReadout))]
    public static class Patch_ShotReport_GetTextReadout
    {
        private static readonly AccessTools.StructFieldRef<ShotReport, TargetInfo> TargetField =
            AccessTools.StructFieldRefAccess<ShotReport, TargetInfo>("target");

        public const string LineLabel = "glowing in the dark";

        public static void Postfix(ref ShotReport __instance, ref string __result)
        {
            if (!LuminousPigmentSettings.combatPenaltiesEnabled) return;
            TargetInfo t = TargetField(ref __instance);
            if (!(t.Thing is Pawn pawn)) return;
            if (!DeepfireDarkness.IsGlowingInDark(pawn)) return;
            __result += "   " + LineLabel.CapitalizeFirst() + ": x"
                + LuminousPigmentSettings.glowTargetFactor.ToString("0.##") + " target size\n";
        }
    }

    // Melee half: XML-patched onto MeleeDodgeChance's <parts>
    // (Patches/DeepfireGlowingTargetStatPart.xml). StatWorker.FinalizeValue
    // runs parts BEFORE the stat's postProcessCurve (RimSage
    // RimWorld/StatWorker.cs), and MeleeDodgeChance's unfinalized value is
    // on a 5..60 scale mapped to 0..0.5 by that curve -- so a raw -0.08 here
    // would do nothing. The offset is instead applied to the FINAL value:
    // evaluate the curve, subtract, and invert the (monotonic, piecewise
    // linear) curve back into the unfinalized domain.
    public class RM_StatPart_GlowingTarget : StatPart
    {
        // XML-declared default (Patches/DeepfireGlowingTargetStatPart.xml),
        // kept for schema validity -- DEEPFIRE_MOD_SETTINGS_1 reads the live
        // LuminousPigmentSettings.glowDodgePenalty below instead.
        public float penalty = DeepfirePaintDefaults.GlowDodgePenalty;

        public override void TransformValue(StatRequest req, ref float val)
        {
            if (!Applies(req)) return;
            float livePenalty = LuminousPigmentSettings.glowDodgePenalty;
            SimpleCurve curve = parentStat?.postProcessCurve;
            if (curve == null || curve.PointsCount < 2)
            {
                val -= livePenalty;
                return;
            }
            float final = curve.Evaluate(val);
            float target = Mathf.Max(parentStat.minValue, final - livePenalty);
            val = InverseEvaluate(curve, target, val);
        }

        public override string ExplanationPart(StatRequest req)
        {
            if (!Applies(req)) return null;
            return Patch_ShotReport_GetTextReadout.LineLabel.CapitalizeFirst() + ": -"
                + LuminousPigmentSettings.glowDodgePenalty.ToStringPercent() + " (after the curve)";
        }

        private static bool Applies(StatRequest req) =>
            LuminousPigmentSettings.combatPenaltiesEnabled
            && req.Thing is Pawn pawn && DeepfireDarkness.IsGlowingInDark(pawn);

        // Smallest x whose curve value reaches `y`, never above the current
        // value (the offset only ever lowers dodge).
        internal static float InverseEvaluate(SimpleCurve curve, float y, float current)
        {
            var pts = curve.Points;
            if (y <= pts[0].y) return Mathf.Min(current, pts[0].x);
            for (int i = 1; i < pts.Count; i++)
            {
                CurvePoint a = pts[i - 1], b = pts[i];
                if (y <= b.y)
                {
                    if (Mathf.Approximately(b.y, a.y)) return Mathf.Min(current, a.x);
                    float x = a.x + (y - a.y) / (b.y - a.y) * (b.x - a.x);
                    return Mathf.Min(current, x);
                }
            }
            return current;
        }
    }
}
