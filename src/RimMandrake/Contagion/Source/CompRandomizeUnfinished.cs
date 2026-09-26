using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_UNFINISHED_SPAWNER_1. Declared directly on RM_TheUnfinished's
    // own ThingDef (this is OUR race, not a donor's, so no patch is needed —
    // contrast CompProperties_SpawnerUnfinished below, which IS patched onto
    // the donor AA_RedGoo). Fires once per pawn at spawn and rolls:
    //
    //   1. A random subset of "attempted limb" Hediff_AddedPart hediffs onto
    //      random un-missing leaf body parts — vanilla's own bionic/prosthetic
    //      mechanism (HediffDef.hediffClass=Hediff_AddedPart,
    //      HediffCompProperties_VerbGiver for the ones that fight back). The
    //      exact pattern the_contagion.md §4 points at ("the pattern the
    //      consumables plunder already found") — verified against the donor
    //      "More Consumables & Mutagens" mod's own UrsaClaws/UrsaHorns
    //      HediffDefs (Hediff_AddedPart + addedPartProps.partEfficiency +
    //      HediffCompProperties_VerbGiver, both vanilla RimWorld classes).
    //   2. A rare "rolled a monster" bonus hediff (owner's ruling: "most are
    //      nuisances, some roll a monster").
    //   3. The days-long lifespan timer (RM_UnfinishedUnraveling) — a plain
    //      vanilla HediffCompProperties_SeverityPerDay ticking to a vanilla
    //      HediffDef.lethalSeverity. Randomised per individual by rolling the
    //      hediff's INITIAL severity here rather than mutating the shared,
    //      def-level CompProperties (which every instance shares).
    public class CompProperties_RandomizeUnfinished : CompProperties
    {
        public List<HediffDef> limbPool;
        public IntRange limbCountRange = new IntRange(1, 3);

        public HediffDef monstrousHediff;
        public float monstrousChance = 0.12f;

        public HediffDef unravelingHediff;
        public FloatRange unravelingInitialSeverityRange = new FloatRange(0f, 0.5f);

        public CompProperties_RandomizeUnfinished()
        {
            compClass = typeof(CompRandomizeUnfinished);
        }
    }

    public class CompRandomizeUnfinished : ThingComp
    {
        private bool rolled;

        private CompProperties_RandomizeUnfinished Props => (CompProperties_RandomizeUnfinished)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref rolled, "rmUnfinishedRolled", false);
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            // A loaded save already carries whatever this pawn rolled at its
            // original spawn — the hediffs themselves Scribe normally as part
            // of ordinary pawn health. Never re-roll on load.
            if (rolled || respawningAfterLoad)
            {
                return;
            }
            rolled = true;

            Pawn pawn = parent as Pawn;
            if (pawn?.health?.hediffSet == null)
            {
                return;
            }

            RollLimbs(pawn);
            RollMonstrous(pawn);
            RollLifespan(pawn);
        }

        private void RollLimbs(Pawn pawn)
        {
            if (Props.limbPool.NullOrEmpty())
            {
                return;
            }

            List<BodyPartRecord> leafParts = pawn.health.hediffSet
                .GetNotMissingParts()
                .Where(p => p.parts.NullOrEmpty())
                .InRandomOrder()
                .ToList();
            List<HediffDef> pool = Props.limbPool.InRandomOrder().ToList();

            int count = Math.Min(Props.limbCountRange.RandomInRange, Math.Min(leafParts.Count, pool.Count));
            for (int i = 0; i < count; i++)
            {
                pawn.health.AddHediff(pool[i], leafParts[i]);
            }
        }

        private void RollMonstrous(Pawn pawn)
        {
            if (Props.monstrousHediff == null || !Rand.Chance(Props.monstrousChance))
            {
                return;
            }
            pawn.health.AddHediff(Props.monstrousHediff);
            Messages.Message(
                "One of the Contagion's Unfinished has budded wrong in a dangerous direction.",
                pawn,
                MessageTypeDefOf.ThreatBig,
                historical: false);
        }

        private void RollLifespan(Pawn pawn)
        {
            if (Props.unravelingHediff == null)
            {
                return;
            }
            Hediff hediff = pawn.health.AddHediff(Props.unravelingHediff);
            if (hediff != null)
            {
                hediff.Severity = Props.unravelingInitialSeverityRange.RandomInRange;
            }
        }
    }
}
