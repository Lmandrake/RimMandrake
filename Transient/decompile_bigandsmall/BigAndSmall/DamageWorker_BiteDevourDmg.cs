using System;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public class DamageWorker_BiteDevourDmg
{
	[HarmonyPatch(typeof(DamageWorker_AddInjury), "FinalizeAndAddInjury", new Type[]
	{
		typeof(Pawn),
		typeof(Hediff_Injury),
		typeof(DamageInfo),
		typeof(DamageResult)
	})]
	[HarmonyPostfix]
	public static void FinalizeAndAddInjury_Postfix(Pawn pawn, Hediff_Injury injury, DamageInfo dinfo, DamageResult result, DamageWorker_AddInjury __instance)
	{
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_020e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0304: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a3: Unknown result type (might be due to invalid IL or missing references)
		if (!BigSmall.BSGenesActive || !((Def)((DamageInfo)(ref dinfo)).Def).defName.ToLower().Contains("devourdmg"))
		{
			return;
		}
		Thing instigator = ((DamageInfo)(ref dinfo)).Instigator;
		Pawn val = (Pawn)(object)((instigator is Pawn) ? instigator : null);
		if (val == null || val.Dead)
		{
			return;
		}
		RaceProperties raceProps = pawn.RaceProps;
		if (raceProps == null || !raceProps.IsFlesh)
		{
			return;
		}
		float num = pawn.BodySize;
		bool flag = false;
		bool flag2 = Rand.Chance(0.5f) && pawn.Downed;
		if (!pawn.Dead && (pawn.health.ShouldBeDead() || flag2))
		{
			((Thing)pawn).Kill((DamageInfo?)dinfo, (Hediff)null);
			flag = true;
		}
		else if (pawn.Dead)
		{
			flag = true;
		}
		if (flag && pawn != null)
		{
			RaceProperties raceProps2 = pawn.RaceProps;
			if (((raceProps2 != null) ? new bool?(raceProps2.IsMechanoid) : ((bool?)null)) == false && val.BodySize > pawn.BodySize * 2f && Rand.Chance(0.7f))
			{
				Gibblets.SpawnGibblets(pawn, ((Thing)val).Position, ((Thing)val).Map, 10, 20, 1, 3, 1f, 1f, 0.1f, 0.4f);
				object obj;
				if (pawn == null)
				{
					obj = null;
				}
				else
				{
					Pawn_ApparelTracker apparel = pawn.apparel;
					obj = ((apparel != null) ? apparel.WornApparel : null);
				}
				if (obj != null)
				{
					for (int num2 = pawn.apparel.WornApparel.Count - 1; num2 >= 0; num2--)
					{
						((Thing)pawn.apparel.WornApparel[num2]).Destroy((DestroyMode)0);
					}
					pawn.inventory.DropAllNearPawn(((Thing)val).Position, true, false);
				}
				num *= 6f;
				IngestTarget(pawn, val, num);
				Corpse corpse = MakeCorpse_Patch.corpse;
				if (corpse != null && !((Thing)corpse).Destroyed)
				{
					((Thing)MakeCorpse_Patch.corpse).Destroy((DestroyMode)0);
					MakeCorpse_Patch.corpse = null;
				}
				val.stances.stunner.StunFor(100, (Thing)(object)val, true, true, false);
				goto IL_033a;
			}
		}
		if (flag)
		{
			Gibblets.SpawnGibblets(pawn, ((Thing)pawn).Position, ((Thing)val).Map, 7, 18, 1, 1, 1f, 0.7f);
			if (Rand.Chance(Mathf.Clamp((val.BodySize - pawn.BodySize * 0.8f) * 2f / 2f, 0f, 0.4f)))
			{
				Corpse corpse2 = MakeCorpse_Patch.corpse;
				if (corpse2 != null)
				{
					CompRottable val2 = ThingCompUtility.TryGetComp<CompRottable>((Thing)(object)corpse2);
					num *= 5f;
					val.stances.stunner.StunFor(100, (Thing)(object)val, true, true, false);
					Gibblets.SpawnGibblets(pawn, ((Thing)val).Position, ((Thing)val).Map, 7, 30, 1, 2, 1f, 0.7f, 0.1f);
					IngestTarget(pawn, val, num);
					if (!((Thing)corpse2).Destroyed && val2 != null)
					{
						val2.RotProgress = val2.PropsRot.TicksToDessicated + 10;
					}
					goto IL_033a;
				}
			}
			Gibblets.SpawnGibblets(pawn, ((Thing)pawn).Position, ((Thing)val).Map, 7, 18, 1, 1, 1f, 0.7f);
			IngestTarget(pawn, val, num);
		}
		goto IL_033a;
		IL_033a:
		if (!pawn.Dead)
		{
			float maxHealth = ((Hediff)injury).Part.def.GetMaxHealth(pawn);
			num *= ((Hediff)injury).Part?.coverage ?? 0f;
			num *= Mathf.Min(result.totalDamageDealt, maxHealth) / maxHealth;
			if (result.totalDamageDealt > pawn.BodySize * 10f && Rand.Chance(0.1f))
			{
				Gibblets.SpawnGibblets(pawn, ((Thing)pawn).Position, ((Thing)val).Map, 1, 4, 1, 1);
			}
			IngestTarget(pawn, val, num);
		}
	}

	private static void IngestTarget(Pawn target, Pawn eater, float nutritionMax, float maxPercentOfFoodBar = 0.25f)
	{
		if (eater?.needs?.food == null || target == null)
		{
			return;
		}
		Corpse corpse = target.Corpse;
		float num = ((Need)eater.needs.food).MaxLevel * maxPercentOfFoodBar;
		float nutritionWanted = eater.needs.food.NutritionWanted;
		float num2 = Mathf.Min(num, Mathf.Min(nutritionMax, nutritionWanted));
		if (nutritionMax > 0f && target.Dead && corpse != null)
		{
			if (((Thing)target).IngestibleNow)
			{
				Need_Food food = eater.needs.food;
				((Need)food).CurLevel = ((Need)food).CurLevel + ((Thing)target).Ingested(eater, num2);
				return;
			}
			Corpse corpse2 = target.Corpse;
			if (corpse2 != null && ((Thing)corpse2).IngestibleNow)
			{
				Need_Food food2 = eater.needs.food;
				((Need)food2).CurLevel = ((Need)food2).CurLevel + ((Thing)target.Corpse).Ingested(eater, num2);
			}
		}
		else
		{
			if (!(nutritionMax > 0f))
			{
				return;
			}
			ThingDef val = target.RaceProps?.meatDef;
			if (val == null)
			{
				return;
			}
			IngestibleProperties ingestible = val.ingestible;
			float? num3 = ((ingestible != null) ? new float?(ingestible.CachedNutrition) : ((float?)null));
			if (num3.HasValue)
			{
				float valueOrDefault = num3.GetValueOrDefault();
				if (valueOrDefault > 0f)
				{
					Thing val2 = ThingMaker.MakeThing(val, (ThingDef)null);
					val2.stackCount = FoodUtility.StackCountForNutrition(num2, valueOrDefault);
					val2.stackCount = ((val2.stackCount < 1) ? 1 : val2.stackCount);
					Need_Food food3 = eater.needs.food;
					((Need)food3).CurLevel = ((Need)food3).CurLevel + val2.Ingested(eater, num2);
				}
			}
		}
	}
}
