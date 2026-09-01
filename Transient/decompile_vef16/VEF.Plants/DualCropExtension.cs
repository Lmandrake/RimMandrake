using System.Collections.Generic;
using Verse;

namespace VEF.Plants;

public class DualCropExtension : DefModExtension
{
	public ThingDef secondaryOutput;

	public int outPutAmount;

	public bool randomOutput;

	public List<ThingDef> randomSecondaryOutput;
}
