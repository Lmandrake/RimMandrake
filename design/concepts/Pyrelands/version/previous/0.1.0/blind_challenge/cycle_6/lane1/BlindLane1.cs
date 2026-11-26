// Pyrelands blind challenge cycle 6, lane 1: written from the bars (tree.json, sheet.md) and the changed kernels alone.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimMandrake.Pyrelands;
using RM_CarryCell = RimMandrake.Pyrelands.RM_BurnKernel.RM_CarryCell;

static class BlindLane1
{
    static int fails;
    static void Row(string id, string bars, string kind, string verdict, int cases, string detail)
    {
        if (verdict == "FAIL") fails++;
        Console.WriteLine("{\"id\":\"" + id + "\",\"bars\":[" + string.Join(",", bars.Split(' ').Select(b => "\"" + b + "\"")) + "],\"kind\":\"" + kind
            + "\",\"verdict\":\"" + verdict + "\",\"cases\":" + cases + ",\"detail\":\"" + detail.Replace("\\", "/").Replace("\"", "'") + "\"}");
    }
    static void T(string id, string bars, string kind, int cases, Func<int, string> one)
    {
        for (int seed = 0; seed < cases; seed++)
        {
            string r;
            try { r = one(seed); } catch (Exception e) { r = "threw " + e.GetType().Name + " " + e.Message; }
            if (r != null) { Row(id, bars, kind, "FAIL", seed + 1, "seed=" + seed + " " + r); return; }
        }
        Row(id, bars, kind, "PASS", cases, "seeds 0.." + (cases - 1));
    }

    const string WIND = "fire_walks_with_wind burn_line_walks";
    static void Main()
    {
        CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
        Carry(); Flank(); Sims(); History(); Foam(); Probe();
        Row("nk_lightning_breaker", "inv_lightning_breaker", "info", "INFO", 0, "absence bar: decided by text_absent_breaker in lane1 python rows");
        Environment.Exit(fails > 0 ? 1 : 0);
    }

    // ---------------------------------------------------------------- carry
    static void Carry()
    {
        T("probes_never_upwind", WIND, "random", 20000, s =>
        {
            var r = new Random(s);
            float b = (float)(r.NextDouble() * 1440 - 720); int reach = 1 + r.Next(3);
            var dx = new int[3 * reach]; var dz = new int[3 * reach];
            RM_BurnKernel.WindProbes(b, (float)r.NextDouble(), (float)r.NextDouble(), reach, dx, dz);
            double wx = Math.Sin(b * Math.PI / 180), wz = Math.Cos(b * Math.PI / 180);
            for (int i = 0; i < dx.Length; i++)
            {
                double along = dx[i] * wx + dz[i] * wz;
                if (along <= 0) return "b=" + b + " probe " + dx[i] + "," + dz[i] + " along " + along;
                if (!RM_BurnKernel.Downwind(dx[i], dz[i], (float)wx, (float)wz)) return "b=" + b + " probe outside Downwind cone " + dx[i] + "," + dz[i];
            }
            if (dx.Zip(dz, (a, c) => (a, c)).Distinct().Count() != dx.Length) return "b=" + b + " duplicate probe";
            return null;
        });
        T("probes_mean_heading_is_wind", WIND, "random", 72, s =>
        {
            var r = new Random(s); float b = s * 5f; double sx = 0, sz = 0; int n = 4000;
            var dx = new int[3]; var dz = new int[3];
            for (int i = 0; i < n; i++) { RM_BurnKernel.WindProbes(b, (float)r.NextDouble(), (float)r.NextDouble(), 1, dx, dz); double l = Math.Sqrt(dx[0] * dx[0] + dz[0] * dz[0]); sx += dx[0] / l; sz += dz[0] / l; }
            double h = Math.Atan2(sx, sz) * 180 / Math.PI; double d = Math.Abs(((h - b) % 360 + 540) % 360 - 180);
            return d <= 5 ? null : "b=" + b + " heading=" + h;
        });
        T("carry_plan_lights_fuel_only_at_most_two_adjacent", WIND, "random", 20000, s =>
        {
            var r = new Random(s); var g = new Dictionary<(int, int), int>(); double pf = r.NextDouble(), pb = r.NextDouble() * 0.5;
            Func<int, int, int> at = (x, z) => { if (!g.TryGetValue((x, z), out int v)) { double q = r.NextDouble(); v = q < pf ? 1 : q < pf + pb ? 2 : 0; g[(x, z)] = v; } return v; };
            Func<int, int, RM_CarryCell> cell = (x, z) => at(x, z) == 1 ? RM_CarryCell.Fuel : at(x, z) == 2 ? RM_CarryCell.Burning : RM_CarryCell.Bare;
            var anch = new HashSet<(int, int)>(); for (int i = 0; i < r.Next(10); i++) anch.Add((r.Next(-9, 10), r.Next(-9, 10)));
            Func<int, int, bool> anchor = (x, z) => at(x, z) == 2 || anch.Contains((x, z));
            float b = (float)(r.NextDouble() * 360), r1 = (float)r.NextDouble(), r2 = (float)r.NextDouble(), rs = (float)r.NextDouble();
            int heal = r.Next(0, 6), reach = 1 + r.Next(2);
            var ox = new int[2]; var oz = new int[2];
            int n = RM_BurnKernel.CarryPlan(b, r1, r2, rs, reach, heal, cell, anchor, ox, oz, out bool healed);
            if (n < 0 || n > 2) return "n=" + n;
            if (healed != (n == 2)) return "healed " + healed + " n " + n;
            var px = new int[3 * reach]; var pz = new int[3 * reach]; RM_BurnKernel.WindProbes(b, r1, r2, reach, px, pz);
            int want = -1; bool merged = false;
            for (int i = 0; i < px.Length; i++) { var c = cell(px[i], pz[i]); if (c == RM_CarryCell.Burning) { merged = true; break; } if (c == RM_CarryCell.Fuel) { want = i; break; } }
            if (merged || want < 0) return n == 0 ? null : "lit " + n + " where the line merges or nothing burns";
            if (n == 0 || ox[0] != px[want] || oz[0] != pz[want]) return "first cell wrong";
            if (n == 2)
            {
                if (heal == 0) return "healed at healReach 0";
                if (cell(ox[1], oz[1]) != RM_CarryCell.Fuel) return "second not fuel";
                int hx = ox[1] - ox[0], hz = oz[1] - oz[0];
                if (Math.Max(Math.Abs(hx), Math.Abs(hz)) != 1) return "second not adjacent";
                double wx = Math.Sin(b * Math.PI / 180), wz = Math.Cos(b * Math.PI / 180);
                double cos = (hx * wx + hz * wz) / Math.Sqrt(hx * hx + hz * hz);
                if (cos > 0.39) return "heal goes ahead, cos " + cos;
                bool closed = false; for (int k = 2; k <= heal + 1; k++) closed |= anchor(ox[0] + k * hx, oz[0] + k * hz);
                if (!closed) return "healed a gap nothing closes";
            }
            return null;
        });
        T("carry_due_once_and_vanilla_spread_exclusive", WIND + " inv_settings_gate", "sweep", 1, _ =>
        {
            foreach (bool en in new[] { true, false }) foreach (bool fs in new[] { true, false }) foreach (bool pg in new[] { true, false }) foreach (bool al in new[] { true, false })
                foreach (int t in new[] { 0, 1199, 1200, 1399, 1400, 1600, 5000 })
                {
                    bool due = RM_BurnKernel.WindCarryDue(en, fs, pg, al, t, 1400);
                    if (due != (en && fs && pg && !al && t >= 1400)) return "due " + en + fs + pg + al + t;
                    if (due && RM_BurnKernel.VanillaSpreadRuns(en, fs, pg)) return "both spreads";
                    if (!en && !RM_BurnKernel.VanillaSpreadRuns(en, fs, pg)) return "switch off leaves no spread";
                }
            return null;
        });
        T("recent_burn_window", WIND, "random", 5000, s =>
        {
            var r = new Random(s); int now = r.Next(0, 2000000), bt = r.Next(-1, now + 1), w = r.Next(0, 100000); bool bu = r.Next(4) == 0;
            bool want = bu || (bt >= 0 && now - bt <= w);
            return RM_BurnKernel.RecentBurn(bu, bt, now, w) == want ? null : "now " + now + " bt " + bt + " w " + w;
        });
        T("carry_age_in_range_smooth_deterministic", "burn_line_walks", "random", 20000, s =>
        {
            var r = new Random(s); int x = r.Next(-400, 400), z = r.Next(-400, 400), seed = r.Next(int.MinValue, int.MaxValue);
            int a = RM_BurnKernel.CarryAge(x, z, seed, 28);
            if (a < RM_BurnKernel.WindCarryTicks || a > RM_BurnKernel.WindCarryTicks + RM_BurnKernel.WindCarryExtraTicks) return "age " + a;
            if (a != RM_BurnKernel.CarryAge(x, z, seed, 28)) return "not deterministic";
            if (RM_BurnKernel.CarryAge(x, z, seed, r.Next(0, 4)) != RM_BurnKernel.WindCarryTicks) return "spent fuel waits";
            if (a >= 1800) return "outlives the grass";
            int n = RM_BurnKernel.GroundNoise(x, z, seed, 8), m = RM_BurnKernel.GroundNoise(x + 1, z, seed, 8);
            if (n < 0 || n > 1023) return "noise " + n;
            if (Math.Abs(n - m) > 1023 / 8 + 1) return "noise jumps " + n + " " + m;
            return null;
        });
        T("ground_noise_not_constant_across_maps", "burn_line_walks", "random", 200, s =>
        {
            var set = new HashSet<int>(); for (int k = 0; k < 20; k++) set.Add(RM_BurnKernel.CarryAge(50, 50, s * 1000 + k, 28));
            return set.Count > 5 ? null : "only " + set.Count + " ages over 20 map seeds";
        });
    }

    // ---------------------------------------------------------------- flank
    static void Flank()
    {
        T("flank_plan_bounds", WIND, "random", 30000, s =>
        {
            var r = new Random(s); var g = new Dictionary<(int, int), int>(); double pf = 0.3 + 0.7 * r.NextDouble(), pb = (1 - pf) * r.NextDouble() * 0.4;
            Func<int, int, int> at = (x, z) => { if (!g.TryGetValue((x, z), out int v)) { double q = r.NextDouble(); v = q < pf ? 1 : q < pf + pb ? 2 : 0; g[(x, z)] = v; } return v; };
            Func<int, int, RM_CarryCell> cell = (x, z) => at(x, z) == 1 ? RM_CarryCell.Fuel : at(x, z) == 2 ? RM_CarryCell.Burning : RM_CarryCell.Bare;
            Func<int, int, bool> anchor = (x, z) => (x == 0 && z == 0) || at(x, z) == 2;
            float b = (float)(r.NextDouble() * 360), rs = (float)r.NextDouble();
            var ox = new int[2]; var oz = new int[2];
            int n = RM_BurnKernel.CarryPlan(b, (float)r.NextDouble(), (float)r.NextDouble(), rs, 2, RM_BurnKernel.HealReach, cell, anchor, ox, oz, out bool healed);
            int x0 = r.Next(-50, 300), z0 = r.Next(-50, 300), seed = r.Next();
            var bx = (int[])ox.Clone(); var bz = (int[])oz.Clone();
            if (RM_BurnKernel.FlankPlan(b, rs, x0, z0, seed, 0, cell, anchor, ox, oz, n, healed) != n) return "healReach 0 still flanks";
            int m = RM_BurnKernel.FlankPlan(b, rs, x0, z0, seed, RM_BurnKernel.HealReach, cell, anchor, ox, oz, n, healed);
            if (!(m == n || m == 0 || m == n + 1)) return "m " + m + " n " + n;
            if (m > 2) return "lights three";
            if (n == 0 && m != 0) return "a fire that carries nothing opens a flank";
            for (int i = 0; i < n; i++) if (ox[i] != bx[i] || oz[i] != bz[i]) return "carried cell moved";
            if (m == n + 1)
            {
                if (healed) return "opened after a heal";
                if (cell(ox[n], oz[n]) != RM_CarryCell.Fuel) return "opens into no fuel";
                int hx = ox[n] - ox[0], hz = oz[n] - oz[0];
                if (Math.Max(Math.Abs(hx), Math.Abs(hz)) != 1) return "flank not adjacent";
                double cos = (hx * Math.Sin(b * Math.PI / 180) + hz * Math.Cos(b * Math.PI / 180)) / Math.Sqrt(hx * hx + hz * hz);
                if (Math.Abs(cos) > 0.39) return "flank not beside, cos " + cos;
                for (int k = 1; k <= RM_BurnKernel.HealReach + 1; k++) if (anchor(hx * k, hz * k)) return "opens on a side that burns";
            }
            return null;
        });
        T("lone_fire_never_closes", "burn_line_walks", "random", 5000, s =>
        {   // a lone fire in full grass: no bar lets the only fire put itself out
            var r = new Random(s); float b = (float)(r.NextDouble() * 360), rs = (float)r.NextDouble();
            Func<int, int, RM_CarryCell> cell = (x, z) => x == 0 && z == 0 ? RM_CarryCell.Burning : RM_CarryCell.Fuel;
            Func<int, int, bool> anchor = (x, z) => x == 0 && z == 0;
            var ox = new int[2]; var oz = new int[2];
            int n = RM_BurnKernel.CarryPlan(b, (float)r.NextDouble(), (float)r.NextDouble(), rs, 2, RM_BurnKernel.HealReach, cell, anchor, ox, oz, out bool h);
            int m = RM_BurnKernel.FlankPlan(b, rs, r.Next(250), r.Next(250), r.Next(), RM_BurnKernel.HealReach, cell, anchor, ox, oz, n, h);
            return m >= 1 ? null : "lone fire not carried, b=" + b;
        });
    }

    // ---------------------------------------------------------------- whole-map fire
    class Map
    {
        public int W, H, seed; public bool[] fuel; public int[] lit, burn; public float[] hp; public bool[] carried; public Random r; public float bearing;
        public List<int> live = new List<int>(); public int now, maxLive, burned;
        public Map(int w, int h, int sd, double cover, float b)
        {
            W = w; H = h; seed = sd * 7919 + 13; r = new Random(sd); bearing = b;
            fuel = new bool[w * h]; lit = new int[w * h]; burn = new int[w * h]; hp = new float[w * h]; carried = new bool[w * h];
            for (int i = 0; i < w * h; i++) { fuel[i] = r.NextDouble() < cover; lit[i] = -1; burn[i] = -1; hp[i] = 28; }
        }
        bool In(int x, int z) => x >= 0 && z >= 0 && x < W && z < H;
        public bool Light(int x, int z) { if (!In(x, z)) return false; int i = z * W + x; if (!fuel[i] || lit[i] >= 0) return false; lit[i] = now; carried[i] = false; burn[i] = now; live.Add(i); burned++; return true; }
        public void Run(int ticks)
        {
            int end = now + ticks;
            for (; now < end && live.Count > 0; now += 50)
            {
                if (live.Count > maxLive) maxLive = live.Count;
                foreach (int i in live.ToArray())
                {
                    int x = i % W, z = i / W, age = now - lit[i];
                    int beats = age / 150; float left = 28; for (int k = 1; k <= beats; k++) left -= 1.875f + 0.54f * Math.Min(1.75f, 0.1f + 0.132f * k);
                    if (age > 0 && age % 150 == 0) { burn[i] = now; }
                    if (!carried[i] && age >= RM_BurnKernel.CarryAge(x, z, seed, (int)Math.Ceiling(Math.Max(0, left))))
                    {
                        carried[i] = true;
                        Func<int, int, RM_CarryCell> cell = (dx, dz) => !In(x + dx, z + dz) ? RM_CarryCell.Bare : lit[(z + dz) * W + x + dx] >= 0 ? RM_CarryCell.Burning : fuel[(z + dz) * W + x + dx] ? RM_CarryCell.Fuel : RM_CarryCell.Bare;
                        Func<int, int, bool> anchor = (dx, dz) => In(x + dx, z + dz) && RM_BurnKernel.RecentBurn(lit[(z + dz) * W + x + dx] >= 0, burn[(z + dz) * W + x + dx], now, RM_BurnKernel.HealRecentTicks);
                        var ox = new int[2]; var oz = new int[2]; float rs = (float)r.NextDouble();
                        int n = RM_BurnKernel.CarryPlan(bearing, (float)r.NextDouble(), (float)r.NextDouble(), rs, RM_BurnKernel.WindCarryReach, RM_BurnKernel.HealReach, cell, anchor, ox, oz, out bool healed);
                        n = RM_BurnKernel.FlankPlan(bearing, rs, x, z, seed, RM_BurnKernel.HealReach, cell, anchor, ox, oz, n, healed);
                        for (int k = 0; k < n; k++) Light(x + ox[k], z + oz[k]);
                    }
                    if (left <= 0) { lit[i] = -1; fuel[i] = false; live.Remove(i); }
                }
            }
        }
    }
    static double[] Extents(Map m, int cx, int cz)
    {
        double wx = Math.Sin(m.bearing * Math.PI / 180), wz = Math.Cos(m.bearing * Math.PI / 180), down = 0, up = 0, side = 0;
        for (int i = 0; i < m.burn.Length; i++) if (m.burn[i] >= 0)
        { double dx = i % m.W - cx, dz = i / m.W - cz, a = dx * wx + dz * wz, c = Math.Abs(dx * wz - dz * wx); down = Math.Max(down, a); up = Math.Max(up, -a); side = Math.Max(side, c); }
        return new[] { down, up, side };
    }
    static void Sims()
    {
        // lone fire: runs downwind, fans out, never floods
        int wide = 0, runs = 0; double minDown = 1e9, maxFrac = 0; string bad = null; int deadEarly = 0;
        for (int s = 0; s < 64; s++)
        {
            float b = s < 32 ? (s % 8) * 45f : (float)(new Random(s).NextDouble() * 360);
            var m = new Map(200, 200, s, 1.0, b); m.Light(100, 100); m.Run(4 * 60000); runs++;
            var e = Extents(m, 100, 100); minDown = Math.Min(minDown, e[0]); maxFrac = Math.Max(maxFrac, m.burned / 40000.0);
            if (e[1] > 8) bad = bad ?? "s=" + s + " b=" + b + " upwind " + e[1];
            if (m.burned / 40000.0 > 0.5) bad = bad ?? "s=" + s + " burned " + m.burned;
            if (e[0] < 60) { deadEarly++; bad = bad ?? "s=" + s + " b=" + b + " died at " + e[0] + " cells downwind in full grass"; }
            if (m.burned >= 4 * e[0]) wide++;
        }
        Row("sim_lone_fire_runs_downwind_and_fans_out", WIND, "random", bad == null && wide >= 60 ? "PASS" : "FAIL", runs,
            (bad ?? "ok") + " | minDown=" + minDown.ToString("0") + " maxFrac=" + maxFrac.ToString("0.00") + " wideRuns=" + wide + "/" + runs + " diedEarly=" + deadEarly);
        // fire_walks_with_wind strip: 61x21, 9-cell line, both bearings, 10,000 ticks; outer three lanes never burn; few fires at once
        foreach (float b in new[] { 90f, 270f })
        {
            int outer = 0, max = 0, noLean = 0; string first = null;
            for (int s = 0; s < 500; s++)
            {
                var m = new Map(61, 21, s + (b > 180 ? 5000 : 0), 1.0, b);
                for (int z = 6; z < 15; z++) m.Light(30, z);
                m.Run(10000);
                bool o = false; int dn = 0, up = 0;
                for (int i = 0; i < m.burn.Length; i++) if (m.burn[i] >= 0) { int z = i / 61, x = i % 61 - 30; if (z < 3 || z > 17) o = true; int a = b == 90f ? x : -x; dn = Math.Max(dn, a); up = Math.Max(up, -a); }
                if (o) { outer++; first = first ?? "s=" + s; }
                if (dn <= up) { noLean++; first = first ?? "s=" + s + " dn " + dn + " up " + up; }
                max = Math.Max(max, m.maxLive);
            }
            Row("sim_strip_" + (int)b, "fire_walks_with_wind", "random", noLean == 0 && outer <= 2 && max <= 27 ? "PASS" : "FAIL", 500,
                "outer-lane runs " + outer + "/500, no lean " + noLean + ", most fires at once " + max + " (limit 27 = 3x the 9 lit) " + first);
        }
        // a 60-cell front, every 3rd cell lit, on a 250 map: never most of the map in four days, strands heal
        double worst = 0, worstStrand = 0; string badF = null;
        for (int s = 0; s < 24; s++)
        {
            float b = s * 15f; var m = new Map(250, 250, s, s % 3 == 0 ? 0.75 : 1.0, b);
            double wx = Math.Sin(b * Math.PI / 180), wz = Math.Cos(b * Math.PI / 180);
            RM_BurnKernel.FrontLine(RM_BurnKernel.AcrossWind(b), 60, out int[] dx, out int[] dz);
            int cx = 125 - (int)(100 * wx), cz = 125 - (int)(100 * wz); int lit = 0;
            for (int i = 0; i < 60; i += 3) if (m.Light(cx + dx[i], cz + dz[i])) lit++;
            m.Run(4 * 60000); double f = m.burned / 62500.0; worst = Math.Max(worst, f);
            if (f > 0.5) badF = badF ?? "s=" + s + " burned " + f;
            if (m.burned < lit * 60) badF = badF ?? "s=" + s + " b=" + b + " cover " + (s % 3 == 0 ? 0.75 : 1) + " front died: burned " + m.burned + " from " + lit;
            if (s % 3 != 0) { int strand = 0, tot = 0; for (int i = 0; i < m.burn.Length; i++) if (m.burn[i] >= 0) { int x = i % 250, z = i / 250; if (x < 2 || z < 2 || x > 247 || z > 247) continue; tot++; int nb = 0; for (int k = 0; k < 8; k++) if (m.burn[(z + RM_BurnKernel.Dir8Z[k]) * 250 + x + RM_BurnKernel.Dir8X[k]] >= 0) nb++; if (nb <= 2) strand++; } worstStrand = Math.Max(worstStrand, strand / Math.Max(1.0, tot)); }
        }
        Row("sim_front_walks_never_floods", "burn_line_walks", "random", badF == null && worstStrand < 0.25 ? "PASS" : "FAIL", 24, (badF ?? "ok") + " worst burned share " + worst.ToString("0.00") + ", worst one-cell-strand share " + worstStrand.ToString("0.00"));
        // conservation: every fire was lit by at most one carrier, never more than two a carrier -> live fires bounded by 2^k is moot; check nothing burns twice
    }

    // ---------------------------------------------------------------- history
    static void History()
    {
        T("history_probe_counts_after_prune", "ullai_graze_old_burns", "random", 20000, s =>
        {
            var r = new Random(s); var t = new List<int>(); var c = new List<int>(); int now = 0;
            for (int i = 0; i < r.Next(0, 30); i++) { now += r.Next(1, 20000); t.Add(now); c.Add(i); }
            now += r.Next(0, 400000); int keep = r.Next(0, 300000), ago = r.Next(0, 300000);
            var ot = t.ToList();
            var keepT = ot.Where(q => now - q <= keep).ToList();
            int want = keepT.FindLastIndex(q => q <= now - ago);
            int at = RM_BurnKernel.ProbeHistory(t, c, now, keep, ago, out int n, out int old, out int nw, out int nwAt);
            if (at != want) return "ago " + at + " want " + want;
            if (n != keepT.Count || t.Count != n || c.Count != n) return "count " + n + " want " + keepT.Count;
            if (n == 0) return old == -1 && nw == -1 && nwAt == -1 ? null : "empty reads " + old + " " + nw + " " + nwAt;
            if (old != keepT[0] || nw != keepT[n - 1] || nwAt != n - 1) return "ends";
            if (c[0] != ot.Count - n) return "cells not pruned with ticks";
            return null;
        });
    }

    // ---------------------------------------------------------------- foam
    static void Foam()
    {
        T("foam_gate_exhaustive", "firefoam_sprayer_reaches_the_fruit inv_settings_gate", "fixed", 128, s =>
        {
            bool B(int k) => (s >> k & 1) == 1;
            var g = RM_FoamPathKernel.Gate(B(0), B(1), B(2), B(3), B(4), B(5), B(6));
            bool want = B(0) && B(1) && B(2) && !B(3) && !B(4) && !B(5) && B(6);
            if ((g == RM_FoamGate.Foam) != want) return "gate " + g;
            if (!B(0) && g != RM_FoamGate.Disabled) return "switch off reads " + g;
            return null;
        });
        T("foam_target_is_first_hittable_fire_in_the_way", "firefoam_sprayer_reaches_the_fruit", "random", 30000, s =>
        {
            var r = new Random(s); var px = new List<int>(); var pz = new List<int>(); int x = 0, z = 0, len = r.Next(0, 30);
            for (int i = 0; i < len; i++) { int d = r.Next(8); x += RM_BurnKernel.Dir8X[d]; z += RM_BurnKernel.Dir8Z[d]; px.Add(x); pz.Add(z); }
            var fire = new HashSet<(int, int)>(); for (int i = 0; i < r.Next(0, 25); i++) fire.Add((r.Next(-12, 13), r.Next(-12, 13)));
            var blocked = new HashSet<(int, int)>(); for (int i = 0; i < r.Next(0, 6); i++) blocked.Add((r.Next(-12, 13), r.Next(-12, 13)));
            Func<int, int, bool> hit = (a, b) => a * a + b * b <= 9.9 * 9.9 && !blocked.Contains((a, b));
            bool got = RM_FoamPathKernel.PickTarget(0, 0, px, pz, (a, b) => fire.Contains((a, b)), hit, out int tx, out int tz);
            // oracle: rank of a cell = the first path index (own cell = -1) it equals or touches
            int best = int.MaxValue;
            foreach (var f in fire) { if (!hit(f.Item1, f.Item2)) continue; for (int i = -1; i < Math.Min(20, len); i++) { int cx = i < 0 ? 0 : px[i], cz = i < 0 ? 0 : pz[i]; if (Math.Max(Math.Abs(f.Item1 - cx), Math.Abs(f.Item2 - cz)) <= 1) { best = Math.Min(best, i); break; } } }
            if (!got) return best == int.MaxValue ? null : "missed a fire in the way at path index " + best;
            if (!fire.Contains((tx, tz)) || !hit(tx, tz)) return "target not burning or not hittable";
            int rank = int.MaxValue; for (int i = -1; i < Math.Min(20, len); i++) { int cx = i < 0 ? 0 : px[i], cz = i < 0 ? 0 : pz[i]; if (Math.Max(Math.Abs(tx - cx), Math.Abs(tz - cz)) <= 1) { rank = i; break; } }
            if (rank != best) return "rank " + rank + " best " + best;
            if (!RM_FoamPathKernel.InTheWay(tx, tz, 0, 0, px, pz)) return "InTheWay disagrees";
            return null;
        });
        T("foam_null_path_safe", "firefoam_sprayer_reaches_the_fruit", "fixed", 1, _ =>
            RM_FoamPathKernel.PickTarget(3, 3, null, null, (a, b) => a == 3 && b == 3, (a, b) => true, out int tx, out int tz) && tx == 3 && tz == 3 ? null : "own cell not foamed with no path");
        T("foam_walk_never_steps_on_fire", "firefoam_sprayer_reaches_the_fruit", "random", 3000, s =>
        {   // a burn band between carrier and fruit; a splash puts out radius 2.5; the carrier must never enter or touch a fire
            var r = new Random(s); int band = r.Next(3, 15), w = r.Next(1, 8); var fire = new HashSet<(int, int)>();
            for (int q = band; q < band + w; q++) for (int k = -12; k <= 12; k++) if (r.NextDouble() < 0.85) fire.Add((q, k));
            int px = 0, pz = 0, shots = 0;
            while (px < 28)
            {
                var ax = new List<int>(); var az = new List<int>(); for (int q = px + 1; q <= 28; q++) { ax.Add(q); az.Add(0); }
                if (RM_FoamPathKernel.PickTarget(px, pz, ax, az, (a, b) => fire.Contains((a, b)), (a, b) => (a - px) * (a - px) + (b - pz) * (b - pz) <= 9.9 * 9.9, out int tx, out int tz))
                { if (++shots > 200) return "endless foam"; int cx = tx, cz = tz; fire.RemoveWhere(f => (f.Item1 - cx) * (f.Item1 - cx) + (f.Item2 - cz) * (f.Item2 - cz) <= 6.25); continue; }
                px++;
                for (int a = -1; a <= 1; a++) for (int b = -1; b <= 1; b++) if (fire.Contains((px + a, pz + b))) return "walked beside a fire at " + px;
            }
            return null;
        });
    }

    // ---------------------------------------------------------------- probe
    static Dictionary<string, string> Parse(string l) => l.Split(';').Where(p => p.Contains("=")).ToDictionary(p => p.Substring(0, p.IndexOf('=')), p => p.Substring(p.IndexOf('=') + 1));
    static void Probe()
    {
        T("probe_parts_sum_over_shipped_ranges", "ash_fertility_probe fresh_burn_compounds_with_black_rain", "sweep", 30000, s =>
        {
            var r = new Random(s); float dry = (float)r.NextDouble(), wet = 0.4f + 1.6f * (float)r.NextDouble(), bon = 1.5f * (float)r.NextDouble(); int dur = (int)((1 + 19 * r.NextDouble()) * 60000);
            int now = r.Next(0, 5000000); int bt = r.Next(3) == 0 ? -1 : Math.Max(-1, now - r.Next(0, 25 * 60000)); bool watered = r.Next(2) == 0, won = r.Next(5) > 0, gate = r.Next(5) > 0; float cap = 10f;
            float bonus = RM_FireEcoKernel.BurnBonus(bt, now, bon, dur);
            double want = bt < 0 || now < bt ? 0 : Math.Max(0, bon * (1.0 - (now - bt) / (double)dur));
            if (Math.Abs(want - bonus) > 1e-4) return "bonus " + bonus + " want " + want;
            float f = RM_FireEcoKernel.AshFertility(dry, wet, watered, won, bonus, cap);
            if (Math.Abs(f - ((won && watered ? wet : dry) + bonus)) > 1e-4) return "fertility " + f;
            bool rain = r.Next(2) == 0, roof = r.Next(2) == 0;
            var p = Parse(RM_FireEcoKernel.ProbeLine(f, "RM_FE_Ash_Deep", true, watered, dry, wet, bonus, bt, now, dur, rain, roof, 0, true, won, gate, cap));
            double D(string k) => double.Parse(p[k], CultureInfo.InvariantCulture);
            if (p.ContainsKey("refused") != (!won || !gate)) return "refused wrong";
            if (Math.Abs(D("base") - dry) > 6e-4 || Math.Abs(D("bonus") - bonus) > 6e-4) return "base/bonus";
            if (Math.Abs(D("lift") - (won && watered ? wet - dry : 0)) > 6e-4) return "lift";
            if (Math.Abs(D("base") + D("lift") + D("bonus") - D("expected")) > 3e-3) return "parts do not sum";
            if (won && gate && p["consistent"] != "True") return "consistent " + p["consistent"];
            if (p["rainOnCell"] != (rain && !roof).ToString()) return "rainOnCell";
            if (bt >= 0 && Math.Abs(D("bonusAgeDays") - (now - bt) / 60000.0) > 6e-3) return "age";
            if (bt < 0 && D("bonusAgeDays") != -1) return "never burned age";
            if (won && gate && bonus > 0.01f) { var q = Parse(RM_FireEcoKernel.ProbeLine(dry, "RM_FE_Ash_Deep", true, watered, dry, wet, bonus, bt, now, dur, rain, roof, 0, true, won, gate, cap)); if ((won && watered ? wet : dry) + bonus - dry > 0.002 && q["consistent"] != "False") return "a probe that hands back the base reads consistent"; }
            return null;
        });
        T("wet_fresh_beats_dry_fresh_and_wet_old_at_defaults", "fresh_burn_compounds_with_black_rain ash_fertility_probe", "fixed", 1, _ =>
        {
            float b = RM_FireEcoKernel.BurnBonus(0, 60000, 0.5f, 6 * 60000);
            float wf = RM_FireEcoKernel.AshFertility(.7f, 1.4f, true, true, b, 10), df = RM_FireEcoKernel.AshFertility(.7f, 1.4f, false, true, b, 10), wo = RM_FireEcoKernel.AshFertility(.7f, 1.4f, true, true, 0, 10);
            return wf > df && wf > wo && RM_FireEcoKernel.BurnBonus(0, 6 * 60000, .5f, 6 * 60000) == 0 ? null : wf + " " + df + " " + wo;
        });
        T("mechanics_gate_table", "inv_settings_gate", "fixed", 8, s =>
        {
            bool m = (s & 1) > 0, sp = (s & 2) > 0, so = (s & 4) > 0;
            return RM_FireEcoKernel.MechanicsOn(m, sp, so) == (m && (!sp || so)) ? null : "gate " + s;
        });
    }
}
