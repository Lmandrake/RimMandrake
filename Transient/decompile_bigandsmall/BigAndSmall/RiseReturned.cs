using System;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class RiseReturned : CompAbilityEffect
{
	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn != null)
		{
			RiseDead(pawn);
		}
		if (pawn == null)
		{
			Thing thing = ((LocalTargetInfo)(ref target)).Thing;
			Corpse val = (Corpse)(object)((thing is Corpse) ? thing : null);
			if (val != null)
			{
				RiseDead(val.InnerPawn);
			}
		}
	}

	public override bool CanApplyOn(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return ((CompAbilityEffect)this).Valid(target, false);
	}

	public override bool Valid(LocalTargetInfo target, bool throwMessages = false)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		bool result = ((CompAbilityEffect)this).Valid(target, throwMessages);
		if (((LocalTargetInfo)(ref target)).Pawn.IsUndead())
		{
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_TargetAlreadyUndead", NamedArgument.op_Implicit(((LocalTargetInfo)(ref target)).Label))), LookTargets.op_Implicit((Thing)(object)((LocalTargetInfo)(ref target)).Pawn), MessageTypeDefOf.RejectInput, false);
			result = false;
		}
		return result;
	}

	public void RiseDead(Pawn pawn)
	{
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Expected O, but got Unknown
		//IL_0163: Unknown result type (might be due to invalid IL or missing references)
		//IL_0168: Unknown result type (might be due to invalid IL or missing references)
		//IL_017e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0185: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b4: Expected O, but got Unknown
		if (Rand.Chance(0.5f))
		{
			OnKillPatch.TriggerZombieApocalypse((pawn != null) ? ((Thing)pawn).Map : null, sendMessage: false);
		}
		try
		{
			if (Rand.Chance(0.75f))
			{
				Hediff val = HediffMaker.MakeHediff(HediffDef.Named("BS_ReturnedReanimation"), pawn, (BodyPartRecord)null);
				pawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
			else
			{
				GameUtils.UnhealingRessurection(pawn);
			}
		}
		catch (Exception ex)
		{
			Log.Warning("BS_ReturnedReanimation failed to apply hediff to " + ((Entity)pawn).LabelShort + ": " + ex.Message + "\n" + ex.StackTrace);
		}
		bool flag = false;
		if (Rand.Chance(0.5f))
		{
			IncidentDef obj = GenCollection.RandomElement<IncidentDef>(DefDatabase<IncidentDef>.AllDefs.Where((IncidentDef x) => x.category == IncidentCategoryDefOf.ThreatBig));
			IncidentParms val2 = new IncidentParms
			{
				target = (IIncidentTarget)(object)((Thing)((AbilityComp)this).parent.pawn).Map,
				forced = true,
				points = StorytellerUtility.DefaultThreatPointsNow((IIncidentTarget)(object)((Thing)((AbilityComp)this).parent.pawn).Map) * Mathf.Lerp(0.5f, 1.2f, Rand.Value)
			};
			obj.Worker.TryExecute(val2);
			flag = true;
		}
		if (Rand.Chance(0.5f))
		{
			float num = (flag ? 1f : 1.2f);
			IncidentParms val3 = new IncidentParms
			{
				target = (IIncidentTarget)(object)((Thing)((AbilityComp)this).parent.pawn).Map,
				forced = true,
				points = StorytellerUtility.DefaultThreatPointsNow((IIncidentTarget)(object)((Thing)((AbilityComp)this).parent.pawn).Map) * Mathf.Lerp(0.5f, num, Rand.Value)
			};
			IncidentDefOf.RaidEnemy.Worker.TryExecute(val3);
		}
	}
}
