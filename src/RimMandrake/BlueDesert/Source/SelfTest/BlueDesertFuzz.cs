// Approach B for BlueDesert: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/*.cs):
//   cold     the blue-ice heat sink: heat/ice conservation against the vanilla cooler step, melt drips, clarity stages (RM_BlueKernel)
//   thaw     the thaw-roll counter, the weighted pick shared with the ablation corpses
//   rules    vhaulk detonation gate, EMP trap, plant charge, road/departure, ablation timeline, ossivel choir, virr song
//   murrek   the reseed plan after an ice-sand drift: burrows, spacing, the spawn cap (RM_MurrekKernel)
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.BlueDesert.SelfTest
{
    internal static class BlueDesertFuzz
    {
        public static long Cases, Steps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static bool Near(double a, double b, double eps) { return Math.Abs(a - b) <= eps; }

        internal struct Act
        {
            public int kind, a, b;
            public string[] names;
            public override string ToString() { return (names != null && kind < names.Length ? names[kind] : "k" + kind) + "(" + a + "," + b + ")"; }
        }

        internal static List<T> Shrink<T>(List<T> acts, Func<List<T>, bool> fails)
        {
            var cur = new List<T>(acts);
            for (int chunk = Math.Max(1, cur.Count / 2); chunk >= 1; chunk /= 2)
            {
                bool progress = true;
                while (progress)
                {
                    progress = false;
                    for (int i = 0; i + chunk <= cur.Count; i++)
                    {
                        var trial = new List<T>(cur);
                        trial.RemoveRange(i, chunk);
                        if (fails(trial)) { cur = trial; progress = true; break; }
                    }
                }
            }
            return cur;
        }

        private static string Drive(int seed, Func<Random, List<Act>> gen, Func<int, List<Act>, string> run)
        {
            var acts = gen(new Random(seed));
            string err = run(seed, acts);
            if (err == null) return null;
            var small = Shrink(acts, t => run(seed, t) != null);
            return run(seed, small) + " | " + string.Join(" ", small);
        }

        private static List<string> Family(string name, int n, int baseSeed, Func<int, string> one)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                Cases++;
                try { string e = one(baseSeed + k); if (e != null) fails.Add($"{name} seed {baseSeed + k}: {e}"); }
                catch (Exception e) { fails.Add($"{name} seed {baseSeed + k}: {e.Message} {(e is IndexOutOfRangeException || e is ArgumentOutOfRangeException ? e.StackTrace : "")}"); }
            }
            return fails;
        }

        private static List<Act> GenActs(Random r, int minN, int maxN, int[] weights, string[] names)
        {
            int total = weights.Sum(), n = minN + r.Next(maxN - minN + 1);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(total), kind = 0;
                while (w >= weights[kind]) { w -= weights[kind]; kind++; }
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = names });
            }
            return l;
        }


        // ════════════════════════ cold ════════════════════════
        private static readonly string[] CdNames = { "Tick", "Warm", "Load", "Target", "Factor", "Blackout" };
        public static long Absorbs, Drips, Empties, StageChanges;

        // vanilla GenTemperature.ControlTemperatureTempChange for a cooler (energyLimit < 0)
        private static float CoolStep(float roomTemp, int cells, float energyLimit, float target)
        {
            float a = energyLimit / cells, b = target - roomTemp;
            float num = Math.Max(a, b);
            if (num > 0f) num = 0f;
            return num;
        }

        private static string RunCold(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0xc01d);
            int cells = new[] { 1, 6, 30, 120 }[r.Next(4)];
            float T = 25f, target = -5f, fuel = 0f, maxFuel = 20f, melted = 0f;
            float cold = new[] { 500f, 60f, 5000f }[r.Next(3)], factor = 1f, perSec = -12f, blocksPerCan = new[] { 5f, 1f, 0f }[r.Next(3)];
            int cansPerMelt = new[] { 0, 1, 3 }[r.Next(3)];
            double heatRemoved = 0, blocksUsed = 0; long cans = 0; double meltedTotal = 0;
            int lastStage = RM_BlueKernel.ClarityStage(true, fuel / maxFuel);
            bool power = true;
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                switch (a.kind)
                {
                    case 1: T += (a.a % 30) * (cells > 30 ? 0.2f : 1f); break;
                    case 2: fuel = Math.Min(maxFuel, fuel + (a.a % 8)); break;
                    case 3: target = new[] { -20f, -5f, 10f, 21f }[a.a % 4]; break;
                    case 4: factor = new[] { 0.1f, 1f, 3f }[a.a % 3]; break;
                    case 5: power = !power; break;   // the rack draws no power: nothing depends on it
                    case 0:
                        {
                            float cpb = RM_BlueKernel.ColdPerBlock(cold, factor);
                            Check(cpb >= 1f, "cold per block under 1" + where);
                            if (fuel <= 0f) { Empties++; break; }
                            float step0 = CoolStep(T, cells, perSec * 4.1666665f, target);
                            float scaled, blocks;
                            float fuelBefore = fuel, tBefore = T;
                            bool worked = RM_BlueKernel.Absorb(step0, cells, fuel, cpb, out scaled, out blocks);
                            Check(worked == (step0 < 0f && Math.Abs(step0) >= 1e-6f), "Absorb verdict != 'the room is above target'" + where);
                            if (!worked) { Check(scaled == 0f && blocks == 0f, "a rack that did nothing reported work" + where); break; }
                            Absorbs++;
                            Check(scaled <= 0f && scaled >= step0 - 1e-6f, "the scaled cooling step is warmer than 0 or colder than asked" + where);
                            Check(blocks >= 0f && blocks <= fuelBefore + 1e-4f, $"used {blocks} blocks of {fuelBefore}" + where);
                            // heat conservation: what the room lost is what the ice absorbed
                            Check(Near(-scaled * cells, blocks * cpb, 1e-2 + 1e-4 * blocks * cpb), $"room lost {-scaled * cells} heat, ice absorbed {blocks * cpb}" + where);
                            T += scaled; fuel -= blocks;
                            heatRemoved += -scaled * cells; blocksUsed += blocks * cpb;
                            Check(T >= target - 1e-3f || tBefore < target, "the rack cooled the room past its target" + where);
                            Check(fuel >= -1e-4f, "negative ice" + where);
                            if (fuel < 0f) fuel = 0f;
                            melted += blocks; meltedTotal += blocks;
                            float meltedBeforeDrip = melted;
                            int drips = RM_BlueKernel.Drip(ref melted, blocksPerCan);
                            Drips += drips;
                            if (blocksPerCan <= 0f) Check(drips == 0 && melted == meltedBeforeDrip, "dripped with no blocksPerCan" + where);
                            else
                            {
                                Check(melted < blocksPerCan && melted >= -1e-4f, $"melt store {melted} not in [0, {blocksPerCan})" + where);
                                Check(Near(melted + drips * blocksPerCan, meltedBeforeDrip, 1e-3), "the drips did not account for the melt" + where);
                                cans += (long)drips * RM_BlueKernel.CansPerDrip(cansPerMelt);
                            }
                            Check(RM_BlueKernel.CansPerDrip(cansPerMelt) >= 1, "a drip with no cans" + where);
                            break;
                        }
                }
                int stage = RM_BlueKernel.ClarityStage(true, fuel / maxFuel);
                if (stage != lastStage) StageChanges++;
                lastStage = stage;
                float pct = fuel / maxFuel;
                Check(stage == (pct > 0.5f ? 0 : pct > 0.1f ? 1 : 2), $"clarity {stage} at {pct}" + where);
                Check(Near(heatRemoved, blocksUsed, 1e-2 + 1e-4 * blocksUsed), "total heat removed != total ice absorbed" + where);
            }
            if (blocksPerCan > 0f) Check(Math.Abs(meltedTotal - (cans / (double)RM_BlueKernel.CansPerDrip(cansPerMelt)) * blocksPerCan - melted) < 1e-2 + 1e-4 * meltedTotal, "melt, cans and store do not balance at the end");
            return null;
        }

        private static string ColdUnits(int seed)
        {
            Check(RM_BlueKernel.ClarityStage(false, 1f) == 2 && RM_BlueKernel.ClarityStage(true, 0.5f) == 1 && RM_BlueKernel.ClarityStage(true, 0.5001f) == 0 && RM_BlueKernel.ClarityStage(true, 0.1f) == 2 && RM_BlueKernel.ClarityStage(true, 0.1001f) == 1, "clarity boundaries");
            Check(RM_BlueKernel.ColdPerBlock(500f, 0f) == 1f && RM_BlueKernel.ColdPerBlock(500f, 2f) == 1000f, "cold per block");
            float s, b;
            Check(!RM_BlueKernel.Absorb(0f, 10, 5f, 500f, out s, out b) && !RM_BlueKernel.Absorb(3f, 10, 5f, 500f, out s, out b), "a warming step must never consume ice (ConsumeFuel would ADD fuel for a negative count)");
            // exactly enough ice: the whole store goes, no more
            Check(RM_BlueKernel.Absorb(-2f, 10, 1f, 20f, out s, out b) && Near(b, 1f, 1e-5) && Near(s, -2f, 1e-5), "exactly enough ice");
            Check(RM_BlueKernel.Absorb(-2f, 10, 0.5f, 20f, out s, out b) && Near(b, 0.5f, 1e-5) && Near(s, -1f, 1e-5), "half the ice cools half as far");
            return null;
        }

        // ════════════════════════ thaw ════════════════════════
        public static long Rolls, Picks;

        private static string ThawCase(int seed)
        {
            var r = new Random(seed ^ 0x7a);
            int per = new[] { -1, 0, 1, 3, 7 }[r.Next(5)];
            int since = 0, rolled = 0, mined = 0;
            for (int i = 0; i < 200; i++)
            {
                mined++;
                if (RM_BlueKernel.ThawCounts(ref since, per)) { rolled++; Rolls++; Check(since == 0, "the counter did not reset after a roll"); }
                Check(since >= 0 && since < Math.Max(1, per), "counter outside [0, blocksPerRoll)");
            }
            Check(rolled == mined / Math.Max(1, per), $"{rolled} rolls from {mined} blocks at {per} per roll");
            // weighted pick
            int n = r.Next(0, 6); var w = new float[n];
            for (int i = 0; i < n; i++) w[i] = new[] { -2f, 0f, 0.5f, 1f, 3f }[r.Next(5)];
            double total = w.Sum(x => Math.Max(0f, x));
            int[] hits = new int[n]; int N = 2000, none = 0;
            for (int k = 0; k < N; k++)
            {
                int p = RM_BlueKernel.PickWeighted(w, n, (k + 0.5) / N);
                if (p < 0) { none++; continue; }
                Check(p < n && w[p] > 0f, "picked an item with no weight");
                hits[p]++; Picks++;
            }
            if (total <= 0) Check(none == N, "picked from nothing");
            else
            {
                Check(none == 0, "a roll found nothing though weights exist");
                for (int i = 0; i < n; i++) Check(Math.Abs(hits[i] / (double)N - Math.Max(0f, w[i]) / total) < 0.01, $"item {i} picked {hits[i] / (double)N}, weight share {Math.Max(0f, w[i]) / total}");
            }
            Check(RM_BlueKernel.PickWeighted(new[] { 1f }, 1, 0.9999999999) == 0, "a roll at the top of the range must still pick");
            Check(RM_BlueKernel.ThawStack(0, 75) == 1 && RM_BlueKernel.ThawStack(99, 75) == 75 && RM_BlueKernel.ThawStack(4, 0) == 1 && RM_BlueKernel.ThawStack(4, 75) == 4, "thaw stack clamp");
            return null;
        }

        // ════════════════════════ rules ════════════════════════
        public static long Detonations, EmpKills, ChargeBooms, Departs, ChoirSongs, ChoirSilences, Exposures;
        private static readonly string[] RlNames = { "Charge", "Choir", "Time", "Intruder", "Singer", "Depart", "Stage" };

        private static string RunRules(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x1f);
            // charge
            int warm = 0; bool chargeOn = true;
            // choir
            int now = r.Next(0, 10000); int silencedUntil = -1; int min = 3; float radius = 15f; int hold = 900;
            var singers = new List<int[]>(); var intruders = new List<int[]>();
            int lastIntruderTick = int.MinValue;
            // ablation
            int stage = 0; int silTick = RM_BlueKernel.SilhouetteTick(now, 2f + (float)r.NextDouble(), new[] { 0.1f, 1f, 3f }[r.Next(3)]);
            int expTick = RM_BlueKernel.ExposureTick(silTick, 3f + (float)r.NextDouble(), 1f);
            int calls = 0, exposes = 0; int prevStage = 0;
            // depart
            int departTick = RM_BlueKernel.DepartTick(now, 0.2f, 1f); bool departing = false;
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                switch (a.kind)
                {
                    case 2: now += 1 + a.a % 9000; break;
                    case 3: intruders.Add(new[] { a.a % 41 - 20, a.b % 41 - 20 }); if (intruders.Count > 3) intruders.RemoveAt(0); break;
                    case 4: if (a.b % 3 == 0 && singers.Count > 0) singers.RemoveAt(0); else singers.Add(new[] { a.a % 11 - 5, a.b % 11 - 5 }); if (singers.Count > 7) singers.RemoveAt(0); break;
                    case 0:
                        {
                            bool enabled = a.a % 9 != 0, hasMap = a.a % 11 != 0, warmNow = a.b % 2 == 0;
                            int before = warm;
                            int act = RM_BlueKernel.ChargeStep(ref warm, enabled, hasMap, warmNow);
                            if (!enabled) Check(act == 0 && warm == 0, "a disabled charge advanced" + where);
                            else if (!hasMap) Check(act == 0 && warm == before, "a charge off the map advanced" + where);
                            else if (warmNow) { Check(warm == before + 1 && act == (warm >= 2 ? 2 : 1), $"warm step: {before} -> {warm}, act {act}" + where); if (act == 2) ChargeBooms++; }
                            else Check(warm == 0 && act == 0, "a cool tick did not reset the charge" + where);
                            break;
                        }
                    case 1:
                        {
                            var res = RM_BlueKernel.Choir(true, now, silencedUntil, min, radius, hold, singers.Count, singers.Select(s => s[0]).ToArray(), singers.Select(s => s[1]).ToArray(),
                                intruders.Count, intruders.Select(s => s[0]).ToArray(), intruders.Select(s => s[1]).ToArray());
                            bool anyNear = intruders.Any(i => singers.Any(s => (double)(i[0] - s[0]) * (i[0] - s[0]) + (double)(i[1] - s[1]) * (i[1] - s[1]) <= radius * radius));
                            int expectUntil = anyNear ? now + hold : silencedUntil;
                            Check(res.SilencedUntil == expectUntil, $"silenced-until {res.SilencedUntil}, spec {expectUntil}" + where);
                            bool enough = singers.Count >= min;
                            Check(res.Silenced == (enough && now < expectUntil) && res.Singing == (enough && !(now < expectUntil)), $"choir state singing={res.Singing} silenced={res.Silenced}" + where);
                            Check(!(res.Singing && res.Silenced), "singing and silenced at once" + where);
                            Check(res.Singers == singers.Count, "singer count" + where);
                            if (res.Singing)
                            {
                                Check(res.CentreX >= singers.Min(s => s[0]) && res.CentreX <= singers.Max(s => s[0]) && res.CentreZ >= singers.Min(s => s[1]) && res.CentreZ <= singers.Max(s => s[1]), "choir centre outside the singers' bounds" + where);
                                ChoirSongs++;
                            }
                            if (res.Silenced) ChoirSilences++;
                            if (anyNear) lastIntruderTick = now;
                            if (lastIntruderTick != int.MinValue && enough && now - lastIntruderTick < hold) Check(!res.Singing, "the choir sang inside the hold after an intruder" + where);
                            silencedUntil = res.SilencedUntil;
                            var off = RM_BlueKernel.Choir(false, now, silencedUntil, min, radius, hold, singers.Count, singers.Select(s => s[0]).ToArray(), singers.Select(s => s[1]).ToArray(), 0, new int[0], new int[0]);
                            Check(!off.Singing && !off.Silenced && off.Singers == 0 && off.SilencedUntil == silencedUntil, "a gated choir did something" + where);
                            break;
                        }
                    case 5:
                        {
                            bool on = a.a % 7 != 0, hash = a.b % 2 == 0, jobExits = a.a % 3 == 0;
                            int act = RM_BlueKernel.DepartAction(on, departTick, now, hash, departing, jobExits);
                            bool due = on && departTick >= 0 && now >= departTick && hash;
                            if (!due) Check(act == 0, "departure acted when not due" + where);
                            else if (departing && !jobExits) Check(act == 1, "a replaced walk-off job was not restarted" + where);
                            else if (departing) Check(act == 0, "restarted a departure already under way" + where);
                            else Check(act == 2, "a due departure did not start" + where);
                            if (act != 0) { departing = true; Departs++; }
                            break;
                        }
                    case 6:
                        {
                            bool call, expose;
                            int ns = RM_BlueKernel.AblationStage(stage, now, silTick, expTick, out call, out expose);
                            Check(ns >= stage && ns <= 2, "stage went backwards or past 2" + where);
                            Check(call == (stage == 0 && now >= silTick), "scavenger call != crossing the silhouette time" + where);
                            Check(expose == (ns == 2 && stage < 2 && now >= expTick), "exposure verdict" + where);
                            if (expose) Check(now >= silTick && now >= expTick, "exposed before the silhouette or its own time" + where);
                            if (call) calls++;
                            if (expose) { exposes++; Exposures++; }
                            Check(calls <= 1 && exposes <= 1, "the call or the exposure fired twice" + where);
                            stage = ns;
                            break;
                        }
                }
                Check(expTick >= silTick, "exposure scheduled before the silhouette" + where);
            }
            return null;
        }

        private static string RulesUnits(int seed)
        {
            var r = new Random(seed ^ 0x2c);
            for (int m = 0; m < 16; m++)
            {
                bool on = (m & 1) != 0, emp = (m & 2) != 0, gate = (m & 4) != 0, heat = (m & 8) != 0;
                Check(RM_BlueKernel.Detonates(on, emp, gate, heat) == (on && (emp || !gate || heat)), "detonation truth");
                if (RM_BlueKernel.Detonates(on, emp, gate, heat)) Detonations++;
            }
            // a kinetic or cold kill leaves it intact; heat or lightning, or an EMP hit, sets it off
            Check(!RM_BlueKernel.Detonates(true, false, true, false) && RM_BlueKernel.Detonates(true, false, true, true) && RM_BlueKernel.Detonates(true, true, true, false) && RM_BlueKernel.Detonates(true, false, false, false) && !RM_BlueKernel.Detonates(false, true, false, true), "ruled detonation cases");
            for (int m = 0; m < 32; m++)
            {
                bool on = (m & 1) != 0, trap = (m & 2) != 0, dead = (m & 4) != 0, dest = (m & 8) != 0, emp = (m & 16) != 0;
                bool g = RM_BlueKernel.EmpTrap(on, trap, dead, dest, emp);
                Check(g == (on && trap && !dead && !dest && emp), "EMP trap truth");
                if (g) EmpKills++;
            }
            for (int m = 0; m < 16; m++)
            {
                bool a = (m & 1) != 0, b = (m & 2) != 0, c = (m & 4) != 0, d = (m & 8) != 0;
                Check(RM_BlueKernel.IsHeatKill(a, b, c, d) == ((a && b) || (c && d)), "heat kill truth");
                Check(RM_BlueKernel.PartKills(a, b, c, d) == (a && b && c && d), "part kill truth");
                Check(RM_BlueKernel.IsEmp(a, b, c) == (a ? b : c), "IsEmp truth");
                Check(RM_BlueKernel.RoadCell(a, b, c, d, (seed & 1) != 0) == (a && !b && (c || d) && !((seed & 1) != 0)), "road cell truth");
            }
            Check(RM_BlueKernel.WeatherCommonality(true, 0.7f) == 0.7f && RM_BlueKernel.WeatherCommonality(false, 0.7f) == 0f, "ruled weathers toggle");
            Check(RM_BlueKernel.CropGrowth(0.5f, 0.08f, false) == 0.08f && RM_BlueKernel.CropGrowth(0.05f, 0.08f, false) == 0.05f && RM_BlueKernel.CropGrowth(0.5f, 0.08f, true) == 0.5f && RM_BlueKernel.CropGrowth(0.08f, 0.08f, false) == 0.08f, "crop to growth");
            // timings
            int now = r.Next(0, 1000000); float days = 2f + (float)r.NextDouble() * 3f; float f = new[] { 0f, 0.1f, 1f, 4f }[r.Next(4)];
            int dt = RM_BlueKernel.DepartTick(now, days, f);
            Check(dt >= now + (int)Math.Round(days * 0.1 * 60000) - 1, "stay shorter than the 0.1 factor floor");
            Check(RM_BlueKernel.RoadRemoveTick(now, days, f) == dt, "road removal and departure clocks disagree on the same inputs");
            // virr
            int n = r.Next(0, 8); var vx = new int[n]; var vz = new int[n];
            for (int i = 0; i < n; i++) { vx[i] = r.Next(-40, 41); vz[i] = r.Next(-40, 41); }
            int ex = r.Next(-30, 31), ez = r.Next(-30, 31); float rad = 30f;
            int got = RM_BlueKernel.NearestVirr(n, vx, vz, ex, ez, rad), best = -1; double bd = rad * rad;
            for (int i = 0; i < n; i++) { double d = (double)(vx[i] - ex) * (vx[i] - ex) + (double)(vz[i] - ez) * (vz[i] - ez); if (d <= bd) { bd = d; best = i; } }
            Check(got == best, $"nearest virr {got}, spec {best}");
            float p0 = RM_BlueKernel.VirrPitch(0.85f, 1.35f, 0f), p1 = RM_BlueKernel.VirrPitch(0.85f, 1.35f, 1f);
            Check(Near(p0, 0.85f, 1e-6) && Near(p1, 1.35f, 1e-6) && RM_BlueKernel.VirrPitch(0.85f, 1.35f, 5f) == p1 && RM_BlueKernel.VirrPitch(0.85f, 1.35f, -1f) == p0, "virr pitch lerp and clamp");
            return null;
        }

        // ════════════════════════ murrek ════════════════════════
        public static long Burrows, Spawned, Plans, Reach;

        // independent spec of "keeps its distance from every taken cell": strictly closer than the spacing is crowding
        private static bool ClearSpec(int x, int z, List<int[]> taken, float spacing)
        {
            foreach (var t in taken) if ((double)(t[0] - x) * (t[0] - x) + (double)(t[1] - z) * (t[1] - z) < (double)spacing * spacing) return false;
            return true;
        }

        private static string MurrekCase(int seed)
        {
            var r = new Random(seed ^ 0x9d);
            int nd = r.Next(0, 60), nm = r.Next(0, 8), nsp = r.Next(0, 20);
            int span = r.Next(5, 60);
            var dx = new int[nd]; var dz = new int[nd];
            for (int i = 0; i < nd; i++) { dx[i] = r.Next(span); dz[i] = r.Next(span); }
            var mx = new int[nm]; var mz = new int[nm]; var el = new bool[nm]; var hb = new bool[nm]; var bx = new int[nm]; var bz = new int[nm];
            for (int i = 0; i < nm; i++) { mx[i] = r.Next(span); mz[i] = r.Next(span); el[i] = r.Next(4) != 0; hb[i] = !el[i] && r.Next(2) == 0; bx[i] = r.Next(span); bz[i] = r.Next(span); }
            var spx = new int[nsp]; var spz = new int[nsp];
            for (int i = 0; i < nsp; i++) { spx[i] = r.Next(span); spz[i] = r.Next(span); }
            float search = new[] { 5f, 20f, 40f }[r.Next(3)], spacing = new[] { 0f, 3f, 6f }[r.Next(3)];
            int rolled = r.Next(0, 4), cap = r.Next(0, 9); bool full = r.Next(5) == 0;
            int reachSeed = r.Next();
            Func<int, int, int, bool> reach = (m, x, z) => new Random(reachSeed ^ (m * 7919 + x * 104729 + z * 1299709)).Next(3) != 0;
            var plan = RM_MurrekKernel.Make(nd, dx, dz, nm, mx, mz, el, hb, bx, bz, search, spacing, rolled, cap, full, nsp, spx, spz, reach);
            Plans++;
            // oracle
            var taken = new List<int[]>();
            for (int i = 0; i < nm; i++) if (hb[i]) taken.Add(new[] { bx[i], bz[i] });
            var burrowed = new List<int[]>();
            for (int m = 0; m < nm; m++)
            {
                if (!el[m]) continue;
                var cand = Enumerable.Range(0, nd).Where(c => (double)(dx[c] - mx[m]) * (dx[c] - mx[m]) + (double)(dz[c] - mz[m]) * (dz[c] - mz[m]) <= (double)search * search && ClearSpec(dx[c], dz[c], taken, spacing))
                    .OrderBy(c => (double)(dx[c] - mx[m]) * (dx[c] - mx[m]) + (double)(dz[c] - mz[m]) * (dz[c] - mz[m])).Take(12).ToList();
                foreach (int c in cand) if (reach(m, dx[c], dz[c])) { taken.Add(new[] { dx[c], dz[c] }); burrowed.Add(new[] { m, dx[c], dz[c] }); break; }
            }
            Check(plan.Burrows.Count == burrowed.Count, $"{plan.Burrows.Count} burrows, oracle {burrowed.Count}");
            for (int i = 0; i < burrowed.Count; i++) Check(plan.Burrows[i].SequenceEqual(burrowed[i]), $"burrow {i}: {string.Join(",", plan.Burrows[i])} vs {string.Join(",", burrowed[i])}");
            Burrows += plan.Burrows.Count;
            // structural invariants
            Check(plan.Burrows.Select(b => b[0]).Distinct().Count() == plan.Burrows.Count, "a murrek took two burrows");
            foreach (var b in plan.Burrows)
            {
                Check(el[b[0]] && !hb[b[0]], "an ineligible or already burrowing murrek was sent");
                Check(Enumerable.Range(0, nd).Any(c => dx[c] == b[1] && dz[c] == b[2]), "burrow not on a drift cell");
                Reach++;
            }
            var all = new List<int[]>();
            for (int i = 0; i < nm; i++) if (hb[i]) all.Add(new[] { bx[i], bz[i] });
            all.AddRange(plan.Burrows.Select(b => new[] { b[1], b[2] }));
            all.AddRange(plan.Spawns);
            for (int i = 0; i < all.Count; i++)
            {
                // the pre-existing burrows may sit closer than the spacing (not ours to move); every cell WE add keeps the spacing from everything taken before it
            }
            var acc = new List<int[]>();
            for (int i = 0; i < nm; i++) if (hb[i]) acc.Add(new[] { bx[i], bz[i] });
            foreach (var cell in plan.Burrows.Select(b => new[] { b[1], b[2] }).Concat(plan.Spawns))
            {
                Check(ClearSpec(cell[0], cell[1], acc, spacing), "a new burrow or spawn crowds one already taken");
                acc.Add(cell);
            }
            int room = cap - nm, expectSpawns = (full || Math.Min(rolled, room) <= 0) ? 0 : Math.Min(rolled, room);
            Check(plan.Spawns.Count <= expectSpawns, $"{plan.Spawns.Count} spawns over the allowance {expectSpawns}");
            if (full || room <= 0 || rolled <= 0) Check(plan.Spawns.Count == 0, "spawned against the cap, the full ecosystem or a zero roll");
            foreach (var s in plan.Spawns) Check(Enumerable.Range(0, nsp).Any(i => spx[i] == s[0] && spz[i] == s[1]), "spawn not on a spawnable cell");
            Spawned += plan.Spawns.Count;
            // liveness: with room, an open ecosystem and an unspaced field, spawns happen up to the allowance
            if (!full && expectSpawns > 0 && spacing == 0f && nsp >= expectSpawns) Check(plan.Spawns.Count == expectSpawns, "a spawn allowance went unused with free cells");
            // the buried murrek's decision table
            for (int m = 0; m < 512; m++)
            {
                bool noProps = (m & 1) != 0, noGrid = (m & 2) != 0, shallow = (m & 4) != 0, old = (m & 8) != 0, hungry = (m & 16) != 0, tired = (m & 32) != 0, prey = (m & 64) != 0;
                int v = RM_MurrekKernel.LieBuried(noProps, noGrid, shallow ? 0.1f : 0.5f, 0.25f, old ? 200000 : 1000, 0, 120000, hungry, tired, prey);
                int spec = noProps ? 1 : (noGrid || shallow) ? 1 : old ? 2 : (hungry || tired) ? 2 : prey ? 3 : 0;
                Check(v == spec, $"buried check {v}, spec {spec}, mask {m}");
            }
            return null;
        }

        // ════════════════════════ runner ════════════════════════
        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("cold", () => Family("cold", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 10, 90, new[] { 60, 12, 12, 6, 4, 2 }, CdNames), RunCold) ?? ColdUnits(s))),
                ("thaw", () => Family("thaw", N(3000), S(1), ThawCase)),
                ("rules", () => Family("rules", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 10, 100, new[] { 15, 20, 20, 8, 12, 10, 10 }, RlNames), RunRules) ?? RulesUnits(s))),
                ("murrek", () => Family("murrek", N(3000), S(1), MurrekCase)),
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
            Console.WriteLine($"reached: cold absorbs {Absorbs}, drips {Drips}, empty racks {Empties}, clarity changes {StageChanges}; thaw rolls {Rolls}, picks {Picks}; rules detonations {Detonations}, emp kills {EmpKills}, charge booms {ChargeBooms}, departs {Departs}, choir songs {ChoirSongs} (silenced {ChoirSilences}), exposures {Exposures}; murrek plans {Plans}, burrows {Burrows}, spawns {Spawned}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                if (Absorbs == 0 || Drips == 0 || Empties == 0 || StageChanges == 0 || Rolls == 0 || Picks == 0 || Detonations == 0 || EmpKills == 0 || ChargeBooms == 0 || Departs == 0 || ChoirSongs == 0 || ChoirSilences == 0 || Exposures == 0 || Burrows == 0 || Spawned == 0)
                { Console.WriteLine("FAIL a fuzz family never reached one of its key transitions (blind)"); ok = false; }
            }
            Console.WriteLine($"bluedesert fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
