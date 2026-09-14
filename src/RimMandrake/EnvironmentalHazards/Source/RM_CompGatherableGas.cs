using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FORGE_MECHANICS_1 F2 spike (forge_kit_spec.md "the tibanna harvest").
    // Generic body-gas tap: crib of RimWorld/CompMilkable.cs and
    // RimWorld/CompShearable.cs (both verified, decompile) — both are thin
    // CompHasGatherableBodyResource subclasses that override only the four
    // abstract accessors (GatherResourcesIntervalDays / ResourceAmount /
    // ResourceDef / SaveKey), Active for their own gate, and
    // CompInspectStringExtra for a "growth so far" line. Vanilla owns the
    // whole job/gizmo/WorkGiver pipeline off CompHasGatherableBodyResource —
    // RimWorld/WorkGiver_GatherAnimalBodyResources.cs and
    // RimWorld/JobDriver_GatherAnimalBodyResources.cs — so this comp needs
    // no bespoke job/gizmo code of its own; only the strings are RM_-generic
    // rather than tibanna-specific (the concrete gas ThingDef and the
    // beldon PawnKindDef wiring are XML, later, per the kit spec's own
    // scoping — "attached by XML to the beldon kinds").
    //
    // Sex-independent per the spec ("a sex-independent gate"): unlike
    // CompMilkable's milkFemaleOnly + CurLifeStage.milkable gate, this
    // comp's Active adds no gender/life-stage check beyond base.Active
    // (Faction != null && !Suspended) and the Anomaly shambler check both
    // vanilla siblings already carry.
    public class CompProperties_GatherableGas : CompProperties
    {
        /// <summary>Days per full gather cycle. INVENTED, F2 spec default:
        /// 2 (tibanna tap interval).</summary>
        public int gatherIntervalDays = 2;

        /// <summary>Amount yielded at full fullness. INVENTED, F2 spec
        /// default: 12 (tibanna gas per tap).</summary>
        public int gatherAmount = 12;

        /// <summary>What comes out of the tap. Null here — the concrete
        /// RUT_TibannaGas wiring is the full build's XML, not this spike.</summary>
        public ThingDef gatherDef;

        /// <summary>Translate key for the CompInspectStringExtra line
        /// ("tibanna pressure" in the concrete build). Falls back to the
        /// literal key text if untranslated, same as this mod's other RM_
        /// comps (RM_CompResourceCondenser, RM_CompGatherableCalmGated).</summary>
        public string fullnessLabelKey = "RM_GasPressure";

        public CompProperties_GatherableGas()
        {
            compClass = typeof(RM_CompGatherableGas);
        }
    }

    public class RM_CompGatherableGas : CompHasGatherableBodyResource
    {
        protected override int GatherResourcesIntervalDays => Props.gatherIntervalDays;
        protected override int ResourceAmount => Props.gatherAmount;
        protected override ThingDef ResourceDef => Props.gatherDef;
        protected override string SaveKey => "gasFullness";

        public CompProperties_GatherableGas Props => (CompProperties_GatherableGas)props;

        protected override bool Active
        {
            get
            {
                if (!base.Active)
                {
                    return false;
                }
                // No gender/life-stage gate here — sex-independent by design
                // (the spec's own line), unlike CompMilkable's
                // milkFemaleOnly + CurLifeStage.milkable checks.
                if (ModsConfig.AnomalyActive && parent is Pawn pawn && pawn.IsShambler)
                {
                    return false;
                }
                return true;
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!Active)
            {
                return null;
            }
            return Props.fullnessLabelKey.Translate() + ": " + base.Fullness.ToStringPercent();
        }
    }
}
