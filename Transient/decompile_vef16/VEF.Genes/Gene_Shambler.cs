using Verse;

namespace VEF.Genes;

public class Gene_Shambler : Gene
{
	public override bool Active
	{
		get
		{
			Pawn pawn = base.pawn;
			if (pawn == null || !pawn.IsShambler)
			{
				return false;
			}
			return ((Gene)this).Active;
		}
	}
}
