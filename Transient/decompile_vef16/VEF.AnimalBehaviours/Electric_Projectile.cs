using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class Electric_Projectile : Projectile
{
	protected override void Impact(Thing hitThing, bool blockedByShield = false)
	{
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Expected O, but got Unknown
		//IL_013b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_0168: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0125: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Expected O, but got Unknown
		Map map = ((Thing)this).Map;
		((Projectile)this).Impact(hitThing, false);
		BattleLogEntry_RangedImpact val = new BattleLogEntry_RangedImpact(base.launcher, hitThing, ((LocalTargetInfo)(ref base.intendedTarget)).Thing, InternalDefOf.Gun_Autopistol, ((Thing)this).def, base.targetCoverDef);
		Find.BattleLog.Add((LogEntry)(object)val);
		if (hitThing != null)
		{
			DamageDef damageDef = ((Thing)this).def.projectile.damageDef;
			float num = ((Projectile)this).DamageAmount;
			float armorPenetration = ((Projectile)this).ArmorPenetration;
			Quaternion exactRotation = ((Projectile)this).ExactRotation;
			float y = ((Quaternion)(ref exactRotation)).eulerAngles.y;
			Thing launcher = base.launcher;
			_ = base.equipmentDef;
			DamageInfo val2 = default(DamageInfo);
			((DamageInfo)(ref val2))._002Ector(damageDef, num, armorPenetration, y, launcher, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, ((LocalTargetInfo)(ref base.intendedTarget)).Thing, true, true, (QualityCategory)2, true, false);
			hitThing.TakeDamage(val2).AssociateWithLog((LogEntry_DamageResult)(object)val);
			Pawn val3 = (Pawn)(object)((hitThing is Pawn) ? hitThing : null);
			if (val3 != null && val3.stances != null && val3.BodySize <= ((Thing)this).def.projectile.stoppingPower + 0.001f)
			{
				val3.stances.stagger.StaggerFor(95, 0.17f);
			}
			if (map != null && hitThing != null)
			{
				map.weatherManager.eventHandler.AddEvent((WeatherEvent)new WeatherEvent_LightningStrike(map, hitThing.Position));
			}
		}
		else
		{
			SoundStarter.PlayOneShot(SoundDefOf.BulletImpact_Ground, SoundInfo.op_Implicit(new TargetInfo(((Thing)this).Position, map, false)));
			FleckMaker.Static(((Projectile)this).ExactPosition, map, FleckDefOf.ShotHit_Dirt, 1f);
			if (GridsUtility.GetTerrain(((Thing)this).Position, map).takeSplashes)
			{
				FleckMaker.WaterSplash(((Projectile)this).ExactPosition, map, Mathf.Sqrt((float)((Projectile)this).DamageAmount) * 1f, 4f);
			}
		}
	}
}
