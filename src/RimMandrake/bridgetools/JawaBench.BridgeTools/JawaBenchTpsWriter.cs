// JawaBenchTpsWriter.cs - the TPS record's ONE ordered, bounded writer (BRIDGE_TPS_CAPTURE_FIXES_1, item 4).
//
// Replaces "one thread-pool job per sample" (unordered, unbounded, a rotation that deleted the archive
// before moving the live file). Now:
//   * Every line gets a sequence number under one lock at ENQUEUE time, so the file order is the
//     event order, across the main thread, the watchdog thread and shutdown.
//   * One dedicated background thread drains the queue in batches. The queue is bounded
//     (JawaBenchTpsMath.QueueCapacity); a line beyond it is DROPPED and counted - the game is never
//     blocked by the disk. A failed write keeps the batch for retry (bounded the same way) and counts
//     writeErrors; the counters ride on every window line (wq/wdrop/werr) so a writer that is failing
//     is visible in the record itself and in jawa/tps_report.
//   * Files are session-named SEGMENTS: tps_<startUtc>_<session>_<pid>_<seg>.jsonl. A full segment is
//     simply closed and the next number opened: rotation never moves, renames or deletes a file that
//     holds history, and two game processes can never write the same file.
//   * Retention (JawaBenchTpsMath.PlanRetention): files older than RetentionDays go; then, only if the
//     directory exceeds the byte cap, the oldest go first. A current-session file is never deleted.
//   * Durability: each batch is written and the file CLOSED, so it is in the OS cache the moment the
//     batch ends - a killed or crashed game loses at most the lines still queued (normally < 1 s).
//     An OS crash or power cut can still lose the OS cache; that limit is stated in the doc.
//
// ⛔ No Verse/Unity calls on the writer thread (Unity APIs are main-thread only).

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchTpsWriter
    {
        private static readonly object Q = new object();
        private static readonly Queue<string> Pending = new Queue<string>();
        private static readonly List<string> Retry = new List<string>();
        private static Thread _thread;
        private static long _seq;
        private static bool _draining;
        private static int _inFlight;

        internal static long Enqueued, Written, Dropped, WriteErrors;
        internal static string LastError;
        internal static string Dir, Session, CurrentPath, LogDir;
        internal static int Pid;
        internal static long RetentionCapBytes = M.RetentionBytes;
        internal static long LogRetentionCapBytes = M.LogRetentionBytes;
        internal static double RetentionDays = M.RetentionDays;
        private static DateTime _startUtc;
        private static int _segment;
        private static long _bytes;
        internal static readonly Stopwatch Clock = Stopwatch.StartNew();   // monotonic, process-relative

        internal static bool Running => _thread != null;
        internal static int QueueDepth { get { lock (Q) return Pending.Count + Retry.Count; } }

        internal static void Start(string dir, string session, int pid)
        {
            lock (Q)
            {
                if (_thread != null) return;
                Dir = dir;
                LogDir = Path.Combine(dir, "logs");
                Session = session;
                Pid = pid;
                _startUtc = DateTime.UtcNow;
                Directory.CreateDirectory(dir);
                Directory.CreateDirectory(LogDir);
                OpenSegment(0);
                _thread = new Thread(Loop) { IsBackground = true, Name = "JawaBench.TpsWriter", Priority = ThreadPriority.BelowNormal };
                _thread.Start();
            }
            RunRetention();
        }

        private static void OpenSegment(int n)
        {
            _segment = n;
            CurrentPath = Path.Combine(Dir, M.SegmentName(_startUtc, Session, Pid, n));
            _bytes = File.Exists(CurrentPath) ? new FileInfo(CurrentPath).Length : 0L;
        }

        internal static string Utc()
        {
            return DateTime.UtcNow.ToString("yyyy-MM-dd'T'HH:mm:ss.fff'Z'", CultureInfo.InvariantCulture);
        }

        /// <summary>
        /// Append one record line. <paramref name="fields"/> are JSON fields without braces (may be empty).
        /// Thread-safe, never blocks on disk, never throws. Returns the line's seq, or -1 if dropped.
        /// </summary>
        internal static long Enqueue(string kind, string fields)
        {
            try
            {
                lock (Q)
                {
                    long seq = ++_seq;
                    if (Pending.Count + Retry.Count >= M.QueueCapacity)
                    {
                        Dropped++;
                        return -1;
                    }
                    Pending.Enqueue(Envelope(seq, Utc(), Clock.Elapsed.TotalSeconds, Session, kind, fields));
                    Enqueued++;
                    Monitor.Pulse(Q);
                    return seq;
                }
            }
            catch { return -1; }
        }

        /// <summary>One record line: the envelope keys, then the caller's fields.</summary>
        internal static string Envelope(long seq, string utc, double mono, string session, string kind, string fields)
        {
            var sb = new StringBuilder(96 + (fields?.Length ?? 0));
            sb.Append("{\"seq\":").Append(seq)
              .Append(",\"utc\":\"").Append(utc).Append('"')
              .Append(",\"mono\":").Append(M.F(mono, 3))
              .Append(",\"session\":\"").Append(session).Append('"')
              .Append(",\"kind\":\"").Append(kind).Append('"');
            if (!string.IsNullOrEmpty(fields)) sb.Append(',').Append(fields);
            return sb.Append('}').ToString();
        }

        /// <summary>The writer's health as JSON fields, carried on every window line.</summary>
        internal static string HealthFields()
        {
            lock (Q)
                return "\"wq\":" + (Pending.Count + Retry.Count) + ",\"wdrop\":" + Dropped + ",\"werr\":" + WriteErrors;
        }

        private static void Loop()
        {
            var batch = new List<string>();
            while (true)
            {
                lock (Q)
                {
                    while (Pending.Count == 0 && Retry.Count == 0) Monitor.Wait(Q, 1000);
                    batch.Clear();
                    batch.AddRange(Retry);
                    Retry.Clear();
                    while (Pending.Count > 0) batch.Add(Pending.Dequeue());
                    _inFlight = batch.Count;
                }
                if (batch.Count == 0) continue;
                if (!WriteBatch(batch))
                {
                    lock (Q)
                    {
                        // keep for retry, oldest first, bounded: the overflow is counted, never silently lost
                        int room = Math.Max(0, M.QueueCapacity - Pending.Count);
                        if (batch.Count > room) { Dropped += batch.Count - room; batch.RemoveRange(0, batch.Count - room); }
                        Retry.InsertRange(0, batch);
                    }
                    Thread.Sleep(1000);
                }
                lock (Q) { _inFlight = 0; Monitor.PulseAll(Q); }
            }
        }

        private static bool WriteBatch(List<string> lines)
        {
            try
            {
                int i = 0;
                while (i < lines.Count)
                {
                    var buf = new MemoryStream();
                    bool rotated = false;
                    while (i < lines.Count)
                    {
                        byte[] b = Encoding.UTF8.GetBytes(lines[i] + "\n");
                        if (M.ShouldRotate(_bytes + buf.Length, b.Length) && (_bytes + buf.Length) > 0)
                        {
                            rotated = true;
                            break;
                        }
                        buf.Write(b, 0, b.Length);
                        i++;
                    }
                    if (buf.Length > 0)
                    {
                        using (var fs = new FileStream(CurrentPath, FileMode.Append, FileAccess.Write, FileShare.ReadWrite | FileShare.Delete))
                            buf.WriteTo(fs);
                        _bytes += buf.Length;
                    }
                    if (rotated)
                    {
                        OpenSegment(_segment + 1);
                        RunRetention();
                    }
                }
                Written += lines.Count;
                LastError = null;
                return true;
            }
            catch (Exception e)
            {
                WriteErrors++;
                LastError = e.GetType().Name + ": " + e.Message;
                return false;
            }
        }

        /// <summary>Wait (bounded) until everything queued so far is on disk. For shutdown.</summary>
        internal static bool Drain(int timeoutMs)
        {
            if (_thread == null) return false;
            var until = DateTime.UtcNow.AddMilliseconds(timeoutMs);
            lock (Q)
            {
                if (_draining) return false;
                _draining = true;
                try
                {
                    Monitor.PulseAll(Q);
                    while (Pending.Count + Retry.Count + _inFlight > 0)
                    {
                        int left = (int)(until - DateTime.UtcNow).TotalMilliseconds;
                        if (left <= 0) return false;
                        Monitor.Wait(Q, Math.Min(left, 100));
                    }
                    return true;
                }
                finally { _draining = false; }
            }
        }

        /// <summary>Apply retention to the record dir (segments, heartbeats, session manifests) and the log archive.</summary>
        internal static void RunRetention()
        {
            try
            {
                Prune(Dir, new[] { "tps_*.jsonl", "hb_*.json", "session_*.json" }, RetentionCapBytes);
                Prune(LogDir, new[] { "*.log" }, LogRetentionCapBytes);
            }
            catch (Exception e)
            {
                LastError = "retention: " + e.GetType().Name + ": " + e.Message;
            }
        }

        private static void Prune(string dir, string[] patterns, long cap)
        {
            if (string.IsNullOrEmpty(dir) || !Directory.Exists(dir)) return;
            var files = patterns.SelectMany(p => new DirectoryInfo(dir).GetFiles(p)).GroupBy(f => f.FullName).Select(g => g.First()).ToList();
            var now = DateTime.UtcNow;
            var del = PlanWithDays(files.Select(f => f.Length).ToList(),
                                   files.Select(f => (now - f.LastWriteTimeUtc).TotalDays).ToList(),
                                   files.Select(f => f.Name.IndexOf(Session, StringComparison.Ordinal) >= 0).ToList(), cap);
            foreach (int i in del)
            {
                try { files[i].Delete(); } catch { }
            }
        }

        private static List<int> PlanWithDays(IList<long> bytes, IList<double> age, IList<bool> current, long cap)
        {
            // the settings file may LENGTHEN retention; PlanRetention's age rule is scaled to match.
            double k = RetentionDays > 0 ? M.RetentionDays / RetentionDays : 1.0;
            return M.PlanRetention(bytes, age.Select(a => a * k).ToList(), current, cap);
        }

        /// <summary>Copy a file into the log archive off the main thread (best effort, retention-bounded).</summary>
        internal static void ArchiveLog(string source, string name)
        {
            ThreadPool.QueueUserWorkItem(_ => ArchiveLogNow(source, name));
        }

        internal static void ArchiveLogNow(string source, string name)
        {
            try
            {
                if (string.IsNullOrEmpty(source) || !File.Exists(source)) return;
                string dst = Path.Combine(LogDir, name);
                if (File.Exists(dst) && new FileInfo(dst).Length == new FileInfo(source).Length) return;
                using (var src = new FileStream(source, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete))
                using (var o = new FileStream(dst, FileMode.Create, FileAccess.Write, FileShare.Read))
                    src.CopyTo(o);
                Enqueue("log", "\"archived\":" + Json(dst) + ",\"from\":" + Json(source));
                RunRetention();
            }
            catch (Exception e)
            {
                Enqueue("error", "\"where\":\"log-archive\",\"error\":" + Json(e.GetType().Name + ": " + e.Message));
            }
        }

        internal static string Json(string s) => M.Json(s);
    }
}
