using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;
using RimMandrake.EnvironmentalHazards;

namespace RimMandrake.FeverWood
{
    // ════════════════════════════════════════════════════════════════════
    // FEVERWOOD_BROOD_RANSOM_1 — the ransom of its young (decision taken by
    // question card 2026-10-02). The young kept in prison tanks are the
    // sekkulaath's own; the more of them the world holds, the bolder the pools
    // get; returning one to a Fever Wood pool makes the deep set down one great
    // gift from the very bottom.
    //
    // Free-tier mechanism only. The campaign names who and where in
    // src/RimUtinni/UtinniPatches/Patches/RUT_BroodRansom_Campaign.xml:
    // Sporefall's display tank (RM_GenStep_DisplayTank + a displayTank
    // RM_CompProperties_CapturedSpecimen with giftRolls 2), the Wildsteam's
    // young-cask stock (RM_StockGenerator_DeepYoung.onlyFactions), Sporefall's
    // place in the tally (RM_DeepYoungKeeperExtension.onlySettlementNames), and
    // the deep's lines (RM_CompProperties_DeepYoungLines).
    // ════════════════════════════════════════════════════════════════════

    /// <summary>Flags every settlement of a FactionDef as keeping this many of
    /// the deep's young in a tank. Free tier: no FactionDef carries it (tally
    /// contribution 0); the campaign flags its prison towns.</summary>
    public class RM_DeepYoungKeeperExtension : DefModExtension
    {
        public int youngPerSettlement = 1;
        // Empty: every settlement of the faction keeps young. Otherwise only
        // the settlements with these names (campaign: Sporefall).
        public List<string> onlySettlementNames = new List<string>();

        public int YoungFor(Settlement settlement)
        {
            if (settlement == null)
            {
                return 0;
            }
            if (onlySettlementNames != null && onlySettlementNames.Count > 0 && !onlySettlementNames.Contains(settlement.Name))
            {
                return 0;
            }
            return Mathf.Max(0, youngPerSettlement);
        }
    }

    /// <summary>The world's tally of the deep's young, recomputed on a long
    /// interval (never per tick) and on the player's own release acts.</summary>
    public class RM_WorldComponent_DeepYoung : WorldComponent
    {
        public const int RecomputeIntervalTicks = 15000; // 6 in-game hours

        // INVENTED thresholds: the letter the player gets as the tally rises.
        private static readonly int[] Thresholds = { 1, 3, 6, 10 };

        private int tally;
        private int lastComputedTick = -999999;
        private int announcedLevel;
        private Dictionary<int, int> settlementYoungOverride = new Dictionary<int, int>();
        private HashSet<int> freedDisplayTanks = new HashSet<int>(); // settlement IDs whose display tank was freed

        public RM_WorldComponent_DeepYoung(World world) : base(world)
        {
        }

        public static RM_WorldComponent_DeepYoung Get => Find.World?.GetComponent<RM_WorldComponent_DeepYoung>();

        public int Tally
        {
            get
            {
                if (Find.TickManager.TicksGame - lastComputedTick >= RecomputeIntervalTicks)
                {
                    Recompute();
                }
                return tally;
            }
        }

        /// <summary>1 when the brood ransom is off; otherwise
        /// min(cap, 1 + perYoung * tally).</summary>
        public static float BoldnessMultiplier
        {
            get
            {
                if (!RM_FeverWoodSettings.broodRansomEnabled)
                {
                    return 1f;
                }
                RM_WorldComponent_DeepYoung comp = Get;
                int t = comp?.Tally ?? 0;
                float cap = Mathf.Max(1f, RM_FeverWoodSettings.broodBoldnessCap);
                return Mathf.Min(cap, 1f + Mathf.Max(0f, RM_FeverWoodSettings.broodBoldnessPerYoung) * t);
            }
        }

        public static string RestlessnessLine()
        {
            if (!RM_FeverWoodSettings.broodRansomEnabled || Get == null)
            {
                return null;
            }
            int t = Get.Tally;
            string mood = t == 0 ? "the pools are quiet"
                : t < Thresholds[1] ? "the pools are uneasy"
                : t < Thresholds[2] ? "the pools are restless"
                : t < Thresholds[3] ? "the pools are bold"
                : "the pools are savage";
            return "Young of the deep held in the world: " + t + " (" + mood + ", tentacles x"
                + BoldnessMultiplier.ToString("0.00") + ")";
        }

        public void SetSettlementYoung(Settlement settlement, int count)
        {
            if (settlement == null)
            {
                return;
            }
            settlementYoungOverride[settlement.ID] = Mathf.Max(0, count);
            Recompute();
        }

        /// <summary>How many young this settlement keeps: its override, else
        /// its faction's RM_DeepYoungKeeperExtension, else 0.</summary>
        public int SettlementYoung(Settlement settlement)
        {
            if (settlement == null)
            {
                return 0;
            }
            if (settlementYoungOverride.TryGetValue(settlement.ID, out int ov))
            {
                return ov;
            }
            RM_DeepYoungKeeperExtension ext = settlement.Faction?.def?.GetModExtension<RM_DeepYoungKeeperExtension>();
            return ext != null ? ext.YoungFor(settlement) : 0;
        }

        /// <summary>FEVERWOOD_BROOD_RANSOM_1 §5: the settlement's display tank
        /// was freed. Remembered so the tank is not regenerated on the next
        /// visit (settlement maps are rebuilt), and the town keeps one young
        /// fewer in the tally.</summary>
        public void Notify_DisplayTankFreed(Settlement settlement)
        {
            if (settlement == null)
            {
                return;
            }
            if (freedDisplayTanks.Add(settlement.ID))
            {
                settlementYoungOverride[settlement.ID] = Mathf.Max(0, SettlementYoung(settlement) - 1);
            }
            Recompute();
        }

        public bool DisplayTankFreed(Settlement settlement)
        {
            return settlement != null && freedDisplayTanks.Contains(settlement.ID);
        }

        public override void WorldComponentTick()
        {
            base.WorldComponentTick();
            if (Find.TickManager.TicksGame % RecomputeIntervalTicks == 0)
            {
                Recompute();
            }
        }

        public int Recompute()
        {
            lastComputedTick = Find.TickManager.TicksGame;
            int n = 0;
            ThingDef cask = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SekkulaathYoungCask");

            List<Map> maps = Find.Maps;
            for (int m = 0; m < maps.Count; m++)
            {
                Map map = maps[m];
                if (!map.IsPlayerHome)
                {
                    continue;
                }
                List<Building> buildings = map.listerBuildings.allBuildingsColonist;
                for (int i = 0; i < buildings.Count; i++)
                {
                    RM_CompCapturedSpecimen spec = buildings[i].TryGetComp<RM_CompCapturedSpecimen>();
                    if (spec != null && spec.Occupied)
                    {
                        n++;
                    }
                }
                if (cask != null)
                {
                    List<Thing> casks = map.listerThings.ThingsOfDef(cask);
                    for (int i = 0; i < casks.Count; i++)
                    {
                        n += casks[i].stackCount;
                    }
                }
            }

            if (cask != null)
            {
                List<Caravan> caravans = Find.WorldObjects.Caravans;
                for (int c = 0; c < caravans.Count; c++)
                {
                    if (!caravans[c].IsPlayerControlled)
                    {
                        continue;
                    }
                    List<Thing> items = CaravanInventoryUtility.AllInventoryItems(caravans[c]);
                    for (int i = 0; i < items.Count; i++)
                    {
                        if (items[i].def == cask)
                        {
                            n += items[i].stackCount;
                        }
                    }
                }
            }

            List<Settlement> settlements = Find.WorldObjects.Settlements;
            for (int s = 0; s < settlements.Count; s++)
            {
                Settlement st = settlements[s];
                if (settlementYoungOverride.TryGetValue(st.ID, out int ov))
                {
                    n += ov;
                    continue;
                }
                RM_DeepYoungKeeperExtension ext = st.Faction?.def?.GetModExtension<RM_DeepYoungKeeperExtension>();
                if (ext != null)
                {
                    n += ext.YoungFor(st);
                }
            }

            tally = n;
            Announce();
            return tally;
        }

        private void Announce()
        {
            if (!RM_FeverWoodSettings.broodRansomEnabled)
            {
                return;
            }
            while (announcedLevel > 0 && tally < Thresholds[announcedLevel - 1])
            {
                announcedLevel--; // quiet step down; the next rise announces again
            }
            int reached = announcedLevel;
            while (reached < Thresholds.Length && tally >= Thresholds[reached])
            {
                reached++;
            }
            if (reached <= announcedLevel)
            {
                return;
            }
            announcedLevel = reached;
            Map home = Find.AnyPlayerHomeMap;
            string date = home != null
                ? GenDate.DateFullStringAt(GenTicks.TicksAbs, Find.WorldGrid.LongLatOf(home.Tile))
                : "the last few days";
            Find.LetterStack.ReceiveLetter(
                "The pools grow bold",
                "The pools of the Fever Wood have been restless since " + date + ". The world now holds "
                + tally + " of the deep's young in tanks and casks, and the thing below knows it: tentacles rise "
                + "more often, and the snares and lashes come first.\n\nReturn its young to a Fever Wood pool and "
                + "the deep quiets, and pays.",
                LetterDefOf.NegativeEvent);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref tally, "tally", 0);
            Scribe_Values.Look(ref announcedLevel, "announcedLevel", 0);
            Scribe_Collections.Look(ref settlementYoungOverride, "settlementYoungOverride", LookMode.Value, LookMode.Value);
            if (settlementYoungOverride == null)
            {
                settlementYoungOverride = new Dictionary<int, int>();
            }
            Scribe_Collections.Look(ref freedDisplayTanks, "freedDisplayTanks", LookMode.Value);
            if (freedDisplayTanks == null)
            {
                freedDisplayTanks = new HashSet<int>();
            }
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                lastComputedTick = -999999; // recompute on first read after load
            }
        }
    }

    public class RM_DeepGiftEntry
    {
        public ThingDef thing;
        public float weight = 1f;
        public IntRange count = new IntRange(1, 1);
    }

    /// <summary>RM_DeepGiftLoot: old, heavy things from the very bottom.</summary>
    public class RM_DeepGiftTableDef : Def
    {
        public List<RM_DeepGiftEntry> entries = new List<RM_DeepGiftEntry>();

        public float EffectiveWeight(RM_DeepGiftEntry e)
        {
            float mult = RM_FeverWoodSettings.broodGiftWeightMultipliers.TryGetValue(e.thing.defName, out float m) ? m : 1f;
            return Mathf.Max(0f, e.weight * mult);
        }
    }

    public static class RM_DeepGift
    {
        public const string TableDefName = "RM_DeepGiftLoot";
        public const string GiftLetterDefName = "RM_DeepGiftLetter";
        public const float GiftRadius = 5.9f; // criteria: within 6 cells of the pool

        // The Fever Wood's own registered pool terrain. A young freed at any
        // other water settles in and gives nothing.
        public static readonly string[] FeverWoodPoolTerrains = { "RUT_FeverWoodMirrorPool" };

        public static bool IsFeverWoodPool(IntVec3 c, Map map)
        {
            if (!c.InBounds(map))
            {
                return false;
            }
            RUT_MapComponent_TheTenant tenant = map.GetComponent<RUT_MapComponent_TheTenant>();
            if (tenant == null || !tenant.IsRegisteredWater(c))
            {
                return false;
            }
            string t = c.GetTerrain(map)?.defName;
            for (int i = 0; i < FeverWoodPoolTerrains.Length; i++)
            {
                if (FeverWoodPoolTerrains[i] == t)
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>Sets down <paramref name="rolls"/> gifts from RM_DeepGiftLoot
        /// beside the pool and sends one letter naming them. Returns the things
        /// placed.</summary>
        public static List<Thing> Grant(Map map, IntVec3 pool, int rolls = 1)
        {
            List<Thing> placed = new List<Thing>();
            RM_DeepGiftTableDef table = DefDatabase<RM_DeepGiftTableDef>.GetNamedSilentFail(TableDefName);
            if (table == null || map == null)
            {
                return placed;
            }
            for (int r = 0; r < Mathf.Max(1, rolls); r++)
            {
                Thing t = RollAndPlace(table, map, pool);
                if (t != null)
                {
                    placed.Add(t);
                }
            }
            if (placed.Count == 0)
            {
                return placed;
            }

            string names = "";
            for (int i = 0; i < placed.Count; i++)
            {
                names += (i > 0 ? ", " : "") + placed[i].LabelCap;
            }
            LetterDef letterDef = DefDatabase<LetterDef>.GetNamedSilentFail(GiftLetterDefName) ?? LetterDefOf.PositiveEvent;
            Find.LetterStack.ReceiveLetter(
                "A gift from the bottom",
                "A tentacle rose at the pool where the young went home, and set something down at the water's edge: "
                + names + ".\n\nIt is old, and heavy, and has been at the very bottom for a long time.",
                letterDef, new LookTargets(placed));
            return placed;
        }

        private static Thing RollAndPlace(RM_DeepGiftTableDef table, Map map, IntVec3 pool)
        {
            List<RM_DeepGiftEntry> candidates = new List<RM_DeepGiftEntry>();
            for (int i = 0; i < table.entries.Count; i++)
            {
                if (table.entries[i].thing != null && table.EffectiveWeight(table.entries[i]) > 0f)
                {
                    candidates.Add(table.entries[i]);
                }
            }
            // A building that finds no footprint near the pool drops out and the roll is retried.
            while (candidates.Count > 0)
            {
                RM_DeepGiftEntry e = candidates.RandomElementByWeight(table.EffectiveWeight);
                Thing t = TryPlace(e, map, pool);
                if (t != null)
                {
                    return t;
                }
                candidates.Remove(e);
            }
            return null;
        }

        private static Thing TryPlace(RM_DeepGiftEntry e, Map map, IntVec3 pool)
        {
            ThingDef def = e.thing;
            Thing thing = ThingMaker.MakeThing(def, def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null);
            if (def.category == ThingCategory.Building)
            {
                foreach (IntVec3 c in GenRadial.RadialCellsAround(pool, GiftRadius, true))
                {
                    if (FootprintClear(c, def, map))
                    {
                        GenSpawn.Spawn(thing, c, map, Rot4.North);
                        return thing;
                    }
                }
                return null;
            }

            thing.stackCount = Mathf.Clamp(e.count.RandomInRange, 1, def.stackLimit);
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pool, GiftRadius, true))
            {
                if (c.InBounds(map) && c.Standable(map) && !c.GetTerrain(map).IsWater && c.GetFirstItem(map) == null)
                {
                    GenSpawn.Spawn(thing, c, map);
                    return thing;
                }
            }
            return null;
        }

        private static bool FootprintClear(IntVec3 c, ThingDef def, Map map)
        {
            foreach (IntVec3 f in GenAdj.OccupiedRect(c, Rot4.North, def.size))
            {
                if (!f.InBounds(map) || !f.Standable(map) || f.GetTerrain(map).IsWater
                    || f.GetEdifice(map) != null || f.GetFirstItem(map) != null || f.GetFirstPawn(map) != null)
                {
                    return false;
                }
            }
            return true;
        }
    }

    /// <summary>Exotic traders rarely stock a young-cask, and every trader
    /// carrying this generator buys one back. Chance from Mod Settings.</summary>
    public class RM_StockGenerator_DeepYoung : StockGenerator
    {
        // Campaign hooks (FEVERWOOD_BROOD_RANSOM_1 §4): stock only for these
        // factions' traders (empty = any trader carrying the generator), and a
        // fixed stock chance in place of the Mod Settings one (<0 = settings).
        public List<FactionDef> onlyFactions = new List<FactionDef>();
        public float stockChance = -1f;

        public float EffectiveStockChance => Mathf.Clamp01(stockChance >= 0f ? stockChance : RM_FeverWoodSettings.broodCaskTraderStockChance);

        public bool StocksFor(Faction faction)
        {
            if (onlyFactions == null || onlyFactions.Count == 0)
            {
                return true;
            }
            return faction != null && onlyFactions.Contains(faction.def);
        }

        public override IEnumerable<Thing> GenerateThings(PlanetTile forTile, Faction faction = null)
        {
            if (!RM_FeverWoodSettings.broodRansomEnabled || !StocksFor(faction))
            {
                yield break;
            }
            ThingDef cask = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SekkulaathYoungCask");
            if (cask != null && Rand.Chance(EffectiveStockChance))
            {
                yield return ThingMaker.MakeThing(cask);
            }
        }

        public override bool HandlesThingDef(ThingDef thingDef)
        {
            return RM_FeverWoodSettings.broodRansomEnabled && thingDef.defName == "RM_SekkulaathYoungCask";
        }
    }

    /// <summary>The young-cask, opened at a water's edge: the young inside
    /// goes home. Only a Fever Wood pool answers with a gift.</summary>
    public class RM_CompUseEffect_ReleaseYoung : CompUseEffect
    {
        private const float EdgeRadius = 2.9f;

        public static IntVec3 NearestWater(IntVec3 from, Map map, float radius)
        {
            IntVec3 best = IntVec3.Invalid;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(from, radius, true))
            {
                if (c.InBounds(map) && c.GetTerrain(map).IsWater)
                {
                    if (RM_DeepGift.IsFeverWoodPool(c, map))
                    {
                        return c;
                    }
                    if (!best.IsValid)
                    {
                        best = c;
                    }
                }
            }
            return best;
        }

        public override AcceptanceReport CanBeUsedBy(Pawn p)
        {
            if (!RM_FeverWoodSettings.broodRansomEnabled)
            {
                return "The deep is not listening (Fever Wood mod setting: brood ransom off).";
            }
            if (!parent.Spawned || !NearestWater(parent.Position, parent.Map, EdgeRadius).IsValid)
            {
                return "Set the cask down at a water's edge first.";
            }
            return true;
        }

        public override void DoEffect(Pawn usedBy)
        {
            base.DoEffect(usedBy);
            Map map = parent.MapHeld;
            IntVec3 pos = parent.PositionHeld;
            if (map == null)
            {
                return;
            }
            PawnKindDef kind = RM_CompCapturedSpecimen.YoungKind(null);
            if (kind == null)
            {
                return;
            }
            Pawn young = PawnGenerator.GeneratePawn(kind, null);
            GenSpawn.Spawn(young, CellFinder.RandomClosewalkCellNear(pos, map, 1), map);
            young.GetComp<RM_CompEscapedCaptive>()?.Notify_ReleasedToDeep();
            Messages.Message("The cask is unsealed and the young slides out, making for the water.",
                young, MessageTypeDefOf.NeutralEvent);
        }

        public override string CompInspectStringExtra()
        {
            return RM_WorldComponent_DeepYoung.RestlessnessLine();
        }
    }

    /// <summary>FEVERWOOD_BROOD_RANSOM_1 §5: places a settlement's display
    /// tank when its map is generated. Free-tier mechanism; the campaign
    /// names the faction and town (Sporefall) in XML. Skipped once that
    /// settlement's tank was freed, and with the brood ransom or tank off.</summary>
    public class RM_GenStep_DisplayTank : GenStep
    {
        public ThingDef tankDef;
        public FactionDef faction;
        public string settlementName; // null/empty: every settlement of the faction
        public float searchRadius = 14f;

        public override int SeedPart => 518302771;

        public static bool Applies(Settlement settlement, FactionDef faction, string settlementName)
        {
            if (settlement == null || faction == null || settlement.Faction?.def != faction)
            {
                return false;
            }
            return settlementName.NullOrEmpty() || settlement.Name == settlementName;
        }

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_FeverWoodSettings.broodRansomEnabled || !RM_FeverWoodSettings.sekkulaathTankEnabled || tankDef == null)
            {
                return;
            }
            Settlement settlement = map.Parent as Settlement;
            if (!Applies(settlement, faction, settlementName))
            {
                return;
            }
            if (RM_WorldComponent_DeepYoung.Get?.DisplayTankFreed(settlement) == true)
            {
                return;
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, Mathf.RoundToInt(searchRadius),
                    c => FootprintClear(c, map), out IntVec3 cell))
            {
                Log.Warning("[RM FeverWood] No room for " + tankDef.defName + " at " + settlement.Name + "; display tank not placed.");
                return;
            }
            Thing tank = ThingMaker.MakeThing(tankDef, tankDef.MadeFromStuff ? GenStuff.DefaultStuffFor(tankDef) : null);
            tank.SetFaction(settlement.Faction);
            GenSpawn.Spawn(tank, cell, map, Rot4.North);
        }

        private bool FootprintClear(IntVec3 c, Map map)
        {
            foreach (IntVec3 f in GenAdj.OccupiedRect(c, Rot4.North, tankDef.size).ExpandedBy(1))
            {
                if (!f.InBounds(map) || !f.Standable(map) || f.GetTerrain(map).IsWater || f.GetEdifice(map) != null
                    || f.GetFirstItem(map) != null || f.GetFirstPawn(map) != null)
                {
                    return false;
                }
            }
            return true;
        }
    }

    /// <summary>FEVERWOOD_BROOD_RANSOM_1 §4: what the deep thinks of traders
    /// in its children. Lines shown when a young-cask is bought or sold, and
    /// when a young comes home. Free tier: not attached (no lines); the
    /// campaign adds it to RM_SekkulaathYoungCask with its own wording.</summary>
    public class RM_CompProperties_DeepYoungLines : CompProperties
    {
        public string boughtLine;
        public string soldLine;
        public string returnedLine;

        public RM_CompProperties_DeepYoungLines()
        {
            compClass = typeof(RM_CompDeepYoungLines);
        }

        public static RM_CompProperties_DeepYoungLines ForCask()
        {
            return DefDatabase<ThingDef>.GetNamedSilentFail("RM_SekkulaathYoungCask")?.GetCompProperties<RM_CompProperties_DeepYoungLines>();
        }
    }

    public class RM_CompDeepYoungLines : ThingComp
    {
        public RM_CompProperties_DeepYoungLines Props => (RM_CompProperties_DeepYoungLines)props;

        public static string LineFor(RM_CompProperties_DeepYoungLines p, TradeAction action)
        {
            if (p == null)
            {
                return null;
            }
            return action == TradeAction.PlayerBuys ? p.boughtLine
                : action == TradeAction.PlayerSells ? p.soldLine
                : null;
        }

        public override void PrePreTraded(TradeAction action, Pawn playerNegotiator, ITrader trader)
        {
            base.PrePreTraded(action, playerNegotiator, trader);
            if (!RM_FeverWoodSettings.broodRansomEnabled)
            {
                return;
            }
            string line = LineFor(Props, action);
            if (!line.NullOrEmpty())
            {
                Messages.Message(line, MessageTypeDefOf.NeutralEvent);
            }
        }
    }
}
