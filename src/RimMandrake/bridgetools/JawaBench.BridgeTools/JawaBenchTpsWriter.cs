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

        // ---- test seams (the offline harness swaps these to inject faults; production never touches them) ----
        /// <summary>Append bytes to a file. Default: open for append, write, close.</summary>
        internal static Action<string, byte[], int> AppendImpl = (path, buf, len) =>
        {
            using (var fs = new FileStream(path, FileMode.Append, FileAccess.Write, FileShare.ReadWrite | FileShare.Delete))
                fs.Write(buf, 0, len);
        };
        private static volatile bool _stop;

        /// <summary>Stop the writer thread (harness only) and forget all state, so a test starts clean.</summary>
        internal static void ResetForTest()
        {
            _stop = true;
            lock (Q) Monitor.PulseAll(Q);
            _thread?.Join(5000);
            lock (Q)
            {
                _thread = null; _stop = false;
                Pending.Clear(); Retry.Clear(); _inFlight = 0; _seq = 0; _draining = false;
                Enqueued = Written = Dropped = WriteErrors = 0; LastError = null;
            }
        }
        /// <summary>All outstanding lines: queued + awaiting retry + in flight (MUST 14).</summary>
        internal static int QueueDepth { get { lock (Q) return Pending.Count + Retry.Count + _inFlight; } }
        internal static long TornTails;

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
        /// MUST 14: the bound is on ALL outstanding work - queued, waiting for retry AND in flight in the writer
        /// thread - so it can never approach twice QueueCapacity. Bulk rows (sample, context, marker) may use
        /// only QueueCapacity - CriticalReserve of it; lifecycle, incident, silence and error rows keep the
        /// reserve, so they are written exactly when storage trouble makes them matter. A dropped row still
        /// consumes its seq, so the gap is visible on disk; drops are counted and their seq range reported in
        /// a `dropped` row once the writer catches up.
        /// </summary>
        internal static long Enqueue(string kind, string fields)
        {
            try
            {
                lock (Q)
                {
                    long seq = ++_seq;
                    int outstanding = Pending.Count + Retry.Count + _inFlight;
                    int limit = IsBulk(kind) ? M.QueueCapacity - M.CriticalReserve : M.QueueCapacity;
                    if (outstanding >= limit)
                    {
                        NoteDrop(seq, !IsBulk(kind));
                        return -1;
                    }
                    Pending.Enqueue(Envelope(seq, Utc(), Clock.Elapsed.TotalSeconds, Session, kind, fields));
                    Enqueued++;
                    Monitor.Pulse(Q);
                    return seq;
                }
            }
            catch
            {
                try { lock (Q) NoteDrop(-1, true); } catch { }
                return -1;
            }
        }

        internal static bool IsBulk(string kind) => kind == "sample" || kind == "context" || kind == "marker";

        private static long _dropFirst = -1, _dropLast = -1, _dropPending;
        internal static long DroppedCritical;

        private static void NoteDrop(long seq, bool critical)
        {
            Dropped++;
            if (critical) DroppedCritical++;
            if (seq > 0)
            {
                if (_dropFirst < 0) _dropFirst = seq;
                _dropLast = seq;
            }
            _dropPending++;
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
                return "\"wq\":" + (Pending.Count + Retry.Count + _inFlight) + ",\"wfly\":" + _inFlight +
                       ",\"wdrop\":" + Dropped + ",\"wdropCrit\":" + DroppedCritical + ",\"werr\":" + WriteErrors +
                       ",\"wtorn\":" + TornTails;
        }

        private static void Loop()
        {
            var batch = new List<string>();
            while (!_stop)
            {
                lock (Q)
                {
                    while (Pending.Count == 0 && Retry.Count == 0 && !_stop) Monitor.Wait(Q, 1000);
                    if (_stop) return;
                    batch.Clear();
                    batch.AddRange(Retry);
                    Retry.Clear();
                    while (Pending.Count > 0) batch.Add(Pending.Dequeue());
                    _inFlight = batch.Count;
                }
                int done = WriteBatch(batch);
                lock (Q)
                {
                    // MUST 4: commit-aware. Only the lines NOT yet on disk go back for retry (front of the
                    // line, in order); the bound already counted them as in flight, so nothing is dropped here.
                    Written += done;
                    if (done < batch.Count) Retry.InsertRange(0, batch.GetRange(done, batch.Count - done));
                    _inFlight = 0;
                    if (done == batch.Count && _dropPending > 0)
                    {
                        long first = _dropFirst, last = _dropLast, n = _dropPending;
                        _dropFirst = _dropLast = -1;
                        _dropPending = 0;
                        long seq = ++_seq;
                        Pending.Enqueue(Envelope(seq, Utc(), Clock.Elapsed.TotalSeconds, Session, "dropped",
                            "\"count\":" + n + ",\"seqFirst\":" + first + ",\"seqLast\":" + last +
                            ",\"wdrop\":" + Dropped + ",\"wdropCrit\":" + DroppedCritical));
                        Enqueued++;
                    }
                    Monitor.PulseAll(Q);
                }
                if (done < batch.Count) Thread.Sleep(1000);
            }
        }

        /// <summary>
        /// Append the lines in order, one segment-bounded chunk at a time. Returns how many lines are COMMITTED
        /// (every byte of them appended); the caller retries only the rest. Before each append the file length
        /// is reconciled with what we believe we wrote: a failed append can leave a TORN tail (part of a chunk),
        /// which is truncated away, or - if truncation fails - closed with a newline so the fragment stays a
        /// lone malformed line the reader counts instead of being glued to the next row.
        /// </summary>
        private static int WriteBatch(List<string> lines)
        {
            int committed = 0;
            try
            {
                int i = 0;
                while (i < lines.Count)
                {
                    Reconcile();
                    var buf = new MemoryStream();
                    bool rotated = false;
                    int start = i;
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
                        AppendImpl(CurrentPath, buf.GetBuffer(), (int)buf.Length);
                        _bytes += buf.Length;
                    }
                    committed = i;
                    if (rotated)
                    {
                        OpenSegment(_segment + 1);
                        RunRetention();
                    }
                    if (i == start && !rotated) break;   // defensive: no progress
                }
                LastError = null;
                return committed;
            }
            catch (Exception e)
            {
                WriteErrors++;
                LastError = e.GetType().Name + ": " + e.Message;
                return committed;
            }
        }

        /// <summary>Make the file length agree with the bytes we know we committed (see WriteBatch).</summary>
        private static void Reconcile()
        {
            long actual = File.Exists(CurrentPath) ? new FileInfo(CurrentPath).Length : 0L;
            if (actual == _bytes) return;
            if (actual > _bytes)
            {
                TornTails++;
                try
                {
                    using (var fs = new FileStream(CurrentPath, FileMode.Open, FileAccess.Write, FileShare.ReadWrite | FileShare.Delete))
                        fs.SetLength(_bytes);
                    return;
                }
                catch
                {
                    var nl = new byte[] { (byte)'\n' };
                    AppendImpl(CurrentPath, nl, 1);
                    _bytes = actual + 1;
                    return;
                }
            }
            _bytes = actual;     // the file shrank under us (deleted / replaced): continue from what is there
            LastError = "segment shrank under the writer: " + Path.GetFileName(CurrentPath);
        }

        /// <summary>Wait (bounded) until everything queued so far is on disk. For shutdown.</summary>
        internal static bool Drain(int timeoutMs)
        {
            if (_thread == null) return false;
            var sw = Stopwatch.StartNew();        // monotonic: a wall-clock jump cannot stretch or cut the bound
            lock (Q)
            {
                if (_draining) return false;
                _draining = true;
                try
                {
                    Monitor.PulseAll(Q);
                    while (Pending.Count + Retry.Count + _inFlight > 0)
                    {
                        int left = timeoutMs - (int)sw.ElapsedMilliseconds;
                        if (left <= 0) return false;
                        Monitor.Wait(Q, Math.Min(left, 100));
                    }
                    return true;
                }
                finally { _draining = false; }
            }
        }

        /// <summary>
        /// MUST 16: shutdown as INTENT then COMPLETION. Writes `shutdown` (intent, with the caller's fields),
        /// drains (bounded), runs <paramref name="archive"/> (the Player.log copy) on a thread and waits at most
        /// <paramref name="archiveMs"/>, then writes `shutdown-complete` stating drained / archived /
        /// archiveTimedOut / elapsed ms, and drains again. A reader treats only intent + completion as a clean
        /// end. Every bound is monotonic. Returns the completion fields.
        /// </summary>
        internal static string Shutdown(string fields, Func<string> archive, int drainMs, int archiveMs)
        {
            var sw = Stopwatch.StartNew();
            Enqueue("shutdown", "\"phase\":\"intent\"" + (string.IsNullOrEmpty(fields) ? "" : "," + fields));
            bool drained = Drain(drainMs);
            string archived = null;
            bool timedOut = false;
            if (archive != null)
            {
                string result = null;
                var t = new Thread(() => { try { result = archive(); } catch { } }) { IsBackground = true, Name = "JawaBench.TpsLogCopy" };
                t.Start();
                timedOut = !t.Join(archiveMs);
                archived = timedOut ? null : result;
            }
            string done = "\"drained\":" + (drained ? "true" : "false") + ",\"archived\":" + (archived != null ? "true" : "false") +
                          ",\"archive\":" + Json(archived) + ",\"archiveTimedOut\":" + (timedOut ? "true" : "false") +
                          ",\"ms\":" + sw.ElapsedMilliseconds + "," + HealthFields();
            Enqueue("shutdown-complete", done);
            Drain(Math.Max(200, drainMs / 2));
            return done;
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

        /// <summary>A session whose heartbeat file changed within this many seconds is ACTIVE: its files are a
        /// live process's evidence and are never pruned by another process (the heartbeat is the lease).</summary>
        internal const double LeaseSeconds = 60;

        private static readonly System.Text.RegularExpressions.Regex SegRe =
            new System.Text.RegularExpressions.Regex("^tps_\\d{8}T\\d{6}Z_([0-9a-f]+)_\\d+_(\\d{3,})\\.jsonl$");
        private static readonly System.Text.RegularExpressions.Regex MetaRe =
            new System.Text.RegularExpressions.Regex("^(?:hb|session)_([0-9a-f]+)\\.json$");

        private static void Prune(string dir, string[] patterns, long cap)
        {
            if (string.IsNullOrEmpty(dir) || !Directory.Exists(dir)) return;
            var files = patterns.SelectMany(p => new DirectoryInfo(dir).GetFiles(p)).GroupBy(f => f.FullName).Select(g => g.First()).ToList();
            var now = DateTime.UtcNow;
            int n = files.Count;
            var sess = new string[n];
            var segNo = new int[n];
            for (int i = 0; i < n; i++)
            {
                var m = SegRe.Match(files[i].Name);
                if (m.Success) { sess[i] = m.Groups[1].Value; segNo[i] = int.Parse(m.Groups[2].Value, CultureInfo.InvariantCulture); continue; }
                segNo[i] = -1;
                var mm = MetaRe.Match(files[i].Name);
                sess[i] = mm.Success ? mm.Groups[1].Value : "file:" + files[i].Name;   // anything else: its own bundle
            }
            var activeSessions = new HashSet<string>(StringComparer.Ordinal) { Session ?? "" };
            for (int i = 0; i < n; i++)
                if (files[i].Name.StartsWith("hb_", StringComparison.Ordinal) && (now - files[i].LastWriteTimeUtc).TotalSeconds < LeaseSeconds)
                    activeSessions.Add(sess[i]);
            var liveSeg = new Dictionary<string, int>(StringComparer.Ordinal);
            for (int i = 0; i < n; i++)
                if (segNo[i] >= 0 && (!liveSeg.ContainsKey(sess[i]) || segNo[i] > liveSeg[sess[i]])) liveSeg[sess[i]] = segNo[i];
            var active = new bool[n];
            var pinned = new bool[n];
            for (int i = 0; i < n; i++)
            {
                active[i] = activeSessions.Contains(sess[i]);
                if (!active[i]) continue;
                bool own = sess[i] == Session;
                bool live = segNo[i] >= 0 && liveSeg[sess[i]] == segNo[i];
                pinned[i] = !own || live || segNo[i] < 0 || files[i].FullName == CurrentPath;
            }
            var del = M.PlanRetention(files.Select(f => f.Length).ToList(),
                                      files.Select(f => (now - f.LastWriteTimeUtc).TotalDays).ToList(),
                                      sess, pinned, active, cap, RetentionDays);
            foreach (int i in del)
            {
                try { files[i].Delete(); } catch { }
            }
        }

        /// <summary>Copy a file into the log archive off the main thread (best effort, retention-bounded).</summary>
        internal static void ArchiveLog(string source, string name, string fromSession = null)
        {
            ThreadPool.QueueUserWorkItem(_ => ArchiveLogNow(source, name, fromSession));
        }

        /// <summary>
        /// MUST 12: the archive name carries the content's SHA-256 (first 12 hex): <c>name_&lt;sha12&gt;.log</c>.
        /// The same content is archived once (any existing <c>*_&lt;sha12&gt;.log</c> = already kept, whoever wrote
        /// it - belt_watchdog's tps_record.preserve_prev_log uses the same rule); different content never
        /// overwrites or dedupes into another archive, whatever its length or second-resolution timestamp.
        /// The source is hashed from a snapshot copy, so a log still being written cannot mismatch its name.
        /// Returns the archive path, or null.
        /// </summary>
        internal static string ArchiveLogNow(string source, string name, string fromSession = null)
        {
            string tmp = null;
            try
            {
                if (string.IsNullOrEmpty(source) || !File.Exists(source)) return null;
                Directory.CreateDirectory(LogDir);
                tmp = Path.Combine(LogDir, ".archiving_" + Guid.NewGuid().ToString("N").Substring(0, 8) + ".tmp");
                string hex;
                using (var src = new FileStream(source, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete))
                using (var o = new FileStream(tmp, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                using (var sha = System.Security.Cryptography.SHA256.Create())
                {
                    var buf = new byte[1 << 16];
                    int n;
                    while ((n = src.Read(buf, 0, buf.Length)) > 0) { sha.TransformBlock(buf, 0, n, null, 0); o.Write(buf, 0, n); }
                    sha.TransformFinalBlock(buf, 0, 0);
                    hex = BitConverter.ToString(sha.Hash).Replace("-", "").ToLowerInvariant();
                }
                string tag = hex.Substring(0, 12);
                if (Directory.GetFiles(LogDir, "*_" + tag + ".log").Length > 0)
                {
                    File.Delete(tmp);
                    return null;
                }
                string stem = name.EndsWith(".log", StringComparison.OrdinalIgnoreCase) ? name.Substring(0, name.Length - 4) : name;
                string dst = Path.Combine(LogDir, stem + "_" + tag + ".log");
                File.Move(tmp, dst);
                tmp = null;
                Enqueue("log", "\"archived\":" + Json(dst) + ",\"from\":" + Json(source) + ",\"sha256\":\"" + hex + "\"" +
                               ",\"bytes\":" + new FileInfo(dst).Length + ",\"fromSession\":" + Json(fromSession));
                RunRetention();
                return dst;
            }
            catch (Exception e)
            {
                try { if (tmp != null && File.Exists(tmp)) File.Delete(tmp); } catch { }
                Enqueue("error", "\"where\":\"log-archive\",\"error\":" + Json(e.GetType().Name + ": " + e.Message));
                return null;
            }
        }

        internal static string Json(string s) => M.Json(s);
    }
}
