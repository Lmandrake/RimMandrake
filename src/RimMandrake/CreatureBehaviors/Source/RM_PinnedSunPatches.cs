using System;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // LONGSHADE_BEDAZZLE_MECHANICS_1 part 1 — pinned shadow OPACITY.
    //
    // SkyManager.SkyManagerUpdate (RimSage, 1.6) writes the sun-shadow vector
    // as Vector4(vec.x, 0, vec.y, GenCelestial.CurShadowStrength(map)). The
    // vector itself is pinned by RM_WeatherEvent_PinnedSun's
    // OverrideShadowVector, but the w component still follows the REAL
    // turning sun — CurShadowStrength is 0 whenever real sun glow crosses
    // 0.6, so a pinned-sun map's shadows would fade out twice a day.
    //
    // Postfix on SkyManagerUpdate (a large method — no inlining risk, unlike
    // a patch on the tiny GenCelestial.CurShadowStrength), current map only,
    // same condition vanilla uses: re-write the global with the pinned
    // vector and the extension's own shadowStrength. Inert on every map whose
    // biome carries no RM_PinnedSunExtension, and whenever the pin is off.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_PinnedSunPatches
    {
        static RM_PinnedSunPatches()
        {
            try
            {
                Harmony harmony = new Harmony("mandrake.rm.creaturebehaviors.pinnedsun");
                MethodInfo target = AccessTools.Method(typeof(SkyManager), nameof(SkyManager.SkyManagerUpdate));
                if (target == null)
                {
                    Log.Warning("[RM CreatureBehaviors] pinned sun: SkyManager.SkyManagerUpdate not found; "
                        + "pinned shadows will fade with the real sun (sky and vector still pinned).");
                    return;
                }
                harmony.Patch(target, postfix: new HarmonyMethod(typeof(RM_PinnedSunPatches), nameof(Postfix_SkyManagerUpdate)));
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] pinned sun: patch failed; shadows follow the real sun's opacity: " + e);
            }
        }

        public static void Postfix_SkyManagerUpdate(Map ___map)
        {
            try
            {
                if (___map == null || ___map != Find.CurrentMap || ___map.gameConditionManager.IsAlwaysDarkOutside)
                {
                    return;
                }
                RM_MapComponent_PinnedSun pin = RM_MapComponent_PinnedSun.For(___map);
                if (pin == null || !pin.IsActive)
                {
                    return;
                }
                Vector2 v = pin.RenderedShadowVector;
                float strength = Mathf.Clamp01(pin.Extension.shadowStrength);
                Shader.SetGlobalVector(ShaderPropertyIDs.MapSunLightDirection, new Vector4(v.x, 0f, v.y, strength));
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM CreatureBehaviors] pinned sun postfix: " + e, 0x5E1A7);
            }
        }
    }
}
