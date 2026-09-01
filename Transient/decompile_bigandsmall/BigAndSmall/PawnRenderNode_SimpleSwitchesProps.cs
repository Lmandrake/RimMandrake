using RimWorld;
using Verse;

namespace BigAndSmall;

/// <summary>
/// This class is essentially a greatly simplified version of UltimateRenderNode, etc, for some common "switch my thing's graphic out if" rules.
///
/// Complex Rendernode supports these properties. The Ultimate one does not, it has its own more powerful system.
///
/// The main purpose of this node is to make it easier to just copy-paste add/patch compatibility for wings, tails, etc.
///
/// If the pawn doesn't have the part at all it won't disable the node, so this only works on pawns that have the part. The
/// reason for this is to avoid hiding wings from mods like "Sarg's Alpha Genes" that render wings but don't actually add them to the pawn.
/// </summary>
public class PawnRenderNode_SimpleSwitchesProps : PawnRenderNodeProperties
{
	public class DisableIfWing
	{
		public bool bionic;

		public bool bionicLeft;

		public bool bionicRight;

		public bool missingTwo;

		public bool missingLeft;

		public bool missingRight;

		public bool ShouldDisable(Pawn pawn)
		{
			if ((!missingTwo || GraphicsHelper.GetPartsWithHediff(pawn, 1, BSDefs.BS_Wing, HediffDefOf.MissingBodyPart, null) <= 1) && (!missingLeft || GraphicsHelper.GetPartsWithHediff(pawn, 1, BSDefs.BS_Wing, HediffDefOf.MissingBodyPart, true) <= 0) && (!missingRight || GraphicsHelper.GetPartsWithHediff(pawn, 1, BSDefs.BS_Wing, HediffDefOf.MissingBodyPart, false) <= 0) && (!bionic || GraphicsHelper.GetPartsReplaced(pawn, 1, BSDefs.BS_Wing, null) <= 0) && (!bionicLeft || GraphicsHelper.GetPartsReplaced(pawn, 1, BSDefs.BS_Wing, true) <= 0))
			{
				if (bionicRight)
				{
					return GraphicsHelper.GetPartsReplaced(pawn, 1, BSDefs.BS_Wing, false) > 0;
				}
				return false;
			}
			return true;
		}
	}

	public class DisableIfTail
	{
		public bool missing;

		public bool bionic;

		public bool ShouldDisable(Pawn pawn)
		{
			if (!missing || GraphicsHelper.GetPartsWithHediff(pawn, 1, BSDefs.Tail, HediffDefOf.MissingBodyPart, null) <= 0)
			{
				if (bionic)
				{
					return GraphicsHelper.GetPartsReplaced(pawn, 1, BSDefs.Tail, null) > 0;
				}
				return false;
			}
			return true;
		}
	}

	public DisableIfWing disableIfWing;

	public DisableIfTail disableIfTail;

	public bool ShouldDisable(Pawn pawn)
	{
		DisableIfWing obj = disableIfWing;
		if (obj == null || !obj.ShouldDisable(pawn))
		{
			return disableIfTail?.ShouldDisable(pawn) ?? false;
		}
		return true;
	}
}
