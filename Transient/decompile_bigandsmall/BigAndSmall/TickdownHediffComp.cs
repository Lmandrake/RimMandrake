using Verse;

namespace BigAndSmall;

public abstract class TickdownHediffComp : HediffComp
{
	protected int tickDown;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		tickDown -= delta;
		if (tickDown <= 0)
		{
			tickDown = 0;
			TickEvent();
			ResetCountdown();
		}
	}

	public abstract void TickEvent();

	public abstract void ResetCountdown();
}
