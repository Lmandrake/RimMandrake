using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Scarlands
{
    // ════════════════════════════════════════════════════════════════════
    // Mod Settings for Warscar (SCARLANDS_STANDALONE_MOD_1, extended by
    // WARSCAR_FREE_TIER_BODY_1): worldgen rarity, a toggle per new species,
    // the wreck-lichen seeder, and the interim donor rows.
    //
    // STATIC FIELDS, read from worldgen with no Mod instance handy.
    // Species toggles are applied once at startup by RM_WarscarStartup,
    // which removes disabled rows from RM_Warscar's wildAnimals; changing
    // one needs a restart (said on the screen).
    // ════════════════════════════════════════════════════════════════════
    public class RM_WarscarSettings : ModSettings
    {
        public static float biomeRarityFactor = 1f;

        public static bool enableChatrak = true;
        public static bool enableTotchak = true;
        public static bool enableTetchik = true;
        public static bool enablePallbearer = true;
        public static bool enableScarRoach = true;
        public static bool enableWreckLichenSeeder = true;
        public static bool enableInterimDonors = true;

        // MOD_OPTIONS_RETROFIT_1 reserved cross-biome fields, not wired to any mechanic.
        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref enableChatrak, "enableChatrak", true);
            Scribe_Values.Look(ref enableTotchak, "enableTotchak", true);
            Scribe_Values.Look(ref enableTetchik, "enableTetchik", true);
            Scribe_Values.Look(ref enablePallbearer, "enablePallbearer", true);
            Scribe_Values.Look(ref enableScarRoach, "enableScarRoach", true);
            Scribe_Values.Look(ref enableWreckLichenSeeder, "enableWreckLichenSeeder", true);
            Scribe_Values.Look(ref enableInterimDonors, "enableInterimDonors", true);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 Warscar never generates on a new planet. Affects planets "
                       + "generated afterwards, never one that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
            list.GapLine();

            list.Label("Species (restart required; affects maps generated afterwards)");
            list.CheckboxLabeled("Chatrak (plated grazer)", ref enableChatrak);
            list.CheckboxLabeled("Totchak (colossus)", ref enableTotchak);
            list.CheckboxLabeled("Tetchik (glower beetle)", ref enableTetchik);
            list.CheckboxLabeled("Pallbearer (carrion eater)", ref enablePallbearer);
            list.CheckboxLabeled("Scar roach (cleaner)", ref enableScarRoach);
            list.CheckboxLabeled("Interim donor animals (spined gow, rimclaw, helixien)", ref enableInterimDonors);
            list.GapLine();

            list.CheckboxLabeled("Wreck-lichen grows beside ruins and wreck", ref enableWreckLichenSeeder,
                "Places wreck-lichen on open cells next to ruins and wreck. Worldgen-affecting.");
            list.GapLine();

            list.Label("Cross-biome (reserved, not yet wired to any mechanic in this build)");
            bool crossBiomeEnabledLocal = crossBiomeEnabled;
            list.CheckboxLabeled("Allow this mod's mechanics on other biomes", ref crossBiomeEnabledLocal,
                "Reserved for a future pass. No mechanic in this mod currently reads this switch.");
            crossBiomeEnabled = crossBiomeEnabledLocal;

            list.End();
        }

        private static string RarityLabel()
        {
            if (biomeRarityFactor <= 0.001f) return "never generates";
            if (biomeRarityFactor < 0.6f) return "very rare (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 1.6f) return "default (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 4f) return "uncommon (" + biomeRarityFactor.ToString("0.0") + "x)";
            return "common (" + biomeRarityFactor.ToString("0.0") + "x)";
        }
    }

    public class RM_WarscarMod : Mod
    {
        public static RM_WarscarSettings settings;

        public RM_WarscarMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WarscarSettings>();
            new Harmony("mandrake.rm.warscar").PatchAll(Assembly.GetExecutingAssembly());
        }

        public override string SettingsCategory()
        {
            return "Warscar";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }

    // Removes the wildAnimals rows of species the player switched off.
    // BiomeDef.wildAnimals is private and its commonality cache is lazy, so
    // this runs once at startup, before any map asks for a commonality.
    [StaticConstructorOnStartup]
    public static class RM_WarscarStartup
    {
        static RM_WarscarStartup()
        {
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Warscar");
            if (biome == null) return;

            HashSet<string> off = new HashSet<string>();
            if (!RM_WarscarSettings.enableChatrak) off.Add("RM_Chatrak");
            if (!RM_WarscarSettings.enableTotchak) off.Add("RM_Totchak");
            if (!RM_WarscarSettings.enableTetchik) off.Add("RM_Tetchik");
            if (!RM_WarscarSettings.enablePallbearer) off.Add("RM_Pallbearer");
            if (!RM_WarscarSettings.enableScarRoach) off.Add("RM_ScarRoach");
            if (!RM_WarscarSettings.enableInterimDonors)
            {
                off.Add("AA_SpinedGow");
                off.Add("RG_Rimclaw");
                off.Add("AA_Helixien");
            }
            if (off.Count == 0) return;

            FieldInfo wild = AccessTools.Field(typeof(BiomeDef), "wildAnimals");
            FieldInfo cache = AccessTools.Field(typeof(BiomeDef), "cachedAnimalCommonalities");
            if (wild == null || cache == null)
            {
                Log.Warning("[RM_Warscar] BiomeDef.wildAnimals/cachedAnimalCommonalities not found; species toggles not applied.");
                return;
            }
            List<BiomeAnimalRecord> rows = (List<BiomeAnimalRecord>)wild.GetValue(biome);
            rows.RemoveAll(r => r.animal != null && off.Contains(r.animal.defName));
            cache.SetValue(biome, null);
        }
    }
}
