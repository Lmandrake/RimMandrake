using Verse;

namespace VEF.Memes;

public class GameComponent_IdeologicalGoodies : GameComponent
{
	public bool sentOncePerGame;

	public GameComponent_IdeologicalGoodies(Game game)
	{
	}

	public override void ExposeData()
	{
		((GameComponent)this).ExposeData();
		Scribe_Values.Look<bool>(ref sentOncePerGame, "sentOncePerGame", false, true);
	}
}
