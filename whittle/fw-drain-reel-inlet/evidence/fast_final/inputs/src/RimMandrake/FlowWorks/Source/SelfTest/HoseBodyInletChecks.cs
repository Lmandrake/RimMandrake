// REEL_BODY_INLET_FIX_SKIPS_DEPTH_RULES: production Pick must rank reachable contacts, not accept a footprint then
// return its unreachable first edge cell. Engine-side BandAt/OccupiedRect are exercised by the retained adapter and live proof.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;
namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseBodyInletChecks
    {
        private static void Assert(bool ok, string why) { if (!ok) throw new Exception(why); }
        public static void Run(Action<string, Action> Case)
        {
            Case("ReelBodyInlet_multicell_contacts_all_sides", () =>
            {
                var reel = new HoseReelRect(10, 10, 3, 2);
                foreach (Cell side in HosePortRule.SideOrder)
                {
                    List<Cell> edge = reel.EdgeCells(side);
                    Cell first = edge[0] + side, last = edge[edge.Count - 1] + side;
                    var neighbour = side.X != 0
                        ? new HosePortCandidate(first.X, first.Z, 1, reel.H, HosePortKind.Tank)
                        : new HosePortCandidate(first.X, first.Z, reel.W, 1, HosePortKind.Tank);
                    var cands = new[] { neighbour };
                    var valid = new HashSet<Cell> { last };
                    Assert(HosePortRule.Pick(reel, cands, out Cell s, out Cell c, valid) == 0
                        && s.Equals(side) && c.Equals(last), "must select later valid contact: " + side);
                    valid.Clear();
                    Assert(HosePortRule.Pick(reel, cands, out _, out _, valid) == -1, "sheer wall has no contact");
                    Assert(HosePortRule.Pick(reel, cands, out _, out c) == 0 && c.Equals(first), "unfiltered caller keeps old choice");
                }
            });
            Case("ReelBodyInlet_filtered_oracle", () =>
            {
                var rng = new Random(7919);
                for (int trial = 0; trial < 300; trial++)
                {
                    var reel = new HoseReelRect(10, 10, rng.Next(1, 5), rng.Next(1, 5));
                    var cands = new List<HosePortCandidate>();
                    for (int j = 0; j < 8; j++) cands.Add(new HosePortCandidate(rng.Next(6, 17), rng.Next(6, 17),
                        rng.Next(1, 5), rng.Next(1, 5), (HosePortKind)rng.Next(0, 4)));
                    var valid = new HashSet<Cell>();
                    foreach (Cell c in reel.Perimeter()) if (rng.Next(2) == 0) valid.Add(c);
                    int best = -1, rank = int.MaxValue; Cell wantSide = new Cell(), wantCell = new Cell();
                    for (int j = 0; j < cands.Count; j++)
                    {
                        var c = cands[j];
                        if (c.Kind == HosePortKind.None || reel.Overlaps(c)) continue;
                        for (int si = 0; si < HosePortRule.SideOrder.Length; si++)
                        {
                            Cell side = HosePortRule.SideOrder[si];
                            var edge = reel.EdgeCells(side);
                            for (int k = 0; k < edge.Count; k++)
                            {
                                Cell n = edge[k] + side;
                                if (!valid.Contains(n) || !c.Contains(n)) continue;
                                int r = ((int)c.Kind * 8 + si) * 64 + k;
                                if (r < rank) { best = j; rank = r; wantSide = side; wantCell = n; }
                            }
                        }
                    }
                    int got = HosePortRule.Pick(reel, cands, out Cell gs, out Cell gc, valid);
                    Assert(got == best && gs.Equals(wantSide) && gc.Equals(wantCell), "filtered edge-list oracle trial " + trial);
                }
            });
            Case("ReelBodyInlet_filtered_pick_no_alloc", () =>
            {
                var reel = new HoseReelRect(10, 10, 3, 2);
                var cands = new[] { new HosePortCandidate(13, 10, 2, 2, HosePortKind.Tank) };
                var valid = new HashSet<Cell> { new Cell(13, 11) };
                for (int i = 0; i < 100; i++) HosePortRule.Pick(reel, cands, out _, out _, valid);
                long before = GC.GetAllocatedBytesForCurrentThread();
                for (int i = 0; i < 1000; i++) HosePortRule.Pick(reel, cands, out _, out _, valid);
                long allocated = GC.GetAllocatedBytesForCurrentThread() - before;
                Assert(allocated == 0, "filtered Pick allocated " + allocated);
            });
            Case("ReelBodyInlet_reachable_candidate_ranking", () =>
            {
                var reel = new HoseReelRect(10, 10, 3, 2);
                var east = new Cell(13, 10); var north = new Cell(11, 12); var west = new Cell(9, 11);
                var cands = new[] {
                    new HosePortCandidate(13,10,1,1,HosePortKind.Pipe),
                    new HosePortCandidate(11,12,1,1,HosePortKind.Tank),
                    new HosePortCandidate(9,11,1,1,HosePortKind.Pipe) };
                var valid = new HashSet<Cell> { north, west };
                Assert(HosePortRule.Pick(reel, cands, out _, out Cell c, valid) == 2 && c.Equals(west), "valid pipe beats tank");
                valid.Remove(west);
                Assert(HosePortRule.Pick(reel, cands, out _, out _, valid) == 1, "invalid preferred pipe falls back to tank");
                valid.Add(east);
                Assert(HosePortRule.Pick(reel, cands, out _, out _, valid) == 0, "restored pipe wins");
                var ties = new[] { cands[0], cands[0] };
                Assert(HosePortRule.Pick(reel, ties, out _, out _, valid) == 0, "equal ranks preserve caller's id ordering");
                var excluded = new[] { new HosePortCandidate(12,11,2,2,HosePortKind.Pipe), new HosePortCandidate(13,12,1,1,HosePortKind.Pipe) };
                Assert(HosePortRule.Pick(reel, excluded, out _, out _, valid) == -1, "overlaps/corners never become contacts");
            });
        }
    }
}
