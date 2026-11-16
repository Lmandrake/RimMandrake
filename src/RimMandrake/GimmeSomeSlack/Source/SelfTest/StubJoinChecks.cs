// RIMMANDRAKE_BIND_SLACK_STUB_ANGLE_RULE_FOURTH_ASK (owner 2026-11-16): the position-and-slope rule as an acceptance check, swept over every
// stubbed piece x look x rotation x arriving cord direction, the whipping live end over its frames, and a conduit dead-ending inside a wall
// or rock (his station 12). One instrument (Core/StubJoinAudit.cs) judges these scenes and the live game (probe "joins:").
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class StubJoinChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "stub joins: " + msg);

        private static readonly Cell[] Dirs = { new Cell(0, 1), new Cell(1, 0), new Cell(0, -1), new Cell(-1, 0) };
        internal static readonly string[] Looks = { "Modern", "Industrial", "Futuristic", "Scrapper" };

        private static BuildOptions Opt(string look, ulong seed) =>
            new BuildOptions { Pile = look == "Modern" ? PileArt.Strips : PileArt.Junctions, Seed = seed, PlugBoot = CordBuilder.PlugBootU(look) };

        private static List<LaidPiece> Build(CordWorld w, BuildOptions opt, Func<Cell, bool> live, out CordGraph g)
        {
            var b = new CordBuilder();
            List<LaidPiece> ps = b.Build(w, opt, c => live(c));
            g = b.Graph;
            return ps;
        }

        /// <summary>His station 12: a junction box whose north branch turns east and ENDS inside the wall cell, its south branch running on
        /// through the wall to a lamp; a battery feeds it from the west.</summary>
        internal static CordWorld Station12(BlockKind kind)
        {
            var w = new CordWorld(30, 30);
            for (int z = 10; z <= 22; z++) w.SetBlocked(new Cell(17, z), kind);
            foreach (Cell c in new[] { new Cell(12, 16), new Cell(13, 16), new Cell(14, 16), new Cell(14, 17), new Cell(14, 18), new Cell(15, 18), new Cell(16, 18),
                                       new Cell(17, 18), new Cell(14, 15), new Cell(14, 14), new Cell(15, 14), new Cell(16, 14), new Cell(17, 14), new Cell(18, 14), new Cell(19, 14) })
                w.SetConduit(c);
            w.SetBlocked(new Cell(11, 16), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = 11, Z0 = 16, Hookups = new List<Cell> { new Cell(12, 16) } });
            w.SetBlocked(new Cell(20, 14), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "lamp", Kind = MachineKind.Consumer, X0 = 20, Z0 = 14, Hookups = new List<Cell> { new Cell(19, 14) } });
            return w;
        }

        /// <summary>His station 25 and its kin: a box fed from the west, a lamp east, and a short stub run of <paramref name="len"/> cells off
        /// its <paramref name="d"/> side that ends on open floor (a live end below the box); <paramref name="bend"/> turns that run once.</summary>
        internal static CordWorld LiveStubScene(Cell d, int len, bool bend)
        {
            var w = new CordWorld(32, 32);
            Cell c = new Cell(16, 16);
            for (int x = 11; x <= 21; x++) w.SetConduit(new Cell(x, 16));
            w.SetBlocked(new Cell(10, 16), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = 10, Z0 = 16, Hookups = new List<Cell> { new Cell(11, 16) } });
            w.SetBlocked(new Cell(22, 16), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "lamp", Kind = MachineKind.Consumer, X0 = 22, Z0 = 16, Hookups = new List<Cell> { new Cell(21, 16) } });
            Cell cur = c;
            for (int k = 1; k <= len; k++) { cur = new Cell(c.X + d.X * k, c.Z + d.Z * k); w.SetConduit(cur); }
            if (bend) { cur = new Cell(cur.X + 1, cur.Z); w.SetConduit(cur); cur = new Cell(cur.X + 1, cur.Z); w.SetConduit(cur); }
            return w;
        }

        public static void Run()
        {
            var all = new StubJoins.JoinRead();
            var ends = new CordEndAudit.EndRead();
            var live = new StubJoins.LiveRead();
            int scenes = 0, wallDeadEnds = 0;
            List<LaidPiece> plantPs = null; CordWorld plantW = null; BuildOptions plantOpt = null;
            void Take(CordWorld w, BuildOptions opt, string name, Func<Cell, bool> lv)
            {
                List<LaidPiece> ps = Build(w, opt, lv, out CordGraph g);
                scenes++;
                StubJoins.JoinRead r = StubJoins.Joins(w, ps, opt, name);
                all.Add(r);
                CordEndAudit.EndRead e = CordEndAudit.Ends(g, ps, name);
                ends.Both += e.Both; ends.FitSparks += e.FitSparks; ends.None += e.None; ends.WallTerminalsLoose += e.WallTerminalsLoose; ends.Bad.AddRange(e.Bad);
                wallDeadEnds += g.Nodes.Values.Count(n => n.WallTerminal);
                live.Add(StubJoins.LiveEnds(ps, name));
                if (plantPs == null && name.StartsWith("Industrial box4", StringComparison.Ordinal)) { plantPs = ps; plantW = w; plantOpt = opt; }
            }
            foreach (string look in Looks)
            {
                // boxes and switches: every arm set (4-way, each 3-way rotation; switches 1-4 cords), cords coming back from varied bends
                var sets = new List<Cell[]> { Dirs };
                for (int k = 0; k < 4; k++) sets.Add(Dirs.Where((_, i) => i != k).ToArray());
                var switchSets = new List<Cell[]>(sets);
                for (int k = 0; k < 4; k++) { switchSets.Add(new[] { Dirs[k] }); switchSets.Add(new[] { Dirs[k], Dirs[(k + 1) % 4] }); switchSets.Add(new[] { Dirs[k], Dirs[(k + 2) % 4] }); }
                for (int seed = 0; seed < 3; seed++)
                {
                    foreach (Cell[] arms in sets)
                        Take(CordEndKindChecks.BoxScene(arms, 100 + seed * 7 + arms.Length, false), Opt(look, (ulong)(11 + seed)), $"{look} box{arms.Length} s{seed} [{string.Join(" ", arms)}]", _ => true);
                    foreach (Cell[] arms in switchSets)
                        Take(CordEndKindChecks.BoxScene(arms, 200 + seed * 7 + arms.Length, true), Opt(look, (ulong)(21 + seed)), $"{look} switch{arms.Length} s{seed} [{string.Join(" ", arms)}]", _ => true);
                }
                // wall plates, rock holes, outlets and wall plugs: each face, through and dead-ending, corners, two arrival sides
                foreach (Cell d in Dirs)
                    foreach (bool terminal in new[] { false, true })
                        foreach (bool corner in new[] { false, true })
                            foreach (int lateral in new[] { -2, 1 })
                                foreach (BlockKind kind in new[] { BlockKind.Wall, BlockKind.Rock })
                                {
                                    if (kind == BlockKind.Rock && corner) continue;
                                    Take(CordEndKindChecks.WallScene(d, terminal, corner, lateral, kind), Opt(look, (ulong)(31 + scenes)),
                                         $"{look} wall[{d} {(terminal ? "ends-in" : "through")}{(corner ? " corner" : "")} lat{lateral} {kind}]", _ => true);
                                }
                Take(CordEndKindChecks.DeviceStubScene(), Opt(look, 41), $"{look} device stub", _ => true);
                foreach (BlockKind kind in new[] { BlockKind.Wall, BlockKind.Rock })
                    foreach (bool lv in new[] { true, false })
                        Take(Station12(kind), Opt(look, 51), $"{look} station12 {kind} {(lv ? "live" : "dead")}", _ => lv);
                foreach (Cell d in new[] { new Cell(0, -1), new Cell(0, 1) })
                    foreach (int len in new[] { 1, 2, 3 })
                        foreach (bool bend in new[] { false, true })
                            Take(LiveStubScene(d, len, bend), Opt(look, (ulong)(61 + len)), $"{look} live stub {d} len{len}{(bend ? " bend" : "")}", _ => true);
            }

            string[] kinds = { "box X", "box T", "switch", "plug", "strip plug", "strip lead", "wall plate", "rock hole", "wall plug" };
            string[] missing = kinds.Where(k => !all.ByKind.TryGetValue(k, out int[] a) || a[1] == 0).ToArray();
            Console.WriteLine($"  stub joins: {scenes} scenes; {all.Summary()}");
            Console.WriteLine($"  stub joins: live ends {live.Tails} tails x frames {live.Frames}: {live.OffSlope} turn at the join, {live.Pinched} pinched, {live.Jumped} jump; worst {live.WorstDeg:0} deg, min radius {(live.Tails > 0 ? live.MinR : 0):0.000}");
            foreach (var grp in all.Bad.GroupBy(x => kinds.Concat(new[] { "wall outlet" }).OrderByDescending(k => k.Length).FirstOrDefault(k => x.Contains(" " + k + "@")) ?? "?"))
                foreach (string x in grp.Take(3)) Console.WriteLine("  stub joins refused: " + x);
            if (Environment.GetEnvironmentVariable("GSS_JOINS_DEBUG") == "1")
                foreach (string look in new[] { "Modern", "Industrial" })
                {
                    CordWorld cw = LiveStubScene(new Cell(0, -1), 3, false);
                    List<LaidPiece> cps = Build(cw, Opt(look, 64), _ => true, out _);
                    foreach (LaidPiece p in cps)
                        foreach (CordStrand s in p.Strands.Where(x => x.WhipA > 0 || x.WhipB > 0))
                        {
                            var pts = (s.WhipA > 0 ? s.Pts : Enumerable.Reverse(s.Pts)).Select(q => $"({q.X:0.00},{q.Z:0.00})");
                            Console.WriteLine($"  DEBUG {look} {p.EndA}|{p.EndB} whip {s.WhipA}/{s.WhipB} of {s.Pts.Count} lay {s.Lay}: " + string.Join(" ", pts));
                        }
                }
            {
                CordWorld dw = CordEndKindChecks.DeviceStubScene();
                List<LaidPiece> dps = Build(dw, Opt("Industrial", 41), _ => true, out CordGraph dg);
                Console.WriteLine("  stub joins: device stub scene nodes " + string.Join(" ", dg.Nodes.Values.Select(n => $"{n.Type}@{n.Cell}")) + " | decals " + string.Join(" ", dps.SelectMany(p => p.Decals).Select(d => $"{d.Kind}/{d.Scale:0.00}")));
            }
            foreach (string b in live.Bad.Take(6)) Console.WriteLine("  live end refused: " + b);
            foreach (string b in ends.Bad.Where(x => x.Contains("inside the wall or rock")).Take(4)) Console.WriteLine("  dead end refused: " + b);

            Check(missing.Length == 0, $"coverage: every stubbed piece is met by a cord in the sweep (missing: {string.Join(", ", missing)})");
            Check(all.Taken >= 500 && all.OffLine == 0 && all.OffSlope == 0,
                  $"position AND slope: {all.Taken} cords at stubs over {scenes} scenes, {all.OffLine} off the stub's line, {all.OffSlope} off its slope (worst {all.WorstPos:0.00} cell, {all.WorstDeg:0} deg)");
            Check(all.Empty == 0, $"no bare stub: {all.Empty} stubs drawn with no cord while their piece has one");
            Check(live.Tails >= 20 && live.OffSlope == 0 && live.Pinched == 0 && live.Jumped == 0,
                  $"live end continues its cord: {live.Tails} tails, {live.OffSlope} turning at the join, {live.Pinched} pinched under radius {StubJoins.MinBendR}, {live.Jumped} leaving the cord");
            Check(wallDeadEnds >= 40 && ends.WallTerminalsLoose == 0 && ends.None == 0,
                  $"wall and rock dead ends: {wallDeadEnds} runs ending inside a wall or rock, {ends.WallTerminalsLoose} drawn with a loose or sparking end, {ends.None} drawn as nothing");

            // ---- the guard can fail: a cord kinked 40 deg at a plug's boot, a box arm stripped of its cord, a pinched live tail
            if (plantPs != null)
            {
                List<LaidPiece> Copy() => plantPs.Select(p => new LaidPiece { Key = p.Key, EndA = p.EndA, EndB = p.EndB, Owner = p.Owner, Decals = new List<CordDecal>(p.Decals), Ends = new List<CordEnd>(p.Ends),
                    Strands = p.Strands.Select(s => new CordStrand { Pts = new List<V2>(s.Pts), WhipA = s.WhipA, WhipB = s.WhipB, OverFace = s.OverFace, Lifted = s.Lifted }).ToList() }).ToList();
                StubJoins.JoinRead clean = StubJoins.Joins(plantW, plantPs, plantOpt, "plant control");
                // kink: rotate the far side of every strand about the point nearest a plug's boot by 40 deg
                List<LaidPiece> kinked = Copy();
                List<StubArt.Stub> plugs = StubArt.Of(plantW, kinked, plantOpt).Where(s => s.Kind == "plug").ToList();
                int bent = 0;
                foreach (LaidPiece p in kinked)
                    foreach (CordStrand s in p.Strands)
                        foreach (StubArt.Stub st in plugs)
                        {
                            int i = Enumerable.Range(0, s.Pts.Count).OrderBy(k => V2.Dist(s.Pts[k], st.T)).First();
                            if (V2.Dist(s.Pts[i], st.T) > 0.05) continue;
                            bool tailIsStart = i > s.Pts.Count / 2;
                            V2 pv = s.Pts[i];
                            for (int k = 0; k < s.Pts.Count; k++)
                                if (tailIsStart ? k < i : k > i) s.Pts[k] = pv + CordEndAudit.Rot(s.Pts[k] - pv, 40 * Math.PI / 180);
                            bent++;
                        }
                StubJoins.JoinRead kr = StubJoins.Joins(plantW, kinked, plantOpt, "planted kink");
                // bare arm: drop every strand that ends at a box's centre
                List<LaidPiece> stripped = Copy();
                List<StubArt.Stub> arms = StubArt.Of(plantW, stripped, plantOpt).Where(s => s.Kind == "box X").ToList();
                StubArt.Stub arm0 = arms.FirstOrDefault();
                CordStrand cut = arm0 == null ? null : stripped.SelectMany(p => p.Strands).FirstOrDefault(s => s.Pts.Any(q => V2.Dist(q, arm0.T) < CordEndAudit.PosMax));
                LaidPiece host = cut == null ? null : stripped.First(p => p.Strands.Contains(cut));
                host?.Strands.Remove(cut);
                StubJoins.JoinRead er = StubJoins.Joins(plantW, stripped, plantOpt, "planted bare arm");
                // pinch: a live tail grafted on at a right angle
                var hair = new List<LaidPiece> { new LaidPiece { Key = "pinch", Decals = new List<CordDecal>(), Ends = new List<CordEnd>(), Strands = new List<CordStrand> {
                    new CordStrand { Pts = Enumerable.Range(0, 30).Select(k => new V2(k * 0.04, 0)).Concat(Enumerable.Range(1, 24).Select(k => new V2(1.16, k * 0.04))).ToList(), WhipB = 24 } } } };
                StubJoins.LiveRead pr = StubJoins.LiveEnds(hair, "planted pinch");
                Check(bent >= 1 && kr.OffSlope + kr.OffLine > clean.OffSlope + clean.OffLine && host != null && er.Empty > clean.Empty && pr.Pinched >= 1,
                      $"can fail: {bent} cords kinked 40 deg at a plug boot are caught ({clean.OffSlope + clean.OffLine} -> {kr.OffSlope + kr.OffLine}), a box arm stripped of its cord is caught ({clean.Empty} -> {er.Empty}), a tail grafted at a right angle is caught (pinch {pr.Pinched})");
            }
            else Check(false, "can fail: no scene with a plug and a + box to plant on");
        }
    }
}
