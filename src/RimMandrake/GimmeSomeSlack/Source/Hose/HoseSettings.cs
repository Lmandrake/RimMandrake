using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Hose
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
        /// <summary>Hose length on a reel, cells. Default 40 since round 6 (owner 2026-10-04: "I think the hose should go 40
        /// cells by itself already though, by default"); HoseMath.DefaultMaxLength is the one number.</summary>
        public static float maxLength = (float)HoseMath.DefaultMaxLength;
        /// <summary>Which shipped default the saved maxLength was written under (0 = before round 6, when it was 30). Same
        /// "maxLength" key as ever; HoseMath.MigrateMaxLength lifts an untouched old default to the new one.</summary>
        public static int maxLengthDefaults = HoseMath.MaxLengthDefaultsVersion;
        public static int couplingSpacing = 8;
        /// <summary>Carry (design 12): one slider scaling the grab (45), set-down (30) and couple (90) ticks together, 0.25-3x.</summary>
        public static float handlingTime = 1f;
        /// <summary>Carry: winding speed when a colonist reels a hose in, cells per second (scaled by his Manipulation).</summary>
        public static float windCellsPerSecond = 3f;
        /// <summary>Carry: an interrupted hose (end dropped, order kept) is picked up again by an idle colonist.</summary>
        public static bool autoResumeDroppedHose = true;
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
            Scribe_Values.Look(ref maxLength, "maxLength", (float)HoseMath.DefaultMaxLength);
            Scribe_Values.Look(ref maxLengthDefaults, "maxLengthDefaults", 0);
            if (Scribe.mode == LoadSaveMode.LoadingVars)
            {
                maxLength = (float)HoseMath.MigrateMaxLength(maxLength, maxLengthDefaults);
                maxLengthDefaults = HoseMath.MaxLengthDefaultsVersion;
            }
            Scribe_Values.Look(ref couplingSpacing, "couplingSpacing", 8);
            Scribe_Values.Look(ref handlingTime, "handlingTime", 1f);
            Scribe_Values.Look(ref windCellsPerSecond, "windCellsPerSecond", 3f);
            Scribe_Values.Look(ref autoResumeDroppedHose, "autoResumeDroppedHose", true);
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
            maxLength = (float)HoseMath.DefaultMaxLength;
            couplingSpacing = 8;
            handlingTime = 1f;
            windCellsPerSecond = 3f;
            autoResumeDroppedHose = true;
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
                                                   plumpAmount.ToString("0.###") + "|" + couplingSpacing +
                                                   "|L" + maxLength.ToString("0.###");   // GPT source read B8: a new hose length re-lays (and re-checks) every hose

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Flexible hoses", RimMandrake.Shared.SettingScope.Now, new[] { "enabled", "plumpAmount", "transitionTicks", "releaseTicks", "minPlumpDwell" }))
            {
            list.CheckboxLabeled("Flexible hoses (master switch)", ref enabled,
                "Thick, stiff sack-cloth hoses laid from a hose reel. They lie flat when empty and plump up while liquid flows. " +
                "Off: hoses are hidden; reels stay and keep their hose ends, so no save breaks.");
            list.Label("Plump amount: " + plumpAmount.ToString("0.0") + "x");
            plumpAmount = Mathf.Round(list.Slider(plumpAmount, 0f, 1.5f) * 10f) / 10f;
            list.Label("Flat/plump transition: " + transitionTicks + " ticks");
            transitionTicks = Mathf.RoundToInt(list.Slider(transitionTicks, 10f, 120f));
            list.Label("Collapse after no flow for: " + releaseTicks + " ticks (keeps a stalling pump from flickering the hose)");
            releaseTicks = Mathf.RoundToInt(list.Slider(releaseTicks, 100f, 1500f) / 50f) * 50;
                list.GapLine();
            }

            if (Group(list, "Hose length and shape", RimMandrake.Shared.SettingScope.Now, new[] { "minBendRadius", "maxLength", "couplingSpacing", "slack", "maxLengthDefaults" }))
            {
            list.Label("Stiffness (smallest bend radius): " + minBendRadius.ToString("0.0") + " cells");
            minBendRadius = Mathf.Round(list.Slider(minBendRadius, 0.6f, 2.5f) * 10f) / 10f;
            list.Label("Hose length on a reel: " + maxLength.ToString("0") + " cells");
            maxLength = Mathf.Round(list.Slider(maxLength, 8f, 60f));
            list.Label("Hose joiners: only at bends, at least " + couplingSpacing + " cells apart", -1f,
                (TipSignal?)"Where one hose length is screwed to the next. A straight hose has no joiner; a joiner sits at the sharpest point of a bend.");
            couplingSpacing = Mathf.RoundToInt(list.Slider(couplingSpacing, 4f, 16f));
            list.Label("Hose slack: " + slack.ToString("0.0") + "x");
            slack = Mathf.Round(list.Slider(slack, 0f, 2f) * 10f) / 10f;
                list.GapLine();
            }

            if (Group(list, "Colonists carrying hoses", RimMandrake.Shared.SettingScope.Now, new[] { "handlingTime", "windCellsPerSecond", "autoResumeDroppedHose" }))
            {
            list.Label("Colonists carrying hoses", -1f, (TipSignal?)("Hoses are laid by a colonist who carries the end out and winds it back in. " +
                "The instant Lay / Reel in buttons exist only in dev mode and have no setting."));
            list.Label("Handling time (grab, set down, couple): " + handlingTime.ToString("0.00") + "x", -1f,
                (TipSignal?)"Scales how long a colonist takes to pick the hose end up, put it down and screw it on. 1x = 45 / 30 / 90 ticks.");
            handlingTime = Mathf.Round(list.Slider(handlingTime, 0.25f, 3f) * 20f) / 20f;
            list.Label("Winding speed: " + windCellsPerSecond.ToString("0.0") + " cells per second", -1f,
                (TipSignal?)"How fast a colonist winds a hose back onto the reel (a clumsy colonist is slower).");
            windCellsPerSecond = Mathf.Round(list.Slider(windCellsPerSecond, 1f, 8f) * 2f) / 2f;
            list.CheckboxLabeled("Interrupted hoses are picked up again automatically", ref autoResumeDroppedHose,
                "When a colonist is drafted, downed or distracted mid-carry the hose end lies where he left it and the order stays. " +
                "On: an idle colonist takes it up again. Off: the end waits until you order it.");
                list.GapLine();
            }

            if (Group(list, "Look and FlowWorks", RimMandrake.Shared.SettingScope.Now, new[] { "tintByContents", "fillWobble", "useFlowWorksPumps", "defaultFluid" }))
            {
            list.CheckboxLabeled("Charged hoses darken with what they carry", ref tintByContents);
            list.CheckboxLabeled("Brief wobble when a hose fills or drains", ref fillWobble);
            list.CheckboxLabeled("Read FlowWorks pumps beside a reel (when FlowWorks has them)", ref useFlowWorksPumps);
                list.GapLine();
            }

            viewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1200f;

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int/string/enum setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(HoseSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int) || f.FieldType == typeof(string) || f.FieldType.IsEnum)
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(HoseSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): every Hose setting is read live by the hose draw pass, a colonist job, or a re-lay on window close (the shape fingerprint changes), none at world or map generation, so all are [now]. minPlumpDwell, defaultFluid and maxLengthDefaults have no control on this screen (probe and migration values) and only reset.</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }
    }

    public class FireHosesMod : Mod
    {
        public static HoseSettings Settings;

        // Harmony: GimmeSomeSlackMod's PatchAll(assembly) already applies every [HarmonyPatch] in this assembly.
        public FireHosesMod(ModContentPack content) : base(content)
        {
            LegacyMigration.SettingsFiles(content);
            Settings = GetSettings<HoseSettings>();
        }

        /// <summary>B27: empty, so RimWorld lists no separate entry; drawn as a tab of GimmeSomeSlackMod's one window.</summary>
        public override string SettingsCategory() => "";

        public override void DoSettingsWindowContents(Rect inRect) => Settings.DoWindowContents(inRect);
    }
}
