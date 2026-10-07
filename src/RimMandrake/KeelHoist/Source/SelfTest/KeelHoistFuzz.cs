// Approach B for KeelHoist: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_HoistKernel.cs):
//   transit  hoist action sequences (begin / tick / arrive-all / refusals to land / holder acceptance / silver coming back up)
//            through the production schedule + tick loop + arrival plan, against an independent per-thing ledger
//   chute    the chance-chute lifecycle: stakes, one clock, the roll, the payout and crate composition, the house edge
//   market   pit pricing, fighter test, silver stacking, cycle time
//   gates    every decision table exhaustively against an independent restatement, plus the cross-table safety properties
//            (no free colonist is ever sold, captured pawns are never the player's, ...)
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.KeelHoist.SelfTest
{
    internal static class KeelHoistFuzz
    {
        public static long Cases, Steps, Landed, Deferred, IntoHolders, Below, SilverBack, Rolls, Jackpots, Busts;
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

        // ════════════════════════ transit ════════════════════════
        private enum A { Begin, Tick, TickBig, ArriveAll, Reload, Mode }
        private struct Act
        {
            public A kind; public int a, b; public bool f;
            public override string ToString() { return kind + "(" + a + "," + b + (f ? ",T" : "") + ")"; }
        }

        private sealed class Thing { public int id; public float mass; public bool pawn, colonist, downed, silver; }
        private struct Pending { public int id; public int due; public bool up; public string from; }

        private static readonly float[] Masses = { 0f, 6.25f, 12.5f, 25f, 50f, 75f, 100f };
        private static readonly float[] Mults = { 0.25f, 0.5f, 1f, 2f, 4f };

        // deterministic per (thing, tick) world outcomes shared by kernel driver and spec
        private static bool DropOk(int id, int now, int mode) { return mode == 0 || ((id * 2654435761u + (uint)(now / 625) * 40503u) >> 7) % 3 != 0; }
        private static bool HolderAccepts(int id) { return (id * 40503u >> 3) % 4 != 0; }

        private sealed class HoistModel : IHoistTransitSink
        {
            public List<Thing> owner = new List<Thing>();
            public RM_TransitSchedule sched = new RM_TransitSchedule();
            public List<string> manifest = new List<string>();
            public int now; public float mult = 1f; public int mode; public bool handlesBelow, holderSpawned; public int nextId = 1;
            public List<int> arrivedThisTick = new List<int>(), deferredThisTick = new List<int>();
            public long landed, deferred, intoHolder, below, silverBack;

            public int TransitCount { get { return owner.Count; } }

            public void BeginTransit(Thing t, bool up, string from)
            {
                owner.Add(t);
                sched.Add(now + RM_HoistKernel.CycleTicks(t.mass * 1f, mult), up, from);
            }

            public void ArriveAt(int i)
            {
                Thing t = owner[i];
                bool up = sched.Up(i); string from = sched.From(i);
                bool holderPath = RM_HoistKernel.GoesIntoHolder(up, holderSpawned, t.pawn, t.colonist, t.downed);
                ArrivalPlan plan = RM_HoistKernel.PlanArrival(up, handlesBelow, holderPath);
                if (plan == ArrivalPlan.HandledBelow)
                {
                    owner.RemoveAt(i); sched.RemoveAt(i);
                    manifest.Add("below:" + t.id); RM_HoistKernel.CapList(manifest, RM_HoistKernel.ManifestCap);
                    arrivedThisTick.Add(t.id); below++;
                    return;
                }
                bool inHolder = plan == ArrivalPlan.IntoHolder;
                if (inHolder)
                {
                    owner.RemoveAt(i);
                    if (!HolderAccepts(t.id)) inHolder = false;          // placed near the holder instead
                    else
                    {
                        intoHolder++;
                        // a sale: the silver comes back up the cable (appended while the tick loop is running)
                        foreach (int n in RM_HoistKernel.SilverStacks(100 + t.id % 7 * 1000, 500))
                        {
                            BeginTransit(new Thing { id = nextId++, mass = n / 500f * 10f, silver = true }, true, "pit");
                            silverBack++;
                        }
                    }
                }
                else if (!DropOk(t.id, now, mode))
                {
                    sched.Defer(i, now + RM_HoistKernel.BaseCycleTicks);
                    deferredThisTick.Add(t.id); deferred++;
                    return;
                }
                else owner.RemoveAt(i);
                sched.RemoveAt(i);
                manifest.Add((up ? "up:" : "down:") + t.id + (inHolder ? ":holder" : ""));
                RM_HoistKernel.CapList(manifest, RM_HoistKernel.ManifestCap);
                arrivedThisTick.Add(t.id); landed++;
            }
        }

        private static Act[] GenActs(Random r, int len)
        {
            var a = new Act[len];
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(100);
                A kind = k < 38 ? A.Begin : k < 78 ? A.Tick : k < 86 ? A.TickBig : k < 90 ? A.ArriveAll : k < 94 ? A.Reload : A.Mode;
                a[i] = new Act { kind = kind, a = r.Next(1 << 12), b = r.Next(1 << 12), f = r.Next(2) == 0 };
            }
            return a;
        }

        private static string RunTransit(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x1b873593);
            var h = new HoistModel { now = 10000, handlesBelow = rr.Next(4) == 0, holderSpawned = rr.Next(2) == 0, mult = Mults[rr.Next(Mults.Length)], mode = rr.Next(2) };
            var spec = new List<Pending>();                      // the independent ledger
            var byId = new Dictionary<int, Thing>();
            int specManifest = 0; int totalBegun = 0, specArrived = 0;
            int stepNo = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch (a.kind)
                    {
                        case A.Begin:
                            {
                                var t = new Thing { id = h.nextId++, mass = Masses[a.a % Masses.Length], pawn = (a.a & 8) != 0, colonist = (a.a & 16) != 0, downed = (a.a & 32) != 0 };
                                bool up = a.f;
                                h.BeginTransit(t, up, "src" + (a.b % 3));
                                byId[t.id] = t;
                                double cyc = 625.0 * h.mult * (1.0 + t.mass / 50.0);
                                spec.Add(new Pending { id = t.id, due = h.now + Math.Max(60, (int)Math.Round(cyc)), up = up, from = "src" + (a.b % 3) });
                                totalBegun++;
                                break;
                            }
                        case A.Mode:
                            h.handlesBelow = a.f; h.holderSpawned = (a.a & 1) != 0; h.mult = Mults[a.b % Mults.Length];
                            break;
                        case A.Reload:
                            // a save/load round trip: the saved lists may be missing or shorter than the owner (older saves); they are padded back
                            // (an entry that lost its schedule arrives at once, going down, from "?")
                            {
                                int cut = a.f ? a.a % 4 : 0;
                                int keep = Math.Max(0, h.sched.Count - cut);
                                if (a.b % 5 == 0 && a.f) keep = 0;
                                h.sched.arriveAt.RemoveRange(keep, h.sched.arriveAt.Count - keep);
                                h.sched.goingUp.RemoveRange(keep, h.sched.goingUp.Count - keep);
                                h.sched.fromLabel.RemoveRange(keep, h.sched.fromLabel.Count - keep);
                                if (a.b % 7 == 0) { h.sched.goingUp = null; h.sched.fromLabel = null; h.sched.arriveAt = new List<int>(h.sched.arriveAt); }
                                int padded = 0;
                                h.sched.PadTo(h.owner.Count);
                                for (int i = 0; i < h.owner.Count; i++)
                                {
                                    int ix = spec.FindIndex(p => p.id == h.owner[i].id);
                                    bool lostEntry = i >= keep || (a.b % 7 == 0);
                                    if (lostEntry && a.b % 7 == 0 && i < keep)
                                    {   // goingUp / fromLabel lists were missing entirely: direction false, origin "?", time kept
                                        Pending p = spec[ix]; p.up = false; p.from = "?"; spec[ix] = p; padded++;
                                    }
                                    else if (i >= keep)
                                    {   // the whole entry was missing
                                        Pending p = spec[ix]; p.due = 0; p.up = false; p.from = "?"; spec[ix] = p; padded++;
                                    }
                                }
                                Check(h.sched.Count == h.owner.Count && h.sched.goingUp.Count == h.owner.Count && h.sched.fromLabel.Count == h.owner.Count, "PadTo left the lists out of step");
                                break;
                            }
                        case A.Tick:
                        case A.TickBig:
                            h.now += a.kind == A.Tick ? 1 + a.a % 700 : 700 + a.a * 3;
                            RunTick(h, spec, byId, ref specManifest, ref specArrived, count);
                            break;
                        case A.ArriveAll:
                            {
                                h.arrivedThisTick.Clear(); h.deferredThisTick.Clear();
                                int nBefore = h.owner.Count;
                                var idsBefore = h.owner.Select(t => t.id).ToList();
                                h.sched.ArriveAllNow(h);
                                // everything that was in transit either arrived, or could not land and was deferred; nothing else changed
                                var settled = new HashSet<int>(h.arrivedThisTick.Concat(h.deferredThisTick));
                                foreach (int id in idsBefore) Check(settled.Contains(id), $"ArriveAllNow left {id} untouched");
                                Check(h.arrivedThisTick.Count == h.arrivedThisTick.Distinct().Count(), "a thing arrived twice");
                                // mirror in the spec: arrived ones leave the ledger, deferred ones are due at now+625
                                foreach (int id in h.arrivedThisTick.ToList()) { int ix = spec.FindIndex(p => p.id == id); if (ix >= 0) { spec.RemoveAt(ix); specManifest++; specArrived++; } }
                                foreach (int id in h.deferredThisTick) { int ix = spec.FindIndex(p => p.id == id); Pending p = spec[ix]; p.due = h.now + 625; spec[ix] = p; }
                                // silver appended while it ran is in the owner but not yet in the spec: adopt it
                                AdoptNew(h, spec, byId);
                                break;
                            }
                    }
                    Compare(h, spec, specManifest);
                }
                // conservation: begun things (plus the silver the pit sent back) = still riding + landed + into holders + below
                long accounted = h.owner.Count + h.landed + h.below;   // landed already includes the ones lowered into the holder
                Check(accounted == h.nextId - 1, $"conservation: {h.nextId - 1} things begun but {accounted} accounted for (riding {h.owner.Count}, landed {h.landed} of which {h.intoHolder} into the holder, below {h.below})");
                if (count) { Landed += h.landed; Deferred += h.deferred; IntoHolders += h.intoHolder; Below += h.below; SilverBack += h.silverBack; }
            }
            catch (Exception e) { return $"step {stepNo}: {e.Message}"; }
            return null;
        }

        private static void AdoptNew(HoistModel h, List<Pending> spec, Dictionary<int, Thing> byId)
        {
            // things appended during an arrival (silver coming up) enter the spec with the same independent cycle formula
            var known = new HashSet<int>(spec.Select(p => p.id));
            for (int i = 0; i < h.owner.Count; i++)
            {
                Thing t = h.owner[i];
                if (known.Contains(t.id)) continue;
                byId[t.id] = t;
                double cyc = 625.0 * h.mult * (1.0 + t.mass / 50.0);
                spec.Add(new Pending { id = t.id, due = h.sched.arriveAt[i], up = h.sched.Up(i), from = h.sched.From(i) });
                Check(h.sched.arriveAt[i] == h.now + Math.Max(60, (int)Math.Round(cyc)), $"silver {t.id} scheduled at {h.sched.arriveAt[i]}, want {h.now + Math.Max(60, (int)Math.Round(cyc))}");
            }
        }

        private static void RunTick(HoistModel h, List<Pending> spec, Dictionary<int, Thing> byId, ref int specManifest, ref int specArrived, bool count)
        {
            h.arrivedThisTick.Clear(); h.deferredThisTick.Clear();
            var due = spec.Where(p => p.due <= h.now).Select(p => p.id).OrderBy(x => x).ToList();   // snapshot: things added during the tick do not land in it
            h.sched.Tick(h, h.now);
            var settled = h.arrivedThisTick.Concat(h.deferredThisTick).OrderBy(x => x).ToList();
            Check(settled.SequenceEqual(due), $"tick {h.now}: settled [{string.Join(",", settled)}] but spec says due [{string.Join(",", due)}]");
            Check(h.arrivedThisTick.Count == h.arrivedThisTick.Distinct().Count(), "a thing arrived twice in one tick");
            foreach (int id in h.arrivedThisTick) { int ix = spec.FindIndex(p => p.id == id); Check(ix >= 0, $"{id} arrived but was never begun"); Check(spec[ix].due <= h.now, $"{id} landed before its time"); spec.RemoveAt(ix); specManifest++; specArrived++; }
            foreach (int id in h.deferredThisTick)
            {
                Check(!DropOk(id, h.now, h.mode), $"{id} deferred although it could land");
                int ix = spec.FindIndex(p => p.id == id); Pending p = spec[ix]; p.due = h.now + 625; spec[ix] = p;
            }
            AdoptNew(h, spec, byId);
        }

        private static void Compare(HoistModel h, List<Pending> spec, int specManifest)
        {
            Check(h.sched.Count == h.owner.Count && h.sched.goingUp.Count == h.owner.Count && h.sched.fromLabel.Count == h.owner.Count, $"schedule out of step with the owner ({h.sched.arriveAt.Count}/{h.sched.goingUp.Count}/{h.sched.fromLabel.Count} vs {h.owner.Count})");
            Check(spec.Count == h.owner.Count, $"ledger holds {spec.Count} but the cable holds {h.owner.Count}");
            for (int i = 0; i < h.owner.Count; i++)
            {
                int ix = spec.FindIndex(p => p.id == h.owner[i].id);
                Check(ix >= 0, $"{h.owner[i].id} rides the cable but is not in the ledger");
                Check(spec[ix].due == h.sched.arriveAt[i] && spec[ix].up == h.sched.Up(i) && spec[ix].from == h.sched.From(i), $"{h.owner[i].id}: schedule entry differs from the ledger");
            }
            Check(h.manifest.Count == Math.Min(specManifest, RM_HoistKernel.ManifestCap), $"manifest holds {h.manifest.Count}, want {Math.Min(specManifest, RM_HoistKernel.ManifestCap)}");
            Check(h.sched.Soonest() == (spec.Count == 0 ? 0 : spec.Min(p => p.due)), "Soonest() differs from the ledger minimum");
        }

        private static List<string> Transit(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed);
                var acts = GenActs(r, 30 + r.Next(170)); Cases++;
                if (RunTransit(acts, seed, true) == null) continue;
                var small = Shrink(acts.ToList(), t => RunTransit(t, seed, false) != null);
                fails.Add($"transit seed {seed}: {RunTransit(small, seed, false)} | {string.Join(" ", small)}");
                if (fails.Count >= 3) break;
            }
            return fails;
        }

        // ════════════════════════ chute ════════════════════════
        private static List<string> Chute(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed); Cases++;
                try
                {
                    float cut = 0.02f + (float)r.NextDouble() * 0.48f, jp = (float)r.NextDouble() * 0.3f, bust = (float)r.NextDouble() * 0.5f;
                    int chuteTicks = (1 + r.Next(24)) * 2500;
                    int now = r.Next(100000);
                    float stake = 0f; int rollAt = -1, stakes = r.Next(1, 8), firstRoll = -1; int rolls = 0;
                    for (int s = 0; s < stakes; s++)
                    {
                        float v = (float)(r.NextDouble() * 3000);
                        stake += v;
                        int before = rollAt;
                        rollAt = RM_HoistKernel.NextRollAt(rollAt, now, chuteTicks);
                        if (before < 0) { Check(rollAt == now + chuteTicks, "first stake did not start the clock"); firstRoll = rollAt; }
                        else Check(rollAt == before, "a later stake moved the clock");
                        now += r.Next(0, chuteTicks / 2);
                        Steps++;
                    }
                    Check(rollAt == firstRoll, "the clock drifted");
                    Check(!RM_HoistKernel.RollDue(rollAt, rollAt - 1) && RM_HoistKernel.RollDue(rollAt, rollAt) && RM_HoistKernel.RollDue(rollAt, rollAt + 1), "RollDue boundary");
                    Check(!RM_HoistKernel.RollDue(-1, 1000000), "no stake, no roll");
                    // bands: forced r values at and around the cut points
                    int middleDraws = 0;
                    Func<float> mid = () => { middleDraws++; return 0.9f; };
                    Check(RM_HoistKernel.RollMultiplier(Math.Max(0f, jp - 1e-6f), jp, bust, mid) == (jp > 1e-6f ? 3f : 0.9f) || jp <= 1e-6f, "just under the jackpot edge");
                    if (jp > 0f) Check(RM_HoistKernel.RollMultiplier(0f, jp, bust, mid) == 3f, "r=0 must be the jackpot when jackpot chance > 0");
                    Check(RM_HoistKernel.RollMultiplier(jp, jp, bust, mid) == (bust > 0f ? 0.3f : 0.9f), "r exactly at the jackpot edge starts the bust band");
                    middleDraws = 0;
                    float top = RM_HoistKernel.RollMultiplier(Math.Min(0.999999f, jp + bust), jp, bust, mid);
                    Check(top == 0.9f && middleDraws == 1 || jp + bust >= 0.999999f, "r at the bust edge is the middle band");
                    // the middle band is drawn only when needed (RNG stream stays the original's)
                    middleDraws = 0; RM_HoistKernel.RollMultiplier(0f, jp, bust, mid);
                    if (jp > 0f) Check(middleDraws == 0, "the middle draw was made for a jackpot");
                    // payout and the house edge
                    foreach (float m in new[] { 3f, 0.3f, 0.7f, 1.1f })
                    {
                        float p = RM_HoistKernel.Payout(stake, cut, m);
                        Check(Math.Abs(p - stake * (1 - cut) * m) <= 1e-3f * Math.Max(1f, stake), "payout formula");
                        Check(p <= stake * m + 1e-3f, "the house cut paid out extra");
                    }
                    // expected return of the shipped odds is below the stake; for any settings the closed form matches a sampled mean
                    double ev = RM_HoistKernel.ExpectedMultiplier(jp, bust) * (1.0 - cut);
                    double sum = 0; var rnd = new Random(seed * 7 + 1); int N = 4000;
                    for (int k = 0; k < N; k++) sum += RM_HoistKernel.Payout(1000f, cut, RM_HoistKernel.RollMultiplier((float)rnd.NextDouble(), jp, bust, () => 0.7f + (float)rnd.NextDouble() * 0.4f)) / 1000.0;
                    double midP = Math.Max(0.0, 1.0 - jp - bust), m1 = RM_HoistKernel.ExpectedMultiplier(jp, bust), m2 = jp * 9.0 + bust * 0.09 + midP * 0.8233;
                    double tol = 5.0 * Math.Sqrt(Math.Max(0.0, m2 - m1 * m1)) * (1.0 - cut) / Math.Sqrt(N) + 0.003;   // five sigma of the sample mean
                    Check(Math.Abs(sum / N - ev) < tol, $"sampled return {sum / N:F3} vs closed form {ev:F3} +-{tol:F3} (cut {cut:F2} jp {jp:F2} bust {bust:F2})");
                    // crate composition
                    float value = (float)(r.NextDouble() * (r.Next(3) == 0 ? 100 : 5000));
                    if (RM_HoistKernel.CrateIsEmpty(value)) { Check(value < 1f, "empty crate above 1"); }
                    else
                    {
                        float got = RM_HoistKernel.CrateNeedsItemSet(value) ? value * (0.9f + (float)r.NextDouble() * 0.1f) : 0f;
                        int silver = RM_HoistKernel.CrateSilver(value, got);
                        Check(silver >= 0, $"negative silver {silver}");
                        Check(got + silver <= value + 1e-3f && got + silver > value - 1.001f - 1e-3f, $"crate worth {got + silver} for value {value}");
                        var stacks = RM_HoistKernel.SilverStacks(silver, 500);
                        Check(stacks.Sum() == silver && stacks.All(x => x > 0 && x <= 500), "silver stacks");
                        if (value < 150f) Check(got == 0f, "an item set below the threshold");
                    }
                    Check(RM_HoistKernel.CrateNeedsItemSet(150f) && !RM_HoistKernel.CrateNeedsItemSet(149.99f) && RM_HoistKernel.CrateIsEmpty(0.99f) && !RM_HoistKernel.CrateIsEmpty(1f), "crate thresholds");
                    // ring of rolls
                    var ring = new List<int>(); for (int k = 0; k < 80; k++) { ring.Add(k); RM_HoistKernel.CapList(ring, RM_HoistKernel.RollsCap); }
                    Check(ring.Count == 50 && ring[0] == 30 && ring[49] == 79, "roll ring");
                    rolls++;
                    Rolls++;
                }
                catch (Exception e) { fails.Add($"chute seed {seed}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            // the shipped odds, measured: the house wins on average (86% back), and every cut point is exercised
            try
            {
                double ev = RM_HoistKernel.ExpectedMultiplier(0.08, 0.1) * (1.0 - 0.15);
                Check(ev < 1.0 && Math.Abs(ev - 0.857) < 0.01, $"shipped odds return {ev:F3}, the settings text says about 86%");
                var rnd = new Random(12345); int N = 200000; int jack = 0, bu = 0; double sum = 0;
                for (int k = 0; k < N; k++)
                {
                    float m = RM_HoistKernel.RollMultiplier((float)rnd.NextDouble(), 0.08f, 0.1f, () => 0.7f + (float)rnd.NextDouble() * 0.4f);
                    sum += RM_HoistKernel.Payout(1000f, 0.15f, m); jack += m == 3f ? 1 : 0; bu += m == 0.3f ? 1 : 0;
                }
                Jackpots += jack; Busts += bu;
                Check(Math.Abs(jack / (double)N - 0.08) < 0.005 && Math.Abs(bu / (double)N - 0.10) < 0.005, $"band frequencies {jack / (double)N:F3} / {bu / (double)N:F3} vs 0.08 / 0.10");
                Check(sum / N < 1000 && Math.Abs(sum / N - ev * 1000) < 10, $"mean payout of a 1000 stake {sum / N:F0}");
                Steps += N; Cases++;
            }
            catch (Exception e) { fails.Add("chute shipped odds: " + e.Message); }
            return fails;
        }

        // ════════════════════════ market ════════════════════════
        private static List<string> Market(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed); Cases++; Steps++;
                try
                {
                    float mv = (float)(r.NextDouble() * 3000), pm = 0.1f + (float)r.NextDouble() * 1.9f, bonus = 1f + (float)r.NextDouble() * 2f;
                    bool fighter = r.Next(2) == 0, arena = r.Next(2) == 0;
                    int price = RM_HoistKernel.Price(mv, pm, fighter, arena, bonus);
                    Check(price >= 1, "price below 1");
                    double want = mv * (double)pm * (fighter && arena ? bonus : 1.0);
                    Check(Math.Abs(price - Math.Max(1.0, want)) <= 1.0 + 1e-3 * want, $"price {price} vs {want:F2}");
                    Check(RM_HoistKernel.Price(mv, pm, false, false, bonus) <= RM_HoistKernel.Price(mv, pm, true, true, bonus) || bonus < 1f, "the fighter bonus lowered the price");
                    Check(RM_HoistKernel.Price(mv, pm, fighter, !arena, bonus) == RM_HoistKernel.Price(mv, pm, fighter, !arena, bonus), "price not deterministic");
                    if (!(fighter && arena)) Check(RM_HoistKernel.Price(mv, pm, fighter, arena, 1f) == RM_HoistKernel.Price(mv, pm, fighter, arena, bonus), "the bonus applied without a fighter and an arena week");
                    float mv2 = mv + (float)(r.NextDouble() * 500);
                    Check(RM_HoistKernel.Price(mv2, pm, fighter, arena, bonus) >= price, "price fell as value rose");
                    // fighters
                    int lvl = r.Next(-1, 21); float cp = (float)(r.NextDouble() * 300);
                    Check(RM_HoistKernel.IsFighter(true, lvl, cp) == (lvl >= 8) && RM_HoistKernel.IsFighter(false, lvl, cp) == (cp >= 100f), "IsFighter");
                    Check(RM_HoistKernel.IsFighter(true, -1, 999f) == false, "an unskilled human with a big combat power is a fighter");
                    // weeks
                    int t = r.Next(0, 100000000);
                    Check(RM_HoistKernel.WeekOf(t) == t / 420000 && RM_HoistKernel.WeekOf(t) == RM_HoistKernel.WeekOf(t - t % 420000) && RM_HoistKernel.WeekOf(t + 1) >= RM_HoistKernel.WeekOf(t), "WeekOf");
                    // silver
                    int amount = r.Next(0, 4) == 0 ? r.Next(0, 5) : r.Next(0, 200000), lim = r.Next(1, 3) == 1 ? 500 : r.Next(1, 800);
                    var stacks = RM_HoistKernel.SilverStacks(amount, lim);
                    Check(stacks.Sum() == amount, $"silver stacks sum {stacks.Sum()} != {amount}");
                    Check(stacks.All(x => x >= 1 && x <= lim), "a stack outside 1..limit");
                    Check(stacks.Count == (amount + lim - 1) / lim, "stack count not minimal");
                    // cycle time
                    float mass = Masses[r.Next(Masses.Length)]; float mult = Mults[r.Next(Mults.Length)];
                    int c = RM_HoistKernel.CycleTicks(mass, mult);
                    Check(c >= 60, "cycle under the floor");
                    Check(Math.Abs(c - Math.Max(60.0, 625.0 * mult * (1.0 + mass / 50.0))) < 1.0 + 1e-6, $"cycle {c} vs closed form");
                    Check(RM_HoistKernel.CycleTicks(mass + 12.5f, mult) >= c && RM_HoistKernel.CycleTicks(mass, mult * 2f) >= c, "cycle not monotone in mass / multiplier");
                    Check(RM_HoistKernel.CycleTicks(0f, 1f) == 625 && RM_HoistKernel.CycleTicks(50f, 1f) == 1250 && RM_HoistKernel.CycleTicks(0f, 0.25f) == 156 && RM_HoistKernel.CycleTicks(0f, 4f) == 2500, "ruled cycle anchors");
                    Check(RM_HoistKernel.CycleTicks(0f, 0.01f) == 60, "floor not applied");
                    Check(RM_HoistKernel.RestraintTicks(24f) == 60000 && RM_HoistKernel.RestraintTicks(1f) == 2500, "restraint ticks");
                    // Open Line
                    float lv = (float)(r.NextDouble() * 20);
                    Check(RM_HoistKernel.OpenLineNext(lv, true) == lv + 1f && RM_HoistKernel.OpenLineNext(lv, false) == Math.Max(0f, lv - 0.5f) && RM_HoistKernel.OpenLineNext(0.2f, false) == 0f, "Open Line step");
                    int tick = r.Next(0, 10000000);
                    Check(RM_HoistKernel.OpenLineStepsNow(true, tick, true) == (tick % 2500 == 137) && !RM_HoistKernel.OpenLineStepsNow(false, tick - tick % 2500 + 137, true) && !RM_HoistKernel.OpenLineStepsNow(true, tick - tick % 2500 + 137, false), "Open Line cadence / gates");
                    // reach
                    float range = 4f + (float)r.NextDouble() * 36f, size = r.Next(1, 4), d = (float)(r.NextDouble() * 50);
                    Check(RM_HoistKernel.PortalInReach(range + size, range, size) && !RM_HoistKernel.PortalInReach(range + size + 0.01f, range, size) && RM_HoistKernel.CellInReach(range, range) && !RM_HoistKernel.CellInReach(range + 0.01f, range), "reach edges are inclusive");
                    Check(RM_HoistKernel.PortalInReach(d, range, size) == (d <= range + size), "portal reach");
                }
                catch (Exception e) { fails.Add($"market seed {seed}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            return fails;
        }

        // ════════════════════════ gates ════════════════════════
        private static bool Bit(int m, int i) { return (m >> i & 1) != 0; }

        private static List<string> Gates()
        {
            var fails = new List<string>();
            try
            {
                // EnterRefusal: master, then cable, then power
                for (int m = 0; m < 8; m++)
                {
                    string got = RM_HoistKernel.EnterRefusal(Bit(m, 0), Bit(m, 1), Bit(m, 2));
                    string want = !Bit(m, 0) ? "off" : !Bit(m, 1) ? "cable" : !Bit(m, 2) ? "power" : null;
                    Check(got == want, $"EnterRefusal({m}) = {got}");
                    Cases++; Steps++;
                }
                // HoldsRiderInTransit / PlanArrival / GoesIntoHolder
                for (int m = 0; m < 8; m++)
                {
                    bool may = Bit(m, 0), col = Bit(m, 1), down = Bit(m, 2);
                    Check(RM_HoistKernel.HoldsRiderInTransit(may, col, down) == (may || !col || down), "HoldsRiderInTransit");
                    Cases++; Steps++;
                }
                for (int m = 0; m < 32; m++)
                {
                    bool up = Bit(m, 0), spawned = Bit(m, 1), pawn = Bit(m, 2), col = Bit(m, 3), down = Bit(m, 4);
                    bool g = RM_HoistKernel.GoesIntoHolder(up, spawned, pawn, col, down);
                    Check(g == (!up && spawned && pawn && (!col || down)), "GoesIntoHolder");
                    if (g) Check(!(col && !down), "an awake colonist was lowered into a holder");
                    foreach (bool below in new[] { false, true })
                    {
                        ArrivalPlan p = RM_HoistKernel.PlanArrival(up, below, g);
                        Check(p == (!up && below ? ArrivalPlan.HandledBelow : g ? ArrivalPlan.IntoHolder : ArrivalPlan.Drop), "PlanArrival");
                        if (up) Check(p != ArrivalPlan.HandledBelow, "a thing coming UP was kept by the chute");
                    }
                    Cases++; Steps++;
                }
                // CaptureFor (2^8)
                for (int m = 0; m < 256; m++)
                {
                    bool on = Bit(m, 0), dead = Bit(m, 1), player = Bit(m, 2), human = Bit(m, 3), ps = Bit(m, 4), guest = Bit(m, 5), animal = Bit(m, 6), free = Bit(m, 7);
                    CaptureKind k = RM_HoistKernel.CaptureFor(on, dead, player, human, ps, guest, animal, free);
                    CaptureKind want = !on || dead || player ? CaptureKind.None
                        : human ? (ps || !guest ? CaptureKind.None : CaptureKind.Prisoner)
                        : (animal && free ? CaptureKind.Bound : CaptureKind.None);
                    Check(k == want, $"CaptureFor({m}) = {k}, want {want}");
                    if (player) Check(k == CaptureKind.None, "the player's own pawn was captured");
                    if (!on) Check(k == CaptureKind.None, "captures happened with the setting off");
                    if (k == CaptureKind.Bound) Check(!human && animal && free, "a non-wild-animal was bound");
                    Cases++; Steps++;
                }
                // CradleTakesPawn (2^5)
                for (int m = 0; m < 32; m++)
                {
                    bool ours = Bit(m, 0), may = Bit(m, 1), down = Bit(m, 2), col = Bit(m, 3), cap = Bit(m, 4);
                    bool g = RM_HoistKernel.CradleTakesPawn(ours, may, down, col, cap);
                    Check(g == ((ours && (may || down || !col)) || (down && cap)), "CradleTakesPawn");
                    if (!ours && !down) Check(!g, "the cradle lifted an awake stranger");
                    Cases++; Steps++;
                }
                // IsLowerableCaptive (2^11)
                for (int m = 0; m < 2048; m++)
                {
                    bool dead = Bit(m, 0), down = Bit(m, 1), player = Bit(m, 2), ps = Bit(m, 3), caravan = Bit(m, 4), quest = Bit(m, 5), human = Bit(m, 6), guest = Bit(m, 7), join = Bit(m, 8), animal = Bit(m, 9), free = Bit(m, 10);
                    bool g = RM_HoistKernel.IsLowerableCaptive(dead, down, player, ps, caravan, quest, human, guest, join, animal, free);
                    bool want = !(dead || !down || player || ps) && !( !caravan || quest) && (human ? guest && !join : animal && free);
                    Check(g == want, $"IsLowerableCaptive({m})");
                    if (g) Check(down && !dead && !player && !ps && caravan && !quest, "a lowerable captive that is up, dead, ours or a quest pawn");
                    Cases++; Steps++;
                }
                // DialogHidesPawn (2^6) + the safety property: a buyer pit / chute never lists a free colonist
                for (int m = 0; m < 64; m++)
                {
                    bool may = Bit(m, 0), holder = Bit(m, 1), buyer = Bit(m, 2), col = Bit(m, 3), down = Bit(m, 4), slave = Bit(m, 5);
                    bool hide = RM_HoistKernel.DialogHidesPawn(may, holder, buyer, col, down, slave);
                    Check(hide == (((!may || holder) && col && !down) || (buyer && col && !slave)), "DialogHidesPawn");
                    if (buyer && col && !slave) Check(hide, "a free colonist is listed for a buyer pit or chute");
                    if (!may && col && !down) Check(hide, "an awake colonist is listed with riding off");
                    if (!col) Check(!hide, "a non-colonist was hidden");
                    Cases++; Steps++;
                }
                // HolderRefusal / GateOpen / KeepersBuying + the same safety property at the holder itself
                for (int m = 0; m < 64; m++)
                {
                    bool buyer = Bit(m, 0), col = Bit(m, 1), slave = Bit(m, 2), hostile = Bit(m, 3), other = Bit(m, 4), open = Bit(m, 5);
                    string ref_ = RM_HoistKernel.HolderRefusal(buyer, col, slave, hostile, other, open);
                    string want = !buyer ? null : col && !slave ? "own" : other && hostile && !open ? "enemy" : null;
                    Check(ref_ == want, $"HolderRefusal({m}) = {ref_}, want {want}");
                    if (buyer && col && !slave) Check(ref_ != null, "a buyer holder accepted a free colonist");
                    Cases++; Steps++;
                }
                for (int m = 0; m < 8; m++)
                {
                    bool g = RM_HoistKernel.GateOpen(Bit(m, 0), Bit(m, 1), Bit(m, 2));
                    Check(g == (Bit(m, 0) || Bit(m, 1) || !Bit(m, 2)), "GateOpen");
                    if (Bit(m, 2) && !Bit(m, 0) && !Bit(m, 1)) Check(!g, "the gate opened while keepers stand");
                    Cases++; Steps++;
                }
                for (int m = 0; m < 32; m++)
                {
                    bool kb = RM_HoistKernel.KeepersBuying(Bit(m, 0), Bit(m, 1), Bit(m, 2), Bit(m, 3), Bit(m, 4));
                    Check(kb == (Bit(m, 0) && Bit(m, 1) && Bit(m, 2) && !Bit(m, 3) && !Bit(m, 4)), "KeepersBuying");
                    if (Bit(m, 4)) Check(!kb, "a pit bought while its gate was open");
                    if (Bit(m, 3)) Check(!kb, "a hostile pit bought");
                    Cases++; Steps++;
                }
                // tether lock: refuses only an accepted launch, with a map, a known def and a hoist on the substructure
                for (int m = 0; m < 32; m++)
                {
                    bool b = RM_HoistKernel.TetherBlocksLaunch(Bit(m, 0), Bit(m, 1), Bit(m, 2), Bit(m, 3), Bit(m, 4));
                    Check(b == (Bit(m, 0) && Bit(m, 1) && Bit(m, 2) && Bit(m, 3) && Bit(m, 4)), "TetherBlocksLaunch");
                    if (!Bit(m, 1)) Check(!b, "the tether lock blocked with the setting off");
                    Cases++; Steps++;
                }
                // hourly Open Line walk: 10 open hours then 30 closed
                float lv = 0f; for (int k = 0; k < 10; k++) lv = RM_HoistKernel.OpenLineNext(lv, true);
                Check(lv == 10f, "10 open hours");
                for (int k = 0; k < 30; k++) lv = RM_HoistKernel.OpenLineNext(lv, false);
                Check(lv == 0f, "30 closed hours");
            }
            catch (Exception e) { fails.Add("gates: " + e.Message); }
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
                ("transit", () => Transit(N(6000), S(1))),
                ("chute", () => Chute(N(1500), S(1))),
                ("market", () => Market(N(5000), S(1))),
                ("gates", () => Gates()),
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
            if (only == null || only == "transit")
            {
                Console.WriteLine($"transit reached: landed {Landed}, deferred {Deferred}, into holders {IntoHolders}, kept below {Below}, silver back up {SilverBack}");
                if (!oneSeed.HasValue && scale >= 1 && (Landed == 0 || Deferred == 0 || IntoHolders == 0 || Below == 0 || SilverBack == 0)) { Console.WriteLine("FAIL transit fuzz never reached a path (blind)"); ok = false; }
            }
            Console.WriteLine($"keelhoist fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
