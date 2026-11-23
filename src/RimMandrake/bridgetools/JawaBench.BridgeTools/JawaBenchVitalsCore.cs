// JawaBenchVitalsCore.cs - the PURE half of the test-state monitor (TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO).
// Design: design/RimMandrake/test_control/monitor_governor_build.md; basis GPT review §5
// (design/RimMandrake/test_control/test_control_review_gpt_20261013.md) and the owner's "Test disturbances" rulings
// (design/RimMandrake/debug_process.md).
//
// ⛔ Compiled into bridgetools/AwarenessSelfTest too (UnitsVitals.cs): a `using Verse;` here breaks that build.
//
// What lives here (every rule unit-tested offline):
//   * PawnObs + Diff: what changed between two samples of a map's spawned pawns -> triggers (arrival, downed, hurt,
//     colonist turned hostile, starving, mental state, departed). A pawn that LEAVES the spawned set is "departed",
//     never dead: deaths come only from the Kill hook's tombstone (absence is not death, GPT §2.3).
//   * Latch: every trigger, in order, bounded; the first non-info one is kept apart (first disturbance tick).
//   * ClockLedger: processed ticks (DoSingleTick) vs TicksGame. A change of TicksGame that no DoSingleTick made is a
//     DISCONTINUITY (reassignment), detected between ticks and between frames (so while paused too). A reassignment the
//     caller declared beforehand (time_set_ticks with a time exception) is recorded as declared, never hidden.
//   * Advance policy and stop rules for jawa/safe_advance.
//   * Rollups keep role (cls) and relationship (rel) as SEPARATE labels: an animal can be hostile, a mech friendly.
//   * Absent mood/food is NOT APPLICABLE (NaN / null), never zero.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchVitalsCore
    {
        // ------------------------------------------------------------------ channels (each has its own switch + meter)
        internal const string ChPawns = "pawns", ChThreats = "threats", ChClock = "clock", ChUi = "ui", ChSubjects = "subjects",
                              ChHeartbeat = "heartbeat";
        internal static readonly string[] Channels = { ChPawns, ChThreats, ChClock, ChUi, ChSubjects, ChHeartbeat };

        internal const int SampleEveryTicks = 60;          // T60 on PROCESSED ticks, not TicksGame % 60
        internal const int ThreatEveryTicks = 240;         // threat-structure census cadence (ticks)
        internal const double WallPassSeconds = 0.25;      // W250
        internal const double HeartbeatSeconds = 5.0;
        internal const double RollupMinWallSeconds = 1.0;  // a rollup row at most once per wall second unless it changed
        internal const double ModalStuckSeconds = 30.0;    // a blocking window older than this latches modal_stuck
        internal const float HurtDrop = 0.05f;             // GPT §2.3 illustrative: health drop >= 0.05 between samples
        internal const int LatchCapacity = 512;
        internal const int TombCapacity = 256;
        internal const int MaxChunk = 60;                  // GPT §3.1: chunks no larger than 60 ticks
        internal const long DefaultAdvanceBudget = 30000;  // per call on a populated map without a declared budget (half a day)
        internal const long HardAdvanceCap = 1200000;      // never, exception or not (20 days)

        // severities
        internal const string SInfo = "info", SThreat = "threat", SDamage = "damage", SBlock = "block", SClock = "clock",
                              SCoverage = "coverage";

        // trigger kinds
        internal const string KDeath = "death", KDowned = "downed", KHurt = "hurt", KColonistHostile = "colonist_hostile",
                              KHostileArrival = "hostile_arrival", KThreatStructure = "threat_structure", KModalStuck = "modal_stuck",
                              KColonyLoss = "colony_loss", KStarving = "starving", KMental = "mental", KClock = "clock_discontinuity",
                              KSpecimenLost = "specimen_lost", KCoverage = "coverage", KDeparted = "departed", KLetter = "letter",
                              KCancel = "cancel";

        internal static readonly string[] DefaultStopKinds =
            { KDeath, KDowned, KHurt, KColonistHostile, KHostileArrival, KThreatStructure, KModalStuck, KColonyLoss, KStarving,
              KMental, KClock, KSpecimenLost, KCoverage, KCancel };

        // ------------------------------------------------------------------ pawn observation
        internal sealed class PawnObs
        {
            internal int Id, Map, X, Z;
            internal string Label, Def, Kind, Cls, Rel, Mental, Food, Job, Newest;   // Newest: youngest hediff (colonists/critical)
            internal string NewestWound;   // youngest Hediff_Injury or Hediff_MissingPart (colonists/critical), same format as Newest
            internal string Ailments;      // a downed colonist's/critical actor's bad hediffs, worst first (AilmentList)
            internal bool Downed, Hostile, Colonist, Critical;
            // OffMap: at death, on no map, in no caravan and in no transporter: a world pawn (an abandoned colony's colonist,
            // a pawn away on a quest). Its harm cannot touch the test (RIMMANDRAKE_IGNORE_OFFMAP_COLONIST_DEATH_HEART_ATTACK_TWICE:
            // Randall, map -1, a heart attack, stopped two Pyrelands rows). Set only by the Kill hook; a sampled pawn is spawned.
            internal bool OffMap;
            internal float Health = float.NaN, Bleed, Mood = float.NaN, MoodBreak = float.NaN;
            internal float Wounds = float.NaN;   // WoundScore of the pawn's wounds; NaN = not read (the hurt stop then stands)

            internal string Json()
            {
                var sb = new StringBuilder(200);
                sb.Append("{\"id\":").Append(Id).Append(",\"map\":").Append(Map)
                  .Append(",\"label\":").Append(J(Label)).Append(",\"def\":").Append(J(Def))
                  .Append(",\"cls\":").Append(J(Cls)).Append(",\"rel\":").Append(J(Rel))
                  .Append(",\"downed\":").Append(B(Downed)).Append(",\"hostile\":").Append(B(Hostile))
                  .Append(",\"colonist\":").Append(B(Colonist)).Append(",\"critical\":").Append(B(Critical))
                  .Append(",\"health\":").Append(F(Health, 3)).Append(",\"bleed\":").Append(F(Bleed, 3))
                  .Append(",\"mood\":").Append(F(Mood, 3)).Append(",\"moodBreak\":").Append(F(MoodBreak, 3))
                  .Append(",\"mental\":").Append(J(Mental)).Append(",\"food\":").Append(J(Food))
                  .Append(",\"job\":").Append(J(Job)).Append(",\"x\":").Append(X).Append(",\"z\":").Append(Z).Append('}');
                return sb.ToString();
            }

            /// <summary>Worth a per-pawn delta row: any state change, health moved >= 0.02, mood moved >= 0.05.</summary>
            internal bool Changed(PawnObs o)
            {
                if (o == null) return true;
                if (Downed != o.Downed || Hostile != o.Hostile || Mental != o.Mental || Food != o.Food || Cls != o.Cls || Rel != o.Rel ||
                    Map != o.Map || (Bleed > 0) != (o.Bleed > 0)) return true;
                if (Moved(Health, o.Health, 0.02f) || Moved(Mood, o.Mood, 0.05f)) return true;
                return false;
            }

            private static bool Moved(float a, float b, float d)
            {
                if (float.IsNaN(a) != float.IsNaN(b)) return true;
                return !float.IsNaN(a) && Math.Abs(a - b) >= d;
            }
        }

        // ------------------------------------------------------------------ triggers + latch
        internal sealed class Trigger
        {
            internal long Seq;
            internal string Kind, Severity, Subject, Detail;
            internal int SubjectId = -1, Tick, Map = -1;
            internal bool Critical, Declared;
            internal double Mono;

            internal string Json()
            {
                return "{\"seq\":" + Seq + ",\"kind\":" + J(Kind) + ",\"severity\":" + J(Severity) + ",\"tick\":" + Tick +
                       ",\"mono\":" + F(Mono, 3) + ",\"map\":" + Map + ",\"subjectId\":" + SubjectId + ",\"subject\":" + J(Subject) +
                       ",\"critical\":" + B(Critical) + ",\"declared\":" + B(Declared) + ",\"detail\":" + J(Detail) + "}";
            }
        }

        internal sealed class Latch
        {
            private readonly List<Trigger> _all = new List<Trigger>();
            private readonly object _gate = new object();
            internal long Seq, Overflow;
            internal Trigger First;          // first non-info trigger since the last Clear

            internal Trigger Add(Trigger t)
            {
                lock (_gate)
                {
                    t.Seq = ++Seq;
                    if (_all.Count >= LatchCapacity) { _all.RemoveAt(0); Overflow++; }
                    _all.Add(t);
                    if (First == null && t.Severity != SInfo && !t.Declared) First = t;
                    return t;
                }
            }

            internal List<Trigger> Since(long seq)
            {
                lock (_gate)
                {
                    var r = new List<Trigger>();
                    foreach (var t in _all) if (t.Seq > seq) r.Add(t);
                    return r;
                }
            }

            internal int Count { get { lock (_gate) return _all.Count; } }

            internal void Clear() { lock (_gate) { _all.Clear(); First = null; Overflow = 0; } }
        }

        internal static Trigger T(string kind, string sev, int tick, PawnObs p, string detail)
        {
            var t = new Trigger { Kind = kind, Severity = sev, Tick = tick, Detail = detail };
            if (p != null) { t.SubjectId = p.Id; t.Subject = p.Label; t.Critical = p.Critical; t.Map = p.Map; }
            return t;
        }

        /// <summary>A pawn whose harm damages the test: a required actor, or (absent any declared actors) any colonist.</summary>
        /// A colonist off every map (OffMap) does not matter unless it is a declared actor.
        internal static bool Matters(PawnObs p, bool anyCritical) => p.Critical || (!anyCritical && p.Colonist && !p.OffMap);

        /// <summary>A death's severity: damage when the pawn matters, threat for another colonist on a map or journey, else
        /// info. An off-map colonist's death is info: it never stops an advance.</summary>
        internal static string DeathSeverity(PawnObs p, bool anyCritical) =>
            Matters(p, anyCritical) ? SDamage : (p.Colonist && !p.OffMap ? SThreat : SInfo);

        // ------------------------------------------------------------------ wounds (RIMMANDRAKE_SHIELD_PYRE_WALK_FROM_FULL_LIST_EVENTS)
        // In vanilla 1.6 only Hediff_Injury and Hediff_MissingPart override SummaryHealthPercentImpact (Verse/SummaryHealthHandler.cs,
        // RimSage 2026-11-21). A summary-health drop with no new wound is another mod's hediff class: his 315-mod list read
        // "health 1 -> 0.87; newest hediff SEX_Penis/SEX_Reproduction age 0" and stopped a two-week walk on it.
        internal const float MissingPartWeight = 100f;   // a part lost outweighs any injury severity sum: either rising is a wound
        internal const float WoundRiseEps = 0.001f;      // float noise on a severity sum; an injury's smallest severity is far above

        /// <summary>Injury severities summed, plus MissingPartWeight per missing part. Pure.</summary>
        internal static float WoundScore(float injurySeveritySum, int missingParts) => injurySeveritySum + MissingPartWeight * missingParts;

        /// <summary>True when a new wound came between two samples, or when either sample did not read wounds (could not look:
        /// the stop stands). Pure.</summary>
        internal static bool WoundRose(PawnObs prev, PawnObs cur)
        {
            if (prev == null || cur == null || float.IsNaN(prev.Wounds) || float.IsNaN(cur.Wounds)) return true;
            return cur.Wounds > prev.Wounds + WoundRiseEps;
        }

        internal sealed class Ail { internal string Def, Part; internal float Sev; }

        /// <summary>"B/Leg 0.90, C 0.50 (+1 more)": the worst `max` hediffs by severity; null when there are none. Pure.</summary>
        internal static string AilmentList(List<Ail> xs, int max)
        {
            if (xs == null || xs.Count == 0) return null;
            var s = new List<Ail>(xs);
            s.Sort((a, b) => b.Sev.CompareTo(a.Sev));
            var sb = new StringBuilder();
            for (int i = 0; i < s.Count && i < max; i++)
            {
                if (i > 0) sb.Append(", ");
                sb.Append(s[i].Def).Append(s[i].Part != null ? "/" + s[i].Part : "").Append(' ').Append(F(s[i].Sev, 2));
            }
            if (s.Count > max) sb.Append(" (+").Append(s.Count - max).Append(" more)");
            return sb.ToString();
        }

        // ------------------------------------------------------------------ diff of two samples (one map)
        /// <summary>prev = null for the baseline sample: hostiles already present are reported once as present-at-arm.</summary>
        internal static List<Trigger> Diff(Dictionary<int, PawnObs> prev, List<PawnObs> cur, bool anyCritical, int tick)
        {
            var outT = new List<Trigger>();
            var seen = new HashSet<int>();
            foreach (var c in cur)
            {
                seen.Add(c.Id);
                PawnObs p = null;
                bool had = prev != null && prev.TryGetValue(c.Id, out p);
                bool matters = Matters(c, anyCritical);
                if (!had)
                {
                    if (c.Hostile)
                        outT.Add(T(KHostileArrival, SThreat, tick, c, (prev == null ? "present at arm: " : "arrived: ") + c.Def + " " + c.Kind + " (" + c.Cls + ")"));
                    if (c.Hostile && c.Colonist)
                        outT.Add(T(KColonistHostile, matters ? SDamage : SThreat, tick, c, "colonist hostile to the player (" + (c.Mental ?? "faction") + ")"));
                    continue;
                }
                if (!p.Hostile && c.Hostile && (p.Colonist || c.Colonist))
                    outT.Add(T(KColonistHostile, matters ? SDamage : SThreat, tick, c, "colonist turned hostile (" + (c.Mental ?? "faction") + ")"));
                else if (!p.Hostile && c.Hostile)
                    outT.Add(T(KHostileArrival, SThreat, tick, c, "turned hostile: " + c.Def + " (" + (c.Mental ?? "faction") + ")"));
                if (!p.Downed && c.Downed)
                    outT.Add(T(KDowned, matters ? SDamage : (c.Hostile ? SInfo : SThreat), tick, c, "downed (health " + F(c.Health, 2) + ")"
                                   + (c.Ailments != null ? "; hediffs " + c.Ailments : "")));
                if (!float.IsNaN(p.Health) && !float.IsNaN(c.Health) && p.Health - c.Health >= HurtDrop)
                {
                    // RIMMANDRAKE_SHIELD_PYRE_WALK_FROM_FULL_LIST_EVENTS: only a new wound is harm (WoundRose); the detail names the
                    // youngest WOUND when there is one, so "newest hediff" no longer points at an unrelated hediff of age 0.
                    bool wound = WoundRose(p, c);
                    string newest = wound && c.NewestWound != null ? c.NewestWound : c.Newest;
                    outT.Add(T(KHurt, wound && matters ? SDamage : SInfo, tick, c, "health " + F(p.Health, 2) + " -> " + F(c.Health, 2)
                                   + (wound ? "" : " with no new wound or missing part (a hediff that is not an injury)")
                                   + (newest != null ? "; newest hediff " + newest : "")));
                }
                if (c.Food == "Starving" && p.Food != "Starving")
                    outT.Add(T(KStarving, matters ? SDamage : (c.Colonist ? SThreat : SInfo), tick, c, "food category Starving"));
                if (c.Mental != null && c.Mental != p.Mental)
                    outT.Add(T(KMental, matters ? SDamage : (c.Hostile || c.Colonist ? SThreat : SInfo), tick, c, "mental state " + c.Mental));
            }
            if (prev != null)
                foreach (var kv in prev)
                    if (!seen.Contains(kv.Key))
                        outT.Add(T(KDeparted, kv.Value.Critical ? SDamage : SInfo, tick, kv.Value,
                                   "left the spawned set (not a death unless a tombstone says so)"));
            return outT;
        }

        // ------------------------------------------------------------------ rollup (bounded categories)
        internal sealed class Rollup
        {
            internal readonly SortedDictionary<string, int[]> Groups = new SortedDictionary<string, int[]>(StringComparer.Ordinal);
            // per group: alive, downed, bleeding, mental
            internal int Pawns, ColonistsAlive, ColonistsDowned, ColonistsHostile, Hostiles, Critical, CriticalAvailable;
            internal float MinColonistHealth = float.NaN, MinColonistMoodMargin = float.NaN;

            internal static Rollup Of(List<PawnObs> ps)
            {
                var r = new Rollup();
                foreach (var p in ps)
                {
                    r.Pawns++;
                    string k = (p.Cls ?? "other") + "|" + (p.Rel ?? "neutral");
                    if (!r.Groups.TryGetValue(k, out var g)) r.Groups[k] = g = new int[4];
                    g[0]++;
                    if (p.Downed) g[1]++;
                    if (p.Bleed > 0) g[2]++;
                    if (p.Mental != null) g[3]++;
                    if (p.Hostile) r.Hostiles++;
                    if (p.Colonist)
                    {
                        r.ColonistsAlive++;
                        if (p.Downed) r.ColonistsDowned++;
                        if (p.Hostile) r.ColonistsHostile++;
                        if (!float.IsNaN(p.Health) && (float.IsNaN(r.MinColonistHealth) || p.Health < r.MinColonistHealth)) r.MinColonistHealth = p.Health;
                        if (!float.IsNaN(p.Mood) && !float.IsNaN(p.MoodBreak))
                        {
                            float m = p.Mood - p.MoodBreak;
                            if (float.IsNaN(r.MinColonistMoodMargin) || m < r.MinColonistMoodMargin) r.MinColonistMoodMargin = m;
                        }
                    }
                    if (p.Critical) { r.Critical++; if (!p.Downed && !p.Hostile && p.Mental == null) r.CriticalAvailable++; }
                }
                return r;
            }

            internal string Key()
            {
                var sb = new StringBuilder();
                foreach (var kv in Groups) sb.Append(kv.Key).Append(':').Append(string.Join(",", kv.Value)).Append(';');
                return sb.Append(ColonistsHostile).Append('/').Append(CriticalAvailable).ToString();
            }

            internal string Fields()
            {
                var sb = new StringBuilder(300);
                sb.Append("\"pawns\":").Append(Pawns).Append(",\"colonistsAlive\":").Append(ColonistsAlive)
                  .Append(",\"colonistsDowned\":").Append(ColonistsDowned).Append(",\"colonistsHostile\":").Append(ColonistsHostile)
                  .Append(",\"hostiles\":").Append(Hostiles).Append(",\"critical\":").Append(Critical)
                  .Append(",\"criticalAvailable\":").Append(CriticalAvailable)
                  .Append(",\"minColonistHealth\":").Append(F(MinColonistHealth, 3))
                  .Append(",\"minColonistMoodMargin\":").Append(F(MinColonistMoodMargin, 3)).Append(",\"groups\":{");
                bool first = true;
                foreach (var kv in Groups)
                {
                    if (!first) sb.Append(',');
                    first = false;
                    sb.Append(J(kv.Key)).Append(":{\"alive\":").Append(kv.Value[0]).Append(",\"downed\":").Append(kv.Value[1])
                      .Append(",\"bleeding\":").Append(kv.Value[2]).Append(",\"mental\":").Append(kv.Value[3]).Append('}');
                }
                return sb.Append('}').ToString();
            }
        }

        // ------------------------------------------------------------------ clock ledger
        internal sealed class ClockLedger
        {
            internal long Processed, Discontinuities, Declared;
            internal int LastAfter = int.MinValue;
            internal int PendingDeclaredTo = int.MinValue;      // a declared reassignment target, consumed by the next discontinuity
            internal string PendingDeclaredWhy;

            internal void Reset() { LastAfter = int.MinValue; PendingDeclaredTo = int.MinValue; PendingDeclaredWhy = null; }

            internal void Declare(int target, string why) { PendingDeclaredTo = target; PendingDeclaredWhy = why; }

            /// <summary>Before a DoSingleTick: TicksGame differs from where the last tick left it -> reassignment between ticks.</summary>
            internal Trigger BeforeTick(int now, double mono) => Check(now, mono, "between ticks");

            /// <summary>After a DoSingleTick: a step other than +1 (fastEcology steps 2000) is recorded.</summary>
            internal Trigger AfterTick(int before, int after, double mono)
            {
                Processed++;
                Trigger t = null;
                int d = after - before;
                if (d != 1)
                {
                    Discontinuities++;
                    t = new Trigger { Kind = KClock, Severity = SClock, Tick = after, Mono = mono,
                                      Detail = "one processed tick moved TicksGame by " + d + (d == 2000 ? " (fastEcology)" : "") };
                }
                LastAfter = after;
                return t;
            }

            /// <summary>Every wall pass (W250, paused too): TicksGame moved with no processed tick.</summary>
            internal Trigger Frame(int now, double mono) => Check(now, mono, "between frames");

            private Trigger Check(int now, double mono, string where)
            {
                if (LastAfter == int.MinValue) { LastAfter = now; return null; }
                if (now == LastAfter) return null;
                int from = LastAfter;
                LastAfter = now;
                Discontinuities++;
                bool declared = PendingDeclaredTo == now;
                if (declared) { Declared++; }
                var t = new Trigger { Kind = KClock, Severity = SClock, Tick = now, Mono = mono, Declared = declared,
                                      Detail = "TicksGame " + from + " -> " + now + " (" + (now - from) + ") " + where + " with no processed tick" +
                                               (declared ? "; DECLARED: " + PendingDeclaredWhy : "; UNDECLARED") };
                if (declared) { PendingDeclaredTo = int.MinValue; PendingDeclaredWhy = null; }
                return t;
            }
        }

        // ------------------------------------------------------------------ advance policy + stop rule
        /// <summary>null = allowed. A populated map (a spawned free colonist) refuses more than `budget` ticks unless the row
        /// declared a safe colony through `timeException` (debug_process.md "A long clock advance"); nothing ever exceeds HardAdvanceCap.</summary>
        internal static string AdvanceRefusal(long requested, long budget, bool populated, bool timeException)
        {
            if (requested <= 0) return "ticks must be > 0";
            if (requested > HardAdvanceCap)
                return "refused: " + requested + " ticks exceeds the hard cap " + HardAdvanceCap + " (" + (HardAdvanceCap / 60000) + " days) even with a time exception";
            if (budget <= 0) budget = DefaultAdvanceBudget;
            if (populated && !timeException && requested > budget)
                return "refused before any tick: " + requested + " ticks (" + (requested / 60000.0).ToString("0.##", CultureInfo.InvariantCulture) +
                       " days) on a POPULATED map exceeds the budget " + budget + "; a long clock advance needs a safe colony: " +
                       "no colonist on any map, or timeException=true in a row that protects its colonists from starving and dying and " +
                       "is not about health, needs, damage or death (owner 2026-11-23: allowed when the colony is safe).";
            return null;
        }

        internal const int MaxFrameSamples = 20000;       // per-run (ticks, ms) frame samples kept for the histogram / p99

        /// <summary>The next chunk the stepper runs inside this frame (TICKBURST_PROVE_MANY_TICKS_ONE_FRAME): the smallest of
        /// `chunk`, the ticks still `remaining` and, when `perFrameTickCap` &gt; 0, what the cap leaves after `doneThisFrame`
        /// ticks already stepped this frame. 0 = this frame steps no more. perFrameTickCap 0 means unlimited (only the wall
        /// budget, read between chunks, ends the frame). With a cap, a frame never steps more than the cap: a chunk is cut
        /// short rather than overshooting it.</summary>
        internal static int NextChunk(int chunk, long remaining, int perFrameTickCap, int doneThisFrame)
        {
            if (chunk < 1 || remaining <= 0) return 0;
            long n = Math.Min(chunk, remaining);
            if (perFrameTickCap > 0) n = Math.Min(n, (long)perFrameTickCap - doneThisFrame);
            return n > 0 ? (int)n : 0;
        }

        /// <summary>Nearest-rank percentile (0 &lt; p &lt;= 100) of `xs`; NaN on an empty list. Does not reorder `xs`.</summary>
        internal static double Percentile(IList<double> xs, double p)
        {
            if (xs == null || xs.Count == 0) return double.NaN;
            var s = new List<double>(xs); s.Sort();
            int rank = (int)Math.Ceiling(p / 100.0 * s.Count);
            return s[Math.Max(0, Math.Min(s.Count - 1, rank - 1))];
        }

        /// <summary>Exact histogram of ticks stepped per frame: "ticks" -&gt; frames, keys sorted numerically.</summary>
        internal static SortedDictionary<int, int> FrameTickHistogram(IList<int> frameTicks)
        {
            var h = new SortedDictionary<int, int>();
            if (frameTicks == null) return h;
            foreach (int t in frameTicks) h[t] = h.TryGetValue(t, out int c) ? c + 1 : 1;
            return h;
        }

        /// <summary>The stepper's per-frame end conditions, checked BEFORE the game-readiness gate: "cancelled", "aborted: ..."
        /// or null to go on. A run must end on a cancel, a wall timeout or a lost monitor even while no game is ready - a run
        /// left "running" refuses every later safe_advance (night review 2026-10-13).</summary>
        internal static string AdvanceFrameStop(bool cancelRequested, double wallS, double maxWallS, bool armed)
        {
            if (cancelRequested) return "cancelled";
            if (wallS > maxWallS) return "aborted: exceeded " + maxWallS.ToString("0.#", CultureInfo.InvariantCulture) + " s wall";
            if (!armed) return "aborted: monitor disarmed mid-advance (coverage lost)";
            return null;
        }

        /// <summary>TTL of the monitor that jawa/safe_advance arms for itself when nothing armed it. It guards against a
        /// monitor left armed (hooks and wall passes running) after the last advance; it is counted from the last advance's
        /// start or end, never from the first arm (RIMMANDRAKE_RENEW_SAFE_ADVANCE_AUTO_ARM_HOURLY: counted from the first
        /// arm, it disarmed the monitor mid-advance 60 wall minutes into a chain, Pyrelands visit 2, 2026-11-21).</summary>
        internal const double AutoArmTtlMin = 60;

        internal static double AutoArmUntil(double now) => now + AutoArmTtlMin * 60.0;

        /// <summary>What jawa/safe_advance does to the monitor at an advance start: "arm" (not armed: arm it for itself),
        /// "renew" (armed by an earlier safe_advance: restart its TTL) or "keep" (armed explicitly by a governor row: that
        /// row's TTL binds).</summary>
        internal static string AdvanceArmAction(bool armed, bool autoArmed) => !armed ? "arm" : autoArmed ? "renew" : "keep";

        /// <summary>Whether an advance's end restarts the monitor's TTL: only a monitor safe_advance armed for itself, so its
        /// TTL counts from the last advance's end.</summary>
        internal static bool AdvanceEndRenews(bool armed, bool autoArmed) => armed && autoArmed;

        /// <summary>Whether the monitor's TTL disarms it now. A safe_advance-armed monitor never lapses while an advance
        /// runs: the run's own wall bound ends that advance. An explicit arm's TTL always binds.</summary>
        internal static bool TtlExpired(double now, double until, bool autoArmed, bool advanceRunning)
            => now >= until && !(autoArmed && advanceRunning);

        /// <summary>The stepper's game-identity gate, checked every frame BEFORE anything reads Find.TickManager or steps a tick:
        /// "game_changed: ..." when there is no game, the program is not Playing, or Current.Game is not the Game the run
        /// started in (main menu, a load, a new game); "map_gone: ..." when the run's start map is no longer in Find.Maps;
        /// null to go on. Before this a return to the menu ended the run only through a caught NullReferenceException
        /// (abortWhy "stepper exception", SAFE_ADVANCE_MENU_DIAGNOSE_LUCKY_NULLREF).</summary>
        internal static string AdvanceGameGate(bool gameNull, bool playing, bool sameGame, bool mapPresent, int mapId)
        {
            if (gameNull) return "game_changed: no game loaded (returned to the main menu)";
            if (!sameGame) return "game_changed: Current.Game is a different game than at start (a load or a new game)";
            if (!playing) return "game_changed: ProgramState is no longer Playing";
            if (!mapPresent) return "map_gone: start map #" + mapId.ToString(CultureInfo.InvariantCulture) + " is no longer in Find.Maps";
            return null;
        }

        /// <summary>The first trigger that stops a governed advance: its kind is in stopKinds and it is not info and not a
        /// declared clock change.</summary>
        internal static Trigger FirstStop(List<Trigger> since, ICollection<string> stopKinds)
        {
            foreach (var t in since)
                if (stopKinds.Contains(t.Kind) && t.Severity != SInfo && !t.Declared) return t;
            return null;
        }

        internal static HashSet<string> ParseKinds(string csv, out string bad)
        {
            bad = null;
            var s = new HashSet<string>(StringComparer.Ordinal);
            if (string.IsNullOrWhiteSpace(csv) || csv.Trim() == "default") { foreach (var k in DefaultStopKinds) s.Add(k); return s; }
            foreach (var raw in csv.Split(','))
            {
                string k = raw.Trim();
                if (k.Length == 0) continue;
                if (Array.IndexOf(DefaultStopKinds, k) < 0) { bad = k; return s; }
                s.Add(k);
            }
            return s;
        }

        internal static List<int> ParseIds(string csv, out string bad)
        {
            bad = null;
            var r = new List<int>();
            if (string.IsNullOrWhiteSpace(csv)) return r;
            foreach (var raw in csv.Split(','))
            {
                string s = raw.Trim();
                if (s.Length == 0) continue;
                int i = s.Length - 1;
                while (i >= 0 && char.IsDigit(s[i])) i--;          // "Human123" or "123" -> 123 (thingIDNumber)
                string digits = s.Substring(i + 1);
                if (digits.Length == 0 || !int.TryParse(digits, NumberStyles.Integer, CultureInfo.InvariantCulture, out int v)) { bad = s; return r; }
                r.Add(v);
            }
            return r;
        }

        // ------------------------------------------------------------------ modal ages
        internal sealed class ModalAges
        {
            private readonly Dictionary<int, double> _first = new Dictionary<int, double>();
            private readonly HashSet<int> _latched = new HashSet<int>();

            /// <summary>Returns ids newly seen, and the ids whose age just crossed `stuck` (each latched once).</summary>
            internal void Observe(IList<int> blockingIds, double now, double stuck, List<int> fresh, List<int> crossed)
            {
                var live = new HashSet<int>(blockingIds);
                foreach (int id in blockingIds)
                {
                    if (!_first.ContainsKey(id)) { _first[id] = now; fresh.Add(id); }
                    else if (now - _first[id] >= stuck && _latched.Add(id)) crossed.Add(id);
                }
                var gone = new List<int>();
                foreach (var k in _first.Keys) if (!live.Contains(k)) gone.Add(k);
                foreach (var k in gone) { _first.Remove(k); _latched.Remove(k); }
            }

            internal double Age(int id, double now) => _first.TryGetValue(id, out var t) ? now - t : 0;
            internal double MaxAge(double now) { double m = 0; foreach (var v in _first.Values) m = Math.Max(m, now - v); return m; }
            internal void Clear() { _first.Clear(); _latched.Clear(); }
        }

        // ------------------------------------------------------------------ json helpers
        internal static string J(string s) => JawaBenchTpsMath.Json(s);
        internal static string F(double v, int p) => JawaBenchTpsMath.F(v, p);
        internal static string B(bool b) => b ? "true" : "false";
    }
}
