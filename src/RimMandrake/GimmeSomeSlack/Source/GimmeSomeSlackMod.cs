using System;
using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.GimmeSomeSlack.Core;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack
{
    /// <summary>The cord art families of design §8.11. Only families whose art is installed are
    /// selectable; the rest show as "art not installed yet" (phase 1a ships the Jawa set only).</summary>
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
        /// <summary>Optional: outdoor floor cords ripple slightly in the wind. Off by default (floor cords lie still).</summary>
        public static bool floorRipple = false;
        /// <summary>Far-zoom simplification: one thin strand per cord, no decals.</summary>
        public static bool lod = true;
        // ---- art styles (lane C, 2026-10-02)
        /// <summary>Extension-cord style only: one colour per net (Mixed) or one colour everywhere (Single).</summary>
        public static ExtCordColorMode extCordColorMode = ExtCordColorMode.Mixed;
        /// <summary>The single colour, an index into CordMaterials.ExtCordColors (0 Orange .. 4 Blue).</summary>
        public static int extCordColor = 0;

        public override void ExposeData()
        {
            base.ExposeData();
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
            Scribe_Values.Look(ref floorRipple, "floorRipple", false);
            Scribe_Values.Look(ref lod, "lod", true);
            Scribe_Values.Look(ref extCordColorMode, "extCordColorMode", ExtCordColorMode.Mixed);
            Scribe_Values.Look(ref extCordColor, "extCordColor", 0);
        }

        public static void ResetToDefaults()
        {
            enabled = true;
            style = CordStyle.StarWarsJawa;
            slack = 1f;
            loopBudget = 16f;
            cordsPerConnection = 3;
            tangles = true;
            needlessLoops = true;
            diveThrough = true;
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
            floorRipple = false;
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
            o.Lay.SlackScale = Mathf.Clamp(slack, 0f, 2f);
            o.Lay.MaxExtra = Mathf.Clamp(loopBudget, 2f, 40f);
            o.Lay.MinExtra = Math.Min(o.Lay.MinExtra, o.Lay.MaxExtra);
            o.Lay.CordsMax = Mathf.Clamp(cordsPerConnection, 1, 3);
            return o;
        }

        /// <summary>Make the current values take effect: conduit texture swap or restore, and a
        /// rebuild of every map's cords and hookup-wire prints.</summary>
        public static void Apply()
        {
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
    }

    public class GimmeSomeSlackMod : Mod
    {
        public static GimmeSomeSlackSettings Settings;

        public GimmeSomeSlackMod(ModContentPack content) : base(content)
        {
            LegacyMigration.SettingsFiles(content);
            Settings = GetSettings<GimmeSomeSlackSettings>();
            new Harmony("mandrake.rm.gimmesomeslack").PatchAll(typeof(GimmeSomeSlackMod).Assembly);
        }

        public override string SettingsCategory() => "RimMandrake: Gimme Some Slack";

        /// <summary>Owner review 2026-10-04 B27, his words: the one header line of the one settings entry.</summary>
        public const string Header = "Drawn flexible pipes and wires to better display simple circuit-like plans underneath.";

        /// <summary>B27: ONE Mod Settings entry for the one mod. The overhead-line and flexible-hose settings keep their own
        /// ModSettings classes and saved files (no settings lost on upgrade), but their Mods return an empty category so
        /// RimWorld does not list them; this window draws all three as tabs and writes all three when it closes.</summary>
        public override void WriteSettings()
        {
            base.WriteSettings();
            GimmeSomeSlackSettings.Apply();
            LoadedModManager.GetMod<Aerial.AerialLinesMod>()?.WriteSettings();
            LoadedModManager.GetMod<Hose.FireHosesMod>()?.WriteSettings();
        }

        public enum SettingsTab { Cables, OverheadLines, FlexibleHoses }
        private static SettingsTab tab = SettingsTab.Cables;

        public override void DoSettingsWindowContents(Rect inRect)
        {
            Text.Font = GameFont.Small;
            Widgets.Label(new Rect(inRect.x, inRect.y, inRect.width, 26f), Header);
            var tabs = new List<TabRecord>
            {
                new TabRecord("Cables", () => tab = SettingsTab.Cables, tab == SettingsTab.Cables),
                new TabRecord("Overhead lines", () => tab = SettingsTab.OverheadLines, tab == SettingsTab.OverheadLines),
                new TabRecord("Flexible hoses", () => tab = SettingsTab.FlexibleHoses, tab == SettingsTab.FlexibleHoses),
            };
            Rect body = new Rect(inRect.x, inRect.y + 26f + TabDrawer.TabHeight + 6f, inRect.width, inRect.height - 32f - TabDrawer.TabHeight);
            Widgets.DrawMenuSection(body);
            TabDrawer.DrawTabs(new Rect(body.x, body.y, body.width, TabDrawer.TabHeight), tabs);
            Rect inner = body.ContractedBy(10f);
            switch (tab)
            {
                case SettingsTab.OverheadLines: LoadedModManager.GetMod<Aerial.AerialLinesMod>()?.DoSettingsWindowContents(inner); break;
                case SettingsTab.FlexibleHoses: LoadedModManager.GetMod<Hose.FireHosesMod>()?.DoSettingsWindowContents(inner); break;
                default: DrawCables(inner); break;
            }
        }

        private static Vector2 scroll;
        private static float viewHeight = 1200f;

        private void DrawCables(Rect inRect)
        {
            var view = new Rect(0f, 0f, inRect.width - 20f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            var l = new Listing_Standard { maxOneColumn = true };
            l.Begin(view);
            l.CheckboxLabeled("Messy cords (master switch)", ref GimmeSomeSlackSettings.enabled,
                "Conduit becomes invisible and is drawn as loose, too-long cords between what it connects. " +
                "Off: vanilla conduit art and hookup wires come back as soon as you close this window.");
            l.GapLine();
            // per-build style (stage 2, design 2.4): the style is picked on each build button; this is only the default
            l.Label("Default style. Style is chosen when you build (the build button's menu); this sets what new games start with and how unstyled conduit looks (changes take effect when this window closes)");
            foreach (CordStyle s in Enum.GetValues(typeof(CordStyle)))
            {
                bool installed = CordMaterials.StyleInstalled(s);
                string label = StyleLabel(s) + (installed ? "" : "  (art not installed yet)");
                Rect r = l.GetRect(30f);
                Rect swatchRect = new Rect(r.xMax - 210f, r.y + 7f, 200f, 16f);
                Rect radio = new Rect(r.x, r.y, r.width - 220f, r.height);
                if (installed)
                {
                    if (Widgets.RadioButtonLabeled(radio, label, GimmeSomeSlackSettings.style == s)) GimmeSomeSlackSettings.style = s;
                    DrawSwatch(swatchRect, s);
                }
                else
                {
                    GUI.color = Color.gray;
                    Widgets.Label(radio, "   " + label);
                    GUI.color = Color.white;
                }
            }
            if (GimmeSomeSlackSettings.style == CordStyle.ExtensionCord)
            {
                if (l.RadioButton("   Default Modern colour: a different colour per run", GimmeSomeSlackSettings.extCordColorMode == ExtCordColorMode.Mixed))
                    GimmeSomeSlackSettings.extCordColorMode = ExtCordColorMode.Mixed;
                if (l.RadioButton("   Default Modern colour: one colour (" + CordMaterials.ExtCordColors[Mathf.Clamp(GimmeSomeSlackSettings.extCordColor, 0, 4)] + ")",
                                  GimmeSomeSlackSettings.extCordColorMode == ExtCordColorMode.Single))
                    GimmeSomeSlackSettings.extCordColorMode = ExtCordColorMode.Single;
                if (GimmeSomeSlackSettings.extCordColorMode == ExtCordColorMode.Single)
                    GimmeSomeSlackSettings.extCordColor = Mathf.RoundToInt(l.Slider(GimmeSomeSlackSettings.extCordColor, 0f, CordMaterials.ExtCordColors.Length - 1));
            }
            l.GapLine();
            l.Label("Slack: " + (GimmeSomeSlackSettings.slack <= 0.01f ? "off (path-tight)" : GimmeSomeSlackSettings.slack.ToString("0.00") + "x the owner level"),
                    tooltip: "How much spare cord each cord carries. 1.00 = loops, figure-eights and heaps like a too-long extension cord.");
            GimmeSomeSlackSettings.slack = l.Slider(GimmeSomeSlackSettings.slack, 0f, 1.8f);
            l.Label("Loop budget: up to " + GimmeSomeSlackSettings.loopBudget.ToString("0") + " cells of each cord in loops and heaps",
                    tooltip: "How much cord one cord may spend on loops, figure-eights and heaps. This is not a length cap: a cord's side-to-side wander comes on top, so a short lead can still lie several times its distance.");
            GimmeSomeSlackSettings.loopBudget = l.Slider(GimmeSomeSlackSettings.loopBudget, 2f, 40f);
            l.Label("Cords per connection: 1 to " + GimmeSomeSlackSettings.cordsPerConnection);
            GimmeSomeSlackSettings.cordsPerConnection = Mathf.RoundToInt(l.Slider(GimmeSomeSlackSettings.cordsPerConnection, 1f, 3f));
            l.CheckboxLabeled("Dense conduit fields become one tangle", ref GimmeSomeSlackSettings.tangles);
            l.CheckboxLabeled("Needless conduit stubs become pointless loops", ref GimmeSomeSlackSettings.needlessLoops);
            l.CheckboxLabeled("Cords dive under walls and water where they must (a plate marks each wall crossing)", ref GimmeSomeSlackSettings.diveThrough);
            l.Label("Messiness: a dense conduit field of " + GimmeSomeSlackSettings.tangleMin + "+ cells becomes one tangle",
                    tooltip: "Lower = more of a crowded base turns into heaps of cord plugged into junction boxes (power strips in the Modern look).");
            GimmeSomeSlackSettings.tangleMin = Mathf.RoundToInt(l.Slider(GimmeSomeSlackSettings.tangleMin, 6f, 20f));
            l.GapLine();
            l.CheckboxLabeled("Break readout: live ends spark, dead ends lie limp", ref GimmeSomeSlackSettings.breakReadout);
            l.Label("Spark intensity: " + GimmeSomeSlackSettings.sparkIntensity.ToString("0.0") + "x");
            GimmeSomeSlackSettings.sparkIntensity = l.Slider(GimmeSomeSlackSettings.sparkIntensity, 0f, 2f);
            l.CheckboxLabeled("Live broken ends whip about (also while paused)", ref GimmeSomeSlackSettings.whip);
            l.CheckboxLabeled("Live wires hanging out of walls drip sparks in bursts", ref GimmeSomeSlackSettings.downedWire);
            l.CheckboxLabeled("Sparks only while the power overlay is open", ref GimmeSomeSlackSettings.sparksOnlyOverlay);
            l.Label("Most sparking ends per map: " + GimmeSomeSlackSettings.maxSparkingEnds);
            GimmeSomeSlackSettings.maxSparkingEnds = Mathf.RoundToInt(l.Slider(GimmeSomeSlackSettings.maxSparkingEnds, 8f, 48f));
            l.CheckboxLabeled("Selecting a powered building highlights every cord of its net", ref GimmeSomeSlackSettings.highlight);
            l.CheckboxLabeled("Hanging cords sway in the wind (obeys the game's plant-sway option)", ref GimmeSomeSlackSettings.sway);
            l.Label("Sway strength: " + GimmeSomeSlackSettings.swayAmplitude.ToString("0.0") + "x");
            GimmeSomeSlackSettings.swayAmplitude = l.Slider(GimmeSomeSlackSettings.swayAmplitude, 0f, 2f);
            if (l.RadioButton("   Sway drawn on the CPU (default, always works)", GimmeSomeSlackSettings.swayMode == SwayMode.CPU,
                              tooltip: "Each hanging cord on screen is bent every frame. Costs a little CPU; this is the shipping behaviour."))
                GimmeSomeSlackSettings.swayMode = SwayMode.CPU;
            if (l.RadioButton("   Sway drawn by the plant wind shader (experimental, zero CPU)", GimmeSomeSlackSettings.swayMode == SwayMode.Shader,
                              tooltip: "Hanging cords use the same wind shader as plants and move with them. Falls back to the CPU route " +
                                       "by itself if the shader is unavailable. Under a roof hanging cords never sway."))
                GimmeSomeSlackSettings.swayMode = SwayMode.Shader;
            l.CheckboxLabeled("Outdoor floor cords ripple slightly in the wind (off by default)", ref GimmeSomeSlackSettings.floorRipple,
                "Off: cords on the floor lie still, as shipped. On: unroofed floor cords on screen ripple gently with the wind " +
                "(uses the sway strength above; obeys the game's plant-sway option).");
            l.CheckboxLabeled("Far zoom: simplify cords (one thin strand, no pieces)", ref GimmeSomeSlackSettings.lod);
            l.CheckboxLabeled("Hide vanilla's thin machine hookup wires (power overlay lines always stay)", ref GimmeSomeSlackSettings.hideHookupWires);
            l.CheckboxLabeled("Debug: draw the node graph", ref GimmeSomeSlackSettings.debugDraw);
            l.GapLine();
            if (l.ButtonText("Reset to defaults")) GimmeSomeSlackSettings.ResetToDefaults();
            viewHeight = Mathf.Max(600f, l.CurHeight + 40f);
            l.End();
            Widgets.EndScrollView();
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
        private static void DrawSwatch(Rect r, CordStyle s)
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
