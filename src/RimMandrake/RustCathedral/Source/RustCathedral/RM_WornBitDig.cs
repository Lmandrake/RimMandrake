using System.Collections.Generic;
using System.Linq;
using RimMandrake.RustCathedral.Hum;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.RustCathedral
{
    public class RM_Area_BorehulkDig : Area
    {
        public override string Label => "Borehulk dig";

        public override Color Color => new Color(0.85f, 0.45f, 0.15f);

        public override int ListPriority => 8900;

        public RM_Area_BorehulkDig()
        {
        }

        public RM_Area_BorehulkDig(AreaManager manager) : base(manager)
        {
        }

        public override string GetUniqueLoadID()
        {
            return "Area_" + ID + "_RM_BorehulkDig";
        }
    }

    public abstract class RM_Designator_BorehulkDig : Designator_Cells
    {
        protected abstract bool Value { get; }

        public override bool DragDrawMeasurements => true;

        public override DrawStyleCategoryDef DrawStyleCategory => DrawStyleCategoryDefOf.Areas;

        protected RM_Designator_BorehulkDig()
        {
            soundDragSustain = SoundDefOf.Designate_DragAreaAdd;
            soundDragChanged = SoundDefOf.Designate_DragZone_Changed;
            soundSucceeded = SoundDefOf.Designate_ZoneAdd;
            useMouseIcon = true;
        }

        public override AcceptanceReport CanDesignateCell(IntVec3 c)
        {
            return c.InBounds(Map) && !c.Fogged(Map) && RM_WornBit.DigArea(Map)[c] != Value;
        }

        public override void DesignateSingleCell(IntVec3 c)
        {
            RM_WornBit.DigArea(Map)[c] = Value;
        }

        public override void SelectedUpdate()
        {
            GenUI.RenderMouseoverBracket();
            RM_WornBit.DigArea(Map)?.MarkForDraw();
        }
    }

    public class RM_Designator_BorehulkDigExpand : RM_Designator_BorehulkDig
    {
        protected override bool Value => true;

        public RM_Designator_BorehulkDigExpand()
        {
            defaultLabel = "Expand dig area";
            icon = ContentFinder<Texture2D>.Get("UI/Designators/Mine");
        }
    }

    public class RM_Designator_BorehulkDigClear : RM_Designator_BorehulkDig
    {
        protected override bool Value => false;

        public RM_Designator_BorehulkDigClear()
        {
            defaultLabel = "Clear dig area";
            icon = ContentFinder<Texture2D>.Get("UI/Designators/Cancel");
        }
    }

    public static class RM_DigFinder
    {
        private const int MaxTries = 40;
        private const float FreeBoreRadius = 25f;

        public static Thing DiggableAt(IntVec3 c, Map map)
        {
            List<Thing> list = c.GetThingList(map);
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i] is Mineable || RM_WornBit.IsSacred(list[i]))
                {
                    return list[i];
                }
            }
            return null;
        }

        public static int SacredCellsInArea(Map map)
        {
            int n = 0;
            foreach (IntVec3 c in RM_WornBit.DigArea(map).ActiveCells)
            {
                if (RM_WornBit.IsSacred(DiggableAt(c, map)))
                {
                    n++;
                }
            }
            return n;
        }

        /// <summary>The cell comes out: the normal yield, or for a sacred cell the player's sacrilege, recorded on the comp.</summary>
        public static void MineOne(Pawn hulk, Thing t)
        {
            RM_CompBorehulkDrill comp = hulk.TryGetComp<RM_CompBorehulkDrill>();
            Map map = hulk.Map;
            comp.cellsMined++;
            comp.lastSelfBoreTick = Find.TickManager.TicksGame;
            if (RM_WornBit.IsSacred(t))
            {
                comp.sacredCellsMined++;
                RM_MapComponent_BiomeAttitude.AffectStanding(map, -RM_RustCathedralSettings.wornBitSacrilegeStanding);
                Log.Message("[" + RM_WornBit.CampaignTag + "] sacrilege: a sacred cell mined at " + t.Position);
                t.Destroy(DestroyMode.KillFinalize);
            }
            else if (t is Mineable m)
            {
                m.DestroyMined(hulk.Faction == Faction.OfPlayer ? hulk : null);
            }
            else
            {
                t.Destroy(DestroyMode.KillFinalize);
            }
        }

        private static Thing Closest(Pawn hulk, IEnumerable<Thing> things)
        {
            foreach (Thing t in things.OrderBy(t => t.Position.DistanceToSquared(hulk.Position)).Take(MaxTries))
            {
                if (hulk.CanReach(t, PathEndMode.Touch, Danger.Deadly))
                {
                    return t;
                }
            }
            return null;
        }

        public static Thing KeptTarget(Pawn hulk)
        {
            Map map = hulk.Map;
            var things = new List<Thing>();
            foreach (IntVec3 c in RM_WornBit.DigArea(map).ActiveCells)
            {
                Thing t = DiggableAt(c, map);
                if (t != null)
                {
                    things.Add(t);
                }
            }
            return Closest(hulk, things);
        }

        /// <summary>Free: plain deck plate only, near where it stands.</summary>
        public static Thing SelfBoreTarget(Pawn hulk)
        {
            return Closest(hulk, hulk.Map.listerThings.ThingsOfDef(RM_WornBitDefOf.RM_CathedralDeckPlate)
                .Where(t => t.Position.InHorDistOf(hulk.Position, FreeBoreRadius)));
        }

        /// <summary>A favour: the colony's own Mine designations, the "dig job" it came to help with.</summary>
        public static Thing FavourTarget(Pawn hulk)
        {
            Map map = hulk.Map;
            var things = new List<Thing>();
            foreach (Designation d in map.designationManager.SpawnedDesignationsOfDef(DesignationDefOf.Mine))
            {
                Thing t = DiggableAt(d.target.Cell, map);
                if (t != null && !RM_WornBit.IsSacred(t))
                {
                    things.Add(t);
                }
            }
            return Closest(hulk, things);
        }
    }

    /// <summary>In RM_ThinkTree_Borehulk after the freeze: a Restored hulk's own work. Worn and Unbitted hulks give no job here.</summary>
    public class RM_JobGiver_BorehulkWork : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            RM_CompBorehulkDrill comp = pawn.TryGetComp<RM_CompBorehulkDrill>();
            if (comp == null || comp.State != RM_BorehulkDrillState.Restored || !RM_RustCathedralSettings.wornBitEnabled)
            {
                return null;
            }
            Thing target = null;
            if (comp.Kept)
            {
                if (comp.MayDigKept)
                {
                    target = RM_DigFinder.KeptTarget(pawn);
                }
            }
            else if (comp.FreedWild)
            {
                if (RM_WornBitGame.Instance?.FavourAt(pawn.Map) == true)
                {
                    target = RM_DigFinder.FavourTarget(pawn);
                }
                else if (RM_RustCathedralSettings.wornBitFreeBoreEnabled
                    && RM_WornBitKernel.SelfBoreDue(Find.TickManager.TicksGame, comp.lastSelfBoreTick, Mathf.RoundToInt(RM_RustCathedralSettings.wornBitFreeBoreHours * GenDate.TicksPerHour)))
                {
                    target = RM_DigFinder.SelfBoreTarget(pawn);
                }
            }
            return target == null ? null : JobMaker.MakeJob(RM_WornBitDefOf.RM_Job_BorehulkDig, target);
        }
    }

    public class RM_JobDriver_BorehulkDig : JobDriver
    {
        private float dealt;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return true;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref dealt, "dealt", 0f);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil dig = ToilMaker.MakeToil("RM_BorehulkDig");
            dig.defaultCompleteMode = ToilCompleteMode.Never;
            dig.handlingFacing = true;
            dig.tickAction = delegate
            {
                Thing t = job.targetA.Thing;
                pawn.rotationTracker.FaceTarget(t);
                dealt += RM_WornBitKernel.ColonistDigPerTick * RM_RustCathedralSettings.wornBitDigSpeed;
                if (pawn.IsHashIntervalTick(30))
                {
                    FleckMaker.ThrowMicroSparks(t.DrawPos, pawn.Map);
                }
                if (dealt >= t.HitPoints)
                {
                    RM_DigFinder.MineOne(pawn, t);
                    EndJobWith(JobCondition.Succeeded);
                }
            };
            yield return dig;
        }
    }
}
