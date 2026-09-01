using Verse;

namespace VEF.Weapons;

public class Verb_MakeshiftShoot : Verb_ShootWithSmoke
{
	protected override int ShotsPerBurst
	{
		get
		{
			ThingDef projectile = VerbUtility.GetProjectile((Verb)(object)this);
			ThingDef val = ((Thing)(((Verb)this).EquipmentSource?)).def;
			if (val == null)
			{
				Log.Error($"Unable to retrieve weapon def from <color=teal>{((object)this).GetType()}</color>. Please report to Oskar or Smash Phil.");
				return base.ShotsPerBurst;
			}
			MakeshiftProperties modExtension = ((Def)val).GetModExtension<MakeshiftProperties>();
			if (modExtension == null)
			{
				Log.ErrorOnce($"<color=teal>{((object)this).GetType()}</color> cannot be used without <color=teal>MakeshiftProperties</color> DefModExtension. Motes will not be thrown.", Gen.HashCombine<int>(((object)projectile).GetHashCode(), "MakeshiftProperties".GetHashCode()));
				return base.ShotsPerBurst;
			}
			return ((IntRange)(ref modExtension.shots)).RandomInRange;
		}
	}

	public override bool TryStartCastOn(LocalTargetInfo castTarg, LocalTargetInfo destTarg, bool surpriseAttack = false, bool canHitNonTargetPawns = true, bool preventFriendlyFire = false, bool nonInterruptingSelfCast = false)
	{
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Expected O, but got Unknown
		if (((Verb)this).ShotsPerBurst <= 0)
		{
			((Verb)this).ticksToNextBurstShot = ((Verb)this).verbProps.ticksBetweenBurstShots;
			if (((Verb)this).CasterIsPawn && !((Verb)this).verbProps.nonInterruptingSelfCast)
			{
				((Verb)this).CasterPawn.stances.SetStance((Stance)new Stance_Cooldown(((Verb)this).verbProps.ticksBetweenBurstShots + 1, ((Verb)this).currentTarget, (Verb)(object)this));
			}
			return false;
		}
		return ((Verb)this).TryStartCastOn(castTarg, destTarg, surpriseAttack, canHitNonTargetPawns, preventFriendlyFire, nonInterruptingSelfCast);
	}
}
