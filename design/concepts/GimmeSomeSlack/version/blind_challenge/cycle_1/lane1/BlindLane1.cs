// Blind lane 1, Gimme Some Slack 0.1.0, cycle 1: game-logic tests written from the bars (tree.json, sheet.md, plan.md) and
// the kernels' public surface alone, before any builder test, journal or evidence was opened. One JSON row per line on
// stdout. Random cases carry their seed; a failing random case is shrunk (fewer runs, shorter runs) and the shrunk form is
// printed. Built by run_lane1.py against the shipped kernels or a planted copy.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using RimMandrake.Shared.Slack;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.GimmeSomeSlack.Aerial;

static class BlindLane1
{
    static int fails;
    static string only = Environment.GetEnvironmentVariable("GSS_BLIND_ONLY") ?? "";

    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") fails++;
        Console.WriteLine(JsonSerializer.Serialize(new Dictionary<string, object>
        { ["id"] = id, ["bars"] = bars, ["kind"] = kind, ["verdict"] = verdict, ["cases"] = cases, ["detail"] = detail }));
    }

    static void Run(string id, Action a)
    {
        if (only != "" && !only.Split(',').Any(o => id.StartsWith(o))) return;
        try { a(); }
        catch (Exception e) { Row(id, new[] { "?" }, "fixed", "FAIL", 0, "threw " + e.GetType().Name + ": " + e.Message + " @ " + (e.StackTrace ?? "").Split('\n').FirstOrDefault()); }
    }

    static int Main()
    {
        Run("L1_SHOCK_TABLE", ShockTable);
        Run("L1_SHOCK_PARSE", ShockParse);
        Run("L1_SHOCK_FIXER_SCOPE", ShockFixerScope);
        Run("L1_SHOCK_END_CELL", ShockEndCell);
        Run("L1_SHOCK_AERIAL_FIXER", ShockAerialFixer);
        Run("L1_TAP_WINDOW_CONSERVES", TapWindowConserves);
        Run("L1_TAP_STOLEN_BOUNDS", TapStolenBounds);
        Run("L1_THEFT_GOODWILL_STEADY", TheftGoodwillSteady);
        Run("L1_THEFT_WITNESS", TheftWitness);
        Run("L1_LINK_VERDICTS", LinkVerdicts);
        Run("L1_LINK_MST", LinkMst);
        Run("L1_SPAN_SAG_SWEEP", SpanSagSweep);
        Run("L1_REMOVAL_PLAN", RemovalPlanCheck);
        Run("L1_WATCHDOG", Watchdog);
        Run("L1_FALLEN_LAY_GROUND", FallenLayGround);
        Run("L1_KIND_SWITCHES", KindSwitches);
        Run("L1_CONDUIT_TARGETS", ConduitTargetsCheck);
        Run("L1_CORD_NET_TRUTH", CordNetTruth);
        Run("L1_CORD_DEVICE_ONE_LEAD", CordDeviceOneLead);
        Run("L1_CORD_SLACK_RATIO", CordSlackRatio);
        Run("L1_CORD_EXCURSION", CordExcursion);
        Run("L1_CORD_WALL_FACE", CordWallFace);
        Run("L1_CORD_SHARP_TURN", CordSharpTurn);
        Run("L1_CORD_BENDS_TALLY", CordBendsTally);
        Run("L1_CORD_RATES", CordRates);
        Run("L1_CUT_ENDS_LIVE_DEAD", CutEndsLiveDead);
        Run("L1_CUT_FAR_SOURCE", CutFarSource);
        Run("L1_JUNCTION_PIECE", JunctionPiece);
        Run("L1_DENSE_TANGLE", DenseTangle);
        Run("L1_NO_REPEAT", NoRepeat);
        Run("L1_BUILD_DETERMINISTIC", BuildDeterministic);
        Run("L1_CACHE_CURRENT_AFTER_CHANGE", CacheCurrent);
        Run("L1_REACH_SOUND", ReachSound);
        Run("L1_REBUILD_GATE", RebuildGateCheck);
        Run("L1_SLICE_WINDOW_MAX", SliceWindowMax);
        Run("L1_SNAPSHOT_POOL", SnapshotPoolCheck);
        Run("L1_SETTINGS_SWEEP_CORDS", SettingsSweepCords);
        Run("L1_NOT_KERNEL", NotKernel);
        return fails > 0 ? 1 : 0;
    }

    // ===================================================================== shock (bars floor_end_shocks_crossers,
    // fallen_wire_shocks_crossers, shock_reach_setting)
    static void ShockTable()
    {
        int cases = 0; var bad = new List<string>();
        foreach (ShockReach r in Enum.GetValues(typeof(ShockReach)))
            foreach (LineKind k in Enum.GetValues(typeof(LineKind)))
                for (int m = 0; m < 32; m++)
                {
                    bool live = (m & 1) != 0, flesh = (m & 2) != 0, dead = (m & 4) != 0, outp = (m & 8) != 0, fix = (m & 16) != 0;
                    // the bars: floor ends bite only under All; downed spans and dropped cords under Only downed lines and All;
                    // nothing under None; only a live line; never the pawn fixing that line; a dead or already-out pawn is not shocked again
                    bool kindBites = r == ShockReach.All || (r == ShockReach.OnlyDownedLines && k != LineKind.FloorEnd);
                    bool want = live && kindBites && flesh && !dead && !outp && !fix;
                    bool got = ShockRule.Takes(r, k, live, flesh, dead, outp, fix);
                    cases++;
                    if (got != want) bad.Add($"{r}/{k}/live={live}/flesh={flesh}/dead={dead}/out={outp}/fix={fix}: got {got}");
                }
        Row("L1_SHOCK_TABLE", new[] { "shock_reach_setting", "floor_end_shocks_crossers", "fallen_wire_shocks_crossers" }, "fixed",
            bad.Count == 0 ? "PASS" : "FAIL", cases, "whole table reach x kind x 5 flags against the bar text; mismatches: " + string.Join("; ", bad.Take(6)));
    }

    static void ShockParse()
    {
        var want = new Dictionary<string, ShockReach?> { ["None"] = ShockReach.None, ["OnlyDownedLines"] = ShockReach.OnlyDownedLines, ["All"] = ShockReach.All,
            ["0"] = null, ["2"] = null, ["7"] = null, [""] = null, ["Everything"] = null, ["true"] = null, ["False"] = null };
        var bad = want.Where(kv => ShockRule.Parse(kv.Key) != kv.Value).Select(kv => kv.Key + "->" + ShockRule.Parse(kv.Key)).ToList();
        // a comma list parses as flags in .NET; report what it gives (a saved value is never written that way)
        string info = "\"None, All\"->" + (ShockRule.Parse("None, All")?.ToString() ?? "null") + ", \"all\"->" + (ShockRule.Parse("all")?.ToString() ?? "null");
        Row("L1_SHOCK_PARSE", new[] { "shock_reach_setting" }, "fixed", bad.Count == 0 ? "PASS" : "FAIL", want.Count,
            "the three names round-trip, numbers and other words refused; mismatches " + string.Join(",", bad) + "; info " + info);
    }

    static void ShockFixerScope()
    {
        // bar: the constructor whose job targets the blueprint/frame JOINING this end is safe; one building some other conduit is shocked.
        // A target joins the end only at the end's own cell or the cell it faces (an orthogonal neighbour); a diagonal or a cell two away never.
        var rng = new Random(20261115); int cases = 0; var bad = new List<string>();
        for (int i = 0; i < 20000; i++)
        {
            int ex = rng.Next(-5, 300), ez = rng.Next(-5, 300), dx = rng.Next(-3, 4), dz = rng.Next(-3, 4);
            bool want = Math.Abs(dx) + Math.Abs(dz) <= 1;
            bool got = ShockRule.TargetJoinsEnd(ex, ez, ex + dx, ez + dz);
            cases++;
            if (got != want && bad.Count < 5) bad.Add($"end({ex},{ez}) target d({dx},{dz}) got {got}");
        }
        Row("L1_SHOCK_FIXER_SCOPE", new[] { "floor_end_shocks_crossers" }, "random", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "seed 20261115; exempt only for a target on the end cell or an orthogonal neighbour; " + (bad.Count == 0 ? "no mismatch" : "shrunk first: " + string.Join("; ", bad)));
    }

    static void ShockEndCell()
    {
        var rng = new Random(7); int cases = 0; var bad = new List<string>();
        for (int i = 0; i < 20000; i++)
        {
            double x = rng.NextDouble() * 300 - 2, z = rng.NextDouble() * 300 - 2;
            var c = ShockRule.EndCell(x, z); cases++;
            if (!(c.x <= x && x < c.x + 1 && c.z <= z && z < c.z + 1) && bad.Count < 5) bad.Add($"tip({x:0.###},{z:0.###})->{c}");
        }
        Row("L1_SHOCK_END_CELL", new[] { "floor_end_shocks_crossers" }, "random", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "seed 7; the one biting cell is the cell holding the drawn tip (only the end cell bites); " + string.Join("; ", bad));
    }

    static void ShockAerialFixer()
    {
        // the older aerial rule: the re-stringer of THIS cut is exempt; ShockTakes carries no line kind or setting
        int cases = 0; var bad = new List<string>();
        for (int m = 0; m < 16; m++)
        {
            bool flesh = (m & 1) != 0, dead = (m & 2) != 0, outp = (m & 4) != 0, rs = (m & 8) != 0;
            bool want = flesh && !dead && !outp && !rs; cases++;
            if (AerialMath.ShockTakes(flesh, dead, outp, rs) != want) bad.Add(m.ToString());
            if (ShockRule.Takes(ShockReach.All, LineKind.DownedSpan, true, flesh, dead, outp, rs) != want) bad.Add("rule" + m);
        }
        Row("L1_SHOCK_AERIAL_FIXER", new[] { "fallen_wire_shocks_crossers" }, "fixed", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "AerialMath.ShockTakes agrees with ShockRule.Takes under All for a live downed span; mismatching masks " + string.Join(",", bad));
    }

    // ===================================================================== theft (bar tap_steals_and_costs_goodwill)
    sealed class Fac { public string N; public Fac(string n) { N = n; } }

    static void TapWindowConserves()
    {
        var rng = new Random(424242); int cases = 0; string fail = null;
        for (int trial = 0; trial < 3000 && fail == null; trial++)
        {
            var facs = Enumerable.Range(0, 1 + rng.Next(4)).Select(i => new Fac("f" + i)).ToArray();
            var drained = new Dictionary<Fac, double>(); var ticks = new Dictionary<Fac, int>();
            var charged = new Dictionary<Fac, double>(); var chargedTicks = new Dictionary<Fac, int>();
            var win = new TapWindow<Fac, Fac>();
            Action<Fac, float, int> flush = (v, wd, t) => { charged[v] = charged.GetValueOrDefault(v) + wd; chargedTicks[v] = chargedTicks.GetValueOrDefault(v) + t; };
            int n = rng.Next(1, 400); var trace = new List<string>();
            for (int t = 0; t < n; t++)
            {
                Fac f = facs[rng.Next(facs.Length)];
                float s = rng.Next(5) == 0 ? 0f : (float)(rng.NextDouble() * 3);
                trace.Add(f.N + ":" + s.ToString("0.00"));
                win.Drain(f, f, s, flush);
                if (s > 0) { drained[f] = drained.GetValueOrDefault(f) + s; ticks[f] = ticks.GetValueOrDefault(f) + 1; }
                if (rng.Next(250) == 0) win.Flush(flush);
            }
            win.Flush(flush);
            cases++;
            foreach (Fac f in facs)
            {
                double a = drained.GetValueOrDefault(f), b = charged.GetValueOrDefault(f);
                if (Math.Abs(a - b) > 1e-3 * Math.Max(1, a) || ticks.GetValueOrDefault(f) != chargedTicks.GetValueOrDefault(f))
                { fail = $"seed 424242 trial {trial}: faction {f.N} drained {a:0.###}/{ticks.GetValueOrDefault(f)} ticks, charged {b:0.###}/{chargedTicks.GetValueOrDefault(f)}; trace head {string.Join(" ", trace.Take(8))}"; break; }
            }
        }
        Row("L1_TAP_WINDOW_CONSERVES", new[] { "tap_steals_and_costs_goodwill" }, "random", fail == null ? "PASS" : "FAIL", cases,
            fail ?? "seed 424242; every faction is charged exactly the energy and draining ticks taken from it, none from another (victim switches, idle ticks, early flushes)");
    }

    static void TapStolenBounds()
    {
        var rng = new Random(99); int cases = 0; var bad = new List<string>(); double k = 1.0 / 60000;
        for (int i = 0; i < 20000; i++)
        {
            double rate = rng.Next(8) == 0 ? -rng.NextDouble() * 100 : rng.NextDouble() * 2000, gain = (rng.NextDouble() - 0.4) * 0.05, stored = (rng.NextDouble() - 0.2) * 500;
            bool same = rng.Next(6) == 0, en = rng.Next(6) != 0, working = rng.Next(6) != 0; double others = rng.NextDouble() * 0.03;
            double s = AerialMath.TapStolenPerTick(rate, gain, stored, k, same, en, others, working); cases++;
            double avail = gain - others + Math.Max(0, stored);
            bool ok = s >= 0 && (!(same || !en || !working || rate <= 0) || s == 0) && s <= Math.Max(0, rate) * k + 1e-12 && s <= Math.Max(0, avail) + 1e-12;
            if (!ok && bad.Count < 4) bad.Add($"rate {rate:0.#} gain {gain:0.####} stored {stored:0.#} others {others:0.####} same {same} en {en} work {working} -> {s}");
        }
        // several taps on one victim in one tick: their sum never exceeds the victim's surplus (sharing, not each claiming it all)
        int sumBad = 0;
        for (int i = 0; i < 5000; i++)
        {
            double gain = rng.NextDouble() * 0.02, taken = 0; int taps = rng.Next(1, 6);
            for (int t = 0; t < taps; t++) taken += AerialMath.TapStolenPerTick(2000, gain, 0, k, false, true, taken, true);
            cases++; if (taken > gain + 1e-12) sumBad++;
        }
        foreach (double nan in new[] { double.NaN, double.PositiveInfinity })
        { cases++; double s = AerialMath.TapStolenPerTick(nan, 1, 1, k, false, true); if (!(s == 0)) bad.Add("rate " + nan + " -> " + s); }
        Row("L1_TAP_STOLEN_BOUNDS", new[] { "tap_steals_and_costs_goodwill" }, "random", bad.Count == 0 && sumBad == 0 ? "PASS" : "FAIL", cases,
            "seed 99; 0 <= stolen <= rate x k and <= the victim's own surplus; 0 off, on our own net or broken; taps sharing a victim never take more than its surplus (over: " + sumBad + "); " + string.Join("; ", bad));
    }

    static void TheftGoodwillSteady()
    {
        // caught: goodwill drains steadily, perDay per whole day of draining; idle accrues nothing; removing the clamp stops it
        var rng = new Random(31337); int cases = 0; var bad = new List<string>(); const int day = 60000;
        for (int perDay = 0; perDay <= 10; perDay++)
            for (int trial = 0; trial < 200; trial++)
            {
                int acc = 0, total = 0, drainT = 0, chunks = rng.Next(1, 60); var daily = new List<int>();
                for (int c = 0; c < chunks; c++)
                {
                    int t = rng.Next(1, 20000); bool draining = rng.Next(4) != 0;
                    total += AerialMath.TheftGoodwillAccrue(ref acc, t, draining, perDay, day);
                    if (draining) drainT += t;
                }
                cases++;
                int want = -perDay * (drainT / day);
                if (total != want && bad.Count < 4) bad.Add($"perDay {perDay} drainTicks {drainT}: got {total} want {want}");
                // after removal no more drain however long
                int after = AerialMath.TheftGoodwillAccrue(ref acc, 10 * day, false, perDay, day);
                if (after != 0 && bad.Count < 4) bad.Add("idle after removal charged " + after);
            }
        // steady: one charge per day of continuous drain, never a single lump
        int a2 = 0, lumps = 0;
        for (int d = 0; d < 30; d++) { int g = 0; for (int t = 0; t < day; t += 250) g += AerialMath.TheftGoodwillAccrue(ref a2, 250, true, 2, day); if (g != -2) lumps++; }
        cases += 30;
        Row("L1_THEFT_GOODWILL_STEADY", new[] { "tap_steals_and_costs_goodwill" }, "sweep", bad.Count == 0 && lumps == 0 ? "PASS" : "FAIL", cases,
            "seed 31337; theftGoodwillPerDay swept 0..10 (slider); total = -perDay x whole draining days, remainder carried; idle and removed clamps cost nothing; 30 days of 250-tick polls charge -2 each day (days off: " + lumps + "); " + string.Join("; ", bad));
    }

    static void TheftWitness()
    {
        var rng = new Random(5); int cases = 0; var bad = new List<string>();
        for (int range = 3; range <= 30; range++)
            for (int i = 0; i < 300; i++)
            {
                double d = rng.NextDouble() * 40; bool los = rng.Next(3) != 0, up = rng.Next(4) != 0, held = rng.Next(6) == 0;
                bool want = d <= range && los && up && !held; cases++;
                if (AerialMath.TheftSpotted(d, range, los, up, held) != want && bad.Count < 4) bad.Add($"d {d:0.##} r {range} los {los} up {up} held {held}");
            }
        cases++; if (AerialMath.TheftSpotted(double.NaN, 12, true, true, false)) bad.Add("NaN distance spotted");
        Row("L1_THEFT_WITNESS", new[] { "tap_steals_and_costs_goodwill" }, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "seed 5; theftSightRange swept 3..30; no drain without a witness: spotted only within range, with sight, awake and up, not our prisoner; " + string.Join("; ", bad));
    }

    // ===================================================================== overhead lines (spans_above_everything, fallen_span_on_ground,
    // gravship_keeps_connections, settings_switch_cleanly pipe-pole switch)
    static AnchorInfo An(int id, int x, int z, int fac = 1, int max = 4, bool roof = false, AerialLineKind k = AerialLineKind.Power, bool anchor = true)
        => new AnchorInfo { Id = id, X = x, Z = z, Faction = fac, MaxLinks = max, Roofed = roof, Kind = k, IsAnchor = anchor };

    static void LinkVerdicts()
    {
        var bad = new List<string>(); int cases = 0;
        void Want(LinkVerdict w, AnchorInfo a, AnchorInfo b, double r) { cases++; var g = AerialMath.CanLink(a, b, r); if (g != w) bad.Add($"want {w} got {g}"); }
        Want(LinkVerdict.Ok, An(1, 0, 0), An(2, 10, 0), 20);
        Want(LinkVerdict.OutOfRange, An(1, 0, 0), An(2, 21, 0), 20);
        Want(LinkVerdict.Ok, An(1, 0, 0), An(2, 12, 16), 20);      // exactly 20 cells
        Want(LinkVerdict.OutOfRange, An(1, 0, 0), An(2, 12, 17), 20);
        Want(LinkVerdict.Foreign, An(1, 0, 0), An(2, 5, 0, fac: 2), 20);
        Want(LinkVerdict.Roofed, An(1, 0, 0, roof: true), An(2, 5, 0), 20);
        Want(LinkVerdict.WrongKind, An(1, 0, 0), An(2, 5, 0, k: AerialLineKind.Pipe), 20);
        Want(LinkVerdict.NotAnchor, An(1, 0, 0), An(2, 5, 0, anchor: false), 20);
        Want(LinkVerdict.Self, An(1, 0, 0), An(1, 0, 0), 20);
        var full = An(1, 0, 0, max: 1); full.Linked.Add(9);
        Want(LinkVerdict.FullA, full, An(2, 5, 0), 20);
        var linked = An(1, 0, 0); linked.Linked.Add(2);
        Want(LinkVerdict.AlreadyLinked, linked, An(2, 5, 0), 20);
        // random: an Ok verdict always means same faction, same kind, both unroofed anchors, within range and room on both ends
        var rng = new Random(2468);
        for (int i = 0; i < 20000; i++)
        {
            var a = An(rng.Next(1, 50), rng.Next(0, 60), rng.Next(0, 60), rng.Next(1, 3), rng.Next(0, 4), rng.Next(8) == 0, rng.Next(5) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power);
            var b = An(rng.Next(1, 50), rng.Next(0, 60), rng.Next(0, 60), rng.Next(1, 3), rng.Next(0, 4), rng.Next(8) == 0, rng.Next(5) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power);
            for (int l = rng.Next(3); l > 0; l--) a.Linked.Add(rng.Next(1, 50));
            double r = rng.Next(8, 41); cases++;
            if (AerialMath.CanLink(a, b, r) == LinkVerdict.Ok)
            {
                double d = Math.Sqrt((a.X - b.X) * (a.X - b.X) + (a.Z - b.Z) * (a.Z - b.Z));
                if (a.Id == b.Id || a.Faction != b.Faction || a.Kind != b.Kind || a.Roofed || b.Roofed || d > r + 1e-6 || a.Linked.Count >= a.MaxLinks || b.Linked.Count >= b.MaxLinks || a.Linked.Contains(b.Id))
                    if (bad.Count < 8) bad.Add($"seed 2468 case {i}: Ok for a{a.Id}({a.X},{a.Z}) b{b.Id}({b.X},{b.Z}) r {r}");
            }
        }
        Row("L1_LINK_VERDICTS", new[] { "spans_above_everything", "overhead_spans" }, "random", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "the bad links refused with their reasons (range, faction, roof, kind, full, self, already linked) at fixed cases and 20000 random pairs (seed 2468); " + string.Join("; ", bad));
    }

    static void LinkMst()
    {
        var rng = new Random(1357); int cases = 0; string fail = null;
        for (int trial = 0; trial < 1500 && fail == null; trial++)
        {
            int n = rng.Next(2, 14); double r = rng.Next(8, 41);
            var sel = Enumerable.Range(1, n).Select(i => An(i, rng.Next(0, 80), rng.Next(0, 80), 1, rng.Next(1, 5))).ToList();
            var links = AerialMath.MinimumSpanningLinks(sel, r); cases++;
            var parent = Enumerable.Range(0, n + 1).ToArray(); int F(int x) => parent[x] == x ? x : parent[x] = F(parent[x]);
            var deg = new int[n + 1];
            foreach (var (a, b) in links)
            {
                var A = sel[a - 1]; var B = sel[b - 1];
                if (!AerialMath.InRange(A.X, A.Z, B.X, B.Z, r)) { fail = $"trial {trial}: link {a}-{b} out of range"; break; }
                if (F(a) == F(b)) { fail = $"trial {trial}: link {a}-{b} closes a cycle"; break; }
                parent[F(a)] = F(b); deg[a]++; deg[b]++;
                if (deg[a] > A.MaxLinks || deg[b] > B.MaxLinks) { fail = $"trial {trial}: maxLinks broken at {a}-{b}"; break; }
            }
            if (fail != null) break;
            // with room everywhere (maxLinks >= n) the forest must join every pair that is joinable through in-range hops
            if (sel.All(s => s.MaxLinks >= 4))
            {
                var p2 = Enumerable.Range(0, n + 1).ToArray(); int G(int x) => p2[x] == x ? x : p2[x] = G(p2[x]);
                for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (AerialMath.InRange(sel[i].X, sel[i].Z, sel[j].X, sel[j].Z, r)) p2[G(i + 1)] = G(j + 1);
                for (int i = 1; i <= n; i++) for (int j = i + 1; j <= n; j++)
                        if (G(i) == G(j) && F(i) != F(j) && fail == null && sel.Count <= 4) fail = $"trial {trial}: {i} and {j} joinable but left apart";
            }
        }
        Row("L1_LINK_MST", new[] { "overhead_spans" }, "random", fail == null ? "PASS" : "FAIL", cases,
            fail ?? "seed 1357; auto-link-selected: every link in range, no cycle, maxLinks kept, small joinable sets joined (graph connectivity conserved)");
    }

    static void SpanSagSweep()
    {
        int cases = 0; var bad = new List<string>(); int straightAtZero = 0;
        for (double sag = 0; sag <= 0.15001; sag += 0.01)
            for (int len = 4; len <= 40; len += 2)
                for (int ang = 0; ang < 8; ang++)
                {
                    double th = ang * Math.PI / 4; var a = new P2(10, 10); var b = new P2(10 + len * Math.Cos(th), 10 + len * Math.Sin(th));
                    var pts = AerialMath.SpanCurve(a, b, sag); cases++;
                    if (P2.Dist(pts[0], a) > 1e-9 || P2.Dist(pts[pts.Count - 1], b) > 1e-9) { bad.Add($"ends moved sag {sag} len {len}"); continue; }
                    double deepest = 0; var ts = AerialMath.SpanTs(P2.Dist(a, b), 0.5);
                    if (ts.Count != pts.Count) { bad.Add($"sample count {pts.Count} vs fractions {ts.Count}"); continue; }
                    for (int i = 0; i < pts.Count; i++)
                    {
                        var on = P2.Lerp(a, b, ts[i]);
                        double drop = on.Z - pts[i].Z; // screen-down = hanging
                        if (drop < -1e-9 && bad.Count < 5) bad.Add($"point above chord sag {sag} len {len}");
                        deepest = Math.Max(deepest, drop);
                    }
                    double want = AerialKinds.SagDepth(P2.Dist(a, b), sag);
                    if (Math.Abs(deepest - want) > 0.02 * Math.Max(0.05, want) + 1e-6 && bad.Count < 5) bad.Add($"sag {sag:0.00} len {len} ang {ang}: deepest {deepest:0.###} want {want:0.###}");
                    if (sag == 0 && deepest < 1e-9) straightAtZero++;
                }
        Row("L1_SPAN_SAG_SWEEP", new[] { "spans_above_everything", "overhead_spans" }, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "sag slider 0..0.15 x span 4..40 x 8 headings: ends exactly at the insulators, every sample at or below its chord point (screen-down = hanging), deepest drop = sag x span; " + string.Join("; ", bad));
        Row("L1_SPAN_SAG_ZERO_INFO", new[] { "spans_above_everything" }, "info", "INFO", straightAtZero,
            "the sag slider reaches 0 (AerialSettings sag 0..0.15, default 0.06): at 0 every span is ruler-straight (" + straightAtZero + " curves), which the bar's 'must not read as a ruler-straight wire' names; the shipped default sags");
    }

    static void RemovalPlanCheck()
    {
        var rng = new Random(8642); int cases = 0; string fail = null;
        for (int trial = 0; trial < 5000 && fail == null; trial++)
        {
            int id = 100; var spans = new List<(int, SpanState)>(); int n = rng.Next(0, 6);
            for (int i = 0; i < n; i++) spans.Add((rng.Next(1, 8), rng.Next(3) == 0 ? SpanState.Cut : SpanState.Up));
            bool killed = rng.Next(2) == 0; HashSet<int> aboard = rng.Next(3) == 0 ? new HashSet<int>(Enumerable.Range(1, 7).Where(x => rng.Next(2) == 0)) : null;
            var plan = AerialMath.PlanRemoval(id, killed, spans, aboard); cases++;
            var partners = spans.Select(s => s.Item1).Distinct().ToList();
            int upCount = spans.Count(s => s.Item2 == SpanState.Up);
            if (killed)
            {
                if (plan.Fallen.Count != upCount) fail = $"trial {trial}: killed with {upCount} up spans dropped {plan.Fallen.Count}";
                else if (plan.Fallen.Any(f => !f.TowardDead)) fail = "fallen not toward the dead anchor";
                else if (partners.Any(p => !plan.Reseed.Contains(p))) fail = "a partner not re-seeded after a kill";
            }
            else if (aboard == null)
            {
                if (plan.Fallen.Count != 0) fail = $"trial {trial}: dismantled but {plan.Fallen.Count} wires fell";
                else if (partners.Any(p => !plan.Reseed.Contains(p))) fail = "a partner not re-seeded after a dismantle";
            }
            else
            {
                if (plan.Fallen.Count != 0) fail = $"trial {trial}: gravship lift dropped wires";
                else if (partners.Any(p => aboard.Contains(p) != plan.Kept.Contains(p))) fail = $"trial {trial}: kept set wrong";
                else if (partners.Any(p => !aboard.Contains(p) != plan.Grounded.Contains(p))) fail = $"trial {trial}: grounded set wrong";
                else if (plan.Kept.Any(p => plan.Reseed.Contains(p))) fail = "a kept (flying) partner re-seeded";
            }
            if (fail != null) fail += $" (killed {killed}, spans [{string.Join(",", spans)}], aboard [{(aboard == null ? "null" : string.Join(",", aboard))}])";
        }
        Row("L1_REMOVAL_PLAN", new[] { "fallen_span_on_ground", "gravship_keeps_connections", "downed_spans", "gravship_connectivity" }, "random", fail == null ? "PASS" : "FAIL", cases,
            fail ?? "seed 8642; a killed mast drops every up span onto its survivor, a cut span drops nothing new, dismantling coils, a gravship keeps spans to partners aboard and coils the rest, every partner left behind is re-seeded");
    }

    static void Watchdog()
    {
        var rng = new Random(11); int cases = 0; var bad = new List<string>();
        for (int i = 0; i < 20000; i++)
        {
            var r = new SpanNetRead { Span = i, NetA = rng.Next(-1, 3), NetB = rng.Next(-1, 3), State = rng.Next(3) == 0 ? SpanState.Cut : SpanState.Up };
            bool want = r.State == SpanState.Up && !(r.NetA >= 0 && r.NetA == r.NetB);
            bool got = AerialMath.WatchdogRepairs(new[] { r }).Contains(i); cases++;
            if (got != want && bad.Count < 4) bad.Add($"{r.State} {r.NetA}/{r.NetB} got {got}");
        }
        Row("L1_WATCHDOG", new[] { "overhead_spans", "connectivity_truth" }, "random", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "seed 11; an up span whose two ends are not on one net is repaired; a cut span is meant to split its nets; " + string.Join("; ", bad));
    }

    static void FallenLayGround()
    {
        var rng = new Random(97531); int cases = 0; string fail = null; int blocked = 0;
        for (int trial = 0; trial < 1500 && fail == null; trial++)
        {
            var walls = new HashSet<(int, int)>();
            for (int i = rng.Next(0, 30); i > 0; i--) walls.Add((rng.Next(0, 40), rng.Next(0, 40)));
            Func<int, int, bool> walk = (x, z) => x >= 0 && z >= 0 && x < 40 && z < 40 && !walls.Contains((x, z));
            int bx = rng.Next(8, 32), bz = rng.Next(8, 32); walls.Remove((bx, bz));
            var basePt = new P2(bx + 0.5, bz + 0.5); var top = new P2(basePt.X, basePt.Z + 1.6);
            double ang = rng.NextDouble() * 2 * Math.PI, dist = rng.Next(4, 20);
            var toward = new P2(basePt.X + dist * Math.Cos(ang), basePt.Z + dist * Math.Sin(ang));
            double length = dist * 1.05;
            var l = AerialMath.LayFallen(top, basePt, toward, length, trial, walk); cases++;
            if (l.Blocked) blocked++;
            if (!l.TipGrounded) { if (!l.Blocked) fail = $"trial {trial}: unblocked wire never reached the ground"; continue; }
            var g = AerialMath.GroundPts(l).ToList();
            double run = 0; for (int i = 1; i < l.Pts.Count; i++) run += P2.Dist(l.Pts[i - 1], l.Pts[i]);
            foreach (var p in g)
            {
                if (P2.Dist(p, basePt) < 0.75) continue; // the first 0.75 cell is the base's own face (documented)
                if (!walk((int)Math.Floor(p.X), (int)Math.Floor(p.Z)))
                {
                    double fx = p.X - Math.Floor(p.X), fz = p.Z - Math.Floor(p.Z), depth = Math.Min(Math.Min(fx, 1 - fx), Math.Min(fz, 1 - fz));
                    fail = $"seed 97531 trial {trial}: base ({bx},{bz}) toward ({toward.X:0.##},{toward.Z:0.##}) length {length:0.##}, not Blocked, grounded point {p.X:0.###},{p.Z:0.###} lies {depth:0.###} cell inside wall cell ({Math.Floor(p.X)},{Math.Floor(p.Z)}) ({walls.Count} walls; smallest: the one wall cell it clips)"; break;
                }
            }
            if (fail == null && !AerialMath.LayTouches(l, (int)Math.Floor(l.Tip.X), (int)Math.Floor(l.Tip.Z))) fail = $"trial {trial}: tip cell not a contact";
        }
        Row("L1_FALLEN_LAY_GROUND", new[] { "fallen_span_on_ground", "fallen_wire_shocks_crossers" }, "random", fail == null ? "PASS" : "FAIL", cases,
            fail ?? $"seed 97531; a fallen wire reaches the ground unless a wall stops it ({blocked} blocked), every grounded point past the base lies on a walkable cell, the tip's cell is a shock contact");
    }

    static void KindSwitches()
    {
        var bad = new List<string>(); int cases = 0;
        foreach (bool p in new[] { false, true }) foreach (bool q in new[] { false, true }) foreach (bool s in new[] { false, true })
                {
                    cases++;
                    if (AerialKinds.KindOn(AerialLineKind.Power, p, q) != p) bad.Add("power anchor follows pipe switch");
                    if (AerialKinds.KindOn(AerialLineKind.Pipe, p, q) != q) bad.Add("pipe pole follows power switch");
                    if (AerialKinds.KindBehaviour(AerialLineKind.Power, p, q, s) != (p && s)) bad.Add("power behaviour");
                    if (AerialKinds.KindBehaviour(AerialLineKind.Pipe, p, q, s) != q) bad.Add("pipe behaviour");
                }
        cases += 2;
        if (AerialKinds.CarriesPower(AerialLineKind.Pipe)) bad.Add("pipe carries power");
        if (AerialKinds.StrandCap(AerialLineKind.Pipe, 3) != 1) bad.Add("pipe more than one strand");
        Row("L1_KIND_SWITCHES", new[] { "settings_switch_cleanly", "pipe_pole_switch" }, "fixed", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "pipe poles obey their own switch only, power anchors only the power master; a pipe joins no power net; " + string.Join("; ", bad.Distinct()));
    }

    static void ConduitTargetsCheck()
    {
        var rng = new Random(3); int cases = 0; var bad = new List<string>();
        string[] names = { "PowerConduit", "WaterproofConduit", "RM_A", "RM_B", "X" };
        for (int i = 0; i < 2000; i++)
        {
            var ex = new List<string>(); var want = new HashSet<string>(names);
            for (int t = rng.Next(0, 8); t > 0; t--) { string n = names[rng.Next(names.Length)]; bool on = rng.Next(2) == 0; ConduitTargets.Toggle(ex, n, on); if (on) want.Add(n); else want.Remove(n); }
            var got = ConduitTargets.Select(names, ex); cases++;
            if (!got.SequenceEqual(names.Where(want.Contains))) bad.Add(string.Join(",", got));
            if (ex.Count != ex.Distinct().Count()) bad.Add("duplicate exclusion");
        }
        Row("L1_CONDUIT_TARGETS", new[] { "conduit_invisible", "invisible_conduit" }, "random", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "seed 3; the per-def toggles: an unticked conduit def keeps vanilla, every other candidate is drawn as cords, order kept; " + string.Join("; ", bad.Take(3)));
    }

    // ===================================================================== cord scenes
    sealed class Scene
    {
        public CordWorld W; public int Seed; public int Runs, MaxLen; public bool Walls;
        public List<MachineInfo> Ms = new List<MachineInfo>();
        public string Desc => $"seed {Seed} runs {Runs} maxLen {MaxLen} walls {Walls}";
    }

    // Random sparse base: runs of conduit as orthogonal random walks; each run end gets a device beside it (a source on some),
    // walls optionally laid across some runs (conduit passes under them, buried). Shrinkable by runs and maxLen.
    static Scene MakeScene(int seed, int runs, int maxLen, bool walls, int size = 48)
    {
        var rng = new Random(seed); var w = new CordWorld(size, size); var sc = new Scene { W = w, Seed = seed, Runs = runs, MaxLen = maxLen, Walls = walls };
        var used = new HashSet<Cell>(); int mid = 0;
        for (int r = 0; r < runs; r++)
        {
            var c = new Cell(rng.Next(4, size - 4), rng.Next(4, size - 4)); var run = new List<Cell>();
            int len = rng.Next(3, maxLen + 1); Cell dir = Cell.Dirs4[rng.Next(4)];
            for (int i = 0; i < len; i++)
            {
                if (c.X < 3 || c.Z < 3 || c.X >= size - 3 || c.Z >= size - 3) break;
                run.Add(c); w.SetConduit(c);
                if (rng.Next(4) == 0) dir = Cell.Dirs4[rng.Next(4)];
                c = c + dir;
            }
            foreach (var x in run) used.Add(x);
            if (run.Count < 2) continue;
            foreach (Cell end in new[] { run[0], run[run.Count - 1] })
            {
                if (rng.Next(4) == 0) continue;
                foreach (Cell d in Cell.Dirs4.OrderBy(_ => rng.Next()))
                {
                    Cell m = end + d;
                    if (!w.InBounds(m) || w.IsConduit(m) || used.Contains(m) || sc.Ms.Any(o => o.Hookups.Contains(end))) continue;
                    var kind = rng.Next(3) == 0 ? MachineKind.Source : rng.Next(5) == 0 ? MachineKind.Battery : MachineKind.Consumer;
                    var mi = new MachineInfo { Id = "m" + (mid++), DefName = kind.ToString(), Kind = kind, X0 = m.X, Z0 = m.Z };
                    mi.Hookups.Add(end); w.Machines.Add(mi); sc.Ms.Add(mi); used.Add(m);
                    w.SetBlocked(m, BlockKind.Device);
                    break;
                }
            }
        }
        if (walls)
            for (int i = rng.Next(1, 4); i > 0; i--)
            {
                bool horiz = rng.Next(2) == 0; int at = rng.Next(6, size - 6), from = rng.Next(2, size / 2), to = from + rng.Next(5, size / 2);
                for (int k = from; k < Math.Min(to, size - 2); k++)
                {
                    var c = horiz ? new Cell(k, at) : new Cell(at, k);
                    if (used.Contains(c) && !w.IsConduit(c)) continue; // never wall over a device
                    w.SetBlocked(c, BlockKind.Wall);
                }
            }
        return sc;
    }

    // conduit components (4-way, buried included); a machine joins its hookup's component
    static Dictionary<Cell, int> Components(CordWorld w)
    {
        var comp = new Dictionary<Cell, int>(); int id = 0;
        foreach (Cell s in w.ConduitCells())
        {
            if (comp.ContainsKey(s)) continue;
            var q = new Queue<Cell>(); q.Enqueue(s); comp[s] = id;
            while (q.Count > 0) { var c = q.Dequeue(); foreach (var d in Cell.Dirs4) { var n = c + d; if (w.IsConduit(n) && !comp.ContainsKey(n)) { comp[n] = id; q.Enqueue(n); } } }
            id++;
        }
        return comp;
    }

    static Cell? ParseEndCell(string e)
    {
        if (e == null) return null;
        var m = System.Text.RegularExpressions.Regex.Match(e, @":(-?\d+),(-?\d+)");
        return m.Success ? new Cell(int.Parse(m.Groups[1].Value), int.Parse(m.Groups[2].Value)) : (Cell?)null;
    }

    static int? CompOf(CordWorld w, Dictionary<Cell, int> comp, Cell c)
    {
        if (comp.TryGetValue(c, out int k)) return k;
        var ks = Cell.Dirs4.Select(d => c + d).Where(comp.ContainsKey).Select(n => comp[n]).Distinct().ToList();
        return ks.Count == 1 ? ks[0] : (int?)null;
    }

    static List<LaidPiece> Build(CordWorld w, BuildOptions o = null, Func<Cell, bool> live = null, CordBuilder b = null)
        => (b ?? new CordBuilder()).Build(w, o ?? new BuildOptions(), live ?? (c => true));

    static bool HasPts(CordStrand s) => s.Pts != null && s.Pts.Count >= 2;

    // A property over random scenes, shrunk on failure (fewer runs, then shorter runs). check returns null or the failure text.
    static void Prop(string id, string[] bars, int trials, int baseSeed, int runs, int maxLen, bool walls, Func<Scene, List<LaidPiece>, string> check, string what, Func<BuildOptions> opt = null)
    {
        int cases = 0; string fail = null; Scene failing = null;
        for (int t = 0; t < trials; t++)
        {
            var sc = MakeScene(baseSeed + t, runs, maxLen, walls); cases++;
            string f = check(sc, Build(sc.W, opt?.Invoke()));
            if (f != null) { fail = f; failing = sc; break; }
        }
        if (fail != null)
        {
            int r = failing.Runs, l = failing.MaxLen; string last = fail; Scene best = failing;
            bool progress = true;
            while (progress)
            {
                progress = false;
                foreach (var (rr, ll) in new[] { (r - 1, l), (r, l - 2), (r / 2, l) })
                {
                    if (rr < 1 || ll < 3 || (rr == r && ll == l)) continue;
                    var sc = MakeScene(failing.Seed, rr, ll, failing.Walls);
                    string f = check(sc, Build(sc.W, opt?.Invoke()));
                    if (f != null) { r = rr; l = ll; last = f; best = sc; progress = true; break; }
                }
            }
            Row(id, bars, "random", "FAIL", cases, $"{what}; first failure {failing.Desc}: {fail}; SHRUNK to {best.Desc}: {last}");
        }
        else Row(id, bars, "random", "PASS", cases, $"{what}; seeds {baseSeed}..{baseSeed + trials - 1}, runs {runs}, maxLen {maxLen}, walls {walls}: no failure");
    }

    static void CordNetTruth()
    {
        Prop("L1_CORD_NET_TRUTH", new[] { "drawing_true_to_grid", "connectivity_truth" }, 60, 1000, 8, 14, true, (sc, ps) =>
        {
            var comp = Components(sc.W); int unknown = 0;
            foreach (var p in ps)
            {
                Cell? a = ParseEndCell(p.EndA), b = ParseEndCell(p.EndB);
                if (a == null || b == null) continue;
                int? ca = CompOf(sc.W, comp, a.Value), cb = CompOf(sc.W, comp, b.Value);
                if (ca == null || cb == null) { unknown++; continue; }
                if (ca != cb) return $"cord {p.EndA} -> {p.EndB} joins two separate conduit nets ({ca} vs {cb})";
            }
            return null;
        }, "no drawn cord joins two separate conduit nets (both ends of every piece on one conduit component)");
    }

    static void CordDeviceOneLead()
    {
        Prop("L1_CORD_DEVICE_ONE_LEAD", new[] { "drawing_true_to_grid", "connectivity_truth" }, 60, 2000, 8, 14, false, (sc, ps) =>
        {
            foreach (var m in sc.Ms)
            {
                Cell h = m.Hookups[0];
                string tag = ":" + h.X + "," + h.Z;
                // a run of conduit holding only this device is still a net: it must get exactly one lead
                int n = ps.Count(p => (p.EndA != null && p.EndA.StartsWith(Name(m.Kind)) && p.EndA.EndsWith(tag)) || (p.EndB != null && p.EndB.StartsWith(Name(m.Kind)) && p.EndB.EndsWith(tag)));
                if (n != 1) return $"device {m.Id} ({m.Kind}) at ({m.X0},{m.Z0}) hooked to {h} has {n} cord ends";
            }
            return null;
        }, "every device on a net has exactly one cord reaching it (no missing lead, no phantom second cable)");
    }

    static string Name(MachineKind k) => k == MachineKind.Source ? "source" : k == MachineKind.Battery ? "battery" : k == MachineKind.Consumer ? "consumer" : k == MachineKind.Lamp ? "lamp" : "transmitter";

    static double Chord(List<V2> p) => V2.Dist(p[0], p[p.Count - 1]);

    static void CordSlackRatio()
    {
        double worst = double.MaxValue; string worstAt = "";
        Prop("L1_CORD_SLACK_RATIO", new[] { "cords_lie_slack", "cord_slack_lay" }, 50, 3000, 7, 16, false, (sc, ps) =>
        {
            foreach (var p in ps)
            {
                if (p.EndA == null || p.EndB == null) continue;
                foreach (var s in p.Strands.Where(HasPts))
                {
                    if (s.OverFace || s.DiveA || s.DiveB) continue;
                    double ch = Chord(s.Pts); if (ch < 2) continue;
                    double ratio = Geo.Length(s.Pts) / ch;
                    if (ratio < worst) { worst = ratio; worstAt = $"{sc.Desc} {p.EndA}->{p.EndB} chord {ch:0.##}"; }
                    if (ratio < 1.4) return $"cord {p.EndA}->{p.EndB} drawn {Geo.Length(s.Pts):0.##} over chord {ch:0.##} = {ratio:0.###} < 1.4";
                }
            }
            return null;
        }, "every end-to-end cord with a chord of 2+ cells is drawn at least 1.4x its chord (shipped slack 1.0)");
        Row("L1_CORD_SLACK_RATIO_MIN", new[] { "cords_lie_slack" }, "info", "INFO", 1, $"lowest drawn/chord seen {worst:0.###} at {worstAt}");
    }

    static void CordExcursion()
    {
        int edges = 0, without = 0; string ex = "";
        Prop("L1_CORD_EXCURSION", new[] { "cords_lie_slack", "cord_slack_lay" }, 40, 4000, 5, 18, false, (sc, ps) =>
        {
            foreach (var p in ps)
            {
                if (p.EndA == null || p.EndB == null || p.Strands.Count == 0 || !HasPts(p.Strands[0])) continue;
                var s = p.Strands[0];
                var chain = System.Text.RegularExpressions.Regex.Matches(p.Key, @"[cw]:\((-?\d+),(-?\d+)\)").Select(m => new V2(int.Parse(m.Groups[1].Value) + 0.5, int.Parse(m.Groups[2].Value) + 0.5)).ToList();
                if (chain.Count < 6) continue; // more than four cells of conduit
                double far = 0;
                foreach (var q in s.Pts) { double d = DistToPolyline(q, chain); if (d > far) far = d; }
                edges++;
                if (far < 1.0) { without++; if (ex == "") ex = $"{sc.Desc} {p.EndA}->{p.EndB} farthest {far:0.##}"; return $"cord {p.EndA}->{p.EndB} ({chain.Count} conduit cells) never strays a cell off its conduit line (farthest {far:0.##})"; }
            }
            return null;
        }, "every cord whose conduit edge runs more than four cells makes at least one excursion of a cell or more off that edge's conduit line (distance to the polyline through its chain's cell centres)");
    }

    static double DistToPolyline(V2 q, List<V2> l)
    {
        double best = double.MaxValue;
        if (l.Count == 1) return V2.Dist(q, l[0]);
        for (int i = 1; i < l.Count; i++)
        {
            V2 a = l[i - 1], b = l[i], ab = b - a; double L2 = ab.X * ab.X + ab.Z * ab.Z;
            double t = L2 < 1e-12 ? 0 : Math.Max(0, Math.Min(1, ((q.X - a.X) * ab.X + (q.Z - a.Z) * ab.Z) / L2));
            best = Math.Min(best, V2.Dist(q, a + ab * t));
        }
        return best;
    }

    static void CordWallFace()
    {
        Prop("L1_CORD_WALL_FACE", new[] { "cords_meet_walls_at_face", "cord_slack_lay" }, 60, 5000, 8, 16, true, (sc, ps) =>
        {
            foreach (var p in ps)
                foreach (var s in p.Strands.Where(HasPts))
                {
                    if (s.OverFace) continue; // a hanging wall-terminal tail is drawn over the face (exempt by its own flag)
                    for (int i = 0; i < s.Pts.Count; i++)
                    {
                        var q = s.Pts[i]; var c = q.Floor; var k = sc.W.BlockAt(c);
                        if (k != BlockKind.Wall && k != BlockKind.Rock) continue;
                        // allowed: the stub into the wall face (within a quarter cell of a walkable neighbour)
                        double inside = DepthInto(sc.W, q);
                        if (inside > 0.3) return $"cord {p.EndA}->{p.EndB} point {i}/{s.Pts.Count} at {q} lies {inside:0.##} deep in a {k} cell (lay {s.Lay}, diveA {s.DiveA} diveB {s.DiveB})";
                    }
                }
            return null;
        }, "no cord point lies more than 0.3 cell inside a wall or rock cell (cords end at the face; only the face stub enters)");
    }

    static double DepthInto(CordWorld w, V2 q)
    {
        // distance from q to the nearest walkable (or device) cell's area
        double best = 9;
        var c = q.Floor;
        for (int dx = -2; dx <= 2; dx++) for (int dz = -2; dz <= 2; dz++)
            {
                var n = new Cell(c.X + dx, c.Z + dz); if (!w.InBounds(n)) continue;
                var k = w.BlockAt(n); if (k == BlockKind.Wall || k == BlockKind.Rock) continue;
                double cx = Math.Max(n.X, Math.Min(q.X, n.X + 1)), cz = Math.Max(n.Z, Math.Min(q.Z, n.Z + 1));
                best = Math.Min(best, Math.Sqrt((q.X - cx) * (q.X - cx) + (q.Z - cz) * (q.Z - cz)));
            }
        return best;
    }

    static void CordSharpTurn()
    {
        int windows = 0, unforced = 0; string first = null;
        Prop("L1_CORD_SHARP_TURN", new[] { "no_unforced_sharp_turn" }, 40, 6000, 6, 14, false, (sc, ps) =>
        {
            foreach (var p in ps)
                foreach (var s in p.Strands.Where(HasPts))
                {
                    var r = Geo.Resample(s.Pts, 0.05); if (r.Count < 25) continue;
                    double[] cum = Geo.CumLen(r);
                    // heading change within any 1-cell arc
                    for (int i = 1; i + 1 < r.Count; i++)
                    {
                        int j = i; double turn = 0;
                        while (j + 1 < r.Count && cum[j] - cum[i] < 1.0)
                        {
                            var u = (r[j] - r[j - 1]).Norm(); var v = (r[j + 1] - r[j]).Norm();
                            turn += Math.Atan2(u.X * v.Z - u.Z * v.X, u.X * v.X + u.Z * v.Z); j++;
                        }
                        if (Math.Abs(turn) <= Math.PI / 2 + 0.05) continue;
                        windows++;
                        if (BroadLoop(r, i, j, turn)) { i = j; continue; }
                        var at = r[(i + j) / 2];
                        // forced: a wall, building or device next to the bend, or the end's own socket (within half a cell of a tip)
                        bool forced = Near(sc.W, at, 1.0) || V2.Dist(at, r[0]) < 0.75 || V2.Dist(at, r[r.Count - 1]) < 0.75
                                      || (s.Ties != null && s.Ties.Count > 0) || (s.Lifted);
                        if (!forced) { unforced++; return $"cord {p.EndA}->{p.EndB} turns {Math.Abs(turn) * 180 / Math.PI:0} deg within one cell at {at} on open floor (lay {s.Lay})"; }
                        i = j;
                    }
                }
            return null;
        }, "no cord turns more than 90 degrees within one cell of arc on open floor (forced: within a cell of a wall/device, within 0.75 of its tip, a tied strain-relief loop; a broad loop of 300+ degrees at radius 0.45+ is a loop, not a bend)");
    }

    // from the window, walk both ways while the heading keeps turning the same way; 300+ degrees at a radius of 0.45 cell or
    // wider (no more than 1/0.45 rad per cell inside the window) is a loop of the cord, not a kink
    static bool BroadLoop(List<V2> r, int i, int j, double turn)
    {
        double arc = 0.05 * (j - i); if (arc <= 0 || Math.Abs(turn) / arc > 1 / 0.45 + 1e-9) return false;
        int sgn = Math.Sign(turn); double tot = 0;
        double T(int k) { var u = (r[k] - r[k - 1]).Norm(); var v = (r[k + 1] - r[k]).Norm(); return Math.Atan2(u.X * v.Z - u.Z * v.X, u.X * v.X + u.Z * v.Z); }
        int lo = i, hi = j - 1, flat = 0;
        for (int k = i; k < j && k + 1 < r.Count; k++) tot += T(k);
        for (int k = lo - 1; k >= 1; k--) { double d = T(k); if (Math.Sign(d) == -sgn && Math.Abs(d) > 1e-4) { if (++flat > 3) break; } else flat = 0; tot += d; }
        flat = 0;
        for (int k = hi + 1; k + 1 < r.Count; k++) { double d = T(k); if (Math.Sign(d) == -sgn && Math.Abs(d) > 1e-4) { if (++flat > 3) break; } else flat = 0; tot += d; }
        return Math.Abs(tot) >= 300 * Math.PI / 180;
    }

    // the bar's own instrument (oracle: "the bridge bends probe (CordShapeAudit.Bends) ... tally unforced == 0"), run offline over my scenes
    static void CordBendsTally()
    {
        int cases = 0; var tally = new CordShapeAudit.BendTally(); string firstAt = null;
        foreach (bool walls in new[] { false, true })
            for (int t = 0; t < 40; t++)
            {
                var sc = MakeScene(6000 + t + (walls ? 500 : 0), 6, 14, walls); int before = tally.Unforced;
                foreach (var p in Build(sc.W)) foreach (var s in p.Strands) tally.Add(sc.W, p, s);
                cases++;
                if (tally.Unforced > before && firstAt == null) firstAt = sc.Desc;
            }
        string json = tally.Json(); int cut = json.IndexOf(",\"rows\"");
        Row("L1_CORD_BENDS_TALLY", new[] { "no_unforced_sharp_turn" }, "random", tally.Unforced == 0 ? "PASS" : "FAIL", cases,
            $"the bar's named instrument CordShapeAudit.BendTally over 80 random scenes (seeds 6000..6039 open, 6500..6539 with walls): {tally.Strands} strands, {tally.Bends} bends, unforced {tally.Unforced}" + (firstAt != null ? $", first unforced in {firstAt}" : "") + "; " + (cut > 0 ? json.Substring(0, cut) : json) + "; first rows " + (cut > 0 ? json.Substring(cut, Math.Min(600, json.Length - cut)) : ""));
    }

    // how often the slack and excursion oracles miss over the whole random set (not stopping at the first), by lay
    static void CordRates()
    {
        int n = 0, under = 0; var why = new Dictionary<string, int>(); double worst = 9;
        for (int t = 0; t < 50; t++)
        {
            var sc = MakeScene(3000 + t, 7, 16, false);
            foreach (var p in Build(sc.W)) foreach (var s in p.Strands.Where(HasPts))
                {
                    if (p.EndA == null || p.EndB == null || s.OverFace || s.DiveA || s.DiveB) continue;
                    double ch = Chord(s.Pts); if (ch < 2) continue; n++;
                    double r = Geo.Length(s.Pts) / ch; worst = Math.Min(worst, r);
                    if (r < 1.4) { under++; string k = s.Lay + (s.WhipA > 0 || s.WhipB > 0 ? "+whip" : ""); why[k] = why.GetValueOrDefault(k) + 1; }
                }
        }
        Row("L1_CORD_SLACK_RATE", new[] { "cords_lie_slack" }, "info", "INFO", n, $"seeds 3000..3049: {under} of {n} strands under 1.4x their chord (worst {worst:0.###}), by lay: " + string.Join(", ", why.Select(kv => kv.Key + " " + kv.Value)));
        int e = 0, miss = 0; var mw = new Dictionary<string, int>(); double low = 9;
        for (int t = 0; t < 40; t++)
        {
            var sc = MakeScene(4000 + t, 5, 18, false);
            foreach (var p in Build(sc.W))
            {
                if (p.EndA == null || p.EndB == null || p.Strands.Count == 0 || !HasPts(p.Strands[0])) continue;
                var chain = System.Text.RegularExpressions.Regex.Matches(p.Key, @"[cw]:\((-?\d+),(-?\d+)\)").Select(m => new V2(int.Parse(m.Groups[1].Value) + 0.5, int.Parse(m.Groups[2].Value) + 0.5)).ToList();
                if (chain.Count < 6) continue; e++;
                double f = p.Strands[0].Pts.Max(q => DistToPolyline(q, chain)); low = Math.Min(low, f);
                if (f < 1.0) { miss++; mw[p.Strands[0].Lay] = mw.GetValueOrDefault(p.Strands[0].Lay) + 1; }
            }
        }
        Row("L1_CORD_EXCURSION_RATE", new[] { "cords_lie_slack" }, "info", "INFO", e, $"seeds 4000..4039: {miss} of {e} edges over four cells never leave their conduit line by a cell (lowest farthest {low:0.##}), by lay: " + string.Join(", ", mw.Select(kv => kv.Key + " " + kv.Value)));
    }

    static bool Near(CordWorld w, V2 q, double r)
    {
        var c = q.Floor; int k = (int)Math.Ceiling(r);
        for (int dx = -k; dx <= k; dx++) for (int dz = -k; dz <= k; dz++)
            {
                var n = new Cell(c.X + dx, c.Z + dz);
                if (!w.InBounds(n)) return true;
                if (w.BlockAt(n) == BlockKind.None) continue;
                double cx = Math.Max(n.X, Math.Min(q.X, n.X + 1)), cz = Math.Max(n.Z, Math.Min(q.Z, n.Z + 1));
                if (Math.Sqrt((q.X - cx) * (q.X - cx) + (q.Z - cz) * (q.Z - cz)) <= r) return true;
            }
        return false;
    }

    // ===================================================================== cuts (cut_live_and_dead_ends)
    static (CordWorld w, MachineInfo s, MachineInfo c) Line(int len, bool farBattery)
    {
        var w = new CordWorld(len + 12, 16); int z = 8;
        for (int x = 4; x < 4 + len; x++) w.SetConduit(new Cell(x, z));
        var src = new MachineInfo { Id = "gen", DefName = "Gen", Kind = MachineKind.Source, X0 = 3, Z0 = z }; src.Hookups.Add(new Cell(4, z));
        var far = new MachineInfo { Id = "far", DefName = farBattery ? "Battery" : "Lamp", Kind = farBattery ? MachineKind.Battery : MachineKind.Consumer, X0 = 4 + len, Z0 = z };
        far.Hookups.Add(new Cell(3 + len, z));
        w.Machines.Add(src); w.Machines.Add(far); w.SetBlocked(new Cell(3, z), BlockKind.Device); w.SetBlocked(new Cell(4 + len, z), BlockKind.Device);
        return (w, src, far);
    }

    static string CheckCut(CordWorld w, int gapX, int z, Func<Cell, bool> live, out int ends)
    {
        var ps = Build(w, null, live); ends = 0;
        var comp = Components(w);
        foreach (var p in ps)
        {
            Cell? a = ParseEndCell(p.EndA), b = ParseEndCell(p.EndB);
            if (a != null && b != null && CompOf(w, comp, a.Value) != CompOf(w, comp, b.Value)) return $"a cord {p.EndA}->{p.EndB} still spans the gap at x={gapX}";
        }
        var all = ps.SelectMany(p => p.Ends.Select(e => (p, e))).ToList();
        foreach (int side in new[] { gapX - 1, gapX + 1 })
        {
            var mine = all.Where(t => t.e.NetCell == new Cell(side, z)).ToList();
            if (mine.Count != 1) return $"cell ({side},{z}) beside the gap has {mine.Count} loose ends (want 1)";
            ends++;
            var (p, e) = mine[0];
            bool isLive = live(e.NetCell);
            var fr = p.Decals.Where(d => (d.Kind == DecalKind.FrayLive || d.Kind == DecalKind.FrayDead) && V2.Dist(d.Pos, e.Tip) < 0.6).ToList();
            if (fr.Count == 0) return $"end at ({side},{z}) has no fray drawn at its tip";
            if (fr.Any(d => d.Kind == (isLive ? DecalKind.FrayDead : DecalKind.FrayLive))) return $"end at ({side},{z}) live={isLive} drawn {string.Join(",", fr.Select(d => d.Kind))}";
        }
        return null;
    }

    static void CutEndsLiveDead()
    {
        int cases = 0; string fail = null;
        for (int len = 5; len <= 24 && fail == null; len++)
            for (int gx = 5; gx < 3 + len - 1 && fail == null; gx++)
            {
                var (w, s, c) = Line(len, false); w.SetConduit(new Cell(gx, 8), false);
                var comp = Components(w); int srcComp = comp[new Cell(4, 8)];
                // live = has a path to a power source (the generator's side); the far side holds only a consumer
                Func<Cell, bool> live = q => comp.TryGetValue(q, out int k) && k == srcComp;
                fail = CheckCut(w, gx, 8, live, out _); cases++;
                if (fail != null) fail = $"line length {len}, cut at x={gx} (smallest failing in scan order): " + fail;
            }
        Row("L1_CUT_ENDS_LIVE_DEAD", new[] { "cut_live_and_dead_ends", "break_ends_live_dead" }, "sweep", fail == null ? "PASS" : "FAIL", cases,
            fail ?? "every line 5..24 cells, every inner cut: no cord across the gap, exactly one loose end on each side, the fed end drawn live and the far end dead");
    }

    static void CutFarSource()
    {
        int cases = 0; string fail = null;
        for (int len = 5; len <= 20 && fail == null; len++)
            for (int gx = 5; gx < 3 + len - 1 && fail == null; gx++)
            {
                var (w, s, c) = Line(len, true); w.SetConduit(new Cell(gx, 8), false);
                // both sides have a source (the far side a charged battery): both ends live; then the battery runs flat: the far end dead
                fail = CheckCut(w, gx, 8, q => true, out _); cases++;
                if (fail == null) { var comp = Components(w); int k0 = comp[new Cell(4, 8)]; fail = CheckCut(w, gx, 8, q => comp.TryGetValue(q, out int k) && k == k0, out _); cases++; }
                if (fail != null) fail = $"line length {len}, cut at x={gx}: " + fail;
            }
        Row("L1_CUT_FAR_SOURCE", new[] { "cut_live_and_dead_ends", "break_ends_live_dead" }, "sweep", fail == null ? "PASS" : "FAIL", cases,
            fail ?? "a far-side battery: both ends drawn live; the battery flat: only the generator's end live (the drawing follows the live flag it is given)");
    }

    // ===================================================================== junctions and piles (strip_at_every_junction, dense_block_tangle)
    static void JunctionPiece()
    {
        int cases = 0; var bad = new List<string>(); int junctions = 0;
        foreach (PileArt art in new[] { PileArt.Strips, PileArt.Junctions })
            for (int seed = 0; seed < 40; seed++)
            {
                var rng = new Random(7000 + seed); var w = new CordWorld(40, 40); var ms = new List<MachineInfo>();
                // a plus or a T at the centre, arms 3..8, a device at each arm end
                int cx = 20, cz = 20; bool four = rng.Next(2) == 0; var arms = four ? Cell.Dirs4 : Cell.Dirs4.Take(3).ToArray();
                w.SetConduit(new Cell(cx, cz)); int mid = 0;
                foreach (var d in arms)
                {
                    int L = rng.Next(3, 9); Cell c = new Cell(cx, cz);
                    for (int i = 0; i < L; i++) { c = c + d; w.SetConduit(c); }
                    var m = c + d; var mi = new MachineInfo { Id = "d" + mid++, DefName = "D", Kind = mid == 1 ? MachineKind.Source : MachineKind.Consumer, X0 = m.X, Z0 = m.Z };
                    mi.Hookups.Add(c); w.Machines.Add(mi); w.SetBlocked(m, BlockKind.Device);
                }
                var ps = Build(w, new BuildOptions { Pile = art, Seed = (ulong)(seed + 1) });
                var b = new CordBuilder(); b.Build(w, new BuildOptions { Pile = art, Seed = (ulong)(seed + 1) }, q => true);
                foreach (var n in b.Graph.Nodes.Values.Where(n => n.Type == NodeType.Junction))
                {
                    junctions++; cases++;
                    var near = ps.SelectMany(p => p.Decals).Where(d => V2.Dist(d.Pos, n.Pos) < 1.6).Select(d => d.Kind).ToList();
                    bool strip = near.Contains(DecalKind.PowerStrip) || near.Contains(DecalKind.PowerStripDark);
                    bool box = near.Contains(DecalKind.JunctionTape) || near.Contains(DecalKind.JunctionTin);
                    if (art == PileArt.Strips && (!strip || box)) bad.Add($"seed {7000 + seed} {(four ? "4" : "3")}-way Modern: near {string.Join(",", near.Distinct())}");
                    if (art == PileArt.Junctions && !box) bad.Add($"seed {7000 + seed} {(four ? "4" : "3")}-way box: near {string.Join(",", near.Distinct())}");
                    // every cord at the junction plugs in: the pieces meeting there end within reach of the piece
                }
            }
        Row("L1_JUNCTION_PIECE", new[] { "strip_at_every_junction", "junction_strips" }, "random", bad.Count == 0 ? "PASS" : "FAIL", cases,
            $"seeds 7000..7039, plus and T junctions, both pile arts: {junctions} junction nodes; Modern (Strips) draws a power strip and no box, the other looks a junction box; " + string.Join("; ", bad.Take(4)));
    }

    static void DenseTangle()
    {
        int cases = 0; var bad = new List<string>(); var info = new List<string>();
        foreach (PileArt art in new[] { PileArt.Strips, PileArt.Junctions })
            foreach (int tmin in new[] { 6, 9, 20 })
            {
                var w = new CordWorld(30, 30);
                for (int x = 10; x < 16; x++) for (int z = 10; z < 16; z++) w.SetConduit(new Cell(x, z));
                var src = new MachineInfo { Id = "g", DefName = "G", Kind = MachineKind.Source, X0 = 9, Z0 = 12 }; src.Hookups.Add(new Cell(10, 12)); w.Machines.Add(src); w.SetBlocked(new Cell(9, 12), BlockKind.Device);
                var b = new CordBuilder(); var ps = b.Build(w, new BuildOptions { Pile = art, TangleMin = tmin }, q => true); cases++;
                bool tangle = b.Graph.Nodes.Values.Any(n => n.Type == NodeType.Tangle || n.IsBlob);
                var kinds = ps.SelectMany(p => p.Decals).Select(d => d.Kind).ToList();
                int strands = ps.Sum(p => p.Strands.Count);
                bool pieces = art == PileArt.Strips ? kinds.Any(k => k == DecalKind.PowerStrip || k == DecalKind.PowerStripDark) : kinds.Any(k => k == DecalKind.JunctionTape || k == DecalKind.JunctionTin);
                info.Add($"{art}/tangleMin {tmin}: tangle {tangle} strands {strands} pile pieces {pieces}");
                if (!tangle || !pieces || strands < 6) bad.Add($"{art} tangleMin {tmin}: 36-cell block tangle {tangle}, pile pieces {pieces}, strands {strands}");
            }
        Row("L1_DENSE_TANGLE", new[] { "dense_block_tangle" }, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "a 6x6 conduit block reads as one heap: a tangle node, its look's pile pieces and many strands, tangleMin swept 6/9/20 (slider); " + string.Join("; ", bad.Count > 0 ? bad : info));
    }

    // ===================================================================== no repeat (cords_never_repeat, cord_shape_variation_probe)
    static double[] Frame(List<V2> pts, int n = 40)
    {
        var r = Geo.Resample(pts, Geo.Length(pts) / (n - 1)); while (r.Count < n) r.Add(r[r.Count - 1]);
        V2 a = r[0], b = r[r.Count - 1], ax = (b - a).Norm(), pe = ax.Perp; var o = new double[2 * n];
        for (int i = 0; i < n; i++) { var d = r[Math.Min(i, r.Count - 1)] - a; o[2 * i] = d.X * ax.X + d.Z * ax.Z; o[2 * i + 1] = d.X * pe.X + d.Z * pe.Z; }
        return o;
    }
    static double Gap(double[] a, double[] b)
    {
        int n = a.Length / 2; double best = double.MaxValue;
        foreach (bool rev in new[] { false, true }) foreach (int mir in new[] { 1, -1 })
            {
                double s = 0;
                for (int i = 0; i < n; i++) { int j = rev ? n - 1 - i : i; double bx = rev ? b[2 * (n - 1)] - b[2 * j] : b[2 * j]; double bz = mir * (rev ? b[2 * j + 1] - b[2 * (n - 1) + 1] : b[2 * j + 1]); s += Math.Sqrt((a[2 * i] - bx) * (a[2 * i] - bx) + (a[2 * i + 1] - bz) * (a[2 * i + 1] - bz)); }
                best = Math.Min(best, s / n);
            }
        return best;
    }

    static void NoRepeat()
    {
        int cases = 0; var bad = new List<string>(); double globalMin = double.MaxValue; int tooAlike = 0, pairs = 0;
        foreach (int L in new[] { 4, 6, 9, 12 })
            for (int seed = 1; seed <= 6; seed++)
            {
                // eight equal runs side by side, three cells apart, each generator -> lamp: one room of same-length cords
                var w = new CordWorld(L + 12, 40); var ms = new List<MachineInfo>();
                for (int r = 0; r < 8; r++)
                {
                    int z = 4 + r * 4;
                    for (int x = 5; x < 5 + L; x++) w.SetConduit(new Cell(x, z));
                    var g = new MachineInfo { Id = "g" + r, DefName = "G", Kind = MachineKind.Source, X0 = 4, Z0 = z }; g.Hookups.Add(new Cell(5, z));
                    var l = new MachineInfo { Id = "l" + r, DefName = "L", Kind = MachineKind.Consumer, X0 = 5 + L, Z0 = z }; l.Hookups.Add(new Cell(4 + L, z));
                    w.Machines.Add(g); w.Machines.Add(l); w.SetBlocked(new Cell(4, z), BlockKind.Device); w.SetBlocked(new Cell(5 + L, z), BlockKind.Device);
                }
                var ps = Build(w, new BuildOptions { Seed = (ulong)seed }).Where(p => p.EndA != null && p.Strands.Count > 0 && HasPts(p.Strands[0])).ToList();
                var fr = ps.Select(p => Frame(p.Strands[0].Pts)).ToList();
                for (int i = 0; i < fr.Count; i++) for (int j = i + 1; j < fr.Count; j++)
                    {
                        double g = Gap(fr[i], fr[j]); cases++; globalMin = Math.Min(globalMin, g);
                        if (g < 0.1) bad.Add($"run length {L} seed {seed}: cords {ps[i].EndA} and {ps[j].EndA} mean gap {g:0.###} cells");
                    }
                foreach (var t in CordShape.Table(ps)) { tooAlike += t.TooAlike; pairs += t.Pairs; }
            }
        string shr = "none";
        for (int runs = 2; runs <= 8 && shr == "none"; runs++)
            for (int seed = 1; seed <= 6 && shr == "none"; seed++)
            {
                var w = new CordWorld(16, 40); int L = 4;
                for (int r = 0; r < runs; r++)
                {
                    int z = 4 + r * 4;
                    for (int x = 5; x < 5 + L; x++) w.SetConduit(new Cell(x, z));
                    var g = new MachineInfo { Id = "g" + r, DefName = "G", Kind = MachineKind.Source, X0 = 4, Z0 = z }; g.Hookups.Add(new Cell(5, z));
                    var l = new MachineInfo { Id = "l" + r, DefName = "L", Kind = MachineKind.Consumer, X0 = 5 + L, Z0 = z }; l.Hookups.Add(new Cell(4 + L, z));
                    w.Machines.Add(g); w.Machines.Add(l); w.SetBlocked(new Cell(4, z), BlockKind.Device); w.SetBlocked(new Cell(5 + L, z), BlockKind.Device);
                }
                var ps = Build(w, new BuildOptions { Seed = (ulong)seed }).Where(p => p.EndA != null && p.Strands.Count > 0 && HasPts(p.Strands[0])).ToList();
                for (int i = 0; i < ps.Count && shr == "none"; i++) for (int j = i + 1; j < ps.Count; j++)
                    { double g2 = Gap(Frame(ps[i].Strands[0].Pts), Frame(ps[j].Strands[0].Pts)); if (g2 < 0.1) { shr = $"{runs} runs of 4 cells, 4 apart, build seed {seed}: {ps[i].EndA} and {ps[j].EndA} gap {g2:0.###}"; break; } }
            }
        bad.Insert(0, "SHRUNK: " + shr);
        Row("L1_NO_REPEAT", new[] { "cords_never_repeat", "cord_shape_variation_probe" }, "random", bad.Count == 0 ? "PASS" : "FAIL", cases,
            $"eight equal runs side by side, lengths 4/6/9/12, seeds 1..6: smallest mean point gap between two cords in their own frames (either way, mirrored) {globalMin:0.###} cells (fail under 0.1); the kernel's own table calls {tooAlike} of {pairs} pairs too alike (under 0.3); " + string.Join("; ", bad.Take(4)));
        Row("L1_NO_REPEAT_KERNEL_TABLE", new[] { "cord_shape_variation_probe" }, "info", "INFO", pairs, $"CordShape.Table on the same rooms: {tooAlike} of {pairs} pairs under TooAlikeBelow 0.3; my independent gap min {globalMin:0.###}");
    }

    // ===================================================================== rebuild (no_stall_on_rewire: the cheap path must stay correct)
    static List<string> Sig(List<LaidPiece> ps) => ps.Select(p => p.Key + "#" + p.GeometryHash() + "#" + string.Join(",", p.Decals.Select(d => d.Kind + "@" + Math.Round(d.Pos.X, 3) + "," + Math.Round(d.Pos.Z, 3)))).OrderBy(x => x, StringComparer.Ordinal).ToList();

    static void BuildDeterministic()
    {
        int cases = 0; string fail = null;
        for (int s = 0; s < 30 && fail == null; s++)
        {
            var sc = MakeScene(8000 + s, 6, 12, true);
            var a = Sig(Build(sc.W)); var b = Sig(Build(MakeScene(8000 + s, 6, 12, true).W)); cases++;
            if (!a.SequenceEqual(b)) fail = $"seed {8000 + s}: two fresh builders drew different cords";
            var bb = new CordBuilder(); Build(sc.W, null, null, bb); var c = Sig(Build(sc.W, null, null, bb));
            if (fail == null && !a.SequenceEqual(c)) fail = $"seed {8000 + s}: a second Build on the same builder (all reused) drew different cords";
        }
        Row("L1_BUILD_DETERMINISTIC", new[] { "no_stall_on_rewire", "cords_never_repeat" }, "random", fail == null ? "PASS" : "FAIL", cases,
            fail ?? "seeds 8000..8029: a fresh build and a cached rebuild draw the same cords, decal for decal (same map, same drawing)");
    }

    static void CacheCurrent()
    {
        int cases = 0; string fail = null; var rng = new Random(4040);
        for (int s = 0; s < 40 && fail == null; s++)
        {
            var sc = MakeScene(9000 + s, 6, 12, s % 2 == 0); var b = new CordBuilder(); Build(sc.W, null, null, b);
            for (int step = 0; step < 4 && fail == null; step++)
            {
                // place, cut or dig: toggle a conduit cell, or wall/unwall an empty cell near the cords
                var cells = sc.W.ConduitCells().ToList(); string what;
                if (rng.Next(3) == 0 && cells.Count > 0) { var c = cells[rng.Next(cells.Count)]; sc.W.SetConduit(c, false); what = "cut " + c; }
                else if (rng.Next(2) == 0 && cells.Count > 0) { var c = cells[rng.Next(cells.Count)] + Cell.Dirs4[rng.Next(4)]; if (sc.W.IsWalkable(c)) sc.W.SetConduit(c); what = "lay " + c; }
                else { var c = new Cell(rng.Next(2, 46), rng.Next(2, 46)); if (!sc.W.IsConduit(c) && sc.W.BlockAt(c) != BlockKind.Device) sc.W.SetBlocked(c, sc.W.IsWalkable(c) ? BlockKind.Wall : BlockKind.None); what = "wall toggle " + c; }
                var got = Sig(Build(sc.W, null, null, b)); var want = Sig(Build(sc.W.Clone())); cases++;
                if (!got.SequenceEqual(want)) fail = $"seed {9000 + s} step {step} ({what}): the cached rebuild drew {got.Count} pieces, a fresh build {want.Count}; first differing: {got.Except(want).FirstOrDefault()?.Substring(0, 80)}";
            }
        }
        Row("L1_CACHE_CURRENT_AFTER_CHANGE", new[] { "no_stall_on_rewire", "drawing_true_to_grid" }, "random", fail == null ? "PASS" : "FAIL", cases,
            fail ?? "seeds 9000..9039, four random place/cut/wall steps each: after every change the cached rebuild equals a fresh build (no stale drawing behind the cheap path)");
    }

    static void ReachSound()
    {
        int cases = 0, tried = 0; string fail = null; var rng = new Random(5150);
        for (int s = 0; s < 30 && fail == null; s++)
        {
            var sc = MakeScene(9500 + s, 4, 10, false); var b = new CordBuilder(); var before = Sig(Build(sc.W, null, null, b));
            var reach = b.Reach;
            for (int k = 0; k < 40 && fail == null; k++)
            {
                var c = new Cell(rng.Next(0, 48), rng.Next(0, 48)); cases++;
                if (reach.Reaches(c) || sc.W.IsConduit(c) || sc.W.BlockAt(c) != BlockKind.None) continue;
                tried++;
                var w2 = sc.W.Clone(); w2.SetBlocked(c, BlockKind.Wall);
                var after = Sig(Build(w2));
                if (!after.SequenceEqual(before)) fail = $"seed {9500 + s}: a wall at {c}, outside the build's reach ({reach.HotBlocks} hot blocks), changed the drawing";
            }
        }
        Row("L1_REACH_SOUND", new[] { "no_stall_on_rewire" }, "random", fail == null ? "PASS" : "FAIL", cases,
            fail ?? $"seed 5150, scenes 9500..9529: {tried} walls dug or built outside CordReach changed nothing a fresh build draws (a skipped rebuild there is sound)");
    }

    static void RebuildGateCheck()
    {
        var bad = new List<string>(); int cases = 0;
        var reach = new CordReach(64, 64); reach.Add(10, 10, 12, 12);
        ulong benign = 0b0110; Func<ulong, string> names = f => f.ToString();
        // benign layer, far, unpowered -> skip; inside reach -> relevant; powered cell -> relevant; other layer -> relevant; no reach -> relevant
        void Want(bool w, bool own, ulong flags, CordReach r, Cell c, bool powered) { cases++; if (RebuildGate.IsBenign(own, flags, benign, r, c, _ => powered) != w) bad.Add($"own {own} flags {flags} cell {c} powered {powered}"); }
        Want(true, false, 0b0010, reach, new Cell(50, 50), false);
        Want(false, false, 0b0010, reach, new Cell(11, 11), false);
        Want(false, false, 0b0010, reach, new Cell(50, 50), true);
        Want(false, false, 0b1000, reach, new Cell(50, 50), false);
        Want(false, false, 0b0010, null, new Cell(50, 50), false);
        Want(true, true, 0b1000, reach, new Cell(11, 11), true);
        var all = new CordReach(64, 64); all.AddAll(); Want(false, false, 0b0010, all, new Cell(50, 50), false);
        Want(false, false, 0b0010, reach, new Cell(-1, 3), false);
        // the gate: a relevant event after a build forces the next regenerate to build; only benign events let the pieces stand
        var g = new RebuildGate(); g.Published(0); cases++;
        g.Note(false, 0b0010, benign, reach, new Cell(50, 50), _ => false, names);
        if (g.RegenerateNeedsBuild()) bad.Add("benign-only regenerate rebuilt");
        g.Note(false, 0b1000, benign, reach, new Cell(50, 50), _ => false, names);
        if (!g.RegenerateNeedsBuild()) bad.Add("relevant event did not rebuild");
        g.Published(3); if (!g.RegenerateNeedsBuild()) bad.Add("pending edges left the drawing standing");
        cases += 3;
        Row("L1_REBUILD_GATE", new[] { "no_stall_on_rewire" }, "fixed", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "a far benign event skips the rebuild; inside the reach, on a powered cell, another layer, no reach, a whole-map reach or off-map rebuilds; pending edges keep it stale; " + string.Join("; ", bad));
    }

    static void SliceWindowMax()
    {
        var rng = new Random(606); int cases = 0; string fail = null;
        for (int t = 0; t < 2000 && fail == null; t++)
        {
            var w = new SliceWindow(); w.Reset(0); double max = -1, maxNo = -1; int gc = 0, n = rng.Next(1, 60);
            for (int i = 0; i < n; i++) { var r = new SliceRecord { TotalMs = rng.NextDouble() * 100, Gc0 = rng.Next(4) == 0 ? 1 : 0 }; w.Record(r, i * 1000, 1000000); max = Math.Max(max, r.TotalMs); if (r.Gc0 > 0) gc++; else maxNo = Math.Max(maxNo, r.TotalMs); }
            cases++;
            if (w.Slices != n || w.Max.TotalMs != max || w.GcHits != gc || (maxNo >= 0 ? w.MaxNoGc == null || w.MaxNoGc.TotalMs != maxNo : w.MaxNoGc != null) || w.First.Ordinal != 1)
                fail = $"trial {t}: window max {w.Max?.TotalMs} want {max}, noGc {w.MaxNoGc?.TotalMs} want {maxNo}, slices {w.Slices}/{n}";
        }
        Row("L1_SLICE_WINDOW_MAX", new[] { "no_stall_on_rewire" }, "random", fail == null ? "PASS" : "FAIL", cases,
            fail ?? "seed 606: the 20 ms bar's instrument keeps the true slowest slice and the slowest one with no collection");
    }

    static void SnapshotPoolCheck()
    {
        var rng = new Random(77); int cases = 0; string fail = null;
        for (int t = 0; t < 300 && fail == null; t++)
        {
            var pool = new SnapshotPool(); var worlds = new List<CordWorld>();
            for (int i = 0; i < 8 && fail == null; i++)
            {
                var src = MakeScene(t * 10 + i, 3, 8, rng.Next(2) == 0, 24).W;
                var got = pool.Take(src, null); cases++;
                if (ReferenceEquals(got, src)) { fail = "pool handed back its own source"; break; }
                for (int x = 0; x < 24 && fail == null; x++) for (int z = 0; z < 24; z++)
                    {
                        var c = new Cell(x, z);
                        if (got.IsConduit(c) != src.IsConduit(c) || got.BlockAt(c) != src.BlockAt(c) || CordSig.CellSig(got, c) != CordSig.CellSig(src, c)) { fail = $"trial {t}: refilled world differs at {c}"; break; }
                    }
                if (fail == null && got.Machines.Count != src.Machines.Count) fail = $"trial {t}: refilled world has {got.Machines.Count} machines, source {src.Machines.Count}";
                worlds.Add(got); if (rng.Next(2) == 0) pool.Retire(worlds[rng.Next(worlds.Count)]);
                if (pool.Count > SnapshotPool.Cap) fail = "pool grew past its cap";
            }
        }
        Row("L1_SNAPSHOT_POOL", new[] { "no_stall_on_rewire" }, "random", fail == null ? "PASS" : "FAIL", cases,
            fail ?? "seed 77: a pooled snapshot reads exactly as its source (conduit, blocks, cell signatures, machines), never the source itself, the pool stays within its cap");
    }

    // ===================================================================== settings sweep (cords half; the aerial sliders are swept above)
    static void SettingsSweepCords()
    {
        int cases = 0; var bad = new List<string>(); var ratios = new List<string>();
        double[] slacks = { 0, 0.45, 0.9, 1.0, 1.35, 1.8 }; double[] budgets = { 2, 8, 16, 40 }; int[] cords = { 1, 2, 3 };
        foreach (double sl in slacks)
        {
            double worst = double.MaxValue;
            foreach (double lb in budgets)
                foreach (int cp in cords)
                    for (int s = 0; s < 2; s++)
                    {
                        var sc = MakeScene(12000 + s, 6, 12, s == 1);
                        var o = new BuildOptions(); o.Lay.SlackScale = sl; o.Lay.MaxExtra = lb; o.Lay.MinExtra = Math.Min(o.Lay.MinExtra, o.Lay.MaxExtra); o.Lay.CordsMax = cp;
                        o.DiveThrough = s == 0; o.SlideUnder = cp != 2; o.Tangles = lb != 8; o.NeedlessLoops = lb != 16;
                        List<LaidPiece> ps; cases++;
                        try { ps = Build(sc.W, o); } catch (Exception e) { bad.Add($"slack {sl} budget {lb} cords {cp} seed {12000 + s}: threw {e.GetType().Name}"); continue; }
                        var comp = Components(sc.W);
                        foreach (var p in ps)
                        {
                            Cell? a = ParseEndCell(p.EndA), b = ParseEndCell(p.EndB);
                            if (a != null && b != null) { var ca = CompOf(sc.W, comp, a.Value); var cb = CompOf(sc.W, comp, b.Value); if (ca != null && cb != null && ca != cb) bad.Add($"slack {sl} budget {lb} cords {cp}: cross-net cord"); }
                            if (p.Strands.Count > cp) bad.Add($"cords per connection {cp}: piece drew {p.Strands.Count} strands");
                            foreach (var st in p.Strands.Where(HasPts)) { if (st.Pts.Any(q => double.IsNaN(q.X) || double.IsNaN(q.Z))) bad.Add("NaN point"); double ch = Chord(st.Pts); if (ch >= 2 && !st.OverFace && !st.DiveA && !st.DiveB && p.EndA != null) worst = Math.Min(worst, Geo.Length(st.Pts) / ch); }
                        }
                    }
            ratios.Add($"slack {sl}: min drawn/chord {worst:0.##}");
        }
        Row("L1_SETTINGS_SWEEP_CORDS", new[] { "settings_switch_cleanly", "mod_settings", "cords_lie_slack", "drawing_true_to_grid" }, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            "slack 0..1.8 x loopBudget 2..40 x cordsPerConnection 1..3, diveThrough, slideUnder, tangles and needlessLoops flipped: every build completes, no NaN, no cross-net cord, strands per lead within the setting; " + string.Join("; ", bad.Distinct().Take(5)));
        Row("L1_SETTINGS_SLACK_RATIO_INFO", new[] { "cords_lie_slack" }, "info", "INFO", slacks.Length, "the bar's 1.4x is a shipped-default promise; per slack value: " + string.Join("; ", ratios));
    }

    static void NotKernel()
    {
        void NK(string id, string bar, string why) => Row(id, new[] { bar }, "not_kernel", "UNSETTLED", 0, why);
        NK("L1_NK_CONDUIT_INVISIBLE", "conduit_invisible", "the conduit def's graphic, the power overlay and HiddenConduit handling live in the game (ConduitVisuals, def patches); ConduitTargets' per-def toggle is covered above");
        NK("L1_NK_SPANS_ALTITUDE", "spans_above_everything", "draw altitude against pawns and buildings is a render-layer fact of the game; the kernel's link refusals and sag are covered above");
        NK("L1_NK_FOUR_LOOKS", "four_looks_one_run", "one style per connected run is ConduitStyles/StylePicker over the game's power nets, not a Core/Aerial kernel; telling looks apart is a judge's eye");
        NK("L1_NK_SETTINGS_PATCH_MAP", "settings_switch_cleanly", "the Harmony patch-to-switch map, master-off vanilla art and no-restart are game-side (Harmony, the def graphic swap); sliders and defaults covered above");
        NK("L1_NK_GRAVSHIP_LANDED", "gravship_keeps_connections", "the landed ship's cords redraw from the game's nets after landing; the kernel's gravship removal plan is covered above");
        NK("L1_NK_OWNER_CHANGE", "owner_change_coils_wires", "the owner sweep runs over live anchors and factions in RM_MapComponent_Aerial (game side); CanLink's Foreign refusal is covered above");
        NK("L1_NK_STATICS", "statics_clear_between_games", "static registries (taps, style picks, printed sections, path cost) and the new-game/load paths are game lifecycle");
        NK("L1_NK_RESTRING_ALERT", "restring_cut_span", "the alert, its jump and the RM_RestringSpan job are game UI and AI; RestringTicks is a formula only");
        NK("L1_NK_FUEL", "live_wire_lights_fuel", "ignition of a filth puddle is a game tick over the map's things");
        NK("L1_NK_LIVE_FLAG", "cut_live_and_dead_ends", "WHICH ends are live (a powered source on the end's PowerNet, cleared within 250 ticks of switch-off) is decided game-side and handed to Build as isLive; the drawing's obedience to that flag is covered above");
        NK("L1_NK_FLOOR_END_CONTACTS", "floor_end_shocks_crossers", "the contact set (which ends are live, a run stopped mid-lay, maxSparkingEnds not gating) and the job-target read are FloorEndShock/RM_FallenWireShock game code; the rule they feed is covered above");
        NK("L1_NK_FLOWWORKS_DECK", "shock_reach_setting", "FlowWorks' dropped bridge-deck cord registering as a DroppedCord line is cross-mod game code; the setting's table for that kind is covered above");
        NK("L1_NK_FRAME_MS", "no_stall_on_rewire", "20 ms a frame on a 2000-cell base is a live measurement on his machine; the cheap path's correctness is covered above");
        NK("L1_NK_WALK", "walk_scavenger_base", "a week of play on the full list");
    }
}
