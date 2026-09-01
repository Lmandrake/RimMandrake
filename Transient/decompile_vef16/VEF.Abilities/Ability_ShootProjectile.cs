using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Abilities;

public class Ability_ShootProjectile : Ability
{
	public override void Cast(params GlobalTargetInfo[] targets)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		base.Cast(targets);
		foreach (GlobalTargetInfo target in targets)
		{
			ShootProjectile(target);
		}
	}

	protected virtual Projectile ShootProjectile(GlobalTargetInfo target)
	{
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0203: Unknown result type (might be due to invalid IL or missing references)
		//IL_0206: Unknown result type (might be due to invalid IL or missing references)
		//IL_020b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0101: Unknown result type (might be due to invalid IL or missing references)
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_0217: Unknown result type (might be due to invalid IL or missing references)
		//IL_0218: Unknown result type (might be due to invalid IL or missing references)
		//IL_021a: Unknown result type (might be due to invalid IL or missing references)
		//IL_021f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0221: Unknown result type (might be due to invalid IL or missing references)
		//IL_0226: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01de: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_019c: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0121: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		//IL_012e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Unknown result type (might be due to invalid IL or missing references)
		//IL_0153: Unknown result type (might be due to invalid IL or missing references)
		//IL_0140: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Unknown result type (might be due to invalid IL or missing references)
		//IL_0158: Unknown result type (might be due to invalid IL or missing references)
		AbilityExtension_Projectile modExtension = ((Def)def).GetModExtension<AbilityExtension_Projectile>();
		Vector3? drawPosHeld = ((Thing)pawn).DrawPosHeld;
		Vector3 val;
		if (!drawPosHeld.HasValue)
		{
			IntVec3 positionHeld = ((Thing)pawn).PositionHeld;
			val = ((IntVec3)(ref positionHeld)).ToVector3Shifted();
		}
		else
		{
			val = drawPosHeld.GetValueOrDefault();
		}
		Vector3 val2 = val;
		IntVec3 positionHeld2 = ((Thing)pawn).PositionHeld;
		Thing obj = GenSpawn.Spawn(modExtension.projectile, positionHeld2, ((Thing)pawn).MapHeld, (WipeMode)0);
		Projectile val3 = (Projectile)(object)((obj is Projectile) ? obj : null);
		if (val3 is AbilityProjectile abilityProjectile)
		{
			abilityProjectile.ability = this;
		}
		CompAbilityProjectile compAbilityProjectile = ((val3 != null) ? ThingCompUtility.TryGetComp<CompAbilityProjectile>((Thing)(object)val3) : null);
		if (compAbilityProjectile != null)
		{
			compAbilityProjectile.ability = this;
		}
		if (modExtension.forcedMissRadius > 0.5f)
		{
			float forcedMissRadius = modExtension.forcedMissRadius;
			if (VerbUtility.CalculateAdjustedForcedMiss(forcedMissRadius, ((GlobalTargetInfo)(ref target)).Cell - base.Caster.Position) > 0.5f)
			{
				int num = GenRadial.NumCellsInRadius(forcedMissRadius);
				IntVec3 val4 = ((GlobalTargetInfo)(ref target)).Cell + GenRadial.RadialPattern[Rand.Range(0, num)];
				if (val4 != ((GlobalTargetInfo)(ref target)).Cell)
				{
					ProjectileHitFlags val5 = (ProjectileHitFlags)4;
					if (Rand.Chance(0.5f))
					{
						val5 = (ProjectileHitFlags)(-1);
					}
					if (val3 != null)
					{
						val3.Launch((Thing)(object)pawn, val2, LocalTargetInfo.op_Implicit(val4), ((GlobalTargetInfo)(ref target)).HasThing ? LocalTargetInfo.op_Implicit(((GlobalTargetInfo)(ref target)).Thing) : LocalTargetInfo.op_Implicit(((GlobalTargetInfo)(ref target)).Cell), val5, false, (Thing)null, (ThingDef)null);
					}
					return val3;
				}
			}
		}
		float num2 = CalculateModifiedStatForPawn(1f, modExtension.accuracyStatFactors, modExtension.accuracyStatOffsets);
		if (Rand.Chance(num2))
		{
			if (((GlobalTargetInfo)(ref target)).HasThing)
			{
				if (val3 != null)
				{
					val3.Launch((Thing)(object)pawn, val2, LocalTargetInfo.op_Implicit(((GlobalTargetInfo)(ref target)).Thing), LocalTargetInfo.op_Implicit(((GlobalTargetInfo)(ref target)).Thing), modExtension.hitFlags, false, (Thing)null, (ThingDef)null);
				}
			}
			else if (val3 != null)
			{
				val3.Launch((Thing)(object)pawn, val2, LocalTargetInfo.op_Implicit(((GlobalTargetInfo)(ref target)).Cell), LocalTargetInfo.op_Implicit(((GlobalTargetInfo)(ref target)).Cell), modExtension.hitFlags, false, (Thing)null, (ThingDef)null);
			}
		}
		else
		{
			ProjectileHitFlags val6 = (ProjectileHitFlags)4;
			IntVec3 val7 = ChangeDestToMissWild(((GlobalTargetInfo)(ref target)).Cell, positionHeld2, num2);
			if (val3 != null)
			{
				val3.Launch((Thing)(object)pawn, val2, LocalTargetInfo.op_Implicit(val7), LocalTargetInfo.op_Implicit(val7), val6, false, (Thing)null, (ThingDef)null);
			}
		}
		return val3;
	}

	public IntVec3 ChangeDestToMissWild(IntVec3 dest, IntVec3 source, float aimOnChance)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		float num = ShootTuning.MissDistanceFromAimOnChanceCurves.Evaluate(aimOnChance, Rand.Value);
		if (num < 0f)
		{
			Log.ErrorOnce("Attempted to wild-miss less than zero tiles away", 94302089);
		}
		Vector3 val = default(Vector3);
		IntVec3 val2;
		IntVec3 val3;
		Vector3 val4;
		do
		{
			Vector2 unitVector = Rand.UnitVector2;
			((Vector3)(ref val))._002Ector(unitVector.x * num, 0f, unitVector.y * num);
			val2 = IntVec3Utility.ToIntVec3(((IntVec3)(ref dest)).ToVector3Shifted() + val);
			val3 = dest - source;
			val4 = ((IntVec3)(ref val3)).ToVector3();
			val3 = val2 - source;
		}
		while (Vector3.Dot(val4, ((IntVec3)(ref val3)).ToVector3()) < 0f);
		return val2;
	}

	public override void CheckCastEffects(GlobalTargetInfo[] targetInfos, out bool cast, out bool target, out bool hediffApply)
	{
		base.CheckCastEffects(targetInfos, out cast, out var _, out var _);
		target = false;
		hediffApply = false;
	}
}
