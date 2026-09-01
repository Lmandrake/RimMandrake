using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Genes;

public class GeneExtension : DefModExtension
{
	public class SizeByAge
	{
		public float minOffset;

		public float maxOffset;

		public FloatRange range = new FloatRange(0f, 0f);

		public float GetSize(float? age)
		{
			if (!age.HasValue)
			{
				return 0f;
			}
			return Mathf.Lerp(minOffset, maxOffset, ((FloatRange)(ref range)).InverseLerpThroughRange(age.Value));
		}
	}

	public bool renderCacheOff;

	public string backgroundPathEndogenes;

	public string backgroundPathXenogenes;

	public string backgroundPathArchite;

	public List<HediffToBodyparts> hediffsToBodyParts;

	public HediffDef hediffToWholeBody;

	public bool useSkinColorForFur;

	public bool useSkinAndHairColorsForFur;

	public bool dontColourFur;

	public bool useMaskForFur;

	public bool furHidesBody;

	public ThingSetMakerDef thingSetMaker;

	public bool forceMale;

	public bool forceFemale;

	public Gender forGenderOnly;

	public ThingDef customBloodThingDef;

	public string customBloodIcon = "";

	public EffecterDef customBloodEffect;

	public FleshTypeDef customWoundsFromFleshtype;

	public ThingDef customBloodSmearThingDef;

	public ThingDef customVomitThingDef;

	public EffecterDef customVomitEffect;

	public ThingDef customMeatThingDef;

	public ThingDef customLeatherThingDef;

	public List<ThingDef> defsTreatedAsHumanMeat;

	public List<ThingDef> defsTreatedAsHumanLeather;

	public float diseaseProgressionFactor = 1f;

	public bool hideGene;

	public bool disableGeneExtraction;

	public SkillDef noSkillLoss;

	public SkillDef skillRecreation;

	public float globalSkillLossMultiplier = 1f;

	public bool skillDegradation;

	public float pregnancySpeedFactor = 1f;

	public float foodBingeMentalBreakSelectionChanceFactor = 1f;

	public bool doubleNegativeFoodThought;

	public SizeByAge sizeByAge;

	public Dictionary<LifeStageDef, Vector2> bodyScaleFactorsPerLifestages;

	public BodyTypeDef forcedBodyType;

	public string bodyNakedGraphicPath;

	public string bodyDessicatedGraphicPath;

	public string headDessicatedGraphicPath;

	public string skullGraphicPath;

	public List<GeneDef> applySkinColorWithGenes;

	public float? bodyScaleFactor;

	public float? headScaleFactor;

	public Dictionary<string, List<MoveSpeedFactor>> moveSpeedFactorByTerrainTag;

	public override IEnumerable<string> ConfigErrors()
	{
		if (bodyScaleFactor.HasValue)
		{
			yield return "GeneExtension.bodyScaleFactor is obsoleted and unused, use StatDef VEF_CosmeticBodySize_Multiplier instead.";
		}
		if (headScaleFactor.HasValue)
		{
			yield return "GeneExtension.headScaleFactor is obsoleted and unused, use StatDef VEF_CosmeticBodySize_Multiplier instead.";
		}
	}
}
