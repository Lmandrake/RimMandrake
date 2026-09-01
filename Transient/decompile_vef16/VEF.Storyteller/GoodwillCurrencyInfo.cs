using RimWorld;
using RimWorld.Planet;

namespace VEF.Storyteller;

public class GoodwillCurrencyInfo : QuestCurrencyInfo
{
	public override void Buy(QuestInfo questInfo)
	{
		base.Buy(questInfo);
		questInfo.askerFaction.TryAffectGoodwillWith(Faction.OfPlayer, -(int)amount, true, true, (HistoryEventDef)null, (GlobalTargetInfo?)null);
	}
}
