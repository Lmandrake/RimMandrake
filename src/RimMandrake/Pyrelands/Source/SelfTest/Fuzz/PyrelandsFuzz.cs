// Approach B for Pyrelands: seeded fuzz over the Verse-free kernels the mods call (../../Kernel/*.cs, plus FurnaceWarmthMath.cs):
//   burn     the burn-line map component driven exactly as MapComponent_BurnLine / PyrelandsFireFront drive it (measure cadence and
//            centroid, the history ring, the arson-debt book, the standing-burn keep-alive clock, the fire-front clock), with the Tribes
//            incidents on top: FireRaid (gate, goodwill plan, points, debt collected) and FlameHarvest (minimum fires); front line
//            geometry; the rite gates. This is where the arson-debt and minimum-fire bars are proven
//   furnace  the thermal-charge step, the world herd's three-leg cycle, the nearest-tile search vs brute force, biome routing against
//            the real name lists, the bed-ignition rest clock, size ratio, hawk cooldown, the warmth maths
//   breaker  the lightning-breaker section flood-fill against a union-find spec on random power graphs, battery partition, blast
//   eco      biome placement score, ash-fall rate and attempts, the once-per-fire roll set, terrain-family predicates, gates, list parser
//   units    tuning-file relationships (read from PyrelandsTuning.cs itself) and exhaustive truth tables
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace RimMandrake.Pyrelands.Fuzz
{
    internal sealed class Tun
    {
        private readonly Dictionary<string, double> v = new Dictionary<string, double>();
        private readonly Dictionary<string, string[]> arrays = new Dictionary<string, string[]>();

        public static Tun Load(string path)
        {
            var t = new Tun();
            string text = Regex.Replace(File.ReadAllText(path), @"//[^\n]*", "");
            var pending = new List<KeyValuePair<string, string>>();
            foreach (Match m in Regex.Matches(text, @"public\s+const\s+(?:float|int)\s+(\w+)\s*=\s*([^;]+);"))
            {
                string expr = m.Groups[2].Value.Trim();
                string num = expr.TrimEnd('f', 'F');
                if (double.TryParse(num, NumberStyles.Float, CultureInfo.InvariantCulture, out double d)) t.v[m.Groups[1].Value] = d;
                else pending.Add(new KeyValuePair<string, string>(m.Groups[1].Value, expr));
            }
            foreach (var p in pending)
            {
                if (t.v.TryGetValue(p.Value, out double d)) t.v[p.Key] = d;
                else throw new Exception("PyrelandsTuning.cs: cannot evaluate " + p.Key + " = " + p.Value);
            }
            foreach (Match m in Regex.Matches(text, @"public\s+static\s+readonly\s+string\[\]\s+(\w+)\s*=\s*\{([^}]*)\}\s*;"))
                t.arrays[m.Groups[1].Value] = Regex.Matches(m.Groups[2].Value, "\"([^\"]+)\"").Cast<Match>().Select(x => x.Groups[1].Value).ToArray();
            return t;
        }

        public float F(string n) { if (!v.TryGetValue(n, out double d)) throw new Exception("PyrelandsTuning.cs has no constant " + n); return (float)d; }
        public int I(string n) { if (!v.TryGetValue(n, out double d)) throw new Exception("PyrelandsTuning.cs has no constant " + n); return (int)d; }
        public string[] A(string n) { if (!arrays.TryGetValue(n, out string[] a)) throw new Exception("PyrelandsTuning.cs has no string array " + n); return a; }
        public int Count => v.Count;
    }

    internal static class PyrelandsFuzz
    {
        public static long Cases, Steps;
        private static Tun T;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        internal static List<X> Shrink<X>(List<X> acts, Func<List<X>, bool> fails)
        {
            var cur = new List<X>(acts);
            for (int chunk = Math.Max(1, cur.Count / 2); chunk >= 1; chunk /= 2)
            {
                bool progress = true;
                while (progress)
                {
                    progress = false;
                    for (int i = 0; i + chunk <= cur.Count; i++)
                    {
                        var trial = new List<X>(cur);
                        trial.RemoveRange(i, chunk);
                        if (fails(trial)) { cur = trial; progress = true; break; }
                    }
                }
            }
            return cur;
        }

        internal struct Act
        {
            public int kind, a, b, c;
            public string[] names;
            public override string ToString() { return names[kind] + "(" + a + "," + b + "," + c + ")"; }
        }

        private static List<string> RunFamily(string name, int n, int baseSeed, Func<int, List<Act>> gen, Func<int, List<Act>, string> run)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k;
                var acts = gen(seed);
                Cases++;
                string err = run(seed, acts);
                if (err == null) continue;
                var min = Shrink(acts, t => run(seed, t) != null);
                fails.Add($"{name} seed {seed}: {run(seed, min)} | {string.Join(" ", min)}");
            }
            return fails;
        }

        private static List<string> RunSeeded(string name, int n, int baseSeed, Action<Random> body)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k;
                Cases++;
                try { body(new Random(seed * 7919 + 13)); }
                catch (Exception e) { fails.Add($"{name} seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        // ════════════════════════ burn ════════════════════════
        private static readonly string[] BurnNames = { "Ticks", "AddFire", "Extinguish", "Attach", "ClearFires", "ToggleBurnLine", "ToggleClock", "ToggleMaster", "SetThreshold", "TryRaid", "TryHarvest", "SetTribes", "ReseedAlways" };
        public static long Measures, DebtRises, DebtDecays, ReseedAttempts, ReseedSuccess, FrontsFired, FrontsArmed, RaidsFired, RaidInsults, RaidRefused, RaidGated, HarvestsAllowed, HarvestsRefused, HistorySamples, LivenessChecks;
        public static int HistoryMaxLen;

        private sealed class FireM { public int x, z; public bool attached; public int inst; }

        private sealed class BurnSim
        {
            public Tun T; public Random rng; public int now, mapId;
            public List<FireM> fires = new List<FireM>();
            public bool burnLine = true, clockOn = true, master = true, reseedAlways;
            public float debt; public int ticksSince, lastReseed = -99999, fireCount, cx, cz; public bool centerValid;
            public List<int> hTicks = new List<int>(), hCells = new List<int>();
            public int nextFront = -1;
            // incident model
            public bool present = true, permanentEnemy, arsonOn = true, harvestOn = true; public int goodwill; public float threshold = 400f;
            // spec
            public double specDebt; public int specQuiet; public int specLastReseed = -99999;
            public int armedAt = -1, armDelay, lastFireSeenTick = 0, playerChecks;
            public bool wasDisabled = true; public int quietAtEnable;
            public string err;
            public int tickInterval;

            public void Fail(string m) { if (err == null) err = m; }
            public bool Hostile { get { return permanentEnemy || goodwill <= -75; } }
            public bool HasGoodwill { get { return !permanentEnemy; } }

            public void Step()
            {
                now++;
                Steps++;
                if (!RM_BurnKernel.MeasureDue(now, mapId, tickInterval)) return;
                if ((now + mapId) % tickInterval != 0) Fail("MeasureDue true off the cadence");
                if (!master) { Front(); return; } // the mod still tells the clock it is off
                if (burnLine) { Measure(); Accrue(); Keep(); }
                Front();
            }

            private void Measure()
            {
                int c = 0, sx = 0, sz = 0;
                foreach (FireM f in fires) if (!f.attached) { c++; sx += f.x; sz += f.z; }
                fireCount = c;
                centerValid = RM_BurnKernel.Centroid(sx, sz, c, out cx, out cz);
                Measures++;
                Check(centerValid == (c > 0), "centroid validity != any free fire");
                if (c > 0)
                {
                    Check(cx == sx / c && cz == sz / c, "centroid != integer mean");
                    int minX = fires.Where(f => !f.attached).Min(f => f.x), maxX = fires.Where(f => !f.attached).Max(f => f.x);
                    int minZ = fires.Where(f => !f.attached).Min(f => f.z), maxZ = fires.Where(f => !f.attached).Max(f => f.z);
                    Check(cx >= minX && cx <= maxX && cz >= minZ && cz <= maxZ, "centroid outside the fires' bounding box");
                    lastFireSeenTick = now;
                }
                Check(RM_BurnKernel.AnyBurn(fireCount, centerValid) == (c > 0), "AnyBurn");
                if (centerValid)
                {
                    int before = hTicks.Count;
                    bool added = RM_BurnKernel.RecordHistory(hTicks, hCells, now, cx * 10000 + cz, 2500, 600000);
                    if (added) HistorySamples++;
                    HistoryMaxLen = Math.Max(HistoryMaxLen, hTicks.Count);
                    Check(hTicks.Count == hCells.Count, "history ticks and cells out of step");
                    for (int i = 1; i < hTicks.Count; i++) Check(hTicks[i] - hTicks[i - 1] >= 2500, "history samples closer than the interval");
                    // pruned when a sample is ADDED (relative to that tick); between samples the oldest may be one interval past it
                    Check(hTicks.Count == 0 || now - hTicks[0] <= 600000 + (added ? 0 : 2500), "history keeps a sample past the horizon");
                    Check(hTicks.Count <= 600000 / 2500 + 1, "history ring longer than its horizon allows");
                    Check(!added || hTicks[hTicks.Count - 1] == now, "an added sample is not the newest");
                }
            }

            private void Accrue()
            {
                int player = 0;
                foreach (FireM f in fires) if (!f.attached && RM_BurnKernel.PlayerAttributed(f.inst != 0, f.inst != 3, f.inst == 1)) player++;
                int specPlayer = fires.Count(f => !f.attached && f.inst == 1);
                Check(player == specPlayer, $"player-attributed fires {player}, spec {specPlayer}");
                float cap = T.F("ArsonDebtCap"), per = T.F("ArsonDebtPerPlayerFirePerCheck"), dec = T.F("ArsonDebtDecayPerCheck");
                float was = debt;
                debt = RM_BurnKernel.ArsonStep(debt, player, per, cap, dec);
                if (player > 0) { specDebt = Math.Min(cap, specDebt + player * (double)per); DebtRises++; playerChecks++; }
                else { if (specDebt > 0) { specDebt = Math.Max(0.0, specDebt - dec); if (specDebt < was) DebtDecays++; } playerChecks = 0; }
                Check(Math.Abs(debt - specDebt) < 1e-3, $"arson debt {debt}, spec {specDebt}");
                Check(debt >= 0f && debt <= cap, "arson debt outside [0, cap]");
                if (player == 0) Check(debt <= was, "debt rose with no player-attributed fire");
            }

            private void Keep()
            {
                int quiet = T.I("StandingBurnQuietTicks"), retry = T.I("StandingBurnRetryTicks");
                var d = RM_BurnKernel.KeepAlive(fireCount, ref ticksSince, tickInterval, quiet, now, lastReseed, retry);
                RM_ReseedDecision spec;
                if (fireCount > 0) { specQuiet = 0; quietAtEnable = 0; spec = RM_ReseedDecision.FiresPresent; }
                else
                {
                    specQuiet += tickInterval;
                    spec = specQuiet < quiet ? RM_ReseedDecision.Quiet : now - specLastReseed < retry ? RM_ReseedDecision.Retry : RM_ReseedDecision.Reseed;
                }
                Check(d == spec, $"keep-alive {d}, spec {spec} (quiet {specQuiet}, since last attempt {now - specLastReseed})");
                Check(ticksSince == specQuiet, "quiet clock drifted");
                if (d == RM_ReseedDecision.Reseed)
                {
                    Check(fireCount == 0, "reseeded with fires present");
                    Check(now - specLastReseed >= retry, "two reseed attempts inside the retry window");
                    lastReseed = now; specLastReseed = now; ReseedAttempts++;
                    if (reseedAlways || rng.Next(100) < 40)
                    {
                        ticksSince = 0; specQuiet = 0; ReseedSuccess++;
                        fires.Add(new FireM { x = rng.Next(250), z = rng.Next(250), inst = 0 });
                    }
                }
                // measured (burn line on) quiet time only: while the burn line is switched off nothing is watching
                if (reseedAlways && fireCount == 0 && specQuiet > Math.Max(quiet, quietAtEnable) + retry + 2 * tickInterval)
                    Fail($"the standing burn stayed out for {specQuiet} measured ticks although every reseed succeeds");
            }

            private void Front()
            {
                float min = T.F("FireFrontMinDays"), max = T.F("FireFrontMaxDays");
                bool enabled = master && clockOn;
                int sched = -1;
                int prevNext = nextFront;
                var act = RM_BurnKernel.FrontTick(ref nextFront, now, enabled, () => { sched = RM_BurnKernel.ScheduleTicks(min, max, (float)rng.NextDouble(), 60000); return sched; });
                if (!enabled)
                {
                    Check(act == RM_FrontAction.Disabled && nextFront == -1, "a disabled clock is not re-armed to -1");
                    wasDisabled = true;
                    return;
                }
                if (wasDisabled) { Check(act == RM_FrontAction.Armed, "re-enabling the clock did not just arm it (" + act + ")"); wasDisabled = false; }
                if (act == RM_FrontAction.Armed || act == RM_FrontAction.Fire)
                {
                    Check(sched >= (int)Math.Round(min * 60000) && sched <= (int)Math.Round(max * 60000), $"front scheduled {sched} ticks out, outside {min}..{max} days");
                    Check(nextFront == now + sched, "next front tick != now + schedule");
                    if (act == RM_FrontAction.Fire)
                    {
                        FrontsFired++;
                        Check(prevNext >= 0 && now >= prevNext, "front fired before it was due");
                        Check(now - prevNext < tickInterval, $"front fired {now - prevNext} ticks late (cadence {tickInterval})");
                        Check(armedAt >= 0 && now - armedAt >= armDelay, "front fired inside its delay");
                    }
                    else FrontsArmed++;
                    armedAt = now; armDelay = sched;
                }
                else
                {
                    Check(act == RM_FrontAction.Wait && now < nextFront, "Wait without a future front");
                    Check(sched == -1, "the schedule was rolled while waiting");
                }
            }

            public void TryRaid()
            {
                float cap = T.F("ArsonDebtCap");
                bool can = RM_BurnKernel.RaidCanFire(arsonOn, true, true, debt, threshold, cap, present, Hostile, HasGoodwill);
                bool spec = arsonOn && debt >= Math.Min(threshold, cap) && present && (Hostile || HasGoodwill);
                Check(can == spec, $"RaidCanFire {can}, spec {spec} (debt {debt}, threshold {threshold}, cap {cap}, hostile {Hostile}, goodwill-capable {HasGoodwill})");
                // liveness: persistent player fire for long enough puts the debt at the cap, and then the raid MUST be on offer
                float per = T.F("ArsonDebtPerPlayerFirePerCheck");
                if (arsonOn && present && (Hostile || HasGoodwill) && playerChecks * per >= cap + per && fires.Any(f => !f.attached && f.inst == 1) && master && burnLine)
                {
                    LivenessChecks++;
                    Check(can, $"persistent arson (debt {debt} of cap {cap}) cannot trigger a raid at threshold {threshold}");
                }
                if (!can) { RaidGated++; return; }
                var plan = RM_BurnKernel.RaidPlan(present, Hostile, HasGoodwill);
                var specPlan = !present ? RM_RaidPlan.Refuse : Hostile ? RM_RaidPlan.RaidNow : HasGoodwill ? RM_RaidPlan.InsultFirst : RM_RaidPlan.Refuse;
                Check(plan == specPlan, $"RaidPlan {plan}, spec {specPlan}");
                if (plan == RM_RaidPlan.Refuse) { RaidRefused++; return; }
                if (plan == RM_RaidPlan.InsultFirst)
                {
                    Check(!Hostile && HasGoodwill, "insulted a faction that is already hostile or has no goodwill");
                    goodwill += T.I("FireRaidGoodwillHit"); RaidInsults++;
                    if (!RM_BurnKernel.RaidAfterInsult(Hostile)) { Check(!Hostile, "RaidAfterInsult said no to a hostile faction"); return; }
                }
                Check(Hostile, "a raid with a faction that is not hostile");
                float def = 100f + rng.Next(2000);
                float pts = rng.Next(3) == 0 ? 0f : rng.Next(2000);
                float used = RM_BurnKernel.RaidPoints(pts, pts <= 0f ? def : 0f, T.F("FireRaidPointsFactor"), T.F("FireRaidPointsMin"));
                float want = Math.Max(T.F("FireRaidPointsMin"), (pts <= 0f ? def : pts) * T.F("FireRaidPointsFactor"));
                Check(used == want && used >= T.F("FireRaidPointsMin"), $"raid points {used}, spec {want}");
                Check(debt >= Math.Min(threshold, cap), "a raid with the debt below the threshold");
                debt = 0f; specDebt = 0; playerChecks = 0; RaidsFired++;
                Check(!RM_BurnKernel.RaidCanFire(arsonOn, true, true, debt, threshold, cap, present, Hostile, HasGoodwill), "the debt was collected but the raid is still on offer");
            }

            public void TryHarvest(int minFires)
            {
                bool any = fireCount > 0 && centerValid;
                bool can = RM_BurnKernel.HarvestCanFire(harvestOn, true, true, any, fireCount, minFires, present, Hostile);
                bool spec = harvestOn && any && fireCount >= minFires && present && !Hostile;
                Check(can == spec, $"HarvestCanFire {can}, spec {spec} (fires {fireCount}, min {minFires}, hostile {Hostile})");
                if (can) HarvestsAllowed++; else HarvestsRefused++;
                // the boundary: exactly minFires standing fires allow it, one fewer does not
                Check(RM_BurnKernel.HarvestCanFire(true, true, true, true, minFires, minFires, true, false) && !RM_BurnKernel.HarvestCanFire(true, true, true, true, minFires - 1, minFires, true, false), "harvest minimum-fires boundary");
            }
        }

        private static List<Act> GenBurn(int seed)
        {
            var r = new Random(seed * 101 + 3);
            var acts = new List<Act>();
            int n = 12 + r.Next(60);
            for (int i = 0; i < n; i++)
            {
                int k = r.Next(100);
                int kind = k < 33 ? 0 : k < 45 ? 1 : k < 48 ? 2 : k < 50 ? 3 : k < 52 ? 4 : k < 55 ? 5 : k < 58 ? 6 : k < 60 ? 7 : k < 68 ? 8 : k < 84 ? 9 : k < 92 ? 10 : k < 97 ? 11 : 12;
                int ticks = r.Next(6) == 0 ? 1 + r.Next(600000) : 1 + r.Next(6000);
                acts.Add(new Act { kind = kind, a = kind == 0 ? ticks : r.Next(100000), b = r.Next(250), c = kind == 1 && r.Next(2) == 0 ? 1 : r.Next(4), names = BurnNames });
            }
            if (r.Next(3) != 0)
            {
                // a persistent arsonist: a player fire, a long wait, then the incidents
                acts.Insert(0, new Act { kind = 1, a = 10, b = 10, c = 1, names = BurnNames });
                acts.Insert(1, new Act { kind = 0, a = 100000 + r.Next(300000), names = BurnNames });
                acts.Insert(2, new Act { kind = 9, names = BurnNames });
                acts.Insert(3, new Act { kind = 10, a = r.Next(50), names = BurnNames });
            }
            return acts;
        }

        private static string RunBurn(int seed, List<Act> acts)
        {
            var s = new BurnSim { T = T, rng = new Random(seed ^ 0xB0A7), mapId = seed % 7, tickInterval = T.I("BurnWatchIntervalTicks") };
            try
            {
                foreach (Act a in acts)
                {
                    switch (a.kind)
                    {
                        case 0: for (int k = 0; k < a.a && s.err == null; k++) s.Step(); break;
                        case 1: s.fires.Add(new FireM { x = a.a % 250, z = a.b % 250, inst = a.c }); break;
                        case 2: if (s.fires.Count > 0) s.fires.RemoveAt(a.a % s.fires.Count); break;
                        case 3: if (s.fires.Count > 0) s.fires[a.a % s.fires.Count].attached = true; break;
                        case 4: s.fires.Clear(); break;
                        case 5: s.burnLine = a.a % 2 == 0; break;
                        case 6: s.clockOn = a.a % 2 == 0; break;
                        case 7: s.master = a.a % 3 != 0; break;
                        case 8: s.threshold = 100f + a.a % 1901; break;
                        case 9: s.TryRaid(); break;
                        case 10: s.TryHarvest(1 + a.a % 50); break;
                        case 11: s.permanentEnemy = a.a % 5 == 0; s.present = a.a % 7 != 0; s.goodwill = -a.b % 160 + 40; break;
                        case 12: s.reseedAlways = a.a % 2 == 0; if (s.reseedAlways) s.quietAtEnable = s.specQuiet; break;
                    }
                    if (s.err != null) return s.err + " @tick " + s.now;
                }
                return null;
            }
            catch (Exception e) { return e.Message + " @tick " + s.now; }
        }

        private static List<string> Burn(int n, int seed)
        {
            var fails = RunFamily("burn", n, seed, GenBurn, RunBurn);
            fails.AddRange(RunSeeded("burn-pure", Math.Max(1, n), seed + 31, r =>
            {
                // front line geometry: exactly `width` DISTINCT cells, 8-adjacent in a row, through the origin, symmetric
                int width = 1 + r.Next(31);
                float angle = (float)(r.NextDouble() * 360.0);
                RM_BurnKernel.FrontLine(angle, width, out int[] dx, out int[] dz);
                Check(dx.Length == width && dz.Length == width, $"front line of width {width} has {dx.Length} cells");
                var seen = new HashSet<long>();
                for (int i = 0; i < width; i++) seen.Add(dx[i] * 100000L + dz[i]);
                Check(seen.Count == width, $"front line of width {width} at {angle:F1} degrees has only {seen.Count} distinct cells");
                int half = width / 2;
                Check(dx[half] == 0 && dz[half] == 0, "the front line does not pass through the origin");
                for (int i = 1; i < width; i++) Check(Math.Max(Math.Abs(dx[i] - dx[i - 1]), Math.Abs(dz[i] - dz[i - 1])) == 1, "front line cells are not 8-adjacent in a row");
                for (int i = 1; i <= half && half + i < width && half - i >= 0; i++) Check(dx[half + i] == -dx[half - i] && dz[half + i] == -dz[half - i], "front line is not symmetric about the origin");
                // the OLD construction (a unit Euclidean step truncated to cells), kept as a spec of the defect it had
                double rad = angle * Math.PI / 180.0; int lost = 0;
                var old = new HashSet<long>();
                for (int i = -half; i < width - half; i++) old.Add((int)(Math.Sin(rad) * i) * 100000L + (int)(Math.Cos(rad) * i));
                lost = width - old.Count; LegacyCellsLost += lost; LegacyWidths += width;
                // history lookups vs brute force
                var ticks = new List<int>(); var cells = new List<int>(); int t = 0;
                for (int k = 0; k < r.Next(0, 40); k++) { t += 2500 + r.Next(3000); RM_BurnKernel.RecordHistory(ticks, cells, t, k, 2500, 600000); }
                int now = t + r.Next(5000), ago = r.Next(0, 700000);
                int idx = RM_BurnKernel.HistoryIndexAgo(ticks, now, ago);
                int spec = -1;
                for (int i = 0; i < ticks.Count; i++) if (ticks[i] <= now - ago) spec = i;
                if (spec < 0 && ticks.Count > 0) spec = 0;
                Check(idx == spec, $"history lookup {idx}, spec {spec}");
                // rite
                Check(RM_BurnKernel.RiteRoll(true, 0.32f, 0.33f) && !RM_BurnKernel.RiteRoll(true, 0.33f, 0.33f) && !RM_BurnKernel.RiteRoll(false, 0f, 1f), "RiteRoll boundary");
                int mn = r.Next(1, 13), mx = r.Next(1, 13);
                RM_BurnKernel.RitePartyRange(mn, mx, out int lo, out int hi);
                Check(lo == mn && hi >= lo && (mx >= mn ? hi == mx : hi == mn), "rite party range");
                Check(RM_BurnKernel.RiteHarvestTicks(0f, 2500f) == 1 && RM_BurnKernel.RiteHarvestTicks(8f, 2500f) == 20000, "rite harvest ticks");
                Check(RM_BurnKernel.RiteRetryAtOrigin(0, false) && !RM_BurnKernel.RiteRetryAtOrigin(0, true) && !RM_BurnKernel.RiteRetryAtOrigin(3, false), "rite retry at the origin");
                // lawful cell: truth table
                for (int m = 0; m < 64; m++)
                {
                    bool inb = (m & 1) != 0, fog = (m & 2) != 0, roof = (m & 4) != 0, home = (m & 8) != 0, far = (m & 16) != 0, can = (m & 32) != 0;
                    bool want = inb && !fog && !roof && can && !home && far;
                    Check(RM_BurnKernel.LawfulBurnCell(inb, fog, roof, can ? 0.5f : 0f, home, far) == want, "LawfulBurnCell table " + m);
                }
                Check(RM_BurnKernel.TooCloseToColony(31, 32f) && !RM_BurnKernel.TooCloseToColony(32 * 32, 32f) && RM_BurnKernel.TooCloseToColony(32 * 32 - 1, 32f), "TooCloseToColony boundary");
                Steps += width + 8;
            }));
            // arson liveness over the whole slider range: persistent player fire reaches the threshold for EVERY value the UI offers
            try
            {
                Cases++;
                float cap = T.F("ArsonDebtCap"), per = T.F("ArsonDebtPerPlayerFirePerCheck"), dec = T.F("ArsonDebtDecayPerCheck");
                for (float thr = 100f; thr <= 2000f; thr += 25f)
                {
                    float d = 0f; int checks = 0;
                    while (!RM_BurnKernel.RaidCanFire(true, true, true, d, thr, cap, true, true, true) && checks < 100000) { d = RM_BurnKernel.ArsonStep(d, 1, per, cap, dec); checks++; }
                    Check(RM_BurnKernel.RaidCanFire(true, true, true, d, thr, cap, true, true, true), $"one player fire never reaches a raid threshold of {thr} (debt cap {cap})");
                    Check(checks <= cap / per + 2, $"threshold {thr} took {checks} checks");
                    Steps += checks;
                }
                // a fire that is lit and put out at once decays faster than it accrues only if decay >= per; report the relation as a metric
                ArsonNetPerFire = per - dec;
            }
            catch (Exception e) { fails.Add("burn-liveness: " + e.Message); }
            return fails;
        }

        public static long LegacyCellsLost, LegacyWidths;
        public static double ArsonNetPerFire;

        // ════════════════════════ furnace ════════════════════════
        public static long ChargeUps, ChargeDowns, ChargeHolds, HerdAdvances, HerdLegsSeen, BfsFound, BfsMissed, RestsRolled, RestsShort, BedZeroCells;
        public static double ChargeDaysAt40, ChargeDaysAt60;

        private static float StepOf(float ambient, bool nearFire)
        {
            return RM_FurnaceKernel.ChargeStep(ambient, nearFire, T.F("FurnaceChargeAmbientC"), T.F("FurnaceChargeAmbientSpanC"), T.F("FurnaceChargePerCheckAtFullHeat"),
                T.F("FurnaceBleedAmbientC"), T.F("FurnaceBleedAmbientSpanC"), T.F("FurnaceBleedPerCheckAtFullCold"), T.F("FurnaceChargePerCheckNearFire"));
        }

        private static List<string> Furnace(int n, int seed)
        {
            var fails = new List<string>();
            fails.AddRange(RunSeeded("furnace-charge", n, seed, r =>
            {
                double cA = T.F("FurnaceChargeAmbientC"), cS = T.F("FurnaceChargeAmbientSpanC"), cP = T.F("FurnaceChargePerCheckAtFullHeat");
                double bA = T.F("FurnaceBleedAmbientC"), bS = T.F("FurnaceBleedAmbientSpanC"), bP = T.F("FurnaceBleedPerCheckAtFullCold"), nf = T.F("FurnaceChargePerCheckNearFire");
                float seekBelow = T.F("FurnaceChargeSeekBelow"), avoid = T.F("FurnaceChargeAvoidAbove");
                float charge = (float)r.NextDouble();
                for (int i = 0; i < 400; i++)
                {
                    float amb = (float)(r.NextDouble() * 200.0 - 80.0);
                    bool fire = r.Next(5) == 0;
                    float step = StepOf(amb, fire);
                    double spec = amb >= cA ? cP * Math.Min(amb - cA, cS) / cS : amb <= bA ? -bP * Math.Min(bA - amb, bS) / bS : 0.0;
                    if (fire) spec += nf;
                    Check(Math.Abs(step - spec) < 1e-6, $"charge step {step}, spec {spec} at {amb:F1} C (fire {fire})");
                    Check(step >= -bP - 1e-9 && step <= cP + nf + 1e-9, "charge step outside its bounds");
                    if (!fire) { if (step > 0) ChargeUps++; else if (step < 0) ChargeDowns++; else ChargeHolds++; }
                    // monotone in ambient
                    float a2 = amb + (float)r.NextDouble() * 30f;
                    Check(StepOf(a2, fire) >= step - 1e-9f, "a warmer ambient charged less");
                    Check(fire || Math.Abs(StepOf(amb, true) - (step + nf)) < 1e-6, "near-fire is not a fixed additive step");
                    charge = RM_FurnaceKernel.ClampCharge(charge + step);
                    Check(charge >= 0f && charge <= 1f, "charge left [0,1]");
                    Check(RM_FurnaceKernel.WantsHeat(charge, seekBelow) == (charge < seekBelow) && RM_FurnaceKernel.IsFullyCharged(charge, avoid) == (charge >= avoid), "hysteresis flags");
                    Check(!(RM_FurnaceKernel.WantsHeat(charge, seekBelow) && RM_FurnaceKernel.IsFullyCharged(charge, avoid)), "a beast both wants heat and is full");
                    Steps++;
                }
                Check(StepOf((float)(bA + cA) / 2f, false) == 0f, "the dead band moved the charge");
                // time to fill from empty, at 40 and 60 C (days), as a metric
                ChargeDaysAt40 = TimeToFull(40f, avoid); ChargeDaysAt60 = TimeToFull(60f, avoid);
            }));
            fails.AddRange(RunSeeded("furnace-herd", n, seed + 5000, r =>
            {
                string[] pyr = T.A("PyrelandsBiomeDefNames"), term = T.A("NearTerminatorBiomeDefNames"), desert = T.A("DeepDesertBiomeDefNames");
                int delta = T.I("WorldHerdUpdateIntervalTicks");
                int deepDwell = T.I("WorldHerdDeepDesertDwellTicks"), maxDwell = T.I("WorldHerdMaxLegDwellTicks");
                float seekBelow = T.F("FurnaceChargeSeekBelow"), avoid = T.F("FurnaceChargeAvoidAbove");
                // ambient per leg: a hot desert, a warm grassland, a cold terminator; some seeds put the herd in the dead band
                float[] amb = { r.Next(4) == 0 ? 20f : 30f + r.Next(40), r.Next(4) == 0 ? 20f : 36f + r.Next(30), r.Next(4) == 0 ? 20f : -r.Next(40) };
                int members = 1 + r.Next(6);
                float[] ch = new float[members];
                for (int m = 0; m < members; m++) ch[m] = (float)r.NextDouble() * 0.5f;
                FurnaceHerdLeg leg = FurnaceHerdLeg.DeepDesert;
                int ticksAtLeg = 0, lastAdvanceAt = 0, t = 0, advances = 0;
                var order = new List<FurnaceHerdLeg>();
                int budget = 6 * maxDwell + 6 * deepDwell;
                while (advances < 6 && t < budget)
                {
                    t += delta; ticksAtLeg += delta; Steps++;
                    for (int m = 0; m < members; m++) ch[m] = RM_FurnaceKernel.ClampCharge(ch[m] + StepOf(amb[(int)leg], false));
                    float avg = ch.Average();
                    bool adv = RM_FurnaceKernel.ShouldAdvance(leg, ticksAtLeg, avg, deepDwell, maxDwell, seekBelow, avoid);
                    bool spec = leg == FurnaceHerdLeg.DeepDesert ? ticksAtLeg >= deepDwell : leg == FurnaceHerdLeg.Pyrelands ? avg >= avoid || ticksAtLeg >= maxDwell : avg <= seekBelow || ticksAtLeg >= maxDwell;
                    Check(adv == spec, $"ShouldAdvance {adv}, spec {spec} ({leg}, {ticksAtLeg} ticks, avg {avg:F3})");
                    Check(ticksAtLeg <= Math.Max(deepDwell, maxDwell) + delta, $"herd stayed {ticksAtLeg} ticks on the {leg} leg, past every dwell bound");
                    if (adv)
                    {
                        var next = RM_FurnaceKernel.NextLeg(leg);
                        Check(next != leg, "NextLeg did not move");
                        order.Add(leg); leg = next; ticksAtLeg = 0; lastAdvanceAt = t; advances++; HerdAdvances++;
                    }
                }
                Check(advances == 6, $"the herd advanced only {advances} legs in {budget} ticks");
                for (int i = 0; i < order.Count; i++) Check(order[i] == (FurnaceHerdLeg)(i % 3), "legs are not DeepDesert -> Pyrelands -> Terminator -> DeepDesert");
                HerdLegsSeen += order.Count;
                // biome routing against the real name lists
                foreach (string nme in pyr) Check(RM_FurnaceKernel.LegForBiome(nme, pyr, term) == FurnaceHerdLeg.Pyrelands, "pyrelands name routed elsewhere: " + nme);
                foreach (string nme in term) if (!pyr.Contains(nme)) Check(RM_FurnaceKernel.LegForBiome(nme, pyr, term) == FurnaceHerdLeg.Terminator, "terminator name routed elsewhere: " + nme);
                foreach (string nme in desert) if (!pyr.Contains(nme) && !term.Contains(nme)) Check(RM_FurnaceKernel.LegForBiome(nme, pyr, term) == FurnaceHerdLeg.DeepDesert, "desert name routed elsewhere: " + nme);
                Check(RM_FurnaceKernel.LegForBiome(null, pyr, term) == FurnaceHerdLeg.DeepDesert && RM_FurnaceKernel.LegForBiome("NotABiome", pyr, term) == FurnaceHerdLeg.DeepDesert && !RM_FurnaceKernel.MatchesAny("rm_pyrelands", pyr), "LegForBiome fallbacks / case sensitivity");
            }));
            fails.AddRange(RunSeeded("furnace-bfs", n, seed + 9000, r =>
            {
                int nodes = 1 + r.Next(60);
                var adj = new List<int>[nodes];
                for (int i = 0; i < nodes; i++) adj[i] = new List<int>();
                int edges = r.Next(nodes * 3);
                for (int e = 0; e < edges; e++) { int a = r.Next(nodes), b = r.Next(nodes); if (a == b) continue; adj[a].Add(b); adj[b].Add(a); }
                var match = new bool[nodes];
                int matches = r.Next(4);
                for (int k = 0; k < matches; k++) match[r.Next(nodes)] = true;
                int start = r.Next(nodes), cap = 1 + r.Next(nodes + 5);
                bool got = RM_FurnaceKernel.NearestMatching(start, x => x, (c, into) => { foreach (int q in adj[c]) into.Add(q); }, x => match[x], cap, out int found);
                // spec: hop distance by BFS layers (independent), then the cap counts DEQUEUES so the answer must be among the first `cap` nodes in BFS order
                var dist = Enumerable.Repeat(-1, nodes).ToArray(); var order = new List<int>(); var q2 = new Queue<int>();
                dist[start] = 0; q2.Enqueue(start);
                while (q2.Count > 0) { int c = q2.Dequeue(); order.Add(c); foreach (int nb in adj[c]) if (dist[nb] < 0) { dist[nb] = dist[c] + 1; q2.Enqueue(nb); } }
                int specIdx = -1;
                for (int i = 0; i < Math.Min(cap, order.Count); i++) if (match[order[i]]) { specIdx = i; break; }
                Check(got == (specIdx >= 0), $"nearest search found={got}, spec {specIdx >= 0} (cap {cap})");
                if (got)
                {
                    Check(match[found], "returned a tile that does not match");
                    Check(found == order[specIdx], $"returned {found}, the nearest in BFS order is {order[specIdx]}");
                    Check(order.Where(x => match[x]).Min(x => dist[x]) == dist[found] || cap < order.Count, "a nearer matching tile exists");
                    BfsFound++;
                }
                else BfsMissed++;
                Steps += nodes;
            }));
            fails.AddRange(RunSeeded("furnace-bed", n, seed + 14000, r =>
            {
                int minRest = T.I("FurnaceMinRestTicks");
                int resting = 0, specRest = 0, runLeft = 0; bool awakeState = true;
                for (int i = 0; i < 300; i++)
                {
                    if (runLeft <= 0) { awakeState = !awakeState; runLeft = awakeState ? 1 + r.Next(5) : 5 + r.Next(60); }
                    runLeft--;
                    bool awake = awakeState; int delta = 30 + r.Next(300);
                    var o = RM_FurnaceKernel.RestStep(ref resting, awake, delta, minRest);
                    RM_RestOutcome spec;
                    if (!awake) { specRest += delta; spec = RM_RestOutcome.Resting; }
                    else if (specRest <= 0) spec = RM_RestOutcome.NothingToReport;
                    else { spec = specRest < minRest ? RM_RestOutcome.WokeTooShort : RM_RestOutcome.WokeRested; specRest = 0; }
                    Check(o == spec, $"RestStep {o}, spec {spec}");
                    Check(resting == specRest, "rest clock drifted");
                    if (o == RM_RestOutcome.WokeRested) RestsRolled++; else if (o == RM_RestOutcome.WokeTooShort) RestsShort++;
                    Check(awake ? resting == 0 : resting > 0, "the rest clock survived a waking");
                    Steps++;
                }
                float cls = T.F("FurnaceClassicBodySize");
                float ratio = RM_FurnaceKernel.SizeRatio(r.Next(4) == 0 ? (float?)null : (float)(r.NextDouble() * 8.0), cls);
                Check(ratio >= 0.25f, "size ratio below its floor");
                Check(RM_FurnaceKernel.SizeRatio(null, cls) == 1f && RM_FurnaceKernel.SizeRatio(cls, cls) == 1f, "a classic-size beast is ratio 1");
                RM_FurnaceKernel.BedCells(ratio, T.I("FurnaceBedIgnitionMinCells"), T.I("FurnaceBedIgnitionMaxCells"), out int lo, out int hi, out float spread);
                Check(lo >= 0 && lo <= hi && spread >= 1.5f, $"bed cells {lo}..{hi}, spread {spread}");
                if (hi == 0) BedZeroCells++;
                RM_FurnaceKernel.BedCells(1f, T.I("FurnaceBedIgnitionMinCells"), T.I("FurnaceBedIgnitionMaxCells"), out int l1, out int h1, out float s1);
                Check(l1 == T.I("FurnaceBedIgnitionMinCells") && h1 == T.I("FurnaceBedIgnitionMaxCells") && s1 == 1.5f, "a ratio-1 beast must smoulder the stated cell range");
                int cd = T.I("FireHawkCooldownTicks"), last = r.Next(-100000, 100000), now = last + r.Next(0, 40000);
                Check(RM_FurnaceKernel.SortieReady(now, last, cd) == (now - last >= cd), "SortieReady");
                Check(RM_FurnaceKernel.SortieReady(last + cd, last, cd) && !RM_FurnaceKernel.SortieReady(last + cd - 1, last, cd), "SortieReady boundary");
                // the warmth maths (existing selftest covers fixed points; this is the property form)
                float rad = 0.5f + (float)r.NextDouble() * 8f, maxC = 14f, strength = (float)r.NextDouble() * 2f;
                float prev = float.MaxValue;
                for (int k = 0; k <= 20; k++)
                {
                    float d = rad * k / 20f; float off = FurnaceWarmthMath.Offset(d * d, rad, maxC, strength);
                    Check(off >= 0f && off <= maxC * strength + 1e-4f && off <= prev + 1e-5f, "warmth offset not bounded / not falling with distance");
                    prev = off;
                }
                Check(FurnaceWarmthMath.Offset(rad * rad, rad, maxC, strength) == 0f && FurnaceWarmthMath.Combine(1f, 2f) == 2f && FurnaceWarmthMath.Combine(2f, 1f) == 2f, "warmth edge / combine");
                float c0 = (float)r.NextDouble() * 3f - 1f;
                float rr = FurnaceWarmthMath.Radius(5f, 0.3f, true, c0);
                Check(rr >= 5f * 0.3f - 1e-5f && rr <= 5f + 1e-5f && FurnaceWarmthMath.Radius(5f, 0.3f, false, c0) == 5f, "warmth radius bounds");
            }));
            return fails;
        }

        private static double TimeToFull(float ambient, float avoid)
        {
            float c = 0f; long ticks = 0;
            while (c < avoid && ticks < 200000000L) { c = RM_FurnaceKernel.ClampCharge(c + StepOf(ambient, false)); ticks += T.I("FurnaceChargeIntervalTicks"); if (StepOf(ambient, false) <= 0f) return -1; }
            return ticks / 60000.0;
        }

        // ════════════════════════ breaker ════════════════════════
        public static long BreakerPlans, BreakerWorth, BreakerNoBoundary, BreakerNoProtected, BreakerBlastsBig, BreakerMonotone;

        private static List<string> Breaker(int n, int seed)
        {
            var fails = new List<string>();
            fails.AddRange(RunSeeded("breaker-graph", n, seed, r =>
            {
                int nodes = 2 + r.Next(40);
                var adj = new List<int>[nodes];
                for (int i = 0; i < nodes; i++) adj[i] = new List<int>();
                int edges = nodes - 1 + r.Next(nodes * 2);
                for (int i = 1; i < nodes && r.Next(8) != 0; i++) { int j = r.Next(i); adj[i].Add(j); adj[j].Add(i); } // mostly connected
                for (int e = 0; e < edges / 2; e++) { int a = r.Next(nodes), b = r.Next(nodes); if (a == b) continue; adj[a].Add(b); adj[b].Add(a); }
                var inNet = new bool[nodes]; var armed = new bool[nodes];
                for (int i = 0; i < nodes; i++) { inNet[i] = r.Next(10) != 0; armed[i] = r.Next(7) == 0; }
                int start = r.Next(nodes);
                RM_BreakerKernel.Section(start, c => adj[c], c => inNet[c], c => armed[c], out HashSet<int> visited, out HashSet<int> boundary);
                // spec: union-find over nodes that may be walked through (in the net, not an armed breaker) plus the start
                var uf = Enumerable.Range(0, nodes).ToArray();
                Func<int, int> find = null; find = x => uf[x] == x ? x : (uf[x] = find(uf[x]));
                Func<int, bool> walk = x => x == start || (inNet[x] && !armed[x]);
                for (int a = 0; a < nodes; a++) if (walk(a)) foreach (int b in adj[a]) if (walk(b)) uf[find(a)] = find(b);
                // the flood only crosses an edge from a node it has entered; a walkable node reached only THROUGH the start is entered too
                var comp = new HashSet<int>(Enumerable.Range(0, nodes).Where(x => walk(x) && find(x) == find(start)));
                var specBoundary = new HashSet<int>();
                foreach (int a in comp) foreach (int b in adj[a]) if (inNet[b] && armed[b] && !comp.Contains(b)) specBoundary.Add(b);
                Check(visited.SetEquals(comp), $"section {{{string.Join(",", visited.OrderBy(x => x))}}}, spec {{{string.Join(",", comp.OrderBy(x => x))}}}");
                Check(boundary.SetEquals(specBoundary), "boundary != armed in-net breakers touching the section");
                Check(visited.Contains(start), "the section lost its start");
                Check(!visited.Overlaps(boundary), "a breaker is both inside the section and on its boundary");
                Check(boundary.All(b => armed[b] && inNet[b]), "a boundary node is not an armed in-net breaker");
                Check(visited.Where(x => x != start).All(x => inNet[x] && !armed[x]), "the section entered an armed or foreign node");
                BreakerPlans++;
                // batteries
                int batt = r.Next(0, 6); int protectedCount = 0, lostCount = 0;
                for (int b = 0; b < batt; b++)
                {
                    bool hasParent = r.Next(5) != 0; int parent = r.Next(nodes); int self = nodes + b;
                    bool inSec = RM_BreakerKernel.InSection(visited, self, hasParent, parent);
                    Check(inSec == (hasParent && comp.Contains(parent)), "battery partition");
                    if (inSec) lostCount++; else protectedCount++;
                }
                bool worth = RM_BreakerKernel.WorthTripping(boundary.Count, protectedCount);
                Check(worth == (boundary.Count > 0 && protectedCount > 0), "WorthTripping");
                if (boundary.Count == 0) BreakerNoBoundary++; else if (protectedCount == 0) BreakerNoProtected++; else BreakerWorth++;
                // arming one more breaker never grows the section
                int extra = r.Next(nodes);
                if (extra != start && !armed[extra])
                {
                    armed[extra] = true;
                    RM_BreakerKernel.Section(start, c => adj[c], c => inNet[c], c => armed[c], out HashSet<int> v2, out HashSet<int> b2);
                    Check(v2.IsSubsetOf(visited), "arming a breaker grew the section");
                    Check(!v2.Contains(extra) || extra == start, "an armed breaker was entered");
                    BreakerMonotone++;
                }
                // blast
                float e1 = (float)(r.NextDouble() * 5000.0), e2 = e1 + (float)(r.NextDouble() * 5000.0);
                float r1 = RM_BreakerKernel.BlastRadius(e1), r2 = RM_BreakerKernel.BlastRadius(e2);
                Check(r1 >= 1.5f && r1 <= 14.9f && r2 >= r1 - 1e-6f, "blast radius out of bounds / not monotone");
                Check(RM_BreakerKernel.BlastRadius(0f) == 1.5f && RM_BreakerKernel.BlastRadius(1e9f) == 14.9f, "blast radius clamps");
                Check(RM_BreakerKernel.SecondBlast(3.51f) && !RM_BreakerKernel.SecondBlast(3.5f), "second-blast boundary");
                if (RM_BreakerKernel.SecondBlast(r1)) BreakerBlastsBig++;
                Check(RM_BreakerKernel.LostCanBlast(new[] { 20.1f }) && !RM_BreakerKernel.LostCanBlast(new[] { 20f, 5f }) && !RM_BreakerKernel.LostCanBlast(new float[0]), "LostCanBlast boundary");
                Steps += nodes + batt;
            }));
            fails.AddRange(RunSeeded("breaker-arm", n, seed + 777, r =>
            {
                for (int m = 0; m < 16; m++)
                {
                    bool tripped = (m & 1) != 0, on = (m & 2) != 0, hopper = (m & 4) != 0, fueled = (m & 8) != 0;
                    float cost = 10f, fuel = fueled ? 10f : 9.99f;
                    bool want = !tripped && on && (!hopper || fuel >= cost);
                    Check(RM_BreakerKernel.Armed(tripped, on, hopper, fuel, cost) == want, "Armed table " + m);
                }
            }));
            return fails;
        }

        // ════════════════════════ eco ════════════════════════
        public static long ScoresInBand, ScoresOutside, ScoresOff, AshSkips, AshAttemptsTotal, OnceHits, OnceClears, ParseCases;

        private static List<string> Eco(int n, int seed)
        {
            return RunSeeded("eco", n, seed, r =>
            {
                float tMin = 25f, tMax = 60f, rMin = 550f, rMax = 1000f, eMin = 0f, eMax = 2200f, bs = 30f, dw = 2.6f, div = 120f;
                float temp = (float)(r.NextDouble() * 90.0 - 10.0), rain = (float)(r.NextDouble() * 1600.0), elev = (float)(r.NextDouble() * 3000.0);
                bool gen = r.Next(10) != 0, has = r.Next(20) != 0, water = r.Next(8) == 0, mount = r.Next(6) == 0;
                float s = RM_FireEcoKernel.BiomeScore(gen, has, water, temp, rain, elev, mount, tMin, tMax, rMin, rMax, eMin, eMax, bs, dw, div);
                float spec = !gen || !has || water ? -100f
                    : temp < tMin || temp > tMax || rain < rMin || rain >= rMax || elev < eMin || elev > eMax || mount ? 0f
                    : bs + (temp - tMin) * dw + (rain - rMin) / div;
                Check(s == spec, $"biome score {s}, spec {spec}");
                if (s > 0f) { ScoresInBand++; Check(s >= bs, "an in-band score below the base score"); } else if (s == 0f) ScoresOutside++; else ScoresOff++;
                Check(RM_FireEcoKernel.BiomeScore(true, true, false, 40f, rMax, 100f, false, tMin, tMax, rMin, rMax, eMin, eMax, bs, dw, div) == 0f, "rainfall is not half-open at the top");
                Check(RM_FireEcoKernel.BiomeScore(true, true, false, 40f, rMin, 100f, false, tMin, tMax, rMin, rMax, eMin, eMax, bs, dw, div) > 0f, "rainfall floor is not inclusive");
                Check(RM_FireEcoKernel.BiomeScore(true, true, false, 40f, 700f, 100f, false, tMin, tMax, rMin, rMax, eMin, eMax, bs, dw, 0f) > 0f, "a zero rainfall divisor broke the score");
                // monotone in temperature and rainfall inside the band
                float t2 = Math.Min(tMax, 30f + (float)r.NextDouble() * 30f), r2 = 600f + (float)r.NextDouble() * 350f;
                float a1 = RM_FireEcoKernel.BiomeScore(true, true, false, t2, r2, 100f, false, tMin, tMax, rMin, rMax, eMin, eMax, bs, dw, div);
                float a2 = RM_FireEcoKernel.BiomeScore(true, true, false, Math.Min(tMax, t2 + 1f), r2 + 10f, 100f, false, tMin, tMax, rMin, rMax, eMin, eMax, bs, dw, div);
                Check(a2 >= a1, "a warmer, wetter tile scored lower");
                // the vanilla rival (arid shrubland) at the same tile: report where the Pyrelands out-bids it
                // ash-fall rate / attempts
                bool ashFall = r.Next(4) == 0, cinder = !ashFall && r.Next(4) == 0, nativeB = r.Next(2) == 0, cross = r.Next(2) == 0;
                float cov = r.Next(0, 5) / 4f, mult = 0.25f + r.Next(0, 12) / 4f;
                float rate = RM_FireEcoKernel.AshRate(ashFall, cinder, 0.45f, nativeB, cross, cov, mult);
                float specRate = ashFall ? mult : cinder ? 0.45f * mult : !nativeB && cross ? cov * mult : -1f;
                Check(rate == specRate, $"ash rate {rate}, spec {specRate}");
                int area = 100 + r.Next(250000);
                int att = RM_FireEcoKernel.AshAttempts(area, 4000f, rate < 0 ? 0f : rate);
                if (rate <= 0f) { Check(att == 0, $"a rate of {rate} still deposits {att} ash"); AshSkips++; }
                else { Check(att >= 1 && att >= (int)((float)area / 4000f * rate), "ash attempts below the floor"); AshAttemptsTotal += att; }
                Check(RM_FireEcoKernel.AshAttempts(area * 2, 4000f, 1f) >= RM_FireEcoKernel.AshAttempts(area, 4000f, 1f), "a bigger map got fewer ash attempts");
                // once-per-fire roll set
                var set = new HashSet<int>(); int bound = 50;
                for (int k = 0; k < 400; k++)
                {
                    int id = r.Next(120); int before = set.Count;
                    bool first = RM_FireEcoKernel.MarkOnce(set, id, bound);
                    Check(set.Count <= bound + 1, "the rolled set outgrew its bound");
                    if (before > bound) { OnceClears++; Check(first && set.Count == 1, "the set was not cleared wholesale past its bound"); } else OnceHits += first ? 1 : 0;
                    Check(set.Contains(id), "MarkOnce did not record the id");
                    Check(!RM_FireEcoKernel.MarkOnce(set, id, bound + 1000) || set.Count > 0, "unreachable");
                    Steps++;
                }
                // list parser vs spec
                string[] bits = { "RM_A", " RM_B ", "", ";", ",", "  ", "x;y", "\tZ\t", "A,B;C" };
                var sb = new System.Text.StringBuilder(); int parts = r.Next(0, 8);
                for (int k = 0; k < parts; k++) { sb.Append(bits[r.Next(bits.Length)]); if (r.Next(2) == 0) sb.Append(r.Next(2) == 0 ? "," : ";"); }
                string text = r.Next(10) == 0 ? null : sb.ToString();
                var got = RM_FireEcoKernel.ParseList(text);
                var want = (text ?? "").Split(new[] { ',', ';' }).Select(x => x.Trim()).Where(x => x.Length > 0).ToList();
                Check(got.SequenceEqual(want), $"ParseList [{string.Join("|", got)}], spec [{string.Join("|", want)}] for '{text}'");
                ParseCases++;
                // gates, exhaustively
                for (int m = 0; m < 32; m++)
                {
                    bool fe = (m & 1) != 0, usable = (m & 2) != 0, sand = (m & 4) != 0, pe = (m & 8) != 0, pg = (m & 16) != 0;
                    bool want2 = fe && usable && sand && (pe || !pg);
                    Check(RM_FireEcoKernel.FulguriteMayRoll(fe, usable, sand, pe, pg) == want2, "FulguriteMayRoll table " + m);
                }
                for (int m = 0; m < 64; m++)
                {
                    bool pe = (m & 1) != 0, ash = (m & 2) != 0, fruit = (m & 4) != 0, spawned = (m & 8) != 0, att2 = (m & 16) != 0, scorch = (m & 32) != 0;
                    bool want3 = pe && (ash || fruit) && spawned && !att2 && scorch;
                    Check(RM_FireEcoKernel.FireTickMayRoll(pe, ash, fruit, spawned, att2, scorch) == want3, "FireTickMayRoll table " + m);
                }
                for (int m = 0; m < 32; m++)
                {
                    bool en = (m & 1) != 0, hasB = (m & 2) != 0, nat = (m & 4) != 0, every = (m & 8) != 0, listed = (m & 16) != 0;
                    Check(RM_FireEcoKernel.CrossBiomeApplies(en, hasB, nat, every, listed) == (en && hasB && !nat && (every || listed)), "CrossBiomeApplies table " + m);
                }
                string[] fam = { "RM_FE_Ground_Sand", "Sand", "SoftSand", "RM_DeepSand" };
                Check(RM_FireEcoKernel.IsSandFamily("Sand", fam) && !RM_FireEcoKernel.IsSandFamily("sand", fam) && !RM_FireEcoKernel.IsSandFamily(null, fam) && !RM_FireEcoKernel.IsSandFamily("SandX", fam), "IsSandFamily exact match");
                Check(RM_FireEcoKernel.IsPyrelandsGround("RM_FE_Anything") && !RM_FireEcoKernel.IsPyrelandsGround("RM_FE") && !RM_FireEcoKernel.IsPyrelandsGround("rm_fe_x") && !RM_FireEcoKernel.IsPyrelandsGround(null), "IsPyrelandsGround prefix");
                Check(RM_FireEcoKernel.IsScorchableGround("RM_FE_Ground_Ash") && RM_FireEcoKernel.IsScorchableGround("SoilRich") && !RM_FireEcoKernel.IsScorchableGround("RM_FE_Ash_Heavy") && !RM_FireEcoKernel.IsScorchableGround("SandX") && !RM_FireEcoKernel.IsScorchableGround(null), "IsScorchableGround");
                Check(RM_FireEcoKernel.DustChance(0.02f, 15) == 0.02f * 15 && RM_FireEcoKernel.UnderFruitCap(39, 40) && !RM_FireEcoKernel.UnderFruitCap(40, 40), "dust chance / fruit cap");
            });
        }

        // ════════════════════════ units ════════════════════════
        private static List<string> Units()
        {
            var fails = new List<string>();
            try
            {
                Cases++;
                Check(T.Count > 40, "PyrelandsTuning.cs parsed to only " + T.Count + " constants: the reader is blind");
                float cap = T.F("ArsonDebtCap");
                Check(T.F("ArsonDebtRaidThreshold") <= cap, "the default raid threshold is above the debt cap");
                Check(T.F("ArsonDebtPerPlayerFirePerCheck") > 0f && T.F("ArsonDebtDecayPerCheck") > 0f, "arson accrual or decay is not positive");
                Check(T.F("ArsonDebtDecayPerCheck") < T.F("ArsonDebtPerPlayerFirePerCheck") * 10f, "arson decay outpaces ten fires");
                Check(T.F("FireFrontMinDays") > 0f && T.F("FireFrontMinDays") <= T.F("FireFrontMaxDays"), "fire front days not ordered");
                Check(T.I("FireFrontWidthCells") >= 1 && T.I("FlameHarvestMinFires") >= 1 && T.I("FireRiteGroupMin") >= 1 && T.I("FireRiteGroupMin") <= T.I("FireRiteGroupMax"), "front width / harvest minimum / rite party size");
                Check(T.I("FireRaidGoodwillHit") < 0 && T.F("FireRaidPointsMin") > 0f && T.F("FireRaidPointsFactor") > 0f && T.F("FireRaidPointsFactor") <= 1f, "raid tuning");
                Check(T.F("FurnaceChargeSeekBelow") < T.F("FurnaceChargeAvoidAbove") && T.F("FurnaceChargeAvoidAbove") <= 1f && T.F("FurnaceChargeSeekBelow") > 0f, "charge hysteresis is not ordered inside (0,1]");
                Check(T.F("FurnaceBleedAmbientC") < T.F("FurnaceChargeAmbientC"), "the bleed and charge ambients overlap (no dead band)");
                Check(T.F("FurnaceChargeAmbientSpanC") > 0f && T.F("FurnaceBleedAmbientSpanC") > 0f, "a zero span would divide by zero");
                Check(T.I("WorldHerdDeepDesertDwellTicks") <= T.I("WorldHerdMaxLegDwellTicks"), "the desert dwell is longer than the max dwell");
                Check(T.I("StandingBurnRetryTicks") <= T.I("StandingBurnQuietTicks") && T.I("BurnWatchIntervalTicks") > 0, "standing-burn clock");
                Check(T.F("FireFrontFireSize") > 0f && T.F("SmoulderFireSize") > 0f, "fire sizes");
                Check(T.I("WorldHerdMinSize") <= T.I("WorldHerdMaxSize"), "herd size range");
                Check(T.A("PyrelandsBiomeDefNames").Length > 0 && T.A("NearTerminatorBiomeDefNames").Length > 0 && T.A("DeepDesertBiomeDefNames").Length > 0, "a herd leg has no biomes");
                var all = T.A("PyrelandsBiomeDefNames").Concat(T.A("NearTerminatorBiomeDefNames")).Concat(T.A("DeepDesertBiomeDefNames")).ToList();
                Check(all.Count == all.Distinct().Count(), "a biome is listed on two herd legs: " + string.Join(",", all.GroupBy(x => x).Where(g => g.Count() > 1).Select(g => g.Key)));
                // fire raid gate table
                for (int m = 0; m < 256; m++)
                {
                    bool en = (m & 1) != 0, bc = (m & 2) != 0, pw = (m & 4) != 0, tp = (m & 8) != 0, ho = (m & 16) != 0, hg = (m & 32) != 0, enough = (m & 64) != 0, big = (m & 128) != 0;
                    float thr = big ? 2000f : 400f, debt = enough ? Math.Min(thr, cap) : Math.Min(thr, cap) - 0.5f;
                    bool want = en && bc && pw && enough && tp && (ho || hg);
                    Check(RM_BurnKernel.RaidCanFire(en, bc, pw, debt, thr, cap, tp, ho, hg) == want, "RaidCanFire table " + m);
                    Check(RM_BurnKernel.HarvestCanFire(en, bc, pw, enough, 10, 10, tp, ho) == (en && bc && pw && enough && tp && !ho), "HarvestCanFire table " + m);
                }
                Check(RM_BurnKernel.EffectiveRaidThreshold(2000f, cap) == cap && RM_BurnKernel.EffectiveRaidThreshold(100f, cap) == 100f, "EffectiveRaidThreshold");
                Check(RM_BurnKernel.PlayerAttributed(true, true, true) && !RM_BurnKernel.PlayerAttributed(false, true, true) && !RM_BurnKernel.PlayerAttributed(true, false, true) && !RM_BurnKernel.PlayerAttributed(true, true, false), "PlayerAttributed");
                Check(RM_BurnKernel.RaidPlan(false, true, true) == RM_RaidPlan.Refuse && RM_BurnKernel.RaidPlan(true, true, false) == RM_RaidPlan.RaidNow && RM_BurnKernel.RaidPlan(true, false, true) == RM_RaidPlan.InsultFirst && RM_BurnKernel.RaidPlan(true, false, false) == RM_RaidPlan.Refuse, "RaidPlan table");
                Check(RM_BurnKernel.RaidPoints(0f, 1000f, 0.6f, 250f) == 600f && RM_BurnKernel.RaidPoints(100f, 0f, 0.6f, 250f) == 250f && RM_BurnKernel.RaidPoints(-5f, 100f, 0.6f, 250f) == 250f, "RaidPoints");
                // keep-alive and centroid corners
                // exact boundaries the random streams (all multiples of the watch interval) cannot land on
                Check(RM_BurnKernel.ArsonStep(0.2f, 0, 1f, cap, 0.5f) == 0f && RM_BurnKernel.ArsonStep(0f, 0, 1f, cap, 0.5f) == 0f && RM_BurnKernel.ArsonStep(cap, 1, 1f, cap, 0.5f) == cap, "ArsonStep clamps at 0 and at the cap");
                { int q = 0; Check(RM_BurnKernel.KeepAlive(0, ref q, 60, 120, 1100, 1000, 100) == RM_ReseedDecision.Quiet && RM_BurnKernel.KeepAlive(0, ref q, 60, 120, 1100, 1000, 100) == RM_ReseedDecision.Reseed && RM_BurnKernel.KeepAlive(0, ref q, 60, 120, 1099, 1000, 100) == RM_ReseedDecision.Retry, "KeepAlive: a retry window of exactly retryTicks has elapsed"); }
                {
                    var tk = new List<int> { 0 }; var cl = new List<int> { 1 };
                    Check(RM_BurnKernel.RecordHistory(tk, cl, 2500, 2, 2500, 600000) && !RM_BurnKernel.RecordHistory(tk, cl, 4999, 3, 2500, 600000) && tk.Count == 2, "RecordHistory: a gap of exactly the interval adds a sample, one tick less does not");
                    Check(RM_BurnKernel.HistoryIndexAgo(tk, 3000, 500) == 1 && RM_BurnKernel.HistoryIndexAgo(tk, 3000, 501) == 0, "HistoryIndexAgo: a sample exactly ticksAgo old counts");
                }
                {
                    int rest = 0;
                    RM_FurnaceKernel.RestStep(ref rest, false, 2500, 2500);
                    Check(RM_FurnaceKernel.RestStep(ref rest, true, 30, 2500) == RM_RestOutcome.WokeRested, "RestStep: a rest of exactly the minimum counts");
                    rest = 0; RM_FurnaceKernel.RestStep(ref rest, false, 2499, 2500);
                    Check(RM_FurnaceKernel.RestStep(ref rest, true, 30, 2500) == RM_RestOutcome.WokeTooShort, "RestStep: one tick under the minimum is too short");
                }
                Check(RM_FireEcoKernel.IsScorchableGround("Gravel") && RM_FireEcoKernel.IsScorchableGround("Soil") && RM_FireEcoKernel.IsScorchableGround("Sand") && RM_FireEcoKernel.IsScorchableGround("RM_FE_Ground_Gravel"), "scorchable ground names");
                int ts = 0;
                Check(RM_BurnKernel.KeepAlive(0, ref ts, 60, 120, 1000, 0, 100) == RM_ReseedDecision.Quiet && ts == 60 && RM_BurnKernel.KeepAlive(0, ref ts, 60, 120, 1000, 0, 100) == RM_ReseedDecision.Reseed && RM_BurnKernel.KeepAlive(0, ref ts, 60, 120, 1050, 1000, 100) == RM_ReseedDecision.Retry, "KeepAlive corners");
                Check(RM_BurnKernel.KeepAlive(3, ref ts, 60, 120, 1000, 0, 100) == RM_ReseedDecision.FiresPresent && ts == 0, "a fire resets the quiet clock");
                Check(!RM_BurnKernel.Centroid(0, 0, 0, out _, out _) && RM_BurnKernel.Centroid(7, 9, 2, out int cx, out int cz) && cx == 3 && cz == 4, "Centroid truncates");
                Check(RM_BurnKernel.MeasureDue(60, 0, 60) && !RM_BurnKernel.MeasureDue(60, 1, 60) && RM_BurnKernel.MeasureDue(59, 1, 60), "MeasureDue offset by map id");
                int nf = 5;
                Check(RM_BurnKernel.FrontTick(ref nf, 10, false, () => 99) == RM_FrontAction.Disabled && nf == -1 && RM_BurnKernel.FrontTick(ref nf, 10, true, () => 99) == RM_FrontAction.Armed && nf == 109 && RM_BurnKernel.FrontTick(ref nf, 108, true, () => 99) == RM_FrontAction.Wait && RM_BurnKernel.FrontTick(ref nf, 109, true, () => 50) == RM_FrontAction.Fire && nf == 159, "FrontTick table");
                Check(RM_BurnKernel.ScheduleTicks(2f, 4f, 0f, 60000) == 120000 && RM_BurnKernel.ScheduleTicks(2f, 4f, 1f, 60000) == 240000, "ScheduleTicks ends");
            }
            catch (Exception e) { fails.Add("units: " + e.Message); }
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only, string tuningPath)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            try
            {
                if (tuningPath == null) throw new Exception("--tuning <path to PyrelandsTuning.cs> was not given");
                T = Tun.Load(tuningPath);
            }
            catch (Exception e) { Console.WriteLine("FAIL cannot read the tuning constants (a fuzz that cannot read them is blind): " + e.Message); return false; }
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("burn", () => Burn(N(1200), S(1))),
                ("furnace", () => Furnace(N(800), S(1))),
                ("breaker", () => Breaker(N(3000), S(1))),
                ("eco", () => Eco(N(4000), S(1))),
                ("units", () => Units()),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            Console.WriteLine($"burn: measures {Measures}, debt rises {DebtRises} / decays {DebtDecays}, reseed attempts {ReseedAttempts} (landed {ReseedSuccess}), fronts armed {FrontsArmed} / fired {FrontsFired}, history samples {HistorySamples} (longest ring {HistoryMaxLen}), raids fired {RaidsFired} / insults {RaidInsults} / refused {RaidRefused} / gated off {RaidGated}, arson-liveness probes {LivenessChecks}, harvests allowed {HarvestsAllowed} / refused {HarvestsRefused}");
            Console.WriteLine($"burn front line: the old truncated construction lit {LegacyWidths - LegacyCellsLost} of {LegacyWidths} requested cells ({100.0 * (LegacyWidths - LegacyCellsLost) / Math.Max(1, LegacyWidths):F1}%); the kernel line is exact");
            Console.WriteLine($"furnace: charge ups {ChargeUps} / downs {ChargeDowns} / holds {ChargeHolds}, herd advances {HerdAdvances}, searches found {BfsFound} / missed {BfsMissed}, rests rolled {RestsRolled} / too short {RestsShort}, small beasts with zero bed cells {BedZeroCells}; empty-to-full at 40 C = {ChargeDaysAt40:F1} days, at 60 C = {ChargeDaysAt60:F1} days");
            Console.WriteLine($"breaker: plans {BreakerPlans} (worth tripping {BreakerWorth}, no boundary {BreakerNoBoundary}, no spared battery {BreakerNoProtected}), arm-monotone probes {BreakerMonotone}, second blasts {BreakerBlastsBig}");
            Console.WriteLine($"eco: scores in band {ScoresInBand} / outside {ScoresOutside} / off {ScoresOff}, zero-rate skips {AshSkips}, ash attempts {AshAttemptsTotal}, once-hits {OnceHits}, set clears {OnceClears}, list parses {ParseCases}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                var blind = new List<string>();
                if (Measures == 0 || DebtRises == 0 || DebtDecays == 0 || ReseedAttempts == 0 || ReseedSuccess == 0 || FrontsFired == 0 || FrontsArmed == 0 || HistorySamples == 0 || RaidsFired == 0 || RaidInsults == 0 || RaidGated == 0 || LivenessChecks == 0 || HarvestsAllowed == 0 || HarvestsRefused == 0) blind.Add("burn never measured/accrued/decayed/reseeded/fired a front/recorded history/raided/insulted/gated/proved liveness/allowed or refused a harvest");
                if (ChargeUps == 0 || ChargeDowns == 0 || ChargeHolds == 0 || HerdAdvances == 0 || BfsFound == 0 || BfsMissed == 0 || RestsRolled == 0 || RestsShort == 0) blind.Add("furnace never charged/bled/held/advanced a herd/found/missed a tile/rolled a rest/skipped a short rest");
                if (BreakerPlans == 0 || BreakerWorth == 0 || BreakerNoBoundary == 0 || BreakerNoProtected == 0 || BreakerMonotone == 0) blind.Add("breaker never planned / found a worthwhile trip / saw an unbounded fault / saw no spared battery");
                if (ScoresInBand == 0 || ScoresOutside == 0 || ScoresOff == 0 || AshSkips == 0 || AshAttemptsTotal == 0 || OnceClears == 0) blind.Add("eco never scored in/out of band/off, skipped a zero rate, deposited ash, or cleared its roll set");
                foreach (var b in blind) { Console.WriteLine("FAIL fuzz is blind: " + b); ok = false; }
            }
            Console.WriteLine($"pyrelands fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
