// WALLREACH_RELABEL_TAME_SLICED_BUFFERED (design/RimMandrake/hose_wire_algorithms_advisory_2026-10-28.md §4 #8): the wall-aware
// reach labels are rebuilt a slice at a time into a spare buffer and published whole. These checks drive the PRODUCTION
// RM_WallReachMath.LabelJob / LabelSlot / Covers against the one-shot RM_WallReachMath.Label over random grids, edit sequences
// and budgets, replay RM_WallReach's scheduling rule on a simulated map to show a veto never answers from a half-built or an
// uncovered labelling (with a negative control proving the instrument can see a false NO), and pin the Verse wiring.
using System;
using System.Collections.Generic;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class WallReachSliceChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static string Between(string src, string start, string end)
        {
            int i = src.IndexOf(start, StringComparison.Ordinal);
            Assert(i >= 0, "marker present: " + start);
            int j = src.IndexOf(end, i + start.Length, StringComparison.Ordinal);
            return j < 0 ? src.Substring(i) : src.Substring(i, j - i);
        }

        private static int Count(string s, string what)
        {
            int n = 0;
            for (int i = s.IndexOf(what, StringComparison.Ordinal); i >= 0; i = s.IndexOf(what, i + what.Length, StringComparison.Ordinal)) n++;
            return n;
        }

        private static bool Same(RM_WallReachMath.Labels a, RM_WallReachMath.Labels b)
        {
            if (a == null || b == null) return a == b;
            if (a.count != b.count || a.width != b.width || a.height != b.height || a.k != b.k || a.cls != b.cls || a.label.Length != b.label.Length) return false;
            for (int i = 0; i < a.label.Length; i++) if (a.label[i] != b.label[i]) return false;
            return true;
        }

        private static readonly byte[] KindPool =
        {
            RM_WallReachMath.Open, RM_WallReachMath.Open, RM_WallReachMath.Open, RM_WallReachMath.Open, RM_WallReachMath.Wall,
            RM_WallReachMath.Wall, RM_WallReachMath.Door, RM_WallReachMath.PlayerDoor, RM_WallReachMath.Fence, RM_WallReachMath.DeepWater,
            RM_WallReachMath.HeldDoor, RM_WallReachMath.ShutGate,
        };

        private static (byte[] kind, byte[] depth, Dictionary<int, int> ramps) RandomInputs(Random r, int w, int h)
        {
            int n = w * h;
            var kind = new byte[n];
            for (int i = 0; i < n; i++) kind[i] = KindPool[r.Next(KindPool.Length)];
            byte[] depth = null;
            Dictionary<int, int> ramps = null;
            if (r.Next(3) > 0)
            {
                depth = new byte[n];
                for (int i = 0; i < n; i++) depth[i] = (byte)(r.Next(4) == 0 ? r.Next(6) : 0);
                if (r.Next(2) == 0)
                {
                    ramps = new Dictionary<int, int>();
                    for (int q = r.Next(1, 6); q > 0; q--)
                    {
                        int a = r.Next(n), b = r.Next(4) switch { 0 => a + 1, 1 => a - 1, 2 => a + w, _ => a - w };
                        if (b >= 0 && b < n) ramps[a] = b;
                    }
                }
            }
            return (kind, depth, ramps);
        }

        private static int RandomBudget(Random r, int n)
        {
            switch (r.Next(5))
            {
                case 0: return 1;
                case 1: return r.Next(1, 8);
                case 2: return r.Next(1, Math.Max(2, n / 3));
                case 3: return r.Next(1, 4 * n + 2);
                default: return int.MaxValue;
            }
        }

        private static int[] Garbage(Random r, int n)
        {
            var a = new int[n];
            for (int i = 0; i < n; i++) a[i] = r.Next(-3, 1000);
            return a;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("WallReach_sliced_equals_one_shot", () =>
            {
                // Any slicing (budgets from 1 unit to unbounded, changing every step) of one job gives Label's labels exactly:
                // the same ids, the same count. Each step stays within its budget, does at least one unit while unfinished, and
                // the whole job costs at most 3 units per square (mark, scan, pop).
                var r = new Random(20261028);
                for (int trial = 0; trial < 600; trial++)
                {
                    int w = r.Next(1, 41), h = r.Next(1, 41), n = w * h;
                    var (kind, depth, ramps) = RandomInputs(r, w, h);
                    int band = r.Next(0, 4), cls = r.Next(RM_WallReachMath.ClassCount);
                    RM_WallReachMath.Labels want = RM_WallReachMath.Label(kind, depth, w, h, band, cls, RM_WallReachMath.RampJoins(ramps));
                    var job = new RM_WallReachMath.LabelJob(kind, depth, ramps, w, h, band, cls, r.Next(2) == 0 ? Garbage(r, n) : null, Garbage(r, n + r.Next(3)));
                    int guard = 0;
                    while (!job.Done)
                    {
                        Assert(job.Result == null, "an unfinished job has no result to read");
                        int b = RandomBudget(r, n);
                        int spent = job.Step(b);
                        Assert(spent >= 1 && spent <= b, "a step does 1.." + b + " units, did " + spent);
                        Assert(++guard <= 3 * n + 2, "the job finishes within 3n unit steps");
                    }
                    Assert(job.work <= 3L * n, "work " + job.work + " > 3n (" + 3 * n + ")");
                    Assert(Same(job.Result, want), "trial " + trial + " " + w + "x" + h + " band " + band + " cls " + cls + ": sliced labels differ from Label's");
                    Assert(job.Step(5) == 0 && Same(job.Result, want), "a finished job stays finished");
                }
            });

            Case("WallReach_slot_double_buffer_never_half_built", () =>
            {
                // LabelSlot over an edit sequence: jobs begun, advanced in random slices, dropped mid-flight (a new Begin), and
                // published. At every point the published labels are exactly Label(the inputs they were published with) — the
                // previous whole labelling until the new one is complete, never the array a job is writing. Skips keep the
                // published labels; Rebuild (the one-shot path) agrees too.
                var r = new Random(4242);
                for (int trial = 0; trial < 80; trial++)
                {
                    int w = r.Next(2, 30), h = r.Next(2, 30), n = w * h;
                    var (kind0, depth, ramps) = RandomInputs(r, w, h);
                    int band = r.Next(0, 4), cls = r.Next(RM_WallReachMath.ClassCount);
                    var slot = new RM_WallReachMath.LabelSlot();
                    var queue = new int[n];
                    byte[] live = (byte[])kind0.Clone();
                    byte[] snap = (byte[])live.Clone();
                    int publishes = 0, drops = 0;
                    for (int step = 0; step < 120; step++)
                    {
                        if (r.Next(3) == 0)
                        {
                            for (int e = r.Next(1, 4); e > 0; e--) live[r.Next(n)] = KindPool[r.Next(KindPool.Length)];
                            snap = (byte[])live.Clone();   // a new published kinds array (never written after)
                        }
                        if (slot.job == null || r.Next(8) == 0)
                        {
                            if (slot.job != null) drops++;
                            RM_WallReachMath.Labels before = slot.labels;
                            bool began = slot.Begin(snap, depth, ramps, w, h, band, cls, queue);
                            Assert(ReferenceEquals(slot.labels, before), "Begin never touches the published labels");
                            Assert(began == (slot.job != null), "Begin reports whether a job is in flight");
                            if (!began) Assert(slot.SameAsPublished(snap, depth, ramps, w, h), "a skip only for the published inputs");
                        }
                        RM_WallReachMath.Labels pub = slot.labels;
                        int[] pubCopy = pub == null ? null : (int[])pub.label.Clone();
                        bool done = slot.Advance(RandomBudget(r, n), out int spent);
                        if (!done && pub != null)
                        {
                            Assert(ReferenceEquals(slot.labels, pub), "an unfinished slice leaves the published labels in place");
                            for (int i = 0; i < n; i++) Assert(pub.label[i] == pubCopy[i], "the published labels are not written by a slice");
                        }
                        if (done)
                        {
                            publishes++;
                            Assert(slot.job == null, "a published job is no longer in flight");
                            Assert(ReferenceEquals(slot.spare, pub), "the labels before become the spare");
                        }
                        if (slot.labels != null)
                        {
                            Assert(slot.job == null || !ReferenceEquals(slot.job.Buffer, slot.labels.label), "a job never writes the published array");
                            var truth = RM_WallReachMath.Label(slot.builtKinds, slot.builtDepth, w, h, band, cls, RM_WallReachMath.RampJoins(slot.builtRamps));
                            Assert(Same(slot.labels, truth), "trial " + trial + " step " + step + ": published labels are not Label(their inputs)");
                        }
                    }
                    Assert(publishes > 0, "the sequence published at least once");
                    var one = new RM_WallReachMath.LabelSlot();
                    Assert(one.Rebuild(live, depth, ramps, w, h, band, cls), "the one-shot path floods");
                    Assert(Same(one.labels, RM_WallReachMath.Label(live, depth, w, h, band, cls, RM_WallReachMath.RampJoins(ramps))), "Rebuild equals Label");
                    Assert(!one.Rebuild(live, depth, ramps, w, h, band, cls) && one.skips == 1, "identical inputs skip");
                }
            });

            Case("WallReach_slice_never_vetoes_from_uncovered_labels", () =>
            {
                // RM_WallReach's rule on a simulated map: edits close squares (a wall built: stale labels stay MORE connected,
                // they may serve) or open them (a breach: forced, the unsafe generation moves). Jobs begin with the generation
                // read before the kinds, run in random slices, finish then restart (oldest-built first), and publish their
                // generation with the labels. A query vetoes only from published labels that cover the current generation.
                // Property: no pair reachable on the live map is ever vetoed. Negative control: the same replay with the
                // coverage gate off must find a false NO, else this replay could not see one.
                int falseNo = Replay(true, 300);
                Assert(falseNo == 0, "false NO with the coverage gate on: " + falseNo);
                int control = Replay(false, 300);
                Assert(control > 0, "negative control: without the gate the replay must see a false NO (saw none: blind instrument)");
            });

            Case("WallReach_paused_write_reaches_every_labelling", () =>
            {
                // RIMMANDRAKE_TRACE_FLOWWORKS_UNDER_DECK_PATH_MISS_ONE_IN_28_RUNS: an 8-square trench is dug one square a write with
                // the clock stopped. The region: 1 to 4 labellings, 1 to 9 frames between writes, 1 to 9 slices a relabel, built
                // before the trench inside or outside the throttle, the last write paused or on the running clock just before the
                // pause. Left out: kinds that move too (a wall beside the trench: the wall part names its squares and is judged
                // by the swim and wall rows above), and the live frame rate (the gap covers it). Each case ends when nothing is
                // owed or 4 relabels a labelling have passed (plus StillFrames when the last write ran on the clock); then no labelling may be stale and none may veto
                // the trench's far end. Negative control: the rule before (one unthrottled frame a write) must strand some.
                PausedSweep(true, out int cases, out int stale, out int vetoed, out int worst, out int limit, out _);
                PausedSweep(false, out int cases0, out int stale0, out int vetoed0, out _, out _, out int staleRan0);
                string read = "cases=" + cases + " stale=" + stale + " vetoed=" + vetoed + " worstPercentOfBound=" + worst + " limit=" + limit
                    + "; before: stale=" + stale0 + " vetoed=" + vetoed0 + " of " + cases0 + " (the last write paused: stale=" + (stale0 - staleRan0) + ")";
                Console.WriteLine("      " + read);
                Assert(stale0 - staleRan0 > 0 && staleRan0 > 0 && vetoed0 > 0, "negative control: the rule before strands a labelling: " + read);
                Assert(stale == 0 && vetoed == 0, "a paused write reaches every labelling while the clock stands: " + read);
                // the soak stays throttled: bursts of stepped ticks with 3 idle frames between, labels always stale
                var d = new RM_WallReachMath.PausedDebt();
                int un = 0, tick = 0;
                for (int b = 0; b < 125; b++)
                    for (int f = 0; f < 4; f++)
                    {
                        if (f == 0) tick += 8;
                        if (d.Unthrottled(tick, b)) un++;
                        d.Left(tick, b, true);
                    }
                Assert(un == 0, "a stepped soak whose labels are always stale: no unthrottled frame, got " + un);
                // a write during an idle gap is owed until the clock moves again
                d = new RM_WallReachMath.PausedDebt();
                d.Unthrottled(5, 1); d.Left(5, 1, false);
                Assert(d.Unthrottled(5, 2), "a paused write: now"); d.Left(5, 2, true);
                Assert(d.Unthrottled(5, 2), "still stale: owed"); d.Left(5, 2, false);
                Assert(!d.Unthrottled(5, 2), "nothing stale: paid"); d.Left(5, 2, false);
                Assert(d.Unthrottled(5, 3), "the next write"); d.Left(5, 3, true);
                Assert(!d.Unthrottled(6, 3), "the clock moved: throttled again");
            });

            Case("WallReach_slice_wiring_source_pins", () =>
            {
                string src = Src("Superdeep", "RM_WallReach.cs");
                // every forced also moves the unsafe generation (so no change that opens a way escapes the coverage gate)
                int forcedSt = Count(src, "Interlocked.Exchange(ref st.forced, 1)");
                Assert(forcedSt > 0 && Count(src, "Interlocked.Increment(ref st.unsafeGen); Interlocked.Exchange(ref st.forced, 1)") == forcedSt,
                    "each Interlocked.Exchange(ref st.forced, 1) is preceded by Interlocked.Increment(ref st.unsafeGen)");
                Assert(!src.Contains("Interlocked.Exchange(ref StateOf(map).forced, 1)"), "Force goes through the st form (counted above)");
                // the query answers only from a covering labelling, after the forced check (W2)
                string judge = Between(src, "private static bool JudgeOwned(", "if (count) { Queries++;");
                int forced = judge.IndexOf("Volatile.Read(ref StateOf(map).forced) != 0", StringComparison.Ordinal);
                int covers = judge.IndexOf("RM_WallReachMath.Covers(e.coverGen, Volatile.Read(ref StateOf(map).unsafeGen))", StringComparison.Ordinal);
                Assert(forced >= 0 && covers > forced, "JudgeOwned: no veto from a labelling that does not cover the current unsafe generation");
                // the Tick: generation read before the stamp, jobs advanced in budgeted slices, published with their generation
                string tick = Between(src, "private static void TickOwned(Map map, MapState st, bool paused, bool drain)", "private static void CountRebuildCause(");
                int gen = tick.IndexOf("int gen = Volatile.Read(ref st.unsafeGen);", StringComparison.Ordinal);
                int stamp = tick.IndexOf("long stamp = StampOf(map, st);", StringComparison.Ordinal);
                Assert(gen >= 0 && stamp > gen, "Tick reads the unsafe generation before the stamp");
                Assert(tick.Contains("e.slot.Advance(SliceUnits, out int spent)") && tick.Contains("SliceMs"), "Tick advances the job in SliceUnits chunks within SliceMs");
                Assert(!tick.Contains("Build(map, st, e, stamp, views);"), "Tick no longer floods whole labellings in one go");
                string publish = Between(src, "private static void Publish(MapState st, Entry e", "}");
                Assert(publish.Contains("e.coverGen = e.jobGen;") && publish.Contains("e.stamp = e.jobStamp;"), "a publish carries the job's generation and stamp");
                string begin = Between(src, "private static bool BeginJob(", "private static void Publish(");
                Assert(begin.Contains("e.slot.Begin(") && begin.Contains("st.sliceQueue"), "a job floods with the map's slice queue, not the per-thread scratch");
                // the first build (inside a query) is the only whole build left, and covers the generation read before its stamp
                string entryFor = Between(src, "private static Entry EntryFor(", "/// <summary>The ladder joins");
                int g2 = entryFor.IndexOf("int gen = Volatile.Read(ref st.unsafeGen);", StringComparison.Ordinal);
                int b2 = entryFor.IndexOf("Build(map, st, e, StampOf(map, st), gen);", StringComparison.Ordinal);
                Assert(g2 >= 0 && b2 > g2, "EntryFor's first build covers the generation read before its stamp");
                Assert(src.Contains("TickOwned(map, st, true, true);") && Between(src, "public static string ProofReachForce(", "/// <summary>").Contains("Drain(map);"),
                    "ProofReachForce drains every due job (a proof cannot wait for slices)");
            });
        }

        private sealed class SimEntry
        {
            public readonly RM_WallReachMath.LabelSlot slot = new RM_WallReachMath.LabelSlot();
            public int cls, stamp = -1, coverGen = -1, jobStamp, jobGen, builtTick = int.MinValue / 2;
        }

        /// <summary>RM_WallReach's paused frames (PausedFrameOwned over TickOwned's slices) on the shipped LabelSlot, KindsSnapshot,
        /// ReadPartsDecision, RebuildDue and PausedDebt. owedRule false: the rule before (PausedUnthrottled alone).</summary>
        private static void PausedSweep(bool owedRule, out int cases, out int stale, out int vetoed, out int worst, out int limit, out int staleRan)
        {
            cases = stale = vetoed = worst = staleRan = 0;
            limit = 100;
            for (int count = 1; count <= 4; count++)
            for (int gap = 1; gap <= 9; gap++)
            for (int slices = 1; slices <= 9; slices++)
            for (int age = 0; age <= 60; age += 20)          // ticks since each labelling was built when the clock stopped
            for (int lastRuns = 0; lastRuns <= 1; lastRuns++)
            {
                cases++;
                const int w = 24, h = 12, n = w * h, z = 6, x0 = 8, len = 8;
                var depth = new byte[n];
                byte Kind(int i) => RM_WallReachMath.Open;
                var kinds = new RM_WallReachMath.KindsSnapshot();
                kinds.Publish(new byte[n], 0, w, h);
                long climb = 0;
                int tick = 1000, frame = 0;
                var queue = new int[n];
                var entries = new List<SimEntry>();
                for (int i = 0; i < count; i++)
                {
                    var e = new SimEntry { cls = i, builtTick = tick - age, stamp = 0 };
                    e.slot.Rebuild(kinds.published, (byte[])depth.Clone(), null, w, h, 2, e.cls);
                    entries.Add(e);
                }
                SimEntry active = null;
                bool reading = false;
                var parts = new long[6];
                var jobParts = new long[6];
                var debt = new RM_WallReachMath.PausedDebt();
                int seenTick = int.MinValue;
                long seenStamp = long.MinValue;
                void Begin(SimEntry e)
                {
                    if (e.slot.Begin(kinds.published, (byte[])depth.Clone(), null, w, h, 2, e.cls, queue)) { active = e; reading = false; }
                    else { e.stamp = e.jobStamp; e.builtTick = tick; active = null; reading = false; }
                }
                // a relabel is one whole kinds read (n units) and at most 3n of flood: 4n units over this many slices
                int budget = Math.Max(1, (4 * n + slices - 1) / slices);
                void Frame(bool paused)
                {
                    frame++;
                    bool un = false;
                    if (paused)
                    {
                        un = owedRule ? debt.Unthrottled(tick, climb) : RM_WallReachMath.PausedUnthrottled(tick, seenTick, climb, seenStamp);
                    }
                    parts[0] = climb;
                    var due = new List<SimEntry>();
                    foreach (SimEntry e in entries)
                    {
                        if (e.stamp == climb)
                        {
                            if (active == e) { if (reading) kinds.AbortRead(); e.slot.Drop(); active = null; reading = false; }
                            continue;
                        }
                        if (active != e && RM_WallReachMath.RebuildDue(true, false, un, tick, e.builtTick, 60)) due.Add(e);
                    }
                    due.Sort((a, b) => a.builtTick.CompareTo(b.builtTick));
                    for (int left = budget, next = 0; left > 0;)
                    {
                        if (active == null)
                        {
                            if (next >= due.Count) break;
                            SimEntry e = due[next++];
                            e.jobStamp = (int)climb;
                            Array.Copy(parts, jobParts, parts.Length);
                            if (!kinds.CurrentFor(climb, w, h)) { kinds.BeginRead(climb, w, h); active = e; reading = true; }
                            else Begin(e);
                        }
                        else if (reading)
                        {
                            if (RM_WallReachMath.ReadPartsDecision(jobParts, parts, 2, 4, 0, true) == RM_WallReachMath.ReadDrop)
                            {
                                kinds.AbortRead(); active = null; reading = false;
                                continue;
                            }
                            bool done = kinds.ReadStep(left, Kind, out int spent);
                            left -= Math.Max(1, spent);
                            if (done) Begin(active);
                        }
                        else
                        {
                            bool done = active.slot.Advance(left, out int spent);
                            left -= Math.Max(1, spent);
                            if (done) { active.stamp = active.jobStamp; active.builtTick = tick; active = null; }
                        }
                    }
                    if (paused)
                    {
                        bool any = entries.Exists(e => e.stamp != climb);
                        debt.Left(tick, climb, any);
                        seenTick = tick; seenStamp = climb;
                    }
                }
                void Dig(int i) { depth[z * w + x0 + i] = 8; climb++; }
                Frame(true);
                for (int i = 0; i < len - 1; i++)
                {
                    Dig(i);
                    for (int f = 0; f < gap; f++) Frame(true);
                }
                if (lastRuns == 1)
                {
                    tick++;                       // the clock ran one tick, the last square was dug on it, and the player paused
                    Dig(len - 1);
                    Frame(false);
                }
                else Dig(len - 1);
                int bound = lastRuns * RM_WallReachMath.PausedDebt.StillFrames + 4 * count * (slices + 1), from = frame;
                while (frame - from < bound && entries.Exists(e => e.stamp != climb)) Frame(true);
                int took = frame - from, behind = 0;
                foreach (SimEntry e in entries)
                {
                    if (e.stamp != climb) behind++;
                    if (RM_WallReachMath.Vetoed(e.slot.labels.At(z * w + x0), new[] { e.slot.labels.At(z * w + x0 + len - 1) }, null)) vetoed++;
                }
                stale += behind;
                staleRan += lastRuns * behind;
                if (behind == 0) worst = Math.Max(worst, 100 * took / bound);
            }
        }

        /// <summary>A replay of RM_WallReach.TickOwned's scheduling on random maps. Returns the false NOs seen.</summary>
        private static int Replay(bool gate, int trials)
        {
            var r = new Random(gate ? 77 : 77);
            int falseNo = 0;
            for (int trial = 0; trial < trials; trial++)
            {
                int w = r.Next(6, 26), h = r.Next(6, 26), n = w * h;
                var live = new byte[n];
                for (int i = 0; i < n; i++) live[i] = r.Next(100) < 35 ? RM_WallReachMath.Wall : RM_WallReachMath.Open;
                int version = 0, unsafeGen = 0;
                byte[] published = (byte[])live.Clone();
                int publishedVersion = 0;
                var entries = new List<SimEntry>();
                foreach (int cls in new[] { 0, RM_WallReachMath.NonOpener | RM_WallReachMath.PlayerDoorsShut | RM_WallReachMath.GateShut })
                    entries.Add(new SimEntry { cls = cls });
                var queue = new int[n];
                SimEntry active = null;
                // first builds (a query's whole build) at version 0
                foreach (SimEntry e in entries)
                {
                    int g = unsafeGen;
                    e.slot.Rebuild(published, null, null, w, h, 0, e.cls);
                    e.stamp = 0; e.coverGen = g; e.builtTick = 0;
                }
                for (int tick = 1; tick < 200; tick++)
                {
                    for (int q = r.Next(0, 3); q > 0; q--)
                    {
                        int c = r.Next(n);
                        if (live[c] == RM_WallReachMath.Wall) { live[c] = RM_WallReachMath.Open; unsafeGen++; }   // breach: forced
                        else live[c] = RM_WallReachMath.Wall;                                                     // wall built: a bump
                        version++;
                    }
                    int gen = unsafeGen;   // read before the stamp
                    if (publishedVersion != version) { published = (byte[])live.Clone(); publishedVersion = version; }
                    // due entries: stale (or uncovered and stale), throttled unless urgent
                    var due = new List<SimEntry>();
                    foreach (SimEntry e in entries)
                    {
                        bool urgent = !RM_WallReachMath.Covers(e.coverGen, gen);
                        if (e.stamp == version)
                        {
                            if (active == e) { e.slot.Drop(); active = null; }
                            e.coverGen = gen;
                            continue;
                        }
                        if (e.slot.job == null && RM_WallReachMath.RebuildDue(true, urgent, false, tick, e.builtTick, 6)) due.Add(e);
                    }
                    due.Sort((a, b) => a.builtTick.CompareTo(b.builtTick));
                    int budget = RandomBudget(r, n) % (2 * n + 1) + 1, left = budget;
                    while (left > 0)
                    {
                        if (active == null)
                        {
                            if (due.Count == 0) break;
                            SimEntry e = due[0];
                            due.RemoveAt(0);
                            e.jobGen = gen; e.jobStamp = version;
                            if (!e.slot.Begin(published, null, null, w, h, 0, e.cls, queue))
                            {
                                e.stamp = e.jobStamp; e.coverGen = e.jobGen; e.builtTick = tick;
                                continue;
                            }
                            active = e;
                        }
                        if (active.slot.Advance(left, out int spent))
                        {
                            active.stamp = active.jobStamp; active.coverGen = active.jobGen; active.builtTick = tick;
                            active = null;
                        }
                        left -= Math.Max(1, spent);
                    }
                    // queries against the live map, mid-job included
                    var truth = RM_WallReachMath.Label(live, null, w, h, 0, 0);
                    foreach (SimEntry e in entries)
                    {
                        var tl = e.cls == 0 ? truth : RM_WallReachMath.Label(live, null, w, h, 0, e.cls);
                        RM_WallReachMath.Labels l = e.slot.labels;
                        if (l == null || (gate && !RM_WallReachMath.Covers(e.coverGen, unsafeGen))) continue;
                        for (int q = 0; q < 12; q++)
                        {
                            int a = r.Next(n), b = r.Next(n);
                            if (tl.label[a] < 0 || tl.label[a] != tl.label[b]) continue;   // not reachable now: any answer is fine
                            if (RM_WallReachMath.Vetoed(l.At(a), new[] { l.At(b) }, null)) falseNo++;
                        }
                    }
                }
            }
            return falseNo;
        }
    }
}
