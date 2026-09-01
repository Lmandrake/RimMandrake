using System;
using Verse;

namespace BigAndSmall.EventArgs;

public class DefSwappedEventArgs : System.EventArgs
{
	public Pawn Pawn { get; }

	public ThingDef NewDef { get; }

	public ThingDef OldDef { get; }

	public DefSwappedEventArgs(Pawn pawn, ThingDef newDef, ThingDef oldDef)
	{
		Pawn = pawn;
		NewDef = newDef;
		OldDef = oldDef;
	}
}
