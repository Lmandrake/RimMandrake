using System.Text;
using RimWorld;
using Verse;

namespace VEF.Pawns;

public class StatWorker_MassCarryCapacity : StatWorker
{
	public override float GetBaseValueFor(StatRequest request)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		float num = ((StatWorker)this).GetBaseValueFor(request);
		Thing thing = ((StatRequest)(ref request)).Thing;
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null)
		{
			VanillaExpandedFramework_MassUtility_Capacity_Patch.includeStatWorkerResult = false;
			num += MassUtility.Capacity(val, (StringBuilder)null);
			VanillaExpandedFramework_MassUtility_Capacity_Patch.includeStatWorkerResult = true;
		}
		return num;
	}
}
