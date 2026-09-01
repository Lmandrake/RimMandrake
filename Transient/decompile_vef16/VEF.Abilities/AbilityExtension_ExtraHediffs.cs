using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Abilities;

public class AbilityExtension_ExtraHediffs : AbilityExtension_AbilityMod
{
	public List<HediffDef> onTarget;

	public List<HediffDef> onCaster;

	public StatDef durationMultiplier;

	public int? durationTimeOverride;

	public override void Cast(GlobalTargetInfo[] targets, Ability ability)
	{
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		base.Cast(targets, ability);
		int num = durationTimeOverride ?? ability.GetDurationForPawn();
		for (int i = 0; i < targets.Length; i++)
		{
			GlobalTargetInfo val = targets[i];
			if (((GlobalTargetInfo)(ref val)).Thing != null && durationMultiplier != null)
			{
				num = Mathf.RoundToInt((float)num * StatExtension.GetStatValue(((GlobalTargetInfo)(ref val)).Thing, durationMultiplier, true, -1));
			}
			if (onCaster != null)
			{
				foreach (HediffDef item in onCaster)
				{
					Hediff val2 = HediffMaker.MakeHediff(item, ability.pawn, (BodyPartRecord)null);
					HediffComp_Disappears val3 = HediffUtility.TryGetComp<HediffComp_Disappears>(val2);
					if (val3 != null)
					{
						val3.ticksToDisappear = num;
					}
					ability.pawn.health.AddHediff(val2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
			}
			Thing thing = ((GlobalTargetInfo)(ref val)).Thing;
			Pawn val4 = (Pawn)(object)((thing is Pawn) ? thing : null);
			if (val4 == null || onTarget == null)
			{
				continue;
			}
			foreach (HediffDef item2 in onTarget)
			{
				Hediff val5 = HediffMaker.MakeHediff(item2, val4, (BodyPartRecord)null);
				HediffComp_Disappears val6 = HediffUtility.TryGetComp<HediffComp_Disappears>(val5);
				if (val6 != null)
				{
					val6.ticksToDisappear = num;
				}
				val4.health.AddHediff(val5, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
	}
}
