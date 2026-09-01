using Verse;

namespace BigAndSmall;

public static class HumanlikeAnimals
{
	public static HumanlikeAnimal GetHumanlikeAnimalFor(ThingDef thingDef)
	{
		if (HumanlikeAnimalGenerator.humanlikeAnimals.TryGetValue(thingDef, out var value))
		{
			return value;
		}
		if (HumanlikeAnimalGenerator.reverseLookupHumanlikeAnimals.TryGetValue(thingDef, out var value2))
		{
			return value2;
		}
		return null;
	}

	public static ThingDef HumanLikeAnimalFor(ThingDef td)
	{
		return GetHumanlikeAnimalFor(td)?.humanlikeAnimal;
	}

	public static ThingDef HumanLikeSourceFor(ThingDef td)
	{
		return GetHumanlikeAnimalFor(td)?.humanlike;
	}

	public static ThingDef AnimalSourceFor(ThingDef td)
	{
		return GetHumanlikeAnimalFor(td)?.animal;
	}

	public static bool IsHumanlikeAnimal(this ThingDef td)
	{
		return HumanlikeAnimalGenerator.humanlikeAnimals.ContainsKey(td);
	}
}
