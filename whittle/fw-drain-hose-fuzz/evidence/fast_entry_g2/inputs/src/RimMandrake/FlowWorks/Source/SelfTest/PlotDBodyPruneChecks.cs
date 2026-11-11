// PLOT_D_BODY_PRUNE_STALE_SEA: a dev plot reset (RM_NorthstarProofs.ProofResetRect) releases every body's claim on its rect.
// Live 2026-10-24 (extension_proof toggle_recession, D:\ClaudeWork\scratch\triage\c5.json): a fresh 5x5 pond painted on plot D
// read back as limitless body 9 (17,434 cells, truncated: the map's sea) with no water near it. The golden save holds bodies
// 1-4 only, so the claim was made in-session: RM_FlowKernel.CollectBody joins ANY claimed 8-neighbour, a Soil-repainted one
// included, and the plot reset repainted Soil and filled dug cells back in without releasing a single claim.
// Proven here: the kernel reproduces the join and the release undoes it (Verse-free), and the production source wires the
// release into ProofResetRect after its fill-in loop. NOT proven here: the live map (live-proof A1 in
// infrastructure/state/live_proofs/PLOT_D_BODY_PRUNE_STALE_SEA.txt).
using System;
using System.Collections.Generic;
using System.IO;
using RR = RimMandrake.FlowWorks.SelfTest.ReleaseRectHarness;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PlotDBodyPruneChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private const int W = 14, H = 10, StaleSea = 9;

        /// <summary>A 5x5 pond at (5..9, 2..6) on a W x H map; the sea's stale claims sit on dry ground at (4,4), just west of
        /// it, and on a real far square (13,9) outside the plot. Returns the walk's owned id and footprint size.</summary>
        private static (int owned, int found) WalkPond(IDictionary<int, int> claims)
        {
            Func<int, bool> pond = i => { int x = i % W, z = i / W; return x >= 5 && x <= 9 && z >= 2 && z <= 6; };
            var found = new List<int>();
            int owned = RM_FlowKernel.CollectBody(W, H, 4 * W + 7, pond, i => claims.TryGetValue(i, out int id) ? id : -1, 4000,
                found, new List<int>(), new HashSet<int>(), out bool _, out bool _);
            return (owned, found.Count);
        }

        private static Dictionary<int, int> StaleClaims() =>
            new Dictionary<int, int> { { 4 * W + 4, StaleSea }, { 9 * W + 13, StaleSea } };

        private static string Between(string src, string start, string end)
        {
            int i = src.IndexOf(start, StringComparison.Ordinal);
            Assert(i >= 0, "marker present: " + start);
            int j = src.IndexOf(end, i + start.Length, StringComparison.Ordinal);
            Assert(j >= 0, "end marker present: " + end);
            return src.Substring(i, j - i);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("PLOT_D_BODY_PRUNE: a stale claim on a dry square beside a fresh pond makes the walk join that far body", () =>
            {
                var (owned, _) = WalkPond(StaleClaims());
                Assert(owned == StaleSea, "the defect reproduces: the pond joins body " + StaleSea + " (got " + owned + ")");
            });

            Case("PLOT_D_BODY_PRUNE: releasing the plot rect's claims lets the same pond form a fresh 25-square body", () =>
            {
                var claims = StaleClaims();
                int released = RM_FlowKernel.ReleaseClaimsInRect(claims, W, H, 1, 0, 11, 9);   // the plot + buffer, not (13,9)
                var (owned, found) = WalkPond(claims);
                Assert(released == 1, "one claim inside the rect released (got " + released + ")");
                Assert(claims.ContainsKey(9 * W + 13), "the claim outside the rect is kept");
                Assert(owned == -1 && found == 25, "a fresh body of 25 squares (owned " + owned + ", found " + found + ")");
            });

            Case("PLOT_D_BODY_PRUNE: the release clips a rect hanging off the map and counts only real claims", () =>
            {
                var claims = new Dictionary<int, int> { { 0, 1 }, { 1, 1 }, { W * H - 1, 2 } };
                int released = RM_FlowKernel.ReleaseClaimsInRect(claims, W, H, -5, -5, 7, 6);
                Assert(released == 2 && claims.Count == 1 && claims.ContainsKey(W * H - 1),
                    "(0,0) and (1,0) released, the far corner kept (released " + released + ", left " + claims.Count + ")");
            });

            Case("PLOT_D_BODY_PRUNE: ProofResetRect releases body claims AFTER its fill-in loop and reports released=", () =>
            {
                string s = RiverSwitchFlipChecks.Src(Path.Combine("RM_NorthstarProofs.cs"));
                string body = Between(s, "public static string ProofResetRect(string arg)", "private static Hose.CompHoseReel ReelAt(");
                int fill = body.IndexOf("eng.FillIn(c);", StringComparison.Ordinal);
                int release = body.IndexOf("eng.Stock?.ReleaseRect(map, r, eng, out dropped)", StringComparison.Ordinal);
                int ret = body.IndexOf("return \"RESET cells=\"", StringComparison.Ordinal);
                Assert(fill >= 0 && release > fill && ret > release,
                    "FillIn reattaches dug squares to their pond, so the release runs after it and before the reply");
                Assert(body.Contains("\" released=\" + released") && body.Contains("\" left=\" + left;"),
                    "the reply names released= and still ENDS with left= (extensions._prep_plot checks endswith left=0)");
            });

            Case("PLOT_D_BODY_PRUNE: RM_LiquidStock.ReleaseRect clears footprint, receded list and index, and drops an emptied body", () =>
            {
                string s = RiverSwitchFlipChecks.Src(Path.Combine("RM_LiquidStock.cs"));
                string body = Between(s, "public int ReleaseRect(Map map, CellRect r, RM_MapComponent_Excavation owner, out int dropped)",
                    "/// <summary>Ruling 6's other half");
                foreach (string need in new[] {
                    "body.cells.RemoveAll(c => r.Contains(c));", "body.receded.RemoveAll(c => r.Contains(c));",
                    "bodies.RemoveAt(b); byId.Remove(body.id);",
                    "body.capacity = RM_BedMath.CapacityForBeds(unit, BedSum(body, owner));",
                    "RM_FlowKernel.ReleaseClaimsInRect(cellToBody, map.Size.x, map.Size.z, r.minX, r.minZ, r.Width, r.Height);" })
                {
                    Assert(body.Contains(need), "ReleaseRect holds: " + need);
                }
            });

            Case("PLOT_D_BODY_PRUNE: the production ReleaseRect, run, empties the rect of footprint, receded and claims", () =>
            {
                // Map 14x10, plot rect (2..8, 1..7). Body 5: a pond wholly inside (dropped). Body 6: a pond straddling the
                // rect's east edge (kept, shrunk, re-sized). Body 9: the limitless sea with one footprint square inside and
                // a truncated far claim inside that is in the index only. A claim of 9 outside the rect stays.
                var h = new RR.StockHarness();
                var rect = new RR.CellRect(2, 1, 7, 7);
                var inside = new List<RR.IntVec3>();
                for (int x = 3; x <= 5; x++) for (int z = 2; z <= 4; z++) inside.Add(new RR.IntVec3(x, z));
                h.Add(5, false, 2f, inside, W);
                var straddle = new List<RR.IntVec3>();
                for (int x = 7; x <= 10; x++) straddle.Add(new RR.IntVec3(x, 6));
                RR.RM_LiquidBody b6 = h.Add(6, false, 2f, straddle, W);
                b6.capacity = 8f; b6.stock = 8f;
                b6.receded.Add(new RR.IntVec3(7, 6)); b6.receded.Add(new RR.IntVec3(10, 6));
                RR.RM_LiquidBody sea = h.Add(StaleSea, true, 0f, new[] { new RR.IntVec3(2, 7), new RR.IntVec3(13, 9) }, W);
                sea.receded.Add(new RR.IntVec3(2, 7));
                h.cellToBody[4 * W + 6] = StaleSea;                        // truncated: indexed, not in the footprint list
                var owner = new RR.RM_MapComponent_Excavation();
                int released = h.ReleaseRect(new RR.Map(W, H), rect, owner, out int dropped);

                Assert(released == 9 + 2 + 1, "released = 9 + 2 + 1 footprint squares (got " + released + ")");
                Assert(dropped == 1 && !h.byId.ContainsKey(5) && h.bodies.Count == 2, "the emptied pond is dropped (dropped "
                    + dropped + ", bodies " + h.bodies.Count + ")");
                foreach (RR.RM_LiquidBody b in h.bodies)
                {
                    foreach (RR.IntVec3 c in b.cells) Assert(!rect.Contains(c), "body " + b.id + " still holds " + c.x + "," + c.z);
                    foreach (RR.IntVec3 c in b.receded) Assert(!rect.Contains(c), "body " + b.id + " still recedes " + c.x + "," + c.z);
                }
                foreach (int k in h.cellToBody.Keys)
                {
                    Assert(!rect.Contains(new RR.IntVec3(k % W, k / W)), "a claim survives in the rect at " + (k % W) + "," + (k / W));
                }
                Assert(h.cellToBody.TryGetValue(9 * W + 13, out int far) && far == StaleSea, "the sea's claim outside is kept");
                Assert(h.cellToBody.TryGetValue(6 * W + 9, out int e6) && e6 == 6 && h.cellToBody.ContainsKey(6 * W + 10),
                    "the straddling pond keeps its squares outside the rect");
                Assert(b6.cells.Count == 2 && b6.receded.Count == 1, "pond 6: 2 squares, 1 receded left");
                float cap = RM_BedMath.CapacityForBeds(2f, 2);
                Assert(Math.Abs(b6.capacity - cap) < 1e-4f && b6.capacity < 8f && b6.stock <= b6.capacity + 1e-4f,
                    "pond 6 re-sized to its 2 beds and its stock clamped (capacity " + b6.capacity + " want " + cap + ", stock " + b6.stock + ")");
                Assert(sea.cells.Count == 1 && sea.limitless, "the sea keeps its far square, still limitless");
            });

            Case("PLOT_D_BODY_PRUNE: after the production ReleaseRect the pond walk forms a fresh body, not the sea", () =>
            {
                var h = new RR.StockHarness();
                h.Add(StaleSea, true, 0f, new[] { new RR.IntVec3(4, 4), new RR.IntVec3(13, 9) }, W);
                h.ReleaseRect(new RR.Map(W, H), new RR.CellRect(1, 0, 11, 9), new RR.RM_MapComponent_Excavation(), out int _);
                var (owned, found) = WalkPond(h.cellToBody);
                Assert(owned == -1 && found == 25, "a fresh body of 25 squares (owned " + owned + ", found " + found + ")");
            });

            Case("PLOT_D_BODY_PRUNE: the production ReleaseRect rebuilds a dirty index before it releases", () =>
            {
                var h = new RR.StockHarness();
                h.Add(5, false, 1f, new[] { new RR.IntVec3(3, 3) }, W);
                h.cellToBody.Clear();
                h.indexDirty = true;
                h.ReleaseRect(new RR.Map(W, H), new RR.CellRect(0, 0, W, H), new RR.RM_MapComponent_Excavation(), out int dropped);
                Assert(h.rebuilds == 1 && dropped == 1 && h.cellToBody.Count == 0, "rebuilt once, body dropped, index empty (rebuilds "
                    + h.rebuilds + ", dropped " + dropped + ", left " + h.cellToBody.Count + ")");
            });

            Case("PLOT_D_BODY_PRUNE: only the dev reset calls ReleaseRect (play keeps ruling 16's sticky classification)", () =>
            {
                string root = Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_LiquidStock.cs"));
                var callers = new List<string>();
                foreach (string f in Directory.GetFiles(root, "*.cs", SearchOption.AllDirectories))
                {
                    if (f.Contains(Path.DirectorySeparatorChar + "SelfTest" + Path.DirectorySeparatorChar)
                        || f.Contains(Path.DirectorySeparatorChar + "obj" + Path.DirectorySeparatorChar))
                    {
                        continue;
                    }
                    if (File.ReadAllText(f).Contains(".ReleaseRect("))
                    {
                        callers.Add(Path.GetFileName(f));
                    }
                }
                Assert(callers.Count == 1 && callers[0] == "RM_NorthstarProofs.cs",
                    "callers of ReleaseRect: " + string.Join(", ", callers));
            });
        }
    }
}
