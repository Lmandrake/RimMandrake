using System.Reflection;
using System.Runtime.CompilerServices;
using System.Collections.Generic;
using System.Linq;
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
    // The per-biome toggles (scald/chill/twilightSea/greySea) each gate their
    // biome's whole kit through the Active properties below; none removes a
    // biome from a generated planet (BIOME_PAINT_ONCE_AT_THE_END_1). The cross-
    // biome block and the tether-chain choice are read by nothing and sit in the
    // screen's "Not wired yet" group.
    // Screen: SettingsKit groups, scope audited per read site 2026-10-10 (b5).
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
        // SCALD_UNDERWATER_FLORA_1: thurlsponge colonising the shallow-band wrecks at map generation.
        public static bool scaldThurlspongeWrecksEnabled = true;

        // Effective state: a sub-toggle only counts while the mod and the
        // Scald are both on. Everything that gates reads these, never the
        // raw fields.
        public static bool ScaldActive => masterEnabled && scaldEnabled;
        public static bool ScaldS1SteamSkyActive => ScaldActive && scaldS1SteamSkyEnabled;
        public static bool ScaldS2SteamCatchActive => ScaldActive && scaldS2SteamCatchEnabled;
        public static bool ScaldS4VentFieldsActive => ScaldActive && scaldS4VentFieldsEnabled;
        public static bool ScaldThurlspongeWrecksActive => ScaldActive && scaldThurlspongeWrecksEnabled;
        public static bool ScaldS5SailWalkerActive => ScaldActive && scaldS5SailWalkerEnabled;
        public static bool ScaldS7SteamExposureActive => ScaldActive && scaldS7SteamExposureEnabled;
        // S1b rides S1: a flash in a sky that is not the boil's breath makes no sense.
        public static bool ScaldS1bVentFlashActive => ScaldS1SteamSkyActive && scaldS1bVentFlashEnabled;

        // ── Twilight Sea danger pass (TWILIGHT_DANGER_LIGHTWEB_1) ───────
        public static bool suulkEnabled = true;
        public static float suulkFrequencyMultiplier = 1f;
        public static bool vauliskEnabled = true;
        // VAULISK_LURE_REVEAL_TRIGGER_1: proximity checked every second and any job aimed at the lure reveals it.
        // PROVISIONAL (auto-decided 2026-10-09). Off: only the old slow (2000-tick) proximity check.
        public static bool vauliskQuickReveal = true;

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
        // CHANNEL_CURRENT_CADENCE_FIDELITY_1: steps keep their authored cadence (re-armed from when they were due, not
        // from the 15-tick processing tick) and a pawn walking onto the current is caught within 15 ticks, not up to
        // 250. PROVISIONAL (auto-decided 2026-10-09, CHANNEL_CURRENT_CADENCE_FIDELITY_1). Off: the old quantised pace.
        public static bool channelCurrentExactPace = true;
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

        // TWILIGHTSEA_FLORA_PASS_1: Route B placement (tithemoss/tollhorn/gleamfloss/farwick) and the light comps (gloamurn, murkspindle).
        public static bool twilightFloraDressingEnabled = true;
        public static bool twilightFloraLightCompsEnabled = true;
        public static bool TwilightFloraDressingActive => masterEnabled && twilightSeaEnabled && twilightFloraDressingEnabled;
        public static bool TwilightFloraLightCompsActive => masterEnabled && twilightSeaEnabled && twilightFloraLightCompsEnabled;
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
        // HAZARD_CLOCK_INSPECT_LINES_1 (TB-4): Grey lamp burn time, twilight well phase and crust count in inspect text.
        public static bool hazardClockInspectEnabled = true;
        public static float greyLampGiantBurnHours = 8f;
        public static float greyLampGiantMinRadius = 12f;
        private static bool GreyActive => masterEnabled && greySeaEnabled;
        public static bool GreyLampDrawnActive => GreyActive && greyLampDrawnEnabled;
        public static bool GreyLampWatcherActive => GreyActive && greyLampWatcherEnabled;
        public static bool GreyLampGiantActive => GreyActive && greyLampGiantEnabled;

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
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
            Scribe_Values.Look(ref scaldThurlspongeWrecksEnabled, "scaldThurlspongeWrecksEnabled", true);
            Scribe_Values.Look(ref suulkEnabled, "suulkEnabled", true);
            Scribe_Values.Look(ref suulkFrequencyMultiplier, "suulkFrequencyMultiplier", 1f);
            Scribe_Values.Look(ref vauliskEnabled, "vauliskEnabled", true);
            Scribe_Values.Look(ref vauliskQuickReveal, "vauliskQuickReveal", true);
            Scribe_Values.Look(ref twilightPaneStrikeEnabled, "twilightPaneStrikeEnabled", true);
            Scribe_Values.Look(ref twilightPaneStrikeFrequency, "twilightPaneStrikeFrequency", 1.0f);
            Scribe_Values.Look(ref twilightDeckAccumulationEnabled, "twilightDeckAccumulationEnabled", true);
            Scribe_Values.Look(ref twilightDeckAccumulationRate, "twilightDeckAccumulationRate", 1.0f);
            Scribe_Values.Look(ref channelCurrentEnabled, "channelCurrentEnabled", true);
            Scribe_Values.Look(ref channelCurrentExactPace, "channelCurrentExactPace", true);
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
            Scribe_Values.Look(ref twilightFloraDressingEnabled, "twilightFloraDressingEnabled", true);
            Scribe_Values.Look(ref twilightFloraLightCompsEnabled, "twilightFloraLightCompsEnabled", true);
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
            Scribe_Values.Look(ref hazardClockInspectEnabled, "hazardClockInspectEnabled", true);
            Scribe_Values.Look(ref greyLampGiantBurnHours, "greyLampGiantBurnHours", 8f);
            Scribe_Values.Look(ref greyLampGiantMinRadius, "greyLampGiantMinRadius", 12f);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int/string/enum setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_TerminalBiomesSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int)
                    || f.FieldType == typeof(string) || f.FieldType.IsEnum)
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_TerminalBiomesSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
            biomeListBuffer = null;
        }

        private static string biomeListBuffer;
        private static Vector2 scrollPos;
        private static float viewHeight = 2000f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string> { "Not wired yet (these change nothing)" };

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10). A setting read both at map generation and
        /// live (the vaulisk, the Scald sail/walker set-pieces, floor flora placement) sits in a NewMapsOnly group, because turning it
        /// ON only reaches newly generated maps; turning it OFF also acts live. The biome switches are read live almost everywhere
        /// but also by three map-generation scatters, so their tooltips say so.</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards" : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        public void DoWindowContents(Rect inRect)
        {
            if (biomeListBuffer == null)
            {
                biomeListBuffer = crossBiomeBiomeList;
            }

            // Scrolls: maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Mod and biome switches", RimMandrake.Shared.SettingScope.Now, new[] { "masterEnabled", "scaldEnabled", "chillEnabled", "twilightSeaEnabled", "greySeaEnabled" }))
            {
                list.CheckboxLabeled("Mod enabled", ref masterEnabled,
                    "Off: this mod's defs still load (nothing on a saved game silently "
                  + "disappears), but every toggle below is treated as off regardless of "
                  + "its own state. Takes effect on what is on the map now; the map-generation scatters "
                  + "(vaulisk lure, Scald wreck sponge and sail set-pieces, floor flora) simply skip on maps made afterwards.");
                list.Label("BIOMES (each independently toggleable, owner ruling §7 Q1)");
                list.CheckboxLabeled("The Scald", ref scaldEnabled,
                    "A perched, boiling crater lake with its own kit (steam sky, steam-catch "
                  + "condenser, vent fields, drifting wrecks) and margin fishing table. Off switches the whole Scald kit off.");
                list.CheckboxLabeled("The Chill", ref chillEnabled,
                    "A black mirror of liquid fuel ringed by a frozen crust, with its own "
                  + "catch table. Off switches off the Chill's growers and wax procession.");
                list.CheckboxLabeled("The Twilight Sea", ref twilightSeaEnabled,
                    "A hypersaline terminal sea, moldy shore to shore, with its own fishing "
                  + "table. Off switches off the suulk, vaulisk, pane strikes, light economy, flora and channel current.");
                list.CheckboxLabeled("The Grey Sea", ref greySeaEnabled,
                    "A hypersaline terminal sea, salt-encrusted and shrinking, with its own "
                  + "fishing table. Off switches off the hull crust and the lamp response.");
                list.GapLine();
            }

            if (Group(list, "The Scald's kit", RimMandrake.Shared.SettingScope.Now, new[] { "scaldS1SteamSkyEnabled", "scaldS1bVentFlashEnabled", "scaldS2SteamCatchEnabled", "scaldS4VentFieldsEnabled", "scaldS7SteamExposureEnabled" }))
            {
                list.Label("Off leaves the biome, its terrain and every def in place; only the "
                           + "named mechanic stops acting.");
                list.CheckboxLabeled("S1 — standing steam sky", ref scaldS1SteamSkyEnabled,
                    "The permanent boil's-breath weather lock and its rare still days.");
                list.CheckboxLabeled("S1b — vent-flash sky pulses", ref scaldS1bVentFlashEnabled,
                    "Every few hours the whole sky briefly whitens and a geyser is heard letting go "
                  + "off-camera — the shore's rhythm, felt map-wide instead of only beside a vent. "
                  + "Purely cosmetic. Rides S1: with the steam sky off there is nothing to flash.");
                list.CheckboxLabeled("S2 — steam-catch condenser", ref scaldS2SteamCatchEnabled,
                    "The buildable condenser that drinks a vent's clean breath for water.");
                list.CheckboxLabeled("S4 — vent fields", ref scaldS4VentFieldsEnabled,
                    "Natural vents S2's condenser keys on.");
                list.CheckboxLabeled("S7 — steam exposure", ref scaldS7SteamExposureEnabled,
                    "The clock that makes the standing steam lethal to an unprotected pawn. Off: "
                  + "nobody accumulates scald exposure and any exposure already carried heals off. "
                  + "The water still burns to wade in either way — that is S8's own switch, in the "
                  + "Environmental Hazards Kit's settings.");
                list.GapLine();
            }

            if (Group(list, "The Scald's map-generation scatter (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "scaldS5SailWalkerEnabled", "scaldThurlspongeWrecksEnabled" }))
            {
                list.CheckboxLabeled("S5 — sail + walker set-pieces", ref scaldS5SailWalkerEnabled,
                    "Drifting bubble-sail wrecks (placed when a map is made) and the bottom-walker surfacing sighting "
                  + "(a live incident, which also stops at once when this is turned off).");
                list.CheckboxLabeled("Thurlsponge colonises wrecks", ref scaldThurlspongeWrecksEnabled,
                    "Each salvage wreck in the shallows is ringed with thurlsponge (harvestable for Steel) "
                  + "when the map is made. Off: thurlsponge grows only on the open floor. Affects map generation.");
                list.GapLine();
            }

            if (Group(list, "The Chill's growers and wax procession", RimMandrake.Shared.SettingScope.Now, new[] { "chillCryoponicsEnabled", "chillFloorBedEnabled", "chillWaxProcessionEnabled" }))
            {
                list.CheckboxLabeled("Chill cryoponics vat", ref chillCryoponicsEnabled,
                    "The sealed, powered vat that grows the Chill's six deep-bed plants anywhere, "
                  + "carrying its own cryogenic bath. Off: the vat gives no cold bath, so the bed "
                  + "plants only grow where the surroundings already allow it.");
                list.CheckboxLabeled("Chill floor growing bed", ref chillFloorBedEnabled,
                    "The plain growing bed that can only be built on the Chill's seabed. Off: no "
                  + "new beds can be placed; existing ones keep working.");
                list.CheckboxLabeled("Chill wax procession", ref chillWaxProcessionEnabled,
                    "The floor's giant: slow wax colonies that pause to shed dead filter sheets for "
                  + "the crew to haul back. Off: colonies still walk the floor but shed no new sheets.");
                list.GapLine();
            }

            if (Group(list, "The suulk (TWILIGHT_DANGER_LIGHTWEB_1)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "suulkEnabled", "suulkFrequencyMultiplier", "twilightSuulkPressureScalingEnabled" }))
            {
                list.CheckboxLabeled("The suulk — lamp-grazer", ref suulkEnabled,
                    "A soft, slow drifter that arrives on a several-day cadence and feeds on the "
                  + "brightest player-owned light, dimming and eventually destroying it. Nearly "
                  + "harmless to pawns; the danger is to the light economy, not to life.");
                if (suulkEnabled)
                {
                    list.Label("  Arrival frequency: " + suulkFrequencyMultiplier.ToString("0.0") + "x");
                    suulkFrequencyMultiplier = list.Slider(suulkFrequencyMultiplier, 0.1f, 3f);
                }
                list.CheckboxLabeled("Suulk pressure scales with constellation size", ref twilightSuulkPressureScalingEnabled,
                    "On: each LIT lamp or cage the colony owns makes a suulk arrival more likely, up to "
                  + "certain at four. Off: the chance stays at the one-lamp level however many you carry "
                  + "(none at all still draws none).");
                list.GapLine();
            }

            if (Group(list, "The vaulisk lure (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "vauliskEnabled" }))
            {
                list.CheckboxLabeled("The vaulisk — counterfeit lure", ref vauliskEnabled,
                    "A rare, one-per-map ambush predator disguised as a lit lamp-bladder plant "
                  + "carrying a false, steady (never-breathing) glow. Swaps to a fightable pawn "
                  + "when approached. Turning it on only places lures on newly generated maps; turning it off also "
                  + "stops lures already on a map from revealing.");
                list.GapLine();
            }

            if (Group(list, "Vaulisk reveal", RimMandrake.Shared.SettingScope.Now, new[] { "vauliskQuickReveal" }))
            {
                list.CheckboxLabeled("The vaulisk springs the moment it is touched", ref vauliskQuickReveal,
                    "On: it reveals as soon as anyone comes within reach or a colonist is ordered to harvest or cut it. "
                  + "Off: it checks only every half-minute or so, so a pawn may walk right past it.");
                list.GapLine();
            }

            if (Group(list, "Pane strikes (TWILIGHT_PANE_STRIKE_1)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "twilightPaneStrikeEnabled", "twilightPaneStrikeFrequency" }))
            {
                list.Label("The waveglass lid sheds panes onto the floor and, "
                           + "while a gravship sits there, onto its own deck — one pane system.");
                list.CheckboxLabeled("Pane strikes", ref twilightPaneStrikeEnabled,
                    "Both the ordinary background shed (harmless veil-fall litter) and the rare "
                  + "whole-pane strike, which CAN kill a pawn caught in its ~15-second shadow "
                  + "warning. Off: neither fires; any pane already on the ground stays and is "
                  + "still harvestable.");
                if (twilightPaneStrikeEnabled)
                {
                    list.Label("  Frequency (litter and whole-pane strikes): " + twilightPaneStrikeFrequency.ToString("0.0") + "x");
                    twilightPaneStrikeFrequency = list.Slider(twilightPaneStrikeFrequency, 0.25f, 3f);
                }
                list.GapLine();
            }

            if (Group(list, "Deck accumulation (TWILIGHT_PANE_STRIKE_1)", RimMandrake.Shared.SettingScope.Now, new[] { "twilightDeckAccumulationEnabled", "twilightDeckAccumulationRate" }))
            {
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
            }

            if (Group(list, "The Twilight Sea's light economy", RimMandrake.Shared.SettingScope.Now, new[] { "twilightWellDriftEnabled", "twilightDriftCadence", "twilightWellAvoidsCurrent", "twilightCagesPassableBeneath", "twilightSunSphereGraceDays" }))
            {
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
                list.CheckboxLabeled("Wells keep out of the current's lanes", ref twilightWellAvoidsCurrent,
                    "On: a twilight well never opens in the middle of a current lane (TB-3). Off: any standable cell may host one.");
                list.CheckboxLabeled("Cages passable beneath", ref twilightCagesPassableBeneath,
                    "The floating farm doesn't use up surface space because it floats above you. "
                  + "Off: a cage occupies its cells like a normal building. Applies at once, including to cages "
                  + "already built (their cells are re-read into the path grid).");
                list.Label("Sun-sphere grace period before it dims to a husk: " + twilightSunSphereGraceDays.ToString("0.#") + " days");
                twilightSunSphereGraceDays = list.Slider(twilightSunSphereGraceDays, 0.5f, 10f);
                list.GapLine();
            }

            if (Group(list, "Floor flora placement (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "twilightFloraDressingEnabled" }))
            {
                list.CheckboxLabeled("Floor flora placement (Route B)", ref twilightFloraDressingEnabled,
                    "Tithemoss on wild lamp-plants at map generation; gleamfloss, farwick buds and tollhorn seeded "
                  + "when a skylight opens, and floss and buds dying when it closes. Off: those four only appear if "
                  + "something else places them. Turning it on only reaches newly generated maps; the skylight seeding "
                  + "and clearing also stop at once when it is turned off.");
                list.GapLine();
            }

            if (Group(list, "Floor flora light behaviour", RimMandrake.Shared.SettingScope.Now, new[] { "twilightFloraLightCompsEnabled" }))
            {
                list.CheckboxLabeled("Floor flora light behaviour", ref twilightFloraLightCompsEnabled,
                    "Gloamurn banks a well's light and glows only after the well closes; murkspindle wilts in strong "
                  + "light. Off: gloamurn stays dark and murkspindle ignores light.");
                list.GapLine();
            }

            if (Group(list, "Channel current (TWILIGHT_CHANNEL_CURRENT_1)", RimMandrake.Shared.SettingScope.Now, new[] { "channelCurrentEnabled", "channelCurrentStrength", "channelCurrentExactPace", "channelFirstEntryWarning", "channelSinkOutcome", "undersurgeFrequency" }))
            {
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
                    list.CheckboxLabeled("  Exact current pace", ref channelCurrentExactPace,
                        "On: the current carries at its true speed (items at half a walking pawn's pace in the margin) "
                      + "and grabs a pawn the moment it wades in. Off: the older, slightly slower stepped pace, and a "
                      + "pawn can sometimes wade a short way before the current notices it.");
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
            }

            if (Group(list, "The Grey Sea files your ship (GREYSEA_HULL_CRUST_BUILD_1)", RimMandrake.Shared.SettingScope.Now, new[] { "greyHullCrustEnabled", "greyHullCrustRate", "greyHullCrustSaltSnowMultiplier", "greyHullCrustBerthMultiplier", "greyTearFreeEnabled", "greyTearFreeDamage" }))
            {
                list.CheckboxLabeled("Hull crystallisation", ref greyHullCrustEnabled,
                    "While a gravship sits parked on the Grey Sea floor, salt rimes its plating (about "
                  + "a day), salts its outer doors shut one by one (from about two and a half days), and "
                  + "after long neglect jackets the hull in crust that must be chipped off before "
                  + "launch (ramping in from day five, up to a third of the hull by about a quadrum). Chipping pays "
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
            }

            if (Group(list, "The Grey Sea answers your light (GREYSEA_LAMP_RESPONSE_BUILD_1)", RimMandrake.Shared.SettingScope.Now, new[] { "greyLampDrawnEnabled", "seekGlowDrawnToDeepfire", "greyLampWatcherEnabled", "hazardClockInspectEnabled", "greyLampGiantEnabled", "greyLampGiantBurnHours", "greyLampGiantMinRadius" }))
            {
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
                list.CheckboxLabeled("Show hazard clocks when inspecting", ref hazardClockInspectEnabled,
                    "A bright lamp in the Grey Sea says how long it has burned steadily; a twilight well says whether it is "
                  + "opening, standing or waning and how long is left; a grav engine on the Grey Sea says how many crust "
                  + "cells still hold the deck. Text only: it changes nothing else. Applies now.");
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
                list.GapLine();
            }

            if (Group(list, "Not wired yet (these change nothing)", RimMandrake.Shared.SettingScope.Now, new[] { "twilightChainAvailability", "crossBiomeEnabled", "crossBiomeEverywhere", "crossBiomeBiomeList", "crossBiomeCoverage" }))
            {
                list.Label("Tether-chain availability — NO EFFECT YET: no trader stocks tether chains "
                  + "(the Compact's stock was retired); the choice is kept for when one does:");
                if (list.RadioButton("  Scarce", twilightChainAvailability == 0)) twilightChainAvailability = 0;
                if (list.RadioButton("  Standard", twilightChainAvailability == 1)) twilightChainAvailability = 1;
                if (list.RadioButton("  Plentiful", twilightChainAvailability == 2)) twilightChainAvailability = 2;
                list.GapLine();
                list.Label("Cross-biome opt-in: reserved for a future pass that lets a Scald mechanic generate on "
                  + "a non-Scald biome's map. NOT YET WIRED — nothing reads these; the fields persist "
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
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
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

    // VALIDATION_SETTINGS_SNAPSHOT_1: the settings ExposeData round trip. The bridge's set/get round trips touch the
    // static fields only, so a field missing its Scribe call passed them. This writes every public static settings
    // field to an alternate value, SAVES the settings through Scribe to a temp file exactly as WriteSettings would,
    // puts the fields back to their prior values, LOADS the file, and reports every field that did not come back as
    // the alternate (= not Scribed, or Scribed under a key that does not load). Prior values are always restored.
    public static class RM_TerminalBiomesSettingsProof
    {
        public static string ExposeRoundTrip()
        {
            if (Scribe.mode != LoadSaveMode.Inactive)
            {
                return "busy: Scribe is " + Scribe.mode;
            }
            var fields = new List<System.Reflection.FieldInfo>();
            foreach (var f in typeof(RM_TerminalBiomesSettings).GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static))
            {
                if (f.IsLiteral || f.IsInitOnly) continue;
                System.Type ty = f.FieldType;
                if (ty == typeof(bool) || ty == typeof(int) || ty == typeof(float) || ty == typeof(string) || ty.IsEnum) fields.Add(f);
            }
            var prior = new Dictionary<System.Reflection.FieldInfo, object>();
            var alt = new Dictionary<System.Reflection.FieldInfo, object>();
            foreach (var f in fields)
            {
                object v = f.GetValue(null);
                prior[f] = v;
                alt[f] = Alt(f.FieldType, v);
            }
            string path = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "rm_tb_settings_roundtrip.xml");
            var bad = new List<string>();
            try
            {
                foreach (var f in fields) f.SetValue(null, alt[f]);
                ModSettings inst = RM_TerminalBiomesMod.settings ?? new RM_TerminalBiomesSettings();
                Scribe.saver.InitSaving(path, "SettingsBlock");
                try { Scribe_Deep.Look(ref inst, "ModSettings"); }
                finally { Scribe.saver.FinalizeSaving(); }
                foreach (var f in fields) f.SetValue(null, prior[f]);
                ModSettings loaded = null;
                Scribe.loader.InitLoading(path);
                try { Scribe_Deep.Look(ref loaded, "ModSettings"); }
                finally { Scribe.loader.FinalizeLoading(); }
                foreach (var f in fields)
                {
                    if (!Same(f.GetValue(null), alt[f])) bad.Add(f.Name);
                }
            }
            catch (System.Exception e)
            {
                Scribe.ForceStop();
                return "error: " + e.Message;
            }
            finally
            {
                foreach (var f in fields) f.SetValue(null, prior[f]);
                try { System.IO.File.Delete(path); } catch { }
            }
            return "fields=" + fields.Count + " lost=" + bad.Count + (bad.Count > 0 ? " missing=" + string.Join(",", bad) : "");
        }

        private static object Alt(System.Type ty, object v)
        {
            if (ty == typeof(bool)) return !(bool)v;
            if (ty == typeof(int)) return (int)v + 1;
            if (ty == typeof(float)) return (float)v * 2f + 1f;
            if (ty == typeof(string)) return (v as string ?? "") + "_rt";
            System.Array vals = System.Enum.GetValues(ty);
            foreach (object m in vals) if (!m.Equals(v)) return m;
            return v;
        }

        private static bool Same(object a, object b)
        {
            if (a is float fa && b is float fb) return System.Math.Abs(fa - fb) < 1e-4f;
            return Equals(a, b);
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

        private static Traversability? applied;
        private static readonly System.Reflection.MethodInfo walkabilityChanged =
            HarmonyLib.AccessTools.Method(typeof(RegionDirtyer), "Notify_WalkabilityChanged");

        // TERMINAL_SETTINGS_CONSUMERS_WIRE_1: writes the defs only when the setting actually changed (it used to run
        // every settings-window frame), and then re-reads every spawned cage's cells into the path grid and marks
        // their regions dirty, so a flip takes effect on maps already loaded instead of at some later rebuild.
        public static void Apply()
        {
            Traversability value = RM_TerminalBiomesSettings.twilightCagesPassableBeneath
                ? Traversability.PassThroughOnly
                : Traversability.Impassable;
            if (applied == value)
            {
                return;
            }
            bool first = applied == null;
            applied = value;
            var defs = new List<ThingDef>();
            foreach (string defName in CageDefNames)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
                if (def != null)
                {
                    def.passability = value;
                    defs.Add(def);
                }
            }
            if (first || Find.Maps == null)
            {
                return; // startup: nothing spawned yet
            }
            foreach (Map map in Find.Maps)
            {
                foreach (ThingDef def in defs)
                {
                    foreach (Thing cage in map.listerThings.ThingsOfDef(def).ToList())
                    {
                        if (!cage.Spawned) continue;
                        foreach (IntVec3 c in cage.OccupiedRect())
                        {
                            walkabilityChanged?.Invoke(map.regionDirtyer, new object[] { c, c.Walkable(map) });
                        }
                        map.pathing.RecalculatePerceivedPathCostUnderThing(cage);
                    }
                }
            }
        }
    }
}
