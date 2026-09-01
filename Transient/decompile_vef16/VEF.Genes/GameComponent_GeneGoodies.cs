using Verse;

namespace VEF.Genes;

public class GameComponent_GeneGoodies : GameComponent
{
	public bool sentOncePerGame;

	public GameComponent_GeneGoodies(Game game)
	{
	}

	public override void ExposeData()
	{
		((GameComponent)this).ExposeData();
		Scribe_Values.Look<bool>(ref sentOncePerGame, "sentOncePerGameGenes", false, true);
	}
}
