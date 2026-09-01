using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class MentalStateWorker_XenophobicRage : MentalStateWorker
{
	public override bool StateCanOccur(Pawn pawn)
	{
		if (((MentalStateWorker)this).StateCanOccur(pawn))
		{
			return XenophobicRageMentalStateUtility.FindPawnToKill(pawn) != null;
		}
		return false;
	}
}
