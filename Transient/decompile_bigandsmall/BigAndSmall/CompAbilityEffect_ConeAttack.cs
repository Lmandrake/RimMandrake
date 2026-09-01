using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class CompAbilityEffect_ConeAttack : CompAbilityEffect
{
	private CompProperties_AbilityConeAttack Props => (CompProperties_AbilityConeAttack)(object)((AbilityComp)this).props;

	private Pawn Pawn => ((AbilityComp)this).parent.pawn;

	public int GetMaxDistance()
	{
		return (int)Props.scaling.ApplyScaling(Props.maxDistance, "MaxRange", Pawn);
	}

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		ThingDef projectile = Props.GetProjectile(Pawn);
		foreach (IntVec3 item in AffectedCells(target))
		{
			((Projectile)GenSpawn.Spawn(projectile, ((Thing)Pawn).Position, ((Thing)Pawn).Map, (WipeMode)0)).Launch((Thing)(object)Pawn, ((Thing)Pawn).DrawPos, LocalTargetInfo.op_Implicit(item), LocalTargetInfo.op_Implicit(item), (ProjectileHitFlags)1, false, (Thing)null, (ThingDef)null);
		}
		((CompAbilityEffect)this).Apply(target, dest);
	}

	public override void DrawEffectPreview(LocalTargetInfo target)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		GenDraw.DrawFieldEdges(AffectedCells(target), 2900);
	}

	public override bool AICanTargetNow(LocalTargetInfo target)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)Pawn).Faction != null)
		{
			foreach (IntVec3 item in AffectedCells(target))
			{
				List<Thing> thingList = GridsUtility.GetThingList(item, ((Thing)Pawn).Map);
				for (int i = 0; i < thingList.Count; i++)
				{
					if (thingList[i].Faction == ((Thing)Pawn).Faction)
					{
						return false;
					}
				}
			}
		}
		return true;
	}

	private List<IntVec3> AffectedCells(LocalTargetInfo target)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		//IL_012c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0131: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_013b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0140: Unknown result type (might be due to invalid IL or missing references)
		//IL_0141: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Unknown result type (might be due to invalid IL or missing references)
		//IL_0151: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_0153: Unknown result type (might be due to invalid IL or missing references)
		//IL_0167: Unknown result type (might be due to invalid IL or missing references)
		//IL_0168: Unknown result type (might be due to invalid IL or missing references)
		//IL_016d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_018d: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01df: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0204: Unknown result type (might be due to invalid IL or missing references)
		//IL_0210: Unknown result type (might be due to invalid IL or missing references)
		//IL_0215: Unknown result type (might be due to invalid IL or missing references)
		//IL_0235: Unknown result type (might be due to invalid IL or missing references)
		//IL_0242: Unknown result type (might be due to invalid IL or missing references)
		List<IntVec3> list = new List<IntVec3>();
		IntVec3 val = ((LocalTargetInfo)(ref target)).Cell;
		Vector3 val2 = ((IntVec3)(ref val)).ToVector3Shifted();
		val = ((Thing)Pawn).Position;
		Vector3 val3 = ((IntVec3)(ref val)).ToVector3Shifted();
		Vector3 val4 = val3;
		Vector3 val5 = val2 - val3;
		if (((Vector3)(ref val5)).magnitude < (float)GetMaxDistance())
		{
			Vector3 val6 = val3;
			val5 = val2 - val3;
			val2 = val6 + ((Vector3)(ref val5)).normalized * (float)Props.minDistnace;
		}
		val5 = val2 - val3;
		if (((Vector3)(ref val5)).magnitude > (float)Props.maxConeLength)
		{
			Vector3 val7 = val2;
			val5 = val2 - val3;
			val3 = val7 - ((Vector3)(ref val5)).normalized * (float)Props.maxConeLength;
		}
		val5 = val2 - val3;
		float magnitude = ((Vector3)(ref val5)).magnitude;
		val5 = val2 - val4;
		float num = ((Vector3)(ref val5)).magnitude / (float)Props.maxDistance;
		float num2 = Mathf.Lerp((float)Props.maxAngle, (float)Props.minAngle, num);
		foreach (IntVec3 item in GenRadial.RadialCellsAround(IntVec3Utility.ToIntVec3(val3), magnitude, true))
		{
			IntVec3 current = item;
			val5 = ((IntVec3)(ref current)).ToVector3Shifted() - val3;
			Vector3 normalized = ((Vector3)(ref val5)).normalized;
			val5 = val2 - val3;
			_ = ((Vector3)(ref val5)).magnitude;
			if (Vector3.Angle(normalized, val2 - val3) <= num2 / 2f && GenSight.LineOfSight(IntVec3Utility.ToIntVec3(val3), current, ((Thing)Pawn).Map, true, (Func<IntVec3, bool>)null, 0, 0) && !((IntVec3)(ref current)).Equals(((Thing)Pawn).Position))
			{
				list.Add(current);
			}
		}
		foreach (IntVec3 item2 in GenRadial.RadialCellsAround(((LocalTargetInfo)(ref target)).Cell, (float)Props.minimumRadiusAroundTarget, true))
		{
			IntVec3 current2 = item2;
			val5 = ((IntVec3)(ref current2)).ToVector3Shifted() - val2;
			_ = ((Vector3)(ref val5)).normalized;
			val5 = val2 - val3;
			_ = ((Vector3)(ref val5)).magnitude;
			if (GenSight.LineOfSight(((LocalTargetInfo)(ref target)).Cell, current2, ((Thing)Pawn).Map, true, (Func<IntVec3, bool>)null, 0, 0) && !((IntVec3)(ref current2)).Equals(((Thing)Pawn).Position))
			{
				list.Add(current2);
			}
		}
		return list.Distinct().ToList();
	}
}
