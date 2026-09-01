using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_LightSustenance : HediffComp
{
	public float growOptimalGlow = 0.4f;

	private bool addHediffOnce = true;

	public HediffCompProperties_LightSustenance Props => (HediffCompProperties_LightSustenance)(object)base.props;

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		Scribe_Values.Look<bool>(ref addHediffOnce, "addHediffOnce", true, false);
	}

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = ((Hediff)base.parent).pawn;
		if (!((Thing)pawn).Spawned)
		{
			return;
		}
		if (addHediffOnce)
		{
			pawn.health.AddHediff(InternalDefOf.VEF_LightSustenance, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			pawn.health.hediffSet.GetFirstHediffOfDef(InternalDefOf.VEF_LightSustenance, false).Severity = 0.2f;
			addHediffOnce = false;
		}
		if (((Thing)pawn).Map.glowGrid.GroundGlowAt(((Thing)pawn).Position, false, false) >= growOptimalGlow)
		{
			Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(InternalDefOf.VEF_LightSustenance, false);
			if (firstHediffOfDef != null && firstHediffOfDef.Severity > 0f)
			{
				firstHediffOfDef.Severity -= 1E-05f * (float)delta;
			}
		}
		else
		{
			Hediff firstHediffOfDef2 = pawn.health.hediffSet.GetFirstHediffOfDef(InternalDefOf.VEF_LightSustenance, false);
			if (firstHediffOfDef2 != null && firstHediffOfDef2.Severity < 1f)
			{
				firstHediffOfDef2.Severity += 1E-05f * (float)delta;
			}
		}
	}
}
