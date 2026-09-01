using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public class DraculStageExtension : DefModExtension
{
	public int draculStage;

	public int durationDays;

	public static (int stage, Gene draculGene) TryGetDraculStage(Pawn pawn)
	{
		IEnumerable<Gene> source = from x in pawn.GetAllActiveGenes()
			where ((Def)x.def).HasModExtension<DraculStageExtension>()
			select x;
		if (source.Count() == 1)
		{
			try
			{
				return (stage: ((Def)source.First().def).GetModExtension<DraculStageExtension>().draculStage, draculGene: source.First());
			}
			catch
			{
				return (stage: 3, draculGene: null);
			}
		}
		return (stage: 3, draculGene: null);
	}
}
