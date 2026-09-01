using System.Collections.Generic;
using Verse;

namespace VEF.Buildings;

public class CompProperties_BuildingCalls : CompProperties
{
	public IntRange interval;

	public List<SoundDef> soundDefs;

	public CompProperties_BuildingCalls()
	{
		base.compClass = typeof(CompBuildingCalls);
	}
}
