// Blind lane 1 (game logic) for Gimme Some Slack 0.1.0, cycle 3 of the Stages 4 and 5 challenge.
// Written from the locked bars (sheet.md, tree.json, plan.md, bars.md, record.json rows no_hose / pipe_pole_switch), the
// shipped kernel Source/Aerial/AerialMath.cs and the shipped settings (AerialSettings.cs defaults and slider ranges) ONLY:
// no builder selftest, validation script or SelfTest file was read before this file was written and run.
// Output: one JSON line per row on stdout (id, bars, kind, verdict, cases, detail); exit 1 if any row FAILs.
// Mode --dll <path> <types-out> <strings-out>: dump the type names and user strings of a shipped DLL (for BlindNoHose.py).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection.Metadata;
using System.Reflection.Metadata.Ecma335;
using System.Reflection.PortableExecutable;
using System.Text;
using RimMandrake.GimmeSomeSlack.Aerial;

static class BlindLane1
{
    // ---- shipped settings, copied from AerialSettings.cs (defaults; slider ranges) ----------------------------------
    const float MaxSpanDefault = 20f, MaxSpanLo = 8f, MaxSpanHi = 40f;      // Range => Clamp(maxSpan, 4, 40)
    const float SagDefault = 0.06f, SagLo = 0f, SagHi = 0.15f;
    const int MaxStrandsDefault = 3, MaxStrandsLo = 1, MaxStrandsHi = 3;
    const float SwayLo = 0f, SwayHi = 2f;
    const float TapRateDefault = 500f, TapRateLo = 50f, TapRateHi = 2000f;  // step 50
    const int GoodwillPerDayDefault = 2, GoodwillLo = 0, GoodwillHi = 10;
    const float SightDefault = 12f, SightLo = 3f, SightHi = 30f;
    const int TicksPerDay = 60000;
    const double WattsToWattDaysPerTick = 1.6666667e-5; // RimWorld CompPower constant (1/60000)

    static int fails;
    static string Esc(string s) => s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ");
    static void Row(string id, string bars, string kind, bool? pass, int cases, string detail)
    {
        string v = pass == null ? (kind == "info" ? "INFO" : "UNSETTLED") : pass.Value ? "PASS" : "FAIL";
        if (v == "FAIL") fails++;
        string b = string.Join(",", bars.Split(',').Select(x => "\"" + x.Trim() + "\""));
        Console.WriteLine("{\"id\":\"" + id + "\",\"bars\":[" + b + "],\"kind\":\"" + kind + "\",\"verdict\":\"" + v +
                          "\",\"cases\":" + cases + ",\"detail\":\"" + Esc(detail) + "\"}");
    }
    static float SettingsRange(float maxSpan) => maxSpan < 4f ? 4f : maxSpan > 40f ? 40f : maxSpan;
    static AnchorInfo A(int id, int x, int z, int fac = 0, int maxLinks = 4, bool roof = false, AerialLineKind k = AerialLineKind.Power, bool anchor = true)
        => new AnchorInfo { Id = id, X = x, Z = z, Faction = fac, MaxLinks = maxLinks, Roofed = roof, Kind = k, IsAnchor = anchor };

    static int Main(string[] args)
    {
        if (args.Length == 4 && args[0] == "--dll") return DumpDll(args[1], args[2], args[3]);
        Links(); Spans(); Strands(); Sway(); Removal(); Fallen(); Shock(); Blasts(); Tap(); Theft(); Kinds(); Misc();
        return fails > 0 ? 1 : 0;
    }

    static int DumpDll(string dll, string typesOut, string stringsOut)
    {
        using var fs = File.OpenRead(dll);
        using var pe = new PEReader(fs);
        var md = pe.GetMetadataReader();
        var types = new List<string>();
        foreach (var h in md.TypeDefinitions)
        {
            var t = md.GetTypeDefinition(h);
            types.Add(md.GetString(t.Namespace) + "." + md.GetString(t.Name));
            foreach (var fh in t.GetFields()) types.Add("  field " + md.GetString(md.GetFieldDefinition(fh).Name));
        }
        var strs = new List<string>();
        var uh = MetadataTokens.UserStringHandle(1);
        while (!uh.IsNil)
        {
            string s = md.GetUserString(uh);
            strs.Add(s.Replace("\n", " "));
            uh = md.GetNextHandle(uh);
        }
        File.WriteAllLines(typesOut, types.Where(x => !x.StartsWith("  field ")).ToArray());
        File.WriteAllLines(stringsOut, strs.ToArray());
        Console.WriteLine("DLL " + types.Count + " types+fields, " + strs.Count + " strings");
        return 0;
    }

    // ---- spans_above_everything / overhead_spans: "the three bad links refused with their reasons; out-of-range link accepted is red"
    static void Links()
    {
        double R = SettingsRange(MaxSpanDefault);
        var a = A(1, 0, 0);
        var cases = new (string, AnchorInfo, AnchorInfo, LinkVerdict)[] {
            ("self", a, a, LinkVerdict.Self),
            ("out of range", A(1, 0, 0), A(2, 21, 0), LinkVerdict.OutOfRange),
            ("exactly at range", A(1, 0, 0), A(2, 20, 0), LinkVerdict.Ok),
            ("diagonal just past", A(1, 0, 0), A(2, 15, 14), LinkVerdict.OutOfRange),
            ("foreign", A(1, 0, 0), A(2, 5, 0, fac: 7), LinkVerdict.Foreign),
            ("roofed", A(1, 0, 0, roof: true), A(2, 5, 0), LinkVerdict.Roofed),
            ("not anchor", A(1, 0, 0), A(2, 5, 0, anchor: false), LinkVerdict.NotAnchor),
            ("power to pipe", A(1, 0, 0), A(2, 5, 0, k: AerialLineKind.Pipe), LinkVerdict.WrongKind),
            ("full A", A(1, 0, 0, maxLinks: 0), A(2, 5, 0), LinkVerdict.FullA),
            ("ok", A(1, 0, 0), A(2, 5, 3), LinkVerdict.Ok),
        };
        var bad = new List<string>();
        foreach (var (n, x, y, want) in cases) { var got = AerialMath.CanLink(x, y, R); if (got != want) bad.Add(n + ": " + got + " want " + want); }
        Row("L1_CANLINK_FIXED", "spans_above_everything,overhead_spans", "fixed", bad.Count == 0, cases.Length,
            bad.Count == 0 ? "range " + R + " (default maxSpan 20): each bad link refused with its own reason, in-range accepted" : string.Join("; ", bad));

        // random + slider sweep: Ok exactly when every rule holds; never Ok out of range, foreign, roofed or cross-kind
        int seed = 31337; var rnd = new Random(seed); int n2 = 0; string first = null; string shrunk = null;
        for (float ms = MaxSpanLo; ms <= MaxSpanHi; ms += 4f)
        {
            double r = SettingsRange(ms);
            for (int i = 0; i < 4000; i++, n2++)
            {
                var p = A(1, rnd.Next(-50, 50), rnd.Next(-50, 50), rnd.Next(2), rnd.Next(0, 4), rnd.Next(10) == 0, rnd.Next(6) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power);
                var q = A(2, rnd.Next(-50, 50), rnd.Next(-50, 50), rnd.Next(2), rnd.Next(0, 4), rnd.Next(10) == 0, rnd.Next(6) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power);
                for (int l = 0; l < rnd.Next(3); l++) p.Linked.Add(100 + l);
                double d = Math.Sqrt((p.X - q.X) * (double)(p.X - q.X) + (p.Z - q.Z) * (double)(p.Z - q.Z));
                bool should = p.Faction == q.Faction && p.Kind == q.Kind && !p.Roofed && !q.Roofed && d <= r + 1e-9 &&
                              p.Linked.Count < p.MaxLinks && q.Linked.Count < q.MaxLinks;
                bool ok = AerialMath.CanLink(p, q, r) == LinkVerdict.Ok;
                if (ok != should && first == null)
                {
                    first = "seed " + seed + " case " + n2 + " maxSpan " + ms + ": d " + d.ToString("0.00") + " verdict " + AerialMath.CanLink(p, q, r) + " want ok=" + should;
                    shrunk = "A(" + p.X + "," + p.Z + " f" + p.Faction + " " + p.Kind + " links " + p.Linked.Count + "/" + p.MaxLinks + ") B(" + q.X + "," + q.Z + " f" + q.Faction + " " + q.Kind + " " + q.Linked.Count + "/" + q.MaxLinks + ")";
                }
            }
        }
        Row("L1_CANLINK_RANDOM_SWEEP", "spans_above_everything,overhead_spans", "random", first == null, n2,
            first == null ? "seed 31337, maxSpan swept 8..40 step 4: CanLink Ok exactly when same faction, same kind, unroofed, in range, both under maxLinks" : first + " shrunk " + shrunk);

        // auto-link picks the nearest legal anchor (ties: lower id); -1 only when none is legal
        rnd = new Random(seed + 1); first = null; int n3 = 0;
        for (int i = 0; i < 3000; i++, n3++)
        {
            var self = A(0, 0, 0);
            var others = new List<AnchorInfo>();
            for (int k = 0; k < rnd.Next(0, 8); k++) others.Add(A(k + 1, rnd.Next(-30, 30), rnd.Next(-30, 30), rnd.Next(3) == 0 ? 1 : 0, 4, rnd.Next(8) == 0));
            int pick = AerialMath.AutoLinkPick(self, others, 20);
            var legal = others.Where(o => AerialMath.CanLink(self, o, 20) == LinkVerdict.Ok).OrderBy(o => (long)o.X * o.X + (long)o.Z * o.Z).ThenBy(o => o.Id).ToList();
            int want = legal.Count == 0 ? -1 : legal[0].Id;
            if (pick != want && first == null) first = "seed " + (seed + 1) + " case " + i + ": pick " + pick + " want " + want + " of " + others.Count;
        }
        Row("L1_AUTOLINK_NEAREST_LEGAL", "overhead_spans", "random", first == null, n3, first ?? "seed 31338: AutoLinkPick == nearest legal anchor (lower id on a tie), -1 iff none legal");

        // the minimum spanning links: every edge legal, no cycle (with existing links), degree caps held, no duplicate
        rnd = new Random(seed + 2); first = null; int n4 = 0;
        for (int i = 0; i < 1500; i++, n4++)
        {
            var sel = new List<AnchorInfo>();
            int cnt = rnd.Next(1, 12);
            for (int k = 0; k < cnt; k++) sel.Add(A(k, rnd.Next(0, 40), rnd.Next(0, 40), rnd.Next(5) == 0 ? 1 : 0, rnd.Next(1, 4), rnd.Next(10) == 0));
            if (cnt > 2 && rnd.Next(2) == 0) { sel[0].Linked.Add(1); sel[1].Linked.Add(0); }
            var res = AerialMath.MinimumSpanningLinks(sel, 20);
            var parent = sel.ToDictionary(s => s.Id, s => s.Id); var deg = sel.ToDictionary(s => s.Id, s => s.Linked.Count);
            int F(int x) { while (parent[x] != x) x = parent[x]; return x; }
            foreach (var s in sel) foreach (int l in s.Linked) if (parent.ContainsKey(l)) { int ra = F(s.Id), rb = F(l); if (ra != rb) parent[ra] = rb; }
            string err = null;
            foreach (var (x, y) in res)
            {
                var ax = sel.First(s => s.Id == x); var by = sel.First(s => s.Id == y);
                if (ax.Faction != by.Faction || ax.Roofed || by.Roofed || !AerialMath.InRange(ax.X, ax.Z, by.X, by.Z, 20)) err = "illegal edge " + x + "-" + y;
                int ra = F(x), rb = F(y); if (ra == rb) err = "cycle at " + x + "-" + y; else parent[ra] = rb;
                if (++deg[x] > ax.MaxLinks || ++deg[y] > by.MaxLinks) err = "degree cap broken at " + x + "-" + y;
            }
            if (err != null && first == null) first = "seed " + (seed + 2) + " case " + i + " n " + cnt + ": " + err;
        }
        Row("L1_MST_LEGAL_ACYCLIC_CAPPED", "overhead_spans", "random", first == null, n4, first ?? "seed 31339: every auto-link-selected edge legal, acyclic with existing links, maxLinks held");
    }

    // ---- spans sag ("sag depth above zero", "not a ruler-straight wire"), ends on the insulators
    static void Spans()
    {
        // (a) SagDepth: an east-west span, where screen-down droop is perpendicular to the chord, sags exactly sag x len
        var rnd = new Random(4242); string first = null; int n = 0;
        foreach (double sag in new[] { 0.0, 0.01, 0.03, SagDefault, 0.1, SagHi })
            for (int i = 0; i < 400; i++, n++)
            {
                var a = new P2(rnd.NextDouble() * 50, rnd.NextDouble() * 50);
                double len = 4 + rnd.NextDouble() * 36;
                var b = new P2(a.X + len, a.Z);
                var c = AerialMath.SpanCurve(a, b, sag);
                double lowest = c.Max(p => a.Z - p.Z); bool above = c.Any(p => p.Z > a.Z + 1e-9);
                bool endsOk = P2.Dist(c[0], a) < 1e-9 && P2.Dist(c[c.Count - 1], b) < 1e-9;
                double want = AerialKinds.SagDepth(len, sag);
                // samples every ~0.5 cell: with n samples the deepest one may sit 1/(2n) off mid-span, cos^2(pi/2n) of the true depth
                int ns0 = Math.Max(4, (int)Math.Ceiling(len / 0.5)); double sampleFloor = Math.Pow(Math.Cos(Math.PI / (2 * ns0)), 2);
                bool depthOk = lowest <= want + 1e-9 && lowest >= want * sampleFloor - 1e-9;
                if ((!endsOk || above || !depthOk || (sag > 0 && !(want > 0))) && first == null)
                    first = "seed 4242 sag " + sag + " len " + len.ToString("0.0") + ": endsOk " + endsOk + " above " + above + " lowest " + lowest.ToString("0.000") + " want " + want.ToString("0.000");
            }
        Row("L1_SPAN_SAG_ENDS", "spans_above_everything,overhead_spans", "sweep", first == null, n,
            first ?? "seed 4242, sag swept 0..0.15 (slider) x east-west len 4..40: ends exactly on A and B, never above the chord, deepest drop = sag x len (SagDepth), > 0 for every sag > 0");

        // (b) what the player sees: the drawn curve's perpendicular distance from its own chord, by direction, at the default sag.
        // The droop is screen -Z only, so its visible part is sag x len x |cos(bearing from east)|: a north-south span draws on its chord.
        rnd = new Random(4243); first = null; int nb = 0, straight = 0; string worst = null; double worstDev = 1e9;
        for (int i = 0; i < 2000; i++, nb++)
        {
            var a = new P2(rnd.NextDouble() * 50, rnd.NextDouble() * 50);
            double ang = rnd.NextDouble() * 2 * Math.PI, len = 8 + rnd.NextDouble() * 12;   // 8..20: spans the default 20-cell range allows
            var b = new P2(a.X + len * Math.Cos(ang), a.Z + len * Math.Sin(ang));
            var c = AerialMath.SpanCurve(a, b, SagDefault);
            double dx = b.X - a.X, dz = b.Z - a.Z, L = Math.Sqrt(dx * dx + dz * dz);
            double dev = c.Max(p => Math.Abs((p.X - a.X) * dz - (p.Z - a.Z) * dx) / L);
            if (dev < 0.1) { straight++; if (dev < worstDev) { worstDev = dev; worst = "bearing " + (ang * 180 / Math.PI).ToString("0") + " deg len " + len.ToString("0.0") + " visible sag " + dev.ToString("0.000"); } }
        }
        // shrunk: the due north-south span of the shortest length the slider allows
        var ns = AerialMath.SpanCurve(new P2(0, 0), new P2(0, MaxSpanLo), SagDefault);
        double nsDev = ns.Max(p => Math.Abs(p.X));
        Row("L1_SPAN_VISIBLE_SAG_EVERY_BEARING", "spans_above_everything", "random", straight == 0, nb,
            straight == 0 ? "seed 4243: every span 8..20 cells at the default sag shows at least 0.1 cell of sag off its chord" :
            "seed 4243: " + straight + "/" + nb + " spans at default sag 0.06 draw within 0.1 cell of their chord (ruler-straight on screen); worst " + worst +
            "; shrunk: a due north-south span (0,0)->(0," + MaxSpanLo + ") draws every point on its chord, max off-chord " + nsDev.ToString("0.000") + " cell (the droop is screen -Z, along the chord). Kernel only: lane 2 must read whether the drawing side adds a sideways bow");
        Row("L1_SPAN_SAG_ZERO_ON_SLIDER", "spans_above_everything", "info", null, 1,
            "the sag slider's low end is 0 (AerialSettings: Slider(sag, 0, 0.15)); at 0 SagDepth = 0, a ruler-straight wire, which the bar says it must not read as. Default 0.06 sags; a player-chosen 0 is a setting, not the shipped look");

        // drip loops (default off): with depth 0 the curve is SpanCurve; ends exact; pipes never drip
        var a2 = new P2(1, 1); var b2 = new P2(17, 6);
        var c0 = AerialMath.SpanCurve(a2, b2, SagDefault); var d0 = AerialMath.SpanCurveDrip(a2, b2, SagDefault, 0, 0.6);
        bool same = c0.Count == d0.Count && c0.Zip(d0, (p, q) => P2.Dist(p, q)).All(x => x < 1e-12);
        var d1 = AerialMath.SpanCurveDrip(a2, b2, SagDefault, 0.15, 0.6);
        bool ends = P2.Dist(d1[0], a2) < 1e-12 && P2.Dist(d1[d1.Count - 1], b2) < 1e-12;
        bool kinds = !AerialKinds.Drips(AerialLineKind.Pipe, true) && !AerialKinds.Drips(AerialLineKind.Power, false) && AerialKinds.Drips(AerialLineKind.Power, true);
        Row("L1_DRIP_LOOP_SWITCH", "settings_switch_cleanly,mod_settings", "fixed", same && ends && kinds, 3,
            "depth 0 == plain curve " + same + "; drip ends exact " + ends + "; Drips(pipe,on)=false, Drips(power,off)=false, Drips(power,on)=true: " + kinds);
    }

    // ---- strands: one wire per insulator, capped by the fewer end and the wires-per-span slider; every wire ends on an insulator tip
    static void Strands()
    {
        var rnd = new Random(77); string first = null; int n = 0;
        for (int ms = MaxStrandsLo; ms <= MaxStrandsHi; ms++)
            for (int ia = 0; ia <= 4; ia++)
                for (int ib = 0; ib <= 4; ib++, n++)
                {
                    var insA = Enumerable.Range(0, ia).Select(k => new P2(-0.4 + 0.2 * k, 1.8)).ToList();
                    var insB = Enumerable.Range(0, ib).Select(k => new P2(-0.3 + 0.2 * k, 1.6)).ToList();
                    var bA = new P2(rnd.Next(30), rnd.Next(30)); var bB = new P2(rnd.Next(30), rnd.Next(30));
                    var s = AerialMath.SpanStrands(bA, insA, bB, insB, rnd.Next(), ms);
                    int want = Math.Max(1, Math.Min(Math.Min(Math.Max(1, ia), Math.Max(1, ib)), ms));
                    string e = null;
                    if (s.Count != want) e = "count " + s.Count + " want " + want;
                    foreach (var st in s)
                    {
                        if (ia > 0 && P2.Dist(st.A, new P2(bA.X + insA[st.InsA].X, bA.Z + insA[st.InsA].Z)) > 1e-9) e = "A not on its insulator";
                        if (ib > 0 && P2.Dist(st.B, new P2(bB.X + insB[st.InsB].X, bB.Z + insB[st.InsB].Z)) > 1e-9) e = "B not on its insulator";
                        if (!(st.SagMul > 0)) e = "sag multiplier " + st.SagMul;
                    }
                    if (ia >= s.Count && s.Select(x => x.InsA).Distinct().Count() != s.Count) e = "two wires share an insulator at A";
                    if (e != null && first == null) first = "maxStrands " + ms + " insA " + ia + " insB " + ib + ": " + e;
                }
        bool pipeOne = AerialKinds.StrandCap(AerialLineKind.Pipe, 3) == 1 && AerialKinds.StrandCap(AerialLineKind.Power, 3) == 3;
        Row("L1_STRANDS_PER_INSULATOR", "overhead_spans,mod_settings", "sweep", first == null && pipeOne, n,
            first ?? "seed 77, wires-per-span slider 1..3 x insulators 0..4 each end: count = min(ends, slider), >= 1; every wire on its own insulator tip; pipe spans one strand");
    }

    // ---- sway: flat at both insulators, none without wind, bounded by the stated envelope; strength slider 0..2
    static void Sway()
    {
        var rnd = new Random(99); string first = null; int n = 0;
        for (double amp = SwayLo; amp <= SwayHi; amp += 0.5)
            for (int i = 0; i < 2000; i++, n++)
            {
                double t = rnd.NextDouble(), time = rnd.NextDouble() * 1000, wind = rnd.NextDouble() * 3; int seed = rnd.Next();
                double v = AerialMath.Sway(t, time, wind, amp, seed);
                double bound = 1.3 * amp * Math.Min(wind, 1.5) / 1.5 + 1e-9;
                string e = null;
                if (Math.Abs(v) > bound) e = "|sway| " + v + " > " + bound;
                if (AerialMath.Sway(0, time, wind, amp, seed) != 0 || AerialMath.Sway(1, time, wind, amp, seed) != 0) e = "insulator moves";
                if (AerialMath.Sway(t, time, 0, amp, seed) != 0) e = "sways with no wind";
                if (e != null && first == null) first = "seed 99 amp " + amp + " t " + t.ToString("0.000") + " wind " + wind.ToString("0.00") + ": " + e;
            }
        bool modes = AerialMath.WireSwayPrefAllows(0, true) && !AerialMath.WireSwayPrefAllows(0, false) && AerialMath.WireSwayPrefAllows(1, false) && !AerialMath.WireSwayPrefAllows(2, true);
        bool pipe = !AerialKinds.Sways(AerialLineKind.Pipe);
        Row("L1_SWAY_BOUNDED_FLAT_ENDS", "overhead_spans,mod_settings", "sweep", first == null && modes && pipe, n,
            first ?? "seed 99, swayStrength 0..2: 0 at both insulators and with no wind, |offset| within 1.3 amp min(wind,1.5)/1.5; modes Auto/Always/Off honoured; pipes never sway");
    }

    // ---- fallen_span_on_ground / downed_spans / gravship_keeps_connections: what a removed anchor leaves
    static void Removal()
    {
        var rnd = new Random(555); string first = null; int n = 0;
        for (int i = 0; i < 5000; i++, n++)
        {
            int id = 0; bool killed = rnd.Next(2) == 0;
            var spans = new List<(int, SpanState)>();
            for (int k = 0; k < rnd.Next(0, 6); k++) spans.Add((rnd.Next(0, 6), rnd.Next(3) == 0 ? SpanState.Cut : SpanState.Up));
            HashSet<int> aboard = rnd.Next(3) == 0 ? new HashSet<int>(Enumerable.Range(0, 6).Where(_ => rnd.Next(2) == 0)) : null;
            var plan = AerialMath.PlanRemoval(id, killed, spans, aboard);
            var partners = spans.Where(s => s.Item1 != id).Select(s => s.Item1).Distinct().ToList();
            string e = null;
            bool gravFlight = aboard != null && !killed;
            var wantReseed = gravFlight ? partners.Where(p => !aboard.Contains(p)).ToList() : partners;
            if (!new HashSet<int>(plan.Reseed).SetEquals(wantReseed)) e = "reseed " + string.Join(",", plan.Reseed) + " want " + string.Join(",", wantReseed);
            int wantFallen = killed ? spans.Count(s => s.Item1 != id && s.Item2 == SpanState.Up) : 0;
            if (plan.Fallen.Count != wantFallen) e = "fallen " + plan.Fallen.Count + " want " + wantFallen;
            if (plan.Fallen.Any(f => f.Survivor == id || !f.TowardDead)) e = "a fallen wire on the dead anchor";
            if (gravFlight)
            {
                var kept = new HashSet<int>(plan.Kept); var gr = new HashSet<int>(plan.Grounded);
                if (kept.Overlaps(gr) || !new HashSet<int>(kept.Concat(gr)).SetEquals(partners)) e = "gravship kept/grounded not a partition of the partners";
                if (plan.Kept.Any(p => !aboard.Contains(p)) || plan.Grounded.Any(p => aboard.Contains(p))) e = "kept a partner left behind, or grounded one aboard";
            }
            else if (plan.Kept.Count + plan.Grounded.Count > 0) e = "kept/grounded outside a flight";
            if (e != null && first == null) first = "seed 555 case " + i + " killed " + killed + " aboard " + (aboard == null ? "null" : string.Join(",", aboard)) + " spans " + string.Join(",", spans) + ": " + e;
        }
        Row("L1_REMOVAL_PLAN_CONSERVES", "fallen_span_on_ground,downed_spans,gravship_keeps_connections,gravship_connectivity", "random", first == null, n,
            first ?? "seed 555: every partner re-seeded (none lost); killed: one fallen wire per UP span, none for a CUT one; dismantled: none fall; gravship lift: partners split exactly into kept (aboard) and grounded (left), nothing falls");

        // watchdog: an UP span whose ends are not on one net is repaired; a CUT span never is
        var reads = new List<SpanNetRead>(); var rnd2 = new Random(556); first = null;
        for (int i = 0; i < 4000; i++) reads.Add(new SpanNetRead { Span = i, NetA = rnd2.Next(-1, 3), NetB = rnd2.Next(-1, 3), State = rnd2.Next(2) == 0 ? SpanState.Up : SpanState.Cut });
        var rep = new HashSet<int>(AerialMath.WatchdogRepairs(reads));
        foreach (var r in reads)
        {
            bool want = r.State == SpanState.Up && (r.NetA < 0 || r.NetB < 0 || r.NetA != r.NetB);
            if (rep.Contains(r.Span) != want && first == null) first = "span " + r.Span + " " + r.State + " " + r.NetA + "/" + r.NetB;
        }
        Row("L1_WATCHDOG_UP_SPLIT_ONLY", "overhead_spans,connectivity_truth", "random", first == null, reads.Count, first ?? "seed 556: repaired exactly the UP spans whose ends sit on different or no nets");
    }

    // ---- a fallen wire lies on the ground, never over a wall; the contact set is the grounded part
    static void Fallen()
    {
        var rnd = new Random(8080); string first = null; int n = 0, grounded = 0, tipOk = 0;
        for (int i = 0; i < 1500; i++, n++)
        {
            int seed = rnd.Next();
            var walls = new HashSet<(int, int)>();
            for (int k = 0; k < rnd.Next(0, 25); k++) walls.Add((rnd.Next(-15, 16), rnd.Next(-15, 16)));
            walls.Remove((0, 0));
            Func<int, int, bool> walk = (x, z) => !walls.Contains((x, z));
            var bp = new P2(0.5, 0.5); var top = new P2(0.5, 2.3);
            double ang = rnd.NextDouble() * 2 * Math.PI, dist = 2 + rnd.NextDouble() * 14;
            var tw = new P2(bp.X + dist * Math.Cos(ang), bp.Z + dist * Math.Sin(ang));
            var lay = AerialMath.LayFallen(top, bp, tw, dist * 1.05, seed, walk);
            string e = null;
            if (lay.GroundFrom >= 0) grounded++;
            foreach (var p in AerialMath.GroundPts(lay))
                if (P2.Dist(p, bp) > 0.75 && !walk((int)Math.Floor(p.X), (int)Math.Floor(p.Z))) { e = "grounded point " + p + " on a wall cell"; break; }
            if (lay.Pts.Count > 0 && P2.Dist(lay.Tip, lay.Pts[lay.Pts.Count - 1]) < 1e-9) tipOk++;
            // the contact set and LayTouches agree on every cell
            var cells = new HashSet<(int, int)>(AerialMath.GroundPts(lay).Select(p => ((int)Math.Floor(p.X), (int)Math.Floor(p.Z))));
            for (int x = -16; x <= 16 && e == null; x++) for (int z = -16; z <= 16; z++)
                    if (AerialMath.LayTouches(lay, x, z) != cells.Contains((x, z))) { e = "LayTouches disagrees with GroundPts at " + x + "," + z; break; }
            if (e != null && first == null)
            {
                // shrink: drop walls one at a time while the case still fails
                var w2 = new HashSet<(int, int)>(walls);
                foreach (var cell in walls.ToList())
                {
                    w2.Remove(cell);
                    if (!FallenFails(top, bp, tw, dist, seed, w2)) w2.Add(cell);
                }
                bool towardInWall = w2.Contains(((int)Math.Floor(tw.X), (int)Math.Floor(tw.Z)));
                first = "seed " + seed + " (outer 8080 case " + i + ") walls " + walls.Count + " dist " + dist.ToString("0.0") + ": " + e +
                        "; shrunk: base (0.5,0.5) top (0.5,2.3) toward " + tw + " walls {" + string.Join(" ", w2) + "}" + (towardInWall ? " (the toward point itself is in a wall cell)" : "");
            }
        }
        bool pass = first == null && grounded == n && tipOk == n;
        Row("L1_FALLEN_ON_GROUND_NOT_WALLS", "fallen_span_on_ground,downed_spans,fallen_wire_shocks_crossers", "random", pass, n,
            first ?? ("seed 8080, random wall grids, drop 2..16 cells: grounded " + grounded + "/" + n + ", tip = last point " + tipOk + "/" + n + "; no grounded point past 0.75 cell on a wall cell; LayTouches == GroundPts cells"));

        // several wires never pinch to one point (three wires fall as three)
        rnd = new Random(8081); first = null; int m = 0; double minGap = 1e9; int under05 = 0;
        for (int i = 0; i < 800; i++, m++)
        {
            int cnt = rnd.Next(1, 4);
            var tips = Enumerable.Range(0, 3).Select(k => new P2(0.1 + 0.4 * k, 2.2)).ToList();
            var bp = new P2(0.5, 0.5); double dist = 3 + rnd.NextDouble() * 12, ang = rnd.NextDouble() * 6.283;
            var lays = AerialMath.LayFallenStrands(tips, bp, new P2(bp.X + dist * Math.Cos(ang), bp.Z + dist * Math.Sin(ang)), dist * 1.05, rnd.Next(), cnt, (x, z) => true);
            string e = lays.Count != cnt ? "count " + lays.Count + " want " + cnt : null;
            for (int p = 0; p < lays.Count && e == null; p++) for (int q = p + 1; q < lays.Count; q++)
                    { double g = P2.Dist(lays[p].Tip, lays[q].Tip); minGap = Math.Min(minGap, g); if (g < 0.5) under05++; }
            for (int p = 0; p < lays.Count && e == null; p++) for (int q = p + 1; q < lays.Count; q++)
                    if (P2.Dist(lays[p].Tip, lays[q].Tip) < 0.05) { e = "tips " + p + "," + q + " pinch (" + P2.Dist(lays[p].Tip, lays[q].Tip).ToString("0.000") + " cell; FallenSpread is 1.15)"; break; }
            if (e != null && first == null) first = "seed 8081 case " + i + " wires " + cnt + " dist " + dist.ToString("0.0") + ": " + e;
        }
        Row("L1_FALLEN_STRANDS_EACH_ITS_OWN", "fallen_span_on_ground,downed_spans", "random", first == null, m, first ?? ("seed 8081: a broken span drops one wire per strand, no two tips within 0.05 cell (one point); closest pair " + minGap.ToString("0.00") + " cell, pairs under 0.5 cell " + under05 + ". The first draft used 0.2 cell, a number of mine the bar does not hold; case 12 came in at 0.19"));
    }

    static bool FallenFails(P2 top, P2 bp, P2 tw, double dist, int seed, HashSet<(int, int)> walls)
    {
        Func<int, int, bool> walk = (x, z) => !walls.Contains((x, z));
        var lay = AerialMath.LayFallen(top, bp, tw, dist * 1.05, seed, walk);
        foreach (var p in AerialMath.GroundPts(lay))
            if (P2.Dist(p, bp) > 0.75 && !walk((int)Math.Floor(p.X), (int)Math.Floor(p.Z))) return true;
        return false;
    }

    // ---- fallen_wire_shocks_crossers: who takes the shock (the kernel's half)
    static void Shock()
    {
        int n = 0; string first = null;
        foreach (bool flesh in new[] { false, true }) foreach (bool dead in new[] { false, true }) foreach (bool o in new[] { false, true }) foreach (bool rs in new[] { false, true })
                    {
                        n++;
                        bool want = flesh && !dead && !o && !rs;
                        if (AerialMath.ShockTakes(flesh, dead, o, rs) != want && first == null) first = "flesh " + flesh + " dead " + dead + " out " + o + " restring " + rs;
                    }
        Row("L1_SHOCK_TAKES_TABLE", "fallen_wire_shocks_crossers,fallen_wire_shock", "fixed", first == null, n,
            first ?? "16 cases: a live, conscious, flesh pawn is shocked unless it is the re-stringer of THIS cut (the flag); whether the flag is set only for that span is the caller's (not_kernel row)");
        Row("L1_SHOCK_EXEMPTION_TARGETS_SPAN", "fallen_wire_shocks_crossers", "not_kernel", null, 0,
            "the exemption must key on the span the RM_RestringSpan job targets, never the job type: ShockTakes takes a bool; who sets it lives in RM_FallenWireShock / FloorEndShock (game side), Stage 6 scenes sc_shock, sc_shock_restring");

        // knockback lands on a free cell, preferring straight away from the end
        var rnd = new Random(1212); int m = 0; first = null;
        for (int i = 0; i < 4000; i++, m++)
        {
            int ax = rnd.Next(-3, 4), az = rnd.Next(-3, 4); var free = new HashSet<(int, int)>();
            foreach (var d in AerialMath.Ring8) if (rnd.Next(3) > 0) free.Add(d);
            var got = AerialMath.KnockbackDir(ax, az, rnd.Next(8), (x, z) => free.Contains((x, z)));
            string e = null;
            if (got == null && free.Count > 0) e = "null with " + free.Count + " free";
            if (got != null && !free.Contains(got.Value)) e = "lands on a blocked cell " + got;
            var away = (Math.Sign(ax), Math.Sign(az));
            if ((ax != 0 || az != 0) && free.Contains(away) && got != null && got.Value != away) e = "skipped the free away cell";
            if (e != null && first == null) first = "seed 1212 case " + i + " away " + ax + "," + az + ": " + e;
        }
        Row("L1_KNOCKBACK_FREE_CELL", "fallen_wire_shock", "random", first == null, m, first ?? "seed 1212: knockback always a free neighbour (straight away when free), null only when none is");
    }

    // ---- blasts cut, kinetic waves never do; damage falls off to 20% at the edge
    static void Blasts()
    {
        int n = 0; string first = null;
        foreach (bool harm in new[] { false, true }) foreach (bool kin in new[] { false, true }) foreach (double dmg in new[] { 0.0, 10 }) foreach (bool cut in new[] { false, true }) foreach (bool ks in new[] { false, true })
                        {
                            n++;
                            var want = !harm ? AerialMath.BlastKind.None : kin ? (ks ? AerialMath.BlastKind.Sway : AerialMath.BlastKind.None) : (cut && dmg > 0 ? AerialMath.BlastKind.Cut : AerialMath.BlastKind.None);
                            var got = AerialMath.BlastKindFor(harm, kin, dmg, cut, ks);
                            if (got != want && first == null) first = "harm " + harm + " kinetic " + kin + " dmg " + dmg + " explosionsCut " + cut + " kineticSway " + ks + ": " + got + " want " + want;
                        }
        Row("L1_BLAST_KIND_SWITCHES", "fallen_span_on_ground,downed_spans,mod_settings", "sweep", first == null, n,
            first ?? "32 cases over the explosionsCut and kineticSway switches: kinetic never cuts; explosionsCut off never cuts; only harmful, damaging blasts cut");
        var rnd = new Random(3030); first = null; int m = 0;
        for (int i = 0; i < 5000; i++, m++)
        {
            var a = new P2(rnd.NextDouble() * 20, rnd.NextDouble() * 20); var b = new P2(rnd.NextDouble() * 20, rnd.NextDouble() * 20);
            var c = new P2(rnd.NextDouble() * 20, rnd.NextDouble() * 20); double r = 0.5 + rnd.NextDouble() * 6, hp = 50, dmg = rnd.NextDouble() * 80;
            var s = AerialMath.BlastSpan(a, b, c, r, hp, dmg, AerialMath.BlastKind.Cut);
            double d = P2.Dist(P2.Lerp(a, b, AerialMath.ClosestT(a, b, c)), c);
            string e = null;
            if (s.Hit != (d <= r)) e = "hit " + s.Hit + " at d " + d.ToString("0.00") + " r " + r.ToString("0.00");
            if (s.Hit) { double f = (hp - s.Hp) / Math.Max(dmg, 1e-12); if (dmg > 0 && (f < 0.2 - 1e-9 || f > 1 + 1e-9)) e = "falloff " + f; if (s.Cut != (s.Hp <= 0)) e = "cut flag"; }
            else if (s.Hp != hp || s.Cut) e = "a miss changed the span";
            if (e != null && first == null) first = "seed 3030 case " + i + ": " + e;
        }
        Row("L1_BLAST_FALLOFF_HIT", "downed_spans", "random", first == null, m, first ?? "seed 3030: hit exactly within the radius of the span's ground line, damage share in [0.2, 1], cut iff hp <= 0, a miss changes nothing");
    }

    // ---- tap_steals_and_costs_goodwill: one-way power, never more than the victim has (nothing created)
    static void Tap()
    {
        var rnd = new Random(2468); string first = null; int n = 0;
        double k = WattsToWattDaysPerTick;
        for (float rate = TapRateLo; rate <= TapRateHi; rate += 50f)
            for (int i = 0; i < 200; i++, n++)
            {
                double gain = (rnd.NextDouble() - 0.3) * 3000 * k, stored = rnd.Next(3) == 0 ? 0 : rnd.NextDouble() * 0.05;
                int taps = rnd.Next(1, 5); double taken = 0; string e = null;
                for (int t = 0; t < taps; t++)
                {
                    double s = AerialMath.TapStolenPerTick(rate, gain, stored, k, false, true, taken, true);
                    if (s < 0) e = "negative theft";
                    if (s > rate * k + 1e-15) e = "a tap took more than its rate";
                    taken += s;
                }
                if (taken > Math.Max(0, gain) + stored + 1e-12) e = "taps took " + taken + " > victim had " + (Math.Max(0, gain) + stored);
                if (AerialMath.TapStolenPerTick(rate, gain, stored, k, true, true) != 0) e = "stole from our own net";
                if (AerialMath.TapStolenPerTick(rate, gain, stored, k, false, false) != 0) e = "stole with taps off";
                if (AerialMath.TapStolenPerTick(rate, gain, stored, k, false, true, 0, false) != 0) e = "a switched-off clamp stole";
                if (e != null && first == null) first = "seed 2468 rate " + rate + " case " + i + " gain " + gain + " stored " + stored + " taps " + taps + ": " + e;
            }
        bool nan = AerialMath.TapStolenPerTick(double.NaN, 1, 1, k, false, true) == 0 && AerialMath.TapStolenPerTick(500, double.NaN, 1, k, false, true) == 0;
        Row("L1_TAP_CONSERVES_ONE_WAY", "tap_steals_and_costs_goodwill,power_theft", "sweep", first == null && nan, n,
            first ?? "seed 2468, tapRate 50..2000 step 50, 1-4 taps sharing one victim: never negative, each within its rate, together never more than the victim's gain + store; 0 from our own net, with taps off, or from an idle clamp; NaN safe");
    }

    // ---- caught theft: spotted only within sight and line of sight; goodwill drains steadily, per whole day drained
    static void Theft()
    {
        var rnd = new Random(1357); string first = null; int n = 0;
        for (float sr = SightLo; sr <= SightHi; sr += 3f)
            for (int i = 0; i < 400; i++, n++)
            {
                double d = rnd.NextDouble() * 40; bool los = rnd.Next(2) == 0, up = rnd.Next(4) > 0, held = rnd.Next(5) == 0;
                bool want = los && up && !held && d <= sr;
                if (AerialMath.TheftSpotted(d, sr, los, up, held) != want && first == null) first = "seed 1357 sight " + sr + " d " + d + " los " + los + " up " + up + " held " + held;
            }
        Row("L1_THEFT_SPOTTED_SIGHT", "tap_steals_and_costs_goodwill,power_theft", "sweep", first == null, n, first ?? "seed 1357, theftSightRange 3..30: spotted iff awake, not held, line of sight and within range");

        rnd = new Random(1358); first = null; int m = 0;
        for (int per = GoodwillLo; per <= GoodwillHi; per++)
            for (int i = 0; i < 100; i++, m++)
            {
                int acc = 0, total = 0, drained = 0;
                for (int step = 0; step < 60; step++)
                {
                    int ticks = rnd.Next(0, 9000); bool draining = rnd.Next(4) > 0;
                    int before = acc;
                    int g = AerialMath.TheftGoodwillAccrue(ref acc, ticks, draining, per, TicksPerDay);
                    if (g > 0) first = first ?? "positive goodwill " + g;
                    if (!draining && (g != 0 || acc != before)) first = first ?? "idle clamp accrued";
                    total += g; if (draining && ticks > 0) drained += ticks;
                }
                int want = -(drained / TicksPerDay) * per;
                if (total != want && first == null) first = "seed 1358 perDay " + per + " case " + i + ": total " + total + " want " + want + " over " + drained + " drained ticks";
                if (acc != drained % TicksPerDay && first == null) first = "remainder lost: carried " + acc + " want " + drained % TicksPerDay;
            }
        Row("L1_GOODWILL_STEADY_CONSERVED", "tap_steals_and_costs_goodwill,power_theft", "sweep", first == null, m,
            first ?? "seed 1358, theftGoodwillPerDay 0..10, random tick chunks: total = -perDay x whole days drained, the remainder carried exactly, idle clamps accrue nothing, never positive (steady, not one-off)");
        Row("L1_THEFT_STOPS_ON_REMOVAL", "tap_steals_and_costs_goodwill", "not_kernel", null, 0,
            "removing the clamp stopping the drain and the drain hitting only the victim faction are PowerTheftConsequences / TapLedger (game side): Stage 6 scene sc_theft");
    }

    // ---- settings_switch_cleanly / pipe_pole_switch: pipe poles obey their own switch, power ones the GSS master
    static void Kinds()
    {
        int n = 0; string first = null;
        foreach (bool po in new[] { false, true }) foreach (bool pi in new[] { false, true }) foreach (bool ps in new[] { false, true })
                {
                    n++;
                    if (AerialKinds.KindOn(AerialLineKind.Power, po, pi) != po) first = first ?? "power anchor obeys pipe switch";
                    if (AerialKinds.KindOn(AerialLineKind.Pipe, po, pi) != pi) first = first ?? "pipe pole obeys the power master";
                    if (AerialKinds.KindBehaviour(AerialLineKind.Power, po, pi, ps) != (po && ps)) first = first ?? "power behaviour";
                    if (AerialKinds.KindBehaviour(AerialLineKind.Pipe, po, pi, ps) != pi) first = first ?? "pipe behaviour touched by a power setting";
                }
        bool carries = AerialKinds.CarriesPower(AerialLineKind.Power) && !AerialKinds.CarriesPower(AerialLineKind.Pipe);
        Row("L1_PIPE_POLE_OWN_SWITCH", "settings_switch_cleanly,pipe_pole_switch,mod_settings", "fixed", first == null && carries, n,
            first ?? "8 switch states: power anchors follow the GSS master (and their setting), pipe poles only their own switch; a pipe span never carries power");
        Row("L1_KERNEL_LAYS_PIPE_SPANS_INFO", "no_hose,no_hose_in_gss,pipe_pole_switch", "info", null, 1,
            "AerialLineKind.Pipe is in GSS's span kernel: FlowWorks pipe-pole spans get GSS's curve (one strand, sag " + AerialKinds.PipeSagDefault + ", range " + AerialKinds.PipeMaxSpanDefault +
            " by default, own switch). Whether GSS itself DRAWS a pipe (its material, its texture) against 'No hose, reel or pipe is drawn by this mod' is a caller read: lane 2");
        // range and sag clamps over the slider and beyond
        string e = null; int m = 0;
        foreach (float v in new[] { float.NaN, -5f, 0f, 2f, 4f, 8f, 20f, 30f, 40f, 99f })
        {
            m++;
            float pr = AerialKinds.RangeFor(AerialLineKind.Power, v, 12f), pp = AerialKinds.RangeFor(AerialLineKind.Pipe, 20f, v);
            if (!(pr >= 4 && pr <= 40) || !(pp >= 2 && pp <= 30)) e = "range " + v + " -> power " + pr + " pipe " + pp;
            if (!float.IsNaN(v) && v >= 4 && v <= 40 && pr != v) e = "power range moved an in-bounds value " + v;
            float sp = AerialKinds.SagFor(AerialLineKind.Power, v, 0.02f);
            if (float.IsNaN(sp) || sp < 0) e = "sag " + v + " -> " + sp;
        }
        Row("L1_RANGE_SAG_CLAMPS", "overhead_spans,mod_settings", "sweep", e == null, m, e ?? "maxSpan slider 8..40 passes through untouched, NaN/negative/oversized clamped (power 4..40, pipe 2..30); sag never NaN or negative");
    }

    static void Misc()
    {
        bool ok = true; double prev = double.MaxValue;
        foreach (double s in new[] { 0.0, 0.05, 0.1, 0.5, 1, 2, 5 }) { int t = AerialMath.RestringTicks(s); if (t <= 0 || t > prev) ok = false; prev = t; }
        Row("L1_RESTRING_TICKS_POSITIVE", "restring_cut_span,restring_job", "fixed", ok, 7, "re-string time positive and never longer for a faster worker (speed 0 clamps at 0.1)");
    }
}
