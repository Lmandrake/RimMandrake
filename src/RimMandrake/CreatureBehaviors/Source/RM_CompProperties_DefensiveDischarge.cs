using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // WASTELAND_BRINE_BATTERY_DISCHARGE_1. wasteland.md §4: "Hypersaline
    // pools over mineral beds are half a voltaic cell; what lives in them
    // runs on ion gradients and discharges them as defense." See
    // RM_CompDefensiveDischarge for the mechanism this drives.
    //
    //   <comps>
    //     <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_DefensiveDischarge" />
    //   </comps>
    public class RM_CompProperties_DefensiveDischarge : CompProperties
    {
        /// <summary>The damage this comp deals back to whoever just hurt
        /// its owner. Null (the XML default) resolves to vanilla's own
        /// DamageDefOf.EMP at the point of use in RM_CompDefensiveDischarge
        /// — same null-then-DamageDefOf-fallback pattern this assembly
        /// already uses in RM_CompGrappler (never resolved eagerly as a
        /// field initializer here, since CompProperties fields are set
        /// during early XML class instantiation, before DefOfHelper is
        /// guaranteed to have resolved DamageDefOf's own static fields).
        /// EMP (Core, no MayRequire — confirmed via RimSage's DamageDefOf
        /// symbol dump) ships with harmsHealth=false + causeStun=true,
        /// which is exactly "a defensive shock, not a ranged attack" — it
        /// does not wound the attacker, it stuns them, the way grabbing an
        /// electrified pool lid should feel.</summary>
        public DamageDef dischargeDamageDef;

        /// <summary>Discharge "damage" amount fed to the DamageInfo (for
        /// EMP this drives stun duration via causeStun, not health loss).
        /// INVENTED: 12 — enough to stagger a single attacker for a few
        /// seconds, not a fight-ending burst; the creature has no offense of
        /// its own beyond the weak "discharge" melee tool already on
        /// RUT_BrineBattery's ThingDef.</summary>
        public float dischargeAmount = 12f;

        /// <summary>Only an instigator within this many cells of the owner
        /// gets shocked — a water-conducted defense doesn't reach a shooter
        /// standing off at range. INVENTED: 1.9 (covers an adjacent
        /// orthogonal or diagonal attacker; matches vanilla's own adjacency
        /// convention for melee range).</summary>
        public float dischargeRange = 1.9f;

        /// <summary>Ticks between discharges — being hit repeatedly in one
        /// fight doesn't re-zap the same attacker every single swing.
        /// INVENTED: 600 (10 seconds).</summary>
        public int dischargeCooldownTicks = 600;

        public RM_CompProperties_DefensiveDischarge()
        {
            compClass = typeof(RM_CompDefensiveDischarge);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (dischargeAmount <= 0f)
            {
                yield return "RM_CompProperties_DefensiveDischarge dischargeAmount must be > 0.";
            }

            if (dischargeRange <= 0f)
            {
                yield return "RM_CompProperties_DefensiveDischarge dischargeRange must be > 0.";
            }

            if (dischargeCooldownTicks < 0)
            {
                yield return "RM_CompProperties_DefensiveDischarge dischargeCooldownTicks must be >= 0.";
            }
        }
    }
}
