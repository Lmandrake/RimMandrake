// Approach B for Warcasket: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_WarcasketKernel.cs):
//   integrity   a worn suit under changing hazards: stacked hazards roll a failure that damages the suit (never destroys it) and loads
//               the wearer's breach hediff, against an independent closed-form ledger
//   immersion   pawns walking in and out of deep water in different gear: the clock gains by drive factor, heals on clear ground, kills
//               at the lethal severity; parallel pawns prove "more protection never hurts"
//   core        a half-extracted core dosing pawns by distance on every fourth rare tick, silent in a shielded bay
//   sarcophagus a dead wearer's corpse: seal at death, strip leaves the sealed suit, crack drops it and spawns the salvage once
//   tables      exhaustive decision tables and the closed-form failure odds
// The hediff model (severity added, removed at <= 0, lethal at >= 1 for both hediffs) restates HealthUtility.AdjustSeverity and
// HediffDef.lethalSeverity as read from the defs; it is the ledger, not the kernel.
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Warcasket.SelfTest
{
    internal static class WarcasketFuzz
    {
        public static long Cases, Steps, Checks, Failures, Deaths, Sealed, Cracked, UnsealedCracks, Doses, ShieldedSkips, Heals, ProtectedGains, StripsBlocked;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

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

        private struct Act
        {
            public int kind, a, b; public bool f;
            public override string ToString() { return "k" + kind + "(" + a + "," + b + (f ? ",T" : "") + ")"; }
        }

        private static List<string> RunFamily(string name, int n, int seed0, Func<Random, int, Act[]> gen, Func<IList<Act>, int, bool, string> run, int minLen, int spread)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed);
                var acts = gen(r, minLen + r.Next(spread)); Cases++;
                if (run(acts, seed, true) == null) continue;
                var small = Shrink(acts.ToList(), t => run(t, seed, false) != null);
                fails.Add($"{name} seed {seed}: {run(small, seed, false)} | {string.Join(" ", small)}");
                if (fails.Count >= 3) break;
            }
            return fails;
        }

        private static Act[] Gen(Random r, int len, int[] weights)
        {
            var a = new Act[len]; int total = weights.Sum();
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(total), kind = 0;
                while (k >= weights[kind]) { k -= weights[kind]; kind++; }
                a[i] = new Act { kind = kind, a = r.Next(1 << 12), b = r.Next(1 << 12), f = r.Next(2) == 0 };
            }
            return a;
        }

        // ════════════════════════ integrity ════════════════════════
        private enum IA { Hazards, Tick, Damage, Repair, Master, Compound, Wear, Props }

        private static readonly float[] Vacuums = { 0f, 0.4f, 0.5f, 0.51f, 1f };
        private static readonly float[] Temps = { 21f, -59.9f, -60f, -80f, 69.9f, 70f, 120f };

        private static string RunIntegrity(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x51ed270b);
            int maxHp = new[] { 320, 1, 100, 400 }[rr.Next(4)];
            int hp = maxHp; float baseC = new[] { 0.015f, 0.5f, 1f, 0f }[rr.Next(4)], perExtra = new[] { 0.02f, 0.5f, 0f }[rr.Next(3)];
            int intDmg = new[] { 12, 0, 1000 }[rr.Next(3)]; float perSev = new[] { 0.08f, 0.5f }[rr.Next(2)];
            float vac = 0f, temp = 21f; bool ground = false, fallout = false, master = true, compound = true, worn = true;
            double sev = 0; bool wearerDead = false; long failures = 0, rolls = 0; int stepNo = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch ((IA)a.kind)
                    {
                        case IA.Hazards: vac = Vacuums[a.a % Vacuums.Length]; temp = Temps[a.b % Temps.Length]; ground = (a.a & 8) != 0; fallout = (a.b & 16) != 0; break;
                        case IA.Damage: hp = Math.Max(1, hp - a.a % (maxHp + 1)); break;
                        case IA.Repair: hp = maxHp; break;
                        case IA.Master: master = a.f; break;
                        case IA.Compound: compound = a.f; break;
                        case IA.Wear: worn = a.f; break;
                        case IA.Props: baseC = new[] { 0.015f, 0.5f, 1f, 0f }[a.a % 4]; perExtra = new[] { 0.02f, 0.5f, 0f }[a.b % 3]; break;
                        case IA.Tick:
                            {
                                int checks = 1 + a.a % 60;
                                for (int c = 0; c < checks; c++)
                                {
                                    float u = (float)rr.NextDouble();
                                    if (!(RM_WarcasketKernel.FailureActive(master, compound))) { Check(!(master && compound), "FailureActive"); continue; }
                                    if (!worn || wearerDead) continue;
                                    bool v = RM_WarcasketKernel.VacuumHazard(vac, 0.5f);
                                    bool t = RM_WarcasketKernel.TemperatureHazard(temp, -60f, 70f);
                                    bool x = RM_WarcasketKernel.ToxinHazard(ground, fallout);
                                    int h = RM_WarcasketKernel.HazardCount(v, t, x);
                                    int specH = (vac > 0.5f ? 1 : 0) + (temp <= -60f || temp >= 70f ? 1 : 0) + ((ground || fallout) ? 1 : 0);
                                    Check(h == specH, $"hazard count {h} spec {specH} (vac {vac} temp {temp} ground {ground} fallout {fallout})");
                                    Checks++;
                                    if (!RM_WarcasketKernel.CanFail(h)) { Check(h < 2, "CanFail below two"); continue; }
                                    rolls++;
                                    float chance = RM_WarcasketKernel.FailureChance(h, baseC, perExtra, hp, maxHp);
                                    double frac = Math.Min(1.0, Math.Max(0.0, (double)hp / maxHp));
                                    double spec = Math.Min(1.0, Math.Max(0.0, (baseC + perExtra * (h - 2)) * (1.6 - 0.6 * frac)));
                                    Check(chance >= 0f && chance <= 1f, "chance outside 0..1: " + chance);
                                    Check(Math.Abs(chance - spec) < 1e-5, $"chance {chance} spec {spec} (h {h} hp {hp}/{maxHp})");
                                    // pristine two-hazard suit fails at exactly the base; wrecked fails 1.6x as often (before the clamp)
                                    if (h == 2 && hp == maxHp) Check(Math.Abs(chance - Math.Min(1f, baseC)) < 1e-6, "pristine two-hazard chance is not the base");
                                    Check(chance + 1e-6f >= RM_WarcasketKernel.FailureChance(h, baseC, perExtra, maxHp, maxHp), "a damaged suit fails less often than a pristine one");
                                    Check(RM_WarcasketKernel.FailureChance(Math.Min(3, h + 1), baseC, perExtra, hp, maxHp) + 1e-6f >= chance, "more hazards failed less often");
                                    if (!RM_WarcasketKernel.Chance(chance, u)) continue;
                                    int extra = rr.Next(0, RM_WarcasketKernel.FailureDamageMax(h) + 1);
                                    int before = hp;
                                    hp = RM_WarcasketKernel.HitPointsAfterFailure(hp, intDmg, extra);
                                    Check(hp >= 1, "a failure destroyed the suit (hp " + hp + ")");
                                    Check(hp <= before || before < 1, "a failure repaired the suit");
                                    Check(hp == Math.Max(1, before - (intDmg + extra)), $"hp after failure {hp} spec {Math.Max(1, before - (intDmg + extra))}");
                                    Check(before - hp <= intDmg + 4 * h && (before - hp == intDmg + extra || hp == 1), "damage outside [base, base + 4 x hazards]");
                                    sev += RM_WarcasketKernel.BreachSeverity(perSev, h);
                                    Check(Math.Abs(RM_WarcasketKernel.BreachSeverity(perSev, h) - perSev * h) < 1e-6, "breach severity");
                                    failures++; Failures++;
                                    if (sev >= 1.0) { wearerDead = true; Deaths++; }
                                }
                                break;
                            }
                    }
                    Check(hp >= 1 && hp <= maxHp, "suit hp left 1.." + maxHp + ": " + hp);
                }
                return null;
            }
            catch (Exception e) { return "step " + stepNo + ": " + e.Message; }
        }

        // ════════════════════════ immersion ════════════════════════
        private enum MA { Move, Equip, Tick, Master, Toggle }
        private static readonly float[] Protections = { 0f, 0.3f, 0.9f, 1f, 1.8f };

        private sealed class Swimmer { public double prot; public bool in_water; public double sev; public bool has, dead; }

        private static string RunImmersion(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x2c1b3c6d);
            // three pawns: A (least protected), B (more), C (naked). Pawns share one path through the terrain unless the action moves one.
            // naked, A and B with B always at least as protected as A: severity must order naked >= A >= B whatever the path
            var ps = new[] { new Swimmer { prot = 0 }, new Swimmer { prot = 0.3 }, new Swimmer { prot = 0.9 } };
            bool master = true, immersion = true; int countdown = 250; long mapTicks = 0, checksRun = 0; int stepNo = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch ((MA)a.kind)
                    {
                        case MA.Move: { foreach (var p in ps) p.in_water = a.f; break; }
                        case MA.Equip: ps[1].prot = Protections[a.b % Protections.Length]; ps[2].prot = Math.Max(ps[2].prot, ps[1].prot); break;
                        case MA.Master: master = a.f; break;
                        case MA.Toggle: immersion = a.f; break;
                        case MA.Tick:
                            {
                                int ticks = 1 + a.a % 1400;
                                for (int t = 0; t < ticks; t++)
                                {
                                    mapTicks++;
                                    if (!RM_WarcasketKernel.ImmersionActive(master, immersion)) continue;
                                    if (!RM_WarcasketKernel.CheckDue(ref countdown)) continue;
                                    checksRun++;
                                    foreach (var p in ps)
                                    {
                                        if (p.dead) continue;
                                        bool hazardous = RM_WarcasketKernel.HazardousCell(true, true, p.in_water, true, false);
                                        Check(hazardous == p.in_water, "HazardousCell(deep water)");
                                        float drive = hazardous ? Math.Max(RM_WarcasketKernel.MinDriveFactor, 1f - Math.Min(1f, Math.Max(0f, (float)p.prot))) : 1f;
                                        float delta = RM_WarcasketKernel.ImmersionDelta(hazardous, p.has, drive);
                                        if (delta == 0f) { Check(!hazardous ? !p.has : false, "no delta while hazardous with a drive factor above zero"); continue; }
                                        // AdjustSeverity: a positive offset creates the hediff, otherwise it moves the existing one; at <= 0 it goes
                                        if (delta > 0f) { Check(hazardous, "gain on clear ground"); p.has = true; p.sev += delta; ProtectedGains += p.prot >= 0.9 ? 1 : 0; }
                                        else { Check(p.has, "healed a hediff that is not there"); p.sev += delta; Heals++; if (p.sev <= 1e-9) { p.sev = 0; p.has = false; } }
                                        if (p.sev >= 1.0) { p.dead = true; Deaths++; }
                                    }
                                    // more protection never hurts: naked >= A >= B in severity whenever the more exposed one is alive
                                    for (int i = 0; i + 1 < ps.Length; i++)
                                    {
                                        if (ps[i].dead) continue;
                                        Check(!ps[i + 1].dead, "a better-protected pawn died while a less protected one lives");
                                        Check(ps[i + 1].sev <= ps[i].sev + 1e-9, $"protection {ps[i + 1].prot} reads {ps[i + 1].sev} above protection {ps[i].prot} reading {ps[i].sev}");
                                    }
                                }
                                break;
                            }
                    }
                    foreach (var p in ps) { Check(p.sev >= 0, "negative severity"); Check(!p.has || p.sev > 0, "hediff present at zero"); Check(p.has || p.sev == 0, "severity without a hediff"); }
                }
                Check(checksRun <= mapTicks / 250 + 1, "more immersion checks than one per 250 ticks");
                return null;
            }
            catch (Exception e) { return "step " + stepNo + ": " + e.Message; }
        }

        // ════════════════════════ core ════════════════════════
        private enum CA { Pawn, Move, Bay, Rare, Settings, Reload }

        private static string RunCore(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x6c8e9cf5);
            float radius = new[] { 4f, 1f, 8f, 0f }[rr.Next(4)], factor = new[] { 1f, 0.5f, 2f }[rr.Next(3)];
            int checkInterval = new[] { 150, 60, 250, 1000 }[rr.Next(4)];
            var dists = new List<float>(); bool bay = false, master = true, coreDose = true, shield = true, spawned = true;
            int rareCount = 0; long rares = 0, doseEvents = 0; var total = new List<double>(); int stepNo = 0;
            try
            {
                float rateScale = RM_WarcasketKernel.RateScale(250, checkInterval);
                Check(Math.Abs(rateScale - 250f * 4f / checkInterval) < 1e-4, "RateScale");
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch ((CA)a.kind)
                    {
                        case CA.Pawn: dists.Add((a.a % 120) / 10f); total.Add(0); break;
                        case CA.Move: if (dists.Count > 0) dists[a.a % dists.Count] = (a.b % 120) / 10f; break;
                        case CA.Bay: bay = a.f; break;
                        case CA.Settings: master = (a.a & 1) == 0; coreDose = (a.a & 2) == 0; shield = (a.b & 1) == 0; spawned = (a.b & 2) == 0; break;
                        case CA.Reload: break;   // rareCount is Scribed: a save round trip keeps it
                        case CA.Rare:
                            {
                                int n = 1 + a.a % 24;
                                for (int r = 0; r < n; r++)
                                {
                                    rares++;
                                    bool due = RM_WarcasketKernel.DoseDue(ref rareCount);
                                    Check(due == (rares % 4 == 0), $"dose cadence: rare tick {rares} due={due}");
                                    Check(rareCount >= 0 && rareCount < 4, "rareCount out of 0..3: " + rareCount);
                                    if (!due) continue;
                                    if (!RM_WarcasketKernel.DoseActive(master, coreDose)) continue;
                                    bool shieldedNow = RM_WarcasketKernel.IsShielded(master && shield, true, true, spawned, bay);
                                    if (shieldedNow) { ShieldedSkips++; Check(master && shield && spawned && bay, "shielded without a bay"); continue; }
                                    doseEvents++;
                                    for (int i = 0; i < dists.Count; i++)
                                    {
                                        float d = dists[i];
                                        if (!RM_WarcasketKernel.InRadius(d, radius)) { Check(d > radius, "InRadius"); continue; }
                                        float fall = RM_WarcasketKernel.Falloff(d, radius);
                                        float dose = RM_WarcasketKernel.Dose(factor, fall, rateScale);
                                        Check(fall > 0f && fall <= 1f, $"falloff {fall} at {d}/{radius}");
                                        Check(dose > 0f, "no dose inside the radius");
                                        Check(Math.Abs(dose - factor * (1.0 - d / (radius + 1.0)) * 250.0 * 4.0 / checkInterval) < 1e-3, "dose formula");
                                        // nearer never doses less
                                        Check(RM_WarcasketKernel.Falloff(Math.Max(0f, d - 0.5f), radius) >= fall, "falloff not decreasing with distance");
                                        total[i] += dose; Doses++;
                                    }
                                }
                                break;
                            }
                    }
                }
                return null;
            }
            catch (Exception e) { return "step " + stepNo + ": " + e.Message; }
        }

        // ════════════════════════ sarcophagus ════════════════════════
        private enum SA { Die, Strip, Crack, Master, Sarc, Salvage, Revive }

        private sealed class Gear { public string name; public bool sarc, locked, worn = true; }

        private static string RunSarcophagus(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x1f83d9ab);
            var gear = new List<Gear> { new Gear { name = "junker", sarc = true }, new Gear { name = "plate" }, new Gear { name = "helmet" } };
            if (rr.Next(2) == 0) gear.Add(new Gear { name = "junker2", sarc = true });
            bool master = true, sarcOn = true, dead = false; int stepNo = 0;
            var ground = new List<string>(); var stackLimits = new[] { 1, 75, 100, 0, -3, 2 };
            // salvage rows: (count, stackLimit, def known)
            var rows = new List<(int count, int limit, bool known)> { (2, 75, true), (25, 75, true), (1, 1, true) };
            long placedTotal = 0, wantedTotal = 0; var cracked = new HashSet<Gear>();
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch ((SA)a.kind)
                    {
                        case SA.Master: master = a.f; break;
                        case SA.Sarc: sarcOn = a.f; break;
                        case SA.Salvage: rows.Add((a.a % 130 - 3, stackLimits[a.b % stackLimits.Length], (a.b & 64) == 0)); if (rows.Count > 6) rows.RemoveAt(0); break;
                        case SA.Revive: break;
                        case SA.Die:
                            if (dead) break;
                            dead = true; Deaths++;
                            foreach (Gear g in gear.Where(x => x.worn))
                            {
                                bool seal = RM_WarcasketKernel.SealsOnDeath(master, sarcOn, g.sarc);
                                Check(seal == (master && sarcOn && g.sarc), "SealsOnDeath");
                                if (seal) { g.locked = true; Sealed++; }
                            }
                            break;
                        case SA.Strip:
                            if (!dead) break;
                            foreach (Gear g in gear.Where(x => x.worn).ToList())
                            {
                                if (g.locked) { StripsBlocked++; continue; }
                                g.worn = false; ground.Add(g.name);
                            }
                            Check(gear.Where(x => x.worn).All(x => x.locked), "stripping left an unlocked item on the corpse");
                            break;
                        case SA.Crack:
                            {
                                Gear suit = gear.FirstOrDefault(x => x.worn && x.sarc);
                                bool offers = RM_WarcasketKernel.OffersCrack(master, sarcOn, dead, suit != null);
                                Check(offers == (master && sarcOn && dead && suit != null), "OffersCrack");
                                if (!offers) { Check(!(dead && suit != null && master && sarcOn), "cracking refused though sealed and enabled"); break; }
                                // the job: it only runs while a sarcophagus suit is worn; unlock, drop, spawn the salvage once
                                if (!suit.locked) UnsealedCracks++;
                                suit.locked = false; suit.worn = false; ground.Add(suit.name); Cracked++;
                                Check(cracked.Add(suit), "cracked the same suit twice");
                                foreach (var row in rows)
                                {
                                    if (!RM_WarcasketKernel.SalvageRowWanted(row.known, row.count)) { Check(!(row.known && row.count > 0), "wanted row skipped"); continue; }
                                    int left = row.count, guard = 0; wantedTotal += row.count;
                                    while (left > 0)
                                    {
                                        if (++guard > 100000) throw new Exception($"salvage loop did not terminate (count {row.count}, limit {row.limit})");
                                        int s = RM_WarcasketKernel.NextSalvageStack(left, row.limit);
                                        Check(s >= 1 && s <= left, $"stack {s} of {left}");
                                        Check(s <= Math.Max(1, row.limit), $"stack {s} over limit {row.limit}");
                                        left -= s; placedTotal += s;
                                    }
                                }
                                Check(placedTotal == wantedTotal, $"salvage placed {placedTotal} of {wantedTotal}");
                                break;
                            }
                    }
                    // standing properties
                    foreach (Gear g in gear)
                    {
                        if (g.locked) Check(g.worn && g.sarc && dead, "a locked item is off the corpse, not a sarcophagus suit, or on the living");
                        if (!dead) Check(g.worn && !g.locked, "living wearer lost or locked gear");
                    }
                    Check(ground.Count == ground.Distinct().Count(), "an item was dropped twice");
                    // nothing stranded: with both switches on, every sealed suit still on the corpse can be cracked
                    if (dead && master && sarcOn)
                        foreach (Gear g in gear.Where(x => x.worn && x.locked))
                            Check(RM_WarcasketKernel.OffersCrack(master, sarcOn, true, true), "a sealed suit cannot be cracked");
                }
                return null;
            }
            catch (Exception e) { return "step " + stepNo + ": " + e.Message; }
        }

        // ════════════════════════ tables ════════════════════════
        private static List<string> Tables(int n, int seed0)
        {
            var fails = new List<string>();
            Action<string, Action> run = (name, act) => { Cases++; try { act(); } catch (Exception e) { fails.Add("tables " + name + ": " + e.Message); } };
            Func<int, bool[]> bits = (k) => Enumerable.Range(0, 5).Select(b => (k >> b & 1) != 0).ToArray();

            run("gates", () =>
            {
                for (int k = 0; k < 32; k++)
                {
                    Steps++;
                    var f = bits(k);
                    Check(RM_WarcasketKernel.FailureActive(f[0], f[1]) == (f[0] && f[1]), "FailureActive");
                    Check(RM_WarcasketKernel.ImmersionActive(f[0], f[1]) == (f[0] && f[1]), "ImmersionActive");
                    Check(RM_WarcasketKernel.DoseActive(f[0], f[1]) == (f[0] && f[1]), "DoseActive");
                    Check(RM_WarcasketKernel.ShieldingActive(f[0], f[1]) == (f[0] && f[1]), "ShieldingActive");
                    Check(RM_WarcasketKernel.SealsOnDeath(f[0], f[1], f[2]) == (f[0] && f[1] && f[2]), "SealsOnDeath");
                    Check(RM_WarcasketKernel.ExtensionApplies(f[0], f[1]) == (f[0] && f[1]), "ExtensionApplies");
                    Check(RM_WarcasketKernel.ToxinHazard(f[0], f[1]) == (f[0] || f[1]), "ToxinHazard");
                    Check(RM_WarcasketKernel.HoldsClock(f[0], f[1], f[2]) == (f[0] && f[1] && f[2]), "HoldsClock");
                    Check(RM_WarcasketKernel.HazardCount(f[0], f[1], f[2]) == (f[0] ? 1 : 0) + (f[1] ? 1 : 0) + (f[2] ? 1 : 0), "HazardCount");
                    Check(RM_WarcasketKernel.HazardousCell(f[0], f[1], f[2], f[3], f[4]) == (f[0] && f[1] && f[2] && (!f[3] || !f[4])), "HazardousCell " + k);
                    for (int m = 0; m < 2; m++)
                        Check(RM_WarcasketKernel.OffersCrack(f[0], f[1], f[2], f[3]) == (f[0] && f[1] && f[2] && f[3]), "OffersCrack");
                    Check(RM_WarcasketKernel.IsShielded(f[0], f[1], f[2], f[3], f[4]) == (f[0] && f[1] && f[2] && f[3] && f[4]), "IsShielded " + k);
                    Check(RM_WarcasketKernel.SalvageRowWanted(f[0], f[1] ? 1 : 0) == (f[0] && f[1]) && !RM_WarcasketKernel.SalvageRowWanted(true, 0) && !RM_WarcasketKernel.SalvageRowWanted(true, -1), "SalvageRowWanted");
                }
                Check(RM_WarcasketKernel.Chance(1f, 1f) && RM_WarcasketKernel.Chance(2f, 0f) && !RM_WarcasketKernel.Chance(0f, 0f) && !RM_WarcasketKernel.Chance(0.5f, 0.5f) && RM_WarcasketKernel.Chance(0.5f, 0.4999f), "Chance edges (Random.value reaches 1.0)");
                Check(RM_WarcasketKernel.CrackTicks(false, 77) == 1200 && RM_WarcasketKernel.CrackTicks(true, 77) == 77, "CrackTicks");
                Check(RM_WarcasketKernel.TemperatureHazard(-60f, -60f, 70f) && RM_WarcasketKernel.TemperatureHazard(70f, -60f, 70f) && !RM_WarcasketKernel.TemperatureHazard(-59.99f, -60f, 70f) && !RM_WarcasketKernel.TemperatureHazard(69.99f, -60f, 70f), "temperature edges");
                Check(!RM_WarcasketKernel.VacuumHazard(0.5f, 0.5f) && RM_WarcasketKernel.VacuumHazard(0.5001f, 0.5f), "vacuum edge is exclusive");
                Check(RM_WarcasketKernel.InRadius(4f, 4f) && !RM_WarcasketKernel.InRadius(4.01f, 4f), "radius edge is inclusive");
                Check(RM_WarcasketKernel.NextSalvageStack(10, 0) == 1 && RM_WarcasketKernel.NextSalvageStack(10, -5) == 1 && RM_WarcasketKernel.NextSalvageStack(10, 75) == 10 && RM_WarcasketKernel.NextSalvageStack(100, 75) == 75, "NextSalvageStack");
            });

            run("immersion-delta", () =>
            {
                foreach (bool haz in new[] { false, true }) foreach (bool has in new[] { false, true })
                        foreach (float d in new[] { -1f, 0f, 0.05f, 0.1f, 0.5f, 1f })
                        {
                            Steps++;
                            float got = RM_WarcasketKernel.ImmersionDelta(haz, has, d);
                            float spec = !haz ? (has ? -0.35f : 0f) : d <= 0f ? (has ? -0.1f : 0f) : 0.12f * d;
                            Check(Math.Abs(got - spec) < 1e-6, $"ImmersionDelta({haz},{has},{d}) = {got}, spec {spec}");
                            if (!haz) Check(got <= 0f, "gain on clear ground");
                            if (haz && d > 0f) Check(got > 0f, "no gain while exposed");
                        }
                // time to lethal in deep water, continuous: protection p -> checks of 250 ticks until severity reaches 1
                foreach (float p in new[] { 0f, 0.3f, 0.9f, 1f })
                {
                    float drive = Math.Max(RM_WarcasketKernel.MinDriveFactor, 1f - p);
                    int checks = 0; double sev = 0;
                    while (sev < 1.0 && checks < 100000) { sev += RM_WarcasketKernel.ImmersionDelta(true, checks > 0, drive); checks++; }
                    Check(Math.Abs(checks - Math.Ceiling(1.0 / (0.12 * drive))) <= 1, $"time to lethal at protection {p}: {checks} checks");
                    Check(checks < 100000, "protection " + p + " never kills: the clock would never run out");
                    Check(drive >= 0.05f, "drive below the floor");
                }
                // clear ground heals any severity below 1 in at most ceil(sev / 0.35) checks
                for (double s0 = 0.01; s0 < 1.0; s0 += 0.01)
                {
                    int checks = 0; double sev = s0;
                    while (sev > 1e-9 && checks < 100) { sev += RM_WarcasketKernel.ImmersionDelta(false, true, 1f); checks++; }
                    Check(sev <= 1e-9 && checks <= 3, $"severity {s0:F2} took {checks} checks to heal");
                }
            });

            run("cadence", () =>
            {
                for (int i = 0; i < 4; i++)
                {
                    int cd = 250; int fired = 0;
                    for (int t = 0; t < 250 * 6 + 3; t++) { Steps++; if (RM_WarcasketKernel.CheckDue(ref cd)) fired++; }
                    Check(fired == 6, $"immersion check fired {fired} times in 1503 ticks");
                }
                int rc = 0, due = 0;
                for (int t = 0; t < 400; t++) if (RM_WarcasketKernel.DoseDue(ref rc)) due++;
                Check(due == 100, $"core doses {due} times in 400 rare ticks");
                // the dose rate per game tick equals vanilla's per-interval figure whatever the cadence
                foreach (int ci in new[] { 60, 150, 250, 600 })
                {
                    double perTick = RM_WarcasketKernel.Dose(1f, 1f, RM_WarcasketKernel.RateScale(250, ci)) / (250.0 * RM_WarcasketKernel.RaresPerDose);
                    Check(Math.Abs(perTick - 1.0 / ci) < 1e-6, $"core dose rate per tick {perTick} vs 1/{ci}");
                }
                Check(Math.Abs(RM_WarcasketKernel.Falloff(4f, 4f) - 0.2f) < 1e-6 && RM_WarcasketKernel.Falloff(5f, 4f) == 0f && RM_WarcasketKernel.Falloff(0f, 4f) == 1f, "falloff ends");
            });

            run("failure-odds", () =>
            {
                // the closed form against a sample: shipped defaults, every hazard count and suit condition
                var r = new Random(seed0 + 3);
                foreach (int hz in new[] { 2, 3 }) foreach (int hp in new[] { 320, 160, 1 })
                    {
                        float p = RM_WarcasketKernel.FailureChance(hz, 0.015f, 0.02f, hp, 320);
                        double want = (0.015 + 0.02 * (hz - 2)) * (1.6 - 0.6 * (hp / 320.0));
                        Check(Math.Abs(p - want) < 1e-6, $"shipped chance at {hz} hazards hp {hp}: {p} vs {want}");
                        int N = 400000, hits = 0;
                        for (int i = 0; i < N; i++) if (RM_WarcasketKernel.Chance(p, (float)r.NextDouble())) hits++;
                        double sd = Math.Sqrt(N * want * (1 - want));
                        Check(Math.Abs(hits - N * want) < 5 * sd, $"sampled failures {hits} vs {N * want:F0} +- {5 * sd:F0}");
                        Steps += N;
                    }
                // expected checks to the first failure: a pristine suit under two hazards fails about once in 67 checks (~4.6 h at 250 ticks)
                Check(Math.Abs(1.0 / RM_WarcasketKernel.FailureChance(2, 0.015f, 0.02f, 320, 320) - 66.67) < 0.1, "mean checks to first failure");
                // a lone hazard never fails the suit, at any damage
                foreach (int hp in new[] { 1, 100, 320 }) for (int h = 0; h < 2; h++) Check(!RM_WarcasketKernel.CanFail(h), "lone hazard fails");
                Check(RM_WarcasketKernel.FailureChance(2, 5f, 5f, 1, 320) == 1f && RM_WarcasketKernel.FailureChance(2, -1f, 0f, 320, 320) == 0f, "chance clamps");
                { float c0 = RM_WarcasketKernel.FailureChance(2, 0.1f, 0f, 0, 0); Check(c0 >= 0.1f && c0 <= 0.16f + 1e-6f, "a suit with no max hit points gave chance " + c0); }
                Check(RM_WarcasketKernel.FailureChance(2, 0.1f, 0f, 5, 0) > 0f && RM_WarcasketKernel.FailureChance(2, 0.1f, 0f, -50, 320) <= 0.16f + 1e-6f, "unusual hp");
            });

            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("integrity", () => RunFamily("integrity", N(5000), S(1), (r, len) => Gen(r, len, new[] { 14, 50, 8, 6, 4, 4, 6, 4 }), RunIntegrity, 30, 170)),
                ("immersion", () => RunFamily("immersion", N(4000), S(1), (r, len) => Gen(r, len, new[] { 20, 8, 55, 5, 5 }), RunImmersion, 20, 120)),
                ("core", () => RunFamily("core", N(4000), S(1), (r, len) => Gen(r, len, new[] { 14, 10, 8, 50, 8, 4 }), RunCore, 20, 120)),
                ("sarcophagus", () => RunFamily("sarcophagus", N(4000), S(1), (r, len) => Gen(r, len, new[] { 12, 14, 24, 8, 8, 16, 2 }), RunSarcophagus, 8, 60)),
                ("tables", () => Tables(Math.Max(1, N(10)), S(1))),
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
            Console.WriteLine($"reached: hazard checks {Checks}, suit failures {Failures}, deaths {Deaths}, protected gains {ProtectedGains}, heals {Heals}, core doses {Doses}, shielded skips {ShieldedSkips}, sealed {Sealed}, cracked {Cracked} ({UnsealedCracks} never sealed), strips blocked {StripsBlocked}");
            if (only == null && !oneSeed.HasValue && scale >= 1 && (Failures == 0 || Deaths == 0 || ProtectedGains == 0 || Heals == 0 || Doses == 0 || ShieldedSkips == 0 || Sealed == 0 || Cracked == 0 || StripsBlocked == 0))
            { Console.WriteLine("FAIL warcasket fuzz never reached a path (blind)"); ok = false; }
            Console.WriteLine($"warcasket fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
