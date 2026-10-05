using System;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>Wire sway (design 2.5): Auto = CPU until the CutoutPlant shader path is proven (not built).</summary>
    public enum WireSwayMode { Auto, CPU, Off }

    /// <summary>
    /// Aerial power lines settings (design 2.9). Kept in their own ModSettings (a second Mod class in this
    /// assembly, its own entry in the Mod Settings list) so the floor-cord settings file is untouched.
    /// Static fields so jawa/mod_settings_field and AerialProbe "set:" can read and write them.
    /// Defaults = shipped behaviour.
    /// </summary>
    public class AerialSettings : ModSettings
    {
        /// <summary>Master switch. Off: anchors leave the architect menu and spans are hidden. Placed anchors stay
        /// (they are real buildings in the save) and their links keep carrying power, so a save is never broken.</summary>
        public static bool enabled = true;
        /// <summary>Longest span, cells (design guess 20; a playtest number).</summary>
        public static float maxSpan = 20f;
        /// <summary>Sag as a fraction of span length.</summary>
        public static float sag = 0.06f;
        /// <summary>A newly built anchor links to the nearest anchor in range with a free slot.</summary>
        public static bool autoLink = true;
        /// <summary>Strands per span: 1 to this, seeded per span.</summary>
        public static int maxStrands = 3;
        public static WireSwayMode sway = WireSwayMode.Auto;
        public static float swayStrength = 1f;
        /// <summary>An explosion whose radius reaches a span's ground line cuts it.</summary>
        public static bool explosionsCut = true;
        /// <summary>The one-way power tap clamp (owner 2026-10-02: build it now).</summary>
        public static bool tapsEnabled = true;
        /// <summary>Most a tap takes from the victim grid, watts.</summary>
        public static float tapRate = 500f;
        /// <summary>Raise TapEvents.Drained for consequence systems (none built yet: alerts/raids are a later design).</summary>
        public static bool tapEvents = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref maxSpan, "maxSpan", 20f);
            Scribe_Values.Look(ref sag, "sag", 0.06f);
            Scribe_Values.Look(ref autoLink, "autoLink", true);
            Scribe_Values.Look(ref maxStrands, "maxStrands", 3);
            Scribe_Values.Look(ref sway, "sway", WireSwayMode.Auto);
            Scribe_Values.Look(ref swayStrength, "swayStrength", 1f);
            Scribe_Values.Look(ref explosionsCut, "explosionsCut", true);
            Scribe_Values.Look(ref tapsEnabled, "tapsEnabled", true);
            Scribe_Values.Look(ref tapRate, "tapRate", 500f);
            Scribe_Values.Look(ref tapEvents, "tapEvents", true);
        }

        public static void ResetToDefaults()
        {
            enabled = true;
            maxSpan = 20f;
            sag = 0.06f;
            autoLink = true;
            maxStrands = 3;
            sway = WireSwayMode.Auto;
            swayStrength = 1f;
            explosionsCut = true;
            tapsEnabled = true;
            tapRate = 500f;
            tapEvents = true;
        }

        public static float Range => Mathf.Clamp(maxSpan, 4f, 40f);

        /// <summary>Make a change take effect: drop cached span meshes, redraw the ground layer.</summary>
        public static void Apply()
        {
            if (Current.ProgramState != ProgramState.Playing || Find.Maps == null) return;
            foreach (Map map in Find.Maps)
            {
                RM_MapComponent_Aerial c = map.GetComponent<RM_MapComponent_Aerial>();
                if (c == null) continue;
                c.Notify_SettingsChanged();
            }
        }
    }

    public class AerialLinesMod : Mod
    {
        public static AerialSettings Settings;

        // Harmony: GimmeSomeSlackMod's PatchAll(assembly) already applies every [HarmonyPatch] in this assembly,
        // the aerial ones included. Patching again here would double every patch.
        public AerialLinesMod(ModContentPack content) : base(content)
        {
            LegacyMigration.SettingsFiles(content);
            Settings = GetSettings<AerialSettings>();
        }

        /// <summary>B27: empty, so RimWorld lists no separate entry; drawn as a tab of GimmeSomeSlackMod's one window.</summary>
        public override string SettingsCategory() => "";

        public override void WriteSettings()
        {
            base.WriteSettings();
            AerialSettings.Apply();
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            var l = new Listing_Standard();
            l.Begin(inRect);
            l.CheckboxLabeled("Aerial power lines (master switch)", ref AerialSettings.enabled,
                "Masts, lamp masts and wall brackets carry power over open ground on sagging overhead wires. Off: they leave the " +
                "architect menu and wires are hidden. Anchors already built stay and keep carrying power, so no save breaks.");
            l.Label("Longest span: " + AerialSettings.maxSpan.ToString("0") + " cells");
            AerialSettings.maxSpan = Mathf.Round(l.Slider(AerialSettings.maxSpan, 8f, 40f));
            l.Label("Sag: " + (AerialSettings.sag * 100f).ToString("0") + "% of the span length");
            AerialSettings.sag = l.Slider(AerialSettings.sag, 0f, 0.15f);
            l.CheckboxLabeled("Link new anchors automatically to the nearest one in range", ref AerialSettings.autoLink);
            l.Label("Wires per span: one per insulator, at most " + AerialSettings.maxStrands);
            AerialSettings.maxStrands = Mathf.RoundToInt(l.Slider(AerialSettings.maxStrands, 1f, 3f));
            l.GapLine();
            l.Label("Wire sway in the wind (also obeys the game's own plant sway preference)");
            foreach (WireSwayMode m in Enum.GetValues(typeof(WireSwayMode)))
                if (l.RadioButton(m == WireSwayMode.Auto ? "Auto" : m == WireSwayMode.CPU ? "Always (CPU)" : "Off", AerialSettings.sway == m))
                    AerialSettings.sway = m;
            l.Label("Sway strength: " + AerialSettings.swayStrength.ToString("0.0") + "x");
            AerialSettings.swayStrength = l.Slider(AerialSettings.swayStrength, 0f, 2f);
            l.CheckboxLabeled("Explosions cut wires (the halves hang and spark)", ref AerialSettings.explosionsCut);
            l.GapLine();
            l.CheckboxLabeled("Allow power-tap clamps on other factions' grids", ref AerialSettings.tapsEnabled,
                "A clamp bitten onto someone else's conduit quietly drains their grid into yours, one way: the grids never merge.");
            l.Label("Tap rate: " + AerialSettings.tapRate.ToString("0") + " W");
            AerialSettings.tapRate = Mathf.Round(l.Slider(AerialSettings.tapRate, 50f, 2000f) / 50f) * 50f;
            l.CheckboxLabeled("Report taps to consequence systems (event hook only; no alerts or raids exist yet)", ref AerialSettings.tapEvents);
            l.GapLine();
            if (l.ButtonText("Reset to defaults")) AerialSettings.ResetToDefaults();
            l.End();
        }
    }
}
