using RimWorld;
using Verse;

namespace VEF.Weapons;

public class CompProperties_Explosive_Shells : CompProperties_Explosive
{
	public ThingDef shell;

	public IntRange shellCount;

	public IntRange shellDist;

	public CompProperties_Explosive_Shells()
	{
		((CompProperties)this).compClass = typeof(CompExplosive_Shells);
	}
}
