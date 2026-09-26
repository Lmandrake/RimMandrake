using System.Collections.Generic;
using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_TENTACLE_BESTIARY_1. Bloom's own comp — "vast, opening,
    // exposes the eye" (§2). Unlike the other five limbs (RM_CompTentacleLimb,
    // a two-tier retreat/sever ladder), Bloom carries the eye's THREE-tier
    // ladder from §2b's own table:
    //   - light damage before it withdraws  -> ordinary retreat (short cooldown)
    //   - MODERATE damage before it withdraws -> every limb on the map is
    //     driven off for a day
    //   - SEVERE damage before it withdraws -> killed PERMANENTLY on this map
    //
    // 🔴 What this class deliberately does NOT do: decide how often Bloom
    // itself gets a chance to appear. The design sheet rules this is the
    // single most important unset tuning number in the whole biome ("too
    // rare and the permanent kill is unreachable... unset") and explicitly
    // says do not guess it — see this item's own "open" section and the
    // follow-up item filed at close. This comp only reacts once Bloom is
    // already on the map; RM_MapComponent_TentacleWatch's ambient roll
    // gives it a low, flagged-INVENTED weight among the other five limbs
    // as a placeholder, not a tuned answer to that question.
    public class RM_CompProperties_TentacleEye : CompProperties
    {
        public int retreatWindowTicks = 240;

        /// <summary>Fraction of MaxHitPoints for the MODERATE row. INVENTED: 0.4.</summary>
        public float moderateDamageFraction = 0.4f;

        /// <summary>Fraction of MaxHitPoints for the SEVERE row. INVENTED: 0.85.</summary>
        public float severeDamageFraction = 0.85f;

        public IntRange retreatCooldownTicks = new IntRange(3750, 10000);

        /// <summary>Ticks every limb on the map is driven off after a
        /// MODERATE hit on the eye. Not invented — the sheet says "a day"
        /// exactly: 60000 ticks.</summary>
        public int mapWideDriveOffTicks = 60000;

        public ThingDef harvestThing;
        public IntRange harvestCountRange = new IntRange(6, 12);

        public RM_CompProperties_TentacleEye()
        {
            compClass = typeof(RM_CompTentacleEye);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (moderateDamageFraction <= 0f || moderateDamageFraction >= severeDamageFraction)
            {
                yield return "RM_CompProperties_TentacleEye moderateDamageFraction must be > 0 and < severeDamageFraction.";
            }

            if (severeDamageFraction > 1f)
            {
                yield return "RM_CompProperties_TentacleEye severeDamageFraction must be <= 1.";
            }
        }
    }
}
