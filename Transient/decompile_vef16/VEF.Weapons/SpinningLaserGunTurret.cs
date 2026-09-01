using RimWorld;

namespace VEF.Weapons;

internal class SpinningLaserGunTurret : SpinningLaserGunBase
{
	internal Building_LaserGun turret;

	public override void UpdateState()
	{
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Invalid comparison between Unknown and I4
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Invalid comparison between Unknown and I4
		if (turret == null)
		{
			return;
		}
		switch (state)
		{
		case State.Idle:
			if (turret.BurstWarmupTicksLeft > 0)
			{
				state = State.Spinup;
				ReachRotationSpeed(base.def.rotationSpeed, turret.BurstWarmupTicksLeft);
			}
			break;
		case State.Spinup:
			if (turret.BurstWarmupTicksLeft == 0 || (int)((Building_Turret)turret).AttackVerb.state == 1)
			{
				state = State.Spinning;
			}
			break;
		case State.Spinning:
			if ((int)((Building_Turret)turret).AttackVerb.state != 1)
			{
				state = State.Idle;
				int burstCooldownTicksLeft = turret.BurstCooldownTicksLeft;
				ReachRotationSpeed(0f, (burstCooldownTicksLeft == -1) ? 30 : burstCooldownTicksLeft);
			}
			break;
		}
	}
}
