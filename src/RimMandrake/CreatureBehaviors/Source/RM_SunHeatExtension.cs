using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // SOLAR_HEAT_EXPOSURE_1 §2 — the per-biome heat kind.
    //
    // Owner ruling (longshade_shade_ideation_2026-09-29.md, "Rulings —
    // volley turn 4"): heat is ONE kind, planet-wide. Sun exposure feeds the
    // game's EXISTING heat — it raises what a pawn feels (AmbientTemperature),
    // so the vanilla comfortable range, apparel insulation and Heatstroke
    // keep their vanilla meaning. There is no sun hediff. What differs per
    // biome is only what PROTECTS you:
    //   overhead — the Long Shade: roofs and cast shade.
    //   lowSun   — the Deep Desert: only a vertical caster's lee shadow.
    //   ambient  — steam / volcanic: shade does nothing; insulation or an
    //              enclosed room.
    //
    // A BiomeDef that carries this extension IS a sun-heat biome. Every
    // map-wide effect (heat, sun-cost pathing, the sun-load readout) is gated
    // on it, and on the Creature Behaviors settings. Wire it with
    // MayRequire="mandrake.rm.creaturebehaviors" on the <li>, as the Long
    // Shade does for RM_PinnedSunExtension.
    //
    // All numbers are INVENTED first values; the owner-watched sitting in
    // the item's criteria rules on the strictness.
    // ════════════════════════════════════════════════════════════════════
    public class RM_SunHeatExtension : DefModExtension
    {
        public RM_HeatKind heatKind = RM_HeatKind.overhead;

        /// <summary>°C added to a size-1 pawn's felt temperature at full
        /// exposure, before the Mod Settings strength dial.</summary>
        public float heatOffsetC = 30f;

        /// <summary>Hard cap on the offset after the body-size term.</summary>
        public float maxHeatOffsetC = 70f;

        /// <summary>Offset × (1 / bodySize)^this. 0 = size does not matter.</summary>
        public float bodySizeExponent = 0.5f;
        public float minBodySizeFactor = 0.25f;
        public float maxBodySizeFactor = 2.5f;

        /// <summary>Extra path cost per fully exposed cell (a cardinal step
        /// costs 13), before the Mod Settings path dial. Ignored for
        /// ambient heat, where shade is not worth a detour.</summary>
        public float sunPathCostPerCell = 20f;

        // ── the sun, when the biome has no pinned sun ───────────────────
        /// <summary>Used ONLY when the map has no active RM_PinnedSunExtension
        /// (which is preferred, because then the rendered shadows and the
        /// mechanical shade are the same cells). Same geometry as the pinned
        /// sun: bearing and arc from the map's tile to the substellar point.</summary>
        public float substellarLatitude = 0f;
        public float substellarLongitude = 0f;
        public float minElevationDegrees = 5f;
        public float maxElevationDegrees = 60f;

        // ── STILLSAND_SUN_FROM_LATITUDE_1: the sun's height decides ─────
        // All three are off by default, so every existing sun-heat biome is
        // unchanged. Elevation is the map's sun elevation: the pinned sun's
        // when the biome has one, else the geometry above — always from the
        // tile's planet position, never from a region name.

        /// <summary>When ≥ 0: at or above this elevation the heat kind is
        /// overhead (roofs and parasols count), below it lowSun (only a lee
        /// or rock counts). Ignored for ambient heat. Negative = off.</summary>
        public float overheadAboveElevationDegrees = -1f;

        /// <summary>When true, heatOffsetC is the offset at the substellar
        /// point (sun at 90°) and the map's offset is heatOffsetC ×
        /// sin(elevation), never below minScaledHeatOffsetC.</summary>
        public bool heatScalesWithElevation = false;
        public float minScaledHeatOffsetC = 0f;

        /// <summary>Sand glare: exposure on natural sand (TerrainDef
        /// categoryType Sand, not a constructed floor) never drops below this,
        /// even in shade, before the Mod Settings strength dial. 0 = off.</summary>
        public float sandGlareExposureFloor = 0f;

        // ── STILLSAND_GLARE_BLIND_GOGGLES_1: glare-blind (RM_GlareBlind.cs) ─
        /// <summary>The hediff unprotected humanlike eyes take in full glare
        /// (it carries its own Sight stages and SeverityPerDay recovery).
        /// Null = this biome does not blind. Protection is a gene or apparel
        /// carrying RM_GlareProtectionExtension, or apparel tagged
        /// RM_GlareProtection — never a race or defName list.</summary>
        public HediffDef glareBlindHediff;

        /// <summary>Exposure (RM_MapComponent_ShadeGrid.ExposureFor) at or
        /// above which a pawn stands in full glare.</summary>
        public float glareBlindExposureMin = 0.6f;

        /// <summary>Severity gained per day spent in full glare, before the
        /// hediff's own decay and the Mod Settings rate dial.</summary>
        public float glareBlindSeverityPerDay = 4f;

        // ── STILLSAND_MIRAGE_CONDITION_1: the mirage (RM_Mirage.cs) ──────
        /// <summary>The permanent GameCondition (class RM_GameCondition_Mirage)
        /// held on this map while the sun stands at or above
        /// mirageMinElevationDegrees. Null = no mirage here.</summary>
        public GameConditionDef mirageCondition;

        public float mirageMinElevationDegrees = 45f;

        /// <summary>The "chasing the water" state a heat-struck pawn can break
        /// into (class RM_MentalState_ChasingWater).</summary>
        public MentalStateDef mirageMentalState;

        /// <summary>Heatstroke severity at or above which a pawn standing in
        /// full sun may break.</summary>
        public float mirageHeatstrokeMin = 0.2f;

        /// <summary>Mean days between breaks for one such pawn, before the
        /// Mod Settings dial.</summary>
        public float mirageBreakMtbDays = 1.5f;

        /// <summary>Exposure at or above which a pawn is "in full sun" for the
        /// break and for the heat-shimmer accuracy cut.</summary>
        public float mirageFullSunExposureMin = 0.6f;

        // ── §5 shade hopping / §6 dash ring (RM_ShadeHop.cs) ───────────
        /// <summary>A cell with exposure at or below this counts as shade in
        /// the patch graph.</summary>
        public float shadeExposureMax = 0.35f;

        /// <summary>Shade groups smaller than this are flecks, not patches.</summary>
        public int minPatchCells = 2;

        /// <summary>Heatstroke severity a wild animal will accept on one dash
        /// (visible heatstroke starts at 0.04). Its current severity is
        /// subtracted, so an animal that is already hot stays put.</summary>
        public float dashHeatstrokeBudget = 0.008f;

        public float minDashCells = 3f;
        public float maxDashCells = 24f;

        /// <summary>Chance per decision that a cool animal in shade moves on
        /// rather than resting.</summary>
        public float hopChance = 0.35f;

        public IntRange restTicks = new IntRange(600, 1500);
        public IntRange rimPauseTicks = new IntRange(45, 120);

        /// <summary>§6 ring: the Heatstroke a drafted colonist may take before
        /// it is back in shade (just short of visible), and the ring's cap.</summary>
        public float ringHeatstrokeBudget = 0.035f;
        public float ringMaxCells = 60f;
    }

    /// <summary>
    /// On a race ThingDef, this is optional and tunes §5 shade hopping for one species.
    /// exempt: the species ignores shade hopping, such as a native sun-lover.
    /// rangeFactor: scales its dash range.
    /// </summary>
    public class RM_SunDashExtension : DefModExtension
    {
        public bool exempt;
        public float rangeFactor = 1f;
    }
}
