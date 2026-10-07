// MESSYCONDUIT_CABLE_PILE_LOOK_1 (owner 2026-10-04): the three pile/hose look rules as offline bars, each with a planted
// fault that must turn it red.
//   rule 1  "There shouldn't be any unused power strips lying in a pile of cables": every strip in a pile has cables
//           plugged in (also ReviewRound1Checks B13, here over seeds and both pile arts)
//   rule 2  "the cables don't look like separate cable lengths laying on each other, but one big flowing cable except
//           where they go into nodes or power strips/joiners": no strand end lies on a strand body without a connector
//           (CordAudit.EndsOnBodies), over every oracle scene and the pile world, both pile arts
//   rule 3  "the brass fixtures at the ends don't just lay on top of other hose lenghts ... They CAN look like sealed
//           joiners": no fitting of a hose draws over another hose's body (HoseMath.FittingsOnTop) once the layering
//           (HoseMath.Layering) has ranked a hose whose end rests on another beneath it and dropped joiners that would
//           sit on a hose below
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.GimmeSomeSlack.Hose;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class PileLookChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "pilelook: " + msg);

        public static void Run(List<JsonElement> scenes)
        {
            // ---- rule 1: no orphan strip, several seeds
            int strips = 0, idle = 0;
            for (ulong seed = 1; seed <= 6; seed++)
            {
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(ReviewRound1Checks.PileWorld(), new BuildOptions { Pile = PileArt.Strips, Seed = seed }, c => true);
                ArtFitResult r = CordAudit.ArtFit(b.Graph, ps, c => true);
                strips += r.Strips; idle += r.PileIdleConnectors;
            }
            Check(strips >= 6 && idle == 0, $"rule 1: {strips} pile strips over 6 seeds, {idle} with < 2 cables plugged in (want 0)");

            // ---- rule 2: ends never lie on a body without a connector
            int scenesRun = 0, ends = 0;
            var faults = new List<string>();
            foreach (JsonElement s in scenes)
            {
                JsonElement sc = s.GetProperty("scene");
                string name = sc.GetProperty("name").GetString();
                foreach (PileArt art in new[] { PileArt.Junctions, PileArt.Strips })
                {
                    CordWorld w = Program.World(sc);
                    HashSet<Cell> live = Program.Live(w, sc);
                    List<LaidPiece> ps = new CordBuilder().Build(w, new BuildOptions { Pile = art }, live.Contains);
                    ends += 2 * ps.Sum(p => p.Strands.Count);
                    faults.AddRange(CordAudit.EndsOnBodies(ps).Select(f => name + "/" + art + ": " + f));
                    scenesRun++;
                }
            }
            for (ulong seed = 1; seed <= 6; seed++)
                foreach (PileArt art in new[] { PileArt.Junctions, PileArt.Strips })
                {
                    List<LaidPiece> ps = new CordBuilder().Build(ReviewRound1Checks.PileWorld(), new BuildOptions { Pile = art, Seed = seed }, c => true);
                    ends += 2 * ps.Sum(p => p.Strands.Count);
                    faults.AddRange(CordAudit.EndsOnBodies(ps).Select(f => "pile" + seed + "/" + art + ": " + f));
                    scenesRun++;
                }
            foreach (string f in faults.Take(8)) Console.WriteLine("    " + f);
            Check(ends > 100 && faults.Count == 0, $"rule 2: {faults.Count} strand ends lie on a cable body with no connector ({ends} ends, {scenesRun} builds; want 0)");
            {
                // planted: a loose length dropped across the middle of a run
                List<LaidPiece> ps = new CordBuilder().Build(ReviewRound1Checks.PileWorld(), new BuildOptions(), c => true);
                CordStrand host = ps.SelectMany(p => p.Strands).Where(x => !x.OverFace).OrderByDescending(x => Geo.Length(x.Pts)).First();
                V2 mid = host.Pts[host.Pts.Count / 2];
                var drop = new LaidPiece { Key = "planted" };
                drop.Strands.Add(new CordStrand { Pts = new List<V2> { mid, mid + new V2(0.4, 0.7), mid + new V2(0.9, 1.1) } });
                int n = CordAudit.EndsOnBodies(ps.Concat(new[] { drop }).ToList()).Count;
                Check(n >= 1, $"rule 2 can fail: a planted length dropped on a run -> {n} faults");
                // and a connector at that end clears it
                drop.Decals.Add(new CordDecal(DecalKind.JunctionTin, mid, 0, 0.6));
                int m = CordAudit.EndsOnBodies(ps.Concat(new[] { drop }).ToList()).Count;
                Check(m == n - 1, $"rule 2: a junction box at the planted end clears it ({n} -> {m})");
            }

            // ---- rule 3: hoses
            HoseRule3();
        }

        private static List<V2> Line(V2 a, V2 b, double step = 0.1)
        {
            int n = Math.Max(2, (int)Math.Ceiling(V2.Dist(a, b) / step) + 1);
            var o = new List<V2>(n);
            for (int i = 0; i < n; i++) o.Add(a + (b - a) * (i / (double)(n - 1)));
            return o;
        }

        private static HoseLay Straight(V2 a, V2 b, params int[] joints)
        {
            List<V2> p = Line(a, b);
            var lay = new HoseLay { Ok = true, Flat = p, Plump = new List<V2>(p), Centre = new List<V2>(p) };
            lay.Joints = joints.ToList();
            lay.Couplings = new List<V2> { p[0] };
            foreach (int j in joints) lay.Couplings.Add(p[j]);
            lay.Couplings.Add(p[p.Count - 1]);
            return lay;
        }

        private static void HoseRule3()
        {
            const double vis = 0.3;
            // A (older, id 1) runs west-east along z=5; B (newer, id 2) runs north-south and ENDS on A's body at (5,5).
            // Thing-id order puts B over A, so B's end coupling would lie on top of A: the layering must put B beneath.
            HoseLay A = Straight(new V2(0, 5), new V2(10, 5));
            HoseLay B = Straight(new V2(5, 12), new V2(5, 5.02));
            var raw = new List<HoseMath.LayeredHose> { new HoseMath.LayeredHose { Id = 1, Lay = A }, new HoseMath.LayeredHose { Id = 2, Lay = B } };
            var naive = new Dictionary<int, int> { { 1, 0 }, { 2, 1 } };
            int before = HoseMath.FittingsOnTop(raw, naive, null, vis).Count;
            Check(before >= 1, $"rule 3 can fail: thing-id order alone leaves {before} fitting(s) on top of a hose (want >= 1)");
            HoseMath.Layering L = HoseMath.Layer(raw, vis);
            List<string> after = HoseMath.FittingsOnTop(raw, L.Rank, L.Joints, vis);
            foreach (string f in after.Take(4)) Console.WriteLine("    " + f);
            Check(after.Count == 0 && L.Rank[2] < L.Rank[1], $"rule 3 (end): B's end on A's body -> B ranked {L.Rank[2]} under A {L.Rank[1]}, {after.Count} fittings on top (want 0)");

            // joiner: C (older) runs north-south through x=5; D (newer) crosses it with a joiner right on the crossing.
            HoseLay C = Straight(new V2(5, 0), new V2(5, 10));
            HoseLay D = Straight(new V2(0, 4), new V2(10, 4), 50);   // sample 50 of 101 = (5,4): on C
            var jr = new List<HoseMath.LayeredHose> { new HoseMath.LayeredHose { Id = 1, Lay = C }, new HoseMath.LayeredHose { Id = 2, Lay = D } };
            int jb = HoseMath.FittingsOnTop(jr, new Dictionary<int, int> { { 1, 0 }, { 2, 1 } }, null, vis).Count;
            Check(jb >= 1, $"rule 3 can fail: a joiner on a crossing reads on top ({jb} fittings)");
            HoseMath.Layering JL = HoseMath.Layer(jr, vis);
            List<string> ja = HoseMath.FittingsOnTop(jr, JL.Rank, JL.Joints, vis);
            Check(ja.Count == 0 && JL.Joints[2].Count == 0, $"rule 3 (joiner): the crossing joiner is dropped ({JL.Joints[2].Count} kept), {ja.Count} fittings on top (want 0)");
            // a joiner clear of every other hose is kept
            HoseLay E = Straight(new V2(0, 8), new V2(10, 8), 20);
            var kr = new List<HoseMath.LayeredHose> { new HoseMath.LayeredHose { Id = 1, Lay = C }, new HoseMath.LayeredHose { Id = 2, Lay = E } };
            HoseMath.Layering KL = HoseMath.Layer(kr, vis);
            Check(KL.Joints[2].Count == 1 && KL.Rank[2] > KL.Rank[1], $"rule 3: a joiner clear of other hoses is kept ({KL.Joints[2].Count}) and thing-id order stands");

            // a cycle (each hose's end on the other) cannot be satisfied by order: it must still return a total order
            HoseLay F = Straight(new V2(0, 0), new V2(6, 0));
            HoseLay G = Straight(new V2(3, -3), new V2(3, 0.02));
            HoseLay F2 = Straight(new V2(3, 0.02), new V2(3, 3));   // G ends and F2 starts on F's body, and on each other's end
            var cy = new List<HoseMath.LayeredHose> { new HoseMath.LayeredHose { Id = 1, Lay = F }, new HoseMath.LayeredHose { Id = 2, Lay = G }, new HoseMath.LayeredHose { Id = 3, Lay = F2 } };
            HoseMath.Layering CL = HoseMath.Layer(cy, vis);
            Check(CL.Rank.Values.Distinct().Count() == 3 && CL.Rank.Values.Min() == 0 && CL.Rank.Values.Max() == 2,
                  $"rule 3: layering is a total order 0..n-1 ({string.Join(",", CL.Rank.Select(kv => kv.Key + ":" + kv.Value))})");
            Console.WriteLine($"  pilelook hoses: end case rank B {L.Rank[2]} / A {L.Rank[1]}; joiner case kept {JL.Joints[2].Count}; before {before}+{jb} on top, after {after.Count}+{ja.Count}");
        }
    }
}
