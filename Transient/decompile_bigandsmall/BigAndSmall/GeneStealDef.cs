using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class GeneStealDef : ScorableDef
{
	public List<ScoreKey> selectors = new List<ScoreKey>();

	public List<GeneDef> genes = new List<GeneDef>();

	public override IEnumerable<IScoreProvider> Selectors => selectors;

	public static ScorableDef GetBestGenesOnPawn(Pawn pawn)
	{
		return ScorableDef.GetBestScoredDef<GeneStealDef>(pawn);
	}
}
