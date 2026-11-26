// Pyrelands 0.1.0, blind challenge cycle 2, lane 1: game-logic tests written from the bars alone (tree.json, sheet.md,
// plan.md, record.json inventory rows) against the shipped kernels and settings. Not the builder's tests; none of them was read.
// Built and run by run_lane1.py (it stages this file with the six kernel files). One JSON row per line on stdout.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimMandrake.Pyrelands;

public static class BlindLane1
{
    static int fails;
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    static string Esc(string s) => (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ");

    static void Row(string id, string[] bars, string kind, bool? pass, int cases, string detail)
    {
        string verdict = pass == null ? (kind == "info" ? "INFO" : "UNSETTLED") : (pass.Value ? "PASS" : "FAIL");
        if (verdict == "FAIL") fails++;
        Console.WriteLine("{\"id\": \"" + Esc(id) + "\", \"bars\": [" + string.Join(", ", bars.Select(b => "\"" + b + "\"")) + "], \"kind\": \""
            + kind + "\", \"verdict\": \"" + verdict + "\", \"cases\": " + cases + ", \"detail\": \"" + Esc(detail) + "\"}");
    }

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

    static float F(string s) => float.Parse(s, Inv);
    static bool Near(float a, float b, float tol = 0.001f) => Math.Abs(a - b) <= tol;

    const int Day = 60000;
    // Shipped defaults (RM_PyrelandsMod.cs, read as settings input).
    const float Dry = 0.70f, Wet = 1.40f, Bonus = 0.50f, BonusDays = 6f, Cap = 2f;

    static string Probe(float fert, bool watered, int burnTick, int now, bool rain, bool roofed, bool waterOn, bool gateOn,
        float dry = Dry, float wet = Wet, float bonus = Bonus, float days = BonusDays, bool active = true)
    {
        int dur = (int)(days * Day);
        float b = RM_FireEcoKernel.BurnBonus(burnTick, now, bonus, dur);
        return RM_FireEcoKernel.ProbeLine(fert, "RM_FE_Ash_Deep", true, watered, dry, wet, b, burnTick, now, dur, rain, roofed,
            rain ? now + 24 * 2500 : -1, active, waterOn, gateOn, Cap);
    }

    static float Field(bool watered, int burnTick, int now, bool waterOn = true, float dry = Dry, float wet = Wet, float bonus = Bonus,
        float days = BonusDays)
    {
        float b = RM_FireEcoKernel.BurnBonus(burnTick, now, bonus, (int)(days * Day));
        return RM_FireEcoKernel.AshFertility(dry, wet, watered, waterOn, b, Cap);
    }

    public static int Main()
    {
        int now = 30 * Day;

        // ---------------------------------------------------------------- ash_fertility_probe (offline bar)
        {
            float wetFresh = Field(true, now - 2500, now), dryOld = Field(false, -1, now);
            var a = Parse(Probe(wetFresh, true, now - 2500, now, true, false, true, true));
            var b = Parse(Probe(dryOld, false, -1, now, false, false, true, true));
            string[] parts = { "watered", "bonus", "lift", "bonusAgeDays", "bonusDaysLeft", "rainOnCell", "expected", "fertility" };
            var differ = parts.Where(p => a.ContainsKey(p) && b.ContainsKey(p) && a[p] != b[p]).ToList();
            bool ok = differ.Count >= 6 && a["consistent"] == "True" && b["consistent"] == "True" && !a.ContainsKey("refused");
            Row("probe_wet_fresh_vs_dry_old_part_by_part", new[] { "ash_fertility_probe" }, "fixed", ok, 2,
                "parts that differ: " + string.Join(",", differ) + "; wet fresh expected=" + a["expected"] + " lift=" + a["lift"] + " bonus=" + a["bonus"]
                + "; dry old expected=" + b["expected"] + " lift=" + b["lift"] + " bonus=" + b["bonus"]);
        }
        {
            string offWater = Probe(Dry, true, now - 2500, now, true, false, false, true);
            string offGate = Probe(Dry, true, now - 2500, now, true, false, true, false);
            bool ok = offWater.StartsWith("refused=") && offGate.StartsWith("refused=") && offWater.Contains("base=") && offGate.Contains("lift=")
                && Parse(offWater)["consistent"] == "n/a" && Parse(offGate)["consistent"] == "n/a";
            Row("probe_refuses_when_ash_field_off", new[] { "ash_fertility_probe", "inv_settings_gate" }, "fixed", ok, 2,
                "ashWaterFertilityEnabled off -> " + offWater.Substring(0, Math.Min(70, offWater.Length)) + " | gate off -> "
                + offGate.Substring(0, Math.Min(70, offGate.Length)));
        }
        {
            // The false pass: a probe handing back the base for every cell must not read consistent on a wet or fresh cell.
            var wetFresh = Parse(Probe(Dry, true, now - 2500, now, true, false, true, true));
            var dryFresh = Parse(Probe(Dry, false, now - 2500, now, false, false, true, true));
            var wetOld = Parse(Probe(Dry, true, -1, now, true, false, true, true));
            bool ok = wetFresh["consistent"] == "False" && dryFresh["consistent"] == "False" && wetOld["consistent"] == "False";
            Row("probe_base_everywhere_reads_inconsistent", new[] { "ash_fertility_probe" }, "fixed", ok, 3,
                "fertility=base on wet fresh/dry fresh/wet old -> consistent " + wetFresh["consistent"] + "/" + dryFresh["consistent"] + "/" + wetOld["consistent"]);
        }
        {
            int seed = 20261116, n = 4000; var rng = new Random(seed); string bad = null; int badMag = int.MaxValue;
            for (int k = 0; k < n; k++)
            {
                float dry = (float)rng.NextDouble(), wet = 0.4f + 1.6f * (float)rng.NextDouble(), bonus = 1.5f * (float)rng.NextDouble();
                float days = 1f + 19f * (float)rng.NextDouble(); bool watered = rng.Next(2) == 0, waterOn = rng.Next(4) != 0, gate = rng.Next(5) != 0;
                int burn = rng.Next(3) == 0 ? -1 : now - rng.Next(0, 25 * Day);
                float fert = RM_FireEcoKernel.AshFertility(dry, wet, watered, waterOn, RM_FireEcoKernel.BurnBonus(burn, now, bonus, (int)(days * Day)), Cap);
                var d = Parse(Probe(fert, watered, burn, now, watered, false, waterOn, gate, dry, wet, bonus, days));
                float exp = F(d["expected"]), lift = F(d["lift"]), left = F(d["bonusDaysLeft"]);
                string why = null;
                if (!Near(exp, fert, 0.0015f)) why = "expected " + exp + " != grid " + fert;
                else if (exp < 0f || exp > Cap + 1e-4f) why = "expected outside [0,cap]";
                else if ((gate && waterOn) != !d.ContainsKey("refused")) why = "refusal does not follow the switches";
                else if (gate && waterOn && d["consistent"] != "True") why = "consistent=" + d["consistent"] + " on an honest grid";
                else if (!(watered && waterOn) && !Near(lift, 0f)) why = "lift on a dry cell";
                else if (watered && waterOn && !Near(lift, wet - dry, 0.0015f)) why = "lift != watered-base";
                else if (left < 0f || left > days + 0.01f) why = "daysLeft out of range";
                if (why != null)
                {
                    int mag = (burn < 0 ? 0 : now - burn);
                    if (mag < badMag) { badMag = mag; bad = why + " at dry=" + dry + " wet=" + wet + " bonus=" + bonus + " days=" + days + " watered=" + watered + " waterOn=" + waterOn + " gate=" + gate + " burn=" + burn; }
                }
            }
            Row("probe_random_parts_reassemble", new[] { "ash_fertility_probe" }, "random", bad == null, n,
                "seed " + seed + (bad == null ? "; every line's expected = AshFertility(parts), lift = watered-base only when wet, refusal iff a switch is off" : "; smallest failing: " + bad));
        }

        // ---------------------------------------------------------------- the ruled numbers behind the probe (stage 6 bars)
        {
            float wetFresh = Field(true, now - 1000, now), dryFresh = Field(false, now - 1000, now), wetOld = Field(true, -1, now), dryOld = Field(false, -1, now);
            bool ok = Near(dryOld, 0.70f, 0.02f) && Near(wetOld, 1.40f, 0.02f) && Near(dryFresh, 1.20f, 0.02f) && Near(wetFresh, 1.90f, 0.02f);
            Row("ruled_fertility_numbers_at_shipped_settings", new[] { "fresh_burn_compounds_with_black_rain", "ash_fertile_when_watered", "ash_fertility_probe" }, "fixed", ok, 4,
                string.Format(Inv, "dry old {0:0.000} (~0.70), wet old {1:0.000} (~1.40), dry fresh {2:0.000} (~1.20), wet fresh {3:0.000} (~1.90)", dryOld, wetOld, dryFresh, wetFresh));
        }
        {
            // The bonus keeps its own clock: gone by day 6-7 whatever the rain; the kernel has no rain input to wipe it.
            float d5 = RM_FireEcoKernel.BurnBonus(now - 5 * Day, now, Bonus, (int)(BonusDays * Day));
            float d6 = RM_FireEcoKernel.BurnBonus(now - 6 * Day, now, Bonus, (int)(BonusDays * Day));
            float d7 = RM_FireEcoKernel.BurnBonus(now - 7 * Day, now, Bonus, (int)(BonusDays * Day));
            float halfDayWet = Field(true, now - Day / 2, now);
            bool ok = d5 > 0f && d6 == 0f && d7 == 0f && halfDayWet > 1.85f;
            Row("burn_bonus_own_clock_rain_never_wipes", new[] { "fresh_burn_compounds_with_black_rain" }, "fixed", ok, 4,
                string.Format(Inv, "bonus day5 {0:0.000}, day6 {1:0.000}, day7 {2:0.000}; wet scar half a day into the rain {3:0.000} (not wiped to 1.40)", d5, d6, d7, halfDayWet));
        }
        {
            int seed = 7151, n = 5000; var rng = new Random(seed); string bad = null;
            for (int k = 0; k < n && bad == null; k++)
            {
                float bonus = 1.5f * (float)rng.NextDouble(), days = 1f + 19f * (float)rng.NextDouble(); int dur = (int)(days * Day);
                int burn = now - rng.Next(0, 30 * Day); int t1 = now + rng.Next(0, 3 * Day);
                float b0 = RM_FireEcoKernel.BurnBonus(burn, now, bonus, dur), b1 = RM_FireEcoKernel.BurnBonus(burn, t1, bonus, dur);
                if (b0 < -1e-6f || b0 > bonus + 1e-6f) bad = "bonus outside [0,base]: " + b0 + " base " + bonus;
                else if (b1 > b0 + 1e-6f) bad = "bonus grew with age: " + b0 + " -> " + b1;
                else if (now - burn >= dur && b0 != 0f) bad = "bonus past its clock: age " + (now - burn) + " dur " + dur;
                else if (RM_FireEcoKernel.BurnBonus(burn + 10 * Day + now, now, bonus, dur) != 0f) bad = "a stamp from the future counted";
            }
            Row("burn_bonus_decays_never_grows_sweep", new[] { "fresh_burn_compounds_with_black_rain", "inv_settings_gate" }, "sweep", bad == null, n,
                "seed " + seed + ", freshBurnBonus 0..1.5, freshBurnDays 1..20 (the shipped slider ranges)" + (bad == null ? "" : "; " + bad));
        }
        {
            // Shipped sliders swept: the field reads inside [0, cap]; water off -> dry; bonus never lowers a cell.
            int seed = 99, n = 6000; var rng = new Random(seed); string bad = null; int capped = 0;
            for (int k = 0; k < n && bad == null; k++)
            {
                float dry = (float)rng.NextDouble(), wet = 0.4f + 1.6f * (float)rng.NextDouble(), bonus = 1.5f * (float)rng.NextDouble();
                float days = 1f + 19f * (float)rng.NextDouble(); int burn = now - rng.Next(0, 10 * Day); bool watered = rng.Next(2) == 0;
                float on = Field(watered, burn, now, true, dry, wet, bonus, days), off = Field(watered, burn, now, false, dry, wet, bonus, days);
                float noBurn = Field(watered, -1, now, true, dry, wet, bonus, days);
                if (on < 0f || on > Cap) bad = "outside [0,cap]: " + on;
                else if (!Near(off, Math.Min(Cap, dry + RM_FireEcoKernel.BurnBonus(burn, now, bonus, (int)(days * Day))))) bad = "water off is not dry+bonus: " + off;
                else if (on + 1e-6f < noBurn) bad = "a burn lowered the cell";
                if (Near(on, Cap) && !Near(noBurn + RM_FireEcoKernel.BurnBonus(burn, now, bonus, (int)(days * Day)), Cap)) capped++;
            }
            Row("ash_field_sweep_inside_cap", new[] { "ash_fertile_when_watered", "fresh_burn_compounds_with_black_rain", "inv_settings_gate" }, "sweep", bad == null, n,
                "seed " + seed + "; ashDryFertility 0..1, ashWateredFertility 0.4..2, bonus 0..1.5, days 1..20; " + capped + " cases clipped at the 2.0 cap" + (bad == null ? "" : "; " + bad));
        }
        {
            bool okHot = !RM_FireEcoKernel.WetRootGrowthSeason(48f, 6f, 42f, 0f) && RM_FireEcoKernel.WetRootGrowthSeason(48f, 6f, 42f, 15f);
            bool okCold = RM_FireEcoKernel.WetRootGrowthSeason(3f, 6f, 42f, 15f) == false && RM_FireEcoKernel.WetRootGrowthSeason(20f, 6f, 42f, 15f);
            int seed = 31, n = 4000; var rng = new Random(seed); string bad = null;
            for (int k = 0; k < n && bad == null; k++)
            {
                float t = -30f + 100f * (float)rng.NextDouble(), mn = 0f + 10f * (float)rng.NextDouble(), mx = 35f + 15f * (float)rng.NextDouble(), c = 30f * (float)rng.NextDouble();
                bool vanilla = t > mn && t < mx, wet = RM_FireEcoKernel.WetRootGrowthSeason(t, mn, mx, c);
                if (vanilla && !wet) bad = "wet roots shut a season vanilla opens: T=" + t + " min=" + mn + " max=" + mx + " cool=" + c;
            }
            Row("wet_roots_grow_as_if_cooler", new[] { "ash_fertile_when_watered" }, "random", okHot && okCold && bad == null, n + 4,
                "seed " + seed + "; 48C crop (max 42) grows only on watered ash; a cold cell never counts warmer" + (bad == null ? "" : "; " + bad));
        }

        // ---------------------------------------------------------------- inv_settings_gate (offline bar), kernel half
        {
            var table = new List<string>(); bool ok = true;
            foreach (bool m in new[] { true, false }) foreach (bool p in new[] { true, false }) foreach (bool s in new[] { true, false })
            {
                bool got = RM_FireEcoKernel.MechanicsOn(m, p, s), want = m && (!p || s);
                ok &= got == want; table.Add((m ? "M" : "m") + (p ? "P" : "p") + (s ? "S" : "s") + "=" + (got ? 1 : 0));
            }
            Row("gate_truth_table_master_and_roster_toggle", new[] { "inv_settings_gate" }, "fixed", ok, 8, string.Join(" ", table));
        }
        {
            // Every kernel decision that reads the master switch does nothing with it off, over random other inputs.
            int seed = 4242, n = 3000; var rng = new Random(seed); string bad = null;
            for (int k = 0; k < n && bad == null; k++)
            {
                bool r() => rng.Next(2) == 0;
                if (RM_FireEcoKernel.FireTickMayRoll(false, r(), r(), r(), r(), r())) bad = "FireTickMayRoll";
                else if (RM_FireEcoKernel.BurnStampMay(false, r(), r(), r(), r())) bad = "BurnStampMay";
                else if (RM_FireEcoKernel.BlackRainDouseAmount(false, r(), 100f * (float)rng.NextDouble(), (float)rng.NextDouble(), r()) != 0f) bad = "BlackRainDouseAmount";
                else if (RM_FireEcoKernel.RainBecomesBlackRain("Rain", r(), false)) bad = "RainBecomesBlackRain";
                else if (RM_FireEcoKernel.DomeOnHeatHit(r(), r(), false, r(), r(), r(), r(), r())) bad = "DomeOnHeatHit";
                else { bool ann = false; if (RM_FireHawkRewardsKernel.TryClaimSighting(ref ann, r(), false, r(), r(), r()) || ann) bad = "TryClaimSighting"; }
            }
            Row("gate_off_every_kernel_decision_inert", new[] { "inv_settings_gate" }, "sweep", bad == null, n * 6,
                "seed " + seed + "; master off -> no fire-tick roll, no burn stamp, no dousing, no rain swap, no dome, no letter" + (bad == null ? "" : "; acted: " + bad));
        }
        {
            int seed = 515, n = 3000; var rng = new Random(seed); string bad = null;
            for (int k = 0; k < n && bad == null; k++)
            {
                float d = 100f * (float)rng.NextDouble(), share = -0.5f + 2f * (float)rng.NextDouble(); bool exp = rng.Next(2) == 0;
                float a = RM_FireEcoKernel.BlackRainDouseAmount(true, true, d, share, exp);
                if (a < 0f || a > d + 1e-4f) bad = "amount outside [0, slider]: " + a;
                else if (!exp && a != 0f) bad = "a sheltered fire doused";
                else if (RM_FireEcoKernel.BlackRainDouseAmount(true, false, d, share, exp) != 0f) bad = "switch off still douses";
            }
            Row("black_rain_dousing_switch_and_slider_sweep", new[] { "inv_settings_gate", "three_skies" }, "sweep", bad == null, n * 2,
                "seed " + seed + "; blackRainDousing 0..100 x share x shelter" + (bad == null ? "" : "; " + bad));
        }

        // ---------------------------------------------------------------- three_skies: black rain puts fires out
        {
            const float flam = 1.6f; // ember grass, Defs
            int Beats(float share, float extra) { float s = 1.75f; for (int i = 1; i <= 400; i++) { s = RM_FireEcoKernel.FireSizeAfterRainBeat(s, flam, share, extra); if (s == 0f) return i; } return -1; }
            int clear = Beats(0f, 0f), vanilla = Beats(1f, 0f), black = Beats(1f, RM_FireEcoKernel.BlackRainDouseAmount(true, true, 40f, 1f, true));
            bool ok = clear < 0 && vanilla < 0 && black > 0 && black <= 20;
            Row("black_rain_puts_a_grass_fire_out_clear_sky_does_not", new[] { "three_skies", "inv_weather" }, "fixed", ok, 3,
                "beats of 150 ticks to out from 1.75 on ember grass: clear " + clear + ", vanilla rain " + vanilla + ", black rain (40) " + black + " (-1 = never in 400)");
            int lo = -1; for (int d = 0; d <= 100; d++) if (Beats(1f, d) > 0) { lo = d; break; }
            Row("black_rain_dousing_threshold_on_slider", new[] { "three_skies", "inv_settings_gate" }, "info", null, 101,
                "smallest blackRainDousing that puts ember grass out: " + lo + " (slider 0..100, default 40); below it black rain is ordinary rain for fire");
        }
        {
            int seed = 8, n = 2000; var rng = new Random(seed); string bad = null;
            for (int k = 0; k < n && bad == null; k++)
            {
                float lerp = -0.5f + 2f * (float)rng.NextDouble(); bool c = rng.Next(2) == 0, l = rng.Next(2) == 0;
                float s = RM_FireEcoKernel.BlackRainShare(c, l, lerp);
                if (s < 0f || s > 1f) bad = "share " + s;
                else if (c && l && !Near(s, 1f)) bad = "black to black blend is not 1";
                else if (!c && !l && s != 0f) bad = "no black rain yet share " + s;
            }
            bool roofOk = RM_FireEcoKernel.FireExposedToRain(false, false, false) && !RM_FireEcoKernel.FireExposedToRain(true, true, true)
                && !RM_FireEcoKernel.FireExposedToRain(true, false, false) && RM_FireEcoKernel.FireExposedToRain(true, false, true);
            Row("black_rain_share_and_shelter", new[] { "three_skies" }, "random", bad == null && roofOk, n + 4, "seed " + seed + (bad == null ? "" : "; " + bad) + "; roof table " + roofOk);
        }

        // ---------------------------------------------------------------- no_ordinary_rain
        {
            string[] rains = { "Rain", "FoggyRain", "RainyThunderstorm", "TorrentialRain" };
            string[] others = { "Clear", "Fog", "DryThunderstorm", "SnowGentle", "SnowHard", "RM_FE_BlackRain", "RM_FE_AshFall", "RM_FE_Cinderfall", null };
            bool ok = rains.All(w => RM_FireEcoKernel.RainBecomesBlackRain(w, true, true)) && others.All(w => !RM_FireEcoKernel.RainBecomesBlackRain(w, true, true))
                && rains.All(w => !RM_FireEcoKernel.RainBecomesBlackRain(w, false, true));
            Row("forced_ordinary_rain_becomes_black_rain", new[] { "no_ordinary_rain" }, "fixed", ok, rains.Length * 2 + others.Length,
                "each of " + string.Join("/", rains) + " -> black rain on a Pyrelands map only; other weathers stand. Completeness of the rain list vs the loaded game is lane 2/stage 6");
        }

        // ---------------------------------------------------------------- ullai_graze_old_burns: the anchor is about two days old, never fresh
        {
            int seed = 2468, n = 4000; var rng = new Random(seed); string bad = null; int lag = 2 * Day;
            for (int k = 0; k < n && bad == null; k++)
            {
                var ticks = new List<int>(); int t = rng.Next(0, Day); int m = rng.Next(0, 30);
                for (int i = 0; i < m; i++) { t += rng.Next(1, Day / 2); ticks.Add(t); }
                int nowH = t + rng.Next(0, 4 * Day);
                int idx = RM_BurnKernel.HistoryIndexAgo(ticks, nowH, lag);
                if (idx >= 0 && nowH - ticks[idx] < lag) bad = "anchor younger than the lag: age " + (nowH - ticks[idx]) + " (m=" + m + ")";
                else if (idx < 0 && ticks.Any(x => nowH - x >= lag)) bad = "no anchor though a sample is old enough";
                else if (idx >= 0 && idx + 1 < ticks.Count && nowH - ticks[idx + 1] >= lag) bad = "not the newest qualifying sample";
            }
            var fresh = new List<int> { now - 2500, now - 1000 };
            bool freshOk = RM_BurnKernel.HistoryIndexAgo(fresh, now, lag) == -1
                && RM_BurnKernel.FollowBurnDecision(false, true, 0f, 5f, 10f) == RM_FollowBurnAction.Stay;
            Row("herd_anchor_never_a_fresh_burn", new[] { "ullai_graze_old_burns" }, "random", bad == null && freshOk, n + 2,
                "seed " + seed + "; HistoryIndexAgo returns the newest sample at least 2 days old or -1; only-fresh history -> no anchor, herd on ash stays" + (bad == null ? "" : "; " + bad));
        }

        // ---------------------------------------------------------------- burn_line_walks: never out for long, relights far from buildings
        {
            int quiet = 120000, retry = 2500, step = 60; int since = 0; int last = -999999; int firstReseed = -1;
            for (int tt = step; tt <= 400000; tt += step)
            {
                var d = RM_BurnKernel.KeepAlive(0, ref since, step, quiet, tt, last, retry);
                if (d == RM_ReseedDecision.Reseed) { firstReseed = tt; break; }
            }
            int s2 = 999999; bool present = RM_BurnKernel.KeepAlive(5, ref s2, step, quiet, 10, -1, retry) == RM_ReseedDecision.FiresPresent && s2 == 0;
            bool lawOk = !RM_BurnKernel.LawfulBurnCell(true, false, false, 1f, true, true) && !RM_BurnKernel.LawfulBurnCell(true, false, true, 1f, false, true)
                && !RM_BurnKernel.LawfulBurnCell(true, true, false, 1f, false, true) && !RM_BurnKernel.LawfulBurnCell(true, false, false, 1f, false, false)
                && RM_BurnKernel.LawfulBurnCell(true, false, false, 0.5f, false, true) && RM_BurnKernel.TooCloseToColony(31 * 31, 32f) && !RM_BurnKernel.TooCloseToColony(32 * 32, 32f);
            Row("smoulder_relights_after_quiet_far_from_colony", new[] { "burn_line_walks" }, "fixed", firstReseed > 0 && firstReseed <= quiet + retry && present && lawOk, 9,
                "first reseed at tick " + firstReseed + " after the last fire (quiet " + quiet + " = 2 days); fires present resets the clock " + present + "; never in home, roofed, fogged or within 32 of the colony " + lawOk);
        }

        // ---------------------------------------------------------------- furnacebeast_warms
        {
            int seed = 77, n = 4000; var rng = new Random(seed); string bad = null;
            for (int k = 0; k < n && bad == null; k++)
            {
                float rad = 0.5f + 10f * (float)rng.NextDouble(), mx = 30f * (float)rng.NextDouble(), st = 2f * (float)rng.NextDouble();
                float d1 = 12f * (float)rng.NextDouble(), d2 = d1 + 3f * (float)rng.NextDouble();
                float o1 = FurnaceWarmthMath.Offset(d1 * d1, rad, mx, st), o2 = FurnaceWarmthMath.Offset(d2 * d2, rad, mx, st);
                if (o1 < 0f || o1 > mx * st + 1e-4f) bad = "offset outside [0, max x strength]";
                else if (o2 > o1 + 1e-4f) bad = "warmer farther away";
                else if (d1 >= rad && o1 != 0f) bad = "warmth beyond the radius";
            }
            bool fixedOk = Near(FurnaceWarmthMath.Offset(0f, 4.9f, 14f, 1f), 14f) && FurnaceWarmthMath.Offset(25f, 4.9f, 14f, 1f) == 0f
                && FurnaceWarmthMath.Offset(1f, 4.9f, 14f, 0f) == 0f && FurnaceWarmthMath.Combine(3f, 5f) == 5f
                && !FurnaceWarmthMath.AuraReaches(true, true) && !FurnaceWarmthMath.AuraReaches(false, false)
                && FurnaceWarmthMath.RoomHeatCeiling(10f, 40f, 15f) == 55f && FurnaceWarmthMath.RoomHeatCeiling(10f, -20f, 15f) == 10f;
            Row("furnace_warmth_falls_off_and_switches_off", new[] { "furnacebeast_warms", "inv_settings_gate" }, "random", bad == null && fixedOk, n + 7,
                "seed " + seed + "; +14C at the beast, 0 at 5 cells, 0 at strength 0, two beasts = the warmer, no aura through walls" + (bad == null ? "" : "; " + bad));
        }
        {
            bool bare = !RM_FurnaceKernel.SleepIgnitionDue(false, 999999, false, 1250), awake = !RM_FurnaceKernel.SleepIgnitionDue(true, 999999, true, 1250);
            bool grace = !RM_FurnaceKernel.SleepIgnitionDue(false, 1249, true, 1250) && RM_FurnaceKernel.SleepIgnitionDue(false, 1250, true, 1250);
            float ratio = RM_FurnaceKernel.SizeRatio(9f, 3.2f); RM_FurnaceKernel.BedCells(ratio, 1, 2, out int lo, out int hi, out float spread);
            bool ok = bare && awake && grace && ratio >= 2.8f && lo >= 1 && hi >= lo && spread >= 1.5f;
            Row("furnace_bed_ignites_grass_never_bare_soil", new[] { "furnacebeast_warms" }, "fixed", ok, 5,
                "bare cell never rolls " + bare + ", awake never " + awake + ", grace 1250 ticks " + grace + "; giant ratio " + ratio.ToString("0.000", Inv) + " bed cells " + lo + ".." + hi + " spread " + spread.ToString("0.0", Inv));
        }
        {
            int seed = 11, n = 3000; var rng = new Random(seed); string bad = null;
            for (int k = 0; k < n && bad == null; k++)
            {
                float c = (float)rng.NextDouble(), amb = -40f + 100f * (float)rng.NextDouble();
                float st = RM_FurnaceKernel.ChargeStep(amb, rng.Next(2) == 0, 35f, 20f, 0.02f, 10f, 30f, 0.02f, 0.05f);
                float c2 = RM_FurnaceKernel.ClampCharge(c + st);
                if (c2 < 0f || c2 > 1f) bad = "charge outside [0,1]";
            }
            Row("furnace_charge_stays_in_unit_range", new[] { "furnacebeast_warms" }, "random", bad == null, n, "seed " + seed + (bad == null ? "" : "; " + bad));
        }

        // ---------------------------------------------------------------- firehawk_hunt_rewards (coverage of inv_firehawk_hunt_rewards)
        {
            int seed = 1313, n = 2000; var rng = new Random(seed); string bad = null; int sent = 0;
            bool announced = false;
            for (int k = 0; k < n; k++)
            {
                bool carry = rng.Next(3) == 0, home = rng.Next(4) != 0, fog = rng.Next(5) == 0;
                if (RM_FireHawkRewardsKernel.TryClaimSighting(ref announced, true, true, carry, home, fog))
                {
                    sent++; if (!carry || !home || fog) bad = "letter on a non-carry, off-home or fogged hawk";
                }
            }
            bool off = false; bool anyOff = false; for (int k = 0; k < 200; k++) anyOff |= RM_FireHawkRewardsKernel.TryClaimSighting(ref off, false, true, true, true, false);
            Row("firehawk_letter_exactly_once_switchable_off", new[] { "inv_firehawk_hunt_rewards" }, "random", bad == null && sent == 1 && !anyOff, n + 200,
                "seed " + seed + "; letters sent " + sent + " over " + n + " looks; with the letter switch off " + (anyOff ? "SENT" : "none") + (bad == null ? "" : "; " + bad));
        }
        {
            int seed = 400, n = 400; var rng = new Random(seed); int drops = 0;
            for (int k = 0; k < n; k++) if (RM_FireHawkRewardsKernel.TrophyDrops((float)rng.NextDouble(), 0.35f)) drops++;
            double mean = n * 0.35, sd = Math.Sqrt(n * 0.35 * 0.65);
            bool none = Enumerable.Range(0, 1000).All(i => !RM_FireHawkRewardsKernel.TrophyDrops(i / 1000f, 0f));
            bool ok = Math.Abs(drops - mean) <= 4 * sd && none && RM_FireHawkRewardsKernel.TrophyDrops(0f, 0.35f) && !RM_FireHawkRewardsKernel.TrophyDrops(0.35f, 0.35f);
            Row("crestfeather_35_percent_within_4_sigma", new[] { "inv_firehawk_hunt_rewards" }, "random", ok, n + 1002,
                "seed " + seed + "; " + drops + " of 400 (mean " + mean + ", 4 sigma " + (4 * sd).ToString("0.0", Inv) + "); chance 0 never drops " + none);
        }
        {
            bool ok = RM_FireHawkRewardsKernel.Compass8(0, 1) == 0 && RM_FireHawkRewardsKernel.Compass8(1, 1) == 1 && RM_FireHawkRewardsKernel.Compass8(1, 0) == 2
                && RM_FireHawkRewardsKernel.Compass8(0, -1) == 4 && RM_FireHawkRewardsKernel.Compass8(-1, 0) == 6 && RM_FireHawkRewardsKernel.Compass8(0, 0) == -1;
            Row("letter_compass_word", new[] { "inv_firehawk_hunt_rewards" }, "fixed", ok, 6, "N, NE, E, S, W and same-cell");
        }

        // ---------------------------------------------------------------- firehawk_lights_ahead: the drop is fuel, lawful, and the tries are bounded
        {
            int seed = 606, n = 600; var rng = new Random(seed); string bad = null; int found = 0;
            for (int k = 0; k < n && bad == null; k++)
            {
                int sx = rng.Next(8, 60), sz = rng.Next(8, 60), bucket = 8; var fuel = new bool[sx * sz]; var fires = new List<int>();
                for (int i = 0; i < fuel.Length; i++) { fuel[i] = rng.NextDouble() < 0.4; if (rng.NextDouble() < 0.03) fires.Add(i); }
                Func<int, int, bool> fuelCell = (x, z) => fuel[z * sx + x];
                var lawfulSet = new HashSet<int>(); for (int i = 0; i < fuel.Length; i++) if (rng.NextDouble() < 0.5) lawfulSet.Add(i);
                int calls = 0, maxTries = rng.Next(1, 6);
                Func<int, int, bool> lawful = (x, z) => { calls++; return lawfulSet.Contains(z * sx + x); };
                int[] fb = RM_FireHawkKernel.BucketFuel(sx, sz, bucket, fuelCell); bool[] fr = RM_FireHawkKernel.FireBuckets(sx, sz, bucket, fires);
                int c = RM_FireHawkKernel.PickDrop(sx, sz, bucket, fb, fr, rng.Next(sx), rng.Next(sz), fuelCell, lawful, maxTries);
                if (c >= 0) { found++; if (!fuel[c] || !lawfulSet.Contains(c)) bad = "drop on a non-fuel or unlawful cell"; }
                if (calls > maxTries) bad = "lawful asked " + calls + " times, max " + maxTries;
            }
            Row("firehawk_drop_is_fuel_and_lawful", new[] { "firehawk_lights_ahead" }, "random", bad == null, n,
                "seed " + seed + "; " + found + " drops picked; never a non-fuel or unlawful cell; tries bounded" + (bad == null ? "" : "; " + bad));
        }

        // ---------------------------------------------------------------- conservation: holds and stamps never shortened, ash never thinned by a fire
        {
            int seed = 123, n = 5000; var rng = new Random(seed); string bad = null;
            for (int k = 0; k < n && bad == null; k++)
            {
                int old = rng.Next(-1, 10 * Day), tnow = rng.Next(0, 10 * Day), dt = rng.Next(-100, 3 * Day);
                if (RM_FireEcoKernel.ExtendWatered(old, tnow, dt) < old) bad = "ExtendWatered shortened a stamp";
                else if (RM_FireEcoKernel.BurrowHeatHoldUntil(tnow, old, dt) < old) bad = "BurrowHeatHoldUntil shortened a hold";
                float depth = (float)rng.NextDouble(); int target = rng.Next(0, 4);
                float s = RM_FireEcoKernel.ScarAshStep(depth, target), l = RM_FireEcoKernel.ScarAshLaid(depth, target);
                if (s + 1e-6f < depth || l + 1e-6f < depth) bad = "a fire thinned the ash: " + depth + " -> " + s + "/" + l;
                else if (depth <= target * 0.25f && s > target * 0.25f + 1e-6f) bad = "step past the target";
                float ash = RM_FireEcoKernel.AshCoverOpacity(depth); if (ash < 0f || ash > 1f) bad = "opacity outside [0,1]";
            }
            Row("conservation_stamps_holds_and_ash", new[] { "ash_ground_and_blowing_ash", "fresh_burn_compounds_with_black_rain", "ashwallow_dives_unharmed" }, "random", bad == null, n * 4,
                "seed " + seed + "; watered stamps and dome holds never shortened; a fire's ash never thins a cell or passes its drift target" + (bad == null ? "" : "; " + bad));
        }
        {
            bool ok = RM_FireEcoKernel.OutdoorSandWear(true, 1.1f) > RM_FireEcoKernel.OutdoorSandWear(true, 0f)
                && RM_FireEcoKernel.AshWeatherSandRate(0.5f, true, false, 1f) == 0f && RM_FireEcoKernel.AshWeatherSandRate(0.5f, true, true, 1f) > 0f
                && RM_FireEcoKernel.AshWeatherSandRate(0.5f, false, true, 1f) == 0f;
            Row("black_rain_washes_ash_ash_fall_banks_it", new[] { "three_skies", "ash_ground_and_blowing_ash" }, "fixed", ok, 4,
                "black rain wear " + RM_FireEcoKernel.OutdoorSandWear(true, 1.1f).ToString("0.000", Inv) + " > dry " + RM_FireEcoKernel.OutdoorSandWear(true, 0f).ToString("0.0000", Inv) + "; ash fall lays only with accumulation on, on an ash map");
        }

        return fails == 0 ? 0 : 1;
    }
}
