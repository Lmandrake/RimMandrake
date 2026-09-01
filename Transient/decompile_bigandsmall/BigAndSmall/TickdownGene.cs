using Verse;

namespace BigAndSmall;

public abstract class TickdownGene : Gene
{
	protected int tickDown;

	public override void TickInterval(int delta)
	{
		tickDown -= delta;
		((Gene)this).TickInterval(delta);
		if (tickDown <= 0)
		{
			tickDown = 0;
			TickEvent();
			ResetCountdown();
		}
	}

	public abstract void TickEvent();

	public abstract void ResetCountdown();

	public override void ExposeData()
	{
		((Gene)this).ExposeData();
		Scribe_Values.Look<int>(ref tickDown, "tickDown", 0, false);
	}
}
