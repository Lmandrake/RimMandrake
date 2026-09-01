using System;
using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class ReturningSoulManager : GameComponent
{
	public static ReturningSoulManager instance;

	public List<ReturningSoulHolder> returningSouls = new List<ReturningSoulHolder>();

	public Game game;

	private const int tickFrequency = 500;

	public ReturningSoulManager(Game game)
	{
		this.game = game;
		instance = this;
	}

	public override void ExposeData()
	{
		Scribe_Collections.Look<ReturningSoulHolder>(ref returningSouls, "BS_ReturningSouls", (LookMode)2, Array.Empty<object>());
	}

	public override void GameComponentTick()
	{
		((GameComponent)this).GameComponentTick();
		if (Find.TickManager.TicksGame % 500 == 0)
		{
			ProcessSouls();
		}
	}

	public void ProcessSouls()
	{
		if (returningSouls.Count == 0)
		{
			return;
		}
		for (int num = returningSouls.Count - 1; num >= 0; num--)
		{
			ReturningSoulHolder returningSoulHolder = returningSouls[num];
			if (((Thing)returningSoulHolder.pawn).Spawned)
			{
				returningSouls.RemoveAt(num);
			}
			else if (returningSoulHolder.Tick(500))
			{
				returningSouls.RemoveAt(num);
			}
		}
	}
}
