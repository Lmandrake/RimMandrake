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

        private static readonly byte[] KindPool =
        {
            RM_WallReachMath.Open, RM_WallReachMath.Open, RM_WallReachMath.Open, RM_WallReachMath.Open, RM_WallReachMath.Wall,
            RM_WallReachMath.Wall, RM_WallReachMath.Door, RM_WallReachMath.PlayerDoor, RM_WallReachMath.Fence, RM_WallReachMath.DeepWater,
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

        /// <summary>One simulated labelling under the new policy: the production rules, minus Verse.</summary>
        private sealed class Sim
        {
            public byte[] snapshot;          // MapState.kinds (kept by reference when its content did not change)
            public long gen;                 // wallGen
            public long builtGen = -1;
            public byte[] builtKinds, builtDepth;
            public RM_WallReachMath.Labels labels;
            public int floods, skips, bumps;

            public void Rebuild(byte[] liveKinds, byte[] depth, int w, int h, int band, int cls)
            {
                byte[] fresh = (byte[])liveKinds.Clone();
                if (!RM_WallReachMath.SameBytes(fresh, snapshot)) snapshot = fresh;      // Kinds()
                if (labels != null && ReferenceEquals(snapshot, builtKinds) && RM_WallReachMath.SameBytes(depth, builtDepth))
                {
                    skips++;
                }
                else
                {
                    labels = RM_WallReachMath.Label(snapshot, depth, w, h, band, cls);
                    floods++;
                }
                builtKinds = snapshot;
                builtDepth = depth;
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

        public static void Run(Action<string, Action> Case)
        {
            // Randomized maps: every step carries GatherData noise (deltas whose square's kind did not move: a haul, a
            // reservation, a thing spawned on open ground), some steps a real kind edit (wall built/mined, door placed) and
            // some a depth edit (a dig). The new policy's labels must equal a fresh full Label of the live state at every
            // step; the old policy flooded every step.
            PulseCases(Case);
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
                RiverSwitchFlipChecks.Has(wr, @"if \(e\.labels != null && ReferenceEquals\(kinds, e\.builtKinds\) && RM_WallReachMath\.SameBytes\(depth, e\.builtDepth\) && RM_WallReachMath\.SameRamps\(ramps, e\.builtRamps\)\)",
                    "Build skips only on identical kinds, depth and ramps");
                RiverSwitchFlipChecks.Has(wr, @"if \(!RM_WallReachMath\.SameBytes\(kinds, st\.kinds\)\) \{ st\.kinds = kinds; \}", "Kinds keeps the old array when nothing moved");
                RiverSwitchFlipChecks.Has(wr, @"FlushDeltas\(map, st\); if \(st\.entries\.Count == 0\)", "Tick judges the deltas first");
                RiverSwitchFlipChecks.Has(wr, @"FlushDeltas\(map, st\);.{0,140}bool unthrottled = RM_WallReachMath\.PausedUnthrottled", "a paused write moves the stamp before PausedFrame compares it");
                RiverSwitchFlipChecks.Has(wr, @"if \(unjudged\) \{ Interlocked\.Increment\(ref st\.wallGen\); \} Build\(map, st, e, StampOf\(map, st\), null\);", "a first build never labels from an unjudged snapshot");
                RiverSwitchFlipChecks.Has(wr, @"if \(deltas == null \|\| deltas\.Count == 0\) \{ return; \}", "an empty gather moves nothing");
                RiverSwitchFlipChecks.Has(wr, @"kinds\[idx\] == RM_WallReachMath\.Wall && pg\.WalkableFast\(idx\)\) \{ Interlocked\.Increment\(ref st\.wallGen\); Interlocked\.Exchange\(ref st\.forced, 1\);",
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
                RiverSwitchFlipChecks.Has(pg, @"bool sameInput = old != null && old\.Length == BandCount && RM_WallReachMath\.SameBytes\(depth, lastDepth\) && RM_WallReachMath\.SameRamps\(rampPairs, lastRamps\);",
                    "PocketGrid.Build skips only on an identical view and ramps");
                RiverSwitchFlipChecks.Has(pg, @"if \(!sameInput && notifyFlips", "kept bands flip nothing");
            });
        }
    }
}
