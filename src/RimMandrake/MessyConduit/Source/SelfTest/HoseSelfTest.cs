// Messy Conduit L6 (fire hoses) offline checks: the Verse-free half of the hose feature
// (Source/Hose/HoseMath.cs, the PRODUCTION file, compiled in directly). Design:
// design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md section 3. Called from Program.Main.
// Written red-first (2026-10-02): every case below failed against a stub HoseMath before the real one.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.MessyConduit.Core;
using RimMandrake.MessyConduit.Hose;

namespace RimMandrake.MessyConduit.SelfTest
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
            Console.WriteLine($"hose: {mine - mineFails}/{mine} checks passed");
        }

        // ------------------------------------------------------------------ width rules
        private static void Widths()
        {
            double wire = HoseMath.WireVisibleWidth;
            double f = HoseMath.VisibleWidth(0, 1), p = HoseMath.VisibleWidth(1, 1);
            C(wire > 0.05 && wire < 0.12, "wire visible width is the strand's band (" + wire.ToString("0.000") + ")");
            C(f >= 4 * wire && f <= 5.5 * wire, "flat hose is 4-5x a wire (" + (f / wire).ToString("0.00") + "x)");
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
            int want = (int)Math.Floor(lay.FlatLen / p.CouplingSpacing) + 2;
            C(lay.Couplings.Count == want, "couplings at both ends and every " + p.CouplingSpacing + " cells (" + lay.Couplings.Count + " vs " + want + ")");
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
    }
}
