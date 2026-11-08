using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.Noise;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// The rare water, never none. Standing water here comes only from the biome's noise patch maker (water where the noise
    /// passes 1.0), and some maps never pass it: map `n` (2026-11-07, 38 C) had no water, no mud and 0.3% rich soil. Every
    /// colonist carries FlowWorks thirst (empty in about 0.6 days at 40 C, dead about 3 days later) and food gives no water,
    /// so that landing killed its colony. The cast's thirst (owner, 2026-11-07: "occasionally increase their density near the
    /// rare water") had nowhere to send it either.
    ///
    /// Right after Terrain (210), in four passes:
    /// 1. Ragged shores on every pond. The patch maker's contour is a smooth noise level (frequency 0.012), and snapped to
    ///    whole cells it drew as long 45-degree staircases at play zoom (map s, 2026-11-07); vanilla fades a shore by only half
    ///    a cell, so the outline itself has to be broken at the 1-2 cell scale.
    /// 2. A map still holding fewer than MinWaterCells water cells gets two or three small ponds on the ash away from the
    ///    edges, rock and the landing spot, and their shores get the same ragging. A map the noise already watered is left be.
    /// 3. One ring for every pond: a thin mud margin (none on firm stretches), a ragged rich-soil band, then deep ash.
    /// 4. Firm stretches of any mud left that no pond owns.
    /// </summary>
    public class GenStep_PyrelandsStandingWater : GenStep
    {
        public int minWaterCells = 150;
        public IntRange pondCount = new IntRange(2, 3);
        public FloatRange pondRadius = new FloatRange(4.5f, 7f);
        public int edgeMargin = 20;
        public int centreClear = 16;
        public int pondSpacing = 55;

        public override int SeedPart => 1462093117;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!PyrelandsMechanicsGate.On) return;
            // No deep water: its seam with shallow draws as hard whole-cell blocks (q_pond_h3); a pan is shallow throughout.
            TerrainDef deep = TerrainDefOf.WaterShallow, shallow = TerrainDefOf.WaterShallow, mud = TerrainDefOf.Mud;
            TerrainDef rich = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_FE_Ground_SoilRich") ?? TerrainDefOf.Soil;
            TerrainDef ash = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_FE_Ash_Deep");
            RaggedShores(map, shallow, mud, null);
            // Counted after the ragging (it moves a pond's area by a few percent either way), so the guarantee holds on what
            // the map actually ends with.
            if (WaterCells(map) < minWaterCells)
            {
                List<CellRect> dug = DigPonds(map, deep, shallow, mud, rich);
                if (dug.Count > 0) RaggedShores(map, shallow, mud, dug);
            }
            var bank = new Perlin(0.07, 2.0, 0.5, 2, Rand.Int, QualityMode.Medium);
            bool[] ringed = ReRing(map, shallow, mud, rich, ash, bank);
            FirmBanks(map, mud, rich, bank, ringed);
            if (Prefs.DevMode) Log.Message("[RimMandrake.Pyrelands] standing water: " + ShoreCensus(map, shallow, mud, rich));
        }

        // ── 1. ragged shores ────────────────────────────────────────────────────────────────────────────────────────────

        /// <summary>
        /// Moves every standing-water shore by up to about two cells: a cell within ShoreBand of the shore is water where its
        /// signed distance to the shore (negative in the water) plus ShoreAmplitude times a fine noise falls below zero, so the
        /// edge wanders on the noise's 3-cell grain instead of the contour's straight steps. Then three clean-ups, each judged on
        /// the offline prototype (shore_proto.py, 2026-11-07): a cell with three or four of its four sides the other kind flips
        /// (no one-cell spikes or notches), water pools under MinPool cells become land, and land isles under MinIsle cells with
        /// water on every side become water. Only shallow standing water and soft ground move; rivers, rock, rock floor and
        /// anything built stay. areas null means the whole map. Water given up turns to mud; ReRing decides what it ends as.
        /// </summary>
        private static void RaggedShores(Map map, TerrainDef shallow, TerrainDef mud, List<CellRect> areas)
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
                if (areas != null && !areas.Any(r => r.Contains(c))) continue;
                free[i] = true;
            }
            float[] toWater = Distance(sx, sz, water);
            var land = new bool[n];
            for (int i = 0; i < n; i++) land[i] = !water[i];
            float[] toLand = Distance(sx, sz, land);

            var grain = new Perlin(ShoreFrequency, 2.0, 0.5, 2, Rand.Int, QualityMode.Medium);
            var signed = new float[n];
            var wet = (bool[])water.Clone();
            for (int i = 0; i < n; i++)
            {
                signed[i] = water[i] ? 0.5f - toLand[i] : toWater[i] - 0.5f;
                if (!free[i] || Math.Abs(signed[i]) > ShoreBand) continue;
                IntVec3 c = ci.IndexToCell(i);
                wet[i] = signed[i] + ShoreAmplitude * (float)grain.GetValue(c.x, 0, c.z) < 0f;
            }

            var flips = new List<int>();
            for (int pass = 0; pass < CleanPasses; pass++)
            {
                flips.Clear();
                for (int i = 0; i < n; i++)
                {
                    if (!free[i] || Math.Abs(signed[i]) > ShoreBand + 1f) continue;
                    int x = i % sx, z = i / sx, other = 0;
                    if (x > 0 && wet[i - 1] != wet[i]) other++;
                    if (x < sx - 1 && wet[i + 1] != wet[i]) other++;
                    if (z > 0 && wet[i - sx] != wet[i]) other++;
                    if (z < sz - 1 && wet[i + sx] != wet[i]) other++;
                    if (other >= 3) flips.Add(i);
                }
                foreach (int i in flips) wet[i] = !wet[i];
            }
            DropSmall(sx, sz, wet, free, true, MinPool, false);
            DropSmall(sx, sz, wet, free, false, MinIsle, true);

            for (int i = 0; i < n; i++)
            {
                if (!free[i] || wet[i] == water[i]) continue;
                g.SetTerrain(ci.IndexToCell(i), wet[i] ? shallow : mud);
            }
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

        /// <summary>Fine shore noise, cycles per cell: about a 3-cell grain, the scale of the bays and points at play zoom.</summary>
        public const double ShoreFrequency = 0.30;
        /// <summary>How far the noise moves the shore, in cells; a Perlin field rarely passes +-1.2, so about two cells at most.</summary>
        public const float ShoreAmplitude = 1.7f;
        /// <summary>Only cells this close to the old shore (in cells) may change side.</summary>
        public const float ShoreBand = 2.5f;
        /// <summary>A pool of fewer cells than this reads as a puddle speck, not a pond, and becomes land.</summary>
        public const int MinPool = 6;
        /// <summary>An isle of fewer cells than this reads as a speck in the water and goes under.</summary>
        public const int MinIsle = 6;
        /// <summary>Majority clean-up passes on the shore and on the rich band's outer edge.</summary>
        public const int CleanPasses = 2;

        // ── 3. the ring ─────────────────────────────────────────────────────────────────────────────────────────────────

        /// <summary>
        /// One ring per pond, drawn by distance to the water. The patch maker's ring was wide, smooth mud (0.90-1.00 of its
        /// noise, often 4-8 cells) inside a smooth rich band, and map s (2026-11-07) showed a bare brown moat round the water:
        /// mud has no fertility, so nothing grows on it. Now: a mud margin MudMin-MudMax cells wide, none at all where the bank
        /// noise says firm (about three stretches in ten, in runs several cells long) so the grass and FlowWorks canals reach
        /// the water there (FlowWorks will neither dig Mud nor pass water through it); then rich soil out to a ragged BandMin-
        /// BandMax cells further; then deep ash. Every mud or rich-soil cell joined to the water beyond that band (the patch
        /// maker's old ring, a dug pond's own ring) goes back to deep ash. Returns the cells it decided, so FirmBanks leaves them.
        /// </summary>
        private static bool[] ReRing(Map map, TerrainDef shallow, TerrainDef mud, TerrainDef rich, TerrainDef ash, Perlin bank)
        {
            CellIndices ci = map.cellIndices;
            TerrainGrid g = map.terrainGrid;
            int sx = map.Size.x, sz = map.Size.z, n = ci.NumGridCells;
            var water = new bool[n];
            for (int i = 0; i < n; i++) water[i] = g.TerrainAt(i) == shallow;
            float[] d = Distance(sx, sz, water);

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

        // ── 4. firm banks of unowned mud ────────────────────────────────────────────────────────────────────────────────

        /// <summary>
        /// Firm stretches of bank. Every pond, the noise ponds and the dug ones alike, came ringed all the way round in vanilla
        /// Mud, and FlowWorks will neither dig Mud (it slides back) nor pass water through it, so no canal could ever reach the
        /// water and a watered strip of ash was out of a player's reach (map p, 2026-11-07). ReRing now draws the firm stretches
        /// of every pond's own ring from this same noise; this pass covers the mud no pond owns (the patch maker's mud where
        /// its noise reached 0.90 but never 1.0, and puddles RaggedShores filled), cells ReRing decided are skipped.
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

        // ── 2. dug ponds ────────────────────────────────────────────────────────────────────────────────────────────────

        /// <summary>Digs the ponds and returns each one's reach, for RaggedShores.</summary>
        private List<CellRect> DigPonds(Map map, TerrainDef deep, TerrainDef shallow, TerrainDef mud, TerrainDef rich)
        {
            int wanted = pondCount.RandomInRange;
            var centres = new List<IntVec3>();
            var reaches = new List<CellRect>();
            IntVec3 mid = map.Center;
            for (int tries = 0; tries < 400 && centres.Count < wanted; tries++)
            {
                float r = pondRadius.RandomInRange;
                var c = new IntVec3(Rand.RangeInclusive(edgeMargin, map.Size.x - 1 - edgeMargin), 0,
                    Rand.RangeInclusive(edgeMargin, map.Size.z - 1 - edgeMargin));
                if (c.DistanceTo(mid) < centreClear + r * 2f) continue;
                bool apart = true;
                foreach (IntVec3 o in centres) apart &= c.DistanceTo(o) >= pondSpacing;
                if (!apart || !SiteFits(map, c, r)) continue;
                Dig(map, c, r, deep, shallow, mud, rich);
                centres.Add(c);
                int reach = (int)Math.Ceiling(Math.Min(r * 2.4f, GenRadial.MaxRadialPatternRadius - 1f));
                reaches.Add(CellRect.CenteredOn(c, reach).ClipInsideMap(map));
            }
            if (centres.Count < wanted)
            {
                Log.Warning("[RimMandrake.Pyrelands] standing water: dug " + centres.Count + " of " + wanted
                            + " ponds; the map had no room on open ash for the rest.");
            }
            return reaches;
        }

        private static int WaterCells(Map map)
        {
            int n = 0;
            TerrainGrid g = map.terrainGrid;
            for (int i = 0; i < map.cellIndices.NumGridCells; i++)
            {
                TerrainDef t = g.TerrainAt(i);
                if (t != null && t.IsWater) n++;
            }
            return n;
        }

        /// <summary>Open, soft ground all the way out to the rich-soil ring, and no rock anywhere near it.</summary>
        private static bool SiteFits(Map map, IntVec3 c, float r)
        {
            int soft = 0, all = 0;
            foreach (IntVec3 x in GenRadial.RadialCellsAround(c, Math.Min(r * 2.4f, GenRadial.MaxRadialPatternRadius - 1f), true))
            {
                if (!x.InBounds(map)) return false;
                if (x.GetEdifice(map) != null) return false;
                all++;
                if (Writable(x.GetTerrain(map))) soft++;
            }
            return all > 0 && soft >= all * 0.92f;
        }

        /// <summary>The ash and the unburned pockets; never rock floor, water or anything built.</summary>
        private static bool Writable(TerrainDef t)
        {
            return t != null && !t.IsWater && (t.defName.StartsWith("RM_FE_Ash") || t.defName.StartsWith("RM_FE_Ground"));
        }

        private static void Dig(Map map, IntVec3 c, float r, TerrainDef deep, TerrainDef shallow, TerrainDef mud, TerrainDef rich)
        {
            float p1 = Rand.Range(0f, 6.283f), p2 = Rand.Range(0f, 6.283f);
            float a1 = Rand.Range(0.12f, 0.24f), a2 = Rand.Range(0.06f, 0.16f);
            float reach = Math.Min(r * 2.4f, GenRadial.MaxRadialPatternRadius - 1f);
            // Shore grain at a few cells' scale. A smooth wobble snapped to whole cells drew as long straight terraces at play
            // zoom (map p, 2026-11-07); vanilla only fades a shore half a cell, so the outline itself has to be ragged.
            var grain = new Perlin(0.28, 2.0, 0.5, 2, Rand.Int, QualityMode.Medium);
            foreach (IntVec3 x in GenRadial.RadialCellsAround(c, reach, true))
            {
                if (!x.InBounds(map) || x.GetEdifice(map) != null) continue;
                float dx = x.x - c.x, dz = x.z - c.z;
                double th = Math.Atan2(dz, dx);
                float rr = r * (1f + a1 * (float)Math.Sin(2 * th + p1) + a2 * (float)Math.Sin(3 * th + p2));
                float d = (float)Math.Sqrt(dx * dx + dz * dz) / rr + ShoreGrain * (float)grain.GetValue(x.x, 0, x.z);
                int ring = Ring(Math.Max(0f, d), r);
                if (ring < 0) continue;
                TerrainDef want = ring == 0 ? deep : ring == 1 ? shallow : ring == 2 ? mud : rich;
                TerrainDef cur = x.GetTerrain(map);
                if (cur != null && Rank(cur, deep, shallow, mud, rich) <= ring) continue;   // never dry a wetter cell
                if (cur != null && !Writable(cur) && !cur.IsWater && cur != mud && cur != rich) continue;
                map.terrainGrid.SetTerrain(x, want);
            }
        }

        /// <summary>How far the shore grain moves a band edge, as a share of the pond's radius.</summary>
        public const float ShoreGrain = 0.16f;

        /// <summary>0 deep water (big ponds only), 1 shallow water, 2 mud, 3 rich soil, -1 outside; d is distance over the
        /// pond's own radius at that angle. The mud and rich bands only seed the old ring; ReRing redraws them.</summary>
        public static int Ring(float d, float r)
        {
            if (d < 0.4f && r >= 6f) return 0;
            if (d < 1f) return 1;
            if (d < 1.4f) return 2;
            if (d < 2f) return 3;
            return -1;
        }

        private static int Rank(TerrainDef t, TerrainDef deep, TerrainDef shallow, TerrainDef mud, TerrainDef rich)
        {
            if (t == deep) return 0;
            if (t.IsWater) return 1;
            if (t == mud) return 2;
            if (t == rich) return 3;
            return 4;
        }

        // ── shared ──────────────────────────────────────────────────────────────────────────────────────────────────────

        /// <summary>
        /// Distance in cells from every cell to the nearest source cell (0 on a source), by the two-pass chamfer with straight
        /// steps 1 and diagonal steps sqrt 2: within 8% of true distance, in two sweeps of the grid. Index = z * sizeX + x,
        /// as CellIndices.
        /// </summary>
        internal static float[] Distance(int sx, int sz, bool[] source)
        {
            const float Far = 1e9f, Diag = 1.41421356f;
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
            float[] d = GenStep_PyrelandsStandingWater.Distance(map.Size.x, map.Size.z, water);
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
