using System.Linq;
using HarmonyLib;
using RimWorld.Planet;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(MapTemperature))]
[HarmonyPatch("SeasonAcceptableFor")]
public static class VanillaExpandedFramework_MapTemperature_SeasonAcceptableFor_Patch
{
	[HarmonyPostfix]
	public static void AllowAnimalSpawns(ThingDef animalRace, ref bool __result, Map ___map)
	{
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		if (VanillaAnimalsExpanded_Mod.settings.pawnSpawnStates != null && VanillaAnimalsExpanded_Mod.settings.pawnSpawnStates.Keys.Contains(((Def)animalRace).defName) && VanillaAnimalsExpanded_Mod.settings.pawnSpawnStates[((Def)animalRace).defName])
		{
			__result = false;
		}
		if (animalRace != null && StaticCollectionsClass.riverAnimals.Contains(animalRace))
		{
			PlanetTile tile = ___map.Tile;
			Tile tile2 = ((PlanetTile)(ref tile)).Tile;
			if (((SurfaceTile)((tile2 is SurfaceTile) ? tile2 : null)).Rivers == null)
			{
				__result = false;
			}
		}
	}
}
