using UnityEngine;
using Verse;

namespace RimMandrake.Cauldron
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — MOD_OPTIONS_RETROFIT_1 doctrine: every mod ships a real
    // settings screen. No mechanics kit exists for this biome yet (thin
    // biome per biome_mod_architecture.md — def + terrain + plants + fauna
    // partition only, no mechanic to gate beyond worldgen insertion), so the
    // only control is the standard worldgen-rarity slider every sibling
    // biome mod ships.
    //
    // STATIC FIELD, read from the biome worker which runs during worldgen
    // with no Mod instance handy — same pattern as every sibling.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CauldronSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new
        // planet. 1 = the shipped default.
        public static float biomeRarityFactor = 1f;

        // CAULDRON_TREE_METAL_YIELD_1: the metal second yield on the thornwood
        // and martyr tree. Off = they yield wood only. Factor scales the count.
        public static bool metalYieldEnabled = true;
        public static float metalYieldFactor = 1f;

        // CAULDRON_MECHANICS_BUILD_1 part 2: the vent bloom's stacking metal
        // load on pawns outdoors + unroofed. Off = the bloom is weather only.
        public static bool ventBloomExposureEnabled = true;
        public static float ventBloomExposureFactor = 1f;

        // CAULDRON_MECHANICS_BUILD_1 part 5: vexxiss behaviours.
        public static bool vexxissFireWardenEnabled = true;
        public static bool vexxissAttacksIgniter = true;
        public static bool vexxissPoisonsWater = true;

        // CAULDRON_GPT_ENRICHMENT_1: assay grade inspect line (part 4), the
        // poisoned-water warning letter (part 2), nettles colonizing poisoned
        // shorelines (part 5).
        public static bool assayGradeEnabled = true;
        public static bool vexxissWaterLetter = true;
        public static bool condensateGardensEnabled = true;

        // CAULDRON_VENT_ENRICHMENT_HOOKS_1: the vents and what hangs on them.
        // ventsEnabled is WORLDGEN-affecting: it decides whether a newly made Cauldron map gets vents.
        public static bool ventsEnabled = true;
        public static bool ventWeatherEnabled = true;
        public static bool ventFalterMessage = true;
        public static bool ventLocalExposureEnabled = true;
        public static bool vexxissDrinksVentsEnabled = true;
        public static bool ventGardensEnabled = true;
        public static float ventSilenceDays = 4f;
        // CAULDRON_FLORA_EXPANSION_BUILD_1: the six admitted flora in the wild roster (applies on restart) and fexxil's venom.
        public static bool floraExpansionEnabled = true;
        public static bool fexxilVenomEnabled = true;
        // VEXXITH_CLOSED_LOOP_BUILD_1: vexxith (and the vexxith door) takes no acid damage; the door in the
        // architect menu (restart to apply).
        public static bool vexxithAcidImmunityEnabled = true;
        public static bool vexxithDoorEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref metalYieldEnabled, "metalYieldEnabled", true, true);
            Scribe_Values.Look(ref metalYieldFactor, "metalYieldFactor", 1f, true);
            Scribe_Values.Look(ref ventBloomExposureEnabled, "ventBloomExposureEnabled", true, true);
            Scribe_Values.Look(ref ventBloomExposureFactor, "ventBloomExposureFactor", 1f, true);
            Scribe_Values.Look(ref vexxissFireWardenEnabled, "vexxissFireWardenEnabled", true, true);
            Scribe_Values.Look(ref vexxissAttacksIgniter, "vexxissAttacksIgniter", true, true);
            Scribe_Values.Look(ref vexxissPoisonsWater, "vexxissPoisonsWater", true, true);
            Scribe_Values.Look(ref assayGradeEnabled, "assayGradeEnabled", true, true);
            Scribe_Values.Look(ref vexxissWaterLetter, "vexxissWaterLetter", true, true);
            Scribe_Values.Look(ref condensateGardensEnabled, "condensateGardensEnabled", true, true);
            Scribe_Values.Look(ref ventsEnabled, "ventsEnabled", true, true);
            Scribe_Values.Look(ref ventWeatherEnabled, "ventWeatherEnabled", true, true);
            Scribe_Values.Look(ref ventFalterMessage, "ventFalterMessage", true, true);
            Scribe_Values.Look(ref ventLocalExposureEnabled, "ventLocalExposureEnabled", true, true);
            Scribe_Values.Look(ref vexxissDrinksVentsEnabled, "vexxissDrinksVentsEnabled", true, true);
            Scribe_Values.Look(ref ventGardensEnabled, "ventGardensEnabled", true, true);
            Scribe_Values.Look(ref ventSilenceDays, "ventSilenceDays", 4f, true);
            Scribe_Values.Look(ref floraExpansionEnabled, "floraExpansionEnabled", true, true);
            Scribe_Values.Look(ref fexxilVenomEnabled, "fexxilVenomEnabled", true, true);
            Scribe_Values.Look(ref vexxithAcidImmunityEnabled, "vexxithAcidImmunityEnabled", true, true);
            Scribe_Values.Look(ref vexxithDoorEnabled, "vexxithDoorEnabled", true, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls (cfdba9344 pattern): ~30 rows overflow the settings window. View height = last measured
            // content height. maxOneColumn is load-bearing: lastContentHeight starts at 0, and without it the
            // overflow wraps into an off-screen second column and the view never grows past the window.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(lastContentHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPosition, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 the Cauldron never generates on a new planet. "
                       + "The default places a scattering of cold, permanently dim, "
                       + "toxin-laced forest patches. Affects planets generated "
                       + "afterwards, never one that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);

            list.GapLine();
            list.CheckboxLabeled("Metal-infused trees yield metal",
                ref metalYieldEnabled,
                "Twisting thornwood and martyr trees drop steel beside their wood, "
                + "more from older growth. Off: wood only. Takes effect on the next harvest.");
            if (metalYieldEnabled)
            {
                list.Label("Metal yield: " + metalYieldFactor.ToString("0.0") + "x (default 1.0x)");
                metalYieldFactor = list.Slider(metalYieldFactor, 0.1f, 3f);
                list.CheckboxLabeled("  ...and show an assay grade",
                    ref assayGradeEnabled,
                    "The inspect pane of a thornwood or martyr tree reads its grade (unripe, trace, fair, "
                    + "rich, lode) and roughly how much metal it would give if cut now.");
            }

            list.GapLine();
            list.CheckboxLabeled("Vent bloom builds a metal load",
                ref ventBloomExposureEnabled,
                "During a vent bloom, anyone outdoors under open sky slowly takes on a "
                + "metal-load condition. A roof or toxic-resistant gear keeps it off; native "
                + "animals are unaffected. Off: the bloom is weather only.");
            if (ventBloomExposureEnabled)
            {
                list.Label("Metal load build-up: " + ventBloomExposureFactor.ToString("0.0") + "x (default 1.0x)");
                ventBloomExposureFactor = list.Slider(ventBloomExposureFactor, 0.1f, 3f);
            }

            list.GapLine();
            list.CheckboxLabeled("Vexxiss puts out fires",
                ref vexxissFireWardenEnabled,
                "A vexxiss that notices a nearby fire walks to it and smothers it. Off: it ignores fire.");
            if (vexxissFireWardenEnabled)
            {
                list.CheckboxLabeled("  ...and attacks whoever started it",
                    ref vexxissAttacksIgniter,
                    "When the fire has a known starter still in reach, the vexxiss goes for them first. "
                    + "A tame vexxiss never attacks its own faction.");
            }
            list.CheckboxLabeled("Vexxiss poisons the water it wades through",
                ref vexxissPoisonsWater,
                "Water cells a vexxiss stands in, and the cells touching it, turn to toxic water. "
                + "Off: water is left alone.");
            if (vexxissPoisonsWater)
            {
                list.CheckboxLabeled("  ...and warn me when it does",
                    ref vexxissWaterLetter,
                    "A letter when a vexxiss starts turning water toxic on a map where you have colonists. "
                    + "At most one per animal per day.");
            }

            list.GapLine();
            list.CheckboxLabeled("Nettles colonize poisoned shorelines",
                ref condensateGardensEnabled,
                "Raven nettles grow up along the banks of toxic water: some when the map is made, more "
                + "over the following weeks wherever a shore turns toxic. Off: nettles grow only as ordinary "
                + "wild plants. Affects maps made afterwards for the first part; the spread applies at once.");

            list.GapLine();
            list.CheckboxLabeled("Ground vents (new maps only)",
                ref ventsEnabled,
                "WORLDGEN: a Cauldron map made from now on gets a handful of vents. Off: none, and every "
                + "vent feature below does nothing on that map. Maps already made are unchanged.");
            list.CheckboxLabeled("Vents follow the weather",
                ref ventWeatherEnabled,
                "A vent breathes harder in a vent bloom, softer in vapour bank and dewfall, and goes "
                + "hushed while a bloom is arriving.");
            list.CheckboxLabeled("  ...and warn me when the vents go quiet",
                ref ventFalterMessage,
                "A message when the vents hush ahead of a vent bloom.");
            list.CheckboxLabeled("Bloom exposure is strongest near vents",
                ref ventLocalExposureEnabled,
                "The bloom's metal load is full strength beside a live vent and fades to a tenth far from "
                + "every one. Off: it reaches everyone outdoors equally. Maps with no vents are unaffected.");
            list.CheckboxLabeled("Vexxiss drink from vents",
                ref vexxissDrinksVentsEnabled,
                "A wild vexxiss braces over a vent and inhales until it falls silent for days, then the vent "
                + "slowly recovers. Off: vexxiss ignore vents.");
            list.Label("Silence lasts: " + ventSilenceDays.ToString("0.0") + " days (default 4.0)");
            ventSilenceDays = list.Slider(ventSilenceDays, 1f, 10f);
            list.CheckboxLabeled("Flowers grow around vents",
                ref ventGardensEnabled,
                "Crystal flowers ring stable vents, blood bouquets mark chronic leaks, giant toxic flowers "
                + "favour vents that blew out recently. Needs nettle gardens above to be on.");
            list.CheckboxLabeled("Flora expansion (restart to apply)",
                ref floraExpansionEnabled,
                "Tsevrix, ixalith, fexxil, sessarix, kissaveth and selvix in the wild roster. Off: only the original "
                + "eleven plants grow. The roster change applies on the next launch.");
            list.CheckboxLabeled("Fexxil burrs carry venom (restart to apply)",
                ref fexxilVenomEnabled,
                "Walking through fexxil gives a toxic scratch. Off: the thicket only slows you down.");

            list.GapLine();
            list.CheckboxLabeled("Vexxith is acid-proof",
                ref vexxithAcidImmunityEnabled,
                "Anything made of vexxith plate, and the acid-proof door, takes no acid damage. Off: acid burns "
                + "vexxith like anything else. A pawn in vexxith armour is still burned; the armour is not.");
            list.CheckboxLabeled("Acid-proof vexxith door (restart to apply)",
                ref vexxithDoorEnabled,
                "A door that can only be built from vexxith plate. Off: it leaves the architect menu on the next "
                + "launch; doors already built stay.");

            lastContentHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }

        private Vector2 scrollPosition;
        private float lastContentHeight;

        private static string RarityLabel()
        {
            if (biomeRarityFactor <= 0.001f) return "never generates";
            if (biomeRarityFactor < 0.6f) return "very rare (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 1.6f) return "default, a handful of patches (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 4f) return "uncommon (" + biomeRarityFactor.ToString("0.0") + "x)";
            return "common (" + biomeRarityFactor.ToString("0.0") + "x)";
        }
    }

    public class RM_CauldronMod : Mod
    {
        public static RM_CauldronSettings settings;

        public RM_CauldronMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_CauldronSettings>();
        }

        public override string SettingsCategory()
        {
            return "The Cauldron";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
