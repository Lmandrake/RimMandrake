// HOSE_INVALIDATION_REWIRE_EVENT_DRIVEN part (b) (design/RimMandrake/hose_wire_algorithms_advisory_2026-10-28.md §4 #5 b):
// RM_HoseLinks used to evaluate every reel's link ends (eligibility, drawbridge cut, relay, body port, free end) on every
// Refresh, i.e. on every liquid query tick: 200 reels' Ends() per call on map1 (live c3 DRY: Refresh max 168 ms, mean 0.23 ms,
// a fresh List copy and an RM_NetPort per free end each call). This is the per-reel memo that replaces that walk. Verse-free,
// so the net8 SelfTest drives it against a brute-force oracle.
//
// A slot (one reel, in the relay index's thing-id order) is re-evaluated only when
//   - the global fold changed (settings, relay version / signature, the net revision not caused by our own rebuild): all slots;
//   - its cheap per-reel key changed (carry, lay present, spawned, far cell, free-end role, the reel's end/port re-read
//     serial: CompHoseReel.linkInputSerial, bumped when a cached FreeEnd / Port re-read comes back different);
//   - a cached endpoint despawned (gone), or a thing the last read saw already despawned (down: it may respawn with
//     no event the key sees, and the old walk would link it again at once);
//   - its phased audit came due (once per AuditTicks window, phased by the reel's id like HoseLive.PhasedFresh): the
//     backstop for any input no event reaches. Its window is the reels' own 60-tick port / free-end cache window (same
//     interval, same phase), so the audit's re-read lands on the tick those caches go stale: no staleness is added.
// The links are rebuilt (in slot order, so link ids match the old full rebuild) only when some slot's (ok, inlet id, far id)
// changed: the same rule as the old 64-bit signature, kept per slot. The pre-Move RM_HoseLinks.Live check is untouched.
namespace RimMandrake.FlowWorks.Machinery
{
    internal sealed class RM_HoseLinkCache
    {
        /// <summary>Audit window: every slot is re-evaluated at least once per this many ticks.</summary>
        public const int AuditTicks = 60;

        private ulong[] keys = new ulong[0];
        private int[] evalAt = new int[0];
        private bool[] ok = new bool[0], down = new bool[0];
        private long[] inletId = new long[0], farId = new long[0], reelId = new long[0];
        private object[] inlet = new object[0], far = new object[0];
        private object[] watchA = new object[0], watchB = new object[0];
        private int count = -1;
        private ulong global;
        private bool any, resized;

        /// <summary>Slots evaluated / skipped since construction (the probe and the SelfTest read them).</summary>
        public long Evals, Skips;

        public int Count => count < 0 ? 0 : count;

        /// <summary>Start a refresh over <paramref name="n"/> slots under global fold <paramref name="g"/>. Returns true when
        /// every slot must be evaluated (first use, a new slot count, or a changed fold); the old results are then dropped.</summary>
        public bool Begin(int n, ulong g)
        {
            bool all = !any || n != count || g != global;
            if (n != count)
            {
                if (keys.Length < n)
                {
                    int cap = System.Math.Max(n, keys.Length * 2);
                    System.Array.Resize(ref keys, cap);
                    System.Array.Resize(ref evalAt, cap);
                    System.Array.Resize(ref ok, cap);
                    System.Array.Resize(ref down, cap);
                    System.Array.Resize(ref inletId, cap);
                    System.Array.Resize(ref farId, cap);
                    System.Array.Resize(ref reelId, cap);
                    System.Array.Resize(ref inlet, cap);
                    System.Array.Resize(ref far, cap);
                    System.Array.Resize(ref watchA, cap);
                    System.Array.Resize(ref watchB, cap);
                }
                for (int i = 0; i < keys.Length; i++) { ok[i] = down[i] = false; inlet[i] = far[i] = watchA[i] = watchB[i] = null; inletId[i] = farId[i] = reelId[i] = 0; }
                count = n;
                resized = true;
            }
            global = g;
            return all;
        }

        /// <summary>Must slot <paramref name="i"/> be evaluated now? <paramref name="phase"/> spreads the audit (the reel's id).</summary>
        public bool Due(bool all, int i, ulong key, bool gone, int now, int phase)
        {
            if (all || gone || down[i] || keys[i] != key || !Fresh(now, evalAt[i], phase)) return true;
            Skips++;
            return false;
        }

        /// <summary>The audit window rule: HoseLive.PhasedFresh with the reel's own port / free-end cache interval and phase, so
        /// a slot's audit comes due on the very tick those caches go stale (a re-read then happens inside the audit's Ends):
        /// the links see a port change exactly as early as the old every-tick walk did.</summary>
        public static bool Fresh(int now, int at, int phase) => RimMandrake.FlowWorks.Hose.HoseLive.PhasedFresh(now, at, AuditTicks, phase);

        /// <summary>Record slot i's evaluation. Returns true when its link identity changed (the links must be rebuilt). An
        /// unchanged identity keeps the old endpoint objects, as the old signature rule kept the old links. <paramref name="wa"/>
        /// and <paramref name="wb"/> are the raw things the evaluation read (the body port, the free end's port), kept whatever
        /// the result: the caller re-evaluates the slot when one of them despawns (<see cref="WatchA"/>). <paramref name="isDown"/>: one of them
        /// was already despawned when read; the slot then stays due on every refresh until a read sees none down.</summary>
        public bool Store(int i, ulong key, int now, long reel, bool isOk, object a, long aId, object b, long bId, object wa, object wb, bool isDown)
        {
            Evals++;
            keys[i] = key;
            evalAt[i] = now;
            watchA[i] = wa;
            watchB[i] = wb;
            down[i] = isDown;
            bool changed = !any || isOk != ok[i] || (isOk && (reel != reelId[i] || aId != inletId[i] || bId != farId[i]));
            if (changed)
            {
                ok[i] = isOk;
                inlet[i] = isOk ? a : null;
                far[i] = isOk ? b : null;
                inletId[i] = isOk ? aId : 0;
                farId[i] = isOk ? bId : 0;
                reelId[i] = isOk ? reel : 0;
            }
            return changed;
        }

        /// <summary>Close a refresh (after every Due slot was stored). Returns whether the links must be rebuilt: some Store
        /// reported a change (<paramref name="changed"/>) or the slot count changed (a reel's link may be gone).</summary>
        public bool End(bool changed)
        {
            bool rebuild = changed || resized || !any;
            any = true;
            resized = false;
            return rebuild;
        }

        public bool Ok(int i) => ok[i];
        public object Inlet(int i) => inlet[i];
        public object Far(int i) => far[i];
        public long InletId(int i) => inletId[i];
        public long FarId(int i) => farId[i];
        public object WatchA(int i) => watchA[i];
        public object WatchB(int i) => watchB[i];

        /// <summary>Forget everything: the next Begin evaluates every slot.</summary>
        public void Reset() { any = false; count = -1; resized = false; }

        /// <summary>FNV-style fold step for the keys.</summary>
        public static ulong Mix(ulong h, long v) => (h ^ (ulong)v) * 1099511628211UL;
    }
}
