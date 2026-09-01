using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Thing), "TakeDamage")]
public class TakeDamagePatch
{
	public static void Prefix(Thing __instance, ref DamageInfo dinfo)
	{
		//IL_0321: Unknown result type (might be due to invalid IL or missing references)
		//IL_0332: Unknown result type (might be due to invalid IL or missing references)
		Pawn val = (Pawn)(object)((__instance is Pawn) ? __instance : null);
		if (val == null || HumanoidPawnScaler.GetCache(val, forceRefresh: false, canRegenerate: true, 30) == null)
		{
			return;
		}
		Thing instigator = ((DamageInfo)(ref dinfo)).Instigator;
		Pawn val2 = (Pawn)(object)((instigator is Pawn) ? instigator : null);
		if (val2 != null && val2.IsShambler)
		{
			Pawn val3 = (Pawn)(object)((__instance is Pawn) ? __instance : null);
			if (val3 != null)
			{
				BSCache cachePrepatched = val3.GetCachePrepatched();
				if (cachePrepatched != null && cachePrepatched.deathlike)
				{
					if (Rand.Chance(0.3f) && ((Thing)val3).Faction != null)
					{
						((Thing)val2).SetFaction(((Thing)val3).Faction, (Pawn)null);
					}
					if (Rand.Chance(0.25f))
					{
						((DamageInfo)(ref dinfo)).SetAmount(((DamageInfo)(ref dinfo)).Amount * 0.05f);
					}
					else if (Rand.Chance(0.8f))
					{
						((DamageInfo)(ref dinfo)).SetAmount(((DamageInfo)(ref dinfo)).Amount * 0.5f);
					}
				}
			}
		}
		DamageDef namedSilentFail = DefDatabase<DamageDef>.GetNamedSilentFail("BombSuper");
		bool num = ((DamageInfo)(ref dinfo)).Def == DamageDefOf.Bullet;
		bool flag = ((DamageInfo)(ref dinfo)).Def == BSDefs.Arrow;
		bool flag2 = ((DamageInfo)(ref dinfo)).Def == DamageDefOf.Stab;
		bool flag3 = ((DamageInfo)(ref dinfo)).Def == DamageDefOf.Blunt;
		bool flag4 = ((DamageInfo)(ref dinfo)).Def == DamageDefOf.Crush;
		bool flag5 = ((DamageInfo)(ref dinfo)).Def == DamageDefOf.Bomb || ((DamageInfo)(ref dinfo)).Def == namedSilentFail;
		bool flag6 = ((DamageInfo)(ref dinfo)).Def == DamageDefOf.ToxGas || ((Def)((DamageInfo)(ref dinfo)).Def).defName.ToLower().Contains("poison") || ((Def)((DamageInfo)(ref dinfo)).Def).defName.ToLower().Contains("tox") || ((Def)((DamageInfo)(ref dinfo)).Def).defName.ToLower().Contains("venom");
		bool flag7 = ((DamageInfo)(ref dinfo)).Def == DamageDefOf.Flame || ((Def)((DamageInfo)(ref dinfo)).Def).defName == "Burn" || ((Def)((DamageInfo)(ref dinfo)).Def).defName == "Fire";
		bool flag8 = ((Def)((DamageInfo)(ref dinfo)).Def).defName.ToLower().Contains("acid") || ((Def)((DamageInfo)(ref dinfo)).Def).defName.ToLower().Contains("corro");
		if (num || flag || flag2)
		{
			StatDef val4 = StatDef.Named("SM_BulletDmgMult");
			float num2 = StatExtension.GetStatValue((Thing)(object)val, val4, true, -1);
			if (flag2)
			{
				num2 = 1f - (1f - num2) / 2f;
			}
			if (num2 != 1f)
			{
				((DamageInfo)(ref dinfo)).SetAmount(((DamageInfo)(ref dinfo)).Amount * num2);
			}
		}
		if (flag3 || flag4 || flag5)
		{
			StatDef val5 = StatDef.Named("SM_ConcussiveDmgMult");
			float num3 = StatExtension.GetStatValue((Thing)(object)val, val5, true, -1);
			if (flag3)
			{
				num3 = 1f - (1f - num3) / 2f;
			}
			if (num3 != 1f)
			{
				((DamageInfo)(ref dinfo)).SetAmount(((DamageInfo)(ref dinfo)).Amount * num3);
			}
		}
		if (flag8)
		{
			StatDef val6 = StatDef.Named("SM_AcidDmgMult");
			float num4 = StatExtension.GetStatValue((Thing)(object)val, val6, true, -1);
			if (flag6)
			{
				num4 = 1f - (1f - num4) / 2f;
			}
			if (num4 != 1f)
			{
				num4 = Mathf.Clamp(num4, 0f, 99f);
				((DamageInfo)(ref dinfo)).SetAmount(((DamageInfo)(ref dinfo)).Amount * num4);
			}
		}
		if (flag7)
		{
			Pawn_GeneTracker genes = val.genes;
			if (((genes != null) ? genes.FactorForDamage(dinfo) : 1f) * val.health.FactorForDamage(dinfo) > 0f && GeneHelpers.GetActiveGenesByName(val, "BS_ReturningSoul").Count() > 0 && val.health.hediffSet.GetFirstHediffOfDef(BSDefs.BS_BurnReturnDenial, false) == null)
			{
				val.health.AddHediff(BSDefs.BS_BurnReturnDenial, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
	}
}
