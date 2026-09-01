using System.Collections.Generic;
using Verse;

namespace VEF.Weapons;

public class CompProperties_WeaponHediffs : CompProperties
{
	public List<HediffDef> hediffs;

	public CompProperties_WeaponHediffs()
	{
		base.compClass = typeof(CompWeaponHediffs);
	}
}
