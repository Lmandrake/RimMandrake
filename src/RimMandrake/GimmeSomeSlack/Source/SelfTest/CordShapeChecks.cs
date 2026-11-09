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

        /// <summary>Pass-17 diagnostic (--shape-diag): where the folds sit, and which cords a sliced lay lays differently from one plain Build.</summary>
        internal static void Diag()
        {
            foreach (string look in new[] { "Scrapper", "Modern" })
            {
                string f = System.IO.Path.Combine(Environment.CurrentDirectory, "ba_" + look + ".json");
                if (!System.IO.File.Exists(f)) { Console.WriteLine("TIME no " + f); continue; }
                using var doc = System.Text.Json.JsonDocument.Parse(System.IO.File.ReadAllText(f));
                CordWorld w = LabWorld.Read(doc.RootElement, out BuildOptions opt, out HashSet<Cell> liveT);
                var bt = new CordBuilder();
                var sw = System.Diagnostics.Stopwatch.StartNew();
                bt.Build(w, opt, c => liveT.Contains(c));
                Console.WriteLine($"TIME {look}: a cold Build {sw.Elapsed.TotalMilliseconds:0.0} ms");
                sw.Restart();
                for (int k = 0; k < 10; k++) bt.Build(w, opt, c => liveT.Contains(c));
                double all = sw.Elapsed.TotalMilliseconds / 10;
                opt.Tangles = false;
                var b2 = new CordBuilder();
                b2.Build(w, opt, c => liveT.Contains(c));
                sw.Restart();
                for (int k = 0; k < 10; k++) b2.Build(w, opt, c => liveT.Contains(c));
                Console.WriteLine($"TIME {look}: a reused Build {all:0.00} ms with heaps, {sw.Elapsed.TotalMilliseconds / 10:0.00} ms without");
            }
            {
                var sb = new System.Text.StringBuilder("{\"walks\":[");
                var ic = System.Globalization.CultureInfo.InvariantCulture;   // JSON numbers need '.' in every locale
                Func<V2, bool> g0 = null;
                int nw = 0;
                CordBuilder.HeapWalkTrace = (pts, stops, done, g) =>
                {
                    g0 = g;
                    if (nw++ > 0) sb.Append(',');
                    sb.Append("{\"done\":").Append(done ? "true" : "false").Append(",\"stops\":[").Append(string.Join(",", stops.Select(q => string.Format(ic, "[{0:0.###},{1:0.###}]", q.X, q.Z))))
                      .Append("],\"pts\":[").Append(string.Join(",", pts.Select(q => string.Format(ic, "[{0:0.###},{1:0.###}]", q.X, q.Z)))).Append("]}");
                };
                CordBuilder.HeapWalkWhy = t => Console.WriteLine("WHY " + t);
                List<LaidPiece> ps0 = new CordBuilder().Build(ReviewRound1Checks.PileWorld(), new BuildOptions { Seed = 1 }, c => true);
                CordBuilder.HeapWalkWhy = null;
                CordBuilder.HeapWalkTrace = null;
                sb.Append("],\"ground\":[");
                bool f = true;
                for (double x = 4; x < 13; x += 0.1)
                    for (double z = 4; z < 13; z += 0.1)
                        if (g0 != null && g0(new V2(x, z))) { if (!f) sb.Append(','); f = false; sb.Append(string.Format(ic, "[{0:0.##},{1:0.##}]", x, z)); }
                sb.Append("],\"decals\":[").Append(string.Join(",", ps0.Where(p => p.Key.StartsWith("tangle")).SelectMany(p => p.Decals).Select(d => string.Format(ic, "[\"{0}\",{1:0.###},{2:0.###},{3:0.###},{4:0.###}]", d.Kind, d.Pos.X, d.Pos.Z, d.Angle, d.Scale)))).Append("]}");
                System.IO.File.WriteAllText(System.IO.Path.Combine(Environment.CurrentDirectory, "heapwalk_trace.json"), sb.ToString());
                Console.WriteLine($"HEAPTRACE {nw} attempts -> heapwalk_trace.json in {Environment.CurrentDirectory}");
            }
            foreach (ulong seed in new ulong[] { 1, 2, 3, 7, 19 })
                foreach (var (name, w) in new[] { ("room", Room()), ("pile", ReviewRound1Checks.PileWorld()) })
                    foreach (LaidPiece p in new CordBuilder().Build(w, new BuildOptions { Seed = seed }, c => true))
                        for (int si = 0; si < p.Strands.Count; si++)
                        {
                            List<V2> P = p.Strands[si].Pts;
                            double[] cum = Geo.CumLen(P);
                            foreach (V2 k in CordShape.Kinks(P))
                            {
                                int i = P.IndexOf(k);
                                Console.WriteLine($"FOLD {name} s{seed} [{p.EndA} | {p.EndB}] key={(p.Key ?? "").Split('#')[0]} strand {si}/{p.Strands.Count} L={cum[cum.Length - 1]:0.00} at {cum[i]:0.00} ({k.X:0.00},{k.Z:0.00})");
                            }
                        }
            Func<Cell, bool> live = c => ((c.X * 7 + c.Z * 3) & 1) == 0;
            var (cells, lamps) = CordScaleBench.Lattice(2);
            int n = Math.Min(120, cells.Count / 2), nc0 = cells.Count - n;
            List<LaidPiece> one = new CordBuilder().Build(CordScaleBench.World(2, nc0, lamps.Count), new BuildOptions(), live);
            var b = new CordBuilder();
            List<LaidPiece> outp = null;
            for (int i = 0; i < 60; i++)
            {
                outp = b.Build(CordScaleBench.World(2, nc0, lamps.Count), new BuildOptions { AsyncLay = true }, live);
                if (b.LastPending == 0 && !b.LayRunning) break;
                var waited = System.Diagnostics.Stopwatch.StartNew();   // bounded: a stalled worker fails the diagnostic, never hangs it
                while (b.LayRunning && waited.Elapsed.TotalSeconds < 120) System.Threading.Thread.Sleep(1);
                if (b.LayRunning) { Console.WriteLine("SLICE FAIL: the lay worker is still running after 120 s"); return; }
            }
            var byKey = one.Where(p => p.Key != null).GroupBy(p => p.Key).ToDictionary(g => g.Key, g => g.First());
            int diff = 0;
            foreach (LaidPiece p in outp)
            {
                if (p.Key == null || !byKey.TryGetValue(p.Key, out LaidPiece q)) { Console.WriteLine($"SLICE only in sliced: {p.Key}"); diff++; continue; }
                string why = null;
                if (p.Strands.Count != q.Strands.Count) why = $"strands {p.Strands.Count} vs {q.Strands.Count}";
                else for (int si = 0; si < p.Strands.Count && why == null; si++)
                    {
                        List<V2> a = p.Strands[si].Pts, c = q.Strands[si].Pts;
                        if (a.Count != c.Count) { why = $"strand {si} pts {a.Count} vs {c.Count}"; break; }
                        for (int j = 0; j < a.Count; j++) if (V2.Dist(a[j], c[j]) > 5e-4) { why = $"strand {si} pt {j}/{a.Count} ({a[j].X:0.000},{a[j].Z:0.000}) vs ({c[j].X:0.000},{c[j].Z:0.000})"; break; }
                    }
                if (why == null && p.Decals.Count != q.Decals.Count) why = $"decals {p.Decals.Count} vs {q.Decals.Count}";
                if (why == null && p.Ends.Count != q.Ends.Count) why = $"ends {p.Ends.Count} vs {q.Ends.Count}";
                if (why != null) { diff++; if (diff <= 30) Console.WriteLine($"SLICE differs [{p.EndA} | {p.EndB}] {why}"); }
            }
            Console.WriteLine($"HEAPWALK misses {CordBuilder.HeapWalkMisses}, attempts off the ground {CordBuilder.HeapWalkOff}, over budget {CordBuilder.HeapWalkLong}");
            Console.WriteLine($"SLICE {diff} pieces differ of {outp.Count} (plain {one.Count}); live misses {CordBuilder.LiveMisses}");
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
                            int fk = CordShape.Kinks(s.Pts).Count;
                            folds += fk;
                            if (fk > 0 && folds <= 8) Console.WriteLine($"  FOLD seed {seed} [{p.EndA} | {p.EndB}] {p.Key} x{fk} at {string.Join(" ", CordShape.Kinks(s.Pts).Select(q => $"({q.X:0.00},{q.Z:0.00})"))}");
                        }
            Check(strands > 100 && folds <= strands / 20, $"{folds} folds in {strands} strands (bar: one in twenty, where the bend would leave open ground)");
            Console.WriteLine($"  cord folds: {folds} in {strands} strands");
            PolishChecks();
            CurvatureRepairChecks();

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

            // one cord through a door to a conduit end draws two lines at that door, and no coil on its own end (owner 2026-11-07, three cables out of a doorway to one terminal node).
            // Every seed and length of the plain case, with the plain draw as the control, which lays coils there.
            {
                Func<int, CordWorld> room = d =>
                {
                    var w = new CordWorld(50, 30);
                    for (int z = 4; z <= 26; z++) if (z != 15) w.SetBlocked(new Cell(20, z), BlockKind.Wall);
                    w.SetDoor(new Cell(20, 15));
                    for (int x = 6; x <= 20 + d; x++) w.SetConduit(new Cell(x, 15));
                    return w;
                };
                int lays = 0, returns = 0, doorReturns = 0, plain = 0;
                foreach (int d in new[] { 2, 3, 4, 6, 8, 12, 18 })
                    foreach (ulong seed in new ulong[] { 1, 2, 3, 4, 5, 6 })
                    {
                        CordWorld w = room(d);
                        foreach (LaidPiece p in new CordBuilder().Build(w, new BuildOptions { Seed = seed }, c => true))
                            foreach (CordStrand st in p.Strands)
                            {
                                lays++;
                                returns += CordShape.RingReturns(w, st.Pts, out int atDoor) - atDoor;
                                doorReturns += atDoor;
                            }
                        var line = new List<V2>();
                        for (double x = 6.5; x <= 20.5 + d; x += 0.05) line.Add(new V2(x, 15.5));
                        plain += CordShape.RingReturns(w, CordLayer.Sprawl(w, line, new BuildOptions().Lay, 0.8, 8, CordRng.Of(seed, "b"), CordRng.Of(seed, "s"), 1));
                    }
                Console.WriteLine($"  ring returns: {doorReturns} at the door and {returns} at an end in {lays} lays through a door; plain draw {plain}");
                Check(plain > 0, $"can-fail: the plain draw lays coils on a door or an end ({plain} extra lines)");
                Check(lays >= 42 && doorReturns == 0, $"a cord through a door crosses it once: {doorReturns} extra lines there in {lays} lays");
                // a long cord takes three draws, not six, for a coil at its own end (its settle is what a frame's budget feels): one end in ten may keep one
                Check(returns <= lays / 10, $"a cord through a door reaches its end once: {returns} extra lines at an end in {lays} lays");
                var coil = new List<V2> { new V2(10, 15.5) };
                for (double t = 0; t < 2 * Math.PI; t += 0.1) coil.Add(new V2(19 + 2.2 * Math.Cos(t), 15.5 + 2.2 * Math.Sin(t)));
                coil.Add(new V2(21.5, 15.5));
                coil.Add(new V2(30, 15.5));
                Check(CordShape.RingReturns(room(10), coil) > 0, "a loop round a door reads as extra lines there");
                var plainPass = new List<V2> { new V2(10, 15.5), new V2(20.5, 15.5), new V2(30, 15.5) };
                Check(CordShape.RingReturns(room(10), plainPass) == 0, "one pass through a door reads none");
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

            // a slack cord on open floor takes slow, wide curves, no hairpin (owner 2026-11-07 7:07 PM: "what they avoid are sharp curves unless they must ... slowly curving
            // loops as the preferred option"): a short hop given a lot of slack, the lay a row of junctions draws, with no loops or heaps (those coil on purpose).
            // The excursions as drawn before (RoundExcursions off) as the control: a tall narrow finger, a hairpin at its tip.
            {
                var open = new CordWorld(30, 30);
                int Sharp(List<V2> Q)
                {
                    List<V2> R = Geo.Resample(Q, 0.05);
                    double[] s = Geo.CumLen(R);
                    int bends = 0;
                    bool inBend = false;
                    for (int i = 5; i < R.Count - 5; i++)
                    {
                        V2 a = R[i - 5], b = R[i], c = R[i + 5];
                        double cross = Math.Abs((b.X - a.X) * (c.Z - a.Z) - (b.Z - a.Z) * (c.X - a.X));
                        bool tight = s[i] > 1.0 && s[s.Length - 1] - s[i] > 1.0 && cross > 1e-12
                                     && V2.Dist(a, b) * V2.Dist(b, c) * V2.Dist(c, a) / (2 * cross) < 0.6;
                        if (tight && !inBend) bends++;
                        inBend = tight;
                    }
                    return bends;
                }
                int sharpOff = 0, sharpOn = 0, lays = 0;
                foreach (double hop in new[] { 3.0, 4.0, 5.0, 6.0 })
                    foreach (ulong seed in new ulong[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 })
                    {
                        var line = new List<V2>();
                        for (double x = 13; x <= 13 + hop + 1e-9; x += 0.05) line.Add(new V2(x, 15.5));
                        var off = new BuildOptions().Lay;
                        off.LoopsPerCell = 0; off.HeapP = 0; off.RoundExcursions = false;
                        var on = new BuildOptions().Lay;
                        on.LoopsPerCell = 0; on.HeapP = 0;     // the builder's own lay: with RoundExcursions off there the row fails
                        sharpOff += Sharp(CordLayer.Sprawl(open, line, off, 1.2, 8, CordRng.Of(seed, "b"), CordRng.Of(seed, "s"), 1));
                        sharpOn += Sharp(CordLayer.Sprawl(open, line, on, 1.2, 8, CordRng.Of(seed, "b"), CordRng.Of(seed, "s"), 1));
                        lays++;
                    }
                Console.WriteLine($"  bends tighter than 0.6 cell on open floor: {sharpOn} in {lays} short slack hops; drawn as before {sharpOff}");
                Check(sharpOff >= lays / 2, $"can-fail: the excursions as drawn before bend tighter than 0.6 cell {sharpOff} times in {lays} hops");
                Check(sharpOn <= sharpOff / 4, $"a slack hop on open floor bends tighter than 0.6 cell {sharpOn} times in {lays} hops (as drawn before {sharpOff})");
            }
        }

        private static void CurvatureRepairChecks()
        {
            var open = new CordWorld(40, 40);
            bool Same(V2 a, V2 b) => a.X == b.X && a.Z == b.Z;
            bool Pinned(List<V2> before, List<V2> after)
            {
                double[] s = Geo.CumLen(before);
                int a = 0, b = before.Count - 1;
                while (a < before.Count - 1 && s[a] < CordShape.RepairPin) a++;
                while (b > 0 && s[b] > s[s.Length - 1] - CordShape.RepairPin) b--;
                if (after.Count < Math.Max(a + 1, before.Count - b)) return false;
                for (int i = 0; i <= a; i++) if (!Same(before[i], after[i])) return false;
                for (int i = b; i < before.Count; i++)
                    if (!Same(before[i], after[after.Count - before.Count + i])) return false;
                return true;
            }

            var elbow = new List<V2>();
            for (int i = 0; i <= 100; i++) elbow.Add(new V2(5 + i * 0.05, 10));
            for (int i = 1; i <= 100; i++) elbow.Add(new V2(10, 10 + i * 0.05));
            Check(CordShape.CurvatureFaults(elbow).Count > 0, "final repair sees a planted corner");
            List<V2> round = CordShape.RepairCurvature(open, elbow);
            Check(CordShape.CurvatureFaults(round).Count == 0, "final repair rounds the corner through both joins");
            Check(Pinned(elbow, round), "final repair preserves both 0.35-cell end runs exactly");

            var tied = new List<V2>();
            for (int i = 0; i <= 100; i++)
                tied.Add(new V2(5 + i * 0.05, 20 + (i > 35 && i < 65 ? 0.06 * Math.Sin(i * 2.2) : 0)));
            int loopStart = tied.Count - 1;
            V2 crossing = tied[loopStart];
            double s0 = Geo.Length(tied);
            for (int i = 1; i <= 64; i++)
            {
                double h = -Math.PI / 2 + 2 * Math.PI * i / 64;
                tied.Add(i == 64 ? crossing : new V2(crossing.X + 0.16 * Math.Cos(h), crossing.Z + 0.16 + 0.16 * Math.Sin(h)));
            }
            double s1 = Geo.Length(tied);
            for (int i = 1; i <= 100; i++) tied.Add(crossing + new V2(i * 0.05, 0));
            var ties = new List<CordTie> { new CordTie { S0 = s0, S1 = s1, At = crossing } };
            Check(CordShape.CurvatureFaults(tied, ties).Count > 0, "a tied loop does not hide a separate planted sawtooth");
            List<V2> calm = CordShape.RepairCurvature(open, tied, ties);
            Check(CordShape.CurvatureFaults(calm, ties).Count == 0, "final repair removes the separate sawtooth");
            int start = calm.FindIndex(q => Same(q, crossing));
            bool kept = start >= 0 && start + 64 < calm.Count;
            for (int i = 0; i <= 64 && kept; i++) kept = Same(tied[loopStart + i], calm[start + i]);
            Check(kept && Pinned(tied, calm), "final repair preserves the entire tied loop and both end runs exactly");
            if (kept)
            {
                double[] s = Geo.CumLen(calm);
                Check(Math.Abs(ties[0].S0 - s[start]) < 1e-9 && Math.Abs(ties[0].S1 - s[start + 64]) < 1e-9,
                    "a repair before a tie updates its arc offsets");
            }

            var broad = new List<V2>();
            for (int i = 0; i <= 200; i++)
                broad.Add(new V2(20 + 2 * Math.Cos(i * 0.025), 20 + 2 * Math.Sin(i * 0.025)));
            Check(!CordShape.MayNeedCurvatureRepair(broad)
                && CordShape.CurvatureFaults(broad).Count == 0
                && ReferenceEquals(broad, CordShape.RepairCurvature(open, broad)),
                "a broad clean curve takes the cheap path and retains its original list");
            var duplicateElbow = new List<V2>(elbow);
            duplicateElbow.Insert(101, elbow[100]);
            Check(CordShape.MayNeedCurvatureRepair(duplicateElbow)
                && CordShape.CurvatureFaults(CordShape.RepairCurvature(open, duplicateElbow)).Count == 0,
                "a duplicate vertex cannot hide a corner from the cheap bound");
            var shifted = new List<V2>(elbow);
            shifted.Add(elbow[elbow.Count - 1] + new V2(0, 0.007));
            List<double> beforeShift = CordShape.CurvatureFaults(elbow);
            List<double> afterShift = CordShape.CurvatureFaults(shifted);
            Check(beforeShift.SequenceEqual(afterShift),
                "a distant length change does not move existing curvature samples");

            var blocked = new CordWorld(30, 30);
            blocked.SetBlocked(new Cell(10, 10), BlockKind.Wall);
            Check(!CordShape.RepairSegmentClear(blocked, new V2(9.8, 10.3), new V2(10.3, 9.8)),
                "segment clearance catches a blocked corner between clear endpoints");
            Check(!CordShape.RepairSegmentClear(null, new V2(9, 5), new V2(12, 5), q => q.X < 10 || q.X > 11),
                "segment clearance applies the supplied ground rule between vertices");
        }

        /// <summary>The polish: planted sawtooth and corners come out, the ends stay point for point;
        /// a strip beside a device keeps its captive lead upstream and takes the device through a socket PlugTop.</summary>
        private static void PolishChecks()
        {
            var open = new CordWorld(40, 40);
            var saw = new List<V2>();
            for (int i = 0; i <= 200; i++) saw.Add(new V2(5 + i * 0.05, 20 + (i > 60 && i < 140 ? 0.05 * Math.Sin(i * 2.2) : 0)));
            Check(CordShapeAudit.Corners(saw).Count > 0, "planted sawtooth reads as corners");
            List<V2> calm = CordShape.Polish(open, saw);
            Check(CordShapeAudit.Corners(calm).Count == 0, $"polish takes the sawtooth out ({CordShapeAudit.Corners(calm).Count} left)");
            Check(calm[0].X == saw[0].X && calm[calm.Count - 1].X == saw[saw.Count - 1].X && calm[3].Z == saw[3].Z, "polish leaves both ends as laid");
            var elbow = new List<V2>();
            for (int i = 0; i <= 40; i++) elbow.Add(new V2(5 + i * 0.05, 20));
            for (int i = 1; i <= 40; i++) elbow.Add(new V2(7, 20 + i * 0.05));
            Check(CordShapeAudit.Corners(elbow).Count == 1, "planted right angle reads as one corner");
            Check(CordShapeAudit.Corners(CordShape.Polish(open, elbow)).Count == 0, "polish rounds the right angle");
            var coil = new List<V2>();
            for (int i = 0; i < 160; i++) coil.Add(new V2(10 + 0.3 * Math.Cos(i * 0.16), 10 + 0.3 * Math.Sin(i * 0.16)));
            Check(CordShapeAudit.Corners(coil).Count == 0 && Geo.Length(CordShape.Polish(open, coil)) > 0.8 * Geo.Length(coil), "a coil of 0.3 cell is no corner and keeps its size");
            // slack under a machine it does not plug into reads as extra cables into it: the count sees a planted pass, spares a route that really crosses, and laying leaves almost none
            var bench = new CordWorld(40, 20);
            bench.Machines.Add(new MachineInfo { Id = "bench", Kind = MachineKind.Consumer, X0 = 18, Z0 = 11, W = 3, H = 1 });
            var pass = new List<V2>();
            for (int i = 0; i <= 200; i++) pass.Add(new V2(10 + i * 0.1, 11.5));
            Check(CordShape.MachineStrays(bench, pass, null) > 0, "a planted pass under a bench reads as a stray");
            Check(CordShape.MachineStrays(bench, pass, pass) == 0, "a route that really crosses the bench is no stray");
            int straysLaid = 0, strandsLaid = 0;
            for (ulong seed = 1; seed <= 12; seed++)
            {
                var room = new CordWorld(40, 24);
                for (int x = 4; x <= 34; x++) room.SetConduit(new Cell(x, 10));
                room.Machines.Add(new MachineInfo { Id = "bench", Kind = MachineKind.Consumer, X0 = 17, Z0 = 12, W = 3, H = 1, Hookups = new List<Cell> { new Cell(18, 10) } });
                foreach (LaidPiece p in new CordBuilder().Build(room, new BuildOptions { Seed = seed }, c => true))
                    if (p.EndA != null && !p.EndA.StartsWith("consumer") && !p.EndB.StartsWith("consumer"))
                        foreach (CordStrand t in p.Strands) { strandsLaid++; straysLaid += CordShape.MachineStrays(room, t.Pts, null); }
            }
            Check(strandsLaid > 0 && straysLaid * 10 <= strandsLaid, $"laying keeps a through cord's slack out from under a bench: {straysLaid} passes in {strandsLaid} strands");
            // the same under furniture (judge, pass 12: a bed "plugged in twice"): beds either side of a conduit run; the control lays the room with no furniture marked
            {
                CordWorld Bedroom(bool furnished)
                {
                    var r = new CordWorld(40, 24);
                    for (int x = 4; x <= 34; x++) r.SetConduit(new Cell(x, 10));
                    r.Machines.Add(new MachineInfo { Id = "bench", Kind = MachineKind.Consumer, X0 = 17, Z0 = 12, W = 3, H = 1, Hookups = new List<Cell> { new Cell(18, 10) } });
                    if (furnished)
                    {
                        foreach (int x in new[] { 8, 11, 14, 22, 25, 28 }) { r.SetFurniture(new Cell(x, 11)); r.SetFurniture(new Cell(x, 12)); }
                        foreach (int x in new[] { 10, 13, 20, 23, 26 }) { r.SetFurniture(new Cell(x, 8)); r.SetFurniture(new Cell(x, 9)); }
                    }
                    return r;
                }
                int under = 0, underOld = 0, strands = 0;
                CordWorld marks = Bedroom(true);
                for (ulong seed = 1; seed <= 12; seed++)
                {
                    foreach (bool furnished in new[] { true, false })
                        foreach (LaidPiece p in new CordBuilder().Build(Bedroom(furnished), new BuildOptions { Seed = seed }, c => true))
                            if (p.EndA != null && !p.EndA.StartsWith("consumer") && !p.EndB.StartsWith("consumer"))
                                foreach (CordStrand t in p.Strands)
                                {
                                    int u = CordShape.FurnitureStrays(marks, t.Pts, null);
                                    if (furnished) { strands++; under += u; } else underOld += u;
                                }
                }
                Console.WriteLine($"  furniture: {under} passes under a bed in {strands} strands; laid blind to the beds {underOld}");
                Check(underOld >= 4, $"can-fail: laid blind to the beds, a through cord's slack passes under one {underOld} times");
                Check(strands > 0 && under * 4 <= underOld, $"laying keeps a through cord's slack out from under beds: {under} passes in {strands} strands (blind to them {underOld})");
            }
            // A Modern T beside a device: the captive lead takes the upstream arm;
            // this device branch must attach to a socket through a seated PlugTop.
            var w = new CordWorld(30, 20);
            for (int x = 4; x <= 24; x++) w.SetConduit(new Cell(x, 8));
            // World/lab machine kind 0 is a source. Without a supply this fixture
            // cannot assert which graph edge is upstream.
            w.SetBlocked(new Cell(5, 6), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "supply", Kind = (MachineKind)0, X0 = 5, Z0 = 6, W = 1, H = 1, Hookups = new List<Cell> { new Cell(5, 8) } });
            w.SetBlocked(new Cell(14, 9), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "lamp", Kind = MachineKind.Consumer, X0 = 14, Z0 = 9, W = 1, H = 1, Hookups = new List<Cell> { new Cell(14, 8) } });
            var b = new CordBuilder();
            List<LaidPiece> ps = b.Build(w, JunctionStripChecks.Modern(), c => true);
            LaidPiece lead = ps.FirstOrDefault(p => p.EndA != null && (p.EndA.StartsWith("consumer") || p.EndB.StartsWith("consumer")));
            CordEdge device = b.Graph.CordEdges().First(e =>
                (b.Graph.Nodes[e.A].IsMachine && b.Graph.Nodes[e.A].Machine?.Id == "lamp")
                || (b.Graph.Nodes[e.B].IsMachine && b.Graph.Nodes[e.B].Machine?.Id == "lamp"));
            VId v = b.Graph.Nodes[device.A].IsMachine ? device.B : device.A;
            bool atA = device.A.Equals(v);
            CordBuilder.StripPose sp = CordBuilder.PoseStrip(b.Graph, v, JunctionStripChecks.Modern().Seed);
            V2 ad = CordBuilder.ArmDir(b.Graph, device, atA);
            var deviceArm = new Cell((int)ad.X, (int)ad.Z);
            CordEdge upstream = b.Graph.StripLeadOf(v);
            V2 supplyDir = upstream == null ? default(V2) : CordBuilder.ArmDir(b.Graph, upstream, upstream.A.Equals(v));
            Check(upstream != null && !ReferenceEquals(upstream, device)
                && sp.LeadArm == new Cell((int)supplyDir.X, (int)supplyDir.Z)
                && sp.LeadArm != deviceArm,
                "a strip's captive lead takes the upstream arm, not the machine beside it");

            bool DeviceSocketRule(LaidPiece cord)
            {
                if (cord == null || cord.Strands.Count != 1) return false;
                List<CordDecal> tops = cord.Decals.Where(d => d.Kind == DecalKind.PlugTop).ToList();
                if (tops.Count != 1) return false;
                CordDecal top = tops[0];
                if (!Enumerable.Range(0, CordBuilder.StripHeads.Length)
                    .Any(k => V2.Dist(top.Pos, sp.SocketAt(k)) < 1e-8)) return false;
                V2 outDir = CordAudit.Dir(top.Angle);
                if (V2.Dist(outDir, sp.PlugOut(deviceArm)) > 1e-8) return false;
                V2 boot = top.Pos + outDir * CordBuilder.PlugTopReach;
                foreach (CordStrand s in cord.Strands)
                {
                    if (s.Pts == null || s.Pts.Count < 2) return false;
                    V2 a = s.Pts[0], z = s.Pts[s.Pts.Count - 1];
                    if (V2.Dist(atA ? a : z, boot) > 1e-7
                        || V2.Dist(a, sp.LeadTip) < 1e-7
                        || V2.Dist(z, sp.LeadTip) < 1e-7) return false;
                }
                return true;
            }
            Check(DeviceSocketRule(lead),
                "the adjacent machine's cord ends at a socket PlugTop boot; neither end uses the captive lead point");
            if (lead != null && lead.Strands.Count == 1 && lead.Strands[0].Pts.Count >= 2)
            {
                var missingPlug = new LaidPiece
                {
                    Strands = lead.Strands,
                    Decals = lead.Decals.Where(d => d.Kind != DecalKind.PlugTop).ToList()
                };
                Check(!DeviceSocketRule(missingPlug), "can-fail: a missing socket PlugTop is rejected");
                var wrong = new List<V2>(lead.Strands[0].Pts);
                wrong[atA ? 0 : wrong.Count - 1] = sp.LeadTip;
                var stolenLead = new LaidPiece { Decals = lead.Decals };
                stolenLead.Strands.Add(new CordStrand { Pts = wrong });
                Check(!DeviceSocketRule(stolenLead), "can-fail: a device strand ending at the captive lead point is rejected");
            }
        }
    }
}
