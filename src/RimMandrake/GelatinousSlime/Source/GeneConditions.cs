using RimWorld;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // ════════════════════════════════════════════════════════════════════
    // FORCED CONDITIONS (SLIME_GENE_ARCHIVE_BUILD_1).
    //
    // GeneDef has no native "hunger rate" or "rest fall rate" field of its
    // own — those only live on HediffStage (hungerRateFactor/Offset,
    // restFallFactor/Offset, opinionOfOthersFactor: Source/Verse/
    // HediffStage.cs). Vanilla's own answer to "a gene inflicts a standing
    // biological condition" is a custom Gene subclass that adds/removes a
    // real permanent Hediff — precedent: Gene_ChemicalDependency,
    // Gene_Bloodfeeder, Gene_Clotting (all Source/Verse/Gene_*.cs). This is
    // that subclass, generic over WHICH hediff via a DefModExtension, so the
    // ~17 A/B-list entries whose cost is hunger/rest/opinion can share one
    // mechanism instead of one bespoke class each. Every other gift/cost in
    // this build's gene set is wired through GeneDef's own native fields
    // (statOffsets, statFactors, capMods, aptitudes, disabledWorkTags, the
    // various *ChanceFactor fields) — this class exists only for the
    // handful of effects those fields cannot reach.
    // ════════════════════════════════════════════════════════════════════
    public class RM_ForcedConditionExtension : DefModExtension
    {
        public HediffDef hediff;

        // A3 "Limb regrowth" needs BOTH the forced hunger condition above
        // AND vanilla's own periodic permanent-wound healing (Gene_Healing,
        // Source/Verse/Gene_Healing.cs) — and geneClass is exclusive, so
        // rather than a second Gene subclass this just folds Gene_Healing's
        // own tick-and-call pattern into Gene_ForcesHediff behind a flag.
        public bool alsoHealsPermanentWounds;
    }

    public class Gene_ForcesHediff : Gene
    {
        private static readonly IntRange HealingIntervalTicksRange = new IntRange(900000, 1800000);

        private int ticksToHeal = -1;

        private RM_ForcedConditionExtension Ext
        {
            get { return def.GetModExtension<RM_ForcedConditionExtension>(); }
        }

        public override void PostAdd()
        {
            base.PostAdd();
            RM_ForcedConditionExtension ext = Ext;
            if (ext == null)
            {
                return;
            }
            if (ext.hediff != null && pawn != null && pawn.health != null
                && !pawn.health.hediffSet.HasHediff(ext.hediff))
            {
                pawn.health.AddHediff(ext.hediff);
            }
            if (ext.alsoHealsPermanentWounds)
            {
                ticksToHeal = HealingIntervalTicksRange.RandomInRange;
            }
        }

        public override void PostRemove()
        {
            RM_ForcedConditionExtension ext = Ext;
            if (ext != null && ext.hediff != null && pawn != null && pawn.health != null)
            {
                Hediff existing = pawn.health.hediffSet.GetFirstHediffOfDef(ext.hediff);
                if (existing != null)
                {
                    pawn.health.RemoveHediff(existing);
                }
            }
            base.PostRemove();
        }

        public override void TickInterval(int delta)
        {
            base.TickInterval(delta);
            RM_ForcedConditionExtension ext = Ext;
            if (ext == null || !ext.alsoHealsPermanentWounds || pawn == null)
            {
                return;
            }
            ticksToHeal -= delta;
            if (ticksToHeal <= 0)
            {
                HediffComp_HealPermanentWounds.TryHealRandomPermanentWound(pawn, LabelCap);
                ticksToHeal = HealingIntervalTicksRange.RandomInRange;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ticksToHeal, "ticksToHeal", -1);
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // B25 — THE REEK (owner-commissioned, the_slime_gene_lists.md). "An
    // animated stink-cloud gas visibly emits from you." Reuses the actual
    // vanilla gas system rather than inventing a visual effect:
    // GasType.RotStink is the exact gas a rotting corpse already emits
    // (Source/RimWorld/CompRottable.cs: GasUtility.AddGas(pos, map,
    // GasType.RotStink, amount)), already rendered by the vanilla gas grid
    // and already tied to real mood workers (ThoughtWorker_RotStink,
    // ThoughtWorker_RotStinkLingering). This gene just keeps a small patch
    // of that same gas topped up around the carrier while they are spawned
    // — the same extensibility point (a custom Gene subclass with real
    // per-tick behaviour) vanilla itself uses for Gene_PollutionRush et al.
    // ════════════════════════════════════════════════════════════════════
    public class Gene_TheReek : Gene
    {
        private const int EmitIntervalTicks = 250;
        private const float EmitRadius = 1.5f;

        public override void Tick()
        {
            base.Tick();
            if (!Active || pawn == null || !pawn.Spawned || pawn.Map == null)
            {
                return;
            }
            if (Find.TickManager.TicksGame % EmitIntervalTicks == 0)
            {
                GasUtility.AddGas(pawn.Position, pawn.Map, GasType.RotStink, EmitRadius);
            }
        }
    }
}
