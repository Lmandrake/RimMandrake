using System;
using Verse;

namespace BigAndSmall;

public class CompRemover : ThingComp
{
	public override void Initialize(CompProperties props)
	{
		((ThingComp)this).Initialize(props);
		if (!(props is CompProperties_CompRemover compProperties_CompRemover))
		{
			return;
		}
		foreach (string compName in compProperties_CompRemover.compNameList)
		{
			ThingComp val = GenCollection.FirstOrDefault<ThingComp>(base.parent.AllComps, (Predicate<ThingComp>)((ThingComp x) => ((object)x).GetType().Name == compName));
			if (val != null)
			{
				base.parent.AllComps.Remove(val);
			}
		}
		foreach (string compName2 in compProperties_CompRemover.compNamespaceList)
		{
			ThingComp val2 = GenCollection.FirstOrDefault<ThingComp>(base.parent.AllComps, (Predicate<ThingComp>)((ThingComp x) => ((object)x).GetType().Namespace == compName2));
			if (val2 != null)
			{
				base.parent.AllComps.Remove(val2);
			}
		}
		foreach (string compName3 in compProperties_CompRemover.compFullNameList)
		{
			ThingComp val3 = GenCollection.FirstOrDefault<ThingComp>(base.parent.AllComps, (Predicate<ThingComp>)((ThingComp x) => ((object)x).GetType().FullName == compName3));
			if (val3 != null)
			{
				base.parent.AllComps.Remove(val3);
			}
		}
	}
}
