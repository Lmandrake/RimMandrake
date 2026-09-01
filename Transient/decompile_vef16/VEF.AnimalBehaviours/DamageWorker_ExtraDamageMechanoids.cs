using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class DamageWorker_ExtraDamageMechanoids : DamageWorker_Cut
{
	protected override void ApplySpecialEffectsToPart(Pawn pawn, float totalDamage, DamageInfo dinfo, DamageResult result)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		((DamageWorker_Cut)this).ApplySpecialEffectsToPart(pawn, totalDamage, dinfo, result);
		if (pawn.RaceProps.FleshType == FleshTypeDefOf.Mechanoid)
		{
			((Thing)pawn).TakeDamage(new DamageInfo(DamageDefOf.EMP, 30f, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
		}
	}
}
