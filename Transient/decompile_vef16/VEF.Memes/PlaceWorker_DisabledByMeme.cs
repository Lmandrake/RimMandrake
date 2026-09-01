using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Memes;

public class PlaceWorker_DisabledByMeme : PlaceWorker
{
	public override bool IsBuildDesignatorVisible(BuildableDef def)
	{
		Game game = Current.Game;
		object obj;
		if (game == null)
		{
			obj = null;
		}
		else
		{
			World world = game.World;
			if (world == null)
			{
				obj = null;
			}
			else
			{
				FactionManager factionManager = world.factionManager;
				if (factionManager == null)
				{
					obj = null;
				}
				else
				{
					Faction ofPlayer = factionManager.OfPlayer;
					if (ofPlayer == null)
					{
						obj = null;
					}
					else
					{
						FactionIdeosTracker ideos = ofPlayer.ideos;
						obj = ((ideos == null) ? null : ideos.PrimaryIdeo?.memes);
					}
				}
			}
		}
		List<MemeDef> list = (List<MemeDef>)obj;
		if (list != null)
		{
			foreach (MemeDef item in list)
			{
				ExtendedMemeProperties modExtension = ((Def)item).GetModExtension<ExtendedMemeProperties>();
				if (modExtension == null || modExtension.removedDesignators == null)
				{
					continue;
				}
				foreach (ThingDef removedDesignator in modExtension.removedDesignators)
				{
					if (removedDesignator == def)
					{
						return false;
					}
				}
			}
		}
		return true;
	}
}
