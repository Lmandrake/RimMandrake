using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Greentide
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Greentide.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs (static
    // fields read from everywhere, Scribe_Values in ExposeData, a
    // DoWindowContents helper called from the Mod subclass).
    //
    // Three things this exposes, per the item's own spec:
    //   1. Master on/off per mechanic (mire hazard, buried caches) — default
    //      ON, matching shipped GREENTIDE_STANDALONE_MOD_1 behavior.
    //   2. A tuning number (mire severity multiplier) — default 1.0x.
    //   3. The named trigger case: per-feature biome opt-in so the churnmud/
    //      mire hazard can run on a NON-Greentide biome's maps without
    //      importing the whole Greentide biome. WORLDGEN-AFFECTING — labeled
    //      as such in the UI and only ever applied once, to a freshly
    //      generated map (RM_MapComponent_CrossBiomeChurnmud).
    //
    // Buried caches (RM_MapComponent_MudSwallow) need no separate cross-biome
    // toggle: it already fires off the terrain extension alone, wherever
    // RM_GreentideChurnmud exists, native map or opted-in map alike. The Greatbole
    // does not exist yet (About.xml: gated on ALPHA_MECHANICS_KIT_1 /
    // EXPLOSIVE_PLANT_GROWTH_1) — nothing to gate.
    // ════════════════════════════════════════════════════════════════════
    public class RM_GreentideSettings : ModSettings
    {
        public static bool mireEnabled = true;
        public static bool buriedCacheEnabled = true;
        public static float mireSeverityMultiplier = 1f;

        // GREENTIDE_DENSITY_SETTINGS_1. Ship values from GREENTIDE_BIOME_DENSITY_1
        // (RM_Greentide_Biome.xml, MEASURED against vanilla TropicalSwamp). Applied
        // to the live RM_Greentide BiomeDef at runtime by
        // RM_GreentideDensityApplier — BiomeDef has no settings hook of its own,
        // so writing the runtime instance's fields directly is the mechanism
        // (same shape as src/RimMandrake/Pyrelands/Source/RM_PyrelandsDensityEnforcer.cs).
        // Slider floors match the item's own de-escalation target: vanilla
        // TropicalRainforest (plantDensity 0.90, movementDifficulty 2), not zero
        // — this stays a jungle at the softest setting, never a plain.
        public static float plantDensity = 0.99f;
        public static float movementDifficulty = 4f;

        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;

        // GREENTIDE_FRENZY_DISEASE_1. Master on/off covers BOTH routes RM_Frenzy
        // can reach a pawn through — the ambient biome disease
        // (RM_IncidentWorker_FrenzyDisease) and the deliberate RM_FrenzyDose item
        // (RM_IngestionOutcomeDoer_FrenzyDose) — since both read this same flag.
        // The multiplier only tunes the dose route's initial kick; the natural
        // per-day climb, the coma threshold and tend strength are the disease's
        // own HediffDef numbers and are not settings (a number that changes the
        // shape of the death/survival curve, not just its speed, is a design
        // call, not a player-tuning knob).
        public static bool frenzyEnabled = true;
        public static float frenzySeverityMultiplier = 1f;

        // GREENTIDE_FEVER_SPECIALISTS_1. R1 "immunological capital" — the
        // permanent RM_FeverMark badge on a colonist who survives the Frenzy
        // (reaches the collapse stage and is tended out of it alive) and the
        // resistance-on-re-exposure gate that makes it a real qualification.
        // feverMarkEnabled is the master switch (off: RM_Frenzy behaves exactly
        // as GREENTIDE_FRENZY_DISEASE_1 shipped it, no mark ever applied).
        // feverMarkGrantsImmunity is a separate sub-toggle so a player can keep
        // the cosmetic badge (health-tab bragging rights) without the gameplay
        // gate, or turn the gate off while the badge still applies — both read
        // false with feverMarkEnabled off regardless of their own state.
        public static bool feverMarkEnabled = true;
        public static bool feverMarkGrantsImmunity = true;

        // GREENTIDE_GRENADE_WEAPONS_1. The stench smoke grenade — the only
        // one of the jungle's three named grenades this item builds (the
        // seeding grenade and both toxin routes stay designed-but-unbuilt,
        // queued behind this proof). StenchGrenadeBaseRadius MUST match
        // RM_Proj_GrenadeStenchSmoke's <explosionRadius> in
        // RM_StenchGrenade_Items.xml — RM_Proj_GrenadeStenchSmoke.cs reads
        // this constant every throw rather than the XML value directly, so
        // the two are coupled by convention, not by a shared reference.
        public const float StenchGrenadeBaseRadius = 3.6f;
        public static bool stenchGrenadeEnabled = true;
        public static float stenchGrenadeRadiusMultiplier = 1f;

        // GREENTIDE_CANOPY_SWARM_1. RM_Krannock's own tree-gnawing AI is
        // ALREADY gated for free by the shared Environmental Hazards Kit's
        // "Tree fall (crack, shatter, gnaw)" toggle (RM_EnvironmentalHazardsSettings
        // .treeFallEnabled) — that toggle's own tooltip already names "a
        // creature built to gnaw one down stops seeking a trunk to chew", so
        // no duplicate Greentide-local toggle is wired to the mechanic
        // itself; a second checkbox that just mirrored the kit's own would
        // be a decoy, not a control.
        //
        // canopySwarmEnabled below is the master on/off for RM_Krannock's
        // WILD SPAWNING once the Greentide's own review sitting places it in
        // the biome roster (out of THIS item's scope by the item's own
        // instruction — see GREENTIDE_CANOPY_SWARM_1). It is a deliberate
        // no-op today, same posture as grazingSuppressionHookEnabled in
        // RM_EnvironmentalHazardsSettings ("armed but the system it feeds
        // hasn't shipped") — shipped now so no later pass has to retrofit
        // MOD_OPTIONS_RETROFIT_1 onto it once placement lands.
        public static bool canopySwarmEnabled = true;

        private string biomeListBuffer;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref mireEnabled, "mireEnabled", true);
            Scribe_Values.Look(ref buriedCacheEnabled, "buriedCacheEnabled", true);
            Scribe_Values.Look(ref mireSeverityMultiplier, "mireSeverityMultiplier", 1f);
            Scribe_Values.Look(ref plantDensity, "plantDensity", 0.99f);
            Scribe_Values.Look(ref movementDifficulty, "movementDifficulty", 4f);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);
            Scribe_Values.Look(ref frenzyEnabled, "frenzyEnabled", true);
            Scribe_Values.Look(ref frenzySeverityMultiplier, "frenzySeverityMultiplier", 1f);
            Scribe_Values.Look(ref feverMarkEnabled, "feverMarkEnabled", true);
            Scribe_Values.Look(ref feverMarkGrantsImmunity, "feverMarkGrantsImmunity", true);
            Scribe_Values.Look(ref stenchGrenadeEnabled, "stenchGrenadeEnabled", true);
            Scribe_Values.Look(ref stenchGrenadeRadiusMultiplier, "stenchGrenadeRadiusMultiplier", 1f);
            Scribe_Values.Look(ref canopySwarmEnabled, "canopySwarmEnabled", true);
        }

        /// <summary>True if the cross-biome opt-in currently applies to this biome (never to Greentide's own — that is native, not "cross").</summary>
        public static bool AppliesToBiome(BiomeDef biome)
        {
            if (!crossBiomeEnabled || biome == null || biome.defName == "RM_Greentide")
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

            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Churnmud / mire hazard");
            list.CheckboxLabeled("Mire hazard enabled", ref mireEnabled,
                "Standing on churnmud escalates the RM_Mired hediff (slowed, then stuck). "
              + "Off: churnmud is inert underfoot — no NREs, the terrain just does nothing.");
            list.Label("Mire severity: " + mireSeverityMultiplier.ToString("0.00") + "x");
            mireSeverityMultiplier = list.Slider(mireSeverityMultiplier, 0.25f, 3f);
            list.Gap();
            list.CheckboxLabeled("Buried caches enabled", ref buriedCacheEnabled,
                "Loose items left on churnmud long enough get buried (dig them back out, nothing "
              + "is destroyed). Off: items just sit there like any other terrain.");
            list.GapLine();

            list.Label("Jungle density");
            list.Label("Plant density: " + plantDensity.ToString("0.00")
              + " (new maps only — a map you've already generated keeps the coverage it was born with)");
            plantDensity = list.Slider(plantDensity, 0.90f, 0.99f);
            list.Label("World-map movement difficulty: " + movementDifficulty.ToString("0.0")
              + " — how much SLOWER a caravan crosses Greentide tiles on the PLANET map. This does "
              + "NOT affect walking speed inside a Greentide map at all; in-map crossing cost comes "
              + "from the churnmud terrain above, not this number.");
            movementDifficulty = list.Slider(movementDifficulty, 2f, 4f);
            list.GapLine();

            list.Label("Cross-biome opt-in (WORLDGEN-AFFECTING — new maps only)");
            list.Label("Lets churnmud/mire generate on a NON-Greentide biome's map, without "
              + "adding the whole Greentide biome. Applies once, right after a map generates; "
              + "a map that already exists is never retroactively changed.");
            list.CheckboxLabeled("Enable outside the Greentide biome", ref crossBiomeEnabled,
                "Master switch for the section below.");
            if (crossBiomeEnabled)
            {
                list.CheckboxLabeled("  Every biome", ref crossBiomeEverywhere,
                    "Apply to any non-Greentide biome. Off: only the biomes named below.");
                if (!crossBiomeEverywhere)
                {
                    list.Label("  Biome defNames, comma-separated (e.g. TropicalRainforest, AridShrubland):");
                    biomeListBuffer = list.TextEntry(biomeListBuffer);
                    crossBiomeBiomeList = biomeListBuffer;
                }
                list.Label("  Coverage: " + (crossBiomeCoverage * 100f).ToString("0") + "% of that map's ordinary Mud terrain becomes churnmud");
                crossBiomeCoverage = list.Slider(crossBiomeCoverage, 0f, 1f);
            }
            list.GapLine();

            list.Label("The Frenzy");
            list.CheckboxLabeled("The Frenzy enabled", ref frenzyEnabled,
                "Covers both routes: the jungle handing it out on its own as an ambient disease, "
              + "and a colonist taking a harvested RM_FrenzyDose on purpose. Off: neither ever "
              + "applies the hediff.");
            if (frenzyEnabled)
            {
                list.Label("  Dose strength: " + frenzySeverityMultiplier.ToString("0.00") + "x");
                frenzySeverityMultiplier = list.Slider(frenzySeverityMultiplier, 0.5f, 2f);
                list.Gap();
                list.CheckboxLabeled("  Survivors become specialists", ref feverMarkEnabled,
                    "A colonist who lives through the Frenzy's coma keeps a permanent, visible "
                  + "RM_FeverMark in their health tab — earned only by reaching the coma stage and "
                  + "being tended out of it alive, never by an early cure. Off: the Frenzy behaves "
                  + "exactly as before, no mark is ever applied.");
                if (feverMarkEnabled)
                {
                    list.CheckboxLabeled("    Marked colonists are resistant to catching it again", ref feverMarkGrantsImmunity,
                        "The qualification half of the reward: a fever-marked colonist is dropped from "
                      + "the ambient Frenzy incident's victim pool, and a harvested dose is wasted on "
                      + "one rather than re-applying. Off: the badge is purely cosmetic — a marked "
                      + "colonist can still catch or be dosed with the Frenzy like anyone else.");
                }
            }
            list.GapLine();

            list.Label("Jungle grenades");
            list.CheckboxLabeled("Stench smoke grenades enabled", ref stenchGrenadeEnabled,
                "Thrown grenades that burst into a reeking cloud every animal in the biome "
              + "flees — beasts and the wasp swarm alike. Off: a thrown one is a dud, no "
              + "explosion, no gas, no flee. The reek is real rot-stink gas, so it costs your "
              + "own colonists and animals the same lingering-exposure risk it costs anyone "
              + "else caught in it.");
            if (stenchGrenadeEnabled)
            {
                list.Label("  Cloud radius: " + (StenchGrenadeBaseRadius * stenchGrenadeRadiusMultiplier).ToString("0.0")
                    + " cells (" + stenchGrenadeRadiusMultiplier.ToString("0.00") + "x)");
                stenchGrenadeRadiusMultiplier = list.Slider(stenchGrenadeRadiusMultiplier, 0.5f, 2f);
            }
            list.GapLine();

            list.Label("Canopy swarm (the krannock)");
            list.CheckboxLabeled("Canopy swarm wild spawning", ref canopySwarmEnabled,
                "Master on/off for the krannock (RM_Krannock) once it is placed in the biome's "
              + "wild-animal roster by a future sitting — currently has no visible effect, since "
              + "this creature is not yet wired into any roster. Its tree-gnawing AI is already "
              + "covered by the Environmental Hazards Kit's own \"Tree fall\" toggle, not this one.");

            list.End();
        }
    }

    public class RM_GreentideMod : Mod
    {
        public static RM_GreentideSettings settings;

        public RM_GreentideMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_GreentideSettings>();
        }

        public override string SettingsCategory()
        {
            return "Greentide";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            // GREENTIDE_DENSITY_SETTINGS_1: re-assert onto the live BiomeDef the
            // moment the settings window closes, so a movementDifficulty change
            // (a world-tile stat read on demand, not cached at worldgen) is felt
            // immediately rather than waiting on the next game load.
            RM_GreentideDensityApplier.Apply();
        }
    }
}
