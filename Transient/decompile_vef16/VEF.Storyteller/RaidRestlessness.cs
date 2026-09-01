using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class RaidRestlessness : IExposable
{
	public int startAfterTicks;

	public ThoughtDef thoughtDef;

	public int GetThoughtState()
	{
		if (Find.TickManager.TicksGame < startAfterTicks)
		{
			return -1;
		}
		int num = startAfterTicks + Current.Game.GetComponent<StorytellerWatcher>().lastRaidExpansionTicks;
		return (int)((float)(int)((float)(Find.TickManager.TicksGame - num) / 900000f) / 4f);
	}

	public void ExposeData()
	{
		Scribe_Values.Look<int>(ref startAfterTicks, "startAfterTicks", 0, true);
		Scribe_Defs.Look<ThoughtDef>(ref thoughtDef, "thoughtDef");
	}
}
