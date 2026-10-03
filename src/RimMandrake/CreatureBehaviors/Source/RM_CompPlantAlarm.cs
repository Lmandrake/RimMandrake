using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ROT_GUARDIAN_GROVES_1 (rot_kit_spec.md M6, "the network alarm"). The
    // fallback for RUT_RegenerantVeil: RM_CompBeastWakeRelay (EnvironmentalHazards,
    // read in full this pass) was checked first and does NOT fit — its only
    // signal is RM_CompWorkedLottery's static BeastWakeRequested event (a
    // dig-lottery disturbance, unrelated to plant damage), not a
    // damage-taken hook, and it relays into CompWakeUpDormant.Activate()
    // specifically, which no plant carries. This is the "small new comp"
    // the ticket calls for instead, generic and content-blind like every
    // other mechanism in this assembly (RM_CompWoundLink, M7, is the direct
    // sibling pattern: a comp + a DefModExtension tag on the race, zero
    // hardcoded species).
    //
    // Two ways to ring the alarm: automatically, when the carrying Thing
    // takes damage (RUT_RegenerantVeil's own "harvesting/damaging it wakes
    // nearby hybrid fauna"); or on demand via the public TriggerAlarm(),
    // which RUT_Plant_FalseFruit's PlantCollected override calls directly
    // (harvesting a plant is not damage — Plant.PlantCollected is the only
    // seam for that, RimSage-verified against RimWorld/Plant.cs this pass,
    // no TakeDamage involved).
    //
    //   <comps>
    //     <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_PlantAlarm">
    //       <radius>18</radius>
    //     </li>
    //   </comps>
    public class RM_CompPlantAlarm : ThingComp
    {
        private int lastTriggerTick = -999999;

        public RM_CompProperties_PlantAlarm Props => (RM_CompProperties_PlantAlarm)props;

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            TriggerAlarm();
        }

        // Public so a harvest hook (or a quicktest) can ring the alarm
        // without needing a damage event at all.
        public void TriggerAlarm()
        {
            if (!RM_CreatureBehaviorsSettings.guardianAlarmEnabled)
            {
                return; // mod option: guardian defenses disabled
            }

            if (!parent.Spawned)
            {
                return;
            }

            Map map = parent.Map;
            if (map == null)
            {
                return;
            }

            int now = Find.TickManager.TicksGame;
            if (now - lastTriggerTick < Props.cooldownTicks)
            {
                return;
            }
            lastTriggerTick = now;

            // REACTION_MECHANISM_GENERALISE_1 step 4: the same behaviour, now
            // on the general path — one event (propagation none), one
            // RM_ReactionResponseRule_WakeResponders built from this comp's
            // own radius/tag. The event budget is effectively unbounded so the
            // radius stays the only bound, exactly as before the migration.
            // No instigator is recorded: the wake response never reads one.
            RM_ReactionEvent evt = new RM_ReactionEvent(
                parent, map, parent.Position, Props.tag, null, int.MaxValue);
            evt.TryMarkActivated(parent);
            WakeResponse.Respond(evt, parent);
        }

        private RM_ReactionResponseRule_WakeResponders wakeResponse;

        // Built once per comp from its props. Literal message, not a
        // translation key: this mod ships no Languages/ folder for it (same
        // posture as CompActiveGasEmitter's own inspect string in
        // EnvironmentalHazards).
        private RM_ReactionResponseRule_WakeResponders WakeResponse =>
            wakeResponse ?? (wakeResponse = new RM_ReactionResponseRule_WakeResponders
            {
                radius = Props.radius,
                wokeMessage = "The grove's mycelial network answers the disturbance.",
            });

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastTriggerTick, "lastTriggerTick", -999999);
        }
    }
}
