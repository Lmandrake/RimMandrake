using RimWorld;
using VEF.AnimalBehaviours;
using Verse;

namespace VEF.Pawns;

public class ThoughtWorker_NotInVacuum_Inverted : ThoughtWorker
{
	protected override ThoughtState CurrentStateInternal(Pawn p)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)p).Position != IntVec3.Invalid)
		{
			Map map = ((Thing)p).Map;
			if (map != null && MapGenUtility.BiomeAt(map, ((Thing)p).Position)?.inVacuum == false && p.VacuumResistanceFromArmor() < 0.8f)
			{
				return ThoughtState.op_Implicit(true);
			}
		}
		return ThoughtState.Inactive;
	}
}
