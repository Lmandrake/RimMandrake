using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public static class GenesFromSpecial
{
	public static List<GeneDef> GetGenesFromAnomalyCreature(Pawn pawn)
	{
		if (GeneStealDef.GetBestGenesOnPawn(pawn) is GeneStealDef geneStealDef)
		{
			return geneStealDef.genes;
		}
		return new List<GeneDef>();
	}
}
