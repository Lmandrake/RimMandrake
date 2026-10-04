using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit.Hose
{
    /// <summary>
    /// Flexible-hose settings (design 3.10). Their own ModSettings (a third Mod class in this assembly, its own entry
    /// in the Mod Settings list), like the aerial lines, so the floor-cord settings file is untouched. Static fields
    /// so HoseProbe "set:" and jawa/mod_settings_field can read and write them. Defaults = shipped behaviour.
    /// </summary>
    public class HoseSettings : ModSettings
    {
        /// <summary>Master switch. Off: hoses are not drawn and the reel's hose gizmos are hidden; reels and their
        /// saved hose ends stay, so a save never breaks.</summary>
        public static bool enabled = true;
        /// <summary>Stiffness: the smallest bend radius a hose takes, cells.</summary>
        public static float minBendRadius = 1.2f;
        /// <summary>How much a charged hose swells, straightens and wobbles (0 = no visible change).</summary>
        public static float plumpAmount = 1f;
        /// <summary>Flat-to-plump blend time, ticks.</summary>
        public static int transitionTicks = 30;
        /// <summary>Hysteresis: ticks without flow before a plump hose drains (two FlowWorks pulses).</summary>
        public static int releaseTicks = 500;
        /// <summary>Hysteresis: least ticks a hose stays plump.</summary>
        public static int minPlumpDwell = 600;
        /// <summary>Hose length on a reel, cells.</summary>
        public static float maxLength = 30f;
        public static int couplingSpacing = 8;
        /// <summary>Scales the S-curve slack.</summary>
        public static float slack = 1f;
        /// <summary>Wet darkening of a charged hose tinted by what it carries.</summary>
        public static bool tintByContents = true;
        public static bool fillWobble = true;
        /// <summary>Read a FlowWorks pump's last-pulse record next to the reel when one exists (none is built yet).</summary>
        public static bool useFlowWorksPumps = true;
        /// <summary>Per-fluid tint stub: what a hose carries when no pump says (FlowWorks has no pump yet).</summary>
        public static string defaultFluid = "RM_Fluid_Water";

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref minBendRadius, "minBendRadius", 1.2f);
            Scribe_Values.Look(ref plumpAmount, "plumpAmount", 1f);
            Scribe_Values.Look(ref transitionTicks, "transitionTicks", 30);
            Scribe_Values.Look(ref releaseTicks, "releaseTicks", 500);
            Scribe_Values.Look(ref minPlumpDwell, "minPlumpDwell", 600);
            Scribe_Values.Look(ref maxLength, "maxLength", 30f);
            Scribe_Values.Look(ref couplingSpacing, "couplingSpacing", 8);
            Scribe_Values.Look(ref slack, "slack", 1f);
            Scribe_Values.Look(ref tintByContents, "tintByContents", true);
            Scribe_Values.Look(ref fillWobble, "fillWobble", true);
            Scribe_Values.Look(ref useFlowWorksPumps, "useFlowWorksPumps", true);
            Scribe_Values.Look(ref defaultFluid, "defaultFluid", "RM_Fluid_Water");
        }

        public static void ResetToDefaults()
        {
            enabled = true;
            minBendRadius = 1.2f;
            plumpAmount = 1f;
            transitionTicks = 30;
            releaseTicks = 500;
            minPlumpDwell = 600;
            maxLength = 30f;
            couplingSpacing = 8;
            slack = 1f;
            tintByContents = true;
            fillWobble = true;
            useFlowWorksPumps = true;
            defaultFluid = "RM_Fluid_Water";
        }

        public static HoseTuning Tuning() => new HoseTuning
        {
            TransitionTicks = Mathf.Clamp(transitionTicks, 1, 600),
            ReleaseTicks = Mathf.Max(0, releaseTicks),
            MinPlumpDwell = Mathf.Max(0, minPlumpDwell)
        };

        public static HoseShapeParams Shape() => new HoseShapeParams
        {
            MinBendRadius = Mathf.Clamp(minBendRadius, 0.3f, 4f),
            Slack = Mathf.Clamp(slack, 0f, 2f),
            PlumpAmount = Mathf.Clamp(plumpAmount, 0f, 2f),
            CouplingSpacing = Mathf.Clamp(couplingSpacing, 4, 16)
        };

        /// <summary>Everything the laid geometry depends on: a change re-lays every hose.</summary>
        public static string ShapeFingerprint() => minBendRadius.ToString("0.###") + "|" + slack.ToString("0.###") + "|" +
                                                   plumpAmount.ToString("0.###") + "|" + couplingSpacing;
    }

    public class FireHosesMod : Mod
    {
        public static HoseSettings Settings;

        // Harmony: MessyConduitMod's PatchAll(assembly) already applies every [HarmonyPatch] in this assembly.
        public FireHosesMod(ModContentPack content) : base(content) => Settings = GetSettings<HoseSettings>();

        public override string SettingsCategory() => "RimMandrake: Messy Conduit - flexible hoses";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            var l = new Listing_Standard();
            l.Begin(inRect);
            l.CheckboxLabeled("Flexible hoses (master switch)", ref HoseSettings.enabled,
                "Thick, stiff sack-cloth hoses laid from a hose reel. They lie flat when empty and plump up while liquid flows. " +
                "Off: hoses are hidden; reels stay and keep their hose ends, so no save breaks.");
            l.Label("Stiffness (smallest bend radius): " + HoseSettings.minBendRadius.ToString("0.0") + " cells");
            HoseSettings.minBendRadius = Mathf.Round(l.Slider(HoseSettings.minBendRadius, 0.6f, 2.5f) * 10f) / 10f;
            l.Label("Plump amount: " + HoseSettings.plumpAmount.ToString("0.0") + "x");
            HoseSettings.plumpAmount = Mathf.Round(l.Slider(HoseSettings.plumpAmount, 0f, 1.5f) * 10f) / 10f;
            l.Label("Flat/plump transition: " + HoseSettings.transitionTicks + " ticks");
            HoseSettings.transitionTicks = Mathf.RoundToInt(l.Slider(HoseSettings.transitionTicks, 10f, 120f));
            l.Label("Collapse after no flow for: " + HoseSettings.releaseTicks + " ticks (keeps a stalling pump from flickering the hose)");
            HoseSettings.releaseTicks = Mathf.RoundToInt(l.Slider(HoseSettings.releaseTicks, 100f, 1500f) / 50f) * 50;
            l.Label("Hose length on a reel: " + HoseSettings.maxLength.ToString("0") + " cells");
            HoseSettings.maxLength = Mathf.Round(l.Slider(HoseSettings.maxLength, 8f, 60f));
            l.Label("Hose joiners: only at bends, at least " + HoseSettings.couplingSpacing + " cells apart", -1f,
                (TipSignal?)"Where one hose length is screwed to the next. A straight hose has no joiner; a joiner sits at the sharpest point of a bend.");
            HoseSettings.couplingSpacing = Mathf.RoundToInt(l.Slider(HoseSettings.couplingSpacing, 4f, 16f));
            l.Label("Hose slack: " + HoseSettings.slack.ToString("0.0") + "x");
            HoseSettings.slack = Mathf.Round(l.Slider(HoseSettings.slack, 0f, 2f) * 10f) / 10f;
            l.CheckboxLabeled("Charged hoses darken with what they carry", ref HoseSettings.tintByContents);
            l.CheckboxLabeled("Brief wobble when a hose fills or drains", ref HoseSettings.fillWobble);
            l.CheckboxLabeled("Read FlowWorks pumps beside a reel (when FlowWorks has them)", ref HoseSettings.useFlowWorksPumps);
            l.GapLine();
            if (l.ButtonText("Reset to defaults")) HoseSettings.ResetToDefaults();
            l.End();
        }
    }
}
