using System.Collections.Generic;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class ProjectileByStat
{
	public class ProjectileAtValue
	{
		public float value;

		public ThingDef def;
	}

	public StatDef stat;

	public List<ProjectileAtValue> projectileAtValue = new List<ProjectileAtValue>();

	public ThingDef GetProjectileByStat(ThingDef previous, Pawn pawn)
	{
		float num = ((stat == null) ? 1f : StatExtension.GetStatValue((Thing)(object)pawn, stat, true, 100));
		ProjectileAtValue projectileAtValue = null;
		foreach (ProjectileAtValue item in this.projectileAtValue)
		{
			if (!(item.value > num) && (projectileAtValue == null || projectileAtValue.value < item.value))
			{
				projectileAtValue = item;
			}
		}
		if (projectileAtValue == null)
		{
			return previous;
		}
		return projectileAtValue.def;
	}
}
