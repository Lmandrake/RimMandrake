using UnityEngine;
using Verse;

namespace RimMandrake.Visibility
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Visibility.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData).
    //
    // Two things exposed:
    //   1. Master on/off for the raid threat-point scaling
    //      (ColonyVisibilityRaidPatch.Prefix_ScaleHostilePoints) — the dial
    //      itself (GameComponent_ColonyVisibility) keeps tracking harmlessly
    //      either way; only the gameplay EFFECT on raid points is gated.
    //   2. A strength slider that lerps between "no effect" (1.0x) and the
    //      design doc's ruled curve output, so a player can soften/amplify
    //      the whole mechanic without hand-editing
    //      GameComponent_ColonyVisibility.VisibilityToThreatCurve (which
    //      stays the ruled base curve, untouched).
    //   3. The Ta'Baa launch-reset multiplier (how far a gravship launch
    //      resets the dial toward 0) as a tunable, default matching the
    //      shipped 0.15x.
    // ════════════════════════════════════════════════════════════════════
    public class RM_VisibilitySettings : ModSettings
    {
        public static bool enableRaidScaling = true;
        public static float raidScalingStrength = 1f;
        public static float launchResetMultiplier = 0.15f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enableRaidScaling, "enableRaidScaling", true);
            Scribe_Values.Look(ref raidScalingStrength, "raidScalingStrength", 1f);
            Scribe_Values.Look(ref launchResetMultiplier, "launchResetMultiplier", 0.15f);
        }

        /// <summary>
        /// Applies the strength dial to the curve's raw output: at 0 strength,
        /// visibility never changes raid points (factor 1.0); at 1 (default),
        /// the full ruled curve applies; up to 2, the curve's deviation from
        /// 1.0 is doubled.
        /// </summary>
        public static float ScaledThreatFactor(float visibility)
        {
            float curveFactor = GameComponent_ColonyVisibility.ThreatFactor(visibility);
            return 1f + (curveFactor - 1f) * raidScalingStrength;
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Colony Visibility raid scaling");
            list.CheckboxLabeled("Raids scale with Colony Visibility", ref enableRaidScaling,
                "How exposed the colony's ship is on the desert changes how hard hostile raids, "
              + "infestations, manhunter packs and mech clusters hit. Off: the Visibility dial "
              + "keeps tracking in the background, but raids are never scaled by it.");

            if (enableRaidScaling)
            {
                list.Label("Scaling strength: " + raidScalingStrength.ToString("0.00") + "x");
                list.Label("0x = no effect at all. 1x = the ruled curve (unchanged). 2x = double the swing.");
                raidScalingStrength = list.Slider(raidScalingStrength, 0f, 2f);
            }

            list.GapLine();
            list.Label("Launch reset (worldgen-affecting: only changes the dial at the moment a gravship launches)");
            list.Label("Launching a gravship resets Visibility toward "
                + (launchResetMultiplier * 100f).ToString("0") + "% of its old value (floor 5, ceiling 15).");
            launchResetMultiplier = list.Slider(launchResetMultiplier, 0.05f, 0.5f);

            list.End();
        }
    }

    public class RM_VisibilityMod : Mod
    {
        public static RM_VisibilitySettings settings;

        public RM_VisibilityMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_VisibilitySettings>();
        }

        public override string SettingsCategory()
        {
            return "Colony Visibility";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
