using Verse;

namespace VEF.Abilities;

public class CompDuration : ThingComp
{
	public int durationTicksLeft;

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		durationTicksLeft -= delta;
		if (durationTicksLeft <= 0)
		{
			((Thing)base.parent).Destroy((DestroyMode)0);
		}
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int>(ref durationTicksLeft, "durationTicksLeft", 0, false);
	}
}
