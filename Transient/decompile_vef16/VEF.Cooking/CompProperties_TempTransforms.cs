using Verse;

namespace VEF.Cooking;

public class CompProperties_TempTransforms : CompProperties
{
	public float minSafeTemperature;

	public float maxSafeTemperature = 100f;

	public float progressPerDegreePerTick = 1E-05f;

	public string thingToTransformInto = "";

	public bool preserveHp = true;

	public bool keepForbidden = true;

	public bool keepQuality = true;

	public bool keepRottableProgress = true;

	public CompProperties_TempTransforms()
	{
		base.compClass = typeof(CompTempTransforms);
	}
}
