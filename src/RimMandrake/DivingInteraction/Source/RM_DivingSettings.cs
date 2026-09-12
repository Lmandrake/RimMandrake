using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // SCALD_DIVING_MOD_1 — Mod Settings.
    // Precedent: src/RimStarWars/Shokk/Source/RSW_ShokkSettings.cs.
    //
    // Every default here is the SHIPPED behavior described in About.xml —
    // MOD_OPTIONS_RETROFIT_1 doctrine (CLAUDE.md "Every mod ships superb
    // Mod Settings"): defaults = shipped, all-off degrades gracefully
    // (masterEnabled false removes both float menu options entirely).
    // ════════════════════════════════════════════════════════════════════
    public class RM_DivingSettings : ModSettings
    {
        public static bool masterEnabled = true;
        public static bool huntEnabled = true;
        public static bool communeEnabled = true;

        // The actual "priced in burns" dial: this is how many ticks the
        // pawn stands on the burnDamage terrain, which is the ONLY thing
        // that costs them anything — no parallel damage system exists here.
        public static int diveDurationTicks = 2500;      // ~ 1 in-game hour
        public static int diveCooldownTicks = 30000;      // ~ half a day, per cell

        public static float huntSuccessChance = 0.65f;
        public static float huntLashbackChance = 0.15f;   // rolled only on a failed hunt
        public static int huntYieldMin = 1;
        public static int huntYieldMax = 3;

        public static float communeMoodOffset = 6f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref huntEnabled, "huntEnabled", true);
            Scribe_Values.Look(ref communeEnabled, "communeEnabled", true);
            Scribe_Values.Look(ref diveDurationTicks, "diveDurationTicks", 2500);
            Scribe_Values.Look(ref diveCooldownTicks, "diveCooldownTicks", 30000);
            Scribe_Values.Look(ref huntSuccessChance, "huntSuccessChance", 0.65f);
            Scribe_Values.Look(ref huntLashbackChance, "huntLashbackChance", 0.15f);
            Scribe_Values.Look(ref huntYieldMin, "huntYieldMin", 1);
            Scribe_Values.Look(ref huntYieldMax, "huntYieldMax", 3);
            Scribe_Values.Look(ref communeMoodOffset, "communeMoodOffset", 6f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Diving enabled", ref masterEnabled,
                "Master switch. Off: no dive options appear anywhere, on any terrain, in any "
              + "biome — the mod is fully inert.");

            if (masterEnabled)
            {
                list.Gap();
                list.CheckboxLabeled("Hunt enabled", ref huntEnabled,
                    "Colonists can dive to hunt whatever the deep holds. May return meat/materials, "
                  + "may return nothing, may return a burn.");
                list.CheckboxLabeled("Commune enabled", ref communeEnabled,
                    "Colonists can dive to sit with the deep rather than take from it. Always "
                  + "resolves peacefully; grants a mood thought.");

                list.Gap();
                list.Label("Dive duration: " + diveDurationTicks + " ticks ("
                    + (diveDurationTicks / 2500f).ToString("0.0") + " in-game hours)"
                    + " — this is the actual cost dial: it is how long the pawn stands on the "
                    + "burning terrain, and the terrain's own burn tick does the rest.");
                diveDurationTicks = (int)list.Slider(diveDurationTicks, 500, 10000);

                list.Label("Cooldown per dive cell: " + diveCooldownTicks + " ticks ("
                    + (diveCooldownTicks / 60000f).ToString("0.00") + " days)");
                diveCooldownTicks = (int)list.Slider(diveCooldownTicks, 2500, 120000);

                if (huntEnabled)
                {
                    list.Gap();
                    list.Label("Hunt success chance: " + huntSuccessChance.ToString("0%"));
                    huntSuccessChance = list.Slider(huntSuccessChance, 0f, 1f);

                    list.Label("Lashback chance on a failed hunt: " + huntLashbackChance.ToString("0%")
                        + " (a burn hit on top of the standing terrain cost)");
                    huntLashbackChance = list.Slider(huntLashbackChance, 0f, 1f);

                    list.Label("Hunt yield, minimum: " + huntYieldMin + " chitin per success");
                    huntYieldMin = (int)list.Slider(huntYieldMin, 1, 8);
                    list.Label("Hunt yield, maximum: " + huntYieldMax + " chitin per success");
                    huntYieldMax = Mathf.Max(huntYieldMin, (int)list.Slider(huntYieldMax, 1, 8));
                }

                if (communeEnabled)
                {
                    list.Gap();
                    list.Label("Commune mood offset: +" + communeMoodOffset.ToString("0.0"));
                    communeMoodOffset = list.Slider(communeMoodOffset, 0f, 20f);
                }
            }

            list.End();
        }
    }

    public class RM_DivingInteractionMod : Mod
    {
        public static RM_DivingSettings settings;

        public RM_DivingInteractionMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_DivingSettings>();
        }

        public override string SettingsCategory()
        {
            return "Deep Diving";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
