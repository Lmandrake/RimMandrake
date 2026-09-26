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
    // ⚠️ Same honest scope as RM_TheRotSettings: the five per-mechanic
    // toggles below (F1 weather-pulse bursts already lives as
    // RM_EnvironmentalHazardsSettings.weatherPulseEnabled in the shared
    // assembly; F2-F6's own C#/XML remain FORGE_MECHANICS_1's, still `doing`)
    // are declared, exposed and shown in THIS screen as the per-biome front
    // §6a asks for, but are NOT yet wired to change behaviour — that
    // consolidation is FORGE_MECHANICS_1's own remaining work, not this
    // build. Toggling one below is scaffolding today, not a behavior change.
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
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("The Forge enabled", ref modEnabled,
                "Master switch. Off: the biome and its defs still load unchanged, but every "
              + "per-feature toggle below is ignored as off.");
            list.GapLine();

            list.CheckboxLabeled("Weather-pulse bursts", ref weatherPulseEnabled,
                "The closed boiling-rain cycle: long still heat broken by sudden scalding "
              + "bursts, with a flash-growth window after each one.");
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

            list.End();
        }
    }

    public class RM_TheForgeMod : Mod
    {
        public static RM_TheForgeSettings settings;

        public RM_TheForgeMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_TheForgeSettings>();
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
