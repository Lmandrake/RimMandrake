using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Factions;

public static class VanillaExpandedFramework_GameComponentUtility_LoadedGame_Patch
{
	[HarmonyPatch(typeof(GameComponentUtility), "LoadedGame")]
	public static class LoadedGame
	{
		[HarmonyPostfix]
		public static void Postfix()
		{
			LongEventHandler.ExecuteWhenFinished((Action)OnGameLoaded);
		}

		private static void OnGameLoaded()
		{
			if (Current.Game != null)
			{
				List<FactionDef> list = new List<FactionDef>();
				List<(FactionDef, ForcedFactionData)> forcedFactions = new List<(FactionDef, ForcedFactionData)>();
				CollectPotentialFactionsToSpawn(DefDatabase<FactionDef>.AllDefs, list, forcedFactions);
				NewFactionSpawningUtility.SpawnFactions(forcedFactions);
				List<FactionDef>.Enumerator enumerator = list.GetEnumerator();
				if (enumerator.MoveNext())
				{
					Dialog_NewFactionSpawning.OpenDialog(enumerator);
				}
				else
				{
					enumerator.Dispose();
				}
			}
		}

		internal static void CollectPotentialFactionsToSpawn(IEnumerable<FactionDef> factions, ICollection<FactionDef> factionsToConsider = null, ICollection<(FactionDef, ForcedFactionData)> forcedFactions = null)
		{
			if (factionsToConsider == null && forcedFactions == null)
			{
				Log.Error("Trying to gather list of factions to spawn, but both working lists were null.");
				return;
			}
			foreach (FactionDef faction in factions)
			{
				if (faction == null || faction.isPlayer || (faction.hidden && faction.requiredCountAtGameStart <= 0) || NewFactionSpawningUtility.NeverSpawn(faction))
				{
					continue;
				}
				ForcedFactionData forcedFactionData = FactionDefExtension.Get((Def)(object)faction).forcedFactionData;
				if (faction.requiredCountAtGameStart < forcedFactionData.requiredFactionCountAtWorldGeneration)
				{
					Log.Error(string.Format("Faction of type {0} requires {1} factions at world creation, but {2}.{3} is {4}.", faction, forcedFactionData.requiredFactionCountDuringGameplay, "FactionDef", "requiredCountAtGameStart", faction.requiredCountAtGameStart));
				}
				if (faction.requiredCountAtGameStart < forcedFactionData.requiredFactionCountDuringGameplay)
				{
					Log.Error(string.Format("Faction of type {0} requires {1} factions during gameplay, but {2}.{3} is {4}.", faction, forcedFactionData.requiredFactionCountDuringGameplay, "FactionDef", "requiredCountAtGameStart", faction.requiredCountAtGameStart));
				}
				int num = Find.FactionManager.AllFactions.Count((Faction f) => f.def == faction);
				if ((forcedFactionData.forceAddFactionIfMissing || forcedFactionData.forcePlayerToAddFactionIfMissing) && forcedFactionData.UnderRequiredGameplayFactionCount(faction, num))
				{
					if (forcedFactionData.forceAddFactionIfMissing)
					{
						forcedFactions?.Add((faction, forcedFactionData));
					}
					else
					{
						factionsToConsider?.Add(faction);
					}
				}
				else if (num <= 0)
				{
					World world = Find.World;
					if (world == null || world.GetComponent<NewFactionSpawningState>()?.IsIgnored(faction) != true)
					{
						factionsToConsider?.Add(faction);
					}
				}
			}
		}
	}

	[HarmonyPatch(typeof(GameComponentUtility), "StartedNewGame")]
	public static class StartedNewGame
	{
		[HarmonyPostfix]
		public static void Postfix()
		{
			LongEventHandler.ExecuteWhenFinished((Action)OnNewGame);
		}

		private static void OnNewGame()
		{
			World world = Find.World;
			if (world != null)
			{
				world.GetComponent<NewFactionSpawningState>()?.Ignore(DefDatabase<FactionDef>.AllDefs);
			}
		}
	}
}
