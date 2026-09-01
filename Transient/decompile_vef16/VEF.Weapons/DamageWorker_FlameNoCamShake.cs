using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Weapons;

public class DamageWorker_FlameNoCamShake : DamageWorker_AddInjury
{
	public override DamageResult Apply(DamageInfo dinfo, Thing victim)
	{
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
		Pawn val = (Pawn)(object)((victim is Pawn) ? victim : null);
		if (val != null && ((Thing)val).Faction == Faction.OfPlayer)
		{
			Find.TickManager.slower.SignalForceNormalSpeedShort();
		}
		Map map = victim.Map;
		DamageResult val2 = ((DamageWorker_AddInjury)this).Apply(dinfo, victim);
		if (!val2.deflected && !((DamageInfo)(ref dinfo)).InstantPermanentInjury)
		{
			FireUtility.TryAttachFire(victim, Rand.Range(0.15f, 0.25f), (Thing)null);
		}
		if (victim.Destroyed && map != null && val == null)
		{
			CellRect val3 = GenAdj.OccupiedRect(victim);
			Enumerator enumerator = ((CellRect)(ref val3)).GetEnumerator();
			try
			{
				while (((Enumerator)(ref enumerator)).MoveNext())
				{
					FilthMaker.TryMakeFilth(((Enumerator)(ref enumerator)).Current, map, ThingDefOf.Filth_Ash, 1, (FilthSourceFlags)0, true);
				}
			}
			finally
			{
				((IDisposable)(Enumerator)(ref enumerator)/*cast due to .constrained prefix*/).Dispose();
			}
			Plant val4 = (Plant)(object)((victim is Plant) ? victim : null);
			if (val4 != null && victim.def.plant.IsTree && victim.def != InternalDefOf.BurnedTree)
			{
				((Plant)(DeadPlant)GenSpawn.Spawn(InternalDefOf.BurnedTree, victim.Position, map, (WipeMode)0)).Growth = val4.Growth;
			}
		}
		return val2;
	}

	public override void ExplosionAffectCell(Explosion explosion, IntVec3 c, List<Thing> damagedThings, List<Thing> ignoredThings, bool canThrowMotes)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		((DamageWorker)this).ExplosionAffectCell(explosion, c, damagedThings, ignoredThings, canThrowMotes);
		if (((DamageWorker)this).def == DamageDefOf.Flame && Rand.Chance(FireUtility.ChanceToStartFireIn(c, ((Thing)explosion).Map, (SimpleCurve)null)))
		{
			FireUtility.TryStartFireIn(c, ((Thing)explosion).Map, Rand.Range(0.2f, 0.6f), (Thing)null, (SimpleCurve)null);
		}
	}

	public override void ExplosionStart(Explosion explosion, List<IntVec3> cellsToAffect)
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		if (((DamageWorker)this).def.explosionHeatEnergyPerCell > float.Epsilon)
		{
			GenTemperature.PushHeat(((Thing)explosion).Position, ((Thing)explosion).Map, ((DamageWorker)this).def.explosionHeatEnergyPerCell * (float)cellsToAffect.Count);
		}
		FleckMaker.Static(((Thing)explosion).Position, ((Thing)explosion).Map, FleckDefOf.ExplosionFlash, explosion.radius * 6f);
	}
}
