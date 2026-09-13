using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F8 spike (fever_wood_kit_spec.md). Thornbugs:
    // nectar for safety, fear dries the yield — "a thornbug yields only
    // while it feels safe; a frightened herd dries up for days... every
    // raid costs nectar before it costs blood" (the_fever_wood.md §4);
    // hard ban §6.6: "Thornbugs never yield under fear."
    //
    // CORRECTION to the kit spec, found by re-verifying against the live
    // 1.6 decompile rather than assuming the spec's own plan: the spec's
    // "Gathered() override yields ZERO below a calm floor" is NOT buildable
    // as written. RimWorld/CompHasGatherableBodyResource.cs's Gathered(Pawn)
    // is a plain `public void` method — not virtual, not abstract — so no
    // subclass can override it. The real, and better, seam is `Active`
    // (`protected virtual bool Active`, same file): CompTick only accrues
    // fullness while Active; ActiveAndFull (Active && fullness >= 1f) is
    // the ONLY gate both vanilla callers use —
    // RimWorld/WorkGiver_GatherAnimalBodyResources.cs (ShouldSkip,
    // HasJobOnThing) and RimWorld/JobDriver_GatherAnimalBodyResources.cs
    // (its AddEndCondition literally reads `ActiveAndFull ? Ongoing :
    // Incompletable`, aborting an in-progress gather the instant it turns
    // false). A repo-wide grep of the decompile for ".Gathered(" turns up
    // exactly one call site — the JobDriver above — so gating Active
    // satisfies "regardless of caller" for every vanilla-reachable path,
    // not just a best-effort guard. This is exactly the precedent
    // RimWorld/CompMilkable.cs already sets (its own Active override adds
    // milkFemaleOnly/life-stage/shambler gates on top of base.Active) —
    // the calm gate below follows that same, real, shipped pattern rather
    // than the spec's unbuildable one.
    //
    // Fear source: rather than inventing a bespoke "recent combat" signal
    // (the spec's own ❓), this reuses Map.dangerWatcher.DangerRating —
    // a real, cheap, already-ticking per-map signal
    // (Verse/Map.cs field `dangerWatcher`, RimWorld/DangerWatcher.cs) that
    // already aggregates hostile-threat presence and a recent-harm timer
    // (Notify_ColonistHarmedExternally / lastColonistHarmedTick). Combined
    // with a direct hostile-pawn-in-radius scan (card 3, ruled: ~40 cells)
    // for the "a far-side raid does not dry a sheltered herd" placement
    // rule the owner ruled on.
    public class CompProperties_GatherableCalmGated : CompProperties
    {
        public int gatherIntervalDays = 2;
        public int gatherAmount = 25;
        public ThingDef gatherDef;

        /// <summary>Card 3, ruled 2026-09-12: fear radius as drafted (~40
        /// cells). A hostile pawn within this radius of the thornbug drops
        /// calm; a raid on the far side of a sprawling map does not dry a
        /// sheltered herd.</summary>
        public float fearRadius = 40f;

        /// <summary>Ban §6.6's floor: below this calm, Active (and so
        /// ActiveAndFull, and so every vanilla gather path) returns false.
        /// INVENTED, kit spec default.</summary>
        public float calmFloor = 0.3f;

        /// <summary>Ticks for calm to recover fully from 0 once no fear
        /// source remains. INVENTED, kit spec default: 4 days.</summary>
        public int calmRecoveryTicks = 60000 * 4;

        public CompProperties_GatherableCalmGated()
        {
            compClass = typeof(RM_CompGatherableCalmGated);
        }
    }

    public class RM_CompGatherableCalmGated : CompHasGatherableBodyResource
    {
        private const int FearScanIntervalTicks = 250;

        private float calm = 1f;

        protected override int GatherResourcesIntervalDays => Props.gatherIntervalDays;
        protected override int ResourceAmount => Props.gatherAmount;
        protected override ThingDef ResourceDef => Props.gatherDef;
        protected override string SaveKey => "calmGatedFullness";

        public CompProperties_GatherableCalmGated Props => (CompProperties_GatherableCalmGated)props;

        public float Calm => calm;

        // The enforcement point (see class header): below the calm floor,
        // Active is false, which vanilla's own gather machinery already
        // treats as "nothing to gather here" everywhere it looks.
        protected override bool Active
        {
            get
            {
                if (!base.Active)
                {
                    return false;
                }
                return calm >= Props.calmFloor;
            }
        }

        public override void CompTick()
        {
            base.CompTick(); // accrues fullness only while Active — frozen while scared, per §4 "dries up"

            if (Find.TickManager.TicksGame % FearScanIntervalTicks != 0)
            {
                return;
            }

            bool feared = IsFeared();
            if (feared)
            {
                calm = 0f;
            }
            else if (calm < 1f)
            {
                float recoveryPerTick = 1f / Props.calmRecoveryTicks;
                calm = Mathf.Clamp01(calm + recoveryPerTick * FearScanIntervalTicks);
            }
        }

        private bool IsFeared()
        {
            Map map = parent.Map;
            if (map == null)
            {
                return false;
            }
            // Map-level signal: a raid this hostile is already alarming
            // the whole map's story danger, not just this pawn's own
            // neighborhood.
            if (map.dangerWatcher != null && map.dangerWatcher.DangerRating == StoryDanger.High)
            {
                return true;
            }
            // Card 3: local hostile presence within the ruled ~40-cell
            // radius — sheltered herds on the far side of a raid stay calm.
            float radiusSq = Props.fearRadius * Props.fearRadius;
            var hostiles = map.attackTargetsCache?.TargetsHostileToColony;
            if (hostiles == null)
            {
                return false;
            }
            foreach (IAttackTarget t in hostiles)
            {
                if (t?.Thing == null)
                {
                    continue;
                }
                if ((t.Thing.Position - parent.Position).LengthHorizontalSquared <= radiusSq)
                {
                    return true;
                }
            }
            return false;
        }

        public override string CompInspectStringExtra()
        {
            if (!base.Active)
            {
                return null;
            }
            string calmLine = "RUT_ThornbugCalm".Translate() + ": " + calm.ToStringPercent();
            if (calm < Props.calmFloor)
            {
                calmLine += " (" + "RUT_ThornbugDry".Translate() + ")";
            }
            return calmLine;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref calm, "calm", 1f);
        }
    }
}
