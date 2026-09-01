using RimWorld;
using RimWorld.QuestGen;
using Verse;

namespace VEF.Storyteller;

public class GoodwillCurrency : QuestCurrency
{
	public int minimunGoodwillRequirement = -100;

	public override bool Allows(QuestGiverManager questGiverManager, Quest quest, Slate slate, out QuestInfo questInfo)
	{
		Pawn val = slate.Get<Pawn>("asker", (Pawn)null, false);
		if (((val != null) ? ((Thing)val).Faction : null) != null && ((Thing)val).Faction.GoodwillWith(Faction.OfPlayer) >= minimunGoodwillRequirement)
		{
			GoodwillCurrencyInfo goodwillCurrencyInfo = new GoodwillCurrencyInfo();
			goodwillCurrencyInfo.amount = questGiverManager.def.currency.costToAcceptQuest;
			questInfo = new QuestInfo(quest, ((Thing)val).Faction, goodwillCurrencyInfo, questGiverManager.def.onlyOneReward, saveQuestDeeply: true);
			return true;
		}
		questInfo = null;
		return false;
	}
}
