using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class StatWorker_MaxNutritionFromSize : StatWorker
{
	public static FieldRef<StatWorker, Dictionary<Thing, StatCacheEntry>> temporaryCacheDelegate = (FieldRef<StatWorker, Dictionary<Thing, StatCacheEntry>>)(object)AccessTools.FieldRefAccess<Dictionary<Thing, StatCacheEntry>>("RimWorld.StatWorker:temporaryStatCache");

	public void SetTemporaryStatCache(Pawn pawn, float value)
	{
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		Dictionary<Thing, StatCacheEntry> dictionary = temporaryCacheDelegate.Invoke((StatWorker)(object)this);
		if (dictionary != null && !GenDictionary.NullOrEmpty<Thing, StatCacheEntry>(dictionary))
		{
			value = GetNutritionMultiplier(value);
			if (!dictionary.ContainsKey((Thing)(object)pawn))
			{
				dictionary[(Thing)(object)pawn] = new StatCacheEntry(value, Find.TickManager.TicksGame);
				return;
			}
			StatCacheEntry val = dictionary[(Thing)(object)pawn];
			val.statValue = value;
			val.gameTick = Find.TickManager.TicksGame;
		}
	}

	public override float GetValueUnfinalized(StatRequest req, bool applyPostProcess = true)
	{
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Invalid comparison between Unknown and I4
		if (!base.stat.supressDisabledError && Prefs.DevMode && ((StatWorker)this).IsDisabledFor(((StatRequest)(ref req)).Thing))
		{
			Log.ErrorOnce($"Attempted to calculate value for disabled stat {base.stat}; this is meant as a consistency check, either set the stat to neverDisabled or ensure this pawn cannot accidentally use this stat (thing={Gen.ToStringSafe<Thing>(((StatRequest)(ref req)).Thing)})", 75193282 + ((Def)base.stat).index);
		}
		float result = 1f;
		Thing thing = ((StatRequest)(ref req)).Thing;
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(val);
			if (cache != null)
			{
				if ((int)cache.developmentalStage <= 2)
				{
					return 1f;
				}
				return GetNutritionMultiplier(cache.scaleMultiplier.linear);
			}
		}
		return result;
	}

	public static float GetNutritionMultiplier(float scale)
	{
		float num = 1f;
		if (scale > 1f)
		{
			scale = Mathf.Clamp01((scale - 1f) / 3f);
			num *= Mathf.Lerp(1f, 3f, scale);
		}
		else if (scale < 1f)
		{
			num = (num / scale + 1f) / 2f;
		}
		return num;
	}

	public override void FinalizeValue(StatRequest req, ref float val, bool applyPostProcess)
	{
	}
}
