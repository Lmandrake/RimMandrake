using Verse;

namespace VEF.Genes;

public class Gene_Ghoul : Gene
{
	public override bool Active
	{
		get
		{
			if (!base.pawn.IsGhoul)
			{
				return false;
			}
			return ((Gene)this).Active;
		}
	}
}
