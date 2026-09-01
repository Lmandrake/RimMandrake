using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_Blink : CompProperties
{
	public int blinkInterval = 500;

	public IntRange distance = new IntRange(5, 10);

	public bool warpEffect;

	public bool effectOnlyWhenManhunter;

	public bool blinkWhenManhunter;

	public CompProperties_Blink()
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		base.compClass = typeof(CompBlink);
	}
}
