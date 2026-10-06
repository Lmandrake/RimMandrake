using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Watchers
{
    // WATCHER_CREATURES_MOD_1, design §9 step 9 (owner ruling Q4, 2026-10-03: "hunting is
    // flush-only (dimple untargetable, a pawn sent makes it bolt)"). A hidden watcher is hidden from
    // the player (HediffComp_Invisibility, visibleToPlayer false), so it cannot be selected or
    // designated; its sign can. The Flush order marks the sign, a hunter walks to it, the watcher
    // bolts (RM_WatcherUtility.Flush) and, if the setting is on, is marked for hunting while it runs.
    // Same shapes as vanilla Designator_Hunt and WorkGiver_HunterHunt (RimSage, decompiled 1.6).

    public class RM_Designator_Flush : Designator
    {
        protected override DesignationDef Designation => RM_WatchersDefOf.RM_WatcherFlushMark;

        public override DrawStyleCategoryDef DrawStyleCategory => DrawStyleCategoryDefOf.FilledRectangle;

        public RM_Designator_Flush()
        {
            defaultLabel = "RM_Watchers_DesignatorFlush".Translate();
            defaultDesc = "RM_Watchers_DesignatorFlushDesc".Translate();
            icon = ContentFinder<Texture2D>.Get("UI/Designators/Hunt");
            soundDragSustain = SoundDefOf.Designate_DragStandard;
            soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
            useMouseIcon = true;
            soundSucceeded = SoundDefOf.Designate_Hunt;
        }

        public override AcceptanceReport CanDesignateCell(IntVec3 c)
        {
            if (!c.InBounds(Map) || c.Fogged(Map))
            {
                return false;
            }
            foreach (Thing t in c.GetThingList(Map))
            {
                if (CanDesignateThing(t).Accepted)
                {
                    return true;
                }
            }
            return "RM_Watchers_MustDesignateSign".Translate();
        }

        public override void DesignateSingleCell(IntVec3 c)
        {
            List<Thing> things = c.GetThingList(Map);
            for (int i = things.Count - 1; i >= 0; i--)
            {
                if (CanDesignateThing(things[i]).Accepted)
                {
                    DesignateThing(things[i]);
                }
            }
        }

        public override AcceptanceReport CanDesignateThing(Thing t)
        {
            return t is RM_WatcherSign s && s.owner != null && !s.owner.Dead
                && Map.designationManager.DesignationOn(t, Designation) == null;
        }

        public override void DesignateThing(Thing t)
        {
            Map.designationManager.AddDesignation(new Designation(t, Designation));
        }
    }

    public class RM_WorkGiver_Flush : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override Danger MaxPathDanger(Pawn pawn)
        {
            return Danger.Deadly;
        }

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            foreach (Designation d in pawn.Map.designationManager.SpawnedDesignationsOfDef(RM_WatchersDefOf.RM_WatcherFlushMark))
            {
                yield return d.target.Thing;
            }
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !pawn.Map.designationManager.AnySpawnedDesignationOfDef(RM_WatchersDefOf.RM_WatcherFlushMark);
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return t is RM_WatcherSign s && s.owner != null && !s.owner.Dead
                && pawn.Map.designationManager.DesignationOn(t, RM_WatchersDefOf.RM_WatcherFlushMark) != null
                && pawn.CanReserve(t, 1, -1, null, forced);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return JobMaker.MakeJob(RM_WatchersDefOf.RM_WatcherFlush, t);
        }
    }

    public class RM_JobDriver_Flush : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Do(() =>
            {
                if (TargetThingA is RM_WatcherSign s)
                {
                    Pawn watcher = s.owner;
                    s.Map?.designationManager.TryRemoveDesignationOn(s, RM_WatchersDefOf.RM_WatcherFlushMark);
                    RM_WatcherUtility.Flush(watcher, pawn);
                }
            });
        }
    }
}
