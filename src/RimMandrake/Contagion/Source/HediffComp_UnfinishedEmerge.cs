using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Contagion
{
    // CONTAGION_GROWN_LIMBS_BUILD_1. Vanilla HediffComp_FleshbeastEmerge is
    // hard-coded to spawn a Fingerspike in the Entities faction, so a grown
    // limb needs its own: removing or replacing the limb surgically spawns
    // RM_TheUnfinished beside the patient as a manhunter, and the existing
    // CompRandomizeUnfinished then rolls that Unfinished's own limbs and
    // lifespan. Copied in shape from HediffComp_FleshbeastEmerge.
    public class HediffCompProperties_UnfinishedEmerge : HediffCompProperties
    {
        public PawnKindDef emergeKind;
        public string letterLabel;
        public string letterText;
        public IntRange stunDuration = new IntRange(120, 240);

        public HediffCompProperties_UnfinishedEmerge()
        {
            compClass = typeof(HediffComp_UnfinishedEmerge);
        }
    }

    public class HediffComp_UnfinishedEmerge : HediffComp
    {
        public HediffCompProperties_UnfinishedEmerge Props => (HediffCompProperties_UnfinishedEmerge)props;

        public override void Notify_SurgicallyRemoved(Pawn surgeon)
        {
            Emerge(surgeon);
        }

        public override void Notify_SurgicallyReplaced(Pawn surgeon)
        {
            Emerge(surgeon);
        }

        private void Emerge(Pawn surgeon)
        {
            Pawn patient = parent.pawn;
            Map map = patient.MapHeld;
            if (map == null || Props.emergeKind == null)
            {
                return;
            }
            Pawn unfinished = PawnGenerator.GeneratePawn(new PawnGenerationRequest(Props.emergeKind, null));
            IntVec3 cell = CellFinder.StandableCellNear(patient.PositionHeld, map, 2f);
            GenSpawn.Spawn(unfinished, cell, map);
            unfinished.stances.stunner.StunFor(Props.stunDuration.RandomInRange, surgeon);
            unfinished.mindState?.mentalStateHandler?.TryStartMentalState(MentalStateDefOf.Manhunter, null, true);
            TaggedString label = Props.letterLabel.Formatted(patient.Named("PAWN"));
            TaggedString text = Props.letterText.Formatted(patient.Named("PAWN"));
            Find.LetterStack.ReceiveLetter(label, text, LetterDefOf.ThreatBig, unfinished);
        }
    }
}
