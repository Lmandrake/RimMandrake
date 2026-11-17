// Pyrelands 0.1.0, blind challenge cycle 3, lane 1: game-logic tests written from the bars alone (tree.json, sheet.md,
// record.json rows, plan.md) and the shipped settings (RM_PyrelandsMod.cs defaults and slider ranges, PyrelandsTuning.cs).
// Runs against the Verse-free kernels; prints one JSON row per line. Exit 0 = no FAIL row, 1 = a FAIL row.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.Pyrelands;

public static class BlindLane1
{
    const int Seed = 20261117;
    const int Day = 60000;
    static int fails;
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    static string J(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";

    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") fails++;
        Console.WriteLine("{\"id\": " + J(id) + ", \"bars\": [" + string.Join(", ", bars.Select(J)) + "], \"kind\": " + J(kind)
            + ", \"verdict\": " + J(verdict) + ", \"cases\": " + cases + ", \"detail\": " + J(detail) + "}");
    }

    static void Check(string id, string[] bars, string kind, int cases, List<string> bad, string passDetail, string attainable)
    {
        if (bad.Count == 0) Row(id, bars, kind, "PASS", cases, passDetail);
        else Row(id, bars, kind, "FAIL", cases, bad.Count + " bad of " + cases + "; first: " + string.Join(" | ", bad.Take(3))
            + "; would pass: " + attainable);
    }

    static Dictionary<string, string> Parse(string line)
    {
        var d = new Dictionary<string, string>();
        foreach (var part in line.Split(';'))
        {
            int i = part.IndexOf('=');
            if (i > 0) d[part.Substring(0, i)] = part.Substring(i + 1);
        }
        return d;
    }

    static bool Near(float a, float b, float eps = 1e-4f) => Math.Abs(a - b) <= eps;

    // shipped defaults (RM_PyrelandsMod.cs) and ranges (its sliders)
    const float Dry = 0.70f, Wet = 1.40f, Bonus = 0.50f, BonusDays = 6f, Cap = 2f;

    static string Probe(float fert, bool ashField, bool watered, float baseF, float wetF, float bonus, int burnTick, int now,
        float days, bool raining, bool roofed, bool active, bool waterOn, bool gateOn)
    {
        return RM_FireEcoKernel.ProbeLine(fert, "RM_FE_Ash_Deep", ashField, watered, baseF, wetF, bonus, burnTick, now, (int)(days * Day),
            raining, roofed, -1, active, waterOn, gateOn, Cap);
    }

    // the honest fertility a correct grid would hand the probe, from the bar's parts: base, the watered lift, the bonus, clamped to the cap
    static float Honest(float baseF, float wetF, bool watered, bool waterOn, float bonus)
    {
        float v = (waterOn && watered ? wetF : baseF) + Math.Max(0f, bonus);
        return Math.Max(0f, Math.Min(Cap, v));
    }

    public static int Main()
    {
        AshProbe();
        CompoundRuling();
        SettingsGateKernel();
        WindCarry();
        BurnClocks();
        FireHawk();
        HuntRewards();
        FurnaceWarmth();
        return fails > 0 ? 1 : 0;
    }

    // ------------------------------------------------------------------ ash_fertility_probe (offline)
    static void AshProbe()
    {
        string[] bars = { "ash_fertility_probe" };
        var bad = new List<string>();
        int now = 10 * Day;
        // a burned wet cell (burned half a day ago, black-rain watered) and a dry old cell (never burned)
        float bWet = RM_FireEcoKernel.BurnBonus(now - Day / 2, now, Bonus, (int)(BonusDays * Day));
        string wetLine = Probe(Honest(Dry, Wet, true, true, bWet), true, true, Dry, Wet, bWet, now - Day / 2, now, BonusDays, true, false, true, true, true);
        string dryLine = Probe(Honest(Dry, Wet, false, true, 0f), true, false, Dry, Wet, 0f, -1, now, BonusDays, false, false, true, true, true);
        var w = Parse(wetLine); var d = Parse(dryLine);
        foreach (var k in new[] { "base", "lift", "bonus", "bonusAgeDays", "rainOnCell", "watered", "fertility", "expected", "consistent" })
            if (!w.ContainsKey(k) || !d.ContainsKey(k)) bad.Add("missing part " + k);
        if (bad.Count == 0)
        {
            if (w["base"] != d["base"]) bad.Add("base differs on the same terrain: " + w["base"] + " vs " + d["base"]);
            if (w["lift"] == d["lift"]) bad.Add("watered lift reads the same wet and dry: " + w["lift"]);
            if (w["bonus"] == d["bonus"]) bad.Add("bonus reads the same burned and unburned: " + w["bonus"]);
            if (w["bonusAgeDays"] == d["bonusAgeDays"]) bad.Add("bonus age reads the same: " + w["bonusAgeDays"]);
            if (w["rainOnCell"] == d["rainOnCell"]) bad.Add("rain-on-cell reads the same: " + w["rainOnCell"]);
            if (w["consistent"] != "True" || d["consistent"] != "True") bad.Add("honest grid not consistent: " + w["consistent"] + "/" + d["consistent"]);
            if (wetLine.StartsWith("refused") || dryLine.StartsWith("refused")) bad.Add("refused with every switch on");
        }
        Check("probe_fixed_wet_burned_vs_dry_old_part_by_part", bars, "fixed", 2, bad,
            "wet burned cell: " + wetLine + " || dry old cell: " + dryLine, "each of base, lift, bonus, bonus age and rain reported per cell");

        // the false pass the bar names: a probe that hands back the base for every cell must show inconsistent on a wet or fresh cell
        bad = new List<string>();
        string fake = Probe(Dry, true, true, Dry, Wet, bWet, now - Day / 2, now, BonusDays, true, false, true, true, true);
        if (Parse(fake).GetValueOrDefault("consistent") != "False") bad.Add("base-for-every-cell grid read consistent: " + fake);
        string fakeFresh = Probe(Dry, true, false, Dry, Wet, bWet, now - Day / 2, now, BonusDays, false, false, true, true, true);
        if (Parse(fakeFresh).GetValueOrDefault("consistent") != "False") bad.Add("base grid on a dry fresh cell read consistent: " + fakeFresh);
        Check("probe_fixed_false_pass_base_for_every_cell_caught", bars, "fixed", 2, bad,
            "a grid returning base fertility for every cell reads consistent=False on a wet cell and on a dry fresh cell", "consistent=False on such a grid");

        // refuses when the ash-field switch is off, and when the mechanics gate is off; still lists the parts
        bad = new List<string>();
        string offWater = Probe(Dry, true, true, Dry, Wet, bWet, now - Day / 2, now, BonusDays, true, false, true, false, true);
        string offGate = Probe(Dry, true, true, Dry, Wet, bWet, now - Day / 2, now, BonusDays, true, false, true, true, false);
        string onAll = Probe(Honest(Dry, Wet, true, true, bWet), true, true, Dry, Wet, bWet, now - Day / 2, now, BonusDays, true, false, true, true, true);
        if (!offWater.StartsWith("refused=")) bad.Add("ash field off, not refused: " + offWater);
        if (!offGate.StartsWith("refused=")) bad.Add("mechanics gate off, not refused: " + offGate);
        if (onAll.StartsWith("refused=")) bad.Add("refused with the switches on");
        foreach (var l in new[] { offWater, offGate }) if (!Parse(l).ContainsKey("base") || !Parse(l).ContainsKey("bonus")) bad.Add("refusal drops the parts: " + l);
        foreach (var l in new[] { offWater, offGate })
        {
            string r = Parse(l).GetValueOrDefault("refused", "");
            if (r.Length < 10) bad.Add("refusal carries no reason: " + l);
        }
        Check("probe_fixed_refuses_with_reason_when_ash_field_off", bars, "fixed", 3, bad,
            "ash field off: " + offWater.Split(';')[0] + " | gate off: " + offGate.Split(';')[0], "refused=<reason> when ashWaterFertilityEnabled or the gate is off");

        // random: parts add up (nothing created or lost), consistency flag, rain on cell, days left in range
        var rng = new Random(Seed);
        bad = new List<string>();
        int n = 20000; string firstBad = null;
        for (int i = 0; i < n; i++)
        {
            float baseF = (float)rng.NextDouble();            // slider 0..1
            float wetF = 0.4f + 1.6f * (float)rng.NextDouble(); // slider 0.4..2
            float bset = 1.5f * (float)rng.NextDouble();       // slider 0..1.5
            float days = 1f + 19f * (float)rng.NextDouble();   // slider 1..20
            int t = Day * 30 + rng.Next(0, Day * 30);
            int burn = rng.Next(4) == 0 ? -1 : t - rng.Next(0, (int)(days * Day * 1.5f));
            bool watered = rng.Next(2) == 0, raining = rng.Next(2) == 0, roofed = rng.Next(4) == 0;
            bool active = rng.Next(8) != 0, waterOn = rng.Next(8) != 0, gateOn = rng.Next(8) != 0, ash = rng.Next(8) != 0;
            float b = RM_FireEcoKernel.BurnBonus(burn, t, bset, (int)(days * Day));
            float honest = Honest(baseF, wetF, watered, waterOn, b);
            string line = Probe(honest, ash, watered, baseF, wetF, b, burn, t, days, raining, roofed, active, waterOn, gateOn);
            var p = Parse(line);
            string why = null;
            float lift = float.Parse(p["lift"], Inv), exp = float.Parse(p["expected"], Inv), bon = float.Parse(p["bonus"], Inv), bas = float.Parse(p["base"], Inv);
            float sum = Math.Max(0f, Math.Min(Cap, bas + lift + bon));
            if (!Near(sum, exp, 2e-3f)) why = "parts do not add to expected: base+lift+bonus=" + sum + " expected=" + exp;
            else if (!Near(exp, honest, 2e-3f)) why = "expected " + exp + " != honest " + honest;
            else if ((waterOn && watered) != (Math.Abs(lift - (wetF - baseF)) < 2e-3f && p["watered"] == "True")) why = "lift/watered wrong: " + line;
            else if ((p["rainOnCell"] == "True") != (raining && !roofed)) why = "rainOnCell wrong: " + line;
            else
            {
                float left = float.Parse(p["bonusDaysLeft"], Inv);
                if (left < 0f || left > days + 0.01f) why = "days left out of range " + left;
                bool want = gateOn && waterOn && ash && active;
                string c = p["consistent"];
                if (want && c != "True") why = "honest grid read " + c + ": " + line;
                if (!want && c != "n/a") why = "consistency judged while refused/inactive: " + line;
                if ((!gateOn || !waterOn) != line.StartsWith("refused=")) why = "refusal does not follow the switches: " + line;
            }
            if (why != null) { bad.Add("case " + i + ": " + why); if (firstBad == null) firstBad = why; }
        }
        Check("probe_random_parts_add_up_and_flags_follow_switches", bars, "random", n, bad,
            "seed " + Seed + ": base+lift+bonus (clamped to cap 2) equals expected and the honest fertility in every case; lift only when wet and the switch on; rainOnCell = black rain and unroofed; consistent only judged with gate, switch, ash field and component on",
            "parts that add to the fertility, flags that follow the switches");

        // info: the probe's days-left part keeps counting when the bonus itself is switched off (the caller passes bonus 0)
        string offBonus = Probe(Dry, true, false, Dry, Wet, 0f, now - Day, now, BonusDays, false, false, true, true, true);
        Row("probe_info_days_left_with_bonus_off", bars, "info", "INFO", 1,
            "bonus switched off (bonus=0 passed) on a cell burned a day ago reads " + string.Join(";", offBonus.Split(';').Where(s => s.StartsWith("bonus")))
            + ": bonusDaysLeft is the clock, not the bonus, so a tester could read a live bonus that is not there; the bar asks for 'the fresh-burn bonus and its age', which both still read right");
    }

    // ------------------------------------------------------------------ fresh_burn_compounds_with_black_rain / ash_fertile_when_watered (stage 6, kernel half)
    static void CompoundRuling()
    {
        string[] bars = { "fresh_burn_compounds_with_black_rain", "ash_fertile_when_watered" };
        var bad = new List<string>();
        int dur = (int)(BonusDays * Day);
        float b0 = RM_FireEcoKernel.BurnBonus(0, 0, Bonus, dur);
        float wetFresh = RM_FireEcoKernel.AshFertility(Dry, Wet, true, true, b0, Cap);
        float dryFresh = RM_FireEcoKernel.AshFertility(Dry, Wet, false, true, b0, Cap);
        float wetOld = RM_FireEcoKernel.AshFertility(Dry, Wet, true, true, 0f, Cap);
        float dryOld = RM_FireEcoKernel.AshFertility(Dry, Wet, false, true, 0f, Cap);
        if (!Near(wetFresh, 1.9f, 0.01f)) bad.Add("wet fresh scar " + wetFresh + " (bar about 190%)");
        if (!Near(dryFresh, 1.2f, 0.01f)) bad.Add("dry fresh scar " + dryFresh + " (bar about 120%)");
        if (!Near(wetOld, 1.4f, 0.01f)) bad.Add("wet old ash " + wetOld + " (bar about 140%)");
        if (!Near(dryOld, 0.7f, 0.01f)) bad.Add("dry old ash " + dryOld + " (bar about 70%)");
        float d6 = RM_FireEcoKernel.BurnBonus(0, 6 * Day, Bonus, dur), d7 = RM_FireEcoKernel.BurnBonus(0, 7 * Day, Bonus, dur), d3 = RM_FireEcoKernel.BurnBonus(0, 3 * Day, Bonus, dur);
        if (d6 > 0f || d7 > 0f) bad.Add("bonus not gone by day 6-7: " + d6 + "/" + d7);
        if (!(d3 > 0f && d3 < b0)) bad.Add("bonus not fading mid-clock: day3 " + d3);
        Check("compound_fixed_shipped_numbers", bars, "fixed", 8, bad,
            "shipped settings: wet fresh " + wetFresh + ", dry fresh " + dryFresh + ", wet old " + wetOld + ", dry old " + dryOld + "; bonus day 3 " + d3 + ", day 6 " + d6,
            "190/120/140/70 at the shipped settings, bonus 0 by day 6-7");

        // sweep the shipped ranges: ordering wet fresh >= max(dry fresh, wet old); never negative, never above cap; bonus monotone non-increasing; 0 at its own days
        bad = new List<string>(); int cases = 0, belowDry = 0;
        for (float dry = 0f; dry <= 1.0001f; dry += 0.1f)
            for (float wet = 0.4f; wet <= 2.0001f; wet += 0.2f)
                for (float bonus = 0f; bonus <= 1.5001f; bonus += 0.25f)
                    for (float days = 1f; days <= 20.0001f; days += 3.8f)
                    {
                        cases++;
                        int du = (int)(days * Day);
                        float prev = float.MaxValue;
                        for (int t = 0; t <= du + Day; t += Day / 4)
                        {
                            float bb = RM_FireEcoKernel.BurnBonus(0, t, bonus, du);
                            if (bb > prev + 1e-6f) { bad.Add("bonus rose at t=" + t + " bonus=" + bonus + " days=" + days); break; }
                            if (bb < 0f || bb > bonus + 1e-6f) { bad.Add("bonus out of [0,setting] " + bb); break; }
                            prev = bb;
                        }
                        if (RM_FireEcoKernel.BurnBonus(0, du, bonus, du) != 0f) bad.Add("bonus not 0 at its own end, days=" + days);
                        float bb0 = RM_FireEcoKernel.BurnBonus(0, 0, bonus, du);
                        float wf = RM_FireEcoKernel.AshFertility(dry, wet, true, true, bb0, Cap), df = RM_FireEcoKernel.AshFertility(dry, wet, false, true, bb0, Cap);
                        float wo = RM_FireEcoKernel.AshFertility(dry, wet, true, true, 0f, Cap);
                        // compounding = the bonus survives the rain: wet fresh - wet old is the whole bonus, short only by the cap
                        // (a first form also asked wet fresh >= dry fresh, which a player who sets watered below dry breaks by choice)
                        if (!Near(wf - wo, Math.Min(bb0, Math.Max(0f, Cap - wo)), 1e-4f)) bad.Add("rain took bonus: dry=" + dry + " wet=" + wet + " bonus=" + bonus + " wf=" + wf + " wo=" + wo);
                        if (wet >= dry && (wf + 1e-5f < df)) bad.Add("wet fresh below dry fresh with watered >= dry: dry=" + dry + " wet=" + wet);
                        if (wet < dry) belowDry++;
                        foreach (var v in new[] { wf, df, wo }) if (v < 0f || v > Cap + 1e-6f) bad.Add("fertility out of [0,cap] " + v);
                        // the watered switch off: watered reads dry
                        if (!Near(RM_FireEcoKernel.AshFertility(dry, wet, true, false, 0f, Cap), Math.Min(Cap, dry))) bad.Add("water switch off still lifts");
                    }
        Check("compound_sweep_shipped_ranges", bars, "sweep", cases, bad,
            "dry 0..1, watered 0.4..2, bonus 0..1.5, days 1..20: rain never takes the bonus (wet fresh - wet old is the whole bonus, short only by the cap 2; wet fresh >= dry fresh wherever watered >= dry), bonus fades monotonically to 0 on its own clock, fertility in [0, 2]",
            "compounding at every setting");
        Row("compound_info_watered_slider_can_sit_below_dry", bars, "info", "INFO", cases,
            belowDry + " of " + cases + " swept setting pairs put 'Water makes deep ash fertile' (0.4..2) below dry fertility (0..1), so water makes ash LESS fertile there; the shipped pair (0.70, 1.40) is right and the bonus still compounds; a player's own choice, Polish at most");

        // wet roots: on watered ash the heat growth season opens where the dry cell's is shut, never shut where dry is open; cold side unchanged
        bad = new List<string>(); var rng = new Random(Seed + 1); int m = 5000;
        for (int i = 0; i < m; i++)
        {
            float minG = (float)(rng.NextDouble() * 10), maxG = minG + 20 + (float)rng.NextDouble() * 30, T = -20 + (float)rng.NextDouble() * 100;
            float cool = (float)rng.NextDouble() * 30;
            bool dry = T > minG && T < maxG, wetS = RM_FireEcoKernel.WetRootGrowthSeason(T, minG, maxG, cool);
            if (dry && !wetS) bad.Add("wet roots shut an open season T=" + T + " min=" + minG + " max=" + maxG + " cool=" + cool);
            if (T <= minG && wetS) bad.Add("wet roots warmed a cold cell T=" + T);
            float rt = RM_FireEcoKernel.WetRootTemperature(T, cool);
            if (rt > T) bad.Add("roots warmer than the cell");
        }
        float hot = 53.6f; // the biome's median named in PyrelandsTuning.WetRootsCoolingC
        bool opens = RM_FireEcoKernel.WetRootGrowthSeason(hot + 5, 6f, 58f, 15f) && !(hot + 5 > 6f && hot + 5 < 58f);
        if (!opens) bad.Add("at 58.6 C a 6..58 crop's season does not open on wet roots");
        Check("wet_roots_random_season_opens_never_shuts", bars, "random", m + 1, bad,
            "seed " + (Seed + 1) + ": watered ash only opens a heat-shut season, never shuts an open one or warms a cold cell; at 58.6 C a 6..58 C crop opens",
            "cooler roots on watered ash only");
    }

    // ------------------------------------------------------------------ inv_settings_gate (offline), kernel half
    static void SettingsGateKernel()
    {
        string[] bars = { "inv_settings_gate" };
        var bad = new List<string>();
        foreach (bool m in new[] { false, true })
            foreach (bool p in new[] { false, true })
                foreach (bool s in new[] { false, true })
                {
                    bool want = m && (!p || s);
                    if (RM_FireEcoKernel.MechanicsOn(m, p, s) != want) bad.Add("MechanicsOn(" + m + "," + p + "," + s + ")");
                }
        Check("gate_fixed_truth_table", bars, "fixed", 8, bad, "Mod enabled AND (shell absent OR its Pyrelands toggle)", "master AND roster toggle");

        // every gated decision reads its off value with the gate off or its own switch off
        bad = new List<string>(); int c = 0;
        void Off(string what, bool isOff) { c++; if (!isOff) bad.Add(what); }
        Off("black rain douse with gate off", RM_FireEcoKernel.BlackRainDouseAmount(false, true, 40f, 1f, true) == 0f);
        Off("black rain douse with its switch off", RM_FireEcoKernel.BlackRainDouseAmount(true, false, 40f, 1f, true) == 0f);
        Off("black rain douse at slider 0", RM_FireEcoKernel.BlackRainDouseAmount(true, true, 0f, 1f, true) == 0f);
        Off("rain becomes black rain with gate off", !RM_FireEcoKernel.RainBecomesBlackRain("Rain", true, false));
        Off("rain becomes black rain off the biome", !RM_FireEcoKernel.RainBecomesBlackRain("Rain", false, true));
        Off("dome on heat hit with mechanics off", !RM_FireEcoKernel.DomeOnHeatHit(true, true, false, true, true, true, false, false));
        Off("dome on heat hit with burrow off", !RM_FireEcoKernel.DomeOnHeatHit(true, true, true, false, true, true, false, false));
        Off("dome on heat hit with dome switch off", !RM_FireEcoKernel.DomeOnHeatHit(true, true, true, true, false, true, false, false));
        Off("fire tick rolls with master off", !RM_FireEcoKernel.FireTickMayRoll(false, true, true, true, false, true));
        Off("fire tick rolls with ash and fruit off", !RM_FireEcoKernel.FireTickMayRoll(true, false, false, true, false, true));
        Off("burn stamp with master off", !RM_FireEcoKernel.BurnStampMay(false, true, true, false, true));
        Off("burn stamp with bonus off", !RM_FireEcoKernel.BurnStampMay(true, false, true, false, true));
        Off("biome scores with generation off", RM_FireEcoKernel.BiomeScore(false, true, false, 30f, 800f, 100f, false, 0f, 60f, 0f, 3000f, 0f, 3000f, 10f, 1f, 100f) == -100f);
        Off("opening front with fire clock off", RM_BurnKernel.OpeningFront(false, false, 0, 2500) == RM_OpeningAction.Skip);
        int nf = 500; Off("front clock fires with switch off", RM_BurnKernel.FrontTick(ref nf, 1000, false, () => 10) == RM_FrontAction.Disabled && nf == -1);
        Off("wind carries with switch off", !RM_BurnKernel.WindCarryDue(false, true, true, false, 5000));
        Off("vanilla spread stops with wind switch off", RM_BurnKernel.VanillaSpreadRuns(false, true, true));
        Off("tribes incident with gate off", !RM_BurnKernel.TribesIncidentSwitchesOn(true, false, true, true));
        Off("tribes incident with burn line off", !RM_BurnKernel.TribesIncidentSwitchesOn(true, true, false, true));
        Off("tribes incident with fire clock off", !RM_BurnKernel.TribesIncidentSwitchesOn(true, true, true, false));
        bool ann = false;
        Off("hawk letter with letter switch off", !RM_FireHawkRewardsKernel.TryClaimSighting(ref ann, false, true, true, true, false) && !ann);
        Off("hawk letter with mechanics off", !RM_FireHawkRewardsKernel.TryClaimSighting(ref ann, true, false, true, true, false) && !ann);
        Off("furnace warmth at strength 0", FurnaceWarmthMath.Offset(0f, 4.9f, 14f, 0f) == 0f);
        RM_FireEcoKernel.SplitClear(30f, false, 1f, out float dr, out float cl);
        Off("ash drift with ambient off", dr == 0f && cl == 30f);
        Off("trophy at chance 0", !RM_FireHawkRewardsKernel.TrophyDrops(0f, 0f));
        Off("black rain water at hours 0", !RM_FireEcoKernel.BlackRainWaters(1000000, 10, 0f, false));
        Off("cross biome off", !RM_FireEcoKernel.CrossBiomeApplies(false, true, false, true, true));
        Check("gate_fixed_every_switch_off_reads_off", bars, "sweep", c, bad,
            "each switch off (and the master gate off) turns its decision off: black rain dousing/conversion, dome, fire-tick rolls, burn stamp, worldgen score, opening front, fire clock, wind carry (vanilla spread returns), tribes incidents, hawk letter, warmth, ash drift, trophy, black-rain water, cross-biome",
            "every switch off, its mechanic off");

        // conservation: the clear-weather split loses or makes no weight, at every share and both states
        bad = new List<string>(); var rng = new Random(Seed + 2); int n = 5000;
        for (int i = 0; i < n; i++)
        {
            float wgt = (float)rng.NextDouble() * 50f, sh = -0.5f + (float)rng.NextDouble() * 2f; bool on = rng.Next(2) == 0;
            RM_FireEcoKernel.SplitClear(wgt, on, sh, out float a, out float b);
            if (!Near(a + b, wgt, 1e-3f) || a < 0f || b < -1e-5f) bad.Add("split " + wgt + " share " + sh + " on " + on + " -> " + a + "+" + b);
        }
        Check("gate_random_clear_split_conserves_weight", bars, "random", n, bad, "seed " + (Seed + 2) + ": AshDrift + Clear = the biome's old Clear weight at any share, on or off", "split conserves weight");
    }

    // ------------------------------------------------------------------ burn_line_walks (changed bar, stage 6): the wind-carry kernel
    static void WindCarry()
    {
        string[] bars = { "burn_line_walks" };
        var rng = new Random(Seed + 3);
        var bad = new List<string>(); int n = 20000; int reach = RM_BurnKernel.WindCarryReach;
        for (int i = 0; i < n; i++)
        {
            float b = (float)(rng.NextDouble() * 720 - 360);
            int[] dx = new int[3 * reach], dz = new int[3 * reach];
            RM_BurnKernel.WindProbes(b, (float)rng.NextDouble(), (float)rng.NextDouble(), reach, dx, dz);
            double rad = b * Math.PI / 180.0; float wx = (float)Math.Sin(rad), wz = (float)Math.Cos(rad);
            var seen = new HashSet<long>();
            for (int k = 0; k < dx.Length; k++)
            {
                float along = dx[k] * wx + dz[k] * wz;
                if (along <= 0f) { bad.Add("probe sideways/back: bearing " + b + " (" + dx[k] + "," + dz[k] + ")"); break; }
                if (!RM_BurnKernel.Downwind(dx[k], dz[k], wx, wz)) { bad.Add("probe outside Downwind cone: bearing " + b + " (" + dx[k] + "," + dz[k] + ")"); break; }
                if (Math.Max(Math.Abs(dx[k]), Math.Abs(dz[k])) > reach) { bad.Add("probe past reach"); break; }
                if (!seen.Add(((long)dx[k] << 32) ^ (uint)dz[k])) { bad.Add("duplicate probe bearing " + b); break; }
            }
        }
        Check("wind_random_probes_downwind_only", bars, "random", n, bad,
            "seed " + (Seed + 3) + ": every probe at any bearing is downwind (along > 0), inside the 67.5-degree cone the warning reads, within reach " + reach + ", distinct",
            "never sideways, never back");

        // mean heading of the first probe equals the wind (INFO: report the bias)
        double worst = 0; float worstB = 0;
        for (float b = 0; b < 360; b += 1f)
        {
            double sx = 0, sz = 0; var r2 = new Random(Seed + 4);
            for (int i = 0; i < 4000; i++)
            {
                int[] dx = new int[3], dz = new int[3];
                RM_BurnKernel.WindProbes(b, (float)r2.NextDouble(), (float)r2.NextDouble(), 1, dx, dz);
                sx += dx[0]; sz += dz[0];
            }
            double h = Math.Atan2(sx, sz) * 180 / Math.PI; if (h < 0) h += 360;
            double err = Math.Abs(((h - b) + 540) % 360 - 180);
            if (err > worst) { worst = err; worstB = b; }
        }
        Row("wind_info_mean_heading_bias", bars, "info", worst <= 10 ? "INFO" : "FAIL", 360,
            "seed " + (Seed + 4) + ": the vector mean of the first carry probe departs from the wind by at most " + worst.ToString("0.0", Inv) + " degrees (worst at bearing " + worstB
            + "); diagonal steps are longer than straight ones, so the angle mean is the wind and the vector mean leans to the diagonals; a natural grass fire is not harmed by this");

        // a front line lit across the wind: exactly width distinct cells, 8-adjacent, abreast (little along-wind spread)
        bad = new List<string>(); int m = 5000;
        for (int i = 0; i < m; i++)
        {
            float wind = (float)(rng.NextDouble() * 360);
            int width = rng.Next(1, 40);
            RM_BurnKernel.FrontLine(RM_BurnKernel.AcrossWind(wind), width, out int[] dx, out int[] dz);
            if (dx.Length != width) { bad.Add("width " + width + " gave " + dx.Length); continue; }
            var set = new HashSet<long>();
            double rad = wind * Math.PI / 180.0; double wx = Math.Sin(rad), wz = Math.Cos(rad);
            for (int k = 0; k < width; k++)
            {
                if (!set.Add(((long)dx[k] << 32) ^ (uint)dz[k])) { bad.Add("duplicate cell wind " + wind + " width " + width); break; }
                if (k > 0 && Math.Max(Math.Abs(dx[k] - dx[k - 1]), Math.Abs(dz[k] - dz[k - 1])) != 1) { bad.Add("gap in line wind " + wind); break; }
                if (Math.Abs(dx[k] * wx + dz[k] * wz) > 1.01) { bad.Add("line not abreast of wind " + wind + ": cell (" + dx[k] + "," + dz[k] + ") along " + (dx[k] * wx + dz[k] * wz).ToString("0.00", Inv)); break; }
            }
        }
        Check("wind_random_front_line_abreast", bars, "random", m, bad, "seed " + (Seed + 3) + ": FrontLine(AcrossWind(w), n) is n distinct 8-adjacent cells within one cell of the line across the wind", "a line abreast");

        // carried once, at its age; never twice
        bad = new List<string>();
        if (RM_BurnKernel.WindCarryDue(true, true, true, false, RM_BurnKernel.WindCarryTicks - 1)) bad.Add("carried before its age");
        if (!RM_BurnKernel.WindCarryDue(true, true, true, false, RM_BurnKernel.WindCarryTicks)) bad.Add("not carried at its age");
        if (RM_BurnKernel.WindCarryDue(true, true, true, true, 99999)) bad.Add("carried twice");
        if (RM_BurnKernel.WindCarryDue(true, false, true, false, 99999)) bad.Add("a burning pawn/thing carried");
        if (RM_BurnKernel.WindCarryDue(true, true, false, false, 99999)) bad.Add("carried off Pyrelands ground");
        if (RM_BurnKernel.VanillaSpreadRuns(true, true, true)) bad.Add("vanilla spread still runs where the wind carries");
        if (!RM_BurnKernel.VanillaSpreadRuns(true, true, false)) bad.Add("vanilla spread stopped off Pyrelands ground");
        Check("wind_fixed_carry_once_at_age", bars, "fixed", 7, bad, "carry due once at " + RM_BurnKernel.WindCarryTicks + " ticks, only free-standing on Pyrelands ground; vanilla spread runs everywhere else", "one carry per fire");

        // whole-front model on open grass: each fire, at its age, lights the first unburnt grass probe; conservation and motion
        Sim("wind_sim_open_grass", bars, 1.0, rng);
        Sim("wind_sim_patchy_grass_70pct", bars, 0.7, rng);
    }

    // toy map: 300 x 300, fuel density `dens`, wind random; front of FireFrontWidthCells across it in the middle; steps of WindCarryTicks
    static void Sim(string id, string[] bars, double dens, Random rng)
    {
        int S = 300, width = 24, trials = 20; var bad = new List<string>(); var info = new StringBuilder();
        int reach = RM_BurnKernel.WindCarryReach; int outSteps = 0, trialsOut = 0; double meanAdvance = 0, meanArea = 0;
        for (int t = 0; t < trials; t++)
        {
            int seed = rng.Next(); var r = new Random(seed);
            float wind = (float)(r.NextDouble() * 360); double rad = wind * Math.PI / 180.0; double wx = Math.Sin(rad), wz = Math.Cos(rad);
            bool[] fuel = new bool[S * S], burnt = new bool[S * S];
            for (int i = 0; i < fuel.Length; i++) fuel[i] = r.NextDouble() < dens;
            int ox = S / 2 - (int)(wx * 100), oz = S / 2 - (int)(wz * 100);
            RM_BurnKernel.FrontLine(RM_BurnKernel.AcrossWind(wind), width, out int[] lx, out int[] lz);
            var fires = new List<int>();
            for (int k = 0; k < width; k++) { int x = ox + lx[k], z = oz + lz[k]; int c = z * S + x; fires.Add(c); burnt[c] = true; fuel[c] = false; }
            int area = fires.Count; double startAlong = fires.Average(c => (c % S) * wx + (c / S) * wz);
            int steps = 0; double lastAlong = startAlong;
            for (steps = 0; steps < 200 && fires.Count > 0; steps++)
            {
                var next = new List<int>();
                foreach (int c in fires)
                {
                    int x = c % S, z = c / S; int[] dx = new int[3 * reach], dz = new int[3 * reach];
                    RM_BurnKernel.WindProbes(wind, (float)r.NextDouble(), (float)r.NextDouble(), reach, dx, dz);
                    for (int k = 0; k < dx.Length; k++)
                    {
                        int nx = x + dx[k], nz = z + dz[k]; if (nx < 0 || nz < 0 || nx >= S || nz >= S) break;
                        int nc = nz * S + nx; if (!fuel[nc]) continue;
                        fuel[nc] = false; burnt[nc] = true; next.Add(nc); break;
                    }
                }
                if (next.Count > fires.Count) bad.Add("trial seed " + seed + ": " + next.Count + " fires from " + fires.Count + " (a fire made two)");
                area += next.Count; fires = next;
                if (fires.Count > 0) lastAlong = fires.Average(c => (c % S) * wx + (c / S) * wz);
            }
            int burntCount = burnt.Count(b => b);
            if (burntCount != area) bad.Add("seed " + seed + ": burnt cells " + burntCount + " != fires lit " + area + " (created or lost)");
            if (fires.Count == 0) { trialsOut++; outSteps += steps; }
            meanAdvance += (lastAlong - startAlong) / trials; meanArea += area / (double)trials;
        }
        double cellsPerDay = meanAdvance / 200.0 * (60000.0 / RM_BurnKernel.WindCarryTicks);
        info.Append("dens " + dens + ", " + trials + " trials of 200 carries (" + (200 * RM_BurnKernel.WindCarryTicks / 60000.0).ToString("0.0", Inv) + " days): mean advance "
            + meanAdvance.ToString("0.0", Inv) + " cells downwind (" + cellsPerDay.ToString("0", Inv) + " cells/day while alive), mean area " + meanArea.ToString("0", Inv)
            + " cells; " + trialsOut + " of " + trials + " fronts went out, after " + (trialsOut > 0 ? (outSteps / (double)trialsOut).ToString("0", Inv) : "-") + " carries on average");
        if (bad.Count > 0) Row(id, bars, "random", "FAIL", trials, string.Join(" | ", bad.Take(3)) + "; " + info);
        else Row(id, bars, "random", "PASS", trials, "conservation: every burnt cell is a lit fire, no fire makes two, no cell burns twice; motion: " + info);
    }

    // ------------------------------------------------------------------ inv_burn_line_fire_clock / burn_line_walks: the clocks
    static void BurnClocks()
    {
        string[] bars = { "inv_burn_line_fire_clock", "burn_line_walks" };
        var bad = new List<string>(); var rng = new Random(Seed + 5); int n = 5000;
        for (int i = 0; i < n; i++)
        {
            int t = RM_BurnKernel.ScheduleTicks(PyrelandsTuning.FireFrontMinDays, PyrelandsTuning.FireFrontMaxDays, (float)rng.NextDouble(), Day);
            if (t < 2 * Day || t > 4 * Day) bad.Add("front in " + t / (float)Day + " days");
        }
        // keep-alive: quiet for StandingBurnQuietTicks, then a reseed, retried no faster than the retry interval
        int since = 0, iv = PyrelandsTuning.BurnWatchIntervalTicks, first = -1, last = -999999, attempts = 0;
        for (int now = 0; now < 4 * Day; now += iv)
        {
            var d = RM_BurnKernel.KeepAlive(0, ref since, iv, PyrelandsTuning.StandingBurnQuietTicks, now, last, PyrelandsTuning.StandingBurnRetryTicks);
            if (d == RM_ReseedDecision.Reseed) { if (first < 0) first = now; if (now - last < PyrelandsTuning.StandingBurnRetryTicks) bad.Add("retry too soon"); last = now; attempts++; }
        }
        if (first < 0 || first > PyrelandsTuning.StandingBurnQuietTicks + iv) bad.Add("no reseed within the quiet window: first " + first);
        int s2 = 5000; if (RM_BurnKernel.KeepAlive(3, ref s2, iv, 1, 0, -99999, 1) != RM_ReseedDecision.FiresPresent || s2 != 0) bad.Add("fires present did not reset the quiet clock");
        Check("clock_random_front_every_two_to_four_days_and_keepalive", bars, "random", n + 2, bad,
            "seed " + (Seed + 5) + ": the next front in [2, 4] days ('every few days'); a fireless map first reseeds at tick " + first + " (" + (first / (float)Day).ToString("0.00", Inv) + " days quiet) and retries every "
            + PyrelandsTuning.StandingBurnRetryTicks + " ticks (" + attempts + " attempts in 4 days); lit cells must be lawful (not home, >= " + PyrelandsTuning.StandingBurnMinDistFromColony + " from the colony)",
            "fronts every few days and a relight after a quiet spell");
        bad = new List<string>();
        if (RM_BurnKernel.LawfulBurnCell(true, false, false, 1f, true, true)) bad.Add("lights in the home area");
        if (RM_BurnKernel.LawfulBurnCell(true, false, false, 1f, false, false)) bad.Add("lights near the colony");
        if (RM_BurnKernel.LawfulBurnCell(true, false, true, 1f, false, true)) bad.Add("lights under a roof");
        if (!RM_BurnKernel.LawfulBurnCell(true, false, false, 1f, false, true)) bad.Add("refuses open grass");
        Check("clock_fixed_relight_in_open_grass_never_in_colony", new[] { "burn_line_walks" }, "fixed", 4, bad,
            "the biome lights only open, unroofed, unfogged, burnable cells outside home and away from the colony (bar: 'a fire that lights inside the colony' is a red)", "lawful cells only");
    }

    // ------------------------------------------------------------------ firehawk_lights_ahead (stage 6), kernel half
    static void FireHawk()
    {
        string[] bars = { "firehawk_lights_ahead" };
        var bad = new List<string>(); var rng = new Random(Seed + 6); int n = 400; int bucket = PyrelandsTuning.FireHawkFuelBucket;
        for (int i = 0; i < n; i++)
        {
            int sx = rng.Next(40, 200), sz = rng.Next(40, 200);
            double dens = rng.NextDouble();
            bool[] f = new bool[sx * sz], fire = new bool[sx * sz];
            for (int k = 0; k < f.Length; k++) { f[k] = rng.NextDouble() < dens * (k % 7 == 0 ? 0.2 : 1); if (rng.NextDouble() < 0.01) { fire[k] = true; f[k] = false; } }
            Func<int, int, bool> fc = (x, z) => f[z * sx + x];
            int[] fuel = RM_FireHawkKernel.BucketFuel(sx, sz, bucket, fc);
            var fireCells = new List<int>(); for (int k = 0; k < fire.Length; k++) if (fire[k]) fireCells.Add(k);
            bool[] fb = RM_FireHawkKernel.FireBuckets(sx, sz, bucket, fireCells);
            int srcX = rng.Next(sx), srcZ = rng.Next(sz);
            int c = RM_FireHawkKernel.PickDrop(sx, sz, bucket, fuel, fb, srcX, srcZ, fc, (x, z) => true, 5);
            int bw = RM_FireHawkKernel.BucketsAlong(sx, bucket), bh = RM_FireHawkKernel.BucketsAlong(sz, bucket);
            // the best lawful target: any fuelled bucket with no burning bucket in its 3x3
            bool anyCand = false; int bestScore = -1;
            for (int bz = 0; bz < bh; bz++) for (int bx = 0; bx < bw; bx++)
                {
                    if (fuel[bz * bw + bx] <= 0) continue; bool burning = false; int sum = 0;
                    for (int az = Math.Max(0, bz - 1); az <= Math.Min(bh - 1, bz + 1); az++) for (int ax = Math.Max(0, bx - 1); ax <= Math.Min(bw - 1, bx + 1); ax++) { burning |= fb[az * bw + ax]; sum += fuel[az * bw + ax]; }
                    if (!burning) { anyCand = true; bestScore = Math.Max(bestScore, sum); }
                }
            if (anyCand && c < 0) { bad.Add("case " + i + ": fuel to carry to, none chosen"); continue; }
            if (!anyCand && c >= 0) { bad.Add("case " + i + ": chose a cell with no lawful bucket"); continue; }
            if (c < 0) continue;
            int cx = c % sx, cz = c / sx;
            if (!f[c]) bad.Add("case " + i + ": drop on no fuel");
            if (fire[c]) bad.Add("case " + i + ": drop into the fire");
            int b = (cz / bucket) * bw + cx / bucket; int s = 0;
            for (int az = Math.Max(0, cz / bucket - 1); az <= Math.Min(bh - 1, cz / bucket + 1); az++) for (int ax = Math.Max(0, cx / bucket - 1); ax <= Math.Min(bw - 1, cx / bucket + 1); ax++) s += fuel[az * bw + ax];
            if (s != bestScore) bad.Add("case " + i + ": chose score " + s + " not the best " + bestScore);
        }
        Check("hawk_random_drop_goes_to_largest_unburnt_fuel", bars, "random", n, bad,
            "seed " + (Seed + 6) + ": the ember goes to the most-fuelled unburnt patch anywhere on the map (plan.md, owner 2026-11-13), onto fuel, never into a burning patch; none when no lawful patch",
            "the largest unburnt fuel");
        bad = new List<string>();
        if (!RM_FireHawkKernel.FireInScan(30, 40, PyrelandsTuning.FireHawkScanRadius)) bad.Add("fire 50 cells off not seen at scan 54");
        if (RM_FireHawkKernel.FireInScan(40, 40, PyrelandsTuning.FireHawkScanRadius)) bad.Add("fire 56.6 cells off seen at scan 54");
        Check("hawk_fixed_scan_radius", bars, "fixed", 2, bad, "a hawk sees fire within its scan radius " + PyrelandsTuning.FireHawkScanRadius + " (x3 the old 18, owner 2026-11-13) and not beyond", "the ruled scan");
    }

    // ------------------------------------------------------------------ inv_firehawk_hunt_rewards (stage 6), kernel half
    static void HuntRewards()
    {
        string[] bars = { "inv_firehawk_hunt_rewards" };
        var bad = new List<string>(); var rng = new Random(Seed + 7);
        bool ann = false; int sent = 0;
        for (int i = 0; i < 10000; i++)
            if (RM_FireHawkRewardsKernel.TryClaimSighting(ref ann, true, true, rng.Next(2) == 0, rng.Next(2) == 0, rng.Next(2) == 0)) sent++;
        if (sent != 1) bad.Add("letters sent " + sent + " in a game");
        int[] want = { 0, 1, 2, 3, 4, 5, 6, 7 };
        int[] gx = { 0, 1, 1, 1, 0, -1, -1, -1 }, gz = { 1, 1, 0, -1, -1, -1, 0, 1 };
        for (int k = 0; k < 8; k++) if (RM_FireHawkRewardsKernel.Compass8(gx[k] * 10, gz[k] * 10) != want[k]) bad.Add("compass " + k + " -> " + RM_FireHawkRewardsKernel.Compass8(gx[k] * 10, gz[k] * 10));
        int drops = 0, n = 100000; for (int i = 0; i < n; i++) if (RM_FireHawkRewardsKernel.TrophyDrops((float)rng.NextDouble(), 0.2f)) drops++;
        if (Math.Abs(drops / (double)n - 0.2) > 0.01) bad.Add("trophy rate " + drops / (double)n + " at chance 0.2");
        Check("rewards_random_one_letter_a_game_and_sometimes_a_feather", bars, "random", 10000 + 8 + n, bad,
            "seed " + (Seed + 7) + ": one letter a game out of 10,000 random looks; compass words right; the feather drops at its chance ('sometimes')", "once a game, sometimes");
    }

    // ------------------------------------------------------------------ furnacebeast_warms (stage 6), kernel half
    static void FurnaceWarmth()
    {
        string[] bars = { "furnacebeast_warms" };
        var bad = new List<string>(); var rng = new Random(Seed + 8); int n = 20000;
        for (int i = 0; i < n; i++)
        {
            float r = 0.5f + (float)rng.NextDouble() * 10, st = (float)rng.NextDouble() * 2; float d1 = (float)rng.NextDouble() * r * 1.3f, d2 = d1 + (float)rng.NextDouble() * 2;
            float o1 = FurnaceWarmthMath.Offset(d1 * d1, r, 14f, st), o2 = FurnaceWarmthMath.Offset(d2 * d2, r, 14f, st);
            if (o2 > o1 + 1e-5f) bad.Add("warmer farther: r " + r + " d " + d1 + "->" + d2);
            if (o1 < 0f || o1 > 14f * st + 1e-4f) bad.Add("offset out of [0, max*strength]");
            if (d1 >= r && o1 != 0f) bad.Add("warm beyond the radius");
        }
        if (!(FurnaceWarmthMath.Offset(1f, PyrelandsTuning.FurnaceAuraRadius, PyrelandsTuning.FurnaceWarmthMaxC, 1f) > 5f)) bad.Add("a pawn one cell off barely warmed");
        if (FurnaceWarmthMath.Combine(3f, 5f) != 5f) bad.Add("two beasts stack");
        if (FurnaceWarmthMath.RoomHeatCeiling(24f, 50f, 25f) != 75f || FurnaceWarmthMath.RoomHeatCeiling(24f, -10f, 25f) != 24f) bad.Add("room ceiling");
        Check("warmth_random_falls_off_to_radius", bars, "random", n + 3, bad,
            "seed " + (Seed + 8) + ": warmth highest at the beast, never rising with distance, 0 at and past the radius, scaled by the strength dial; one cell off at shipped values reads "
            + FurnaceWarmthMath.Offset(1f, PyrelandsTuning.FurnaceAuraRadius, PyrelandsTuning.FurnaceWarmthMaxC, 1f).ToString("0.0", Inv) + " C",
            "warms anyone standing near it");
    }
}
