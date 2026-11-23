// T_NO_KINK_OFFLINE (RIMMANDRAKE_SMOOTH_SLACK_GROUND_CORD_KINKS_AT_STATION_THREE; the owner at his walk of 2026-11-22, station 3, ground cords, Modern):
// "Station 3 has radical kinks in the swarm of blue cables ... I don't even see why, it didn't have to bend that radically."
// The bar: no ground cord bends sharply where nothing forces it. A kink is a turn of CordShapeAudit.KinkDeg within KinkArc of cord (a radius under 0.14 cell;
// the loose loops lie at 0.45 and wider); it is forced only where it lies under art (hidden), in a cut end's own limp curl, or beside a wall, furniture or another
// machine (CordShapeAudit.KinkWhy).
//
// The scenes, and the range of situations they cover:
//   stations 1-4   the owner's review map as the live probe dumped it (owner_look_20261116.json; station 3 is the very build he walked on 2026-11-22),
//                  the four looks' ground-cord stations: battery, 3x3 pile (strips or boxes), a wall the run passes under, an in-line switch, lamps, a cut;
//   region         the same build made in code over seeds, pile size (3x3, 4x3, 3x4, 4x4), battery lead length, lamp place, wall on or off, pile look
//                  (strips, boxes): the geometry sweep that ruled the fix (design/concepts/GimmeSomeSlack/version/evidence/kinks_20261122/).
// Left out: aerial wires (their own sag), a dead end's limp curl (its own art), a pile so cramped no blend stays on its ground (forced).
//
// Red on the builder before the fix (--no-unkink: CordBuilder.UnkinkOff, the builder before CordShape.Unkink): station 3 has 3 visible kinks, there.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class KinkChecks
    {
        /// <summary>The ground-cord stations 1-4 on the owner's review map (human_review.py ground_station: origin x 142 + 24 i, z 42, 16 x 7 cells), with a cell's margin.</summary>
        private static readonly (string name, int x0, int z0, int x1, int z1)[] Stations =
        {
            ("station 1 (Scrapper)", 141, 41, 159, 50), ("station 2 (Industrial)", 165, 41, 183, 50),
            ("station 3 (Modern, his walk 2026-11-22)", 189, 41, 207, 50), ("station 4 (Futuristic)", 213, 41, 231, 50),
        };

        internal sealed class Tally
        {
            public int Strands, Kinks, Unforced, Jogs;
            public readonly List<string> JogRows = new List<string>();
            public readonly Dictionary<string, int> ByWhy = new Dictionary<string, int>();
            public readonly List<string> Rows = new List<string>();
        }

        private static string F(double d) => d.ToString("0.00", CultureInfo.InvariantCulture);

        /// <summary>The kinks of every ground strand of <paramref name="ps"/> that lies (any point) inside the rect, classed by <see cref="CordShapeAudit.KinkWhy"/>.</summary>
        internal static void Count(CordWorld w, List<LaidPiece> ps, Tally t, string where, double x0 = double.MinValue, double z0 = double.MinValue, double x1 = double.MaxValue, double z1 = double.MaxValue)
        {
            foreach (LaidPiece p in ps)
                foreach (CordStrand s in p.Strands)
                {
                    if (s.Pts == null || s.Pts.Count < 3 || s.Lifted || s.OverFace) continue;
                    if (!s.Pts.Any(q => q.X >= x0 && q.X <= x1 && q.Z >= z0 && q.Z <= z1)) continue;
                    t.Strands++;
                    foreach (double a in CordShapeAudit.Kinks(s.Pts, s.Ties))
                    {
                        string why = CordShapeAudit.KinkWhy(w, p.EndA, p.EndB, s.Pts, a);
                        t.Kinks++;
                        t.ByWhy[why] = t.ByWhy.TryGetValue(why, out int n) ? n + 1 : 1;
                        if (why != "unforced") continue;
                        if (IsJog(s.Pts, a))
                        {
                            // an S-notch: two opposite turns a few hundredths of a cell apart, the cord's way the same either side; not a sharp turn
                            t.Jogs++;
                            if (t.JogRows.Count < 6) t.JogRows.Add(where + " " + (p.EndA ?? p.Key) + "|" + (p.EndB ?? "") + " (" + F(a) + " along)");
                            continue;
                        }
                        t.Unforced++;
                        if (t.Rows.Count < 12)
                        {
                            V2 at = Geo.Resample(s.Pts, CordShapeAudit.KinkStep)[Math.Min((int)Math.Round(a / CordShapeAudit.KinkStep), Geo.Resample(s.Pts, CordShapeAudit.KinkStep).Count - 1)];
                            t.Rows.Add(where + " " + (p.EndA ?? p.Key) + "|" + (p.EndB ?? "") + " at " + F(at.X) + "," + F(at.Z) + " (" + F(a) + " along, lay " + s.Lay + ")");
                        }
                    }
                }
        }

        /// <summary>A jog, not a kink: the cord's heading over the 0.12 cell before <see cref="JogReach"/> of the apex and the 0.12 after differs by under
        /// <see cref="JogNetDeg"/> (an S-notch whose two turns cancel), where a kink turns the cord's way (his station-3 hooks: 114 and 129 degrees).</summary>
        internal static bool IsJog(List<V2> pts, double a)
        {
            double L = Geo.Length(pts);
            // near an end the windows shrink to what cord there is (at least 0.05 cell either side)
            double r0 = Math.Min(JogReach, a - 0.06), r1 = Math.Min(JogReach, L - a - 0.06);
            if (r0 < 0.03 || r1 < 0.03) return false;
            V2 h0 = At(pts, a - r0) - At(pts, Math.Max(0, a - r0 - 0.12)), h1 = At(pts, Math.Min(L, a + r1 + 0.12)) - At(pts, a + r1);
            if (h0.Len < 1e-9 || h1.Len < 1e-9) return false;
            double turn = Math.Abs(Math.Atan2(h0.X * h1.Z - h0.Z * h1.X, h0.X * h1.X + h0.Z * h1.Z)) * 180 / Math.PI;
            return turn < JogNetDeg;
        }
        internal const double JogReach = 0.1, JogNetDeg = 35;

        private static V2 At(List<V2> pts, double s)
        {
            double acc = 0;
            for (int i = 1; i < pts.Count; i++)
            {
                double d = V2.Dist(pts[i - 1], pts[i]);
                if (acc + d >= s) return d < 1e-12 ? pts[i] : pts[i - 1] + (pts[i] - pts[i - 1]) * ((s - acc) / d);
                acc += d;
            }
            return pts[pts.Count - 1];
        }

        /// <summary>The review map's stations 1-4, laid by the production builder from the probe's dump.</summary>
        internal static Tally Stations14(bool perStation = false, Action<string, Tally> each = null)
        {
            using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "owner_look_20261116.json")));
            CordWorld w = LabWorld.Read(doc.RootElement, out BuildOptions opt, out HashSet<Cell> live);
            List<LaidPiece> ps = new CordBuilder().Build(w, opt, c => live.Contains(c));
            var all = new Tally();
            foreach (var st in Stations)
            {
                var t = new Tally();
                Count(w, ps, t, st.name, st.x0, st.z0, st.x1, st.z1);
                each?.Invoke(st.name, t);
                all.Strands += t.Strands; all.Kinks += t.Kinks; all.Unforced += t.Unforced; all.Jogs += t.Jogs; all.Rows.AddRange(t.Rows);
                foreach (var kv in t.ByWhy) all.ByWhy[kv.Key] = all.ByWhy.TryGetValue(kv.Key, out int n) ? n + kv.Value : kv.Value;
            }
            return all;
        }

        /// <summary>One station-3-like build in a 30 x 16 world (the sweep's gen.py, in code): battery, a lead of <paramref name="blead"/> cells, a tw x th pile, a run
        /// of three cells (under a wall when <paramref name="wall"/>), an in-line switch, two cells, a missing cell, two cells, a heater; a lamp by the pile and two by the run.</summary>
        internal static string StationWorld(int seed, int tw, int th, int blead, int ldz, int ldx, bool wall, bool strips)
        {
            int ox = 3, oz = 4, tx0 = ox + 2 + blead, zc = oz + 3, tz0 = zc - th / 2, xe = tx0 + tw, sw = xe + 3;
            var cells = new SortedSet<(int, int)>();
            for (int x = ox + 1; x < tx0; x++) cells.Add((x, zc));
            for (int x = tx0; x < tx0 + tw; x++) for (int z = tz0; z < tz0 + th; z++) cells.Add((x, z));
            for (int x = xe; x < sw; x++) cells.Add((x, zc));
            foreach (int x in new[] { sw + 1, sw + 2, sw + 4, sw + 5 }) cells.Add((x, zc));
            string C((int x, int z) c) => "[" + c.x + "," + c.z + "]";
            var sb = new StringBuilder("{\"w\":30,\"h\":16,\"conduit\":[").Append(string.Join(",", cells.Select(C))).Append("],\"blocked\":[");
            if (wall) sb.Append(string.Join(",", Enumerable.Range(zc - 2, 5).Select(z => "[" + (xe + 1) + "," + z + ",1]")));
            sb.Append("],\"doors\":[],\"buried\":[],\"busy\":[").Append(string.Join(",", cells.Select(C))).Append("],\"furniture\":[],\"costs\":[],\"connectParentData\":true,\"unhooked\":[],\"machines\":[");
            string M(string id, string def, int kind, int x, int z, int w, int h, string hooks, string cp, double baseDz = 0) =>
                "{\"id\":\"" + id + "\",\"def\":\"" + def + "\",\"baseDz\":" + baseDz.ToString(CultureInfo.InvariantCulture) + ",\"kind\":" + kind + ",\"x\":" + x + ",\"z\":" + z + ",\"w\":" + w + ",\"h\":" + h +
                ",\"hookups\":[" + hooks + "],\"links\":[],\"insets\":[0,0,0,0],\"connectParent\":" + (cp ?? "null") + "}";
            int lx = tx0 - 1 + ldx;
            var ms = new List<string>
            {
                M("bat", "Battery", 1, ox, zc, 1, 2, "[" + (ox + 1) + "," + zc + "]", null),
                M("sw", "PowerSwitch", 4, sw, zc, 1, 1, "[" + (sw + 1) + "," + zc + "],[" + (sw - 1) + "," + zc + "]", null),
                M("heat", "Heater", 2, sw + 6, zc, 1, 1, "[" + (sw + 5) + "," + zc + "]", "[" + (sw + 5) + "," + zc + "]"),
                M("lamp0", "StandingLamp", 2, lx, zc + ldz, 1, 1, "[" + tx0 + "," + (tz0 + th - 1) + "]", "[" + tx0 + "," + (tz0 + th - 1) + "]", -0.25),
                M("lamp1", "StandingLamp", 2, sw + 1, zc + 3, 1, 1, "[" + (sw + 1) + "," + zc + "]", "[" + (sw + 1) + "," + zc + "]", -0.25),
                M("lamp2", "StandingLamp", 2, sw + 5, zc + 3, 1, 1, "[" + (sw + 5) + "," + zc + "]", "[" + (sw + 5) + "," + zc + "]", -0.25),
            };
            if (cells.Contains((lx, zc + ldz))) return null;
            sb.Append(string.Join(",", ms)).Append("],\"live\":[").Append(string.Join(",", cells.Where(c => c != (sw + 4, zc) && c != (sw + 5, zc)).Select(C))).Append(']');
            var all = cells.Concat(new[] { (sw, zc) }).ToList();
            sb.Append(",\"strips\":[").Append(strips ? string.Join(",", all.Select(C)) : "").Append("],\"boxes\":[").Append(strips ? "" : string.Join(",", all.Select(C))).Append(']');
            string look = strips ? "Modern" : "Scrapper";
            sb.Append(",\"looks\":[").Append(string.Join(",", all.Select(c => "[" + c.Item1 + "," + c.Item2 + ",\"" + look + "\"]"))).Append(']');
            sb.Append(",\"opt\":{\"boot\":0.102,\"tangles\":true,\"needless\":true,\"tangleMin\":9,\"strips\":").Append(strips ? "true" : "false")
              .Append(",\"dive\":true,\"slide\":true,\"seed\":").Append(seed).Append(",\"slack\":1,\"maxExtra\":16,\"cordsMax\":1,\"straight\":[]}}");
            return sb.ToString();
        }

        /// <summary>The region round station 3: <paramref name="seeds"/> seeds x 4 pile sizes x 2 battery leads x 2 lamp places x wall on/off x 2 pile looks.</summary>
        internal static Tally Region(int seeds, out int worlds)
        {
            var t = new Tally();
            worlds = 0;
            foreach (int seed in Enumerable.Range(1, seeds))
                foreach (var (tw, th) in new[] { (3, 3), (4, 3), (3, 4), (4, 4) })
                    foreach (int blead in new[] { 1, 3 })
                        foreach (var (ldz, ldx) in new[] { (3, 0), (2, 2) })
                            foreach (bool wall in new[] { true, false })
                                foreach (bool strips in new[] { true, false })
                                {
                                    string json = StationWorld(seed, tw, th, blead, ldz, ldx, wall, strips);
                                    if (json == null) continue;
                                    using JsonDocument doc = JsonDocument.Parse(json);
                                    CordWorld w = LabWorld.Read(doc.RootElement, out BuildOptions opt, out HashSet<Cell> live);
                                    List<LaidPiece> ps = new CordBuilder().Build(w, opt, c => live.Contains(c));
                                    Count(w, ps, t, "s" + seed + "_t" + tw + "x" + th + "_b" + blead + "_l" + ldz + ldx + "_w" + (wall ? 1 : 0) + (strips ? "_strips" : "_boxes"));
                                    worlds++;
                                }
            return t;
        }

        private static string Why(Tally t) => string.Join(" ", t.ByWhy.OrderBy(kv => kv.Key, StringComparer.Ordinal).Select(kv => kv.Key + "=" + kv.Value));

        /// <summary>T_CORE entry: no unforced kink at stations 1-4 or over the region (2 seeds in T_CORE, <paramref name="seeds"/> with --kinks-only).</summary>
        internal static void Run(int seeds = 2)
        {
            Tally s = Stations14(each: (name, t) =>
            {
                Console.WriteLine("no kink: " + name + ": " + t.Strands + " strands, " + t.Kinks + " kinks (" + Why(t) + "), unforced " + t.Unforced + ", S-jogs " + t.Jogs);
                Program.Check(t.Unforced == 0, "no kink: " + name + ": " + t.Unforced + " unforced kinks" + (t.Rows.Count > 0 ? ": " + string.Join("; ", t.Rows.Take(3)) : ""));
            });
            Tally r = Region(seeds, out int worlds);
            Console.WriteLine("no kink: region round station 3: " + worlds + " worlds, " + r.Strands + " strands, " + r.Kinks + " kinks (" + Why(r) + "), unforced " + r.Unforced
                              + ", S-jogs " + r.Jogs + " (a stub join's notch, polish.md; not a sharp turn)");
            foreach (string row in r.Rows.Take(6)) Console.WriteLine("  unforced kink: " + row);
            foreach (string row in r.JogRows) Console.WriteLine("  jog: " + row);
            Program.Check(worlds >= 64 * seeds - 8 * seeds, "no kink: the region built its worlds (" + worlds + ")");
            Program.Check(r.Unforced == 0, "no kink: region round station 3: " + r.Unforced + " unforced kinks over " + worlds + " worlds");
        }

        /// <summary>--kinks-plant: the builder before the fix (<see cref="CordBuilder.UnkinkOff"/>) must turn station 3 red, and a planted hook must read as a kink.</summary>
        internal static void Plant()
        {
            var hook = new List<V2>();
            for (int i = 0; i <= 10; i++) hook.Add(new V2(i * 0.05, 0));
            for (int i = 1; i <= 10; i++) hook.Add(new V2(0.5 - i * 0.035, i * 0.035));
            Program.Check(CordShapeAudit.Kinks(hook).Count == 1, "no kink plant: a planted 135 degree hook reads as one kink");
            var loop = new List<V2>();
            for (int i = 0; i <= 60; i++) loop.Add(new V2(0.45 * Math.Cos(i * 2 * Math.PI / 60), 0.45 * Math.Sin(i * 2 * Math.PI / 60)));
            Program.Check(CordShapeAudit.Kinks(loop).Count == 0, "no kink plant: a 0.45 cell loop (the north star's own) reads as no kink");
            double hookApex = CordShapeAudit.Kinks(hook).FirstOrDefault();
            var notch = new List<V2>();
            for (int i = 0; i <= 10; i++) notch.Add(new V2(i * 0.05, 0));
            notch.Add(new V2(0.52, 0.04));
            for (int i = 1; i <= 10; i++) notch.Add(new V2(0.52 + i * 0.05, 0.04));
            List<double> nk = CordShapeAudit.Kinks(notch);
            Program.Check(nk.Count > 0 && nk.All(a => IsJog(notch, a)), "no kink plant: a 0.04 cell S-notch reads as a jog (" + nk.Count + " turns)");
            Program.Check(!IsJog(hook, hookApex), "no kink plant: a 135 degree hook is never a jog");
            bool was = CordBuilder.UnkinkOff;
            CordBuilder.UnkinkOff = true;
            int st3 = 0;
            try { Stations14(each: (name, t) => { if (name.StartsWith("station 3", StringComparison.Ordinal)) st3 = t.Unforced; }); }
            finally { CordBuilder.UnkinkOff = was; }
            Console.WriteLine("planted [the builder before CordShape.Unkink]: station 3 has " + st3 + " unforced kinks: " + (st3 > 0 ? "CAUGHT" : "NOT CAUGHT"));
            Program.Check(st3 > 0, "no kink plant: the builder before the fix is caught at station 3");
        }
    }
}
