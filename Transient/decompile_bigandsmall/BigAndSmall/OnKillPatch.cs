using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Pawn), "Kill", new Type[]
{
	typeof(DamageInfo),
	typeof(Hediff)
})]
public static class OnKillPatch
{
	[HarmonyPostfix]
	public static void OnKillPostfix(Pawn __instance, DamageInfo? dinfo, Hediff exactCulprit)
	{
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		if (ModsConfig.IsActive("RedMattis.Undead") || ModsConfig.IsActive("RedMattis.Yokai") || ModsConfig.IsActive("RedMattis.Undead.ZombieApoc"))
		{
			ReturnedReanimation(__instance, 60000);
		}
		object obj;
		if (!dinfo.HasValue)
		{
			obj = null;
		}
		else
		{
			DamageInfo valueOrDefault = dinfo.GetValueOrDefault();
			obj = ((DamageInfo)(ref valueOrDefault)).Instigator;
		}
		Pawn val = (Pawn)((obj is Pawn) ? obj : null);
		if (val == null || __instance == null)
		{
			return;
		}
		Corpse val2 = ((MakeCorpse_Patch.corpse != null && MakeCorpse_Patch.corpse.InnerPawn == __instance) ? MakeCorpse_Patch.corpse : null);
		IntVec3? val3 = ((val2 != null) ? new IntVec3?(((Thing)val2).Position) : ((val != null) ? new IntVec3?(((Thing)val).Position) : ((IntVec3?)null)));
		if (!val3.HasValue || (((val2 != null && ((Thing)val2).Spawned) || (__instance != null && ((Thing)__instance).Spawned)) && IntVec3Utility.DistanceTo(((Thing)val).Position, val3.Value) > 2f))
		{
			return;
		}
		IEnumerable<SiphonSoul> enumerable = from x in val.GetAllPawnExtensions()
			select x.siphonSoul into x
			where x != null && x.type == SiphonType.KillingBlow
			select x;
		if (!enumerable.Any())
		{
			return;
		}
		SiphonSoul parms = enumerable.FuseAll(SiphonType.KillingBlow);
		Soul.GetOrAddSoulCollector(val).AddPawnSoul(__instance, parms);
		if (__instance != null)
		{
			RaceProperties raceProps = __instance.RaceProps;
			if (((raceProps != null) ? new bool?(raceProps.Humanlike) : ((bool?)null)) == true)
			{
				CompAbilityEffect_ConsumeSoul.ApplySoulless(__instance);
			}
		}
	}

	private static void ReturnedReanimation(Pawn __instance, int ticksPerDay)
	{
		Corpse val = null;
		if (MakeCorpse_Patch.corpse != null)
		{
			val = MakeCorpse_Patch.corpse;
		}
		if (((__instance != null) ? __instance.RaceProps : null) == null || val == null || __instance.IsUndead())
		{
			return;
		}
		if (__instance != null)
		{
			Pawn_HealthTracker health = __instance.health;
			bool? obj;
			if (health == null)
			{
				obj = null;
			}
			else
			{
				HediffSet hediffSet = health.hediffSet;
				Hediff val2 = default(Hediff);
				obj = ((hediffSet != null) ? new bool?(hediffSet.TryGetHediff(BSDefs.BS_Soulless, ref val2)) : ((bool?)null));
			}
			bool? flag = obj;
			if (flag == true)
			{
				return;
			}
		}
		float num = VUReturning.ZombieApocalypseChance;
		float num2 = VUReturning.DeadRisingChance;
		if (BSDefs.VU_Returned == null || BigSmallMod.settings.preventUndead)
		{
			num = 0f;
			num2 = 0f;
		}
		Map targetMap = ((Thing)__instance).Map ?? ((Thing)val).Map;
		if (!__instance.RaceProps.Humanlike && !VUReturning.zombieApocalypseMode)
		{
			return;
		}
		if (Find.TickManager.TicksGame - VUReturning.lastCheckTick > ticksPerDay)
		{
			if (Rand.Chance(num))
			{
				VUReturning.lastCheckTick = Find.TickManager.TicksGame + ticksPerDay * 2;
				VUReturning.zombieApocalypseMode = true;
				TriggerZombieApocalypse(targetMap);
			}
			else if (Rand.Chance(num2))
			{
				VUReturning.deadRisingMode = true;
				VUReturning.zombieApocalypseMode = false;
				VUReturning.lastCheckTick = Find.TickManager.TicksGame;
			}
			else
			{
				VUReturning.deadRisingMode = false;
				VUReturning.zombieApocalypseMode = false;
				VUReturning.lastCheckTick = Find.TickManager.TicksGame;
			}
		}
		if (!__instance.health.hediffSet.HasHediff(HediffDef.Named("BS_ReturnedReanimation"), false) && (__instance.RaceProps.FleshType == FleshTypeDefOf.Normal || __instance.RaceProps.FleshType == FleshTypeDefOf.Insectoid))
		{
			if (VUReturning.zombieApocalypseMode && Rand.Chance(VUReturning.ReturnChanceApoc))
			{
				Hediff val3 = HediffMaker.MakeHediff(HediffDef.Named("BS_ReturnedReanimation"), __instance, (BodyPartRecord)null);
				__instance.health.AddHediff(val3, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
			else if (VUReturning.deadRisingMode && Rand.Chance(VUReturning.ReturnChance))
			{
				Hediff val4 = HediffMaker.MakeHediff(HediffDef.Named("BS_ReturnedReanimation"), __instance, (BodyPartRecord)null);
				__instance.health.AddHediff(val4, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
			if (((Thing)__instance).Faction == Faction.OfPlayerSilentFail && (ModsConfig.IsActive("RedMattis.Undead") || ModsConfig.IsActive("RedMattis.Undead.ZombieApoc")) && !BigSmallMod.settings.preventUndead && Rand.Chance(VUReturning.ReturnChanceColonist))
			{
				Hediff val5 = HediffMaker.MakeHediff(HediffDef.Named("BS_ReturnedReanimation"), __instance, (BodyPartRecord)null);
				__instance.health.AddHediff(val5, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
	}

	public static void TriggerZombieApocalypse(Map targetMap, bool sendMessage = true)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		if (sendMessage)
		{
			Messages.Message(TaggedString.op_Implicit(Translator.Translate("BS_ZombieApocalypse")), MessageTypeDefOf.ThreatSmall, true);
		}
		if (targetMap?.listerThings == null)
		{
			return;
		}
		foreach (Corpse item in from Corpse x in targetMap.listerThings.ThingsInGroup((ThingRequestGroup)8)
			where !RottableUtility.IsDessicated((Thing)(object)x) && x.InnerPawn.RaceProps.IsFlesh && !x.InnerPawn.IsUndead()
			select x)
		{
			if (Rand.Chance(VUReturning.ReturnChanceApoc / 2f))
			{
				Hediff val = HediffMaker.MakeHediff(HediffDef.Named("BS_ReturnedReanimation"), item.InnerPawn, (BodyPartRecord)null);
				item.InnerPawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
	}
}
