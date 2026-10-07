// Approach B for FeverWood: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/*.cs):
//   tally    the brood-ransom world tally, boldness multiplier, emergence chance and letter hysteresis, driven by
//            action sequences against a literal spec ledger
//   tank     the prison / display tank: check gate, neglect clock, both escape rolls, occupied flag, breach routing
//   pool     the pool's ambient clock (block respites, Uranium suppression, pressure, Great Emergence), the pending-gift
//            queue and the sentinel counter
//   weights  the ambient limb table and the deep's gift roll (weighted picks, retry-on-no-footprint)
//   units    exhaustive truth tables for the small decisions (trader gates, display-tank gates, charges, ticks)
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.FeverWood.SelfTest
{
    internal static class FeverWoodFuzz
    {
        public static long Cases, Steps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static bool Near(double a, double b, double tol = 1e-5) { return Math.Abs(a - b) <= tol; }

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

        internal struct Act
        {
            public int kind, a, b, c;
            public string[] names;
            public override string ToString() { return names[kind] + "(" + a + "," + b + "," + c + ")"; }
        }

        // ════════════════════════ tally ════════════════════════
        private static readonly string[] TallyNames = { "SetYoung", "FreeDisplayTank", "ReleaseOwnTank", "CasksOnMaps", "CasksInCaravan", "ToggleRansom", "Recompute", "AddOwnTank" };
        public static long LettersFired, TankFrees, BoldnessCapped;

        private static string RunTally(int seed, List<Act> acts, out string digest)
        {
            var r = new Random(seed);
            int nS = 1 + r.Next(5);
            bool[] hasExt = new bool[nS], hasFilter = new bool[nS], listed = new bool[nS];
            int[] per = new int[nS];
            for (int i = 0; i < nS; i++) { hasExt[i] = r.Next(3) != 0; per[i] = r.Next(-1, 4); hasFilter[i] = r.Next(2) == 0; listed[i] = r.Next(2) == 0; }
            float perYoung = r.Next(0, 11) * 0.05f, cap = new[] { 0.5f, 1f, 1.5f, 2f, 3f, 5f }[r.Next(6)];
            float mtbSetting = new[] { 1f, 6f, 12f, 24f, 0.5f }[r.Next(5)];

            var ov = new Dictionary<int, int>(); var freed = new HashSet<int>();
            var dispOcc = Enumerable.Repeat(true, nS).ToArray();
            var own = new List<bool>(); int casksMap = 0, casksCar = 0; bool ransom = true; int level = 0; int tally = 0; long letters = 0;
            // spec ledger
            var sOv = new Dictionary<int, int>(); var sFreed = new HashSet<int>();
            var sDisp = Enumerable.Repeat(true, nS).ToArray(); var sOwn = new List<bool>(); int sCaskMap = 0, sCaskCar = 0; int sLevel = 0; long sLetters = 0;
            Func<int, int> sYoung = s =>
            {
                if (sOv.TryGetValue(s, out int v)) return v;
                if (!hasExt[s]) return 0;
                if (hasFilter[s] && !listed[s]) return 0;
                return per[s] < 0 ? 0 : per[s];
            };
            Func<int, int> kYoung = s =>
            {
                bool has = ov.TryGetValue(s, out int v);
                bool ext = !has && hasExt[s];
                return RM_BroodKernel.SettlementYoung(has, v, ext, ext ? RM_BroodKernel.KeeperYoung(true, per[s], hasFilter[s], listed[s]) : 0);
            };
            Func<int> sTally = () => sOwn.Count(x => x) + sCaskMap + sCaskCar + Enumerable.Range(0, nS).Sum(sYoung);
            int step = 0; string err = null;
            try
            {
                foreach (var a in acts)
                {
                    step++; Steps++;
                    int s = a.a % nS;
                    int before = sTally();
                    bool recompute = true;
                    switch (a.kind)
                    {
                        case 0:
                            ov[s] = RM_BroodKernel.OverrideFor(a.b - 3); sOv[s] = Math.Max(0, a.b - 3);
                            break;
                        case 1:
                            if (RM_TankKernel.TryFreeDisplay(ref dispOcc[s], true))
                            {
                                TankFrees++;
                                if (RM_BroodKernel.FreedTankLowersYoung(!freed.Add(s))) ov[s] = RM_BroodKernel.YoungAfterFreedTank(kYoung(s));
                            }
                            if (sDisp[s])
                            {
                                sDisp[s] = false;
                                if (sFreed.Add(s)) sOv[s] = Math.Max(0, sYoung(s) - 1);
                            }
                            Check(sTally() <= before, "freeing a display tank raised the spec tally");
                            break;
                        case 2:
                            if (own.Count > 0)
                            {
                                int t = a.a % own.Count; bool o = own[t];
                                if (RM_TankKernel.TryRelease(ref o, true)) own[t] = o;
                                if (sOwn[t]) sOwn[t] = false;
                            }
                            break;
                        case 3: casksMap = Math.Max(0, casksMap + a.b - 3); sCaskMap = Math.Max(0, sCaskMap + a.b - 3); break;
                        case 4: casksCar = Math.Max(0, casksCar + a.b - 3); sCaskCar = Math.Max(0, sCaskCar + a.b - 3); break;
                        case 5: ransom = !ransom; break;
                        case 6: break;
                        case 7: own.Add(true); sOwn.Add(true); break;
                    }
                    if (recompute)
                    {
                        // production Recompute: every occupied tank, casks, then every settlement
                        int tanks = 0; foreach (bool o in own) if (RM_TankKernel.CountsInTally(o)) tanks++;
                        long settle = 0; for (int i = 0; i < nS; i++) settle += kYoung(i);
                        tally = RM_BroodKernel.Tally(tanks, casksMap, casksCar, settle);
                        int oldLevel = level;
                        bool fired = RM_BroodKernel.AnnounceStep(ransom, ref level, tally);
                        if (fired) { letters++; LettersFired++; }
                        int spec = sTally();
                        Check(tally == spec, $"tally {tally} != spec {spec}");
                        Check(tally >= 0, "negative tally");
                        // spec level: the number of thresholds <= tally, letter iff it exceeds the previous level
                        int cnt = new[] { 1, 3, 6, 10 }.Count(th => th <= spec);
                        if (ransom) { Check(level == cnt, $"announced level {level} but {cnt} thresholds are cleared at tally {spec}"); Check(fired == (cnt > oldLevel), $"letter {fired} but level {oldLevel}->{cnt}"); }
                        else { Check(level == oldLevel && !fired, "announce ran while the brood ransom is off"); }
                        sLevel = level;
                        // boldness / emergence
                        float b = RM_BroodKernel.Boldness(ransom, perYoung, cap, tally);
                        float b2 = RM_BroodKernel.Boldness(ransom, perYoung, cap, tally + 1);
                        double specB = ransom ? Math.Min(Math.Max(1.0, cap), 1.0 + perYoung * (double)tally) : 1.0;
                        Check(Near(b, specB), $"boldness {b} != spec {specB} (tally {tally} per {perYoung} cap {cap})");
                        Check(b >= 1f && b <= Math.Max(1f, cap) + 1e-6f, "boldness outside [1, cap]");
                        Check(b2 >= b, "boldness fell as the tally rose");
                        if (!ransom || tally == 0) Check(b == 1f, "boldness is not 1 with ransom off or no young");
                        if (ransom && perYoung * tally >= cap - 1f && cap >= 1f && perYoung * tally > 0) { BoldnessCapped++; }
                        float mtb = RM_BroodKernel.EffectiveAmbientMtbHours(mtbSetting, b);
                        float ch = RM_BroodKernel.EmergenceChancePerCheck(mtb);
                        double specMtb = Math.Max(0.1, mtbSetting) / Math.Max(1.0, b);
                        Check(Near(mtb, specMtb, 1e-4), $"effective mtb {mtb} != {specMtb}");
                        Check(ch > 0f && ch <= 1f, "emergence chance outside (0,1]");
                        double specCh = Math.Min(1.0, 1.0 / specMtb);
                        Check(Near(ch, specCh, 1e-4), $"emergence chance {ch} != 1/mtb {specCh}");
                        float chBase = RM_BroodKernel.EmergenceChancePerCheck(RM_BroodKernel.EffectiveAmbientMtbHours(mtbSetting, 1f));
                        Check(ch >= chBase - 1e-6f, "boldness lowered the emergence chance");
                        Check(!(mtb > Math.Max(0.1f, mtbSetting) + 1e-6f), "boldness lengthened the MTB");
                        // mood is monotone and agrees with the thresholds
                        int mood = RM_BroodKernel.MoodIndex(tally);
                        Check(mood >= 0 && mood <= 4 && mood <= RM_BroodKernel.MoodIndex(tally + 1), "mood not monotone");
                        Check(mood == (spec == 0 ? 0 : spec < 3 ? 1 : spec < 6 ? 2 : spec < 10 ? 3 : 4), "mood differs from the threshold table");
                    }
                    // state agreement
                    for (int i = 0; i < nS; i++)
                    {
                        Check(dispOcc[i] == sDisp[i], "display tank occupancy drifted");
                        Check(kYoung(i) == sYoung(i), $"settlement {i} young {kYoung(i)} != spec {sYoung(i)}");
                    }
                    Check(freed.SetEquals(sFreed), "freed-tank set drifted");
                    Check(own.SequenceEqual(sOwn), "own tank occupancy drifted");
                }
                Check(letters >= 0 && sLetters == 0, "ledger");
            }
            catch (Exception e) { err = $"step {step}: {e.Message}"; }
            digest = $"{tally}/{level}/{letters}/{string.Join(",", Enumerable.Range(0, nS).Select(i => kYoung(i)))}";
            return err;
        }

        private static List<Act> GenTally(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(24);
                int kind = k < 5 ? 0 : k < 9 ? 1 : k < 11 ? 2 : k < 14 ? 3 : k < 16 ? 4 : k < 17 ? 5 : k < 21 ? 6 : 7;
                l.Add(new Act { kind = kind, a = r.Next(8), b = r.Next(0, 9), c = 0, names = TallyNames });
            }
            return l;
        }

        public static List<string> Tally(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 7919 + 3);
                var acts = GenTally(r, r.Next(4, 80));
                Cases++;
                string err = RunTally(seed, acts, out string d1);
                if (err == null)
                {
                    RunTally(seed, acts, out string d2);
                    if (d1 != d2) fails.Add($"tally seed {seed}: two replays diverged");
                    continue;
                }
                var min = Shrink(acts, t => RunTally(seed, t, out _) != null);
                fails.Add($"tally seed {seed}: {RunTally(seed, min, out _)} | {string.Join(" ", min)}");
            }
            return fails;
        }

        // ════════════════════════ tank ════════════════════════
        private static readonly string[] TankNames = { "Hours", "Hit", "Enable", "Ransom", "Own", "FreeGizmo", "Release", "Break" };
        public static long NeglectRolls, NeglectEscapes, DamageEscapes, DisplayBreaches, TankDestroyed;

        private static string RunTank(int seed, List<Act> acts, out string digest)
        {
            var r = new Random(seed);
            float[] thrs = { 0f, 0.5f, 1f, 1.5f, 2f, 3f };
            float thr = thrs[r.Next(thrs.Length)];
            float neglectMtb = r.Next(1, 9);
            float[] risks = { 0.005f, 0.25f, 0.5f, 1f, 2f, 4f };
            float risk = risks[r.Next(risks.Length)];
            float[] dthr = { 0.25f, 0.5f, 0.75f };
            float dmgThr = dthr[r.Next(3)];
            float[] dch = { 0f, 0.1f, 0.5f, 1f, 3f };
            float dmgChance = dch[r.Next(dch.Length)];
            int maxHp = new[] { 64, 128, 256, 0 }[r.Next(4)];
            bool displayProps = r.Next(2) == 0;
            bool foreignOwner = displayProps && r.Next(2) == 0;
            bool hasOwner = displayProps && r.Next(5) != 0 ? true : r.Next(2) == 0;
            bool ownerIsPlayer = !foreignOwner;
            var rng = new Random(seed ^ 0x5bd1e995);

            // kernel-driven state
            int now = r.Next(0, 50) * 2500; int unfedSince = -1; bool occupied = true, enabled = true, ransom = true, destroyed = false;
            bool fedNow = true; int released = 0, escapedPawns = 0, freedYoung = 0;
            // spec ledger
            long sStart = -1; bool sOccupied = true; bool sDestroyed = false; int sReleased = 0, sEscaped = 0, sFreed = 0;
            long hours = 0;
            int step = 0; string err = null;
            Func<bool> sForeign = () => displayProps && hasOwner && !ownerIsPlayer;
            Action destroy = () => { destroyed = true; sDestroyed = true; TankDestroyed++; };
            Action<bool> escape = breached =>
            {
                // Escape(): a foreign display tank under the ransom frees its young and vanishes; otherwise the occupant gets out
                if (RM_TankKernel.EscapeFreesDisplayYoung(RM_TankKernel.IsForeignDisplay(displayProps, hasOwner, ownerIsPlayer), ransom))
                {
                    if (RM_TankKernel.TryFreeDisplay(ref occupied, true)) { freedYoung++; DisplayBreaches++; }
                    if (sOccupied) { sOccupied = false; sFreed++; }
                    destroy();
                    return;
                }
                destroy(); escapedPawns++; sEscaped++;
            };
            try
            {
                foreach (var a in acts)
                {
                    step++; Steps++;
                    switch (a.kind)
                    {
                        case 0: // Hours(n, fedBits)
                            for (int h = 0; h < 1 + a.a % 12 && !destroyed; h++)
                            {
                                now += 2500; hours++;
                                // off-grid ticks between hours never run
                                int off = 1 + rng.Next(2499);
                                Check(!RM_TankKernel.RunsThisTick(true, true, false, now + off), "ran on an off-hour tick");
                                bool run = enabled && occupied && !RM_TankKernel.IsForeignDisplay(displayProps, hasOwner, ownerIsPlayer);
                                Check(RM_TankKernel.RunsThisTick(enabled, occupied, RM_TankKernel.IsForeignDisplay(displayProps, hasOwner, ownerIsPlayer), now) == run, "RunsThisTick != spec gate");
                                bool sRun = enabled && sOccupied && !sForeign();
                                if (!run) continue;
                                bool fed = ((a.b >> h) & 1) != 0;
                                fedNow = fed;
                                bool due = RM_TankKernel.NeglectStep(ref unfedSince, fed, now, thr);
                                // spec
                                bool sDue;
                                if (fed) { sStart = -1; sDue = false; }
                                else if (sStart < 0) { sStart = now; sDue = false; }
                                else sDue = (now - sStart) >= (long)(thr * 60000f);
                                Check(due == sDue, $"neglect due {due} != spec {sDue} (unfedSince {unfedSince}, spec {sStart}, now {now}, thr {thr})");
                                Check((unfedSince < 0) == (sStart < 0) && (unfedSince < 0 || unfedSince == sStart), "unfed clock drifted");
                                if (fed) Check(!due, "a fed tank rolled for neglect");
                                if (due)
                                {
                                    NeglectRolls++;
                                    float mtbDays = RM_TankKernel.NeglectMtbDays(neglectMtb, risk);
                                    Check(Near(mtbDays, neglectMtb * Math.Max(0.01, risk), 1e-4), "neglect MTB != base * max(0.01,risk)");
                                    Check(mtbDays <= RM_TankKernel.NeglectMtbDays(neglectMtb, risk * 2) + 1e-5f, "a lower risk setting lengthened the MTB");
                                    // adversarial roll: one hour in four hits regardless of probability
                                    if (rng.Next(4) == 0) { NeglectEscapes++; escape(false); }
                                }
                            }
                            break;
                        case 1: // Hit(hpPercent)
                            {
                                int mhp = maxHp;
                                int hp = mhp > 0 ? (int)Math.Round(mhp * (a.a % 101) / 100.0) : (a.a % 3 == 0 ? 0 : 1);
                                bool armed = RM_TankKernel.DamageArmed(enabled, occupied, hp, mhp, dmgThr);
                                double lost = mhp > 0 ? (mhp - hp) / (double)mhp : (1.0 - hp);
                                bool sArmed = enabled && sOccupied && lost >= dmgThr - 1e-9;
                                if (Math.Abs(lost - dmgThr) > 1e-4) Check(armed == sArmed, $"damage armed {armed} != spec {sArmed} (hp {hp}/{mhp}, thr {dmgThr})");
                                float p = RM_TankKernel.DamageEscapeChance(dmgChance, risk);
                                Check(p >= 0f && p <= 1f, "damage escape chance outside [0,1]");
                                Check(Near(p, Math.Min(1.0, Math.Max(0.0, dmgChance / Math.Max(0.01, risk))), 1e-4), "damage escape chance != clamp(chance/risk)");
                                Check(p >= RM_TankKernel.DamageEscapeChance(dmgChance, risk * 2) - 1e-6f, "a lower risk setting lowered the escape chance");
                                if (dmgChance == 0f) Check(p == 0f, "zero per-hit chance escapes");
                                if (armed && !destroyed && rng.NextDouble() < p) { DamageEscapes++; escape(false); }
                            }
                            break;
                        case 2: enabled = !enabled; break;
                        case 3: ransom = !ransom; break;
                        case 4: // owner flips (a display tank bought / seized)
                            if (displayProps) { ownerIsPlayer = !ownerIsPlayer; hasOwner = true; }
                            break;
                        case 5: // FreeDisplayYoung gizmo / breach: idempotent
                            {
                                bool acted = RM_TankKernel.TryFreeDisplay(ref occupied, !destroyed);
                                if (acted) freedYoung++;
                                if (!sDestroyed && sOccupied) { sOccupied = false; sFreed++; }
                                Check(acted == (sFreed > 0 && (freedYoung == sFreed)) || !acted || freedYoung == sFreed, "free bookkeeping");
                            }
                            break;
                        case 6: // Return to the deep
                            {
                                bool acted = RM_TankKernel.TryRelease(ref occupied, !destroyed);
                                if (acted) released++;
                                if (!sDestroyed && sOccupied) { sOccupied = false; sReleased++; }
                            }
                            break;
                        case 7: // broken outright (KillFinalize)
                            if (!destroyed)
                            {
                                bool frees = RM_TankKernel.DestroyFreesDisplayYoung(true, occupied, displayProps, true, hasOwner, ownerIsPlayer, ransom, enabled);
                                bool sFrees = sOccupied && displayProps && hasOwner && !ownerIsPlayer && ransom && enabled;
                                Check(frees == sFrees, $"destroy frees {frees} != spec {sFrees}");
                                if (frees) { if (RM_TankKernel.TryFreeDisplay(ref occupied, true)) freedYoung++; sOccupied = false; sFreed++; }
                                destroy();
                            }
                            break;
                    }
                    // ---- invariants after every step ----
                    Check(occupied == sOccupied, $"occupied {occupied} != spec {sOccupied}");
                    Check(destroyed == sDestroyed, "destroyed flag drifted");
                    Check(escapedPawns == sEscaped && freedYoung == sFreed && released == sReleased, "release/escape/free counters drifted");
                    Check(escapedPawns + freedYoung + released <= 1 + 0, $"occupant left the tank {escapedPawns + freedYoung + released} times");
                    Check(RM_TankKernel.CountsInTally(occupied) == sOccupied, "tally membership != occupied");
                    if (destroyed) Check(escapedPawns <= 1, "two escapees from one tank");
                    Check(RM_TankKernel.GiftRolls(a.c) >= 1, "gift rolls below 1");
                }
            }
            catch (Exception e) { err = $"step {step}: {e.Message}"; }
            digest = $"{now}/{unfedSince}/{occupied}/{destroyed}/{escapedPawns}/{freedYoung}/{released}";
            return err;
        }

        private static List<Act> GenTank(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(30);
                int kind = k < 12 ? 0 : k < 18 ? 1 : k < 20 ? 2 : k < 21 ? 3 : k < 23 ? 4 : k < 25 ? 5 : k < 27 ? 6 : 7;
                if (kind == 7 && r.Next(3) != 0) kind = 0;
                // fed bits biased toward long unfed runs so the neglect threshold is reached
                int bits = r.Next(3) == 0 ? r.Next(1 << 12) : (r.Next(2) == 0 ? 0 : 0xFFF);
                l.Add(new Act { kind = kind, a = kind == 0 ? r.Next(12) : r.Next(101), b = bits, c = r.Next(-2, 5), names = TankNames });
            }
            return l;
        }

        public static List<string> Tank(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 7919 + 5);
                var acts = GenTank(r, r.Next(4, 70));
                Cases++;
                string err = RunTank(seed, acts, out string d1);
                if (err == null)
                {
                    RunTank(seed, acts, out string d2);
                    if (d1 != d2) fails.Add($"tank seed {seed}: two replays diverged");
                    continue;
                }
                var min = Shrink(acts, t => RunTank(seed, t, out _) != null);
                fails.Add($"tank seed {seed}: {RunTank(seed, min, out _)} | {string.Join(" ", min)}");
            }
            return fails;
        }

        // ════════════════════════ pool ════════════════════════
        private static readonly string[] PoolNames = { "Hours", "Retreat", "Sever", "Suppress", "DriveOff", "Force", "Kill", "Install", "SentinelUp", "SentinelDown", "Schedule", "PollGifts", "Toggle", "Pools" };
        public static long Ordinary, Great, Forced, Suppressions, GiftsDelivered, Hushes, Restores;

        private static string RunPool(int seed, List<Act> acts, out string digest)
        {
            var r = new Random(seed);
            var rng = new Random(seed ^ 0x2545F491);
            int sizeThr = r.Next(0, 8), pressThr = r.Next(-1, 6);
            float greatSetting = new[] { -0.5f, 0f, 0.02f, 0.5f, 1f, 3f }[r.Next(6)];
            int now = r.Next(0, 40) * 2500;
            bool bestiary = true, greatOn = true, killed = false; int pools = r.Next(0, 12);
            int blocked = 0; int pressure = 0; int sentinel = 0; bool hushed = false;
            long sBlocked = 0; int sPressure = 0; int sSentinel = 0; int hushEvents = 0, restoreEvents = 0;
            var gTicks = new List<int>(); var gCells = new List<int>(); var gRolls = new List<int>();
            var sGifts = new List<(int tick, int cell, int rolls)>(); int cellSeq = 0; var delivered = new HashSet<int>();
            int step = 0; string err = null;
            try
            {
                foreach (var a in acts)
                {
                    step++; Steps++;
                    switch (a.kind)
                    {
                        case 0:
                            for (int h = 0; h < 1 + a.a % 10; h++)
                            {
                                now += 2500;
                                bool open = RM_PoolKernel.AmbientOpen(bestiary, killed, now, blocked);
                                bool sOpen = bestiary && !killed && now >= sBlocked;
                                Check(open == sOpen, $"AmbientOpen {open} != spec {sOpen} (now {now}, blocked {blocked})");
                                if (!open || pools == 0) continue;
                                bool mtbHit = ((a.b >> h) & 1) != 0;
                                if (!mtbHit) continue;
                                bool eligible = RM_PoolKernel.GreatEligible(pools, sizeThr, pressure, pressThr);
                                bool sElig = pools >= Math.Max(1, sizeThr) && sPressure >= Math.Max(0, pressThr);
                                Check(eligible == sElig, $"GreatEligible {eligible} != spec {sElig} (pools {pools}/{sizeThr}, pressure {pressure}/{pressThr})");
                                bool greatHit = rng.NextDouble() < RM_PoolKernel.GreatChance(greatSetting);
                                AmbientKind kind = RM_PoolKernel.Escalate(greatOn, eligible, greatHit);
                                if (kind == AmbientKind.Great)
                                {
                                    Great++;
                                    Check(greatOn && sElig, "a Great Emergence fired while ineligible or disabled");
                                    Check(now >= sBlocked, "a Great Emergence fired inside a respite");
                                    sPressure = 0;
                                }
                                else { Ordinary++; Check(now >= sBlocked, "an ordinary emergence fired inside a respite"); sPressure++; }
                                pressure = RM_PoolKernel.PressureAfter(pressure, kind);
                                if (kind == AmbientKind.Great) Check(pressure == 0, "Great emergence did not spend the pressure");
                            }
                            break;
                        case 1:
                        case 2:
                        case 4:
                            {
                                // Retreat / Sever / DriveOff: all extend the same clock; huge values must saturate, never wrap
                                long ticks = a.a == 0 ? int.MaxValue - now + (long)a.b : a.a * 1000L + a.b % 5000;
                                int t = (int)Math.Min(ticks, int.MaxValue);
                                int pre = blocked;
                                blocked = RM_PoolKernel.Extend(blocked, RM_PoolKernel.Until(now, t));
                                sBlocked = Math.Max(sBlocked, Math.Min((long)now + t, int.MaxValue));
                                Check(blocked >= pre, "a respite shortened the block");
                            }
                            break;
                        case 3: // Suppress(days*10)
                            {
                                float days = (a.a % 301) / 10f;
                                int ticks = RM_PoolKernel.SuppressionTicks(days);
                                Suppressions++;
                                Check(ticks >= 6000, "suppression shorter than the 0.1 day floor");
                                Check(Near(ticks, Math.Round(Math.Max(0.1f, days) * 60000.0), 1.0), $"SuppressionTicks({days}) = {ticks}");
                                int pre = blocked;
                                blocked = RM_PoolKernel.Extend(blocked, RM_PoolKernel.Until(now, ticks));
                                sBlocked = Math.Max(sBlocked, (long)now + ticks);
                                Check(blocked >= pre, "suppression shortened the block");
                                Check(blocked >= now + ticks - 1, "suppression shorter than its duration");
                            }
                            break;
                        case 5: // ForceEmergenceNear: ignores the block, respects bestiary and kill
                            if (bestiary && !killed && pools > 0) { pressure = RM_PoolKernel.PressureAfterForced(pressure); sPressure += 2; Forced++; }
                            break;
                        case 6: killed = true; break;
                        case 7: killed = false; break;
                        case 8:
                            sentinel = RM_PoolKernel.SentinelUp(sentinel, out bool hush); sSentinel++;
                            if (hush) { hushEvents++; Hushes++; hushed = true; }
                            break;
                        case 9:
                            sentinel = RM_PoolKernel.SentinelDown(sentinel, out bool restore); sSentinel = Math.Max(0, sSentinel - 1);
                            if (restore) { restoreEvents++; Restores++; hushed = false; }
                            break;
                        case 10: // ScheduleDeepGift
                            {
                                int tick = now + 600 + a.a % 1600; int cell = cellSeq++; int rolls = Math.Max(1, a.b % 3);
                                gTicks.Add(tick); gCells.Add(cell); gRolls.Add(rolls); sGifts.Add((tick, cell, rolls));
                            }
                            break;
                        case 11: // PollGifts at now + dt (a third of polls land exactly on the earliest pending due tick)
                            {
                                now += a.a * 250;
                                var pend = sGifts.Where(g => !delivered.Contains(g.cell)).Select(g => g.tick).ToList();
                                if (a.b % 3 == 0 && pend.Count > 0 && pend.Min() > now) now = pend.Min();
                                var due = RM_BroodKernel.CollectDue(gTicks, gCells, gRolls, now);
                                var expect = sGifts.Where(g => g.tick <= now && !delivered.Contains(g.cell)).ToList();
                                Check(due.Count == expect.Count, $"{due.Count} gifts due, spec {expect.Count} at {now}");
                                foreach (var d in due)
                                {
                                    var g = sGifts.First(x => x.cell == d.Key);
                                    Check(g.tick <= now, "a gift was delivered early");
                                    Check(delivered.Add(d.Key), "a gift was delivered twice");
                                    Check(d.Value == g.rolls, "a gift lost its roll count");
                                    GiftsDelivered++;
                                }
                                Check(gTicks.Count == gCells.Count && gCells.Count == gRolls.Count, "gift lists drifted apart");
                                Check(gTicks.Count == sGifts.Count - delivered.Count, "undelivered gift count drifted");
                            }
                            break;
                        case 12:
                            if (a.a % 3 == 0) bestiary = !bestiary; else if (a.a % 3 == 1) greatOn = !greatOn; else { sizeThr = a.b % 8; pressThr = a.b % 7 - 1; }
                            break;
                        case 13: pools = a.a % 14; break;
                    }
                    // ---- invariants after every step ----
                    Check(Math.Min(sBlocked, int.MaxValue) == blocked, $"blocked {blocked} != spec {sBlocked}");
                    Check(pressure == sPressure && pressure >= 0, $"pressure {pressure} != spec {sPressure}");
                    Check(sentinel == sSentinel && sentinel >= 0, $"sentinel {sentinel} != spec {sSentinel}");
                    Check(hushed == (sentinel > 0), "chorus hushed state != sentinel count > 0");
                    Check(restoreEvents <= hushEvents && hushEvents - restoreEvents == (hushed ? 1 : 0), "hush / restore events do not alternate");
                }
                // a late save: the lists survive the repair intact
                var t2 = new List<int>(gTicks); var c2 = new List<int>(gCells); var r2 = new List<int>(gRolls);
                RM_BroodKernel.RepairQueues(ref t2, ref c2, ref r2);
                Check(t2.SequenceEqual(gTicks) && c2.SequenceEqual(gCells) && r2.SequenceEqual(gRolls), "RepairQueues altered consistent lists");
            }
            catch (Exception e) { err = $"step {step}: {e.Message}"; }
            digest = $"{now}/{blocked}/{pressure}/{sentinel}/{gTicks.Count}";
            return err;
        }

        private static List<Act> GenPool(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(40);
                int kind = k < 14 ? 0 : k < 16 ? 1 : k < 18 ? 2 : k < 20 ? 3 : k < 21 ? 4 : k < 23 ? 5 : k < 24 ? 6 : k < 25 ? 7 : k < 28 ? 8 : k < 31 ? 9 : k < 33 ? 10 : k < 36 ? 11 : k < 38 ? 12 : 13;
                int hits = r.Next(3) == 0 ? r.Next(1 << 10) : (r.Next(2) == 0 ? 0x3FF : 0);
                int a = kind == 0 ? r.Next(10) : kind == 1 || kind == 2 || kind == 4 ? (r.Next(12) == 0 ? 0 : r.Next(1, 3000)) : kind == 11 ? r.Next(0, 40) : r.Next(400);
                l.Add(new Act { kind = kind, a = a, b = kind == 0 ? hits : r.Next(100000), c = 0, names = PoolNames });
            }
            return l;
        }

        public static List<string> Pool(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 7919 + 7);
                var acts = GenPool(r, r.Next(4, 90));
                Cases++;
                string err = RunPool(seed, acts, out string d1);
                if (err == null)
                {
                    RunPool(seed, acts, out string d2);
                    if (d1 != d2) fails.Add($"pool seed {seed}: two replays diverged");
                    continue;
                }
                var min = Shrink(acts, t => RunPool(seed, t, out _) != null);
                fails.Add($"pool seed {seed}: {RunPool(seed, min, out _)} | {string.Join(" ", min)}");
            }
            // load-time repair: any mismatch yields consistent lists
            var rr = new Random(baseSeed + 99);
            for (int k = 0; k < 200; k++)
            {
                Cases++; Steps++;
                var t = rr.Next(2) == 0 ? null : Enumerable.Range(0, rr.Next(4)).ToList();
                var c = rr.Next(2) == 0 ? null : Enumerable.Range(0, rr.Next(4)).ToList();
                var ro = rr.Next(2) == 0 ? null : Enumerable.Range(0, rr.Next(4)).ToList();
                bool consistent = t != null && c != null && t.Count == c.Count;
                int n0 = consistent ? t.Count : 0;
                RM_BroodKernel.RepairQueues(ref t, ref c, ref ro);
                if (t == null || c == null || ro == null || t.Count != c.Count || t.Count != ro.Count) fails.Add("RepairQueues left the lists unequal or null");
                else if (t.Count != n0) fails.Add("RepairQueues changed the length of consistent lists");
            }
            return fails;
        }

        // ════════════════════════ weights ════════════════════════
        public static long Picks, Retries;

        public static List<string> Weights(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k;
                Cases++;
                try { WeightCase(seed); } catch (Exception e) { fails.Add($"weights seed {seed}: {e.Message}"); }
            }
            try { WeightUnits(); } catch (Exception e) { fails.Add("weights units: " + e.Message); }
            Cases++;
            return fails;
        }

        private static void WeightCase(int seed)
        {
            var r = new Random(seed);
            // ---- the ambient limb table: 5 rows, porter may be skipped, snare/lash scaled by boldness ----
            float[] baseW = { 40f, 25f, 20f, 10f, 8f };
            float bold = 1f + r.Next(0, 9) * 0.25f;
            bool porterAnger = r.Next(2) == 0;
            var w = new float[5]; var skip = new bool[5];
            for (int i = 0; i < 5; i++) { w[i] = RM_BroodKernel.AmbientWeight(i == 1 || i == 2, baseW[i], bold); skip[i] = porterAnger && i == 3; }
            double total = 0; for (int i = 0; i < 5; i++) if (!skip[i]) total += w[i];
            const int N = 4096;
            var hits = new int[5];
            for (int s = 0; s < N; s++)
            {
                Steps++; Picks++;
                float roll = (float)((s + 0.5) / N * total);
                int p = RM_BroodKernel.PickLimb(w, skip, roll);
                Check(p >= 0 && p < 5, "PickLimb found nothing in a non-empty table");
                Check(!skip[p], "PickLimb returned a skipped row");
                hits[p]++;
            }
            for (int i = 0; i < 5; i++)
            {
                double want = skip[i] ? 0 : w[i] / total;
                Check(Math.Abs(hits[i] / (double)N - want) < 2.0 / N + 1e-9, $"limb {i} frequency {hits[i] / (double)N:F4} != weight share {want:F4}");
            }
            if (porterAnger) Check(hits[3] == 0, "the angered porter was still rolled");
            // boldness only moves weight toward snare and lash
            double shareLow = (25 + 20) / (double)(40 + 25 + 20 + (porterAnger ? 0 : 10) + 8);
            double shareNow = (w[1] + w[2]) / total;
            Check(shareNow >= shareLow - 1e-9, "boldness lowered the snare/lash share");
            Check(RM_BroodKernel.PickLimb(w, Enumerable.Repeat(true, 5).ToArray(), 1f) == -1, "all rows skipped must pick nothing");
            Check(RM_BroodKernel.PickLimb(new float[] { 0f, 0f }, null, 0f) == -1, "all-zero table must pick nothing");
            // a zero row is never picked, even on a roll of exactly 0
            int z = RM_BroodKernel.PickLimb(new float[] { 0f, 5f, 0f, 3f }, null, 0f);
            Check(z == 1, $"roll 0 landed on row {z}, a zero-weight row or the wrong one");

            // ---- the gift roll: rows with weight 0 are not candidates; a row with no footprint drops out ----
            int rows = r.Next(1, 8);
            var gw = new float[rows]; var placeable = new bool[rows];
            for (int i = 0; i < rows; i++) { gw[i] = r.Next(4) == 0 ? 0f : r.Next(1, 20); placeable[i] = r.Next(3) != 0; }
            var rolls = new Random(seed + 17);
            var tried = new List<int>();
            int got = RM_BroodKernel.RollGift(gw, i => { tried.Add(i); Retries++; return placeable[i]; }, () => (float)rolls.NextDouble());
            bool any = Enumerable.Range(0, rows).Any(i => gw[i] > 0f && placeable[i]);
            Check((got >= 0) == any, $"RollGift returned {got} but a placeable row exists = {any}");
            if (got >= 0) Check(gw[got] > 0f && placeable[got], "RollGift placed a zero-weight or unplaceable row");
            Check(tried.Distinct().Count() == tried.Count, "a row was tried twice");
            Check(tried.All(i => gw[i] > 0f), "a zero-weight row was tried");
            if (!any) Check(tried.Count == gw.Count(x => x > 0f), "RollGift gave up before trying every candidate");
            // frequency: all placeable, distribution proportional (large sample, wide tolerance)
            if (rows >= 2 && gw.Sum() > 0)
            {
                var cnt = new int[rows]; var rr = new Random(seed + 23); int M = 6000;
                for (int s = 0; s < M; s++) { Steps++; cnt[RM_BroodKernel.RollGift(gw, i => true, () => (float)rr.NextDouble())]++; }
                double sum = gw.Sum();
                for (int i = 0; i < rows; i++) Check(Math.Abs(cnt[i] / (double)M - gw[i] / sum) < 0.035, $"gift row {i} frequency {cnt[i] / (double)M:F3} != share {gw[i] / sum:F3}");
                // one unplaceable row: the rest keep their relative proportions
                int bad = Enumerable.Range(0, rows).FirstOrDefault(i => gw[i] > 0f);
                var cnt2 = new int[rows]; int placed = 0;
                for (int s = 0; s < M; s++) { Steps++; int g = RM_BroodKernel.RollGift(gw, i => i != bad, () => (float)rr.NextDouble()); if (g >= 0) { cnt2[g]++; placed++; } }
                double rest = sum - gw[bad];
                if (rest > 0) { Check(cnt2[bad] == 0, "the blocked row was placed"); for (int i = 0; i < rows; i++) if (i != bad) Check(Math.Abs(cnt2[i] / (double)placed - gw[i] / rest) < 0.035, $"after dropping row {bad}, row {i} share {cnt2[i] / (double)placed:F3} != {gw[i] / rest:F3}"); }
                else Check(placed == 0, "nothing placeable yet something was placed");
            }
        }

        private static void WeightUnits()
        {
            Check(RM_BroodKernel.GiftWeight(4f, true, 0f) == 0f && RM_BroodKernel.GiftWeight(4f, true, -2f) == 0f, "a zero or negative multiplier must zero the weight");
            Check(RM_BroodKernel.GiftWeight(4f, false, 99f) == 4f && RM_BroodKernel.GiftWeight(4f, true, 2.5f) == 10f, "GiftWeight multiplier handling");
            Check(RM_BroodKernel.PickByWeight(new float[0], new List<int>(), 0.5f) == -1, "no candidates");
            Check(RM_BroodKernel.PickByWeight(new float[] { 1f, 1f }, new List<int> { 0, 1 }, 1f) == 1, "u = 1 must fall to the last candidate");
        }

        // ════════════════════════ units ════════════════════════
        public static List<string> Units()
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                // KeeperYoung / SettlementYoung
                for (int m = 0; m < 16; m++)
                {
                    bool exists = (m & 1) != 0, filt = (m & 2) != 0, listed = (m & 4) != 0; int per = (m & 8) != 0 ? -2 : 3;
                    int want = !exists ? 0 : (filt && !listed) ? 0 : Math.Max(0, per);
                    Check(RM_BroodKernel.KeeperYoung(exists, per, filt, listed) == want, $"KeeperYoung row {m}"); Steps++;
                }
                Check(RM_BroodKernel.SettlementYoung(true, 0, true, 9) == 0 && RM_BroodKernel.SettlementYoung(false, 0, true, 9) == 9 && RM_BroodKernel.SettlementYoung(false, 5, false, 9) == 0, "SettlementYoung precedence: an override of 0 beats the extension");
                Check(RM_BroodKernel.Tally(1, 2, 3, 4) == 10 && RM_BroodKernel.Tally(0, 0, 0, 0) == 0 && RM_BroodKernel.Tally(int.MaxValue, 5, 5, 5) == int.MaxValue, "Tally sum / saturation");
                Check(RM_BroodKernel.FreedTankLowersYoung(false) && !RM_BroodKernel.FreedTankLowersYoung(true), "a tank freed twice lowers the town once");
                Check(RM_BroodKernel.YoungAfterFreedTank(0) == 0 && RM_BroodKernel.YoungAfterFreedTank(3) == 2, "YoungAfterFreedTank");
                // Boldness table
                Check(RM_BroodKernel.Boldness(false, 0.5f, 5f, 99) == 1f && RM_BroodKernel.Boldness(true, 0.1f, 2f, 0) == 1f, "Boldness off / zero young");
                Check(Near(RM_BroodKernel.Boldness(true, 0.1f, 2f, 4), 1.4) && RM_BroodKernel.Boldness(true, 0.1f, 2f, 50) == 2f, "Boldness slope / cap");
                Check(RM_BroodKernel.Boldness(true, 0.1f, 0.2f, 50) == 1f, "a cap below 1 must still be 1");
                Check(RM_BroodKernel.Boldness(true, -1f, 3f, 5) == 1f, "a negative slope must not lower boldness below 1");
                // mood and thresholds, announce closed form exhaustively
                int[] th = { 1, 3, 6, 10 };
                for (int L = 0; L <= 4; L++) for (int t = 0; t <= 14; t++)
                {
                    int lv = L; bool fired = RM_BroodKernel.AnnounceStep(true, ref lv, t);
                    int cnt = th.Count(x => x <= t);
                    Check(lv == cnt && fired == (cnt > L), $"AnnounceStep level {L} tally {t} -> {lv} fired {fired} (want {cnt}, {cnt > L})"); Steps++;
                    int lv2 = L; Check(!RM_BroodKernel.AnnounceStep(false, ref lv2, t) && lv2 == L, "AnnounceStep ran while disabled");
                }
                // emergence chance boundary: mtb 1 hour is certain, 2 hours is one half, 0.05 h clamps to 1
                Check(RM_BroodKernel.EmergenceChancePerCheck(1f) == 1f && Near(RM_BroodKernel.EmergenceChancePerCheck(2f), 0.5) && RM_BroodKernel.EmergenceChancePerCheck(0.05f) == 1f && Near(RM_BroodKernel.EmergenceChancePerCheck(6f), 1 / 6.0), "EmergenceChancePerCheck");
                Check(RM_BroodKernel.EffectiveAmbientMtbHours(6f, 2f) == 3f && RM_BroodKernel.EffectiveAmbientMtbHours(6f, 0.5f) == 6f && RM_BroodKernel.EffectiveAmbientMtbHours(0f, 1f) == 0.1f, "EffectiveAmbientMtbHours (boldness below 1 must not stretch it)");
                // trader gates
                Check(RM_BroodKernel.StockChance(-1f, 0.3f) == 0.3f && RM_BroodKernel.StockChance(0.8f, 0.3f) == 0.8f && RM_BroodKernel.StockChance(0f, 0.3f) == 0f && RM_BroodKernel.StockChance(7f, 0f) == 1f && RM_BroodKernel.StockChance(-1f, -3f) == 0f, "StockChance fixed/setting/clamp (a fixed 0 is fixed, not 'use settings')");
                Check(RM_BroodKernel.StocksFor(0, false, false) && RM_BroodKernel.StocksFor(0, true, false) && !RM_BroodKernel.StocksFor(2, false, false) && !RM_BroodKernel.StocksFor(2, true, false) && RM_BroodKernel.StocksFor(2, true, true), "StocksFor");
                Check(!RM_BroodKernel.StocksCask(false, true) && !RM_BroodKernel.StocksCask(true, false) && RM_BroodKernel.StocksCask(true, true), "StocksCask");
                for (int m = 0; m < 32; m++)
                {
                    bool hs = (m & 1) != 0, hf = (m & 2) != 0, fm = (m & 4) != 0, ne = (m & 8) != 0, nm = (m & 16) != 0;
                    bool want = hs && hf && fm && (ne || nm);
                    Check(RM_BroodKernel.DisplayTankApplies(hs, hf, fm, ne, nm) == want, $"DisplayTankApplies row {m}"); Steps++;
                }
                for (int m = 0; m < 32; m++)
                {
                    bool a = (m & 1) != 0, b = (m & 2) != 0, c = (m & 4) != 0, d = (m & 8) != 0, e = (m & 16) != 0;
                    Check(RM_BroodKernel.PlaceDisplayTank(a, b, c, d, e) == (a && b && c && d && !e), $"PlaceDisplayTank row {m}"); Steps++;
                }
                // tank tables
                Check(RM_TankKernel.GiftRolls(0) == 1 && RM_TankKernel.GiftRolls(-4) == 1 && RM_TankKernel.GiftRolls(2) == 2, "GiftRolls floor");
                for (int now = 0; now < 8 * 2500; now += 125)
                    Check(RM_TankKernel.RunsThisTick(true, true, false, now) == (now % 2500 == 0), "RunsThisTick hourly gate");
                Check(!RM_TankKernel.RunsThisTick(false, true, false, 0) && !RM_TankKernel.RunsThisTick(true, false, false, 0) && !RM_TankKernel.RunsThisTick(true, true, true, 0), "RunsThisTick inert cases");
                Check(RM_TankKernel.ProductionWindow(10000, 9000) == 1000 && RM_TankKernel.ProductionWindow(10000, 0) == 2500 && RM_TankKernel.ProductionWindow(10000, 7500) == 2500, "ProductionWindow");
                Check(RM_TankKernel.LostFraction(0, 0) == 0f - 0f + (1f - 0f) && RM_TankKernel.LostFraction(1, 0) == 0f && RM_TankKernel.LostFraction(50, 100) == 0.5f, "LostFraction with zero max HP");
                Check(RM_TankKernel.DamageArmed(true, true, 50, 100, 0.5f) && !RM_TankKernel.DamageArmed(true, true, 51, 100, 0.5f) && !RM_TankKernel.DamageArmed(true, false, 0, 100, 0.5f) && !RM_TankKernel.DamageArmed(false, true, 0, 100, 0.5f), "DamageArmed boundary at exactly the threshold");
                Check(RM_TankKernel.DestroyFreesDisplayYoung(true, true, true, true, true, false, true, true), "a broken foreign display tank frees its young");
                Check(!RM_TankKernel.DestroyFreesDisplayYoung(true, true, true, true, true, true, true, true) && !RM_TankKernel.DestroyFreesDisplayYoung(false, true, true, true, true, false, true, true) && !RM_TankKernel.DestroyFreesDisplayYoung(true, false, true, true, true, false, true, true) && !RM_TankKernel.DestroyFreesDisplayYoung(true, true, false, true, true, false, true, true), "DestroyFreesDisplayYoung negatives");
                Check(RM_TankKernel.IsForeignDisplay(true, true, false) && !RM_TankKernel.IsForeignDisplay(true, true, true) && !RM_TankKernel.IsForeignDisplay(true, false, false) && !RM_TankKernel.IsForeignDisplay(false, true, false), "IsForeignDisplay");
                bool occ = false; Check(!RM_TankKernel.TryFreeDisplay(ref occ, true) && !occ && !RM_TankKernel.TryRelease(ref occ, true), "an empty tank frees and releases nothing");
                occ = true; Check(!RM_TankKernel.TryRelease(ref occ, false) && occ && RM_TankKernel.TryRelease(ref occ, true) && !occ, "TryRelease needs a spawned tank");
                // pool tables
                Check(RM_PoolKernel.Until(int.MaxValue - 5, 100) == int.MaxValue && RM_PoolKernel.Until(10, 5) == 15, "Until saturates instead of wrapping");
                Check(RM_PoolKernel.Extend(10, 5) == 10 && RM_PoolKernel.Extend(10, 15) == 15, "Extend never shortens");
                Check(RM_PoolKernel.SuppressionTicks(5f) == 300000 && RM_PoolKernel.SuppressionTicks(0.5f) == 30000 && RM_PoolKernel.SuppressionTicks(0f) == 6000 && RM_PoolKernel.SuppressionTicks(1e9f) == int.MaxValue, "SuppressionTicks");
                Check(RM_PoolKernel.ChargesTaken(3, 5) == 3 && RM_PoolKernel.ChargesTaken(9, 5) == 5 && RM_PoolKernel.ChargesTaken(9, 0) == 1 && RM_PoolKernel.ChargesTaken(9, -3) == 1, "ChargesTaken");
                Check(RM_PoolKernel.TakesAll(5, 5) && !RM_PoolKernel.TakesAll(6, 5), "TakesAll");
                Check(!RM_PoolKernel.AmbientOpen(true, false, 99, 100) && RM_PoolKernel.AmbientOpen(true, false, 100, 100) && !RM_PoolKernel.AmbientOpen(false, false, 100, 0) && !RM_PoolKernel.AmbientOpen(true, true, 100, 0), "AmbientOpen boundary: the tick the respite ends is open");
                Check(RM_PoolKernel.GreatChance(-1f) == 0f && RM_PoolKernel.GreatChance(2f) == 1f && RM_PoolKernel.GreatChance(0.02f) == 0.02f, "GreatChance clamp");
                Check(RM_PoolKernel.Escalate(true, true, true) == AmbientKind.Great && RM_PoolKernel.Escalate(false, true, true) == AmbientKind.Ordinary && RM_PoolKernel.Escalate(true, false, true) == AmbientKind.Ordinary && RM_PoolKernel.Escalate(true, true, false) == AmbientKind.Ordinary, "Escalate");
                Check(RM_PoolKernel.GreatEligible(24, 24, 6, 6) && !RM_PoolKernel.GreatEligible(23, 24, 6, 6) && !RM_PoolKernel.GreatEligible(24, 24, 5, 6) && RM_PoolKernel.GreatEligible(1, 0, 0, -3), "GreatEligible boundaries and floors");
                Check(RM_PoolKernel.PressureAfter(5, AmbientKind.Ordinary) == 6 && RM_PoolKernel.PressureAfter(5, AmbientKind.Great) == 0 && RM_PoolKernel.PressureAfterForced(5) == 7, "pressure transitions");
            }
            catch (Exception e) { fails.Add("units: " + e.Message); }
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
                ("tally", () => Tally(N(4000), S(1))),
                ("tank", () => Tank(N(4000), S(1))),
                ("pool", () => Pool(N(4000), S(1))),
                ("weights", () => Weights(N(300), S(1))),
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
            Console.WriteLine($"tally: letters fired {LettersFired}, display tanks freed {TankFrees}, boldness at cap {BoldnessCapped}");
            Console.WriteLine($"tank: neglect rolls due {NeglectRolls}, neglect escapes {NeglectEscapes}, damage escapes {DamageEscapes}, display breaches {DisplayBreaches}, tanks destroyed {TankDestroyed}");
            Console.WriteLine($"pool: ordinary {Ordinary}, great {Great}, forced {Forced}, suppressions {Suppressions}, gifts delivered {GiftsDelivered}, hushes {Hushes}, restores {Restores}; weighted picks {Picks}, gift retries {Retries}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                var blind = new List<string>();
                if (LettersFired == 0) blind.Add("tally never fired a letter");
                if (TankFrees == 0) blind.Add("tally never freed a display tank");
                if (NeglectRolls == 0 || NeglectEscapes == 0 || DamageEscapes == 0 || DisplayBreaches == 0) blind.Add("tank never reached a neglect/damage/display escape");
                if (Great == 0 || Ordinary == 0 || Suppressions == 0 || GiftsDelivered == 0 || Hushes == 0 || Restores == 0) blind.Add("pool never reached great/ordinary/suppression/gift/hush/restore");
                foreach (var b in blind) { Console.WriteLine("FAIL fuzz is blind: " + b); ok = false; }
            }
            Console.WriteLine($"feverwood fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
