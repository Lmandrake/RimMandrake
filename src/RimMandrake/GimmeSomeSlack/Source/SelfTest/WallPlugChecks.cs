// T_WALL_PLUG_STRAIGHT_OFFLINE (RIMMANDRAKE_STRAIGHTEN_SLACK_CORD_WHERE_IT_LEAVES_WALL_PLUG_HE_SAW_IT_LIVE; the owner on ArchBig, 2026-11-23): "Note the
// cord that does not come out stright so it doesn't look aligned with the wall plug".
// The bar: a cord leaves a wall plug straight out of it. Read where the plug's boot ends, over the next SlopeChord (0.08 cell, about one cord's width): within
// MaxDeg of the plug's axis and MaxOff of its line, and no device plug is drawn on a wall plug. MaxDeg 3: over the chord the cord's middle then strays 0.004 cell,
// half a screen pixel at 110 px a cell (the zoom of his picture). MaxOff 0.02: the boot and the cord are both about 0.08 wide, so under a quarter of that shows as a step.
// The rule at every stub (StubJoins, 12 degrees) is the looser one: 12 degrees is what "5-12 degree plug-join slopes" was.
//
// The scenes: Modern (the one look whose wall ends are plugs); every face a plug stands out of (east, west, the hidden north) and the south outlet;
//   lamp       a wall lamp on the far side of a wall (his picture), 4 cells either way along the wall
//   across     a device on the far side of a wall no conduit passes, its cord dived through: 1-5 cells off the wall, 5 either way
//   through    conduit through the wall to a device: 1-4 cells from the plug, the device before, beside or past the run's end, the near side 1-5 cells, a battery or a lamp
//   ends       a run that ends in the wall, and the room-corner walls (CordEndKindChecks.WallScene)
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class WallPlugChecks
    {
        public const double MaxDeg = 3, MaxOff = 0.02, MidDeg = CordEndAudit.SlopeMaxDeg;
        private static readonly Cell[] Dirs = { new Cell(0, 1), new Cell(1, 0), new Cell(0, -1), new Cell(-1, 0) };

        internal sealed class Read
        {
            public int Scenes, Plugs, Cords, Bare, Off, Slant, Stacked, Kinks, BendsNear;
            public readonly SortedDictionary<string, int> BendWhy = new SortedDictionary<string, int>(StringComparer.Ordinal);
            public readonly List<string> Unforced = new List<string>();
            public double WorstDeg, WorstOff;
            public readonly SortedDictionary<string, List<double>> ByKind = new SortedDictionary<string, List<double>>(StringComparer.Ordinal);
            /// <summary>Each plug cord's (cell off the stub's end, degrees off its axis), by stub kind.</summary>
            public readonly SortedDictionary<string, List<(double Off, double Deg)>> OffByKind = new SortedDictionary<string, List<(double Off, double Deg)>>(StringComparer.Ordinal);
            public readonly List<string> Bad = new List<string>();
        }

        private static string F(double d) => d.ToString("0.###", CultureInfo.InvariantCulture);

        /// <summary>Every wall plug's cord of a built scene (and, for the table, every other plug's).</summary>
        internal static void Take(Read r, CordWorld w, List<LaidPiece> ps, BuildOptions opt, string name, StreamWriter dump = null)
        {
            r.Scenes++;
            List<StubArt.Stub> stubs = StubArt.Of(w, ps, opt);
            var seen = new HashSet<StubArt.Stub>();
            foreach (LaidPiece p in ps)
                foreach (CordStrand s in p.Strands)
                {
                    if (s.OverFace || s.Lifted || s.Pts == null || s.Pts.Count < 2) continue;
                    foreach (bool atStart in new[] { true, false })
                    {
                        StubArt.Stub st = StubJoins.StubFor(stubs, s.Pts, atStart, out V2 q, out V2 h);
                        if (st == null || !st.Kind.Contains("plug") && st.Kind != "wall outlet") continue;
                        double deg = Math.Acos(Math.Max(-1, Math.Min(1, h.X * st.U.X + h.Z * st.U.Z))) * 180 / Math.PI, off = V2.Dist(q, st.T);
                        if (!r.ByKind.TryGetValue(st.Kind, out List<double> l)) r.ByKind[st.Kind] = l = new List<double>();
                        l.Add(deg);
                        if (!r.OffByKind.TryGetValue(st.Kind, out List<(double, double)> lo)) r.OffByKind[st.Kind] = lo = new List<(double, double)>();
                        lo.Add((off, deg));
                        if (st.Kind != "wall plug" && st.Kind != "wall outlet") continue;
                        seen.Add(st);
                        r.Cords++;
                        // (instrument, fresh reader of 1e926ebe4c: the bar sc_no_sharp_turn's bends on this cord within 1.5 cells of the plug, as the bar classes them)
                        foreach (CordShapeAudit.Bend b in CordShapeAudit.Bends(s.Pts, s.Ties))
                        {
                            double fromPlug = atStart ? b.S : Geo.Length(s.Pts) - b.S;
                            if (fromPlug > 1.5) continue;
                            r.BendsNear++;
                            string why = CordShapeAudit.Why(w, p.EndA, p.EndB, s.Pts, b);
                            r.BendWhy[why] = r.BendWhy.TryGetValue(why, out int nw) ? nw + 1 : 1;
                            if (why == "unforced") r.Unforced.Add($"{name} {st.Piece}: an unforced bend {b.Turn:0} deg over {b.Arc:0.00} cell, {fromPlug:0.00} from the plug (lay {s.Lay})");
                        }
                        r.WorstDeg = Math.Max(r.WorstDeg, deg); r.WorstOff = Math.Max(r.WorstOff, off);
                        bool bad = false;
                        if (off > MaxOff) { r.Off++; bad = true; }
                        if (deg > MaxDeg) { r.Slant++; bad = true; }
                        // ("+straight": two fittings nearer each other than their two straight runs; counted, held to the stub rule)
                        if (bad) r.Bad.Add($"{name} {st.Piece}: the cord leaves the plug {deg:0.0} deg off its axis, {off:0.000} cell off its line (lay {s.Lay}, {Geo.Length(s.Pts):0.00} cells)");
                        dump?.WriteLine($"{{\"scene\":\"{name}\",\"kind\":\"{st.Kind}\",\"deg\":{F(deg)},\"off\":{F(off)},\"lay\":\"{s.Lay}\",\"start\":{(atStart ? "true" : "false")},\"dive\":{((atStart ? s.DiveA : s.DiveB) ? "true" : "false")},"
                            + $"\"T\":[{F(st.T.X)},{F(st.T.Z)}],\"U\":[{F(st.U.X)},{F(st.U.Z)}],\"pts\":[{string.Join(",", s.Pts.Select(x => "[" + F(x.X) + "," + F(x.Z) + "]"))}]}}");
                    }
                }
            foreach (StubArt.Stub st in stubs.Where(x => x.Kind == "wall plug"))
            {
                r.Plugs++;
                if (!seen.Contains(st)) { r.Bare++; r.Bad.Add($"{name} {st.Piece}: no cord leaves the wall plug"); }
            }
            List<CordDecal> walls = ps.SelectMany(p => p.Decals).Where(d => d.Kind == DecalKind.Plug && d.Scale == CordBuilder.WallPlugScale).ToList();
            foreach (CordDecal d in ps.SelectMany(p => p.Decals).Where(d => d.Kind == DecalKind.Plug && d.Scale != CordBuilder.WallPlugScale))
                if (walls.Any(x => V2.Dist(x.Pos, d.Pos) < 0.3)) { r.Stacked++; r.Bad.Add($"{name}: a device plug is drawn on a wall plug at ({d.Pos.X:0.00},{d.Pos.Z:0.00})"); }
            foreach (LaidPiece p in ps)
                foreach (CordStrand s in p.Strands)
                    if (s.Pts != null && s.Pts.Count > 2 && !s.Lifted && !s.OverFace)
                        foreach (double a in CordShapeAudit.Kinks(s.Pts, s.Ties))
                            if (CordShapeAudit.KinkWhy(w, p.EndA, p.EndB, s.Pts, a) == "unforced") { r.Kinks++; r.Bad.Add($"{name} {p.EndA}|{p.EndB}: an unforced kink {a:0.00} along {Geo.Length(s.Pts):0.00} (lay {s.Lay})"); }
        }

        private static Cell At(Cell into, int along, int deep) => new Cell(20 + into.Z * along + into.X * deep, 20 + into.X * along + into.Z * deep);

        private static void Dev(CordWorld w, string id, MachineKind k, Cell c, Cell hook)
        {
            w.SetBlocked(c, BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = id, Kind = k, X0 = c.X, Z0 = c.Z, Hookups = new List<Cell> { hook } });
        }

        /// <summary>A wall no conduit passes; the device beyond it hooks to the run on the near side.</summary>
        internal static CordWorld Across(Cell into, int dx, int dz, int near)
        {
            var w = new CordWorld(40, 40);
            for (int k = -14; k <= 14; k++) w.SetBlocked(At(into, k, near), BlockKind.Wall);
            for (int k = -6; k <= 6; k++) w.SetConduit(At(into, k, 0));
            Dev(w, "bat", MachineKind.Battery, At(into, -7, 0), At(into, -6, 0));
            Dev(w, "lamp", MachineKind.Consumer, At(into, dx, near + dz), At(into, 0, 0));
            return w;
        }

        /// <summary>Conduit through the wall: <paramref name="near"/> cells before it, <paramref name="far"/> past it, then <paramref name="bend"/> along it; the device at the end.</summary>
        internal static CordWorld Through(Cell into, int near, int far, int bend, bool battery)
        {
            var w = new CordWorld(40, 40);
            for (int k = -14; k <= 14; k++) if (k != 0) w.SetBlocked(At(into, k, 0), BlockKind.Wall);
            w.SetBlocked(At(into, 0, 0), BlockKind.Wall);
            for (int k = -near; k <= far; k++) w.SetConduit(At(into, 0, k));
            int sg = Math.Sign(bend);
            for (int k = 1; k <= Math.Abs(bend); k++) w.SetConduit(At(into, sg * k, far));
            Cell end = At(into, bend, far), dev = bend == 0 ? At(into, 0, far + 1) : At(into, bend + sg, far);
            Dev(w, "src", MachineKind.Battery, At(into, 0, -near - 1), At(into, 0, -near));
            Dev(w, "dev", battery ? MachineKind.Battery : MachineKind.Consumer, dev, end);
            return w;
        }

        internal static Read Sweep(StreamWriter dump = null, int seeds = 2, int cords = 0, int firstSeed = 71, string look = "Modern")
        {
            var r = new Read();
            void Run1(CordWorld w, string name, int seed)
            {
                var opt = new BuildOptions { Pile = look == "Modern" ? PileArt.Strips : PileArt.Junctions, Seed = (ulong)seed, PlugBoot = CordBuilder.PlugBootU(look) };
                if (cords > 0) opt.Lay.CordsMin = opt.Lay.CordsMax = cords;
                List<LaidPiece> ps = new CordBuilder().Build(w, opt, _ => true);
                Take(r, w, ps, opt, name + " s" + seed, dump);
            }
            for (int seed = firstSeed; seed < firstSeed + seeds; seed++)
                foreach (Cell d in Dirs)
                {
                    for (int dx = -4; dx <= 4; dx++) Run1(StubJoinChecks.FarWallLampScene(dx, d), $"lamp {d} dx{dx}", seed);
                    for (int dx = -5; dx <= 5; dx++)
                        foreach (int dz in new[] { 1, 2, 3, 5 })
                            foreach (int near in new[] { 1, 3 }) Run1(Across(d, dx, dz, near), $"across {d} dx{dx} dz{dz} near{near}", seed);
                    foreach (int near in new[] { 1, 2, 4 })
                        foreach (int far in new[] { 1, 2, 4 })
                            foreach (int bend in new[] { -3, -1, 0, 1, 3 })
                                foreach (bool bat in new[] { false, true }) Run1(Through(d, near, far, bend, bat), $"through {d} near{near} far{far} bend{bend} {(bat ? "battery" : "device")}", seed);
                    foreach (bool term in new[] { false, true })
                        foreach (bool corner in new[] { false, true })
                            foreach (int lat in new[] { -2, 1 }) Run1(CordEndKindChecks.WallScene(d, term, corner, lat, BlockKind.Wall), $"ends {d} {(term ? "in" : "through")}{(corner ? " corner" : "")} lat{lat}", seed);
                }
            return r;
        }

        public static void Run(string path = null, int seeds = 2, int firstSeed = 71)
        {
            Read r;
            using (StreamWriter sw = string.IsNullOrEmpty(path) ? null : new StreamWriter(path)) r = Sweep(sw, seeds, 0, firstSeed);
            // the Mod Setting cords per run at 2: a bundle's strands share the one outlet, a plug each
            Read two = Sweep(null, 1, 2, firstSeed);
            foreach (var kv in r.ByKind)
            {
                List<double> l = kv.Value; l.Sort();
                Console.WriteLine($"  wall plugs: {kv.Key}: {l.Count} cords, median {l[l.Count / 2]:0.0} deg, p99 {l[(int)(l.Count * 0.99)]:0.0}, worst {l[l.Count - 1]:0.0}; over {MaxDeg}: {l.Count(x => x > MaxDeg)}, over {MidDeg}: {l.Count(x => x > MidDeg)}");
            }
            foreach (string b in r.Bad.Take(16).Concat(two.Bad.Select(x => "(2 cords per run) " + x).Take(12))) Console.WriteLine("  wall plugs refused: " + b);
            Console.WriteLine($"  wall plugs: {r.Scenes} scenes, {r.Plugs} plugs, {r.Cords} cords at a wall plug or outlet, {r.Slant} slanted, {r.Off} off line, {r.Bare} bare, {r.Stacked} stacked, {r.Kinks} unforced kinks; worst {r.WorstDeg:0.0} deg, {r.WorstOff:0.000} cell");
            Console.WriteLine($"  wall plugs, 2 cords per run: {two.Scenes} scenes, {two.Cords} cords, {two.Slant} slanted, {two.Off} off line, {two.Bare} bare, {two.Stacked} stacked, {two.Kinks} unforced kinks; worst {two.WorstDeg:0.0} deg, {two.WorstOff:0.000} cell");
            Program.Check(two.Scenes >= 500 && two.Slant == 0 && two.Off == 0 && two.Bare == 0 && two.Stacked == 0, $"wall plugs, 2 cords per run: every cord leaves its wall plug straight ({two.Slant} over {MaxDeg} deg, {two.Off} over {MaxOff} cell, {two.Bare} bare, {two.Stacked} stacked, of {two.Cords})");
            Console.WriteLine($"  wall plugs: bends within 1.5 cells of a wall plug: {r.BendsNear}; by the bar's class: {string.Join(", ", r.BendWhy.Select(kv => kv.Key + " " + kv.Value))}");
            // every plug a cord leaves, in every look (owner 2026-11-23, via the Conductor: "the wall-plug connector has a literal stub for the cord to
            // connect to ... it's coming out of the side of the wall-plug connector impossibly"): the cord starts on the drawn stub's end and runs along
            // its axis, for the device and battery plug (kind "plug", each look's boot: PlugBootU, measured from the art by selftest_gss_stub_art_census.py),
            // the strip plug, the wall plug and the south outlet. The wall plug's own bars hold here for all of them.
            int anchorCords = 0, anchorBad = 0; double anchorOff = 0, anchorDeg = 0;
            var anchorWhy = new List<string>();
            void Hold(string lk, Read o)
            {
                foreach (var kv in o.OffByKind)
                {
                    List<double> offs = kv.Value.Select(x => x.Off).ToList(), degs = kv.Value.Select(x => x.Deg).ToList();
                    int bad = kv.Value.Count(x => x.Off > MaxOff || x.Deg > MaxDeg);
                    anchorCords += offs.Count; anchorBad += bad; anchorOff = Math.Max(anchorOff, offs.Max()); anchorDeg = Math.Max(anchorDeg, degs.Max());
                    Console.WriteLine($"  plugs ({lk}): {kv.Key}: {offs.Count} cords, worst {offs.Max():0.000} cell off the stub's end (limit {MaxOff}), worst {degs.Max():0.0} deg off its axis (limit {MaxDeg}); {bad} over");
                    if (bad > 0) anchorWhy.Add($"{lk} {kv.Key} {bad}");
                }
            }
            Hold("Modern", r);
            foreach (string lk in new[] { "Industrial", "Futuristic", "Scrapper" }) Hold(lk, Sweep(null, 1, 0, firstSeed, lk));
            Program.Check(anchorCords >= 8000 && anchorBad == 0, $"plugs, every look: each cord starts on its plug's stub end and runs along it ({anchorBad} of {anchorCords} over {MaxOff} cell or {MaxDeg} deg: {string.Join(", ", anchorWhy)}; worst {anchorOff:0.000} cell, {anchorDeg:0.0} deg)");
            foreach (string b in r.Unforced.Take(Environment.GetEnvironmentVariable("WP_ALL") != null ? 9999 : 12)) Console.WriteLine("  wall plugs, unforced bend: " + b);
            Program.Check(r.Kinks == 0, $"wall plugs: no cord kinks where nothing forces it ({r.Kinks})");
            Program.Check(r.Scenes >= 1000 && r.Plugs >= 1500, $"wall plugs: the sweep reads its scenes ({r.Scenes} scenes, {r.Plugs} plugs)");
            Program.Check(r.Slant == 0 && r.Off == 0 && r.Bare == 0, $"wall plugs: every cord leaves its wall plug straight ({r.Slant} over {MaxDeg} deg, {r.Off} over {MaxOff} cell, {r.Bare} bare, of {r.Cords}; worst {r.WorstDeg:0.0} deg)");
            Program.Check(r.Stacked == 0, $"wall plugs: no device plug is drawn on a wall plug ({r.Stacked})");
        }
    }
}
