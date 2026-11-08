using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.Noise;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// The rare water, as the map rolled it. Standing water here comes only from the biome's noise patch maker (water where
    /// the noise passes 1.0), and some maps never pass it (map `n`, 2026-11-07: no water at all). That is a correct map, not
    /// a defect: the owner (2026-11-07) "No guarantee. It is absolutely not ok to assume you can appear on these harsh maps and
    /// be ok." A colony that lands dry walks to another map; nothing here digs a pond or sinks a well.
    ///
    /// Right after Terrain (210), in three passes over whatever water there is:
    /// 1. Ragged shores. The patch maker's contour is a smooth noise level (frequency 0.012), and snapped to whole cells it
    ///    drew 45-degree staircases (map s) and then long straight sides like a rectangular pool (map t, 2026-11-07).
    /// 2. One ring for every pond: a thin mud margin (none on firm stretches), a ragged rich-soil band, then deep ash.
    /// 3. Firm stretches of any mud left that no pond owns.
    /// </summary>
    public class GenStep_PyrelandsStandingWater : GenStep
    {
        public override int SeedPart => 1462093117;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!PyrelandsMechanicsGate.On) return;
            TerrainDef shallow = TerrainDefOf.WaterShallow, mud = TerrainDefOf.Mud;
            TerrainDef rich = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_FE_Ground_SoilRich") ?? TerrainDefOf.Soil;
            TerrainDef ash = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_FE_Ash_Deep");
            RaggedShores(map, shallow, mud);
            var bank = new Perlin(0.07, 2.0, 0.5, 2, Rand.Int, QualityMode.Medium);
            bool[] ringed = ReRing(map, shallow, mud, rich, ash, bank);
            FirmBanks(map, mud, rich, bank, ringed);
            if (Prefs.DevMode) Log.Message("[RimMandrake.Pyrelands] standing water: " + ShoreCensus(map, shallow, mud, rich));
        }

        // ── 1. ragged shores ────────────────────────────────────────────────────────────────────────────────────────────

        /// <summary>
        /// Redraws every standing-water shore (PyrelandsShoreShape does the grid work). Only shallow standing water and soft
        /// ground move; rivers, rock, rock floor and anything built stay. Water given up turns to mud; ReRing decides what it
        /// ends as.
        /// </summary>
        private static void RaggedShores(Map map, TerrainDef shallow, TerrainDef mud)
        {
            CellIndices ci = map.cellIndices;
            TerrainGrid g = map.terrainGrid;
            int sx = map.Size.x, sz = map.Size.z, n = ci.NumGridCells;
            var water = new bool[n];
            var free = new bool[n];
            for (int i = 0; i < n; i++)
            {
                TerrainDef t = g.TerrainAt(i);
                water[i] = t == shallow;
                if (t != shallow && t != mud && !Writable(t)) continue;
                IntVec3 c = ci.IndexToCell(i);
                if (c.GetEdifice(map) != null) continue;
                free[i] = true;
            }
            int seed = Rand.Int;
            var grain = new Perlin[PyrelandsShoreShape.LayerFrequency.Length];
            for (int l = 0; l < grain.Length; l++)
                grain[l] = new Perlin(PyrelandsShoreShape.LayerFrequency[l], 2.0, 0.5, 2, seed + 7 * l, QualityMode.Medium);
            bool[] wet = PyrelandsShoreShape.Shape(sx, sz, water, free, (l, x, z) => (float)grain[l].GetValue(x, 0, z), seed);

            for (int i = 0; i < n; i++)
            {
                if (!free[i] || wet[i] == water[i]) continue;
                g.SetTerrain(ci.IndexToCell(i), wet[i] ? shallow : mud);
            }
        }

        /// <summary>Majority clean-up passes on the rich band's outer edge.</summary>
        public const int CleanPasses = 2;

        // ── 2. the ring ─────────────────────────────────────────────────────────────────────────────────────────────────

        /// <summary>
        /// One ring per pond, drawn by distance to the water. The patch maker's ring was wide, smooth mud (0.90-1.00 of its
        /// noise, often 4-8 cells) inside a smooth rich band, and map s (2026-11-07) showed a bare brown moat round the water:
        /// mud has no fertility, so nothing grows on it. Now: a mud margin MudMin-MudMax cells wide, none at all where the bank
        /// noise says firm (about three stretches in ten, in runs several cells long) so the grass and FlowWorks canals reach
        /// the water there (FlowWorks will neither dig Mud nor pass water through it); then rich soil out to a ragged BandMin-
        /// BandMax cells further; then deep ash. Every mud or rich-soil cell joined to the water beyond that band (the patch
        /// maker's old ring) goes back to deep ash. Returns the cells it decided, so FirmBanks leaves them.
        /// </summary>
        private static bool[] ReRing(Map map, TerrainDef shallow, TerrainDef mud, TerrainDef rich, TerrainDef ash, Perlin bank)
        {
            CellIndices ci = map.cellIndices;
            TerrainGrid g = map.terrainGrid;
            int sx = map.Size.x, sz = map.Size.z, n = ci.NumGridCells;
            var water = new bool[n];
            for (int i = 0; i < n; i++) water[i] = g.TerrainAt(i) == shallow;
            float[] d = PyrelandsShoreShape.Distance(sx, sz, water);

            // The old ring: mud and rich soil joined (8-way) to the water.
            var old = new bool[n];
            var seen = (bool[])water.Clone();
            var queue = new Queue<int>();
            for (int i = 0; i < n; i++) if (water[i]) queue.Enqueue(i);
            while (queue.Count > 0)
            {
                int i = queue.Dequeue(), x = i % sx, z = i / sx;
                for (int k = 0; k < 8; k++)
                {
                    IntVec3 o = GenAdj.AdjacentCells[k];
                    int nx = x + o.x, nz = z + o.z;
                    if (nx < 0 || nz < 0 || nx >= sx || nz >= sz) continue;
                    int j = nz * sx + nx;
                    if (seen[j]) continue;
                    TerrainDef t = g.TerrainAt(j);
                    if (t != mud && t != rich) continue;
                    seen[j] = old[j] = true;
                    queue.Enqueue(j);
                }
            }

            var fine = new Perlin(0.33, 2.0, 0.5, 2, Rand.Int, QualityMode.Medium);
            var mid = new Perlin(0.15, 2.0, 0.5, 2, Rand.Int, QualityMode.Medium);
            var wide = new Perlin(0.06, 2.0, 0.5, 2, Rand.Int, QualityMode.Medium);
            var edge = new Perlin(0.30, 2.0, 0.5, 2, Rand.Int, QualityMode.Medium);
            var ringed = new bool[n];
            var kind = new byte[n];   // 0 untouched, 1 mud, 2 rich, 3 ash
            for (int i = 0; i < n; i++)
            {
                if (water[i]) continue;
                TerrainDef t = g.TerrainAt(i);
                if (t != mud && !Writable(t)) continue;
                if (!old[i] && d[i] > MudMax + BandMax) continue;
                IntVec3 c = ci.IndexToCell(i);
                if (c.GetEdifice(map) != null) continue;
                bool firm = bank.GetValue(c.x, 0, c.z) + FirmGrain * fine.GetValue(c.x, 0, c.z) > FirmBankNoise;
                float mudWidth = firm ? 0f : Clamp(MudBase + MudSwing * (float)mid.GetValue(c.x, 0, c.z), MudMin, MudMax);
                float band = Clamp(BandBase + BandSwing * (float)wide.GetValue(c.x, 0, c.z) + BandGrain * (float)edge.GetValue(c.x, 0, c.z),
                    BandMin, BandMax);
                if (d[i] <= mudWidth) kind[i] = 1;
                else if (d[i] <= mudWidth + band) kind[i] = 2;
                else if (old[i] || t == ash) kind[i] = 3;
            }

            // The band's outer edge: a lone rich cell out in the ash, or a lone ash cell inside the band, joins its neighbours.
            var flips = new List<int>();
            for (int pass = 0; pass < CleanPasses; pass++)
            {
                flips.Clear();
                for (int i = 0; i < n; i++)
                {
                    if (kind[i] != 2 && kind[i] != 3) continue;
                    int x = i % sx, z = i / sx, other = 0;
                    if (x > 0 && Swaps(kind[i], kind[i - 1])) other++;
                    if (x < sx - 1 && Swaps(kind[i], kind[i + 1])) other++;
                    if (z > 0 && Swaps(kind[i], kind[i - sx])) other++;
                    if (z < sz - 1 && Swaps(kind[i], kind[i + sx])) other++;
                    if (other >= 3) flips.Add(i);
                }
                foreach (int i in flips) kind[i] = (byte)(kind[i] == 2 ? 3 : 2);
            }

            // Mud off the water's edge (two cells out) needs mud between it and the water, or it is a brown speck in the band.
            for (int i = 0; i < n; i++)
            {
                if (kind[i] != 1 || d[i] < 1.5f) continue;
                int x = i % sx, z = i / sx;
                bool held = false;
                for (int k = 0; k < 8 && !held; k++)
                {
                    IntVec3 o = GenAdj.AdjacentCells[k];
                    int nx = x + o.x, nz = z + o.z;
                    if (nx < 0 || nz < 0 || nx >= sx || nz >= sz) continue;
                    int j = nz * sx + nx;
                    held = kind[j] == 1 && d[j] < 1.5f;
                }
                if (!held) kind[i] = 2;
            }

            for (int i = 0; i < n; i++)
            {
                ringed[i] = kind[i] != 0;
                TerrainDef want = kind[i] == 1 ? mud : kind[i] == 2 ? rich : kind[i] == 3 ? ash : null;
                if (want == null || g.TerrainAt(i) == want) continue;
                g.SetTerrain(ci.IndexToCell(i), want);
            }
            return ringed;
        }

        /// <summary>True when a rich (2) and an ash (3) cell meet: the band edge's majority clean-up counts only those.</summary>
        private static bool Swaps(byte me, byte other) => (me == 2 && other == 3) || (me == 3 && other == 2);

        private static float Clamp(float v, float lo, float hi) => v < lo ? lo : v > hi ? hi : v;

        /// <summary>Mud margin width in cells: MudBase plus MudSwing times a mid noise, clamped. At 1.0-1.4 only the four
        /// straight neighbours of the water are mud, so the margin's inner corners already go rich; at 2+ it is two cells.</summary>
        public const float MudBase = 1.6f, MudSwing = 0.8f, MudMin = 1f, MudMax = 2.3f;
        /// <summary>Rich-soil band beyond the mud, in cells: BandBase plus a slow swing and a fine grain, clamped.</summary>
        public const float BandBase = 3.5f, BandSwing = 1.4f, BandGrain = 0.9f, BandMin = 2f, BandMax = 5.5f;
        /// <summary>How much fine noise roughens a firm stretch's ends, so a firm bank does not start on a straight line.</summary>
        public const double FirmGrain = 0.25;

        // ── 3. firm banks of unowned mud ────────────────────────────────────────────────────────────────────────────────

        /// <summary>
        /// Firm stretches of bank. Every pond came ringed all the way round in vanilla Mud, and FlowWorks will neither dig Mud
        /// (it slides back) nor pass water through it, so no canal could ever reach the water and a watered strip of ash was
        /// out of a player's reach (map p, 2026-11-07). ReRing now draws the firm stretches of every pond's own ring from this
        /// same noise; this pass covers the mud no pond owns (the patch maker's mud where its noise reached 0.90 but never 1.0,
        /// and puddles RaggedShores filled), cells ReRing decided are skipped.
        /// </summary>
        private static void FirmBanks(Map map, TerrainDef mud, TerrainDef rich, Perlin bank, bool[] ringed)
        {
            TerrainGrid g = map.terrainGrid;
            for (int i = 0; i < map.cellIndices.NumGridCells; i++)
            {
                if (ringed[i] || g.TerrainAt(i) != mud) continue;
                IntVec3 c = map.cellIndices.IndexToCell(i);
                if (c.GetEdifice(map) != null) continue;
                if (bank.GetValue(c.x, 0, c.z) > FirmBankNoise) g.SetTerrain(c, rich);
            }
        }

        /// <summary>Bank noise above this is firm ground; about 30% of a Perlin field lies above 0.2 (40% above 0.1, which left
        /// too little mud once the ring's margin itself was thinned to 1-2 cells: the prototype's shores went 46% rich).</summary>
        public const double FirmBankNoise = 0.2;

        // ── shared ──────────────────────────────────────────────────────────────────────────────────────────────────────

        /// <summary>The ash and the unburned pockets; never rock floor, water or anything built.</summary>
        private static bool Writable(TerrainDef t)
        {
            return t != null && !t.IsWater && (t.defName.StartsWith("RM_FE_Ash") || t.defName.StartsWith("RM_FE_Ground"));
        }

        /// <summary>The dev-mode census line: what the parent's live look checks against the design numbers.</summary>
        private static string ShoreCensus(Map map, TerrainDef shallow, TerrainDef mud, TerrainDef rich)
        {
            TerrainGrid g = map.terrainGrid;
            int sx = map.Size.x, sz = map.Size.z, n = map.cellIndices.NumGridCells;
            int water = 0, shore = 0, shoreMud = 0, shoreRich = 0, mudCells = 0, richCells = 0;
            for (int i = 0; i < n; i++)
            {
                TerrainDef t = g.TerrainAt(i);
                if (t == shallow) { water++; continue; }
                if (t == mud) mudCells++;
                if (t == rich) richCells++;
                int x = i % sx, z = i / sx;
                bool edge = (x > 0 && g.TerrainAt(i - 1) == shallow) || (x < sx - 1 && g.TerrainAt(i + 1) == shallow)
                            || (z > 0 && g.TerrainAt(i - sx) == shallow) || (z < sz - 1 && g.TerrainAt(i + sx) == shallow);
                if (!edge) continue;
                shore++;
                if (t == mud) shoreMud++;
                if (t == rich) shoreRich++;
            }
            return "water " + water + ", mud " + mudCells + ", rich soil " + richCells + "; shore cells " + shore + " (mud "
                   + shoreMud + ", rich soil " + shoreRich + ")";
        }
    }

    /// <summary>
    /// The shore's shape on plain grids (index z * sizeX + x, as CellIndices), so it runs without a map. Map t (2026-11-07)
    /// read as rectangular pools with a notch: one fine noise added to the shore's distance moved it a median of half a
    /// cell, and any smooth noise snapped to cells keeps a straight side wherever the shore runs near a grid axis and the
    /// noise is near zero. So, as judged on the offline prototype (shore_shape.py, six seeds of patch-maker ponds and
    /// small round ones): two noise layers draw bays and points, each capped by the pond's own inscribed radius so a small pond is not
    /// torn apart, with each pond's offset fitted so its area holds; spikes flip, square corners are bevelled, and every
    /// straight run still longer than MaxRun gets a small bump or notch.
    /// </summary>
    internal static class PyrelandsShoreShape
    {
        /// <summary>Noise layers, cycles per cell: a 10-cell swing for bays and points, a 4-cell grain on it.</summary>
        public static readonly double[] LayerFrequency = { 0.10, 0.25 };
        /// <summary>Each layer's shore move, in cells per standard deviation of its noise.</summary>
        public static readonly float[] LayerAmplitude = { 1.8f, 1.2f };
        /// <summary>Each layer's move at most this share of the pond's inscribed radius (0.4 made a 5-cell pond a cross).</summary>
        public static readonly float[] LayerCap = { 0.3f, 0.25f };
        /// <summary>Standard deviation of a two-octave Verse Perlin, measured on the prototype's port of it.</summary>
        public const float NoiseSigma = 0.411f;
        /// <summary>No cell farther than this (cells) from the old shore changes side.</summary>
        public const float Band = 5f;
        /// <summary>A square corner whose two arms run straight this many cells loses its corner cell.</summary>
        public const int CornerArm = 3;
        /// <summary>The longest straight shore run left alone; map t's ponds had sides of 8 to 10.</summary>
        public const int MaxRun = 4;
        /// <summary>Spike passes before the corner cut; one more follows it.</summary>
        public const int SpikePasses = 2;
        /// <summary>A pool of fewer cells than this reads as a puddle speck, not a pond, and becomes land.</summary>
        public const int MinPool = 6;
        /// <summary>An isle of fewer cells than this reads as a speck in the water and goes under.</summary>
        public const int MinIsle = 6;

        private const float Far = 1e9f, Diag = 1.41421356f;

        /// <summary>The new wet grid. free: cells allowed to change; grain(layer, x, z): that layer's Perlin at the cell.</summary>
        public static bool[] Shape(int sx, int sz, bool[] water, bool[] free, Func<int, int, int, float> grain, int seed)
        {
            int n = sx * sz;
            var wet = (bool[])water.Clone();
            int[] pond = Ponds(sx, water, out int count);
            if (count == 0) return wet;
            float[] toWater = Distance(sx, sz, water);
            var land = new bool[n];
            for (int i = 0; i < n; i++) land[i] = !water[i];
            float[] toLand = Distance(sx, sz, land);
            var radius = new float[count];
            for (int i = 0; i < n; i++) if (pond[i] >= 0) radius[pond[i]] = Math.Max(radius[pond[i]], toLand[i]);
            int[] near = Nearest(sx, sz, water, pond);

            var signed = new float[n];
            var disp = new float[n];
            var zone = new bool[n];
            var mine = new List<int>[count];
            for (int k = 0; k < count; k++) mine[k] = new List<int>();
            for (int i = 0; i < n; i++)
            {
                signed[i] = water[i] ? 0.5f - toLand[i] : toWater[i] - 0.5f;
                if (!free[i] || near[i] < 0) continue;
                float a = Math.Abs(signed[i]);
                zone[i] = a <= Band + 1f;
                if (a > Band) continue;
                mine[near[i]].Add(i);
                float r = radius[near[i]], v = 0f;
                for (int l = 0; l < LayerFrequency.Length; l++)
                    v += Math.Min(LayerAmplitude[l], LayerCap[l] * r) * grain(l, i % sx, i / sx) / NoiseSigma;
                disp[i] = v < -Band ? -Band : v > Band ? Band : v;
            }
            // Unfitted, the noise moved a small pond's area by up to a quarter; a binary search on each pond's offset
            // keeps the water its band had.
            foreach (List<int> cells in mine)
            {
                if (cells.Count == 0) continue;
                int want = 0;
                foreach (int i in cells) if (water[i]) want++;
                float lo = -Band, hi = Band;
                for (int it = 0; it < 20; it++)
                {
                    float c = 0.5f * (lo + hi);
                    int got = 0;
                    foreach (int i in cells) if (signed[i] + disp[i] + c < 0f) got++;
                    if (got > want) lo = c; else hi = c;
                }
                float off = 0.5f * (lo + hi);
                foreach (int i in cells) wet[i] = signed[i] + (disp[i] + off) < 0f;
            }

            for (int p = 0; p < SpikePasses; p++) Despike(sx, sz, wet, zone);
            CornerCut(sx, sz, wet, zone);
            Despike(sx, sz, wet, zone);
            BreakRuns(sx, sz, wet, zone, seed);
            DropSmall(sx, sz, wet, free, true, MinPool, false);
            DropSmall(sx, sz, wet, free, false, MinIsle, true);
            return wet;
        }

        /// <summary>Every zone cell with three or four of its four sides the other kind flips, all at once.</summary>
        private static void Despike(int sx, int sz, bool[] wet, bool[] zone)
        {
            var flips = new List<int>();
            for (int i = 0; i < wet.Length; i++) if (zone[i] && Others(sx, sz, wet, i) >= 3) flips.Add(i);
            foreach (int i in flips) wet[i] = !wet[i];
        }

        private static int Others(int sx, int sz, bool[] wet, int i)
        {
            int x = i % sx, z = i / sx, other = 0;
            if (x > 0 && wet[i - 1] != wet[i]) other++;
            if (x < sx - 1 && wet[i + 1] != wet[i]) other++;
            if (z > 0 && wet[i - sx] != wet[i]) other++;
            if (z < sz - 1 && wet[i + sx] != wet[i]) other++;
            return other;
        }

        /// <summary>A square corner whose arms both run straight CornerArm cells loses its corner cell (a point gives up
        /// water, a bay takes it), so it reads as a bevel. Judged all at once on the grid as it stood.</summary>
        private static void CornerCut(int sx, int sz, bool[] wet, bool[] zone)
        {
            var cut = new List<int>();
            for (int z = 1; z < sz - 1; z++)
            {
                for (int x = 1; x < sx - 1; x++)
                {
                    int i = z * sx + x;
                    if (!zone[i]) continue;
                    bool me = wet[i];
                    for (int k = 0; k < 4; k++)
                    {
                        int dz = k < 2 ? 1 : -1, dx = k % 2 == 0 ? 1 : -1;
                        // the corner's two outward sides are the other kind, its two inward sides mine
                        if (wet[i + dz * sx] == me || wet[i + dx] == me) continue;
                        if (wet[i - dz * sx] != me || wet[i - dx] != me) continue;
                        bool ok = true;
                        for (int t = 1; t < CornerArm && ok; t++)
                        {
                            int zz = z - dz * t, xx = x - dx * t;
                            ok = zz >= 0 && zz < sz && xx >= 0 && xx < sx
                                 && wet[zz * sx + x] == me && wet[zz * sx + x + dx] != me
                                 && wet[z * sx + xx] == me && wet[(z + dz) * sx + xx] != me;
                        }
                        if (ok) { cut.Add(i); break; }
                    }
                }
            }
            foreach (int i in cut) wet[i] = !wet[i];
        }

        /// <summary>
        /// Every straight shore run longer than MaxRun gets a two- or three-cell bump or notch a few cells in from its start,
        /// whichever keeps the area even, kept only if it leaves no spike and shortens the runs around it. Up to six sweeps,
        /// since a break can leave a shorter run that is still too long.
        /// </summary>
        private static void BreakRuns(int sx, int sz, bool[] wet, bool[] zone, int seed)
        {
            int balance = 0;
            var found = new List<int[]>();
            var cells = new List<int>();
            for (int sweep = 0; sweep < 6; sweep++)
            {
                found.Clear();
                for (int v = 0; v < 2; v++)
                {
                    bool vert = v == 1;
                    int lines = vert ? sx + 1 : sz + 1, span = vert ? sz : sx;
                    for (int line = 0; line < lines; line++)
                    {
                        int t = 0;
                        while (t < span)
                        {
                            int o = Edge(sx, sz, wet, vert, line, t);
                            if (o == 0) { t++; continue; }
                            int a = t;
                            while (t < span && Edge(sx, sz, wet, vert, line, t) == o) t++;
                            if (t - a > MaxRun) found.Add(new[] { v, line, a, t - a, o });
                        }
                    }
                }
                if (found.Count == 0) return;
                foreach (int[] f in found)
                {
                    bool vert = f[0] == 1;
                    int line = f[1], a = f[2], len = f[3], o = f[4];
                    if (RunAt(sx, sz, wet, vert, line, a) != len) continue;   // an earlier break this sweep moved it
                    double h = Hash01(a + 31 * line, f[0] + 7 * sweep, seed);
                    int m = 2 + (int)(h * 2.0);
                    int s = a + 1 + (int)(h * 977.0) % Math.Max(1, Math.Min(MaxRun, len - m - 1));
                    if (s + m > a + len - 1) s = a + Math.Max(1, len - m - 1);
                    for (int c = 0; c < 2; c++)
                    {
                        bool bump = (c == 0) == (balance <= 0);
                        // water on the low side (o = +1): a bump wets the high side, a notch dries the low side
                        int side = bump == (o > 0) ? 1 : 0;
                        cells.Clear();
                        for (int t = s; t < s + m; t++)
                        {
                            int x = vert ? line - 1 + side : t, z = vert ? t : line - 1 + side;
                            if (x < 0 || z < 0 || x >= sx || z >= sz || !zone[z * sx + x]) break;
                            cells.Add(z * sx + x);
                        }
                        if (cells.Count < m) continue;
                        int before = Around(sx, sz, wet, cells);
                        foreach (int i in cells) wet[i] = !wet[i];
                        if (!Spiky(sx, sz, wet, cells) && Around(sx, sz, wet, cells) < before)
                        {
                            balance += bump ? m : -m;
                            break;
                        }
                        foreach (int i in cells) wet[i] = !wet[i];
                    }
                }
            }
        }

        /// <summary>How the shore crosses grid line `line` at t: +1 water on the low side, -1 on the high side, 0 not at
        /// all. Vertical line x lies between columns x-1 and x, horizontal line z between rows z-1 and z. The map's own
        /// edge is never a shore.</summary>
        private static int Edge(int sx, int sz, bool[] wet, bool vert, int line, int t)
        {
            bool a, b;
            if (vert)
            {
                if (t < 0 || t >= sz || line <= 0 || line >= sx) return 0;
                a = wet[t * sx + line - 1];
                b = wet[t * sx + line];
            }
            else
            {
                if (t < 0 || t >= sx || line <= 0 || line >= sz) return 0;
                a = wet[(line - 1) * sx + t];
                b = wet[line * sx + t];
            }
            return a == b ? 0 : a ? 1 : -1;
        }

        /// <summary>Length of the straight run through grid line `line` at t, 0 where the shore does not cross it.</summary>
        private static int RunAt(int sx, int sz, bool[] wet, bool vert, int line, int t)
        {
            int o = Edge(sx, sz, wet, vert, line, t);
            if (o == 0) return 0;
            int a = t, b = t;
            while (Edge(sx, sz, wet, vert, line, a - 1) == o) a--;
            while (Edge(sx, sz, wet, vert, line, b + 1) == o) b++;
            return b - a + 1;
        }

        /// <summary>The longest straight run through any grid edge of these cells.</summary>
        private static int Around(int sx, int sz, bool[] wet, List<int> cells)
        {
            int best = 0;
            foreach (int i in cells)
            {
                int x = i % sx, z = i / sx;
                best = Math.Max(best, Math.Max(RunAt(sx, sz, wet, false, z, x), RunAt(sx, sz, wet, false, z + 1, x)));
                best = Math.Max(best, Math.Max(RunAt(sx, sz, wet, true, x, z), RunAt(sx, sz, wet, true, x + 1, z)));
            }
            return best;
        }

        /// <summary>True when any of these cells or its four neighbours has three or four sides the other kind.</summary>
        private static bool Spiky(int sx, int sz, bool[] wet, List<int> cells)
        {
            foreach (int i in cells)
            {
                int x = i % sx, z = i / sx;
                if (Others(sx, sz, wet, i) >= 3) return true;
                if (x > 0 && Others(sx, sz, wet, i - 1) >= 3) return true;
                if (x < sx - 1 && Others(sx, sz, wet, i + 1) >= 3) return true;
                if (z > 0 && Others(sx, sz, wet, i - sx) >= 3) return true;
                if (z < sz - 1 && Others(sx, sz, wet, i + sx) >= 3) return true;
            }
            return false;
        }

        /// <summary>A uniform [0, 1) from (x, z, seed): a 32-bit integer mix, bit for bit the prototype's.</summary>
        internal static double Hash01(int x, int z, int seed)
        {
            unchecked
            {
                uint h = (uint)x * 0x27D4EB2Du + (uint)z * 0x165667B1u + (uint)seed * 0x9E3779B9u;
                h ^= h >> 15;
                h *= 0x85EBCA6Bu;
                h ^= h >> 13;
                h *= 0xC2B2AE35u;
                h ^= h >> 16;
                return h / 4294967296.0;
            }
        }

        /// <summary>Each water cell's pond (4-connected), numbered in index order; -1 on land.</summary>
        private static int[] Ponds(int sx, bool[] water, out int count)
        {
            int n = water.Length;
            var pond = new int[n];
            for (int i = 0; i < n; i++) pond[i] = -1;
            var queue = new Queue<int>();
            count = 0;
            for (int s = 0; s < n; s++)
            {
                if (!water[s] || pond[s] >= 0) continue;
                pond[s] = count;
                queue.Enqueue(s);
                while (queue.Count > 0)
                {
                    int i = queue.Dequeue(), x = i % sx;
                    for (int k = 0; k < 4; k++)
                    {
                        int j = k == 0 ? (x < sx - 1 ? i + 1 : -1) : k == 1 ? (x > 0 ? i - 1 : -1) : k == 2 ? i + sx : i - sx;
                        if (j < 0 || j >= n || !water[j] || pond[j] >= 0) continue;
                        pond[j] = count;
                        queue.Enqueue(j);
                    }
                }
                count++;
            }
            return pond;
        }

        /// <summary>Each cell's nearest pond, by Distance's chamfer carrying the pond's number.</summary>
        private static int[] Nearest(int sx, int sz, bool[] water, int[] pond)
        {
            int n = sx * sz;
            var d = new float[n];
            var near = (int[])pond.Clone();
            for (int i = 0; i < n; i++) d[i] = water[i] ? 0f : Far;
            for (int z = 0; z < sz; z++)
            {
                for (int x = 0; x < sx; x++)
                {
                    int i = z * sx + x;
                    if (d[i] == 0f) continue;
                    if (x > 0) Pull(d, near, i, i - 1, 1f);
                    if (z == 0) continue;
                    Pull(d, near, i, i - sx, 1f);
                    if (x > 0) Pull(d, near, i, i - sx - 1, Diag);
                    if (x < sx - 1) Pull(d, near, i, i - sx + 1, Diag);
                }
            }
            for (int z = sz - 1; z >= 0; z--)
            {
                for (int x = sx - 1; x >= 0; x--)
                {
                    int i = z * sx + x;
                    if (d[i] == 0f) continue;
                    if (x < sx - 1) Pull(d, near, i, i + 1, 1f);
                    if (z == sz - 1) continue;
                    Pull(d, near, i, i + sx, 1f);
                    if (x < sx - 1) Pull(d, near, i, i + sx + 1, Diag);
                    if (x > 0) Pull(d, near, i, i + sx - 1, Diag);
                }
            }
            return near;
        }

        private static void Pull(float[] d, int[] near, int i, int j, float step)
        {
            if (d[j] + step >= d[i]) return;
            d[i] = d[j] + step;
            near[i] = near[j];
        }

        /// <summary>
        /// Flips every 4-connected patch of kind (wet true = water) smaller than minSize to the other kind, when all of it is
        /// free to change; with enclosed, only a patch whose every outside side is the other kind (an isle, not a cape).
        /// </summary>
        private static void DropSmall(int sx, int sz, bool[] wet, bool[] free, bool kind, int minSize, bool enclosed)
        {
            int n = wet.Length;
            var seen = new bool[n];
            var patch = new List<int>();
            var queue = new Queue<int>();
            for (int s = 0; s < n; s++)
            {
                if (seen[s] || wet[s] != kind) continue;
                patch.Clear();
                bool movable = true, shut = true;
                seen[s] = true;
                queue.Enqueue(s);
                while (queue.Count > 0)
                {
                    int i = queue.Dequeue();
                    patch.Add(i);
                    movable &= free[i];
                    int x = i % sx, z = i / sx;
                    for (int k = 0; k < 4; k++)
                    {
                        int nx = x + (k == 0 ? 1 : k == 1 ? -1 : 0), nz = z + (k == 2 ? 1 : k == 3 ? -1 : 0);
                        if (nx < 0 || nz < 0 || nx >= sx || nz >= sz) { shut = false; continue; }
                        int j = nz * sx + nx;
                        if (wet[j] != kind) continue;
                        if (seen[j]) continue;
                        seen[j] = true;
                        queue.Enqueue(j);
                    }
                }
                if (patch.Count >= minSize || !movable || (enclosed && !shut)) continue;
                foreach (int i in patch) wet[i] = !kind;
            }
        }

        /// <summary>
        /// Distance in cells from every cell to the nearest source cell (0 on a source), by the two-pass chamfer with straight
        /// steps 1 and diagonal steps sqrt 2: within 8% of true distance, in two sweeps of the grid. Index = z * sizeX + x,
        /// as CellIndices.
        /// </summary>
        internal static float[] Distance(int sx, int sz, bool[] source)
        {
            int n = sx * sz;
            var d = new float[n];
            for (int i = 0; i < n; i++) d[i] = source[i] ? 0f : Far;
            for (int z = 0; z < sz; z++)
            {
                for (int x = 0; x < sx; x++)
                {
                    int i = z * sx + x;
                    float v = d[i];
                    if (v == 0f) continue;
                    if (x > 0) v = Math.Min(v, d[i - 1] + 1f);
                    if (z > 0)
                    {
                        v = Math.Min(v, d[i - sx] + 1f);
                        if (x > 0) v = Math.Min(v, d[i - sx - 1] + Diag);
                        if (x < sx - 1) v = Math.Min(v, d[i - sx + 1] + Diag);
                    }
                    d[i] = v;
                }
            }
            for (int z = sz - 1; z >= 0; z--)
            {
                for (int x = sx - 1; x >= 0; x--)
                {
                    int i = z * sx + x;
                    float v = d[i];
                    if (v == 0f) continue;
                    if (x < sx - 1) v = Math.Min(v, d[i + 1] + 1f);
                    if (z < sz - 1)
                    {
                        v = Math.Min(v, d[i + sx] + 1f);
                        if (x < sx - 1) v = Math.Min(v, d[i + sx + 1] + Diag);
                        if (x > 0) v = Math.Min(v, d[i + sx - 1] + Diag);
                    }
                    d[i] = v;
                }
            }
            return d;
        }

    }

    /// <summary>
    /// The green ring. Rich soil within RingReach of water is the one place the Pyrelands should read green, and map s's
    /// first look (2026-11-07) found it about a third planted, and orange. Vanilla mapgen should fill it: plantDensity 16
    /// saturates every cell (desired min(16 x fertility^2, 1) = 1 at rich soil's 1.4, RimSage WildPlantSpawner.cs:718), the
    /// fill is map-wide in random cell order (SaturatedAt :613, the biome ignores local fertility), and no tile mutator of ours
    /// carries an override density curve (:418; only Oasis, Desert biomes). So the bare cells come after mapgen, most likely
    /// the opening burn or grazers at the only water; a natural pond is no Explosive Growth wet source (FlowWorks irrigation
    /// reads natural water as not irrigation), so the ring's grass never cycles. Whatever thins it, the ring starts whole and
    /// green: after the wild plants (900) and the late ruin scorch (965), every rich-soil cell in reach gets grass, Quickgrass
    /// QuickgrassShare of the time; a wild Ember Grass there is re-rolled the same way, since vanilla's commonalities (9.0
    /// ember, 3.8 quick) would leave a full ring 70% orange. Growth is mature-ish and age stays in the first half of life, so
    /// the ring neither shows as sprouts nor dies off together.
    /// </summary>
    public class GenStep_PyrelandsGreenRing : GenStep
    {
        public float ringReach = 7.5f;
        public float quickgrassShare = 0.8f;
        public FloatRange growth = new FloatRange(0.55f, 1.3f);

        public override int SeedPart => 778772307;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!PyrelandsMechanicsGate.On) return;
            TerrainDef rich = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_FE_Ground_SoilRich");
            ThingDef quick = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Plant_Quickgrass");
            ThingDef ember = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Plant_EmberGrass");
            if (rich == null || quick == null || ember == null)
            {
                Log.Warning("[RimMandrake.Pyrelands] green ring: rich soil or a Pyrelands grass def is missing; ring left as vanilla made it.");
                return;
            }
            CellIndices ci = map.cellIndices;
            TerrainGrid g = map.terrainGrid;
            int n = ci.NumGridCells;
            var water = new bool[n];
            for (int i = 0; i < n; i++) water[i] = g.TerrainAt(i)?.IsWater == true;
            float[] d = PyrelandsShoreShape.Distance(map.Size.x, map.Size.z, water);
            int ring = 0, planted = 0, rerolled = 0, held = 0;
            for (int i = 0; i < n; i++)
            {
                if (d[i] > ringReach || g.TerrainAt(i) != rich) continue;
                IntVec3 c = ci.IndexToCell(i);
                if (c.Roofed(map) || !PlantUtility.SnowAllowsPlanting(c, map)) continue;
                ring++;
                Plant was = c.GetPlant(map);
                if (was != null && was.def != ember) { held++; continue; }
                ThingDef want = Rand.Chance(quickgrassShare) ? quick : ember;
                if (was != null && want == ember) { held++; continue; }
                if (!want.CanEverPlantAt(c, map, canWipePlantsExceptTree: true)) continue;
                was?.Destroy();
                var p = (Plant)ThingMaker.MakeThing(want);
                p.Growth = Math.Min(1f, growth.RandomInRange);
                if (p.def.plant.LimitedLifespan) p.Age = Rand.Range(0, Math.Max(p.def.plant.LifespanTicks / 2, 1));
                GenSpawn.Spawn(p, c, map);
                if (was != null) rerolled++; else planted++;
            }
            if (Prefs.DevMode)
            {
                Log.Message("[RimMandrake.Pyrelands] green ring: " + ring + " rich-soil cells within " + ringReach + " of water; planted "
                            + planted + ", ember grass turned to quickgrass " + rerolled + ", already held " + held);
            }
        }
    }
}
