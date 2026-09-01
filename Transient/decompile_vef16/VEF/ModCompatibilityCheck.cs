using System.Collections.Generic;
using System.Linq;
using Verse;

namespace VEF;

[StaticConstructorOnStartup]
public static class ModCompatibilityCheck
{
	public static bool DualWield;

	public static bool FacialStuff;

	public static bool ResearchTree;

	public static bool ResearchPal;

	public static bool RimCities;

	public static bool RPGStyleInventory;

	public static bool RPGStyleInventoryRevamped;

	public static bool RunAndGun;

	public static bool FactionDiscovery;

	public static bool WhatTheHack;

	public static bool CombatExtended;

	public static bool HumanAlienRace;

	static ModCompatibilityCheck()
	{
		List<ModMetaData> list = ModsConfig.ActiveModsInLoadOrder.ToList();
		for (int i = 0; i < list.Count; i++)
		{
			ModMetaData val = list[i];
			if (val.Name == "Dual Wield")
			{
				DualWield = true;
			}
			else if (val.Name == "Facial Stuff 1.1")
			{
				FacialStuff = true;
			}
			else if (val.Name == "Research Tree")
			{
				ResearchTree = true;
			}
			else if (val.Name == "ResearchPal")
			{
				ResearchPal = true;
			}
			else if (val.Name == "RimCities")
			{
				RimCities = true;
			}
			else if (val.Name == "RPG Style Inventory Revamped")
			{
				RPGStyleInventoryRevamped = true;
			}
			else if (val.Name == "RunAndGun")
			{
				RunAndGun = true;
			}
			else if (val.Name == "Faction Discovery")
			{
				FactionDiscovery = true;
			}
			else if (val.Name == "What the hack?!")
			{
				WhatTheHack = true;
			}
			else if (val.Name == "Combat Extended")
			{
				CombatExtended = true;
			}
			else if (val.Name == "Humanoid Alien Races" || val.Name == "Humanoid Alien Races ~ Dev")
			{
				HumanAlienRace = true;
			}
		}
	}
}
