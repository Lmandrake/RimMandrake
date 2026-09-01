using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Plants;

public class Plant_Resistant : Plant
{
	public override float CurrentDyingDamagePerTick
	{
		get
		{
			if (!((Thing)this).Spawned)
			{
				return 0f;
			}
			float num = 0f;
			if (((Thing)this).def.plant.LimitedLifespan && base.ageInt > ((Thing)this).def.plant.LifespanTicks)
			{
				num = Mathf.Max(num, 0.002f);
			}
			if (!((Thing)this).def.plant.cavePlant && ((Thing)this).def.plant.dieIfNoSunlight && base.unlitTicks > 650000)
			{
				num = Mathf.Max(num, 0.002f);
			}
			return num;
		}
	}

	public override void TickLong()
	{
		((Plant)this).TickLong();
		if (((Thing)this).HitPoints < ((Thing)this).MaxHitPoints && ((Plant)this).CurrentDyingDamagePerTick == 0f)
		{
			int hitPoints = ((Thing)this).HitPoints;
			((Thing)this).HitPoints = hitPoints + 1;
		}
	}
}
