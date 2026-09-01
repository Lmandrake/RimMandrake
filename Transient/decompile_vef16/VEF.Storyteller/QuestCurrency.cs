using RimWorld;
using RimWorld.QuestGen;

namespace VEF.Storyteller;

public class QuestCurrency
{
	public float costToAcceptQuest;

	public virtual bool Allows(QuestGiverManager questGiverManager, Quest toCheck, Slate slate, out QuestInfo questInfo)
	{
		questInfo = null;
		return true;
	}
}
