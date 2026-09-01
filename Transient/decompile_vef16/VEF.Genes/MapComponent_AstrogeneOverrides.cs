using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Genes;

public class MapComponent_AstrogeneOverrides : MapComponent
{
	public MapComponent_AstrogeneOverrides(Map map)
		: base(map)
	{
	}

	public override void MapComponentTick()
	{
		((MapComponent)this).MapComponentTick();
		if (Find.TickManager.TicksGame % 1000 != 0)
		{
			return;
		}
		List<Pawn> list = base.map.mapPawns.AllHumanlike.Where(delegate(Pawn x)
		{
			Pawn_GeneTracker genes = x.genes;
			return genes != null && GenCollection.ContainsAny<Gene>((IList<Gene>)genes.GenesListForReading, (Func<Gene, bool>)((Gene x) => x.def.geneClass == typeof(Gene_Astrogene)));
		})?.ToList();
		if (GenList.NullOrEmpty<Pawn>((IList<Pawn>)list))
		{
			return;
		}
		foreach (Pawn item in list)
		{
			foreach (Gene item2 in item.genes.GenesListForReading)
			{
				if (item2 is Gene_Astrogene)
				{
					if (item2.Active)
					{
						GeneUtils.ApplyGeneEffects(item2);
					}
					else
					{
						GeneUtils.RemoveGeneEffects(item2);
					}
				}
			}
			ReflectionCache.checkForOverrides(item.genes);
			item.Drawer.renderer.SetAllGraphicsDirty();
		}
	}
}
