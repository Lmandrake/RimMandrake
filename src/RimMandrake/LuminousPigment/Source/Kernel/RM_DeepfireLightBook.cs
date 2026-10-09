// Verse-free kernel of the Deepfire light bookkeeping (MapComponent_DeepfireLights.Clusters.cs): the per-cell floor coat
// grid, the 3x3 block clustering of coated floor cells and 1x1 coated buildings, the anchor cell and radius of a cluster,
// and which Thing owns its own proxy light versus joins a cluster. The mod keeps the engine half (proxies, colours,
// terrain); this book decides WHAT lights exist and calls setLight/removeLight/setOwn/removeOwn for each change.
// SelfTest/LuminousPigmentFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.LuminousPigment
{
    public readonly struct DeepfireClusterKey : IEquatable<DeepfireClusterKey>
    {
        public readonly int Block;
        public readonly byte Kind;
        public readonly int Coats;
        public readonly int Color;

        public DeepfireClusterKey(int block, byte kind, int coats, int color) { Block = block; Kind = kind; Coats = coats; Color = color; }

        public bool Equals(DeepfireClusterKey o) { return Block == o.Block && Kind == o.Kind && Coats == o.Coats && Color == o.Color; }
        public override bool Equals(object obj) { return obj is DeepfireClusterKey k && Equals(k); }
        public override int GetHashCode()
        {
            unchecked
            {
                int h = Block;
                h = h * 397 ^ Kind;
                h = h * 397 ^ Coats;
                h = h * 397 ^ Color;
                return h;
            }
        }
        public override string ToString() { return "b" + Block + "/k" + Kind + "/c" + Coats + "/#" + Color; }
    }

    // A glow colour as the book sees it: Packed is the 8-bit-per-channel identity used in the cluster key (cells with the
    // same packed colour share a light), Color is the payload handed back to setLight (the first cell's exact colour).
    public struct DeepfireGlow<TColor> { public int Packed; public TColor Color; }

    // What the mod reports about a registered Thing at rebuild time: Live = spawned on this map with a coated comp.
    public struct DeepfireThingView<TColor> { public bool Live; public int Coats; public int X, Z; public DeepfireGlow<TColor> Glow; }

    public sealed class DeepfireLightBook<TThing, TColor> where TThing : class
    {
        public const byte KindFloor = 0;
        public const byte KindBuilding = 1;

        private sealed class Group { public TColor Color; public readonly List<int> Xs = new List<int>(); public readonly List<int> Zs = new List<int>(); }

        private readonly int mapX, mapZ;
        private readonly Func<int> blockSize;
        private readonly Func<int, float> radiusForCoats;
        private readonly float radiusBonus;
        private readonly Func<int, int, int, DeepfireGlow<TColor>> floorGlow;
        private readonly Func<TThing, DeepfireThingView<TColor>> thingView;
        private readonly Action<DeepfireClusterKey, int, int, TColor, float> setLight;
        private readonly Action<DeepfireClusterKey> removeLight;
        private readonly Action<TThing, int, int, TColor, float> setOwn;
        private readonly Action<TThing> removeOwn;

        private byte[] floor;
        private int coated;
        private readonly Dictionary<TThing, long> clustered = new Dictionary<TThing, long>();   // thing -> cell it joined at (x,z packed)
        private readonly Dictionary<int, List<TThing>> blockThings = new Dictionary<int, List<TThing>>();
        private readonly Dictionary<int, List<DeepfireClusterKey>> blockKeys = new Dictionary<int, List<DeepfireClusterKey>>();
        private readonly HashSet<TThing> own = new HashSet<TThing>();
        private readonly Dictionary<DeepfireClusterKey, Group> tmp = new Dictionary<DeepfireClusterKey, Group>();

        public DeepfireLightBook(int mapX, int mapZ, Func<int> blockSize, Func<int, float> radiusForCoats, float radiusBonus,
            Func<int, int, int, DeepfireGlow<TColor>> floorGlow, Func<TThing, DeepfireThingView<TColor>> thingView,
            Action<DeepfireClusterKey, int, int, TColor, float> setLight, Action<DeepfireClusterKey> removeLight,
            Action<TThing, int, int, TColor, float> setOwn, Action<TThing> removeOwn)
        {
            this.mapX = mapX; this.mapZ = mapZ; this.blockSize = blockSize; this.radiusForCoats = radiusForCoats; this.radiusBonus = radiusBonus;
            this.floorGlow = floorGlow; this.thingView = thingView; this.setLight = setLight; this.removeLight = removeLight;
            this.setOwn = setOwn; this.removeOwn = removeOwn;
        }

        // ---- static geometry ----
        public static long Pack(int x, int z) { return ((long)x << 32) | (uint)z; }
        public static int BlockSizeOf(int setting) { return Math.Max(1, setting); }
        public static int BlocksX(int mapX, int size) { return (mapX + size - 1) / size; }
        public static int BlockIndexOf(int x, int z, int mapX, int size) { return (z / size) * BlocksX(mapX, size) + (x / size); }
        // Spec §3.6: a 1x1 Building joins a cluster only while clustering is on (block size above 1).
        public static bool Clusterable(int blockSizeSetting, bool isBuilding, int sizeX, int sizeZ) { return blockSizeSetting > 1 && isBuilding && sizeX == 1 && sizeZ == 1; }

        // The cell nearest the group's centroid (first wins a tie).
        // A cluster light must reach every member it stands for: radius is at least the farthest member's distance plus this.
        public const float ClusterCoverage = 0.5f;

        public static float FarthestMemberDistance(IList<int> xs, IList<int> zs, int anchor)
        {
            double best = 0;
            for (int i = 0; i < xs.Count; i++)
            {
                double dx = xs[i] - xs[anchor], dz = zs[i] - zs[anchor], d = dx * dx + dz * dz;
                if (d > best) best = d;
            }
            return (float)Math.Sqrt(best);
        }

        public static int AnchorIndex(IList<int> xs, IList<int> zs)
        {
            if (xs.Count == 1) return 0;
            float sx = 0f, sz = 0f;
            for (int i = 0; i < xs.Count; i++) { sx += xs[i]; sz += zs[i]; }
            sx /= xs.Count; sz /= xs.Count;
            int best = 0; float bestD = float.MaxValue;
            for (int i = 0; i < xs.Count; i++)
            {
                float d = (xs[i] - sx) * (xs[i] - sx) + (zs[i] - sz) * (zs[i] - sz);
                if (d < bestD) { bestD = d; best = i; }
            }
            return best;
        }

        private bool InBounds(int x, int z) { return x >= 0 && z >= 0 && x < mapX && z < mapZ; }
        private int Size { get { return BlockSizeOf(blockSize()); } }
        private int BlockOf(int x, int z) { return BlockIndexOf(x, z, mapX, Size); }

        // ---- floor grid ----
        public byte[] FloorGrid { get { return floor; } set { floor = value; } }
        public int CoatedFloorCells { get { return coated; } }
        public int NumCells { get { return mapX * mapZ; } }
        public void EnsureGrid() { if (floor == null || floor.Length != mapX * mapZ) { floor = new byte[mapX * mapZ]; coated = 0; } }
        public int FloorCoatsAt(int x, int z) { return floor == null || !InBounds(x, z) ? 0 : floor[z * mapX + x]; }

        // Spec §3.3: coatable floor with fewer than `cap` coats.
        public bool CanAddFloorCoat(bool coatable, int x, int z, int cap) { return coatable && InBounds(x, z) && FloorCoatsAt(x, z) < cap; }

        public bool AddFloorCoat(bool coatable, int x, int z, int cap, out bool firstCoat)
        {
            firstCoat = false;
            if (!CanAddFloorCoat(coatable, x, z, cap)) return false;
            EnsureGrid();
            int i = z * mapX + x;
            firstCoat = floor[i] == 0;
            if (firstCoat) coated++;
            floor[i]++;
            RebuildBlock(BlockOf(x, z));
            return true;
        }

        public bool ClearFloorCoats(int x, int z)
        {
            if (floor == null || !InBounds(x, z)) return false;
            int i = z * mapX + x;
            if (floor[i] == 0) return false;
            floor[i] = 0;
            coated--;
            RebuildBlock(BlockOf(x, z));
            return true;
        }

        public void NotifyFloorColorChanged(int x, int z) { if (FloorCoatsAt(x, z) > 0) RebuildBlock(BlockOf(x, z)); }

        public int CountCoated(IEnumerable<long> cells)
        {
            if (floor == null || coated == 0) return 0;
            int n = 0;
            foreach (long c in cells) { int x = (int)(c >> 32), z = (int)(c & 0xffffffffL); if (InBounds(x, z) && floor[z * mapX + x] > 0) n++; }
            return n;
        }

        // Map load: drop a grid of the wrong size, drop coats whose floor vanished, clamp to the ceiling, recount, relight.
        public void Finalize(Func<int, int, bool> coatable, int ceiling)
        {
            if (floor != null && floor.Length != mapX * mapZ) floor = null;
            EnsureGrid();
            coated = 0;
            var dirty = new HashSet<int>();
            for (int i = 0; i < floor.Length; i++)
            {
                if (floor[i] == 0) continue;
                int x = i % mapX, z = i / mapX;
                if (!coatable(x, z)) { floor[i] = 0; continue; }
                if (floor[i] > ceiling) floor[i] = (byte)ceiling;
                coated++;
                dirty.Add(BlockOf(x, z));
            }
            foreach (int b in dirty) RebuildBlock(b);
        }

        // ---- things ----
        public bool IsClustered(TThing t) { return clustered.ContainsKey(t); }
        public bool HasOwn(TThing t) { return own.Contains(t); }
        public int ClusteredCount { get { return clustered.Count; } }
        public int OwnCount { get { return own.Count; } }

        // RegisterThingLight: a clusterable thing joins its block (and loses any proxy of its own), anything else owns a proxy
        // (and leaves any cluster it was in).
        public void RegisterThing(TThing t, int x, int z, bool clusterable, TColor color, float radius)
        {
            if (clusterable)
            {
                if (own.Remove(t)) removeOwn(t);
                long cell = Pack(x, z);
                if (clustered.TryGetValue(t, out long old))
                {
                    if (old != cell)
                    {
                        int ox = (int)(old >> 32), oz = (int)(old & 0xffffffffL);
                        RemoveFromBlockList(t, ox, oz);
                        AddToBlockList(t, x, z);
                        RebuildBlock(BlockOf(ox, oz));
                    }
                }
                else AddToBlockList(t, x, z);
                clustered[t] = cell;
                RebuildBlock(BlockOf(x, z));
            }
            else
            {
                DeregisterCluster(t);
                own.Add(t);
                setOwn(t, x, z, color, radius);
            }
        }

        // DeregisterThingLight: whichever light the thing had goes.
        public bool DeregisterThing(TThing t)
        {
            bool was = DeregisterCluster(t);
            if (own.Remove(t)) { removeOwn(t); was = true; }
            return was;
        }

        private bool DeregisterCluster(TThing t)
        {
            if (!clustered.TryGetValue(t, out long cell)) return false;
            clustered.Remove(t);
            int x = (int)(cell >> 32), z = (int)(cell & 0xffffffffL);
            RemoveFromBlockList(t, x, z);
            RebuildBlock(BlockOf(x, z));
            return true;
        }

        private void AddToBlockList(TThing t, int x, int z)
        {
            int b = BlockOf(x, z);
            if (!blockThings.TryGetValue(b, out List<TThing> l)) { l = new List<TThing>(); blockThings[b] = l; }
            if (!l.Contains(t)) l.Add(t);
        }

        private void RemoveFromBlockList(TThing t, int x, int z)
        {
            int b = BlockOf(x, z);
            if (blockThings.TryGetValue(b, out List<TThing> l)) { l.Remove(t); if (l.Count == 0) blockThings.Remove(b); }
        }

        // ---- rebuild ----
        public void ClearClusterState()
        {
            clustered.Clear(); blockThings.Clear(); blockKeys.Clear();
        }

        // Settings change of the block size (or a map reload of the cluster state): drop every cluster light, forget every
        // membership, relight every coated floor block, then re-register every coated building via `register` (the mod
        // routes each through RegisterThing so clustered and own-light things both end up lit).
        public void RebuildAll(Action registerThings)
        {
            var stale = new List<DeepfireClusterKey>();
            foreach (List<DeepfireClusterKey> ks in blockKeys.Values) stale.AddRange(ks);
            for (int i = 0; i < stale.Count; i++) removeLight(stale[i]);
            ClearClusterState();
            if (floor != null && coated > 0)
            {
                var done = new HashSet<int>();
                for (int i = 0; i < floor.Length; i++)
                {
                    if (floor[i] == 0) continue;
                    int b = BlockOf(i % mapX, i / mapX);
                    if (done.Add(b)) RebuildBlock(b);
                }
            }
            registerThings();
        }

        public void RebuildBlock(int block)
        {
            int size = Size;
            int bx = block % BlocksX(mapX, size);
            int bz = block / BlocksX(mapX, size);
            tmp.Clear();
            if (floor != null && coated > 0)
            {
                for (int dz = 0; dz < size; dz++)
                    for (int dx = 0; dx < size; dx++)
                    {
                        int x = bx * size + dx, z = bz * size + dz;
                        if (!InBounds(x, z)) continue;
                        int coats = floor[z * mapX + x];
                        if (coats <= 0) continue;
                        AddToGroup(block, KindFloor, coats, floorGlow(x, z, coats), x, z);
                    }
            }
            if (blockThings.TryGetValue(block, out List<TThing> things))
            {
                for (int i = 0; i < things.Count; i++)
                {
                    DeepfireThingView<TColor> v = thingView(things[i]);
                    if (!v.Live || v.Coats <= 0) continue;
                    AddToGroup(block, KindBuilding, v.Coats, v.Glow, v.X, v.Z);
                }
            }

            var produced = new List<DeepfireClusterKey>(tmp.Count);
            foreach (KeyValuePair<DeepfireClusterKey, Group> kv in tmp)
            {
                Group g = kv.Value;
                float radius = radiusForCoats(kv.Key.Coats);
                if (g.Xs.Count > 1) radius += radiusBonus;
                int a = AnchorIndex(g.Xs, g.Zs);
                radius = Math.Max(radius, FarthestMemberDistance(g.Xs, g.Zs, a) + ClusterCoverage);   // CLUSTER_LIGHT_MEMBER_COVERAGE_1
                setLight(kv.Key, g.Xs[a], g.Zs[a], g.Color, radius);
                produced.Add(kv.Key);
            }
            tmp.Clear();

            if (blockKeys.TryGetValue(block, out List<DeepfireClusterKey> previous))
                for (int i = 0; i < previous.Count; i++)
                    if (!produced.Contains(previous[i])) removeLight(previous[i]);
            if (produced.Count > 0) blockKeys[block] = produced; else blockKeys.Remove(block);
        }

        private void AddToGroup(int block, byte kind, int coats, DeepfireGlow<TColor> glow, int x, int z)
        {
            var key = new DeepfireClusterKey(block, kind, coats, glow.Packed);
            if (!tmp.TryGetValue(key, out Group g)) { g = new Group { Color = glow.Color }; tmp[key] = g; }
            g.Xs.Add(x); g.Zs.Add(z);
        }

        // For the fuzz and the dev counters: every cluster key currently lit.
        public IEnumerable<DeepfireClusterKey> LitKeys() { foreach (List<DeepfireClusterKey> ks in blockKeys.Values) foreach (DeepfireClusterKey k in ks) yield return k; }
    }
}
