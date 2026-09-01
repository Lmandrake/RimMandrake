using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class ConditionalManager
{
	/// <summary>
	/// This methods fetches the Gene Extension, which makes it marginally slower than the one which just takes a List of ConditionalStatAffecters.
	/// </summary>
	public static bool TestConditionals(Gene gene, List<PawnExtension> pawnExtensions)
	{
		if (gene == null || gene.def == null)
		{
			return false;
		}
		if (GenList.NullOrEmpty<PawnExtension>((IList<PawnExtension>)pawnExtensions))
		{
			return true;
		}
		_ = gene.def;
		foreach (PawnExtension item in pawnExtensions.Where((PawnExtension x) => x.conditionals != null))
		{
			bool valueOrDefault = item.invert == true;
			if (TestConditionals(gene, item.conditionals))
			{
				if (valueOrDefault)
				{
					return false;
				}
				continue;
			}
			return false;
		}
		return true;
	}

	public static bool TestConditionals(Gene gene, List<ConditionalStatAffecter> conditionalStatEffectors)
	{
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		if (conditionalStatEffectors != null)
		{
			foreach (ConditionalStatAffecter conditionalStatEffector in conditionalStatEffectors)
			{
				StatRequest val = StatRequest.For((Thing)(object)gene.pawn);
				if (!conditionalStatEffector.Applies(val))
				{
					return false;
				}
			}
		}
		return true;
	}

	public static bool TestConditionals(Pawn pawn, List<ConditionalStatAffecter> conditionalStatEffectors)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		if (conditionalStatEffectors != null)
		{
			foreach (ConditionalStatAffecter conditionalStatEffector in conditionalStatEffectors)
			{
				StatRequest val = StatRequest.For((Thing)(object)pawn);
				if (!conditionalStatEffector.Applies(val))
				{
					return false;
				}
			}
		}
		return true;
	}
}
