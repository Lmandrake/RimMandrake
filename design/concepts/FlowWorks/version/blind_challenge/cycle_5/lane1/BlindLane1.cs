// Blind lane 1, FlowWorks 0.1.0, cycle 5 (judge run judge-1795794888). Written from the bars (record.json inventory rows
// inv_overflow_sheet, inv_converters, inv_bottles_thirst, inv_drilling, inv_sprinklers; sheet.md; plan.md) and the shipped
// settings, against the shipped kernels only. Not the builder's tests. One JSON row per line on stdout.
// Settings defaults arrive as FW_<field> environment variables, read by run_lane1.py from the settings files (never hand-copied).
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.FlowWorks;
using RimMandrake.FlowWorks.Drilling;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.FlowWorks.Sprinklers;
using RimMandrake.FlowWorks.Thirst;
using static RimMandrake.FlowWorks.RM_SheetMath;

public static class BlindLane1
{
    static readonly List<string> Out = new List<string>();
    static int fails;

    static string J(string s)
    {
        var b = new StringBuilder("\"");
        foreach (char c in s ?? "")
        {
            if (c == '"' || c == '\\') b.Append('\\').Append(c);
            else if (c < ' ') b.Append("\\u").Append(((int)c).ToString("x4"));
            else b.Append(c);
        }
        return b.Append('"').ToString();
    }

    static void Row(string id, string[] bars, string kind, string verdict, long cases, string detail)
    {
        if (verdict == "FAIL") fails++;
        Out.Add("{\"id\": " + J(id) + ", \"bars\": [" + string.Join(", ", bars.Select(J)) + "], \"kind\": " + J(kind)
                + ", \"verdict\": " + J(verdict) + ", \"cases\": " + cases + ", \"detail\": " + J(detail) + "}");
    }

    static float EnvF(string n, float d)
    {
        string v = Environment.GetEnvironmentVariable("FW_" + n);
        return v != null && float.TryParse(v, NumberStyles.Float, CultureInfo.InvariantCulture, out float f) ? f : d;
    }

    static readonly string[] SHEET = { "inv_overflow_sheet" };
    static readonly string[] CONV = { "inv_converters" };
    static readonly string[] THIRST = { "inv_bottles_thirst" };
    static readonly string[] DRILL = { "inv_drilling" };
    static readonly string[] SPRINK = { "inv_sprinklers" };

    // ───────────────────────────── sheet kernel ─────────────────────────────

    sealed class Rig
    {
        public State S; public World W; public Params P; public Random R; public int Fluids;
    }

    static Rig RandomRig(int seed, Params p = null)
    {
        var r = new Random(seed);
        int w = r.Next(3, 11), h = r.Next(3, 11);
        var world = new World(w, h);
        int nf = r.Next(1, 4);
        for (int c = 0; c < w * h; c++)
        {
            int k = r.Next(100);
            world.Kinds[c] = k < 62 ? Kind.Open : k < 72 ? Kind.Blocked : k < 78 ? Kind.Door : k < 84 ? Kind.Grate : k < 95 ? Kind.Receiver : Kind.Sink;
            if (world.Kinds[c] == Kind.Receiver) world.RoomDl[c] = r.Next(0, 6000);
            if (world.Kinds[c] == Kind.Receiver || world.Kinds[c] == Kind.Sink) world.BodyFluid[c] = (byte)(r.Next(3) == 0 ? r.Next(1, nf + 1) : 0);
            world.SoakMilliDl[c] = r.Next(4) == 0 ? 0 : r.Next(0, 3000);
            world.EvapMilliDl[c] = r.Next(3) == 0 ? 0 : r.Next(0, 2000);
            world.TempDeciC[c] = r.Next(5) == 0 ? r.Next(-80, 20) : r.Next(-20, 400);
        }
        for (int f = 1; f <= nf; f++)
            world.Fluids[f] = new FluidRule
            {
                InfiltrationPermille = r.Next(0, 2000), EvaporationPermille = r.Next(0, 2000),
                FreezeDeciC = r.Next(3) == 0 ? -100 : 0, NeverFreezes = r.Next(3) == 0,
                BoilMilliDl = r.Next(5) == 0 ? r.Next(1, 4000) : 0, BoilAboveDeciC = r.Next(-400, 300)
            };
        if (r.Next(3) == 0) world.Credit = (cell, want, fl) => want * ((cell % 3) + 1) / 3;
        return new Rig { S = new State(w, h, (uint)r.Next()), W = world, P = p ?? new Params(), R = r, Fluids = nf };
    }

    static SpillOffer RandomOffer(Rig g)
    {
        int n = g.S.Dl.Length;
        int len = g.R.Next(1, Math.Min(n, 8) + 1);
        var lips = new int[len];
        int start = g.R.Next(n);
        for (int i = 0; i < len; i++) lips[i] = (start + i * (g.R.Next(2) == 0 ? 1 : g.S.W)) % n;
        return new SpillOffer { LipNearestFirst = lips, AmountDl = g.R.Next(-5, 25000), Fluid = (byte)g.R.Next(0, g.Fluids + 1), From = (Source)g.R.Next(SourceCount) };
    }

    static string Invariants(Rig g)
    {
        State s = g.S;
        if (!s.LedgerCloses) return "ledger: in " + s.TotalIn + " != standing " + s.Standing + " + out " + s.TotalOut;
        int wet = 0;
        for (int c = 0; c < s.Dl.Length; c++)
        {
            if (s.Dl[c] < 0) return "cell " + c + " holds " + s.Dl[c] + " dL";
            if (s.Dl[c] > 0) { wet++; if (s.Fluid[c] == 0) return "cell " + c + " wet with no fluid"; }
            else if (s.Fluid[c] != 0 || s.Tiers[c] != Tier.None) return "dry cell " + c + " keeps fluid/tier";
            if (s.Dl[c] > g.P.SheetCapDl) return "cell " + c + " over the cap: " + s.Dl[c];
            if (s.Dl[c] > 0 && !World.HoldsSheet(g.W.Kinds[c])) return "sheet on a " + g.W.Kinds[c] + " cell " + c;
        }
        if (wet != s.WetCount) return "wet cells " + wet + " but WetCount " + s.WetCount;
        if (s.WetCount > g.P.MaxWetCells) return "wet cells " + s.WetCount + " over the cap " + g.P.MaxWetCells;
        for (int c = 0; c < g.W.RoomDl.Length; c++) if (g.W.Kinds[c] == Kind.Receiver && g.W.RoomDl[c] < 0) return "receiver " + c + " room went negative";
        return null;
    }

    // one random operation; returns a description
    static string Op(Rig g, PulseReport rep)
    {
        int k = g.R.Next(100);
        State s = g.S;
        if (k < 35)
        {
            int m = g.R.Next(1, 4);
            var offers = new List<SpillOffer>();
            for (int i = 0; i < m; i++) offers.Add(RandomOffer(g));
            var before = (int[])s.Dl.Clone(); var fb = (byte[])s.Fluid.Clone();
            int[] acc = ResolveSpills(s, g.W, g.P, offers);
            for (int i = 0; i < m; i++)
                if (acc[i] < 0 || acc[i] > Math.Max(0, offers[i].AmountDl)) return "FAILOP spill accepted " + acc[i] + " of " + offers[i].AmountDl;
            for (int c = 0; c < s.Dl.Length; c++)
                if (before[c] > 0 && fb[c] != s.Fluid[c]) return "FAILOP spill changed cell " + c + " fluid " + fb[c] + "->" + s.Fluid[c] + " (liquids mixed)";
            return "spill x" + m;
        }
        if (k < 85) { Pulse(s, g.W, g.P, rep); return "pulse"; }
        if (k < 90) { int c = g.R.Next(s.Dl.Length); Burn(s, c, g.R.Next(-3, 3000)); return "burn " + c; }
        if (k < 94) { int c = g.R.Next(s.Dl.Length); HandOver(s, c, g.R.Next(-3, 3000), g.R.Next(2) == 0); return "handover " + c; }
        if (k < 98) { int c = g.R.Next(s.Dl.Length); PurgeConnected(s, c, g.R.Next(3) == 0 ? AllDl : g.R.Next(-3, 20000)); return "purgeConnected " + c; }
        PurgeAll(s); return "purgeAll";
    }

    static string RunRandom(int seed, int ops, Params p, out int doneOps)
    {
        var g = RandomRig(seed, p);
        var rep = new PulseReport();
        doneOps = 0;
        var trace = new List<string>();
        for (int i = 0; i < ops; i++)
        {
            string d;
            try { d = Op(g, rep); }
            catch (Exception e) { return "op " + i + " threw " + e.GetType().Name + ": " + e.Message + " after [" + string.Join(", ", trace.Skip(Math.Max(0, trace.Count - 4))) + "]"; }
            trace.Add(d);
            doneOps++;
            if (d.StartsWith("FAILOP")) return "op " + i + ": " + d.Substring(7);
            string bad = Invariants(g);
            if (bad != null) return "op " + i + " (" + d + "): " + bad + " after [" + string.Join(", ", trace.Skip(Math.Max(0, trace.Count - 4))) + "]";
        }
        return null;
    }

    static void SheetRandomLedger()
    {
        int cases = 0; string first = null; int firstSeed = -1;
        long opsTotal = 0;
        for (int seed = 1; seed <= 1500; seed++)
        {
            string bad = RunRandom(seed, 120, null, out int done);
            opsTotal += done; cases++;
            if (bad != null && first == null) { first = bad; firstSeed = seed; }
        }
        string shrunk = "";
        if (first != null)
        {
            // shrink: the fewest ops on that seed that still fail
            for (int n = 1; n <= 120; n++) if (RunRandom(firstSeed, n, null, out _) != null) { shrunk = "; shrunk to the first " + n + " ops of seed " + firstSeed; break; }
        }
        Row("L1_RANDOM_SHEET_LEDGER_AND_INVARIANTS", SHEET, "random", first == null ? "PASS" : "FAIL", cases,
            first == null
                ? "seeds 1..1500, 120 random ops each (" + opsTotal + " ops: spills from every source and fluid incl. bad amounts and fluid 0, pulses, burns, hand-overs, connected and whole purges) on random worlds (open/blocked/door/grate/receiver/sink, soak, evaporation, frost, boil, partial engine credit): after every op the ledger In == Standing + Returned + JoinedLake + Soaked + Evaporated + Burned + Purged closes to the dL; no negative, over-cap or orphan cell; no sheet on a cell that cannot hold one; wet cells == WetCount <= MaxWetCells; a spill never changes the liquid of a wet cell"
                : "seed " + firstSeed + ": " + first + shrunk);
    }

    static void SheetSaveLoad()
    {
        int cases = 0; string first = null;
        for (int seed = 1; seed <= 400 && first == null; seed++)
        {
            var a = RandomRig(seed);
            var rep = new PulseReport();
            int at = a.R.Next(1, 40), total = at + a.R.Next(1, 60);
            Rig b = null;
            var rngA = new Random(seed * 7919); Random rngB = null;
            for (int i = 0; i < total; i++)
            {
                if (i == at)
                {
                    byte[] bytes = Save(a.S);
                    b = new Rig { S = Load(bytes), W = a.W.Clone(), P = a.P, Fluids = a.Fluids };
                    if (Hash(b.S) != Hash(a.S)) { first = "seed " + seed + ": load hash differs right after load at pulse " + i; break; }
                    rngB = new Random(seed * 7919 + i);
                    rngA = new Random(seed * 7919 + i);
                }
                foreach (var (g, rng) in new[] { (a, rngA), (b, rngB) })
                {
                    if (g == null) continue;
                    g.R = rng;
                    if (rng.Next(3) == 0) ResolveSpills(g.S, g.W, g.P, new List<SpillOffer> { RandomOffer(g) });
                    Pulse(g.S, g.W, g.P, rep);
                }
            }
            cases++;
            if (first == null && b != null && Hash(a.S) != Hash(b.S))
                first = "seed " + seed + ": saved at pulse " + at + ", after " + (total - at) + " more pulses the loaded copy's hash differs (standing " + a.S.Standing + " vs " + b.S.Standing + ")";
            if (first == null && b != null && !a.W.RoomDl.SequenceEqual(b.W.RoomDl)) first = "seed " + seed + ": receivers credited differently after load";
        }
        Row("L1_RANDOM_SHEET_SAVE_LOAD_CONTINUES_IDENTICAL", SHEET, "random", first == null ? "PASS" : "FAIL", cases,
            first ?? "400 random worlds saved at a random pulse and loaded: the loaded copy and the uninterrupted run, fed the same later spills, end with the same state hash and the same receiver credits");
    }

    static void SheetPreviewAndOrder()
    {
        int cases = 0; string first = null;
        for (int seed = 1; seed <= 1500 && first == null; seed++)
        {
            var g = RandomRig(seed);
            for (int i = 0; i < 6; i++) { ResolveSpills(g.S, g.W, g.P, new List<SpillOffer> { RandomOffer(g) }); Pulse(g.S, g.W, g.P, null); }
            var o = RandomOffer(g);
            int pre = PreviewSpill(g.S, g.W, g.P, o);
            var copy = Load(Save(g.S));
            int got = ResolveSpills(copy, g.W, g.P, new List<SpillOffer> { o })[0];
            cases++;
            if (pre != got) { first = "seed " + seed + ": PreviewSpill " + pre + " but ResolveSpills accepted " + got + " (lips " + string.Join(",", o.LipNearestFirst) + ", " + o.AmountDl + " dL)"; break; }
            // order independence
            var offers = new List<SpillOffer> { RandomOffer(g), RandomOffer(g), RandomOffer(g) };
            var s1 = Load(Save(g.S)); var s2 = Load(Save(g.S));
            int[] a1 = ResolveSpills(s1, g.W, g.P, offers);
            var rev = new List<SpillOffer>(offers); rev.Reverse();
            int[] a2 = ResolveSpills(s2, g.W, g.P, rev);
            cases++;
            if (Hash(s1) != Hash(s2) || a1[0] != a2[2] || a1[1] != a2[1] || a1[2] != a2[0])
                first = "seed " + seed + ": three offers resolved in two caller orders give different states or acceptances";
        }
        Row("L1_RANDOM_SHEET_PREVIEW_AND_ORDER", SHEET, "random", first == null ? "PASS" : "FAIL", cases,
            first ?? "PreviewSpill equals what ResolveSpills then accepts for the same offer; three offers in two caller orders give the same state and per-offer acceptance");
    }

    static Rig Basin(int w, int h, int soak, int evap)
    {
        var world = new World(w, h);
        for (int z = 0; z < h; z++)
            for (int x = 0; x < w; x++)
            {
                int c = z * w + x;
                world.Kinds[c] = x == 0 || z == 0 || x == w - 1 || z == h - 1 ? Kind.Blocked : Kind.Open;
                world.SoakMilliDl[c] = soak; world.EvapMilliDl[c] = evap;
            }
        return new Rig { S = new State(w, h, 12345u), W = world, P = new Params(), R = new Random(1), Fluids = 1 };
    }

    static void SheetLevelAndSpread()
    {
        // a walled 8x8 yard (6x6 inside), no losses: a spill at one corner spreads over the yard and lies level
        var g = Basin(8, 8, 0, 0);
        int inner = 36; int vol = inner * 5 * DlPerCm;
        var lips = new List<int>();
        for (int z = 1; z < 7; z++) for (int x = 1; x < 7; x++) lips.Add(z * 8 + x);
        int acc = ResolveSpills(g.S, g.W, g.P, new List<SpillOffer> { new SpillOffer { LipNearestFirst = lips.ToArray(), AmountDl = vol, Fluid = 1, From = Source.Pump } })[0];
        for (int i = 0; i < 400; i++) Pulse(g.S, g.W, g.P, null);
        long lo = long.MaxValue, hi = long.MinValue; int wet = 0;
        foreach (int c in lips)
        {
            if (g.S.Dl[c] > 0) wet++;
            if (g.S.Dl[c] <= g.P.RetentionDl || g.S.Dl[c] >= g.P.SheetCapDl) continue;
            long surf = g.S.Dl[c] + Relief(g.S.Salt, c, g.P.ReliefDl);
            lo = Math.Min(lo, surf); hi = Math.Max(hi, surf);
        }
        bool ok = acc == vol && wet == inner && hi - lo <= 1 && g.S.LedgerCloses;
        Row("L1_FIXED_SHEET_FILLS_YARD_AND_LIES_LEVEL", SHEET, "fixed", ok ? "PASS" : "FAIL", 1,
            "5 cm over a walled 6x6 yard poured nearest-first from one corner (accepted " + acc + " of " + vol + " dL), 400 pulses, no losses: " + wet + " of " + inner + " squares wet, surface (dL + relief) spread " + (hi - lo) + " dL over the unclamped squares (level means <= 1)");

        // with soak and evaporation the sheet soaks in and dries to nothing, every dL disclosed
        var d = Basin(6, 6, 900, 300);
        var l2 = new List<int>(); for (int z = 1; z < 5; z++) for (int x = 1; x < 5; x++) l2.Add(z * 6 + x);
        ResolveSpills(d.S, d.W, d.P, new List<SpillOffer> { new SpillOffer { LipNearestFirst = l2.ToArray(), AmountDl = 16 * 2 * DlPerCm, Fluid = 1, From = Source.Rain } });
        int pulses = 0; while (d.S.WetCount > 0 && pulses < 100000) { Pulse(d.S, d.W, d.P, null); pulses++; }
        bool ok2 = d.S.WetCount == 0 && d.S.LedgerCloses && d.S.Soaked + d.S.Evaporated == d.S.TotalIn;
        Row("L1_FIXED_SHEET_SOAKS_IN_AND_DRIES", SHEET, "fixed", ok2 ? "PASS" : "FAIL", 1,
            "2 cm over 4x4 squares with soak 0.9 dL and evaporation 0.3 dL a pulse: dry after " + pulses + " pulses; soaked " + d.S.Soaked + " + evaporated " + d.S.Evaporated + " == poured " + d.S.TotalIn);
    }

    static void SheetCropWeek()
    {
        float pulseDefault = EnvF("pulseIntervalTicks", 250f);
        int stored = (int)EnvF("cropDrownPulses", 1680);
        var bad = new List<string>(); int cases = 0;
        // the shipped days slider (0.5..30 in 0.5) through the shipped flow-pulse range (60..2500)
        for (float days = 0.5f; days <= 30.001f; days += 0.5f)
        {
            int pulsesAtBase = Math.Max(1, PulsesFor((int)Math.Round(days * 60000), CropDelayBasePulseTicks));
            foreach (int pt in new[] { 60, 61, 100, 137, 250, 251, 500, 999, 1000, 2500 })
            {
                cases++;
                int kp = CropKillPulsesFor(pulsesAtBase, pt);
                long t = (long)kp * pt, want = (long)pulsesAtBase * CropDelayBasePulseTicks;
                if (t < want || t >= want + pt) bad.Add(days + " d at " + pt + " ticks: " + kp + " pulses = " + t + " ticks, want [" + want + ", " + (want + pt) + ")");
            }
        }
        int shipped = CropKillPulsesFor(stored, (int)pulseDefault);
        bool weekOk = (long)shipped * (int)pulseDefault >= 7 * 60000 && (long)shipped * (int)pulseDefault < 7 * 60000 + pulseDefault;
        if (!weekOk) bad.Add("shipped " + stored + " stored pulses at " + pulseDefault + " ticks is " + (long)shipped * (int)pulseDefault + " ticks, not one week");
        Row("L1_SWEEP_SHEET_CROP_DELAY_IS_WALL_TIME", SHEET, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? "days slider 0.5..30 x flow pulse 60..2500 ticks: the crop delay stays the chosen time, rounded up to one pulse; shipped default " + stored + " stored pulses at " + pulseDefault + " ticks = one week"
                           : string.Join("; ", bad.Take(6)));

        // standing sheet on one crop square: drowns at exactly the delay; a film never stands; a young crop is spared
        var g = Basin(3, 3, 0, 0);
        g.P.CropKillPulses = 50;
        ResolveSpills(g.S, g.W, g.P, new List<SpillOffer> { new SpillOffer { LipNearestFirst = new[] { 4 }, AmountDl = 5 * DlPerCm, Fluid = 1, From = Source.Pump } });
        var rep = new PulseReport(); int firstDrown = -1;
        for (int i = 1; i <= 60; i++) { Pulse(g.S, g.W, g.P, rep); if (firstDrown < 0 && rep.CropDrowning.Any(x => x.cell == 4)) firstDrown = i; }
        var f = Basin(3, 3, 0, 0); f.P.CropKillPulses = 50;
        ResolveSpills(f.S, f.W, f.P, new List<SpillOffer> { new SpillOffer { LipNearestFirst = new[] { 4 }, AmountDl = (int)(2.5 * DlPerCm), Fluid = 1, From = Source.Pump } });
        bool filmStood = false;
        for (int i = 1; i <= 120; i++) { Pulse(f.S, f.W, f.P, rep); if (rep.CropDrowning.Count > 0) filmStood = true; }
        bool young = !CropDrowns(1000, 49 * 250 + 249, 250, g.P) && CropDrowns(1000, 50 * 250, 250, g.P) && !CropDrowns(49, 1_000_000, 250, g.P);
        bool ok = firstDrown == 50 && !filmStood && young;
        Row("L1_FIXED_SHEET_CROP_DROWNS_AT_THE_DELAY", SHEET, "fixed", ok ? "PASS" : "FAIL", 3,
            "5 cm standing on one square, delay 50 pulses: first reported drowning at pulse " + firstDrown + " (want 50); 2.5 cm poured on dry ground (a film) reported as standing: " + filmStood + " (want false); a crop younger than the delay, or a square stood 49 pulses, spared: " + young);
    }

    static void SheetIceDoorSwitches()
    {
        // ice: freezes below 0 °C keeping every dL, neither flows nor soaks; thaws only 1 °C above
        var g = Basin(5, 3, 500, 0);
        for (int c = 0; c < 15; c++) g.W.TempDeciC[c] = -50;
        ResolveSpills(g.S, g.W, g.P, new List<SpillOffer> { new SpillOffer { LipNearestFirst = new[] { 6 }, AmountDl = 10 * DlPerCm, Fluid = 1, From = Source.Rain } });
        for (int i = 0; i < 30; i++) Pulse(g.S, g.W, g.P, null);
        bool iced = g.S.Tiers[6] == Tier.Ice && g.S.Dl[6] == 10 * DlPerCm && g.S.Dl[7] == 0;
        for (int c = 0; c < 15; c++) g.W.TempDeciC[c] = 5;
        Pulse(g.S, g.W, g.P, null);
        bool stillIce = g.S.Tiers[6] == Tier.Ice;
        for (int c = 0; c < 15; c++) g.W.TempDeciC[c] = 10;
        Pulse(g.S, g.W, g.P, null);
        bool thawed = g.S.Tiers[6] != Tier.Ice && g.S.LedgerCloses;
        Row("L1_FIXED_SHEET_FREEZES_AND_THAWS", SHEET, "fixed", iced && stillIce && thawed ? "PASS" : "FAIL", 3,
            "10 cm at -5 C over soaking ground: ice keeping every dL, nothing moved (" + iced + "); at +0.5 C still ice (" + stillIce + "); at +1.0 C thawed, ledger closed (" + thawed + ")");

        // a door at 0 % seals; at 5 % it leaks slowly
        foreach (int leak in new[] { 0, 50 })
        {
            var d = Basin(7, 3, 0, 0);
            d.W.Kinds[10] = Kind.Door; d.P.DoorLeakPermille = leak;
            ResolveSpills(d.S, d.W, d.P, new List<SpillOffer> { new SpillOffer { LipNearestFirst = new[] { 8, 9 }, AmountDl = 2 * 20 * DlPerCm, Fluid = 1, From = Source.Pump } });
            int p1 = 0; for (; p1 < 2000 && d.S.Dl[11] == 0; p1++) Pulse(d.S, d.W, d.P, null);
            bool ok = leak == 0 ? d.S.Dl[10] == 0 && d.S.Dl[11] == 0 && d.S.Dl[12] == 0 : d.S.Dl[11] > 0 && p1 > 3;
            Row("L1_FIXED_SHEET_DOOR_LEAK_" + (leak == 0 ? "SEALED" : "SLOW"), SHEET, "fixed", ok ? "PASS" : "FAIL", 1,
                "a door between a 20 cm pool and dry ground, leak " + leak / 10 + " %: door square " + d.S.Dl[10] + " dL, far side " + d.S.Dl[11] + " dL after " + p1 + " pulses (" + (leak == 0 ? "want both 0 for good" : "want a slow leak, more than 3 pulses") + ")");
        }

        // switches: AcceptsSpill over every combination (master/inflow off, water/other, other-liquids switch, force)
        int bad = 0, cases = 0;
        for (int m = 0; m < 64; m++)
        {
            bool spills = (m & 1) != 0, depth = (m & 2) != 0, has = (m & 4) != 0, water = (m & 8) != 0, other = (m & 16) != 0, force = (m & 32) != 0;
            bool want = depth && has && (force || (spills && (water || other)));
            cases++;
            if (AcceptsSpill(spills, depth, has, water, other, force) != want) bad++;
        }
        Row("L1_SWEEP_SHEET_SWITCHES_ACCEPT_SPILL", SHEET, "sweep", bad == 0 ? "PASS" : "FAIL", cases,
            bad == 0 ? "64 switch combinations: a spill enters only with the depth engine, a known liquid, and (forced or (the master and inflow switch on, and water or 'every liquid spills' on))" : bad + " combinations wrong");

        // default-on check: the bar's experience as shipped
        float master = EnvF("sheetOverflowEnabled", -1f);
        Row("L1_INFO_SHEET_MASTER_SWITCH_SHIPS_OFF", SHEET, "info", "INFO", 1,
            "RM_SheetSettings.sheetOverflowEnabled ships " + (master > 0.5f ? "ON" : master < -0.5f ? "UNREAD" : "OFF") + "; its comment says the default stays OFF until the feature's live acceptance signs it off (owner card D7: on once validated). With it off, a fresh game shows none of inv_overflow_sheet's overspill. Lane 2 weighs whether this blocks the bar.");
    }

    static void SheetSettingsSweep()
    {
        int cases = 0; string first = null;
        foreach (float ret in new[] { 0.5f, 1f, 2.5f, 5f })
            foreach (int cap in new[] { 5, 20, 50, 100 })
                foreach (int sw in new[] { 1, 3, 6 })
                    foreach (int door in new[] { 0, 5, 50 })
                        foreach (int maxWet in new[] { 1, 500, 20000 })
                        {
                            var p = new Params
                            {
                                RetentionDl = Math.Max(1, (int)Math.Round(ret * DlPerCm)), SheetCapDl = Math.Max(DlPerCm, cap * DlPerCm),
                                SweepsPerPulse = sw, DoorLeakPermille = door * 10, MaxWetCells = maxWet
                            };
                            p.MinReceiveDl = Math.Max(1, p.RetentionDl / 2);
                            for (int seed = 1; seed <= 6 && first == null; seed++)
                            {
                                cases++;
                                string bad = RunRandom(seed * 131 + cap + sw, 60, p, out _);
                                if (bad != null) first = "retention " + ret + " cm, cap " + cap + " cm, sweeps " + sw + ", door " + door + " %, max wet " + maxWet + ", seed " + (seed * 131 + cap + sw) + ": " + bad;
                            }
                        }
        Row("L1_SWEEP_SHEET_SETTINGS_KEEP_THE_LEDGER", SHEET, "sweep", first == null ? "PASS" : "FAIL", cases,
            first ?? "retention 0.5..5 cm x cap 5..100 cm x sweeps 1..6 x door 0..50 % x max wet squares 1..20000 (the shipped slider ends, SyncParams' conversion), 6 random 60-op runs each: every invariant of L1_RANDOM_SHEET_LEDGER_AND_INVARIANTS holds");
    }

    static void SheetCreepingFire()
    {
        // vanilla grass fire: 0.8 x 1/8 per 150 ticks => one burning square lights a given neighbour in ~1500 ticks at speed 1
        var bad = new List<string>(); int cases = 0;
        foreach (int chk in new[] { 30, 60, 150, 250, 500, 1000 })
            foreach (float sp in new[] { 0.25f, 0.5f, 1f, 2f })
            {
                cases++;
                float p = RM_SheetFluidMath.CreepingCatchChance(chk, sp);
                float t = RM_SheetFluidMath.CreepingTicksPerNeighbour(chk, sp);
                float want = p >= 1f ? chk : 1500f / sp;
                if (p < 0f || p > 1f || Math.Abs(t - want) > want * 0.001f) bad.Add("check " + chk + ", speed " + sp + ": p " + p + ", ticks " + t + " (want " + want + ")");
            }
        float tz = RM_SheetFluidMath.CreepingTicksPerNeighbour(0, 1f);
        Row("L1_FIXED_SHEET_CREEPING_FIRE_PACE", new[] { "inv_overflow_sheet", "canal_fire_burns_back" }, "fixed", bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? "creeping spills (tar) light a given neighbour in 1500/speed ticks at any check length, vanilla grass-fire pace; chance stays in [0, 1]. A zero check length gives " + tz + " ticks (callers must not pass 0; lane 2 reads them)"
                           : string.Join("; ", bad.Take(6)));
    }

    // ───────────────────────────── converters ─────────────────────────────

    static void Converters()
    {
        float mDefault = EnvF("converterRateMultiplier", 1f);
        // rate fidelity: a machine with input and room to spare runs batches worth its daily rate, at every multiplier
        var bad = new List<string>(); int cases = 0;
        var r = new Random(20261127);
        for (float m = 0.1f; m <= 5.0001f; m += 0.1f)
            for (int t = 0; t < 30; t++)
            {
                int inU = r.Next(1, 400), outU = r.Next(1, 400);
                float perDay = r.Next(1, 20000), tier = (float)(0.25 + r.NextDouble() * 2);
                float per = RM_ConversionMath.BudgetPerRareTick(perDay, tier, m, 1f);
                float accrued = 0; long batches = 0; int days = 10;
                for (int k = 0; k < RM_ConversionMath.RareTicksPerDay * days; k++)
                {
                    accrued += per;
                    float capped = RM_ConversionMath.CapAccrued(accrued, inU, per);
                    float clipped = RM_ConversionMath.ClippedIncome(accrued, capped, per);
                    int n = RM_ConversionMath.Batches(capped, inU, outU, int.MaxValue / 2, -1);
                    batches += n;
                    accrued = capped - n * inU + clipped;
                }
                cases++;
                double income = (double)per * RM_ConversionMath.RareTicksPerDay * days, used = (double)batches * inU;
                if (used > income + 1e-3 * income + 1 || used < income - (per + 2.0 * inU) - 1e-3 * income)
                    bad.Add("x" + m.ToString("0.0") + " in " + inU + " out " + outU + " rate " + perDay + "/d tier " + tier.ToString("0.00") + ": used " + used.ToString("0") + " of income " + income.ToString("0"));
            }
        Row("L1_SWEEP_CONVERTER_RUNS_AT_ITS_RATE", CONV, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? "converter multiplier 0.1..5 (shipped " + mDefault + ") x 30 random recipes and rates, 10 days of rare ticks with input and room to spare, budget capped and clipped income carried as the kernel documents: input used within one tick's income plus two batches of the 10-day income, never above it"
                           : bad.Count + " of " + cases + " off; first: " + string.Join("; ", bad.Take(3)));

        // idle cap: a machine dry for a week bursts at most one tick's income plus one batch when filled
        bad.Clear(); int c2 = 0;
        for (int t = 0; t < 2000; t++)
        {
            int inU = r.Next(1, 400); float per = (float)(r.NextDouble() * 900 + 0.01);
            float accrued = 0;
            for (int k = 0; k < RM_ConversionMath.RareTicksPerDay * 7; k++)
            {
                accrued += per;
                float capped = RM_ConversionMath.CapAccrued(accrued, inU, per);
                float clipped = RM_ConversionMath.ClippedIncome(accrued, capped, per);
                int n0 = RM_ConversionMath.Batches(capped, inU, 1, 0, -1); // no input on hand
                accrued = capped - n0 * inU + clipped;
            }
            accrued += per;
            float cap2 = RM_ConversionMath.CapAccrued(accrued, inU, per);
            int burst = RM_ConversionMath.Batches(cap2, inU, 1, int.MaxValue / 2, -1);
            c2++;
            double bound = Math.Floor((per > inU ? per + inU : inU) / inU + 1e-4);
            if (burst > bound) bad.Add("in " + inU + ", income " + per.ToString("0.00") + "/tick: burst " + burst + " batches, bound " + bound);
        }
        Row("L1_RANDOM_CONVERTER_IDLE_WEEK_DOES_NOT_BURST", CONV, "random", bad.Count == 0 ? "PASS" : "FAIL", c2,
            bad.Count == 0 ? "2000 random recipes left dry a week, then filled: the first tick runs no more than one tick's income plus one batch (seed 20261127)" : string.Join("; ", bad.Take(3)));

        // batches bounded by input, room; invalid recipes run nothing; rotation is fair; a blocked input never starves the rest
        int c3 = 0; string f3 = null;
        for (int t = 0; t < 20000 && f3 == null; t++)
        {
            float acc = (float)(r.NextDouble() * 5000 - 50); int inU = r.Next(-1, 300), outU = r.Next(-1, 300), have = r.Next(0, 3000), room = r.Next(-1, 3000);
            int n = RM_ConversionMath.Batches(acc, inU, outU, have, room);
            c3++;
            if (n < 0 || (inU < 1 || outU < 1) && n != 0 || inU >= 1 && n * (long)inU > have || n > 0 && inU >= 1 && n * (long)inU > acc + 1 || room >= 0 && outU >= 1 && n * (long)outU > room)
                f3 = "Batches(" + acc + ", in " + inU + ", out " + outU + ", have " + have + ", room " + room + ") = " + n;
        }
        for (int t = 0; t < 5000 && f3 == null; t++)
        {
            int nIn = r.Next(1, 6); var b = new List<int>(); for (int i = 0; i < nIn; i++) b.Add(r.Next(3) == 0 ? 0 : r.Next(1, 4));
            int runnable = b.Count(x => x > 0); var seen = new HashSet<int>(); int last = -1;
            for (int k = 0; k < nIn; k++) { last = RM_ConversionMath.NextRunnable(b, last); if (last >= 0) seen.Add(last); }
            c3++;
            if (seen.Count != runnable || (runnable == 0) != (RM_ConversionMath.FirstRunnable(b) < 0)) f3 = "rotation over [" + string.Join(",", b) + "] reached " + seen.Count + " of " + runnable + " runnable inputs";
            var capped = new List<float>(); for (int i = 0; i < nIn; i++) capped.Add((float)r.NextDouble() * 500);
            float kept = RM_ConversionMath.AccruedAfterPick(1e9f, capped, -1);
            if (kept != capped.Max()) f3 = "nothing ran: kept " + kept + ", largest cap " + capped.Max();
        }
        bool sun = RM_ConversionMath.SunFactor(0.5f, false) == 1f && RM_ConversionMath.SunFactor(0.49f, false) == 0f && RM_ConversionMath.SunFactor(1f, true) == 0f;
        if (!sun) f3 = f3 ?? "solar still works at night or under a roof";
        Row("L1_RANDOM_CONVERTER_BATCH_BOUNDS_AND_ROTATION", CONV, "random", f3 == null ? "PASS" : "FAIL", c3,
            f3 ?? "20000 random Batches calls never exceed budget, input or room and run nothing for a bad recipe; 5000 random input sets: rotation reaches every runnable input once per round, none when none can run, and a blocked round keeps the largest cap; a solar still runs only in daylight, unroofed");
    }

    // ───────────────────────────── thirst, bottles ─────────────────────────────

    static void Thirst()
    {
        var bad = new List<string>();
        float rate = EnvF("thirstRateMultiplier", 1f);
        float fall = RM_ThirstMath.FallPerDay(rate, 1f, false, false);
        if (Math.Abs(1f / fall - 1.25f) > 0.01f) bad.Add("full to empty " + (1f / fall) + " d, ruled about 1.25");
        if (Math.Abs(RM_ThirstMath.HeatFactor(100f, 26f, true) - 3f) > 1e-5f || RM_ThirstMath.HeatFactor(100f, 26f, false) != 1f || RM_ThirstMath.HeatFactor(20f, 26f, true) != 1f)
            bad.Add("heat factor not capped 3x / not off with its switch / not 1 in comfort");
        if (Math.Abs(RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Potable, true) - 0.5f) > 1e-5f) bad.Add("a 1.5 L bottle restores " + RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Potable, true));
        // death after empty: dehydration at zero thirst, need-interval steps
        float sev = 0; int steps = 0; while (sev < RM_ThirstMath.DehydrationLethal && steps < 1000000) { sev += RM_ThirstMath.DehydrationDelta(0f, RM_ThirstMath.NeedIntervalTicks); steps++; }
        float daysToDeath = steps * RM_ThirstMath.NeedIntervalTicks / RM_ThirstMath.TicksPerDay;
        if (daysToDeath < 2.5f || daysToDeath > 3.6f) bad.Add("death " + daysToDeath + " d after empty, ruled about 3");
        if (RM_ThirstMath.DehydrationDelta(0.5f, 150) >= 0 || RM_ThirstMath.DehydrationDelta(0.2f, 150) != 0) bad.Add("dehydration does not heal above 0.3 / moves between");
        if (RM_ThirstMath.OrphanDehydrationDelta(false, 60000) >= 0 || RM_ThirstMath.OrphanDehydrationDelta(true, 60000) != 0) bad.Add("dehydration with thirst off does not heal");
        Row("L1_FIXED_THIRST_RULED_NUMBERS", THIRST, "fixed", bad.Count == 0 ? "PASS" : "FAIL", 8,
            bad.Count == 0 ? "at the shipped rate x" + rate + ": full to empty in " + (1f / fall).ToString("0.00") + " d; heat up to 3x and off with its switch; a 1.5 L bottle restores 0.5; dehydration kills " + daysToDeath.ToString("0.00") + " d after empty (ruled about 3) and heals with thirst switched off" : string.Join("; ", bad));

        // the rate slider 0.25..3, every switch off included
        bad.Clear(); int cases = 0;
        for (float m = 0.25f; m <= 3.0001f; m += 0.05f)
            foreach (bool heat in new[] { false, true })
                foreach (bool hard in new[] { false, true })
                    foreach (bool asleep in new[] { false, true })
                    {
                        cases++;
                        float hf = RM_ThirstMath.HeatFactor(45f, 26f, heat);
                        float f = RM_ThirstMath.FallPerDay(m, hf, hard, asleep);
                        float want = 0.8f * m * hf * (hard ? 1.3f : 1f) * (asleep ? 0.5f : 1f);
                        float perInt = RM_ThirstMath.FallPerInterval(f);
                        if (Math.Abs(f - want) > 1e-4f || Math.Abs(perInt * 400f - f) > 1e-4f || f <= 0) bad.Add("x" + m + " heat " + heat + " hard " + hard + " asleep " + asleep + ": " + f + " (want " + want + ")");
                        float dw = RM_ThirstMath.DaysOfWater(30f, 3, m);
                        if (Math.Abs(dw * 3 * 0.8f * m - 10f) > 1e-3f) bad.Add("days of water off at x" + m);
                    }
        Row("L1_SWEEP_THIRST_RATE_SLIDER", THIRST, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? "rate 0.25..3 x heat on/off x hard labour x asleep: the fall is 0.8 x rate x heat x 1.3 x 0.5 per day, 400 need intervals a day; days-of-water readout agrees" : string.Join("; ", bad.Take(4)));

        // drink gates: every use class x level x humanlike x native x salt break x last-resort switch
        bad.Clear(); cases = 0;
        foreach (RM_DrinkUse use in Enum.GetValues(typeof(RM_DrinkUse)))
            foreach (float lvl in new[] { 0f, 0.004f, 0.006f, 0.05f, 0.5f, 1f })
                for (int m = 0; m < 16; m++)
                {
                    bool human = (m & 1) != 0, native = (m & 2) != 0, brk = (m & 4) != 0, lr = (m & 8) != 0;
                    bool want = use == RM_DrinkUse.Potable || use != RM_DrinkUse.Never && (!human ? native : use == RM_DrinkUse.LastResort ? lr && lvl <= 0.005f : brk);
                    cases++;
                    if (RM_ThirstMath.MayDrink(use, lvl, human, native, brk, lr) != want) bad.Add(use + " at " + lvl + " human " + human + " native " + native + " break " + brk + " lastResort " + lr);
                }
        // quality off: every drinkable counts as potable, hydrates fully
        foreach (RM_WaterQuality q in Enum.GetValues(typeof(RM_WaterQuality)))
        {
            cases++;
            if (RM_ThirstMath.HydrateFactor(q, false) != 1f || RM_ThirstMath.Effective(q, false) != RM_WaterQuality.Potable) bad.Add("quality effects off still marks " + q);
            if (RM_ThirstMath.HydrateFactor(q, true) > 1f || RM_ThirstMath.HydrateFactor(q, true) <= 0f) bad.Add(q + " hydrates " + RM_ThirstMath.HydrateFactor(q, true));
        }
        // salt break gate
        for (int m = 0; m < 32; m++)
        {
            float lvl = (m & 1) != 0 ? 0.05f : 0.2f; bool sp = (m & 2) != 0, pr = (m & 4) != 0, sr = (m & 8) != 0;
            cases++;
            if (RM_ThirstMath.SaltBreakCan(lvl, sp, pr, sr) != (lvl < 0.1f && !sp && !pr && sr)) bad.Add("salt break gate at " + lvl);
        }
        // awkward access per the owner's Q1: terrain never, caravan/container always, bottle/tank only away from home
        foreach (RM_DrinkSource src in Enum.GetValues(typeof(RM_DrinkSource)))
            foreach (bool home in new[] { false, true })
            {
                cases++;
                bool want = src == RM_DrinkSource.Terrain ? false : src == RM_DrinkSource.Caravan || src == RM_DrinkSource.Container ? true : !home;
                if (RM_ThirstMath.Awkward(src, home) != want) bad.Add("awkward " + src + " at home " + home);
            }
        Row("L1_SWEEP_THIRST_DRINK_GATES", THIRST, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? "every use class x thirst level x humanlike x native x salt break x last-resort switch: potable always, never never, last resort only when empty and allowed, salt only in its break, animals any native water; quality off makes every drinkable potable; salt break gate; awkward access as the owner ruled" : string.Join("; ", bad.Take(6)));

        // pick order is a strict order (random), reserve, bottle target, categories
        bad.Clear(); cases = 0; var r = new Random(4242);
        var uses = (RM_DrinkUse[])Enum.GetValues(typeof(RM_DrinkUse)); var qs = (RM_WaterQuality[])Enum.GetValues(typeof(RM_WaterQuality));
        for (int t = 0; t < 30000; t++)
        {
            var a = (uses[r.Next(4)], r.Next(2) == 0, qs[r.Next(5)], (float)r.Next(0, 5));
            var b = (uses[r.Next(4)], r.Next(2) == 0, qs[r.Next(5)], (float)r.Next(0, 5));
            var c = (uses[r.Next(4)], r.Next(2) == 0, qs[r.Next(5)], (float)r.Next(0, 5));
            Func<(RM_DrinkUse, bool, RM_WaterQuality, float), (RM_DrinkUse, bool, RM_WaterQuality, float), bool> B = (x, y) => RM_ThirstMath.BetterPick(x.Item1, x.Item2, x.Item3, x.Item4, y.Item1, y.Item2, y.Item3, y.Item4);
            cases++;
            if (B(a, a)) bad.Add("a pick better than itself");
            if (B(a, b) && B(b, a)) bad.Add("two picks each better than the other");
            if (B(a, b) && B(b, c) && !B(a, c)) bad.Add("pick order not transitive");
            if (bad.Count > 0) break;
        }
        float reserve = EnvF("drinkingReserveLitres", 200f);
        int resU = (int)(reserve * 10);
        for (int t = 0; t < 5000; t++)
        {
            int av = r.Next(0, 10000), rs = r.Next(-5, 5000); bool pot = r.Next(2) == 0;
            int sp = RM_ThirstMath.Spendable(av, rs, pot);
            cases++;
            if (sp < 0 || sp > av || pot && rs > 0 && av - sp < Math.Min(av, rs)) { bad.Add("Spendable(" + av + ", " + rs + ", " + pot + ") = " + sp); break; }
        }
        int perCol = (int)EnvF("filledBottlesPerColonist", 3);
        if (RM_ThirstMath.BottleDeficit(perCol, 0, 0) != perCol || RM_ThirstMath.BottleDeficit(0, 5, 0) != 0 || RM_ThirstMath.BottleDeficit(3, 4, 20) != 0 || RM_ThirstMath.BottleDeficit(3, 4, 5) != 7)
            bad.Add("bottle target arithmetic");
        if (RM_ThirstMath.Category(0f) != 3 || RM_ThirstMath.Category(0.05f) != 2 || RM_ThirstMath.Category(0.2f) != 1 || RM_ThirstMath.Category(0.3f) != 0) bad.Add("need categories");
        Row("L1_RANDOM_THIRST_PICK_ORDER_RESERVE_TARGET", THIRST, "random", bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? "30000 random triples: the drink pick is a strict order (use class, then not awkward, then quality, then nearer); 5000 random draws never touch the potable reserve (shipped " + reserve + " L = " + resU + " units); bottles-to-fill = target x colonists - held (shipped target " + perCol + "), 0 at target 0; need categories (seed 4242)" : string.Join("; ", bad.Take(4)));

        // container looks: four styles, names round-trip, stacking keeps looks apart
        bad.Clear(); cases = 0;
        if (RM_ContainerStyleMath.Looks.Length != 4) bad.Add("looks " + RM_ContainerStyleMath.Looks.Length);
        foreach (string s in RM_ContainerStyleMath.Sizes)
            foreach (string l in RM_ContainerStyleMath.Looks)
            {
                cases++;
                if (RM_ContainerStyleMath.LookOfStyleDefName(RM_ContainerStyleMath.StyleDefName(s, l)) != l) bad.Add(s + "/" + l + " does not round-trip");
            }
        foreach (string n in new[] { null, "", "RM_", "RM_Bottle", "RM_Cup_Modern", "RM_Bottle_Neon", "XX_Bottle_Modern", "RM__Modern" })
        {
            cases++;
            if (RM_ContainerStyleMath.LookOfStyleDefName(n) != null) bad.Add("'" + n + "' read as a look");
        }
        foreach (string tl in new[] { "Undefined", "Animal", "Neolithic", "Medieval", "Industrial", "Spacer", "Ultra", "Archotech", null, "Weird" })
        {
            cases++;
            if (!RM_ContainerStyleMath.IsLook(RM_ContainerStyleMath.LookForTech(tl))) bad.Add("tech " + tl + " has no look");
        }
        cases += 3;
        if (!RM_ContainerStyleMath.MayStack("Modern", null) || RM_ContainerStyleMath.MayStack(null, "Modern") || RM_ContainerStyleMath.MayStack("Modern", "Scrapper")) bad.Add("stacking rule");
        Row("L1_FIXED_CONTAINER_FOUR_STYLES", THIRST, "fixed", bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? "four looks for bottle, bucket and barrel; each style name round-trips to its look and nothing else reads as one; every tech level wears a look; an unstyled stack joins a styled one, never the reverse, and two looks never merge" : string.Join("; ", bad));
    }

    // ───────────────────────────── drilling ─────────────────────────────

    static void Drilling()
    {
        var bad = new List<string>(); int cases = 0;
        foreach (bool sv in new[] { false, true })
            foreach (bool hy in new[] { false, true })
                foreach (float res in new[] { -1f, 0f, 0.001f, 50f })
                {
                    cases++;
                    var v = RM_DrillSurveyMath.Placement(sv, hy, res);
                    var want = !sv ? RM_DrillSurveyMath.Verdict.Allowed : !hy ? RM_DrillSurveyMath.Verdict.NoYield : res <= 0 ? RM_DrillSurveyMath.Verdict.Spent : RM_DrillSurveyMath.Verdict.Allowed;
                    if (v != want) bad.Add("Placement(" + sv + ", " + hy + ", " + res + ") = " + v);
                }
        // why-not: exhaustive over the twelve facts; one answer; None only when every condition holds; agrees with placement
        for (int m = 0; m < 4096; m++)
            foreach (float res in new[] { 0f, 10f })
            {
                var s = new RM_DrillSurveyMath.State
                {
                    settingOn = (m & 1) != 0, switchedOn = (m & 2) != 0, needsPower = (m & 4) != 0, powered = (m & 8) != 0,
                    surveyed = (m & 16) != 0, hasYield = (m & 32) != 0, hasCanalForm = (m & 64) != 0, fluidAllowed = (m & 128) != 0,
                    outletDug = (m & 256) != 0, outletOtherLiquid = (m & 512) != 0, outletBrimming = (m & 1024) != 0, reserve = res
                };
                cases++;
                var w = RM_DrillSurveyMath.WhyNot(s);
                bool allOk = s.settingOn && s.switchedOn && (!s.needsPower || s.powered) && s.surveyed && s.hasYield && s.hasCanalForm && s.fluidAllowed
                             && s.outletDug && !s.outletOtherLiquid && !s.outletBrimming && s.reserve > 0;
                if ((w == RM_DrillSurveyMath.Block.None) != allOk) bad.Add("WhyNot " + w + " with all-ok " + allOk + " (mask " + m + ", reserve " + res + ")");
                if (!s.settingOn && w != RM_DrillSurveyMath.Block.DisabledInSettings) bad.Add("settings off reads " + w);
                if (w == RM_DrillSurveyMath.Block.NoSubsurface && RM_DrillSurveyMath.Placement(s.surveyed, s.hasYield, s.reserve) != RM_DrillSurveyMath.Verdict.NoYield) bad.Add("why-not NoSubsurface but placement " + RM_DrillSurveyMath.Placement(s.surveyed, s.hasYield, s.reserve));
                if (bad.Count > 6) break;
            }
        Row("L1_SWEEP_DRILL_PLACEMENT_AND_WHY_NOT", DRILL, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? "placement refuses a surveyed dry or spent square and allows unsurveyed ground (owner card 2026-10-22); the why-not answer over all 4096 x 2 fact sets is None exactly when every condition holds, 'disabled in settings' first, and agrees with placement" : string.Join("; ", bad.Take(6)));

        // spent units: what landed, never what was asked; conservation over a random run
        bad.Clear(); cases = 0; var r = new Random(777);
        for (int t = 0; t < 20000; t++)
        {
            long before = r.Next(0, 40000), after = before + r.Next(-500, 4000); long dlPer = r.Next(1, 2) == 1 ? RM_Volume.UnitsPerLevel : r.Next(-2, 5000);
            float upl = (float)(r.NextDouble() * 6);
            float got = RM_DrillSurveyMath.SpentUnits(before, after, dlPer, upl);
            double want = after <= before || dlPer <= 0 ? 0 : (after - before) / (double)dlPer * upl;
            cases++;
            if (got < 0 || Math.Abs(got - want) > 1e-3 * Math.Max(1, want)) { bad.Add("SpentUnits(" + before + ", " + after + ", " + dlPer + ", " + upl + ") = " + got + ", want " + want); break; }
        }
        Row("L1_RANDOM_DRILL_CHARGES_WHAT_LANDED", DRILL, "random", bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? "20000 random drill writes: the reserve is charged the decilitres that landed in the outlet, in level units, never negative (seed 777)" : bad[0]);
    }

    // ───────────────────────────── sprinklers ─────────────────────────────

    static void Sprinklers()
    {
        var bad = new List<string>(); int cases = 0;
        // decide: pressure (a pump on the network) is required; all-or-nothing pulse
        for (int m = 0; m < 32; m++)
            foreach (int cells in new[] { 0, 5 })
                foreach (int need in new[] { 0, 3 })
                    foreach (int av in new[] { 0, 2, 3, 100 })
                    {
                        bool en = (m & 1) != 0, sw = (m & 2) != 0, pr = (m & 4) != 0, liq = (m & 8) != 0, thick = (m & 16) != 0;
                        var d = RM_SprinklerKernel.Decide(en, sw, pr, liq, thick, cells, need, av);
                        cases++;
                        bool spray = en && sw && pr && liq && !thick && cells > 0 && need > 0 && av >= need;
                        if ((d == RM_SprinklerState.Spraying) != spray) bad.Add("Decide(" + en + "," + sw + "," + pr + "," + liq + "," + thick + "," + cells + "," + need + "," + av + ") = " + d);
                        if (en && sw && !pr && d != RM_SprinklerState.NoPressure) bad.Add("no pump reads " + d);
                    }
        Row("L1_SWEEP_SPRINKLER_NEEDS_A_PUMP", SPRINK, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? "every switch, pressure, liquid, clog, cell and supply combination: a head sprays only when enabled, switched on, pressured by a pump on its net, holding a sprayable liquid, with cells and the whole pulse paid; with no pump it says NoPressure" : string.Join("; ", bad.Take(5)));

        // cost: never free, never short; MaxCellsFor is the true maximum, at every litres setting of the slider
        bad.Clear(); cases = 0;
        float lDefault = EnvF("sprinklerLitresPerCellHour", 0.5f);
        for (float L = 0.1f; L <= 5.0001f; L += 0.05f)
        {
            float Lq = (float)Math.Round(L * 20f) / 20f;
            for (int n = 1; n <= 60; n++)
            {
                cases++;
                int u = RM_SprinklerKernel.UnitsFor(n, Lq, RM_Volume.UnitsPerLitre);
                double exact = n * (double)Lq * RM_Volume.UnitsPerLitre;
                if (u < exact - 1e-3 || u >= exact + 1) bad.Add(n + " cells at " + Lq + " L: " + u + " units, exact " + exact);
            }
            for (int units = 0; units <= 400; units += 7)
            {
                cases++;
                int mc = RM_SprinklerKernel.MaxCellsFor(units, Lq, RM_Volume.UnitsPerLitre);
                bool ok = (mc == 0 || RM_SprinklerKernel.UnitsFor(mc, Lq, 10) <= units) && RM_SprinklerKernel.UnitsFor(mc + 1, Lq, 10) > units;
                if (!ok) bad.Add("MaxCellsFor(" + units + ", " + Lq + ") = " + mc);
            }
            if (bad.Count > 5) break;
        }
        Row("L1_SWEEP_SPRINKLER_PULSE_COST", SPRINK, "sweep", bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? "litres per cell-hour 0.1..5 in 0.05 (shipped " + lDefault + "): a pulse costs cells x litres rounded up, never free or short; the most cells a supply pays for is the true maximum" : string.Join("; ", bad.Take(5)));

        // valve: wanted cells only, nearest first, within budget and reserve, maximal
        bad.Clear(); cases = 0; var r = new Random(99);
        for (int t = 0; t < 20000 && bad.Count == 0; t++)
        {
            int n = r.Next(0, 30); var cells = new List<RM_ValveCell>();
            for (int i = 0; i < n; i++) cells.Add(new RM_ValveCell(i, (float)Math.Round(r.NextDouble() * 4, 1), r.Next(4) > 0, r.Next(6) == 0, r.Next(5) == 0, r.Next(6) > 0, r.Next(8) == 0));
            float L = (float)Math.Round((0.1 + r.NextDouble() * 4.9) * 20) / 20f;
            int budget = r.Next(-1, 200), net = r.Next(0, 400), res = r.Next(-1, 300);
            var kept = RM_SprinklerKernel.Valve(cells, L, 10, budget, net, res, out bool trimmed);
            var want = cells.Where(RM_SprinklerKernel.ValveWants).OrderBy(c => c.Dist).ThenBy(c => c.Index).Select(c => c.Index).ToList();
            int cost = RM_SprinklerKernel.UnitsFor(kept.Count, L, 10);
            cases++;
            bool prefix = kept.SequenceEqual(want.Take(kept.Count));
            bool fits = (budget < 0 || cost <= budget) && (res <= 0 || net - cost >= res || kept.Count == 0);
            int next = RM_SprinklerKernel.UnitsFor(kept.Count + 1, L, 10);
            bool maximal = kept.Count == want.Count || (budget >= 0 && next > budget) || (res > 0 && net - next < res);
            if (!prefix || !fits || !maximal || trimmed != (kept.Count < want.Count))
                bad.Add("seed 99 case " + t + ": " + n + " cells, " + L + " L, budget " + budget + ", net " + net + ", reserve " + res + ": kept " + kept.Count + " of " + want.Count + " wanted (prefix " + prefix + ", fits " + fits + ", maximal " + maximal + ", trimmed " + trimmed + ")");
        }
        // pick liquid, wet record
        var held = new List<KeyValuePair<string, int>> { new("b", 5), new("a", 5), new("c", 4), new(null, 99), new("d", -3) };
        if (RM_SprinklerKernel.PickLiquid(held) != "a" || RM_SprinklerKernel.PickLiquid(new List<KeyValuePair<string, int>>()) != null) bad.Add("PickLiquid tie or empty");
        var g = new RM_SprinkledGrid(4);
        int now = 1000; g.Wet(2, "Water", RM_SprinklerKernel.WetUntil(now), 7);
        bool wetOk = g.WetBy(2, now + 2749) == "Water" && g.WetBy(2, now + 2750) == null && g.WetByOther(2, 8, now) && !g.WetByOther(2, 7, now) && g.Spend(2, now) && g.WetBy(2, now) == null && !g.Spend(2, now) && g.LiveCells(now) == 0;
        if (!wetOk) bad.Add("wet record: a paid pulse does not keep its cells wet to the next pulse plus grace, or a fruiting crop does not spend it");
        cases += 2;
        Row("L1_RANDOM_SPRINKLER_VALVE_AND_WET_RECORD", SPRINK, "random", bad.Count == 0 ? "PASS" : "FAIL", cases,
            bad.Count == 0 ? "20000 random fields (seed 99): the thirst valve waters only cells where water changes growth, nearest first, within the day's budget and above the reserve, and as many as those allow; the head sprays the liquid its net holds most of (ties by name); a paid pulse keeps a cell wet to the next pulse plus 250 ticks and a fruiting crop spends it" : string.Join("; ", bad.Take(3)));
    }

    public static int Main()
    {
        Action[] all = { SheetRandomLedger, SheetSaveLoad, SheetPreviewAndOrder, SheetLevelAndSpread, SheetCropWeek, SheetIceDoorSwitches, SheetSettingsSweep, SheetCreepingFire, Converters, Thirst, Drilling, Sprinklers };
        foreach (var a in all)
        {
            try { a(); }
            catch (Exception e) { Row("L1_CRASH_" + a.Method.Name.ToUpperInvariant(), new[] { "inv_overflow_sheet" }, "fixed", "FAIL", 0, a.Method.Name + " threw " + e); }
        }
        foreach (string l in Out) Console.WriteLine(l);
        return fails > 0 ? 1 : 0;
    }
}
