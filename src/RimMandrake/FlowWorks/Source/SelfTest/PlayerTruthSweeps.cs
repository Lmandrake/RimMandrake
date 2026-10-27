// PLAYER-TRUTH PILOT (owner 2026-10-26: "How do we make a system that moves towards a more realistic, sensible testing
// scheme? Can we even?"). Each case states one property a player expects, in plain words, and sweeps the WHOLE small input
// space through the production Verse-free code, so a defect is not missed just because nobody thought to try that case.
// Design: design/RimMandrake/player_truth_testing_pilot_2026-10-26.md (truth ids PT-xx match the doc's table).
// Production code under test: RM_LadderWallMath, RM_CliffMaskMath, RM_PocketGridMath, HoseReelLinkChecks.LayLink/HoseRelay,
// RM_FlowKernel (through ArrayWorld, the shipped levelling flags as LevelExactChecks.World sets them).
// NOT proven here: the Verse layers that feed these functions (RM_CliffMask filling d9 from the map, RM_ClimbJoins, the
// drawn pawn sink, the drawn hose mesh) and anything the game only shows on screen.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PlayerTruthSweeps
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>Throws with the first few failing cases and the totals; can-fail when nothing was swept.</summary>
        private static void Verdict(string truth, int swept, List<string> bad)
        {
            Assert(swept > 0, "can-fail: " + truth + " swept nothing");
            if (bad.Count > 0)
                throw new Exception(truth + ": " + bad.Count + " of " + swept + " cases fail; first: " + string.Join(" || ", bad.Take(4)));
            Console.WriteLine("    " + truth + ": " + swept + " cases, all hold");
        }

        private static Action Timed(string id, Action body)
        {
            return () =>
            {
                var sw = System.Diagnostics.Stopwatch.StartNew();
                try { body(); }
                finally { Console.WriteLine("    " + id + " took " + sw.Elapsed.TotalSeconds.ToString("0.00") + " s"); }
            };
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("PlayerTruth_PT00 the instruments can see: each sweep's check fails on an injected fault", Timed("PT00", InstrumentsSee));
            Case("PlayerTruth_PT01 a ladder hangs on a real wall: every 4-side neighbourhood x depth x placed turn", Timed("PT01", LadderHangsOnAWall));
            Case("PlayerTruth_PT02 a ladder leads up only the wall it shows, and does lead up it", Timed("PT02", LadderLeadsUpItsWall));
            Case("PlayerTruth_PT03 a ladder's wall does not depend on which way the map is turned (rotate, mirror)", Timed("PT03", LadderEquivariant));
            Case("PlayerTruth_PT04 a ladder keeps its wall on reload (resolving its own turn again gives the same wall)", Timed("PT04", LadderStable));
            Case("PlayerTruth_PT05 if you can step A->B you can step B->A (masks symmetric, every 3x3 pit 0..3 deep, K 1..3)", Timed("PT05", MaskSymmetric));
            Case("PlayerTruth_PT06 pathing and the pocket grid agree on who can reach whom (same partition)", Timed("PT06", MaskMatchesPockets));
            Case("PlayerTruth_PT07 a pit has no favourite side: turning the pit turns its walkable regions", Timed("PT07", PitNoDirectionBias));
            Case("PlayerTruth_PT08 a flat pit floor is walkable in every direction to every floor cell", Timed("PT08", FlatFloorAllDirections));
            Case("PlayerTruth_PT09 a pit too deep to climb traps you, and a ladder on any wall cell gets you out", Timed("PT09", DeepPitTrapsLadderFrees));
            Case("PlayerTruth_PT10 a hose leaves its reel along the outlet and arrives along the inlet, no end hook", Timed("PT10", HoseEndsStraight));
            Case("PlayerTruth_PT11 water poured anywhere in a pit levels across the whole pit (one surface, nothing perched)", Timed("PT11", WaterLevelsOnePour));
            Case("PlayerTruth_PT12 digging the dry half of a flooded pit lets the water flow into it", Timed("PT12", WaterLevelsAfterSecondDig));
        }

        /// <summary>A sweep that finds nothing proves something only if its check can fail. Each of the owner's five
        /// defects, injected into the same instrument, must be caught.</summary>
        private static void InstrumentsSee()
        {
            // 1 ladders: a ladder turned to face AWAY from its wall (the reversed perspective) breaks PT01's predicate
            int reversedCaught = 0, hung = 0;
            foreach (var (ladderD, placed, sideD, inB) in LadderSpace())
            {
                int r = RM_LadderWallMath.Resolve(placed, ladderD, sideD, inB);
                if (r < 0) continue;
                hung++;
                int rev = (r + 2) % 4;
                if (!(inB[rev] && sideD[rev] < ladderD)) reversedCaught++;
            }
            Assert(hung > 0 && reversedCaught > hung / 2, "probe: a reversed ladder is caught in only " + reversedCaught + " of " + hung);
            // 2 pits: drop the south step from every dug cell; PT07 (direction bias) and PT08 (flat floor) must both fire
            faultNoSouthInPits = true;
            try
            {
                bool c7 = false, c8 = false;
                try { PitNoDirectionBias(); } catch (Exception) { c7 = true; }
                try { FlatFloorAllDirections(); } catch (Exception) { c8 = true; }
                Assert(c7 && c8, "probe: a pit with no south step is caught by PT07 " + c7 + ", PT08 " + c8);
            }
            finally { faultNoSouthInPits = false; }
            // 3 hoses: a hook (straight east, then back on itself) in the last cell reads > 90 deg; a reversed inlet is caught
            var hook = new List<V2> { new V2(0, 0), new V2(1, 0), new V2(2, 0), new V2(2.3, 0), new V2(2.1, 0.25) };
            double L = Arc(hook, out double[] sh);
            Assert(Turning(hook, sh, L - 1.0, L) > 90, "probe: an end hook reads only " + Turning(hook, sh, L - 1.0, L).ToString("0") + " deg");
            HoseReelRect A = HoseReelLinkChecks.Placed(20, 20, 1), B = HoseReelLinkChecks.Placed(28, 20, 3);
            var w = new CordWorld(44, 44);
            HoseLay lay = HoseReelLinkChecks.LayLink(w, A, B, out Cell intake, out V2 end);
            Assert(lay.Ok, "probe: the reference hose was not laid (" + lay.Reason + ")");
            HoseRelay.DrawnEnd(B, intake, B.Look ?? "Scrapper", false, out V2 inward);
            double Lp = Arc(lay.Flat, out double[] sp);
            V2 h1 = (lay.Flat[lay.Flat.Count - 1] - At(lay.Flat, sp, Lp - 0.3)).Norm();
            Assert(Dot(h1, inward.Norm()) > 0.8 && Dot(h1, (-inward).Norm()) < 0, "probe: the inlet check cannot tell arriving from leaving (" + h1 + " vs " + inward + ")");
            // 4 water: deep water in one half of a pit and none in the other, unpulsed, is perched
            var lw = LevelWorld();
            var cells = new List<int> { 1 * WW + 1, 1 * WW + 2, 1 * WW + 3, 1 * WW + 4 };
            foreach (int c in cells) lw.k.depth[c] = 3;
            foreach (int c in cells.Take(2)) { lw.k.fill[c] = 3; lw.cellFluid[c] = ArrayWorld.Water; }
            Assert(Perched(lw, cells, out string where) >= 2.9, "probe: a half-full pit reads as level (" + where + ")");
        }

        // ── ladders ─────────────────────────────────────────────────────

        private const int OOB = -1;

        /// <summary>Every side state (off the map, or depth 0..4) for the four sides, every ladder depth 0..3, every placed
        /// turn (-1 = none, 0..3).</summary>
        private static IEnumerable<(int ladderD, int placed, int[] sideD, bool[] inB)> LadderSpace()
        {
            for (int code = 0; code < 6 * 6 * 6 * 6; code++)
                for (int ladderD = 0; ladderD <= 3; ladderD++)
                    for (int placed = -1; placed < 4; placed++)
                    {
                        var sideD = new int[4];
                        var inB = new bool[4];
                        int c = code;
                        for (int s = 0; s < 4; s++)
                        {
                            int v = c % 6 - 1;
                            c /= 6;
                            inB[s] = v != OOB;
                            sideD[s] = v == OOB ? ladderD : v;
                        }
                        yield return (ladderD, placed, sideD, inB);
                    }
        }

        private static string Show(int ladderD, int placed, int[] sideD, bool[] inB)
        {
            return "ladderD " + ladderD + " placed " + (placed < 0 ? "-" : "NESW"[placed].ToString()) + " sides N/E/S/W "
                + string.Join("/", Enumerable.Range(0, 4).Select(s => inB[s] ? sideD[s].ToString() : "off"));
        }

        private static void LadderHangsOnAWall()
        {
            int n = 0;
            var bad = new List<string>();
            foreach (var (ladderD, placed, sideD, inB) in LadderSpace())
            {
                n++;
                int r = RM_LadderWallMath.Resolve(placed, ladderD, sideD, inB);
                bool any = Enumerable.Range(0, 4).Any(s => inB[s] && ladderD > 0 && sideD[s] < ladderD);
                if (any != (r >= 0)) bad.Add(Show(ladderD, placed, sideD, inB) + " -> " + r + " (a wall exists: " + any + ")");
                else if (r >= 0 && !(inB[r] && sideD[r] < ladderD)) bad.Add(Show(ladderD, placed, sideD, inB) + " -> hangs on " + "NESW"[r] + ", not a wall");
                else if (placed >= 0 && inB[placed] && ladderD > 0 && sideD[placed] < ladderD && r != placed)
                    bad.Add(Show(ladderD, placed, sideD, inB) + " -> " + r + ": the wall the player chose was overruled");
            }
            Verdict("PT01", n, bad);
        }

        private static void LadderLeadsUpItsWall()
        {
            int n = 0;
            var bad = new List<string>();
            foreach (var (ladderD, placed, sideD, inB) in LadderSpace())
            {
                int r = RM_LadderWallMath.Resolve(placed, ladderD, sideD, inB);
                if (r < 0) continue;
                n++;
                for (int s = 0; s < 4; s++)
                {
                    if (!inB[s]) continue;
                    bool j = RM_LadderWallMath.Joins(r, ladderD, RM_LadderWallMath.FX[s], RM_LadderWallMath.FZ[s], sideD[s]);
                    if (s == r && !j) bad.Add(Show(ladderD, placed, sideD, inB) + ": hangs on " + "NESW"[r] + " but does not lead up it");
                    if (s != r && j) bad.Add(Show(ladderD, placed, sideD, inB) + ": hangs on " + "NESW"[r] + " but leads up " + "NESW"[s]);
                }
            }
            Verdict("PT02", n, bad);
        }

        private static void LadderEquivariant()
        {
            int n = 0;
            var bad = new List<string>();
            foreach (var (ladderD, placed, sideD, inB) in LadderSpace())
            {
                int r = RM_LadderWallMath.Resolve(placed, ladderD, sideD, inB);
                bool placedIsWall = placed >= 0 && inB[placed] && ladderD > 0 && sideD[placed] < ladderD;
                int best = 0, ties = 0;
                for (int s = 0; s < 4; s++)
                    if (inB[s] && ladderD > 0 && sideD[s] < ladderD)
                    {
                        int drop = ladderD - sideD[s];
                        if (drop > best) { best = drop; ties = 1; }
                        else if (drop == best) ties++;
                    }
                // The tie-break (first in N, E, S, W order) is the one place turning the map may change the answer; a tie with
                // the player's own pick is no tie.
                bool determined = r < 0 || placedIsWall || ties == 1;
                if (!determined) continue;
                n++;
                for (int turn = 1; turn < 4; turn++)
                {
                    var d2 = new int[4];
                    var b2 = new bool[4];
                    for (int s = 0; s < 4; s++) { d2[(s + turn) % 4] = sideD[s]; b2[(s + turn) % 4] = inB[s]; }
                    int p2 = placed < 0 ? -1 : (placed + turn) % 4;
                    int r2 = RM_LadderWallMath.Resolve(p2, ladderD, d2, b2);
                    int want = r < 0 ? -1 : (r + turn) % 4;
                    if (r2 != want) bad.Add(Show(ladderD, placed, sideD, inB) + " turned " + turn * 90 + " deg: " + r2 + " want " + want);
                }
                int[] mirror = { 0, 3, 2, 1 };
                var dm = new int[4];
                var bm = new bool[4];
                for (int s = 0; s < 4; s++) { dm[mirror[s]] = sideD[s]; bm[mirror[s]] = inB[s]; }
                int rm = RM_LadderWallMath.Resolve(placed < 0 ? -1 : mirror[placed], ladderD, dm, bm);
                int wantM = r < 0 ? -1 : mirror[r];
                if (rm != wantM) bad.Add(Show(ladderD, placed, sideD, inB) + " mirrored east-west: " + rm + " want " + wantM);
            }
            Verdict("PT03", n, bad);
        }

        private static void LadderStable()
        {
            int n = 0;
            var bad = new List<string>();
            foreach (var (ladderD, placed, sideD, inB) in LadderSpace())
            {
                int r = RM_LadderWallMath.Resolve(placed, ladderD, sideD, inB);
                if (r < 0) continue;
                n++;
                int again = RM_LadderWallMath.Resolve(r, ladderD, sideD, inB);
                if (again != r) bad.Add(Show(ladderD, placed, sideD, inB) + ": " + r + " then " + again);
            }
            Verdict("PT04", n, bad);
        }

        // ── pit pathing ─────────────────────────────────────────────────

        /// <summary>Probe only (PT00): drop the south step from every dug cell, the shape of a pit whose people "could only
        /// move along the southern edge".</summary>
        private static bool faultNoSouthInPits;

        private const int G = 5;          // grid side: a 3x3 dug block inside a one-cell ring of undug ground
        private static readonly int[] Opp = { 1, 0, 3, 2, 6, 7, 4, 5 };

        /// <summary>The production masks (AllowedBits per cell, d9 as RM_CliffMask fills it: off the map reads 0 and vanilla
        /// already clears those bits, so they are cleared here too).</summary>
        private static byte[] Masks(int[] depth, int k)
        {
            var m = new byte[G * G];
            var d9 = new int[9];
            for (int z = 0; z < G; z++)
                for (int x = 0; x < G; x++)
                {
                    for (int dz = -1; dz <= 1; dz++)
                        for (int dx = -1; dx <= 1; dx++)
                        {
                            int xx = x + dx, zz = z + dz;
                            d9[RM_CliffMaskMath.N9(dx, dz)] = xx >= 0 && zz >= 0 && xx < G && zz < G ? depth[zz * G + xx] : 0;
                        }
                    byte bits = RM_CliffMaskMath.AllowedBits(d9, k);
                    if (faultNoSouthInPits && depth[z * G + x] > 0) bits &= unchecked((byte)~(1 << 1));
                    for (int b = 0; b < 8; b++)
                    {
                        int xx = x + RM_CliffMaskMath.Dx[b], zz = z + RM_CliffMaskMath.Dz[b];
                        if (xx < 0 || zz < 0 || xx >= G || zz >= G) bits &= (byte)~(1 << b);
                    }
                    m[z * G + x] = bits;
                }
            return m;
        }

        private static int[] Components(byte[] m, out int count)
        {
            var lab = Enumerable.Repeat(-1, G * G).ToArray();
            count = 0;
            var q = new Queue<int>();
            for (int s = 0; s < G * G; s++)
            {
                if (lab[s] >= 0) continue;
                lab[s] = count;
                q.Enqueue(s);
                while (q.Count > 0)
                {
                    int c = q.Dequeue(), x = c % G, z = c / G;
                    for (int b = 0; b < 8; b++)
                    {
                        if ((m[c] & (1 << b)) == 0) continue;
                        int o = (z + RM_CliffMaskMath.Dz[b]) * G + x + RM_CliffMaskMath.Dx[b];
                        if (lab[o] < 0) { lab[o] = count; q.Enqueue(o); }
                    }
                }
                count++;
            }
            return lab;
        }

        private static IEnumerable<int[]> PitDepths(int maxD)
        {
            int span = maxD + 1, total = 1;
            for (int i = 0; i < 9; i++) total *= span;
            for (int code = 0; code < total; code++)
            {
                var d = new int[G * G];
                int c = code;
                for (int i = 0; i < 9; i++) { d[(1 + i / 3) * G + 1 + i % 3] = c % span; c /= span; }
                yield return d;
            }
        }

        private static string Pit(int[] d)
        {
            var rows = new List<string>();
            for (int z = G - 2; z >= 1; z--) rows.Add(string.Concat(Enumerable.Range(1, 3).Select(x => d[z * G + x].ToString())));
            return string.Join("/", rows) + " (north row first)";
        }

        private static void MaskSymmetric()
        {
            int n = 0;
            var bad = new List<string>();
            foreach (int[] d in PitDepths(3).TakeWhile(_ => bad.Count < 20))
                for (int k = 1; k <= 3 && bad.Count < 20; k++)
                {
                    n++;
                    byte[] m = Masks(d, k);
                    for (int c = 0; c < G * G && bad.Count < 20; c++)
                        for (int b = 0; b < 8; b++)
                        {
                            int x = c % G + RM_CliffMaskMath.Dx[b], z = c / G + RM_CliffMaskMath.Dz[b];
                            if (x < 0 || z < 0 || x >= G || z >= G) continue;
                            bool fwd = (m[c] & (1 << b)) != 0, back = (m[z * G + x] & (1 << Opp[b])) != 0;
                            if (fwd != back) bad.Add(Pit(d) + " K" + k + ": cell " + c % G + "," + c / G + " bit " + b + " " + fwd + ", back " + back);
                        }
                }
            Verdict("PT05", n, bad);
        }

        private static void MaskMatchesPockets()
        {
            int n = 0;
            var bad = new List<string>();
            foreach (int[] d in PitDepths(3).TakeWhile(_ => bad.Count < 20))
                for (int k = 1; k <= 3 && bad.Count < 20; k++)
                {
                    n++;
                    int[] mine = Components(Masks(d, k), out _);
                    var labels = RM_PocketGridMath.Label(d.Select(v => (byte)v).ToArray(), G, G, k);
                    for (int a = 0; a < G * G && bad.Count < 20; a++)
                        for (int b = a + 1; b < G * G; b++)
                            if ((mine[a] == mine[b]) != labels.SameComponent(a, b))
                            {
                                bad.Add(Pit(d) + " K" + k + ": cells " + a + "," + b + " masks " + (mine[a] == mine[b]) + ", pocket grid " + labels.SameComponent(a, b));
                                b = G * G;
                                a = G * G;
                            }
                }
            Verdict("PT06", n, bad);
        }

        private static int[] Turn(int[] d)
        {
            var t = new int[G * G];
            for (int z = 0; z < G; z++)
                for (int x = 0; x < G; x++)
                    t[(G - 1 - x) * G + z] = d[z * G + x];   // a quarter turn about the grid centre
            return t;
        }

        private static string Shape(int[] lab, int count)
        {
            return string.Join(",", Enumerable.Range(0, count).Select(l => lab.Count(v => v == l)).OrderBy(v => v));
        }

        private static void PitNoDirectionBias()
        {
            int n = 0;
            var bad = new List<string>();
            foreach (int[] d in PitDepths(3).TakeWhile(_ => bad.Count < 20))
                for (int k = 1; k <= 3 && bad.Count < 20; k++)
                {
                    n++;
                    int[] l0 = Components(Masks(d, k), out int c0);
                    int[] dt = Turn(d);
                    int[] l1 = Components(Masks(dt, k), out int c1);
                    // the turned grid's cell (x, z) came from (z, G-1-x): same partition, moved
                    bool same = c0 == c1;
                    for (int z = 0; z < G && same; z++)
                        for (int x = 0; x < G && same; x++)
                            for (int z2 = 0; z2 < G && same; z2++)
                                for (int x2 = 0; x2 < G && same; x2++)
                                {
                                    int a0 = z * G + x, b0 = z2 * G + x2;
                                    int a1 = (G - 1 - x) * G + z, b1 = (G - 1 - x2) * G + z2;
                                    if ((l0[a0] == l0[b0]) != (l1[a1] == l1[b1])) same = false;
                                }
                    if (!same && bad.Count < 20) bad.Add(Pit(d) + " K" + k + ": regions " + Shape(l0, c0) + " turned become " + Shape(l1, c1));
                }
            Verdict("PT07", n, bad);
        }

        private static void FlatFloorAllDirections()
        {
            int n = 0;
            var bad = new List<string>();
            for (int shape = 1; shape < 512; shape++)
                for (int depth = 1; depth <= 4; depth++)
                    for (int k = 1; k <= 3; k++)
                    {
                        var d = new int[G * G];
                        for (int i = 0; i < 9; i++) if ((shape & (1 << i)) != 0) d[(1 + i / 3) * G + 1 + i % 3] = depth;
                        n++;
                        byte[] m = Masks(d, k);
                        // every pair of floor cells that touch along an edge, or diagonally with both corners floor, is a step
                        for (int c = 0; c < G * G; c++)
                        {
                            if (d[c] != depth) continue;
                            for (int b = 0; b < 8; b++)
                            {
                                int dx = RM_CliffMaskMath.Dx[b], dz = RM_CliffMaskMath.Dz[b], x = c % G, z = c / G;
                                int o = (z + dz) * G + x + dx;
                                if (d[o] != depth) continue;
                                if (b >= 4 && (d[z * G + x + dx] != depth || d[(z + dz) * G + x] != depth)) continue;
                                if ((m[c] & (1 << b)) == 0 && bad.Count < 20)
                                    bad.Add(Pit(d) + " K" + k + ": floor " + x + "," + z + " cannot step " + "N S E W NE SE SW NW".Split(' ')[b]);
                            }
                        }
                        // and every floor cell reaches every floor cell of its edge-connected pit
                        int[] lab = Components(m, out _);
                        var floor = Enumerable.Range(0, G * G).Where(i => d[i] == depth).ToList();
                        int[] pit = FloorPieces(d, depth);
                        foreach (int a in floor)
                            foreach (int b2 in floor)
                                if (pit[a] == pit[b2] && lab[a] != lab[b2] && bad.Count < 20)
                                    bad.Add(Pit(d) + " K" + k + ": floor " + a + " cannot reach floor " + b2);
                    }
            Verdict("PT08", n, bad);
        }

        /// <summary>Edge-connected pieces of the cells at exactly <paramref name="depth"/> (a plain flood fill, independent
        /// of the climb rule under test).</summary>
        private static int[] FloorPieces(int[] d, int depth)
        {
            var lab = Enumerable.Repeat(-1, G * G).ToArray();
            int count = 0;
            for (int s = 0; s < G * G; s++)
            {
                if (d[s] != depth || lab[s] >= 0) continue;
                var stack = new Stack<int>();
                stack.Push(s);
                lab[s] = count;
                while (stack.Count > 0)
                {
                    int c = stack.Pop(), x = c % G, z = c / G;
                    foreach (int o in new[] { x + 1 < G ? c + 1 : -1, x > 0 ? c - 1 : -1, z + 1 < G ? c + G : -1, z > 0 ? c - G : -1 })
                        if (o >= 0 && d[o] == depth && lab[o] < 0) { lab[o] = count; stack.Push(o); }
                }
                count++;
            }
            return lab;
        }

        private static void DeepPitTrapsLadderFrees()
        {
            int n = 0;
            var bad = new List<string>();
            for (int shape = 1; shape < 512; shape++)
                for (int depth = 2; depth <= 4; depth++)
                    for (int k = 1; k < depth; k++)
                    {
                        var d = new int[G * G];
                        for (int i = 0; i < 9; i++) if ((shape & (1 << i)) != 0) d[(1 + i / 3) * G + 1 + i % 3] = depth;
                        var labels = RM_PocketGridMath.Label(d.Select(v => (byte)v).ToArray(), G, G, k);
                        for (int c = 0; c < G * G; c++)
                        {
                            if (d[c] != depth) continue;
                            n++;
                            int x = c % G, z = c / G;
                            if (!labels.IsPocketCell(c) && bad.Count < 20) bad.Add(Pit(d) + " K" + k + ": floor " + x + "," + z + " is not trapped");
                            var sideD = new int[4];
                            var inB = new bool[4];
                            for (int s = 0; s < 4; s++)
                            {
                                int xx = x + RM_LadderWallMath.FX[s], zz = z + RM_LadderWallMath.FZ[s];
                                inB[s] = xx >= 0 && zz >= 0 && xx < G && zz < G;
                                sideD[s] = inB[s] ? d[zz * G + xx] : depth;
                            }
                            bool hasRim = Enumerable.Range(0, 4).Any(s => inB[s] && sideD[s] < depth);
                            int r = RM_LadderWallMath.Resolve(-1, depth, sideD, inB);
                            if (!hasRim) { if (r >= 0 && bad.Count < 20) bad.Add(Pit(d) + ": a ladder mid-floor at " + x + "," + z + " hangs on " + r); continue; }
                            int o = (z + RM_LadderWallMath.FZ[Math.Max(r, 0)]) * G + x + RM_LadderWallMath.FX[Math.Max(r, 0)];
                            bool edge = r >= 0 && RM_PocketGridMath.LadderEdge(r, depth, labels.label[c], d[o], labels.label[o], true);
                            if (!(edge && labels.surface[labels.label[o]]) && bad.Count < 20)
                                bad.Add(Pit(d) + " K" + k + ": a ladder at " + x + "," + z + " (wall " + r + ") does not lead to the surface");
                        }
                    }
            Verdict("PT09", n, bad);
        }

        // ── hoses ───────────────────────────────────────────────────────

        private static double Arc(IList<V2> p, out double[] s)
        {
            s = new double[p.Count];
            for (int i = 1; i < p.Count; i++) s[i] = s[i - 1] + V2.Dist(p[i - 1], p[i]);
            return s[p.Count - 1];
        }

        private static V2 At(IList<V2> p, double[] s, double t)
        {
            t = Math.Max(0, Math.Min(s[s.Length - 1], t));
            int i = 1;
            while (i < p.Count - 1 && s[i] < t) i++;
            double f = s[i] - s[i - 1] < 1e-12 ? 0 : (t - s[i - 1]) / (s[i] - s[i - 1]);
            return p[i - 1] + (p[i] - p[i - 1]) * f;
        }

        private static double Dot(V2 a, V2 b) => a.X * b.X + a.Z * b.Z;

        /// <summary>Total absolute turning (degrees) of the polyline over arc [t0, t1], sampled every 0.05 cells.</summary>
        private static double Turning(IList<V2> p, double[] s, double t0, double t1)
        {
            double sum = 0, prev = double.NaN;
            for (double t = t0; t + 0.05 <= t1 + 1e-9; t += 0.05)
            {
                V2 a = At(p, s, t), b = At(p, s, t + 0.05);
                if ((b - a).Len < 1e-6) continue;
                double h = Math.Atan2(b.Z - a.Z, b.X - a.X);
                if (!double.IsNaN(prev))
                {
                    double dh = h - prev;
                    while (dh > Math.PI) dh -= 2 * Math.PI;
                    while (dh < -Math.PI) dh += 2 * Math.PI;
                    sum += Math.Abs(dh);
                }
                prev = h;
            }
            return sum * 180 / Math.PI;
        }

        private static void HoseEndsStraight()
        {
            int n = 0, refused = 0;
            var bad = new List<string>();
            double cos = Math.Cos(35 * Math.PI / 180);
            for (int ra = 0; ra < 4; ra++)
                for (int rb = 0; rb < 4; rb++)
                    for (int dx = -8; dx <= 8; dx += 2)
                        for (int dz = -8; dz <= 8; dz += 2)
                        {
                            if (Math.Max(Math.Abs(dx), Math.Abs(dz)) < 4) continue;
                            HoseReelRect A = HoseReelLinkChecks.Placed(20, 20, ra), B = HoseReelLinkChecks.Placed(20 + dx, 20 + dz, rb);
                            var w = new CordWorld(44, 44);
                            foreach (HoseReelRect r in new[] { A, B })
                                for (int x = r.X0; x < r.X0 + r.W; x++)
                                    for (int z = r.Z0; z < r.Z0 + r.H; z++) w.SetExtraCost(new Cell(x, z), (float)HoseMath.BuildingCrossCost);
                            HoseLay lay = HoseReelLinkChecks.LayLink(w, A, B, out Cell intake, out V2 end);
                            if (!lay.Ok || lay.Flat == null || lay.Flat.Count < 2) { refused++; continue; }
                            n++;
                            HoseRelay.DrawnEnd(B, intake, B.Look ?? "Scrapper", false, out V2 inward);
                            var p = lay.Flat;
                            double L = Arc(p, out double[] s);
                            string tag = "A " + "NESW"[ra] + " at 20,20 -> B " + "NESW"[rb] + " at " + (20 + dx) + "," + (20 + dz) + " (len " + L.ToString("0.0") + ")";
                            if (V2.Dist(p[0], A.Mouth) > 0.06) bad.Add(tag + ": starts " + V2.Dist(p[0], A.Mouth).ToString("0.00") + " off the outlet");
                            if (V2.Dist(p[p.Count - 1], end) > 0.06) bad.Add(tag + ": ends " + V2.Dist(p[p.Count - 1], end).ToString("0.00") + " off the inlet");
                            V2 h0 = (At(p, s, 0.3) - p[0]).Norm(), h1 = (p[p.Count - 1] - At(p, s, L - 0.3)).Norm();
                            if (A.Outward.HasValue && Dot(h0, A.Outward.Value.Norm()) < cos) bad.Add(tag + ": leaves at " + h0 + ", outlet points " + A.Outward);
                            if (Dot(h1, inward.Norm()) < cos) bad.Add(tag + ": arrives heading " + h1 + ", inlet wants " + inward);
                            double tEnd = Turning(p, s, Math.Max(0, L - 1.0), L), tStart = Turning(p, s, 0, Math.Min(L, 1.0));
                            if (tEnd > 90) bad.Add(tag + ": turns " + tEnd.ToString("0") + " deg in its last cell");
                            if (tStart > 90) bad.Add(tag + ": turns " + tStart.ToString("0") + " deg in its first cell");
                        }
            Console.WriteLine("    PT10: " + refused + " layouts refused (not laid; not judged)");
            Verdict("PT10", n, bad);
        }

        // ── water levelling ─────────────────────────────────────────────

        private const int U = RM_LevelSolve.U;
        private const int WW = 7, WH = 6;   // a 5x4 dig area inside a ring of undug ground

        private static ArrayWorld LevelWorld()
        {
            var world = new ArrayWorld(WW, WH);
            world.k.levelBySurfaceEnabled = true;
            world.k.levelSetEnabled = true;
            world.k.creepWaterEnabled = true;
            world.k.creepEnabled = true;
            world.k.viscosityEnabled = true;
            world.k.levelExactEnabled = true;
            return world;
        }

        private static long Water(ArrayWorld w)
        {
            long t = 0;
            for (int i = 0; i < WW * WH; i++) if (w.k.depth[i] > 0) t += w.k.WaterOf(i);
            return t;
        }

        /// <summary>Pulse until three identical snapshots; false when it never rests.</summary>
        private static bool Rest(ArrayWorld w, List<int> dug, int maxPulses)
        {
            string prev = null;
            int still = 0;
            for (int p = 0; p < maxPulses && still < 3; p++)
            {
                w.Pulse(dug);
                string snap = string.Join(",", dug.Select(c => w.k.WaterOf(c))) + "|" + w.k.exactCreditDl + "|" + w.k.exactDrainDl;
                still = snap == prev ? still + 1 : 0;
                prev = snap;
            }
            return still >= 3;
        }

        /// <summary>Water perched above a neighbour it could flow into: surfaces (dL above the pit's rim, negative = below)
        /// of two edge-touching dug cells differ by more than a quarter notch while the higher one stands above the lower
        /// cell's floor. Returns the worst such step in notches (0 = none).</summary>
        private static double Perched(ArrayWorld w, List<int> dug, out string where)
        {
            where = "";
            double worst = 0;
            var set = new HashSet<int>(dug);
            foreach (int a in dug)
            {
                int ax = a % WW, az = a / WW;
                foreach (int b in new[] { a + 1, a - 1, a + WW, a - WW })
                {
                    if (!set.Contains(b) || Math.Abs(b % WW - ax) + Math.Abs(b / WW - az) != 1) continue;
                    long wa = w.k.WaterOf(a), wb = w.k.WaterOf(b);
                    if (wa <= 0) continue;
                    long sa = wa - (long)w.k.depth[a] * U, sb = wb - (long)w.k.depth[b] * U, floorB = -(long)w.k.depth[b] * U;
                    if (sa <= floorB + U / 4) continue;          // the water stands below the neighbour's floor: a real step
                    double step = (sa - sb) / (double)U;
                    if (step > 0.25 && step > worst)
                    {
                        worst = step;
                        where = "cell " + ax + "," + az + " (depth " + w.k.depth[a] + ", water " + wa + " dL) over " + b % WW + "," + b / WW
                            + " (depth " + w.k.depth[b] + ", water " + wb + " dL)";
                    }
                }
            }
            return worst;
        }

        private static string Depths(ArrayWorld w)
        {
            var rows = new List<string>();
            for (int z = WH - 1; z >= 0; z--) rows.Add(string.Concat(Enumerable.Range(0, WW).Select(x => w.k.depth[z * WW + x].ToString())));
            return string.Join("/", rows);
        }

        /// <summary>Every pit shape of the sweep: rectangles 1..5 x 1..4 at (1,1), each uniform or split into two depths
        /// (west/east or south/north half), depths 1..4. half: true = the cell is in the second (east or north) half.</summary>
        private static IEnumerable<(int[] depth, bool[] half, string name)> LevelPits()
        {
            for (int pw = 1; pw <= 5; pw++)
                for (int ph = 1; ph <= 4; ph++)
                    for (int split = 0; split < 2; split++)
                    {
                        if (split == 0 && pw < 2 || split == 1 && ph < 2) continue;
                        for (int dA = 1; dA <= 4; dA++)
                            for (int dB = 1; dB <= 4; dB++)
                            {
                                var depth = new int[WW * WH];
                                var half = new bool[WW * WH];
                                for (int z = 1; z <= ph; z++)
                                    for (int x = 1; x <= pw; x++)
                                    {
                                        bool second = split == 0 ? x - 1 >= pw / 2 : z - 1 >= ph / 2;
                                        half[z * WW + x] = second;
                                        depth[z * WW + x] = second ? dB : dA;
                                    }
                                yield return (depth, half, pw + "x" + ph + (split == 0 ? " west/east " : " south/north ") + dA + "/" + dB);
                            }
                    }
        }

        private static void WaterLevelsOnePour()
        {
            int n = 0, unrested = 0, spread = 0, multi = 0;
            var bad = new List<string>();
            foreach (var (depth, half, name) in LevelPits())
            {
                var cells = Enumerable.Range(0, WW * WH).Where(i => depth[i] > 0).ToList();
                foreach (int pour in new[] { cells.First(), cells.Last() })
                {
                    var w = LevelWorld();
                    foreach (int c in cells) w.k.depth[c] = (byte)depth[c];
                    w.k.fill[pour] = (byte)depth[pour];
                    w.cellFluid[pour] = ArrayWorld.Water;
                    long t0 = Water(w);
                    n++;
                    if (!Rest(w, cells, 300)) { unrested++; continue; }
                    long t1 = Water(w);
                    if (cells.Count > 1) { multi++; if (cells.Count(c => c != pour && w.k.WaterOf(c) > 0) > 0) spread++; }
                    if (t1 != t0) bad.Add(name + " pour at " + pour % WW + "," + pour / WW + ": water " + t0 + " -> " + t1 + " dL");
                    double p = Perched(w, cells, out string where);
                    if (p > 0) bad.Add(name + " pour at " + pour % WW + "," + pour / WW + ": " + p.ToString("0.00") + " notches perched at " + where + " depths " + Depths(w));
                }
            }
            Console.WriteLine("    PT11: " + unrested + " scenes never came to rest in 300 pulses (not judged); water left the poured cell in " + spread + " of " + multi + " multi-cell pits");
            Assert(spread * 2 > multi, "can-fail: the water moved in only " + spread + " of " + multi + " pits (is the kernel pulsing?)");
            Assert(unrested * 10 < n, "PT11: " + unrested + " of " + n + " scenes never rest");
            Verdict("PT11", n, bad);
        }

        private static void WaterLevelsAfterSecondDig()
        {
            int n = 0, unrested = 0, reached = 0;
            var bad = new List<string>();
            foreach (var (depth, half, name) in LevelPits())
            {
                var first = Enumerable.Range(0, WW * WH).Where(i => depth[i] > 0 && !half[i]).ToList();
                var all = Enumerable.Range(0, WW * WH).Where(i => depth[i] > 0).ToList();
                if (first.Count == 0 || first.Count == all.Count) continue;
                var w = LevelWorld();
                foreach (int c in first) { w.k.depth[c] = (byte)depth[c]; w.k.fill[c] = (byte)depth[c]; w.cellFluid[c] = ArrayWorld.Water; }
                n++;
                if (!Rest(w, first, 100)) { unrested++; continue; }
                long t0 = Water(w);
                foreach (int c in all) w.k.depth[c] = (byte)depth[c];
                if (!Rest(w, all, 300)) { unrested++; continue; }
                long t1 = Water(w);
                if (all.Any(c => half[c] && w.k.WaterOf(c) > 0)) reached++;
                if (t1 != t0) bad.Add(name + ": water " + t0 + " -> " + t1 + " dL after the second dig");
                double p = Perched(w, all, out string where);
                if (p > 0) bad.Add(name + ": " + p.ToString("0.00") + " notches perched at " + where + " depths " + Depths(w));
            }
            Console.WriteLine("    PT12: " + unrested + " scenes never came to rest (not judged); water reached the new half in " + reached + " of " + n);
            Assert(reached * 2 > n, "can-fail: the water reached the new half in only " + reached + " of " + n);
            Assert(unrested * 10 < n, "PT12: " + unrested + " of " + n + " scenes never rest");
            Verdict("PT12", n, bad);
        }
    }
}
