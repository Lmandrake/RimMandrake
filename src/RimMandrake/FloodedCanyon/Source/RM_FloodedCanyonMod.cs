using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — MOD_OPTIONS_RETROFIT_1 doctrine: on/off per major
    // mechanic, tuning where a number is the experience, defaults = shipped
    // behavior. Follows the sibling Gelatinous Slime mod's exact pattern
    // (SlimeMod.cs): STATIC FIELDS, read from everywhere (the biome worker
    // runs during worldgen with no Mod instance handy; the map component
    // reads settings every flood-cycle check), written only through the
    // settings window and ExposeData.
    // ════════════════════════════════════════════════════════════════════
    public class RM_FloodedCanyonSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new
        // planet. 1 = the shipped default (rare patches, same "1-3 per
        // planet" order of magnitude as Gelatinous Slime's own slider).
        public static float biomeRarityFactor = 1f;

        // "canyon biome insertion vs feature-only in other biomes" — the
        // item's own spec line. When true, the flood cycle + chime + growth
        // coupling run on EVERY map's biome, not only RM_FloodedCanyon, so a
        // player can have the mechanic without the biome (mirrors the
        // Greentide standalone mod's per-feature cross-biome toggle).
        public static bool featureInOtherBiomes = false;

        // Master switch for the whole flood cycle (chime + wall + soil).
        public static bool floodCycleEnabled = true;

        // Average days between floods on a given map.
        public static float floodPeriodDays = 20f;

        // Warning lead time before the wall arrives, once the chime rings.
        public static float chimeLeadTimeHours = 2f;

        // How long the wall stands before it recedes to soil.
        public static float floodDurationHours = 6f;

        // Whether the wall of water can lightly hurt a pawn caught in it.
        // Capped low by design — a startle, never a killer (this mod never
        // promises the campaign's own injury-ceiling ruling; it ships its
        // own conservative default because nothing here should feel unfair
        // in a mod a player added for the biome, not the danger).
        public static bool floodDamageEnabled = true;

        // Soak coupling: the flood hands every cell it wets to RimMandrake:
        // Explosive Plant Growth as SOAKED for the flood's duration plus
        // soakDecayDays. That mod owns the growth multiplier (its own
        // setting) and everything after; without it this does nothing.
        public static bool growthCouplingEnabled = true;
        public static float soakDecayDays = 4f;

        // CRACKEDLANDS_MECHANICS_BUILD_1 §3 — fossils in the walls.
        // WORLDGEN-AFFECTING: the seeding runs once, when a map is generated,
        // so these three only change maps generated afterwards.
        public static bool fossilSeamsEnabled = true;
        public static bool fossilSeamsInOtherBiomes = false;
        public static float fossilSeamDensity = 1f;

        // §3 — the flood re-cuts the ledger: fresh seams along the wetted
        // wall line at every recede. Runs wherever the flood cycle runs.
        public static bool floodRecutSeamsEnabled = true;
        public static int floodRecutSeamCount = 4;

        // §4 — the muttavaq: the flood wakes it (water reaching its pan), and
        // at the dry it digs in and seals where it stands. Off = the stock
        // behaviour the content def ships alone (sleeps until damaged).
        public static bool muttavaqWaterWakeEnabled = true;
        public static bool muttavaqDigInEnabled = true;

        // §5 — Peakstorm Light pulls the next flood forward (the chime
        // follows the storm on the peaks). The weather itself is a biome
        // weather commonality, not a setting.
        public static bool peakstormBiasEnabled = true;

        // CRACKEDLANDS_PEAKSTORM_DUST_REVERSAL_1 — the sky overlay's dust drifts one way and briefly reverses.
        // Off = it drifts one way only.
        public static bool peakstormDustReversalEnabled = true;

        // §5 — chimes staged by distance-to-flood (three rings across the
        // lead time). Off = the single chime at the start of the lead time.
        public static bool chimeStagingEnabled = true;

        // CRACKEDLANDS_GPT_ENRICHMENT_1 §2 — five beats before water: slot
        // wind, ticking pans, the tarruq hush (a herald window before the
        // chimes), then chimes tolling far-to-near, then the roar. Off = the
        // chimes alone, on the camera, as before.
        public static bool fiveBeatsEnabled = true;
        // TUNED: 2 h, the same as the chime lead, so the whole warning runs
        // ~4 h and each herald beat has ~40 min to itself.
        public static float heraldLeadHours = 2f;

        // §5 — the recede feast: the irqit carpet and the migrant sky.
        public static bool recedeFeastEnabled = true;
        public static bool recedeMigrantsEnabled = true;
        // TUNED: 40 — a carpet on a default flood, without a pawn-count spike.
        public static int irqitCohortMax = 40;

        // §6 — floodline salvage (the scatter; claim stakes and the rival
        // crew are CRACKEDLANDS_SALVAGE_CLAIM_CREW_1).
        public static bool floodlineSalvageEnabled = true;
        // TUNED: 3 days — "decaying fast" (review §H), shorter than the soak.
        public static float salvageDecayDays = 3f;

        // CRACKEDLANDS_FLORA_EXPANSION_BUILD_1 — six admitted flora in the wild roster
        // (applies at startup: off removes the rows on the next launch), and the
        // zennaq's pull on lightning strikes.
        public static bool floraExpansionEnabled = true;
        public static bool zennaqLightningPullEnabled = true;

        // CRACKEDLANDS_LEDGES_OF_MERCY_1 — refuge ledges: while the warning
        // stands and the water is up, neutral visitors and the player's
        // trained animals make for the nearest refuge ledge and are held
        // there. Inert on a map with no ledges (mercyLedgesEnabled cuts them
        // at map generation). Off = nobody seeks a ledge; the flood still
        // never takes a ledge cell.
        public static bool ledgeRefugeEnabled = true;
        // Chime-line anchors: the staged chimes toll from the anchor nearest
        // each staged position. Off (or no anchors on the map) = positions.
        public static bool chimeAnchorsEnabled = true;
        // Ledges cut into the cliff faces at map generation (with their
        // carving and chime-line anchors). Off = no ledges on new maps.
        public static bool mercyLedgesEnabled = true;
        // Reading a ledge carving gives a one-shot mood memory, once per
        // person per carving. Off = carvings are inspect text only.
        public static bool carvingMemoryEnabled = true;

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref featureInOtherBiomes, "featureInOtherBiomes", false, true);
            Scribe_Values.Look(ref floodCycleEnabled, "floodCycleEnabled", true, true);
            Scribe_Values.Look(ref floodPeriodDays, "floodPeriodDays", 20f, true);
            Scribe_Values.Look(ref chimeLeadTimeHours, "chimeLeadTimeHours", 2f, true);
            Scribe_Values.Look(ref floodDurationHours, "floodDurationHours", 6f, true);
            Scribe_Values.Look(ref floodDamageEnabled, "floodDamageEnabled", true, true);
            Scribe_Values.Look(ref growthCouplingEnabled, "growthCouplingEnabled", true, true);
            Scribe_Values.Look(ref soakDecayDays, "soakDecayDays", 4f, true);
            Scribe_Values.Look(ref fossilSeamsEnabled, "fossilSeamsEnabled", true, true);
            Scribe_Values.Look(ref fossilSeamsInOtherBiomes, "fossilSeamsInOtherBiomes", false, true);
            Scribe_Values.Look(ref fossilSeamDensity, "fossilSeamDensity", 1f, true);
            Scribe_Values.Look(ref floodRecutSeamsEnabled, "floodRecutSeamsEnabled", true, true);
            Scribe_Values.Look(ref floodRecutSeamCount, "floodRecutSeamCount", 4, true);
            Scribe_Values.Look(ref muttavaqWaterWakeEnabled, "muttavaqWaterWakeEnabled", true, true);
            Scribe_Values.Look(ref muttavaqDigInEnabled, "muttavaqDigInEnabled", true, true);
            Scribe_Values.Look(ref peakstormBiasEnabled, "peakstormBiasEnabled", true, true);
            Scribe_Values.Look(ref peakstormDustReversalEnabled, "peakstormDustReversalEnabled", true, true);
            Scribe_Values.Look(ref chimeStagingEnabled, "chimeStagingEnabled", true, true);
            Scribe_Values.Look(ref fiveBeatsEnabled, "fiveBeatsEnabled", true, true);
            Scribe_Values.Look(ref heraldLeadHours, "heraldLeadHours", 2f, true);
            Scribe_Values.Look(ref recedeFeastEnabled, "recedeFeastEnabled", true, true);
            Scribe_Values.Look(ref recedeMigrantsEnabled, "recedeMigrantsEnabled", true, true);
            Scribe_Values.Look(ref irqitCohortMax, "irqitCohortMax", 40, true);
            Scribe_Values.Look(ref floodlineSalvageEnabled, "floodlineSalvageEnabled", true, true);
            Scribe_Values.Look(ref salvageDecayDays, "salvageDecayDays", 3f, true);
            Scribe_Values.Look(ref floraExpansionEnabled, "floraExpansionEnabled", true, true);
            Scribe_Values.Look(ref zennaqLightningPullEnabled, "zennaqLightningPullEnabled", true, true);
            Scribe_Values.Look(ref ledgeRefugeEnabled, "ledgeRefugeEnabled", true, true);
            Scribe_Values.Look(ref chimeAnchorsEnabled, "chimeAnchorsEnabled", true, true);
            Scribe_Values.Look(ref mercyLedgesEnabled, "mercyLedgesEnabled", true, true);
            Scribe_Values.Look(ref carvingMemoryEnabled, "carvingMemoryEnabled", true, true);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPosition, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Biome rarity (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "biomeRarityFactor" }))
            {
                list.Label("Biome rarity: " + RarityLabel());
                list.Label("At 0 the flooded canyon never generates on a new planet. "
                           + "The default places a handful of rare canyon patches. Affects "
                           + "planets generated afterwards, never one that already exists.");
                biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
                list.GapLine();
            }

            if (Group(list, "Flood cycle", RimMandrake.Shared.SettingScope.Now, new[] { "floodCycleEnabled", "featureInOtherBiomes", "floodDamageEnabled" }))
            {
                list.CheckboxLabeled("Flood cycle enabled", ref floodCycleEnabled,
                    "The chime warning, the wall of water, and the soil it leaves behind. "
                    + "Off means the biome stays permanently dry.");
                list.CheckboxLabeled("Run the flood cycle in other biomes too", ref featureInOtherBiomes,
                    "Applies the flood cycle to EVERY map's biome, not only the flooded "
                    + "canyon — the mechanic without the biome.");
                list.CheckboxLabeled("The wall of water can hurt a caught pawn", ref floodDamageEnabled,
                    "A single light, non-fatal hit when the wall first reaches a pawn's cell. "
                    + "Never applied after that — standing water is just slow, not dangerous.");
                list.GapLine();
            }

            if (Group(list, "Warning: chimes and signs", RimMandrake.Shared.SettingScope.Now, new[] { "chimeStagingEnabled", "fiveBeatsEnabled", "heraldLeadHours", "chimeLeadTimeHours", "peakstormBiasEnabled", "peakstormDustReversalEnabled" }))
            {
                list.CheckboxLabeled("Chimes ring in stages as the water nears", ref chimeStagingEnabled,
                    "The first chime rings at the full warning lead time, then again at half "
                    + "of it, then once more just before the water arrives. Off means one "
                    + "chime only.");
                list.CheckboxLabeled("Five beats before water", ref fiveBeatsEnabled,
                    "Before the chimes: wind threads the slots, the sleeper pans start ticking, "
                    + "the tarruq fall silent. Then the chimes toll from the far canyon toward where "
                    + "the water will arrive, and the flood itself roars. Off means the chimes alone.");
                list.Label("Signs before the chimes: " + heraldLeadHours.ToString("0.0") + " h");
                heraldLeadHours = list.Slider(heraldLeadHours, 0.5f, 6f);
                list.Label("Chime warning lead time: " + chimeLeadTimeHours.ToString("0.0") + " h");
                chimeLeadTimeHours = list.Slider(chimeLeadTimeHours, 0.5f, 6f);
                list.CheckboxLabeled("Floods follow the peakstorm light", ref peakstormBiasEnabled,
                    "When the far skyline flickers with a storm on the peaks, the next flood "
                    + "often comes sooner — within two days or so — but not always. The chime still rings first. "
                    + "Never within half a flood period of the last one.");
                list.CheckboxLabeled("Peakstorm dust reverses", ref peakstormDustReversalEnabled,
                    "During peakstorm light the dust haze drifts one way, then every so often (about five seconds "
                    + "in every forty) swings round and flows back the other way. Off means it drifts one way only.");
                list.GapLine();
            }

            if (Group(list, "Flood timing", RimMandrake.Shared.SettingScope.NextPulse, new[] { "floodPeriodDays", "floodDurationHours" }))
            {
                list.Label("Days between floods: " + floodPeriodDays.ToString("0"));
                floodPeriodDays = list.Slider(floodPeriodDays, 6f, 60f);
                list.Label("Flood duration: " + floodDurationHours.ToString("0.0") + " h");
                floodDurationHours = list.Slider(floodDurationHours, 1f, 24f);
                list.GapLine();
            }

            if (Group(list, "Soaked ground", RimMandrake.Shared.SettingScope.Now, new[] { "growthCouplingEnabled" }))
            {
                list.CheckboxLabeled("The flood soaks the ground it wets", ref growthCouplingEnabled,
                    "Hands the flooded cells to RimMandrake: Explosive Plant Growth as soaked "
                    + "ground — its plants swell, charge and reach their top. Needs that mod; "
                    + "without it this does nothing. The growth multiplier is that mod's setting.");
                list.GapLine();
            }

            if (Group(list, "Fossil seams (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "fossilSeamsEnabled", "fossilSeamsInOtherBiomes", "fossilSeamDensity" }))
            {
                list.CheckboxLabeled("Fossil seams in the canyon walls (worldgen)", ref fossilSeamsEnabled,
                    "Seeds fossil-bearing strata into the rock wall faces of newly generated "
                    + "Cracked Lands maps — common impressions low on the faces, rarer "
                    + "articulated seams, deep-stratum seams only well inside the walls. "
                    + "Affects maps generated afterwards, never an existing one.");
                list.CheckboxLabeled("Fossil seams in other biomes too (worldgen)", ref fossilSeamsInOtherBiomes,
                    "Seeds the same strata into the walls of every newly generated map, "
                    + "not only the Cracked Lands.");
                list.Label("Fossil seam density: " + fossilSeamDensity.ToString("0.0") + "x");
                fossilSeamDensity = list.Slider(fossilSeamDensity, 0f, 4f);
                list.GapLine();
            }

            if (Group(list, "Muttavaq", RimMandrake.Shared.SettingScope.Now, new[] { "muttavaqWaterWakeEnabled", "muttavaqDigInEnabled" }))
            {
                list.CheckboxLabeled("The flood wakes a sleeping muttavaq", ref muttavaqWaterWakeEnabled,
                    "A muttavaq asleep under its pan wakes when water reaches it. Off means "
                    + "it only wakes when hurt.");
                list.CheckboxLabeled("A muttavaq digs back in at the dry", ref muttavaqDigInEnabled,
                    "After the flood is gone and its ground has dried, an awake muttavaq "
                    + "seals itself in where it stands and sleeps until the next flood.");
                list.GapLine();
            }

            if (Group(list, "After the water recedes", RimMandrake.Shared.SettingScope.NextPulse, new[] { "soakDecayDays", "floodRecutSeamsEnabled", "floodRecutSeamCount", "recedeFeastEnabled", "recedeMigrantsEnabled", "irqitCohortMax", "floodlineSalvageEnabled", "salvageDecayDays" }))
            {
                list.Label("Ground stays soaked for: " + soakDecayDays.ToString("0.0") + " days after the water recedes");
                soakDecayDays = list.Slider(soakDecayDays, 1f, 10f);
                list.CheckboxLabeled("The flood cuts fresh fossil seams", ref floodRecutSeamsEnabled,
                    "When the water recedes, a few rock wall cells along the wetted line "
                    + "turn into freshly exposed fossil seams — walls near the water line "
                    + "are worth walking after every flood.");
                list.Label("Fresh seams per flood: " + floodRecutSeamCount);
                floodRecutSeamCount = Mathf.RoundToInt(list.Slider(floodRecutSeamCount, 0f, 20f));
                list.CheckboxLabeled("The recede feast", ref recedeFeastEnabled,
                    "When the water recedes, an irqit carpet hatches on the wet ground and dies "
                    + "where it stands as the mud dries, leaving windrows of spent bodies.");
                list.CheckboxLabeled("Migrants fly in to feed", ref recedeMigrantsEnabled,
                    "This biome's own flying animals fly in to feed on the carpet and fly out "
                    + "again at the dry. They always arrive and leave by visible flight.");
                list.Label("Largest irqit carpet: " + irqitCohortMax);
                irqitCohortMax = Mathf.RoundToInt(list.Slider(irqitCohortMax, 0f, 120f));
                list.CheckboxLabeled("Floodline salvage", ref floodlineSalvageEnabled,
                    "The receding water exposes a few half-buried components and slag along "
                    + "the flood line. Unclaimed, the mud takes it back.");
                list.Label("Salvage lies exposed for: " + salvageDecayDays.ToString("0.0") + " days");
                salvageDecayDays = list.Slider(salvageDecayDays, 1f, 10f);
                list.GapLine();
            }

            if (Group(list, "Native plants", RimMandrake.Shared.SettingScope.Now, new[] { "floraExpansionEnabled" }, "[next game start]"))
            {
                list.CheckboxLabeled("Six extra native plants (restart to apply)", ref floraExpansionEnabled,
                    "Nabbuq, ruqqal, sevvuq, zennaq, luqqim and harrovaq in the wild roster. "
                    + "Off removes them from the roster on the next launch; the original plants stay.");
                list.GapLine();
            }

            if (Group(list, "Zennaq and lightning", RimMandrake.Shared.SettingScope.Now, new[] { "zennaqLightningPullEnabled" }))
            {
                list.CheckboxLabeled("Lightning is drawn to zennaq", ref zennaqLightningPullEnabled,
                    "A random lightning strike that would land near a zennaq plant lands on it instead. "
                    + "Zennaq is dry as tinder, so a storm on the mesa tops can start a fire.");
                list.GapLine();
            }

            if (Group(list, "Refuge ledges and carvings", RimMandrake.Shared.SettingScope.Now, new[] { "ledgeRefugeEnabled", "chimeAnchorsEnabled", "carvingMemoryEnabled" }))
            {
                list.CheckboxLabeled("Visitors and trained animals climb to the refuge ledges", ref ledgeRefugeEnabled,
                    "From the first sign of a flood until the water recedes, neutral visitors and your "
                    + "trained animals run for the nearest reachable refuge ledge and wait on it. The flood "
                    + "never covers a ledge. Only matters on a map that has ledges. "
                    + "PROVISIONAL numbers: they re-check every 250 ticks (a tenth of an hour), test the 12 "
                    + "nearest ledge cells for a path, and wait 500 ticks at a time.");
                list.CheckboxLabeled("Chimes ring from the chime-line anchors", ref chimeAnchorsEnabled,
                    "Where the canyon has chime-line anchors, each staged chime tolls from the anchor nearest "
                    + "its point on the line toward the water. Off, or with no anchors, the chime tolls "
                    + "from the point itself.");
                list.CheckboxLabeled("Reading a ledge carving lifts the mood", ref carvingMemoryEnabled,
                    "A person who comes within a couple of cells of a ledge carving and can see it reads it once "
                    + "and gains a small mood memory. PROVISIONAL numbers: +4 mood for 2 days.");
                list.GapLine();
            }

            if (Group(list, "Cliff ledges (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "mercyLedgesEnabled" }))
            {
                list.CheckboxLabeled("Ledges cut into the cliff faces (worldgen)", ref mercyLedgesEnabled,
                    "Newly generated canyon maps get a few refuge ledges carved into high rock faces, each "
                    + "with a carving and a chime-line anchor, plus more anchors along the walls. Also on other "
                    + "biomes when the flood runs there. Affects maps generated afterwards, never an existing one. "
                    + "PROVISIONAL numbers: about 3 ledges on a 250x250 map (2 to 6), at least 30 cells apart.");
                list.GapLine();
            }

            viewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }

        private static Vector2 scrollPosition = Vector2.zero;
        private static float viewHeight = 1200f;

        private static string RarityLabel()
        {
            if (biomeRarityFactor <= 0.001f) return "never generates";
            if (biomeRarityFactor < 0.6f) return "very rare (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 1.6f) return "default, a handful of patches (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 4f) return "uncommon (" + biomeRarityFactor.ToString("0.0") + "x)";
            return "common (" + biomeRarityFactor.ToString("0.0") + "x)";
        }


        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int/string/enum setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_FloodedCanyonSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int) || f.FieldType == typeof(string) || f.FieldType.IsEnum)
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_FloodedCanyonSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the biome rarity, the fossil seam seeding and the cliff ledges run once when a map is generated, so [new maps only]; the flood schedule (days between floods), the flood duration, and everything the receding water does (soak, fresh seams, the feast, salvage) are rolled when the next flood is scheduled, begins or recedes, so [next pulse]; the six extra plants are removed from the wild roster at startup (their own label says restart), so [next game start]; the warning beats, the flood cycle switches, the muttavaq, ledge seeking and carving memory are read each tick by the map component, comp or job, so [now].</summary>
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
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }
    }

    public class RM_FloodedCanyonMod : Mod
    {
        public static RM_FloodedCanyonSettings settings;

        public RM_FloodedCanyonMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_FloodedCanyonSettings>();
            // CRACKEDLANDS_GPT_ENRICHMENT_1 §2: the tarruq hush (RM_TarruqHushPatch).
            RimMandrake.Shared.PatchApplier.Apply(new HarmonyLib.Harmony("mandrake.rm.biomes.floodedcanyon"), typeof(RM_FloodedCanyonMod).Assembly, "RimMandrake.FloodedCanyon");
        }

        public override string SettingsCategory()
        {
            return "Flooded Canyon";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
