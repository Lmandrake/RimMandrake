using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

/// <summary>
/// Bite and apply Vampirism
/// </summary>
public class CompAbilityEffect_DraculBite : CompAbilityEffect_BloodfeederBite
{
	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn != null)
		{
			IncreaseVampirism(pawn);
			((CompAbilityEffect_BloodfeederBite)this).Apply(target, dest);
		}
	}

	private void IncreaseVampirism(Pawn pawn)
	{
		Pawn pawn2 = ((AbilityComp)this).parent.pawn;
		Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(BSDefs.VU_DraculVampirism, false);
		int item = DraculStageExtension.TryGetDraculStage(pawn2).stage;
		if (firstHediffOfDef is DraculVampirism || firstHediffOfDef == null)
		{
			DraculVampirism draculVampirism;
			if (firstHediffOfDef == null)
			{
				draculVampirism = (DraculVampirism)(object)HediffMaker.MakeHediff(BSDefs.VU_DraculVampirism, pawn, (BodyPartRecord)null);
				pawn.health.AddHediff((Hediff)(object)draculVampirism, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
			else
			{
				draculVampirism = (DraculVampirism)(object)firstHediffOfDef;
				DraculVampirism draculVampirism2 = draculVampirism;
				((Hediff)draculVampirism2).Severity = ((Hediff)draculVampirism2).Severity + 0.15f;
			}
			draculVampirism.stageOfMostPowerfulDracul = Mathf.Max(draculVampirism.stageOfMostPowerfulDracul, item);
			draculVampirism.factionOfMaster = ((Thing)pawn2).Faction;
		}
		else
		{
			Log.Warning($"Something went wrong, {pawn} hediff should be DraculVampirism but is {((object)firstHediffOfDef).GetType()}");
		}
	}
}
