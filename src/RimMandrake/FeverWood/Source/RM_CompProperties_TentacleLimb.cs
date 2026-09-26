using System.Collections.Generic;
using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_TENTACLE_BESTIARY_1. XML shape for RM_CompTentacleLimb —
    // one of the "six limb-types" (feeler/snare/lash/porter/sentinel;
    // bloom uses RM_CompProperties_TentacleEye instead, see that class's
    // header). Every number below is INVENTED tuning, flagged per-field —
    // the design sheet rules the LADDER's shape (§2b) and the ROLES'
    // flavour (§2) but not a single one of these numbers.
    //
    //   <comps>
    //     <li Class="RimMandrake.FeverWood.RM_CompProperties_TentacleLimb">
    //       <role>Snare</role>
    //     </li>
    //   </comps>
    public class RM_CompProperties_TentacleLimb : CompProperties
    {
        public RM_TentacleRole role = RM_TentacleRole.Feeler;

        /// <summary>Ticks after first taking damage before this limb
        /// completes its withdrawal ("damaging them causes a retreat").
        /// INVENTED: 180 (3s) — long enough for one more hit, short enough
        /// to read as "it's already leaving".</summary>
        public int retreatWindowTicks = 180;

        /// <summary>Fraction of MaxHitPoints that must be dealt within the
        /// retreat window for the limb to be SEVERED instead of retreating
        /// cleanly (§2b: "severe damage before they can retreat can sever
        /// them"). INVENTED: 0.6.</summary>
        public float severeDamageFraction = 0.6f;

        /// <summary>Ticks the pool stays quiet after an ORDINARY retreat
        /// ("reset within hours"). INVENTED range: 1.5–4 in-game hours
        /// (2500 ticks/hour).</summary>
        public IntRange retreatCooldownTicks = new IntRange(3750, 10000);

        /// <summary>Ticks the pool stays quiet after a SEVER ("a full day
        /// of respite"). Not invented — the design sheet gives this number
        /// exactly: one day (60000 ticks).</summary>
        public int severRespiteTicks = 60000;

        /// <summary>What a severed limb drops. INVENTED default: the raw
        /// flesh resource this item ships (RM_SeveredTentacleFlesh).</summary>
        public ThingDef harvestThing;

        /// <summary>How many harvestThing stacks a sever drops. INVENTED:
        /// 2–5.</summary>
        public IntRange harvestCountRange = new IntRange(2, 5);

        // --- Lash-only (ranged strikes at range) ---
        /// <summary>Cells a Lash limb can reach. INVENTED: 6 — "strikes and
        /// wounds at maximum reach without grabbing".</summary>
        public float lashRange = 6f;
        public int lashIntervalTicks = 240;
        public float lashDamage = 8f;
        public float lashArmorPenetration = 0.2f;

        // --- Snare-only (grip + drag, rides F1's rescue window) ---
        public float snareRange = 1.9f;
        public int snareIntervalTicks = 200;

        // --- Porter-only (the treasure trickle) ---
        public IntRange porterDepositDelayTicks = new IntRange(600, 1800);

        public RM_CompProperties_TentacleLimb()
        {
            compClass = typeof(RM_CompTentacleLimb);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (retreatWindowTicks <= 0)
            {
                yield return "RM_CompProperties_TentacleLimb retreatWindowTicks must be > 0.";
            }

            if (severeDamageFraction <= 0f || severeDamageFraction > 1f)
            {
                yield return "RM_CompProperties_TentacleLimb severeDamageFraction must be in (0,1].";
            }
        }
    }
}
