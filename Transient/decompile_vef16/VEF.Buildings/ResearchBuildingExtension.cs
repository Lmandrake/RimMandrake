using System.Collections.Generic;
using Verse;

namespace VEF.Buildings;

public class ResearchBuildingExtension : DefModExtension, IMergeable
{
	public List<ThingDef> equivalentBenches;

	public List<ThingDef> equivalentFacilities;

	public float Priority => 0f;

	public void Merge(object extension)
	{
		ResearchBuildingExtension researchBuildingExtension = (ResearchBuildingExtension)extension;
		if (!GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)researchBuildingExtension.equivalentBenches))
		{
			if (equivalentBenches == null)
			{
				equivalentBenches = new List<ThingDef>();
			}
			GenCollection.AddRangeUnique<ThingDef>(equivalentBenches, researchBuildingExtension.equivalentBenches);
		}
		if (!GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)equivalentFacilities))
		{
			if (equivalentFacilities == null)
			{
				equivalentFacilities = new List<ThingDef>();
			}
			GenCollection.AddRangeUnique<ThingDef>(equivalentFacilities, researchBuildingExtension.equivalentFacilities);
		}
	}

	public bool CanMerge(object other)
	{
		if (other != null)
		{
			return other.GetType() == typeof(ResearchBuildingExtension);
		}
		return false;
	}
}
