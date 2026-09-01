using System.Collections.Generic;
using Verse;

namespace VEF.Plants;

public class MapComponent_BloomingPlants : MapComponent
{
	public bool alternateBloomingTextures;

	public HashSet<Thing> flowersOrderedForExtraction_InMap = new HashSet<Thing>();

	public HashSet<Thing> weedsOrderedForRemoval_InMap = new HashSet<Thing>();

	public MapComponent_BloomingPlants(Map map)
		: base(map)
	{
	}

	public override void FinalizeInit()
	{
		((MapComponent)this).FinalizeInit();
		alternateBloomingTextures = Rand.Chance(0.5f);
	}

	public override void ExposeData()
	{
		((MapComponent)this).ExposeData();
		Scribe_Values.Look<bool>(ref alternateBloomingTextures, "alternateBloomingTextures", false, false);
	}

	public void AddObjectToMap(Thing thing)
	{
		if (!flowersOrderedForExtraction_InMap.Contains(thing))
		{
			flowersOrderedForExtraction_InMap.Add(thing);
		}
	}

	public void RemoveObjectFromMap(Thing thing)
	{
		if (flowersOrderedForExtraction_InMap.Contains(thing))
		{
			flowersOrderedForExtraction_InMap.Remove(thing);
		}
	}

	public void AddWeedToMap(Thing thing)
	{
		if (!weedsOrderedForRemoval_InMap.Contains(thing))
		{
			weedsOrderedForRemoval_InMap.Add(thing);
		}
	}

	public void RemoveWeedFromMap(Thing thing)
	{
		if (weedsOrderedForRemoval_InMap.Contains(thing))
		{
			weedsOrderedForRemoval_InMap.Remove(thing);
		}
	}
}
