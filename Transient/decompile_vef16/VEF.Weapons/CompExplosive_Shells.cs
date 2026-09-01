using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch]
public class CompExplosive_Shells : CompExplosive
{
	public CompProperties_Explosive_Shells Props => ((ThingComp)this).props as CompProperties_Explosive_Shells;

	public void DetonateExtra(Map map, bool ignoreUnspawned = false)
	{
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Expected O, but got Unknown
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		ThingDef val = Props.shell ?? ThingDefOf.Shell_HighExplosive;
		ThingDef val2 = val?.projectileWhenLoaded ?? val;
		List<Thing> list = new List<Thing>();
		int randomInRange = ((IntRange)(ref Props.shellCount)).RandomInRange;
		while (randomInRange-- > 0)
		{
			Projectile val3 = (Projectile)ThingMaker.MakeThing(val2, (ThingDef)null);
			Rot4 random = Rot4.Random;
			float num = ((Rot4)(ref random)).AsAngle + Rand.Range(-45f, 45f);
			IntVec3 val4 = IntVec3Utility.ToIntVec3(GenThing.TrueCenter((Thing)(object)((ThingComp)this).parent) + Vector3Utility.RotatedBy(Vector3.right * (float)((IntRange)(ref Props.shellDist)).RandomInRange, num) - Gen.RandomHorizontalVector(0.15f));
			CellRect val5 = GenAdj.OccupiedRect((Thing)(object)((ThingComp)this).parent);
			val5 = ((CellRect)(ref val5)).ExpandedBy(1);
			IntVec3 val6 = ((CellRect)(ref val5)).ClosestCellTo(val4);
			GenSpawn.Spawn((Thing)(object)val3, val6, map, random, (WipeMode)0, false, false);
			val3.Launch((Thing)(object)((ThingComp)this).parent, LocalTargetInfo.op_Implicit(val4), LocalTargetInfo.op_Implicit(val4), (ProjectileHitFlags)(-1), false, (Thing)null);
			list.Add((Thing)(object)val3);
		}
		((CompExplosive)this).AddThingsIgnoredByExplosion(list);
	}

	[HarmonyPatch(typeof(CompExplosive), "Detonate")]
	[HarmonyPrefix]
	public static void Detonate_Prefix(CompExplosive __instance, Map map, bool ignoreUnspawned = false)
	{
		if (__instance is CompExplosive_Shells compExplosive_Shells)
		{
			compExplosive_Shells.DetonateExtra(map, ignoreUnspawned);
		}
	}
}
