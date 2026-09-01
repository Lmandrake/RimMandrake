using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Factions;

public class NewFactionSpawningState : WorldComponent
{
	private HashSet<FactionDef> ignoredFactions = new HashSet<FactionDef>();

	public NewFactionSpawningState(World world)
		: base(world)
	{
	}

	public override void ExposeData()
	{
		Scribe_Collections.Look<FactionDef>(ref ignoredFactions, "ignoredFactions", (LookMode)4);
	}

	public void Ignore(FactionDef faction)
	{
		ignoredFactions.Add(faction);
	}

	public void Ignore(IEnumerable<FactionDef> factions)
	{
		GenCollection.AddRange<FactionDef>(ignoredFactions, factions);
	}

	public void ClearIgnored()
	{
		ignoredFactions.Clear();
	}

	public bool IsIgnored(FactionDef faction)
	{
		return ignoredFactions.Contains(faction);
	}
}
