using System.Reflection;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — the ruled rarity slider and the two ruled flavor hooks.
    //
    // Spec §2, round 2: "worldgen 1-3 rare patches + rarity slider ... Engine:
    // the standard Mod + ModSettings classes — precedent already verified
    // in-repo: the decompiled GenepacksInjection mod's
    // GenepacksInjectionMod.Settings.UseEndogenes toggle."
    // Spec §10, ruled round 2: "BOTH flavor hooks SHIP as mod-settings
    // toggles — the 'Entry recorded' registry flavor and the read-mark scars
    // are options, ON BY DEFAULT [default state INVENTED]."
    //
    // 🔑 STATIC FIELDS, READ FROM EVERYWHERE, WRITTEN ONLY HERE. The biome
    // worker runs during worldgen when no Mod instance may be handy, so the
    // values have to be statics that survive a settings load — hence the
    // Scribe_Values pattern below rather than instance fields.
    // ════════════════════════════════════════════════════════════════════
    public class SlimeSettings : ModSettings
    {
        // 1.0 = the ruled default (1-3 rare patches on a default planet).
        // 0 = the biome never generates at all. 8 = common.
        public static float rarityFactor = 1f;

        // "Entry recorded" — the body acknowledges what it just read.
        public static bool flavorEntryRecorded = true;

        // Read-marks: the smear a slimified creature leaves where it walked.
        public static bool flavorReadMarks = true;


        // ── TITANOSLIME (TITANOSLIME_SLIME_BIOME_1, spec §5) ────────────
        // Project rule: every mod ships a real settings screen — on/off per
        // major feature, tuning where a number is the experience, defaults =
        // shipped behaviour, all-off degrades gracefully. All-off here leaves
        // a slow, big, slam-only predator that still works.

        // Rarity of the titanoslime in any biome that rosters it. Applied by
        // rewriting the LOADED BiomeDef's wildAnimals commonality — see
        // TitanoslimeSpawnTuning below.
        public static float titanoslimeSpawnFactor = 1f;

        // Off: the engulf tool always slams, and anything already held is
        // released on the next round.
        public static bool titanoslimeEngulfs = true;

        // Off: absorbedMass is frozen at its spawn value; the creature keeps
        // whatever stage it rolled and never moves off it.
        public static bool titanoslimeGrows = true;

        // SLIME_GENE_ARCHIVE_BUILD_1: on (default) is the shipped mechanism
        // GeneArchiveDef.priority exists for — the highest-priority archive
        // with any targetGenes wins, so the campaign's own frozen gene
        // lists (RUT_SlimeGeneArchive, priority 100) replace this mod's
        // 17-entry universal default (priority 0) with no patch. Off: this
        // mod ignores any higher-priority archive and always offers its own
        // universal list, even in a campaign that ships a better one.
        public static bool preferHigherPriorityArchive = true;

        // On: mass can decrease again — starving, dry ground and wounds take
        // it back, so nothing is permanently huge. OFF is the owner's shipped
        // default (ruling, 2026-09-21, TITANOSLIME_SLIME_BIOME_1): growth is
        // permanent, not reversible — once it grows it stays huge, a fed
        // slime is a permanently escalating threat. Overturns the spec's
        // original "reversible: yes" default (§11 answer 4).
        public static bool titanoslimeReversible = false;

        // 1-5. Caps the ladder; at 2, absorbedMass 12 still reads as stage 2.
        public static int titanoslimeMaxStage = 5;

        // Off: a cut titanoslime stops leaking gelatids.
        public static bool titanoslimeSheds = true;

        // ── SLIMIFICATION / FARMS / VISITORS (GELATINOUSSLIME_SETTINGS_SWITCHES_1) ──
        // Off = a body you can stand on: no film is applied, none grows, and
        // anything already on a pawn only wipes off or leaches away.
        public static bool slimificationEnabled = true;

        // Days for the film to read a pawn standing on the body (shipped ~7;
        // the injected dose scales with it). 2-30.
        public static float slimificationClockDays = 7f;

        // Off: sown fields on slime-grass stay slime-grass.
        public static bool fieldConversionEnabled = true;

        // Multiplier on how many cells are tried per pass. 0.25-4.
        public static float fieldConversionRate = 1f;

        // GELATINOUSSLIME_FARM_RUINS_1 (WORLDGEN-AFFECTING: applies to maps generated afterwards).
        // Off: no ruined farms are placed on a newly generated slime map.
        public static bool farmRuinsEnabled = true;

        // Off: no wandering arrivals and no map-generation seed pass.
        public static bool visitorsEnabled = true;

        // Multiplier on the arrival chance. 0.25-4.
        public static float visitorArrivalRate = 1f;

        // GELATINOUSSLIME_GAPPO_FAMILY_1: the greater gappo hardens the slime it grazes into a
        // clean channel. Off: it still grazes, the ground is left as it was.
        public static bool gappoChannels = true;

        // GELATINOUSSLIME_FUBBUM_HUNTER_1: the fubbum hunts gelatid herds. Off: it is a placid
        // grazer-of-nothing that ignores prey (race.predator false); applied by FubbumHunting.
        public static bool fubbumHunts = true;

        // GELATINOUSSLIME_DWOMMO_FLIER_1: the dwommo flies. Off: MaxFlightTime 0, it stays grounded;
        // applied by DwommoFlight.
        public static bool dwommoFlies = true;

        // GELATINOUSSLIME_PIT_SOLVENT_1: the slime pit offers the solvent recipes (toxipotatoes, twisted
        // meat). Off: only the original slime-to-meal bill (applied by PitSolvent).
        public static bool pitSolvent = true;

        // GELATINOUSSLIME_VAULT_SEAL_BREACH_1: a titanoslime chunk dissolves a slime-breachable seal. Off: the chunk does nothing.
        public static bool sealBreach = true;

        // GELATINOUSSLIME_TITAN_CHUNK_BOMB_1: a thrown titanoslime chunk bursts (drench + slime ground). Off: a thrown chunk lands inert.
        public static bool chunkBomb = true;

        // Days a chunk keeps off the body before it runs to slime (applies to every chunk, seal use included).
        public static float chunkShelfDays = 1.5f;

        // GELATINOUSSLIME_ARCHIVE_RESURRECTION_1: the body files each colonist it reads, and the archive vat can grow a dead one back from the last entry. Off: no new entries, the vat does nothing.
        public static bool archiveResurrection = true;

        // GELATINOUSSLIME_JOINING_WATER_STANDALONE_1: the found hand-ring on a Slime map and the rite's spreading of permanent hurts. Worldgen-affecting (the ring is placed at generation). Off: no ring, and the rite shares nothing.
        public static bool joiningWaterEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref joiningWaterEnabled, "joiningWaterEnabled", true, true);
            Scribe_Values.Look(ref pitSolvent, "pitSolvent", true, true);
            Scribe_Values.Look(ref sealBreach, "sealBreach", true, true);
            Scribe_Values.Look(ref chunkBomb, "chunkBomb", true, true);
            Scribe_Values.Look(ref chunkShelfDays, "chunkShelfDays", 1.5f, true);
            Scribe_Values.Look(ref archiveResurrection, "archiveResurrection", true, true);
            Scribe_Values.Look(ref gappoChannels, "gappoChannels", true, true);
            Scribe_Values.Look(ref fubbumHunts, "fubbumHunts", true, true);
            Scribe_Values.Look(ref dwommoFlies, "dwommoFlies", true, true);
            Scribe_Values.Look(ref preferHigherPriorityArchive, "preferHigherPriorityArchive", true, true);
            Scribe_Values.Look(ref rarityFactor, "rarityFactor", 1f, true);
            Scribe_Values.Look(ref flavorEntryRecorded, "flavorEntryRecorded", true, true);
            Scribe_Values.Look(ref flavorReadMarks, "flavorReadMarks", true, true);
            Scribe_Values.Look(ref titanoslimeSpawnFactor, "titanoslimeSpawnFactor", 1f, true);
            Scribe_Values.Look(ref titanoslimeEngulfs, "titanoslimeEngulfs", true, true);
            Scribe_Values.Look(ref titanoslimeGrows, "titanoslimeGrows", true, true);
            Scribe_Values.Look(ref titanoslimeReversible, "titanoslimeReversible", false, true);
            Scribe_Values.Look(ref titanoslimeMaxStage, "titanoslimeMaxStage", 5, true);
            Scribe_Values.Look(ref titanoslimeSheds, "titanoslimeSheds", true, true);
            Scribe_Values.Look(ref slimificationEnabled, "slimificationEnabled", true, true);
            Scribe_Values.Look(ref slimificationClockDays, "slimificationClockDays", 7f, true);
            Scribe_Values.Look(ref fieldConversionEnabled, "fieldConversionEnabled", true, true);
            Scribe_Values.Look(ref fieldConversionRate, "fieldConversionRate", 1f, true);
            Scribe_Values.Look(ref farmRuinsEnabled, "farmRuinsEnabled", true, true);
            Scribe_Values.Look(ref visitorsEnabled, "visitorsEnabled", true, true);
            Scribe_Values.Look(ref visitorArrivalRate, "visitorArrivalRate", 1f, true);
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1200f;

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "The gene archive", RimMandrake.Shared.SettingScope.Now, new[] { "preferHigherPriorityArchive" }))
            {
                list.CheckboxLabeled("Prefer the higher-priority gene archive", ref preferHigherPriorityArchive,
                    "On (default): if another mod or the campaign ships its own gene archive with a "
                    + "higher priority than this mod's own 17-entry universal one, the gene machine "
                    + "offers that archive instead — this is how a campaign swaps in its own gene "
                    + "lists with no patch. Off: always use this mod's own universal archive, even "
                    + "if a higher-priority one is loaded.");
                list.GapLine();
            }

            if (Group(list, "Biome rarity (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "rarityFactor" }))
            {
                list.Label("Biome rarity: " + RarityLabel());
                list.Label("At 0 the gelatinous slime never generates on a new planet. "
                           + "The default places roughly one to three rare patches. "
                           + "Changing this affects planets generated afterwards, never "
                           + "one that already exists.");
                rarityFactor = list.Slider(rarityFactor, 0f, 8f);
                list.GapLine();
            }

            if (Group(list, "Flavour", RimMandrake.Shared.SettingScope.Now, new[] { "flavorEntryRecorded", "flavorReadMarks" }))
            {
                list.CheckboxLabeled("\"Entry recorded\" messages", ref flavorEntryRecorded,
                    "The body acknowledges each genome it finishes filing.");
                list.CheckboxLabeled("Read-marks", ref flavorReadMarks,
                    "Slimified creatures leave a smear where they have walked.");
                list.GapLine();
            }

            if (Group(list, "Slimification and fields", RimMandrake.Shared.SettingScope.Now, new[] { "slimificationEnabled", "slimificationClockDays", "fieldConversionEnabled", "fieldConversionRate" }))
            {
                list.CheckboxLabeled("Slimification", ref slimificationEnabled,
                    "On (default): standing on the body slowly reads a creature into it. "
                    + "Off: nothing is applied or grows, so the slime is ground you can stand on; "
                    + "any film already on a pawn just wipes off.");
                list.Label("Days to be read: " + slimificationClockDays.ToString("0.0")
                           + " (shipped 7). Shorter is deadlier; the injected dose scales with it.");
                slimificationClockDays = Mathf.Round(list.Slider(slimificationClockDays, 2f, 30f) * 2f) / 2f;
                list.CheckboxLabeled("Farm conversion", ref fieldConversionEnabled,
                    "On (default): sown fields on slime-grass revert to ordinary slime ground over "
                    + "a few harvests. Off: fields stay as laid.");
                list.Label("Conversion rate: " + fieldConversionRate.ToString("0.00") + "x");
                fieldConversionRate = list.Slider(fieldConversionRate, 0.25f, 4f);
                list.GapLine();
            }

            if (Group(list, "Ruined farms (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "farmRuinsEnabled" }))
            {
                list.CheckboxLabeled("Ruined farms (affects newly generated maps)", ref farmRuinsEnabled,
                    "On (default): a newly generated slime map holds two to four failed farms half "
                    + "sunk into slime-grass: fence stubs, a dead irrigation channel, a collapsed "
                    + "shed and a little left behind. Off: none are placed. WORLDGEN-AFFECTING: "
                    + "changes only maps generated afterwards, never one that already exists.");
                list.GapLine();
            }

            if (Group(list, "Joining Water ring", RimMandrake.Shared.SettingScope.Now, new[] { "joiningWaterEnabled" }))
            {
                list.CheckboxLabeled("Joining Water ring", ref joiningWaterEnabled,
                    "On (default): a newly generated slime map holds a ring of hand-prints pressed into hardened slime, where the clan's "
                    + "Joining Water rite can be held, and the rite shares one person's lasting hurts out among the ring as weak, passing ones. "
                    + "Off: no ring is placed on maps generated afterwards, and the rite shares nothing on any map, rings already placed included.");
                list.GapLine();
            }

            if (Group(list, "Visitors", RimMandrake.Shared.SettingScope.Now, new[] { "visitorsEnabled", "visitorArrivalRate" }))
            {
                list.CheckboxLabeled("Visitors", ref visitorsEnabled,
                    "On (default): placid, part-read wild animals wander onto a slime map. "
                    + "Off: none arrive and the map opens without them.");
                list.Label("Arrival rate: " + visitorArrivalRate.ToString("0.00") + "x");
                visitorArrivalRate = list.Slider(visitorArrivalRate, 0.25f, 4f);
                list.GapLine();
            }

            if (Group(list, "Creatures and the slime pit", RimMandrake.Shared.SettingScope.Now, new[] { "gappoChannels", "fubbumHunts", "dwommoFlies", "pitSolvent" }))
            {
                list.CheckboxLabeled("Greater gappo clears channels", ref gappoChannels,
                    "On (default): the greater gappo's scoop hardens the soft slime under it and wipes "
                    + "the smear, leaving a clean channel behind it. Off: it grazes and the ground is "
                    + "left as it was.");
                list.CheckboxLabeled("Fubbum hunts gelatids", ref fubbumHunts,
                    "On (default): the fubbum, the Slime's one hunter, stalks the gelatid herds. It "
                    + "never hunts colonists first. Off: it stays on the map but hunts nothing.");
                list.CheckboxLabeled("Dwommo flies", ref dwommoFlies,
                    "On (default): the dwommo, the Slime's gas-float aristocracy, drifts over the body in "
                    + "real flight. Off: it stays on the map but never leaves the ground.");
                list.CheckboxLabeled("Slime pit as a solvent", ref pitSolvent,
                    "On (default): the slime pit also renders toxipotatoes and twisted meat safe to eat. "
                    + "Off: the pit only makes simple meals from raw slime.");
                list.GapLine();
            }

            if (Group(list, "Titanoslime chunks and the archive vat", RimMandrake.Shared.SettingScope.Now, new[] { "sealBreach", "chunkBomb", "chunkShelfDays", "archiveResurrection" }))
            {
                list.CheckboxLabeled("Titanoslime chunk breaches seals", ref sealBreach,
                    "On (default): a chunk cut from a titanoslime dissolves an Assailant seal and drenches the "
                    + "doorway in slime. Off: the chunk does nothing and seals stay shut.");
                list.CheckboxLabeled("Titanoslime chunk is a thrown bomb", ref chunkBomb,
                    "On (default): a chunk thrown by a pawn bursts, drenching everyone near it to a late stage of "
                    + "slimification and turning the ground to slime for a day. No armour stops it; dry ground and "
                    + "the antidote undo it. Off: a thrown chunk lands inert.");
                list.Label("Chunk keeps for: " + chunkShelfDays.ToString("0.0") + " days off the body");
                chunkShelfDays = Mathf.Round(list.Slider(chunkShelfDays, 0.5f, 5f) * 10f) / 10f;
                list.CheckboxLabeled("Archive resurrection", ref archiveResurrection,
                    "On (default): every time the body reads a colonist it files them as they were, and an "
                    + "archive vat can grow a dead one back from that last entry, with no memory of anything since. "
                    + "Off: no new entries are filed and the vat does nothing; entries already filed are kept.");
                list.GapLine();
            }

            if (Group(list, "The titanoslime", RimMandrake.Shared.SettingScope.Now, new[] { "titanoslimeEngulfs", "titanoslimeGrows", "titanoslimeReversible", "titanoslimeSheds", "titanoslimeMaxStage" }))
            {
                list.Label("A titanic green slime that swallows pawns whole and grows on what "
                           + "it absorbs. With every box below unticked it is still a large, "
                           + "slow predator that slams — nothing breaks, it just stops being "
                           + "the thing it was built to be.");
                list.CheckboxLabeled("Swallow pawns whole", ref titanoslimeEngulfs,
                    "On: a titanoslime that hits with its engulfing mass takes the target "
                    + "inside itself and digests it. Off: that attack is an ordinary slam, "
                    + "and anything already held is released.");
                list.CheckboxLabeled("Grows as it eats", ref titanoslimeGrows,
                    "On: absorbing prey, and ordinary eating, move it up a five-stage ladder "
                    + "from body size 6 to 40. Off: it keeps the stage it spawned at.");
                list.CheckboxLabeled("Growth is reversible", ref titanoslimeReversible,
                    "Off (default): the ladder only climbs — starving, standing off slime "
                    + "terrain and being wounded never take mass back, so a fed titanoslime "
                    + "is a permanent, escalating threat. On: all three take mass back, so "
                    + "nothing is permanently huge.");
                list.CheckboxLabeled("Sheds gelatids when cut", ref titanoslimeSheds,
                    "On: a wounded titanoslime of stage 2 or better comes apart into wild "
                    + "gelatids as you fight it, losing mass with each one.");
                list.Label("Largest stage it can reach: " + MaxStageLabel());
                titanoslimeMaxStage = Mathf.RoundToInt(list.Slider(titanoslimeMaxStage, 1f, 5f));
                list.GapLine();
            }

            if (Group(list, "Titanoslime rarity (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "titanoslimeSpawnFactor" }))
            {
                list.Label("Titanoslime rarity: " + TitanoslimeRarityLabel());
                list.Label("Multiplies how often a titanoslime spawns in any biome that lists "
                           + "one. At 0 none ever spawns. Takes effect on the next map "
                           + "generated; a titanoslime already on a map is unaffected.");
                titanoslimeSpawnFactor = list.Slider(titanoslimeSpawnFactor, 0f, 3f);
                list.GapLine();
            }

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(SlimeSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(SlimeSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. A search matches the section title or any of its setting names. Scope AUDITED per setting against its
        /// read site (2026-10-10): the biome rarity, the ruined farms and the titanoslime spawn weight are read while a map is generated ([new maps only]); the fubbum, dwommo and pit-solvent switches are re-applied to the loaded defs when the window closes, and every other setting is read by a tick, job, hediff, comp or interaction ([now]).</summary>
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
            // tagOverride "[next game start]": the kit has no such scope; these are read while defs load or when a game loads.
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        private static string MaxStageLabel()
        {
            switch (titanoslimeMaxStage)
            {
                case 1: return "1 — young titanoslime (body size 6)";
                case 2: return "2 — titanoslime (body size 10)";
                case 3: return "3 — great titanoslime (body size 16)";
                case 4: return "4 — elder titanoslime (body size 24)";
                default: return "5 — titanoslime colossus (body size 40)";
            }
        }

        private static string TitanoslimeRarityLabel()
        {
            if (titanoslimeSpawnFactor <= 0.001f) return "never spawns";
            if (titanoslimeSpawnFactor < 0.6f) return "very rare ("
                + titanoslimeSpawnFactor.ToString("0.0") + "x)";
            if (titanoslimeSpawnFactor < 1.6f) return "default ("
                + titanoslimeSpawnFactor.ToString("0.0") + "x)";
            return "common (" + titanoslimeSpawnFactor.ToString("0.0") + "x)";
        }

        private static string RarityLabel()
        {
            if (rarityFactor <= 0.001f) return "never generates";
            if (rarityFactor < 0.6f) return "very rare (" + rarityFactor.ToString("0.0") + "x)";
            if (rarityFactor < 1.6f) return "default, 1-3 patches (" + rarityFactor.ToString("0.0") + "x)";
            if (rarityFactor < 4f) return "uncommon (" + rarityFactor.ToString("0.0") + "x)";
            return "common (" + rarityFactor.ToString("0.0") + "x)";
        }
    }

    public class SlimeMod : Mod
    {
        public static SlimeSettings settings;

        public SlimeMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<SlimeSettings>();
        }

        public override string SettingsCategory()
        {
            return "The Gelatinous Slime";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        // Settings close -> re-apply the titanoslime rarity to the loaded
        // BiomeDefs, so the slider does not need a game restart.
        public override void WriteSettings()
        {
            base.WriteSettings();
            TitanoslimeSpawnTuning.Apply();
            FubbumHunting.Apply();
            DwommoFlight.Apply();
            PitSolvent.Apply();
            GeneArchiveDef.InvalidateActiveCache();
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // DEFS THIS ASSEMBLY NAMES.
    //
    // 🔴 GetNamedSilentFail, NOT [DefOf], AND THAT IS DELIBERATE. A [DefOf]
    // field for a Biotech-gated def logs a hard error on every load of a game
    // without Biotech, and About.xml promises that game works unchanged. The
    // resolver below returns null instead, and every caller is written to
    // no-op on null.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class SlimeDefs
    {
        public const string SlimeTerrainTag = "RM_SlimeTerrain";

        public static readonly BiomeDef GelatinousSlime =
            DefDatabase<BiomeDef>.GetNamedSilentFail("RM_GelatinousSlime");

        public static readonly HediffDef Slimification =
            DefDatabase<HediffDef>.GetNamedSilentFail("RM_Slimification");

        public static readonly HediffDef SlimeMarked =
            DefDatabase<HediffDef>.GetNamedSilentFail("RM_SlimeMarked");

        public static readonly HediffDef XenogerminationComa =
            DefDatabase<HediffDef>.GetNamedSilentFail("XenogerminationComa");

        public static readonly ThingDef RawSlime =
            DefDatabase<ThingDef>.GetNamedSilentFail("RM_RawSlime");

        public static readonly ThingDef SlimeSmear =
            DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_SlimeSmear");

        public static readonly ThingDef GeneSeekerLoaded =
            DefDatabase<ThingDef>.GetNamedSilentFail("RM_GeneSeeker_Loaded");

        public static readonly TerrainDef SlimeRich =
            DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Slime_Rich");

        public static readonly TerrainDef SlimeGrass =
            DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Slime_Grass");

        public static readonly TerrainDef SlimeLiquid =
            DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Slime_Liquid");

        // SLIME_GENE_ARCHIVE_BUILD_1 — the two P7-named exceptions
        // (the_slime_gene_lists.md): B25 doubles the Slime-marked
        // increment, A16 fights it to a draw. GetNamedSilentFail, not
        // [DefOf]: both genes are Biotech-gated and this mod must still
        // load clean without Biotech.
        public static readonly GeneDef TheReek =
            DefDatabase<GeneDef>.GetNamedSilentFail("RM_Gene_B25_TheReek");

        public static readonly GeneDef PheromoneCharm =
            DefDatabase<GeneDef>.GetNamedSilentFail("RM_Gene_A16_PheromoneCharm");
    }
}
