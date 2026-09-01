using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Planet;

public class LordToilData_SiegeCustom : LordToilData_Siege
{
	private List<ThingDef> artilleryBlueprintCountsKeysWorkingList;

	private List<int> artilleryBlueprintCountsValuesWorkingList;

	public Dictionary<ThingDef, int> artilleryCounts = new Dictionary<ThingDef, int>();

	public override void ExposeData()
	{
		((LordToilData_Siege)this).ExposeData();
		Scribe_Collections.Look<ThingDef, int>(ref artilleryCounts, "artilleryBlueprintCounts", (LookMode)4, (LookMode)1, ref artilleryBlueprintCountsKeysWorkingList, ref artilleryBlueprintCountsValuesWorkingList, true, false, false);
	}
}
