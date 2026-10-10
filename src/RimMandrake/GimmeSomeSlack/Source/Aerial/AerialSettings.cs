using System;
using System.Collections.Generic;
using System.Reflection;
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
        /// <summary>GOS GS-5: when a pole changes owner, wires to the other owner's poles are coiled (a captured pole never fuses two grids).</summary>
        public static bool cutWiresOnOwnerChange = true;

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
            Scribe_Values.Look(ref cutWiresOnOwnerChange, "cutWiresOnOwnerChange", true);
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
            cutWiresOnOwnerChange = true;
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

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Overhead power lines", RimMandrake.Shared.SettingScope.Now, new[] { "enabled", "maxSpan", "sag", "autoLink", "maxStrands", "keepWiresOnGravship" }))
            {
            list.CheckboxLabeled("Aerial power lines (master switch)", ref enabled,
                "Masts, lamp masts and wall brackets carry power over open ground on sagging overhead wires. Off: they leave the " +
                "architect menu and wires are hidden. Anchors already built stay and keep carrying power, so no save breaks.");
            list.Label("Longest span: " + maxSpan.ToString("0") + " cells");
            maxSpan = Mathf.Round(list.Slider(maxSpan, 8f, 40f));
            list.Label("Sag: " + (sag * 100f).ToString("0") + "% of the span length");
            sag = list.Slider(sag, 0f, 0.15f);
            list.CheckboxLabeled("Link new anchors automatically to the nearest one in range", ref autoLink);
            list.Label("Wires per span: one per insulator, at most " + maxStrands);
            maxStrands = Mathf.RoundToInt(list.Slider(maxStrands, 1f, 3f));
            list.CheckboxLabeled("Wires strung between two anchors on a gravship stay up through the flight", ref keepWiresOnGravship,
                "On: a wire with both anchors aboard lands still strung and still carrying power; a wire to an anchor left on the ground " +
                "is taken down and coiled at launch, with a message. Off: every wire on the ship is taken down and coiled at launch.");
                list.GapLine();
            }

            if (Group(list, "Wire sway", RimMandrake.Shared.SettingScope.Now, new[] { "sway", "swayStrength" }))
            {
            list.Label("Wire sway in the wind (also obeys the game's own plant sway preference)");
            foreach (WireSwayMode m in Enum.GetValues(typeof(WireSwayMode)))
                if (list.RadioButton(m == WireSwayMode.Auto ? "Auto" : m == WireSwayMode.CPU ? "Always (CPU)" : "Off", sway == m))
                    sway = m;
            list.Label("Sway strength: " + swayStrength.ToString("0.0") + "x");
            swayStrength = list.Slider(swayStrength, 0f, 2f);
                list.GapLine();
            }

            if (Group(list, "Damage, shock and alerts", RimMandrake.Shared.SettingScope.Now, new[] { "explosionsCut", "kineticSway", "fallenWireShock", "fallenWireKnockback", "fallenWireIgnites", "wireDownAlert", "cutWiresOnOwnerChange" }))
            {
            list.CheckboxLabeled("Explosions cut wires (the halves hang and spark)", ref explosionsCut);
            list.CheckboxLabeled("Kinetic blasts (Kinetic Arms push waves) swing wires instead of cutting them", ref kineticSway,
                "A push wave never cuts a wire. Off: the wires ignore it.");
            list.CheckboxLabeled("Live fallen wires shock whoever touches them", ref fallenWireShock,
                "Anyone, colonists included, who touches a live wire lying on the ground is thrown back and knocked out for a couple " +
                "of hours. Only a weak heart (artery blockage, a heart attack, or a damaged heart) is killed. A dead wire is harmless. " +
                "Applies now.");
            list.Label("Shock throws the victim back: " + fallenWireKnockback + " cell(s)");
            fallenWireKnockback = Mathf.RoundToInt(list.Slider(fallenWireKnockback, 0f, 3f));
            list.CheckboxLabeled("Live fallen wires light spilled fuel", ref fallenWireIgnites,
                "A live end lying in spilled chemfuel, or in a burnable Flow Works liquid when that mod is loaded, can set it alight. " +
                "Applies now.");
            list.CheckboxLabeled("Alert when a wire is cut or lying on the ground", ref wireDownAlert,
                "An alert lists each anchor with a cut or fallen wire; clicking it jumps to the anchor, where Re-string cut wires lives. " +
                "Applies now.");
            list.CheckboxLabeled("Claiming a pole cuts wires to the other owner", ref cutWiresOnOwnerChange,
                "When a pole changes hands, its wires to poles of a different owner are coiled, so capturing one enemy pole never fuses your grid with theirs. " +
                "Power-tap clamps are the one way to draw from another grid. Applies now.");
                list.GapLine();
            }

            if (Group(list, "Power-tap clamps", RimMandrake.Shared.SettingScope.Now, new[] { "tapsEnabled", "tapRate", "tapEvents" }))
            {
            list.CheckboxLabeled("Allow power-tap clamps on other factions' grids", ref tapsEnabled,
                "A clamp bitten onto someone else's conduit quietly drains their grid into yours, one way: the grids never merge.");
            list.Label("Tap rate: " + tapRate.ToString("0") + " W");
            tapRate = Mathf.Round(list.Slider(tapRate, 50f, 2000f) / 50f) * 50f;
            list.CheckboxLabeled("Report taps to consequence systems (event hook only; no alerts or raids exist yet)", ref tapEvents);
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
            foreach (FieldInfo f in typeof(AerialSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int) || f.FieldType == typeof(string) || f.FieldType.IsEnum)
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(AerialSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): every Aerial setting is read live by a tick, placement, link, damage or launch handler (Apply() redraws on window close), none at world or map generation, so all are [now].</summary>
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

        public override void DoSettingsWindowContents(Rect inRect) => Settings.DoWindowContents(inRect);
    }
}
