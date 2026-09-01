using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Genes;

public static class GeneExtensionMethods
{
	public static List<GeneExtension> GetActiveGeneExtensions(this Pawn_GeneTracker geneTracker)
	{
		List<GeneExtension> list = ((geneTracker == null) ? null : (from extension in geneTracker.GenesListForReading?.Select((Gene gene) => ((Def)gene.def).GetModExtension<GeneExtension>())
			where extension != null
			select extension).ToList());
		if (list == null)
		{
			return new List<GeneExtension>();
		}
		return list;
	}
}
