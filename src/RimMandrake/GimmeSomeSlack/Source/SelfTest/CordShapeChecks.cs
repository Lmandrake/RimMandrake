// cords_never_repeat (GSS_SHAPE_PROBE_MEASURE_NO_TWO_ALIKE): eight parallel runs of one length, no two the same drawn curve; a planted
// copy of one cord on another's ends reads as identical, so the instrument can fail.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class CordShapeChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "cord-shape: " + msg);

        /// <summary>Eight separate straight runs of one length, three cells apart, in open floor.</summary>
        private static CordWorld Room()
        {
            var w = new CordWorld(40, 44);
            for (int k = 0; k < 8; k++)
                for (int x = 6; x <= 30; x++) w.SetConduit(new Cell(x, 6 + 4 * k));
            return w;
        }

        /// <summary>The lived-in colony's kitchen corner: a run down the room's edge with a machine a few cells off it, walled.</summary>
        private static CordWorld KitchenLead()
        {
            var w = new CordWorld(24, 24);
            for (int k = 3; k <= 18; k++)
                foreach (Cell c in new[] { new Cell(k, 3), new Cell(k, 18), new Cell(3, k), new Cell(18, k) }) w.SetBlocked(c, BlockKind.Wall);
            for (int z = 4; z <= 17; z++) w.SetConduit(new Cell(17, z));
            for (int x = 6; x <= 16; x++) w.SetConduit(new Cell(x, 11));
            var heater = new MachineInfo { Id = "heater", Kind = MachineKind.Consumer, X0 = 15, Z0 = 6, W = 1, H = 1 };
            heater.Hookups.Add(new Cell(17, 6));
            w.SetBlocked(new Cell(15, 6), BlockKind.Device);
            w.Machines.Add(heater);
            return w;
        }

        /// <summary>Short stumps off a long run in a walled yard, as a blast leaves them: a short edge carrying a lot of spare length.</summary>
        private static CordWorld ShortStumps()
        {
            var w = new CordWorld(40, 30);
            for (int x = 3; x <= 36; x++) { w.SetConduit(new Cell(x, 12)); w.SetBlocked(new Cell(x, 18), BlockKind.Wall); }
            foreach (int x in new[] { 8, 16, 24, 32 })
                for (int z = 13; z <= 15; z++) w.SetConduit(new Cell(x, z));
            return w;
        }

        /// <summary>Conduit run wholly inside the wall of a room: a machine wired to it draws one cord, out of the wall's face and
        /// across the floor to it. Rock the same; hidden conduit draws nothing (M3); a lamp hard against the wall draws nothing.</summary>
        private static void InWallHookups()
        {
            foreach (BlockKind kind in new[] { BlockKind.Wall, BlockKind.Rock, BlockKind.Hidden })
            {
                var w = new CordWorld(30, 30);
                for (int x = 5; x <= 20; x++)
                    foreach (int z in new[] { 5, 20 })
                    {
                        w.SetConduit(new Cell(x, z));
                        if (kind == BlockKind.Hidden) w.SetForcedBuried(new Cell(x, z)); else w.SetBlocked(new Cell(x, z), kind);
                    }
                for (int z = 6; z <= 19; z++)
                    foreach (int x in new[] { 5, 20 })
                    {
                        w.SetConduit(new Cell(x, z));
                        if (kind == BlockKind.Hidden) w.SetForcedBuried(new Cell(x, z)); else w.SetBlocked(new Cell(x, z), kind);
                    }
                var far = new MachineInfo { Id = "far", Kind = MachineKind.Consumer, X0 = 12, Z0 = 11, W = 1, H = 1 };
                far.Hookups.Add(new Cell(12, 5));
                w.Machines.Add(far);
                var near = new MachineInfo { Id = "near", Kind = MachineKind.Consumer, X0 = 6, Z0 = 15, W = 1, H = 1 };
                near.Hookups.Add(new Cell(5, 15));
                w.Machines.Add(near);
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(w, new BuildOptions(), c => true);
                List<CordEdge> edges = b.Graph.CordEdges().ToList();
                bool farDrawn = edges.Any(e => e.A.T == 'm' && e.A.M == "far" || e.B.T == 'm' && e.B.M == "far");
                bool nearDrawn = edges.Any(e => e.A.T == 'm' && e.A.M == "near" || e.B.T == 'm' && e.B.M == "near");
                bool plate = ps.Any(p => p.Decals.Any(d => d.Kind == DecalKind.StubWall || d.Kind == DecalKind.StubRock));
                bool want = kind != BlockKind.Hidden;
                Check(farDrawn == want, $"{kind}: a machine across the room from its in-wall run draws {(farDrawn ? "a cord" : "nothing")}");
                Check(!nearDrawn, $"{kind}: a machine hard against its in-wall run draws {(nearDrawn ? "a cord" : "nothing")}");
                Check(plate == want, $"{kind}: the cord's plate on the face {(plate ? "drawn" : "absent")}");
                Check(!ps.Any(p => p.Strands.Any(s => s.Pts.Skip(3).Take(Math.Max(0, s.Pts.Count - 6)).Any(q => !w.IsWalkable(q.Floor)))), $"{kind}: the cord stays on the floor");
            }
        }

        public static void Run()
        {
            int alike = 0, cords = 0;
            double worst = double.MaxValue;
            foreach (ulong seed in new ulong[] { 1, 2, 3, 7, 19 })
            {
                List<LaidPiece> ps = new CordBuilder().Build(Room(), new BuildOptions { Seed = seed }, c => true);
                List<ShapeClass> t = CordShape.Table(ps);
                alike += t.Sum(c => c.TooAlike);
                cords += t.Sum(c => c.Cords);
                worst = Math.Min(worst, t.Where(c => c.Pairs > 0).Select(c => c.MinDistance).DefaultIfEmpty(double.MaxValue).Min());
            }
            Check(cords >= 40, $"the room lays {cords} cords over 5 seeds");
            Check(alike == 0, $"{alike} pairs of one length class under {CordShape.TooAlikeBelow} cells apart; closest pair {worst:0.00}");
            Console.WriteLine($"  cord shape: {cords} cords over 5 seeds, closest pair {worst:0.00} cells apart, {alike} too alike");

            // no strand folds back on itself, in a walled room with machines and a dense block as well as the open runs
            int strands = 0, folds = 0;
            foreach (ulong seed in new ulong[] { 1, 2, 3, 7, 19 })
                foreach (CordWorld w in new[] { Room(), ReviewRound1Checks.PileWorld() })
                    foreach (LaidPiece p in new CordBuilder().Build(w, new BuildOptions { Seed = seed }, c => true))
                        foreach (CordStrand s in p.Strands)
                        {
                            strands++;
                            folds += CordShape.Kinks(s.Pts).Count;
                        }
            Check(strands > 100 && folds <= strands / 20, $"{folds} folds in {strands} strands (bar: one in twenty, where the bend would leave open ground)");
            Console.WriteLine($"  cord folds: {folds} in {strands} strands");

            // no sawtooth (seen in a lived-in colony 2026-11-07: a stretch of settled cord buckled into a jag on a run cut to two cells), walled room and open alike
            foreach (var scene in new (string name, Func<CordWorld> make, bool laidHere)[] { ("open runs", Room, true), ("short stumps", ShortStumps, true), ("heap", ReviewRound1Checks.PileWorld, false) })
            {
                int jagStrands = 0, jags = 0;
                foreach (ulong seed in new ulong[] { 1, 2, 3, 7, 19, 23, 41, 57 })
                    foreach (LaidPiece p in new CordBuilder().Build(scene.make(), new BuildOptions { Seed = seed }, c => true))
                        foreach (CordStrand s in p.Strands)
                        {
                            jagStrands++;
                            jags += CordShape.Saws(s.Pts);
                        }
                Console.WriteLine($"  cord saws, {scene.name}: {jags} in {jagStrands} strands");
                if (scene.laidHere) Check(jags <= jagStrands / 8, $"{scene.name}: {jags} sawtooth stretches in {jagStrands} strands (bar: one in eight; before the relaxing 30 and 40 in these scenes, and what stays is inside a coil bunch, plotted 2026-11-07)");
            }

            // one cord reads as one cord (owner 2026-11-07, three cables to one terminal): a lead across a walled room to a machine must not run back alongside itself
            {
                int leads = 0, over = 0;
                double worstD = 0;
                foreach (ulong seed in new ulong[] { 1, 2, 3, 7, 19, 23, 41, 57, 88, 101, 133, 200 })
                    foreach (LaidPiece p in new CordBuilder().Build(KitchenLead(), new BuildOptions { Seed = seed }, c => true))
                        foreach (CordStrand s in p.Strands)
                        {
                            leads++;
                            double d = CordShape.Doubled(s.Pts);
                            worstD = Math.Max(worstD, d);
                            if (d > CordShape.DoubledMax) over++;
                        }
                Console.WriteLine($"  cord doubled: {over} of {leads} strands over, worst {worstD:0.00} cells");
                Check(leads > 40 && over <= leads / 20, $"{over} of {leads} strands run back alongside themselves (worst {worstD:0.00} cells)");
                // planted: a Z of three parallel lines reads as doubled, a plain circle does not, two broad loops far apart do not
                var zed = new List<V2>();
                for (int k = 0; k <= 60; k++) zed.Add(new V2(5 + k * 0.05, 5));
                for (int k = 0; k <= 10; k++) zed.Add(new V2(8, 5 + k * 0.05));
                for (int k = 0; k <= 60; k++) zed.Add(new V2(8 - k * 0.05, 5.5));
                for (int k = 0; k <= 10; k++) zed.Add(new V2(5, 5.5 + k * 0.05));
                for (int k = 0; k <= 60; k++) zed.Add(new V2(5 + k * 0.05, 6));
                Check(CordShape.Doubled(zed) > CordShape.DoubledMax, $"planted Z reads {CordShape.Doubled(zed):0.00} cells doubled");
                var ring = new List<V2>();
                for (int k = 0; k <= 200; k++) ring.Add(new V2(9 + 0.5 * Math.Cos(k * 0.0628), 9 + 0.5 * Math.Sin(k * 0.0628)));
                Check(CordShape.Doubled(ring) < 0.01, $"a coil is not doubled ({CordShape.Doubled(ring):0.00})");
            }

            // a cord's slack stays out of a door its route does not run through (owner 2026-11-07, three cables out of a doorway): a run along a wall of doors, a route through one door
            {
                Func<CordWorld> doors = () =>
                {
                    var w = new CordWorld(40, 26);
                    for (int x = 3; x <= 36; x++)
                    {
                        if (x % 5 == 0) w.SetDoor(new Cell(x, 13)); else w.SetBlocked(new Cell(x, 13), BlockKind.Wall);
                        w.SetConduit(new Cell(x, 11));
                    }
                    for (int z = 11; z <= 19; z++) w.SetConduit(new Cell(20, z));
                    return w;
                };
                int strands2 = 0, strays = 0, oldStrays = 0;
                foreach (ulong seed in new ulong[] { 1, 2, 3, 7, 19, 23, 41, 57, 88, 101, 133, 200 })
                {
                    foreach (LaidPiece p in new CordBuilder().Build(doors(), new BuildOptions { Seed = seed }, c => true))
                        foreach (CordStrand s in p.Strands) { strands2++; strays += s.DoorStrays; }
                    // the plain draw, with no second look, as the control: this scene must be able to fail
                    var line = new List<V2>();
                    for (double x = 4; x <= 35; x += 0.05) line.Add(new V2(x, 11.5));
                    oldStrays += CordShape.DoorStrays(doors(), CordLayer.Sprawl(doors(), line, new BuildOptions().Lay, 0.8, 8, CordRng.Of(seed, "b"), CordRng.Of(seed, "s"), 1), line);
                }
                Console.WriteLine($"  door strays: {strays} in {strands2} strands; plain draw {oldStrays}");
                Check(oldStrays > 0, $"can-fail: the plain draw goes under doors {oldStrays} times");
                Check(strands2 > 40 && strays <= strands2 / 50, $"{strays} stray passes under a door in {strands2} strands");
                var pl = new CordWorld(12, 12);
                pl.SetDoor(new Cell(6, 6));
                var through = new List<V2> { new V2(6.5, 4), new V2(6.5, 5), new V2(6.5, 6.5), new V2(6.5, 8) };
                var thrice = new List<V2> { new V2(6.5, 4), new V2(6.5, 6.5), new V2(6.5, 8), new V2(6.5, 6.5), new V2(6.5, 4), new V2(6.5, 6.5), new V2(6.5, 8) };
                Check(CordShape.DoorStrays(pl, through, through) == 0, "a cord through a door its route runs through is no stray");
                Check(CordShape.DoorStrays(pl, through, new List<V2>()) == 1, "under a door off its route: one stray");
                Check(CordShape.DoorStrays(pl, thrice, through) == 2, "three passes under its one door: two strays");
            }

            // planted: a sawtooth reads as jags, relaxing removes them, the strand's ends stay put, a one-way coil is not one
            {
                var saw = new List<V2>();
                for (int k = 0; k <= 120; k++) saw.Add(new V2(5 + k * 0.04, 5 + (k > 40 && k < 80 ? 0.05 * ((k / 3) % 2 == 0 ? 1 : -1) : 0)));
                var open = new CordWorld(20, 20);
                Check(CordShape.Jags(saw).Count >= 2, $"planted sawtooth reads {CordShape.Jags(saw).Count} jags");
                List<V2> calm = CordShape.Dejag(open, saw);
                Check(CordShape.Jags(calm).Count == 0 && V2.Dist(calm[0], saw[0]) < 1e-9 && V2.Dist(calm[calm.Count - 1], saw[saw.Count - 1]) < 1e-9,
                    $"relaxed: {CordShape.Jags(calm).Count} jags left, ends in place");
                var coil = new List<V2>();
                for (int k = 0; k <= 100; k++) coil.Add(new V2(8 + 0.4 * Math.Cos(k * 0.15), 8 + 0.4 * Math.Sin(k * 0.15)));
                Check(CordShape.Jags(coil).Count == 0, $"a coil is not a jag ({CordShape.Jags(coil).Count})");
            }

            InWallHookups();

            // planted: a hairpin reads as a fold, rounding removes it, and the strand's ends stay put
            {
                var hair = new List<V2>();
                for (int k = 0; k <= 40; k++) hair.Add(new V2(5 + k * 0.05, 5));
                for (int k = 39; k >= 0; k--) hair.Add(new V2(5 + k * 0.05, 5.01));
                var open = new CordWorld(20, 20);
                Check(CordShape.Kinks(hair).Count == 1, $"planted hairpin reads {CordShape.Kinks(hair).Count} folds");
                List<V2> round = CordShape.Unfold(open, hair);
                Check(CordShape.Kinks(round).Count == 0 && round[0].X == hair[0].X && V2.Dist(round[round.Count - 1], hair[hair.Count - 1]) < 1e-9, "the hairpin rounds, its ends unmoved");
            }

            // planted: the same drawn vertices on two distinct edges, one laid again turned, moved and running the other way
            {
                List<LaidPiece> ps = new CordBuilder().Build(Room(), new BuildOptions(), c => true);
                LaidPiece a = ps.First(p => p.EndA != null && p.Owner.Z == 6);
                var moved = new List<V2>();
                foreach (V2 q in Enumerable.Reverse(a.Strands[0].Pts)) moved.Add(CordAudit.Rot(q, 1.1) + new V2(3, 40));
                var twin = new LaidPiece { Key = "twin", EndA = "planted:0,0", EndB = "planted:1,1", PathLen = a.PathLen };
                twin.Strands.Add(new CordStrand { Pts = moved });
                List<ShapeClass> t = CordShape.Table(new[] { a, twin });
                Check(t.Count == 1 && t[0].TooAlike == 1 && t[0].MinDistance < 0.05, $"planted: a cord and its moved, turned, reversed copy read {(t.Count > 0 ? t[0].MinDistance : -1):0.000} apart");
            }
        }
    }
}
