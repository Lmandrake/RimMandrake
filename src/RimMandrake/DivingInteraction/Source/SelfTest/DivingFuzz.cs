// Approach B for DivingInteraction: seeded random ACTION SEQUENCES over the two Verse-free kernels the mod calls,
//   RM_GardenDefenseKernel (Chill garden offense scoring, tiers, cooldowns) and
//   RM_ElderEconomyKernel   (Brine Elder novelty ledger, unique-treasure claims, silver payout).
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
                    bool wantT2 = scoreIn >= RM_GardenDefenseKernel.Tier2Threshold * (1f - RM_GardenDefenseKernel.TrailThresholdDiscount * d) && w.now >= before.tier2CooldownUntilTick;
                    bool wantT1 = !wantT2 && scoreIn >= RM_GardenDefenseKernel.Tier1Threshold * (1f - RM_GardenDefenseKernel.TrailThresholdDiscount * d) && w.now >= before.tier1CooldownUntilTick;
                    var o = RM_GardenDefenseKernel.Offense(ref w.s, kind, w.now, d);
                    Check((o == RM_GardenDefenseKernel.Outcome.Tier2Wake) == wantT2, $"tier-2 wake {(o == RM_GardenDefenseKernel.Outcome.Tier2Wake ? "fired" : "did not fire")} but score {scoreIn} at t={w.now} (cd2 {before.tier2CooldownUntilTick}, density {d}) says it should {(wantT2 ? "" : "not ")}");
                    Check((o == RM_GardenDefenseKernel.Outcome.Tier1Arc) == wantT1, $"tier-1 arc {(o == RM_GardenDefenseKernel.Outcome.Tier1Arc ? "fired" : "did not fire")} but score {scoreIn} at t={w.now} (cd1 {before.tier1CooldownUntilTick}, density {d}) says it should {(wantT1 ? "" : "not ")}");
                    if (o == RM_GardenDefenseKernel.Outcome.None)
                        Check(w.s.offenseScore == scoreIn, "a non-firing offense changed the score by other than its weight");
                    else
                    {
                        Check(w.s.offenseScore == 0f, "a firing offense left score " + w.s.offenseScore);
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
                    r.agitationScore = float.Parse(w.s.agitationScore.ToString("R", CultureInfo.InvariantCulture), CultureInfo.InvariantCulture);
                    Check(r.offenseScore == w.s.offenseScore && r.agitationScore == w.s.agitationScore, "score did not survive a text round trip");
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
            return fails;
        }

        // ════════════════ oxygen (DESIGN_PASS DI-2): the pumped-air ledger never lets one pump cancel another ════════════════
        private static List<string> Oxygen(int n, int seed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                Cases++;
                var r = new Random(seed * 7919 + k);
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
                catch (Exception e) { fails.Add($"oxygen seed {k}: {e.Message}"); }
            }
            Cases++; Steps++;
            if (!RM_OxygenLedgerKernel.RoomServed(true, 60, 1, 60) || RM_OxygenLedgerKernel.RoomServed(true, 61, 1, 60) || !RM_OxygenLedgerKernel.RoomServed(true, 120, 2, 60)
                || RM_OxygenLedgerKernel.RoomServed(false, 10, 3, 60) || RM_OxygenLedgerKernel.RoomServed(true, 10, 0, 60) || !RM_OxygenLedgerKernel.RoomServed(true, 99999, 1, 0)
                || RM_OxygenLedgerKernel.RoomServed(true, 0, 1, 60) || !RM_OxygenLedgerKernel.RoomServed(true, int.MaxValue, 2, int.MaxValue))
                fails.Add("oxygen units: RoomServed boundaries (capacity pooled, unsealed/no pump/empty never served, 0 = no limit, no overflow)");
            return fails;
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
            };
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
