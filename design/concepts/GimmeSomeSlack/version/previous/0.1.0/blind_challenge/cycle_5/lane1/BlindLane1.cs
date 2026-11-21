// Blind lane 1, cycle 5, GimmeSomeSlack 0.1.0: game-logic tests written from the bars (tree.json, sheet.md) and the
// shipped settings (AerialSettings.cs defaults and slider ranges) alone, against the kernel AerialMath.cs.
// One JSON row per line on stdout. Exit 0 = no FAIL row, 1 = some FAIL.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.GimmeSomeSlack.Aerial;

static class BlindLane1
{
    static int fails;
    static string J(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";
    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") fails++;
        Console.WriteLine("{\"id\": " + J(id) + ", \"bars\": [" + string.Join(", ", bars.Select(J)) + "], \"kind\": " + J(kind) +
                          ", \"verdict\": " + J(verdict) + ", \"cases\": " + cases + ", \"detail\": " + J(detail) + "}");
    }
    static string F(double d) => d.ToString("0.####", CultureInfo.InvariantCulture);

    // shipped settings (AerialSettings.cs): defaults and slider ranges
    const float SagDefault = 0.06f, SagMin = 0f, SagMax = 0.15f;
    const float SpanDefault = 20f, SpanSliderMin = 8f, SpanSliderMax = 40f;
    const int StrandsDefault = 3, StrandsMin = 1, StrandsMax = 3;
    const float TapRateDefault = 500f, TapRateMin = 50f, TapRateMax = 2000f;
    const int GoodwillDefault = 2, GoodwillMin = 0, GoodwillMax = 10;
    const float SightDefault = 12f, SightMin = 3f, SightMax = 30f;
    const float SwayDefault = 1f, SwayMin = 0f, SwayMax = 2f;
    const double WattsToWattDaysPerTick = 1.0 / 60000.0;   // RimWorld CompPower.WattsToWattDaysPerTick
    const int TicksPerDay = 60000;

    static void Main()
    {
        Console.OutputEncoding = new UTF8Encoding(false); CultureInfo.DefaultThreadCurrentCulture = CultureInfo.InvariantCulture; CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
        Spans(); Links(); Removal(); Tap(); Theft(); Restring(); Shock(); Blast(); Fallen(); Strands(); Kinds(); Sway();
        Environment.Exit(fails > 0 ? 1 : 0);
    }

    // ---------------------------------------------------------------- spans_above_everything: sagging, never ruler-straight
    static double PerpDev(List<P2> pts, P2 a, P2 b)
    {
        double len = P2.Dist(a, b), best = 0;
        foreach (P2 p in pts)
        {
            double cross = ((b.X - a.X) * (p.Z - a.Z) - (b.Z - a.Z) * (p.X - a.X)) / len;
            best = Math.Max(best, Math.Abs(cross));
        }
        return best;
    }
    static void Spans()
    {
        // sweep: every sag on the slider (0..0.15 by 0.01) x span lengths 4..40: ends exact, deepest drop = sag x length
        int cases = 0, bad = 0; string first = null;
        for (int si = 0; si <= 15; si++)
            for (int len = 4; len <= 40; len += 4)
            {
                double sag = si / 100.0; cases++;
                var a = new P2(0, 0); var b = new P2(len, 0);
                var pts = AerialMath.SpanCurve(a, b, sag);
                double drop = pts.Max(p => -p.Z);
                bool endsOk = P2.Dist(pts[0], a) < 1e-9 && P2.Dist(pts[pts.Count - 1], b) < 1e-9;
                bool dropOk = Math.Abs(drop - sag * len) <= 0.02 * Math.Max(1, sag * len);
                bool noRise = pts.All(p => p.Z <= 1e-9);
                if (!(endsOk && dropOk && noRise)) { bad++; first = first ?? $"sag {F(sag)} len {len}: ends {endsOk} drop {F(drop)} vs {F(sag * len)} rise {!noRise}"; }
            }
        Row("L1_SPAN_SAG_SWEEP", new[] { "spans_above_everything", "overhead_spans" }, "sweep", bad == 0 ? "PASS" : "FAIL", cases,
            bad == 0 ? "sag slider 0..0.15 x length 4..40: ends exactly on the insulators, deepest drop = sag x length, never above the chord"
                     : bad + " bad; first " + first);

        // the slider's own minimum: sag 0 draws the chord exactly
        var z = AerialMath.SpanCurve(new P2(0, 0), new P2(20, 0), 0);
        Row("L1_SPAN_SAG_SLIDER_ZERO_IS_STRAIGHT", new[] { "spans_above_everything" }, "info", "INFO", 1,
            "sag slider minimum " + F(SagMin) + " (AerialSettings.cs Slider(sag, 0, 0.15)): a 20-cell span's largest drop " + F(z.Max(p => -p.Z)) +
            " cell, i.e. ruler-straight by player choice; the default " + F(SagDefault) + " drops " + F(SagDefault * 20) + " cell; SagFor(Power) clamps NaN/negative to 0 and has no upper clamp: SagFor(Power, 5) = " +
            F(AerialKinds.SagFor(AerialLineKind.Power, 5f, 0f)));

        // random: every bearing at the default sag, the drawn wire must visibly leave its chord (screen-down droop)
        var rng = new Random(5150); int n = 2000, straight = 0; double worst = 1e9; P2 wa = default, wb = default;
        for (int i = 0; i < n; i++)
        {
            double ang = rng.NextDouble() * 2 * Math.PI, len = 8 + rng.NextDouble() * 32;
            var a = new P2(rng.Next(0, 200), rng.Next(0, 200)); var b = new P2(a.X + len * Math.Cos(ang), a.Z + len * Math.Sin(ang));
            double dev = PerpDev(AerialMath.SpanCurve(a, b, SagDefault), a, b);
            if (dev < 0.1) straight++;
            if (dev < worst) { worst = dev; wa = a; wb = b; }
        }
        // shrink: the straightest bearing is the pure north-south one
        var ns = AerialMath.SpanCurve(new P2(0, 0), new P2(0, 8), SagDefault);
        double nsDev = PerpDev(ns, new P2(0, 0), new P2(0, 8));
        Row("L1_SPAN_VISIBLE_OFF_CHORD_EVERY_BEARING", new[] { "spans_above_everything" }, "random", straight == 0 ? "PASS" : "FAIL", n,
            $"seed 5150, default sag {F(SagDefault)}, spans 8..40 cells: {straight} of {n} leave their chord by under 0.1 cell sideways (worst {F(worst)} cell, {wa}->{wb}); " +
            $"shrunk: (0,0)->(0,8) north-south, largest sideways offset {F(nsDev)} cell: the droop is screen-down, along the span, so the line is drawn on its own chord");
    }

    // ---------------------------------------------------------------- link rules: spans_above_everything's three bad links refused
    static AnchorInfo A(int id, int x, int z, int fac = 0, int max = 4, bool roof = false, AerialLineKind k = AerialLineKind.Power, bool anchor = true)
        => new AnchorInfo { Id = id, X = x, Z = z, Faction = fac, MaxLinks = max, Roofed = roof, Kind = k, IsAnchor = anchor };
    static LinkVerdict Oracle(AnchorInfo a, AnchorInfo b, double range)
    {
        // my own reading of the bar: a link is allowed only between two distinct anchors of one kind and one faction, not
        // already linked, neither roofed, within range, both with a free slot
        if (a.Id == b.Id) return LinkVerdict.Self;
        bool ok = a.IsAnchor && b.IsAnchor && a.Kind == b.Kind && a.Faction == b.Faction && !a.Linked.Contains(b.Id) && !b.Linked.Contains(a.Id)
                  && !a.Roofed && !b.Roofed && (a.X - b.X) * (long)(a.X - b.X) + (a.Z - b.Z) * (long)(a.Z - b.Z) <= range * range + 1e-9
                  && a.Linked.Count < a.MaxLinks && b.Linked.Count < b.MaxLinks;
        return ok ? LinkVerdict.Ok : LinkVerdict.OutOfRange;   // only Ok-ness is compared
    }
    static void Links()
    {
        double r = SpanDefault; var cases = new List<(string, LinkVerdict, LinkVerdict)>();
        var a = A(1, 0, 0);
        cases.Add(("self", AerialMath.CanLink(a, a, r), LinkVerdict.Self));
        cases.Add(("not anchor", AerialMath.CanLink(a, A(2, 3, 0, anchor: false), r), LinkVerdict.NotAnchor));
        cases.Add(("wrong kind", AerialMath.CanLink(a, A(2, 3, 0, k: AerialLineKind.Pipe), r), LinkVerdict.WrongKind));
        cases.Add(("foreign", AerialMath.CanLink(a, A(2, 3, 0, fac: 1), r), LinkVerdict.Foreign));
        cases.Add(("roofed", AerialMath.CanLink(a, A(2, 3, 0, roof: true), r), LinkVerdict.Roofed));
        cases.Add(("out of range by 1", AerialMath.CanLink(a, A(2, 21, 0), r), LinkVerdict.OutOfRange));
        cases.Add(("exactly at range", AerialMath.CanLink(a, A(2, 20, 0), r), LinkVerdict.Ok));
        cases.Add(("diagonal just over (15,14)", AerialMath.CanLink(a, A(2, 15, 14), r), LinkVerdict.OutOfRange));
        var full = A(3, 0, 0, max: 1); full.Linked.Add(9);
        cases.Add(("full A", AerialMath.CanLink(full, A(2, 3, 0), r), LinkVerdict.FullA));
        var al = A(4, 0, 0); al.Linked.Add(2);
        cases.Add(("already linked", AerialMath.CanLink(al, A(2, 3, 0), r), LinkVerdict.AlreadyLinked));
        int bad = cases.Count(c => c.Item2 != c.Item3);
        Row("L1_CANLINK_FIXED", new[] { "spans_above_everything", "overhead_spans" }, "fixed", bad == 0 ? "PASS" : "FAIL", cases.Count,
            bad == 0 ? "self, not-anchor, wrong kind, foreign, roofed, out of range, at range, full, already linked: each answered as the bar says"
                     : string.Join("; ", cases.Where(c => c.Item2 != c.Item3).Select(c => c.Item1 + ": got " + c.Item2 + " want " + c.Item3)));

        // random against my oracle, over the span slider range
        var rng = new Random(424242); int n = 20000, mism = 0; string firstM = null;
        for (int i = 0; i < n; i++)
        {
            double range = SpanSliderMin + rng.Next(0, 33);
            var x = A(rng.Next(0, 5), rng.Next(0, 50), rng.Next(0, 50), rng.Next(0, 2), rng.Next(1, 4), rng.Next(0, 8) == 0, rng.Next(0, 6) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power, rng.Next(0, 10) != 0);
            var y = A(rng.Next(0, 5), rng.Next(0, 50), rng.Next(0, 50), rng.Next(0, 2), rng.Next(1, 4), rng.Next(0, 8) == 0, rng.Next(0, 6) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power, rng.Next(0, 10) != 0);
            for (int k = rng.Next(0, 4); k > 0; k--) x.Linked.Add(rng.Next(0, 5));
            for (int k = rng.Next(0, 4); k > 0; k--) y.Linked.Add(rng.Next(0, 5));
            bool got = AerialMath.CanLink(x, y, range) == LinkVerdict.Ok, want = Oracle(x, y, range) == LinkVerdict.Ok;
            if (x.Id == y.Id) { want = false; got = AerialMath.CanLink(x, y, range) == LinkVerdict.Ok; }
            if (got != want) { mism++; firstM = firstM ?? $"case {i}: ids {x.Id},{y.Id} got Ok={got} want {want}"; }
        }
        Row("L1_CANLINK_RANDOM_VS_ORACLE", new[] { "spans_above_everything", "overhead_spans" }, "random", mism == 0 ? "PASS" : "FAIL", n,
            mism == 0 ? "seed 424242, range over the slider 8..40: CanLink == Ok exactly when my own reading of the rules allows the link" : mism + " mismatches; first " + firstM);

        // auto-link picks the nearest allowed anchor, ties to the lower id, -1 when none
        var rg = new Random(77); int m = 5000, badPick = 0; string fp = null;
        for (int i = 0; i < m; i++)
        {
            var self = A(100, rg.Next(0, 40), rg.Next(0, 40));
            var others = new List<AnchorInfo>();
            for (int k = rg.Next(0, 8); k > 0; k--) others.Add(A(rg.Next(0, 20), rg.Next(0, 40), rg.Next(0, 40), rg.Next(0, 4) == 0 ? 1 : 0, 4, rg.Next(0, 6) == 0));
            int got = AerialMath.AutoLinkPick(self, others, SpanDefault);
            var ok = others.Where(o => AerialMath.CanLink(self, o, SpanDefault) == LinkVerdict.Ok)
                           .OrderBy(o => (o.X - self.X) * (o.X - self.X) + (o.Z - self.Z) * (o.Z - self.Z)).ThenBy(o => o.Id).ToList();
            int want = ok.Count == 0 ? -1 : ok[0].Id;
            if (got != want) { badPick++; fp = fp ?? $"case {i}: got {got} want {want}"; }
        }
        Row("L1_AUTOLINK_NEAREST_ALLOWED", new[] { "overhead_spans" }, "random", badPick == 0 ? "PASS" : "FAIL", m,
            badPick == 0 ? "seed 77: AutoLinkPick returns the nearest allowed anchor (ties to the lower id), -1 when none is allowed" : badPick + " bad; first " + fp);
    }

    // ---------------------------------------------------------------- downed spans, gravship: nothing created or lost
    static void Removal()
    {
        var rng = new Random(9001); int n = 5000, bad = 0; string first = null;
        for (int i = 0; i < n; i++)
        {
            int id = 0; bool killed = rng.Next(0, 2) == 0; bool flying = !killed && rng.Next(0, 2) == 0;
            var spans = new List<(int, SpanState)>();
            var partners = new HashSet<int>();
            for (int k = rng.Next(0, 6); k > 0; k--) { int p = rng.Next(1, 8); if (partners.Add(p)) spans.Add((p, rng.Next(0, 3) == 0 ? SpanState.Cut : SpanState.Up)); }
            var aboard = flying ? new HashSet<int>(partners.Where(_ => rng.Next(0, 2) == 0)) : null;
            var plan = AerialMath.PlanRemoval(id, killed, spans, aboard);
            var why = new List<string>();
            int ups = spans.Count(s => s.Item2 == SpanState.Up);
            if (killed && plan.Fallen.Count != ups) why.Add($"killed: {plan.Fallen.Count} fallen for {ups} up spans");
            if (!killed && plan.Fallen.Count != 0) why.Add("not killed but " + plan.Fallen.Count + " fallen");
            if (plan.Fallen.Any(f => !partners.Contains(f.Survivor))) why.Add("fallen at a non-partner");
            if (flying)
            {
                var kept = new HashSet<int>(plan.Kept); var gr = new HashSet<int>(plan.Grounded);
                if (kept.Overlaps(gr)) why.Add("kept and grounded overlap");
                if (!new HashSet<int>(kept.Union(gr)).SetEquals(partners)) why.Add("kept+grounded != partners");
                if (!kept.SetEquals(aboard)) why.Add("kept != aboard");
                if (plan.Reseed.Any(kept.Contains)) why.Add("a kept partner is reseeded (its span stays)");
            }
            else if (!new HashSet<int>(plan.Reseed).SetEquals(partners)) why.Add("reseed != partners");
            if (why.Count > 0) { bad++; first = first ?? $"case {i}: killed {killed} flying {flying} spans [{string.Join(",", spans.Select(s => s.Item1 + ":" + s.Item2))}]: {string.Join("; ", why)}"; }
        }
        Row("L1_REMOVAL_CONSERVES_SPANS", new[] { "downed_spans", "fallen_span_on_ground", "gravship_keeps_connections", "gravship_connectivity" }, "random",
            bad == 0 ? "PASS" : "FAIL", n,
            bad == 0 ? "seed 9001: a killed anchor drops exactly one fallen wire per up span (none for cut ones), every partner reseeded; on a gravship lift every partner is kept (aboard) or grounded, never both, none lost"
                     : bad + " bad; first " + first);

        var reads = new List<SpanNetRead>(); var rr = new Random(31); var want = new List<int>();
        for (int i = 0; i < 2000; i++)
        {
            var s = new SpanNetRead { Span = i, NetA = rr.Next(-1, 3), NetB = rr.Next(-1, 3), State = rr.Next(0, 3) == 0 ? SpanState.Cut : SpanState.Up };
            reads.Add(s); if (s.State == SpanState.Up && !(s.NetA >= 0 && s.NetA == s.NetB)) want.Add(i);
        }
        var got = AerialMath.WatchdogRepairs(reads);
        Row("L1_WATCHDOG_REPAIRS_SPLIT_UP_SPANS", new[] { "connectivity_truth", "overhead_spans" }, "random", got.SequenceEqual(want) ? "PASS" : "FAIL", 2000,
            "seed 31: an up span whose ends sit on different or no nets is repaired, a cut span never: " + got.Count + " repaired, " + want.Count + " expected");
    }

    // ---------------------------------------------------------------- tap_steals_and_costs_goodwill
    static void Tap()
    {
        var rng = new Random(2718); int n = 20000, bad = 0; string first = null;
        for (int i = 0; i < n; i++)
        {
            double rate = TapRateMin + 50 * rng.Next(0, 40);
            double raw = rng.NextDouble() * 0.05 - 0.02, stored = rng.Next(0, 3) == 0 ? 0 : rng.NextDouble() * 2;
            int taps = rng.Next(1, 5); double taken = 0; bool sameNet = rng.Next(0, 10) == 0, en = rng.Next(0, 10) != 0;
            for (int t = 0; t < taps; t++)
            {
                bool working = rng.Next(0, 8) != 0;
                double s = AerialMath.TapStolenPerTick(rate, raw, stored, WattsToWattDaysPerTick, sameNet, en, taken, working);
                if (s < 0 || s > rate * WattsToWattDaysPerTick + 1e-15 || ((!en || sameNet || !working) && s != 0)) { bad++; first = first ?? $"case {i} tap {t}: s {s}"; }
                taken += s;
            }
            // the victim never gives more than it had: raw gain this tick plus stored energy, all taps together
            if (taken > Math.Max(0, raw) + stored + 1e-12) { bad++; first = first ?? $"case {i}: {taps} taps took {taken} of raw {raw} + stored {stored}"; }
        }
        double nanRate = AerialMath.TapStolenPerTick(double.NaN, 1, 1, 1, false, true), infRate = AerialMath.TapStolenPerTick(double.PositiveInfinity, 1, 1, 1, false, true);
        if (nanRate != 0 || infRate != 0) { bad++; first = first ?? "NaN/inf rate steals"; }
        Row("L1_TAP_TAKES_NO_MORE_THAN_VICTIM_HAS", new[] { "tap_steals_and_costs_goodwill", "power_theft" }, "random", bad == 0 ? "PASS" : "FAIL", n,
            bad == 0 ? "seed 2718, tapRate over the slider 50..2000 by 50, 1-4 taps on one victim: each takes 0..rate x k, nothing when off, same net or broken, and together never more than the victim's raw gain + stored"
                     : bad + " bad; first " + first);
    }
    static void Theft()
    {
        // goodwill drains steadily: perDay per whole day of draining, the remainder carried; idle clamps accrue nothing
        var rng = new Random(1618); int n = 3000, bad = 0; string first = null;
        for (int i = 0; i < n; i++)
        {
            int perDay = rng.Next(GoodwillMin, GoodwillMax + 1), drain = 0, total = 0, drainingTicks = 0;
            for (int s = rng.Next(1, 60); s > 0; s--)
            {
                int ticks = rng.Next(1, 3) == 1 ? rng.Next(1, 250) : rng.Next(1, 90000); bool d = rng.Next(0, 4) != 0;
                total += AerialMath.TheftGoodwillAccrue(ref drain, ticks, d, perDay, TicksPerDay);
                if (d) drainingTicks += ticks;
            }
            int want = -(drainingTicks / TicksPerDay) * perDay;
            if (total != want || drain != drainingTicks % TicksPerDay) { bad++; first = first ?? $"case {i}: perDay {perDay} drained {drainingTicks} ticks: goodwill {total} want {want}, carry {drain} want {drainingTicks % TicksPerDay}"; }
        }
        Row("L1_GOODWILL_STEADY_CONSERVED", new[] { "tap_steals_and_costs_goodwill", "power_theft" }, "random", bad == 0 ? "PASS" : "FAIL", n,
            bad == 0 ? "seed 1618, perDay over the slider 0..10, mixed 250-tick polls and long jumps: total goodwill = -(whole draining days) x perDay, remainder carried, idle time free"
                     : bad + " bad; first " + first);

        // sighting: sweep the sight-range slider; no line of sight, asleep/down, or held by us never sees
        int sb = 0, sc = 0;
        for (float rg = SightMin; rg <= SightMax; rg += 1)
            for (double d = 0; d <= 40; d += 0.25)
                foreach (bool los in new[] { false, true }) foreach (bool up in new[] { false, true }) foreach (bool held in new[] { false, true })
                {
                    sc++;
                    bool want = los && up && !held && d <= rg;
                    if (AerialMath.TheftSpotted(d, rg, los, up, held) != want) sb++;
                }
        Row("L1_THEFT_SPOTTED_SWEEP", new[] { "tap_steals_and_costs_goodwill", "power_theft" }, "sweep", sb == 0 ? "PASS" : "FAIL", sc,
            "sight range 3..30 x distance 0..40: spotted exactly within range, with line of sight, awake and not held by us: " + sb + " wrong");
    }

    // ---------------------------------------------------------------- restring_cut_span: a colonist's job, never instant
    static void Restring()
    {
        var speeds = new List<double> { double.NaN, double.NegativeInfinity, -1, 0, 0.01, 0.05, 0.1, 0.2, 0.5, 1, 1.5, 2, 3, 5, 10, double.PositiveInfinity };
        var bad = new List<string>(); int prev = int.MaxValue;
        foreach (double s in speeds)
        {
            int t = AerialMath.RestringTicks(s);
            if (t < 1) bad.Add($"speed {s}: {t} ticks (a job of no time)");
            if (!double.IsNaN(s) && t > prev) bad.Add($"speed {s}: {t} > {prev} (slower worker faster)");
            if (!double.IsNaN(s)) prev = t;
        }
        if (AerialMath.RestringTicks(1) != AerialMath.RestringBaseTicks) bad.Add("speed 1 not the base 300");
        Row("L1_RESTRING_TICKS_SWEEP", new[] { "restring_cut_span", "restring_job" }, "sweep", bad.Count == 0 ? "PASS" : "FAIL", speeds.Count,
            bad.Count == 0 ? "construction speed NaN, -inf..+inf: the re-string job is at least one tick, monotone, 300 at speed 1"
                           : string.Join("; ", bad) + " (shrunk: RestringTicks(NaN); Math.Max(0.1, NaN) is NaN)");
    }
    static void Shock()
    {
        int bad = 0, c = 0;
        foreach (bool flesh in new[] { false, true }) foreach (bool dead in new[] { false, true }) foreach (bool outd in new[] { false, true }) foreach (bool rs in new[] { false, true })
        { c++; if (AerialMath.ShockTakes(flesh, dead, outd, rs) != (flesh && !dead && !outd && !rs)) bad++; }
        Row("L1_SHOCK_TAKES_TABLE", new[] { "fallen_wire_shocks_crossers", "fallen_wire_shock" }, "fixed", bad == 0 ? "PASS" : "FAIL", c,
            "a live wire shocks living, standing flesh, and spares only the worker re-stringing that wire (the per-wire key is the caller's): " + bad + " wrong of 16");
    }

    // ---------------------------------------------------------------- explosions cut spans (downed_spans), kinetic blasts sway them
    static void Blast()
    {
        var bad = new List<string>(); int c = 0;
        foreach (bool harm in new[] { false, true }) foreach (bool kin in new[] { false, true }) foreach (bool cut in new[] { false, true }) foreach (bool ks in new[] { false, true }) foreach (double dmg in new[] { 0.0, 10.0 })
        {
            c++;
            var k = AerialMath.BlastKindFor(harm, kin, dmg, cut, ks);
            var want = !harm ? AerialMath.BlastKind.None : kin ? (ks ? AerialMath.BlastKind.Sway : AerialMath.BlastKind.None) : (cut && dmg > 0 ? AerialMath.BlastKind.Cut : AerialMath.BlastKind.None);
            if (k != want) bad.Add($"harm {harm} kin {kin} cut {cut} ks {ks} dmg {dmg}: {k}");
        }
        double f0 = AerialMath.BlastCutFalloff(0, 5), f1 = AerialMath.BlastCutFalloff(5, 5), fo = AerialMath.BlastCutFalloff(9, 5);
        if (Math.Abs(f0 - 1) > 1e-9 || Math.Abs(f1 - 0.2) > 1e-9 || Math.Abs(fo - 0.2) > 1e-9) bad.Add($"falloff 0/edge/outside {f0}/{f1}/{fo}");
        var rng = new Random(606); int n = 20000;
        for (int i = 0; i < n; i++)
        {
            var a = new P2(rng.NextDouble() * 30, rng.NextDouble() * 30); var b = new P2(rng.NextDouble() * 30, rng.NextDouble() * 30); var ctr = new P2(rng.NextDouble() * 30, rng.NextDouble() * 30);
            double rad = rng.NextDouble() * 6, hp = 1 + rng.NextDouble() * 100, dmg = rng.NextDouble() * 120;
            var r = AerialMath.BlastSpan(a, b, ctr, rad, hp, dmg, AerialMath.BlastKind.Cut);
            bool hit = AerialMath.SpanHit(a, b, ctr, rad);
            if (r.Hp > hp + 1e-9) bad.Add($"case {i}: hp rose");
            if (!hit && (r.Cut || r.Hp != hp)) bad.Add($"case {i}: missed span damaged");
            if (r.Cut != (r.Hp <= 0)) bad.Add($"case {i}: cut flag {r.Cut} at hp {r.Hp}");
            if (hit && dmg >= hp / 0.2 && !r.Cut) bad.Add($"case {i}: lethal anywhere in radius but not cut");
            if (bad.Count > 5) break;
        }
        Row("L1_BLAST_CUT_RULES", new[] { "downed_spans", "fallen_span_on_ground" }, "random", bad.Count == 0 ? "PASS" : "FAIL", c + n,
            bad.Count == 0 ? "the explosionsCut/kineticSway switches x blast kinds answer as the settings say; seed 606: a blast's falloff 1 at centre to 0.2 at the radius, hp never rises, a span outside the radius untouched, cut exactly when hp <= 0"
                           : string.Join("; ", bad.Take(5)));
    }

    // ---------------------------------------------------------------- fallen_span_on_ground: on the ground, not across walls, nothing created
    static double PathLen(List<P2> p) { double s = 0; for (int i = 1; i < p.Count; i++) s += P2.Dist(p[i - 1], p[i]); return s; }
    static void Fallen()
    {
        var rng = new Random(4405); int n = 2500, inWall = 0, notGround = 0, tooLong = 0; string fw = null, fg = null, fl = null; double worstIn = 0, worstRatio = 0;
        for (int i = 0; i < n; i++)
        {
            int seed = rng.Next();
            var walls = new HashSet<(int, int)>();
            int nw = rng.Next(0, 4);
            for (int k = 0; k < nw; k++) { int wx = rng.Next(2, 30), wz = rng.Next(2, 30), wl = rng.Next(1, 8); bool hz = rng.Next(0, 2) == 0; for (int j = 0; j < wl; j++) walls.Add(hz ? (wx + j, wz) : (wx, wz + j)); }
            var basePt = new P2(rng.Next(3, 28) + 0.5, rng.Next(3, 28) + 0.5);
            if (walls.Contains(((int)Math.Floor(basePt.X), (int)Math.Floor(basePt.Z)))) continue;
            double ang = rng.NextDouble() * 2 * Math.PI, dist = 2 + rng.NextDouble() * 18;
            var toward = new P2(basePt.X + dist * Math.Cos(ang), basePt.Z + dist * Math.Sin(ang));
            double length = dist * 1.05;
            Func<int, int, bool> walk = (x, z) => !walls.Contains((x, z));
            var top = new P2(basePt.X, basePt.Z + 1.4);
            var l = AerialMath.LayFallen(top, basePt, toward, length, seed, walk);
            if (walls.Count == 0 && !l.TipGrounded) { notGround++; fg = fg ?? $"seed {seed}: open floor, wire never reaches the ground"; }
            var gp = AerialMath.GroundPts(l).ToList();
            foreach (P2 p in gp)
            {
                if (P2.Dist(p, basePt) < 0.75) continue;
                int cx = (int)Math.Floor(p.X), cz = (int)Math.Floor(p.Z);
                if (walls.Contains((cx, cz)))
                {
                    double depth = Math.Min(Math.Min(p.X - cx, cx + 1 - p.X), Math.Min(p.Z - cz, cz + 1 - p.Z));
                    if (depth > worstIn) worstIn = depth;
                    inWall++; fw = fw ?? $"seed {seed}: base {basePt} toward {toward}, {walls.Count} wall cells, ground point {p} {F(depth)} cell inside wall ({cx},{cz}), Blocked {l.Blocked}";
                    break;
                }
            }
            double drawn = PathLen(gp);
            double ratio = drawn / Math.Max(1e-9, length);
            if (!l.Blocked && ratio > worstRatio) worstRatio = ratio;
            if (drawn > 2 * length + 2) { tooLong++; fl = fl ?? $"seed {seed}: {F(drawn)} cells drawn on the ground for a {F(length)}-cell cable, blocked {l.Blocked}, {walls.Count} wall cells"; }
        }
        Row("L1_FALLEN_ON_GROUND_NOT_IN_WALLS", new[] { "fallen_span_on_ground", "downed_spans", "cords_meet_walls_at_face" }, "random", inWall == 0 && notGround == 0 ? "PASS" : "FAIL", n,
            (inWall == 0 && notGround == 0) ? "seed 4405: every grounded point of a fallen wire past its first 0.75 cell lies on a walkable cell; on open floor the wire always reaches the ground"
                : $"seed 4405: {inWall} of {n} wires put a grounded point inside an unwalkable cell (deepest {F(worstIn)} cell); {notGround} open-floor wires never grounded. first: {fw ?? fg}");
        Row("L1_FALLEN_LENGTH_NOTHING_CREATED", new[] { "fallen_span_on_ground", "downed_spans" }, "random", tooLong == 0 ? "PASS" : "FAIL", n,
            tooLong == 0 ? $"seed 4405: a fallen wire's grounded length never exceeds 2 x its cable + 2 cells (worst unblocked ratio {F(worstRatio)})"
                         : $"seed 4405: {tooLong} of {n} draw more than 2 x cable + 2 cells on the ground (worst unblocked ratio {F(worstRatio)}); first {fl}");

        // three wires fall as three: each its own lay, tips apart
        var rr = new Random(8081); int m = 1000, pinch = 0, wrongCount = 0; double minTip = 1e9; string fp = null;
        for (int i = 0; i < m; i++)
        {
            int cnt = rr.Next(1, 4); var basePt = new P2(20.5, 20.5);
            double ang = rr.NextDouble() * 2 * Math.PI, dist = 4 + rr.NextDouble() * 14;
            var toward = new P2(basePt.X + dist * Math.Cos(ang), basePt.Z + dist * Math.Sin(ang));
            var tips = new List<P2> { new P2(basePt.X - 0.4, basePt.Z + 1.4), new P2(basePt.X, basePt.Z + 1.5), new P2(basePt.X + 0.4, basePt.Z + 1.4) };
            var lays = AerialMath.LayFallenStrands(tips, basePt, toward, dist * 1.05, rr.Next(), cnt, (x, z) => true);
            if (lays.Count != cnt) { wrongCount++; continue; }
            for (int p = 0; p < lays.Count; p++) for (int q = p + 1; q < lays.Count; q++)
            {
                double d = P2.Dist(lays[p].Tip, lays[q].Tip); minTip = Math.Min(minTip, d);
                if (d < 0.25) { pinch++; fp = fp ?? $"case {i}: {cnt} wires over {F(dist)} cells, tips {p},{q} {F(d)} cell apart"; }
            }
        }
        Row("L1_FALLEN_STRANDS_EACH_ITS_OWN", new[] { "fallen_span_on_ground", "downed_spans" }, "random", pinch == 0 && wrongCount == 0 ? "PASS" : "FAIL", m,
            $"seed 8081: a span of N wires drops N lays ({wrongCount} wrong counts); pairs of tips under 0.25 cell apart: {pinch} (closest {F(minTip)}){(fp != null ? "; first " + fp : "")}");
    }

    // ---------------------------------------------------------------- wires per span (maxStrands slider) and the pipe/power switches
    static void Strands()
    {
        var bad = new List<string>(); int c = 0;
        for (int ms = StrandsMin; ms <= StrandsMax; ms++)
            for (int ia = 0; ia <= 4; ia++) for (int ib = 0; ib <= 4; ib++)
            {
                c++;
                int n = AerialMath.StrandCount(ia, ib, ms);
                if (n < 1 || n > ms || n > Math.Max(1, Math.Min(ia, ib))) bad.Add($"ms {ms} ins {ia}/{ib}: {n}");
                var insA = Enumerable.Range(0, ia).Select(k => new P2(k * 0.3 - 0.45, 1.5)).ToList();
                var insB = Enumerable.Range(0, ib).Select(k => new P2(k * 0.3 - 0.45, 1.5)).ToList();
                var ss = AerialMath.SpanStrands(new P2(0, 0), insA, new P2(15, 3), insB, 11, ms);
                if (ss.Count != n) bad.Add($"strands {ss.Count} != count {n}");
                foreach (var s in ss)
                {
                    bool aOk = ia == 0 ? P2.Dist(s.A, new P2(0, 0)) < 1e-9 : insA.Any(p => P2.Dist(s.A, new P2(p.X, p.Z)) < 1e-9);
                    bool bOk = ib == 0 ? P2.Dist(s.B, new P2(15, 3)) < 1e-9 : insB.Any(p => P2.Dist(s.B, new P2(15 + p.X, 3 + p.Z)) < 1e-9);
                    if (!aOk || !bOk) bad.Add($"ms {ms} ins {ia}/{ib}: a strand ends off an insulator");
                    if (s.SagMul <= 0) bad.Add("strand sag multiplier <= 0");
                }
            }
        Row("L1_STRANDS_PER_SPAN_SWEEP", new[] { "overhead_spans", "fallen_span_on_ground" }, "sweep", bad.Count == 0 ? "PASS" : "FAIL", c,
            bad.Count == 0 ? "wires-per-span slider 1..3 x insulators 0..4 per end: 1..min(ends, setting) wires, each ending exactly on an insulator tip" : string.Join("; ", bad.Take(5)));
    }
    static void Kinds()
    {
        var bad = new List<string>(); int c = 0;
        foreach (bool pw in new[] { false, true }) foreach (bool pp in new[] { false, true }) foreach (bool set in new[] { false, true })
        {
            c++;
            if (AerialKinds.KindOn(AerialLineKind.Power, pw, pp) != pw) bad.Add("power pole follows the pipe switch");
            if (AerialKinds.KindOn(AerialLineKind.Pipe, pw, pp) != pp) bad.Add("pipe pole follows the power master");
            if (AerialKinds.KindBehaviour(AerialLineKind.Power, pw, pp, set) != (pw && set)) bad.Add("power behaviour not master AND setting");
            if (AerialKinds.KindBehaviour(AerialLineKind.Pipe, pw, pp, set) != pp) bad.Add("pipe behaviour reads a power setting");
        }
        if (AerialKinds.CarriesPower(AerialLineKind.Pipe) || AerialKinds.Sways(AerialLineKind.Pipe) || AerialKinds.Drips(AerialLineKind.Pipe, true) || AerialKinds.StrandCap(AerialLineKind.Pipe, 3) != 1)
            bad.Add("a pipe span carries power, sways, drips or has more than one strand");
        Row("L1_PIPE_POLE_SWITCH_ITS_OWN", new[] { "pipe_pole_switch", "settings_switch_cleanly" }, "fixed", bad.Count == 0 ? "PASS" : "FAIL", c,
            bad.Count == 0 ? "every power/pipe/feature switch combination: power poles obey only the power master (AND their feature setting), pipe poles only their own switch; a pipe span carries no power, never sways or drips, one strand"
                           : string.Join("; ", bad.Distinct()));
        // the span slider range vs the kernel's clamp
        float lo = AerialKinds.RangeFor(AerialLineKind.Power, SpanSliderMin, 0), hi = AerialKinds.RangeFor(AerialLineKind.Power, SpanSliderMax, 0);
        Row("L1_SPAN_RANGE_SLIDER_INSIDE_CLAMP", new[] { "mod_settings", "overhead_spans" }, "sweep", lo == SpanSliderMin && hi == SpanSliderMax ? "PASS" : "FAIL", 2,
            $"maxSpan slider {SpanSliderMin}..{SpanSliderMax} reaches the kernel as {lo}..{hi} (kernel clamp {AerialKinds.PowerSpanMin}..{AerialKinds.PowerSpanMax}); NaN -> {AerialKinds.RangeFor(AerialLineKind.Power, float.NaN, 0)}");
    }
    static void Sway()
    {
        var rng = new Random(1234); int n = 50000, bad = 0; string first = null;
        for (int i = 0; i < n; i++)
        {
            double t = rng.NextDouble() * 1.2 - 0.1, time = rng.NextDouble() * 1000, wind = rng.NextDouble() * 3 - 0.5, amp = (SwayMin + rng.NextDouble() * (SwayMax - SwayMin)) * 0.3;
            double s = AerialMath.Sway(t, time, wind, amp, rng.Next());
            double cap = amp * Math.Min(Math.Max(wind, 0), 1.5) / 1.5 * 1.3 + 1e-12;
            if (double.IsNaN(s) || Math.Abs(s) > cap || ((t <= 0 || t >= 1 || wind <= 0 || amp <= 0) && s != 0)) { bad++; first = first ?? $"t {F(t)} wind {F(wind)} amp {F(amp)}: {s}"; }
        }
        Row("L1_SWAY_BOUNDED_STILL_AT_ENDS", new[] { "spans_above_everything", "overhead_spans" }, "random", bad == 0 ? "PASS" : "FAIL", n,
            bad == 0 ? "seed 1234, sway strength 0..2: the wind offset is 0 at both insulators and with no wind, never past 1.3 x amp x min(wind,1.5)/1.5" : bad + " bad; first " + first);
    }
}
