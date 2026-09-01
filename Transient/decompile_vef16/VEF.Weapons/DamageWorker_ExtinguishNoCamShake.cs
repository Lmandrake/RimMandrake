using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Weapons;

public class DamageWorker_ExtinguishNoCamShake : DamageWorker
{
	public override DamageResult Apply(DamageInfo dinfo, Thing victim)
	{
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Expected O, but got Unknown
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Expected O, but got Unknown
		Fire val = (Fire)(object)((victim is Fire) ? victim : null);
		if (val == null || ((Thing)val).Destroyed)
		{
			return new DamageResult();
		}
		((DamageWorker)this).Apply(dinfo, victim);
		val.fireSize -= ((DamageInfo)(ref dinfo)).Amount * 0.01f;
		if (val.fireSize <= 0.1f)
		{
			((Thing)val).Destroy((DestroyMode)0);
		}
		return new DamageResult();
	}

	public override void ExplosionStart(Explosion explosion, List<IntVec3> cellsToAffect)
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		if (base.def.explosionHeatEnergyPerCell > float.Epsilon)
		{
			GenTemperature.PushHeat(((Thing)explosion).Position, ((Thing)explosion).Map, base.def.explosionHeatEnergyPerCell * (float)cellsToAffect.Count);
		}
		FleckMaker.Static(((Thing)explosion).Position, ((Thing)explosion).Map, FleckDefOf.ExplosionFlash, explosion.radius * 6f);
	}
}
