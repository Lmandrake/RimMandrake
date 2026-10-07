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
    // Free tier only. The campaign half (Sporefall's display tank, the
    // Wildsteam/prison-town trade, the Narrator's trader lines, the goodwill
    // break) belongs in src/RimUtinni/ and is NOT built here; the hooks it needs
    // are public: RM_DeepYoungKeeperExtension (flag a FactionDef's settlements
    // as keeping young), RM_WorldComponent_DeepYoung.SetSettlementYoung (e.g.
    // zero Sporefall once its young is freed), RM_DeepGift.Grant(rolls: 2) (the
    // doubled "greatest gift").
    // ════════════════════════════════════════════════════════════════════

    /// <summary>Flags every settlement of a FactionDef as keeping this many of
    /// the deep's young in a tank. Free tier: no FactionDef carries it (tally
    /// contribution 0); the campaign flags its prison towns.</summary>
    public class RM_DeepYoungKeeperExtension : DefModExtension
    {
        public int youngPerSettlement = 1;
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
                    n += Mathf.Max(0, ext.youngPerSettlement);
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
        public override IEnumerable<Thing> GenerateThings(PlanetTile forTile, Faction faction = null)
        {
            if (!RM_FeverWoodSettings.broodRansomEnabled)
            {
                yield break;
            }
            ThingDef cask = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SekkulaathYoungCask");
            if (cask != null && Rand.Chance(Mathf.Clamp01(RM_FeverWoodSettings.broodCaskTraderStockChance)))
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
}
