// Approach B for Contagion: seeded fuzz over the Verse-free kernels the Contagion mod calls (../Kernel/*.cs):
//   sky          the Burn clock, its tells, the Bloom clock and the Cloud Repulsor against a mock Burn condition (RM_SkyKernel)
//   coalescence  the Coalescence's stage / growth / emission / death spill (RM_CoalescenceKernel)
//   burn         the Burn's pressure classification, exposure and dive choice, exhaustively (RM_SkyKernel)
//   draftprint   sampling, extreme stat, worst limb, contract match and reward, market value, gestation plan, the Unfinished
//                spawner arithmetic (RM_DraftprintKernel)
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Contagion.SelfTest
{
    internal static class ContagionFuzz
    {
        public static long Cases, Steps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private const int Tpd = 60000, Iv = 250;

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

        // ════════════════════════ sky ════════════════════════
        private static readonly string[] SkyNames = { "Poll", "Burn", "Tells", "Repulsor", "Power", "Ext", "Coal", "Freq" };
        public static long SNaturalBurns, SForced, STellFirst, STells, SGapWindows, SCoalForm;

        private static List<Act> GenSky(Random r)
        {
            int n = 6 + r.Next(40);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 58 ? 0 : w < 64 ? 1 : w < 70 ? 2 : w < 78 ? 3 : w < 88 ? 4 : w < 92 ? 5 : w < 96 ? 6 : 7;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = SkyNames });
            }
            return l;
        }

        private static string RunSky(int seed, List<Act> acts)
        {
            var rng = new Random(seed ^ 0x2222);
            float meanDays = new[] { 0.25f, 1f, 3f }[rng.Next(3)];
            int lead = new[] { 0, 100, 250, 1250 }[rng.Next(4)], longBloom = new[] { 2500, 15000, 90000 }[rng.Next(3)];
            int durMin = 1500, durMax = 4000, warmup = new[] { 250, 2500 }[rng.Next(2)], hold = new[] { 250, 750, 1500 }[rng.Next(3)];
            float freq = 1f;
            var st = SkyState.Fresh;
            bool burnEnabled = true, tellsOn = true, coalOn = true, repOn = true, powered = false, hasExt = true, hasRep = false, coal = false;
            int burnLeft = 0, now = 250 * 400, warm = 0;
            int scheduledAt = -1, tellFirsts = 0; bool cycleDisturbed = false, sawTellThisCycle = false;
            bool otherBurn = false;   // the live Burn is (also) someone else's: natural or dev
            int unpoweredPolls = 0;
            string where = "";
            try
            {
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    switch (a.kind)
                    {
                        case 1: burnLeft = Math.Max(burnLeft, 500 + a.a % 3000); otherBurn = true; break;    // a dev-tool / other-cause Burn
                        case 2: tellsOn = !tellsOn; cycleDisturbed = true; break;
                        case 3: if (a.a % 2 == 0) hasRep = true; else repOn = !repOn; break;
                        case 4: powered = !powered; break;
                        case 5: hasExt = !hasExt; cycleDisturbed = true; break;
                        case 6: if (a.a % 2 == 0) coalOn = !coalOn; else burnEnabled = !burnEnabled; cycleDisturbed = true; break;
                        case 7: freq = new[] { 0.05f, 0.5f, 1f, 4f }[a.a % 4]; cycleDisturbed = true; break;
                        case 0:
                            for (int t = 0, n = 1 + a.a % (a.b % 4 == 0 ? 400 : 40); t < n; t++)
                            {
                                now += Iv;
                                burnLeft = Math.Max(0, burnLeft - Iv);
                                bool burnActive = burnLeft > 0;
                                int gapRolled = -1;
                                var before = st;
                                var act = RM_SkyKernel.Tick(ref st, now, hasExt, hasExt && burnActive, burnEnabled, tellsOn, lead,
                                    () => { gapRolled = RM_SkyKernel.RollGap(meanDays, freq, 0.5f + (float)rng.NextDouble(), lead, Iv, Tpd); return gapRolled; }, out int ticksToBurn);
                                // ---- clock ----
                                if (!hasExt) { Check(act == SkyAct.Reset && st.nextBurnTick == -1 && st.bloomSinceTick == -1 && !st.tellsBegun, "no sky extension must fully reset the clock"); }
                                else if (burnActive) { Check(act == SkyAct.BurnHeld && st.nextBurnTick == -1 && !st.tellsBegun && st.bloomSinceTick == -1, "a Burn in the sky must hold the clock reset"); }
                                else
                                {
                                    Check((act & SkyAct.TryCoalescence) != 0 && st.bloomSinceTick >= 0, "a calm sky must run the bloom clock and try the Coalescence");
                                    if (!burnEnabled) Check((act & (SkyAct.StartBurn | SkyAct.Tell | SkyAct.Scheduled)) == 0 && st.nextBurnTick == -1, "Burns disabled yet the clock scheduled or acted");
                                    else if ((act & SkyAct.Scheduled) != 0)
                                    {
                                        Check(before.nextBurnTick < 0 && gapRolled >= lead + Iv, $"gap {gapRolled} shorter than lead {lead} + one poll");
                                        Check(st.nextBurnTick == now + gapRolled, "next Burn is not now + gap");
                                        scheduledAt = now; tellFirsts = 0; sawTellThisCycle = false; cycleDisturbed = false; SGapWindows++;
                                    }
                                    else if ((act & SkyAct.StartBurn) != 0)
                                    {
                                        Check(before.nextBurnTick >= 0 && now >= before.nextBurnTick, "Burn started before its time");
                                        Check(st.nextBurnTick == -1 && !st.tellsBegun, "Burn start must clear the schedule");
                                        int dur = durMin + rng.Next(durMax - durMin + 1);
                                        Check(RM_SkyKernel.StretchBurn(0, dur) == dur, "new Burn has the rolled duration");
                                        burnLeft = Math.Max(burnLeft, dur); SNaturalBurns++; otherBurn = true;
                                        if (!cycleDisturbed && tellsOn && lead >= Iv && scheduledAt >= 0) Check(sawTellThisCycle, "an undisturbed cycle with tells on began its Burn without a single tell");
                                        scheduledAt = -1;
                                    }
                                    else if ((act & SkyAct.Tell) != 0)
                                    {
                                        STells++;
                                        Check(tellsOn && burnEnabled && before.nextBurnTick >= 0, "a tell with tells off or no Burn scheduled");
                                        Check(now >= before.nextBurnTick - Math.Max(0, lead) && now < before.nextBurnTick, "a tell outside the lead window");
                                        Check(ticksToBurn == before.nextBurnTick - now && ticksToBurn > 0, "tell countdown wrong");
                                        sawTellThisCycle = true;
                                        if ((act & SkyAct.TellFirst) != 0) { tellFirsts++; STellFirst++; Check(!before.tellsBegun && tellFirsts == 1, $"first-tell flag fired {tellFirsts} times in one cycle"); }
                                        else Check(before.tellsBegun, "a later tell before any first tell");
                                    }
                                    else Check(act == SkyAct.TryCoalescence, "unexpected act " + act);
                                    if (st.nextBurnTick >= 0) Check(before.nextBurnTick < 0 || st.nextBurnTick == before.nextBurnTick, "a schedule moved without a reset");
                                }
                                // ---- the Coalescence rides the bloom clock and dies to the Burn ----
                                if ((act & SkyAct.TryCoalescence) != 0)
                                {
                                    bool gate = RM_SkyKernel.CoalescenceGate(coalOn, burnEnabled, true, now, st.bloomSinceTick, longBloom, coal);
                                    Check(gate == (coalOn && burnEnabled && now - st.bloomSinceTick >= longBloom && !coal), "CoalescenceGate disagrees with enabled && Burns on && long bloom && none already");
                                    if (gate && rng.Next(4) == 0) { coal = true; SCoalForm++; Check(now - st.bloomSinceTick >= longBloom, "formed before the bloom was long"); Check(burnEnabled, "a Coalescence formed while Burns are disabled: nothing but a Repulsor could ever kill it"); }
                                }
                                if (hasExt && burnActive) coal = false;   // any Burn kills it
                                // ---- the Repulsor ----
                                if (hasRep)
                                {
                                    var step2 = RM_SkyKernel.RepulsorTick(ref warm, repOn, powered, Iv, warmup);
                                    if (!repOn || !powered) Check(warm == 0 && step2 == RepulsorStep.Reset, "the repulsor kept its warm-up without power or while off");
                                    if (step2 == RepulsorStep.Holding)
                                    {
                                        Check(warm >= warmup, "emitting before warmed up");
                                        if (hasExt)
                                        {
                                            int prev = burnLeft;
                                            burnLeft = burnLeft > 0 ? RM_SkyKernel.StretchBurn(burnLeft, hold) : hold;
                                            Check(burnLeft >= prev, "the repulsor shortened a Burn");
                                            Check(burnLeft >= hold, "the held Burn has fewer than holdTicks left");
                                            if (prev == 0) { SForced++; otherBurn = false; }
                                        }
                                    }
                                }
                                // ---- a Burn that is only the repulsor's never has more than holdTicks left, so it dies by itself after power loss ----
                                if (burnLeft == 0) otherBurn = false;
                                if (!otherBurn) Check(burnLeft <= hold, $"a repulsor-only Burn has {burnLeft} ticks left, hold is {hold}");
                                unpoweredPolls = (hasRep && (!powered || !repOn)) ? unpoweredPolls + 1 : 0;
                                if (!otherBurn && unpoweredPolls > hold / Iv + 1) Check(burnLeft == 0, $"a repulsor-only Burn survived {unpoweredPolls} polls without power (hold {hold})");
                                Check(burnLeft >= 0, "negative Burn time");
                            }
                            break;
                    }
                }
                return null;
            }
            catch (Exception e) { return e.Message + where; }
        }

        private static string SkyUnits(int seed)
        {
            var r = new Random(seed);
            // gap: scales with the mean and inversely with frequency; floor is lead + one poll
            Check(RM_SkyKernel.RollGap(3f, 1f, 1f, 1250, 250, Tpd) == 180000 && RM_SkyKernel.RollGap(3f, 2f, 1f, 1250, 250, Tpd) == 90000, "gap scaling");
            Check(RM_SkyKernel.RollGap(0.01f, 1f, 0.5f, 1250, 250, Tpd) == 1500, "gap floor = lead + interval");
            Check(RM_SkyKernel.RollGap(3f, 0f, 1f, 0, 250, Tpd) == RM_SkyKernel.RollGap(3f, 0.05f, 1f, 0, 250, Tpd), "frequency 0 must clamp to 0.05, not divide by zero");
            for (int i = 0; i < 1000; i++)
            {
                float f = (float)(r.NextDouble() * 5), m = (float)(r.NextDouble() * 6 + 0.01), roll = 0.5f + (float)r.NextDouble();
                int lead = r.Next(0, 3000), g = RM_SkyKernel.RollGap(m, f, roll, lead, Iv, Tpd); Steps++;
                Check(g >= lead + Iv && g > 0, $"gap {g} below the floor");
            }
            // tell window: [next - lead, next)
            Check(RM_SkyKernel.InTellWindow(750, 1000, 250) && !RM_SkyKernel.InTellWindow(749, 1000, 250) && !RM_SkyKernel.InTellWindow(1000, 1000, 250) && RM_SkyKernel.InTellWindow(999, 1000, -5) == false, "tell window edges");
            Check(RM_SkyKernel.StretchBurn(100, 750) == 750 && RM_SkyKernel.StretchBurn(3000, 750) == 3000, "StretchBurn only lengthens");
            for (int m = 0; m < 64; m++)
            {
                bool en = (m & 1) != 0, def = (m & 2) != 0, one = (m & 4) != 0, burns = (m & 32) != 0; int bloom = (m & 8) != 0 ? 0 : 99999; Steps++;
                Check(RM_SkyKernel.CoalescenceGate(en, burns, def, 100000, bloom, 90000, one) == (en && burns && def && 100000 - bloom >= 90000 && !one), $"CoalescenceGate row {m}");
            }
            // repulsor warm-up: exact polls to hold, instant reset
            int warm = 0, polls = 0; while (RM_SkyKernel.RepulsorTick(ref warm, true, true, 250, 2500) != RepulsorStep.Holding) polls++; Check(polls == 10 && warm == 2500, $"repulsor took {polls} polls to warm");
            Check(RM_SkyKernel.RepulsorTick(ref warm, true, false, 250, 2500) == RepulsorStep.Reset && warm == 0, "power loss resets warm-up");
            warm = 100; Check(RM_SkyKernel.RepulsorTick(ref warm, false, true, 250, 2500) == RepulsorStep.Reset && warm == 0, "disabled resets warm-up");
            return null;
        }

        public static List<string> Sky(int n, int baseSeed)
        {
            var fails = new List<string>();
            Cases++;
            try { string e = SkyUnits(baseSeed); if (e != null) fails.Add("sky units: " + e); } catch (Exception e) { fails.Add("sky units: " + e.Message); }
            fails.AddRange(Family("sky", n, baseSeed, s => Drive(s, GenSky, RunSky)));
            return fails;
        }

        // ════════════════════════ coalescence ════════════════════════
        private static readonly string[] CoalNames = { "Poll", "Absorb", "Burn", "Kill", "Setting" };
        public static long CEmits, CBlocked, CPassive, CStages, CCollapses;

        private static List<Act> GenCoal(Random r)
        {
            int n = 6 + r.Next(40);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 55 ? 0 : w < 75 ? 1 : w < 82 ? 2 : w < 92 ? 3 : 4;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = CoalNames });
            }
            return l;
        }

        private static string RunCoal(int seed, List<Act> acts)
        {
            var rng = new Random(seed ^ 0x4444);
            int nst = 1 + rng.Next(4);
            var thr = new List<int> { 0 }; for (int i = 1; i < nst; i++) thr.Add(thr[i - 1] + 1 + rng.Next(12));
            var emit = Enumerable.Range(0, nst).Select(_ => 500 + 250 * rng.Next(0, 20)).ToList();
            var maxM = Enumerable.Range(0, nst).Select(i => 1 + rng.Next(6)).ToList();
            int passive = new[] { 0, 5000, 60000 }[rng.Next(3)], perStage = rng.Next(0, 4), baseS = rng.Next(0, 4), massPer = new[] { 0, 1, 4 }[rng.Next(3)], sMax = rng.Next(1, 20);
            int mass = 0, now = 100000, lastEmit = now, lastGrowth = now, live = 0; bool enabled = true, burn = false, dead = false;
            string where = "";
            try
            {
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    if (dead) break;
                    switch (a.kind)
                    {
                        case 1: if (enabled) mass += 1 + a.a % 3; break;     // absorption only while it acts
                        case 2: burn = !burn; break;
                        case 3: live = Math.Max(0, live - 1 - a.a % 2); break;
                        case 4: enabled = !enabled; break;
                        case 0:
                            for (int t = 0, n = 1 + a.a % (a.b % 3 == 0 ? 300 : 20); t < n; t++)
                            {
                                now += Iv;
                                if (RM_CoalescenceKernel.Collapses(burn))
                                {
                                    int stage = RM_CoalescenceKernel.Stage(mass, thr);
                                    int s = RM_CoalescenceKernel.Samples(baseS, perStage, stage, massPer, mass, sMax);
                                    Check(s <= sMax, "more samples than the cap"); Check(s >= Math.Min(sMax, baseS), "fewer samples than the base");
                                    CCollapses++; dead = true; break;
                                }
                                if (!RM_CoalescenceKernel.Acts(burn, enabled)) { continue; }
                                int massBefore = mass, stageBefore = RM_CoalescenceKernel.Stage(mass, thr);
                                if (RM_CoalescenceKernel.PassiveGrowthDue(passive, now, lastGrowth)) { lastGrowth = now; mass++; CPassive++; Check(passive > 0, "passive growth with passive disabled"); }
                                int stg = RM_CoalescenceKernel.Stage(mass, thr);
                                Check(stg >= stageBefore && stg <= nst - 1 && stg == thr.Count(x => x <= mass) - 1, $"stage {stg} for mass {mass}, thresholds [{string.Join(",", thr)}]");
                                if (stg > stageBefore) CStages++;
                                int iv = RM_CoalescenceKernel.At(emit, stg, 3000);
                                Check(RM_CoalescenceKernel.EmitDue(now, lastEmit, iv) == (now - lastEmit >= iv), "EmitDue disagrees with now - lastEmit >= interval");
                                if (RM_CoalescenceKernel.EmitDue(now, lastEmit, iv))
                                {
                                    Check(now - lastEmit >= iv, "emitted before the interval");
                                    lastEmit = now;
                                    if (RM_CoalescenceKernel.MayEmit(live, RM_CoalescenceKernel.At(maxM, stg, 3))) { live++; CEmits++; Check(live <= RM_CoalescenceKernel.At(maxM, stg, 3), "emitted past the manhunter cap"); }
                                    else CBlocked++;
                                }
                            }
                            break;
                    }
                    Check(mass >= 0, "negative mass");
                }
                return null;
            }
            catch (Exception e) { return e.Message + where; }
        }

        private static string CoalUnits()
        {
            var tbl = new List<int> { 10, 20, 30 };
            Check(RM_CoalescenceKernel.At(tbl, -5, 0) == 10 && RM_CoalescenceKernel.At(tbl, 9, 0) == 30 && RM_CoalescenceKernel.At(tbl, 1, 0) == 20, "At clamps to the table ends");
            Check(RM_CoalescenceKernel.At(new List<int>(), 3, 77) == 77 && RM_CoalescenceKernel.At(null, 0, 5) == 5, "At empty -> fallback");
            var th = new List<int> { 0, 6, 15 };
            foreach (var (mass, want) in new[] { (0, 0), (5, 0), (6, 1), (14, 1), (15, 2), (400, 2) }) Check(RM_CoalescenceKernel.Stage(mass, th) == want, $"Stage({mass})");
            Check(RM_CoalescenceKernel.Samples(2, 2, 2, 4, 15, 14) == 2 + 4 + 3 && RM_CoalescenceKernel.Samples(2, 2, 2, 0, 15, 14) == 6 && RM_CoalescenceKernel.Samples(2, 2, 2, 4, 400, 14) == 14, "Samples (cap, no divide by zero)");
            Check(RM_CoalescenceKernel.Collapses(true) && !RM_CoalescenceKernel.Collapses(false) && !RM_CoalescenceKernel.Acts(true, true) && !RM_CoalescenceKernel.Acts(false, false) && RM_CoalescenceKernel.Acts(false, true), "collapse / acts truth");
            Check(!RM_CoalescenceKernel.PassiveGrowthDue(0, 99999, 0) && RM_CoalescenceKernel.PassiveGrowthDue(60000, 60000, 0) && !RM_CoalescenceKernel.PassiveGrowthDue(60000, 59999, 0), "passive growth boundary");
            return null;
        }

        public static List<string> Coal(int n, int baseSeed)
        {
            var fails = new List<string>();
            Cases++;
            try { CoalUnits(); } catch (Exception e) { fails.Add("coalescence units: " + e.Message); }
            fails.AddRange(Family("coalescence", n, baseSeed, s => Drive(s, GenCoal, RunCoal)));
            return fails;
        }

        // ════════════════════════ burn ════════════════════════
        public static List<string> Burn(int n, int baseSeed)
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                for (int m = 0; m < 16; m++)
                {
                    bool inb = (m & 1) != 0, roof = (m & 2) != 0, water = (m & 4) != 0, tree = (m & 8) != 0; Steps++;
                    Check(RM_SkyKernel.Exposed(inb, roof, water, tree) == (inb && !roof && !water && !tree), $"Exposed row {m}");
                }
                for (int m = 0; m < 16; m++)
                {
                    bool nat = (m & 1) != 0, arm = (m & 2) != 0, leak = (m & 4) != 0, living = (m & 8) != 0; Steps++;
                    var got = RM_SkyKernel.Classify(nat, arm, leak, living);
                    var want = nat ? (arm ? BurnEffect.None : leak ? BurnEffect.Damage : BurnEffect.DamageAndDive) : living ? BurnEffect.Dose : BurnEffect.None;
                    Check(got == want, $"Classify({nat},{arm},{leak},{living}) = {got}, want {want}");
                    if (arm && nat) Check(got == BurnEffect.None, "an armoured native was hurt");
                    if (leak && nat && !arm) Check(got == BurnEffect.Damage, "a leaker dived or was spared");
                    if (nat) Check(got != BurnEffect.Dose, "a native took the visitor dose");
                }
                for (int m = 0; m < 16; m++)
                {
                    bool ext = (m & 1) != 0, en = (m & 2) != 0, arrived = (m & 4) != 0; float f = (m & 8) != 0 ? 1f : 0f; Steps++;
                    Check(RM_SkyKernel.PressureActive(ext, en, arrived, f) == (ext && en && arrived && f > 0f), $"PressureActive row {m}");
                }
                for (int m = 0; m < 32; m++)
                {
                    bool dn = (m & 1) != 0, dr = (m & 2) != 0, mental = (m & 4) != 0, jobs = (m & 8) == 0, running = (m & 16) != 0; Steps++;
                    Check(RM_SkyKernel.MayDive(dn, dr, mental, jobs, running) == (!dn && !dr && !mental && jobs && !running), $"MayDive row {m}");
                }
                // dive pick: only the first four sheltered cells are tried, the first reachable wins, reachability is asked lazily
                for (int count = 0; count <= 7; count++) for (int mask = 0; mask < 128; mask++)
                {
                    int asked = 0; Steps++;
                    int got = RM_SkyKernel.PickDive(count, i => { asked++; return (mask & (1 << i)) != 0; });
                    int want = -1; for (int i = 0; i < Math.Min(count, 4); i++) if ((mask & (1 << i)) != 0) { want = i; break; }
                    Check(got == want, $"PickDive(count {count}, mask {mask}) = {got}, want {want}");
                    Check(asked <= 4 && asked == (want >= 0 ? want + 1 : Math.Min(count, 4)), $"PickDive asked {asked} reachability checks");
                }
            }
            catch (Exception e) { fails.Add("burn: " + e.Message); }
            return fails;
        }

        // ════════════════════════ draftprint ════════════════════════
        public static long DMatch, DNoMatch, DExtreme, DWorst, DPlans;

        private static string DraftCase(int seed)
        {
            var r = new Random(seed);
            // contract matching vs a set oracle
            int pool = 1 + r.Next(6);
            var printLimbs = new HashSet<int>(); for (int i = 0; i < pool; i++) if (r.Next(2) == 0) printLimbs.Add(i);
            var req = new List<int>(); int nreq = r.Next(0, 4); for (int i = 0; i < nreq; i++) req.Add(r.Next(8) == 0 ? -1 : r.Next(pool));
            bool recorded = r.Next(5) != 0, reqM = r.Next(3) == 0, prM = r.Next(2) == 0;
            bool m = RM_DraftprintKernel.Matches(recorded, reqM, prM, req, printLimbs); Steps++;
            bool want = recorded && (!reqM || prM); foreach (int d in req) if (d >= 0 && !printLimbs.Contains(d)) want = false;
            Check(m == want, $"Matches kernel={m} oracle={want} (recorded {recorded}, need monstrous {reqM}/{prM}, req [{string.Join(",", req)}], has [{string.Join(",", printLimbs)}])");
            if (m) DMatch++; else DNoMatch++;
            if (!recorded) Check(!m, "an unrecorded print satisfied a contract");
            // extra features never break a match; dropping one the contract needs does
            foreach (int d in req.Where(x => x >= 0).Distinct()) { var fewer = new HashSet<int>(printLimbs); fewer.Remove(d); Check(!RM_DraftprintKernel.Matches(true, false, true, req, fewer), "a print missing a required limb matched"); }
            if (m) { var more = new HashSet<int>(printLimbs) { 99 }; Check(RM_DraftprintKernel.Matches(recorded, reqM, prM, req, more), "an extra limb broke a match"); }
            // reward
            int per = r.Next(-5, 300), limbs = r.Next(1, 4); bool mon = r.Next(2) == 0; float mf = new[] { -1f, 0f, 1.5f, 2f, 3f }[r.Next(5)], sf = new[] { 0f, 0.5f, 1f, 3f }[r.Next(4)];
            int rew = RM_DraftprintKernel.Reward(per, limbs, mon, mf, sf);
            double pp = per > 0 ? per : 120, spec = pp * (limbs + (mon ? 1 : 0)) * (mon ? (mf > 0 ? mf : 2.0) : 1.0) * sf;
            Check(rew >= 1 && Math.Abs(rew - Math.Max(1, spec)) <= 1.0, $"Reward {rew} vs spec {spec}");
            Check(RM_DraftprintKernel.Reward(per, limbs + 1, mon, mf, sf) >= rew, "more features paid less");
            if (!mon) Check(RM_DraftprintKernel.Reward(per, limbs, true, mf, sf) >= rew, "a monstrous requirement paid less");
            // market factor
            float bv = r.Next(0, 400), pl = r.Next(0, 60), mvf = new[] { 1f, 2f, 3f }[r.Next(3)];
            float mfv = RM_DraftprintKernel.MarketFactor(true, limbs, pl, bv, mon, mvf);
            Check(RM_DraftprintKernel.MarketFactor(false, limbs, pl, bv, mon, mvf) == 1f, "an unrecorded print changed the market value");
            Check(mfv >= 1f && Math.Abs(mfv - (1.0 + limbs * (double)pl / Math.Max(1.0, bv)) * (mon ? mvf : 1.0)) < 1e-3, "market factor");
            // extreme stat vs a double oracle
            int ns = r.Next(0, 5); var bases = new List<float>(); var vals = new List<float>();
            for (int i = 0; i < ns; i++) { float b0 = r.Next(4) == 0 ? 0f : r.Next(1, 40) / 4f; bases.Add(b0); vals.Add(b0 > 0f ? r.Next(0, 80) / 4f : r.Next(-40, 40) / 4f); }
            int ex = RM_DraftprintKernel.ExtremeStat(bases, vals); Steps++;
            int wantEx = -1; double bestS = 0;
            for (int i = 0; i < ns; i++) { double sc = bases[i] > 0.001f ? Math.Abs(Math.Log(Math.Max(vals[i], 0.001f) / (double)bases[i])) : Math.Abs(vals[i] - bases[i]); if (sc > bestS + 1e-6) { bestS = sc; wantEx = i; } }
            if (ex != wantEx) { double sk = ex >= 0 ? (bases[ex] > 0.001f ? Math.Abs(Math.Log(Math.Max(vals[ex], 0.001f) / (double)bases[ex])) : Math.Abs(vals[ex] - bases[ex])) : 0; Check(Math.Abs(sk - bestS) < 1e-5, $"ExtremeStat {ex}, oracle {wantEx} (scores {sk} vs {bestS})"); }
            if (ex >= 0) DExtreme++;
            // worst limb
            int nh = r.Next(0, 6); var isLimb = new List<bool>(); var eff = new List<float>();
            for (int i = 0; i < nh; i++) { isLimb.Add(r.Next(3) != 0); eff.Add(r.Next(0, 12) / 10f); }
            int wl = RM_DraftprintKernel.WorstLimb(isLimb, eff); Steps++;
            int wantW = -1; for (int i = 0; i < nh; i++) if (isLimb[i] && (wantW < 0 || eff[i] < eff[wantW])) wantW = i;
            Check(wl == wantW, $"WorstLimb {wl}, oracle {wantW}"); if (wl >= 0) DWorst++;
            Check(RM_DraftprintKernel.IsAbandonedAttempt(0.3f) && !RM_DraftprintKernel.IsAbandonedAttempt(0.31f), "abandoned-attempt boundary");
            // sampling and provocation
            for (int mk = 0; mk < 16; mk++)
            {
                bool hc = (mk & 1) != 0, taken = (mk & 2) != 0, sp = (mk & 4) != 0, dead = (mk & 8) != 0;
                Check(RM_DraftprintKernel.CanBeSampled(hc, taken, sp, dead) == (hc && !taken && sp && !dead), $"CanBeSampled row {mk}");
            }
            int calls = 0;
            bool prov = RM_DraftprintKernel.MaybeProvokes(r.Next(2) == 0, r.Next(2) == 0, 0f, () => { calls++; return 0f; });
            Check(!prov && calls == 0, "chance 0 provoked or rolled");
            Check(RM_DraftprintKernel.MaybeProvokes(false, false, 1f, () => { calls++; return 1f; }) && calls == 0, "chance 1 must always provoke without a roll");
            Check(!RM_DraftprintKernel.MaybeProvokes(true, false, 1f, () => 0f) && !RM_DraftprintKernel.MaybeProvokes(false, true, 1f, () => 0f), "downed / mad never provoke");
            Check(RM_DraftprintKernel.MaybeProvokes(false, false, 0.35f, () => 0.349f) && !RM_DraftprintKernel.MaybeProvokes(false, false, 0.35f, () => 0.35f), "provoke is strictly below the chance");
            // gestation
            for (int mk = 0; mk < 16; mk++)
            {
                bool mon2 = (mk & 1) != 0, on = (mk & 2) != 0; int lp = (mk & 4) != 0 ? 3 : 0;
                var plan = RM_DraftprintKernel.Plan(mon2, on, lp);
                Check(plan == (mon2 && on && lp > 0 ? GestationPlan.OneLimb : GestationPlan.OrganBatch), $"Plan row {mk}"); DPlans++;
            }
            Check(RM_DraftprintKernel.GestationDone(1f, 1f) && RM_DraftprintKernel.GestationDone(0.9995f, 1f) && !RM_DraftprintKernel.GestationDone(0.998f, 1f), "gestation completes within 0.001 of the max");
            Check(RM_DraftprintKernel.BatchSize(3, 0) == 0 && RM_DraftprintKernel.BatchSize(3, 4) == 3, "BatchSize");
            // the Unfinished
            Check(RM_DraftprintKernel.SpawnDue(100, 100) && !RM_DraftprintKernel.SpawnDue(99, 100) && RM_DraftprintKernel.NearbyAllows(2, 3) && !RM_DraftprintKernel.NearbyAllows(3, 3), "spawner clocks");
            float days = r.Next(1, 30) / 10f; Check(RM_DraftprintKernel.NextSpawn(1000, days) == 1000 + (int)(days * 60000f) && RM_DraftprintKernel.NextSpawn(1000, days) > 1000, "NextSpawn is always later");
            int roll = r.Next(0, 5), leaf = r.Next(0, 6), ps = r.Next(0, 6), lc = RM_DraftprintKernel.LimbCount(roll, leaf, ps);
            Check(lc == Math.Min(roll, Math.Min(leaf, ps)) && lc <= leaf && lc <= ps, "LimbCount");
            Check(RM_DraftprintKernel.FeatureCount(r.Next(-2, 8), 4) is >= 1 and <= 4, "FeatureCount outside [1,pool]");
            return null;
        }

        public static List<string> Draft(int n, int baseSeed) { return Family("draftprint", n, baseSeed, DraftCase); }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("sky", () => Sky(N(3000), S(1))),
                ("coalescence", () => Coal(N(3000), S(1))),
                ("burn", () => Burn(0, 0)),
                ("draftprint", () => Draft(N(4000), S(1))),
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
            Console.WriteLine($"reached: sky natural burns {SNaturalBurns}, forced {SForced}, schedules {SGapWindows}, tells {STells} (first {STellFirst}), coalescences formed {SCoalForm}; coalescence emits {CEmits}, blocked {CBlocked}, passive growths {CPassive}, stage-ups {CStages}, collapses {CCollapses}; draftprint matches {DMatch}/{DMatch + DNoMatch}, extreme {DExtreme}, worst {DWorst}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                if (SNaturalBurns == 0 || SForced == 0 || STellFirst == 0 || SCoalForm == 0 || CEmits == 0 || CBlocked == 0 || CPassive == 0 || CStages == 0 || CCollapses == 0 || DMatch == 0 || DNoMatch == 0 || DExtreme == 0 || DWorst == 0)
                { Console.WriteLine("FAIL a fuzz family never reached one of its key transitions (blind)"); ok = false; }
            }
            Console.WriteLine($"contagion fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
