using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class FactionExtension : DefModExtension
{
	public class PawnKindSwap
	{
		public List<string> eventsToSwapPawnKind = new List<string>();

		public List<PawnkindChance> pawnKindSet = new List<PawnkindChance>();

		public bool forcePawnKindIdeology;
	}

	public List<PawnKindSwap> pawnKindSwaps = new List<PawnKindSwap>();
}
