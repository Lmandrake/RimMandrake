using RimWorld;
using Verse;

namespace VEF.Plants;

public class CompProperties_GlowerBlooming : CompProperties_Glower
{
	public CompProperties_GlowerBlooming()
	{
		((CompProperties)this).compClass = typeof(CompGlowerBlooming);
	}
}
