// FlowWorks 0.1.0, blind challenge cycle 2, lane 1 (run judge-1794833810). Written from the bars (record.json inventory rows,
// sheet.md, plan.md), the shipped settings (defaults and slider ranges) and the kernels alone, before any builder test, journal
// or test table was opened. Each test prints one JSON row. Seeds are fixed; a failing random case is shrunk (ops dropped one at a
// time while it still fails) and printed in its smallest form.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.FlowWorks;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.FlowWorks.Drilling;
using RimMandrake.FlowWorks.Sprinklers;
using RimMandrake.FlowWorks.Thirst;
using SM = RimMandrake.FlowWorks.RM_SheetMath;

static class BlindLane1
{
    static int fails;
    static string J(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";
    static void Row(string id, string[] bars, string kind, string verdict, long cases, string detail)
    {
        if (verdict == "FAIL") fails++;
        Console.WriteLine("{\"id\": " + J(id) + ", \"bars\": [" + string.Join(", ", bars.Select(J)) + "], \"kind\": " + J(kind)
            + ", \"verdict\": " + J(verdict) + ", \"cases\": " + cases + ", \"detail\": " + J(detail) + "}");
    }
    static string F(double d) => d.ToString("0.######", CultureInfo.InvariantCulture);
    static readonly string[] SHEET = { "inv_overflow_sheet" }, CONV = { "inv_converters" }, THIRST = { "inv_bottles_thirst" },
        DRILL = { "inv_drilling" }, SPRK = { "inv_sprinklers" };

    static void Guard(string id, string[] bars, string kind, Action a)
    {
        try { a(); }
        catch (Exception e) { Row(id, bars, kind, "FAIL", 0, "threw " + e.GetType().Name + ": " + e.Message); }
    }

    static int Main()
    {
        Guard("SHEET_RANDOM_LEDGER_AND_INVARIANTS", SHEET, "random", SheetRandom);
        Guard("SHEET_SAVELOAD_CONTINUES_IDENTICAL", SHEET, "random", SheetSaveLoad);
        Guard("SHEET_SPILL_ORDER_FREE", SHEET, "random", SheetOrderFree);
        Guard("SHEET_PREVIEW_EQUALS_ACCEPT", SHEET, "random", SheetPreview);
        Guard("SHEET_CROPS_DROWN_AFTER_ONE_WEEK", SHEET, "fixed", SheetCropWeek);
        Guard("SHEET_CROP_DELAY_SETTING_SWEEP", SHEET, "sweep", SheetCropSweep);
        Guard("SHEET_FILM_NEVER_DROWNS", SHEET, "fixed", SheetFilmNeverDrowns);
        Guard("SHEET_TIER_HYSTERESIS", SHEET, "fixed", SheetTiers);
        Guard("SHEET_LIES_LEVEL", SHEET, "random", SheetLevel);
        Guard("SHEET_FREEZE_KEEPS_EVERY_DL", SHEET, "fixed", SheetFreeze);
        Guard("SHEET_LOWER_CAP_DELETES_NOTHING", SHEET, "fixed", SheetLowerCap);
        Guard("SHEET_SINK_TAKES_ONLY_MOBILE", SHEET, "fixed", SheetSink);
        Guard("SHEET_DOOR_ZERO_SEALS", SHEET, "fixed", SheetDoorSeal);
        Guard("SHEET_SOAKS_IN_COMPLETELY", SHEET, "fixed", SheetSoaksIn);
        Guard("SHEET_SETTINGS_SWEEP_EXTREMES", SHEET, "sweep", SheetSettingsSweep);
        Guard("SHEET_SPILL_SWITCHES", SHEET, "fixed", SheetAccepts);
        Guard("CONV_LONG_RUN_RATE_NOTHING_EATEN", CONV, "sweep", ConvRate);
        Guard("CONV_IDLE_BURST_BOUNDED", CONV, "sweep", ConvIdle);
        Guard("CONV_BATCH_BOUNDS_CONSERVE", CONV, "random", ConvBatches);
        Guard("CONV_ROTATION_FAIR_NO_STARVING", CONV, "random", ConvRotation);
        Guard("CONV_BLOCKED_SMALL_RECIPE_NEVER_STARVES_BIG", CONV, "fixed", ConvBlocked);
        Guard("CONV_BUDGET_ZERO_AND_LINEAR", CONV, "sweep", ConvBudget);
        Guard("DRILL_PLACEMENT_TABLE", DRILL, "fixed", DrillPlacement);
        Guard("DRILL_WHYNOT_SOUND_AND_COMPLETE", DRILL, "fixed", DrillWhyNot);
        Guard("DRILL_PLACEMENT_AGREES_WITH_WHYNOT", DRILL, "fixed", DrillAgree);
        Guard("DRILL_SPENT_UNITS_CONSERVE", DRILL, "random", DrillSpent);
        Guard("SPRK_DECIDE_NEEDS_PUMP_ALL_OR_NOTHING", SPRK, "fixed", SprkDecide);
        Guard("SPRK_UNITS_NEVER_FREE_SLIDER_SWEEP", SPRK, "sweep", SprkUnits);
        Guard("SPRK_VALVE_BUDGET_RESERVE_NEAREST", SPRK, "random", SprkValve);
        Guard("SPRK_PICK_LIQUID_ARGMAX_ORDER_FREE", SPRK, "random", SprkPick);
        Guard("SPRK_WET_GRID_LIFETIME", SPRK, "fixed", SprkGrid);
        Guard("SPRK_RADIUS_CHOICES_CELLS", SPRK, "info", SprkRadius);
        Guard("THIRST_RULED_NUMBERS", THIRST, "fixed", ThirstRuled);
        Guard("THIRST_RATE_SLIDER_SWEEP", THIRST, "sweep", ThirstRateSweep);
        Guard("THIRST_DEHYDRATION_TIMELINE", THIRST, "fixed", ThirstDehydration);
        Guard("THIRST_MAY_DRINK_MATRIX", THIRST, "fixed", ThirstMayDrink);
        Guard("THIRST_PICK_ORDER_IS_STRICT", THIRST, "random", ThirstOrder);
        Guard("THIRST_SPENDABLE_RESERVE_SWEEP", THIRST, "sweep", ThirstSpendable);
        Guard("THIRST_DAYS_OF_WATER_AGREES_WITH_FALL", THIRST, "sweep", ThirstDays);
        Guard("THIRST_CATEGORY_DESPERATE_CONSISTENT", THIRST, "sweep", ThirstCategory);
        NotKernel();
        return fails > 0 ? 1 : 0;
    }

    // Bars whose inputs changed since cycle 1 but whose logic is game-side (Verse jobs, Harmony, defs, live scenes): owed to Stage 6.
    static void NotKernel()
    {
        var rows = new (string bar, string why)[]
        {
            ("inv_toss_flame", "RM_TossFlame.cs (new, 169 lines) is a JobDriver + float-menu provider on Verse; JobDef RM_TossFlame added. No Verse-free kernel."),
            ("toss_flame_from_rim", "a colonist walking to the rim and tossing a flame is a Verse job (RM_TossFlame.cs); live scene only."),
            ("inv_raider_fetch_fallen", "RM_RaiderFetchFallen.cs (new, 247 lines) is a JobGiver/JobDriver/Harmony patch; AssaultColony duty patched (FlowWorks_RaiderTrenchDuties.xml). No kernel."),
            ("raiders_fetch_their_fallen", "raider AI (chop wood for a ladder, fetch, leave when driven off) is lord/duty behaviour; live scene only."),
            ("trench_gives_cover", "RM_RaiderTrench.cs changed (14 lines) and FlowWorks_RaiderTrench.xml jobs; cover and AI shelter choice are game-side."),
            ("inv_trench_cover", "as trench_gives_cover: RM_RaiderTrench.cs and its JobDefs, game-side."),
            ("inv_liquid_coating", "RM_LiquidCoating.cs (new, 205 lines) is a Hediff and a per-tick pawn check on Verse; FluidDef.coats/washesCoat added to the fluid defs. No kernel."),
            ("inv_liquid_roster", "FlowWorks_Fluids.xml / FlowWorks_PitFluids.xml / FluidDef.cs gained coats/washesCoat fields only (def data read by RM_LiquidCoating)."),
            ("inv_dig_depth", "RM_MapComponent_Excavation.cs changed (2 lines), a Verse map component; no kernel touched."),
            ("inv_settings", "RimMandrakeFlowWorksMod.cs changed (32 lines): the settings window on Verse; a settings window is judged in game."),
            ("inv_pits", "Pit_Hediffs.xml changed (17 lines, the RM_LiquidCoat hediff lives there); pits are game-side."),
            ("moat_raid_sequence", "northstar scene scripts changed (concept_scenes.py, selftest_moat_scene.py); the flagship is a live sequence."),
            ("drained_hole_is_a_prison", "selftest_hole_prison.py changed; capture with no bed is a live mechanic."),
            ("covered_pit_springs", "selftest_pit_trap_raid_scene.py changed; a live raid scene."),
            ("island_bridges_trap_and_fail", "selftest_islands_scene.py changed; a live raid scene."),
            ("ice_cuts_and_melts", "selftest_ice_scene.py changed; live scene."),
            ("pawn_height_follows_depth", "selftest_pawn_height_scene.py changed; live render."),
            ("hose_reads_as_hose", "selftest_hose_look_scene.py changed; a look bar."),
            ("source_pays_and_refills", "selftest_source_pays_scene.py changed; live scene (the stock kernel RM_StockMath.cs did not change)."),
            ("walk_moat_season", "selftest_walk_scene.py changed; the walk is live by definition."),
        };
        foreach (var (bar, why) in rows) Row("NOT_KERNEL_" + bar.ToUpperInvariant(), new[] { bar }, "not_kernel", "UNSETTLED", 0, why + " Owed to Stage 6.");
    }

    // ───────────────────────────── sheet (inv_overflow_sheet) ─────────────────────────────

    enum OpK { Spill, Pulse, Burn, Purge, PurgeConn, HandOver, SaveLoad }
    sealed class Op
    {
        public OpK K; public int Cell, Dl; public bool Lake; public List<SM.SpillOffer> Offers;
        public override string ToString()
        {
            switch (K)
            {
                case OpK.Spill: return "Spill[" + string.Join(";", Offers.Select(o => "f" + o.Fluid + " " + o.From + " " + o.AmountDl + "dL lips " + string.Join(",", o.LipNearestFirst))) + "]";
                case OpK.Burn: return "Burn(" + Cell + "," + Dl + ")";
                case OpK.PurgeConn: return "PurgeConn(" + Cell + "," + Dl + ")";
                case OpK.HandOver: return "HandOver(" + Cell + "," + Dl + "," + Lake + ")";
                default: return K.ToString();
            }
        }
    }

    sealed class Scenario { public int W, H; public uint Salt; public SM.World World; public SM.Params P; public List<Op> Ops; }

    static SM.World RandomWorld(Random r, int w, int h, bool losses, bool cold)
    {
        var wd = new SM.World(w, h);
        for (int c = 0; c < w * h; c++)
        {
            int k = r.Next(100);
            wd.Kinds[c] = k < 70 ? SM.Kind.Open : k < 80 ? SM.Kind.Blocked : k < 85 ? SM.Kind.Door : k < 90 ? SM.Kind.Grate : k < 95 ? SM.Kind.Receiver : SM.Kind.Sink;
            if (wd.Kinds[c] == SM.Kind.Receiver) wd.RoomDl[c] = r.Next(0, 5000);
            if (wd.Kinds[c] == SM.Kind.Receiver || wd.Kinds[c] == SM.Kind.Sink) wd.BodyFluid[c] = (byte)r.Next(0, 3);
            if (losses) { wd.SoakMilliDl[c] = r.Next(0, 900); wd.EvapMilliDl[c] = r.Next(0, 300); }
            if (cold) wd.TempDeciC[c] = r.Next(-60, 60);
        }
        wd.Fluids[1] = new SM.FluidRule { InfiltrationPermille = 1000, EvaporationPermille = 1000, FreezeDeciC = 0 };
        wd.Fluids[2] = new SM.FluidRule { InfiltrationPermille = 500, EvaporationPermille = 300, NeverFreezes = true };
        wd.Fluids[3] = new SM.FluidRule { InfiltrationPermille = 0, EvaporationPermille = 2000, NeverFreezes = true, BoilMilliDl = 3000, BoilAboveDeciC = -400 };
        return wd;
    }

    static Scenario MakeScenario(int seed, bool withSaveLoad)
    {
        var r = new Random(seed);
        int w = r.Next(3, 13), h = r.Next(3, 11);
        var sc = new Scenario { W = w, H = h, Salt = (uint)r.Next(), P = new SM.Params(), Ops = new List<Op>() };
        sc.World = RandomWorld(r, w, h, r.Next(3) > 0, r.Next(4) == 0);
        if (r.Next(4) == 0) sc.P.MaxWetCells = r.Next(1, 12);
        if (r.Next(3) == 0) sc.P.SheetCapDl = r.Next(1, 30) * SM.DlPerCm;
        int n = r.Next(10, 70);
        for (int i = 0; i < n; i++)
        {
            int t = r.Next(100);
            if (t < 35)
            {
                var offers = new List<SM.SpillOffer>();
                int no = r.Next(1, 4);
                for (int k = 0; k < no; k++)
                {
                    int nl = r.Next(1, 6);
                    var lips = new int[nl];
                    for (int q = 0; q < nl; q++) lips[q] = r.Next(-1, w * h + 1);
                    offers.Add(new SM.SpillOffer { LipNearestFirst = lips, AmountDl = r.Next(0, 6000), Fluid = (byte)r.Next(0, 4), From = (SM.Source)r.Next(0, SM.SourceCount) });
                }
                sc.Ops.Add(new Op { K = OpK.Spill, Offers = offers });
            }
            else if (t < 80) sc.Ops.Add(new Op { K = OpK.Pulse });
            else if (t < 85) sc.Ops.Add(new Op { K = OpK.Burn, Cell = r.Next(-1, w * h + 1), Dl = r.Next(-5, 3000) });
            else if (t < 87) sc.Ops.Add(new Op { K = OpK.Purge });
            else if (t < 90) sc.Ops.Add(new Op { K = OpK.PurgeConn, Cell = r.Next(-1, w * h + 1), Dl = r.Next(-2, 4000) });
            else if (t < 95) sc.Ops.Add(new Op { K = OpK.HandOver, Cell = r.Next(0, w * h), Dl = r.Next(0, 3000), Lake = r.Next(2) == 0 });
            else if (withSaveLoad) sc.Ops.Add(new Op { K = OpK.SaveLoad });
            else sc.Ops.Add(new Op { K = OpK.Pulse });
        }
        return sc;
    }

    static SM.SpillOffer CloneOffer(SM.SpillOffer o) => new SM.SpillOffer { LipNearestFirst = (int[])o.LipNearestFirst.Clone(), AmountDl = o.AmountDl, Fluid = o.Fluid, From = o.From };

    // Runs the ops, checking the invariants after each; returns null or the first violation.
    static string RunChecked(Scenario sc, List<Op> ops, out SM.State finalState)
    {
        var w = sc.World.Clone();
        var p = sc.P;
        var s = new SM.State(sc.W, sc.H, sc.Salt);
        var rep = new SM.PulseReport();
        finalState = s;
        for (int i = 0; i < ops.Count; i++)
        {
            Op op = ops[i];
            long beforeIn = s.TotalIn;
            switch (op.K)
            {
                case OpK.Spill:
                    var offers = op.Offers.Select(CloneOffer).ToList();
                    int[] acc = SM.ResolveSpills(s, w, p, offers);
                    for (int k = 0; k < offers.Count; k++)
                        if (acc[k] < 0 || acc[k] > Math.Max(0, offers[k].AmountDl)) return "op " + i + ": accepted " + acc[k] + " of " + offers[k].AmountDl;
                    if (s.TotalIn - beforeIn != acc.Sum()) return "op " + i + ": In grew by " + (s.TotalIn - beforeIn) + " but accepted " + acc.Sum();
                    break;
                case OpK.Pulse: SM.Pulse(s, w, p, rep); break;
                case OpK.Burn: SM.Burn(s, op.Cell, op.Dl); break;
                case OpK.Purge: SM.PurgeAll(s); break;
                case OpK.PurgeConn: SM.PurgeConnected(s, op.Cell, op.Dl == -1 ? SM.AllDl : op.Dl); break;
                case OpK.HandOver: SM.HandOver(s, op.Cell, op.Dl, op.Lake); break;
                case OpK.SaveLoad: s = SM.Load(SM.Save(s)); break;
            }
            finalState = s;
            string v = Invariants(s, w, p);
            if (v != null) return "op " + i + " (" + op + "): " + v;
        }
        return null;
    }

    static string Invariants(SM.State s, SM.World w, SM.Params p)
    {
        if (!s.LedgerCloses) return "ledger open: In " + s.TotalIn + " != Standing " + s.Standing + " + Out " + s.TotalOut;
        var occ = new HashSet<int>();
        for (int i = 0; i < s.Occ.Count; i++)
        {
            if (i > 0 && s.Occ[i] <= s.Occ[i - 1]) return "Occ not ascending/unique at " + i;
            occ.Add(s.Occ[i]);
        }
        if (s.Occ.Count > p.MaxWetCells) return "wet cells " + s.Occ.Count + " over cap " + p.MaxWetCells;
        for (int c = 0; c < s.Dl.Length; c++)
        {
            if (s.Dl[c] < 0) return "cell " + c + " holds " + s.Dl[c] + " dL";
            if (s.Dl[c] > 0 != occ.Contains(c)) return "cell " + c + " Dl " + s.Dl[c] + " but in Occ=" + occ.Contains(c);
            if (s.Dl[c] == 0 && (s.Fluid[c] != 0 || s.Tiers[c] != SM.Tier.None)) return "dry cell " + c + " keeps fluid " + s.Fluid[c] + " tier " + s.Tiers[c];
            if (s.Dl[c] > 0 && s.Fluid[c] == 0) return "wet cell " + c + " has no fluid";
            if (s.Dl[c] > 0 && !SM.World.HoldsSheet(w.Kinds[c])) return "sheet on a " + w.Kinds[c] + " cell " + c;
            if (s.Dl[c] > p.SheetCapDl) return "cell " + c + " holds " + s.Dl[c] + " over the cap " + p.SheetCapDl;
            if (w.Kinds[c] == SM.Kind.Receiver && w.RoomDl[c] < 0) return "receiver " + c + " room went negative";
        }
        return null;
    }

    static List<Op> Shrink(Scenario sc, List<Op> ops)
    {
        var cur = new List<Op>(ops);
        bool progress = true;
        while (progress)
        {
            progress = false;
            for (int i = cur.Count - 1; i >= 0; i--)
            {
                var trial = new List<Op>(cur); trial.RemoveAt(i);
                if (RunChecked(sc, trial, out _) != null) { cur = trial; progress = true; }
            }
        }
        return cur;
    }

    static void SheetRandom()
    {
        int seeds = 600, ops = 0;
        for (int seed = 1; seed <= seeds; seed++)
        {
            var sc = MakeScenario(seed, true);
            ops += sc.Ops.Count;
            string v = RunChecked(sc, sc.Ops, out _);
            if (v != null)
            {
                var small = Shrink(sc, sc.Ops);
                Row("SHEET_RANDOM_LEDGER_AND_INVARIANTS", SHEET, "random", "FAIL", seed, "seed " + seed + " grid " + sc.W + "x" + sc.H + ": " + v
                    + " | shrunk to " + small.Count + " ops: " + string.Join(" ", small) + " -> " + RunChecked(sc, small, out _));
                return;
            }
        }
        Row("SHEET_RANDOM_LEDGER_AND_INVARIANTS", SHEET, "random", "PASS", seeds, "seeds 1.." + seeds + ", " + ops + " ops (spills of 4 fluids incl. invalid lips, pulses with soak/evap/boil/freeze, burns, purges, hand-overs, save/load); after every op: In == Standing + Out to the dL, no negative cell, Occ == wet cells, dry cells carry no fluid/tier, sheet only on Open/Door/Grate, never over the cap or the wet-cell cap, receiver room never negative");
    }

    static void SheetSaveLoad()
    {
        int seeds = 300, checks = 0;
        for (int seed = 1; seed <= seeds; seed++)
        {
            var sc = MakeScenario(10000 + seed, false);
            var r = new Random(seed);
            int cut = r.Next(0, sc.Ops.Count);
            // A: uninterrupted; B: saved and loaded at the cut. Same world, same params.
            var wa = sc.World.Clone(); var wb = sc.World.Clone();
            var a = new SM.State(sc.W, sc.H, sc.Salt); var b = new SM.State(sc.W, sc.H, sc.Salt);
            var ra = new SM.PulseReport(); var rb = new SM.PulseReport();
            for (int i = 0; i < sc.Ops.Count; i++)
            {
                if (i == cut) b = SM.Load(SM.Save(b));
                foreach (var (st, wd, rp) in new[] { (a, wa, ra), (b, wb, rb) }) Apply(st, wd, sc.P, rp, sc.Ops[i]);
                if (i >= cut)
                {
                    checks++;
                    if (SM.Hash(a) != SM.Hash(b))
                    {
                        Row("SHEET_SAVELOAD_CONTINUES_IDENTICAL", SHEET, "random", "FAIL", seed, "seed " + (10000 + seed) + " cut at op " + cut + ": state hash splits at op " + i + " (" + sc.Ops[i] + ")");
                        return;
                    }
                    if (sc.Ops[i].K == OpK.Pulse && !SameReport(ra, rb) && !(i == cut))
                    {
                        Row("SHEET_SAVELOAD_CONTINUES_IDENTICAL", SHEET, "random", "FAIL", seed, "seed " + (10000 + seed) + " cut at op " + cut + ": pulse report differs at op " + i);
                        return;
                    }
                }
            }
        }
        Row("SHEET_SAVELOAD_CONTINUES_IDENTICAL", SHEET, "random", "PASS", seeds, seeds + " random runs, each saved+loaded at a random op; state hash identical to the uninterrupted run after every later op (" + checks + " compares); pulse reports identical after the first pulse past the cut (" + driedNotReplayed + " reports lacked only drying done before the save, which is not saved by design)");
    }

    static int driedNotReplayed;
    // Dried (between-pulse drying awaiting report) is not saved by design ("a dry cell has no picture to keep"): a report that
    // differs ONLY by such leading to-None entries is counted, not failed.
    static bool SameReport(SM.PulseReport x, SM.PulseReport y)
    {
        if (!(x.Soaked.SequenceEqual(y.Soaked) && x.CropDrowning.SequenceEqual(y.CropDrowning) && x.Returned.SequenceEqual(y.Returned))) return false;
        if (x.TierChanged.SequenceEqual(y.TierChanged)) return true;
        int k = x.TierChanged.Count - y.TierChanged.Count;
        if (k > 0 && x.TierChanged.Skip(k).SequenceEqual(y.TierChanged) && x.TierChanged.Take(k).All(t => t.to == SM.Tier.None)) { driedNotReplayed++; return true; }
        return false;
    }

    static void Apply(SM.State s, SM.World w, SM.Params p, SM.PulseReport rep, Op op)
    {
        switch (op.K)
        {
            case OpK.Spill: SM.ResolveSpills(s, w, p, op.Offers.Select(CloneOffer).ToList()); break;
            case OpK.Pulse: SM.Pulse(s, w, p, rep); break;
            case OpK.Burn: SM.Burn(s, op.Cell, op.Dl); break;
            case OpK.Purge: SM.PurgeAll(s); break;
            case OpK.PurgeConn: SM.PurgeConnected(s, op.Cell, op.Dl == -1 ? SM.AllDl : op.Dl); break;
            case OpK.HandOver: SM.HandOver(s, op.Cell, op.Dl, op.Lake); break;
        }
    }

    static void SheetOrderFree()
    {
        int seeds = 400;
        for (int seed = 1; seed <= seeds; seed++)
        {
            var sc = MakeScenario(20000 + seed, false);
            var r = new Random(seed);
            var pre = sc.Ops.Take(r.Next(0, sc.Ops.Count)).ToList();
            var a = new SM.State(sc.W, sc.H, sc.Salt); var wa = sc.World.Clone();
            foreach (var op in pre) Apply(a, wa, sc.P, null, op);
            var b = SM.Load(SM.Save(a)); var wb = wa.Clone();
            var offers = new List<SM.SpillOffer>();
            for (int k = 0; k < r.Next(2, 6); k++)
            {
                var lips = Enumerable.Range(0, r.Next(1, 5)).Select(_ => r.Next(0, sc.W * sc.H)).ToArray();
                offers.Add(new SM.SpillOffer { LipNearestFirst = lips, AmountDl = r.Next(1, 8000), Fluid = (byte)r.Next(1, 4), From = (SM.Source)r.Next(0, 5) });
            }
            var perm = offers.Select((o, i) => i).OrderBy(_ => r.Next()).ToArray();
            int[] accA = SM.ResolveSpills(a, wa, sc.P, offers.Select(CloneOffer).ToList());
            int[] accB = SM.ResolveSpills(b, wb, sc.P, perm.Select(i => CloneOffer(offers[i])).ToList());
            for (int i = 0; i < perm.Length; i++)
                if (accB[i] != accA[perm[i]])
                {
                    Row("SHEET_SPILL_ORDER_FREE", SHEET, "random", "FAIL", seed, "seed " + seed + ": offer " + perm[i] + " accepted " + accA[perm[i]] + " in caller order, " + accB[i] + " permuted");
                    return;
                }
            if (SM.Hash(a) != SM.Hash(b)) { Row("SHEET_SPILL_ORDER_FREE", SHEET, "random", "FAIL", seed, "seed " + seed + ": state differs with the offers permuted"); return; }
        }
        Row("SHEET_SPILL_ORDER_FREE", SHEET, "random", "PASS", seeds, "2-5 offers resolved in caller order and permuted give the same accepted dL per offer and the same state");
    }

    static void SheetPreview()
    {
        int seeds = 600;
        for (int seed = 1; seed <= seeds; seed++)
        {
            var sc = MakeScenario(30000 + seed, false);
            var r = new Random(seed);
            var a = new SM.State(sc.W, sc.H, sc.Salt); var wa = sc.World.Clone();
            foreach (var op in sc.Ops.Take(r.Next(0, sc.Ops.Count))) Apply(a, wa, sc.P, null, op);
            var lips = Enumerable.Range(0, r.Next(1, 7)).Select(_ => r.Next(-1, sc.W * sc.H)).ToArray();
            if (r.Next(3) == 0 && lips.Length > 1) lips[lips.Length - 1] = lips[0]; // a repeated lip
            var o = new SM.SpillOffer { LipNearestFirst = lips, AmountDl = r.Next(-10, 20000), Fluid = (byte)r.Next(0, 4), From = (SM.Source)r.Next(0, 5) };
            ulong h0 = SM.Hash(a);
            int pv = SM.PreviewSpill(a, wa, sc.P, o);
            if (SM.Hash(a) != h0) { Row("SHEET_PREVIEW_EQUALS_ACCEPT", SHEET, "random", "FAIL", seed, "seed " + seed + ": PreviewSpill changed the state"); return; }
            int ac = SM.ResolveSpills(a, wa, sc.P, new List<SM.SpillOffer> { CloneOffer(o) })[0];
            if (pv != ac) { Row("SHEET_PREVIEW_EQUALS_ACCEPT", SHEET, "random", "FAIL", seed, "seed " + (30000 + seed) + ": preview " + pv + " but accepted " + ac + " for lips " + string.Join(",", lips) + " amount " + o.AmountDl + " fluid " + o.Fluid + " wet " + a.WetCount + "/" + sc.P.MaxWetCells); return; }
        }
        Row("SHEET_PREVIEW_EQUALS_ACCEPT", SHEET, "random", "PASS", seeds, "PreviewSpill changes nothing and equals the single-offer ResolveSpills accept, repeated and invalid lips included");
    }

    static (SM.State, SM.World) Basin(int w, int h, int inner, int fill, byte fluid, int soak = 0, int evap = 0)
    {
        // a w x h grid walled at its rim (Blocked), open inside
        var wd = new SM.World(w, h);
        for (int z = 0; z < h; z++) for (int x = 0; x < w; x++)
        {
            int c = z * w + x;
            wd.Kinds[c] = x == 0 || z == 0 || x == w - 1 || z == h - 1 ? SM.Kind.Blocked : SM.Kind.Open;
            wd.SoakMilliDl[c] = soak; wd.EvapMilliDl[c] = evap;
        }
        wd.Fluids[1] = new SM.FluidRule { InfiltrationPermille = 1000, EvaporationPermille = 1000, FreezeDeciC = 0 };
        var s = new SM.State(w, h, 7);
        return (s, wd);
    }

    static int FirstDrownPulse(int stand, SM.Params p, int maxPulses)
    {
        var (s, w) = Basin(3, 3, 1, stand, 1);
        SM.ResolveSpills(s, w, p, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 4 }, AmountDl = stand, Fluid = 1, From = SM.Source.Pump } });
        var rep = new SM.PulseReport();
        for (int i = 1; i <= maxPulses; i++)
        {
            SM.Pulse(s, w, p, rep);
            if (rep.CropDrowning.Count > 0) return i;
        }
        return -1;
    }

    static void SheetCropWeek()
    {
        var p = new SM.Params();
        // the bar: "kills crops under standing overflow after a week"; a week at the shipped 250-tick pulse
        int week = 7 * 60000 / 250;
        int first = FirstDrownPulse(5 * SM.DlPerCm, p, week + 10);
        bool young = !SM.CropDrowns(week + 5, week * 250 - 1, 250, p), old = SM.CropDrowns(week, week * 250, 250, p);
        bool ok = first == week && p.CropKillPulses == week && young && old;
        Row("SHEET_CROPS_DROWN_AFTER_ONE_WEEK", SHEET, "fixed", ok ? "PASS" : "FAIL", 4,
            "5 cm standing on one square, no losses: first CropDrowning at pulse " + first + " (expected " + week + " = 7 days x 60000 / 250); Params.CropKillPulses " + p.CropKillPulses
            + "; a crop one tick younger than a week survives: " + young + "; a week-old one drowns: " + old);
    }

    static void SheetCropSweep()
    {
        // shipped slider: 0.5 to 30 days in half days, converted with PulsesFor(days*60000, 250)
        int cases = 0; string bad = null;
        for (double d = 0.5; d <= 30.0001 && bad == null; d += 0.5)
        {
            var p = new SM.Params { CropKillPulses = Math.Max(1, SM.PulsesFor((int)Math.Round(d * 60000), 250)) };
            int expect = (int)Math.Ceiling(d * 60000 / 250);
            if (d > 3 && (int)(d * 2) % 7 != 0) continue; // sample the long end
            int first = FirstDrownPulse(5 * SM.DlPerCm, p, expect + 5);
            cases++;
            if (first != expect) bad = d + " days: first drown at pulse " + first + ", expected " + expect;
        }
        Row("SHEET_CROP_DELAY_SETTING_SWEEP", SHEET, "sweep", bad == null ? "PASS" : "FAIL", cases, bad ?? "the crop-drown delay slider (0.5-30 days) maps to the first CropDrowning at exactly ceil(days x 240) pulses");
    }

    static void SheetFilmNeverDrowns()
    {
        var p = new SM.Params();
        int film = FirstDrownPulse(2 * SM.DlPerCm, p, p.CropKillPulses * 2);
        Row("SHEET_FILM_NEVER_DROWNS", SHEET, "fixed", film == -1 ? "PASS" : "FAIL", 1, "2 cm (a film, under the 3 cm sheet tier) standing two weeks: first drown " + film + " (expected never, -1): a film only irrigates");
    }

    static void SheetTiers()
    {
        var p = new SM.Params();
        int D = SM.DlPerCm; var errs = new List<string>();
        void Eq(SM.Tier got, SM.Tier want, string what) { if (got != want) errs.Add(what + ": " + got + " want " + want); }
        Eq(SM.NextTier(SM.Tier.None, 0, p), SM.Tier.None, "dry");
        Eq(SM.NextTier(SM.Tier.None, 1, p), SM.Tier.Film, "1 dL");
        Eq(SM.NextTier(SM.Tier.None, 3 * D, p), SM.Tier.Sheet, "3 cm up");
        Eq(SM.NextTier(SM.Tier.Film, 3 * D - 1, p), SM.Tier.Film, "just under 3 cm");
        Eq(SM.NextTier(SM.Tier.Sheet, 2 * D, p), SM.Tier.Sheet, "sheet holds at 2 cm");
        Eq(SM.NextTier(SM.Tier.Sheet, 2 * D - 1, p), SM.Tier.Film, "sheet drops under 2 cm");
        Eq(SM.NextTier(SM.Tier.None, 15 * D, p), SM.Tier.Pool, "15 cm up");
        Eq(SM.NextTier(SM.Tier.Pool, 13 * D, p), SM.Tier.Pool, "pool holds at 13 cm");
        Eq(SM.NextTier(SM.Tier.Pool, 13 * D - 1, p), SM.Tier.Sheet, "pool drops under 13 cm");
        Eq(SM.NextTier(SM.Tier.Pool, D, p), SM.Tier.Film, "pool to 1 cm");
        Eq(SM.NextTier(SM.Tier.Ice, 5 * D, p), SM.Tier.Sheet, "thawed 5 cm");
        int cases = 11;
        foreach (SM.Tier t in new[] { SM.Tier.None, SM.Tier.Film, SM.Tier.Sheet, SM.Tier.Pool, SM.Tier.Ice })
            for (int dl = 0; dl <= 20 * D; dl += 7)
            {
                cases++;
                var t1 = SM.NextTier(t, dl, p);
                if (SM.NextTier(t1, dl, p) != t1) { errs.Add("flaps at " + t + " " + dl); break; }
            }
        Row("SHEET_TIER_HYSTERESIS", SHEET, "fixed", errs.Count == 0 ? "PASS" : "FAIL", cases, errs.Count == 0 ? "film/sheet/pool with 3/2 cm and 15/13 cm bands; tier is a fixed point at constant depth (no flapping)" : string.Join("; ", errs.Take(5)));
    }

    static void SheetLevel()
    {
        int seeds = 120; string bad = null; int cases = 0;
        for (int seed = 1; seed <= seeds && bad == null; seed++)
        {
            var r = new Random(seed);
            int w = r.Next(4, 12), h = r.Next(4, 10);
            var (s, wd) = Basin(w, h, 0, 0, 1);
            var p = new SM.Params();
            int inner = (w - 2) * (h - 2);
            int vol = r.Next(inner * 2 * SM.DlPerCm, inner * 40 * SM.DlPerCm);
            int lip = (1 + r.Next(h - 2)) * w + 1 + r.Next(w - 2);
            int left = vol;
            for (int k = 0; k < 400 && left > 0; k++)
            {
                left -= SM.ResolveSpills(s, wd, p, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { lip }, AmountDl = left, Fluid = 1, From = SM.Source.Pump } })[0];
                SM.Pulse(s, wd, p, null);
            }
            for (int k = 0; k < 300; k++) SM.Pulse(s, wd, p, null);
            cases++;
            // every interior cell wet, one surface: Dl + relief equal to within 1 dL for every cell between retention and cap
            long lo = long.MaxValue, hi = long.MinValue; int dry = 0;
            for (int c = 0; c < w * h; c++)
            {
                if (wd.Kinds[c] != SM.Kind.Open) continue;
                if (s.Dl[c] == 0) { dry++; continue; }
                if (s.Dl[c] <= p.RetentionDl || s.Dl[c] >= p.SheetCapDl) continue;
                long surf = s.Dl[c] + SM.Relief(s.Salt, c, p.ReliefDl);
                lo = Math.Min(lo, surf); hi = Math.Max(hi, surf);
            }
            if (left > 0 && s.Standing < (long)inner * p.SheetCapDl) bad = "seed " + seed + ": " + left + " dL refused before the basin was full";
            else if (dry > 0 && s.Standing >= (long)inner * 2 * p.RetentionDl) bad = "seed " + seed + ": " + dry + " interior squares dry under " + s.Standing + " dL in a " + inner + "-square basin";
            else if (hi != long.MinValue && hi - lo > 1) bad = "seed " + seed + " " + w + "x" + h + " vol " + vol + ": surface spread " + (hi - lo) + " dL after 300 still pulses";
            else if (!s.LedgerCloses) bad = "seed " + seed + ": ledger open";
        }
        Row("SHEET_LIES_LEVEL", SHEET, "random", bad == null ? "PASS" : "FAIL", cases, bad ?? "walled basins 2x2..10x8, 2-40 cm poured at one lip, no losses: every square wet, one surface (Dl + relief) to within 1 dL, ledger closed");
    }

    static void SheetFreeze()
    {
        var p = new SM.Params();
        var (s, w) = Basin(5, 3, 0, 0, 1);  // interior cells 6, 7, 8
        SM.ResolveSpills(s, w, p, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 6 }, AmountDl = 3000, Fluid = 1, From = SM.Source.Rain } });
        w.TempDeciC[6] = -1; w.TempDeciC[7] = -1; w.TempDeciC[8] = -1;
        var rep = new SM.PulseReport();
        SM.Pulse(s, w, p, rep);
        var errs = new List<string>();
        if (s.Tiers[6] != SM.Tier.Ice) errs.Add("cell 6 at -0.1 C is " + s.Tiers[6]);
        if (s.Dl[6] != 3000) errs.Add("froze with " + s.Dl[6] + " dL of 3000");
        for (int i = 0; i < 50; i++) SM.Pulse(s, w, p, rep);
        if (s.Dl[7] != 0) errs.Add("ice flowed " + s.Dl[7] + " dL to its neighbour");
        w.TempDeciC[6] = 9; SM.Pulse(s, w, p, rep);
        if (s.Tiers[6] != SM.Tier.Ice) errs.Add("thawed at +0.9 C (margin 1 C)");
        w.TempDeciC[6] = 10; w.TempDeciC[7] = 10; w.TempDeciC[8] = 10; SM.Pulse(s, w, p, rep);
        if (s.Tiers[6] == SM.Tier.Ice) errs.Add("still ice at +1.0 C");
        for (int i = 0; i < 100; i++) SM.Pulse(s, w, p, rep);
        if (s.Standing != 3000) errs.Add("after thaw standing " + s.Standing);
        if (s.Dl[8] == 0) errs.Add("thawed water never spread");
        Row("SHEET_FREEZE_KEEPS_EVERY_DL", SHEET, "fixed", errs.Count == 0 ? "PASS" : "FAIL", 7, errs.Count == 0 ? "freezes strictly below 0 C keeping all 3000 dL, ice does not flow, holds at +0.9 C, thaws at +1.0 C and spreads, nothing lost" : string.Join("; ", errs));
    }

    static void SheetLowerCap()
    {
        var p = new SM.Params();
        var (s, w) = Basin(6, 6, 0, 0, 1);
        int left = 16 * 40 * SM.DlPerCm;
        for (int k = 0; k < 100 && left > 0; k++) { left -= SM.ResolveSpills(s, w, p, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 14 }, AmountDl = left, Fluid = 1, From = SM.Source.Flood } })[0]; SM.Pulse(s, w, p, null); }
        long before = s.Standing;
        p.SheetCapDl = 10 * SM.DlPerCm;
        int refused = SM.ResolveSpills(s, w, p, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 14, 15 }, AmountDl = 500, Fluid = 1, From = SM.Source.Flood } })[0];
        for (int i = 0; i < 200; i++) SM.Pulse(s, w, p, null);
        bool ok = s.Standing == before && refused == 0 && s.LedgerCloses;
        Row("SHEET_LOWER_CAP_DELETES_NOTHING", SHEET, "fixed", ok ? "PASS" : "FAIL", 3, "basin filled to ~40 cm then the cap lowered to 10 cm: standing " + before + " -> " + s.Standing + " (no losses set), new spill accepted " + refused + " (expected 0), ledger " + s.LedgerCloses);
    }

    static void SheetSink()
    {
        var p = new SM.Params();
        var w = new SM.World(3, 1);
        w.Kinds[0] = SM.Kind.Blocked; w.Kinds[1] = SM.Kind.Open; w.Kinds[2] = SM.Kind.Sink;
        w.Fluids[1] = new SM.FluidRule { InfiltrationPermille = 1000, EvaporationPermille = 1000 };
        var s = new SM.State(3, 1, 1);
        SM.ResolveSpills(s, w, p, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 1 }, AmountDl = 2000, Fluid = 1, From = SM.Source.Pump } });
        for (int i = 0; i < 20; i++) SM.Pulse(s, w, p, null);
        bool ok = s.Dl[1] == p.RetentionDl && s.JoinedLake == 2000 - p.RetentionDl && s.LedgerCloses;
        Row("SHEET_SINK_TAKES_ONLY_MOBILE", SHEET, "fixed", ok ? "PASS" : "FAIL", 1, "2000 dL beside an endless lake: left " + s.Dl[1] + " dL (retention " + p.RetentionDl + "), joined the lake " + s.JoinedLake);
    }

    static void SheetDoorSeal()
    {
        var p = new SM.Params { DoorLeakPermille = 0 };
        var w = new SM.World(5, 1);
        w.Kinds[0] = SM.Kind.Open; w.Kinds[1] = SM.Kind.Open; w.Kinds[2] = SM.Kind.Door; w.Kinds[3] = SM.Kind.Open; w.Kinds[4] = SM.Kind.Sink;
        w.Fluids[1] = new SM.FluidRule { InfiltrationPermille = 1000, EvaporationPermille = 1000 };
        var s = new SM.State(5, 1, 3);
        SM.ResolveSpills(s, w, p, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 0, 1 }, AmountDl = 8000, Fluid = 1, From = SM.Source.Pump } });
        for (int i = 0; i < 400; i++) SM.Pulse(s, w, p, null);
        bool sealedOk = s.Dl[2] == 0 && s.Dl[3] == 0 && s.JoinedLake == 0;
        var p2 = new SM.Params(); var s2 = new SM.State(5, 1, 3);
        SM.ResolveSpills(s2, w, p2, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 0, 1 }, AmountDl = 8000, Fluid = 1, From = SM.Source.Pump } });
        for (int i = 0; i < 400; i++) SM.Pulse(s2, w, p2, null);
        bool leaks = s2.JoinedLake > 0;
        Row("SHEET_DOOR_ZERO_SEALS", SHEET, "fixed", sealedOk && leaks ? "PASS" : "FAIL", 2, "door leak 0%: door/beyond " + s.Dl[2] + "/" + s.Dl[3] + " dL, lake " + s.JoinedLake + " (expected 0/0/0); shipped 5%: lake got " + s2.JoinedLake + " over 400 pulses (expected > 0)");
    }

    static void SheetSoaksIn()
    {
        // shipped soak 2 cm/day soil = 400 dL / 240 pulses = 1666 milli-dL a pulse; 5 cm should be gone within ~2.5 days
        var p = new SM.Params();
        var (s, w) = Basin(3, 3, 0, 0, 1, soak: 1666, evap: 0);
        SM.ResolveSpills(s, w, p, new List<SM.SpillOffer> { new SM.SpillOffer { LipNearestFirst = new[] { 4 }, AmountDl = 1000, Fluid = 1, From = SM.Source.Rain } });
        int pulses = 0; long soakedReported = 0; var rep = new SM.PulseReport();
        while (s.WetCount > 0 && pulses < 2000) { SM.Pulse(s, w, p, rep); pulses++; soakedReported += rep.Soaked.Sum(x => x.dl); }
        bool ok = s.WetCount == 0 && s.Soaked == 1000 && soakedReported == 1000 && pulses <= 605 && s.LedgerCloses;
        Row("SHEET_SOAKS_IN_COMPLETELY", SHEET, "fixed", ok ? "PASS" : "FAIL", 1, "5 cm on soil at the shipped 2 cm/day: dry after " + pulses + " pulses (expected ~600), Soaked " + s.Soaked + ", reported per cell " + soakedReported + " (irrigation), nothing stranded");
    }

    static void SheetSettingsSweep()
    {
        // shipped slider extremes: cap 5..100 cm, wet squares 500..20000, retention 0.5..5 cm, sweeps 1..6, door 0..50 %
        int[] caps = { 5, 50, 100 }; double[] rets = { 0.5, 1, 5 }; int[] sweeps = { 1, 3, 6 }; int[] doors = { 0, 5, 50 };
        int cases = 0; string bad = null;
        foreach (int cap in caps) foreach (double ret in rets) foreach (int sw in sweeps) foreach (int door in doors)
        {
            if (bad != null) break;
            var p = new SM.Params
            {
                SheetCapDl = Math.Max(SM.DlPerCm, cap * SM.DlPerCm), RetentionDl = Math.Max(1, (int)Math.Round(ret * SM.DlPerCm)),
                SweepsPerPulse = sw, DoorLeakPermille = door * 10, MaxWetCells = 500,
            };
            for (int seed = 1; seed <= 8 && bad == null; seed++)
            {
                var sc = MakeScenario(40000 + seed * 7 + cases, true); sc.P = p;
                cases++;
                string v = RunChecked(sc, sc.Ops, out _);
                if (v != null) bad = "cap " + cap + " cm, retention " + ret + " cm, sweeps " + sw + ", door " + door + "%, seed " + (40000 + seed * 7 + cases - 1) + ": " + v;
            }
        }
        Row("SHEET_SETTINGS_SWEEP_EXTREMES", SHEET, "sweep", bad == null ? "PASS" : "FAIL", cases, bad ?? "81 slider-extreme combinations x 8 random runs: every invariant of SHEET_RANDOM holds, no throw (levelling included)");
    }

    static void SheetAccepts()
    {
        // master switch on: water spills when its inflow switch is on; another liquid only with "other liquids spill"; force overrides
        var errs = new List<string>();
        if (!SM.AcceptsSpill(true, true, true, true, false, false)) errs.Add("water refused");
        if (SM.AcceptsSpill(true, true, true, false, false, false)) errs.Add("other liquid accepted with other-liquids off");
        if (!SM.AcceptsSpill(true, true, true, false, true, false)) errs.Add("other liquid refused with other-liquids on");
        if (SM.AcceptsSpill(false, true, true, true, true, false)) errs.Add("switch off but accepted");
        if (!SM.AcceptsSpill(false, true, true, true, true, true)) errs.Add("forced dev pour refused");
        if (SM.AcceptsSpill(true, false, true, true, true, true)) errs.Add("no depth engine but accepted");
        if (SM.AcceptsSpill(true, true, false, true, true, true)) errs.Add("unknown liquid accepted");
        Row("SHEET_SPILL_SWITCHES", SHEET, "fixed", errs.Count == 0 ? "PASS" : "FAIL", 7, errs.Count == 0 ? "AcceptsSpill truth table matches the settings text (master + per-inflow switch, other liquids, forced dev pour). INFO: the master switch sheetOverflowEnabled ships OFF (RM_SheetSettings.cs:21, 'until the Stage 4 live acceptance validates it')" : string.Join("; ", errs));
    }

    // ───────────────────────────── converters (inv_converters) ─────────────────────────────

    // The cycle as the kernel's own docs describe it: income accrues each rare tick, the budget is capped (CapAccrued), the clipped
    // part (ClippedIncome) is added back after the batch is spent; batches come from the capped budget.
    static int Tick(ref float acc, float perTick, int inU, int outU, int inAvail, int room)
    {
        acc += perTick;
        float capped = RM_ConversionMath.CapAccrued(acc, inU, perTick);
        float clip = RM_ConversionMath.ClippedIncome(acc, capped, perTick);
        int n = RM_ConversionMath.Batches(capped, inU, outU, inAvail, room);
        acc = RM_ConversionMath.AccruedAfterPick(acc, new List<float> { capped }, n > 0 ? 0 : -1) - n * inU + clip;
        return n;
    }

    static void ConvRate()
    {
        float[] perDay = { 1, 5, 10, 40, 100, 500, 2000 }; float[] mult = { 0.1f, 0.5f, 1f, 2f, 5f }; float[] env = { 1f, 0.5f };
        int[] inUnits = { 1, 5, 10, 50, 200 };
        int cases = 0; string bad = null; double worst = 0;
        foreach (float d in perDay) foreach (float m in mult) foreach (float e in env) foreach (int iu in inUnits)
        {
            float per = RM_ConversionMath.BudgetPerRareTick(d, 1f, m, e);
            float acc = 0; long batches = 0; int days = 20;
            for (int t = 0; t < RM_ConversionMath.RareTicksPerDay * days; t++) batches += Tick(ref acc, per, iu, 1, int.MaxValue, -1);
            double income = (double)d * m * e * days;
            double expect = income / iu;
            double cap = per > iu ? per + iu : iu;
            double lost = (income - batches * (double)iu - acc) / iu; // in batches; acc is what is still held
            cases++;
            if (Math.Abs(lost) > 0.01 + income * 1e-5 / iu) { bad = bad ?? ("per day " + d + " x" + m + " env " + e + ", batch " + iu + ": made " + batches + " batches of " + F(expect) + ", " + F(lost) + " batches of income vanished"); }
            worst = Math.Max(worst, Math.Abs(lost));
            if (acc > cap + per + 1e-3) bad = bad ?? ("held budget " + acc + " above cap+tick " + (cap + per));
        }
        Row("CONV_LONG_RUN_RATE_NOTHING_EATEN", CONV, "sweep", bad == null ? "PASS" : "FAIL", cases, (bad ?? "20 days on the shipped multiplier slider 0.1-5, inputs 1-2000/day, batches 1-200: income == batches x input + held budget") + "; worst unaccounted " + F(worst) + " batch. Model: the cycle per the kernel's docs (cap, then add back ClippedIncome after the batch)");
    }

    static void ConvIdle()
    {
        int cases = 0; string bad = null;
        foreach (float d in new float[] { 10, 240, 2400, 24000 }) foreach (int iu in new[] { 1, 10, 100 })
        {
            float per = RM_ConversionMath.BudgetPerRareTick(d, 1f, 1f, 1f);
            float acc = 0;
            for (int t = 0; t < 240 * 7; t++) Tick(ref acc, per, iu, 1, 0, -1); // a dry week
            int burst = Tick(ref acc, per, iu, 1, int.MaxValue, -1);
            double bound = Math.Floor((per + iu) / iu + 1e-6);
            cases++;
            if (burst > Math.Max(1, bound)) bad = "per tick " + per + " batch " + iu + ": first tick after a dry week ran " + burst + " batches, bound " + bound;
        }
        Row("CONV_IDLE_BURST_BOUNDED", CONV, "sweep", bad == null ? "PASS" : "FAIL", cases, bad ?? "after a dry week, the first wet tick runs at most one tick's income plus one batch");
    }

    static void ConvBatches()
    {
        var r = new Random(5); int cases = 20000;
        for (int i = 0; i < cases; i++)
        {
            float acc = (float)(r.NextDouble() * 1000 - 50); int iu = r.Next(-1, 60), ou = r.Next(-1, 60), avail = r.Next(-5, 2000), room = r.Next(-3, 2000);
            int n = RM_ConversionMath.Batches(acc, iu, ou, avail, room);
            string why = null;
            if (n < 0) why = "negative";
            else if (n > 0 && (iu < 1 || ou < 1)) why = "ran with a zero recipe";
            else if (n > 0 && n * iu > avail) why = "ate more input than on hand";
            else if (n > 0 && room >= 0 && n * ou > room) why = "made more output than room";
            else if (n > 0 && n * iu > acc + 1e-3 * iu) why = "spent more budget than accrued";
            else if (iu >= 1 && ou >= 1 && avail >= 0)
            {
                int best = (int)Math.Floor(acc / iu + 1e-4f); best = Math.Min(best, avail / iu); if (room >= 0) best = Math.Min(best, room / ou); best = Math.Max(0, best);
                if (n != best) why = "not the most batches allowed (" + best + ")";
            }
            if (why != null) { Row("CONV_BATCH_BOUNDS_CONSERVE", CONV, "random", "FAIL", i, "seed 5 case " + i + ": Batches(" + acc + "," + iu + "," + ou + "," + avail + "," + room + ")=" + n + ": " + why); return; }
        }
        Row("CONV_BATCH_BOUNDS_CONSERVE", CONV, "random", "PASS", cases, "seed 5: batches never negative, never more input than on hand, output than room or budget than accrued, and the most all three allow");
    }

    static void ConvRotation()
    {
        var r = new Random(11); int cases = 5000;
        for (int i = 0; i < cases; i++)
        {
            int n = r.Next(1, 7);
            var b = Enumerable.Range(0, n).Select(_ => r.Next(3) == 0 ? 0 : r.Next(1, 4)).ToList();
            int last = r.Next(-1, n);
            int pick = RM_ConversionMath.NextRunnable(b, last);
            bool any = b.Any(x => x > 0);
            if (any != (pick >= 0) || (pick >= 0 && b[pick] <= 0)) { Row("CONV_ROTATION_FAIR_NO_STARVING", CONV, "random", "FAIL", i, "seed 11: [" + string.Join(",", b) + "] last " + last + " -> " + pick); return; }
            int first = RM_ConversionMath.FirstRunnable(b);
            if (any != (first >= 0) || (first >= 0 && (b[first] <= 0 || b.Take(first).Any(x => x > 0)))) { Row("CONV_ROTATION_FAIR_NO_STARVING", CONV, "random", "FAIL", i, "FirstRunnable [" + string.Join(",", b) + "] -> " + first); return; }
            // fairness: rotating from 'last' visits every runnable input within n calls
            var seen = new HashSet<int>(); int l = last;
            for (int k = 0; k < n; k++) { l = RM_ConversionMath.NextRunnable(b, l); if (l >= 0) seen.Add(l); }
            if (seen.Count != b.Count(x => x > 0)) { Row("CONV_ROTATION_FAIR_NO_STARVING", CONV, "random", "FAIL", i, "rotation [" + string.Join(",", b) + "] from " + last + " saw only " + string.Join(",", seen)); return; }
        }
        Row("CONV_ROTATION_FAIR_NO_STARVING", CONV, "random", "PASS", cases, "seed 11: the pick is always runnable (or -1 when none is); rotation visits every runnable input within n cycles");
    }

    static void ConvBlocked()
    {
        // two recipes share one budget: small (5/batch) has no input; big (50/batch) has input. Income 10 a tick.
        float acc = 0; int bigRuns = 0;
        for (int t = 0; t < 100; t++)
        {
            acc += 10f;
            float cSmall = RM_ConversionMath.CapAccrued(acc, 5, 10f), cBig = RM_ConversionMath.CapAccrued(acc, 50, 10f);
            int nSmall = RM_ConversionMath.Batches(cSmall, 5, 1, 0, -1), nBig = RM_ConversionMath.Batches(cBig, 50, 1, 1000, -1);
            int pick = RM_ConversionMath.FirstRunnable(new List<int> { nSmall, nBig });
            float clip = RM_ConversionMath.ClippedIncome(acc, pick == 1 ? cBig : pick == 0 ? cSmall : Math.Max(cSmall, cBig), 10f);
            acc = RM_ConversionMath.AccruedAfterPick(acc, new List<float> { cSmall, cBig }, pick);
            if (pick == 1) { acc -= 50 * nBig; bigRuns += nBig; }
            acc += clip;
        }
        // 100 ticks x 10 = 1000 income = 20 big batches
        bool ok = bigRuns >= 19;
        Row("CONV_BLOCKED_SMALL_RECIPE_NEVER_STARVES_BIG", CONV, "fixed", ok ? "PASS" : "FAIL", 1, "a blocked 5-unit recipe beside a fed 50-unit one, 10 a tick for 100 ticks: big ran " + bigRuns + " batches (expected about 20)");
    }

    static void ConvBudget()
    {
        int cases = 0; var errs = new List<string>();
        foreach (float a in new[] { -1f, 0f, 10f }) foreach (float b in new[] { -1f, 0f, 1f }) foreach (float c in new[] { -1f, 0f, 1f }) foreach (float d in new[] { -1f, 0f, 1f })
        {
            cases++;
            float v = RM_ConversionMath.BudgetPerRareTick(a, b, c, d);
            bool pos = a > 0 && b > 0 && c > 0 && d > 0;
            if (pos ? Math.Abs(v - a / 240f) > 1e-5 : v != 0f) errs.Add(a + "," + b + "," + c + "," + d + " -> " + v);
        }
        for (float m = 0.1f; m <= 5.0001f; m += 0.1f) { cases++; if (Math.Abs(RM_ConversionMath.BudgetPerRareTick(240, 1, m, 1) - m) > 1e-4) errs.Add("mult " + m); }
        if (RM_ConversionMath.SunFactor(0.5f, false) != 1f || RM_ConversionMath.SunFactor(0.49f, false) != 0f || RM_ConversionMath.SunFactor(1f, true) != 0f) errs.Add("solar still daylight rule");
        Row("CONV_BUDGET_ZERO_AND_LINEAR", CONV, "sweep", errs.Count == 0 ? "PASS" : "FAIL", cases + 3, errs.Count == 0 ? "any non-positive factor gives no budget; budget is linear in the multiplier over the shipped slider 0.1-5; solar still runs only unroofed at glow >= 0.5" : string.Join("; ", errs.Take(5)));
    }

    // ───────────────────────────── drilling (inv_drilling) ─────────────────────────────

    static void DrillPlacement()
    {
        var errs = new List<string>();
        void Eq(RM_DrillSurveyMath.Verdict g, RM_DrillSurveyMath.Verdict w, string what) { if (g != w) errs.Add(what + " " + g); }
        Eq(RM_DrillSurveyMath.Placement(false, false, 0f), RM_DrillSurveyMath.Verdict.Allowed, "unsurveyed");
        Eq(RM_DrillSurveyMath.Placement(true, false, 100f), RM_DrillSurveyMath.Verdict.NoYield, "surveyed empty");
        Eq(RM_DrillSurveyMath.Placement(true, true, 0f), RM_DrillSurveyMath.Verdict.Spent, "drawn to zero");
        Eq(RM_DrillSurveyMath.Placement(true, true, -1f), RM_DrillSurveyMath.Verdict.Spent, "overdrawn");
        Eq(RM_DrillSurveyMath.Placement(true, true, 0.01f), RM_DrillSurveyMath.Verdict.Allowed, "a little left");
        Row("DRILL_PLACEMENT_TABLE", DRILL, "fixed", errs.Count == 0 ? "PASS" : "FAIL", 5, errs.Count == 0 ? "a drill is refused only on a surveyed map with no liquid or a spent reserve (the right maps)" : string.Join("; ", errs));
    }

    static RM_DrillSurveyMath.State StateOf(int bits, float reserve)
    {
        return new RM_DrillSurveyMath.State
        {
            settingOn = (bits & 1) != 0, switchedOn = (bits & 2) != 0, needsPower = (bits & 4) != 0, powered = (bits & 8) != 0,
            surveyed = (bits & 16) != 0, hasYield = (bits & 32) != 0, hasCanalForm = (bits & 64) != 0, fluidAllowed = (bits & 128) != 0,
            outletDug = (bits & 256) != 0, outletOtherLiquid = (bits & 512) != 0, outletBrimming = (bits & 1024) != 0, reserve = reserve,
        };
    }

    static bool Fails(RM_DrillSurveyMath.State s, RM_DrillSurveyMath.Block b)
    {
        switch (b)
        {
            case RM_DrillSurveyMath.Block.DisabledInSettings: return !s.settingOn;
            case RM_DrillSurveyMath.Block.SwitchedOff: return !s.switchedOn;
            case RM_DrillSurveyMath.Block.Unpowered: return s.needsPower && !s.powered;
            case RM_DrillSurveyMath.Block.NoSubsurface: return s.surveyed && !s.hasYield;
            case RM_DrillSurveyMath.Block.Unsurveyed: return !s.surveyed;
            case RM_DrillSurveyMath.Block.ReserveSpent: return s.reserve <= 0f;
            case RM_DrillSurveyMath.Block.NoCanalForm: return !s.hasCanalForm;
            case RM_DrillSurveyMath.Block.LiquidDisabledInSettings: return !s.fluidAllowed;
            case RM_DrillSurveyMath.Block.OutletNotDug: return !s.outletDug;
            case RM_DrillSurveyMath.Block.OutletOtherLiquid: return s.outletOtherLiquid;
            case RM_DrillSurveyMath.Block.OutletBrimming: return s.outletBrimming;
        }
        return false;
    }

    static void DrillWhyNot()
    {
        int cases = 0; var errs = new List<string>();
        foreach (float res in new[] { -1f, 0f, 5f })
            for (int bits = 0; bits < 2048; bits++)
            {
                var s = StateOf(bits, res); cases++;
                var b = RM_DrillSurveyMath.WhyNot(s);
                bool anyFail = Enum.GetValues(typeof(RM_DrillSurveyMath.Block)).Cast<RM_DrillSurveyMath.Block>().Any(x => x != RM_DrillSurveyMath.Block.None && Fails(s, x));
                if (b == RM_DrillSurveyMath.Block.None && anyFail) errs.Add("bits " + bits + " res " + res + ": None although a condition fails");
                if (b != RM_DrillSurveyMath.Block.None && !Fails(s, b)) errs.Add("bits " + bits + " res " + res + ": " + b + " though it holds");
                if (!s.settingOn && b != RM_DrillSurveyMath.Block.DisabledInSettings) errs.Add("bits " + bits + ": setting off but " + b);
                if (errs.Count > 3) break;
            }
        Row("DRILL_WHYNOT_SOUND_AND_COMPLETE", DRILL, "fixed", errs.Count == 0 ? "PASS" : "FAIL", cases, errs.Count == 0 ? "all 2048 x 3 states: None exactly when every condition holds, each reason named is a condition that really fails, the master switch always wins" : string.Join("; ", errs.Take(4)));
    }

    static void DrillAgree()
    {
        int cases = 0; var errs = new List<string>();
        foreach (bool sv in new[] { false, true }) foreach (bool y in new[] { false, true }) foreach (float res in new[] { 0f, 5f })
        {
            cases++;
            var pv = RM_DrillSurveyMath.Placement(sv, y, res);
            var s = StateOf(1 | 2 | 64 | 128 | 256, res); s.surveyed = sv; s.hasYield = y;
            var why = RM_DrillSurveyMath.WhyNot(s);
            if (pv == RM_DrillSurveyMath.Verdict.NoYield && why != RM_DrillSurveyMath.Block.NoSubsurface) errs.Add("placement NoYield but tick says " + why);
            if (pv == RM_DrillSurveyMath.Verdict.Spent && why != RM_DrillSurveyMath.Block.ReserveSpent) errs.Add("placement Spent but tick says " + why);
            if (pv == RM_DrillSurveyMath.Verdict.Allowed && sv && why != RM_DrillSurveyMath.Block.None) errs.Add("placement Allowed on a surveyed map but tick says " + why);
        }
        Row("DRILL_PLACEMENT_AGREES_WITH_WHYNOT", DRILL, "fixed", errs.Count == 0 ? "PASS" : "FAIL", cases, errs.Count == 0 ? "with everything else ready, the placement verdict and the tick's reason agree (NoYield/NoSubsurface, Spent/ReserveSpent). INFO: an unsurveyed map allows placement but the tick blocks it as Unsurveyed until surveyed" : string.Join("; ", errs));
    }

    static void DrillSpent()
    {
        var r = new Random(17); int cases = 3000; double landedLevels = 0, charged = 0;
        for (int i = 0; i < cases; i++)
        {
            long before = r.Next(0, 100000), after = before + r.Next(-500, 3000); long per = r.Next(1, 4) == 1 ? 1000 : 200; float upl = (float)(r.NextDouble() * 20);
            float sp = RM_DrillSurveyMath.SpentUnits(before, after, per, upl);
            if (sp < 0 || (after <= before && sp != 0)) { Row("DRILL_SPENT_UNITS_CONSERVE", DRILL, "random", "FAIL", i, "seed 17: SpentUnits(" + before + "," + after + "," + per + "," + upl + ")=" + sp); return; }
            if (after > before) { double exp = (after - before) / (double)per * upl; if (Math.Abs(sp - exp) > 1e-3 * Math.Max(1, exp)) { Row("DRILL_SPENT_UNITS_CONSERVE", DRILL, "random", "FAIL", i, "charged " + sp + " for landed " + exp); return; } landedLevels += exp; charged += sp; }
        }
        if (RM_DrillSurveyMath.SpentUnits(0, 100, 0, 5f) != 0f) { Row("DRILL_SPENT_UNITS_CONSERVE", DRILL, "random", "FAIL", 1, "dlPerLevel 0 charged"); return; }
        Row("DRILL_SPENT_UNITS_CONSERVE", DRILL, "random", "PASS", cases, "seed 17: the reserve is charged exactly the decilitres that landed, never negative, nothing for a write that landed nothing; total charged " + F(charged) + " of landed " + F(landedLevels));
    }

    // ───────────────────────────── sprinklers (inv_sprinklers) ─────────────────────────────

    static void SprkDecide()
    {
        int cases = 0; var errs = new List<string>();
        for (int bits = 0; bits < 32; bits++) foreach (int cells in new[] { 0, 5 }) foreach (int need in new[] { 0, 3 }) foreach (int avail in new[] { 0, 2, 3, 100 })
        {
            bool en = (bits & 1) != 0, sw = (bits & 2) != 0, pr = (bits & 4) != 0, liq = (bits & 8) != 0, thick = (bits & 16) != 0;
            var st = RM_SprinklerKernel.Decide(en, sw, pr, liq, thick, cells, need, avail); cases++;
            bool spray = en && sw && pr && liq && !thick && cells > 0 && need > 0 && avail >= need;
            if ((st == RM_SprinklerState.Spraying) != spray) errs.Add(bits + "/" + cells + "/" + need + "/" + avail + " -> " + st);
            if (!pr && st == RM_SprinklerState.Spraying) errs.Add("sprays with no pump");
            if (spray == false && en && sw && pr && liq && !thick && cells > 0 && need > 0 && st != RM_SprinklerState.Dry) errs.Add("short of the pulse but " + st);
            if (!en && st != RM_SprinklerState.Disabled) errs.Add("disabled reads " + st);
        }
        Row("SPRK_DECIDE_NEEDS_PUMP_ALL_OR_NOTHING", SPRK, "fixed", errs.Count == 0 ? "PASS" : "FAIL", cases, errs.Count == 0 ? "sprays only with the setting, switch, a pump's pressure, a thin liquid, cells and the whole pulse on hand; a short net reads Dry (all or nothing)" : string.Join("; ", errs.Take(4)));
    }

    static void SprkUnits()
    {
        int cases = 0; var errs = new List<string>();
        for (int step = 2; step <= 100; step++)   // the slider: 0.1-5 L in 0.05 steps
        {
            float L = (float)Math.Round(step * 0.05f * 20f) / 20f;
            int prev = 0;
            for (int cells = 1; cells <= 60; cells++)
            {
                cases++;
                int u = RM_SprinklerKernel.UnitsFor(cells, L, 10);
                if (u <= 0) errs.Add("free pulse at " + L + " L x " + cells);
                if (u < prev) errs.Add("cost fell " + L + " L at " + cells);
                if (u + 1e-6 < cells * L * 10 - 1e-3) errs.Add("undercharged " + L + " x " + cells + ": " + u);
                if (u > Math.Ceiling(cells * L * 10 - 1e-6) + 0) errs.Add("overcharged " + L + " x " + cells + ": " + u + " for " + (cells * L * 10));
                prev = u;
            }
            for (int units = 0; units <= 400; units += 3)
            {
                cases++;
                int m = RM_SprinklerKernel.MaxCellsFor(units, L, 10);
                if (m > 0 && RM_SprinklerKernel.UnitsFor(m, L, 10) > units) errs.Add("MaxCellsFor over budget " + L + "/" + units);
                if (RM_SprinklerKernel.UnitsFor(m + 1, L, 10) <= units) errs.Add("MaxCellsFor not max " + L + "/" + units + " -> " + m);
            }
            if (errs.Count > 4) break;
        }
        Row("SPRK_UNITS_NEVER_FREE_SLIDER_SWEEP", SPRK, "sweep", errs.Count == 0 ? "PASS" : "FAIL", cases, errs.Count == 0 ? "over the shipped 0.1-5 L slider (0.05 steps), 10 units a litre: a pulse is never free, never under- or over-charged by a unit, monotone in cells; MaxCellsFor is the exact inverse" : string.Join("; ", errs.Take(4)));
    }

    static void SprkValve()
    {
        var r = new Random(23); int cases = 4000;
        for (int i = 0; i < cases; i++)
        {
            int n = r.Next(0, 30);
            var cells = Enumerable.Range(0, n).Select(k => new RM_ValveCell(r.Next(0, 1000), (float)Math.Round(r.NextDouble() * 3, 1), r.Next(4) > 0, r.Next(6) == 0, r.Next(5) == 0, r.Next(5) > 0, r.Next(8) == 0)).ToList();
            float L = r.Next(2, 101) * 0.05f; int budget = r.Next(-1, 200), net = r.Next(0, 500), reserve = r.Next(0, 300);
            var kept = RM_SprinklerKernel.Valve(cells, L, 10, budget, net, reserve, out bool trimmed);
            var want = cells.Where(RM_SprinklerKernel.ValveWants).OrderBy(c => c.Dist).ThenBy(c => c.Index).Select(c => c.Index).ToList();
            int cost = RM_SprinklerKernel.UnitsFor(kept.Count, L, 10);
            string why = null;
            if (!kept.SequenceEqual(want.Take(kept.Count))) why = "not the nearest wanted cells in order";
            else if (budget >= 0 && kept.Count > 0 && cost > budget) why = "over the day's budget";
            else if (reserve > 0 && kept.Count > 0 && net - cost < reserve) why = "below the reserve floor";
            else if (trimmed != (kept.Count < want.Count)) why = "trimmed flag wrong";
            else if (kept.Count < want.Count)
            {
                int c2 = RM_SprinklerKernel.UnitsFor(kept.Count + 1, L, 10);
                if ((budget < 0 || c2 <= budget) && (reserve <= 0 || net - c2 >= reserve)) why = "trimmed a cell it could pay for";
            }
            foreach (var c in cells) if (kept.Contains(c.Index) && !RM_SprinklerKernel.ValveWants(c) && !cells.Any(o => o.Index == c.Index && RM_SprinklerKernel.ValveWants(o))) why = why ?? "watered a cell that does not need it";
            if (why != null) { Row("SPRK_VALVE_BUDGET_RESERVE_NEAREST", SPRK, "random", "FAIL", i, "seed 23 case " + i + ": " + why + " (L " + L + " budget " + budget + " net " + net + " reserve " + reserve + ")"); return; }
        }
        // the native head charges every unsealed cell
        var nat = RM_SprinklerKernel.NativeCharge(new List<RM_ValveCell> { new RM_ValveCell(1, 0, false, false, false, false, false), new RM_ValveCell(2, 1, true, true, false, true, false) });
        bool natOk = nat.Count == 1 && nat[0] == 1;
        Row("SPRK_VALVE_BUDGET_RESERVE_NEAREST", SPRK, natOk ? "random" : "random", natOk ? "PASS" : "FAIL", cases + 1, natOk ? "seed 23: the valve waters only lit unsealed dry non-exempt plants, nearest first, the most the day's budget and the reserve floor allow, trimmed flag exact; native head charges every unsealed square" : "NativeCharge kept " + string.Join(",", nat));
    }

    static void SprkPick()
    {
        var r = new Random(29); int cases = 3000;
        string[] keys = { "Water", "Chemfuel", "Acid", "Brine", null };
        for (int i = 0; i < cases; i++)
        {
            var held = Enumerable.Range(0, r.Next(0, 8)).Select(_ => new KeyValuePair<string, int>(keys[r.Next(keys.Length)], r.Next(-5, 50))).ToList();
            var sums = held.Where(kv => kv.Key != null && kv.Value > 0).GroupBy(kv => kv.Key).ToDictionary(g => g.Key, g => g.Sum(kv => kv.Value));
            string want = sums.Count == 0 ? null : sums.OrderByDescending(kv => kv.Value).ThenBy(kv => kv.Key, StringComparer.Ordinal).First().Key;
            string a = RM_SprinklerKernel.PickLiquid(held), b = RM_SprinklerKernel.PickLiquid(held.OrderBy(_ => r.Next()).ToList());
            if (a != want || b != want) { Row("SPRK_PICK_LIQUID_ARGMAX_ORDER_FREE", SPRK, "random", "FAIL", i, "seed 29: held [" + string.Join(",", held.Select(kv => kv.Key + ":" + kv.Value)) + "] -> " + a + " / permuted " + b + ", want " + want); return; }
        }
        Row("SPRK_PICK_LIQUID_ARGMAX_ORDER_FREE", SPRK, "random", "PASS", cases, "seed 29: sprays the liquid the net holds most of, ties by ordinal key, null when empty, independent of the order the net lists them");
    }

    static void SprkGrid()
    {
        var g = new RM_SprinkledGrid(10); var errs = new List<string>();
        int now = 1000; int until = RM_SprinklerKernel.WetUntil(now);
        g.Wet(3, "Water", until, 7);
        if (until != now + 2750) errs.Add("wet until " + until);
        if (g.WetBy(3, now + 2749) != "Water") errs.Add("dried before the next pulse + grace");
        if (g.WetBy(3, now + 2750) != null) errs.Add("still wet after the grace");
        if (!g.WetByOther(3, 8, now) || g.WetByOther(3, 7, now)) errs.Add("other-head test");
        if (!g.Spend(3, now) || g.WetBy(3, now) != null || g.Spend(3, now)) errs.Add("spend");
        g.Wet(-1, "Water", until, 1); g.Wet(10, "Water", until, 1);
        if (g.LiveCells(now) != 0) errs.Add("live cells " + g.LiveCells(now));
        Row("SPRK_WET_GRID_LIFETIME", SPRK, "fixed", errs.Count == 0 ? "PASS" : "FAIL", 7, errs.Count == 0 ? "a paid pulse wets until the next hourly pulse plus 250 ticks of grace; a fruiting crop spends it; off-grid writes ignored" : string.Join("; ", errs));
    }

    static void SprkRadius()
    {
        var counts = new List<string>();
        foreach (float rad in new[] { 1.9f, 2.9f, 3.9f })
        {
            int n = 0; int R = (int)Math.Ceiling(rad);
            for (int x = -R; x <= R; x++) for (int z = -R; z <= R; z++) if (x * x + z * z <= rad * rad) n++;
            counts.Add(rad + ": " + n);
        }
        Row("SPRK_RADIUS_CHOICES_CELLS", SPRK, "info", "INFO", 3, "squares within the radius choices (distance <= r, GenRadial's rule): " + string.Join(", ", counts) + "; the settings label says 2.9 is about 25");
    }

    // ───────────────────────────── thirst (inv_bottles_thirst) ─────────────────────────────

    static int IntervalsToEmpty(float start, float fallPerDay)
    {
        float lvl = start; int k = 0;
        float step = RM_ThirstMath.FallPerInterval(fallPerDay);
        while (lvl > 0f && k < 1000000) { lvl -= step; k++; }
        return k;
    }

    static void ThirstRuled()
    {
        var errs = new List<string>();
        float perDayIntervals = RM_ThirstMath.TicksPerDay / RM_ThirstMath.NeedIntervalTicks; // 400
        int k = IntervalsToEmpty(1f, RM_ThirstMath.FallPerDay(1f, 1f, false, false));
        if (Math.Abs(k / perDayIntervals - 1.25) > 0.01) errs.Add("empties in " + k / perDayIntervals + " days, ruled 1.25");
        float hot = RM_ThirstMath.HeatFactor(80f, 26f, true);
        if (hot != 3f) errs.Add("heat factor at +54 C over comfort " + hot);
        if (RM_ThirstMath.HeatFactor(36f, 26f, true) != 1.5f) errs.Add("heat at +10 C " + RM_ThirstMath.HeatFactor(36f, 26f, true));
        if (RM_ThirstMath.HeatFactor(80f, 26f, false) != 1f) errs.Add("heat scaling off still scales");
        int kh = IntervalsToEmpty(1f, RM_ThirstMath.FallPerDay(1f, hot, false, false));
        if (Math.Abs(kh / perDayIntervals - 1.25 / 3) > 0.01) errs.Add("hot empties in " + kh / perDayIntervals);
        if (Math.Abs(RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Potable, true) - 0.5f) > 1e-6) errs.Add("1.5 L bottle restores " + RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Potable, true));
        if (Math.Abs(RM_ThirstMath.Hydration(RM_ThirstMath.TerrainDrinkLitres, RM_WaterQuality.Potable, true) - 0.5f) > 1e-6) errs.Add("terrain drink != bottle");
        if (RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Toxic, false) != 0.5f) errs.Add("quality effects off still reduce");
        if (!(RM_ThirstMath.HydrateFactor(RM_WaterQuality.Distilled, true) >= RM_ThirstMath.HydrateFactor(RM_WaterQuality.Potable, true)
              && RM_ThirstMath.HydrateFactor(RM_WaterQuality.Potable, true) > RM_ThirstMath.HydrateFactor(RM_WaterQuality.Fouled, true)
              && RM_ThirstMath.HydrateFactor(RM_WaterQuality.Fouled, true) > RM_ThirstMath.HydrateFactor(RM_WaterQuality.Toxic, true))) errs.Add("quality order");
        if (Math.Abs(RM_ThirstMath.FallPerDay(1f, 1f, true, true) - 0.8f * 1.3f * 0.5f) > 1e-6) errs.Add("labour/asleep");
        if (RM_ThirstMath.Effective(RM_WaterQuality.Toxic, false) != RM_WaterQuality.Potable) errs.Add("effective quality with effects off");
        Row("THIRST_RULED_NUMBERS", THIRST, "fixed", errs.Count == 0 ? "PASS" : "FAIL", 11, errs.Count == 0 ? "full to empty in 1.25 days at 1x (500 need intervals), 3x cap in heat (0.42 days), 1.5 L bottle and a terrain drink restore 0.5, labour 1.3x, asleep 0.5x, quality factors ordered and off when quality effects are off" : string.Join("; ", errs));
    }

    static void ThirstRateSweep()
    {
        int cases = 0; string bad = null;
        for (float m = 0.25f; m <= 3.0001f; m += 0.05f)
        {
            cases++;
            int k = IntervalsToEmpty(1f, RM_ThirstMath.FallPerDay(m, 1f, false, false));
            double days = k / 400.0, want = 1.25 / m;
            if (Math.Abs(days - want) > 1.0 / 400 + 1e-6) bad = "x" + m + ": empty in " + days + " days, want " + want;
            if (!(RM_ThirstMath.DaysOfWater(30f, 1, m) > 0)) bad = "days of water at x" + m;
        }
        Row("THIRST_RATE_SLIDER_SWEEP", THIRST, "sweep", bad == null ? "PASS" : "FAIL", cases, bad ?? "rate slider 0.25-3: time to empty is 1.25 days / rate to one need interval");
    }

    static void ThirstDehydration()
    {
        float sev = 0f; int k = 0;
        while (sev < RM_ThirstMath.DehydrationLethal && k < 100000) { sev += RM_ThirstMath.DehydrationDelta(0f, RM_ThirstMath.NeedIntervalTicks); k++; }
        double daysToDeath = k / 400.0;
        float heal = 0.5f; int h = 0;
        while (heal > 0f && h < 100000) { heal += RM_ThirstMath.DehydrationDelta(0.5f, RM_ThirstMath.NeedIntervalTicks); h++; }
        bool still = RM_ThirstMath.DehydrationDelta(0.2f, 150f) == 0f;
        bool orphan = RM_ThirstMath.OrphanDehydrationDelta(false, 60000f) < 0f && RM_ThirstMath.OrphanDehydrationDelta(true, 60000f) == 0f;
        bool ok = daysToDeath > 3.0 && daysToDeath < 3.5 && Math.Abs(h / 400.0 - 0.5 / 0.6) < 0.01 && still && orphan;
        Row("THIRST_DEHYDRATION_TIMELINE", THIRST, "fixed", ok ? "PASS" : "FAIL", 4, "lethal " + F(daysToDeath) + " days after empty (ruled 'about 3 days'), 0.5 severity heals in " + F(h / 400.0) + " days above 30%, holds between empty and 30%: " + still + ", dehydration with thirst switched off heals: " + orphan);
    }

    static void ThirstMayDrink()
    {
        int cases = 0; var errs = new List<string>();
        foreach (RM_DrinkUse use in Enum.GetValues(typeof(RM_DrinkUse))) foreach (float lvl in new[] { 0f, 0.004f, 0.2f, 0.9f })
        foreach (bool hum in new[] { false, true }) foreach (bool nat in new[] { false, true }) foreach (bool brk in new[] { false, true }) foreach (bool lr in new[] { false, true })
        {
            cases++;
            bool got = RM_ThirstMath.MayDrink(use, lvl, hum, nat, brk, lr);
            bool want;
            if (use == RM_DrinkUse.Potable) want = true;
            else if (use == RM_DrinkUse.Never) want = false;
            else if (!hum) want = nat;
            else if (use == RM_DrinkUse.LastResort) want = lr && lvl <= 0.005f;
            else want = brk;
            if (got != want) errs.Add(use + " lvl " + lvl + " hum " + hum + " native " + nat + " break " + brk + " lastResortOn " + lr + " -> " + got);
        }
        bool salt = RM_ThirstMath.SaltBreakCan(0.05f, false, false, true) && !RM_ThirstMath.SaltBreakCan(0.2f, false, false, true) && !RM_ThirstMath.SaltBreakCan(0.05f, true, false, true) && !RM_ThirstMath.SaltBreakCan(0.05f, false, true, true) && !RM_ThirstMath.SaltBreakCan(0.05f, false, false, false);
        if (!salt) errs.Add("salt break gate");
        Row("THIRST_MAY_DRINK_MATRIX", THIRST, "fixed", errs.Count == 0 ? "PASS" : "FAIL", cases + 5, errs.Count == 0 ? "potable always, never-class never, last resort only when empty and allowed, salt only in the break (parched, nothing potable in reach), animals any native water" : string.Join("; ", errs.Take(4)));
    }

    static void ThirstOrder()
    {
        var r = new Random(31); int cases = 20000;
        var uses = (RM_DrinkUse[])Enum.GetValues(typeof(RM_DrinkUse)); var qs = (RM_WaterQuality[])Enum.GetValues(typeof(RM_WaterQuality));
        (RM_DrinkUse, bool, RM_WaterQuality, float) Gen() => (uses[r.Next(uses.Length)], r.Next(2) == 0, qs[r.Next(qs.Length)], r.Next(0, 4));
        bool B((RM_DrinkUse u, bool a, RM_WaterQuality q, float d) x, (RM_DrinkUse u, bool a, RM_WaterQuality q, float d) y) => RM_ThirstMath.BetterPick(x.u, x.a, x.q, x.d, y.u, y.a, y.q, y.d);
        for (int i = 0; i < cases; i++)
        {
            var a = Gen(); var b = Gen(); var c = Gen();
            if (B(a, a)) { Row("THIRST_PICK_ORDER_IS_STRICT", THIRST, "random", "FAIL", i, "irreflexive fails for " + a); return; }
            if (B(a, b) && B(b, a)) { Row("THIRST_PICK_ORDER_IS_STRICT", THIRST, "random", "FAIL", i, "both better: " + a + " " + b); return; }
            if (B(a, b) && B(b, c) && !B(a, c)) { Row("THIRST_PICK_ORDER_IS_STRICT", THIRST, "random", "FAIL", i, "not transitive " + a + " " + b + " " + c); return; }
            if (a.Item1 == RM_DrinkUse.Potable && b.Item1 != RM_DrinkUse.Potable && !B(a, b)) { Row("THIRST_PICK_ORDER_IS_STRICT", THIRST, "random", "FAIL", i, "a potable source lost to " + b); return; }
            if (a.Item1 == b.Item1 && !a.Item2 && b.Item2 && !B(a, b)) { Row("THIRST_PICK_ORDER_IS_STRICT", THIRST, "random", "FAIL", i, "a tap lost to an awkward scoop " + a + " " + b); return; }
        }
        bool awk = !RM_ThirstMath.Awkward(RM_DrinkSource.Terrain, false) && RM_ThirstMath.Awkward(RM_DrinkSource.Caravan, true) && RM_ThirstMath.Awkward(RM_DrinkSource.Container, true)
                   && !RM_ThirstMath.Awkward(RM_DrinkSource.Bottle, true) && RM_ThirstMath.Awkward(RM_DrinkSource.Bottle, false) && !RM_ThirstMath.Awkward(RM_DrinkSource.Tank, true);
        Row("THIRST_PICK_ORDER_IS_STRICT", THIRST, "random", awk ? "PASS" : "FAIL", cases + 6, awk ? "seed 31: the drink pick is a strict order (irreflexive, asymmetric, transitive), potable beats any lesser class, a tap beats an awkward scoop; awkwardness follows the owner's Q1 rule" : "Awkward() table wrong");
    }

    static void ThirstSpendable()
    {
        int cases = 0; string bad = null;
        for (int res = 0; res <= 20000; res += 500) // the reserve slider 0-2000 L in 50 L steps, 10 units a litre
            for (int avail = 0; avail <= 30000; avail += 1500)
                foreach (bool pot in new[] { false, true })
                {
                    cases++;
                    int s = RM_ThirstMath.Spendable(avail, res, pot);
                    int want = !pot || res <= 0 ? avail : Math.Max(0, avail - res);
                    if (s != want || s < 0 || s > avail) bad = "Spendable(" + avail + "," + res + "," + pot + ")=" + s;
                }
        bool def = RM_ThirstMath.BottleDeficit(3, 0, 0) == 3 && RM_ThirstMath.BottleDeficit(3, 4, 20) == 0 && RM_ThirstMath.BottleDeficit(3, 4, 5) == 7;
        if (!def) bad = bad ?? "bottle deficit";
        Row("THIRST_SPENDABLE_RESERVE_SWEEP", THIRST, "sweep", bad == null ? "PASS" : "FAIL", cases + 3, bad ?? "drinking reserve slider 0-2000 L: a potable net keeps the reserve back from sprinklers and machines, never negative, other liquids have none; bottles-per-colonist deficit");
    }

    static void ThirstDays()
    {
        int cases = 0; string bad = null;
        foreach (float L in new[] { 1.5f, 15f, 300f }) foreach (int dr in new[] { 1, 3, 10 }) foreach (float m in new[] { 0.25f, 1f, 3f })
        {
            cases++;
            float days = RM_ThirstMath.DaysOfWater(L, dr, m);
            // the stock restores L/3 of a full need; drinkers lose 0.8*m a day each
            double want = L / 3.0 / (0.8 * m * dr);
            if (Math.Abs(days - want) > 1e-4 * want) bad = L + " L " + dr + " drinkers x" + m + ": " + days + " want " + want;
        }
        if (!float.IsPositiveInfinity(RM_ThirstMath.DaysOfWater(10f, 0, 1f))) bad = bad ?? "no drinkers is not infinite";
        Row("THIRST_DAYS_OF_WATER_AGREES_WITH_FALL", THIRST, "sweep", bad == null ? "PASS" : "FAIL", cases + 1, bad ?? "the days-of-water readout equals the stock's hydration over the drinkers' fall rate");
    }

    static void ThirstCategory()
    {
        int cases = 0; string bad = null;
        for (int i = -10; i <= 1010; i++)
        {
            float lvl = i / 1000f; cases++;
            int cat = RM_ThirstMath.Category(lvl);
            if (cat == 3 && !RM_ThirstMath.Desperate(lvl)) bad = "dehydrated but not desperate at " + lvl;
            if (cat == 0 && lvl < 0.3f) bad = "fine at " + lvl;
            if (cat == 2 && !(lvl < 0.1f)) bad = "parched at " + lvl;
            if (RM_ThirstMath.SaltBreakCan(lvl, false, false, true) && cat < 2) bad = "salt break while only thirsty at " + lvl;
        }
        Row("THIRST_CATEGORY_DESPERATE_CONSISTENT", THIRST, "sweep", bad == null ? "PASS" : "FAIL", cases, bad ?? "categories fine/thirsty/parched/dehydrated at 0.3/0.1/0; a dehydrated pawn is desperate; the salt break only for a parched pawn");
    }
}
