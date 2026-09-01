using Verse;

namespace VEF.Genes;

public class GeneGendered : Gene
{
	private GeneExtension _extension;

	public GeneExtension Extension => _extension ?? (_extension = ((Def)base.def).GetModExtension<GeneExtension>());

	public override bool Active
	{
		get
		{
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			GeneExtension extension = Extension;
			if (base.pawn != null && extension != null && base.pawn.gender != Extension.forGenderOnly)
			{
				return false;
			}
			return ((Gene)this).Active;
		}
	}
}
