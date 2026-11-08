// The owner's live sitting of 2026-11-08 (12:20 PM): "The modern cable is a bit of a mess. Interestingly, the industrial and scrapper look
// much better and bend appropriately. ... Items should connect to the bottom of a power pole (beneath its base), not run a line up to the
// top of the power pole. ... The massive tangle shown for the grid is indeed a bit excessive. I did want a tangled rats-nest of wires, but
// that's overkill. The top of power poles shows needless kinks in the wires where they connect too."
// Each row was written failing on the code he saw, on the colony worlds the live probe dumped that sitting (sitting_ba_*.json).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class SittingChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "sitting-20261108: " + msg);

        private static readonly DecalKind[] Connectors = { DecalKind.JunctionTin, DecalKind.JunctionTape, DecalKind.PowerStrip, DecalKind.PowerStripDark };

        internal static void Run()
        {
            Lay("Modern", out CordWorld wm, out List<LaidPiece> modern);
            Lay("Scrapper", out CordWorld ws, out List<LaidPiece> scrapper);
            if (modern == null || scrapper == null) { Check(false, "the sitting's worlds (sitting_ba_Modern/Scrapper.json) beside the self-test"); return; }

            // WHY Modern was worse: every socket of a strip faced one side, so a cord from behind or off the free end swung round the strip and
            // hooked into its plug ("<" hooks, plugs facing away from their cords: 13 of 39 socket ends turned past 100 degrees in the last 1.2 cells)
            List<double> turns = SocketTurns(modern);
            Check(turns.Count >= 20, $"the Modern colony plugs at least 20 strip sockets (instrument sees them: {turns.Count})");
            // the "<" is a hairpin: past 150 degrees (9 of 39 on the sitting's code). A cord from behind the strip cannot do with less than about 100
            // (it must come round to a plug standing out on the sockets' side, CordAudit.StripFits), so the 100-degree count is reported, not barred
            int hooked = turns.Count(t => t > 150), wrapped = turns.Count(t => t > 100);
            Check(hooked <= 2, $"Modern: a strip socket's cord hairpins (past 150 degrees in its last 1.2 cells) at most twice (was 9 of 39): {hooked} of {turns.Count}; past 100: {wrapped} (was 13)");
            var bm = new CordShapeAudit.BendTally();
            foreach (LaidPiece p in modern) foreach (CordStrand s in p.Strands) bm.Add(wm, p, s);
            int sock = bm.ByWhy.TryGetValue("socket", out int k) ? k : 0;
            // a ratchet, not the goal: the plug lean took the hairpins (9 to 2) but each cord from behind still turns a Gamma corner at the plug
            // tail (105-139 degrees) the audit excuses as 'socket', and a lamp sharing its cell with a wall stub loops round (157,113 and 163,113).
            // Goal 3 (Scrapper 1); lesson 20261108T211040Z-BENCH-gss-strip-back-arm-geometric-turn, open as a design question to the owner
            Check(sock <= 8, $"Modern: bends excused as 'socket' no more than the plug lean leaves (8; was 9, goal 3, Scrapper 1): {sock}");

            // the grid's heap: "a tangled rats-nest of wires, but that's overkill" (Modern 14 cables and 7 strips, the junction looks 22-23 and 13 boxes)
            foreach ((string look, List<LaidPiece> ps) in new[] { ("Modern", modern), ("Scrapper", scrapper) })
            {
                List<LaidPiece> heaps = ps.Where(p => p.EndA == null && (p.Key ?? "").StartsWith("tangle:", StringComparison.Ordinal)).ToList();
                Check(heaps.Count >= 1, $"{look}: the colony has its grid heap (instrument sees it: {heaps.Count})");
                foreach (LaidPiece h in heaps)
                {
                    int strands = h.Strands.Count, cons = h.Decals.Count(d => Connectors.Contains(d.Kind));
                    Console.WriteLine($"  heap {look} {h.Key}: {strands} cables, {cons} connectors");
                    Check(strands <= 10 && cons <= 6 && strands >= 3 && cons >= 1,
                          $"{look} {h.Key}: a rats-nest, not overkill: 3..10 cables and 1..6 connectors, got {strands} cables, {cons} connectors");
                }
            }

            // pole tops: "needless kinks in the wires where they connect" are the drip loops at each insulator
            Check(!AerialMath.DripLoopsDefault, "drip loops at the insulators are off by default (they kinked every wire at a pole top)");

            FootDrop();
            MastFoot();
        }

        private static void Lay(string look, out CordWorld w, out List<LaidPiece> ps)
        {
            w = null; ps = null;
            string path = Path.Combine(AppContext.BaseDirectory, "sitting_ba_" + look + ".json");
            if (!File.Exists(path)) return;
            using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(path));
            w = LabWorld.Read(doc.RootElement, out BuildOptions opt, out HashSet<Cell> live);
            ps = new CordBuilder().Build(w, opt, c => live.Contains(c));
        }

        /// <summary>Each strip-socket plug (a Plug decal at the pile plug scale on a laid cord, not a heap's own): the cord's total turn over the
        /// last 1.2 cells into it, in degrees (gss_sitting/tools/strip_ends.py, the instrument that found the hooks).</summary>
        private static List<double> SocketTurns(List<LaidPiece> ps)
        {
            var o = new List<double>();
            foreach (LaidPiece p in ps)
            {
                if ((p.EndA ?? p.Key ?? "").StartsWith("tangle", StringComparison.Ordinal)) continue;
                foreach (CordDecal d in p.Decals.Where(d => d.Kind == DecalKind.Plug && Math.Abs(d.Scale - CordBuilder.PilePlugScale) < 1e-3))
                {
                    List<V2> best = null;
                    double bd = double.MaxValue;
                    foreach (CordStrand s in p.Strands)
                    {
                        if (s.Pts == null || s.Pts.Count < 3) continue;
                        foreach (bool atEnd in new[] { false, true })
                        {
                            V2 t = atEnd ? s.Pts[s.Pts.Count - 1] : s.Pts[0];
                            double dd = V2.Dist(t, d.Pos);
                            if (dd < bd) { bd = dd; best = atEnd ? s.Pts : Enumerable.Reverse(s.Pts).ToList(); }
                        }
                    }
                    if (best == null) continue;
                    double acc = 0, tot = 0, prev = double.NaN;
                    for (int i = best.Count - 1; i > 0 && acc < 1.2; i--)
                    {
                        double a = Math.Atan2(best[i].Z - best[i - 1].Z, best[i].X - best[i - 1].X);
                        if (!double.IsNaN(prev)) { double da = a - prev; while (da > Math.PI) da -= 2 * Math.PI; while (da < -Math.PI) da += 2 * Math.PI; tot += da; }
                        prev = a;
                        acc += V2.Dist(best[i], best[i - 1]);
                    }
                    o.Add(Math.Abs(tot) * 180 / Math.PI);
                }
            }
            return o;
        }

        /// <summary>A device's lead to a pole or mast starts on the ground at the pole's foot (121837, 121857: it hung from the crossarm).</summary>
        private static void FootDrop()
        {
            var basePt = new P2(20.5, 20.5);
            int n = 0, footed = 0, low = 0, reached = 0;
            foreach (P2 dev in new[] { new P2(24.5, 20.5), new P2(16.5, 22.5), new P2(20.5, 16.5), new P2(23.5, 24.5), new P2(21.2, 20.9) })
                for (int seed = 0; seed < 6; seed++)
                {
                    FallenLay l = AerialMath.LayFootDrop(basePt, dev, 1000 + 37 * seed, (x, z) => true);
                    n++;
                    if (l == null || l.Pts.Count < 2) continue;
                    if (P2.Dist(l.Pts[0], basePt) < 0.05 && l.GroundFrom == 0) footed++;
                    if (l.Pts.All(q => q.Z <= Math.Max(basePt.Z, dev.Z) + 0.6)) low++;
                    if (P2.Dist(l.Pts[l.Pts.Count - 1], dev) < 0.05) reached++;
                }
            Check(footed == n, $"a pole's lead to a device starts at the pole's foot, on the ground: {footed} of {n}");
            Check(low == n, $"a pole's lead never climbs toward the crossarm: {low} of {n}");
            Check(reached == n, $"a pole's lead ends at its device: {reached} of {n}");
            FallenLay walled = AerialMath.LayFootDrop(basePt, new P2(24.5, 20.5), 7, (x, z) => x != 22);
            Check(walled != null && P2.Dist(walled.Pts[0], basePt) < 0.05 && walled.GroundFrom == 0, "with a wall between, the lead still lies from the foot (under the wall)");
        }

        /// <summary>A floor cord to a mast (a Transmitter with Foot) from a run beside it ends under its foot, not at the cell's side (121837:
        /// a Futuristic cord into the mast's side box, mid-height).</summary>
        private static void MastFoot()
        {
            int bad = 0, n = 0;
            var seen = new List<string>();
            foreach (int side in new[] { -1, 1 })
                foreach (PileArt look in new[] { PileArt.Strips, PileArt.Junctions })
                {
                    var w = new CordWorld(30, 24);
                    int mx = 15, mz = 12;
                    w.SetBlocked(new Cell(mx, mz), BlockKind.Device);
                    int hx = mx + side;
                    for (int z = 6; z <= 18; z++) w.SetConduit(new Cell(hx, z));
                    for (int x = Math.Min(hx, hx + 8 * side); x <= Math.Max(hx, hx + 8 * side); x++) w.SetConduit(new Cell(x, 6));
                    var mast = new MachineInfo { Id = "mast", Kind = MachineKind.Transmitter, X0 = mx, Z0 = mz, Foot = true, Hookups = new List<Cell> { new Cell(hx, mz) } };
                    w.Machines.Add(mast);
                    var lamp = new MachineInfo { Id = "lamp", Kind = MachineKind.Consumer, X0 = hx + 8 * side, Z0 = 7, Hookups = new List<Cell> { new Cell(hx + 8 * side, 6) } };
                    w.SetBlocked(new Cell(lamp.X0, lamp.Z0), BlockKind.Device);
                    w.Machines.Add(lamp);
                    List<LaidPiece> ps = new CordBuilder().Build(w, new BuildOptions { Pile = look, Seed = 3, SlideUnder = true }, c => true);
                    V2 c = new V2(mx + 0.5, mz + 0.5);
                    foreach (LaidPiece p in ps)
                        foreach (CordStrand s in p.Strands)
                        {
                            if (s.Pts == null || s.Pts.Count < 2) continue;
                            foreach (V2 e in new[] { s.Pts[0], s.Pts[s.Pts.Count - 1] })
                            {
                                if (V2.Dist(e, c) > 0.9) continue;   // a cord end at the mast (a junction on the run beside it is a cell off)
                                n++;
                                if (!(e.Z <= mz + 0.3 && Math.Abs(e.X - (mx + 0.5)) <= 0.3)) { bad++; if (seen.Count < 4) seen.Add($"{look} {p.EndA}-{p.EndB} ({e.X:0.00},{e.Z:0.00})"); }
                            }
                        }
                }
            Check(n >= 2, $"the mast scenes lay a cord to the mast (instrument sees it: {n})");
            Check(bad == 0, $"a floor cord to a mast ends under its foot (x within 0.3 of its middle, no higher than 0.3 into its cell): {bad} of {n} do not {string.Join("; ", seen)}");
        }
    }
}
