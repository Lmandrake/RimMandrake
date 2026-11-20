// Blind lane 1, FlowWorks 0.1.0 cycle 4 (run judge-1795134433). Written from the bars (record.json inventory rows
// inv_overflow_sheet, inv_converters, inv_bottles_thirst, inv_drilling, inv_sprinklers), the kernels' public contracts and
// the shipped settings ranges, before any builder test, journal or earlier finding was opened.
// One JSON row per line on stdout. Exit 0 = no FAIL row, 1 = at least one FAIL.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.FlowWorks;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.FlowWorks.Thirst;
using RimMandrake.FlowWorks.Drilling;
using RimMandrake.FlowWorks.Sprinklers;
using SM = RimMandrake.FlowWorks.RM_SheetMath;

public static class BlindLane1
{
    static readonly List<string> Rows = new List<string>();
    static bool anyFail;

    static string J(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";

    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") anyFail = true;
        Rows.Add("{\"id\":" + J(id) + ",\"bars\":[" + string.Join(",", bars.Select(J)) + "],\"kind\":" + J(kind)
                 + ",\"verdict\":" + J(verdict) + ",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }

    static void Check(string id, string[] bars, string kind, Func<(int cases, string fail, string info)> body)
    {
        try
        {
            var r = body();
            Row(id, bars, kind, r.fail == null ? "PASS" : "FAIL", r.cases, r.fail ?? r.info ?? "");
        }
        catch (Exception e)
        {
            Row(id, bars, kind, "FAIL", 0, "threw " + e.GetType().Name + ": " + e.Message);
        }
    }

    static readonly string[] SHEET = { "inv_overflow_sheet" };
    static readonly string[] CONV = { "inv_converters" };
    static readonly string[] THIRST = { "inv_bottles_thirst" };
    static readonly string[] DRILL = { "inv_drilling" };
    static readonly string[] SPRK = { "inv_sprinklers" };

    public static int Main()
    {
        SheetRows();
        ConverterRows();
        ThirstRows();
        DrillRows();
        SprinklerRows();
        foreach (var r in Rows) Console.WriteLine(r);
        return anyFail ? 1 : 0;
    }

    // ───────────────────────────── sheet ─────────────────────────────

    sealed class Sim
    {
        public SM.World W; public SM.State S; public SM.Params P; public Random R; public int Cells;
        public int[] wetFluid; // fluid a cell held when it became wet; -1 dry
        public string Violation;
    }

    static SM.Params DefaultParams()
    {
        return new SM.Params(); // the kernel's defaults; RM_SheetSettings defaults map 1:1 (cap 50 cm, 4000 squares, 1 cm, 3, 5%)
    }

    static Sim NewRandomSim(int seed, int w, int h, SM.Params p)
    {
        var R = new Random(seed);
        var W = new SM.World(w, h);
        int n = w * h;
        for (int c = 0; c < n; c++)
        {
            int k = R.Next(100);
            W.Kinds[c] = k < 68 ? SM.Kind.Open : k < 78 ? SM.Kind.Blocked : k < 83 ? SM.Kind.Door : k < 88 ? SM.Kind.Grate
                       : k < 94 ? SM.Kind.Receiver : SM.Kind.Sink;
            W.RoomDl[c] = R.Next(3) == 0 ? 0 : R.Next(5000);
            W.BodyFluid[c] = (byte)R.Next(3);
            W.SoakMilliDl[c] = R.Next(3) == 0 ? 0 : R.Next(4000);
            W.EvapMilliDl[c] = R.Next(3) == 0 ? 0 : R.Next(2000);
            W.TempDeciC[c] = R.Next(5) == 0 ? -R.Next(100) : R.Next(400);
        }
        W.Fluids[1] = new SM.FluidRule { InfiltrationPermille = 1000, EvaporationPermille = 1000, FreezeDeciC = 0 };
        W.Fluids[2] = new SM.FluidRule { InfiltrationPermille = 300, EvaporationPermille = 300, NeverFreezes = true };
        W.Fluids[3] = new SM.FluidRule { InfiltrationPermille = 0, EvaporationPermille = 0, NeverFreezes = true, BoilMilliDl = 2500, BoilAboveDeciC = -420 };
        var S = new SM.State(w, h, (uint)seed * 2654435761u);
        var sim = new Sim { W = W, S = S, P = p, R = R, Cells = n, wetFluid = Enumerable.Repeat(-1, n).ToArray() };
        return sim;
    }

    static SM.SpillOffer RandomOffer(Sim s)
    {
        int len = 1 + s.R.Next(6);
        var lips = new int[len];
        for (int i = 0; i < len; i++) lips[i] = s.R.Next(-2, s.Cells + 2); // off-grid lips included
        return new SM.SpillOffer { LipNearestFirst = lips, AmountDl = s.R.Next(-50, 40000), Fluid = (byte)s.R.Next(0, 4), From = (SM.Source)s.R.Next(SM.SourceCount) };
    }

    // invariants checked after every operation; returns null or a violation text
    static string Invariants(Sim sim, string after)
    {
        var s = sim.S; var w = sim.W;
        if (!s.LedgerCloses) return after + ": ledger open: in " + s.TotalIn + " != standing " + s.Standing + " + out " + s.TotalOut;
        int wet = 0;
        for (int c = 0; c < sim.Cells; c++)
        {
            if (s.Dl[c] < 0) return after + ": negative dL at " + c;
            if (s.Dl[c] > 0)
            {
                wet++;
                if (s.Fluid[c] == 0) return after + ": wet cell " + c + " has no fluid";
                if (!SM.World.HoldsSheet(w.Kinds[c])) return after + ": sheet on a " + w.Kinds[c] + " cell " + c;
                if (s.Dl[c] > sim.P.SheetCapDl) return after + ": cell " + c + " holds " + s.Dl[c] + " over the cap " + sim.P.SheetCapDl;
                if (sim.wetFluid[c] >= 0 && sim.wetFluid[c] != s.Fluid[c]) return after + ": liquids mixed at " + c + ": " + sim.wetFluid[c] + " became " + s.Fluid[c];
                sim.wetFluid[c] = s.Fluid[c];
            }
            else
            {
                sim.wetFluid[c] = -1;
                if (s.Fluid[c] != 0) return after + ": dry cell " + c + " keeps fluid " + s.Fluid[c];
            }
        }
        if (wet != s.WetCount) return after + ": wet list " + s.WetCount + " != wet cells " + wet;
        if (wet > sim.P.MaxWetCells) return after + ": " + wet + " wet cells over the cap " + sim.P.MaxWetCells;
        return null;
    }

    static string RunRandom(int seed, int pulses, SM.Params p, int w = 12, int h = 12)
    {
        var sim = NewRandomSim(seed, w, h, p);
        var rep = new SM.PulseReport();
        for (int t = 0; t < pulses; t++)
        {
            int nOff = sim.R.Next(0, 4);
            var offers = new List<SM.SpillOffer>();
            for (int i = 0; i < nOff; i++) offers.Add(RandomOffer(sim));
            var previews = offers.Select(o => o.AmountDl).ToArray();
            int[] acc = SM.ResolveSpills(sim.S, sim.W, p, offers);
            for (int i = 0; i < offers.Count; i++)
            {
                if (acc[i] < 0 || acc[i] > Math.Max(0, offers[i].AmountDl)) return "pulse " + t + ": offer " + i + " accepted " + acc[i] + " of " + offers[i].AmountDl;
            }
            string v = Invariants(sim, "pulse " + t + " spill"); if (v != null) return v;
            long roomBefore = sim.W.RoomDl.Select(x => (long)x).Sum();
            SM.Pulse(sim.S, sim.W, p, rep);
            long roomAfter = sim.W.RoomDl.Select(x => (long)x).Sum();
            long reported = rep.Returned.Sum(x => (long)x.dl);
            if (roomBefore - roomAfter != reported) return "pulse " + t + ": receivers took " + (roomBefore - roomAfter) + " but the report says " + reported;
            v = Invariants(sim, "pulse " + t); if (v != null) return v;
            int op = sim.R.Next(40);
            if (op == 0) SM.PurgeAll(sim.S);
            else if (op < 4 && sim.S.WetCount > 0) { int c = sim.S.Occ_Get(sim.R.Next(sim.S.WetCount)); SM.Burn(sim.S, c, sim.R.Next(1, 3000)); }
            else if (op < 6 && sim.S.WetCount > 0) { int c = sim.S.Occ_Get(sim.R.Next(sim.S.WetCount)); SM.HandOver(sim.S, c, sim.R.Next(1, 3000), sim.R.Next(2) == 0); }
            else if (op < 8 && sim.S.WetCount > 0) { int c = sim.S.Occ_Get(sim.R.Next(sim.S.WetCount)); SM.PurgeConnected(sim.S, c, sim.R.Next(3) == 0 ? SM.AllDl : sim.R.Next(1, 5000)); }
            v = Invariants(sim, "pulse " + t + " op " + op); if (v != null) return v;
        }
        return null;
    }

    static void SheetRows()
    {
        // S1 conservation + no mixing + cap + wet cap, random worlds (seeded), shrunk by halving pulses then grid
        Check("SHEET_RANDOM_LEDGER_CLOSES_NO_MIX", SHEET, "random", () =>
        {
            int cases = 0;
            for (int seed = 1; seed <= 400; seed++)
            {
                var p = DefaultParams();
                if (seed % 4 == 1) p.MaxWetCells = 1 + seed % 17;
                if (seed % 5 == 2) p.DoorLeakPermille = 0;
                if (seed % 7 == 3) p.SheetCapDl = 5 * SM.DlPerCm;
                if (seed % 3 == 0) p.SweepsPerPulse = 1 + seed % 6;
                cases++;
                string f = RunRandom(seed, 120, p);
                if (f != null)
                {
                    // shrink: smallest pulse count and grid that still fails with this seed
                    int bp = 120, bw = 12;
                    for (int ps = 1; ps <= 120; ps++) if (RunRandom(seed, ps, p) != null) { bp = ps; break; }
                    for (int g = 2; g <= 12; g++) if (RunRandom(seed, bp, p, g, g) != null) { bw = g; break; }
                    return (cases, "seed " + seed + " (cap " + p.SheetCapDl + ", wetcap " + p.MaxWetCells + ", door " + p.DoorLeakPermille + "): " + f
                                   + "; shrunk: " + bw + "x" + bw + " grid, " + bp + " pulses: " + RunRandom(seed, bp, p, bw, bw), null);
                }
            }
            return (cases, null, "400 seeded worlds x 120 pulses: ledger closes after every spill, pulse, burn, hand-over and purge; no cell changes liquid while wet; no cell over the cap or the wet-square cap; receivers' room drop equals the reported returns");
        });

        // S2 save mid-run, load, continue: identical to an uninterrupted run
        Check("SHEET_SAVE_LOAD_CONTINUES_IDENTICAL", SHEET, "random", () =>
        {
            int cases = 0;
            for (int seed = 1; seed <= 150; seed++)
            {
                var p = DefaultParams();
                var a = NewRandomSim(seed, 10, 10, p);
                var rep = new SM.PulseReport();
                var offersBy = new List<List<SM.SpillOffer>>();
                var rr = new Random(seed * 31);
                for (int t = 0; t < 80; t++) { var l = new List<SM.SpillOffer>(); int k = rr.Next(3); for (int i = 0; i < k; i++) l.Add(RandomOffer(a)); offersBy.Add(l); }
                int cut = 1 + seed % 70;
                SM.State b = null; SM.World wb = null;
                for (int t = 0; t < 80; t++)
                {
                    if (t == cut) { b = SM.Load(SM.Save(a.S)); wb = a.W.Clone(); }
                    if (b != null) { SM.ResolveSpills(b, wb, p, offersBy[t]); SM.Pulse(b, wb, p, null); }
                    SM.ResolveSpills(a.S, a.W, p, offersBy[t]); SM.Pulse(a.S, a.W, p, rep);
                    cases++;
                    if (b != null && SM.Hash(a.S) != SM.Hash(b))
                        return (cases, "seed " + seed + ": saved at pulse " + cut + ", loaded copy diverged at pulse " + t, null);
                }
            }
            return (cases, null, "150 seeds, save/load at a varying pulse, 80 pulses: hash identical every pulse after the load");
        });

        // S3 the week: a crop under standing overflow (sheet tier) dies after exactly the shipped week; a film never
        Check("SHEET_CROP_DIES_AFTER_A_WEEK_STANDING", SHEET, "fixed", () =>
        {
            var p = DefaultParams();
            int expect = SM.CropKillPulsesFor(1680, 250);
            if (expect * 250 != SM.TicksPerWeek) return (1, "1680 pulses at 250 ticks is " + expect * 250 + " ticks, not a week", null);
            int first = Enclosed(p, 5 * SM.DlPerCm, 3000);
            if (first != expect) return (1, "a 5 cm sheet first reported drowning at pulse " + first + ", expected " + expect, null);
            int film = Enclosed(p, 2 * SM.DlPerCm, 3000);
            if (film != -1) return (2, "a 2 cm film (irrigates only) reported drowning at pulse " + film, null);
            var p2 = DefaultParams(); p2.CropKillPulses = 1680;
            bool young = SM.CropDrowns(5000, 1679 * 250, 250, p2), old = SM.CropDrowns(1680, 1680 * 250, 250, p2), late = SM.CropDrowns(1679, 9999999, 250, p2);
            if (young || !old || late) return (5, "CropDrowns young " + young + " old " + old + " stood-short " + late, null);
            return (5, null, "5 cm sheet: drowning first reported at pulse " + expect + " (7 days); 2 cm film never; crop younger than the delay never drowns");
        });

        // S4 the crop delay sweep: days slider 0.5..30 x flow pulse 60..2500 keeps the time in days
        Check("SHEET_CROP_DELAY_SWEEP_PULSE_SLIDER", SHEET, "sweep", () =>
        {
            int cases = 0;
            for (double days = 0.5; days <= 30.0001; days += 0.5)
            {
                int stored = Math.Max(1, SM.PulsesFor((int)Math.Round(days * 60000), 250));
                foreach (int pulse in new[] { 60, 61, 100, 125, 199, 250, 251, 333, 500, 997, 1000, 2000, 2499, 2500 })
                {
                    cases++;
                    int k = SM.CropKillPulsesFor(stored, pulse);
                    long ticks = (long)k * pulse, want = (long)Math.Round(days * 60000);
                    if (ticks < want || ticks >= want + pulse)
                        return (cases, "days " + days + ", pulse " + pulse + ": " + k + " pulses = " + ticks + " ticks for a delay of " + want, null);
                }
            }
            return (cases, null, "every 0.5-day step 0.5..30 at 14 pulse lengths 60..2500: the drowning time stays within one pulse above the set days");
        });

        // S5 soak: a sheet on sand soaks in and is gone; every dL counted
        Check("SHEET_SOAKS_IN_AND_IS_COUNTED", SHEET, "fixed", () =>
        {
            var p = DefaultParams();
            var w = new SM.World(3, 3);
            for (int c = 0; c < 9; c++) w.Kinds[c] = c == 4 ? SM.Kind.Open : SM.Kind.Blocked;
            int soak = (int)Math.Round(4.0 * SM.DlPerCm * 1000 / 240); // 4 cm/day on sand at 240 pulses a day
            w.SoakMilliDl[4] = soak;
            var s = new SM.State(3, 3, 7);
            SM.ResolveSpills(s, w, p, new[] { new SM.SpillOffer { LipNearestFirst = new[] { 4 }, AmountDl = 2 * SM.DlPerCm, Fluid = 1, From = SM.Source.Pump } });
            int t = 0;
            while (s.WetCount > 0 && t < 10000) { SM.Pulse(s, w, p, null); t++; }
            if (s.WetCount > 0) return (1, "2 cm on sand still standing after 10000 pulses", null);
            if (s.Soaked != 2 * SM.DlPerCm || !s.LedgerCloses) return (1, "soaked " + s.Soaked + " of " + 2 * SM.DlPerCm, null);
            if (Math.Abs(t - 120) > 1) return (1, "2 cm at 4 cm/day took " + t + " pulses, expected ~120 (half a day)", null);
            return (1, null, "2 cm on sand at 4 cm/day gone in " + t + " pulses (half a day), every dL in Soaked");
        });

        // S6 order independence: the same offers in any order give the same state
        Check("SHEET_SPILL_ORDER_INDEPENDENT", SHEET, "random", () =>
        {
            int cases = 0;
            for (int seed = 1; seed <= 300; seed++)
            {
                var a = NewRandomSim(seed, 8, 8, DefaultParams());
                var b = NewRandomSim(seed, 8, 8, DefaultParams());
                var offers = new List<SM.SpillOffer>();
                for (int i = 0; i < 5; i++) offers.Add(RandomOffer(a));
                var rev = offers.AsEnumerable().Reverse().ToList();
                int[] x = SM.ResolveSpills(a.S, a.W, a.P, offers), y = SM.ResolveSpills(b.S, b.W, b.P, rev);
                cases++;
                if (SM.Hash(a.S) != SM.Hash(b.S)) return (cases, "seed " + seed + ": reversed offer order changed the sheet", null);
                for (int i = 0; i < 5; i++) if (x[i] != y[4 - i]) return (cases, "seed " + seed + ": offer " + i + " accepted " + x[i] + " forward, " + y[4 - i] + " reversed", null);
            }
            return (cases, null, "300 seeds x 5 offers: state and per-offer accepts identical forward and reversed");
        });

        // S7 PreviewSpill is exact
        Check("SHEET_PREVIEW_EQUALS_ACCEPT", SHEET, "random", () =>
        {
            int cases = 0;
            for (int seed = 1; seed <= 2000; seed++)
            {
                var p = DefaultParams(); if (seed % 3 == 0) p.MaxWetCells = 1 + seed % 5;
                var a = NewRandomSim(seed, 6, 6, p);
                for (int i = 0; i < seed % 4; i++) SM.ResolveSpills(a.S, a.W, p, new[] { RandomOffer(a) });
                var o = RandomOffer(a);
                if (o.LipNearestFirst.Length > 1 && seed % 2 == 0) o.LipNearestFirst[1] = o.LipNearestFirst[0]; // a repeated lip
                int pv = SM.PreviewSpill(a.S, a.W, p, o);
                int ac = SM.ResolveSpills(a.S, a.W, p, new[] { o })[0];
                cases++;
                if (pv != ac) return (cases, "seed " + seed + ": preview " + pv + " but accepted " + ac + " (lips " + string.Join(",", o.LipNearestFirst) + ", amount " + o.AmountDl + ")", null);
            }
            return (cases, null, "2000 random offers incl. repeated lips and a small wet cap: preview equals accept");
        });

        // S8 door at 0% seals; at 5% it leaks slowly
        Check("SHEET_DOOR_ZERO_SEALS", SHEET, "sweep", () =>
        {
            int cases = 0;
            foreach (int pct in new[] { 0, 1, 5, 25, 50 })
            {
                var p = DefaultParams(); p.DoorLeakPermille = pct * 10;
                var w = new SM.World(7, 1);
                for (int c = 0; c < 7; c++) w.Kinds[c] = SM.Kind.Open;
                w.Kinds[3] = SM.Kind.Door;
                var s = new SM.State(7, 1, 3);
                SM.ResolveSpills(s, w, p, new[] { new SM.SpillOffer { LipNearestFirst = new[] { 0, 1, 2 }, AmountDl = 3 * 20 * SM.DlPerCm, Fluid = 1, From = SM.Source.Pump } });
                for (int t = 0; t < 2000; t++) SM.Pulse(s, w, p, null);
                long past = s.Dl[4] + s.Dl[5] + s.Dl[6];
                cases++;
                if (pct == 0 && (past > 0 || s.Dl[3] > 0)) return (cases, "door at 0% let " + past + " dL past it and holds " + s.Dl[3], null);
                if (pct > 0 && past == 0) return (cases, "door at " + pct + "% passed nothing in 2000 pulses", null);
                if (!s.LedgerCloses) return (cases, "ledger open at door " + pct + "%", null);
            }
            return (cases, null, "door 0% passes nothing over 2000 pulses; 1..50% passes some; ledger closes");
        });

        // S9 frost: below 0 °C the sheet is ice and keeps every dL; above the thaw margin it is liquid again
        Check("SHEET_FREEZE_KEEPS_EVERY_DL", SHEET, "fixed", () =>
        {
            var p = DefaultParams();
            var w = new SM.World(5, 1);
            for (int c = 0; c < 5; c++) { w.Kinds[c] = SM.Kind.Open; w.TempDeciC[c] = -50; w.SoakMilliDl[c] = 2000; }
            var s = new SM.State(5, 1, 9);
            SM.ResolveSpills(s, w, p, new[] { new SM.SpillOffer { LipNearestFirst = new[] { 0 }, AmountDl = 40 * SM.DlPerCm, Fluid = 1, From = SM.Source.Rain } });
            for (int t = 0; t < 500; t++) SM.Pulse(s, w, p, null);
            if (s.Dl[0] != 40 * SM.DlPerCm || s.Tiers[0] != SM.Tier.Ice) return (1, "frozen cell holds " + s.Dl[0] + " tier " + s.Tiers[0] + " after 500 pulses at -5 C", null);
            for (int c = 0; c < 5; c++) { w.TempDeciC[c] = 5; w.SoakMilliDl[c] = 0; }
            SM.Pulse(s, w, p, null);
            if (s.Tiers[0] == SM.Tier.Ice) return (2, null, null); // +0.5 C is inside the 1 C thaw margin: still ice is right
            return (2, "thawed at +0.5 C, inside the 1 C thaw margin", null);
        });

        // S10 the spill gate as the settings words say it
        Check("SHEET_SPILL_SWITCHES_SWEEP", SHEET, "sweep", () =>
        {
            int cases = 0;
            for (int m = 0; m < 64; m++)
            {
                bool spillsFrom = (m & 1) != 0, engine = (m & 2) != 0, has = (m & 4) != 0, water = (m & 8) != 0, other = (m & 16) != 0, force = (m & 32) != 0;
                bool got = SM.AcceptsSpill(spillsFrom, engine, has, water, other, force);
                // settings text: "Off: only water spills" (other liquids); the master or the inflow's switch off: refuses; the depth engine and a known liquid always needed
                bool want = engine && has && (force || (spillsFrom && (water || other)));
                cases++;
                if (got != want) return (cases, "mask " + m + ": got " + got, null);
            }
            return (cases, null, "64 switch combinations as the settings text reads");
        });

        // S11 every liquid soaks in or dries (audited for every FlowWorks liquid): derived rules never stand forever
        Check("SHEET_EVERY_DERIVED_LIQUID_LEAVES", SHEET, "sweep", () =>
        {
            int cases = 0;
            foreach (bool burn in new[] { false, true }) foreach (bool hot in new[] { false, true }) foreach (bool slip in new[] { false, true })
                foreach (int tpt in new[] { 1, 30, 60, 61, 120, 600, 6000, 60000, int.MaxValue })
                {
                    var r = RM_SheetFluidMath.RuleFor(burn, hot, slip, tpt, -1, -1);
                    cases++;
                    if (r.InfiltrationPermille <= 0 || r.EvaporationPermille <= 0) return (cases, "burn " + burn + " hot " + hot + " slip " + slip + " tpt " + tpt + ": soak " + r.InfiltrationPermille + " evap " + r.EvaporationPermille, null);
                    if (r.NeverFreezes == (!burn && !hot && !slip)) return (cases, "freeze rule wrong for burn " + burn + " hot " + hot + " slip " + slip, null);
                }
            return (cases, null, "every derived liquid rule soaks and dries at 10% or more of water's rate; only plain liquids freeze. Authored 0% percents are a Defs question (lane 2)");
        });

        Row("SHEET_SHIPPED_DEFAULT_OFF", SHEET, "info", "INFO", 1,
            "RM_SheetSettings.sheetOverflowEnabled ships false ('being tested: off until the live walk signs it off'): a new game shows no overspill unless the player turns it on. The bar's experience is behind a default-off switch; lane 2 weighs it.");
        Row("SHEET_GAME_SIDE_NOT_KERNEL", SHEET, "not_kernel", "UNSETTLED", 0,
            "Game-side: which cells the map component classifies Open/Door/Receiver, crops actually killed by the CropDrowning report, the Flood_FlowWorks legacy release, and the per-FluidDef authored soak/evap percents. Settled by reading RM_MapComponent_Sheet.SyncParams/ClassifyCell and the FluidDefs (lane 2), and by the live sheet proof at stage 6.");
    }

    static int Enclosed(SM.Params p, int dl, int maxPulses)
    {
        var w = new SM.World(3, 3);
        for (int c = 0; c < 9; c++) w.Kinds[c] = c == 4 ? SM.Kind.Open : SM.Kind.Blocked;
        var s = new SM.State(3, 3, 1);
        SM.ResolveSpills(s, w, p, new[] { new SM.SpillOffer { LipNearestFirst = new[] { 4 }, AmountDl = dl, Fluid = 1, From = SM.Source.Pump } });
        var rep = new SM.PulseReport();
        for (int t = 1; t <= maxPulses; t++)
        {
            SM.Pulse(s, w, p, rep);
            if (rep.CropDrowning.Any(x => x.cell == 4)) return t;
        }
        return -1;
    }

    // ───────────────────────────── converters ─────────────────────────────

    // One converter cycle as the kernel's own comments describe it: income in, cap, batches from the capped budget, spend,
    // the clipped part of this tick's income added back.
    static (long batches, float accrued) ConvTick(float accrued, float perTick, int inU, int outU, int avail, int room)
    {
        accrued += perTick;
        float capped = RM_ConversionMath.CapAccrued(accrued, inU, perTick);
        float clipped = RM_ConversionMath.ClippedIncome(accrued, capped, perTick);
        int n = RM_ConversionMath.Batches(capped, inU, outU, avail, room);
        return (n, capped - n * inU + clipped);
    }

    static void ConverterRows()
    {
        Check("CONV_LONG_RUN_RATE_EQUALS_SETTING", CONV, "sweep", () =>
        {
            int cases = 0;
            foreach (float mult in new[] { 0.1f, 0.25f, 0.5f, 1f, 1.37f, 2f, 3f, 4.5f, 5f })
                foreach (float perDay in new[] { 10f, 60f, 240f, 500f, 1000f, 4800f, 20000f })
                    foreach (int inU in new[] { 1, 3, 10, 25, 100, 1000 })
                    {
                        float perTick = RM_ConversionMath.BudgetPerRareTick(perDay, 1f, mult, 1f);
                        float acc = 0f; long eaten = 0; int T = 2400;
                        for (int t = 0; t < T; t++) { var r = ConvTick(acc, perTick, inU, 1, int.MaxValue, -1); acc = r.accrued; eaten += r.batches * inU; }
                        double want = (double)perTick * T;
                        cases++;
                        if (eaten > want + 1e-3 * want + 1 || eaten < want - inU - perTick - 1e-3 * want - 1)
                            return (cases, "mult " + mult + " perDay " + perDay + " batch " + inU + ": ate " + eaten + " in 10 days, the rate pays " + want.ToString("0.0"), null);
                    }
            return (cases, null, "9 throughput settings x 7 rates x 6 batch sizes, 10 days unbounded: input eaten equals the paid rate within one batch plus one tick");
        });

        Check("CONV_BATCH_CONSERVES_UNITS", CONV, "random", () =>
        {
            var R = new Random(1016); int cases = 0;
            for (int i = 0; i < 200000; i++)
            {
                float acc = (float)(R.NextDouble() * 5000); int inU = R.Next(-2, 200), outU = R.Next(-2, 200), avail = R.Next(-5, 5000), room = R.Next(-3, 5000);
                int n = RM_ConversionMath.Batches(acc, inU, outU, avail, room);
                cases++;
                if (n < 0) return (cases, "negative batches (seed 1016 case " + i + ")", null);
                if (n == 0) continue;
                if (inU < 1 || outU < 1) return (cases, "batches " + n + " with a non-positive recipe " + inU + "->" + outU, null);
                if ((long)n * inU > avail) return (cases, "case " + i + ": " + n + " batches eat " + n * inU + " of " + avail + " on hand", null);
                if (room >= 0 && (long)n * outU > room) return (cases, "case " + i + ": " + n + " batches make " + n * outU + " into room " + room, null);
                if (n * inU > acc + 0.01f * inU) return (cases, "case " + i + ": " + n + " batches overspend budget " + acc, null);
            }
            return (cases, null, "200000 random cases (seed 1016): never more input eaten than on hand or paid, never more output than room, never negative");
        });

        Check("CONV_IDLE_BURST_BOUNDED", CONV, "sweep", () =>
        {
            int cases = 0;
            foreach (float mult in new[] { 0.1f, 1f, 5f })
                foreach (float perDay in new[] { 10f, 240f, 4800f, 20000f })
                    foreach (int inU in new[] { 1, 10, 100 })
                    {
                        float perTick = RM_ConversionMath.BudgetPerRareTick(perDay, 1f, mult, 1f);
                        float acc = 0f;
                        for (int t = 0; t < 240 * 7; t++) acc = ConvTick(acc, perTick, inU, 1, 0, -1).accrued; // a dry week
                        var r = ConvTick(acc, perTick, inU, 1, int.MaxValue, -1);
                        long bound = (long)Math.Floor((Math.Max(inU, perTick + inU)) / inU + 1e-4);
                        cases++;
                        if (r.batches > Math.Max(1, bound)) return (cases, "after a dry week, mult " + mult + " perDay " + perDay + " batch " + inU + ": burst " + r.batches + " batches, bound " + bound, null);
                    }
            return (cases, null, "a dry week then a full tank: the first tick runs at most one tick's income plus one batch");
        });

        Check("CONV_ROTATION_FAIR_AND_SKIPS_BLOCKED", CONV, "random", () =>
        {
            var R = new Random(77); int cases = 0;
            for (int i = 0; i < 20000; i++)
            {
                int k = R.Next(1, 6); var b = new List<int>(); for (int j = 0; j < k; j++) b.Add(R.Next(3) == 0 ? 0 : R.Next(1, 4));
                int f = RM_ConversionMath.FirstRunnable(b);
                int wantF = b.FindIndex(x => x > 0);
                cases++;
                if (f != wantF) return (cases, "FirstRunnable(" + string.Join(",", b) + ") = " + f, null);
                var counts = new int[k]; int last = -1;
                for (int t = 0; t < 60 * k; t++) { last = RM_ConversionMath.NextRunnable(b, last); if (last >= 0) counts[last]++; }
                int runnable = b.Count(x => x > 0);
                for (int j = 0; j < k; j++)
                {
                    if (b[j] == 0 && counts[j] != 0) return (cases, "blocked input " + j + " ran (" + string.Join(",", b) + ")", null);
                    if (b[j] > 0 && counts[j] != 60 * k / runnable) return (cases, "input " + j + " ran " + counts[j] + " of " + 60 * k + " with " + runnable + " runnable (" + string.Join(",", b) + ")", null);
                }
                if (runnable == 0 && RM_ConversionMath.NextRunnable(b, R.Next(-1, k)) != -1) return (cases, "nothing runnable but NextRunnable picked one", null);
            }
            return (cases, null, "20000 random input sets (seed 77): blocked inputs skipped, runnable ones share cycles evenly");
        });

        Check("CONV_BLOCKED_SMALL_RECIPE_NEVER_STARVES_BIG", CONV, "fixed", () =>
        {
            // two recipes on one machine: small (5 in) blocked for output, big (50 in) with input; one budget
            float perTick = 7f; float acc = 0f; int bigRuns = 0;
            for (int t = 0; t < 200; t++)
            {
                acc += perTick;
                var capped = new List<float> { RM_ConversionMath.CapAccrued(acc, 5, perTick), RM_ConversionMath.CapAccrued(acc, 50, perTick) };
                var batches = new List<int> { RM_ConversionMath.Batches(capped[0], 5, 1, 1000, 0), RM_ConversionMath.Batches(capped[1], 50, 1, 1000, -1) };
                int pick = RM_ConversionMath.FirstRunnable(batches);
                float kept = RM_ConversionMath.AccruedAfterPick(acc, capped, pick);
                if (pick >= 0) { kept -= batches[pick] * (pick == 0 ? 5 : 50); if (pick == 1) bigRuns += batches[pick]; }
                acc = kept;
            }
            if (bigRuns == 0) return (1, "the big recipe never ran in 200 ticks while the small one was blocked", null);
            return (1, null, "big recipe ran " + bigRuns + " batches in 200 ticks beside a blocked small one");
        });

        Check("CONV_SOLAR_STILL_DAYLIGHT_ONLY", CONV, "sweep", () =>
        {
            int cases = 0;
            for (int g = 0; g <= 100; g++) foreach (bool roof in new[] { false, true })
                {
                    float f = RM_ConversionMath.SunFactor(g / 100f, roof); cases++;
                    float want = !roof && g >= 50 ? 1f : 0f;
                    if (f != want) return (cases, "glow " + g / 100f + " roofed " + roof + ": " + f, null);
                    if (RM_ConversionMath.BudgetPerRareTick(240f, 1f, 1f, f) != (want > 0 ? 1f : 0f)) return (cases, "budget at sun " + f, null);
                }
            return (cases, null, "sky glow 0..1, roofed or not: full from 0.5 open sky, nothing otherwise; budget follows");
        });

        Row("CONV_GAME_SIDE_NOT_KERNEL", CONV, "not_kernel", "UNSETTLED", 0,
            "Game-side: CompLiquidConverter's tick order (does it apply the cap, clipped income and AccruedAfterPick as modelled above), the network draw and the output write (does a batch take exactly inputUnits from the net and put exactly outputUnits back). Settled by reading CompLiquidConverter.CompTickRare in lane 2.");
    }

    // ───────────────────────────── thirst and bottles ─────────────────────────────

    static void ThirstRows()
    {
        Check("THIRST_RULED_NUMBERS", THIRST, "fixed", () =>
        {
            var fails = new List<string>();
            float perDay = RM_ThirstMath.FallPerDay(1f, 1f, false, false);
            if (Math.Abs(1f / perDay - 1.25f) > 1e-3) fails.Add("full need empties in " + 1f / perDay + " days, ruled 1.25");
            float perInt = RM_ThirstMath.FallPerInterval(perDay); int ints = (int)Math.Ceiling(1f / perInt);
            if (Math.Abs(ints * 150f / 60000f - 1.25f) > 0.01f) fails.Add("interval sum empties in " + ints * 150f / 60000f + " days");
            if (Math.Abs(RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Potable, true) - 0.5f) > 1e-5) fails.Add("1.5 L bottle restores " + RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Potable, true));
            if (RM_ThirstMath.HeatFactor(100f, 26f, true) != 3f) fails.Add("heat factor not capped at 3");
            if (RM_ThirstMath.HeatFactor(100f, 26f, false) != 1f) fails.Add("heat scaling off still scales");
            // death about 3 days after empty
            float sev = 0f; int k = 0; while (sev < RM_ThirstMath.DehydrationLethal && k < 100000) { sev += RM_ThirstMath.DehydrationDelta(0f, 150f); k++; }
            float d = k * 150f / 60000f; if (d < 2.5f || d > 3.6f) fails.Add("death " + d + " days after empty, ruled about 3");
            if (RM_ThirstMath.DehydrationDelta(0.5f, 150f) >= 0f) fails.Add("dehydration does not heal above 0.3");
            if (RM_ThirstMath.OrphanDehydrationDelta(false, 150f) >= 0f) fails.Add("orphan dehydration with thirst off does not heal");
            if (Math.Abs(RM_ThirstMath.FallPerDay(1f, 1f, true, false) / perDay - 1.3f) > 1e-4) fails.Add("hard labour not x1.3");
            if (Math.Abs(RM_ThirstMath.FallPerDay(1f, 1f, false, true) / perDay - 0.5f) > 1e-4) fails.Add("asleep not x0.5");
            return (10, fails.Count == 0 ? null : string.Join("; ", fails), "empties in 1.25 days, bottle 0.5, heat cap x3, labour x1.3, asleep x0.5, death " + d.ToString("0.00") + " days after empty");
        });

        Check("THIRST_RATE_SLIDER_SWEEP", THIRST, "sweep", () =>
        {
            int cases = 0;
            for (float m = 0.25f; m <= 3.0001f; m += 0.05f)
                foreach (bool heat in new[] { false, true })
                    for (float amb = -20f; amb <= 80f; amb += 5f)
                    {
                        float hf = RM_ThirstMath.HeatFactor(amb, 26f, heat);
                        float f = RM_ThirstMath.FallPerDay(m, hf, false, false);
                        cases++;
                        if (!(f > 0f) || f > 0.8f * 3f * 3f + 1e-4) return (cases, "rate " + m + " heat " + heat + " " + amb + "C: fall " + f, null);
                        float days = RM_ThirstMath.DaysOfWater(30f, 1, m);
                        if (Math.Abs(days * 0.8f * m * 3f - 30f) > 1e-2) return (cases, "DaysOfWater(30 L, 1, " + m + ") = " + days, null);
                    }
            if (!float.IsPositiveInfinity(RM_ThirstMath.DaysOfWater(10f, 0, 1f))) return (cases, "no drinkers is not unlimited", null);
            return (cases, null, "rate 0.25..3 x heat on/off x -20..80 C: fall positive, at most 0.8x3x3 a day; days-of-water readout consistent");
        });

        Check("THIRST_DRINK_GATES", THIRST, "sweep", () =>
        {
            int cases = 0;
            foreach (RM_DrinkUse use in Enum.GetValues(typeof(RM_DrinkUse)))
                foreach (bool human in new[] { false, true }) foreach (bool native in new[] { false, true })
                    foreach (bool salt in new[] { false, true }) foreach (bool lr in new[] { false, true })
                        foreach (float lvl in new[] { 0f, 0.004f, 0.006f, 0.1f, 0.5f, 1f })
                        {
                            bool got = RM_ThirstMath.MayDrink(use, lvl, human, native, salt, lr);
                            bool want = use == RM_DrinkUse.Potable ? true : use == RM_DrinkUse.Never ? false : !human ? native
                                      : use == RM_DrinkUse.LastResort ? lr && lvl <= 0.005f : salt;
                            cases++;
                            if (got != want) return (cases, use + " human " + human + " native " + native + " salt " + salt + " lr " + lr + " lvl " + lvl + ": " + got, null);
                        }
            // the pick: potable beats last resort whatever the quality or distance
            if (!RM_ThirstMath.BetterPick(RM_DrinkUse.Potable, true, RM_WaterQuality.Fouled, 999f, RM_DrinkUse.LastResort, false, RM_WaterQuality.Distilled, 1f))
                return (cases, "a last-resort source beat a potable one", null);
            return (cases, null, "every use class x humanlike x native x salt break x last-resort switch x level: gates as the rulings say");
        });

        Check("THIRST_RESERVE_NEVER_OVERDRAWN", THIRST, "random", () =>
        {
            var R = new Random(2000); int cases = 0;
            for (int i = 0; i < 100000; i++)
            {
                int avail = R.Next(0, 30000), res = R.Next(-10, 20001); bool pot = R.Next(2) == 0; // a net never holds negative units (first draft drew negatives: outside the contract)
                int sp = RM_ThirstMath.Spendable(avail, res, pot); cases++;
                if (sp > Math.Max(avail, 0) && avail >= 0) return (cases, "spendable " + sp + " of " + avail, null);
                if (pot && res > 0 && avail - sp < Math.Min(res, avail)) return (cases, "potable reserve " + res + " broken: spend " + sp + " of " + avail, null);
                if (sp < 0) return (cases, "negative spendable " + sp + " (avail " + avail + ")", null);
            }
            for (int per = 0; per <= 10; per++) for (int col = 0; col <= 20; col++) for (int have = 0; have <= 60; have += 3)
                    {
                        int d = RM_ThirstMath.BottleDeficit(per, col, have); cases++;
                        if (d < 0 || d != Math.Max(0, per * Math.Max(1, col) - have)) return (cases, "BottleDeficit(" + per + "," + col + "," + have + ") = " + d, null);
                    }
            return (cases, null, "100000 random (seed 2000), stock 0..30000, reserve -10..20000: the drinking reserve is kept; bottles per colonist 0..10 deficit exact");
        });

        Check("THIRST_QUALITY_OFF_ALL_POTABLE", THIRST, "sweep", () =>
        {
            int cases = 0;
            foreach (RM_WaterQuality q in Enum.GetValues(typeof(RM_WaterQuality)))
            {
                cases++;
                if (RM_ThirstMath.HydrateFactor(q, false) != 1f || RM_ThirstMath.Effective(q, false) != RM_WaterQuality.Potable) return (cases, q + " with quality effects off is not plain potable", null);
                float on = RM_ThirstMath.HydrateFactor(q, true);
                if (on <= 0f || on > 1f) return (cases, q + " hydrates x" + on, null);
            }
            return (cases, null, "quality effects off: every drinkable restores fully; on: each 0..1");
        });

        Row("THIRST_GAME_SIDE_NOT_KERNEL", THIRST, "not_kernel", "UNSETTLED", 0,
            "Game-side: bottle fill/empty/wash jobs (JobDriver_FillBottle), the player's material pick (RM_ContainerMaterials), Dubs Bad Hygiene Lite optional, the pipe faucet. Does a filled bottle take exactly its litres from the source and give them back on emptying? Settled by reading the job drivers in lane 2 and the thirst live rows at stage 6.");
    }

    // ───────────────────────────── drilling ─────────────────────────────

    static void DrillRows()
    {
        Check("DRILL_PLACEMENT_REFUSES_EMPTY_SURVEY", DRILL, "sweep", () =>
        {
            int cases = 0;
            foreach (bool sv in new[] { false, true }) foreach (bool y in new[] { false, true }) foreach (float r in new[] { -1f, 0f, 0.001f, 500f })
                    {
                        var v = RM_DrillSurveyMath.Placement(sv, y, r); cases++;
                        var want = !sv ? RM_DrillSurveyMath.Verdict.Allowed : !y ? RM_DrillSurveyMath.Verdict.NoYield : r <= 0f ? RM_DrillSurveyMath.Verdict.Spent : RM_DrillSurveyMath.Verdict.Allowed;
                        if (v != want) return (cases, "Placement(" + sv + "," + y + "," + r + ") = " + v, null);
                    }
            return (cases, null, "surveyed-empty and spent refuse; unsurveyed allowed; a reserve allows");
        });

        Check("DRILL_WHYNOT_ONE_ANSWER_AND_NONE_MEANS_POURS", DRILL, "sweep", () =>
        {
            int cases = 0;
            for (int m = 0; m < (1 << 12); m++)
            {
                var s = new RM_DrillSurveyMath.State
                {
                    settingOn = (m & 1) != 0, switchedOn = (m & 2) != 0, needsPower = (m & 4) != 0, powered = (m & 8) != 0, surveyed = (m & 16) != 0,
                    hasYield = (m & 32) != 0, reserve = (m & 64) != 0 ? 100f : 0f, hasCanalForm = (m & 128) != 0, fluidAllowed = (m & 256) != 0,
                    outletDug = (m & 512) != 0, outletOtherLiquid = (m & 1024) != 0, outletBrimming = (m & 2048) != 0,
                };
                var b = RM_DrillSurveyMath.WhyNot(s); cases++;
                bool pours = s.settingOn && s.switchedOn && (!s.needsPower || s.powered) && s.surveyed && s.hasYield && s.reserve > 0f && s.hasCanalForm
                             && s.fluidAllowed && s.outletDug && !s.outletOtherLiquid && !s.outletBrimming;
                if ((b == RM_DrillSurveyMath.Block.None) != pours) return (cases, "mask " + m + ": WhyNot " + b + " but pours=" + pours, null);
                if (b == RM_DrillSurveyMath.Block.None && RM_DrillSurveyMath.Placement(s.surveyed, s.hasYield, s.reserve) != RM_DrillSurveyMath.Verdict.Allowed)
                    return (cases, "mask " + m + ": pours on a square placement refuses", null);
                if (!s.settingOn && b != RM_DrillSurveyMath.Block.DisabledInSettings) return (cases, "mask " + m + ": setting off reads " + b, null);
            }
            return (cases, null, "all 4096 states: None exactly when every condition holds; a pouring drill is always on a placeable square; setting off always reads so");
        });

        Check("DRILL_SPENT_UNITS_COUNT_WHAT_LANDED", DRILL, "random", () =>
        {
            var R = new Random(58); int cases = 0;
            for (int i = 0; i < 100000; i++)
            {
                long b = R.Next(0, 40000), a = R.Next(0, 40000); long per = R.Next(-1, 12000); float upl = (float)(R.NextDouble() * 10);
                float u = RM_DrillSurveyMath.SpentUnits(b, a, per, upl); cases++;
                if (u < 0f) return (cases, "negative spend", null);
                if (a > b && per > 0 && Math.Abs(u - (a - b) / (double)per * upl) > 1e-3 * Math.Max(1, u)) return (cases, "spent " + u + " for " + (a - b) + " dL landed", null);
                if (a <= b && u != 0f) return (cases, "spent " + u + " for nothing landed", null);
            }
            return (cases, null, "100000 random writes (seed 58): spend equals what landed, never negative");
        });

        Row("DRILL_RIGHT_MAPS_NOT_KERNEL", DRILL, "not_kernel", "UNSETTLED", 0,
            "Game-side: 'on the right maps' is the survey roll per biome (RM_MapComponent_SubsurfaceLiquid, RM_SubsurfaceLiquidBiomeExtension) and the bleed well's draw against the reserve. Settled by reading the component and the biome extension Defs in lane 2.");
    }

    // ───────────────────────────── sprinklers ─────────────────────────────

    static void SprinklerRows()
    {
        Check("SPRK_PUMP_REQUIRED_ALL_OR_NOTHING", SPRK, "sweep", () =>
        {
            int cases = 0;
            for (int m = 0; m < 32; m++)
                foreach (int cells in new[] { 0, 1, 25 }) foreach (int need in new[] { 0, 1, 13 }) foreach (int av in new[] { 0, 12, 13, 100 })
                        {
                            bool en = (m & 1) != 0, sw = (m & 2) != 0, pr = (m & 4) != 0, liq = (m & 8) != 0, thick = (m & 16) != 0;
                            var st = RM_SprinklerKernel.Decide(en, sw, pr, liq, thick, cells, need, av); cases++;
                            bool sprays = en && sw && pr && liq && !thick && cells > 0 && need > 0 && av >= need;
                            if ((st == RM_SprinklerState.Spraying) != sprays) return (cases, "mask " + m + " cells " + cells + " need " + need + " av " + av + ": " + st, null);
                            if (!pr && st == RM_SprinklerState.Spraying) return (cases, "sprays without a pump", null);
                        }
            return (cases, null, "every switch x pump x liquid x clog x cells x need x stock: sprays only with a pump and the whole pulse paid");
        });

        Check("SPRK_COST_NEVER_FREE_AND_MAXCELLS_EXACT", SPRK, "sweep", () =>
        {
            int cases = 0;
            for (float l = 0.1f; l <= 5.0001f; l += 0.05f)
            {
                float lit = (float)Math.Round(l * 20) / 20f; // the slider rounds to 0.05
                for (int cells = 1; cells <= 60; cells++)
                {
                    int u = RM_SprinklerKernel.UnitsFor(cells, lit, 10); cases++;
                    if (u < 1) return (cases, cells + " cells at " + lit + " L cost " + u, null);
                    if (u < cells * lit * 10 - 1e-3) return (cases, cells + " cells at " + lit + " L cost " + u + " < " + cells * lit * 10, null);
                }
                for (int units = 0; units <= 400; units += 7)
                {
                    int n = RM_SprinklerKernel.MaxCellsFor(units, lit, 10); cases++;
                    if (n > 0 && RM_SprinklerKernel.UnitsFor(n, lit, 10) > units) return (cases, units + " units at " + lit + " L: " + n + " cells cost more", null);
                    if (RM_SprinklerKernel.UnitsFor(n + 1, lit, 10) <= units) return (cases, units + " units at " + lit + " L: " + (n + 1) + " cells also fit", null);
                }
            }
            return (cases, null, "litres slider 0.1..5 in 0.05 steps: every pulse costs at least its litres; MaxCellsFor is the exact maximum");
        });

        Check("SPRK_VALVE_BUDGET_RESERVE_NEAREST", SPRK, "random", () =>
        {
            var R = new Random(316); int cases = 0;
            for (int i = 0; i < 20000; i++)
            {
                int n = R.Next(0, 40); var cells = new List<RM_ValveCell>();
                for (int c = 0; c < n; c++) cells.Add(new RM_ValveCell(c, (float)Math.Round(R.NextDouble() * 4, 1), R.Next(4) > 0, R.Next(6) == 0, R.Next(5) == 0, R.Next(5) > 0, R.Next(8) == 0));
                float lit = 0.05f * R.Next(2, 101); int budget = R.Next(-1, 200), net = R.Next(0, 500), res = R.Next(0, 300);
                var kept = RM_SprinklerKernel.Valve(cells, lit, 10, budget, net, res, out bool trimmed);
                int cost = RM_SprinklerKernel.UnitsFor(kept.Count, lit, 10); cases++;
                if (budget >= 0 && cost > budget) return (cases, "case " + i + " (seed 316): pulse " + cost + " over budget " + budget, null);
                if (res > 0 && kept.Count > 0 && net - cost < res) return (cases, "case " + i + ": pulse " + cost + " breaks reserve " + res + " of " + net, null);
                foreach (int k in kept) if (!RM_SprinklerKernel.ValveWants(cells[k])) return (cases, "case " + i + ": watered a cell that did not need it", null);
                var want = cells.Where(RM_SprinklerKernel.ValveWants).ToList();
                float maxKept = kept.Count == 0 ? -1 : kept.Max(k => cells[k].Dist);
                foreach (var c in want) if (!kept.Contains(c.Index) && c.Dist < maxKept) return (cases, "case " + i + ": skipped a nearer cell " + c.Index, null);
                if (trimmed != (kept.Count < want.Count)) return (cases, "case " + i + ": trimmed flag wrong", null);
            }
            return (cases, null, "20000 random valve pulses (seed 316): within the day's budget, above the reserve floor, only cells that need water, nearest first");
        });

        Check("SPRK_WET_UNTIL_NEXT_PULSE_AND_SPEND", SPRK, "fixed", () =>
        {
            var g = new RM_SprinkledGrid(10);
            g.Wet(3, "Water", RM_SprinklerKernel.WetUntil(1000), 7);
            if (g.WetBy(3, 1000 + 2500) != "Water") return (1, "dry before the next pulse is due", null);
            if (g.WetBy(3, 1000 + 2500 + 250) != null) return (2, "still wet after the grace", null);
            if (!g.WetByOther(3, 8, 2000) || g.WetByOther(3, 7, 2000)) return (3, "WetByOther wrong", null);
            if (!g.Spend(3, 2000) || g.WetBy(3, 2000) != null || g.Spend(3, 2000)) return (4, "a fruiting crop's spend does not dry the cell once", null);
            g.Wet(-1, "x", 5, 1); g.Wet(10, "x", 5, 1);
            if (g.LiveCells(0) != 0) return (5, "off-grid wet landed", null);
            if (RM_SprinklerKernel.PickLiquid(new[] { new KeyValuePair<string, int>("B", 5), new KeyValuePair<string, int>("A", 5), new KeyValuePair<string, int>("C", 4), new KeyValuePair<string, int>("C", 2) }) != "C")
                return (6, "PickLiquid does not take the liquid the net holds most of", null);
            if (RM_SprinklerKernel.PickLiquid(new[] { new KeyValuePair<string, int>("B", 5), new KeyValuePair<string, int>("A", 5) }) != "A") return (7, "tie not by key", null);
            if (RM_SprinklerKernel.PickLiquid(new KeyValuePair<string, int>[0]) != null) return (8, "an empty net picks a liquid", null);
            return (8, null, "wet until the next pulse plus grace; a crop's spend dries it once; off-grid ignored; picks the most-held liquid, ties by key, none when empty");
        });

        Check("SPRK_RADIUS_CHOICES", SPRK, "fixed", () =>
        {
            if (Array.IndexOf(RM_SprinklerSettings_Shadow.RadiusChoices, RM_SprinklerKernel.NativeRadius) != 1) return (1, "the default radius is not the middle choice", null);
            int n = 0; for (int x = -3; x <= 3; x++) for (int z = -3; z <= 3; z++) if (x * x + z * z <= RM_SprinklerKernel.NativeRadius * RM_SprinklerKernel.NativeRadius) n++;
            if (n != 25) return (2, "radius 2.9 covers " + n + " squares, settings text says about 25", null);
            return (2, null, "default 2.9 covers 25 squares, the middle of 1.9/2.9/3.9");
        });

        Row("SPRK_GAME_SIDE_NOT_KERNEL", SPRK, "not_kernel", "UNSETTLED", 0,
            "Game-side: 'needing a pump on the network' is decided by the caller's pressure flag (CompRM_SprinklerHead), 'on a universal pipe' by its placement, and the draw of exactly UnitsFor from the net. Settled by reading CompRM_SprinklerHead in lane 2.");
    }
}

// the shipped radius choices, copied from RM_SprinklerSettings.cs (a Verse file) by run_lane1.py at run time
public static partial class RM_SprinklerSettings_Shadow { }

public static class StateExt
{
    // the wet list is internal to the kernel; reach it through the public Dl array instead
    public static int Occ_Get(this SM.State s, int k)
    {
        int seen = 0;
        for (int c = 0; c < s.Dl.Length; c++) if (s.Dl[c] > 0) { if (seen == k) return c; seen++; }
        return -1;
    }
}
