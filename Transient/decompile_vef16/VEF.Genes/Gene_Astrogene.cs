using RimWorld;
using Verse;

namespace VEF.Genes;

public class Gene_Astrogene : Gene
{
	public override bool Active
	{
		get
		{
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_0063: Unknown result type (might be due to invalid IL or missing references)
			if (base.pawn == null)
			{
				return false;
			}
			Pawn pawn = base.pawn;
			IntVec3? val = ((pawn != null) ? new IntVec3?(((Thing)pawn).Position) : ((IntVec3?)null));
			IntVec3 invalid = IntVec3.Invalid;
			if (!val.HasValue || val.GetValueOrDefault() != invalid)
			{
				Map map = ((Thing)base.pawn).Map;
				if (map != null && MapGenUtility.BiomeAt(map, ((Thing)base.pawn).Position)?.inVacuum == false)
				{
					return false;
				}
			}
			if (base.pawn?.ageTracker != null && (float)base.pawn.ageTracker.AgeBiologicalYears < base.def.minAgeActive)
			{
				return false;
			}
			if (base.pawn?.mutant != null && base.pawn.mutant.Def.disablesGenes.Contains(base.def))
			{
				return false;
			}
			return true;
		}
	}
}
