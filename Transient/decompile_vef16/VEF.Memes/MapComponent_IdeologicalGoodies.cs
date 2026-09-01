using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Memes;

public class MapComponent_IdeologicalGoodies : MapComponent
{
	public MapComponent_IdeologicalGoodies(Map map)
		: base(map)
	{
	}

	public override void FinalizeInit()
	{
		//IL_00fd: Unknown result type (might be due to invalid IL or missing references)
		((MapComponent)this).FinalizeInit();
		if (Current.Game.GetComponent<GameComponent_IdeologicalGoodies>().sentOncePerGame)
		{
			return;
		}
		List<Thing> list = new List<Thing>();
		foreach (StartingItemsByIdeologyDef item in DefDatabase<StartingItemsByIdeologyDef>.AllDefsListForReading)
		{
			Game game = Current.Game;
			if (game == null)
			{
				continue;
			}
			World world = game.World;
			bool? obj;
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
						if (ideos == null)
						{
							obj = null;
						}
						else
						{
							Ideo primaryIdeo = ideos.PrimaryIdeo;
							obj = ((primaryIdeo != null) ? new bool?(primaryIdeo.HasMeme(item.associatedMeme)) : ((bool?)null));
						}
					}
				}
			}
			bool? flag = obj;
			if (flag == true)
			{
				list.AddRange(item.thingSetMaker.root.Generate());
			}
		}
		if (list.Count > 0)
		{
			DropPodUtility.DropThingsNear(MapGenerator.PlayerStartSpot, base.map, (IEnumerable<Thing>)list, 110, false, false, true, true, true, (Faction)null);
		}
		Game game2 = Current.Game;
		object obj2;
		if (game2 == null)
		{
			obj2 = null;
		}
		else
		{
			World world2 = game2.World;
			if (world2 == null)
			{
				obj2 = null;
			}
			else
			{
				FactionManager factionManager2 = world2.factionManager;
				if (factionManager2 == null)
				{
					obj2 = null;
				}
				else
				{
					Faction ofPlayer2 = factionManager2.OfPlayer;
					if (ofPlayer2 == null)
					{
						obj2 = null;
					}
					else
					{
						FactionIdeosTracker ideos2 = ofPlayer2.ideos;
						obj2 = ((ideos2 == null) ? null : ideos2.PrimaryIdeo?.memes);
					}
				}
			}
		}
		if (obj2 != null)
		{
			foreach (MemeDef meme in Current.Game.World.factionManager.OfPlayer.ideos.PrimaryIdeo.memes)
			{
				ExtendedMemeProperties modExtension = ((Def)meme).GetModExtension<ExtendedMemeProperties>();
				if (modExtension == null || modExtension.factionOpinionOffset == 0)
				{
					continue;
				}
				foreach (Faction allFaction in Find.FactionManager.AllFactions)
				{
					allFaction.TryAffectGoodwillWith(Faction.OfPlayer, modExtension.factionOpinionOffset, true, true, (HistoryEventDef)null, (GlobalTargetInfo?)null);
				}
			}
		}
		Current.Game.GetComponent<GameComponent_IdeologicalGoodies>().sentOncePerGame = true;
	}
}
