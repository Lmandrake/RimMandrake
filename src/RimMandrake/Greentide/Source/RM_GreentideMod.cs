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
    // RM_GreentideChurnmud exists, native map or opted-in map alike.
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

        // GREENTIDE_VURRAK_BUILD_1 — the false bank (RM_CompBankAmbusher). Off: a vurrak never lies
        // hidden and never bites on contact; it is a slow, ordinary riverbank animal.
        public static bool vurrakAmbushEnabled = true;
        // Weight threshold, as body size. A person is 1.0; the default lets a teenager or a dog set it off
        // and a hare only reveal it.
        public static float vurrakTriggerBodySize = 0.6f;
        // Owner ruling 2026-10-03: the first-ever reveal pauses the game and explains itself.
        public static bool vurrakFirstRevealPause = true;

        // GREENTIDE_ILLISK_BUILD_1 - the shoal's hide (RM_CompShoalHide). Off: an illisk takes damage like any small animal.
        // Non-blast factor is PROVISIONAL: 0.04 turns a 12-damage bullet into 0.5.
        public static bool shoalHideEnabled = true;
        public static float shoalNonBlastFactor = 0.04f;

        // GREENTIDE_STELLOCK_LACE_BUILD_1 (RM_StellockLace.cs). Off: no branch
        // drops and the project is never hidden-then-revealed (the shared
        // found-tech gate, registered in RM_GreentideMod). Made laces still work.
        public static bool stellockLaceEnabled = true;
        // PROVISIONAL: spec's "about 1 in 8" per felled roster tree.
        public static float stellockBranchChance = 0.125f;
        // Spec default: 12 in-game hours.
        public static float stellockLaceHours = 12f;

        // GREENTIDE_THURROCK_HERD_BUILD_1 — the thurrock's RM_ThurrockShatter auras, written onto the live
        // HediffDef by RM_ThurrockAuraApplier. Felling off: a big browser that fells nothing. Pace multiplies
        // how often the resting aura bursts (trees felled per hour). Wall damage off: provoked, it still
        // fells trees but never touches a building.
        public static bool thurrockFellingEnabled = true;
        public static float thurrockFellingPace = 1f;
        public static bool thurrockProvokedWallDamage = true;

        // GREENTIDE_BASE_PORT_BUILD_1 — the spine moved down from the campaign tier.
        // The Roil: RM_RoilLock (and RM_RoilWeather's table row) are taken off RM_Greentide by
        // RM_GreentideDensityApplier when off. biomeMapConditions are applied in
        // BiomeConditionMapComponent.MapGenerated, so this reaches NEW maps only.
        public static bool roilEnabled = true;
        // Greatbole fruitfall (RM_IncidentWorker_GreatboleFruitfall.CanFireNowSub).
        public static bool fruitfallEnabled = true;
        // GREATBOLE_HARVEST_LADDER_1 thresholds, read by RM_CompGreatboleHarvestLadder (moved here from
        // the campaign's UtinniPatchesSettings with the comp). Grub breeding is not duplicated: it is
        // RM_CreatureBehaviorsSettings.verminBreedingEnabled. Breaklight, living boles and
        // root causeways are already live toggles in the Environmental Hazards Kit's screen; this screen
        // names them rather than adding a second switch on the same wire.
        public static float greatboleShakingThreshold = 0.40f;
        public static float greatboleHealingThreshold = 0.60f;
        public static float greatboleCatastropheThreshold = 0.70f;
        public static bool greatboleCatastropheEnabled = true;
        // GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1. Seed planting (spec §3c): gates the seed's
        // CompPlantable (Patches/RM_Greatbole_Crossovers.xml) and RM_Plant_Greatbole's water rule and
        // fast growth. Shipped behaviour, so default ON. Servants (spec §8b-ii): the opt-in Gauranlen
        // crossover on RM_GreatboleCore, DEFAULT OFF by owner ruling (Utinni ships it off). Both are
        // read when patches apply, so a change takes effect on the next game start.
        public static bool greatboleSeedPlantingEnabled = true;
        public static bool greatboleServantsEnabled = false;

        private string biomeListBuffer;
        private static Vector2 scrollPosition;
        private static float lastContentHeight = 1200f;

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
            Scribe_Values.Look(ref vurrakAmbushEnabled, "vurrakAmbushEnabled", true);
            Scribe_Values.Look(ref vurrakTriggerBodySize, "vurrakTriggerBodySize", 0.6f);
            Scribe_Values.Look(ref vurrakFirstRevealPause, "vurrakFirstRevealPause", true);
            Scribe_Values.Look(ref shoalHideEnabled, "shoalHideEnabled", true);
            Scribe_Values.Look(ref shoalNonBlastFactor, "shoalNonBlastFactor", 0.04f);
            Scribe_Values.Look(ref stellockLaceEnabled, "stellockLaceEnabled", true);
            Scribe_Values.Look(ref stellockBranchChance, "stellockBranchChance", 0.125f);
            Scribe_Values.Look(ref stellockLaceHours, "stellockLaceHours", 12f);
            Scribe_Values.Look(ref thurrockFellingEnabled, "thurrockFellingEnabled", true);
            Scribe_Values.Look(ref thurrockFellingPace, "thurrockFellingPace", 1f);
            Scribe_Values.Look(ref thurrockProvokedWallDamage, "thurrockProvokedWallDamage", true);
            Scribe_Values.Look(ref roilEnabled, "roilEnabled", true);
            Scribe_Values.Look(ref fruitfallEnabled, "fruitfallEnabled", true);
            Scribe_Values.Look(ref greatboleShakingThreshold, "greatboleShakingThreshold", 0.40f);
            Scribe_Values.Look(ref greatboleHealingThreshold, "greatboleHealingThreshold", 0.60f);
            Scribe_Values.Look(ref greatboleCatastropheThreshold, "greatboleCatastropheThreshold", 0.70f);
            Scribe_Values.Look(ref greatboleCatastropheEnabled, "greatboleCatastropheEnabled", true);
            Scribe_Values.Look(ref greatboleSeedPlantingEnabled, "greatboleSeedPlantingEnabled", true);
            Scribe_Values.Look(ref greatboleServantsEnabled, "greatboleServantsEnabled", false);
        }

        /// <summary>True if the cross-biome opt-in currently applies to this biome (never to Greentide's own - that is native, not "cross").</summary>
        public static bool AppliesToBiome(BiomeDef biome)
        {
            return RM_RulesKernel.AppliesToBiome(crossBiomeEnabled, biome?.defName, "RM_Greentide", crossBiomeEverywhere, crossBiomeBiomeList);
        }

        public void DoWindowContents(Rect inRect)
        {
            if (biomeListBuffer == null)
            {
                biomeListBuffer = crossBiomeBiomeList;
            }

            // Scrolls: the screen outgrew one window height when the vurrak joined.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 20f, Mathf.Max(lastContentHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPosition, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);

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
            list.GapLine();

            list.Label("Stellock lace");
            list.CheckboxLabeled("Stellock branches and the lace research", ref stellockLaceEnabled,
                "On: felling a Greentide tree on a Greentide map can drop a stellock branch; studying branches "
              + "reveals the stellock lace research. Off: no branches drop and the research is an ordinary "
              + "visible project. Laces already made still work either way.");
            if (stellockLaceEnabled)
            {
                list.Label("  Branch drop chance per felled tree: " + stellockBranchChance.ToStringPercent());
                stellockBranchChance = list.Slider(stellockBranchChance, 0f, 1f);
            }
            list.Label("  A lace stops bleeding for: " + stellockLaceHours.ToString("0.#") + " hours");
            stellockLaceHours = list.Slider(stellockLaceHours, 1f, 48f);
            list.GapLine();

            list.Label("The shoal (the illisk)");
            list.CheckboxLabeled("Illisk hide", ref shoalHideEnabled,
                "On: bullets, blades, claws and fists barely scratch an illisk; only blasts hurt it at full strength. "
              + "Off: an illisk takes damage like any small animal.");
            if (shoalHideEnabled)
            {
                list.Label("  Damage that is not a blast gets through at: " + (shoalNonBlastFactor * 100f).ToString("0") + "%");
                shoalNonBlastFactor = list.Slider(shoalNonBlastFactor, 0f, 1f);
            }
            list.GapLine();

            list.Label("The false bank (the vurrak)");
            list.CheckboxLabeled("Vurrak ambush", ref vurrakAmbushEnabled,
                "On: a vurrak lies flat along the water's edge, invisible as silted bank, and bites whatever heavy "
              + "enough steps on it. Lighter animals only make it flinch and show itself. Off: it never hides and "
              + "never bites on contact; it is an ordinary slow riverbank animal.");
            if (vurrakAmbushEnabled)
            {
                list.Label("  Weight that sets it off (body size): " + vurrakTriggerBodySize.ToString("0.00")
                         + " (a person is 1.00)");
                vurrakTriggerBodySize = list.Slider(vurrakTriggerBodySize, 0.2f, 2f);
                list.CheckboxLabeled("  Pause the first time one is revealed", ref vurrakFirstRevealPause,
                    "On: the very first time your people see a vurrak reveal itself, the game pauses and a letter "
                  + "explains what happened. Once per game.");
            }

            list.GapLine();

            list.Label("The canopy-breaker (the thurrock)");
            list.CheckboxLabeled("Thurrock fells trees", ref thurrockFellingEnabled,
                "On: a thurrock herd batters the trees around it as it browses, and a tree beaten low enough comes "
              + "down as a fallen trunk and wood. Off: it is a huge browser that fells nothing.");
            if (thurrockFellingEnabled)
            {
                list.Label("  Felling pace: " + thurrockFellingPace.ToString("0.00") + "x (how often the herd's blows land; higher fells more trees per hour)");
                thurrockFellingPace = list.Slider(thurrockFellingPace, 0.25f, 3f);
            }
            list.CheckboxLabeled("Provoked thurrocks batter walls", ref thurrockProvokedWallDamage,
                "On: a manhunting thurrock shoulders walls and doors the way it shoulders trees. Natural rock is "
              + "always spared, and a calm one never damages buildings. Off: no building damage even when provoked.");

            list.GapLine();

            list.Label("The Roil, Breaklight and the greatbole");
            list.CheckboxLabeled("The Roil (WORLDGEN-AFFECTING — new maps only)", ref roilEnabled,
                "On: a Greentide map stands under permanent waist-deep hot fog (aim x0.7, move x0.95), and the "
              + "fog can throw up a steam devil. Off: maps generated after the change get ordinary weather. "
              + "A map that already exists keeps the fog it was born with.");
            list.CheckboxLabeled("Greatbole fruitfall", ref fruitfallEnabled,
                "On: now and then a living greatbole drops a fruit or two and a few grubs on its own, no wound "
              + "needed. Off: fruit only comes from felling or wounding.");
            list.Label("Greatbole harvest ladder — share of a bole's footprint mined away.");
            list.Label("  The Great Shaking: " + (greatboleShakingThreshold * 100f).ToString("0") + "% removed");
            greatboleShakingThreshold = list.Slider(greatboleShakingThreshold, 0.1f, 0.9f);
            list.Label("  The violent healing: " + (greatboleHealingThreshold * 100f).ToString("0") + "% removed");
            greatboleHealingThreshold = list.Slider(greatboleHealingThreshold, 0.1f, 0.95f);
            list.CheckboxLabeled("  The catastrophe can happen", ref greatboleCatastropheEnabled,
                "Off: a greatbole never dies from being mined out, no matter how much of its footprint is removed. "
              + "The Great Shaking and the violent healing still fire.");
            if (greatboleCatastropheEnabled)
            {
                list.Label("  The catastrophe: " + (greatboleCatastropheThreshold * 100f).ToString("0") + "% removed");
                greatboleCatastropheThreshold = list.Slider(greatboleCatastropheThreshold, 0.1f, 0.99f);
            }
            list.CheckboxLabeled("Greatbole seeds can be planted (next game start)", ref greatboleSeedPlantingEnabled,
                "On: a greatbole seed can be planted like a Gauranlen seed. A planted greatbole grows only with open "
              + "water in a neighbouring cell, and then grows far faster than any other tree; its inspect pane says "
              + "which. Off: seeds are trade goods only, and any already-planted greatbole grows at the ordinary "
              + "rate with no water rule. Takes effect the next time the game starts.");
            list.CheckboxLabeled("Opt-in: greatbole servants (dryads) (next game start)", ref greatboleServantsEnabled,
                "Changes the tree's character — default off, and the Utinni campaign ships with it off. On: the "
              + "living heart of a greatbole works like a Gauranlen tree. A colonist can connect to it (stand in the "
              + "mined-open cell just west of the heart) and direct its dryads; colony buildings near it do NOT "
              + "weaken the connection. Expected: its dryads will fight the fruit's grubs, which stay hostile in "
              + "every configuration. Takes effect the next time the game starts.");
            list.Label("Breaklight, the dry-air blower's field, living greatbole placement and "
              + "root causeways are switched in the Environmental Hazards Kit's settings.");

            lastContentHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_GreentideMod : Mod
    {
        public static RM_GreentideSettings settings;

        public RM_GreentideMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_GreentideSettings>();
            RimMandrake.EnvironmentalHazards.RM_MechanicGates.Register(
                RM_StellockLace.GateKey, () => RM_GreentideSettings.stellockLaceEnabled);
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
            RM_ThurrockAuraApplier.Apply();
        }
    }
}
