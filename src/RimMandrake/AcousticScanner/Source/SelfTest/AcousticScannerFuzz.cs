// Approach B for the Acoustic Scanner: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_AcousticKernel.cs):
//   band   pulse banding on random maps / hit clouds / origins against an independent spec, plus the invariants the item
//          promises: every band sits inside the map at full block size, every hit is covered by a band of its own target,
//          the reading does not depend on hit order, and scaling a target's weights changes nothing
//   gate   CanPulse's decision table exhaustively (6 flags x ticks) against an ordered-rule spec
//   clock  cooldown lifecycle over random settings (no two pulses closer than the cooldown, a pulse allowed the tick it is
//          due) and the overlay lifetime window
//   ship   the landed-ship test exhaustively over small footprints
//   units  constants, clamps and the best-tier line
// A failing case is printed as `family seed N: message | detail`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.AcousticScanner.SelfTest
{
    internal static class AcousticScannerFuzz
    {
        public static long Cases, Steps;
        public static long CornerSlides, EdgeSlides, StrongBands, ModerateBands, FaintBands, LoneHits, Refused, Allowed, Tiny;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private static string Fmt(RM_KBand b) { return $"t{b.targetIndex}:{b.tier}@({b.x},{b.z}){b.w}x{b.h}"; }

        // ════════════════════════ band ════════════════════════
        private sealed class BandCase
        {
            public int mapW, mapH, bandSetting, ox, oz;
            public List<List<RM_KCell>> hits = new List<List<RM_KCell>>();
            public List<float> weights = new List<float>();
            public override string ToString()
            {
                return $"map {mapW}x{mapH} band {bandSetting} origin ({ox},{oz}) targets [" +
                    string.Join(" ; ", hits.Select((h, i) => $"w{(i < weights.Count ? weights[i].ToString() : "-")}:" + string.Join(",", h.Take(12).Select(c => $"({c.x},{c.z})")) + (h.Count > 12 ? "+" + (h.Count - 12) : ""))) + "]";
            }
        }

        private static BandCase GenBand(Random r)
        {
            var c = new BandCase();
            bool tiny = r.Next(8) == 0;
            c.mapW = tiny ? r.Next(1, 9) : r.Next(7, 90);
            c.mapH = tiny ? r.Next(1, 9) : r.Next(7, 90);
            if (tiny) Tiny++;
            int[] raw = { -5, 0, 3, 6, 7, 8, 11, 11, 11, 13, 25, 30 };
            c.bandSetting = r.Next(3) == 0 ? r.Next(-4, 31) : raw[r.Next(raw.Length)];
            int b = Math.Max(c.bandSetting, RM_AcousticKernel.MinBandSize);
            c.ox = r.Next(0, b); c.oz = r.Next(0, b);
            int targets = r.Next(0, 5);
            float[] ws = { 0.5f, 1f, 1f, 2f, 5f, 0f, -1f };
            for (int t = 0; t < targets; t++)
            {
                var list = new List<RM_KCell>();
                int kind = r.Next(6);
                int n = kind == 0 ? 0 : kind == 1 ? 1 : r.Next(2, 60);
                int cx = r.Next(c.mapW), cz = r.Next(c.mapH);
                for (int i = 0; i < n; i++)
                {
                    int x, z;
                    if (kind == 3) { x = Math.Min(c.mapW - 1, Math.Max(0, cx + r.Next(-b, b + 1))); z = Math.Min(c.mapH - 1, Math.Max(0, cz + r.Next(-b, b + 1))); }
                    else if (kind == 4) { x = r.Next(2) == 0 ? 0 : c.mapW - 1; z = r.Next(2) == 0 ? 0 : c.mapH - 1; }       // corners
                    else if (kind == 5) { x = r.Next(c.mapW); z = r.Next(2) == 0 ? 0 : c.mapH - 1; }                         // top / bottom edge
                    else { x = r.Next(c.mapW); z = r.Next(c.mapH); }
                    list.Add(new RM_KCell(x, z));
                }
                c.hits.Add(list);
                c.weights.Add(r.Next(10) == 0 ? ws[r.Next(ws.Length)] : (r.Next(3) == 0 ? ws[r.Next(5)] : 1f));
            }
            if (r.Next(10) == 0 && c.weights.Count > 0) c.weights.RemoveAt(c.weights.Count - 1);   // a weights list shorter than the targets: missing = 1
            return c;
        }

        private static int FloorDivD(int a, int b) { return (int)Math.Floor((double)a / b); }

        // Independent spec: block counts per (bx,bz) as tuples, tier from shares, 3x3 halo, window slid inward.
        private static List<RM_KBand> SpecBands(BandCase c)
        {
            var res = new List<RM_KBand>();
            int b = c.bandSetting < 7 ? 7 : c.bandSetting;
            for (int t = 0; t < c.hits.Count; t++)
            {
                var h = c.hits[t];
                if (h.Count == 0) continue;
                float w = t < c.weights.Count ? c.weights[t] : 1f;
                var sums = new Dictionary<(int, int), float>();
                foreach (var cell in h)
                {
                    var k = (FloorDivD(cell.x + c.ox, b), FloorDivD(cell.z + c.oz, b));
                    sums[k] = (sums.ContainsKey(k) ? sums[k] : 0f) + w;
                }
                float mx = sums.Values.Max();
                if (mx <= 0f) continue;
                var tier = new Dictionary<(int, int), RM_AcousticTier>();
                foreach (var kv in sums)
                {
                    float share = kv.Value / mx;
                    RM_AcousticTier tr = share >= 0.6f ? RM_AcousticTier.Strong : share >= 0.25f ? RM_AcousticTier.Moderate : RM_AcousticTier.Faint;
                    if (sums.Count == 1 && h.Count == 1) tr = RM_AcousticTier.Moderate;
                    tier[kv.Key] = tr;
                }
                foreach (var k in sums.Keys.ToList())
                    for (int dx = -1; dx <= 1; dx++)
                        for (int dz = -1; dz <= 1; dz++)
                            if (!tier.ContainsKey((k.Item1 + dx, k.Item2 + dz))) tier[(k.Item1 + dx, k.Item2 + dz)] = RM_AcousticTier.Faint;
                foreach (var kv in tier)
                {
                    int minX = kv.Key.Item1 * b - c.ox, minZ = kv.Key.Item2 * b - c.oz;
                    int maxX = minX + b - 1, maxZ = minZ + b - 1;
                    if (maxX < 0 || maxZ < 0 || minX > c.mapW - 1 || minZ > c.mapH - 1) continue;
                    int bw = Math.Min(b, c.mapW), bh = Math.Min(b, c.mapH);
                    int x0 = minX < 0 ? 0 : (minX + bw > c.mapW ? c.mapW - bw : minX);
                    int z0 = minZ < 0 ? 0 : (minZ + bh > c.mapH ? c.mapH - bh : minZ);
                    res.Add(new RM_KBand { targetIndex = t, tier = kv.Value, x = x0, z = z0, w = bw, h = bh });
                }
            }
            return res;
        }

        private static string Canon(IEnumerable<RM_KBand> bands)
        {
            return string.Join("|", bands.Select(Fmt).OrderBy(s => s, StringComparer.Ordinal));
        }

        private static string BandCheck(BandCase c)
        {
            Steps += c.hits.Sum(h => h.Count) + 1;
            int b = Math.Max(c.bandSetting, RM_AcousticKernel.MinBandSize);
            var got = RM_AcousticKernel.Build(c.mapW, c.mapH, c.hits, c.weights, c.bandSetting, c.ox, c.oz);
            var spec = SpecBands(c);
            if (Canon(got) != Canon(spec)) return "kernel differs from spec: kernel " + Canon(got).Substring(0, Math.Min(300, Canon(got).Length)) + " spec " + Canon(spec).Substring(0, Math.Min(300, Canon(spec).Length));
            int bw = Math.Min(b, c.mapW), bh = Math.Min(b, c.mapH);
            foreach (var band in got)
            {
                if (band.x < 0 || band.z < 0 || band.x + band.w > c.mapW || band.z + band.h > c.mapH) return "band outside the map: " + Fmt(band);
                if (band.w != bw || band.h != bh) return "band not at full block size (an edge band narrower than the block reads as an exact hit): " + Fmt(band) + " block " + b;
                if (band.w < Math.Min(RM_AcousticKernel.MinBandSize, c.mapW) || band.h < Math.Min(RM_AcousticKernel.MinBandSize, c.mapH)) return "band under the banding floor: " + Fmt(band);
                if (band.x == 0 && band.z == 0 || band.x + band.w == c.mapW && band.z + band.h == c.mapH) CornerSlides++;
                if (band.x == 0 || band.z == 0 || band.x + band.w == c.mapW || band.z + band.h == c.mapH) EdgeSlides++;
                if (band.tier == RM_AcousticTier.Strong) StrongBands++; else if (band.tier == RM_AcousticTier.Moderate) ModerateBands++; else FaintBands++;
            }
            for (int t = 0; t < c.hits.Count; t++)
            {
                float w = t < c.weights.Count ? c.weights[t] : 1f;
                if (c.hits[t].Count == 1) LoneHits++;
                bool any = got.Any(x => x.targetIndex == t);
                if (c.hits[t].Count == 0 && any) return $"target {t} heard nothing but has bands";
                if (w > 0f)
                    foreach (var cell in c.hits[t])
                        if (!got.Any(x => x.targetIndex == t && cell.x >= x.x && cell.x < x.x + x.w && cell.z >= x.z && cell.z < x.z + x.h))
                            return $"hit ({cell.x},{cell.z}) of target {t} is covered by no band of its own target";
                if (w <= 0f && any) return $"target {t} has non-positive weight {w} yet bands";
                if (c.hits[t].Count == 1 && w > 0f && c.mapW >= 3 * b && c.mapH >= 3 * b)
                {
                    var mine = got.Where(x => x.targetIndex == t).ToList();
                    var cell = c.hits[t][0];
                    if (mine.Count(x => x.tier == RM_AcousticTier.Strong) != 0) return "a lone hit read Strong";
                    if (mine.Count(x => x.tier == RM_AcousticTier.Moderate) != 1) return "a lone hit has " + mine.Count(x => x.tier == RM_AcousticTier.Moderate) + " Moderate bands, want exactly 1";
                    if (mine.Count > 9) return "a lone hit has more than 9 bands";
                }
                if (c.mapW > b && c.mapH > b)     // a map side equal to the block makes the two edge blocks slide onto the same whole-axis window
                {
                    var seen = new HashSet<string>();
                    foreach (var x in got.Where(x => x.targetIndex == t))
                        if (!seen.Add($"{x.x},{x.z}")) return $"target {t} has two bands on one window ({x.x},{x.z})";
                }
            }
            // reading does not depend on hit order
            var shuffled = new BandCase { mapW = c.mapW, mapH = c.mapH, bandSetting = c.bandSetting, ox = c.ox, oz = c.oz, weights = c.weights };
            var rr = new Random(c.GetHashCode() ^ 77);
            foreach (var h in c.hits) shuffled.hits.Add(h.OrderBy(_ => rr.Next()).ToList());
            if (Canon(RM_AcousticKernel.Build(shuffled.mapW, shuffled.mapH, shuffled.hits, shuffled.weights, shuffled.bandSetting, shuffled.ox, shuffled.oz)) != Canon(got)) return "reading depends on hit order";
            // scaling every weight by 2 (exact in binary) changes nothing
            var doubled = c.weights.Select(x => x * 2f).ToList();
            if (Canon(RM_AcousticKernel.Build(c.mapW, c.mapH, c.hits, doubled, c.bandSetting, c.ox, c.oz)) != Canon(got)) return "doubling every weight changed the reading";
            return null;
        }

        private static List<string> Band(int n, int seed)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int s = seed + i;
                var c = GenBand(new Random(s));
                Cases++;
                string err;
                try { err = BandCheck(c); } catch (Exception e) { err = "threw " + e.GetType().Name + ": " + e.Message; }
                if (err != null)
                {
                    var small = ShrinkBand(c);
                    string e2;
                    try { e2 = BandCheck(small); } catch (Exception e) { e2 = "threw " + e.GetType().Name + ": " + e.Message; }
                    fails.Add($"band seed {s}: {e2 ?? err} | {(e2 != null ? small : c)}");
                    if (fails.Count >= 3) break;
                }
            }
            return fails;
        }

        private static BandCase ShrinkBand(BandCase c)
        {
            Func<BandCase, bool> fails = x => { try { return BandCheck(x) != null; } catch { return true; } };
            BandCase cur = c;
            bool progress = true;
            while (progress)
            {
                progress = false;
                for (int t = 0; t < cur.hits.Count && !progress; t++)
                    for (int i = 0; i < cur.hits[t].Count && !progress; i++)
                    {
                        var trial = new BandCase { mapW = cur.mapW, mapH = cur.mapH, bandSetting = cur.bandSetting, ox = cur.ox, oz = cur.oz, weights = cur.weights };
                        for (int u = 0; u < cur.hits.Count; u++) trial.hits.Add(new List<RM_KCell>(cur.hits[u]));
                        trial.hits[t].RemoveAt(i);
                        if (fails(trial)) { cur = trial; progress = true; }
                    }
            }
            return cur;
        }

        // ════════════════════════ gate ════════════════════════
        private static RM_PulseGate SpecGate(bool enabled, bool spawned, bool hasPower, bool powerOn, bool needShip, bool onShip, int left)
        {
            var rules = new List<(bool blocked, RM_PulseGate why)>
            {
                (!enabled, RM_PulseGate.Disabled),
                (!spawned, RM_PulseGate.NotSpawned),
                (hasPower && !powerOn, RM_PulseGate.NoPower),
                (needShip && !onShip, RM_PulseGate.NotOnShip),
                (left > 0, RM_PulseGate.Cooldown),
            };
            foreach (var r in rules) if (r.blocked) return r.why;
            return RM_PulseGate.Ready;
        }

        private static List<string> Gate(int n, int seed)
        {
            var fails = new List<string>();
            int[] ticks = { -5000, -1, 0, 1, 2500, 300000 };
            int seen = 0;
            for (int m = 0; m < 64; m++)
                foreach (int tk in ticks)
                {
                    Cases++; Steps++;
                    bool[] f = Enumerable.Range(0, 6).Select(i => (m >> i & 1) == 1).ToArray();
                    var got = RM_AcousticKernel.Gate(f[0], f[1], f[2], f[3], f[4], f[5], tk);
                    var want = SpecGate(f[0], f[1], f[2], f[3], f[4], f[5], tk);
                    if (got != want) fails.Add($"gate seed {m}: flags {string.Join("", f.Select(x => x ? 1 : 0))} left {tk}: got {got} want {want}");
                    if (got == RM_PulseGate.Ready) { seen++; Check(f[0] && f[1] && (!f[2] || f[3]) && (!f[4] || f[5]) && tk <= 0, "Ready with a failed condition"); }
                }
            if (seen == 0) fails.Add("gate seed 0: no flag combination ever read Ready (blind)");
            return fails;
        }

        // ════════════════════════ clock ════════════════════════
        private static string ClockCase(int seed)
        {
            var r = new Random(seed);
            float hours = r.Next(8, 960) / 8f;                    // 1 .. 120 h in 1/8 h steps, like the slider after rounding
            if (r.Next(2) == 0) hours = (float)Math.Round(hours);
            int cd = RM_AcousticKernel.CooldownTicks(hours);
            Check(Math.Abs(cd - hours * RM_AcousticKernel.TicksPerHour) <= 0.5 + 1e-6, $"cooldown {hours} h -> {cd} ticks is not the rounded product");
            int last = -999999, now = r.Next(0, 5000000);
            int lastReal = int.MinValue;                          // spec ledger: tick of the last successful pulse
            for (int step = 0; step < 60; step++)
            {
                Steps++;
                now += r.Next(3) == 0 ? r.Next(0, cd * 3 / 2 + 1) : r.Next(0, 400);
                int left = RM_AcousticKernel.TicksUntilReady(last, cd, now);
                var g = RM_AcousticKernel.Gate(true, true, true, true, true, true, left);
                long since = lastReal == int.MinValue ? long.MaxValue : (long)now - lastReal;
                bool due = since >= cd;
                if (lastReal == int.MinValue) due = true;
                Check((g == RM_PulseGate.Ready) == due, $"at tick {now} (last pulse {(lastReal == int.MinValue ? "none" : lastReal.ToString())}, cooldown {cd}) gate {g} but due={due}");
                if (g == RM_PulseGate.Ready) { Allowed++; last = now; lastReal = now; } else Refused++;
            }
            // overlay lifetime
            int dur = RM_AcousticKernel.OverlayTicks(r.Next(1, 49));
            int start = r.Next(0, 3000000);
            int exp = RM_AcousticKernel.OverlayExpiry(start, r.Next(5) == 0 ? -r.Next(0, 3) : dur);
            Check(exp > start, "overlay expiry not after its start");
            Check(RM_AcousticKernel.OverlayActive(exp, start, 3), "overlay not active the tick it was set");
            Check(RM_AcousticKernel.OverlayActive(exp, exp - 1, 3), "overlay not active on its last tick");
            Check(!RM_AcousticKernel.OverlayActive(exp, exp, 3), "overlay still active on its expiry tick");
            Check(!RM_AcousticKernel.OverlayActive(exp, start, 0), "overlay active with no bands");
            Check(!RM_AcousticKernel.OverlayActive(-1, start, 3), "a cleared overlay (-1) is active");
            return null;
        }

        private static List<string> Clock(int n, int seed)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                Cases++;
                try { ClockCase(seed + i); } catch (Exception e) { fails.Add($"clock seed {seed + i}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            return fails;
        }

        // ════════════════════════ ship ════════════════════════
        private static List<string> Ship(int n, int seed)
        {
            var fails = new List<string>();
            for (int engines = -1; engines <= 2; engines++)
                for (int cells = 0; cells <= 9; cells++)
                    for (int mask = 0; mask < (1 << cells); mask++)
                    {
                        Cases++; Steps++;
                        var list = Enumerable.Range(0, cells).Select(i => (mask >> i & 1) == 1).ToList();
                        bool got = RM_AcousticKernel.OnLandedShip(engines, list);
                        bool want = engines > 0 && list.All(x => x);
                        if (got != want) { fails.Add($"ship seed {engines * 1000 + mask}: engines {engines} cells {string.Join("", list.Select(x => x ? 1 : 0))} got {got} want {want}"); return fails; }
                    }
            return fails;
        }

        // ════════════════════════ units ════════════════════════
        private static List<string> Units(int n, int seed)
        {
            var fails = new List<string>();
            Action<string, Action> t = (name, a) => { Cases++; Steps++; try { a(); } catch (Exception e) { fails.Add("units seed 0: " + name + ": " + e.Message); } };
            t("floor is 7", () => Check(RM_AcousticKernel.MinBandSize >= 7, "MinBandSize " + RM_AcousticKernel.MinBandSize + " < 7"));
            t("max above min", () => Check(RM_AcousticKernel.MaxBandSize > RM_AcousticKernel.MinBandSize, "MaxBandSize <= MinBandSize"));
            t("effective band never under the floor", () =>
            {
                var r = new Random(seed);
                foreach (int v in new[] { int.MinValue, -1, 0, 6, 7, 8, 25, 26, int.MaxValue }.Concat(Enumerable.Range(0, 200).Select(_ => r.Next(int.MinValue, int.MaxValue))))
                    Check(RM_AcousticKernel.EffectiveBand(v) >= RM_AcousticKernel.MinBandSize, "EffectiveBand(" + v + ") under the floor");
            });
            t("clamp is within min..max and idempotent", () =>
            {
                foreach (int v in new[] { int.MinValue, -3, 0, 7, 11, 25, 26, 100, int.MaxValue })
                {
                    int c = RM_AcousticKernel.ClampBandSetting(v);
                    Check(c >= RM_AcousticKernel.MinBandSize && c <= RM_AcousticKernel.MaxBandSize, "clamp(" + v + ") = " + c);
                    Check(RM_AcousticKernel.ClampBandSetting(c) == c, "clamp not idempotent at " + v);
                    if (v >= RM_AcousticKernel.MinBandSize && v <= RM_AcousticKernel.MaxBandSize) Check(c == v, "clamp moved an in-range value " + v);
                }
            });
            t("tier thresholds", () =>
            {
                Check(RM_AcousticKernel.TierFor(1f) == RM_AcousticTier.Strong, "share 1 not Strong");
                Check(RM_AcousticKernel.TierFor(0.6f) == RM_AcousticTier.Strong, "share 0.6 not Strong (>= inclusive)");
                Check(RM_AcousticKernel.TierFor(0.5999f) == RM_AcousticTier.Moderate, "share 0.5999 not Moderate");
                Check(RM_AcousticKernel.TierFor(0.25f) == RM_AcousticTier.Moderate, "share 0.25 not Moderate (>= inclusive)");
                Check(RM_AcousticKernel.TierFor(0.2499f) == RM_AcousticTier.Faint, "share 0.2499 not Faint");
                Check(RM_AcousticKernel.StrongShare > RM_AcousticKernel.ModerateShare, "Strong share not above Moderate share");
            });
            t("best tier", () =>
            {
                var bands = new List<RM_KBand> { new RM_KBand { targetIndex = 0, tier = RM_AcousticTier.Moderate }, new RM_KBand { targetIndex = 1, tier = RM_AcousticTier.Strong }, new RM_KBand { targetIndex = 0, tier = RM_AcousticTier.Faint } };
                Check(RM_AcousticKernel.BestTier(bands, 0) == RM_AcousticTier.Moderate, "best of target 0 is not Moderate");
                Check(RM_AcousticKernel.BestTier(bands, 1) == RM_AcousticTier.Strong, "best of target 1 is not Strong");
                Check(RM_AcousticKernel.BestTier(bands, 2) == RM_AcousticTier.Faint, "best of an unheard target is not Faint");
            });
            t("a cell left of the map floors into the block to its left", () =>
            {
                var hits = new List<List<RM_KCell>> { new List<RM_KCell> { new RM_KCell(-3, 5) } };
                var bands = RM_AcousticKernel.Build(30, 30, hits, new List<float> { 1f }, 7, 0, 0);
                Check(bands.Count > 0, "no halo reached the map from a hit just left of it");
                Check(bands.All(b => b.tier == RM_AcousticTier.Faint), "a hit at x=-3 read as a heard block inside the map (truncating division)");
            });
            t("ticks until ready", () =>
            {
                Check(RM_AcousticKernel.TicksUntilReady(-999999, 60000, 0) < 0, "a never-fired sounder is not ready at tick 0");
                Check(RM_AcousticKernel.TicksUntilReady(1000, 60000, 61000) == 0, "ready exactly at last+cooldown");
                Check(RM_AcousticKernel.TicksUntilReady(1000, 60000, 60999) == 1, "one tick early reads 1");
            });
            return fails;
        }

        // ════════════════════════ run ════════════════════════
        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("band", () => Band(N(6000), S(1))),
                ("gate", () => Gate(1, 1)),
                ("clock", () => Clock(N(3000), S(1))),
                ("ship", () => Ship(1, 1)),
                ("units", () => Units(1, S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                if (scale <= 0 && !oneSeed.HasValue && (f.name == "band" || f.name == "clock")) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            if ((only == null || only == "band") && !oneSeed.HasValue && scale >= 1)
            {
                Console.WriteLine($"band reached: strong {StrongBands}, moderate {ModerateBands}, faint {FaintBands}, edge-slid {EdgeSlides}, corner-slid {CornerSlides}, lone hits {LoneHits}, tiny maps {Tiny}");
                if (StrongBands == 0 || ModerateBands == 0 || FaintBands == 0 || EdgeSlides == 0 || CornerSlides == 0 || LoneHits == 0 || Tiny == 0) { Console.WriteLine("FAIL band fuzz never reached a tier / edge / corner / lone hit / tiny map (blind)"); ok = false; }
            }
            if ((only == null || only == "clock") && !oneSeed.HasValue && scale >= 1)
            {
                Console.WriteLine($"clock reached: pulses allowed {Allowed}, refused {Refused}");
                if (Allowed == 0 || Refused == 0) { Console.WriteLine("FAIL clock fuzz never both allowed and refused a pulse (blind)"); ok = false; }
            }
            Console.WriteLine($"acousticscanner fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
