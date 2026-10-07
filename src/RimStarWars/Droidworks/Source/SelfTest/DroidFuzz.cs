// Approach B for Droidworks: seeded random ACTION SEQUENCES over the Verse-free kernel the mod calls (DroidworksKernel.cs):
//   drift  - format-tier recipes + wipes + the unwiped-time idiosyncrasy ladder (CompDWServiceRecord.TryDrift)
//   power  - Need_Power drain / charger refill / bolt resentment / detonation arithmetic
//   spike  - data-spike resistance (CompDWDataSpike.TryReprogram)
//   trade  - protocol-droid price shift (Patch_ProtocolTradeAdvantage)
//   units  - tables, boundaries, exhaustive truth tables
// The model (reference sets, double-precision oracles) is this file's own; every number under test comes from the production
// kernel. A failing sequence is shrunk by delta debugging and printed as `family seed N: message | actions`, so it replays.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;

namespace RimMandrake.StarWars.Droidworks.SelfTest
{
    internal static class DroidFuzz
    {
        public static long Cases, Steps;

        internal struct Act
        {
            public int kind, a, b, c;
            public string Name;
            public override string ToString() { return Name + "(" + a + "," + b + "," + c + ")"; }
        }

        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static string F(double v) { return v.ToString("R", CultureInfo.InvariantCulture); }

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

        private static List<string> RunFamily<W>(string name, int n, int baseSeed, int mult, string[] names, int[] kindWeights, int maxLen,
            Func<int, W> make, Action<W, Act> step, int aMax, int bMax, int cMax)
        {
            var fails = new List<string>();
            int total = kindWeights.Sum();
            Func<int, List<Act>, string> run = (seed, acts) =>
            {
                try { var w = make(seed); foreach (var a in acts) { step(w, a); Steps++; } return null; }
                catch (Exception ex) { return ex.Message; }
            };
            for (int k = 0; k < n; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * mult + 3);
                int len = r.Next(5, maxLen);
                var acts = new List<Act>(len);
                for (int i = 0; i < len; i++)
                {
                    int pick = r.Next(total), kind = 0;
                    while (pick >= kindWeights[kind]) { pick -= kindWeights[kind]; kind++; }
                    acts.Add(new Act { kind = kind, Name = names[kind], a = r.Next(aMax), b = r.Next(bMax), c = r.Next(cMax) });
                }
                Cases++;
                if (run(seed, acts) == null) continue;
                var min = Shrink(acts, t => run(seed, t) != null);
                fails.Add(name + " seed " + seed + ": " + run(seed, min) + " | " + string.Join(" ", min));
                if (fails.Count >= 5) break;
            }
            return fails;
        }

        // ===================================================================== drift

        private const int TicksPerYear = 3600000;
        private static readonly int[] Dts = { 0, 0, 1, 60000, 600000, 2500000, 5399999, 5400000, 7199999, 7200000, 7200001, 12600000, 36000000 };
        private static readonly float[] Scales = { 0.25f, 0.5f, 1f, 1f, 2f, 3f };
        private static readonly float[] DefaultWeights = { 0f, 0f, 1f, 1f, 2f, 4f, -1f, 0.5f };
        private static readonly string[] Recipes = { "Standard", "Restrictive", "Deformat" };

        private sealed class PoolTrait
        {
            public float def;
            public List<DroidChassis> chassis = new List<DroidChassis>();
            public List<float> weight = new List<float>();
        }

        private sealed class DriftWorld
        {
            public PoolTrait[] pool;
            public DroidChassis chassis;
            public DroidFormatTier tier = DroidFormatTier.Programmable;
            public List<int> held = new List<int>();
            public int now, lastReset, first, interval, maxAcc;
            public float scale;
            public bool enabled, promote;
            public int oracleReset;               // independent bookkeeping of the same clock
            public long gains;
        }

        private static DriftWorld MakeDrift(int seed)
        {
            var r = new Random(seed * 31 + 7);
            var w = new DriftWorld();
            w.pool = new PoolTrait[8];
            for (int i = 0; i < 8; i++)
            {
                var p = new PoolTrait { def = DefaultWeights[r.Next(DefaultWeights.Length)] };
                int ov = r.Next(4);
                for (int j = 0; j < ov; j++) { p.chassis.Add((DroidChassis)r.Next(8)); p.weight.Add(DefaultWeights[r.Next(DefaultWeights.Length)] * 2f); }
                w.pool[i] = p;
            }
            w.chassis = (DroidChassis)r.Next(8);
            int[] firsts = { 2 * TicksPerYear, TicksPerYear, 100, 60000 };
            int[] intervals = { TicksPerYear * 3 / 2, 1000, 60000 };
            int[] maxes = { 0, 1, 3, 3, 3, 8 };
            w.first = firsts[r.Next(firsts.Length)];
            w.interval = intervals[r.Next(intervals.Length)];
            w.maxAcc = maxes[r.Next(maxes.Length)];
            w.scale = Scales[r.Next(Scales.Length)];
            w.enabled = r.Next(5) != 0;
            w.promote = r.Next(5) != 0;
            w.tier = (DroidFormatTier)(r.Next(4) == 0 ? r.Next(4) : 2);
            w.now = 1000 + r.Next(100000);
            w.lastReset = r.Next(5) == 0 ? -1 : w.now;      // a never-set clock (fresh spawn path)
            w.oracleReset = w.lastReset;
            return w;
        }

        private static float PoolWeight(DriftWorld w, int i)
        {
            return DroidworksKernel.ClampWeight(DroidworksKernel.ChassisWeight(w.pool[i].def, w.pool[i].chassis, w.pool[i].weight, w.chassis));
        }

        private static void ResetClock(DriftWorld w) { w.lastReset = w.now; w.oracleReset = w.now; }

        private static void DriftStep(DriftWorld w, Act a)
        {
            var tierBefore = w.tier;
            var heldBefore = new List<int>(w.held);
            switch (a.kind)
            {
                case 0: // the daily CompTick check, then TryDrift - the SAME call sequence the comp makes
                {
                    float roll = a.a / 1000f;
                    if (w.lastReset < 0) { ResetClock(w); break; }     // CompTick: an unset clock starts, nothing else this tick
                    // ---- production TryDrift
                    int gained = -1;
                    if (w.enabled)
                    {
                        int accreted = w.held.Count;
                        long due = DroidworksKernel.DriftDue(w.first, w.interval, accreted, w.scale);
                        var verdict = DroidworksKernel.DriftCheck(true, w.tier, accreted, w.maxAcc, DroidworksKernel.TicksSince(w.now, w.lastReset), due);
                        if (verdict == DriftVerdict.Due)
                        {
                            var cand = new List<int>();
                            for (int i = 0; i < w.pool.Length; i++) if (!w.held.Contains(i)) cand.Add(i);
                            var weights = new List<float>();
                            foreach (int i in cand) weights.Add(PoolWeight(w, i));
                            int pick = DroidworksKernel.WeightedPick(weights, roll);
                            if (pick >= 0)
                            {
                                gained = cand[pick];
                                Check(weights[pick] > 0f, "drew trait " + gained + " at weight " + weights[pick]);
                                w.held.Add(gained);
                                if (DroidworksKernel.PromotesToSapient(accreted, w.promote, w.tier)) w.tier = DroidFormatTier.Sapient;
                            }
                        }
                    }
                    // ---- independent oracle
                    long elapsed = w.oracleReset < 0 ? 0 : Math.Max(0L, (long)w.now - w.oracleReset);
                    decimal dueD = ((decimal)w.first + (decimal)heldBefore.Count * w.interval) * (decimal)w.scale;
                    long expDue = (long)Math.Floor(dueD);
                    bool poolHas = Enumerable.Range(0, w.pool.Length).Any(i => !heldBefore.Contains(i) && PoolWeight(w, i) > 0f);
                    bool expect = w.enabled && tierBefore >= DroidFormatTier.Programmable && heldBefore.Count < w.maxAcc && elapsed >= expDue && poolHas;
                    Check((gained >= 0) == expect,
                        "drift " + (gained >= 0 ? "fired" : "did not fire") + " but elapsed " + elapsed + " vs due " + expDue + " (accreted " + heldBefore.Count + "/" + w.maxAcc +
                        ", tier " + tierBefore + ", enabled " + w.enabled + ", pool has a positive weight " + poolHas + ") says it should" + (expect ? "" : " not"));
                    if (gained >= 0)
                    {
                        w.gains++;
                        bool promoted = heldBefore.Count == 0 && w.promote && tierBefore == DroidFormatTier.Programmable;
                        Check(w.tier == (promoted ? DroidFormatTier.Sapient : tierBefore),
                            "tier went " + tierBefore + " -> " + w.tier + " on drift #" + (heldBefore.Count + 1) + " (promote " + w.promote + ")");
                        Check(w.held.Count == heldBefore.Count + 1, "a single check gained more than one idiosyncrasy");
                    }
                    else
                    {
                        Check(w.held.SequenceEqual(heldBefore) && w.tier == tierBefore, "a check that did not fire changed the droid");
                    }
                    break;
                }
                case 1: // time passes
                {
                    int dt = Dts[a.a % Dts.Length];
                    if ((long)w.now + dt < 2000000000L) w.now += dt;
                    break;
                }
                case 2: // a memory wipe: Recipe_DWMemoryWipe -> NotifyWiped
                    w.held.Clear();
                    ResetClock(w);
                    Check(DroidworksKernel.TicksSince(w.now, w.lastReset) == 0, "the clock did not read zero straight after a wipe");
                    break;
                case 3: // a format recipe
                {
                    string recipe = Recipes[a.a % 3];
                    DroidFormatTier target = recipe == "Standard" ? DroidFormatTier.Programmable : recipe == "Restrictive" ? DroidFormatTier.Mindless : DroidFormatTier.Blank;
                    bool applicable = recipe == "Standard" ? DroidworksKernel.StandardFormatApplicable(w.tier)
                        : recipe == "Restrictive" ? DroidworksKernel.RestrictiveFormatApplicable(w.tier)
                        : DroidworksKernel.DeformatApplicable(w.tier);
                    bool wantApplicable = recipe == "Standard" ? (w.tier == DroidFormatTier.Blank || w.tier == DroidFormatTier.Mindless)
                        : recipe == "Restrictive" ? (w.tier == DroidFormatTier.Programmable || w.tier == DroidFormatTier.Sapient)
                        : w.tier != DroidFormatTier.Blank;
                    Check(applicable == wantApplicable, recipe + " offered=" + applicable + " from " + w.tier + ", design says " + wantApplicable);
                    if (!applicable) break;
                    var before = w.tier;
                    w.tier = target;
                    if (DroidworksKernel.FormatClearsServiceRecord(target)) { w.held.Clear(); ResetClock(w); }
                    bool murder = DroidworksKernel.MindDestroyed(before, target);
                    bool wantMurder = before == DroidFormatTier.Sapient && (target == DroidFormatTier.Blank || target == DroidFormatTier.Mindless);
                    Check(murder == wantMurder, "mind-destroyed=" + murder + " for " + before + " -> " + target);
                    Check((recipe == "Standard") == (target > before), recipe + " moved " + before + " -> " + target + " the wrong way");
                    if (recipe == "Deformat")
                        Check(w.held.Count == 0 && DroidworksKernel.TicksSince(w.now, w.lastReset) == 0,
                            "a deformat to Blank left " + w.held.Count + " idiosyncrasies and a clock at " + DroidworksKernel.TicksSince(w.now, w.lastReset) + ": the wiped droid keeps the personality it earned");
                    else
                        Check(w.held.SequenceEqual(heldBefore), recipe + " format changed the idiosyncrasies");
                    break;
                }
                case 4: // settings flip
                    switch (a.a % 3)
                    {
                        case 0: w.enabled = !w.enabled; break;
                        case 1: w.promote = !w.promote; break;
                        default: w.scale = Scales[a.b % Scales.Length]; break;
                    }
                    break;
                case 5: // save + load: the clock is one int in the save
                {
                    int before = DroidworksKernel.TicksSince(w.now, w.lastReset);
                    w.lastReset = int.Parse(w.lastReset.ToString(CultureInfo.InvariantCulture), CultureInfo.InvariantCulture);
                    Check(DroidworksKernel.TicksSince(w.now, w.lastReset) == before, "the clock changed across a save/load");
                    break;
                }
            }
            // ---- invariants after every step
            Check(w.held.Distinct().Count() == w.held.Count, "the same idiosyncrasy was accreted twice");
            Check(w.held.Count <= w.maxAcc, "accreted " + w.held.Count + " over the cap " + w.maxAcc);
            Check(w.held.All(i => i >= 0 && i < w.pool.Length), "an accreted trait is not in the pool");
            Check(DroidworksKernel.TicksSince(w.now, w.lastReset) >= 0, "negative service time");
            Check(DroidworksKernel.TicksSince(w.now, -1) == 0, "an unset clock read nonzero service time");
            Check(w.lastReset == w.oracleReset, "model clock and oracle clock diverged");
            if (a.kind != 0 && a.kind != 3) Check(w.tier == tierBefore, "tier changed outside a drift or a recipe");
        }

        // ===================================================================== power

        private static readonly float[] FallPerDay = { 0.33f, 1.0f, 0.1f, 0.5f };
        private static readonly float[] Rates = { 0.25f, 0.5f, 1f, 2f, 3f };
        private static readonly float[] ChargePph = { 8f, 15f, 25f, 40f };
        private static readonly float[] Charges = { 0f, 0.02f, 0.04f, 0.05f, 0.0501f, 0.3f, 0.5f, 1f };
        private static readonly float[] Densities = { 0f, 0.3f, 1f, 2f, 50f, 1e9f };

        private sealed class PowerWorld
        {
            public float level = 1f;
            public bool poweredDown, enabled = true, deny;
            public float fallPerDay, drain, charge, pph, size = 1f, density;
            public float resent, maxResent = 1f, resentPerDay = 0.05f, resentRate = 1f;
            public bool bolted, humanlike = true;
        }

        private static PowerWorld MakePower(int seed)
        {
            var r = new Random(seed * 17 + 5);
            return new PowerWorld
            {
                fallPerDay = FallPerDay[r.Next(FallPerDay.Length)], drain = Rates[r.Next(Rates.Length)], charge = Rates[r.Next(Rates.Length)],
                pph = ChargePph[r.Next(ChargePph.Length)], density = Densities[r.Next(Densities.Length)], deny = r.Next(4) == 0,
                size = Rates[r.Next(Rates.Length)], maxResent = r.Next(3) == 0 ? 0.7f : 1f, level = r.Next(3) == 0 ? 0.5f : 1f
            };
        }

        private static void PowerStep(PowerWorld w, Act a)
        {
            float levelBefore = w.level;
            switch (a.kind)
            {
                case 0: // Drain: k NeedIntervals
                {
                    int k = a.a % 80 + 1;
                    double fall = (double)w.fallPerDay * w.drain / 400.0;
                    double od = w.level;
                    for (int i = 0; i < k; i++)
                    {
                        bool wasDown = w.poweredDown;
                        float lv = w.level;
                        w.level = DroidworksKernel.PowerAfterFall(w.level, DroidworksKernel.PowerFallPerInterval(w.fallPerDay, w.drain));
                        Check(w.level <= lv && w.level >= 0f, "draining raised or underflowed the bar: " + lv + " -> " + w.level);
                        if (DroidworksKernel.ShouldPowerDown(w.enabled, w.level, w.poweredDown)) w.poweredDown = true;
                        od = Math.Max(0.0, od - fall);
                        Check(Math.Abs(w.level - od) < 1e-3, "bar " + w.level + " drifted from the reference " + F(od));
                        if (w.enabled && od <= DroidworksKernel.PoweredDownAt - 1e-3) Check(w.poweredDown, "level " + F(od) + " is under the power-down line and the droid is still up");
                        if (!wasDown && (!w.enabled || od > DroidworksKernel.PoweredDownAt + 1e-3)) Check(!w.poweredDown, "powered down at level " + F(od) + " (enabled " + w.enabled + ")");
                        w.level = (float)od;       // re-sync so float noise cannot accumulate across actions
                    }
                    break;
                }
                case 1: // Dock: JobDriver_DWRecharge, one tick at a time until full
                {
                    int ticks = a.a % 6000;
                    double want = Math.Min(1.0 - w.level, ticks * (double)w.pph * w.charge / 100.0 / 2500.0);
                    float lv0 = w.level;
                    int done = 0;
                    for (; done < ticks; done++)
                    {
                        w.level = DroidworksKernel.ClampBar(w.level + DroidworksKernel.DockGainPerTick(w.pph, w.charge, 2500));
                        if (w.level >= 1f) break;
                    }
                    Check(w.level >= lv0 && w.level <= 1f, "docking moved the bar the wrong way: " + lv0 + " -> " + w.level);
                    Check(Math.Abs((w.level - lv0) - want) < 2e-3, "docked " + ticks + " ticks at " + w.pph + "%/h x" + w.charge + ": gained " + F(w.level - lv0) + ", expected " + F(want));
                    break;
                }
                case 2: // Nimbus: scans every 60 ticks, skipping a full droid
                {
                    int scans = a.a % 100;
                    float gain = DroidworksKernel.NimbusGainPerScan(w.pph, w.charge, 60, 2500);
                    Check(Math.Abs(gain / 60f - DroidworksKernel.DockGainPerTick(w.pph, w.charge, 2500)) < 1e-7, "nimbus and dock disagree on the per-tick rate");
                    for (int i = 0; i < scans; i++) { if (w.level >= 1f) continue; w.level = DroidworksKernel.ClampBar(w.level + gain); }
                    Check(w.level >= levelBefore && w.level <= 1f, "nimbus moved the bar the wrong way");
                    break;
                }
                case 3: // reboot
                    w.poweredDown = false;
                    break;
                case 4: // settings
                    switch (a.a % 4)
                    {
                        case 0: w.enabled = !w.enabled; break;
                        case 1: w.drain = Rates[a.b % Rates.Length]; break;
                        case 2: w.charge = Rates[a.b % Rates.Length]; break;
                        default: w.fallPerDay = FallPerDay[a.b % FallPerDay.Length]; break;
                    }
                    break;
                case 5: // death: CompDroidDetonation.Notify_Killed
                {
                    float charge = a.a % 3 == 0 ? Charges[a.b % Charges.Length] : w.level;
                    float density = Densities[a.c % Densities.Length];
                    bool deny = (a.c / 7) % 3 == 0;
                    float size = Rates[(a.c / 31) % Rates.Length];
                    float eff = DroidworksKernel.EffectiveDensity(density, true, deny);
                    float scale = DroidworksKernel.DetonationScale(charge, eff, size);
                    double effO = deny ? Math.Max(density, 1.0) : density;
                    bool wantBlast = effO > 0 && charge > 0.05f;
                    Check((scale > 0f) == wantBlast, "blast=" + (scale > 0f) + " for charge " + charge + " density " + density + " deny " + deny + " (wanted " + wantBlast + ")");
                    if (scale > 0f)
                    {
                        float radius = DroidworksKernel.DetonationRadius(3.9f, scale);
                        int dmg = DroidworksKernel.DetonationDamage(scale);
                        double so = (double)charge * effO * size;
                        Check(Math.Abs(scale - so) <= so * 1e-5 + 1e-9, "scale " + scale + " != " + F(so));
                        Check(Math.Abs(radius - 3.9 * Math.Sqrt(so)) <= 1e-3 * (1 + 3.9 * Math.Sqrt(so)) || float.IsInfinity(radius), "radius " + radius);
                        Check(dmg >= 0 && dmg <= DroidworksKernel.MaxDetonationDamage, "damage " + dmg + " out of range");
                        Check(dmg == (int)Math.Min(DroidworksKernel.MaxDetonationDamage, Math.Round(50.0 * so)) || Math.Abs(dmg - 50.0 * so) <= 1.0, "damage " + dmg + " vs 50 x " + F(so));
                        // monotone: more charge never blasts less
                        float more = DroidworksKernel.DetonationScale(Math.Min(1f, charge + 0.1f), eff, size);
                        Check(more >= scale, "more charge blasted less");
                        Check(DroidworksKernel.DetonationDamage(more) >= dmg, "more charge dealt less damage");
                    }
                    else Check(DroidworksKernel.DetonationDamage(scale) == 0, "no blast but nonzero damage");
                    break;
                }
                case 6: // bolt toggles
                    if (a.a % 2 == 0) w.bolted = !w.bolted; else w.humanlike = !w.humanlike;
                    break;
                case 7: // resentment scans (HediffComp_DWBoltResentment)
                {
                    int scans = a.a % 400 + 1;
                    float before = w.resent;
                    for (int i = 0; i < scans; i++)
                    {
                        // production gates: a Humanlike pawn wearing the bolt; anything else returns before touching severity
                        if (!w.humanlike || !w.bolted) continue;
                        w.resent = DroidworksKernel.ResentmentAfter(w.resent, w.resentPerDay, w.resentRate, 60, 60000, w.maxResent);
                    }
                    Check(w.resent >= before, "resentment fell from " + before + " to " + w.resent);
                    Check(w.resent <= w.maxResent + 1e-6f, "resentment " + w.resent + " over the hediff max " + w.maxResent);
                    if (!w.humanlike || !w.bolted) Check(w.resent == before, "resentment moved with no bolt on a thinking droid");
                    else
                    {
                        double perScan = (double)w.resentPerDay * w.resentRate / 60000.0 * 60.0;
                        double want = Math.Min(w.maxResent, before + scans * perScan);
                        Check(Math.Abs(w.resent - want) < 1e-3, "resentment " + w.resent + ", expected " + F(want) + " after " + scans + " scans");
                    }
                    break;
                }
            }
            Check(w.level >= 0f && w.level <= 1f && !float.IsNaN(w.level), "bar " + w.level + " out of [0,1]");
            if (a.kind != 0 && a.kind != 1 && a.kind != 2) Check(w.level == levelBefore, "level moved outside a drain or charge");
        }

        // ===================================================================== data spike

        private sealed class SpikeWorld
        {
            public float r0, resLow, resHigh, perUse;
            public bool captured, hasGuest;
            public int count;
        }

        private static readonly float[] Res0 = { 0f, 0.4f, 1f, 10f, 25f, 100f };
        private static readonly float[] PerUses = { 0f, 1f, 5f, 12f };

        private static SpikeWorld MakeSpike(int seed)
        {
            var r = new Random(seed * 13 + 1);
            var w = new SpikeWorld { r0 = Res0[r.Next(Res0.Length)], perUse = PerUses[r.Next(PerUses.Length)], hasGuest = r.Next(8) != 0 };
            w.resLow = w.resHigh = w.r0;
            return w;
        }

        private static void SpikeStep(SpikeWorld w, Act a)
        {
            if (w.captured) return;
            int level = a.a % 21;
            w.count++;
            // ---- production TryReprogram, as a sequence of one spiker
            float before = w.resLow;
            bool rejected = false;
            if (w.perUse > 0f && w.hasGuest)
            {
                w.resLow = DroidworksKernel.ResistanceAfterSpike(w.resLow, w.perUse, level);
                rejected = w.resLow > 0f;
            }
            if (!rejected) w.captured = true;
            Check(w.resLow >= 0f, "resistance went negative");
            Check(w.resLow <= before, "resistance rose after a spike: " + before + " -> " + w.resLow);
            if (w.perUse > 0f && w.hasGuest && before > 0f) Check(w.resLow < before, "a spike made no progress at level " + level + " (resistance stuck at " + before + ")");
            Check(w.captured == (w.resLow <= 0f || w.perUse <= 0f || !w.hasGuest), "captured=" + w.captured + " with resistance " + w.resLow);
            // ---- a better spiker is never slower
            w.resHigh = DroidworksKernel.ResistanceAfterSpike(w.resHigh, w.perUse, 20);
            if (w.perUse > 0f) Check(w.resHigh <= w.resLow + 1e-4f || w.resLow == 0f, "a level-20 spiker is behind a level-" + level + " spiker");
            // ---- termination bound: even at level 0 (factor 0.5) the droid falls within r0/(perUse*0.5) spikes
            if (w.perUse > 0f && w.hasGuest)
            {
                int bound = (int)Math.Ceiling(w.r0 / (w.perUse * 0.5)) + 1;
                Check(w.captured || w.count < bound, "not captured after " + w.count + " spikes (bound " + bound + ")");
            }
        }

        // ===================================================================== trade

        private static readonly float[] PerSides = { 0f, 0.01f, 0.06f, 0.06f, 0.12f, 0.25f };
        private static readonly float[] Vanilla = { 0.5f, 1f, 7.3f, 50f, 99.4f, 99.5f, 99.6f, 120f, 1999f, 25000f };

        private sealed class TradeWorld { public float perSide = 0.06f; }

        private static float VanillaRound(float v) { return v > 99.5f ? (float)Math.Round(v) : v; }

        private static void TradeStep(TradeWorld w, Act a)
        {
            if (a.kind == 1) { w.perSide = PerSides[a.a % PerSides.Length]; return; }
            bool p = (a.a & 1) != 0, known = (a.a & 2) != 0, th = (a.a & 4) != 0;
            float v = VanillaRound(Vanilla[a.b % Vanilla.Length] * (a.c % 5 == 0 ? 1f : 1f + (a.c % 7) * 0.013f));
            const float MinBuy = 0.5f, MinSell = 0.01f;
            float adv = DroidworksKernel.TradeAdvantage(p, known, th, w.perSide);
            int net = (p ? 1 : -1) + (known ? (th ? -1 : 1) : 0);
            Check(adv == net * w.perSide, "advantage " + adv + " != net " + net + " x " + w.perSide);
            Check(Math.Abs(adv) <= 2 * w.perSide + 1e-9f, "advantage " + adv + " beyond two sides");
            if (known && p == th) Check(adv == 0f, "both-or-neither did not cancel: " + adv);
            Check(adv == -DroidworksKernel.TradeAdvantage(!p, known, !th, w.perSide), "the advantage is not antisymmetric when the roles swap");
            if (!known) Check(adv == DroidworksKernel.TradeAdvantage(p, false, !th, w.perSide), "an uninspectable trader changed the advantage");
            float buy = DroidworksKernel.BuyPrice(v, adv, MinBuy), sell = DroidworksKernel.SellPrice(v, adv, MinSell);
            if (adv == 0f) Check(buy == v && sell == v, "zero advantage changed a price");
            else
            {
                Check(buy >= MinBuy && sell >= MinSell, "price under the vanilla floor: buy " + buy + " sell " + sell);
                Check(!float.IsNaN(buy) && !float.IsNaN(sell) && !float.IsInfinity(buy) && !float.IsInfinity(sell), "non-finite price");
                if (adv > 0f) Check(buy <= v && sell >= v, "an advantage of " + adv + " raised the buy price or cut the sell price: v " + v + " buy " + buy + " sell " + sell);
                else Check(buy >= v && sell <= v, "a penalty of " + adv + " cut the buy price or raised the sell price: v " + v + " buy " + buy + " sell " + sell);
                if (buy > 99.5f) Check(buy == (float)Math.Round(buy), "a large buy price kept a fraction: " + buy);
                // monotone in the vanilla price
                float v2 = VanillaRound(v * 1.5f + 0.5f);
                Check(DroidworksKernel.BuyPrice(v2, adv, MinBuy) >= buy && DroidworksKernel.SellPrice(v2, adv, MinSell) >= sell, "prices not monotone in the base price");
            }
        }

        // ===================================================================== units

        public static List<string> Units(int n, int baseSeed)
        {
            var fails = new List<string>();
            Action<string> bad = m => { if (fails.Count < 8) fails.Add("units: " + m); };
            var r = new Random(baseSeed);

            // --- severity -> tier must agree with the RSW_DW_FormatTier HediffDef stage cuts 0 / 1.5 / 2.5 / 3.5 (HediffDefs_Droidworks.xml)
            Cases++;
            float[] cuts = { 0f, 1.5f, 2.5f, 3.5f };
            Func<float, DroidFormatTier> stageOracle = s => { int t = 0; for (int i = 0; i < 4; i++) if (s >= cuts[i]) t = i; return (DroidFormatTier)t; };
            var probes = new List<float> { -1e30f, -5f, -0.5f, 0f, 0.49f, 0.5f, 1f, 1.49f, 1.5f, 1.51f, 2f, 2.49f, 2.5f, 2.51f, 3f, 3.49f, 3.5f, 3.51f, 4f, 4.5f, 9f, 3e9f, 1e30f, float.MaxValue, float.PositiveInfinity, float.NegativeInfinity };
            foreach (float c in cuts) { probes.Add(BitDown(c)); probes.Add(BitUp(c)); }
            DroidFormatTier prev = DroidFormatTier.Blank; float prevS = float.NegativeInfinity;
            foreach (float s in probes.OrderBy(x => x))
            {
                Steps++;
                var got = DroidworksKernel.TierForSeverity(s);
                if (got != stageOracle(s)) bad("severity " + F(s) + " maps to " + got + " but the hediff stage cuts say " + stageOracle(s));
                if (got < prev) bad("tier fell from " + prev + " at " + F(prevS) + " to " + got + " at " + F(s));
                prev = got; prevS = s;
            }
            if (DroidworksKernel.TierForSeverity(float.NaN) != DroidworksKernel.DefaultTier) bad("NaN severity did not read as the default tier");
            foreach (DroidFormatTier t in Enum.GetValues(typeof(DroidFormatTier)))
            {
                Steps++;
                if (DroidworksKernel.TierForSeverity(DroidworksKernel.SeverityFor(t)) != t) bad("severity round trip failed for " + t);
            }

            // --- weighted pick: respects zero/negative/NaN weights, proportional, extremes
            Cases++;
            {
                var wts = new List<float> { 1f, 0f, 3f, -2f, float.NaN, 6f };
                var counts = new int[wts.Count];
                int N = 200000;
                for (int i = 0; i < N; i++) { Steps++; counts[DroidworksKernel.WeightedPick(wts, (float)r.NextDouble())]++; }
                if (counts[1] + counts[3] + counts[4] != 0) bad("weighted pick chose a zero, negative or NaN weight: " + string.Join(",", counts));
                double[] share = { 0.1, 0, 0.3, 0, 0, 0.6 };
                for (int i = 0; i < wts.Count; i++) if (Math.Abs(counts[i] / (double)N - share[i]) > 0.01) bad("weighted pick share of " + i + " is " + counts[i] / (double)N + ", want " + share[i]);
                if (DroidworksKernel.WeightedPick(wts, 0f) != 0) bad("roll 0 did not pick the first positive entry");
                if (DroidworksKernel.WeightedPick(wts, BitDown(1f)) != 5) bad("the top of the roll range did not pick the last positive entry");
                if (DroidworksKernel.WeightedPick(wts, 1f) != 5) bad("roll 1.0 ran off the end");
                if (DroidworksKernel.WeightedPick(new List<float> { 0f, -1f }, 0.5f) != -1) bad("an all-zero pool still picked");
                if (DroidworksKernel.WeightedPick(new List<float>(), 0.5f) != -1) bad("an empty pool still picked");
                if (DroidworksKernel.WeightedPick(null, 0.5f) != -1) bad("a null pool still picked");
            }

            // --- the design timeline (CompDWServiceRecord): 2 y / 3.5 y / 5 y at scale 1, and the setting scales it
            Cases++;
            {
                long[] want = { 7200000, 12600000, 18000000 };
                for (int k = 0; k < 3; k++) { Steps++; long d = DroidworksKernel.DriftDue(2 * TicksPerYear, TicksPerYear * 3 / 2, k, 1f); if (d != want[k]) bad("drift #" + (k + 1) + " due at " + d + ", design " + want[k]); }
                if (DroidworksKernel.DriftDue(2 * TicksPerYear, TicksPerYear * 3 / 2, 0, 0.25f) != 1800000) bad("driftTime 0.25x did not quarter the first drift");
                if (DroidworksKernel.DriftDue(int.MaxValue, int.MaxValue, 1000, 3f) <= 0) bad("a huge ladder overflowed to a non-positive due");
                if (DroidworksKernel.DriftDue(100, 100, 5, -1f) != 0) bad("a negative time scale produced a positive due");
                if (DroidworksKernel.DriftDue(100, 100, 5, float.NaN) != 0) bad("a NaN time scale was not clamped");
                if (DroidworksKernel.ChassisWeight(2f, null, null, DroidChassis.Battle) != 2f) bad("no overrides did not fall back to the default weight");
                var ch = new List<DroidChassis> { DroidChassis.Battle, DroidChassis.Battle };
                if (DroidworksKernel.ChassisWeight(2f, ch, new List<float> { 9f, 1f }, DroidChassis.Battle) != 9f) bad("the first override for a chassis did not win");
                if (DroidworksKernel.ChassisWeight(2f, ch, new List<float> { 9f, 1f }, DroidChassis.Labour) != 2f) bad("an unnamed chassis did not take the default");
            }

            // --- salvage tables: design facts per chassis
            Cases++;
            {
                const DroidPartSlot Legs = DroidPartSlot.Leg | DroidPartSlot.Manipulator;
                foreach (int c in new[] { 2, 5 }) { Steps++; if ((DroidworksKernel.LegalParts(c) & Legs) != 0) bad("chassis " + c + " (small hoverer) sheds legs or arms"); }
                if ((DroidworksKernel.LegalParts(6) & DroidPartSlot.Manipulator) != 0 || (DroidworksKernel.LegalParts(6) & DroidPartSlot.Sensor) != 0) bad("the power hauler sheds arms or a sensor");
                if ((DroidworksKernel.LegalParts(0) & DroidPartSlot.Sensor) != 0) bad("labour droids shed a sensor");
                foreach (int c in new[] { 1, 3, 4, 7, -1, 8, 99 })
                    if (DroidworksKernel.LegalParts(c) != (DroidPartSlot.Leg | DroidPartSlot.Manipulator | DroidPartSlot.Sensor | DroidPartSlot.Motivator | DroidPartSlot.Servo | DroidPartSlot.PowerCell)) bad("chassis " + c + " does not shed the full set");
                for (int c = -3; c < 12; c++)
                {
                    Steps++;
                    if (DroidworksKernel.UsesPrimitiveParts(c) != (c == 7)) bad("primitive parts for chassis " + c);
                    var want = c >= 0 && c <= 7 ? (DroidChassis)c : DroidChassis.Labour;
                    if (DroidworksKernel.HeadChassis(c) != want) bad("head chassis for class " + c + " is " + DroidworksKernel.HeadChassis(c));
                    if (!DroidworksKernel.LegalParts(c).HasFlag(DroidPartSlot.Servo) || !DroidworksKernel.LegalParts(c).HasFlag(DroidPartSlot.PowerCell)) bad("chassis " + c + " does not shed the servo and power cell every droid has");
                }
                int[] bucket = { 0, 0, 1, 1, 2, 2, 2 };
                for (int q = 0; q < 7; q++) if (DroidworksKernel.QualityBucket(q) != bucket[q]) bad("quality " + q + " bucket " + DroidworksKernel.QualityBucket(q));
            }

            // --- detonation numbers
            Cases++;
            {
                float s = DroidworksKernel.DetonationScale(1f, 1f, 1f);
                if (s != 1f || DroidworksKernel.DetonationDamage(s) != 50 || Math.Abs(DroidworksKernel.DetonationRadius(3.9f, s) - 3.9f) > 1e-6) bad("a full unit droid should blast scale 1 / 50 damage / radius 3.9");
                if (DroidworksKernel.DetonationDamage(3.0e12f) != DroidworksKernel.MaxDetonationDamage) bad("a huge blast did not saturate (it wrapped negative)");
                if (DroidworksKernel.DetonationDamage(float.NaN) != 0) bad("a NaN blast dealt damage");
            }

            // --- spike target tables, exhaustive
            Cases++;
            {
                foreach (bool tn in new[] { false, true }) foreach (bool fl in new[] { false, true }) foreach (bool hasF in new[] { false, true })
                foreach (string tf in new string[] { null, "Pirate", "Empire" }) foreach (string sf in new string[] { null, "", "Empire" })
                {
                    Steps++;
                    bool want = !tn && (fl ? !hasF : (tf != null && !string.IsNullOrEmpty(sf) && tf == sf));
                    if (DroidworksKernel.SpikeMatchesFaction(tn, fl, hasF, tf, sf) != want) bad("faction match (null " + tn + ", factionless " + fl + ", has " + hasF + ", " + tf + " vs " + sf + ")");
                }
                foreach (bool tn in new[] { false, true }) foreach (bool dead in new[] { false, true }) foreach (bool dn in new[] { false, true })
                foreach (bool pr in new[] { false, true }) foreach (bool rq in new[] { false, true }) foreach (bool m in new[] { false, true })
                {
                    Steps++;
                    bool want = !tn && !dead && (dn || pr) && (!rq || pr) && m;
                    if (DroidworksKernel.SpikeValidTarget(tn, dead, dn, pr, rq, m) != want) bad("valid target (null " + tn + ", dead " + dead + ", downed " + dn + ", prisoner " + pr + ", requiresPrisoner " + rq + ", match " + m + ")");
                }
                for (int l = 0; l < 21; l++) if (Math.Abs(DroidworksKernel.SpikeSkillFactor(l) - (0.5 + 0.05 * l)) > 1e-6) bad("skill factor at level " + l);
            }

            // --- format applicability matrix, exhaustive
            Cases++;
            foreach (DroidFormatTier t in Enum.GetValues(typeof(DroidFormatTier)))
            {
                Steps++;
                bool[] want = {
                    t == DroidFormatTier.Blank || t == DroidFormatTier.Mindless,
                    t == DroidFormatTier.Programmable || t == DroidFormatTier.Sapient,
                    t != DroidFormatTier.Blank };
                bool[] got = { DroidworksKernel.StandardFormatApplicable(t), DroidworksKernel.RestrictiveFormatApplicable(t), DroidworksKernel.DeformatApplicable(t) };
                for (int i = 0; i < 3; i++) if (want[i] != got[i]) bad(Recipes[i] + " applicability from " + t + " is " + got[i]);
                if (DroidworksKernel.PromotesToSapient(0, true, t) != (t == DroidFormatTier.Programmable)) bad("promotion from " + t);
            }
            return fails;
        }

        private static float BitDown(float f) { return MathF.BitDecrement(f); }
        private static float BitUp(float f) { return MathF.BitIncrement(f); }

        // ===================================================================== driver

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("drift", () => RunFamily("drift", N(4000), S(1), 7919, new[] { "Check", "Time", "Wipe", "Format", "Setting", "Reload" }, new[] { 12, 8, 2, 4, 2, 1 }, 220, MakeDrift, DriftStep, 1000, 1000, 1)),
                ("power", () => RunFamily("power", N(3000), S(1), 104729, new[] { "Drain", "Dock", "Nimbus", "Reboot", "Setting", "Die", "Bolt", "Resent" }, new[] { 6, 4, 2, 1, 2, 4, 2, 4 }, 120, MakePower, PowerStep, 6000, 40, 100000)),
                ("spike", () => RunFamily("spike", N(2000), S(1), 6007, new[] { "Spike" }, new[] { 1 }, 260, MakeSpike, SpikeStep, 21, 1, 1)),
                ("trade", () => RunFamily("trade", N(2000), S(1), 30011, new[] { "Session", "SetPerSide" }, new[] { 9, 1 }, 120, seed => new TradeWorld { perSide = PerSides[seed % PerSides.Length] }, TradeStep, 8, 10, 100)),
                ("units", () => Units(N(1000), S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine("fuzz " + f.name + ": " + (Cases - c0) + " cases, " + (Steps - s0) + " steps, " + t.Elapsed.TotalSeconds.ToString("F2") + "s, " + (fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES"));
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            Console.WriteLine("droidworks fuzz: " + Cases + " cases, " + Steps + " steps, " + sw.Elapsed.TotalSeconds.ToString("F2") + "s total -> " + (ok ? "OK" : "FAILED"));
            return ok;
        }
    }
}
