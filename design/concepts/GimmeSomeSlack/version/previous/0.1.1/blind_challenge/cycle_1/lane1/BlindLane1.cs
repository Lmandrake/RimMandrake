// Blind lane 1, GimmeSomeSlack 0.1.1, cycle 1: properties of the aerial kernel (AerialMath.cs) written from the bars
// alone (tree.json, sheet.md, record.json inventory words) and the shipped settings ranges (AerialSettings.cs sliders),
// before any builder test was read. Prints one JSON row per line. Exit 0 = no FAIL row, 1 = a FAIL row.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.GimmeSomeSlack.Aerial;

static class BlindLane1
{
    static readonly List<string> Rows = new List<string>();
    static bool AnyFail;
    static string J(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";
    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") AnyFail = true;
        Rows.Add("{\"id\":" + J(id) + ",\"bars\":[" + string.Join(",", bars.Select(J)) + "],\"kind\":" + J(kind) +
                 ",\"verdict\":" + J(verdict) + ",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }
    // a property over many cases: the first failing case, its seed, and the smallest failing case after shrinking
    class Prop { public int Cases, Fails; public string First, Smallest; public double SmallSize = double.MaxValue;
        public void Fail(string c, double size) { Fails++; if (First == null) First = c; if (size < SmallSize) { SmallSize = size; Smallest = c; } }
        public string V => Fails == 0 ? "PASS" : "FAIL";
        public string D(string what) => what + (Fails == 0 ? "" : "; FAILS " + Fails + "/" + Cases + "; first " + First + "; smallest " + Smallest); }

    static AnchorInfo A(int id, int x, int z, int fac = 0, int max = 6, bool roof = false, AerialLineKind k = AerialLineKind.Power, bool anchor = true)
        => new AnchorInfo { Id = id, X = x, Z = z, Faction = fac, MaxLinks = max, Roofed = roof, Kind = k, IsAnchor = anchor };

    const int Seed = 20261120;
    static readonly float[] MaxSpanSweep = Enumerable.Range(8, 33).Select(i => (float)i).ToArray(); // slider 8..40, rounded
    static readonly float[] SagSweep = { 0f, 0.01f, 0.03f, 0.06f, 0.09f, 0.12f, 0.15f };           // slider 0..0.15

    static int Main()
    {
        var rng = new Random(Seed);
        Links(rng); AutoLink(rng); Mst(rng); Curves(rng); Kinds(); Sway(rng); Removal(rng); Watchdog(rng);
        Fallen(rng); Shock(rng); Blast(rng); Tap(rng); Theft(rng); Restring();
        foreach (string r in Rows) Console.WriteLine(r);
        return AnyFail ? 1 : 0;
    }

    // ---------------------------------------------------------------- spans: the three bad links refused with their reasons
    static void Links(Random rng)
    {
        var bars = new[] { "spans_above_everything", "overhead_spans", "no_roof_over_pole" };
        var fx = new List<(string, LinkVerdict, LinkVerdict)>();
        void C(string n, AnchorInfo a, AnchorInfo b, double r, LinkVerdict want) => fx.Add((n, AerialMath.CanLink(a, b, r), want));
        C("self", A(1, 0, 0), A(1, 0, 0), 20, LinkVerdict.Self);
        C("battery (not an anchor)", A(1, 0, 0), A(2, 3, 0, anchor: false), 20, LinkVerdict.NotAnchor);
        C("hostile pole", A(1, 0, 0), A(2, 3, 0, fac: 1), 20, LinkVerdict.Foreign);
        C("21 cells at range 20", A(1, 0, 0), A(2, 21, 0), 20, LinkVerdict.OutOfRange);
        C("exactly at range 20", A(1, 0, 0), A(2, 20, 0), 20, LinkVerdict.Ok);
        C("diagonal 15,15 at range 20 (21.2)", A(1, 0, 0), A(2, 15, 15), 20, LinkVerdict.OutOfRange);
        C("roofed target", A(1, 0, 0), A(2, 5, 0, roof: true), 20, LinkVerdict.Roofed);
        C("roofed self", A(1, 0, 0, roof: true), A(2, 5, 0), 20, LinkVerdict.Roofed);
        C("power to pipe pole", A(1, 0, 0), A(2, 5, 0, k: AerialLineKind.Pipe), 20, LinkVerdict.WrongKind);
        var full = A(1, 0, 0, max: 1); full.Linked.Add(9);
        C("self full", full, A(2, 5, 0), 20, LinkVerdict.FullA);
        var fullB = A(2, 5, 0, max: 1); fullB.Linked.Add(9);
        C("target full", A(1, 0, 0), fullB, 20, LinkVerdict.FullB);
        var lk = A(1, 0, 0); lk.Linked.Add(2);
        C("already linked (one side recorded)", A(2, 5, 0), lk, 20, LinkVerdict.AlreadyLinked);
        var bad = fx.Where(f => f.Item2 != f.Item3).Select(f => f.Item1 + " got " + f.Item2 + " want " + f.Item3).ToList();
        Row("span_link_fixed_refusals", bars, "fixed", bad.Count == 0 ? "PASS" : "FAIL", fx.Count,
            "CanLink on named cases (self, battery, hostile, range edge, roof, pipe kind, full, linked)" + (bad.Count == 0 ? "" : ": " + string.Join("; ", bad)));
        // random: Ok exactly when every rule holds
        var p = new Prop();
        for (int i = 0; i < 20000; i++)
        {
            int s = rng.Next();
            var r2 = new Random(s);
            double range = MaxSpanSweep[r2.Next(MaxSpanSweep.Length)];
            var a = A(1, r2.Next(-30, 30), r2.Next(-30, 30), r2.Next(2), r2.Next(1, 4), r2.Next(10) == 0, r2.Next(8) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power, r2.Next(15) != 0);
            var b = A(2, r2.Next(-30, 30), r2.Next(-30, 30), r2.Next(2), r2.Next(1, 4), r2.Next(10) == 0, r2.Next(8) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power, r2.Next(15) != 0);
            for (int k = r2.Next(4); k > 0; k--) a.Linked.Add(100 + k);
            if (r2.Next(10) == 0) a.Linked.Add(2);
            p.Cases++;
            double d = Math.Sqrt((a.X - b.X) * (a.X - b.X) + (a.Z - b.Z) * (a.Z - b.Z));
            bool should = a.IsAnchor && b.IsAnchor && a.Kind == b.Kind && a.Faction == b.Faction && !a.Linked.Contains(2) &&
                          !a.Roofed && !b.Roofed && d <= range && a.Linked.Count < a.MaxLinks && b.Linked.Count < b.MaxLinks;
            bool ok = AerialMath.CanLink(a, b, range) == LinkVerdict.Ok;
            if (ok != should) p.Fail("seed " + s + " d=" + d.ToString("0.00") + " range " + range + " got " + AerialMath.CanLink(a, b, range), d);
        }
        Row("span_link_random_rules", bars, "random", p.V, p.Cases, p.D("seed " + Seed + ": CanLink Ok iff both anchors, one kind, one faction, unlinked, unroofed, within range (slider 8..40), both under MaxLinks"));
    }

    static void AutoLink(Random rng)
    {
        var p = new Prop();
        for (int i = 0; i < 3000; i++)
        {
            int s = rng.Next(); var r = new Random(s);
            int n = r.Next(1, 12); double range = MaxSpanSweep[r.Next(MaxSpanSweep.Length)];
            var self = A(0, r.Next(-20, 20), r.Next(-20, 20));
            var others = Enumerable.Range(1, n).Select(k => A(r.Next(1, 40) * 10 + k, r.Next(-25, 25), r.Next(-25, 25), r.Next(4) == 0 ? 1 : 0, 6, r.Next(8) == 0)).ToList();
            int got = AerialMath.AutoLinkPick(self, others, range);
            var ok = others.Where(o => AerialMath.CanLink(self, o, range) == LinkVerdict.Ok).ToList();
            int want = ok.Count == 0 ? -1 : ok.OrderBy(o => (long)(o.X - self.X) * (o.X - self.X) + (long)(o.Z - self.Z) * (o.Z - self.Z)).ThenBy(o => o.Id).First().Id;
            p.Cases++;
            if (got != want) p.Fail("seed " + s + " n=" + n + " got " + got + " want " + want, n);
        }
        Row("autolink_nearest_legal", new[] { "overhead_spans", "spans_above_everything" }, "random", p.V, p.Cases,
            p.D("seed " + Seed + ": auto-link on build picks the nearest legal anchor, ties to the lower id, -1 when none is legal (brute force)"));
    }

    static void Mst(Random rng)
    {
        var p = new Prop(); var cons = new Prop();
        for (int i = 0; i < 2000; i++)
        {
            int s = rng.Next(); var r = new Random(s);
            int n = r.Next(2, 10); double range = MaxSpanSweep[r.Next(MaxSpanSweep.Length)];
            bool capped = r.Next(3) == 0;
            var sel = Enumerable.Range(1, n).Select(k => A(k, r.Next(-30, 30), r.Next(-30, 30), r.Next(5) == 0 ? 1 : 0, capped ? r.Next(1, 3) : 99, r.Next(10) == 0, r.Next(10) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power)).ToList();
            // a few existing links (legal ones)
            for (int k = 0; k < r.Next(3); k++)
            {
                var x = sel[r.Next(n)]; var y = sel[r.Next(n)];
                if (AerialMath.CanLink(x, y, range) == LinkVerdict.Ok) { x.Linked.Add(y.Id); y.Linked.Add(x.Id); }
            }
            var res = AerialMath.MinimumSpanningLinks(sel, range);
            p.Cases++; cons.Cases++;
            var byId = sel.ToDictionary(a => a.Id);
            // union-find over existing links + result: no cycle, each edge legal, degree caps
            var par = sel.ToDictionary(a => a.Id, a => a.Id);
            int F(int x) { while (par[x] != x) x = par[x] = par[par[x]]; return x; }
            foreach (var a in sel) foreach (int l in a.Linked) if (par.ContainsKey(l)) { int ra = F(a.Id), rb = F(l); if (ra != rb) par[ra] = rb; }
            var deg = sel.ToDictionary(a => a.Id, a => a.Linked.Count);
            string why = null;
            var seen = new HashSet<(int, int)>();
            foreach (var (u, v) in res)
            {
                var a = byId[u]; var b = byId[v];
                if (!seen.Add((Math.Min(u, v), Math.Max(u, v)))) { why = "edge twice " + u + "-" + v; break; }
                if (a.Linked.Contains(v)) { why = "re-adds an existing link " + u + "-" + v; break; }
                if (AerialMath.CanLink(a, b, range) != LinkVerdict.Ok && !(a.Linked.Count >= a.MaxLinks || b.Linked.Count >= b.MaxLinks))
                { why = "illegal edge " + u + "-" + v + " " + AerialMath.CanLink(a, b, range); break; }
                if (F(u) == F(v)) { why = "cycle at " + u + "-" + v; break; }
                par[F(u)] = F(v); deg[u]++; deg[v]++;
                if (deg[u] > a.MaxLinks || deg[v] > b.MaxLinks) { why = "MaxLinks exceeded at " + u + "-" + v; break; }
            }
            if (why != null) { p.Fail("seed " + s + " n=" + n + ": " + why, n); continue; }
            if (!capped)
            {
                // spanning and minimal: against Kruskal by hand over legal pairs, components and total length must match
                var edges = new List<(long d, int a, int b)>();
                for (int x = 0; x < n; x++) for (int y = x + 1; y < n; y++)
                {
                    var a = sel[x]; var b = sel[y];
                    if (a.Linked.Contains(b.Id) || b.Linked.Contains(a.Id)) continue;
                    if (AerialMath.CanLink(a, b, range) != LinkVerdict.Ok) continue;
                    edges.Add(((long)(a.X - b.X) * (a.X - b.X) + (long)(a.Z - b.Z) * (a.Z - b.Z), a.Id, b.Id));
                }
                var par2 = sel.ToDictionary(a => a.Id, a => a.Id);
                int G(int x) { while (par2[x] != x) x = par2[x] = par2[par2[x]]; return x; }
                foreach (var a in sel) foreach (int l in a.Linked) if (par2.ContainsKey(l)) { int ra = G(a.Id), rb = G(l); if (ra != rb) par2[ra] = rb; }
                double wantW = 0; int wantN = 0;
                foreach (var e in edges.OrderBy(e => e.d)) { int ra = G(e.a), rb = G(e.b); if (ra == rb) continue; par2[ra] = rb; wantW += Math.Sqrt(e.d); wantN++; }
                double gotW = res.Sum(e => Math.Sqrt((double)(byId[e.Item1].X - byId[e.Item2].X) * (byId[e.Item1].X - byId[e.Item2].X) + (double)(byId[e.Item1].Z - byId[e.Item2].Z) * (byId[e.Item1].Z - byId[e.Item2].Z)));
                if (wantN != res.Count || Math.Abs(wantW - gotW) > 1e-6)
                    cons.Fail("seed " + s + " n=" + n + " edges " + res.Count + " want " + wantN + ", length " + gotW.ToString("0.00") + " want " + wantW.ToString("0.00"), n);
            }
        }
        Row("autolink_selected_forest_legal", new[] { "overhead_spans", "spans_above_everything" }, "random", p.V, p.Cases,
            p.D("seed " + Seed + ": 'auto-link selected' adds only legal, new, non-cyclic links within MaxLinks (with pre-existing links)"));
        Row("autolink_selected_spans_minimal", new[] { "overhead_spans" }, "random", cons.V, cons.Cases,
            cons.D("seed " + Seed + ": uncapped selections are joined as far as legal links allow (edge count = brute-force Kruskal), with the least total wire"));
    }

    // ---------------------------------------------------------------- span shape: sags, never taut upward, ends on the insulators
    static void Curves(Random rng)
    {
        var p = new Prop(); var drip = new Prop(); var shadow = new Prop();
        for (int i = 0; i < 6000; i++)
        {
            int s = rng.Next(); var r = new Random(s);
            float sag = SagSweep[r.Next(SagSweep.Length)];
            double ang = r.NextDouble() * 2 * Math.PI, len = 0.5 + r.NextDouble() * 39.5;
            var a = new P2(r.NextDouble() * 100, r.NextDouble() * 100); var b = new P2(a.X + len * Math.Cos(ang), a.Z + len * Math.Sin(ang));
            var c = AerialMath.SpanCurve(a, b, sag);
            p.Cases++;
            string why = null;
            if (c.Count < 2 || c[0].X != a.X || c[0].Z != a.Z || c[c.Count - 1].X != b.X || c[c.Count - 1].Z != b.Z) why = "ends not exactly on the insulators";
            double deepest = 0;
            double prevT = -1;
            for (int k = 0; k < c.Count && why == null; k++)
            {
                var q = c[k];
                if (double.IsNaN(q.X) || double.IsNaN(q.Z)) { why = "NaN point " + k; break; }
                // undo the droop: q = lerp(a,b,t) + (0, -drop). Solve t from X when the span is not vertical-on-screen, else from the order
                double t = Math.Abs(b.X - a.X) > 1e-6 ? (q.X - a.X) / (b.X - a.X) : double.NaN;
                if (!double.IsNaN(t))
                {
                    if (t < prevT - 1e-9) { why = "samples go backwards at " + k; break; }
                    prevT = t;
                    double chordZ = a.Z + (b.Z - a.Z) * t, drop = chordZ - q.Z;
                    if (drop < -1e-9) { why = "point " + k + " above its chord by " + (-drop).ToString("0.0000"); break; }
                    if (drop > sag * len + 1e-9) { why = "point " + k + " sags " + drop.ToString("0.000") + " > sag x len " + (sag * len).ToString("0.000"); break; }
                    deepest = Math.Max(deepest, drop);
                }
            }
            if (why == null && Math.Abs(b.X - a.X) > 0.5 && sag > 0 && len > 2 && deepest < 0.9 * sag * len)
                why = "deepest sag " + deepest.ToString("0.000") + " < 0.9 x sag x len " + (sag * len).ToString("0.000");
            if (why == null && sag > 0 && len > 2 && Math.Abs(b.X - a.X) > 0.5 && !(deepest > 0)) why = "no sag at sag " + sag;
            if (why != null) p.Fail("seed " + s + " len " + len.ToString("0.0") + " sag " + sag + ": " + why, len);
            // drip loops: off (depth 0) is the plain curve; on, the ends stay exactly on the insulators
            var d0 = AerialMath.SpanCurveDrip(a, b, sag, 0, 0.6);
            var d1 = AerialMath.SpanCurveDrip(a, b, sag, 0.15, 0.6);
            drip.Cases++;
            bool same = d0.Count == c.Count && d0.Zip(c, (x, y) => x.X == y.X && x.Z == y.Z).All(x => x);
            bool ends = d1.Count >= 2 && d1[0].X == a.X && d1[0].Z == a.Z && d1[d1.Count - 1].X == b.X && d1[d1.Count - 1].Z == b.Z && d1.All(q => !double.IsNaN(q.X + q.Z));
            if (!same || !ends) drip.Fail("seed " + s + " len " + len.ToString("0.0") + (same ? "" : " drip-off differs from the plain curve") + (ends ? "" : " drip-on ends off the insulators"), len);
            // the shadow joins the pole feet (ends = base + h k)
            double hA = 1 + r.NextDouble(), hB = 1 + r.NextDouble();
            var sh = AerialMath.SpanShadow(a, b, hA, hB, sag);
            shadow.Cases++;
            if (sh.Count < 2 || Math.Abs(sh[0].X - (a.X + hA * 0.10)) > 1e-9 || Math.Abs(sh[0].Z - (a.Z - hA * 0.16)) > 1e-9 ||
                Math.Abs(sh[sh.Count - 1].X - (b.X + hB * 0.10)) > 1e-9 || Math.Abs(sh[sh.Count - 1].Z - (b.Z - hB * 0.16)) > 1e-9)
                shadow.Fail("seed " + s + " len " + len.ToString("0.0"), len);
        }
        Row("span_curve_sags_ends_exact", new[] { "spans_above_everything", "overhead_spans" }, "sweep", p.V, p.Cases,
            p.D("seed " + Seed + ", sag swept over the slider 0..0.15, length 0.5..40: ends exactly A and B, every sample on or below its chord, no deeper than sag x length, deepest >= 0.9 x sag x length, samples in order"));
        Row("span_drip_loop_switch", new[] { "settings_switch_cleanly", "mod_settings" }, "sweep", drip.V, drip.Cases,
            drip.D("seed " + Seed + ": drip loops off draws the plain span exactly; on keeps both ends on the insulators"));
        Row("span_shadow_ends_at_feet", new[] { "spans_above_everything" }, "random", shadow.V, shadow.Cases,
            shadow.D("seed " + Seed + ": the ground shadow ends at each pole foot offset by its height (stated sun 0.10, -0.16)"));
        // fixed: default settings 0.06 on a 10-cell span sags 0.6 cell at the middle
        var m = AerialMath.SpanCurve(new P2(0, 0), new P2(10, 0), 0.06);
        double mid = m.Where(q => Math.Abs(q.X - 5) < 1e-6).Select(q => -q.Z).DefaultIfEmpty(double.NaN).First();
        Row("span_default_sag_fixed", new[] { "spans_above_everything" }, "fixed", Math.Abs(mid - 0.6) < 1e-9 ? "PASS" : "FAIL", 1,
            "shipped sag 0.06 on a 10-cell span: mid-span depth " + mid.ToString("0.0000") + " (want 0.6, above zero: the bar's 'sag depth above zero')");
    }

    // ---------------------------------------------------------------- per-kind numbers and the pipe poles' own switch
    static void Kinds()
    {
        var bad = new List<string>(); int cases = 0;
        foreach (bool powerOn in new[] { false, true })
            foreach (bool pipeOn in new[] { false, true })
                foreach (bool setting in new[] { false, true })
                {
                    cases++;
                    if (AerialKinds.KindOn(AerialLineKind.Power, powerOn, pipeOn) != powerOn) bad.Add("power anchor follows pipe switch " + powerOn + pipeOn);
                    if (AerialKinds.KindOn(AerialLineKind.Pipe, powerOn, pipeOn) != pipeOn) bad.Add("pipe pole follows power master " + powerOn + pipeOn);
                    if (AerialKinds.KindBehaviour(AerialLineKind.Power, powerOn, pipeOn, setting) != (powerOn && setting)) bad.Add("power behaviour " + powerOn + pipeOn + setting);
                    if (AerialKinds.KindBehaviour(AerialLineKind.Pipe, powerOn, pipeOn, setting) != pipeOn) bad.Add("pipe behaviour " + powerOn + pipeOn + setting);
                }
        Row("pipe_pole_own_switch", new[] { "pipe_pole_switch", "settings_switch_cleanly" }, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "all 8 switch states: a power anchor obeys the GSS master only, a pipe pole its own switch only and never the power one" + (bad.Count == 0 ? "" : ": " + string.Join("; ", bad.Distinct())));
        bad.Clear(); cases = 0;
        foreach (float v in MaxSpanSweep) { cases++; if (AerialKinds.RangeFor(AerialLineKind.Power, v, 12) != v) bad.Add("power range " + v + " -> " + AerialKinds.RangeFor(AerialLineKind.Power, v, 12)); }
        foreach (float v in SagSweep) { cases++; if (AerialKinds.SagFor(AerialLineKind.Power, v, 0.02f) != v) bad.Add("power sag " + v); }
        foreach (int ms in new[] { 1, 2, 3 })
            for (int ia = 1; ia <= 4; ia++) for (int ib = 1; ib <= 4; ib++)
                { cases++; int sc = AerialMath.StrandCount(ia, ib, ms); if (sc < 1 || sc > ms) bad.Add("strands " + ia + "x" + ib + " max " + ms + " -> " + sc); }
        cases++; if (AerialKinds.StrandCap(AerialLineKind.Pipe, 3) != 1 || AerialKinds.Drips(AerialLineKind.Pipe, true) || AerialKinds.Sways(AerialLineKind.Pipe) || AerialKinds.CarriesPower(AerialLineKind.Pipe)) bad.Add("pipe is not one rigid powerless run");
        cases++; if (float.IsNaN(AerialKinds.RangeFor(AerialLineKind.Power, float.NaN, 12)) || float.IsNaN(AerialKinds.SagFor(AerialLineKind.Power, float.NaN, 0))) bad.Add("NaN setting leaks");
        Row("span_settings_sweep", new[] { "mod_settings", "settings_switch_cleanly", "overhead_spans" }, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "maxSpan slider 8..40 is the link range unchanged, sag slider 0..0.15 the sag unchanged, maxStrands 1..3 bounds the wire count, a pipe span is one powerless rigid strand, NaN never leaks" + (bad.Count == 0 ? "" : ": " + string.Join("; ", bad.Take(8))));
    }

    static void Sway(Random rng)
    {
        var p = new Prop();
        for (int i = 0; i < 20000; i++)
        {
            int s = rng.Next(); var r = new Random(s);
            double wind = r.NextDouble() * 2.5, amp = r.NextDouble(), time = r.NextDouble() * 1000, t = r.NextDouble();
            p.Cases++;
            double v = AerialMath.Sway(t, time, wind, amp, s);
            double cap = 1.3 * amp * Math.Min(wind, 1.5) / 1.5 + 1e-9;
            string why = null;
            if (double.IsNaN(v) || Math.Abs(v) > cap) why = "|sway| " + v.ToString("0.0000") + " > cap " + cap.ToString("0.0000");
            if (Math.Abs(AerialMath.Sway(0, time, wind, amp, s)) > 1e-12 || Math.Abs(AerialMath.Sway(1, time, wind, amp, s)) > 1e-9) why = "moves at an insulator";
            if (AerialMath.Sway(t, time, 0, amp, s) != 0) why = "moves with no wind";
            double strength = r.NextDouble() * 2; double sag = 0.05 + r.NextDouble() * 3;
            foreach (WireSwayLook look in new[] { WireSwayLook.Pendulum, WireSwayLook.Rope, WireSwayLook.Gust })
            {
                var f = AerialMath.SwayFrame(look, time, wind, strength, sag, s, r.Next(3), r.NextDouble() * 100, r.NextDouble() * 100);
                AerialMath.SwayPose(f, 0, out double l0, out double r0); AerialMath.SwayPose(f, 1, out double l1, out double r1);
                if (Math.Abs(l0) + Math.Abs(r0) + Math.Abs(l1) + Math.Abs(r1) > 1e-9) why = look + " pose moves an insulator";
                var f0 = AerialMath.SwayFrame(look, time, wind, 0, sag, s, 0, 5, 5);
                AerialMath.SwayPose(f0, t, out double lz, out double rz);
                if (Math.Abs(lz) + Math.Abs(rz) > 1e-9) why = look + " moves with sway strength 0 (the slider's off end)";
                AerialMath.SwayPose(f, t, out double lt, out double rt);
                if (double.IsNaN(lt) || double.IsNaN(rt)) why = look + " NaN";
            }
            if (why != null) p.Fail("seed " + s + " wind " + wind.ToString("0.00") + " t " + t.ToString("0.00") + ": " + why, wind);
        }
        var modes = new List<string>();
        foreach (bool pref in new[] { false, true })
        {
            if (AerialMath.WireSwayPrefAllows(0, pref) != pref) modes.Add("Auto ignores the plant-sway preference");
            if (!AerialMath.WireSwayPrefAllows(1, pref)) modes.Add("CPU does not always sway");
            if (AerialMath.WireSwayPrefAllows(2, pref)) modes.Add("Off sways");
        }
        if (modes.Count > 0) { p.Fails++; p.First = (p.First ?? "") + " " + string.Join("; ", modes); }
        Row("sway_pinned_bounded_off", new[] { "spans_above_everything", "settings_switch_cleanly" }, "sweep", p.V, p.Cases,
            p.D("seed " + Seed + ": sway is 0 at both insulators, 0 with no wind, within 1.3 x amp x min(wind,1.5)/1.5; each of the three looks keeps the insulators still and stands still at strength 0; sway mode Auto/CPU/Off obeys the preference"));
    }

    // ---------------------------------------------------------------- a killed mast drops its spans, a dismantled one coils them
    static void Removal(Random rng)
    {
        var p = new Prop();
        for (int i = 0; i < 20000; i++)
        {
            int s = rng.Next(); var r = new Random(s);
            int id = 50, n = r.Next(0, 7);
            var spans = new List<(int, SpanState)>();
            for (int k = 0; k < n; k++) spans.Add((r.Next(10) == 0 ? id : r.Next(1, 8), r.Next(3) == 0 ? SpanState.Cut : SpanState.Up));
            bool killed = r.Next(2) == 0;
            HashSet<int> aboard = r.Next(3) == 0 ? new HashSet<int>(Enumerable.Range(1, 7).Where(_ => r.Next(2) == 0)) : null;
            var plan = AerialMath.PlanRemoval(id, killed, spans, aboard);
            var partners = spans.Where(x => x.Item1 != id).Select(x => x.Item1).Distinct().ToList();
            p.Cases++;
            string why = null;
            int upSpans = spans.Count(x => x.Item1 != id && x.Item2 == SpanState.Up);
            bool flight = aboard != null && !killed;
            var kept = flight ? partners.Where(aboard.Contains).ToList() : new List<int>();
            var mustReseed = partners.Except(kept).ToList();
            if (plan.Reseed.Distinct().Count() != plan.Reseed.Count) why = "a partner reseeded twice";
            else if (!new HashSet<int>(plan.Reseed).SetEquals(mustReseed)) why = "reseed " + string.Join(",", plan.Reseed) + " want " + string.Join(",", mustReseed);
            else if (killed && plan.Fallen.Count != upSpans) why = "killed: " + plan.Fallen.Count + " fallen for " + upSpans + " up spans";
            else if (!killed && plan.Fallen.Count != 0) why = "not killed but " + plan.Fallen.Count + " wires fell";
            else if (plan.Fallen.Any(f => f.Survivor == id || !f.TowardDead)) why = "a fallen wire lies on the dead anchor or away from it";
            else if (killed && plan.Fallen.GroupBy(f => f.Survivor).Any(g => g.Count() != spans.Count(x => x.Item1 == g.Key && x.Item2 == SpanState.Up))) why = "fallen per survivor != its up spans";
            else if (flight && (!new HashSet<int>(plan.Kept).SetEquals(kept) || plan.Grounded.Intersect(plan.Kept).Any() || !new HashSet<int>(plan.Grounded).SetEquals(partners.Except(kept))))
                why = "flight: kept " + string.Join(",", plan.Kept) + " grounded " + string.Join(",", plan.Grounded);
            else if (!flight && (plan.Kept.Count > 0 || plan.Grounded.Count > 0)) why = "kept/grounded outside a flight";
            if (why != null) p.Fail("seed " + s + " n " + n + " killed " + killed + " aboard " + (aboard == null ? "null" : string.Join(",", aboard)) + ": " + why, n);
        }
        Row("removal_plan_conserves_spans", new[] { "fallen_span_on_ground", "downed_spans", "gravship_keeps_connections", "gravship_connectivity" }, "random", p.V, p.Cases,
            p.D("seed " + Seed + ": every partner re-seeded once; a killed mast drops exactly one wire per UP span onto its survivor, none per CUT span; a dismantled one drops none; on lift-off the partners aboard keep their span and the rest are taken down, never both, nothing falls"));
    }

    static void Watchdog(Random rng)
    {
        var p = new Prop();
        for (int i = 0; i < 5000; i++)
        {
            int s = rng.Next(); var r = new Random(s);
            var reads = Enumerable.Range(0, r.Next(0, 8)).Select(k => new SpanNetRead { Span = k, NetA = r.Next(-1, 3), NetB = r.Next(-1, 3), State = r.Next(3) == 0 ? SpanState.Cut : SpanState.Up }).ToList();
            var got = new HashSet<int>(AerialMath.WatchdogRepairs(reads));
            var want = new HashSet<int>(reads.Where(x => x.State == SpanState.Up && !(x.NetA >= 0 && x.NetA == x.NetB)).Select(x => x.Span));
            p.Cases++;
            if (!got.SetEquals(want)) p.Fail("seed " + s, reads.Count);
        }
        Row("watchdog_repairs_only_broken_up_spans", new[] { "overhead_spans", "spans_above_everything", "downed_spans" }, "random", p.V, p.Cases,
            p.D("seed " + Seed + ": an UP span is repaired exactly when its ends are not on one shared net; a CUT span is never rejoined"));
    }

    // ---------------------------------------------------------------- a fallen wire lies on the ground and stops at walls
    static void Fallen(Random rng)
    {
        var p = new Prop(); var open = new Prop(); double maxDepth = 0;
        for (int i = 0; i < 6000; i++)
        {
            int s = rng.Next(); var r = new Random(s);
            int W = 40;
            var wall = new bool[W, W];
            int walls = r.Next(0, 4);
            for (int k = 0; k < walls; k++)
            {
                bool vert = r.Next(2) == 0; int at = r.Next(5, 35), from = r.Next(0, 30), to = from + r.Next(3, 15);
                for (int q = from; q < Math.Min(W, to); q++) { if (vert) wall[at, q] = true; else wall[q, at] = true; }
            }
            Func<int, int, bool> walk = (x, z) => x >= 0 && z >= 0 && x < W && z < W && !wall[x, z];
            var basePt = new P2(20.5, 20.5);
            if (!walk(20, 20)) continue;
            var top = new P2(20.5 + (r.NextDouble() - 0.5) * 0.6, 20.5 + 1.5 + r.NextDouble());
            double ang = r.NextDouble() * 2 * Math.PI, dist = 2 + r.NextDouble() * 16;
            var toward = new P2(basePt.X + dist * Math.Cos(ang), basePt.Z + dist * Math.Sin(ang));
            double length = dist * 1.05;
            var lay = AerialMath.LayFallen(top, basePt, toward, length, s, walk);
            p.Cases++;
            string why = null;
            if (lay.Pts.Count == 0 || lay.Pts[0].X != top.X || lay.Pts[0].Z != top.Z) why = "does not start at the insulator";
            for (int k = Math.Max(0, lay.GroundFrom); lay.GroundFrom >= 0 && k < lay.Pts.Count && why == null; k++)
            {
                var q = lay.Pts[k];
                if (double.IsNaN(q.X + q.Z)) { why = "NaN"; break; }
                if (P2.Dist(q, basePt) <= 0.75) continue; // the bar's wall face: a bracket's base sits on its wall
                int cx = (int)Math.Floor(q.X), cz = (int)Math.Floor(q.Z);
                if (!walk(cx, cz))
                {
                    // how deep into the wall: distance to the nearest edge shared with a walkable neighbour (diagnostic only)
                    double dep = double.MaxValue;
                    if (walk(cx - 1, cz)) dep = Math.Min(dep, q.X - cx); if (walk(cx + 1, cz)) dep = Math.Min(dep, cx + 1 - q.X);
                    if (walk(cx, cz - 1)) dep = Math.Min(dep, q.Z - cz); if (walk(cx, cz + 1)) dep = Math.Min(dep, cz + 1 - q.Z);
                    maxDepth = Math.Max(maxDepth, dep);
                    why = "ground point " + k + " " + q + " on a wall cell, " + dep.ToString("0.000") + " cell past the face";
                }
            }
            var tip = lay.Pts[lay.Pts.Count - 1];
            if (why == null && (lay.Tip.X != tip.X || lay.Tip.Z != tip.Z)) why = "Tip is not the last point";
            if (why != null) p.Fail("seed " + s + " walls " + walls + " dist " + dist.ToString("0.0") + ": " + why, walls * 100 + dist);
            if (walls == 0)
            {
                open.Cases++;
                if (!lay.TipGrounded || lay.Blocked) open.Fail("seed " + s + " dist " + dist.ToString("0.0") + " grounded " + lay.TipGrounded + " blocked " + lay.Blocked, dist);
            }
        }
        Row("fallen_wire_never_on_a_wall", new[] { "fallen_span_on_ground", "downed_spans", "cords_meet_walls_at_face" }, "random", p.V, p.Cases,
            p.D("seed " + Seed + ": random walls on a 40x40 grid; a fallen wire starts at its insulator, ends at its Tip, and no grounded point past 0.75 cell from the base lies on an unwalkable cell" + (p.Fails > 0 ? "; deepest point past a wall face " + maxDepth.ToString("0.000") + " cell" : "")));
        Row("fallen_wire_reaches_ground_in_open", new[] { "fallen_span_on_ground", "downed_spans" }, "random", open.V, open.Cases,
            open.D("seed " + Seed + ": with no wall in the way a cut span (2..18 cells) lies on the ground, not hanging, and is not Blocked"));
    }

    static void Shock(Random rng)
    {
        var bad = new List<string>(); int cases = 0;
        foreach (bool flesh in new[] { false, true }) foreach (bool dead in new[] { false, true }) foreach (bool outd in new[] { false, true }) foreach (bool rs in new[] { false, true })
        {
            cases++;
            bool want = flesh && !dead && !outd && !rs;
            if (AerialMath.ShockTakes(flesh, dead, outd, rs) != want) bad.Add("flesh " + flesh + " dead " + dead + " out " + outd + " restring " + rs);
        }
        Row("shock_truth_table", new[] { "fallen_wire_shocks_crossers", "fallen_wire_shock" }, "fixed", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "16 cases: only a living, conscious flesh pawn that is not the re-stringer of this wire is shocked" + (bad.Count == 0 ? "" : ": " + string.Join("; ", bad)));
        // contacts are the grounded points, never the hanging part
        var p = new Prop();
        for (int i = 0; i < 3000; i++)
        {
            int s = rng.Next(); var r = new Random(s);
            var basePt = new P2(20.5, 20.5); var top = new P2(20.5, 22.5);
            double ang = r.NextDouble() * 2 * Math.PI, dist = 2 + r.NextDouble() * 14;
            var lay = AerialMath.LayFallen(top, basePt, new P2(basePt.X + dist * Math.Cos(ang), basePt.Z + dist * Math.Sin(ang)), dist * 1.05, s, (x, z) => true);
            p.Cases++;
            var gp = AerialMath.GroundPts(lay).ToList();
            string why = null;
            if (gp.Count == 0) why = "no ground contact";
            foreach (var q in gp) if (!AerialMath.LayTouches(lay, (int)Math.Floor(q.X), (int)Math.Floor(q.Z))) { why = "ground point " + q + " not a contact"; break; }
            if (why == null && AerialMath.LayTouches(lay, 200, 200)) why = "far cell touches";
            for (int k = 0; k < lay.Pts.Count && why == null; k++)
                if (AerialMath.FallenPointOnGround(lay, k) != (lay.GroundFrom >= 0 && k >= lay.GroundFrom)) why = "on-ground flag " + k;
            if (why != null) p.Fail("seed " + s + " dist " + dist.ToString("0.0") + ": " + why, dist);
        }
        Row("shock_contacts_are_ground_points", new[] { "fallen_wire_shocks_crossers", "fallen_wire_shock" }, "random", p.V, p.Cases,
            p.D("seed " + Seed + ": every grounded point of a fallen wire, its tip included, is a contact cell; a far cell is not"));
        // knockback: a free neighbour or nothing; never into a blocked cell
        var kb = new Prop();
        for (int i = 0; i < 5000; i++)
        {
            int s = rng.Next(); var r = new Random(s);
            var blocked = new HashSet<(int, int)>(AerialMath.Ring8.Where(_ => r.Next(3) == 0));
            int ax = r.Next(-3, 4), az = r.Next(-3, 4);
            var d = AerialMath.KnockbackDir(ax, az, r.Next(8), (x, z) => !blocked.Contains((x, z)));
            kb.Cases++;
            if (d.HasValue && (blocked.Contains(d.Value) || !AerialMath.Ring8.Contains(d.Value))) kb.Fail("seed " + s + " -> " + d, blocked.Count);
            if (!d.HasValue && blocked.Count < 8) kb.Fail("seed " + s + " none chosen with " + (8 - blocked.Count) + " free", blocked.Count);
        }
        Row("shock_knockback_free_cell", new[] { "fallen_wire_shocks_crossers" }, "random", kb.V, kb.Cases,
            kb.D("seed " + Seed + ": a shock throws a pawn to a free neighbour cell, never into a blocked one, and finds one whenever any is free"));
    }

    static void Blast(Random rng)
    {
        var p = new Prop();
        var kinds = new List<string>();
        foreach (bool harms in new[] { false, true }) foreach (bool kin in new[] { false, true }) foreach (bool cut in new[] { false, true }) foreach (bool sw in new[] { false, true })
        {
            var k = AerialMath.BlastKindFor(harms, kin, 10, cut, sw);
            var want = !harms ? AerialMath.BlastKind.None : kin ? (sw ? AerialMath.BlastKind.Sway : AerialMath.BlastKind.None) : (cut ? AerialMath.BlastKind.Cut : AerialMath.BlastKind.None);
            if (k != want) kinds.Add(harms + "/" + kin + "/" + cut + "/" + sw + " -> " + k);
        }
        for (int i = 0; i < 20000; i++)
        {
            int s = rng.Next(); var r = new Random(s);
            var a = new P2(r.NextDouble() * 40, r.NextDouble() * 40); var b = new P2(r.NextDouble() * 40, r.NextDouble() * 40); var c = new P2(r.NextDouble() * 40, r.NextDouble() * 40);
            double rad = r.NextDouble() * 8, hp = 1 + r.NextDouble() * 100, dmg = r.NextDouble() * 150;
            var kind = (AerialMath.BlastKind)r.Next(3);
            var res = AerialMath.BlastSpan(a, b, c, rad, hp, dmg, kind);
            p.Cases++;
            string why = null;
            bool hit = AerialMath.SpanHit(a, b, c, rad);
            if (kind == AerialMath.BlastKind.None && (res.Hit || res.Cut || res.Hp != hp)) why = "no-kind blast touched the span";
            else if (!hit && (res.Hit || res.Cut || res.Hp != hp || res.Kick != 0)) why = "blast outside its radius touched the span";
            else if (kind == AerialMath.BlastKind.Cut && hit && (res.Hp > hp || res.Cut != (res.Hp <= 0) || res.Hp < hp - dmg - 1e-9 || res.Hp > hp - 0.2 * dmg + 1e-9)) why = "cut hp " + res.Hp.ToString("0.00") + " of " + hp.ToString("0.00") + " dmg " + dmg.ToString("0.00");
            else if (kind == AerialMath.BlastKind.Sway && hit && (res.Cut || res.Hp != hp || res.Kick < AerialMath.BlastKickFloor - 1e-9 || res.Kick > 1 + 1e-9 || Math.Abs(res.Side) != 1)) why = "sway blast wounded or kick " + res.Kick;
            for (int age = 0; age < 400 && why == null; age += 37)
            {
                double v0 = AerialMath.BlastSway(0, age, 1, 1, 1, s), v1 = AerialMath.BlastSway(1, age, 1, 1, 1, s);
                if (v0 != 0 || v1 != 0) why = "blast sway moves an insulator";
                if (age >= AerialMath.BlastSwayTicks && AerialMath.BlastSway(0.5, age, 1, 1, 1, s) != 0) why = "still swinging at " + age;
            }
            if (why != null) p.Fail("seed " + s + " kind " + kind + ": " + why, rad);
        }
        if (kinds.Count > 0) { p.Fails++; p.First = string.Join("; ", kinds) + " " + p.First; }
        Row("blast_cuts_inside_radius_only", new[] { "downed_spans", "fallen_span_on_ground", "settings_switch_cleanly" }, "random", p.V, p.Cases,
            p.D("seed " + Seed + ": a cutting blast wounds only a span its radius reaches, by 20..100% of its damage, parting it exactly at hp <= 0; a kinetic blast sways without wounding (kick 0.35..1); explosionsCut/kineticSway off stop each; the swing stays off the insulators and ends at 180 ticks"));
    }

    // ---------------------------------------------------------------- the tap: steals, never creates, shares one surplus
    static void Tap(Random rng)
    {
        var p = new Prop(); var share = new Prop();
        const double k = 1.0 / 60000.0 * 1; // any positive watts-to-watt-days factor
        for (int i = 0; i < 20000; i++)
        {
            int s = rng.Next(); var r = new Random(s);
            double rate = 50 + 50 * r.Next(0, 40), gain = (r.NextDouble() - 0.3) * 0.05, stored = r.Next(3) == 0 ? 0 : r.NextDouble() * 10 - 1;
            bool same = r.Next(8) == 0, en = r.Next(8) != 0, working = r.Next(8) != 0;
            double others = r.NextDouble() * 0.02;
            double got = AerialMath.TapStolenPerTick(rate, gain, stored, k, same, en, others, working);
            double avail = gain - others + Math.Max(0, stored);
            p.Cases++;
            string why = null;
            if (double.IsNaN(got) || got < 0) why = "negative or NaN " + got;
            else if (got > rate * k + 1e-15) why = "over the clamp rate";
            else if (got > Math.Max(0, avail) + 1e-15) why = "more than the victim has after other taps: " + got + " > " + avail;
            else if ((same || !en || !working) && got != 0) why = "takes while off, broken or from our own net";
            else if (!same && en && working && avail > 0 && Math.Abs(got - Math.Min(rate * k, avail)) > 1e-15) why = "takes less than it may";
            if (why != null) p.Fail("seed " + s + ": " + why, rate);
            // several taps on one victim in one tick: the sum is the victim's to give, never more
            int nt = r.Next(1, 6); double taken = 0;
            for (int t = 0; t < nt; t++) taken += AerialMath.TapStolenPerTick(50 + 50 * r.Next(0, 40), gain, stored, k, false, true, taken, true);
            share.Cases++;
            if (taken > Math.Max(0, gain + Math.Max(0, stored)) + 1e-12) share.Fail("seed " + s + " " + nt + " taps took " + taken + " of " + (gain + Math.Max(0, stored)), nt);
        }
        var nan = new List<string>();
        if (AerialMath.TapStolenPerTick(double.NaN, 1, 1, k, false, true) != 0) nan.Add("NaN rate");
        if (AerialMath.TapStolenPerTick(double.PositiveInfinity, 1, 1, k, false, true) != 0) nan.Add("infinite rate");
        if (AerialMath.TapStolenPerTick(500, double.NaN, 1, k, false, true) != 0) nan.Add("NaN gain");
        if (nan.Count > 0) { p.Fails++; p.First = string.Join(",", nan) + " " + p.First; }
        Row("tap_steals_never_creates", new[] { "tap_steals_and_costs_goodwill", "power_theft" }, "random", p.V, p.Cases,
            p.D("seed " + Seed + ", tapRate over the slider 50..2000 step 50: never negative or NaN, never over rate x k, never over what the victim has left after other taps, all of that when it may, nothing when off, broken or on our own net"));
        Row("tap_shared_surplus_conserved", new[] { "tap_steals_and_costs_goodwill", "power_theft" }, "random", share.V, share.Cases,
            share.D("seed " + Seed + ": 1..5 taps on one victim in one tick take together no more than its gain plus stored energy (nothing created)"));
    }

    static void Theft(Random rng)
    {
        var p = new Prop(); var gw = new Prop();
        for (int i = 0; i < 20000; i++)
        {
            int s = rng.Next(); var r = new Random(s);
            double sight = r.Next(3, 31), dist = r.NextDouble() * 40; bool los = r.Next(4) != 0, up = r.Next(4) != 0, held = r.Next(6) == 0;
            bool want = los && up && !held && dist <= sight;
            p.Cases++;
            if (AerialMath.TheftSpotted(dist, sight, los, up, held) != want) p.Fail("seed " + s + " dist " + dist.ToString("0.0") + " sight " + sight, dist);
            // the steady leak: over any run of draining and idle stretches, goodwill falls perDay per whole draining day, remainder carried
            int perDay = r.Next(0, 11), tpd = 60000, drain = 0, total = 0, drainedTicks = 0;
            int steps = r.Next(1, 30);
            for (int t = 0; t < steps; t++)
            {
                int ticks = r.Next(0, 90000); bool draining = r.Next(4) != 0;
                total += AerialMath.TheftGoodwillAccrue(ref drain, ticks, draining, perDay, tpd);
                if (draining && ticks > 0) drainedTicks += ticks;
            }
            gw.Cases++;
            int wantTotal = -(drainedTicks / tpd) * perDay;
            if (total != wantTotal || drain != drainedTicks % tpd || total > 0)
                gw.Fail("seed " + s + " perDay " + perDay + " drained " + drainedTicks + " total " + total + " want " + wantTotal + " carry " + drain, steps);
        }
        Row("theft_witness_rules", new[] { "tap_steals_and_costs_goodwill", "power_theft" }, "random", p.V, p.Cases,
            p.D("seed " + Seed + ", sight range over the slider 3..30: a witness catches the clamp only awake and up, not held by us, with line of sight, within range"));
        Row("theft_goodwill_leak_conserved", new[] { "tap_steals_and_costs_goodwill", "power_theft" }, "sweep", gw.V, gw.Cases,
            gw.D("seed " + Seed + ", goodwill per day over the slider 0..10: total change = -perDay x whole draining days, idle time accrues nothing, the remainder is carried, never a gain"));
    }

    static void Restring()
    {
        var bad = new List<string>(); int prev = int.MaxValue, cases = 0;
        foreach (double sp in new[] { 0.0, 0.05, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0 })
        {
            cases++;
            int t = AerialMath.RestringTicks(sp);
            if (t <= 0 || t > prev) bad.Add("speed " + sp + " -> " + t);
            prev = t;
        }
        if (AerialMath.RestringTicks(1.0) != 300) bad.Add("speed 1 is not 300 ticks");
        Row("restring_job_duration", new[] { "restring_cut_span", "restring_job" }, "fixed", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "the re-string job takes a positive time that never grows with construction speed, 300 ticks at speed 1, bounded at speed 0" + (bad.Count == 0 ? "" : ": " + string.Join("; ", bad)));
    }
}
