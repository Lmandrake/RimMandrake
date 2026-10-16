using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// Flexible-hose settings (moved from Gimme Some Slack at the hose port, step 2; design v2 §8): a static section of
    /// RimMandrakeFlowWorksSettings, exposed from its ExposeData with a `hose_` key prefix and drawn in FlowWorks' window under
    /// "Hoses and pipes". Static fields so HoseProbe "set:" and jawa/mod_settings_field can read and write them. Defaults =
    /// shipped behaviour. The old GSS file (Mod_*_FireHosesMod.xml) is imported once (RM_HoseLegacy.ImportOnce).
    /// </summary>
    public static class RM_HoseSettings
    {
        /// <summary>Master switch. Off: hoses are not drawn and the reel's hose gizmos are hidden; reels and their
        /// saved hose ends stay, so a save never breaks.</summary>
        public static bool enabled = true;
        /// <summary>Tank jobs (liquid networks L4, rev 2 §3.2; owner ruling #9 "a tank would pass liquid on to a hose screwed
        /// into it, without a pump needed"): each tank is Store / Fill / Empty / Dump, and Empty and Fill move liquid tank to tank
        /// with no pump. Off: every tank acts as Store (never the old equalising feed). Replaces hose_tanksFeedHoses (read once).</summary>
        public static bool tankModesEnabled = true;
        /// <summary>Liquid networks L5 (rev 2 §3.4): hose free ends take a role (Capped / Intake / Outflow). Off: every free end is
        /// Capped and the role button is hidden; saved roles stay.</summary>
        public static bool freeEndRolesEnabled = true;
        /// <summary>PROVISIONAL (rev 2 §3.2): LITRES an Empty tank sends, or a Fill tank takes in, per 250-tick settle (2,000 L =
        /// the old 10 units; LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS).</summary>
        public static int tankLitresPerCycle = 2000;
        /// <summary>PROVISIONAL (rev 2 §3.2, §3.5): LITRES a Dump tank drains out of Outflow ends per 250-tick settle with no pump
        /// (the slow drain; a pump on Pour is the fast one). 1,000 L = one level.</summary>
        public static int dumpLitresPerCycle = 1000;
        /// <summary>Liquid networks L8 (rev 2 §3.7, owner Q2: real): a hose holds a little of what it carries and empties it out of
        /// its open end when it stops (a cleanable spill on ground). Off: hoses hold nothing (anything held drains at once).</summary>
        public static bool hoseHoldsLiquid = true;
        /// <summary>PROVISIONAL (rev 2 §3.7): LITRES a hose holds per cell of its length. 5 L: a ~65 mm hose 1.46 m long holds
        /// 4.8 L (LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS; the old 0.2 units was 40 L a cell). A 40-cell hose holds 200 L.</summary>
        public static float hoseLitresPerCell = 5f;

        /// <summary>Tank units (decilitres) per settle, per Dump drain, per hose cell: the litre settings at their read sites.</summary>
        public static int TankUnitsPerCycle => RM_Volume.Units(tankLitresPerCycle);
        public static int DumpUnitsPerCycle => RM_Volume.Units(dumpLitresPerCycle);
        public static float HoseUnitsPerCell => hoseLitresPerCell * RM_Volume.UnitsPerLitre;

        /// <summary>Model-2 settings stored these three in 200 L units under the old keys: read once into litres when the new key
        /// was never written. An untouched old default becomes the new default (the hose's 40 L a cell was never a ruling).</summary>
        internal static void MigrateLegacyLitres()
        {
            System.Xml.XmlNode parent = Scribe.loader.curXmlParent;
            if (parent == null) return;
            if (parent["hose_tankLitresPerCycle"] == null && parent["hose_tankUnitsPerCycle"] is System.Xml.XmlNode t && int.TryParse(t.InnerText, out int tu))
                tankLitresPerCycle = tu * RM_Volume.LegacyUnitLitres;
            if (parent["hose_dumpLitresPerCycle"] == null && parent["hose_dumpUnitsPerCycle"] is System.Xml.XmlNode d && int.TryParse(d.InnerText, out int du))
                dumpLitresPerCycle = du * RM_Volume.LegacyUnitLitres;
            if (parent["hose_hoseLitresPerCell"] == null && parent["hose_hoseUnitsPerCell"] is System.Xml.XmlNode h
                && float.TryParse(h.InnerText, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float hu)
                && System.Math.Abs(hu - 0.2f) > 1e-4f)
                hoseLitresPerCell = hu * RM_Volume.LegacyUnitLitres;
        }
        /// <summary>Stiffness: the smallest bend radius a hose takes, cells.</summary>
        public static float minBendRadius = 1.2f;
        /// <summary>How much a charged hose swells, straightens and wobbles (0 = no visible change).</summary>
        public static float plumpAmount = 1f;
        /// <summary>HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY: hose thickness, x the shipped width (HoseMath.WidthScale). 1 until the owner
        /// rules on design/RimMandrake/liquid_connections_visuals_2026-10-16.md (proposal 0.65).</summary>
        public static float thickness = 1f;
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
        /// <summary>The look a reel built without a picked style draws in (Scrapper / Industrial / Modern / Futuristic).
        /// Seeded once from Gimme Some Slack's global cord style by the settings import, so nothing already built changes.</summary>
        public static string defaultLook = "Scrapper";
        /// <summary>Internal migration flag (no control): the GSS hose settings file has been imported once.</summary>
        public static bool hoseSettingsImported = false;

        /// <summary>Called from RimMandrakeFlowWorksSettings.ExposeData. Keys carry a `hose_` prefix.</summary>
        public static void ExposeData()
        {
            Scribe_Values.Look(ref enabled, "hose_enabled", true);
            Scribe_Values.Look(ref tankModesEnabled, "hose_tankModesEnabled", true);
            Scribe_Values.Look(ref tankLitresPerCycle, "hose_tankLitresPerCycle", 2000);
            Scribe_Values.Look(ref freeEndRolesEnabled, "hose_freeEndRolesEnabled", true);
            Scribe_Values.Look(ref dumpLitresPerCycle, "hose_dumpLitresPerCycle", 1000);
            Scribe_Values.Look(ref hoseHoldsLiquid, "hose_hoseHoldsLiquid", true);
            Scribe_Values.Look(ref hoseLitresPerCell, "hose_hoseLitresPerCell", 5f);
            if (Scribe.mode == LoadSaveMode.LoadingVars) MigrateLegacyLitres();
            // §3.11: the old tank-feed switch is read once into tank jobs (only when the new key was never written)
            if (Scribe.mode == LoadSaveMode.LoadingVars && Scribe.loader.curXmlParent?["hose_tankModesEnabled"] == null
                && Scribe.loader.curXmlParent?["hose_tanksFeedHoses"] is System.Xml.XmlNode legacyFeed && bool.TryParse(legacyFeed.InnerText, out bool fed))
            {
                tankModesEnabled = fed;
            }
            Scribe_Values.Look(ref minBendRadius, "hose_minBendRadius", 1.2f);
            Scribe_Values.Look(ref plumpAmount, "hose_plumpAmount", 1f);
            Scribe_Values.Look(ref thickness, "hose_thickness", 1f);
            ApplyThickness();
            Scribe_Values.Look(ref transitionTicks, "hose_transitionTicks", 30);
            Scribe_Values.Look(ref releaseTicks, "hose_releaseTicks", 500);
            Scribe_Values.Look(ref minPlumpDwell, "hose_minPlumpDwell", 600);
            Scribe_Values.Look(ref maxLength, "hose_maxLength", (float)HoseMath.DefaultMaxLength);
            Scribe_Values.Look(ref maxLengthDefaults, "hose_maxLengthDefaults", HoseMath.MaxLengthDefaultsVersion);
            if (Scribe.mode == LoadSaveMode.LoadingVars)
            {
                maxLength = (float)HoseMath.MigrateMaxLength(maxLength, maxLengthDefaults);
                maxLengthDefaults = HoseMath.MaxLengthDefaultsVersion;
            }
            Scribe_Values.Look(ref couplingSpacing, "hose_couplingSpacing", 8);
            Scribe_Values.Look(ref handlingTime, "hose_handlingTime", 1f);
            Scribe_Values.Look(ref windCellsPerSecond, "hose_windCellsPerSecond", 3f);
            Scribe_Values.Look(ref autoResumeDroppedHose, "hose_autoResumeDroppedHose", true);
            Scribe_Values.Look(ref slack, "hose_slack", 1f);
            Scribe_Values.Look(ref tintByContents, "hose_tintByContents", true);
            Scribe_Values.Look(ref fillWobble, "hose_fillWobble", true);
            Scribe_Values.Look(ref defaultLook, "hose_defaultLook", "Scrapper");
            Scribe_Values.Look(ref hoseSettingsImported, "hoseSettingsImported", false);
        }

        /// <summary>HoseProbe "defaults": the same reset as the Reset-all button (one list, so a new setting cannot be missed
        /// here; a hand-kept copy of every default used to sit here).</summary>
        public static void ResetToDefaults() => ResetAllFields();

        /// <summary>Push the thickness setting into HoseMath (clamped 0.5-1).</summary>
        public static void ApplyThickness() => HoseMath.WidthScale = Mathf.Clamp(thickness, 0.5f, 1f);

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
                                                   plumpAmount.ToString("0.###") + "|" + couplingSpacing + "|T" + thickness.ToString("0.###") +
                                                   "|L" + maxLength.ToString("0.###");   // GPT source read B8: a new hose length re-lays (and re-checks) every hose

        /// <summary>The "Hoses and pipes" part of FlowWorks' settings window: four collapsible groups (design v2 §8).</summary>
        public static void DoSettingsSection(Listing_Standard list)
        {
            list.GapLine();
            Text.Font = GameFont.Medium;
            list.Label("Hoses and pipes");
            Text.Font = GameFont.Small;
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);
            RimMandrake.Shared.SettingsKitMastersDrawer.ResetAllButton(list, "Flow Works hose", ResetAllFields);

            if (Group(list, "Flexible hoses", RimMandrake.Shared.SettingScope.Now, new[] { "enabled", "tankModesEnabled", "tankLitresPerCycle", "freeEndRolesEnabled", "dumpLitresPerCycle", "hoseHoldsLiquid", "hoseLitresPerCell", "plumpAmount", "thickness", "transitionTicks", "releaseTicks", "minPlumpDwell" }))
            {
            list.CheckboxLabeled("Flexible hoses (master switch)", ref enabled,
                "Thick, stiff sack-cloth hoses laid from a hose reel. They lie flat when empty and plump up while liquid flows. " +
                "Off: hoses are hidden and carry nothing; reels stay and keep their hose ends, so switching back on restores everything.");
            list.CheckboxLabeled("Tank jobs: Store / Fill / Empty / Dump (no pump needed tank to tank)", ref tankModesEnabled,
                "On: each tank has a job button. Empty sends its liquid to the other tanks on its pipes and hoses, Fill pulls their " +
                "liquid in, Dump lets it leave through outflow hose ends. Off: every tank just stores; only pumps and machines move liquid.");
            list.CheckboxLabeled("Hose free ends: Capped / Intake / Outflow", ref freeEndRolesEnabled,
                "On: a hose's loose end has a role button. Intake lets a pump on that network draw from the water the end lies in; " +
                "Outflow lets liquid leave the network there. Off: every loose end is capped.");
            using (Dependent(list, "tankLitresPerCycle"))
            {
                list.Label("Tank to tank: " + RM_Volume.FormatLitres(tankLitresPerCycle) + " per tank per pump cycle");
                tankLitresPerCycle = Mathf.RoundToInt(list.Slider(tankLitresPerCycle, 100f, 10000f) / 100f) * 100;
            }
            list.CheckboxLabeled("Hoses hold liquid and spill it when they stop", ref hoseHoldsLiquid,
                "On: a hose holds a little of what flows through it, and when it stops carrying (capped, wound in, dropped, unplugged) " +
                "that liquid runs out of its open end: into a channel, or onto the ground as a spill colonists clean up. Off: hoses hold nothing.");
            using (Dependent(list, "hoseLitresPerCell"))
            {
                list.Label("Liquid held per hose cell: " + RM_Volume.FormatLitres(hoseLitresPerCell));
                hoseLitresPerCell = Mathf.Round(list.Slider(hoseLitresPerCell, 0f, 50f) * 2f) / 2f;
            }
            list.Label("Dump tank drain with no pump: " + RM_Volume.FormatLitres(dumpLitresPerCycle) + " per pump cycle (a pump set to Pour is faster)");
            dumpLitresPerCycle = Mathf.RoundToInt(list.Slider(dumpLitresPerCycle, 100f, 5000f) / 100f) * 100;
            list.Label("Plump amount: " + plumpAmount.ToString("0.0") + "x");
            plumpAmount = Mathf.Round(list.Slider(plumpAmount, 0f, 1.5f) * 10f) / 10f;
            list.Label("Hose thickness: " + thickness.ToString("0.00") + "x (art only; 1 = the standard hose)");
            thickness = Mathf.Round(list.Slider(thickness, 0.5f, 1f) * 20f) / 20f;
            ApplyThickness();
            list.Label("Flat/plump transition: " + transitionTicks + " ticks");
            transitionTicks = Mathf.RoundToInt(list.Slider(transitionTicks, 10f, 120f));
            list.Label("Collapse after no flow for: " + releaseTicks + " ticks (keeps a stalling pump from flickering the hose)");
            releaseTicks = Mathf.RoundToInt(list.Slider(releaseTicks, 100f, 1500f) / 50f) * 50;
            list.Label("Least time a hose stays plump: " + minPlumpDwell + " ticks (also how long a new liquid must flow before the hose takes its colour)");
            minPlumpDwell = Mathf.RoundToInt(list.Slider(minPlumpDwell, 0f, 2000f) / 50f) * 50;
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
            using (Dependent(list, "handlingTime", "windCellsPerSecond", "autoResumeDroppedHose"))
            {
                list.Label("Handling time (grab, set down, couple): " + handlingTime.ToString("0.00") + "x", -1f,
                    (TipSignal?)"Scales how long a colonist takes to pick the hose end up, put it down and screw it on. 1x = 45 / 30 / 90 ticks.");
                handlingTime = Mathf.Round(list.Slider(handlingTime, 0.25f, 3f) * 20f) / 20f;
                list.Label("Winding speed: " + windCellsPerSecond.ToString("0.0") + " cells per second", -1f,
                    (TipSignal?)"How fast a colonist winds a hose back onto the reel (a clumsy colonist is slower).");
                windCellsPerSecond = Mathf.Round(list.Slider(windCellsPerSecond, 1f, 8f) * 2f) / 2f;
                list.CheckboxLabeled("Interrupted hoses are picked up again automatically", ref autoResumeDroppedHose,
                    "When a colonist is drafted, downed or distracted mid-carry the hose end lies where he left it and the order stays. " +
                    "On: an idle colonist takes it up again. Off: the end waits until you order it.");
            }
                list.GapLine();
            }

            if (Group(list, "Look", RimMandrake.Shared.SettingScope.Now, new[] { "tintByContents", "fillWobble", "defaultLook" }))
            {
            using (Dependent(list, "tintByContents", "fillWobble"))
            {
                list.CheckboxLabeled("Charged hoses darken with what they carry", ref tintByContents);
                list.CheckboxLabeled("Brief wobble when a hose fills or drains", ref fillWobble);
            }
            list.Label("Look of reels built without a picked look: " + defaultLook);
            if (list.ButtonText("Change default reel look"))
            {
                var opts = new List<FloatMenuOption>();
                foreach (string l in HoseStyles.Looks) { string look = l; opts.Add(new FloatMenuOption(look, () => defaultLook = look)); }
                Find.WindowStack.Add(new FloatMenu(opts));
            }
                list.GapLine();
            }
        }

        // SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST: master -> dependents, each checked at its read site (2026-10-14).
        // `enabled` stops the hose draw (RM_MapComponent_Hoses.MapComponentUpdate returns), the hose orders (WorkGiver_HoseOrders,
        // the float-menu provider) and the carry/retract jobs, so the draw tint/wobble and the colonist-handling numbers are inert
        // with it off. Left Independent on purpose because something still reads them with the master off: the tank rules and
        // liquid-network numbers belong to the pipe network, not the hose draw; dumpLitresPerCycle is also the Pour pump's cap;
        // the shape numbers (bend, length, joiners, slack, plump, timings) are read by the reel's saved layout and the probe;
        // defaultLook styles a reel at build time. hoseSettingsImported is a migration flag with no control.
        internal static readonly RimMandrake.Shared.SettingDependencies Masters = new RimMandrake.Shared.SettingDependencies()
            .Declare("enabled", "tintByContents", "fillWobble", "handlingTime", "windCellsPerSecond", "autoResumeDroppedHose")
            .Declare("tankModesEnabled", "tankLitresPerCycle")
            .Declare("hoseHoldsLiquid", "hoseLitresPerCell")
            .Independent("freeEndRolesEnabled", "dumpLitresPerCycle", "plumpAmount", "thickness", "transitionTicks", "releaseTicks", "minPlumpDwell",
                         "minBendRadius", "maxLength", "maxLengthDefaults", "couplingSpacing", "slack", "defaultLook")
            .Name("enabled", "Flexible hoses (master switch)").Name("tankModesEnabled", "Tank jobs: Store / Fill / Empty / Dump")
            .Name("hoseHoldsLiquid", "Hoses hold liquid and spill it when they stop");

        private static object GetField(string n) => typeof(RM_HoseSettings).GetField(n, BindingFlags.Public | BindingFlags.Static)?.GetValue(null);
        private static void SetField(string n, object v) => typeof(RM_HoseSettings).GetField(n, BindingFlags.Public | BindingFlags.Static)?.SetValue(null, v);

        private static System.IDisposable Dependent(Listing_Standard list, params string[] keys) =>
            RimMandrake.Shared.SettingsKitMastersDrawer.Dependent(list, Masters, GetField, SetField, keys);

        /// <summary>Every hose setting back to its shipped value (the hose section's Reset-all button, after its confirmation).
        /// hoseSettingsImported is the one-time migration flag, not a setting: resetting it would re-import the old GSS file.</summary>
        public static void ResetAllFields()
        {
            var names = new List<string>(shippedDefaults.Keys);
            names.Remove("hoseSettingsImported");
            ResetFields(names.ToArray());
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int/string/enum setting, read from the field
        // initialisers. MUST stay below every public setting field (C# runs static initialisers in textual order); the
        // private UI state below it is not snapshotted.
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_HoseSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int) || f.FieldType == typeof(string) || f.FieldType.IsEnum)
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_HoseSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): every Hose setting is read live by the hose draw pass, a colonist job, or a re-lay on window close (the shape fingerprint changes), none at world or map generation, so all are [now]. maxLengthDefaults has no control on this screen (probe and migration values) and only reset.</summary>
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
}
