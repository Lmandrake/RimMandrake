// Verse-free kernel of how Huge Things turns many plants' desired footprints into real blocker cells safely (GPT review
// 2026-10-07, #1 #2 #5 #6 #8 #9 #16; owner ruling 2026-10-07 20:38 on #4). SelfTest/HugeThingsFuzz.cs compiles this file:
// no Verse/RimWorld/UnityEngine. Cells are RM_HugeFootprintKernel.Key(x, z) longs.
//   ClaimLedger      multi-owner cell claims: a cell is blocked while ANY owner claims it; one physical blocker per cell;
//                    the result never depends on the order owners registered or refreshed in.
//   Planner          which claimed-but-open cells may close NOW: never a cell holding a pawn or an item (so nothing is ever
//                    moved aside or destroyed), never a protected cell (buildings, blueprints, frames, their interaction cells,
//                    door approaches, trees, other giants, unwalkable ground), and never one whose closing would cut a
//                    passable cell off from the window's border (no trapped pawns, no new pockets) or cut a giant's root off
//                    from every open 4-neighbour (it must stay cuttable). A refused cell is deferred, not dropped.
//   FootprintSignature  everything the geometry depends on, compared field by field (the selection/refresh cache key).
//   DamageDedup      one forwarded hit per (tick, source, owner): a beam or blast crossing several cells of one giant hits it once.
using System;
using System.Collections.Generic;

namespace RimMandrake.HugeThings
{
    public sealed class ClaimLedger
    {
        private readonly Dictionary<long, SortedSet<int>> cellOwners = new Dictionary<long, SortedSet<int>>();
        private readonly Dictionary<int, HashSet<long>> ownerCells = new Dictionary<int, HashSet<long>>();

        public bool IsClaimed(long cell) => cellOwners.ContainsKey(cell);

        public int ClaimedCount => cellOwners.Count;

        /// <summary>The owner a cell answers to (labels, damage): the lowest id among its claimants, or -1.</summary>
        public int PrimaryOwner(long cell) => cellOwners.TryGetValue(cell, out SortedSet<int> o) && o.Count > 0 ? o.Min : -1;

        public IEnumerable<long> Claimed => cellOwners.Keys;

        public IEnumerable<long> CellsOf(int owner)
        {
            if (ownerCells.TryGetValue(owner, out HashSet<long> c)) return c;
            return Array.Empty<long>();
        }

        /// <summary>Replace an owner's claims. becameClaimed: cells nobody claimed before; becameFree: cells nobody claims now.</summary>
        public void Set(int owner, IEnumerable<long> cells, List<long> becameClaimed, List<long> becameFree)
        {
            HashSet<long> want = new HashSet<long>(cells);
            if (!ownerCells.TryGetValue(owner, out HashSet<long> had))
            {
                had = new HashSet<long>();
                ownerCells[owner] = had;
            }
            List<long> drop = new List<long>();
            foreach (long c in had) if (!want.Contains(c)) drop.Add(c);
            drop.Sort();
            foreach (long c in drop)
            {
                had.Remove(c);
                SortedSet<int> o = cellOwners[c];
                o.Remove(owner);
                if (o.Count == 0)
                {
                    cellOwners.Remove(c);
                    becameFree?.Add(c);
                }
            }
            List<long> add = new List<long>();
            foreach (long c in want) if (!had.Contains(c)) add.Add(c);
            add.Sort();
            foreach (long c in add)
            {
                had.Add(c);
                if (!cellOwners.TryGetValue(c, out SortedSet<int> o))
                {
                    o = new SortedSet<int>();
                    cellOwners[c] = o;
                    becameClaimed?.Add(c);
                }
                o.Add(owner);
            }
            if (had.Count == 0) ownerCells.Remove(owner);
        }

        public void Remove(int owner, List<long> becameFree) => Set(owner, Array.Empty<long>(), null, becameFree);
    }

    [Flags]
    public enum CellFlags
    {
        None = 0,
        Passable = 1,     // a pawn can walk here now (vanilla Walkable, which is false under any impassable edifice)
        Pawn = 2,
        Item = 4,
        Protected = 8,    // building/blueprint/frame/interaction cell/door approach/tree/other giant/indestructible/bad ground
    }

    public static class Planner
    {
        public const int Margin = 4;

        /// <summary>The planning window for a plant: every cell it could claim (its whole footprint, realized or not) and
        /// its root, grown by Margin. It must NOT depend on which cells happen to be open yet, or a later pass would judge
        /// reachability against a nearer border than an earlier one did (measured: 134/3000 fuzz cases closed cells on a
        /// second pass that the first had refused).</summary>
        public static CellBox Window(IEnumerable<long> footprint, long root)
        {
            int minX = RM_HugeFootprintKernel.KeyX(root), minZ = RM_HugeFootprintKernel.KeyZ(root), maxX = minX, maxZ = minZ;
            foreach (long k in footprint)
            {
                int x = RM_HugeFootprintKernel.KeyX(k), z = RM_HugeFootprintKernel.KeyZ(k);
                if (x < minX) minX = x;
                if (z < minZ) minZ = z;
                if (x > maxX) maxX = x;
                if (z > maxZ) maxZ = z;
            }
            return new CellBox(minX - Margin, minZ - Margin, maxX + Margin, maxZ + Margin);
        }

        /// <summary>
        /// Decide which of `wanted` (claimed, not yet blocked) may close now, in a deterministic order. flagsAt answers for
        /// any cell; roots are giants' own cells that must keep an open 4-neighbour reachable from the window border if
        /// they have one now. The window's border stands for "the rest of the map"; a pocket larger than the window is not
        /// seen (see REWORK.md, Needs owner). Cells of `wanted` outside the window are refused.
        /// </summary>
        public static List<long> Plan(IList<long> wanted, IList<long> roots, Func<long, CellFlags> flagsAt, CellBox window)
        {
            List<long> accepted = new List<long>();
            if (wanted == null || wanted.Count == 0) return accepted;
            int minX = window.MinX, minZ = window.MinZ, maxX = window.MaxX, maxZ = window.MaxZ;
            int w = maxX - minX + 1, h = maxZ - minZ + 1;
            bool[] pass = new bool[w * h];
            for (int z = 0; z < h; z++)
                for (int x = 0; x < w; x++)
                    pass[z * w + x] = (flagsAt(RM_HugeFootprintKernel.Key(minX + x, minZ + z)) & CellFlags.Passable) != 0;

            bool[] before = Reach(pass, w, h);
            List<int> rootIdx = new List<int>();
            if (roots != null)
            {
                foreach (long k in roots)
                {
                    if (!window.Contains(RM_HugeFootprintKernel.KeyX(k), RM_HugeFootprintKernel.KeyZ(k))) continue;
                    int i = (RM_HugeFootprintKernel.KeyZ(k) - minZ) * w + (RM_HugeFootprintKernel.KeyX(k) - minX);
                    if (RootServed(i, pass, before, w, h)) rootIdx.Add(i);   // only roots that have access now must keep it
                }
            }

            List<long> order = new List<long>(new HashSet<long>(wanted));
            order.Sort((a, b) =>
            {
                int za = RM_HugeFootprintKernel.KeyZ(a), zb = RM_HugeFootprintKernel.KeyZ(b);
                if (za != zb) return za.CompareTo(zb);
                return RM_HugeFootprintKernel.KeyX(a).CompareTo(RM_HugeFootprintKernel.KeyX(b));
            });
            // Repeat to a fixpoint: a cell refused because closing it would cut off a neighbour becomes acceptable once that
            // neighbour itself closes later in the pass (measured: without this a second pass closed more, 132/3000 cases).
            bool progress = true;
            while (progress)
            {
                progress = false;
                for (int n = 0; n < order.Count; n++)
                {
                    long k = order[n];
                    CellFlags f = flagsAt(k);
                    if (!window.Contains(RM_HugeFootprintKernel.KeyX(k), RM_HugeFootprintKernel.KeyZ(k))) continue;
                    if ((f & CellFlags.Passable) == 0 || (f & (CellFlags.Pawn | CellFlags.Item | CellFlags.Protected)) != 0) continue;
                    int i = (RM_HugeFootprintKernel.KeyZ(k) - minZ) * w + (RM_HugeFootprintKernel.KeyX(k) - minX);
                    if (rootIdx.Contains(i) || !pass[i]) continue;
                    pass[i] = false;
                    bool[] after = Reach(pass, w, h);
                    bool ok = true;
                    for (int j = 0; j < pass.Length && ok; j++)
                    {
                        if (pass[j] && before[j] && !after[j]) ok = false;     // a cell that reached the border no longer does
                    }
                    for (int r = 0; r < rootIdx.Count && ok; r++)
                    {
                        if (!RootServed(rootIdx[r], pass, after, w, h)) ok = false;
                    }
                    if (ok)
                    {
                        accepted.Add(k);
                        before = after;
                        progress = true;
                    }
                    else
                    {
                        pass[i] = true;
                    }
                }
            }
            accepted.Sort((a, b) =>
            {
                int za = RM_HugeFootprintKernel.KeyZ(a), zb = RM_HugeFootprintKernel.KeyZ(b);
                return za != zb ? za.CompareTo(zb) : RM_HugeFootprintKernel.KeyX(a).CompareTo(RM_HugeFootprintKernel.KeyX(b));
            });
            return accepted;
        }

        private static bool RootServed(int i, bool[] pass, bool[] reach, int w, int h)
        {
            int x = i % w, z = i / w;
            int[] dx = { 1, -1, 0, 0 }, dz = { 0, 0, 1, -1 };
            for (int d = 0; d < 4; d++)
            {
                int nx = x + dx[d], nz = z + dz[d];
                if (nx < 0 || nz < 0 || nx >= w || nz >= h) return true;   // touches the border: reachable from outside
                int j = nz * w + nx;
                if (pass[j] && reach[j]) return true;
            }
            return false;
        }

        /// <summary>4-connected flood from every passable border cell.</summary>
        public static bool[] Reach(bool[] pass, int w, int h)
        {
            bool[] seen = new bool[pass.Length];
            Stack<int> st = new Stack<int>();
            for (int x = 0; x < w; x++)
            {
                Seed(x, pass, seen, st);
                Seed((h - 1) * w + x, pass, seen, st);
            }
            for (int z = 0; z < h; z++)
            {
                Seed(z * w, pass, seen, st);
                Seed(z * w + w - 1, pass, seen, st);
            }
            while (st.Count > 0)
            {
                int i = st.Pop();
                int x = i % w, z = i / w;
                if (x > 0) Seed(i - 1, pass, seen, st);
                if (x < w - 1) Seed(i + 1, pass, seen, st);
                if (z > 0) Seed(i - w, pass, seen, st);
                if (z < h - 1) Seed(i + w, pass, seen, st);
            }
            return seen;
        }

        private static void Seed(int i, bool[] pass, bool[] seen, Stack<int> st)
        {
            if (pass[i] && !seen[i])
            {
                seen[i] = true;
                st.Push(i);
            }
        }
    }

    /// <summary>
    /// Owner ruling 2026-10-07 21:08 (decision taken by question card): a footprint cell held only by items closes after its
    /// items are pushed, gently, to the nearest free valid cell that is in NO footprint (claimed by any plant); pawns are
    /// never moved. Every item of a cell must fit or none moves (the cell then stays open). Capacity is shared across the
    /// whole pass so two cells never overfill one destination. Search is a 4-connected BFS over cells with capacity >= 0
    /// (passable ground), preferred cells first at each distance, then key order: deterministic.
    /// </summary>
    public static class ItemMover
    {
        public const int MaxRadius = 12;

        /// <summary>
        /// For each source cell (in key order) with itemCounts[cell] items, a destination per item, or no entry when they
        /// do not all fit. capacity(k): how many more items cell k takes (-1 = not a valid cell at all). excluded(k): in some
        /// footprint. preferred(src, k): e.g. the same stockpile as the source.
        /// </summary>
        public static Dictionary<long, List<long>> Assign(IDictionary<long, int> itemCounts, Func<long, int> capacity,
                                                          Func<long, bool> excluded, Func<long, long, bool> preferred)
        {
            Dictionary<long, List<long>> outMoves = new Dictionary<long, List<long>>();
            Dictionary<long, int> used = new Dictionary<long, int>();
            List<long> srcs = new List<long>(itemCounts.Keys);
            srcs.Sort();
            foreach (long src in srcs)
            {
                int need = itemCounts[src];
                if (need <= 0) continue;
                List<long> dests = new List<long>();
                Dictionary<long, int> take = new Dictionary<long, int>();
                foreach (long k in Ring(src, capacity, preferred))
                {
                    if (k == src || excluded(k)) continue;
                    int cap = capacity(k) - (used.TryGetValue(k, out int u) ? u : 0) - (take.TryGetValue(k, out int t) ? t : 0);
                    while (cap > 0 && dests.Count < need)
                    {
                        dests.Add(k);
                        take[k] = (take.TryGetValue(k, out int t2) ? t2 : 0) + 1;
                        cap--;
                    }
                    if (dests.Count == need) break;
                }
                if (dests.Count < need) continue;
                foreach (KeyValuePair<long, int> kv in take) used[kv.Key] = (used.TryGetValue(kv.Key, out int u2) ? u2 : 0) + kv.Value;
                outMoves[src] = dests;
            }
            return outMoves;
        }

        /// <summary>Cells reachable from src over capacity >= 0 ground, nearest first (BFS layers), preferred first within a
        /// layer, then by key.</summary>
        private static IEnumerable<long> Ring(long src, Func<long, int> capacity, Func<long, long, bool> preferred)
        {
            HashSet<long> seen = new HashSet<long> { src };
            List<long> layer = new List<long> { src };
            for (int d = 0; d < MaxRadius && layer.Count > 0; d++)
            {
                List<long> next = new List<long>();
                foreach (long k in layer)
                {
                    int x = RM_HugeFootprintKernel.KeyX(k), z = RM_HugeFootprintKernel.KeyZ(k);
                    long[] ns = { RM_HugeFootprintKernel.Key(x + 1, z), RM_HugeFootprintKernel.Key(x - 1, z),
                                  RM_HugeFootprintKernel.Key(x, z + 1), RM_HugeFootprintKernel.Key(x, z - 1) };
                    foreach (long n in ns)
                    {
                        if (seen.Add(n) && capacity(n) >= 0) next.Add(n);
                    }
                }
                next.Sort((a, b) =>
                {
                    bool pa = preferred != null && preferred(src, a), pb = preferred != null && preferred(src, b);
                    if (pa != pb) return pa ? -1 : 1;
                    return a.CompareTo(b);
                });
                foreach (long k in next) yield return k;
                layer = next;
            }
        }
    }

    public static class RootRule
    {
        /// <summary>Owner ruling 2026-10-07 21:08: a huge plant whose every measured picture touches the ground only in its
        /// own cell makes that cell impassable (the plant itself), so it is still solid somewhere. Generic, never per species.
        /// </summary>
        public static bool RootImpassable(bool blockingEnabled, bool blockingSupported, IList<int> contactCountsPerVariant)
        {
            if (!blockingEnabled || !blockingSupported || contactCountsPerVariant == null || contactCountsPerVariant.Count == 0) return false;
            for (int i = 0; i < contactCountsPerVariant.Count; i++) if (contactCountsPerVariant[i] != 0) return false;
            return true;
        }
    }

    /// <summary>Everything a plant's footprint depends on. Two equal signatures give equal footprints and selection rects.</summary>
    public struct FootprintSignature : IEquatable<FootprintSignature>
    {
        public int RootX, RootZ, MaskId;
        public float DrawX, Visual, JitterX, JitterZ, BlockScale;
        public bool Flip, Measured, Blocking, Selecting, OldEnough;

        public bool Equals(FootprintSignature o)
            => RootX == o.RootX && RootZ == o.RootZ && MaskId == o.MaskId && DrawX == o.DrawX && Visual == o.Visual
            && JitterX == o.JitterX && JitterZ == o.JitterZ && BlockScale == o.BlockScale && Flip == o.Flip
            && Measured == o.Measured && Blocking == o.Blocking && Selecting == o.Selecting && OldEnough == o.OldEnough;

        public override bool Equals(object obj) => obj is FootprintSignature o && Equals(o);

        public override int GetHashCode()
        {
            unchecked
            {
                int h = RootX * 73856093 ^ RootZ * 19349663 ^ MaskId * 83492791;
                h = h * 31 + Visual.GetHashCode();
                h = h * 31 + BlockScale.GetHashCode();
                return h * 31 + (Flip ? 1 : 0) + (Blocking ? 2 : 0) + (Selecting ? 4 : 0) + (OldEnough ? 8 : 0) + (Measured ? 16 : 0);
            }
        }
    }

    /// <summary>One-entry cache keyed on a full signature.</summary>
    public sealed class SignatureCache<T>
    {
        private bool has;
        private FootprintSignature key;
        private T value;

        public T Get(FootprintSignature sig, Func<FootprintSignature, T> compute)
        {
            if (has && key.Equals(sig)) return value;
            value = compute(sig);
            key = sig;
            has = true;
            return value;
        }

        public void Clear() => has = false;
    }

    /// <summary>One forwarded hit per (tick, source, owner).</summary>
    public sealed class DamageDedup
    {
        private int tick = int.MinValue;
        private readonly HashSet<(long, int)> seen = new HashSet<(long, int)>();

        /// <summary>PLANT_INTERACTION_GUARDS_1 (A3.7): only an AREA event (an explosion, a multi-cell titan step) is deduplicated per
        /// (tick, source, owner). A single projectile is its own event: 1.6 Bullet.Impact makes one DamageInfo per projectile, so
        /// pellets or burst rounds from one launcher in one tick each land.</summary>
        public bool ShouldForward(int nowTick, long sourceKey, int ownerId, bool areaEvent)
        {
            if (!areaEvent) return true;
            return ShouldForward(nowTick, sourceKey, ownerId);
        }

        public bool ShouldForward(int nowTick, long sourceKey, int ownerId)
        {
            if (nowTick != tick)
            {
                tick = nowTick;
                seen.Clear();
            }
            return seen.Add((sourceKey, ownerId));
        }
    }

    /// <summary>PLANT_INTERACTION_GUARDS_1 (C3.3): the drawn size a huge pawn's hitbox is built from. 1.6
    /// PawnRenderNode_AnimalPart.GraphicFor draws an alternate graphic or femaleGraphicData when one applies, and the mesh follows
    /// THAT graphic's drawSize; the hitbox takes the larger of it and the body graphic per axis, so it never shrinks below the
    /// default body.</summary>
    public static class HitboxDraw
    {
        public static void Pick(float bodyX, float bodyY, bool hasActive, float activeX, float activeY, out float x, out float y)
        {
            x = bodyX; y = bodyY;
            if (!hasActive) return;
            if (!float.IsNaN(activeX) && activeX > x) x = activeX;
            if (!float.IsNaN(activeY) && activeY > y) y = activeY;
        }
    }
}
