// Power-tap clamp v3 pose (owner 2026-10-11: "it needs to look like it's clamped vertically DOWN onto the wire itself").
// Lays the REAL cord graph around a tap (CordBuilder, as CordWorldAdapter.AddTapNodes hooks it: our conduit + the bitten one)
// for every bitten-cord direction x every side our cord can come from x 4 seeds, then asks the production pose
// (../Aerial/AerialMath.TapClampPose, which RM_MapComponent_Aerial.TapBite draws with) three things:
//   on-wire   the bite lies on THEIR laid strand (<= 0.02 cell) and off the node where our cord meets it (>= 0.08 cell)
//   along     the art's jaw axis lies along their strand at the bite (<= 10 degrees)
//   handles   upright (up-screen) on an east-west cord; on a north-south cord, turned away from the side our cord is on
//             (east when ours comes straight through)
// Planted faults: the round-3 pose (jaws on the node, art +x turned toward our connector) must fail, and one mutant per
// predicate (bite 0.3 cell off the wire, jaws turned a quarter, handles flipped) must trip exactly that predicate.
// --dump <dir> also writes tapclamp_poses.json (seed 1: every laid strand + the pose) for the offline composite
// src/RimMandrake/GimmeSomeSlack/art_source/tapclamp_v3_2026-10-11/render_tapclamp_poses.py.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class TapClampPoseChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "tapclamp: " + msg);

        private static readonly (int X, int Z, string Name)[] Dirs = { (-1, 0, "W"), (1, 0, "E"), (0, -1, "S"), (0, 1, "N") };

        private static void M(CordWorld w, string id, MachineKind k, int x, int z, params Cell[] hooks)
        {
            w.SetBlocked(new Cell(x, z), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = id, Kind = k, X0 = x, Z0 = z, Hookups = hooks.ToList() });
        }

        /// <summary>Distance from p to the polyline, and the unit tangent of the nearest segment.</summary>
        private static double Near(List<V2> pts, P2 p, out P2 tangent)
        {
            double best = double.MaxValue;
            tangent = new P2(1, 0);
            for (int i = 0; i + 1 < pts.Count; i++)
            {
                P2 a = new P2(pts[i].X, pts[i].Z), b = new P2(pts[i + 1].X, pts[i + 1].Z);
                double t = AerialMath.ProjectT(a, b, p), d = P2.Dist(P2.Lerp(a, b, t), p), l = P2.Dist(a, b);
                if (d < best && l > 1e-9) { best = d; tangent = new P2((b.X - a.X) / l, (b.Z - a.Z) / l); }
            }
            return best;
        }

        private struct Verdict { public bool OnWire, OffNode, Along, Handles; public double Dist, Deg; }

        private static Verdict Judge(List<List<V2>> theirs, P2 home, (int X, int Z) d, (int X, int Z) o, P2 bite, P2 jaw, P2 handles)
        {
            var v = new Verdict { Dist = double.MaxValue };
            P2 tan = new P2(1, 0);
            foreach (List<V2> s in theirs)
            {
                double dd = Near(s, bite, out P2 t);
                if (dd < v.Dist) { v.Dist = dd; tan = t; }
            }
            v.OnWire = v.Dist <= 0.02;
            v.OffNode = P2.Dist(bite, home) >= 0.08 && ((bite.X - home.X) * d.X + (bite.Z - home.Z) * d.Z) > 0;
            double cross = Math.Abs(jaw.X * tan.Z - jaw.Z * tan.X);
            v.Deg = Math.Asin(Math.Min(1, cross)) * 180 / Math.PI;
            v.Along = v.Deg <= 10;
            // east-west: upright; north-south: away from our side, east when our cord comes straight through
            v.Handles = d.Z == 0 ? handles.Z > 0.99 : o.X != 0 ? handles.X * o.X < -0.99 : handles.X > 0.99;
            return v;
        }

        public static void Run()
        {
            int scenes = 0, good = 0, oldCaught = 0, offCaught = 0, turnCaught = 0, flipCaught = 0;
            double worst = 0, worstDeg = 0;
            var dump = new List<object>();
            foreach (var d in Dirs)
                foreach (var o in Dirs)
                {
                    if (o.X == d.X && o.Z == d.Z) continue;            // our cord never comes in on the bitten side
                    for (ulong seed = 1; seed <= 4; seed++)
                    {
                        const int tx = 6, tz = 5;
                        var w = new CordWorld(14, 12);
                        Cell v1 = new Cell(tx + d.X, tz + d.Z), v2 = new Cell(tx + 2 * d.X, tz + 2 * d.Z);
                        Cell o1 = new Cell(tx + 2 * o.X, tz + 2 * o.Z), o2 = new Cell(tx + 3 * o.X, tz + 3 * o.Z);
                        foreach (Cell c in new[] { v1, v2, o1, o2 }) w.SetConduit(c);
                        M(w, "theirbat", MachineKind.Battery, tx + 3 * d.X, tz + 3 * d.Z, v2);
                        M(w, "lamp", MachineKind.Consumer, tx + 4 * o.X, tz + 4 * o.Z, o2);
                        M(w, "tap", MachineKind.Consumer, tx, tz, o1, v1);   // CordWorldAdapter.AddTapNodes: ours + bitten
                        // CordWorldAdapter.TapIds: the clamp keeps the straight plug (CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT)
                        List<LaidPiece> laid = new CordBuilder().Build(w, new BuildOptions { Seed = seed, StraightPlugIds = new HashSet<string> { "tap" } }, c => true);
                        // THEIR cord into the tap: every strand that passes through the bitten conduit cell
                        List<List<V2>> theirs = laid.SelectMany(p => p.Strands).Select(s => s.Pts)
                            .Where(pts => pts.Any(q => q.X >= v1.X && q.X <= v1.X + 1 && q.Z >= v1.Z && q.Z <= v1.Z + 1)).ToList();
                        P2 home = new P2(tx + 0.5, tz + 0.5);
                        P2 toV = new P2(d.X, d.Z), toO = new P2(2 * o.X, 2 * o.Z);
                        AerialMath.TapClampPose(home, toV, toO, out P2 bite, out double ang, out P2 jaw, out P2 handles);
                        Verdict v = Judge(theirs, home, (d.X, d.Z), (o.X, o.Z), bite, jaw, handles);
                        scenes++;
                        bool ok = theirs.Count > 0 && v.OnWire && v.OffNode && v.Along && v.Handles;
                        if (ok) good++;
                        else Check(false, $"their cord {d.Name}, ours {o.Name}, seed {seed}: {theirs.Count} strands of theirs, bite {bite} " +
                                          $"{v.Dist:0.000} off their strand (onWire {v.OnWire}, offNode {v.OffNode}), jaws {v.Deg:0.0} deg off it, " +
                                          $"handles {handles} ok {v.Handles} (angle {ang})");
                        worst = Math.Max(worst, v.Dist); worstDeg = Math.Max(worstDeg, v.Deg);
                        if (seed == 1)
                            dump.Add(new
                            {
                                their = d.Name, ours = o.Name, tap = new[] { tx, tz }, angle = ang, bite = new[] { bite.X, bite.Z },
                                conduits = new[] { v1, v2, o1, o2 }.Select(c => new[] { c.X, c.Z }),
                                machines = new[] { new[] { tx + 3 * d.X, tz + 3 * d.Z }, new[] { tx + 4 * o.X, tz + 4 * o.Z } },
                                strands = laid.SelectMany(p => p.Strands).Select(st => new
                                {
                                    theirs = theirs.Contains(st.Pts),
                                    pts = st.Pts.Select(q => new[] { Math.Round(q.X, 4), Math.Round(q.Z, 4) })
                                })
                            });
                        // planted fault: round 3 drew the jaws ON the node, art +x turned toward our connector
                        P2 back = new P2(o.X, o.Z), oldHandles = new P2(-back.Z, back.X);
                        Verdict old = Judge(theirs, home, (d.X, d.Z), (o.X, o.Z), home, back, oldHandles);
                        if (!(old.OnWire && old.OffNode && old.Along && old.Handles)) oldCaught++;
                        P2 side = new P2(-jaw.Z, jaw.X);
                        Verdict off = Judge(theirs, home, (d.X, d.Z), (o.X, o.Z), new P2(bite.X + 0.3 * side.X, bite.Z + 0.3 * side.Z), jaw, handles);
                        if (!off.OnWire && off.Along && off.Handles) offCaught++;
                        Verdict turn = Judge(theirs, home, (d.X, d.Z), (o.X, o.Z), bite, side, handles);
                        if (turn.OnWire && turn.OffNode && !turn.Along && turn.Handles) turnCaught++;
                        Verdict flip = Judge(theirs, home, (d.X, d.Z), (o.X, o.Z), bite, jaw, new P2(-handles.X, -handles.Z));
                        if (flip.OnWire && flip.Along && !flip.Handles) flipCaught++;
                    }
                }
            Check(scenes == 48 && good == scenes, $"{good}/{scenes} laid tap scenes put the jaws on their wire, along it, handles right " +
                                                  $"(worst {worst:0.000} cell off the strand, {worstDeg:0.0} deg)");
            Check(oldCaught == scenes, $"can fail: the round-3 pose (jaws on the node, turned toward ours) fails {oldCaught}/{scenes} scenes (want all)");
            Check(offCaught == scenes && turnCaught == scenes && flipCaught == scenes,
                  $"can fail, per predicate: bite 0.3 off the wire trips on-wire {offCaught}/{scenes}, jaws turned a quarter trip along " +
                  $"{turnCaught}/{scenes}, flipped handles trip handles {flipCaught}/{scenes} (want all)");
            if (Program.dumpDir != null)
                System.IO.File.WriteAllText(System.IO.Path.Combine(Program.dumpDir, "tapclamp_poses.json"), System.Text.Json.JsonSerializer.Serialize(dump));
            Console.WriteLine($"  tapclamp: {good}/{scenes} poses on their wire (worst {worst:0.000} cell, {worstDeg:0.0} deg); old pose caught {oldCaught}/{scenes}; mutants off/turn/flip {offCaught}/{turnCaught}/{flipCaught}");
        }
    }
}
