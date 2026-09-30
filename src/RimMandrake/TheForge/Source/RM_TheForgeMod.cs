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
