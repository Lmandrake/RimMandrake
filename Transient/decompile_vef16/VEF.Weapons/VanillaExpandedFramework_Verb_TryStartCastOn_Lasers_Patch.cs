using System;
using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Verb), "TryStartCastOn", new Type[]
{
	typeof(LocalTargetInfo),
	typeof(LocalTargetInfo),
	typeof(bool),
	typeof(bool),
	typeof(bool),
	typeof(bool)
})]
public static class VanillaExpandedFramework_Verb_TryStartCastOn_Lasers_Patch
{
	[HarmonyPrefix]
	[HarmonyPriority(100)]
	public static void TryStartCastOn_RapidFire_Prefix(ref Verb __instance, LocalTargetInfo castTarg)
	{
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0129: Unknown result type (might be due to invalid IL or missing references)
		//IL_012e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0207: Unknown result type (might be due to invalid IL or missing references)
		//IL_022c: Unknown result type (might be due to invalid IL or missing references)
		//IL_023d: Expected O, but got Unknown
		if (!(((object)__instance).GetType() == typeof(Verb_Shoot)) || __instance.EquipmentSource == null || __instance.CasterPawn == null)
		{
			return;
		}
		Pawn casterPawn = __instance.CasterPawn;
		if (!(castTarg != LocalTargetInfo.op_Implicit((Thing)null)) || !__instance.CanHitTarget(castTarg) || ThingCompUtility.TryGetComp<CompLaserCapacitor>((Thing)(object)__instance.EquipmentSource) == null)
		{
			return;
		}
		CompLaserCapacitor comp = __instance.EquipmentSource.GetComp<CompLaserCapacitor>();
		if (comp == null)
		{
			return;
		}
		if (!comp.initalized)
		{
			comp.originalwarmupTime = __instance.verbProps.warmupTime;
			comp.initalized = true;
		}
		if (comp.hotshot)
		{
			CompEquippable val = ThingCompUtility.TryGetComp<CompEquippable>((Thing)(object)__instance.EquipmentSource);
			if ((IntVec3)comp.lastFiringLocation == ((Thing)casterPawn).Position)
			{
				comp.shotstack++;
				__instance.verbProps.warmupTime = Math.Max(comp.originalwarmupTime - comp.Props.WarmUpReductionPerShot * (float)comp.shotstack, 0f);
			}
			else
			{
				comp.shotstack = 0;
				__instance.verbProps.warmupTime = comp.originalwarmupTime;
			}
			comp.lastFiringLocation = LocalTargetInfo.op_Implicit(((Thing)casterPawn).Position);
			if (!comp.Props.Overheats || __instance.verbProps.warmupTime != 0f)
			{
				return;
			}
			if (Rand.Chance(comp.Props.OverheatChance))
			{
				comp.CriticalOverheatExplosion((Verb_Shoot)(object)__instance);
				if (comp.Props.OverheatDestroys)
				{
					((Thing)((ThingComp)val).parent).Destroy((DestroyMode)0);
				}
			}
			else if (comp.Props.OverheatMoteThrown != null)
			{
				MoteThrown val2 = (MoteThrown)ThingMaker.MakeThing(comp.Props.OverheatMoteThrown, (ThingDef)null);
				((Mote)val2).Scale = Rand.Range(2f, 3f) * comp.Props.OverheatMoteSize;
				((Mote)val2).exactPosition = ((LocalTargetInfo)(ref comp.lastFiringLocation)).CenterVector3;
				((Mote)val2).rotationRate = Rand.Range(-0.5f, 0.5f);
				val2.SetVelocity((float)Rand.Range(30, 40), Rand.Range(0.008f, 0.012f));
				GenSpawn.Spawn((Thing)val2, ((LocalTargetInfo)(ref comp.lastFiringLocation)).Cell, ((Thing)casterPawn).Map, (WipeMode)0);
			}
		}
		else if (comp.originalwarmupTime != 0f)
		{
			__instance.verbProps.warmupTime = comp.originalwarmupTime;
		}
	}

	[HarmonyPostfix]
	[HarmonyPriority(401)]
	public static void TryStartCastOn_RapidFire_Postfix(ref Verb __instance, LocalTargetInfo castTarg, float __state)
	{
		if (((object)__instance).GetType() == typeof(Verb_Shoot) && __instance.EquipmentSource != null && !GenList.NullOrEmpty<ThingComp>((IList<ThingComp>)__instance.EquipmentSource.AllComps) && ThingCompUtility.TryGetComp<CompLaserCapacitor>((Thing)(object)__instance.EquipmentSource) != null)
		{
			CompLaserCapacitor compLaserCapacitor = ThingCompUtility.TryGetComp<CompLaserCapacitor>((Thing)(object)__instance.EquipmentSource);
			if (compLaserCapacitor != null && compLaserCapacitor != null && compLaserCapacitor.initalized)
			{
				__instance.verbProps.warmupTime = compLaserCapacitor.originalwarmupTime;
			}
		}
	}
}
