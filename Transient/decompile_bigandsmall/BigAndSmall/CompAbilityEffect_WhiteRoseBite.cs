using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class CompAbilityEffect_WhiteRoseBite : CompAbilityEffect_BloodfeederBite
{
	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn != null)
		{
			WhiteRoseBite(pawn);
			((CompAbilityEffect_BloodfeederBite)this).Apply(target, dest);
		}
	}

	public static void WhiteRoseBite(Pawn pawn)
	{
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_016c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		Hediff val = pawn.health.hediffSet.GetFirstHediffOfDef(BSDefs.VU_WhiteRoseBite, false);
		Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(BSDefs.VU_WhiteRoseThrall, false);
		if (firstHediffOfDef == null)
		{
			if (val == null)
			{
				val = HediffMaker.MakeHediff(BSDefs.VU_WhiteRoseBite, pawn, (BodyPartRecord)null);
				pawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
			else
			{
				Hediff obj = val;
				obj.Severity += 0.5f;
			}
			if (val.Severity >= 1f)
			{
				firstHediffOfDef = HediffMaker.MakeHediff(BSDefs.VU_WhiteRoseThrall, pawn, (BodyPartRecord)null);
				pawn.health.AddHediff(firstHediffOfDef, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				pawn.health.RemoveHediff(val);
			}
		}
		else
		{
			Hediff obj2 = firstHediffOfDef;
			obj2.Severity += 0.7f;
		}
		Hediff firstHediffOfDef2 = pawn.health.hediffSet.GetFirstHediffOfDef(BSDefs.VU_Euphoria, false);
		if (firstHediffOfDef2 == null)
		{
			firstHediffOfDef2 = HediffMaker.MakeHediff(BSDefs.VU_Euphoria, pawn, (BodyPartRecord)null);
			pawn.health.AddHediff(firstHediffOfDef2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
		else
		{
			firstHediffOfDef2.Severity = 1f;
		}
		if (pawn.IsPrisoner)
		{
			Pawn_GuestTracker guest = pawn.guest;
			float num = pawn.guest.resistance - 2f;
			FloatRange value = pawn.kindDef.initialResistanceRange.Value;
			guest.resistance = Mathf.Min(num, ((FloatRange)(ref value)).TrueMax);
			Pawn_GuestTracker guest2 = pawn.guest;
			float num2 = pawn.guest.will - 2f;
			value = pawn.kindDef.initialWillRange.Value;
			guest2.will = Mathf.Min(num2, ((FloatRange)(ref value)).TrueMax);
		}
	}
}
