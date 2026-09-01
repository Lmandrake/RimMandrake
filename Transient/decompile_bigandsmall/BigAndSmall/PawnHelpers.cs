using Verse;

namespace BigAndSmall;

public static class PawnHelpers
{
	public static int GetPawnRNGSeed(this Pawn pawn)
	{
		return ((Thing)pawn).thingIDNumber + ((Def)((Thing)pawn).def).defName.GetHashCode();
	}
}
