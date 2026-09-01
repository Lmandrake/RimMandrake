using Verse;

namespace VEF.Storyteller;

public class CompProperties_QuestGiver : CompProperties
{
	public string floatOptionLabel;

	public JobDef jobToGive;

	public int questManagerID;

	public QuestGiverDef questGiver;

	public CompProperties_QuestGiver()
	{
		base.compClass = typeof(CompQuestGiver);
	}
}
