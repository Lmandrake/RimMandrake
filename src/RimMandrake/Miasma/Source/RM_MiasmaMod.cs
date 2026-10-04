using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Miasma
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Miasma.
    //
    // Precedent: src/RimMandrake/PoisonForest/Source/RM_PoisonForestMod.cs
    // (the worldgen-rarity slider, since this biome ships a real
    // RM_BiomeWorker_Miasma of its own) and
    // src/RimMandrake/NightsideIce/Source/RM_NightsideIceMod.cs (the
    // honest-about-scope reasoning below).
    //
    // This mod ships six real mechanics (gradient axis, breath-tide surge,
    // stranding pools, weather lock + exposure, fever-forged boons, warden/
    // crèche placement), but every one of them is implemented by classes in
    // the SHARED mandrake.rm.environmentalhazards assembly, gated by THAT
    // mod's own static toggles (RM_EnvironmentalHazardsSettings) —
    // strandingPoolsEnabled, wardenCrecheScattererEnabled,
    // crecheDespoilMemoryEnabled and biomeGlowMultiplierEnabled are already
    // shared with Greentide and Sump (both also carry
    // RM_StrandingPoolsExtension). Duplicating a Miasma-only copy of any of
    // those switches here would either do nothing (the shared class only
    // ever reads the shared statics) or silently diverge from what that
    // mod's own settings screen already promises a player. So this screen
    // ships only the standard worldgen-rarity slider every biome-worker mod
    // ships, plus an honest pointer to where the mechanic toggles actually
    // live — a per-mechanic toggle for content this screen does not itself
    // gate would be a settings screen that lies (NightsideIce's own
    // reasoning, same shape here).
    //
    // STATIC FIELD, read from the biome worker which runs during worldgen
    // with no Mod instance handy — same pattern as every sibling.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MiasmaSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new planet.
        // 1 = the shipped default.
        public static float biomeRarityFactor = 1f;

        // WARDEN_MOTHER_SUCCESSION_1: unlike the six mechanics above, self-
        // taming/water-scoped training/succession is implemented entirely in
        // THIS mod's own assembly (RM_WardenMotherSuccession.cs) — no shared
        // EnvironmentalHazards switch to point at instead, so it belongs on
        // this screen. Default = shipped behavior; off degrades gracefully
        // (the young simply stay wild and the crèche is never inherited).
        public static bool wardenSuccessionEnabled = true;
        public static float selfTameChancePerCheck = 0.12f;

        // MIASMA_SETTINGS_SWITCHES_1. Defaults = shipped behaviour; each off degrades to
        // "the mechanic simply does not fire".
        // Plant predation: RM_CompPlantPredator.CompTickLong returns early.
        public static bool plantPredationEnabled = true;
        // Pollination gate: the RM_PollinationGateExtension on the Miasma's mangals is
        // detached from the defs (RM_MiasmaSettingsApplier), so the shared patch never gates them.
        public static bool pollinationGateEnabled = true;
        // Stranded deformation: the stranding-pool roll's chance on the Miasma BiomeDef is
        // set to 0 when off, else to the slider (shipped 0.25).
        public static bool strandedDeformationEnabled = true;
        public static float strandedDeformationChance = 0.25f;
        // MIASMA_AMBUSH_FROG_REMAKE_1: the bozzuga hunts scuttlers and stranded young (race.predator).
        public static bool ambushFrogHunts = true;
        // MIASMA_ATTAR_STILL_1: the attar still's recipe, glazing artworks and balming scars.
        public static bool attarEnabled = true;

        // MIASMA_FLOTSAM_YARD_1: river goods washed into the root-lines at map start and after each surge recede.
        // MIASMA_YOUNG_CALL_1: the stranded young's cry, the first-cry letter, and the warden mother heading for it.
        public static bool youngCallEnabled = true;

        public static bool flotsamEnabled = true;
        public static float flotsamAmount = 1f;

        // MIASMA_DECAY_CELLS_1: the old meter appears on Miasma maps, and built decay cells make power.
        public static bool decayCellsEnabled = true;
        public static float decayCellPowerMultiplier = 1f;
        // MIASMA_ROTTING_BED_CORPSES_1: a rotting bed rots stored corpses down to bones and skulls.
        public static bool rottingBedCorpsesEnabled = true;
        public static float rottingBedRotDays = 3f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref youngCallEnabled, "youngCallEnabled", true, true);
            Scribe_Values.Look(ref flotsamEnabled, "flotsamEnabled", true, true);
            Scribe_Values.Look(ref flotsamAmount, "flotsamAmount", 1f, true);
            Scribe_Values.Look(ref decayCellsEnabled, "decayCellsEnabled", true, true);
            Scribe_Values.Look(ref decayCellPowerMultiplier, "decayCellPowerMultiplier", 1f, true);
            Scribe_Values.Look(ref rottingBedCorpsesEnabled, "rottingBedCorpsesEnabled", true, true);
            Scribe_Values.Look(ref rottingBedRotDays, "rottingBedRotDays", 3f, true);
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref wardenSuccessionEnabled, "wardenSuccessionEnabled", true, true);
            Scribe_Values.Look(ref selfTameChancePerCheck, "selfTameChancePerCheck", 0.12f, true);
            Scribe_Values.Look(ref plantPredationEnabled, "plantPredationEnabled", true, true);
            Scribe_Values.Look(ref pollinationGateEnabled, "pollinationGateEnabled", true, true);
            Scribe_Values.Look(ref strandedDeformationEnabled, "strandedDeformationEnabled", true, true);
            Scribe_Values.Look(ref strandedDeformationChance, "strandedDeformationChance", 0.25f, true);
            Scribe_Values.Look(ref ambushFrogHunts, "ambushFrogHunts", true, true);
            Scribe_Values.Look(ref attarEnabled, "attarEnabled", true, true);
        }

        private static Vector2 scroll;
        private static float viewHeight = 1400f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, viewHeight);
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width };
            list.Begin(view);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 the Miasma never generates on a new planet. The default "
                       + "places a scattering of hot, salt-crusted delta forest along "
                       + "rivers. Affects planets generated afterwards, never one that "
                       + "already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
            list.GapLine();

            list.Label("This biome's own mechanics — the salinity gradient, the "
                      + "breath-tide surge, stranding pools, the weather lock and "
                      + "exposure hediff, fever-forged boons, and warden/crèche "
                      + "placement — are togglable per-mechanic in the shared "
                      + "\"RimMandrake: Environmental Hazards Kit\" mod's own settings "
                      + "screen, not here: Greentide and Sump read those exact same "
                      + "switches, so a second, Miasma-only copy of them on this "
                      + "screen would either do nothing or quietly disagree with that "
                      + "one.");
            list.GapLine();

            list.CheckboxLabeled("Warden mother young: self-taming and succession",
                ref wardenSuccessionEnabled,
                "A stranded young may quietly self-tame if the player never harms one "
                + "of its crèche-mates, becomes trainable for water-bound work only, "
                + "and can inherit the crèche if the mother dies of old age. Off: the "
                + "young stay wild and the crèche is never inherited.");
            if (wardenSuccessionEnabled)
            {
                list.Label("  Self-tame chance per check: " + (selfTameChancePerCheck * 100f).ToString("0") + "%");
                selfTameChancePerCheck = list.Slider(selfTameChancePerCheck, 0.01f, 0.5f);
            }

            list.GapLine();
            list.CheckboxLabeled("Predatory plants feed on wild scuttlers",
                ref plantPredationEnabled,
                "The Miasma's carnivorous plants kill wild, unfactioned scuttlers that wander "
                + "within reach. Off: they never hunt.");
            list.CheckboxLabeled("Pollination gate on the mangals",
                ref pollinationGateEnabled,
                "The Miasma's mangals only grow where their pollinator swarm lives. Off: they grow "
                + "wherever the terrain allows. Takes effect after the settings window closes.");
            list.CheckboxLabeled("Stranded deformation",
                ref strandedDeformationEnabled,
                "Some creatures stranded in a drying pool are born deformed and do not thrive. "
                + "Off: none are.");
            if (strandedDeformationEnabled)
            {
                list.Label("  Chance per stranded creature: " + (strandedDeformationChance * 100f).ToString("0") + "%");
                strandedDeformationChance = list.Slider(strandedDeformationChance, 0.01f, 1f);
            }

            list.GapLine();
            list.CheckboxLabeled("Bozzuga hunts",
                ref ambushFrogHunts,
                "The bozzuga, the root-maze's ambush frog, lies in wait and eats scuttlers and stranded young. "
                + "Off: it is a placid animal that hunts nothing.");

            list.GapLine();
            list.CheckboxLabeled("Stranded young call",
                ref youngCallEnabled,
                "A stranded young cries out, a letter points at the first one, and the warden mother lumbers toward "
                + "it through the water, never onto dry land. Off: the young are silent and the mother ignores them. "
                + "Takes effect after the settings window closes.");

            list.GapLine();
            list.CheckboxLabeled("Flotsam in the root-lines",
                ref flotsamEnabled,
                "River goods (scrap steel, wood, cloth, the odd component) wash into the roots at the start of "
                + "a Miasma map and again after every surge recedes. Off: none arrives.");
            if (flotsamEnabled)
            {
                list.Label("  Amount: " + flotsamAmount.ToString("0.0") + "x");
                flotsamAmount = list.Slider(flotsamAmount, 0.25f, 3f);
            }

            list.GapLine();
            list.CheckboxLabeled("Attar: still, glaze and balm",
                ref attarEnabled,
                "Delta silt and salt refine into attar at the attar still. Glazing raises an artwork's beauty; balm "
                + "fades one scar and heals nothing else. Off: the still's recipe is hidden and glaze and balm cannot "
                + "be used (glazed artworks lose the bonus). Attar already made stays in the world.");

            list.GapLine();
            list.CheckboxLabeled("Decay cells: power from rot",
                ref decayCellsEnabled,
                "An old meter still reading current lies in a compost bed on each new Miasma map; analyzing it unlocks "
                + "the decay cell research. A built cell fed rotting goods makes power, less as the feed runs down, and "
                + "a cell that has digested its lifetime of feed becomes a rotting bed. Off: no meter is placed and "
                + "cells make no power (built ones stay).");
            if (decayCellsEnabled)
            {
                list.Label("  Power: " + decayCellPowerMultiplier.ToStringPercent());
                decayCellPowerMultiplier = list.Slider(decayCellPowerMultiplier, 0.25f, 2f);
            }

            list.GapLine();
            list.CheckboxLabeled("Rotting bed: corpse disposal",
                ref rottingBedCorpsesEnabled,
                "A spent decay cell's rotting bed takes corpses as storage, one per cell, and rots them down one at a "
                + "time: the body is consumed, its gear drops beside the bed, and it leaves bones and, for a person "
                + "with a head, a skull that names whose it was. Off: the bed still holds corpses but nothing rots down.");
            if (rottingBedCorpsesEnabled)
            {
                list.Label("  Rot-down time: " + rottingBedRotDays.ToString("0.0") + " days per corpse");
                rottingBedRotDays = list.Slider(rottingBedRotDays, 0.5f, 10f);
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }

        private static string RarityLabel()
        {
            if (biomeRarityFactor <= 0.001f) return "never generates";
            if (biomeRarityFactor < 0.6f) return "very rare (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 1.6f) return "default, a handful of patches (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 4f) return "uncommon (" + biomeRarityFactor.ToString("0.0") + "x)";
            return "common (" + biomeRarityFactor.ToString("0.0") + "x)";
        }
    }

    // Applies the two switches that live in the SHARED environmental-hazards assembly by editing the
    // Miasma's own defs (this assembly does not reference that one, so it works by reflection and
    // fails soft with a warning). Called at startup and whenever the settings window closes.
    [StaticConstructorOnStartup]
    public static class RM_MiasmaSettingsApplier
    {
        public static readonly string[] GatedPlants = { "RM_Thessamor", "RM_Quennath" };
        private static readonly System.Collections.Generic.Dictionary<string, DefModExtension> stashed =
            new System.Collections.Generic.Dictionary<string, DefModExtension>();

        static RM_MiasmaSettingsApplier()
        {
            Apply();
        }

        public static void Apply()
        {
            try
            {
                ApplyDeformation();
                ApplyPollinationGate();
                ApplyAttar();
                ApplyYoungCall();
            }
            catch (System.Exception e)
            {
                Log.Warning("[RM Miasma] settings applier failed, defs left as shipped: " + e.Message);
            }
        }

        // The cry lives in the shared assembly's hediff comp props (read by reflection; the comp returns early
        // when callSound is null). Props are shared by every hediff instance, so this reaches existing young too.
        private static SoundDef stashedCall;

        private static void ApplyYoungCall()
        {
            HediffDef hd = DefDatabase<HediffDef>.GetNamedSilentFail("RUT_StrandedDeformation");
            if (hd == null || hd.comps == null) return;
            foreach (HediffCompProperties cp in hd.comps)
            {
                System.Reflection.FieldInfo f = cp.GetType().GetField("callSound");
                if (f == null) continue;
                if (RM_MiasmaSettings.youngCallEnabled)
                {
                    if (stashedCall != null && f.GetValue(cp) == null) f.SetValue(cp, stashedCall);
                }
                else
                {
                    if (f.GetValue(cp) is SoundDef sd) stashedCall = sd;
                    f.SetValue(cp, null);
                }
            }
        }

        // Hides/shows the attar recipe on its still. ThingDef.allRecipesCached is private, so reset by reflection.
        private static void ApplyAttar()
        {
            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail("RM_MakeAttar");
            ThingDef bench = DefDatabase<ThingDef>.GetNamedSilentFail("RM_AttarStill");
            if (recipe == null || bench == null) return;
            if (recipe.recipeUsers == null) recipe.recipeUsers = new System.Collections.Generic.List<ThingDef>();
            if (RM_MiasmaSettings.attarEnabled) { if (!recipe.recipeUsers.Contains(bench)) recipe.recipeUsers.Add(bench); }
            else recipe.recipeUsers.Remove(bench);
            typeof(ThingDef).GetField("allRecipesCached", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                ?.SetValue(bench, null);
        }

        private static void ApplyDeformation()
        {
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Miasma");
            if (biome == null || biome.modExtensions == null) return;
            foreach (DefModExtension ext in biome.modExtensions)
            {
                System.Reflection.FieldInfo f = ext.GetType().GetField("strandedDeformationChance");
                if (f == null) continue;
                f.SetValue(ext, RM_MiasmaSettings.strandedDeformationEnabled
                    ? RM_MiasmaSettings.strandedDeformationChance : 0f);
            }
        }

        private static void ApplyPollinationGate()
        {
            foreach (string name in GatedPlants)
            {
                ThingDef plant = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (plant == null) continue;
                if (!RM_MiasmaSettings.pollinationGateEnabled)
                {
                    if (plant.modExtensions == null) continue;
                    for (int i = plant.modExtensions.Count - 1; i >= 0; i--)
                    {
                        if (plant.modExtensions[i].GetType().Name == "RM_PollinationGateExtension")
                        {
                            stashed[name] = plant.modExtensions[i];
                            plant.modExtensions.RemoveAt(i);
                        }
                    }
                }
                else if (stashed.TryGetValue(name, out DefModExtension ext))
                {
                    if (plant.modExtensions == null) plant.modExtensions = new System.Collections.Generic.List<DefModExtension>();
                    plant.modExtensions.Add(ext);
                    stashed.Remove(name);
                }
            }
        }
    }

    public class RM_MiasmaMod : Mod
    {
        public static RM_MiasmaSettings settings;

        public RM_MiasmaMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_MiasmaSettings>();
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            RM_MiasmaSettingsApplier.Apply();
            RM_AmbushFrogHunting.Apply();
        }

        public override string SettingsCategory()
        {
            return "the Miasma";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
