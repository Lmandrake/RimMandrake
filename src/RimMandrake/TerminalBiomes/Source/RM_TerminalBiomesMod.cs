using System.Runtime.CompilerServices;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;
using HarmonyLib;

namespace RimMandrake.TerminalBiomes
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Terminal Biomes.
    //
    // TWILIGHT_PANE_STRIKE_1, 2026-09-27: this mod now carries ONE Harmony
    // patch (RM_Patch_GravEngineLaunchGate.cs, PatchAll'd from this class's
    // constructor below) — the RM_TerminalBiomes.csproj header's older "No
    // Harmony" line is corrected in the same commit. Every other class in
    // this assembly is still plain XML-wired (thingClass/placeWorkers/
    // GenStep Class=); this is the first and only reflection-based hook.
    //
    // TERMINALBIOMES_RM_MOD_BUILD_1 §11 step 1: five toggles (master + one
    // per biome, all default ON), plus one sub-toggle per Scald mechanic the
    // kit spec names (S1/S2/S4/S5/S7; S3 is unbuilt, and S6 wreck salvage
    // moved to the Wreckage engine's per-biome "Wreck field: Scald" checkbox,
    // SALVAGE_WRECKAGE_EVERYWHERE_1 slice 3),
    // plus a cross-biome block matching Greentide's own shape.
    //
    // The Scald sub-toggles are LIVE. Each is read as
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
    //       Scald.S7 -> RUT_ScaldSteamCarrier (GameCondition_EnvironmentalWeather)
    //       Scald    -> the biome switch alone (ScaldActive). Read by the Wreckage
    //                   engine's RM_WreckField_Scald, whose own checkbox lives in
    //                   the Wreckage settings; that engine registers "Scald.S6" as
    //                   an alias of the field.
    //       Scald.S1.flash -> RUT_WeatherEvent_VentFlash (no def of its own; the
    //                         event checks the key directly, since a WeatherEvent
    //                         is constructed from a Type and carries no Def)
    //   - Mechanics whose engine class was vanilla (the vent's
    //     Building_SteamGeyser): a thin subclass in RM_TerminalBiomesScaldKit.cs
    //     reads these settings directly.
    // Every gate acts at its comp/condition/incident/GenStep entry point,
    // never by removing a def, so a flip takes effect on the next tick (or,
    // for a scatter GenStep, on the next NEW map) and flipping back
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
        public static bool chillEnabled = true;
        public static bool twilightSeaEnabled = true;
        public static bool greySeaEnabled = true;

        // ── The Chill's growers (CHILL_CRYOPONICS_GROWER_1 / CHILL_FLOOR_GROWING_BED_1)
        // Off: the cryoponics vat is an ordinary bed (no cryogenic bath, so the
        // bed plants only grow where the ambient already permits); the floor bed
        // refuses NEW placement (anything already built stays and keeps working).
        public static bool chillCryoponicsEnabled = true;
        public static bool chillFloorBedEnabled = true;
        public static bool chillWaxProcessionEnabled = true;
        public static bool ChillWaxProcessionActive => masterEnabled && chillEnabled && chillWaxProcessionEnabled;
        public static bool ChillCryoponicsActive => masterEnabled && chillEnabled && chillCryoponicsEnabled;
        public static bool ChillFloorBedActive => masterEnabled && chillEnabled && chillFloorBedEnabled;

        // ── Scald mechanic sub-toggles (kit spec S1/S2/S4/S5/S7; S3 unbuilt; S6 is Wreckage's) ─
        public static bool scaldS1SteamSkyEnabled = true;
        public static bool scaldS2SteamCatchEnabled = true;
        public static bool scaldS4VentFieldsEnabled = true;
        public static bool scaldS5SailWalkerEnabled = true;
        public static bool scaldS7SteamExposureEnabled = true;
        public static bool scaldS1bVentFlashEnabled = true;

        // Effective state: a sub-toggle only counts while the mod and the
        // Scald are both on. Everything that gates reads these, never the
        // raw fields.
        public static bool ScaldActive => masterEnabled && scaldEnabled;
        public static bool ScaldS1SteamSkyActive => ScaldActive && scaldS1SteamSkyEnabled;
        public static bool ScaldS2SteamCatchActive => ScaldActive && scaldS2SteamCatchEnabled;
        public static bool ScaldS4VentFieldsActive => ScaldActive && scaldS4VentFieldsEnabled;
        public static bool ScaldS5SailWalkerActive => ScaldActive && scaldS5SailWalkerEnabled;
        public static bool ScaldS7SteamExposureActive => ScaldActive && scaldS7SteamExposureEnabled;
        // S1b rides S1: a flash in a sky that is not the boil's breath makes no sense.
        public static bool ScaldS1bVentFlashActive => ScaldS1SteamSkyActive && scaldS1bVentFlashEnabled;

        // ── Twilight Sea danger pass (TWILIGHT_DANGER_LIGHTWEB_1) ───────
        public static bool suulkEnabled = true;
        public static float suulkFrequencyMultiplier = 1f;
        public static bool vauliskEnabled = true;

        private static bool TwilightSeaActive => masterEnabled && twilightSeaEnabled;
        public static bool SuulkActive => TwilightSeaActive && suulkEnabled;
        public static bool VauliskActive => TwilightSeaActive && vauliskEnabled;

        // ── Twilight Sea kit (TWILIGHT_PANE_STRIKE_1, D1+D8: "floor and
        // deck are ONE pane system") ─────────────────────────────────────
        // Item 5's ask: "pane strikes on/off + frequency, deck accumulation
        // rate + off." Frequency/rate are multipliers on the two
        // MapComponent tickers' own base chance (RM_MapComponent_VeilFall.cs)
        // and, for the strike, on nothing else — the IncidentDef's own
        // baseChance/minRefireDays are Storyteller-side and not user-tunable
        // by this mod's own convention (no other incident here exposes one).
        public static bool twilightPaneStrikeEnabled = true;
        public static float twilightPaneStrikeFrequency = 1.0f;
        public static bool twilightDeckAccumulationEnabled = true;
        public static float twilightDeckAccumulationRate = 1.0f;

        private static bool TwilightActive => masterEnabled && twilightSeaEnabled;
        // Gates BOTH the floor strike IncidentDef (RM_IncidentWorker_
        // PaneStrike) and the ordinary shed cadence (RM_MapComponent_
        // VeilFall's TrySpawnLightShed) -- D1's own text treats "most
        // veil-fall is flakes and litter" and "once in a while ... a whole
        // pane" as ONE cadence, never two switches.
        public static bool TwilightPaneStrikeActive => TwilightActive && twilightPaneStrikeEnabled;
        // Gates D8's deck accumulation ticker AND the launch-gate postfix
        // (RM_Patch_GravEngineLaunchGate) together -- degrades gracefully
        // per MOD_OPTIONS_RETROFIT_1: off means new panes stop landing on a
        // ship's deck AND the launch-gate postfix stops checking for them,
        // so any pane already sitting on a deck from before the flip is
        // left in place (cosmetic only, still clearable by hand) but can
        // never block a launch. Off can only ever REMOVE a constraint, so
        // it can never itself cause a stranding.
        public static bool TwilightDeckAccumulationActive => TwilightActive && twilightDeckAccumulationEnabled;

        // ── TWILIGHT_CHANNEL_CURRENT_1 (§1.6, the owed set) ─────────────
        public static bool channelCurrentEnabled = true;
        public static float channelCurrentStrength = 1f;
        public static RM_SinkOutcome channelSinkOutcome = RM_SinkOutcome.Recoverable;
        public static bool channelFirstEntryWarning = true;
        public static RM_UndersurgeFrequency undersurgeFrequency = RM_UndersurgeFrequency.Rare;

        // Effective state: on only while the mod, the Twilight Sea, and the
        // current's own toggle are all on. §1.6 "all-off degrades
        // gracefully: the bed becomes ordinary slow terrain... nothing
        // errors" — everything in RM_MapComponent_ChannelCurrent reads this,
        // never the raw field.
        // SILTTRAP_TERRAINS_UNBUILT_1: the bank works (weir, stake, silt-trap) are buildings, not the sea-floor
        // carry. They answer to the master switch only, so turning the Twilight Sea off no longer kills them.
        public static bool BankWorksActive => masterEnabled;
        public static bool ChannelCurrentActive => masterEnabled && twilightSeaEnabled && channelCurrentEnabled;
        public static RM_SinkOutcome SinkOutcome => channelSinkOutcome;

        // ── Cross-biome opt-in (Greentide's own shape; WORLDGEN-AFFECTING) ─
        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;

        // ── TWILIGHT_LIGHT_ECONOMY_1: the Twilight Sea's light layer ─────
        // (well-ledger drift, mobile constellation, sun-sphere, tenancy).
        // Mod Settings owed list per that item's §7. twilightChainAvailability:
        // 0 = scarce, 1 = standard, 2 = plentiful. twilightDriftCadence:
        // 0 = frozen (sandbox), 1 = week (shipped), 2 = slow.
        public static bool twilightWellDriftEnabled = true;
        public static int twilightDriftCadence = 1;
        public static int twilightChainAvailability = 1;
        public static bool twilightSuulkPressureScalingEnabled = true;
        public static bool twilightCagesPassableBeneath = true;
        public static float twilightSunSphereGraceDays = 3f;
        public static bool twilightChartsAgeEnabled = true;

        public static bool TwilightWellDriftActive => masterEnabled && twilightSeaEnabled && twilightWellDriftEnabled;
        // No dedicated toggle of its own (it's a buildable, not a spawned
        // mechanism) — but the mod's own master/biome switches must still
        // degrade it like everything else in this layer (RM_Building_SunSphere).
        public static bool SunSphereActive => masterEnabled && twilightSeaEnabled;

        // ── GREYSEA_HULL_CRUST_BUILD_1: the Grey files a parked ship (Q10/Q11) ─
        // Rate scales the whole ladder; the two multipliers are the ruled
        // environment (salt snow "roughly doubles", a brine berth is "faster").
        // Nothing purchasable modifies the pace — there is deliberately no
        // heat or fuel knob here. Off: no new rime, salt or crust, and the
        // launch gate and the salted-door lock both stop applying (off can
        // only remove a constraint).
        public static bool greyHullCrustEnabled = true;
        public static float greyHullCrustRate = 1f;
        public static float greyHullCrustSaltSnowMultiplier = 2f;
        public static float greyHullCrustBerthMultiplier = 1.5f;
        // CRUST_NEVER_STRANDS_1 (owner card 2026-10-08): a costly tear-free launch is always on offer on the Grey Sea
        // floor. PROVISIONAL: 30% of every hull building's max HP (never to death). Off: the gizmo is not offered.
        public static bool greyTearFreeEnabled = true;
        public static float greyTearFreeDamage = 0.3f;
        public static bool GreyHullCrustActive => masterEnabled && greySeaEnabled && greyHullCrustEnabled;

        // ── GREYSEA_LAMP_RESPONSE_BUILD_1: the Grey answers a player light (Q12) ─
        // Deterministic and forgiving: only powered lamps at or above the
        // radius, only after the hours of continuous burn, telegraphed by the
        // watcher (50%) and scrape-sign (75%); a dark lamp loses its clock.
        public static bool greyLampDrawnEnabled = true;
        // DEEPFIRE_WORLD_LIGHT_1 (a), owner card 2026-10-08: glow-seekers are drawn to deepfire light of any owner
        // (painted floors, glowing pawns, the glow tank). They bask at it; they never graze it.
        public static bool seekGlowDrawnToDeepfire = true;
        public static bool greyLampWatcherEnabled = true;
        public static bool greyLampGiantEnabled = true;
        public static bool twilightWellAvoidsCurrent = true;
        public static float greyLampGiantBurnHours = 8f;
        public static float greyLampGiantMinRadius = 12f;
        private static bool GreyActive => masterEnabled && greySeaEnabled;
        public static bool GreyLampDrawnActive => GreyActive && greyLampDrawnEnabled;
        public static bool GreyLampWatcherActive => GreyActive && greyLampWatcherEnabled;
        public static bool GreyLampGiantActive => GreyActive && greyLampGiantEnabled;

        private string biomeListBuffer;
        private Vector2 settingsScroll;
        private float lastListHeight = 1600f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref scaldEnabled, "scaldEnabled", true);
            Scribe_Values.Look(ref chillEnabled, "chillEnabled", true);
            Scribe_Values.Look(ref chillCryoponicsEnabled, "chillCryoponicsEnabled", true);
            Scribe_Values.Look(ref chillFloorBedEnabled, "chillFloorBedEnabled", true);
            Scribe_Values.Look(ref chillWaxProcessionEnabled, "chillWaxProcessionEnabled", true);
            Scribe_Values.Look(ref twilightSeaEnabled, "twilightSeaEnabled", true);
            Scribe_Values.Look(ref greySeaEnabled, "greySeaEnabled", true);
            Scribe_Values.Look(ref scaldS1SteamSkyEnabled, "scaldS1SteamSkyEnabled", true);
            Scribe_Values.Look(ref scaldS2SteamCatchEnabled, "scaldS2SteamCatchEnabled", true);
            Scribe_Values.Look(ref scaldS4VentFieldsEnabled, "scaldS4VentFieldsEnabled", true);
            Scribe_Values.Look(ref scaldS5SailWalkerEnabled, "scaldS5SailWalkerEnabled", true);
            Scribe_Values.Look(ref scaldS7SteamExposureEnabled, "scaldS7SteamExposureEnabled", true);
            Scribe_Values.Look(ref scaldS1bVentFlashEnabled, "scaldS1bVentFlashEnabled", true);
            Scribe_Values.Look(ref suulkEnabled, "suulkEnabled", true);
            Scribe_Values.Look(ref suulkFrequencyMultiplier, "suulkFrequencyMultiplier", 1f);
            Scribe_Values.Look(ref vauliskEnabled, "vauliskEnabled", true);
            Scribe_Values.Look(ref twilightPaneStrikeEnabled, "twilightPaneStrikeEnabled", true);
            Scribe_Values.Look(ref twilightPaneStrikeFrequency, "twilightPaneStrikeFrequency", 1.0f);
            Scribe_Values.Look(ref twilightDeckAccumulationEnabled, "twilightDeckAccumulationEnabled", true);
            Scribe_Values.Look(ref twilightDeckAccumulationRate, "twilightDeckAccumulationRate", 1.0f);
            Scribe_Values.Look(ref channelCurrentEnabled, "channelCurrentEnabled", true);
            Scribe_Values.Look(ref channelCurrentStrength, "channelCurrentStrength", 1f);
            Scribe_Values.Look(ref channelSinkOutcome, "channelSinkOutcome", RM_SinkOutcome.Recoverable);
            Scribe_Values.Look(ref channelFirstEntryWarning, "channelFirstEntryWarning", true);
            Scribe_Values.Look(ref undersurgeFrequency, "undersurgeFrequency", RM_UndersurgeFrequency.Rare);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);
            Scribe_Values.Look(ref twilightWellDriftEnabled, "twilightWellDriftEnabled", true);
            Scribe_Values.Look(ref twilightDriftCadence, "twilightDriftCadence", 1);
            Scribe_Values.Look(ref twilightChainAvailability, "twilightChainAvailability", 1);
            Scribe_Values.Look(ref twilightSuulkPressureScalingEnabled, "twilightSuulkPressureScalingEnabled", true);
            Scribe_Values.Look(ref twilightCagesPassableBeneath, "twilightCagesPassableBeneath", true);
            Scribe_Values.Look(ref twilightSunSphereGraceDays, "twilightSunSphereGraceDays", 3f);
            Scribe_Values.Look(ref twilightChartsAgeEnabled, "twilightChartsAgeEnabled", true);
            Scribe_Values.Look(ref greyHullCrustEnabled, "greyHullCrustEnabled", true);
            Scribe_Values.Look(ref greyHullCrustRate, "greyHullCrustRate", 1f);
            Scribe_Values.Look(ref greyHullCrustSaltSnowMultiplier, "greyHullCrustSaltSnowMultiplier", 2f);
            Scribe_Values.Look(ref greyHullCrustBerthMultiplier, "greyHullCrustBerthMultiplier", 1.5f);
            Scribe_Values.Look(ref greyTearFreeEnabled, "greyTearFreeEnabled", true);
            Scribe_Values.Look(ref greyTearFreeDamage, "greyTearFreeDamage", 0.3f);
            Scribe_Values.Look(ref greyLampDrawnEnabled, "greyLampDrawnEnabled", true);
            Scribe_Values.Look(ref seekGlowDrawnToDeepfire, "seekGlowDrawnToDeepfire", true);
            Scribe_Values.Look(ref greyLampWatcherEnabled, "greyLampWatcherEnabled", true);
            Scribe_Values.Look(ref greyLampGiantEnabled, "greyLampGiantEnabled", true);
            Scribe_Values.Look(ref twilightWellAvoidsCurrent, "twilightWellAvoidsCurrent", true);
            Scribe_Values.Look(ref greyLampGiantBurnHours, "greyLampGiantBurnHours", 8f);
            Scribe_Values.Look(ref greyLampGiantMinRadius, "greyLampGiantMinRadius", 12f);
        }

        public void DoWindowContents(Rect inRect)
        {
            if (biomeListBuffer == null)
            {
                biomeListBuffer = crossBiomeBiomeList;
            }

            // Scrolls: the list outgrew the window once the Grey's section landed.
            // maxOneColumn is load-bearing: the content (~2100px) is taller than the
            // initial 1600px guess, and without it the overflow wraps into an off-screen
            // second column, CurHeight resets, and the view shrinks instead of growing.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(lastListHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);

            list.CheckboxLabeled("Mod enabled", ref masterEnabled,
                "Off: this mod's defs still load (nothing on a saved game silently "
              + "disappears), but every toggle below is treated as off regardless of "
              + "its own state.");
            list.GapLine();

            list.Label("BIOMES (each independently toggleable, owner ruling §7 Q1)");
            list.CheckboxLabeled("The Scald", ref scaldEnabled,
                "A perched, boiling crater lake with its own kit (steam sky, steam-catch "
              + "condenser, vent fields, drifting wrecks) and margin fishing table.");
            list.CheckboxLabeled("The Chill", ref chillEnabled,
                "A black mirror of liquid fuel ringed by a frozen crust, with its own "
              + "catch table.");
            list.CheckboxLabeled("  Chill cryoponics vat", ref chillCryoponicsEnabled,
                "The sealed, powered vat that grows the Chill's six deep-bed plants anywhere, "
              + "carrying its own cryogenic bath. Off: the vat gives no cold bath, so the bed "
              + "plants only grow where the surroundings already allow it.");
            list.CheckboxLabeled("  Chill floor growing bed", ref chillFloorBedEnabled,
                "The plain growing bed that can only be built on the Chill's seabed. Off: no "
              + "new beds can be placed; existing ones keep working.");
            list.CheckboxLabeled("  Chill wax procession", ref chillWaxProcessionEnabled,
                "The floor's giant: slow wax colonies that pause to shed dead filter sheets for "
              + "the crew to haul back. Off: colonies still walk the floor but shed no new sheets.");
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
            list.CheckboxLabeled("S1b — vent-flash sky pulses", ref scaldS1bVentFlashEnabled,
                "Every few hours the whole sky briefly whitens and a geyser is heard letting go "
              + "off-camera — the shore's rhythm, felt map-wide instead of only beside a vent. "
              + "Purely cosmetic. Rides S1: with the steam sky off there is nothing to flash.");
            list.CheckboxLabeled("S2 — steam-catch condenser", ref scaldS2SteamCatchEnabled,
                "The buildable condenser that drinks a vent's clean breath for water.");
            list.CheckboxLabeled("S4 — vent fields", ref scaldS4VentFieldsEnabled,
                "Natural vents S2's condenser and S5's set-pieces key on.");
            list.CheckboxLabeled("S5 — sail + walker set-pieces", ref scaldS5SailWalkerEnabled,
                "Drifting bubble-sail wrecks and the bottom-walker surfacing sighting.");
            list.CheckboxLabeled("S7 — steam exposure", ref scaldS7SteamExposureEnabled,
                "The clock that makes the standing steam lethal to an unprotected pawn. Off: "
              + "nobody accumulates scald exposure and any exposure already carried heals off. "
              + "The water still burns to wade in either way — that is S8's own switch, in the "
              + "Environmental Hazards Kit's settings.");
            list.GapLine();

            list.Label("THE TWILIGHT SEA'S DANGER PASS (TWILIGHT_DANGER_LIGHTWEB_1)");
            list.CheckboxLabeled("The suulk — lamp-grazer", ref suulkEnabled,
                "A soft, slow drifter that arrives on a several-day cadence and feeds on the "
              + "brightest player-owned light, dimming and eventually destroying it. Nearly "
              + "harmless to pawns; the danger is to the light economy, not to life.");
            if (suulkEnabled)
            {
                list.Label("  Arrival frequency: " + suulkFrequencyMultiplier.ToString("0.0") + "x");
                suulkFrequencyMultiplier = list.Slider(suulkFrequencyMultiplier, 0.1f, 3f);
            }
            list.CheckboxLabeled("The vaulisk — counterfeit lure", ref vauliskEnabled,
                "A rare, one-per-map ambush predator disguised as a lit lamp-bladder plant "
              + "carrying a false, steady (never-breathing) glow. Swaps to a fightable pawn "
              + "when approached.");
            list.GapLine();

            list.Label("THE TWILIGHT SEA'S KIT");
            list.Label("TWILIGHT_PANE_STRIKE_1: the waveglass lid sheds panes onto the floor and, "
                       + "while a gravship sits there, onto its own deck — one pane system.");
            list.CheckboxLabeled("Pane strikes", ref twilightPaneStrikeEnabled,
                "Both the ordinary background shed (harmless veil-fall litter) and the rare "
              + "whole-pane strike, which CAN kill a pawn caught in its ~15-second shadow "
              + "warning. Off: neither fires; any pane already on the ground stays and is "
              + "still harvestable.");
            if (twilightPaneStrikeEnabled)
            {
                list.Label("  Frequency: " + twilightPaneStrikeFrequency.ToString("0.0") + "x");
                twilightPaneStrikeFrequency = list.Slider(twilightPaneStrikeFrequency, 0.25f, 3f);
            }
            list.CheckboxLabeled("Deck accumulation", ref twilightDeckAccumulationEnabled,
                "While a gravship sits on the Twilight floor, panes can also land on its own "
              + "hull footprint and must be cleared (deconstructed, same as any salvage) before "
              + "it can launch. This only ever DELAYS a launch behind a job the colony can "
              + "always do — never disables the engine. Off: no new panes land on a deck, and "
              + "the launch check stops looking for them; any pane already there stays but no "
              + "longer blocks anything.");
            if (twilightDeckAccumulationEnabled)
            {
                list.Label("  Rate: " + twilightDeckAccumulationRate.ToString("0.0") + "x");
                twilightDeckAccumulationRate = list.Slider(twilightDeckAccumulationRate, 0f, 3f);
            }
            list.GapLine();

            list.Label("THE TWILIGHT SEA'S LIGHT ECONOMY");
            list.CheckboxLabeled("Skylight drift", ref twilightWellDriftEnabled,
                "Skylights age, warn, close and reopen elsewhere on the sea floor. Off: "
              + "whatever wells exist stay as they are, no ledger clock runs.");
            if (twilightWellDriftEnabled)
            {
                list.Label("  Cadence: " + (twilightDriftCadence == 0 ? "frozen (sandbox)" : twilightDriftCadence == 1 ? "week (shipped)" : "slow"));
                if (list.RadioButton("  Frozen — sandbox, wells never age", twilightDriftCadence == 0)) twilightDriftCadence = 0;
                if (list.RadioButton("  Week — the shipped pace", twilightDriftCadence == 1)) twilightDriftCadence = 1;
                if (list.RadioButton("  Slow — roughly double the week", twilightDriftCadence == 2)) twilightDriftCadence = 2;
            }
            list.Label("Tether-chain availability (how many mobile cages/lamps the Compact "
              + "restocks toward):");
            if (list.RadioButton("  Scarce", twilightChainAvailability == 0)) twilightChainAvailability = 0;
            if (list.RadioButton("  Standard", twilightChainAvailability == 1)) twilightChainAvailability = 1;
            if (list.RadioButton("  Plentiful", twilightChainAvailability == 2)) twilightChainAvailability = 2;
            list.CheckboxLabeled("Suulk pressure scales with constellation size", ref twilightSuulkPressureScalingEnabled,
                "Carrying more mobile lamps/cages than the ruled handful shortens the suulk's "
              + "grazing cadence. No effect until the suulk incident (a separate item) ships — "
              + "persisted so a save carries a chosen value forward.");
            list.CheckboxLabeled("Cages passable beneath", ref twilightCagesPassableBeneath,
                "The floating farm doesn't use up surface space because it floats above you. "
              + "Off: a cage occupies its cells like a normal building. Takes effect after mod "
              + "settings apply, at the next map/region rebuild.");
            list.Label("Sun-sphere grace period before it dims to a husk: " + twilightSunSphereGraceDays.ToString("0.#") + " days");
            twilightSunSphereGraceDays = list.Slider(twilightSunSphereGraceDays, 0.5f, 10f);
            list.CheckboxLabeled("Charts age", ref twilightChartsAgeEnabled,
                "Off: a well-chart's forecast never marks itself stale.");
            list.GapLine();

            list.Label("THE TWILIGHT SEA'S CHANNEL CURRENT (TWILIGHT_CHANNEL_CURRENT_1)");
            list.CheckboxLabeled("Channel current", ref channelCurrentEnabled,
                "The dense floor current that carries a pawn or a dropped item along the "
              + "Twilight Sea's channels, the undersurge that widens it, and the bank works "
              + "(weir, silt-trap, stake-line) built into it. Off: the bed becomes ordinary "
              + "slow terrain, a weir catches nothing but its edge still gathers, and nothing "
              + "errors.");
            if (channelCurrentEnabled)
            {
                list.Label("  Current strength: " + channelCurrentStrength.ToString("0.0") + "x");
                channelCurrentStrength = list.Slider(channelCurrentStrength, 0.25f, 3f);
                list.CheckboxLabeled("  First-entry warning", ref channelFirstEntryWarning,
                    "A one-time message and mood-free alert the first time each colonist steps "
                  + "onto the bed.");
                list.Label("  Sink outcome (§3's ruled ladder):");
                if (list.RadioButton("    Recoverable (default)", channelSinkOutcome == RM_SinkOutcome.Recoverable, 0f))
                {
                    channelSinkOutcome = RM_SinkOutcome.Recoverable;
                }
                if (list.RadioButton("    Recoverable, but injured (permanent scar)", channelSinkOutcome == RM_SinkOutcome.RecoverableInjured, 0f))
                {
                    channelSinkOutcome = RM_SinkOutcome.RecoverableInjured;
                }
                if (list.RadioButton("    Lost (gone at arrival, no corpse)", channelSinkOutcome == RM_SinkOutcome.Lost, 0f))
                {
                    channelSinkOutcome = RM_SinkOutcome.Lost;
                }
                list.Label("  Undersurge frequency:");
                if (list.RadioButton("    Off", undersurgeFrequency == RM_UndersurgeFrequency.Off, 0f))
                {
                    undersurgeFrequency = RM_UndersurgeFrequency.Off;
                }
                if (list.RadioButton("    Rare (default)", undersurgeFrequency == RM_UndersurgeFrequency.Rare, 0f))
                {
                    undersurgeFrequency = RM_UndersurgeFrequency.Rare;
                }
                if (list.RadioButton("    Common", undersurgeFrequency == RM_UndersurgeFrequency.Common, 0f))
                {
                    undersurgeFrequency = RM_UndersurgeFrequency.Common;
                }
            }
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
            list.GapLine();

            list.Label("THE GREY SEA FILES YOUR SHIP (GREYSEA_HULL_CRUST_BUILD_1)");
            list.CheckboxLabeled("Hull crystallisation", ref greyHullCrustEnabled,
                "While a gravship sits parked on the Grey Sea floor, salt rimes its plating (about "
              + "a day), salts its outer doors shut one by one (from about two and a half days), and "
              + "after long neglect jackets the hull in crust that must be chipped off before "
              + "launch (ramping in from day five, whole hull by about a quadrum). Chipping pays "
              + "salt and sets the clock back. A salted door always yields to a short no-tool job "
              + "from either side, and crust only ever delays a launch. Off: nothing new grows, "
              + "salted doors open normally and crust no longer blocks launch.");
            if (greyHullCrustEnabled)
            {
                list.Label("  Pace: " + greyHullCrustRate.ToString("0.00") + "x");
                greyHullCrustRate = list.Slider(greyHullCrustRate, 0.25f, 3f);
                list.Label("  Salt-snow speed-up: " + greyHullCrustSaltSnowMultiplier.ToString("0.0") + "x");
                greyHullCrustSaltSnowMultiplier = list.Slider(greyHullCrustSaltSnowMultiplier, 1f, 4f);
                list.Label("  Brine-berth speed-up (brine channel or chimney field within 5 cells): "
                    + greyHullCrustBerthMultiplier.ToString("0.0") + "x");
                greyHullCrustBerthMultiplier = list.Slider(greyHullCrustBerthMultiplier, 1f, 3f);
                list.CheckboxLabeled("Tear-free launch (always available)", ref greyTearFreeEnabled,
                    "The gravship engine gains a costly forced launch on the Grey Sea floor: it rips all crust off the hull, "
                  + "unsalts every door, and damages every hull building. Never needs a working colonist, so crust can never "
                  + "strand a colony. Off: crust must be chipped off by hand.");
                if (greyTearFreeEnabled)
                {
                    list.Label("  Hull damage per building: " + (greyTearFreeDamage * 100f).ToString("0") + "% of max HP (never lethal)");
                    greyTearFreeDamage = list.Slider(greyTearFreeDamage, 0.05f, 0.8f);
                }
            }
            list.GapLine();

            list.Label("THE GREY SEA ANSWERS YOUR LIGHT (GREYSEA_LAMP_RESPONSE_BUILD_1)");
            list.CheckboxLabeled("Small things drawn to the light", ref greyLampDrawnEnabled,
                "Litter-pickers, salt crabs and the pink immu come and linger in a lit area. "
              + "Harmless; the busiest ground on the map is around your lamps.");
            list.CheckboxLabeled("Light-seekers are drawn to deepfire", ref seekGlowDrawnToDeepfire,
                "Creatures that seek out light also come to deepfire light (painted floors, glowing pawns, the glow tank), "
              + "whoever it belongs to. They linger at it and never eat it. Needs Luminous Pigment. Safe mid-game.");
            list.CheckboxLabeled("The watcher and the scrape-sign", ref greyLampWatcherEnabled,
                "Halfway to the giant's hours, a fessk comes to the edge of a bright lamp's light and "
              + "watches (it never enters, never attacks, leaves when approached). Three quarters "
              + "of the way, fresh scrape-sign appears in the silt at the light's edge. These are the "
              + "warnings: switch the lamp off and its clock is gone.");
            list.CheckboxLabeled("Wells keep out of the current's lanes", ref twilightWellAvoidsCurrent,
                "On: a twilight well never opens in the middle of a current lane (TB-3). Off: any standable cell may host one.");
            list.CheckboxLabeled("The giant breaks bright lamps", ref greyLampGiantEnabled,
                "A powered lamp at least as bright as the radius below, left burning without a break "
              + "for the hours below, reads to the reefback as a rival's mark. It comes and breaks that "
              + "lamp — never the ship, never your people — then leaves. Torches and braziers never "
              + "count, a lamp it cannot reach is never answered, and switching the lamp off at any "
              + "point resets it completely.");
            if (greyLampGiantEnabled)
            {
                list.Label("  Hours of steady burn before it comes: " + greyLampGiantBurnHours.ToString("0.0"));
                greyLampGiantBurnHours = list.Slider(greyLampGiantBurnHours, 2f, 24f);
                list.Label("  Brightest-lamp threshold (glow radius; standing lamp 12, sun lamp 14, floodlight 24): "
                    + greyLampGiantMinRadius.ToString("0.0"));
                greyLampGiantMinRadius = list.Slider(greyLampGiantMinRadius, 9f, 24f);
            }

            list.End();
            lastListHeight = list.CurHeight + 24f;
            Widgets.EndScrollView();
        }
    }

    public class RM_TerminalBiomesMod : Mod
    {
        public static RM_TerminalBiomesSettings settings;

        public RM_TerminalBiomesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_TerminalBiomesSettings>();
            // BAROQUE_BIOMES_WAVE2_FOLD_1: EnvironmentalHazards folds into
            // mandrake.rm.biomes in the same wave as TerminalBiomes, so its
            // packageId stops being independently active — this guard would
            // go permanently false and silently stop registering the
            // mechanic gates. Its own content is always co-present with
            // TerminalBiomes' now (same mod), so the guard is unconditional.
            RegisterMechanicGates();
            // TWILIGHT_PANE_STRIKE_1, D8's launch gate
            // (RM_Patch_GravEngineLaunchGate.cs). Building_GravEngine is a
            // plain Assembly-CSharp type present whether or not Odyssey is
            // active (Ninefold's own Patch_GravshipLaunched.cs header, this
            // same repo, verifies this against the decompiled source) — the
            // patch target always resolves, and the postfix itself is a
            // no-op on any map with no RM_VeilPane things on it.
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.terminalbiomes"), typeof(RM_TerminalBiomesMod).Assembly, "RimMandrake.TerminalBiomes");
            RegisterRiverWorksSeams();
        }

        // SURFACE_RIVER_WEIRS_1 slice 2: the weir/stake/silt-trap live in FlowWorks (Rivers) (a hard
        // dependency). The sea plugs its channel current into two of its seams: the undersurge
        // counts as a flood (weir breach, as before the move), and channel cells count as moving
        // water (the weir PlaceWorker accepts a channel margin as its wet end).
        private static void RegisterRiverWorksSeams()
        {
            RimMandrake.FlowWorks.Rivers.RM_RiverWorks.RegisterFloodSource(
                map => map.GetComponent<RM_MapComponent_ChannelCurrent>()?.SurgeActive == true);
            RimMandrake.FlowWorks.Rivers.RM_RiverWorks.RegisterCurrentCellRule(
                (map, c) => map.GetComponent<RM_MapComponent_ChannelCurrent>()?.HasCurrent(c) == true);
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
            // S6 (wreck salvage) is the Wreckage engine's field "Scald"; it registers
            // "Scald.S6" as an alias and reads this bare key for the biome switch.
            RM_MechanicGates.Register("Scald", () => RM_TerminalBiomesSettings.ScaldActive);
            RM_MechanicGates.Register("Scald.S7", () => RM_TerminalBiomesSettings.ScaldS7SteamExposureActive);
            RM_MechanicGates.Register("Scald.S1.flash", () => RM_TerminalBiomesSettings.ScaldS1bVentFlashActive);
        }

        public override string SettingsCategory()
        {
            return "Terminal Biomes";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
            RM_TwilightPassabilityApplier.Apply();
        }
    }

    // TWILIGHT_LIGHT_ECONOMY_1: "cages passable-beneath" (Mod Settings).
    // No Harmony patch exists for this specific lever, so the only vanilla
    // one for a building's own collision is ThingDef.passability itself — a shared,
    // def-level field, not a per-instance override. [StaticConstructorOnStartup]
    // guarantees this runs after every def is loaded and resolved (Mod
    // constructors, where settings are READ from disk via GetSettings, run
    // earlier still — before defs load — so by the time this fires the
    // setting's saved value is already in RM_TerminalBiomesSettings's
    // static fields). Re-applied on every settings-window frame too, so
    // flipping the checkbox takes effect at the next pathfinder/region
    // rebuild rather than needing a restart.
    [StaticConstructorOnStartup]
    public static class RM_TwilightPassabilityApplier
    {
        private static readonly string[] CageDefNames = { "RM_ConstellationCageSphere", "RM_ConstellationCageCube" };

        static RM_TwilightPassabilityApplier()
        {
            Apply();
        }

        public static void Apply()
        {
            Traversability value = RM_TerminalBiomesSettings.twilightCagesPassableBeneath
                ? Traversability.PassThroughOnly
                : Traversability.Impassable;
            foreach (string defName in CageDefNames)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
                if (def != null)
                {
                    def.passability = value;
                }
            }
        }
    }
}
