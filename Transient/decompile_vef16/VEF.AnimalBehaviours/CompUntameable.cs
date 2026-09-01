using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompUntameable : ThingComp
{
	public bool externalOverride;

	public CompProperties_Untameable Props => (CompProperties_Untameable)(object)base.props;

	public override void PostExposeData()
	{
		Scribe_Values.Look<bool>(ref externalOverride, "externalOverride", false, true);
	}

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		if (Gen.IsHashIntervalTick((Thing)(object)base.parent, 500, delta) && !externalOverride)
		{
			CheckFaction();
		}
	}

	public void CheckFaction()
	{
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		if (!AnimalBehaviours_Settings.flagUntameable || ((Thing)base.parent).Faction != Faction.OfPlayer)
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (val != null)
		{
			if (Props.goWild)
			{
				((Thing)base.parent).SetFaction((Faction)null, (Pawn)null);
			}
			if (!Props.goesManhunter)
			{
				((Thing)base.parent).SetFaction((Faction)null, (Pawn)null);
			}
			else if (Props.factionToReturnTo == "")
			{
				val.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.ManhunterPermanent, (string)null, false, false, false, (Pawn)null, false, false, false);
			}
			else
			{
				((Thing)base.parent).SetFaction(Find.FactionManager.FirstFactionOfDef(FactionDef.Named(Props.factionToReturnTo)), (Pawn)null);
				val.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.ManhunterPermanent, (string)null, false, false, false, (Pawn)null, false, false, false);
			}
			if (Props.sendMessage)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.message, NamedArgument.op_Implicit(GenText.CapitalizeFirst(GenText.LabelIndefinite(val))))), LookTargets.op_Implicit((Thing)(object)val), MessageTypeDefOf.NegativeEvent, true);
			}
		}
	}
}
