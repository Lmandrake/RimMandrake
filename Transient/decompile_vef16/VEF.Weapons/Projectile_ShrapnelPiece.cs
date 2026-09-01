using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class Projectile_ShrapnelPiece : Bullet
{
	private IntVec3 prevPos;

	public void Launch(Thing launcher, Vector3 origin, Vector3 dest, ThingDef equipmentDef, Thing equipment)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).launcher = launcher;
		((Projectile)this).origin = origin;
		((Projectile)this).destination = dest;
		((Projectile)this).equipmentDef = equipmentDef;
		((Projectile)this).equipment = equipment;
		((Projectile)this).HitFlags = (ProjectileHitFlags)(-1);
		((Projectile)this).ticksToImpact = Mathf.CeilToInt(((Projectile)this).StartingTicksToImpact);
		if (((Projectile)this).ticksToImpact < 1)
		{
			((Projectile)this).ticksToImpact = 1;
		}
	}

	protected override void Tick()
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Invalid comparison between Unknown and I4
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Invalid comparison between Unknown and I4
		IntVec3 val = IntVec3Utility.ToIntVec3(((Projectile)this).ExactPosition);
		if (prevPos != val)
		{
			prevPos = val;
			foreach (Thing thing in GridsUtility.GetThingList(val, ((Thing)this).Map))
			{
				bool flag = ((Projectile)this).CanHit(thing);
				if (flag)
				{
					ThingCategory category = thing.def.category;
					bool flag2 = (((int)category == 1 || (int)category == 3) ? true : false);
					flag = flag2;
				}
				if (flag)
				{
					((Projectile)this).Impact(thing, false);
					return;
				}
			}
		}
		((Projectile)this).Tick();
	}

	public override void ExposeData()
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).ExposeData();
		Scribe_Values.Look<IntVec3>(ref prevPos, "prevPos", default(IntVec3), false);
	}
}
