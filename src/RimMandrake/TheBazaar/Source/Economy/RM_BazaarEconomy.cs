using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_PRICE_ENGINE_1 — design §3. The settlement price economy.
    ///
    /// 🔴 READ-SIDE ONLY. Nothing here writes a price anywhere. The whole read
    /// path is <see cref="MultiplierFor(ITrader, ThingDef)"/> /
    /// <see cref="MultiplierFor(int, ThingDef)"/>, and its only callers are
    /// the session-guarded <c>Tradeable.GetPriceFor</c> postfix
    /// (<see cref="RM_Patch_GetPriceFor"/>) and the intel workers. Vanilla
    /// market value, colony wealth, raid points and caravan valuations never
    /// see it: no StatWorker or MarketValue hook exists in this mod (the VTE
    /// blast radius the item rules out).
    ///
    /// Store: sparse (tile → PriceKey → bucket). A tile is seeded lazily the
    /// first time anything asks about it, so new settlements are covered and
    /// the daily drift only ever walks buckets that exist.
    /// </summary>
    public class RM_BazaarEconomy : WorldComponent
    {
        public const float BandMin = RM_BazaarKernel.BandMin;
        public const float BandMax = RM_BazaarKernel.BandMax;
        public const int HistorySize = RM_BazaarKernel.HistorySize;
        public const int MaxVisits = 64;
        public const int MaxStockPerVisit = 40;

        /// <summary>Orbital traders and anything with no settlement resolve here. Never seeded: ×1.0.</summary>
        public const int GlobalTile = -1;

        /// <summary>Per drift step: pull toward target, random walk, and the
        /// largest relative move allowed in one day.</summary>
        public const float ReversionRate = RM_BazaarKernel.ReversionRate;
        public const float DailyNoise = RM_BazaarKernel.DailyNoise;
        public const float MaxDailyStep = RM_BazaarKernel.MaxDailyStep;
        public const float NudgeDecay = RM_BazaarKernel.NudgeDecay;

        /// <summary>Procedural locality spread for untagged settlements (design §3: "mild").</summary>
        public static readonly FloatRange ProceduralRange = new FloatRange(0.85f, 1.2f);

        /// <summary>Top-level categories procedural locality varies. Missing ones are skipped.</summary>
        public static readonly string[] ProceduralCategories =
            { "Foods", "Medicine", "Drugs", "ResourcesRaw", "Manufactured", "Textiles", "Weapons", "Apparel" };

        private List<RM_BazaarBucket> buckets = new List<RM_BazaarBucket>();
        private List<int> seededTiles = new List<int>();
        private List<RM_BazaarVisit> visits = new List<RM_BazaarVisit>();
        private int lastDriftDay = -1;

        // Rebuilt from the scribed lists; never scribed themselves.
        private Dictionary<int, Dictionary<string, RM_BazaarBucket>> index;
        private HashSet<int> seededSet;

        public RM_BazaarEconomy(World world) : base(world)
        {
        }

        public static RM_BazaarEconomy Get() => Find.World?.GetComponent<RM_BazaarEconomy>();

        public IReadOnlyList<RM_BazaarVisit> Visits => visits;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref buckets, "buckets", LookMode.Deep);
            Scribe_Collections.Look(ref seededTiles, "seededTiles", LookMode.Value);
            Scribe_Collections.Look(ref visits, "visits", LookMode.Deep);
            Scribe_Values.Look(ref lastDriftDay, "lastDriftDay", -1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (buckets == null) buckets = new List<RM_BazaarBucket>();
                if (seededTiles == null) seededTiles = new List<int>();
                if (visits == null) visits = new List<RM_BazaarVisit>();
                buckets.RemoveAll(b => b == null || b.key.NullOrEmpty());
                index = null;
            }
        }

        private void EnsureIndex()
        {
            if (index != null) return;
            index = new Dictionary<int, Dictionary<string, RM_BazaarBucket>>();
            for (int i = 0; i < buckets.Count; i++) AddToIndex(buckets[i]);
            seededSet = new HashSet<int>(seededTiles);
        }

        private void AddToIndex(RM_BazaarBucket b)
        {
            Dictionary<string, RM_BazaarBucket> perTile;
            if (!index.TryGetValue(b.tile, out perTile))
            {
                perTile = new Dictionary<string, RM_BazaarBucket>();
                index[b.tile] = perTile;
            }
            perTile[b.key] = b;
        }

        // ─────────────────────────── read path ───────────────────────────

        /// <summary>The multiplier a trader's economy applies to a def. 1 when
        /// the engine is off, the trader resolves to the global bucket, or no
        /// bucket covers the def.</summary>
        public float MultiplierFor(ITrader trader, ThingDef def) => MultiplierFor(TileFor(trader), def);

        public float MultiplierFor(int tile, ThingDef def)
        {
            RM_BazaarBucket b = BucketFor(tile, def);
            return b != null ? b.multiplier : 1f;
        }

        /// <summary>The bucket that prices <paramref name="def"/> at <paramref name="tile"/>, or null.</summary>
        public RM_BazaarBucket BucketFor(int tile, ThingDef def)
        {
            if (!RM_BazaarSettings.economyEnabled || tile == GlobalTile || def == null) return null;
            EnsureSeeded(tile);
            Dictionary<string, RM_BazaarBucket> perTile;
            if (!index.TryGetValue(tile, out perTile)) return null;
            List<string> keys = RM_BazaarPriceKeys.KeysFor(def);
            for (int i = 0; i < keys.Count; i++)
            {
                RM_BazaarBucket b;
                if (perTile.TryGetValue(keys[i], out b)) return b;
            }
            return null;
        }

        public IEnumerable<RM_BazaarBucket> BucketsAt(int tile)
        {
            EnsureSeeded(tile);
            Dictionary<string, RM_BazaarBucket> perTile;
            return index.TryGetValue(tile, out perTile) ? perTile.Values : Enumerable.Empty<RM_BazaarBucket>();
        }

        /// <summary>
        /// Design §3: a settlement trades as itself; a roaming caravan or a
        /// visiting trader pawn trades as its faction's nearest settlement;
        /// an orbital ship (or anything factionless) uses the global bucket.
        /// </summary>
        public static int TileFor(ITrader trader)
        {
            if (trader == null) return GlobalTile;
            Settlement settlement = trader as Settlement;
            if (settlement != null) return settlement.Tile;

            PlanetTile origin = PlanetTile.Invalid;
            WorldObject wo = trader as WorldObject;
            if (wo != null) origin = wo.Tile;
            else
            {
                Pawn pawn = trader as Pawn;
                if (pawn != null && pawn.MapHeld != null) origin = pawn.MapHeld.Tile;
            }
            if (!origin.Valid || trader.Faction == null) return GlobalTile;
            return NearestSettlementTile(trader.Faction, origin);
        }

        public static int NearestSettlementTile(Faction faction, PlanetTile origin)
        {
            List<Settlement> all = Find.WorldObjects?.Settlements;
            if (all == null) return GlobalTile;
            float best = float.MaxValue;
            int bestTile = GlobalTile;
            for (int i = 0; i < all.Count; i++)
            {
                Settlement s = all[i];
                if (s.Faction != faction || !s.Tile.Valid || s.Tile.Layer != origin.Layer) continue;
                float d = Find.WorldGrid.ApproxDistanceInTiles(origin, s.Tile);
                if (d < best)
                {
                    best = d;
                    bestTile = s.Tile;
                }
            }
            return bestTile;
        }

        // ─────────────────────────── seeding ───────────────────────────

        public void EnsureSeeded(int tile)
        {
            EnsureIndex();
            if (tile == GlobalTile || seededSet.Contains(tile)) return;
            seededSet.Add(tile);
            seededTiles.Add(tile);
            Seed(tile);
        }

        private void Seed(int tile)
        {
            PlanetTile pt = tile;
            Faction faction = FactionAt(pt);
            HashSet<string> tags = RM_BazaarTags.TagsFor(pt, faction);
            Dictionary<string, float> targets = new Dictionary<string, float>();

            foreach (RM_BazaarSeedRuleDef rule in DefDatabase<RM_BazaarSeedRuleDef>.AllDefsListForReading)
            {
                if (!rule.Matches(tags) || rule.targets == null) continue;
                for (int i = 0; i < rule.targets.Count; i++)
                {
                    string key = rule.targets[i].Key;
                    if (key == null) continue;
                    float m = rule.targets[i].multiplier.LerpThroughRange(Hash01(tile, key, rule.defName));
                    float prior;
                    targets[key] = targets.TryGetValue(key, out prior) ? prior * m : m;
                }
            }

            if (RM_BazaarSettings.proceduralLocality)
            {
                int fac = faction != null && faction.def != null ? GenText.StableStringHash(faction.def.defName) : 0;
                BiomeDef biome = null;
                try { biome = Find.WorldGrid[pt]?.PrimaryBiome; } catch { biome = null; }
                int bio = biome != null ? GenText.StableStringHash(biome.defName) : 0;
                for (int i = 0; i < ProceduralCategories.Length; i++)
                {
                    if (DefDatabase<ThingCategoryDef>.GetNamedSilentFail(ProceduralCategories[i]) == null) continue;
                    string key = RM_BazaarPriceKeys.CategoryKey(ProceduralCategories[i]);
                    if (targets.ContainsKey(key)) continue; // authored wins
                    float u = Hash01(Gen.HashCombineInt(fac, bio), key, "locality");
                    targets[key] = ProceduralRange.LerpThroughRange(u);
                }
            }

            int day = Day;
            foreach (KeyValuePair<string, float> kv in targets)
            {
                float m = RM_BazaarKernel.SeedLevel(kv.Value);
                RM_BazaarBucket b = new RM_BazaarBucket { tile = tile, key = kv.Key, multiplier = m, target = m };
                b.Record(day, m, -1f);
                buckets.Add(b);
                AddToIndex(b);
            }
        }

        private static Faction FactionAt(PlanetTile tile)
        {
            List<Settlement> all = Find.WorldObjects?.Settlements;
            if (all == null) return null;
            for (int i = 0; i < all.Count; i++)
            {
                if (all[i].Tile == tile) return all[i].Faction;
            }
            return null;
        }

        /// <summary>Stable [0,1) from (seed, key, salt) — no Rand state touched,
        /// so seeding and drift replay identically across save/load.</summary>
        public static float Hash01(int seed, string key, string salt)
        {
            int h = Gen.HashCombineInt(seed, GenText.StableStringHash(key));
            h = Gen.HashCombineInt(h, GenText.StableStringHash(salt));
            return RM_BazaarKernel.ToUnit(h);
        }

        // ─────────────────────────── drift ───────────────────────────

        private static int Day => Find.TickManager != null ? GenDate.DaysPassed : 0;

        public override void WorldComponentTick()
        {
            if (!RM_BazaarSettings.economyEnabled) return;
            if (Find.TickManager.TicksGame % 250 != 0) return;
            int day = Day;
            if (day == lastDriftDay) return;
            lastDriftDay = day;
            DriftAll(day);
        }

        /// <summary>
        /// One pass over seeded buckets only: pull toward the (nudged) target,
        /// add a small deterministic walk, clamp the step to ±10% and the
        /// value to the ×0.25–×4.0 band, decay the nudge, record history.
        /// </summary>
        public void DriftAll(int day)
        {
            for (int i = 0; i < buckets.Count; i++)
            {
                RM_BazaarBucket b = buckets[i];
                float noiseU = Hash01(Gen.HashCombineInt(b.tile, day), b.key, "drift");
                b.multiplier = RM_BazaarKernel.DriftStep(b.multiplier, b.target, ref b.nudge, noiseU);
                b.Record(day, b.multiplier, -1f);
            }
        }

        /// <summary>Event hook (a drought, a big broker sale): push one
        /// bucket's target by a fraction; reversion pulls it back over days.</summary>
        public void Nudge(int tile, ThingDef def, float fraction)
        {
            RM_BazaarBucket b = BucketFor(tile, def);
            if (b != null) b.nudge = RM_BazaarKernel.NudgeBy(b.nudge, fraction);
        }

        // ─────────────────────── session observations ───────────────────────

        /// <summary>
        /// Called once when a Bazaar session opens, BEFORE the session guard is
        /// raised (so the prices observed are vanilla, not our own output fed
        /// back in). Writes one history entry per touched bucket with the mean
        /// observed buy price, and one trader-visit log entry.
        /// </summary>
        public void RecordSessionOpen(ITrader trader, IList<Tradeable> tradeables)
        {
            if (trader == null) return;
            int tile = TileFor(trader);
            int day = Day;

            List<string> stock = new List<string>();
            if (trader.Goods != null)
            {
                foreach (Thing t in trader.Goods.OrderByDescending(g => g.MarketValue * g.stackCount))
                {
                    if (t?.def == null || stock.Contains(t.def.defName)) continue;
                    stock.Add(t.def.defName);
                    if (stock.Count >= MaxStockPerVisit) break;
                }
            }
            visits.Add(new RM_BazaarVisit
            {
                day = day,
                tile = tile,
                traderKind = trader.TraderKind?.defName,
                traderName = trader.TraderName,
                stock = stock,
            });
            while (visits.Count > MaxVisits) visits.RemoveAt(0);

            if (tradeables == null || tile == GlobalTile) return;
            Dictionary<RM_BazaarBucket, float> sum = new Dictionary<RM_BazaarBucket, float>();
            Dictionary<RM_BazaarBucket, int> n = new Dictionary<RM_BazaarBucket, int>();
            for (int i = 0; i < tradeables.Count; i++)
            {
                Tradeable td = tradeables[i];
                if (td == null || td.IsCurrency || td.TraderWillTrade == false) continue;
                RM_BazaarBucket b = BucketFor(tile, td.ThingDef);
                if (b == null) continue;
                float price;
                try { price = td.GetPriceFor(TradeAction.PlayerBuys); } catch { continue; }
                float s;
                sum[b] = sum.TryGetValue(b, out s) ? s + price : price;
                int c;
                n[b] = n.TryGetValue(b, out c) ? c + 1 : 1;
            }
            foreach (KeyValuePair<RM_BazaarBucket, float> kv in sum)
            {
                kv.Key.Record(day, kv.Key.multiplier, kv.Value / n[kv.Key]);
            }
        }

        /// <summary>Distinct traders (by tile + name) that carried
        /// <paramref name="def"/> within the last <paramref name="days"/> days.</summary>
        public int TradersCarrying(ThingDef def, int days)
        {
            if (def == null) return 0;
            int since = Day - days;
            HashSet<string> who = new HashSet<string>();
            for (int i = 0; i < visits.Count; i++)
            {
                RM_BazaarVisit v = visits[i];
                if (v.day < since || v.stock == null || !v.stock.Contains(def.defName)) continue;
                who.Add(v.tile + "|" + v.traderName);
            }
            return who.Count;
        }
    }

    /// <summary>One price bucket at one settlement tile.</summary>
    public class RM_BazaarBucket : IExposable
    {
        public int tile;
        public string key;
        public float multiplier = 1f;

        /// <summary>The seeded resting level drift reverts to.</summary>
        public float target = 1f;

        /// <summary>Transient fractional push on the target from events; decays daily.</summary>
        public float nudge;

        /// <summary>32-entry ring (design §3). Read through <see cref="HistoryOldestFirst"/>.</summary>
        public List<RM_BazaarHistoryEntry> history = new List<RM_BazaarHistoryEntry>();
        public int head;

        public void Record(int day, float mult, float observedOffer)
        {
            RM_BazaarHistoryEntry e = new RM_BazaarHistoryEntry { day = day, multiplier = mult, observedOffer = observedOffer };
            RM_BazaarKernel.RingPush(history, ref head, e);
        }

        public IEnumerable<RM_BazaarHistoryEntry> HistoryOldestFirst()
        {
            return RM_BazaarKernel.RingOldestFirst(history, head);
        }

        /// <summary>"Typical" for L1/L2: the mean multiplier across the ring.</summary>
        public float TypicalMultiplier
        {
            get
            {
                if (history.Count == 0) return target;
                float s = 0f;
                for (int i = 0; i < history.Count; i++) s += history[i].multiplier;
                return s / history.Count;
            }
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref tile, "tile", 0);
            Scribe_Values.Look(ref key, "key");
            Scribe_Values.Look(ref multiplier, "multiplier", 1f);
            Scribe_Values.Look(ref target, "target", 1f);
            Scribe_Values.Look(ref nudge, "nudge", 0f);
            Scribe_Values.Look(ref head, "head", 0);
            Scribe_Collections.Look(ref history, "history", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (history == null) history = new List<RM_BazaarHistoryEntry>();
                history.RemoveAll(h => h == null);
                head = RM_BazaarKernel.RingRepair(history, head);
            }
        }
    }

    public class RM_BazaarHistoryEntry : IExposable
    {
        public int day;
        public float multiplier = 1f;

        /// <summary>Mean observed buy price at a session open; -1 for a drift-tick entry.</summary>
        public float observedOffer = -1f;

        public void ExposeData()
        {
            Scribe_Values.Look(ref day, "day", 0);
            Scribe_Values.Look(ref multiplier, "multiplier", 1f);
            Scribe_Values.Look(ref observedOffer, "observedOffer", -1f);
        }
    }

    /// <summary>One trader visit (design §3 "Trader-visit log"), feeding L4 scarcity.</summary>
    public class RM_BazaarVisit : IExposable
    {
        public int day;
        public int tile;
        public string traderKind;
        public string traderName;
        public List<string> stock = new List<string>();

        public void ExposeData()
        {
            Scribe_Values.Look(ref day, "day", 0);
            Scribe_Values.Look(ref tile, "tile", 0);
            Scribe_Values.Look(ref traderKind, "traderKind");
            Scribe_Values.Look(ref traderName, "traderName");
            Scribe_Collections.Look(ref stock, "stock", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && stock == null) stock = new List<string>();
        }
    }
}
