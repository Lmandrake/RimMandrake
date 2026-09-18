using System.Collections.Generic;
using RimWorld;
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

            IntVec3 origin = parent.Position;
            float radiusSq = Props.radius * Props.radius;
            bool wokeAny = false;

            // Snapshot: TryStartMentalState can trigger further reactions
            // (fleeing, aggro) that mutate the map's pawn list underneath us.
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p.Dead || p.Downed)
                {
                    continue;
                }

                if ((p.Position - origin).LengthHorizontalSquared > radiusSq)
                {
                    continue;
                }

                RM_AlarmResponderExtension ext = p.def.GetModExtension<RM_AlarmResponderExtension>();
                if (ext == null || ext.tag.NullOrEmpty())
                {
                    continue; // this race never answers any grove alarm
                }

                if (!Props.tag.NullOrEmpty() && ext.tag != Props.tag)
                {
                    continue; // wrong group for this specific alarm source
                }

                if (p.mindState == null || p.mindState.mentalStateHandler == null)
                {
                    continue;
                }

                if (p.InMentalState)
                {
                    continue;
                }

                if (p.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Manhunter, forceWake: true))
                {
                    wokeAny = true;
                }
            }

            if (wokeAny)
            {
                // Literal, not a translation key: this mod ships no
                // Languages/ folder (same posture as CompActiveGasEmitter's
                // own inspect string in EnvironmentalHazards).
                Messages.Message(
                    "The grove's mycelial network answers the disturbance.",
                    new TargetInfo(origin, map),
                    MessageTypeDefOf.ThreatBig);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastTriggerTick, "lastTriggerTick", -999999);
        }
    }
}
