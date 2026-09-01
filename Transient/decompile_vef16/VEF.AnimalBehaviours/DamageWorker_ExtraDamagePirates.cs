using System.Linq;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class DamageWorker_ExtraDamagePirates : DamageWorker_Bite
{
	protected override void ApplySpecialEffectsToPart(Pawn pawn, float totalDamage, DamageInfo dinfo, DamageResult result)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		((DamageWorker_AddInjury)this).ApplySpecialEffectsToPart(pawn, totalDamage, dinfo, result);
		if (((Thing)pawn).Faction != null && ((Def)((Thing)pawn).Faction.def).defName == "Pirate")
		{
			((Thing)pawn).TakeDamage(new DamageInfo(DamageDefOf.Scratch, 50f, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
			if (((DamageInfo)(ref dinfo)).HitPart.def.bleedRate > 0f)
			{
				HediffSet hediffSet = pawn.health.hediffSet;
				HealthUtility.AdjustSeverity(pawn, pawn.health.hediffSet.hediffs.Last().def, hediffSet.BleedRateTotal * 0.01f);
			}
		}
	}
}
