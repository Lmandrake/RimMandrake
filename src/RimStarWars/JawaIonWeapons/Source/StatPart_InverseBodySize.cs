using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.JawaIonWeapons
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
        /// <summary>
        /// MOD_OPTIONS_RETROFIT_1. The engine ALREADY supplies one factor of
        /// 1/BodySize on any li that sets victimSeverityScalingByInvBodySize, so
        /// this part only has to supply the REMAINDER of the player's chosen
        /// exponent: total = 1 (engine) + this. At the default
        /// bodySizeResistExponent of 2 that remainder is 1, i.e. exactly the
        /// shipped `val = 1f / pawn.BodySize`.
        /// </summary>
        private static float RemainderExponent
        {
            get { return RSW_JawaIonWeaponsSettings.bodySizeResistExponent - 1f; }
        }

        public override void TransformValue(StatRequest req, ref float val)
        {
            if (!RSW_JawaIonWeaponsSettings.thirdPartyBodySizeScaling)
            {
                // Leave val at the StatDef's own defaultBaseValue of 1.0 — a
                // neutral multiplier, so a third-party weapon keeps whatever
                // scaling it had before this mod existed.
                return;
            }
            if (req.Thing is Pawn pawn && pawn.BodySize > 0f)
            {
                float scaled = Mathf.Pow(pawn.BodySize, RemainderExponent);
                if (scaled > 0f)
                {
                    val = 1f / scaled;
                }
            }
        }

        public override string ExplanationPart(StatRequest req)
        {
            if (!RSW_JawaIonWeaponsSettings.thirdPartyBodySizeScaling)
            {
                return "body-size stun scaling for other mods' weapons is off in mod settings";
            }
            if (req.Thing is Pawn pawn && pawn.BodySize > 0f)
            {
                return "1 / body size (" + pawn.BodySize.ToString("F2") + ") ^ "
                       + RemainderExponent.ToString("F2");
            }
            return null;
        }
    }
}
