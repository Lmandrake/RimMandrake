using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using Verse;

namespace VEF.Buildings;

public class CompProperties_StatsWhenPowered : CompProperties
{
	public List<StatModifier> poweredStatFactors;

	public List<StatModifier> poweredStatOffsets;

	public List<StatModifier> unpoweredStatFactors;

	public List<StatModifier> unpoweredStatOffsets;

	public bool clearRoomCacheOnPowerChange;

	public List<StatDef> clearStatCacheOnPowerChange;

	public bool onlyWorksIndoors;

	public bool onlyWorksOutdoors;

	public CompProperties_StatsWhenPowered()
	{
		base.compClass = typeof(CompStatsWhenPowered);
	}

	public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
	{
		foreach (string item in _003C_003En__0(parentDef))
		{
			yield return item;
		}
		if (onlyWorksIndoors && onlyWorksOutdoors)
		{
			onlyWorksIndoors = false;
			onlyWorksOutdoors = false;
			yield return string.Format("{0} has {1} with both {2} and {3} set to true. Setting both to false to prevent issues.", ((Def)parentDef).defName, "CompProperties_StatsWhenPowered", onlyWorksIndoors, onlyWorksOutdoors);
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<string> _003C_003En__0(ThingDef parentDef)
	{
		return ((CompProperties)this).ConfigErrors(parentDef);
	}
}
