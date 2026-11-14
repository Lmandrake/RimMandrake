using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    /// <summary>RIMMANDRAKE_KEEP_DIG_PROGRESS_ACROSS_MEALS_AND_NAPS: an interrupted dig or fill keeps its work per square.
    /// The job model below is vanilla JobDriver_AffectFloor's work toil (workLeft = total at start, minus 1.7 x speed per
    /// tick, DoEffect and the order's deletion at 0) with RM_JobDriver_ShovelFloor's two hooks, both calling the
    /// production RM_DigProgressMath and RM_DigProgressStore. The wiring cases read the production source that calls them.</summary>
    internal static class DigProgressChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(string rel) => RiverSwitchFlipChecks.Src(rel);

        private static void Has(string src, string pattern, string what) => RiverSwitchFlipChecks.Has(src, pattern, what);

        private const float Notch = RM_DigDepthMath.WorkPerNotch * RM_DigDepthMath.DefaultLabourMultiplier; // 12,800, the live soil cut

        /// <summary>One square: its depth and whether its order stands. Removing the order is the RemoveDesignation postfix.</summary>
        private sealed class Square
        {
            public int Cell = 4321;
            public int Depth;
            public bool Order = true;

            public void RemoveOrder(RM_DigProgressStore store, bool fill)
            {
                Order = false;
                store.Clear(Cell, fill);
            }
        }

        /// <summary>One job on the square, at most <paramref name="maxTicks"/> working ticks (then broken off: a draft, a
        /// meal). <paramref name="keep"/> false is vanilla (no store). Returns the ticks it worked.</summary>
        private static int Job(RM_DigProgressStore store, Square sq, bool fill, float total, float speed, int maxTicks,
            bool keep, out bool landed, bool refusedAtCap = false)
        {
            landed = false;
            float workLeft = total;                                                     // vanilla initAction
            if (keep)
            {
                workLeft = RM_DigProgressMath.WorkLeftAtStart(total, store.Take(sq.Cell, fill, sq.Depth));
            }
            int ticks = 0;
            bool effect = false;
            while (ticks < maxTicks)
            {
                workLeft = RM_DigProgressMath.AfterTicks(workLeft, speed, 1);
                ticks++;
                if (workLeft <= 0f)
                {
                    if (!refusedAtCap)
                    {
                        sq.Depth += fill ? -1 : 1;                                      // DoEffect
                    }
                    sq.RemoveOrder(store, fill);                                        // vanilla deletes the order
                    if (refusedAtCap)
                    {
                        sq.Order = true;                                                // the dig's finish action puts it back
                    }
                    effect = true;
                    break;
                }
            }
            if (keep)
            {
                float done = RM_DigProgressMath.DoneAtEnd(total, workLeft, true);
                bool spent = effect && !refusedAtCap;
                if (RM_DigProgressMath.Keep(done, spent, sq.Order))
                {
                    store.Put(sq.Cell, fill, done, sq.Depth);
                }
            }
            landed = effect && !refusedAtCap;
            return ticks;
        }

        private static int Uninterrupted(float total, float speed)
        {
            return Job(new RM_DigProgressStore(), new Square(), false, total, speed, int.MaxValue, true, out _);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("DigProgress_interrupt_at_60_percent_costs_the_uninterrupted_work", () =>
            {
                foreach (float speed in new[] { 0.19f, 0.5f, 1f, 1.7f })
                {
                    foreach (float total in new[] { 3200f, Notch, 51200f })
                    {
                        int whole = Uninterrupted(total, speed);
                        var store = new RM_DigProgressStore();
                        var sq = new Square();
                        int first = Job(store, sq, false, total, speed, (int)(0.6f * whole), true, out bool l1);
                        Assert(!l1 && store.Count == 1, "broken off at 60% (speed " + speed + ", " + total + "): work parked");
                        int second = Job(store, sq, false, total, speed, int.MaxValue, true, out bool l2);
                        Assert(l2 && sq.Depth == 1, "the resumed job lands the cut");
                        float ratio = (first + second) / (float)whole;
                        Assert(ratio <= 1.05f && ratio >= 0.999f, "speed " + speed + ", work " + total + ": interrupted " + (first + second)
                            + " vs uninterrupted " + whole + " ticks (ratio " + ratio + ", bar 1.05)");
                        Assert(store.Count == 0, "nothing left parked after the cut lands");

                        // vanilla (the base commit's behaviour): the second job starts from zero
                        var sqv = new Square();
                        int v1 = Job(store, sqv, false, total, speed, (int)(0.6f * whole), false, out _);
                        int v2 = Job(store, sqv, false, total, speed, int.MaxValue, false, out _);
                        Assert((v1 + v2) / (float)whole > 1.55f, "the model sees vanilla's restart (ratio " + (v1 + v2) / (float)whole + ", live 1.61)");
                    }
                }
            });

            Case("DigProgress_many_breaks_sum_to_the_uninterrupted_work", () =>
            {
                foreach (int chunk in new[] { 1, 37, 2000, 2500 })
                {
                    int whole = Uninterrupted(Notch, 0.6f);
                    var store = new RM_DigProgressStore();
                    var sq = new Square();
                    int ticks = 0, jobs = 0;
                    bool landed = false;
                    while (!landed && jobs < 100000)
                    {
                        ticks += Job(store, sq, false, Notch, 0.6f, chunk, true, out landed);
                        jobs++;
                    }
                    Assert(landed && Math.Abs(ticks - whole) <= 1 + whole / 1000, "broken every " + chunk + " ticks: " + ticks + " vs " + whole);
                }
                // vanilla: a colonist who stops every 2000 ticks never lands a 12,800 cut at speed 0.6 (needs 12,550 ticks)
                var sqv = new Square();
                bool lv = false;
                for (int j = 0; j < 50 && !lv; j++)
                {
                    Job(new RM_DigProgressStore(), sqv, false, Notch, 0.6f, 2000, false, out lv);
                }
                Assert(!lv, "without the store the cut never lands");
            });

            Case("DigProgress_second_pawn_continues_the_first", () =>
            {
                var store = new RM_DigProgressStore();
                var sq = new Square();
                int a = Job(store, sq, false, Notch, 1f, (int)(0.6f * Uninterrupted(Notch, 1f)), true, out _);
                float parked = store.Peek(sq.Cell, false, sq.Depth);
                Assert(Math.Abs(parked - a * 1.7f) < 1f, "pawn A's work is parked (" + parked + ")");
                int b = Job(store, sq, false, Notch, 0.5f, int.MaxValue, true, out bool lb);
                float expect = (Notch - parked) / (1.7f * 0.5f);
                Assert(lb && Math.Abs(b - expect) <= 1.5f, "pawn B (half speed) does only the rest: " + b + " vs " + expect + " ticks");

                // dig and fill keep apart: a filler on the square never inherits a digger's work
                var s2 = new RM_DigProgressStore();
                s2.Put(9, false, 5000f, 0);
                Assert(s2.Take(9, true, 0) == 0f && s2.Peek(9, false, 0) == 5000f, "a dig's work never counts toward a fill");
            });

            Case("DigProgress_cancel_clears", () =>
            {
                var store = new RM_DigProgressStore();
                var sq = new Square();
                Job(store, sq, false, Notch, 1f, 4000, true, out _);
                Assert(store.Count == 1, "parked");
                sq.RemoveOrder(store, false);                                           // the player cancels
                Assert(store.Count == 0, "the cancelled order takes its work with it");
                sq.Order = true;                                                        // and designates again
                int again = Job(store, sq, false, Notch, 1f, int.MaxValue, true, out _);
                Assert(Math.Abs(again - Uninterrupted(Notch, 1f)) <= 1, "a fresh order starts from zero: " + again);

                // an order cancelled while the job runs: the job ends with no order, nothing is parked
                var sq2 = new Square();
                var st2 = new RM_DigProgressStore();
                sq2.Order = false;
                Job(st2, sq2, false, Notch, 1f, 4000, true, out _);
                Assert(st2.Count == 0, "no standing order, nothing parked");
                Assert(!RM_DigProgressMath.Keep(4000f, false, false) && RM_DigProgressMath.Keep(4000f, false, true), "Keep needs the order");
            });

            Case("DigProgress_save_load_keeps_and_sanitises", () =>
            {
                var store = new RM_DigProgressStore();
                store.Put(0, false, 100f, 0);
                store.Put(0, true, 200f, 3);
                store.Put(159999, false, 12000.5f, 7);
                var k = new List<int>(); var w = new List<float>(); var d = new List<int>();
                store.ToLists(k, w, d);
                Assert(k.Count == 3 && w.Count == 3 && d.Count == 3, "three rows saved");
                var back = RM_DigProgressStore.FromLists(k, w, d, 160000);
                Assert(back.Count == 3 && back.Take(0, false, 0) == 100f && back.Take(0, true, 3) == 200f
                       && back.Take(159999, false, 7) == 12000.5f, "every row loads with its work and depth");
                var reload = RM_DigProgressStore.FromLists(k, w, d, 160000);
                Assert(reload.Take(159999, false, 6) == 0f, "the depth tag survives the save (a moved depth still voids)");

                Assert(RM_DigProgressStore.FromLists(null, null, null, 100).Count == 0, "a save from before this fix: empty store");
                var bad = RM_DigProgressStore.FromLists(
                    new List<int> { RM_DigProgressMath.Key(5, false), -4, RM_DigProgressMath.Key(5000, false), RM_DigProgressMath.Key(6, false), RM_DigProgressMath.Key(7, false), RM_DigProgressMath.Key(8, false) },
                    new List<float> { 50f, 50f, 50f, float.NaN, -1f },
                    new List<int> { 1, 1, 1, 1, 1, 1 }, 100);
                Assert(bad.Count == 1 && bad.Take(5, false, 1) == 50f, "negative key, off-map cell, NaN, negative and short rows are dropped");

                // a job saved mid-work keeps vanilla's workLeft and our total: its end reads the same done work
                Assert(RM_DigProgressMath.DoneAtEnd(Notch, Notch - 7680f, true) == 7680f, "60% done reads 7,680 of 12,800");
            });

            Case("DigProgress_edges", () =>
            {
                var s = new RM_DigProgressStore();
                Assert(s.Take(0, false, 0) == 0f && s.Peek(12, true, 0) == 0f, "an empty store resumes nothing");
                s.Clear(3, false);
                s.Clear(-1, true);
                s.Put(-1, false, 10f, 0);
                Assert(s.Count == 0 && s.Take(-1, false, 0) == 0f, "an off-map square (index -1) is never stored");
                s.Put(3, false, 10f, 0);
                s.Put(3, false, 0f, 0);
                Assert(s.Count == 0, "parking no work clears the square");
                foreach (float bad in new[] { float.NaN, float.PositiveInfinity, -5f })
                {
                    s.Put(3, false, bad, 0);
                    Assert(s.Count == 0, "unusable work " + bad + " is not parked");
                }
                s.Put(3, false, 5000f, 2);
                Assert(s.Take(3, false, 3) == 0f && s.Count == 0, "the square was cut since: the work is void and dropped");
                Assert(RM_DigProgressMath.Resume(true, 5f, 2, 2) == 5f && RM_DigProgressMath.Resume(false, 5f, 2, 2) == 0f, "nothing stored, nothing resumed");

                Assert(RM_DigProgressMath.WorkLeftAtStart(Notch, 0f) == Notch, "no parked work: vanilla's full work");
                Assert(RM_DigProgressMath.WorkLeftAtStart(Notch, 20000f) == 0f, "more parked than the total (labour lowered): lands at once");
                Assert(RM_DigProgressMath.WorkLeftAtStart(Notch, float.NaN) == Notch, "a bad parked value is ignored");
                Assert(RM_DigProgressMath.WorkLeftAtStart(0f, 100f) == 0f, "a zero-work job stays vanilla's");
                Assert(RM_DigProgressMath.DoneAtEnd(Notch, RM_DigProgressMath.VanillaNotStarted, false) == 0f, "ended before the work toil: nothing");
                Assert(RM_DigProgressMath.DoneAtEnd(Notch, -3f, true) == Notch && RM_DigProgressMath.DoneAtEnd(Notch, Notch + 50f, true) == 0f
                       && RM_DigProgressMath.DoneAtEnd(0f, 5f, true) == 0f && RM_DigProgressMath.DoneAtEnd(Notch, float.NaN, true) == 0f, "DoneAtEnd clamps");
                Assert(!RM_DigProgressMath.WasMidWork(RM_DigProgressMath.VanillaNotStarted) && RM_DigProgressMath.WasMidWork(2800f)
                       && !RM_DigProgressMath.WasMidWork(0f), "an old save's countdown: -1000 is not started, positive is mid-work");
                Assert(!RM_DigProgressMath.Keep(4000f, true, true), "landed work is spent, not parked (no second notch from it)");

                // a cut refused at the digger's cap: the order comes back and the finished work waits for the next digger
                var sq = new Square();
                var st = new RM_DigProgressStore();
                Job(st, sq, false, Notch, 1f, int.MaxValue, true, out bool l1, refusedAtCap: true);
                Assert(!l1 && sq.Depth == 0 && st.Peek(sq.Cell, false, 0) == Notch, "the refused cut's whole work is parked");
                int next = Job(st, sq, false, Notch, 1f, int.MaxValue, true, out bool l2);
                Assert(l2 && next == 1 && sq.Depth == 1, "the next digger lands it on the first tick (" + next + ")");

                for (int i = 0; i < 400 * 400; i += 397)
                {
                    foreach (bool f in new[] { false, true })
                    {
                        int key = RM_DigProgressMath.Key(i, f);
                        Assert(RM_DigProgressMath.CellOf(key) == i && RM_DigProgressMath.IsFill(key) == f, "key round-trips for cell " + i);
                    }
                }
            });

            Case("DigProgress_wiring_vanilla_toil_kept_and_hooked_at_start_and_end", () =>
            {
                string s = Src("RM_JobDriver_ShovelFloor.cs");
                Has(s, @"abstract class RM_JobDriver_ShovelFloor : JobDriver_AffectFloor", "derives vanilla AffectFloor");
                Has(s, @"AccessTools\.FieldRefAccess<JobDriver_AffectFloor, float>\(""workLeft""\)", "reads vanilla's own countdown");
                Has(s, @"catch \(Exception e\) \{ Log\.Warning\(", "a renamed field warns instead of breaking every dig");
                Has(s, @"private void ResumeParkedWork\(\) \{ if \(WorkLeft == null\) \{ return; \}", "start hook stands aside without the field");
                Has(s, @"if \(WorkLeft == null \|\| map == null", "end hook stands aside without the field");
                Has(s, @"AddFinishAction\(delegate \(JobCondition cond\) \{ ParkUnfinishedWork\(\); \}\); return ResumeOnWorkToil\(base\.MakeNewToils\(\)\);",
                    "vanilla's toils, wrapped; parking is a finish action");
                Has(s, @"t\.initAction = delegate \{ setFullWork\(\); ResumeParkedWork\(\); \};", "after vanilla sets the full work, the parked work comes off it");
                Has(s, @"WorkLeft\(this\) = RM_DigProgressMath\.WorkLeftAtStart\(total, parked\);", "start: WorkLeftAtStart");
                Has(s, @"\?\.Take\(job\.targetA\.Cell, IsFill\)", "start: takes the square's parked work");
                Has(s, @"float done = RM_DigProgressMath\.DoneAtEnd\(total, workLeft, started\);", "end: DoneAtEnd");
                Has(s, @"bool landed = workLeft <= 0f && !KeepWorkAfterEffect;", "end: landed unless the cut was refused");
                Has(s, @"bool orderStands = job\.ignoreDesignations \|\| map\.designationManager\.DesignationAt\(c, DesDef\) != null;", "end: the order must stand");
                Has(s, @"if \(RM_DigProgressMath\.Keep\(done, landed, orderStands\)\) \{ map\.GetComponent<RM_MapComponent_DigProgress>\(\)\?\.Put\(c, IsFill, done\);", "end: parks");
                Has(s, @"Scribe_Values\.Look\(ref rmWorkTotal, ""rmShovelWorkTotal"", 0f\); Scribe_Values\.Look\(ref rmWorkStarted, ""rmShovelWorkStarted"", false\);", "saved with the job");
                Assert(!s.Contains("tickIntervalAction =") && !s.Contains("tickAction ="), "no tick of its own: vanilla's work tick is untouched");

                string dig = Src("JobDriver_DigCanal.cs");
                Has(dig, @"class JobDriver_DigCanal : RM_JobDriver_ShovelFloor", "dig rides it");
                Has(dig, @"protected override bool IsFill => false;", "dig keys as dig");
                Has(dig, @"protected override bool KeepWorkAfterEffect => cutRefusedButOwed;", "a refused-but-owed cut keeps its work");
                int fin = dig.IndexOf("AddFinishAction(", StringComparison.Ordinal), bas = dig.IndexOf("return base.MakeNewToils();", StringComparison.Ordinal);
                Assert(fin >= 0 && bas > fin, "the dig's re-designation finish action is added before the base's parking one");
                string fill = Src("JobDriver_FillInCanal.cs");
                Has(fill, @"class JobDriver_FillInCanal : RM_JobDriver_ShovelFloor", "fill rides it");
                Has(fill, @"protected override bool IsFill => true;", "fill keys as fill");

                string root = Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_JobDriver_ShovelFloor.cs"));
                var direct = Directory.EnumerateFiles(root, "*.cs", SearchOption.AllDirectories)
                    .Where(f => !f.Contains(Path.DirectorySeparatorChar + "SelfTest" + Path.DirectorySeparatorChar)
                                && !f.Contains(Path.DirectorySeparatorChar + "obj" + Path.DirectorySeparatorChar))
                    .Where(f => Regex.IsMatch(File.ReadAllText(f), @"class \w+ : JobDriver_AffectFloor\b"))
                    .Select(Path.GetFileName).ToList();
                Assert(direct.Count == 1 && direct[0] == "RM_JobDriver_ShovelFloor.cs",
                    "only the shovel driver derives AffectFloor directly (found: " + string.Join(", ", direct) + ")");
            });

            Case("DigProgress_wiring_store_saved_cleared_with_its_order_no_tick", () =>
            {
                string s = Src("RM_DigProgress.cs");
                Has(s, @"class RM_MapComponent_DigProgress : MapComponent", "a map component");
                Has(s, @"private RM_DigProgressStore store", "wraps the tested store");
                Has(s, @"store\.ToLists\(saveKeys, saveWork, saveDepths\);", "saves the store");
                foreach (string n in new[] { "rmDigProgressKeys", "rmDigProgressWork", "rmDigProgressDepths" })
                {
                    Has(s, @"Scribe_Collections\.Look\(ref save\w+, """ + n + @""", LookMode\.Value\);", n + " scribed");
                }
                Has(s, @"store = RM_DigProgressStore\.FromLists\(saveKeys, saveWork, saveDepths, map\.cellIndices\.NumGridCells\);", "loads through FromLists");
                Has(s, @"store\.Take\(i, fill, DepthNow\(c\)\)", "Take checks today's depth");
                Has(s, @"\[HarmonyPatch\(typeof\(DesignationManager\), nameof\(DesignationManager\.RemoveDesignation\)\)\]", "cleared when its order is removed");
                Has(s, @"des\.def == RimMandrakeFlowWorks_DefOf\.RM_DigCanal\) \{ fill = false; \} else if \(des\.def == RimMandrakeFlowWorks_DefOf\.RM_FillInCanal\) \{ fill = true; \}", "dig and fill orders only");
                Has(s, @"___map\.GetComponent<RM_MapComponent_DigProgress>\(\)\?\.Clear\(des\.target\.Cell, fill\);", "clears that square");
                Assert(!s.Contains("MapComponentTick") && !s.Contains("MapComponentUpdate"), "no per-tick cost: the store has no tick");
                string proj = Src("RimMandrake_FlowWorks.csproj");
                foreach (string f in new[] { "RM_JobDriver_ShovelFloor.cs", "RM_DigProgress.cs", "RM_DigProgressMath.cs" })
                {
                    Assert(proj.Contains("<Compile Include=\"" + f + "\" />"), f + " is compiled into the mod");
                }
            });
        }
    }
}
