using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // Owner 2026-10-20: "Sure would be nice if we couldn't see the sun shining THROUGH the planet when we're
    // looking at the dark side."
    //
    // Cause (measured live 2026-10-20, read from RW_PlanetAtmosphere's SunFlare.shader pass 1): Planet Atmosphere
    // draws its lens flare as a full-screen quad with ZTest Always and additive blend, weighted by the frame's
    // pixels at the sun disc's screen position. When the sun is behind the planet those pixels are the night
    // side, dim but not black, so a faint streak and halo are still added straight across the dark disc; with
    // the sun just past the limb the full flare runs over the planet.
    //
    // Fix: a postfix on PlanetAtmosphereRenderer.Update (resolved by name - no reference to that mod) swaps the
    // flare material's texture to black while the ray from the world camera toward the sun hits the planet
    // sphere, and restores the mod's own texture otherwise. The sun disc pass, the atmosphere, the rings and the
    // limb glow are untouched. Setting: sunFlareHiddenBehindPlanet (off = the flare as that mod draws it).
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_SunFlareOcclusionPatch
    {
        private static FieldInfo fMaterial;
        private static FieldInfo fTexture;
        private static FieldInfo fRadius;
        private static readonly int propFlare = Shader.PropertyToID("sunFlareTexture");
        private static bool warned;

        static RM_SunFlareOcclusionPatch()
        {
            try
            {
                Type t = AccessTools.TypeByName("RW_PlanetAtmosphere.PlanetAtmosphereRenderer");
                if (t == null) return; // Planet Atmosphere not loaded: nothing to do.
                fMaterial = AccessTools.Field(t, "materialSunFlear");
                fTexture = AccessTools.Field(t, "sunFlareTexture");
                fRadius = AccessTools.Field(t, "planetRadius");
                MethodInfo update = AccessTools.Method(t, "Update");
                if (fMaterial == null || fTexture == null || update == null)
                {
                    Log.Warning("[RM CreatureBehaviors] sun flare: Planet Atmosphere's renderer changed shape (material/texture/Update not found); the flare still shows through the planet.");
                    return;
                }
                new Harmony("mandrake.rm.creaturebehaviors.sunflare").Patch(update,
                    postfix: new HarmonyMethod(typeof(RM_SunFlareOcclusionPatch), nameof(Postfix_Update)));
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] sun flare: patch failed; the flare still shows through the planet: " + e);
            }
        }

        /// <summary>True when the ray from <paramref name="eye"/> along <paramref name="dir"/> (unit) hits a sphere of radius r at the origin, in front of the eye.</summary>
        public static bool RayHitsPlanet(Vector3 eye, Vector3 dir, float r)
        {
            float b = Vector3.Dot(eye, dir);
            float c = eye.sqrMagnitude - r * r;
            if (c <= 0f) return false;          // eye inside the sphere: never blank
            if (b >= 0f) return false;          // planet is behind the eye
            return b * b - c > 0f;
        }

        public static void Postfix_Update(object __instance)
        {
            try
            {
                Material mat = fMaterial.GetValue(__instance) as Material;
                if (mat == null) return;
                Texture own = fTexture.GetValue(__instance) as Texture;
                bool hide = false;
                if (RM_CreatureBehaviorsSettings.sunFlareHiddenBehindPlanet && Find.World != null)
                {
                    Camera cam = Find.WorldCamera;
                    if (cam != null)
                    {
                        float r = 100f;
                        if (fRadius != null && fRadius.GetValue(__instance) is float pr && pr > 50f && pr < 200f) r = pr; // sane range only
                        Vector3 sun = GenCelestial.CurSunPositionInWorldSpace();
                        if (sun.sqrMagnitude > 1e-8f)
                            hide = RayHitsPlanet(cam.transform.position, sun.normalized, r);
                    }
                }
                Texture want = hide ? (Texture)Texture2D.blackTexture : own;
                if (mat.GetTexture(propFlare) != want) mat.SetTexture(propFlare, want);
            }
            catch (Exception e)
            {
                if (!warned) { warned = true; Log.Warning("[RM CreatureBehaviors] sun flare: occlusion test failed (once): " + e.Message); }
            }
        }
    }
}
