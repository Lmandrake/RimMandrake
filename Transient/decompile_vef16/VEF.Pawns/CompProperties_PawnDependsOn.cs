using Verse;

namespace VEF.Pawns;

public class CompProperties_PawnDependsOn : CompProperties
{
	public PawnKindDef pawnToSpawn;

	public bool killPawnAfterDestroying = true;

	public CompProperties_PawnDependsOn()
	{
		base.compClass = typeof(CompPawnDependsOn);
	}
}
