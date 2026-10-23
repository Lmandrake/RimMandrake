using System;
using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.GimmeSomeSlack.Core;
using System.Reflection;
using UnityEngine;
using Verse;
using RimMandrake.Shared.Slack;

// The JawaBench bridge companion (bridgetools/JawaBench.BridgeTools) drives this mod's internal cord geometry types
// (_Shared/SlackGeometry is internal in each assembly since the hose port).
[assembly: System.Runtime.CompilerServices.InternalsVisibleTo("JawaBench.BridgeTools")]

namespace RimMandrake.GimmeSomeSlack
{
    /// <summary>The cord art families of design §8.11. Only families whose art is installed are
    /// selectable; the rest show as "art not installed yet" (CordMaterials.StyleInstalled checks the strand textures).</summary>
    public enum CordStyle { StarWarsJawa, ExtensionCord, Cybertek, StarWars }

    /// <summary>Extension-cord colours: a different colour per power net (seeded per net), or one colour everywhere.</summary>
    public enum ExtCordColorMode { Mixed, Single }

    /// <summary>How lifted pieces sway (phase-2 doc 1.5): CPU (shipping default, per-frame deformed mesh) or Shader
    /// (the engine's CutoutPlant vertex shader, vertex alpha = sway weight). Shader falls back to CPU by itself when
    /// the plant shader or its wind registration is unavailable (see RM_MapComponent_CordGraph.EffectiveSwayMode).</summary>
    public enum SwayMode { CPU, Shader }

    // ════════════════════════════════════════════════════════════════════
    // Mod Settings (owner, 2026-09-12: every mod ships a real settings screen; defaults = shipped
    // behaviour; all-off degrades to vanilla). Static fields so jawa/mod_settings_field can read and
    // write them; GimmeSomeSlackSettings.Apply() is what makes a change take effect, and the screen and
    // the probe channel (GimmeSomeSlackProbe) both call it.
    // ════════════════════════════════════════════════════════════════════
    public class GimmeSomeSlackSettings : ModSettings
    {
        /// <summary>Master switch. Off: conduit art and hookup wires are vanilla again, no cords.</summary>
        public static bool enabled = true;
        public static CordStyle style = CordStyle.StarWarsJawa;
        /// <summary>Multiplier on the seeded slack: 0 path-tight, 1 owner level (design §8.2.4), 1.8 feral.</summary>
        public static float slack = 1f;
        /// <summary>Loop budget, cells: the most cord one cord may spend on loops, figure-eights and heaps (LayParams.MaxExtra:
        /// CordLayer.Sprawl's slack target and settle clamp). It does NOT cap a cord's length: the side-to-side wander comes on
        /// top (gss_offline_fuzz_B.md seed 141: budget 2, a 1-cell lead lays 10.9 cells). Renamed from the old key by GPT source
        /// read 2026-10-06 A12/B15 (owner decision by question card: name it for what it controls); the old saved key is read
        /// once on load (LegacyName.LoopBudgetOnLoad).</summary>
        public static float loopBudget = 16f;
        /// <summary>Cords drawn per connection: 1..this, seeded per edge, never by load.</summary>
        public static int cordsPerConnection = 3;
        /// <summary>Dense conduit fields drawn as one heap (§8.7.4).</summary>
        public static bool tangles = true;
        /// <summary>Short needless spurs drawn as pointless loops in the cord (§8.7.5).</summary>
        public static bool needlessLoops = true;
        /// <summary>Dive-through (owner 2026-10-06): a cord with no open-floor route dives under the wall, rock, water or
        /// building in its way and comes back up on the far side. Off = such a cord is drawn straight across, flagged unroutable.</summary>
        public static bool diveThrough = true;
        /// <summary>CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT (owner 2026-10-23): a cord into a building comes in at a diagonal and slides
        /// under it, never onto a side's midpoint where pipe and hose ports sit. Off = the straight, square plug of round 2.</summary>
        public static bool slideUnder = true;
        /// <summary>Break readout (§8.5): live ends spark, dead ends lie limp.</summary>
        public static bool breakReadout = true;
        /// <summary>Spark rate multiplier for live ends (0 = never).</summary>
        public static float sparkIntensity = 1f;
        /// <summary>Hide vanilla's thin machine hookup wires for our conduit (never the power-overlay lines).</summary>
        public static bool hideHookupWires = true;
        /// <summary>Draw the node graph (nodes, edges) over the map. Off by default.</summary>
        public static bool debugDraw = false;
        // ---- phase 1b (lane A, 2026-10-02)
        /// <summary>Messiness: a dense conduit field of at least this many cells becomes one tangle (6-20).</summary>
        public static int tangleMin = 9;
        /// <summary>Live floor ends whip (drawn per frame, also while paused).</summary>
        public static bool whip = true;
        /// <summary>Live wall-terminal ends drip sparks in irregular bursts (downed wire), never a steady arc.</summary>
        public static bool downedWire = true;
        /// <summary>Sparks and glow only while the power overlay is open.</summary>
        public static bool sparksOnlyOverlay = false;
        /// <summary>Most sparking/whipping/dripping ends per map (8-48).</summary>
        public static int maxSparkingEnds = 24;
        /// <summary>Selecting anything on a power net highlights every cord of that net.</summary>
        public static bool highlight = true;
        /// <summary>Lifted pieces (wall-hanging tails) sway in the wind; obeys vanilla's plant-sway preference.</summary>
        public static bool sway = true;
        /// <summary>Sway strength multiplier (0-2).</summary>
        public static float swayAmplitude = 1f;
        /// <summary>Sway route for lifted pieces: CPU (default) or the plant vertex shader (optional).</summary>
        public static SwayMode swayMode = SwayMode.CPU;
        /// <summary>Optional: outdoor floor cords ripple slightly in the wind. On by default (owner 2026-10-15); off leaves floor cords still.</summary>
        public static bool floorRipple = true;
        /// <summary>Far-zoom simplification: one thin strand per cord, no decals.</summary>
        public static bool lod = true;
        // ---- art styles (lane C, 2026-10-02)
        /// <summary>Extension-cord style only: one colour per net (Mixed) or one colour everywhere (Single).</summary>
        public static ExtCordColorMode extCordColorMode = ExtCordColorMode.Mixed;
        /// <summary>The single colour, an index into CordMaterials.ExtCordColors (0 Orange .. 4 Blue).</summary>
        public static int extCordColor = 0;
        /// <summary>Design §5 per-def toggles: conduit defNames the player unticked (they keep vanilla art, no cords). Empty =
        /// every eligible conduit becomes cords (the shipped behaviour).</summary>
        public static List<string> excludedConduits = new List<string>();

        public override void ExposeData()
        {
            base.ExposeData();
            RimMandrake.Shared.PatchApplier.BeforeExpose(GetType());   // a feature forced off by a failed patch is never SAVED as off
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref style, "style", CordStyle.StarWarsJawa);
            Scribe_Values.Look(ref slack, "slack", 1f);
            Scribe_Values.Look(ref loopBudget, "loopBudget", LegacyName.Unset);
            if (Scribe.mode == LoadSaveMode.LoadingVars)
            {
                float legacy = LegacyName.Unset;
                Scribe_Values.Look(ref legacy, LegacyName.OldLoopBudgetKey, LegacyName.Unset);
                loopBudget = LegacyName.LoopBudgetOnLoad(loopBudget, legacy, 16f);
            }
            Scribe_Values.Look(ref cordsPerConnection, "cordsPerConnection", 3);
            Scribe_Values.Look(ref tangles, "tangles", true);
            Scribe_Values.Look(ref needlessLoops, "needlessLoops", true);
            Scribe_Values.Look(ref diveThrough, "diveThrough", true);
            Scribe_Values.Look(ref slideUnder, "slideUnder", true);
            Scribe_Values.Look(ref breakReadout, "breakReadout", true);
            Scribe_Values.Look(ref sparkIntensity, "sparkIntensity", 1f);
            Scribe_Values.Look(ref hideHookupWires, "hideHookupWires", true);
            Scribe_Values.Look(ref debugDraw, "debugDraw", false);
            Scribe_Values.Look(ref tangleMin, "tangleMin", 9);
            Scribe_Values.Look(ref whip, "whip", true);
            Scribe_Values.Look(ref downedWire, "downedWire", true);
            Scribe_Values.Look(ref sparksOnlyOverlay, "sparksOnlyOverlay", false);
            Scribe_Values.Look(ref maxSparkingEnds, "maxSparkingEnds", 24);
            Scribe_Values.Look(ref highlight, "highlight", true);
            Scribe_Values.Look(ref sway, "sway", true);
            Scribe_Values.Look(ref swayAmplitude, "swayAmplitude", 1f);
            Scribe_Values.Look(ref swayMode, "swayMode", SwayMode.CPU);
            Scribe_Values.Look(ref floorRipple, "floorRipple", true);
            Scribe_Values.Look(ref lod, "lod", true);
            Scribe_Values.Look(ref extCordColorMode, "extCordColorMode", ExtCordColorMode.Mixed);
            Scribe_Values.Look(ref extCordColor, "extCordColor", 0);
            Scribe_Collections.Look(ref excludedConduits, "excludedConduits", LookMode.Value);
            if (excludedConduits == null) excludedConduits = new List<string>();
            RimMandrake.Shared.PatchApplier.AfterExpose(GetType());
        }

        public static void ResetToDefaults()
        {
            enabled = true;
            excludedConduits = new List<string>();
            style = CordStyle.StarWarsJawa;
            slack = 1f;
            loopBudget = 16f;
            cordsPerConnection = 3;
            tangles = true;
            needlessLoops = true;
            diveThrough = true;
            slideUnder = true;
            breakReadout = true;
            sparkIntensity = 1f;
            hideHookupWires = true;
            debugDraw = false;
            tangleMin = 9;
            whip = true;
            downedWire = true;
            sparksOnlyOverlay = false;
            maxSparkingEnds = 24;
            highlight = true;
            sway = true;
            swayAmplitude = 1f;
            swayMode = SwayMode.CPU;
            floorRipple = true;
            lod = true;
            extCordColorMode = ExtCordColorMode.Mixed;
            extCordColor = 0;
        }

        public static BuildOptions BuildOptions()
        {
            var o = new BuildOptions { Tangles = tangles, NeedlessLoops = needlessLoops, TangleMin = Mathf.Clamp(tangleMin, 6, 20),
                                     // power strips are the modern extension-cord look only (owner review 2026-10-04 B1/B15)
                                     Pile = style == CordStyle.ExtensionCord ? PileArt.Strips : PileArt.Junctions };
            o.DiveThrough = diveThrough;
            o.SlideUnder = slideUnder;
            o.Lay.SlackScale = Mathf.Clamp(slack, 0f, 2f);
            o.Lay.MaxExtra = Mathf.Clamp(loopBudget, 2f, 40f);
            o.Lay.MinExtra = Math.Min(o.Lay.MinExtra, o.Lay.MaxExtra);
            o.Lay.CordsMax = Mathf.Clamp(cordsPerConnection, 1, 3);
            return o;
        }

        /// <summary>The settings as they were last applied (Core.SettingsPrint); WriteSettings skips the whole re-print when
        /// the window closes on unchanged settings (GPT pre-release B24).</summary>
        private static string appliedPrint;
        internal static bool ChangedSinceApply => appliedPrint != Core.SettingsPrint.Of(typeof(GimmeSomeSlackSettings));

        /// <summary>Make the current values take effect: conduit texture swap or restore, and a
        /// rebuild of every map's cords and hookup-wire prints.</summary>
        public static void Apply()
        {
            appliedPrint = Core.SettingsPrint.Of(typeof(GimmeSomeSlackSettings));
            ConduitVisuals.RetargetFromSettings();
            ConduitVisuals.Apply(enabled);
            // a style / colour-mode change rebuilds the materials in place (no restart); the regenerate below
            // reprints every cord mesh with them
            CordMaterials.EnsureCurrent();
            Aerial.AerialMaterials.EnsureCurrent();
            if (Current.ProgramState != ProgramState.Playing || Find.Maps == null) return;
            foreach (Map map in Find.Maps)
            {
                map.GetComponent<RM_MapComponent_CordGraph>()?.Notify_SettingsChanged();
                map.mapDrawer.RegenerateEverythingNow();
            }
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);
            RimMandrake.Shared.SettingsKitMastersDrawer.ResetAllButton(list, "Gimme Some Slack (both tabs)", ResetEverything);

            if (Group(list, "Messy cords and default style", RimMandrake.Shared.SettingScope.Now, new[] { "enabled", "style", "extCordColorMode", "extCordColor", "hideHookupWires" }))
            {
            list.CheckboxLabeled("Messy cords (master switch)", ref enabled,
                "Conduit becomes invisible and is drawn as loose, too-long cords between what it connects. " +
                "Off: vanilla conduit art and hookup wires come back as soon as you close this window.");
            // per-build style (stage 2, design 2.4): the style is picked on each build button; this is only the default
            list.Label("Default style. Style is chosen when you build (the build button's menu); this sets what new games start with and how unstyled conduit looks (changes take effect when this window closes)");
            foreach (CordStyle s in Enum.GetValues(typeof(CordStyle)))
            {
                bool installed = CordMaterials.StyleInstalled(s);
                string label = GimmeSomeSlackMod.StyleLabel(s) + (installed ? "" : "  (art not installed yet)");
                Rect r = list.GetRect(30f);
                Rect swatchRect = new Rect(r.xMax - 210f, r.y + 7f, 200f, 16f);
                Rect radio = new Rect(r.x, r.y, r.width - 220f, r.height);
                if (installed)
                {
                    if (Widgets.RadioButtonLabeled(radio, label, style == s)) style = s;
                    GimmeSomeSlackMod.DrawSwatch(swatchRect, s);
                }
                else
                {
                    GUI.color = Color.gray;
                    Widgets.Label(radio, "   " + label);
                    GUI.color = Color.white;
                }
            }
            using (Dependent(list, "extCordColorMode", "extCordColor", "hideHookupWires"))
            {
            if (style == CordStyle.ExtensionCord)
            {
                if (list.RadioButton("   Default Modern colour: a different colour per run", extCordColorMode == ExtCordColorMode.Mixed))
                    extCordColorMode = ExtCordColorMode.Mixed;
                if (list.RadioButton("   Default Modern colour: one colour (" + CordMaterials.ExtCordColors[Mathf.Clamp(extCordColor, 0, CordMaterials.ExtCordColors.Length - 1)] + ")",
                                  extCordColorMode == ExtCordColorMode.Single))
                    extCordColorMode = ExtCordColorMode.Single;
                if (extCordColorMode == ExtCordColorMode.Single)
                    extCordColor = Mathf.RoundToInt(list.Slider(extCordColor, 0f, CordMaterials.ExtCordColors.Length - 1));
            }
            list.CheckboxLabeled("Hide vanilla's thin machine hookup wires (power overlay lines always stay)", ref hideHookupWires);
            }
                list.GapLine();
            }

            if (Group(list, "Slack, loops and tangles", RimMandrake.Shared.SettingScope.Now, new[] { "slack", "loopBudget", "cordsPerConnection", "tangles", "needlessLoops", "diveThrough", "slideUnder", "tangleMin" }))
            {
            using (Dependent(list, "slack", "loopBudget", "cordsPerConnection", "tangles", "needlessLoops", "diveThrough", "slideUnder"))
            {
            list.Label("Slack: " + (slack <= 0.01f ? "off (path-tight)" : slack.ToString("0.00") + "x the owner level"),
                    tooltip: "How much spare cord each cord carries. 1.00 = loops, figure-eights and heaps like a too-long extension cord.");
            slack = list.Slider(slack, 0f, 1.8f);
            list.Label("Loop budget: up to " + loopBudget.ToString("0") + " cells of each cord in loops and heaps",
                    tooltip: "How much cord one cord may spend on loops, figure-eights and heaps. This is not a length cap: a cord's side-to-side wander comes on top, so a short lead can still lie several times its distance.");
            loopBudget = list.Slider(loopBudget, 2f, 40f);
            list.Label("Cords per connection: 1 to " + cordsPerConnection);
            cordsPerConnection = Mathf.RoundToInt(list.Slider(cordsPerConnection, 1f, 3f));
            list.CheckboxLabeled("Dense conduit fields become one tangle", ref tangles);
            list.CheckboxLabeled("Needless conduit stubs become pointless loops", ref needlessLoops);
            list.CheckboxLabeled("Cords dive under walls and water where they must (a plate marks each wall crossing)", ref diveThrough);
            list.CheckboxLabeled("Cords slide under buildings at a diagonal (never onto a pipe or hose port)", ref slideUnder,
                    "On: a cord comes in at a slant, off the middle of the building's side where pipe and hose ports sit, and runs on under it. Off: the straight plug into the middle of the side.");
            }
            using (Dependent(list, "tangleMin"))
            {
            list.Label("Messiness: a dense conduit field of " + tangleMin + "+ cells becomes one tangle",
                    tooltip: "Lower = more of a crowded base turns into heaps of cord plugged into junction boxes (power strips in the Modern look).");
            tangleMin = Mathf.RoundToInt(list.Slider(tangleMin, 6f, 20f));
            }
                list.GapLine();
            }

            if (Group(list, "Breaks and sparks", RimMandrake.Shared.SettingScope.Now, new[] { "breakReadout", "sparkIntensity", "whip", "downedWire", "sparksOnlyOverlay", "maxSparkingEnds", "highlight" }))
            {
            list.Label("These also govern fallen overhead wires (with their own sparking-ends budget of the same size); spark intensity and the overlay-only option also govern power-tap clamp sparks.");
            list.CheckboxLabeled("Break readout: live ends spark, dead ends lie limp", ref breakReadout);
            list.Label("Spark intensity: " + sparkIntensity.ToString("0.0") + "x");
            sparkIntensity = list.Slider(sparkIntensity, 0f, 2f);
            using (Dependent(list, "whip"))
            {
            list.CheckboxLabeled("Live broken ends whip about (also while paused)", ref whip);
            }
            using (Dependent(list, "downedWire"))
            {
            list.CheckboxLabeled("Live wires hanging out of walls drip sparks in bursts", ref downedWire);
            }
            list.CheckboxLabeled("Sparks only while the power overlay is open", ref sparksOnlyOverlay);
            list.Label("Most sparking ends per map: " + maxSparkingEnds);
            maxSparkingEnds = Mathf.RoundToInt(list.Slider(maxSparkingEnds, 8f, 48f));
            using (Dependent(list, "highlight"))
            {
            list.CheckboxLabeled("Selecting a powered building highlights every cord of its net", ref highlight);
            }
                list.GapLine();
            }

            if (Group(list, "Wind sway", RimMandrake.Shared.SettingScope.Now, new[] { "sway", "swayAmplitude", "swayMode", "floorRipple" }))
            {
            using (Dependent(list, "sway", "swayAmplitude", "floorRipple", "swayMode"))
            {
            list.CheckboxLabeled("Hanging cords sway in the wind (obeys the game's plant-sway option)", ref sway);
            list.Label("Sway strength: " + swayAmplitude.ToString("0.0") + "x");
            swayAmplitude = list.Slider(swayAmplitude, 0f, 2f);
            using (Dependent(list, "swayMode"))
            {
            if (list.RadioButton("   Sway drawn on the CPU (default, always works)", swayMode == SwayMode.CPU,
                              tooltip: "Each hanging cord on screen is bent every frame. Costs a little CPU; this is the shipping behaviour."))
                swayMode = SwayMode.CPU;
            if (list.RadioButton("   Sway drawn by the plant wind shader (experimental, zero CPU)", swayMode == SwayMode.Shader,
                              tooltip: "Hanging cords use the same wind shader as plants and move with them. Falls back to the CPU route " +
                                       "by itself if the shader is unavailable. Under a roof hanging cords never sway."))
                swayMode = SwayMode.Shader;
            }
            list.CheckboxLabeled("Outdoor floor cords ripple slightly in the wind", ref floorRipple,
                "Off: cords on the floor lie still. On (default): unroofed floor cords on screen ripple gently with the wind " +
                "(uses the sway strength above; obeys the game's plant-sway option).");
            }
                list.GapLine();
            }

            if (Group(list, "Which conduits become cords", RimMandrake.Shared.SettingScope.Now, new[] { "excludedConduits" }))
            {
            using (Dependent(list, "excludedConduits"))
            {
            list.Label("Ticked conduits are drawn as messy cords; unticked ones keep their own art. Hidden conduit always stays hidden.");
            foreach (ThingDef d in ConduitVisuals.Candidates)
            {
                bool on = !excludedConduits.Contains(d.defName), was = on;
                list.CheckboxLabeled(d.LabelCap + "  (" + d.defName + (d.modContentPack != null && !d.modContentPack.IsOfficialMod ? ", " + d.modContentPack.Name : "") + ")", ref on);
                if (on != was) Core.ConduitTargets.Toggle(excludedConduits, d.defName, on);
            }
            }
                list.GapLine();
            }

            if (Group(list, "Far zoom and debug", RimMandrake.Shared.SettingScope.Now, new[] { "lod", "debugDraw" }))
            {
            using (Dependent(list, "lod", "debugDraw"))
            {
            list.CheckboxLabeled("Far zoom: simplify cords (one thin strand, no pieces)", ref lod);
            list.CheckboxLabeled("Debug: draw the node graph", ref debugDraw);
            }
                list.GapLine();
            }

            viewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1200f;

        /// <summary>SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST: master switches, from each setting's READ SITE (2026-10-14).
        /// "enabled" gates the cord graph, its section layers, sparks, highlight and debug draw, the hookup-wire hiding, the
        /// conduit style picker and the conduit swap. Independent, because the Overhead lines tab reads them with only its own
        /// master, so greying them here would lie: the default style (AerialMaterials / StylePicker.DefaultLook: the default
        /// look of masts and wires too) and the four spark settings (RM_MapComponent_Aerial: fallen wires and tap clamps).</summary>
        internal static readonly RimMandrake.Shared.SettingDependencies Masters = new RimMandrake.Shared.SettingDependencies()
            .Declare("enabled", "extCordColorMode", "extCordColor", "hideHookupWires", "slack", "loopBudget", "cordsPerConnection",
                     "tangles", "needlessLoops", "diveThrough", "slideUnder", "tangleMin", "whip", "downedWire", "highlight", "sway", "swayAmplitude",
                     "swayMode", "floorRipple", "excludedConduits", "lod", "debugDraw")
            .Declare("tangles", "tangleMin")          // BuildOptions: TangleMin is used only while Tangles (CordBuilder)
            .Declare("breakReadout", "whip")           // whip = whip && breakReadout (CordGraph, MessyCords layer)
            .Declare("sway", "swayMode")               // the sway route only matters while hanging cords sway
            .Independent("style", "breakReadout", "sparkIntensity", "sparksOnlyOverlay", "maxSparkingEnds")
            .Name("enabled", "Messy cords (master switch)").Name("tangles", "Dense conduit fields become one tangle")
            .Name("breakReadout", "Break readout").Name("sway", "Hanging cords sway in the wind");

        private static object GetField(string n)
        {
            // a COPY of the per-def list, so a greyed block's snapshot is not mutated in place
            if (n == nameof(excludedConduits)) return new List<string>(excludedConduits);
            return typeof(GimmeSomeSlackSettings).GetField(n, BindingFlags.Public | BindingFlags.Static)?.GetValue(null);
        }

        private static void SetField(string n, object v)
        {
            if (n == nameof(excludedConduits)) { excludedConduits = new List<string>((List<string>)v); return; }
            typeof(GimmeSomeSlackSettings).GetField(n, BindingFlags.Public | BindingFlags.Static)?.SetValue(null, v);
        }

        private static IDisposable Dependent(Listing_Standard list, params string[] keys) =>
            RimMandrake.Shared.SettingsKitMastersDrawer.Dependent(list, Masters, GetField, SetField, keys);

        /// <summary>Every Cables setting back to its shipped value (the field-initialiser snapshot plus the per-def list).</summary>
        public static void ResetAllFields()
        {
            var names = new List<string>(shippedDefaults.Keys) { nameof(excludedConduits) };
            ResetFields(names.ToArray());
        }

        /// <summary>The Reset-all button (both tabs, after the confirmation): both settings classes back to shipped, then applied.</summary>
        internal static void ResetEverything()
        {
            ResetAllFields();
            Aerial.AerialSettings.ResetAllFields();
            Apply();
            Aerial.AerialSettings.Apply();
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int/string/enum setting, read from the field
        // initialisers. MUST stay textually AFTER every public static setting's initialiser (C# runs them in textual order;
        // only the private UI-state fields below may follow it).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(GimmeSomeSlackSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int) || f.FieldType == typeof(string) || f.FieldType.IsEnum)
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                // the per-def conduit list is a collection, which the scalar snapshot does not hold: its shipped value is empty
                if (n == nameof(excludedConduits)) { excludedConduits = new List<string>(); continue; }
                FieldInfo f = typeof(GimmeSomeSlackSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): every cable setting is read live by the cord graph rebuild, per-frame draw, spark/whip tick or placement, and GimmeSomeSlackSettings.Apply() re-prints every map when this window closes; none is read at world or map generation, so all are [now].</summary>
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

    public class GimmeSomeSlackMod : Mod
    {
        public static GimmeSomeSlackSettings Settings;

        public GimmeSomeSlackMod(ModContentPack content) : base(content)
        {
            LegacyMigration.SettingsFiles(content);
            try { Settings = GetSettings<GimmeSomeSlackSettings>(); }
            finally { SettingsLoaded(); }
        }

        private static int settingsLoaded;

        /// <summary>Both Mod constructors call this after their GetSettings; the second applies Harmony, so no patch can fail
        /// (and force a feature off) before both settings files have loaded their player values. Each class also passes
        /// GetType() to PatchApplier.Before/AfterExpose, so a later load re-reads only its own fields.</summary>
        internal static void SettingsLoaded()
        {
            if (++settingsLoaded != 2) return;
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.gimmesomeslack"), typeof(GimmeSomeSlackMod).Assembly, "RimMandrake.GimmeSomeSlack");
        }

        public override string SettingsCategory() => "RimMandrake: Gimme Some Slack";

        /// <summary>Owner review 2026-10-04 B27, his words: the one header line of the one settings entry.</summary>
        public const string Header = "Drawn flexible pipes and wires to better display simple circuit-like plans underneath.";

        /// <summary>B27: ONE Mod Settings entry for the one mod. The overhead-line settings keep their own ModSettings class and
        /// saved file (no settings lost on upgrade), but its Mod returns an empty category so RimWorld does not list it; this
        /// window draws both as tabs and writes both when it closes. (The flexible hoses moved to FlowWorks, 2026-10-11.)</summary>
        public override void WriteSettings()
        {
            base.WriteSettings();
            if (GimmeSomeSlackSettings.ChangedSinceApply) GimmeSomeSlackSettings.Apply();   // B24: no re-print on an unchanged close
            LoadedModManager.GetMod<Aerial.AerialLinesMod>()?.WriteSettings();
        }

        public enum SettingsTab { Cables, OverheadLines }
        private static SettingsTab tab = SettingsTab.Cables;

        public override void DoSettingsWindowContents(Rect inRect)
        {
            Text.Font = GameFont.Small;
            Widgets.Label(new Rect(inRect.x, inRect.y, inRect.width, 26f), Header);
            var tabs = new List<TabRecord>
            {
                new TabRecord("Cables", () => tab = SettingsTab.Cables, tab == SettingsTab.Cables),
                new TabRecord("Overhead lines", () => tab = SettingsTab.OverheadLines, tab == SettingsTab.OverheadLines),
            };
            Rect body = new Rect(inRect.x, inRect.y + 26f + TabDrawer.TabHeight + 6f, inRect.width, inRect.height - 32f - TabDrawer.TabHeight);
            Widgets.DrawMenuSection(body);
            TabDrawer.DrawTabs(new Rect(body.x, body.y, body.width, TabDrawer.TabHeight), tabs);
            Rect inner = body.ContractedBy(10f);
            switch (tab)
            {
                case SettingsTab.OverheadLines: LoadedModManager.GetMod<Aerial.AerialLinesMod>()?.DoSettingsWindowContents(inner); break;
                default: Settings?.DoWindowContents(inner); break;
            }
            RimMandrake.Shared.PatchApplier.ReforceOff();   // a feature whose patch failed cannot be clicked (or reset) back on
        }

        public static string StyleLabel(CordStyle s)
        {
            switch (s)
            {
                // owner review 2026-10-04 B19: labels only; the enum names and the saved key stay as they were
                case CordStyle.StarWarsJawa: return "Scrapper: rough, hacked-together scrap cable and crude scrap masts (default)";
                case CordStyle.ExtensionCord: return "Modern: multi-coloured extension cords and power strips, black power lines";
                case CordStyle.Cybertek: return "Futuristic: sleek grey metallic cable, teal accents, sleek steel poles";
                default: return "Industrial: thick black cable and tough industrial steel poles";
            }
        }

        /// <summary>The style's strand art tiled across the row (every colour / cable kind it uses).</summary>
        internal static void DrawSwatch(Rect r, CordStyle s)
        {
            string[] paths;
            if (s == CordStyle.ExtensionCord)
            {
                paths = new string[CordMaterials.ExtCordColors.Length];
                for (int i = 0; i < paths.Length; i++) paths[i] = CordMaterials.StyleDir + "ExtCord/Strand_" + CordMaterials.ExtCordColors[i];
            }
            else paths = CordMaterials.StrandPathsFor(s);
            float w = r.width / paths.Length;
            for (int i = 0; i < paths.Length; i++)
            {
                Texture2D t = ContentFinder<Texture2D>.Get(paths[i], reportFailure: false);
                if (t != null) GUI.DrawTexture(new Rect(r.x + i * w, r.y, w - 2f, r.height), t, ScaleMode.StretchToFill);
            }
        }
    }

    /// <summary>GIMMESOMESLACK_RENAME_1: the mod was Messy Conduit. Old settings files are copied to their new names
    /// once (each Mod constructor calls this before its GetSettings, whichever runs first does the work), and saved
    /// pre-rename type names resolve to the renamed types (Core/LegacyName.cs holds the mapping and is selftested).</summary>
    internal static class LegacyMigration
    {
        private static bool settingsDone;

        internal static void SettingsFiles(ModContentPack content)
        {
            if (settingsDone) return;
            settingsDone = true;
            try
            {
                foreach (string f in LegacyName.MigrateSettingsFiles(GenFilePaths.ConfigFolderPath, content?.FolderName))
                    Log.Message("[GimmeSomeSlack] carried old Messy Conduit settings over to " + f);
            }
            catch (Exception ex) { Log.Warning("[GimmeSomeSlack] could not carry old Messy Conduit settings over: " + ex.Message); }
        }
    }

    /// <summary>A save made before the rename names our map components and job drivers RimMandrake.MessyConduit.*;
    /// Scribe resolves every Class attribute through GenTypes.GetTypeInAnyAssembly, so the old name is mapped here.</summary>
    // always on: save compatibility; pre-rename saves name our classes RimMandrake.MessyConduit.*
    [RimMandrake.Shared.PatchFeature("Messy cords: load saves from before the rename")]
    [HarmonyPatch(typeof(GenTypes), nameof(GenTypes.GetTypeInAnyAssembly))]
    internal static class Patch_GenTypes_LegacyTypeName
    {
        private static void Prefix(ref string typeName)
        {
            string mapped = LegacyName.MapTypeName(typeName);
            if (mapped != null) typeName = mapped;
        }
    }
}
