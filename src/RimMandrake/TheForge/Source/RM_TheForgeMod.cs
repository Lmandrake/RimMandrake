using UnityEngine;
using Verse;

namespace RimMandrake.TheForge
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 / §6a of THEFORGE_RM_MOD_BUILD_1 — Mod Settings
    // for The Forge. Pattern copied from RM_TheRotSettings
    // (src/RimMandrake/TheRot/Source/RM_TheRotMod.cs): static fields read
    // from everywhere, Scribe_Values in ExposeData, a DoWindowContents helper
    // called from the Mod subclass. Defaults = shipped behavior throughout.
    //
    // Wired: modEnabled, weatherPulseEnabled (via the RM_MechanicGates key
    // "TheForge.Pulse" on RM_ForgePulse) and every grand-cycle toggle
    // (FORGE_CYCLE_MECHANICS_1). ⚠️ Still scaffolding, same honest scope as
    // RM_TheRotSettings: tibannaTapRate, vaporColumnImmunity,
    // towerScatterCount, dieOffRingDensity and ventWorkSpeedBonus are
    // declared and shown but change nothing yet — FORGE_MECHANICS_1's own
    // remaining work.
    // ════════════════════════════════════════════════════════════════════
    public class RM_TheForgeSettings : ModSettings
    {
        // Master switch: turns this mod's OWN settings-driven behaviour off
        // without touching the biome def — the massif, its plants and its
        // animals keep loading and playing exactly as before either way
        // (biome_mod_architecture.md §6c, "all-off degrades gracefully").
        public static bool modEnabled = true;

        public static bool weatherPulseEnabled = true;
        public static float tibannaTapRate = 1f;
        public static bool vaporColumnImmunity = true;
        public static int towerScatterCount = 1;
        public static float dieOffRingDensity = 1f;
        public static float ventWorkSpeedBonus = 1.2f;

        // FORGE_CYCLE_MECHANICS_1 — the six-phase grand cycle. All live:
        // each is read on the tick it matters, so flipping one takes effect
        // at once and flipping it back loses nothing.
        public static bool grandCycleEnabled = true;
        public static bool gasWashEnabled = true;
        public static bool cycleFloodingEnabled = true;
        public static bool lavaFreezeEnabled = true;
        public static bool meltBackDestroys = true;
        public static bool floatstoneBloomEnabled = true;
        public static bool cycleDormancyEnabled = true;
        public static bool cycleTelegraphLetters = true;

        // FORGE_GPT_ENRICHMENT_1 — the owner-picked enrichments. Each is read
        // live, so flipping one takes effect at once.
        public static bool keelworkEnabled = true;
        public static bool keelRingEnabled = true;
        public static bool spunstoneStudyEnabled = true;
        public static bool forgeVoicesEnabled = true;
        public static bool forgeVoicesVisualCues = false;
        public static bool dhuvvoxClockEnabled = true;
        public static bool dhuvvoxRunSoundEnabled = true;

        // FORGE_WHITE_PLUME_FRONTS_1 — quench-steam fronts off the new crust, each half separately switchable.
        public static bool plumeFrontsEnabled = true;
        public static bool plumeObscureEnabled = true;
        public static bool plumeSoakEnabled = true;
        public static bool plumeHeatEnabled = true;
        public static bool plumeAdaptedExempt = true;
        public static float plumeStrength = 1f;

        // FORGE_SKY_PASTURES_1 — the vapour-column pastures. Each is read live.
        public static bool skyColumnGridEnabled = true;
        public static bool skyAshSpiralsEnabled = true;
        public static bool skyColumnHuntEnabled = true;
        public static bool jossurStoopEnabled = true;
        public static bool skyColumnHighlightEnabled = true;

        // Master switch folded in: a feature is on only while the mod is.
        private static Vector2 scrollPos;
        private static float viewHeight = 900f;

        public static bool Active(bool feature)
        {
            return modEnabled && feature;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref modEnabled, "modEnabled", true, true);
            Scribe_Values.Look(ref weatherPulseEnabled, "weatherPulseEnabled", true);
            Scribe_Values.Look(ref tibannaTapRate, "tibannaTapRate", 1f);
            Scribe_Values.Look(ref vaporColumnImmunity, "vaporColumnImmunity", true);
            Scribe_Values.Look(ref towerScatterCount, "towerScatterCount", 1);
            Scribe_Values.Look(ref dieOffRingDensity, "dieOffRingDensity", 1f);
            Scribe_Values.Look(ref ventWorkSpeedBonus, "ventWorkSpeedBonus", 1.2f);
            Scribe_Values.Look(ref grandCycleEnabled, "grandCycleEnabled", true);
            Scribe_Values.Look(ref gasWashEnabled, "gasWashEnabled", true);
            Scribe_Values.Look(ref cycleFloodingEnabled, "cycleFloodingEnabled", true);
            Scribe_Values.Look(ref lavaFreezeEnabled, "lavaFreezeEnabled", true);
            Scribe_Values.Look(ref meltBackDestroys, "meltBackDestroys", true);
            Scribe_Values.Look(ref floatstoneBloomEnabled, "floatstoneBloomEnabled", true);
            Scribe_Values.Look(ref cycleDormancyEnabled, "cycleDormancyEnabled", true);
            Scribe_Values.Look(ref cycleTelegraphLetters, "cycleTelegraphLetters", true);
            Scribe_Values.Look(ref keelworkEnabled, "keelworkEnabled", true);
            Scribe_Values.Look(ref keelRingEnabled, "keelRingEnabled", true);
            Scribe_Values.Look(ref spunstoneStudyEnabled, "spunstoneStudyEnabled", true);
            Scribe_Values.Look(ref forgeVoicesEnabled, "forgeVoicesEnabled", true);
            Scribe_Values.Look(ref forgeVoicesVisualCues, "forgeVoicesVisualCues", false);
            Scribe_Values.Look(ref dhuvvoxClockEnabled, "dhuvvoxClockEnabled", true);
            Scribe_Values.Look(ref dhuvvoxRunSoundEnabled, "dhuvvoxRunSoundEnabled", true);
            Scribe_Values.Look(ref plumeFrontsEnabled, "plumeFrontsEnabled", true);
            Scribe_Values.Look(ref plumeObscureEnabled, "plumeObscureEnabled", true);
            Scribe_Values.Look(ref plumeSoakEnabled, "plumeSoakEnabled", true);
            Scribe_Values.Look(ref plumeHeatEnabled, "plumeHeatEnabled", true);
            Scribe_Values.Look(ref plumeAdaptedExempt, "plumeAdaptedExempt", true);
            Scribe_Values.Look(ref plumeStrength, "plumeStrength", 1f);
            Scribe_Values.Look(ref skyColumnGridEnabled, "skyColumnGridEnabled", true);
            Scribe_Values.Look(ref skyAshSpiralsEnabled, "skyAshSpiralsEnabled", true);
            Scribe_Values.Look(ref skyColumnHuntEnabled, "skyColumnHuntEnabled", true);
            Scribe_Values.Look(ref jossurStoopEnabled, "jossurStoopEnabled", true);
            Scribe_Values.Look(ref skyColumnHighlightEnabled, "skyColumnHighlightEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls: the grand-cycle rows made the list taller than the
            // default settings window.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, viewHeight);
            Widgets.BeginScrollView(inRect, ref scrollPos, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width };
            list.Begin(viewRect);

            list.CheckboxLabeled("The Forge enabled", ref modEnabled,
                "Master switch. Off: the biome and its defs still load unchanged, but every "
              + "per-feature toggle below is ignored as off.");
            list.GapLine();

            list.CheckboxLabeled("Weather-pulse bursts", ref weatherPulseEnabled,
                "The closed boiling-rain cycle: long still heat broken by sudden scalding "
              + "bursts, with a flash-growth window after each one. Off: the Forge keeps its "
              + "own weather and no burst, scald or flash window happens.");
            list.GapLine();

            list.CheckboxLabeled("Grand cycle (fire and water)", ref grandCycleEnabled,
                "Stretches the pulse into six phases: still heat, a gas wash that sets the "
              + "map alight, torrential boiling rain with flooding, the freeze (lava crusts "
              + "over into basalt and pumice), the growth (floatstone gardens bloom on the "
              + "crust), then glowing cracks and the melt-back. Off: plain random pulses "
              + "only; any crust still standing melts back gently, harming nothing.");
            list.CheckboxLabeled("  Gas wash ignites the map", ref gasWashEnabled,
                "Phase 2: superheated gas bursts set flammable ground alight in swathes.");
            list.CheckboxLabeled("  Boiling-rain flooding", ref cycleFloodingEnabled,
                "Phase 3: the torrential rain releases standing water floods (FlowWorks).");
            list.CheckboxLabeled("  Lava freezes into walkable crust", ref lavaFreezeEnabled,
                "Phase 4: open lava crusts over into temporary basalt shingle and pumice.");
            list.CheckboxLabeled("  Melt-back destroys what stands on the crust", ref meltBackDestroys,
                "Phase 6: when the crust melts, things on it burn and are destroyed and "
              + "pawns are badly burned. Off: they are moved to safe ground instead.");
            list.CheckboxLabeled("  Floatstone gardens bloom on the crust", ref floatstoneBloomEnabled,
                "Phase 5: floatstone gardens grow on the frozen crust; unharvested ones "
              + "tear free and drift away when the cracks appear.");
            list.CheckboxLabeled("  Creatures sleep through the dry phases", ref cycleDormancyEnabled,
                "The dhokkur stands up only in the boiling rain; the julmox and the dhuvvox "
              + "stay sealed until the rain and its growth window. Off: all stay awake.");
            list.CheckboxLabeled("  Warning letters", ref cycleTelegraphLetters,
                "Letters before the gas wash (the hiss), at the glowing cracks and at the "
              + "melt. Off: the phases still happen, unannounced.");
            list.GapLine();

            list.CheckboxLabeled("Floatstone keelwork", ref keelworkEnabled,
                "Floatstone keel braces linked to a grav engine cut the gravship's fuel use. "
              + "Off: braces still build and stand, but save no fuel.");
            list.CheckboxLabeled("  Keel braces ring at launch", ref keelRingEnabled,
                "Each keel brace linked to the grav engine rings once, glassily, as the gravship "
              + "launches. Off: the braces launch silently.");
            list.CheckboxLabeled("Spunstone bonding is learned in the Forge", ref spunstoneStudyEnabled,
                "The spunstone bonding research stays hidden until colonists have studied "
              + "enough mature floatstone gardens. Off: the project is visible and "
              + "researchable from the start, and gardens are not studied.");
            list.CheckboxLabeled("Four voices of the Forge", ref forgeVoicesEnabled,
                "Each phase of the grand cycle has its own sound: a turbine throb in the still "
              + "heat, coughing vents in the gas wash, a hiss under the boiling rain, ticking "
              + "glass as the basalt cools, and a deep cracking pulse before the melt.");
            list.CheckboxLabeled("  Visual cues for the voices", ref forgeVoicesVisualCues,
                "Show a message naming each phase's sound as it begins. Always on while the "
              + "game or ambient volume is muted.");
            list.CheckboxLabeled("The dhuvvox clock", ref dhuvvoxClockEnabled,
                "Awake dhuvvox show how long their run has left, slow in its final "
              + "quarter-hour, and visibly curl back into their nodules when it ends. "
              + "Off: they still seal on the cycle, without the clock.");
            list.CheckboxLabeled("  Scuttling sound", ref dhuvvoxRunSoundEnabled,
                "Awake dhuvvox tick and scuttle where they run; the ticks space out and fade as the "
              + "run's final quarter-hour passes. Needs the dhuvvox clock.");
            list.GapLine();

            list.CheckboxLabeled("White plume fronts", ref plumeFrontsEnabled,
                "During the freeze, quench steam rolls off newly crusted ground in moving white fronts. "
              + "Off: no fronts form (the freeze itself is unchanged).");
            list.CheckboxLabeled("  Plumes blind shooters", ref plumeObscureEnabled,
                "Fronts lay vanilla blind smoke, which cuts ranged accuracy and stops targets being picked through it.");
            list.CheckboxLabeled("  Plumes soak the ground", ref plumeSoakEnabled,
                "Fronts leave water puddles, which evaporate within hours and do not burn.");
            list.CheckboxLabeled("  Plumes raise heat", ref plumeHeatEnabled,
                "Pawns inside a front feel hotter air, so vanilla heatstroke sets in faster. No new condition is added.");
            list.CheckboxLabeled("  Vapour-adapted creatures are exempt", ref plumeAdaptedExempt,
                "Creatures that live in the vapour columns take no extra heat from a front.");
            list.Label("Plume strength: " + plumeStrength.ToString("0.00") + "x");
            plumeStrength = list.Slider(plumeStrength, 0.25f, 2f);
            list.GapLine();

            list.CheckboxLabeled("Vapour-column haze", ref skyColumnGridEnabled,
                "A faint haze, brighter at the rim, marks the ground under each vapour column where the sky creatures graze.");
            list.CheckboxLabeled("  Ash spirals in the columns", ref skyAshSpiralsEnabled,
                "Ash flecks wind upward inside the vapour columns near the camera. Cosmetic only.");
            list.CheckboxLabeled("  Column-aware hunting", ref skyColumnHuntEnabled,
                "Predators that live in the columns prefer prey inside them and ignore prey far out on the open ash.");
            list.CheckboxLabeled("  Jossur stoops", ref jossurStoopEnabled,
                "A hunting jossur takes to the air when its prey is a way off and closes in on the wing.");
            list.CheckboxLabeled("  Selecting a sky creature lights up its columns", ref skyColumnHighlightEnabled,
                "While a column-bound flier is selected, the columns it can reach are outlined. Nothing is shown otherwise.");
            list.GapLine();
            list.Label("Tibanna-tap rate: " + tibannaTapRate.ToString("0.00") + "x");
            tibannaTapRate = list.Slider(tibannaTapRate, 0.25f, 3f);
            list.CheckboxLabeled("Vapor-column immunity", ref vaporColumnImmunity,
                "Sky fauna drifting in the vent columns are immune to ground heat hazards "
              + "while aloft.");
            list.Label("Foundry tower scatter count: " + towerScatterCount);
            towerScatterCount = (int)list.Slider(towerScatterCount, 0f, 3f);
            list.Label("Die-off ring density: " + dieOffRingDensity.ToString("0.00") + "x");
            dieOffRingDensity = list.Slider(dieOffRingDensity, 0f, 3f);
            list.Label("Vent work-speed bonus: " + ventWorkSpeedBonus.ToString("0.00") + "x");
            ventWorkSpeedBonus = list.Slider(ventWorkSpeedBonus, 1f, 2f);

            viewHeight = Mathf.Max(inRect.height, list.CurHeight + 12f);
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_TheForgeMod : Mod
    {
        public static RM_TheForgeSettings settings;

        public RM_TheForgeMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_TheForgeSettings>();
            // FORGE_CYCLE_MECHANICS_1: the pulse's C# lives in the shared
            // EnvironmentalHazards assembly; RM_ForgePulse carries
            // RM_MechanicGateExtension gateKey "TheForge.Pulse", so this is
            // what makes the "Weather-pulse bursts" toggle real.
            RimMandrake.EnvironmentalHazards.RM_MechanicGates.Register(
                "TheForge.Pulse",
                () => RM_TheForgeSettings.Active(RM_TheForgeSettings.weatherPulseEnabled));
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            // FORGE_GPT_ENRICHMENT_1: the keelwork toggle rewrites the brace's
            // vanilla fuel-savings number, so it must re-apply on every save.
            RM_KeelworkUtility.ApplySetting();
        }

        public override string SettingsCategory()
        {
            return "The Forge";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
