using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_WORN_GLOW_1, spec §3.4 paths 2 and 3: lacquer an item the pawn
    // is WEARING/WIELDING. Fetch `cost` Deepfire, walk to the station (a
    // powered RM_DeepfirePress, or -- path 3 -- the Ideology styling
    // station), work LacquerWorkTicks x WorkSpeedGlobal, then AddCoat.
    //   A = the station, B = the Deepfire stack, C = the worn item (unspawned,
    //   never pathed to -- only read).
    // Same no-FailOn shape as JobDriver_ApplyDeepfire (see its header: every
    // FailOn helper there ended the job on its first toil, MEASURED live
    // 2026-09-29); the checks are done by hand inside the work toil.
    public class JobDriver_LacquerWornItem : JobDriver
    {
        private float workDone;

        private Thing Station => job.GetTarget(TargetIndex.A).Thing;
        private Thing DeepfireStack => job.GetTarget(TargetIndex.B).Thing;
        private Thing Item => job.GetTarget(TargetIndex.C).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            if (!pawn.Reserve(Station, job, 1, -1, null, errorOnFailed)) return false;
            // PIGMENT_JOB_PAYMENT_ALLOCATION_1: reserve job.count units (the old call passed the count as maxPawns and
            // reserved the whole stack). If the stack picked at order time no longer has room, re-resolve it now.
            if (!pawn.CanReserve(DeepfireStack, DeepfireCostUtility.StackShareMaxPawns, job.count))
            {
                Thing other = DeepfireCostUtility.FindNearbyDeepfire(pawn, job.count, forced: true);
                if (other != null) job.SetTarget(TargetIndex.B, other);
            }
            return pawn.Reserve(DeepfireStack, job, DeepfireCostUtility.StackShareMaxPawns, job.count, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch);
            yield return Toils_Haul.StartCarryThing(TargetIndex.B, putRemainderInQueue: false, subtractNumTakenFromJobCount: true);
            yield return Toils_Goto.GotoThing(TargetIndex.A,
                Station != null && Station.def.hasInteractionCell ? PathEndMode.InteractionCell : PathEndMode.Touch);

            Toil work = ToilMaker.MakeToil("LacquerWornItem");
            work.initAction = delegate { workDone = 0f; };
            work.tickIntervalAction = delegate(int delta)
            {
                if (!StillValid(out string why))
                {
                    if (why != null) Messages.Message(why, pawn, MessageTypeDefOf.RejectInput, historical: false);
                    EndJobWith(JobCondition.Incompletable);
                    return;
                }
                pawn.rotationTracker.FaceTarget(Station);
                workDone += pawn.GetStatValue(StatDefOf.WorkSpeedGlobal) * delta;
                if (workDone >= DeepfirePaintDefaults.LacquerWorkTicks)
                {
                    // PIGMENT_JOB_PAYMENT_ALLOCATION_1: the coat lands only when the carried deepfire covers its cost.
                    int cost = LacquerWornItemUtility.CostFor(Item);
                    if (!DeepfireCostUtility.TryPayCarried(pawn, cost))
                    {
                        Messages.Message("Not enough deepfire carried to lacquer " + Item.LabelShort + " (needs " + cost + ").",
                            pawn, MessageTypeDefOf.RejectInput, historical: false);
                        EndJobWith(JobCondition.Incompletable);
                        return;
                    }
                    pawn.skills?.Learn(SkillDefOf.Artistic, DeepfirePaintDefaults.LacquerArtisticXP);
                    Item.TryGetComp<CompDeepfire>()?.AddCoat();
                    ReadyForNextToil();
                }
            };
            work.defaultCompleteMode = ToilCompleteMode.Never;
            work.WithEffect(EffecterDefOf.Paint, TargetIndex.A);
            work.WithProgressBar(TargetIndex.A, () => workDone / DeepfirePaintDefaults.LacquerWorkTicks);
            work.activeSkill = () => SkillDefOf.Artistic;
            work.handlingFacing = true;
            yield return work;
        }

        private bool StillValid(out string why)
        {
            why = null;
            if (Station == null || Station.Destroyed || DeepfireStack == null) return false;
            if (pawn.carryTracker.CarriedThing == null) return false; // GPT review #5: never "pay" with nothing
            if (Item == null || Item.Destroyed || WornGlowUtility.WearerOf(Item) != pawn) return false;
            CompDeepfire comp = Item.TryGetComp<CompDeepfire>();
            if (comp == null || !comp.CanAddCoat) return false;
            if (!WornGlowUtility.LacquerAllowed(Item)) return false; // GPT review #7
            if (!LacquerWornItemUtility.StationUsable(Station))
            {
                why = "The deepfire press lost power.";
                return false;
            }
            return true;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref workDone, "workDone", 0f);
        }
    }

    public static class LacquerWornItemUtility
    {
        public const string PressDefName = "RM_DeepfirePress";
        public const string StylingStationDefName = "StylingStation";

        public static int CostFor(Thing item) => DeepfireCostUtility.CostFor(item);

        // The press is powered-only (spec §2.3); the styling station needs no
        // power in vanilla and gets none here.
        public static bool StationUsable(Thing station)
        {
            if (station == null || !station.Spawned) return false;
            if (station.def.defName != PressDefName) return true;
            CompPowerTrader power = station.TryGetComp<CompPowerTrader>();
            return power == null || power.PowerOn;
        }

        public static Thing FindPress(Pawn pawn, bool forced)
        {
            ThingDef pressDef = DefDatabase<ThingDef>.GetNamedSilentFail(PressDefName);
            if (pressDef == null || pawn.Map == null) return null;
            List<Thing> presses = pawn.Map.listerThings.ThingsOfDef(pressDef);
            Thing best = null;
            int bestDist = int.MaxValue;
            for (int i = 0; i < presses.Count; i++)
            {
                Thing p = presses[i];
                if (!StationUsable(p) || p.IsForbidden(pawn)) continue;
                if (!pawn.CanReserveAndReach(p, PathEndMode.InteractionCell, Danger.Some, 1, -1, null, forced)) continue;
                int d = (p.Position - pawn.Position).LengthHorizontalSquared;
                if (d < bestDist) { bestDist = d; best = p; }
            }
            return best;
        }

        // Returns the job, or null with a player-facing reason.
        public static Job MakeJob(Pawn pawn, ThingWithComps item, Thing station, out string failReason)
        {
            failReason = null;
            CompDeepfire comp = item?.GetComp<CompDeepfire>();
            if (comp == null || !comp.CanAddCoat) { failReason = "Already at the maximum number of coats."; return null; }
            if (!WornGlowUtility.LacquerAllowed(item)) { failReason = "Painting this kind of item is disabled in Mod Settings."; return null; }
            if (station == null) { failReason = "Needs a powered, reachable deepfire press."; return null; }
            int cost = CostFor(item);
            Thing stack = DeepfireCostUtility.FindNearbyDeepfire(pawn, cost, forced: true);
            if (stack == null) { failReason = "Needs " + cost + " deepfire in one reachable stack."; return null; }

            Job job = JobMaker.MakeJob(DeepfireDefOf.RM_LacquerWornItem, station, stack, item);
            job.count = cost;
            return job;
        }

        public static Gizmo MakeGizmo(Pawn pawn)
        {
            List<ThingWithComps> items = WornGlowUtility.Lacquerable(pawn);
            var cmd = new Command_Action
            {
                defaultLabel = "lacquer worn item...",
                defaultDesc = "Walk to a powered deepfire press with enough deepfire and lacquer one worn "
                    + "garment or held weapon (one coat, up to three). A lacquered item glows on its wearer -- "
                    + "and a pawn glowing in the dark is easier to hit.",
                icon = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Deepfire")?.uiIcon ?? BaseContent.BadTex,
                action = delegate
                {
                    var options = new List<FloatMenuOption>();
                    Thing press = FindPress(pawn, forced: true);
                    foreach (ThingWithComps item in WornGlowUtility.Lacquerable(pawn))
                    {
                        ThingWithComps target = item;
                        int coats = target.GetComp<CompDeepfire>().coats;
                        string label = target.LabelCap + " (coats " + coats + ", costs " + CostFor(target) + " deepfire)";
                        Job job = MakeJob(pawn, target, press, out string why);
                        if (job == null)
                        {
                            options.Add(new FloatMenuOption(label + ": " + why, null));
                            continue;
                        }
                        options.Add(new FloatMenuOption(label, delegate
                        {
                            pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
                        }));
                    }
                    Find.WindowStack.Add(new FloatMenu(options));
                },
            };
            if (items.Count == 0) cmd.Disable("Nothing worn or held can take another coat.");
            return cmd;
        }
    }

    // Spec §3.4: the pawn's own gizmo, drafted or not. One gizmo per pawn
    // (not per item), so it rides Pawn.GetGizmos rather than a per-apparel
    // CompGetWornGizmosExtra. Pass-through iterator postfix.
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.GetGizmos))]
    public static class Patch_Pawn_GetGizmos_Lacquer
    {
        public static IEnumerable<Gizmo> Postfix(IEnumerable<Gizmo> __result, Pawn __instance)
        {
            foreach (Gizmo g in __result) yield return g;
            if (__instance.IsColonistPlayerControlled && __instance.Spawned
                && (__instance.apparel != null || __instance.equipment != null))
            {
                yield return LacquerWornItemUtility.MakeGizmo(__instance);
            }
        }
    }
}
