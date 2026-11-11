// HOSES_MAP1_DIAGNOSE_TICK_STALLS (cycle 2) and WALLREACH_BUILD_DIAGNOSE_RAIN_TAIL.
// Hoses: with the band pass allocation-free (HoseBandsApplyChecks), map1's hose tick still took 80-127 ms full-GC pauses in
// HoseEnds.Read (FreeEndOf -> HosePorts.FindAt -> RawFindAt) and CheckReplan. Mono's collector is full on every collection and
// the thread whose allocation crosses the threshold pays it, so every byte the hose tick allocates is a ticket in that draw.
// RawFind / RawFindAt allocated a perimeter list, two candidate lists and (ById) an index list, a closure and two copies on
// every call (~4 a tick on map1). These checks hold them to reused scratch, hold PerimeterInto to Perimeter's order, and hold
// the hose tick to an own-work vs GC-pause split (ProofTickSplit) so a stall is attributed, not guessed.
// WallReach: the rain tail was Kinds' whole-map pass (9.7 ms of an 11.8 ms build in RAIN_B2): per square IsDeepSwimCell
// scanned the thing list for a deck, rebuilt the cell from its index and looked the engine up. The index rule reads the
// terrain and the dug-swim set first and scans for a deck only on a square that would swim; the old rule stays as the oracle
// RM_WallReach.ProofKinds compares against live.
using System;
using System.Collections.Generic;
using System.IO;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseTickAllocChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Body(string src, string start, string end)
        {
            int i = src.IndexOf(start, StringComparison.Ordinal);
            Assert(i >= 0, "marker present: " + start);
            int j = src.IndexOf(end, i + start.Length, StringComparison.Ordinal);
            Assert(j >= 0, "end marker present: " + end);
            return src.Substring(i, j - i);
        }

        /// <summary>The pre-fix HosePortRule.Pick, kept as the oracle: the edge cells come from HoseReelRect.EdgeCells.</summary>
        private static int PickByEdgeLists(HoseReelRect reel, IList<HosePortCandidate> cands, out Cell side, out Cell contact)
        {
            side = new Cell(0, 0);
            contact = new Cell(0, 0);
            int best = -1, bestRank = int.MaxValue;
            for (int i = 0; i < cands.Count; i++)
            {
                HosePortCandidate c = cands[i];
                if (c.Kind == HosePortKind.None || reel.Overlaps(c)) continue;
                for (int s = 0; s < HosePortRule.SideOrder.Length; s++)
                {
                    List<Cell> edge = reel.EdgeCells(HosePortRule.SideOrder[s]);
                    for (int k = 0; k < edge.Count; k++)
                    {
                        Cell n = edge[k] + HosePortRule.SideOrder[s];
                        if (!c.Contains(n)) continue;
                        int rank = ((int)c.Kind * 8 + s) * 64 + k;
                        if (rank < bestRank) { bestRank = rank; best = i; side = HosePortRule.SideOrder[s]; contact = n; }
                    }
                }
            }
            return best;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("HOSEPORTS_RAWFIND_NO_PER_CALL_ALLOC", () =>
            {
                string src = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "HosePorts.cs"));
                string raw = Body(src, "private static Thing RawFind(CompHoseReel r,", "/// <summary>Carry stage S4");
                string rawAt = Body(src, "private static Thing RawFindAt(Map map,", "// end RawFindAt");
                foreach (var (name, b) in new[] { ("RawFind", raw), ("RawFindAt", rawAt) })
                {
                    Assert(!b.Contains("new List<"), name + " allocates its candidate lists per call");
                    Assert(!b.Contains(".Perimeter()"), name + " allocates the perimeter list per call (use PerimeterInto)");
                    Assert(b.Contains("PerimeterInto("), name + " reads the perimeter into scratch");
                }
                string byId = Body(src, "private static void ById(List<Thing> things, List<HosePortCandidate> cands)", "internal static int FindCalls;");
                Assert(byId.Contains("if (things.Count < 2) return;"), "ById sorts only when there is something to order");
                // HOSE_TICK_REBUILD_ZERO_ALLOC: two candidates beside one reel (a pump by a pipe) allocated an index list, a
                // closure and two copies per Find; the order is now built in place
                Assert(!byId.Contains("new List<") && !byId.Contains("=>") && !byId.Contains(".Sort("), "ById allocates to order two or more candidates");
            });
            // HOSE_TICK_REBUILD_ZERO_ALLOC: Find / FindAt on a pump runs the one-port-per-side gate, which allocated an id list,
            // its ToArray copy and (foreach over the IReadOnlyList) a boxed enumerator on every call -- the 60-tick Port() and
            // free-end refreshes of every pump-coupled reel. The gate reads into scratch and HoseMayTake takes the scratch.
            Case("HOSEPORTS_PUMPSIDETAKES_NO_PER_CALL_ALLOC", () =>
            {
                string src = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "HosePorts.cs"));
                string gate = Body(src, "private static bool PumpSideTakes(Thing pump, int side, CompHoseReel self)", "/// <summary>The geometric coupling of a free end");
                Assert(!gate.Contains("new List<"), "PumpSideTakes allocates its id list per call");
                Assert(!gate.Contains(".ToArray()"), "PumpSideTakes copies its id list per call");
                Assert(!gate.Contains("foreach"), "PumpSideTakes enumerates the reels through an interface (a boxed enumerator per call)");
                // the list overload answers as the array one, and allocates nothing warm
                var ids = new List<int>();
                var cases = new (int side, int id, int[] others)[]
                {
                    (2, 50, new int[0]), (-1, 40, new int[0]), (2, 50, new[] { 40 }), (2, 40, new[] { 50 }), (1, 40, new[] { 40, 60 }), (3, 40, new[] { 60, 39 }),
                };
                foreach (var c in cases)
                {
                    ids.Clear(); ids.AddRange(c.others);
                    Assert(RimMandrake.FlowWorks.Machinery.RM_PumpPortMath.HoseMayTake(c.side, c.id, ids) == RimMandrake.FlowWorks.Machinery.RM_PumpPortMath.HoseMayTake(c.side, c.id, c.others),
                        $"HoseMayTake(list) differs from HoseMayTake(array) at side {c.side} id {c.id}");
                }
                ids.Clear(); ids.Add(60); ids.Add(70);
                bool sink = false;
                for (int i = 0; i < 100; i++) sink ^= RimMandrake.FlowWorks.Machinery.RM_PumpPortMath.HoseMayTake(2, 40, ids);
                long b0 = GC.GetAllocatedBytesForCurrentThread();
                for (int i = 0; i < 1000; i++) sink ^= RimMandrake.FlowWorks.Machinery.RM_PumpPortMath.HoseMayTake(2, 40 + (i & 1) * 30, ids);
                long bytes = GC.GetAllocatedBytesForCurrentThread() - b0;
                Assert(bytes == 0, $"HoseMayTake(list) allocates {bytes} B over 1000 calls");
                // the instrument can see: a known allocation registers
                long k0 = GC.GetAllocatedBytesForCurrentThread();
                var probe = new int[256];
                Assert(GC.GetAllocatedBytesForCurrentThread() - k0 >= 1024 && probe.Length == 256, "the allocation counter sees a 1 KB array");
            });
            // HOSE_WATCH_ALLOC_HUNT_GC_IN_TICK: after the zero-alloc rebuild a full GC still landed in the hose watch phase
            // (HoseEnds.Read -> HosePorts.FindAt, CompHoseReel.Port -> HosePorts.Find). The Verse-free tail both share is
            // HosePortRule.Pick, which built a List<Cell> of the reel's edge cells for every side of every candidate (four lists a
            // candidate, every Port() and free-end refresh, plus PumpSideTakes' nested finds). Pick walks the edge in place now,
            // in the same ascending order, so its answer (index, side, contact) equals the list-built rule on every input.
            Case("HOSEPORTRULE_PICK_NO_PER_CALL_ALLOC", () =>
            {
                var rng = new Random(1028);
                var cands = new List<HosePortCandidate>();
                int checkedPicks = 0, hits = 0;
                for (int trial = 0; trial < 4000; trial++)
                {
                    var reel = new HoseReelRect(rng.Next(-2, 3), rng.Next(-2, 3), rng.Next(1, 4), rng.Next(1, 4));
                    cands.Clear();
                    int n = rng.Next(0, 5);
                    for (int i = 0; i < n; i++)
                        cands.Add(new HosePortCandidate(rng.Next(-5, 6), rng.Next(-5, 6), rng.Next(1, 4), rng.Next(1, 4), (HosePortKind)rng.Next(0, 5)));
                    int want = PickByEdgeLists(reel, cands, out Cell ws, out Cell wc);
                    int got = HosePortRule.Pick(reel, cands, out Cell gs, out Cell gc);
                    Assert(got == want && gs.X == ws.X && gs.Z == ws.Z && gc.X == wc.X && gc.Z == wc.Z,
                        $"Pick differs from the edge-list rule at trial {trial}: got {got} ({gs.X},{gs.Z})/({gc.X},{gc.Z}) want {want} ({ws.X},{ws.Z})/({wc.X},{wc.Z})");
                    checkedPicks++;
                    if (want >= 0) hits++;
                }
                Assert(hits > 500 && hits < checkedPicks - 500, $"the random inputs exercise both outcomes ({hits} picks of {checkedPicks})");
                // a 2x2 reel with a pipe east and a tank north: the pump-side and free-end refresh shape
                var reel2 = new HoseReelRect(10, 10, 2, 2);
                cands.Clear();
                cands.Add(new HosePortCandidate(12, 10, 1, 1, HosePortKind.Pipe));
                cands.Add(new HosePortCandidate(10, 12, 2, 2, HosePortKind.Tank));
                int sink = 0;
                for (int i = 0; i < 100; i++) sink += HosePortRule.Pick(reel2, cands, out _, out _);
                long b0 = GC.GetAllocatedBytesForCurrentThread();
                for (int i = 0; i < 1000; i++) sink += HosePortRule.Pick(reel2, cands, out _, out _);
                long bytes = GC.GetAllocatedBytesForCurrentThread() - b0;
                Assert(sink == 0, "the pipe east wins (index 0)");
                Assert(bytes == 0, $"HosePortRule.Pick allocates {bytes} B over 1000 calls");
                // the instrument can see: the list-built rule allocates on the same input
                long k0 = GC.GetAllocatedBytesForCurrentThread();
                for (int i = 0; i < 10; i++) sink += PickByEdgeLists(reel2, cands, out _, out _);
                Assert(GC.GetAllocatedBytesForCurrentThread() - k0 > 0, "the allocation counter sees the edge-list rule's lists");
            });
            Case("HOSEREELRECT_PERIMETERINTO_EQUALS_PERIMETER", () =>
            {
                var scratch = new List<Cell> { new Cell(99, 99) };
                foreach (var rc in new[] { new HoseReelRect(0, 0, 1, 1), new HoseReelRect(5, 7, 2, 2), new HoseReelRect(-3, 4, 3, 1), new HoseReelRect(10, 10, 1, 4) })
                {
                    List<Cell> want = rc.Perimeter();
                    rc.PerimeterInto(scratch);
                    Assert(scratch.Count == want.Count, "PerimeterInto count " + scratch.Count + " != " + want.Count);
                    for (int i = 0; i < want.Count; i++)
                        Assert(scratch[i].X == want[i].X && scratch[i].Z == want[i].Z, "PerimeterInto order differs at " + i);
                }
            });
            Case("HOSES_TICK_SPLITS_OWN_WORK_FROM_GC", () =>
            {
                string src = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                string tick = Body(src, "public override void MapComponentTick()", "private void TickBody()");
                Assert(tick.Contains("GC.CollectionCount(0)") && tick.Contains("TickBody();") && tick.Contains("GC.GetTotalMemory(false)"),
                    "the hose tick records whether a collection landed in it and what it allocated");
                Assert(src.Contains("public static string ProofTickSplit(string arg)"), "the split is readable live");
            });
            Case("WALLREACH_KINDS_SWIM_BY_INDEX", () =>
            {
                string src = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_WallReach.cs"));
                string kindAt = Body(src, "private static byte KindAt(Map map,", "private static byte KindAtLegacy(");
                Assert(!kindAt.Contains("IsDeepSwimCell("), "KindAt scans every square's things for a deck (IsDeepSwimCell)");
                Assert(kindAt.Contains("IsDeepSwimIndex(map, ex, i)"), "KindAt reads swim by index with the engine passed in");
                string kinds = Body(src, "private static byte[] Kinds(Map map, MapState st, long stamp)", "private static byte KindAt(Map map,");
                int eng = kinds.IndexOf("RM_SuperdeepTrap.EngineOf(map)", StringComparison.Ordinal);
                int loop = kinds.IndexOf("for (int i = 0; i < n; i++)", StringComparison.Ordinal);
                Assert(eng >= 0 && loop > eng, "Kinds looks the engine up once, before the per-square loop");
                string probe = Body(src, "public static string ProofKinds(string arg)", "// end ProofKinds");
                Assert(probe.Contains("KindAtLegacy(") && probe.Contains("KindAt("), "the probe compares the old rule with the new square by square");
                string legacy = Body(src, "private static byte KindAtLegacy(", "private static void Build(");
                Assert(legacy.Contains("IsDeepSwimCell(map, map.cellIndices.IndexToCell(i))"), "the oracle is the pre-fix rule");
                string swim = Body(RiverSwitchFlipChecks.Src(Path.Combine("Swimming", "RM_Swim.cs")),
                    "public static bool IsDeepSwimIndex(Map map, RM_MapComponent_Excavation ex, int i)", "// end IsDeepSwimIndex");
                int terr = swim.IndexOf("IsSwimTerrain(", StringComparison.Ordinal), dug = swim.IndexOf("IsDugSwimIndex(i)", StringComparison.Ordinal),
                    deck = swim.IndexOf("DeckedAt(", StringComparison.Ordinal);
                Assert(terr >= 0 && dug >= 0 && deck > terr && deck > dug, "the deck scan runs only after the square is known to swim");
            });
        }
    }
}
