// RIMMANDRAKE_FIX_SLACK_CORD_ENDS_OWNER_CAUGHT_TWO (owner, live look at the automatic in-game visit 1, 2026-11-16 ~5:46 AM PST):
//   ends   "I just saw it connect a wire to a wall, and there was both a hanging out sparking end as well as the wire plugging into the
//          same point on the wall. That's not ok": every cord end is exactly ONE kind, a fitting (plug, outlet, wall plate, rock hole,
//          junction piece, strip) or a loose end (frayed, live or dead), never both at one point; a fitted end throws no sparks and
//          hangs no loose tail; and every end is one of the two (an end drawn as nothing is not a fix).
//   slope  "wires coming out of a junction box not honoring the "preserve the right slope" rule, so the junction box has stubby
//          connectors that don't line up" (the rule: owner 2026-11-09 8:10 AM, "Match position AND slope, and match the slope where your
//          adapter plug ENDS... that's the point that must agree", CordBuilder.SeatPlugTails): at every junction box arm and every power
//          switch stub a cord takes, the cord crosses the stub's tip on the stub's line (PosMax) heading along it (SlopeMaxDeg); a box arm
//          with no cord on it is not drawn. Kept on purpose (Allowed): the power switch's four stubs are its building art, drawn on and
//          off whatever is wired; the small box a device stub ends in has no one-port art (it is a 4-arm box at 0.6 scale).
// Scenes are generated, not only the oracle's seven: wall and rock entry from each side, corners, runs ending inside a wall with and
// without power, both pile looks, boxes of 2, 3 and 4 cords at varied approach angles, a switch with 1-4 cords, a device stub.
// The two readings live in ../Core/CordEndAudit.cs (the live probe "endkind:" runs the same). Each check carries a planted fault that
// must turn it red. Live row: northstar/scene_rows.py end_kind_and_slope (SC_cord_end_one_kind, SC_box_stub_slope).
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class CordEndKindChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "end-kind: " + msg);

        private static readonly Cell[] Dirs = { new Cell(0, 1), new Cell(1, 0), new Cell(0, -1), new Cell(-1, 0) };
        private static Cell Add(Cell a, Cell d, int k = 1) => new Cell(a.X + d.X * k, a.Z + d.Z * k);
        private static Cell Perp(Cell d) => new Cell(-d.Z, d.X);

        // ------------------------------------------------------------------ scenes
        /// <summary>A run from a battery that bends twice and goes into a wall (or rock) line across its way at (15,15), entered from
        /// the side <paramref name="d"/> points away from. <paramref name="terminal"/>: the run ENDS inside the wall cell; else it goes
        /// through and on to a lamp beyond. <paramref name="corner"/>: a second wall leg runs on from the entry cell, so the run enters
        /// a corner.</summary>
        internal static CordWorld WallScene(Cell d, bool terminal, bool corner, int lateral, BlockKind kind)
        {
            var w = new CordWorld(32, 32);
            Cell c = new Cell(15, 15), p = Perp(d);
            for (int t = corner ? 0 : -3; t <= 3; t++) w.SetBlocked(Add(c, p, t), kind);
            if (corner) for (int k = 1; k <= 3; k++) w.SetBlocked(Add(c, d, k), kind);
            var run = new List<Cell>();
            Cell s = Add(Add(c, d, -6), p, lateral);
            for (int k = 0; k <= 3; k++) run.Add(Add(s, d, k));
            Cell bend = Add(s, d, 3);
            int step = lateral > 0 ? -1 : 1;
            for (int t = 1; t <= Math.Abs(lateral); t++) run.Add(Add(bend, p, step * t));
            Cell b2 = Add(c, d, -3);
            for (int k = 1; k <= 3; k++) run.Add(Add(b2, d, k));
            if (!terminal) for (int k = 1; k <= 4; k++) run.Add(Add(c, d, k));
            foreach (Cell x in run) w.SetConduit(x);
            Cell bat = Add(s, d, -1);
            w.SetBlocked(bat, BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = bat.X, Z0 = bat.Z, Hookups = new List<Cell> { s } });
            if (!terminal)
            {
                Cell lamp = Add(c, d, 5);
                w.SetBlocked(lamp, BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "lamp", Kind = MachineKind.Consumer, X0 = lamp.X, Z0 = lamp.Z, Hookups = new List<Cell> { Add(c, d, 4) } });
            }
            return w;
        }

        /// <summary>A box at (15,15) with a run out along each of <paramref name="arms"/>: each goes 2-4 cells out, turns to one side
        /// for 1-3 cells (seeded) and ends at a battery or a lamp, so the cords come back at the box from varied angles.</summary>
        internal static CordWorld BoxScene(IList<Cell> arms, int seed, bool asSwitch)
        {
            var w = new CordWorld(34, 34);
            Cell c = new Cell(16, 16);
            var rng = new Random(seed);
            var hooks = new List<Cell>();
            int i = 0;
            foreach (Cell a in arms)
            {
                int out1 = 2 + rng.Next(3), side = rng.Next(4) - 1, lenSide = 1 + rng.Next(3);
                Cell cur = c;
                if (!asSwitch) w.SetConduit(c);
                for (int k = 1; k <= out1; k++) { cur = Add(c, a, k); w.SetConduit(cur); }
                hooks.Add(Add(c, a, 1));
                Cell sd = side < 0 ? Perp(a) : side > 0 ? new Cell(-Perp(a).X, -Perp(a).Z) : a;
                for (int k = 1; k <= lenSide; k++) { cur = Add(cur, sd, 1); w.SetConduit(cur); }
                Cell m = Add(cur, a, 1);
                w.SetBlocked(m, BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "m" + i, Kind = i == 0 ? MachineKind.Battery : MachineKind.Consumer, X0 = m.X, Z0 = m.Z, Hookups = new List<Cell> { cur } });
                i++;
            }
            if (asSwitch)
            {
                w.SetBlocked(c, BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "switch", Kind = MachineKind.Transmitter, X0 = c.X, Z0 = c.Z, Hookups = hooks, SidePorts = true });
            }
            return w;
        }

        /// <summary>A run that ends under an impassable building that is no machine (the device stub's little box).</summary>
        internal static CordWorld DeviceStubScene()
        {
            var w = new CordWorld(24, 24);
            for (int x = 4; x <= 12; x++) w.SetConduit(new Cell(x, 10));
            w.SetBlocked(new Cell(12, 10), BlockKind.Device);
            w.SetBlocked(new Cell(3, 10), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = 3, Z0 = 10, Hookups = new List<Cell> { new Cell(4, 10) } });
            return w;
        }

        // ------------------------------------------------------------------ run
        private static List<LaidPiece> Build(CordWorld w, PileArt pile, ulong seed, Func<Cell, bool> live, out CordGraph g)
        {
            var b = new CordBuilder();
            List<LaidPiece> ps = b.Build(w, new BuildOptions { Pile = pile, Seed = seed }, c => live(c));
            g = b.Graph;
            return ps;
        }

        public static void Run(List<System.Text.Json.JsonElement> oracle = null)
        {
            // ---- ends: wall and rock entry from each side, corners, runs ending in a wall with and without power, both looks
            int scenes = 0, ends = 0, wallTerminals = 0;
            var all = new CordEndAudit.EndRead();
            var bad = new List<string>();
            List<LaidPiece> plantOn = null; CordGraph plantG = null;
            foreach (Cell d in Dirs)
                foreach (bool terminal in new[] { true, false })
                    foreach (bool corner in new[] { false, true })
                        foreach (bool live in new[] { true, false })
                            foreach (PileArt pile in new[] { PileArt.Junctions, PileArt.Strips })
                                foreach (int lateral in new[] { -2, 1 })
                                    foreach (BlockKind kind in new[] { BlockKind.Wall, BlockKind.Rock })
                                    {
                                        if (kind == BlockKind.Rock && (corner || pile == PileArt.Strips)) continue;
                                        CordWorld w = WallScene(d, terminal, corner, lateral, kind);
                                        string name = $"wall[{d} {(terminal ? "ends-in" : "through")}{(corner ? " corner" : "")} {(live ? "live" : "dead")} {pile} lat{lateral} {kind}]";
                                        List<LaidPiece> ps = Build(w, pile, (ulong)(7 + scenes), _ => live, out CordGraph g);
                                        CordEndAudit.EndRead r = CordEndAudit.Ends(g, ps, name);
                                        scenes++; ends += r.Ends;
                                        wallTerminals += g.Nodes.Values.Count(n => n.WallTerminal);
                                        all.Both += r.Both; all.None += r.None; all.FitSparks += r.FitSparks; all.TerminalsFitted += r.TerminalsFitted;
                                        all.WallTerminalsLoose += r.WallTerminalsLoose; all.StubsLoose += r.StubsLoose; all.FitTails += r.FitTails;
                                        bad.AddRange(r.Bad);
                                        if (plantOn == null && !terminal && pile == PileArt.Junctions && kind == BlockKind.Wall) { plantOn = ps; plantG = g; }
                                    }
            if (oracle != null)
                foreach (System.Text.Json.JsonElement s in oracle)
                {
                    System.Text.Json.JsonElement sc = s.GetProperty("scene");
                    CordWorld w = Program.World(sc);
                    HashSet<Cell> lv = Program.Live(w, sc);
                    List<LaidPiece> ps = Build(w, PileArt.Junctions, 1, lv.Contains, out CordGraph g);
                    CordEndAudit.EndRead r = CordEndAudit.Ends(g, ps, "oracle " + sc.GetProperty("name").GetString());
                    scenes++; ends += r.Ends;
                    all.Both += r.Both; all.None += r.None; all.FitSparks += r.FitSparks; all.TerminalsFitted += r.TerminalsFitted;
                    all.WallTerminalsLoose += r.WallTerminalsLoose; all.StubsLoose += r.StubsLoose; all.FitTails += r.FitTails;
                    bad.AddRange(r.Bad);
                }
            Check(scenes >= 100 && ends >= scenes + scenes / 2 && wallTerminals > 0 && all.Both == 0 && all.FitSparks == 0,
                  $"ends: {ends} ends over {scenes} scenes ({wallTerminals} runs ending inside a wall); {all.Both} drawn as BOTH a fitting and a loose end, {all.FitSparks} fitted ends throwing sparks" +
                  (bad.Count > 0 ? " | " + string.Join("; ", bad.Take(4)) : ""));
            Check(all.None == 0 && all.TerminalsFitted == 0 && all.WallTerminalsLoose == 0 && all.StubsLoose == 0,
                  $"ends: every end is one kind: {all.None} drawn as nothing, {all.TerminalsFitted} conduit ends with a fitting, {all.WallTerminalsLoose} runs ending in a wall or rock drawn loose or sparking, {all.StubsLoose} through-wall entries fraying");
            // can fail: a fray planted on a wall plate (the owner's 2026-11-16 picture) and a spark end planted on it
            if (plantOn != null)
            {
                CordNode st = plantG.Nodes.Values.First(n => n.Type == NodeType.StubWall && !n.WallTerminal);
                var planted = plantOn.Select(p => new LaidPiece { Key = p.Key, Strands = p.Strands, Decals = new List<CordDecal>(p.Decals), Ends = new List<CordEnd>(p.Ends) }).ToList();
                LaidPiece host = planted.First(p => p.Decals.Any(d => d.Kind == DecalKind.StubWall && V2.Dist(d.Pos, st.Face) < CordEndAudit.EndRadius));
                host.Decals.Add(new CordDecal(DecalKind.FrayLive, st.Face - st.Into * 0.3, 0, 0.5));
                host.Ends.Add(new CordEnd { Tip = st.Face - st.Into * 0.3, Dir = -st.Into, NetCell = st.Cell, Wall = true });
                CordEndAudit.EndRead pr = CordEndAudit.Ends(plantG, planted, "planted");
                Check(pr.Both >= 1 && pr.FitSparks >= 1, $"can fail: a loose sparking end planted on a wall plate is caught (both {pr.Both}, sparks {pr.FitSparks})");
            }
            else Check(false, "can fail: no through-wall scene to plant on");

            // ---- slope: boxes of 2, 3 and 4 cords at varied approach angles, switches with 1-4 cords, a device stub
            var sAll = new CordEndAudit.SlopeRead();
            var sBad = new List<string>();
            int boxes = 0, switches = 0, bends = 0, bendBoxes = 0;
            var sets = new List<Cell[]>
            {
                new[] { Dirs[0], Dirs[1], Dirs[2], Dirs[3] },
                new[] { Dirs[1], Dirs[2], Dirs[3] }, new[] { Dirs[0], Dirs[2], Dirs[3] }, new[] { Dirs[0], Dirs[1], Dirs[3] }, new[] { Dirs[0], Dirs[1], Dirs[2] },
                new[] { Dirs[0], Dirs[1] }, new[] { Dirs[1], Dirs[3] },
            };
            void Take(CordEndAudit.SlopeRead r)
            {
                sAll.Arms += r.Arms; sAll.Taken += r.Taken; sAll.Empty += r.Empty; sAll.EmptyAllowed += r.EmptyAllowed;
                sAll.OffLine += r.OffLine; sAll.OffSlope += r.OffSlope; sAll.Short += r.Short;
                sAll.WorstDeg = Math.Max(sAll.WorstDeg, r.WorstDeg); sAll.WorstPos = Math.Max(sAll.WorstPos, r.WorstPos);
                sBad.AddRange(r.Bad);
            }
            List<LaidPiece> plantBox = null; CordWorld plantBoxW = null; CordGraph plantBoxG = null;
            foreach (Cell[] set in sets)
                for (int seed = 1; seed <= 6; seed++)
                {
                    CordWorld w = BoxScene(set, seed * 31 + set.Length, false);
                    List<LaidPiece> ps = Build(w, PileArt.Junctions, (ulong)seed, _ => true, out CordGraph g);
                    List<CordEndAudit.Fitted> cs = CordEndAudit.Connectors(w, g, ps);
                    if (set.Length == 2) { bends++; bendBoxes += cs.Count(x => V2.Dist(x.M, new V2(16.5, 16.5)) < 0.3); }
                    else boxes += cs.Count;
                    Take(CordEndAudit.Slopes(w, g, ps, $"box[{set.Length} cords seed {seed}]"));
                    if (plantBox == null && set.Length == 4) { plantBox = ps; plantBoxW = w; plantBoxG = g; }
                    CordWorld sw = BoxScene(set, seed * 17 + set.Length, true);
                    List<LaidPiece> sps = Build(sw, PileArt.Junctions, (ulong)seed, _ => true, out CordGraph sg);
                    switches++;
                    Take(CordEndAudit.Slopes(sw, sg, sps, $"switch[{set.Length} cords seed {seed}]"));
                }
            for (int seed = 1; seed <= 4; seed++)
            {
                CordWorld one = BoxScene(new[] { Dirs[seed - 1] }, seed, true);
                List<LaidPiece> ops = Build(one, PileArt.Junctions, (ulong)seed, _ => true, out CordGraph og);
                switches++;
                Take(CordEndAudit.Slopes(one, og, ops, $"switch[1 cord {Dirs[seed - 1]}]"));
            }
            {
                CordWorld dv = DeviceStubScene();
                List<LaidPiece> dps = Build(dv, PileArt.Junctions, 1, _ => true, out CordGraph dg);
                Take(CordEndAudit.Slopes(dv, dg, dps, "device stub"));
            }
            if (Environment.GetEnvironmentVariable("GSS_ENDKIND_ALL") == "1")
            {
                foreach (string x in bad) Console.WriteLine("  end-kind refused: " + x);
                foreach (string x in sBad) Console.WriteLine("  slope refused: " + x);
                Console.WriteLine($"  slope: {bends} bend scenes drew {bendBoxes} boxes");
            }
            Check(boxes >= 30 && switches >= 40 && sAll.Taken >= 150 && sAll.OffLine == 0 && sAll.OffSlope == 0 && sAll.Short == 0,
                  $"slope: {sAll.Taken} cords at {boxes} boxes and {switches} switches leave the stub's tip on its line and slope (<= {CordEndAudit.PosMax} cells, <= {CordEndAudit.SlopeMaxDeg} deg): " +
                  $"{sAll.OffLine} off the line, {sAll.OffSlope} off the slope, {sAll.Short} short of the tip; worst {sAll.WorstDeg:0} deg, {sAll.WorstPos:0.00} cells" +
                  (sBad.Count > 0 ? " | " + string.Join("; ", sBad.Where(x => !x.Contains("no cord")).Take(4)) : ""));
            Check(sAll.Empty == 0 && bendBoxes == 0,
                  $"slope: no box arm drawn without its cord: {sAll.Empty} empty arms ({sAll.EmptyAllowed} kept as art: switch stubs, device-stub box); {bendBoxes} boxes on {bends} 2-way bends" +
                  (sAll.Empty > 0 ? " | " + string.Join("; ", sBad.Where(x => x.Contains("no cord")).Take(3)) : ""));
            // can fail: one cord of a 4-way box turned 40 degrees just past the tip (the 2026-11-16 switch) is caught; an arm with its cord taken away reads empty
            if (plantBox != null)
            {
                CordEndAudit.Fitted f = CordEndAudit.Connectors(plantBoxW, plantBoxG, plantBox).First(x => x.Name.StartsWith("box"));
                var kinked = new List<LaidPiece>();
                bool done = false;
                foreach (LaidPiece p in plantBox)
                {
                    var q = new LaidPiece { Key = p.Key, Decals = p.Decals, Ends = p.Ends };
                    foreach (CordStrand s in p.Strands)
                    {
                        if (done || s.Pts == null || s.Pts.Count < 2 || V2.Dist(s.Pts[0], f.M) > f.Tip + 0.25) { q.Strands.Add(s); continue; }
                        V2 x = s.Pts[0];
                        var pts = new List<V2> { x };
                        V2 u = (s.Pts[Math.Min(3, s.Pts.Count - 1)] - x).Norm();
                        V2 k = CordEndAudit.Rot(u, 40 * Math.PI / 180);
                        for (int i = 1; i <= 20; i++) pts.Add(f.M + (x - f.M).Norm() * f.Tip * 0.9 + k * (0.04 * i));
                        q.Strands.Add(s.With(pts));
                        done = true;
                    }
                    kinked.Add(q);
                }
                CordEndAudit.SlopeRead kr = CordEndAudit.Slopes(plantBoxW, plantBoxG, kinked, "planted kink");
                bool cut = false;
                bool Near(V2 q) => V2.Dist(q, f.M) <= f.Tip + 0.25;
                var stripped = plantBox.Select(p =>
                {
                    bool here = !cut && p.Strands.Any(s => s.Pts != null && s.Pts.Count > 1 && (Near(s.Pts[0]) || Near(s.Pts[s.Pts.Count - 1])));
                    if (here) cut = true;
                    return new LaidPiece { Key = p.Key, Decals = p.Decals, Ends = p.Ends,
                        Strands = here ? p.Strands.Where(s => s.Pts == null || s.Pts.Count < 2 || !(Near(s.Pts[0]) || Near(s.Pts[s.Pts.Count - 1]))).ToList() : p.Strands };
                }).ToList();
                CordEndAudit.SlopeRead er = CordEndAudit.Slopes(plantBoxW, plantBoxG, stripped, "planted empty");
                Check(done && kr.OffSlope + kr.OffLine >= 1 && er.Empty >= 1, $"can fail: a cord kinked 40 deg at a box's tip is caught ({kr.OffSlope + kr.OffLine}), an arm stripped of its cord reads empty ({er.Empty})");
            }
            else Check(false, "can fail: no 4-way box to plant on");
        }
    }
}
