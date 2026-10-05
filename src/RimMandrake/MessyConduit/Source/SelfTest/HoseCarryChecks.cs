// Colonist-carried hose, stage S1 selftest rows 1-5 (design/RimMandrake/hose_carry_design_2026-10-04.md section 13).
// Every row has a can-fail: a mutated rule that the same assertion must reject.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.MessyConduit.Core;
using RimMandrake.MessyConduit.Hose;

namespace RimMandrake.MessyConduit.SelfTest
{
    internal static class HoseCarryChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "hosecarry: " + msg);

        private const HoseCarryState S = HoseCarryState.Stored, C = HoseCarryState.Carrying, D = HoseCarryState.Dropped, L = HoseCarryState.Laid, R = HoseCarryState.Retracting;
        private static readonly HoseCarryState[] All = { S, C, D, L, R };

        // The section 3 table, written out independently of HoseCarryTable (event, from, to).
        private static readonly (HoseCarryEvent, HoseCarryState, HoseCarryState)[] Spec =
        {
            (HoseCarryEvent.Grab, S, C), (HoseCarryEvent.Step, C, C), (HoseCarryEvent.Stretch, C, D), (HoseCarryEvent.Stow, C, S),
            (HoseCarryEvent.SetDown, C, L), (HoseCarryEvent.Interrupt, C, D),
            (HoseCarryEvent.PickUp, L, C), (HoseCarryEvent.PickUp, D, C), (HoseCarryEvent.Wind, L, R), (HoseCarryEvent.Wind, D, R),
            (HoseCarryEvent.Replan, L, L), (HoseCarryEvent.Replan, D, D), (HoseCarryEvent.ReplanFail, L, R), (HoseCarryEvent.ReplanFail, D, R),
            (HoseCarryEvent.WindDone, R, S), (HoseCarryEvent.WindInterrupt, R, D),
            (HoseCarryEvent.ReelGone, S, S), (HoseCarryEvent.ReelGone, C, S), (HoseCarryEvent.ReelGone, D, S), (HoseCarryEvent.ReelGone, L, S), (HoseCarryEvent.ReelGone, R, S),
            (HoseCarryEvent.DevLay, S, L), (HoseCarryEvent.DevLay, L, L), (HoseCarryEvent.DevLay, D, L),
            (HoseCarryEvent.DevReelIn, S, S), (HoseCarryEvent.DevReelIn, L, S), (HoseCarryEvent.DevReelIn, D, S),
        };

        private static bool TableMatchesSpec(Dictionary<(HoseCarryState, HoseCarryEvent), HoseCarryState> t, out string why)
        {
            why = null;
            foreach (HoseCarryState s in All)
                foreach (HoseCarryEvent e in Enum.GetValues(typeof(HoseCarryEvent)))
                {
                    var hit = Spec.Where(x => x.Item1 == e && x.Item2 == s).ToList();
                    HoseCarryState? got = HoseCarryTable.Next(s, e, t);
                    if (hit.Count == 1 ? got != hit[0].Item3 : got != null) { why = s + "+" + e + " -> " + (got?.ToString() ?? "refused"); return false; }
                }
            return true;
        }

        private static CordWorld Open(int w = 120, int h = 40) => new CordWorld(w, h);

        public static void Run()
        {
            Row1Table();
            Row2Trail();
            Row3Stretch();
            Row4Random();
            Row5Clip();
        }

        private static void Row1Table()
        {
            Check(TableMatchesSpec(HoseCarryTable.Default, out string why), "row1 every (state, event) pair matches design section 3, every other refused (" + why + ")");
            Check(Spec.Length == 27 && HoseCarryTable.Default.Count == 27, "row1 the table has the 27 rows of section 3 (" + HoseCarryTable.Default.Count + ")");
            // can-fail: without Carrying->Dropped on Interrupt the check must reject, and a machine must stop dropping
            var mut = HoseCarryTable.Build();
            mut.Remove((C, HoseCarryEvent.Interrupt));
            Check(!TableMatchesSpec(mut, out _), "row1 can-fail: a table without the Carrying->Dropped interrupt row is rejected");
            var m = new HoseCarryMachine(Open(), new V2(10.5, 10.5), 40) { Table = mut };
            m.Grab(new Cell(10, 10));
            Check(!m.Interrupt() && m.State == C, "row1 can-fail: the mutant machine cannot drop on interrupt");
            var ok = new HoseCarryMachine(Open(), new V2(10.5, 10.5), 40);
            ok.Grab(new Cell(10, 10)); ok.CarrierStep(new Cell(11, 10));
            Check(ok.Interrupt() && ok.State == D && ok.Far == new Cell(11, 10) && ok.PendingKept, "row1 interrupt drops the end at the last trail cell, pending kept");
        }

        private static HoseTrail Walk(CordWorld w, HoseTrail t, params (int x, int z)[] legs)
        {
            // legs are waypoints; walk axis-aligned cell by cell
            Cell cur = t.Last;
            foreach (var (x, z) in legs)
                while (cur.X != x || cur.Z != z)
                {
                    cur = new Cell(cur.X + Math.Sign(x - cur.X), cur.Z + (cur.X != x ? 0 : Math.Sign(z - cur.Z)));
                    if (t.Step(cur, w) == TrailStep.Stretched) return t;
                }
            return t;
        }

        private static void Row2Trail()
        {
            CordWorld w = Open();
            var t = new HoseTrail(new Cell(10, 10).Centre, 40);
            t.Begin(new Cell(10, 10));
            Walk(w, t, (20, 10));
            Check(t.Cells.Count - 1 == 10, "row2 walk out 10 -> 10 steps on the trail (" + (t.Cells.Count - 1) + ")");
            Walk(w, t, (16, 10));
            Check(t.Cells.Count - 1 == 6 && t.Last == new Cell(16, 10), "row2 back 4 -> trail 6 (" + (t.Cells.Count - 1) + ")");
            TrailStep last = TrailStep.Unchanged;
            for (int x = 15; x >= 10; x--) last = t.Step(new Cell(x, 10), w);
            Check(last == TrailStep.Stowed && t.Cells.Count == 1, "row2 walking all the way back to the reel stows the hose");
            var m = new HoseCarryMachine(w, new Cell(10, 10).Centre, 40);
            m.Grab(new Cell(10, 10)); m.CarrierStep(new Cell(11, 10)); m.CarrierStep(new Cell(10, 10));
            Check(m.State == S && m.Invariant() == null, "row2 machine: back at the reel -> Stored");
            // can-fail: no truncate rule leaves 14
            var nt = new HoseTrail(new Cell(10, 10).Centre, 40) { TruncateOnRevisit = false };
            nt.Begin(new Cell(10, 10));
            Walk(w, nt, (20, 10), (16, 10));
            Check(nt.Cells.Count - 1 != 6 && nt.Cells.Count - 1 == 14, "row2 can-fail: a no-truncate rule leaves 14 (" + (nt.Cells.Count - 1) + ")");

            // U-walk round a wall stub pulls taut: wall x=15, z 10..16; walk (10,13) up round the top and down the far side.
            CordWorld u = Open();
            for (int z = 10; z <= 16; z++) u.SetBlocked(new Cell(15, z), BlockKind.Wall);
            var ut = new HoseTrail(new Cell(10, 13).Centre, 60);
            ut.Begin(new Cell(10, 13));
            Walk(u, ut, (14, 13), (14, 17), (16, 17), (16, 13), (20, 13));
            double want = 2 * Math.Sqrt(41);   // (10.5,13.5)->(15.5,17.5)->(20.5,13.5): the farthest walked cell centre in view each time, hand-derived
            double got = ut.PulledLength(u);
            Check(Math.Abs(got - want) < 0.01, "row2 U-walk round a wall stub pulls taut to " + want.ToString("0.000") + " (" + got.ToString("0.000") + ")");
            Check(got < ut.Cells.Count - 1 && got > 10, "row2 the pulled hose is shorter than the walked cells (" + got.ToString("0.0") + " < " + (ut.Cells.Count - 1) + ")");
            Check(HoseMath.SegmentClear(u, new Cell(10, 13).Centre, new Cell(20, 13).Centre) == false, "row2 the straight line through the stub is blocked (fixture sanity)");
        }

        private static void Row3Stretch()
        {
            CordWorld w = Open();
            var t = new HoseTrail(new Cell(10, 10).Centre, 40);
            t.Begin(new Cell(10, 10));
            int stoppedAt = -1;
            for (int i = 1; i <= 50; i++)
                if (t.Step(new Cell(10 + i, 10), w) == TrailStep.Stretched) { stoppedAt = i; break; }
            Check(stoppedAt == 41 && t.Last == new Cell(50, 10) && t.PulledLength(w) <= 40 + 1e-9,
                "row3 a 50-cell walk with MaxLength 40 stops at cell 41 and the end lies at 40 (stopped " + stoppedAt + ", last " + t.Last + ")");
            var m = new HoseCarryMachine(w, new Cell(10, 10).Centre, 40);
            m.Grab(new Cell(10, 10));
            for (int i = 1; i <= 50 && m.State == C; i++) m.CarrierStep(new Cell(10 + i, 10));
            Check(m.State == D && m.Far == new Cell(50, 10) && !m.PendingKept && m.Invariant() == null, "row3 machine: full stretch drops, pending cleared");
            // can-fail: a longer limit must not stop at 41
            var t2 = new HoseTrail(new Cell(10, 10).Centre, 60);
            t2.Begin(new Cell(10, 10));
            bool stopped = false;
            for (int i = 1; i <= 50; i++) if (t2.Step(new Cell(10 + i, 10), w) == TrailStep.Stretched) { stopped = true; break; }
            Check(!stopped, "row3 can-fail: with MaxLength 60 the same walk is not stopped");
        }

        private static void Row4Random()
        {
            var evs = new[] { "grab", "step", "step", "step", "step", "setdown", "interrupt", "pickup", "wind", "windby", "windint", "replan", "replanbad", "reelgone", "devlay", "devlaybad", "devreelin" };
            int seen = 0, bad = 0; string first = null;
            var visited = new HashSet<HoseCarryState>();
            for (int seed = 1; seed <= 200; seed++)
            {
                var rng = new Random(seed);
                CordWorld w = Open(60, 30);
                for (int i = 0; i < 40; i += 3) w.SetBlocked(new Cell(30, 2 + i % 20), BlockKind.Wall);
                var m = new HoseCarryMachine(w, new Cell(10, 10).Centre, 40);
                var cur = new Cell(10, 10);
                for (int step = 0; step < 120; step++)
                {
                    switch (evs[rng.Next(evs.Length)])
                    {
                        case "grab": m.Grab(new Cell(10, 10)); cur = new Cell(10, 10); break;
                        case "step": { Cell n = new Cell(cur.X + rng.Next(-1, 2), cur.Z + rng.Next(-1, 2)); if (w.IsWalkable(n)) { if (m.State == C) { m.CarrierStep(n); if (m.State == C) cur = n; } } break; }
                        case "setdown": m.SetDown(); break;
                        case "interrupt": m.Interrupt(); break;
                        case "pickup": if (m.PickUp()) cur = m.Trail.Last; break;
                        case "wind": m.BeginWind(); break;
                        case "windby": m.WindBy(rng.NextDouble() * 6); break;
                        case "windint": m.WindInterrupt(); break;
                        case "replan": m.Replan(Line(10, 10, 5 + rng.Next(25))); break;
                        case "replanbad": m.Replan(Line(10, 10, 60)); break;
                        case "reelgone": m.ReelGone(); break;
                        case "devlay": m.DevLay(Line(10, 10, 1 + rng.Next(35))); break;
                        case "devlaybad": m.DevLay(Line(10, 10, 55)); break;
                        case "devreelin": m.DevReelIn(); break;
                    }
                    seen++;
                    visited.Add(m.State);
                    string inv = m.Invariant();
                    if (inv != null) { bad++; first ??= "seed " + seed + " step " + step + ": " + inv; }
                }
            }
            Check(bad == 0, "row4 invariants hold after every step of 200 seeded sequences (" + seen + " steps; " + (first ?? "clean") + ")");
            Check(visited.Count == 5, "row4 the random walk reaches all 5 states (" + visited.Count + ")");
            // can-fail: break the Carrying <=> carrier invariant by hand
            var b = new HoseCarryMachine(Open(), new V2(10.5, 10.5), 40);
            b.Grab(new Cell(10, 10)); b.HasCarrier = false;
            Check(b.Invariant() != null, "row4 can-fail: a Carrying hose with no carrier is flagged");
        }

        private static List<Cell> Line(int x, int z, int n)
        {
            var l = new List<Cell>();
            for (int i = 0; i <= n; i++) l.Add(new Cell(x + i, z));
            return l;
        }

        private static void Row5Clip()
        {
            var p = new List<V2> { new V2(0, 0), new V2(10, 0), new V2(10, 7), new V2(3, 7) };
            double L = Geo.Length(p);   // 24
            int bad = 0;
            foreach (double wound in new[] { 0.0, 0.5, 5, 10, 12.25, 17, 23.9, 24 })
            {
                double got = Geo.Length(HoseTrail.Clip(p, wound));
                if (Math.Abs(got - (L - wound)) > 1e-6) bad++;
            }
            Check(bad == 0 && Math.Abs(L - 24) < 1e-9, "row5 winding w cells from a lay of length L leaves a drawn length L - w (bad " + bad + ")");
            List<V2> c = HoseTrail.Clip(p, 12);
            Check(Math.Abs(c[c.Count - 1].X - 10) < 1e-9 && Math.Abs(c[c.Count - 1].Z - 2) < 1e-9, "row5 the cut point is interpolated on the right segment (" + c[c.Count - 1] + ")");
            // can-fail: a clip that wound the wrong way (kept 'wound' instead of L - wound) is not L - w
            Check(Math.Abs(Geo.Length(HoseTrail.Clip(p, 17)) - 17) > 1, "row5 can-fail: clipping 17 does not leave 17");
            // trail-level: ShortenBy drops cells so the pulled length falls by at least the wound length less one cell
            CordWorld w = Open();
            var t = new HoseTrail(new Cell(10, 10).Centre, 40);
            t.Begin(new Cell(10, 10));
            for (int i = 1; i <= 30; i++) t.Step(new Cell(10 + i, 10), w);
            double before = t.PulledLength(w);
            t.ShortenBy(12, w);
            double after = t.PulledLength(w);
            Check(Math.Abs((before - after) - 12) <= 1.0, "row5 trail ShortenBy 12 shortens the pulled hose by 12 within one sample (" + (before - after).ToString("0.0") + ")");
        }
    }
}
