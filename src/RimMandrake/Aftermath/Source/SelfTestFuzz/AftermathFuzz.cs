// Approach B for Aftermath: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_AftermathKernel.cs) and the production
// BattleOutcomeClassifier:
//   classify  the four-way outcome over every (total, dead, exited, casualty) up to 12 raiders against an ordered-rule spec
//   battle    raid scripts (walk-in, drop-pod, flee, die, downed) polled every 250 ticks: the fallback close never fires while a raider is still
//             on the map or still to arrive, closes within a poll of the truth, and the exited count matches the truth at the close
//   prison    prisoner clocks over 1..3 maps polled every 5000 ticks: a clock runs unbroken while a prisoner is held on ANY map, restarts only
//             after a real absence, fires at the first poll past the threshold; plus a negative control that polling map by map (the original
//             runner) never lets a clock mature
//   queue     the one-per-faction / two-total discipline over a timed queue
//   units     eligibility, windows and tick conversions
// A failing case is printed as `family seed N: message | detail`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Aftermath.SelfTestFuzz
{
    internal static class AftermathFuzz
    {
        public static long Cases, Steps, PodRaids, Closed, MidFlightPolls, Fired, Restarts, Refusals;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private static List<string> Loop(string name, int n, int seed, Action<Random> one)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                Cases++;
                try { one(new Random(seed + i)); } catch (Exception e) { fails.Add($"{name} seed {seed + i}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            return fails;
        }

        // ════════════════════════ classify ════════════════════════
        private static BattleOutcome SpecClassify(int total, int dead, int exited, bool casualty)
        {
            if (total <= 0) return BattleOutcome.Stalemate;
            if (dead * 10 >= total * 6) return BattleOutcome.Repelled;       // integer form of >= 60%
            if (casualty) return BattleOutcome.Lost;
            if (exited > 0) return BattleOutcome.Routed;
            return BattleOutcome.Stalemate;
        }

        private static List<string> Classify()
        {
            var fails = new List<string>();
            var seen = new HashSet<BattleOutcome>();
            try
            {
                for (int total = -1; total <= 12; total++)
                    for (int dead = 0; dead <= Math.Max(total, 0); dead++)
                        for (int exited = 0; exited <= Math.Max(total, 0) - dead; exited++)
                            foreach (bool cas in new[] { false, true })
                            {
                                Cases++; Steps++;
                                var got = BattleOutcomeClassifier.Classify(total, dead, exited, cas);
                                var want = SpecClassify(total, dead, exited, cas);
                                // 60% boundary: 3/5, 6/10, 9/15 are exactly on the line (float division must not tip them under)
                                Check(got == want, $"Classify(total {total}, dead {dead}, exited {exited}, casualty {cas}) = {got}, spec {want}");
                                seen.Add(got);
                            }
                Check(seen.Count == 4, "only " + seen.Count + " of the 4 outcomes are reachable");
                Check(BattleOutcomeClassifier.Classify(5, 3, 0, true) == BattleOutcome.Repelled, "3 of 5 (exactly 60%) with a casualty must be Repelled, not Lost");
                Check(BattleOutcomeClassifier.Classify(10, 6, 0, false) == BattleOutcome.Repelled, "6 of 10 is exactly 60%");
                Check(BattleOutcomeClassifier.Classify(15, 9, 0, false) == BattleOutcome.Repelled, "9 of 15 is exactly 60%");
                Check(BattleOutcomeClassifier.Classify(20, 12, 0, false) == BattleOutcome.Repelled, "12 of 20 is exactly 60%");
                for (int total = 1; total <= 200; total++)
                    for (int dead = 0; dead <= total; dead++)
                    {
                        Cases++;
                        var got = BattleOutcomeClassifier.Classify(total, dead, 0, false);
                        Check((got == BattleOutcome.Repelled) == (dead * 10 >= total * 6), $"Classify({total}, {dead}) boundary: {got}");
                    }
            }
            catch (Exception e) { fails.Add("classify seed 0: " + e.Message); }
            return fails;
        }

        // ════════════════════════ battle ════════════════════════
        private sealed class Raider
        {
            public int arriveAt;           // tick it first stands on the map (pods land late)
            public int leaveAt = -1;       // tick it walks off (-1 never)
            public int downAt = -1;        // tick it dies or is downed (-1 never)
            public bool dies;              // dead raiders leave the map as a corpse (not spawned); a downed one lies there, still spawned
            public bool Spawned(int t) { return t >= arriveAt && (leaveAt < 0 || t < leaveAt) && !(dies && downAt >= 0 && t >= downAt); }
            public bool Down(int t) { return downAt >= 0 && t >= downAt; }
            public bool EverArrived(int t) { return t >= arriveAt; }
        }

        private static List<string> Battle(int n, int seed)
        {
            return Loop("battle", n, seed, r =>
            {
                int count = r.Next(1, 9);
                bool pods = r.Next(2) == 0;
                int opened = r.Next(0, 100000);
                var raiders = new List<Raider>();
                for (int i = 0; i < count; i++)
                {
                    var rd = new Raider { arriveAt = opened + (pods ? r.Next(60, 900) : r.Next(0, 3)) };
                    int fate = r.Next(4);
                    if (fate == 0) rd.leaveAt = rd.arriveAt + r.Next(30, 4000);
                    else if (fate == 1) { rd.downAt = rd.arriveAt + r.Next(30, 4000); rd.dies = r.Next(2) == 0; }
                    else if (fate == 2) { rd.leaveAt = rd.arriveAt + r.Next(30, 800); }
                    else { rd.leaveAt = rd.arriveAt + r.Next(30, 4000); }
                    raiders.Add(rd);
                }
                if (pods) PodRaids++;
                var seenSpawned = new bool[count];
                int firstPoll = (opened / RM_AftermathKernel.FallbackPollIntervalTicks + 1) * RM_AftermathKernel.FallbackPollIntervalTicks;
                int closedAt = -1;
                var obsAtClose = new List<RM_RaiderObs>();
                for (int t = firstPoll; t < opened + 20000; t += RM_AftermathKernel.FallbackPollIntervalTicks)
                {
                    Steps++;
                    var obs = new List<RM_RaiderObs>();
                    for (int i = 0; i < count; i++)
                    {
                        if (raiders[i].Spawned(t)) seenSpawned[i] = true;
                        obs.Add(new RM_RaiderObs(raiders[i].Down(t), raiders[i].Spawned(t), seenSpawned[i]));
                    }
                    bool grace = RM_AftermathKernel.GraceExpired(opened, t);
                    bool close = RM_AftermathKernel.AllAccountedFor(obs, grace);
                    // truth: nobody is alive on the map and everyone alive has arrived (or the grace is over)
                    bool anyOnMap = raiders.Any(x => x.Spawned(t) && !x.Down(t));      // a downed raider lying there is accounted for
                    bool anyToArrive = raiders.Any(x => !x.EverArrived(t) && !x.Down(t));
                    if (anyOnMap) Check(!close, $"closed at tick {t} (opened {opened}) with a raider still on the map");
                    if (anyToArrive && !grace) { Check(!close, $"closed at tick {t} (opened {opened}) with a raider still to arrive (pods {pods}), before the grace"); MidFlightPolls++; }
                    if (close)
                    {
                        closedAt = t; obsAtClose = obs; Closed++;
                        // the exited count equals the number of raiders that arrived, are alive and standing, and are gone
                        int want = raiders.Count(x => !x.Down(t) && !x.Spawned(t) && x.EverArrived(t));
                        int got = RM_AftermathKernel.CountSurvivedAndExited(obs, grace);
                        if (!anyToArrive) Check(got <= want, $"exited count {got} exceeds the truth {want}");
                        if (seenSpawned.All(x => x) || raiders.All(x => x.Down(t) || x.EverArrived(t) && !x.Spawned(t) && seenSpawned[raiders.IndexOf(x)])) Check(got == raiders.Count(x => !x.Down(t) && !x.Spawned(t)), $"exited count {got} differs from the survivors who left ({raiders.Count(x => !x.Down(t) && !x.Spawned(t))})");
                        Check(RM_AftermathKernel.CountDeadOrDowned(obs) == raiders.Count(x => x.Down(t)), "dead/downed count differs from the truth");
                        break;
                    }
                }
                // liveness: if the truth settles (everyone resolved) well before the end, the close happens within one poll plus the grace
                int settle = raiders.Max(x => x.downAt >= 0 ? x.downAt : (x.leaveAt >= 0 ? x.leaveAt : int.MaxValue));
                if (settle != int.MaxValue)
                {
                    int bound = Math.Max(settle, opened + RM_AftermathKernel.ArrivalGraceTicks) + 2 * RM_AftermathKernel.FallbackPollIntervalTicks;
                    Check(closedAt >= 0 && closedAt <= bound, $"battle settled at {settle} (opened {opened}) but closed at {closedAt}, bound {bound}");
                }
            });
        }

        // ════════════════════════ prison ════════════════════════
        private static List<string> Prison(int n, int seed)
        {
            return Loop("prison", n, seed, r =>
            {
                int maps = r.Next(1, 4), people = r.Next(1, 6), polls = 60;
                const int step = RM_AftermathKernel.HousekeepingIntervalTicks;
                // presence[p][poll] = map index or -1
                var presence = new int[people, polls];
                for (int p = 0; p < people; p++)
                {
                    int map = r.Next(maps);
                    bool held = r.Next(3) != 0;
                    for (int k = 0; k < polls; k++)
                    {
                        if (r.Next(12) == 0) held = !held;
                        if (held && r.Next(15) == 0) map = r.Next(maps);          // moved between maps: still held
                        presence[p, k] = held ? map : -1;
                    }
                }
                var clock = new RM_PrisonerClock();
                var start = new int[people]; for (int p = 0; p < people; p++) start[p] = -1;
                var firedSpec = new bool[people];
                int now0 = r.Next(0, 100000);
                for (int k = 0; k < polls; k++)
                {
                    Steps++;
                    int now = now0 + k * step;
                    var all = new HashSet<int>();
                    for (int p = 0; p < people; p++) if (presence[p, k] >= 0) all.Add(p);
                    clock.Poll(now, all);
                    for (int p = 0; p < people; p++)
                    {
                        bool here = presence[p, k] >= 0;
                        if (!here) { if (start[p] >= 0) Restarts++; start[p] = -1; firedSpec[p] = false; continue; }
                        if (start[p] < 0) start[p] = now;
                        float want = (now - start[p]) / (float)RM_AftermathKernel.TicksPerDay;
                        Check(Math.Abs(clock.HeldDays(p, now) - want) < 1e-4f, $"prisoner {p} held {clock.HeldDays(p, now)} days at poll {k}, the truth is {want} (clock restarted while held)");
                        Check(clock.HasFired(p) == firedSpec[p], $"prisoner {p} fired flag {clock.HasFired(p)}, truth {firedSpec[p]} at poll {k}");
                        if (!firedSpec[p] && want >= 3f) { clock.MarkFired(p); firedSpec[p] = true; Fired++; }
                    }
                    for (int p = 0; p < people; p++) if (presence[p, k] < 0) Check(clock.HeldDays(p, now) == 0f && !clock.HasFired(p), $"absent prisoner {p} still tracked");
                    Check(clock.Tracked == all.Count, $"tracking {clock.Tracked} prisoners, {all.Count} are held");
                }
            });
        }

        private static List<string> PrisonNegative()
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                // two maps, one prisoner on each, held for 6 days: polled map by map (the original runner) neither clock ever reaches 3 days
                var old = new RM_PrisonerClock(); var fixedClock = new RM_PrisonerClock();
                bool oldMatured = false, fixedMatured = false;
                for (int k = 0; k < 6 * 12; k++)
                {
                    int now = k * RM_AftermathKernel.HousekeepingIntervalTicks;
                    old.Poll(now, new HashSet<int> { 1 }); old.Poll(now, new HashSet<int> { 2 });
                    fixedClock.Poll(now, new HashSet<int> { 1, 2 });
                    oldMatured |= old.HeldDays(1, now) >= 3f || old.HeldDays(2, now) >= 3f;
                    fixedMatured |= fixedClock.HeldDays(1, now) >= 3f && fixedClock.HeldDays(2, now) >= 3f;
                }
                Check(!oldMatured, "negative control broke: per-map polling matured a clock (the control no longer shows the original defect)");
                Check(fixedMatured, "polling the union never matured both clocks in 6 days");
            }
            catch (Exception e) { fails.Add("prison seed 0: " + e.Message); }
            return fails;
        }

        // ════════════════════════ queue ════════════════════════
        private static List<string> Queue(int n, int seed)
        {
            return Loop("queue", n, seed, r =>
            {
                int maxPer = r.Next(1, 4), maxTotal = r.Next(1, 6), factions = r.Next(1, 5);
                var q = new List<(int faction, int fire)>();
                int now = r.Next(0, 1000);
                for (int i = 0; i < 80; i++)
                {
                    Steps++;
                    now += r.Next(0, 4) == 0 ? r.Next(0, 30000) : r.Next(0, 800);
                    q.RemoveAll(e => now >= e.fire);                                                    // housekeeping
                    int f = r.Next(factions);
                    int liveF = q.Count(e => e.fire > now && e.faction == f), liveT = q.Count(e => e.fire > now);
                    bool ok = RM_AftermathKernel.PassesDiscipline(liveF, liveT, maxPer, maxTotal);
                    Check(ok == (liveF < maxPer && liveT < maxTotal), $"PassesDiscipline({liveF},{liveT},{maxPer},{maxTotal}) = {ok}");
                    if (ok) q.Add((f, now + r.Next(1, 90000))); else Refusals++;
                    Check(q.Count(e => e.fire > now) <= maxTotal, "more than the total cap is live");
                    for (int ff = 0; ff < factions; ff++) Check(q.Count(e => e.fire > now && e.faction == ff) <= maxPer, "more than the per-faction cap is live");
                }
            });
        }

        // ════════════════════════ units ════════════════════════
        private static List<string> Units()
        {
            var fails = new List<string>();
            Action<string, Action> t = (name, a) => { Cases++; Steps++; try { a(); } catch (Exception e) { fails.Add("units seed 0: " + name + ": " + e.Message); } };
            t("outcome eligibility table", () =>
            {
                for (int m = 0; m < 8; m++)
                    foreach (int surv in new[] { 0, 2, 3, 4 })
                    {
                        bool kind = (m & 1) != 0, listed = (m & 2) != 0;
                        Check(RM_AftermathKernel.OutcomeEligible(kind, listed, surv, 3) == (kind && listed && surv >= 3), $"OutcomeEligible({kind},{listed},{surv},3)");
                    }
            });
            t("held eligibility", () =>
            {
                Check(RM_AftermathKernel.HeldEligible(true, 3f, 3f) && !RM_AftermathKernel.HeldEligible(true, 2.99f, 3f) && !RM_AftermathKernel.HeldEligible(false, 9f, 3f), "HeldEligible");
            });
            t("mental break window edges", () =>
            {
                int w = RM_AftermathKernel.WindowTicks(2f);
                Check(w == 120000, "2 days is 120000 ticks");
                Check(RM_AftermathKernel.InMentalBreakWindow(0, w) && RM_AftermathKernel.InMentalBreakWindow(w, w) && !RM_AftermathKernel.InMentalBreakWindow(w + 1, w) && !RM_AftermathKernel.InMentalBreakWindow(-1, w), "window edges are inclusive at 0 and the window, exclusive outside");
            });
            t("grace edge", () =>
            {
                Check(!RM_AftermathKernel.GraceExpired(100, 100 + RM_AftermathKernel.ArrivalGraceTicks - 1) && RM_AftermathKernel.GraceExpired(100, 100 + RM_AftermathKernel.ArrivalGraceTicks), "grace expires exactly ArrivalGraceTicks after opening");
            });
            t("delay ticks", () => { Check(RM_AftermathKernel.DelayTicks(0.5f) == 30000 && RM_AftermathKernel.DelayTicks(0f) == 0, "DelayTicks"); });
            t("a pod raid polled mid-flight does not close as Routed", () =>
            {
                var inPods = new List<RM_RaiderObs> { new RM_RaiderObs(false, false, false), new RM_RaiderObs(false, false, false) };
                Check(!RM_AftermathKernel.AllAccountedFor(inPods, false), "closed with every raider still in its pod");
                Check(RM_AftermathKernel.CountSurvivedAndExited(inPods, false) == 0, "raiders in pods counted as exited");
                Check(RM_AftermathKernel.AllAccountedFor(inPods, true), "the grace never releases a raid whose raiders never arrived");
            });
            t("a standing raider is not exited, a downed one on the map is accounted for", () =>
            {
                var standing = new List<RM_RaiderObs> { new RM_RaiderObs(false, true, true) };
                Check(RM_AftermathKernel.CountSurvivedAndExited(standing, true) == 0, "a raider still on the map counted as exited");
                var downed = new List<RM_RaiderObs> { new RM_RaiderObs(true, true, true) };
                Check(RM_AftermathKernel.AllAccountedFor(downed, false), "a downed raider lying on the map blocks the close");
                Check(RM_AftermathKernel.CountDeadOrDowned(downed) == 1 && RM_AftermathKernel.CountSurvivedAndExited(downed, true) == 0, "a downed raider counted wrongly");
            });
            t("empty raid and null-free lists", () => { Check(RM_AftermathKernel.AllAccountedFor(new List<RM_RaiderObs>(), false) && RM_AftermathKernel.CountSurvivedAndExited(new List<RM_RaiderObs>(), true) == 0, "empty list"); });
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
                ("classify", () => Classify()),
                ("battle", () => Battle(N(8000), S(1))),
                ("prison", () => Prison(N(3000), S(1)).Concat(PrisonNegative()).ToList()),
                ("queue", () => Queue(N(3000), S(1))),
                ("units", () => Units()),
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
            if (only == null && !oneSeed.HasValue && scale >= 1)
            {
                Console.WriteLine($"reached: pod raids {PodRaids}, closes {Closed}, polls with a raider still to arrive {MidFlightPolls}, fired rules {Fired}, clock restarts {Restarts}, refusals {Refusals}");
                if (PodRaids == 0 || Closed == 0 || MidFlightPolls == 0 || Fired == 0 || Restarts == 0 || Refusals == 0) { Console.WriteLine("FAIL fuzz never reached pod raid / close / mid-flight poll / fired rule / clock restart / refusal (blind)"); ok = false; }
            }
            Console.WriteLine($"aftermath fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
