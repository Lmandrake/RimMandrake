using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // REACTION_MECHANISM_GENERALISE_1 step 1's actual deliverable: the SPAWN
    // response GREENTIDE_WASP_SWARM_1 needs. Content-blind like every other
    // comp in this assembly — `pawnKind` is set from XML by a content pack
    // (RM_SkerrelGall in mandrake.rm.greentide), this assembly hardcodes no
    // species.
    //
    // Two independent bounds, per the item's own words ("how many wasps exist
    // per hive and per map at once"):
    //   - the event's own shared RemainingBudget (how much THIS trigger grants);
    //   - mapPopulationCap (how many of `pawnKind` may be alive on the map at
    //     once, counted fresh every trigger rather than tracked — cheap at the
    //     rate a gall can trigger, gated by the same cooldown as everything
    //     else in this family).
    // The smaller of the two wins; a map already at its cap grants nothing,
    // even with a full event budget still sitting unspent.
    //
    // Spawned pawns start hostile via RM_MentalState_ScopedAggression (not
    // plain vanilla Manhunter) so the swarm is aimed at evt.Instigator alone —
    // never a map-wide manhunter flip — and disengages once its target is far
    // enough from the disturbance. That is what makes the swarm "survivable
    // by withdrawing" (GREENTIDE_WASP_SWARM_1's own requirement) rather than a
    // death sentence, without needing the general reaction-suppression
    // mechanism a later step builds.
    public class RM_ReactionResponseRule_SpawnPawns : RM_ReactionResponseRule
    {
        /// <summary>The kind to spawn. Left for XML to fill — this class names no species.</summary>
        public PawnKindDef pawnKind;

        /// <summary>Cells around the origin a spawned pawn may land on. INVENTED: 3 — "boils out of the gall", not "appears across the clearing".</summary>
        public float spawnRadius = 3f;

        /// <summary>
        /// Total live pawns of `pawnKind` this map tolerates from this
        /// response at once. Distinct from the event's own shared budget
        /// (that is the per-TRIGGER grant); this is the standing population
        /// ceiling. INVENTED: 24.
        /// </summary>
        public int mapPopulationCap = 24;

        /// <summary>
        /// Mental state a spawned pawn starts in. Null spawns it as ordinary
        /// passive wildlife — a content author sets this (RM_SwarmAggression)
        /// to get the "swarms and stings, then loses interest" behaviour at
        /// all. If the state's stateClass derives from
        /// RM_MentalState_ScopedAggression, this response also configures its
        /// anchor and disengage radius; any other MentalStateDef is started
        /// exactly as given, unconfigured.
        /// </summary>
        public MentalStateDef startMentalState;

        /// <summary>How far the target must get from the disturbance before a spawned pawn in startMentalState gives up. Only meaningful if startMentalState's stateClass derives from RM_MentalState_ScopedAggression.</summary>
        public float disengageRadius = 20f;

        public override void Respond(RM_ReactionEvent evt, Thing source)
        {
            if (pawnKind == null || evt.Map == null)
            {
                return;
            }

            int currentAlive = CountAlive(evt.Map, pawnKind);
            int mapRoom = mapPopulationCap - currentAlive;
            if (mapRoom <= 0)
            {
                return; // the map is already at its ceiling — this trigger spawns nothing
            }

            int wantToSpawn = Mathf.Min(mapRoom, evt.RemainingBudget);
            int granted = evt.Spend(wantToSpawn);

            for (int i = 0; i < granted; i++)
            {
                SpawnOne(evt);
            }
        }

        private void SpawnOne(RM_ReactionEvent evt)
        {
            if (!CellFinder.TryFindRandomCellNear(
                    evt.OriginCell,
                    evt.Map,
                    Mathf.Max(1, Mathf.CeilToInt(spawnRadius)),
                    c => c.InBounds(evt.Map) && c.Standable(evt.Map),
                    out IntVec3 cell))
            {
                cell = evt.OriginCell;
            }

            Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
                pawnKind,
                faction: null,
                context: PawnGenerationContext.NonPlayer,
                forceGenerateNewPawn: true,
                allowDowned: false,
                canGeneratePawnRelations: false,
                allowFood: false,
                allowAddictions: false));

            GenSpawn.Spawn(pawn, cell, evt.Map);

            if (startMentalState == null || pawn.mindState?.mentalStateHandler == null)
            {
                return;
            }

            bool started = pawn.mindState.mentalStateHandler.TryStartMentalState(
                startMentalState,
                reason: null,
                forced: true,
                forceWake: true,
                causedByMood: false,
                otherPawn: evt.Instigator);

            if (started && pawn.MentalState is RM_MentalState_ScopedAggression state)
            {
                state.anchorCell = evt.OriginCell;
                state.disengageRadius = disengageRadius;
            }
        }

        private static int CountAlive(Map map, PawnKindDef kind)
        {
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            int count = 0;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p != null && !p.Dead && p.kindDef == kind)
                {
                    count++;
                }
            }
            return count;
        }
    }
}
