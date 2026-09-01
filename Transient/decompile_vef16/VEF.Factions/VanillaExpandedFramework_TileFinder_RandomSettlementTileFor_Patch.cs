using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Factions;

[HarmonyPatch]
public static class VanillaExpandedFramework_TileFinder_RandomSettlementTileFor_Patch
{
	[HarmonyPatch(typeof(TileFinder), "RandomSettlementTileFor")]
	[HarmonyPatch(new Type[]
	{
		typeof(PlanetLayer),
		typeof(Faction),
		typeof(bool),
		typeof(Predicate<PlanetTile>)
	})]
	public static class VanillaExpandedFramework_TileFinder_RandomSettlementTileFor_Prefix_Patch
	{
		public static Faction factionToCheck;

		public static void Prefix(Faction faction)
		{
			factionToCheck = faction;
		}

		public static void Postfix()
		{
			factionToCheck = null;
		}
	}

	[HarmonyTargetMethod]
	public static MethodBase TargetMethod()
	{
		return typeof(TileFinder).GetNestedTypes(AccessTools.all).SelectMany((Type x) => x.GetMethods(AccessTools.all)).FirstOrDefault((MethodInfo x) => x.Name.Contains("<RandomSettlementTileFor>") && x.ReturnType == typeof(float));
	}

	public static void Postfix(ref float __result, int x)
	{
		//IL_0254: Unknown result type (might be due to invalid IL or missing references)
		//IL_025f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_0169: Unknown result type (might be due to invalid IL or missing references)
		//IL_016e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0173: Unknown result type (might be due to invalid IL or missing references)
		if (((Def)(VanillaExpandedFramework_TileFinder_RandomSettlementTileFor_Prefix_Patch.factionToCheck?.def?)).modExtensions == null || !(__result > 0f))
		{
			return;
		}
		List<DefModExtension> modExtensions = ((Def)VanillaExpandedFramework_TileFinder_RandomSettlementTileFor_Prefix_Patch.factionToCheck.def).modExtensions;
		if (modExtensions != null)
		{
			foreach (FactionDefExtension options in modExtensions.OfType<FactionDefExtension>())
			{
				Tile val = (Tile)(object)Find.WorldGrid[x];
				List<BiomeDef> disallowedBiomes = options.disallowedBiomes;
				if (disallowedBiomes != null && GenCollection.Any<BiomeDef>(disallowedBiomes) && options.disallowedBiomes.Contains(val.PrimaryBiome))
				{
					__result = 0f;
					return;
				}
				List<BiomeDef> allowedBiomes = options.allowedBiomes;
				if (allowedBiomes != null && GenCollection.Any<BiomeDef>(allowedBiomes) && !options.allowedBiomes.Contains(val.PrimaryBiome))
				{
					__result = 0f;
					return;
				}
				List<Hilliness> requiredHillLevels = options.requiredHillLevels;
				if (requiredHillLevels != null && GenCollection.Any<Hilliness>(requiredHillLevels) && !options.requiredHillLevels.Contains(val.hilliness))
				{
					__result = 0f;
					return;
				}
				if (options.spawnOnCoastalTilesOnly)
				{
					Rot4 val2 = Find.World.CoastDirectionAt(PlanetTile.op_Implicit(x));
					if (!((Rot4)(ref val2)).IsValid)
					{
						__result = 0f;
						return;
					}
				}
				if (options.minDistanceToOtherSettlements > 0f && GenCollection.Any<Settlement>(Find.WorldObjects.SettlementBases, (Predicate<Settlement>)((Settlement other) => Find.WorldGrid.ApproxDistanceInTiles(((WorldObject)other).Tile, PlanetTile.op_Implicit(x)) < options.minDistanceToOtherSettlements)))
				{
					__result = 0f;
					return;
				}
			}
		}
		foreach (Settlement settlementBasis in Find.WorldObjects.SettlementBases)
		{
			modExtensions = ((settlementBasis == null) ? null : ((Def)(((WorldObject)settlementBasis).Faction?.def?)).modExtensions);
			if (modExtensions == null)
			{
				continue;
			}
			foreach (FactionDefExtension item in modExtensions.OfType<FactionDefExtension>())
			{
				if (item != null && item.minDistanceToOtherSettlements > 0f && Find.WorldGrid.ApproxDistanceInTiles(((WorldObject)settlementBasis).Tile, PlanetTile.op_Implicit(x)) < item.minDistanceToOtherSettlements)
				{
					__result = 0f;
					return;
				}
			}
		}
	}
}
