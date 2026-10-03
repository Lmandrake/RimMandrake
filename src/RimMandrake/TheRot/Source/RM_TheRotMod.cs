using System.Collections.Generic;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TheRot
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 / §6a of THEROT_RM_MOD_BUILD_1 — Mod Settings for
    // The Rot. Pattern copied from RM_GreentideSettings
    // (src/RimMandrake/Greentide/Source/RM_GreentideMod.cs): static fields read
    // from everywhere, Scribe_Values in ExposeData, a DoWindowContents helper
    // called from the Mod subclass. Defaults = shipped behavior throughout.
    //
    // ROT_MOD_SETTINGS_WIRING_1: every control on this screen is wired, or hidden until the item that
    // wires it lands. This screen is the per-biome FRONT for mechanics living in mandrake.rm.environmentalhazards:
    // RM_TheRotFront (below) registers into RM_KitFronts at startup, and the shared mechanics ask it before
    // running on a map. The shared screen's own gate still applies first. A map that is neither The Rot nor an
    // opted-in cross-biome map is never affected by this screen.
    //   theRotEnabled             master: off = every gated mechanic reads off on Rot / cross-biome maps
    //   sheenExposure             sheenExposure          acceleratedRot(+Rate)   acceleratedRot
    //   livingProduceHeat(+PerUnit) livingProduceHeat    warmMat(+Warmth)        warmGround
    //   livePreparations / ...StrictViability            livePrepStrict (both must be on for strict)
    //   sporeCloudIncidentWeight  sporeCloud: 0 = never fires, otherwise scales the incident's chance
    //   sporeAllergy(+Incidence)  sporeAllergy: the RM_Disease_SporeAllergy pair, on/off and chance factor
    //   guardianGroves, paleTreeSpawn: the wild-spawn rows leave RM_TheRot's wildPlants at startup (restart)
    //   crossBiome*: opt-in donor (RM_TheRot's extensions) for non-Rot maps; Coverage scales their intensity
    //   healthSharing: the wound-link / kin-mending comps patched onto the five Alpha Animals bodies are removed again
    //                  at startup when off (restart to apply) - ROT_WOUND_SHARING_WIRING_1
    // ════════════════════════════════════════════════════════════════════
    public class RM_TheRotSettings : ModSettings
    {
        public static bool theRotEnabled = true;

        public static bool sheenExposure = true;
        public static bool acceleratedRot = true;
        public static float acceleratedRotRate = 1f;
        public static bool livingProduceHeat = true;
        public static float livingProduceHeatPerUnit = 1f;
        public static bool warmMat = true;
        public static float warmMatWarmth = 1f;
        public static bool livePreparations = true;
        public static bool livePreparationsStrictViability = true;
        public static bool guardianGroves = true;
        public static bool healthSharing = true;
        public static bool paleTreeSpawn = true;
        public static float sporeCloudIncidentWeight = 1f;
        public static bool sporeAllergy = true;
        public static float sporeAllergyIncidence = 1f;

        // ROT_HWELGRUE_GIANT_BUILD_1 — the Giant section.
        public static bool hwelgrue = true;
        public static float hwelgrueCastingDays = 2f;
        public static float hwelgrueRotMultiplier = 3f;
        public static int hwelgrueMapCap = 1;
        // ROT_STILL_ALIVE_SWALLOW_1
        public static bool hwelgrueSwallow = true;
        public static float swallowHoursPerBodySize = 24f;
        public static float swallowBellyCutDamage = 150f;
        public static float swallowStrangerChance = 0.15f;
        public static float swallowLoudness = 1f;
        // ROT_SWALLOWED_NAVIGATOR_1 (Ship section)
        public static bool navigatorCore = true;
        public static float navigatorPingHours = 12f;
        public static float navigatorRangeBonus = 0.25f;
        public static float navigatorShipDamageFactor = 0.5f;
        public static float navigatorRuinThreshold = 25f;
        // ROT_GUT_MOTHER_VAT_1 (Technology section)
        public static bool gutMother = true;
        public static float gutMotherDigestHours = 24f;
        public static float gutMotherRecoveryChance = 1f;
        public static float gutMotherStarterValue = 900f;

        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;

        private string biomeListBuffer;
        private Vector2 scrollPos;
        private float scrollHeight = 1400f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref theRotEnabled, "theRotEnabled", true);
            Scribe_Values.Look(ref sheenExposure, "sheenExposure", true);
            Scribe_Values.Look(ref acceleratedRot, "acceleratedRot", true);
            Scribe_Values.Look(ref acceleratedRotRate, "acceleratedRotRate", 1f);
            Scribe_Values.Look(ref livingProduceHeat, "livingProduceHeat", true);
            Scribe_Values.Look(ref livingProduceHeatPerUnit, "livingProduceHeatPerUnit", 1f);
            Scribe_Values.Look(ref warmMat, "warmMat", true);
            Scribe_Values.Look(ref warmMatWarmth, "warmMatWarmth", 1f);
            Scribe_Values.Look(ref livePreparations, "livePreparations", true);
            Scribe_Values.Look(ref livePreparationsStrictViability, "livePreparationsStrictViability", true);
            Scribe_Values.Look(ref guardianGroves, "guardianGroves", true);
            Scribe_Values.Look(ref healthSharing, "healthSharing", true);
            Scribe_Values.Look(ref paleTreeSpawn, "paleTreeSpawn", true);
            Scribe_Values.Look(ref sporeCloudIncidentWeight, "sporeCloudIncidentWeight", 1f);
            Scribe_Values.Look(ref sporeAllergy, "sporeAllergy", true);
            Scribe_Values.Look(ref sporeAllergyIncidence, "sporeAllergyIncidence", 1f);
            Scribe_Values.Look(ref hwelgrue, "hwelgrue", true);
            Scribe_Values.Look(ref hwelgrueCastingDays, "hwelgrueCastingDays", 2f);
            Scribe_Values.Look(ref hwelgrueRotMultiplier, "hwelgrueRotMultiplier", 3f);
            Scribe_Values.Look(ref hwelgrueMapCap, "hwelgrueMapCap", 1);
            Scribe_Values.Look(ref hwelgrueSwallow, "hwelgrueSwallow", true);
            Scribe_Values.Look(ref swallowHoursPerBodySize, "swallowHoursPerBodySize", 24f);
            Scribe_Values.Look(ref swallowBellyCutDamage, "swallowBellyCutDamage", 150f);
            Scribe_Values.Look(ref swallowStrangerChance, "swallowStrangerChance", 0.15f);
            Scribe_Values.Look(ref swallowLoudness, "swallowLoudness", 1f);
            Scribe_Values.Look(ref navigatorCore, "navigatorCore", true);
            Scribe_Values.Look(ref navigatorPingHours, "navigatorPingHours", 12f);
            Scribe_Values.Look(ref navigatorRangeBonus, "navigatorRangeBonus", 0.25f);
            Scribe_Values.Look(ref navigatorShipDamageFactor, "navigatorShipDamageFactor", 0.5f);
            Scribe_Values.Look(ref navigatorRuinThreshold, "navigatorRuinThreshold", 25f);
            Scribe_Values.Look(ref gutMother, "gutMother", true);
            Scribe_Values.Look(ref gutMotherDigestHours, "gutMotherDigestHours", 24f);
            Scribe_Values.Look(ref gutMotherRecoveryChance, "gutMotherRecoveryChance", 1f);
            Scribe_Values.Look(ref gutMotherStarterValue, "gutMotherStarterValue", 900f);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);
        }

        /// <summary>True if the cross-biome opt-in currently applies to this biome (never to The Rot's own — that is native, not "cross").</summary>
        public static bool AppliesToBiome(BiomeDef biome)
        {
            if (!crossBiomeEnabled || biome == null || biome.defName == "RM_TheRot")
            {
                return false;
            }
            if (crossBiomeEverywhere)
            {
                return true;
            }
            return ParseBiomeList().Contains(biome.defName);
        }

        private static List<string> ParseBiomeList()
        {
            var result = new List<string>();
            if (crossBiomeBiomeList.NullOrEmpty())
            {
                return result;
            }
            string[] parts = crossBiomeBiomeList.Split(',', ';');
            for (int i = 0; i < parts.Length; i++)
            {
                string trimmed = parts[i].Trim();
                if (trimmed.Length > 0)
                {
                    result.Add(trimmed);
                }
            }
            return result;
        }

        public void DoWindowContents(Rect inRect)
        {
            if (biomeListBuffer == null)
            {
                biomeListBuffer = crossBiomeBiomeList;
            }

            Rect view = new Rect(0f, 0f, inRect.width - 16f, scrollHeight);
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width };
            list.Begin(view);

            list.CheckboxLabeled("The Rot enabled", ref theRotEnabled,
                "Master switch. Off: the biome and its defs still load (nothing here is worldgen-affecting "
              + "except the cross-biome section below), but every per-feature toggle is ignored as off.");
            list.GapLine();

            list.CheckboxLabeled("Sheen exposure ladder", ref sheenExposure,
                "The Sheen weather rotation bootstraps a spore-coating hediff on unprotected pawns.");
            list.CheckboxLabeled("Accelerated rot/decay", ref acceleratedRot,
                "Items and corpses decay faster on this biome's living ground.");
            list.Label("  Rate: " + acceleratedRotRate.ToString("0.00") + "x");
            acceleratedRotRate = list.Slider(acceleratedRotRate, 0.25f, 3f);
            list.CheckboxLabeled("Living produce heat", ref livingProduceHeat,
                "Live food preparations radiate warmth proportional to stored mass.");
            list.Label("  Heat per unit: " + livingProduceHeatPerUnit.ToString("0.00") + "x");
            livingProduceHeatPerUnit = list.Slider(livingProduceHeatPerUnit, 0.25f, 3f);
            list.CheckboxLabeled("Warm living ground", ref warmMat,
                "The biome's natural terrain and living mycelium floors radiate ambient warmth.");
            list.Label("  Warmth: " + warmMatWarmth.ToString("0.00") + "x");
            warmMatWarmth = list.Slider(warmMatWarmth, 0.25f, 3f);
            list.CheckboxLabeled("Live preparations", ref livePreparations,
                "Food/ingredient preparations stay biologically \"alive\" until used.");
            list.CheckboxLabeled("  Strict viability", ref livePreparationsStrictViability,
                "Strict: viability lapses on any mishandling. Lenient: more forgiving window.");
            list.CheckboxLabeled("Health sharing (restart to apply)", ref healthSharing,
                "Chittik, gromma and rennok split wounds with kin in their grove; mullgoth and durrok heal faster among kin. "
              + "Needs Alpha Animals. Applies on the next launch.");
            list.CheckboxLabeled("Guardian groves (new maps, restart to apply)", ref guardianGroves,
                "Defended tea-source mushrooms wild-spawn with the false-fruit lure ring. WORLDGEN-AFFECTING: "
              + "applies to maps generated after the next launch.");
            list.CheckboxLabeled("Pale tree spawn (new maps, restart to apply)", ref paleTreeSpawn,
                "The rare pale tree (a door-ajar oddity) wild-spawns. Royalty-gated regardless of this toggle. "
              + "WORLDGEN-AFFECTING: applies to maps generated after the next launch.");
            list.Label("Spore cloud incident weight: " + sporeCloudIncidentWeight.ToString("0.00") + "x");
            sporeCloudIncidentWeight = list.Slider(sporeCloudIncidentWeight, 0f, 3f);
            list.CheckboxLabeled("Spore allergy", ref sporeAllergy,
                "The Sheen's spores cause the spore-allergy disease in people and animals (an incident). Off: never fires on this biome.");
            list.Label("  Incidence: " + sporeAllergyIncidence.ToString("0.00") + "x");
            sporeAllergyIncidence = list.Slider(sporeAllergyIncidence, 0.25f, 3f);
            list.GapLine();

            list.Label("Giant: the hwelgrue");
            list.CheckboxLabeled("Hwelgrue (wild spawn: new maps, restart to apply)", ref hwelgrue,
                "The gut that walks: a huge slow maggot that eats whatever lies on open ground and passes the metal in Sheen "
              + "castings. Off: it stops grazing and digesting, it leaves the Rot's wild roster on the next launch "
              + "(WORLDGEN-AFFECTING), and any wild one that appears is removed.");
            list.Label("  Days between castings: " + hwelgrueCastingDays.ToString("0.0"));
            hwelgrueCastingDays = list.Slider(hwelgrueCastingDays, 0.5f, 10f);
            list.Label("  Rot speed-up where it rests: " + hwelgrueRotMultiplier.ToString("0.0") + "x");
            hwelgrueRotMultiplier = list.Slider(hwelgrueRotMultiplier, 1f, 10f);
            list.Label("  Most on one map: " + hwelgrueMapCap);
            hwelgrueMapCap = Mathf.RoundToInt(list.Slider(hwelgrueMapCap, 1f, 5f));
            list.CheckboxLabeled("  Swallows the downed (Still Alive In There)", ref hwelgrueSwallow,
                "A hwelgrue takes a downed pawn lying in the open, any faction, and digests it slowly enough to rescue. "
              + "Knocking from inside says someone is still alive. Off: it never swallows anyone.");
            list.Label("  Hours to digest, per unit of body size: " + swallowHoursPerBodySize.ToString("0"));
            swallowHoursPerBodySize = list.Slider(swallowHoursPerBodySize, 3f, 72f);
            list.Label("  Damage that cuts its belly open: " + swallowBellyCutDamage.ToString("0"));
            swallowBellyCutDamage = list.Slider(swallowBellyCutDamage, 25f, 600f);
            list.Label("  Chance a newly met hwelgrue already holds someone: " + (swallowStrangerChance * 100f).ToString("0") + "%");
            swallowStrangerChance = list.Slider(swallowStrangerChance, 0f, 1f);
            list.Label("  Knocking loudness: " + swallowLoudness.ToString("0.00") + "x");
            swallowLoudness = list.Slider(swallowLoudness, 0f, 2f);
            list.GapLine();

            list.Label("Ship: the swallowed navigator");
            list.CheckboxLabeled("One hwelgrue per world carries an old drive core", ref navigatorCore,
                "It pings your gravship while it lives; cut out, the core is a facility that multiplies the grav engine's "
              + "total range. Off: no hwelgrue carries it, no pings, and an installed core adds nothing.");
            list.Label("  Hours between pings: " + navigatorPingHours.ToString("0"));
            navigatorPingHours = list.Slider(navigatorPingHours, 1f, 48f);
            list.Label("  Range bonus at full integrity: +" + (navigatorRangeBonus * 100f).ToString("0") + "% of total range");
            navigatorRangeBonus = list.Slider(navigatorRangeBonus, 0f, 1f);
            list.Label("  Core integrity lost per point of ship-weapon damage: " + navigatorShipDamageFactor.ToString("0.00"));
            navigatorShipDamageFactor = list.Slider(navigatorShipDamageFactor, 0f, 2f);
            list.Label("  Integrity below which the core comes out ruined: " + navigatorRuinThreshold.ToString("0"));
            navigatorRuinThreshold = list.Slider(navigatorRuinThreshold, 0f, 90f);
            list.GapLine();

            list.Label("Technology: the gut-mother");
            list.CheckboxLabeled("Gut-mother vat", ref gutMother,
                "A dead hwelgrue leaves its digesting sac; studied and researched, it grows a vat anywhere that digests "
              + "corpses and gives back their implants and gear. Off: no sac drops, vats take no bodies and digest nothing.");
            list.Label("  Hours to digest a body: " + gutMotherDigestHours.ToString("0"));
            gutMotherDigestHours = list.Slider(gutMotherDigestHours, 1f, 96f);
            list.Label("  Chance each implant comes back: " + (gutMotherRecoveryChance * 100f).ToString("0") + "%");
            gutMotherRecoveryChance = list.Slider(gutMotherRecoveryChance, 0f, 1f);
            list.Label("  Starter culture market value: " + gutMotherStarterValue.ToString("0"));
            gutMotherStarterValue = list.Slider(gutMotherStarterValue, 50f, 3000f);
            list.GapLine();

            list.Label("Cross-biome opt-in (WORLDGEN-AFFECTING — new maps only)");
            list.Label("Lets Rot mechanics generate on a NON-Rot biome's map, without adding the whole "
              + "biome. Applies once, right after a map generates; an existing map is never retroactively "
              + "changed.");
            list.CheckboxLabeled("Enable outside The Rot biome", ref crossBiomeEnabled,
                "Master switch for the section below.");
            if (crossBiomeEnabled)
            {
                list.CheckboxLabeled("  Every biome", ref crossBiomeEverywhere,
                    "Apply to any non-Rot biome. Off: only the biomes named below.");
                if (!crossBiomeEverywhere)
                {
                    list.Label("  Biome defNames, comma-separated (e.g. TropicalRainforest, AridShrubland):");
                    biomeListBuffer = list.TextEntry(biomeListBuffer);
                    crossBiomeBiomeList = biomeListBuffer;
                }
                list.Label("  Intensity on those maps: " + (crossBiomeCoverage * 100f).ToString("0") + "%");
                crossBiomeCoverage = list.Slider(crossBiomeCoverage, 0f, 1f);
            }

            list.End();
            scrollHeight = Mathf.Max(inRect.height, list.CurHeight + 24f);
            Widgets.EndScrollView();
        }
    }

    /// <summary>ROT_MOD_SETTINGS_WIRING_1: registers this screen as the front for the shared Rot mechanics.</summary>
    [StaticConstructorOnStartup]
    public static class RM_TheRotFront
    {
        public static bool IsRotBiome(BiomeDef biome)
        {
            return biome != null && (biome.defName == "RM_TheRot" || biome.defName == "RUT_TheRot");
        }

        /// <summary>True when this screen governs a map of this biome (the Rot itself, or an opted-in cross-biome map).</summary>
        public static bool Governs(BiomeDef biome)
        {
            return IsRotBiome(biome) || RM_TheRotSettings.AppliesToBiome(biome);
        }

        public static bool Enabled(string key, BiomeDef biome)
        {
            if (!Governs(biome))
            {
                return true;
            }
            if (!RM_TheRotSettings.theRotEnabled)
            {
                return false;
            }
            switch (key)
            {
                case "sheenExposure": return RM_TheRotSettings.sheenExposure;
                case "acceleratedRot": return RM_TheRotSettings.acceleratedRot;
                case "livingProduceHeat": return RM_TheRotSettings.livingProduceHeat;
                case "warmGround": return RM_TheRotSettings.warmMat;
                case "livePrepStrict": return RM_TheRotSettings.livePreparations && RM_TheRotSettings.livePreparationsStrictViability;
                case "sporeCloud": return RM_TheRotSettings.sporeCloudIncidentWeight > 0f;
                case "sporeAllergy": return RM_TheRotSettings.sporeAllergy;
                default: return true;
            }
        }

        public static float Factor(string key, BiomeDef biome)
        {
            if (!Governs(biome))
            {
                return 1f;
            }
            float f;
            switch (key)
            {
                case "acceleratedRot": f = RM_TheRotSettings.acceleratedRotRate; break;
                case "livingProduceHeat": f = RM_TheRotSettings.livingProduceHeatPerUnit; break;
                case "warmGround": f = RM_TheRotSettings.warmMatWarmth; break;
                case "sporeCloud": f = RM_TheRotSettings.sporeCloudIncidentWeight; break;
                case "sporeAllergy": f = RM_TheRotSettings.sporeAllergyIncidence; break;
                default: return 1f;
            }
            return IsRotBiome(biome) ? f : f * RM_TheRotSettings.crossBiomeCoverage;
        }

        static RM_TheRotFront()
        {
            RM_KitFronts.enabled = Enabled;
            RM_KitFronts.factor = Factor;
            RM_KitFronts.extensionDonor = biome =>
                !IsRotBiome(biome) && RM_TheRotSettings.theRotEnabled && RM_TheRotSettings.AppliesToBiome(biome)
                    ? DefDatabase<BiomeDef>.GetNamedSilentFail("RM_TheRot")
                    : null;

            if (!RM_TheRotSettings.theRotEnabled || !RM_TheRotSettings.healthSharing)
            {
                foreach (string body in HealthSharingBodies)
                {
                    ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(body);
                    def?.comps?.RemoveAll(c => c is RimMandrake.CreatureBehaviors.CompProperties_WoundLink
                                               || c is RimMandrake.CreatureBehaviors.CompProperties_GrantHediff);
                }
            }

            // Wild-spawn gates take effect on the next launch (the roster is read at map generation).
            BiomeDef rot = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_TheRot");
            if (rot == null || rot.wildPlants == null)
            {
                return;
            }
            if (!RM_TheRotSettings.theRotEnabled || !RM_TheRotSettings.paleTreeSpawn)
            {
                rot.wildPlants.RemoveAll(r => r.plant != null && r.plant.defName == "RM_PaleTree");
            }
            if (!RM_TheRotSettings.theRotEnabled || !RM_TheRotSettings.guardianGroves)
            {
                rot.wildPlants.RemoveAll(r => r.plant != null && System.Array.IndexOf(GuardianGroveRows, r.plant.defName) >= 0);
            }
            if (!RM_TheRotSettings.theRotEnabled || !RM_TheRotSettings.hwelgrue)
            {
                // BiomeDef.wildAnimals is private; its commonality cache is built lazily on first read (after startup).
                var field = typeof(BiomeDef).GetField("wildAnimals", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
                (field?.GetValue(rot) as List<BiomeAnimalRecord>)?.RemoveAll(r => r.animal != null && r.animal.defName == "RM_Hwelgrue");
            }
        }

        private static readonly string[] HealthSharingBodies = { "AA_Swarmling", "AA_Agaripod", "AA_Agaripawn", "AA_Wildpod", "AA_Wildpawn" };
        private static readonly string[] GuardianGroveRows = { "RM_AgelessCap", "RM_RegenerantVeil", "RM_EuphoricCrown", "RM_FalseFruit" };
    }

    public class RM_TheRotMod : Mod
    {
        public static RM_TheRotSettings settings;

        public RM_TheRotMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_TheRotSettings>();
        }

        public override string SettingsCategory()
        {
            return "The Rot";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            RM_GutMother.ApplyStarterValue();
        }
    }
}
