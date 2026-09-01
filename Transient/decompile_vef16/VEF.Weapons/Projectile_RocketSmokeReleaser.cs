using Verse;

namespace VEF.Weapons;

public class Projectile_RocketSmokeReleaser : Projectile_Explosive
{
	private int TicksforAppearence = 3;

	private bool JustStarted = true;

	protected override void Tick()
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).Tick();
		TicksforAppearence--;
		IntVec3 position;
		if ((TicksforAppearence == 0) & (((Thing)this).Map != null))
		{
			position = ((Thing)this).Position;
			SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 1f, ((Thing)this).Map, "Mote_Smoketrail");
			TicksforAppearence = 5;
		}
		else if (JustStarted & (((Thing)this).Map != null))
		{
			for (int i = 0; i < 6; i++)
			{
				position = ((Thing)this).Position;
				SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 2f, ((Thing)this).Map, "Mote_Smoketrail");
			}
		}
		if (((Thing)this).Map != null)
		{
			position = ((Thing)this).Position;
			SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 4f, ((Thing)this).Map, "Mote_Firetrail");
		}
	}
}
