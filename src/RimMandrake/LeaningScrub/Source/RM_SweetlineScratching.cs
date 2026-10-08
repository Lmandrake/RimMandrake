using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // SWEETLINE_SCRATCHING_TREE_BUILD_1 — the scratching tree.
    // Spec: design/Jawa/worldbuilding/biomes/sweetline_guardian_spec.md §3-§4.
    //
    // Owner 2026-10-03: any animal that grows a shearable coat now and then walks to
    // a sweetline tree and rubs it off — "just a really wonderfully scratchy tree they
    // like". Most of the coat drops beside the trunk as the animal's own woolDef; the
    // rest felts into the bark (the station comp's felt store, paid out at harvest).
    //
    //   registry   which sweetline trees stand on which map (station comp spawn/despawn),
    //              so neither the job giver nor the per-tick patch ever scans.
    //   patch      CompShearable.Active postfix: a WILD animal grows its coat too (vanilla
    //              E2: no faction -> no growth), only while scratching is on and a tree
    //              stands somewhere in this game. Per-tick getter: field tests only.
    //   giver      inserted at Animal_PreWander behind a ~6 h MTB node (ThinkTreeDef).
    //   driver     touch the trunk, rub 600 ticks, drop + bank + zero fullness by field ref.
    //              Never Gathered(doer) (E3: colonist-shearing API, errors when not Active).
    // ════════════════════════════════════════════════════════════════════
    public static class RM_SweetlineScratching
    {
        private static readonly Dictionary<Map, List<Thing>> trees = new Dictionary<Map, List<Thing>>();
        private static Game registryGame;
        private static int treeCount;

        private static readonly AccessTools.FieldRef<CompHasGatherableBodyResource, float> FullnessRef =
            AccessTools.FieldRefAccess<CompHasGatherableBodyResource, float>("fullness");

        public static bool On =>
            RM_WindCalendar.On(RM_LeaningScrubSettings.sweetlineStationsEnabled)
            && RM_LeaningScrubSettings.sweetlineScratchingEnabled;

        /// <summary>True when at least one sweetline tree is spawned in the running game.</summary>
        public static bool AnyTree
        {
            get
            {
                CheckGame();
                return treeCount > 0;
            }
        }

        private static void CheckGame()
        {
            if (registryGame != Current.Game)
            {
                trees.Clear();
                treeCount = 0;
                registryGame = Current.Game;
            }
        }

        public static void Register(Thing tree)
        {
            CheckGame();
            Map map = tree.Map;
            if (map == null)
            {
                return;
            }
            if (!trees.TryGetValue(map, out List<Thing> list))
            {
                list = new List<Thing>();
                trees[map] = list;
            }
            if (!list.Contains(tree))
            {
                list.Add(tree);
                treeCount++;
            }
        }

        public static void Deregister(Thing tree, Map map)
        {
            CheckGame();
            if (map != null && trees.TryGetValue(map, out List<Thing> list) && list.Remove(tree))
            {
                treeCount--;
            }
        }

        public static List<Thing> TreesOn(Map map)
        {
            CheckGame();
            return map != null && trees.TryGetValue(map, out List<Thing> list) ? list : null;
        }

        public static float Fullness(CompShearable comp) => FullnessRef(comp);

        public static void SetFullness(CompShearable comp, float value) => FullnessRef(comp) = value;

        /// <summary>Why this animal would not go to scratch now, or null when it would (tree in `found`).</summary>
        public static string WhyNot(Pawn pawn, out Thing found, float range)
        {
            found = null;
            if (!On)
            {
                return "scratching is off";
            }
            if (pawn == null || !pawn.Spawned || pawn.RaceProps == null || !pawn.RaceProps.Animal)
            {
                return "not a spawned animal";
            }
            CompShearable coat = pawn.TryGetComp<CompShearable>();
            if (coat == null || coat.Props.woolDef == null)
            {
                return "no shearable coat";
            }
            if (Fullness(coat) < RM_LeaningScrubSettings.sweetlineCoatReady)
            {
                return "coat at " + Fullness(coat).ToStringPercent() + ", below the ready mark";
            }
            if (pawn.roping != null && pawn.roping.IsRoped)
            {
                return "roped";
            }
            List<Thing> list = TreesOn(pawn.Map);
            if (list == null || list.Count == 0)
            {
                return "no sweetline tree on this map";
            }
            float best = range * range;
            for (int i = 0; i < list.Count; i++)
            {
                Thing tree = list[i];
                if (tree == null || !tree.Spawned || tree.Map != pawn.Map)
                {
                    continue;
                }
                float d = (tree.Position - pawn.Position).LengthHorizontalSquared;
                if (d > best)
                {
                    continue;
                }
                if (Awake(tree))
                {
                    continue;
                }
                if (pawn.Faction == Faction.OfPlayer && !tree.Position.InAllowedArea(pawn))
                {
                    continue;
                }
                if (!pawn.CanReach(tree, PathEndMode.Touch, Danger.Some))
                {
                    continue;
                }
                best = d;
                found = tree;
            }
            return found == null ? "no reachable, calm sweetline tree within " + range.ToString("F0") + " cells" : null;
        }

        /// <summary>An animal walking into a warden fight looks wrong: an awake roost is skipped.</summary>
        public static bool Awake(Thing tree)
        {
            RM_CompGuardianRoost roost = tree.TryGetComp<RM_CompGuardianRoost>();
            return roost != null && RM_SweetlineGuardianRules.StageOf(roost.Disturbance) >= 3;
        }

        /// <summary>The rub's end: drop most of the coat at the trunk, felt the rest, zero the coat.</summary>
        public static void Rub(Pawn pawn, Thing tree)
        {
            CompShearable coat = pawn.TryGetComp<CompShearable>();
            if (coat == null || coat.Props.woolDef == null || tree == null || !tree.Spawned)
            {
                return;
            }
            ThingDef woolDef = coat.Props.woolDef;
            List<int> stacks = new List<int>();
            RM_CoatKernel.Rub(coat.Props.woolAmount, Fullness(coat), RM_LeaningScrubSettings.sweetlineFeltShare, Rand.Value, Rand.Value,
                woolDef.stackLimit, out int amount, out int ground, out float felted, stacks);
            for (int i = 0; i < stacks.Count; i++)
            {
                Thing wool = ThingMaker.MakeThing(woolDef);
                wool.stackCount = stacks[i];
                GenPlace.TryPlaceThing(wool, tree.Position, tree.Map, ThingPlaceMode.Near);
            }
            SetFullness(coat, 0f);
            tree.TryGetComp<RM_CompSweetlineStation>()?.Notify_Scratched(pawn, felted);
        }

        /// <summary>
        /// Bridge proof (jawa/static_call): set the coat of the shearable animal at `cell` to
        /// `fullness`, then ask the real job giver. "ORDERED ..." when it started the job,
        /// "REFUSED: why" otherwise. Exercises the giver's whole gate, not a forced job.
        /// </summary>
        public static string ProofOrderScratch(Map map, IntVec3 cell, float fullness)
        {
            if (map == null)
            {
                return "REFUSED: no map";
            }
            Pawn animal = null;
            foreach (Thing t in cell.GetThingList(map))
            {
                if (t is Pawn p && p.TryGetComp<CompShearable>() != null)
                {
                    animal = p;
                    break;
                }
            }
            if (animal == null)
            {
                return "REFUSED: no shearable animal at " + cell;
            }
            SetFullness(animal.TryGetComp<CompShearable>(), Mathf.Clamp01(fullness));
            Job job = new RM_JobGiver_ScratchOnSweetline().TryIssueJobPackage(animal, default(JobIssueParams)).Job;
            if (job == null)
            {
                return "REFUSED: " + (WhyNot(animal, out _, RM_JobGiver_ScratchOnSweetline.Range) ?? "giver returned no job");
            }
            animal.jobs.StartJob(job, JobCondition.InterruptForced);
            return "ORDERED " + animal.ThingID + " -> " + job.targetA.Thing?.ThingID;
        }
    }

    public class RM_JobGiver_ScratchOnSweetline : ThinkNode_JobGiver
    {
        public const float Range = 60f;

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (RM_SweetlineScratching.WhyNot(pawn, out Thing tree, Range) != null)
            {
                return null;
            }
            Job job = JobMaker.MakeJob(RM_LeaningScrubDefOf.RM_ScratchOnSweetline, tree);
            job.expiryInterval = 2500;
            job.checkOverrideOnExpire = true;
            return job;
        }
    }

    public class RM_JobDriver_ScratchOnSweetline : JobDriver
    {
        public const int RubTicks = 600;

        // A herd may share one trunk, and a colonist harvesting it holds no claim the animal
        // should respect: no reservation.
        public override bool TryMakePreToilReservations(bool errorOnFailed) => true;

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            this.FailOn(() => !RM_SweetlineScratching.On || RM_SweetlineScratching.Awake(job.targetA.Thing));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil rub = Toils_General.Wait(RubTicks, TargetIndex.A);
            rub.WithProgressBarToilDelay(TargetIndex.A);
            rub.WithEffect(EffecterDefOf.Harvest_Tree, TargetIndex.A);
            rub.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            yield return rub;
            Toil done = ToilMaker.MakeToil("RM_ScratchOnSweetline_Done");
            done.initAction = () => RM_SweetlineScratching.Rub(pawn, job.targetA.Thing);
            done.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return done;
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_SweetlineScratchingPatches
    {
        static RM_SweetlineScratchingPatches()
        {
            try
            {
                var target = AccessTools.PropertyGetter(typeof(CompShearable), "Active");
                if (target == null)
                {
                    Log.Error("[RM LeaningScrub] wild-coat growth: CompShearable.Active not found — rule NOT armed.");
                    return;
                }
                new Harmony("mandrake.rm.leaningscrub").Patch(target,
                    postfix: new HarmonyMethod(typeof(RM_SweetlineScratchingPatches), nameof(Active_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM LeaningScrub] wild-coat growth: patch failed, rule NOT armed. " + e);
            }
        }

        // Runs every tick for every shearable pawn: cheap tests first, settings bools, a static int.
        public static void Active_Postfix(CompShearable __instance, ref bool __result)
        {
            if (__result)
            {
                return;
            }
            Pawn pawn = __instance.parent as Pawn;
            if (pawn == null || pawn.Faction != null || pawn.Suspended)
            {
                return;
            }
            if (!RM_SweetlineScratching.On || !RM_SweetlineScratching.AnyTree)
            {
                return;
            }
            if (pawn.ageTracker == null || !pawn.ageTracker.CurLifeStage.shearable)
            {
                return;
            }
            if (ModsConfig.AnomalyActive && pawn.IsShambler)
            {
                return;
            }
            __result = true;
        }
    }
}
