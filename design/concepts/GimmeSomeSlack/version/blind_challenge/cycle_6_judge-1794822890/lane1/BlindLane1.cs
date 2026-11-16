// Blind lane 1, GimmeSomeSlack 0.1.0 cycle 6 (judge-1794822890): game-logic tests written from the bars alone
// (tree.json, sheet.md, plan.md, record.json rows) against the Verse-free kernels AerialMath.cs and ShockRule.cs,
// and the shipped settings (AerialSettings.cs defaults and slider ranges, handed in by run_lane1.py).
// One JSON row per line on stdout. Exit 0 = no FAIL row.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.GimmeSomeSlack.Aerial;

static class BlindLane1
{
    static int fails;
    static string J(string s) { var b = new StringBuilder("\""); foreach (char c in s) { if (c == '"' || c == '\\') b.Append('\\').Append(c); else if (c < 32) b.Append(' '); else b.Append(c); } return b.Append('"').ToString(); }
    static void Row(string id, string[] bars, string kind, bool ok, int cases, string detail, string verdictOverride = null)
    {
        string v = verdictOverride ?? (ok ? "PASS" : "FAIL");
        if (v == "FAIL") fails++;
        Console.WriteLine("{\"id\":" + J(id) + ",\"bars\":[" + string.Join(",", bars.Select(J)) + "],\"kind\":" + J(kind) + ",\"verdict\":" + J(v) + ",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }
    static double Env(string k, double d) { var s = Environment.GetEnvironmentVariable(k); return double.TryParse(s, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out double v) ? v : d; }

    static AnchorInfo A(int id, int x, int z, int fac = 1, int max = 4, AerialLineKind k = AerialLineKind.Power) =>
        new AnchorInfo { Id = id, X = x, Z = z, Faction = fac, MaxLinks = max, Kind = k };

    static int Main()
    {
        // shipped settings, from AerialSettings.cs (run_lane1.py reads them; the fallbacks are the values read by hand 2026-11-16)
        double maxSpanDef = Env("GSS_MAXSPAN", 20), maxSpanLo = Env("GSS_MAXSPAN_LO", 8), maxSpanHi = Env("GSS_MAXSPAN_HI", 40);
        double sagDef = Env("GSS_SAG", 0.06), sagHi = Env("GSS_SAG_HI", 0.15);
        double tapRateDef = Env("GSS_TAPRATE", 500), tapLo = Env("GSS_TAPRATE_LO", 50), tapHi = Env("GSS_TAPRATE_HI", 2000);
        double sightDef = Env("GSS_SIGHT", 12), sightLo = Env("GSS_SIGHT_LO", 3), sightHi = Env("GSS_SIGHT_HI", 30);
        int perDayDef = (int)Env("GSS_PERDAY", 2), perDayHi = (int)Env("GSS_PERDAY_HI", 10);
        int strandsDef = (int)Env("GSS_STRANDS", 3), strandsHi = (int)Env("GSS_STRANDS_HI", 3);
        string shockDef = Environment.GetEnvironmentVariable("GSS_SHOCK_DEFAULT") ?? "All";
        string[] OS = { "spans_above_everything", "overhead_spans" };

        // ---------------------------------------------------------------- link rules
        {
            var bad = new List<string>(); int n = 0;
            double r = maxSpanDef;
            void Expect(string what, LinkVerdict got, LinkVerdict want) { n++; if (got != want) bad.Add(what + ": " + got + " want " + want); }
            Expect("in range", AerialMath.CanLink(A(1, 0, 0), A(2, 20, 0), r), LinkVerdict.Ok);
            Expect("one past range", AerialMath.CanLink(A(1, 0, 0), A(2, 21, 0), r), LinkVerdict.OutOfRange);
            Expect("diagonal past range", AerialMath.CanLink(A(1, 0, 0), A(2, 15, 14), r), LinkVerdict.OutOfRange);
            Expect("self", AerialMath.CanLink(A(1, 0, 0), A(1, 0, 0), r), LinkVerdict.Self);
            Expect("foreign", AerialMath.CanLink(A(1, 0, 0), A(2, 3, 0, 2), r), LinkVerdict.Foreign);
            Expect("power to pipe pole", AerialMath.CanLink(A(1, 0, 0), A(2, 3, 0, 1, 4, AerialLineKind.Pipe), r), LinkVerdict.WrongKind);
            var ro = A(2, 3, 0); ro.Roofed = true; Expect("roofed", AerialMath.CanLink(A(1, 0, 0), ro, r), LinkVerdict.Roofed);
            var na = A(2, 3, 0); na.IsAnchor = false; Expect("not an anchor", AerialMath.CanLink(A(1, 0, 0), na, r), LinkVerdict.NotAnchor);
            var full = A(1, 0, 0, 1, 1); full.Linked.Add(9); Expect("full", AerialMath.CanLink(full, A(2, 3, 0), r), LinkVerdict.FullA);
            var al = A(1, 0, 0); al.Linked.Add(2); Expect("already", AerialMath.CanLink(al, A(2, 3, 0), r), LinkVerdict.AlreadyLinked);
            Row("L1_LINK_FIXED", OS, "fixed", bad.Count == 0, n, bad.Count == 0 ? "range " + r + ": in-range Ok, one past refused, self/foreign/wrong kind/roofed/not-anchor/full/already refused with their reasons" : string.Join("; ", bad));
        }
        {
            // random: Ok implies in range, same kind, same faction, room on both; range is the setting swept through its slider
            var rng = new Random(61601); var bad = new List<string>(); int n = 0;
            for (double ms = maxSpanLo; ms <= maxSpanHi; ms += 1)
            {
                double range = AerialKinds.RangeFor(AerialLineKind.Power, (float)ms, 12f);
                if (Math.Abs(range - ms) > 1e-6) bad.Add("RangeFor(power," + ms + ")=" + range);
                for (int i = 0; i < 400; i++)
                {
                    n++;
                    var a = A(1, rng.Next(-50, 50), rng.Next(-50, 50), rng.Next(2), rng.Next(1, 4), rng.Next(4) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power);
                    var b = A(2, rng.Next(-50, 50), rng.Next(-50, 50), rng.Next(2), rng.Next(1, 4), rng.Next(4) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power);
                    var v = AerialMath.CanLink(a, b, range);
                    double d = Math.Sqrt((a.X - b.X) * (a.X - b.X) + (a.Z - b.Z) * (a.Z - b.Z));
                    if (v == LinkVerdict.Ok && (d > range + 1e-9 || a.Kind != b.Kind || a.Faction != b.Faction))
                        bad.Add("seed 61601 ms " + ms + " i " + i + ": Ok at d " + d.ToString("0.00") + " kinds " + a.Kind + "/" + b.Kind);
                    if (v == LinkVerdict.OutOfRange && d <= range) bad.Add("refused in range d " + d);
                }
            }
            Row("L1_LINK_RANDOM_SWEEP", OS, "sweep", bad.Count == 0, n, "seed 61601, maxSpan " + maxSpanLo + ".." + maxSpanHi + " step 1, 400 pairs each; " + (bad.Count == 0 ? "no accepted out-of-range, cross-kind or foreign link" : string.Join("; ", bad.Take(4))));
        }
        {
            // auto-link selected: a spanning forest, every link legal, degree within MaxLinks, no cycle (conservation of components)
            var rng = new Random(61602); var bad = new List<string>(); int n = 0;
            for (int trial = 0; trial < 300; trial++)
            {
                int cnt = rng.Next(2, 12); var sel = new List<AnchorInfo>();
                for (int i = 0; i < cnt; i++) sel.Add(A(i + 1, rng.Next(0, 60), rng.Next(0, 60), 1, rng.Next(1, 5), rng.Next(5) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power));
                var links = AerialMath.MinimumSpanningLinks(sel, maxSpanDef); n++;
                var deg = sel.ToDictionary(s => s.Id, s => 0); var par = sel.ToDictionary(s => s.Id, s => s.Id);
                int F(int x) { while (par[x] != x) x = par[x]; return x; }
                foreach (var (p, q) in links)
                {
                    var a = sel.First(s => s.Id == p); var b = sel.First(s => s.Id == q);
                    if (AerialMath.CanLink(a, b, maxSpanDef) != LinkVerdict.Ok && AerialMath.CanLink(a, b, maxSpanDef) != LinkVerdict.FullA && AerialMath.CanLink(a, b, maxSpanDef) != LinkVerdict.FullB)
                        bad.Add("trial " + trial + " illegal link " + p + "-" + q + " " + AerialMath.CanLink(a, b, maxSpanDef));
                    deg[p]++; deg[q]++;
                    if (F(p) == F(q)) bad.Add("trial " + trial + " cycle at " + p + "-" + q); else par[F(p)] = F(q);
                }
                foreach (var s in sel) if (deg[s.Id] > s.MaxLinks) bad.Add("trial " + trial + " anchor " + s.Id + " degree " + deg[s.Id] + " > " + s.MaxLinks);
            }
            Row("L1_AUTOLINK_FOREST_RANDOM", new[] { "overhead_spans" }, "random", bad.Count == 0, n, "seed 61602, 300 selections of 2-11 anchors (1 in 5 a pipe pole): " + (bad.Count == 0 ? "every link legal, no cycle, no anchor over MaxLinks" : string.Join("; ", bad.Take(4))));
        }
        // ---------------------------------------------------------------- the sag: a hanging wire, ends exact, deepest mid-span
        {
            var rng = new Random(61603); var bad = new List<string>(); int n = 0;
            for (double sg = 0; sg <= sagHi + 1e-9; sg += 0.01)
                for (int i = 0; i < 60; i++)
                {
                    n++;
                    var a = new P2(rng.NextDouble() * 40, rng.NextDouble() * 40); var b = new P2(rng.NextDouble() * 40, rng.NextDouble() * 40);
                    double len = P2.Dist(a, b); if (len < 0.5 || Math.Abs(b.X - a.X) < 0.5 * len) continue; // the droop is screen-down: read it on spans that run more east-west than north-south
                    var pts = AerialMath.SpanCurve(a, b, sg);
                    if (P2.Dist(pts[0], a) > 1e-9 || P2.Dist(pts[pts.Count - 1], b) > 1e-9) bad.Add("ends moved sag " + sg);
                    double deepest = 0;
                    foreach (var p in pts)
                    {
                        double chordZ = a.Z + (b.Z - a.Z) * (p.X - a.X) / (b.X - a.X);
                        double below = chordZ - p.Z; if (below < -1e-9) bad.Add("point above chord sag " + sg); deepest = Math.Max(deepest, below);
                    }
                    // the drawn drop at the samples is sag x length x Droop(t); the full sag (SagDepth) is reached at t = 0.5, which a short span may not sample
                    double peak = AerialMath.SpanTs(len, 0.5).Max(t => AerialMath.Droop(t));
                    double want = AerialKinds.SagDepth(len, sg) * peak;
                    if (Math.Abs(deepest - want) > 1e-6 + 1e-9 * len) bad.Add("deepest " + deepest.ToString("0.000") + " want " + want.ToString("0.000") + " sag " + sg);
                    if (len >= 4 && peak < 0.9) bad.Add("span " + len.ToString("0.0") + " samples its middle at only " + peak.ToString("0.00") + " of the sag");
                }
            double defDepth = AerialKinds.SagDepth(10, AerialKinds.SagFor(AerialLineKind.Power, (float)sagDef, 0.02f));
            if (!(defDepth > 0)) bad.Add("default sag depth on a 10-cell span is " + defDepth);
            Row("L1_SAG_SWEEP", OS, "sweep", bad.Count == 0, n, "seed 61603, sag 0.." + sagHi + " step 0.01 x 60 random spans (east-west-ish; a north-south span's screen-down droop lies along its own line): ends exact, no point above the chord, drop below the chord at the same x = sag x length x Droop(t) at every sample, and spans of 4+ cells sample at least 90% of the full sag; default " + sagDef + " gives " + defDepth.ToString("0.00") + " cells on 10 " + (bad.Count == 0 ? "" : "| " + string.Join("; ", bad.Distinct().Take(4))));
        }
        {
            // the pole top: the wire leaves the insulator level (owner 2026-11-08, "needless kinks"): end segment angle off the chord
            var bad = new List<string>(); int n = 0; double worst = 0;
            for (double len = 4; len <= maxSpanHi; len += 1)
                for (double sg = 0.01; sg <= sagHi + 1e-9; sg += 0.02)
                {
                    n++;
                    var pts = AerialMath.SpanCurve(new P2(0, 0), new P2(len, 0), sg);
                    double ang = Math.Abs(Math.Atan2(pts[1].Z - pts[0].Z, pts[1].X - pts[0].X)) * 180 / Math.PI;
                    worst = Math.Max(worst, ang);
                }
            Row("L1_POLE_TOP_FLAT_SWEEP", new[] { "spans_above_everything", "no_unforced_sharp_turn" }, "sweep", worst < 5, n, "span 4.." + maxSpanHi + " x sag 0.01.." + sagHi + ": worst first-segment angle off the chord " + worst.ToString("0.00") + " deg (bar: no kink at the insulator; threshold 5 deg is this judge's)");
        }
        {
            // pipe spans: one rigid strand, no drip, no sway, never a power carrier; pipe sag clamped
            var bad = new List<string>(); int n = 0;
            for (int ms = 1; ms <= strandsHi; ms++) { n++; if (AerialKinds.StrandCap(AerialLineKind.Pipe, ms) != 1) bad.Add("pipe strands " + ms); if (AerialKinds.StrandCap(AerialLineKind.Power, ms) != ms) bad.Add("power strands " + ms); }
            n++; if (AerialKinds.Sways(AerialLineKind.Pipe) || AerialKinds.Drips(AerialLineKind.Pipe, true) || AerialKinds.CarriesPower(AerialLineKind.Pipe)) bad.Add("pipe sways/drips/carries power");
            n++; if (!AerialKinds.Sways(AerialLineKind.Power) || !AerialKinds.CarriesPower(AerialLineKind.Power) || AerialKinds.Drips(AerialLineKind.Power, false)) bad.Add("power kind wrong");
            foreach (float s in new[] { -1f, float.NaN, 0.5f, 0.1f }) { n++; float g = AerialKinds.SagFor(AerialLineKind.Pipe, 0.06f, s); if (!(g >= 0 && g <= AerialKinds.PipeSagMax)) bad.Add("pipe sag " + s + "->" + g); }
            foreach (float s in new[] { -1f, float.NaN }) { n++; float g = AerialKinds.SagFor(AerialLineKind.Power, s, 0.02f); if (!(g >= 0)) bad.Add("power sag " + s + "->" + g); }
            Row("L1_KIND_SPAN_SHAPE", new[] { "pipe_pole_switch", "overhead_spans" }, "fixed", bad.Count == 0, n, bad.Count == 0 ? "pipe span: 1 strand, no drip, no sway, carries no power, sag clamped to [0," + AerialKinds.PipeSagMax + "]; power sag NaN/negative -> 0" : string.Join("; ", bad));
        }
        {
            // strands: one per insulator, capped, every strand ends exactly on an insulator tip of each pole
            var rng = new Random(61604); var bad = new List<string>(); int n = 0;
            for (int ms = 1; ms <= strandsHi; ms++)
                for (int i = 0; i < 300; i++)
                {
                    n++;
                    int na = rng.Next(0, 5), nb = rng.Next(0, 5);
                    var ia = Enumerable.Range(0, na).Select(k => new P2(k * 0.3 - 0.5, 1.2)).ToList(); var ib = Enumerable.Range(0, nb).Select(k => new P2(k * 0.3 - 0.5, 1.2)).ToList();
                    var ba = new P2(rng.Next(0, 30), rng.Next(0, 30)); var bb = new P2(rng.Next(0, 30), rng.Next(0, 30));
                    var st = AerialMath.SpanStrands(ba, ia, bb, ib, rng.Next(), ms);
                    int want = Math.Max(1, Math.Min(Math.Min(Math.Max(1, na), Math.Max(1, nb)), ms));
                    if (st.Count != want) bad.Add("seed 61604 ms " + ms + " ins " + na + "/" + nb + ": " + st.Count + " strands want " + want);
                    foreach (var s in st)
                    {
                        if (na > 0 && !ia.Any(p => Math.Abs(ba.X + p.X - s.A.X) < 1e-9 && Math.Abs(ba.Z + p.Z - s.A.Z) < 1e-9)) bad.Add("strand end A off every insulator");
                        if (nb > 0 && !ib.Any(p => Math.Abs(bb.X + p.X - s.B.X) < 1e-9 && Math.Abs(bb.Z + p.Z - s.B.Z) < 1e-9)) bad.Add("strand end B off every insulator");
                    }
                    if (na >= st.Count && st.Select(s => s.InsA).Distinct().Count() != st.Count) bad.Add("two strands on one insulator at A with enough insulators");
                }
            Row("L1_STRANDS_RANDOM_SWEEP", new[] { "overhead_spans" }, "sweep", bad.Count == 0, n, "seed 61604, wires per span 1.." + strandsHi + " x 300 random pole pairs (0-4 insulators each): " + (bad.Count == 0 ? "count = min(insulators, setting, >=1); every strand ends on an insulator tip; distinct insulators" : string.Join("; ", bad.Distinct().Take(4))));
        }
        // ---------------------------------------------------------------- removal: killed falls, dismantled coils, the gravship keeps
        {
            var rng = new Random(61605); var bad = new List<string>(); int n = 0;
            for (int i = 0; i < 2000; i++)
            {
                n++;
                int cnt = rng.Next(0, 6); var spans = new List<(int, SpanState)>();
                for (int k = 0; k < cnt; k++) spans.Add((rng.Next(2, 9), rng.Next(3) == 0 ? SpanState.Cut : SpanState.Up));
                bool killed = rng.Next(2) == 0; bool gs = !killed && rng.Next(2) == 0;
                var aboard = gs ? new HashSet<int>(Enumerable.Range(2, 7).Where(_ => rng.Next(2) == 0)) : null;
                var plan = AerialMath.PlanRemoval(1, killed, spans, aboard);
                var partners = spans.Select(s => s.Item1).Distinct().ToList();
                int upSpans = spans.Count(s => s.Item2 == SpanState.Up);
                if (killed)
                {
                    if (plan.Fallen.Count != upSpans) bad.Add("seed 61605 i " + i + ": killed with " + upSpans + " up spans, " + plan.Fallen.Count + " fall");
                    if (plan.Fallen.Any(f => !f.TowardDead)) bad.Add("fallen not toward the dead mast");
                    if (!partners.All(plan.Reseed.Contains)) bad.Add("killed: a partner not re-seeded");
                }
                else if (plan.Fallen.Count != 0) bad.Add("i " + i + ": dismantled/lifted but " + plan.Fallen.Count + " fall");
                if (gs)
                {
                    var kept = partners.Where(aboard.Contains).ToList(); var left = partners.Where(p => !aboard.Contains(p)).ToList();
                    if (!kept.OrderBy(x => x).SequenceEqual(plan.Kept.OrderBy(x => x)) || !left.OrderBy(x => x).SequenceEqual(plan.Grounded.OrderBy(x => x)))
                        bad.Add("i " + i + ": gravship kept/grounded split wrong");
                    if (!left.All(plan.Reseed.Contains)) bad.Add("gravship: a partner left behind not re-seeded");
                }
                else if (!killed && !partners.All(plan.Reseed.Contains)) bad.Add("dismantled: partner not re-seeded");
                if (plan.Reseed.Contains(1)) bad.Add("re-seeds itself");
            }
            Row("L1_REMOVAL_RANDOM", new[] { "fallen_span_on_ground", "downed_spans", "gravship_keeps_connections", "gravship_connectivity" }, "random", bad.Count == 0, n,
                "seed 61605, 2000 removals (killed / dismantled / lifted on a gravship with a random crew): " + (bad.Count == 0 ? "killed: exactly one fallen wire per UP span (a cut span drops nothing new), every partner re-seeded; dismantled or lifted: nothing falls; lifted: partners aboard kept, left ones grounded and re-seeded" : string.Join("; ", bad.Distinct().Take(4))));
        }
        {
            var bad = new List<string>(); int n = 0;
            var reads = new List<SpanNetRead> {
                new SpanNetRead { Span = 1, NetA = 3, NetB = 3, State = SpanState.Up }, new SpanNetRead { Span = 2, NetA = 3, NetB = 4, State = SpanState.Up },
                new SpanNetRead { Span = 3, NetA = -1, NetB = 3, State = SpanState.Up }, new SpanNetRead { Span = 4, NetA = 3, NetB = 4, State = SpanState.Cut },
                new SpanNetRead { Span = 5, NetA = -1, NetB = -1, State = SpanState.Cut } };
            var rep = AerialMath.WatchdogRepairs(reads); n = reads.Count;
            if (!rep.OrderBy(x => x).SequenceEqual(new[] { 2, 3 })) bad.Add("repairs " + string.Join(",", rep));
            var ro = AerialMath.ReseedOnLinkChange(4, 7); if (!(ro.Count == 2 && ro.Contains(4) && ro.Contains(7))) bad.Add("link change re-seeds " + string.Join(",", ro));
            Row("L1_WATCHDOG_FIXED", new[] { "cut_live_and_dead_ends", "connectivity_truth" }, "fixed", bad.Count == 0, n + 1, bad.Count == 0 ? "an UP span on two nets or a null net is repaired; a CUT span splitting its nets is left split; a link change re-seeds both ends" : string.Join("; ", bad));
        }
        // ---------------------------------------------------------------- blasts: cut, sway, nothing
        {
            var rng = new Random(61606); var bad = new List<string>(); int n = 0;
            foreach (bool cutOn in new[] { true, false })
                foreach (bool kin in new[] { true, false })
                    foreach (bool kinSway in new[] { true, false })
                        foreach (bool harms in new[] { true, false })
                        {
                            var k = AerialMath.BlastKindFor(harms, kin, 50, cutOn, kinSway); n++;
                            var want = !harms ? AerialMath.BlastKind.None : kin ? (kinSway ? AerialMath.BlastKind.Sway : AerialMath.BlastKind.None) : (cutOn ? AerialMath.BlastKind.Cut : AerialMath.BlastKind.None);
                            if (k != want) bad.Add("harms " + harms + " kinetic " + kin + " cut " + cutOn + " sway " + kinSway + ": " + k);
                        }
            for (int i = 0; i < 3000; i++)
            {
                n++;
                var a = new P2(rng.NextDouble() * 30, rng.NextDouble() * 30); var b = new P2(rng.NextDouble() * 30, rng.NextDouble() * 30);
                var c = new P2(rng.NextDouble() * 30, rng.NextDouble() * 30); double rad = 0.5 + rng.NextDouble() * 6, hp = 1 + rng.NextDouble() * 100, dmg = rng.NextDouble() * 120;
                var r = AerialMath.BlastSpan(a, b, c, rad, hp, dmg, AerialMath.BlastKind.Cut);
                double d = P2.Dist(P2.Lerp(a, b, AerialMath.ClosestT(a, b, c)), c);
                if (d > rad + 1e-9 && (r.Hit || r.Cut || r.Hp != hp)) bad.Add("seed 61606 i " + i + ": blast out of reach touched the span");
                if (d <= rad && (r.Hp > hp - 0.2 * dmg + 1e-9 || r.Hp < hp - dmg - 1e-9)) bad.Add("i " + i + ": hp loss outside [20%,100%] of damage");
                if (r.Cut != (r.Hp <= 0)) bad.Add("i " + i + ": cut flag disagrees with hp");
                var s = AerialMath.BlastSpan(a, b, c, rad, hp, dmg, AerialMath.BlastKind.Sway);
                if (s.Cut || s.Hp != hp) bad.Add("i " + i + ": a sway blast wounded the span");
            }
            Row("L1_BLAST_RANDOM", new[] { "cut_live_and_dead_ends", "break_ends_live_dead", "settings_switch_cleanly" }, "random", bad.Count == 0, n,
                "seed 61606: the 16 switch combinations (explosionsCut, kineticSway) and 3000 random blasts: " + (bad.Count == 0 ? "kinetic never cuts, a switched-off cut never cuts, out-of-reach blasts touch nothing, hp loss between 20% and 100% of damage, cut iff hp <= 0, sway never wounds" : string.Join("; ", bad.Distinct().Take(4))));
        }
        // ---------------------------------------------------------------- shock: who is bitten
        {
            var bad = new List<string>(); int n = 0;
            foreach (bool flesh in new[] { true, false }) foreach (bool dead in new[] { true, false }) foreach (bool outd in new[] { true, false }) foreach (bool fix in new[] { true, false })
            {
                n++; bool want = flesh && !dead && !outd && !fix;
                if (AerialMath.ShockTakes(flesh, dead, outd, fix) != want) bad.Add("ShockTakes(" + flesh + "," + dead + "," + outd + "," + fix + ")");
            }
            Row("L1_SHOCK_TAKES_TABLE", new[] { "fallen_wire_shocks_crossers", "fallen_wire_shock" }, "fixed", bad.Count == 0, n, bad.Count == 0 ? "16 cases: a live fallen wire bites any living, standing flesh pawn except the one re-stringing THAT wire" : string.Join("; ", bad));
        }
        {
            // the three-way setting: floor ends only under All; downed spans and dropped cords under Only downed lines and All; nothing under None
            var bad = new List<string>(); int n = 0;
            foreach (ShockReach r in Enum.GetValues(typeof(ShockReach)))
                foreach (LineKind k in Enum.GetValues(typeof(LineKind)))
                    foreach (bool live in new[] { true, false }) foreach (bool fix in new[] { true, false }) foreach (bool flesh in new[] { true, false })
                    {
                        n++;
                        bool reach = r == ShockReach.All || (r == ShockReach.OnlyDownedLines && k != LineKind.FloorEnd);
                        bool want = reach && live && flesh && !fix;
                        if (ShockRule.Takes(r, k, live, flesh, false, false, fix) != want) bad.Add(r + "/" + k + " live " + live + " fix " + fix + " flesh " + flesh);
                    }
            var def = ShockRule.Parse(shockDef); n++;
            if (def != ShockReach.All) bad.Add("shipped default parses to " + def);
            foreach (var s in new[] { "2", "all", "", "Everything", null }) { n++; if (s != null && ShockRule.Parse(s) != null) bad.Add("Parse accepted '" + s + "'"); }
            foreach (var s in new[] { "None", "OnlyDownedLines", "All" }) { n++; if (ShockRule.Parse(s)?.ToString() != s) bad.Add("Parse(" + s + ")"); }
            Row("L1_SHOCK_REACH_TABLE", new[] { "shock_reach_setting", "floor_end_shocks_crossers", "fallen_wire_shocks_crossers", "floor_end_shock" }, "sweep", bad.Count == 0, n,
                "every setting x line kind x live x fixer x flesh (" + (n - 9) + " cases) + the shipped default '" + shockDef + "' + Parse: " + (bad.Count == 0 ? "None bites nothing; Only downed lines bites downed spans and FlowWorks' dropped cords, never a floor end; All bites all three; dead lines and the fixer of that line never" : string.Join("; ", bad.Take(5))));
        }
        {
            // floor-end fixer scope: only a build target on the end cell or one of its four neighbours exempts; the bite is the tip's one cell
            var bad = new List<string>(); int n = 0;
            for (int dx = -3; dx <= 3; dx++) for (int dz = -3; dz <= 3; dz++)
            {
                n++; bool want = Math.Abs(dx) + Math.Abs(dz) <= 1;
                if (ShockRule.TargetJoinsEnd(10, 10, 10 + dx, 10 + dz) != want) bad.Add("target offset " + dx + "," + dz);
            }
            var rng = new Random(61607);
            for (int i = 0; i < 500; i++) { n++; double x = rng.NextDouble() * 200 - 100, z = rng.NextDouble() * 200 - 100; var c = ShockRule.EndCell(x, z); if (c.x != (int)Math.Floor(x) || c.z != (int)Math.Floor(z)) bad.Add("EndCell(" + x + "," + z + ")"); }
            Row("L1_FLOOR_END_FIXER_SCOPE", new[] { "floor_end_shocks_crossers", "floor_end_shock" }, "fixed", bad.Count == 0, n, "seed 61607: " + (bad.Count == 0 ? "a constructor is exempt only for a target on the end cell or its four neighbours (diagonal and two away are shocked); the bite is the one cell under the drawn tip, negative coordinates floored" : string.Join("; ", bad.Take(4))));
        }
        // ---------------------------------------------------------------- restring
        {
            var bad = new List<string>(); int n = 0; int prev = int.MaxValue;
            if (AerialMath.RestringTicks(1.0) != 300) bad.Add("speed 1 -> " + AerialMath.RestringTicks(1.0));
            for (double s = 0; s <= 3.0001; s += 0.05) { n++; int t = AerialMath.RestringTicks(s); if (t <= 0 || t > prev) bad.Add("speed " + s.ToString("0.00") + " -> " + t); prev = t; }
            n++; if (AerialMath.RestringTicks(double.NaN) <= 0) bad.Add("NaN speed -> " + AerialMath.RestringTicks(double.NaN));
            Row("L1_RESTRING_TICKS_SWEEP", new[] { "restring_cut_span", "restring_job" }, "sweep", bad.Count == 0, n + 1, bad.Count == 0 ? "300 ticks at speed 1; positive and never longer for a faster worker over speed 0..3 (0 clamps to 3000)" : string.Join("; ", bad.Take(4)));
        }
        // ---------------------------------------------------------------- the tap: nothing made from nothing
        {
            var rng = new Random(61608); var bad = new List<string>(); int n = 0; const double k = 1.0 / 60000;
            for (double rate = tapLo; rate <= tapHi; rate += 50)
                for (int i = 0; i < 200; i++)
                {
                    n++;
                    double raw = rng.NextDouble() * 0.05 - 0.02, stored = rng.Next(3) == 0 ? 0 : rng.NextDouble() * 2; int taps = rng.Next(1, 5);
                    double taken = 0; bool off = rng.Next(6) == 0, same = rng.Next(8) == 0;
                    for (int t = 0; t < taps; t++)
                    {
                        double got = AerialMath.TapStolenPerTick(rate, raw, stored, k, same, !off, taken, true);
                        if (got < 0 || got > rate * k + 1e-15) bad.Add("seed 61608 rate " + rate + " i " + i + ": one tap took " + got + " (cap " + rate * k + ")");
                        taken += got;
                    }
                    if (taken > Math.Max(0, raw + Math.Max(0, stored)) + 1e-12) bad.Add("seed 61608 rate " + rate + " i " + i + ": " + taps + " taps took " + taken + " of raw " + raw + " + stored " + stored);
                    if ((off || same) && taken != 0) bad.Add("off/same net took " + taken);
                }
            foreach (double bogus in new[] { double.NaN, double.PositiveInfinity, -5, 0 }) { n++; if (AerialMath.TapStolenPerTick(bogus, 1, 1, k, false, true) != 0) bad.Add("rate " + bogus + " took power"); }
            n++; if (AerialMath.TapStolenPerTick(500, double.NaN, 1, k, false, true) != 0) bad.Add("NaN gain took power");
            n++; if (AerialMath.TapStolenPerTick(500, 1, 1, k, false, true, 0, false) != 0) bad.Add("broken-down clamp took power");
            Row("L1_TAP_CONSERVATION_SWEEP", new[] { "tap_steals_and_costs_goodwill", "power_theft" }, "sweep", bad.Count == 0, n,
                "seed 61608, tap rate " + tapLo + ".." + tapHi + " step 50 x 200 victims, 1-4 taps sharing a victim: " + (bad.Count == 0 ? "each tap within [0, rate x k]; all taps together never take more than the victim's gain + stored; off, own net, broken-down, NaN/inf rate take nothing" : string.Join("; ", bad.Distinct().Take(4))));
        }
        {
            // caught theft: spotted needs range, sight, an awake free witness; the leak is steady and charges whole draining days only
            var rng = new Random(61609); var bad = new List<string>(); int n = 0;
            for (double sight = sightLo; sight <= sightHi; sight += 1)
                for (int i = 0; i < 100; i++)
                {
                    n++; double d = rng.NextDouble() * 40; bool los = rng.Next(2) == 0, up = rng.Next(2) == 0, held = rng.Next(4) == 0;
                    bool want = d <= sight && los && up && !held;
                    if (AerialMath.TheftSpotted(d, sight, los, up, held) != want) bad.Add("sight " + sight + " d " + d.ToString("0.0"));
                }
            n++; if (AerialMath.TheftSpotted(double.NaN, sightDef, true, true, false)) bad.Add("NaN distance spotted");
            const int TPD = 60000;
            for (int perDay = 0; perDay <= perDayHi; perDay++)
                for (int trial = 0; trial < 50; trial++)
                {
                    n++; int acc = 0, total = 0; long drained = 0;
                    for (int c = 0; c < 200; c++)
                    {
                        int ticks = rng.Next(0, 5000); bool draining = rng.Next(4) != 0;
                        int g = AerialMath.TheftGoodwillAccrue(ref acc, ticks, draining, perDay, TPD);
                        if (g > 0) bad.Add("goodwill rose"); total += g; if (draining) drained += ticks;
                    }
                    long wantTotal = -(drained / TPD) * perDay;
                    if (total != wantTotal || acc != drained % TPD) bad.Add("seed 61609 perDay " + perDay + " trial " + trial + ": charged " + total + " want " + wantTotal + ", carry " + acc + " want " + drained % TPD);
                }
            Row("L1_THEFT_SPOT_AND_LEAK_SWEEP", new[] { "tap_steals_and_costs_goodwill", "power_theft" }, "sweep", bad.Count == 0, n,
                "seed 61609, sight " + sightLo + ".." + sightHi + " x 100 witnesses; goodwill per day 0.." + perDayHi + " x 50 runs of 200 random chunks: " + (bad.Count == 0 ? "spotted exactly when in range with line of sight, awake and free; charged exactly perDay per whole day of DRAINING (idle time free, remainder carried, nothing lost or created)" : string.Join("; ", bad.Distinct().Take(4))));
        }
        // ---------------------------------------------------------------- switches: pipe poles answer to their own switch
        {
            var bad = new List<string>(); int n = 0;
            foreach (bool pw in new[] { true, false }) foreach (bool pp in new[] { true, false }) foreach (bool st in new[] { true, false })
            {
                n += 4;
                if (AerialKinds.KindOn(AerialLineKind.Power, pw, pp) != pw) bad.Add("power anchor follows the pipe switch");
                if (AerialKinds.KindOn(AerialLineKind.Pipe, pw, pp) != pp) bad.Add("pipe pole follows the power master");
                if (AerialKinds.KindBehaviour(AerialLineKind.Power, pw, pp, st) != (pw && st)) bad.Add("power behaviour");
                if (AerialKinds.KindBehaviour(AerialLineKind.Pipe, pw, pp, st) != pp) bad.Add("pipe behaviour reads a power setting");
            }
            for (int m = 0; m < 3; m++) foreach (bool pref in new[] { true, false }) { n++; bool want = m == 1 || (m == 0 && pref); if (AerialMath.WireSwayPrefAllows(m, pref) != want) bad.Add("sway mode " + m + " pref " + pref); }
            Row("L1_SWITCH_TABLES", new[] { "settings_switch_cleanly", "pipe_pole_switch", "mod_settings" }, "fixed", bad.Count == 0, n, bad.Count == 0 ? "power anchors follow only the power master (and their own setting); pipe poles only their own switch; sway Auto follows the plant-sway preference, CPU always, Off never" : string.Join("; ", bad.Distinct()));
        }
        {
            // sway: zero at both insulators, zero without wind, bounded; strength swept 0..2; blast sway dies by 180 ticks
            var rng = new Random(61610); var bad = new List<string>(); int n = 0;
            for (double amp = 0; amp <= 2.0001; amp += 0.25)
                for (int i = 0; i < 300; i++)
                {
                    n++; double t = rng.NextDouble(), time = rng.NextDouble() * 1000, wind = rng.NextDouble() * 3; int seed = rng.Next();
                    double o = AerialMath.Sway(t, time, wind, amp, seed); double cap = 1.3 * amp * Math.Min(wind, 1.5) / 1.5 + 1e-12;
                    if (Math.Abs(o) > cap) bad.Add("seed 61610 amp " + amp + " i " + i + ": |sway| " + o + " > " + cap);
                    if (AerialMath.Sway(0, time, wind, amp, seed) != 0 || AerialMath.Sway(1, time, wind, amp, seed) != 0 || AerialMath.Sway(t, time, 0, amp, seed) != 0) bad.Add("sway at an insulator or without wind");
                    int age = rng.Next(0, 400);
                    double bs = AerialMath.BlastSway(t, age, 1, 1, amp, seed);
                    if (age >= AerialMath.BlastSwayTicks && bs != 0) bad.Add("blast sway alive at " + age);
                    if (AerialMath.BlastSway(0, age, 1, 1, amp, seed) != 0 || AerialMath.BlastSway(1, age, 1, 1, amp, seed) != 0) bad.Add("blast sway moves an insulator");
                }
            Row("L1_SWAY_BOUNDS_SWEEP", new[] { "settings_switch_cleanly", "overhead_spans" }, "sweep", bad.Count == 0, n, "seed 61610, sway strength 0..2 step 0.25 x 300: " + (bad.Count == 0 ? "zero at both insulators and with no wind, never past 1.3 x amp x min(wind,1.5)/1.5; blast sway still at both ends and gone from tick 180" : string.Join("; ", bad.Distinct().Take(4))));
        }
        // ---------------------------------------------------------------- the fallen wire lies on walkable ground
        {
            var rng = new Random(61611); var bad = new List<string>(); int n = 0, grounded = 0, blocked = 0, atFace = 0; double maxDepth = 0; const double FaceTol = 0.10;
            for (int i = 0; i < 1500; i++)
            {
                n++;
                var wall = new HashSet<(int, int)>(); int wc = rng.Next(0, 25);
                for (int w = 0; w < wc; w++) wall.Add((rng.Next(0, 30), rng.Next(0, 30)));
                var basePt = new P2(rng.Next(5, 25) + 0.5, rng.Next(5, 25) + 0.5); wall.Remove(((int)basePt.X, (int)basePt.Z));
                var toward = new P2(rng.Next(0, 30) + 0.5, rng.Next(0, 30) + 0.5);
                if (P2.Dist(toward, basePt) < 2) continue;
                var top = new P2(basePt.X, basePt.Z + 1.2);
                double len = P2.Dist(basePt, toward) * 1.05;
                Func<int, int, bool> walk = (x, z) => x >= 0 && z >= 0 && x < 30 && z < 30 && !wall.Contains((x, z));
                FallenLay l;
                try { l = AerialMath.LayFallen(top, basePt, toward, len, rng.Next(), walk); }
                catch (Exception e) { bad.Add("seed 61611 i " + i + ": threw " + e.GetType().Name); continue; }
                if (l.TipGrounded) grounded++; if (l.Blocked) blocked++;
                foreach (var p in AerialMath.GroundPts(l))
                {
                    var dv = new P2(p.X - basePt.X, p.Z - basePt.Z);
                    if (Math.Sqrt(dv.X * dv.X + dv.Z * dv.Z) < 0.75) continue; // the first 0.75 cell is exempt (a bracket sits on its wall face)
                    if (!walk((int)Math.Floor(p.X), (int)Math.Floor(p.Z)))
                    {
                        // depth into the wall: distance to the nearest walkable cell's square (a point on the face is 0 deep)
                        int cx = (int)Math.Floor(p.X), cz = (int)Math.Floor(p.Z); double depth = 9;
                        for (int ox = -2; ox <= 2; ox++) for (int oz = -2; oz <= 2; oz++)
                            if (walk(cx + ox, cz + oz)) { double ddx = Math.Max(0, Math.Max(cx + ox - p.X, p.X - (cx + ox + 1))), ddz = Math.Max(0, Math.Max(cz + oz - p.Z, p.Z - (cz + oz + 1))); depth = Math.Min(depth, Math.Sqrt(ddx * ddx + ddz * ddz)); }
                        maxDepth = Math.Max(maxDepth, depth);
                        if (depth > FaceTol) { bad.Add("seed 61611 i " + i + ": grounded point " + p + " " + depth.ToString("0.00") + " cell inside a wall (walls " + wc + ")"); break; }
                        atFace++;
                    }
                }
                if (!l.TipGrounded && !l.Blocked) bad.Add("seed 61611 i " + i + ": the wire never reached the ground and was not stopped");
                foreach (var p in AerialMath.GroundPts(l)) { if (!AerialMath.LayTouches(l, (int)Math.Floor(p.X), (int)Math.Floor(p.Z))) { bad.Add("LayTouches misses a grounded point"); break; } }
            }
            Row("L1_FALLEN_LAY_RANDOM", new[] { "fallen_span_on_ground", "downed_spans", "cords_meet_walls_at_face" }, "random", bad.Count == 0, n,
                "seed 61611, 1500 killed spans on 30x30 grids with 0-24 wall cells: " + grounded + " tips grounded, " + blocked + " stopped by a wall, " + atFace + " grounded points on a wall face (deepest " + maxDepth.ToString("0.000") + " cell; tolerance " + FaceTol + " is this judge's); " + (bad.Count == 0 ? "every grounded point (past the exempt first 0.75 cell) lies on walkable ground or on a wall face, a wire that does not reach the ground is one a wall stopped, the shock contacts cover every grounded point" : string.Join("; ", bad.Distinct().Take(4))));
        }
        // ---------------------------------------------------------------- the shipped assembly: no hose or reel type (no_hose bars)
        {
            string dll = Environment.GetEnvironmentVariable("GSS_DLL");
            if (string.IsNullOrEmpty(dll) || !System.IO.File.Exists(dll)) Row("NH_DLL_TYPES", new[] { "no_hose", "no_hose_in_gss" }, "fixed", false, 0, "assembly not found: " + dll, "UNSETTLED");
            else
            {
                using var fs = System.IO.File.OpenRead(dll);
                using var pe = new System.Reflection.PortableExecutable.PEReader(fs);
                var md = System.Reflection.Metadata.PEReaderExtensions.GetMetadataReader(pe);
                var bad = new List<string>(); var members = new List<string>(); int n = 0;
                var rx = new System.Text.RegularExpressions.Regex("(?i)hose|reel");
                foreach (var h in md.TypeDefinitions)
                {
                    var t = md.GetTypeDefinition(h); string name = md.GetString(t.Name), ns = md.GetString(t.Namespace); n++;
                    if (rx.IsMatch(name) || rx.IsMatch(ns)) bad.Add(ns + "." + name);
                    foreach (var mh in t.GetMethods()) { string m = md.GetString(md.GetMethodDefinition(mh).Name); if (rx.IsMatch(m)) members.Add(name + "." + m); }
                    foreach (var fh in t.GetFields()) { string f = md.GetString(md.GetFieldDefinition(fh).Name); if (rx.IsMatch(f)) members.Add(name + "." + f); }
                }
                Row("NH_DLL_TYPES", new[] { "no_hose", "no_hose_in_gss" }, "fixed", bad.Count == 0, n, n + " type definitions in the shipped DLL: " + (bad.Count == 0 ? "none names a hose or reel" : "hose/reel types " + string.Join(", ", bad.Take(6)))
                    + "; hose-named members (draw-order numbers, INFO): " + string.Join(", ", members.Distinct().Take(8)));
            }
        }
        // ---------------------------------------------------------------- bars this kernel cannot decide (game-side)
        void NK(string id, string[] bars, string why) => Row(id, bars, "not_kernel", true, 0, why, "UNSETTLED");
        NK("NK_SPAN_ALTITUDE", new[] { "spans_above_everything" }, "draw altitude above pawns and buildings is a render-queue/altitude read in the game (AerialMaterials, SectionLayer); the kernel holds geometry only. Stage 6.");
        NK("NK_SHOCK_JOB_TARGET", new[] { "fallen_wire_shocks_crossers" }, "the exemption must key on the wire the RM_RestringSpan job targets, not the job type: decided by RM_FallenWireShock's caller in game; the kernel takes a bool. Stage 6.");
        NK("NK_TAP_GOODWILL_FACTION", new[] { "tap_steals_and_costs_goodwill" }, "which faction's goodwill falls (only the victim's) is PowerTheftConsequences in game. Stage 6.");
        NK("NK_OWNER_CHANGE", new[] { "owner_change_coils_wires", "owner_change_cut" }, "the owner-mismatch sweep runs on live Things. Stage 6.");
        NK("NK_FUEL_IGNITION", new[] { "live_wire_lights_fuel" }, "ignition of a puddle is a game read. Stage 6.");
        return fails == 0 ? 0 : 1;
    }
}
