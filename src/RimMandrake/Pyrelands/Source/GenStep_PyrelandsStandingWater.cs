using System;
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
    /// Right after Terrain (210): a map holding fewer than MinWaterCells water cells gets two or three small ponds, each
    /// ringed the way the noise ponds are (shallow water, mud, rich soil), on the ash away from the edges, rock and the
    /// landing spot. A map the noise already watered is left alone.
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
            TerrainDef deep = TerrainDefOf.WaterDeep, shallow = TerrainDefOf.WaterShallow, mud = TerrainDefOf.Mud;
            TerrainDef rich = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_FE_Ground_SoilRich") ?? TerrainDefOf.Soil;
            if (WaterCells(map) < minWaterCells) DigPonds(map, deep, shallow, mud, rich);
            FirmBanks(map, mud, rich);
        }

        /// <summary>
        /// Firm stretches of bank. Every pond, the noise ponds and the dug ones alike, came ringed all the way round in vanilla Mud,
        /// and FlowWorks will neither dig Mud (it slides back) nor pass water through it, so no canal could ever reach the water and
        /// a watered strip of ash was out of a player's reach (map p, 2026-11-07). Where a coarse noise says so, a Mud cell is rich
        /// soil instead: about four banks in ten are firm, in runs several cells long, and the rest stay muddy.
        /// </summary>
        private static void FirmBanks(Map map, TerrainDef mud, TerrainDef rich)
        {
            var bank = new Perlin(0.07, 2.0, 0.5, 2, Rand.Int, QualityMode.Medium);
            TerrainGrid g = map.terrainGrid;
            for (int i = 0; i < map.cellIndices.NumGridCells; i++)
            {
                if (g.TerrainAt(i) != mud) continue;
                IntVec3 c = map.cellIndices.IndexToCell(i);
                if (c.GetEdifice(map) != null) continue;
                if (bank.GetValue(c.x, 0, c.z) > FirmBankNoise) g.SetTerrain(c, rich);
            }
        }

        /// <summary>Bank noise above this is firm ground; about 40% of a Perlin field lies above 0.1.</summary>
        public const double FirmBankNoise = 0.1;

        private void DigPonds(Map map, TerrainDef deep, TerrainDef shallow, TerrainDef mud, TerrainDef rich)
        {
            int wanted = pondCount.RandomInRange;
            var centres = new System.Collections.Generic.List<IntVec3>();
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
            }
            if (centres.Count < wanted)
            {
                Log.Warning("[RimMandrake.Pyrelands] standing water: dug " + centres.Count + " of " + wanted
                            + " ponds; the map had no room on open ash for the rest.");
            }
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
        /// pond's own radius at that angle.</summary>
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
    }
}
