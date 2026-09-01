using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class AnimalCrossbreedExtension : DefModExtension
{
	public FatherOrMother crossBreedKindDef;

	public List<PawnKindDefWeight> otherPawnKindsByWeight;

	public PawnKindDef otherPawnKind;
}
