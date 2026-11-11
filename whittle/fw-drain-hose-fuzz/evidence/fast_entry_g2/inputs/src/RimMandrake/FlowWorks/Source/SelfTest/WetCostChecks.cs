// WET_FOXHOLE_BUILD_COLD_FEET_SHAKY_AIM (canal cover design §5, §10 step 4; owner Q4/Q6/Q8 2026-10-18). Arithmetic is the
// PRODUCTION Verse-free RM_WetCostMath; the Verse wiring (Swimming/RM_WetCosts.cs, the settings in Swimming/RM_Swim.cs and
// the StatDef patch) is read from production source.
using System;
using System.IO;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class WetCostChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private const float Person = 1.75f;   // RM_RelativeRulesMath.HeightByBand[2]
        private const float Rat = 0.5f;       // HeightByBand[1]

        public static void Run(Action<string, Action> Case)
        {
            Case("WetCost_person_height_matches_the_relative_rules_table", () =>
            {
                Assert(RM_RelativeRulesMath.HeightMetres(2) == RM_WetCostMath.PersonHeightMetres, "person height drifted from HeightByBand[2]");
            });

            Case("WetCost_aim_0_85_at_chest_depth_1_0_below", () =>
            {
                float f = RM_WetCostMath.DefaultAimFactor;
                Assert(RM_WetCostMath.AimFactor(true, 1.5f, Person, false, f) == 0.85f, "person in 1.5 m: x0.85");
                Assert(RM_WetCostMath.AimFactor(true, 1.4995f, Person, false, f) == 0.85f, "decilitre rounding under 1.5 m still chest-deep");
                Assert(RM_WetCostMath.AimFactor(true, 1.0f, Person, false, f) == 1f, "person in 1 m (waist): no penalty");
                Assert(RM_WetCostMath.AimFactor(true, 0.5f, Person, false, f) == 1f, "person in 0.5 m: no penalty");
                Assert(RM_WetCostMath.AimFactor(true, 0f, Person, false, f) == 1f, "dry: no penalty");
                Assert(RM_WetCostMath.AimFactor(false, 1.5f, Person, false, f) == 1f, "setting off: no penalty");
                Assert(RM_WetCostMath.AimFactor(true, 1.5f, Person, true, f) == 1f, "lying: the rule is a standing shooter's");
            });

            Case("WetCost_chest_depth_is_relative_to_height", () =>
            {
                Assert(RM_WetCostMath.ChestDeep(0.45f, Rat), "rat chest-deep at 0.45 m");
                Assert(!RM_WetCostMath.ChestDeep(0.3f, Rat), "rat not chest-deep at 0.3 m");
                Assert(!RM_WetCostMath.ChestDeep(1.5f, 3.5f), "a thrumbo-height creature is not chest-deep in 1.5 m");
                Assert(!RM_WetCostMath.ChestDeep(1.5f, 0f), "no height: never");
            });

            Case("WetCost_aim_factor_clamped_never_helps", () =>
            {
                Assert(RM_WetCostMath.AimFactor(true, 2f, Person, false, 1.4f) == 1f, "a factor over 1 is clamped to 1");
                Assert(RM_WetCostMath.AimFactor(true, 2f, Person, false, -0.2f) == 0f, "a negative factor is clamped to 0");
            });

            Case("WetCost_cold_offset_only_while_in_water", () =>
            {
                Assert(RM_WetCostMath.ColdOffset(true, true, RM_WetCostMath.DefaultColdOffset) == 6f, "in water: +6");
                Assert(RM_WetCostMath.ColdOffset(true, false, 6f) == 0f, "dry: 0");
                Assert(RM_WetCostMath.ColdOffset(false, true, 6f) == 0f, "setting off: 0");
                Assert(RM_WetCostMath.ColdOffset(true, true, -3f) == 0f, "never makes the cold easier");
            });

            Case("WetCost_swimmers_have_no_ranged_verb_melee_kept", () =>
            {
                Assert(!RM_WetCostMath.RangedAllowed(true, true, false), "swimmer, ranged: refused");
                Assert(RM_WetCostMath.RangedAllowed(true, true, true), "swimmer, melee: kept");
                Assert(RM_WetCostMath.RangedAllowed(true, false, false), "wader, ranged: kept");
                Assert(RM_WetCostMath.RangedAllowed(false, true, false), "setting off: kept");
            });

            Case("WetCost_wiring_patches_settings_and_statdef", () =>
            {
                string w = RiverSwitchFlipChecks.Src(Path.Combine("Swimming", "RM_WetCosts.cs"));
                Assert(Regex.IsMatch(w, @"\[HarmonyPatch\(typeof\(ShotReport\), nameof\(ShotReport\.HitReportFor\)\)\]\s*\[RimMandrake\.Shared\.PatchFeature\(.{0,160}?""deepWaterAimPenalty""\)\]"),
                    "aim postfix on HitReportFor, switched by deepWaterAimPenalty");
                Assert(w.Contains("StructFieldRefAccess<ShotReport, float>(\"factorFromShooterAndDist\")"), "aim folds into the shooter's half");
                Assert(Regex.IsMatch(w, @"\[HarmonyPatch\(typeof\(Verb\), nameof\(Verb\.CanHitTargetFrom\)\)\]\s*\[RimMandrake\.Shared\.PatchFeature\(.{0,160}?""swimmersCannotShoot""\)\]"),
                    "no-guns postfix on CanHitTargetFrom, switched by swimmersCannotShoot");
                Assert(w.Contains("RM_WetCosts.SwimmingAt(p, root)"), "no-guns judges the candidate square (root), not the current one");
                Assert(w.Contains("__instance.IsMeleeAttack"), "melee verbs are never refused");
                Assert(w.Contains("public class StatPart_RM_WetCold : StatPart"), "the cold StatPart exists");

                string sw = RiverSwitchFlipChecks.Src(Path.Combine("Swimming", "RM_Swim.cs"));
                foreach (string f in new[] { "deepWaterAimPenalty", "deepWaterAimFactor", "wetFeelsColder", "wetColdOffset", "swimmersCannotShoot" })
                {
                    Assert(Regex.IsMatch(sw, @"public static (bool|float) " + f + @" = "), f + ": a public setting");
                    Assert(sw.Contains("Scribe_Values.Look(ref " + f + ", \"" + f + "\""), f + ": scribed under its own name");
                    Assert(sw.IndexOf("public static " , sw.IndexOf(" " + f + " = ")) < sw.IndexOf("shippedDefaults = RM_SettingsReset.Snapshot"),
                        f + ": declared above the Reset snapshot");
                }

                string xml = File.ReadAllText(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_WetCostMath.cs")), "..", "Patches", "Swimming", "FlowWorks_WetCold.xml"));
                Assert(xml.Contains("Defs/StatDef[defName=\"ComfyTemperatureMin\"]/parts"), "the patch targets ComfyTemperatureMin's parts");
                Assert(xml.Contains("Class=\"RimMandrake.FlowWorks.Swimming.StatPart_RM_WetCold\""), "the patch names the StatPart by its full type name");
            });
        }
    }
}
