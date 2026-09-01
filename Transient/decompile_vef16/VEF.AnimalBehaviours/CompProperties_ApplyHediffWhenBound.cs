using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_ApplyHediffWhenBound : CompProperties
{
	public int checkingInterval = 1000;

	public HediffDef hediffToApply;

	public bool applyHediffToBonded;

	public HediffDef hediffToApplyToBonded;

	public bool doJobIfBondedDies;

	public JobDef jobToDoIfBondedDies;

	public bool dieIfBondedDies;

	public CompProperties_ApplyHediffWhenBound()
	{
		base.compClass = typeof(CompApplyHediffWhenBound);
	}
}
