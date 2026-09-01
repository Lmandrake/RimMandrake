using System.Collections.Generic;
using VEF.CacheClearing;
using Verse;

namespace VEF.Apparels;

public static class StaticCollectionsClass
{
	public static HashSet<Thing> camouflaged_pawns;

	static StaticCollectionsClass()
	{
		camouflaged_pawns = new HashSet<Thing>();
		ClearCaches.clearCacheTypes.Add(typeof(StaticCollectionsClass));
	}

	public static void AddCamouflagedPawnToList(Thing thing)
	{
		if (!camouflaged_pawns.Contains(thing))
		{
			camouflaged_pawns.Add(thing);
		}
	}

	public static void RemoveCamouflagedPawnFromList(Thing thing)
	{
		if (camouflaged_pawns.Contains(thing))
		{
			camouflaged_pawns.Remove(thing);
		}
	}
}
