using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Factions;

public class ForcedFactionData
{
	public int requiredFactionCountAtWorldGeneration;

	public bool preventRemovalAtWorldGeneration;

	public bool displayMissingWarningIfNoFactionPresent;

	public string factionDisabledAtWorldGenerationMessage;

	public int requiredFactionCountDuringGameplay;

	public bool forceAddFactionIfMissing;

	public bool forcePlayerToAddFactionIfMissing;

	public string factionDiscoverySpecialMessage;

	public string factionDiscoveryFailedMessage;

	public float factionDiscoveryFactionCountFactor = 1f;

	public int factionDiscoveryMinimumDistanceFromPlayer = -1;

	public bool UnderRequiredWorldGenFactionCount(FactionDef faction, List<FactionDef> factions)
	{
		if (requiredFactionCountAtWorldGeneration > 0)
		{
			return GenCollection.Count<FactionDef>(factions, (Predicate<FactionDef>)((FactionDef x) => x == faction)) < Mathf.Min(faction.maxConfigurableAtWorldCreation, requiredFactionCountAtWorldGeneration);
		}
		return false;
	}

	public bool UnderRequiredGameplayFactionCount(FactionDef faction)
	{
		return UnderRequiredGameplayFactionCount(faction, Find.FactionManager.AllFactions.Count((Faction f) => f.def == faction));
	}

	public bool UnderRequiredGameplayFactionCount(FactionDef faction, int factionCount)
	{
		if (requiredFactionCountDuringGameplay > 0)
		{
			return factionCount < Mathf.Min(faction.maxConfigurableAtWorldCreation, requiredFactionCountDuringGameplay);
		}
		return false;
	}

	public TaggedString GetWorldGenMissingFactionMessage(FactionDef faction, List<FactionDef> factions)
	{
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		bool num = string.IsNullOrWhiteSpace(factionDisabledAtWorldGenerationMessage);
		bool flag = preventRemovalAtWorldGeneration;
		string text = ((!num) ? factionDisabledAtWorldGenerationMessage : ((!flag) ? "VanillaFactionsExpanded.FactionRecommended" : "VanillaFactionsExpanded.FactionRequired"));
		TaggedString val = TranslatorFormattedStringExtensions.Translate(text, NamedArgumentUtility.Named((object)((Def)faction).label, "FACTION"), NamedArgumentUtility.Named((object)GenCollection.Count<FactionDef>(factions, (Predicate<FactionDef>)((FactionDef x) => x == faction)), "COUNT"), NamedArgumentUtility.Named((object)requiredFactionCountAtWorldGeneration, "REQUIRED"));
		return ((TaggedString)(ref val)).CapitalizeFirst();
	}

	public TaggedString GetFactionDiscoveryMessage(FactionDef faction)
	{
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		TaggedString val = TranslatorFormattedStringExtensions.Translate(string.IsNullOrWhiteSpace(factionDiscoverySpecialMessage) ? "VanillaFactionsExpanded.FactionDiscoveryRequired" : factionDiscoverySpecialMessage, NamedArgumentUtility.Named((object)((Def)faction).label, "FACTION"), NamedArgumentUtility.Named((object)Find.FactionManager.AllFactions.Count((Faction f) => f.def == faction), "COUNT"), NamedArgumentUtility.Named((object)requiredFactionCountAtWorldGeneration, "REQUIRED"));
		return ((TaggedString)(ref val)).CapitalizeFirst();
	}

	public TaggedString GetFactionDiscoveryFailedMessage(FactionDef faction)
	{
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		TaggedString val = TranslatorFormattedStringExtensions.Translate(string.IsNullOrWhiteSpace(factionDiscoveryFailedMessage) ? "VanillaFactionsExpanded.FactionFailedMessage" : factionDiscoveryFailedMessage, NamedArgumentUtility.Named((object)((Def)faction).label, "FACTION"), NamedArgumentUtility.Named((object)Find.FactionManager.AllFactions.Count((Faction f) => f.def == faction), "COUNT"), NamedArgumentUtility.Named((object)requiredFactionCountAtWorldGeneration, "REQUIRED"));
		return ((TaggedString)(ref val)).CapitalizeFirst();
	}

	public IEnumerable<string> ConfigErrors()
	{
		if (requiredFactionCountAtWorldGeneration < 0)
		{
			yield return string.Format("{0} cannot be less than 0, but currently it is {1}. Fixing.", "requiredFactionCountAtWorldGeneration", requiredFactionCountAtWorldGeneration);
			requiredFactionCountAtWorldGeneration = 0;
		}
		if (requiredFactionCountDuringGameplay < 0)
		{
			yield return string.Format("{0} cannot be less than 0, but currently it is {1}. Fixing.", "requiredFactionCountDuringGameplay", requiredFactionCountDuringGameplay);
			requiredFactionCountDuringGameplay = 0;
		}
		if (factionDiscoveryFactionCountFactor < 0f)
		{
			yield return string.Format("{0} cannot be less than 0, but currently it is {1}. Fixing.", "factionDiscoveryFactionCountFactor", factionDiscoveryFactionCountFactor);
			factionDiscoveryFactionCountFactor = 0f;
		}
		if (factionDiscoveryMinimumDistanceFromPlayer > 10)
		{
			yield return string.Format("{0} cannot be more than 10, but currently it is {1}. Fixing.", "factionDiscoveryMinimumDistanceFromPlayer", factionDiscoveryMinimumDistanceFromPlayer);
			factionDiscoveryMinimumDistanceFromPlayer = 10;
		}
	}
}
