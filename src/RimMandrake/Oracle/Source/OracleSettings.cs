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

        public void DoSettingsWindowContents(Rect inRect)
        {
            Listing_Standard listing = new Listing_Standard();
            listing.Begin(inRect);

            listing.CheckboxLabeled("Oracle enabled (kill switch)", ref enabled,
                "Off: every consumer always ships its prescribed fallback text, and no claude process is ever launched.");
            listing.Gap();

            listing.Label("Requires the Claude Code CLI installed and logged in on this machine. "
                        + "Without it every call fails and the prescribed fallback text ships instead.");
            listing.Gap();

            listing.Label("Path to the claude executable (blank = find it on PATH)");
            claudeCliPath = listing.TextEntry(claudeCliPath);

            listing.Gap();
            listing.Label("Timeout (seconds): " + timeoutSeconds);
            timeoutSeconds = System.Math.Max(5, (int)listing.Slider(timeoutSeconds, 5, 180));
            listing.Label("Gods budget per in-game day: " + godsBudgetPerDay);
            godsBudgetPerDay = (int)listing.Slider(godsBudgetPerDay, 0, 20);

            listing.End();
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
            Settings.DoSettingsWindowContents(inRect);
        }
    }
}
