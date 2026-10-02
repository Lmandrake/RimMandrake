using System;
using HarmonyLib;
using RimMandrake.MessyConduit.Core;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit
{
    /// <summary>The cord art families of design §8.11. Only families whose art is installed are
    /// selectable; the rest show as "art not installed yet" (phase 1a ships the Jawa set only).</summary>
    public enum CordStyle { StarWarsJawa, ExtensionCord, Cybertek, StarWars }

    // ════════════════════════════════════════════════════════════════════
    // Mod Settings (owner, 2026-09-12: every mod ships a real settings screen; defaults = shipped
    // behaviour; all-off degrades to vanilla). Static fields so jawa/mod_settings_field can read and
    // write them; MessyConduitSettings.Apply() is what makes a change take effect, and the screen and
    // the probe channel (MessyConduitProbe) both call it.
    // ════════════════════════════════════════════════════════════════════
    public class MessyConduitSettings : ModSettings
    {
        /// <summary>Master switch. Off: conduit art and hookup wires are vanilla again, no cords.</summary>
        public static bool enabled = true;
        public static CordStyle style = CordStyle.StarWarsJawa;
        /// <summary>Multiplier on the seeded slack: 0 path-tight, 1 owner level (design §8.2.4), 1.8 feral.</summary>
        public static float slack = 1f;
        /// <summary>Most extra cord any one cord may carry, cells (the sprawl cap, §8.2.4).</summary>
        public static float sprawlCap = 16f;
        /// <summary>Cords drawn per connection: 1..this, seeded per edge, never by load.</summary>
        public static int cordsPerConnection = 3;
        /// <summary>Dense conduit fields drawn as one heap (§8.7.4).</summary>
        public static bool tangles = true;
        /// <summary>Short needless spurs drawn as pointless loops in the cord (§8.7.5).</summary>
        public static bool needlessLoops = true;
        /// <summary>Break readout (§8.5): live ends spark, dead ends lie limp.</summary>
        public static bool breakReadout = true;
        /// <summary>Spark rate multiplier for live ends (0 = never).</summary>
        public static float sparkIntensity = 1f;
        /// <summary>Hide vanilla's thin machine hookup wires for our conduit (never the power-overlay lines).</summary>
        public static bool hideHookupWires = true;
        /// <summary>Draw the node graph (nodes, edges) over the map. Off by default.</summary>
        public static bool debugDraw = false;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref style, "style", CordStyle.StarWarsJawa);
            Scribe_Values.Look(ref slack, "slack", 1f);
            Scribe_Values.Look(ref sprawlCap, "sprawlCap", 16f);
            Scribe_Values.Look(ref cordsPerConnection, "cordsPerConnection", 3);
            Scribe_Values.Look(ref tangles, "tangles", true);
            Scribe_Values.Look(ref needlessLoops, "needlessLoops", true);
            Scribe_Values.Look(ref breakReadout, "breakReadout", true);
            Scribe_Values.Look(ref sparkIntensity, "sparkIntensity", 1f);
            Scribe_Values.Look(ref hideHookupWires, "hideHookupWires", true);
            Scribe_Values.Look(ref debugDraw, "debugDraw", false);
        }

        public static void ResetToDefaults()
        {
            enabled = true;
            style = CordStyle.StarWarsJawa;
            slack = 1f;
            sprawlCap = 16f;
            cordsPerConnection = 3;
            tangles = true;
            needlessLoops = true;
            breakReadout = true;
            sparkIntensity = 1f;
            hideHookupWires = true;
            debugDraw = false;
        }

        public static BuildOptions BuildOptions()
        {
            var o = new BuildOptions { Tangles = tangles, NeedlessLoops = needlessLoops };
            o.Lay.SlackScale = Mathf.Clamp(slack, 0f, 2f);
            o.Lay.MaxExtra = Mathf.Clamp(sprawlCap, 2f, 40f);
            o.Lay.MinExtra = Math.Min(o.Lay.MinExtra, o.Lay.MaxExtra);
            o.Lay.CordsMax = Mathf.Clamp(cordsPerConnection, 1, 3);
            return o;
        }

        /// <summary>Make the current values take effect: conduit texture swap or restore, and a
        /// rebuild of every map's cords and hookup-wire prints.</summary>
        public static void Apply()
        {
            ConduitVisuals.Apply(enabled);
            if (Current.ProgramState != ProgramState.Playing || Find.Maps == null) return;
            foreach (Map map in Find.Maps)
            {
                map.GetComponent<RM_MapComponent_CordGraph>()?.Notify_SettingsChanged();
                map.mapDrawer.RegenerateEverythingNow();
            }
        }
    }

    public class MessyConduitMod : Mod
    {
        public static MessyConduitSettings Settings;

        public MessyConduitMod(ModContentPack content) : base(content)
        {
            Settings = GetSettings<MessyConduitSettings>();
            new Harmony("mandrake.rm.messyconduit").PatchAll(typeof(MessyConduitMod).Assembly);
        }

        public override string SettingsCategory() => "RimMandrake: Messy Conduit";

        public override void WriteSettings()
        {
            base.WriteSettings();
            MessyConduitSettings.Apply();
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            var l = new Listing_Standard();
            l.Begin(inRect);
            l.CheckboxLabeled("Messy cords (master switch)", ref MessyConduitSettings.enabled,
                "Conduit becomes invisible and is drawn as loose, too-long cords between what it connects. " +
                "Off: vanilla conduit art and hookup wires come back as soon as you close this window.");
            l.GapLine();
            l.Label("Art style");
            foreach (CordStyle s in Enum.GetValues(typeof(CordStyle)))
            {
                bool installed = CordMaterials.StyleInstalled(s);
                string label = StyleLabel(s) + (installed ? "" : "  (art not installed yet)");
                if (installed)
                {
                    if (l.RadioButton(label, MessyConduitSettings.style == s)) MessyConduitSettings.style = s;
                }
                else
                {
                    GUI.color = Color.gray;
                    l.Label("   " + label);
                    GUI.color = Color.white;
                }
            }
            l.GapLine();
            l.Label("Slack: " + (MessyConduitSettings.slack <= 0.01f ? "off (path-tight)" : MessyConduitSettings.slack.ToString("0.00") + "x the owner level"),
                    tooltip: "How much spare cord each cord carries. 1.00 = loops, figure-eights and heaps like a too-long extension cord.");
            MessyConduitSettings.slack = l.Slider(MessyConduitSettings.slack, 0f, 1.8f);
            l.Label("Sprawl cap: at most " + MessyConduitSettings.sprawlCap.ToString("0") + " cells of extra cord per cord");
            MessyConduitSettings.sprawlCap = l.Slider(MessyConduitSettings.sprawlCap, 2f, 40f);
            l.Label("Cords per connection: 1 to " + MessyConduitSettings.cordsPerConnection);
            MessyConduitSettings.cordsPerConnection = Mathf.RoundToInt(l.Slider(MessyConduitSettings.cordsPerConnection, 1f, 3f));
            l.CheckboxLabeled("Dense conduit fields become one tangle", ref MessyConduitSettings.tangles);
            l.CheckboxLabeled("Needless conduit stubs become pointless loops", ref MessyConduitSettings.needlessLoops);
            l.GapLine();
            l.CheckboxLabeled("Break readout: live ends spark, dead ends lie limp", ref MessyConduitSettings.breakReadout);
            l.Label("Spark intensity: " + MessyConduitSettings.sparkIntensity.ToString("0.0") + "x");
            MessyConduitSettings.sparkIntensity = l.Slider(MessyConduitSettings.sparkIntensity, 0f, 2f);
            l.CheckboxLabeled("Hide vanilla's thin machine hookup wires (power overlay lines always stay)", ref MessyConduitSettings.hideHookupWires);
            l.CheckboxLabeled("Debug: draw the node graph", ref MessyConduitSettings.debugDraw);
            l.GapLine();
            if (l.ButtonText("Reset to defaults")) MessyConduitSettings.ResetToDefaults();
            l.End();
        }

        public static string StyleLabel(CordStyle s)
        {
            switch (s)
            {
                case CordStyle.StarWarsJawa: return "Star Wars: Jawa (matte black, taped)";
                case CordStyle.ExtensionCord: return "Extension cord";
                case CordStyle.Cybertek: return "Cybertek";
                default: return "Star Wars";
            }
        }
    }
}
