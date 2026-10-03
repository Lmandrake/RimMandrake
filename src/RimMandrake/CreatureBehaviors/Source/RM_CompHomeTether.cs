using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    // REACTION_MECHANISM_GENERALISE_1 step 3 support (FEVERWOOD_ANT_HIVE_DUNGEON_1).
    // A reacting hive's residents must be AT HOME when the player arrives:
    // before this, hive ants were spawned already Manhunter (nothing to
    // notice — they came looking), and a calm wild animal drifts across the
    // whole map on vanilla wander. This keeps a calm pawn near a home cell:
    // every `checkIntervalTicks`, if it is idle-wandering farther than
    // `tetherRadius` from home, it walks back to a cell near home.
    //
    // It never interrupts a mental state (a rally/hunt goes wherever it
    // goes, and ScopedAggression's own disengage ends it), a downed or
    // sleeping pawn, or a non-wander job (eating, fleeing, fighting). Home is
    // the spawn cell unless a generator calls SetHome. Content-blind.
    //
    //   <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_HomeTether">
    //     <tetherRadius>8</tetherRadius>
    //   </li>
    public class RM_CompProperties_HomeTether : CompProperties
    {
        public float tetherRadius = 8f;

        public int checkIntervalTicks = 250;

        public RM_CompProperties_HomeTether()
        {
            compClass = typeof(RM_CompHomeTether);
        }
    }

    public class RM_CompHomeTether : ThingComp
    {
        private IntVec3 home = IntVec3.Invalid;

        public RM_CompProperties_HomeTether Props => (RM_CompProperties_HomeTether)props;

        public IntVec3 Home => home;

        public void SetHome(IntVec3 cell)
        {
            home = cell;
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!home.IsValid)
            {
                home = parent.Position;
            }
        }

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);
            if (!RM_CreatureBehaviorsSettings.homeTetherEnabled || !home.IsValid)
            {
                return;
            }

            if (!parent.Spawned || !parent.IsHashIntervalTick(Mathf.Max(1, Props.checkIntervalTicks), delta))
            {
                return;
            }

            Pawn pawn = parent as Pawn;
            if (pawn == null || pawn.Dead || pawn.Downed || pawn.InMentalState || !pawn.Awake()
                || pawn.Faction != null || pawn.jobs == null)
            {
                return; // tamed/recruited pawns are the player's, not the hive's
            }

            if ((pawn.Position - home).LengthHorizontalSquared <= Props.tetherRadius * Props.tetherRadius)
            {
                return;
            }

            Job cur = pawn.CurJob;
            if (cur != null && cur.def != JobDefOf.Wait_Wander && cur.def != JobDefOf.GotoWander
                && cur.def != JobDefOf.Wait)
            {
                return; // busy with something real — eating, fleeing, fighting
            }

            if (!CellFinder.TryFindRandomCellNear(home, pawn.Map, Mathf.Max(1, Mathf.FloorToInt(Props.tetherRadius / 2f)),
                    c => c.Standable(pawn.Map) && pawn.CanReach(c, PathEndMode.OnCell, Danger.Some),
                    out IntVec3 cell))
            {
                return;
            }

            pawn.jobs.StartJob(JobMaker.MakeJob(JobDefOf.Goto, cell), JobCondition.InterruptForced);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref home, "rmTetherHome", IntVec3.Invalid);
        }
    }
}
