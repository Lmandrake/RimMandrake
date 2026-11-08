using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
    /// <summary>
    /// PIT_COVER_SOD (bar pit_covered_invisible): a lid that prints ground also prints the low wild plant the ground round it
    /// carries, so a covered pit in a grassy field is not a bare square. Called from Building_PitCover.Print (the ground
    /// branch only: a lid showing its plank art grows nothing). The census and the layout rules are RM_PitCoverSodMath's;
    /// the drawing is vanilla Plant.Print's (mesh count, sub-square layout and jitter, Graphic_Random variant, flip, atlas,
    /// wind-sway vertex alpha, snow overlay over 0.8 snow, shadow), seeded by the lid's position.
    /// Refresh: the sod is part of the lid's things-mesh print, so it re-reads its surroundings only when that section
    /// regenerates (a plant spawned, cut or grown a stage in the same section dirties it; one across a section edge waits
    /// for the next regeneration). No per-tick work, by design.
    /// </summary>
    public static class RM_PitCoverSod
    {
        // vanilla Plant.workingColors: rgb 0, wind exposure in the alpha of the top two vertices
        private static readonly Color32[] windColors = new Color32[4];
        private static readonly int[] keys = new int[80];
        private static readonly Plant[] samples = new Plant[80];
        private static readonly List<ThingDef> defs = new List<ThingDef>(8);

        /// <summary>Is <paramref name="p"/> sod: a low wild plant, drawn where it stands (vanilla SectionLayer_Things hides a
        /// plant under deep enough snow or sand, and one on thin ice that does not show in frozen water)?</summary>
        public static bool IsSod(Plant p, Map map)
        {
            PlantProperties pp = p?.def?.plant;
            if (pp == null || pp.IsTree || p.sown || p.LifeStage == PlantLifeStage.Sowing || p.def.graphicData == null)
            {
                return false;
            }
            if (pp.visualSizeRange.max > RM_PitCoverSodMath.MaxVisualSize)
            {
                return false;
            }
            return !HiddenAt(p.def, p.Position, map);
        }

        private static bool HiddenAt(ThingDef def, IntVec3 c, Map map)
        {
            if (def.hideAtSnowOrSandDepth < 1f && Mathf.Max(c.GetSnowDepth(map), c.GetSandDepth(map)) > def.hideAtSnowOrSandDepth)
            {
                return true;
            }
            return def.plant != null && !def.plant.showInFrozenWater && c.GetTerrain(map) == TerrainDefOf.ThinIce;
        }

        /// <summary>Prints the sod on <paramref name="lid"/>'s square into <paramref name="layer"/>, if its surroundings carry
        /// enough of it. <paramref name="surface"/>: the terrain the lid printed (sod is not drawn where that terrain would hide
        /// it). Returns whether anything was printed.</summary>
        public static bool TryPrint(Building_PitCover lid, SectionLayer layer, TerrainDef surface)
        {
            Map map = lid?.Map;
            if (map == null || !RimMandrakeFlowWorksSettings.pitCoverSodEnabled)
            {
                return false;
            }
            RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
            IntVec3 c = lid.Position;
            // the census: rings outward until a full ring's worth of ground squares (a lid inside a wide deck reads past it)
            defs.Clear();
            int n = 0;
            for (int r = 1; r <= RM_PitCoverSodMath.MaxRing && n < RM_PitCoverSodMath.WantSamples; r++)
            {
                int[] ring = RM_PitCoverSodMath.RingOffsets(r);
                for (int i = 0; i + 1 < ring.Length && n < keys.Length; i += 2)
                {
                    IntVec3 g = new IntVec3(c.x + ring[i], 0, c.z + ring[i + 1]);
                    if (!g.InBounds(map) || (eng != null && eng.HollowDepthAt(g) != 0) || RM_PitCoverUtility.CoverAt(map, g) != null)
                    {
                        continue;
                    }
                    Plant p = g.GetPlant(map);
                    int key = -1;
                    if (p != null && IsSod(p, map))
                    {
                        key = defs.IndexOf(p.def);
                        if (key < 0)
                        {
                            key = defs.Count;
                            defs.Add(p.def);
                        }
                    }
                    keys[n] = key;
                    samples[n] = key >= 0 ? p : null;
                    n++;
                }
            }
            int carriers = 0;
            for (int i = 0; i < n; i++)
            {
                if (keys[i] >= 0)
                {
                    carriers++;
                }
            }
            int win = RM_PitCoverSodMath.Enough(carriers, n) ? RM_PitCoverSodMath.Commonest(keys, n, out _) : -1;
            Plant rep = null;
            float growth = 0f;
            if (win >= 0)
            {
                int m = 0;
                for (int i = 0; i < n; i++)
                {
                    if (keys[i] == win)
                    {
                        growth += samples[i].Growth;
                        m++;
                    }
                }
                growth /= Mathf.Max(1, m);
                // the neighbour nearest the mean growth lends its graphic (immature, leafless, polluted as it stands)
                float bestGap = float.MaxValue;
                for (int i = 0; i < n; i++)
                {
                    if (keys[i] == win && Mathf.Abs(samples[i].Growth - growth) < bestGap)
                    {
                        bestGap = Mathf.Abs(samples[i].Growth - growth);
                        rep = samples[i];
                    }
                }
            }
            System.Array.Clear(samples, 0, n);
            defs.Clear();
            if (rep == null || HiddenAt(rep.def, c, map) || (surface != null && surface == TerrainDefOf.ThinIce && !rep.def.plant.showInFrozenWater))
            {
                return false;
            }
            Print(lid, rep, growth, layer);
            return true;
        }

        /// <summary>vanilla Plant.Print for <paramref name="rep"/>'s def at <paramref name="growth"/>, on the lid's square.</summary>
        private static void Print(Building_PitCover lid, Plant rep, float growth, SectionLayer layer)
        {
            Map map = lid.Map;
            ThingDef def = rep.def;
            IntVec3 c = lid.Position;
            // the plant's own altitude (LowPlant for grass): above the lid's FloorEmplacement ground print, below items and pawns
            Vector3 centre = c.ToVector3Shifted();
            centre.y = def.Altitude;
            bool snowy = c.GetSnowDepth(map) > 0.8f;
            Rand.PushState();
            try
            {
                Rand.Seed = c.GetHashCode();
                int max = Mathf.Max(1, def.plant.maxMeshCount);
                int meshes = RM_PitCoverSodMath.MeshCount(growth, max);
                float sizeFactor = def.plant.visualSizeRange.LerpThroughRange(growth);
                float size = def.graphicData.drawSize.x * sizeFactor;
                int side = RM_PitCoverSodMath.GridSide(max);
                int[] order = RM_PitCoverSodMath.PositionOrder(max, c.GetHashCode());
                Graphic graphic = rep.Graphic;
                Graphic snowGraphic = snowy ? rep.SnowOverlayGraphic : null;
                if (graphic == null)
                {
                    return;
                }
                PlantUtility.SetWindExposureColors(windColors, rep);
                TextureAtlasGroup atlas = def.category.ToAtlasGroup();
                int payload = lid.HashOffset() % 1024;
                bool lifted = false;
                int drawn = 0;
                foreach (int index in order)
                {
                    Vector3 pos;
                    if (max == 1)
                    {
                        pos = centre + Gen.RandomHorizontalVector(0.05f);
                        pos.z = RM_PitCoverSodMath.ClampSingleZ(pos.z, c.z, sizeFactor, out bool up);
                        lifted |= up;
                    }
                    else
                    {
                        RM_PitCoverSodMath.SubSquareCentre(index, side, out float dx, out float dz);
                        pos = new Vector3(c.x + dx, def.Altitude, c.z + dz);
                        pos += Gen.RandomHorizontalVector(RM_PitCoverSodMath.JitterMax(side));
                    }
                    bool flip = Rand.Bool;
                    Material mat = graphic.MatSingleFor(rep);
                    Material snowMat = snowGraphic?.MatSingleFor(rep);
                    if (graphic is Graphic_Random random && random.SubGraphicsCount > 0)
                    {
                        int variant = Rand.Range(0, random.SubGraphicsCount);
                        mat = random.SubGraphicAtIndex(variant).MatSingle;
                        if (snowGraphic is Graphic_Random snowRandom && variant < snowRandom.SubGraphicsCount)
                        {
                            snowMat = snowRandom.SubGraphicAtIndex(variant).MatSingle;
                        }
                    }
                    if (mat == null)
                    {
                        break;
                    }
                    Graphic.TryGetTextureAtlasReplacementInfo(mat, atlas, flip, false, out mat, out Vector2[] uvs, out _);
                    Vector2 quad = new Vector2(size, size);
                    Printer_Plane.PrintPlane(layer, pos, quad, mat, 0f, flip, uvs, windColors, 0.1f, payload);
                    if (snowMat != null)
                    {
                        Graphic.TryGetTextureAtlasReplacementInfo(snowMat, atlas, flip, false, out snowMat, out uvs, out _);
                        Printer_Plane.PrintPlane(layer, pos.WithYOffset(0.0003658537f), quad, snowMat, 0f, flip, uvs, windColors, 0.1f, payload);
                    }
                    if (++drawn >= meshes)
                    {
                        break;
                    }
                }
                ShadowData shadow = def.graphicData.shadowData;
                if (shadow != null)
                {
                    Vector3 sc = centre + shadow.offset * sizeFactor;
                    if (lifted)
                    {
                        sc.z = c.ToVector3Shifted().z + shadow.offset.z;
                    }
                    sc.y -= Altitudes.AltInc;
                    Printer_Shadow.PrintShadow(layer, sc, shadow.volume * sizeFactor, Rot4.North);
                }
            }
            finally
            {
                Rand.PopState();
            }
        }

        /// <summary>The sod setting changed: every lid re-prints (its things mesh regenerates), on every map.</summary>
        public static void RedrawAllLids()
        {
            if (Current.ProgramState != ProgramState.Playing || Find.Maps == null)
            {
                return;
            }
            foreach (Map map in Find.Maps)
            {
                if (map?.mapDrawer == null)
                {
                    continue;
                }
                foreach (Building b in map.listerBuildings.allBuildingsColonist)
                {
                    if (b is Building_PitCover)
                    {
                        map.mapDrawer.MapMeshDirty(b.Position, (ulong)MapMeshFlagDefOf.Things | (ulong)MapMeshFlagDefOf.Buildings);
                    }
                }
                foreach (Building b in map.listerBuildings.allBuildingsNonColonist)
                {
                    if (b is Building_PitCover)
                    {
                        map.mapDrawer.MapMeshDirty(b.Position, (ulong)MapMeshFlagDefOf.Things | (ulong)MapMeshFlagDefOf.Buildings);
                    }
                }
            }
        }
    }
}
