using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Plants;

public class Plant_PrefersRockyAndNoFrost : Plant
{
	public const float MinGrowthTemperature = 10f;

	public override float GrowthRate
	{
		get
		{
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			if (((Plant)this).Blighted)
			{
				return 0f;
			}
			if (((Thing)this).Spawned && !PlantUtility.GrowthSeasonNow(((Thing)this).Position, ((Thing)this).Map, ((Thing)this).def))
			{
				return 0f;
			}
			return GrowthRateFactor_Fertility_Inverse * GrowthRateFactor_Temperature_BelowFrost * ((Plant)this).GrowthRateFactor_Light * ((Plant)this).GrowthRateFactor_NoxiousHaze * ((Plant)this).GrowthRateFactor_Drought;
		}
	}

	public float GrowthRateFactor_Temperature_BelowFrost
	{
		get
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			float num = default(float);
			if (!GenTemperature.TryGetTemperatureForCell(((Thing)this).Position, ((Thing)this).Map, ref num))
			{
				return 1f;
			}
			if (num < 20f)
			{
				return Mathf.InverseLerp(10f, 20f, num);
			}
			if (num > 42f)
			{
				return Mathf.InverseLerp(58f, 42f, num);
			}
			return 1f;
		}
	}

	public float GrowthRateFactor_Fertility_Inverse
	{
		get
		{
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			float num = ((Thing)this).Map.fertilityGrid.FertilityAt(((Thing)this).Position);
			if ((double)num <= 0.7)
			{
				return 1f;
			}
			if ((double)num > 0.7 && num <= 1f)
			{
				return 0.6f;
			}
			return 0f;
		}
	}

	public override string GetInspectString()
	{
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Invalid comparison between Unknown and I4
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_017a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Invalid comparison between Unknown and I4
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_0203: Unknown result type (might be due to invalid IL or missing references)
		//IL_020d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_0106: Unknown result type (might be due to invalid IL or missing references)
		//IL_0162: Unknown result type (might be due to invalid IL or missing references)
		//IL_0167: Unknown result type (might be due to invalid IL or missing references)
		//IL_0136: Unknown result type (might be due to invalid IL or missing references)
		StringBuilder stringBuilder = new StringBuilder();
		if (GrowthRateFactor_Fertility_Inverse == 0.6f)
		{
			stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("VCE_StuntedGrowthFertility")));
		}
		else if (GrowthRateFactor_Fertility_Inverse == 0f)
		{
			stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("VCE_StoppedGrowthFertility")));
		}
		if ((int)((Plant)this).LifeStage == 1)
		{
			stringBuilder.AppendLine(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("PercentGrowth", NamedArgument.op_Implicit(((Plant)this).GrowthPercentString))));
			stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("GrowthRate") + ": " + GenText.ToStringPercent(((Plant)this).GrowthRate)));
			if (!((Plant)this).Blighted)
			{
				if (((Plant)this).Resting)
				{
					stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("PlantResting")));
				}
				if (!((Plant)this).HasEnoughLightToGrow)
				{
					stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("PlantNeedsLightLevel") + ": " + GenText.ToStringPercent(((Thing)this).def.plant.growMinGlow)));
				}
				float growthRateFactor_Temperature_BelowFrost = GrowthRateFactor_Temperature_BelowFrost;
				if (growthRateFactor_Temperature_BelowFrost < 0.99f)
				{
					if (growthRateFactor_Temperature_BelowFrost < 0.01f)
					{
						stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("OutOfIdealTemperatureRangeNotGrowing")));
					}
					else
					{
						stringBuilder.AppendLine(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("OutOfIdealTemperatureRange", NamedArgument.op_Implicit(Mathf.RoundToInt(growthRateFactor_Temperature_BelowFrost * 100f).ToString()))));
					}
				}
			}
		}
		else if ((int)((Plant)this).LifeStage == 2)
		{
			if (((Plant)this).HarvestableNow)
			{
				stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("ReadyToHarvest")));
			}
			else
			{
				stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("Mature")));
			}
		}
		if (((Plant)this).DyingBecauseExposedToLight)
		{
			stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("DyingBecauseExposedToLight")));
		}
		if (((Plant)this).Blighted)
		{
			stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("Blighted") + " (" + GenText.ToStringPercent(((Plant)this).Blight.Severity) + ")"));
		}
		string text = ((ThingWithComps)this).InspectStringPartsFromComps();
		if (!GenText.NullOrEmpty(text))
		{
			stringBuilder.Append(text);
		}
		return GenText.TrimEndNewlines(stringBuilder.ToString());
	}
}
