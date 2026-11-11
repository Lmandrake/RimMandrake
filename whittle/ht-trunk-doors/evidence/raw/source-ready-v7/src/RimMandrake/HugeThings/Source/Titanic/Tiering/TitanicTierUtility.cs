using System.Linq;
using RimWorld;
using Verse;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// The one place tier is computed. Everything else in the mod (comp
    /// auto-attach, the wake processor, the yield curve, the corpse-site
    /// conversion, LargePawnsBridge) calls through here rather than reading
    /// bodySize or the modExtension itself. Comp attachment is conservative;
    /// event eligibility uses lineage, spacing uses supported stages, and runtime uses actual size.
    /// </summary>
    public static class TitanicTierUtility
    {
        private static RM_TitanicTierDef cachedThresholds;
        private static readonly RM_TitanicTierDef customThresholds = new RM_TitanicTierDef { defName = "RM_TitanicTiers_ModSettings" };

        /// <summary>
        /// The ladder in force: the player's custom tiers (Mod Settings, giant animals on, custom tiers on, and strictly rising),
        /// else the shipped RM_TitanicTierDef. Which races carry the wake comp and the Large Pawns rows are decided from this at
        /// startup, so a change that moves a race across T1 needs a restart (the settings label says so); runtime tiers follow
        /// it at once.
        /// </summary>
        public static RM_TitanicTierDef Thresholds
        {
            get
            {
                if (RM_HugeThingsSettings.TierThresholdsCustomActive
                    && RM_TitanicKernel.ThresholdsValid(RM_HugeThingsSettings.tierT1MinBodySize, RM_HugeThingsSettings.tierT2MinBodySize,
                                                        RM_HugeThingsSettings.tierT3MinBodySize))
                {
                    customThresholds.t1MinBodySize = RM_HugeThingsSettings.tierT1MinBodySize;
                    customThresholds.t2MinBodySize = RM_HugeThingsSettings.tierT2MinBodySize;
                    customThresholds.t3MinBodySize = RM_HugeThingsSettings.tierT3MinBodySize;
                    return customThresholds;
                }
                return ShippedThresholds;
            }
        }

        /// <summary>The shipped ladder, Defs/TitanicTierDefs/RM_TitanicTierDef.xml.</summary>
        public static RM_TitanicTierDef ShippedThresholds
        {
            get
            {
                if (cachedThresholds == null)
                {
                    cachedThresholds = DefDatabase<RM_TitanicTierDef>.AllDefsListForReading.FirstOrDefault();
                    if (cachedThresholds == null)
                    {
                        Log.Error("[RimMandrake.TitanicCreatures] No RM_TitanicTierDef found - " +
                                  "Defs/TitanicTierDefs/RM_TitanicTierDef.xml is missing or failed to " +
                                  "load. Falling back to hardcoded defaults (4/8/20); fix the XML.");
                        cachedThresholds = new RM_TitanicTierDef();
                    }
                }
                return cachedThresholds;
            }
        }

        /// <summary>RM_TitanicExtension.forceEnabled as the kernel's tri-state.</summary>
        public static int ForceOf(RM_TitanicExtension ext)
        {
            if (ext == null || ext.forceEnabled == null) return RM_TitanicKernel.ForceAuto;
            return ext.forceEnabled == true ? RM_TitanicKernel.ForceIn : RM_TitanicKernel.ForceOut;
        }

        /// <summary>
        /// Def-level qualification check: could ANY pawn of this race ever be
        /// tiered? Used only to decide whether to auto-attach CompTitanicWake
        /// at def-load time (a lifestage/gene swelling a borderline race past
        /// the floor at runtime must not require the comp to already be
        /// present, so this checks the race's base bodySize, not any one
        /// pawn's current BodySize).
        /// </summary>
        public static bool DefQualifies(ThingDef raceDef)
        {
            if (raceDef?.race == null)
            {
                return false;
            }
            // TITAN_WAKE_FIXES_1 (B3.18 / C3.4): Pawn.BodySize = CurLifeStage.bodySizeFactor * baseBodySize, so qualify on the base times
            // the largest life-stage factor; a race whose adult stage swells past T1 must carry the comp from the start.
            float maxFactor = 1f;
            if (raceDef.race.lifeStageAges != null)
                foreach (LifeStageAge a in raceDef.race.lifeStageAges)
                    if (a?.def != null && a.def.bodySizeFactor > maxFactor) maxFactor = a.def.bodySizeFactor;
            return RM_TitanicKernel.DefQualifies(raceDef.race.baseBodySize, maxFactor, Thresholds.t1MinBodySize,
                ForceOf(raceDef.GetModExtension<RM_TitanicExtension>()));
        }

        /// <summary>TITAN_CAMPS_SCAVENGERS_EVENTS_1: the tier a race's grown adult reaches (base size times its largest life-stage
        /// factor) - what decides whether a race is a titan for the titan event and a non-titan for the scavenger draw.</summary>
        public static TitanicTier AdultTier(ThingDef raceDef)
        {
            if (raceDef?.race == null) return TitanicTier.None;
            float maxFactor = 1f;
            if (raceDef.race.lifeStageAges != null)
                foreach (LifeStageAge a in raceDef.race.lifeStageAges)
                    if (a?.def != null && a.def.bodySizeFactor > maxFactor) maxFactor = a.def.bodySizeFactor;
            RM_TitanicTierDef t = Thresholds;
            return (TitanicTier)RM_TitanicKernel.TierFor(raceDef.race.baseBodySize * maxFactor, t.t1MinBodySize, t.t2MinBodySize,
                t.t3MinBodySize, ForceOf(raceDef.GetModExtension<RM_TitanicExtension>()));
        }

        /// <summary>Passage spacing only: the largest supported stage of this race. Lineage eligibility stays on AdultTier
        /// ("Calves are ok"). Incomplete/malformed stage data cannot justify relaxing spacing, so it falls back to AdultTier.
        /// Read the current ladder every time; neither tiers nor stage factors are cached. Comp attachment stays separate.</summary>
        public static TitanicTier SpacingTier(ThingDef raceDef)
        {
            if (raceDef?.race == null) return TitanicTier.None;
            float maxFactor = RM_TitanicKernel.MaxSupportedLifeStageFactor(
                raceDef.race.lifeStageAges?.Select(a => a?.def == null ? float.NaN : a.def.bodySizeFactor));
            if (!RM_TitanicKernel.Finite(maxFactor)) return AdultTier(raceDef);
            RM_TitanicTierDef t = Thresholds;
            return (TitanicTier)RM_TitanicKernel.TierFor(raceDef.race.baseBodySize * maxFactor, t.t1MinBodySize,
                t.t2MinBodySize, t.t3MinBodySize, ForceOf(raceDef.GetModExtension<RM_TitanicExtension>()));
        }

        /// <summary>
        /// The runtime tier for one pawn right now - the authority every
        /// other system in this mod reads.
        /// </summary>
        public static TitanicTier GetTier(Pawn pawn)
        {
            if (pawn?.RaceProps == null)
            {
                return TitanicTier.None;
            }
            // Core BodySize is current-stage factor times base size. Loaded postfixes can modify that getter
            // (VEF adds its cached offset and floors at 0.05); read the actual property, never substitute a formula.
            // Def-level event spacing cannot forecast external runtime modifiers. The L1 needs-null fixture exercises
            // VEF's default-cache branch only, not generated-pawn gene/hediff modifier computation.
            RM_TitanicTierDef t = Thresholds;
            return (TitanicTier)RM_TitanicKernel.TierFor(pawn.BodySize, t.t1MinBodySize, t.t2MinBodySize, t.t3MinBodySize,
                ForceOf(pawn.def.GetModExtension<RM_TitanicExtension>()));
        }
    }
}
