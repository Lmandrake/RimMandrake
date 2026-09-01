using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class HumanlikeAnimal
{
	public PawnKindDef animalKind;

	public ThingDef humanlikeAnimal;

	public ThingDef humanlike;

	public ThingDef animal;

	public int GetLifeStageIndex(Pawn pawn)
	{
		List<LifeStageAge> lifeStageAges = animal.race.lifeStageAges;
		int ageBiologicalYears = pawn.ageTracker.AgeBiologicalYears;
		for (int num = lifeStageAges.Count - 1; num >= 0; num--)
		{
			if ((float)ageBiologicalYears >= lifeStageAges[num].minAge)
			{
				return num;
			}
		}
		return 0;
	}
}
