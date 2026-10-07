// Approach B for EmpirePursuit: seeded fuzz over the Verse-free ladder kernel (../../Kernel/EmpireLadderKernel.cs) and the
// pure math it sits on (../../EmpireLadderMath.cs):
//   ladder  whole-game action sequences (arrive / leave / hourly tick / contact checks / storyteller raids / floor raised / rung
//           lowered / settings flipped) against an independent spec of the design text, full state compared after every step
//   timers  the hourly scheduler: a scheduled rung fires on exactly one future hour tick, its warning strictly before, endless cadence
//   math    EmpireLadderMath properties (clamp, climb/hold, decay monotonicity, band table, 60% rule, sighting predicate)
// A failing sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RuthlessPursuingMechanoids;

namespace RuthlessPursuingMechanoids.Fuzz
{
    internal static class EmpirePursuitFuzz
    {
        public static long Cases, Steps, Fires, Climbs, Holds, Terminals, Postponed, Blocked, Remembers, Revived;
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

        // ════════════════════════ ladder ════════════════════════
        private enum A { Arrive, Leave, Hours, Fire, Contact, Aftermath, ProbeDied, Storyteller, RaiseFloor, Lower, Gates, Settings }
        private struct Act
        {
            public A kind; public int m, a, b; public bool f;
            public override string ToString() { return kind + "(" + m + "," + a + "," + b + (f ? ",T" : "") + ")"; }
        }

        private sealed class Rung { public bool exists; public EmpireRungKind kind; public int successTicks, timeoutTicks; public float warnHours; }
        private sealed class Table : IEmpireRungTable
        {
            public Rung[] r = new Rung[7];
            public bool TryGetRung(int i, out EmpireRungKind k)
            {
                k = EmpireRungKind.Probe;
                if (i < 1 || i > 6 || !r[i].exists) return false;
                k = r[i].kind; return true;
            }
        }

        private sealed class Game
        {
            public int now = 5 * 2500;
            public int floor;
            public Dictionary<int, int[]> memory = new Dictionary<int, int[]>();     // tile -> {rung, departedTick}
            public EmpireRungGates gates = new EmpireRungGates { cordonEnabled = true, bombardmentEnabled = true, probesOpen = true };
            public bool remember = true; public int decay = 1;
            public Table table = new Table();
        }

        // ---- the kernel driver (the thin glue the map component runs) ----
        private sealed class KMap
        {
            public int tile; public bool live; public EmpireLadderState st = new EmpireLadderState();
            public int active = -1; public EmpireRungKind activeKind;     // the live contact's rung
            public int raidTimer, warnTimer; public bool anyTimers;
        }

        // ---- the independent spec ----
        private sealed class SMap
        {
            public int tile; public bool live;
            public int next = -1; public bool terminal, blind;
            public int lastFire = -9999999, lastStory = -9999999;
            public int start = -1, progress, ion = -1, bomb = -1; public bool probeDied; public string after;
            public int active = -1; public int kind;
            public int raidTimer, warnTimer;
        }

        private static readonly EmpireRungKind[] Kinds = { EmpireRungKind.Probe, EmpireRungKind.Spotter, EmpireRungKind.Strike, EmpireRungKind.Cordon, EmpireRungKind.Breach, EmpireRungKind.Bombardment };

        private static Act[] GenActs(Random r, int len)
        {
            var a = new Act[len];
            int burst = 0, burstMap = 0; bool bursty = r.Next(2) == 0;
            for (int i = 0; i < len; i++)
            {
                if (burst > 0)   // checks run every 250 ticks in the game: threshold boundaries need consecutive steps
                {
                    burst--;
                    a[i] = new Act { kind = A.Contact, m = burstMap, a = r.Next(8), b = r.Next(1 << 12), f = r.Next(2) == 0 };
                    continue;
                }
                int k = r.Next(100);
                A kind = k < 7 ? A.Arrive : k < 12 ? A.Leave : k < 24 ? A.Hours : k < 40 ? A.Fire : k < 74 ? A.Contact : k < 78 ? A.Aftermath
                    : k < 82 ? A.ProbeDied : k < 88 ? A.Storyteller : k < 91 ? A.RaiseFloor : k < 94 ? A.Lower : k < 97 ? A.Gates : A.Settings;
                a[i] = new Act { kind = kind, m = r.Next(3), a = r.Next(8), b = r.Next(1 << 12), f = r.Next(2) == 0 };
                if (kind == A.Fire && bursty) { burst = r.Next(0, 70); burstMap = a[i].m; }
            }
            return a;
        }

        private static string RunLadder(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x2545F491);
            var g = new Game();
            // a random rung table: usually the shipped one, sometimes with holes or other kinds
            bool shipped = rr.Next(3) != 0;
            for (int i = 1; i <= 6; i++)
            {
                var d = new Rung { exists = shipped || rr.Next(8) != 0, kind = shipped ? Kinds[i - 1] : Kinds[rr.Next(6)] };
                d.successTicks = 250 * (1 + rr.Next(8)); d.timeoutTicks = 250 * (8 + rr.Next(40));   // scaled down so a 200-step case reaches the thresholds d.warnHours = rr.Next(3) == 0 ? 0f : rr.Next(1, 25);
                g.table.r[i] = d;
            }
            var K = new KMap[3]; var S = new SMap[3];
            for (int i = 0; i < 3; i++) { K[i] = new KMap(); S[i] = new SMap(); }
            int spec_floor = 0;
            var specMem = new Dictionary<int, int[]>();
            int stepNo = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    KMap k = K[a.m]; SMap s = S[a.m];
                    switch (a.kind)
                    {
                        case A.Settings:
                            g.remember = a.f; g.decay = a.a % 4;
                            break;
                        case A.Gates:
                            g.gates = new EmpireRungGates { cordonEnabled = (a.a & 1) != 0, bombardmentEnabled = (a.a & 2) != 0, probesOpen = (a.a & 4) != 0 };
                            break;
                        case A.Hours: g.now += a.b % 6 == 0 ? 48 * 2500 : 2500 * (1 + a.a + (a.f ? 24 * (a.b % 20) : 0)); break;   // 48 h exactly = the spacing boundary
                        case A.Arrive:
                            {
                                if (k.live) break;
                                int tile = a.a % 4;
                                k.live = true; k.tile = tile; k.st = new EmpireLadderState(); k.active = -1; 
                                int rem = -1;
                                int[] mem; bool has = g.memory.TryGetValue(tile, out mem);
                                rem = EmpireLadderState.RememberedRung(g.remember, true, has, has ? mem[0] : 0, has ? mem[1] : 0, g.now, 900000, g.decay);
                                k.st.EnsureInit(g.floor, g.gates.probesOpen, rem);
                                // spec
                                s.live = true; s.tile = tile; s.next = -1; s.terminal = false; s.blind = false; s.lastFire = s.lastStory = -9999999; s.start = -1; s.progress = 0;
                                s.ion = s.bomb = -1; s.probeDied = false; s.after = null; s.active = -1;
                                int srem = -1;
                                if (g.remember && specMem.ContainsKey(tile))
                                {
                                    int lost = (int)Math.Floor(Math.Max(0.0, (g.now - specMem[tile][1]) / 900000.0)) * Math.Max(0, g.decay);
                                    srem = Math.Max(0, specMem[tile][0] - lost);
                                }
                                int startRung = g.gates.probesOpen ? 1 : 3;
                                if (srem > startRung) startRung = srem;
                                s.next = Math.Min(6, Math.Max(1, Math.Max(startRung, spec_floor)));
                                if (count && srem >= 0) Remembers++;
                                break;
                            }
                        case A.Leave:
                            {
                                if (!k.live) break;
                                if (EmpireLadderState.ShouldRecordDeparture(true, k.st.nextRung)) g.memory[k.tile] = new[] { k.st.nextRung, g.now };
                                k.live = false;
                                if (s.next >= 0) specMem[s.tile] = new[] { s.next, g.now };
                                s.live = false;
                                break;
                            }
                        case A.RaiseFloor:
                            {
                                int f = a.a % 8;
                                g.floor = EmpireLadderState.RaisedFloor(g.floor, f);
                                for (int i = 0; i < 3; i++) if (K[i].live) K[i].st.ApplyFloor(g.floor);
                                spec_floor = Math.Min(6, Math.Max(spec_floor, Math.Max(0, f)));
                                for (int i = 0; i < 3; i++) if (S[i].live && S[i].next >= 0) S[i].next = Math.Min(6, Math.Max(1, Math.Max(S[i].next, spec_floor)));
                                Check(g.floor == spec_floor, $"floor kernel {g.floor} vs spec {spec_floor}");
                                break;
                            }
                        case A.Lower:
                            {
                                if (!k.live) break;
                                bool revived;
                                bool did = k.st.LowerRung(a.a % 4 - 1, g.floor, out revived);
                                bool sdid = s.next >= 0;
                                bool srevived = false;
                                if (sdid)
                                {
                                    int by = Math.Max(0, a.a % 4 - 1);
                                    bool wasT = s.terminal;
                                    s.next = Math.Min(6, Math.Max(1, Math.Max(s.next - by, spec_floor)));
                                    s.terminal = s.terminal && s.next >= 6;
                                    srevived = wasT && !s.terminal;
                                }
                                Check(did == sdid, "LowerRung applicability differs");
                                Check(revived == srevived, $"LowerRung revived {revived} vs spec {srevived}");
                                if (revived && k.active < 0)
                                {   // the component schedules the next rung; a revived ladder must never be left without a future raid timer
                                    int idx = k.st.NextRungIndex(g.table, g.gates);
                                    float wh = idx >= 0 ? g.table.r[idx].warnHours : 0f;
                                    int raid, warn;
                                    EmpireLadderTimers.Schedule(g.now, 5 * 60000, 1f, wh, out raid, out warn);
                                    k.raidTimer = raid; k.warnTimer = warn; k.anyTimers = true; s.raidTimer = raid; s.warnTimer = warn;
                                    Check(EmpireLadderTimers.TimerIntervalTick(raid) > g.now, "revived ladder scheduled in the past");
                                    if (count) Revived++;
                                }
                                break;
                            }
                        case A.Storyteller:
                            {
                                if (!k.live) break;
                                if (a.f) g.now = (g.now + 2499) / 2500 * 2500;   // on an hour boundary, so a later hourly tick can land exactly on the spacing edge
                                bool block = EmpireLadderState.BlockStorytellerRaid(k.active >= 0, g.now, k.st.lastLadderFireTick);
                                bool sblock = s.active >= 0 || g.now - s.lastFire < 120000;
                                Check(block == sblock, $"storyteller raid block {block} vs spec {sblock}");
                                if (!block) { k.st.lastStorytellerRaidTick = g.now; s.lastStory = g.now; }
                                else if (count) Blocked++;
                                break;
                            }
                        case A.ProbeDied:
                            if (!k.live) break;
                            k.st.anyProbeDestroyed = true; s.probeDied = true;
                            break;
                        case A.Aftermath:
                            if (!k.live || k.active < 0) break;
                            if (k.activeKind == EmpireRungKind.Strike || k.activeKind == EmpireRungKind.Breach)
                            {
                                string o = a.a % 3 == 0 ? "Repelled" : a.a % 3 == 1 ? "Overrun" : "Costly";
                                k.st.aftermathOutcome = o; s.after = o;
                            }
                            break;
                        case A.Fire:
                            {
                                if (!k.live) break;
                                // the hourly tick lands on an hour boundary
                                g.now = (g.now + 2499) / 2500 * 2500;
                                {   // TickLadder calls search.EnsureInit() first, every hour: it must never re-roll an initialised ladder
                                    int[] mm; bool hh = g.memory.TryGetValue(k.tile, out mm);
                                    int rem2 = EmpireLadderState.RememberedRung(g.remember, true, hh, hh ? mm[0] : 0, hh ? mm[1] : 0, g.now, 900000, g.decay);
                                    k.st.EnsureInit(g.floor, g.gates.probesOpen, rem2);
                                }
                                // timers: scheduled state present?
                                bool live = k.active >= 0;
                                bool warn = k.anyTimers && EmpireLadderTimers.ShouldWarn(live, k.st.terminal, g.now, k.warnTimer, k.raidTimer);
                                bool swarn = s.raidTimer != 0 && s.active < 0 && !s.terminal && g.now == Ceil(s.warnTimer) && Ceil(s.warnTimer) != Ceil(s.raidTimer);
                                Check(warn == swarn, $"warn decision {warn} vs spec {swarn}");
                                // an unscheduled ladder fires when its fire flag is forced by the action (the scenario part's first timer)
                                bool fire = k.anyTimers ? EmpireLadderTimers.ShouldFire(live, k.st.terminal, g.now, k.raidTimer) : a.f;
                                bool sfire = s.raidTimer != 0 ? (s.active < 0 && !s.terminal && g.now == Ceil(s.raidTimer)) : a.f;
                                Check(fire == sfire, $"fire decision {fire} vs spec {sfire}");
                                if (!fire) { bool en = EmpireLadderTimers.ShouldEndless(k.st.terminal, true, false, g.now, 3 * 2500); Check(en == (s.terminal && g.now % 7500 == 0), "endless decision"); break; }
                                int before = k.st.nextRung;
                                // component FireNextRung
                                int gate = k.st.FireGate(live, g.now);
                                // spec
                                int sgate;
                                if (s.active >= 0 || s.terminal) sgate = 0;
                                else if (g.now - s.lastStory < 120000) sgate = 120000 - (g.now - s.lastStory);
                                else sgate = -1;
                                Check(gate == sgate, $"FireGate {gate} vs spec {sgate}");
                                if (gate > 0)
                                {
                                    k.raidTimer = g.now + gate; k.warnTimer = k.raidTimer; k.anyTimers = true;
                                    s.raidTimer = g.now + sgate; s.warnTimer = s.raidTimer;
                                    Check(Ceil(k.raidTimer) > g.now, "a postponed rung would be scheduled at or before this tick");
                                    if (count) Postponed++;
                                    break;
                                }
                                if (gate == 0) break;
                                // pick the rung
                                int idx = k.st.NextRungIndex(g.table, g.gates);
                                int sidx = -1;
                                for (int r = s.next; r <= 6; r++)
                                {
                                    Rung d = g.table.r[r];
                                    if (!d.exists) continue;
                                    int kd = Array.IndexOf(Kinds, d.kind);
                                    if (kd == 3 && !g.gates.cordonEnabled) continue;
                                    if (kd == 5 && !g.gates.bombardmentEnabled) continue;
                                    if (kd == 0 && !g.gates.probesOpen) continue;
                                    sidx = r; break;
                                }
                                Check(idx == sidx, $"NextRungIndex {idx} vs spec {sidx} (from {before})");
                                if (idx < 0) { k.st.MarkExhausted(); s.terminal = true; if (count) Terminals++; break; }
                                Check(idx >= before, "fired a rung below nextRung");
                                Check(g.now - k.st.lastStorytellerRaidTick >= EmpireLadderState.StorytellerSpacingTicks, "fired inside the storyteller spacing");
                                k.st.Begin(idx, g.now); k.active = idx; k.activeKind = g.table.r[idx].kind;
                                s.next = idx; s.start = g.now; s.progress = 0; s.probeDied = false; s.after = null; s.lastFire = g.now; s.active = idx; s.kind = Array.IndexOf(Kinds, g.table.r[idx].kind);
                                if (g.table.r[idx].kind == EmpireRungKind.Cordon) { k.st.nextIonTick = g.now + 60000; s.ion = g.now + 60000; }
                                if (g.table.r[idx].kind == EmpireRungKind.Bombardment) { int t = g.now + 24 * 2500; k.st.bombardTick = t; s.bomb = t; }
                                if (count) Fires++;
                                // a rung that could not fire: resolved as a quiet failure
                                if (!a.f && a.a == 0) Resolve(g, k, s, false, ref spec_floor, count);
                                break;
                            }
                        case A.Contact:
                            {
                                if (!k.live || k.active < 0) break;
                                g.now += (250 - g.now % 250 == 0 ? 250 : 250 - g.now % 250);
                                Rung d = g.table.r[k.active];
                                int elapsed = g.now - k.st.contactStartTick, selapsed = g.now - s.start;
                                Check(elapsed == selapsed, "contact elapsed differs");
                                bool b1 = (a.b & 1) != 0, b2 = (a.b & 2) != 0, b3 = (a.b & 4) != 0, b4 = (a.b & 8) != 0, b5 = (a.b & 16) != 0;
                                int raiders = a.b >> 5 & 7, down = Math.Min(raiders, a.b >> 8 & 7);
                                ContactOutcome o = ContactOutcome.Continue; float vis = 0f; bool volley = false;
                                // spec outcome
                                int so = 0; float svis = 0f; bool svolley = false;   // 0 continue 1 empire wins 2 empire fails
                                switch (d.kind)
                                {
                                    case EmpireRungKind.Probe:
                                        o = k.st.ProbeStep(b1, d.successTicks, b2, elapsed, d.timeoutTicks, out vis);
                                        if (b1) s.progress += 250;
                                        if (s.progress >= d.successTicks) { so = 1; svis = 8f; s.blind = false; }
                                        else if (b2 || selapsed > d.timeoutTicks + 60000) { so = 2; svis = s.probeDied ? -3f : 0f; s.blind = !s.probeDied; }
                                        break;
                                    case EmpireRungKind.Spotter:
                                        o = k.st.SpotterStep(b3, b1, d.successTicks, elapsed, d.timeoutTicks, out vis);
                                        if (b3) so = 2;
                                        else { if (b1) s.progress += 250; if (s.progress >= d.successTicks) { so = 1; svis = 8f; } else if (selapsed > d.timeoutTicks) so = 2; }
                                        break;
                                    case EmpireRungKind.Cordon:
                                        o = k.st.CordonStep(b1, g.now, 8 * 2500, elapsed, d.successTicks, out volley);
                                        if (b1 && s.ion > 0 && g.now >= s.ion) { svolley = true; s.ion = g.now + 8 * 2500; }
                                        if (!b1) so = 2; else if (selapsed >= d.successTicks) so = 1;
                                        break;
                                    case EmpireRungKind.Strike:
                                    case EmpireRungKind.Breach:
                                        o = k.st.StrikeStep(b2, elapsed, d.timeoutTicks, raiders, down);
                                        if (s.after != null) so = s.after == "Repelled" ? 2 : 1;
                                        else if (b2 || selapsed > d.timeoutTicks) so = (raiders <= 0 || down * 10 >= raiders * 6) ? 2 : 1;
                                        break;
                                    case EmpireRungKind.Bombardment:
                                        if (k.st.BombardmentDue(g.now)) { k.st.BombardmentLanded(); o = ContactOutcome.EmpireSucceeds; }
                                        if (s.bomb > 0 && g.now >= s.bomb) { s.bomb = -1; s.terminal = true; so = 1; }
                                        break;
                                }
                                int ko = o == ContactOutcome.Continue ? 0 : o == ContactOutcome.EmpireSucceeds ? 1 : 2;
                                Check(ko == so, $"contact outcome {o} vs spec {so} on {d.kind}");
                                Check(vis == svis, $"visibility delta {vis} vs spec {svis} on {d.kind}");
                                Check(volley == svolley, "ion volley decision differs");
                                if (ko != 0) Resolve(g, k, s, ko == 1, ref spec_floor, count);
                                break;
                            }
                    }
                    Compare(g, K, S, spec_floor, specMem);
                }
            }
            catch (Exception e) { return $"step {stepNo}: {e.Message}"; }
            return null;
        }

        private static int Ceil(int t) { return (t + 2499) / 2500 * 2500; }

        // Resolve + reschedule on both sides.
        private static void Resolve(Game g, KMap k, SMap s, bool succeeded, ref int specFloor, bool count)
        {
            int fired = k.active;
            bool sched = k.st.Resolve(fired, succeeded, g.floor);
            k.active = -1;
            // spec
            int sfired = s.active;
            if (sfired >= 0)
            {
                int n = succeeded ? sfired + 1 : sfired;
                s.next = Math.Min(6, Math.Max(1, Math.Max(n, specFloor)));
                if (sfired >= 6 && succeeded) s.terminal = true;
                if (count) { if (succeeded && sfired < 6) Climbs++; else if (!succeeded) Holds++; }
            }
            s.start = -1; s.progress = 0; s.ion = -1; s.after = null; s.active = -1;
            Check(sched == !s.terminal, $"Resolve schedule flag {sched} vs spec {!s.terminal}");
            if (sched)
            {
                // next rung timers: the warning is the NEXT rung's, found with the same table walk
                int idx = k.st.NextRungIndex(g.table, g.gates);
                float wh = idx >= 0 ? g.table.r[idx].warnHours : 0f;
                int raw = 5 * 60000 + (k.st.nextRung * 977);
                int raid, warn;
                EmpireLadderTimers.Schedule(g.now, raw, 1.25f, wh, out raid, out warn);
                k.raidTimer = raid; k.warnTimer = warn; k.anyTimers = true;
                int sraid = g.now + Math.Max((int)Math.Round(raw * 1.25f), 2500);
                int swarn = wh > 0f ? Math.Max(g.now + 2500, sraid - (int)Math.Round(wh * 2500f)) : sraid;
                s.raidTimer = sraid; s.warnTimer = swarn;
                Check(raid == sraid && warn == swarn, $"schedule kernel ({raid},{warn}) vs spec ({sraid},{swarn})");
            }
        }

        private static void Compare(Game g, KMap[] K, SMap[] S, int specFloor, Dictionary<int, int[]> specMem)
        {
            for (int i = 0; i < 3; i++)
            {
                KMap k = K[i]; SMap s = S[i];
                Check(k.live == s.live, $"map {i} liveness");
                if (!k.live) continue;
                EmpireLadderState t = k.st;
                Check(t.nextRung == s.next, $"map {i} nextRung kernel {t.nextRung} vs spec {s.next}");
                Check(t.terminal == s.terminal, $"map {i} terminal kernel {t.terminal} vs spec {s.terminal}");
                Check(t.lastProbeBlind == s.blind, $"map {i} lastProbeBlind");
                Check(t.lastLadderFireTick == s.lastFire, $"map {i} lastLadderFireTick");
                Check(t.lastStorytellerRaidTick == s.lastStory, $"map {i} lastStorytellerRaidTick");
                Check(t.contactStartTick == s.start, $"map {i} contactStartTick {t.contactStartTick} vs {s.start}");
                Check(t.progressTicks == s.progress, $"map {i} progress {t.progressTicks} vs {s.progress}");
                Check(t.nextIonTick == s.ion, $"map {i} nextIon {t.nextIonTick} vs {s.ion}");
                Check(t.bombardTick == s.bomb, $"map {i} bombardTick {t.bombardTick} vs {s.bomb}");
                Check(t.anyProbeDestroyed == s.probeDied, $"map {i} anyProbeDestroyed");
                Check(t.aftermathOutcome == s.after, $"map {i} aftermath");
                Check(k.active == s.active, $"map {i} active rung {k.active} vs {s.active}");
                if (k.anyTimers) Check(k.raidTimer == s.raidTimer && k.warnTimer == s.warnTimer, $"map {i} timers");
                // invariants of the design
                if (t.nextRung >= 0) Check(t.nextRung >= Math.Max(1, g.floor) && t.nextRung <= 6, $"map {i} nextRung {t.nextRung} outside [max(1,floor {g.floor}), 6]");
                if (k.active >= 0) Check(!t.terminal || k.activeKind == EmpireRungKind.Bombardment || k.active >= 0, "live contact on a terminal ladder");
                if (k.active >= 0) Check(t.contactStartTick >= 0, "a live contact has no start tick");
                else Check(t.contactStartTick == -1 && t.progressTicks == 0 && t.nextIonTick == -1 && t.aftermathOutcome == null, $"map {i}: idle ladder carries contact state");
                Check(g.floor == specFloor, "floor drifted");
            }
            foreach (var kv in specMem) { int[] m; Check(g.memory.TryGetValue(kv.Key, out m) && m[0] == kv.Value[0] && m[1] == kv.Value[1], $"tile memory {kv.Key} differs"); }
        }

        private static List<string> Ladder(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed);
                var acts = GenActs(r, 40 + r.Next(160)); Cases++;
                if (RunLadder(acts, seed, true) == null) continue;
                var small = Shrink(acts.ToList(), t => RunLadder(t, seed, false) != null);
                fails.Add($"ladder seed {seed}: {RunLadder(small, seed, false)} | {string.Join(" ", small)}");
                if (fails.Count >= 3) break;
            }
            return fails;
        }

        // ════════════════════════ timers ════════════════════════
        private static List<string> Timers(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed); Cases++;
                try
                {
                    int now = r.Next(0, 100000000);
                    int rawDelay = r.Next(3) == 0 ? r.Next(0, 20000) : r.Next(0, 3 * 60000 * 12); float factor = r.Next(3) == 0 ? 0.05f + (float)r.NextDouble() * 0.95f : 0.05f + (float)r.NextDouble() * 6f; float wh = r.Next(3) == 0 ? 0f : r.Next(1, 49);
                    int raid, warn;
                    EmpireLadderTimers.Schedule(now, rawDelay, factor, wh, out raid, out warn);
                    Check(raid >= now + 2500, $"raid timer {raid} is under an hour from now {now}");
                    Check(warn >= now + 2500 && warn <= raid, $"warn timer {warn} outside [now+1h, raid {raid}]");
                    if (wh <= 0f) Check(warn == raid, "no warning hours but warn != raid");
                    int raidTick = EmpireLadderTimers.TimerIntervalTick(raid), warnTick = EmpireLadderTimers.TimerIntervalTick(warn);
                    Check(raidTick % 2500 == 0 && raidTick >= raid && raidTick - raid < 2500, "TimerIntervalTick is not the next hour boundary");
                    Check(EmpireLadderTimers.TimerIntervalTick(raidTick) == raidTick, "TimerIntervalTick not idempotent on a boundary");
                    // walk the hourly ticks after 'now'
                    int firstTick = (now / 2500 + 1) * 2500; int fireHits = 0, warnHits = 0, firstWarn = -1, firstFire = -1;
                    for (int t = firstTick; t <= raidTick + 2500 * 3; t += 2500)
                    {
                        Steps++;
                        bool w = EmpireLadderTimers.ShouldWarn(false, false, t, warn, raid), f = EmpireLadderTimers.ShouldFire(false, false, t, raid);
                        Check(!(w && f), $"warn and fire on the same tick {t}");
                        if (w) { warnHits++; if (firstWarn < 0) firstWarn = t; }
                        if (f) { fireHits++; if (firstFire < 0) firstFire = t; }
                        Check(!EmpireLadderTimers.ShouldWarn(true, false, t, warn, raid) && !EmpireLadderTimers.ShouldFire(true, false, t, raid), "a live contact must block warn/fire");
                        Check(!EmpireLadderTimers.ShouldWarn(false, true, t, warn, raid) && !EmpireLadderTimers.ShouldFire(false, true, t, raid), "a terminal ladder must block warn/fire");
                    }
                    Check(fireHits == 1, $"the rung fires on {fireHits} hour ticks, want exactly 1 (raid {raid}, now {now})");
                    Check(firstFire == raidTick, "fires on the wrong tick");
                    if (warnTick != raidTick) { Check(warnHits == 1 && firstWarn == warnTick && warnTick < raidTick, $"warning hits {warnHits} at {firstWarn}, want one at {warnTick} before {raidTick}"); }
                    else Check(warnHits == 0, "warning fired on the raid tick");
                    // a postponement is never lost: any postponed timer fires on a later hour tick
                    int postpone = r.Next(1, 120001); int pt = (now / 2500) * 2500; int pr = pt + postpone;
                    Check(EmpireLadderTimers.TimerIntervalTick(pr) > pt, "postponed rung would fire on or before the tick that postponed it");
                    // endless cadence
                    int interval = 2500 * r.Next(1, 100);
                    int hits = 0; for (int t = 0; t < interval * 6; t += 2500) if (EmpireLadderTimers.ShouldEndless(true, true, false, t, interval)) hits++;
                    Check(hits == 6, $"endless waves fired {hits} times in 6 intervals");
                    Check(!EmpireLadderTimers.ShouldEndless(false, true, false, 0, interval) && !EmpireLadderTimers.ShouldEndless(true, false, false, 0, interval) && !EmpireLadderTimers.ShouldEndless(true, true, true, 0, interval), "endless gates");
                }
                catch (Exception e) { fails.Add($"timers seed {seed}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            return fails;
        }

        // ════════════════════════ math ════════════════════════
        private static List<string> Math_(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed); Cases++; Steps++;
                try
                {
                    int rung = r.Next(-3, 12), floor = r.Next(-2, 9);
                    int c = EmpireLadderMath.Clamp(rung, floor);
                    Check(c >= 1 && c <= 6 && c >= Math.Min(floor, 6), $"Clamp({rung},{floor})={c}");
                    Check(EmpireLadderMath.Clamp(c, floor) == c, "Clamp not idempotent");
                    foreach (bool ok in new[] { true, false })
                    {
                        int fr = r.Next(1, 7);
                        int nx = EmpireLadderMath.NextRungAfter(fr, ok, floor);
                        Check(nx >= 1 && nx <= 6 && nx >= Math.Min(floor, 6), "NextRungAfter outside [1,6]/floor");
                        if (ok) Check(nx == Math.Min(6, Math.Max(fr + 1, Math.Max(floor, 1))), $"success from {fr} floor {floor} -> {nx}");
                        else Check(nx == Math.Max(fr, Math.Min(6, Math.Max(floor, 1))), $"hold from {fr} floor {floor} -> {nx}");
                    }
                    bool probes = r.Next(2) == 0; int rem = r.Next(-1, 8);
                    int sr = EmpireLadderMath.StartingRung(floor, probes, rem);
                    Check(sr >= 1 && sr <= 6 && sr >= Math.Min(floor, 6) && sr >= (probes ? 1 : 3), $"StartingRung({floor},{probes},{rem})={sr}");
                    if (rem > (probes ? 1 : 3)) Check(sr >= Math.Min(rem, 6), "a remembered higher rung was ignored");
                    int rd = r.Next(0, 7); float se = (float)(r.NextDouble() * 8 - 1); int dps = r.Next(-1, 5);
                    int d1 = EmpireLadderMath.DecayedRung(rd, se, dps), d2 = EmpireLadderMath.DecayedRung(rd, se + 1f, dps);
                    Check(d1 >= 0 && d1 <= rd, "decay out of [0,rung]"); Check(d2 <= d1, "more time away raised the rung");
                    float v1 = (float)(r.NextDouble() * 120 - 5), v2 = v1 + (float)r.NextDouble() * 40;
                    Check(EmpireLadderMath.BandIntervalMultiplier(v1) >= EmpireLadderMath.BandIntervalMultiplier(v2) || v1 < 0f, "a more visible colony paced SLOWER");
                    int raiders = r.Next(0, 40), dn = r.Next(0, raiders + 3);
                    bool rep = EmpireLadderMath.Repelled(raiders, dn);
                    Check(rep == (raiders <= 0 || dn * 10 >= raiders * 6), $"Repelled({raiders},{dn})={rep} vs exact 60%");
                    float dist = (float)(r.NextDouble() * 60), glow = (float)r.NextDouble();
                    bool s1 = EmpireLadderMath.Sees(dist, true, glow), s2 = EmpireLadderMath.Sees(dist + 5f, true, glow);
                    Check(!s2 || s1, "seen farther away but not nearer"); Check(!EmpireLadderMath.Sees(dist, false, glow), "seen without line of sight");
                    float f1 = EmpireLadderMath.RungIntervalFactor(r.Next(1, 7), r.Next(2) == 0);
                    Check(f1 == 0.5f || f1 == 1f || f1 == 1.5f, "interval factor off the table");
                    // memory + floor + spacing helpers
                    int fl = EmpireLadderState.RaisedFloor(r.Next(0, 7), r.Next(-3, 12));
                    Check(fl >= 0 && fl <= 6, "RaisedFloor out of [0,6]");
                    int cur = r.Next(0, 7);
                    Check(EmpireLadderState.RaisedFloor(cur, r.Next(-3, 12)) >= cur, "the permanent floor went DOWN");
                    Check(EmpireLadderState.RememberedRung(false, true, true, 4, 0, 5000000, 900000, 1) == -1 && EmpireLadderState.RememberedRung(true, false, true, 4, 0, 5000000, 900000, 1) == -1
                          && EmpireLadderState.RememberedRung(true, true, false, 4, 0, 5000000, 900000, 1) == -1, "memory gates");
                }
                catch (Exception e) { fails.Add($"math seed {seed}: {e.Message}"); if (fails.Count >= 3) break; }
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
                ("ladder", () => Ladder(N(8000), S(1))),
                ("timers", () => Timers(N(3000), S(1))),
                ("math", () => Math_(N(5000), S(1))),
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
            if (only == null || only == "ladder")
            {
                Console.WriteLine($"ladder reached: fires {Fires}, climbs {Climbs}, holds {Holds}, terminal {Terminals}, postponed {Postponed}, storyteller refusals {Blocked}, remembered tiles {Remembers}, revived ladders {Revived}");
                if (!oneSeed.HasValue && scale >= 1 && (Fires == 0 || Climbs == 0 || Holds == 0 || Terminals == 0 || Postponed == 0 || Blocked == 0 || Remembers == 0 || Revived == 0)) { Console.WriteLine("FAIL ladder fuzz never reached a transition (blind)"); ok = false; }
            }
            Console.WriteLine($"empirepursuit fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
