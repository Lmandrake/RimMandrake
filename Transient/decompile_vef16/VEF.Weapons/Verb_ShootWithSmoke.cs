using System.Text;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class Verb_ShootWithSmoke : Verb_Shoot
{
	protected override bool TryCastShot()
	{
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		//IL_013c: Unknown result type (might be due to invalid IL or missing references)
		if (base.TryCastShot())
		{
			ThingDef projectile = VerbUtility.GetProjectile((Verb)(object)this);
			ProjectileProperties projectile2 = projectile.projectile;
			ThingDef val = ((Thing)(((Verb)this).EquipmentSource?)).def;
			if (val == null)
			{
				Log.Error($"Unable to retrieve weapon def from <color=teal>{((object)this).GetType()}</color>. Please report to Oskar or Smash Phil.");
				return true;
			}
			MoteProperties modExtension = ((Def)val).GetModExtension<MoteProperties>();
			if (modExtension == null)
			{
				Log.ErrorOnce($"<color=teal>{((object)this).GetType()}</color> cannot be used without <color=teal>MoteProperties</color> DefModExtension. Motes will not be thrown.", Gen.HashCombine<int>(((object)projectile).GetHashCode(), "MoteProperties".GetHashCode()));
				return true;
			}
			float size = modExtension.Size(projectile2.GetDamageAmount(((Verb)this).caster, (StringBuilder)null));
			for (int i = 0; i < modExtension.numTimesThrown; i++)
			{
				LocalTargetInfo currentTarget = ((Verb)this).CurrentTarget;
				Vector3 centerVector = ((LocalTargetInfo)(ref currentTarget)).CenterVector3;
				IntVec3 val2 = ((Verb)this).Caster.Position;
				Quaternion val3 = Quaternion.LookRotation(centerVector - ((IntVec3)(ref val2)).ToVector3Shifted());
				float y = ((Quaternion)(ref val3)).eulerAngles.y;
				if (modExtension.moteDef != null)
				{
					ThingDef moteDef = modExtension.moteDef;
					val2 = ((Verb)this).caster.PositionHeld;
					SmokeMaker.ThrowMoteDef(moteDef, ((IntVec3)(ref val2)).ToVector3Shifted(), ((Verb)this).caster.MapHeld, size, modExtension.Velocity, y + modExtension.Angle, modExtension.Rotation);
				}
				if (modExtension.fleckDef != null)
				{
					FleckDef fleckDef = modExtension.fleckDef;
					val2 = ((Verb)this).caster.PositionHeld;
					SmokeMaker.ThrowFleckDef(fleckDef, ((IntVec3)(ref val2)).ToVector3Shifted(), ((Verb)this).caster.MapHeld, size, modExtension.Velocity, y + modExtension.Angle, modExtension.Rotation);
				}
			}
			return true;
		}
		return false;
	}
}
