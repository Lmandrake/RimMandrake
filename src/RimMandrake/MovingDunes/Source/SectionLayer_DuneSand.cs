using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MovingDunes
{
    /// <summary>
    /// The per-map skinned sand layer — MOVING_DUNES_DESIGN.md §2 "Rendering".
    ///
    /// Vanilla's <c>SectionLayer_Sand</c> draws opacity-blended windswept sand from ONE
    /// static shared material (<c>GetSubMesh(MatBases.Sand)</c>), so no per-map colour
    /// source exists anywhere in the engine. <c>Section</c>'s constructor instantiates
    /// every non-abstract <c>SectionLayer</c> subclass once per section per map, so a
    /// subclass is per-map by construction — that is the whole route.
    ///
    /// This subclasses <c>SectionLayer</c> DIRECTLY rather than <c>SectionLayer_Sand</c>
    /// on purpose: the suppression prefix in
    /// <see cref="Patch_SectionLayerSand_Regenerate"/> patches
    /// <c>SectionLayer_Sand.Regenerate</c>, and a subclass that did not override it
    /// would inherit that same patched method body and disable itself.
    ///
    /// Two things it adds over the vanilla layer:
    ///   1. the material def's <c>tint</c>, by whichever of the two routes the def names
    ///      (see <see cref="DuneTintMode"/> — the design's pre-build shader gate);
    ///   2. crest shading along the downwind depth gradient, which is what makes sand
    ///      legible ON sand at all — the reason vanilla excluded sand terrain.
    /// </summary>
    public class SectionLayer_DuneSand : SectionLayer
    {
        private readonly float[] adjValuesTmp = new float[9];
        private static readonly List<float> opacityListTmp = new List<float>();

        /// <summary>The per-map tinted clone of <c>MatBases.Sand</c>. Built lazily, once
        /// per section-layer; Unity materials are cheap clones of an already-loaded
        /// shader+texture pair.</summary>
        private Material tintedMat;
        private RM_DuneMaterialDef tintedFor;

        public SectionLayer_DuneSand(Section section)
            : base(section)
        {
            relevantChangeTypes = MapMeshFlagDefOf.Sand;
        }

        public override bool Visible
        {
            get
            {
                if (!DebugViewSettings.drawSand || !ModsConfig.OdysseyActive)
                {
                    return false;
                }
                return DuneFieldRegistry.IsActive(base.Map);
            }
        }

        private Material MaterialFor(RM_DuneMaterialDef def)
        {
            if (tintedMat != null && tintedFor == def)
            {
                return tintedMat;
            }
            tintedFor = def;
            tintedMat = new Material(MatBases.Sand);
            if (def.tintMode == DuneTintMode.MaterialColor)
            {
                tintedMat.color = def.tint;
            }
            return tintedMat;
        }

        public override void Regenerate()
        {
            MapComponent_DuneField field = DuneFieldRegistry.Get(base.Map);
            if (field == null || field.Material == null)
            {
                return;
            }
            RM_DuneMaterialDef def = field.Material;

            LayerSubMesh subMesh = GetSubMesh(MaterialFor(def));
            if (subMesh == null)
            {
                return;
            }
            if (subMesh.mesh.vertexCount == 0)
            {
                SectionLayerGeometryMaker_Solid.MakeBaseGeometry(section, subMesh, AltitudeLayer.Terrain);
            }
            subMesh.Clear(MeshParts.Colors);

            bool vertexTint = def.tintMode == DuneTintMode.VertexColor;
            byte tintR = ToByte(def.tint.r);
            byte tintG = ToByte(def.tint.g);
            byte tintB = ToByte(def.tint.b);

            IntVec3 wind = field.WindVector;
            float shade = Mathf.Clamp(def.crestShading, 0f, 0.5f);

            CellRect cellRect = section.CellRect;
            bool anySand = false;

            for (int x = cellRect.minX; x <= cellRect.maxX; x++)
            {
                for (int z = cellRect.minZ; z <= cellRect.maxZ; z++)
                {
                    IntVec3 cell = new IntVec3(x, 0, z);
                    float here = DepthAt(cell);

                    // Crest shading: the downwind gradient. A cell higher than the cell
                    // downwind of it is a crest (lighter, thinner-reading); a cell lower
                    // than the one upwind of it sits in a slip face (darker, denser).
                    // Applied to OPACITY in both tint modes, because alpha is the one
                    // channel of the vanilla sand shader whose meaning is not in doubt
                    // — this reads correctly whichever way the design's shader-tint gate
                    // falls. Vertex RGB gets it too, but only when we own RGB.
                    float relief = 0f;
                    if (shade > 0f && here > 0.001f)
                    {
                        IntVec3 down = cell + wind;
                        float downstream = down.InBounds(base.Map) ? DepthAt(down) : here;
                        relief = Mathf.Clamp(here - downstream, -1f, 1f) * shade;
                    }

                    opacityListTmp.Clear();
                    for (int k = 0; k < 9; k++)
                    {
                        IntVec3 c = cell + GenAdj.AdjacentCellsAndInsideForUV[k];
                        adjValuesTmp[k] = c.InBounds(base.Map) ? DepthAt(c) : here;
                    }
                    for (int l = 0; l < 9; l++)
                    {
                        List<int> weights = SectionLayer_Sand.vertexWeights[l];
                        float sum = 0f;
                        for (int m = 0; m < weights.Count; m++)
                        {
                            sum += adjValuesTmp[weights[m]];
                        }
                        float opacity = sum / weights.Count;
                        if (opacity > 0.01f)
                        {
                            anySand = true;
                        }
                        // A slip face reads denser, a crest thinner. Never below zero,
                        // never above full, so a fully-buried cell still reads buried.
                        opacityListTmp.Add(Mathf.Clamp01(opacity - relief));
                    }

                    if (!vertexTint)
                    {
                        // Vanilla meaning: red carries the pollution mask, alpha the opacity.
                        for (int n = 0; n < 9; n++)
                        {
                            IntVec3 c = cell + GenAdj.AdjacentCellsAndInsideForUV[n];
                            adjValuesTmp[n] = base.Map.pollutionGrid.IsPolluted(c) ? 1f : 0f;
                        }
                        for (int i = 0; i < 9; i++)
                        {
                            List<int> weights = SectionLayer_Sand.vertexWeights[i];
                            float sum = 0f;
                            for (int m = 0; m < weights.Count; m++)
                            {
                                sum += adjValuesTmp[weights[m]];
                            }
                            subMesh.colors.Add(new Color32(
                                ToByte(sum / weights.Count),
                                byte.MaxValue, byte.MaxValue,
                                ToByte(opacityListTmp[i])));
                        }
                    }
                    else
                    {
                        // We own RGB on a skinned map: the pollution mask is surrendered
                        // (design §2 says so explicitly — "red is free on skinned maps")
                        // and the tint, relief-modulated, goes there instead.
                        float lift = Mathf.Clamp(1f + relief * 2f, 0.5f, 1.5f);
                        byte r = ToByte(tintR / 255f * lift);
                        byte g = ToByte(tintG / 255f * lift);
                        byte b = ToByte(tintB / 255f * lift);
                        for (int i = 0; i < 9; i++)
                        {
                            subMesh.colors.Add(new Color32(r, g, b, ToByte(opacityListTmp[i])));
                        }
                    }
                }
            }

            if (anySand)
            {
                subMesh.disabled = false;
                subMesh.FinalizeMesh(MeshParts.Colors);
            }
            else
            {
                subMesh.disabled = true;
            }
        }

        // SandGrid.DepthGrid_Unsafe is INTERNAL — the vanilla layer reads the
        // NativeArray directly, a modded one cannot. GetDepth is the public route and
        // adds one bounds check per read; the layer only regenerates on a dirty
        // section, so this is not on any hot path.
        private float DepthAt(IntVec3 c)
        {
            return base.Map.sandGrid.GetDepth(c);
        }

        private static byte ToByte(float v)
        {
            return (byte)Mathf.Clamp(Mathf.RoundToInt(v * 255f), 0, 255);
        }
    }

    /// <summary>
    /// Suppresses the vanilla sand submesh on a skinned map so the two layers never
    /// double-draw. On an ordinary map the prefix falls straight through.
    /// </summary>
    public static class Patch_SectionLayerSand_Regenerate
    {
        private static AccessTools.FieldRef<MapDrawLayer, Map> mapRef;
        private static bool resolved;

        public static bool Prefix(SectionLayer_Sand __instance)
        {
            try
            {
                if (!resolved)
                {
                    resolved = true;
                    try
                    {
                        mapRef = AccessTools.FieldRefAccess<MapDrawLayer, Map>("map");
                    }
                    catch (Exception e)
                    {
                        mapRef = null;
                        Log.Error(MovingDunesMod.LogPrefix + "vanilla-sand-layer-suppression: "
                                  + "MapDrawLayer.map not found — the vanilla and skinned sand "
                                  + "layers WILL double-draw on skinned maps. " + e.Message);
                    }
                }
                if (mapRef == null)
                {
                    return true;
                }

                Map map = mapRef(__instance);
                if (!DuneFieldRegistry.IsActive(map))
                {
                    return true;
                }

                LayerSubMesh sm = __instance.GetSubMesh(MatBases.Sand);
                if (sm != null)
                {
                    sm.disabled = true;
                }
                return false;
            }
            catch (Exception e)
            {
                Log.ErrorOnce(MovingDunesMod.LogPrefix + "SectionLayer_Sand prefix threw, falling "
                              + "back to vanilla for the rest of this session: " + e, 0x5D07E3);
                return true;
            }
        }
    }
}
