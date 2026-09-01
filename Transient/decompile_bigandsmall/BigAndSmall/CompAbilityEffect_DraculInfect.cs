using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

/// <summary>
/// Just apply a bunch of Vampirism.
/// </summary>
public class CompAbilityEffect_DraculInfect : CompAbilityEffect
{
	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		object obj = ((LocalTargetInfo)(ref target)).Pawn;
		if (obj == null)
		{
			Thing thing = ((LocalTargetInfo)(ref target)).Thing;
			Thing obj2 = ((thing is Corpse) ? thing : null);
			obj = ((obj2 != null) ? ((Corpse)obj2).InnerPawn : null);
		}
		Pawn val = (Pawn)obj;
		if (val != null)
		{
			IncreaseVampirism(val);
			((CompAbilityEffect)this).Apply(target, dest);
		}
	}

	private void IncreaseVampirism(Pawn pawn)
	{
		Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(BSDefs.VU_DraculVampirism, false);
		Pawn pawn2 = ((AbilityComp)this).parent.pawn;
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
			}
			DraculVampirism draculVampirism2 = draculVampirism;
			((Hediff)draculVampirism2).Severity = ((Hediff)draculVampirism2).Severity + 0.45f;
			draculVampirism.stageOfMostPowerfulDracul = Mathf.Max(draculVampirism.stageOfMostPowerfulDracul, item);
			draculVampirism.factionOfMaster = ((Thing)pawn2).Faction;
		}
		else
		{
			Log.Warning($"Something went wrong, {pawn} hediff should be DraculVampirism but is {((object)firstHediffOfDef).GetType()}");
		}
	}
}
