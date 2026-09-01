using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI.Group;

namespace BigAndSmall;

[StaticConstructorOnStartup]
public class UsableDownedAbility : Ability
{
	public override bool CanQueueCast
	{
		get
		{
			if (!base.pawn.Downed)
			{
				return ((Ability)this).CanQueueCast;
			}
			return true;
		}
	}

	public UsableDownedAbility()
	{
	}

	public UsableDownedAbility(Pawn pawn)
		: base(pawn)
	{
	}

	public UsableDownedAbility(Pawn pawn, AbilityDef def)
		: base(pawn, def)
	{
	}

	public override void QueueCastingJob(LocalTargetInfo target, LocalTargetInfo destination)
	{
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		if (!((Ability)this).CanQueueCast || !((Ability)this).CanApplyOn(target))
		{
			return;
		}
		if (base.pawn.Downed)
		{
			TargetingParameters targetParams = ((Ability)this).verb.verbProps.targetParams;
			if (targetParams != null && targetParams.canTargetSelf)
			{
				((Ability)this).verb.TryStartCastOn(LocalTargetInfo.op_Implicit(((Ability)this).verb.Caster), false, true, false, false);
				return;
			}
		}
		((Ability)this).QueueCastingJob(target, destination);
	}

	public override bool GizmoDisabled(out string reason)
	{
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00de: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_018c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		//IL_016c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		if (((Ability)this).CanCooldown && ((Ability)this).OnCooldown && (!base.def.cooldownPerCharge || base.charges == 0))
		{
			TaggedString val = TranslatorFormattedStringExtensions.Translate("AbilityOnCooldown", NamedArgument.op_Implicit(GenDate.ToStringTicksToPeriod(((Ability)this).CooldownTicksRemaining, true, false, true, true, false)));
			reason = ((TaggedString)(ref val)).Resolve();
			return true;
		}
		if (((Ability)this).UsesCharges && base.charges <= 0)
		{
			reason = TaggedString.op_Implicit(Translator.Translate("AbilityNoCharges"));
			return true;
		}
		if (!GenList.NullOrEmpty<AbilityComp>((IList<AbilityComp>)base.comps))
		{
			for (int i = 0; i < base.comps.Count; i++)
			{
				if (base.comps[i].GizmoDisabled(ref reason))
				{
					return true;
				}
			}
		}
		AcceptanceReport canCast = ((Ability)this).CanCast;
		if (!((AcceptanceReport)(ref canCast)).Accepted)
		{
			reason = ((AcceptanceReport)(ref canCast)).Reason;
			return true;
		}
		Lord lord = LordUtility.GetLord(base.pawn);
		if (lord != null)
		{
			AcceptanceReport val2 = lord.AbilityAllowed((Ability)(object)this);
			if (!AcceptanceReport.op_Implicit(val2))
			{
				reason = ((AcceptanceReport)(ref val2)).Reason;
				return true;
			}
		}
		if (!base.pawn.Drafted && base.def.disableGizmoWhileUndrafted && CaravanUtility.GetCaravan((Thing)(object)base.pawn) == null && !DebugSettings.ShowDevGizmos)
		{
			reason = TaggedString.op_Implicit(Translator.Translate("AbilityDisabledUndrafted"));
			return true;
		}
		if (base.def.casterMustBeCapableOfViolence && base.pawn.WorkTagIsDisabled((WorkTags)8))
		{
			reason = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("IsIncapableOfViolence", NamedArgument.op_Implicit(((Entity)base.pawn).LabelShort), NamedArgument.op_Implicit((Thing)(object)base.pawn)));
			return true;
		}
		if (!((Ability)this).CanQueueCast)
		{
			reason = TaggedString.op_Implicit(Translator.Translate("AbilityAlreadyQueued"));
			return true;
		}
		reason = null;
		return false;
	}
}
