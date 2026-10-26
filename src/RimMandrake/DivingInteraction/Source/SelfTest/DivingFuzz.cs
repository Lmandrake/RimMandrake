// Approach B for DivingInteraction: seeded random ACTION SEQUENCES over the Verse-free kernels the mod calls,
//   RM_GardenDefenseKernel (Chill garden offense scoring, tiers, cooldowns),
//   RM_ElderEconomyKernel   (Brine Elder novelty ledger, unique-treasure claims, silver payout),
//   RM_OxygenLedgerKernel   (pump-served rooms), RM_WalkerTrampleKernel (Scald walker trample/warn) and
//   RM_ChillFireBanKernel   (the seabed fire ban: flame classification, output gates, ignition of cells and pawns).
// The model (event log, reference sets) is this file's own; every number comes from the production kernel. A failing
// sequence is shrunk by delta debugging and printed as `family seed N: message | actions`, so it replays exactly.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;

namespace RimMandrake.DivingInteraction.SelfTest
{
    internal static class DivingFuzz
    {
        public static long Cases, Steps;

        internal struct Act
        {
            public int kind, a, b, c;
            public string Name;
            public override string ToString() { return Name + "(" + a + "," + b + "," + c + ")"; }
        }

        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        internal static List<T> Shrink<T>(List<T> acts, Func<List<T>, bool> fails)
        {
            var cur = new List<T>(acts);
            for (int chunk = Math.Max(1, cur.Count / 2); chunk >= 1; chunk /= 2)
            {
                bool progress = true;
                while (progress)
                {
                    progress = false;
                    for (int i = 0; i + chunk <= cur.Count; i++)
                    {
                        var trial = new List<T>(cur);
                        trial.RemoveRange(i, chunk);
                        if (fails(trial)) { cur = trial; progress = true; break; }
                    }
                }
            }
            return cur;
        }

        // ===================================================================== garden defense

        private static readonly int[] Dts = { 0, 0, 1, 17, 300, 2499, 2500, 2501, 10000, 59999, 60000, 60001, 200000 };
        private static readonly float[] Densities = { 0f, 0f, 1f, 0.5f, 0.1f, 0.999f };
        private static float Density(int arg) { return Densities[arg % Densities.Length]; }

        private sealed class GardenWorld
        {
            public RM_GardenDefenseKernel.State s = RM_GardenDefenseKernel.State.Fresh();
            public int now = 1000;
            public int lastT1 = int.MinValue / 2, lastT2 = int.MinValue / 2, lastAg = int.MinValue / 2;  // last fire of each channel
            public int lastT1Block = int.MinValue / 2;                                                     // last time the tier-1 channel was armed to cool (T1 or T2 fire)
        }

        private static GardenWorld MakeGarden(int seed) { return new GardenWorld { now = 1000 + (seed % 5) * 7919 }; }

        private static void GardenStep(GardenWorld w, Act a)
        {
            var before = w.s;
            switch (a.kind)
            {
                case 0: // offense: Harvest/Kill/HeatDamage after dt ticks
                {
                    w.now += Dts[a.b % Dts.Length];
                    var kind = (RM_GardenOffenseKind)(a.a % 3);
                    float d = Density(a.c);
                    float weight = RM_GardenDefenseKernel.WeightFor(kind);
                    float scoreIn = before.offenseScore + weight;
                    bool wantT2 = before.escalationScore + weight >= RM_GardenDefenseKernel.Tier2Threshold * (1f - RM_GardenDefenseKernel.TrailThresholdDiscount * d) && w.now >= before.tier2CooldownUntilTick;
                    bool wantT1 = !wantT2 && scoreIn >= RM_GardenDefenseKernel.Tier1Threshold * (1f - RM_GardenDefenseKernel.TrailThresholdDiscount * d) && w.now >= before.tier1CooldownUntilTick;
                    var o = RM_GardenDefenseKernel.Offense(ref w.s, kind, w.now, d);
                    Check((o == RM_GardenDefenseKernel.Outcome.Tier2Wake) == wantT2, $"tier-2 wake {(o == RM_GardenDefenseKernel.Outcome.Tier2Wake ? "fired" : "did not fire")} but score {scoreIn} at t={w.now} (cd2 {before.tier2CooldownUntilTick}, density {d}) says it should {(wantT2 ? "" : "not ")}");
                    Check((o == RM_GardenDefenseKernel.Outcome.Tier1Arc) == wantT1, $"tier-1 arc {(o == RM_GardenDefenseKernel.Outcome.Tier1Arc ? "fired" : "did not fire")} but score {scoreIn} at t={w.now} (cd1 {before.tier1CooldownUntilTick}, density {d}) says it should {(wantT1 ? "" : "not ")}");
                    if (o == RM_GardenDefenseKernel.Outcome.None)
                        Check(w.s.offenseScore == scoreIn && w.s.escalationScore == before.escalationScore + weight, "a non-firing offense changed the scores by other than its weight");
                    else
                    {
                        Check(w.s.offenseScore == 0f, "a firing offense left score " + w.s.offenseScore);
                        Check(o == RM_GardenDefenseKernel.Outcome.Tier2Wake ? w.s.escalationScore == 0f : w.s.escalationScore == before.escalationScore + weight, "escalation pool wrong after " + o);
                        Check(w.s.tier1CooldownUntilTick == w.now + RM_GardenDefenseKernel.Tier1CooldownTicks, "a fire did not arm the tier-1 cooldown");
                        // spacing: the tier-1 channel (arc, or the arc a wake replaces) is never re-armed early
                        if (o == RM_GardenDefenseKernel.Outcome.Tier1Arc)   // a wake may follow an arc at once; an arc never follows either inside the cooldown
                            Check(w.now - w.lastT1Block >= RM_GardenDefenseKernel.Tier1CooldownTicks, $"arc {w.now - w.lastT1Block} ticks after the last arc or wake (< {RM_GardenDefenseKernel.Tier1CooldownTicks})");
                        w.lastT1Block = w.now;
                    }
                    if (o == RM_GardenDefenseKernel.Outcome.Tier2Wake)
                    {
                        Check(w.now - w.lastT2 >= RM_GardenDefenseKernel.Tier2CooldownTicks, $"two wakes {w.now - w.lastT2} ticks apart (< a day)");
                        Check(w.s.tier2CooldownUntilTick == w.now + RM_GardenDefenseKernel.Tier2CooldownTicks, "a wake did not arm the tier-2 cooldown");
                        w.lastT2 = w.now;
                    }
                    Check(w.s.agitationScore == before.agitationScore && w.s.agitationCooldownUntilTick == before.agitationCooldownUntilTick, "an offense touched the drill-agitation pool");
                    break;
                }
                case 1: // drill agitation
                {
                    w.now += Dts[a.b % Dts.Length];
                    float d = Density(a.c);
                    float scoreIn = before.agitationScore + RM_GardenDefenseKernel.DrillAgitationWeight;
                    bool want = scoreIn >= RM_GardenDefenseKernel.AgitationTier1Threshold * (1f - RM_GardenDefenseKernel.TrailThresholdDiscount * d) && w.now >= before.agitationCooldownUntilTick;
                    bool fired = RM_GardenDefenseKernel.Agitation(ref w.s, w.now, d);
                    Check(fired == want, $"agitation arc {(fired ? "fired" : "did not fire")} but score {scoreIn} at t={w.now} (cd {before.agitationCooldownUntilTick}, density {d}) says it should {(want ? "" : "not ")}");
                    if (fired)
                    {
                        Check(w.now - w.lastAg >= RM_GardenDefenseKernel.AgitationCooldownTicks, $"two agitation arcs {w.now - w.lastAg} ticks apart");
                        Check(w.s.agitationScore == 0f, "a firing agitation left a score");
                        w.lastAg = w.now;
                    }
                    Check(w.s.offenseScore == before.offenseScore && w.s.tier1CooldownUntilTick == before.tier1CooldownUntilTick && w.s.tier2CooldownUntilTick == before.tier2CooldownUntilTick,
                          "drilling touched the offense pool or the tier cooldowns (it must never be able to wake the Tarnn)");
                    break;
                }
                case 2: // save + load: Scribe writes floats as text
                {
                    var r = w.s;
                    r.offenseScore = float.Parse(w.s.offenseScore.ToString("R", CultureInfo.InvariantCulture), CultureInfo.InvariantCulture);
                    r.escalationScore = float.Parse(w.s.escalationScore.ToString("R", CultureInfo.InvariantCulture), CultureInfo.InvariantCulture);
                    r.agitationScore = float.Parse(w.s.agitationScore.ToString("R", CultureInfo.InvariantCulture), CultureInfo.InvariantCulture);
                    Check(r.offenseScore == w.s.offenseScore && r.agitationScore == w.s.agitationScore, "score did not survive a text round trip");
                    Check(r.escalationScore == w.s.escalationScore, "escalation score did not survive a text round trip");
                    w.s = r;
                    break;
                }
                case 3: // idle time passes
                    w.now += Dts[a.b % Dts.Length];
                    break;
            }
            var x = w.s;
            Check(x.offenseScore >= 0f && !float.IsNaN(x.offenseScore) && !float.IsInfinity(x.offenseScore), "offense score " + x.offenseScore);
            Check(x.agitationScore >= 0f && !float.IsNaN(x.agitationScore) && !float.IsInfinity(x.agitationScore), "agitation score " + x.agitationScore);
            Check(x.tier1CooldownUntilTick >= before.tier1CooldownUntilTick && x.tier2CooldownUntilTick >= before.tier2CooldownUntilTick && x.agitationCooldownUntilTick >= before.agitationCooldownUntilTick,
                  "a cooldown moved backwards");
        }

        private static List<Act> GenGarden(Random r, int len)
        {
            var l = new List<Act>(len);
            string[] names = { "Offense", "Agitate", "Reload", "Idle" };
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(20);
                int kind = k < 11 ? 0 : k < 16 ? 1 : k < 18 ? 2 : 3;
                l.Add(new Act { kind = kind, Name = names[kind], a = r.Next(30), b = r.Next(1000), c = r.Next(1000) });
            }
            return l;
        }

        private static string RunGarden(int seed, List<Act> acts)
        {
            try { var w = MakeGarden(seed); foreach (var a in acts) { GardenStep(w, a); Steps++; } return null; }
            catch (Exception ex) { return ex.Message; }
        }

        public static List<string> Garden(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 7919 + 3);
                var acts = GenGarden(r, r.Next(5, 200));
                Cases++;
                if (RunGarden(seed, acts) == null) continue;
                var min = Shrink(acts, t => RunGarden(seed, t) != null);
                fails.Add($"garden seed {seed}: {RunGarden(seed, min)} | {string.Join(" ", min)}");
                if (fails.Count >= 5) break;
            }
            return fails;
        }

        // ===================================================================== elder economy

        private sealed class Rec : IElderTileRecord
        {
            public int tile; public List<string> seen = new List<string>();
            public int Tile => tile;
            public List<string> SeenKeys => seen;
        }

        private static readonly string[] Pool = { "RM_ElderSealedRelic", "RM_ElderUnknownWeapon", "RUT_ElderLightsaber", "RUT_ElderNavcore" };
        private static readonly string[] Keys = { "Material:Steel", "Material:Silver", "Lifeform:Muffalo", "Xenotype:Sanguophage", "Lifeform:Thrumbo", "Material:Gold" };
        private static readonly float[] Values = { 0f, 0.01f, 1.9f, 8f, 36f, 450f, 3500f, 1.0e7f, 4.0e8f, 3.0e10f };
        private static readonly int[] Stacks = { 1, 1, 2, 75, 500, 100000 };

        private sealed class ElderWorld
        {
            public List<Rec> recs = new List<Rec>();
            public List<string> granted = new List<string>();
            public HashSet<string> resolvable = new HashSet<string>(Pool);
            public Dictionary<int, HashSet<string>> seen = new Dictionary<int, HashSet<string>>();   // reference ledger
            public List<string> delivered = new List<string>();                                       // treasures actually handed over
        }

        private static ElderWorld MakeElder(int seed)
        {
            var w = new ElderWorld();
            var r = new Random(seed);
            foreach (var p in Pool) if (r.Next(4) == 0) w.resolvable.Remove(p);   // some treasure mods absent from the start
            return w;
        }

        private static int Round(float scaled) { return (int)Math.Round(scaled); }

        private static void ElderStep(ElderWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: // Offer(tile, key, value, stack, roll, pick)
                {
                    int tile = a.a % 6 - 1;              // -1 = a map with no world tile
                    string key = Keys[a.b % Keys.Length];
                    float mv = Values[a.c % Values.Length];
                    int stack = Stacks[(a.c / 10) % Stacks.Length];
                    bool roll = (a.c / 100) % 3 != 0;
                    int pickSeed = a.c / 7;
                    bool wasSeen = tile >= 0 && w.seen.TryGetValue(tile, out var hs) && hs.Contains(key);
                    int recsBefore = w.recs.Count;
                    var grantedBefore = new List<string>(w.granted);
                    int pickCalls = 0;
                    var d = RM_ElderEconomyKernel.Decide(w.recs, w.granted, t => new Rec { tile = t }, tile, key, tile >= 0, mv, stack, Pool,
                        n => w.resolvable.Contains(n), () => roll, n => { pickCalls++; return pickSeed % n; });

                    Check(d.Novel == (tile >= 0 && !wasSeen), $"novel={d.Novel} for tile {tile} key {key} but the ledger had it seen={wasSeen}");
                    if (tile >= 0)
                    {
                        if (!w.seen.ContainsKey(tile)) w.seen[tile] = new HashSet<string>();
                        w.seen[tile].Add(key);
                    }
                    else Check(w.recs.Count == recsBefore, "a tile-less offer wrote a ledger record");
                    if (!d.Novel) Check(d.Treasure == null, "a stale offer was paid a unique treasure");
                    if (d.Treasure != null)
                    {
                        Check(Pool.Contains(d.Treasure), "treasure " + d.Treasure + " is not in the pool");
                        Check(w.resolvable.Contains(d.Treasure), "treasure " + d.Treasure + " was claimed although its def cannot be made: the payout is lost and the world's only copy is burned");
                        Check(!grantedBefore.Contains(d.Treasure), "treasure " + d.Treasure + " granted a second time");
                        Check(d.Silver == 0, "a treasure trade also paid silver " + d.Silver);
                        w.delivered.Add(d.Treasure);
                    }
                    else
                    {
                        Check(d.Silver >= (d.Novel ? RM_ElderEconomyKernel.NovelValueFloor : RM_ElderEconomyKernel.StaleValueFloor), $"silver {d.Silver} below the floor (novel={d.Novel}, value {mv} x{stack})");
                        Check(d.Silver <= RM_ElderEconomyKernel.MaxSilver, "silver " + d.Silver + " above the cap");
                        float v = mv * stack;
                        if (v * 8f < 1.0e6f)    // the exact range: compare to an independent rounding
                        {
                            int want = Math.Max(d.Novel ? 50 : 1, Round(v * (d.Novel ? 8f : 0.05f)));
                            Check(d.Silver == want, $"silver {d.Silver} != {want} for value {v} novel={d.Novel}");
                        }
                    }
                    if (!roll || !d.Novel) Check(pickCalls == 0, "the treasure pick ran without a winning roll on a novel trade");
                    break;
                }
                case 1: // save + load: the ledger and the granted list survive a deep copy
                {
                    var copy = w.recs.Select(r => new Rec { tile = r.tile, seen = new List<string>(r.seen) }).ToList();
                    w.recs = copy;
                    w.granted = new List<string>(w.granted);
                    break;
                }
                case 2: // a treasure's mod is added or removed between sessions
                {
                    string p = Pool[a.a % Pool.Length];
                    if (!w.resolvable.Add(p)) w.resolvable.Remove(p);
                    break;
                }
                case 3: // pure query
                {
                    int tile = a.a % 6 - 1; string key = Keys[a.b % Keys.Length];
                    bool got = RM_ElderEconomyKernel.HasSeen(w.recs, tile, key);
                    bool want = tile >= 0 && w.seen.TryGetValue(tile, out var hs2) && hs2.Contains(key);
                    Check(got == want, $"HasSeen({tile},{key})={got}, reference {want}");
                    break;
                }
            }
            // ledger == reference, no duplicate tiles or keys, granted == delivered
            Check(w.recs.Select(r => r.tile).Distinct().Count() == w.recs.Count, "two ledger records for one tile");
            foreach (var r in w.recs)
            {
                Check(r.seen.Distinct().Count() == r.seen.Count, "a duplicate key in tile " + r.tile);
                Check(w.seen.TryGetValue(r.tile, out var hs3) && hs3.SetEquals(r.seen), "ledger of tile " + r.tile + " differs from the reference");
            }
            Check(w.recs.Count == w.seen.Count, "ledger has " + w.recs.Count + " tiles, reference " + w.seen.Count);
            Check(w.granted.Distinct().Count() == w.granted.Count, "granted list holds a duplicate");
            Check(new HashSet<string>(w.granted).SetEquals(w.delivered), $"granted [{string.Join(",", w.granted)}] but delivered [{string.Join(",", w.delivered)}]: a claim was burned without a delivery");
        }

        private static List<Act> GenElder(Random r, int len)
        {
            var l = new List<Act>(len);
            string[] names = { "Offer", "Reload", "ToggleMod", "Query" };
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(20);
                int kind = k < 14 ? 0 : k < 16 ? 1 : k < 18 ? 2 : 3;
                l.Add(new Act { kind = kind, Name = names[kind], a = r.Next(60), b = r.Next(60), c = r.Next(100000) });
            }
            return l;
        }

        private static string RunElder(int seed, List<Act> acts)
        {
            try { var w = MakeElder(seed); foreach (var a in acts) { ElderStep(w, a); Steps++; } return null; }
            catch (Exception ex) { return ex.Message; }
        }

        public static List<string> Elder(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 104729 + 5);
                var acts = GenElder(r, r.Next(5, 160));
                Cases++;
                if (RunElder(seed, acts) == null) continue;
                var min = Shrink(acts, t => RunElder(seed, t) != null);
                fails.Add($"elder seed {seed}: {RunElder(seed, min)} | {string.Join(" ", min)}");
                if (fails.Count >= 5) break;
            }
            return fails;
        }

        // ===================================================================== units

        public static List<string> Units(int n, int baseSeed)
        {
            var fails = new List<string>();
            var r = new Random(baseSeed);
            // payout never falls as the offered value grows (an int overflow would drop it to the floor)
            foreach (bool novel in new[] { true, false })
                for (int k = 0; k < Math.Max(1, n / 20) && fails.Count < 5; k++)
                {
                    Cases++;
                    int stack = Stacks[r.Next(Stacks.Length)];
                    int prev = 0; float prevV = 0f;
                    for (double e = -2; e <= 12.5; e += 0.05)
                    {
                        Steps++;
                        float mv = (float)Math.Pow(10, e);
                        int s = RM_ElderEconomyKernel.SilverFor(novel, mv, stack);
                        if (s < prev) { fails.Add($"units: silver fell from {prev} (value {prevV}) to {s} (value {mv}) at stack {stack}, novel={novel}"); break; }
                        prev = s; prevV = mv;
                    }
                }
            // thresholds fall as trail density rises, never to zero at density 1
            for (int k = 0; k < Math.Max(1, n / 20) && fails.Count < 5; k++)
            {
                Cases++; Steps++;
                float b = 1f + k * 0.37f, d1 = (float)r.NextDouble(), d2 = Math.Min(1f, d1 + (float)r.NextDouble());
                if (RM_GardenDefenseKernel.AdjustedThreshold(b, d2) > RM_GardenDefenseKernel.AdjustedThreshold(b, d1)) fails.Add($"units: threshold rose with density ({d1}->{d2})");
                if (!(RM_GardenDefenseKernel.AdjustedThreshold(b, 1f) > 0f)) fails.Add("units: a saturated trail drives the threshold to zero or below");
            }
            // a Drill kind carries no weight into the offense pool
            Cases++; Steps++;
            if (RM_GardenDefenseKernel.WeightFor(RM_GardenOffenseKind.DrillAgitation) != 0f) fails.Add("units: DrillAgitation carries offense weight");
            // the first real-world numbers from the design text: ~8 harvests to Tier1 alone, a kill or a heat hit alone crosses Tier1
            Cases++; Steps++;
            {
                var s = RM_GardenDefenseKernel.State.Fresh(); int h = 0; var o = RM_GardenDefenseKernel.Outcome.None;
                while (o == RM_GardenDefenseKernel.Outcome.None && h < 50) { o = RM_GardenDefenseKernel.Offense(ref s, RM_GardenOffenseKind.Harvest, 5000, 0f); h++; }
                if (!(o == RM_GardenDefenseKernel.Outcome.Tier1Arc && h == 8)) fails.Add($"units: harvest-only reached {o} after {h} harvests (design: Tier1 after 8)");
                var s2 = RM_GardenDefenseKernel.State.Fresh();
                if (RM_GardenDefenseKernel.Offense(ref s2, RM_GardenOffenseKind.Kill, 5000, 0f) != RM_GardenDefenseKernel.Outcome.Tier1Arc) fails.Add("units: one kill did not arc");
                var s3 = RM_GardenDefenseKernel.State.Fresh();
                if (RM_GardenDefenseKernel.Offense(ref s3, RM_GardenOffenseKind.HeatDamage, 5000, 0f) != RM_GardenDefenseKernel.Outcome.Tier1Arc) fails.Add("units: one heat hit did not arc");
            }
            // GARDEN_ESCALATION_PROGRESS_FIX_1: offending at the tier-1 cadence must still reach the wake
            Cases++; Steps++;
            {
                var s = RM_GardenDefenseKernel.State.Fresh(); int t = 5000; bool woke = false;
                for (int i = 0; i < 6 && !woke; i++)
                {
                    woke = RM_GardenDefenseKernel.Offense(ref s, RM_GardenOffenseKind.Kill, t, 0f) == RM_GardenDefenseKernel.Outcome.Tier2Wake;
                    t += RM_GardenDefenseKernel.Tier1CooldownTicks;
                }
                if (!woke) fails.Add("units: six kills at the tier-1 cadence never woke the Tarnn (tier-1 arcs reset tier-2 progress)");
            }
            return fails;
        }

        // ════════════════ oxygen (DESIGN_PASS DI-2): the pumped-air ledger never lets one pump cancel another ════════════════
        // One RNG per printed seed: the seed in a FAIL line is the seed --fuzz-seed replays (oxygen, trample, fireban).
        private static Random CaseRng(int seed, int salt) { return new Random(seed * 7919 + salt); }
        public static List<int> RngTrace;   // when set, each case appends its RNG's first draw (replay check)
        private static Random Traced(int seed, int salt) { if (RngTrace != null) RngTrace.Add(CaseRng(seed, salt).Next()); return CaseRng(seed, salt); }

        private static List<string> Oxygen(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                Cases++;
                int seed = baseSeed + k;
                var r = Traced(seed, 11);
                var led = new RM_OxygenLedgerKernel();
                var model = new Dictionary<int, HashSet<int>>();
                int steps = r.Next(1, 60);
                try
                {
                    for (int st = 0; st < steps; st++)
                    {
                        Steps++;
                        int prov = r.Next(0, 5);
                        if (r.Next(3) == 0) { led.Clear(prov); model.Remove(prov); }
                        else
                        {
                            var cells = new List<int>(); int m = r.Next(0, 12);
                            for (int i = 0; i < m; i++) cells.Add(r.Next(0, 20));
                            led.Set(prov, cells);
                            if (cells.Count == 0) model.Remove(prov); else model[prov] = new HashSet<int>(cells);
                        }
                        for (int c = 0; c < 20; c++)
                        {
                            int want = model.Values.Count(h => h.Contains(c));
                            Check(led.CoverCount(c) == want, $"cell {c} count {led.CoverCount(c)} != spec {want}");
                            Check(led.Covered(c) == (want > 0), $"cell {c} covered {led.Covered(c)} with {want} providers");
                        }
                        Check(led.ProviderCount == model.Count, $"providers {led.ProviderCount} != spec {model.Count}");
                    }
                }
                catch (Exception e) { fails.Add($"oxygen seed {seed}: {e.Message}"); }
            }
            Cases++; Steps++;
            if (!RM_OxygenLedgerKernel.RoomServed(true, 60, 1, 60) || RM_OxygenLedgerKernel.RoomServed(true, 61, 1, 60) || !RM_OxygenLedgerKernel.RoomServed(true, 120, 2, 60)
                || RM_OxygenLedgerKernel.RoomServed(false, 10, 3, 60) || RM_OxygenLedgerKernel.RoomServed(true, 10, 0, 60) || !RM_OxygenLedgerKernel.RoomServed(true, 99999, 1, 0)
                || RM_OxygenLedgerKernel.RoomServed(true, 0, 1, 60) || !RM_OxygenLedgerKernel.RoomServed(true, int.MaxValue, 2, int.MaxValue))
                fails.Add("oxygen units: RoomServed boundaries (capacity pooled, unsealed/no pump/empty never served, 0 = no limit, no overflow)");
            Cases++; Steps++;
            if (RM_ElderEconomyKernel.DistinctKinds(new[] { "a", "b", "a", "", null, "c" }) != 3 || RM_ElderEconomyKernel.DistinctKinds(null) != 0
                || RM_ElderEconomyKernel.CabinetBeauty(0) != 0f || RM_ElderEconomyKernel.CabinetBeauty(-5) != 0f || RM_ElderEconomyKernel.CabinetBeauty(3) != 6f
                || RM_ElderEconomyKernel.CabinetBeauty(100000) != RM_ElderEconomyKernel.CabinetBeautyCap
                || RM_ElderEconomyKernel.MuseumMoodStage(0) != -1 || RM_ElderEconomyKernel.MuseumMoodStage(1) != 0 || RM_ElderEconomyKernel.MuseumMoodStage(3) != 0
                || RM_ElderEconomyKernel.MuseumMoodStage(4) != 1 || RM_ElderEconomyKernel.MuseumMoodStage(10) != 2 || RM_ElderEconomyKernel.MuseumMoodStage(int.MaxValue) != 2)
                fails.Add("cabinet units: DistinctKinds counts each key once and ignores empties; beauty 0 below one kind and capped; mood stage -1/0/1/2 at 0/1/4/10 kinds");
            return fails;
        }

        // SCALD_WALKING_PASTURE_1 trample: drive RM_WalkerTrampleKernel.Decide exactly as the map component does
        // (it records lastTrample AND lastWarn on a trample, lastWarn on a warning) and check every outcome against
        // the ruling's own rule written out here.
        public static List<string> Trample(int n, int baseSeed)
        {
            var fails = new List<string>();
            float tr2 = RM_WalkerTrampleKernel.TrampleRadius * RM_WalkerTrampleKernel.TrampleRadius;
            float wr2 = RM_WalkerTrampleKernel.WarnRadius * RM_WalkerTrampleKernel.WarnRadius;
            for (int c = 0; c < n && fails.Count < 5; c++)
            {
                Cases++;
                int seed = baseSeed + c;
                var r = Traced(seed, 13);
                int now = r.Next(0, 100000), lt = -1, lw = -1, lastTrampleSeen = -1000000;
                bool en = r.Next(4) != 0, warn = r.Next(4) != 0;
                for (int step = 0; step < 60; step++)
                {
                    Steps++;
                    now += RM_WalkerTrampleKernel.SweepInterval * (1 + r.Next(4));
                    float d;
                    int pick = r.Next(10);
                    if (pick == 0) d = float.PositiveInfinity;
                    else if (pick == 1) d = float.NaN;
                    else if (pick == 2) d = -1f;
                    else d = r.Next(0, 50);
                    bool downed = r.Next(8) == 0;
                    var o = RM_WalkerTrampleKernel.Decide(d, downed, now, lt, lw, en, warn);
                    bool valid = !float.IsNaN(d) && d >= 0f;
                    bool wantT = valid && en && !downed && d <= tr2 && (lt < 0 || now - lt >= RM_WalkerTrampleKernel.TrampleCooldownTicks);
                    bool wantW = !wantT && valid && en && warn && !downed && d <= wr2 && (lw < 0 || now - lw >= RM_WalkerTrampleKernel.WarnCooldownTicks);
                    var want = wantT ? RM_WalkerTrampleKernel.Outcome.Trample : (wantW ? RM_WalkerTrampleKernel.Outcome.Warn : RM_WalkerTrampleKernel.Outcome.None);
                    if (o != want) { fails.Add($"trample seed {seed}: got {o}, want {want} (d2 {d}, downed {downed}, now {now}, lt {lt}, lw {lw}, en {en}, warn {warn})"); break; }
                    if (o == RM_WalkerTrampleKernel.Outcome.Trample)
                    {
                        if (now - lastTrampleSeen < RM_WalkerTrampleKernel.TrampleCooldownTicks) { fails.Add($"trample seed {seed}: two tramples {now - lastTrampleSeen} ticks apart"); break; }
                        lastTrampleSeen = now; lt = now; lw = now;
                    }
                    else if (o == RM_WalkerTrampleKernel.Outcome.Warn) lw = now;
                    if (!en && o != RM_WalkerTrampleKernel.Outcome.None) { fails.Add($"trample seed {seed}: {o} with trampling switched off"); break; }
                }
            }
            // damage: clamped, NaN/inf -> default, monotone, default inside the range
            Cases++;
            float prev = float.MinValue;
            for (float v = -10f; v <= 50f; v += 0.25f)
            {
                Steps++;
                float dmg = RM_WalkerTrampleKernel.Damage(v);
                if (dmg < RM_WalkerTrampleKernel.MinDamage || dmg > RM_WalkerTrampleKernel.MaxDamage) fails.Add($"trample: damage {dmg} for setting {v} outside the slider range");
                if (dmg < prev) fails.Add($"trample: damage fell from {prev} to {dmg} as the setting rose to {v}");
                prev = dmg;
            }
            if (RM_WalkerTrampleKernel.Damage(float.NaN) != RM_WalkerTrampleKernel.DefaultDamage || RM_WalkerTrampleKernel.Damage(float.PositiveInfinity) != RM_WalkerTrampleKernel.DefaultDamage)
                fails.Add("trample: NaN/infinite damage setting does not fall back to the shipped default");
            if (RM_WalkerTrampleKernel.Damage(RM_WalkerTrampleKernel.DefaultDamage) != RM_WalkerTrampleKernel.DefaultDamage)
                fails.Add("trample: the shipped default lies outside the slider range");
            return fails;
        }

        // CHILL_FIRE_BAN_1 + CHILLFIREBAN_DECIDE_FUELLED_COOKING_POWER: a random fuel-burning (or not) building lives on
        // the seabed while a pump switches the air on and off. Drive RM_ChillFireBanKernel exactly as Patch_ChillFireBan
        // does (UsesFlame per def; Output gates lit/heat/bills/power with the flame flag; SkipFuelBurn on CompTick) and
        // check it against the ruling written out here: "total ban — no flame works on the Chill seabed map. Campfires
        // fizzle, chemfuel won't light"; pumped air brings fire back; electric things and fuelled machines are untouched.
        public static List<string> FireBan(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int c = 0; c < n && fails.Count < 5; c++)
            {
                Cases++;
                int seed = baseSeed + c;
                var r = Traced(seed, 17);
                bool refuel = r.Next(4) != 0, glow = r.Next(2) == 0, heat = r.Next(2) == 0, overlay = r.Next(3) == 0;
                bool table = r.Next(3) == 0, plant = r.Next(4) == 0, powered = plant || r.Next(3) == 0;
                bool inert = r.Next(6) == 0;   // RM_NonCombustionExtension on the def
                bool flame = RM_ChillFireBanKernel.UsesFlame(refuel, glow, heat, overlay, table, plant, powered, inert);
                string who = $"refuel {refuel} glow {glow} heat {heat} overlay {overlay} table {table} plant {plant} powered {powered} burnsNothing {inert}";
                // The classification is checked clause by clause, each one a ruling, not the kernel's expression copied
                // back. Over seven flags any complete oracle is the same truth table, so the check that can disagree with
                // the kernel is the named-building table below (real comp sets from the def dump, verdict from what the
                // building's description says it burns); the random part here tests the gating plumbing.
                string clause = null;
                if (!refuel && flame) clause = "no fuel, yet a flame (electric things are never touched)";
                else if (inert && flame) clause = "a def marked burns-nothing (RM_NonCombustionExtension) counted as a flame";
                else if (refuel && powered && !plant && flame) clause = "a fuelled powered machine counted as a flame (CHILLFIREBAN_FIX_POWERED_MACHINE_FREE_FUEL)";
                else if (refuel && !powered && !inert && flame != (glow || heat || overlay || table)) clause = "an unpowered fuelled building is a flame exactly when it lights, heats, shows a flame or works bills";
                else if (refuel && plant && !inert && (heat || overlay) && !flame) clause = "a fuelled plant that pushes heat or shows a flame is combustion and must be banned";
                else if (refuel && plant && !heat && !overlay && flame) clause = "a fuelled plant with no heat and no flame is not burning (CHILLFIREBAN_FIX_NONCOMBUSTION_PLANT_BANNED)";
                if (clause != null) { fails.Add($"fireban seed {seed}: UsesFlame {flame}: {clause} ({who})"); continue; }
                float fuel = refuel ? r.Next(1, 50) : 0f;
                bool air = r.Next(2) == 0;
                try
                {
                    for (int step = 0; step < 40; step++)
                    {
                        Steps++;
                        if (r.Next(5) == 0) air = !air;   // the pump starts, stops, the room unseals
                        bool hasFuel = !refuel || fuel > 0f;
                        bool vLit = refuel && hasFuel, vHeat = hasFuel && (heat || !refuel), vBills = table && hasFuel && r.Next(6) != 0, vPower = plant && hasFuel;
                        bool lit = RM_ChillFireBanKernel.Output(vLit, flame, air);               // ShouldBeLitNow: Gate(), flame buildings only
                        bool hot = RM_ChillFireBanKernel.Output(vHeat, flame, air);              // heaters: Gate(), flame buildings only
                        bool bills = RM_ChillFireBanKernel.Output(vBills, flame, air);           // Gate(): flame buildings only
                        bool power = RM_ChillFireBanKernel.Output(vPower, flame, air);
                        bool skip = RM_ChillFireBanKernel.SkipFuelBurn(flame, air);
                        bool note = RM_ChillFireBanKernel.ShowNoAirNote(flame, air);
                        Check((!lit || vLit) && (!hot || vHeat) && (!bills || vBills) && (!power || vPower), "the ban turned an output ON");
                        if (air) Check(lit == vLit && hot == vHeat && bills == vBills && power == vPower && !skip && !note, "pumped air did not give the building back its vanilla behaviour");
                        if (!refuel) Check(hot == vHeat && bills == vBills && power == vPower && !skip && !note, "an electric building was touched by the fire ban");
                        if (flame && !air)
                        {
                            Check(!lit && !hot && !bills && !power, $"a banned flame building still works: lit {lit} heat {hot} bills {bills} power {power}");
                            Check(skip, "a banned flame building still burns fuel");
                            Check(note, "a banned flame building does not say why it is out");
                        }
                        if (!flame) Check(lit == vLit && hot == vHeat && bills == vBills && power == vPower && !skip && !note, "a non-flame building (machine, turret barrel, tank, non-combustion plant) was gated");
                        float before = fuel;
                        if (refuel && !skip && hasFuel) fuel = Math.Max(0f, fuel - 1f);
                        if (flame && !air) Check(fuel == before, "fuel fell while the ban held");
                    }
                }
                catch (Exception e) { fails.Add($"fireban seed {seed}: {e.Message} ({who})"); }
            }
            // the named vanilla and modded buildings the ruling and the review name
            Cases++; Steps++;
            bool Banned(bool rf, bool g, bool h, bool o, bool t, bool p, bool pw, bool inertDef = false) { return RM_ChillFireBanKernel.UsesFlame(rf, g, h, o, t, p, pw, inertDef); }
            if (!Banned(true, true, true, true, true, false, false)) fails.Add("fireban units: Campfire (fuel, glow, heat, flame, bills) is not a flame building — it would still cook on the seabed");
            if (!Banned(true, false, true, false, true, false, false)) fails.Add("fireban units: FueledStove is not a flame building");
            if (!Banned(true, false, false, false, true, false, false)) fails.Add("fireban units: FueledSmithy is not a flame building");
            if (!Banned(true, true, true, false, false, true, true)) fails.Add("fireban units: WoodFiredGenerator / ChemfuelPoweredGenerator is not a flame building — it would still make power");
            if (!Banned(true, true, false, true, false, false, false)) fails.Add("fireban units: TorchLamp is not a flame building");
            if (Banned(false, true, true, false, true, false, true)) fails.Add("fireban units: ElectricStove (no fuel) was banned");
            if (Banned(true, true, false, false, false, false, true)) fails.Add("fireban units: KoltoTank (fuelled powered machine) was banned");
            if (Banned(true, false, false, false, false, false, false)) fails.Add("fireban units: a turret barrel / shuttle tank (fuel, no flame use) was banned");
            // Fuelled power plants from the def-dump census (2026-10-26), comp sets as shipped (glow, heat, overlay):
            if (!Banned(true, true, true, false, false, true, true)) fails.Add("fireban units: BioferriteGenerator (\"igniting bioferrite\": glow, heat) is not a flame building");
            if (!Banned(true, false, true, false, false, true, true)) fails.Add("fireban units: KOTOR_ReactorRhydonium_small (\"igniting motes of Rhydonium\": heat, no glow) is not a flame building");
            if (Banned(true, false, false, false, false, true, true)) fails.Add("fireban units: RM_DecayCell (digests rot: no glow, heat or flame) was banned");
            if (Banned(true, true, false, false, false, true, true)) fails.Add("fireban units: RUT_VaultHeart / OuterRim_FusionReactorLight (glow only, nothing burns) was banned");
            // VQE The Generator, Buildings_Nuclear_Genetrons.xml (1.6): refuel (RefuelableWithOverdrive), glow, heat, power plant.
            if (Banned(true, true, true, false, false, true, true, true)) fails.Add("fireban units: VQE_Genetron_UraniumPowered (fission, RM_NonCombustionExtension) was banned — it burns nothing");
            if (!Banned(true, true, true, false, false, true, true, false)) fails.Add("fireban units: a chemfuel/wood Genetron (same comps, no burns-nothing tag) is not a flame building");
            if (RM_ChillFireBanKernel.Output(false, true, false) || RM_ChillFireBanKernel.Output(false, true, true)) fails.Add("fireban units: Output turned an off output on");
            return fails;
        }

        // CHILLFIREBAN_FIX_ATTACHED_FIRE_UNGATED + _MELTDOWN_FIRE_ESCAPES_BAN + _FUSELIGHT_FIRE_SPREADS. A fire source (named below)
        // goes off on a small map; its fire tries cells (TryStartFireIn) and pawns standing in burning cells
        // (TryAttachFire), and spreads cell to cell carrying its instigator (Fire.cs:403), all asked through
        // RM_ChillFireBanKernel.IgnitionAllowed exactly as RM_ChillFireGate does. The oracle is the ruling written out,
        // not the kernel's expression: on the Chill seabed with the ban on, "fire exists below only where someone pumps
        // air down", and the one exception is a thing that carries its own oxidizer (Fuselight). A reactor that "burns
        // nothing" keeps running (FireBan above) but its meltdown flame is not an oxidizer. Anywhere else, fire is vanilla.
        private static readonly (string name, bool selfOx, bool burnsNothing)[] FireSources =
        {
            ("molotov (pawn instigator)", false, false),
            ("incendiary launcher / IncendiaryShell", false, false),
            ("flamethrower hit (FlameThrower.cs:19 attach)", false, false),
            ("beam weapon (Verb_ShootBeam.cs:457 attach)", false, false),
            ("lightning / short circuit (no instigator)", false, false),
            ("lava terrain (HediffGiver_Terrain attach, no instigator)", false, false),
            ("RM_Fuselight explosion (RM_SelfOxidizingExtension)", true, false),
            ("VQE_Genetron_UraniumPowered meltdown (RM_NonCombustionExtension)", false, true),
            ("VQE_Genetron_Atomic meltdown (RM_NonCombustionExtension)", false, true),
            ("chemfuel Genetron meltdown (no extension)", false, false),
        };

        public static List<string> Ignition(int n, int baseSeed)
        {
            var fails = new List<string>();
            const int W = 10;
            for (int c = 0; c < n && fails.Count < 5; c++)
            {
                Cases++;
                int seed = baseSeed + c;
                var r = Traced(seed, 23);
                var src = FireSources[r.Next(FireSources.Length)];
                bool seabed = r.Next(4) != 0, banOn = r.Next(6) != 0;
                var air = new bool[W * W];
                if (r.Next(3) != 0)
                {
                    int x0 = r.Next(W), y0 = r.Next(W), x1 = Math.Min(W, x0 + 1 + r.Next(4)), y1 = Math.Min(W, y0 + 1 + r.Next(4));
                    for (int x = x0; x < x1; x++) for (int y = y0; y < y1; y++) air[x * W + y] = true;   // a sealed pumped room
                }
                var pawn = new bool[W * W];
                for (int i = 0; i < W * W; i++) pawn[i] = r.Next(8) == 0;
                // byFire: asked from inside a burning Fire's tick (spread, attach, its own damage), as Patch_Fire_TickInterval marks it
                bool Ask(int cell, bool byFire) { return RM_ChillFireBanKernel.IgnitionAllowed(seabed, banOn, src.selfOx, src.burnsNothing, byFire, air[cell]); }
                // independent truth: does the ruling allow fire from THIS source in THIS cell? Fuselight's oxidizer is its
                // flash: the cells the blast itself reaches. What then burns is the tar or wood, which has no air either.
                bool vanilla = !seabed || !banOn;
                bool Ruled(int cell, bool byFire) { return vanilla || air[cell] || (src.selfOx && !byFire); }
                string who = $"{src.name} seabed {seabed} ban {banOn}";
                var burning = new bool[W * W];
                var onFire = new bool[W * W];
                var flashed = new bool[W * W];   // cell lit by the blast itself, not by a fire
                var pawnFlashed = new bool[W * W];
                try
                {
                    // the blast: a few cells around a centre (DamageWorker_Flame.ExplosionAffectCell -> TryStartFireIn, victim -> TryAttachFire)
                    int cx = r.Next(W), cy = r.Next(W), rad = 1 + r.Next(3);
                    for (int x = Math.Max(0, cx - rad); x < Math.Min(W, cx + rad + 1); x++)
                        for (int y = Math.Max(0, cy - rad); y < Math.Min(W, cy + rad + 1); y++)
                        {
                            int i = x * W + y;
                            if (Ask(i, false)) burning[i] = flashed[i] = true;
                            if (pawn[i] && Ask(i, false)) onFire[i] = pawnFlashed[i] = true;
                        }
                    for (int step = 0; step < 30; step++)
                    {
                        Steps++;
                        for (int i = 0; i < W * W; i++)
                        {
                            if (!burning[i] || r.Next(3) != 0) continue;
                            int x = i / W, y = i % W, d = r.Next(4);
                            int nx = x + (d == 0 ? 1 : d == 1 ? -1 : 0), ny = y + (d == 2 ? 1 : d == 3 ? -1 : 0);
                            if (nx < 0 || ny < 0 || nx >= W || ny >= W) continue;
                            int j = nx * W + ny;
                            if (Ask(j, true)) burning[j] = true;               // Fire.TrySpread, instigator carried
                            if (pawn[j] && burning[j] && Ask(j, true)) { if (!onFire[j]) pawnFlashed[j] = false; onFire[j] = true; }   // Fire.cs:272 attach to a pawn in the cell
                        }
                    }
                    for (int i = 0; i < W * W; i++)
                    {
                        if (burning[i] && !Ruled(i, !flashed[i])) Check(false, $"a cell with no air burned on the seabed (cell {i}, {(flashed[i] ? "blast" : "spread")})");
                        if (onFire[i] && !Ruled(i, !pawnFlashed[i])) Check(false, $"a pawn with no air around it caught fire on the seabed (cell {i})");
                    }
                    for (int i = 0; i < W * W; i++)
                    {
                        if (vanilla) Check(Ask(i, false) && Ask(i, true), "fire was refused off the seabed or with the ban switched off");
                        if (src.selfOx) Check(Ask(i, false), "Fuselight's own flash was refused (it carries its oxidizer)");
                        if (seabed && banOn) Check(Ask(i, true) == air[i], "on the banned seabed a fire's spread did not follow the pumped air exactly (it inherited its source's oxidizer)");
                        if (seabed && banOn && !src.selfOx) Check(Ask(i, false) == air[i], "on the banned seabed a non-oxidizer source's fire did not follow the pumped air exactly");
                    }
                }
                catch (Exception e) { fails.Add($"ignition seed {seed}: {e.Message} ({who})"); }
            }
            // named rows: the reported incidents, asked directly
            Cases++; Steps++;
            foreach (var src in FireSources)
            {
                bool noAir = RM_ChillFireBanKernel.IgnitionAllowed(true, true, src.selfOx, src.burnsNothing, false, false);
                bool expect = src.name.StartsWith("RM_Fuselight");
                if (noAir != expect) fails.Add($"ignition units: {src.name} on the banned seabed with no air: fire {noAir}, ruling says {expect}");
                if (RM_ChillFireBanKernel.IgnitionAllowed(true, true, src.selfOx, src.burnsNothing, true, false)) fails.Add($"ignition units: {src.name}'s fire spread on the banned seabed with no air (CHILLFIREBAN_FIX_FUSELIGHT_FIRE_SPREADS: a Tarspool beside a Fuselight lit the floor)");
                if (!RM_ChillFireBanKernel.IgnitionAllowed(true, true, src.selfOx, src.burnsNothing, true, true)) fails.Add($"ignition units: {src.name} refused in a pumped-air cell");
                if (!RM_ChillFireBanKernel.IgnitionAllowed(false, true, src.selfOx, src.burnsNothing, true, false)) fails.Add($"ignition units: {src.name} refused on a surface map");
            }
            // CHILLFIREBAN_FIX_DETONATION_INSTIGATOR_SWAP: CompExplosive.Detonate (CompExplosive.cs:252) names the explosion
            // `(stored == null || hostile) ? parent : stored`, stored = whoever damaged it. Played through the kernel's drop,
            // the explosion's oxidizer must be the exploding thing's own on the banned seabed, whoever set it off.
            var explosives = new (string name, bool selfOx)[] { ("RM_Fuselight", true), ("chemfuel stack / shell", false) };
            var setters = new (string name, bool selfOx, bool hostile)[] { ("nobody", false, false), ("cutting pawn", false, false), ("hostile raider", false, true), ("a Fuselight flash", true, false) };
            foreach (var ex in explosives)
                foreach (var by in setters)
                    foreach (bool seabed in new[] { true, false })
                        foreach (bool banOn in new[] { true, false })
                        {
                            Cases++;
                            bool stored = by.name != "nobody";
                            if (stored && RM_ChillFireBanKernel.DropDetonationInstigator(seabed, banOn, ex.selfOx, by.selfOx)) stored = false;
                            bool namedOx = (!stored || by.hostile) ? ex.selfOx : by.selfOx;   // the engine's choice
                            bool fire = RM_ChillFireBanKernel.IgnitionAllowed(seabed, banOn, namedOx, false, false, false);
                            bool ruled = !seabed || !banOn || ex.selfOx;
                            if (fire != ruled) fails.Add($"detonation units: {ex.name} set off by {by.name} (seabed {seabed}, ban {banOn}): fire {fire}, ruling says {ruled}");
                            if ((!seabed || !banOn) && stored != (by.name != "nobody")) fails.Add($"detonation units: {ex.name} lost its instigator off the banned seabed (kill credit must stay vanilla)");
                        }
            // CHILLFIREBAN_FIX_MODDED_DIRECT_FIRE_SPAWN: the creation-path table. Every way a Fire comes to exist, from the
            // wave-62 enumeration of decompiled 1.6 (only FireUtility.cs:85 and :115 make a Fire; every caller below reaches
            // one of them) and the IL scan of the owner's 320 active mods (the Bypass rows make and spawn a Fire themselves).
            // `inFire`: asked inside a burning Fire's scope (its tick, its Spark, its burning pawn's death), as the patches
            // mark it. Played through the doors the patches build: a gated row spawns iff the gate admits it and is then
            // never put out; a bypass row always spawns and lives iff PutOutUngatedFire spares it. The ruling's oracle: on
            // the banned airless seabed only a Fuselight flash burns; with pumped air, off the seabed or with the ban off,
            // every path burns as vanilla.
            var paths = new (string path, char door, bool selfOx, bool burnsNothing, bool inFire, bool flash)[]
            {
                ("DamageWorker_Flame.ExplosionAffectCell (explosion instigator)", 'S', false, false, false, false),
                ("DamageWorker_Flame cell, RM_Fuselight flash (Detonate names the Fuselight)", 'S', true, false, false, true),
                ("DamageWorker_Flame victim attach, RM_Fuselight flash", 'A', true, false, false, true),
                ("DamageWorker_Vaporize cell (explosion instigator)", 'S', false, false, false, false),
                ("Explosion.cs:335 cell fire (explosion instigator)", 'S', false, false, false, false),
                ("Genetron meltdown flame cell (RM_NonCombustionExtension)", 'S', false, true, false, false),
                ("Bullet incendiary (launcher)", 'S', false, false, false, false),
                ("FlameThrower cell + attach (caster)", 'S', false, false, false, false),
                ("FireArrow / Verb_Ignite / PowerBeam / Bombardment (caster or null)", 'S', false, false, false, false),
                ("Verb_ShootBeam attach (caster)", 'A', false, false, false, false),
                ("Thing.TakeDamage:1554 attach, pawn's Flame hit (dinfo.Instigator)", 'A', false, false, false, false),
                ("Thing.TakeDamage:1554 attach, Fuselight fire's own damage (instigator ?? this, in tick)", 'A', true, false, true, false),
                ("Fire.TrySpread:403 (Fuselight instigator carried, in tick)", 'S', true, false, true, false),
                ("Fire.cs:272 attach to pawn in cell (in tick)", 'A', true, false, true, false),
                ("Spark.Impact, launcher a Fuselight's Fire (Patch_Spark_Impact)", 'S', true, false, true, false),
                ("Pawn.Kill:2208 corpse fire (Patch_Pawn_Kill_CorpseFire)", 'S', true, false, true, false),
                ("SteadyEnvironmentEffects lightning / ShortCircuitUtility (null)", 'S', false, false, false, false),
                ("HediffGiver_Terrain lava attach (null)", 'A', false, false, false, false),
                ("VEF FlamethrowProjectile.DoDamage (no instigator set)", 'B', false, false, false, false),
                ("VEF TeslaProjectile.Impact addFire (no instigator set)", 'B', false, false, false, false),
                ("modded spawn, Fuselight instigator, from inside a Fire's tick", 'B', true, false, true, false),
                ("modded spawn, Fuselight instigator, its own flash", 'B', true, false, false, true),
            };
            foreach (var p in paths)
                foreach (bool seabed in new[] { true, false })
                    foreach (bool banOn in new[] { true, false })
                        foreach (bool air in new[] { false, true })
                        {
                            Cases++;
                            bool allowed = RM_ChillFireBanKernel.IgnitionAllowed(seabed, banOn, p.selfOx, p.burnsNothing, p.inFire, air);
                            bool spawned = p.door == 'B' || allowed;
                            bool admitted = p.door != 'B' && allowed;
                            bool burns = spawned && !RM_ChillFireBanKernel.PutOutUngatedFire(seabed, banOn, admitted, false, p.selfOx, p.inFire, air);
                            bool ruled = !seabed || !banOn || air || p.flash;
                            if (burns != ruled) fails.Add($"fire paths: {p.path} [{p.door}] seabed {seabed} ban {banOn} air {air}: burns {burns}, ruling says {ruled}");
                            // a Fire already admitted or loaded from a save is never put out, whatever the cell
                            if (RM_ChillFireBanKernel.PutOutUngatedFire(seabed, banOn, true, false, p.selfOx, p.inFire, air)) fails.Add($"fire paths: {p.path}: an admitted Fire was put out");
                            if (RM_ChillFireBanKernel.PutOutUngatedFire(seabed, banOn, false, true, p.selfOx, p.inFire, air)) fails.Add($"fire paths: {p.path}: a Fire loaded from a save was put out");
                        }
            return fails;
        }

        // A printed seed must replay the very case that failed: case k of a batch from base B equals the single case at seed B+k.
        private static bool ReplayReproduces()
        {
            var fns = new (string name, Func<int, int, List<string>> run)[] { ("oxygen", Oxygen), ("trample", Trample), ("fireban", FireBan), ("ignition", Ignition) };
            bool good = true;
            foreach (var f in fns)
            {
                RngTrace = new List<int>(); f.run(6, 100); var batch = RngTrace;
                for (int k = 0; k < batch.Count; k++)
                {
                    RngTrace = new List<int>(); f.run(1, 100 + k);
                    if (RngTrace.Count != 1 || RngTrace[0] != batch[k]) { Console.WriteLine($"FAIL replay: {f.name} --fuzz-seed {100 + k} does not reproduce batch case {k}"); good = false; }
                }
            }
            RngTrace = null;
            return good;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("garden", () => Garden(N(4000), S(1))),
                ("elder", () => Elder(N(4000), S(1))),
                ("units", () => Units(N(2000), S(1))),
                ("oxygen", () => Oxygen(N(3000), S(1))),
                ("trample", () => Trample(N(3000), S(1))),
                ("fireban", () => FireBan(N(3000), S(1))),
                ("ignition", () => Ignition(N(2000), S(1))),
            };
            if (only == null && !ReplayReproduces()) ok = false;
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            Console.WriteLine($"diving fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
