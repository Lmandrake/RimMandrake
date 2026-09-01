using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Weapons;

public class ConditionalStatAffecter_PrimaryVerbLabel : ConditionalStatAffecter
{
	public string explanationLabel;

	public List<string> applicableVerbLabels;

	public override string Label => explanationLabel;

	public override bool Applies(StatRequest req)
	{
		Thing thing = ((StatRequest)(ref req)).Thing;
		ThingWithComps val = (ThingWithComps)(object)((thing is ThingWithComps) ? thing : null);
		if (val == null)
		{
			return false;
		}
		CompEquippable comp = val.GetComp<CompEquippable>();
		if (comp == null)
		{
			return false;
		}
		Verb primaryVerb = comp.PrimaryVerb;
		if (primaryVerb == null)
		{
			return false;
		}
		return IsApplicableVerbs(primaryVerb);
	}

	protected virtual bool IsApplicableVerbs(Verb verb)
	{
		if (applicableVerbLabels != null)
		{
			for (int i = 0; i < applicableVerbLabels.Count; i++)
			{
				if (applicableVerbLabels[i] == verb.verbProps.untranslatedLabel)
				{
					return true;
				}
			}
		}
		return false;
	}
}
