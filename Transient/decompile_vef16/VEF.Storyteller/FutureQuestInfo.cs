using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class FutureQuestInfo : IExposable
{
	public int tickToFire;

	public float mtbDays;

	public QuestScriptDef questDef;

	public bool TryFire()
	{
		if ((tickToFire > 0 && Find.TickManager.TicksGame >= tickToFire) || (mtbDays > 0f && Rand.MTBEventOccurs(mtbDays, 60000f, 60f)))
		{
			questDef.CreateQuest();
			return true;
		}
		return false;
	}

	public void ExposeData()
	{
		Scribe_Values.Look<int>(ref tickToFire, "tickToFire", 0, false);
		Scribe_Values.Look<float>(ref mtbDays, "mtbDays", 0f, false);
		Scribe_Defs.Look<QuestScriptDef>(ref questDef, "questDef");
	}
}
