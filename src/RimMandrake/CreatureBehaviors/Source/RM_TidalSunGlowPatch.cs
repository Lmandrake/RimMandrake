using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // SUN_GLOW_DECIDE_WEST_TERMINATOR_SUNBATHING. Owner, by card 2026-10-20: "Light follows the sun".
    //
    // A POSTFIX on GenCelestial.CelestialSunGlow(PlanetTile,int) — every map's glow (CurCelestialSunGlow(map) ->
    // CelestialSunGlow(map.Tile, ticks)) goes through it. A postfix runs whatever Alien Worlds' skipping prefix
    // returned, so it simply overwrites the mod's lopsided value with RM_TidalSunGlowMath (sun elevation alone).
    //
    // Guard: it acts ONLY while 7f.alienworlds.tidallylocked's own patch sits on this method — the mod applies its
    // patches only while TidallyLocked is the active planet type (PlanetTypeDef.OnActivate/OnDeactivate). Not locked,
    // mod absent, or setting off => vanilla/the mod's value untouched. The owner check is re-read every 2 s of wall
    // time (Environment.TickCount, thread-safe), never per call.
    // Setting: tidalSunGlowByGeometry (default on), tidalTwilightBandDegrees (default 6).
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_TidalSunGlowPatch
    {
        public const string TidalLockHarmonyId = "7f.alienworlds.tidallylocked";

        private static MethodBase target;
        private static volatile bool lockActive;
        private static int nextCheckMs = int.MinValue;
        private static bool checkedOnce;

        static RM_TidalSunGlowPatch()
        {
            try
            {
                target = AccessTools.Method(typeof(GenCelestial), nameof(GenCelestial.CelestialSunGlow),
                    new[] { typeof(PlanetTile), typeof(int) });
                if (target == null)
                {
                    Log.Warning("[RM CreatureBehaviors] tidal sun glow: GenCelestial.CelestialSunGlow(PlanetTile,int) not found; "
                        + "tidal-lock light stays the Alien Worlds mod's own.");
                    return;
                }
                new Harmony("mandrake.rm.creaturebehaviors.tidalsunglow").Patch(target,
                    postfix: new HarmonyMethod(typeof(RM_TidalSunGlowPatch), nameof(Postfix_CelestialSunGlow)));
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] tidal sun glow: patch failed; tidal-lock light stays the mod's own: " + e);
            }
        }

        /// <summary>True while Alien Worlds - Tidally Locked has its patch on CelestialSunGlow (the planet is locked).</summary>
        public static bool TidalLockActive()
        {
            int now = Environment.TickCount;
            if (checkedOnce && now - nextCheckMs < 0) return lockActive;
            bool active = false;
            try
            {
                Patches info = target == null ? null : Harmony.GetPatchInfo(target);
                if (info != null)
                {
                    foreach (string owner in info.Owners)
                    {
                        if (owner == TidalLockHarmonyId) { active = true; break; }
                    }
                }
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM CreatureBehaviors] tidal sun glow: lock check failed: " + e.Message, 0x7A1D5);
            }
            lockActive = active;
            nextCheckMs = now + 2000;
            checkedOnce = true;
            return active;
        }

        public static void Postfix_CelestialSunGlow(PlanetTile tile, ref float __result)
        {
            if (!RM_CreatureBehaviorsSettings.tidalSunGlowByGeometry || !TidalLockActive()) return;
            try
            {
                if (Find.WorldGrid == null) return;
                Vector2 longLat = Find.WorldGrid.LongLatOf(tile);
                __result = RM_TidalSunGlowMath.GlowAt(longLat.y, longLat.x, RM_CreatureBehaviorsSettings.tidalTwilightBandDegrees);
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM CreatureBehaviors] tidal sun glow postfix: " + e, 0x7A1D6);
            }
        }
    }
}
