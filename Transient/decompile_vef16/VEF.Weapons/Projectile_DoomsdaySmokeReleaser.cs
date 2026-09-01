using RimWorld;
using Verse;

namespace VEF.Weapons;

public class Projectile_DoomsdaySmokeReleaser : Projectile_DoomsdayRocket
{
	private int TicksforAppearence = 3;

	private bool JustStarted = true;

	protected override void Tick()
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		((Projectile)this).Tick();
		TicksforAppearence--;
		IntVec3 position;
		if ((TicksforAppearence == 0) & (((Thing)this).Map != null))
		{
			position = ((Thing)this).Position;
			SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 2.5f, ((Thing)this).Map, "Mote_Smoketrail");
			TicksforAppearence = 3;
		}
		else if (JustStarted & (((Thing)this).Map != null))
		{
			JustStarted = false;
			for (int i = 0; i < 4; i++)
			{
				position = ((Thing)this).Position;
				SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 4f, ((Thing)this).Map, "Mote_Smoketrail");
			}
		}
		if (((Thing)this).Map != null)
		{
			position = ((Thing)this).Position;
			SmokeMaker.ThrowSmokeTrail(((IntVec3)(ref position)).ToVector3Shifted(), 4f, ((Thing)this).Map, "Mote_Firetrail");
		}
	}
}
