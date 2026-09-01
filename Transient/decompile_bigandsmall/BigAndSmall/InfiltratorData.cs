using System.Collections.Generic;
using System.Linq;
using BigAndSmall.FilteredLists;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class InfiltratorData
{
	public FilterListSet<FactionDef> factionFilter;

	public List<XenotypeChance> doubleXenotypes = new List<XenotypeChance>();

	public FilterListSet<XenotypeDef> xenoFilter;

	public FilterListSet<ThingDef> thingFilter;

	public bool canFactionSwap = true;

	public bool canSwapXeno;

	public bool disguised;

	public FactionDef ideologyOf;

	public bool canBeFullRaid;

	public bool canOnlyBeFullRaid;

	public float? chanceOverride;

	public float TotalChance => chanceOverride ?? doubleXenotypes.Sum((XenotypeChance x) => x.chance);
}
