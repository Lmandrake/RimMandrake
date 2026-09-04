using RimWorld;
using Verse;
using Verse.AI;

namespace KoltoTank;

public class FloatMenuOptionProvider_CarryToKoltoTank : FloatMenuOptionProvider
{
    protected override bool Drafted => true;

    protected override bool Undrafted => true;

    protected override bool Multiselect => false;

    protected override bool RequiresManipulation => true;

    protected override FloatMenuOption GetSingleOptionFor(Pawn clickedPawn, FloatMenuContext context)
    {
        if (!clickedPawn.Downed)
        {
            return null;
        }
        if (!context.FirstSelectedPawn.CanReserveAndReach(clickedPawn, PathEndMode.OnCell, Danger.Deadly, 1, -1, null, true))
        {
            return null;
        }
        Building_KoltoTank tank = Building_KoltoTank.FindKoltoTankFor(clickedPawn, context.FirstSelectedPawn, ignoreOtherReservations: true);
        if (tank == null)
        {
            return null;
        }
        string label = "CarryToKoltoTank".Translate(clickedPawn.LabelCap, clickedPawn);
        if (QuestUtility.IsQuestLodger(clickedPawn))
        {
            return FloatMenuUtility.DecoratePrioritizedTask(
                new FloatMenuOption(label + " (" + "CryptosleepCasketGuestsNotAllowed".Translate() + ")", null, MenuOptionPriority.Default, revalidateClickTarget: clickedPawn),
                context.FirstSelectedPawn, clickedPawn, "ReservedBy");
        }
        void Action()
        {
            Building_KoltoTank found = Building_KoltoTank.FindKoltoTankFor(clickedPawn, context.FirstSelectedPawn)
                ?? Building_KoltoTank.FindKoltoTankFor(clickedPawn, context.FirstSelectedPawn, ignoreOtherReservations: true);
            if (found == null || !found.PowerOn || found.HasAnyContents)
            {
                Messages.Message(Translator.Translate("CannotCarryToKoltoTank") + ": " + Translator.Translate("NoAvailableKoltoTank"), clickedPawn, MessageTypeDefOf.RejectInput);
            }
            else
            {
                Job job = JobMaker.MakeJob(Kolto_DefOf.CarryToKoltoTank, clickedPawn, found);
                job.count = 1;
                context.FirstSelectedPawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            }
        }
        return FloatMenuUtility.DecoratePrioritizedTask(
            new FloatMenuOption(label, Action, MenuOptionPriority.Default, revalidateClickTarget: clickedPawn),
            context.FirstSelectedPawn, clickedPawn, "ReservedBy");
    }
}
