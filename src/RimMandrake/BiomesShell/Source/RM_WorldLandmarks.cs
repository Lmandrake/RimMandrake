using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Biomes
{
    // SOFT LANDMARK ICONS (owner by card 2026-10-20, "Fade and shrink icons"; LANDMARK_ICONS_DECIDE_THE_REAL_SPECKLE).
    //
    // How vanilla 1.6 draws them (RimSage, WorldDrawLayer_Landmarks): one quad per Standard landmark, size = tile size x
    // LandmarkDef.drawScale, lifted +0.0075 (+0.025 when drawAboveRoads, i.e. over rivers and roads), random rotation and
    // random cell of the def's iconTexturePath atlas, on LandmarkDef.Material = MaterialPool(iconTexturePath,
    // WorldOverlayTransparentLit, queue 3510). On the Rust Cathedral 155 of 236 tiles carry one, which reads as speckle.
    //
    // Look only. The world's landmarks, their tiles and their hover/inspect text are untouched; only the icon mesh is drawn
    // smaller and fainter:
    // - OPACITY through the engine's own fade: WorldDrawLayerBase.Render multiplies the material colour's alpha by the
    //   virtual Alpha property through a MaterialPropertyBlock. A postfix on the Alpha getter returns a lower value for
    //   the landmark layer only. Per frame, so it follows the camera and the setting at once.
    // - SIZE by shrinking each quad about its own centre. Vanilla's vertices are captured after each Regenerate and the
    //   mesh is rewritten from them only when the (quantized) scale changes.
    // Both ease back to vanilla as the camera zooms in close (AltitudePercent below fullAt), so an icon is still found
    // and read where the player looks at one tile. Off restores vanilla at once, without a redraw.
    [StaticConstructorOnStartup]
    public static class RM_WorldLandmarks
    {
        public static float fullAt = 0.05f;    // AltitudePercent at or below which icons draw as vanilla
        public static float softAt = 0.20f;    // at or above which they draw at the settings' size and opacity
        public static float scaleStep = 0.05f; // mesh is rewritten only when the scale moves by this much

        public static string lastInfo = "never built";

        sealed class Captured
        {
            public readonly List<LayerSubMesh> subs = new List<LayerSubMesh>();
            public readonly List<Vector3[]> verts = new List<Vector3[]>();
            public float applied = 1f;
        }

        static readonly FieldInfo SubMeshesField = AccessTools.Field(typeof(WorldDrawLayerBase), "subMeshes");
        // weak: a world reload drops its layers; a strong map would pin every dead layer
        static readonly System.Runtime.CompilerServices.ConditionalWeakTable<WorldDrawLayer_Landmarks, Captured> Caps =
            new System.Runtime.CompilerServices.ConditionalWeakTable<WorldDrawLayer_Landmarks, Captured>();

        static RM_WorldLandmarks()
        {
            try
            {
                var h = new Harmony("mandrake.rm.biomes.worldlandmarks");
                h.Patch(AccessTools.Method(typeof(WorldDrawLayer_Landmarks), "Regenerate"),
                    postfix: new HarmonyMethod(typeof(RM_WorldLandmarks), nameof(RegeneratePostfix)));
                h.Patch(AccessTools.PropertyGetter(typeof(WorldDrawLayerBase), "Alpha"),
                    postfix: new HarmonyMethod(typeof(RM_WorldLandmarks), nameof(AlphaPostfix)));
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake.Biomes] soft landmark icons patch failed, icons keep the vanilla look: " + e.Message);
            }
        }

        // 0 = close in (vanilla), 1 = far out (fully softened)
        public static float Softness()
        {
            if (!RM_BiomesSettings.worldSoftLandmarks) return 0f;
            if (!RM_BiomesSettings.worldLandmarksFullClose) return 1f;
            WorldCameraDriver cam = Find.WorldCameraDriver;
            if (cam == null) return 1f;
            return Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(fullAt, Mathf.Max(fullAt + 0.001f, softAt), cam.AltitudePercent));
        }

        public static float TargetScale(float soft) => Mathf.Lerp(1f, Mathf.Clamp(RM_BiomesSettings.worldLandmarkSize, 0.1f, 1f), soft);
        public static float TargetAlpha(float soft) => Mathf.Lerp(1f, Mathf.Clamp(RM_BiomesSettings.worldLandmarkOpacity, 0.05f, 1f), soft);

        static void AlphaPostfix(WorldDrawLayerBase __instance, ref float __result)
        {
            if (!(__instance is WorldDrawLayer_Landmarks layer)) return;
            try
            {
                float soft = Softness();
                __result *= TargetAlpha(soft);
                if (Caps.TryGetValue(layer, out Captured cap))
                {
                    float s = TargetScale(soft);
                    if (s >= 0.999f) s = 1f;
                    else s = Mathf.Max(0.1f, Mathf.Round(s / scaleStep) * scaleStep);
                    if (!Mathf.Approximately(s, cap.applied)) Rescale(cap, s);
                }
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RimMandrake.Biomes] soft landmark icons failed: " + e, 0x524c4d31);
            }
        }

        static void RegeneratePostfix(ref IEnumerable __result, WorldDrawLayer_Landmarks __instance)
        {
            __result = Wrap(__result, __instance);
        }

        static IEnumerable Wrap(IEnumerable inner, WorldDrawLayer_Landmarks layer)
        {
            foreach (object o in inner) yield return o;
            try
            {
                // vanilla just finalized meshes at full size; capture them so every scale is computed from the original
                var cap = new Captured();
                int quads = 0;
                foreach (LayerSubMesh sm in (List<LayerSubMesh>)SubMeshesField.GetValue(layer))
                {
                    if (!sm.finalized || sm.verts.Count == 0 || sm.verts.Count % 4 != 0) continue;
                    cap.subs.Add(sm);
                    cap.verts.Add(sm.verts.ToArray());
                    quads += sm.verts.Count / 4;
                }
                Caps.Remove(layer);
                Caps.Add(layer, cap);
                lastInfo = quads + " landmark quads in " + cap.subs.Count + " submeshes captured";
            }
            catch (Exception e)
            {
                lastInfo = "capture failed: " + e.Message;
                Log.ErrorOnce("[RimMandrake.Biomes] soft landmark icons capture failed, icons keep their size: " + e, 0x524c4d32);
            }
        }

        // every quad shrinks about its own centre (4 vertices per quad, PrintQuadTangentialToPlanet); lift is kept
        static void Rescale(Captured cap, float s)
        {
            for (int k = 0; k < cap.subs.Count; k++)
            {
                LayerSubMesh sm = cap.subs[k];
                Vector3[] orig = cap.verts[k];
                if (sm.mesh == null || sm.verts.Count != orig.Length) continue;   // regenerated under us; next capture fixes it
                for (int q = 0; q < orig.Length; q += 4)
                {
                    Vector3 c = (orig[q] + orig[q + 1] + orig[q + 2] + orig[q + 3]) * 0.25f;
                    for (int j = 0; j < 4; j++) sm.verts[q + j] = c + (orig[q + j] - c) * s;
                }
                sm.mesh.SetVertices(sm.verts);
                sm.mesh.RecalculateBounds();
            }
            cap.applied = s;
        }

        // ---------------------------------------------------------------- bridge helpers (jawa/static_call)
        public static string Set(string key, string value)
        {
            FieldInfo f = typeof(RM_WorldLandmarks).GetField(key, BindingFlags.Static | BindingFlags.Public);
            if (f == null || f.FieldType != typeof(float)) return "no float field " + key;
            f.SetValue(null, float.Parse(value, System.Globalization.CultureInfo.InvariantCulture));
            return key + " = " + f.GetValue(null);
        }

        public static string Info()
        {
            float soft = Softness();
            return lastInfo + " | on=" + RM_BiomesSettings.worldSoftLandmarks + " size=" + RM_BiomesSettings.worldLandmarkSize
                   + " opacity=" + RM_BiomesSettings.worldLandmarkOpacity + " fullClose=" + RM_BiomesSettings.worldLandmarksFullClose
                   + " | altitude%=" + (Find.WorldCameraDriver?.AltitudePercent ?? -1f) + " softness=" + soft
                   + " scale=" + TargetScale(soft) + " alpha=" + TargetAlpha(soft) + " | fullAt=" + fullAt + " softAt=" + softAt;
        }
    }
}
