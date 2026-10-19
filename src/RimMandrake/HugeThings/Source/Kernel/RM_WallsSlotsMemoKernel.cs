// HUGE_WALLS_FIX_DECIDER_RETRIES_FOREVER: Verse-free memos of the walls-and-slots decider. Offline-tested by
// SelfTest/WallsSlotsMemoFuzz.cs. Not thread-safe: callers lock where another thread reads (the held book).
using System;
using System.Collections.Generic;

namespace RimMandrake.HugeThings
{
    /// <summary>Per-creature cooldown for a destination the decider found unreachable and could not open: until it lapses the
    /// decider answers "no decision" without a reachability call, a pawnless path or a breach search. Rebuilt, never saved: a lost
    /// memo only costs one more decision. A tick that goes backwards (a load) clears it; a stamp from the far future never applies.</summary>
    public sealed class UnreachableMemo
    {
        public const int CooldownTicks = 600;
        public const int MaxEntries = 512;

        private struct Entry { public long dest; public int until; }
        private readonly Dictionary<int, Entry> map = new Dictionary<int, Entry>();
        private int lastNow = int.MinValue;

        public int Count => map.Count;

        public bool Blocked(int creature, long dest, int now)
        {
            return map.TryGetValue(creature, out Entry e) && e.dest == dest && e.until > now && e.until - now <= CooldownTicks;
        }

        public void Note(int creature, long dest, int now)
        {
            if (map.Count >= MaxEntries && !map.ContainsKey(creature))
            {
                Prune(now);
                if (map.Count >= MaxEntries) EvictOldest();
            }
            map[creature] = new Entry { dest = dest, until = now + CooldownTicks };
        }

        /// <summary>Call with the current tick before reading: a tick earlier than the last one seen is a load, so forget everything.</summary>
        public void Sync(int now)
        {
            if (now < lastNow) map.Clear();
            lastNow = now;
        }

        public void Prune(int now)
        {
            List<int> dead = null;
            foreach (KeyValuePair<int, Entry> kv in map)
                if (kv.Value.until <= now || kv.Value.until - now > CooldownTicks) (dead ?? (dead = new List<int>())).Add(kv.Key);
            if (dead != null) foreach (int k in dead) map.Remove(k);
        }

        public void Forget(int creature) => map.Remove(creature);

        private void EvictOldest()
        {
            int worst = 0, worstUntil = int.MaxValue;
            bool any = false;
            foreach (KeyValuePair<int, Entry> kv in map)
                if (!any || kv.Value.until < worstUntil) { worst = kv.Key; worstUntil = kv.Value.until; any = true; }
            if (any) map.Remove(worst);
        }
    }

    /// <summary>The crossings each creature holds at (cell indices, per map, with an expiry), kept bounded and pruned: expired,
    /// far-future (stale save), dead/despawned-creature and gone-map entries are dropped by Prune.</summary>
    public sealed class HeldBook
    {
        public const int MaxPerCreature = 8;
        public const int MaxCreatures = 256;

        private sealed class Entry { public int mapId; public int until; public int[] cells; }
        private readonly Dictionary<int, List<Entry>> byCreature = new Dictionary<int, List<Entry>>();

        public bool Any => byCreature.Count > 0;
        public int CreatureCount => byCreature.Count;
        public int Count { get { int n = 0; foreach (List<Entry> l in byCreature.Values) n += l.Count; return n; } }
        public int EntryCount(int creature) => byCreature.TryGetValue(creature, out List<Entry> l) ? l.Count : 0;
        public int EntryCountOnMap(int creature, int mapId)
        {
            int n = 0;
            if (byCreature.TryGetValue(creature, out List<Entry> l)) foreach (Entry e in l) if (e.mapId == mapId) n++;
            return n;
        }

        public void Add(int creature, int mapId, int now, int memoTicks, int[] cells)
        {
            if (cells == null || cells.Length == 0) return;
            if (!byCreature.TryGetValue(creature, out List<Entry> list))
            {
                if (byCreature.Count >= MaxCreatures) EvictOldestCreature();
                byCreature[creature] = list = new List<Entry>();
            }
            list.Add(new Entry { mapId = mapId, until = now + memoTicks, cells = cells });
            if (list.Count > MaxPerCreature) list.RemoveAt(0);
        }

        public void CellsFor(int creature, int mapId, int now, int memoTicks, List<int> into)
        {
            into.Clear();
            if (!byCreature.TryGetValue(creature, out List<Entry> list)) return;
            foreach (Entry e in list)
                if (e.mapId == mapId && e.until > now && e.until - now <= memoTicks) into.AddRange(e.cells);
        }

        /// <summary>Forget every held crossing on this map for which `hit` says one of its cell indices matters. Returns the
        /// creatures that lost one (null when none), so their other "this goal is closed" memos can be dropped too.</summary>
        public List<int> RemoveWhere(int mapId, Func<int[], bool> hit)
        {
            List<int> empty = null, touched = null;
            foreach (KeyValuePair<int, List<Entry>> kv in byCreature)
            {
                if (kv.Value.RemoveAll(e => e.mapId == mapId && hit(e.cells)) > 0) (touched ?? (touched = new List<int>())).Add(kv.Key);
                if (kv.Value.Count == 0) (empty ?? (empty = new List<int>())).Add(kv.Key);
            }
            if (empty != null) foreach (int k in empty) byCreature.Remove(k);
            return touched;
        }

        /// <summary>Drop expired and stale entries, entries of a creature that is no longer alive and spawned, and entries of a
        /// map that is gone. Returns how many entries were removed.</summary>
        public int Prune(int now, int memoTicks, Func<int, bool> creatureLive, Func<int, bool> mapLive)
        {
            int removed = 0;
            List<int> empty = null;
            foreach (KeyValuePair<int, List<Entry>> kv in byCreature)
            {
                if (!creatureLive(kv.Key)) { removed += kv.Value.Count; kv.Value.Clear(); }
                else removed += kv.Value.RemoveAll(e => e.until <= now || e.until - now > memoTicks || !mapLive(e.mapId));
                if (kv.Value.Count == 0) (empty ?? (empty = new List<int>())).Add(kv.Key);
            }
            if (empty != null) foreach (int k in empty) byCreature.Remove(k);
            return removed;
        }

        private void EvictOldestCreature()
        {
            int worst = 0, worstUntil = int.MaxValue;
            bool any = false;
            foreach (KeyValuePair<int, List<Entry>> kv in byCreature)
            {
                int u = int.MinValue;
                foreach (Entry e in kv.Value) if (e.until > u) u = e.until;
                if (!any || u < worstUntil) { worst = kv.Key; worstUntil = u; any = true; }
            }
            if (any) byCreature.Remove(worst);
        }
    }
}
