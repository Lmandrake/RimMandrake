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
            internal bool Downed, Hostile, Colonist, Critical;
            internal float Health = float.NaN, Bleed, Mood = float.NaN, MoodBreak = float.NaN;

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
        internal static bool Matters(PawnObs p, bool anyCritical) => p.Critical || (!anyCritical && p.Colonist);

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
                    outT.Add(T(KDowned, matters ? SDamage : (c.Hostile ? SInfo : SThreat), tick, c, "downed (health " + F(c.Health, 2) + ")"));
                if (!float.IsNaN(p.Health) && !float.IsNaN(c.Health) && p.Health - c.Health >= HurtDrop)
                    outT.Add(T(KHurt, matters ? SDamage : SInfo, tick, c, "health " + F(p.Health, 2) + " -> " + F(c.Health, 2)
                                   + (c.Newest != null ? "; newest hediff " + c.Newest : "")));
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
        /// declared a time exception; nothing ever exceeds HardAdvanceCap.</summary>
        internal static string AdvanceRefusal(long requested, long budget, bool populated, bool timeException)
        {
            if (requested <= 0) return "ticks must be > 0";
            if (requested > HardAdvanceCap)
                return "refused: " + requested + " ticks exceeds the hard cap " + HardAdvanceCap + " (" + (HardAdvanceCap / 60000) + " days) even with a time exception";
            if (budget <= 0) budget = DefaultAdvanceBudget;
            if (populated && !timeException && requested > budget)
                return "refused before any tick: " + requested + " ticks (" + (requested / 60000.0).ToString("0.##", CultureInfo.InvariantCulture) +
                       " days) on a POPULATED map exceeds the budget " + budget + "; long runs need the row to declare timeException=true " +
                       "(owner 2026-10-13: long runs only when clearly worth it). Prefer a prepared fixture over advancing a live colony.";
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
