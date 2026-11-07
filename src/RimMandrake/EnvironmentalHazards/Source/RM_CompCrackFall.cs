using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.EnvironmentalHazards
{
    //   <ThingDef ParentName="TreeBase">
    //     <defName>RM_Mirrelbole</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_CrackFall">
    //         <mtbDaysAtFullGrowth>3</mtbDaysAtFullGrowth>
    //         <minGrowthFraction>0.6</minGrowthFraction>
    //         <fallDelayTicksRange>200~600</fallDelayTicksRange>
    //       </li>
    //     </comps>
    //   </ThingDef>
    //
    // GREENTIDE_JUNGLE_TREE_ROSTER_1 (2026-09-26): the mechanism-proof stub
    // this comment used to name, RUT_Placeholder_GreentideGiantTree, is
    // retired now that the roster's real trees ship and wire this comp for
    // real (RM_Mirrelbole, "highest crack-fall rate on the page").
    public class CompProperties_CrackFall : CompProperties
    {
        // INVENTED (kit spec M6, feller 1: "MTB 8 days at full growth").
        public float mtbDaysAtFullGrowth = 8f;

        // Below this growth fraction the tree never rolls at all — "past a
        // growth/age threshold" per the spec's own wording. INVENTED: 0.9,
        // i.e. only a tree at or near full maturity cracks under its own
        // weight. Between minGrowthFraction and 1.0, MTB scales down
        // linearly with growth (a tree right at the threshold cracks about
        // as often as the full-growth number; RM_CompCrackFall.EffectiveMtbDays
        // documents the exact formula) — reads better mechanically than a
        // flat on/off per the build brief's own discretion.
        public float minGrowthFraction = 0.9f;

        // "a few hundred ticks" per the spec. INVENTED range.
        public IntRange fallDelayTicksRange = new IntRange(300, 900);

        // Falls back to SoundDefOf.Building_Complete (the same creak cue
        // RM_MapComponent_LivingRegrowth's own CreakWarning already uses in
        // this assembly) when left unset.
        public SoundDef creakSound;

        public CompProperties_CrackFall()
        {
            compClass = typeof(RM_CompCrackFall);
        }
    }

    // GREENTIDE_MECHANICS_2 M6 build, feller 1 ("cracked from within").
    // CompTickRare (vanilla's 250-tick cadence) matches every other interval
    // roll in this assembly (RM_CompDryFieldEmitter, HediffComp_
    // PeriodicAreaAttack's own tickIntervalTicks default). Two states, not
    // Scribed as an enum: warnTicksRemaining < 0 means "not yet warned, still
    // rolling"; >= 0 counts down to the delayed fall (0 = due, queued for the map's
    // next tick).
    public class RM_CompCrackFall : ThingComp
    {
        private int warnTicksRemaining = -1;

        public CompProperties_CrackFall Props => (CompProperties_CrackFall)props;

        // A Plant parent is Long-ticked (TreeBase/PlantBase tickerType Long),
        // and Plant only ever runs ThingWithComps.TickLong -> CompTickLong, so
        // a CompTickRare-only comp never fires on a tree. Both cadences route
        // to one step with the elapsed tick count.
        public override void CompTickRare()
        {
            base.CompTickRare();
            Step(250);
        }

        public override void CompTickLong()
        {
            base.CompTickLong();
            Step(2000);
        }

        private void Step(int elapsedTicks)
        {
            if (!RM_EnvironmentalHazardsSettings.treeFallEnabled)
            {
                return; // mod option: RM_TreeFallUtility.FellTree itself no-ops too, but skip the roll/countdown work as well
            }

            Plant tree = parent as Plant;
            if (tree == null || tree.Destroyed || !tree.Spawned || tree.Map == null)
            {
                return;
            }

            if (warnTicksRemaining >= 0)
            {
                // Held at 0, never negative: a queue entry lost to a save re-queues on the next tick.
                warnTicksRemaining = Mathf.Max(0, warnTicksRemaining - elapsedTicks);
                if (warnTicksRemaining == 0)
                {
                    // Never fell here: this runs inside Plant.TickLong's base call, and vanilla goes on to read
                    // base.Map with no second Destroyed check (null once destroyed), the NRE in
                    // RegionAndRoomQuery.RegionAt under PlantUtility.GrowthSeasonNow. The fall happens on the map's
                    // next tick instead.
                    tree.Map.GetComponent<RM_MapComponent_DeferredTreeFall>()?.Enqueue(tree);
                }
                return;
            }

            if (tree.Growth < Props.minGrowthFraction)
            {
                return;
            }

            if (Rand.MTBEventOccurs(EffectiveMtbDays(tree), 60000f, elapsedTicks))
            {
                warnTicksRemaining = Props.fallDelayTicksRange.RandomInRange;
                (Props.creakSound ?? SoundDefOf.Building_Complete).PlayOneShot(SoundInfo.InMap(new TargetInfo(tree.Position, tree.Map)));
                Messages.Message(
                    "RM_TreeFallCreak".Translate(tree.LabelShort),
                    new TargetInfo(tree.Position, tree.Map),
                    MessageTypeDefOf.ThreatSmall);
            }
        }

        // Linear scale-down below full growth: at minGrowthFraction the MTB
        // is exactly mtbDaysAtFullGrowth (still crack-eligible, just at the
        // named rate); above that it only gets more likely, up to double
        // the base rate (half the MTB) at Growth == 1. INVENTED shape —
        // "scaling down at lower growth if that reads better mechanically"
        // per the build brief's own discretion.
        private float EffectiveMtbDays(Plant tree)
        {
            float t = Mathf.InverseLerp(Props.minGrowthFraction, 1f, Mathf.Clamp01(tree.Growth));
            return Mathf.Lerp(Props.mtbDaysAtFullGrowth * 2f, Props.mtbDaysAtFullGrowth, t);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref warnTicksRemaining, "warnTicksRemaining", -1);
        }

        public override string CompInspectStringExtra()
        {
            return warnTicksRemaining >= 0 ? "RM_TreeFallCracking".Translate() : null;
        }

        /// <summary>Live proof only: the countdown is over, the next step fells.</summary>
        internal void ForceDueForProof()
        {
            warnTicksRemaining = 0;
        }
    }

    /// <summary>Fells a cracked tree outside Plant.TickLong (see RM_CompCrackFall.Step). Not saved: an entry lost to a
    /// save re-queues on the tree's next long tick, since its countdown stays at 0.</summary>
    public class RM_MapComponent_DeferredTreeFall : MapComponent
    {
        private readonly List<Plant> pending = new List<Plant>();
        private readonly List<Plant> draining = new List<Plant>();

        public RM_MapComponent_DeferredTreeFall(Map map) : base(map)
        {
        }

        public void Enqueue(Plant tree)
        {
            if (tree != null && !pending.Contains(tree)) pending.Add(tree);
        }

        public bool IsQueued(Plant tree)
        {
            return pending.Contains(tree);
        }

        public override void MapComponentTick()
        {
            if (pending.Count == 0) return;
            // Emptied before the first fall, so one that throws cannot repeat every tick.
            draining.AddRange(pending);
            pending.Clear();
            for (int i = 0; i < draining.Count; i++)
            {
                Plant tree = draining[i];
                if (tree.Spawned && !tree.Destroyed && tree.Map == map)
                {
                    RM_TreeFallUtility.FellTree(tree, Rot4.Random, RM_TreeFallUtility.FallCause.Cracked);
                }
            }
            draining.Clear();
        }
    }

    /// <summary>Live proof of MIRRELBOLE_FIX_TICK_NRE_THIRTY_FIVE_TIMES, through jawa/static_call
    /// (prove_crackfall_deferred.py). Stage ticks a due RM_Mirrelbole through the real Plant.TickLong; Read asks
    /// whether the fall came after the map ticked.</summary>
    public static class RM_CrackFallProof
    {
        private static Plant tree;

        public static string Stage(string unused)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "UNMEASURED: no current map";
            if (!RM_EnvironmentalHazardsSettings.treeFallEnabled) return "UNMEASURED: treeFallEnabled is off";
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Mirrelbole");
            if (def == null) return "UNMEASURED: RM_Mirrelbole not loaded (needs Greentide)";
            var queue = map.GetComponent<RM_MapComponent_DeferredTreeFall>();
            if (queue == null) return "FAIL: RM_MapComponent_DeferredTreeFall not on the map";
            IntVec3 cell = IntVec3.Invalid;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(map.Center, 40f, true))
            {
                if (c.InBounds(map) && c.Standable(map) && c.GetThingList(map).Count == 0)
                {
                    cell = c;
                    break;
                }
            }
            if (!cell.IsValid) return "UNMEASURED: no clear cell within 40 of the map centre";
            tree = (Plant)GenSpawn.Spawn(def, cell, map);
            tree.Growth = 1f;
            var comp = tree.TryGetComp<RM_CompCrackFall>();
            if (comp == null) return "FAIL: RM_Mirrelbole has no RM_CompCrackFall";
            comp.ForceDueForProof();
            try
            {
                tree.TickLong();
            }
            catch (System.Exception ex)
            {
                return "FAIL: Plant.TickLong threw " + ex.GetType().Name + " with the fall due";
            }
            if (tree.Destroyed) return "FAIL: the tree was destroyed inside its own tick";
            if (!queue.IsQueued(tree)) return "UNMEASURED: the comp did not step (a TickLong prefix took the tick)";
            return "STAGED at " + cell;
        }

        public static string Read(string unused)
        {
            if (tree == null) return "UNMEASURED: nothing staged";
            return "READ felled=" + tree.Destroyed;
        }
    }
}
