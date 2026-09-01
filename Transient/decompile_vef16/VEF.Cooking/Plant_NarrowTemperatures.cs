using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Cooking;

public class Plant_NarrowTemperatures : Plant
{
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
				return 0.1f;
			}
			return ((Plant)this).GrowthRateFactor_Fertility * GrowthRateFactor_TemperatureNarrow * ((Plant)this).GrowthRateFactor_Light;
		}
	}

	public float GrowthRateFactor_TemperatureNarrow
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
				return Mathf.InverseLerp(0f, 20f, num);
			}
			if (num > 30f)
			{
				return Mathf.InverseLerp(50f, 30f, num);
			}
			return 1f;
		}
	}

	public override string GetInspectString()
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Invalid comparison between Unknown and I4
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0138: Invalid comparison between Unknown and I4
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_017e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0160: Unknown result type (might be due to invalid IL or missing references)
		//IL_0148: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_019c: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		StringBuilder stringBuilder = new StringBuilder();
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
				float growthRateFactor_TemperatureNarrow = GrowthRateFactor_TemperatureNarrow;
				if (growthRateFactor_TemperatureNarrow < 0.99f)
				{
					if (growthRateFactor_TemperatureNarrow < 0.01f)
					{
						stringBuilder.AppendLine(TaggedString.op_Implicit(Translator.Translate("OutOfIdealTemperatureRangeNotGrowing")));
					}
					else
					{
						stringBuilder.AppendLine(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("OutOfIdealTemperatureRange", NamedArgument.op_Implicit(Mathf.RoundToInt(growthRateFactor_TemperatureNarrow * 100f).ToString()))));
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
