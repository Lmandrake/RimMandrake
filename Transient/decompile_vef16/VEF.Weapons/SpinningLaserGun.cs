using Verse;

namespace VEF.Weapons;

internal class SpinningLaserGun : SpinningLaserGunBase
{
	private bool IsBrusting(Pawn pawn)
	{
		if (pawn.CurrentEffectiveVerb == null)
		{
			return false;
		}
		return pawn.CurrentEffectiveVerb.Bursting;
	}

	public override void UpdateState()
	{
		IThingHolder parentHolder = ((Thing)this).ParentHolder;
		Pawn_EquipmentTracker val = (Pawn_EquipmentTracker)(object)((parentHolder is Pawn_EquipmentTracker) ? parentHolder : null);
		if (val == null)
		{
			return;
		}
		Stance curStance = val.pawn.stances.curStance;
		switch (state)
		{
		case State.Idle:
		{
			Stance_Warmup val3 = (Stance_Warmup)(object)((curStance is Stance_Warmup) ? curStance : null);
			if (val3 != null)
			{
				state = State.Spinup;
				ReachRotationSpeed(base.def.rotationSpeed, ((Stance_Busy)val3).ticksLeft);
			}
			break;
		}
		case State.Spinup:
		{
			if (IsBrusting(val.pawn))
			{
				state = State.Spinning;
				break;
			}
			Stance_Warmup val3 = (Stance_Warmup)(object)((curStance is Stance_Warmup) ? curStance : null);
			if (val3 == null)
			{
				state = State.Idle;
				ReachRotationSpeed(0f, 30);
			}
			break;
		}
		case State.Spinning:
			if (!IsBrusting(val.pawn))
			{
				state = State.Idle;
				Stance_Cooldown val2 = (Stance_Cooldown)(object)((curStance is Stance_Cooldown) ? curStance : null);
				if (val2 != null)
				{
					ReachRotationSpeed(0f, ((Stance_Busy)val2).ticksLeft);
				}
				else
				{
					ReachRotationSpeed(0f, 0);
				}
			}
			break;
		}
	}
}
