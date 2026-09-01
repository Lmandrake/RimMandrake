using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[StaticConstructorOnStartup]
public class CompGraphicByStyle : ThingComp
{
	public CompProperties_GraphicByStyle Props => (CompProperties_GraphicByStyle)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		if (Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.changeGraphicsInterval, delta))
		{
			ChangeTheGraphics();
		}
		((ThingComp)this).CompTickInterval(delta);
	}

	public void ChangeTheGraphics()
	{
		if (((Thing)base.parent).Map != null && ((Thing)base.parent).Faction == Faction.OfPlayer && AnimalBehaviours_Settings.flagGraphicChanging)
		{
			ThingWithComps parent = base.parent;
			((Pawn)((parent is Pawn) ? parent : null)).Drawer.renderer.SetAllGraphicsDirty();
		}
	}
}
