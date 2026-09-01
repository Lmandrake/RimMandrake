using Verse;

namespace VEF.Weapons;

public class Projectile_SmokeGrenade : Projectile_Explosive
{
	private int Burnticks = 5;

	protected override void Tick()
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).Tick();
		Burnticks--;
		if ((Burnticks == 0) & (((Thing)this).Map != null))
		{
			IntVec3 position = ((Thing)this).Position;
			SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 0.3f, ((Thing)this).Map, "Mote_Smoketrail");
			Burnticks = 5;
		}
	}
}
