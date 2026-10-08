using System.Linq;
using Verse;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// The one place tier is computed. Everything else in the mod (comp
    /// auto-attach, the wake processor, the yield curve, the corpse-site
    /// conversion, LargePawnsBridge) calls through here rather than reading
    /// bodySize or the modExtension itself, so the auto-attach rule and the
    /// runtime tier can never drift apart.
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
            return RM_TitanicKernel.DefQualifies(raceDef.race.baseBodySize, Thresholds.t1MinBodySize,
                ForceOf(raceDef.GetModExtension<RM_TitanicExtension>()));
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
            // Pawn.BodySize = lifestage.bodySizeFactor * RaceProps.baseBodySize
            // (Verse/Pawn.cs). OPEN QUESTION (flagged, not guessed): whether any
            // gene StatDef offsets a separate "BodySize" stat outside this
            // formula is unconfirmed - if a future gene needs to move a pawn
            // between tiers independently of RaceProps/lifestage, that stat
            // must be found and read here rather than assumed absent.
            RM_TitanicTierDef t = Thresholds;
            return (TitanicTier)RM_TitanicKernel.TierFor(pawn.BodySize, t.t1MinBodySize, t.t2MinBodySize, t.t3MinBodySize,
                ForceOf(pawn.def.GetModExtension<RM_TitanicExtension>()));
        }
    }
}
