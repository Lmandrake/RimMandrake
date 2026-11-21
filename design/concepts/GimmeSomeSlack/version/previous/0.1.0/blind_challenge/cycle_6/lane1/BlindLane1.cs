// Blind lane 1, cycle 6 (judge-1794822790): GimmeSomeSlack's Verse-free kernels tested from the bars alone.
// Compiled against the shipped Source/Aerial/AerialMath.cs and Source/Aerial/ShockRule.cs (or a planted copy, --kernel).
// Also reads the shipped DLL's metadata (env GSS_DLL) for the no-hose bars: type, member and user-string heaps.
// One JSON row per line; exit 1 when any decided row FAILs.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection.Metadata;
using System.Reflection.Metadata.Ecma335;
using System.Reflection.PortableExecutable;
using System.Text.Json;
using System.Text.RegularExpressions;
using RimMandrake.GimmeSomeSlack.Aerial;

public static class BlindLane1
{
    static readonly List<string> Rows = new List<string>();
    static bool anyFail;

    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") anyFail = true;
        Rows.Add(JsonSerializer.Serialize(new Dictionary<string, object> {
            ["id"] = id, ["bars"] = bars, ["kind"] = kind, ["verdict"] = verdict, ["cases"] = cases, ["detail"] = detail }));
    }

    static string[] B(params string[] b) => b;

    public static int Main()
    {
        int seed = 1794822790;
        ShockTable();
        ShockJoinAndEnd(seed);
        FallenShock();
        TapOneWayAndConserved(seed);
        TheftLeak(seed);
        TheftSight(seed);
        LinkRules(seed);
        SpanningForest(seed);
        AutoLink(seed);
        KindSwitches();
        RangeSagSweep();
        Restring();
        Removal(seed);
        FallenLies(seed);
        DllScan();
        foreach (string r in Rows) Console.WriteLine(r);
        return anyFail ? 1 : 0;
    }

    // ---------------------------------------------------------------- shock_reach_setting, floor_end_shocks_crossers, fallen_wire_shocks_crossers
    static void ShockTable()
    {
        // Bar: All -> floor end, downed wire and dropped deck cord all bite; Only downed lines -> downed and dropped bite, floor end not;
        // None -> nothing. Only a live line bites; the fixer of THIS line, a non-flesh, a dead or an already-out pawn are never shocked.
        var bad = new List<string>(); int n = 0;
        foreach (ShockReach r in new[] { ShockReach.None, ShockReach.OnlyDownedLines, ShockReach.All })
            foreach (LineKind k in new[] { LineKind.FloorEnd, LineKind.DownedSpan, LineKind.DroppedCord })
                for (int m = 0; m < 32; m++)
                {
                    bool live = (m & 1) != 0, flesh = (m & 2) != 0, dead = (m & 4) != 0, outAlready = (m & 8) != 0, fixing = (m & 16) != 0;
                    bool kindBites = r == ShockReach.All || (r == ShockReach.OnlyDownedLines && k != LineKind.FloorEnd);
                    bool want = live && kindBites && flesh && !dead && !outAlready && !fixing;
                    bool got = ShockRule.Takes(r, k, live, flesh, dead, outAlready, fixing);
                    n++;
                    if (got != want && bad.Count < 6) bad.Add($"{r}/{k} live={live} flesh={flesh} dead={dead} out={outAlready} fixing={fixing}: got {got}, want {want}");
                }
        Row("K_SHOCK_REACH_TABLE", B("shock_reach_setting", "floor_end_shock", "fallen_wire_shock", "floor_end_shocks_crossers", "fallen_wire_shocks_crossers"),
            "fixed", bad.Count == 0 ? "PASS" : "FAIL", n, bad.Count == 0 ? "3 reaches x 3 line kinds x 32 pawn states, the bar's table exactly" : string.Join("; ", bad));
        // the default is All (bar: "set to All on a fresh install"): the enum value the settings default names is checked by the Python half;
        // here: the three values are distinct and None silences every kind
        bool distinct = ShockRule.KindBites(ShockReach.All, LineKind.FloorEnd) && !ShockRule.KindBites(ShockReach.OnlyDownedLines, LineKind.FloorEnd)
                        && ShockRule.KindBites(ShockReach.OnlyDownedLines, LineKind.DroppedCord) && !ShockRule.KindBites(ShockReach.None, LineKind.DroppedCord);
        Row("K_SHOCK_THREE_VALUES_DIFFER", B("shock_reach_setting"), "fixed", distinct ? "PASS" : "FAIL", 4,
            "Only downed lines differs from All at a floor end and from None at a dropped cord (false pass: the third value wired to the old on/off)");
    }

    static void ShockJoinAndEnd(int seed)
    {
        // Bar: safe is the constructor whose job targets the conduit JOINING this end (the end cell or an orthogonal neighbour); a
        // constructor building some other conduit (diagonal or farther) is shocked. Only the end cell bites (EndCell = the tip's cell).
        var bad = new List<string>(); int n = 0;
        var rng = new Random(seed);
        for (int i = 0; i < 20000; i++)
        {
            int ex = rng.Next(-50, 250), ez = rng.Next(-50, 250), dx = rng.Next(-3, 4), dz = rng.Next(-3, 4);
            bool want = Math.Abs(dx) + Math.Abs(dz) <= 1;
            n++;
            if (ShockRule.TargetJoinsEnd(ex, ez, ex + dx, ez + dz) != want && bad.Count < 5) bad.Add($"end ({ex},{ez}) target d=({dx},{dz})");
            double tx = ex + rng.NextDouble() * 0.999, tz = ez + rng.NextDouble() * 0.999;
            var c = ShockRule.EndCell(tx, tz);
            n++;
            if ((c.x != ex || c.z != ez) && bad.Count < 5) bad.Add($"tip ({tx:0.000},{tz:0.000}) -> cell ({c.x},{c.z}), want ({ex},{ez})");
        }
        Row("K_SHOCK_JOINING_CONDUIT_ONLY", B("floor_end_shocks_crossers", "floor_end_shock"), "random", bad.Count == 0 ? "PASS" : "FAIL", n,
            $"seed {seed}: 20000 end/target pairs and tip cells, negative coordinates included; " + (bad.Count == 0 ? "joining = Manhattan <= 1, end cell = floor of the tip" : string.Join("; ", bad)));
    }

    static void FallenShock()
    {
        var bad = new List<string>(); int n = 0;
        for (int m = 0; m < 16; m++)
        {
            bool flesh = (m & 1) != 0, dead = (m & 2) != 0, outA = (m & 4) != 0, rest = (m & 8) != 0;
            bool want = flesh && !dead && !outA && !rest; n++;
            if (AerialMath.ShockTakes(flesh, dead, outA, rest) != want) bad.Add($"flesh={flesh} dead={dead} out={outA} restringing={rest}");
        }
        Row("K_FALLEN_SHOCK_FIXER_SAFE", B("fallen_wire_shocks_crossers", "fallen_wire_shock"), "fixed", bad.Count == 0 ? "PASS" : "FAIL", n,
            bad.Count == 0 ? "16 pawn states: only the colonist re-stringing THIS wire is exempt (which wire his job targets is game-side: not_kernel row)" : string.Join("; ", bad));
    }

    // ---------------------------------------------------------------- tap_steals_and_costs_goodwill, power_theft
    static void TapOneWayAndConserved(int seed)
    {
        var rng = new Random(seed + 1);
        var bad = new List<string>(); int n = 0;
        const double k = 1.0 / 60000.0; // CompPower.WattsToWattDaysPerTick
        for (int i = 0; i < 20000; i++)
        {
            double rate = rng.Next(0, 5) == 0 ? new[] { 0.0, -10, double.NaN, double.PositiveInfinity }[rng.Next(4)] : 50 + rng.NextDouble() * 1950;
            double gain = (rng.NextDouble() - 0.4) * 0.05, stored = rng.Next(0, 3) == 0 ? 0 : (rng.NextDouble() - 0.1) * 30;
            if (rng.Next(50) == 0) gain = double.NaN;
            bool same = rng.Next(10) == 0, en = rng.Next(10) != 0;
            double got = AerialMath.TapStolenPerTick(rate, gain, stored, k, same, en);
            n++;
            double avail = (double.IsNaN(gain) ? 0 : gain) + Math.Max(0, double.IsNaN(stored) ? 0 : stored);
            bool off = !en || same || !(rate > 0) || double.IsInfinity(rate) || double.IsNaN(gain);
            double want = off || avail <= 0 ? 0 : Math.Min(rate * k, avail);
            if (!(got >= 0) || double.IsInfinity(got) || Math.Abs(got - want) > 1e-12)
                if (bad.Count < 5) bad.Add($"rate={rate} gain={gain} stored={stored} same={same} en={en}: got {got}, want {want}");
        }
        // several taps on one victim in one tick never take more than the victim had (nothing created)
        int over = 0; string firstOver = null;
        for (int i = 0; i < 5000; i++)
        {
            double gain = rng.NextDouble() * 0.02, stored = rng.NextDouble() * 5; int taps = rng.Next(1, 7);
            double taken = 0;
            for (int t = 0; t < taps; t++)
                taken += AerialMath.TapStolenPerTick(50 + rng.NextDouble() * 1950, gain, stored, k, false, true, taken, rng.Next(8) != 0);
            n++;
            if (taken > gain + stored + 1e-12) { over++; firstOver ??= $"gain={gain} stored={stored} taps={taps} took {taken}"; }
        }
        if (over > 0) bad.Add($"{over} multi-tap ticks took more than the victim had, first {firstOver}");
        Row("K_TAP_ONE_WAY_CONSERVED", B("tap_steals_and_costs_goodwill", "power_theft"), "random", bad.Count == 0 ? "PASS" : "FAIL", n,
            $"seed {seed + 1}: 20000 single taps (never negative, never above rate x k or what the victim has, zero off/own-net/NaN) and 5000 multi-tap ticks (sum <= victim's gain + store); " + (bad.Count == 0 ? "all hold" : string.Join("; ", bad)));
    }

    static void TheftLeak(int seed)
    {
        // Bar: once caught, goodwill drains steadily (each whole day of draining costs perDay), an idle or removed clamp costs nothing.
        var rng = new Random(seed + 2);
        var bad = new List<string>(); int n = 0;
        const int tpd = 60000;
        for (int perDay = 0; perDay <= 10; perDay++)        // the slider's range, 0..10, default 2
            for (int trial = 0; trial < 300; trial++)
            {
                int drain = 0, total = 0; long drained = 0; int[] perDayCharges = new int[40];
                long clock = 0;
                for (int step = 0; step < 200; step++)
                {
                    int ticks = rng.Next(-5, 4000); bool draining = rng.Next(4) != 0;
                    int before = total;
                    total += AerialMath.TheftGoodwillAccrue(ref drain, ticks, draining, perDay, tpd);
                    if (draining && ticks > 0) drained += ticks;
                    clock += Math.Max(0, ticks);
                    n++;
                    if (total > before) { bad.Add($"perDay={perDay}: goodwill ROSE"); break; }
                    if (drain < 0 || drain >= tpd) { bad.Add($"perDay={perDay}: remainder {drain} out of [0,{tpd})"); break; }
                }
                long want = perDay > 0 ? -(drained / tpd) * perDay : 0;
                if (total != want && bad.Count < 5) bad.Add($"perDay={perDay} trial {trial}: charged {total}, want {want} for {drained} draining ticks");
            }
        // steady: 3 days of draining in 250-tick steps charge perDay at each day boundary, and nothing while idle
        int d2 = 0, tot2 = 0; var days = new List<int>();
        for (int t = 0; t < 3 * tpd / 250; t++) { int c = AerialMath.TheftGoodwillAccrue(ref d2, 250, true, 2, tpd); if (c != 0) days.Add(c); tot2 += c; }
        for (int t = 0; t < 1000; t++) tot2 += AerialMath.TheftGoodwillAccrue(ref d2, 250, false, 2, tpd);
        n++;
        if (days.Count != 3 || days.Any(c => c != -2) || tot2 != -6) bad.Add($"3 caught days at default 2/day: charges [{string.Join(",", days)}], total {tot2} (want -2,-2,-2 = -6, then nothing while removed)");
        Row("K_THEFT_STEADY_LEAK", B("tap_steals_and_costs_goodwill", "power_theft"), "sweep", bad.Count == 0 ? "PASS" : "FAIL", n,
            $"seed {seed + 2}: perDay swept 0..10 (slider), 300 random histories each: charge = -perDay x whole draining days, never a gain, remainder in range; " + (bad.Count == 0 ? "all hold" : string.Join("; ", bad.Take(5))));
    }

    static void TheftSight(int seed)
    {
        var rng = new Random(seed + 3); var bad = new List<string>(); int n = 0;
        for (int i = 0; i < 20000; i++)
        {
            double range = rng.Next(3, 31), dist = rng.NextDouble() * 40; bool los = rng.Next(3) != 0, up = rng.Next(3) != 0, held = rng.Next(5) == 0;
            bool want = !held && up && los && dist <= range; n++;
            if (AerialMath.TheftSpotted(dist, range, los, up, held) != want && bad.Count < 5) bad.Add($"d={dist:0.00} r={range} los={los} up={up} held={held}");
        }
        n++; if (AerialMath.TheftSpotted(double.NaN, 12, true, true, false)) bad.Add("NaN distance spots");
        Row("K_THEFT_NEEDS_A_WITNESS", B("tap_steals_and_costs_goodwill", "power_theft"), "sweep", bad.Count == 0 ? "PASS" : "FAIL", n,
            $"seed {seed + 3}: sight range swept 3..30 (slider): spotted only by an awake, free witness with line of sight within range (control: no witness, no drain); " + (bad.Count == 0 ? "all hold" : string.Join("; ", bad)));
    }

    // ---------------------------------------------------------------- spans: link rules (overhead_spans, pipe_pole_switch)
    static AnchorInfo RandAnchor(Random r, int id)
    {
        var a = new AnchorInfo { Id = id, X = r.Next(0, 60), Z = r.Next(0, 60), Faction = r.Next(6) == 0 ? 1 : 0, MaxLinks = r.Next(1, 5),
                                 Roofed = r.Next(10) == 0, IsAnchor = r.Next(15) != 0, Kind = r.Next(5) == 0 ? AerialLineKind.Pipe : AerialLineKind.Power };
        return a;
    }

    static void LinkRules(int seed)
    {
        var rng = new Random(seed + 4); var bad = new List<string>(); int n = 0;
        for (int i = 0; i < 20000; i++)
        {
            var a = RandAnchor(rng, 1); var b = RandAnchor(rng, rng.Next(6) == 0 ? 1 : 2);
            for (int l = rng.Next(0, 5); l > 0; l--) a.Linked.Add(100 + l);
            if (rng.Next(10) == 0) a.Linked.Add(b.Id);
            double range = 4 + rng.NextDouble() * 36;
            var v = AerialMath.CanLink(a, b, range); n++;
            double d2 = (a.X - b.X) * (double)(a.X - b.X) + (a.Z - b.Z) * (double)(a.Z - b.Z);
            if (v == LinkVerdict.Ok)
            {
                string why = a.Id == b.Id ? "self" : !a.IsAnchor || !b.IsAnchor ? "not an anchor" : a.Kind != b.Kind ? "pipe to power" : a.Faction != b.Faction ? "foreign"
                           : a.Roofed || b.Roofed ? "roofed" : d2 > range * range + 1e-9 ? "out of range" : a.Linked.Count >= a.MaxLinks || b.Linked.Count >= b.MaxLinks ? "full"
                           : a.Linked.Contains(b.Id) ? "already linked" : null;
                if (why != null && bad.Count < 5) bad.Add($"Ok but {why}: a=({a.X},{a.Z},{a.Kind},f{a.Faction}) b=({b.X},{b.Z},{b.Kind},f{b.Faction}) range {range:0.0}");
            }
            else
            {
                bool shouldOk = a.Id != b.Id && a.IsAnchor && b.IsAnchor && a.Kind == b.Kind && a.Faction == b.Faction && !a.Roofed && !b.Roofed
                                && d2 <= range * range && a.Linked.Count < a.MaxLinks && b.Linked.Count < b.MaxLinks && !a.Linked.Contains(b.Id) && !b.Linked.Contains(a.Id);
                if (shouldOk && bad.Count < 5) bad.Add($"{v} for a valid pair d={Math.Sqrt(d2):0.00} range {range:0.0}");
            }
            // symmetry of Ok
            n++;
            if ((v == LinkVerdict.Ok) != (AerialMath.CanLink(b, a, range) == LinkVerdict.Ok) && !a.Linked.Contains(b.Id) && bad.Count < 5) bad.Add("CanLink not symmetric");
        }
        Row("K_LINK_RULES", B("overhead_spans", "spans_above_everything", "pipe_pole_switch"), "random", bad.Count == 0 ? "PASS" : "FAIL", n,
            $"seed {seed + 4}: 20000 anchor pairs, ranges 4..40: Ok exactly when both anchors, same kind (pipe never to power), same faction, unroofed, in range, both under max links, not linked; " + (bad.Count == 0 ? "all hold" : string.Join("; ", bad)));
    }

    static List<AnchorInfo> RandSel(Random rng, int cnt)
    {
        var sel = new List<AnchorInfo>();
        for (int i = 0; i < cnt; i++) { var a = RandAnchor(rng, i + 1); a.IsAnchor = true; a.Roofed = rng.Next(20) == 0; a.Faction = rng.Next(10) == 0 ? 1 : 0; sel.Add(a); }
        return sel;
    }

    static void SpanningForest(int seed)
    {
        var rng = new Random(seed + 5); var bad = new List<string>(); int n = 0;
        for (int trial = 0; trial < 1500; trial++)
        {
            int cnt = rng.Next(2, 14); var sel = RandSel(rng, cnt); double range = 6 + rng.NextDouble() * 20;
            bool bigCaps = rng.Next(2) == 0; if (bigCaps) foreach (var a in sel) a.MaxLinks = 99;
            var res = AerialMath.MinimumSpanningLinks(sel, range); n++;
            var byId = sel.ToDictionary(a => a.Id);
            var parent = sel.ToDictionary(a => a.Id, a => a.Id);
            int Find(int x) { while (parent[x] != x) x = parent[x]; return x; }
            var deg = sel.ToDictionary(a => a.Id, a => 0);
            foreach (var (x, y) in res)
            {
                var a = byId[x]; var b = byId[y];
                if (AerialMath.CanLink(a, b, range) != LinkVerdict.Ok) { bad.Add($"trial {trial}: edge {x}-{y} not linkable ({AerialMath.CanLink(a, b, range)})"); break; }
                if (Find(x) == Find(y)) { bad.Add($"trial {trial}: edge {x}-{y} closes a cycle"); break; }
                parent[Find(x)] = Find(y); deg[x]++; deg[y]++;
            }
            foreach (var a in sel) if (deg[a.Id] > a.MaxLinks) { bad.Add($"trial {trial}: anchor {a.Id} gets {deg[a.Id]} links, max {a.MaxLinks}"); break; }
            if (bigCaps)
            {
                // with no link cap, the forest joins every pair the range graph joins (nothing left out)
                var p2 = sel.ToDictionary(a => a.Id, a => a.Id);
                int F2(int x) { while (p2[x] != x) x = p2[x]; return x; }
                for (int i = 0; i < cnt; i++) for (int j = i + 1; j < cnt; j++)
                    if (AerialMath.CanLink(sel[i], sel[j], range) == LinkVerdict.Ok) { int ra = F2(sel[i].Id), rb = F2(sel[j].Id); if (ra != rb) p2[ra] = rb; }
                for (int i = 0; i < cnt; i++) for (int j = i + 1; j < cnt; j++)
                    if ((F2(sel[i].Id) == F2(sel[j].Id)) != (Find(sel[i].Id) == Find(sel[j].Id)) && bad.Count < 6)
                    { bad.Add($"trial {trial}: {sel[i].Id} and {sel[j].Id} joinable by range but left apart"); i = cnt; break; }
            }
        }
        Row("K_AUTOLINK_SELECTED_FOREST", B("overhead_spans", "spans_above_everything"), "random", bad.Count == 0 ? "PASS" : "FAIL", n,
            $"seed {seed + 5}: 1500 selections of 2..13 anchors: every edge linkable, no cycle, max links kept, and uncapped it joins every range-connected pair; " + (bad.Count == 0 ? "all hold" : string.Join("; ", bad.Take(5))));
    }

    static void AutoLink(int seed)
    {
        var rng = new Random(seed + 6); var bad = new List<string>(); int n = 0;
        for (int trial = 0; trial < 5000; trial++)
        {
            var self = RandAnchor(rng, 1000); self.IsAnchor = true; self.Roofed = false;
            var others = RandSel(rng, rng.Next(0, 10)); double range = 4 + rng.NextDouble() * 36;
            int got = AerialMath.AutoLinkPick(self, others, range); n++;
            int want = -1; long bd = long.MaxValue;
            foreach (var o in others.OrderBy(o => o.Id))
                if (AerialMath.CanLink(self, o, range) == LinkVerdict.Ok) { long d = (o.X - self.X) * (long)(o.X - self.X) + (o.Z - self.Z) * (long)(o.Z - self.Z); if (d < bd) { bd = d; want = o.Id; } }
            if (got != want && bad.Count < 5) bad.Add($"trial {trial}: picked {got}, nearest linkable (lower id on ties) {want}");
        }
        Row("K_AUTOLINK_NEAREST", B("overhead_spans"), "random", bad.Count == 0 ? "PASS" : "FAIL", n,
            $"seed {seed + 6}: 5000 builds: auto-link picks the nearest anchor it may link to, ties to the lower id, -1 when none; " + (bad.Count == 0 ? "all hold" : string.Join("; ", bad)));
    }

    // ---------------------------------------------------------------- settings_switch_cleanly, pipe_pole_switch, mod_settings
    static void KindSwitches()
    {
        var bad = new List<string>(); int n = 0;
        foreach (bool p in new[] { false, true }) foreach (bool q in new[] { false, true }) foreach (bool s in new[] { false, true })
        {
            n += 4;
            if (AerialKinds.KindOn(AerialLineKind.Power, p, q) != p) bad.Add($"power anchor with master={p}, pipe switch={q} reads {AerialKinds.KindOn(AerialLineKind.Power, p, q)}");
            if (AerialKinds.KindOn(AerialLineKind.Pipe, p, q) != q) bad.Add($"pipe pole with master={p}, pipe switch={q} reads {AerialKinds.KindOn(AerialLineKind.Pipe, p, q)}");
            if (AerialKinds.KindBehaviour(AerialLineKind.Power, p, q, s) != (p && s)) bad.Add($"power behaviour master={p} setting={s}");
            if (AerialKinds.KindBehaviour(AerialLineKind.Pipe, p, q, s) != q) bad.Add($"pipe behaviour pipe switch={q} master={p} setting={s}");
        }
        n += 4;
        if (AerialKinds.StrandCap(AerialLineKind.Pipe, 3) != 1 || AerialKinds.Drips(AerialLineKind.Pipe, true) || AerialKinds.Sways(AerialLineKind.Pipe) || AerialKinds.CarriesPower(AerialLineKind.Pipe))
            bad.Add("a pipe span strands/drips/sways/carries power");
        for (int m = 1; m <= 3; m++) { n++; if (AerialKinds.StrandCap(AerialLineKind.Power, m) != m) bad.Add($"power strand cap {m} -> {AerialKinds.StrandCap(AerialLineKind.Power, m)}"); }
        n += 3;
        if (AerialMath.WireSwayPrefAllows(2, true) || !AerialMath.WireSwayPrefAllows(1, false) || AerialMath.WireSwayPrefAllows(0, false) != false) bad.Add("sway mode Off/Always/Auto wrong");
        Row("K_SWITCHES_OWN_THEIR_KIND", B("settings_switch_cleanly", "pipe_pole_switch", "mod_settings"), "fixed", bad.Count == 0 ? "PASS" : "FAIL", n,
            bad.Count == 0 ? "every on/off combination: the power master governs power anchors only, the pipe-pole switch pipe poles only; strands 1..3 pass through; sway modes" : string.Join("; ", bad));
    }

    static void RangeSagSweep()
    {
        var bad = new List<string>(); int n = 0;
        for (float v = 8f; v <= 40f; v += 1f) { n++; if (AerialKinds.RangeFor(AerialLineKind.Power, v, 0) != v) bad.Add($"power maxSpan slider {v} -> {AerialKinds.RangeFor(AerialLineKind.Power, v, 0)}"); }
        for (float v = 0f; v <= 0.15001f; v += 0.005f) { n++; if (Math.Abs(AerialKinds.SagFor(AerialLineKind.Power, v, 0) - v) > 1e-6) bad.Add($"power sag slider {v}"); }
        n += 4;
        if (AerialKinds.RangeFor(AerialLineKind.Pipe, 0, float.NaN) != AerialKinds.PipeSpanMin) bad.Add("pipe NaN range");
        if (AerialKinds.RangeFor(AerialLineKind.Pipe, 0, 1000) != AerialKinds.PipeSpanMax) bad.Add("pipe range unclamped");
        if (AerialKinds.SagFor(AerialLineKind.Power, float.NaN, 0) != 0f || AerialKinds.SagFor(AerialLineKind.Pipe, 0, 9f) != AerialKinds.PipeSagMax) bad.Add("sag NaN/clamp");
        if (AerialKinds.RangeFor(AerialLineKind.Pipe, 40, AerialKinds.PipeMaxSpanDefault) != 12f) bad.Add("pipe default range");
        // sag depth: never negative, proportional to span
        var rng = new Random(7);
        for (int i = 0; i < 2000; i++) { double L = rng.NextDouble() * 40, s = rng.NextDouble() * 0.15; n++; if (Math.Abs(AerialKinds.SagDepth(L, s) - s * L) > 1e-12 || AerialKinds.SagDepth(-L, s) != 0) { bad.Add("sag depth"); break; } }
        Row("K_RANGE_SAG_SETTINGS_SWEEP", B("overhead_spans", "mod_settings", "settings_switch_cleanly"), "sweep", bad.Count == 0 ? "PASS" : "FAIL", n,
            bad.Count == 0 ? "max span slider 8..40 and sag slider 0..0.15 pass through unchanged; pipe range/sag clamped, NaN safe; sag depth = factor x span" : string.Join("; ", bad.Take(6)));
    }

    static void Restring()
    {
        var bad = new List<string>(); int n = 0; int prev = int.MaxValue;
        for (double s = 0.1; s <= 3.0; s += 0.05) { int t = AerialMath.RestringTicks(s); n++; if (t <= 0 || t > prev) bad.Add($"speed {s:0.00} -> {t}"); prev = t; }
        n += 3;
        if (AerialMath.RestringTicks(1.0) != 300) bad.Add("speed 1 is not the 300-tick job");
        if (AerialMath.RestringTicks(0) <= 0 || AerialMath.RestringTicks(-1) <= 0 || AerialMath.RestringTicks(double.NaN) <= 0) bad.Add($"zero/negative/NaN speed -> {AerialMath.RestringTicks(0)}/{AerialMath.RestringTicks(-1)}/{AerialMath.RestringTicks(double.NaN)}");
        Row("K_RESTRING_IS_A_JOB", B("restring_cut_span", "restring_job"), "sweep", bad.Count == 0 ? "PASS" : "FAIL", n,
            bad.Count == 0 ? "construction speed 0.1..3.0: the re-string job always takes positive time, faster with skill, 300 ticks at speed 1, never instant at 0/negative/NaN" : string.Join("; ", bad.Take(5)));
    }

    // ---------------------------------------------------------------- downed_spans, fallen_span_on_ground, gravship_keeps_connections
    static void Removal(int seed)
    {
        var rng = new Random(seed + 8); var bad = new List<string>(); int n = 0;
        for (int trial = 0; trial < 5000; trial++)
        {
            int id = 1; var spans = new List<(int, SpanState)>();
            int cnt = rng.Next(0, 6);
            for (int i = 0; i < cnt; i++) spans.Add((rng.Next(2, 9), rng.Next(3) == 0 ? SpanState.Cut : SpanState.Up));
            bool killed = rng.Next(2) == 0; HashSet<int> aboard = rng.Next(2) == 0 ? new HashSet<int>(spans.Select(s => s.Item1).Where(_ => rng.Next(2) == 0)) : null;
            var plan = AerialMath.PlanRemoval(id, killed, spans, aboard); n++;
            var partners = spans.Select(s => s.Item1).Distinct().ToList();
            int wantFallen = killed ? spans.Count(s => s.Item2 == SpanState.Up) : 0;
            string why = null;
            if (plan.Fallen.Count != wantFallen) why = $"fallen {plan.Fallen.Count}, want one per UP span when killed ({wantFallen})";
            else if (plan.Fallen.Any(f => !f.TowardDead || !partners.Contains(f.Survivor))) why = "a fallen half not on a survivor toward the dead anchor";
            else if (aboard == null || killed)
            {
                if (!partners.All(plan.Reseed.Contains) || plan.Reseed.Count != partners.Count) why = "reseed is not every former partner once";
                else if (plan.Kept.Count + plan.Grounded.Count != 0) why = "kept/grounded outside a gravship lift";
            }
            else
            {
                if (plan.Kept.Any(p => !aboard.Contains(p)) || plan.Grounded.Any(p => aboard.Contains(p)) || plan.Kept.Count + plan.Grounded.Count != partners.Count)
                    why = "gravship lift: kept must be exactly the partners aboard, grounded exactly those left";
                else if (plan.Reseed.Any(aboard.Contains)) why = "a partner flying along is re-seeded as if left";
            }
            if (why != null && bad.Count < 5) bad.Add($"trial {trial} killed={killed} aboard={(aboard == null ? "null" : string.Join(",", aboard))} spans=[{string.Join(",", spans.Select(s => s.Item1 + ":" + s.Item2))}]: {why}");
        }
        Row("K_REMOVAL_PLAN", B("downed_spans", "fallen_span_on_ground", "gravship_connectivity", "gravship_keeps_connections", "connectivity_truth"), "random", bad.Count == 0 ? "PASS" : "FAIL", n,
            $"seed {seed + 8}: 5000 removals: a killed mast drops one wire per UP span onto each survivor (none for a cut span, none when dismantled), every partner re-seeded once, a gravship lift keeps exactly the partners aboard; " + (bad.Count == 0 ? "all hold" : string.Join("; ", bad)));
        // watchdog: an UP span whose ends are not on one net is repaired; a CUT span is left split
        var w = new List<SpanNetRead> { new SpanNetRead { Span = 1, NetA = 3, NetB = 3, State = SpanState.Up }, new SpanNetRead { Span = 2, NetA = 3, NetB = 4, State = SpanState.Up },
                                        new SpanNetRead { Span = 3, NetA = -1, NetB = -1, State = SpanState.Up }, new SpanNetRead { Span = 4, NetA = 3, NetB = 4, State = SpanState.Cut } };
        var rep = AerialMath.WatchdogRepairs(w);
        Row("K_WATCHDOG_CUT_STAYS_SPLIT", B("connectivity_truth", "break_ends_live_dead", "cut_live_and_dead_ends"), "fixed", rep.SequenceEqual(new[] { 2, 3 }) ? "PASS" : "FAIL", 4,
            "watchdog repairs [" + string.Join(",", rep) + "], want [2,3]: an up span split or net-less is repaired, a joined one left, a cut one stays split");
    }

    static void FallenLies(int seed)
    {
        var rng = new Random(seed + 9); var bad = new List<string>(); int n = 0, grounded = 0, blocked = 0; int nan = 0;
        string shrink = null; double shrinkLen = double.MaxValue;
        var depths = new List<double>(); int failLays = 0;
        for (int trial = 0; trial < 3000; trial++)
        {
            int W = 40; var wall = new bool[W, W];
            int walls = rng.Next(0, 3);
            for (int k = 0; k < walls; k++) { int wx = rng.Next(5, 35); for (int z = 0; z < W; z++) if (rng.Next(8) != 0) wall[wx, z] = true; }
            Func<int, int, bool> walkable = (x, z) => x >= 0 && z >= 0 && x < W && z < W && !wall[x, z];
            double bx = rng.Next(8, 32) + 0.5, bz = rng.Next(8, 32) + 0.5; if (!walkable((int)bx, (int)bz)) continue;
            double ang = rng.NextDouble() * Math.PI * 2, span = 4 + rng.NextDouble() * 16;
            var basePt = new P2(bx, bz); var toward = new P2(bx + Math.Cos(ang) * span, bz + Math.Sin(ang) * span);
            var top = new P2(bx + (rng.NextDouble() - 0.5) * 0.6, bz + 1.5 + rng.NextDouble());
            int lseed = rng.Next(), lside = rng.Next(-1, 2);
            var lay = AerialMath.LayFallen(top, basePt, toward, span * 1.05, lseed, walkable, lside); n++;
            if (lay.Pts.Any(p => double.IsNaN(p.X) || double.IsNaN(p.Z))) { nan++; continue; }
            if (lay.Blocked) blocked++;
            if (lay.TipGrounded) grounded++;
            string why = null;
            if (!lay.TipGrounded && !lay.Blocked) why = "an unblocked fallen wire never reaches the ground (would hang in the air)";
            for (int i = Math.Max(0, lay.GroundFrom); lay.GroundFrom >= 0 && i < lay.Pts.Count && why == null; i++)
            {
                var p = lay.Pts[i];
                if (P2.Dist(p, basePt) > 0.75 && !walkable((int)Math.Floor(p.X), (int)Math.Floor(p.Z)))
                {
                    var wallCols = new List<string>();
                    for (int x = 0; x < W; x++) { var gaps = Enumerable.Range(0, W).Where(z => !wall[x, z]).ToList(); if (gaps.Count < W) wallCols.Add($"x={x} gaps z=[{string.Join(",", gaps)}]"); }
                    why = $"ground point {i}/{lay.Pts.Count} {p} lies in a wall cell; repro: LayFallen(top={top}, base={basePt}, toward={toward}, length={span * 1.05:0.000}, seed={lseed}, side={lside}), walls {string.Join("; ", wallCols)}, Blocked={lay.Blocked}, GroundFrom={lay.GroundFrom}, dist from base {P2.Dist(p, basePt):0.00}";
                }
            }
            if (why == null && lay.Pts.Count > 0 && (lay.Tip.X != lay.Pts[lay.Pts.Count - 1].X || lay.Tip.Z != lay.Pts[lay.Pts.Count - 1].Z)) why = "Tip is not the polyline's last point";
            if (lay.GroundFrom >= 0)
            {
                bool any = false;
                for (int i = lay.GroundFrom; i < lay.Pts.Count; i++)
                {
                    var p = lay.Pts[i]; int cx = (int)Math.Floor(p.X), cz = (int)Math.Floor(p.Z);
                    if (P2.Dist(p, basePt) <= 0.75 || walkable(cx, cz)) continue;
                    any = true; double best = 9;
                    for (int ox = -2; ox <= 2; ox++) for (int oz = -2; oz <= 2; oz++)
                        if (walkable(cx + ox, cz + oz))
                        { double qx = Math.Max(cx + ox, Math.Min(cx + ox + 1, p.X)), qz = Math.Max(cz + oz, Math.Min(cz + oz + 1, p.Z)); best = Math.Min(best, Math.Sqrt((qx - p.X) * (qx - p.X) + (qz - p.Z) * (qz - p.Z))); }
                    depths.Add(best);
                }
                if (any) failLays++;
            }
            if (why != null) { if (span < shrinkLen) { shrinkLen = span; shrink = $"trial {trial} span {span:0.00} walls {walls}: {why}"; } if (bad.Count < 3) bad.Add($"trial {trial}: {why.Substring(0, Math.Min(60, why.Length))}"); }
        }
        if (nan > 0) bad.Add($"{nan} lays with NaN points");
        depths.Sort();
        Row("K_INFO_FALLEN_WALL_DEPTH", B("fallen_span_on_ground", "cords_meet_walls_at_face"), "info", "INFO", depths.Count,
            depths.Count == 0 ? "no ground point inside a wall" : $"{failLays} of {n} lays put {depths.Count} ground points inside a wall cell; depth into the wall (cells): median {depths[depths.Count / 2]:0.000}, 90th {depths[(int)(depths.Count * 0.9)]:0.000}, max {depths[depths.Count - 1]:0.000}");
        Row("K_FALLEN_WIRE_LIES_ON_GROUND", B("fallen_span_on_ground", "downed_spans", "cords_meet_walls_at_face"), "random", bad.Count == 0 ? "PASS" : "FAIL", n,
            $"seed {seed + 9}: {n} fallen wires on 40x40 maps with 0..2 gappy walls ({grounded} reached the ground, {blocked} stopped by a wall): an unblocked wire reaches the ground, no ground point in a wall past the 0.75-cell bracket face, Tip is the end; "
            + (bad.Count == 0 ? "all hold" : string.Join("; ", bad) + (shrink != null ? " | smallest failing span: " + shrink : "")));
    }

    // ---------------------------------------------------------------- no_hose, no_hose_in_gss: what the shipped DLL itself carries
    static void DllScan()
    {
        string path = Environment.GetEnvironmentVariable("GSS_DLL");
        string[] bars = B("no_hose", "no_hose_in_gss");
        if (string.IsNullOrEmpty(path) || !File.Exists(path)) { Row("K_DLL_NO_HOSE_TYPES", bars, "fixed", "UNSETTLED", 0, "GSS_DLL not given or missing: " + path); return; }
        var hose = new Regex(@"(?<![A-Za-z])[hH]oses?(?![a-z])|Hose|(?<![A-Za-z])[rR]eels?(?![a-z])|Reel");
        var port = new Regex(@"(?<![A-Za-z])hoses?\s+ports?|pipe (or|and) hose ports?", RegexOptions.IgnoreCase);
        var identLike = new Regex(@"^[A-Za-z_][A-Za-z0-9_.]*$");
        using var fs = File.OpenRead(path); using var pe = new PEReader(fs); var md = pe.GetMetadataReader();
        var names = new List<string>(); int nNames = 0;
        foreach (var th in md.TypeDefinitions)
        {
            var t = md.GetTypeDefinition(th); string tn = md.GetString(t.Namespace) + "." + md.GetString(t.Name); nNames++;
            if (hose.IsMatch(md.GetString(t.Name))) names.Add("type " + tn);
            foreach (var mh in t.GetMethods()) { nNames++; string m = md.GetString(md.GetMethodDefinition(mh).Name); if (hose.IsMatch(m)) names.Add(tn + "::" + m); }
            foreach (var fh in t.GetFields()) { nNames++; string f = md.GetString(md.GetFieldDefinition(fh).Name); if (hose.IsMatch(f) && !f.Contains("<")) names.Add(tn + "." + f); }
        }
        Row("K_DLL_NO_HOSE_TYPES", bars, "fixed", names.Count == 0 ? "PASS" : "FAIL", nNames,
            $"shipped DLL: {nNames} type/method/field names, Hose/Reel among them: " + (names.Count == 0 ? "none" : string.Join(", ", names.Take(10))));
        var texts = new List<string>(); var idents = new List<string>(); int nUs = 0; string header = null;
        var h = MetadataTokens.UserStringHandle(1);
        while (!h.IsNil)
        {
            string s = md.GetUserString(h); nUs++;
            if (s.StartsWith("Drawn ")) header = s;
            if (hose.IsMatch(s) && !port.IsMatch(s) && s.IndexOf("FlowWorks", StringComparison.OrdinalIgnoreCase) < 0) (identLike.IsMatch(s) ? idents : texts).Add(s.Length > 100 ? s.Substring(0, 100) : s);
            h = md.GetNextHandle(h);
        }
        Row("K_DLL_NO_HOSE_TEXT", bars, "fixed", texts.Count == 0 ? "PASS" : "FAIL", nUs,
            $"shipped DLL user strings: {nUs}; player text offering a hose/reel: " + (texts.Count == 0 ? "none" : string.Join(" | ", texts.Take(8))) + $"; identifier-shaped (INFO): [{string.Join(", ", idents.Distinct())}]");
        bool hdrOk = header != null && !Regex.IsMatch(header, "pipe|hose", RegexOptions.IgnoreCase);
        Row("K_DLL_HEADER_NO_PIPE_HOSE", bars, "fixed", header == null ? "UNSETTLED" : hdrOk ? "PASS" : "FAIL", 1,
            "the settings header the shipped DLL carries: " + (header ?? "not found (no user string starting 'Drawn ')"));
    }
}
