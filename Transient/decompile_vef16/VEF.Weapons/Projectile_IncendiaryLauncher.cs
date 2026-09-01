using Verse;

namespace VEF.Weapons;

public class Projectile_IncendiaryLauncher : Projectile_Explosive
{
	private int TicksforAppearence = 3;

	private bool JustStarted = true;

	protected override void Tick()
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).Tick();
		TicksforAppearence--;
		IntVec3 position;
		if ((TicksforAppearence == 0) & (((Thing)this).Map != null))
		{
			position = ((Thing)this).Position;
			SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 1f, ((Thing)this).Map, "Mote_Firetrail");
			TicksforAppearence = 5;
		}
		else if (JustStarted & (((Thing)this).Map != null))
		{
			JustStarted = false;
			position = ((Thing)this).Position;
			SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 1f, ((Thing)this).Map, "Mote_Firetrail");
		}
		if (((Thing)this).Map != null)
		{
			position = ((Thing)this).Position;
			SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 4f, ((Thing)this).Map, "Mote_Firetrail");
		}
	}
}
