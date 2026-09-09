using System.Linq;
using Verse;

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

        public static RM_TitanicTierDef Thresholds
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
            RM_TitanicExtension ext = raceDef.GetModExtension<RM_TitanicExtension>();
            if (ext != null && ext.forceEnabled == false)
            {
                return false;
            }
            if (ext != null && ext.forceEnabled == true)
            {
                return true;
            }
            return raceDef.race.baseBodySize >= Thresholds.t1MinBodySize;
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
            RM_TitanicExtension ext = pawn.def.GetModExtension<RM_TitanicExtension>();
            if (ext != null && ext.forceEnabled == false)
            {
                return TitanicTier.None;
            }
            bool forcedOn = ext != null && ext.forceEnabled == true;

            // Pawn.BodySize = lifestage.bodySizeFactor * RaceProps.baseBodySize
            // (Verse/Pawn.cs). OPEN QUESTION (flagged, not guessed): whether any
            // gene StatDef offsets a separate "BodySize" stat outside this
            // formula is unconfirmed - if a future gene needs to move a pawn
            // between tiers independently of RaceProps/lifestage, that stat
            // must be found and read here rather than assumed absent.
            float bodySize = pawn.BodySize;
            RM_TitanicTierDef t = Thresholds;

            TitanicTier tier;
            if (bodySize >= t.t3MinBodySize)
            {
                tier = TitanicTier.T3;
            }
            else if (bodySize >= t.t2MinBodySize)
            {
                tier = TitanicTier.T2;
            }
            else if (bodySize >= t.t1MinBodySize)
            {
                tier = TitanicTier.T1;
            }
            else
            {
                tier = TitanicTier.None;
            }

            if (tier == TitanicTier.None && forcedOn)
            {
                tier = TitanicTier.T1;
            }
            return tier;
        }
    }
}
