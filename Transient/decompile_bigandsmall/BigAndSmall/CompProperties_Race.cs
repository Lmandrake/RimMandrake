using Verse;

namespace BigAndSmall;

public class CompProperties_Race : CompProperties_ColorAndFur
{
	public static CompProperties_Race defaultMissingProps = new CompProperties_Race
	{
		canSwapAwayFrom = false
	};

	/// <summary>
	/// If TRUE this will let genes and hediffs change the pawn's race without the force command.
	/// If you want genes that change the body shape to work then this is advised.
	/// </summary>
	public bool canSwapAwayFrom = true;

	public CompProperties_Race()
	{
		((HediffCompProperties)this).compClass = typeof(HediffComp_Race);
	}
}
