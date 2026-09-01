using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using VEF.Factions.GameComponents;
using Verse;

namespace VEF.Factions;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class TradeDeal_TryExecute_Patch
{
	public class FoundContraband
	{
		public int count;

		public ContrabandDef contrabandDef;

		public ChemicalDef chemical;

		public ThingDef thing;

		public override string ToString()
		{
			return $"Found contraband {count} of {contrabandDef} : thing = {thing} | chemical = {chemical}";
		}
	}

	public static void Prefix(List<Tradeable> ___tradeables, out List<FoundContraband> __state)
	{
		__state = new List<FoundContraband>();
		foreach (Tradeable ___tradeable in ___tradeables)
		{
			if (((Transferable)___tradeable).CountToTransferToDestination > 0)
			{
				((Transferable)___tradeable).AnyThing.GetContrabandMaterialCount(ref __state, ((Transferable)___tradeable).CountToTransferToDestination);
			}
		}
	}

	public static void GetContrabandMaterialCount(this Thing thing, ref List<FoundContraband> contrabandList, int countToTransfer)
	{
		if (thing?.def == null)
		{
			return;
		}
		foreach (ContrabandDef contrabandDef in DefDatabase<ContrabandDef>.AllDefs)
		{
			if (contrabandDef.IsThingContraband(thing, out var count, out var thingDef, out var chemicalDef))
			{
				FoundContraband foundContraband = GenCollection.FirstOrFallback<FoundContraband>((IEnumerable<FoundContraband>)contrabandList, (Func<FoundContraband, bool>)((FoundContraband c) => c.contrabandDef == contrabandDef && c.thing == thingDef && c.chemical == chemicalDef), (FoundContraband)null);
				if (foundContraband == null)
				{
					foundContraband = new FoundContraband
					{
						contrabandDef = contrabandDef,
						thing = thingDef,
						chemical = chemicalDef
					};
					contrabandList.Add(foundContraband);
				}
				foundContraband.count += count * countToTransfer;
			}
		}
	}

	public static List<TaggedString> GetContrabandWarningMessages(this Thing thing, bool isGifting)
	{
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0103: Unknown result type (might be due to invalid IL or missing references)
		List<TaggedString> list = new List<TaggedString>();
		if (thing?.def == null)
		{
			return list;
		}
		foreach (ContrabandDef allDef in DefDatabase<ContrabandDef>.AllDefs)
		{
			if (!allDef.IsThingContraband(thing, out var _, out var contrabandThingDef, out var contrabandChemicalDef))
			{
				continue;
			}
			Def val = (Def)((contrabandThingDef != null) ? ((object)contrabandThingDef) : ((object)contrabandChemicalDef));
			bool num = !GenList.NullOrEmpty<FactionDef>((IList<FactionDef>)allDef.illegalFactions) && allDef.illegalFactions.Contains(TradeSession.trader.Faction.def);
			string text = "";
			text = ((!num) ? (isGifting ? allDef.giftWarningKey : allDef.sellWarningKey) : (isGifting ? allDef.giftIllegalFactionWarningKey : allDef.sellIllegalFactionWarningKey));
			foreach (FactionDef faction in allDef.factions)
			{
				Faction val2 = Find.FactionManager.FirstFactionOfDef(faction);
				if (val2 != null)
				{
					NamedArgument val3 = NamedArgumentUtility.Named((object)val2, "FACTION");
					list.Add(TranslatorFormattedStringExtensions.Translate(text, NamedArgumentUtility.Named((object)val, "ILLEGALTHING"), val3, NamedArgumentUtility.Named((object)TradeSession.trader.Faction, "ILLEGALFACTION")));
				}
			}
		}
		return list;
	}

	public static void Postfix(List<FoundContraband> __state, bool __result)
	{
		if (GenList.NullOrEmpty<FoundContraband>((IList<FoundContraband>)__state) || !__result)
		{
			return;
		}
		foreach (FoundContraband item in __state)
		{
			if (item.count > 0 && !item.contrabandDef.factions.Contains(TradeSession.trader.Faction.def) && Rand.Chance(item.contrabandDef.chanceToGetCaught))
			{
				ProcessCaughtContraband(item);
			}
		}
	}

	private static void ProcessCaughtContraband(FoundContraband contraband)
	{
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		FactionDef val = GenCollection.RandomElement<FactionDef>((IEnumerable<FactionDef>)contraband.contrabandDef.factions);
		Faction val2 = Find.FactionManager.FirstFactionOfDef(val);
		Def contrabandThingDef = (Def)((contraband.thing != null) ? ((object)contraband.thing) : ((object)contraband.chemical));
		bool tradedToIllegalFaction = contraband.contrabandDef.illegalFactions?.Contains(TradeSession.trader.Faction.def) ?? false;
		HistoryEventDef historyEvent = (TradeSession.giftMode ? contraband.contrabandDef.giftedHistoryEvent : contraband.contrabandDef.soldHistoryEvent);
		string letterLabel = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(contraband.contrabandDef.letterLabelKey, NamedArgumentUtility.Named((object)val2, "FACTION")));
		string letterDesc = GenerateLetterDescription(contraband, val2, contrabandThingDef, tradedToIllegalFaction);
		int goodwillImpact = Mathf.RoundToInt(contraband.contrabandDef.impactMultiplier * (float)contraband.count);
		Find.World.GetComponent<WorldComponent_FactionGoodwillImpactManager>().ImpactFactionGoodwill(new GoodwillImpactDelayed
		{
			factionToImpact = val2,
			goodwillImpact = goodwillImpact,
			historyEvent = historyEvent,
			impactInTicks = contraband.contrabandDef.ImpactInTicks,
			letterLabel = letterLabel,
			letterDesc = letterDesc,
			relationInfoKey = contraband.contrabandDef.relationInfoKey,
			letterType = contraband.contrabandDef.letterType
		});
	}

	private static string GenerateLetterDescription(FoundContraband contraband, Faction affectedFaction, Def contrabandThingDef, bool tradedToIllegalFaction)
	{
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		if (!tradedToIllegalFaction)
		{
			return TaggedString.op_Implicit(TradeSession.giftMode ? TranslatorFormattedStringExtensions.Translate(contraband.contrabandDef.letterDescGiftKey, NamedArgumentUtility.Named((object)affectedFaction, "FACTION"), NamedArgumentUtility.Named((object)contrabandThingDef, "ILLEGALTHING")) : TranslatorFormattedStringExtensions.Translate(contraband.contrabandDef.letterDescSoldKey, NamedArgumentUtility.Named((object)affectedFaction, "FACTION"), NamedArgumentUtility.Named((object)contrabandThingDef, "ILLEGALTHING")));
		}
		return TaggedString.op_Implicit(TradeSession.giftMode ? TranslatorFormattedStringExtensions.Translate(contraband.contrabandDef.letterDescGifIllegalFactionKey, NamedArgumentUtility.Named((object)affectedFaction, "FACTION"), NamedArgumentUtility.Named((object)contrabandThingDef, "ILLEGALTHING"), NamedArgumentUtility.Named((object)TradeSession.trader.Faction, "ILLEGALFACTION")) : TranslatorFormattedStringExtensions.Translate(contraband.contrabandDef.letterDescSoldIllegalFactionKey, NamedArgumentUtility.Named((object)affectedFaction, "FACTION"), NamedArgumentUtility.Named((object)contrabandThingDef, "ILLEGALTHING"), NamedArgumentUtility.Named((object)TradeSession.trader.Faction, "ILLEGALFACTION")));
	}
}
