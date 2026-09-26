using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pyrelands
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Pyrelands.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData, a
    // DoWindowContents helper called from the Mod subclass).
    //
    // Five things this gates, each read straight out of FireEcologyHook.cs's
    // own hardcoded numbers (defaults below = shipped behavior, unchanged):
    //   1. Fulgurite left by a lightning strike on sand-family ground.
    //   2. Loose ash dusting off a burning cell.
    //   3. Scorch-fruit seeded by a burning cell, plus its per-map cap.
    //   4. Ash accumulation (drifts) during Ash Fall / Cinderfall weather.
    //   5. Whether the Pyrelands biome can win tile placement at all —
    //      WORLDGEN-AFFECTING, a new-worlds-only switch.
    // ════════════════════════════════════════════════════════════════════
    public class RM_PyrelandsSettings : ModSettings
    {
        public static bool fulguriteEnabled = true;
        public static float fulguriteChance = 0.35f;

        public static bool ashDustingEnabled = true;
        public static float ashDustingChance = 0.02f;

        public static bool scorchFruitEnabled = true;
        // Per-burned-cell probability (one roll per Fire instance), NOT
        // per-tick. Owner 2026-09-16: "perhaps one in twenty squares".
        public static float scorchFruitChance = 0.05f;
        public static int scorchFruitMapCap = 40;

        public static bool ashfallAccumulationEnabled = true;
        public static float ashfallRateMultiplier = 1f;

        public static bool biomeGenerationEnabled = true;

        // PYRELANDS_FLORA_LEAK_1 — a Harmony postfix on WildPlantSpawner strips
        // any wild-plant candidate off the RM_FE_ grass allowlist on a
        // Pyrelands map, however it reached the candidate list (a foreign
        // mod's plant.wildBiomes entry, a tile mutator's AdditionalWildPlants,
        // or a mixed-biome secondary biome sharing the map). Off: Pyrelands
        // reverts to trusting its own biome-level <wildPlants> list alone,
        // which measurably does not hold on a heavily biome-modded list.
        public static bool wildPlantAllowlistEnabled = true;

        public static bool plantGrowthStagesEnabled = true;

        // PYRELANDS_SCORCHED_RUINS_1: GenStep_ScorchPyrelandsRuins (FireEcologyHook.cs)
        // reads this at mapgen time, per new map — flip it and the NEXT map generated
        // honors it immediately, no restart needed (a map already on disk is untouched).
        public static bool scorchedRuinsEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref fulguriteEnabled, "fulguriteEnabled", true);
            Scribe_Values.Look(ref fulguriteChance, "fulguriteChance", 0.35f);
            Scribe_Values.Look(ref ashDustingEnabled, "ashDustingEnabled", true);
            Scribe_Values.Look(ref ashDustingChance, "ashDustingChance", 0.02f);
            Scribe_Values.Look(ref scorchFruitEnabled, "scorchFruitEnabled", true);
            // Key renamed with the semantics change (per-tick -> per-cell,
            // 2026-09-16): a settings file saved under the old key holds a
            // per-tick number that would read as ~1-in-400 cells; ignoring
            // the old key gives everyone the new 0.05 default instead.
            Scribe_Values.Look(ref scorchFruitChance, "scorchFruitChancePerCell", 0.05f);
            Scribe_Values.Look(ref scorchFruitMapCap, "scorchFruitMapCap", 40);
            Scribe_Values.Look(ref ashfallAccumulationEnabled, "ashfallAccumulationEnabled", true);
            Scribe_Values.Look(ref ashfallRateMultiplier, "ashfallRateMultiplier", 1f);
            Scribe_Values.Look(ref biomeGenerationEnabled, "biomeGenerationEnabled", true);
            Scribe_Values.Look(ref wildPlantAllowlistEnabled, "wildPlantAllowlistEnabled", true);
            Scribe_Values.Look(ref plantGrowthStagesEnabled, "plantGrowthStagesEnabled", true);
            Scribe_Values.Look(ref scorchedRuinsEnabled, "scorchedRuinsEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Fulgurite");
            list.CheckboxLabeled("Lightning leaves fulgurite", ref fulguriteEnabled,
                "A strike on sand-family ground has a chance to leave a fulgurite behind. "
              + "Off: lightning strikes normally, nothing spawns.");
            if (fulguriteEnabled)
            {
                list.Label("Chance per strike: " + fulguriteChance.ToString("0%"));
                fulguriteChance = list.Slider(fulguriteChance, 0f, 1f);
            }
            list.GapLine();

            list.Label("Loose ash");
            list.CheckboxLabeled("Fire dusts loose ash", ref ashDustingEnabled,
                "A burning cell on scorchable ground has a small chance, per tick batch, to "
              + "drop loose ash filth. Off: fire still burns, no extra ash from this. Rides "
              + "alongside vanilla's own unconditional scorch mark — that is unaffected either way.");
            if (ashDustingEnabled)
            {
                list.Label("Rate: " + (ashDustingChance / 0.02f).ToString("0.00") + "x default");
                ashDustingChance = list.Slider(ashDustingChance, 0.02f * 0.25f, 0.02f * 3f);
            }
            list.Gap();

            list.CheckboxLabeled("Fire seeds scorch-fruit", ref scorchFruitEnabled,
                "A burning cell on scorchable ground rarely seeds a scorch-fruit pod nearby. "
              + "Off: no scorch-fruit ever appears this way.");
            if (scorchFruitEnabled)
            {
                list.Label("Chance per burned cell: 1 in " + (1f / scorchFruitChance).ToString("0") + " (default 1 in 20)");
                scorchFruitChance = list.Slider(scorchFruitChance, 0.0125f, 0.15f);
                list.Label("Per-map cap: " + scorchFruitMapCap + " (stops seeding once a map holds this many)");
                scorchFruitMapCap = (int)list.Slider(scorchFruitMapCap, 10f, 100f);
            }
            list.GapLine();

            list.Label("Ash accumulation (Ash Fall / Cinderfall weather)");
            list.CheckboxLabeled("Weather deposits ash drifts", ref ashfallAccumulationEnabled,
                "Ash Fall and Cinderfall weather bank loose ash across the map over time. "
              + "Off: the weather still occurs (darkened sky, lightning on Cinderfall), it just "
              + "leaves no ash behind.");
            if (ashfallAccumulationEnabled)
            {
                list.Label("Accumulation rate: " + ashfallRateMultiplier.ToString("0.00") + "x");
                ashfallRateMultiplier = list.Slider(ashfallRateMultiplier, 0.25f, 3f);
            }
            list.GapLine();

            list.Label("Plant art");
            list.CheckboxLabeled("Grass shows its growth stage", ref plantGrowthStagesEnabled,
                "Quickgrass is drawn as a sprout, then half-grown, then tall lush grass as it "
              + "regrows after a fire. Off: it is always drawn with its full-grown art (it still "
              + "grows and still starts small — only the artwork stops changing).");
            list.GapLine();

            list.Label("Scorched ruins");
            list.CheckboxLabeled("Ruins generate scorched and burned", ref scorchedRuinsEnabled,
                "Ancient ruins (and mutator-placed ancient structures) on a Pyrelands map get "
              + "ash terrain and soot filth laid over their footprint as the map is made. "
              + "Off: ruins generate with plain ground, same as any other biome. Map-generation-"
              + "affecting — only the NEXT map generated is affected; an existing map is untouched.");
            list.GapLine();

            list.Label("Wild flora enforcement");
            list.CheckboxLabeled("Only RM_FE grasses grow wild on Pyrelands", ref wildPlantAllowlistEnabled,
                "Strips any wild-plant candidate outside the two RM_FE_ grasses on a Pyrelands map, "
              + "however it got there (a foreign mod's own biome list leaking in via a mixed-biome "
              + "or tile-mutator mechanism). Off: Pyrelands trusts its own biome definition alone, "
              + "which other biome-blending mods can bypass.");
            list.GapLine();

            list.Label("Biome placement (WORLDGEN-AFFECTING — new worlds only)");
            list.CheckboxLabeled("Pyrelands can generate on new worlds", ref biomeGenerationEnabled,
                "Off: the Pyrelands biome never wins tile placement when generating a NEW world. "
              + "A world already generated, and any Pyrelands tiles already on it, are unaffected — "
              + "this never retroactively changes an existing planet.");

            list.End();
        }
    }

    public class RM_PyrelandsMod : Mod
    {
        public static RM_PyrelandsSettings settings;

        public RM_PyrelandsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_PyrelandsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Pyrelands";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
