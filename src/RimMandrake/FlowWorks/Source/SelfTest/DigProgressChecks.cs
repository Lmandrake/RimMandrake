// Live bug (save NS_Pyrelands_play_q_col_d3dig, 2026-11-07): a colonist on RM_DigCanalJob stood on one square for over 10
// game hours, food 0.38 -> 0.05 and thirst 0.6 -> 0.0, the square still undug. Vanilla AffectFloor's work toil never
// re-reads the think tree and keeps its work in a private per-job field, so a 12,800-work cut (3200 x 4) held a weak miner
// for 16-31 hours and any interruption threw the work away. The fix (RM_JobDriver_ShovelFloor + RM_MapComponent_DigProgress):
// the job re-reads the think tree every RM_DigProgressMath.OverrideCheckTicks, and unfinished work is parked per square.
// Here: the PRODUCTION Verse-free arithmetic (RM_DigProgressMath) with a can-fail per clause, then the Verse-bound wiring read
// from the production source.
// NOT proven here (live rows owed): a hungry digger really leaves for food at the next check and comes back to the same
// progress bar; a forced dig restarts on its square without a jump in the bar; an old save loaded mid-dig carries on.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class DigProgressChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static void Has(string src, string pattern, string what) => RiverSwitchFlipChecks.Has(src, pattern, what);

        /// <summary>The store as the map component keeps it (RM_DigProgress.cs Take/Put), on a plain dictionary.</summary>
        private sealed class Store
        {
            private readonly Dictionary<int, (float work, int depth)> parked = new Dictionary<int, (float, int)>();

            public float Take(int cell, bool fill, int depthNow)
            {
                int key = RM_DigProgressMath.Key(cell, fill);
                bool has = parked.TryGetValue(key, out var v);
                parked.Remove(key);
                return RM_DigProgressMath.Resume(has, v.work, v.depth, depthNow);
            }

            public void Put(int cell, bool fill, float work, int depthNow)
            {
                parked[RM_DigProgressMath.Key(cell, fill)] = (work, depthNow);
            }

            public int Count => parked.Count;
        }

        /// <summary>Ticks a job needs to finish <paramref name="total"/> work at <paramref name="speed"/>, the job being cut
        /// short every <paramref name="chunk"/> ticks (0: never) and parked or (vanilla) thrown away.</summary>
        private static int TicksToFinish(float total, float speed, int chunk, bool persist, int giveUpAfter, out int jobs)
        {
            var store = new Store();
            jobs = 0;
            int ticks = 0;
            while (ticks < giveUpAfter)
            {
                jobs++;
                float done = persist ? store.Take(7, false, 0) : 0f;
                for (int t = 0; chunk == 0 || t < chunk; t++)
                {
                    done = RM_DigProgressMath.AfterTicks(done, speed, 1);
                    ticks++;
                    if (RM_DigProgressMath.Finished(done, total))
                    {
                        return ticks;
                    }
                    if (ticks >= giveUpAfter)
                    {
                        return -1;
                    }
                }
                if (persist && RM_DigProgressMath.Keep(done, false, true))
                {
                    store.Put(7, false, done, 0);
                }
            }
            return -1;
        }

        public static void Run(Action<string, Action> Case)
        {
            const float Notch = RM_DigDepthMath.WorkPerNotch * RM_DigDepthMath.DefaultLabourMultiplier; // 12,800, the live cut

            Case("DigProgress: interrupted work sums to the uninterrupted run, no tick double-counted or skipped", () =>
            {
                foreach (float speed in new[] { 0.1f, 0.19f, 0.6f, 1f, 1.7f })
                {
                    int whole = TicksToFinish(Notch, speed, 0, true, 2_000_000, out int j0);
                    Assert(whole > 0 && j0 == 1, "an uninterrupted cut at speed " + speed + " finishes in one job");
                    foreach (int chunk in new[] { 1, 37, RM_DigProgressMath.OverrideCheckTicks, 2500 })
                    {
                        int parts = TicksToFinish(Notch, speed, chunk, true, 2_000_000, out int jobs);
                        Assert(parts == whole, "speed " + speed + ", cut every " + chunk + " ticks: " + parts + " ticks vs " + whole + " uninterrupted");
                        Assert(jobs == (whole + chunk - 1) / chunk, "speed " + speed + ", chunk " + chunk + ": " + jobs + " jobs");
                    }
                }
                // can-fail: vanilla's per-job countdown (no store) never lands a cut that is longer than the gap between
                // interruptions, which is the live bug with the interruption it lacked added back
                int lost = TicksToFinish(Notch, 0.15f, RM_DigProgressMath.OverrideCheckTicks, false, 500_000, out _);
                Assert(lost == -1, "without the store a 12,800 cut at speed 0.15 cut short every 2000 ticks never lands");
            });

            Case("DigProgress: the think tree is re-read well inside one notch, and the live cut really took hours", () =>
            {
                Assert(RM_DigProgressMath.OverrideCheckTicks > 0, "an expiry is set");
                Assert(RM_DigProgressMath.OverrideCheckTicks < RM_DigDepthMath.TicksPerHour, "re-read under an hour");
                float notchTicksAtOne = Notch / RM_DigDepthMath.WorkPerTickAtSpeedOne;
                Assert(RM_DigProgressMath.OverrideCheckTicks < notchTicksAtOne / 3f,
                    "at least three re-reads in one notch at speed 1 (" + notchTicksAtOne + " ticks)");
                float hoursAt010 = Notch / (RM_DigDepthMath.WorkPerTickAtSpeedOne * 0.1f * RM_DigDepthMath.TicksPerHour);
                float hoursAt019 = Notch / (RM_DigDepthMath.WorkPerTickAtSpeedOne * 0.19f * RM_DigDepthMath.TicksPerHour);
                Assert(hoursAt010 > 30f && hoursAt010 < 31f && hoursAt019 > 15f && hoursAt019 < 16.5f,
                    "a 10-19% miner needs 16-31 hours for the first cut (" + hoursAt019 + ".." + hoursAt010 + ")");
                Assert(Math.Abs(RM_DigProgressMath.AfterTicks(0f, 1f, 1) - RM_DigDepthMath.WorkPerTickAtSpeedOne) < 1e-6f,
                    "the work rate is vanilla AffectFloor's 1.7 x speed per tick");
                Assert(Math.Abs(RM_DigProgressMath.AfterTicks(10f, 0.5f, 4) - (10f + 0.5f * 1.7f * 4)) < 1e-4f, "rate x delta");
            });

            Case("DigProgress: parked work is kept only at the depth it was done at, per square and direction", () =>
            {
                var store = new Store();
                store.Put(100, false, 5000f, 2);
                Assert(store.Take(100, true, 2) == 0f, "a dig's work never counts toward a fill of the same square");
                Assert(store.Take(100, false, 2) == 5000f, "a dig resumes its own work at the same depth");
                Assert(store.Count == 0 && store.Take(100, false, 2) == 0f, "taking it removes it (the job holds it now)");
                store.Put(100, false, 5000f, 2);
                Assert(store.Take(100, false, 3) == 0f, "the square was cut (or filled) since: the work is void");
                Assert(store.Count == 0, "and dropped");
                Assert(RM_DigProgressMath.Resume(true, 5000f, 2, 2) == 5000f && RM_DigProgressMath.Resume(false, 5000f, 2, 2) == 0f,
                    "nothing stored, nothing resumed");
                Assert(RM_DigProgressMath.Resume(true, float.NaN, 0, 0) == 0f && RM_DigProgressMath.Resume(true, -3f, 0, 0) == 0f
                       && RM_DigProgressMath.Resume(true, float.PositiveInfinity, 0, 0) == 0f, "a bad record resumes nothing");
                for (int i = 0; i < 400 * 400; i += 397)
                {
                    foreach (bool f in new[] { false, true })
                    {
                        int k = RM_DigProgressMath.Key(i, f);
                        Assert(RM_DigProgressMath.CellOf(k) == i && RM_DigProgressMath.IsFill(k) == f, "key round-trips for cell " + i);
                    }
                    Assert(RM_DigProgressMath.Key(i, false) != RM_DigProgressMath.Key(i, true), "dig and fill keys differ");
                    Assert(RM_DigProgressMath.Key(i + 1, false) != RM_DigProgressMath.Key(i, true), "neighbour keys differ");
                }
            });

            Case("DigProgress: what a job keeps when it ends", () =>
            {
                Assert(RM_DigProgressMath.Keep(4000f, false, true), "unfinished work on a standing order is parked");
                Assert(!RM_DigProgressMath.Keep(4000f, true, true), "landed work is spent, not parked (no second notch from it)");
                Assert(!RM_DigProgressMath.Keep(4000f, false, false), "a cancelled order takes its work with it");
                Assert(!RM_DigProgressMath.Keep(0f, false, true) && !RM_DigProgressMath.Keep(float.NaN, false, true), "no work, nothing kept");
            });

            Case("DigProgress: the bar and the old-save countdown", () =>
            {
                Assert(RM_DigProgressMath.Fraction(6400f, Notch) == 0.5f, "half done reads half");
                Assert(RM_DigProgressMath.Fraction(13000f, Notch) == 1f && RM_DigProgressMath.Fraction(-5f, Notch) == 0f
                       && RM_DigProgressMath.Fraction(5f, 0f) == 0f && RM_DigProgressMath.Fraction(float.NaN, Notch) == 0f, "the bar clamps 0..1");
                Assert(!RM_DigProgressMath.Finished(0f, 0f) && RM_DigProgressMath.Finished(Notch, Notch)
                       && !RM_DigProgressMath.Finished(Notch - 0.01f, Notch), "finished exactly at the total");
                Assert(RM_DigProgressMath.FromWorkLeft(2800f, Notch) == 10000f, "vanilla workLeft 2800 of 12,800 is 10,000 done");
                Assert(RM_DigProgressMath.FromWorkLeft(-1000f, Notch) == 0f, "vanilla's -1000 (work not begun) is nothing");
                Assert(RM_DigProgressMath.FromWorkLeft(0f, Notch) == 0f && RM_DigProgressMath.FromWorkLeft(float.NaN, Notch) == 0f,
                    "an absent or bad countdown is nothing");
                Assert(RM_DigProgressMath.FromWorkLeft(20000f, Notch) == 0f, "a countdown above the total (cheaper now) is nothing done");
                Assert(RM_DigProgressMath.FromWorkLeft(100f, 0f) == 0f, "no total, nothing");
            });

            Case("DigProgress wiring: the shovel driver keeps vanilla's toil and adds the re-read and the parking", () =>
            {
                string s = Src("RM_JobDriver_ShovelFloor.cs");
                Has(s, @"abstract class RM_JobDriver_ShovelFloor : JobDriver_AffectFloor", "derives AffectFloor (reservation, DesDef, BaseWorkAmount, SpeedStat)");
                Assert(!s.Contains("base.MakeNewToils("), "never runs vanilla's work toil (its private countdown loses the work)");
                Has(s, @"job\.expiryInterval = RM_DigProgressMath\.OverrideCheckTicks; job\.checkOverrideOnExpire = true;", "expiry + override check");
                Has(s, @"public override void Notify_Starting\(\) \{ base\.Notify_Starting\(\); EnsureInterruptible\(\); \}", "set at job start");
                Has(s, @"tickIntervalAction = delegate \(int delta\) \{(?:(?!initAction).)*?EnsureInterruptible\(\);", "and every work tick (old saved jobs)");
                Has(s, @"this\.FailOn\(\(\) => !job\.ignoreDesignations && Map\.designationManager\.DesignationAt\(TargetLocA, DesDef\) == null\);", "designation FailOn");
                Has(s, @"yield return Toils_Goto\.GotoCell\(TargetIndex\.A, PathEndMode\.Touch\);", "Goto Touch");
                Has(s, @"doWork\.FailOnCannotTouch\(TargetIndex\.A, PathEndMode\.Touch\);", "FailOnCannotTouch");
                Has(s, @"doWork\.WithProgressBar\(TargetIndex\.A, \(\) => RM_DigProgressMath\.Fraction\(workDone, workTotal\)\);", "progress bar from the kept work");
                Has(s, @"doWork\.defaultCompleteMode = ToilCompleteMode\.Never;", "Never complete mode");
                Has(s, @"doWork\.activeSkill = \(\) => SkillDefOf\.Construction;", "active skill");
                Has(s, @"actor\.skills\?\.Learn\(SkillDefOf\.Construction, 0\.1f \* delta\);", "Construction learning 0.1/tick");
                Has(s, @"stat != null && !stat\.Worker\.IsDisabledFor\(actor\) \? actor\.GetStatValue\(stat\) : 1f; workDone = RM_DigProgressMath\.AfterTicks\(workDone, speed, delta\);", "speed stat, vanilla rate");
                Has(s, @"if \(RM_DigProgressMath\.Finished\(workDone, workTotal\)\) \{ IntVec3 c = TargetLocA; DoEffect\(c\); workLanded = !KeepWorkAfterEffect; Map\.designationManager\.DesignationAt\(c, DesDef\)\?\.Delete\(\); ReadyForNextToil\(\);",
                    "DoEffect, then the designation's deletion, then the next toil");
                Has(s, @"doWork\.initAction = delegate \{ BeginWork\(TakeParked\(\)\); \};", "a new job takes the square's parked work");
                Has(s, @"workTotal = System\.Math\.Max\(1, BaseWorkAmount\);", "the total is fixed at the start, never 0");
                Has(s, @"RM_DigProgressMath\.FromWorkLeft\(old, workTotal\)", "an old save carries on from vanilla's countdown");
                Has(s, @"AddFinishAction\(delegate \(JobCondition cond\) \{ ParkUnfinishedWork\(\); \}\); return ShovelToils\(\);", "parking is a finish action");
                Has(s, @"if \(RM_DigProgressMath\.Keep\(workDone, workLanded, orderStands\)\) \{ map\.GetComponent<RM_MapComponent_DigProgress>\(\)\?\.Put\(c, IsFill, workDone\);", "parks unfinished work on a standing order");
                Has(s, @"Scribe_Values\.Look\(ref workDone, ""rmShovelWorkDone"", 0f\); Scribe_Values\.Look\(ref workTotal, ""rmShovelWorkTotal"", 0f\);", "saved with the job");

                string dig = Src("JobDriver_DigCanal.cs");
                Has(dig, @"class JobDriver_DigCanal : RM_JobDriver_ShovelFloor", "dig rides it");
                Has(dig, @"protected override bool IsFill => false;", "dig keys as dig");
                Has(dig, @"protected override bool KeepWorkAfterEffect => cutRefusedButOwed;", "a refused-but-owed cut keeps its work");
                int fin = dig.IndexOf("AddFinishAction(", StringComparison.Ordinal), bas = dig.IndexOf("return base.MakeNewToils();", StringComparison.Ordinal);
                Assert(fin >= 0 && bas > fin, "the dig's re-designation finish action is added before the base's parking one");
                string fill = Src("JobDriver_FillInCanal.cs");
                Has(fill, @"class JobDriver_FillInCanal : RM_JobDriver_ShovelFloor", "fill rides it");
                Has(fill, @"protected override bool IsFill => true;", "fill keys as fill");
                Has(fill, @"foreach \(Toil t in base\.MakeNewToils\(\)\)", "fill's credit FailOn is laid on the shovel toils");

                // every FlowWorks AffectFloor job goes through the shovel driver
                string root = Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_JobDriver_ShovelFloor.cs"));
                var direct = Directory.EnumerateFiles(root, "*.cs", SearchOption.AllDirectories)
                    .Where(f => !f.Contains(Path.DirectorySeparatorChar + "SelfTest" + Path.DirectorySeparatorChar)
                                && !f.Contains(Path.DirectorySeparatorChar + "obj" + Path.DirectorySeparatorChar))
                    .Where(f => Regex.IsMatch(File.ReadAllText(f), @"class \w+ : JobDriver_AffectFloor\b"))
                    .Select(Path.GetFileName).ToList();
                Assert(direct.Count == 1 && direct[0] == "RM_JobDriver_ShovelFloor.cs",
                    "only the shovel driver derives AffectFloor directly (found: " + string.Join(", ", direct) + ")");
            });

            Case("DigProgress wiring: the store saves, drops cancelled or moved work, and idles free", () =>
            {
                string s = Src("RM_DigProgress.cs");
                Has(s, @"class RM_MapComponent_DigProgress : MapComponent", "a map component");
                Has(s, @"Scribe_Collections\.Look\(ref done, ""rmDigProgressDone"", LookMode\.Value, LookMode\.Value\);", "work saved");
                Has(s, @"Scribe_Collections\.Look\(ref depthAt, ""rmDigProgressDepth"", LookMode\.Value, LookMode\.Value\);", "depth tags saved");
                Has(s, @"if \(done == null\) \{ done = new Dictionary<int, float>\(\); \}", "an old save loads an empty store");
                Has(s, @"if \(done\.Count == 0 \|\| Find\.TickManager\.TicksGame % RM_DigProgressMath\.PruneEveryTicks != 0\) \{ return; \}", "idle tick returns first");
                Has(s, @"dm\.DesignationAt\(c, des\) == null \|\| \(ex\?\.ExcavatedDepthAt\(c\) \?\? 0\) != storedDepth", "drops cancelled orders and moved depths");
                Has(s, @"done\.Remove\(key\); depthAt\.Remove\(key\); return RM_DigProgressMath\.Resume\(has, stored, storedDepth, DepthNow\(c\)\);", "Take removes and resumes by depth");
                Assert(!Regex.IsMatch(s, @"void Prune\(\) \{(?:(?!ExposeData).)*new List<"), "the prune reuses its buffer");
                string proj = Src("RimMandrake_FlowWorks.csproj");
                foreach (string f in new[] { "RM_JobDriver_ShovelFloor.cs", "RM_DigProgress.cs", "RM_DigProgressMath.cs" })
                {
                    Assert(proj.Contains("<Compile Include=\"" + f + "\" />"), f + " is compiled into the mod");
                }
            });
        }
    }
}
