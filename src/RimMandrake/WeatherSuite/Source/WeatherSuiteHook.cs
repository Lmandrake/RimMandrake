using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.WeatherSuite
{
    // WEATHER_SUITE_SLICE_1, v1 — the ONE light C# hook this item budgets:
    // a fixed-geometry arc-from-substellar-point test (doc §1's own words:
    // "a small, one-time WorldComponent query, not a per-tick simulation"),
    // reused for two purposes:
    //   1. MapComponent_TerminatorBand — on map init, starts a PERMANENT
    //      GameCondition on any map whose tile sits in the terminator band,
    //      and sends a "you crossed the front" letter once per MAP (not
    //      once per game — corrected 2026-09-02, opus code review: the
    //      flag is MapComponent state, so a caravan camp, quest site or
    //      enemy settlement inside the band gets its own letter the first
    //      time it's entered. Left as-is: a fresh warning for each new
    //      place in a hazardous permanent-storm region reads as intended,
    //      not spam — reconsider only if the owner disagrees on sight).
    //   2. IncidentWorker_NightsideAurora — gates vanilla's own Aurora
    //      incident (reused via a new GameConditionDef pointing at the SAME
    //      GameCondition_Aurora class) to nightside-band maps only.
    // Everything else — the storm wall's lightning, the aurora's mood buff
    // and sky brightening — rides vanilla GameCondition_Flashstorm /
    // GameCondition_Aurora / ThoughtWorker_Aurora UNCHANGED, exactly the way
    // FIRE_ECOLOGY_LOOP_1's Black Rain rides vanilla's own rain-on-fire
    // mechanism. No per-tick C# is added anywhere in this assembly.
    //
    // The substellar point and the band thresholds are NOT hardcoded here —
    // they come from a single PlanetGeometryDef instance the RimUtinni-tier
    // wiring mod ships with Ash'karr's real, already-authored numbers (see
    // that mod's WeatherGeometryDefs_Ashkarr.xml for the citations). This
    // assembly only knows the MECHANISM: "read whichever PlanetGeometryDef
    // is loaded, do the great-circle arc test." A second Star Wars planet
    // would ship its own PlanetGeometryDef and get the same mechanism free.
    public class PlanetGeometryDef : Def
    {
        // Substellar point, degrees. Ash'karr's is (0, 0) — see
        // ASHKARR_WORLD_DEFINITION.md §2b and the_one_map.md's own
        // reconciliation ("Substellar point = latitude 0.0, longitude 0.0").
        public float substellarLat;
        public float substellarLon;

        // Terminator storm-wall band, degrees of arc from the substellar
        // point. A map whose tile's arc falls in [terminatorBandMinArc,
        // terminatorBandMaxArc] gets the permanent TerminatorFront
        // GameCondition.
        public float terminatorBandMinArc = 63f;
        public float terminatorBandMaxArc = 117f;

        // Deep-night band: arc >= this value is eligible for dark-side
        // auroras. Deliberately set at the terminator band's OWN outer
        // edge (see terminatorBandMaxArc) so a map never carries both the
        // storm wall and the aurora at once — the front guards the seam,
        // the aurora owns the dark past it.
        public float nightsideBandMinArc = 117f;
    }

    public static class WeatherGeometryUtility
    {
        private static PlanetGeometryDef cachedGeometry;
        private static bool warnedMissing;

        public static PlanetGeometryDef ActiveGeometry
        {
            get
            {
                if (cachedGeometry == null)
                {
                    cachedGeometry = DefDatabase<PlanetGeometryDef>.AllDefsListForReading.FirstOrDefault();
                    if (cachedGeometry == null && !warnedMissing)
                    {
                        warnedMissing = true;
                        Log.Warning("[RimMandrake.StarWars.WeatherSuite] no PlanetGeometryDef loaded — "
                                    + "terminator-band and nightside-band checks will always return false. "
                                    + "The RimUtinni wiring mod ships the one Ash'karr needs.");
                    }
                }
                return cachedGeometry;
            }
        }

        // Great-circle arc distance, in degrees, from the geometry def's
        // substellar point to this tile — same formula the world-paint
        // recipe used to fill world/ASHKARR_WORLDMAP_tiles.csv's own `arc`
        // column (verified against that CSV's row 0 before shipping: a
        // tile at lat 58.2787, lon -90 from substellar (0,0) reads arc 90.0
        // by both this formula and the CSV).
        public static float ArcFromSubstellar(PlanetTile tile)
        {
            PlanetGeometryDef geo = ActiveGeometry;
            if (geo == null) return -1f;
            if (Find.WorldGrid == null) return -1f;
            // Fixed 2026-09-02 (opus code review): vanilla WorldGrid.LongLatOf
            // silently substitutes the player's home tile for an invalid one
            // (pocket maps - Anomaly's undercave and similar - carry an invalid
            // PlanetTile). Left unguarded, every pocket map would inherit the
            // HOME colony's band membership, including a permanent
            // GameCondition_Flashstorm bypassing this def's own allowUnderground
            // gate, with no exception to catch.
            if (!tile.Valid) return -1f;

            Vector2 longLat = Find.WorldGrid.LongLatOf(tile);
            float lat = longLat.y * Mathf.Deg2Rad;
            float lon = longLat.x * Mathf.Deg2Rad;
            float lat0 = geo.substellarLat * Mathf.Deg2Rad;
            float lon0 = geo.substellarLon * Mathf.Deg2Rad;

            float cosArc = Mathf.Sin(lat0) * Mathf.Sin(lat)
                           + Mathf.Cos(lat0) * Mathf.Cos(lat) * Mathf.Cos(lon - lon0);
            cosArc = Mathf.Clamp(cosArc, -1f, 1f);
            return Mathf.Acos(cosArc) * Mathf.Rad2Deg;
        }

        public static bool TileInTerminatorBand(PlanetTile tile)
        {
            PlanetGeometryDef geo = ActiveGeometry;
            if (geo == null) return false;
            float arc = ArcFromSubstellar(tile);
            return arc >= geo.terminatorBandMinArc && arc <= geo.terminatorBandMaxArc;
        }

        public static bool TileInNightsideBand(PlanetTile tile)
        {
            PlanetGeometryDef geo = ActiveGeometry;
            if (geo == null) return false;
            float arc = ArcFromSubstellar(tile);
            // Fixed 2026-09-02 (opus code review): TileInTerminatorBand uses
            // `<= terminatorBandMaxArc`, and on Ash'karr's geometry def
            // terminatorBandMaxArc == nightsideBandMinArc (117). A tile at
            // exactly that arc satisfied both bands, breaking the "never both
            // at once" invariant this header claims. Exclusive here so the two
            // bands share a single dividing line instead of overlapping on it.
            return arc > geo.nightsideBandMinArc;
        }

        public static bool MapInTerminatorBand(Map map)
        {
            if (map == null) return false;
            return TileInTerminatorBand(map.Tile);
        }

        public static bool MapInNightsideBand(Map map)
        {
            if (map == null) return false;
            return TileInNightsideBand(map.Tile);
        }
    }

    [StaticConstructorOnStartup]
    public static class WeatherSuiteHookMod
    {
        static WeatherSuiteHookMod()
        {
            Log.Message("[RimMandrake.StarWars.WeatherSuite] loaded — terminator-band and "
                        + "nightside-band geometry checks armed (MapComponent_TerminatorBand, "
                        + "IncidentWorker_NightsideAurora). No Harmony patches: both hooks are "
                        + "ordinary MapComponent/IncidentWorker overrides.");
        }
    }

    public class MapComponent_TerminatorBand : MapComponent
    {
        private bool crossingLetterSent;

        public MapComponent_TerminatorBand(Map map) : base(map) { }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref crossingLetterSent, "crossingLetterSent", false);
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            try
            {
                if (!WeatherGeometryUtility.MapInTerminatorBand(map)) return;

                GameConditionDef frontDef = DefDatabase<GameConditionDef>.GetNamedSilentFail("RSW_WS_TerminatorFront");
                if (frontDef == null)
                {
                    Log.Error("[RimMandrake.StarWars.WeatherSuite] RSW_WS_TerminatorFront GameConditionDef "
                              + "missing — the terminator band is geometrically active on this map but has "
                              + "nothing to start.");
                    return;
                }

                if (map.gameConditionManager.GetActiveCondition(frontDef) == null)
                {
                    GameCondition cond = GameConditionMaker.MakeConditionPermanent(frontDef);
                    map.gameConditionManager.RegisterCondition(cond);
                }

                if (!crossingLetterSent)
                {
                    crossingLetterSent = true;
                    Find.LetterStack.ReceiveLetter(
                        "Entering the Terminator Front",
                        "This ground sits inside the standing front where the dayside furnace meets "
                            + "the nightside cold. The weather here never settles — expect a permanent "
                            + "storm wall and lightning well above ambient, day after day, forever.",
                        LetterDefOf.NeutralEvent,
                        new LookTargets(map.Parent));
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.StarWars.WeatherSuite] MapComponent_TerminatorBand.FinalizeInit: "
                                 + e.Message, 0x57A01);
            }
        }
    }

    // Owner's ruling (design doc's RULED table, saved 2026-09-02 — AFTER
    // this file's original v1 build on 2026-09-01): "use the Aurora graphic
    // effect but maximized in brightness and color. It should be awesome!"
    // Vanilla GameCondition_Aurora's palette/strength/brightness are
    // hardcoded PRIVATE consts (Colors[], SkyColorStrength = 0.075f,
    // OverlayColorStrength = 0.025f, BaseBrightness = 0.73f — RimSage,
    // GameCondition_Aurora.cs) with no XML hook to raise them, so honoring
    // the ruling needs this one small subclass rather than a def tweak.
    // Reuses everything else from the base class unchanged (color cycling,
    // ExposeData, mood/sight-range plumbing via SkyTarget's glow).
    //
    // 🔴 FIXED AGAIN 2026-09-02 (opus code review, verified against
    // GameCondition_Aurora's real SkyTarget()): the previous attempt at
    // this fix used `Color.Lerp(Color.white, currentColor, 1f)` — full
    // saturation with NO brightness multiplier at all. Every one of
    // vanilla's 8 aurora colours has at least one channel at exactly 0
    // (Colors[], GameCondition_Aurora.cs), so lerping all the way to pure
    // saturation zeroes that channel outright — e.g. (0,0,1) instead of
    // vanilla's near-white ~(0.68,0.68,0.73) tint. That is OBJECTIVELY
    // DARKER than vanilla in two of three channels, the opposite of
    // "maximized", and the SECOND time this exact regression shape (fix
    // one axis, break brightness on another) has landed here.
    //
    // 🔴 FIXED AGAIN 2026-09-02 (opus code review, second pass): the
    // previous attempt shared ONE heavy lerp (0.5) between sky AND
    // overlay, and floored "brightness" at `Mathf.Max(1f, sunGlow)` —
    // which is always exactly 1f (sunGlow never exceeds 1), so it was
    // really just `Lerp(white, C, 0.5)` with no multiplier at all. For
    // the low-green colours (index 5/6/7 in vanilla's Colors[] — (0,0,1),
    // (0.87,0,1), (0.75,0,1)) that is DARKER in the R/G channels than
    // vanilla's `Lerp(white, C, 0.075) * 0.73`, backwards from "maximized".
    // Reusing that same heavy lerp for the OVERLAY colour (vanilla lerps
    // overlay only 0.025 — near-white) also darkened rendered terrain
    // under a blue/violet aurora.
    //
    // Vanilla's own SkyTarget is `Lerp(white, color, 0.075) *
    // Brightness(map)` for the sky and `Lerp(white, color, 0.025) *
    // Brightness(map)` for the overlay, where private Brightness() is
    // `Max(0.73, CurCelestialSunGlow(map))`. This fix keeps the sky and
    // overlay as two SEPARATE lerps (sky noticeably more saturated than
    // vanilla, since "maximized colour" is the actual ask; overlay close
    // to vanilla's own near-white amount so terrain doesn't darken), and
    // replaces the always-1f brightness with a FIXED multiplier above
    // vanilla's 0.73-to-1.0 range so the sky is genuinely brighter, not
    // merely un-dimmed — clamped per-channel so it can't blow out past
    // pure white. `glow:` floors at 0.25 (vanilla's own private `Glow`
    // const), not at `MaxSunGlow` (0.5) — see AuroraGlowFloor below.
    public class GameCondition_DarkAuroraMax : GameCondition_Aurora
    {
        private const float SkySaturationLerp = 0.35f;     // vanilla sky: 0.075f
        private const float OverlaySaturationLerp = 0.05f; // vanilla overlay: 0.025f
        private const float SkyBrightness = 1.15f;         // fixed; vanilla's Brightness() ranges 0.73-1.0
        private const float AuroraGlowFloor = 0.25f;        // vanilla's private `Glow` const — NOT MaxSunGlow

        public override SkyTarget? SkyTarget(Map map)
        {
            if (map.GameConditionManager.IsAlwaysDarkOutside) return null;

            Color currentColor = CurrentColor;
            Color sky = ClampToOne(Color.Lerp(Color.white, currentColor, SkySaturationLerp) * SkyBrightness);
            Color overlay = ClampToOne(Color.Lerp(Color.white, currentColor, OverlaySaturationLerp) * SkyBrightness);
            float glow = Mathf.Max(GenCelestial.CurCelestialSunGlow(map), AuroraGlowFloor);
            return new SkyTarget(
                colorSet: new SkyColorSet(
                    sky,
                    new Color(0.92f, 0.92f, 0.92f),
                    overlay,
                    1f),
                glow: glow,
                lightsourceShineSize: 1f,
                lightsourceShineIntensity: 1f);
        }

        private static Color ClampToOne(Color c)
        {
            return new Color(Mathf.Min(c.r, 1f), Mathf.Min(c.g, 1f), Mathf.Min(c.b, 1f), c.a);
        }
    }

    // Reuses vanilla IncidentWorker_Aurora wholesale (same darkness/timing
    // gating, same "will it end soon" check) and adds exactly one more
    // requirement: at least one player-home map sits in the geometry def's
    // nightside band. No duplicated aurora logic.
    public class IncidentWorker_NightsideAurora : IncidentWorker_Aurora
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms)) return false;
            foreach (Map m in Find.Maps)
            {
                if (m.IsPlayerHome && WeatherGeometryUtility.MapInNightsideBand(m))
                    return true;
            }
            return false;
        }
    }

    public class CompProperties_Forecaster : CompProperties
    {
        public CompProperties_Forecaster()
        {
            compClass = typeof(CompForecaster);
        }
    }

    // Tier 0-1 forecast instrument. CompInspectStringExtra() is called on
    // hover/selection, not per-tick, and ComputeCommonality() never touches
    // Rand — it replicates WeatherDecider.CurrentWeatherCommonality's public
    // surface read-only, so it can never desync the real weather roll it is
    // reporting on. It is deliberately imprecise where the private
    // ticksWhenRainAllowedAgain gate would matter (that field is not
    // reachable from outside WeatherDecider) — exactly the Tier-1 "crude,
    // imprecise" register the design doc asks for, not a Tier-4 guarantee.
    public class CompForecaster : ThingComp
    {
        public override string CompInspectStringExtra()
        {
            if (!parent.Spawned) return null;
            Map map = parent.Map;
            if (map?.weatherManager == null || map.Biome?.baseWeatherCommonalities == null) return null;

            WeatherDef forced = ForcedWeatherOn(map);
            if (forced != null)
            {
                return "Instrument reading: front-forced weather incoming — " + forced.label + ".";
            }

            List<(WeatherDef weather, float weight)> weighted = new List<(WeatherDef, float)>();
            foreach (WeatherDef w in DefDatabase<WeatherDef>.AllDefsListForReading)
            {
                float c = ComputeCommonality(w, map);
                if (c > 0f) weighted.Add((w, c));
            }
            if (weighted.Count == 0) return "Instrument reading: no clear signal.";

            weighted.Sort((a, b) => b.weight.CompareTo(a.weight));
            float total = weighted.Sum(x => x.weight);

            StringBuilder sb = new StringBuilder("Instrument reading — likely next: ");
            int shown = Math.Min(2, weighted.Count);
            for (int i = 0; i < shown; i++)
            {
                if (i > 0) sb.Append(", then ");
                float pct = total > 0f ? weighted[i].weight / total * 100f : 0f;
                sb.Append(weighted[i].weather.label).Append(" (~").Append(pct.ToString("F0")).Append("%)");
            }
            return sb.ToString();
        }

        private static WeatherDef ForcedWeatherOn(Map map)
        {
            WeatherDef result = null;
            foreach (GameCondition cond in map.gameConditionManager.ActiveConditions)
            {
                WeatherDef fw = cond.ForcedWeather();
                if (fw != null) result = fw;
            }
            return result;
        }

        // Deliberate near-copy of WeatherDecider.CurrentWeatherCommonality
        // (RimSage, WeatherDecider.cs) using only its PUBLIC surface — see
        // this class's own header for the one gate it cannot see.
        private static float ComputeCommonality(WeatherDef weather, Map map)
        {
            if (map.weatherManager.curWeather != null && !weather.repeatable
                && weather == map.weatherManager.curWeather)
                return 0f;
            if (!weather.temperatureRange.Includes(map.mapTemperature.OutdoorTemp))
                return 0f;
            if ((int)weather.favorability < 2 && GenDate.DaysPassedSinceSettle < 8)
                return 0f;
            if (weather.rainRate > 0.1f
                && map.gameConditionManager.ActiveConditions.Any(x => x.def.preventRain))
                return 0f;
            if (ModsConfig.AnomalyActive && weather.minMonolithLevel > Find.Anomaly.HighestLevelReached
                && (!weather.canOccurInAmbientHorror || !Find.Anomaly.AmbientHorrorMode))
                return 0f;

            BiomeDef biome = map.Biome;
            float commonality = 0f;
            for (int i = 0; i < biome.baseWeatherCommonalities.Count; i++)
            {
                WeatherCommonalityRecord rec = biome.baseWeatherCommonalities[i];
                if (rec.weather != weather) continue;
                float c = rec.commonality;
                if (map.fireWatcher.LargeFireDangerPresent && weather.rainRate > 0.1f) c *= 15f;
                if (rec.weather.commonalityRainfallFactor != null)
                    c *= rec.weather.commonalityRainfallFactor.Evaluate(map.TileInfo.rainfall);
                foreach (GameCondition cond in map.gameConditionManager.ActiveConditions)
                    c *= cond.WeatherCommonalityFactor(weather, map);
                commonality = c;
                break;
            }
            PlanetTile tile = map.Tile;
            for (int i = 0; i < map.TileInfo.Mutators.Count; i++)
                map.TileInfo.Mutators[i].Worker?.MutateWeatherCommonalityFor(weather, tile, ref commonality);
            return commonality;
        }
    }
}
