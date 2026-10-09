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
        /// <summary>A kinetic blast (Kinetic Arms' push wave) swings the spans it reaches; it never cuts them (owner Q3).</summary>
        public static bool kineticSway = true;
        /// <summary>The one-way power tap clamp (owner 2026-10-02: build it now).</summary>
        public static bool tapsEnabled = true;
        /// <summary>Most a tap takes from the victim grid, watts.</summary>
        public static float tapRate = 500f;
        /// <summary>Raise TapEvents.Drained for consequence systems (none built yet: alerts/raids are a later design).</summary>
        public static bool tapEvents = true;
        /// <summary>GS-1: a span with both anchors aboard a launching gravship lands still strung.</summary>
        public static bool keepWiresOnGravship = true;
        /// <summary>FALLEN_WIRE_SHOCK_1: a live fallen wire knocks out whoever touches it, colonists included; lethal
        /// only to a weak heart (RM_FallenWireShock).</summary>
        public static bool fallenWireShock = true;
        /// <summary>FALLEN_WIRE_SHOCK_1 (X-7): a live end lying in spilled fuel can light it.</summary>
        public static bool fallenWireIgnites = true;
        /// <summary>Cells a shock throws a pawn back, 0-3. PROVISIONAL.</summary>
        public static int fallenWireKnockback = 2;
        /// <summary>WIRE_DOWN_ALERT_1: an Alert lists anchors with a cut or fallen wire, click to jump to it.</summary>
        public static bool wireDownAlert = true;

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
            Scribe_Values.Look(ref kineticSway, "kineticSway", true);
            Scribe_Values.Look(ref tapsEnabled, "tapsEnabled", true);
            Scribe_Values.Look(ref tapRate, "tapRate", 500f);
            Scribe_Values.Look(ref tapEvents, "tapEvents", true);
            Scribe_Values.Look(ref keepWiresOnGravship, "keepWiresOnGravship", true);
            Scribe_Values.Look(ref fallenWireShock, "fallenWireShock", true);
            Scribe_Values.Look(ref fallenWireIgnites, "fallenWireIgnites", true);
            Scribe_Values.Look(ref fallenWireKnockback, "fallenWireKnockback", 2);
            Scribe_Values.Look(ref wireDownAlert, "wireDownAlert", true);
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
            kineticSway = true;
            tapsEnabled = true;
            tapRate = 500f;
            tapEvents = true;
            keepWiresOnGravship = true;
            fallenWireShock = true;
            fallenWireIgnites = true;
            fallenWireKnockback = 2;
            wireDownAlert = true;
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

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1200f;

        public override void DoSettingsWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            var l = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            l.Begin(settingsView);
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
            l.CheckboxLabeled("Wires strung between two anchors on a gravship stay up through the flight", ref AerialSettings.keepWiresOnGravship,
                "On: a wire with both anchors aboard lands still strung and still carrying power; a wire to an anchor left on the ground " +
                "is taken down and coiled at launch, with a message. Off: every wire on the ship is taken down and coiled at launch.");
            l.CheckboxLabeled("Explosions cut wires (the halves hang and spark)", ref AerialSettings.explosionsCut);
            l.CheckboxLabeled("Kinetic blasts (Kinetic Arms push waves) swing wires instead of cutting them", ref AerialSettings.kineticSway,
                "A push wave never cuts a wire. Off: the wires ignore it.");
            l.CheckboxLabeled("Live fallen wires shock whoever touches them", ref AerialSettings.fallenWireShock,
                "Anyone, colonists included, who touches a live wire lying on the ground is thrown back and knocked out for a couple " +
                "of hours. Only a weak heart (artery blockage, a heart attack, or a damaged heart) is killed. A dead wire is harmless. " +
                "Applies now.");
            l.Label("Shock throws the victim back: " + AerialSettings.fallenWireKnockback + " cell(s)");
            AerialSettings.fallenWireKnockback = Mathf.RoundToInt(l.Slider(AerialSettings.fallenWireKnockback, 0f, 3f));
            l.CheckboxLabeled("Live fallen wires light spilled fuel", ref AerialSettings.fallenWireIgnites,
                "A live end lying in spilled chemfuel, or in a burnable Flow Works liquid when that mod is loaded, can set it alight. " +
                "Applies now.");
            l.CheckboxLabeled("Alert when a wire is cut or lying on the ground", ref AerialSettings.wireDownAlert,
                "An alert lists each anchor with a cut or fallen wire; clicking it jumps to the anchor, where Re-string cut wires lives. " +
                "Applies now.");
            l.GapLine();
            l.CheckboxLabeled("Allow power-tap clamps on other factions' grids", ref AerialSettings.tapsEnabled,
                "A clamp bitten onto someone else's conduit quietly drains their grid into yours, one way: the grids never merge.");
            l.Label("Tap rate: " + AerialSettings.tapRate.ToString("0") + " W");
            AerialSettings.tapRate = Mathf.Round(l.Slider(AerialSettings.tapRate, 50f, 2000f) / 50f) * 50f;
            l.CheckboxLabeled("Report taps to consequence systems (event hook only; no alerts or raids exist yet)", ref AerialSettings.tapEvents);
            l.GapLine();
            if (l.ButtonText("Reset to defaults")) AerialSettings.ResetToDefaults();
            settingsViewHeight = Mathf.Max(l.CurHeight + 20f, inRect.height);
            l.End();
            Widgets.EndScrollView();
        }
    }
}
