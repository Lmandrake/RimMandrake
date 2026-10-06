using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UnfinishedLine
{
    // UNFINISHED_LINE_SPINE_COUNT_1 — Mod Settings for The Unfinished Line
    // (design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md §5). Only the
    // settings the spine and beat 1 read live here; each later beat adds its own.
    public class UnfinishedLineSettings : ModSettings
    {
        public static bool chainEnabled = true;
        public static int minEnclaveGoodwill = 20;
        public static int earliestDay = 30;
        public static int daysBetweenBeatsMin = 5;
        public static int daysBetweenBeatsMax = 10;
        public static int failuresAllowedPerBeat = 2;
        public static bool brokeredTruceEnabled = true;
        public static int ruinWildDroidsMax = 6;
        public static int freedWildDroidGoodwill = 4;
        public static bool coreBrokerEnabled = true;
        public static int coreBrokerWaitDays = 3;
        public static int coreSaleSilver = 2500;
        public static int coreSaleEmpireGoodwill = 15;
        // UNFINISHED_LINE_FIRSTLIGHT_BEAT_1
        public static float firstLightRunDays = 2f;
        public static float firstLightStrikeDelayHours = 6f;
        public static float firstLightHoldDays = 3f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref chainEnabled, "chainEnabled", true);
            Scribe_Values.Look(ref minEnclaveGoodwill, "minEnclaveGoodwill", 20);
            Scribe_Values.Look(ref earliestDay, "earliestDay", 30);
            Scribe_Values.Look(ref daysBetweenBeatsMin, "daysBetweenBeatsMin", 5);
            Scribe_Values.Look(ref daysBetweenBeatsMax, "daysBetweenBeatsMax", 10);
            Scribe_Values.Look(ref failuresAllowedPerBeat, "failuresAllowedPerBeat", 2);
            Scribe_Values.Look(ref brokeredTruceEnabled, "brokeredTruceEnabled", true);
            Scribe_Values.Look(ref ruinWildDroidsMax, "ruinWildDroidsMax", 6);
            Scribe_Values.Look(ref freedWildDroidGoodwill, "freedWildDroidGoodwill", 4);
            Scribe_Values.Look(ref coreBrokerEnabled, "coreBrokerEnabled", true);
            Scribe_Values.Look(ref coreBrokerWaitDays, "coreBrokerWaitDays", 3);
            Scribe_Values.Look(ref coreSaleSilver, "coreSaleSilver", 2500);
            Scribe_Values.Look(ref coreSaleEmpireGoodwill, "coreSaleEmpireGoodwill", 15);
            Scribe_Values.Look(ref firstLightRunDays, "firstLightRunDays", 2f);
            Scribe_Values.Look(ref firstLightStrikeDelayHours, "firstLightStrikeDelayHours", 6f);
            Scribe_Values.Look(ref firstLightHoldDays, "firstLightHoldDays", 3f);
        }

        private static Vector2 scroll = Vector2.zero;
        private static float viewHeight = 900f;

        public void DoWindowContents(Rect inRect)
        {
            // the page outgrew one screen with beat 5: the whole of it scrolls
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(inRect.height, viewHeight));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);

            list.CheckboxLabeled("Enable The Unfinished Line quest chain", ref chainEnabled,
                "Off: the chain is never offered. A chain already running carries on. Nothing else changes.");
            list.GapLine();

            list.Label("Offer gate: Free Droid Enclave goodwill at least " + minEnclaveGoodwill);
            minEnclaveGoodwill = Mathf.RoundToInt(list.Slider(minEnclaveGoodwill, 0f, 75f));
            list.Label("Offer gate: not before day " + earliestDay);
            earliestDay = Mathf.RoundToInt(list.Slider(earliestDay, 0f, 120f));
            list.GapLine();

            list.Label("Days between beats: " + daysBetweenBeatsMin + " to " + daysBetweenBeatsMax);
            daysBetweenBeatsMin = Mathf.RoundToInt(list.Slider(daysBetweenBeatsMin, 1f, 30f));
            daysBetweenBeatsMax = Mathf.Max(daysBetweenBeatsMin, Mathf.RoundToInt(list.Slider(daysBetweenBeatsMax, 1f, 30f)));
            list.GapLine();

            list.Label("Failed attempts a beat may take before the chain breaks: " + failuresAllowedPerBeat);
            list.Label("A failed beat is offered again; one failure past this number ends the chain.");
            failuresAllowedPerBeat = Mathf.RoundToInt(list.Slider(failuresAllowedPerBeat, 0f, 5f));
            list.GapLine();

            list.CheckboxLabeled("The Enclaves broker a truce with the Hive", ref brokeredTruceEnabled,
                "On: from the moment you accept the Hive's envoy until the chain ends, the Geonosian Foundry "
              + "Hive is held at least neutral to you, so it does not raid while the chain runs. Harming the "
              + "envoy breaks the truce and the chain. Off: the Hive stays as it is, and only the goodwill "
              + "each beat earns moves it.");
            list.GapLine();

            list.Label("The Pattern Cores (beat 3)");
            list.Label("Most wild droids in the foundry ruin: " + ruinWildDroidsMax + " (fewer at low threat points; at least 2)");
            ruinWildDroidsMax = Mathf.RoundToInt(list.Slider(ruinWildDroidsMax, 1f, 12f));
            list.Label("Enclave goodwill per wild droid released unbolted: " + freedWildDroidGoodwill);
            freedWildDroidGoodwill = Mathf.RoundToInt(list.Slider(freedWildDroidGoodwill, 0f, 15f));
            list.CheckboxLabeled("A broker offers to buy the cores (the sell-out)", ref coreBrokerEnabled,
                "On: once all three cores are at your colony, an Imperial salvage broker offers to buy them. Selling "
              + "ends the whole chain and turns the Hive and the Enclaves hostile. Off: the cores go straight to the "
              + "Enclaves and there is no betrayal path.");
            list.Label("Days the broker waits for an answer: " + coreBrokerWaitDays);
            coreBrokerWaitDays = Mathf.RoundToInt(list.Slider(coreBrokerWaitDays, 1f, 10f));
            list.Label("Silver the broker pays: " + coreSaleSilver);
            coreSaleSilver = Mathf.RoundToInt(list.Slider(coreSaleSilver, 0f, 10000f) / 100f) * 100;
            list.Label("Empire goodwill for the sale: " + coreSaleEmpireGoodwill);
            coreSaleEmpireGoodwill = Mathf.RoundToInt(list.Slider(coreSaleEmpireGoodwill, 0f, 50f));
            list.GapLine();

            list.Label("First Light (beat 5)");
            list.Label("Length of the line's first run: " + firstLightRunDays.ToString("0.0") + " days");
            firstLightRunDays = Mathf.Round(list.Slider(firstLightRunDays, 0.5f, 6f) * 2f) / 2f;
            list.Label("Hours before the strike arrives: " + firstLightStrikeDelayHours.ToString("0"));
            firstLightStrikeDelayHours = Mathf.Round(list.Slider(firstLightStrikeDelayHours, 0f, 24f));
            list.Label("Days the strike may hold your colony after the run before the beat fails: " + firstLightHoldDays.ToString("0.0"));
            firstLightHoldDays = Mathf.Round(list.Slider(firstLightHoldDays, 1f, 10f) * 2f) / 2f;

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class UnfinishedLineMod : Mod
    {
        public static UnfinishedLineSettings settings;

        public UnfinishedLineMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<UnfinishedLineSettings>();
        }

        public override string SettingsCategory() => "The Unfinished Line";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }

    /// <summary>The two authored factions the chain sits between (faction_roster_v2.md). Looked up by
    /// defName, silently, so a list without the Utinni factions gets a chain that never offers rather
    /// than a load error.</summary>
    public static class LineFactions
    {
        public const string EnclavesDefName = "RUT_Jawa_FreeDroidEnclaves";
        public const string HiveDefName = "RUT_Jawa_GeonosianFoundryHive";
        public const string ShopRepairResearch = "RSW_DW_Research_ShopRepair";

        public static Faction Enclaves => Find(EnclavesDefName);

        public static Faction Hive => Find(HiveDefName);

        private static Faction Find(string defName)
        {
            FactionDef def = DefDatabase<FactionDef>.GetNamedSilentFail(defName);
            return def == null ? null : Verse.Find.FactionManager.FirstFactionOfDef(def);
        }

        /// <summary>The faction's settlement nearest <paramref name="tile"/> (any, if the tile is invalid).</summary>
        public static Settlement NearestSettlement(Faction f, PlanetTile tile)
        {
            if (f == null) return null;
            Settlement best = null;
            float bestDist = float.MaxValue;
            foreach (Settlement s in Verse.Find.WorldObjects.Settlements)
            {
                if (s.Faction != f) continue;
                float d = tile.Valid && tile.Layer == s.Tile.Layer ? Verse.Find.WorldGrid.ApproxDistanceInTiles(tile, s.Tile) : 0f;
                if (d < bestDist)
                {
                    best = s;
                    bestDist = d;
                }
            }
            return best;
        }
    }
}
