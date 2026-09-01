using Verse;

namespace VEF.Apparels;

public class CompProperties_SwitchApparel : CompProperties
{
	public ThingDef SwitchTo;

	public string Label;

	public string graphicPath = "UI/Gizmo/Switch";

	public CompProperties_SwitchApparel()
	{
		base.compClass = typeof(CompSwitchApparel);
	}
}
