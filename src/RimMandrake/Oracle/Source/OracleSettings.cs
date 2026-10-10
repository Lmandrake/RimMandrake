using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Oracle
{
    /// <summary>
    /// Owner ruling 2026-09-05: the transport is the Claude Code CLI, so there
    /// is no base URL, no model string and no API key here any more. What the
    /// subprocess path actually needs is a way to say where the binary is, for
    /// the case where the game process's PATH does not carry it. Old saved
    /// values for the dropped fields are simply ignored by Scribe.
    /// </summary>
    public class OracleSettings : ModSettings
    {
        public bool enabled = false;

        /// <summary>
        /// Blank = find it on PATH (then the CLI installer's default location).
        /// A full path to claude.exe if it lives somewhere else.
        /// </summary>
        public string claudeCliPath = "";

        /// <summary>
        /// The CLI is a Node process that has to start, authenticate and answer,
        /// so its floor is seconds, not milliseconds -- the old 15s HTTP default
        /// would have timed out perfectly good calls.
        /// </summary>
        public int timeoutSeconds = 60;

        public int godsBudgetPerDay = 3;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", false);
            Scribe_Values.Look(ref claudeCliPath, "claudeCliPath", "");
            Scribe_Values.Look(ref timeoutSeconds, "timeoutSeconds", 60);
            Scribe_Values.Look(ref godsBudgetPerDay, "godsBudgetPerDay", 3);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public instance bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();  // instance settings: read from a fresh instance

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            var fresh = new OracleSettings();
            foreach (FieldInfo f in typeof(OracleSettings).GetFields(BindingFlags.Public | BindingFlags.Instance))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int) || f.FieldType == typeof(string))
                    d[f.Name] = f.GetValue(fresh);
            return d;
        }

        public void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(OracleSettings).GetField(n, BindingFlags.Public | BindingFlags.Instance);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(this, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
        private bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
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
                ? " changes take effect the next time the game starts or a save loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 400f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            // Scopes audited per read site (OracleGameComponent): every setting is read when the next Oracle request is made.
            if (Group(list, "Oracle kill switch", RimMandrake.Shared.SettingScope.Now, new[] { "enabled" }))
            {
                list.CheckboxLabeled("Oracle enabled (kill switch)", ref enabled,
                    "Off: every consumer always ships its prescribed fallback text, and no claude process is ever launched.");
                list.Label("Requires the Claude Code CLI installed and logged in on this machine. "
                         + "Without it every call fails and the prescribed fallback text ships instead.");
                list.GapLine();
            }

            if (Group(list, "Claude CLI and timeout", RimMandrake.Shared.SettingScope.Now, new[] { "claudeCliPath", "timeoutSeconds" }))
            {
                list.Label("Path to the claude executable (blank = find it on PATH)");
                claudeCliPath = list.TextEntry(claudeCliPath);
                list.Label("Timeout (seconds): " + timeoutSeconds);
                timeoutSeconds = System.Math.Max(5, (int)list.Slider(timeoutSeconds, 5, 180));
                list.GapLine();
            }

            if (Group(list, "Gods budget", RimMandrake.Shared.SettingScope.Now, new[] { "godsBudgetPerDay" }))
            {
                list.Label("Gods budget per in-game day: " + godsBudgetPerDay);
                godsBudgetPerDay = (int)list.Slider(godsBudgetPerDay, 0, 20);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class OracleMod : Mod
    {
        public static OracleSettings Settings;

        public OracleMod(ModContentPack content) : base(content)
        {
            Settings = GetSettings<OracleSettings>();
        }

        public override string SettingsCategory() => "RimMandrake: Oracle";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            Settings.DoWindowContents(inRect);
        }
    }
}
