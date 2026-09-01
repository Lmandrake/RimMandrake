using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class CompAbilityEffect_SprayLiquid : CompAbilityEffect
{
	private List<Pair<IntVec3, float>> tmpCellDots = new List<Pair<IntVec3, float>>();

	private List<IntVec3> tmpCells = new List<IntVec3>();

	private CompProperties_AbilitySprayLiquid Props => (CompProperties_AbilitySprayLiquid)(object)((AbilityComp)this).props;

	private Pawn Pawn => ((AbilityComp)this).parent.pawn;

	public ThingDef GetProjectile()
	{
		return Props.GetProjectile(Pawn);
	}

	public int GetRadius()
	{
		return (int)Props.scaling.ApplyScaling(Props.radiusToHit, "AoE", Pawn);
	}

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		ThingDef projectile = GetProjectile();
		foreach (IntVec3 item in AffectedCells(target, null))
		{
			((Projectile)GenSpawn.Spawn(projectile, ((Thing)Pawn).Position, ((Thing)Pawn).Map, (WipeMode)0)).Launch((Thing)(object)Pawn, ((Thing)Pawn).DrawPos, LocalTargetInfo.op_Implicit(item), LocalTargetInfo.op_Implicit(item), (ProjectileHitFlags)1, false, (Thing)null, (ThingDef)null);
		}
		if (Props.sprayEffecter != null)
		{
			Props.sprayEffecter.Spawn(((Thing)((AbilityComp)this).parent.pawn).Position, ((LocalTargetInfo)(ref target)).Cell, ((Thing)((AbilityComp)this).parent.pawn).Map, 1f).Cleanup();
		}
		((CompAbilityEffect)this).Apply(target, dest);
	}

	public override void DrawEffectPreview(LocalTargetInfo target)
	{
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		int num = GetRadius();
		ThingDef projectile = GetProjectile();
		if (projectile != null && projectile.projectile?.explosionRadius > 0f)
		{
			num += Mathf.FloorToInt(projectile.projectile.explosionRadius);
		}
		GenDraw.DrawFieldEdges(AffectedCells(target, num), 2900);
	}

	public override bool AICanTargetNow(LocalTargetInfo target)
	{
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)Pawn).Faction != null)
		{
			int num = GetRadius();
			ThingDef projectile = GetProjectile();
			if (projectile != null && projectile.projectile?.explosionRadius > 0f)
			{
				num += Mathf.FloorToInt(projectile.projectile.explosionRadius);
			}
			foreach (IntVec3 item in AffectedCells(target, num))
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

	protected List<IntVec3> AffectedCells(LocalTargetInfo target, int? radiusOverride = null)
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0122: Unknown result type (might be due to invalid IL or missing references)
		//IL_0127: Unknown result type (might be due to invalid IL or missing references)
		//IL_0129: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_013d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_015c: Unknown result type (might be due to invalid IL or missing references)
		//IL_017a: Unknown result type (might be due to invalid IL or missing references)
		tmpCellDots.Clear();
		tmpCells.Clear();
		tmpCellDots.Add(new Pair<IntVec3, float>(((LocalTargetInfo)(ref target)).Cell, 999f));
		IntVec3 cell = ((LocalTargetInfo)(ref target)).Cell;
		Vector3 val = Vector3Utility.Yto0(((IntVec3)(ref cell)).ToVector3Shifted());
		int num = radiusOverride ?? GetRadius();
		if (num > 0)
		{
			foreach (IntVec3 item in GenRadial.RadialCellsAround(((LocalTargetInfo)(ref target)).Cell, (float)num, true))
			{
				IntVec3 current = item;
				Vector3 val2 = Vector3Utility.Yto0(((IntVec3)(ref current)).ToVector3Shifted()) - val;
				float num2 = Vector3.Dot(((Vector3)(ref val2)).normalized, ((Vector3)(ref val)).normalized);
				tmpCellDots.Add(new Pair<IntVec3, float>(current, num2));
			}
			GenCollection.SortByDescending<Pair<IntVec3, float>, float>(tmpCellDots, (Func<Pair<IntVec3, float>, float>)((Pair<IntVec3, float> x) => x.Second));
		}
		foreach (Pair<IntVec3, float> tmpCellDot in tmpCellDots)
		{
			IntVec3 first = tmpCellDot.First;
			if (GenGrid.InBounds(first, ((Thing)Pawn).Map) && !GridsUtility.Filled(first, ((Thing)Pawn).Map) && GenSight.LineOfSight(((Thing)Pawn).Position, first, ((Thing)Pawn).Map, true, (Func<IntVec3, bool>)null, 0, 0))
			{
				tmpCells.Add(first);
			}
		}
		return tmpCells;
	}
}
