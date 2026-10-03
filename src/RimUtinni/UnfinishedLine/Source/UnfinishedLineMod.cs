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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref chainEnabled, "chainEnabled", true);
            Scribe_Values.Look(ref minEnclaveGoodwill, "minEnclaveGoodwill", 20);
            Scribe_Values.Look(ref earliestDay, "earliestDay", 30);
            Scribe_Values.Look(ref daysBetweenBeatsMin, "daysBetweenBeatsMin", 5);
            Scribe_Values.Look(ref daysBetweenBeatsMax, "daysBetweenBeatsMax", 10);
            Scribe_Values.Look(ref failuresAllowedPerBeat, "failuresAllowedPerBeat", 2);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

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

            list.End();
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
