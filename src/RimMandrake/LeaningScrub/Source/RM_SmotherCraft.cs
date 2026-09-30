using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_MECHANICS_BUILD_1 part 4 — the smother-craft.
    //
    // A pawn carries a smother-blanket to a venomvine stand and throws it over
    // (right-click order). The stand becomes a banked claim: the comp Scribes
    // the tick the blanket went on and shows a countdown on inspect. When the
    // claim matures the stand is gone and its dead wood lies where it stood.
    //
    // Why maturation is a MapComponent and not the comp's CompTickLong:
    // Plant.TickLong runs the comps (base.TickLong) and THEN its own growth
    // code, which dereferences Map — a comp destroying its plant mid-TickLong
    // would NRE the rest of that call (RimSage, decompiled Plant.TickLong).
    // So the comp only records state and registers itself; the MapComponent
    // (a transient index rebuilt from PostSpawnSetup on load) does the swap.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_Smotherable : CompProperties
    {
        // Dead venomvine yielded by a fully grown stand; scaled by growth.
        public int yieldCount = 40;

        public RM_CompProperties_Smotherable()
        {
            compClass = typeof(RM_CompSmotherable);
        }
    }

    public class RM_CompSmotherable : ThingComp
    {
        private int smotherStartTick = -1;

        public RM_CompProperties_Smotherable Props => (RM_CompProperties_Smotherable)props;

        public bool Smothered => smotherStartTick >= 0;

        public static int ClaimTicks => Mathf.RoundToInt(Mathf.Max(0.1f, RM_LeaningScrubSettings.smotherDays) * GenDate.TicksPerDay);

        public int TicksRemaining => Smothered ? smotherStartTick + ClaimTicks - Find.TickManager.TicksGame : -1;

        public void StartSmother()
        {
            if (Smothered)
            {
                return;
            }
            smotherStartTick = Find.TickManager.TicksGame;
            parent.Map?.GetComponent<RM_MapComponent_SmotherClaims>()?.Register(this);
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (Smothered)
            {
                parent.Map.GetComponent<RM_MapComponent_SmotherClaims>()?.Register(this);
            }
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            map?.GetComponent<RM_MapComponent_SmotherClaims>()?.Deregister(this);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref smotherStartTick, "rmSmotherStartTick", -1);
        }

        public override string CompInspectStringExtra()
        {
            if (!Smothered)
            {
                return null;
            }
            int left = TicksRemaining;
            if (left <= 0)
            {
                return "Smothered: dead through, ready to fall.";
            }
            return "Smothered under a blanket: dead wood in " + left.ToStringTicksToPeriod() + ".";
        }
    }

    public class RM_MapComponent_SmotherClaims : MapComponent
    {
        private const int CheckInterval = 2500;

        private readonly HashSet<RM_CompSmotherable> claims = new HashSet<RM_CompSmotherable>();
        private readonly List<RM_CompSmotherable> tmpDue = new List<RM_CompSmotherable>();

        public RM_MapComponent_SmotherClaims(Map map) : base(map)
        {
        }

        public void Register(RM_CompSmotherable comp)
        {
            claims.Add(comp);
        }

        public void Deregister(RM_CompSmotherable comp)
        {
            claims.Remove(comp);
        }

        public override void MapComponentTick()
        {
            if (claims.Count == 0 || Find.TickManager.TicksGame % CheckInterval != 0)
            {
                return;
            }
            // A claim already on the ground keeps its clock with the feature off;
            // it simply does not mature until the feature is back on.
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.smotherCraftEnabled))
            {
                return;
            }
            tmpDue.Clear();
            foreach (RM_CompSmotherable c in claims)
            {
                if (c.parent.Spawned && c.TicksRemaining <= 0)
                {
                    tmpDue.Add(c);
                }
            }
            for (int i = 0; i < tmpDue.Count; i++)
            {
                Mature(tmpDue[i]);
            }
            tmpDue.Clear();
        }

        private void Mature(RM_CompSmotherable comp)
        {
            Thing plant = comp.parent;
            IntVec3 pos = plant.Position;
            float growth = plant is Plant p ? p.Growth : 1f;
            int count = Mathf.Max(1, Mathf.RoundToInt(comp.Props.yieldCount * Mathf.Max(0.3f, growth)
                * RM_LeaningScrubSettings.smotherYieldFactor));

            plant.Destroy(DestroyMode.Vanish); // PostDeSpawn deregisters

            ThingDef wood = RM_LeaningScrubDefOf.RM_DeadVenomvine;
            while (count > 0)
            {
                Thing stack = ThingMaker.MakeThing(wood);
                stack.stackCount = Mathf.Min(count, wood.stackLimit);
                count -= stack.stackCount;
                GenPlace.TryPlaceThing(stack, pos, map, ThingPlaceMode.Near);
            }
            Messages.Message("A smothered venomvine stand has died back to dead wood.",
                new TargetInfo(pos, map), MessageTypeDefOf.PositiveEvent);
        }
    }

    public class RM_JobDriver_SmotherVenomvine : JobDriver
    {
        private const TargetIndex StandInd = TargetIndex.A;
        private const TargetIndex BlanketInd = TargetIndex.B;
        private const int ThrowTicks = 600;

        private Thing Stand => job.GetTarget(StandInd).Thing;
        private Thing Blanket => job.GetTarget(BlanketInd).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(Stand, job, 1, -1, null, errorOnFailed)
                && pawn.Reserve(Blanket, job, 1, 1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedOrNull(StandInd);
            this.FailOn(() => Stand.TryGetComp<RM_CompSmotherable>()?.Smothered != false);

            yield return Toils_Goto.GotoThing(BlanketInd, PathEndMode.ClosestTouch)
                .FailOnDespawnedNullOrForbidden(BlanketInd)
                .FailOnSomeonePhysicallyInteracting(BlanketInd);
            yield return Toils_Haul.StartCarryThing(BlanketInd);
            yield return Toils_Goto.GotoThing(StandInd, PathEndMode.Touch);

            Toil work = Toils_General.Wait(ThrowTicks, StandInd);
            work.WithProgressBarToilDelay(StandInd);
            work.FailOnCannotTouch(StandInd, PathEndMode.Touch);
            yield return work;

            Toil finish = ToilMaker.MakeToil("SmotherVenomvine");
            finish.defaultCompleteMode = ToilCompleteMode.Instant;
            finish.initAction = delegate
            {
                Thing carried = pawn.carryTracker.CarriedThing;
                RM_CompSmotherable comp = Stand.TryGetComp<RM_CompSmotherable>();
                if (carried == null || carried.def != RM_LeaningScrubDefOf.RM_SmotherBlanket || comp == null)
                {
                    return;
                }
                Thing used = carried.SplitOff(1);
                used.Destroy();
                if (pawn.carryTracker.CarriedThing != null)
                {
                    pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out Thing _);
                }
                comp.StartSmother();
            };
            yield return finish;
        }
    }

    // Right-click a venomvine stand with a colonist selected. FloatMenuMakerMap
    // auto-registers every non-abstract FloatMenuOptionProvider subclass.
    public class RM_FloatMenuOptionProvider_Smother : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;

        protected override bool Undrafted => true;

        protected override bool Multiselect => false;

        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.smotherCraftEnabled) || !(clickedThing is Plant))
            {
                return null;
            }
            RM_CompSmotherable comp = clickedThing.TryGetComp<RM_CompSmotherable>();
            if (comp == null || comp.Smothered)
            {
                return null;
            }
            Pawn actor = context.FirstSelectedPawn;
            if (actor == null || actor.Map != clickedThing.Map)
            {
                return null;
            }

            string label = "Smother " + clickedThing.LabelShort + " with a smother-blanket";
            if (!actor.CanReach(clickedThing, PathEndMode.Touch, Danger.Deadly))
            {
                return new FloatMenuOption(label + ": " + "NoPath".Translate().CapitalizeFirst(), null);
            }
            Thing blanket = GenClosest.ClosestThingReachable(actor.Position, actor.Map,
                ThingRequest.ForDef(RM_LeaningScrubDefOf.RM_SmotherBlanket), PathEndMode.ClosestTouch,
                TraverseParms.For(actor), 9999f,
                t => !t.IsForbidden(actor) && actor.CanReserve(t));
            if (blanket == null)
            {
                return new FloatMenuOption(label + ": no reachable smother-blanket", null);
            }
            if (!actor.CanReserve(clickedThing))
            {
                return new FloatMenuOption(label + ": reserved", null);
            }

            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(label, delegate
            {
                Job job = JobMaker.MakeJob(RM_LeaningScrubDefOf.RM_SmotherVenomvine, clickedThing, blanket);
                job.count = 1;
                actor.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            }), actor, clickedThing);
        }
    }
}
