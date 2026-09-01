using System;
using System.Collections.Generic;
using VEF.Things;
using Verse;

namespace VEF.Planet;

public class SiegeParameterSetDef : Def
{
	public ThingDef coverDef;

	public List<string> artilleryBuildingTags;

	public IntRange artilleryCountRange;

	public ThingDef mealDef;

	[Unsaved(false)]
	public List<ThingDef> artilleryDefs = new List<ThingDef>();

	[Unsaved(false)]
	public float lowestArtilleryBlueprintPoints = 2.1474836E+09f;

	[Unsaved(false)]
	public int maxArtilleryConstructionSkill;

	public override void ResolveReferences()
	{
		List<ThingDef> allDefsListForReading = DefDatabase<ThingDef>.AllDefsListForReading;
		for (int i = 0; i < allDefsListForReading.Count; i++)
		{
			ThingDef val = allDefsListForReading[i];
			if (val.building != null && !GenList.NullOrEmpty<string>((IList<string>)val.building.buildingTags) && GenCollection.Any<string>(val.building.buildingTags, (Predicate<string>)((string t) => artilleryBuildingTags.Contains(t))))
			{
				ThingDefExtension modExtension = ((Def)val).GetModExtension<ThingDefExtension>();
				if (modExtension != null && modExtension.siegeBlueprintPoints < lowestArtilleryBlueprintPoints)
				{
					lowestArtilleryBlueprintPoints = modExtension.siegeBlueprintPoints;
				}
				if (((BuildableDef)val).constructionSkillPrerequisite > maxArtilleryConstructionSkill)
				{
					maxArtilleryConstructionSkill = ((BuildableDef)val).constructionSkillPrerequisite;
				}
				if (!artilleryDefs.Contains(val))
				{
					artilleryDefs.Add(val);
				}
			}
		}
	}

	public override IEnumerable<string> ConfigErrors()
	{
		if (coverDef != null && coverDef.size != IntVec2.One)
		{
			yield return $"coverDef must be a 1x1 building. {coverDef}'s size is {coverDef.size.x}x{coverDef.size.z}";
		}
	}
}
