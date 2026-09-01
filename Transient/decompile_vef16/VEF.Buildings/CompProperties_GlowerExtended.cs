using System.Collections.Generic;
using Verse;

namespace VEF.Buildings;

public class CompProperties_GlowerExtended : CompProperties
{
	public List<ColorOption> colorOptions;

	public bool spawnGlowerInFacedCell;

	public CompProperties_GlowerExtended()
	{
		base.compClass = typeof(CompGlowerExtended);
	}
}
