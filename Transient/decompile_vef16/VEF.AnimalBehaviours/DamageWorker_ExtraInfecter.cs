using System;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class DamageWorker_ExtraInfecter : DamageWorker_Cut
{
	protected override void ApplySpecialEffectsToPart(Pawn pawn, float totalDamage, DamageInfo dinfo, DamageResult result)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		((DamageWorker_Cut)this).ApplySpecialEffectsToPart(pawn, totalDamage, dinfo, result);
		if (pawn.IsGhoul)
		{
			return;
		}
		Random random = new Random();
		Thing instigator = ((DamageInfo)(ref dinfo)).Instigator;
		CompInfecter compInfecter = ((instigator != null) ? ThingCompUtility.TryGetComp<CompInfecter>(instigator) : null);
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_HealthTracker health = pawn.health;
			if (health == null)
			{
				obj = null;
			}
			else
			{
				HediffSet hediffSet = health.hediffSet;
				obj = ((hediffSet != null) ? hediffSet.GetFirstHediffOfDef(HediffDefOf.WoundInfection, false) : null);
			}
		}
		if (obj != null && compInfecter != null && compInfecter.Props.worsenExistingInfection)
		{
			Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.WoundInfection, false);
			firstHediffOfDef.Severity += compInfecter.Props.severityToAdd;
		}
		else if (StatExtension.GetStatValue((Thing)(object)pawn, StatDefOf.ToxicResistance, true, -1) < 1f && random.NextDouble() > (double)((float)(100 - compInfecter.GetChance) / 100f))
		{
			pawn.health.AddHediff(HediffDefOf.WoundInfection, ((DamageInfo)(ref dinfo)).HitPart, (DamageInfo?)null, (DamageResult)null);
		}
	}
}
