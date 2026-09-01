using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class AnimalStatExtension : DefModExtension
{
	public List<string> statToAdd;

	public List<string> statValues;

	public List<string> statDescriptions;

	public bool showImageInInfoCard;

	public string ImageToShowInInfoCard = "UI/EmptyImage";
}
