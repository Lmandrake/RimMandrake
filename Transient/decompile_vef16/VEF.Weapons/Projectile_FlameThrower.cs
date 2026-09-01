using Verse;

namespace VEF.Weapons;

public class Projectile_FlameThrower : Projectile_Explosive
{
	private int TicksforAppearence = 3;

	protected override void Tick()
	{
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).Tick();
		TicksforAppearence--;
		if (TicksforAppearence == 0 && ((Thing)this).Map != null)
		{
			IntVec3 position = ((Thing)this).Position;
			SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 0.7f, ((Thing)this).Map, "Mote_Firetrail");
			TicksforAppearence = 6;
		}
	}
}
