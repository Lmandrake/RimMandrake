using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// LONGSHADE_BEDAZZLE_MECHANICS_1 part 1 — the pinned sun (golden hour).
    /// See RM_PinnedSunExtension for the design citation.
    ///
    /// HOW (MEASURED via RimSage against the 1.6 decompile, 2026-09-29):
    /// SkyManager.CurrentSkyTarget lerps the weather's sky toward every live
    /// WeatherEvent whose SkyTargetLerpFactor > 0, and GetOverridenShadowVector
    /// returns the FIRST live WeatherEvent's non-null OverrideShadowVector
    /// before it ever consults CompAffectsSky things. So one never-expiring
    /// WeatherEvent (RM_WeatherEvent_PinnedSun) gives all three things §3.1
    /// asks for — glow, colour set and the shadow vector — with no invisible
    /// map-anchor Thing in the save at all (the §3.1 draft's CompAffectsSky
    /// route works too, but leaves a Thing behind when the mod is removed).
    /// WeatherEventHandler's live list is NOT saved, so this component re-adds
    /// the event on FinalizeInit and re-checks it every CheckIntervalTicks
    /// (which is also how the Mod Settings toggle takes effect live).
    ///
    /// The one thing the event cannot pin is shadow OPACITY: SkyManager writes
    /// GenCelestial.CurShadowStrength (from the real turning sun) into the
    /// shadow vector's w — RM_PinnedSunPatches re-writes it afterwards.
    ///
    /// Gated on the BIOME (the map's BiomeDef must carry RM_PinnedSunExtension)
    /// and on a valid planet tile (pocket maps never get one).
    ///
    /// PUBLIC CONTRACT for the directional shade grid (SOLAR_HEAT_EXPOSURE_1
    /// spec 3), the smoke calendar's haze, and anything else that needs the
    /// sun: For(map), IsActive, ShadowDirection, SunElevationDegrees,
    /// ShadowLengthPerHeight, and the settable ShadowLengthFactor.
    /// </summary>
    public class RM_MapComponent_PinnedSun : MapComponent
    {
        private const int CheckIntervalTicks = 250;

        private RM_WeatherEvent_PinnedSun liveEvent;

        private bool geometryResolved;
        private Vector2 shadowDirection = new Vector2(0f, -1f);
        private float elevationDegrees = 45f;

        /// <summary>Multiplier on every shadow's length, 1 by default. Not
        /// saved: whatever lengthens the shadows (the ruled smoke calendar's
        /// haze act, §3.3 "haze … lengthens the vector") re-asserts it while
        /// it runs and sets it back to 1 when it ends.</summary>
        public float ShadowLengthFactor = 1f;

        public RM_MapComponent_PinnedSun(Map map) : base(map)
        {
        }

        public static RM_MapComponent_PinnedSun For(Map map)
        {
            return map?.GetComponent<RM_MapComponent_PinnedSun>();
        }

        public RM_PinnedSunExtension Extension => map?.Biome?.GetModExtension<RM_PinnedSunExtension>();

        /// <summary>True while this map's sun is pinned: the biome carries the
        /// extension, the tile is a real planet tile, and the Mod Settings
        /// toggle is on.</summary>
        public bool IsActive => RM_CreatureBehaviorsSettings.pinnedSunEnabled
                                && Extension != null
                                && map.Tile.Valid;

        /// <summary>Unit vector, map space (x = east, y = north/z), pointing
        /// the way shadows fall — away from the sun.</summary>
        public Vector2 ShadowDirection
        {
            get { ResolveGeometry(); return shadowDirection; }
        }

        public float SunElevationDegrees
        {
            get { ResolveGeometry(); return elevationDegrees; }
        }

        /// <summary>Cells of ground shadow per unit of caster height:
        /// cot(elevation) × ShadowLengthFactor. True geometry — the rendered
        /// vector is scaled separately for looks (renderLengthScale).</summary>
        public float ShadowLengthPerHeight
        {
            get
            {
                ResolveGeometry();
                float elev = Mathf.Max(0.5f, elevationDegrees) * Mathf.Deg2Rad;
                return Mathf.Cos(elev) / Mathf.Sin(elev) * Mathf.Max(0f, ShadowLengthFactor);
            }
        }

        /// <summary>The vector SkyManager renders shadows along.</summary>
        public Vector2 RenderedShadowVector
        {
            get
            {
                RM_PinnedSunExtension ext = Extension;
                if (ext == null)
                {
                    return shadowDirection;
                }
                float length = Mathf.Clamp(ShadowLengthPerHeight * ext.renderLengthScale,
                    ext.minRenderLength, ext.maxRenderLength);
                return shadowDirection * length;
            }
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            geometryResolved = false;
            EnsureEventState();
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (Find.TickManager.TicksGame % CheckIntervalTicks == 0)
            {
                EnsureEventState();
            }
        }

        private void EnsureEventState()
        {
            if (map?.weatherManager?.eventHandler == null)
            {
                return;
            }
            List<WeatherEvent> live = map.weatherManager.eventHandler.LiveEventsListForReading;
            bool present = liveEvent != null && live.Contains(liveEvent);
            if (IsActive)
            {
                if (!present)
                {
                    liveEvent = new RM_WeatherEvent_PinnedSun(map, this);
                    // Insert FIRST, not appended: GetOverridenShadowVector takes the
                    // first live event with an override, so a lightning flash
                    // (which also overrides the vector for its few ticks) never
                    // swings the pinned shadows. Flashes still brighten the sky,
                    // because SkyTarget lerps run in list order and theirs come after.
                    live.Insert(0, liveEvent);
                    liveEvent.FireEvent();
                }
            }
            else if (present)
            {
                live.Remove(liveEvent);
                liveEvent = null;
            }
        }

        private void ResolveGeometry()
        {
            if (geometryResolved)
            {
                return;
            }
            geometryResolved = true;
            RM_PinnedSunExtension ext = Extension;
            if (ext == null || Find.WorldGrid == null || !map.Tile.Valid)
            {
                return;
            }
            Vector2 longLat = Find.WorldGrid.LongLatOf(map.Tile);
            SunGeometry(longLat.y, longLat.x, ext.substellarLatitude, ext.substellarLongitude,
                out float bearingDeg, out float arcDeg);
            elevationDegrees = Mathf.Clamp(90f - arcDeg, ext.minElevationDegrees, ext.maxElevationDegrees);
            float b = bearingDeg * Mathf.Deg2Rad;
            // Bearing is clockwise from north toward the sun; map x = east, z = north.
            // Shadows fall directly away from the sun.
            shadowDirection = new Vector2(-Mathf.Sin(b), -Mathf.Cos(b));
        }

        /// <summary>Great-circle initial bearing (degrees clockwise from north)
        /// from (lat, lon) toward the substellar point, and the arc between
        /// them (degrees). Same spherical-law-of-cosines arc as the
        /// WeatherSuite's ArcFromSubstellar. Public and static so a selftest or
        /// another consumer can reuse it without a map.</summary>
        public static void SunGeometry(float latDeg, float lonDeg, float subLatDeg, float subLonDeg,
            out float bearingDeg, out float arcDeg)
        {
            float lat1 = latDeg * Mathf.Deg2Rad;
            float lat2 = subLatDeg * Mathf.Deg2Rad;
            float dLon = (subLonDeg - lonDeg) * Mathf.Deg2Rad;
            float cosArc = Mathf.Sin(lat1) * Mathf.Sin(lat2) + Mathf.Cos(lat1) * Mathf.Cos(lat2) * Mathf.Cos(dLon);
            arcDeg = Mathf.Acos(Mathf.Clamp(cosArc, -1f, 1f)) * Mathf.Rad2Deg;
            float y = Mathf.Sin(dLon) * Mathf.Cos(lat2);
            float x = Mathf.Cos(lat1) * Mathf.Sin(lat2) - Mathf.Sin(lat1) * Mathf.Cos(lat2) * Mathf.Cos(dLon);
            bearingDeg = Mathf.Atan2(y, x) * Mathf.Rad2Deg;
        }
    }

    /// <summary>
    /// The never-expiring weather event that carries the pinned sky and
    /// shadow vector. Owned and re-created by RM_MapComponent_PinnedSun;
    /// never saved (WeatherEventHandler is not scribed).
    /// </summary>
    public class RM_WeatherEvent_PinnedSun : WeatherEvent
    {
        private readonly RM_MapComponent_PinnedSun owner;

        private readonly List<GameCondition> tmpConditions = new List<GameCondition>();

        public RM_WeatherEvent_PinnedSun(Map map, RM_MapComponent_PinnedSun owner) : base(map)
        {
            this.owner = owner;
        }

        // Expires the moment the pin is switched off (setting, biome, removal);
        // the handler then drops it and the component will not re-add it.
        public override bool Expired => owner == null || !owner.IsActive;

        public override SkyTarget SkyTarget
        {
            get
            {
                RM_PinnedSunExtension ext = owner?.Extension;
                if (ext == null)
                {
                    return map.skyManager.CurSky;
                }
                return new SkyTarget(
                    ext.glow,
                    new SkyColorSet(ext.skyColor, ext.shadowColor, ext.overlayColor, ext.saturation),
                    ext.lightsourceShineSize,
                    ext.lightsourceShineIntensity);
            }
        }

        /// <summary>
        /// ext.lerpFactor × the Mod Settings strength, yielding to any active
        /// GameCondition that paints its own sky (eclipse, aurora, toxic
        /// fallout, unnatural darkness, and later the smoke calendar's haze):
        /// the pinned sky gives way by exactly that condition's own lerp
        /// factor, so those events still read on a golden-hour map instead of
        /// being painted over.
        /// </summary>
        public override float SkyTargetLerpFactor
        {
            get
            {
                RM_PinnedSunExtension ext = owner?.Extension;
                if (ext == null || !owner.IsActive)
                {
                    return 0f;
                }
                float factor = Mathf.Clamp01(ext.lerpFactor * RM_CreatureBehaviorsSettings.pinnedSunSkyStrength);
                if (factor <= 0f)
                {
                    return 0f;
                }
                float yieldTo = 0f;
                map.gameConditionManager.GetAllGameConditionsAffectingMap(map, tmpConditions);
                for (int i = 0; i < tmpConditions.Count; i++)
                {
                    if (tmpConditions[i].SkyTarget(map).HasValue)
                    {
                        yieldTo = Mathf.Max(yieldTo, tmpConditions[i].SkyTargetLerpFactor(map));
                    }
                }
                tmpConditions.Clear();
                return factor * (1f - Mathf.Clamp01(yieldTo));
            }
        }

        public override Vector2? OverrideShadowVector
        {
            get
            {
                if (owner == null || !owner.IsActive || map.gameConditionManager.IsAlwaysDarkOutside)
                {
                    return null;
                }
                return owner.RenderedShadowVector;
            }
        }

        public override void FireEvent()
        {
        }

        public override void WeatherEventTick()
        {
        }
    }
}
