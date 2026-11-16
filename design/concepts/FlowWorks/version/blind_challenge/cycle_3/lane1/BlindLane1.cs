// Blind lane 1 (game logic) for FlowWorks 0.1.0, blind challenge cycle 3 (judge run judge-1794849236).
// Written from the locked bars (record.json inventory rows inv_overflow_sheet, inv_converters, inv_bottles_thirst,
// inv_drilling, inv_sprinklers; sheet.md; plan.md), the shipped kernels and the shipped settings (defaults and slider
// ranges: Sheet/RM_SheetSettings.cs, Machinery/RM_MachinerySettings.cs, Thirst/RM_ThirstSettings.cs,
// Sprinklers/RM_SprinklerSettings.cs) ONLY. The builder's selftests were not read before this file was written and run.
// Output: one JSON line per row on stdout (id, bars, kind, verdict, cases, detail); exit 1 if any row FAILs.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.FlowWorks.Thirst;
using RimMandrake.FlowWorks.Drilling;
using RimMandrake.FlowWorks.Sprinklers;
using SM = RimMandrake.FlowWorks.RM_SheetMath;

static class BlindLane1
{
    static readonly List<string> Out = new List<string>();
    static int fails;

    static string J(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";

    static void Row(string id, string bar, string kind, bool pass, int cases, string detail)
    {
        if (!pass) fails++;
        Out.Add("{\"id\":" + J(id) + ",\"bars\":[" + J(bar) + "],\"kind\":" + J(kind) + ",\"verdict\":" + J(pass ? "PASS" : "FAIL")
            + ",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }

    static void Info(string id, string bar, int cases, string detail) =>
        Out.Add("{\"id\":" + J(id) + ",\"bars\":[" + J(bar) + "],\"kind\":\"info\",\"verdict\":\"INFO\",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");

    // The part of an offline bar no kernel holds (Verse-side wiring). Not decided in lane 1: the bar's kernel part is decided by
    // the rows above it, and lane 2 reads the game-side callers named here. Kept as INFO, not a not_kernel row, because the
    // bar is not game-side as a whole.
    static void GameSide(string id, string bar, string why) =>
        Out.Add("{\"id\":" + J(id) + ",\"bars\":[" + J(bar) + "],\"kind\":\"info\",\"verdict\":\"INFO\",\"cases\":0,\"detail\":" + J("Not decided in lane 1 (game-side part, read in lane 2): " + why) + "}");

    const string SHEET = "inv_overflow_sheet", CONV = "inv_converters", THIRST = "inv_bottles_thirst", DRILL = "inv_drilling", SPRINK = "inv_sprinklers";
    const int CM = SM.DlPerCm;

    // ================================================================ sheet world builders
    sealed class Rig
    {
        public SM.World W; public SM.State S; public SM.Params P; public SM.PulseReport R = new SM.PulseReport();
    }

    static Rig Enclosed(int w, int h, uint salt, SM.Params p)
    {
        var r = new Rig { W = new SM.World(w, h), S = new SM.State(w, h, salt), P = p };
        for (int z = 0; z < h; z++)
            for (int x = 0; x < w; x++)
                r.W.Kinds[z * w + x] = (x == 0 || z == 0 || x == w - 1 || z == h - 1) ? SM.Kind.Blocked : SM.Kind.Open;
        return r;
    }

    static int Spill(Rig r, int amount, byte fluid, SM.Source src, params int[] lips) =>
        SM.ResolveSpills(r.S, r.W, r.P, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = lips, AmountDl = amount, Fluid = fluid, From = src } })[0];

    static long Sum(int[] a) { long s = 0; foreach (int v in a) s += v; return s; }

    // full structural check of a state; returns null when fine
    static string Check(Rig r, string where)
    {
        var s = r.S; var w = r.W; var p = r.P;
        if (!s.LedgerCloses) return where + ": ledger open In=" + s.TotalIn + " Standing=" + s.Standing + " Out=" + s.TotalOut;
        long direct = Sum(s.Dl);
        if (direct != s.Standing) return where + ": Standing " + s.Standing + " != sum of Dl " + direct + " (Occ out of step)";
        var occ = s.Occ;
        for (int i = 1; i < occ.Count; i++) if (occ[i] <= occ[i - 1]) return where + ": Occ not strictly ascending at " + i;
        int wet = 0;
        for (int c = 0; c < s.Dl.Length; c++)
        {
            if (s.Dl[c] < 0) return where + ": negative Dl at " + c + " = " + s.Dl[c];
            if (s.Dl[c] > 0) { wet++; if (s.Fluid[c] == 0) return where + ": wet cell " + c + " has no fluid"; if (!SM.World.HoldsSheet(w.Kinds[c])) return where + ": sheet water on a non-sheet cell " + c + " kind " + w.Kinds[c]; }
            else if (s.Fluid[c] != 0) return where + ": dry cell " + c + " keeps fluid " + s.Fluid[c];
            if (w.RoomDl[c] < 0) return where + ": receiver room negative at " + c;
        }
        if (wet != occ.Count) return where + ": Occ count " + occ.Count + " != wet cells " + wet;
        return null;
    }

    // a random world for the conservation fuzz
    static Rig RandomRig(Random rng, int w, int h, SM.Params p)
    {
        var r = new Rig { W = new SM.World(w, h), S = new SM.State(w, h, (uint)rng.Next()), P = p };
        for (int c = 0; c < w * h; c++)
        {
            int k = rng.Next(100);
            r.W.Kinds[c] = k < 62 ? SM.Kind.Open : k < 74 ? SM.Kind.Blocked : k < 80 ? SM.Kind.Door : k < 86 ? SM.Kind.Grate : k < 96 ? SM.Kind.Receiver : SM.Kind.Sink;
            if (r.W.Kinds[c] == SM.Kind.Receiver) r.W.RoomDl[c] = rng.Next(0, 20 * CM);
            if (r.W.Kinds[c] == SM.Kind.Receiver || r.W.Kinds[c] == SM.Kind.Sink) r.W.BodyFluid[c] = (byte)(rng.Next(3) == 0 ? rng.Next(1, 4) : 0);
            r.W.SoakMilliDl[c] = rng.Next(3) == 0 ? 0 : rng.Next(0, 2000);
            r.W.EvapMilliDl[c] = rng.Next(3) == 0 ? 0 : rng.Next(0, 1200);
            r.W.TempDeciC[c] = rng.Next(-60, 300);
        }
        r.W.Fluids[2] = new SM.FluidRule { InfiltrationPermille = 300, EvaporationPermille = 200, NeverFreezes = true };
        r.W.Fluids[3] = new SM.FluidRule { InfiltrationPermille = 0, EvaporationPermille = 0, NeverFreezes = true, BoilMilliDl = 900, BoilAboveDeciC = -420 };
        return r;
    }

    static SM.Params ParamsFrom(int capCm, int maxWet, float retentionCm, int sweeps, int doorPct)
    {
        // as the settings page sets them (RM_SheetSettings: cap 5-100 cm, wet squares 500-20000, retention 0.5-5 cm, sweeps 1-6, door 0-50 %)
        return new SM.Params
        {
            SheetCapDl = capCm * CM, MaxWetCells = maxWet, RetentionDl = (int)Math.Round(retentionCm * CM), SweepsPerPulse = sweeps,
            DoorLeakPermille = doorPct * 10,
        };
    }

    // one fuzz run; returns null or the failure text (with pulse index)
    static string FuzzRun(int seed, int w, int h, int pulses, SM.Params p, bool lowerCapMidway)
    {
        var rng = new Random(seed);
        var r = RandomRig(rng, w, h, p);
        int n = w * h;
        string e;
        for (int t = 0; t < pulses; t++)
        {
            if (lowerCapMidway && t == pulses / 2) p.SheetCapDl = Math.Max(CM, p.SheetCapDl / 3);
            // offers
            int no = rng.Next(0, 4);
            var offers = new List<SM.SpillOffer>();
            for (int o = 0; o < no; o++)
            {
                int nl = rng.Next(1, 6);
                var lips = new int[nl];
                for (int i = 0; i < nl; i++) lips[i] = rng.Next(-1, n + 1);
                offers.Add(new SM.SpillOffer { LipNearestFirst = lips, AmountDl = rng.Next(-5, 60 * CM), Fluid = (byte)rng.Next(0, 4), From = (SM.Source)rng.Next(0, SM.SourceCount) });
            }
            long inBefore = r.S.TotalIn;
            int[] acc = SM.ResolveSpills(r.S, r.W, r.P, offers);
            for (int o = 0; o < offers.Count; o++)
            {
                if (acc[o] < 0 || acc[o] > Math.Max(0, offers[o].AmountDl)) return "pulse " + t + ": offer " + o + " accepted " + acc[o] + " of " + offers[o].AmountDl;
            }
            if (r.S.TotalIn - inBefore != acc.Sum()) return "pulse " + t + ": In rose " + (r.S.TotalIn - inBefore) + " but accepted " + acc.Sum();
            for (int c = 0; c < n; c++) if (r.S.Dl[c] > p.SheetCapDl && !lowerCapMidway) return "pulse " + t + ": spill put " + r.S.Dl[c] + " dL over the cap " + p.SheetCapDl + " at " + c;
            if ((e = Check(r, "after spills pulse " + t)) != null) return e;
            // temperature drift (freeze / thaw)
            if (rng.Next(5) == 0) for (int c = 0; c < n; c++) r.W.TempDeciC[c] = rng.Next(-60, 300);
            var fluidBefore = (byte[])r.S.Fluid.Clone();
            var roomBefore = (int[])r.W.RoomDl.Clone();
            var bodyBefore = (byte[])r.W.BodyFluid.Clone();
            long retBefore = r.S.Returned;
            int[] dlBefore = (int[])r.S.Dl.Clone();
            SM.Pulse(r.S, r.W, r.P, r.R);
            if ((e = Check(r, "after pulse " + t)) != null) return e;
            for (int c = 0; c < n; c++)
            {
                if (fluidBefore[c] != 0 && r.S.Fluid[c] != 0 && fluidBefore[c] != r.S.Fluid[c]) return "pulse " + t + ": cell " + c + " changed liquid " + fluidBefore[c] + " -> " + r.S.Fluid[c] + " (liquids mixed)";
                if (bodyBefore[c] != 0 && r.W.BodyFluid[c] != bodyBefore[c]) return "pulse " + t + ": receiver " + c + " changed body liquid";
                if (r.S.Dl[c] > p.SheetCapDl && r.S.Dl[c] > dlBefore[c]) return "pulse " + t + ": cell " + c + " rose to " + r.S.Dl[c] + " above the cap " + p.SheetCapDl;
            }
            long roomDrop = Sum(roomBefore) - Sum(r.W.RoomDl), retRise = r.S.Returned - retBefore;
            if (roomDrop != retRise) return "pulse " + t + ": receivers took " + roomDrop + " dL but Returned rose " + retRise;
            long repSum = r.R.Returned.Sum(x => (long)x.dl);
            if (repSum != retRise) return "pulse " + t + ": report Returned " + repSum + " != " + retRise;
            if (r.S.WetCount > p.MaxWetCells) return "pulse " + t + ": " + r.S.WetCount + " wet cells over the cap " + p.MaxWetCells;
            // exits by hand
            int pick = rng.Next(n);
            int act = rng.Next(40);
            if (act == 0 && r.S.Dl[pick] > 0) SM.Burn(r.S, pick, rng.Next(1, 3 * CM));
            else if (act == 1 && r.S.Dl[pick] > 0) SM.HandOver(r.S, pick, rng.Next(1, 3 * CM), rng.Next(2) == 0);
            else if (act == 2) SM.PurgeConnected(r.S, pick, rng.Next(3) == 0 ? SM.AllDl : rng.Next(-2, 10 * CM));
            else if (act == 3 && rng.Next(4) == 0) SM.PurgeAll(r.S);
            if ((e = Check(r, "after hand exit pulse " + t)) != null) return e;
        }
        return null;
    }

    static void SheetConservation()
    {
        // random worlds, shipped params
        int cases = 0; string fail = null; int failSeed = -1;
        for (int seed = 1; seed <= 300 && fail == null; seed++)
        {
            var rng = new Random(seed * 7919);
            int w = rng.Next(3, 15), h = rng.Next(3, 15);
            fail = FuzzRun(seed, w, h, 120, new SM.Params(), false); cases++;
            if (fail != null) failSeed = seed;
        }
        string shrunk = "";
        if (fail != null)
        {
            // shrink: same seed, smallest grid that still fails, then the first pulse it fails at
            for (int sz = 3; sz <= 14; sz++) { string f2 = FuzzRun(failSeed, sz, sz, 120, new SM.Params(), false); if (f2 != null) { shrunk = " shrunk: seed " + failSeed + " grid " + sz + "x" + sz + " -> " + f2; break; } }
        }
        Row("SHEET_LEDGER_CLOSES_RANDOM", SHEET, "random", fail == null, cases,
            fail == null ? "300 random worlds (seeds 1-300, grids 3-14, 120 pulses, every kind, 3 liquids, freeze/thaw, burns, hand-overs, purges): In == Standing + Returned + JoinedLake + Soaked + Evaporated + Burned + Purged after every step; no negative cell; no wet cell without a liquid; Occ in step; no liquid changed in a wet cell; receivers' room drop == Returned rise == report; wet count <= cap"
            : "seed " + failSeed + ": " + fail + shrunk);
    }

    static void SheetSettingsSweep()
    {
        int[] caps = { 5, 50, 100 }; int[] wets = { 500, 4000, 20000 }; float[] rets = { 0.5f, 1f, 5f }; int[] sweeps = { 1, 3, 6 }; int[] doors = { 0, 5, 50 };
        int cases = 0; var fl = new List<string>();
        foreach (int cap in caps) foreach (int wt in wets) foreach (float rt in rets) foreach (int sw in sweeps) foreach (int dr in doors)
        {
            cases++;
            var p = ParamsFrom(cap, wt, rt, sw, dr);
            string f = FuzzRun(1000 + cases, 9, 9, 60, p, false);
            if (f != null && fl.Count < 3) fl.Add("cap " + cap + " wet " + wt + " ret " + rt + " sweeps " + sw + " door " + dr + "%: " + f);
        }
        // the cap lowered mid-game deletes nothing and grows nothing above the new cap
        int capCases = 0;
        for (int seed = 1; seed <= 40; seed++) { capCases++; string f = FuzzRun(5000 + seed, 8, 8, 80, new SM.Params(), true); if (f != null && fl.Count < 3) fl.Add("lowered cap seed " + (5000 + seed) + ": " + f); }
        // small wet cap: the cap is honoured even at 500
        Row("SHEET_SETTINGS_SWEEP_CONSERVES", SHEET, "sweep", fl.Count == 0, cases + capCases,
            fl.Count == 0 ? "every combination of sheet cap {5,50,100} cm x wet squares {500,4000,20000} x retention {0.5,1,5} cm x steps {1,3,6} x door leak {0,5,50} % (243 runs, 60 pulses each) plus 40 runs with the cap lowered to a third midway: ledger closes, no cell over the cap rises, wet count under its cap"
            : string.Join(" | ", fl));
    }

    static void SheetLevel()
    {
        // D8 "sheets lie level": an enclosed 12x12 yard, no losses, 8 cm per square poured in at one corner
        var p = new SM.Params();
        var r = Enclosed(14, 14, 12345u, p);
        int perPulse = 144 * 8 * CM / 20;
        for (int t = 0; t < 20; t++) { Spill(r, perPulse, 1, SM.Source.Pump, 15); SM.Pulse(r.S, r.W, p, r.R); }
        for (int t = 0; t < 200; t++) SM.Pulse(r.S, r.W, p, r.R);
        long lo = long.MaxValue, hi = long.MinValue; int wet = 0;
        for (int c = 0; c < r.S.Dl.Length; c++)
        {
            if (r.W.Kinds[c] != SM.Kind.Open) continue;
            if (r.S.Dl[c] > 0) wet++;
            long surf = r.S.Dl[c] + SM.Relief(r.S.Salt, c, p.ReliefDl);
            lo = Math.Min(lo, surf); hi = Math.Max(hi, surf);
        }
        bool ok = wet == 144 && hi - lo <= 1 && r.S.LedgerCloses;
        Row("SHEET_STILL_POOL_ONE_LEVEL", SHEET, "fixed", ok, 1,
            "12x12 walled yard, 8 cm a square poured at a corner over 20 pulses, 200 more pulses, no soak/evaporation: wet " + wet + "/144, surface (depth + relief) spread " + (hi - lo) + " dL (want <= 1)");
    }

    static void SheetSpreadStops()
    {
        // "spreads until it is about 1 cm deep" (settings text) on open ground, then stops: a 400-square field, 60 cm·squares spilled at the centre
        var p = new SM.Params();
        var r = Enclosed(42, 42, 777u, p);
        int centre = 21 * 42 + 21;
        int vol = 60 * CM;
        int got = 0;
        for (int t = 0; t < 10 && got < vol; t++) { got += Spill(r, vol - got, 1, SM.Source.Rain, centre); SM.Pulse(r.S, r.W, p, r.R); }
        for (int t = 0; t < 400; t++) SM.Pulse(r.S, r.W, p, r.R);
        int wet = r.S.WetCount; double mean = wet == 0 ? 0 : (double)r.S.Standing / wet / CM;
        bool touchesWall = false;
        for (int c = 0; c < r.S.Dl.Length; c++) if (r.S.Dl[c] > 0) { int x = c % 42, z = c / 42; if (x <= 1 || z <= 1 || x >= 40 || z >= 40) touchesWall = true; }
        bool ok = got == vol && wet > 1 && mean >= 0.5 && mean <= 3.0 && !touchesWall && r.S.LedgerCloses;
        Row("SHEET_SPREAD_STOPS_NEAR_RETENTION", SHEET, "fixed", ok, 1,
            "60 cm·squares spilled at the centre of a 40x40 field, 410 pulses, no losses: accepted " + got + " dL, " + wet + " squares wet, mean depth " + mean.ToString("0.00") + " cm (want 0.5-3), reached the wall " + touchesWall);
    }

    static void SheetCropWeek()
    {
        var p = new SM.Params();
        int center = 2 * 5 + 2;
        // 5 cm standing: first CropDrowning report at pulse CropKillPulses (1680 x 250 ticks = 7 days)
        var r = Enclosed(5, 5, 1u, p);
        Spill(r, 9 * 5 * CM, 1, SM.Source.Pump, 6, 7, 8, 11, 12, 13, 16, 17, 18);
        int first = -1;
        for (int t = 1; t <= p.CropKillPulses + 5; t++)
        {
            SM.Pulse(r.S, r.W, p, r.R);
            if (first < 0 && r.R.CropDrowning.Any(x => x.cell == center)) first = t;
        }
        bool okWeek = first == p.CropKillPulses && (long)p.CropKillPulses * 250 == 7L * 60000;
        // a crop younger than the delay never drowns; one at least that old does
        bool okAge = !SM.CropDrowns(p.CropKillPulses, p.CropKillPulses * 250 - 1, 250, p) && SM.CropDrowns(p.CropKillPulses, p.CropKillPulses * 250, 250, p)
            && !SM.CropDrowns(p.CropKillPulses - 1, int.MaxValue, 250, p);
        Row("SHEET_CROP_DROWNS_AFTER_A_WEEK", SHEET, "fixed", okWeek && okAge, 4,
            "5 cm standing on a crop: first drowning report at pulse " + first + " (want " + p.CropKillPulses + " = 7 days at 250 ticks); crop age gate " + okAge);
        // a film (1.5 cm) never drowns a crop
        var f = Enclosed(5, 5, 2u, p);
        Spill(f, 9 * 3 * CM / 2, 1, SM.Source.Pump, 6, 7, 8, 11, 12, 13, 16, 17, 18);
        bool anyFilm = false;
        for (int t = 0; t < p.CropKillPulses * 2; t++) { SM.Pulse(f.S, f.W, p, f.R); if (f.R.CropDrowning.Count > 0) anyFilm = true; }
        Row("SHEET_FILM_NEVER_DROWNS", SHEET, "fixed", !anyFilm, 1, "1.5 cm film for two weeks: drowning reports " + anyFilm);
        // 2.5 cm risen from dry: the settings text says "water at least 2 cm deep standing on a plant for the whole delay kills it"
        var g = Enclosed(5, 5, 3u, p);
        Spill(g, 9 * 5 * CM / 2, 1, SM.Source.Pump, 6, 7, 8, 11, 12, 13, 16, 17, 18);
        bool any25 = false;
        for (int t = 0; t < p.CropKillPulses + 10; t++) { SM.Pulse(g.S, g.W, p, g.R); if (g.R.CropDrowning.Count > 0) any25 = true; }
        Info("SHEET_CROP_TWO_AND_A_HALF_CM_RISEN", SHEET, 1,
            "2.5 cm risen from dry, one week + 10 pulses: drowning reported " + any25 + ". The kernel's 'standing' tier is Sheet, entered at " + p.SheetUpDl / CM
            + " cm rising and left below " + p.SheetDownDl / CM + " cm; the Mod Settings tooltip says 'at least 2 cm deep ... kills it'. Read in lane 2: the words or the tier.");
    }

    static void SheetCropSlider()
    {
        // the delay keeps its days whatever the flow-pulse slider (60-2500 ticks) and the days slider (0.5-30)
        int cases = 0; var bad = new List<string>();
        for (int pi = 60; pi <= 2500; pi += 10)
        {
            for (double days = 0.5; days <= 30.0001; days += 0.5)
            {
                cases++;
                int ticks = (int)Math.Round(days * 60000);
                int stored = Math.Max(1, SM.PulsesFor(ticks, SM.CropDelayBasePulseTicks));
                int kill = SM.CropKillPulsesFor(stored, pi);
                long got = (long)kill * pi;
                if (got < ticks || got >= ticks + pi + SM.CropDelayBasePulseTicks) { if (bad.Count < 3) bad.Add("pulse " + pi + " days " + days + ": " + got + " ticks"); }
            }
        }
        Row("SHEET_CROP_DELAY_FOLLOWS_SLIDERS", SHEET, "sweep", bad.Count == 0, cases,
            bad.Count == 0 ? "flow pulse 60-2500 (step 10) x delay 0.5-30 days (step 0.5): the kill delay in ticks is the slider's days, rounded up by less than one pulse" : string.Join("; ", bad));
    }

    static void SheetSaveLoad()
    {
        int cases = 0; string fail = null;
        for (int seed = 1; seed <= 60 && fail == null; seed++)
        {
            cases++;
            var rngA = new Random(seed); var a = RandomRig(rngA, 10, 10, new SM.Params());
            var rngB = new Random(seed); var b = RandomRig(rngB, 10, 10, new SM.Params());
            var drive = new Random(seed * 31);
            var offersPlan = new List<List<SM.SpillOffer>>();
            for (int t = 0; t < 80; t++)
            {
                var l = new List<SM.SpillOffer>();
                if (drive.Next(3) == 0) l.Add(new SM.SpillOffer { LipNearestFirst = new[] { drive.Next(100), drive.Next(100) }, AmountDl = drive.Next(1, 30 * CM), Fluid = (byte)drive.Next(1, 4), From = SM.Source.Pump });
                offersPlan.Add(l);
            }
            for (int t = 0; t < 80; t++)
            {
                SM.ResolveSpills(a.S, a.W, a.P, offersPlan[t]); SM.Pulse(a.S, a.W, a.P, null);
                if (t == 39) { byte[] bytes = SM.Save(b.S); b.S = SM.Load(bytes); }
                SM.ResolveSpills(b.S, b.W, b.P, offersPlan[t]); SM.Pulse(b.S, b.W, b.P, null);
                if (t == 38) { /* b runs the same as a up to here */ }
                if (SM.Hash(a.S) != SM.Hash(b.S)) { fail = "seed " + seed + ": hash splits at pulse " + t + " after a save/load at pulse 39"; break; }
            }
        }
        // kind memory: a save/load between generations gives the same Changed answers
        int kmCases = 0; string kmFail = null;
        for (int seed = 1; seed <= 100 && kmFail == null; seed++)
        {
            kmCases++;
            var rng = new Random(seed);
            var m1 = new SM.KindMemory(50); var m2 = new SM.KindMemory(50);
            for (int g = 0; g < 30; g++)
            {
                m1.NextGeneration(); m2.NextGeneration();
                if (g == 15) m2 = SM.KindMemory.Load(m2.Save(), 50);
                for (int k = 0; k < 12; k++)
                {
                    int c = rng.Next(50); var kind = (SM.Kind)rng.Next(0, 6);
                    if (m1.Changed(c, kind) != m2.Changed(c, kind)) { kmFail = "seed " + seed + " gen " + g + " cell " + c; break; }
                }
                if (kmFail != null) break;
            }
        }
        Row("SHEET_SAVE_LOAD_CONTINUES_IDENTICAL", SHEET, "random", fail == null && kmFail == null, cases + kmCases,
            (fail ?? "60 random 10x10 worlds, 80 pulses, save/load at pulse 39: the state hash matches the uninterrupted run every pulse") + "; kind memory: " + (kmFail ?? "100 random sequences, save/load at generation 15, Changed() identical"));
    }

    static void SheetOffers()
    {
        // order independence and preview == resolve
        int cases = 0; string fail = null;
        for (int seed = 1; seed <= 300 && fail == null; seed++)
        {
            cases++;
            var rng = new Random(seed);
            var p = new SM.Params { MaxWetCells = rng.Next(1, 40), SheetCapDl = rng.Next(1, 10) * CM };
            var r1 = RandomRig(new Random(seed), 8, 8, p); var r2 = RandomRig(new Random(seed), 8, 8, p);
            // pre-wet some cells identically
            var pre = new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 9, 10, 11 }, AmountDl = 5 * CM, Fluid = 1, From = SM.Source.Rain } };
            SM.ResolveSpills(r1.S, r1.W, p, pre); SM.ResolveSpills(r2.S, r2.W, p, pre);
            var offers = new List<SM.SpillOffer>();
            int no = rng.Next(1, 6);
            for (int o = 0; o < no; o++)
            {
                var lips = Enumerable.Range(0, rng.Next(1, 8)).Select(_ => rng.Next(64)).ToArray();
                offers.Add(new SM.SpillOffer { LipNearestFirst = lips, AmountDl = rng.Next(1, 40 * CM), Fluid = (byte)rng.Next(1, 4), From = (SM.Source)rng.Next(0, 5) });
            }
            if (no == 1)
            {
                int prev = SM.PreviewSpill(r1.S, r1.W, p, offers[0]);
                int got = SM.ResolveSpills(r1.S, r1.W, p, offers)[0];
                SM.ResolveSpills(r2.S, r2.W, p, offers);
                if (prev != got) fail = "seed " + seed + ": preview " + prev + " != resolve " + got;
                continue;
            }
            var perm = Enumerable.Range(0, no).OrderBy(_ => rng.Next()).ToArray();
            var shuffled = perm.Select(i => offers[i]).ToList();
            int[] a1 = SM.ResolveSpills(r1.S, r1.W, p, offers);
            int[] a2 = SM.ResolveSpills(r2.S, r2.W, p, shuffled);
            for (int k = 0; k < no; k++) if (a2[k] != a1[perm[k]]) fail = "seed " + seed + ": offer order changed what offer " + perm[k] + " got (" + a1[perm[k]] + " vs " + a2[k] + ")";
            if (fail == null && SM.Hash(r1.S) != SM.Hash(r2.S)) fail = "seed " + seed + ": offer order changed the state";
        }
        Row("SHEET_SPILLS_ORDER_FREE_AND_PREVIEW_EXACT", SHEET, "random", fail == null, cases,
            fail ?? "300 random offer sets (seeds 1-300): accepted dL per offer and the resulting state do not depend on the order offers arrive; PreviewSpill equals ResolveSpills for a single offer");
    }

    static void SheetDoors()
    {
        // a wall with one door; water on one side only
        Func<int, SM.Kind, (long other, bool ok)> run = (permille, gateKind) =>
        {
            var p = new SM.Params { DoorLeakPermille = permille };
            var r = Enclosed(13, 7, 99u, p);
            for (int z = 1; z < 6; z++) r.W.Kinds[z * 13 + 6] = SM.Kind.Blocked;
            r.W.Kinds[3 * 13 + 6] = gateKind;
            for (int t = 0; t < 10; t++) Spill(r, 25 * 5 * 3 * CM / 10, 1, SM.Source.Pump, 3 * 13 + 2, 2 * 13 + 2, 4 * 13 + 2);
            for (int t = 0; t < 300; t++) SM.Pulse(r.S, r.W, p, r.R);
            long other = 0; for (int z = 1; z < 6; z++) for (int x = 7; x < 12; x++) other += r.S.Dl[z * 13 + x];
            return (other, r.S.LedgerCloses);
        };
        var sealedDoor = run(0, SM.Kind.Door); var leak5 = run(50, SM.Kind.Door); var grate = run(50, SM.Kind.Grate); var wall = run(50, SM.Kind.Blocked);
        bool ok = sealedDoor.other == 0 && wall.other == 0 && leak5.other > 0 && grate.other > leak5.other && sealedDoor.ok && leak5.ok && grate.ok;
        Row("SHEET_DOOR_LEAKS_SLOWLY_GRATE_PASSES", SHEET, "fixed", ok, 4,
            "water beyond a wall after 300 pulses: door at 0% " + sealedDoor.other + " dL (want 0), wall " + wall.other + " (want 0), door at 5% " + leak5.other + " (want > 0), grate " + grate.other + " (want more than the door)");
    }

    static void SheetReceivers()
    {
        var p = new SM.Params();
        // a pool beside a dug cell with 3 cm of room, one beside a foreign-liquid body, one beside the lake
        var r = Enclosed(9, 5, 5u, p);
        int recv = 1 * 9 + 1, foreign = 1 * 9 + 4, sink = 1 * 9 + 7;
        r.W.Kinds[recv] = SM.Kind.Receiver; r.W.RoomDl[recv] = 3 * CM;
        r.W.Kinds[foreign] = SM.Kind.Receiver; r.W.RoomDl[foreign] = 50 * CM; r.W.BodyFluid[foreign] = 2;
        r.W.Kinds[sink] = SM.Kind.Sink;
        for (int c = 0; c < 45; c++) if (c % 9 == 3 || c % 9 == 6) r.W.Kinds[c] = SM.Kind.Blocked; // three separate bays
        Spill(r, 10 * CM, 1, SM.Source.Pump, 2 * 9 + 1); Spill(r, 10 * CM, 1, SM.Source.Pump, 2 * 9 + 4); Spill(r, 10 * CM, 1, SM.Source.Pump, 2 * 9 + 7);
        for (int t = 0; t < 100; t++) SM.Pulse(r.S, r.W, p, r.R);
        long bay(int x0) { long s = 0; for (int z = 1; z < 4; z++) for (int x = x0; x < x0 + 2; x++) s += r.S.Dl[z * 9 + x]; return s; }
        bool ok = r.S.Returned == 3 * CM && r.W.RoomDl[recv] == 0 && r.W.RoomDl[foreign] == 50 * CM && r.S.JoinedLake > 0 && r.S.LedgerCloses
                  && bay(4) == 10 * CM;
        Row("SHEET_RETURNS_TO_ROOM_ONLY", SHEET, "fixed", ok, 3,
            "dug cell with 3 cm room took " + r.S.Returned + " dL (want " + 3 * CM + "), foreign-liquid body room left " + r.W.RoomDl[foreign] + " (want untouched), foreign bay keeps " + bay(4) + " dL (want " + 10 * CM + "), lake took " + r.S.JoinedLake);
    }

    static void SheetIceKeepsWater()
    {
        var p = new SM.Params();
        var r = Enclosed(6, 6, 8u, p);
        for (int c = 0; c < 36; c++) r.W.TempDeciC[c] = -50;
        Spill(r, 16 * 4 * CM, 1, SM.Source.Rain, 7, 8, 9, 10, 13, 14, 15, 16, 19, 20, 21, 22, 25, 26, 27, 28);
        long before = r.S.Standing;
        bool allIce = true;
        for (int t = 0; t < 30; t++) SM.Pulse(r.S, r.W, p, r.R);
        for (int c = 0; c < 36; c++) if (r.S.Dl[c] > 0 && r.S.Tiers[c] != SM.Tier.Ice) allIce = false;
        // a new spill on ice is refused
        int onIce = Spill(r, 5 * CM, 1, SM.Source.Pump, 7);
        for (int c = 0; c < 36; c++) r.W.TempDeciC[c] = 50;
        for (int t = 0; t < 5; t++) SM.Pulse(r.S, r.W, p, r.R);
        bool thawed = true; for (int c = 0; c < 36; c++) if (r.S.Dl[c] > 0 && r.S.Tiers[c] == SM.Tier.Ice) thawed = false;
        bool ok = allIce && r.S.Standing == before && onIce == 0 && thawed && r.S.LedgerCloses;
        Row("SHEET_ICE_KEEPS_EVERY_DL", SHEET, "fixed", ok, 1, "4 cm frozen at -5 C for 30 pulses then thawed at +5 C: all ice " + allIce + ", standing " + before + " -> " + r.S.Standing + ", spill onto ice accepted " + onIce + " (want 0), thawed " + thawed);
    }

    static void SheetSoakRate()
    {
        // remainder carrying: a soak rate of k milli-dL per pulse removes exactly floor(P*k/1000) over P pulses from a deep pool
        int cases = 0; var bad = new List<string>();
        foreach (int rate in new[] { 1, 37, 333, 999, 1000, 1001, 2777 })
        {
            cases++;
            var p = new SM.Params { LevelBasins = false };
            var r = Enclosed(3, 3, 1u, p);
            r.W.SoakMilliDl[4] = rate;
            Spill(r, 40 * CM, 1, SM.Source.Pump, 4);
            int P = 500;
            for (int t = 0; t < P; t++) SM.Pulse(r.S, r.W, p, r.R);
            long want = (long)P * rate / 1000;
            if (r.S.Soaked != want && bad.Count < 3) bad.Add("rate " + rate + ": soaked " + r.S.Soaked + " want " + want);
        }
        // shipped evaporation formula: 0.5 cm a day at 20 C in the open, scaled by heat (cap 3x), roof 30 %, none at or below 0
        int ev20 = RM_SheetTemp.EvapMilliDl(20 * 16, 0.5f, 3f, 1f, CM, 240f);
        int ev20roof = RM_SheetTemp.EvapMilliDl(20 * 16, 0.5f, 3f, 0.3f, CM, 240f);
        int ev0 = RM_SheetTemp.EvapMilliDl(0, 0.5f, 3f, 1f, CM, 240f), evNeg = RM_SheetTemp.EvapMilliDl(-16, 0.5f, 3f, 1f, CM, 240f);
        int ev100 = RM_SheetTemp.EvapMilliDl(100 * 16, 0.5f, 3f, 1f, CM, 240f);
        bool mono = true; int last = 0;
        for (int q = -100; q <= 120 * 16; q++) { int e = RM_SheetTemp.EvapMilliDl(q, 0.5f, 3f, 1f, CM, 240f); if (e < last) mono = false; last = e; }
        double cmPerDay = ev20 * 240.0 / 1000 / CM;
        bool evOk = Math.Abs(cmPerDay - 0.5) < 0.01 && ev0 == 0 && evNeg == 0 && ev100 == 3 * ev20 - (3 * ev20 - ev100) && ev100 <= 3 * ev20 + 1 && ev100 >= 3 * ev20 - 1 && Math.Abs(ev20roof - 0.3 * ev20) <= 1 && mono;
        Row("SHEET_SOAK_AND_DRY_RATES", SHEET, "fixed", bad.Count == 0 && evOk, cases + 5,
            (bad.Count == 0 ? "soak remainders carried exactly for 7 rates over 500 pulses" : string.Join("; ", bad)) + "; evaporation at 20 C open " + ev20 + " milli-dL/pulse = " + cmPerDay.ToString("0.000") + " cm/day (want 0.5), roofed " + ev20roof + ", 0 C " + ev0 + ", -1 C " + evNeg + ", 100 C " + ev100 + " (cap 3x), monotone " + mono);
    }

    static void SheetLiquids()
    {
        var water = RM_SheetFluidMath.RuleFor(false, false, false, 60, -1, -1);
        var tar = RM_SheetFluidMath.RuleFor(true, false, false, 600, -1, -1);
        var hot = RM_SheetFluidMath.RuleFor(false, true, false, 60, -1, -1);
        var slime = RM_SheetFluidMath.RuleFor(false, false, true, 6000, -1, -1);
        var authored = RM_SheetFluidMath.RuleFor(false, false, false, 60, 25, 0);
        bool ok = water.InfiltrationPermille == 1000 && !water.NeverFreezes && water.FreezeDeciC == 0
            && tar.InfiltrationPermille == 100 && tar.NeverFreezes && hot.EvaporationPermille == 3000 && hot.NeverFreezes
            && slime.InfiltrationPermille == 100 && slime.NeverFreezes && authored.InfiltrationPermille == 250 && authored.EvaporationPermille == 0
            && RM_SheetFluidMath.PutsOutFire(false) && !RM_SheetFluidMath.PutsOutFire(true);
        Row("SHEET_EACH_LIQUID_BY_ITS_NATURE", SHEET, "fixed", ok, 6,
            "water soak/evap/freeze " + water.InfiltrationPermille + "/" + water.EvaporationPermille + "/" + !water.NeverFreezes + "; tar (10x thicker, burnable) soak " + tar.InfiltrationPermille + " never freezes " + tar.NeverFreezes + "; hot evap " + hot.EvaporationPermille + "; slime soak " + slime.InfiltrationPermille + "; authored soak and evaporation percentages (25 and 0) honoured; only non-burning liquids put out fire");
        // master and inflow switches: AcceptsSpill truth table
        int bad = 0, cases = 0;
        foreach (bool spillsFrom in new[] { false, true }) foreach (bool engine in new[] { false, true }) foreach (bool has in new[] { false, true })
        foreach (bool isWater in new[] { false, true }) foreach (bool other in new[] { false, true }) foreach (bool force in new[] { false, true })
        {
            cases++;
            bool want = engine && has && (force || (spillsFrom && (isWater || other)));
            if (SM.AcceptsSpill(spillsFrom, engine, has, isWater, other, force) != want) bad++;
        }
        Row("SHEET_SWITCHES_GATE_EVERY_SPILL", SHEET, "sweep", bad == 0, cases, "every combination of inflow switch x depth engine x known liquid x water x other-liquids switch x dev force: " + bad + " wrong");
        GameSide("SHEET_SWITCH_WIRING_GAME_SIDE", SHEET, "Which inflow reads which switch (RM_SheetSettings.SpillsFrom, the component's callers) and that 'off' refuses at the brim or discloses as lost is Verse-side; lane 2 reads the callers. The kernel's gate is decided by SHEET_SWITCHES_GATE_EVERY_SPILL.");
    }

    static void FloodRelease()
    {
        int cases = 0; string fail = null;
        var rng = new Random(424242);
        for (int k = 0; k < 20000 && fail == null; k++)
        {
            cases++;
            long start = rng.Next(-5, 200000);
            var L = RM_FloodReleaseMath.Ledger.Start(start);
            for (int st = 0; st < 30; st++)
            {
                long per = RM_FloodReleaseMath.PerTileDl((float)(rng.NextDouble() * 2));
                int a = rng.Next(4);
                if (a == 0) { long room = rng.Next(-5, 30000); bool exact = rng.Next(2) == 0; long pour = RM_FloodReleaseMath.DugPourDl(L.Remaining, room, exact);
                    if (pour > L.Remaining || pour > Math.Max(0, room) || pour < 0 || (!exact && pour % RM_FloodReleaseMath.U != 0)) { fail = "dug pour " + pour + " from " + L.Remaining + " room " + room + " exact " + exact; break; }
                    L.Place(pour); }
                else if (a == 1) { long d = RM_FloodReleaseMath.SurfaceDebitDl(L.Remaining, per); if (d > L.Remaining || d < 0) { fail = "surface overdraw"; break; } L.Place(d); }
                else if (a == 2) L.Spill(rng.Next(-10, 50000));
                else L.Place(rng.Next(-10, 50000));
                if (!L.Closes) { fail = "release ledger open: In " + L.In + " R " + L.Remaining + " P " + L.Placed + " S " + L.Spilled + " L " + L.Lost; break; }
            }
            L.Lose();
            if (fail == null && (!L.Closes || L.Remaining != 0)) fail = "after Lose remaining " + L.Remaining;
        }
        // expiry grows with unpaid steps; pick is deterministic and in range
        bool exp = RM_FloodReleaseMath.ExpiryTick(100, 30, 10, 5) == 100 + 2 * 30 * 10 + 30 * 5 && RM_FloodReleaseMath.ExpiryTick(int.MaxValue - 10, 1000, 1000, 1000) == int.MaxValue;
        var hist = new int[7]; bool det = true;
        for (int s = 0; s < 70000; s++) { int v = RM_FloodReleaseMath.Pick(17, s, 2, 7); if (v < 0 || v >= 7) det = false; else hist[v]++; if (RM_FloodReleaseMath.Pick(17, s, 2, 7) != v) det = false; }
        bool uni = hist.All(h => h > 9000 && h < 11000);
        Row("FLOOD_RELEASE_BOOKS_CLOSE", SHEET, "random", fail == null && exp && det && uni, cases + 2,
            (fail ?? "20000 random releases (seed 424242), 30 steps each: In == Remaining + Placed + Spilled + Lost after every step; no overdraw; whole notches when not level-exact; Lose empties") + "; expiry " + exp + "; pick in range, repeatable " + det + ", even " + uni + " [" + string.Join(",", hist) + "]");
    }

    // ================================================================ converters
    static (long batches, long inUsed, long outMade, double maxAccrued, string bad) RunConverter(float perTick, int inU, int outU, int ticks, Func<int, int> inputAvail, int outRoomCap)
    {
        float accrued = 0; long batches = 0, inUsed = 0, outMade = 0; double maxAcc = 0; string bad = null;
        int outStore = 0;
        for (int t = 0; t < ticks; t++)
        {
            accrued += perTick;
            float capped = RM_ConversionMath.CapAccrued(accrued, inU, perTick);
            float clip = RM_ConversionMath.ClippedIncome(accrued, capped, perTick);
            int avail = inputAvail(t);
            int room = outRoomCap < 0 ? -1 : outRoomCap - outStore;
            int n = RM_ConversionMath.Batches(capped, inU, outU, avail, room);
            if (n * inU > avail) bad = bad ?? "tick " + t + ": " + n + " batches eat " + n * inU + " of " + avail;
            if (room >= 0 && n * outU > room) bad = bad ?? "tick " + t + ": " + n + " batches overfill room " + room;
            if (n * (double)inU > capped + 1e-3 * inU) bad = bad ?? "tick " + t + ": ran " + n + " batches on a budget of " + capped;
            batches += n; inUsed += (long)n * inU; outMade += (long)n * outU;
            accrued = capped - n * inU + clip;
            if (outRoomCap >= 0) outStore = Math.Max(0, outStore + n * outU - outU); // a consumer drains one batch a tick
            maxAcc = Math.Max(maxAcc, accrued);
        }
        return (batches, inUsed, outMade, maxAcc, bad);
    }

    static void Converters()
    {
        // long-run rate: shipped converterRateMultiplier 0.1-5 x a sweep of recipes; ample input, no output limit
        int cases = 0; var bad = new List<string>();
        foreach (float mult in new[] { 0.1f, 0.5f, 1f, 2f, 3.3f, 5f })
        foreach (float perDay in new[] { 10f, 240f, 1000f, 5000f, 24000f })
        foreach (int inU in new[] { 1, 7, 50, 200 })
        {
            cases++;
            float per = RM_ConversionMath.BudgetPerRareTick(perDay, 1f, mult, 1f);
            int T = 240 * 30;
            var r = RunConverter(per, inU, 3, T, _ => int.MaxValue / 2, -1);
            double want = (double)per * T;
            if (r.bad != null) { if (bad.Count < 3) bad.Add(r.bad); continue; }
            if (r.inUsed > want + 1e-3 * want + 1 || r.inUsed < want - inU - per - 1e-3 * want) { if (bad.Count < 3) bad.Add("x" + mult + " " + perDay + "/day batch " + inU + ": used " + r.inUsed + " of income " + want.ToString("0.0")); }
            if (r.outMade != r.batches * 3 || r.inUsed != r.batches * inU) { if (bad.Count < 3) bad.Add("ratio broke"); }
        }
        Row("CONVERTER_RATE_KEPT_ACROSS_SLIDER", CONV, "sweep", bad.Count == 0, cases,
            bad.Count == 0 ? "converter throughput x0.1-5 x 10-24000 units/day x batch 1-200, 30 days with ample input: input consumed equals income within one batch plus one tick (no part-batch lost to the cap); in:out ratio exact every batch" : string.Join("; ", bad));

        // idle burst bound: a dry machine left a week bursts at most one tick's income plus one batch
        cases = 0; bad.Clear();
        foreach (float per in new[] { 0.3f, 1f, 7f, 49f, 260f })
        foreach (int inU in new[] { 1, 5, 50 })
        {
            cases++;
            int week = 240 * 7;
            var r = RunConverter(per, inU, 1, week + 1, t => t < week ? 0 : int.MaxValue / 2, -1);
            double bound = Math.Max(inU, per + inU) + per;
            if (r.inUsed > bound + 1e-3) { if (bad.Count < 3) bad.Add("per " + per + " batch " + inU + ": first wet tick used " + r.inUsed + " > " + bound); }
        }
        Row("CONVERTER_IDLE_BURST_BOUNDED", CONV, "sweep", bad.Count == 0, cases,
            bad.Count == 0 ? "a week dry, then input: the first tick runs at most one tick's income plus one batch (+ the clipped tick)" : string.Join("; ", bad));

        // random: input scarce / output room scarce: never eats input it lacks or overfills output
        cases = 0; string rf = null;
        var rng = new Random(9090);
        for (int k = 0; k < 2000 && rf == null; k++)
        {
            cases++;
            float per = (float)(rng.NextDouble() * 80); int inU = rng.Next(1, 60), outU = rng.Next(1, 60);
            int[] avail = Enumerable.Range(0, 200).Select(_ => rng.Next(0, 3 * inU)).ToArray();
            var r = RunConverter(per, inU, outU, 200, t => avail[t], rng.Next(0, 4 * outU));
            if (r.bad != null) rf = "seed 9090 case " + k + ": " + r.bad;
        }
        Row("CONVERTER_NEVER_OVERDRAWS", CONV, "random", rf == null, cases, rf ?? "2000 random machines (seed 9090), scarce input and output room: batches never exceed input on hand, output room or budget");

        // rotation and the blocked-input rule
        bool rot = true; var counts = new int[4]; int last = -1;
        for (int i = 0; i < 400; i++) { last = RM_ConversionMath.NextRunnable(new[] { 1, 1, 1, 1 }, last); counts[last]++; }
        rot &= counts.All(c => c == 100);
        rot &= RM_ConversionMath.NextRunnable(new[] { 0, 0, 0 }, 1) == -1 && RM_ConversionMath.NextRunnable(new[] { 0, 3, 0 }, 1) == 1 && RM_ConversionMath.NextRunnable(new[] { 2, 0, 5 }, 0) == 2;
        rot &= RM_ConversionMath.FirstRunnable(new[] { 0, 0, 4 }) == 2 && RM_ConversionMath.FirstRunnable(new int[0]) == -1;
        rot &= RM_ConversionMath.AccruedAfterPick(5f, new[] { 1f, 9f, 3f }, -1) == 9f && RM_ConversionMath.AccruedAfterPick(5f, new[] { 1f, 9f, 3f }, 0) == 1f;
        Row("CONVERTER_ROTATES_AND_SKIPS_BLOCKED", CONV, "fixed", rot, 7, "four runnable inputs share 400 cycles " + string.Join("/", counts) + "; a blocked input is skipped, none runnable gives -1; nothing running keeps the largest budget");
        bool sun = RM_ConversionMath.SunFactor(0.5f, false) == 1f && RM_ConversionMath.SunFactor(0.49f, false) == 0f && RM_ConversionMath.SunFactor(1f, true) == 0f;
        bool zero = RM_ConversionMath.BudgetPerRareTick(100, 1, 0, 1) == 0 && RM_ConversionMath.Batches(1000, 0, 1, 100, -1) == 0;
        Row("CONVERTER_SOLAR_AND_ZERO_GUARDS", CONV, "fixed", sun && zero, 5, "solar still daylight-only unroofed " + sun + "; zero rate / zero recipe guarded " + zero);
        GameSide("CONVERTER_TICK_ORDER_GAME_SIDE", CONV, "The order CompLiquidConverter applies income, cap, clipped income and batches (this lane modelled: accrue, cap, clip, batches on the capped budget, add the clip back) and its network draw are Verse-side; lane 2 reads the caller.");
    }

    // ================================================================ thirst
    static void Thirst()
    {
        float fall = RM_ThirstMath.FallPerDay(1f, 1f, false, false);
        bool ruled = Math.Abs(1f / fall - 1.25f) < 1e-4 && Math.Abs(RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Potable, true) - 0.5f) < 1e-6
            && Math.Abs(RM_ThirstMath.DehydrationLethal / RM_ThirstMath.DehydrationGainPerDay - 3.333f) < 0.01;
        // simulate a pawn from full, no drink, at 1x: empty day, death day
        double lvl = 1, sev = 0; double emptyAt = -1, deadAt = -1;
        for (int tick = 0; tick < 60000 * 10; tick += 150)
        {
            lvl = Math.Max(0, lvl - RM_ThirstMath.FallPerInterval(fall));
            if (lvl <= 0 && emptyAt < 0) emptyAt = tick / 60000.0;
            sev = Math.Max(0, sev + RM_ThirstMath.DehydrationDelta((float)lvl, 150));
            if (sev >= RM_ThirstMath.DehydrationLethal && deadAt < 0) { deadAt = tick / 60000.0; break; }
        }
        bool timeline = Math.Abs(emptyAt - 1.25) < 0.01 && deadAt - emptyAt > 3.0 && deadAt - emptyAt < 3.5;
        Row("THIRST_RULED_NUMBERS", THIRST, "fixed", ruled && timeline, 4,
            "full to empty " + emptyAt.ToString("0.000") + " days (want 1.25), death " + (deadAt - emptyAt).ToString("0.00") + " days after empty (want about 3), a 1.5 L bottle restores " + RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Potable, true));
        // heat: x(1 + 0.05/degree over comfy max) capped at 3; off switch gives 1; settings rate 0.25-3
        int cases = 0; var bad = new List<string>();
        for (float amb = -50; amb <= 120; amb += 0.5f)
        {
            cases++;
            float h = RM_ThirstMath.HeatFactor(amb, 26f, true);
            float want = Math.Min(3f, Math.Max(1f, 1f + 0.05f * (amb - 26f)));
            if (Math.Abs(h - want) > 1e-4 || RM_ThirstMath.HeatFactor(amb, 26f, false) != 1f) { if (bad.Count < 3) bad.Add("amb " + amb + ": " + h); }
        }
        foreach (float rate in new[] { 0.25f, 1f, 3f })
        foreach (bool lab in new[] { false, true }) foreach (bool sl in new[] { false, true })
        {
            cases++;
            float f = RM_ThirstMath.FallPerDay(rate, 3f, lab, sl);
            float want = 0.8f * rate * 3f * (lab ? 1.3f : 1f) * (sl ? 0.5f : 1f);
            if (Math.Abs(f - want) > 1e-4) bad.Add("rate " + rate + " " + f);
        }
        Row("THIRST_HEAT_AND_RATE_SWEEP", THIRST, "sweep", bad.Count == 0, cases, bad.Count == 0 ? "ambient -50..120 C: heat factor 1 + 0.05/degree over comfy max, capped x3, 1 with heat scaling off; rate 0.25-3 x labour x asleep multiply as ruled" : string.Join("; ", bad));
        // who may drink what
        bool gate = RM_ThirstMath.MayDrink(RM_DrinkUse.Potable, 1f, true, false, false, false)
            && !RM_ThirstMath.MayDrink(RM_DrinkUse.Never, 0f, true, true, true, true)
            && !RM_ThirstMath.MayDrink(RM_DrinkUse.LastResort, 0.5f, true, false, false, true)
            && RM_ThirstMath.MayDrink(RM_DrinkUse.LastResort, 0f, true, false, false, true)
            && !RM_ThirstMath.MayDrink(RM_DrinkUse.LastResort, 0f, true, false, false, false)
            && !RM_ThirstMath.MayDrink(RM_DrinkUse.BreakOnly, 0f, true, false, false, true)
            && RM_ThirstMath.MayDrink(RM_DrinkUse.BreakOnly, 0.5f, true, false, true, true)
            && RM_ThirstMath.MayDrink(RM_DrinkUse.LastResort, 1f, false, true, false, false)
            && !RM_ThirstMath.MayDrink(RM_DrinkUse.LastResort, 0f, false, false, false, true);
        bool pick = RM_ThirstMath.Better(RM_DrinkUse.Potable, RM_WaterQuality.Fouled, 99, RM_DrinkUse.LastResort, RM_WaterQuality.Distilled, 1)
            && RM_ThirstMath.BetterPick(RM_DrinkUse.Potable, false, RM_WaterQuality.Potable, 50, RM_DrinkUse.Potable, true, RM_WaterQuality.Distilled, 1);
        bool awk = !RM_ThirstMath.Awkward(RM_DrinkSource.Terrain, false) && RM_ThirstMath.Awkward(RM_DrinkSource.Caravan, true)
            && !RM_ThirstMath.Awkward(RM_DrinkSource.Bottle, true) && RM_ThirstMath.Awkward(RM_DrinkSource.Bottle, false) && RM_ThirstMath.Awkward(RM_DrinkSource.Container, true);
        Row("THIRST_WHO_DRINKS_WHAT", THIRST, "fixed", gate && pick && awk, 16, "use-class gate (potable always, last resort only when empty and allowed, salt only in the break, never never, animals by native biome) " + gate + "; potable beats last resort, tap beats bucket " + pick + "; awkward only away from home or from a bucket/caravan " + awk);
        // reserve for drinkers; bottle target; categories
        int sc = 0; string sf = null;
        var rng = new Random(77);
        for (int k = 0; k < 5000 && sf == null; k++)
        {
            sc++;
            int avail = rng.Next(-10, 5000), res = rng.Next(-10, 2000 * 10 + 1); bool pot = rng.Next(2) == 0;
            int s = RM_ThirstMath.Spendable(avail, res, pot);
            if (s < 0 && avail >= 0) sf = "negative spendable";
            else if (pot && res > 0 && avail - s < Math.Min(avail, res)) sf = "potable reserve breached: avail " + avail + " reserve " + res + " spend " + s;
            else if ((!pot || res <= 0) && s != avail) sf = "non-potable held back";
        }
        bool deficit = RM_ThirstMath.BottleDeficit(3, 0, 0) == 3 && RM_ThirstMath.BottleDeficit(3, 4, 20) == 0 && RM_ThirstMath.BottleDeficit(0, 4, 0) == 0 && RM_ThirstMath.BottleDeficit(10, 5, 7) == 43;
        bool cat = RM_ThirstMath.Category(0f) == 3 && RM_ThirstMath.Category(0.05f) == 2 && RM_ThirstMath.Category(0.1f) == 1 && RM_ThirstMath.Category(0.29f) == 1 && RM_ThirstMath.Category(0.3f) == 0;
        bool days = Math.Abs(RM_ThirstMath.DaysOfWater(24f, 2, 1f) - 5f) < 1e-4 && float.IsPositiveInfinity(RM_ThirstMath.DaysOfWater(5, 0, 1));
        Row("THIRST_RESERVE_BOTTLES_CATEGORIES", THIRST, "random", sf == null && deficit && cat && days, sc + 9,
            (sf ?? "5000 random nets (seed 77): a potable net never spends into its drinkers' reserve; anything else has none") + "; bottle target per colonist " + deficit + "; thirsty/parched/dehydrated bands " + cat + "; days of water readout " + days);
        bool orphan = RM_ThirstMath.OrphanDehydrationDelta(false, 60000) < 0 && RM_ThirstMath.OrphanDehydrationDelta(true, 60000) == 0;
        Row("THIRST_OFF_HEALS_DEHYDRATION", THIRST, "fixed", orphan, 2, "dehydration with no thirst need behind it heals; with the need it is left to the need");
        GameSide("THIRST_BOTTLE_JOBS_GAME_SIDE", THIRST, "Bottles filled/emptied/washed by jobs, the player's material pick, the faucet and Dubs Bad Hygiene compatibility are Verse-side jobs and defs: no kernel decides them (Stage 6).");
    }

    // ================================================================ drilling
    static void Drilling()
    {
        int cases = 0; var bad = new List<string>();
        foreach (bool sv in new[] { false, true }) foreach (bool hy in new[] { false, true }) foreach (float res in new[] { -1f, 0f, 0.001f, 50f })
        {
            cases++;
            var v = RM_DrillSurveyMath.Placement(sv, hy, res);
            var want = !sv ? RM_DrillSurveyMath.Verdict.Allowed : !hy ? RM_DrillSurveyMath.Verdict.NoYield : res <= 0 ? RM_DrillSurveyMath.Verdict.Spent : RM_DrillSurveyMath.Verdict.Allowed;
            if (v != want) bad.Add(sv + "/" + hy + "/" + res + " -> " + v);
        }
        Row("DRILL_PLACEMENT_REFUSES_DRY_SURVEY", DRILL, "fixed", bad.Count == 0, cases, bad.Count == 0 ? "placement refused on a surveyed empty map and on a spent reserve, allowed unsurveyed or with reserve" : string.Join("; ", bad));
        // WhyNot: None exactly when every condition holds; a pouring drill never sits on a spent or empty survey
        cases = 0; bad.Clear();
        for (int mask = 0; mask < (1 << 12); mask++)
        {
            cases++;
            var s = new RM_DrillSurveyMath.State
            {
                settingOn = (mask & 1) != 0, switchedOn = (mask & 2) != 0, needsPower = (mask & 4) != 0, powered = (mask & 8) != 0,
                surveyed = (mask & 16) != 0, hasYield = (mask & 32) != 0, reserve = (mask & 64) != 0 ? 10f : 0f, hasCanalForm = (mask & 128) != 0,
                fluidAllowed = (mask & 256) != 0, outletDug = (mask & 512) != 0, outletOtherLiquid = (mask & 1024) != 0, outletBrimming = (mask & 2048) != 0,
            };
            bool allGood = s.settingOn && s.switchedOn && (!s.needsPower || s.powered) && s.surveyed && s.hasYield && s.reserve > 0 && s.hasCanalForm
                && s.fluidAllowed && s.outletDug && !s.outletOtherLiquid && !s.outletBrimming;
            var why = RM_DrillSurveyMath.WhyNot(s);
            if ((why == RM_DrillSurveyMath.Block.None) != allGood) { if (bad.Count < 3) bad.Add("mask " + mask + " -> " + why); }
            if (!s.settingOn && why != RM_DrillSurveyMath.Block.DisabledInSettings) { if (bad.Count < 3) bad.Add("setting off reads " + why); }
        }
        Row("DRILL_WHY_NOT_POURING_COMPLETE", DRILL, "sweep", bad.Count == 0, cases, bad.Count == 0 ? "all 4096 combinations of the twelve facts: the drill pours (None) exactly when every condition holds; the settings switch off always reads first" : string.Join("; ", bad));
        // the reserve is charged what landed
        cases = 0; bad.Clear();
        var rng = new Random(31337);
        for (int k = 0; k < 10000; k++)
        {
            cases++;
            long b = rng.Next(0, 40000), a = rng.Next(0, 40000); float upl = (float)rng.NextDouble() * 5;
            float sp = RM_DrillSurveyMath.SpentUnits(b, a, 10000, upl);
            double want = a > b ? (a - b) / 10000.0 * upl : 0;
            if (sp < 0 || Math.Abs(sp - want) > 1e-4 * Math.Max(1, want)) { if (bad.Count < 3) bad.Add(b + "->" + a + ": " + sp); }
        }
        Row("DRILL_CHARGES_WHAT_LANDED", DRILL, "random", bad.Count == 0, cases, bad.Count == 0 ? "10000 random writes (seed 31337): reserve charged exactly the dL that landed, never negative" : string.Join("; ", bad));
        GameSide("DRILL_RIGHT_MAPS_GAME_SIDE", DRILL, "'Drilling liquids on the right maps' is the per-biome survey roll (RM_MapComponent_SubsurfaceLiquid, biome extensions, defs) and the bleed well's tick: Verse-side, Stage 6 or lane 2's caller read.");
    }

    // ================================================================ sprinklers
    static void Sprinklers()
    {
        int cases = 0; var bad = new List<string>();
        // shipped litres/cell/hour slider 0.1-5 in 0.05 steps; units per litre 10
        for (int s = 2; s <= 100; s++)
        {
            float lph = s / 20f;
            for (int cells = 0; cells <= 60; cells++)
            {
                cases++;
                int u = RM_SprinklerKernel.UnitsFor(cells, lph, 10);
                double exact = cells * lph * 10.0;
                if (cells > 0 && (u < exact - 1e-3 || u >= exact + 1)) { if (bad.Count < 3) bad.Add(lph + " L x " + cells + ": " + u + " units"); }
                if (cells > 0 && u <= 0) { if (bad.Count < 3) bad.Add("free pulse " + lph + " x " + cells); }
            }
            for (int units = 0; units <= 800; units += 7)
            {
                cases++;
                int n = RM_SprinklerKernel.MaxCellsFor(units, lph, 10);
                if (n < 0 || RM_SprinklerKernel.UnitsFor(n, lph, 10) > units || RM_SprinklerKernel.UnitsFor(n + 1, lph, 10) <= units) { if (bad.Count < 3) bad.Add("max cells " + units + " units @ " + lph + ": " + n); }
            }
        }
        Row("SPRINKLER_COST_AND_INVERSE_SWEEP", SPRINK, "sweep", bad.Count == 0, cases, bad.Count == 0 ? "slider 0.1-5 L/cell/hour (0.05 steps) x 0-60 cells: a pulse costs the exact litres rounded up, never free; MaxCellsFor is the exact inverse at every budget" : string.Join("; ", bad));
        // the head needs a pump; all-or-nothing; thick liquids clog
        bool dec = RM_SprinklerKernel.Decide(true, true, false, true, false, 25, 125, 1000) == RM_SprinklerState.NoPressure
            && RM_SprinklerKernel.Decide(true, true, true, true, false, 25, 125, 124) == RM_SprinklerState.Dry
            && RM_SprinklerKernel.Decide(true, true, true, true, false, 25, 125, 125) == RM_SprinklerState.Spraying
            && RM_SprinklerKernel.Decide(true, true, true, true, true, 25, 125, 1000) == RM_SprinklerState.Clogged
            && RM_SprinklerKernel.Decide(false, true, true, true, false, 25, 125, 1000) == RM_SprinklerState.Disabled
            && RM_SprinklerKernel.Decide(true, false, true, true, false, 25, 125, 1000) == RM_SprinklerState.SwitchedOff
            && RM_SprinklerKernel.Decide(true, true, true, false, false, 25, 125, 1000) == RM_SprinklerState.NoLiquid;
        int spray = 0;
        for (int m = 0; m < 128; m++)
        {
            var st = RM_SprinklerKernel.Decide((m & 1) != 0, (m & 2) != 0, (m & 4) != 0, (m & 8) != 0, (m & 16) != 0, (m & 32) != 0 ? 10 : 0, 50, (m & 64) != 0 ? 50 : 49);
            bool all = (m & 1) != 0 && (m & 2) != 0 && (m & 4) != 0 && (m & 8) != 0 && (m & 16) == 0 && (m & 32) != 0 && (m & 64) != 0;
            if ((st == RM_SprinklerState.Spraying) != all) dec = false;
            if (st == RM_SprinklerState.Spraying) spray++;
        }
        Row("SPRINKLER_NEEDS_PUMP_ALL_OR_NOTHING", SPRINK, "sweep", dec && spray == 1, 135, "no pump -> NoPressure, short by one unit -> Dry, thick -> Clogged; over all 128 fact combinations it sprays exactly when every condition holds (" + spray + ")");
        // valve: nearest first, never breaches budget or reserve
        cases = 0; string vf = null;
        var rng = new Random(2468);
        for (int k = 0; k < 3000 && vf == null; k++)
        {
            cases++;
            var cells = new List<RM_ValveCell>();
            int nc = rng.Next(0, 40);
            for (int i = 0; i < nc; i++) cells.Add(new RM_ValveCell(i, (float)Math.Round(rng.NextDouble() * 3, 1), rng.Next(4) > 0, rng.Next(6) == 0, rng.Next(6) == 0, rng.Next(5) > 0, rng.Next(8) == 0));
            float lph = rng.Next(2, 101) / 20f; int budget = rng.Next(-1, 300), net = rng.Next(0, 600), reserve = rng.Next(0, 300);
            var kept = RM_SprinklerKernel.Valve(cells, lph, 10, budget, net, reserve, out bool trimmed);
            int cost = RM_SprinklerKernel.UnitsFor(kept.Count, lph, 10);
            if (budget >= 0 && cost > budget) vf = "case " + k + ": cost " + cost + " over budget " + budget;
            else if (reserve > 0 && kept.Count > 0 && net - cost < reserve) vf = "case " + k + ": dips into reserve";
            else if (kept.Any(i => !RM_SprinklerKernel.ValveWants(cells[i]))) vf = "case " + k + ": waters a cell that gains nothing";
            else
            {
                var wanted = cells.Where(RM_SprinklerKernel.ValveWants).ToList();
                float maxKept = kept.Count == 0 ? -1 : kept.Max(i => cells[i].Dist);
                if (wanted.Any(c => !kept.Contains(c.Index) && c.Dist < maxKept)) vf = "case " + k + ": skipped a nearer wanting cell";
                if (trimmed != (kept.Count < wanted.Count)) vf = vf ?? "case " + k + ": trimmed flag wrong";
            }
        }
        Row("SPRINKLER_VALVE_BUDGET_RESERVE_NEAREST", SPRINK, "random", vf == null, cases, vf ?? "3000 random heads (seed 2468): the thirst valve waters only cells that gain, nearest first, never over the day's budget or into the reserve");
        // wet record
        var g = new RM_SprinkledGrid(10);
        g.Wet(3, "Water", RM_SprinklerKernel.WetUntil(1000), 7);
        bool grid = g.WetBy(3, 1000 + 2500 + 249) == "Water" && g.WetBy(3, 1000 + 2750) == null && g.WetByOther(3, 8, 1500) && !g.WetByOther(3, 7, 1500)
            && g.Spend(3, 1500) && g.WetBy(3, 1501) == null && !g.Spend(3, 1501) && g.LiveCells(1501) == 0;
        string pickA = RM_SprinklerKernel.PickLiquid(new[] { new KeyValuePair<string, int>("B", 5), new KeyValuePair<string, int>("A", 5), new KeyValuePair<string, int>("C", 4) });
        string pickB = RM_SprinklerKernel.PickLiquid(new[] { new KeyValuePair<string, int>("A", 5), new KeyValuePair<string, int>("C", 4), new KeyValuePair<string, int>("B", 5) });
        Row("SPRINKLER_WET_UNTIL_AND_PICK", SPRINK, "fixed", grid && pickA == "A" && pickB == "A" && RM_SprinklerKernel.PickLiquid(new KeyValuePair<string, int>[0]) == null, 4,
            "a paid pulse wets until the next pulse plus grace; another head's wetting is seen; a fruiting crop spends it; the most-held liquid sprays, ties by name in any order (" + pickA + "/" + pickB + ")");
        GameSide("SPRINKLER_UNIVERSAL_PIPE_GAME_SIDE", SPRINK, "'on a universal pipe, needing a pump on the network' is the head's network lookup (Building_RM_SprinklerHead, CompRM_SprinklerHead, the pipe net): Verse-side; the kernel's NoPressure is decided above.");
    }

    static int Main()
    {
        Console.OutputEncoding = new System.Text.UTF8Encoding(false);
        SheetConservation(); SheetSettingsSweep(); SheetLevel(); SheetSpreadStops(); SheetCropWeek(); SheetCropSlider(); SheetSaveLoad();
        SheetOffers(); SheetDoors(); SheetReceivers(); SheetIceKeepsWater(); SheetSoakRate(); SheetLiquids(); FloodRelease();
        Converters(); Thirst(); Drilling(); Sprinklers();
        foreach (string l in Out) Console.WriteLine(l);
        return fails > 0 ? 1 : 0;
    }
}
