using System;
using System.Reflection;
using HarmonyLib;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // PLANET_GEOMETRY_WIDEN_SUN_STANDS_STILL: Sun & Shade's ONE reader of the planet's sun geometry.
    //
    // WeatherSuite's PlanetGeometryDef is the pluggable sun-angle provider
    // (design/RimMandrake/sun_and_shade_modularity_2026-10-19.md §2): WeatherSuite is generic and inert without one,
    // and Utinni ships Ash'karr's (RUT_WS_AshkarrGeometry). It carries the substellar point and `fixedSun`
    // (time of day = location, design/RimMandrake/unified_direct_sun_heat_2026-10-19.md DS7).
    //
    // This assembly does not reference WeatherSuite, so the def is read by TYPE NAME through reflection, once
    // (defs do not change after load). Every sun consumer here (the shade grid's ResolveSun, the pinned sky's
    // ResolveGeometry, the world-view sun) takes its substellar point, and so E and the bearing, from this class.
    // With no PlanetGeometryDef loaded, a caller's own fallback point is used (today a biome extension's
    // substellar* fields, which DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES (DS1) deletes).
    //
    // FixedSun is exposed for DS7 (a day/night world turns Direct Sun off); this item does not switch on it.
    // selftest: src/RimMandrake/Utils/selftest_planet_fixed_sun.py
    // ════════════════════════════════════════════════════════════════════
    public static class RM_PlanetSunGeometry
    {
        public const string PlanetGeometryDefType = "RimMandrake.StarWars.WeatherSuite.PlanetGeometryDef";

        private static bool resolved;
        private static bool loaded;
        private static float substellarLat;
        private static float substellarLon;
        private static bool fixedSun;
        private static string defName;

        /// <summary>True when a PlanetGeometryDef is loaded and was read.</summary>
        public static bool Loaded { get { Resolve(); return loaded; } }

        /// <summary>The def's `fixedSun`: the sun stands still over every map. False with no def.</summary>
        public static bool FixedSun { get { Resolve(); return loaded && fixedSun; } }

        /// <summary>The loaded def's defName, or null.</summary>
        public static string DefName { get { Resolve(); return defName; } }

        /// <summary>The substellar point (degrees): the PlanetGeometryDef's when one is loaded, else the fallback.</summary>
        public static void SubstellarPoint(float fallbackLat, float fallbackLon, out float lat, out float lon)
        {
            Resolve();
            if (loaded)
            {
                lat = substellarLat;
                lon = substellarLon;
            }
            else
            {
                lat = fallbackLat;
                lon = fallbackLon;
            }
        }

        /// <summary>The sun over a world tile: elevation E = 90 - arc to the substellar point (degrees, unclamped;
        /// negative is below the horizon) and the bearing toward it (degrees clockwise from north). False for an
        /// invalid tile (pocket maps) or no world grid.</summary>
        public static bool TrySunAt(PlanetTile tile, float fallbackLat, float fallbackLon, out float elevationDeg, out float bearingDeg)
        {
            elevationDeg = float.NaN;
            bearingDeg = float.NaN;
            if (Find.WorldGrid == null || !tile.Valid)
            {
                return false;
            }
            Vector2 longLat = Find.WorldGrid.LongLatOf(tile);
            SubstellarPoint(fallbackLat, fallbackLon, out float lat, out float lon);
            RM_MapComponent_PinnedSun.SunGeometry(longLat.y, longLat.x, lat, lon, out bearingDeg, out float arcDeg);
            elevationDeg = 90f - arcDeg;
            return true;
        }

        private static void Resolve()
        {
            if (resolved)
            {
                return;
            }
            resolved = true;
            try
            {
                Type geo = GenTypes.GetTypeInAnyAssembly(PlanetGeometryDefType);
                if (geo == null)
                {
                    return;
                }
                FieldInfo fLat = AccessTools.Field(geo, "substellarLat");
                FieldInfo fLon = AccessTools.Field(geo, "substellarLon");
                FieldInfo fFixed = AccessTools.Field(geo, "fixedSun");
                if (fLat == null || fLon == null)
                {
                    Log.Warning("[RM CreatureBehaviors] planet sun: " + PlanetGeometryDefType + " has no substellarLat/Lon; using each biome's own point.");
                    return;
                }
                foreach (Def d in GenDefDatabase.GetAllDefsInDatabaseForDef(geo))
                {
                    substellarLat = (float)fLat.GetValue(d);
                    substellarLon = (float)fLon.GetValue(d);
                    fixedSun = fFixed != null && (bool)fFixed.GetValue(d);
                    defName = d.defName;
                    loaded = true;
                    break;
                }
                if (loaded && fFixed == null)
                {
                    Log.Warning("[RM CreatureBehaviors] planet sun: " + PlanetGeometryDefType + " has no fixedSun field (old WeatherSuite); reading it as false.");
                }
            }
            catch (Exception e)
            {
                loaded = false;
                Log.Warning("[RM CreatureBehaviors] planet sun: PlanetGeometryDef read failed, using each biome's own point: " + e.Message);
            }
        }
    }
}
