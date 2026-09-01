using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using VEF.Genes;
using Verse;

namespace VEF.AestheticScaling;

public class CachedPawnData : ICacheable
{
	public static bool cacheCanBeRecalculated = true;

	public static CachedPawnData defaultCache = new CachedPawnData();

	public static Dictionary<Pawn, CachedPawnData> cache = new Dictionary<Pawn, CachedPawnData>();

	public Pawn pawn;

	public float totalSize = 1f;

	public float bodySizeOffset;

	public float headPositionMultiplier = 1f;

	public float percentChange = 1f;

	public float quadraticChange = 1f;

	public float cubicChange = 1f;

	public bool renderCacheOff;

	public float bodyRenderSize = 1f;

	public float headRenderSize = 1f;

	public float renderPosOffset;

	public Vector3 vCosmeticScale = Vector3.one;

	public bool isHumanlike;

	public float healthMultiplier = 1f;

	public float foodCapacityMult = 1f;

	public float growthPointMultiplier = 1f;

	public CachedPawnData()
	{
	}//IL_004e: Unknown result type (might be due to invalid IL or missing references)
	//IL_0053: Unknown result type (might be due to invalid IL or missing references)


	public CachedPawnData(Pawn pawn)
	{
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		this.pawn = pawn;
		try
		{
			RaceProperties raceProps = pawn.RaceProps;
			isHumanlike = raceProps != null && raceProps.Humanlike;
		}
		catch
		{
			Log.Error($"[VEF] Error checking Humanlike when setting up {pawn}");
		}
	}

	public static CachedPawnData GetDefaultCache()
	{
		return defaultCache;
	}

	public bool RegenerateCache()
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Invalid comparison between Unknown and I4
		//IL_012f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		//IL_022e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0231: Invalid comparison between Unknown and I4
		//IL_0266: Unknown result type (might be due to invalid IL or missing references)
		//IL_0269: Invalid comparison between Unknown and I4
		//IL_0281: Unknown result type (might be due to invalid IL or missing references)
		//IL_0284: Invalid comparison between Unknown and I4
		//IL_02ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b1: Invalid comparison between Unknown and I4
		//IL_02c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02cc: Invalid comparison between Unknown and I4
		//IL_03b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_03d3: Unknown result type (might be due to invalid IL or missing references)
		if (!cacheCanBeRecalculated || pawn == null)
		{
			return false;
		}
		if ((int)Scribe.mode == 2)
		{
			return false;
		}
		if (pawn.needs == null && !pawn.Dead)
		{
			return false;
		}
		try
		{
			cacheCanBeRecalculated = false;
			List<GeneExtension> list = (from x in (pawn.genes == null) ? new List<Gene>() : pawn.genes.GenesListForReading
				where x.Active && ((Def)x.def).modExtensions != null && GenCollection.Any<DefModExtension>(((Def)x.def).modExtensions, (Predicate<DefModExtension>)((DefModExtension y) => ((object)y).GetType() == typeof(GeneExtension)))
				select ((Def)x.def).GetModExtension<GeneExtension>()).ToList();
			RaceProperties raceProps = pawn.RaceProps;
			isHumanlike = raceProps != null && raceProps.Humanlike;
			LifeStageDef lifestage = pawn.ageTracker.CurLifeStage;
			Vector2 val = default(Vector2);
			((Vector2)(ref val))._002Ector(1f, 1f);
			IEnumerable<GeneExtension> source = list.Where((GeneExtension x) => x.bodyScaleFactorsPerLifestages != null && x.bodyScaleFactorsPerLifestages.ContainsKey(lifestage));
			if (source.Any())
			{
				val = source.Aggregate(val, (Vector2 acc, GeneExtension x) => acc * x.bodyScaleFactorsPerLifestages[lifestage]);
			}
			DevelopmentalStage developmentalStage = pawn.DevelopmentalStage;
			float bodySizeFactor = pawn.ageTracker.CurLifeStage.bodySizeFactor;
			float baseBodySize = pawn.RaceProps.baseBodySize;
			float num = bodySizeFactor * baseBodySize;
			float statValue = StatExtension.GetStatValue((Thing)(object)pawn, VEFDefOf.VEF_BodySize_Offset, true, -1);
			float statValue2 = StatExtension.GetStatValue((Thing)(object)pawn, VEFDefOf.VEF_CosmeticBodySize_Offset, true, -1);
			float num2 = list.Where((GeneExtension x) => x.sizeByAge != null).Sum(delegate(GeneExtension x)
			{
				GeneExtension.SizeByAge sizeByAge = x.sizeByAge;
				Pawn obj = pawn;
				float? age;
				if (obj == null)
				{
					age = null;
				}
				else
				{
					Pawn_AgeTracker ageTracker = obj.ageTracker;
					age = ((ageTracker != null) ? new float?(ageTracker.AgeBiologicalYearsFloat) : ((float?)null));
				}
				return sizeByAge.GetSize(age);
			});
			statValue += num2;
			statValue2 += statValue;
			float statValue3 = StatExtension.GetStatValue((Thing)(object)pawn, VEFDefOf.VEF_BodySize_Multiplier, true, -1);
			float statValue4 = StatExtension.GetStatValue((Thing)(object)pawn, VEFDefOf.VEF_CosmeticBodySize_Multiplier, true, -1);
			float num3 = statValue3 + statValue4 - 1f;
			float num4 = (baseBodySize + statValue) * statValue3 * bodySizeFactor - num;
			float num5 = (baseBodySize + statValue2) * num3 * bodySizeFactor - num;
			float num6 = num4 + num;
			if ((int)developmentalStage < 4)
			{
				num6 = Mathf.Clamp(num6, 0.05f, 0.24f);
			}
			else if ((double)num6 < 0.1)
			{
				num6 = 0.1f;
			}
			if (num6 < 0.05f && (int)developmentalStage < 4)
			{
				num4 = 0f - (num - 0.05f);
			}
			else if (num6 > 0.24f && (int)developmentalStage < 4 && pawn.RaceProps.Humanlike)
			{
				num4 = 0f - (num - 0.24f);
			}
			else if (num6 < 0.1f && (int)developmentalStage == 4)
			{
				num4 = 0f - (num - 0.1f);
			}
			else if (num6 < 0.1f && (int)developmentalStage > 4 && pawn.RaceProps.Humanlike)
			{
				num4 = 0f - (num - 0.1f);
			}
			(float, float, float) tuple = GetPercentChange(num4, pawn);
			float item = tuple.Item1;
			float item2 = tuple.Item2;
			float item3 = tuple.Item3;
			float num7 = GetPercentChange(num5, pawn).Item1;
			if (!pawn.RaceProps.Humanlike)
			{
				num7 = Mathf.Sqrt(num7);
			}
			float statValue5 = StatExtension.GetStatValue((Thing)(object)pawn, VEFDefOf.VEF_HeadSize_Cosmetic, true, -1);
			float statValue6 = StatExtension.GetStatValue((Thing)(object)pawn, VEFDefOf.VEF_PawnRenderPosOffset, true, -1);
			totalSize = num6;
			percentChange = item;
			quadraticChange = item2;
			cubicChange = item3;
			bodySizeOffset = num4;
			bodyRenderSize = GetBodyRenderSize(num7);
			headRenderSize = GetHeadRenderSize(bodyRenderSize) * statValue5;
			vCosmeticScale = new Vector3(bodyRenderSize * val.x, 1f, bodyRenderSize * val.y);
			renderPosOffset = GetYPositionOffset(bodyRenderSize, statValue6);
			renderCacheOff = GenCollection.Any<GeneExtension>(list, (Predicate<GeneExtension>)((GeneExtension x) => x.renderCacheOff));
			healthMultiplier = CalculateHealthMultiplier(item, pawn);
			foodCapacityMult = StatExtension.GetStatValue((Thing)(object)pawn, VEFDefOf.VEF_FoodCapacityMultiplier, true, -1);
			growthPointMultiplier = StatExtension.GetStatValue((Thing)(object)pawn, VEFDefOf.VEF_GrowthPointMultiplier, true, -1);
			CalculateHeadOffset();
		}
		finally
		{
			cacheCanBeRecalculated = true;
		}
		return true;
	}

	private void CalculateHeadOffset()
	{
		float num = Mathf.Lerp(bodyRenderSize, headRenderSize, 0.8f);
		if (num < 1f)
		{
			num = Mathf.Pow(num, 0.96f);
		}
		headPositionMultiplier = num;
	}

	private static (float, float, float) GetPercentChange(float bodySizeOffset, Pawn pawn)
	{
		float num = 0.2f;
		float bodySizeFactor = pawn.ageTracker.CurLifeStage.bodySizeFactor;
		float baseBodySize = pawn.RaceProps.baseBodySize;
		float num2 = bodySizeFactor * baseBodySize;
		float num3 = num2 + bodySizeOffset;
		float num4 = num3 / num2;
		float num5 = Mathf.Pow(num3, 2f) - Mathf.Pow(num2, 2f);
		float num6 = Mathf.Pow(num3, 3f) - Mathf.Pow(num2, 3f);
		num4 = Mathf.Max(num4, 0.04f);
		num5 = Mathf.Max(num5, 0.04f);
		num6 = Mathf.Max(num6, 0.04f);
		if (num4 < num)
		{
			num4 = num;
		}
		return (num4, num5, num6);
	}

	public float GetBodyRenderSize(float size)
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Invalid comparison between Unknown and I4
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Invalid comparison between Unknown and I4
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Invalid comparison between Unknown and I4
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Invalid comparison between Unknown and I4
		if (size == 1f)
		{
			return 1f;
		}
		if (size < 1f)
		{
			size = (((int)pawn.DevelopmentalStage < 4) ? Mathf.Pow(size, 0.95f) : (((int)pawn.DevelopmentalStage >= 8) ? Mathf.Pow(size, 0.75f) : Mathf.Pow(size, 0.9f)));
		}
		else if (size > 1f)
		{
			size = (((int)pawn.DevelopmentalStage < 4) ? Mathf.Pow(size, 0.4f) : (((int)pawn.DevelopmentalStage >= 8) ? Mathf.Pow(size, 0.7f) : Mathf.Pow(size, 0.5f)));
		}
		return size;
	}

	public static float GetHeadRenderSize(float size)
	{
		float num = 0.8f;
		float num2 = 0.65f;
		float num3 = size;
		if (num3 > 1f)
		{
			num3 = Mathf.Pow(size, num);
			return Math.Max(size - 0.5f, num3);
		}
		return Mathf.Pow(size, num2);
	}

	public float GetYPositionOffset(float bodyRenderSize, float offsetFromCache)
	{
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		float num = bodyRenderSize;
		float num2 = num;
		if ((double)num <= 1.0001)
		{
			num = 1f;
		}
		Pawn obj = pawn;
		float num3;
		if (obj != null)
		{
			Pawn_StoryTracker story = obj.story;
			if (story != null)
			{
				BodyTypeDef bodyType = story.bodyType;
				if (bodyType != null)
				{
					_ = bodyType.bodyGraphicScale;
					if (0 == 0)
					{
						num3 = pawn.story.bodyType.bodyGraphicScale.y;
						goto IL_0066;
					}
				}
			}
		}
		num3 = 1f;
		goto IL_0066;
		IL_0066:
		float num4 = num3;
		return (num - 1f) / 2f * (offsetFromCache + 1f) + offsetFromCache * 0.25f * ((num2 < 1f) ? num2 : 1f) * num4;
	}

	private static float CalculateHealthMultiplier(float percentChange, Pawn pawn)
	{
		if (percentChange <= 1f)
		{
			return percentChange;
		}
		float num = 4f;
		float num2 = pawn.RaceProps?.baseHealthScale ?? 1f;
		float num3 = pawn.RaceProps?.baseBodySize ?? 1f;
		float num4 = num2 / num3;
		float num5 = Mathf.Max(4f, num4);
		float num6 = num3;
		float? obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_AgeTracker ageTracker = pawn.ageTracker;
			obj = ((ageTracker == null) ? ((float?)null) : ageTracker.CurLifeStage?.bodySizeFactor);
		}
		float num7 = (num6 * obj) ?? 1f;
		float num8 = Mathf.Clamp01((percentChange * num7 - num7) / num);
		float num9 = Mathf.SmoothStep(num4, num5, num8);
		float num10 = Mathf.Lerp(num4, num5, num8);
		float num11 = Mathf.Lerp(num9, num10, 0.5f) / num4;
		return percentChange * num11;
	}
}
