using Verse;

namespace VEF.AnimalBehaviours;

public class CompDiseaseImmunity : ThingComp
{
	public CompProperties_DiseaseImmunity Props => (CompProperties_DiseaseImmunity)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		if (Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickInterval, delta))
		{
			TryRemoveDiseases();
		}
	}

	public void TryRemoveDiseases()
	{
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (val.health == null || val.health.hediffSet == null)
		{
			return;
		}
		foreach (string item in Props.hediffsToRemove)
		{
			Hediff firstHediffOfDef = val.health.hediffSet.GetFirstHediffOfDef(DefDatabase<HediffDef>.GetNamed(item, false), false);
			if (firstHediffOfDef != null)
			{
				val.health.RemoveHediff(firstHediffOfDef);
			}
		}
	}
}
