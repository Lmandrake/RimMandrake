using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class HumanlikeAnimalSettings : Def
{
	private static List<HumanlikeAnimalSettings> allSettings;

	public List<string> hasHandsWildcards = new List<string>();

	public List<string> hasPoorHandsWildcards = new List<string>();

	public List<string> compWhitelist = new List<string>();

	public List<string> tabWhitelist = new List<string>();

	public List<string> modExtensionWhitelist = new List<string>();

	public List<RenderTreeOverride> renderTreeWhitelist = new List<RenderTreeOverride>();

	public List<AnimalFamilySettings> animalFamilySettings = new List<AnimalFamilySettings>();

	public static List<HumanlikeAnimalSettings> AllHASettings => allSettings ?? (allSettings = DefDatabase<HumanlikeAnimalSettings>.AllDefsListForReading);
}
