using Verse;

namespace BigAndSmall;

public class ReturningGC : GameComponent
{
	public ReturningGC(Game game)
	{
	}

	public override void ExposeData()
	{
		Scribe_Values.Look<int>(ref VUReturning.lastCheckTick, "lastCheckTick", 0, false);
		Scribe_Values.Look<bool>(ref VUReturning.deadRisingMode, "deadRisingMode", false, false);
		Scribe_Values.Look<bool>(ref VUReturning.zombieApocalypseMode, "zombieApocalypseMode", false, false);
		((GameComponent)this).ExposeData();
	}
}
