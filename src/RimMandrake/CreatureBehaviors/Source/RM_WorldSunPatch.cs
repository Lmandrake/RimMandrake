using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY, part 2: the world-view SUN. Owner's card (2026-10-20) filed it as
    // "pin the sun direction ... so stars, sun disc and planet light stop spinning daily".
    //
    // Vanilla 1.6: GenCelestial.CurSunPositionInWorldSpace() turns 360 degrees per day (it reads TicksAbs), and four
    // things read it: GlobalDrawLayer_Sun.Rotation (the disc), GlobalDrawLayer_Stars.Rotation (the starfield; ours is
    // overridden by RM_WorldStarsPatch), WorldRendererUtility.UpdateGlobalShadersParams (the planet's lit side), and
    // Planet Atmosphere's renderer (_WorldSpaceLightPos0).
    //
    // A postfix here returns the direction toward the substellar point instead, while a game is being played.
    //
    // How it lives with Alien Worlds - Tidally Locked (read from AlienWorlds.TidallyLocked.dll, 2026-10-21). While its
    // planet type is active the mod patches this area twice. First, a prefix on SunPositionUnmodified forces day 0 at
    // noon, which freezes this method at (0,0,-1). Second, a postfix here sets y = clamp01(y + 0.15), which tilts the
    // sun up.
    // Our postfix runs at Priority.First, before that y-lift, and for Ash'karr's substellar point (0,0) it writes the
    // same (0,0,-1). So with the mod active nothing visible changes and its tilt still applies. With the mod inactive
    // (its planet type drops to Default when Worldbuilder is loaded, see this item's ledger note), the disc and the lit
    // side stop turning anyway.
    //
    // Substellar point: WeatherSuite's PlanetGeometryDef (read by name, no reference), else the first biome's
    // RM_PinnedSunExtension, else (0,0). Setting: worldSunPinned (off = vanilla, or the Alien Worlds sun).
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_WorldSunPatch
    {
        public const string PlanetGeometryDefType = "RimMandrake.StarWars.WeatherSuite.PlanetGeometryDef";

        private static Vector3? pinned;

        static RM_WorldSunPatch()
        {
            try
            {
                MethodInfo target = AccessTools.Method(typeof(GenCelestial), nameof(GenCelestial.CurSunPositionInWorldSpace));
                if (target == null)
                {
                    Log.Warning("[RM CreatureBehaviors] world sun: GenCelestial.CurSunPositionInWorldSpace not found; the planet-view sun turns daily.");
                    return;
                }
                new Harmony("mandrake.rm.creaturebehaviors.worldsun").Patch(target,
                    postfix: new HarmonyMethod(typeof(RM_WorldSunPatch).GetMethod(nameof(Postfix_CurSunPositionInWorldSpace)), Priority.First));
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] world sun: patch failed; the planet-view sun turns daily: " + e);
            }
        }

        /// <summary>The unit vector toward the substellar point, resolved once (defs do not change after load).</summary>
        public static Vector3 PinnedDirection()
        {
            if (pinned.HasValue) return pinned.Value;
            float lat = 0f, lon = 0f;
            string source = "default (0,0)";
            try
            {
                Type geo = GenTypes.GetTypeInAnyAssembly(PlanetGeometryDefType);
                if (geo != null)
                {
                    FieldInfo fLat = AccessTools.Field(geo, "substellarLat"), fLon = AccessTools.Field(geo, "substellarLon");
                    foreach (Def d in GenDefDatabase.GetAllDefsInDatabaseForDef(geo))
                    {
                        if (fLat != null && fLon != null)
                        {
                            lat = (float)fLat.GetValue(d);
                            lon = (float)fLon.GetValue(d);
                            source = "PlanetGeometryDef " + d.defName;
                        }
                        break;
                    }
                }
                if (source.StartsWith("default"))
                {
                    foreach (BiomeDef b in DefDatabase<BiomeDef>.AllDefsListForReading)
                    {
                        RM_PinnedSunExtension ext = b.GetModExtension<RM_PinnedSunExtension>();
                        if (ext == null) continue;
                        lat = ext.substellarLatitude;
                        lon = ext.substellarLongitude;
                        source = "RM_PinnedSunExtension on " + b.defName;
                        break;
                    }
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RM CreatureBehaviors] world sun: substellar point read failed, using (0,0): " + e.Message);
                lat = lon = 0f;
                source = "default (0,0) after error";
            }
            RM_WorldStarsMath.SubstellarDirection(lat, lon, out float x, out float y, out float z);
            pinned = new Vector3(x, y, z);
            Log.Message("[RM CreatureBehaviors] world sun pinned toward substellar (" + lat + ", " + lon + ") from " + source + ".");
            return pinned.Value;
        }

        public static void Postfix_CurSunPositionInWorldSpace(ref Vector3 __result)
        {
            if (!RM_WorldStarsMath.PinsWorldSun(RM_CreatureBehaviorsSettings.worldSunPinned, Current.ProgramState == ProgramState.Playing))
            {
                return;
            }
            __result = PinnedDirection();
        }
    }
}
