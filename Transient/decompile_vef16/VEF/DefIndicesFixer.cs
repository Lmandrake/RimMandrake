using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF;

[HarmonyPatch(typeof(PlayerKnowledgeDatabase), "ReloadAndRebind")]
public static class DefIndicesFixer
{
	public static bool ranAlready;

	public static void Prefix()
	{
		if (!ranAlready)
		{
			FixIndices();
			ranAlready = true;
		}
	}

	private static void FixIndices()
	{
		Dictionary<Type, HashSet<int>> dictionary = new Dictionary<Type, HashSet<int>>();
		foreach (Type item in GenTypes.AllSubclasses(typeof(Def)))
		{
			if (!(item != typeof(BuildableDef)))
			{
				continue;
			}
			foreach (Def item2 in GenDefDatabase.GetAllDefsInDatabaseForDef(item).ToList())
			{
				if (!dictionary.TryGetValue(item, out var value))
				{
					value = (dictionary[item] = new HashSet<int>());
				}
				if (value.Contains(item2.index))
				{
					item2.index = (ushort)(value.Max() + 1);
				}
				if (!value.Add(item2.index))
				{
					Log.Error("Failed to assign non duplicate index to " + ((object)item2)?.ToString() + " - " + item2.index);
				}
			}
		}
	}
}
