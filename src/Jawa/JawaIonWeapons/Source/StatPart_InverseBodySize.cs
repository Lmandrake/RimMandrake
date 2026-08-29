using RimWorld;
using Verse;

namespace JawaIonWeapons
{
    /// <summary>
    /// Second multiplier that turns the owner's ruled bodySize^2 stun-scaling standard
    /// (ION_STUN_IGNORES_BODY_SIZE_1, C# in DamageWorker_IonBuildup for OUR OWN weapon) into a
    /// pure-XML route for a THIRD-PARTY weapon with no C# of ours to patch
    /// (OTHER_STUN_WEAPONS_SURVEY_1, guy762_RangedDamage_sonic / guy762_RangedDamage_KOstun).
    ///
    /// Verse.Pawn_HealthTracker.PostApplyDamage already multiplies a DamageDefAdditionalHediff's
    /// severity by 1/BodySize ONCE when victimSeverityScalingByInvBodySize is true, and by an
    /// arbitrary StatDef's value when victimSeverityScaling names one - the two multiply
    /// together (source read, not guessed):
    ///     num *= 1f / pawn.BodySize;                                  // ByInvBodySize
    ///     num *= pawn.GetStatValue(victimSeverityScaling);            // this StatDef's value
    /// So a StatDef whose value IS 1/BodySize, pointed at by victimSeverityScaling on a li that
    /// also sets victimSeverityScalingByInvBodySize=true, composes to bodySize^2 with no
    /// Harmony and no new DamageWorker - see Patches/ThirdPartyStunBodySize_Squared.xml.
    /// </summary>
    public class StatPart_InverseBodySize : StatPart
    {
        public override void TransformValue(StatRequest req, ref float val)
        {
            if (req.Thing is Pawn pawn && pawn.BodySize > 0f)
            {
                val = 1f / pawn.BodySize;
            }
        }

        public override string ExplanationPart(StatRequest req)
        {
            if (req.Thing is Pawn pawn && pawn.BodySize > 0f)
            {
                return "1 / body size (" + pawn.BodySize.ToString("F2") + ")";
            }
            return null;
        }
    }
}
