using Verse;

namespace VEF.Weapons;

public class Projectile_SmokeReleaserMortar : Projectile_Explosive
{
	private int Burnticks = 3;

	private bool JustStarted = true;

	protected override void Tick()
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).Tick();
		Burnticks--;
		IntVec3 position;
		if ((Burnticks == 0) & (((Thing)this).Map != null))
		{
			position = ((Thing)this).Position;
			SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 0.3f, ((Thing)this).Map, "Mote_Smoketrail");
			Burnticks = 3;
		}
		else if (JustStarted & (((Thing)this).Map != null))
		{
			JustStarted = false;
			position = ((Thing)this).Position;
			SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 4f, ((Thing)this).Map, "Mote_Smoketrail");
		}
	}
}
