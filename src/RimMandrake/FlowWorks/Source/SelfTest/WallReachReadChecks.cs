// WALLREACH_BEGINJOB_TAME_INPUTS_OUT_OF_SLICE: a job's kinds read (the whole map, one KindAt per square: 3.9 ms on the live
// 250 x 250 map, p1_DRY_prof RM_WallReach:Kinds maxUs=3933.8 against maxSliceMs=4.111) ran inside the 1 ms slice. It is now
// a sliced read (RM_WallReachMath.KindsSnapshot.BeginRead / ReadStep) whose squares changed behind the cursor are read
// again (Touch, fed by the queued deltas and walkability notes), into recycled arrays. These checks drive the PRODUCTION
// KindsSnapshot: a torn read with its touches equals the map when it is published (and without touches it does not: the
// negative control); steady reads allocate nothing; RM_WallReach's protocol (notes judged against the published snapshot,
// sliced reads, sliced floods, the coverage gate) never vetoes a reachable pair, while the same replay without touches does.
// The Verse wiring is pinned by source text.
using System;
using System.Collections.Generic;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class WallReachReadChecks
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

        /// <summary>Read a random map in random slices while random squares change between slices (each change touched when
        /// <paramref name="touch"/>); returns how many published reads differed from the map at the moment they published.</summary>
        private static int TornReads(bool touch, int trials)
        {
            var r = new Random(7101);
            int bad = 0;
            for (int t = 0; t < trials; t++)
            {
                int w = 4 + r.Next(14), h = 4 + r.Next(14), n = w * h;
                var live = new byte[n];
                for (int i = 0; i < n; i++) live[i] = (byte)r.Next(3);
                var snap = new RM_WallReachMath.KindsSnapshot();
                Func<int, byte> kindAt = i => live[i];
                snap.BeginRead(t, w, h);
                bool done = false;
                for (int guard = 0; !done && guard < 10 * n + 10; guard++)
                {
                    int edits = r.Next(4);
                    for (int k = 0; k < edits; k++)
                    {
                        int c = r.Next(n);
                        live[c] = (byte)((live[c] + 1 + r.Next(2)) % 3);
                        if (touch) snap.Touch(c, kindAt);
                    }
                    if (r.Next(40) == 0) snap.RestartRead();
                    done = snap.ReadStep(1 + r.Next(Math.Max(1, n / 3)), kindAt, out _);
                }
                Assert(done, "read finished");
                for (int i = 0; i < n; i++)
                {
                    if (snap.published[i] != live[i]) { bad++; break; }
                }
            }
            return bad;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("WallReach_read_sliced_touched_equals_map", () =>
            {
                Assert(TornReads(true, 400) == 0, "a sliced read with its touches equals the map when it publishes");
                Assert(TornReads(false, 400) > 0, "negative control: without touches a torn read is seen to differ");
            });

            Case("WallReach_read_recycles_arrays", () =>
            {
                int w = 250, h = 250, n = w * h;
                var snap = new RM_WallReachMath.KindsSnapshot();
                var held = new List<byte[]>();   // the arrays labellings were built from (two entries, one a step behind)
                snap.inUse = a =>
                {
                    for (int i = 0; i < held.Count; i++) if (ReferenceEquals(held[i], a)) return true;
                    return false;
                };
                byte phase = 0;
                Func<int, byte> kindAt = i => (byte)((i + phase) & 3);
                long allocAfterWarm = 0, bytesAfterWarm = 0;
                for (int round = 0; round < 40; round++)
                {
                    if (round == 8)
                    {
                        allocAfterWarm = snap.allocs;
                        bytesAfterWarm = GC.GetAllocatedBytesForCurrentThread();
                    }
                    phase = (byte)(round % 3);   // content moves each read: the published array is replaced
                    byte[] before = snap.published;
                    snap.BeginRead(round, w, h);
                    while (!snap.ReadStep(4096, kindAt, out _)) { }
                    Assert(!ReferenceEquals(snap.published, before) || round == 0 && before == null, "content moved: a new array is published");
                    foreach (byte[] hold in held) Assert(!ReferenceEquals(hold, snap.published), "a read never lands in an array a labelling holds");
                    held.Insert(0, snap.published);
                    if (held.Count > 2) held.RemoveAt(2);
                    // a reused array is never one a labelling holds: every held array still has the content it was published with
                    for (int k = 0; k < held.Count; k++)
                    {
                        byte expect = (byte)(((round - k) % 3 + 3) % 3);
                        if (round - k < 0) continue;
                        Assert(held[k][1] == (byte)((1 + expect) & 3), "held array " + k + " untouched at round " + round);
                    }
                }
                long bytes = GC.GetAllocatedBytesForCurrentThread() - bytesAfterWarm;
                Assert(snap.allocs - allocAfterWarm == 0, "steady reads allocate no kinds array (allocs " + (snap.allocs - allocAfterWarm) + ")");
                Assert(bytes < n, "steady reads allocate under one map of bytes (" + bytes + ")");
                // negative control: without the in-use predicate nothing is reused, and the counter sees it
                var plain = new RM_WallReachMath.KindsSnapshot();
                for (int round = 0; round < 4; round++)
                {
                    phase = (byte)(round % 3);
                    plain.BeginRead(round, w, h);
                    while (!plain.ReadStep(4096, kindAt, out _)) { }
                }
                Assert(plain.allocs >= 4, "negative control: no predicate, a new array per moved read (" + plain.allocs + ")");
            });

            Case("WallReach_read_protocol_never_vetoes_reachable", () =>
            {
                Assert(Replay(true, 300) == 0, "sliced reads with touches: no false NO");
                Assert(Replay(false, 300) > 0, "negative control: the replay without touches sees a false NO");
            });

            Case("WallReach_read_wiring_source_pins", () =>
            {
                string src = Src("Superdeep", "RM_WallReach.cs");
                string begin = Between(src, "private static bool BeginJob(", "private static void Publish(");
                string beginHead = Between(begin, "private static bool BeginJob(", "private static bool StartFlood(");
                Assert(!beginHead.Contains("Inputs(") && !beginHead.Contains("Kinds("), "BeginJob reads no map: no Inputs/Kinds before the flood");
                Assert(beginHead.Contains("st.kinds.BeginRead(stamp, w, h);") && beginHead.Contains("st.kinds.CurrentFor(stamp, w, h)"),
                    "BeginJob begins a sliced read unless the kinds are current");
                string tick = Between(src, "private static void TickOwned(Map map, MapState st, bool paused, bool drain)", "private static void CountRebuildCause(");
                Assert(tick.Contains("st.kinds.ReadStep(ReadUnits, KindFn(map), out int read)"), "the read advances in the slice loop");
                Assert(!tick.Contains("new Dictionary<RM_PocketGrid"), "the per-tick views dictionary is reused");
                Assert(tick.Contains("ReadPartsMoved(st, e)"), "a read whose non-wall stamp parts moved is dropped");
                string flush = Between(src, "private static void FlushDeltas(Map map, MapState st)", "/// <summary>REACH_WINCH_FIX_GHOST_ROAD_RETURNS");
                Assert(flush.Contains("st.kinds.Touch(work[i], kindAt);") && flush.Contains("st.kinds.RestartRead();"),
                    "flushed squares are touched; an overflow restarts the read");
                Assert(!flush.Contains("i => KindAt("), "no closure per flush");
                string walk = Between(src, "internal static void NoteWalkability(Map map, IntVec3 c, bool nowWalkable)", "private static void StaleWhileOff(");
                Assert(walk.Contains("QueueTouch(st, idx);"), "a walkability note during a read is queued for its touch");
                string barrier = Between(src, "internal static void NoteBarrier(Map map, Thing t, bool removed)", "public static void Force(Map map)");
                Assert(barrier.Contains("QueueTouch(st, "), "a barrier note during a read is queued for its touch");
                string drop = Between(src, "private static void DropJob(MapState st, Entry e)", "private static double MsSince(");
                Assert(drop.Contains("st.kinds.AbortRead();"), "a dropped job drops its read");
                string kinds = Between(src, "private static byte[] Kinds(Map map, MapState st, long stamp)", "private static byte KindAt(Map map,");
                Assert(kinds.Contains("AbortActiveRead(st);"), "a whole read in a query drops the sliced read in flight");
                Assert(src.Contains("kinds.inUse = "), "the snapshot knows which arrays labellings hold");
            });
        }

        private sealed class SimEntry
        {
            public RM_WallReachMath.LabelSlot slot = new RM_WallReachMath.LabelSlot();
            public int cls, coverGen = -1, jobGen;
            public long stamp = -1, jobStamp;
            public int builtTick = -1000;
            public bool reading;
        }

        /// <summary>RM_WallReach's protocol on a simulated map: a change is judged against the PUBLISHED snapshot (the
        /// generation moves only when the square's kind differs from it; a wall in it now open is a breach and moves the unsafe
        /// generation), and is queued for a touch while a read is in flight; a job captures the unsafe generation, then the
        /// stamp, reads the kinds a slice at a time unless they are current, then floods a slice at a time; queries answer only
        /// from covered labels. Returns false NOs (a pair reachable on the live map vetoed).</summary>
        private static int Replay(bool touch, int trials)
        {
            var r = new Random(4412);
            int falseNo = 0;
            for (int t = 0; t < trials; t++)
            {
                int w = 5 + r.Next(9), h = 5 + r.Next(9), n = w * h;
                var live = new byte[n];
                for (int i = 0; i < n; i++) live[i] = r.Next(4) == 0 ? RM_WallReachMath.Wall : RM_WallReachMath.Open;
                var snap = new RM_WallReachMath.KindsSnapshot();
                Func<int, byte> kindAt = i => live[i];
                var entries = new List<SimEntry> { new SimEntry { cls = 0 }, new SimEntry { cls = 1 } };
                snap.inUse = a =>
                {
                    foreach (SimEntry e in entries)
                    {
                        if (ReferenceEquals(e.slot.builtKinds, a) || e.slot.job != null && ReferenceEquals(e.slot.job.kinds, a)) return true;
                    }
                    return false;
                };
                int[] queue = new int[n];
                var pending = new List<int>();
                var hot = new List<int>();
                long version = 0;
                int unsafeGen = 0;
                SimEntry active = null;
                for (int tick = 0; tick < 120; tick++)
                {
                    // changes between ticks, judged against the published snapshot (NoteWalkability's rule)
                    int edits = r.Next(3);
                    for (int k = 0; k < edits; k++)
                    {
                        int c = hot.Count > 0 && r.Next(2) == 0 ? hot[r.Next(hot.Count)] : r.Next(n);
                        if (hot.Count < 6) hot.Add(c);
                        byte now = live[c] == RM_WallReachMath.Wall ? RM_WallReachMath.Open : RM_WallReachMath.Wall;
                        live[c] = now;
                        byte[] pub = snap.published;
                        if (pub == null || pub[c] != now) version++;
                        if (pub != null && pub[c] == RM_WallReachMath.Wall && now != RM_WallReachMath.Wall) unsafeGen++;
                        if (snap.Reading) pending.Add(c);
                    }
                    // FlushDeltas: touch the queued squares
                    if (touch) foreach (int c in pending) snap.Touch(c, kindAt);
                    pending.Clear();
                    int gen = unsafeGen;
                    long stamp = version;
                    foreach (SimEntry e in entries)
                    {
                        if (e.stamp == stamp)
                        {
                            if (active == e) { e.slot.Drop(); snap.AbortRead(); e.reading = false; active = null; }
                            e.coverGen = gen;
                        }
                    }
                    var due = new List<SimEntry>();
                    foreach (SimEntry e in entries)
                    {
                        if (e.stamp != stamp && active != e
                            && RM_WallReachMath.RebuildDue(true, !RM_WallReachMath.Covers(e.coverGen, gen), false, tick, e.builtTick, 6)) due.Add(e);
                    }
                    due.Sort((a, b) => a.builtTick.CompareTo(b.builtTick));
                    int left = 1 + r.Next(n);
                    while (left > 0)
                    {
                        if (active == null)
                        {
                            if (due.Count == 0) break;
                            SimEntry e = due[0];
                            due.RemoveAt(0);
                            e.jobGen = gen;
                            e.jobStamp = stamp;
                            active = e;
                            if (!snap.CurrentFor(stamp, w, h))
                            {
                                snap.BeginRead(stamp, w, h);
                                e.reading = true;
                                continue;
                            }
                            if (!StartFlood(e, snap, w, h, queue, tick)) active = null;
                            continue;
                        }
                        if (active.reading)
                        {
                            bool read = snap.ReadStep(Math.Min(left, 1 + r.Next(n / 2)), kindAt, out int got);
                            left -= Math.Max(1, got);
                            if (read)
                            {
                                active.reading = false;
                                if (!StartFlood(active, snap, w, h, queue, tick)) active = null;
                            }
                            continue;
                        }
                        if (active.slot.Advance(left, out int spent))
                        {
                            active.stamp = active.jobStamp; active.coverGen = active.jobGen; active.builtTick = tick;
                            active = null;
                        }
                        left -= Math.Max(1, spent);
                    }
                    // queries against the live map, mid-read and mid-flood included
                    foreach (SimEntry e in entries)
                    {
                        RM_WallReachMath.Labels l = e.slot.labels;
                        if (l == null || !RM_WallReachMath.Covers(e.coverGen, unsafeGen)) continue;
                        var tl = RM_WallReachMath.Label(live, null, w, h, 0, e.cls);
                        for (int q = 0; q < 12; q++)
                        {
                            int a = r.Next(n), b = r.Next(n);
                            if (tl.label[a] < 0 || tl.label[a] != tl.label[b]) continue;
                            if (RM_WallReachMath.Vetoed(l.At(a), new[] { l.At(b) }, null)) falseNo++;
                        }
                    }
                }
            }
            return falseNo;
        }

        /// <summary>The flood begins from the published kinds; a skip (inputs of the published labelling) publishes at once.</summary>
        private static bool StartFlood(SimEntry e, RM_WallReachMath.KindsSnapshot snap, int w, int h, int[] queue, int tick)
        {
            if (e.slot.Begin(snap.published, null, null, w, h, 0, e.cls, queue)) return true;
            e.stamp = e.jobStamp; e.coverGen = e.jobGen; e.builtTick = tick;
            return false;
        }
    }
}
