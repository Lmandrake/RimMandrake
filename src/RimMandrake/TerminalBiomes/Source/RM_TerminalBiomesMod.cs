using System.Runtime.CompilerServices;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Terminal Biomes.
    //
    // TERMINALBIOMES_RM_MOD_BUILD_1 §11 step 1: five toggles (master + one
    // per biome, all default ON), plus one sub-toggle per Scald mechanic the
    // kit spec names (S1/S2/S4/S5/S6 — S3 is unbuilt, so it gets no toggle),
    // plus a cross-biome block matching Greentide's own shape.
    //
    // The five Scald sub-toggles are LIVE. Each is read as
    // masterEnabled && scaldEnabled && its own flag (the Scald*Active
    // properties below) and reaches its mechanic one of two ways:
    //   - Mechanics whose C# lives in the SHARED mandrake.rm.environmental
    //     hazards assembly (it serves Greentide/Forge/Scald alike and loads
    //     BEFORE this mod, so it cannot reference us): the constructor
    //     registers each toggle as a key in that assembly's RM_MechanicGates,
    //     and the Scald's own defs carry an RM_MechanicGateExtension naming
    //     the key. Only defs carrying the extension are gated; every other
    //     biome's use of the same classes is untouched.
    //       Scald.S1 -> RUT_ScaldSteamLock (RM_GameCondition_WeatherPulse)
    //       Scald.S2 -> RUT_SteamCatch (RM_CompResourceCondenser)
    //       Scald.S4 -> RUT_ScaldVent, as the condenser sees it
    //       Scald.S5 -> RUT_WalkerSurfacing, RUT_GenStep_ScaldSailScatterer
    //   - Mechanics whose engine class was vanilla (the vent's
    //     Building_SteamGeyser, the wrecks' GenStep_ScatterThings): thin
    //     subclasses in RM_TerminalBiomesScaldKit.cs read these settings
    //     directly.
    // Every gate acts at its comp/condition/incident/GenStep entry point,
    // never by removing a def, so a flip takes effect on the next tick (or,
    // for the two scatter GenSteps, on the next NEW map) and flipping back
    // restores the mechanic. The shared assembly is loadAfter, not a hard
    // dependency: registration is skipped when it is not active.
    //
    // The per-biome toggles are narrower: nothing on the world is painted
    // to any RM_* biome yet (BIOME_PAINT_ONCE_AT_THE_END_1 — the planet
    // repaints once, at the end), so "biome off" cannot remove a biome from
    // a generated planet. scaldEnabled does switch off the whole Scald kit
    // (via the Active properties); the other three biome toggles are
    // persisted state with no consumer yet.
    // ════════════════════════════════════════════════════════════════════
    public class RM_TerminalBiomesSettings : ModSettings
    {
        // ── Master ───────────────────────────────────────────────────────
        public static bool masterEnabled = true;

        // ── Per-biome (§7 Q1: four independent toggles) ─────────────────
        public static bool scaldEnabled = true;
        public static bool propaneLakeEnabled = true;
        public static bool twilightSeaEnabled = true;
        public static bool greySeaEnabled = true;

        // ── Scald mechanic sub-toggles (kit spec S1/S2/S4/S5/S6; S3 unbuilt) ─
        public static bool scaldS1SteamSkyEnabled = true;
        public static bool scaldS2SteamCatchEnabled = true;
        public static bool scaldS4VentFieldsEnabled = true;
        public static bool scaldS5SailWalkerEnabled = true;
        public static bool scaldS6WreckSalvageEnabled = true;

        // Effective state: a sub-toggle only counts while the mod and the
        // Scald are both on. Everything that gates reads these, never the
        // raw fields.
        private static bool ScaldActive => masterEnabled && scaldEnabled;
        public static bool ScaldS1SteamSkyActive => ScaldActive && scaldS1SteamSkyEnabled;
        public static bool ScaldS2SteamCatchActive => ScaldActive && scaldS2SteamCatchEnabled;
        public static bool ScaldS4VentFieldsActive => ScaldActive && scaldS4VentFieldsEnabled;
        public static bool ScaldS5SailWalkerActive => ScaldActive && scaldS5SailWalkerEnabled;
        public static bool ScaldS6WreckSalvageActive => ScaldActive && scaldS6WreckSalvageEnabled;

        // ── Cross-biome opt-in (Greentide's own shape; WORLDGEN-AFFECTING) ─
        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;

        private string biomeListBuffer;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref scaldEnabled, "scaldEnabled", true);
            Scribe_Values.Look(ref propaneLakeEnabled, "propaneLakeEnabled", true);
            Scribe_Values.Look(ref twilightSeaEnabled, "twilightSeaEnabled", true);
            Scribe_Values.Look(ref greySeaEnabled, "greySeaEnabled", true);
            Scribe_Values.Look(ref scaldS1SteamSkyEnabled, "scaldS1SteamSkyEnabled", true);
            Scribe_Values.Look(ref scaldS2SteamCatchEnabled, "scaldS2SteamCatchEnabled", true);
            Scribe_Values.Look(ref scaldS4VentFieldsEnabled, "scaldS4VentFieldsEnabled", true);
            Scribe_Values.Look(ref scaldS5SailWalkerEnabled, "scaldS5SailWalkerEnabled", true);
            Scribe_Values.Look(ref scaldS6WreckSalvageEnabled, "scaldS6WreckSalvageEnabled", true);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            if (biomeListBuffer == null)
            {
                biomeListBuffer = crossBiomeBiomeList;
            }

            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Mod enabled", ref masterEnabled,
                "Off: this mod's defs still load (nothing on a saved game silently "
              + "disappears), but every toggle below is treated as off regardless of "
              + "its own state.");
            list.GapLine();

            list.Label("BIOMES (each independently toggleable, owner ruling §7 Q1)");
            list.CheckboxLabeled("The Scald", ref scaldEnabled,
                "A perched, boiling crater lake with its own kit (steam sky, steam-catch "
              + "condenser, vent fields, drifting wrecks) and margin fishing table.");
            list.CheckboxLabeled("The Propane Lake", ref propaneLakeEnabled,
                "A black mirror of liquid fuel ringed by a frozen crust, with its own "
              + "catch table.");
            list.CheckboxLabeled("The Twilight Sea", ref twilightSeaEnabled,
                "A hypersaline terminal sea, moldy shore to shore, with its own fishing "
              + "table.");
            list.CheckboxLabeled("The Grey Sea", ref greySeaEnabled,
                "A hypersaline terminal sea, salt-encrusted and shrinking, with its own "
              + "fishing table.");
            list.GapLine();

            list.Label("THE SCALD'S KIT");
            list.Label("Off leaves the biome, its terrain and every def in place; only the "
                       + "named mechanic stops acting. Wreck and set-piece scatter changes "
                       + "apply to newly generated maps.");
            list.CheckboxLabeled("S1 — standing steam sky", ref scaldS1SteamSkyEnabled,
                "The permanent boil's-breath weather lock and its rare still days.");
            list.CheckboxLabeled("S2 — steam-catch condenser", ref scaldS2SteamCatchEnabled,
                "The buildable condenser that drinks a vent's clean breath for water.");
            list.CheckboxLabeled("S4 — vent fields", ref scaldS4VentFieldsEnabled,
                "Natural vents S2's condenser and S5's set-pieces key on.");
            list.CheckboxLabeled("S5 — sail + walker set-pieces", ref scaldS5SailWalkerEnabled,
                "Drifting bubble-sail wrecks and the bottom-walker surfacing sighting.");
            list.CheckboxLabeled("S6 — wreck salvage", ref scaldS6WreckSalvageEnabled,
                "Salvageable wrecks scattered in the burning shallows.");
            list.GapLine();

            list.Label("Cross-biome opt-in (WORLDGEN-AFFECTING — new maps only)");
            list.Label("Reserved for a future pass that lets a Scald mechanic generate on "
              + "a non-Scald biome's map. Inert until that pass exists; the fields persist "
              + "so a save carries a chosen value forward.");
            list.CheckboxLabeled("Enable outside the Scald biome", ref crossBiomeEnabled,
                "Master switch for the section below.");
            if (crossBiomeEnabled)
            {
                list.CheckboxLabeled("  Every biome", ref crossBiomeEverywhere,
                    "Apply to any non-Scald biome. Off: only the biomes named below.");
                if (!crossBiomeEverywhere)
                {
                    list.Label("  Biome defNames, comma-separated:");
                    biomeListBuffer = list.TextEntry(biomeListBuffer);
                    crossBiomeBiomeList = biomeListBuffer;
                }
                list.Label("  Coverage: " + (crossBiomeCoverage * 100f).ToString("0") + "%");
                crossBiomeCoverage = list.Slider(crossBiomeCoverage, 0f, 1f);
            }

            list.End();
        }
    }

    public class RM_TerminalBiomesMod : Mod
    {
        public static RM_TerminalBiomesSettings settings;

        public RM_TerminalBiomesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_TerminalBiomesSettings>();
            if (ModsConfig.IsActive("mandrake.rm.environmentalhazards"))
            {
                RegisterMechanicGates();
            }
        }

        // Kept in its own non-inlined method so the JIT only resolves the
        // shared assembly's types when that mod is actually active.
        [MethodImpl(MethodImplOptions.NoInlining)]
        private static void RegisterMechanicGates()
        {
            RM_MechanicGates.Register("Scald.S1", () => RM_TerminalBiomesSettings.ScaldS1SteamSkyActive);
            RM_MechanicGates.Register("Scald.S2", () => RM_TerminalBiomesSettings.ScaldS2SteamCatchActive);
            RM_MechanicGates.Register("Scald.S4", () => RM_TerminalBiomesSettings.ScaldS4VentFieldsActive);
            RM_MechanicGates.Register("Scald.S5", () => RM_TerminalBiomesSettings.ScaldS5SailWalkerActive);
            RM_MechanicGates.Register("Scald.S6", () => RM_TerminalBiomesSettings.ScaldS6WreckSalvageActive);
        }

        public override string SettingsCategory()
        {
            return "Terminal Biomes";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
