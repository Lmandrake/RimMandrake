using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Genes;

public class MapComponent_GeneGoodies : MapComponent
{
	public MapComponent_GeneGoodies(Map map)
		: base(map)
	{
	}

	public override void FinalizeInit()
	{
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		((MapComponent)this).FinalizeInit();
		if (Current.Game.GetComponent<GameComponent_GeneGoodies>().sentOncePerGame)
		{
			return;
		}
		List<Thing> list = new List<Thing>();
		foreach (Pawn allMaps_FreeColonist in PawnsFinder.AllMaps_FreeColonists)
		{
			foreach (Gene item in allMaps_FreeColonist.genes.GenesListForReading)
			{
				GeneExtension modExtension = ((Def)item.def).GetModExtension<GeneExtension>();
				if (modExtension?.thingSetMaker != null)
				{
					list.AddRange((modExtension != null) ? modExtension.thingSetMaker.root.Generate() : null);
				}
			}
		}
		if (list.Count > 0)
		{
			DropPodUtility.DropThingsNear(MapGenerator.PlayerStartSpot, base.map, (IEnumerable<Thing>)list, 110, false, false, true, true, true, (Faction)null);
		}
		Current.Game.GetComponent<GameComponent_GeneGoodies>().sentOncePerGame = true;
	}
}
