using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_FLOOR_LIGHT_1 — the drowned aurora (layer 1 of the seabed's
    // layered light; layer 2, the bioluminescent point-glow constants, is
    // ordinary CompGlower on RM_Fuselight/RM_Ghostpane, no C# needed).
    //
    // Owner, typed verbatim (2026-09-27 card ruling): "Liquid propane is
    // water-clear; the black mirror is only black from above. From the
    // floor, the brightest sky on the planet arrives as dim shifting
    // curtains — a map-light level that rises and falls with aurora
    // weather on the surface above. The floor breathes light." And on the
    // palette: "the bottom is violet-teal dusk lit by a sky that ripples."
    //
    // SCOPE: RM_ChillFireGate.IsChillSeabedMap(map) only, same identity
    // check every sibling Chill mechanism this session uses.
    //
    // ── WHAT "SURFACE AURORA STATE" ACTUALLY IS (MEASURED, not assumed) ──
    // Two GameConditionDefs can put an aurora over a SURFACE map in this
    // campaign: vanilla's own `Aurora` (GameConditionDefOf.Aurora,
    // conditionClass GameCondition_Aurora) and this campaign's own
    // `RM_WS_DarkAurora` (WeatherSuite,
    // GameConditionDefs_DarkAurora.xml — nightside-band-gated, conditionClass
    // GameCondition_DarkAuroraMax, a subclass of GameCondition_Aurora that
    // only maximizes SkyTarget's brightness/saturation). RM_TheChill's own
    // world-tile placement is not assumed here — whichever of the two
    // actually fires there, both share the SAME base class and the SAME
    // public hook: GameCondition.SkyTargetLerpFactor(Map), a real 0..1 ramp
    // (GameConditionUtility.LerpInOutValue under TransitionTicks, the exact
    // value vanilla's own SkyManager blends sky/overlay/glow by) that rises
    // when the condition starts and falls as it ends — "does it have an
    // intensity/strength value that varies over time?" Yes, and it is
    // already public; no private field, no reflection, needed to read it.
    //
    // ── WHY THIS COMPONENT, NOT A GAMECONDITION ON THE SEABED ITSELF ──
    // GameCondition.CanApplyOnMap (RimSage, GameCondition.cs) refuses ANY
    // condition on this map outright unless its def sets
    // allowUnderground="true" — RM_SeaDiveGenerator_TheChill's own
    // MapGeneratorDef carries isUnderground="true" (RM_SeaDiveGenerators.xml),
    // and GameConditionManager.GetAllGameConditionsAffectingMap filters
    // through that same check before SkyManager ever sees a condition's
    // SkyTarget(). Registering our own condition on the seabed map itself
    // would work (we control the def, we'd just set allowUnderground=true),
    // but SkyTarget.LerpDarken (SkyTarget.cs) — the ONLY way a GameCondition's
    // contribution blends into SkyManager.CurrentSkyTarget() — can only ever
    // take the per-channel MIN of the base sky and the condition's own
    // target: `glow = Lerp(A.glow, Min(A.glow, B.glow), t)`. It can DARKEN,
    // never BRIGHTEN, the map's baseline. That is backwards for "the floor
    // breathes light" when aurora is active, and it makes the ceiling of our
    // effect hostage to whatever vanilla's own weather-worker computes for
    // an underground pocket map's baseline sky glow (unmeasured, and
    // plausibly non-zero from an ordinary day/night curve that makes no
    // fictional sense on a sunless seabed).
    //
    // Instead this MapComponent computes the intensity, and
    // Patch_ChillDrownedAurora.cs (a Harmony POSTFIX on
    // SkyManager.SkyManagerUpdate — this assembly's third patch, same
    // pattern as Patch_ChillFireBan.cs/Patch_ChillGardenDefense.cs) applies
    // it directly to the Chill seabed map's own SkyManager AFTER vanilla's
    // own computation runs each frame, via Mathf.Max (raises the floor,
    // never darkens below whatever vanilla itself already produced). See
    // that file's header for the full reflection/ordering argument for why
    // this is safe and why the one-frame staleness on the rendered tint is
    // imperceptible.
    //
    // ── THE PUBLIC HOOK CHILL_AURORA_SURGE_1 OWNS ──
    // CurrentAuroraIntensity (0..1) is the "surface aurora, right now, as a
    // strength value" read CHILL_AURORA_SURGE_1's own item text asks
    // CHILL_FLOOR_LIGHT_1 to expose. It is smoothed (MoveTowards, not a
    // snap) so "rises and falls" reads as breathing, not a light switch.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_ChillDrownedAurora : MapComponent
    {
        private const string DarkAuroraDefName = "RM_WS_DarkAurora";

        // Cheap to poll; not a rescan of anything expensive (two
        // GameConditionManager.GetActiveCondition lookups on the SOURCE
        // map), but there is no reason to do it every single tick either —
        // the ramp below is already slow enough that sub-second precision
        // buys nothing visible.
        private const int RescanIntervalTicks = 30;

        // How far currentIntensity moves toward its target per rescan.
        // 0.04 * (60000/RescanIntervalTicks... ) — in practice a full 0->1
        // ramp takes ~25 rescans = 750 ticks = 12.5 real seconds at 1x:
        // slow enough to read as "breathing," fast enough that a player
        // watching an aurora start on the surface (if they could) would
        // see the floor visibly respond within the same scene.
        private const float RampStepPerRescan = 0.04f;

        // Layer 1's own floor and ceiling. MinFloorGlow is deliberately
        // near-zero — "never absolutely black" is layer 2's job
        // (Fuselight/Ghostpane CompGlower, ordinary point light, unaffected
        // by any of this). MaxAuroraGlow matches the ORDER OF MAGNITUDE of
        // vanilla's own aurora-related constants (GameCondition_Aurora.
        // MaxSunGlow = 0.5f) — "dim shifting curtains," not full daylight;
        // GlowGrid's own PsychGlowAtGlow bands read this as "Lit," never
        // "Overlit" (>0.9f).
        private const float MinFloorGlow = 0.02f;
        private const float MaxAuroraGlow = 0.5f;

        // "A sky that ripples" — a slow violet<->teal cycle, independent of
        // aurora intensity (it ripples even while quiet, at floor
        // brightness; intensity controls how STRONG the tint reads, not
        // whether it moves). One full cycle every 2400 ticks = 40 real
        // seconds at 1x: slow, alien, never a strobe.
        private const float RippleFullCycleTicks = 2400f;

        private static readonly Color TealColor = new Color(0.16f, 0.55f, 0.56f);
        private static readonly Color VioletColor = new Color(0.46f, 0.20f, 0.62f);

        // Vanilla GameCondition_DarkAuroraMax's own shadow colour (near-
        // white) — shadows read almost untinted while the sky/overlay
        // carry the palette, same balance vanilla's own aurora uses.
        private static readonly Color ShadowTint = new Color(0.92f, 0.92f, 0.92f);

        private static GameConditionDef darkAuroraDefCache;
        private static bool darkAuroraLookupDone;

        private bool isChillSeabed;
        private int ticksUntilRescan = 1;

        // Scribed: RM_MapComponent_ChillAuroraSurge saves surgeActive and reads
        // this value; reloading it as 0 ended a saved surge on the first rescan
        // and then re-announced it as the ramp climbed back.
        private float currentIntensity;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref currentIntensity, "currentIntensity", 0f);
        }

        public RM_MapComponent_ChillDrownedAurora(Map map) : base(map)
        {
        }

        private static GameConditionDef DarkAuroraDef
        {
            get
            {
                if (!darkAuroraLookupDone)
                {
                    darkAuroraLookupDone = true;
                    darkAuroraDefCache = DefDatabase<GameConditionDef>.GetNamedSilentFail(DarkAuroraDefName);
                }
                return darkAuroraDefCache;
            }
        }

        // DIVING_SETTINGS_CONTRACT_1: sensing is separate from presentation. The intensity is SENSED
        // whenever either consumer is on (the floor light or the surge storms); chillDrownedAuroraEnabled
        // turns off only the light, never the surges or the collector that ride the same reading.
        private static bool SensingWanted => RM_DivingSettings.masterEnabled
            && (RM_DivingSettings.chillDrownedAuroraEnabled || RM_DivingSettings.chillAuroraSurgeEnabled);

        private bool Sensing => isChillSeabed && SensingWanted;

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            isChillSeabed = RM_ChillFireGate.IsChillSeabedMap(map);
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!isChillSeabed)
            {
                return; // every other map in the game: one bool check, nothing else
            }
            if (--ticksUntilRescan > 0)
            {
                return;
            }
            ticksUntilRescan = RescanIntervalTicks;

            if (!SensingWanted)
            {
                return; // frozen at its last value while both consumers are off
            }

            float target = RawSurfaceIntensity();
            currentIntensity = Mathf.MoveTowards(currentIntensity, target, RampStepPerRescan);
        }

        /// <summary>
        /// CHILL_AURORA_SURGE_1's own hook — "CHILL_FLOOR_LIGHT_1 owns the
        /// coupling; this item consumes it." 0 (aurora fully quiet / off /
        /// not the Chill seabed) .. 1 (surface aurora at full strength).
        /// Smoothed, never a step. Safe to call unconditionally — off or
        /// off-map both simply read 0, same "no caller-side gating needed"
        /// idiom RM_MapComponent_ChillFootprints.TrailDensityAt documents.
        /// </summary>
        public float CurrentAuroraIntensity => Sensing ? currentIntensity : 0f;

        /// <summary>The floor-light read: CurrentAuroraIntensity, or 0 while the light toggle is off.</summary>
        public float LightIntensity => RM_DivingSettings.chillDrownedAuroraEnabled ? CurrentAuroraIntensity : 0f;

        /// <summary>
        /// Patch_ChillDrownedAurora's own read: the violet-teal SkyTarget
        /// this instant, built from CurrentAuroraIntensity and the slow
        /// independent colour ripple. Never call this off the Chill seabed
        /// — it returns a target regardless, the caller is expected to have
        /// already gated on IsChillSeabedMap (the patch does).
        /// </summary>
        public SkyTarget ComputeSkyTarget()
        {
            float t = LightIntensity;

            float ripplePhase = (Find.TickManager.TicksGame % RippleFullCycleTicks) / RippleFullCycleTicks;
            float ripple = (Mathf.Sin(ripplePhase * 2f * Mathf.PI) + 1f) * 0.5f;
            Color tint = Color.Lerp(TealColor, VioletColor, ripple);

            // Sky carries most of the tint, overlay a weaker echo of it —
            // the same ratio vanilla's own GameCondition_Aurora/
            // GameCondition_DarkAuroraMax use between their sky and overlay
            // lerp strengths, so terrain doesn't get over-tinted while the
            // open-sky read stays strongly violet-teal.
            Color sky = tint * Mathf.Lerp(0.25f, 1f, t);
            Color overlay = tint * Mathf.Lerp(0.08f, 0.35f, t);
            float glow = Mathf.Lerp(MinFloorGlow, MaxAuroraGlow, t);

            SkyColorSet colors = new SkyColorSet(sky, ShadowTint, overlay, 1f);
            return new SkyTarget(glow: glow, colorSet: colors, lightsourceShineSize: 1f, lightsourceShineIntensity: 0.6f);
        }

        /// <summary>
        /// The pocket map's own portal back to the surface —
        /// PocketMapParent.sourceMap (RimSage, RimWorld/Planet/
        /// PocketMapParent.cs), MEASURED as the field every pocket map
        /// carries a live reference through, not a paraphrase.
        /// </summary>
        private Map SourceMap()
        {
            if (map?.Parent is PocketMapParent pocket)
            {
                return pocket.sourceMap;
            }

            // Seabed-layer floor (the gravship path): the surface map above, when one is loaded.
            // With no loaded surface map the floor reads 0, same as the pocket path's null.
            if (map == null || !RM_SeabedLayerUtility.IsSeabedTile(map.Tile))
            {
                return null;
            }
            PlanetTile above = RM_SeabedLayerUtility.SurfaceTileOf(map.Tile);
            if (!above.Valid)
            {
                return null;
            }
            List<Map> maps = Find.Maps;
            for (int i = 0; i < maps.Count; i++)
            {
                if (maps[i] != map && maps[i].Tile == above)
                {
                    return maps[i];
                }
            }
            return null;
        }

        // "Is the surface tile experiencing [aurora] right now, and how
        // strong?" — checks BOTH aurora-family conditions that could be
        // active on the surface Chill tile (vanilla's own Aurora, and this
        // campaign's nightside-gated RM_WS_DarkAurora) rather than assuming
        // which one this world's geometry actually fires there, and takes
        // the stronger of the two if somehow both are active.
        // GameCondition.SkyTargetLerpFactor(Map) is PUBLIC on the base
        // class (RimSage, GameCondition.cs) — no reflection needed, works
        // for either concrete subtype.
        private float RawSurfaceIntensity()
        {
            Map source = SourceMap();
            if (source?.gameConditionManager == null)
            {
                return UnattendedIntensity();
            }

            float best = 0f;

            GameCondition vanilla = source.gameConditionManager.GetActiveCondition(GameConditionDefOf.Aurora);
            if (vanilla != null)
            {
                best = Mathf.Max(best, vanilla.SkyTargetLerpFactor(source));
            }

            GameConditionDef darkDef = DarkAuroraDef;
            if (darkDef != null)
            {
                GameCondition dark = source.gameConditionManager.GetActiveCondition(darkDef);
                if (dark != null)
                {
                    best = Mathf.Max(best, dark.SkyTargetLerpFactor(source));
                }
            }

            return best;
        }

        // CHILL_AURORA_UNATTENDED_SOURCE_1. With no surface map loaded above (the normal gravship case) the
        // floor used to read 0 forever, so the light, the surges and the collector never woke.
        // PROVISIONAL (auto-decided 2026-10-09, CHILL_AURORA_UNATTENDED_SOURCE_1): first a WORLD-level aurora
        // condition (Find.World.gameConditionManager) if one is active; otherwise an intrinsic floor schedule:
        // each in-game day, seeded by tile and day, has a 35% chance of an aurora night whose strength is a
        // sine envelope over the day's second half, peaking at 0.6-1.0. Toggle: chillAuroraUnattendedEnabled.
        private const float UnattendedAuroraDayChance = 0.35f;

        private float UnattendedIntensity()
        {
            if (!RM_DivingSettings.chillAuroraUnattendedEnabled)
            {
                return 0f;
            }

            GameConditionManager world = Find.World?.gameConditionManager;
            if (world != null)
            {
                float best = 0f;
                GameCondition vanilla = world.GetActiveCondition(GameConditionDefOf.Aurora);
                if (vanilla != null)
                {
                    best = Mathf.Max(best, vanilla.SkyTargetLerpFactor(map));
                }
                GameConditionDef darkDef = DarkAuroraDef;
                GameCondition dark = darkDef != null ? world.GetActiveCondition(darkDef) : null;
                if (dark != null)
                {
                    best = Mathf.Max(best, dark.SkyTargetLerpFactor(map));
                }
                if (best > 0f)
                {
                    return best;
                }
            }

            int ticks = Find.TickManager.TicksAbs;
            int day = ticks / GenDate.TicksPerDay;
            float dayFraction = (ticks % GenDate.TicksPerDay) / (float)GenDate.TicksPerDay;
            if (dayFraction < 0.5f)
            {
                return 0f;
            }
            int seed = Gen.HashCombineInt(map.Tile.tileId, day);
            if (Rand.ValueSeeded(seed) >= UnattendedAuroraDayChance)
            {
                return 0f;
            }
            float peak = Mathf.Lerp(0.6f, 1f, Rand.ValueSeeded(seed ^ 0x5f3759df));
            return peak * Mathf.Sin((dayFraction - 0.5f) * 2f * Mathf.PI);
        }
    }
}
