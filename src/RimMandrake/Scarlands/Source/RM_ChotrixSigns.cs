using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Scarlands
{
    // WARSCAR_CHOTRIX_SIGNS_1. The chotrix's readable signs on the shared track grid (FOOTPRINT_TRACK_GRID_1,
    // CreatureBehaviors):
    //  * Prints: the grid records invisible walkers itself; RM_Filth_SettledFilm's extension gives RM_Chotrix
    //    its own print class (a raceOverride, XML only).
    //  * Dragged-kill marks: after a kill it drags the corpse off to cover (JobDriver_ChotrixDragKill). Every film
    //    cell it crosses while dragging takes a drag furrow in place of its print (RM_ChotrixTrackLink.DragMark).
    //  * The tetchik silence ring is the Geiger choir's (RM_GeigerChoir.Silenced reads CompChotrix.All/SilenceRadius).
    // Reaches the grid by reflection, like RM_TrackGridLink in RM_Settling.cs: no assembly reference; absent = no marks.
    public static class RM_ChotrixTrackLink
    {
        private static bool resolved;
        private static MethodInfo mFor, mSurfaceAt, mRecordPrint;
        private static Type extType;
        private static FieldInfo fHuman, fAnimal, fLarge, fDrag, fSize;
        // One drag-only surface per film surface it was built from (defs are immutable, so never stale).
        private static readonly Dictionary<object, object> dragSurfaces = new Dictionary<object, object>();

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            Type grid = GenTypes.GetTypeInAnyAssembly("RimMandrake.CreatureBehaviors.RM_MapComponent_TrackGrid");
            Type patches = GenTypes.GetTypeInAnyAssembly("RimMandrake.CreatureBehaviors.RM_TrackGridPatches");
            extType = GenTypes.GetTypeInAnyAssembly("RimMandrake.CreatureBehaviors.RM_TrackSurfaceExtension");
            if (grid == null || patches == null || extType == null) { extType = null; return; }
            mFor = grid.GetMethod("For", BindingFlags.Public | BindingFlags.Static);
            mRecordPrint = grid.GetMethod("RecordPrint", BindingFlags.Public | BindingFlags.Instance, null,
                new[] { typeof(IntVec3), typeof(Pawn), extType }, null);
            mSurfaceAt = patches.GetMethod("SurfaceAt", BindingFlags.Public | BindingFlags.Static);
            fHuman = extType.GetField("humanTexPath");
            fAnimal = extType.GetField("animalTexPath");
            fLarge = extType.GetField("largeTexPath");
            fDrag = extType.GetField("dragTexPath");
            fSize = extType.GetField("printSize");
            if (mFor == null || mRecordPrint == null || mSurfaceAt == null || fHuman == null || fAnimal == null
                || fLarge == null || fDrag == null || fSize == null)
            {
                extType = null;
                Log.Warning("[RM_Warscar] track grid print API not found; the chotrix will leave no drag marks.");
            }
        }

        public static bool Available { get { Resolve(); return extType != null; } }

        /// <summary>
        /// Lay a drag furrow on cell c if it takes prints (the settled film, on the Warscar). The grid's own
        /// cell-entry writer has already laid the dragger's print there; this overwrites it.
        /// </summary>
        public static bool DragMark(Map map, IntVec3 c, Pawn dragger)
        {
            Resolve();
            if (extType == null || map == null || dragger == null || !c.InBounds(map)) return false;
            try
            {
                object surface = mSurfaceAt.Invoke(null, new object[] { c, map });
                if (surface == null) return false;
                object grid = mFor.Invoke(null, new object[] { map });
                if (grid == null) return false;
                object drag = DragSurfaceFor(surface);
                return (bool)mRecordPrint.Invoke(grid, new object[] { c, dragger, drag });
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM_Warscar] chotrix drag mark threw: " + e, 0x5C4D7A);
                return false;
            }
        }

        // Every print class of the drag surface is the film's drag sprite, a little wider than a print.
        private static object DragSurfaceFor(object surface)
        {
            if (dragSurfaces.TryGetValue(surface, out object d)) return d;
            d = Activator.CreateInstance(extType);
            string tex = (string)fDrag.GetValue(surface);
            fHuman.SetValue(d, tex);
            fAnimal.SetValue(d, tex);
            fLarge.SetValue(d, tex);
            fDrag.SetValue(d, tex);
            fSize.SetValue(d, (float)fSize.GetValue(surface) * 1.3f);
            dragSurfaces[surface] = d;
            return d;
        }
    }

    // Right after a kill, drag the corpse off to cover before eating. One drag per kill.
    public class JobGiver_ChotrixDragKill : ThinkNode_JobGiver
    {
        public const int FreshKillTicks = 1200;
        public const float ReachRadius = 6f;

        protected override Job TryGiveJob(Pawn pawn)
        {
            CompChotrix c = pawn.TryGetComp<CompChotrix>();
            if (c == null || !RM_WarscarSettings.chotrixEnabled || !RM_WarscarSettings.chotrixDragEnabled) return null;
            if (pawn.Downed || pawn.InMentalState || c.Fleeing || pawn.carryTracker == null) return null;
            Pawn victim = c.lastVictim;
            if (victim == null || c.victimDragged || !victim.Dead) return null;
            if (Find.TickManager.TicksGame - c.lastStrikeTick > FreshKillTicks) { c.lastVictim = null; return null; }
            Corpse corpse = victim.Corpse;
            if (corpse == null || !corpse.Spawned || corpse.Map != pawn.Map) return null;
            // It drags what it can move: nothing much heavier than itself.
            if (victim.BodySize > pawn.BodySize * 1.25f) { c.victimDragged = true; return null; }
            if ((corpse.Position - pawn.Position).LengthHorizontalSquared > ReachRadius * ReachRadius) return null;
            c.victimDragged = true; // one attempt per kill, whatever happens to the job
            if (!pawn.CanReserveAndReach(corpse, PathEndMode.ClosestTouch, Danger.Some)) return null;
            if (!TryFindCover(pawn, corpse.Position, out IntVec3 dest)) return null;
            Job j = JobMaker.MakeJob(RM_ChotrixDefOf.RM_ChotrixDragKill, corpse, dest);
            j.count = 1;
            j.locomotionUrgency = LocomotionUrgency.Walk;
            j.expiryInterval = 2500;
            return j;
        }

        // 8-16 cells from the kill, standable, reachable, out of the home area, and as far from people as a few
        // samples find.
        public static bool TryFindCover(Pawn pawn, IntVec3 from, out IntVec3 dest)
        {
            Map map = pawn.Map;
            dest = IntVec3.Invalid;
            float bestScore = -1f;
            for (int i = 0; i < 12; i++)
            {
                if (!CellFinder.TryFindRandomCellNear(from, map, 16, c =>
                        c.Standable(map) && (c - from).LengthHorizontalSquared >= 64
                        && !map.areaManager.Home[c] && pawn.CanReach(c, PathEndMode.OnCell, Danger.Some),
                        out IntVec3 cell, 30))
                    continue;
                float score = NearestPersonDistSq(map, cell, pawn) + (cell.Roofed(map) ? 100f : 0f);
                if (score > bestScore) { bestScore = score; dest = cell; }
            }
            return dest.IsValid;
        }

        private static float NearestPersonDistSq(Map map, IntVec3 cell, Pawn self)
        {
            float best = 10000f;
            IReadOnlyList<Pawn> all = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn o = all[i];
                if (o == self || o.Dead || !o.RaceProps.Humanlike) continue;
                float d = (o.Position - cell).LengthHorizontalSquared;
                if (d < best) best = d;
            }
            return best;
        }
    }

    // A: the corpse. B: the cover cell. Carry it there, furrowing the film on every cell it crosses, then drop it.
    public class JobDriver_ChotrixDragKill : JobDriver
    {
        private IntVec3 lastMarked = IntVec3.Invalid;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            // However the job ends, never leave the kill held.
            AddFinishAction(delegate(JobCondition _)
            {
                if (pawn.Spawned && pawn.carryTracker != null && pawn.carryTracker.CarriedThing != null)
                    pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out Thing _);
            });
            // Only until it is picked up: once carried, A is the held (unspawned) corpse.
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch).FailOnDespawnedOrNull(TargetIndex.A);
            yield return Toils_Haul.StartCarryThing(TargetIndex.A);
            Toil drag = Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.OnCell);
            drag.AddPreTickAction(delegate
            {
                IntVec3 here = pawn.Position;
                if (here == lastMarked) return;
                lastMarked = here;
                RM_ChotrixTrackLink.DragMark(pawn.Map, here, pawn);
            });
            drag.AddFailCondition(() => pawn.carryTracker.CarriedThing == null);
            yield return drag;
            Toil drop = ToilMaker.MakeToil("ChotrixDropKill");
            drop.initAction = delegate
            {
                RM_ChotrixTrackLink.DragMark(pawn.Map, pawn.Position, pawn);
                if (pawn.carryTracker.CarriedThing != null)
                    pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out Thing _);
            };
            drop.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return drop;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lastMarked, "lastMarked", IntVec3.Invalid);
        }
    }

    [DefOf]
    public static class RM_ChotrixDefOf
    {
        public static JobDef RM_ChotrixDragKill;
        static RM_ChotrixDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(RM_ChotrixDefOf)); }
    }
}
