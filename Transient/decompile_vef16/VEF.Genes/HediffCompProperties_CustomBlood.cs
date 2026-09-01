using RimWorld;
using Verse;

namespace VEF.Genes;

public class HediffCompProperties_CustomBlood : HediffCompProperties
{
	public ThingDef customBloodThingDef;

	public string customBloodIcon = "";

	public EffecterDef customBloodEffect;

	public FleshTypeDef customWoundsFromFleshtype;

	public HediffCompProperties_CustomBlood()
	{
		base.compClass = typeof(HediffComp_CustomBlood);
	}
}
