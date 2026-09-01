using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class DamageWorker_OPToxic : DamageWorker
{
	public override void ExplosionStart(Explosion explosion, List<IntVec3> cellsToAffect)
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		if (base.def.explosionHeatEnergyPerCell > float.Epsilon)
		{
			GenTemperature.PushHeat(((Thing)explosion).Position, ((Thing)explosion).Map, base.def.explosionHeatEnergyPerCell * (float)cellsToAffect.Count);
		}
		FleckMaker.Static(((Thing)explosion).Position, ((Thing)explosion).Map, FleckDefOf.ExplosionFlash, explosion.radius * 6f);
		FleckMaker.Static(((Thing)explosion).Position, ((Thing)explosion).Map, FleckDefOf.ExplosionFlash, explosion.radius * 6f);
		((DamageWorker)this).ExplosionVisualEffectCenter(explosion);
	}

	public override DamageResult Apply(DamageInfo dinfo, Thing victim)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Invalid comparison between Unknown and I4
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		DamageResult val = new DamageResult();
		if ((int)victim.def.category == 1 && victim.def.useHitPoints && ((DamageInfo)(ref dinfo)).Def.harmsHealth)
		{
			bool flag = false;
			Pawn_ApparelTracker apparel = ((Pawn)((victim is Pawn) ? victim : null)).apparel;
			List<Apparel> list = ((apparel != null) ? apparel.WornApparel : null);
			if (list != null && list.Count > 0)
			{
				for (int i = 0; i < list.Count; i++)
				{
					if (((Thing)list[i]).def == ThingDefOf.Apparel_GasMask)
					{
						flag = true;
						Log.Message("gas mask found");
						break;
					}
				}
			}
			if (!flag)
			{
				Log.Message("no gas mask found");
				float amount = ((DamageInfo)(ref dinfo)).Amount;
				val.totalDamageDealt = Mathf.Min(victim.HitPoints, GenMath.RoundRandom(amount));
				victim.HitPoints -= Mathf.RoundToInt(val.totalDamageDealt);
				if (victim.HitPoints <= 0)
				{
					victim.HitPoints = 0;
					victim.Kill((DamageInfo?)dinfo, (Hediff)null);
				}
			}
		}
		return val;
	}
}
