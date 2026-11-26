using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // Optional per-biome data beside Direct Sun. It decides NOTHING about Direct
    // Sun's heat, shade, sun elevation or path cost.
    //
    // DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES (owner, 2026-10-19: "no
    // biome-specific heat, no biome-specific sun. It's a matter of
    // geometry"): Direct Sun runs on every sunlit map of a fixed-sun world,
    // with no biome opt-in, by the planet constants in RM_DirectSun. The
    // heat kind, heat offset, scaling, floor, threshold, elevation clamps,
    // body-size terms, path cost and glare floor were removed from this
    // class. A biome without this extension reads RM_SunHeatExtension.Planet
    // (all defaults).
    //
    // What stays here is behaviour data a biome still carries (the glare-blind
    // hediff, the mirage, the shade-hop and dash tuning): each is its mod's
    // conversion row for its next version
    // (design/specs/2026-11-21-guiding-principles/conversion_list.md).
    // The removed fields are stripped at load from any BiomeDef that still
    // names them (CreatureBehaviors/Patches/RM_DirectSun_LegacyFields.xml),
    // so a held mod's XML loads clean until its own next build strips them.
    // ════════════════════════════════════════════════════════════════════
    public class RM_SunHeatExtension : DefModExtension
    {
        /// <summary>The defaults every map without its own extension reads.</summary>
        public static readonly RM_SunHeatExtension Planet = new RM_SunHeatExtension();

        /// <summary>LEGACY, decides nothing in Direct Sun: Stillsand's compiled RM_PreciousCaves reads these two
        /// for a cave bearing when no pinned sun is active, and Stillsand is held by the owner, so its DLL is not
        /// rebuilt. Direct Sun takes its sun from RM_PlanetSunGeometry. Delete both when Stillsand next builds
        /// (RIMMANDRAKE_STRIP_HELD_BIOMES_LEGACY_SUN_FIELDS_AT_LIFT).</summary>
        public float substellarLatitude = 0f;
        public float substellarLongitude = 0f;

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
