using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Patches
{
    // RIMMANDRAKE_ADD_LIGHT_ANYTHING_FLAMMABLE_ORDER_TO_ALL_COLONISTS: right-click a flammable thing with a colonist selected ->
    // "Set fire to <thing>". The colonist walks to touch range, works a moment, and starts a fire on the thing's square
    // nearest them. Who and what: LightOrderRule (tested offline by Scenario/LightOrder); this file reads its facts from the
    // game and does the work. FlowWorks keeps its own "Toss a flame here" for canal liquid and spills (owner: "FlowWorks can
    // have its own too in case it isn't present"); where FlowWorks offers that on the clicked square, this line stays away.
    [DefOf]
    public static class RM_PatchesJobDefOf
    {
        public static JobDef RM_LightFire;

        static RM_PatchesJobDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_PatchesJobDefOf));
        }
    }

    public static class LightOrder
    {
        // FlowWorks' RM_TossFlame.AimTicks: the same short moment before the flame, one second at speed 1.
        public const int WorkTicks = 60;
        // Vanilla Verb_Ignite's fire size (and FlowWorks' toss): a small starting fire that grows by itself.
        public const float FireSize = 0.3f;

        public static string Status => !RM_PatchesSettings.lightOrderEnabled
            ? "Off: no colonist has the order."
            : "On: right-click a flammable thing with one colonist selected. Plants " + (RM_PatchesSettings.lightOrderPlants ? "included." : "left out.")
              + (FlowWorksBound ? " FlowWorks found: its toss line keeps its own squares." : "");

        public static LightFacts Facts(Pawn pawn, Thing thing, IntVec3 clickedCell)
        {
            bool isPawn = thing is Pawn;
            return new LightFacts
            {
                OrderOn = RM_PatchesSettings.lightOrderEnabled,
                PlantsOn = RM_PatchesSettings.lightOrderPlants,
                PawnControllable = pawn.IsColonistPlayerControlled,
                PawnDowned = pawn.Downed,
                PawnHasHands = pawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation),
                TargetIsPawn = thing is Pawn,
                TargetIsPlant = thing is Plant,
                TargetIsFire = thing is Fire,
                // the cheap facts first: the menu is built on every right-click
                FlammableNow = thing.FlammableNow,
                Burning = thing.IsBurning(),
                CellTakesFire = !isPawn && FireCell(thing, pawn.Position).IsValid,
                Reachable = !isPawn && pawn.CanReach(thing, PathEndMode.Touch, Danger.Deadly),
                OtherModCellLine = FlowWorksOffersLine(thing.Map, clickedCell),
            };
        }

        // The thing's square nearest `from` where vanilla would start a fire (no fire yet, no fire foam, not the inside of
        // an impassable building), or Invalid.
        public static IntVec3 FireCell(Thing thing, IntVec3 from)
        {
            Map map = thing.Map;
            if (map == null)
                return IntVec3.Invalid;
            IntVec3 best = IntVec3.Invalid;
            int bestDist = int.MaxValue;
            foreach (IntVec3 c in thing.OccupiedRect())
            {
                if (!c.InBounds(map) || FireUtility.ChanceToStartFireIn(c, map) <= 0f)
                    continue;
                int d = (c - from).LengthHorizontalSquared;
                if (d < bestDist)
                {
                    best = c;
                    bestDist = d;
                }
            }
            return best;
        }

        public static bool Order(Pawn pawn, Thing thing)
        {
            Job job = JobMaker.MakeJob(RM_PatchesJobDefOf.RM_LightFire, thing);
            job.playerForced = true;
            return pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
        }

        // ---- FlowWorks, bound by name (it may be absent; the CaiFogOff pattern) ----
        private static bool bound;
        private static MethodInfo canLight;
        private static FieldInfo tossOn;

        private static bool FlowWorksBound
        {
            get
            {
                if (!bound)
                {
                    bound = true;
                    Type toss = AccessTools.TypeByName("RimMandrake.FlowWorks.RM_TossFlame");
                    Type settings = AccessTools.TypeByName("RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings");
                    canLight = toss == null ? null : AccessTools.Method(toss, "CanLight", new[] { typeof(Map), typeof(IntVec3) });
                    tossOn = settings == null ? null : AccessTools.Field(settings, "tossFlameOrderEnabled");
                }
                return canLight != null && tossOn != null;
            }
        }

        // True when FlowWorks' "Toss a flame here" shows on this square: its switch is on and something there will catch
        // by its own test. Its provider asks exactly these two, so the two lines never sit on one right-click.
        public static bool FlowWorksOffersLine(Map map, IntVec3 c)
        {
            if (map == null || !FlowWorksBound)
                return false;
            try
            {
                return (bool)tossOn.GetValue(null) && (bool)canLight.Invoke(null, new object[] { map, c });
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake Patches] the FlowWorks toss-line test failed (" + e.GetType().Name + "); the light order no longer steps aside for it.", 0x4c49474e);
                canLight = null;
                return false;
            }
        }
    }

    public class FloatMenuOptionProvider_LightFire : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;
        protected override bool Undrafted => true;
        protected override bool Multiselect => false;
        // false on purpose: a colonist without hands gets the greyed line with its reason (LightOrderRule), not silence.
        protected override bool RequiresManipulation => false;

        protected override bool AppliesInt(FloatMenuContext context) => RM_PatchesSettings.lightOrderEnabled;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            Pawn pawn = context.FirstSelectedPawn;
            if (pawn == null || clickedThing == null || !clickedThing.Spawned)
                return null;
            LightVerdict v = LightOrderRule.Decide(LightOrder.Facts(pawn, clickedThing, context.ClickedCell), out string reason);
            string label = LightOrderRule.Label(clickedThing.LabelShort, v, reason);
            if (label == null)
                return null;
            if (v == LightVerdict.Disabled)
                return new FloatMenuOption(label, null);
            Thing target = clickedThing;
            return new FloatMenuOption(label, () => LightOrder.Order(pawn, target), MenuOptionPriority.Default, null, target);
        }
    }

    public class JobDriver_LightFire : JobDriver
    {
        private const TargetIndex A = TargetIndex.A;

        public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(A);
            this.FailOn(() => !RM_PatchesSettings.lightOrderEnabled);
            yield return Toils_Goto.GotoThing(A, PathEndMode.Touch).FailOnBurningImmobile(A);
            yield return Toils_General.Wait(LightOrder.WorkTicks, A)
                .FailOnCannotTouch(A, PathEndMode.Touch)
                .FailOnBurningImmobile(A)
                .WithProgressBarToilDelay(A);
            Toil light = ToilMaker.MakeToil("LightFire");
            light.initAction = () =>
            {
                Thing t = job.GetTarget(A).Thing;
                IntVec3 c = LightOrder.FireCell(t, pawn.Position);
                if (c.IsValid)
                {
                    FleckMaker.ThrowMicroSparks(c.ToVector3Shifted(), Map);
                    if (FireUtility.TryStartFireIn(c, Map, LightOrder.FireSize, pawn))
                        return;
                }
                Messages.Message(pawn.LabelShort + " could not set fire to " + t.LabelShort + ": nothing there caught.",
                    new LookTargets(t), MessageTypeDefOf.RejectInput, false);
            };
            light.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return light;
        }
    }
}
