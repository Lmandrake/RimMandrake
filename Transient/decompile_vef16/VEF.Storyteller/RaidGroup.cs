using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace VEF.Storyteller;

public class RaidGroup : IExposable
{
	public HashSet<Pawn> pawns;

	public HashSet<Lord> lords;

	public Faction faction;

	public RaidGroup()
	{
		pawns = new HashSet<Pawn>();
		lords = new HashSet<Lord>();
	}

	public void ExposeData()
	{
		Scribe_Collections.Look<Pawn>(ref pawns, "pawns", (LookMode)3);
		Scribe_Collections.Look<Lord>(ref lords, "lords", (LookMode)3);
		Scribe_References.Look<Faction>(ref faction, "faction", false);
	}
}
