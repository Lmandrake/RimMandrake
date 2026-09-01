using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_AutoPermanentInjury : HediffComp
{
	public override void CompPostMake()
	{
		HediffUtility.TryGetComp<HediffComp_GetsPermanent>((Hediff)(object)base.parent).IsPermanent = true;
	}
}
