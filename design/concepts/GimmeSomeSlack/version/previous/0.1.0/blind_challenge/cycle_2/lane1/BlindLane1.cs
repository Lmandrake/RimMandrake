// Blind lane 1, Gimme Some Slack 0.1.0, cycle 2: game-logic tests of the Verse-free kernel AerialMath.cs, written from
// the bars (tree.json, sheet.md, plan.md) and the shipped settings (AerialSettings.cs defaults and slider ranges) alone.
// The builder's SelfTest was not read. One JSON row per line on stdout; exit 1 when a row FAILs.
// Settings as shipped, copied by hand from AerialSettings.cs (2026-11-15): maxSpan 20 (slider 8..40, Range clamps 4..40),
// sag 0.06 (slider 0..0.15), maxStrands 3 (1..3), tapRate 500 (50..2000 step 50), theftGoodwillPerDay 2 (0..10),
// theftSightRange 12 (3..30), explosionsCut on, kineticSway on.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.GimmeSomeSlack.Aerial;

static class BlindLane1
{
    static readonly List<string> Rows = new List<string>();
    static bool anyFail;

    static string J(string s) => "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";
    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") anyFail = true;
        Rows.Add("{\"id\": " + J(id) + ", \"bars\": [" + string.Join(", ", bars.Select(J)) + "], \"kind\": " + J(kind) +
                 ", \"verdict\": " + J(verdict) + ", \"cases\": " + cases + ", \"detail\": " + J(detail) + "}");
    }
    static string F(double d) => d.ToString("0.####", CultureInfo.InvariantCulture);

    /// <summary>Runs a property over n seeded cases; returns (fails, first failing case's description).</summary>
    static (int fails, string first) Prop(int n, int seed, Func<Random, string> one)
    {
        var rng = new Random(seed);
        int fails = 0; string first = null;
        for (int i = 0; i < n; i++)
        {
            string bad = one(rng);
            if (bad != null) { fails++; if (first == null) first = "case " + i + ": " + bad; }
        }
        return (fails, first);
    }

    static AnchorInfo A(int id, int x, int z, int fac = 0, int max = 4, bool roof = false, bool anchor = true, AerialLineKind k = AerialLineKind.Power)
        => new AnchorInfo { Id = id, X = x, Z = z, Faction = fac, MaxLinks = max, Roofed = roof, IsAnchor = anchor, Kind = k };

    static void Main()
    {
        string[] SPANS = { "spans_above_everything", "overhead_spans" };
        string[] FALLEN = { "fallen_span_on_ground", "downed_spans" };
        string[] SHOCK = { "fallen_wire_shocks_crossers", "fallen_wire_shock" };
        string[] RESTRING = { "restring_cut_span", "restring_job" };
        string[] TAP = { "tap_steals_and_costs_goodwill", "power_theft" };
        string[] GRAV = { "gravship_keeps_connections", "gravship_connectivity" };

        // ---------------------------------------------------------------- spans: the three bad links refused (fixed)
        {
            double range = 20;
            var a = A(1, 0, 0);
            var cases = new (string what, AnchorInfo b, LinkVerdict want)[]
            {
                ("in range, same faction", A(2, 12, 16), LinkVerdict.Ok),            // dist 20 exactly: in range
                ("out of range by one cell", A(3, 21, 0), LinkVerdict.OutOfRange),
                ("hostile anchor", A(4, 5, 0, fac: 7), LinkVerdict.Foreign),
                ("not an anchor (a battery)", A(5, 5, 0, anchor: false), LinkVerdict.NotAnchor),
                ("itself", A(1, 0, 0), LinkVerdict.Self),
                ("roofed target", A(6, 3, 0, roof: true), LinkVerdict.Roofed),
                ("a pipe pole", A(7, 3, 0, k: AerialLineKind.Pipe), LinkVerdict.WrongKind),
            };
            var bad = new List<string>();
            foreach (var c in cases)
            {
                var v = AerialMath.CanLink(a, c.b, range);
                if (v != c.want) bad.Add(c.what + ": got " + v + " want " + c.want);
                var vr = AerialMath.CanLink(c.b, a, range);   // symmetric refusals
                if (c.what != "itself" && c.what != "roofed target" && (vr == LinkVerdict.Ok) != (c.want == LinkVerdict.Ok)) bad.Add(c.what + " reversed: " + vr);
            }
            Row("L1_SPAN_BAD_LINKS_REFUSED", SPANS, "fixed", bad.Count == 0 ? "PASS" : "FAIL", cases.Length * 2,
                bad.Count == 0 ? "out-of-range, hostile and non-anchor links refused with their reasons; a 20-cell link at range 20 accepted" : string.Join("; ", bad));
        }
        // ---------------------------------------------------------------- spans: random links obey every rule (random)
        {
            int seed = 4101;
            var r = Prop(3000, seed, rng =>
            {
                double range = 8 + rng.Next(33);
                var a = A(1, rng.Next(-30, 30), rng.Next(-30, 30), rng.Next(2), rng.Next(1, 4), rng.Next(10) == 0, rng.Next(12) != 0);
                var b = A(2, rng.Next(-30, 30), rng.Next(-30, 30), rng.Next(2), rng.Next(1, 4), rng.Next(10) == 0, rng.Next(12) != 0,
                          rng.Next(10) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power);
                for (int i = 0, n = rng.Next(4); i < n; i++) a.Linked.Add(100 + i);
                var v = AerialMath.CanLink(a, b, range);
                double d = Math.Sqrt((a.X - b.X) * (a.X - b.X) + (a.Z - b.Z) * (a.Z - b.Z));
                bool legal = a.IsAnchor && b.IsAnchor && a.Faction == b.Faction && a.Kind == b.Kind && !a.Roofed && !b.Roofed
                             && d <= range + 1e-9 && a.Linked.Count < a.MaxLinks && b.Linked.Count < b.MaxLinks;
                return (v == LinkVerdict.Ok) == legal ? null : "range " + range + " a(" + a.X + "," + a.Z + " f" + a.Faction + " links " + a.Linked.Count + "/" + a.MaxLinks +
                    ") b(" + b.X + "," + b.Z + " f" + b.Faction + " " + b.Kind + ") dist " + F(d) + " verdict " + v + " legal " + legal;
            });
            Row("L1_SPAN_LINK_RULES_RANDOM", SPANS, "random", r.fails == 0 ? "PASS" : "FAIL", 3000,
                "seed " + seed + ": Ok exactly when both are our anchors, same faction and kind, unroofed, within range, with room; " + r.fails + " disagreements" + (r.first != null ? "; first " + r.first : ""));
        }
        // ---------------------------------------------------------------- spans: auto-link picks the nearest legal anchor (random)
        {
            int seed = 4102;
            var r = Prop(1500, seed, rng =>
            {
                double range = 8 + rng.Next(33);
                var self = A(0, 0, 0);
                var others = new List<AnchorInfo>();
                for (int i = 1, n = rng.Next(1, 9); i <= n; i++) others.Add(A(i, rng.Next(-40, 40), rng.Next(-40, 40), rng.Next(4) == 0 ? 1 : 0, 3, rng.Next(8) == 0, rng.Next(8) != 0));
                int pick = AerialMath.AutoLinkPick(self, others, range);
                var legal = others.Where(o => AerialMath.CanLink(self, o, range) == LinkVerdict.Ok).ToList();
                if (legal.Count == 0) return pick == -1 ? null : "picked " + pick + " with no legal target";
                long best = legal.Min(o => (long)o.X * o.X + (long)o.Z * o.Z);
                int want = legal.Where(o => (long)o.X * o.X + (long)o.Z * o.Z == best).Min(o => o.Id);
                return pick == want ? null : "picked " + pick + " want " + want;
            });
            Row("L1_SPAN_AUTOLINK_NEAREST_RANDOM", SPANS, "random", r.fails == 0 ? "PASS" : "FAIL", 1500,
                "seed " + seed + ": nearest legal anchor, ties to the lower id, -1 when none; " + r.fails + " wrong" + (r.first != null ? "; first " + r.first : ""));
        }
        // ---------------------------------------------------------------- spans: "auto-link selected" forest (random)
        {
            int seed = 4103;
            var r = Prop(800, seed, rng =>
            {
                double range = 8 + rng.Next(20);
                var sel = new List<AnchorInfo>();
                int n = rng.Next(2, 12);
                for (int i = 0; i < n; i++) sel.Add(A(i, rng.Next(0, 40), rng.Next(0, 40), rng.Next(6) == 0 ? 1 : 0, rng.Next(1, 4)));
                var links = AerialMath.MinimumSpanningLinks(sel, range);
                var parent = Enumerable.Range(0, n).ToArray();
                int Find(int x) { while (parent[x] != x) x = parent[x] = parent[parent[x]]; return x; }
                var deg = new int[n];
                foreach (var (p, q) in links)
                {
                    var a = sel[p]; var b = sel[q];
                    if (AerialMath.CanLink(a, b, range) != LinkVerdict.Ok && !(a.Linked.Count < a.MaxLinks)) return "illegal link " + p + "-" + q;
                    if (a.Faction != b.Faction) return "foreign link " + p + "-" + q;
                    if (!AerialMath.InRange(a.X, a.Z, b.X, b.Z, range)) return "out-of-range link " + p + "-" + q;
                    if (Find(p) == Find(q)) return "cycle at " + p + "-" + q;
                    parent[Find(p)] = Find(q);
                    if (++deg[p] > a.MaxLinks || ++deg[q] > b.MaxLinks) return "over maxLinks at " + p + "-" + q;
                }
                return null;
            });
            Row("L1_SPAN_MST_FOREST_RANDOM", SPANS, "random", r.fails == 0 ? "PASS" : "FAIL", 800,
                "seed " + seed + ": every proposed link same-faction, in range, acyclic, within maxLinks; " + r.fails + " bad" + (r.first != null ? "; first " + r.first : ""));
        }
        // ---------------------------------------------------------------- spans: sag, never ruler-straight at the shipped default (sweep)
        {
            var bad = new List<string>(); int n = 0; string zero = "";
            for (double sag = 0; sag <= 0.150001; sag += 0.01)
                for (double len = 4; len <= 40; len += 4)
                {
                    n++;
                    var pts = AerialMath.SpanCurve(new P2(0, 0), new P2(len, 0), sag);
                    double deepest = pts.Max(p => -p.Z);
                    double want = AerialKinds.SagDepth(len, sag);
                    if (Math.Abs(pts[0].X) > 1e-9 || Math.Abs(pts[pts.Count - 1].X - len) > 1e-9 || Math.Abs(pts[0].Z) > 1e-9 || Math.Abs(pts[pts.Count - 1].Z) > 1e-9) bad.Add("ends moved at sag " + F(sag) + " len " + len);
                    if (Math.Abs(deepest - want) > 0.02 * want + 1e-6) bad.Add("sag " + F(sag) + " len " + len + ": deepest " + F(deepest) + " vs SagDepth " + F(want));
                    if (sag > 0 && !(deepest > 0)) bad.Add("ruler-straight at sag " + F(sag));
                    if (sag == 0 && deepest <= 1e-12) zero = "sag 0 (the slider's floor) draws a ruler-straight wire: a player's choice, not the shipped default";
                }
            double defDepth = AerialKinds.SagDepth(20, 0.06);
            if (!(defDepth > 0.5)) bad.Add("default 20-cell span sags only " + F(defDepth));
            Row("L1_SPAN_SAG_SWEEP", SPANS, "sweep", bad.Count == 0 ? "PASS" : "FAIL", n,
                (bad.Count == 0 ? "ends pinned, deepest point = SagDepth within 2%, positive for every sag > 0 over 0..0.15 x 4..40 cells; shipped default sags " + F(defDepth) + " cells on a 20-cell span. " + zero : string.Join("; ", bad.Take(6))));
        }
        // ---------------------------------------------------------------- spans: range slider vs clamp (sweep)
        {
            var bad = new List<string>(); int n = 0;
            for (float s = 0; s <= 60; s += 1)
            {
                n++;
                float r = AerialKinds.RangeFor(AerialLineKind.Power, s, 12);
                float want = Math.Max(4, Math.Min(40, s));
                if (Math.Abs(r - want) > 1e-6) bad.Add("maxSpan " + s + " -> " + r);
                if (s >= 8 && s <= 40 && r != s) bad.Add("slider value " + s + " not honoured: " + r);
            }
            float nan = AerialKinds.RangeFor(AerialLineKind.Power, float.NaN, 12);
            if (!(nan >= 4 && nan <= 40)) bad.Add("NaN maxSpan -> " + nan);
            Row("L1_SPAN_RANGE_SWEEP", SPANS, "sweep", bad.Count == 0 ? "PASS" : "FAIL", n + 1,
                bad.Count == 0 ? "every slider value 8..40 is the link range; outside it clamps to 4..40; NaN clamps" : string.Join("; ", bad.Take(6)));
        }
        // ---------------------------------------------------------------- strands: one per insulator, capped, distinct (sweep)
        {
            var bad = new List<string>(); int n = 0;
            for (int ia = 0; ia <= 5; ia++) for (int ib = 0; ib <= 5; ib++) for (int ms = 1; ms <= 3; ms++)
            {
                n++;
                int c = AerialMath.StrandCount(ia, ib, ms);
                if (c < 1 || c > ms || c > Math.Max(1, Math.Min(ia, ib))) bad.Add("count " + c + " for " + ia + "/" + ib + " cap " + ms);
                var insA = Enumerable.Range(0, ia).Select(i => new P2(i * 0.2, 1.5)).ToList();
                var insB = Enumerable.Range(0, ib).Select(i => new P2(i * 0.2, 1.5)).ToList();
                var st = AerialMath.SpanStrands(new P2(0, 0), insA, new P2(10, 0), insB, 7, ms);
                if (st.Count != c) bad.Add("strands " + st.Count + " != count " + c);
                foreach (var s in st) if (s.InsA < 0 || (ia > 0 && s.InsA >= ia) || s.InsB < 0 || (ib > 0 && s.InsB >= ib)) bad.Add("insulator out of range");
                if (Math.Min(ia, ib) >= c && st.Select(s => s.InsA).Distinct().Count() != c) bad.Add("shared insulator at " + ia + "/" + ib + " cap " + ms);
            }
            Row("L1_SPAN_STRANDS_SWEEP", SPANS, "sweep", bad.Count == 0 ? "PASS" : "FAIL", n,
                bad.Count == 0 ? "1..min(insulators, wires-per-span 1..3) strands, each on its own insulator, never out of range" : string.Join("; ", bad.Distinct().Take(6)));
        }
        // ---------------------------------------------------------------- downed: a killed mast drops its up spans, nothing else (random + conservation)
        {
            int seed = 4201;
            var r = Prop(2000, seed, rng =>
            {
                int id = 50; bool killed = rng.Next(2) == 0;
                var spans = new List<(int, SpanState)>();
                for (int i = 0, n = rng.Next(0, 6); i < n; i++) spans.Add((rng.Next(1, 9), rng.Next(3) == 0 ? SpanState.Cut : SpanState.Up));
                if (rng.Next(8) == 0) spans.Add((id, SpanState.Up));
                HashSet<int> aboard = rng.Next(3) == 0 ? new HashSet<int>(spans.Where(_ => rng.Next(2) == 0).Select(s => s.Item1)) : null;
                var plan = AerialMath.PlanRemoval(id, killed, spans, aboard);
                var partners = new HashSet<int>(spans.Select(s => s.Item1).Where(p => p != id));
                int wantFall = killed ? spans.Count(s => s.Item1 != id && s.Item2 == SpanState.Up) : 0;
                if (plan.Fallen.Count != wantFall) return "fallen " + plan.Fallen.Count + " want " + wantFall + " (killed " + killed + ")";
                if (plan.Fallen.Any(f => !partners.Contains(f.Survivor) || !f.TowardDead)) return "a fallen wire on a non-partner";
                if (plan.Reseed.Contains(id) || plan.Kept.Contains(id)) return "the leaving anchor itself re-seeded or kept";
                // conservation: every partner either flies along (kept) or is re-seeded, never both, never neither
                foreach (int p in partners)
                {
                    bool kept = plan.Kept.Contains(p), re = plan.Reseed.Contains(p);
                    if (kept == re) return "partner " + p + " kept " + kept + " reseeded " + re + " (aboard " + (aboard == null ? "null" : string.Join(",", aboard)) + ", killed " + killed + ")";
                }
                if (aboard != null && !killed && plan.Fallen.Count > 0) return "a gravship lift dropped a wire";
                if (aboard != null && !killed && plan.Grounded.Any(p => aboard.Contains(p))) return "a flying partner grounded";
                return null;
            });
            Row("L1_DOWNED_REMOVAL_PLAN_RANDOM", FALLEN.Concat(GRAV).ToArray(), "random", r.fails == 0 ? "PASS" : "FAIL", 2000,
                "seed " + seed + ": killed -> one fallen wire per UP span, none per CUT; dismantled -> none; a gravship lift keeps the spans to partners aboard, takes down the rest, drops none; every partner kept xor re-seeded; " + r.fails + " bad" + (r.first != null ? "; first " + r.first : ""));
        }
        // ---------------------------------------------------------------- downed: the fallen wire lies on open ground (random)
        {
            int seed = 4202; int blockedSeen = 0, groundedSeen = 0;
            var r = Prop(1500, seed, rng =>
            {
                int W = 40;
                var wall = new bool[W, W];
                int walls = rng.Next(0, 4);
                for (int w = 0; w < walls; w++) { int x = rng.Next(12, 30); for (int z = 0; z < W; z++) if (rng.Next(6) != 0) wall[x, z] = true; }
                Func<int, int, bool> walk = (x, z) => x >= 0 && z >= 0 && x < W && z < W && !wall[x, z];
                var basePt = new P2(10.5, 20.5);
                var toward = new P2(10.5 + rng.Next(-15, 16), 20.5 + rng.Next(-15, 16));
                if (P2.Dist(basePt, toward) < 2) toward = new P2(25.5, 20.5);
                double len = P2.Dist(basePt, toward) * (0.6 + rng.NextDouble() * 0.6);
                var top = new P2(basePt.X, basePt.Z + 1.5 + rng.NextDouble());
                int seedLay = rng.Next();
                var lay = AerialMath.LayFallen(top, basePt, toward, len, seedLay, walk, rng.Next(-1, 2));
                if (lay.Blocked) blockedSeen++;
                if (lay.GroundFrom >= 0) groundedSeen++;
                if (lay.Pts.Count < 2) return "no wire laid (len " + F(len) + ", seed " + seedLay + ")";
                if (lay.GroundFrom < 0) return "nothing of a " + F(len) + "-cell wire reached the ground (seed " + seedLay + ")";
                foreach (var p in AerialMath.GroundPts(lay))
                {
                    if (P2.Dist(p, basePt) <= 0.75) continue;
                    if (!walk((int)Math.Floor(p.X), (int)Math.Floor(p.Z))) return "grounded point " + p + " in a wall (seed " + seedLay + ", toward " + toward + ")";
                }
                double path = 0; for (int i = 1; i < lay.Pts.Count; i++) path += P2.Dist(lay.Pts[i - 1], lay.Pts[i]);
                double cableUsed = len >= 0.8 * P2.Dist(basePt, toward) ? P2.Dist(basePt, toward) : len;   // the kernel's own rule
                double groundLen = 0; P2? prevG = null;
                foreach (var gp in AerialMath.GroundPts(lay)) { if (prevG != null) groundLen += P2.Dist(prevG.Value, gp); prevG = gp; }
                if (groundLen > 2.0 * cableUsed + 2)
                {
                    // shrink: the shortest cable on this geometry that still overdraws (same seed, same walls)
                    double lo = 0.5, best = cableUsed;
                    for (double l2 = cableUsed; l2 >= lo; l2 -= 0.25)
                    {
                        var t2 = new P2(basePt.X + (toward.X - basePt.X) * l2 / P2.Dist(basePt, toward), basePt.Z + (toward.Z - basePt.Z) * l2 / P2.Dist(basePt, toward));
                        var lay2 = AerialMath.LayFallen(top, basePt, t2, l2 * 1.05, seedLay, walk, 0);
                        double g2 = 0; P2? pv = null;
                        foreach (var gp in AerialMath.GroundPts(lay2)) { if (pv != null) g2 += P2.Dist(pv.Value, gp); pv = gp; }
                        if (g2 > 2.0 * l2 + 2) best = l2;
                    }
                    return "ground length " + F(groundLen) + " for a cable of " + F(cableUsed) + " cells (" + F(groundLen / cableUsed) + "x; blocked " + lay.Blocked + ", walls " + walls + ", seed " + seedLay + ", toward " + toward + "); shrunk: still over 2x+2 at a " + F(best) + "-cell span, cable 1.05x";
                }
                if (!AerialMath.LayTouches(lay, (int)Math.Floor(lay.Tip.X), (int)Math.Floor(lay.Tip.Z)) && lay.TipGrounded) return "tip cell not a contact";
                return null;
            });
            Row("L1_DOWNED_LAY_ON_GROUND_RANDOM", FALLEN.Concat(SHOCK).ToArray(), "random", r.fails == 0 ? "PASS" : "FAIL", 1500,
                "seed " + seed + ": every fallen wire reaches the ground, no grounded point inside a wall, its grounded length at most 2x the cable + 2 cells (nothing created), the tip a shock contact; blocked " + blockedSeen + ", grounded " + groundedSeen + "; " + r.fails + " bad" + (r.first != null ? "; first " + r.first : ""));
        }
        // ---------------------------------------------------------------- shock: who takes it (fixed truth table)
        {
            var bad = new List<string>(); int n = 0;
            foreach (bool flesh in new[] { true, false }) foreach (bool dead in new[] { true, false })
            foreach (bool outd in new[] { true, false }) foreach (bool rs in new[] { true, false })
            {
                n++;
                bool want = flesh && !dead && !outd && !rs;
                if (AerialMath.ShockTakes(flesh, dead, outd, rs) != want) bad.Add(flesh + "/" + dead + "/" + outd + "/" + rs);
            }
            Row("L1_SHOCK_WHO_TAKES_IT", SHOCK, "fixed", bad.Count == 0 ? "PASS" : "FAIL", n,
                bad.Count == 0 ? "a live, conscious flesh pawn is shocked unless it is the fixer of THAT wire; the kernel takes 'restringing' as given: which wire the job targets is game-side (RM_FallenWireShock), owed to lane 2 and Stage 6" : "wrong for " + string.Join(", ", bad));
        }
        // ---------------------------------------------------------------- knockback: thrown off the wire to a free cell (random)
        {
            int seed = 4301;
            var r = Prop(3000, seed, rng =>
            {
                var free = new bool[8]; for (int i = 0; i < 8; i++) free[i] = rng.Next(3) != 0;
                int ax = rng.Next(-3, 4), az = rng.Next(-3, 4);
                var d = AerialMath.KnockbackDir(ax, az, rng.Next(-20, 20), (x, z) => free[Array.IndexOf(AerialMath.Ring8, (x, z))]);
                bool any = free.Any(f => f);
                if (d == null) return any ? "null with a free neighbour" : null;
                int idx = Array.IndexOf(AerialMath.Ring8, d.Value);
                if (idx < 0 || !free[idx]) return "chose a blocked cell " + d;
                if ((ax != 0 || az != 0) && free[Array.IndexOf(AerialMath.Ring8, (Math.Sign(ax), Math.Sign(az)))] && d.Value != (Math.Sign(ax), Math.Sign(az))) return "away direction free but not taken";
                return null;
            });
            Row("L1_SHOCK_KNOCKBACK_RANDOM", SHOCK, "random", r.fails == 0 ? "PASS" : "FAIL", 3000,
                "seed " + seed + ": straight away when free, else the nearest free turn, null only when boxed in; " + r.fails + " bad" + (r.first != null ? "; first " + r.first : ""));
        }
        // ---------------------------------------------------------------- explosions: cut, sway, never both (sweep)
        {
            var bad = new List<string>(); int n = 0;
            foreach (bool harms in new[] { true, false }) foreach (bool kin in new[] { true, false })
            foreach (bool cut in new[] { true, false }) foreach (bool sw in new[] { true, false })
            foreach (double dmg in new[] { 0.0, 10, 200 })
            {
                n++;
                var k = AerialMath.BlastKindFor(harms, kin, dmg, cut, sw);
                if (kin && k == AerialMath.BlastKind.Cut) bad.Add("a kinetic blast cut");
                if (!cut && k == AerialMath.BlastKind.Cut) bad.Add("explosionsCut off still cut");
                if (!harms && k != AerialMath.BlastKind.None) bad.Add("a harmless blast did " + k);
                if (harms && !kin && cut && dmg > 0 && k != AerialMath.BlastKind.Cut) bad.Add("a harmful blast with explosionsCut on did " + k);
            }
            for (double d = 0; d <= 5; d += 0.25)
            {
                n++;
                double f = AerialMath.BlastCutFalloff(d, 5);
                if (f < 0.2 - 1e-9 || f > 1 + 1e-9) bad.Add("falloff " + F(f) + " at " + F(d));
                if (d > 0 && f > AerialMath.BlastCutFalloff(d - 0.25, 5) + 1e-12) bad.Add("falloff rises at " + F(d));
            }
            var hit = AerialMath.BlastSpan(new P2(0, 0), new P2(10, 0), new P2(5, 1), 2, 100, 200, AerialMath.BlastKind.Cut);
            var miss = AerialMath.BlastSpan(new P2(0, 0), new P2(10, 0), new P2(5, 4), 2, 100, 200, AerialMath.BlastKind.Cut);
            var sway = AerialMath.BlastSpan(new P2(0, 0), new P2(10, 0), new P2(5, 1), 2, 100, 200, AerialMath.BlastKind.Sway);
            if (!hit.Cut) bad.Add("200 damage under a 100-hp span did not cut it");
            if (miss.Hit || miss.Cut) bad.Add("a blast 4 cells off with radius 2 hit");
            if (sway.Cut || sway.Hp != 100 || !(sway.Kick > 0)) bad.Add("a sway blast wounded or did not kick");
            Row("L1_DOWNED_BLAST_SWEEP", FALLEN, "sweep", bad.Count == 0 ? "PASS" : "FAIL", n + 3,
                bad.Count == 0 ? "kinetic never cuts, explosionsCut off never cuts, harmless never acts; falloff 1 -> 0.2 monotone; hit test honours the radius" : string.Join("; ", bad.Distinct().Take(6)));
        }
        // ---------------------------------------------------------------- re-string: a job of honest length (sweep)
        {
            var bad = new List<string>(); int n = 0;
            int prev = int.MaxValue;
            for (double s = 0.1; s <= 3.0; s += 0.05)
            {
                n++;
                int t = AerialMath.RestringTicks(s);
                if (t < 1) bad.Add("speed " + F(s) + " -> " + t);
                if (t > prev) bad.Add("slower at higher speed " + F(s));
                prev = t;
            }
            if (AerialMath.RestringTicks(1.0) != 300) bad.Add("speed 1 -> " + AerialMath.RestringTicks(1.0));
            foreach (double s in new[] { 0.0, -1.0, double.NaN })
            {
                n++;
                int t = AerialMath.RestringTicks(s);
                if (t < 1 || t > 3000) bad.Add("speed " + s + " -> " + t + " ticks");
            }
            Row("L1_RESTRING_TICKS_SWEEP", RESTRING, "sweep", bad.Count == 0 ? "PASS" : "FAIL", n,
                bad.Count == 0 ? "300 ticks at speed 1, never below 1, never slower with skill; 0 / negative / NaN speed stay in 1..3000" : string.Join("; ", bad.Take(6)));
        }
        // ---------------------------------------------------------------- watchdog: an up span on two nets is repaired, a cut one is not
        {
            var reads = new List<SpanNetRead>
            {
                new SpanNetRead { Span = 1, NetA = 3, NetB = 3, State = SpanState.Up },
                new SpanNetRead { Span = 2, NetA = 3, NetB = 4, State = SpanState.Up },
                new SpanNetRead { Span = 3, NetA = -1, NetB = 4, State = SpanState.Up },
                new SpanNetRead { Span = 4, NetA = 3, NetB = 4, State = SpanState.Cut },
            };
            var rep = AerialMath.WatchdogRepairs(reads);
            bool ok = rep.SequenceEqual(new[] { 2, 3 });
            Row("L1_SPAN_ONE_NET_WATCHDOG", SPANS.Concat(GRAV).ToArray(), "fixed", ok ? "PASS" : "FAIL", 4,
                ok ? "an up span whose ends sit on two nets or none is repaired; a cut span is meant to split" : "repairs " + string.Join(",", rep));
        }
        // ---------------------------------------------------------------- tap: one way, never more than offered, shared by many (random + conservation)
        {
            int seed = 4401; double k = 1.0 / 60000.0 * 0.6; // any positive watt -> watt-day factor
            var r = Prop(5000, seed, rng =>
            {
                double rate = 50 * rng.Next(1, 41);
                double gain = (rng.NextDouble() - 0.4) * 0.02, stored = rng.Next(3) == 0 ? 0 : rng.NextDouble() * 5;
                bool same = rng.Next(10) == 0, en = rng.Next(10) != 0;
                int taps = rng.Next(1, 5);
                double taken = 0;
                for (int t = 0; t < taps; t++)
                {
                    bool working = rng.Next(8) != 0;
                    double s = AerialMath.TapStolenPerTick(rate, gain, stored, k, same, en, taken, working);
                    if (s < 0 || double.IsNaN(s)) return "negative or NaN theft " + s;
                    if (s > rate * k + 1e-15) return "took " + s + " over its rate " + rate * k;
                    if ((!working || same || !en) && s != 0) return "an off / same-net / disabled tap took " + s;
                    taken += s;
                }
                double offered = Math.Max(0, gain + Math.Max(0, stored));
                if (taken > offered + 1e-12) return taps + " taps took " + taken + " of " + offered + " offered (gain " + gain + ", stored " + stored + ")";
                return null;
            });
            var nanCases = new[] { double.NaN, double.PositiveInfinity, -5.0, 0.0 };
            int nanBad = nanCases.Count(x => AerialMath.TapStolenPerTick(x, 1, 1, k, false, true) != 0);
            Row("L1_TAP_ONE_WAY_CONSERVED_RANDOM", TAP, "random", r.fails == 0 && nanBad == 0 ? "PASS" : "FAIL", 5000 + nanCases.Length,
                "seed " + seed + ": theft never negative, never over rate, never over the victim's surplus + battery even shared by up to 4 taps, zero when off/own net/disabled; NaN/inf/negative/zero rate takes 0 (" + nanBad + " bad); " + r.fails + " bad" + (r.first != null ? "; first " + r.first : ""));
        }
        // ---------------------------------------------------------------- tap: a witness catches it only in sight (sweep)
        {
            var bad = new List<string>(); int n = 0;
            for (double sr = 3; sr <= 30; sr += 1)
                for (double d = 0; d <= 35; d += 0.5)
                    foreach (bool los in new[] { true, false }) foreach (bool up in new[] { true, false }) foreach (bool held in new[] { true, false })
                    {
                        n++;
                        bool want = d <= sr && los && up && !held;
                        if (AerialMath.TheftSpotted(d, sr, los, up, held) != want) bad.Add("range " + sr + " dist " + d + " los " + los + " up " + up + " held " + held);
                    }
            if (AerialMath.TheftSpotted(double.NaN, 12, true, true, false)) bad.Add("NaN distance spotted");
            Row("L1_TAP_SPOTTED_SWEEP", TAP, "sweep", bad.Count == 0 ? "PASS" : "FAIL", n + 1,
                bad.Count == 0 ? "sight range 3..30: caught exactly within range, in line of sight, awake and free" : string.Join("; ", bad.Take(5)));
        }
        // ---------------------------------------------------------------- tap: a steady drain, chunking-independent, stops when the clamp goes (random + conservation)
        {
            int seed = 4402; const int day = 60000;
            var r = Prop(1500, seed, rng =>
            {
                int perDay = rng.Next(0, 11);
                int drain = 0, total = 0, drainingTicks = 0, idleTotal = 0;
                int steps = rng.Next(5, 60);
                for (int i = 0; i < steps; i++)
                {
                    int ticks = rng.Next(1, 3) == 1 ? rng.Next(1, 2500) : rng.Next(1, 90000);
                    bool draining = rng.Next(5) != 0;
                    int g = AerialMath.TheftGoodwillAccrue(ref drain, ticks, draining, perDay, day);
                    if (g > 0) return "goodwill rose by " + g;
                    if (!draining && g != 0) { idleTotal += g; return "an idle clamp cost " + g; }
                    total += g; if (draining) drainingTicks += ticks;
                }
                int want = -(drainingTicks / day) * perDay;
                if (total != want) return "perDay " + perDay + ": " + drainingTicks + " draining ticks charged " + total + " want " + want;
                if (drain != drainingTicks % day) return "remainder " + drain + " want " + drainingTicks % day;
                // the clamp removed: no further charge however long
                int after = AerialMath.TheftGoodwillAccrue(ref drain, 10 * day, false, perDay, day);
                return after == 0 ? null : "charged " + after + " after removal";
            });
            Row("L1_TAP_GOODWILL_STEADY_RANDOM", TAP, "random", r.fails == 0 ? "PASS" : "FAIL", 1500,
                "seed " + seed + ": perDay 0..10 per whole day of draining, the same whatever the tick chunking, remainder carried, nothing while idle or after removal; " + r.fails + " bad" + (r.first != null ? "; first " + r.first : ""));
        }
        // ---------------------------------------------------------------- sway: bounded, still at the insulators (random)
        {
            int seed = 4501;
            var r = Prop(20000, seed, rng =>
            {
                double t = rng.NextDouble(), time = rng.NextDouble() * 1000, wind = rng.NextDouble() * 3, amp = rng.NextDouble() * 2;
                int sd = rng.Next();
                double s = AerialMath.Sway(t, time, wind, amp, sd);
                double cap = 1.3 * amp * Math.Min(wind, 1.5) / 1.5 + 1e-12;
                if (Math.Abs(s) > cap) return "sway " + F(s) + " over cap " + F(cap);
                if (AerialMath.Sway(0, time, wind, amp, sd) != 0 || AerialMath.Sway(1, time, wind, amp, sd) != 0) return "insulator moved";
                double b = AerialMath.BlastSway(t, rng.Next(-10, 400), rng.NextDouble(), rng.Next(2) * 2 - 1, amp, sd);
                if (Math.Abs(b) > amp * AerialMath.BlastSwayGain + 1e-9) return "blast sway " + F(b);
                if (AerialMath.BlastSway(t, AerialMath.BlastSwayTicks, 1, 1, amp, sd) != 0) return "blast sway outlived its window";
                return null;
            });
            Row("L1_SPAN_SWAY_BOUNDS_RANDOM", SPANS, "random", r.fails == 0 ? "PASS" : "FAIL", 20000,
                "seed " + seed + ": wind sway within 1.3 amp min(wind,1.5)/1.5, zero at both insulators; blast sway within 2.5 amp and over by 180 ticks; " + r.fails + " bad" + (r.first != null ? "; first " + r.first : ""));
        }
        // ---------------------------------------------------------------- pipe poles: their own switch (sweep, the kernel half of settings_switch_cleanly)
        {
            var bad = new List<string>(); int n = 0;
            foreach (AerialLineKind kd in new[] { AerialLineKind.Power, AerialLineKind.Pipe })
            foreach (bool p in new[] { true, false }) foreach (bool q in new[] { true, false }) foreach (bool s in new[] { true, false })
            {
                n++;
                bool on = AerialKinds.KindOn(kd, p, q), beh = AerialKinds.KindBehaviour(kd, p, q, s);
                if (kd == AerialLineKind.Power && (on != p || beh != (p && s))) bad.Add("power anchor obeys the pipe switch");
                if (kd == AerialLineKind.Pipe && (on != q || beh != q)) bad.Add("pipe pole obeys the power master");
            }
            Row("L1_SETTINGS_PIPE_POLE_OWN_SWITCH", new[] { "settings_switch_cleanly", "pipe_pole_switch" }, "sweep", bad.Count == 0 ? "PASS" : "FAIL", n,
                bad.Count == 0 ? "a power anchor follows the power master (and its sub-setting), a pipe pole only its own switch" : string.Join("; ", bad.Distinct()));
        }
        foreach (string s in Rows) Console.WriteLine(s);
        Environment.Exit(anyFail ? 1 : 0);
    }
}
