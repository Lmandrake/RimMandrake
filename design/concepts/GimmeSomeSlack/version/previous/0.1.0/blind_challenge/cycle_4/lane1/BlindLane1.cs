// Blind lane 1, GimmeSomeSlack 0.1.0 cycle 4: tests written from the bars (tree.json, sheet.md, plan.md) and the shipped
// settings alone, against the production kernel AerialMath.cs (and ConduitPlacementGate.cs), before any builder test was read.
// Modes:  BlindLane1            run the kernel rows, one JSON row per line on stdout; exit 0 all PASS, 1 any FAIL
//         BlindLane1 --types X  list every TypeDefinition (namespace.name) of assembly X, one per line (a metadata reader,
//                               for the no-hose scan of the shipped DLL; never a string scan)
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Text;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;

public static class BlindLane1
{
    static int fails;
    static string Esc(string s) => s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ");
    static void Row(string id, string bars, string kind, bool ok, int cases, string detail)
    {
        if (!ok) fails++;
        Console.WriteLine("{\"id\":\"" + id + "\",\"bars\":[" + string.Join(",", bars.Split(',').Select(b => "\"" + b.Trim() + "\"")) +
                          "],\"kind\":\"" + kind + "\",\"verdict\":\"" + (ok ? "PASS" : "FAIL") + "\",\"cases\":" + cases +
                          ",\"detail\":\"" + Esc(detail) + "\"}");
    }

    public static int Main(string[] args)
    {
        if (args.Length == 2 && args[0] == "--types") return Types(args[1]);
        SpanCurveRows();
        LinkRows();
        RemovalRows();
        FallenLayRows();
        ShockRows();
        TheftRows();
        KindRows();
        GateRows();
        return fails == 0 ? 0 : 1;
    }

    static int Types(string path)
    {
        using var fs = File.OpenRead(path);
        using var pe = new PEReader(fs);
        MetadataReader md = pe.GetMetadataReader();
        foreach (TypeDefinitionHandle h in md.TypeDefinitions)
        {
            TypeDefinition t = md.GetTypeDefinition(h);
            Console.WriteLine(md.GetString(t.Namespace) + "." + md.GetString(t.Name));
        }
        // resource names too: an embedded texture would show here
        foreach (ManifestResourceHandle h in md.ManifestResources)
            Console.WriteLine("resource:" + md.GetString(md.GetManifestResource(h).Name));
        return 0;
    }

    // ---------------------------------------------------------------- spans_above_everything: a span sags, hangs, ends on its insulators
    static void SpanCurveRows()
    {
        // fixed: a 10-cell span at the shipped sag 0.06 dips 0.6 cells at mid-span, ends exactly on A and B
        var a = new P2(0, 0); var b = new P2(10, 0);
        var c = AerialMath.SpanCurve(a, b, 0.06);
        double minZ = c.Min(p => p.Z);
        bool endsOk = c[0].X == a.X && c[0].Z == a.Z && c[c.Count - 1].X == b.X && c[c.Count - 1].Z == b.Z;
        Row("span_fixed_shipped_sag", "spans_above_everything,overhead_spans", "fixed", endsOk && Math.Abs(minZ + 0.6) < 1e-6, 1,
            "10-cell span, sag 0.06: ends exact " + endsOk + ", deepest z " + minZ.ToString("0.0000") + " (want -0.6000)");

        // random: any span, any sag in the slider range 0-0.15, never rises above its chord, never sags past sag*len,
        // deepest point mid-span within one sample, ends exact; seed recorded
        int seed = 4401, n = 0; var rnd = new Random(seed); string bad = null;
        for (int i = 0; i < 4000 && bad == null; i++)
        {
            var pa = new P2(rnd.NextDouble() * 200, rnd.NextDouble() * 200);
            double ang = rnd.NextDouble() * 2 * Math.PI, len = 4 + rnd.NextDouble() * 36;
            var pb = new P2(pa.X + Math.Cos(ang) * len, pa.Z + Math.Sin(ang) * len);
            double sag = rnd.NextDouble() * 0.15; n++;
            var pts = AerialMath.SpanCurve(pa, pb, sag);
            if (pts[0].X != pa.X || pts[0].Z != pa.Z || pts[pts.Count - 1].X != pb.X || pts[pts.Count - 1].Z != pb.Z) { bad = "ends moved"; break; }
            double depthMax = 0;
            foreach (P2 p in pts)
            {
                double t = AerialMath.ProjectT(pa, pb, p);
                P2 chord = P2.Lerp(pa, pb, Math.Max(0, Math.Min(1, t)));
                // the droop is straight screen-down (-Z) from the chord point at the same t; compare at the sample's own t
                double dz = p.Z - (pa.Z + (pb.Z - pa.Z) * SampleT(pa, pb, p));
                if (dz > 1e-9) { bad = "point above chord by " + dz; break; }
                depthMax = Math.Max(depthMax, -dz);
            }
            if (bad == null && depthMax > sag * len + 1e-9) bad = "sag " + depthMax + " > " + sag * len;
            if (bad == null && Math.Abs(AerialKinds.SagDepth(len, sag) - sag * len) > 1e-9) bad = "SagDepth disagrees with sag*len";
            if (bad == null && sag > 0.001 && depthMax < sag * len * 0.95) bad = "sampled sag " + depthMax + " < 95% of " + sag * len;
            if (bad != null) bad += " | case a=" + pa + " len=" + len.ToString("0.00") + " ang=" + ang.ToString("0.000") + " sag=" + sag.ToString("0.0000");
        }
        Row("span_random_hangs_below_chord", "spans_above_everything,overhead_spans", "random", bad == null, n,
            "seed " + seed + (bad == null ? ": every span ends on its insulators, hangs below its chord, sags sag*len" : ": " + bad));

        // fixed: the insulator ends are flat (owner 2026-11-08 "needless kinks"): first segment within 2 deg of the chord at 0.06
        var flat = AerialMath.SpanCurve(new P2(0, 0), new P2(20, 0), 0.06);
        double ang0 = Math.Atan2(-(flat[1].Z - flat[0].Z), flat[1].X - flat[0].X) * 180 / Math.PI;
        Row("span_leaves_insulator_flat", "spans_above_everything", "fixed", Math.Abs(ang0) < 2, 1,
            "20-cell span sag 0.06: first segment " + ang0.ToString("0.00") + " deg off the chord (want < 2)");

        // sway: zero with no wind, zero at both insulators, bounded by the strength slider 0-2
        int sseed = 4402; var sr = new Random(sseed); string sbad = null; int sn = 0;
        foreach (double amp in new[] { 0.0, 0.5, 1.0, 2.0 })
            for (int i = 0; i < 500; i++)
            {
                double t = sr.NextDouble(), time = sr.NextDouble() * 1000, wind = sr.NextDouble() * 3; int s = sr.Next(); sn++;
                double v = AerialMath.Sway(t, time, wind, amp, s);
                if (Math.Abs(v) > amp * Math.Min(wind, 1.5) / 1.5 * 1.3 + 1e-9) sbad = "sway " + v + " over bound at amp " + amp + " wind " + wind;
                if (AerialMath.Sway(0, time, wind, amp, s) != 0 || AerialMath.Sway(1, time, wind, amp, s) != 0) sbad = "insulator moves";
                if (AerialMath.Sway(t, time, 0, amp, s) != 0) sbad = "sways with no wind";
                if (amp == 0 && v != 0) sbad = "sways at strength 0";
            }
        Row("sway_sweep_strength", "spans_above_everything,mod_settings", "sweep", sbad == null, sn,
            "seed " + sseed + ", strength 0/0.5/1/2" + (sbad == null ? ": no wind or strength 0 = still; insulators fixed; bounded" : ": " + sbad));
    }

    // t of a SpanCurve sample: X/Z lerp + Z droop, so t comes from the along-chord coordinate when the chord is not vertical
    static double SampleT(P2 a, P2 b, P2 p)
    {
        double dx = b.X - a.X, dz = b.Z - a.Z;
        if (Math.Abs(dx) > 1e-6) return (p.X - a.X) / dx;
        // a pure north-south span: X carries nothing; droop is along Z itself, so the "chord point" is ambiguous; use ProjectT
        return Math.Max(0, Math.Min(1, AerialMath.ProjectT(a, b, p)));
    }

    // ---------------------------------------------------------------- drawing_true_to_grid / owner_change_coils_wires: who may link
    static AnchorInfo A(int id, int x, int z, int fac = 0, AerialLineKind k = AerialLineKind.Power, int max = 4, bool roof = false) =>
        new AnchorInfo { Id = id, X = x, Z = z, Faction = fac, Kind = k, MaxLinks = max, Roofed = roof };

    static void LinkRows()
    {
        double R = 20;
        var checks = new List<(string, LinkVerdict, LinkVerdict)>
        {
            ("self", AerialMath.CanLink(A(1, 0, 0), A(1, 0, 0), R), LinkVerdict.Self),
            ("foreign", AerialMath.CanLink(A(1, 0, 0), A(2, 5, 0, fac: 1), R), LinkVerdict.Foreign),
            ("pipe-power", AerialMath.CanLink(A(1, 0, 0), A(2, 5, 0, k: AerialLineKind.Pipe), R), LinkVerdict.WrongKind),
            ("roofed", AerialMath.CanLink(A(1, 0, 0), A(2, 5, 0, roof: true), R), LinkVerdict.Roofed),
            ("range", AerialMath.CanLink(A(1, 0, 0), A(2, 21, 0), R), LinkVerdict.OutOfRange),
            ("range-edge", AerialMath.CanLink(A(1, 0, 0), A(2, 20, 0), R), LinkVerdict.Ok),
            ("ok", AerialMath.CanLink(A(1, 0, 0), A(2, 12, 16), R), LinkVerdict.Ok),
        };
        var full = A(1, 0, 0, max: 1); full.Linked.Add(9);
        checks.Add(("fullA", AerialMath.CanLink(full, A(2, 3, 0), R), LinkVerdict.FullA));
        var bad = checks.Where(c => c.Item2 != c.Item3).Select(c => c.Item1 + "=" + c.Item2 + " want " + c.Item3).ToList();
        Row("canlink_truth_table", "drawing_true_to_grid,owner_change_coils_wires,overhead_spans", "fixed", bad.Count == 0, checks.Count,
            bad.Count == 0 ? "self, foreign, pipe-vs-power, roofed, range, range edge, full: each refused/allowed as the bars need" : string.Join("; ", bad));

        // random: auto-link (MST) never joins two factions or two kinds, never exceeds range or maxLinks, never closes a loop
        int seed = 4403, n = 0; var rnd = new Random(seed); string why = null; List<AnchorInfo> worst = null;
        for (int trial = 0; trial < 600 && why == null; trial++)
        {
            int cnt = 2 + rnd.Next(14); var sel = new List<AnchorInfo>();
            for (int i = 0; i < cnt; i++)
                sel.Add(A(i + 1, rnd.Next(60), rnd.Next(60), rnd.Next(2), rnd.Next(4) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power, 1 + rnd.Next(4), rnd.Next(10) == 0));
            // a few pre-existing links between compatible anchors
            for (int i = 0; i + 1 < cnt; i += 3)
                if (AerialMath.CanLink(sel[i], sel[i + 1], R) == LinkVerdict.Ok) { sel[i].Linked.Add(sel[i + 1].Id); sel[i + 1].Linked.Add(sel[i].Id); }
            n++;
            var links = AerialMath.MinimumSpanningLinks(sel, R);
            var byId = sel.ToDictionary(s => s.Id);
            var deg = sel.ToDictionary(s => s.Id, s => s.Linked.Count);
            var uf = sel.ToDictionary(s => s.Id, s => s.Id);
            int F(int x) { while (uf[x] != x) x = uf[x]; return x; }
            foreach (var s in sel) foreach (int l in s.Linked) { int ra = F(s.Id), rb = F(l); if (ra != rb) uf[ra] = rb; }
            foreach (var (x, y) in links)
            {
                AnchorInfo p = byId[x], q = byId[y];
                if (p.Faction != q.Faction) why = "joined two factions";
                else if (p.Kind != q.Kind) why = "joined pipe and power";
                else if (p.Roofed || q.Roofed) why = "linked a roofed anchor";
                else if (!AerialMath.InRange(p.X, p.Z, q.X, q.Z, R)) why = "out of range";
                else if (++deg[x] > p.MaxLinks || ++deg[y] > q.MaxLinks) why = "over maxLinks";
                else { int ra = F(x), rb = F(y); if (ra == rb) why = "closed a loop"; else uf[ra] = rb; }
                if (why != null) { worst = sel; why += " on (" + x + "," + y + ")"; break; }
            }
        }
        Row("autolink_random_respects_grid", "drawing_true_to_grid,overhead_spans", "random", why == null, n,
            "seed " + seed + (why == null ? ": no cross-faction, cross-kind, roofed, out-of-range, over-full or looping link" :
            ": " + why + " | anchors " + string.Join(" ", worst.Select(s => s.Id + "@" + s.X + "," + s.Z + "f" + s.Faction + (s.Kind == AerialLineKind.Pipe ? "P" : "W") + "m" + s.MaxLinks))));

        // watchdog: an UP span across two nets (or none) is repaired; a CUT span is meant to split, never repaired
        var reads = new List<SpanNetRead>
        {
            new SpanNetRead { Span = 1, NetA = 3, NetB = 3, State = SpanState.Up },
            new SpanNetRead { Span = 2, NetA = 3, NetB = 4, State = SpanState.Up },
            new SpanNetRead { Span = 3, NetA = -1, NetB = 4, State = SpanState.Up },
            new SpanNetRead { Span = 4, NetA = 3, NetB = 4, State = SpanState.Cut },
            new SpanNetRead { Span = 5, NetA = -1, NetB = -1, State = SpanState.Up },
        };
        var rep = AerialMath.WatchdogRepairs(reads);
        bool wok = rep.SequenceEqual(new[] { 2, 3, 5 });
        Row("watchdog_repairs_only_up_split", "drawing_true_to_grid,connectivity_truth,cut_live_and_dead_ends", "fixed", wok, reads.Count,
            "repairs " + string.Join(",", rep) + " (want 2,3,5: up spans not on one shared net; the cut span 4 stays split)");
    }

    // ---------------------------------------------------------------- fallen_span_on_ground / gravship_keeps_connections: what a removal does
    static void RemovalRows()
    {
        int seed = 4404, n = 0; var rnd = new Random(seed); string why = null;
        for (int trial = 0; trial < 3000 && why == null; trial++)
        {
            int id = 100; int cnt = rnd.Next(7);
            var spans = new List<(int, SpanState)>();
            for (int i = 0; i < cnt; i++) spans.Add((1 + rnd.Next(5), rnd.Next(3) == 0 ? SpanState.Cut : SpanState.Up));
            if (rnd.Next(8) == 0) spans.Add((id, SpanState.Up));          // a self-span never counts
            bool killed = rnd.Next(2) == 0; bool grav = rnd.Next(3) == 0;
            HashSet<int> aboard = grav ? new HashSet<int>(Enumerable.Range(1, 5).Where(_ => rnd.Next(2) == 0)) : null;
            n++;
            RemovalPlan p = AerialMath.PlanRemoval(id, killed, spans, aboard);
            var partners = new HashSet<int>(spans.Select(s => s.Item1).Where(x => x != id));
            string cs = " | id=100 killed=" + killed + " aboard=" + (aboard == null ? "null" : "{" + string.Join(",", aboard) + "}") +
                        " spans=" + string.Join(",", spans.Select(s => s.Item1 + (s.Item2 == SpanState.Up ? "U" : "C")));
            if (p.Reseed.Distinct().Count() != p.Reseed.Count) why = "a partner reseeded twice";
            else if (aboard == null || killed)
            {
                // every partner is reseeded (no side left net-less); killed = one fallen wire per UP span, none for a cut one
                if (!partners.SetEquals(p.Reseed)) why = "reseed " + string.Join(",", p.Reseed) + " != partners";
                int ups = spans.Count(s => s.Item1 != id && s.Item2 == SpanState.Up);
                int want = killed ? ups : 0;
                if (why == null && p.Fallen.Count != want) why = "fallen " + p.Fallen.Count + " want " + want;
                if (why == null && p.Fallen.Any(f => !partners.Contains(f.Survivor) || !f.TowardDead)) why = "a fallen wire lies at a non-partner or away from the dead mast";
                if (why == null && (p.Kept.Count > 0 || p.Grounded.Count > 0)) why = "kept/grounded outside a gravship lift";
            }
            else
            {
                // gravship lift: partners aboard keep their span, partners left behind are coiled; nothing falls (nothing died)
                var kept = new HashSet<int>(partners.Where(aboard.Contains));
                var grounded = new HashSet<int>(partners.Where(x => !aboard.Contains(x)));
                if (!kept.SetEquals(p.Kept)) why = "kept " + string.Join(",", p.Kept) + " want " + string.Join(",", kept);
                else if (!grounded.SetEquals(p.Grounded)) why = "grounded " + string.Join(",", p.Grounded) + " want " + string.Join(",", grounded);
                else if (p.Fallen.Count > 0) why = "a wire fell on a gravship lift";
                else if (!grounded.SetEquals(p.Reseed)) why = "reseed " + string.Join(",", p.Reseed) + " want the grounded " + string.Join(",", grounded);
                else if (p.Kept.Intersect(p.Grounded).Any()) why = "a partner both kept and grounded";
            }
            if (why != null) why += cs;
        }
        Row("removal_random_conserves_spans", "fallen_span_on_ground,downed_spans,gravship_keeps_connections,gravship_connectivity", "random", why == null, n,
            "seed " + seed + (why == null ? ": every partner reseeded once; killed drops one wire per up span, none per cut; gravship keeps aboard, coils the rest, drops none" : ": " + why));

        // fixed: dismantling coils, nothing falls (bar: a KILLED mast or a cut span leaves the wire on the ground)
        var d = AerialMath.PlanRemoval(1, false, new List<(int, SpanState)> { (2, SpanState.Up), (3, SpanState.Up) });
        var k = AerialMath.PlanRemoval(1, true, new List<(int, SpanState)> { (2, SpanState.Up), (3, SpanState.Cut) });
        bool ok = d.Fallen.Count == 0 && d.Reseed.Count == 2 && k.Fallen.Count == 1 && k.Fallen[0].Survivor == 2 && k.Reseed.Count == 2;
        Row("removal_fixed_killed_vs_dismantled", "fallen_span_on_ground,downed_spans", "fixed", ok, 2,
            "dismantled: fallen " + d.Fallen.Count + " (want 0); killed with one up and one cut span: fallen " + k.Fallen.Count + " (want 1, at 2)");

        // restring_cut_span: a re-string is a job, 300 ticks at speed 1, never instant, faster for a faster builder
        bool rok = AerialMath.RestringTicks(1.0) == 300 && AerialMath.RestringTicks(0) > 0 && AerialMath.RestringTicks(2.0) < AerialMath.RestringTicks(1.0)
                   && AerialMath.RestringTicks(1e9) >= 1 && AerialMath.RestringTicks(-5) > 0;
        Row("restring_job_ticks", "restring_cut_span,restring_job", "fixed", rok, 5,
            "ticks at speed 1 / 0 / 2 / 1e9 / -5: " + AerialMath.RestringTicks(1.0) + " / " + AerialMath.RestringTicks(0) + " / " +
            AerialMath.RestringTicks(2.0) + " / " + AerialMath.RestringTicks(1e9) + " / " + AerialMath.RestringTicks(-5));
    }

    // ---------------------------------------------------------------- fallen_span_on_ground: the fallen wire lies on the ground, never over a wall
    // one fallen-wire case: null when it holds, else why
    static double LastDepth;
    static string FallenCheck(HashSet<(int, int)> wall, P2 basePt, P2 top, P2 toward, double length, int s)
    {
        Func<int, int, bool> walkable = (x, z) => x >= 0 && z >= 0 && !wall.Contains((x, z));
        double dist = P2.Dist(basePt, toward);
        FallenLay l = AerialMath.LayFallen(top, basePt, toward, length, s, walkable);
        if (l.Pts.Count < 2) return "no cable laid";
        if (l.Pts[0].X != top.X || l.Pts[0].Z != top.Z) return "does not leave the insulator";
        if (!l.TipGrounded) return "the end never reaches the ground";
        var g = AerialMath.GroundPts(l).ToList();
        if (g.Count == 0) return "no grounded points";
        // a grounded point inside a wall cell beyond the first 0.75 cell = drawn across a wall
        foreach (P2 p in g)
            if (P2.Dist(p, basePt) > 0.75 + 1e-9 && !walkable((int)Math.Floor(p.X), (int)Math.Floor(p.Z)))
            {
                double fx = p.X - Math.Floor(p.X), fz = p.Z - Math.Floor(p.Z);
                double depth = Math.Min(Math.Min(fx, 1 - fx), Math.Min(fz, 1 - fz));   // how far inside the cell's edge
                LastDepth = Math.Max(LastDepth, depth);
                return "grounded point " + p + " in wall cell (" + (int)Math.Floor(p.X) + "," + (int)Math.Floor(p.Z) + "), " +
                       depth.ToString("0.000") + " cell inside its edge, blocked=" + l.Blocked + ", tip " + l.Tip;
            }
        // the tip is the last grounded point and LayTouches sees its cell (a shock contact at the live end)
        if (!AerialMath.LayTouches(l, (int)Math.Floor(l.Tip.X), (int)Math.Floor(l.Tip.Z))) return "LayTouches misses the tip cell";
        double gs = 0; for (int i = 1; i < g.Count; i++) gs += P2.Dist(g[i - 1], g[i]);
        // the ground part is laid with slack (bends, coils): bound it at 3x the cable so a runaway lay is caught
        if (gs > Math.Max(length, dist) * 3 + 2) return "ground run " + gs.ToString("0.0") + " vs cable " + length.ToString("0.0");
        return null;
    }

    static void FallenLayRows()
    {
        int seed = 4405, n = 0, fallsInWall = 0, firstFail = -1; double depthMax = 0; var rnd = new Random(seed); string why = null, shrunk = null;
        for (int trial = 0; trial < 2500; trial++)
        {
            // a random wall field; map cells are never negative in game: the mast stands at (30, 30) with the walls around it
            var wall = new HashSet<(int, int)>();
            int walls = rnd.Next(3) == 0 ? 0 : rnd.Next(40);
            for (int i = 0; i < walls; i++) wall.Add((30 + rnd.Next(-15, 16), 30 + rnd.Next(-15, 16)));
            wall.Remove((30, 30));
            var basePt = new P2(30.5, 30.5); double h = 1.5 + rnd.NextDouble();
            var top = new P2(basePt.X + (rnd.NextDouble() - 0.5) * 0.6, basePt.Z + h);
            double ang = rnd.NextDouble() * 2 * Math.PI, dist = 2 + rnd.NextDouble() * 12;
            var toward = new P2(basePt.X + Math.Cos(ang) * dist, basePt.Z + Math.Sin(ang) * dist);
            double length = dist * (rnd.Next(4) == 0 ? 0.5 + rnd.NextDouble() * 0.3 : 1.05);
            int s = rnd.Next(); n++;
            string w = FallenCheck(wall, basePt, top, toward, length, s);
            if (w == null) continue;
            fallsInWall++;
            depthMax = Math.Max(depthMax, LastDepth); LastDepth = 0;
            if (why != null) continue;
            firstFail = trial;
            why = w + " | base=" + basePt + " top=" + top + " toward=" + toward + " length=" + length.ToString("0.00") + " seed=" + s + " walls=" + wall.Count;
            // shrink: drop walls one at a time while it still fails, then report the smallest wall set
            var cur = new HashSet<(int, int)>(wall);
            bool changed = true;
            while (changed)
            {
                changed = false;
                foreach (var c in cur.ToList())
                {
                    var tryW = new HashSet<(int, int)>(cur); tryW.Remove(c);
                    if (FallenCheck(tryW, basePt, top, toward, length, s) != null) { cur = tryW; changed = true; }
                }
            }
            shrunk = "shrunk to " + cur.Count + " wall cell(s) {" + string.Join(" ", cur.Select(c => c.Item1 + "," + c.Item2)) + "}: " +
                     FallenCheck(cur, basePt, top, toward, length, s);
        }
        Row("fallen_random_lies_on_ground", "fallen_span_on_ground,downed_spans,fallen_wire_shocks_crossers,cords_meet_walls_at_face", "random", why == null, n,
            "seed " + seed + (why == null ? ": every fallen wire leaves its insulator, reaches the ground, never lies in a wall cell, its tip cell is a shock contact" :
            ": " + fallsInWall + " of " + n + " cases fail (deepest grounded point " + depthMax.ToString("0.000") + " cell inside a wall cell's edge); first at trial " + firstFail + ": " + why + " | " + shrunk));
        // deterministic: same seed, same lay (a reload redraws the same wire)
        Func<int, int, bool> open = (x, z) => true;
        var l1 = AerialMath.LayFallen(new P2(0.5, 2), new P2(0.5, 0.5), new P2(8, 3), 8.4, 77, open);
        var l2 = AerialMath.LayFallen(new P2(0.5, 2), new P2(0.5, 0.5), new P2(8, 3), 8.4, 77, open);
        bool same = l1.Pts.Count == l2.Pts.Count && l1.Pts.Zip(l2.Pts, (p, q) => p.X == q.X && p.Z == q.Z).All(x => x);
        Row("fallen_deterministic", "fallen_span_on_ground,statics_clear_between_games", "fixed", same, 1,
            "same inputs twice: " + (same ? "identical lay" : "different lays"));
    }

    // ---------------------------------------------------------------- fallen_wire_shocks_crossers: who the live wire takes
    static void ShockRows()
    {
        var bad = new List<string>(); int n = 0;
        foreach (bool flesh in new[] { true, false })
            foreach (bool dead in new[] { true, false })
                foreach (bool outAlready in new[] { true, false })
                    foreach (bool restring in new[] { true, false })
                    {
                        n++;
                        bool want = flesh && !dead && !outAlready && !restring;
                        if (AerialMath.ShockTakes(flesh, dead, outAlready, restring) != want)
                            bad.Add("flesh=" + flesh + " dead=" + dead + " out=" + outAlready + " restring=" + restring);
                    }
        Row("shock_truth_table", "fallen_wire_shocks_crossers,fallen_wire_shock", "fixed", bad.Count == 0, n,
            bad.Count == 0 ? "a living, standing flesh crosser on another job is shocked; the re-stringer of that wire, mechanoids, the dead and the already-out are not" : string.Join("; ", bad));
    }

    // ---------------------------------------------------------------- tap_steals_and_costs_goodwill
    static void TheftRows()
    {
        const double K = 1.0 / 60000 * 1; // any positive k
        // conservation: several taps on one victim in one tick never take more than the victim had to give
        int seed = 4406, n = 0; var rnd = new Random(seed); string why = null;
        for (int trial = 0; trial < 5000 && why == null; trial++)
        {
            double raw = (rnd.NextDouble() - 0.3) * 0.02, stored = rnd.Next(3) == 0 ? 0 : rnd.NextDouble() * 5;
            int taps = 1 + rnd.Next(5); double taken = 0; n++;
            var each = new List<double>();
            for (int i = 0; i < taps; i++)
            {
                double rate = 50 + 50 * rnd.Next(40);
                bool working = rnd.Next(6) != 0;
                double got = AerialMath.TapStolenPerTick(rate, raw, stored, K, false, true, taken, working);
                if (got < 0) { why = "negative take"; break; }
                if (got > rate * K + 1e-15) { why = "over the clamp's rate"; break; }
                if (!working && got != 0) { why = "a switched-off clamp took power"; break; }
                taken += got; each.Add(got);
            }
            double avail = raw + Math.Max(0, stored);
            if (why == null && taken > Math.Max(0, avail) + 1e-12) why = "taps took " + taken + " of " + avail;
            if (why != null) why += " | raw=" + raw + " stored=" + stored + " takes=" + string.Join(",", each);
        }
        Row("tap_random_conserves_power", "tap_steals_and_costs_goodwill,power_theft", "random", why == null, n,
            "seed " + seed + (why == null ? ": taps never take more than the victim had (gain + battery), nor over rate, nor when off" : ": " + why));

        // fixed: own net, taps disabled, NaN never steal; a plain tap on a powered neighbour does
        bool fok = AerialMath.TapStolenPerTick(500, 1, 0, K, true, true) == 0 && AerialMath.TapStolenPerTick(500, 1, 0, K, false, false) == 0 &&
                   AerialMath.TapStolenPerTick(double.NaN, 1, 0, K, false, true) == 0 && AerialMath.TapStolenPerTick(500, double.NaN, 0, K, false, true) == 0 &&
                   Math.Abs(AerialMath.TapStolenPerTick(500, 1, 0, K, false, true) - 500 * K) < 1e-15;
        Row("tap_fixed_steals_from_neighbour_only", "tap_steals_and_costs_goodwill,power_theft", "fixed", fok, 5,
            "own net 0, disabled 0, NaN rate 0, NaN gain 0, neighbour with surplus: rate*k");

        // spotted: within sight range with line of sight, awake, not ours
        bool sok = AerialMath.TheftSpotted(12, 12, true, true, false) && !AerialMath.TheftSpotted(12.01, 12, true, true, false) &&
                   !AerialMath.TheftSpotted(3, 12, false, true, false) && !AerialMath.TheftSpotted(3, 12, true, false, false) &&
                   !AerialMath.TheftSpotted(3, 12, true, true, true) && !AerialMath.TheftSpotted(double.NaN, 12, true, true, false);
        Row("theft_spotted_rules", "tap_steals_and_costs_goodwill,power_theft", "fixed", sok, 6, "edge of sight, beyond, no LOS, asleep, held by us, NaN");

        // goodwill drains steadily: total charged = perDay x whole days spent draining, idle time free; swept over the slider 0-10
        int gseed = 4407; var gr = new Random(gseed); string gwhy = null; int gn = 0;
        foreach (int perDay in Enumerable.Range(0, 11))
        {
            int drain = 0, charged = 0, drained = 0; const int TPD = 60000;
            for (int step = 0; step < 4000; step++)
            {
                int ticks = gr.Next(1, 2500); bool draining = gr.Next(3) != 0; gn++;
                int before = drain;
                charged += AerialMath.TheftGoodwillAccrue(ref drain, ticks, draining, perDay, TPD);
                if (draining) drained += ticks; else if (drain != before) { gwhy = "idle ticks accrued"; break; }
            }
            int want = -perDay * (drained / TPD);
            if (gwhy == null && charged != want) gwhy = "perDay " + perDay + ": charged " + charged + " want " + want + " over " + drained + " drained ticks";
            if (gwhy != null) break;
        }
        Row("theft_goodwill_sweep_steady", "tap_steals_and_costs_goodwill,power_theft,mod_settings", "sweep", gwhy == null, gn,
            "seed " + gseed + ", perDay 0..10" + (gwhy == null ? ": charge = perDay x whole drained days, remainder carried, idle free" : ": " + gwhy));
    }

    // ---------------------------------------------------------------- settings_switch_cleanly: pipe poles have their own switch
    static void KindRows()
    {
        var bad = new List<string>(); int n = 0;
        foreach (bool pw in new[] { true, false })
            foreach (bool pp in new[] { true, false })
                foreach (bool setting in new[] { true, false })
                {
                    n++;
                    if (AerialKinds.KindOn(AerialLineKind.Power, pw, pp) != pw) bad.Add("power anchor follows pipe switch");
                    if (AerialKinds.KindOn(AerialLineKind.Pipe, pw, pp) != pp) bad.Add("pipe pole follows power switch");
                    if (AerialKinds.KindBehaviour(AerialLineKind.Power, pw, pp, setting) != (pw && setting)) bad.Add("power behaviour");
                    if (AerialKinds.KindBehaviour(AerialLineKind.Pipe, pw, pp, setting) != pp) bad.Add("pipe behaviour reads power settings");
                }
        Row("kind_switch_sweep", "settings_switch_cleanly,pipe_pole_switch,mod_settings", "sweep", bad.Count == 0, n,
            bad.Count == 0 ? "every switch combination: power anchors obey the power master (and their setting), pipe poles only their own switch" : string.Join("; ", bad.Distinct()));

        // range / sag clamps over the slider ranges and beyond, NaN included; a pipe never carries power, sways, drips or multi-strands
        string why = null; int rn = 0;
        foreach (float v in new[] { float.NaN, -1f, 0f, 2f, 4f, 8f, 12f, 20f, 30f, 40f, 41f, 1e9f })
        {
            rn++;
            float pr = AerialKinds.RangeFor(AerialLineKind.Power, v, 12f), pi = AerialKinds.RangeFor(AerialLineKind.Pipe, 20f, v);
            if (!(pr >= AerialKinds.PowerSpanMin && pr <= AerialKinds.PowerSpanMax)) why = "power range " + pr + " for " + v;
            if (!(pi >= AerialKinds.PipeSpanMin && pi <= AerialKinds.PipeSpanMax)) why = "pipe range " + pi + " for " + v;
            float ps = AerialKinds.SagFor(AerialLineKind.Power, v / 100f, 0.02f);
            if (float.IsNaN(ps) || ps < 0) why = "power sag " + ps + " for " + v;
        }
        if (AerialKinds.CarriesPower(AerialLineKind.Pipe) || AerialKinds.Sways(AerialLineKind.Pipe) || AerialKinds.Drips(AerialLineKind.Pipe, true) ||
            AerialKinds.StrandCap(AerialLineKind.Pipe, 3) != 1) why = "a pipe span acts as a wire";
        if (!AerialKinds.CarriesPower(AerialLineKind.Power) || AerialKinds.StrandCap(AerialLineKind.Power, 3) != 3) why = "a power span lost its power or strands";
        Row("kind_clamps_sweep", "settings_switch_cleanly,mod_settings,overhead_spans", "sweep", why == null, rn,
            why ?? "span range and sag stay in bounds for NaN, negative and huge settings; a pipe span never carries power or sways");
    }

    // ---------------------------------------------------------------- four_looks_one_run: a placement beside a styled run must flood
    static void GateRows()
    {
        var none = new ConduitPlacementGate.Neighbour[0];
        var plain = new[] { new ConduitPlacementGate.Neighbour(false, false) };
        var styled = new[] { new ConduitPlacementGate.Neighbour(false, false), new ConduitPlacementGate.Neighbour(true, false) };
        var bridge = new[] { new ConduitPlacementGate.Neighbour(false, true) };
        bool ok = ConduitPlacementGate.CanSkip(null, none) && ConduitPlacementGate.CanSkip(null, plain) &&
                  !ConduitPlacementGate.CanSkip(null, styled) && !ConduitPlacementGate.CanSkip(null, bridge) &&
                  !ConduitPlacementGate.CanSkip("Modern", plain);
        Row("placement_gate_floods_styled_runs", "four_looks_one_run,four_styles", "fixed", ok, 5,
            "skip only when the new conduit has no look and no neighbour is styled or a bridge conduit");
    }
}
