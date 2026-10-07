using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Wasteland
{
    // ════════════════════════════════════════════════════════════════════
    // WASTELAND_GRIPPER_STEAL_BEHAVIOR_1 — the gripper steals.
    //
    // Owner, Wasteland art-sheet ruling on the Middenbeetle row (2026-09-29):
    // "This beast is capable of stealing. Needs a new name to deconflict
    // Middenshell. How about a Gripper? Always carrying something."
    //
    // One behaviour, four parts, all on RM_Gripper only (the comp is the gate):
    //   1. RM_CompGripperThief — a WILD gripper spawns holding a scrap of junk
    //      in its inventory ("always carrying something"); being hurt makes it
    //      drop its haul (drop-on-death is vanilla: Pawn.Kill ->
    //      DropAndForbidEverything empties the inventory, forbidden).
    //   2. RM_ThinkNode_GripperTheftChance — the MTB gate, read from Mod Settings.
    //   3. RM_JobGiver_GripperSteal — finds a nearby unforbidden, reachable,
    //      light, haulable item worth more than what it is carrying.
    //   4. RM_JobDriver_GripperSteal — go to it, drop the old scrap there, take
    //      the new one into inventory, then scurry off.
    // Tamed or otherwise factioned grippers never steal (the ruling says nothing
    // about tame grippers; they keep whatever they hold, visible and droppable
    // from the Gear tab like any animal inventory).
    // ════════════════════════════════════════════════════════════════════

    public class RM_CompProperties_GripperThief : CompProperties
    {
        /// <summary>How far (cells) a gripper looks for something to steal.</summary>
        public float searchRadius = 20f;

        /// <summary>Most mass (kg) it will lift in one theft; also caps the units taken.</summary>
        public float maxCarryMass = 3f;

        /// <summary>Hard cap on units taken from one stack.</summary>
        public int maxUnitsTaken = 10;

        /// <summary>Chance, per damaging hit, that it lets go of its haul.</summary>
        public float dropOnHarmChance = 0.5f;

        /// <summary>Chance a freshly spawned wild gripper already holds junk.</summary>
        public float startingJunkChance = 1f;

        /// <summary>The junk it may spawn holding; one entry is picked at random.</summary>
        public List<ThingDefCountRangeClass> startingJunk = new List<ThingDefCountRangeClass>();

        public RM_CompProperties_GripperThief()
        {
            compClass = typeof(RM_CompGripperThief);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (parentDef.race == null)
            {
                yield return "RM_CompProperties_GripperThief belongs on a pawn race, not " + parentDef.defName + ".";
            }
            if (searchRadius <= 0f)
            {
                yield return "searchRadius must be > 0.";
            }
            if (maxCarryMass <= 0f)
            {
                yield return "maxCarryMass must be > 0.";
            }
            if (maxUnitsTaken < 1)
            {
                yield return "maxUnitsTaken must be >= 1.";
            }
            if (dropOnHarmChance < 0f || dropOnHarmChance > 1f)
            {
                yield return "dropOnHarmChance must be in [0,1].";
            }
            if (startingJunkChance < 0f || startingJunkChance > 1f)
            {
                yield return "startingJunkChance must be in [0,1].";
            }
            foreach (ThingDefCountRangeClass j in startingJunk)
            {
                if (j.thingDef == null)
                {
                    yield return "startingJunk has a null thingDef.";
                }
                else if (j.thingDef.category != ThingCategory.Item)
                {
                    yield return "startingJunk " + j.thingDef.defName + " is not an item.";
                }
            }
        }
    }

    public class RM_CompGripperThief : ThingComp
    {
        public RM_CompProperties_GripperThief Props => (RM_CompProperties_GripperThief)props;

        private Pawn Gripper => parent as Pawn;

        public static bool TheftActive =>
            RM_WastelandSettings.wastelandEnabled && RM_WastelandSettings.gripperTheftEnabled;

        /// <summary>Total market value of what the gripper holds right now.</summary>
        public float CarriedValue
        {
            get
            {
                Pawn p = Gripper;
                if (p?.inventory == null)
                {
                    return 0f;
                }
                float v = 0f;
                foreach (Thing t in p.inventory.innerContainer)
                {
                    v += t.MarketValue * t.stackCount;
                }
                return v;
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (respawningAfterLoad || !TheftActive || !RM_WastelandSettings.gripperSpawnsCarrying)
            {
                return;
            }
            Pawn p = Gripper;
            if (p == null || p.Faction != null || p.Dead || p.inventory == null
                || p.inventory.innerContainer.Any || Props.startingJunk.NullOrEmpty()
                || !Rand.Chance(Props.startingJunkChance))
            {
                return;
            }
            ThingDefCountRangeClass pick = Props.startingJunk.RandomElement();
            if (pick?.thingDef == null)
            {
                return;
            }
            Thing junk = ThingMaker.MakeThing(pick.thingDef, GenStuff.DefaultStuffFor(pick.thingDef));
            junk.stackCount = Mathf.Clamp(pick.countRange.RandomInRange, 1, pick.thingDef.stackLimit);
            if (!p.inventory.innerContainer.TryAdd(junk))
            {
                junk.Destroy();
            }
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            Pawn p = Gripper;
            if (!TheftActive || p == null || !p.Spawned || p.Dead || totalDamageDealt <= 0f
                || p.inventory == null || !p.inventory.innerContainer.Any)
            {
                return;
            }
            if (Rand.Chance(Props.dropOnHarmChance))
            {
                p.inventory.DropAllNearPawn(p.Position);
            }
        }

        public override string CompInspectStringExtra()
        {
            Pawn p = Gripper;
            if (p?.inventory == null || !p.inventory.innerContainer.Any)
            {
                return null;
            }
            return "Gripping: " + p.inventory.innerContainer[0].LabelCap;
        }
    }

    /// <summary>
    /// MTB gate for the theft subtree. The mean time between attempts comes from
    /// Mod Settings, so the rate is a player-facing number. Same base as vanilla's
    /// ThinkNode_ChancePerHour_Constant (one roll per in-game hour at most).
    /// </summary>
    public class RM_ThinkNode_GripperTheftChance : ThinkNode_ChancePerHour
    {
        protected override float MtbHours(Pawn pawn)
        {
            if (!RM_CompGripperThief.TheftActive)
            {
                return -1f;
            }
            return RM_WastelandSettings.gripperTheftMtbHours;
        }
    }

    public class RM_JobGiver_GripperSteal : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_CompGripperThief.TheftActive || pawn.Faction != null || !pawn.Spawned
                || pawn.Downed || pawn.InMentalState || pawn.inventory == null)
            {
                return null;
            }
            RM_CompGripperThief comp = pawn.GetComp<RM_CompGripperThief>();
            if (comp == null)
            {
                return null;
            }
            RM_CompProperties_GripperThief props = comp.Props;
            float carriedValue = comp.CarriedValue;

            Thing target = GenClosest.ClosestThingReachable(
                pawn.Position, pawn.Map, ThingRequest.ForGroup(ThingRequestGroup.HaulableEver),
                PathEndMode.ClosestTouch, TraverseParms.For(pawn, Danger.Some), props.searchRadius,
                t => UnitsToTake(pawn, t, props) > 0
                     && t.MarketValue * UnitsToTake(pawn, t, props) > carriedValue
                     && pawn.CanReserve(t));
            if (target == null)
            {
                return null;
            }
            Job job = JobMaker.MakeJob(RM_WastelandJobDefOf.RM_GripperSteal, target);
            job.count = UnitsToTake(pawn, target, props);
            job.expiryInterval = 2000;
            job.checkOverrideOnExpire = true;
            job.locomotionUrgency = LocomotionUrgency.Jog;
            return job;
        }

        /// <summary>
        /// How many units of <paramref name="t"/> this gripper would take, or 0 if
        /// it is not a legal target: a spawned, visible, unforbidden, haulable item
        /// (never a corpse, minified building, pawn, or anything burning), with at
        /// least one unit under the mass cap.
        /// </summary>
        public static int UnitsToTake(Pawn pawn, Thing t, RM_CompProperties_GripperThief props)
        {
            bool legal = t != null && t.Spawned && t.def.category == ThingCategory.Item && t.def.EverHaulable
                && !(t is Corpse) && !(t is MinifiedThing) && !(t is Pawn) && !t.IsBurning()
                && !t.IsForbidden(Faction.OfPlayer) && !t.Position.Fogged(t.Map);
            if (!legal)
            {
                return 0;
            }
            return RM_DoseKernel.UnitsToTake(true, t.GetStatValue(StatDefOf.Mass), t.stackCount, props.maxUnitsTaken, props.maxCarryMass);
        }
    }

    public class RM_JobDriver_GripperSteal : JobDriver
    {
        private const float ScurryRadius = 12f; // RCellFinder.RandomWanderDestFor warns above 12

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, job.count, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            // Job-wide: a gripper tamed mid-theft stops. Target checks are scoped to
            // the approach toil only — once the whole stack is in inventory the
            // target is legitimately despawned and must not fail the scurry.
            this.FailOn(() => pawn.Faction != null);
            Toil approach = Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
            approach.FailOnDespawnedOrNull(TargetIndex.A);
            approach.FailOn(() => job.targetA.Thing.IsForbidden(Faction.OfPlayer));
            yield return approach;

            // Swap: let go of the old scrap where the new one lay.
            Toil dropOld = ToilMaker.MakeToil("RM_GripperDropOld");
            dropOld.initAction = delegate
            {
                if (pawn.inventory.innerContainer.Any)
                {
                    pawn.inventory.DropAllNearPawn(pawn.Position);
                }
            };
            dropOld.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return dropOld;

            yield return Toils_Haul.TakeToInventory(TargetIndex.A, job.count);

            // Scurry off with it.
            Toil scurry = ToilMaker.MakeToil("RM_GripperScurry");
            scurry.initAction = delegate
            {
                IntVec3 root = pawn.Position;
                IntVec3 dest = RCellFinder.RandomWanderDestFor(pawn, root, ScurryRadius,
                    (p, c, r) => c.DistanceToSquared(r) >= 36, Danger.Some);
                if (!dest.IsValid || dest == root)
                {
                    ReadyForNextToil();
                    return;
                }
                pawn.pather.StartPath(dest, PathEndMode.OnCell);
            };
            scurry.defaultCompleteMode = ToilCompleteMode.PatherArrival;
            yield return scurry;
        }
    }

    [DefOf]
    public static class RM_WastelandJobDefOf
    {
        public static JobDef RM_GripperSteal;

        static RM_WastelandJobDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_WastelandJobDefOf));
        }
    }
}
