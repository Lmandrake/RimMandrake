using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_TurnWhenDead : HediffCompProperties
{
	public string thingToTurnTo = "";

	public float severityToTurn = 0.85f;

	public List<int> numberOfSpawn;

	public bool isHostile = true;

	public bool keepGender;

	public string factionToTurnTo = "";

	public HediffCompProperties_TurnWhenDead()
	{
		base.compClass = typeof(HediffComp_TurnWhenDead);
	}
}
