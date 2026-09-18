using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.TrophyCraft
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Trophy Craft.
    // Precedent: src/RimStarWars/Shokk/Source/RSW_ShokkSettings.cs.
    //
    // One toggle (default ON, per the item's spec) plus one opinion
    // magnitude multiplier read by RSW_Thought_ObserverBraveFang.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_TrophyCraftSettings : ModSettings
    {
        public static bool socialConsequenceEnabled = true;
        public static float opinionMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref socialConsequenceEnabled, "socialConsequenceEnabled", true);
            Scribe_Values.Look(ref opinionMultiplier, "opinionMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Fang pendant social consequence enabled", ref socialConsequenceEnabled,
                "Observers whose faction is configured (the campaign's hunting tribes) form an "
              + "opinion of anyone wearing the wyyyschokk fang pendant. Off: the pendant is a "
              + "trade good and crafted item only, no social effect from anyone.");
            if (socialConsequenceEnabled)
            {
                list.Label("  Opinion magnitude: " + opinionMultiplier.ToString("0.00")
                    + "x (base +8 opinion)");
                opinionMultiplier = list.Slider(opinionMultiplier, 0f, 3f);
            }

            list.End();
        }
    }

    public class RSW_TrophyCraftMod : Mod
    {
        public static RSW_TrophyCraftSettings settings;

        public RSW_TrophyCraftMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_TrophyCraftSettings>();
        }

        public override string SettingsCategory()
        {
            return "Trophy Craft";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
