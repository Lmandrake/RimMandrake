using System.Collections.Generic;
using Verse;

namespace VEF.Buildings;

public class CompProperties_ThrowMote : CompProperties
{
	public ThingDef mote;

	public int emissionInterval = -1;

	public int moteScale = 1;

	public int solidTime = -1;

	public int fadeOutTime = -1;

	public FloatRange speedRange = new FloatRange(0.6f, 0.75f);

	public FloatRange angleRange = new FloatRange(0f, 360f);

	public FloatRange rotationRange = new FloatRange(-60f, 60f);

	public CompProperties_ThrowMote()
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		base.compClass = typeof(CompThrowMote);
	}

	public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
	{
		if (mote == null)
		{
			yield return "VEF.CompThrowMote must have a mote assigned.";
		}
		if (emissionInterval == -1)
		{
			yield return "VEF.CompThrowMote must have an emissionInterval.";
		}
	}
}
