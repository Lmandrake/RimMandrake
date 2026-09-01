using Verse;

namespace VEF.Buildings;

public class ThingAndCount
{
	public ThingDef thing;

	public int count = 1;

	public IntRange randomCount = new IntRange(1, 1);
}
