using System.Collections.Generic;
using Verse;

namespace VEF.Weapons;

public class ExpandableBullet : ExpandableProjectile
{
	public override void DoDamage(IntVec3 pos)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		base.DoDamage(pos);
		try
		{
			if (!(pos != ((Projectile)this).launcher.Position) || ((Projectile)this).launcher.Map == null || !GenGrid.InBounds(pos, ((Projectile)this).launcher.Map))
			{
				return;
			}
			List<Thing> list = ((Projectile)this).launcher.Map.thingGrid.ThingsListAt(pos);
			for (int num = list.Count - 1; num >= 0; num--)
			{
				if (IsDamagable(list[num]))
				{
					customImpact = true;
					Impact(list[num]);
					customImpact = false;
				}
			}
		}
		catch
		{
		}
	}
}
