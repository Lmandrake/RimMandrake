using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.CreatureBehaviors
{
    // REACTION_MECHANISM_GENERALISE_1 step 3 (FEVERWOOD_ANT_HIVE_DUNGEON_1).
    // "Rally existing responders toward the origin without berserking them"
    // (reaction_mechanism_spec.md). `source` is the responder itself (a pawn
    // carrying RM_CompReactionSource, reached either by its own detection or
    // by RM_ReactionPropagationRule_RespondersWithinRadius).
    //
    // What "rally without berserk" IS here — the spec's open engine question,
    // answered from the shape this assembly already proved:
    //   - with an instigator (the intruder that was noticed, or whoever did
    //     the damage): `mentalState` — RM_HiveRally, an
    //     RM_MentalState_ScopedAggression — aimed at THAT pawn only, anchored
    //     on the event's origin with a hive-sized disengage radius. Vanilla
    //     JobGiver_Manhunter (inherited, MEASURED 2026-09-20) then chases it
    //     through the corridors; nothing else on the map is a target, and
    //     leaving the hive's reach ends it.
    //   - without one (a harvest-style trigger, an intruder already gone):
    //     converge — a sprinting Goto to a cell near the origin, then the
    //     pawn's own think tree resumes.
    //
    // 🔴 The hive must telegraph (the owner's own stated cost on this choice).
    // Three signs, all optional in XML, so a non-hive consumer can stay quiet:
    //   - `alarmSound` played once per EVENT at the origin (evt.Announced),
    //   - `alarmMessage` posted once per event as a ThreatBig message,
    //   - `telegraphText` thrown as a text mote over EVERY responder that
    //     answers, so the rally is visibly spreading room to room.
    //
    // Budget: `budgetCost` per responder from the shared event. A responder in
    // a suppressed cell (step 5) does not answer and spends nothing.
    //
    //   <response Class="RimMandrake.CreatureBehaviors.RM_ReactionResponseRule_Rally">
    //     <mentalState>RM_HiveRally</mentalState>
    //     <disengageRadius>45</disengageRadius>
    //     <alarmSound>Pawn_Megascarab_Angry</alarmSound>
    //     <alarmMessage>The hive has noticed you.</alarmMessage>
    //   </response>
    public class RM_ReactionResponseRule_Rally : RM_ReactionResponseRule
    {
        public MentalStateDef mentalState;

        /// <summary>How far the intruder must get from the event's origin before a rallied responder gives up. INVENTED default 40 — a hive, not a gall; the consumer sets its own.</summary>
        public float disengageRadius = 40f;

        public int budgetCost = 1;

        /// <summary>Converge target spread around the origin when there is no instigator to chase.</summary>
        public int convergeRadius = 4;

        public SoundDef alarmSound;

        public string alarmMessage;

        public string telegraphText = "!";

        public Color telegraphColor = new Color(0.95f, 0.35f, 0.2f);

        public override void Respond(RM_ReactionEvent evt, Thing source)
        {
            Pawn pawn = source as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed || pawn.Map != evt.Map)
            {
                return;
            }

            if (pawn.InMentalState || pawn.mindState?.mentalStateHandler == null || pawn.jobs == null)
            {
                return; // already rallied (or otherwise occupied) — never re-charged
            }

            if (pawn.Faction != null)
            {
                return; // a faction pawn (a raiding column of the same race) answers its lord, not the hive
            }

            if (RM_ReactionSuppression.IsSuppressed(evt.Map, pawn.Position))
            {
                return;
            }

            if (evt.Spend(budgetCost) < budgetCost)
            {
                return; // the shared budget is spent — this one stays where it is
            }

            Announce(evt);

            if (!telegraphText.NullOrEmpty())
            {
                MoteMaker.ThrowText(pawn.DrawPos, evt.Map, telegraphText, telegraphColor);
            }

            Pawn target = evt.Instigator;
            bool chase = mentalState != null && target != null && target.Spawned && !target.Dead
                         && target.Map == evt.Map;
            if (chase)
            {
                bool started = pawn.mindState.mentalStateHandler.TryStartMentalState(
                    mentalState,
                    reason: null,
                    forced: true,
                    forceWake: true,
                    causedByMood: false,
                    otherPawn: target);

                if (started && pawn.MentalState is RM_MentalState_ScopedAggression state)
                {
                    state.anchorCell = evt.OriginCell;
                    state.disengageRadius = disengageRadius;
                }
                return;
            }

            Converge(evt, pawn);
        }

        private void Announce(RM_ReactionEvent evt)
        {
            if (evt.Announced)
            {
                return;
            }
            evt.Announced = true;

            TargetInfo at = new TargetInfo(evt.OriginCell, evt.Map);
            alarmSound?.PlayOneShot(SoundInfo.InMap(at));
            if (!alarmMessage.NullOrEmpty())
            {
                Messages.Message(alarmMessage, at, MessageTypeDefOf.ThreatBig);
            }
        }

        private void Converge(RM_ReactionEvent evt, Pawn pawn)
        {
            if (!CellFinder.TryFindRandomCellNear(evt.OriginCell, evt.Map, Mathf.Max(1, convergeRadius),
                    c => c.Standable(evt.Map) && pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly),
                    out IntVec3 cell))
            {
                return;
            }

            if (!pawn.Awake())
            {
                RestUtility.WakeUp(pawn);
            }

            Job job = JobMaker.MakeJob(JobDefOf.Goto, cell);
            job.locomotionUrgency = LocomotionUrgency.Sprint;
            pawn.jobs.StartJob(job, JobCondition.InterruptForced);
        }
    }
}
