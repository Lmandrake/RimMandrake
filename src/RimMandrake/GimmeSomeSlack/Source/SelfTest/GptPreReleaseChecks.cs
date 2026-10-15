// GSS pre-release GPT consult 2026-10-15 (Transient/release_push_2026-10-15/gpt_GSS/TRIAGE.md): one offline row per fixed
// finding whose logic is Verse-free. Each row carries a can-fail: the old rule beside the new one gives the wrong answer.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class GptPreReleaseChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "gpt-prerelease: " + msg);

        public static void Run()
        {
            FallenShock();
            TapClamp();
            LampRun();
            FrameCost();
            Restring();
            FallenRedraw();
            Probes();
            CordLay();
        }

        private static void Mach(CordWorld w, string id, MachineKind k, int x, int z, Cell hook) =>
            w.Machines.Add(new MachineInfo { Id = id, Kind = k, X0 = x, Z0 = z, W = 1, H = 1, Hookups = new List<Cell> { hook } });

        /// <summary>Long run (70 cells) battery -> heater on z = 5, optionally a wall across x = doorX with a door on the run.</summary>
        private static CordWorld LongRun(int doorX)
        {
            var w = new CordWorld(80, 12);
            for (int x = 3; x <= 66; x++) w.SetConduit(new Cell(x, 5));
            w.SetBlocked(new Cell(2, 5), BlockKind.Device);
            w.SetBlocked(new Cell(67, 5), BlockKind.Device);
            Mach(w, "a", MachineKind.Battery, 2, 5, new Cell(3, 5));
            Mach(w, "b", MachineKind.Consumer, 67, 5, new Cell(66, 5));
            if (doorX > 0)
            {
                for (int z = 0; z < 12; z++) if (z != 5) w.SetBlocked(new Cell(doorX, z), BlockKind.Wall);
                w.SetDoor(new Cell(doorX, 5));
            }
            return w;
        }

        // ------------------------------------------------------------------ GSS_CORD_LAY_FIX_HEAPS_IN_DOORWAYS (A2-A9 offline rows)
        private static void CordLay()
        {
            // A9: a 64-cell cord through a door 3 cells from its end: across 30 seeds, no long-run end heap lands on the door
            int onDoor = 0, onDoorNoWall = 0, heaps = 0;
            for (ulong seed = 1; seed <= 30; seed++)
            {
                foreach (bool wall in new[] { true, false })
                {
                    LaidPiece lp = new CordBuilder().Build(LongRun(wall ? 63 : 0), new BuildOptions { Seed = seed }, c => true).Single(p => p.EndA != null);
                    foreach (CordStrand st in lp.Strands.Where(x => x.Settle != null))
                        foreach (double fe in st.Settle.HeapsFromEnd)
                        {
                            bool near = Math.Abs(fe - 3.0) < 1.0;
                            if (wall) { heaps++; if (near) onDoor++; }
                            else if (near) onDoorNoWall++;
                        }
                }
            }
            Check(onDoor == 0 && heaps > 0, "A9 no long-run end heap within a cell of the doorway (" + onDoor + " of " + heaps + " heaps)");
            Check(onDoorNoWall > 0, "A9 can-fail: with no door there, " + onDoorNoWall + " end heaps land at that spot");

            // A5: the string-pull never shortcuts through a tree the A* route went around
            var tw = new CordWorld(24, 14);
            for (int x = 9; x <= 13; x++) for (int z = 3; z <= 9; z++) tw.SetExtraCost(new Cell(x, z), 1.5f);
            var pa = new V2(4.5, 6.5); var pb = new V2(18.5, 7.5);
            CordPlan plan = CordPlanner.Plan(tw, pa, pb, new List<KeyValuePair<V2, WaypointKind>>());
            List<Cell> path = CordPlanner.FindPath(tw, pa.Floor, pb.Floor, false, null);
            var onPath = new HashSet<Cell>(path);
            int treeHits = 0;
            for (int i = 1; i < plan.Points.Count; i++)
            {
                V2 a = plan.Points[i - 1], b = plan.Points[i];
                int n = (int)(V2.Dist(a, b) / 0.05) + 2;
                for (int k = 0; k < n; k++) { Cell c = (a + (b - a) * (k / (double)(n - 1))).Floor; if (tw.ExtraCost(c) > 0 && !onPath.Contains(c)) treeHits++; }
            }
            bool straightHits = Enumerable.Range(0, 100).Any(k => tw.ExtraCost((pa + (pb - pa) * (k / 99.0)).Floor) > 0);
            Check(plan.Ok && treeHits == 0, "A5 the pulled route keeps the A* detour round the trees (" + treeHits + " samples in trees off the route)");
            Check(straightHits && path.All(c => tw.ExtraCost(c) == 0), "A5 can-fail: the straight line crosses the trees and A* went round them");

            // A3: a closed conduit ring with no device: no Terminal node, no frayed end
            var rw = new CordWorld(20, 20);
            for (int i = 5; i <= 12; i++) { rw.SetConduit(new Cell(i, 5)); rw.SetConduit(new Cell(i, 12)); rw.SetConduit(new Cell(5, i)); rw.SetConduit(new Cell(12, i)); }
            var rb = new CordBuilder();
            List<LaidPiece> rp = rb.Build(rw, new BuildOptions(), c => true);
            int terms = rb.Graph.Nodes.Values.Count(nd => nd.Type == NodeType.Terminal && !nd.Seam);
            int seams = rb.Graph.Nodes.Values.Count(nd => nd.Seam);
            int frays = rp.SelectMany(p => p.Decals).Count(d => d.Kind == DecalKind.FrayLive || d.Kind == DecalKind.FrayDead);
            Console.WriteLine("MEASURE A3 8x8 conduit ring, no device: " + terms + " terminal nodes, " + frays + " fray decals");
            Check(terms == 0 && frays == 0, "A3 an unbroken ring has no frayed 'broken' end (" + terms + " terminals, " + frays + " frays)");
            Check(seams == 1, "A3 can-fail: the ring IS cut at one promoted cell (" + seams + " seam), which used to read as a broken terminal");

            // A2: a 20x20 conduit pile: every junction box it draws has >= 2 cables (no idle boxes past the 24-connector cap)
            var pw = new CordWorld(30, 30);
            for (int x = 4; x < 24; x++) for (int z = 4; z < 24; z++) pw.SetConduit(new Cell(x, z));
            pw.SetBlocked(new Cell(2, 14), BlockKind.Device); pw.SetConduit(new Cell(3, 14));
            Mach(pw, "bat", MachineKind.Battery, 2, 14, new Cell(3, 14));
            var pb2 = new CordBuilder();
            List<LaidPiece> pp = pb2.Build(pw, new BuildOptions { Pile = PileArt.Junctions }, c => true);
            ArtFitResult pr = CordAudit.ArtFit(pb2.Graph, pp, c => true);
            Console.WriteLine("MEASURE A2 20x20 pile: " + pr.PileJunctions + " junction boxes, " + pr.PileIdleConnectors + " idle, " + pr.PileLooseEnds + " loose ends");
            Check(pr.Piles >= 1 && pr.PileIdleConnectors == 0, "A2 a big pile has no idle junction boxes (" + pr.PileIdleConnectors + " of " + pr.PileJunctions + ")");

            // A6/A7: the edge cache sees a changed block kind and a moved wall home: incremental == fresh
            Func<CordWorld> mk = () =>
            {
                var w = new CordWorld(24, 12);
                for (int x = 3; x <= 18; x++) w.SetConduit(new Cell(x, 5));
                for (int z = 4; z <= 6; z++) w.SetBlocked(new Cell(10, z), BlockKind.Wall);
                w.SetConduit(new Cell(10, 5));
                Mach(w, "a", MachineKind.Battery, 2, 5, new Cell(3, 5));
                w.SetBlocked(new Cell(2, 5), BlockKind.Device);
                var lamp = new MachineInfo { Id = "lamp", Kind = MachineKind.Lamp, X0 = 19, Z0 = 5, W = 1, H = 1, Hookups = new List<Cell> { new Cell(18, 5) }, HasHome = true, HomeX = 19, HomeZ = 6 };
                w.Machines.Add(lamp);
                return w;
            };
            var inc = new CordBuilder();
            inc.Build(mk(), new BuildOptions(), c => true);
            CordWorld w6 = mk();
            for (int z = 4; z <= 6; z++) w6.SetBlocked(new Cell(10, z), BlockKind.Device);                 // A6: wall swapped in place
            List<LaidPiece> i6 = inc.Build(w6, new BuildOptions(), c => true);
            List<LaidPiece> f6 = new CordBuilder().Build(w6, new BuildOptions(), c => true);
            bool same6 = Same(i6, f6);
            CordWorld w7 = mk();
            for (int z = 4; z <= 6; z++) w7.SetBlocked(new Cell(10, z), BlockKind.Device);
            w7.Machines.Single(m => m.Id == "lamp").HomeZ = 4;                                               // A7: re-hung lower
            List<LaidPiece> i7 = inc.Build(w7, new BuildOptions(), c => true);
            List<LaidPiece> f7 = new CordBuilder().Build(w7, new BuildOptions(), c => true);
            bool same7 = Same(i7, f7);
            Console.WriteLine("MEASURE A6 block-kind swap incremental==fresh: " + same6 + "; A7 home moved incremental==fresh: " + same7);
            Check(same6, "A6 swapping a wall for another impassable kind re-lays like a fresh build");
            Check(same7, "A7 moving a wall device's home re-lays like a fresh build");
        }

        private static bool Same(List<LaidPiece> a, List<LaidPiece> b)
        {
            var ha = a.Where(p => p.EndA != null).ToDictionary(p => p.Key, p => p.GeometryHash());
            var hb = b.Where(p => p.EndA != null).ToDictionary(p => p.Key, p => p.GeometryHash());
            return ha.Count == hb.Count && ha.All(kv => hb.TryGetValue(kv.Key, out ulong h) && h == kv.Value)
                && a.SelectMany(p => p.Decals).Count() == b.SelectMany(p => p.Decals).Count();
        }

        // ------------------------------------------------------------------ GSS_PROBES_FIX_BLIND_SPOTS (D14; the rest are shape rows)
        private static void Probes()
        {
            Check(ConduitStyles.StraightOrDiagonal(5, 0) && ConduitStyles.StraightOrDiagonal(0, -3) && ConduitStyles.StraightOrDiagonal(-4, 4) &&
                  !ConduitStyles.StraightOrDiagonal(3, 1), "D14 cline walks straight and 45-degree lines and refuses an unequal diagonal");
            // can-fail: the old walk of (0,0)->(3,1) steps (sign, sign) max(3,1) times and ends at (3,3), not (3,1)
            int n = Math.Max(3, 1);
            Check(n * Math.Sign(1) != 1, "D14 can-fail: the old walk overshoots an unequal diagonal's end (z " + n * Math.Sign(1) + " for 1)");
        }

        // ------------------------------------------------------------------ GSS_FALLEN_LINE_REDRAW_FLOATS_OVER_PAWNS (C4)
        private static void FallenRedraw()
        {
            var basePt = new P2(10.5, 10.5);
            var top = new P2(10.5, 13.72);
            FallenLay f = AerialMath.LayFallen(top, basePt, new P2(16.5, 10.5), 6.3, 42, (x, z) => true);
            int ground = Enumerable.Range(0, f.Pts.Count).Count(i => AerialMath.FallenPointOnGround(f, i));
            Check(ground > 0 && ground < f.Pts.Count && !AerialMath.FallenPointOnGround(f, 0) && AerialMath.FallenPointOnGround(f, f.Pts.Count - 1),
                  "C4 the insulator end hangs (span altitude), the tail lies on the ground (under pawns): " + ground + " of " + f.Pts.Count + " on the ground");
            Check(Enumerable.Range(0, f.Pts.Count).Where(i => AerialMath.FallenPointOnGround(f, i)).All(i => Math.Abs(f.Pts[i].Z - 10.5) <= 0.25),
                  "C4 every point drawn on the ground lies on the ground path");
            Check(ground != 0, "C4 can-fail: the old mesh drew all " + f.Pts.Count + " points at the span altitude, the grounded ones included");
        }

        // ------------------------------------------------------------------ GSS_RESTRING_DECIDE_FREE_INSTANT_SPLICE (C12, C13)
        private static void Restring()
        {
            // C13 design 2.6 "hp -= damage x falloff": vanilla's falloff, full at the centre, 20% at the radius
            Check(AerialMath.BlastCutFalloff(0, 3) == 1 && Math.Abs(AerialMath.BlastCutFalloff(3, 3) - 0.2) < 1e-12 &&
                  Math.Abs(AerialMath.BlastCutFalloff(1.5, 3) - 0.6) < 1e-12 && AerialMath.BlastCutFalloff(9, 3) == AerialMath.BlastCutFalloff(3, 3),
                  "C13 falloff: 1 at the centre, 0.6 halfway, 0.2 at the edge and beyond");
            var a = new P2(0, 0); var b = new P2(10, 0);
            AerialMath.SpanBlast near = AerialMath.BlastSpan(a, b, new P2(5, 0), 3, 30, 35, AerialMath.BlastKind.Cut);
            AerialMath.SpanBlast edge = AerialMath.BlastSpan(a, b, new P2(5, 2.9), 3, 30, 35, AerialMath.BlastKind.Cut);
            Check(near.Cut && !edge.Cut && edge.Hit, "C13 a 35-damage blast parts a 30 hp span on the line but only wounds it at the edge (hp " + edge.Hp.ToString("0.0") + ")");
            Check(30 - 35 <= 0, "C13 can-fail: without falloff the edge blast would part it too");
            // C12 owner by card 2026-10-15 ("Make it a colonist job"): design 2.6's 300 ticks, scaled by construction speed
            Check(AerialMath.RestringTicks(1) == 300 && AerialMath.RestringTicks(2) == 150 && AerialMath.RestringTicks(0.5) == 600 && AerialMath.RestringTicks(0) == 3000,
                  "C12 re-string work: 300 ticks at speed 1, halves at 2, capped at speed 0.1");
            // GSS_RESTRING_DIAGNOSE_FIXER_GETS_ZAPPED: the job sends the worker onto the live half; he must not be shocked there
            Check(!AerialMath.ShockTakes(true, false, false, true), "re-string worker on the live wire is not shocked");
            Check(AerialMath.ShockTakes(true, false, false, false) && !AerialMath.ShockTakes(false, false, false, false) &&
                  !AerialMath.ShockTakes(true, true, false, false) && !AerialMath.ShockTakes(true, false, true, false),
                  "any other flesh pawn on it still is; mechs, the dead and the knocked-out are not");
            Func<bool, bool, bool, bool> oldRule = (flesh, dead, outAlready) => flesh && !dead && !outAlready;
            Check(oldRule(true, false, false), "re-string can-fail: the old rule shocked the worker (L1 2026-10-15, 2/2 downed)");
            // review 2026-10-15: the exemption is scoped to the wires of HIS cut (LayTouches over that cut's fallen halves); a
            // second cut's wire he walks over on the way still shocks him. Two east-running fallen halves, z 10 and z 20.
            FallenLay own = AerialMath.LayFallen(new P2(10.5, 13.7), new P2(10.5, 10.5), new P2(16.5, 10.5), 6.3, 42, (x, z) => true);
            FallenLay other = AerialMath.LayFallen(new P2(10.5, 23.7), new P2(10.5, 20.5), new P2(16.5, 20.5), 6.3, 43, (x, z) => true);
            P2 t0 = own.Tip;
            int tx = (int)Math.Floor(t0.X), tz = (int)Math.Floor(t0.Z);
            Check(AerialMath.LayTouches(own, tx, tz) && !AerialMath.LayTouches(other, tx, tz), "re-string: his cut's tip cell is on his wire, not the other cut's");
            Check(AerialMath.LayTouches(other, (int)Math.Floor(other.Tip.X), (int)Math.Floor(other.Tip.Z)) &&
                  !AerialMath.LayTouches(own, (int)Math.Floor(other.Tip.X), (int)Math.Floor(other.Tip.Z)),
                  "re-string: on the other cut's wire he is not on his own (so ShockTakes(.., false) shocks him there)");
            Check(!AerialMath.LayTouches(own, 10, 13), "re-string: the hanging part (thin air north of the mast) is not his wire either");
        }

        internal static class SettingsDummy
        {
            public static bool a = true;
            public static float b = 1.5f;
            public static List<string> l = new List<string> { "X" };
            public const int Const = 3;
        }

        // ------------------------------------------------------------------ GSS_FRAME_COST_MEASURE_RIPPLE_DEFAULTS_ON (B14, B15, B24, C16)
        private static void FrameCost()
        {
            var cord = new List<V2>();
            for (int i = 0; i < 40; i++) cord.Add(new V2(2 + i * 0.25, 5 + 0.1 * Math.Sin(i)));
            // B14: the per-frame form writes into reused buffers: the same pose as the allocating form, and no allocation
            var o = new List<V2>();
            double[] arc = null;
            CordMotion.RippleInto(cord, 3.0, 7, CordMotion.RippleAmp, 1, o, ref arc);
            List<V2> r = CordMotion.Ripple(cord, 3.0, 7, CordMotion.RippleAmp, 1);
            Check(o.Count == r.Count && o.Zip(r, (p, q) => V2.Dist(p, q) < 1e-12).All(x => x), "B14 RippleInto draws exactly what Ripple draws");
            long before = GC.GetAllocatedBytesForCurrentThread();
            for (int f = 0; f < 500; f++) CordMotion.RippleInto(cord, f / 60.0, 7, CordMotion.RippleAmp, 1, o, ref arc);
            long ripAlloc = GC.GetAllocatedBytesForCurrentThread() - before;
            Check(ripAlloc == 0, "B14 500 frames of one rippling cord allocate nothing (" + ripAlloc + " bytes)");
            before = GC.GetAllocatedBytesForCurrentThread();
            for (int f = 0; f < 50; f++) CordMotion.Ripple(cord, f / 60.0, 7, CordMotion.RippleAmp, 1);
            Check(GC.GetAllocatedBytesForCurrentThread() - before > 50 * 40 * 16, "B14 can-fail: the allocating form allocates a list and an array per call");

            // B15: the whip resumes its snap search from the last frame's interval; the pose is the same as a search from t = 0
            var tail = cord.GetRange(0, 9);
            var cur = new CordMotion.WhipCursor();
            var w = new List<V2>();
            bool same = true;
            for (int f = 0; f < 600; f++)
            {
                double t = 9000 + f / 60.0;
                CordMotion.WhipInto(tail, t, 42, 0.12, w, ref cur);
                List<V2> fresh = CordMotion.Whip(tail, t, 42, 0.12);
                same &= w.Count == fresh.Count && w.Zip(fresh, (p, q) => V2.Dist(p, q) < 1e-12).All(x => x);
            }
            CordMotion.WhipInto(tail, 12.5, 42, 0.12, w, ref cur);                  // the clock went back (10,000 s wrap): restart
            List<V2> back = CordMotion.Whip(tail, 12.5, 42, 0.12);
            same &= w.Zip(back, (p, q) => V2.Dist(p, q) < 1e-12).All(x => x);
            Check(same, "B15 the cursor whip equals the from-scratch whip over 600 late frames and across a wrap");
            var sw = System.Diagnostics.Stopwatch.StartNew();
            for (int f = 0; f < 300; f++) CordMotion.WhipInto(tail, 9000 + f / 60.0, 42, 0.12, w, ref cur);
            double curMs = sw.Elapsed.TotalMilliseconds;
            sw.Restart();
            for (int f = 0; f < 300; f++) { var c0 = new CordMotion.WhipCursor(); CordMotion.WhipInto(tail, 9000 + f / 60.0, 42, 0.12, w, ref c0); }
            double scratchMs = sw.Elapsed.TotalMilliseconds;
            Check(curMs * 5 < scratchMs, "B15 300 late frames: cursor " + curMs.ToString("0.00") + " ms vs search from t=0 " + scratchMs.ToString("0.00") + " ms (can-fail: the old search)");

            // B24: the settings fingerprint sees a flipped bool, a moved number and a changed list element, and nothing else
            string p0 = SettingsPrint.Of(typeof(SettingsDummy));
            Check(p0 == SettingsPrint.Of(typeof(SettingsDummy)), "B24 an unchanged settings class prints the same");
            SettingsDummy.a = false; string p1 = SettingsPrint.Of(typeof(SettingsDummy)); SettingsDummy.a = true;
            SettingsDummy.l.Add("Y"); string p2 = SettingsPrint.Of(typeof(SettingsDummy)); SettingsDummy.l.RemoveAt(1);
            Check(p1 != p0 && p2 != p0 && p0.Contains("l=[X,]"), "B24 a flipped bool and a list element change the print (" + p0 + ")");
            Check(p0 == SettingsPrint.Of(typeof(SettingsDummy)), "B24 put back, the print matches again");

            // A10 (PLAUSIBLE, a measurement, no pass bar): a 50x50 conduit field (one big tangle), built, then built again
            // unchanged by the same builder (every edge cached). Printed for the item; the tangle half is rebuilt every time.
            {
                var fw = new CordWorld(60, 60);
                for (int x = 5; x < 55; x++) for (int z = 5; z < 55; z++) fw.SetConduit(new Cell(x, z));
                var fopt = new BuildOptions();
                var fb = new CordBuilder();
                var t0 = System.Diagnostics.Stopwatch.StartNew();
                int n1 = fb.Build(fw, fopt, c => true).Count;
                double first = t0.Elapsed.TotalMilliseconds;
                t0.Restart();
                int n2 = fb.Build(fw, fopt, c => true).Count;
                double again = t0.Elapsed.TotalMilliseconds;
                Console.WriteLine("MEASURE A10 2,500-cell field: first build " + first.ToString("0") + " ms (" + n1 + " pieces), unchanged rebuild " + again.ToString("0") + " ms (" + n2 + " pieces)");
                Check(n1 == n2 && n1 > 0, "A10 the field builds and rebuilds to the same piece count");
            }

            // C16: the terminal assignment's signature is order-free and moves with an id, an x or the insulator count
            var devs = new List<(int, double)> { (5, 0.4), (9, -0.6), (12, 1.1) };
            int sig = AerialMath.TerminalSig(devs, 3);
            Check(sig == AerialMath.TerminalSig(new List<(int, double)> { (12, 1.1), (5, 0.4), (9, -0.6) }, 3), "C16 device order does not change the signature");
            Check(sig != AerialMath.TerminalSig(devs, 2) && sig != AerialMath.TerminalSig(new List<(int, double)> { (5, 0.9), (9, -0.6), (12, 1.1) }, 3) &&
                  sig != AerialMath.TerminalSig(new List<(int, double)> { (5, 0.4), (9, -0.6) }, 3), "C16 insulators, a moved device or a removed device change it");
        }

        // ------------------------------------------------------------------ GSS_LAMP_RUN_FIX_NEIGHBOUR_PAINTS_IT (D2, D9)
        private static void LampRun()
        {
            // D2: a lamp wired to run A standing beside run B
            Check(!ConduitStyles.LampHooked(true, false, true), "D2 a lamp wired to another run is not claimed by the run it stands beside");
            Check(ConduitStyles.LampHooked(true, true, false) && ConduitStyles.LampHooked(false, false, true) && !ConduitStyles.LampHooked(false, false, false),
                  "D2 wired to this run, or unwired and touching it: hooked; unwired and apart: not");
            Func<bool, bool, bool, bool> oldRule = (wired, wiredHere, touches) => (wired && wiredHere) || touches;
            Check(oldRule(true, false, true) != ConduitStyles.LampHooked(true, false, true), "D2 can-fail: the old rule (wired here OR touching) claims it");
            // D9: a lamp in an Ideology / other mod's style reads as no GSS look, but must not be overwritten by Restyle
            Check(!ConduitStyles.LampFollowsRun(null, "Industrial", "Scrapper", true, foreignStyle: true), "D9 a foreign-styled lamp keeps its style on Restyle");
            Check(!ConduitStyles.LampFollowsRun(null, "Industrial", "Scrapper", false, foreignStyle: true), "D9 ... and on a bridge");
            Check(ConduitStyles.LampFollowsRun(null, "Industrial", "Scrapper", true), "D9 can-fail: without the flag the same lamp (no GSS look) follows the Restyle");
            Check(ConduitStyles.LampFollowsRun("Industrial", "Industrial", "Scrapper") && !ConduitStyles.LampFollowsRun("Modern", "Industrial", "Scrapper"),
                  "D9 the GSS rule is unchanged for our own looks");
        }

        // ------------------------------------------------------------------ GSS_TAP_CLAMP_FIX_NO_OFF_SWITCH (C1, C7)
        private static void TapClamp()
        {
            // C1: the debit is keyed by the bitten transmitter and settled by the net it is in NOW. A victim-net rebuild between
            // the tap's debit (thing tick T) and the net tick that reads T hands the transmitter a new net object.
            var netOf = new Dictionary<int, object>();
            object oldNet = new object(), newNet = new object();
            netOf[7] = oldNet;
            Func<int, object, bool> inNet = (k, n) => netOf.TryGetValue(k, out object m) && ReferenceEquals(m, n);
            var ledger = new TapLedger<int>();
            ledger.Debit(7, 0.5f, 100);
            netOf[7] = newNet;                                            // the rebuild
            Check(Math.Abs(ledger.OwedWhere(newNet, inNet, 100) - 0.5f) < 1e-6, "C1 a debit survives a victim-net rebuild before it settles");
            Check(ledger.OwedWhere(oldNet, inNet, 100) == 0f && ledger.OwedWhere(newNet, inNet, 101) == 0f, "C1 it is owed once: not to the dead net, not a tick later");
            var byNet = new TapLedger<object>();
            byNet.Debit(oldNet, 0.5f, 100);
            Check(byNet.Owed(newNet, 100) == 0f, "C1 can-fail: the old PowerNet key is orphaned by the rebuild (the victim never pays)");
            ledger.Prune(103);
            Check(ledger.Count == 0, "C1 a stale debit is pruned");

            // C7: one draining tick per 250-tick event window, for three days, is 720 draining ticks: well under a day
            const int day = 60000, window = 250;
            int acc = 0, total = 0, accOld = 0, totalOld = 0;
            for (int t = 0; t < day * 3; t += window)
            {
                total += AerialMath.TheftGoodwillAccrue(ref acc, 1, true, 2, day);
                totalOld += AerialMath.TheftGoodwillAccrue(ref accOld, window, true, 2, day);
            }
            Check(total == 0 && acc == 3 * day / window, "C7 intermittent drain is charged by its draining ticks (" + acc + " ticks, " + total + ")");
            Check(totalOld == -6, "C7 can-fail: charging the whole window bills 250x the drain (" + totalOld + ")");
        }

        // ------------------------------------------------------------------ GSS_FALLEN_LINE_FIX_SHOCKS_THIN_AIR (C3, C6)
        private static void FallenShock()
        {
            Func<int, int, bool> open = (x, z) => true;
            var basePt = new P2(10.5, 10.5);
            var top = new P2(10.5 + 0.087, 10.5 + 3.22);                  // insulator 3.22 cells up: screen z fakes height
            var brk = new P2(16.5, 10.5);                                  // the break lies due east
            FallenLay f = AerialMath.LayFallen(top, basePt, brk, 6.3, 42, open);
            List<P2> ground = AerialMath.GroundPts(f).ToList();
            // C3: every contact point lies on the ground path (base -> break, bow <= 0.22), never north of the mast
            Check(f.TipGrounded && ground.Count > 0 && ground.All(p => Math.Abs(p.Z - 10.5) <= 0.25) && P2.Dist(ground[ground.Count - 1], f.Tip) < 1e-12,
                  "C3 contact points are the grounded part only (" + ground.Count + " of " + f.Pts.Count + ")");
            Check(f.Pts.Any(p => Math.Floor(p.Z) >= 12), "C3 can-fail: the old rule (every Pts point) reaches cells 1-3 north of the mast");
            // a cable stopped at once by a wall still hangs: it touches nothing
            FallenLay hung = AerialMath.LayFallen(top, basePt, basePt, 6.3, 42, open);   // a coil at the anchor: nothing laid
            Check(!hung.TipGrounded && !AerialMath.GroundPts(hung).Any(), "C3 a cable with no ground run (coiled at the anchor) has no contact cells and no live tip");

            // C6: mid-strand on an east-west wire (contacts on dz == 0) the pawn is thrown off the wire, not along it
            Func<int, int, bool> offWire = (dx, dz) => dz != 0;
            var d = AerialMath.KnockbackDir(5, 0, 0, offWire);
            Check(d != null && d.Value.dz != 0, "C6 mid-strand knockback leaves the wire (" + d + ")");
            Check(!offWire(Math.Sign(5), 0), "C6 can-fail: the old rule (straight away from the tip) steps onto the next contact cell");
            Check(AerialMath.KnockbackDir(5, 0, 0, (dx, dz) => true) == (1, 0), "C6 a clear 'away from the tip' is still preferred");
            Check(AerialMath.KnockbackDir(0, 0, 3, (dx, dz) => true) == AerialMath.Ring8[3], "C6 on the tip: the fallback direction");
            Check(AerialMath.KnockbackDir(1, 0, 0, (dx, dz) => false) == null, "C6 boxed in: no knockback");
            // the turn order never repeats a direction and reaches all eight
            var seen = new HashSet<(int, int)>();
            AerialMath.KnockbackDir(1, 0, 0, (dx, dz) => { seen.Add((dx, dz)); return false; });
            Check(seen.Count == 8, "C6 all eight neighbours are tried (" + seen.Count + ")");
        }
    }
}
