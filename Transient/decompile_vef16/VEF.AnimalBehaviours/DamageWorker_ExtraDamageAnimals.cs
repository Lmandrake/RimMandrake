using System.Linq;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class DamageWorker_ExtraDamageAnimals : DamageWorker_Cut
{
	protected override void ApplySpecialEffectsToPart(Pawn pawn, float totalDamage, DamageInfo dinfo, DamageResult result)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		((DamageWorker_Cut)this).ApplySpecialEffectsToPart(pawn, totalDamage, dinfo, result);
		if (pawn.RaceProps.Animal)
		{
			((Thing)pawn).TakeDamage(new DamageInfo(DamageDefOf.Cut, 20f, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
			if (((DamageInfo)(ref dinfo)).HitPart.def.bleedRate > 0f)
			{
				HediffSet hediffSet = pawn.health.hediffSet;
				HealthUtility.AdjustSeverity(pawn, pawn.health.hediffSet.hediffs.Last().def, hediffSet.BleedRateTotal * 0.01f);
			}
		}
	}
}
