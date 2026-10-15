// JawaBenchTpsTierCore.cs - the pure accounting of the TPS record's TEST TIER (telemetry design P2,
// Transient/weekly_cleaning_2026-10-11/08_telemetry_deep_design.md sections 2-3).
//
// ⛔ NO Verse, NO UnityEngine, NO HarmonyLib: compiled into the companion AND into the offline harness
// (bridgetools/TpsMathSelfTest, UnitsTier.cs). The Harmony side (JawaBenchTpsTier.cs) only reads clocks and calls in here.
//
// WHAT LIVES HERE
//   Hist        T0: 28 fixed log-spaced tick-duration buckets (histV 1). Bucket 0 = under 0.25 ms; bucket i (1..26) =
//               [0.25 x R^(i-1), 0.25 x R^i) ms with R = 16000^(1/26) (so bucket 26 ends at exactly 4000 ms);
//               bucket 27 = 4 s and over. Edges are precomputed in Stopwatch ticks; bucketing is a 5-step binary search.
//   TickTier    T0 per tick, main thread, called from JawaBenchTpsStages.TickEnd: one histogram increment and one row of
//               the preallocated struct-of-arrays FLIGHT RING (8,192 ticks: tg, durUs, 10 exclusive stage deltas in us,
//               gen-0 GC delta, log error+warning delta). No allocation, no lock, no string on that path.
//   FlightSnap  a pooled copy of the ring, oldest tick first, handed to the writer thread for the gzip side file.
//   FlightGate  the dump rate limit (one per 30 s), counting what it suppressed.
//   ExcCounter  the log counter: signature normalisation, per-window top signatures (cap 64 + overflow), first sight
//               per session. Called from the Log prefixes on ANY thread, so it locks (never on the tick path).
//   FlightFile  the side-file format and the 1 GB oldest-first directory cap.
//
// FLIGHT FILE FORMAT (flightV 1) - <JawaBench>\tps\flight\flight_<session>_<seq 4 digits>.jsonl.gz, gzip of UTF-8 lines:
//   line 1  header object: {"flightV":1,"session","seq","trigger","utc","tickFrom","tickTo","ticks","worstDurUs",
//           "worstTg","freqHz","fields":[...],"stageFields":"exclusive stage time in microseconds; tickOther = tick
//           minus its timed children; mapPost excludes mapComp"}
//   line 2+ one JSON ARRAY per tick, oldest first, in `fields` order:
//           [tg, durUs, tickOther, tl:Normal, tl:Rare, tl:Long, world, worldPost, mapPre, mapPost, mapComp, gameComp,
//            gc0, logEW]
//           gc0 = gen-0 collections that completed during that tick (0..255), logEW = Log.Error/ErrorOnce/Warning/
//           WarningOnce calls during it (0..32767, clamped).

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;
using System.Threading;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;
using S = JawaBench.BridgeTools.JawaBenchTpsStages;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchTpsTierCore
    {
        // ------------------------------------------------------------------ constants (the design's numbers)
        public const int RingTicks = 8192;
        public const double SpikeTickSeconds = 0.250;        // a single tick over this triggers a flight dump
        public const int ExcBurst = 50;                       // more than this many errors+warnings in one window trigger one
        public const double DumpMinIntervalSeconds = 30.0;
        public const long FlightDirCapBytes = 1024L * 1024L * 1024L;
        public const long ExcFileCapBytes = 64L * 1024L * 1024L;
        public const int ExcSigLen = 160, ExcWindowSigs = 64, ExcTop = 5, ExcFirstSightBytes = 4096, ExcSessionSigs = 4096;
        public const double TestCadenceSeconds = 1.0;
        public const double DefaultTtlMinutes = 60, MaxTtlMinutes = 240;
        public const string TierTest = "test", TierCampaign = "campaign";
        public const string TrigIncident = "incident", TrigTick = "tick", TrigExc = "exc-burst", TrigMark = "mark", TrigDisarm = "disarm";

        public static double ClampTtl(double minutes) =>
            double.IsNaN(minutes) || double.IsInfinity(minutes) || minutes <= 0 ? DefaultTtlMinutes : Math.Min(minutes, MaxTtlMinutes);

        // ------------------------------------------------------------------ histogram
        public static class Hist
        {
            public const int Version = 1, Buckets = 28;
            public const double MinMs = 0.25, MaxMs = 4000.0;
            public static readonly double Ratio = Math.Pow(MaxMs / MinMs, 1.0 / 26.0);

            /// <summary>Lower edge (ms) of bucket i (1..27); bucket 0 starts at 0.</summary>
            public static double LowerEdgeMs(int i) => i <= 0 ? 0.0 : (i == 27 ? MaxMs : MinMs * Math.Pow(Ratio, i - 1));

            /// <summary>The 27 bucket boundaries in Stopwatch ticks: edge k = lower edge of bucket k+1.</summary>
            public static long[] EdgesTicks(double freq)
            {
                var e = new long[Buckets - 1];
                for (int k = 0; k < e.Length; k++) e[k] = (long)Math.Ceiling(LowerEdgeMs(k + 1) * freq / 1000.0);
                return e;
            }

            /// <summary>The bucket of a duration: how many edges it reaches. Allocation-free.</summary>
            public static int Bucket(long d, long[] edges)
            {
                int lo = 0, hi = edges.Length;           // answer in [0, edges.Length]
                while (lo < hi)
                {
                    int mid = (lo + hi) >> 1;
                    if (d >= edges[mid]) lo = mid + 1; else hi = mid;
                }
                return lo;
            }

            /// <summary>The edges as a JSON array of ms (for the arm marker, so a reader never recomputes them).</summary>
            public static string EdgesJson()
            {
                var sb = new StringBuilder(300).Append('[');
                for (int i = 1; i < Buckets; i++) { if (i > 1) sb.Append(','); sb.Append(M.F(LowerEdgeMs(i), 4)); }
                return sb.Append(']').ToString();
            }

            /// <summary>Sparse `"hist":[[bucket,count],...],"histV":1` (no braces), then zero the counts.</summary>
            public static string TakeFields(int[] counts)
            {
                var sb = new StringBuilder(120).Append("\"hist\":[");
                bool first = true;
                for (int i = 0; i < counts.Length; i++)
                {
                    if (counts[i] == 0) continue;
                    if (!first) sb.Append(',');
                    first = false;
                    sb.Append('[').Append(i).Append(',').Append(counts[i]).Append(']');
                }
                Array.Clear(counts, 0, counts.Length);
                return sb.Append("],\"histV\":").Append(Version).ToString();
            }
        }

        // ------------------------------------------------------------------ the per-tick recorder (main thread)
        public sealed class TickTier
        {
            public volatile bool On;              // test tier armed (and T0 not switched off): Record is called
            public bool HistOn = true, FlightOn = true;
            public readonly int Capacity;
            private readonly double _freq;
            private readonly long[] _edges;
            private readonly long _spikeTicks;
            public readonly int[] HistCounts = new int[Hist.Buckets];

            // ring (struct of arrays), allocated on first Enable
            private int[] _tg, _dur, _stage;
            private byte[] _gc;
            private short[] _ew;
            private int _head, _count;
            private readonly long[] _scratch = new long[S.N];
            private int _gcPrev = -1;
            private long _ewPrev = -1;
            /// <summary>The log counter whose running error+warning total feeds logEW (null = 0).</summary>
            public ExcCounter Exc;
            public long Recorded;

            // trigger raised on the tick path, consumed once per frame (a string CONSTANT: no allocation)
            public volatile string PendingTrigger;
            public int PendingTg;

            public TickTier(double freq, int capacity = RingTicks)
            {
                _freq = freq;
                Capacity = capacity;
                _edges = Hist.EdgesTicks(freq);
                _spikeTicks = (long)(SpikeTickSeconds * freq);
            }

            public int Count => _count;
            public bool Allocated => _tg != null;

            /// <summary>Allocate the ring once (~420 KB at 8,192 ticks). Main thread, at arm.</summary>
            public void Allocate()
            {
                if (_tg != null) return;
                _tg = new int[Capacity]; _dur = new int[Capacity]; _stage = new int[Capacity * S.N];
                _gc = new byte[Capacity]; _ew = new short[Capacity];
            }

            /// <summary>Forget the ring's content (not its memory) and the window histogram. At arm.</summary>
            public void Clear()
            {
                _head = 0; _count = 0; _gcPrev = -1; _ewPrev = -1;
                Array.Clear(HistCounts, 0, HistCounts.Length);
                PendingTrigger = null;
            }

            private int Us(long ticks)
            {
                double us = ticks * 1e6 / _freq;
                return us >= int.MaxValue ? int.MaxValue : (us <= 0 ? 0 : (int)us);
            }

            /// <summary>
            /// One finished tick. <paramref name="d"/> = whole-tick Stopwatch ticks; <paramref name="total"/> and
            /// <paramref name="tickBase"/> are the stage accumulators after the tick and at its start (inclusive), so
            /// their difference is this tick's inclusive stage time. <paramref name="gc0"/> = GC.CollectionCount(0) now,
            /// <paramref name="logEW"/> = the running error+warning count now. No allocation.
            /// </summary>
            public void Record(long d, int tg, long[] total, long[] tickBase, int gc0, long logEW)
            {
                if (HistOn) HistCounts[Hist.Bucket(d, _edges)]++;
                if (d >= _spikeTicks && PendingTrigger == null) { PendingTg = tg; PendingTrigger = TrigTick; }
                Recorded++;
                if (!FlightOn || _tg == null) return;
                var x = _scratch;
                for (int i = 0; i < S.N; i++) x[i] = total[i] - tickBase[i];
                x[S.CTick] = d;
                long other = d - x[S.CNormal] - x[S.CRare] - x[S.CLong] - x[S.CWorld] - x[S.CWorldPost] - x[S.CMapPre] - x[S.CMapPost] - x[S.CGameComp];
                long mapPost = x[S.CMapPost] - x[S.CMapComp];
                x[S.CTick] = other < 0 ? 0 : other;
                x[S.CMapPost] = mapPost < 0 ? 0 : mapPost;
                int h = _head;
                _tg[h] = tg;
                _dur[h] = Us(d);
                int b = h * S.N;
                for (int i = 0; i < S.N; i++) _stage[b + i] = Us(x[i]);
                int dg = _gcPrev < 0 ? 0 : gc0 - _gcPrev;
                _gc[h] = (byte)(dg < 0 ? 0 : (dg > 255 ? 255 : dg));
                long de = _ewPrev < 0 ? 0 : logEW - _ewPrev;
                _ew[h] = (short)(de < 0 ? 0 : (de > short.MaxValue ? short.MaxValue : de));
                _gcPrev = gc0;
                _ewPrev = logEW;
                _head = h + 1 == Capacity ? 0 : h + 1;
                if (_count < Capacity) _count++;
            }

            /// <summary>Copy the ring into <paramref name="s"/>, OLDEST tick first (two Array.Copy segments per column).</summary>
            public void CopyTo(FlightSnap s)
            {
                int n = _count;
                s.Count = n;
                if (n == 0 || _tg == null) { s.Count = 0; return; }
                int start = (_head - n + Capacity) % Capacity;
                int first = Math.Min(n, Capacity - start), second = n - first;
                Array.Copy(_tg, start, s.Tg, 0, first); Array.Copy(_dur, start, s.Dur, 0, first);
                Array.Copy(_gc, start, s.Gc, 0, first); Array.Copy(_ew, start, s.Ew, 0, first);
                Array.Copy(_stage, start * S.N, s.Stage, 0, first * S.N);
                if (second > 0)
                {
                    Array.Copy(_tg, 0, s.Tg, first, second); Array.Copy(_dur, 0, s.Dur, first, second);
                    Array.Copy(_gc, 0, s.Gc, first, second); Array.Copy(_ew, 0, s.Ew, first, second);
                    Array.Copy(_stage, 0, s.Stage, first * S.N, second * S.N);
                }
            }
        }

        /// <summary>A copy of the ring for the writer thread. Pooled: allocated at most PoolSize times per process.</summary>
        public sealed class FlightSnap
        {
            public readonly int[] Tg, Dur, Stage;
            public readonly byte[] Gc;
            public readonly short[] Ew;
            public int Count;
            public FlightSnap(int capacity)
            {
                Tg = new int[capacity]; Dur = new int[capacity]; Stage = new int[capacity * S.N];
                Gc = new byte[capacity]; Ew = new short[capacity];
            }

            public int TickFrom => Count > 0 ? Tg[0] : -1;
            public int TickTo => Count > 0 ? Tg[Count - 1] : -1;

            /// <summary>Index of the slowest tick, or -1.</summary>
            public int Worst()
            {
                int w = -1;
                for (int i = 0; i < Count; i++) if (w < 0 || Dur[i] > Dur[w]) w = i;
                return w;
            }
        }

        public sealed class SnapPool
        {
            public const int PoolSize = 2;
            private readonly object _g = new object();
            private readonly Stack<FlightSnap> _free = new Stack<FlightSnap>();
            private int _made;
            private readonly int _cap;
            public long Exhausted;
            public SnapPool(int capacity) { _cap = capacity; }

            public FlightSnap Rent()
            {
                lock (_g)
                {
                    if (_free.Count > 0) return _free.Pop();
                    if (_made < PoolSize) { _made++; return new FlightSnap(_cap); }
                    Exhausted++;
                    return null;
                }
            }

            public void Return(FlightSnap s) { if (s == null) return; lock (_g) { s.Count = 0; _free.Push(s); } }
        }

        // ------------------------------------------------------------------ dump rate limit
        public sealed class FlightGate
        {
            private double _last = double.NegativeInfinity;
            public int SuppressedSinceLast;
            public long Suppressed, Fired;
            public readonly double MinInterval;
            public FlightGate(double minInterval = DumpMinIntervalSeconds) { MinInterval = minInterval; }

            /// <summary>True (and the clock restarts) when at least MinInterval has passed since the last fired dump;
            /// otherwise the trigger is counted as suppressed. <paramref name="suppressedBefore"/> = triggers suppressed
            /// since the previous dump (carried on the flight row).</summary>
            public bool TryFire(double now, out int suppressedBefore)
            {
                suppressedBefore = SuppressedSinceLast;
                if (now - _last < MinInterval) { SuppressedSinceLast++; Suppressed++; return false; }
                _last = now;
                SuppressedSinceLast = 0;
                Fired++;
                return true;
            }

            public void Reset() { _last = double.NegativeInfinity; SuppressedSinceLast = 0; }
        }

        // ------------------------------------------------------------------ the log counter
        public sealed class ExcCounter
        {
            public const char LError = 'E', LErrorOnce = 'O', LWarning = 'W', LWarningOnce = 'V', LMessage = 'M';
            /// <summary>An ErrorOnce/WarningOnce call whose key vanilla already used: it writes NOTHING, so it is counted
            /// only in `rep` - never in e/w, the signature table, the burst trigger or the flight ring's logEW.</summary>
            public const char LOnceRepeat = 'R';
            private readonly object _g = new object();
            private readonly Dictionary<string, int> _win = new Dictionary<string, int>(StringComparer.Ordinal);
            private readonly HashSet<string> _seen = new HashSet<string>(StringComparer.Ordinal);
            /// <summary>Once-repeats per window by their ErrorOnce/WarningOnce KEY (no string is built for a repeat: it can
            /// run hundreds of times a second). The key joins the `|key=` of that signature's first-sight line.</summary>
            private readonly Dictionary<int, int> _repKeys = new Dictionary<int, int>();
            private long _n, _sup, _e, _w, _m, _over, _rep;
            /// <summary>Running error+warning count (all levels except Message and once-repeats), read per tick by the flight ring.</summary>
            public long ErrWarnTotal;
            public long SeenOverflow, Total;

            /// <summary>The signature: level, ':', the first 160 chars of the message with every digit as '#', then
            /// '|key=' and the ErrorOnce/WarningOnce key when there is one.</summary>
            public static string Signature(char level, string text, int? key)
            {
                string t = text ?? "";
                int n = Math.Min(t.Length, ExcSigLen);
                var c = new char[n];
                for (int i = 0; i < n; i++)
                {
                    char ch = t[i];
                    c[i] = ch >= '0' && ch <= '9' ? '#' : (ch == '\n' || ch == '\r' || ch == '\t' ? ' ' : ch);
                }
                string s = level + ":" + new string(c);
                return key.HasValue ? s + "|key=" + key.Value.ToString(CultureInfo.InvariantCulture) : s;
            }

            /// <summary>Count one call. Returns true when this signature was never seen before in this session (the caller
            /// writes the full message + stack once). The session set is capped; past it nothing is "first" again.</summary>
            public bool Note(char level, string sig, bool suppressed)
            {
                lock (_g)
                {
                    _n++; Total++;
                    if (level == LOnceRepeat) { _rep++; return false; }   // keyless repeat (see NoteRepeat)
                    if (suppressed) _sup++;
                    if (level == LMessage) _m++;
                    else
                    {
                        Interlocked.Increment(ref ErrWarnTotal);
                        if (level == LWarning || level == LWarningOnce) _w++; else _e++;
                    }
                    int c;
                    if (_win.TryGetValue(sig, out c)) _win[sig] = c + 1;
                    else if (_win.Count < ExcWindowSigs) _win[sig] = 1;
                    else _over++;
                    if (_seen.Contains(sig)) return false;
                    if (_seen.Count >= ExcSessionSigs) { SeenOverflow++; return false; }
                    _seen.Add(sig);
                    return true;
                }
            }

            /// <summary>Count one once-repeat and remember its key for the window's `repTop`.</summary>
            public void NoteRepeat(int key)
            {
                lock (_g)
                {
                    _n++; Total++; _rep++;
                    int c;
                    if (_repKeys.TryGetValue(key, out c)) _repKeys[key] = c + 1;
                    else if (_repKeys.Count < ExcWindowSigs) _repKeys[key] = 1;
                }
            }

            public long ErrWarnNow { get { return Interlocked.Read(ref ErrWarnTotal); } }

            /// <summary>`"exc":{"n","sup","e","w","m","rep","over","top":[[sig,count]...5]}` (no outer braces), then reset the
            /// window. n = every counted call (e + w + m + rep); <paramref name="errWarn"/> = e + w, which is what the
            /// exception-burst trigger compares (messages and once-repeats are not exceptions).</summary>
            public string TakeFields(out long errWarn)
            {
                lock (_g)
                {
                    errWarn = _e + _w;
                    var sb = new StringBuilder(200);
                    sb.Append("\"exc\":{\"n\":").Append(_n).Append(",\"sup\":").Append(_sup).Append(",\"e\":").Append(_e)
                      .Append(",\"w\":").Append(_w).Append(",\"m\":").Append(_m).Append(",\"rep\":").Append(_rep).Append(",\"over\":").Append(_over).Append(",\"top\":[");
                    int k = 0;
                    foreach (var kv in _win.OrderByDescending(p => p.Value).ThenBy(p => p.Key, StringComparer.Ordinal))
                    {
                        if (k >= ExcTop) break;
                        if (k++ > 0) sb.Append(',');
                        sb.Append('[').Append(M.Json(kv.Key)).Append(',').Append(kv.Value).Append(']');
                    }
                    sb.Append("],\"repTop\":[");
                    k = 0;
                    foreach (var kv in _repKeys.OrderByDescending(p => p.Value).ThenBy(p => p.Key))
                    {
                        if (k >= ExcTop) break;
                        if (k++ > 0) sb.Append(',');
                        sb.Append('[').Append(kv.Key.ToString(CultureInfo.InvariantCulture)).Append(',').Append(kv.Value).Append(']');
                    }
                    sb.Append("]}");
                    _win.Clear();
                    _repKeys.Clear();
                    _n = _sup = _e = _w = _m = _over = _rep = 0;
                    return sb.ToString();
                }
            }

            /// <summary>The first-sight line for exc_&lt;session&gt;.jsonl: message + stack together truncated to 4 KB.</summary>
            public static string FirstSightLine(string utc, string session, char level, string sig, int? key, bool suppressed,
                                                int tg, string text, string stack)
            {
                string msg = text ?? "";
                if (msg.Length > ExcFirstSightBytes) msg = msg.Substring(0, ExcFirstSightBytes);
                string st = stack ?? "";
                int room = ExcFirstSightBytes - msg.Length;
                if (st.Length > room) st = st.Substring(0, Math.Max(0, room));
                return "{\"excV\":1,\"utc\":\"" + utc + "\",\"session\":\"" + session + "\",\"level\":\"" + LevelName(level) +
                       "\",\"sig\":" + M.Json(sig) + ",\"key\":" + (key.HasValue ? key.Value.ToString(CultureInfo.InvariantCulture) : "null") +
                       ",\"sup\":" + (suppressed ? "true" : "false") + ",\"tg\":" + tg +
                       ",\"msg\":" + M.Json(msg) + ",\"stack\":" + M.Json(st) + "}";
            }

            public static string LevelName(char l)
            {
                switch (l)
                {
                    case LError: return "error";
                    case LErrorOnce: return "errorOnce";
                    case LWarning: return "warning";
                    case LWarningOnce: return "warningOnce";
                    default: return "message";
                }
            }
        }

        // ------------------------------------------------------------------ bridge occupancy (main thread + Interlocked)
        public sealed class BridgeOcc
        {
            public long Calls, MainTicks, QMaxTicks;
            /// <summary>Stopwatch time of the first enqueue since the last pump (0 = none); set from any thread.</summary>
            public long FirstEnqueue;

            public string TakeFields(double freq)
            {
                string s = "\"br\":{\"calls\":" + Calls + ",\"mainMs\":" + M.F(MainTicks * 1000.0 / freq, 2) +
                           ",\"qMaxMs\":" + M.F(QMaxTicks * 1000.0 / freq, 2) + "}";
                Calls = 0; MainTicks = 0; QMaxTicks = 0;
                return s;
            }
        }

        // ------------------------------------------------------------------ flight side file
        public static readonly string[] FlightFields =
            { "tg", "durUs", "tickOther", "tl:Normal", "tl:Rare", "tl:Long", "world", "worldPost", "mapPre", "mapPost", "mapComp", "gameComp", "gc0", "logEW" };

        public static string FlightFileName(string session, int seq) =>
            "flight_" + session + "_" + seq.ToString("D4", CultureInfo.InvariantCulture) + ".jsonl.gz";

        public static string FlightHeader(string session, int seq, string trigger, string utc, FlightSnap s, double freq)
        {
            int w = s.Worst();
            return "{\"flightV\":1,\"session\":\"" + session + "\",\"seq\":" + seq + ",\"trigger\":" + M.Json(trigger) +
                   ",\"utc\":\"" + utc + "\",\"tickFrom\":" + s.TickFrom + ",\"tickTo\":" + s.TickTo + ",\"ticks\":" + s.Count +
                   ",\"worstDurUs\":" + (w < 0 ? 0 : s.Dur[w]) + ",\"worstTg\":" + (w < 0 ? -1 : s.Tg[w]) +
                   ",\"freqHz\":" + M.F(freq, 0) +
                   ",\"fields\":[" + string.Join(",", FlightFields.Select(f => "\"" + f + "\"").ToArray()) + "]" +
                   ",\"stageFields\":\"exclusive stage time in microseconds; tickOther = tick minus its timed children; mapPost excludes mapComp\"}";
        }

        /// <summary>One tick as a JSON array in FlightFields order.</summary>
        public static void AppendTick(StringBuilder sb, FlightSnap s, int i)
        {
            sb.Append('[').Append(s.Tg[i]).Append(',').Append(s.Dur[i]);
            int b = i * S.N;
            for (int k = 0; k < S.N; k++) sb.Append(',').Append(s.Stage[b + k]);
            sb.Append(',').Append(s.Gc[i]).Append(',').Append(s.Ew[i]).Append(']');
        }

        /// <summary>Write the gzip side file (writer thread). Returns its byte size.</summary>
        public static long WriteFlightFile(string path, string header, FlightSnap s)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            string tmp = path + ".tmp";
            using (var fs = new FileStream(tmp, FileMode.Create, FileAccess.Write, FileShare.None))
            using (var gz = new GZipStream(fs, CompressionMode.Compress))
            using (var tw = new StreamWriter(gz, new UTF8Encoding(false)))
            {
                tw.Write(header); tw.Write('\n');
                var sb = new StringBuilder(128);
                for (int i = 0; i < s.Count; i++)
                {
                    sb.Length = 0;
                    AppendTick(sb, s, i);
                    tw.Write(sb.ToString()); tw.Write('\n');
                }
            }
            if (File.Exists(path)) File.Delete(path);
            File.Move(tmp, path);
            return new FileInfo(path).Length;
        }

        /// <summary>Directory cap, oldest first: indices to delete so the total fits <paramref name="cap"/>. The file at
        /// <paramref name="keep"/> (the one just written) is never chosen.</summary>
        public static List<int> PlanCap(IList<long> bytes, IList<double> ageSeconds, long cap, int keep)
        {
            long total = 0;
            for (int i = 0; i < bytes.Count; i++) total += bytes[i];
            var del = new List<int>();
            foreach (int i in Enumerable.Range(0, bytes.Count).OrderByDescending(i => ageSeconds[i]).ThenBy(i => i))
            {
                if (total <= cap) break;
                if (i == keep) continue;
                del.Add(i);
                total -= bytes[i];
            }
            return del;
        }

        /// <summary>Apply PlanCap to the flight directory (writer thread).</summary>
        public static int EnforceFlightCap(string dir, string keepPath, long cap)
        {
            if (!Directory.Exists(dir)) return 0;
            var files = new DirectoryInfo(dir).GetFiles("flight_*.jsonl.gz").ToList();
            var now = DateTime.UtcNow;
            int keep = files.FindIndex(f => string.Equals(f.FullName, Path.GetFullPath(keepPath), StringComparison.OrdinalIgnoreCase));
            var del = PlanCap(files.Select(f => f.Length).ToList(), files.Select(f => (now - f.LastWriteTimeUtc).TotalSeconds).ToList(), cap, keep);
            int n = 0;
            foreach (int i in del) { try { files[i].Delete(); n++; } catch { } }
            return n;
        }
    }
}
