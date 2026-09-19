using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1. SIMPLIFIED half of "builds armor out of
    // crystal shards it collects along the ground": passive, capped growth
    // while the carrier is spawned, alive and (by default) unroofed —
    // approximating "out foraging" without a real ground-clutter shard
    // resource def and a JobGiver to seek it out. That fuller version (an
    // actual pickable "crystal shard" Thing on Deeps terrain + a foraging
    // job) is explicitly OWED, not built this pass — see this item's own
    // status log. This half still delivers the player-visible outcome the
    // spec asked for (armor that visibly thickens over time, capped) with
    // no new ground-clutter content and no new JobDriver to get wrong
    // un-tested.
    //
    //   <comps>
    //     <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_ShardArmor">
    //       <armorHediff>RM_ShardArmor</armorHediff>
    //     </li>
    //   </comps>
    public class RM_CompShardArmor : ThingComp
    {
        private int ticksUntilCycle;

        public RM_CompProperties_ShardArmor Props => (RM_CompProperties_ShardArmor)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!respawningAfterLoad)
            {
                ticksUntilCycle = Rand.RangeInclusive(1, Mathf.Max(1, Props.cycleTicks));
            }
        }

        public override void CompTickRare()
        {
            base.CompTickRare();

            if (!RM_CreatureBehaviorsSettings.soulchimeShardArmorEnabled)
            {
                return;
            }

            if (!(parent is Pawn self) || !self.Spawned || self.Dead || self.health == null)
            {
                return;
            }

            ticksUntilCycle -= GenTicks.TickRareInterval;
            if (ticksUntilCycle > 0)
            {
                return;
            }
            ticksUntilCycle = Mathf.Max(1, Props.cycleTicks);

            if (Props.requireUnroofed && self.Position.Roofed(self.Map))
            {
                return; // not out where shards would actually be
            }

            Hediff hediff = self.health.hediffSet.GetFirstHediffOfDef(Props.armorHediff);
            if (hediff == null)
            {
                hediff = HediffMaker.MakeHediff(Props.armorHediff, self);
                hediff.Severity = 0f;
                self.health.AddHediff(hediff);
            }

            if (hediff.Severity >= Props.maxSeverity)
            {
                return;
            }

            float mult = Mathf.Max(0f, RM_CreatureBehaviorsSettings.soulchimeShardArmorRateMultiplier);
            hediff.Severity = Mathf.Min(Props.maxSeverity, hediff.Severity + Props.severityGainPerCycle * mult);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksUntilCycle, "ticksUntilCycle", 0);
        }
    }
}
