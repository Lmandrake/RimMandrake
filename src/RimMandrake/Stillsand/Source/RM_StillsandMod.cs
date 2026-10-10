using System.Collections.Generic;
using System.Reflection;
using static RimMandrake.Stillsand.RM_PreciousCaveSettings;
using static RimMandrake.Stillsand.RM_StillsandWaterSettings;
using static RimMandrake.Stillsand.RM_SandSwimRemSettings;
using static RimMandrake.Stillsand.RM_DuneTrackEraserSettings;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Stillsand.
    //
    // Precedent: src/RimMandrake/FeverWood/Source/RM_FeverWoodMod.cs.
    //
    // The biome itself reuses vanilla Core's BiomeWorker_ExtremeDesert unchanged,
    // so there is no placement score to gate. The one mechanic this assembly
    // owns besides the sand-buster eruption is the zuurrik blood-waker
    // (STILLSAND_BEDAZZLE_CONTENT_1), which has a toggle and a threshold, and the
    // rock-and-cave gen steps (STILLSAND_PRECIOUS_CAVES_1, RM_PreciousCaveSettings). Defaults
    // are the shipped behaviour; all-off leaves the biome whole (the zuurrik
    // def is then simply never woken).
    // ════════════════════════════════════════════════════════════════════
    public class RM_StillsandSettings : ModSettings
    {
        /// <summary>Master toggle for the zuurrik: blood on sand wakes a stripping swarm.</summary>
        public static bool zuurrikEnabled = true;

        /// <summary>Stained sand cells within one cluster that wake a swarm.</summary>
        public static int zuurrikBloodThreshold = 8;

        /// <summary>ZUURRIK_GROWTH_BY_FEEDING_1: the next swarm grows by what this one really ate.
        /// PROVISIONAL (auto-decided 2026-10-09, ZUURRIK_GROWTH_BY_FEEDING_1). Off: by the stain it woke to.</summary>
        public static bool zuurrikGrowByFeeding = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref zuurrikEnabled, "zuurrikEnabled", true);
            Scribe_Values.Look(ref zuurrikBloodThreshold, "zuurrikBloodThreshold", 8);
            Scribe_Values.Look(ref zuurrikGrowByFeeding, "zuurrikGrowByFeeding", true);
            RM_PreciousCaveSettings.Expose(); // STILLSAND_PRECIOUS_CAVES_1
            RM_StillsandWaterSettings.Expose(); // STILLSAND_RETURN_RITUAL_1
            RM_SandSwimRemSettings.Expose(); // STILLSAND_SAND_SWIM_REMAINDER_1
            RM_DuneTrackEraserSettings.Expose(); // FOOTPRINT_TRACK_GRID_1
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order). The screen also
        // draws the settings of the four static helper classes below, so their fields are snapshotted and reset here too.
        private static readonly System.Type[] settingTypes =
        {
            typeof(RM_StillsandSettings), typeof(RM_PreciousCaveSettings), typeof(RM_StillsandWaterSettings),
            typeof(RM_SandSwimRemSettings), typeof(RM_DuneTrackEraserSettings)
        };

        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (System.Type t in settingTypes)
                foreach (FieldInfo f in t.GetFields(BindingFlags.Public | BindingFlags.Static))
                    if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                        d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                if (n == "rowEnabled") { RM_PreciousCaveSettings.rowEnabled.Clear(); continue; }
                if (n == "rowWeight") { RM_PreciousCaveSettings.rowWeight.Clear(); continue; }
                foreach (System.Type t in settingTypes)
                {
                    FieldInfo f = t.GetField(n, BindingFlags.Public | BindingFlags.Static);
                    if (f != null && shippedDefaults.TryGetValue(n, out object v)) { f.SetValue(null, v); break; }
                }
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1400f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): map-generation steps (cave carving, yardang,
        /// tor, wall ring, tribal mark, drip, cave-row rolls) are NewMapsOnly; the debt-weighted incident roll is NextPulse; the rest
        /// (zuurrik, cave preservation, water bloom and ledger, thumper, swimmers, listening, track eraser) are read per tick or call.</summary>
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
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            list.Label("The biome itself reuses vanilla Core's BiomeWorker_ExtremeDesert unchanged, "
              + "so there is no natural-placement score of this mod's own to toggle. The event "
              + "creatures (muurrok, krayt attack) have their own panel: \"Stillsand: event creatures\".");
            list.GapLine();

            if (Group(list, "Zuurrik (blood on the sand)", RimMandrake.Shared.SettingScope.Now, new[] { "zuurrikEnabled", "zuurrikBloodThreshold", "zuurrikGrowByFeeding" }))
            {
                list.CheckboxLabeled("Blood on the sand wakes the zuurrik",
                    ref zuurrikEnabled,
                    "On a Stillsand map, enough fresh blood on sand wakes a swarm that strips the stain "
                    + "and the bodies beside it, then re-buries. Never attacks the unwounded. Off: the "
                    + "zuurrik never wakes.");
                if (zuurrikEnabled)
                {
                    list.Label("Stained cells needed to wake a swarm: " + zuurrikBloodThreshold);
                    zuurrikBloodThreshold = (int)list.Slider(zuurrikBloodThreshold, 2, 40);
                    list.CheckboxLabeled("Swarms grow by what they eat", ref zuurrikGrowByFeeding,
                        "On: the next swarm is bigger by the stains and bodies this one actually stripped; a stain your "
                        + "colonists cleaned first feeds nothing. Off: it grows by the size of the stain it woke to.");
                }
                list.GapLine();
            }

            if (Group(list, "Precious cave: carving and set pieces (fixed at map generation)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "genStepEnabled", "yardangShapingEnabled", "torEnabled", "torChance", "dripEnabled", "wallRingEnabled", "tribalMarkEnabled" }))
            {
                list.CheckboxLabeled("Carve a cave into the map's largest outcrop", ref genStepEnabled,
                    "Off: the Stillsand generates its rock as before, with no cave, no table roll and no landing letter.");
                list.CheckboxLabeled("Shape the outcrop as a wind-aligned yardang", ref yardangShapingEnabled,
                    "Trims and fills the largest outcrop into a long, tapering ridge laid along the one wind. Off: the outcrop keeps its generated shape; the cave is still carved.");
                list.CheckboxLabeled("Seat a small tor on rockless maps", ref torEnabled,
                    "When a map has no rock at all, sometimes raise one small yardang tor so the map still has its landmark.");
                if (torEnabled)
                {
                    list.Label("Rockless-map tor chance: " + torChance.ToStringPercent());
                    torChance = list.Slider(torChance, 0f, 1f);
                }
                list.CheckboxLabeled("The cave drips", ref dripEnabled,
                    "Each new cave carries one ambient water-drip sound, the only water sound in the biome. New maps only.");
                list.CheckboxLabeled("Lens grotto: grown-biosilica walls", ref wallRingEnabled,
                    "The lens grotto rings its chamber with mineable biosilica wall. Off: the grotto is bare rock. New maps only.");
                list.CheckboxLabeled("Taken cave: tribal mark on the wall", ref tribalMarkEnabled,
                    "The emptied cave carries its own tribal glyph. New maps only.");
                list.GapLine();
            }

            if (Group(list, "Precious cave: what it holds (fixed at map generation)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "rowEnabled", "rowWeight" }))
            {
                list.Label("What the cave holds (one weighted roll per cave):");
                RM_PreciousCaveSettings.DrawRows(list);
                list.GapLine();
            }

            if (Group(list, "Nothing rots in the cave", RimMandrake.Shared.SettingScope.Now, new[] { "preservationEnabled" }))
            {
                list.CheckboxLabeled("Nothing rots in the cave", ref preservationEnabled,
                    "Corpses and food lying on a roofed cave cell do not rot, and desiccated remains stay. Acts live, on existing caves too. Off: vanilla rot resumes.");
                list.GapLine();
            }

            if (Group(list, "Water on the sand", RimMandrake.Shared.SettingScope.Now, new[] { "bloomOnPour", "ledgerEnabled" }))
            {
                list.CheckboxLabeled("Poured water blooms", ref bloomOnPour,
                    "Water poured onto Stillsand sand sows a short-lived bloom along the pour. Off: the sand only gets wet "
                    + "(a fresh pour still draws the swimmers).");
                // The ledger rows exist only when a tier above ships a ledger def: the RM
                // tier has no debt and shows no debt UI.
                RM_WaterLedgerDef ledger = RM_WaterLedger.ActiveDef;
                if (ledger != null)
                {
                    list.CheckboxLabeled(ledger.LabelCap + ": count the water drawn", ref ledgerEnabled,
                        "Off: drinking and drawing water on these maps adds nothing to " + ledger.label
                        + ", its mood line and goodwill stop moving, and it never opens a ritual.");
                }
                list.GapLine();
            }

            if (Group(list, "Water debt weights the sand's events", RimMandrake.Shared.SettingScope.NextPulse, new[] { "ledgerIncidentWeighting" }))
            {
                RM_WaterLedgerDef ledger2 = RM_WaterLedger.ActiveDef;
                if (ledger2 != null)
                {
                    list.CheckboxLabeled(ledger2.LabelCap + " weights the sand's events", ref ledgerIncidentWeighting,
                        "Unpaid debt raises the odds of the biome's leviathans and sand-buster eruptions. Off: odds ignore the debt.");
                }
                else
                {
                    list.Label("Not shown on this tier: it has no water debt.");
                }
                list.GapLine();
            }

            if (Group(list, "Under the sand: thumper, fishing and swimmers", RimMandrake.Shared.SettingScope.Now, new[] { "thumperEnabled", "thumperRadius", "sandFishingWakeEnabled", "sandFishingWakeChance", "driftSwimEnabled", "driftSwimDepth" }))
            {
                list.CheckboxLabeled("Thumper calls swimmers", ref thumperEnabled,
                    "A charged, beating thumper wets the sand around it and calls submerged sand swimmers within its radius toward it. Off: it never beats.");
                list.Label("Thumper call radius: " + Mathf.RoundToInt(thumperRadius) + " cells");
                thumperRadius = Mathf.Round(list.Slider(thumperRadius, 10f, 80f));
                list.CheckboxLabeled("Sand fishing draws a stalker wake", ref sandFishingWakeEnabled,
                    "A fishing session on deep sand has a small chance to draw a nearby submerged swimmer toward the fisher. Off: fishing is quiet.");
                list.Label("Chance per catch: " + sandFishingWakeChance.ToStringPercent());
                sandFishingWakeChance = Mathf.Round(list.Slider(sandFishingWakeChance, 0f, 1f) * 100f) / 100f;
                list.CheckboxLabeled("Swimmers swim through deep drifts", ref driftSwimEnabled,
                    "Where the dune engine is present, a drift of sand at or above the depth below counts as swim ground. Off: only sand terrain does.");
                list.Label("Drift depth that counts as swim ground: " + driftSwimDepth.ToString("0.00"));
                driftSwimDepth = Mathf.Round(list.Slider(driftSwimDepth, 0.1f, 1f) * 20f) / 20f;
                list.GapLine();
            }

            if (Group(list, "The Listening", RimMandrake.Shared.SettingScope.Now, new[] { "listeningHissEnabled", "listeningSingingEnabled", "listeningWarningEnabled", "singingWarningCells", "listeningRumbleEnabled" }))
            {
                list.CheckboxLabeled("Wind hiss and saltation", ref listeningHissEnabled,
                    "The always-on room tone of the sand, scaled by wind speed. Off: no hiss bed.");
                list.CheckboxLabeled("Singing dunes", ref listeningSingingEnabled,
                    "A slab sliding off a slip face booms. Off: the dunes stay quiet.");
                list.CheckboxLabeled("Singing-dune warning", ref listeningWarningEnabled,
                    "A one-line warning the first time a singing slip face comes near one of your buildings.");
                list.Label("Warning distance: " + Mathf.RoundToInt(singingWarningCells) + " cells");
                singingWarningCells = Mathf.Round(list.Slider(singingWarningCells, 4f, 40f));
                list.CheckboxLabeled("Rumble and breach sounds", ref listeningRumbleEnabled,
                    "Stillsand's own rumble and breach sounds for swimmers. Off: swimmers use whatever sound their extension names, if any.");
                list.GapLine();
            }

            if (Group(list, "Footprints in moving sand", RimMandrake.Shared.SettingScope.Now, new[] { "duneErasesTracks" }))
            {
                list.CheckboxLabeled("Moving sand buries tracks", ref duneErasesTracks,
                    "On a Stillsand map, a cell whose sand depth shifts noticeably loses its footprints, so dunes on the move wipe the trail. "
                    + "Off: prints stay until the track limit pushes the oldest out. Safe mid-game.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_StillsandMod : Mod
    {
        public static RM_StillsandSettings settings;

        public RM_StillsandMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_StillsandSettings>();
        }

        public override string SettingsCategory()
        {
            return "Stillsand";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
