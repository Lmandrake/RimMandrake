using RimWorld;
using Verse;

namespace VEF.Weapons;

public class Verb_Shoot : Verb_LaunchProjectile
{
	protected override int ShotsPerBurst => ((Verb)this).verbProps.burstShotCount;

	public override void WarmupComplete()
	{
		((Verb_LaunchProjectile)this).WarmupComplete();
		Thing thing = ((LocalTargetInfo)(ref ((Verb)this).currentTarget)).Thing;
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null && !val.Downed && ((Verb)this).CasterIsPawn && ((Verb)this).CasterPawn.skills != null)
		{
			float num = (GenHostility.HostileTo((Thing)(object)val, ((Verb)this).caster) ? 170f : 20f);
			float num2 = ((Verb)this).verbProps.AdjustedFullCycleTime((Verb)(object)this, ((Verb)this).CasterPawn);
			((Verb)this).CasterPawn.skills.Learn(SkillDefOf.Shooting, num * num2, false, false);
		}
	}

	protected override bool TryCastShot()
	{
		bool num = ((Verb_LaunchProjectile)this).TryCastShot();
		if (num && ((Verb)this).CasterIsPawn)
		{
			((Verb)this).CasterPawn.records.Increment(RecordDefOf.ShotsFired);
		}
		if (num && ((Def)((Thing)((Verb)this).EquipmentSource).def).HasModExtension<HeavyWeapon>())
		{
			HeavyWeapon modExtension = ((Def)((Thing)((Verb)this).EquipmentSource).def).GetModExtension<HeavyWeapon>();
			if (modExtension.weaponHitPointsDeductionOnShot > 0)
			{
				ThingWithComps equipmentSource = ((Verb)this).EquipmentSource;
				((Thing)equipmentSource).HitPoints = ((Thing)equipmentSource).HitPoints - modExtension.weaponHitPointsDeductionOnShot;
				if (((Thing)((Verb)this).EquipmentSource).HitPoints <= 0)
				{
					((Thing)((Verb)this).EquipmentSource).Destroy((DestroyMode)0);
					if (((Verb)this).CasterIsPawn)
					{
						((Verb)this).CasterPawn.jobs.StopAll(false, true);
					}
				}
			}
		}
		return num;
	}
}
