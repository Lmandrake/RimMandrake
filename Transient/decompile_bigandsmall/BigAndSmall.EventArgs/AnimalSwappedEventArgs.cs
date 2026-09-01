using System;
using Verse;

namespace BigAndSmall.EventArgs;

public class AnimalSwappedEventArgs : System.EventArgs
{
	public Pawn OriginalPawn { get; }

	public Pawn NewPawn { get; }

	public AnimalSwappedEventArgs(Pawn originalPawn, Pawn newPawn)
	{
		OriginalPawn = originalPawn;
		NewPawn = newPawn;
	}
}
