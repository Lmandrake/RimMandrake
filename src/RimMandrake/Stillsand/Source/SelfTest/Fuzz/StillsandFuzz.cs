// Approach B for Stillsand: seeded fuzz over the Verse-free kernels the mod calls (../../Kernel/*.cs):
//   leviathan  the sand-leviathan visit driven exactly as RM_MapComponent_SandLeviathans drives it (classify, rumble, arrival
//              fallback, the fed / fire / bored / hard-ground dive state machine, hunt gates), plus the wettest-body
//              appraisal, the entry-cell preference and the odds factor against brute-force specs
//   ledger     the water-debt book (draw, pay, opening throttle, band goodwill) against an exact dyadic spec, and the incident weight
//   gale       the dune-gale wind step, carry walk against a grid, exit / return edges, the walk back in, the carried-pawn book
//              scans and the emergence filter
//   sun        the sun factor of sun-fed tables, work speed, the solar still's progress clock, corpse yield, the thumper's beat
//              clock and call selection, the mirror beam's sun and damage
//   horizon    the announced-group clock (RM_HorizonMath): the plume stands through the retry window, a group turns back only after it
//   units      exhaustive truth tables for the small decisions
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Stillsand.Fuzz
{
    internal static class StillsandFuzz
    {
        public static long Cases, Steps;
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

        // ════════════════════════ leviathan ════════════════════════
        private static readonly string[] LevNames = { "Ticks", "SetSand", "AddKill", "SetBurn", "SetDowned", "KillPawn", "Despawn", "SetEntry", "Enqueue", "SetSubmerged", "SetGoto", "ToggleBeams", "Retarget" };
        public static long VisitsEnqueued, VisitsArrived, ArriveFailed, ArriveFallback, DivesFed, DivesFire, DivesBored, DivesHard, DivedOut, KilledOrGone, BeamsStarted, Breaches, Rumbles, ExactOffSand;

        private sealed class VisitSim
        {
            public int plannedArrive, arriveTick, warning, maxStay, giveUp, cooldown; public bool appraise;
            public bool hasPawn, spawned = true, dead, downed, burning, onSand, submerged, wasSubmerged, hasGoto, targetValid;
            public int kills, killsAtArrival, hardGround, diveStart = -1, lastBeam = -999999, arrivedAt = -1, enqueuedAt;
            public bool diving;
            // spec bookkeeping
            public int offRun; public bool everDowned, downedSinceDive, everKillOrBurn, everSand;
            public float lastT = -1f;
            public List<int> beamTicks = new List<int>();
            public int dives; public RM_DiveReason diveReason;
        }

        private sealed class LevSim
        {
            public int now;
            public List<VisitSim> visits = new List<VisitSim>();
            public bool entryValid = true, entryStandable = true, fallbackFound = true, beamsEnabled = true;
            public int signs, ended;
            public Random rng;
            public string err;

            public void Fail(string m) { if (err == null) err = m; }

            public void Enqueue(int warn, int maxStay, int giveUp)
            {
                var v = new VisitSim { warning = warn, plannedArrive = now + Math.Max(0, warn), maxStay = maxStay, giveUp = giveUp, cooldown = 300 + rng.Next(3) * 300, appraise = rng.Next(2) == 0, enqueuedAt = now };
                v.arriveTick = v.plannedArrive;
                visits.Add(v);
                VisitsEnqueued++; enq++;
            }

            private void End(int i, RM_VisitEnd end, bool signGiven)
            {
                if (RM_LeviathanKernel.EndNeedsSign(end) && !signGiven) Fail("visit ended " + end + " with no readable sign");
                if (RM_LeviathanKernel.EndNeedsSign(end) != (end == RM_VisitEnd.ArriveFailed || end == RM_VisitEnd.Dived)) Fail("EndNeedsSign disagrees with the ending table for " + end);
                if (signGiven) signs++;
                ended++;
                visits.RemoveAt(i);
            }

            public void Step()
            {
                now++;
                Steps++;
                if (!RM_LeviathanKernel.ShouldProcess(visits.Count, now)) return;
                if (now % RM_LeviathanKernel.Interval != 0 || visits.Count == 0) Fail("ShouldProcess true off the interval or with no visits");
                for (int i = visits.Count - 1; i >= 0; i--)
                {
                    VisitSim v = visits[i];
                    bool gone = v.hasPawn && (v.dead || !v.spawned);
                    RM_VisitClass cls = RM_LeviathanKernel.Classify(false, false, v.hasPawn, gone, now, v.arriveTick);
                    if (!v.hasPawn && cls != (now < v.plannedArrive ? RM_VisitClass.Rumble : RM_VisitClass.Arrive)) Fail("Classify of a pending visit");
                    if (cls == RM_VisitClass.Drop)
                    {
                        if (!gone) Fail("a live visit was dropped");
                        KilledOrGone++;
                        End(i, v.dead ? RM_VisitEnd.Killed : RM_VisitEnd.Gone, false);
                        continue;
                    }
                    if (cls == RM_VisitClass.Rumble)
                    {
                        if (now >= v.plannedArrive) Fail("rumble at or after the arrival tick");
                        float t = RM_LeviathanKernel.RumbleT(v.plannedArrive, now, v.warning);
                        if (t < 0f || t > 1f) Fail("rumble t outside 0..1: " + t);
                        if (t + 1e-6f < v.lastT) Fail("rumble t went backwards");
                        v.lastT = t;
                        float shake = RM_LeviathanKernel.RumbleShake(t);
                        if (shake < 0.02f - 1e-6f || shake > 0.2f + 1e-6f) Fail("rumble shake outside 0.02..0.2");
                        float dust = RM_LeviathanKernel.RumbleDustChance(t);
                        if (dust < 0.3f - 1e-6f || dust > 1f + 1e-6f) Fail("rumble dust chance outside 0.3..1");
                        Rumbles++;
                        continue;
                    }
                    if (cls == RM_VisitClass.Arrive)
                    {
                        bool usable = entryValid && entryStandable;
                        bool sign = false;
                        if (!usable)
                        {
                            RM_ArriveCell r = RM_LeviathanKernel.ResolveArrival(false, false, fallbackFound);
                            if (r == RM_ArriveCell.Fail)
                            {
                                if (fallbackFound) Fail("ResolveArrival failed with a fallback cell found");
                                sign = true; // the mod posts a message here
                                ArriveFailed++;
                                End(i, RM_VisitEnd.ArriveFailed, sign);
                                continue;
                            }
                            ArriveFallback++;
                            if (!fallbackFound) Fail("ResolveArrival used a fallback that was not found");
                        }
                        else if (RM_LeviathanKernel.ResolveArrival(true, true, false) != RM_ArriveCell.UseEntry) Fail("a usable entry cell was not used");
                        v.hasPawn = true; v.arrivedAt = now; v.arriveTick = now; v.killsAtArrival = v.kills = 0;
                        v.onSand = rng.Next(4) != 0;
                        {
                            int lowest = Math.Max(v.plannedArrive, v.enqueuedAt + 1);
                            int first = (lowest + 29) / 30 * 30;
                            if (now != first) Fail($"arrival at {now}, spec: first processed tick {first} (planned {v.plannedArrive}, enqueued {v.enqueuedAt})");
                        }
                        VisitsArrived++;
                        continue;
                    }
                    Tick(v, i);
                }
            }

            private void Tick(VisitSim v, int i)
            {
                bool breach = RM_LeviathanKernel.IsBreach(v.wasSubmerged, v.submerged, v.downed);
                if (breach != (v.wasSubmerged && !v.submerged && !v.downed)) Fail("IsBreach");
                if (breach) Breaches++;
                v.wasSubmerged = v.submerged;
                if (v.downed) { v.everDowned = true; v.downedSinceDive = v.downedSinceDive || v.diving; return; }
                if (v.onSand) v.everSand = true;
                if (!v.diving)
                {
                    int hg = v.hardGround;
                    // spec, independent: consecutive evaluated off-sand checks
                    v.offRun = v.onSand ? 0 : v.offRun + 1;
                    RM_DiveReason spec = v.kills > v.killsAtArrival ? RM_DiveReason.Fed
                        : v.burning ? RM_DiveReason.Fire
                        : now - v.arriveTick > v.maxStay ? RM_DiveReason.Bored
                        : v.offRun * 30 > v.giveUp ? RM_DiveReason.HardGround : RM_DiveReason.None;
                    if (v.kills > v.killsAtArrival || v.burning) v.everKillOrBurn = true;
                    RM_DiveReason why = RM_LeviathanKernel.DecideDive(v.kills, v.killsAtArrival, v.burning, now, v.arriveTick, v.maxStay, v.onSand, v.giveUp, ref hg);
                    v.hardGround = hg;
                    if (why != spec) Fail($"dive decision {why}, spec {spec} (kills {v.kills}/{v.killsAtArrival} burn {v.burning} stay {now - v.arriveTick}/{v.maxStay} sand {v.onSand} offRun {v.offRun} give {v.giveUp})");
                    if (v.onSand && v.hardGround != 0 && why == RM_DiveReason.None) Fail("the hard-ground clock did not reset on sand");
                    if (why == RM_DiveReason.None && v.hardGround != v.offRun * 30) Fail($"hard-ground clock {v.hardGround}, spec {v.offRun * 30}");
                    if (why != RM_DiveReason.None)
                    {
                        if (v.diving) Fail("second dive");
                        v.diving = true; v.diveStart = now; v.hasGoto = false; v.dives++; v.diveReason = why;
                        if (why == RM_DiveReason.Fed) DivesFed++; else if (why == RM_DiveReason.Fire) DivesFire++; else if (why == RM_DiveReason.Bored) DivesBored++; else DivesHard++;
                    }
                }
                if (v.diving)
                {
                    RM_DiveStep step = RM_LeviathanKernel.DiveStep(v.onSand, now, v.diveStart, v.hasGoto);
                    bool timeout = now - v.diveStart > RM_LeviathanKernel.DiveTimeoutTicks;
                    RM_DiveStep want = v.onSand || timeout ? RM_DiveStep.Dive : v.hasGoto ? RM_DiveStep.KeepSeeking : RM_DiveStep.SeekSand;
                    if (step != want) Fail($"dive step {step}, spec {want}");
                    if (step == RM_DiveStep.Dive)
                    {
                        if (!v.downedSinceDive && now - v.diveStart > RM_LeviathanKernel.DiveTimeoutTicks + RM_LeviathanKernel.Interval) Fail("a dive outlived its timeout");
                        // exact lifetime of a visitor that never touched sand, never fed or burned and was never downed
                        if (v.diveReason == RM_DiveReason.HardGround && !v.everSand && !v.everDowned)
                        {
                            int expect = 30 * (v.giveUp / 30 + 1) + 1260;
                            if (now - v.arrivedAt != expect) Fail($"off-sand visitor lived {now - v.arrivedAt} ticks, spec {expect}");
                            ExactOffSand++;
                        }
                        DivedOut++;
                        End(i, RM_VisitEnd.Dived, true);
                        return;
                    }
                    if (step == RM_DiveStep.SeekSand) v.hasGoto = rng.Next(3) != 0;
                    return;
                }
                if (v.appraise)
                {
                    bool invalid = !v.targetValid;
                    if (RM_LeviathanKernel.ShouldRetarget(invalid, now) != (invalid || now % 250 < 30)) Fail("ShouldRetarget");
                    if (RM_LeviathanKernel.ShouldRetarget(invalid, now)) v.targetValid = rng.Next(5) != 0;
                    if (!v.targetValid) return;
                    if (rng.Next(10) == 0) return; // the beam is warming up
                    bool busy = rng.Next(6) == 0;
                    bool gate = RM_LeviathanKernel.BeamGate(beamsEnabled, now, v.lastBeam, v.cooldown, true, busy);
                    bool specGate = beamsEnabled && now - v.lastBeam >= v.cooldown && !busy;
                    if (gate != specGate) Fail("BeamGate");
                    if (gate && rng.Next(2) == 0)
                    {
                        if (!beamsEnabled) Fail("a beam started with beams disabled");
                        if (v.beamTicks.Count > 0 && now - v.beamTicks[v.beamTicks.Count - 1] < v.cooldown) Fail("two beams closer than the cooldown");
                        v.beamTicks.Add(now); v.lastBeam = now; BeamsStarted++;
                    }
                }
            }

            public void Invariants()
            {
                foreach (VisitSim v in visits)
                {
                    if (!v.hasPawn && v.arrivedAt >= 0) Fail("a pending visit has an arrival tick");
                    if (v.hasPawn && v.arrivedAt < v.plannedArrive) Fail("arrived before the planned tick");
                    if (v.hardGround % 30 != 0 || v.hardGround < 0) Fail("hard-ground clock not a multiple of the interval");
                    if (v.dives > 1) Fail("more than one dive");
                    if (!v.diving && v.diveStart != -1) Fail("dive tick set without a dive");
                    // a live visitor never outstays: bored fires at the first check past maxStay unless downed
                    if (v.hasPawn && !v.everDowned && !v.diving && now - v.arriveTick > v.maxStay + RM_LeviathanKernel.Interval) Fail("a healthy visitor outstayed maxStay without diving");
                }
                if (visits.Count + ended != enq) Fail("visit bookkeeping: live + ended != enqueued");
            }

            public int enq;
        }

        private static List<Act> GenLev(int seed)
        {
            var r = new Random(seed * 7919 + 1);
            var acts = new List<Act>();
            acts.Add(new Act { kind = 8, a = 100 + r.Next(2900), b = 200 + r.Next(20000), c = 30 + r.Next(1200), names = LevNames });
            int n = 20 + r.Next(80);
            for (int i = 0; i < n; i++)
            {
                int k = r.Next(100);
                int kind = k < 40 ? 0 : k < 52 ? 1 : k < 56 ? 2 : k < 59 ? 3 : k < 63 ? 4 : k < 65 ? 5 : k < 67 ? 6 : k < 73 ? 7 : k < 77 ? 8 : k < 85 ? 9 : k < 92 ? 10 : k < 95 ? 11 : 12;
                acts.Add(new Act { kind = kind, a = kind == 0 ? 1 + r.Next(r.Next(4) == 0 ? 3000 : 400) : r.Next(4000), b = r.Next(20000), c = r.Next(2) * (30 + r.Next(1200)), names = LevNames });
            }
            return acts;
        }

        private static string RunLev(int seed, List<Act> acts)
        {
            var s = new LevSim { rng = new Random(seed ^ 0x5eed) };
            try
            {
                foreach (Act a in acts)
                {
                    VisitSim v = s.visits.Count > 0 ? s.visits[(a.b & 0xffff) % s.visits.Count] : null;
                    switch (a.kind)
                    {
                        case 0: for (int k = 0; k < a.a && s.err == null; k++) { s.Step(); s.Invariants(); } break;
                        case 1: if (v != null) v.onSand = a.a % 2 == 0; break;
                        case 2: if (v != null && v.hasPawn) v.kills++; break;
                        case 3: if (v != null) v.burning = a.a % 2 == 0; break;
                        case 4: if (v != null) v.downed = a.a % 3 == 0; break;
                        case 5: if (v != null && v.hasPawn) v.dead = true; break;
                        case 6: if (v != null && v.hasPawn) v.spawned = false; break;
                        case 7: s.entryValid = a.a % 4 != 0; s.entryStandable = a.a % 5 != 0; s.fallbackFound = a.c % 2 == 0 || a.a % 7 == 0; break;
                        case 8: s.Enqueue(a.a % 3200, 100 + a.b % 20000, 30 + a.c % 1300); break;
                        case 9: if (v != null) v.submerged = a.a % 2 == 0; break;
                        case 10: if (v != null) v.hasGoto = a.a % 2 == 0; break;
                        case 11: s.beamsEnabled = a.a % 2 == 0; break;
                        case 12: if (v != null) v.targetValid = false; break;
                    }
                    if (s.err != null) return s.err + " @tick " + s.now;
                }
                // run everything out: with no further interference every visit must end (healthy ones by boredom, dives by timeout)
                foreach (VisitSim v in s.visits) { v.downed = false; v.targetValid = true; }
                for (int k = 0; k < 200000 && s.visits.Count > 0 && s.err == null; k++)
                {
                    s.Step(); s.Invariants();
                    // a pending or healthy visit with no help ends
                    if (k > 150000) break;
                }
                if (s.err != null) return s.err + " @tick " + s.now;
                if (s.visits.Count > 0) return $"{s.visits.Count} visit(s) still alive after 200000 undisturbed ticks";
                return null;
            }
            catch (Exception e) { return e.Message + " @tick " + s.now; }
        }

        private static List<string> Leviathan(int n, int seed)
        {
            var fails = RunFamily("leviathan", n, seed, GenLev, RunLev);
            // appraisal, entry preference and odds, against brute-force specs
            try
            {
                var r = new Random(seed + 77);
                for (int k = 0; k < Math.Max(1, n); k++)
                {
                    int m = r.Next(0, 12);
                    var player = new bool[m]; var score = new float[m];
                    for (int i = 0; i < m; i++)
                    {
                        player[i] = r.Next(3) == 0;
                        float body = (float)(r.Next(1, 40)) / 8f;
                        bool has = r.Next(2) == 0;
                        float pct = (float)r.Next(0, 33) / 32f;
                        score[i] = RM_LeviathanKernel.WaterScore(body, has, pct);
                        float want = body * (has ? Math.Max(0.05f, pct) : 1f);
                        Check(score[i] == want, "WaterScore " + score[i] + " vs " + want);
                        Check(has == false || RM_LeviathanKernel.WaterScore(body, true, 0f) == body * 0.05f, "a thirsty body is floored at 5%");
                        Check(score[i] > 0f, "a body scored zero");
                    }
                    int best = -1; float bs = 0f; bool bp = false;
                    for (int i = 0; i < m; i++)
                        if (RM_LeviathanKernel.BeatsBest(player[i], bp, score[i], bs)) { best = i; bs = score[i]; bp = player[i]; }
                    // spec: any player -> the first highest-scoring player; else the first highest-scoring other
                    int spec = -1;
                    for (int cls = 1; cls >= 0 && spec < 0; cls--)
                        for (int i = 0; i < m; i++)
                            if (player[i] == (cls == 1) && (spec < 0 || score[i] > score[spec])) spec = i;
                    Check(best == spec, $"wettest body {best}, spec {spec} of {m}");
                    Cases++; Steps += m;
                    // entry cell: any sand beats any non-sand; nearest wins; first of equals keeps
                    int cn = r.Next(1, 61);
                    var sand = new bool[cn]; var d = new float[cn];
                    for (int i = 0; i < cn; i++) { sand[i] = r.Next(4) == 0; d[i] = r.Next(0, 5000); }
                    int bi = -1; float bd = float.MaxValue; bool bsand = false;
                    for (int i = 0; i < cn; i++) if (RM_LeviathanKernel.BetterEntry(sand[i], bsand, d[i], bd)) { bi = i; bd = d[i]; bsand = sand[i]; }
                    int es = -1;
                    bool anySand = sand.Any(x => x);
                    for (int i = 0; i < cn; i++) if (sand[i] == anySand && (es < 0 || d[i] < d[es])) es = i;
                    Check(bi == es, $"entry cell {bi}, spec {es} of {cn} (sand anywhere: {anySand})");
                    // odds
                    int drills = r.Next(0, 20); float per = r.Next(0, 9) / 4f; float max = 1f + r.Next(0, 13) / 4f;
                    float vf = RM_LeviathanKernel.VibrationFactor(drills, per, max);
                    Check(vf >= 1f && vf <= max, "vibration factor outside 1..max");
                    Check(drills == 0 && vf == 1f || drills > 0, "no drills must not change the odds");
                    Check(RM_LeviathanKernel.VibrationFactor(drills + 1, per, max) >= vf, "more drills lowered the odds");
                }
            }
            catch (Exception e) { fails.Add("leviathan-pure: " + e.Message); }
            return fails;
        }

        // ════════════════════════ ledger ════════════════════════
        private static readonly string[] LedNames = { "Draw", "Pay", "Open", "Advance", "Reload" };
        public static long LedDraws, LedPays, LedOpensAccepted, LedOpensRefused, LedCrossings, LedThrottledCrossings, LedBandUps, LedBandDowns;

        private static string RunLedger(int seed, List<Act> acts)
        {
            var r = new Random(seed * 31 + 5);
            int nb = 2 + r.Next(5);
            var bands = new List<float> { 0f };
            for (int i = 1; i < nb; i++) bands.Add(bands[i - 1] + 8 + r.Next(60));
            float threshold = 10 + r.Next(150);
            int minGap = 100 + r.Next(40000);
            int[] gws = { -4, 0, -1, 3, -10 };
            int gw = gws[r.Next(gws.Length)];
            float wph = r.Next(0, 9) / 4f, maxW = r.Next(0, 17) / 4f;
            var book = new RM_LedgerBook();
            double drawn = 0, paid = 0, debtSpec = 0; int lastBandSpec = 0; long goodwillSpec = 0, goodwillGot = 0;
            int now = 0, acceptedSerial = 0, lastAccept = -999999; float prevFactor = 1f; double prevDebtForFactor = 0;
            try
            {
                foreach (Act a in acts)
                {
                    Steps++;
                    switch (a.kind)
                    {
                        case 0:
                        {
                            float l = (a.a % 400 + 1) / 4f;
                            double before = debtSpec;
                            RM_LedgerDraw d = book.Draw(l, bands, gw, threshold);
                            debtSpec += l; drawn += l; LedDraws++;
                            int b = SpecBand(bands, debtSpec);
                            long ug = b > lastBandSpec ? (long)gw * (b - lastBandSpec) : 0; if (b > lastBandSpec) LedBandUps++;
                            lastBandSpec = b; goodwillSpec += ug; goodwillGot += d.goodwillDelta;
                            Check(d.goodwillDelta == ug, $"draw goodwill {d.goodwillDelta}, spec {ug}");
                            bool cross = before < threshold && debtSpec >= threshold;
                            Check(d.crossedOpening == cross, $"crossedOpening {d.crossedOpening}, spec {cross} ({before} -> {debtSpec}, threshold {threshold})");
                            if (cross) { LedCrossings++; if (now - book.lastOpeningTick < minGap) LedThrottledCrossings++; }
                            break;
                        }
                        case 1:
                        {
                            float l = (a.a % 400) / 4f;
                            float p = book.Pay(l, bands, gw, out int pgw);
                            double sp = Math.Min(l, debtSpec);
                            debtSpec -= sp; paid += sp; LedPays++;
                            Check(p == sp, $"paid {p}, spec {sp}");
                            int b = SpecBand(bands, debtSpec);
                            if (b < lastBandSpec) LedBandDowns++;
                            long ug = b > lastBandSpec ? (long)gw * (b - lastBandSpec) : 0;
                            lastBandSpec = b; goodwillSpec += ug; goodwillGot += pgw;
                            Check(pgw == ug, $"pay goodwill {pgw}, spec {ug}");
                            Check(pgw == 0, "paying a debt down cost goodwill");
                            break;
                        }
                        case 2:
                        {
                            bool want = now - lastAccept >= minGap;
                            bool got = book.TryOpen(now, minGap);
                            Check(got == want, $"TryOpen at {now} gave {got}, spec {want}");
                            if (want) { lastAccept = now; acceptedSerial++; LedOpensAccepted++; } else LedOpensRefused++;
                            break;
                        }
                        case 3: now += a.a * 7 % 30000; break;
                        case 4:
                        {
                            var copy = new RM_LedgerBook { debt = book.debt, drawnTotal = book.drawnTotal, paidTotal = book.paidTotal, openingSerial = book.openingSerial, lastOpeningTick = book.lastOpeningTick, lastBand = book.lastBand };
                            book = copy; // Scribe round trip: the fields are the whole state
                            break;
                        }
                    }
                    Check(book.debt == debtSpec, $"debt {book.debt}, spec {debtSpec}");
                    Check(book.drawnTotal == drawn && book.paidTotal == paid, "drawn / paid totals");
                    Check(book.debt >= 0f, "negative debt");
                    Check(book.paidTotal <= book.drawnTotal, "paid more than was ever drawn");
                    Check(book.debt == book.drawnTotal - book.paidTotal, "debt != drawn - paid");
                    Check(book.openingSerial == acceptedSerial, $"opening serial {book.openingSerial}, spec {acceptedSerial}");
                    Check(book.lastBand == SpecBand(bands, debtSpec), $"lastBand {book.lastBand} out of step with the debt ({SpecBand(bands, debtSpec)})");
                    Check(goodwillGot == goodwillSpec, "goodwill total drifted");
                    float f = RM_LedgerBook.IncidentFactor(book.debt, wph, maxW);
                    Check(f >= 1f && f <= Math.Max(1f, maxW), $"incident factor {f} outside 1..max({maxW})");
                    Check(book.debt != 0f || f == 1f, "an unpaid-nothing ledger weights an incident");
                    if (debtSpec >= prevDebtForFactor) Check(f >= prevFactor - 1e-6f, "more debt lowered the incident factor"); else Check(f <= prevFactor + 1e-6f, "less debt raised the incident factor");
                    prevFactor = f; prevDebtForFactor = debtSpec;
                }
                return null;
            }
            catch (Exception e) { return e.Message; }
        }

        private static int SpecBand(List<float> bands, double debt)
        {
            int b = 0;
            for (int i = 0; i < bands.Count; i++) if (debt >= bands[i]) b = i;
            return b;
        }

        private static List<Act> GenLed(int seed)
        {
            var r = new Random(seed * 13 + 3);
            var acts = new List<Act>();
            int n = 30 + r.Next(170);
            for (int i = 0; i < n; i++)
            {
                int k = r.Next(100);
                acts.Add(new Act { kind = k < 40 ? 0 : k < 62 ? 1 : k < 76 ? 2 : k < 94 ? 3 : 4, a = r.Next(100000), b = 0, c = 0, names = LedNames });
            }
            return acts;
        }

        private static List<string> Ledger(int n, int seed)
        {
            return RunFamily("ledger", n, seed, GenLed, RunLedger);
        }

        // ════════════════════════ gale ════════════════════════
        private static readonly string[] GaleNames = { "Add", "Ticks", "EndGale" };
        public static long WindSamples, CarryWalks, CarriedOff, CarryBlocked, CarryMoved, CarryFilth, WalkIns, DiagonalOffNorthSouth, Returned, ReturnedByGale, BookAdds;

        private static List<string> Gale(int n, int seed)
        {
            var fails = RunFamily("gale-book", n, seed, GenBook, RunBook);
            try
            {
                var r = new Random(seed + 4242);
                // wind: sector spec away from the 22.5-degree boundaries, exact compass vectors, full-circle sweep
                int[] wantIdx = { 0, 2, 4, 6 };
                double[][] card = { new[] { 0.0, 1.0 }, new[] { 1.0, 0.0 }, new[] { 0.0, -1.0 }, new[] { -1.0, 0.0 } };
                for (int i = 0; i < 4; i++) Check(RM_GaleKernel.WindIndexFromShadow((float)card[i][0], (float)card[i][1]) == wantIdx[i], "cardinal shadow " + i);
                for (int k = 0; k < Math.Max(1, n) * 4; k++)
                {
                    double deg = r.NextDouble() * 360.0;
                    double frac = (deg / 45.0) - Math.Floor(deg / 45.0);
                    if (Math.Abs(frac - 0.5) < 0.01) continue;
                    double len = 0.1 + r.NextDouble() * 5.0;
                    float x = (float)(Math.Sin(deg * Math.PI / 180.0) * len), y = (float)(Math.Cos(deg * Math.PI / 180.0) * len);
                    int got = RM_GaleKernel.WindIndexFromShadow(x, y);
                    int want = (int)Math.Round(deg / 45.0) & 7;
                    Check(got >= 0 && got <= 7, "wind index outside 0..7");
                    Check(got == want, $"wind index {got}, spec {want} for bearing {deg:F2}");
                    Check(RM_GaleKernel.BearingName(RM_GaleKernel.DirX[got], RM_GaleKernel.DirZ[got]) == RM_GaleKernel.DirNames[got], "bearing name of a wind step");
                    WindSamples++;
                }
                Check(RM_GaleKernel.BearingName(0, 0) == "downwind" && RM_GaleKernel.BearingName(2, 0) == "downwind", "an off-table vector is 'downwind'");
                for (int i = 0; i < 8; i++)
                {
                    Check(Math.Abs(RM_GaleKernel.DirX[i]) <= 1 && Math.Abs(RM_GaleKernel.DirZ[i]) <= 1 && (RM_GaleKernel.DirX[i] != 0 || RM_GaleKernel.DirZ[i] != 0), "wind step " + i);
                    for (int j = i + 1; j < 8; j++) Check(RM_GaleKernel.DirX[i] != RM_GaleKernel.DirX[j] || RM_GaleKernel.DirZ[i] != RM_GaleKernel.DirZ[j], "two wind steps equal");
                    Check(RM_GaleKernel.ExitEdge(RM_GaleKernel.DirX[i], RM_GaleKernel.DirZ[i]) == RM_GaleKernel.ReturnEdge(RM_GaleKernel.DirX[i], RM_GaleKernel.DirZ[i]),
                        "exit and return edge differ for wind " + RM_GaleKernel.DirNames[i]);
                    // a cardinal wind leaves by the edge it blows toward
                    int wx = RM_GaleKernel.DirX[i], wz = RM_GaleKernel.DirZ[i];
                    if (wx == 0 || wz == 0)
                    {
                        RM_Edge e = RM_GaleKernel.ExitEdge(wx, wz);
                        Check((wz > 0 && e == RM_Edge.North) || (wz < 0 && e == RM_Edge.South) || (wx > 0 && e == RM_Edge.East) || (wx < 0 && e == RM_Edge.West), "cardinal exit edge");
                    }
                }
                Check(RM_GaleKernel.ReturnEdge(0, 0) == RM_Edge.South, "a zero wind returns from the south");
                // carry walk against a grid with walls
                for (int k = 0; k < Math.Max(1, n) * 3; k++)
                {
                    int w = r.Next(5, 40), h = r.Next(5, 40);
                    var wall = new bool[w, h];
                    double density = r.NextDouble() * 0.25;
                    for (int x = 0; x < w; x++) for (int z = 0; z < h; z++) wall[x, z] = r.NextDouble() < density;
                    int dir = r.Next(8), wx = RM_GaleKernel.DirX[dir], wz = RM_GaleKernel.DirZ[dir];
                    int sx = r.Next(w), sz = r.Next(h), steps = r.Next(0, 14);
                    Func<int, int, bool> inb = (x, z) => x >= 0 && z >= 0 && x < w && z < h;
                    Func<int, int, bool> walk = (x, z) => !wall[x, z];
                    var left = new List<(int, int)>();
                    RM_CarryResult res = RM_GaleKernel.CarryWalk(sx, sz, wx, wz, steps, inb, walk, (x, z) => left.Add((x, z)));
                    // spec by ray
                    int cx = sx, cz = sz, mv = 0; bool off = false;
                    for (int s = 1; s <= steps; s++)
                    {
                        int nx = sx + wx * s, nz = sz + wz * s;
                        if (!inb(nx, nz)) { off = true; break; }
                        if (wall[nx, nz]) break;
                        cx = nx; cz = nz; mv = s;
                    }
                    Check(res.moved == mv && res.x == cx && res.z == cz && res.offMap == off, $"carry walk ended {res.x},{res.z} moved {res.moved} off {res.offMap}; spec {cx},{cz} moved {mv} off {off}");
                    Check(left.Count == mv, "onLeave called " + left.Count + " times for " + mv + " steps");
                    for (int i = 0; i < left.Count; i++) Check(left[i].Item1 == sx + wx * i && left[i].Item2 == sz + wz * i, "onLeave cell " + i);
                    Check(res.moved <= steps, "walked more steps than rolled");
                    Check(!res.offMap || (res.moved < steps && !inb(res.x + wx, res.z + wz)), "off-map flag without the edge ahead");
                    Check(res.offMap || res.moved == steps || !walk(res.x + wx, res.z + wz) , "stopped short without a wall ahead");
                    CarryWalks++; Steps += steps + 1;
                    if (res.offMap) { CarriedOff++; if (wx != 0 && wz != 0 && (res.z + wz < 0 || res.z + wz >= h) && !(res.x + wx < 0 || res.x + wx >= w)) DiagonalOffNorthSouth++; }
                    else if (res.moved == 0) CarryBlocked++; else CarryMoved++;
                    CarryFilth += left.Count;
                    // walk back in from an edge cell
                    int ex = r.Next(w), ez = r.Next(h);
                    int ix = ex, iz = ez;
                    RM_GaleKernel.WalkIn(ref ix, ref iz, wx, wz, inb, (x, z) => !wall[x, z]);
                    int back = Math.Max(Math.Abs(ix - ex), Math.Abs(iz - ez));
                    Check(back <= 4 && ix == ex - wx * back && iz == ez - wz * back && inb(ix, iz), "walk-in left the line or the map");
                    if (back < 4) { int nx = ix - wx, nz = iz - wz; Check(!inb(nx, nz) || wall[nx, nz], "walk-in stopped early in open ground"); }
                    WalkIns++;
                }
                // return outcome and carry eligibility, exhaustive
                for (int m = 0; m < 16; m++)
                {
                    bool pm = (m & 1) != 0, mm = (m & 2) != 0, dd = (m & 4) != 0, al = (m & 8) != 0;
                    RM_ReturnOutcome want = pm || mm ? RM_ReturnOutcome.LostMissing : dd ? RM_ReturnOutcome.LostDead : al ? RM_ReturnOutcome.SpawnAlive : RM_ReturnOutcome.SpawnThenKill;
                    Check(RM_GaleKernel.Decide(pm, mm, dd, al) == want, "Decide table " + m);
                }
                foreach (float body in new[] { 0.5f, 1f, 1.01f, 3f })
                    for (int m = 0; m < 8; m++)
                    {
                        bool roof = (m & 1) != 0, crest = (m & 2) != 0, dead = (m & 4) != 0;
                        bool want = !(body > 1f) && !roof && crest && !dead;
                        Check(RM_GaleKernel.CarryEligible(body, 1f, roof, crest, dead) == want, $"CarryEligible({body},{roof},{crest},{dead})");
                    }
                for (int m = 0; m < 64; m++)
                {
                    bool allowed = (m & 1) != 0, ns = (m & 2) != 0, sa = (m & 4) != 0, nc = (m & 8) != 0, cf = (m & 16) != 0, pos = (m & 32) != 0;
                    bool want = pos && allowed && (!ns || sa) && (!nc || cf);
                    Check(RM_GaleKernel.EmergenceOk(pos ? 1f : 0f, allowed, ns, sa, nc, cf) == want, "EmergenceOk table " + m);
                }
                Check(!RM_GaleKernel.EmergenceOk(-1f, true, false, false, false, false), "a negative weight is not a candidate");
            }
            catch (Exception e) { fails.Add("gale-pure: " + e.Message); }
            return fails;
        }

        private sealed class Rec { public int id, map, returnTick; public bool returned; }

        private static List<Act> GenBook(int seed)
        {
            var r = new Random(seed * 17 + 9);
            var acts = new List<Act>();
            int n = 15 + r.Next(60);
            for (int i = 0; i < n; i++)
            {
                int k = r.Next(100);
                int kind = k < 35 ? 0 : k < 90 ? 1 : 2;
                acts.Add(new Act { kind = kind, a = kind == 1 ? 1 + r.Next(r.Next(3) == 0 ? 9000 : 700) : r.Next(5), b = r.Next(200000), c = 0, names = GaleNames });
            }
            return acts;
        }

        private static string RunBook(int seed, List<Act> acts)
        {
            var book = new List<Rec>();
            var all = new List<Rec>();
            int now = 0, nextId = 1;
            try
            {
                foreach (Act a in acts)
                {
                    switch (a.kind)
                    {
                        case 0:
                        {
                            var rec = new Rec { id = nextId++, map = a.a % 3, returnTick = now + 100 + a.b % 30000 };
                            book.Add(rec); all.Add(rec); BookAdds++;
                            break;
                        }
                        case 1:
                            for (int t = 0; t < a.a; t++)
                            {
                                now++; Steps++;
                                if (!RM_GaleKernel.ShouldScanCarried(book.Count, now)) continue;
                                Check(now % 2000 == 0 && book.Count > 0, "scan off the interval or with an empty book");
                                int before = book.Count;
                                var due = RM_GaleKernel.TakeWhere(book, c => RM_GaleKernel.IsDue(c.returnTick, now));
                                foreach (Rec c in due)
                                {
                                    Check(!c.returned, "record " + c.id + " returned twice");
                                    Check(c.returnTick <= now, "record returned before it was due");
                                    Check(now - c.returnTick < 2000, "record " + c.id + " returned " + (now - c.returnTick) + " ticks late");
                                    c.returned = true; Returned++;
                                }
                                Check(before - due.Count == book.Count, "TakeWhere lost a record");
                                foreach (Rec c in book) Check(c.returnTick > now, "a due record was left in the book at tick " + now);
                            }
                            break;
                        case 2:
                        {
                            int m = a.a % 3;
                            int expect = book.Count(c => c.map == m);
                            var got = RM_GaleKernel.TakeWhere(book, c => c.map == m);
                            Check(got.Count == expect, "gale end returned " + got.Count + ", spec " + expect);
                            foreach (Rec c in got) { Check(!c.returned && c.map == m, "gale end returned a foreign or already-returned record"); c.returned = true; ReturnedByGale++; }
                            Check(book.All(c => c.map != m), "a record of the ended map stayed");
                            break;
                        }
                    }
                    Check(book.Count + all.Count(c => c.returned) == all.Count, "records lost or duplicated");
                    Check(book.All(c => !c.returned), "a returned record is still in the book");
                }
                return null;
            }
            catch (Exception e) { return e.Message; }
        }

        // ════════════════════════ sun ════════════════════════
        private static readonly string[] StillNames = { "Step", "NoFeed", "NoRate", "SetRate" };
        public static long StillFired, StillStepsRun, StillResets, StillHolds, ThumperBeats, ThumperCallsMade, SunReasons, FactorCases;

        private static List<string> Sun(int n, int seed)
        {
            var fails = RunFamily("sun-still", n, seed, GenStill, RunStill);
            try
            {
                var r = new Random(seed + 991);
                // intensity: pinned sun follows sin(elevation), NaN is dark, monotone over 0..90, unpinned clamps the glow
                Check(RM_SunKernel.Intensity(true, float.NaN, 1f) == 0f && RM_SunKernel.Intensity(false, 90f, 2f) == 1f && RM_SunKernel.Intensity(false, 90f, -1f) == 0f, "Intensity corner cases");
                float prev = -1f;
                for (int e = 0; e <= 90; e++)
                {
                    float v = RM_SunKernel.Intensity(true, e, 0f);
                    Check(v >= prev - 1e-6f && v >= 0f && v <= 1f, "intensity not monotone / out of range at " + e);
                    Check(Math.Abs(v - Math.Sin(e * Math.PI / 180.0)) < 1e-5, "intensity != sin(elevation) at " + e);
                    prev = v;
                }
                Check(RM_SunKernel.Intensity(true, -20f, 0.9f) == 0f && RM_SunKernel.Intensity(true, 120f, 0f) >= 0f, "a sun below the horizon gives no light");
                // factor table
                for (int k = 0; k < Math.Max(1, n) * 4; k++)
                {
                    bool spawned = r.Next(8) != 0, roofed = r.Next(5) == 0, blotted = r.Next(6) == 0;
                    float sun = r.Next(5) == 0 ? 0f : r.Next(0, 17) / 16f, shade = r.Next(0, 17) / 16f;
                    float f = RM_SunKernel.Factor(spawned, roofed, blotted, sun, shade, out RM_SunReason why);
                    RM_SunReason wr; float wf;
                    if (!spawned) { wr = RM_SunReason.NotSpawned; wf = 0f; }
                    else if (roofed) { wr = RM_SunReason.Roofed; wf = 0f; }
                    else if (blotted) { wr = RM_SunReason.Blotted; wf = 0f; }
                    else if (sun <= 0f) { wr = RM_SunReason.NoSun; wf = 0f; }
                    else { wf = sun * (1f - shade); wr = shade >= 0.5f ? RM_SunReason.InShade : wf < 0.3f ? RM_SunReason.TooLow : RM_SunReason.None; }
                    Check(f == wf && why == wr, $"Factor {f}/{why}, spec {wf}/{wr}");
                    Check(f >= 0f && f <= 1f, "factor outside 0..1");
                    Check(!(roofed && f > 0f) && !(blotted && f > 0f), "a roofed or blotted-out thing has sun");
                    Check(RM_SunKernel.Factor(spawned, roofed, blotted, sun, shade + 5f, out _) <= f + 1e-6f, "more shade gave more sun");
                    float cl = RM_SunKernel.Factor(spawned, roofed, blotted, sun, -3f, out _);
                    Check(cl == (spawned && !roofed && !blotted && sun > 0f ? sun : 0f), "shade below 0 is clamped to 0");
                    FactorCases++; if (why != RM_SunReason.None) SunReasons++;
                    // can work / work speed
                    float min = r.Next(0, 9) / 16f;
                    Check(RM_SunKernel.CanWork(true, f, min) == (f >= min) && !RM_SunKernel.CanWork(false, f, min), "CanWork");
                    float ws = RM_SunKernel.WorkSpeed(true, f, 1.5f, 2f);
                    Check(ws == Math.Max(0.05f, f) * 1.5f * 2f && ws >= 0.15f - 1e-6f, "WorkSpeed floor / formula");
                    Check(RM_SunKernel.WorkSpeed(false, f, 1.5f, 2f) == 1f, "an unscaled table works at 1");
                    Check(RM_SunKernel.WorkSpeed(true, f + 0.1f, 1f, 1f) >= RM_SunKernel.WorkSpeed(true, f, 1f, 1f), "work speed fell with more sun");
                    // still rate
                    float rate = RM_SunKernel.StillRate(f >= min, f, 0.5f + r.Next(0, 5) / 2f, r.Next(2) == 0, 2f);
                    Check(f >= min || rate == 0f, "a still that cannot work has a rate");
                    Check(rate >= 0f, "negative rate");
                    // beam sun
                    float glow = r.Next(0, 17) / 16f, minGlow = r.Next(0, 17) / 16f;
                    float bs = RM_SunKernel.BeamSunPawn(roofed, blotted, glow, minGlow);
                    Check(bs == (roofed || blotted || glow < minGlow ? 0f : glow), "BeamSunPawn");
                    Check(RM_SunKernel.BeamSunTurret(glow, minGlow) == (glow < minGlow ? 0f : glow), "BeamSunTurret");
                    float total = r.Next(0, 3) == 0 ? 0f : r.Next(1, 40), def = r.Next(1, 20); int cells = r.Next(0, 30);
                    float dmg = RM_SunKernel.BeamDamage(total, cells, def, glow);
                    Check(dmg == (total > 0f ? total / Math.Max(1, cells) * glow : def * glow) && dmg >= 0f, "BeamDamage");
                    Check(RM_SunKernel.BeamDamage(total, cells, def, glow) <= RM_SunKernel.BeamDamage(total, cells, def, Math.Min(1f, glow + 0.25f)) + 1e-6f, "a stronger sun did less beam damage");
                    if (total > 0f && glow > 0.01f) Check(RM_SunKernel.BeamDamage(total, cells + 1, def, 1f) <= dmg / Math.Max(glow, 1e-9f) + 1e-4f, "more swept cells raised the per-cell damage");
                }
                // corpse yield
                for (int k = 0; k < Math.Max(1, n); k++)
                {
                    float body = r.Next(0, 80) / 8f, per = r.Next(0, 40) / 4f;
                    int lit = RM_SunKernel.CorpseLitres(body, per);
                    Check(lit >= 1 && lit == Math.Max(1, (int)Math.Round((double)(body * per))), "CorpseLitres");
                    Check(RM_SunKernel.CorpseLitres(body + 1f, per) >= lit, "a bigger corpse gave less water");
                }
                // thumper beat clock and call selection
                for (int k = 0; k < Math.Max(1, n); k++)
                {
                    bool en = r.Next(5) != 0, fuel = r.Next(4) != 0; int interval = r.Next(1, 800), last = -99999 + r.Next(200000), now = r.Next(200000);
                    bool due = RM_SunKernel.BeatDue(en, now, last, interval, fuel);
                    Check(due == (en && fuel && now - last >= interval), "BeatDue");
                    if (due) ThumperBeats++;
                    Check(!RM_SunKernel.BeatDue(en, last + interval - 1, last, interval, true) && RM_SunKernel.BeatDue(true, last + interval, last, interval, true), "BeatDue boundary");
                    int m = r.Next(0, 14), max = r.Next(0, 6), arrive = r.Next(0, 6);
                    var cands = new List<RM_CallCand>();
                    int d0 = 0;
                    for (int i = 0; i < m; i++)
                    {
                        d0 += r.Next(0, 30);
                        cands.Add(new RM_CallCand { id = i, distSq = d0, player = r.Next(6) == 0, downed = r.Next(6) == 0, cantMove = r.Next(8) == 0, busyHunting = r.Next(5) == 0 });
                    }
                    var noDest = new HashSet<int>(Enumerable.Range(0, m).Where(i => r.Next(5) == 0));
                    int destCalls = 0;
                    var got = RM_SunKernel.SelectCalls(cands, max, arrive, i => { destCalls++; return !noDest.Contains(i); });
                    var elig = Enumerable.Range(0, m).Where(i => !cands[i].player && !cands[i].downed && !cands[i].cantMove && !cands[i].busyHunting && cands[i].distSq > arrive * arrive && !noDest.Contains(i)).Take(max).ToList();
                    Check(got.SequenceEqual(elig), $"calls [{string.Join(",", got)}], spec [{string.Join(",", elig)}]");
                    Check(got.Count <= max, "more calls than the cap");
                    Check(destCalls <= m, "destination probed more than once per swimmer");
                    foreach (int i in got) Check(cands[i].distSq > arrive * arrive, "called a swimmer already at the thumper");
                    ThumperCallsMade += got.Count; Steps += m + 1; Cases++;
                }
            }
            catch (Exception e) { fails.Add("sun-pure: " + e.Message); }
            return fails;
        }

        private static List<Act> GenStill(int seed)
        {
            var r = new Random(seed * 23 + 7);
            var acts = new List<Act>();
            int n = 20 + r.Next(120);
            for (int i = 0; i < n; i++)
            {
                int k = r.Next(100);
                acts.Add(new Act { kind = k < 70 ? 0 : k < 80 ? 1 : k < 90 ? 2 : 3, a = r.Next(1, 40), b = r.Next(0, 5), c = 0, names = StillNames });
            }
            return acts;
        }

        private static string RunStill(int seed, List<Act> acts)
        {
            var r = new Random(seed * 3 + 1);
            int[] tpcs = { 1024, 2048, 4096, 8192 };
            int tpc = tpcs[r.Next(4)];
            float[] rates = { 0.25f, 0.5f, 1f, 2f, 4f };
            float rate = rates[r.Next(rates.Length)];
            float progress = 0f; double sp = 0; int sinceFire = 0;
            try
            {
                foreach (Act a in acts)
                {
                    Steps++; StillStepsRun++;
                    bool feed = a.kind != 1; float rt = a.kind == 2 ? 0f : rate;
                    if (a.kind == 3) rate = rates[a.b % rates.Length];
                    float before = progress;
                    float np = RM_SunKernel.StillStep(progress, feed, rt, 250, tpc, out bool fired);
                    if (!feed) { Check(np == 0f && !fired, "a still with no feed kept progress"); sp = 0; StillResets++; sinceFire = 0; }
                    else if (rt <= 0f) { Check(np == before && !fired, "a still with no sun lost or gained progress"); StillHolds++; }
                    else
                    {
                        sp += 250.0 * rt / tpc; sinceFire++;
                        bool want = sp >= 1.0;
                        Check(fired == want, $"fired {fired}, spec {want} (progress {sp})");
                        if (fired) { sp = 0; StillFired++; Check(np == 0f, "progress not reset after a cycle"); }
                        else Check(np == (float)sp && np < 1f, "progress drifted from the exact accumulation");
                    }
                    Check(np >= 0f && np < 1f, "progress outside [0,1)");
                    progress = np;
                }
                return null;
            }
            catch (Exception e) { return e.Message; }
        }

        // ════════════════════════ units ════════════════════════
        private static List<string> Units()
        {
            var fails = new List<string>();
            try
            {
                Cases++;
                // sign table
                Check(RM_LeviathanKernel.EndNeedsSign(RM_VisitEnd.ArriveFailed) && RM_LeviathanKernel.EndNeedsSign(RM_VisitEnd.Dived) && !RM_LeviathanKernel.EndNeedsSign(RM_VisitEnd.Killed) && !RM_LeviathanKernel.EndNeedsSign(RM_VisitEnd.Gone), "EndNeedsSign table");
                // process gate
                Check(!RM_LeviathanKernel.ShouldProcess(0, 30) && !RM_LeviathanKernel.ShouldProcess(1, 31) && RM_LeviathanKernel.ShouldProcess(1, 30) && RM_LeviathanKernel.ShouldProcess(3, 0), "ShouldProcess");
                // classify
                Check(RM_LeviathanKernel.Classify(true, false, true, false, 0, 0) == RM_VisitClass.Drop && RM_LeviathanKernel.Classify(false, true, false, false, 0, 0) == RM_VisitClass.Drop, "no ext / kind drops the visit");
                Check(RM_LeviathanKernel.Classify(false, false, false, false, 99, 100) == RM_VisitClass.Rumble && RM_LeviathanKernel.Classify(false, false, false, false, 100, 100) == RM_VisitClass.Arrive, "rumble ends exactly at the arrival tick");
                Check(RM_LeviathanKernel.Classify(false, false, true, true, 0, 0) == RM_VisitClass.Drop && RM_LeviathanKernel.Classify(false, false, true, false, 0, 0) == RM_VisitClass.Tick, "pawn gone / alive");
                // arrival
                Check(RM_LeviathanKernel.ResolveArrival(true, true, false) == RM_ArriveCell.UseEntry && RM_LeviathanKernel.ResolveArrival(true, false, true) == RM_ArriveCell.UseFallback && RM_LeviathanKernel.ResolveArrival(false, true, false) == RM_ArriveCell.Fail, "ResolveArrival table");
                // rumble endpoints
                Check(RM_LeviathanKernel.RumbleT(1500, 0, 1500) == 0f && RM_LeviathanKernel.RumbleT(1500, 1500, 1500) == 1f && RM_LeviathanKernel.RumbleT(1500, 1600, 1500) == 1f && RM_LeviathanKernel.RumbleT(1500, -9000, 1500) == 0f && RM_LeviathanKernel.RumbleT(10, 10, 0) == 1f, "RumbleT endpoints / zero warning");
                // dive boundaries
                int hg = 0;
                Check(RM_LeviathanKernel.DecideDive(1, 0, true, 99999, 0, 10, false, 30, ref hg) == RM_DiveReason.Fed, "fed outranks fire and boredom");
                hg = 0; Check(RM_LeviathanKernel.DecideDive(0, 0, true, 99999, 0, 10, false, 30, ref hg) == RM_DiveReason.Fire, "fire outranks boredom");
                hg = 0; Check(RM_LeviathanKernel.DecideDive(0, 0, false, 100, 0, 100, true, 30, ref hg) == RM_DiveReason.None && RM_LeviathanKernel.DecideDive(0, 0, false, 101, 0, 100, true, 30, ref hg) == RM_DiveReason.Bored, "bored is strictly past maxStay");
                hg = 0; Check(RM_LeviathanKernel.DecideDive(0, 0, false, 10, 0, 100, false, 60, ref hg) == RM_DiveReason.None && hg == 30 && RM_LeviathanKernel.DecideDive(0, 0, false, 40, 0, 100, false, 60, ref hg) == RM_DiveReason.None && hg == 60 && RM_LeviathanKernel.DecideDive(0, 0, false, 70, 0, 100, false, 60, ref hg) == RM_DiveReason.HardGround, "hard ground is strictly past the give-up");
                Check(RM_LeviathanKernel.DecideDive(0, 0, false, 70, 0, 100, true, 60, ref hg) == RM_DiveReason.None && hg == 0, "sand resets the clock");
                Check(RM_LeviathanKernel.DiveStep(false, 1250, 0, false) == RM_DiveStep.SeekSand && RM_LeviathanKernel.DiveStep(false, 1251, 0, false) == RM_DiveStep.Dive && RM_LeviathanKernel.DiveStep(true, 0, 0, false) == RM_DiveStep.Dive && RM_LeviathanKernel.DiveStep(false, 10, 0, true) == RM_DiveStep.KeepSeeking, "DiveStep table");
                Check(RM_LeviathanKernel.IsBreach(true, false, false) && !RM_LeviathanKernel.IsBreach(true, false, true) && !RM_LeviathanKernel.IsBreach(false, false, false) && !RM_LeviathanKernel.IsBreach(true, true, false), "IsBreach");
                Check(RM_LeviathanKernel.NeedsStrikeJob(false, true, true) && RM_LeviathanKernel.NeedsStrikeJob(true, false, true) && RM_LeviathanKernel.NeedsStrikeJob(true, true, false) && !RM_LeviathanKernel.NeedsStrikeJob(true, true, true), "NeedsStrikeJob");
                // the player outranks any score, equals keep the first
                Check(RM_LeviathanKernel.BeatsBest(true, false, 0.1f, 99f) && !RM_LeviathanKernel.BeatsBest(false, true, 99f, 0.1f) && !RM_LeviathanKernel.BeatsBest(false, false, 3f, 3f) && RM_LeviathanKernel.BeatsBest(false, false, 3.1f, 3f), "BeatsBest");
                // the ledger's own table
                var bands = new List<float> { 0f, 30f, 90f, 180f };
                Check(RM_LedgerBook.BandFor(bands, 0f) == 0 && RM_LedgerBook.BandFor(bands, 29.99f) == 0 && RM_LedgerBook.BandFor(bands, 30f) == 1 && RM_LedgerBook.BandFor(bands, 180f) == 3 && RM_LedgerBook.BandFor(bands, 1e9f) == 3 && RM_LedgerBook.BandFor(new List<float>(), 50f) == 0, "BandFor boundaries");
                var bk = new RM_LedgerBook();
                RM_LedgerDraw d1 = bk.Draw(95f, bands, -4, 90f);
                Check(d1.crossedOpening && d1.goodwillDelta == -8 && bk.lastBand == 2, "a 95 litre draw: crosses 90, two bands up, -8 goodwill");
                RM_LedgerDraw d2 = bk.Draw(1f, bands, -4, 90f);
                Check(!d2.crossedOpening && d2.goodwillDelta == 0, "a draw past the threshold does not cross it again");
                Check(bk.Pay(500f, bands, -4, out int g) == 96f && g == 0 && bk.debt == 0f && bk.lastBand == 0, "paying more than the debt pays the debt");
                RM_LedgerDraw d3 = bk.Draw(95f, bands, -4, 90f);
                Check(d3.goodwillDelta == -8, "the same bands cost goodwill again after the debt was paid (by design: it is band-up, not first-time)");
                Check(RM_LedgerBook.IncidentFactor(0f, 0.5f, 3f) == 1f && RM_LedgerBook.IncidentFactor(1e6f, 0.5f, 3f) == 3f && RM_LedgerBook.IncidentFactor(100f, 0.5f, 0.2f) == 1f && RM_LedgerBook.IncidentFactor(200f, 0.5f, 3f) == 2f, "IncidentFactor");
                var bk2 = new RM_LedgerBook();
                Check(bk2.TryOpen(0, 30000) && !bk2.TryOpen(29999 , 30000) && bk2.TryOpen(30000, 30000) && bk2.openingSerial == 2, "opening throttle boundary");
                Check(!bk2.TryOpen(30001, 30000) && bk2.openingSerial == 2, "throttle measured from the last ACCEPTED opening");
                Check(RM_SunKernel.StillStep(0.5f, true, 0f, 250, 1024, out bool ff) == 0.5f && !ff, "no rate holds the progress");
            }
            catch (Exception e) { fails.Add("units: " + e.Message); }
            return fails;
        }

        /// <summary>DUST_SETTLED_LETTER_1: for any fire tick and any now, an arrived group never turns back; an unarrived one turns back
        /// exactly when now is past PlumeUntil(fire); the plume never ends before the retry window; the match key is strict.</summary>
        public static List<string> Horizon(int n, int seed)
        {
            var fails = new List<string>();
            var r = new Random(seed);
            for (int i = 0; i < n; i++)
            {
                int fire = r.Next(0, 5_000_000), now = fire + r.Next(-3000, 9000);
                bool arrived = r.Next(2) == 0;
                bool got = RM_HorizonMath.TurnedBack(now, fire, arrived);
                bool want = !arrived && now > fire + RM_HorizonMath.RetryTicks + RM_HorizonMath.GraceTicks;
                Cases++; Steps++;
                if (got != want || RM_HorizonMath.PlumeUntil(fire) < fire + RM_HorizonMath.RetryTicks)
                {
                    fails.Add($"horizon seed {seed} case {i}: fire {fire} now {now} arrived {arrived} -> turnedBack {got}, want {want}");
                    if (fails.Count > 5) break;
                }
                int x = r.Next(0, 250), z = r.Next(0, 250);
                bool m = RM_HorizonMath.Matches("D", x, z, "D", x, z) && !RM_HorizonMath.Matches("D", x, z, "D", x + 1, z) && !RM_HorizonMath.Matches("D", x, z, "E", x, z) && !RM_HorizonMath.Matches("", x, z, "", x, z);
                if (!m) { fails.Add($"horizon seed {seed} case {i}: match key not strict at {x},{z}"); if (fails.Count > 5) break; }
            }
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
                ("leviathan", () => Leviathan(N(2500), S(1))),
                ("ledger", () => Ledger(N(4000), S(1))),
                ("gale", () => Gale(N(2500), S(1))),
                ("sun", () => Sun(N(2500), S(1))),
                ("horizon", () => Horizon(N(8000), S(1))),
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
            Console.WriteLine($"leviathan: visits {VisitsEnqueued}, arrived {VisitsArrived}, arrival failed {ArriveFailed}, fallback cells {ArriveFallback}, dives fed {DivesFed} / fire {DivesFire} / bored {DivesBored} / hard ground {DivesHard}, dived out {DivedOut}, killed or gone {KilledOrGone}, beams {BeamsStarted}, breaches {Breaches}, rumbles {Rumbles}, exact off-sand lifetimes {ExactOffSand}");
            Console.WriteLine($"ledger: draws {LedDraws}, pays {LedPays}, openings accepted {LedOpensAccepted} / refused {LedOpensRefused}, threshold crossings {LedCrossings} (of which inside the opening throttle, so NO opening {LedThrottledCrossings}), band ups {LedBandUps}, downs {LedBandDowns}");
            Console.WriteLine($"gale: wind samples {WindSamples}, carry walks {CarryWalks} (off the map {CarriedOff}, blocked {CarryBlocked}, moved {CarryMoved}; diagonal off a north/south edge {DiagonalOffNorthSouth}), filth cells {CarryFilth}, walk-ins {WalkIns}, book adds {BookAdds}, returned by time {Returned} / by gale end {ReturnedByGale}");
            Console.WriteLine($"sun: factor cases {FactorCases} ({SunReasons} with a reason), still steps {StillStepsRun} (fired {StillFired}, no-feed resets {StillResets}, no-sun holds {StillHolds}), thumper beats due {ThumperBeats}, swimmers called {ThumperCallsMade}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                var blind = new List<string>();
                if (VisitsArrived == 0 || ArriveFailed == 0 || ArriveFallback == 0 || DivesFed == 0 || DivesFire == 0 || DivesBored == 0 || DivesHard == 0 || DivedOut == 0 || KilledOrGone == 0 || BeamsStarted == 0 || Breaches == 0 || Rumbles == 0 || ExactOffSand == 0) blind.Add("leviathan never arrived/failed/fell back/dived (4 ways)/dived out/lost its pawn/beamed/breached/rumbled/lived off-sand");
                if (LedDraws == 0 || LedPays == 0 || LedOpensAccepted == 0 || LedOpensRefused == 0 || LedCrossings == 0 || LedBandUps == 0 || LedBandDowns == 0) blind.Add("ledger never drew/paid/opened/refused/crossed/moved a band");
                if (WindSamples == 0 || CarriedOff == 0 || CarryBlocked == 0 || CarryMoved == 0 || WalkIns == 0 || Returned == 0 || ReturnedByGale == 0) blind.Add("gale never sampled wind / carried off / blocked / moved / walked in / returned (time and gale end)");
                if (StillFired == 0 || StillResets == 0 || StillHolds == 0 || ThumperBeats == 0 || ThumperCallsMade == 0 || SunReasons == 0) blind.Add("sun never fired a still / reset / held / beat / called / gave a reason");
                foreach (var b in blind) { Console.WriteLine("FAIL fuzz is blind: " + b); ok = false; }
            }
            Console.WriteLine($"stillsand fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
