using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.EnvironmentalHazards
{
    //   <ThingDef ParentName="TreeBase">
    //     <defName>RUT_Placeholder_GreentideGiantTree</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_CrackFall">
    //         <mtbDaysAtFullGrowth>8</mtbDaysAtFullGrowth>
    //         <minGrowthFraction>0.9</minGrowthFraction>
    //         <fallDelayTicksRange>300~900</fallDelayTicksRange>
    //       </li>
    //     </comps>
    //   </ThingDef>
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
    // rolling"; >= 0 counts down to the delayed FellTree call.
    public class RM_CompCrackFall : ThingComp
    {
        private int warnTicksRemaining = -1;

        public CompProperties_CrackFall Props => (CompProperties_CrackFall)props;

        public override void CompTickRare()
        {
            base.CompTickRare();

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
                warnTicksRemaining -= 250;
                if (warnTicksRemaining <= 0)
                {
                    RM_TreeFallUtility.FellTree(tree, Rot4.Random, RM_TreeFallUtility.FallCause.Cracked);
                }
                return;
            }

            if (tree.Growth < Props.minGrowthFraction)
            {
                return;
            }

            if (Rand.MTBEventOccurs(EffectiveMtbDays(tree), 60000f, 250f))
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
    }
}
