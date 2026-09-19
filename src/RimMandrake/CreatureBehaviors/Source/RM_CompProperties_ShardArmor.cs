using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1 (owner's own words, Soulchime: "builds armor
    // out of crystal shards it collects along the ground."). See
    // RM_CompShardArmor's own header for the scope this pass actually
    // builds versus the fuller version still owed — this is the simplified
    // half: passive, capped, periodic growth while the carrier is outdoors,
    // not a real forage-a-specific-ground-item job loop.
    public class RM_CompProperties_ShardArmor : CompProperties
    {
        /// <summary>The armor hediff this comp grows. Expected to carry
        /// <stages> with statOffsets (ArmorRating_Sharp/Blunt) gated by
        /// minSeverity, so "more shards" reads as thicker armor in the
        /// health tab, not just a hidden number.</summary>
        public HediffDef armorHediff;

        /// <summary>Severity gained per growth cycle while eligible.
        /// INVENTED: 0.05.</summary>
        public float severityGainPerCycle = 0.05f;

        /// <summary>Severity cap — "collects shards" has to stop somewhere,
        /// a Soulchime doesn't turn into a walking fortress. INVENTED: 1.0
        /// (matches armorHediff's own expected severity range).</summary>
        public float maxSeverity = 1f;

        /// <summary>Ticks between growth cycles. INVENTED: 15000 (a
        /// quarter in-game day) — shard-gathering is meant to read as slow,
        /// patient accumulation over a colony's whole stay, not minutes.</summary>
        public int cycleTicks = 15000;

        /// <summary>Only grows while the carrier is unroofed — "collects
        /// shards along the ground" reads as foraging outdoors, not sitting
        /// in a cage. Set false to grow anywhere.</summary>
        public bool requireUnroofed = true;

        public RM_CompProperties_ShardArmor()
        {
            compClass = typeof(RM_CompShardArmor);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (armorHediff == null)
            {
                yield return "RM_CompProperties_ShardArmor needs an armorHediff.";
            }

            if (severityGainPerCycle < 0f)
            {
                yield return "RM_CompProperties_ShardArmor severityGainPerCycle must be >= 0.";
            }

            if (maxSeverity <= 0f)
            {
                yield return "RM_CompProperties_ShardArmor maxSeverity must be > 0.";
            }

            if (cycleTicks <= 0)
            {
                yield return "RM_CompProperties_ShardArmor cycleTicks must be > 0.";
            }
        }
    }
}
