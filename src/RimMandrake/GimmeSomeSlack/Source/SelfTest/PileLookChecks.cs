// MESSYCONDUIT_CABLE_PILE_LOOK_1 (owner 2026-10-04): the three pile/hose look rules as offline bars, each with a planted
// fault that must turn it red.
//   rule 1  "There shouldn't be any unused power strips lying in a pile of cables": every strip in a pile has cables
//           plugged in (also ReviewRound1Checks B13, here over seeds and both pile arts)
//   rule 2  "the cables don't look like separate cable lengths laying on each other, but one big flowing cable except
//           where they go into nodes or power strips/joiners": no strand end lies on a strand body without a connector
//           (CordAudit.EndsOnBodies), over every oracle scene and the pile world, both pile arts
//   rule 3  (hoses) moved with the hose to FlowWorks/Source/SelfTest/HoseReviewChecks.cs (HosePileLook) at the hose port
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

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

        }

    }
}
