using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Apparels;

public class CompApparelHediffs : ThingComp
{
	public Pawn wearer;

	public List<Hediff> wearerHediffs = new List<Hediff>();

	public CompProperties_ApparelHediffs Props => (CompProperties_ApparelHediffs)(object)base.props;

	public override void CompTick()
	{
		((ThingComp)this).CompTick();
		ThingWithComps parent = base.parent;
		Apparel val = (Apparel)(object)((parent is Apparel) ? parent : null);
		if (val == null || val.Wearer == wearer)
		{
			return;
		}
		List<string> hediffDefnames = Props.hediffDefnames;
		if (hediffDefnames != null && hediffDefnames.Count > 0)
		{
			if (wearer != null)
			{
				foreach (Hediff wearerHediff in wearerHediffs)
				{
					wearer.health.hediffSet.hediffs.Remove(wearerHediff);
				}
			}
			if (val.Wearer != null)
			{
				wearerHediffs.Clear();
				foreach (string item in hediffDefnames)
				{
					Hediff val2 = HediffMaker.MakeHediff(HediffDef.Named(item), val.Wearer, (BodyPartRecord)null);
					if (val2 != null)
					{
						val.Wearer.health.AddHediff(val2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
						wearerHediffs.Add(val2);
					}
				}
			}
		}
		wearer = val.Wearer;
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_References.Look<Pawn>(ref wearer, "wearer", false);
		Scribe_Collections.Look<Hediff>(ref wearerHediffs, "wearerHediffs", (LookMode)3, Array.Empty<object>());
	}
}
