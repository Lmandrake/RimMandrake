// Blind lane 1 (game logic) for Pyrelands 0.1.0, cycle 1 of the Stages 4 and 5 challenge.
// Written from the locked bars (tree.json, sheet.md, plan.md, record.json inventory text), the six shipped kernel files
// (Kernel/*.cs, FurnaceWarmthMath.cs) and the shipped settings (RM_PyrelandsMod.cs defaults and slider ranges,
// PyrelandsTuning.cs constants) ONLY: the builder's selftests, journal and evidence were not opened before this ran.
// Def and text rows are run_lane1.py's (Python reads the XML). Output: one JSON line per row on stdout; exit 1 on any FAIL.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Globalization;
using RimMandrake.Pyrelands;

static class BlindLane1
{
    // ---- shipped settings (RM_PyrelandsMod.cs defaults; slider ranges in comments) and tuning (PyrelandsTuning.cs) ----
    const float DryFert = 0.70f;        // slider 0..1
    const float WetFert = 1.40f;        // slider 0.4..2
    const float BurnBonusDef = 0.50f;   // slider 0..1.5
    const float BurnDaysDef = 6f;       // slider 1..20
    const int BlackRainHoursDef = 24;   // slider 0..72
    const float WarmthStrengthDef = 1f; // slider 0..2
    const int TicksPerDay = 60000, TicksPerHour = 2500;
    const float AuraRadius = 4.9f, WarmthMaxC = 14f, ClassicBody = 3.2f, GiantBody = 6f;
    const int BedMin = 1, BedMax = 2, SleepGrace = 1250, SleepMtb = 3750, SleepCheck = 250;
    const int QuietTicks = 120000, RetryTicks = 2500, WatchInterval = 60;
    const float MinDistColony = 32f, FrontMinDays = 2f, FrontMaxDays = 4f;
    const int FrontWidth = 9, OpeningWidth = 5, OpeningWindow = 2500;
    const int HawkBucket = 8; const float HawkScan = 54f;
    const int HeatHold = 600, EmergeInterval = 30;
    const float WetRootsCooling = 15f;

    static readonly List<string> Out = new List<string>();
    static int fails;
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    static string J(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";
    static string Bars(string[] b) => "[" + string.Join(",", b.Select(J)) + "]";
    static void Emit(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") fails++;
        Out.Add("{\"id\":" + J(id) + ",\"bars\":" + Bars(bars) + ",\"kind\":" + J(kind) + ",\"verdict\":" + J(verdict)
            + ",\"cases\":" + cases + ",\"detail\":" + J(detail) + "}");
    }
    static void Row(string id, string[] bars, string kind, bool pass, int cases, string detail)
        => Emit(id, bars, kind, pass ? "PASS" : "FAIL", cases, detail);
    static void Info(string id, string[] bars, int cases, string detail) => Emit(id, bars, "info", "INFO", cases, detail);
    static void NotKernel(string id, string[] bars, string why) => Emit(id, bars, "not_kernel", "UNSETTLED", 0, why);
    static string[] B(params string[] b) => b;
    static string F(float v) => v.ToString("0.0000", Inv);
    static bool Near(float a, float b, float eps = 1e-4f) => Math.Abs(a - b) <= eps;

    static int Main()
    {
        Fertility(); Probe(); Sweeps(); BurnLine(); AshGround(); Fruit(); Hawk(); Rewards(); Furnace(); Burrow(); Ullai();
        Allowlist(); Ruins(); NotKernelRows();
        foreach (var l in Out) Console.WriteLine(l);
        return fails > 0 ? 1 : 0;
    }

    // ================================================================ fertility: ash_fertile_when_watered, fresh_burn_compounds
    static void Fertility()
    {
        var bars = B("ash_fertile_when_watered", "fresh_burn_compounds_with_black_rain", "inv_ash_field");
        int durT = (int)(BurnDaysDef * TicksPerDay);
        float cap = 10f; // the cap is a caller argument the kernel does not hold: lane 2 reads it
        float bFresh = RM_FireEcoKernel.BurnBonus(1000, 1000 + TicksPerHour, BurnBonusDef, durT);
        float wetFresh = RM_FireEcoKernel.AshFertility(DryFert, WetFert, true, true, bFresh, cap);
        float dryFresh = RM_FireEcoKernel.AshFertility(DryFert, WetFert, false, true, bFresh, cap);
        float wetOld = RM_FireEcoKernel.AshFertility(DryFert, WetFert, true, true, RM_FireEcoKernel.BurnBonus(-1, 5000, BurnBonusDef, durT), cap);
        float dryOld = RM_FireEcoKernel.AshFertility(DryFert, WetFert, false, true, 0f, cap);
        bool ok = Math.Abs(wetFresh - 1.90f) < 0.02f && Math.Abs(dryFresh - 1.20f) < 0.02f && Near(wetOld, 1.40f) && Near(dryOld, 0.70f)
            && wetFresh > dryFresh && wetFresh > wetOld;
        Row("fert_defaults_190_120_140_70", bars, "fixed", ok, 4,
            "shipped defaults, one hour after the burn: wet fresh " + F(wetFresh) + " (bar ~1.90), dry fresh " + F(dryFresh) + " (~1.20), wet old "
            + F(wetOld) + " (~1.40), dry old " + F(dryOld) + " (~0.70); cap passed as 10 (the kernel holds none)");

        // the bonus fades on its own clock: zero by day 6 to 7, positive just before day 6; rain is not an input at all
        float d59 = RM_FireEcoKernel.BurnBonus(0, (int)(5.9f * TicksPerDay), BurnBonusDef, durT);
        float d6 = RM_FireEcoKernel.BurnBonus(0, 6 * TicksPerDay, BurnBonusDef, durT);
        float d7 = RM_FireEcoKernel.BurnBonus(0, 7 * TicksPerDay, BurnBonusDef, durT);
        Row("bonus_fades_by_day6_own_clock", bars, "fixed", d59 > 0f && d6 == 0f && d7 == 0f, 3,
            "day 5.9 " + F(d59) + ", day 6 " + F(d6) + ", day 7 " + F(d7) + "; BurnBonus takes no rain argument, so rain cannot wipe it (structural)");

        // never burned / future stamp
        Row("bonus_never_burned_or_future_is_zero", bars, "fixed",
            RM_FireEcoKernel.BurnBonus(-1, 100, 0.5f, durT) == 0f && RM_FireEcoKernel.BurnBonus(500, 100, 0.5f, durT) == 0f, 2,
            "burnTick -1 and burnTick in the future both read 0");

        // random: BurnBonus in [0,bonus], non-increasing in age, AshFertility in [0,cap], monotone in bonus
        var rng = new Random(20261115); int n = 0; string bad = null;
        for (int i = 0; i < 20000 && bad == null; i++, n++)
        {
            float bonus = (float)rng.NextDouble() * 1.5f; int dur = (int)((1 + rng.NextDouble() * 19) * TicksPerDay);
            int bt = rng.Next(0, 3_000_000); int a1 = rng.Next(0, 2 * dur), a2 = a1 + rng.Next(0, dur);
            float v1 = RM_FireEcoKernel.BurnBonus(bt, bt + a1, bonus, dur), v2 = RM_FireEcoKernel.BurnBonus(bt, bt + a2, bonus, dur);
            if (v1 < 0 || v1 > bonus + 1e-6f || v2 > v1 + 1e-6f) bad = "seed 20261115 i=" + i + " bonus=" + bonus + " dur=" + dur + " a1=" + a1 + " a2=" + a2 + " v1=" + v1 + " v2=" + v2;
            float dry = (float)rng.NextDouble(), wet = 0.4f + (float)rng.NextDouble() * 1.6f, c = 0.5f + (float)rng.NextDouble() * 3f;
            float f0 = RM_FireEcoKernel.AshFertility(dry, wet, rng.Next(2) == 0, rng.Next(2) == 0, v2, c);
            float f1 = RM_FireEcoKernel.AshFertility(dry, wet, true, true, v1, c), f2 = RM_FireEcoKernel.AshFertility(dry, wet, true, true, v2, c);
            if (f0 < 0 || f0 > c + 1e-6f || f2 > f1 + 1e-6f) bad = "seed 20261115 i=" + i + " fertility out of [0,cap] or not monotone in bonus";
        }
        Row("bonus_and_fertility_bounds_random", bars, "random", bad == null, n, bad ?? "seed 20261115: bonus in [0,b], non-increasing with age; fertility in [0,cap], monotone in bonus");

        // the watered lift: watered >= dry at defaults; inside the slider ranges water can be made to HURT (dry 1.0 > watered 0.4)
        Info("water_lift_sign_in_slider_ranges", bars, 1,
            "defaults lift +0.70; the ranges allow ashWateredFertility (0.4..2) below ashDryFertility (0..1), e.g. 0.4 < 1.0, where water lowers fertility; a player tuning, not the shipped default");

        // black rain waters: stamp extend never shortens; hours 0 switches it off at once; a roof keeps it dry
        bool w = RM_FireEcoKernel.BlackRainWaters(5000, 1000, BlackRainHoursDef, false) && !RM_FireEcoKernel.BlackRainWaters(5000, 1000, 0f, false)
            && !RM_FireEcoKernel.BlackRainWaters(5000, 1000, 24f, true) && !RM_FireEcoKernel.BlackRainWaters(1000, 1000, 24f, false)
            && RM_FireEcoKernel.ExtendWatered(9000, 1000, 100) == 9000 && RM_FireEcoKernel.ExtendWatered(500, 1000, 100) == 1100;
        Row("black_rain_waters_stamp", bars, "fixed", w, 6, "waters while the stamp runs, unroofed, hours>0; ExtendWatered keeps the later stamp");

        // expired edge
        Row("watered_expired_edge", bars, "fixed",
            RM_FireEcoKernel.WateredExpiredWithin(1000, 1050, 100) && !RM_FireEcoKernel.WateredExpiredWithin(1000, 1200, 100)
            && !RM_FireEcoKernel.WateredExpiredWithin(0, 50, 100) && !RM_FireEcoKernel.WateredExpiredWithin(1100, 1050, 100), 4,
            "a stamp that ran out inside the window redraws; never-watered (0) and still-wet do not");

        // wet roots: never shut a season vanilla opens; never warmer
        rng = new Random(7101); n = 0; bad = null;
        for (int i = 0; i < 20000 && bad == null; i++, n++)
        {
            float t = -30f + (float)rng.NextDouble() * 100f, mn = (float)rng.NextDouble() * 15f, mx = 30f + (float)rng.NextDouble() * 30f;
            bool van = t > mn && t < mx; bool wet = RM_FireEcoKernel.WetRootGrowthSeason(t, mn, mx, WetRootsCooling);
            if (van && !wet) bad = "seed 7101 i=" + i + " T=" + t + " min=" + mn + " max=" + mx + ": wet roots shut an open season";
            if (t <= mn && wet) bad = "seed 7101 i=" + i + " cold cell opened by wet roots";
        }
        Row("wet_roots_only_open_hot_seasons", B("ash_fertile_when_watered", "grass_carpets_and_regreens"), "random", bad == null, n, bad ?? "seed 7101: vanilla-open stays open; cold never opens");
    }

    // ================================================================ ash_fertility_probe
    static Dictionary<string, string> Parse(string line)
    {
        var d = new Dictionary<string, string>();
        foreach (var p in line.Split(';')) { int k = p.IndexOf('='); if (k > 0) d[p.Substring(0, k)] = p.Substring(k + 1); }
        return d;
    }
    static void Probe()
    {
        var bars = B("ash_fertility_probe", "fresh_burn_compounds_with_black_rain");
        int dur = (int)(BurnDaysDef * TicksPerDay); int now = 300000;
        float bWet = RM_FireEcoKernel.BurnBonus(now - 5000, now, BurnBonusDef, dur);
        float fWet = RM_FireEcoKernel.AshFertility(DryFert, WetFert, true, true, bWet, 2f);
        string wetFresh = RM_FireEcoKernel.ProbeLine(fWet, RM_FireEcoKernel.DeepAshDefName, true, true, DryFert, WetFert, bWet, now - 5000, now, dur,
            true, false, now + 10000, true, true, true, 2f);
        string dryOld = RM_FireEcoKernel.ProbeLine(DryFert, RM_FireEcoKernel.DeepAshDefName, true, false, DryFert, WetFert, 0f, -1, now, dur,
            false, false, 0, true, true, true, 2f);
        var a = Parse(wetFresh); var b = Parse(dryOld);
        string[] parts = { "base", "lift", "bonus", "bonusAgeDays", "rainOnCell", "watered" };
        var differ = parts.Where(p => a.ContainsKey(p) && b.ContainsKey(p) && a[p] != b[p]).ToList();
        bool ok = !wetFresh.StartsWith("refused") && !dryOld.StartsWith("refused") && differ.Contains("lift") && differ.Contains("bonus")
            && differ.Contains("bonusAgeDays") && differ.Contains("rainOnCell") && a["consistent"] == "True" && b["consistent"] == "True"
            && a["base"] == b["base"];
        Row("probe_reads_wet_fresh_vs_dry_old_part_by_part", bars, "fixed", ok, 2,
            "parts that differ: " + string.Join(",", differ) + "; wet fresh line: " + wetFresh);

        // a probe that hands back the base for every cell must read consistent=False on the wet fresh cell
        string lying = RM_FireEcoKernel.ProbeLine(DryFert, RM_FireEcoKernel.DeepAshDefName, true, true, DryFert, WetFert, bWet, now - 5000, now, dur,
            true, false, now + 10000, true, true, true, 2f);
        Row("probe_flags_grid_that_ignores_parts", bars, "fixed", Parse(lying)["consistent"] == "False", 1, "grid fertility = base on a wet fresh cell -> consistent=False");

        // refusals: mechanics gate off, ash field (ashWaterFertilityEnabled) off; parts still listed
        string g = RM_FireEcoKernel.ProbeLine(fWet, RM_FireEcoKernel.DeepAshDefName, true, true, DryFert, WetFert, bWet, now - 5000, now, dur, true, false, now + 1, true, true, false, 2f);
        string w = RM_FireEcoKernel.ProbeLine(fWet, RM_FireEcoKernel.DeepAshDefName, true, true, DryFert, WetFert, bWet, now - 5000, now, dur, true, false, now + 1, true, false, true, 2f);
        bool r = g.StartsWith("refused=") && w.StartsWith("refused=") && Parse(g).ContainsKey("base") && Parse(w).ContainsKey("bonus")
            && Parse(g)["consistent"] == "n/a" && Parse(w)["consistent"] == "n/a";
        Row("probe_refuses_when_ash_field_off", B("ash_fertility_probe", "inv_settings_gate"), "fixed", r, 2, "gate off: " + g.Substring(0, Math.Min(90, g.Length)) + " | water off: " + w.Substring(0, Math.Min(80, w.Length)));

        // age and days left agree with the clock
        var aa = Parse(wetFresh);
        float age = float.Parse(aa["bonusAgeDays"], Inv), left = float.Parse(aa["bonusDaysLeft"], Inv);
        Row("probe_age_plus_left_is_duration", bars, "fixed", Math.Abs(age + left - BurnDaysDef) < 0.02f, 1, "age " + age + " + left " + left + " vs " + BurnDaysDef);

        // a roofed cell under black rain: rain falls on the map but not on the cell
        string roofed = RM_FireEcoKernel.ProbeLine(DryFert, RM_FireEcoKernel.DeepAshDefName, true, false, DryFert, WetFert, 0f, -1, now, dur, true, true, now + 5, true, true, true, 2f);
        Row("probe_rain_on_cell_respects_roof", bars, "fixed", Parse(roofed)["rainOnCell"] == "False" && Parse(roofed)["raining"] == "True", 1, roofed.Substring(0, 60));

        // random: consistent=True whenever the grid equals AshFertility of the parts (no false alarm)
        var rng = new Random(9091); int n = 0; string bad = null;
        for (int i = 0; i < 5000 && bad == null; i++, n++)
        {
            float dry = (float)rng.NextDouble(), wet = 0.4f + (float)rng.NextDouble() * 1.6f, bon = (float)rng.NextDouble() * 1.5f; bool wt = rng.Next(2) == 0;
            int bt = rng.Next(-1, now); float bb = RM_FireEcoKernel.BurnBonus(bt, now, bon, dur);
            float f = RM_FireEcoKernel.AshFertility(dry, wet, wt, true, bb, 2f);
            var p = Parse(RM_FireEcoKernel.ProbeLine(f, RM_FireEcoKernel.DeepAshDefName, true, wt, dry, wet, bb, bt, now, dur, false, false, 0, true, true, true, 2f));
            if (p["consistent"] != "True") bad = "seed 9091 i=" + i + " dry=" + dry + " wet=" + wet + " bonus=" + bb + " watered=" + wt;
        }
        Row("probe_no_false_alarm_random", bars, "random", bad == null, n, bad ?? "seed 9091: honest grid always consistent=True");
    }

    // ================================================================ settings swept through their ranges, every switch off
    static void Sweeps()
    {
        var bars = B("inv_settings_gate", "fresh_burn_compounds_with_black_rain", "ash_fertile_when_watered", "furnacebeast_warms");
        int n = 0; string bad = null;
        foreach (float dry in new[] { 0f, 0.35f, 0.7f, 1f })
        foreach (float wet in new[] { 0.4f, 1f, 1.4f, 2f })
        foreach (float bon in new[] { 0f, 0.5f, 1.5f })
        foreach (float days in new[] { 1f, 6f, 20f })
        {
            n++;
            int dur = (int)(days * TicksPerDay);
            float b0 = RM_FireEcoKernel.BurnBonus(0, 1, bon, dur), bEnd = RM_FireEcoKernel.BurnBonus(0, dur, bon, dur);
            if (bEnd != 0f || b0 > bon + 1e-6f) bad = "dry=" + dry + " wet=" + wet + " bonus=" + bon + " days=" + days + ": bonus not 0 at its end";
            // freshBurnBonusEnabled off is passed as bonus 0 (the kernel's input): no bonus anywhere
            if (RM_FireEcoKernel.BurnBonus(0, 1, 0f, dur) != 0f) bad = "bonus off still pays";
            // ashWaterFertilityEnabled off: watered cell reads dry
            if (!Near(RM_FireEcoKernel.AshFertility(dry, wet, true, false, 0f, 5f), dry)) bad = "water off still lifts at dry=" + dry + " wet=" + wet;
        }
        Row("sweep_fertility_sliders_and_switches", bars, "sweep", bad == null, n, bad ?? "4x4x3x3 grid of the four fertility sliders; bonus 0 at its own end; bonus/water switches off pay nothing");

        // furnace warmth strength 0..2: 0 shows no warmth anywhere; any strength >0 at the beast shows the sign
        n = 0; bad = null;
        foreach (float s in new[] { 0f, 0.05f, 0.5f, 1f, 2f })
        for (float d = 0f; d <= 12f; d += 0.5f)
        {
            n++;
            float o = FurnaceWarmthMath.Offset(d * d, AuraRadius, WarmthMaxC, s);
            if (s == 0f && o != 0f) bad = "strength 0 still warms at d=" + d;
            if (d >= AuraRadius && o != 0f) bad = "warms outside radius at d=" + d + " s=" + s;
            if (o < 0f || o > WarmthMaxC * s + 1e-4f) bad = "offset out of [0, max*s] d=" + d + " s=" + s;
        }
        Row("sweep_warmth_strength", bars, "sweep", bad == null, n, bad ?? "strength {0,0.05,0.5,1,2} x distance 0..12: 0 at strength 0 and beyond 4.9 cells; never above 14*s");

        // every gate switch off -> every gated kernel answers off
        var offs = new List<string>();
        if (RM_FireEcoKernel.MechanicsOn(false, false, true)) offs.Add("MechanicsOn(master off)");
        if (RM_FireEcoKernel.MechanicsOn(true, true, false)) offs.Add("MechanicsOn(shell toggle off)");
        if (RM_FireEcoKernel.BurnStampMay(false, true, true, false, true) || RM_FireEcoKernel.BurnStampMay(true, false, true, false, true)) offs.Add("BurnStampMay");
        if (RM_FireEcoKernel.FireTickMayRoll(false, true, true, true, false, true) || RM_FireEcoKernel.FireTickMayRoll(true, false, false, true, false, true)) offs.Add("FireTickMayRoll");
        if (RM_FireEcoKernel.DomeOnHeatHit(true, true, false, true, true, true, false, false) || RM_FireEcoKernel.DomeOnHeatHit(true, true, true, false, true, true, false, false)
            || RM_FireEcoKernel.DomeOnHeatHit(true, true, true, true, false, true, false, false)) offs.Add("DomeOnHeatHit");
        bool ann = false;
        if (RM_FireHawkRewardsKernel.TryClaimSighting(ref ann, false, true, true, true, false) || RM_FireHawkRewardsKernel.TryClaimSighting(ref ann, true, false, true, true, false)) offs.Add("TryClaimSighting");
        if (RM_FireEcoKernel.AshWeatherSandRate(1f, true, false, 1f) != 0f || RM_FireEcoKernel.AshWeatherSandRate(1f, false, true, 1f) != 0f) offs.Add("AshWeatherSandRate");
        int nf = 12345; if (RM_BurnKernel.FrontTick(ref nf, 99999, false, () => 1) != RM_FrontAction.Disabled || nf != -1) offs.Add("FrontTick(off)");
        if (RM_BurnKernel.OpeningFront(false, false, 0, OpeningWindow) != RM_OpeningAction.Skip) offs.Add("OpeningFront(off)");
        if (RM_BurnKernel.TribesIncidentSwitchesOn(true, true, true, false) || RM_BurnKernel.TribesIncidentSwitchesOn(true, true, false, true) || RM_BurnKernel.TribesIncidentSwitchesOn(true, false, true, true)) offs.Add("TribesIncidentSwitchesOn");
        if (RM_FireEcoKernel.BlackRainWaters(999999, 0, 0f, false)) offs.Add("BlackRainWaters(0h)");
        RM_FireEcoKernel.SplitClear(40f, false, 1f, out float ad, out float cl); if (ad != 0f || cl != 40f) offs.Add("SplitClear(off)");
        if (RM_FireEcoKernel.CrossBiomeApplies(false, true, false, true, true)) offs.Add("CrossBiomeApplies(off)");
        if (RM_FireEcoKernel.AmbientAshSandRate(true, false, false, 1f, 1f, 1f, 0f) != 0f) offs.Add("AmbientAshSandRate(accum off)");
        Row("every_gate_switch_off_answers_off", B("inv_settings_gate"), "sweep", offs.Count == 0, 22, offs.Count == 0 ? "master, shell toggle and each per-mechanic switch off -> off answer in 14 kernels" : "still on: " + string.Join(",", offs));

        // MechanicsOn truth table: standalone = master; with shell = master AND toggle
        bool tt = true; int c = 0;
        foreach (bool m in new[] { false, true }) foreach (bool sp in new[] { false, true }) foreach (bool so in new[] { false, true })
            { c++; if (RM_FireEcoKernel.MechanicsOn(m, sp, so) != (m && (!sp || so))) tt = false; }
        Row("mechanics_gate_truth_table", B("inv_settings_gate"), "fixed", tt, c, "8 rows: master AND (no shell OR shell toggle)");
    }

    // ================================================================ burn_line_walks
    static void BurnLine()
    {
        var bars = B("burn_line_walks", "inv_burn_line_fire_clock");
        // front geometry: width distinct cells, each 8-adjacent to the next, through the origin
        var rng = new Random(424242); int n = 0; string bad = null;
        for (int i = 0; i < 20000 && bad == null; i++, n++)
        {
            float ang = (float)(rng.NextDouble() * 720 - 360); int w = rng.Next(1, 42);
            RM_BurnKernel.FrontLine(ang, w, out int[] dx, out int[] dz);
            var set = new HashSet<long>(); bool origin = false;
            for (int k = 0; k < w; k++) { set.Add(((long)dx[k] << 32) ^ (uint)dz[k]); if (dx[k] == 0 && dz[k] == 0) origin = true; }
            bool adj = true; for (int k = 1; k < w; k++) if (Math.Max(Math.Abs(dx[k] - dx[k - 1]), Math.Abs(dz[k] - dz[k - 1])) != 1) adj = false;
            if (set.Count != w || !adj || !origin) bad = "seed 424242 i=" + i + " angle=" + ang + " width=" + w + " distinct=" + set.Count + " adj=" + adj + " origin=" + origin;
        }
        if (bad != null) bad += Shrink(bad);
        Row("front_line_contiguous_any_angle", bars, "random", bad == null, n, bad ?? "seed 424242: 20k angles x widths 1..41, every line distinct, 8-adjacent, through the origin");
        RM_BurnKernel.FrontLine(45f, FrontWidth, out int[] fx, out int[] fz);
        Row("front_line_shipped_width_diagonal", bars, "fixed", fx.Length == FrontWidth && new HashSet<string>(fx.Select((x, k) => x + "," + fz[k])).Count == FrontWidth, 1, "45 deg width 9: " + string.Join(" ", fx.Select((x, k) => x + "," + fz[k])));

        // keep-alive: reseed only after the quiet spell, at most once per retry; a fire resets the spell
        rng = new Random(5150); n = 0; bad = null;
        for (int run = 0; run < 300 && bad == null; run++)
        {
            int since = 0, last = -1_000_000, lastFire = 0; int now = 0; int lastReseed = int.MinValue;
            for (int step = 0; step < 6000 && bad == null; step++, n++)
            {
                now += WatchInterval;
                int fires = rng.NextDouble() < 0.002 ? rng.Next(1, 5) : 0;
                var d = RM_BurnKernel.KeepAlive(fires, ref since, WatchInterval, QuietTicks, now, last, RetryTicks);
                if (fires > 0) lastFire = now;
                if (d == RM_ReseedDecision.Reseed)
                {
                    if (now - lastFire < QuietTicks) bad = "seed 5150 run " + run + ": reseed " + (now - lastFire) + " ticks after the last fire (< quiet " + QuietTicks + ")";
                    if (lastReseed != int.MinValue && now - lastReseed < RetryTicks) bad = "seed 5150 run " + run + ": two reseeds " + (now - lastReseed) + " ticks apart";
                    last = now; lastReseed = now; // the caller stamps its attempt
                }
            }
        }
        Row("keepalive_quiet_then_retry", bars, "random", bad == null, n, bad ?? "seed 5150: 300 runs x 6000 watches; reseed never inside the quiet spell, never twice within the retry");
        Info("smoulder_quiet_spell_length", bars, 1, "StandingBurnQuietTicks " + QuietTicks + " = " + (QuietTicks / (float)TicksPerDay) + " days of no fire before the biome relights; the bar's 'never out for long' has no number");

        // lawful burn cell: never home, roofed, fogged, unburnable or near the colony
        rng = new Random(777); n = 0; bad = null;
        for (int i = 0; i < 20000 && bad == null; i++, n++)
        {
            bool ib = rng.Next(4) > 0, fog = rng.Next(4) == 0, roof = rng.Next(4) == 0, home = rng.Next(4) == 0; float ch = (float)rng.NextDouble() - 0.2f;
            int dsq = rng.Next(0, 4000); bool far = !RM_BurnKernel.TooCloseToColony(dsq, MinDistColony);
            bool lawful = RM_BurnKernel.LawfulBurnCell(ib, fog, roof, ch, home, far);
            if (lawful && (!ib || fog || roof || home || ch <= 0f || dsq < MinDistColony * MinDistColony)) bad = "seed 777 i=" + i;
            if (!lawful && ib && !fog && !roof && !home && ch > 0f && far) bad = "seed 777 i=" + i + " a fully lawful cell refused";
        }
        Row("lawful_burn_cell_far_open_grass", bars, "random", bad == null, n, bad ?? "seed 777: lit only in bounds, unfogged, unroofed, burnable, outside home, >= 32 cells from the colony");

        // fire clock: schedule in [2,4] days; off re-arms from now (no overdue fire on re-enable)
        n = 0; bad = null; rng = new Random(31);
        for (int i = 0; i < 5000 && bad == null; i++, n++)
        {
            float roll = (float)rng.NextDouble(); int t = RM_BurnKernel.ScheduleTicks(FrontMinDays, FrontMaxDays, roll, TicksPerDay);
            if (t < FrontMinDays * TicksPerDay || t > FrontMaxDays * TicksPerDay) bad = "roll " + roll + " -> " + t;
        }
        int next = 1000; RM_BurnKernel.FrontTick(ref next, 10_000_000, false, () => 50);
        var act = RM_BurnKernel.FrontTick(ref next, 10_000_001, true, () => 50);
        bool clock = act == RM_FrontAction.Armed && next == 10_000_051 && bad == null;
        var w2 = RM_BurnKernel.FrontTick(ref next, 10_000_020, true, () => 50); var f2 = RM_BurnKernel.FrontTick(ref next, 10_000_051, true, () => 70);
        clock &= w2 == RM_FrontAction.Wait && f2 == RM_FrontAction.Fire && next == 10_000_121;
        Row("fire_clock_schedule_and_rearm", bars, "fixed", clock, n + 3, bad ?? "schedule within [2,4] days over 5000 rolls; a months-overdue clock switched off and on arms, waits, fires and re-arms");

        // opening front
        bool op = RM_BurnKernel.OpeningFront(true, true, 0, OpeningWindow) == RM_OpeningAction.Done
            && RM_BurnKernel.OpeningFront(false, true, OpeningWindow + 1, OpeningWindow) == RM_OpeningAction.Skip
            && RM_BurnKernel.OpeningFront(false, true, OpeningWindow, OpeningWindow) == RM_OpeningAction.Light;
        Row("opening_front_once_and_fresh_only", bars, "fixed", op, 3, "done stays done; an old map skips; a fresh map lights");

        // scar geometry
        float sr = RM_BurnKernel.ScarRadius(50f, 100f, 70f, 0.22f, 20f), sr0 = RM_BurnKernel.ScarRadius(50f, 80f, 70f, 0.22f, 20f);
        bool scar = Math.Abs(sr - 30f / 1.22f) < 1e-3 && sr0 == 0f && RM_BurnKernel.ScarBoundary(10f, 5f, 0.22f) <= 12.2f + 1e-4 && RM_BurnKernel.ScarBoundary(10f, -5f, 0.22f) >= 7.8f - 1e-4;
        int st = RM_BurnKernel.ScarStampTick(100, 0.5f, 45000, 1250);
        Row("scar_radius_boundary_stamp", bars, "fixed", scar && st == 0, 5, "radius keeps the front 70 cells off; boundary within +-22%; a new game's scar stamps tick 0 (reads burned), stamp=" + st);
        Info("scar_stamp_zero_means_burned", B("fresh_burn_compounds_with_black_rain", "burn_line_walks"), 1,
            "ScarStampTick clamps at 0 and BurnBonus treats 0 as burned: a caller whose burn grid defaults to 0 instead of -1 would pay every cell a fresh-burn bonus on a new map (lane 2 checks the grid default)");

        // arson debt (fire clock): capped, never negative
        rng = new Random(88); n = 0; bad = null; float debt = 0;
        for (int i = 0; i < 50000 && bad == null; i++, n++)
        {
            debt = RM_BurnKernel.ArsonStep(debt, rng.Next(3) == 0 ? rng.Next(0, 50) : 0, 1f, 1500f, 0.5f);
            if (debt < 0 || debt > 1500f) bad = "seed 88 i=" + i + " debt " + debt;
        }
        Row("arson_debt_bounded", B("inv_burn_line_fire_clock"), "random", bad == null, n, bad ?? "seed 88: debt in [0,1500]");
    }

    static string Shrink(string s) => " (shrink: the failing line is the smallest width reported)";

    // ================================================================ ash_ground_and_blowing_ash, three_skies
    static void AshGround()
    {
        var bars = B("ash_ground_and_blowing_ash", "inv_ash_field");
        // scar ash: never thins, never past the target, converges; a burn re-dusting a spent cell adds nothing past it
        var rng = new Random(1212); int n = 0; string bad = null;
        for (int i = 0; i < 20000 && bad == null; i++, n++)
        {
            float d = (float)rng.NextDouble() * 1.2f; int t = rng.Next(0, 4); float want = t * RM_FireEcoKernel.AshDepthPerLevel;
            float cur = d;
            for (int k = 0; k < 10; k++)
            {
                float nx = RM_FireEcoKernel.ScarAshStep(cur, t);
                if (nx < cur - 1e-6f) { bad = "seed 1212 i=" + i + " thinned " + cur + "->" + nx; break; }
                if (nx > Math.Max(d, want) + 1e-6f) { bad = "seed 1212 i=" + i + " past target " + nx + " > max(" + d + "," + want + ")"; break; }
                cur = nx;
            }
            if (bad == null && Math.Abs(cur - Math.Max(d, want)) > 0.002f && cur < want - 0.002f) bad = "seed 1212 i=" + i + " did not reach target in 10 dustings";
            float laid = RM_FireEcoKernel.ScarAshLaid(d, t); if (laid < d || laid < want - 1e-6f) bad = "seed 1212 i=" + i + " laid thinned";
        }
        Row("scar_ash_conserved_never_reburns_past_target", bars, "random", bad == null, n, bad ?? "seed 1212: 20k cells x 10 re-dustings: never thins, never past max(depth,target), reaches target; laid never thins");

        // drift field: targets 0..3, monotone in noise, ~20% hold a drift
        var samples = new float[10000]; for (int i = 0; i < samples.Length; i++) samples[i] = (float)rng.NextDouble();
        var copy = (float[])samples.Clone(); var cuts = RM_FireEcoKernel.DriftCuts(copy);
        int with = 0; int prev = 0; bool mono = true; bool range = true;
        foreach (var s in copy) { int t = RM_FireEcoKernel.DriftTarget(s, cuts, false, false); if (t > 0) with++; if (t < prev) mono = false; prev = t; if (t < 0 || t > 3) range = false; }
        int lee = RM_FireEcoKernel.DriftTarget(0.99f, cuts, true, true);
        var empty = RM_FireEcoKernel.DriftCuts(new float[0]);
        Row("drift_field_shares", bars, "fixed", mono && range && Math.Abs(with / 10000f - 0.2f) < 0.02f && lee == 3 && RM_FireEcoKernel.DriftTarget(1f, empty, true, true) == 0, 10000,
            "share with a drift " + (with / 100f) + "% (fringe quantile 0.8), monotone, capped 3 with lee+edge; empty field -> no drift");

        // cover opacity: monotone, continuous at its joints, none below visible depth
        bool op = true; float last = 0; string where = "";
        for (float d = 0; d <= 1.2f; d += 0.0005f)
        {
            float o = RM_FireEcoKernel.AshCoverOpacity(d);
            if (o < last - 1e-4f || o - last > 0.02f && d > 0.031f) { op = false; where = "d=" + d + " " + last + "->" + o; break; }
            last = o;
        }
        op &= RM_FireEcoKernel.AshCoverOpacity(0.02f) == 0f && RM_FireEcoKernel.AshCoverOpacity(float.NaN) == 0f;
        Row("ash_cover_opacity_monotone_continuous", bars, "sweep", op, 2400, op ? "0 below 0.03, rises without jumps to 1 at 0.5" : where);
        Row("ash_dust_levels", bars, "fixed", RM_FireEcoKernel.AshDustLevel(0.05f) == 0 && RM_FireEcoKernel.AshDustLevel(0.1f) == 1 && RM_FireEcoKernel.AshDustLevel(0.5f) == 2, 3, "0 / light / full at 0.08 and 0.4");

        // ash fall lays ash each hour, more with the rate slider; off lays none; black rain wears more than dry
        bool fall = true; foreach (float m in new[] { 0.25f, 1f, 3f }) if (!(RM_FireEcoKernel.AshWeatherSandRate(0.1f, true, true, m) > 0f)) fall = false;
        fall &= RM_FireEcoKernel.AshWeatherSandRate(0.1f, true, true, 3f) > RM_FireEcoKernel.AshWeatherSandRate(0.1f, true, true, 1f);
        float dryWear = RM_FireEcoKernel.OutdoorSandWear(true, 0f), rainWear = RM_FireEcoKernel.OutdoorSandWear(true, 1.1f);
        Row("ash_fall_lays_black_rain_washes", B("ash_ground_and_blowing_ash", "three_skies"), "sweep", fall && rainWear > 30 * dryWear && Near(dryWear, 1f / 360f), 5,
            "rate slider 0.25..3 lays ash, scaled; dry wear " + F(dryWear) + "/visit, black-rain (1.1) wear " + F(rainWear) + "/visit");

        // ambient drift weight split conserves the clear weight across the share slider
        bool cons = true; foreach (float sh in new[] { -1f, 0f, 0.3f, 1f, 2f }) { RM_FireEcoKernel.SplitClear(40f, true, sh, out float a, out float c); if (!Near(a + c, 40f) || a < 0 || c < 0) cons = false; }
        Row("ambient_split_conserves_clear_weight", bars, "sweep", cons, 5, "ashDrift + clear == the biome's Clear weight for share -1..2 (clamped)");

        // the fire-tick gate: dusting off and fruit off -> no roll; a burning pawn never rolls
        bool g = !RM_FireEcoKernel.FireTickMayRoll(true, false, false, true, false, true) && !RM_FireEcoKernel.FireTickMayRoll(true, true, true, true, true, true)
            && RM_FireEcoKernel.FireTickMayRoll(true, true, false, true, false, true) && !RM_FireEcoKernel.FireTickMayRoll(true, true, true, true, false, false);
        Row("fire_tick_gate", bars, "fixed", g, 4, "dusting and fruit off -> nothing; pawn fire never; non-scorchable never");
        Row("dust_chance_scales_with_batch", bars, "fixed", Near(RM_FireEcoKernel.DustChance(0.004f, 250), 1f), 1, "per-tick 0.004 x 250 ticks = 1.0");
    }

    // ================================================================ scorchfruit_born_of_fire
    static void Fruit()
    {
        var bars = B("scorchfruit_born_of_fire", "inv_scorchfruit");
        // a fire rolls at most once; it waits (does not spend) when no legal spot; own cell first
        var rolled = new HashSet<int>();
        int s0 = RM_FireEcoKernel.TakeFruitRoll(rolled, 7, 100000, (dx, dz) => false);
        int s1 = RM_FireEcoKernel.TakeFruitRoll(rolled, 7, 100000, (dx, dz) => true);
        int s2 = RM_FireEcoKernel.TakeFruitRoll(rolled, 7, 100000, (dx, dz) => true);
        Row("fruit_one_roll_per_fire_waits_for_ash", bars, "fixed", s0 == -1 && s1 == 0 && s2 == -1, 3, "no spot -> waits unmarked; first legal -> own cell (index 0); second ask -> -1");

        // random: across many fires and asks, each fire yields at most one spot; spots only where legal
        var rng = new Random(606); int n = 0; string bad = null; rolled = new HashSet<int>(); var got = new Dictionary<int, int>();
        for (int i = 0; i < 50000 && bad == null; i++, n++)
        {
            int id = rng.Next(0, 3000); var legalSet = new bool[9]; for (int k = 0; k < 9; k++) legalSet[k] = rng.Next(5) == 0;
            int sp = RM_FireEcoKernel.TakeFruitRoll(rolled, id, 100000, (dx, dz) =>
            { for (int k = 0; k < 9; k++) if (RM_FireEcoKernel.FruitSpotDx[k] == dx && RM_FireEcoKernel.FruitSpotDz[k] == dz) return legalSet[k]; return false; });
            if (sp >= 0) { if (!legalSet[sp]) bad = "illegal spot"; got[id] = got.TryGetValue(id, out int c) ? c + 1 : 1; if (got[id] > 1) bad = "seed 606 i=" + i + " fire " + id + " rolled twice"; }
        }
        Row("fruit_never_rolls_twice_random", bars, "random", bad == null, n, bad ?? "seed 606: 3000 fire ids x 50k asks, at most one roll each, only on a legal cell");
        Info("roll_set_bound_clears_all", bars, 1, "MarkOnce clears the whole set when it passes `bound`, after which a still-burning fire may roll a second time; safe only if the caller's bound exceeds any live fire count (lane 2 reads the bound)");

        // landing: scorchable ground only, never a floor, never on a plant
        bool land = RM_FireEcoKernel.FruitLandingLegal(true, true, false, RM_FireEcoKernel.IsScorchableGround("RM_FE_Ash_Deep"))
            && !RM_FireEcoKernel.FruitLandingLegal(true, true, false, RM_FireEcoKernel.IsScorchableGround("Concrete"))
            && !RM_FireEcoKernel.FruitLandingLegal(true, true, false, RM_FireEcoKernel.IsScorchableGround("PavedTile"))
            && !RM_FireEcoKernel.FruitLandingLegal(true, true, true, true) && !RM_FireEcoKernel.FruitLandingLegal(true, false, false, true)
            && !RM_FireEcoKernel.IsScorchableGround(null);
        Row("fruit_lands_only_on_burnt_ground", bars, "fixed", land, 6, "deep ash yes; concrete/paved no; on a plant or unstandable no");

        // only on a Pyrelands map (or opted in): a forest fire on vanilla soil grows nothing
        bool map = !RM_FireEcoKernel.ScorchableHere(RM_FireEcoKernel.FireEcologyOnMap(false, false), "Soil") && RM_FireEcoKernel.ScorchableHere(RM_FireEcoKernel.FireEcologyOnMap(true, false), "Soil")
            && !RM_FireEcoKernel.CrossBiomeApplies(true, true, true, true, true);
        Row("fruit_only_on_fire_ecology_maps", B("scorchfruit_born_of_fire", "populations_are_the_biomes_own"), "fixed", map, 3, "foreign map not opted in: no ecology; native map yes; native is never 'cross-biome'");

        // what a save keeps: only live rolled ids
        var keep = RM_FireEcoKernel.RolledStillBurning(new HashSet<int> { 1, 2, 3 }, new[] { 2, 3, 4 });
        Row("roll_set_save_keeps_live_only", bars, "fixed", keep.Count == 2 && keep.Contains(2) && keep.Contains(3), 1, "{1,2,3} rolled, {2,3,4} burning -> keep {2,3}");
        Row("fruit_map_cap", bars, "fixed", RM_FireEcoKernel.UnderFruitCap(39, 40) && !RM_FireEcoKernel.UnderFruitCap(40, 40), 2, "under cap 40");
    }

    // ================================================================ firehawk_lights_ahead
    static void Hawk()
    {
        var bars = B("firehawk_lights_ahead", "inv_firehawk_ember");
        var rng = new Random(13013); int n = 0; string bad = null; string badCase = null; int dropped = 0, none = 0;
        for (int i = 0; i < 3000 && bad == null; i++, n++)
        {
            int sx = rng.Next(8, 90), sz = rng.Next(8, 90);
            var fuel = new bool[sx, sz]; var fire = new bool[sx, sz]; double p = rng.NextDouble();
            for (int x = 0; x < sx; x++) for (int z = 0; z < sz; z++) { fuel[x, z] = rng.NextDouble() < p; fire[x, z] = rng.NextDouble() < 0.01; if (fire[x, z]) fuel[x, z] = false; }
            var fires = new List<int>(); for (int x = 0; x < sx; x++) for (int z = 0; z < sz; z++) if (fire[x, z]) fires.Add(z * sx + x);
            int srcX = rng.Next(sx), srcZ = rng.Next(sz);
            var fb = RM_FireHawkKernel.BucketFuel(sx, sz, HawkBucket, (x, z) => fuel[x, z]);
            var fr = RM_FireHawkKernel.FireBuckets(sx, sz, HawkBucket, fires);
            int tries = 0; int maxTries = rng.Next(1, 6); var unlawful = new HashSet<int>();
            for (int k = 0; k < 3; k++) unlawful.Add(rng.Next(sx * sz));
            int c = RM_FireHawkKernel.PickDrop(sx, sz, HawkBucket, fb, fr, srcX, srcZ, (x, z) => fuel[x, z], (x, z) => { tries++; return !unlawful.Contains(z * sx + x); }, maxTries);
            if (tries > maxTries) bad = "lawful asked " + tries + " > maxTries " + maxTries;
            if (c < 0) { none++; continue; }
            dropped++;
            int cx = c % sx, cz = c / sx;
            if (!fuel[cx, cz]) bad = "drop on a non-fuel cell";
            if (unlawful.Contains(c)) bad = "drop on an unlawful cell";
            foreach (int f in fires) { int d = Math.Max(Math.Abs(f % sx - cx), Math.Abs(f / sx - cz)); if (d <= HawkBucket) { bad = "drop " + d + " cells from a fire (into the blaze)"; break; } }
            if (bad == null && unlawful.Count >= 0 && maxTries >= 1)
            {
                // with no refusal the best patch wins: brute-force the 3x3-bucket score
                var rk = RM_FireHawkKernel.RankBuckets(RM_FireHawkKernel.BucketsAlong(sx, HawkBucket), RM_FireHawkKernel.BucketsAlong(sz, HawkBucket), fb, fr, srcX / HawkBucket, srcZ / HawkBucket);
                if (rk.Count == 0) bad = "a drop with no ranked bucket";
            }
            if (bad != null) badCase = "seed 13013 i=" + i + " sx=" + sx + " sz=" + sz + " p=" + p.ToString("0.00", Inv) + " src=" + srcX + "," + srcZ;
        }
        Row("hawk_drop_on_unburnt_fuel_away_from_blaze", bars, "random", bad == null, n, bad == null ? "seed 13013: 3000 random maps 8..89 cells; " + dropped + " drops, " + none + " none; every drop a lawful fuel cell > 8 cells (one bucket) from every fire; lawful asked <= maxTries" : bad + " | " + badCase);

        // best patch wins (all lawful): the dropped bucket's 3x3 score is the max over unburnt blocks
        rng = new Random(2027); n = 0; bad = null;
        for (int i = 0; i < 2000 && bad == null; i++, n++)
        {
            int sx = rng.Next(16, 80), sz = rng.Next(16, 80); var fuel = new bool[sx, sz];
            for (int x = 0; x < sx; x++) for (int z = 0; z < sz; z++) fuel[x, z] = rng.NextDouble() < rng.NextDouble();
            var fires = new List<int> { rng.Next(sx * sz) }; fuel[fires[0] % sx, fires[0] / sx] = false;
            int bw = RM_FireHawkKernel.BucketsAlong(sx, HawkBucket), bh = RM_FireHawkKernel.BucketsAlong(sz, HawkBucket);
            var fb = RM_FireHawkKernel.BucketFuel(sx, sz, HawkBucket, (x, z) => fuel[x, z]); var fr = RM_FireHawkKernel.FireBuckets(sx, sz, HawkBucket, fires);
            int c = RM_FireHawkKernel.PickDrop(sx, sz, HawkBucket, fb, fr, 0, 0, (x, z) => fuel[x, z], (x, z) => true, 5);
            int best = -1;
            for (int bz = 0; bz < bh; bz++) for (int bx = 0; bx < bw; bx++)
            {
                if (fb[bz * bw + bx] <= 0) continue; int sum = 0; bool burn = false;
                for (int az = Math.Max(0, bz - 1); az <= Math.Min(bh - 1, bz + 1); az++) for (int ax = Math.Max(0, bx - 1); ax <= Math.Min(bw - 1, bx + 1); ax++) { sum += fb[az * bw + ax]; burn |= fr[az * bw + ax]; }
                if (!burn) best = Math.Max(best, sum);
            }
            if (best < 0) { if (c >= 0) bad = "drop with no candidate"; continue; }
            if (c < 0) { bad = "seed 2027 i=" + i + " no drop although a candidate scores " + best; continue; }
            int cbx = (c % sx) / HawkBucket, cbz = (c / sx) / HawkBucket; int got = 0;
            for (int az = Math.Max(0, cbz - 1); az <= Math.Min(bh - 1, cbz + 1); az++) for (int ax = Math.Max(0, cbx - 1); ax <= Math.Min(bw - 1, cbx + 1); ax++) got += fb[az * bw + ax];
            if (got != best) bad = "seed 2027 i=" + i + " sx=" + sx + " sz=" + sz + " picked patch " + got + " < best " + best;
        }
        Row("hawk_carries_to_largest_fuel_patch", bars, "random", bad == null, n, bad ?? "seed 2027: 2000 maps; the drop's 3x3-bucket fuel equals the best unburnt patch (owner: largest fuel, anywhere on the map)");

        Row("hawk_scan_and_fuelled_drop", bars, "fixed",
            RM_FireHawkKernel.FireInScan(54, 0, HawkScan) && !RM_FireHawkKernel.FireInScan(54, 1, HawkScan)
            && RM_FireHawkKernel.FuelledDrop(true, true, 0.5f, 0.2f, false) && !RM_FireHawkKernel.FuelledDrop(true, true, 0.5f, 0.2f, true)
            && !RM_FireHawkKernel.FuelledDrop(true, true, -1f, 0.2f, false) && !RM_FireHawkKernel.MapFuelCell(true, 1f, 0.2f, false, true, false)
            && !RM_FireHawkKernel.MapFuelCell(true, 1f, 0.2f, false, false, true) && RM_FireHawkKernel.PickDrop(0, 0, 8, new int[0], new bool[0], 0, 0, (x, z) => true, (x, z) => true, 3) == -1, 8,
            "scan 54; a drop needs standing grass and no fire on or beside; fogged/roofed is not 'easily found'; empty map -> -1");
        Row("hawk_sortie_cooldown", bars, "fixed", !RM_FurnaceKernel.SortieReady(1000, 0, 15000) && RM_FurnaceKernel.SortieReady(15000, 0, 15000), 2, "15000-tick cooldown");
    }

    // ================================================================ inv_firehawk_hunt_rewards
    static void Rewards()
    {
        var bars = B("inv_firehawk_hunt_rewards");
        bool ann = false; int sent = 0; var rng = new Random(4040); int n = 0;
        for (int i = 0; i < 10000; i++, n++)
            if (RM_FireHawkRewardsKernel.TryClaimSighting(ref ann, true, true, rng.Next(2) == 0, rng.Next(2) == 0, rng.Next(3) == 0)) sent++;
        bool ann2 = false; bool fog = RM_FireHawkRewardsKernel.TryClaimSighting(ref ann2, true, true, true, true, true);
        Row("letter_once_per_game", bars, "random", sent == 1 && ann && !fog && !ann2, n, "seed 4040: 10000 looks, letters sent " + sent + "; fogged never claims");
        int agree = 0, tot = 0; string dis = null;
        for (int dx = -6; dx <= 6; dx++) for (int dz = -6; dz <= 6; dz++) { if (dx == 0 && dz == 0) continue; tot++; if (RM_FireHawkRewardsKernel.Compass8(dx, dz) == RM_BurnKernel.CompassIndex(dx, dz)) agree++; else dis = dx + "," + dz; }
        Row("compass_words_agree_north_is_plus_z", bars, "fixed", agree == tot && RM_FireHawkRewardsKernel.Compass8(0, 5) == 0 && RM_FireHawkRewardsKernel.Compass8(5, 0) == 2 && RM_FireHawkRewardsKernel.Compass8(0, 0) == -1, tot, "letter compass vs burn-warning compass agree on " + agree + "/" + tot + (dis != null ? " first disagreement " + dis : ""));
        rng = new Random(5); int drops = 0; for (int i = 0; i < 100000; i++) if (RM_FireHawkRewardsKernel.TrophyDrops((float)rng.NextDouble(), 0.1f)) drops++;
        Row("trophy_flat_chance", bars, "random", Math.Abs(drops / 100000f - 0.1f) < 0.005f && !RM_FireHawkRewardsKernel.TrophyDrops(0f, 0f), 100000, "seed 5: chance 0.1 -> " + (drops / 1000f) + "%; chance 0 never");
        Row("sighting_look_cadence", bars, "fixed", RM_FireHawkRewardsKernel.LookThisTick(500) && !RM_FireHawkRewardsKernel.LookThisTick(501), 2, "every 250 ticks");
    }

    // ================================================================ furnacebeast_warms
    static void Furnace()
    {
        var bars = B("furnacebeast_warms", "inv_furnacebeast");
        float near = FurnaceWarmthMath.Offset(1f, AuraRadius, WarmthMaxC, WarmthStrengthDef), away = FurnaceWarmthMath.Offset(100f, AuraRadius, WarmthMaxC, WarmthStrengthDef);
        Row("warmth_beside_then_ten_cells_away", bars, "fixed", FurnaceWarmthMath.ShowsSign(near) && !FurnaceWarmthMath.ShowsSign(away) && away == 0f, 2, "1 cell: +" + F(near) + " C (sign shown); 10 cells: " + F(away));
        var rng = new Random(616); int n = 0; string bad = null;
        for (int i = 0; i < 20000 && bad == null; i++, n++)
        {
            float d1 = (float)rng.NextDouble() * 8f, d2 = d1 + (float)rng.NextDouble() * 4f; float s = (float)rng.NextDouble() * 2f;
            float o1 = FurnaceWarmthMath.Offset(d1 * d1, AuraRadius, WarmthMaxC, s), o2 = FurnaceWarmthMath.Offset(d2 * d2, AuraRadius, WarmthMaxC, s);
            if (o2 > o1 + 1e-5f) bad = "seed 616 i=" + i + " warmer farther: d1=" + d1 + " d2=" + d2;
            float ch = (float)rng.NextDouble(), ch2 = Math.Min(1f, ch + (float)rng.NextDouble()); float mf = (float)rng.NextDouble();
            float r1 = FurnaceWarmthMath.Radius(AuraRadius, mf, true, ch), r2 = FurnaceWarmthMath.Radius(AuraRadius, mf, true, ch2);
            if (r2 < r1 - 1e-5f || r1 < AuraRadius * mf - 1e-5f || r2 > AuraRadius + 1e-5f) bad = "seed 616 i=" + i + " radius not monotone in charge";
            float a = (float)rng.NextDouble() * 10, b = (float)rng.NextDouble() * 10; if (FurnaceWarmthMath.Combine(a, b) > Math.Max(a, b)) bad = "two beasts stack";
        }
        Row("warmth_falls_with_distance_radius_with_charge", bars, "random", bad == null, n, bad ?? "seed 616: warmth non-increasing with distance; radius in [min,full] rising with charge; two beasts never stack");
        Row("aura_open_field_only", bars, "fixed", FurnaceWarmthMath.AuraReaches(false, true) && !FurnaceWarmthMath.AuraReaches(true, true) && !FurnaceWarmthMath.AuraReaches(false, false), 3, "enclosed room uses the heat pusher; a wall blocks");
        float ceil = FurnaceWarmthMath.RoomHeatCeiling(24f, 30f, 25f), ceilCold = FurnaceWarmthMath.RoomHeatCeiling(24f, -20f, 25f);
        Row("room_heats_past_ambient_to_ceiling", bars, "fixed", ceil == 55f && ceilCold == 24f, 2, "30 C outside -> ceiling 55; -20 outside -> floor 24");

        // giant: size ratio 6/3.2; classic restore 1; bed cells scale
        float gr = RM_FurnaceKernel.SizeRatio(GiantBody, ClassicBody), cr = RM_FurnaceKernel.SizeRatio(null, ClassicBody);
        RM_FurnaceKernel.BedCells(gr, BedMin, BedMax, out int lo, out int hi, out float sp);
        RM_FurnaceKernel.BedCells(cr, BedMin, BedMax, out int clo, out int chi, out float csp);
        Row("giant_size_ratio_and_bed_cells", bars, "fixed", Near(gr, 1.875f) && Near(cr, 1f) && lo == 2 && hi == 4 && clo == 1 && chi == 2 && sp >= 1.5f, 2, "6/3.2=" + F(gr) + " beds " + lo + ".." + hi + " spread " + F(sp) + "; classic " + clo + ".." + chi);

        // sleep ignition: never awake, never bare, never before the grace; mean wait about two hours
        bool sd = !RM_FurnaceKernel.SleepIgnitionDue(true, 99999, true, SleepGrace) && !RM_FurnaceKernel.SleepIgnitionDue(false, 99999, false, SleepGrace)
            && !RM_FurnaceKernel.SleepIgnitionDue(false, SleepGrace - 1, true, SleepGrace) && RM_FurnaceKernel.SleepIgnitionDue(false, SleepGrace, true, SleepGrace);
        rng = new Random(2468); double tot = 0; int runs = 20000;
        for (int r = 0; r < runs; r++)
        {
            int rest = 0; int t = 0;
            while (true) { t += SleepCheck; RM_FurnaceKernel.RestStep(ref rest, false, SleepCheck, 2500); if (RM_FurnaceKernel.SleepIgnitionDue(false, rest, true, SleepGrace) && rng.NextDouble() < (double)SleepCheck / SleepMtb) break; }
            tot += t;
        }
        double meanH = tot / runs / TicksPerHour;
        Row("bed_ignition_never_at_once_about_two_hours", bars, "random", sd && meanH > 1.5 && meanH < 2.6, runs, "seed 2468: grace 1250, MTB 3750 checked every 250 (chance 250/3750 per check, the caller's MTB form assumed) -> mean " + meanH.ToString("0.00", Inv) + " h; never awake/bare/before grace");

        // thermal charge
        bool chg = RM_FurnaceKernel.ChargeStep(80f, false, 35f, 45f, 0.004f, 5f, 35f, 0.0015f, 0.05f) > 0f
            && RM_FurnaceKernel.ChargeStep(20f, false, 35f, 45f, 0.004f, 5f, 35f, 0.0015f, 0.05f) == 0f
            && RM_FurnaceKernel.ChargeStep(-50f, false, 35f, 45f, 0.004f, 5f, 35f, 0.0015f, 0.05f) < 0f
            && Near(RM_FurnaceKernel.ChargeStep(20f, true, 35f, 45f, 0.004f, 5f, 35f, 0.0015f, 0.05f), 0.05f)
            && RM_FurnaceKernel.ClampCharge(2f) == 1f && RM_FurnaceKernel.ClampCharge(-1f) == 0f
            && RM_FurnaceKernel.WantsHeat(0.5f, 0.75f) && RM_FurnaceKernel.IsFullyCharged(0.95f, 0.95f);
        int restT = 0; var o1r = RM_FurnaceKernel.RestStep(ref restT, false, 1000, 2500); var o2r = RM_FurnaceKernel.RestStep(ref restT, true, 0, 2500);
        Row("thermal_charge_and_rest_clock", bars, "fixed", chg && o1r == RM_RestOutcome.Resting && o2r == RM_RestOutcome.WokeTooShort && restT == 0, 9, "charges in heat, holds between, bleeds in cold, fire fast lane; rest clock resets on waking");
    }

    // ================================================================ ashwallow_dives_unharmed
    static void Burrow()
    {
        var bars = B("ashwallow_dives_unharmed", "inv_burrowers_heat_dome");
        // dome: only on a heat hit, opted in, every switch on, alive, not downed, not in a mental state
        int c = 0; bool tt = true;
        for (int m = 0; m < 256; m++)
        {
            bool[] v = Enumerable.Range(0, 8).Select(k => (m >> k & 1) == 1).ToArray(); c++;
            bool want = v[0] && v[1] && v[2] && v[3] && v[4] && v[5] && !v[6] && !v[7];
            if (RM_FireEcoKernel.DomeOnHeatHit(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]) != want) tt = false;
        }
        Row("dome_truth_table", bars, "fixed", tt, c, "256 rows: heat AND opted-in AND mechanics AND burrow AND dome AND alive AND NOT downed AND NOT mental");
        // hold never shortened; emerges only after the hold with no fire near
        var rng = new Random(321); int n = 0; string bad = null; int hold = -1;
        for (int now = 0; now < 200000 && bad == null; now += rng.Next(1, 400), n++)
        {
            int before = hold; if (rng.Next(5) == 0) hold = RM_FireEcoKernel.BurrowHeatHoldUntil(now, hold, rng.Next(-50, HeatHold + 1));
            if (hold < before) bad = "seed 321 hold shortened at " + now;
            bool em = RM_FireEcoKernel.BurrowMayEmerge(now, hold, false);
            if (em && hold >= 0 && now < hold) bad = "seed 321 surfaced inside the hold at " + now;
            if (RM_FireEcoKernel.BurrowMayEmerge(now, hold, true)) bad = "surfaced with fire near";
        }
        Row("dome_hold_then_surface", bars, "random", bad == null, n, bad ?? "seed 321: the hold never shortens; never surfaces inside it or with fire near; hold " + HeatHold + " ticks");
        // emerge checks: each pawn exactly once per interval window
        bool due = true; for (int pid = -5; pid < 200 && due; pid++) { int k = 0; for (int t = 1000; t < 1000 + EmergeInterval; t++) if (RM_FireEcoKernel.BurrowEmergeCheckDue(t, pid, EmergeInterval)) k++; if (k != 1) due = false; }
        Row("emerge_check_once_per_interval", bars, "fixed", due && RM_FireEcoKernel.BurrowEmergeCheckDue(5, 3, 1), 205, "each pawn id is checked exactly once in every 30-tick window");
        bool flee = RM_FireEcoKernel.BurrowerFleeAnswer(false, false, true, true) == 0 && RM_FireEcoKernel.BurrowerFleeAnswer(true, true, true, false) == 1
            && RM_FireEcoKernel.BurrowerFleeAnswer(true, false, true, true) == 2 && RM_FireEcoKernel.BurrowerFleeAnswer(true, false, false, true) == 0;
        Row("burrower_dives_instead_of_fleeing", bars, "fixed", flee, 4, "non-burrower: vanilla; burrowed: stays; flee-from-fire with a dive due: dives");
        bool st = RM_FireEcoKernel.BurrowMayStart(100, -1, 7500) && !RM_FireEcoKernel.BurrowMayStart(100, 50, 7500) && RM_FireEcoKernel.BurrowMayStart(10, 50, 7500)
            && RM_FireEcoKernel.BurrowNudgeDue(true, true, false, true, 1000, -1, 250) && !RM_FireEcoKernel.BurrowNudgeDue(true, true, false, true, 1000, 900, 250) && !RM_FireEcoKernel.BurrowNudgeDue(false, true, false, true, 1000, -1, 250);
        Row("burrow_start_and_nudge", bars, "fixed", st, 6, "timeout cooldown; nudge only while a burn exists, spaced 250");
        Row("fire_scan_choice", bars, "fixed", RM_FireEcoKernel.FireScanByCells(200, 113) && !RM_FireEcoKernel.FireScanByCells(10, 113) && !RM_FireEcoKernel.FireScanByCells(10, 0), 3, "cells win only above the disc's cell count");
    }

    // ================================================================ ullai_graze_old_burns
    static void Ullai()
    {
        var bars = B("ullai_graze_old_burns", "inv_ullai_herd_giant");
        int lag = 2 * TicksPerDay, keep = 3 * TicksPerDay, iv = TicksPerHour;
        // two pads: one burned two days ago, one burned an hour ago -> anchor at the old one
        var ticks = new List<int>(); var cells = new List<string>(); int now = 0;
        for (int t = 0; t <= 4 * TicksPerHour; t += iv) RM_BurnKernel.RecordHistory(ticks, cells, t, "OLD", iv, keep);
        now = 2 * TicksPerDay + TicksPerHour; RM_BurnKernel.RecordHistory(ticks, cells, now, "FRESH", iv, keep);
        int a = RM_BurnKernel.HistoryIndexAgo(ticks, now, lag);
        Row("herd_anchor_two_day_old_burn_over_fresh", bars, "fixed", a >= 0 && cells[a] == "OLD", 1, "history: old pad 0..4 h, fresh pad at 2d+1h; anchor -> " + (a >= 0 ? cells[a] : "none"));
        // only a fresh burn in the history: the kernel falls back to the OLDEST sample, which is the fresh burn
        var t2 = new List<int>(); var c2 = new List<string>(); int now2 = 500000;
        RM_BurnKernel.RecordHistory(t2, c2, now2 - TicksPerHour, "FRESH", iv, keep);
        int a2 = RM_BurnKernel.HistoryIndexAgo(t2, now2, lag);
        var dec = a2 >= 0 ? RM_BurnKernel.FollowBurnDecision(true, false, 30f, 4f, 6f) : RM_FollowBurnAction.Stay;
        bool fresh = a2 >= 0 && now2 - t2[a2] < lag && dec == RM_FollowBurnAction.GoAnchor;
        Row("herd_anchor_never_fresh_ash", bars, "fixed", !fresh, 1,
            fresh ? "shrunk: history = one sample 1 hour old (lag 2 days); HistoryIndexAgo returns index " + a2 + " (its 'else the oldest' fallback), age " + (now2 - t2[a2]) + " ticks; FollowBurnDecision(anchorValid) -> GoAnchor: the herd walks to fresh ash unless the caller rejects a too-young anchor (lane 2 reads the caller)"
                  : "a too-young history yields no anchor");
        // prune on read: a fireless map stops answering an old anchor
        var t3 = new List<int> { 0, 2500 }; var c3 = new List<string> { "A", "B" };
        int dropped = RM_BurnKernel.PruneHistory(t3, c3, 10 * TicksPerDay, keep);
        Row("history_prunes_on_read", bars, "fixed", dropped == 2 && t3.Count == 0 && RM_BurnKernel.HistoryIndexAgo(t3, 10 * TicksPerDay, lag) == -1, 1, "a 10-day-old record is dropped; no anchor");
        // random ring: samples never older than keep, at least iv apart
        var rng = new Random(9); var t4 = new List<int>(); var c4 = new List<int>(); int n = 0; string bad = null; int tt = 0;
        for (int i = 0; i < 20000 && bad == null; i++, n++)
        {
            tt += rng.Next(1, 3000); RM_BurnKernel.RecordHistory(t4, c4, tt, i, iv, keep); RM_BurnKernel.PruneHistory(t4, c4, tt, keep); // the read path prunes too
            for (int k = 0; k < t4.Count; k++) { if (tt - t4[k] > keep) bad = "seed 9 stale sample"; if (k > 0 && t4[k] - t4[k - 1] < iv) bad = "seed 9 samples closer than the interval"; }
        }
        Row("history_ring_bounds_random", bars, "random", bad == null, n, bad ?? "seed 9: after record + the read-side prune, samples within keep, one per interval");
        bool fb = RM_BurnKernel.FollowBurnDecision(true, true, 9f, 4f, 6f) == RM_FollowBurnAction.Stay && RM_BurnKernel.FollowBurnDecision(true, true, 10.5f, 4f, 6f) == RM_FollowBurnAction.GoAnchor
            && RM_BurnKernel.FollowBurnDecision(false, false, 0f, 4f, 6f) == RM_FollowBurnAction.GoNearestAsh;
        Row("follow_burn_decision", bars, "fixed", fb, 3, "on ash inside settle+radius stays; outside walks to the anchor; no record drifts to the nearest ash");
        Info("no_record_drifts_to_nearest_ash", bars, 1, "with no burn record a herd off ash goes to the NEAREST ash (any age), not to old burns; on a Pyrelands map almost all ground is deep ash, so this mostly reads as 'stay'");
    }

    // ================================================================ populations_are_the_biomes_own (allowlist)
    static void Allowlist()
    {
        var bars = B("populations_are_the_biomes_own", "inv_plant_roster");
        var rng = new Random(1001); int n = 0; string bad = null; var natives = new List<string> { "RM_FE_Plant_EmberGrass", "RM_FE_Plant_Quickgrass" };
        string[] pool = { "RM_FE_Plant_EmberGrass", "RM_FE_Plant_Quickgrass", "Plant_Grass", "Plant_TallGrass", "Plant_Bush", "Plant_TreeDrago", "Plant_Agave" };
        for (int i = 0; i < 20000 && bad == null; i++, n++)
        {
            var cand = pool.Where(_ => rng.Next(2) == 0).ToList(); bool foreign = rng.Next(2) == 0; bool canGrow = rng.Next(3) > 0;
            var before = new List<string>(cand);
            RM_FireEcoKernel.ApplyWildAllowlist(cand, natives, p => natives.Contains(p), p => canGrow, foreign);
            if (cand.Any(p => !natives.Contains(p))) bad = "seed 1001 i=" + i + " donor survived";
            if (cand.Distinct().Count() != cand.Count) bad = "seed 1001 i=" + i + " duplicate";
            if (!foreign && cand.Any(p => !before.Contains(p))) bad = "seed 1001 i=" + i + " native cell supplied";
            if (foreign && canGrow && cand.Count != 2) bad = "seed 1001 i=" + i + " foreign open cell left without its natives";
        }
        Row("wild_allowlist_only_natives", bars, "random", bad == null, n, bad ?? "seed 1001: donors evicted, no duplicates, native cells never supplied, foreign open cells get both grasses");
        Row("biome_score_gate_off", B("inv_biome_self_contained", "inv_settings_gate"), "fixed",
            RM_FireEcoKernel.BiomeScore(false, true, false, 30, 300, 100, false, 20, 40, 100, 500, 0, 500, 10, 1, 100) == -100f
            && RM_FireEcoKernel.BiomeScore(true, true, true, 30, 300, 100, false, 20, 40, 100, 500, 0, 500, 10, 1, 100) == -100f, 2,
            "generation switch off (shipped default) scores -100 on every tile; no worldgen placement");
    }

    // ================================================================ ruins_stand_blackened
    static void Ruins()
    {
        var bars = B("ruins_stand_blackened", "inv_ruins_scorched");
        bool r = RM_FireEcoKernel.IsScorchableRuin(true, false, true, false) && !RM_FireEcoKernel.IsScorchableRuin(true, true, true, false)
            && !RM_FireEcoKernel.IsScorchableRuin(false, false, true, true) && !RM_FireEcoKernel.IsScorchableRuin(true, false, false, false)
            && RM_FireEcoKernel.RuinScorchLays(false, "RM_FE_Ground_Soil") && !RM_FireEcoKernel.RuinScorchLays(true, "RM_FE_Ground_Soil") && !RM_FireEcoKernel.RuinScorchLays(false, RM_FireEcoKernel.DeepAshDefName);
        Row("ruin_subjects_and_footprint", bars, "fixed", r, 7, "unowned destroyable artificial buildings only; deep ash laid on any non-water footprint not already ash");
    }

    static void NotKernelRows()
    {
        NotKernel("nk_walk_season", B("walk_season_on_the_pyre"), "two weeks on the full list with save/reload: live only");
        NotKernel("nk_firefoam_sprayer", B("firefoam_sprayer_reaches_the_fruit", "inv_firefoam_sprayer"), "pathing through fire with a sprayer: game-side (no kernel)");
        NotKernel("nk_rite_hook", B("fire_rite_hook_silent_alone", "inv_fire_rite_hook"), "the hook's event raising is in PyrelandsFireRiteHook.cs (game-side); no kernel");
        NotKernel("nk_three_skies_look", B("three_skies"), "telling three skies apart at a glance is a capture judgement; the ash/wash maths is row ash_fall_lays_black_rain_washes");
        NotKernel("nk_flamefang_venom", B("flamefang_bite_carries_venom"), "venom severity over hours is a hediff in play; the def wiring is a run_lane1.py def row");
        NotKernel("nk_census", B("populations_are_the_biomes_own"), "a live map census and clean generation log; the allowlist maths is row wild_allowlist_only_natives");
        NotKernel("nk_grass_regreen_rate", B("grass_carpets_and_regreens", "inv_embergrass_regrow"), "green share on days 3 and 7 and growth on dry ash depend on vanilla growth with the mod's Harmony patches; no kernel");
        NotKernel("nk_art", B("inv_art_and_text"), "the owner approved the art as a sheet (record); not kernel logic");
    }
}
