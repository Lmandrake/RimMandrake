using System;
using System.Collections.Generic;
using System.Linq;
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
            return RM_WeatherKernel.ArcDegrees(longLat.y, longLat.x, geo.substellarLat, geo.substellarLon);
        }

        public static bool TileInTerminatorBand(PlanetTile tile)
        {
            PlanetGeometryDef geo = ActiveGeometry;
            if (geo == null) return false;
            float arc = ArcFromSubstellar(tile);
            return RM_WeatherKernel.InTerminatorBand(arc, geo.terminatorBandMinArc, geo.terminatorBandMaxArc);
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
            return RM_WeatherKernel.InNightsideBand(arc, geo.nightsideBandMinArc);
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
                        + "IncidentWorker_NightsideAurora). Harmony: two postfixes for the perpetual "
                        + "aurora's light (AuroraLight.cs), applied by WeatherSuiteOptionsMod.");
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
                // MOD_OPTIONS_RETROFIT_1: worldgen-affecting master switch —
                // only ever checked here, at map init.
                if (!WeatherSuiteSettings.terminatorFrontEnabled) return;
                if (!WeatherGeometryUtility.MapInTerminatorBand(map)) return;

                GameConditionDef frontDef = DefDatabase<GameConditionDef>.GetNamedSilentFail("RM_WS_TerminatorFront");
                if (frontDef == null)
                {
                    Log.Error("[RimMandrake.StarWars.WeatherSuite] RM_WS_TerminatorFront GameConditionDef "
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
        private const float AuroraGlowFloor = 0.25f;        // vanilla's private `Glow` const — NOT MaxSunGlow

        public override SkyTarget? SkyTarget(Map map)
        {
            // MOD_OPTIONS_RETROFIT_1: off falls back to vanilla's own aurora
            // look entirely.
            if (!WeatherSuiteSettings.auroraMaxBrightnessEnabled) return base.SkyTarget(map);

            if (map.GameConditionManager.IsAlwaysDarkOutside) return null;

            Color currentColor = CurrentColor;
            Color sky = Tint(currentColor, WeatherSuiteSettings.auroraSkySaturation, WeatherSuiteSettings.auroraSkyBrightness, RM_WeatherKernel.VanillaSkySaturation);
            Color overlay = Tint(currentColor, WeatherSuiteSettings.auroraOverlaySaturation, WeatherSuiteSettings.auroraSkyBrightness, RM_WeatherKernel.VanillaOverlaySaturation);
            float glow = Mathf.Max(GenCelestial.CurCelestialSunGlow(map), GlowFloor);
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

        // AURORAL_UMBRA (owner 2026-10-19: "perpetual Auroral activity in that biome"): a PERMANENT instance of this condition is the
        // perpetual aurora MapComponent_PerpetualAurora starts on maps whose biome carries PerpetualAuroraExtension. The glow below only
        // matters for the incident: SkyManager folds conditions in with LerpDarken, so a condition's glow can never raise light. The
        // permanent aurora's LIGHT and moving curtains are AuroraLight.cs (AURORA_LIGHT, 2026-10-20).
        protected float GlowFloor => AuroraGlowFloor;

        // Vanilla slows a permanent aurora's colour drift to 3750 ticks per colour (TransitionDurationTicks_Permanent);
        // the owner asked for a "wildly active" one, so the base tick (colour drift only - a permanent condition has
        // no TicksLeft to shorten) runs perpetualAuroraActivity times per tick. 1 = vanilla's slow drift.
        public override void GameConditionTick()
        {
            int n = Permanent ? Mathf.Clamp(WeatherSuiteSettings.perpetualAuroraActivity, 1, 30) : 1;
            for (int i = 0; i < n; i++) base.GameConditionTick();
            if (!Permanent || !WeatherSuiteSettings.perpetualAuroraEnabled) return;
            List<Map> maps = AffectedMaps;
            for (int i = 0; i < maps.Count; i++)
            {
                AuroraLightRegistry.Refresh(this, maps[i]);
            }
            AuroraLightRegistry.Entry e = maps.Count > 0 ? AuroraLightRegistry.Find(maps[0]) : null;
            if (e != null) AuroraCurtains.Tick(e);
        }

        public override void GameConditionDraw(Map map)
        {
            base.GameConditionDraw(map);
            if (!Permanent || HiddenByOtherCondition(map)) return;
            AuroraLightRegistry.Entry e = AuroraLightRegistry.Live(map);
            if (e != null) AuroraCurtains.Draw(map, e);
        }

        public override void End()
        {
            List<Map> maps = AffectedMaps;
            for (int i = 0; i < maps.Count; i++) AuroraLightRegistry.Remove(maps[i]);
            base.End();
        }

        private static Color Tint(Color c, float saturation, float brightness, float vanillaSaturation)
        {
            return new Color(RM_WeatherKernel.TintChannel(c.r, saturation, brightness, vanillaSaturation), RM_WeatherKernel.TintChannel(c.g, saturation, brightness, vanillaSaturation),
                RM_WeatherKernel.TintChannel(c.b, saturation, brightness, vanillaSaturation), c.a);
        }
    }

    // AURORAL_UMBRA: marks a biome whose sky is never without the aurora. Generic: any biome may carry it.
    public class PerpetualAuroraExtension : DefModExtension
    {
        public string conditionDef = "RM_WS_DarkAurora";
    }

    // Keeps a PERMANENT aurora condition on every map whose biome carries PerpetualAuroraExtension, and ends it
    // when the setting is switched off. Checked at map init and every 2500 ticks (no per-tick work beyond a modulo).
    public class MapComponent_PerpetualAurora : MapComponent
    {
        public MapComponent_PerpetualAurora(Map map) : base(map) { }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            Sync();
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % 2500 == 37) Sync();
        }

        private void Sync()
        {
            try
            {
                PerpetualAuroraExtension ext = map.Biome?.GetModExtension<PerpetualAuroraExtension>();
                if (ext == null) return;
                GameConditionDef def = DefDatabase<GameConditionDef>.GetNamedSilentFail(ext.conditionDef);
                if (def == null)
                {
                    Log.ErrorOnce("[RimMandrake.StarWars.WeatherSuite] perpetual aurora: GameConditionDef '" + ext.conditionDef
                                  + "' missing on biome " + map.Biome.defName, 0x57A02);
                    return;
                }
                GameCondition permanent = map.gameConditionManager.ActiveConditions.FirstOrDefault(c => c.def == def && c.Permanent);
                if (WeatherSuiteSettings.perpetualAuroraEnabled)
                {
                    if (permanent == null)
                        map.gameConditionManager.RegisterCondition(GameConditionMaker.MakeConditionPermanent(def));
                }
                else if (permanent != null)
                {
                    permanent.End();
                    AuroraLightRegistry.Remove(map);
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.StarWars.WeatherSuite] MapComponent_PerpetualAurora: " + e.Message, 0x57A03);
            }
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
            if (!WeatherSuiteSettings.nightsideAuroraEnabled) return false;
            if (!base.CanFireNowSub(parms)) return false;
            foreach (Map m in Find.Maps)
            {
                if (m.IsPlayerHome && WeatherGeometryUtility.MapInNightsideBand(m))
                    return true;
            }
            return false;
        }
    }
}
