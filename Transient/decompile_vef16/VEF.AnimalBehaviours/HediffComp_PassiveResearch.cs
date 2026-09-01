using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_PassiveResearch : HediffComp
{
	public HediffCompProperties_PassiveResearch Props => (HediffCompProperties_PassiveResearch)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.tickInterval, delta) && ((Thing)((HediffComp)this).Pawn).Faction == Faction.OfPlayerSilentFail && ((Thing)((HediffComp)this).Pawn).Map != null)
		{
			ResearchProjectDef project = Find.ResearchManager.GetProject((KnowledgeCategoryDef)null);
			if (project != null)
			{
				Find.ResearchManager.AddProgress(project, (float)Props.researchPoints, (Pawn)null);
			}
		}
	}
}
