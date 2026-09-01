using Verse;

namespace VEF.Hediffs;

public class HediffCompProperties_Mote : HediffCompProperties
{
	public ThingDef mote;

	public float scale;

	public HediffCompProperties_Mote()
	{
		base.compClass = typeof(HediffComp_Mote);
	}
}
