using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_SOLVENT_WAKE_BUILD_1 - pour solvent into the tar and the dormant tar beast wakes AT ONCE as a manhunter.
    // A deliberate player weapon (owner, 2026-10-02): no ritual, no learning step, anyone holding the solvent can do it.
    //
    // Chain: float-menu order on the bulge (FloatMenuOptionProvider_PourSolvent, confirmation dialog) -> JobDriver_RM_PourSolvent
    // (carry the solvent to the tar's edge, wait, pour) -> RM_CompBulgeSolventPour.Pour (splash + hiss, both god deltas,
    // letter, a pending-wake record, the stock CompWakeUpDormant.Activate) -> RM_CompTarBeast's first tick consumes the record
    // and starts ManhunterPermanent. Which items count as solvent is DATA on the bulge's comp props, so the free-tier move of the
    // solvents (SUMP_FREE_TIER_MOVE_BUILD_1) only changes a defName list in RUT_BeastBulge.xml.

    public class CompProperties_BulgeSolventPour : CompProperties
    {
        // Any of these defs poured counts as a solvent; the strong list is the subset that satisfies "strong solvent required".
        public List<string> solventDefNames = new List<string>();
        public List<string> strongSolventDefNames = new List<string>();
        // How far from the bulge a pawn may stand and throw (the bulge sits in impassable deep tar).
        public float pourRange = 6f;

        public CompProperties_BulgeSolventPour()
        {
            compClass = typeof(RM_CompBulgeSolventPour);
        }
    }

    public class RM_CompBulgeSolventPour : ThingComp
    {
        public CompProperties_BulgeSolventPour Props => (CompProperties_BulgeSolventPour)props;

        public bool CanBePouredInto
        {
            get
            {
                CompCanBeDormant dormant = parent.GetComp<CompCanBeDormant>();
                return parent.Spawned && dormant != null && !dormant.Awake;
            }
        }

        public bool IsSolvent(Thing t)
        {
            return t != null && Props.solventDefNames.Contains(t.def.defName)
                && (!RM_EnvironmentalHazardsSettings.tarSolventStrongRequired || IsStrong(t));
        }

        public bool IsStrong(Thing t)
        {
            return t != null && Props.strongSolventDefNames.Contains(t.def.defName);
        }

        public static int MinCount => Mathf.Max(1, Mathf.RoundToInt(RM_EnvironmentalHazardsSettings.tarSolventMinCount));

        // The cell the pourer stands on: standable, reachable, in line of sight of the bulge, nearest to it.
        public bool TryFindStandCell(Pawn pawn, out IntVec3 cell)
        {
            cell = IntVec3.Invalid;
            float best = 9999f;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(parent.Position, Props.pourRange, false))
            {
                if (!c.InBounds(parent.Map) || !c.Standable(parent.Map) || !GenSight.LineOfSight(c, parent.Position, parent.Map, true))
                {
                    continue;
                }
                float d = (c - parent.Position).LengthHorizontalSquared;
                if (d < best && pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
                {
                    best = d;
                    cell = c;
                }
            }
            return cell.IsValid;
        }

        // The pour itself. `solvent` is the carried thing, already split to the poured amount and about to be destroyed.
        public void Pour(Pawn pourer, Thing solvent)
        {
            Map map = parent.Map;
            IntVec3 cell = parent.Position;
            bool strong = IsStrong(solvent);
            int count = solvent.stackCount;
            bool manhunter = RM_EnvironmentalHazardsSettings.tarSolventManhunter && RM_EnvironmentalHazardsSettings.tarBeastEnabled;

            // Readable signs: the black-gold splash and the hiss.
            FleckMaker.ThrowDustPuffThick(parent.DrawPos, map, 2.5f, new Color(0.35f, 0.26f, 0.05f));
            FleckMaker.ThrowDustPuffThick(parent.DrawPos, map, 1.8f, new Color(0.05f, 0.04f, 0.02f));
            SoundDef hiss = DefDatabase<SoundDef>.GetNamedSilentFail("HissJet");
            if (hiss != null)
            {
                hiss.PlayOneShot(new TargetInfo(cell, map));
            }

            // Both gods at once (rare shared offering). Positive = the god is fed; sized by solvent grade and amount.
            float scale = (strong ? 1.5f : 1f) * count / (float)MinCount;
            RM_NinefoldGodBridge.ApplyDelta("Shkaar", RM_EnvironmentalHazardsSettings.tarSolventGodDeltaShkaar * scale, "the tar woken by solvent");
            RM_NinefoldGodBridge.ApplyDelta("Zizzik", RM_EnvironmentalHazardsSettings.tarSolventGodDeltaZizzik * scale, "the tar woken by solvent");

            RM_MapComponent_TarSolventWake.Register(map, cell, manhunter);
            CompWakeUpDormant wake = parent.GetComp<CompWakeUpDormant>();
            if (wake != null)
            {
                wake.Activate(pourer);
            }

            Find.LetterStack.ReceiveLetter(
                "The tar is awake",
                pourer.LabelShortCap + " poured solvent into the tar. The smooth bulge heaves, and the beast beneath it is awake"
                    + (manhunter ? " and hunting everyone on this map." : "."),
                LetterDefOf.ThreatBig,
                new TargetInfo(cell, map));
        }
    }

    // Pending wakes: remembers which bulge was poured into so the emerged beast (spawned a tick later by the stock
    // PawnSpawnOnWakeup comp, within ~8 cells of the bulge) can be told to hunt. Scribed; entries expire.
    public class RM_MapComponent_TarSolventWake : MapComponent
    {
        private const int ExpireTicks = 3000;
        private const float MatchRadius = 14f;

        private List<IntVec3> cells = new List<IntVec3>();
        private List<int> ticks = new List<int>();
        private List<bool> manhunter = new List<bool>();

        public RM_MapComponent_TarSolventWake(Map map) : base(map)
        {
        }

        public static void Register(Map map, IntVec3 cell, bool manhunter)
        {
            RM_MapComponent_TarSolventWake mc = map.GetComponent<RM_MapComponent_TarSolventWake>();
            if (mc == null)
            {
                return;
            }
            mc.cells.Add(cell);
            mc.ticks.Add(Find.TickManager.TicksGame);
            mc.manhunter.Add(manhunter);
        }

        // True when a pour woke a bulge near `pos`; manhunter says whether the pour asked for a hunt. Consumes the record.
        public static bool TryConsume(Map map, IntVec3 pos, out bool manhunter)
        {
            manhunter = false;
            RM_MapComponent_TarSolventWake mc = map.GetComponent<RM_MapComponent_TarSolventWake>();
            if (mc == null)
            {
                return false;
            }
            for (int i = 0; i < mc.cells.Count; i++)
            {
                if ((mc.cells[i] - pos).LengthHorizontal <= MatchRadius)
                {
                    manhunter = mc.manhunter[i];
                    mc.cells.RemoveAt(i);
                    mc.ticks.RemoveAt(i);
                    mc.manhunter.RemoveAt(i);
                    return true;
                }
            }
            return false;
        }

        public int PendingCount => cells.Count;

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (cells.Count == 0 || Find.TickManager.TicksGame % 250 != 0)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            for (int i = cells.Count - 1; i >= 0; i--)
            {
                if (now - ticks[i] > ExpireTicks)
                {
                    cells.RemoveAt(i);
                    ticks.RemoveAt(i);
                    manhunter.RemoveAt(i);
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref cells, "pendingCells", LookMode.Value);
            Scribe_Collections.Look(ref ticks, "pendingTicks", LookMode.Value);
            Scribe_Collections.Look(ref manhunter, "pendingManhunter", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (cells == null) cells = new List<IntVec3>();
                if (ticks == null) ticks = new List<int>();
                if (manhunter == null) manhunter = new List<bool>();
                int n = Mathf.Min(cells.Count, Mathf.Min(ticks.Count, manhunter.Count));
                if (cells.Count != n) cells.RemoveRange(n, cells.Count - n);
                if (ticks.Count != n) ticks.RemoveRange(n, ticks.Count - n);
                if (manhunter.Count != n) manhunter.RemoveRange(n, manhunter.Count - n);
            }
        }
    }

    public class FloatMenuOptionProvider_PourSolvent : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;

        protected override bool Undrafted => true;

        protected override bool Multiselect => false;

        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!RM_EnvironmentalHazardsSettings.tarSolventPourEnabled)
            {
                return null;
            }
            RM_CompBulgeSolventPour comp = clickedThing.TryGetComp<RM_CompBulgeSolventPour>();
            if (comp == null || !comp.CanBePouredInto)
            {
                return null;
            }
            Pawn pawn = context.FirstSelectedPawn;
            if (pawn == null)
            {
                return null;
            }

            string label = "Pour solvent into the tar";
            int need = RM_CompBulgeSolventPour.MinCount;
            Thing solvent = FindSolvent(pawn, comp, need);
            if (solvent == null)
            {
                string why = RM_EnvironmentalHazardsSettings.tarSolventStrongRequired
                    ? "needs " + need + " strong tar solvent"
                    : "needs " + need + " tar solvent";
                return new FloatMenuOption(label + " (" + why + ")", null);
            }
            if (!comp.TryFindStandCell(pawn, out IntVec3 stand))
            {
                return new FloatMenuOption(label + " (" + "NoPath".Translate().CapitalizeFirst() + ")", null);
            }

            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(label, delegate
            {
                Action go = delegate
                {
                    Job job = JobMaker.MakeJob(RM_EnvironmentalHazardsJobDefOf.RM_PourSolvent, clickedThing, stand, solvent);
                    job.count = need;
                    pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
                };
                bool manhunter = RM_EnvironmentalHazardsSettings.tarSolventManhunter && RM_EnvironmentalHazardsSettings.tarBeastEnabled;
                Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(
                    manhunter ? "The tar beast will wake now and hunt everyone on this map." : "The tar beast will wake now.",
                    go,
                    destructive: true));
            }), pawn, clickedThing);
        }

        private static Thing FindSolvent(Pawn pawn, RM_CompBulgeSolventPour comp, int need)
        {
            Thing carried = pawn.carryTracker?.CarriedThing;
            if (carried != null && comp.IsSolvent(carried) && carried.stackCount >= need)
            {
                return carried;
            }
            return GenClosest.ClosestThingReachable(pawn.Position, pawn.Map, ThingRequest.ForGroup(ThingRequestGroup.HaulableEver),
                PathEndMode.ClosestTouch, TraverseParms.For(pawn), 9999f,
                t => comp.IsSolvent(t) && t.stackCount >= need && !t.IsForbidden(pawn) && pawn.CanReserve(t, 1, need));
        }
    }

    public class JobDriver_RM_PourSolvent : JobDriver
    {
        private const int PourTicks = 90;
        private const TargetIndex BulgeInd = TargetIndex.A;
        private const TargetIndex StandInd = TargetIndex.B;
        private const TargetIndex SolventInd = TargetIndex.C;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            Thing solvent = job.GetTarget(SolventInd).Thing;
            if (solvent == null || solvent == pawn.carryTracker?.CarriedThing)
            {
                return true;
            }
            return pawn.Reserve(solvent, job, 1, job.count, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedOrNull(BulgeInd);
            this.FailOn(delegate
            {
                RM_CompBulgeSolventPour comp = job.GetTarget(BulgeInd).Thing?.TryGetComp<RM_CompBulgeSolventPour>();
                return comp == null || !comp.CanBePouredInto;
            });

            Thing solvent = job.GetTarget(SolventInd).Thing;
            if (solvent != null && solvent != pawn.carryTracker?.CarriedThing)
            {
                yield return Toils_Goto.GotoThing(SolventInd, PathEndMode.ClosestTouch)
                    .FailOnDespawnedNullOrForbidden(SolventInd)
                    .FailOnSomeonePhysicallyInteracting(SolventInd);
                yield return Toils_Haul.StartCarryThing(SolventInd);
            }

            yield return Toils_Goto.GotoCell(StandInd, PathEndMode.OnCell);

            Toil pour = ToilMaker.MakeToil("PourSolvent");
            pour.defaultCompleteMode = ToilCompleteMode.Delay;
            pour.defaultDuration = PourTicks;
            pour.WithProgressBar(BulgeInd, () => 1f - (float)pour.actor.jobs.curDriver.ticksLeftThisToil / PourTicks);
            pour.FailOn(() => pawn.carryTracker.CarriedThing == null);
            yield return pour;

            Toil finish = ToilMaker.MakeToil("PourSolventFinish");
            finish.defaultCompleteMode = ToilCompleteMode.Instant;
            finish.initAction = delegate
            {
                Thing carried = pawn.carryTracker.CarriedThing;
                RM_CompBulgeSolventPour comp = job.GetTarget(BulgeInd).Thing?.TryGetComp<RM_CompBulgeSolventPour>();
                if (carried == null || comp == null || !comp.CanBePouredInto)
                {
                    return;
                }
                int amount = Mathf.Min(carried.stackCount, Mathf.Max(1, job.count));
                Thing poured = carried.SplitOff(amount);
                comp.Pour(pawn, poured);
                poured.Destroy();
                // Anything carried beyond the poured amount goes back on the ground.
                if (pawn.carryTracker.CarriedThing != null)
                {
                    pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out Thing _);
                }
            };
            yield return finish;
        }
    }

    // Ninefold is a soft dependency: bound by reflection (same idiom as LuminousPigment's NinefoldDeltaBridge), absent = silent no-op.
    internal static class RM_NinefoldGodBridge
    {
        private static bool resolved;
        private static PropertyInfo instanceProp;
        private static MethodInfo applyDelta;
        private static Type godType;

        private static void Resolve()
        {
            if (resolved)
            {
                return;
            }
            resolved = true;
            Type ninefold = AccessTools.TypeByName("RimMandrake.Ninefold.GameComponent_Ninefold");
            godType = AccessTools.TypeByName("RimMandrake.Ninefold.God");
            if (ninefold == null || godType == null || !godType.IsEnum)
            {
                return;
            }
            instanceProp = AccessTools.Property(ninefold, "Instance");
            applyDelta = AccessTools.Method(ninefold, "ApplyDelta", new[] { godType, typeof(float), typeof(string) });
        }

        public static void ApplyDelta(string godName, float amount, string reason)
        {
            Resolve();
            if (instanceProp == null || applyDelta == null)
            {
                return;
            }
            object instance = instanceProp.GetValue(null);
            if (instance == null)
            {
                return;
            }
            try
            {
                applyDelta.Invoke(instance, new object[] { Enum.Parse(godType, godName), amount, reason });
            }
            catch (ArgumentException)
            {
                Log.Warning("[RimMandrake.EnvironmentalHazards] God." + godName + " no longer exists; solvent-wake god delta skipped.");
            }
        }
    }
}
