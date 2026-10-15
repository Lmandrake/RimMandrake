// JawaBenchHealthCore.cs - the game-health metrics, the PURE half (no Verse, no Unity, no Harmony).
//
// Spec + ledger: design/RimMandrake/game_health_record.md (metric ids tps.frame-hist, tps.log-counts,
// tps.bridge-occupancy, tps.capability-inventory, opt.profiler [opt.own-counters merged into it as preset "own"],
// spike.gc-timing). Item HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP. The Verse half is JawaBenchHealth.cs (hooks) and
// JawaBenchHealthTools.cs (jawa/health, jawa/health_profile).
//
// ⛔ NO Verse/Unity/Harmony here: this file is compiled into the offline harness bridgetools/HealthSelfTest (net8.0)
// too (src/RimMandrake/Utils/selftest_health_core.py). A `using Verse;` landing here breaks that build.
//
// The rules this file enforces (game_health_record.md "Rules that bind every source"; each one is a unit):
//   1. Unavailable is never zero: every value is a Reading with a status word (ok | unavailable | failed | off); a
//      non-ok Reading has NO value field, and Render() prints the word and the reason.
//   2. No automatic mod blame: nothing here names a cause; the profiler reports cost per NAMED method only.
//   3. Process-scoped counters (log tallies, cap resets) are never reset at a game change.
//   4. Merge histograms, never average p99s: FrameHist carries its bucket version and refuses a mismatched merge;
//      quantiles are bucket RANGES recomputed from merged counts, never interpolated values.
//   6. A coincidence is labelled as one: GapGc reports gcCountChangedDuringGap beside the per-frame base rate.
//   7. The Verse.Log cap is 10,000 (decompiled 1.6 Verse/Log.cs StopLoggingAtMessageCount); past it, or while the
//      Unity logger is disabled or Log.LockMessages is held, the wording is "emission suppressed; error activity unknown".

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using System.Threading;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchHealthCore
    {
        // ------------------------------------------------------------------ metric ids (game_health_record.md)
        internal const string MFrameHist = "tps.frame-hist";
        internal const string MLogCounts = "tps.log-counts";
        internal const string MBridgeOcc = "tps.bridge-occupancy";
        internal const string MCapInv = "tps.capability-inventory";
        internal const string MProfiler = "opt.profiler";
        internal const string MGc = "spike.gc-timing";
        internal static readonly string[] MetricIds = { MFrameHist, MLogCounts, MBridgeOcc, MCapInv, MProfiler, MGc };
        /// <summary>Ids that exist in the ledger but are not separate switches here, with where they went.</summary>
        internal static readonly Dictionary<string, string> MergedIds = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            ["opt.own-counters"] = "merged into opt.profiler (preset \"own\": the same expiring allowlist timer, aimed at our own hot paths)",
        };

        // ------------------------------------------------------------------ status words (rule 1)
        internal const string WOk = "ok", WUnavailable = "unavailable", WFailed = "failed", WOff = "off";

        internal sealed class Reading
        {
            internal string Word;
            internal double Value = double.NaN;     // meaningful ONLY when Word == ok
            internal string Unit;
            internal string Reason;
            internal static Reading Ok(double v, string unit) => new Reading { Word = WOk, Value = v, Unit = unit };
            internal static Reading Unavailable(string why) => new Reading { Word = WUnavailable, Reason = why ?? "no reason given" };
            internal static Reading Failed(string err) => new Reading { Word = WFailed, Reason = err ?? "unknown error" };
            internal static Reading SwitchedOff() => new Reading { Word = WOff, Reason = "switched off" };
            internal bool IsOk => Word == WOk;

            /// <summary>ok: "12.5 ms". Anything else: "unavailable: why" - never a number.</summary>
            internal string Render() => IsOk ? F(Value) + (string.IsNullOrEmpty(Unit) ? "" : " " + Unit) : Word + ": " + Reason;

            /// <summary>{"status":"ok","value":12.5,"unit":"ms"} or {"status":"unavailable","reason":"..."}: no value key
            /// at all unless ok, so no reader can pick up a zero.</summary>
            internal string Json()
            {
                if (IsOk) return "{\"status\":\"ok\",\"value\":" + F(Value) + ",\"unit\":" + J(Unit) + "}";
                return "{\"status\":" + J(Word) + ",\"reason\":" + J(Reason) + "}";
            }
        }

        // ------------------------------------------------------------------ switches (one per metric id)
        internal sealed class Switches
        {
            private readonly Dictionary<string, bool> _on = new Dictionary<string, bool>(StringComparer.Ordinal);
            internal string Note = "defaults";
            internal Switches() { foreach (var id in MetricIds) _on[id] = true; }
            internal bool On(string id) { lock (_on) return _on.TryGetValue(id, out var v) && v; }
            internal bool Set(string id, bool v) { lock (_on) { if (!_on.ContainsKey(id)) return false; _on[id] = v; return true; } }
            internal Dictionary<string, bool> Snapshot() { lock (_on) return new Dictionary<string, bool>(_on); }

            /// <summary>One flat JSON object {"tps.frame-hist": bool, ...}. Unknown ids, merged ids and non-bools are
            /// NOTED; the defaults (all on) stand for what the file could not say.</summary>
            internal static Switches Parse(string json)
            {
                var s = new Switches();
                if (string.IsNullOrWhiteSpace(json)) { s.Note = "no settings file: defaults"; return s; }
                Dictionary<string, object> kv;
                string err = ParseFlatBools(json, out kv);
                if (err != null) { s.Note = "invalid settings (" + err + "): defaults"; return s; }
                var notes = new List<string>();
                foreach (var p in kv)
                {
                    if (MergedIds.TryGetValue(p.Key, out var where)) { notes.Add(p.Key + ": " + where + "; ignored"); continue; }
                    if (!(p.Value is bool b)) { notes.Add(p.Key + ": not a bool"); continue; }
                    if (!s.Set(p.Key, b)) notes.Add(p.Key + ": unknown metric id");
                }
                s.Note = notes.Count == 0 ? "ok" : string.Join("; ", notes);
                return s;
            }
        }

        /// <summary>Minimal flat {"key": true|false|other} reader (the health settings file needs nothing more). Values
        /// that are not true/false come back as their raw text, so the caller can say "not a bool".</summary>
        internal static string ParseFlatBools(string t, out Dictionary<string, object> kv)
        {
            kv = new Dictionary<string, object>(StringComparer.Ordinal);
            t = t.Trim();
            if (t.Length < 2 || t[0] != '{' || t[t.Length - 1] != '}') return "not a JSON object";
            string body = t.Substring(1, t.Length - 2).Trim();
            if (body.Length == 0) return null;
            int i = 0;
            while (i < body.Length)
            {
                while (i < body.Length && (char.IsWhiteSpace(body[i]) || body[i] == ',')) i++;
                if (i >= body.Length) break;
                if (body[i] != '"') return "expected a quoted key at " + i;
                int k = body.IndexOf('"', i + 1);
                if (k < 0) return "unterminated key";
                string key = body.Substring(i + 1, k - i - 1);
                int c = body.IndexOf(':', k + 1);
                if (c < 0) return "missing ':' after " + key;
                int e = c + 1;
                while (e < body.Length && body[e] != ',') e++;
                string raw = body.Substring(c + 1, e - c - 1).Trim();
                if (raw == "true") kv[key] = true;
                else if (raw == "false") kv[key] = false;
                else kv[key] = raw;
                i = e + 1;
            }
            return null;
        }

        // ------------------------------------------------------------------ measured cost per metric (hook bodies)
        internal sealed class Meter
        {
            private long _calls, _ticks, _maxTicks;
            internal void Add(long ticks)
            {
                if (ticks < 0) return;
                Interlocked.Increment(ref _calls);
                Interlocked.Add(ref _ticks, ticks);
                long m;
                while (ticks > (m = Interlocked.Read(ref _maxTicks)) && Interlocked.CompareExchange(ref _maxTicks, ticks, m) != m) { }
            }
            internal long Calls => Interlocked.Read(ref _calls);
            /// <summary>Mean us per hook body; UNAVAILABLE (not 0) when nothing was timed.</summary>
            internal Reading MeanUs(double ticksPerSecond) => Calls == 0
                ? Reading.Unavailable("no calls timed")
                : Reading.Ok(Interlocked.Read(ref _ticks) * 1e6 / ticksPerSecond / Calls, "us");
            internal Reading MaxUs(double ticksPerSecond) => Calls == 0
                ? Reading.Unavailable("no calls timed")
                : Reading.Ok(Interlocked.Read(ref _maxTicks) * 1e6 / ticksPerSecond, "us");
            internal double TotalMs(double ticksPerSecond) => Interlocked.Read(ref _ticks) * 1e3 / ticksPerSecond;
        }

        // ------------------------------------------------------------------ tps.frame-hist (rule 4)
        internal sealed class FrameHist
        {
            internal const string Version = "fh-v1";
            /// <summary>Upper edges (ms). Bucket 0 = [0, 1); bucket i = [Edges[i-1], Edges[i]); the last bucket is
            /// [30000, inf), whose upper end is the observed maximum.</summary>
            internal static readonly double[] Edges = { 1, 2, 4, 8, 12, 16.7, 20, 25, 33.4, 40, 50, 66.7, 100, 150, 250, 500, 1000, 2000, 5000, 10000, 30000 };
            /// <summary>Slow-interval thresholds (ms): count and TOTAL TIME above each, because one 20 s stall among
            /// thousands of frames sits above p99 and only the maximum and the time-in-slow show it.</summary>
            internal static readonly double[] Slow = { 50, 100, 250, 1000, 5000 };

            internal string BucketVersion = Version;
            internal readonly long[] Counts = new long[Edges.Length + 1];
            internal readonly long[] SlowCount = new long[Slow.Length];
            internal readonly double[] SlowMs = new double[Slow.Length];
            internal long N, Rejected;
            internal double TotalMs, MaxMs;

            internal static int BucketOf(double ms)
            {
                int lo = 0, hi = Edges.Length;           // first edge > ms
                while (lo < hi) { int mid = (lo + hi) >> 1; if (ms < Edges[mid]) hi = mid; else lo = mid + 1; }
                return lo;
            }

            /// <summary>Main thread only (no locks): the Root.Update prefix is the single writer.</summary>
            internal void Add(double ms)
            {
                if (double.IsNaN(ms) || double.IsInfinity(ms) || ms < 0) { Rejected++; return; }
                Counts[BucketOf(ms)]++;
                N++;
                TotalMs += ms;
                if (ms > MaxMs) MaxMs = ms;
                for (int i = 0; i < Slow.Length; i++) if (ms >= Slow[i]) { SlowCount[i]++; SlowMs[i] += ms; }
            }

            /// <summary>Adds o's counts into this. Refuses (false + why) on a different bucket version.</summary>
            internal bool Merge(FrameHist o, out string why)
            {
                why = null;
                if (o == null) { why = "nothing to merge"; return false; }
                if (o.BucketVersion != BucketVersion) { why = "bucket version " + o.BucketVersion + " != " + BucketVersion + ": not merged"; return false; }
                for (int i = 0; i < Counts.Length; i++) Counts[i] += o.Counts[i];
                for (int i = 0; i < Slow.Length; i++) { SlowCount[i] += o.SlowCount[i]; SlowMs[i] += o.SlowMs[i]; }
                N += o.N; Rejected += o.Rejected; TotalMs += o.TotalMs;
                if (o.MaxMs > MaxMs) MaxMs = o.MaxMs;
                return true;
            }

            internal FrameHist Clone() { var c = new FrameHist { BucketVersion = BucketVersion }; c.Merge(this, out _); return c; }

            /// <summary>The bucket RANGE holding the q-quantile (nearest-rank). False when there are no frames.</summary>
            internal bool QuantileRange(double q, out double lo, out double hi)
            {
                lo = hi = double.NaN;
                if (N == 0 || double.IsNaN(q) || q < 0 || q > 1) return false;
                long rank = (long)Math.Ceiling(q * N);
                if (rank < 1) rank = 1;
                long cum = 0;
                for (int i = 0; i < Counts.Length; i++)
                {
                    cum += Counts[i];
                    if (cum >= rank)
                    {
                        lo = i == 0 ? 0 : Edges[i - 1];
                        hi = i < Edges.Length ? Math.Min(Edges[i], MaxMs) : MaxMs;
                        if (hi < lo) hi = lo;
                        return true;
                    }
                }
                return false;
            }

            internal Reading Quantile(double q, out string text)
            {
                string name = "p" + F(q * 100);
                if (!QuantileRange(q, out var lo, out var hi)) { text = name + ": unavailable (no frames)"; return Reading.Unavailable("no frames recorded"); }
                text = name + " in [" + F(lo) + ", " + F(hi) + "] ms (bucket range, " + BucketVersion + ")";
                return Reading.Ok(hi, "ms upper bound");
            }

            internal string Json()
            {
                if (N == 0) return "{\"status\":\"unavailable\",\"reason\":\"no frames recorded\",\"bucketVersion\":" + J(BucketVersion) + ",\"rejected\":" + I(Rejected) + "}";
                var sb = new StringBuilder("{\"status\":\"ok\",\"bucketVersion\":").Append(J(BucketVersion));
                sb.Append(",\"edgesMs\":[");
                for (int i = 0; i < Edges.Length; i++) sb.Append(i == 0 ? "" : ",").Append(F(Edges[i]));
                sb.Append("],\"counts\":[");
                for (int i = 0; i < Counts.Length; i++) sb.Append(i == 0 ? "" : ",").Append(I(Counts[i]));
                sb.Append("],\"n\":").Append(I(N)).Append(",\"totalMs\":").Append(F(TotalMs)).Append(",\"maxMs\":").Append(F(MaxMs))
                  .Append(",\"rejected\":").Append(I(Rejected)).Append(",\"slow\":[");
                for (int i = 0; i < Slow.Length; i++)
                    sb.Append(i == 0 ? "" : ",").Append("{\"atLeastMs\":").Append(F(Slow[i])).Append(",\"count\":").Append(I(SlowCount[i]))
                      .Append(",\"totalMs\":").Append(F(SlowMs[i])).Append('}');
                foreach (var q in new[] { 0.5, 0.99 })
                {
                    QuantileRange(q, out var lo, out var hi);
                    sb.Append(",\"p").Append(F(q * 100)).Append("RangeMs\":[").Append(F(lo)).Append(',').Append(F(hi)).Append(']');
                }
                return sb.Append('}').ToString();
            }
        }

        /// <summary>Closed per-window histograms (newest last), so any span is a MERGE of windows, never an average.</summary>
        internal sealed class HistRing
        {
            private readonly FrameHist[] _h; private readonly double[] _start, _end; private int _next, _count;
            internal long Evicted;
            internal HistRing(int capacity) { _h = new FrameHist[capacity]; _start = new double[capacity]; _end = new double[capacity]; }
            internal int Count => _count;
            internal void Close(FrameHist w, double startS, double endS)
            {
                if (_count == _h.Length) Evicted++; else _count++;
                _h[_next] = w; _start[_next] = startS; _end[_next] = endS;
                _next = (_next + 1) % _h.Length;
            }
            /// <summary>Merge every retained window that ENDED at or after sinceS. coveredFromS = the earliest start merged.</summary>
            internal FrameHist MergedSince(double sinceS, out int windows, out double coveredFromS)
            {
                var m = new FrameHist(); windows = 0; coveredFromS = double.NaN;
                for (int k = 0; k < _count; k++)
                {
                    int i = (_next - _count + k + _h.Length) % _h.Length;
                    if (_end[i] < sinceS) continue;
                    if (m.Merge(_h[i], out _)) { windows++; if (double.IsNaN(coveredFromS) || _start[i] < coveredFromS) coveredFromS = _start[i]; }
                }
                return m;
            }
        }

        // ------------------------------------------------------------------ tps.log-counts (rules 3 and 7)
        internal const int VerseLogCap = 10000;
        internal const string SuppressedText = "emission suppressed; error activity unknown";
        /// <summary>UnityEngine.LogType ordinals: Error 0, Assert 1, Warning 2, Log 3, Exception 4.</summary>
        internal static readonly string[] LogTypeNames = { "error", "assert", "warning", "log", "exception" };

        /// <summary>Counts of messages that REACHED Application.logMessageReceivedThreaded (any thread; Interlocked).
        /// Process-scoped: never reset at a game change. After suppression these are EMITTED counts only.</summary>
        internal sealed class LogTally
        {
            private readonly long[] _by = new long[5];
            private long _other;
            internal void Note(int unityLogType)
            {
                if (unityLogType >= 0 && unityLogType < 5) Interlocked.Increment(ref _by[unityLogType]);
                else Interlocked.Increment(ref _other);
            }
            internal long Of(int t) => t >= 0 && t < 5 ? Interlocked.Read(ref _by[t]) : Interlocked.Read(ref _other);
            internal long Other => Interlocked.Read(ref _other);
            internal long Total { get { long s = Other; for (int i = 0; i < 5; i++) s += Of(i); return s; } }
        }

        internal sealed class CapState
        {
            internal string Word;     // emitting | suppressed | unknown | unavailable
            internal string Text;
            internal Reading Headroom; // messages left before the Verse cap; unavailable when the count is unreadable
        }

        /// <summary>Judge suppression from the four separately read engine facts (null = could not read).</summary>
        internal static CapState JudgeCap(int? verseCount, bool? reachedLimit, int? logDisablers, bool? loggerEnabled)
        {
            var c = new CapState
            {
                Headroom = verseCount.HasValue
                    ? Reading.Ok(Math.Max(0, VerseLogCap - verseCount.Value), "messages before the Verse.Log cap")
                    : Reading.Unavailable("Verse.Log messageCount unreadable")
            };
            if (reachedLimit == true) { c.Word = "suppressed"; c.Text = "Verse.Log cap (" + VerseLogCap + ") reached: " + SuppressedText; return c; }
            if (loggerEnabled == false) { c.Word = "suppressed"; c.Text = "Debug.unityLogger.logEnabled is false: " + SuppressedText; return c; }
            if (logDisablers.HasValue && logDisablers.Value > 0)
            { c.Word = "suppressed"; c.Text = "Log.LockMessages held (" + logDisablers.Value + "): Verse " + SuppressedText; return c; }
            if (!reachedLimit.HasValue && !loggerEnabled.HasValue)
            { c.Word = "unavailable"; c.Text = "cap and logger state unreadable: suppression cannot be ruled out"; return c; }
            if (!reachedLimit.HasValue || !loggerEnabled.HasValue || !logDisablers.HasValue)
            {
                c.Word = "unknown";
                c.Text = "logger state partly unreadable (" + (!reachedLimit.HasValue ? "cap flag " : "") + (!loggerEnabled.HasValue ? "unity logger " : "") +
                         (!logDisablers.HasValue ? "lock count" : "") + "): suppression cannot be ruled out";
                return c;
            }
            c.Word = "emitting";
            c.Text = verseCount.HasValue ? "emitting; " + verseCount.Value + " of " + VerseLogCap + " counted toward the cap" : "emitting; cap count unreadable";
            return c;
        }

        /// <summary>Counts Verse cap-count resets (Log.Clear / ResetMessageCount): a count that went DOWN.</summary>
        internal sealed class ResetTracker
        {
            private int _last = -1;
            internal long Resets;
            internal void Observe(int count) { if (_last >= 0 && count < _last) Resets++; _last = count; }
        }

        /// <summary>The counts line a reader prints. When suppressed, the counts are labelled as EMITTED only and the
        /// suppression text comes first: a zero after the cap is not "no errors".</summary>
        internal static string LogLine(LogTally t, CapState cap)
        {
            var sb = new StringBuilder();
            if (cap.Word == "suppressed" || cap.Word == "unknown" || cap.Word == "unavailable") sb.Append(cap.Text).Append(". Emitted before/around it: ");
            else sb.Append("emitted: ");
            for (int i = 0; i < 5; i++) sb.Append(i == 0 ? "" : ", ").Append(LogTypeNames[i]).Append(' ').Append(I(t.Of(i)));
            return sb.ToString();
        }

        // ------------------------------------------------------------------ tps.bridge-occupancy
        /// <summary>Main-thread time inside the bridge's pumps (interval UNION, so overlap is never double-counted) and
        /// an UPPER BOUND on queue delay: a work item found in a pump was enqueued after the previous pump of the same
        /// target began, so it waited at most (this start - previous start). Main thread only.</summary>
        internal sealed class Occupancy
        {
            internal long Calls, CallsWithWork, BusyTicks, MaxCallTicks, Rejected;
            internal long DelayBoundSamples, DelayBoundSumTicks, DelayBoundMaxTicks;
            internal int MaxPending;
            private long _lastEnd = long.MinValue;
            private readonly long[] _lastStart;
            internal Occupancy(int targets) { _lastStart = new long[targets]; for (int i = 0; i < targets; i++) _lastStart[i] = -1; }

            internal void Note(int target, long start, long end, int pendingAtStart)
            {
                if (end < start || target < 0 || target >= _lastStart.Length) { Rejected++; return; }
                Calls++;
                long d = end - start;
                if (d > MaxCallTicks) MaxCallTicks = d;
                if (start >= _lastEnd) BusyTicks += d;
                else if (end > _lastEnd) BusyTicks += end - _lastEnd;
                if (end > _lastEnd) _lastEnd = end;
                if (pendingAtStart > 0)
                {
                    CallsWithWork++;
                    if (pendingAtStart > MaxPending) MaxPending = pendingAtStart;
                    if (_lastStart[target] >= 0)
                    {
                        long b = start - _lastStart[target];
                        DelayBoundSamples++; DelayBoundSumTicks += b;
                        if (b > DelayBoundMaxTicks) DelayBoundMaxTicks = b;
                    }
                }
                _lastStart[target] = start;
            }

            /// <summary>Busy share of a wall window; unavailable for an empty window.</summary>
            internal Reading Share(long windowTicks) => windowTicks <= 0
                ? Reading.Unavailable("empty window")
                : Reading.Ok((double)BusyTicks / windowTicks, "share of main-thread wall time");
        }

        // ------------------------------------------------------------------ tps.capability-inventory
        /// <summary>A Unity ProfilerRecorder counter: ok only when the handle is valid AND it collected samples. A
        /// valid handle or a zero alone does not prove collection (GPT review 1.1).</summary>
        internal static Reading ClassifyRecorder(bool started, string startError, bool valid, int sampleCount, long lastValue, string unit)
        {
            if (!started) return Reading.Failed("StartNew threw: " + (startError ?? "?"));
            if (!valid) return Reading.Unavailable("recorder handle invalid: counter not exposed in this player");
            if (sampleCount <= 0) return Reading.Unavailable("valid handle but no samples collected: collection not proven");
            return Reading.Ok(lastValue, unit);
        }

        /// <summary>Word counts across an inventory. Deliberately no overall verdict: a partial build never reads as
        /// "health capture complete".</summary>
        internal static string InventorySummary(IEnumerable<KeyValuePair<string, Reading>> rows)
        {
            int ok = 0, un = 0, fa = 0, off = 0;
            foreach (var r in rows)
            {
                switch (r.Value?.Word)
                {
                    case WOk: ok++; break;
                    case WFailed: fa++; break;
                    case WOff: off++; break;
                    default: un++; break;
                }
            }
            return "ok " + ok + ", unavailable " + un + ", failed " + fa + ", off " + off + " (per source; no overall verdict)";
        }

        // ------------------------------------------------------------------ spike.gc-timing (rule 6)
        internal sealed class GapGc
        {
            internal const double GapMs = 250;
            internal long Frames, FramesWithGcChange, Gaps, GapsWithGcChange;
            internal struct Ev { internal double AtS, GapMs; internal int GcDelta; }
            private readonly Ev[] _ring = new Ev[64]; private int _next, _count;
            internal long Evicted;

            internal void Observe(double intervalMs, int gcDelta, double atS)
            {
                if (double.IsNaN(intervalMs) || intervalMs < 0) return;
                Frames++;
                if (gcDelta > 0) FramesWithGcChange++;
                if (intervalMs < GapMs) return;
                Gaps++;
                if (gcDelta > 0) GapsWithGcChange++;
                if (_count == _ring.Length) Evicted++; else _count++;
                _ring[_next] = new Ev { AtS = atS, GapMs = intervalMs, GcDelta = gcDelta };
                _next = (_next + 1) % _ring.Length;
            }

            internal List<Ev> Events() { var l = new List<Ev>(); for (int k = 0; k < _count; k++) l.Add(_ring[(_next - _count + k + _ring.Length) % _ring.Length]); return l; }

            /// <summary>Both rates, side by side: a GC count change in a gap means little unless it is rarer in ordinary
            /// frames. Never a pause time and never a cause.</summary>
            internal string Text()
            {
                if (Frames == 0) return "unavailable: no frames observed";
                return "gaps >= " + F(GapMs) + " ms: " + Gaps + "; gcCountChangedDuringGap in " + GapsWithGcChange + " of them; base rate: GC count changed in " +
                       FramesWithGcChange + " of " + Frames + " frames. A coincidence, not a cause: no GC pause time is measured.";
            }
        }

        // ------------------------------------------------------------------ opt.profiler (+ merged opt.own-counters)
        internal const int MaxProfileTargets = 32;
        internal const double DefaultProfileMinutes = 10, MaxProfileMinutes = 60;
        /// <summary>Preset "own" (was opt.own-counters): our own mods' map-component ticks, read from our source
        /// 2026-10-14 (src/RimMandrake/FlowWorks/Source). A name that does not resolve in the running game is reported
        /// unavailable, never dropped silently.</summary>
        internal const string OwnPreset =
            "RimMandrake.FlowWorks.RM_MapComponent_Excavation:MapComponentTick;" +
            "RimMandrake.FlowWorks.RM_LiquidSurface:MapComponentTick;" +
            "RimMandrake.FlowWorks.Rivers.RM_MapComponent_RiverCurrent:MapComponentTick;" +
            "RimMandrake.FlowWorks.Hose.RM_MapComponent_Hoses:MapComponentTick";

        internal sealed class Target { internal string Type, Method; internal string Key => Type + ":" + Method; }

        /// <summary>Exact "Namespace.Type:Method" names only, separated by ';', ',' or newlines ('#' starts a comment).
        /// No wildcards, no duplicates, at most max. Any error refuses the WHOLE list (returns empty).</summary>
        internal static List<Target> ParseAllowlist(string spec, int max, List<string> errors)
        {
            var outL = new List<Target>();
            var seen = new HashSet<string>(StringComparer.Ordinal);
            int before = errors.Count;
            if (string.IsNullOrWhiteSpace(spec)) { errors.Add("empty allowlist"); return outL; }
            foreach (var raw0 in spec.Split(new[] { ';', ',', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries))
            {
                string raw = raw0;
                int h = raw.IndexOf('#'); if (h >= 0) raw = raw.Substring(0, h);
                raw = raw.Trim();
                if (raw.Length == 0) continue;
                if (raw.IndexOf('*') >= 0 || raw.IndexOf('?') >= 0) { errors.Add(raw + ": wildcards are refused (exact names only)"); continue; }
                int c = raw.IndexOf(':');
                if (c <= 0 || c != raw.LastIndexOf(':') || c == raw.Length - 1) { errors.Add(raw + ": expected Namespace.Type:Method"); continue; }
                var t = new Target { Type = raw.Substring(0, c).Trim(), Method = raw.Substring(c + 1).Trim() };
                if (t.Type.IndexOf('.') < 0) { errors.Add(raw + ": type must be namespace-qualified"); continue; }
                if (!seen.Add(t.Key)) { errors.Add(raw + ": duplicate"); continue; }
                outL.Add(t);
            }
            if (outL.Count > max) errors.Add("allowlist has " + outL.Count + " entries; the maximum is " + max);
            if (outL.Count == 0 && errors.Count == before) errors.Add("empty allowlist");
            return errors.Count > before ? new List<Target>() : outL;
        }

        /// <summary>null when exactly one method matched; else why the target is refused (never a silent pick).</summary>
        internal static string ResolveVerdict(string key, bool typeFound, int candidates)
        {
            if (!typeFound) return key + ": type not found in the running game";
            if (candidates == 0) return key + ": no declared method of that name";
            if (candidates > 1) return key + ": ambiguous (" + candidates + " overloads); refused rather than pick one";
            return null;
        }

        /// <summary>The profiler's dead-man switch. Times are monotonic seconds.</summary>
        internal sealed class Expiry
        {
            private double _until = double.NegativeInfinity;
            internal double Set(double nowS, double minutes, double defMinutes, double maxMinutes)
            {
                double m = double.IsNaN(minutes) || minutes <= 0 ? defMinutes : Math.Min(minutes, maxMinutes);
                _until = nowS + m * 60.0;
                return m;
            }
            internal void Clear() { _until = double.NegativeInfinity; }
            internal bool Live(double nowS) => nowS < _until;
            internal double UntilS => _until;
        }

        /// <summary>Recursion guard per profiled method, per thread: only the OUTERMOST invocation is timed, so a
        /// recursive method is not double-counted. Thread-static, so a foreign thread has its own depth.</summary>
        internal static class Depth
        {
            [ThreadStatic] private static int[] _d;
            internal static bool Enter(int idx)
            {
                var d = _d ?? (_d = new int[MaxProfileTargets]);
                if (idx < 0 || idx >= d.Length) return false;
                return ++d[idx] == 1;
            }
            internal static void Exit(int idx)
            {
                var d = _d;
                if (d == null || idx < 0 || idx >= d.Length || d[idx] == 0) return;
                d[idx]--;
            }
            internal static void ResetThreadForTest() { _d = null; }
        }

        // ------------------------------------------------------------------ json helpers
        internal static string J(string s) => JawaBenchTpsMath.Json(s);
        internal static string I(long v) => v.ToString(CultureInfo.InvariantCulture);
        internal static string F(double v) => double.IsNaN(v) || double.IsInfinity(v) ? "null" : Math.Round(v, 3).ToString("0.###", CultureInfo.InvariantCulture);
    }
}
