using UnityEngine;
using Verse;

namespace RimMandrake.Oracle
{
    public class OracleSettings : ModSettings
    {
        public bool enabled = false;
        public string baseUrl = "https://api.openai.com/v1";
        public string model = "gpt-4o-mini";
        public string apiKey = "";
        public int timeoutSeconds = 15;
        public int godsBudgetPerDay = 3;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", false);
            Scribe_Values.Look(ref baseUrl, "baseUrl", "https://api.openai.com/v1");
            Scribe_Values.Look(ref model, "model", "gpt-4o-mini");
            Scribe_Values.Look(ref apiKey, "apiKey", "");
            Scribe_Values.Look(ref timeoutSeconds, "timeoutSeconds", 15);
            Scribe_Values.Look(ref godsBudgetPerDay, "godsBudgetPerDay", 3);
        }

        public void DoSettingsWindowContents(Rect inRect)
        {
            Listing_Standard listing = new Listing_Standard();
            listing.Begin(inRect);

            listing.CheckboxLabeled("Oracle enabled (kill switch)", ref enabled,
                "Off: every consumer always ships its prescribed fallback text, no network call is ever made.");
            listing.Gap();

            listing.Label("Base URL (OpenAI-compatible /chat/completions root)");
            baseUrl = listing.TextEntry(baseUrl);
            listing.Label("Model");
            model = listing.TextEntry(model);
            listing.Label("API key (blank = every call falls back silently)");
            apiKey = listing.TextEntry(apiKey);

            listing.Gap();
            listing.Label("Timeout (seconds): " + timeoutSeconds);
            timeoutSeconds = System.Math.Max(1, (int)listing.Slider(timeoutSeconds, 1, 60));
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
