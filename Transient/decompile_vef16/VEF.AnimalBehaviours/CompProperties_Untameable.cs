using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_Untameable : CompProperties
{
	public string factionToReturnTo = "";

	public bool goWild;

	public bool goesManhunter = true;

	public bool sendMessage;

	public string message = "VEF_NotTameable";

	public CompProperties_Untameable()
	{
		base.compClass = typeof(CompUntameable);
	}
}
