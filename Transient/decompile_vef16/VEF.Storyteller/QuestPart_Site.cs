using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Storyteller;

public class QuestPart_Site : QuestPartActivable
{
	public MapParent mapParent;

	public Faction siteFaction;

	private int lastTileChecked = -1;

	public bool applyOnPocketMap;

	public Map Map
	{
		get
		{
			if (applyOnPocketMap)
			{
				PocketMapParent obj = GenCollection.FirstOrDefault<PocketMapParent>(Find.World.pocketMaps, (Predicate<PocketMapParent>)((PocketMapParent mp) => mp.sourceMap == mapParent.Map));
				if (obj == null)
				{
					return null;
				}
				return ((MapParent)obj).Map;
			}
			MapParent obj2 = mapParent;
			if (obj2 == null)
			{
				return null;
			}
			return obj2.Map;
		}
	}

	public override void ExposeData()
	{
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Invalid comparison between Unknown and I4
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		((QuestPartActivable)this).ExposeData();
		Scribe_References.Look<MapParent>(ref mapParent, "mapParent", false);
		Scribe_References.Look<Faction>(ref siteFaction, "siteFaction", false);
		Scribe_Values.Look<int>(ref lastTileChecked, "lastTileChecked", -1, false);
		Scribe_Values.Look<bool>(ref applyOnPocketMap, "applyOnPocketMap", false, false);
		if ((int)Scribe.mode == 4 && mapParent != null)
		{
			lastTileChecked = PlanetTile.op_Implicit(((WorldObject)mapParent).Tile);
		}
	}

	public override void QuestPartTick()
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		((QuestPartActivable)this).QuestPartTick();
		if (mapParent == null || ((WorldObject)mapParent).Destroyed)
		{
			MapParent val = mapParent;
			if (lastTileChecked != -1)
			{
				MapParent val2 = Find.WorldObjects.MapParentAt(PlanetTile.op_Implicit(lastTileChecked));
				mapParent = ((val2 != null && val2 != mapParent) ? val2 : null);
			}
			else
			{
				mapParent = null;
			}
			if (val != null && val != mapParent && ((WorldObject)val).Destroyed)
			{
				MapParent val3 = mapParent;
				if (((WorldObject)val3).questTags == null)
				{
					((WorldObject)val3).questTags = new List<string>();
				}
				((WorldObject)mapParent).questTags.AddRange(((WorldObject)val).questTags);
			}
		}
		else if (lastTileChecked == -1)
		{
			lastTileChecked = PlanetTile.op_Implicit(((WorldObject)mapParent).Tile);
		}
	}
}
