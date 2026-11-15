// Blind lane 1 (game logic) for FlowWorks 0.1.0, cycle 1 of the Stages 4 and 5 challenge.
// Written from the locked bars (record.json inventory text, sheet.md, tree.json, plan.md), the shipped kernels and the
// shipped settings ONLY (defaults and slider ranges are read from the settings files by run_lane1.py and handed over in
// FW_* environment variables). The builder's selftests, journal, evidence and test table were not opened before this file
// was written and run. Each row names the bar it decides.
// Output: one JSON line per row on stdout (id, bars, kind, verdict, cases, detail); exit 1 if any row FAILs.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.FlowWorks;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.FlowWorks.Thirst;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.Drilling;
using RimMandrake.FlowWorks.Sprinklers;
using SM = RimMandrake.FlowWorks.RM_SheetMath;

static class BlindLane1
{
    static int fails;
    static readonly CultureInfo IC = CultureInfo.InvariantCulture;

    static string Esc(string s) => s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ");
    static void Row(string id, string bars, string kind, string verdict, long cases, string detail)
    {
        if (verdict == "FAIL") fails++;
        Console.WriteLine("{\"id\":\"" + id + "\",\"bars\":[" + string.Join(",", bars.Split(',').Select(b => "\"" + b.Trim() + "\"")) +
                          "],\"kind\":\"" + kind + "\",\"verdict\":\"" + verdict + "\",\"cases\":" + cases + ",\"detail\":\"" + Esc(detail) + "\"}");
    }
    static float Env(string k, float dflt = float.NaN)
    {
        string v = Environment.GetEnvironmentVariable(k);
        return v != null && float.TryParse(v, NumberStyles.Float, IC, out float f) ? f : dflt;
    }
    static void Try(string id, string bars, string kind, Func<(bool ok, long cases, string detail)> body)
    {
        try { var r = body(); Row(id, bars, kind, r.ok ? "PASS" : "FAIL", r.cases, r.detail); }
        catch (Exception e) { Row(id, bars, kind, "FAIL", 0, "threw " + e.GetType().Name + ": " + e.Message); }
    }

    // ======================================================================== sheet (inv_overflow_sheet)
    const string SHEET = "inv_overflow_sheet";

    static SM.Params ShippedParams()
    {
        float cap = Env("FW_SHEET_CAP_CM", 50), ret = Env("FW_RETENTION_CM", 1), door = Env("FW_DOOR_LEAK", 5);
        float sweeps = Env("FW_SWEEPS", 3), maxWet = Env("FW_MAX_WET", 4000), crop = Env("FW_CROP_PULSES", 1680);
        return new SM.Params
        {
            SheetCapDl = (int)Math.Round(cap * SM.DlPerCm), RetentionDl = (int)Math.Round(ret * SM.DlPerCm),
            DoorLeakPermille = (int)Math.Round(door * 10), SweepsPerPulse = (int)sweeps, MaxWetCells = (int)maxWet,
            CropKillPulses = (int)crop,
        };
    }

    sealed class Rig
    {
        public SM.World W; public SM.State S; public SM.Params P; public Random R; public int Wd, Ht;
    }

    // a random yard: mostly open ground, walls, doors, grates, receivers (dug cells with room) and sinks (lakes)
    static Rig MakeRig(int seed, SM.Params p, bool losses, bool cold, bool twoFluids)
    {
        var r = new Random(seed);
        int w = r.Next(4, 13), h = r.Next(4, 13);
        var W = new SM.World(w, h);
        for (int c = 0; c < w * h; c++)
        {
            int roll = r.Next(100);
            W.Kinds[c] = roll < 70 ? SM.Kind.Open : roll < 80 ? SM.Kind.Blocked : roll < 85 ? SM.Kind.Door : roll < 90 ? SM.Kind.Grate
                       : roll < 97 ? SM.Kind.Receiver : SM.Kind.Sink;
            if (W.Kinds[c] == SM.Kind.Receiver) { W.RoomDl[c] = r.Next(0, 6000); W.BodyFluid[c] = (byte)(r.Next(3) == 0 ? 0 : r.Next(1, twoFluids ? 3 : 2)); }
            if (W.Kinds[c] == SM.Kind.Sink) W.BodyFluid[c] = (byte)r.Next(0, twoFluids ? 3 : 2);
            if (losses && W.Kinds[c] == SM.Kind.Open) { W.SoakMilliDl[c] = r.Next(0, 4000); W.EvapMilliDl[c] = r.Next(0, 800); }
            W.TempDeciC[c] = cold ? r.Next(-40, 30) : 200;
        }
        // fluid 1 = water (freezes at 0 °C), fluid 2 = a fuel (never freezes, boils on hot ground)
        W.Fluids[1] = RM_SheetFluidMath.RuleFor(false, false, false, 60, -1, -1);
        var fuel = RM_SheetFluidMath.RuleFor(true, false, false, 90, -1, -1);
        fuel.BoilMilliDl = 500; fuel.BoilAboveDeciC = 150;
        W.Fluids[2] = fuel;
        return new Rig { W = W, S = new SM.State(w, h, (uint)seed * 2654435761u), P = p, R = r, Wd = w, Ht = h };
    }

    static List<SM.SpillOffer> RandomOffers(Rig g, bool twoFluids)
    {
        var offers = new List<SM.SpillOffer>();
        int n = g.R.Next(0, 4);
        for (int i = 0; i < n; i++)
        {
            int len = g.R.Next(1, 7);
            var lips = new int[len];
            for (int k = 0; k < len; k++) lips[k] = g.R.Next(-1, g.Wd * g.Ht + 1); // off-grid lips on purpose
            offers.Add(new SM.SpillOffer { LipNearestFirst = lips, AmountDl = g.R.Next(-50, 9000), Fluid = (byte)g.R.Next(0, twoFluids ? 3 : 2),
                                           From = (SM.Source)g.R.Next(0, SM.SourceCount) });
        }
        return offers;
    }

    static long FluidSum(SM.State s, int f) { long t = 0; for (int c = 0; c < s.Dl.Length; c++) if (s.Fluid[c] == f) t += s.Dl[c]; return t; }

    // structural invariants of a state: returns null when sound, else what broke
    static string Check(Rig g, bool capFixed)
    {
        SM.State s = g.S; SM.World w = g.W;
        if (!s.LedgerCloses) return "ledger open: in " + s.TotalIn + " != standing " + s.Standing + " + out " + s.TotalOut;
        int occ = 0, prev = -1;
        var occSet = new HashSet<int>(s.Occ);
        foreach (int c in s.Occ) { if (c <= prev) return "Occ not strictly ascending at " + c; prev = c; }
        for (int c = 0; c < s.Dl.Length; c++)
        {
            if (s.Dl[c] < 0) return "negative dL at " + c;
            if (s.Dl[c] > 0)
            {
                occ++;
                if (!SM.World.HoldsSheet(w.Kinds[c])) return "sheet water on a " + w.Kinds[c] + " cell " + c;
                if (s.Fluid[c] == 0) return "wet cell " + c + " has no fluid";
                if (!occSet.Contains(c)) return "wet cell " + c + " missing from Occ";
                if (capFixed && s.Dl[c] > g.P.SheetCapDl) return "cell " + c + " over the sheet cap: " + s.Dl[c];
            }
            else if (s.Fluid[c] != 0) return "dry cell " + c + " keeps fluid " + s.Fluid[c];
            if (w.RoomDl[c] < 0) return "receiver room negative at " + c;
        }
        if (occ != s.Occ.Count) return "Occ count " + s.Occ.Count + " != wet cells " + occ;
        return null;
    }

    // one random run: spills then a pulse, every step checked; returns (failure or null, steps, final hash)
    static (string err, int steps, ulong hash) RunSheet(int seed, SM.Params p, int pulses, bool losses, bool cold, bool twoFluids,
                                                        bool shuffle = false, int saveAt = -1)
    {
        Rig g = MakeRig(seed, p, losses, cold, twoFluids);
        var orderRng = new Random(seed ^ 0x5a5a);
        var rep = new SM.PulseReport();
        for (int t = 0; t < pulses; t++)
        {
            if (cold && t % 7 == 0) for (int c = 0; c < g.W.TempDeciC.Length; c++) g.W.TempDeciC[c] = g.R.Next(-40, 40);
            var offers = RandomOffers(g, twoFluids);
            if (shuffle) offers = offers.OrderBy(_ => orderRng.Next()).ToList();
            long[] before = { 0, FluidSum(g.S, 1), FluidSum(g.S, 2) };
            int[] acc = SM.ResolveSpills(g.S, g.W, p, offers);
            for (int i = 0; i < offers.Count; i++)
            {
                if (acc[i] < 0 || acc[i] > Math.Max(0, offers[i].AmountDl)) return ("offer " + i + " accepted " + acc[i] + " of " + offers[i].AmountDl, t, 0);
            }
            for (int f = 1; f <= 2; f++)
            {
                long add = 0; for (int i = 0; i < offers.Count; i++) if (offers[i].Fluid == f) add += acc[i];
                if (FluidSum(g.S, f) != before[f] + add) return ("spill of fluid " + f + " not exact: " + before[f] + "+" + add + " != " + FluidSum(g.S, f), t, 0);
            }
            string e = Check(g, true); if (e != null) return ("after spill: " + e, t, 0);
            long ret0 = g.S.Returned, soak0 = g.S.Soaked;
            long[] pre = { 0, FluidSum(g.S, 1), FluidSum(g.S, 2) };
            var iceBefore = new Dictionary<int, int>();
            foreach (int c in g.S.Occ) if (g.S.Tiers[c] == SM.Tier.Ice) iceBefore[c] = g.S.Dl[c];
            SM.Pulse(g.S, g.W, p, rep);
            e = Check(g, true); if (e != null) return ("after pulse: " + e, t, 0);
            for (int f = 1; f <= 2; f++) if (FluidSum(g.S, f) > pre[f]) return ("pulse created fluid " + f + ": " + pre[f] + " -> " + FluidSum(g.S, f), t, 0);
            if (rep.Returned.Sum(x => (long)x.dl) != g.S.Returned - ret0) return ("reported returns != Returned delta", t, 0);
            foreach (var x in rep.Returned) if (g.W.Kinds[x.cell] != SM.Kind.Receiver) return ("return into a non-receiver " + x.cell, t, 0);
            if (rep.Soaked.Sum(x => (long)x.dl) != g.S.Soaked - soak0) return ("reported soak != Soaked delta", t, 0);
            foreach (var kv in iceBefore) if (g.S.Dl[kv.Key] > kv.Value && g.S.Tiers[kv.Key] == SM.Tier.Ice) return ("ice cell " + kv.Key + " gained water", t, 0);
            if (saveAt == t)
            {
                // continuation identity: a save/load here continues exactly as the uninterrupted run
                byte[] bytes = SM.Save(g.S);
                SM.State loaded = SM.Load(bytes);
                if (SM.Hash(loaded) != SM.Hash(g.S)) return ("load hash differs at once", t, 0);
                SM.World w2 = g.W.Clone();
                var r1 = new Random(seed * 31 + t); var r2 = new Random(seed * 31 + t);
                for (int k = 0; k < 40; k++)
                {
                    var o1 = RandomOffersFrom(r1, g.Wd, g.Ht, twoFluids); var o2 = RandomOffersFrom(r2, g.Wd, g.Ht, twoFluids);
                    SM.ResolveSpills(g.S, g.W, p, o1); SM.ResolveSpills(loaded, w2, p, o2);
                    SM.Pulse(g.S, g.W, p, null); SM.Pulse(loaded, w2, p, null);
                    if (SM.Hash(loaded) != SM.Hash(g.S)) return ("save/load diverged " + (k + 1) + " pulses after the load", t, 0);
                }
                return (null, t, SM.Hash(g.S));
            }
        }
        return (null, pulses, SM.Hash(g.S));
    }
    static List<SM.SpillOffer> RandomOffersFrom(Random r, int w, int h, bool two)
    {
        var l = new List<SM.SpillOffer>();
        int n = r.Next(0, 3);
        for (int i = 0; i < n; i++)
        {
            var lips = new int[r.Next(1, 5)]; for (int k = 0; k < lips.Length; k++) lips[k] = r.Next(0, w * h);
            l.Add(new SM.SpillOffer { LipNearestFirst = lips, AmountDl = r.Next(1, 5000), Fluid = (byte)r.Next(1, two ? 3 : 2), From = SM.Source.Pump });
        }
        return l;
    }

    // shrink a failing random case: fewest pulses that still fail
    static string Shrunk(int seed, SM.Params p, int pulses, bool losses, bool cold, bool two)
    {
        int lo = 1, hi = pulses;
        while (lo < hi) { int mid = (lo + hi) / 2; if (RunSheet(seed, p, mid, losses, cold, two).err != null) hi = mid; else lo = mid + 1; }
        var r = RunSheet(seed, p, lo, losses, cold, two);
        return "seed " + seed + " shrunk to " + lo + " pulses: " + r.err;
    }

    static void SheetRows()
    {
        SM.Params p = ShippedParams();
        // conservation + structure, random yards, the shipped settings
        foreach (var (id, losses, cold, two) in new[] { ("sheet_random_conserve_no_losses", false, false, false), ("sheet_random_conserve_losses", true, false, false),
                                                       ("sheet_random_conserve_cold_two_fluids", true, true, true), ("sheet_random_conserve_warm_two_fluids", true, false, true) })
        {
            int bad = -1; string err = null; const int N = 150, T = 60;
            for (int seed = 1; seed <= N && bad < 0; seed++) { var r = RunSheet(seed, p, T, losses, cold, two); if (r.err != null) { bad = seed; err = r.err; } }
            Row(id, SHEET, "random", bad < 0 ? "PASS" : "FAIL", N * (long)T,
                bad < 0 ? "seeds 1.." + N + " x " + T + " pulses: ledger In == Standing + Returned + JoinedLake + Soaked + Evaporated + Burned + Purged after every spill and pulse; spills exact per fluid; a pulse never creates a fluid (no mixing); no sheet on walls/receivers/sinks; dL within 0..cap; Occ exact"
                         : Shrunk(bad, p, T, losses, cold, two));
        }
        // determinism and offer-order independence
        Try("sheet_offer_order_independent", SHEET, "random", () =>
        {
            for (int seed = 1; seed <= 80; seed++)
            {
                var a = RunSheet(seed, p, 40, true, true, true, false); var b = RunSheet(seed, p, 40, true, true, true, true);
                if (a.err != null || b.err != null) return (false, seed, "seed " + seed + ": " + (a.err ?? b.err));
                if (a.hash != b.hash) return (false, seed, "seed " + seed + ": shuffling the offers of each pulse changed the final state hash");
            }
            return (true, 80, "seeds 1..80 x 40 pulses: the same offers collected in a shuffled order give the same state hash");
        });
        Try("sheet_save_load_continues_identical", SHEET, "random", () =>
        {
            for (int seed = 1; seed <= 60; seed++)
            {
                var r = RunSheet(seed, p, 50, true, seed % 2 == 0, true, false, 5 + seed % 30);
                if (r.err != null) return (false, seed, "seed " + seed + ": " + r.err);
            }
            return (true, 60, "seeds 1..60: save, load, then 40 more pulses with the same spills: the hash matches the uninterrupted run every pulse");
        });
        Try("sheet_preview_matches_resolve", SHEET, "random", () =>
        {
            int cases = 0;
            for (int seed = 1; seed <= 300; seed++)
            {
                Rig g = MakeRig(seed, p, true, false, true);
                for (int t = 0; t < 10; t++) { SM.ResolveSpills(g.S, g.W, p, RandomOffers(g, true)); SM.Pulse(g.S, g.W, p, null); }
                foreach (var o in RandomOffers(g, true))
                {
                    int pre = SM.PreviewSpill(g.S, g.W, p, o);
                    byte[] snap = SM.Save(g.S); SM.State copy = SM.Load(snap);
                    int got = SM.ResolveSpills(copy, g.W, p, new List<SM.SpillOffer> { o })[0];
                    cases++;
                    if (pre != got) return (false, cases, "seed " + seed + ": PreviewSpill " + pre + " != ResolveSpills " + got);
                }
            }
            return (true, cases, "single offers on 300 random wetted yards: preview == accept");
        });
        // fixed: a walled yard lies level (D8) and keeps every dL with no losses
        Try("sheet_walled_yard_lies_level", SHEET, "fixed", () =>
        {
            var W = new SM.World(7, 7);
            for (int c = 0; c < 49; c++) { int x = c % 7, z = c / 7; W.Kinds[c] = x == 0 || z == 0 || x == 6 || z == 6 ? SM.Kind.Blocked : SM.Kind.Open; }
            var S = new SM.State(7, 7, 12345);
            int spill = 25 * 600; // 3 cm over 25 squares
            int got = SM.ResolveSpills(S, W, p, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = Enumerable.Range(0, 49).Where(c => W.Kinds[c] == SM.Kind.Open).OrderBy(c => Math.Abs(c % 7 - 3) + Math.Abs(c / 7 - 3)).ThenBy(c => c).ToArray(), AmountDl = spill, Fluid = 1, From = SM.Source.Pump } })[0];
            if (got != spill) return (false, 1, "spill accepted " + got + " of " + spill);
            for (int t = 0; t < 400; t++) SM.Pulse(S, W, p, null);
            long min = long.MaxValue, max = long.MinValue; int wet = 0;
            for (int c = 0; c < 49; c++) if (S.Dl[c] > 0) { wet++; long surf = S.Dl[c] + SM.Relief(S.Salt, c, p.ReliefDl); min = Math.Min(min, surf); max = Math.Max(max, surf); }
            bool ok = S.Standing == spill && wet == 25 && max - min <= 1;
            string dry = "";
            for (int c = 0; c < 49; c++) if (W.Kinds[c] == SM.Kind.Open && S.Dl[c] == 0)
            {
                dry += " dry cell " + c + " (x" + c % 7 + ",z" + c / 7 + ") rel " + SM.Relief(S.Salt, c, p.ReliefDl) + ", neighbours dL/rel/calm:";
                foreach (int n in new[] { c + 7, c + 1, c - 7, c - 1 }) dry += " " + S.Dl[n] + "/" + SM.Relief(S.Salt, n, p.ReliefDl) + "/" + S.Calm[n];
            }
            return (ok, 400, "25-square walled yard, 3 cm poured at the centre, 400 pulses, no losses: standing " + S.Standing + " of " + spill + ", wet " + wet + "/25, surface spread " + (max - min) + " dL (<= 1);" + dry);
        });
        // fixed: crops drown after a week of standing overflow, a film never drowns them, ice pauses the clock
        Try("sheet_crop_week_standing", SHEET, "fixed", () =>
        {
            int kill = p.CropKillPulses;
            int week = SM.PulsesFor(SM.TicksPerWeek, (int)Env("FW_PULSE_TICKS", 250));
            if (kill != week) return (false, 0, "shipped cropDrownPulses " + kill + " != one week at the shipped pulse (" + week + ")");
            string Run(int dl, int iceFrom, int iceFor, out int firstReport)
            {
                var W = new SM.World(3, 3);
                for (int c = 0; c < 9; c++) W.Kinds[c] = c == 4 ? SM.Kind.Open : SM.Kind.Blocked;
                var S = new SM.State(3, 3, 7);
                SM.ResolveSpills(S, W, p, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 4 }, AmountDl = dl, Fluid = 1, From = SM.Source.Rain } });
                var rep = new SM.PulseReport(); firstReport = -1;
                for (int t = 1; t <= kill + 400; t++)
                {
                    W.TempDeciC[4] = t >= iceFrom && t < iceFrom + iceFor ? -50 : 200;
                    SM.Pulse(S, W, p, rep);
                    if (firstReport < 0 && rep.CropDrowning.Count > 0) firstReport = t;
                }
                return null;
            }
            Run(600, int.MaxValue, 0, out int sheet); Run(300, int.MaxValue, 0, out int film); Run(600, 100, 200, out int iced);
            bool ok = sheet == kill && film < 0 && iced > kill;
            bool ownAge = !SM.CropDrowns(kill + 5, (kill - 1) * 250, 250, p) && SM.CropDrowns(kill + 1, kill * 250, 250, p);
            return (ok && ownAge, 3, "3 cm sheet first reports drowning at pulse " + sheet + " (want " + kill + " = 7 days at 250 ticks); 1.5 cm film: " + film +
                    " (want never); 200 pulses frozen mid-way: " + iced + " (want later than " + kill + "); a crop younger than the delay is spared: " + ownAge);
        });
        Try("sheet_freeze_thaw_keeps_every_dl", SHEET, "fixed", () =>
        {
            var W = new SM.World(3, 3);
            for (int c = 0; c < 9; c++) W.Kinds[c] = c == 4 ? SM.Kind.Open : SM.Kind.Blocked;
            var S = new SM.State(3, 3, 9);
            SM.ResolveSpills(S, W, p, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 4 }, AmountDl = 800, Fluid = 1, From = SM.Source.Pump } });
            var seen = new List<string>();
            foreach (int temp in new[] { 0, -1, 5, 9, 10, 0 })
            {
                W.TempDeciC[4] = temp; SM.Pulse(S, W, p, null); seen.Add(temp + ":" + S.Tiers[4] + "/" + S.Dl[4]);
            }
            string got = string.Join(" ", seen);
            string want = "0:Sheet/800 -1:Ice/800 5:Ice/800 9:Ice/800 10:Sheet/800 0:Sheet/800";
            return (got == want, 6, "deci-°C:tier/dL " + got + (got == want ? "" : " ; want " + want));
        });
        Try("sheet_soaks_away_completely", SHEET, "fixed", () =>
        {
            var W = new SM.World(5, 5);
            int soak = (int)Math.Round(4f * SM.DlPerCm * 1000f / 240f); // sand, 4 cm a day at 240 pulses a day
            for (int c = 0; c < 25; c++) { W.Kinds[c] = SM.Kind.Open; W.SoakMilliDl[c] = soak; }
            var S = new SM.State(5, 5, 3);
            SM.ResolveSpills(S, W, p, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 12 }, AmountDl = 2000, Fluid = 1, From = SM.Source.Pump } });
            int t = 0; while (S.Occ.Count > 0 && t < 5000) { SM.Pulse(S, W, p, null); t++; }
            bool ok = S.Occ.Count == 0 && S.Soaked == 2000 && S.LedgerCloses;
            return (ok, t, "10 cm on one square of sand: dry after " + t + " pulses, soaked " + S.Soaked + " of 2000 dL; nothing lost to remainders");
        });
        Try("sheet_door_zero_percent_seals", SHEET, "fixed", () =>
        {
            var q = ShippedParams(); q.DoorLeakPermille = 0;
            var W = new SM.World(5, 1);
            W.Kinds[0] = SM.Kind.Open; W.Kinds[1] = SM.Kind.Open; W.Kinds[2] = SM.Kind.Door; W.Kinds[3] = SM.Kind.Open; W.Kinds[4] = SM.Kind.Sink;
            var S = new SM.State(5, 1, 1);
            SM.ResolveSpills(S, W, q, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 0 }, AmountDl = 4000, Fluid = 1, From = SM.Source.Pump } });
            for (int t = 0; t < 300; t++) SM.Pulse(S, W, q, null);
            bool sealedOk = S.Dl[2] == 0 && S.Dl[3] == 0 && S.JoinedLake == 0;
            var q5 = ShippedParams();
            var S2 = new SM.State(5, 1, 1);
            SM.ResolveSpills(S2, W, q5, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 0 }, AmountDl = 4000, Fluid = 1, From = SM.Source.Pump } });
            for (int t = 0; t < 300; t++) SM.Pulse(S2, W, q5, null);
            return (sealedOk && S2.JoinedLake > 0, 2, "door 0%: door/beyond dL " + S.Dl[2] + "/" + S.Dl[3] + ", joined lake " + S.JoinedLake + " (want 0); door at shipped " + q5.DoorLeakPermille / 10 + "%: joined lake " + S2.JoinedLake + " (want > 0)");
        });
        // sweep the shipped settings through their slider ranges: cap 5..100 cm, retention 0.5..5 cm, door 0..50 %, sweeps 1..6, wet cap 500..20000
        Try("sheet_sweep_settings_ranges", SHEET, "sweep", () =>
        {
            int cases = 0;
            foreach (int cap in new[] { 5, 20, 50, 100 })
            foreach (float ret in new[] { 0.5f, 1f, 2.5f, 5f })
            foreach (int door in new[] { 0, 5, 50 })
            foreach (int sw in new[] { 1, 3, 6 })
            foreach (int wet in new[] { 500, 4000, 20000 })
            {
                var q = new SM.Params { SheetCapDl = cap * SM.DlPerCm, RetentionDl = (int)(ret * SM.DlPerCm), DoorLeakPermille = door * 10, SweepsPerPulse = sw, MaxWetCells = wet };
                for (int seed = 1; seed <= 3; seed++)
                {
                    var r = RunSheet(seed * 1000 + cases, q, 25, true, true, true); cases++;
                    if (r.err != null) return (false, cases, "cap " + cap + " cm, retention " + ret + " cm, door " + door + "%, sweeps " + sw + ", wet cap " + wet + ", seed " + (seed * 1000 + cases - 1) + ": " + r.err);
                }
            }
            return (true, cases, "4 caps x 4 retentions x 3 door leaks x 3 sweep counts x 3 wet caps x 3 seeds x 25 pulses: every invariant of the random rows holds");
        });
        Try("sheet_wet_cap_never_exceeded", SHEET, "random", () =>
        {
            for (int seed = 1; seed <= 100; seed++)
            {
                var q = ShippedParams(); q.MaxWetCells = 1 + seed % 9;
                Rig g = MakeRig(seed, q, false, false, true);
                for (int t = 0; t < 40; t++)
                {
                    SM.ResolveSpills(g.S, g.W, q, RandomOffers(g, true));
                    if (g.S.WetCount > q.MaxWetCells) return (false, seed, "seed " + seed + ": spill wet " + g.S.WetCount + " > cap " + q.MaxWetCells);
                    SM.Pulse(g.S, g.W, q, null);
                    if (g.S.WetCount > q.MaxWetCells) return (false, seed, "seed " + seed + " pulse " + t + ": wet " + g.S.WetCount + " > cap " + q.MaxWetCells);
                }
            }
            return (true, 100, "wet-square caps 1..9 on 100 random yards x 40 pulses: never exceeded (refused spills stay with the inflow)");
        });
        Try("sheet_lowered_cap_deletes_nothing", SHEET, "fixed", () =>
        {
            var W = new SM.World(6, 6);
            for (int c = 0; c < 36; c++) W.Kinds[c] = SM.Kind.Open;
            var S = new SM.State(6, 6, 5);
            var q = ShippedParams();
            SM.ResolveSpills(S, W, q, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = Enumerable.Range(0, 36).ToArray(), AmountDl = 36 * 4000, Fluid = 1, From = SM.Source.Flood } });
            long before = S.Standing; q.SheetCapDl = 5 * SM.DlPerCm;
            for (int t = 0; t < 50; t++) SM.Pulse(S, W, q, null);
            int refused = SM.ResolveSpills(S, W, q, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 0 }, AmountDl = 100, Fluid = 1, From = SM.Source.Pump } })[0];
            return (S.Standing == before && S.LedgerCloses && refused == 0, 50, "20 cm over a closed 6x6 yard, cap lowered to 5 cm: standing " + S.Standing + " of " + before + " after 50 pulses; a new 100 dL spill accepted " + refused + " (want 0)");
        });
        Try("sheet_every_liquid_has_a_rule", SHEET, "sweep", () =>
        {
            int cases = 0;
            foreach (bool burn in new[] { false, true }) foreach (bool hot in new[] { false, true }) foreach (bool slip in new[] { false, true })
            foreach (int tpt in new[] { 10, 60, 61, 120, 600, 6000 })
            {
                var fr = RM_SheetFluidMath.RuleFor(burn, hot, slip, tpt, -1, -1); cases++;
                if (fr.InfiltrationPermille < 100 || fr.EvaporationPermille < 100) return (false, cases, "rule too slow to ever leave: " + burn + hot + slip + tpt);
                if (fr.NeverFreezes != (burn || hot || slip)) return (false, cases, "freezing wrong for burn " + burn + " hot " + hot + " slip " + slip);
            }
            var w = RM_SheetFluidMath.RuleFor(false, false, false, 60, -1, -1);
            return (w.InfiltrationPermille == 1000 && w.EvaporationPermille == 1000 && !w.NeverFreezes, cases,
                    "every combination of burnable/hot/slippery x viscosity 10..6000 soaks and dries at >= 10% of water; only plain liquids freeze; water = 1000/1000");
        });
        Try("flood_release_ledger_random", SHEET, "random", () =>
        {
            var r = new Random(77); long cases = 0;
            for (int run = 0; run < 2000; run++)
            {
                long start = r.Next(-5, 200000);
                var L = RM_FloodReleaseMath.Ledger.Start(start);
                bool exact = r.Next(2) == 0;
                for (int k = 0; k < 50; k++)
                {
                    cases++;
                    long room = r.Next(-10, 6000);
                    long pour = RM_FloodReleaseMath.DugPourDl(L.Remaining, room, exact);
                    if (pour < 0 || pour > Math.Max(0, Math.Min(L.Remaining, room))) return (false, cases, "dug pour " + pour + " with remaining " + L.Remaining + " room " + room);
                    if (!exact && pour % RM_FloodReleaseMath.U != 0) return (false, cases, "part-notch pour " + pour + " in whole-notch mode");
                    long placed = L.Place(pour);
                    if (placed != pour) return (false, cases, "place debited " + placed + " of " + pour);
                    long debit = RM_FloodReleaseMath.SurfaceDebitDl(L.Remaining, RM_FloodReleaseMath.PerTileDl((float)r.NextDouble() * 3));
                    if (debit > L.Remaining) return (false, cases, "surface overdraw");
                    L.Place(debit);
                    if (r.Next(10) == 0) L.Spill(r.Next(-10, 5000));
                    if (!L.Closes) return (false, cases, "ledger open: in " + L.In + " rem " + L.Remaining + " placed " + L.Placed + " spilled " + L.Spilled + " lost " + L.Lose());
                }
                L.Lose();
                if (!L.Closes || L.Remaining != 0) return (false, cases, "end of release not closed");
            }
            // Pick: deterministic, in range, not degenerate
            var hist = new int[7];
            for (int i = 0; i < 70000; i++) { int v = RM_FloodReleaseMath.Pick(12345, i, 0, 7); if (v < 0 || v >= 7) return (false, cases, "pick out of range"); hist[v]++; }
            bool flat = hist.All(h => h > 9000 && h < 11000);
            bool mono = RM_FloodReleaseMath.ExpiryTick(100, 30, 10, 5) > RM_FloodReleaseMath.ExpiryTick(100, 30, 10, 4);
            return (flat && mono, cases, "seed 77, 2000 releases x 50 steps: In == Remaining + Placed + Spilled + Lost always; no overdraw; whole notches in whole-notch mode; Pick histogram " + string.Join("/", hist) + "; expiry grows with unpaid steps " + mono);
        });
        Row("sheet_flowkernel_not_in_lane1", SHEET, "info", "INFO", 0,
            "RM_FlowKernel.cs is the dug-canal depth engine (inv_flow_level); the sheet's own kernel is RM_SheetMath. Lane 1 tested the sheet; the depth engine's conservation is a stage-6 bar's and was not spent on here.");
        float on = Env("FW_SHEET_ON", -1);
        Row("sheet_ships_switched_off", SHEET, "info", "INFO", 1,
            "sheetOverflowEnabled ships " + (on == 1 ? "ON" : on == 0 ? "OFF" : "UNREAD") + " (RM_SheetSettings.cs). With it off no spill enters the sheet (SpillsFrom returns false), so the bar's overspill is not seen in a default game. A question for lane 2: is that the shipped intent?");
        float pt = Env("FW_PULSE_TICKS", 250), cp = Env("FW_CROP_PULSES", 1680);
        Row("sheet_crop_delay_rides_the_pulse_slider", SHEET, "sweep", "INFO", 3,
            "the crop delay is stored in pulses (" + cp + "), so at the pulse slider's ends it reads " + (cp * 60 / 60000f).ToString("0.##", IC) + " days (60 ticks) and " + (cp * 2500 / 60000f).ToString("0.#", IC) +
            " days (2500 ticks); at the shipped " + pt + " ticks it is " + (cp * pt / 60000f).ToString("0.##", IC) + " days. A question for lane 2: does the game re-derive it when the pulse changes?");
    }

    // ======================================================================== converters (inv_converters)
    const string CONV = "inv_converters";
    // my model of a converter's rare tick, from the kernel's documentation: income, cap, clipped income kept, batches spent
    static void ConvTick(ref float accrued, float perTick, int inU, int outU, ref int input, ref int outRoom, ref long made, ref long eaten)
    {
        accrued += perTick;
        float capped = RM_ConversionMath.CapAccrued(accrued, inU, perTick);
        float clipped = RM_ConversionMath.ClippedIncome(accrued, capped, perTick);
        int n = RM_ConversionMath.Batches(capped, inU, outU, input, outRoom);
        input -= n * inU; if (outRoom >= 0) outRoom -= n * outU;
        made += n * (long)outU; eaten += n * (long)inU;
        accrued = capped - n * inU + clipped;
    }
    static void ConverterRows()
    {
        Try("conv_cadence_is_a_day", CONV, "fixed", () =>
            (RM_ConversionMath.RareTicksPerDay * RM_ConversionMath.RareTick == 60000 && Math.Abs(RM_ConversionMath.BudgetPerRareTick(240, 1, 1, 1) - 1f) < 1e-6
             && RM_ConversionMath.BudgetPerRareTick(240, 0, 1, 1) == 0 && RM_ConversionMath.BudgetPerRareTick(-1, 1, 1, 1) == 0, 4,
             "240 rare ticks x 250 = 60000 ticks; 240 units a day = 1 a rare tick; a zero rate or negative input makes nothing"));
        Try("conv_random_conserves_and_keeps_rate", CONV, "random", () =>
        {
            var r = new Random(4242); long cases = 0;
            for (int run = 0; run < 3000; run++)
            {
                int inU = r.Next(1, 400), outU = r.Next(1, 400);
                float perDay = (float)(r.NextDouble() * 20000), tier = (float)(0.25 + r.NextDouble() * 2), mult = (float)(0.1 + r.NextDouble() * 4.9);
                float per = RM_ConversionMath.BudgetPerRareTick(perDay, tier, mult, 1f);
                float acc = 0; int input = int.MaxValue / 2, room = -1; long made = 0, eaten = 0; int days = 3;
                for (int t = 0; t < 240 * days; t++)
                {
                    ConvTick(ref acc, per, inU, outU, ref input, ref room, ref made, ref eaten); cases++;
                    if (acc < -1e-4f * inU - 1e-3f) return (false, cases, "budget negative " + acc + " (run " + run + "), past the kernel's 1e-4 batch slack");
                }
                double want = perDay * tier * mult * days;
                if (eaten > want + 1 || eaten < want - inU - Math.Max(1, want * 1e-4)) return (false, cases,
                    "run " + run + ": inU " + inU + " perDay " + perDay + " tier " + tier + " mult " + mult + ": ate " + eaten + " in " + days + " days, want about " + want.ToString("0", IC));
                if (made != eaten / inU * outU) return (false, cases, "run " + run + ": made " + made + " not batches x output");
            }
            return (true, cases, "seed 4242, 3000 machines x 3 days: input eaten within one batch of rate x days (the cap never eats income); output = batches x outputUnits; budget never negative");
        });
        {
            double worst = 0; string at = "";
            for (int inU = 1; inU <= 200; inU++) for (int p10 = 10; p10 <= 4000; p10 += 7)
            {
                float per = p10 / 10f; float acc = 0; int input = int.MaxValue / 2, room = -1; long made = 0, eaten = 0;
                for (int t = 0; t < 240; t++) ConvTick(ref acc, per, inU, 1, ref input, ref room, ref made, ref eaten);
                double loss = (per * 240.0 - eaten - inU) / (per * 240.0);   // a day may end holding less than one batch: not a loss
                if (loss > worst) { worst = loss; at = "inputUnits " + inU + ", income " + per + " a rare tick: runs " + eaten + " of " + (per * 240) + " units a day"; }
            }
            Row("conv_rate_loss_when_income_beats_a_batch", CONV, "sweep", worst > 0.02 ? "FAIL" : "PASS", 200 * 570,
                "kernel loop as documented (income, CapAccrued, ClippedIncome kept, Batches from the capped budget): when one tick's income exceeds a batch and is not a whole number of batches, the remainder r = income mod batch is lost every tick (the kept clip saturates at one tick's income). Worst over inputUnits 1..200 x income 1..400 a tick: " + (worst * 100).ToString("0.#", IC) + "% (" + at + ")");
        }
        Try("conv_idle_week_no_burst", CONV, "random", () =>
        {
            var r = new Random(9); long cases = 0;
            for (int run = 0; run < 2000; run++)
            {
                int inU = r.Next(1, 300), outU = r.Next(1, 50);
                float per = RM_ConversionMath.BudgetPerRareTick((float)(r.NextDouble() * 9000), 1, (float)(0.1 + r.NextDouble() * 4.9), 1);
                float acc = 0; int input = 0, room = -1; long made = 0, eaten = 0;
                for (int t = 0; t < 240 * 7; t++) ConvTick(ref acc, per, inU, outU, ref input, ref room, ref made, ref eaten);
                input = int.MaxValue / 2; long e0 = eaten;
                ConvTick(ref acc, per, inU, outU, ref input, ref room, ref made, ref eaten); cases++;
                long burst = eaten - e0, bound = (long)Math.Floor(Math.Max(inU, per) + per + 1e-3) ;
                if (burst > bound) return (false, cases, "run " + run + ": a dry week then a full tank ran " + burst + " units at once (bound " + bound + ")");
            }
            return (true, cases, "seed 9, 2000 machines dry for a week then filled: the first tick runs at most max(one batch, one tick) + one tick of income");
        });
        Try("conv_room_and_input_bound", CONV, "random", () =>
        {
            var r = new Random(11);
            for (int i = 0; i < 200000; i++)
            {
                float acc = (float)(r.NextDouble() * 5000); int inU = r.Next(-2, 200), outU = r.Next(-2, 200), have = r.Next(0, 3000), room = r.Next(-1, 3000);
                int n = RM_ConversionMath.Batches(acc, inU, outU, have, room);
                if (n < 0 || (n > 0 && (n * inU > have || n * inU > acc + 1e-2 || (room >= 0 && n * outU > room)))) return (false, i, "Batches(" + acc + "," + inU + "," + outU + "," + have + "," + room + ") = " + n);
                if (n > 0 && inU > 0 && outU > 0 && have >= (n + 1) * inU && acc >= (n + 1) * inU + 1 && (room < 0 || room >= (n + 1) * outU)) return (false, i, "Batches left one runnable batch unrun");
            }
            return (true, 200000, "seed 11: Batches never spends input it lacks, budget it lacks or room it lacks, and never leaves a whole runnable batch");
        });
        Try("conv_rotation_never_starves", CONV, "random", () =>
        {
            var r = new Random(5);
            for (int i = 0; i < 20000; i++)
            {
                int n = r.Next(1, 7); var b = new List<int>(); for (int k = 0; k < n; k++) b.Add(r.Next(3) == 0 ? 0 : r.Next(1, 5));
                int last = r.Next(-1, n);
                int nx = RM_ConversionMath.NextRunnable(b, last), first = RM_ConversionMath.FirstRunnable(b);
                bool any = b.Any(x => x > 0);
                if (!any && (nx != -1 || first != -1)) return (false, i, "a pick with nothing runnable");
                if (any && (nx < 0 || b[nx] <= 0 || first < 0 || b[first] <= 0 || b.Take(first).Any(x => x > 0))) return (false, i, "bad pick " + nx + "/" + first + " of " + string.Join(",", b));
                // every runnable input runs within n cycles when all stay runnable
                var ran = new HashSet<int>(); int l = last;
                for (int k = 0; k < n; k++) { l = RM_ConversionMath.NextRunnable(b, l); if (l >= 0) ran.Add(l); }
                if (ran.Count != b.Count(x => x > 0)) return (false, i, "rotation starved an input: " + string.Join(",", b) + " ran " + string.Join(",", ran));
            }
            var capped = new List<float> { 3, 9, 4 };
            bool keep = RM_ConversionMath.AccruedAfterPick(1, capped, -1) == 9 && RM_ConversionMath.AccruedAfterPick(1, capped, 2) == 4;
            return (keep, 20000, "seed 5: the next pick is always runnable, every runnable input runs within one rotation; a blocked tick keeps the largest cap");
        });
        Try("conv_still_daylight_only", CONV, "fixed", () =>
            (RM_ConversionMath.SunFactor(0.5f, false) == 1 && RM_ConversionMath.SunFactor(0.49f, false) == 0 && RM_ConversionMath.SunFactor(1, true) == 0, 3,
             "solar still: full at sky glow 0.5 unroofed, nothing below or under a roof"));
        float mult = Env("FW_CONV_MULT", -1);
        Try("conv_sweep_rate_setting", CONV, "sweep", () =>
        {
            if (mult != 1f) return (false, 0, "converterRateMultiplier ships " + mult + ", want 1 (defaults = shipped behaviour)");
            float prev = -1; int c = 0;
            for (float m = 0.1f; m <= 5.0001f; m += 0.1f) { float v = RM_ConversionMath.BudgetPerRareTick(1000, 1, m, 1); c++; if (v <= prev) return (false, c, "rate not increasing at " + m); prev = v; }
            return (true, c, "converterRateMultiplier ships 1; across 0.1..5 the budget rises strictly and linearly");
        });
    }

    // ======================================================================== bottles and thirst (inv_bottles_thirst)
    const string THIRST = "inv_bottles_thirst";
    static void ThirstRows()
    {
        Try("thirst_ruled_numbers", THIRST, "fixed", () =>
        {
            float fall = RM_ThirstMath.FallPerDay(1, 1, false, false);
            double daysEmpty = 1.0 / fall;
            double perInterval = RM_ThirstMath.FallPerInterval(fall);
            double daySum = perInterval * (RM_ThirstMath.TicksPerDay / RM_ThirstMath.NeedIntervalTicks);
            double bottle = RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Potable, true);
            double deathDays = RM_ThirstMath.DehydrationLethal / (RM_ThirstMath.DehydrationDelta(0, 60000));
            bool ok = Math.Abs(daysEmpty - 1.25) < 1e-4 && Math.Abs(daySum - fall) < 1e-5 && Math.Abs(bottle - 0.5) < 1e-6 && deathDays > 2.9 && deathDays < 3.5
                      && RM_ThirstMath.HeatFactor(100, 20, true) == 3 && RM_ThirstMath.HeatFactor(30, 20, true) == 1.5f && RM_ThirstMath.HeatFactor(50, 20, false) == 1;
            return (ok, 7, "empty in " + daysEmpty.ToString("0.###", IC) + " days at 1x (ruled ~1.25); 1.5 L bottle restores " + bottle + " (0.5); death " + deathDays.ToString("0.##", IC) +
                    " days after empty (ruled ~3); heat x1.5 at 10 °C over comfort, capped x3");
        });
        Try("thirst_rate_sweep", THIRST, "sweep", () =>
        {
            float shipped = Env("FW_THIRST_RATE", -1);
            if (shipped != 1f) return (false, 0, "thirstRateMultiplier ships " + shipped + ", want 1");
            int c = 0;
            for (float m = 0.25f; m <= 3.0001f; m += 0.05f)
            for (float over = -10; over <= 60; over += 5)
            foreach (bool hard in new[] { false, true }) foreach (bool sleep in new[] { false, true })
            {
                c++;
                float h = RM_ThirstMath.HeatFactor(20 + over, 20, true);
                float f = RM_ThirstMath.FallPerDay(m, h, hard, sleep);
                double days = 1 / f;
                // fastest: x3 rate x3 heat x1.3; slowest: 0.25 x 0.5 asleep
                if (f <= 0 || h < 1 || h > 3 || days < 1.25 / (3 * 3 * 1.3) - 1e-4 || days > 1.25 / (0.25 * 0.5) + 1e-3) return (false, c, "rate " + m + " over " + over + ": fall " + f);
                if (RM_ThirstMath.DaysOfWater(30, 1, m) <= 0) return (false, c, "days of water not positive");
            }
            return (true, c, "thirstRateMultiplier 0.25..3 x heat -10..+60 °C over comfort x labour x sleep: the need always falls, heat factor in 1..3, empty-time bounded by the ruled extremes");
        });
        Try("thirst_drink_gate", THIRST, "sweep", () =>
        {
            int c = 0;
            foreach (RM_DrinkUse use in Enum.GetValues(typeof(RM_DrinkUse)))
            foreach (float lvl in new[] { 0f, 0.004f, 0.006f, 0.05f, 0.5f, 1f })
            foreach (bool human in new[] { false, true }) foreach (bool native in new[] { false, true })
            foreach (bool brk in new[] { false, true }) foreach (bool lr in new[] { false, true })
            {
                c++;
                bool may = RM_ThirstMath.MayDrink(use, lvl, human, native, brk, lr);
                bool want = use == RM_DrinkUse.Potable ? true : use == RM_DrinkUse.Never ? false : !human ? native
                          : use == RM_DrinkUse.LastResort ? lr && lvl <= 0.005f : brk;
                if (may != want) return (false, c, use + " lvl " + lvl + " human " + human + " native " + native + " break " + brk + " lastResort " + lr + ": " + may);
            }
            return (true, c, "potable always, never never; humans take a last resort only when empty and allowed, salt only in the break; animals only their native water");
        });
        Try("thirst_pick_order_is_a_strict_order", THIRST, "random", () =>
        {
            var r = new Random(31);
            var src = Enumerable.Range(0, 60).Select(_ => ((RM_DrinkUse)r.Next(4), r.Next(2) == 0, (RM_WaterQuality)r.Next(5), (float)r.Next(0, 6))).ToList();
            long c = 0;
            foreach (var a in src) foreach (var b in src)
            {
                c++;
                bool ab = RM_ThirstMath.BetterPick(a.Item1, a.Item2, a.Item3, a.Item4, b.Item1, b.Item2, b.Item3, b.Item4);
                bool ba = RM_ThirstMath.BetterPick(b.Item1, b.Item2, b.Item3, b.Item4, a.Item1, a.Item2, a.Item3, a.Item4);
                if (ab && ba) return (false, c, "both better: " + a + " / " + b);
                if (ab && (int)a.Item1 > (int)b.Item1) return (false, c, "a worse use class picked first");
                foreach (var d in src.Take(20)) { bool bd = RM_ThirstMath.BetterPick(b.Item1, b.Item2, b.Item3, b.Item4, d.Item1, d.Item2, d.Item3, d.Item4);
                    bool ad = RM_ThirstMath.BetterPick(a.Item1, a.Item2, a.Item3, a.Item4, d.Item1, d.Item2, d.Item3, d.Item4); if (ab && bd && !ad) return (false, c, "not transitive"); }
            }
            return (true, c, "seed 31, 60 sources: the giver's pick is antisymmetric and transitive, and use class always comes first");
        });
        Try("thirst_reserve_and_deficit", THIRST, "random", () =>
        {
            var r = new Random(8); float shipped = Env("FW_RESERVE_L", -1), per = Env("FW_BOTTLES_PER", -1);
            for (int i = 0; i < 100000; i++)
            {
                int av = r.Next(0, 50000), res = r.Next(-5, 20001); bool pot = r.Next(2) == 0;
                int s = RM_ThirstMath.Spendable(av, res, pot);
                if (s < 0 || s > av || (pot && res > 0 && av - s < Math.Min(av, res)) || (!pot && s != av)) return (false, i, "Spendable(" + av + "," + res + "," + pot + ") = " + s);
                int d = RM_ThirstMath.BottleDeficit(r.Next(0, 11), r.Next(-1, 30), r.Next(0, 400));
                if (d < 0) return (false, i, "negative deficit");
            }
            return (shipped == 200 && per == 3, 100000, "seed 8: a sprinkler or machine never draws a potable net below the drinking reserve, never more than is there; non-potable has none; shipped reserve " + shipped + " L, " + per + " bottles a colonist");
        });
        Try("thirst_awkward_and_categories", THIRST, "fixed", () =>
        {
            bool aw = !RM_ThirstMath.Awkward(RM_DrinkSource.Terrain, false) && RM_ThirstMath.Awkward(RM_DrinkSource.Caravan, true) && RM_ThirstMath.Awkward(RM_DrinkSource.Container, true)
                      && !RM_ThirstMath.Awkward(RM_DrinkSource.Bottle, true) && RM_ThirstMath.Awkward(RM_DrinkSource.Bottle, false) && !RM_ThirstMath.Awkward(RM_DrinkSource.Tank, true);
            bool cat = RM_ThirstMath.Category(0) == 3 && RM_ThirstMath.Category(0.05f) == 2 && RM_ThirstMath.Category(0.2f) == 1 && RM_ThirstMath.Category(0.3f) == 0;
            bool salt = RM_ThirstMath.SaltBreakCan(0.05f, false, false, true) && !RM_ThirstMath.SaltBreakCan(0.05f, true, false, true) && !RM_ThirstMath.SaltBreakCan(0.2f, false, false, true);
            bool deh = RM_ThirstMath.DehydrationDelta(0.2f, 150) == 0 && RM_ThirstMath.DehydrationDelta(0.5f, 150) < 0 && RM_ThirstMath.OrphanDehydrationDelta(false, 600) < 0;
            return (aw && cat && salt && deh, 16, "awkward " + aw + ", categories " + cat + ", salt break " + salt + ", dehydration " + deh);
        });
        Try("bottle_styles_round_trip", THIRST, "sweep", () =>
        {
            int c = 0;
            foreach (string size in RM_ContainerStyleMath.Sizes) foreach (string look in RM_ContainerStyleMath.Looks)
            {
                c++;
                if (RM_ContainerStyleMath.LookOfStyleDefName(RM_ContainerStyleMath.StyleDefName(size, look)) != look) return (false, c, size + "/" + look + " does not round-trip");
                if (!RM_ContainerStyleMath.TexPath(size, look).Contains("/" + look + "/")) return (false, c, "texPath lacks look");
            }
            foreach (string bad in new[] { null, "", "RM_", "RM_Bottle", "RM_Jug_Modern", "XX_Bottle_Modern", "RM_Bottle_Jawa", "RM__Modern" })
            { c++; if (RM_ContainerStyleMath.LookOfStyleDefName(bad) != null) return (false, c, "'" + bad + "' read as a look"); }
            foreach (string tech in new[] { "Animal", "Neolithic", "Medieval", "Industrial", "Spacer", "Ultra", "Archotech", "Undefined", null, "Nonsense" })
            { c++; if (!RM_ContainerStyleMath.IsLook(RM_ContainerStyleMath.LookForTech(tech))) return (false, c, tech + " has no look"); }
            bool stack = RM_ContainerStyleMath.MayStack("Modern", null) && !RM_ContainerStyleMath.MayStack(null, "Modern") && !RM_ContainerStyleMath.MayStack("Modern", "Scrapper") && RM_ContainerStyleMath.MayStack("Modern", "Modern");
            return (stack, c, "3 sizes x 4 looks round-trip defName and texPath; 8 foreign names refused; every tech level wears a look; an unstyled stack joins a styled one, never the reverse");
        });
        Try("stock_debit_credit_conserve", THIRST + ",inv_stock", "random", () =>
        {
            var r = new Random(21);
            for (int i = 0; i < 200000; i++)
            {
                bool lim = r.Next(5) == 0; float stock = (float)(r.NextDouble() * 1000), cap = (float)(r.NextDouble() * 1200), u = (float)(r.NextDouble() * 50 - 2);
                float acc = RM_StockMath.CreditAccepted(lim, stock, cap, u);
                if (acc < 0 || acc > Math.Max(0, u) || (!lim && stock + acc > Math.Max(cap, stock) + 1e-3)) return (false, i, "credit " + acc + " stock " + stock + " cap " + cap + " units " + u);
                if (!lim && RM_StockMath.CanDebit(lim, stock, u) && u > stock) return (false, i, "debit beyond stock");
                int lv = RM_StockMath.CreditableLevels(lim, stock, cap, r.Next(-1, 6), (float)(r.NextDouble() * 3 - 0.2));
                if (lv < 0) return (false, i, "negative levels");
            }
            return (true, 200000, "seed 21: a limited body never accepts past its capacity, never more than offered; a debit beyond stock is refused");
        });
        Row("bottle_jobs_not_kernel", THIRST, "not_kernel", "UNSETTLED", 0,
            "fill/empty/wash jobs, material choice, Dubs Bad Hygiene Lite compatibility and the pipe faucet are game-side (JobDriver_FillBottle, RM_ContainerMaterials, Building_RM_PipeFaucet); no kernel decides them offline");
    }

    // ======================================================================== drilling (inv_drilling)
    const string DRILL = "inv_drilling";
    static void DrillRows()
    {
        Try("drill_placement_and_why_not_agree", DRILL, "sweep", () =>
        {
            int c = 0;
            foreach (float reserve in new[] { -1f, 0f, 0.001f, 50f })
            for (int m = 0; m < 1 << 11; m++)
            {
                var s = new RM_DrillSurveyMath.State
                {
                    settingOn = (m & 1) != 0, switchedOn = (m & 2) != 0, needsPower = (m & 4) != 0, powered = (m & 8) != 0, surveyed = (m & 16) != 0,
                    hasYield = (m & 32) != 0, hasCanalForm = (m & 64) != 0, fluidAllowed = (m & 128) != 0, outletDug = (m & 256) != 0,
                    outletOtherLiquid = (m & 512) != 0, outletBrimming = (m & 1024) != 0, reserve = reserve,
                };
                c++;
                var why = RM_DrillSurveyMath.WhyNot(s);
                var place = RM_DrillSurveyMath.Placement(s.surveyed, s.hasYield, s.reserve);
                bool allGood = s.settingOn && s.switchedOn && (!s.needsPower || s.powered) && s.surveyed && s.hasYield && s.hasCanalForm && s.fluidAllowed
                               && s.outletDug && !s.outletOtherLiquid && !s.outletBrimming && s.reserve > 0f;
                if ((why == RM_DrillSurveyMath.Block.None) != allGood) return (false, c, "mask " + m + " reserve " + reserve + ": WhyNot " + why + " but all-good " + allGood);
                if (why == RM_DrillSurveyMath.Block.None && place != RM_DrillSurveyMath.Verdict.Allowed) return (false, c, "pours on a square placement refuses");
                if (s.surveyed && !s.hasYield && place != RM_DrillSurveyMath.Verdict.NoYield) return (false, c, "a dry survey allowed placement");
                if (!s.surveyed && place != RM_DrillSurveyMath.Verdict.Allowed) return (false, c, "unsurveyed ground refused");
            }
            return (true, c, "2^11 drill states x 4 reserves: WhyNot is None exactly when every condition holds; a pouring drill is always on an allowed square; a dry survey refuses; unsurveyed ground is allowed");
        });
        {
            var sN = new RM_DrillSurveyMath.State { settingOn = true, switchedOn = true, surveyed = true, hasYield = true, hasCanalForm = true, fluidAllowed = true, outletDug = true, reserve = float.NaN };
            Row("drill_nan_reserve_pours", DRILL, "info", "INFO", 1, "a NaN reserve (only from corrupt data) reads WhyNot " + RM_DrillSurveyMath.WhyNot(sN) + " and placement " + RM_DrillSurveyMath.Placement(true, true, float.NaN) + ": `reserve <= 0f` lets NaN through. Not a realistic input; noted, not failed");
        }
        Try("drill_spent_units_conserve", DRILL, "random", () =>
        {
            var r = new Random(13); long cases = 0;
            for (int run = 0; run < 2000; run++)
            {
                long dl = 0; double spent = 0; long dlPer = RM_Volume.UnitsPerLevel; float unit = (float)(0.1 + r.NextDouble() * 5);
                for (int k = 0; k < 30; k++)
                {
                    long before = dl, after = Math.Max(0, dl + r.Next(-3000, 9000)); cases++;
                    float s = RM_DrillSurveyMath.SpentUnits(before, after, dlPer, unit);
                    if (s < 0) return (false, cases, "negative spend");
                    spent += s; if (after > before) dl = after; else dl = before;
                }
                double want = dl / (double)dlPer * unit;
                if (Math.Abs(spent - want) > 1e-3 * Math.Max(1, want)) return (false, cases, "run " + run + ": charged " + spent + " for " + dl + " dL landed (want " + want + ")");
            }
            return (true, cases, "seed 13: a drill is charged exactly the decilitres that landed, in level units, never for a brim it did not fill");
        });
        Try("drill_settings_ship", DRILL, "sweep", () =>
        {
            float on = Env("FW_DRILL_ON", -1), y = Env("FW_DRILL_YIELD", -1), u = Env("FW_DRILL_UNITS", -1);
            return (on == 1 && y == 1 && u == 1, 3, "liquidDrillingEnabled " + on + ", drillYieldChanceMultiplier " + y + " (0.1..3), drillUnitsPerCycle " + u + " (0.1..6): defaults on and 1x");
        });
        Row("drill_yield_and_bleed_not_kernel", DRILL, "not_kernel", "UNSETTLED", 0,
            "which maps hold which liquids (the subsurface survey roll) and the bleed well's pour are game-side (RM_MapComponent_SubsurfaceLiquid, Building_LiquidDrill); no kernel decides them offline");
    }

    // ======================================================================== sprinklers (inv_sprinklers)
    const string SPR = "inv_sprinklers";
    static void SprinklerRows()
    {
        int upl = RM_Volume.UnitsPerLitre;
        Try("spr_pump_required_and_decide_order", SPR, "sweep", () =>
        {
            int c = 0;
            for (int m = 0; m < 32; m++)
            foreach (int cells in new[] { 0, 5 }) foreach (int avail in new[] { 0, 24, 25, 1000 })
            {
                bool en = (m & 1) != 0, sw = (m & 2) != 0, pr = (m & 4) != 0, liq = (m & 8) != 0, thick = (m & 16) != 0; c++;
                int need = RM_SprinklerKernel.UnitsFor(cells, 0.5f, upl);
                var st = RM_SprinklerKernel.Decide(en, sw, pr, liq, thick, cells, need, avail);
                if (st == RM_SprinklerState.Spraying && (!en || !sw || !pr || !liq || thick || avail < need || need <= 0)) return (false, c, "sprays without " + (pr ? "its conditions" : "a pump"));
                if (!pr && en && sw && st != RM_SprinklerState.NoPressure) return (false, c, "no pump reads " + st);
                if (en && sw && pr && liq && !thick && cells > 0 && avail < need && st != RM_SprinklerState.Dry) return (false, c, "short net reads " + st + " not Dry");
            }
            return (true, c, "a head sprays only when enabled, switched on, PUMPED, holding a thin liquid and able to pay the whole pulse; no pump reads NoPressure; a short net reads Dry (all or nothing)");
        });
        Try("spr_units_never_free_and_max_cells_exact", SPR, "sweep", () =>
        {
            int c = 0;
            for (float l = 0.1f; l <= 5.0001f; l += 0.05f)
            {
                float lr = (float)Math.Round(l * 20) / 20f;
                int prev = 0;
                for (int cells = 1; cells <= 60; cells++)
                {
                    int u = RM_SprinklerKernel.UnitsFor(cells, lr, upl); c++;
                    if (u <= 0 || u < prev) return (false, c, lr + " L x " + cells + " cells costs " + u);
                    prev = u;
                }
                for (int units = 0; units <= 400; units += 7)
                {
                    int n = RM_SprinklerKernel.MaxCellsFor(units, lr, upl); c++;
                    if (n < 0 || (n > 0 && RM_SprinklerKernel.UnitsFor(n, lr, upl) > units) || RM_SprinklerKernel.UnitsFor(n + 1, lr, upl) <= units)
                        return (false, c, lr + " L/cell/h, " + units + " units: MaxCellsFor " + n);
                }
            }
            float shipped = Env("FW_SPRINKLER_L", -1);
            return (shipped == 0.5f, c, "litres a cell an hour 0.1..5 (step 0.05, the slider's): a pulse is never free, costs rise with cells, MaxCellsFor is the exact largest payable count; shipped " + shipped + " L (ruled 0.5)");
        });
        Try("spr_radius_shipped", SPR, "fixed", () =>
        {
            int Count(float r) { int n = 0; for (int x = -5; x <= 5; x++) for (int z = -5; z <= 5; z++) if (x * x + z * z <= r * r) n++; return n; }
            float shipped = Env("FW_SPRINKLER_R", -1);
            Row("spr_radius_cells", SPR, "info", "INFO", 3, "vanilla GenRadial.NumCellsInRadius counts cells at distance <= radius (RimSage, Verse/GenRadial.cs): radius 2.9 covers " + Count(2.9f) + " cells incl. its own, not the 29 RM_SprinklerKernel.NativeRadius's comment claims (a PROPOSED number, not a bar); choices 1.9/2.9/3.9 cover " + Count(1.9f) + "/" + Count(2.9f) + "/" + Count(3.9f) + "; shipped " + shipped + ". First run of this row FAILed against the comment; the comment is the false statement");
            return (shipped == 2.9f, 1, "the head's radius ships at the kernel's 2.9 (" + shipped + ")");
        });
        Try("spr_valve_random", SPR, "random", () =>
        {
            var r = new Random(17); long c = 0;
            for (int i = 0; i < 30000; i++)
            {
                int n = r.Next(0, 40); var cells = new List<RM_ValveCell>();
                for (int k = 0; k < n; k++) cells.Add(new RM_ValveCell(k, (float)Math.Round(r.NextDouble() * 3, 1), r.Next(4) > 0, r.Next(6) == 0, r.Next(5) == 0, r.Next(5) > 0, r.Next(8) == 0));
                float l = (float)Math.Round(0.1 + r.NextDouble() * 4.9, 2); int budget = r.Next(-1, 200), net = r.Next(0, 300), reserve = r.Next(0, 200);
                var kept = RM_SprinklerKernel.Valve(cells, l, upl, budget, net, reserve, out bool trimmed); c++;
                int cost = RM_SprinklerKernel.UnitsFor(kept.Count, l, upl);
                var wants = cells.Where(RM_SprinklerKernel.ValveWants).ToList();
                if (kept.Any(ix => !RM_SprinklerKernel.ValveWants(cells[ix]))) return (false, c, "watered a cell where water changes nothing");
                if (budget >= 0 && cost > budget) return (false, c, "over the daily budget: " + cost + " > " + budget);
                if (reserve > 0 && net - cost < reserve && kept.Count > 0) return (false, c, "below the reserve floor: net " + net + " - " + cost + " < " + reserve);
                if (trimmed != (kept.Count < wants.Count)) return (false, c, "trimmed flag wrong");
                if (kept.Count > 0 && wants.Count > kept.Count)
                {
                    float far = kept.Max(ix => cells[ix].Dist); var dropped = wants.Where(w => !kept.Contains(w.Index));
                    if (dropped.Any(w => w.Dist < far)) return (false, c, "trimmed a nearer cell before a farther one");
                }
                if (kept.Distinct().Count() != kept.Count) return (false, c, "a cell charged twice");
                var native = RM_SprinklerKernel.NativeCharge(cells);
                if (native.Count != cells.Count(x => !x.Sealed)) return (false, c, "native head skipped an unsealed cell");
            }
            return (true, c, "seed 17, 30000 valves: only cells where water changes growth, nearest first, within the day's budget and above the reserve floor, trimmed flag exact; the native head charges every unsealed cell");
        });
        Try("spr_pick_liquid", SPR, "random", () =>
        {
            var r = new Random(19); string[] keys = { "Water", "Chemfuel", "Blood", "Slime" };
            for (int i = 0; i < 50000; i++)
            {
                var held = new List<KeyValuePair<string, int>>();
                for (int k = r.Next(0, 6); k > 0; k--) held.Add(new KeyValuePair<string, int>(r.Next(6) == 0 ? null : keys[r.Next(4)], r.Next(-3, 20)));
                string got = RM_SprinklerKernel.PickLiquid(held);
                var sums = held.Where(h => h.Key != null && h.Value > 0).GroupBy(h => h.Key).Select(g => (g.Key, g.Sum(x => x.Value))).ToList();
                string want = sums.Count == 0 ? null : sums.OrderByDescending(s => s.Item2).ThenBy(s => s.Key, StringComparer.Ordinal).First().Key;
                if (got != want) return (false, i, "held " + string.Join(",", held) + " picked " + got + " want " + want);
            }
            return (true, 50000, "seed 19: the head sprays the liquid its net holds most of, ties by name, nothing when empty");
        });
        Try("spr_wet_between_pulses", SPR, "fixed", () =>
        {
            var g = new RM_SprinkledGrid(4);
            int t0 = 1000; g.Wet(1, "Water", RM_SprinklerKernel.WetUntil(t0), 7);
            bool cont = g.WetBy(1, t0 + RM_SprinklerKernel.PulseTicks + RM_SprinklerKernel.GraceTicks - 1) == "Water" && g.WetBy(1, t0 + RM_SprinklerKernel.PulseTicks + RM_SprinklerKernel.GraceTicks) == null;
            bool other = g.WetByOther(1, 8, t0 + 10) && !g.WetByOther(1, 7, t0 + 10);
            bool spend = g.Spend(1, t0 + 5) && g.WetBy(1, t0 + 6) == null && !g.Spend(1, t0 + 7) && g.LiveCells(t0 + 8) == 0;
            bool edge = g.WetBy(-1, 0) == null && g.WetBy(9, 0) == null;
            return (cont && other && spend && edge, 4, "a paid pulse keeps the cell wet to the next pulse + 250 ticks grace " + cont + "; another head's water is told apart " + other + "; a fruiting crop spends it " + spend);
        });
        Try("pipe_seat_on_the_drawn_pipe", SPR, "sweep", () =>
        {
            int c = 0;
            foreach (string look in new[] { "Scrapper", "Industrial", "Modern", "Futuristic" })
            for (int mask = 0; mask < 16; mask++)
            {
                RM_PipeSeatMath.Seat(mask, look, out float x, out float z); c++;
                if (!RM_PipeSeatMath.IsElbow(mask)) { if (Math.Abs(x) > 1e-6 || Math.Abs(z) > 1e-6) return (false, c, look + " mask " + mask + " not centred"); continue; }
                float sx = (mask & RM_PipeSeatMath.E) != 0 ? 1 : -1, sz = (mask & RM_PipeSeatMath.N) != 0 ? 1 : -1;
                double d = Math.Sqrt(Math.Pow(x - 0.5 * sx, 2) + Math.Pow(z - 0.5 * sz, 2)); // the arc's centre is the elbow's outer corner, radius 0.5
                if (Math.Abs(d - 0.5) > 1e-4 || x * sx <= 0 || z * sz <= 0) return (false, c, look + " elbow " + mask + " seat (" + x + "," + z + ") is off the arc (" + d + ")");
            }
            RM_PipeSeatMath.Seat(3, "Unknown", out float ux, out float uz);
            bool look2 = RM_PipeSeatMath.LookOfTexPath("Things/Building/Pipe/Modern/Atlas") == "Modern" && RM_PipeSeatMath.LookOfTexPath("a\\Pipe\\Scrapper\\b") == "Scrapper" && RM_PipeSeatMath.LookOfTexPath("Pipe/X") == null;
            return (ux == 0 && uz == 0 && look2, c, "4 looks x 16 masks: straights, tees, ends and the cross sit at the centre; each elbow's seat lies on its quarter arc (radius 0.5 about the outer corner), toward the linked sides; unknown look reads (0,0)");
        });
        Row("spr_net_draw_not_kernel", SPR, "not_kernel", "UNSETTLED", 0,
            "the head sitting on a universal pipe, the pump found on its network and the units drawn from the net are game-side (Building_RM_SprinklerHead, CompRM_SprinklerHead, RM_MapComponent_Sprinklers)");
    }

    // ======================================================================== stage-6 bars: rows written as not_kernel / owed
    static void StageSixRows()
    {
        foreach (var (bar, why) in new[]
        {
            ("inv_fire,canal_fire_burns_back", "fire burns from a real cause, runs back to the source, leaves a spent channel: RM_FireMath holds the timers (DlDue, FrontDue); the burn of a canal is the depth engine's and the walk's. Not spent on in lane 1 for budget"),
            ("inv_dig_depth,canal_reads_as_dug", "dig ladder, deeper digs and fill-in are jobs and designators; RM_DigDepthMath holds limits. Not spent on in lane 1 for budget"),
            ("inv_pits,covered_pit_springs,pit_reads_as_hole", "a pit falls only when forced, drops onto spikes, reads as a hole: game-side (RM_SuperdeepTrap, Building_PitCover, RM_PitLipOcclusion)"),
            ("inv_liquid_net,one_liquid_network", "pumps, tanks, hoses moving real litres: RM_LiquidTransfer is the kernel; not spent on in lane 1 for budget"),
        })
            Row("stage6_" + bar.Split(',')[0], bar, "not_kernel", "UNSETTLED", 0, why);
    }

    static int Main()
    {
        Console.OutputEncoding = new UTF8Encoding(false);
        SheetRows(); ConverterRows(); ThirstRows(); DrillRows(); SprinklerRows(); StageSixRows();
        return fails > 0 ? 1 : 0;
    }
}
