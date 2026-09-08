using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    public class HediffCompProperties_DWBoltShear : HediffCompProperties
    {
        /// Chance the bolt shears off per point of damage dealt in one hit,
        /// e.g. 0.02 means a 10-damage hit rolls a 1 - (1-0.02)^10 ≈ 18% chance.
        public float shearChancePerDamage = 0.02f;

        public HediffCompProperties_DWBoltShear() =>
            compClass = typeof(HediffComp_DWBoltShear);
    }

    /// <summary>
    /// DROIDWORKS_BOLT_PAYOFF_1 (packet B5): "shear on damage". Lives on
    /// RSW_DW_RestrainingBolt itself - any hit landing on the bolted pawn has
    /// a chance to physically shear the bolt off, an UNCONTROLLED removal
    /// (unlike Recipe_RemoveRestrainingBolt's deliberate one) that still
    /// leaves RSW_DW_BoltResentment exactly where it was - resentment never
    /// resets, however the bolt comes off.
    /// </summary>
    public class HediffComp_DWBoltShear : HediffComp
    {
        public HediffCompProperties_DWBoltShear Props =>
            (HediffCompProperties_DWBoltShear)props;

        public override void Notify_PawnPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            if (totalDamageDealt <= 0f) return;
            float shearChance = 1f - Mathf.Pow(1f - Props.shearChancePerDamage, totalDamageDealt);
            if (!Rand.Chance(shearChance)) return;

            Pawn p = Pawn;
            if (p == null || p.Dead) return;
            Hediff h = p.health.hediffSet.GetFirstHediffOfDef(DroidworksDefOf.RSW_DW_RestrainingBolt);
            if (h != null) p.health.RemoveHediff(h);
        }
    }
}
