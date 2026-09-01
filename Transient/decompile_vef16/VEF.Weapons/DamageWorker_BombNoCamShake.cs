using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Weapons;

public class DamageWorker_BombNoCamShake : DamageWorker_AddInjury
{
	public override void ExplosionStart(Explosion explosion, List<IntVec3> cellsToAffect)
	{
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		if (((DamageWorker)this).def.explosionHeatEnergyPerCell > float.Epsilon)
		{
			GenTemperature.PushHeat(((Thing)explosion).Position, ((Thing)explosion).Map, ((DamageWorker)this).def.explosionHeatEnergyPerCell * (float)cellsToAffect.Count);
		}
		FleckMaker.Static(((Thing)explosion).Position, ((Thing)explosion).Map, FleckDefOf.ExplosionFlash, explosion.radius * 6f);
	}
}
