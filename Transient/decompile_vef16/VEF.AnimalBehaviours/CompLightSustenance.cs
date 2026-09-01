using Verse;

namespace VEF.AnimalBehaviours;

public class CompLightSustenance : ThingComp
{
	public float growOptimalGlow = 0.4f;

	private bool addHediffOnce = true;

	public CompProperties_LightSustenance Props => (CompProperties_LightSustenance)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<bool>(ref addHediffOnce, "addHediffOnce", true, false);
	}

	public override void CompTickInterval(int delta)
	{
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (!((Thing)val).Spawned)
		{
			return;
		}
		if (addHediffOnce)
		{
			val.health.AddHediff(InternalDefOf.VEF_LightSustenance, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			val.health.hediffSet.GetFirstHediffOfDef(InternalDefOf.VEF_LightSustenance, false).Severity = 0.2f;
			addHediffOnce = false;
		}
		if (((Thing)base.parent).Map.glowGrid.GroundGlowAt(((Thing)base.parent).Position, false, false) >= growOptimalGlow)
		{
			Hediff firstHediffOfDef = val.health.hediffSet.GetFirstHediffOfDef(InternalDefOf.VEF_LightSustenance, false);
			if (firstHediffOfDef != null && firstHediffOfDef.Severity > 0f)
			{
				firstHediffOfDef.Severity -= 1E-05f * (float)delta;
			}
		}
		else
		{
			Hediff firstHediffOfDef2 = val.health.hediffSet.GetFirstHediffOfDef(InternalDefOf.VEF_LightSustenance, false);
			if (firstHediffOfDef2 != null && firstHediffOfDef2.Severity < 1f)
			{
				firstHediffOfDef2.Severity += 1E-05f * (float)delta;
			}
		}
	}
}
