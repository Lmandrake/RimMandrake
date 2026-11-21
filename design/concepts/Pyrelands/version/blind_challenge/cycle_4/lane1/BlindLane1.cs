// Pyrelands 0.1.0 blind challenge, cycle 4, lane 1: game-logic tests written from the bars alone (tree.json, sheet.md,
// plan.md, record.json rows, bars.md), the shipped settings (RM_PyrelandsMod.cs defaults and slider ranges) and the
// kernels the brief names. Nothing here was read from the builder's tests. One JSON row per line on stdout.
// Exit 0 = no FAIL row; 1 = at least one FAIL.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using RimMandrake.Pyrelands;

static class BlindLane1
{
    static int fails;
    static readonly List<string> rows = new List<string>();

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

    static void Row(string id, string[] bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") fails++;
        Console.WriteLine("{\"id\": " + J(id) + ", \"bars\": [" + string.Join(", ", bars.Select(J)) + "], \"kind\": " + J(kind)
            + ", \"verdict\": " + J(verdict) + ", \"cases\": " + cases + ", \"detail\": " + J(detail) + "}");
    }

    // Shipped defaults (RM_PyrelandsSettings field initialisers) and slider ranges (DoWindowContents).
    const float Dry = 0.70f, Wet = 1.40f, Bonus = 0.50f, BonusDays = 6f, Cap = 2f;
    const int TicksPerDay = 60000, TicksPerHour = 2500, WaterHours = 24;

    static Dictionary<string, string> Parse(string line)
    {
        var d = new Dictionary<string, string>();
        foreach (string kv in line.Split(';'))
        {
            int i = kv.IndexOf('=');
            if (i > 0) d[kv.Substring(0, i)] = kv.Substring(i + 1);
        }
        return d;
    }

    static float F(Dictionary<string, string> d, string k) => float.Parse(d[k], CultureInfo.InvariantCulture);

    // The probe line exactly as the game side (MapComponent_PyrelandsAshField.ProbeCell) composes it, from one cell's state.
    static string Probe(float fertility, bool watered, int burnTick, int now, bool raining, bool roofed, int wateredUntil, bool waterOn = true,
        bool gateOn = true, float dry = Dry, float wet = Wet, float bonus = Bonus, float days = BonusDays, bool bonusOn = true)
    {
        int dur = (int)(days * TicksPerDay);
        float b = bonusOn ? RM_FireEcoKernel.BurnBonus(burnTick, now, bonus, dur) : 0f;
        return RM_FireEcoKernel.ProbeLine(fertility, "RM_FE_Ash_Deep", true, watered && waterOn, dry, wet, b, burnTick, now, dur, raining,
            roofed, wateredUntil, true, waterOn, gateOn, Cap);
    }

    static float Truth(bool watered, int burnTick, int now, bool waterOn = true, float dry = Dry, float wet = Wet, float bonus = Bonus,
        float days = BonusDays)
    {
        float b = RM_FireEcoKernel.BurnBonus(burnTick, now, bonus, (int)(days * TicksPerDay));
        return RM_FireEcoKernel.AshFertility(dry, wet, watered, waterOn, b, Cap);
    }

    static int Main()
    {
        // The probe line must not depend on the player's locale: run everything under a comma-decimal culture.
        CultureInfo.CurrentCulture = new CultureInfo("de-DE");
        CultureInfo.CurrentUICulture = new CultureInfo("de-DE");
        try { Probes(); } catch (Exception e) { Row("probe_suite_crash", new[] { "ash_fertility_probe" }, "fixed", "FAIL", 0, e.ToString()); }
        try { Fertility(); } catch (Exception e) { Row("fertility_suite_crash", new[] { "fresh_burn_compounds_with_black_rain" }, "fixed", "FAIL", 0, e.ToString()); }
        try { Gate(); } catch (Exception e) { Row("gate_suite_crash", new[] { "inv_settings_gate" }, "fixed", "FAIL", 0, e.ToString()); }
        try { Wind(); } catch (Exception e) { Row("wind_suite_crash", new[] { "fire_walks_with_wind" }, "fixed", "FAIL", 0, e.ToString()); }
        try { Cast(); } catch (Exception e) { Row("cast_suite_crash", new[] { "furnacebeast_warms" }, "fixed", "FAIL", 0, e.ToString()); }
        return fails > 0 ? 1 : 0;
    }

    // ------------------------------------------------------------------ bar ash_fertility_probe
    static void Probes()
    {
        string[] P = { "ash_fertility_probe" };
        int now = 30 * TicksPerDay;
        // A burned wet cell (burned one day ago, under black rain, open sky) and a dry old cell (never burned, no rain).
        int burned = now - TicksPerDay;
        int until = RM_FireEcoKernel.ExtendWatered(-1, now, WaterHours * TicksPerHour);
        float fWet = Truth(true, burned, now), fDry = Truth(false, -1, now);
        var a = Parse(Probe(fWet, true, burned, now, true, false, until));
        var b = Parse(Probe(fDry, false, -1, now, false, false, -1));
        var differ = new List<string>();
        foreach (string k in new[] { "watered", "lift", "bonus", "bonusAgeDays", "bonusDaysLeft", "rainOnCell", "fertility", "expected" })
            if (a[k] != b[k]) differ.Add(k);
        bool sameBase = a["base"] == b["base"];
        bool ok = differ.Count == 8 && sameBase && a["consistent"] == "True" && b["consistent"] == "True"
            && Math.Abs(F(a, "lift") - (Wet - Dry)) < 1e-3 && Math.Abs(F(a, "bonus") - Bonus * (5f / 6f)) < 1e-3 && a["bonusAgeDays"] == "1.00"
            && b["bonusAgeDays"] == "-1" && Math.Abs(F(a, "fertility") - (Wet + Bonus * 5f / 6f)) < 1e-3 && Math.Abs(F(b, "fertility") - Dry) < 1e-3;
        Row("probe_wet_burned_vs_dry_old_part_by_part", P, "fixed", ok ? "PASS" : "FAIL", 2,
            "defaults dry 0.70 / watered 1.40 / bonus 0.50 over 6 d; wet cell burned 1 d ago under open-sky black rain vs a never-burned dry cell; "
            + "parts that differ: [" + string.Join(",", differ) + "] (want all 8), base equal " + sameBase + "; wet=" + a["fertility"] + " dry=" + b["fertility"]);

        // Refusal: the ash field switch off, and the mechanics gate off; the parts are still listed.
        string offWater = Probe(Dry, true, burned, now, true, false, until, waterOn: false);
        string offGate = Probe(Dry, true, burned, now, true, false, until, gateOn: false);
        string on = Probe(fWet, true, burned, now, true, false, until);
        bool refOk = offWater.StartsWith("refused=") && offWater.Contains("ashWaterFertilityEnabled") && offGate.StartsWith("refused=")
            && !on.StartsWith("refused=") && Parse(offWater).ContainsKey("bonus") && Parse(offWater).ContainsKey("base")
            && Parse(offWater)["consistent"] == "n/a" && Parse(offWater)["watered"] == "False";
        Row("probe_refuses_when_ash_field_off", P, "fixed", refOk ? "PASS" : "FAIL", 3,
            "water switch off -> '" + offWater.Substring(0, Math.Min(70, offWater.Length)) + "...'; gate off -> starts refused=" + offGate.StartsWith("refused=")
            + "; on -> refused " + on.StartsWith("refused="));

        // False pass named by the leaf: a probe that returns the BiomeDef's base fertility for every cell.
        var fake = Parse(Probe(Dry, true, burned, now, true, false, until));
        var fakeDry = Parse(Probe(Dry, false, -1, now, false, false, -1));
        bool fpOk = fake["consistent"] == "False" && fakeDry["consistent"] == "True";
        Row("probe_base_everywhere_reads_inconsistent", P, "fixed", fpOk ? "PASS" : "FAIL", 2,
            "a grid that hands back base 0.70 on the wet fresh cell reads consistent=" + fake["consistent"] + " (want False); on the dry old cell "
            + fakeDry["consistent"] + " (want True)");

        // Random cells over the shipped slider ranges: the line's parts add up, round-trip, and are culture-proof.
        int seed = 4401, n = 20000, bad = 0; string first = null;
        var rng = new Random(seed);
        for (int i = 0; i < n; i++)
        {
            float dry = (float)rng.NextDouble(), wet = 0.4f + 1.6f * (float)rng.NextDouble(), bon = 1.5f * (float)rng.NextDouble();
            float days = 1f + 19f * (float)rng.NextDouble();
            int t = rng.Next(0, 400 * TicksPerDay);
            int bt = rng.Next(4) == 0 ? -1 : rng.Next(3) == 0 ? t + rng.Next(1, 9999) : t - rng.Next(0, (int)(25 * TicksPerDay));
            bool w = rng.Next(2) == 0, rain = rng.Next(2) == 0, roof = rng.Next(3) == 0, wOn = rng.Next(5) > 0, gOn = rng.Next(5) > 0;
            float truth = Truth(w, bt, t, wOn, dry, wet, bon, days);
            bool lie = rng.Next(4) == 0;
            float fert = lie ? truth + 0.05f + (float)rng.NextDouble() : truth;
            string line = Probe(fert, w, bt, t, rain, roof, -1, wOn, gOn, dry, wet, bon, days);
            var d = Parse(line);
            string why = null;
            bool refused = line.StartsWith("refused=");
            if (refused != (!wOn || !gOn)) why = "refused=" + refused;
            else if (Math.Abs(F(d, "expected") - truth) > 1.5e-3) why = "expected " + d["expected"] + " truth " + truth;
            else if (!refused && d["consistent"] != (lie ? "False" : "True")) why = "consistent " + d["consistent"] + " lie " + lie;
            else if (refused && d["consistent"] != "n/a") why = "consistent on refusal " + d["consistent"];
            else if (Math.Abs(F(d, "lift") - (w && wOn ? wet - dry : 0f)) > 1.5e-3) why = "lift " + d["lift"];
            else if (d["rainOnCell"] != (rain && !roof).ToString()) why = "rainOnCell " + d["rainOnCell"];
            else if ((F(d, "bonus") > 0f) && !(F(d, "bonusDaysLeft") > 0f)) why = "bonus with no days left";
            else if (bt > t && F(d, "bonus") != 0f) why = "future stamp gave a bonus";
            else if ((refused ? line.Substring(line.IndexOf(";fertility=") + 1) : line).Contains(",")) why = "comma in the line under de-DE";
            if (why != null) { bad++; if (first == null) first = why + " | " + line; }
        }
        Row("probe_random_parts_add_up", P, "random", bad == 0 ? "PASS" : "FAIL", n,
            "seed " + seed + "; slider ranges dry 0..1, watered 0.4..2, bonus 0..1.5, days 1..20; a quarter of the cells lie about fertility; "
            + "culture de-DE; bad " + bad + (first != null ? "; first: " + first : ""));
    }

    // ------------------------------------------------------------------ fertility rules: watered ash, the burn clock, black rain
    static void Fertility()
    {
        string[] C = { "fresh_burn_compounds_with_black_rain", "ash_fertility_probe" };
        int now = 50 * TicksPerDay;
        // Shipped defaults: three pads of the leaf's scenario, read through day 7.
        var log = new StringBuilder();
        bool ok = true;
        for (int day = 0; day <= 7; day++)
        {
            int t = now + day * TicksPerDay;
            float wetFresh = Truth(true, now, t), dryFresh = Truth(false, now, t), wetOld = Truth(true, -1, t);
            log.Append("d" + day + " " + wetFresh.ToString("0.00", CultureInfo.InvariantCulture) + "/" + dryFresh.ToString("0.00", CultureInfo.InvariantCulture)
                + "/" + wetOld.ToString("0.00", CultureInfo.InvariantCulture) + " ");
            if (day < 6 && !(wetFresh > dryFresh && wetFresh > wetOld)) ok = false;
            if (day >= 6 && Math.Abs(wetFresh - wetOld) > 1e-4) ok = false;   // the bonus has faded on its own clock
        }
        Row("compound_three_pads_defaults", C, "fixed", ok ? "PASS" : "FAIL", 8,
            "wet fresh / dry fresh / wet old fertility by day: " + log + "(wet fresh must lead both while the bonus lasts, and equal wet old once its 6-day clock ends)");

        // The burn clock: monotone, bounded, zero after its duration, never for a future or absent stamp, never touched by rain.
        int seed = 4402, n = 40000, bad = 0; string first = null;
        var rng = new Random(seed);
        for (int i = 0; i < n; i++)
        {
            float bon = 1.5f * (float)rng.NextDouble();
            int dur = (int)((1f + 19f * (float)rng.NextDouble()) * TicksPerDay);
            int bt = rng.Next(0, 100 * TicksPerDay);
            int a1 = rng.Next(0, 30 * TicksPerDay), a2 = a1 + rng.Next(0, 5 * TicksPerDay);
            float b1 = RM_FireEcoKernel.BurnBonus(bt, bt + a1, bon, dur), b2 = RM_FireEcoKernel.BurnBonus(bt, bt + a2, bon, dur);
            string why = null;
            if (b2 > b1 + 1e-6f) why = "rose with age";
            else if (b1 < 0f || b1 > bon + 1e-6f) why = "out of [0,bonus]";
            else if (a1 >= dur && b1 != 0f) why = "alive after its clock";
            else if (RM_FireEcoKernel.BurnBonus(bt, bt, bon, dur) != bon) why = "not full at age 0";
            else if (RM_FireEcoKernel.BurnBonus(bt, bt - 1 - rng.Next(9999), bon, dur) != 0f) why = "future stamp";
            else if (RM_FireEcoKernel.BurnBonus(-1, bt, bon, dur) != 0f) why = "never burned";
            else if ((RM_FireEcoKernel.BonusDaysLeft(bt, bt + a1, dur) > 0f) != (a1 < dur)) why = "days-left disagrees with the clock";
            if (why != null) { bad++; if (first == null) first = why + " bt=" + bt + " a1=" + a1 + " a2=" + a2 + " dur=" + dur + " bonus=" + bon; }
        }
        Row("burn_clock_random", C, "random", bad == 0 ? "PASS" : "FAIL", n, "seed " + seed + "; bad " + bad + (first != null ? "; first " + first : ""));

        // Black rain: waters open sky for its hours, never a roofed cell, never with hours 0; a stamp is never shortened.
        bad = 0; first = null; seed = 4403; rng = new Random(seed); n = 20000;
        for (int i = 0; i < n; i++)
        {
            int t = rng.Next(0, 100 * TicksPerDay), old = rng.Next(-1, 100 * TicksPerDay), hrs = rng.Next(0, 73);
            int u = RM_FireEcoKernel.ExtendWatered(old, t, hrs * TicksPerHour);
            string why = null;
            if (u < old || u < t + hrs * TicksPerHour) why = "shortened";
            else if (RM_FireEcoKernel.BlackRainWaters(u, t, hrs, true)) why = "roofed cell watered";
            else if (RM_FireEcoKernel.BlackRainWaters(u, t, 0f, false)) why = "hours 0 still waters";
            else if (hrs > 0 && !RM_FireEcoKernel.BlackRainWaters(u, t, hrs, false)) why = "open sky not watered while stamped";
            else if (RM_FireEcoKernel.BlackRainWaters(u, u, hrs, false)) why = "watered at its own end";
            if (why != null) { bad++; if (first == null) first = why + " t=" + t + " old=" + old + " hrs=" + hrs; }
        }
        Row("black_rain_waters_random", C, "random", bad == 0 ? "PASS" : "FAIL", n, "seed " + seed + "; bad " + bad + (first != null ? "; first " + first : ""));

        // The fertility read stays in [0, cap] for any input, and the bonus adds on the watered lift (not instead of it).
        bad = 0; first = null; seed = 4404; rng = new Random(seed); n = 20000;
        for (int i = 0; i < n; i++)
        {
            float dry = -1f + 3f * (float)rng.NextDouble(), wet = -1f + 4f * (float)rng.NextDouble(), bon = -1f + 3f * (float)rng.NextDouble();
            bool w = rng.Next(2) == 0, on = rng.Next(2) == 0;
            float v = RM_FireEcoKernel.AshFertility(dry, wet, w, on, bon, Cap);
            float want = Math.Max(0f, Math.Min(Cap, (on && w ? wet : dry) + Math.Max(0f, bon)));
            if (v < 0f || v > Cap || Math.Abs(v - want) > 1e-5f) { bad++; if (first == null) first = "dry " + dry + " wet " + wet + " bonus " + bon + " -> " + v + " want " + want; }
        }
        Row("ash_fertility_bounds_random", C, "random", bad == 0 ? "PASS" : "FAIL", n, "seed " + seed + "; bad " + bad + (first != null ? "; first " + first : ""));

        // Sweep the shipped sliders (dry 0..1, watered 0.4..2, bonus 0..1.5 by 0.05): where does the compound ordering hold?
        int total = 0, capped = 0, inverted = 0, noBonus = 0;
        string capEg = null, invEg = null;
        for (int di = 0; di <= 20; di++)
            for (int wi = 0; wi <= 32; wi++)
                for (int bi = 0; bi <= 30; bi++)
                {
                    float dry = di * 0.05f, wet = 0.4f + wi * 0.05f, bon = bi * 0.05f;
                    total++;
                    float wf = RM_FireEcoKernel.AshFertility(dry, wet, true, true, bon, Cap), df = RM_FireEcoKernel.AshFertility(dry, wet, false, true, bon, Cap);
                    float wo = RM_FireEcoKernel.AshFertility(dry, wet, true, true, 0f, Cap);
                    if (bon <= 0f) { noBonus++; continue; }
                    if (!(wf > wo)) { capped++; if (capEg == null) capEg = "dry " + dry.ToString("0.00", CultureInfo.InvariantCulture) + " watered " + wet.ToString("0.00", CultureInfo.InvariantCulture) + " bonus " + bon.ToString("0.00", CultureInfo.InvariantCulture); }
                    else if (!(wf > df)) { inverted++; if (invEg == null) invEg = "dry " + dry.ToString("0.00", CultureInfo.InvariantCulture) + " watered " + wet.ToString("0.00", CultureInfo.InvariantCulture); }
                }
        Row("compound_slider_sweep", C, "sweep", "INFO", total,
            "settings points " + total + "; bonus 0 (the player switched the bonus to nothing) " + noBonus + "; wet fresh not above wet old because the cap 2.0 clips it "
            + capped + " (first " + capEg + "); watered set at or below dry so water gives nothing " + inverted + " (first " + invEg + "). Both are player-chosen tunings outside "
            + "the shipped defaults; the shipped point passes (compound_three_pads_defaults). Recorded, not a defect.");

        // ash_fertile_when_watered: wet roots never shut a season the heat left open, never warm a cold cell; no cooling = vanilla.
        string[] W = { "ash_fertile_when_watered" };
        bad = 0; first = null; seed = 4405; rng = new Random(seed); n = 40000;
        for (int i = 0; i < n; i++)
        {
            float min = -10f + 20f * (float)rng.NextDouble(), max = min + 10f + 40f * (float)rng.NextDouble();
            float T = -30f + 110f * (float)rng.NextDouble(), cool = rng.Next(4) == 0 ? 0f : 30f * (float)rng.NextDouble();
            bool van = T > min && T < max, wet = RM_FireEcoKernel.WetRootGrowthSeason(T, min, max, cool);
            string why = null;
            if (van && !wet) why = "shut a season";
            else if (T <= min && wet) why = "warmed a cold cell";
            else if (cool == 0f && wet != van) why = "no cooling differs from vanilla";
            else if (T >= max && wet != (T - cool > min && T - cool < max)) why = "hot side not the cooled test";
            if (why != null) { bad++; if (first == null) first = why + " T=" + T + " min=" + min + " max=" + max + " cool=" + cool; }
        }
        bool defaultsOk = Wet > Dry && Dry > 0f;
        Row("wet_roots_season_random", W, "random", bad == 0 && defaultsOk ? "PASS" : "FAIL", n,
            "seed " + seed + "; shipped watered 1.40 > dry 0.70 > 0 (sowable dry, faster wet): " + defaultsOk + "; bad " + bad + (first != null ? "; first " + first : ""));
    }

    // ------------------------------------------------------------------ bar inv_settings_gate: every mechanic switches off
    static void Gate()
    {
        string[] G = { "inv_settings_gate" };
        bool table = RM_FireEcoKernel.MechanicsOn(true, false, false) && RM_FireEcoKernel.MechanicsOn(true, true, true)
            && !RM_FireEcoKernel.MechanicsOn(true, true, false) && !RM_FireEcoKernel.MechanicsOn(false, false, true)
            && !RM_FireEcoKernel.MechanicsOn(false, true, true) && !RM_FireEcoKernel.MechanicsOn(false, true, false) && !RM_FireEcoKernel.MechanicsOn(false, false, false);
        Row("gate_truth_table", G, "fixed", table ? "PASS" : "FAIL", 8, "master AND (no shell OR shell toggle on): the roster toggle gates mechanics when the shell is loaded");

        // With the gate closed (master off, or the roster toggle off), every gated decision stays shut whatever the rest says.
        int seed = 4406, n = 20000, bad = 0; string first = null;
        var rng = new Random(seed);
        for (int i = 0; i < n; i++)
        {
            bool shell = rng.Next(2) == 0, master = rng.Next(2) == 0, toggle = rng.Next(2) == 0;
            bool gate = RM_FireEcoKernel.MechanicsOn(master, shell, toggle);
            if (gate) continue;
            bool[] r = Enumerable.Range(0, 8).Select(_ => rng.Next(4) > 0).ToArray();
            bool announced = false;
            string why = null;
            if (RM_FireEcoKernel.BurnStampMay(gate, r[0], r[1], false, r[2])) why = "burn stamp";
            else if (RM_FireEcoKernel.FireTickMayRoll(gate, r[0], r[1], true, false, true)) why = "fire tick roll";
            else if (RM_FireEcoKernel.BlackRainDouseAmount(gate, true, 40f, 1f, true) != 0f) why = "black rain douse";
            else if (RM_FireEcoKernel.RainBecomesBlackRain("Rain", true, gate)) why = "rain to black rain";
            else if (RM_FireEcoKernel.DomeOnHeatHit(true, true, gate, true, true, true, false, false)) why = "heat dome";
            else if (RM_BurnKernel.TribesIncidentSwitchesOn(true, gate, true, true)) why = "tribes incidents";
            else if (RM_FireHawkRewardsKernel.TryClaimSighting(ref announced, true, gate, true, true, false)) why = "hawk letter";
            if (why != null) { bad++; if (first == null) first = why + " master=" + master + " shell=" + shell + " toggle=" + toggle; }
        }
        Row("gate_closed_shuts_every_kernel_gate", G, "random", bad == 0 ? "PASS" : "FAIL", n, "seed " + seed + "; bad " + bad + (first != null ? "; first " + first : ""));

        // Each mechanic's own switch closes its own decision with the master on; the wind switch off gives vanilla's spread back.
        bool announced2 = false;
        var each = new List<string>();
        if (RM_FireEcoKernel.BurnStampMay(true, false, true, false, true)) each.Add("freshBurnBonus off still stamps");
        if (RM_FireEcoKernel.FireTickMayRoll(true, false, false, true, false, true)) each.Add("ash and fruit off still roll");
        if (RM_FireEcoKernel.BlackRainDouseAmount(true, false, 40f, 1f, true) != 0f) each.Add("dousing off still douses");
        if (RM_FireEcoKernel.BlackRainDouseAmount(true, true, 0f, 1f, true) != 0f) each.Add("dousing 0 still douses");
        if (RM_FireEcoKernel.DomeOnHeatHit(true, true, true, false, true, true, false, false)) each.Add("burrow off still domes");
        if (RM_FireEcoKernel.DomeOnHeatHit(true, true, true, true, false, true, false, false)) each.Add("dome off still domes");
        if (RM_BurnKernel.WindCarryDue(false, true, true, false, 99999)) each.Add("wind off still carries");
        if (!RM_BurnKernel.VanillaSpreadRuns(false, true, true)) each.Add("wind off does not give vanilla spread back");
        if (RM_BurnKernel.VanillaSpreadRuns(true, true, true)) each.Add("wind on still runs vanilla spread on Pyrelands ground");
        if (RM_BurnKernel.TribesIncidentSwitchesOn(true, true, false, false)) each.Add("burn line and fire clock off still incidents");
        if (RM_FireHawkRewardsKernel.TryClaimSighting(ref announced2, false, true, true, true, false)) each.Add("letter off still letters");
        if (RM_FireEcoKernel.AshWeatherSandRate(1f, true, false, 1f) != 0f) each.Add("ashfall off still lays ash");
        if (FurnaceWarmthMath.Offset(1f, 6f, 10f, 0f) != 0f) each.Add("warmth 0 still warms");
        float d, c; RM_FireEcoKernel.SplitClear(10f, false, 1f, out d, out c);
        if (d != 0f || c != 10f) each.Add("ambient ash off still drifts");
        if (RM_FireEcoKernel.AshFertility(Dry, Wet, true, false, 0f, Cap) != Dry) each.Add("water fertility off still lifts");
        Row("gate_each_switch_closes_its_mechanic", G, "fixed", each.Count == 0 ? "PASS" : "FAIL", 15,
            each.Count == 0 ? "15 switches each close their own decision with the master on" : string.Join("; ", each));
    }

    // ------------------------------------------------------------------ bars fire_walks_with_wind, burn_line_walks (kernel part)
    static void Wind()
    {
        string[] B = { "fire_walks_with_wind", "burn_line_walks" };
        int seed = 4407, n = 20000, bad = 0; string first = null;
        var rng = new Random(seed);
        int reach = RM_BurnKernel.WindCarryReach;
        double sumErr = 0; int bins = 0; double worst = 0; float worstB = 0;
        for (int i = 0; i < n; i++)
        {
            float bearing = (float)(rng.NextDouble() * 1080.0 - 360.0);
            var dx = new int[3 * reach]; var dz = new int[3 * reach];
            RM_BurnKernel.WindProbes(bearing, (float)rng.NextDouble(), (float)rng.NextDouble(), reach, dx, dz);
            double rad = bearing * Math.PI / 180.0; float wx = (float)Math.Sin(rad), wz = (float)Math.Cos(rad);
            for (int k = 0; k < dx.Length; k++)
            {
                if (!RM_BurnKernel.Downwind(dx[k], dz[k], wx, wz)) { bad++; if (first == null) first = "probe " + k + " (" + dx[k] + "," + dz[k] + ") not downwind of bearing " + bearing; break; }
                if (dx[k] == 0 && dz[k] == 0) { bad++; if (first == null) first = "probe at its own cell"; break; }
            }
        }
        // Mean heading of the first probe = the wind, on a grid of bearings.
        for (int bb = 0; bb < 360; bb += 7)
        {
            double sx = 0, sz = 0; var r2 = new Random(seed + bb);
            for (int k = 0; k < 4000; k++)
            {
                var dx = new int[3 * reach]; var dz = new int[3 * reach];
                RM_BurnKernel.WindProbes(bb, (float)r2.NextDouble(), (float)r2.NextDouble(), reach, dx, dz);
                double ang = Math.Atan2(dx[0], dz[0]) * 180.0 / Math.PI;
                sx += Math.Sin(ang * Math.PI / 180.0); sz += Math.Cos(ang * Math.PI / 180.0);
            }
            double mean = (Math.Atan2(sx, sz) * 180.0 / Math.PI + 360.0) % 360.0;
            double err = Math.Abs(((mean - bb) % 360 + 540) % 360 - 180);
            sumErr += err; bins++; if (err > worst) { worst = err; worstB = bb; }
        }
        Row("wind_probes_downwind_never_back", B, "random", bad == 0 && worst < 6.0 ? "PASS" : "FAIL", n + bins * 4000,
            "seed " + seed + "; bearings -360..720; probes off the downwind cone or at the fire's own cell: " + bad + (first != null ? " (" + first + ")" : "")
            + "; mean first-probe heading vs bearing: mean error " + (sumErr / bins).ToString("0.0", CultureInfo.InvariantCulture) + " deg, worst "
            + worst.ToString("0.0", CultureInfo.InvariantCulture) + " at " + worstB + " (compass-step fuzz; want < 6)");

        // A whole-grid walk: a line lit across the wind, each fire carried once to the first free probe cell.
        var res = new List<string>(); bool walkOk = true; double[] dispX = new double[2], dispZ = new double[2];
        float[] bearings = { 37f, 217f };
        for (int bi = 0; bi < 2; bi++)
        {
            float wb = bearings[bi];
            int N = 200, cx0 = 100, cz0 = 100;
            var state = new byte[N * N];   // 0 fuel, 1 burning, 2 burnt
            int[] lx, lz; RM_BurnKernel.FrontLine(RM_BurnKernel.AcrossWind(wb), 21, out lx, out lz);
            var fires = new List<int>();
            for (int k = 0; k < lx.Length; k++) { int idx = (cz0 + lz[k]) * N + cx0 + lx[k]; if (state[idx] == 0) { state[idx] = 1; fires.Add(idx); } }
            int startCount = fires.Count, maxCount = startCount; bool grew = false;
            var r3 = new Random(seed + bi);
            double sx0 = fires.Average(f => f % N), sz0 = fires.Average(f => f / N);
            int gens = 60;
            for (int g = 0; g < gens && fires.Count > 0; g++)
            {
                var next = new List<int>();
                foreach (int f in fires)
                {
                    var dx = new int[3 * reach]; var dz = new int[3 * reach];
                    RM_BurnKernel.WindProbes(wb, (float)r3.NextDouble(), (float)r3.NextDouble(), reach, dx, dz);
                    int fx = f % N, fz = f / N;
                    for (int k = 0; k < dx.Length; k++)
                    {
                        int x = fx + dx[k], z = fz + dz[k];
                        if (x < 0 || z < 0 || x >= N || z >= N) continue;
                        int j = z * N + x;
                        if (state[j] != 0) continue;
                        state[j] = 1; next.Add(j); break;
                    }
                    state[f] = 2;
                }
                if (next.Count > fires.Count) grew = true;
                maxCount = Math.Max(maxCount, next.Count);
                if (next.Count == 0) break;
                fires = next;
            }
            double ex = fires.Average(f => f % N) - sx0, ez = fires.Average(f => f / N) - sz0;
            dispX[bi] = ex; dispZ[bi] = ez;
            double head = (Math.Atan2(ex, ez) * 180.0 / Math.PI + 360.0) % 360.0, dist = Math.Sqrt(ex * ex + ez * ez);
            double herr = Math.Abs(((head - wb) % 360 + 540) % 360 - 180);
            int burnt = state.Count(s => s == 2);
            res.Add("bearing " + wb + ": line " + startCount + " -> " + fires.Count + " fires, max " + maxCount + ", centroid moved "
                + dist.ToString("0.0", CultureInfo.InvariantCulture) + " cells heading " + head.ToString("0", CultureInfo.InvariantCulture) + " (err " + herr.ToString("0.0", CultureInfo.InvariantCulture) + "), burnt trail " + burnt);
            if (grew || herr > 15 || dist < 30 || burnt < startCount * 20) walkOk = false;
        }
        double dot = dispX[0] * dispX[1] + dispZ[0] * dispZ[1];
        if (!(dot < 0)) walkOk = false;
        Row("wind_line_walks_downwind_and_conserves", B, "sweep", walkOk ? "PASS" : "FAIL", 2,
            string.Join("; ", res) + "; opposite winds move opposite ways (dot " + dot.ToString("0", CultureInfo.InvariantCulture) + " < 0); no carry step ever made more fires than it had");
    }

    // ------------------------------------------------------------------ fire cast kernels: furnace-beast warmth, hawk rewards
    static void Cast()
    {
        string[] F = { "furnacebeast_warms" };
        int seed = 4408, n = 20000, bad = 0; string first = null;
        var rng = new Random(seed);
        for (int i = 0; i < n; i++)
        {
            float r = 0.5f + 12f * (float)rng.NextDouble(), maxC = 30f * (float)rng.NextDouble(), s = 2f * (float)rng.NextDouble();
            float d1 = r * 1.2f * (float)rng.NextDouble(), d2 = d1 + r * 0.5f * (float)rng.NextDouble();
            float o1 = FurnaceWarmthMath.Offset(d1 * d1, r, maxC, s), o2 = FurnaceWarmthMath.Offset(d2 * d2, r, maxC, s);
            string why = null;
            if (o1 < 0f || o1 > maxC * s + 1e-4f) why = "out of [0, max x strength]";
            else if (o2 > o1 + 1e-5f) why = "warmer farther away";
            else if (d1 >= r && o1 != 0f) why = "warm outside the radius";
            else if (Math.Abs(FurnaceWarmthMath.Offset(d1 * d1, r, maxC, 2f * s) - 2f * o1) > 1e-3f * Math.Max(1f, o1)) why = "strength not linear";
            else if (FurnaceWarmthMath.Combine(o1, o2) != Math.Max(o1, o2)) why = "two beasts stack";
            else if (FurnaceWarmthMath.RoomHeatCeiling(5f, -20f + 60f * (float)rng.NextDouble(), 10f) < 5f) why = "ceiling under its floor";
            if (why != null) { bad++; if (first == null) first = why + " r=" + r + " maxC=" + maxC + " s=" + s + " d1=" + d1 + " d2=" + d2; }
        }
        bool near = FurnaceWarmthMath.Offset(1f, 6f, 10f, 1f) > 0f && FurnaceWarmthMath.ShowsSign(FurnaceWarmthMath.Offset(1f, 6f, 10f, 1f));
        Row("furnace_warmth_random", F, "random", bad == 0 && near ? "PASS" : "FAIL", n,
            "seed " + seed + "; strength slider 0..2; someone one cell from a beast is warmed and shows the sign: " + near + "; bad " + bad + (first != null ? "; first " + first : ""));

        string[] H = { "inv_firehawk_hunt_rewards" };
        bool announced = false; int sent = 0;
        for (int i = 0; i < 1000; i++) if (RM_FireHawkRewardsKernel.TryClaimSighting(ref announced, true, true, true, true, false)) sent++;
        int drops = 0; var r4 = new Random(4409); float ch = 0.25f;
        for (int i = 0; i < 100000; i++) if (RM_FireHawkRewardsKernel.TrophyDrops((float)r4.NextDouble(), ch)) drops++;
        int never = 0; for (int i = 0; i < 10000; i++) if (RM_FireHawkRewardsKernel.TrophyDrops((float)r4.NextDouble(), 0f)) never++;
        bool compassOk = RM_FireHawkRewardsKernel.Compass8(0, 5) == 0 && RM_FireHawkRewardsKernel.Compass8(5, 0) == 2 && RM_FireHawkRewardsKernel.Compass8(0, -5) == 4
            && RM_FireHawkRewardsKernel.Compass8(-5, 0) == 6 && RM_FireHawkRewardsKernel.Compass8(3, 3) == 1 && RM_FireHawkRewardsKernel.Compass8(0, 0) == -1;
        bool hOk = sent == 1 && Math.Abs(drops / 100000.0 - ch) < 0.01 && never == 0 && compassOk;
        Row("hawk_letter_once_and_trophy_chance", H, "random", hOk ? "PASS" : "FAIL", 111000,
            "seed 4409; letters from 1000 sightings " + sent + " (want 1); trophy rate at chance 0.25 = " + (drops / 100000.0).ToString("0.000", CultureInfo.InvariantCulture)
            + "; at chance 0: " + never + "; compass words N/E/S/W/NE ok " + compassOk + ". 'Butchering anything else never does' is game-side (the butcher hook), not in this kernel");
    }
}
