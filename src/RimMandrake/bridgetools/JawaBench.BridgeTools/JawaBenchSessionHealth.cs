// JawaBenchSessionHealth.cs - the standing game health check's in-game half (HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME,
// owner C24 in design/RimMandrake/mod_audit/OWNER_RULINGS.md). Reader: src/RimMandrake/Utils/game_health_check.py.
//
// Fields appended to every `context` row (once a minute, main thread, from JawaBenchTpsSampler.Context):
//   privateMB, workingSetMB   psapi GetProcessMemoryInfo(PROCESS_MEMORY_COUNTERS_EX) on the current process. Mono's
//                             Process.WorkingSet64 read 0 on every full-list session 2026-10-26..28, so it is not used.
//   unityAllocMB, unityReservedMB, monoUsedMB, monoHeapMB
//                             UnityEngine.Profiling.Profiler totals (native allocators; Mono heap as Unity sees it)
//   gfxMB                     Profiler.GetAllocatedMemoryForGraphicsDriver: a release player reads 0; the reader
//                             treats 0 as "not read" (UNMEASURED), never as zero memory
//   upS                       Time.realtimeSinceStartup: seconds since the process started (load time at the menu)
//   logMsgs, logCapReached, logEnabled
//                             Verse.Log.messageCount / reachedMaxMessagesLimit (private statics) and
//                             Debug.unityLogger.logEnabled, each null when unreadable
//   logErr, logWarn, logErrLowerBound
//                             error / warning entries (with repeats) seen in Verse.Log's message queue since this
//                             process registered. logErrLowerBound = true when the queue may have evicted entries
//                             before they were seen (full queue at the first read, or a full queue whose oldest entry
//                             is new). Unity-only messages that never pass Verse.Log are not in the queue.
//
// ⛔ NO HOOK, NO PATCH, NO SUBSCRIPTION: game_health_record.md forbids new always-on hooks until the overhead test
// (RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP) passes. This is a once-a-minute read beside the GC.GetTotalMemory the
// context row already makes: one psapi call, five Profiler getters, two reflected fields, one walk of <=1000 queue
// entries under Verse.Log's own lock (TryEnter, 5 ms; a busy lock skips the walk that minute: `logScan:"busy"`).
//
// ENGINE MEMBERS read from decompiled 1.6 (D:\ClaudeWork\rimmandrake\decomp\rw16\all\Verse, 2026-11-02):
//   Log: private static LogMessageQueue messageQueue; private static int messageCount; private static bool
//        reachedMaxMessagesLimit; private static object logLock (Error/Warning/Message enqueue under lock(logLock));
//        public static IEnumerable<LogMessage> Messages => messageQueue.Messages
//   LogMessageQueue: public int maxMessages = 1000; repeats of the last message bump lastMessage.repeats (cap 99)
//   LogMessage: public LogMessageType type; public int repeats = 1

using System;
using System.Collections.Generic;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using HarmonyLib;
using UnityEngine;
using Verse;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchSessionHealth
    {
        [StructLayout(LayoutKind.Sequential)]
        private struct Pmc
        {
            public uint cb, PageFaultCount;
            public UIntPtr PeakWorkingSetSize, WorkingSetSize, QuotaPeakPagedPoolUsage, QuotaPagedPoolUsage,
                QuotaPeakNonPagedPoolUsage, QuotaNonPagedPoolUsage, PagefileUsage, PeakPagefileUsage, PrivateUsage;
        }

        [DllImport("psapi.dll", SetLastError = true)]
        private static extern bool GetProcessMemoryInfo(IntPtr process, out Pmc counters, uint size);

        [DllImport("kernel32.dll")]
        private static extern IntPtr GetCurrentProcess();

        private sealed class RefEq : IEqualityComparer<LogMessage>
        {
            public bool Equals(LogMessage a, LogMessage b) => ReferenceEquals(a, b);
            public int GetHashCode(LogMessage m) => RuntimeHelpers.GetHashCode(m);
        }

        private static readonly FieldInfo FCount = AccessTools.Field(typeof(Log), "messageCount");
        private static readonly FieldInfo FReached = AccessTools.Field(typeof(Log), "reachedMaxMessagesLimit");
        private static readonly FieldInfo FLock = AccessTools.Field(typeof(Log), "logLock");
        private static readonly FieldInfo FQueue = AccessTools.Field(typeof(Log), "messageQueue");

        private static Dictionary<LogMessage, int> _seen = new Dictionary<LogMessage, int>(new RefEq());
        private static long _err, _warn;
        private static bool _lower, _first = true, _psapiFailed;

        private static string MB(double bytes) => M.F(bytes / 1048576.0, 1);

        /// <summary>The fields above, each with a leading comma. Main thread. Never throws.</summary>
        internal static string Fields()
        {
            var sb = new StringBuilder(400);
            try
            {
                if (!_psapiFailed)
                {
                    Pmc c;
                    uint size = (uint)Marshal.SizeOf(typeof(Pmc));
                    if (GetProcessMemoryInfo(GetCurrentProcess(), out c, size))
                        sb.Append(",\"privateMB\":").Append(MB(c.PrivateUsage.ToUInt64()))
                          .Append(",\"workingSetMB\":").Append(MB(c.WorkingSetSize.ToUInt64()));
                    else _psapiFailed = true;
                }
            }
            catch { _psapiFailed = true; }
            if (_psapiFailed) sb.Append(",\"workingSetMB\":0");     // the reader's "not read"
            try
            {
                sb.Append(",\"unityAllocMB\":").Append(MB(UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong()))
                  .Append(",\"unityReservedMB\":").Append(MB(UnityEngine.Profiling.Profiler.GetTotalReservedMemoryLong()))
                  .Append(",\"monoUsedMB\":").Append(MB(UnityEngine.Profiling.Profiler.GetMonoUsedSizeLong()))
                  .Append(",\"monoHeapMB\":").Append(MB(UnityEngine.Profiling.Profiler.GetMonoHeapSizeLong()))
                  .Append(",\"gfxMB\":").Append(MB(UnityEngine.Profiling.Profiler.GetAllocatedMemoryForGraphicsDriver()));
            }
            catch { }
            try { sb.Append(",\"upS\":").Append(M.F(Time.realtimeSinceStartup, 1)); } catch { }
            object count = null, reached = null;
            try { count = FCount?.GetValue(null); } catch { }
            try { reached = FReached?.GetValue(null); } catch { }
            sb.Append(",\"logMsgs\":").Append(count is int n ? n.ToString() : "null")
              .Append(",\"logCapReached\":").Append(reached is bool b ? (b ? "true" : "false") : "null");
            try { sb.Append(",\"logEnabled\":").Append(Debug.unityLogger.logEnabled ? "true" : "false"); } catch { }
            sb.Append(",\"logScan\":\"").Append(Scan()).Append('"')
              .Append(",\"logErr\":").Append(Interlocked.Read(ref _err))
              .Append(",\"logWarn\":").Append(Interlocked.Read(ref _warn))
              .Append(",\"logErrLowerBound\":").Append(_lower ? "true" : "false");
            return sb.ToString();
        }

        /// <summary>Count entries (with repeats) not counted before. ok | busy | unreadable.</summary>
        private static string Scan()
        {
            object gate = null;
            try { gate = FLock?.GetValue(null); } catch { }
            if (gate == null) return "unreadable";
            if (!Monitor.TryEnter(gate, 5)) return "busy";
            try
            {
                int max = 1000;
                try
                {
                    var q = FQueue?.GetValue(null) as LogMessageQueue;
                    if (q != null) max = q.maxMessages;
                }
                catch { }
                var next = new Dictionary<LogMessage, int>(new RefEq());
                int i = 0;
                bool oldestNew = false;
                foreach (var m in Log.Messages)
                {
                    if (m == null) continue;
                    int prev;
                    bool known = _seen.TryGetValue(m, out prev);
                    if (i == 0 && !known) oldestNew = true;
                    int d = known ? m.repeats - prev : m.repeats;
                    if (d > 0)
                    {
                        if (m.type == LogMessageType.Error) _err += d;
                        else if (m.type == LogMessageType.Warning) _warn += d;
                    }
                    next[m] = m.repeats;
                    i++;
                }
                if (i >= max && (_first || oldestNew)) _lower = true;
                _first = false;
                _seen = next;
                return "ok";
            }
            catch { return "unreadable"; }
            finally { Monitor.Exit(gate); }
        }
    }
}
