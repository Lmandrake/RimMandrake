using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using VEF.Planet;
using Verse;

namespace VEF.Factions;

public class FactionDefExtension : DefModExtension
{
	private static readonly FactionDefExtension DefaultValues = new FactionDefExtension();

	public bool hasCities = true;

	public string settlementGenerationSymbol;

	public string packAnimalTexNameSuffix;

	public PawnKindDef strangerInBlackReplacement;

	private string siegeParameterSet = "";

	public SiegeParameterSetDef siegeParameterSetDef;

	public List<StartingGoodwillByFaction> startingGoodwillByFactionDefs = new List<StartingGoodwillByFaction>();

	public List<BiomeDef> allowedBiomes = new List<BiomeDef>();

	public List<BiomeDef> disallowedBiomes = new List<BiomeDef>();

	public List<Hilliness> requiredHillLevels;

	public bool spawnOnCoastalTilesOnly;

	public bool neverConnectToRoads;

	public float minDistanceToOtherSettlements;

	public bool excludeFromCommConsole;

	public bool excludeFromQuests;

	public List<RaidStrategyDef> allowedStrategies = new List<RaidStrategyDef>();

	public ForcedFactionData forcedFactionData = new ForcedFactionData();

	public static FactionDefExtension Get(Def def)
	{
		return def.GetModExtension<FactionDefExtension>() ?? DefaultValues;
	}

	public override IEnumerable<string> ConfigErrors()
	{
		if (!GenText.NullOrEmpty(siegeParameterSet))
		{
			siegeParameterSetDef = DefDatabase<SiegeParameterSetDef>.GetNamed(siegeParameterSet, true);
		}
		foreach (string item in forcedFactionData.ConfigErrors())
		{
			yield return item;
		}
	}
}
