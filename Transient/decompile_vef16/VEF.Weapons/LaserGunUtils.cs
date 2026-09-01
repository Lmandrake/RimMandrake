using RimWorld;
using Verse;

namespace VEF.Weapons;

public static class LaserGunUtils
{
	public static bool IsShielded(this Thing thing)
	{
		return ((Pawn)(object)((thing is Pawn) ? thing : null)).IsShielded();
	}

	public static bool IsShielded(this Pawn pawn)
	{
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		if (pawn == null || pawn.apparel == null)
		{
			return false;
		}
		DamageInfo val = default(DamageInfo);
		((DamageInfo)(ref val))._002Ector(DamageDefOf.Bomb, 0f, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false);
		foreach (Apparel item in pawn.apparel.WornApparel)
		{
			if (item.CheckPreAbsorbDamage(val))
			{
				return true;
			}
		}
		return false;
	}
}
