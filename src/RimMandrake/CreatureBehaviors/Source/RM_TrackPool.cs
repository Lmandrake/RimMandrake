using System;
using System.Collections.Generic;
using System.IO;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // FOOTPRINT_TRACK_GRID_1 — the footprint store, pure C#.
    //
    // Deliberately System-only (no Verse, no Unity) so the offline selftest
    // (Source/SelfTestTracks) compiles THIS file and tests the real rules:
    // the cap, eviction order, overwrite, clears, the downwind sweep order
    // and the packed save format. RM_MapComponent_TrackGrid is the only live
    // owner; it adds the map, the pawn and the draw.
    //
    // One record per cell: direction (3 bits), size class (2), source class
    // (2), a drag bit, the tick it was laid, and a style index (which sprite
    // and draw size, resolved by the component). A fixed-capacity pool with a
    // cell -> slot index. No Thing is ever spawned for a print.
    //
    // Eviction when full (ruled at the GPT card): by priority, then age —
    //   tier 0  small animals (source Animal, size Small)      go first
    //   tier 1  everything else that is not protected          then oldest
    //   tier 2  humanlikes and large animals (bs >= 1.5)       kept; only
    //           when nothing else is left does the OLDEST of these go, so
    //           RECENT humanlike and large prints are what survive.
    // Re-stepping a cell overwrites its record (the newest walker's print is
    // on top) and makes it the newest.
    // ════════════════════════════════════════════════════════════════════
    public enum RM_TrackSource : byte { Animal = 0, Humanlike = 1, Mechanoid = 2, Other = 3 }

    public enum RM_TrackSize : byte { Small = 0, Medium = 1, Large = 2, Huge = 3 }

    public struct RM_TrackRecord
    {
        public int cell;
        public int tick;
        public byte bits;
        public ushort style;

        public int Direction => bits & 0x7;
        public RM_TrackSize Size => (RM_TrackSize)((bits >> 3) & 0x3);
        public RM_TrackSource Source => (RM_TrackSource)((bits >> 5) & 0x3);
        public bool Drag => (bits & 0x80) != 0;
        /// <summary>Compass degrees the walker was heading (0 = north, 90 = east).</summary>
        public float Angle => Direction * 45f;
        /// <summary>The walker was invisible (HediffComp_Invisibility) when it laid this print.
        /// Carried in the style's top bit, so the save format is unchanged.</summary>
        public bool Invisible => (style & RM_TrackPool.InvisibleFlag) != 0;
        /// <summary>The style table index with the invisible flag masked off.</summary>
        public int StyleIndex => style & RM_TrackPool.StyleMask;
    }

    public sealed class RM_TrackPool
    {
        public const int DefaultCapacity = 6000;
        public const float LargeBodySize = 1.5f;
        /// <summary>Top bit of a record's style: laid by an invisible walker. Never affects eviction.</summary>
        public const ushort InvisibleFlag = 0x8000;
        public const ushort StyleMask = 0x7FFF;

        public static ushort PackStyle(int styleIndex, bool invisible)
        {
            return (ushort)((styleIndex & StyleMask) | (invisible ? InvisibleFlag : 0));
        }
        private const int FormatVersion = 1;
        private const int TierCount = 3;

        private readonly int width;
        private readonly int height;
        private int capacity;

        private readonly int[] cellToSlot;
        private int[] slotCell;
        private int[] slotTick;
        private byte[] slotBits;
        private ushort[] slotStyle;
        private long[] slotSeq;
        private int[] slotGen;
        private int[] freeSlots;
        private int freeCount;
        private int count;
        private int invisibleCount;
        private long nextSeq;

        // Per tier, (slot, gen) packed into a long, oldest first. Overwrites and
        // clears leave stale entries behind; they are skipped on pop and the
        // queues are rebuilt when stale entries outnumber live ones.
        private readonly Queue<long>[] tiers = new Queue<long>[TierCount];

        public RM_TrackPool(int width, int height, int capacity)
        {
            if (width <= 0 || height <= 0) throw new ArgumentException("map size must be positive");
            this.width = width;
            this.height = height;
            cellToSlot = new int[width * height];
            for (int i = 0; i < cellToSlot.Length; i++) cellToSlot[i] = -1;
            for (int t = 0; t < TierCount; t++) tiers[t] = new Queue<long>();
            Allocate(Math.Max(1, capacity));
        }

        public int Width => width;
        public int Height => height;
        public int Capacity => capacity;
        public int Count => count;
        /// <summary>Live records flagged invisible, kept incrementally (CountInvisible is the scan that checks it).</summary>
        public int InvisibleCount => invisibleCount;

        /// <summary>Total queued eviction entries, stale ones included. Bounded; the selftest reads it.</summary>
        public int QueuedEntries
        {
            get
            {
                int n = 0;
                for (int t = 0; t < TierCount; t++) n += tiers[t].Count;
                return n;
            }
        }

        // ── classification (pure, so the selftest covers it) ─────────────

        public static byte PackBits(int direction, RM_TrackSize size, RM_TrackSource source, bool drag)
        {
            return (byte)((direction & 0x7) | (((int)size & 0x3) << 3) | (((int)source & 0x3) << 5) | (drag ? 0x80 : 0));
        }

        /// <summary>Compass degrees (0 = north, clockwise) to one of eight directions.</summary>
        public static int QuantizeDirection(float compassDegrees)
        {
            double d = compassDegrees % 360.0;
            if (d < 0) d += 360.0;
            return (int)Math.Round(d / 45.0) & 0x7;
        }

        public static RM_TrackSize SizeClassFor(float bodySize)
        {
            if (bodySize < 0.65f) return RM_TrackSize.Small;
            if (bodySize < LargeBodySize) return RM_TrackSize.Medium;
            if (bodySize < 3f) return RM_TrackSize.Large;
            return RM_TrackSize.Huge;
        }

        /// <summary>
        /// The whole classification a pawn step goes through. There is NO visibility
        /// input by construction: an invisible pawn is classified exactly like a seen
        /// one (turn-4 ruling, "unseen things leave prints").
        /// </summary>
        public static byte Classify(bool humanlike, bool mechanoid, bool animal, float bodySize, bool crawling, float compassDegrees)
        {
            RM_TrackSource src = humanlike ? RM_TrackSource.Humanlike
                : mechanoid ? RM_TrackSource.Mechanoid
                : animal ? RM_TrackSource.Animal
                : RM_TrackSource.Other;
            return PackBits(QuantizeDirection(compassDegrees), SizeClassFor(bodySize), src, crawling);
        }

        public static int TierOf(byte bits)
        {
            var size = (RM_TrackSize)((bits >> 3) & 0x3);
            var src = (RM_TrackSource)((bits >> 5) & 0x3);
            if (src == RM_TrackSource.Humanlike || size >= RM_TrackSize.Large) return 2;
            if (src == RM_TrackSource.Animal && size == RM_TrackSize.Small) return 0;
            return 1;
        }

        // ── reads ────────────────────────────────────────────────────────

        public int CellIndex(int x, int z) => z * width + x;

        public bool InBounds(int x, int z) => x >= 0 && z >= 0 && x < width && z < height;

        public bool Has(int cellIndex) => cellToSlot[cellIndex] >= 0;

        public bool TryGet(int cellIndex, out RM_TrackRecord rec)
        {
            int s = cellToSlot[cellIndex];
            if (s < 0)
            {
                rec = default(RM_TrackRecord);
                return false;
            }
            rec = new RM_TrackRecord { cell = slotCell[s], tick = slotTick[s], bits = slotBits[s], style = slotStyle[s] };
            return true;
        }

        public int CountTier(int tier)
        {
            int n = 0;
            for (int i = 0; i < cellToSlot.Length; i++)
            {
                int s = cellToSlot[i];
                if (s >= 0 && TierOf(slotBits[s]) == tier) n++;
            }
            return n;
        }

        public int CountInvisible()
        {
            int n = 0;
            for (int i = 0; i < cellToSlot.Length; i++)
            {
                int s = cellToSlot[i];
                if (s >= 0 && (slotStyle[s] & InvisibleFlag) != 0) n++;
            }
            return n;
        }

        // ── writes ───────────────────────────────────────────────────────

        /// <summary>Lay a print. Returns the cell index whose print was evicted to make room, or -1.</summary>
        public int Write(int cellIndex, int tick, byte bits, ushort style)
        {
            int evictedCell = -1;
            int s = cellToSlot[cellIndex];
            if (s < 0)
            {
                if (count >= capacity) evictedCell = EvictOne();
                s = freeSlots[--freeCount];
                cellToSlot[cellIndex] = s;
                slotCell[s] = cellIndex;
                count++;
            }
            else if ((slotStyle[s] & InvisibleFlag) != 0)
            {
                invisibleCount--;   // overwriting a flagged record
            }
            slotGen[s]++;
            slotTick[s] = tick;
            slotBits[s] = bits;
            slotStyle[s] = style;
            if ((style & InvisibleFlag) != 0) invisibleCount++;
            slotSeq[s] = nextSeq++;
            tiers[TierOf(bits)].Enqueue(Pack(s, slotGen[s]));
            CompactIfBloated();
            return evictedCell;
        }

        public bool Clear(int cellIndex)
        {
            int s = cellToSlot[cellIndex];
            if (s < 0) return false;
            Free(s);
            return true;
        }

        /// <summary>Clears every print in the inclusive rect (clipped to the map). Calls onCleared per cleared cell.</summary>
        public int ClearRect(int minX, int minZ, int maxX, int maxZ, Action<int> onCleared = null)
        {
            minX = Math.Max(0, minX); minZ = Math.Max(0, minZ);
            maxX = Math.Min(width - 1, maxX); maxZ = Math.Min(height - 1, maxZ);
            int n = 0;
            for (int z = minZ; z <= maxZ; z++)
            {
                for (int x = minX; x <= maxX; x++)
                {
                    int c = z * width + x;
                    if (Clear(c))
                    {
                        n++;
                        onCleared?.Invoke(c);
                    }
                }
            }
            return n;
        }

        public void ClearAll()
        {
            for (int i = 0; i < cellToSlot.Length; i++)
            {
                if (cellToSlot[i] >= 0) Free(cellToSlot[i]);
            }
            for (int t = 0; t < TierCount; t++) tiers[t].Clear();
        }

        /// <summary>Change the cap. Shrinking evicts by the normal rule (priority, then age).</summary>
        public void Resize(int newCapacity)
        {
            newCapacity = Math.Max(1, newCapacity);
            if (newCapacity == capacity) return;
            List<RM_TrackRecord> live = RecordsOldestFirst();
            ClearAll();
            Allocate(newCapacity);
            foreach (RM_TrackRecord r in live) Write(r.cell, r.tick, r.bits, r.style);
        }

        // ── the downwind sweep ───────────────────────────────────────────

        /// <summary>
        /// Every map cell, ordered from the upwind edge to the downwind edge for a wind
        /// blowing TOWARD <paramref name="windTowardDegrees"/> (compass: 0 = north,
        /// 90 = east). Ties break on cell index, so the order is deterministic.
        /// </summary>
        public static int[] SweepOrder(int width, int height, float windTowardDegrees)
        {
            double rad = windTowardDegrees * Math.PI / 180.0;
            double dx = Math.Sin(rad), dz = Math.Cos(rad);
            int n = width * height;
            var keys = new double[n];
            var cells = new int[n];
            for (int z = 0; z < height; z++)
            {
                for (int x = 0; x < width; x++)
                {
                    int c = z * width + x;
                    cells[c] = c;
                    // Rounded so float noise never reorders a straight front.
                    keys[c] = Math.Round(x * dx + z * dz, 6);
                }
            }
            Array.Sort(keys, cells);
            // Array.Sort is not stable: restore cell-index order inside equal keys.
            int i = 0;
            while (i < n)
            {
                int j = i + 1;
                while (j < n && keys[j] == keys[i]) j++;
                if (j - i > 1) Array.Sort(cells, i, j - i);
                i = j;
            }
            return cells;
        }

        // ── save format ──────────────────────────────────────────────────

        /// <summary>
        /// Packed save: header (version, width, height, capacity, count), then each live
        /// record oldest first: cell, tick, bits, style. Load replays them through
        /// Write in that order, so save -> load -> save is byte-identical.
        /// </summary>
        public byte[] ToBytes()
        {
            List<RM_TrackRecord> live = RecordsOldestFirst();
            using (var ms = new MemoryStream(20 + live.Count * 11))
            using (var w = new BinaryWriter(ms))
            {
                w.Write(FormatVersion);
                w.Write(width);
                w.Write(height);
                w.Write(capacity);
                w.Write(live.Count);
                foreach (RM_TrackRecord r in live)
                {
                    w.Write(r.cell);
                    w.Write(r.tick);
                    w.Write(r.bits);
                    w.Write(r.style);
                }
                w.Flush();
                return ms.ToArray();
            }
        }

        /// <summary>
        /// Rebuilds a pool from <see cref="ToBytes"/>. Returns null (and a reason) if the
        /// bytes are for another map size or format — the caller starts empty, never crashes.
        /// <paramref name="capacityOverride"/> &gt; 0 applies the current setting.
        /// </summary>
        public static RM_TrackPool FromBytes(byte[] data, int width, int height, int capacityOverride, out string error)
        {
            error = null;
            if (data == null || data.Length < 20)
            {
                error = "no track data";
                return null;
            }
            using (var ms = new MemoryStream(data))
            using (var r = new BinaryReader(ms))
            {
                int version = r.ReadInt32();
                int w = r.ReadInt32();
                int h = r.ReadInt32();
                int cap = r.ReadInt32();
                int n = r.ReadInt32();
                if (version != FormatVersion) { error = "unknown track format " + version; return null; }
                if (w != width || h != height) { error = "track data is for a " + w + "x" + h + " map"; return null; }
                if (n < 0 || ms.Length - ms.Position < (long)n * 11) { error = "track data truncated"; return null; }
                var pool = new RM_TrackPool(width, height, capacityOverride > 0 ? capacityOverride : cap);
                int cells = width * height;
                for (int i = 0; i < n; i++)
                {
                    int cell = r.ReadInt32();
                    int tick = r.ReadInt32();
                    byte bits = r.ReadByte();
                    ushort style = r.ReadUInt16();
                    if (cell < 0 || cell >= cells) continue;
                    pool.Write(cell, tick, bits, style);
                }
                return pool;
            }
        }

        public List<RM_TrackRecord> RecordsOldestFirst()
        {
            var slots = new List<int>(count);
            for (int i = 0; i < cellToSlot.Length; i++)
            {
                if (cellToSlot[i] >= 0) slots.Add(cellToSlot[i]);
            }
            slots.Sort((a, b) => slotSeq[a].CompareTo(slotSeq[b]));
            var list = new List<RM_TrackRecord>(slots.Count);
            foreach (int s in slots)
            {
                list.Add(new RM_TrackRecord { cell = slotCell[s], tick = slotTick[s], bits = slotBits[s], style = slotStyle[s] });
            }
            return list;
        }

        // ── internals ────────────────────────────────────────────────────

        private void Allocate(int cap)
        {
            capacity = cap;
            slotCell = new int[cap];
            slotTick = new int[cap];
            slotBits = new byte[cap];
            slotStyle = new ushort[cap];
            slotSeq = new long[cap];
            slotGen = new int[cap];
            freeSlots = new int[cap];
            freeCount = cap;
            invisibleCount = 0;
            // Hand out low slots first.
            for (int i = 0; i < cap; i++) freeSlots[i] = cap - 1 - i;
            count = 0;
            for (int t = 0; t < TierCount; t++) tiers[t].Clear();
        }

        private static long Pack(int slot, int gen) => ((long)slot << 32) | (uint)gen;

        private void Free(int s)
        {
            if ((slotStyle[s] & InvisibleFlag) != 0) invisibleCount--;
            slotStyle[s] = 0;
            cellToSlot[slotCell[s]] = -1;
            slotGen[s]++;
            freeSlots[freeCount++] = s;
            count--;
        }

        private int EvictOne()
        {
            for (int t = 0; t < TierCount; t++)
            {
                Queue<long> q = tiers[t];
                while (q.Count > 0)
                {
                    long e = q.Dequeue();
                    int s = (int)(e >> 32);
                    int gen = (int)(e & 0xFFFFFFFF);
                    if (slotGen[s] != gen || cellToSlot[slotCell[s]] != s) continue;
                    int cell = slotCell[s];
                    Free(s);
                    return cell;
                }
            }
            // Unreachable while every live slot has a queue entry; recover anyway.
            RebuildQueues();
            for (int i = 0; i < cellToSlot.Length; i++)
            {
                if (cellToSlot[i] >= 0)
                {
                    Free(cellToSlot[i]);
                    return i;
                }
            }
            return -1;
        }

        private void CompactIfBloated()
        {
            if (QueuedEntries > 2 * capacity + 64) RebuildQueues();
        }

        private void RebuildQueues()
        {
            for (int t = 0; t < TierCount; t++) tiers[t].Clear();
            var slots = new List<int>(count);
            for (int i = 0; i < cellToSlot.Length; i++)
            {
                if (cellToSlot[i] >= 0) slots.Add(cellToSlot[i]);
            }
            slots.Sort((a, b) => slotSeq[a].CompareTo(slotSeq[b]));
            foreach (int s in slots) tiers[TierOf(slotBits[s])].Enqueue(Pack(s, slotGen[s]));
        }
    }
}
