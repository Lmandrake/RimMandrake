using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class XenotypeDefPatcher
{
	public static void PatchDefs()
	{
		foreach (XenotypeDef item in DefDatabase<XenotypeDef>.AllDefs.Where((XenotypeDef x) => ((Def)x).modExtensions != null && GenCollection.FirstOrDefault<DefModExtension>(((Def)x).modExtensions, (Predicate<DefModExtension>)((DefModExtension y) => y is XenotypeExtension)) != null))
		{
			XenotypeExtension xenotypeExtension = ((Def)item).modExtensions.First((DefModExtension x) => x is XenotypeExtension) as XenotypeExtension;
			if (xenotypeExtension.genePickPriority == null)
			{
				continue;
			}
			foreach (List<string> item2 in xenotypeExtension.genePickPriority)
			{
				foreach (string item3 in item2)
				{
					GeneDef named = DefDatabase<GeneDef>.GetNamed(item3, false);
					if (named != null)
					{
						item.genes.Add(named);
						break;
					}
				}
			}
		}
	}
}
