using System;
using System.Linq;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompInitialHediff : ThingComp
{
	private bool addHediffOnce = true;

	private Random rand = new Random();

	public int phase = 1;

	public CompProperties_InitialHediff Props => (CompProperties_InitialHediff)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<bool>(ref addHediffOnce, "addHediffOnce", true, false);
		Scribe_Values.Look<int>(ref phase, "phase", 1, false);
	}

	public override void CompTickRare()
	{
		((ThingComp)this).CompTickRare();
		if (!addHediffOnce)
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (Props.addRandomHediffs)
		{
			int num = (phase = rand.Next(1, Props.numberOfHediffs + 1));
			if (Props.applyToAGivenBodypart)
			{
				BodyPartRecord val2 = val.RaceProps.body.GetPartsWithDef(Props.part).FirstOrDefault();
				val.health.AddHediff(HediffDef.Named(Props.hediffname + num), val2, (DamageInfo?)null, (DamageResult)null);
				Hediff firstHediffOfDef = val.health.hediffSet.GetFirstHediffOfDef(HediffDef.Named(Props.hediffname + num), false);
				firstHediffOfDef.Severity += Props.hediffseverity;
			}
			else
			{
				val.health.AddHediff(HediffDef.Named(Props.hediffname + num), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				Hediff firstHediffOfDef2 = val.health.hediffSet.GetFirstHediffOfDef(HediffDef.Named(Props.hediffname + num), false);
				firstHediffOfDef2.Severity += Props.hediffseverity;
			}
		}
		else if (Props.applyToAGivenBodypart)
		{
			BodyPartRecord val3 = val.RaceProps.body.GetPartsWithDef(Props.part).FirstOrDefault();
			val.health.AddHediff(HediffDef.Named(Props.hediffname), val3, (DamageInfo?)null, (DamageResult)null);
			Hediff firstHediffOfDef3 = val.health.hediffSet.GetFirstHediffOfDef(HediffDef.Named(Props.hediffname), false);
			firstHediffOfDef3.Severity += Props.hediffseverity;
		}
		else
		{
			val.health.AddHediff(HediffDef.Named(Props.hediffname), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			Hediff firstHediffOfDef4 = val.health.hediffSet.GetFirstHediffOfDef(HediffDef.Named(Props.hediffname), false);
			firstHediffOfDef4.Severity += Props.hediffseverity;
		}
		addHediffOnce = false;
	}
}
