// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES (BENCH TPS bisect 2026-10-26: RM_MapComponent_Excavation 0.87 ms/tick on a 325x325
// map, single ticks of 158-172 ms). The excavation tick drives RM_PocketGrid.Tick -> RM_WallReach.Tick. Two whole-map passes ran
// far more often than their inputs changed:
//   1. RM_WallReach: every PathFinderMapData.GatherData (any tick a pawn paths) bumped wallGen, so every labelling (whole-map
//      Kinds() scan + one flood per entry) rebuilt at the 60-tick ceiling even on a map whose walls never moved.
//   2. RM_PocketGrid / RM_WallReach: a ClimbGeneration bump re-flooded every band of every view even when the depth view the
//      floods read came out byte-identical (the spike: plain+stride+floor views x bands x 325x325 in one tick).
// The fix keeps results identical by construction: a delta moves the generation only when its square's kind differs from the
// snapshot the labels were built from (RM_WallReachMath.DeltaMovesKinds), and a rebuild over byte-identical inputs keeps the
// labels (RM_WallReachMath.SameBytes / SameRamps). These checks replay randomized maps against the old full scan.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class ExcavationTickChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static bool SameLabels(RM_WallReachMath.Labels a, RM_WallReachMath.Labels b)
        {
            if (a == null || b == null) return a == b;
            if (a.count != b.count || a.width != b.width || a.height != b.height || a.label.Length != b.label.Length) return false;
            for (int i = 0; i < a.label.Length; i++) if (a.label[i] != b.label[i]) return false;
            return true;
        }

        private static bool SameLabels(RM_PocketGridMath.Labels a, RM_PocketGridMath.Labels b)
        {
            if (a == null || b == null) return a == b;
            if (a.count != b.count || a.k != b.k || a.label.Length != b.label.Length) return false;
            for (int i = 0; i < a.label.Length; i++) if (a.label[i] != b.label[i]) return false;
            for (int c = 0; c < a.count; c++) if (a.surface[c] != b.surface[c] || a.size[c] != b.size[c]) return false;
            return true;
        }

        // EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: the two floods exactly as they were before the scratch rewrite (r13, 54dd83e4d1),
        // kept as the reference the rewritten ones must equal on every input.
        private static RM_PocketGridMath.Labels RefPocketLabel(byte[] depth, int width, int height, int k, Func<int, int, bool> rampJoins = null)
        {
            if (depth == null || width <= 0 || height <= 0 || depth.Length < width * height)
            {
                throw new ArgumentException("depth grid does not match " + width + "x" + height);
            }
            int n = width * height;
            var lab = new int[n];
            for (int i = 0; i < n; i++)
            {
                lab[i] = -1;
            }
            var surface = new List<bool>();
            var size = new List<int>();
            var queue = new int[n];
            int count = 0;
            for (int seed = 0; seed < n; seed++)
            {
                if (lab[seed] >= 0)
                {
                    continue;
                }
                int id = count++;
                bool surf = false;
                int sz = 0;
                int head = 0, tail = 0;
                queue[tail++] = seed;
                lab[seed] = id;
                while (head < tail)
                {
                    int c = queue[head++];
                    sz++;
                    int d = depth[c];
                    if (d == 0)
                    {
                        surf = true;
                    }
                    int x = c % width, z = c / width;
                    for (int dir = 0; dir < 4; dir++)
                    {
                        int nx = x, nz = z;
                        switch (dir)
                        {
                            case 0: nz++; break;
                            case 1: nx++; break;
                            case 2: nz--; break;
                            default: nx--; break;
                        }
                        if (nx < 0 || nz < 0 || nx >= width || nz >= height)
                        {
                            continue;
                        }
                        int ni = nz * width + nx;
                        if (lab[ni] >= 0)
                        {
                            continue;
                        }
                        bool ramp = rampJoins != null && (rampJoins(c, ni) || rampJoins(ni, c));
                        if (!RM_PitTrapMath.StepAllowed(d, depth[ni], k, ramp))
                        {
                            continue;
                        }
                        lab[ni] = id;
                        queue[tail++] = ni;
                    }
                }
                surface.Add(surf);
                size.Add(sz);
            }
            return new RM_PocketGridMath.Labels
            {
                label = lab, count = count, surface = surface.ToArray(), size = size.ToArray(),
                width = width, height = height, k = k,
            };
        }

        private static RM_WallReachMath.Labels RefWallLabel(byte[] kind, byte[] depth, int width, int height, int k, int cls, Func<int, int, bool> rampJoins = null)
        {
            if (kind == null || width <= 0 || height <= 0 || kind.Length < width * height || (depth != null && depth.Length < width * height))
            {
                throw new ArgumentException("grids do not match " + width + "x" + height);
            }
            int n = width * height;
            var lab = new int[n];
            for (int i = 0; i < n; i++)
            {
                lab[i] = RM_WallReachMath.Passable(kind[i], cls) ? int.MaxValue : -1;   // MaxValue = passable, not yet labelled
            }
            var queue = new int[n];
            int count = 0;
            for (int seed = 0; seed < n; seed++)
            {
                if (lab[seed] != int.MaxValue)
                {
                    continue;
                }
                int id = count++;
                int head = 0, tail = 0;
                queue[tail++] = seed;
                lab[seed] = id;
                while (head < tail)
                {
                    int c = queue[head++];
                    int x = c % width, z = c / width;
                    int d = depth == null ? 0 : depth[c];
                    for (int dir = 0; dir < 4; dir++)
                    {
                        int nx = x, nz = z;
                        switch (dir)
                        {
                            case 0: nz++; break;
                            case 1: nx++; break;
                            case 2: nz--; break;
                            default: nx--; break;
                        }
                        if (nx < 0 || nz < 0 || nx >= width || nz >= height)
                        {
                            continue;
                        }
                        int ni = nz * width + nx;
                        if (lab[ni] != int.MaxValue)
                        {
                            continue;
                        }
                        if (depth != null)
                        {
                            bool ramp = rampJoins != null && (rampJoins(c, ni) || rampJoins(ni, c));
                            if (!RM_PitTrapMath.StepAllowed(d, depth[ni], k, ramp))
                            {
                                continue;
                            }
                        }
                        lab[ni] = id;
                        queue[tail++] = ni;
                    }
                }
            }
            return new RM_WallReachMath.Labels { label = lab, count = count, width = width, height = height, k = k, cls = cls };
        }

        private static readonly byte[] KindPool =
        {
            RM_WallReachMath.Open, RM_WallReachMath.Open, RM_WallReachMath.Open, RM_WallReachMath.Open, RM_WallReachMath.Wall,
            RM_WallReachMath.Wall, RM_WallReachMath.Door, RM_WallReachMath.PlayerDoor, RM_WallReachMath.Fence, RM_WallReachMath.DeepWater,
            RM_WallReachMath.HeldDoor, RM_WallReachMath.ShutGate,
        };

        private static byte[] RandomKinds(Random r, int n)
        {
            var k = new byte[n];
            for (int i = 0; i < n; i++) k[i] = KindPool[r.Next(KindPool.Length)];
            return k;
        }

        private static byte[] RandomDepth(Random r, int n, bool anyDug)
        {
            var d = new byte[n];
            if (anyDug) for (int i = 0; i < n; i++) d[i] = r.Next(4) == 0 ? (byte)r.Next(1, 6) : (byte)0;
            return d;
        }

        /// <summary>One simulated labelling under the new policy: the production classes (RM_WallReach.Kinds runs the
        /// KindsSnapshot, RM_WallReach.Build the LabelSlot), driven without Verse.</summary>
        private sealed class Sim
        {
            public readonly RM_WallReachMath.KindsSnapshot kinds = new RM_WallReachMath.KindsSnapshot();
            public readonly RM_WallReachMath.LabelSlot slot = new RM_WallReachMath.LabelSlot();
            public long gen;                 // wallGen
            public long builtGen = -1;
            public int bumps;
            private long reads;
            public byte[] snapshot => kinds.published;
            public byte[] builtDepth => slot.builtDepth;
            public RM_WallReachMath.Labels labels => slot.labels;
            public int floods => slot.floods;
            public int skips => slot.skips;

            public void Rebuild(byte[] liveKinds, byte[] depth, int w, int h, int band, int cls)
            {
                byte[] read = kinds.Take(liveKinds.Length);   // Kinds(): every square written, then published or kept as scratch
                Array.Copy(liveKinds, read, liveKinds.Length);
                byte[] snap = kinds.Publish(read, ++reads, w, h);
                slot.Rebuild(snap, depth, null, w, h, band, cls);
                builtGen = gen;
            }
        }

        // ── EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES, the pulse (live r11: DoPulse up to 576 ms in one tick on 325x325) ──
        // Three changes, each pinned against the pre-fix work on randomized scenes of the shipped Verse-free kernel
        // (RM_FlowKernel / RM_LevelSolve, compiled into this test as they ship; no copy):
        //   1. exact shortcuts: a rotated network skips the flow order the exact path never reads; a domain with no pond and
        //      no limitless mouth solves once (exactShortcutsEnabled off = the old work, byte for byte);
        //   2. the component walk on grid indices with stamp sets (CollectComponentGrid vs RM_StockMath.CollectComponent);
        //   3. the pulse in slices (BeginPulse + StepPulse(budget) vs one Pulse), and its cost bound on a 325x325 map.

        /// <summary>A small random map: dug channels and pits with water, ponds (limited or limitless, some with beds),
        /// edge sinks, a low network cap so big networks rotate. Exact-level or the older unit engine.</summary>
        private static (ArrayWorld w, List<int> seeds) PulseScene(int seed, bool exact)
        {
            var r = new Random(seed);
            int w = r.Next(10, 31), h = r.Next(10, 31), n = w * h;
            var aw = new ArrayWorld(w, h);
            var k = aw.k;
            k.levelExactEnabled = exact;
            k.part = exact ? new ushort[n] : null;
            k.levelBySurfaceEnabled = r.Next(4) != 0;
            k.levelSetEnabled = k.levelBySurfaceEnabled && r.Next(2) == 0;
            k.viscosityEnabled = r.Next(2) == 0;
            k.creepEnabled = k.viscosityEnabled && r.Next(2) == 0;
            k.creepWaterEnabled = r.Next(2) == 0;
            k.flowPerPulse = r.Next(1, 3);
            k.seamRotationEnabled = r.Next(4) != 0;
            k.maxComponentCells = r.Next(12, 120);
            k.edgeSinksEnabled = r.Next(3) == 0;
            if (k.edgeSinksEnabled) for (int i = 0; i < n; i++) aw.sink[i] = i % w == 0 || i / w == 0;
            Fluid[] fluids = r.Next(3) == 0 ? new[] { ArrayWorld.Water, ArrayWorld.Tar } : new[] { ArrayWorld.Water };
            var blobFirst = new List<int>();
            int blobs = r.Next(0, 4);
            for (int b = 0; b < blobs; b++)
            {
                int x0 = r.Next(w), z0 = r.Next(h), bw = r.Next(1, 6), bh = r.Next(1, 6);
                Fluid f = fluids[r.Next(fluids.Length)];
                for (int x = x0; x < Math.Min(w, x0 + bw); x++)
                    for (int z = z0; z < Math.Min(h, z0 + bh); z++)
                    {
                        int i = z * w + x;
                        aw.natural[i] = true; aw.terrainFluid[i] = f;
                        if (r.Next(3) == 0) aw.bed[i] = r.Next(0, 5);
                    }
                blobFirst.Add(z0 * w + x0);
            }
            int digs = r.Next(2, 9);
            for (int d = 0; d < digs; d++)
            {
                int depth = r.Next(1, 5);
                int x = r.Next(w), z = r.Next(h);
                if (r.Next(2) == 0)
                {
                    int bw = r.Next(1, 9), bh = r.Next(1, 9);
                    for (int xx = x; xx < Math.Min(w, x + bw); xx++)
                        for (int zz = z; zz < Math.Min(h, z + bh); zz++) Dig(aw, zz * w + xx, depth);
                }
                else
                {
                    for (int s = r.Next(5, 40); s > 0; s--)
                    {
                        Dig(aw, z * w + x, depth);
                        int dir = r.Next(4);
                        x = Math.Max(0, Math.Min(w - 1, x + (dir == 1 ? 1 : dir == 3 ? -1 : 0)));
                        z = Math.Max(0, Math.Min(h - 1, z + (dir == 0 ? 1 : dir == 2 ? -1 : 0)));
                    }
                }
            }
            var seeds = new List<int>();
            for (int i = 0; i < n; i++)
            {
                if (k.depth[i] == 0) continue;
                seeds.Add(i);
                if (r.Next(2) == 0)
                {
                    k.fill[i] = (byte)r.Next(0, k.depth[i] + 1);
                    if (exact && k.fill[i] < k.depth[i] && r.Next(2) == 0) k.part[i] = (ushort)r.Next(1, RM_LevelSolve.U);
                    if (k.fill[i] > 0 || (exact && k.part[i] > 0)) aw.cellFluid[i] = fluids[r.Next(fluids.Length)];
                }
            }
            // seeds in a shuffled order: the kernel sorts them (owner ruling 2026-10-06)
            for (int i = seeds.Count - 1; i > 0; i--) { int j = r.Next(i + 1); (seeds[i], seeds[j]) = (seeds[j], seeds[i]); }
            foreach (int f in blobFirst) aw.BodyAt(f, (float)r.NextDouble(), r.Next(3) == 0);
            for (int i = 0; i < n; i++) if (aw.natural[i]) aw.BodyAt(i);
            return (aw, seeds);
        }

        private static void Dig(ArrayWorld aw, int i, int depth)
        {
            if (aw.natural[i]) return;
            aw.k.depth[i] = (byte)Math.Max(aw.k.depth[i], depth);
        }

        /// <summary>Everything a pulse writes or reports: the grids, the fluid grid, every body's stock, the external
        /// inputs and the kernel's per-pulse outputs.</summary>
        private static string PulseSnap(ArrayWorld aw)
        {
            var k = aw.k;
            var sb = new System.Text.StringBuilder();
            for (int i = 0; i < aw.w * aw.h; i++)
                sb.Append(k.fill[i]).Append(',').Append(k.part != null ? k.part[i] : 0).Append(',').Append(aw.cellFluid[i]?.name ?? "-").Append(';');
            foreach (var b in aw.bodies) sb.Append('B').Append(b.Dl()).Append('/').Append(b.stock.ToString("R"));
            foreach (var kv in aw.externalIn) sb.Append('E').Append(kv.Key.name).Append('=').Append(kv.Value.ToString("R"));
            sb.Append("|sink=").Append(k.sinkDrained.ToString("R")).Append("|cr=").Append(k.exactCreditDl).Append("|dr=").Append(k.exactDrainDl)
                .Append("|imb=").Append(k.worstImbalance.ToString("R")).Append('|').Append(string.Join(";", k.imbalanceReports))
                .Append("|rot=").Append(k.rotatedNetworks);
            return sb.ToString();
        }

        /// <summary>One pulse in slices of <paramref name="budget"/> cells each, a slice ending after the unit that crosses it
        /// (a fresh random budget per slice when <paramref name="r"/> is given); <paramref name="between"/> runs between slices. Returns the slice count.</summary>
        private static int SlicedPulse(ArrayWorld aw, List<int> seeds, int budget, Random r = null, Action between = null)
        {
            aw.pulse++;
            aw.k.BeginPulse(seeds, aw.pulse);
            int slices = 1;
            while (!aw.k.StepPulse(r != null ? r.Next(1, budget + 1) : budget))
            {
                if (++slices > 1000000) throw new Exception("a sliced pulse never finished");
                between?.Invoke();
            }
            aw.Sync();
            return slices;
        }

        /// <summary>Counts excavated squares resolved more than once in a pulse (ComponentResolved), delegating the rest.</summary>
        private sealed class CountingWorld : RM_IFlowWorld, RM_ILevelWorld
        {
            private readonly ArrayWorld a;
            private readonly long[] stamp;
            public long pulse;
            public int twice, resolved;
            public CountingWorld(ArrayWorld a) { this.a = a; stamp = new long[a.w * a.h]; }
            public bool IsNaturalLiquid(int idx) => a.IsNaturalLiquid(idx);
            public bool CanSupply(int idx) => a.CanSupply(idx);
            public bool TryDebitLevel(int idx) => a.TryDebitLevel(idx);
            public object DonorFluid(int idx, bool source) => a.DonorFluid(idx, source);
            public object CellFluid(int idx) => a.CellFluid(idx);
            public void Claim(int idx, object fluid) => a.Claim(idx, fluid);
            public bool CanClaim(object fluid) => a.CanClaim(fluid);
            public int TicksPerTile(object fluid) => a.TicksPerTile(fluid);
            public bool IsSink(int idx) => a.IsSink(idx);
            public void ComponentResolved(List<int> component)
            {
                foreach (int c in component)
                {
                    if (a.k.depth[c] == 0) continue;
                    if (stamp[c] == pulse) twice++;
                    stamp[c] = pulse;
                    resolved++;
                }
            }
            public int LevelBodyOf(int src) => a.LevelBodyOf(src);
            public long BodyStockDl(int body) => a.BodyStockDl(body);
            public void SetBodyStockDl(int body, long dl) => a.SetBodyStockDl(body, dl);
            public int[] BodyHistogram(int body) => a.BodyHistogram(body);
            public int BedAt(int src) => a.BedAt(src);
            public void NoteLimitlessDl(object fluid, long dl) => a.NoteLimitlessDl(fluid, dl);
        }

        private static void PulseCases(Action<string, Action> Case)
        {
            Case("ExcavationTick_exact_shortcuts_equal_reference", () =>
            {
                int rotated = 0, pondless = 0, ponded = 0;
                for (int seed = 0; seed < 150; seed++)
                {
                    var (refW, seeds) = PulseScene(seed, true);
                    var (newW, _) = PulseScene(seed, true);
                    refW.k.exactShortcutsEnabled = false;
                    if (refW.bodies.Count == 0) pondless++; else ponded++;
                    for (int p = 0; p < 25; p++)
                    {
                        refW.Pulse(seeds);
                        newW.Pulse(seeds);
                        string a = PulseSnap(refW), b = PulseSnap(newW);
                        Assert(a == b, $"seed {seed} pulse {p}: the shortcut kernel differs from the full work");
                        Assert(newW.k.worstImbalance == 0, $"seed {seed} pulse {p}: ledger {string.Join("; ", newW.k.imbalanceReports)}");
                    }
                    if (newW.k.rotatedNetworks > 0) rotated++;
                }
                Console.WriteLine($"    150 exact scenes x 25 pulses equal: {rotated} with rotated networks, {pondless} pondless, {ponded} with ponds");
                Assert(rotated > 10 && pondless > 10 && ponded > 10, "the scenes do not exercise both shortcuts (sanity probe)");
            });
            Case("StepPulse_shrink_end_state_pinned", () =>
            {
                // STEPPULSE_SHRINK_STEADY_SLICE_COST: the faster kernel (linear index sort, flat solver edges, a band that copies the
                // band above, one divide a lay) must end every scene byte-identical to the kernel before it. The digests were taken
                // from that kernel (f9416b0d72 / 8d0d9f511b sources) on these very scenes; a change in any dL, fluid, body stock or
                // ledger line changes them.
                var sha = System.Security.Cryptography.SHA256.Create();
                string Digest(System.Text.StringBuilder sb) =>
                    BitConverter.ToString(sha.ComputeHash(System.Text.Encoding.UTF8.GetBytes(sb.ToString()))).Replace("-", "").Substring(0, 16);
                var scenes = new System.Text.StringBuilder();
                for (int seed = 0; seed < 120; seed++)
                {
                    bool exact = seed % 4 != 3;
                    var (aw, seeds) = PulseScene(seed, exact);
                    for (int p = 0; p < 20; p++)
                    {
                        aw.Pulse(seeds);
                        scenes.Append(PulseSnap(aw)).Append('#');
                    }
                }
                var r = new Random(4242);
                var solves = new System.Text.StringBuilder();
                var solve = new RM_LevelSolve();
                int solved = 0;
                for (int t = 0; t < 3000; t++)
                {
                    solve.Clear();
                    int cells = r.Next(1, 40), ponds = r.Next(3) == 0 ? r.Next(1, 3) : 0;
                    bool even = r.Next(3) == 0;   // a run of one depth: the band copy's case
                    int evenDepth = r.Next(1, 7);
                    var depthOf = new int[cells];
                    for (int i = 0; i < cells; i++)
                    {
                        depthOf[i] = even ? evenDepth : r.Next(1, 7);
                        solve.AddCell(depthOf[i], r.Next(3) == 0 ? 0 : r.Next(0, depthOf[i] * RM_LevelSolve.U + 1));
                    }
                    for (int k = 0; k < ponds; k++)
                    {
                        int bed = r.Next(1, 6);
                        var h = new int[bed + 1];
                        int sq = r.Next(1, 30);
                        h[0] = sq;
                        for (int l = 1; l <= bed; l++) { sq = Math.Max(1, sq - r.Next(0, 6)); h[l] = sq; }
                        solve.AddPond(h, r.Next(0, (int)Math.Min(int.MaxValue, RM_LevelSolve.PondCapacity(h) + 1)));
                    }
                    int nodes = cells + ponds;
                    for (int i = 1; i < cells; i++)
                    {
                        int j = r.Next(2) == 0 ? i - 1 : r.Next(0, i);
                        solve.AddEdge(i, j, even && r.Next(4) != 0 ? evenDepth : Math.Min(depthOf[i], depthOf[j]) - (r.Next(5) == 0 ? 1 : 0));
                    }
                    for (int k = 0; k < ponds; k++)
                    {
                        int c = r.Next(0, cells);
                        solve.AddEdge(c, cells + k, Math.Min(depthOf[c], r.Next(1, 6)));
                    }
                    bool ok = solve.Solve();
                    if (ok) solved++;
                    solves.Append(ok ? 'y' : 'n');
                    for (int i = 0; ok && i < nodes; i++) solves.Append(solve.ResultOf(i)).Append(',');
                    solves.Append('#');
                }
                string ds = Digest(scenes), dv = Digest(solves);
                Console.WriteLine($"    end-state digests: scenes {ds}, solves {dv} ({scenes.Length} + {solves.Length} chars)");
                Assert(ds == "4F4C67DF05591EC5", $"the pulse scenes no longer end where the kernel before ended them (digest {ds})");
                Assert(solved == 3000, $"only {solved} of 3000 random solves conserved (sanity probe)");
                Assert(dv == "3715D3FBB88120C5", $"the level solves no longer give what the solver before gave (digest {dv})");
            });
            Case("ExcavationTick_grid_walk_equals_generic", () =>
            {
                var r = new Random(7);
                int capped = 0;
                for (int t = 0; t < 400; t++)
                {
                    int w = r.Next(1, 25), h = r.Next(1, 25), n = w * h;
                    var kind = new int[n];   // 0 rock, 1 dug, 2 source
                    for (int i = 0; i < n; i++) kind[i] = r.Next(10) < 6 ? 1 : r.Next(3) == 0 ? 2 : 0;
                    var trace = new System.Text.StringBuilder();   // the predicate calls, in order (the live predicates read the map)
                    Predicate<int> isSrc = i => { trace.Append('s').Append(i).Append(','); return kind[i] == 2; };
                    Predicate<int> isExc = i => { trace.Append('e').Append(i).Append(','); return kind[i] == 1; };
                    var kernel = new RM_FlowKernel(w, h);
                    var gVisited = new HashSet<int>(); var gSources = new HashSet<int>(); var gQueue = new Queue<int>();
                    var gScratch = new List<int>(); var gComp = new List<int>();
                    var sVisited = new RM_StampSet(); var sSources = new RM_StampSet(); var sQueue = new List<int>(); var sComp = new List<int>();
                    sVisited.Reset(n);
                    int cap = r.Next(3) == 0 ? int.MaxValue : r.Next(1, 40);
                    for (int seed = 0; seed < n; seed++)
                    {
                        if (kind[seed] != 1 || gVisited.Contains(seed)) continue;
                        trace.Clear();
                        RM_StockMath.CollectComponent(seed, isSrc, isExc, kernel.CardinalInBounds, gVisited, gSources, gQueue, gScratch, gComp, cap);
                        string gTrace = trace.ToString();
                        trace.Clear();
                        RM_FlowKernel.CollectComponentGrid(seed, isSrc, isExc, w, h, sVisited, sSources, sQueue, sComp, cap);
                        Assert(string.Join(",", gComp) == string.Join(",", sComp), $"case {t} seed {seed}: the grid walk's component differs");
                        Assert(gTrace == trace.ToString(), $"case {t} seed {seed}: the grid walk asks the predicates in another order");
                        for (int i = 0; i < n; i++)
                        {
                            Assert(gVisited.Contains(i) == sVisited.Contains(i), $"case {t} seed {seed}: the visited sets differ at {i}");
                            Assert(gSources.Contains(i) == sSources.Contains(i), $"case {t} seed {seed}: the source sets differ at {i}");
                        }
                        if (sComp.Count >= cap) capped++;
                    }
                }
                Assert(capped > 50, "no walk hit its cap (sanity probe)");
            });
            Case("ExcavationTick_sliced_pulse_equals_atomic", () =>
            {
                int multi = 0, rotatedSliced = 0;
                for (int seed = 0; seed < 200; seed++)
                {
                    bool exact = seed % 4 != 3;
                    var (atomW, seeds) = PulseScene(seed, exact);
                    var (sliceW, _) = PulseScene(seed, exact);
                    var r = new Random(seed * 31 + 5);
                    for (int p = 0; p < 20; p++)
                    {
                        atomW.Pulse(seeds);
                        int slices = SlicedPulse(sliceW, seeds, 60, r);
                        if (slices > 1) multi++;
                        Assert(PulseSnap(atomW) == PulseSnap(sliceW), $"seed {seed} pulse {p} ({slices} slices): sliced differs from atomic");
                    }
                    if (sliceW.k.rotatedNetworks > 0) rotatedSliced++;
                }
                Console.WriteLine($"    200 scenes x 20 pulses equal: {multi} pulses ran in more than one slice, {rotatedSliced} scenes rotated");
                Assert(multi > 500 && rotatedSliced > 10, "the slices were not exercised (sanity probe)");
            });
            Case("ExcavationTick_sliced_pulse_survives_digs_between_slices", () =>
            {
                int changed = 0;
                long resolvedAll = 0;
                for (int seed = 0; seed < 150; seed++)
                {
                    var (aw, seeds) = PulseScene(seed, seed % 3 != 2);
                    var cw = new CountingWorld(aw);
                    aw.k.world = cw;
                    var r = new Random(seed + 991);
                    int n = aw.w * aw.h;
                    for (int p = 0; p < 15; p++)
                    {
                        cw.pulse = aw.pulse + 1;
                        SlicedPulse(aw, seeds, 40, r, () =>
                        {
                            // a dig (dry) or a fill-in (its water gone with the square) between two slices
                            int i = r.Next(n);
                            if (aw.natural[i]) return;
                            if (aw.k.depth[i] == 0) aw.k.depth[i] = (byte)r.Next(1, 5);
                            else { aw.k.depth[i] = 0; aw.k.fill[i] = 0; if (aw.k.part != null) aw.k.part[i] = 0; aw.cellFluid[i] = null; }
                            changed++;
                        });
                        Assert(cw.twice == 0, $"seed {seed} pulse {p}: a square was resolved twice in one pulse");
                        Assert(aw.k.worstImbalance == 0, $"seed {seed} pulse {p}: ledger {string.Join("; ", aw.k.imbalanceReports)}");
                        for (int i = 0; i < n; i++)
                        {
                            Assert(aw.k.fill[i] <= aw.k.depth[i], $"seed {seed} pulse {p}: F > D at {i}");
                            Assert(aw.k.part == null || aw.k.part[i] == 0 || aw.k.fill[i] < aw.k.depth[i], $"seed {seed} pulse {p}: water above the brim at {i}");
                        }
                        seeds.Clear();
                        for (int i = 0; i < n; i++) if (aw.k.depth[i] > 0) seeds.Add(i);
                    }
                    resolvedAll += cw.resolved;
                }
                Assert(changed > 1000 && resolvedAll > 10000, $"the map barely changed between slices ({changed}) or nothing resolved ({resolvedAll}) (sanity probe)");
            });
            Case("ExcavationTick_pulse_cost_bound_325", () =>
            {
                // The live r11 shape: two 125x320 basins (80,000 dug squares, one network each, depth 4, one full and one
                // nearly dry) on a 325x325 map at the shipped cap (6000) with moving seams; 100 squares a pulse carried
                // from one to the other keep every pulse doing real work.
                const int w = 325, h = 325;
                ArrayWorld Make()
                {
                    var aw = new ArrayWorld(w, h);
                    var k = aw.k;
                    k.levelExactEnabled = true; k.maxComponentCells = 6000; k.seamRotationEnabled = true; k.levelBySurfaceEnabled = true;
                    k.levelSetEnabled = true; k.creepWaterEnabled = true; k.viscosityEnabled = true; k.creepEnabled = true; k.flowPerPulse = 1;
                    k.part = new ushort[w * h];
                    for (int z = 2; z <= 321; z++)
                        for (int x = 10; x <= 314; x++)
                        {
                            bool a = x <= 134, b = x >= 190;
                            if (!a && !b) continue;
                            int i = z * w + x;
                            k.depth[i] = 4; k.fill[i] = (byte)(a ? 4 : 1); aw.cellFluid[i] = ArrayWorld.Water;
                        }
                    return aw;
                }
                void Carry(ArrayWorld aw)
                {
                    for (int q = 0; q < 100; q++)
                    {
                        int ia = (4 + q * 3) * w + 134, ib = (6 + q * 3) * w + 190;
                        if (aw.k.fill[ia] > 0) { aw.k.fill[ia]--; aw.k.fill[ib]++; }
                    }
                }
                var atom = Make();
                var sliced = Make();
                var seeds = new List<int>();
                for (int i = 0; i < w * h; i++) if (atom.k.depth[i] > 0) seeds.Add(i);
                double atomMax = 0, atomSum = 0, stepMax = 0, stepSum = 0;
                long cellMax = 0;
                int steps = 0;
                for (int p = 1; p <= 10; p++)
                {
                    Carry(atom); Carry(sliced);
                    var sw = Stopwatch.StartNew();
                    atom.Pulse(seeds);
                    double ms = sw.Elapsed.TotalMilliseconds;
                    if (p > 1) { atomMax = Math.Max(atomMax, ms); atomSum += ms; }
                    sliced.pulse++;
                    sliced.k.BeginPulse(seeds, sliced.pulse);
                    bool done;
                    do
                    {
                        sw.Restart();
                        done = sliced.k.StepPulse(RM_FlowKernel.DefaultSliceCells);
                        ms = sw.Elapsed.TotalMilliseconds;
                        if (p > 1) { stepMax = Math.Max(stepMax, ms); stepSum += ms; steps++; }
                        cellMax = Math.Max(cellMax, sliced.k.lastStepCells);
                    } while (!done);
                    sliced.Sync();
                    Assert(PulseSnap(atom) == PulseSnap(sliced), $"pulse {p}: sliced differs from atomic on the 325x325 map");
                }
                Console.WriteLine($"    325x325, 80,000 dug: atomic pulse mean {atomSum / 9:F1} ms max {atomMax:F1}; sliced {steps / 9.0:F1} slices a pulse, "
                    + $"slice mean {stepSum / Math.Max(1, steps):F2} ms max {stepMax:F1} ms, most cells in one slice {cellMax}");
                // The deterministic bound: a slice stops after the unit that crosses the budget, and the largest unit is one
                // network's uncapped walk (40,000 squares here) after at most one capped walk.
                Assert(cellMax <= RM_FlowKernel.DefaultSliceCells + 6000 + 40000, $"a slice walked or resolved {cellMax} cells");
                // Wall time, generous (CoreCLR here; the game's Mono is slower): the unsliced pulse measured 25-90 ms here.
                Assert(stepMax < 40, $"one slice took {stepMax:F1} ms");
            });
            Case("ExcavationTick_edge_drain_picture_writes_budgeted_325", () =>
            {
                // Live r12 (161 ms in one slice): the perf scene's basins run z 2..321, inside the 10-square edge band, and the
                // game's edge sinks are on by default, so both drain off the map; with moving seams the water near the edge swings
                // about half a level each pulse, and every square whose look band changes is one SetTerrain (about 25 us live).
                // The pulse's picture writes go through RM_TerrainWriteBudget: per tick at most WritesPerTick, the rest drained on
                // later ticks, and the final picture equals the unbudgeted one before the next pulse.
                const int w = 325, h = 325, edge = 10, pulseTicks = 250;
                var aw = new ArrayWorld(w, h);
                var k = aw.k;
                k.levelExactEnabled = true; k.maxComponentCells = 6000; k.seamRotationEnabled = true; k.levelBySurfaceEnabled = true;
                k.levelSetEnabled = true; k.creepWaterEnabled = true; k.viscosityEnabled = true; k.creepEnabled = true; k.flowPerPulse = 1;
                k.part = new ushort[w * h];
                k.edgeSinksEnabled = true;
                var seeds = new List<int>();
                for (int z = 2; z <= 321; z++)
                    for (int x = 10; x <= 314; x++)
                    {
                        bool a = x <= 134, b = x >= 190;
                        if (!a && !b) continue;
                        int i = z * w + x;
                        k.depth[i] = 4; k.fill[i] = (byte)(a ? 4 : 1); aw.cellFluid[i] = ArrayWorld.Water; seeds.Add(i);
                        aw.sink[i] = x < edge || z < edge || x >= w - edge || z >= h - edge;
                    }
                int Band(int i) => k.depth[i] == 0 ? -1 : RM_LevelSolve.LookBand(k.fill[i] * (long)RM_LevelSolve.U + k.part[i]);
                var drawn = new int[w * h];
                foreach (int i in seeds) drawn[i] = Band(i);
                var budget = new RM_TerrainWriteBudget();
                long tick = 0;
                int maxWritesTick = 0, maxChangesSlice = 0, changesTotal = 0, deferredMax = 0;
                // The adapter's ApplyFillTerrain(budgeted): no write when the picture already matches; else a write if the tick
                // has one left, else the square waits.
                bool Apply(int i)
                {
                    int want = Band(i);
                    if (drawn[i] == want) return true;
                    if (!budget.TryTakeWrite(tick)) { budget.Defer(i, w * h); return false; }
                    drawn[i] = want;
                    return true;
                }
                var world = new ResolvedHook(aw, comp => { int n = 0; foreach (int i in comp) { if (k.depth[i] == 0) continue; if (drawn[i] != Band(i)) n++; Apply(i); } changesTotal += n; maxChangesSlice = Math.Max(maxChangesSlice, n); });
                k.world = world;
                for (int p = 1; p <= 8; p++)
                {
                    aw.pulse++;
                    long pulseStart = tick;
                    k.BeginPulse(seeds, aw.pulse);
                    bool done = false;
                    for (; tick < pulseStart + pulseTicks; tick++)
                    {
                        budget.Drain(RM_TerrainWriteBudget.JudgedPerTick, Apply);   // MapComponentTick drains first
                        if (!done && (done = k.StepPulse(RM_FlowKernel.DefaultSliceCells))) aw.Sync();
                        maxWritesTick = Math.Max(maxWritesTick, budget.WritesThisTick);
                        deferredMax = Math.Max(deferredMax, budget.Count);
                    }
                    Assert(done, $"pulse {p} did not finish in {pulseTicks} ticks");
                    Assert(budget.Count == 0, $"pulse {p}: {budget.Count} squares still wait for their picture when the next pulse is due");
                    foreach (int i in seeds) Assert(drawn[i] == Band(i), $"pulse {p}: square {i} shows band {drawn[i]}, its water says {Band(i)}");
                }
                Console.WriteLine($"    325x325 draining down the edge: {changesTotal} picture changes in 8 pulses, at most {maxChangesSlice} in one slice; "
                    + $"budgeted at most {maxWritesTick} a tick, at most {deferredMax} waiting");
                // The instrument can see: this scene is the churn the budget exists for (thousands per slice unbudgeted).
                Assert(maxChangesSlice > 10 * RM_TerrainWriteBudget.WritesPerTick, $"the scene changed only {maxChangesSlice} pictures in a slice: it no longer exercises the budget");
                Assert(maxWritesTick <= RM_TerrainWriteBudget.WritesPerTick, $"{maxWritesTick} picture writes in one tick");
                // A square waits once, however often its pulse resolves it.
                var once = new RM_TerrainWriteBudget();
                once.Defer(5, 100); once.Defer(5, 100); once.Defer(7, 100);
                Assert(once.Count == 2, $"a square deferred twice waits twice ({once.Count})");
            });
            Case("ExcavationTick_label_scratch_equals_reference", () =>
            {
                // EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: the rewritten floods (per-thread queue and tallies, a reused label array,
                // ramp pairs read only for a refused step, no div/mod per cell) equal the r13 floods on random grids: every
                // size down to one square wide, every band, every class, ramps or none, a reused array full of garbage or of
                // the wrong length.
                var rng = new Random(1414);
                int checkedCells = 0, reused = 0;
                for (int t = 0; t < 600; t++)
                {
                    int w = 1 + rng.Next(t % 7 == 0 ? 3 : 40), h = 1 + rng.Next(t % 5 == 0 ? 3 : 40), n = w * h;
                    var depth = new byte[n];
                    var kind = new byte[n];
                    int deep = 1 + rng.Next(9);
                    for (int i = 0; i < n; i++)
                    {
                        depth[i] = (byte)(rng.Next(3) == 0 ? 0 : rng.Next(deep));
                        kind[i] = KindPool[rng.Next(KindPool.Length)];
                    }
                    Dictionary<int, int> ramps = null;
                    if (rng.Next(2) == 0)
                    {
                        ramps = new Dictionary<int, int>();
                        for (int q = rng.Next(n / 4 + 1); q > 0; q--)
                        {
                            int a = rng.Next(n), b = rng.Next(4) switch { 0 => a + 1, 1 => a - 1, 2 => a + w, _ => a - w };
                            if (b >= 0 && b < n) ramps[a] = b;
                        }
                    }
                    Func<int, int, bool> joins = ramps == null ? null : (Func<int, int, bool>)((a, b) => ramps.TryGetValue(a, out int to) && to == b);
                    int k = rng.Next(RM_PitTrapMath.ClimbBands + 1);
                    int[] Garbage(int len) { var g = new int[len]; for (int i = 0; i < len; i++) g[i] = rng.Next(-3, 50); return g; }
                    int[] reuse = rng.Next(3) == 0 ? null : Garbage(rng.Next(4) == 0 ? n + 1 : n);
                    RM_PocketGridMath.Labels want = RefPocketLabel(depth, w, h, k, joins), got = RM_PocketGridMath.Label(depth, w, h, k, joins, reuse);
                    Assert(SameLabels(want, got) && got.surface.Length == got.count && got.size.Length == got.count && got.width == w && got.height == h,
                        $"case {t} ({w}x{h}, k {k}): the pocket labels differ from the reference");
                    if (reuse != null && reuse.Length == n) { Assert(ReferenceEquals(got.label, reuse), $"case {t}: the reused array was not used"); reused++; }
                    int cls = rng.Next(RM_WallReachMath.ClassCount);
                    byte[] wd = rng.Next(4) == 0 ? null : depth;
                    reuse = rng.Next(3) == 0 ? null : Garbage(rng.Next(4) == 0 ? n - 1 : n);
                    RM_WallReachMath.Labels wantW = RefWallLabel(kind, wd, w, h, k, cls, joins), gotW = RM_WallReachMath.Label(kind, wd, w, h, k, cls, joins, reuse);
                    Assert(SameLabels(wantW, gotW) && gotW.k == k && gotW.cls == cls, $"case {t} ({w}x{h}, k {k}, cls {cls}): the wall-reach labels differ from the reference");
                    if (reuse != null && reuse.Length == n) { Assert(ReferenceEquals(gotW.label, reuse), $"case {t}: the reused wall array was not used"); reused++; }
                    checkedCells += 2 * n;
                }
                // The instrument can see: a one-cell change in the rewrite's rule would show here (a sanity probe on the
                // comparison itself: a refused step joined by hand differs).
                var probe = RM_PocketGridMath.Label(new byte[] { 0, 5 }, 2, 1, 1);
                Assert(!SameLabels(probe, RM_PocketGridMath.Label(new byte[] { 0, 5 }, 2, 1, 1, (a, b) => true)), "a ramp join does not change the labels (sanity probe)");
                Assert(checkedCells > 200000 && reused > 500, $"too little compared ({checkedCells} cells, {reused} reused)");
                Console.WriteLine($"    {checkedCells} cell labels equal the r13 floods, {reused} through a reused array");
            });
            Case("ExcavationTick_alloc_per_tick_325", () =>
            {
                // EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES (r14): bytes the hot paths allocate, measured on this thread
                // (GC.GetAllocatedBytesForCurrentThread). The game's heap is ~3.6 GB and a full collection ~1.2 s, so every
                // byte allocated here brings the next one closer. Per-tick figures use the live rates: one pulse per
                // 250 ticks, ~3 pocket-grid rebuilds (6 bands each) and ~12 wall-reach labellings per 1000 ticks (r11/r12).
                const int w = 325, h = 325, pulseTicks = 250;
                foreach (bool sinks in new[] { false, true })
                {
                    var aw = new ArrayWorld(w, h);
                    var k = aw.k;
                    k.levelExactEnabled = true; k.maxComponentCells = 6000; k.seamRotationEnabled = true; k.levelBySurfaceEnabled = true;
                    k.levelSetEnabled = true; k.creepWaterEnabled = true; k.viscosityEnabled = true; k.creepEnabled = true; k.flowPerPulse = 1;
                    k.part = new ushort[w * h];
                    k.edgeSinksEnabled = sinks;
                    var seeds = new List<int>();
                    for (int z = 2; z <= 321; z++)
                        for (int x = 10; x <= 314; x++)
                        {
                            bool a = x <= 134, b = x >= 190;
                            if (!a && !b) continue;
                            int i = z * w + x;
                            k.depth[i] = 4; k.fill[i] = (byte)(a ? 4 : 1); aw.cellFluid[i] = ArrayWorld.Water; seeds.Add(i);
                            aw.sink[i] = x < 10 || z < 10 || x >= w - 10 || z >= h - 10;
                        }
                    long bytes = 0;
                    double ms = 0;
                    for (int p = 1; p <= 6; p++)
                    {
                        for (int q = 0; q < 100; q++)
                        {
                            int ia = (4 + q * 3) * w + 134, ib = (6 + q * 3) * w + 190;
                            if (k.fill[ia] > 0) { k.fill[ia]--; k.fill[ib]++; }
                        }
                        aw.pulse++;
                        long before = GC.GetAllocatedBytesForCurrentThread();
                        var sw = Stopwatch.StartNew();
                        k.BeginPulse(seeds, aw.pulse);
                        while (!k.StepPulse(RM_FlowKernel.DefaultSliceCells)) { }
                        double one = sw.Elapsed.TotalMilliseconds;
                        long got = GC.GetAllocatedBytesForCurrentThread() - before;
                        aw.Sync();
                        if (p > 1) { bytes += got; ms += one; }   // pulse 1 sizes the reused scratch
                    }
                    Console.WriteLine($"    kernel pulse (sinks {(sinks ? "on" : "off")}): {bytes / 5 / 1024.0:F1} KB a pulse = {bytes / 5.0 / pulseTicks:F0} B/tick; "
                        + $"{ms / 5:F1} ms a pulse");
                }
                // A dug 325x325 view: the two basins at 4, terraced slopes, scattered deep holes, a few ramps.
                var depth = new byte[w * h];
                var rng = new Random(14);
                for (int z = 2; z <= 321; z++)
                    for (int x = 10; x <= 314; x++)
                    {
                        if (x > 134 && x < 190) depth[z * w + x] = (byte)Math.Min(6, Math.Abs(x - 162) / 5);
                        else depth[z * w + x] = 4;
                    }
                for (int q = 0; q < 400; q++) depth[rng.Next(w * h)] = (byte)rng.Next(0, 9);
                var ramps = new Dictionary<int, int>();
                for (int q = 0; q < 40; q++) { int a = rng.Next(w, w * h - w); ramps[a] = a + w; }
                Func<int, int, bool> joins = (a, b) => ramps.TryGetValue(a, out int t) && t == b;   // RM_PocketGrid.RampJoinsOf
                var kind = new byte[w * h];
                for (int q = 0; q < 3000; q++) kind[rng.Next(w * h)] = RM_WallReachMath.Wall;
                int bands = RM_PitTrapMath.ClimbBands;
                // As RM_PocketGrid.Build and RM_WallReach.Build call them: each rebuild overwrites the arrays of the one before last.
                var spare = new RM_PocketGridMath.Labels[bands];
                for (int band = 1; band < bands; band++) spare[band] = RM_PocketGridMath.Label(depth, w, h, band, joins);   // warm (JIT, scratch)
                RM_WallReachMath.Labels wspare = RM_WallReachMath.Label(kind, depth, w, h, 1, 0, joins);
                long b0 = GC.GetAllocatedBytesForCurrentThread();
                var swp = Stopwatch.StartNew();
                for (int band = 1; band < bands; band++) RM_PocketGridMath.Label(depth, w, h, band, joins, spare[band].label);
                double pgMs = swp.Elapsed.TotalMilliseconds;
                long pg = GC.GetAllocatedBytesForCurrentThread() - b0;
                b0 = GC.GetAllocatedBytesForCurrentThread();
                swp.Restart();
                RM_WallReachMath.Label(kind, depth, w, h, 2, 0, joins, wspare.label);
                double wrMs = swp.Elapsed.TotalMilliseconds;
                long wr = GC.GetAllocatedBytesForCurrentThread() - b0;
                Console.WriteLine($"    pocket grid rebuild ({bands - 1} bands): {pg / 1024.0:F0} KB, {pgMs:F1} ms = {pg * 3 / 1000.0:F0} B/tick at 3/1000; "
                    + $"wall-reach labelling: {wr / 1024.0:F0} KB, {wrMs:F1} ms = {wr * 12 / 1000.0:F0} B/tick at 12/1000");
                // r13 allocated ~4,970 KB a pocket rebuild and ~825 KB a wall-reach labelling (two int[n] per flood); the double
                // buffer leaves only the per-label tallies and the result objects.
                Assert(pg < 64 * 1024 && wr < 4 * 1024, $"a rebuild still allocates {pg / 1024} KB (pocket) / {wr / 1024} KB (wall reach)");
                Assert(pgMs > 0 && wrMs > 0, "the floods took no time (sanity probe)");
            });
        }

        /// <summary>ArrayWorld with a hook on ComponentResolved (the adapter's RenderComponentFill).</summary>
        private sealed class ResolvedHook : RM_IFlowWorld, RM_ILevelWorld
        {
            private readonly ArrayWorld a;
            private readonly Action<List<int>> resolved;
            public ResolvedHook(ArrayWorld a, Action<List<int>> resolved) { this.a = a; this.resolved = resolved; }
            public bool IsNaturalLiquid(int idx) => a.IsNaturalLiquid(idx);
            public bool CanSupply(int idx) => a.CanSupply(idx);
            public bool TryDebitLevel(int idx) => a.TryDebitLevel(idx);
            public object DonorFluid(int idx, bool source) => a.DonorFluid(idx, source);
            public object CellFluid(int idx) => a.CellFluid(idx);
            public void Claim(int idx, object fluid) => a.Claim(idx, fluid);
            public bool CanClaim(object fluid) => a.CanClaim(fluid);
            public int TicksPerTile(object fluid) => a.TicksPerTile(fluid);
            public bool IsSink(int idx) => a.IsSink(idx);
            public void ComponentResolved(List<int> component) => resolved(component);
            public int LevelBodyOf(int src) => a.LevelBodyOf(src);
            public long BodyStockDl(int body) => a.BodyStockDl(body);
            public void SetBodyStockDl(int body, long dl) => a.SetBodyStockDl(body, dl);
            public int[] BodyHistogram(int body) => a.BodyHistogram(body);
            public int BedAt(int src) => a.BedAt(src);
            public void NoteLimitlessDl(object fluid, long dl) => a.NoteLimitlessDl(fluid, dl);
        }

        // ── EXCAVATION_RAIN_TAME_ONE_TICK_DELUGE: the exact rain pass (RM_MapComponent_Excavation.LandRain) and pocket rain ──

        /// <summary>The adapter's LandRain, rule for rule, on an ArrayWorld square (roof first; a brimming water square runs
        /// its notches over the lip; another liquid takes none; a dry square is claimed). Returns the dL run over.</summary>
        private static long ExactRainSquare(ArrayWorld aw, int i, int levels, bool[] roof, ref long landedDl)
        {
            var k = aw.k; int U = RM_LevelSolve.U;
            if (k.depth[i] == 0 || roof[i]) return 0;
            long w = k.part != null ? k.WaterOf(i) : k.fill[i] * (long)U;
            long roomDl = k.depth[i] * (long)U - w;
            int room = roomDl <= 0 ? 0 : (int)(roomDl / U);
            bool wet = w > 0;
            if (room <= 0) return wet && aw.cellFluid[i] == ArrayWorld.Water ? levels * (long)U : 0;
            if (wet && aw.cellFluid[i] != ArrayWorld.Water) return 0;
            int add = room < levels ? room : levels;
            if (!wet) aw.cellFluid[i] = ArrayWorld.Water;
            k.fill[i] += (byte)add;
            landedDl += add * (long)U;
            return (levels - add) * (long)U;
        }

        /// <summary>Deep pits with room (depth 3-12, a little water or tar, no ponds), random kernel switches: rain below the brim.</summary>
        private static (ArrayWorld w, List<int> seeds) RainScene(int seed, bool exact)
        {
            var r = new Random(seed * 101 + 9);
            int w = r.Next(10, 31), h = r.Next(10, 31), n = w * h;
            var aw = new ArrayWorld(w, h);
            var k = aw.k;
            k.levelExactEnabled = exact;
            k.part = exact ? new ushort[n] : null;
            k.levelBySurfaceEnabled = r.Next(4) != 0;
            k.levelSetEnabled = k.levelBySurfaceEnabled && r.Next(2) == 0;
            k.viscosityEnabled = r.Next(2) == 0;
            k.creepEnabled = k.viscosityEnabled && r.Next(2) == 0;
            k.creepWaterEnabled = r.Next(2) == 0;
            k.flowPerPulse = r.Next(1, 3);
            k.seamRotationEnabled = r.Next(4) != 0;
            k.maxComponentCells = r.Next(12, 120);
            k.edgeSinksEnabled = r.Next(3) == 0;
            if (k.edgeSinksEnabled) for (int i = 0; i < n; i++) aw.sink[i] = i % w == 0 || i / w == 0;
            var seeds = new List<int>();
            int digs = r.Next(2, 7);
            for (int d = 0; d < digs; d++)
            {
                int x0 = r.Next(w), z0 = r.Next(h), bw = r.Next(1, 12), bh = r.Next(1, 12), depth = r.Next(3, 13);
                Fluid f = r.Next(5) == 0 ? ArrayWorld.Tar : ArrayWorld.Water;
                for (int x = x0; x < Math.Min(w, x0 + bw); x++)
                    for (int z = z0; z < Math.Min(h, z0 + bh); z++)
                    {
                        int i = z * w + x;
                        if (k.depth[i] == 0) seeds.Add(i);
                        k.depth[i] = (byte)depth;
                        int fill = r.Next(3);
                        k.fill[i] = (byte)fill;
                        aw.cellFluid[i] = fill > 0 ? f : null;
                    }
            }
            aw.Sync();
            return (aw, seeds);
        }

        /// <summary>Copies the water state of <paramref name="from"/> into <paramref name="to"/> (same scene).</summary>
        private static void Resync(ArrayWorld from, ArrayWorld to)
        {
            Array.Copy(from.k.fill, to.k.fill, from.k.fill.Length);
            if (from.k.part != null) Array.Copy(from.k.part, to.k.part, from.k.part.Length);
            Array.Copy(from.cellFluid, to.cellFluid, from.cellFluid.Length);
            for (int b = 0; b < from.bodies.Count; b++) to.bodies[b].SetDl(from.bodies[b].Dl());
            to.externalIn.Clear();
            foreach (var kv in from.externalIn) to.externalIn[kv.Key] = kv.Value;
        }

        private static void ArmPocketRain(ArrayWorld aw, bool[] roof, Action<long> onOffer)
        {
            aw.k.rainFluid = ArrayWorld.Water;
            aw.k.rainCatches = i => !roof[i];
            aw.k.rainOverflow = (i, dl, f) => onOffer(dl);
        }

        /// <summary>RAIN_REVIEW_FIX_SLUICES_AND_OVERFILL: a 1-row scene, row 1 of a W x 3 grid, each square (depth, notches, part dL,
        /// fluid or null, roofed, sealed).</summary>
        private static ArrayWorld RowScene(bool exact, (byte d, byte f, ushort part, Fluid fl, bool roof, bool shut)[] row, out bool[] roof, out List<int> seeds)
        {
            int w = row.Length + 2;
            var aw = new ArrayWorld(w, 3);
            aw.k.levelExactEnabled = exact;
            aw.k.part = new ushort[w * 3];
            aw.k.levelBySurfaceEnabled = true;
            var r = new bool[w * 3];
            var shut = new bool[w * 3];
            seeds = new List<int>();
            for (int x = 0; x < row.Length; x++)
            {
                int i = 1 * w + x + 1;
                aw.k.depth[i] = row[x].d; aw.k.fill[i] = row[x].f; aw.k.part[i] = row[x].part;
                aw.cellFluid[i] = row[x].fl; r[i] = row[x].roof; shut[i] = row[x].shut;
                seeds.Add(i);
            }
            aw.k.sealedCell = i => shut[i];
            roof = r;
            return aw;
        }

        private static void RainReviewCases(Action<string, Action> Case)
        {
            const ushort U = (ushort)RM_LevelSolve.U;
            Case("Rain_review_exact_off_never_overfills_or_converts", () =>
            {
                // HIGH: exact-level water switched off. A square holding only a part-notch (fill 0) is not dry: the whole-notch
                // kernel must neither pour a notch on top of it (fill 1 + part on a depth-1 square overfills) nor claim it for
                // another liquid (the tar became water). The water stays where it is, nothing created or lost.
                int runs = 0;
                foreach (bool bySurface in new[] { false, true })
                    foreach (bool set in new[] { false, true })
                        foreach (bool creep in new[] { false, true })
                        {
                            var aw = RowScene(false, new[] {
                                ((byte)1, (byte)1, (ushort)0, ArrayWorld.Water, false, false),
                                ((byte)1, (byte)0, (ushort)(U / 2), ArrayWorld.Tar, false, false),
                                ((byte)1, (byte)0, (ushort)(U / 2), ArrayWorld.Water, false, false),
                                ((byte)2, (byte)1, (ushort)(U / 3), ArrayWorld.Water, false, false),
                                ((byte)1, (byte)1, (ushort)0, ArrayWorld.Water, false, false) }, out _, out var seeds);
                            aw.k.levelBySurfaceEnabled = bySurface; aw.k.levelSetEnabled = bySurface && set;
                            aw.k.creepWaterEnabled = creep; aw.k.flowPerPulse = 2;
                            long Total() { long t = 0; foreach (int i in seeds) t += aw.k.WaterOf(i); return t; }
                            long before = Total();
                            int tar = seeds[1];
                            for (int p = 0; p < 12; p++)
                            {
                                aw.Pulse(seeds);
                                foreach (int i in seeds)
                                    Assert(aw.k.WaterOf(i) <= aw.k.depth[i] * (long)U, $"surface {bySurface} set {set} creep {creep} pulse {p}: square {i} holds {aw.k.WaterOf(i)} dL over its brim {aw.k.depth[i] * (long)U}");
                                Assert(ReferenceEquals(aw.cellFluid[tar], ArrayWorld.Tar) && aw.k.WaterOf(tar) == U / 2, $"surface {bySurface} set {set} creep {creep} pulse {p}: the tar part-notch became {aw.k.WaterOf(tar)} dL of {(aw.cellFluid[tar] as Fluid)?.name}");
                                Assert(Total() == before, $"surface {bySurface} set {set} creep {creep} pulse {p}: water {before} -> {Total()} dL");
                            }
                            runs++;
                        }
                Assert(runs == 8, "every notch-kernel variant ran");
            });
            Case("Rain_review_due_pulse_lands_a_bounded_slice_and_waits", () =>
            {
                // MED: the 4,000-square slice was not a bound at the pulse's due tick. The first fallback pulse (no lead window),
                // or a pass a long pulse in flight kept from starting, landed every owed square in that one tick. Now the due
                // pulse waits: each tick lands at most a slice (RM_RainPass.HoldsPulse) until the rest fits in the pulse tick.
                foreach (int squares in new[] { 0, 1, RM_RainPass.CellsPerTick, RM_RainPass.CellsPerTick + 1, 80_000, 104_001 })
                {
                    var pass = new RM_RainPass();
                    pass.Begin(2);
                    for (int i = 0; i < squares; i++) pass.Add(i);
                    int landedNow = 0, worst = 0, waits = 0, total = 0;
                    Action<int, int> land = (i, lv) => landedNow++;
                    while (pass.HoldsPulse(land))
                    {
                        worst = Math.Max(worst, landedNow); total += landedNow; landedNow = 0; waits++;
                        Assert(waits < 1000, "the wait ends");
                    }
                    total += landedNow; worst = Math.Max(worst, landedNow); landedNow = 0;
                    pass.Step(int.MaxValue, land);   // the pulse tick lands the rest (ApplyRain's LandRainOwed)
                    worst = Math.Max(worst, landedNow); total += landedNow;
                    Assert(worst <= RM_RainPass.CellsPerTick, $"{squares} squares: a tick landed {worst}");
                    Assert(total == squares, $"{squares} squares: landed {total}");
                    int want = squares <= RM_RainPass.CellsPerTick ? 0 : (squares - 1) / RM_RainPass.CellsPerTick;
                    Assert(waits == want, $"{squares} squares: waited {waits} ticks, want {want}");
                }
                // The Verse-bound call site: the due pulse asks before it starts (after any pulse in flight has ended).
                string src = System.Text.RegularExpressions.Regex.Replace(RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs"), @"\s+", " ");
                Assert(System.Text.RegularExpressions.Regex.IsMatch(src, @"ContinuePulse\(int\.MaxValue\); \} if \(RainPassHoldsPulse\(\)\) \{ return; \} pulseDueTick = nextPulseTick;"),
                    "Tick: the due pulse waits on RainPassHoldsPulse before it starts");
                Assert(System.Text.RegularExpressions.Regex.IsMatch(src, @"bool RainPassHoldsPulse\(\) \{ if \(!RimMandrakeFlowWorksSettings\.rainPocketApproxEnabled && rainDecidedForPulse != nextPulseTick\) \{ DecideRain\(nextPulseTick\); \}"),
                    "RainPassHoldsPulse decides the fallback pass for the due pulse (the first pulse has no lead window)");
            });
            Case("Rain_review_pocket_rain_stops_at_a_shut_sluice_and_foreign_liquid", () =>
            {
                // MED: what a brimming open square cannot hold runs only through squares water can pass: never across a shut
                // sluice (liquid neither enters nor leaves) or a square of another liquid. The roofed water beyond stays put; the
                // pocket's surplus runs over the lip instead.
                foreach (bool exact in new[] { true, false })
                    foreach (bool tarWall in new[] { false, true })
                    {
                        var aw = RowScene(exact, new[] {
                            ((byte)1, (byte)1, (ushort)0, ArrayWorld.Water, false, false),
                            ((byte)1, tarWall ? (byte)1 : (byte)0, (ushort)0, tarWall ? ArrayWorld.Tar : null, true, !tarWall),
                            ((byte)2, (byte)1, (ushort)0, ArrayWorld.Water, true, false) }, out var roof, out var seeds);
                        long offered = 0;
                        ArmPocketRain(aw, roof, dl => offered += dl);
                        aw.k.rainNotches = 1;
                        aw.Pulse(seeds);
                        string tag = $"exact {exact} {(tarWall ? "tar square" : "shut sluice")}";
                        Assert(aw.k.WaterOf(seeds[2]) == U, $"{tag}: the water beyond took rain: {aw.k.WaterOf(seeds[2])} dL");
                        Assert(aw.k.WaterOf(seeds[1]) == (tarWall ? U : 0), $"{tag}: the barrier square changed: {aw.k.WaterOf(seeds[1])} dL");
                        Assert(offered == U && aw.k.rainLandedDl == 0, $"{tag}: offered {offered} dL, landed {aw.k.rainLandedDl}");
                    }
            });
            Case("CsReview_pocket_rain_each_run_keeps_its_own_surplus", () =>
            {
                // cs_review F2 (red-first): two brimming open squares of one pocket parted by a shut sluice. Each run's surplus
                // stays in its run: the right one's notch fills the roofed deep square beside it, the left one's (no room on its
                // side) runs over the lip. Was: one pooled balance, so the left notch crossed the sluice too.
                foreach (bool exact in new[] { true, false })
                {
                    var aw = RowScene(exact, new[] {
                        ((byte)1, (byte)1, (ushort)0, ArrayWorld.Water, false, false),
                        ((byte)1, (byte)0, (ushort)0, (Fluid)null, true, true),
                        ((byte)1, (byte)1, (ushort)0, ArrayWorld.Water, false, false),
                        ((byte)2, (byte)0, (ushort)0, (Fluid)null, true, false) }, out var roof, out var seeds);
                    long offered = 0;
                    ArmPocketRain(aw, roof, dl => offered += dl);
                    aw.k.rainNotches = 1;
                    aw.Pulse(seeds);
                    long right = aw.k.WaterOf(seeds[2]) + aw.k.WaterOf(seeds[3]);
                    Assert(right == 2 * U, $"exact {exact}: the right run holds {right} dL, want {2 * U} (its own notch only)");
                    Assert(aw.k.WaterOf(seeds[0]) == U && aw.k.WaterOf(seeds[1]) == 0, $"exact {exact}: left {aw.k.WaterOf(seeds[0])} dL, sluice {aw.k.WaterOf(seeds[1])} dL");
                    Assert(offered == U && aw.k.rainLandedDl == U, $"exact {exact}: offered {offered} dL, landed {aw.k.rainLandedDl}");
                }
            });
            Case("CsReview_pocket_rain_sealed_square_takes_its_part_notch", () =>
            {
                // cs_review F3 (red-first): exact-level water. A sealed open square holding 1 dL of a 1-notch bed has U-1 dL of
                // room: it takes that and only 1 dL runs over the lip. Was: room rounded to 0 notches, the whole notch spilled.
                var aw = RowScene(true, new[] {
                    ((byte)1, (byte)0, (ushort)1, ArrayWorld.Water, false, true) }, out var roof, out var seeds);
                long offered = 0;
                ArmPocketRain(aw, roof, dl => offered += dl);
                aw.k.rainNotches = 1;
                aw.Pulse(seeds);
                Assert(aw.k.WaterOf(seeds[0]) == U, $"the sealed square holds {aw.k.WaterOf(seeds[0])} dL, want {U}");
                Assert(offered == 1 && aw.k.rainLandedDl == U - 1, $"offered {offered} dL, landed {aw.k.rainLandedDl}");
            });
            Case("CsReview_exact_dry_square_skips_a_switched_off_source", () =>
            {
                // cs_review F4 (red-first): a dry dug square between a switched-off water source and a limitless tar source.
                // The tar fills it whichever side is walked first. Was: the first source named the liquid even when switched
                // off, and the domain then took nothing from it, so the square stayed dry for good.
                foreach (bool waterNorth in new[] { true, false })
                {
                    var aw = new ArrayWorld(3, 3);
                    aw.k.levelExactEnabled = true; aw.k.levelBySurfaceEnabled = true;
                    int c = 4, a = waterNorth ? 7 : 5, b = waterNorth ? 5 : 7;
                    aw.k.depth[c] = 1;
                    aw.natural[a] = true; aw.terrainFluid[a] = ArrayWorld.Water;
                    aw.natural[b] = true; aw.terrainFluid[b] = ArrayWorld.Tar;
                    aw.BodyAt(a);
                    aw.BodyAt(b, 1f, true);
                    aw.disabledFluid = ArrayWorld.Water;
                    for (int p = 0; p < 4; p++) aw.Pulse(new List<int> { c });
                    Assert(aw.k.WaterOf(c) > 0 && ReferenceEquals(aw.cellFluid[c], ArrayWorld.Tar),
                        $"water {(waterNorth ? "north" : "east")}: the square holds {aw.k.WaterOf(c)} dL of {(aw.cellFluid[c] as Fluid)?.name}");
                }
            });
            Case("Rain_review_pocket_rain_fills_dry_and_fractional_room", () =>
            {
                // MED: a pocket with room takes its rain. An open brimming square beside a roofed DRY square of the pocket runs
                // the notch into it; with exact-level water two half-notches of room take one pooled notch. Nothing spills.
                foreach (bool exact in new[] { true, false })
                {
                    var aw = RowScene(exact, new[] {
                        ((byte)1, (byte)1, (ushort)0, ArrayWorld.Water, false, false),
                        ((byte)1, (byte)0, (ushort)0, (Fluid)null, true, false) }, out var roof, out var seeds);
                    long offered = 0;
                    ArmPocketRain(aw, roof, dl => offered += dl);
                    aw.k.rainNotches = 1;
                    aw.Pulse(seeds);
                    Assert(offered == 0 && aw.k.rainLandedDl == U, $"exact {exact}: dry room: offered {offered} dL, landed {aw.k.rainLandedDl}");
                    Assert(aw.k.WaterOf(seeds[0]) + aw.k.WaterOf(seeds[1]) == 2 * U, $"exact {exact}: the pocket holds {aw.k.WaterOf(seeds[0]) + aw.k.WaterOf(seeds[1])} dL");
                }
                {
                    var aw = RowScene(true, new[] {
                        ((byte)1, (byte)1, (ushort)0, ArrayWorld.Water, false, false),
                        ((byte)1, (byte)0, (ushort)(U / 2), ArrayWorld.Water, true, false),
                        ((byte)1, (byte)0, (ushort)(U - U / 2), ArrayWorld.Water, true, false) }, out var roof, out var seeds);
                    long offered = 0;
                    ArmPocketRain(aw, roof, dl => offered += dl);
                    aw.k.rainNotches = 1;
                    aw.Pulse(seeds);
                    Assert(offered == 0 && aw.k.rainLandedDl == U, $"fractional room: offered {offered} dL, landed {aw.k.rainLandedDl}");
                    long t = 0; foreach (int i in seeds) t += aw.k.WaterOf(i);
                    Assert(t == 3 * U, $"fractional room: the pocket holds {t} dL, want {3 * U}");
                }
            });

            // RAIN_REVIEW_FIX_SLUICES_AND_OVERFILL MED5: a pocket-grid query that fills a shared cache takes the owner gate; a
            // second thread overlapping the owner is refused, counted, and answered from the labels without touching the cache.
            Case("Rain_review_pocket_query_caches_take_the_owner_gate", () =>
            {
                var gate = new RM_WallReachMath.OwnerGate();
                var cache = new Dictionary<long, int>();
                int computed = 0;
                Func<int, int> f = v => { computed++; return v * 2; };
                int me = Environment.CurrentManagedThreadId;
                Assert(gate.Cached(me, cache, 7L, 21, f) == 42 && cache.Count == 1 && gate.Holder == 0, "the owner fills the cache and lets go");
                Assert(gate.Cached(me, cache, 7L, 99, f) == 42 && computed == 1, "the owner reads the cache back");
                Assert(gate.TryEnter(me, out bool n0) && !n0, "this thread owns");
                Assert(gate.Cached(me, cache, 9L, 1, f) == 2 && cache.Count == 2 && gate.Holder == me, "a nested query on the owner fills the cache and keeps the owner");
                int got = -1;
                var other = new System.Threading.Thread(() => got = gate.Cached(Environment.CurrentManagedThreadId, cache, 8L, 5, f));
                other.Start();
                other.Join();
                gate.Exit(n0);
                Assert(got == 10, "a refused query still answers from the labels: " + got);
                Assert(cache.Count == 2 && !cache.ContainsKey(8L), "a refused query leaves the shared cache alone");
                Assert(gate.refused == 1, "a refused query is counted: " + gate.refused);
                string pg = Src("Superdeep", "RM_PocketGrid.cs");
                RiverSwitchFlipChecks.Has(pg, @"return Owner\.Cached\(Me, cellsCache, Key\(k, component\), \(l, component, 0\), CellsOfFn\);", "CellsOf goes through the gate");
                RiverSwitchFlipChecks.Has(pg, @"return Owner\.Cached\(Me, wideCache, Key\(k, component, w\), \(l, component, w\), WideFn\);", "WideEverywhere goes through the gate");
                RiverSwitchFlipChecks.Has(pg, @"return Owner\.Cached\(Me, edgeCache, Key\(k, component\), \(l, component, 0\), EdgeFn\);", "TouchesEdge goes through the gate");
                RiverSwitchFlipChecks.Has(pg, @"public List<\(int a, int b\)> LadderEdges\(int k, Pawn p\) \{ if \(!EnterOwner\(out bool nested\)\) \{ return LadderEdgesOwned\(k, p, false\); \}", "LadderEdges goes through the gate");
                RiverSwitchFlipChecks.Has(pg, @"return UsableLadderIn\(k, component, p, owned \? ladderScratch : new List<Thing>\(\)\);", "UsableLadderIn uses the shared scratch only on the owner");
                RiverSwitchFlipChecks.Has(pg, @"LadderJoins\(p, into, owned \? ladderScratch : new List<Thing>\(\)\);", "LadderJoins uses the shared scratch only on the owner");
            });

            // RAIN_REVIEW_FIX_SLUICES_AND_OVERFILL MED6: a removed map's swim grids (native arrays) are freed when the map is
            // disposed, after its pathfinder has completed every job that could read them, not when another map next asks.
            Case("Rain_review_removed_map_frees_swim_grids", () =>
            {
                string sw = Src("Swimming", "RM_Swim.cs");
                RiverSwitchFlipChecks.Has(sw, @"\[HarmonyPatch\(typeof\(Map\), nameof\(Map\.Dispose\)\)\]", "Map.Dispose is patched");
                RiverSwitchFlipChecks.Has(sw, @"public static void Postfix\(Map __instance\) \{ RM_SwimPathing\.Forget\(__instance\); \}", "the postfix forgets the map's grids");
                RiverSwitchFlipChecks.Has(sw, @"public static void Forget\(Map map\) \{ if \(map != null && grids\.TryGetValue\(map, out MapGrids g\)\) \{ Free\(g\); grids\.Remove\(map\); \} \}", "Forget frees and drops the entry");
                RiverSwitchFlipChecks.Has(sw, @"foreach \(Map m in dead\) \{ Free\(grids\[m\]\); grids\.Remove\(m\); \}", "the lazy prune frees the same way");
            });

            // RAIN_REVIEW_FIX_SLUICES_AND_OVERFILL MED7: a closed sluice on a pond or natural-water square holds the sheet off it
            // (displacement and RunIntoBeds already respect it); the return leg never pours through it.
            Case("Rain_review_sheet_return_respects_a_shut_sluice_on_a_pond", () =>
            {
                string sh = Src("Sheet", "RM_MapComponent_Sheet.cs");
                RiverSwitchFlipChecks.Has(sh, @"bool shutHere = RM_FlowDoorRules\.SealsLiquid\(edifice\); RM_LiquidBody body = e\?\.Stock\?\.IndexedBodyAt\(map, c\); if \(body != null\) \{ if \(shutHere\) \{ world\.Kinds\[idx\] = Kind\.Blocked; return; \}", "a pond square under a shut sluice is Blocked");
                RiverSwitchFlipChecks.Has(sh, @"if \(baseT != null && baseT\.IsWater\) \{ if \(shutHere\) \{ world\.Kinds\[idx\] = Kind\.Blocked; return; \}", "a natural-water square under a shut sluice is Blocked");
            });

            // RAIN_REVIEW_FIX_SLUICES_AND_OVERFILL LOW9: the L0 ledger counts the sheet's standing water, and the rain line tells
            // landed, offered-over-the-lip and sheet-accepted rain apart (an offer is not an input).
            Case("Rain_review_ledger_counts_sheet_water_and_accepted_rain", () =>
            {
                string ex = Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"double total = bodiesU \+ canalsU \+ tanksU \+ hoseU \+ sheetU;", "the total holds the sheet");
                RiverSwitchFlipChecks.Has(ex, @"sheetU = \(Sheet\.RM_MapComponent_Sheet\.Of\(map\)\?\.StandingDl \?\? 0\) \* \(RM_Volume\.UnitsPerLevel / \(double\)RM_LevelSolve\.U\);", "sheet standing in tank units");
                RiverSwitchFlipChecks.Has(ex, @"\+ "" \| rain\(session, dL\): landed="" \+ pocketRainLandedDl \+ "" offered="" \+ pocketRainRunOverDl \+ "" sheetAccepted="" \+ pocketRainAcceptedDl", "rain landed/offered/accepted");
                RiverSwitchFlipChecks.Has(ex, @"flowKernel\.rainOverflow = rainOverflowCb \?\?= \(idx, dl, fl\) => pocketRainAcceptedDl \+= Sheet\.RM_MapComponent_Sheet\.RainOverflowDl\(", "accepted rain is what the sheet took");
                string sh = Src("Sheet", "RM_MapComponent_Sheet.cs");
                RiverSwitchFlipChecks.Has(sh, @"public long StandingDl => state\?\.Standing \?\? 0;", "the sheet reports its standing dL");
            });
        }

        private static void RainCases(Action<string, Action> Case)
        {
            Case("Rain_pocket_equals_exact_pass_unless_brimming", () =>
            {
                // Pocket rain lands each open square's own notches inside the pulse walk; the exact pass lands them before it.
                // While no square brims the two end every pulse byte-identical; a pulse where one brims may differ only by the
                // pocket keeping water the exact pass ran over the lip (more water, never less in total, ledger balanced).
                int same = 0, brimPulses = 0, rained = 0;
                for (int seed = 0; seed < 200; seed++)
                {
                    bool exact = seed % 4 != 3;
                    var (exW, seeds) = seed % 2 == 0 ? RainScene(seed, exact) : PulseScene(seed, exact);
                    var (apW, _) = seed % 2 == 0 ? RainScene(seed, exact) : PulseScene(seed, exact);
                    var r = new Random(seed * 13 + 1);
                    var roof = new bool[exW.w * exW.h];
                    for (int i = 0; i < roof.Length; i++) roof[i] = r.Next(4) == 0;
                    long offers = 0;
                    ArmPocketRain(apW, roof, dl => offers++);
                    for (int p = 0; p < 20; p++)
                    {
                        int levels = r.Next(3) != 0 ? 0 : r.Next(1, 3);
                        long over = 0, landedEx = 0;
                        if (levels > 0) foreach (int i in Enumerable.Range(0, roof.Length)) over += ExactRainSquare(exW, i, levels, roof, ref landedEx);
                        apW.k.rainNotches = levels;
                        exW.Pulse(seeds);
                        apW.Pulse(seeds);
                        apW.k.rainNotches = 0;
                        if (levels > 0) rained++;
                        Assert(apW.k.worstImbalance == 0 || !exact, $"seed {seed} pulse {p}: pocket rain unbalanced the ledger: {string.Join("; ", apW.k.imbalanceReports)}");
                        if (over > 0)
                        {
                            // a square brimmed: the pocket may keep what the exact pass ran over. Start the next pulse level again.
                            brimPulses++;
                            Resync(exW, apW);
                        }
                        else
                        {
                            Assert(PulseSnap(exW) == PulseSnap(apW), $"seed {seed} pulse {p}: no square brimmed, yet pocket rain differs from the exact pass");
                            Assert(apW.k.rainLandedDl == landedEx, $"seed {seed} pulse {p}: landed {apW.k.rainLandedDl} dL, the exact pass {landedEx}");
                            if (levels > 0) same++;
                        }
                    }
                }
                Console.WriteLine($"    200 scenes x 20 pulses: {same} rained pulses with no brim byte-identical, {brimPulses} pulses brimmed (resynced), {rained} rained");
                Assert(same > 300 && rained > 800 && brimPulses > 50, "the scenes do not exercise rain both below and at the brim (sanity probe)");
            });
            Case("Rain_pocket_conserves_and_offers_once_per_pocket", () =>
            {
                // Every notch on an open water-or-dry square is landed or run over; the run-over is ONE offer per pocket walked
                // (the exact pass offered once per brimming square: 78,400 a pulse on a brim-full 280x280 pit).
                int offerPulses = 0;
                for (int seed = 0; seed < 150; seed++)
                {
                    var (aw, seeds) = PulseScene(seed, true);
                    var r = new Random(seed * 7 + 3);
                    var roof = new bool[aw.w * aw.h];
                    for (int i = 0; i < roof.Length; i++) roof[i] = r.Next(5) == 0;
                    long offers = 0, offerDl = 0;
                    ArmPocketRain(aw, roof, dl => { offers++; offerDl += dl; });
                    for (int p = 0; p < 15; p++)
                    {
                        int levels = r.Next(1, 4), U = RM_LevelSolve.U;
                        long due = 0;
                        for (int i = 0; i < roof.Length; i++)
                        {
                            if (aw.k.depth[i] == 0 || roof[i]) continue;
                            bool wet = aw.k.WaterOf(i) > 0;
                            if (!wet || aw.cellFluid[i] == ArrayWorld.Water) due += levels * (long)U;
                        }
                        long o0 = offers, d0 = offerDl;
                        aw.k.rainNotches = levels;
                        aw.Pulse(seeds);
                        aw.k.rainNotches = 0;
                        Assert(aw.k.worstImbalance == 0, $"seed {seed} pulse {p}: ledger {string.Join("; ", aw.k.imbalanceReports)}");
                        Assert(aw.k.rainLandedDl + (offerDl - d0) == due, $"seed {seed} pulse {p}: landed {aw.k.rainLandedDl} + run over {offerDl - d0} != rain due {due}");
                        Assert(offerDl - d0 == aw.k.rainOverflowDl, $"seed {seed} pulse {p}: offered {offerDl - d0} dL, the kernel counts {aw.k.rainOverflowDl}");
                        Assert(offers - o0 <= aw.k.rainPockets, $"seed {seed} pulse {p}: {offers - o0} offers from {aw.k.rainPockets} pockets");
                        if (offers > o0) offerPulses++;
                    }
                }
                Assert(offerPulses > 100, $"only {offerPulses} pulses ran rain over a lip (sanity probe)");
            });
            Case("Rain_pocket_sliced_equals_atomic_and_inert_dry", () =>
            {
                int multi = 0;
                for (int seed = 0; seed < 120; seed++)
                {
                    bool exact = seed % 4 != 3;
                    var (atomW, seeds) = PulseScene(seed, exact);
                    var (sliceW, _) = PulseScene(seed, exact);
                    var (dryW, _) = PulseScene(seed, exact);
                    var (plainW, _) = PulseScene(seed, exact);
                    var roof = new bool[atomW.w * atomW.h];
                    var r = new Random(seed * 3 + 11);
                    for (int i = 0; i < roof.Length; i++) roof[i] = r.Next(4) == 0;
                    ArmPocketRain(atomW, roof, dl => { });
                    ArmPocketRain(sliceW, roof, dl => { });
                    ArmPocketRain(dryW, roof, dl => { });   // armed, but never a notch: the kernel must be the plain one
                    for (int p = 0; p < 15; p++)
                    {
                        int levels = r.Next(2) == 0 ? 0 : r.Next(1, 3);
                        atomW.k.rainNotches = levels; sliceW.k.rainNotches = levels;
                        atomW.Pulse(seeds);
                        if (SlicedPulse(sliceW, seeds, 40, r) > 1) multi++;
                        Assert(PulseSnap(atomW) == PulseSnap(sliceW), $"seed {seed} pulse {p}: sliced pocket rain differs from atomic");
                        dryW.Pulse(seeds); plainW.Pulse(seeds);
                        Assert(PulseSnap(dryW) == PulseSnap(plainW), $"seed {seed} pulse {p}: an unrained pulse differs from the kernel without rain");
                    }
                }
                Assert(multi > 300, "the slices were not exercised (sanity probe)");
            });
            Case("Rain_lead_pass_sliced_equals_one_tick_deluge_325", () =>
            {
                // The exact fallback (rainPocketApproxEnabled off): a deluge on 80,000 dug squares. The pass landed a slice a tick
                // (RM_RainPass.CellsPerTick) ends with the grids the one-tick pass gives, pictures through the write budget.
                const int w = 325, h = 325;
                ArrayWorld Scene()
                {
                    var aw = new ArrayWorld(w, h);
                    for (int z = 2; z <= 321; z++)
                        for (int x = 10; x <= 314; x++)
                        {
                            if (x > 134 && x < 190) continue;
                            int i = z * w + x;
                            aw.k.depth[i] = 7; aw.k.fill[i] = (byte)(x <= 134 ? 6 : 0); aw.cellFluid[i] = x <= 134 ? ArrayWorld.Water : null;
                        }
                    return aw;
                }
                var one = Scene(); var sliced = Scene();
                var roof = new bool[w * h];
                for (int i = 0; i < roof.Length; i++) roof[i] = (i % w) % 50 < 7;
                var order = new List<int>();
                for (int i = 0; i < w * h; i++) if (one.k.depth[i] > 0) order.Add(i);
                const int levels = 4;
                long l1 = 0, l2 = 0, o1 = 0, o2 = 0;
                foreach (int i in order) o1 += ExactRainSquare(one, i, levels, roof, ref l1);
                var pass = new RM_RainPass();
                var budget = new RM_TerrainWriteBudget();
                var drawn = new int[w * h];
                int Band(ArrayWorld a, int i) => RM_LevelSolve.LookBand(a.k.fill[i] * (long)RM_LevelSolve.U);
                foreach (int i in order) drawn[i] = Band(sliced, i);
                long tick = 0;
                bool Apply(int i)
                {
                    int want = Band(sliced, i);
                    if (drawn[i] == want) return true;
                    if (!budget.TryTakeWrite(tick)) { budget.Defer(i, w * h); return false; }
                    drawn[i] = want; return true;
                }
                pass.Begin(levels);
                foreach (int i in order) pass.Add(i);
                int lead = RM_RainPass.LeadTicks(order.Count, 250), ticks = 0, maxSquares = 0, maxWrites = 0;
                Assert(lead <= 125 && lead * RM_RainPass.CellsPerTick >= order.Count, $"lead {lead} ticks cannot land {order.Count} squares");
                while (pass.Remaining > 0 || budget.Count > 0)
                {
                    tick++; ticks++;
                    budget.Drain(RM_TerrainWriteBudget.JudgedPerTick, Apply);
                    int n = pass.Step(RM_RainPass.CellsPerTick, (i, lv) => { o2 += ExactRainSquare(sliced, i, lv, roof, ref l2); Apply(i); });
                    maxSquares = Math.Max(maxSquares, n);
                    maxWrites = Math.Max(maxWrites, budget.WritesThisTick);
                    Assert(ticks < 2000, "the backlog never drained");
                }
                for (int i = 0; i < w * h; i++)
                {
                    Assert(one.k.fill[i] == sliced.k.fill[i] && one.cellFluid[i] == sliced.cellFluid[i], $"square {i}: the sliced pass ends otherwise than the one-tick pass");
                    if (sliced.k.depth[i] > 0) Assert(drawn[i] == Band(sliced, i), $"square {i}: its picture never caught up");
                }
                Assert(l1 == l2 && o1 == o2, $"landed {l1}/{l2}, run over {o1}/{o2}");
                Assert(maxSquares <= RM_RainPass.CellsPerTick && maxWrites <= RM_TerrainWriteBudget.WritesPerTick, $"a tick landed {maxSquares} squares, wrote {maxWrites} pictures");
                Console.WriteLine($"    deluge on {order.Count} squares: lead {lead} ticks; rain in {(order.Count + RM_RainPass.CellsPerTick - 1) / RM_RainPass.CellsPerTick} ticks, pictures drained by tick {ticks}; max {maxSquares} squares, {maxWrites} writes a tick");
                Assert(l1 > 0 && o1 > 0, "the deluge neither landed nor ran over (sanity probe)");
            });
            Case("Rain_pins_save_drains_pulse_does_not", () =>
            {
                string exc = Src("RM_MapComponent_Excavation.cs");
                int all = 0;
                for (int at = exc.IndexOf("DrainTerrainWrites(true)"); at >= 0; at = exc.IndexOf("DrainTerrainWrites(true)", at + 1)) all++;
                Assert(all == 1, $"DrainTerrainWrites(true) is called {all} times: only the save (FinishPulse) may draw every waiting picture at once");
                int fp = exc.IndexOf("public void FinishPulse()");
                Assert(fp >= 0 && exc.IndexOf("DrainTerrainWrites(true)") > fp && exc.IndexOf("LandRainOwed();", fp) > fp, "FinishPulse no longer lands owed rain and draws the backlog before a save");
                string k = Src("RM_FlowKernel.cs");
                int er = k.IndexOf("private void ResolveExact(");
                Assert(er >= 0 && k.IndexOf("PocketRain(exDug);", er) > er && k.IndexOf("PocketRain(exDug);", er) < k.IndexOf("long before = 0;", er), "pocket rain no longer lands before the exact ledger's before");
                int pr = k.IndexOf("private void PocketRain(");
                Assert(pr >= 0 && k.IndexOf("rainCatches(c)", pr) < k.IndexOf("long roomDl", pr), "pocket rain asks the roof before the room (a roofed brimming square spills nothing)");
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains("public static bool rainPocketApproxEnabled = true;") && mod.Contains("\"rainPocketApproxEnabled\", true"), "pocket rain is not the scribed default");
            });
        }

        public static void Run(Action<string, Action> Case)
        {
            // Randomized maps: every step carries GatherData noise (deltas whose square's kind did not move: a haul, a
            // reservation, a thing spawned on open ground), some steps a real kind edit (wall built/mined, door placed) and
            // some a depth edit (a dig). The new policy's labels must equal a fresh full Label of the live state at every
            // step; the old policy flooded every step.
            PulseCases(Case);
            RainCases(Case);
            RainReviewCases(Case);
            Case("WallReach_delta_policy_equals_full_scan", () =>
            {
                int cls = RM_WallReachMath.ClassOf(true, true, false, false, false, false);
                int totalSteps = 0, realSteps = 0, newFloods = 0, oldFloods = 0;
                for (int seed = 1; seed <= 40; seed++)
                {
                    var r = new Random(seed * 7919);
                    int w = r.Next(8, 40), h = r.Next(8, 40), n = w * h;
                    byte[] live = RandomKinds(r, n);
                    byte[] depth = r.Next(3) == 0 ? null : RandomDepth(r, n, true);
                    int band = r.Next(0, 4);
                    var sim = new Sim();
                    sim.Rebuild(live, depth, w, h, band, cls);
                    for (int step = 0; step < 60; step++)
                    {
                        totalSteps++;
                        var deltas = new List<int>();
                        int noise = r.Next(0, 12);
                        for (int j = 0; j < noise; j++) deltas.Add(r.Next(n));
                        bool real = false;
                        int roll = r.Next(10);
                        if (roll == 0)
                        {
                            int c = r.Next(n);
                            byte was = live[c];
                            live[c] = KindPool[r.Next(KindPool.Length)];
                            deltas.Add(c);
                            real = live[c] != was;
                        }
                        else if (roll == 1)
                        {
                            // A -> B -> A inside one gather window: the square ends where the snapshot holds it
                            int c = r.Next(n);
                            byte was = live[c];
                            live[c] = was == RM_WallReachMath.Wall ? RM_WallReachMath.Open : RM_WallReachMath.Wall;
                            live[c] = was;
                            deltas.Add(c);
                        }
                        else if (roll == 2 && depth != null)
                        {
                            depth = (byte[])depth.Clone();
                            int c = r.Next(n);
                            byte was = depth[c];
                            depth[c] = (byte)r.Next(0, 6);
                            real = depth[c] != was;
                        }
                        if (real) realSteps++;
                        // judge the deltas (FlushDeltas) against the snapshot the labels came from
                        byte[] snap = sim.snapshot;
                        if (RM_WallReachMath.DeltaMovesKinds(snap, deltas, i => live[i], false))
                        {
                            sim.gen++;
                            sim.bumps++;
                        }
                        bool depthMoved = !RM_WallReachMath.SameBytes(depth, sim.builtDepth);   // ClimbGeneration's own bump
                        if (sim.gen != sim.builtGen || depthMoved)
                        {
                            sim.Rebuild(live, depth, w, h, band, cls);
                        }
                        oldFloods++;   // the old policy: GatherData bumped every step, every step re-flooded
                        var truth = RM_WallReachMath.Label(live, depth, w, h, band, cls);
                        Assert(SameLabels(sim.labels, truth), "seed " + seed + " step " + step + ": the delta policy's labels differ from a full scan");
                    }
                    newFloods += sim.floods - 1;
                }
                Assert(newFloods <= realSteps, "floods only on a real change: " + newFloods + " floods vs " + realSteps + " real changes");
                Assert(oldFloods == totalSteps && newFloods * 4 < oldFloods, "the old policy flooded every step: old " + oldFloods + " new " + newFloods);
                Console.WriteLine("    [excavation-tick] delta policy: " + totalSteps + " gathers, " + realSteps + " real changes, floods old=" + oldFloods + " new=" + newFloods);
            });

            // Per-tick work is bounded: the judge reads at most MaxQueuedDeltas squares; past the cap it is the old eager stale.
            // ── WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP (GPT review of the FlowWorks alloc diff, 2026-10-27) ──
            // The production lifecycle classes (LabelSlot, KindsSnapshot, OwnerGate, StaleAfterLoad) driven directly.
            Case("WallReach_slot_lifecycle", () =>
            {
                int cls = RM_WallReachMath.ClassOf(true, true, false, true, false, false);
                // 1. A retained labelling survives exactly one later flood; the second reuses its array (holders let go first).
                var r0 = new Random(4242);
                int w0 = 17, h0 = 13, n0 = w0 * h0;
                byte[] k1 = RandomKinds(r0, n0), k2 = RandomKinds(r0, n0), k3 = RandomKinds(r0, n0);
                var slot0 = new RM_WallReachMath.LabelSlot();
                slot0.Rebuild(k1, null, null, w0, h0, 0, cls);
                RM_WallReachMath.Labels held = slot0.labels;
                int[] heldCopy = (int[])held.label.Clone();
                Assert(slot0.Rebuild(k2, null, null, w0, h0, 0, cls), "new kinds must flood");
                Assert(!ReferenceEquals(slot0.labels.label, held.label) && held.label.SequenceEqual(heldCopy)
                    && SameLabels(held, RM_WallReachMath.Label(k1, null, w0, h0, 0, cls)), "a labelling held across ONE flood changed under its holder");
                Assert(slot0.Rebuild(k3, null, null, w0, h0, 0, cls), "new kinds must flood (2)");
                Assert(ReferenceEquals(slot0.labels.label, held.label), "the second flood reuses the spare array (the documented contract; the sanity probe that the reuse is real)");
                Assert(SameLabels(slot0.labels, RM_WallReachMath.Label(k3, null, w0, h0, 0, cls)), "the reused array labels the new kinds");

                // 2. Alternating changed / unchanged builds (kinds by reference, depth and ramps by content) equal a fresh Label.
                int floods = 0, skips = 0;
                for (int seed = 1; seed <= 30; seed++)
                {
                    var r = new Random(seed * 104729);
                    int w = r.Next(5, 28), h = r.Next(5, 28), n = w * h;
                    var snap = new RM_WallReachMath.KindsSnapshot();
                    var slot = new RM_WallReachMath.LabelSlot();
                    byte[] live = RandomKinds(r, n);
                    byte[] depth = RandomDepth(r, n, r.Next(3) != 0);
                    Dictionary<int, int> ramps = null;
                    int band = r.Next(0, 4), c = r.Next(RM_WallReachMath.ClassCount);
                    var held2 = new List<(RM_WallReachMath.Labels lab, int[] copy, int life)>();
                    for (int step = 0; step < 80; step++)
                    {
                        switch (r.Next(6))
                        {
                            case 0: live[r.Next(n)] = KindPool[r.Next(KindPool.Length)]; break;
                            case 1: depth = (byte[])depth.Clone(); depth[r.Next(n)] = (byte)r.Next(0, 6); break;
                            case 2: ramps = r.Next(2) == 0 ? null : new Dictionary<int, int> { [r.Next(n)] = r.Next(n), [r.Next(n)] = r.Next(n) }; break;
                            case 3: depth = (byte[])depth.Clone(); break;   // same content, new array: must not flood
                            default: break;                                  // nothing moved
                        }
                        byte[] read = snap.Take(n);
                        Array.Copy(live, read, n);
                        byte[] kinds = snap.Publish(read, step, w, h);
                        slot.Rebuild(kinds, depth, ramps, w, h, band, c);
                        var truth = RM_WallReachMath.Label(live, depth, w, h, band, c, RM_WallReachMath.RampJoins(ramps));
                        Assert(SameLabels(slot.labels, truth), "seed " + seed + " step " + step + ": the slot's labels differ from a fresh Label");
                        // a holder that took the labels last build still reads them unchanged (one flood later at most)
                        foreach (var hv in held2)
                        {
                            if (hv.life >= slot.floods - 1)
                                Assert(hv.lab.label.SequenceEqual(hv.copy), "seed " + seed + " step " + step + ": a labelling held across one flood was written");
                        }
                        held2.RemoveAll(hv => hv.life < slot.floods - 1);
                        held2.Add((slot.labels, (int[])slot.labels.label.Clone(), slot.floods));
                    }
                    floods += slot.floods;
                    skips += slot.skips;
                }
                Assert(floods > 0 && skips > 0, "both paths must run (floods " + floods + ", skips " + skips + ")");

                // 3. Geometry is identity: the same bytes at 2x3 and 3x2 are two maps.
                var g = new RM_WallReachMath.LabelSlot();
                byte[] six = { 0, 1, 0, 0, 1, 0 };
                g.Rebuild(six, null, null, 2, 3, 0, 0);
                Assert(g.Rebuild(six, null, null, 3, 2, 0, 0) && g.labels.width == 3 && g.labels.height == 2, "a geometry change with the same bytes must re-flood");
                Assert(!g.Rebuild(six, null, null, 3, 2, 0, 0), "an identical build must skip (sanity probe)");
                Console.WriteLine("    [excavation-tick] slot lifecycle: " + floods + " floods, " + skips + " skips, every one equal to a fresh Label");
            });

            Case("WallReach_kinds_snapshot_never_written", () =>
            {
                var r = new Random(77);
                int w = 21, h = 9, n = w * h;
                var snap = new RM_WallReachMath.KindsSnapshot();
                byte[] live = RandomKinds(r, n);
                var published = new List<(byte[] arr, byte[] copy)>();
                int kept = 0;
                for (int step = 0; step < 300; step++)
                {
                    if (r.Next(3) == 0) live[r.Next(n)] = KindPool[r.Next(KindPool.Length)];
                    Assert(!snap.CurrentFor(step, w, h), "a new stamp is never current");
                    byte[] read = snap.Take(n);
                    Assert(published.TrueForAll(p => !ReferenceEquals(p.arr, read)), "step " + step + ": a published array was handed out as scratch");
                    Array.Copy(live, read, n);
                    byte[] before = snap.published;
                    byte[] now = snap.Publish(read, step, w, h);
                    Assert(snap.CurrentFor(step, w, h) && now.SequenceEqual(live), "step " + step + ": the published array is not the read");
                    if (ReferenceEquals(now, before)) kept++;
                    else published.Add((now, (byte[])now.Clone()));
                    foreach (var p in published) Assert(p.arr.SequenceEqual(p.copy), "step " + step + ": a published snapshot was written after publication");
                }
                Assert(kept > 50 && published.Count > 20, "both paths must run (kept " + kept + ", published " + published.Count + ")");
                byte[] last = snap.published;
                byte[] same = snap.Take(n);
                Array.Copy(last, same, n);
                Assert(!ReferenceEquals(snap.Publish(same, 1000, h, w), last), "the same bytes at another width and height must publish anew");
                snap.Invalidate();
                Assert(!snap.CurrentFor(1000, h, w), "Invalidate makes the next ask re-read");
            });

            Case("WallReach_post_load_and_owner_gate", () =>
            {
                Assert(RM_WallReachMath.StaleAfterLoad(true, true), "a mid-load build is stale once playing");
                Assert(!RM_WallReachMath.StaleAfterLoad(true, false), "still loading: keep it until play");
                Assert(!RM_WallReachMath.StaleAfterLoad(false, true) && !RM_WallReachMath.StaleAfterLoad(false, false), "an in-play build is not stale");

                var gate = new RM_WallReachMath.OwnerGate();
                Assert(gate.TryEnter(11, out bool n1) && !n1 && gate.Holder == 11, "the first caller owns");
                Assert(gate.TryEnter(11, out bool n2) && n2, "the owner re-enters (nested)");
                gate.Exit(n2);
                Assert(gate.Holder == 11, "a nested exit keeps the owner");
                Assert(!gate.TryEnter(12, out _) && gate.refused == 1, "a second thread overlapping the owner is refused and counted");
                gate.Exit(n1);
                Assert(gate.Holder == 0, "the owner left");
                Assert(gate.TryEnter(12, out bool n3) && !n3, "after the owner leaves, the next thread owns");
                gate.Exit(n3);

                // A real second thread, while this one holds the gate.
                Assert(gate.TryEnter(Environment.CurrentManagedThreadId, out bool n4) && !n4, "this thread owns");
                bool other = true;
                var t = new System.Threading.Thread(() => other = gate.TryEnter(Environment.CurrentManagedThreadId, out _));
                t.Start();
                t.Join();
                gate.Exit(n4);
                Assert(!other && gate.refused == 2, "a real worker thread is refused while the owner holds the caches");

                // Every query class against every kind: the vanilla rules per class bit (ClassOf's inputs), not Passable's own code.
                int classes = 0;
                for (int bits = 0; bits < 64; bits++)
                {
                    bool byPawn = (bits & 1) != 0, open = (bits & 2) != 0, bash = (bits & 4) != 0, shut = (bits & 8) != 0, fence = (bits & 16) != 0, nonSwim = (bits & 32) != 0;
                    int c = RM_WallReachMath.ClassOf(byPawn, open, bash, shut, fence, nonSwim);
                    Assert(c >= 0 && c < RM_WallReachMath.ClassCount, "class out of range");
                    bool judged = byPawn && !bash;
                    Assert(RM_WallReachMath.Passable(RM_WallReachMath.Open, c) && RM_WallReachMath.Passable(RM_WallReachMath.HeldDoor, c), "open ground and a held door pass everyone");
                    Assert(!RM_WallReachMath.Passable(RM_WallReachMath.Wall, c), "a wall passes nobody");
                    Assert(RM_WallReachMath.Passable(RM_WallReachMath.Door, c) == !(judged && !open), "bits " + bits + ": a door");
                    Assert(RM_WallReachMath.Passable(RM_WallReachMath.PlayerDoor, c) == !(judged && (!open || shut)), "bits " + bits + ": a player door");
                    Assert(RM_WallReachMath.Passable(RM_WallReachMath.ShutGate, c) == !judged, "bits " + bits + ": a shut gate");
                    Assert(RM_WallReachMath.Passable(RM_WallReachMath.Fence, c) == !fence, "bits " + bits + ": a fence");
                    Assert(RM_WallReachMath.Passable(RM_WallReachMath.DeepWater, c) == !nonSwim, "bits " + bits + ": deep water");
                }
                for (int c = 0; c < RM_WallReachMath.ClassCount; c++)
                {
                    var r = new Random(c + 1);
                    int w = r.Next(4, 20), h = r.Next(4, 20), n = w * h;
                    byte[] k = RandomKinds(r, n);
                    Assert(SameLabels(RefWallLabel(k, null, w, h, 0, c), RM_WallReachMath.Label(k, null, w, h, 0, c)), "class " + c + ": labels differ from the reference");
                    classes++;
                }
                Assert(classes == 32, "all 32 classes labelled");

                string wr = Src("Superdeep", "RM_WallReach.cs");
                RiverSwitchFlipChecks.Has(wr, @"if \(RM_WallReachMath\.StaleAfterLoad\(st\.builtMidLoad, playing\)\) \{ st\.kinds\.Invalidate\(\); st\.builtMidLoad = false; \}", "Tick re-reads the kinds after a load");
                RiverSwitchFlipChecks.Has(wr, @"if \(e\.stamp == stamp && !reload\).{0,900}RebuildDue\(true, forced \|\| reload \|\| !covered,", "a mid-load labelling is rebuilt unthrottled in play (sliced: stale or reload, urgent while uncovered)");
                RiverSwitchFlipChecks.Has(wr, @"e\.jobMidLoad = Current\.ProgramState != ProgramState\.Playing;", "a build records whether it ran mid-load (at job start)");
                RiverSwitchFlipChecks.Has(wr, @"e\.midLoad = e\.jobMidLoad; st\.builtMidLoad \|= e\.midLoad;", "the publish carries the job's mid-load flag");
                RiverSwitchFlipChecks.Has(wr, @"doorScratch\.Clear\(\); RM_PocketGrid\.ExitOwner\(nested\); \}", "the suspect doors are let go in a finally");
                RiverSwitchFlipChecks.Has(wr, @"if \(!On \|\| map == null \|\| !RM_PocketGrid\.EnterOwner\(out bool nested\)\) \{ return false; \}", "a query off the owner vetoes nothing");
                RiverSwitchFlipChecks.Has(wr, @"if \(!RM_PocketGrid\.EnterOwner\(out bool nested\)\) \{ return; \} try \{ BuildOwned\(", "a build runs on the owner");
                string pg = Src("Superdeep", "RM_PocketGrid.cs");
                RiverSwitchFlipChecks.Has(pg, @"private void Build\(bool notifyFlips, int cause\) \{ if \(!EnterOwner\(out bool nested\)\) \{ return; \}", "a pocket build runs on the owner");
                RiverSwitchFlipChecks.Has(pg, @"lastW != map\.Size\.x \|\| lastH != map\.Size\.z\)", "BuiltView checks the geometry");
                string tr = Src("Superdeep", "RM_SuperdeepTrap.cs");
                RiverSwitchFlipChecks.Has(tr, @"if \(!__result \|\| !RM_PocketGrid\.EnterOwner\(out bool nested\)\) \{ return; \} try \{ Owned\(start, dest, peMode, traverseParams, ref __result, ___map\);", "the CanReach veto runs on the owner");
                RiverSwitchFlipChecks.Has(tr, @"if \(!__result \|\| !RM_PocketGrid\.EnterOwner\(out bool nested\)\) \{ return; \} try \{ Owned\(c, traverseParms, ref __result\);", "the map-edge veto runs on the owner");
            });

            Case("WallReach_delta_judge_bounded", () =>
            {
                var snap = new byte[RM_WallReachMath.MaxQueuedDeltas * 2];
                int reads = 0;
                var many = new List<int>();
                for (int i = 0; i < RM_WallReachMath.MaxQueuedDeltas; i++) many.Add(i);
                Assert(!RM_WallReachMath.DeltaMovesKinds(snap, many, i => { reads++; return snap[i]; }, false), "unchanged squares do not move the labels");
                Assert(reads == RM_WallReachMath.MaxQueuedDeltas, "one read per queued square, got " + reads);
                reads = 0;
                Assert(RM_WallReachMath.DeltaMovesKinds(snap, many, i => { reads++; return snap[i]; }, true) && reads == 0, "overflowed: stale at once, no reads");
                Assert(RM_WallReachMath.DeltaMovesKinds(null, new List<int> { 3 }, i => 0, false), "no snapshot: any delta is a change");
                Assert(!RM_WallReachMath.DeltaMovesKinds(null, new List<int>(), i => 0, false), "no snapshot, no delta: nothing");
                Assert(!RM_WallReachMath.DeltaMovesKinds(snap, null, i => 0, false), "a null list moves nothing");
                Assert(RM_WallReachMath.DeltaMovesKinds(snap, new List<int> { -1 }, i => 0, false)
                    && RM_WallReachMath.DeltaMovesKinds(snap, new List<int> { snap.Length }, i => 0, false), "an out-of-range delta is a change (never trusted)");
                snap[5] = RM_WallReachMath.Wall;
                Assert(RM_WallReachMath.DeltaMovesKinds(snap, new List<int> { 1, 5 }, i => RM_WallReachMath.Open, false), "a wall gone is a change");

                // the 325x325 bisect map: the judge's cost against the flood it saves
                int w = 325, h = 325, n = w * h;
                var r = new Random(325);
                byte[] kinds = RandomKinds(r, n);
                var noise = new List<int>();
                for (int i = 0; i < 64; i++) noise.Add(r.Next(n));
                int cls = RM_WallReachMath.ClassOf(true, true, false, false, false, false);
                RM_WallReachMath.Label(kinds, null, w, h, 0, cls);   // warm
                var sw = Stopwatch.StartNew();
                for (int t = 0; t < 20; t++) RM_WallReachMath.Label(kinds, null, w, h, 0, cls);
                double floodMs = sw.Elapsed.TotalMilliseconds / 20;
                sw.Restart();
                for (int t = 0; t < 2000; t++) RM_WallReachMath.DeltaMovesKinds(kinds, noise, i => kinds[i], false);
                double judgeMs = sw.Elapsed.TotalMilliseconds / 2000;
                sw.Restart();
                byte[] copy = (byte[])kinds.Clone();
                for (int t = 0; t < 200; t++) RM_WallReachMath.SameBytes(kinds, copy);
                double sameMs = sw.Elapsed.TotalMilliseconds / 200;
                Console.WriteLine("    [excavation-tick] 325x325: flood " + floodMs.ToString("0.000") + " ms, 64-delta judge " + judgeMs.ToString("0.0000")
                    + " ms, SameBytes " + sameMs.ToString("0.000") + " ms");
                Assert(judgeMs * 20 < floodMs, "the judge must cost a small fraction of the flood it saves");
            });

            Case("WallReach_content_skip_equals_rebuild", () =>
            {
                Assert(RM_WallReachMath.SameBytes(null, null) && !RM_WallReachMath.SameBytes(new byte[1], null)
                    && !RM_WallReachMath.SameBytes(new byte[2], new byte[3]) && RM_WallReachMath.SameBytes(new byte[] { 1, 2 }, new byte[] { 1, 2 })
                    && !RM_WallReachMath.SameBytes(new byte[] { 1, 2 }, new byte[] { 1, 3 }), "SameBytes");
                Assert(RM_WallReachMath.SameRamps(null, new Dictionary<int, int>()) && RM_WallReachMath.SameRamps(new Dictionary<int, int> { [1] = 2 }, new Dictionary<int, int> { [1] = 2 })
                    && !RM_WallReachMath.SameRamps(new Dictionary<int, int> { [1] = 2 }, new Dictionary<int, int> { [1] = 3 })
                    && !RM_WallReachMath.SameRamps(new Dictionary<int, int> { [1] = 2 }, new Dictionary<int, int> { [2] = 2 })
                    && !RM_WallReachMath.SameRamps(new Dictionary<int, int> { [1] = 2 }, null), "SameRamps");
                // purity: identical inputs (fresh arrays) give identical labels, ramps included
                int cls = RM_WallReachMath.ClassOf(true, true, false, true, false, false);
                for (int seed = 1; seed <= 25; seed++)
                {
                    var r = new Random(seed);
                    int w = r.Next(6, 30), h = r.Next(6, 30), n = w * h;
                    byte[] kinds = RandomKinds(r, n), depth = RandomDepth(r, n, true);
                    var ramps = new Dictionary<int, int>();
                    for (int j = 0; j < 4; j++) ramps[r.Next(n)] = r.Next(n);
                    Func<int, int, bool> joins = (a, b) => (ramps.TryGetValue(a, out int x) && x == b) || (ramps.TryGetValue(b, out int y) && y == a);
                    var ramps2 = new Dictionary<int, int>(ramps);
                    Func<int, int, bool> joins2 = (a, b) => (ramps2.TryGetValue(a, out int x) && x == b) || (ramps2.TryGetValue(b, out int y) && y == a);
                    for (int band = 0; band < 4; band++)
                    {
                        var first = RM_WallReachMath.Label(kinds, depth, w, h, band, cls, joins);
                        var again = RM_WallReachMath.Label((byte[])kinds.Clone(), (byte[])depth.Clone(), w, h, band, cls, joins2);
                        Assert(RM_WallReachMath.SameRamps(ramps, ramps2) && SameLabels(first, again), "seed " + seed + " band " + band + ": identical inputs, different labels");
                    }
                }
                string wr = Src("Superdeep", "RM_WallReach.cs");
                RiverSwitchFlipChecks.Has(wr, @"if \(!e\.slot\.Rebuild\(kinds, depth, ramps, map\.Size\.x, map\.Size\.z, e\.band, e\.cls\)\)",
                    "Build skips through the LabelSlot (identical kinds, depth, ramps and geometry)");
                RiverSwitchFlipChecks.Has(wr, @"byte\[\] kinds = st\.kinds\.Take\(n\);", "Kinds reads into the snapshot's scratch");
                RiverSwitchFlipChecks.Has(wr, @"return st\.kinds\.Publish\(kinds, stamp, w, h\);", "Kinds keeps the old array when nothing moved");
                RiverSwitchFlipChecks.Has(wr, @"RM_PocketGrid\.ReportRefusals\(\); FlushDeltas\(map, st\); TickLap\(st, ref mark, TpFlush\); if \(st\.entries\.Count == 0\)", "Tick judges the deltas first");
                RiverSwitchFlipChecks.Has(wr, @"FlushDeltas\(map, st\);.{0,140}bool unthrottled = RM_WallReachMath\.PausedUnthrottled", "a paused write moves the stamp before PausedFrame compares it");
                RiverSwitchFlipChecks.Has(wr, @"if \(unjudged\) \{ st\.wallGenBy\[WgUnjudged\]\+\+; Interlocked\.Increment\(ref st\.wallGen\); \} int gen = Volatile\.Read\(ref st\.unsafeGen\);.{0,80}Build\(map, st, e, StampOf\(map, st\), gen\);", "a first build never labels from an unjudged snapshot");
                RiverSwitchFlipChecks.Has(wr, @"if \(deltas == null \|\| deltas\.Count == 0\) \{ return; \}", "an empty gather moves nothing");
                RiverSwitchFlipChecks.Has(wr, @"kinds\[idx\] == RM_WallReachMath\.Wall && pg\.WalkableFast\(idx\)\) \{ Interlocked\.Increment\(ref st\.wallGenBy\[WgConnBreach\]\); Interlocked\.Increment\(ref st\.wallGen\); Interlocked\.Increment\(ref st\.unsafeGen\); Interlocked\.Exchange\(ref st\.forced, 1\);",
                    "a wall breach still forces at once");
            });

            Case("PocketGrid_content_skip_equals_rebuild", () =>
            {
                // RM_PocketGrid.Build: a ClimbGeneration bump whose depth view and ramps come out identical keeps the bands.
                int skips = 0, floods = 0, oldFloods = 0;
                for (int seed = 1; seed <= 30; seed++)
                {
                    var r = new Random(seed * 31);
                    int w = r.Next(8, 40), h = r.Next(8, 40), n = w * h, bands = 4;
                    byte[] depth = RandomDepth(r, n, true);
                    byte[] lastDepth = null;
                    RM_PocketGridMath.Labels[] kept = null;
                    for (int step = 0; step < 40; step++)
                    {
                        byte[] view = (byte[])depth.Clone();   // ViewDepth: a fresh array every rebuild
                        if (r.Next(5) == 0)
                        {
                            depth[r.Next(n)] = (byte)r.Next(0, 6);   // a real dig (or a no-op write: same value)
                            view = (byte[])depth.Clone();
                        }
                        oldFloods += bands;
                        if (kept != null && RM_WallReachMath.SameBytes(view, lastDepth))
                        {
                            skips++;
                        }
                        else
                        {
                            kept = new RM_PocketGridMath.Labels[bands];
                            for (int k = 1; k <= bands; k++) kept[k - 1] = RM_PocketGridMath.Label(view, w, h, k);
                            floods += bands;
                        }
                        lastDepth = view;
                        for (int k = 1; k <= bands; k++)
                        {
                            Assert(SameLabels(kept[k - 1], RM_PocketGridMath.Label(depth, w, h, k)), "seed " + seed + " step " + step + " k " + k + ": skip differs from rebuild");
                        }
                    }
                }
                Assert(skips > 0 && floods < oldFloods, "the skip must fire on identical views");
                Console.WriteLine("    [excavation-tick] pocket grid: band floods old=" + oldFloods + " new=" + floods + " (" + skips + " rebuilds kept)");
                string pg = Src("Superdeep", "RM_PocketGrid.cs");
                RiverSwitchFlipChecks.Has(pg, @"bool sameInput = old != null && old\.Length == BandCount && lastW == w && lastH == h && RM_WallReachMath\.SameBytes\(depth, lastDepth\) && RM_WallReachMath\.SameRamps\(rampPairs, lastRamps\);",
                    "PocketGrid.Build skips only on an identical view and ramps");
                RiverSwitchFlipChecks.Has(pg, @"if \(!sameInput && notifyFlips", "kept bands flip nothing");
            });
        }
    }
}
