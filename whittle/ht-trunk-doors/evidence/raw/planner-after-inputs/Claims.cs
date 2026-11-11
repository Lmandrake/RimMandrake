// Verse-free kernel of how Huge Things turns many plants' desired footprints into real blocker cells safely (GPT review
// 2026-10-07, #1 #2 #5 #6 #8 #9 #16; owner ruling 2026-10-07 20:38 on #4). SelfTest/HugeThingsFuzz.cs compiles this file:
// no Verse/RimWorld/UnityEngine. Cells are RM_HugeFootprintKernel.Key(x, z) longs.
//   ClaimLedger      multi-owner cell claims: a cell is blocked while ANY owner claims it; one physical blocker per cell;
//                    the result never depends on the order owners registered or refreshed in.
//   Planner          which claimed-but-open cells may close NOW: never over pawns, items, protected buildings,
//                    blueprints, frames, interaction cells, trees, other giants or unwalkable ground.
//                    Growth may seal doors and disconnect areas (owner answer 4, 2026-11-11).
//   FootprintSignature  everything the geometry depends on, compared field by field (the selection/refresh cache key).
//   DamageDedup      one forwarded hit per (tick, source, owner): a beam or blast crossing several cells of one giant hits it once.
using System;
using System.Collections.Generic;

namespace RimMandrake.HugeThings
{
    /// <summary>Logical work units, not elapsed time. Callers charge visits and reserve bulk copies/sorts BEFORE doing
    /// them. Exhaustion is caught only at a read/transaction boundary; no unproved blocker is spawned. Oversized read
    /// jobs remain deferred (safe open cells), rather than bypassing the cap. Runtime latency is UNVERIFIED.</summary>
    public sealed class FootprintWorkBudget
    {
        public readonly int Limit;
        public int Used { get; private set; }
        public int Refusals { get; private set; }
        private readonly FootprintWorkBudget parent;
        public FootprintWorkBudget(int limit, FootprintWorkBudget parent = null) { this.parent = parent; if (limit < 0) throw new ArgumentOutOfRangeException(nameof(limit)); Limit = limit; }
        public void Spend(long units = 1)
        {
            if (units < 0) throw new ArgumentOutOfRangeException(nameof(units));
            if (units > Limit - Used) { Refusals++; throw new FootprintBudgetExhausted(); }
            parent?.Spend(units);
            Used += (int)units;
        }
    }

    public sealed class FootprintBudgetExhausted : Exception { }

    /// <summary>FIFO with deduplicated owners; requeue AFTER a visit. No phase can monopolize a tick.</summary>
    public sealed class FootprintOwnerQueue
    {
        private readonly Queue<int> queue = new Queue<int>();
        private readonly HashSet<int> queued = new HashSet<int>();
        public int Count => queue.Count;
        public void Add(int id) { if (queued.Add(id)) queue.Enqueue(id); }
        public bool Next(out int id)
        {
            if (queue.Count == 0) { id = -1; return false; }
            id = queue.Dequeue(); queued.Remove(id); return true;
        }
    }

    public sealed class ClaimLedger
    {
        private readonly Dictionary<long, SortedSet<int>> cellOwners = new Dictionary<long, SortedSet<int>>();
        private readonly Dictionary<int, SortedSet<long>> ownerCells = new Dictionary<int, SortedSet<long>>();

        public bool IsClaimed(long cell) => cellOwners.ContainsKey(cell);

        public int ClaimedCount => cellOwners.Count;

        /// <summary>The owner a cell answers to (labels, damage): the lowest id among its claimants, or -1.</summary>
        public int PrimaryOwner(long cell) => cellOwners.TryGetValue(cell, out SortedSet<int> o) && o.Count > 0 ? o.Min : -1;

        public IEnumerable<long> Claimed => cellOwners.Keys;

        /// <summary>Every owner claiming a cell (ascending), or none.</summary>
        public IEnumerable<int> OwnersOf(long cell)
        {
            if (cellOwners.TryGetValue(cell, out SortedSet<int> o)) return o;
            return Array.Empty<int>();
        }

        public IEnumerable<long> CellsOf(int owner)
        {
            if (ownerCells.TryGetValue(owner, out SortedSet<long> c)) return c;
            return Array.Empty<long>();
        }

        /// <summary>Replace an owner's claims. becameClaimed: cells nobody claimed before; becameFree: cells nobody claims now.</summary>
        public void Set(int owner, IEnumerable<long> cells, List<long> becameClaimed, List<long> becameFree)
        {
            HashSet<long> want = new HashSet<long>(cells);
            if (!ownerCells.TryGetValue(owner, out SortedSet<long> had))
            {
                had = new SortedSet<long>();
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

        public bool AddCell(int owner, long cell)
        {
            if (!ownerCells.TryGetValue(owner, out SortedSet<long> cells)) ownerCells[owner] = cells = new SortedSet<long>();
            cells.Add(cell);
            bool fresh = !cellOwners.TryGetValue(cell, out SortedSet<int> owners);
            if (fresh) cellOwners[cell] = owners = new SortedSet<int>();
            owners.Add(owner); return fresh;
        }

        public bool ReleaseCell(int owner, long cell)
        {
            if (!ownerCells.TryGetValue(owner, out SortedSet<long> cells) || !cells.Remove(cell)) return false;
            if (cells.Count == 0) ownerCells.Remove(owner);
            SortedSet<int> owners = cellOwners[cell]; owners.Remove(owner);
            if (owners.Count > 0) return false;
            cellOwners.Remove(cell); return true;
        }

        public int CountOf(int owner) => ownerCells.TryGetValue(owner, out SortedSet<long> cells) ? cells.Count : 0;

        /// <summary>One affected claim, for budgeted mass removal; never walks remaining blockers.</summary>
        public bool RemoveNext(int owner, out long cell, out bool freed)
        {
            cell = 0; freed = false;
            if (!ownerCells.TryGetValue(owner, out SortedSet<long> cells) || cells.Count == 0) return false;
            cell = cells.Min; cells.Remove(cell);
            if (cells.Count == 0) ownerCells.Remove(owner);
            SortedSet<int> owners = cellOwners[cell]; owners.Remove(owner);
            if (owners.Count == 0) { cellOwners.Remove(cell); freed = true; }
            return true;
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
        Protected = 8,    // building/blueprint/frame/interaction cell/tree/other giant/indestructible/bad ground
    }

    public static class Planner
    {
        public const int Margin = 4;

        /// <summary>Bounds placement-flag reads by the supplied cells/root plus Margin.</summary>
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

        /// <summary>Accept empty, passable, unprotected wanted cells in deterministic order. Access is deliberately
        /// not a placement constraint: growing trunks can seal doors and disconnect rooms. Occupied cells stay pending.</summary>
        public static List<long> Plan(IList<long> wanted, Func<long, CellFlags> flagsAt, CellBox window, FootprintWorkBudget budget = null)
        {
            var accepted = new List<long>();
            if (wanted == null || wanted.Count == 0) return accepted;
            long width = (long)window.MaxX - window.MinX + 1, height = (long)window.MaxZ - window.MinZ + 1;
            if (width <= 0 || height <= 0 || width > MaxWindowCells || height > MaxWindowCells || width * height > MaxWindowCells)
                return accepted;
            budget?.Spend(8L * wanted.Count * (1 + (long)Math.Ceiling(Math.Log(wanted.Count + 1, 2))));
            var order = new List<long>(new HashSet<long>(wanted));
            order.Sort((a, b) =>
            {
                int z = RM_HugeFootprintKernel.KeyZ(a).CompareTo(RM_HugeFootprintKernel.KeyZ(b));
                return z != 0 ? z : RM_HugeFootprintKernel.KeyX(a).CompareTo(RM_HugeFootprintKernel.KeyX(b));
            });
            foreach (long cell in order)
            {
                budget?.Spend();
                if (!window.Contains(RM_HugeFootprintKernel.KeyX(cell), RM_HugeFootprintKernel.KeyZ(cell))) continue;
                CellFlags flags = flagsAt(cell);
                if ((flags & CellFlags.Passable) != 0 && (flags & (CellFlags.Pawn | CellFlags.Item | CellFlags.Protected)) == 0)
                    accepted.Add(cell);
            }
            return accepted;
        }

        /// <summary>Realize accepted cells in order, stopping at the first failed placement transaction. Remaining cells stay pending.</summary>
        public static int RealizeInOrder(IList<long> accepted, Func<long, bool> realize)
        {
            int n = 0;
            for (int i = 0; i < accepted.Count; i++)
            {
                if (!realize(accepted[i])) break;
                n++;
            }
            return n;
        }

        /// <summary>PLANT_FOOTPRINT_HARDENING_1 (A3.12): the largest placement-flag window; a bigger one (bad def data) plans nothing.</summary>
        public const long MaxWindowCells = 512L * 512L;

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
                                                          Func<long, bool> excluded, Func<long, long, bool> preferred, FootprintWorkBudget budget = null)
        {
            Dictionary<long, List<long>> outMoves = new Dictionary<long, List<long>>();
            Dictionary<long, int> used = new Dictionary<long, int>();
            budget?.Spend(8L * itemCounts.Count * (1 + (long)Math.Ceiling(Math.Log(itemCounts.Count + 1, 2))));
            List<long> srcs = new List<long>(itemCounts.Keys);
            srcs.Sort();
            foreach (long src in srcs)
            {
                int need = itemCounts[src];
                if (need <= 0) continue;
                List<long> dests = new List<long>();
                Dictionary<long, int> take = new Dictionary<long, int>();
                foreach (long k in Ring(src, capacity, preferred, budget))
                {
                    if (k == src || excluded(k)) continue;
                    int cap = capacity(k) - (used.TryGetValue(k, out int u) ? u : 0) - (take.TryGetValue(k, out int t) ? t : 0);
                    while (cap > 0 && dests.Count < need)
                    {
                        budget?.Spend();
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

        /// <summary>
        /// PLANT_FOOTPRINT_HARDENING_1 (C3.2): Assign reserves destinations BEFORE the planner runs, so a source the planner then
        /// refuses kept its reservation and could starve another source forever. Assign and plan are iterated: a refused source
        /// is dropped and the rest re-assigned, until every source holding a reservation is one the planner accepts. plan(moves)
        /// returns the accepted cells for that move set. Terminates: each round removes at least one source.
        /// </summary>
        public static Dictionary<long, List<long>> AssignAndPlan(IDictionary<long, int> itemCounts, Func<long, int> capacity,
                                                                 Func<long, bool> excluded, Func<long, long, bool> preferred,
                                                                 Func<Dictionary<long, List<long>>, List<long>> plan,
                                                                 out List<long> accepted, FootprintWorkBudget budget = null)
        {
            budget?.Spend(itemCounts.Count);
            var counts = new Dictionary<long, int>(itemCounts);
            while (true)
            {
                Dictionary<long, List<long>> moves = Assign(counts, capacity, excluded, preferred, budget);
                accepted = plan(moves);
                var ok = new HashSet<long>(accepted);
                var refused = new List<long>();
                foreach (long src in moves.Keys) if (!ok.Contains(src)) refused.Add(src);
                if (refused.Count == 0) return moves;
                foreach (long src in refused) counts.Remove(src);
            }
        }

        /// <summary>Cells reachable from src over capacity >= 0 ground, nearest first (BFS layers), preferred first within a
        /// layer, then by key.</summary>
        private static IEnumerable<long> Ring(long src, Func<long, int> capacity, Func<long, long, bool> preferred, FootprintWorkBudget budget)
        {
            HashSet<long> seen = new HashSet<long> { src };
            List<long> layer = new List<long> { src };
            for (int d = 0; d < MaxRadius && layer.Count > 0; d++)
            {
                List<long> next = new List<long>();
                foreach (long k in layer)
                {
                    budget?.Spend();
                    int x = RM_HugeFootprintKernel.KeyX(k), z = RM_HugeFootprintKernel.KeyZ(k);
                    long[] ns = { RM_HugeFootprintKernel.Key(x + 1, z), RM_HugeFootprintKernel.Key(x - 1, z),
                                  RM_HugeFootprintKernel.Key(x, z + 1), RM_HugeFootprintKernel.Key(x, z - 1) };
                    foreach (long n in ns)
                    {
                        budget?.Spend();
                        if (seen.Add(n) && capacity(n) >= 0) next.Add(n);
                    }
                }
                budget?.Spend(8L * next.Count * (1 + (long)Math.Ceiling(Math.Log(next.Count + 1, 2))));
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
