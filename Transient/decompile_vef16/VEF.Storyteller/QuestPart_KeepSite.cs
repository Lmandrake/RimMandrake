using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Storyteller;

public class QuestPart_KeepSite : QuestPart
{
	public MapParent mapParent;

	public override void ExposeData()
	{
		((QuestPart)this).ExposeData();
		Scribe_References.Look<MapParent>(ref mapParent, "mapParent", false);
	}
}
