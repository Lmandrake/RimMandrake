// JawaBenchStallProbe.cs - the Verse half of the stall dump (BRIDGE_STALL_DIAGNOSTIC_1): the "top job" a minute-long
// silence was spent on, read OFF the main thread by JawaBenchStallDump.
//
// ⛔ No new hook on the hot path: the profiler's ruling keeps per-thing / per-pawn instrumentation out of the
// always-on path, so the current Thing is NOT known. What IS known for free: the attribution hook on TickList.Tick
// (JawaBenchTpsProfiler.TlPre) stashes the TickList it is entering and the tick it entered on (TlFin clears it, so a
// stall outside any tick list reads tickList null; with attribution off nothing is captured and `capture` says so).
// From that list this probe reads the bucket being ticked (thingLists[enteredTick % TickInterval]): its size, its most common defs, and
// its pawns with their current job and driver. The stuck thing is one of them; a series of dumps that shows the
// same tick and bucket says the main thread never left it.
// Every read is a racy field read on objects the stuck main thread is not moving; each one is guarded and a
// failure is reported in `errors`, never thrown.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using HarmonyLib;
using Verse;
using Verse.AI;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchStallProbe
    {
        internal const int TopDefs = 8, MaxPawns = 10;

        /// <summary>The TickList the main thread is INSIDE (JawaBenchTpsProfiler.TlPre sets it, TlFin clears it) and the game
        /// tick it entered on. Written on the main thread: CurTick first, then the list; read list, tick, ..., list, tick.</summary>
        internal static volatile TickList CurTickList;
        internal static volatile int CurTick = -1;

        internal static void Enter(TickList l, int tick) { CurTick = tick; CurTickList = l; }
        internal static void Leave() { CurTickList = null; }

        private static AccessTools.FieldRef<TickList, List<List<Thing>>> _lists;
        private static AccessTools.FieldRef<TickList, TickerType> _type;
        internal static string InstallError;

        /// <summary>Main thread, once, beside the watchdog's Start. Never throws. Runs every path of Read here (an empty
        /// bucket, a null pawn) so Mono JIT-compiles them on this thread, not on the watchdog during a stall.</summary>
        internal static void Install()
        {
            try
            {
                _lists = AccessTools.FieldRefAccess<TickList, List<List<Thing>>>("thingLists");
                _type = AccessTools.FieldRefAccess<TickList, TickerType>("tickType");
                JawaBenchStallDump.Probe = Read;
                Read();
                var sb = new StringBuilder();
                Bucket(sb, new List<Thing>());
                var warmDefs = new Dictionary<string, int> { { "warm", 1 } };
                sb.Append(TopDefsJson(warmDefs)).Append(PawnJson(null, "warm"));
            }
            catch (Exception e) { InstallError = e.GetType().Name + ": " + e.Message; }
        }

        private static int Interval(TickerType t) =>
            t == TickerType.Rare ? 250 : t == TickerType.Long ? 2000 : 1;   // TickList.TickInterval, decompiled 1.6

        internal static string Read()
        {
            var errors = new List<string>();
            var sb = new StringBuilder(1024).Append('{');
            int ticks = -1;
            try { ticks = Current.Game?.tickManager?.TicksGame ?? -1; } catch (Exception e) { errors.Add("ticks: " + e.GetType().Name); }
            sb.Append("\"ticksGameNow\":").Append(ticks)
              .Append(",\"capture\":").Append(M.Json(JawaBenchTpsProfiler.Installed ? "attribution hook on TickList.Tick"
                  : "OFF: TPS attribution is not installed, so no tick list is captured"));
            var tl = CurTickList;
            int tick = CurTick;
            if (tl == null) sb.Append(",\"tickList\":null");
            else
            {
                try
                {
                    TickerType tt = _type(tl);
                    int interval = Interval(tt);
                    var lists = _lists(tl);
                    int idx = tick >= 0 && interval > 0 ? tick % interval : -1;
                    sb.Append(",\"tickList\":").Append(M.Json(tt.ToString())).Append(",\"enteredTick\":").Append(tick)
                      .Append(",\"bucket\":").Append(idx);
                    List<Thing> bucket = lists != null && idx >= 0 && idx < lists.Count ? lists[idx] : null;
                    if (bucket == null) sb.Append(",\"bucketCount\":null");
                    else Bucket(sb, bucket);
                }
                catch (Exception e) { errors.Add("tickList: " + e.GetType().Name + ": " + e.Message); }
                // the main thread moved on while we read: the bucket may belong to another tick or list
                sb.Append(",\"changedDuringRead\":").Append(CurTickList != tl || CurTick != tick ? "true" : "false");
            }
            sb.Append(",\"errors\":[").Append(string.Join(",", errors.Select(M.Json))).Append("]}");
            return sb.ToString();
        }

        private static void Bucket(StringBuilder sb, List<Thing> bucket)
        {
            Thing[] things = bucket.ToArray();      // a snapshot; the list itself may be mid-mutation
            sb.Append(",\"bucketCount\":").Append(things.Length);
            var byDef = new Dictionary<string, int>();
            var pawns = new List<string>();
            foreach (var t in things)
            {
                if (t == null) continue;
                string dn = "?";
                try { dn = t.def?.defName ?? "?"; } catch { }
                byDef[dn] = byDef.TryGetValue(dn, out int c) ? c + 1 : 1;
                if (pawns.Count < MaxPawns && t is Pawn p) pawns.Add(PawnJson(p, dn));
            }
            sb.Append(",\"topDefs\":").Append(TopDefsJson(byDef));
            sb.Append(",\"pawns\":[").Append(string.Join(",", pawns)).Append(']');
        }

        private static string TopDefsJson(Dictionary<string, int> byDef) =>
            "[" + string.Join(",", byDef.OrderByDescending(kv => kv.Value).Take(TopDefs)
                .Select(kv => "{\"def\":" + M.Json(kv.Key) + ",\"n\":" + kv.Value + "}")) + "]";

        private static string PawnJson(Pawn p, string def)
        {
            string id = "?", job = null, driver = null, pos = null;
            try { id = p.ThingID; } catch { }
            try { var j = p.jobs?.curJob; job = j?.def?.defName; } catch { }
            try { driver = p.jobs?.curDriver?.GetType().FullName; } catch { }
            try { var c = p.Position; pos = c.x + "," + c.z; } catch { }
            return "{\"id\":" + M.Json(id) + ",\"def\":" + M.Json(def) + ",\"job\":" + M.Json(job) + ",\"driver\":" + M.Json(driver) +
                   ",\"pos\":" + M.Json(pos) + "}";
        }
    }
}
