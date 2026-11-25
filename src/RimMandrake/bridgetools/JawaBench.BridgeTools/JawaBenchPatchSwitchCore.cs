// The pure part of the patch switch: patch names, the choice of one patch, the refusals and the call counters.
// No Harmony and no Verse type here, so PatchSwitchSelfTest compiles it on plain .NET.
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Threading;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchPatchSwitchCore
    {
        internal const string OursPrefix = "mandrake.";
        internal static readonly string[] Kinds = { "prefix", "postfix", "transpiler", "finalizer" };

        // One Harmony patch as the host reads it from Harmony's patch info, or from the off store.
        internal sealed class Row
        {
            internal string Kind, PatchType, PatchMethod, OrigType, OrigMethod, OrigParams, Owner, Mod;
            internal int Priority, Index, Slots, Originals;
            internal string[] Before = new string[0], After = new string[0];
            internal bool Ours, SelfAssembly, Off;

            internal string Id => PatchId(Kind, PatchType, PatchMethod, OrigType, OrigMethod, OrigParams);
            internal string PatchName => PatchType + "." + PatchMethod;
        }

        internal static string PatchId(string kind, string patchType, string patchMethod, string origType, string origMethod, string origParams)
            => kind + ":" + patchType + "." + patchMethod + "@" + origType + "." + origMethod + "(" + origParams + ")";

        internal static string NormId(string id) => (id ?? "").Trim().ToLowerInvariant();

        internal static bool IsOurs(IEnumerable<string> packageIds)
            => packageIds != null && packageIds.Any(p => NormId(p).StartsWith(OursPrefix, StringComparison.Ordinal));

        // JawaBench's own Harmony ids are "mandrake.jawabench.*" and "jawabench.*"; its assembly is the other mark.
        internal static bool IsJawaBench(string owner, bool selfAssembly)
        {
            string o = NormId(owner);
            return selfAssembly || o == "jawabench" || o.StartsWith("jawabench.", StringComparison.Ordinal) ||
                   o == "mandrake.jawabench" || o.StartsWith("mandrake.jawabench.", StringComparison.Ordinal);
        }

        // Exact id first. Then "Type.Method", then a bare method name; each must name one patch.
        internal static Row Select(IList<Row> rows, string name, out string refusal)
        {
            refusal = null;
            string n = (name ?? "").Trim();
            if (n.Length == 0) { refusal = "UNKNOWN_PATCH: give patch= (an id from action=list)"; return null; }
            var exact = rows.Where(r => r.Id == n).ToList();
            if (exact.Count == 1) return exact[0];
            if (exact.Count > 1) { refusal = "AMBIGUOUS: " + exact.Count + " patches have the id " + n; return null; }
            var named = rows.Where(r => r.PatchName == n).ToList();
            if (named.Count == 0) named = rows.Where(r => r.PatchMethod == n).ToList();
            if (named.Count == 1) return named[0];
            if (named.Count > 1)
            {
                refusal = "AMBIGUOUS: " + n + " names " + named.Count + " patches; give one id: " +
                          string.Join(" | ", named.Select(r => r.Id).OrderBy(s => s, StringComparer.Ordinal));
                return null;
            }
            refusal = "UNKNOWN_PATCH: no Harmony patch is named " + n;
            return null;
        }

        // A patch method in two slots of one original goes out of every slot with one Unpatch; Harmony cannot take one alone.
        private static string Slots(Row r)
            => r.Slots > 1 ? "AMBIGUOUS: " + r.PatchName + " is in " + r.Slots + " slots of " + r.OrigType + "." + r.OrigMethod +
                             "; one Unpatch takes all of them off" : null;

        // The order of these refusals is the promise: a patch that is not ours is refused before the save is read.
        internal static string OffRefusal(Row r, Func<string> canonical)
        {
            if (r == null) return "UNKNOWN_PATCH";
            if (IsJawaBench(r.Owner, r.SelfAssembly)) return "JAWABENCH: " + r.PatchName + " is a JawaBench patch; the switch does not take off its own hooks";
            if (!r.Ours) return "NOT_OURS: " + r.PatchName + " is in " + (r.Mod ?? "an assembly of no running mod") + ", not in a mandrake.* mod";
            string slots = Slots(r);
            if (slots != null) return slots;
            string save = canonical?.Invoke();
            if (save != null) return save;
            if (r.Off) return "ALREADY_OFF: " + r.Id;
            return null;
        }

        internal static string OnRefusal(Row r)
        {
            if (r == null) return "UNKNOWN_PATCH";
            if (!r.Off) return "ALREADY_ON: " + r.Id;
            return null;
        }

        // A transpiler is no call: it runs once when Harmony builds the replacement, so a counter on it counts nothing.
        internal static string CountRefusal(Row r)
        {
            if (r == null) return "UNKNOWN_PATCH";
            if (r.Kind == "transpiler") return "TRANSPILER_NOT_COUNTABLE: " + r.Id + " is not called when the original runs";
            if (IsJawaBench(r.Owner, r.SelfAssembly)) return "JAWABENCH: the counters do not count JawaBench's own hooks";
            return null;
        }

        // Re-adding a patch gives it a new index, so it goes after the patches of its own priority. Say if the order moved.
        internal static bool OrderKept(IList<string> before, IList<string> after)
            => before != null && after != null && before.SequenceEqual(after, StringComparer.Ordinal);

        // Call counters. A key is a method handle (the host passes MethodHandle.Value), so the read and the hook
        // agree on the key even when Harmony hands the hook a different MethodBase object for the same method.
        // Interlocked, so any thread may count.
        internal sealed class Counters
        {
            private readonly ConcurrentDictionary<long, long[]> _calls = new ConcurrentDictionary<long, long[]>();
            private long _faults;

            internal void Arm(long key) => _calls.GetOrAdd(key, _ => new long[1]);
            internal bool Armed(long key) => _calls.ContainsKey(key);

            // Counts only an armed key, so a stray call from a method that was never armed adds no row.
            internal void Hit(long key)
            {
                if (_calls.TryGetValue(key, out long[] cell)) Interlocked.Increment(ref cell[0]);
            }

            // -1 means not armed: a counter that was never armed must not read as zero calls.
            internal long Read(long key) => _calls.TryGetValue(key, out long[] cell) ? Interlocked.Read(ref cell[0]) : -1;
            internal void Fault() => Interlocked.Increment(ref _faults);
            internal long Faults => Interlocked.Read(ref _faults);
        }
    }
}
