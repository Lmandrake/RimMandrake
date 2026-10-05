// Gimme Some Slack L6 (flexible hoses) offline checks: the Verse-free half of the hose feature
// (Source/Hose/HoseMath.cs, the PRODUCTION file, compiled in directly). Design:
// design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md section 3. Called from Program.Main.
// Written red-first (2026-10-02): every case below failed against a stub HoseMath before the real one.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.GimmeSomeSlack.Hose;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class HoseSelfTest
    {
        private static Action<bool, string> check;
        private static int mine, mineFails;

        private static void C(bool ok, string msg)
        {
            mine++;
            if (!ok) mineFails++;
            check(ok, "hose: " + msg);
        }

        public static void Run(Action<bool, string> chk)
        {
            check = chk;
            mine = mineFails = 0;
            Widths();
            StateMachine();
            Wobble();
            LayOpen();
            LayAroundWall();
            Install();
            Signals();
            Ports();
            Maze();
            Reel2x2();
            Replan();
            Round4();
            Round5();
            Console.WriteLine($"hose: {mine - mineFails}/{mine} checks passed");
        }

        // ------------------------------------------------------------------ width rules
        private static void Widths()
        {
            double wire = HoseMath.WireVisibleWidth;
            double f = HoseMath.VisibleWidth(0, 1), p = HoseMath.VisibleWidth(1, 1);
            C(wire > 0.05 && wire < 0.12, "wire visible width is the strand's band (" + wire.ToString("0.000") + ")");
            // the hose kept its width when the cord strand thinned 0.11 -> 0.08 (cords round 5): 4.4x the old wire, ~6x today's
            C(f >= 4 * wire && f <= 7 * wire, "flat hose is 4-7x a wire (" + (f / wire).ToString("0.00") + "x)");
            C(p > f * 1.1, "plump hose is visibly swollen over flat (" + p.ToString("0.000") + " vs " + f.ToString("0.000") + ")");
            C(Math.Abs(HoseMath.VisibleWidth(0.5, 1) - (f + p) / 2) < 1e-9, "visible width blends linearly in the eased blend");
            C(Math.Abs(HoseMath.VisibleWidth(1, 0) - f) < 1e-9, "plump amount 0 = no swelling");
            C(Math.Abs(HoseMath.MeshWidthFlat(f) * HoseMath.FlatBand - f) < 1e-9 && Math.Abs(HoseMath.MeshWidthPlump(p) * HoseMath.PlumpBand - p) < 1e-9,
              "mesh widths put the art's opaque band at the visible width");
        }

        // ------------------------------------------------------------------ the flat/plump state machine
        private static List<HoseVis> RunTrace(HoseStateMachine sm, HoseTuning t, Func<int, bool> sig, int ticks, out double maxStep, int t0 = 0)
        {
            var seq = new List<HoseVis> { sm.State };
            maxStep = 0;
            double prev = sm.Blend(t0, t);
            for (int now = t0; now < t0 + ticks; now++)
            {
                sm.Update(now, sig(now), t);
                if (sm.State != seq[seq.Count - 1]) seq.Add(sm.State);
                double b = sm.Blend(now, t);
                maxStep = Math.Max(maxStep, Math.Abs(b - prev));
                prev = b;
            }
            return seq;
        }

        private static string S(List<HoseVis> s) => string.Join(">", s);

        private static void StateMachine()
        {
            var t = new HoseTuning();
            C(t.TransitionTicks == 30 && t.ReleaseTicks == 500 && t.MinPlumpDwell == 600, "default tuning 30 / 500 / 600 ticks");
            var sm = new HoseStateMachine();
            List<HoseVis> s0 = RunTrace(sm, t, n => false, 2000, out _);
            C(s0.Count == 1 && sm.State == HoseVis.Flat && sm.Transitions == 0, "no flow: stays Flat (" + S(s0) + ")");

            sm = new HoseStateMachine();
            sm.Update(0, true, t);
            C(sm.State == HoseVis.Filling, "first flowing tick starts Filling");
            for (int n = 1; n < 15; n++) sm.Update(n, true, t);
            double mid = sm.Blend(14, t);
            C(mid > 0.4 && mid < 0.6, "half way through the transition the blend is ~0.5 (" + mid.ToString("0.00") + ")");
            for (int n = 15; n <= 31; n++) sm.Update(n, true, t);
            C(sm.State == HoseVis.Plump && Math.Abs(sm.Blend(31, t) - 1) < 1e-9, "Plump within the transition window (" + sm.State + ")");

            // the design's pulse trace T F T T F F F (250-tick pulses, the signal held for each pulse)
            bool[] pulses = { true, false, true, true, false, false, false, false };
            sm = new HoseStateMachine();
            List<HoseVis> s1 = RunTrace(sm, t, n => pulses[Math.Min(pulses.Length - 1, n / 250)], 8 * 250, out double step1);
            C(S(s1) == "Flat>Filling>Plump>Draining>Flat", "pulse trace T F T T F F F: " + S(s1));
            var sm1 = new HoseStateMachine();
            bool leftPlumpEarly = false;
            for (int n = 0; n < 1000; n++)
            {
                sm1.Update(n, pulses[n / 250], t);
                if (n > 40 && sm1.State != HoseVis.Plump) leftPlumpEarly = true;
            }
            C(!leftPlumpEarly, "a one-pulse stall never leaves Plump");
            C(step1 <= 1.0 / t.TransitionTicks + 1e-9, "blend never jumps (max step " + step1.ToString("0.000") + ")");

            // flicker: the signal toggling every 40 ticks (far faster than the release) settles Plump and stays
            sm = new HoseStateMachine();
            List<HoseVis> s2 = RunTrace(sm, t, n => (n / 40) % 2 == 0, 3000, out _);
            C(S(s2) == "Flat>Filling>Plump" && sm.Transitions == 2, "fast toggle: no flicker (" + S(s2) + ", " + sm.Transitions + " transitions)");
            // ...and the detector can see flicker: no hysteresis on the same trace flickers
            var none = new HoseTuning { TransitionTicks = 1, ReleaseTicks = 0, MinPlumpDwell = 0 };
            sm = new HoseStateMachine();
            RunTrace(sm, none, n => (n / 40) % 2 == 0, 3000, out _);
            C(sm.Transitions > 20, "negative control: no hysteresis flickers (" + sm.Transitions + " transitions)");

            // re-pressurise mid-drain: Filling resumes from the current blend, no jump
            sm = new HoseStateMachine();
            RunTrace(sm, t, n => n < 100, 1100 + 10, out _);            // Plump, then release at ~tick 700, draining
            HoseVis was = sm.State;
            double bDrain = sm.Blend(1109, t);
            sm.Update(1110, true, t);
            double bNow = sm.Blend(1110, t);
            C(was == HoseVis.Flat || (sm.State == HoseVis.Filling && Math.Abs(bNow - bDrain) <= 1.0 / t.TransitionTicks + 1e-9),
              "re-pressurise: " + was + " -> " + sm.State + " blend " + bDrain.ToString("0.00") + " -> " + bNow.ToString("0.00"));
            sm = new HoseStateMachine();
            RunTrace(sm, t, n => n < 100, 640, out _);              // released at 630 (dwell 600 from Plump at 30)
            HoseVis mid2 = sm.State;
            double bd = sm.Blend(639, t);
            sm.Update(640, true, t);
            C(mid2 == HoseVis.Draining && sm.State == HoseVis.Filling && Math.Abs(sm.Blend(640, t) - bd) <= 1.0 / t.TransitionTicks + 1e-9,
              "mid-drain flow resumes Filling from " + bd.ToString("0.00") + " (" + mid2 + ")");
            sm.ResetFlat();
            C(sm.State == HoseVis.Flat && sm.Blend(641, t) == 0, "reset (cut / reregister) is instant Flat");

            C(HoseMath.Ease(0) == 0 && HoseMath.Ease(1) == 1 && HoseMath.Ease(0.25) < HoseMath.Ease(0.5) && HoseMath.Ease(0.5) < HoseMath.Ease(0.75),
              "ease curve monotone 0..1");
        }

        private static void Wobble()
        {
            double mid = Enumerable.Range(0, 30).Max(k => Math.Abs(HoseMath.Wobble(0.5, k, 30, 1)));
            C(mid > 0.02, "a transition wobbles the middle (" + mid.ToString("0.000") + " cells)");
            C(Math.Abs(HoseMath.Wobble(0, 5, 30, 1)) < 1e-9 && Math.Abs(HoseMath.Wobble(1, 5, 30, 1)) < 1e-9, "wobble pinned at both ends");
            C(Math.Abs(HoseMath.Wobble(0.5, 400, 30, 1)) < 1e-6 && !HoseMath.WobbleActive(400, 30), "the wobble is brief (gone 400 ticks later)");
            C(HoseMath.Wobble(0.5, 5, 30, 0) == 0, "plump amount 0 = no wobble");
        }

        // ------------------------------------------------------------------ laying
        private static CordWorld Open(int w, int h) => new CordWorld(w, h);

        private static double MaxLateral(List<V2> pts, V2 a, V2 b)
        {
            V2 d = (b - a).Norm();
            return pts.Max(p => Math.Abs((p.X - a.X) * d.Z - (p.Z - a.Z) * d.X));
        }

        private static void LayOpen()
        {
            CordWorld w = Open(44, 30);
            var p = new HoseShapeParams();
            V2 a = new V2(5.5, 15.5), b = new V2(33.5, 15.5);
            HoseLay lay = HoseMath.Lay(w, a, b, p, 7);
            C(lay.Ok && lay.Flat.Count > 10, "open floor: laid (" + lay.Reason + ")");
            if (!lay.Ok) return;
            C(V2.Dist(lay.Flat[0], a) < 1e-6 && V2.Dist(lay.Flat[lay.Flat.Count - 1], b) < 1e-6, "flat hose ends exactly at reel and nozzle");
            C(lay.Flat.Count == lay.Plump.Count, "flat and plump poses have matching samples (crossfade)");
            double straight = V2.Dist(a, b);
            C(lay.FlatLen > straight * 1.03 && lay.FlatLen <= lay.PathLen + 6.5, "flat slack within the hose budget (" + lay.FlatLen.ToString("0.0") + " over " + straight.ToString("0.0") + ")");
            C(lay.PlumpLen < lay.FlatLen * 0.995 && lay.PlumpLen >= straight, "plump is shorter (" + lay.PlumpLen.ToString("0.00") + " < " + lay.FlatLen.ToString("0.00") + ")");
            double latF = MaxLateral(lay.Flat, a, b), latP = MaxLateral(lay.Plump, a, b);
            C(latF >= 0.3 && latF <= 2.4, "flat lies in gentle S-curves (max excursion " + latF.ToString("0.00") + " cells)");
            C(latP < latF * 0.9, "plump is straighter (" + latP.ToString("0.00") + " < " + latF.ToString("0.00") + ")");
            C(lay.MinBendFlat >= p.MinBendRadius * 0.95, "flat min bend radius " + lay.MinBendFlat.ToString("0.00") + " >= " + p.MinBendRadius);
            C(lay.MinBendPlump >= p.MinBendRadius * 0.95, "plump min bend radius " + lay.MinBendPlump.ToString("0.00"));
            C(!HoseMath.SelfIntersects(lay.Flat), "no loops: the flat hose never crosses itself");
            C(lay.Flat.All(q => w.IsWalkable(q.Floor)), "every point on walkable floor");
            // B17 (owner review 2026-10-04): no joiner on a straight length; joiners only at real bends
            C(lay.Joints.Count == 0 && lay.Couplings.Count == 2, "straight route: no joiner, only the two end fittings (" + lay.Joints.Count + " joiners)");
            var ell = new List<V2>();
            for (int i = 0; i <= 80; i++) ell.Add(new V2(2 + i * 0.1, 5));
            for (int i = 1; i <= 80; i++) ell.Add(new V2(10, 5 + i * 0.1));
            var zig = new List<V2>(ell);
            for (int i = 1; i <= 80; i++) zig.Add(new V2(10 + i * 0.1, 13));
            List<int> je = HoseMath.Joints(ell, p.CouplingSpacing), jz = HoseMath.Joints(zig, 4);
            C(je.Count == 1 && V2.Dist(ell[je[0]], new V2(10, 5)) < 0.3, "an L route: exactly one joiner, at the corner (" + je.Count + ")");
            C(jz.Count == 2 && jz.All(j => HoseMath.TurnAt(zig, Geo.CumLen(zig), j) >= HoseMath.JointTurn), "a Z route: one joiner per bend, each on a bend (" + jz.Count + ")");
            var straightC = new List<V2>();
            for (int i = 0; i <= 160; i++) straightC.Add(new V2(2 + i * 0.1, 5 + 0.02 * Math.Sin(i * 0.3)));
            C(HoseMath.Joints(straightC, 4).Count == 0, "a 16-cell straight (with a hair of wiggle): no joiner");
            // B9: a joiner is two couplings face to face, their brass faces meeting at the joint
            HoseMath.JoinerPoses(new V2(5, 5), new V2(1, 0), 0.7, 0.46, out V2 fw, out V2 bw);
            C(V2.Dist(fw + new V2(1, 0) * (0.46 * 0.7), new V2(5, 5)) < 1e-9 && V2.Dist(bw - new V2(1, 0) * (0.46 * 0.7), new V2(5, 5)) < 1e-9 && fw.X < 5 && bw.X > 5,
              "joiner: the two couplings sit either side of the joint, faces meeting on it");
            // B18: crossing hoses draw in a fixed order inside the hose altitude layer
            bool mono = true;
            for (int k = 1; k <= HoseMath.CrossRanks; k++) mono &= HoseMath.CrossLift(k) - HoseMath.CrossLift(k - 1) >= 0.0014f;
            C(mono && HoseMath.CrossLift(HoseMath.CrossRanks) + 0.005f < 0.0390625f && HoseMath.CrossLift(99) == HoseMath.CrossLift(HoseMath.CrossRanks),
              "crossings: each newer hose a full band (>= its own 0.0014 span) above the older, all inside one altitude layer");
            HoseLay again = HoseMath.Lay(w, a, b, p, 7);
            C(again.Flat.Count == lay.Flat.Count && again.Flat.Zip(lay.Flat, (x, y) => V2.Dist(x, y) < 1e-12).All(x => x), "deterministic per seed");
            List<V2> p0 = HoseMath.Pose(lay, 0, 10000, 30, 1), p1 = HoseMath.Pose(lay, 1, 10000, 30, 1);
            C(p0.Zip(lay.Flat, (x, y) => V2.Dist(x, y) < 1e-9).All(x => x) && p1.Zip(lay.Plump, (x, y) => V2.Dist(x, y) < 1e-9).All(x => x),
              "pose 0 = flat, pose 1 = plump (no wobble once settled)");
            var stiff = new HoseShapeParams { MinBendRadius = 2.0 };
            HoseLay ls = HoseMath.Lay(w, a, b, stiff, 7);
            C(ls.Ok && ls.MinBendFlat >= 2.0 * 0.95, "stiffness setting raises the bend radius (" + ls.MinBendFlat.ToString("0.00") + ")");
            // negative control: the bend measure sees a tight corner (the raw planned centreline at a right angle)
            var corner = CordPlanner.RoundCorners(new List<V2> { new V2(2, 2), new V2(10, 2), new V2(10, 10) });
            C(HoseMath.MinBendRadius(corner, 0.5) < 1.0, "negative control: a rounded right angle reads tighter than a hose may bend");
        }

        private static void LayAroundWall()
        {
            CordWorld w = Open(44, 34);
            for (int z = 0; z <= 20; z++) w.SetBlocked(new Cell(20, z), BlockKind.Wall);
            var p = new HoseShapeParams();
            V2 a = new V2(8.5, 10.5), b = new V2(32.5, 10.5);
            HoseLay lay = HoseMath.Lay(w, a, b, p, 3);
            C(lay.Ok, "around a wall: laid (" + lay.Reason + ")");
            if (!lay.Ok) return;
            C(lay.Flat.All(q => w.IsWalkable(q.Floor)) && lay.Plump.All(q => w.IsWalkable(q.Floor)), "around a wall: no point inside the wall (flat and plump)");
            C(lay.Flat.Max(q => q.Z) > 20.5, "around a wall: goes round the wall's end");
            C(lay.MinBendFlat >= p.MinBendRadius * 0.95, "around a wall: min bend radius " + lay.MinBendFlat.ToString("0.00"));
            C(!HoseMath.SelfIntersects(lay.Flat), "around a wall: no loops");
        }

        private static void Install()
        {
            CordWorld w = Open(40, 30);
            for (int x = 20; x <= 24; x++) { w.SetBlocked(new Cell(x, 20), BlockKind.Wall); w.SetBlocked(new Cell(x, 24), BlockKind.Wall); }
            for (int z = 20; z <= 24; z++) { w.SetBlocked(new Cell(20, z), BlockKind.Wall); w.SetBlocked(new Cell(24, z), BlockKind.Wall); }
            var reel = new Cell(5, 5);
            C(HoseMath.CheckInstall(w, reel, new Cell(15, 8), 30) == null, "install: an open target in range is valid");
            C(HoseMath.CheckInstall(w, reel, reel, 30) == "same cell", "install: refuses the reel's own cell");
            C(HoseMath.CheckInstall(w, reel, new Cell(38, 28), 30) == "too far", "install: refuses beyond the hose length");
            C(HoseMath.CheckInstall(w, reel, new Cell(20, 22), 30) == "target blocked", "install: refuses a wall cell");
            C(HoseMath.CheckInstall(w, reel, new Cell(22, 22), 30) == "no route", "install: refuses a sealed room");
            C(HoseMath.CheckInstall(w, reel, new Cell(-1, 3), 30) == "out of bounds", "install: refuses off the map");
            // a straight-line-near target whose only route is long: refused on route length
            CordWorld w2 = Open(40, 40);
            for (int z = 0; z <= 36; z++) w2.SetBlocked(new Cell(10, z), BlockKind.Wall);
            C(HoseMath.CheckInstall(w2, new Cell(5, 2), new Cell(15, 2), 30) == "route too long", "install: refuses a route longer than the hose");
        }

        private static void Signals()
        {
            C(HoseMath.PumpFlowing(4, 1000, 1100, 250), "pump moved liquid this pulse = flowing");
            C(!HoseMath.PumpFlowing(0, 1000, 1100, 250), "pump moved 0 units = not flowing");
            C(!HoseMath.PumpFlowing(4, 1000, 1500, 250), "pump's last move is older than a pulse and a half = not flowing");
            int[] w = HoseTint.Rgb("RM_Fluid_Water"), t = HoseTint.Rgb("RM_Fluid_Tar"), u = HoseTint.Rgb("no_such_fluid");
            C(w != null && t != null && !w.SequenceEqual(t), "per-fluid tint: water and tar differ");
            C(u.SequenceEqual(w), "per-fluid tint: an unknown fluid reads as water");
        }

        // ------------------------------------------------------------------ reel ports (owner review round 2, 2026-10-04)
        private static void Ports()
        {
            var reel = new Cell(10, 10);
            var tankE = new HosePortCandidate(11, 9, 2, 2, HosePortKind.Tank);   // 2x2 tank whose west edge touches the reel
            var pipeN = new HosePortCandidate(10, 11, 1, 1, HosePortKind.Pipe);
            var corner = new HosePortCandidate(11, 11, 1, 1, HosePortKind.Pipe); // diagonal only
            var far = new HosePortCandidate(12, 10, 1, 1, HosePortKind.Pipe);    // one cell away
            int i = HosePortRule.Pick(reel, new List<HosePortCandidate> { tankE }, out Cell s);
            C(i == 0 && s == new Cell(1, 0), "ports: a 2x2 tank sharing an edge couples, on the east side");
            i = HosePortRule.Pick(reel, new List<HosePortCandidate> { tankE, pipeN }, out s);
            C(i == 1 && s == new Cell(0, 1), "ports: a pipe is preferred over a tank");
            i = HosePortRule.Pick(reel, new List<HosePortCandidate> { pipeN, tankE }, out s);
            C(i == 0, "ports: the choice does not depend on candidate order");
            C(HosePortRule.Pick(reel, new List<HosePortCandidate> { corner, far }, out s) == -1, "ports: a corner touch or a gap of one cell does not couple");
            var pipeW = new HosePortCandidate(9, 10, 1, 1, HosePortKind.Pipe);
            i = HosePortRule.Pick(reel, new List<HosePortCandidate> { pipeW, pipeN }, out s);
            C(i == 1 && s == new Cell(0, 1), "ports: two pipes tie-break by side (east, north, west, south)");
            C(HosePortRule.Pick(reel, new List<HosePortCandidate> { new HosePortCandidate(9, 9, 3, 3, HosePortKind.Tank) }, out s) == -1,
                "ports: a candidate covering the reel's own cell is ignored");
            HosePortRule.Feed(reel, new Cell(1, 0), out V2 from, out V2 to, out V2 cp);
            C(Math.Abs(to.X - 11.5) < 1e-9 && Math.Abs(to.Z - 10.5) < 1e-9 && Math.Abs(cp.X - 11.0) < 1e-9 && from.X > 10.5 && from.X < cp.X,
                "ports: the feed runs from under the reel, across the coupling on the shared edge, to the port cell's centre");
        }

        // ------------------------------------------------------------------ maze / spiral path solving (round 2)
        /// <summary>The same maze validation_hose.py builds live (MAZE there; keep the two in step). Rows run from high z
        /// to low z. R reel, T target, g the short route's gap (walled in step 2), b a cell of the long route (walled in
        /// step 3). The long route is a 3/4 spiral round the chamber: out west, up, along the top, down the east side.</summary>
        public static readonly string[] MazeRows =
        {
            "###############  ",
            "#.............#  ",
            "#.###########.#  ",
            "#b#.........#.#  ",
            "#...R.......g...T",
            "###.........###  ",
            "  ###########    ",
        };

        private static CordWorld MazeWorld(int ox, int oz, out Cell R, out Cell T, out Cell g, out Cell b)
        {
            var w = Open(ox + 24, oz + 14);
            R = T = g = b = new Cell(0, 0);
            int h = MazeRows.Length;
            for (int i = 0; i < h; i++)
                for (int x = 0; x < MazeRows[i].Length; x++)
                {
                    var c = new Cell(ox + x, oz + h - 1 - i);
                    switch (MazeRows[i][x])
                    {
                        case '#': w.SetBlocked(c, BlockKind.Wall); break;
                        case 'R': R = c; break;
                        case 'T': T = c; break;
                        case 'g': g = c; break;
                        case 'b': b = c; break;
                    }
                }
            return w;
        }

        private static void Maze()
        {
            CordWorld w = MazeWorld(3, 3, out Cell R, out Cell T, out Cell g, out Cell b);
            var p = new HoseShapeParams();
            V2 a = R.Centre + (T.Centre - R.Centre).Norm() * 0.45;
            // 1. both routes open: the obvious (short) one through the gap
            List<Cell> path = CordPlanner.AStar(w, R, T);
            C(path != null && path.Contains(g) && path.Max(c => c.Z) <= R.Z + 1, "maze 1: open maze takes the short route through the gap");
            HoseLay l1 = HoseMath.Lay(w, a, T.Centre, p, 11);
            C(l1.Ok && l1.Flat.All(q => w.IsWalkable(q.Floor)), "maze 1: hose laid, no point inside a wall");
            C(HoseMath.CheckInstall(w, R, T, 20) == null, "maze 1: installable with a 20-cell hose");
            // 2. wall the gap: re-planned from scratch, the hose spirals round the other way
            w.SetBlocked(g, BlockKind.Wall);
            path = CordPlanner.AStar(w, R, T);
            C(path != null && !path.Contains(g) && path.Max(c => c.Z) >= R.Z + 3, "maze 2: gap walled -> the long spiral route over the top");
            HoseLay l2 = HoseMath.Lay(w, a, T.Centre, p, 11);
            C(l2.Ok && l2.PathLen > l1.PathLen * 1.6 && l2.Flat.All(q => w.IsWalkable(q.Floor)) && !HoseMath.SelfIntersects(l2.Flat),
                "maze 2: re-laid along the spiral (" + l2.PathLen.ToString("0.0") + " vs " + l1.PathLen.ToString("0.0") + "), clear of walls, no loops");
            // MEASURED 2026-10-04: a 1-cell corridor cannot hold the hose's 1.2-cell minimum bend -- the stiffened sprawl
            // touches a wall, the lay falls back to the corridor's rounded centreline and the corners bend at ~0.42. That
            // is the corridor's geometric limit (half a cell), not a planner fault; the floor asserted is that limit.
            C(l2.MinBendFlat >= 0.35, "maze 2: corners bend no tighter than a 1-cell corridor allows (" + l2.MinBendFlat.ToString("0.00") + ", fellBack " + l2.FellBack + ")");
            // 3. the length cap: the spiral fits a 30-cell hose but not a 20-cell one (install refuses; the LAY itself has
            //    no cap -- a laid hose re-routed past its length is still drawn; validation_hose.py M3 records that live)
            C(HoseMath.CheckInstall(w, R, T, 30) == null, "maze 3: the spiral fits a 30-cell hose");
            C(HoseMath.CheckInstall(w, R, T, 20) == "route too long", "maze 3: a 20-cell hose refuses the spiral (route too long)");
            // 4. wall the spiral too: unreachable
            w.SetBlocked(b, BlockKind.Wall);
            C(CordPlanner.AStar(w, R, T) == null, "maze 4: both routes walled -> no path");
            C(HoseMath.CheckInstall(w, R, T, 30) == "no route", "maze 4: install refuses (no route)");
            HoseLay l4 = HoseMath.Lay(w, a, T.Centre, p, 11);
            C(!l4.Ok && l4.Reason == "no route", "maze 4: lay fails with 'no route' (live: the hose is not drawn, the reel stays laid)");
            // 5. the A* expansion cap answers 'no route' rather than hanging (a cap of 10 cannot reach T)
            w.SetBlocked(b, BlockKind.None);
            C(CordPlanner.AStar(w, R, T, 10) == null && CordPlanner.AStar(w, R, T) != null, "maze 5: the A* expansion cap gives up cleanly");
        }
            // ------------------------------------------------------------------ round 3: the 2x2 reel (owner 2026-10-04)
        private static void Reel2x2()
        {
            var reel = new HoseReelRect(10, 10, 2, 2);   // cells (10..11, 10..11), centre (11, 11)
            C(Math.Abs(reel.Centre.X - 11) < 1e-9 && Math.Abs(reel.Centre.Z - 11) < 1e-9, "2x2: the hose leaves the reel at its centre (a cell corner)");
            C(reel.Perimeter().Count == 8 && reel.Perimeter().All(c => !reel.Contains(c)), "2x2: 8 edge-sharing neighbour cells, none inside the reel");
            // a 1-cell pipe beside the upper east cell, a 2x2 tank to the south, a pipe touching only a corner
            var pipeE = new HosePortCandidate(12, 11, 1, 1, HosePortKind.Pipe);
            var tankS = new HosePortCandidate(10, 8, 2, 2, HosePortKind.Tank);
            var corner = new HosePortCandidate(12, 12, 1, 1, HosePortKind.Pipe);
            int i = HosePortRule.Pick(reel, new List<HosePortCandidate> { tankS }, out Cell s, out Cell ct);
            C(i == 0 && s == new Cell(0, -1) && ct == new Cell(10, 9), "2x2: a 2x2 tank below couples on the south side, lowest cell along the edge");
            i = HosePortRule.Pick(reel, new List<HosePortCandidate> { tankS, pipeE }, out s, out ct);
            C(i == 1 && s == new Cell(1, 0) && ct == new Cell(12, 11), "2x2: a pipe beside the UPPER east cell couples (pipe over tank)");
            C(HosePortRule.Pick(reel, new List<HosePortCandidate> { corner }, out s, out ct) == -1, "2x2: a corner touch does not couple");
            C(HosePortRule.Pick(reel, new List<HosePortCandidate> { new HosePortCandidate(11, 11, 1, 1, HosePortKind.Pipe) }, out s, out ct) == -1,
                "2x2: a candidate overlapping any reel cell is ignored");
            var pipeE0 = new HosePortCandidate(12, 10, 1, 1, HosePortKind.Pipe);
            i = HosePortRule.Pick(reel, new List<HosePortCandidate> { pipeE, pipeE0 }, out s, out ct);
            C(i == 1 && ct == new Cell(12, 10), "2x2: two pipes on one side tie-break to the lowest cell, not list order");
            var touch = new Cell(ct.X - s.X, ct.Z - s.Z);
            HosePortRule.Feed(touch, s, out V2 from, out V2 to, out V2 cp);
            C(reel.Contains(touch) && Math.Abs(cp.X - 12.0) < 1e-9 && Math.Abs(to.X - 12.5) < 1e-9 && from.X > 11.5 && from.X < 12.0,
                "2x2: the feed starts under the reel's edge cell and crosses the shared edge at x=12");
            // the 1x1 overload still answers as round 2 did
            i = HosePortRule.Pick(new Cell(10, 10), new List<HosePortCandidate> { new HosePortCandidate(11, 10, 1, 1, HosePortKind.Pipe) }, out s);
            C(i == 0 && s == new Cell(1, 0), "2x2: the 1x1 Pick overload is unchanged");
            // install from the 2x2 footprint
            CordWorld w = Open(40, 30);
            C(HoseMath.CheckInstall(w, reel, new Cell(11, 10), 30) == "same cell", "2x2: laying onto any reel cell is refused");
            C(HoseMath.CheckInstall(w, reel, new Cell(20, 11), 30) == null, "2x2: an open target in range is valid");
            C(reel.StartCellToward(new Cell(20, 10)) == new Cell(11, 10), "2x2: the planner starts from the reel cell nearest the target");
            // round 4: the route is measured pulled taut from the hose's mouth under the drum (9.11 cells to (20.5, 11.5))
            // x RouteMargin = 9.56; "too far" still measures from the centre (9.51)
            // round 5: the mouth is the drum's axis (nearer the target than the centre here), so the straight run is exactly
            // mouth -> target; "too far" still measures from the centre
            double rl = HoseMath.RouteLength(w, reel, new Cell(20, 11)), md = V2.Dist(reel.Mouth, new Cell(20, 11).Centre);
            C(Math.Abs(rl - md) < 1e-6 && HoseMath.CheckInstall(w, reel, new Cell(11 + 9, 11), md * HoseMath.RouteMargin - 0.02) != null
                && HoseMath.CheckInstall(w, reel, new Cell(11 + 9, 11), Math.Max(md * HoseMath.RouteMargin, V2.Dist(reel.Centre, new Cell(20, 11).Centre)) + 0.01) == null,
                "2x2: route length counts the run from the drum mouth (" + rl.ToString("0.000") + " = " + md.ToString("0.000") + ")");
            HoseLay l = HoseMath.Lay(w, reel.Centre, new Cell(20, 11).Centre, new HoseShapeParams(), 5);
            C(l.Ok && V2.Dist(l.Flat[0], reel.Centre) < 1e-6, "2x2: the laid hose starts exactly at the reel centre");
        }

        // ------------------------------------------------------------------ round 4 (owner review 2026-10-04 16:19-16:32)
        /// <summary>Stations 22/23 of human_review.py, cell for cell (keep in step with `maze` there): perimeter(0,0,12,10)
        /// with gaps (12,1),(12,2),(12,8),(12,9); the chamber perimeter(4,3,8,7) with its west door (4,5); the spur 9..11 at
        /// z=5. 2x2 reel at (6,5), free end (16,2). Offset into a 30x20 world.</summary>
        public const int SX = 3, SZ = 3;
        public static CordWorld StationMaze(IEnumerable<Cell> extraWalls)
        {
            var w = Open(30, 20);
            var walls = new List<Cell>();
            for (int x = 0; x <= 12; x++) for (int z = 0; z <= 10; z++)
                    if (x == 0 || x == 12 || z == 0 || z == 10) walls.Add(new Cell(x, z));
            walls.RemoveAll(c => c.X == 12 && (c.Z == 1 || c.Z == 2 || c.Z == 8 || c.Z == 9));
            for (int x = 4; x <= 8; x++) for (int z = 3; z <= 7; z++)
                    if ((x == 4 || x == 8 || z == 3 || z == 7) && !(x == 4 && z == 5)) walls.Add(new Cell(x, z));
            for (int x = 9; x <= 11; x++) walls.Add(new Cell(x, 5));
            foreach (Cell c in walls.Concat(extraWalls ?? Enumerable.Empty<Cell>())) w.SetBlocked(new Cell(c.X + SX, c.Z + SZ), BlockKind.Wall);
            return w;
        }

        /// <summary>Fine-sampled (0.02 cell) count of hose centreline samples inside a blocked cell, ends excluded.</summary>
        public static int WallHits(CordWorld w, IList<V2> pts)
        {
            int hits = 0;
            for (int i = 1; i < pts.Count; i++)
            {
                double d = V2.Dist(pts[i - 1], pts[i]);
                int k = Math.Max(1, (int)Math.Ceiling(d / 0.02));
                for (int j = 0; j < k; j++)
                {
                    V2 q = pts[i - 1] + (pts[i] - pts[i - 1]) * (j / (double)k);
                    if ((i > 1 || j > 0) && HoseMath.WallDepth(w, q) > HoseMath.ClipTolerance) hits++;
                }
            }
            return hits;
        }

        /// <summary>Largest distance of the pose points within half of sample j (by arc) from that run's chord.</summary>
        public static double RunDeviation(IList<V2> P, int j, double half)
        {
            double[] s = Geo.CumLen(P);
            var run = Enumerable.Range(0, P.Count).Where(i => Math.Abs(s[i] - s[j]) <= half - 0.05).ToList();
            if (run.Count < 2) return 0;
            V2 a = P[run[0]], b = P[run[run.Count - 1]], d = (b - a).Norm();
            return run.Max(i => Math.Abs((P[i].X - a.X) * d.Z - (P[i].Z - a.Z) * d.X));
        }

        private static void Round4()
        {
            var reel = new HoseReelRect(6 + SX, 5 + SZ, 2, 2);
            var far = new Cell(16 + SX, 2 + SZ);
            var block = new[] { new Cell(12, 1), new Cell(12, 2) };
            // the owner's own walls in station 23 (read off his screenshot 20261004163103_1.jpg on a cell grid): stubs in
            // the north corridor and a wall closing the chamber's west corridor, so the only way out runs south, up the far
            // west side and zig-zags along the top
            var owner = new List<Cell> { new Cell(2, 9), new Cell(6, 9), new Cell(11, 9), new Cell(4, 8), new Cell(8, 8), new Cell(10, 8),
                new Cell(10, 7), new Cell(3, 7) };
            for (int z = 2; z <= 7; z++) owner.Add(new Cell(2, z));
            var sp = new HoseShapeParams { MaxLength = 30 };
            // the hose leaves the 2x2 reel under its drum (east half, front), inside the footprint, not at the pump-side centre
            V2 m0 = reel.Mouth, c0 = reel.Centre;
            C(reel.Contains(m0.Floor) && m0.X > c0.X + 0.3 && new HoseReelRect(4, 4, 1, 1).Mouth.X == 4.5,
                "r4 reel: the hose leaves the 2x2 reel under its drum, drum side (" + (m0.X - c0.X).ToString("0.00") + ", " + (m0.Z - c0.Z).ToString("0.00") + " from the centre); a 1x1 reel keeps its centre");
            // station 22: the short way out fits a 30-cell hose and is laid clear of every wall
            CordWorld w = StationMaze(null);
            double r22 = HoseMath.RouteLength(w, reel, far);
            HoseLay l22 = HoseMath.Lay(w, reel.Mouth, far.Centre, sp, 7);
            C(HoseMath.CheckInstall(w, reel, far, 30) == null && l22.Ok && WallHits(w, l22.Flat) == 0 && WallHits(w, l22.Plump) == 0,
                "r4 st22: the short route (" + r22.ToString("0.0") + " cells) is laid clear of every wall");
            // station 23 as designed: the short gap walled -> the north-east way still fits (re-route, stays laid)
            w = StationMaze(block);
            double r23 = HoseMath.RouteLength(w, reel, far);
            HoseLay l23 = HoseMath.Lay(w, reel.Mouth, far.Centre, sp, 7);
            C(HoseMath.CheckReplan(w, reel, far, 30, false, null) == null && r23 * HoseMath.RouteMargin <= 27 && l23.Ok && WallHits(w, l23.Flat) == 0
                && l23.FlatLen <= 30 && l23.PlumpLen <= 30,
                "r4 st23 designed: walled short way -> the long way (" + r23.ToString("0.0") + " cells, laid " + l23.FlatLen.ToString("0.0") + ") re-routes inside a 30-cell hose with margin");
            // station 23 with the owner's walls: completable as a maze, but the way out is longer than the hose
            w = StationMaze(block.Concat(owner));
            double ro = HoseMath.RouteLength(w, reel, far);
            C(ro > 32 && ro < 40, "r4 owner maze: the only way out pulls taut at " + ro.ToString("0.0") + " cells (the round-3 staircase sum read 44.9 x1.08 = 48.5)");
            C(HoseMath.CheckReplan(w, reel, far, 30, false, null) == "route too long", "r4 owner maze: a 30-cell hose cannot reach -> retract, 'route too long'");
            C(HoseMath.CheckInstall(w, reel, far, 40) == null, "r4 owner maze: a 40-cell hose (Mod Settings) takes it");
            HoseLay lo = HoseMath.Lay(w, reel.Mouth, far.Centre, new HoseShapeParams { MaxLength = 40 }, 7);
            C(lo.Ok && WallHits(w, lo.Flat) == 0 && WallHits(w, lo.Plump) == 0 && HoseMath.Clear(w, lo.Flat),
                "r4 owner maze: laid with a 40-cell hose, the hose never crosses a wall stub (round 3 cut 28 fine samples through walls)");
            C(lo.FlatLen <= 40 + 1e-6 && lo.PlumpLen <= 40 + 1e-6, "r4 owner maze: the laid hose (" + lo.FlatLen.ToString("0.0") + ") is never longer than the hose");
            // the clear test itself: a pinched diagonal (two wall cells corner to corner) is not a gap
            var pw = Open(10, 10);
            pw.SetBlocked(new Cell(5, 5), BlockKind.Wall);
            pw.SetBlocked(new Cell(4, 4), BlockKind.Wall);
            C(!HoseMath.SegmentClear(pw, new V2(3.5, 5.5), new V2(5.5, 3.5)) && HoseMath.SegmentClear(pw, new V2(3.5, 6.5), new V2(6.5, 6.5)),
                "r4 clear: a line through two walls' touching corners is blocked; an open line is clear");
            // slack never makes a hose longer than its reel: a route of ~19.6 under a 21-cell hose
            w = StationMaze(null);
            HoseLay tight = HoseMath.Lay(w, reel.Mouth, far.Centre, new HoseShapeParams { MaxLength = 21, Slack = 2 }, 3);
            // station 22's joiner: every joiner sits on a straight run of the drawn hose (flat and plump), its axis the run's
            // chord, so the two couplings line up with both hose lengths (owner: "improper connectivity of two pipe segments")
            double half = HoseMath.JoinerHalf(HoseMath.VisibleWidth(1, 1));
            int joints = 0;
            double worst = 0;
            foreach (HoseLay lj in new[] { l22, l23, lo })
                foreach (int j in lj.Joints)
                {
                    joints++;
                    worst = Math.Max(worst, Math.Max(RunDeviation(lj.Flat, j, half), RunDeviation(lj.Plump, j, half)));
                }
            C(joints > 0 && worst < 0.02, "r4 joiners: " + joints + " joiners on stations 22/23 + the owner maze, each on a straight run (worst off-axis " + worst.ToString("0.000") + " cell)");
            // an L bend in the open: the joiner leaves the apex for the straight run beside it
            var lw = Open(30, 30);
            for (int x = 0; x < 30; x++) for (int z = 0; z < 30; z++) if (!(x >= 4 && x <= 6 && z >= 4 && z <= 22) && !(z >= 20 && z <= 22 && x >= 4 && x <= 25)) lw.SetBlocked(new Cell(x, z), BlockKind.Wall);
            HoseLay ll = HoseMath.Lay(lw, new V2(5.5, 4.5), new V2(24.5, 21.5), new HoseShapeParams(), 9);
            var apex = new V2(5.5, 21.5);
            C(ll.Ok && ll.Joints.Count == 1 && V2.Dist(ll.Centre[ll.Joints[0]], apex) > half && RunDeviation(ll.Flat, ll.Joints[0], half) < 0.02,
                "r4 joiners: an L-bend's joiner sits on the straight beside the corner (" + (ll.Joints.Count > 0 ? V2.Dist(ll.Centre[ll.Joints[0]], apex).ToString("0.0") : "none") + " cells from the apex), not across it");
            Console.WriteLine($"  hose r4: st22 route {r22:0.0} laid {l22.FlatLen:0.0}; st23 route {r23:0.0} laid {l23.FlatLen:0.0}; owner maze route {ro:0.0} (40-cell lay {lo.FlatLen:0.0}); slack cap {tight.FlatLen:0.0}/21; joiners st22 {l22.Joints.Count} st23 {l23.Joints.Count} owner {lo.Joints.Count} (bends {HoseMath.Joints(l22.Centre, 8).Count}/{HoseMath.Joints(l23.Centre, 8).Count}/{HoseMath.Joints(lo.Centre, 8).Count})");
            C(tight.Ok && tight.FlatLen <= 21 + 1e-6 && tight.PlumpLen <= 21 + 1e-6, "r4 slack cap: a 21-cell hose on a " + r22.ToString("0.0") + "-cell route lays " + tight.FlatLen.ToString("0.0"));
        }

        /// <summary>A square spiral maze, n x n (wall spiral, one-cell corridor), set 2 cells in from the world's edge. The
        /// way in is the gap at the outer ring's west end; the reel (1x1) sits at the corridor's innermost dead end (the
        /// cell farthest from the way in), and the free end is 2 cells outside the gap.</summary>
        public static CordWorld Spiral(int n, out HoseReelRect reel, out Cell exit)
        {
            const int O = 2;
            var w = Open(n + 2 * O, n + 2 * O);
            var walls = new HashSet<Cell>();
            int x = 0, z = n - 1, k = 0;
            var dirs = new[] { new Cell(1, 0), new Cell(0, -1), new Cell(-1, 0), new Cell(0, 1) };
            var lens = new List<int> { n - 1, n - 1, n - 1 };
            for (int L = n - 3; L > 0; L -= 2) { lens.Add(L); lens.Add(L); }
            walls.Add(new Cell(x, z));
            foreach (int L in lens)
            {
                Cell d = dirs[k++ % 4];
                for (int i = 0; i < L; i++) { x += d.X; z += d.Z; walls.Add(new Cell(x, z)); }
            }
            foreach (Cell c in walls) w.SetBlocked(new Cell(c.X + O, c.Z + O), BlockKind.Wall);
            exit = new Cell(O - 2, n - 2 + O);
            // the innermost dead end: the walkable maze cell farthest (BFS) from the way in
            var dist = new Dictionary<Cell, int> { [new Cell(O, n - 2 + O)] = 0 };
            var q = new Queue<Cell>(dist.Keys);
            Cell far = new Cell(O, n - 2 + O);
            while (q.Count > 0)
            {
                Cell c = q.Dequeue();
                if (dist[c] > dist[far]) far = c;
                foreach (Cell d in dirs)
                {
                    Cell nb = c + d;
                    if (nb.X < O || nb.Z < O || nb.X >= O + n || nb.Z >= O + n || !w.IsWalkable(nb) || dist.ContainsKey(nb)) continue;
                    dist[nb] = dist[c] + 1;
                    q.Enqueue(nb);
                }
            }
            reel = new HoseReelRect(far.X, far.Z, 1, 1);
            return w;
        }

        // ------------------------------------------------------------------ round 5 (owner 2026-10-04)
        private static void Round5()
        {
            string perf;
            // owner 2026-10-05: the hose starts at the reel's brass outlet nozzle (west side), not under the drum
            var reel = new HoseReelRect(6 + SX, 5 + SZ, 2, 2);
            V2 m = reel.Mouth, c = reel.Centre, tip = reel.NozzleTip;
            C(reel.Contains(m.Floor) && m.X - c.X < -0.9 && Math.Abs(m.Z - c.Z) < 0.15 && tip.X < reel.X0 - 0.2 && Math.Abs(tip.Z - m.Z) < 1e-9
                && reel.HasNozzle && !new HoseReelRect(4, 4, 1, 1).HasNozzle,
                "nozzle: the hose starts on the west edge at the outlet's height (" + (m.X - c.X).ToString("0.00") + ", " + (m.Z - c.Z).ToString("0.00") + " from the centre) and the coupling meets the nozzle tip "
                + (tip.X - c.X).ToString("0.00") + " from the centre; a 1x1 reel has no nozzle");
            // a hose laid south from the reel: its first sample is the mouth, so its end sits at the axis, not below the drum
            CordWorld ow = Open(30, 30);
            var r2 = new HoseReelRect(10, 20, 2, 2);
            HoseLay ls = HoseMath.Lay(ow, r2.Mouth, new V2(11.5, 6.5), new HoseShapeParams { MaxLength = 30 }, 4);
            C(ls.Ok && V2.Dist(ls.Flat[0], r2.Mouth) < 1e-6 && Math.Abs(ls.Flat[0].Z - (r2.Centre.Z + HoseReelRect.MouthDZ)) < 1e-6,
                "nozzle: a hose laid south still starts at the outlet (" + ls.Flat[0].Z.ToString("0.00") + ")");

            // station 34 (old 22) with the owner's walls, read cell for cell off 20261004210108_1.jpg: the north-east gap
            // shut by (12,8) and (11,9) (a pinched diagonal), the south way out of the west corridor by (3,2), the south-east
            // corridor by (10,1..3). The one way left runs out the chamber's west door, north, round the far west side, along
            // the bottom and up and over (10,1..3) to the south-east gap.
            var owner = new List<Cell> { new Cell(12, 8), new Cell(11, 9), new Cell(3, 2), new Cell(10, 1), new Cell(10, 2), new Cell(10, 3) };
            for (int z = 3; z <= 8; z++) owner.Add(new Cell(2, z));
            CordWorld w = StationMaze(owner);
            var far = new Cell(16 + SX, 2 + SZ);
            double bounded = HoseMath.RouteLength(w, reel, far, 30);
            int expB = HoseMath.LastRouteExpanded;
            double unb = HoseMath.RouteLength(w, reel, far);
            int expU = HoseMath.LastRouteExpanded;
            List<Cell> old20k = CordPlanner.AStar(w, reel.StartCellToward(far), far, 20000);
            string why = HoseMath.CheckReplan(w, reel, far, 30, false, null);
            C(bounded > 0 && Math.Abs(bounded - unb) < 1e-9 && old20k != null && why == "route too long" && unb * HoseMath.RouteMargin > 30
                && Math.Ceiling(unb * HoseMath.RouteMargin) >= 33 && Math.Ceiling(unb * HoseMath.RouteMargin) <= 35,
                "r5 st34: the owner's maze is FOUND (taut " + unb.ToString("0.0") + " cells, x" + HoseMath.RouteMargin + " = " + (unb * HoseMath.RouteMargin).ToString("0.0")
                + "; the game said 34) and is longer than the 30-cell hose -> 'route too long', the length rule, not the search");
            C(HoseMath.CheckInstall(w, reel, far, 36) == null, "r5 st34: a 36-cell hose (Mod Settings) takes the owner's maze");

            // the spiral: every route within the hose's length is found, however winding; the search stays inside the
            // (2 x bound + 1)^2 square round the reel
            var rows = new List<string>();
            bool allFound = true, bounds = true;
            foreach (int turns in new[] { 7, 9, 11, 13 })
            {
                CordWorld sw = Spiral(turns, out HoseReelRect sr, out Cell ex);
                double full = HoseMath.RouteLength(sw, sr, ex);
                int fe = HoseMath.LastRouteExpanded;
                if (full < 0) { allFound = false; rows.Add(turns + "x" + turns + ": NO ROUTE"); continue; }
                double hose = Math.Ceiling(full * HoseMath.RouteMargin) + 1;
                double got = HoseMath.RouteLength(sw, sr, ex, hose);
                int ge = HoseMath.LastRouteExpanded;
                double lim = HoseMath.SearchLengthBound(hose);
                if (got < 0 || Math.Abs(got - full) > 1e-6 || HoseMath.CheckInstall(sw, sr, ex, hose) != null) allFound = false;
                if (ge > Math.Pow(2 * Math.Ceiling(lim) + 3, 2) || HoseMath.LastRouteCapped) bounds = false;
                if (HoseMath.CheckInstall(sw, sr, ex, hose - 3) != "route too long") allFound = false;
                rows.Add(turns + "x" + turns + ": route " + full.ToString("0.0") + ", hose " + hose + " found it in " + ge + " expansions (unbounded " + fe + ")");
            }
            C(allFound && bounds, "r5 spiral: every spiral maze (7x7 to 13x13) is found by a hose just long enough and refused 'route too long' by one 3 cells shorter; " + string.Join("; ", rows));
            // performance bound: a 250x250 open map with the free end walled into a box -- the bounded search stops inside
            // its square, the unbounded one (telling "no route" from "too long") at RouteMaxExpand
            CordWorld big = Open(250, 250);
            for (int x = 139; x <= 141; x++) for (int z = 124; z <= 126; z++) if (x != 140 || z != 125) big.SetBlocked(new Cell(x, z), BlockKind.Wall);
            var br = new HoseReelRect(120, 124, 2, 2);
            var sw0 = System.Diagnostics.Stopwatch.StartNew();
            double bb = HoseMath.RouteLength(big, br, new Cell(140, 125), 30);
            int bexp = HoseMath.LastRouteExpanded;
            long bms = sw0.ElapsedMilliseconds;
            sw0.Restart();
            string bwhy = HoseMath.CheckInstall(big, br, new Cell(140, 125), 30);
            int uexp = HoseMath.LastRouteExpanded;
            long ums = sw0.ElapsedMilliseconds;
            C(bb < 0 && bexp <= Math.Pow(2 * Math.Ceiling(HoseMath.SearchLengthBound(30)) + 3, 2) && bwhy == "no route" && uexp <= HoseMath.RouteMaxExpand + 1,
                "r5 bound: a boxed-in free end on a 250x250 map: the 30-cell hose's search opens " + bexp + " cells (" + bms + " ms), the no-route check " + uexp + " (" + ums + " ms)");
            perf = "boxed target 250x250: bounded " + bexp + " cells " + bms + " ms, unbounded " + uexp + " cells " + ums + " ms";
            Console.WriteLine("  hose r5: " + perf + "; st34 owner maze taut " + unb.ToString("0.0") + " (needs " + Math.Ceiling(unb * HoseMath.RouteMargin) + "), bounded search " + expB + " expansions, unbounded " + expU + "; spiral " + string.Join("; ", rows));
        }

        // ------------------------------------------------------------------ HOSE_BLOCKED_REROUTE_RETRACT_1 (owner card 2026-10-04)
        private static void Replan()
        {
            CordWorld w = MazeWorld(3, 3, out Cell R, out Cell T, out Cell g, out Cell b);
            var reel = new HoseReelRect(R.X, R.Z, 1, 1);
            C(HoseMath.CheckReplan(w, reel, T, 30, false, null) == null, "replan: open maze keeps the hose");
            w.SetBlocked(g, BlockKind.Wall);
            C(HoseMath.CheckReplan(w, reel, T, 30, false, null) == null, "replan: gap walled, the spiral fits a 30-cell hose -> re-route, stay laid");
            C(HoseMath.CheckReplan(w, reel, T, 20, false, null) == "route too long", "replan: gap walled, a 20-cell hose cannot take the spiral -> retract (length enforced on re-plan)");
            w.SetBlocked(b, BlockKind.Wall);
            C(HoseMath.CheckReplan(w, reel, T, 30, false, null) == "no route", "replan: both routes walled -> retract (no route)");
            w.SetBlocked(b, BlockKind.None);
            w.SetBlocked(T, BlockKind.Wall);
            C(HoseMath.CheckReplan(w, reel, T, 30, false, null) == "target blocked", "replan: a wall built on the free end -> retract");
            w.SetBlocked(T, BlockKind.None);
            C(HoseMath.CheckReplan(w, reel, T, 30, true, "no route") == "no route", "replan: a lay that failed although the route check passes is retracted, never left invisible");
            C(HoseMath.CheckReplan(w, reel, T, 30, true, null) == "could not be laid", "replan: a failed lay with no reason still retracts");
        }
    }
}
