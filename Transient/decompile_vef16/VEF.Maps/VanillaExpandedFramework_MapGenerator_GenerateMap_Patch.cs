using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Maps;

[HarmonyPatch(typeof(MapGenerator), "GenerateMap")]
public static class VanillaExpandedFramework_MapGenerator_GenerateMap_Patch
{
	public static void Postfix(Map __result)
	{
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			try
			{
				DoMapSpawns(__result);
			}
			catch (Exception ex)
			{
				Log.Error("[VEF] Error in MapGenerator_GenerateMap_Patch: " + ex.ToString());
			}
		});
	}

	public static bool CanSpawnAt(IntVec3 c, Map map, ObjectSpawnsDef element)
	{
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_016f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0162: Unknown result type (might be due to invalid IL or missing references)
		if (!element.allowOnChunks)
		{
			foreach (Thing thing in GridsUtility.GetThingList(c, map))
			{
				if (thing?.def?.thingCategories == null)
				{
					continue;
				}
				foreach (ThingCategoryDef thingCategory in thing.def.thingCategories)
				{
					if (thingCategory == ThingCategoryDefOf.Chunks || thingCategory == ThingCategoryDefOf.StoneChunks)
					{
						return false;
					}
				}
			}
		}
		TerrainDef terrain = GridsUtility.GetTerrain(c, map);
		bool flag = true;
		if (element.allowedTerrains != null)
		{
			foreach (string allowedTerrain in element.allowedTerrains)
			{
				if (((Def)terrain).defName == allowedTerrain)
				{
					break;
				}
				flag = false;
			}
		}
		if (!flag)
		{
			return false;
		}
		if (element.disallowedTerrainTags != null)
		{
			foreach (string disallowedTerrainTag in element.disallowedTerrainTags)
			{
				if (terrain.HasTag(disallowedTerrainTag))
				{
					return false;
				}
			}
		}
		if (!element.allowOnWater && terrain.IsWater)
		{
			return false;
		}
		if (element.findCellsOutsideColony && !OutOfCenter(c, map, 60))
		{
			return false;
		}
		if (GenCollection.Any<Thing>(GridsUtility.GetThingList(c, map), (Predicate<Thing>)((Thing x) => !(x is Filth))))
		{
			return false;
		}
		return true;
	}

	public static void DoMapSpawns(Map map)
	{
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_018f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0193: Unknown result type (might be due to invalid IL or missing references)
		//IL_019f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0269: Unknown result type (might be due to invalid IL or missing references)
		//IL_0249: Unknown result type (might be due to invalid IL or missing references)
		//IL_0254: Unknown result type (might be due to invalid IL or missing references)
		if (map == null)
		{
			Log.Error("[VEF] Map was null, MapGenerator_GenerateMap_Patch won't properly.");
			return;
		}
		MapParent parent = map.Parent;
		object obj;
		if (parent == null)
		{
			obj = null;
		}
		else
		{
			WorldObjectDef def = ((WorldObject)parent).def;
			obj = ((def != null) ? ((Def)def).GetModExtension<WorldObjectExtension>() : null);
		}
		WorldObjectExtension worldObjectExtension = (WorldObjectExtension)obj;
		if (worldObjectExtension != null && worldObjectExtension.disableObjectSpawnDefs)
		{
			return;
		}
		int num = 0;
		foreach (ObjectSpawnsDef item in DefDatabase<ObjectSpawnsDef>.AllDefs.Where((ObjectSpawnsDef element) => CanSpawnAt(map, element)))
		{
			IEnumerable<IntVec3> enumerable = GenCollection.InRandomOrder<IntVec3>(map.AllCells, (IList<IntVec3>)null);
			if (num == 0)
			{
				num = ((IntRange)(ref item.numberToSpawn)).RandomInRange;
			}
			foreach (IntVec3 item2 in enumerable)
			{
				bool flag = CanSpawnAt(item2, map, item);
				if (flag)
				{
					Faction val = ((item.factionDef != null) ? Find.FactionManager.FirstFactionOfDef(item.factionDef) : null);
					Thing val2;
					if (item.pawnKindDef != null)
					{
						val2 = (Thing)(object)PawnGenerator.GeneratePawn(item.pawnKindDef, val, (PlanetTile?)null);
					}
					else
					{
						ThingDef thingDefToSpawn = GetThingDefToSpawn(item);
						if (thingDefToSpawn == null)
						{
							break;
						}
						try
						{
							val2 = ThingMaker.MakeThing(thingDefToSpawn, GenStuff.RandomStuffFor(thingDefToSpawn));
						}
						catch (Exception)
						{
							Log.Error("Error making: " + (object)thingDefToSpawn);
							break;
						}
					}
					if (val != null && !(val2 is Pawn) && val2.def.CanHaveFaction)
					{
						val2.SetFaction(val, (Pawn)null);
					}
					CellRect val3 = GenAdj.OccupiedRect(item2, val2.Rotation, ((BuildableDef)val2.def).Size);
					if (((CellRect)(ref val3)).InBounds(map))
					{
						flag = true;
						Enumerator enumerator3 = ((CellRect)(ref val3)).GetEnumerator();
						try
						{
							while (((Enumerator)(ref enumerator3)).MoveNext())
							{
								if (!CanSpawnAt(((Enumerator)(ref enumerator3)).Current, map, item))
								{
									flag = false;
									break;
								}
							}
						}
						finally
						{
							((IDisposable)(Enumerator)(ref enumerator3)/*cast due to .constrained prefix*/).Dispose();
						}
						if (flag)
						{
							if (val2.def.stackLimit > 1)
							{
								val2.stackCount = Mathf.Min(Rand.RangeInclusive(1, val2.def.stackLimit), num);
							}
							num -= val2.stackCount;
							try
							{
								if (item.randomRotation)
								{
									GenPlace.TryPlaceThing(val2, item2, map, (ThingPlaceMode)0, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)Rot4.Random, 1);
								}
								else
								{
									GenSpawn.Spawn(val2, item2, map, (WipeMode)0);
								}
							}
							catch (Exception ex2)
							{
								Log.Error("Exception spawning thing " + ((object)val2)?.ToString() + " - " + ex2.ToString());
							}
						}
					}
				}
				if (flag && num <= 0)
				{
					num = 0;
					break;
				}
			}
		}
	}

	private static ThingDef GetThingDefToSpawn(ObjectSpawnsDef element)
	{
		if (element.thingDef != null)
		{
			return element.thingDef;
		}
		if (!GenList.NullOrEmpty<ThingOption>((IList<ThingOption>)element.thingDefs))
		{
			return GenCollection.RandomElementByWeight<ThingOption>((IEnumerable<ThingOption>)element.thingDefs, (Func<ThingOption, float>)((ThingOption x) => x.weight)).thingDef;
		}
		if (element.category != null)
		{
			return GenCollection.RandomElement<ThingDef>((IEnumerable<ThingDef>)element.category.childThingDefs);
		}
		return null;
	}

	private static bool CanSpawnAt(Map map, ObjectSpawnsDef element)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		PlanetTile tile;
		if (element.allowedPlanetLayers == null)
		{
			tile = map.Tile;
			if (((PlanetTile)(ref tile)).LayerDef != PlanetLayerDefOf.Surface)
			{
				return false;
			}
		}
		if (element.allowedPlanetLayers != null)
		{
			List<PlanetLayerDef> allowedPlanetLayers = element.allowedPlanetLayers;
			tile = map.Tile;
			if (!allowedPlanetLayers.Contains(((PlanetTile)(ref tile)).LayerDef))
			{
				return false;
			}
		}
		if (element.spawnOnlyInPlayerMaps && !map.IsPlayerHome)
		{
			return false;
		}
		if (!element.allowSpawningOnPocketMaps && map.IsPocketMap)
		{
			return false;
		}
		if (element.allowedBiomes != null && !element.allowedBiomes.Contains(map.Biome))
		{
			return false;
		}
		SurfaceTile tile2 = Find.WorldGrid[map.Tile.tileId];
		if (element.allowedRoads != null && (tile2.Roads == null || !GenCollection.Any<RoadDef>(element.allowedRoads, (Predicate<RoadDef>)((RoadDef road) => GenCollection.Any<RoadLink>(tile2.Roads, (Predicate<RoadLink>)((RoadLink x) => x.road == road))))))
		{
			return false;
		}
		return true;
	}

	public static bool OutOfCenter(IntVec3 c, Map map, int centerDist)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		IntVec3 center = map.Center;
		if (c.x >= center.x - centerDist && c.z >= center.z - centerDist && c.x < center.x + centerDist)
		{
			return c.z >= center.z + centerDist;
		}
		return true;
	}
}
