using System;
using RimWorld.Planet;
using Verse;
using Verse.AI;

namespace VEF.Abilities;

public class AbilityExtension_AbilityMod : DefModExtension
{
	[Unsaved(false)]
	public AbilityDef abilityDef;

	public virtual bool HidePawnTooltips => false;

	public virtual bool ShowGizmoOnPawn(Pawn pawn)
	{
		return true;
	}

	public virtual bool IsEnabledForPawn(Ability ability, out string reason)
	{
		reason = string.Empty;
		return true;
	}

	public virtual string GetDescription(Ability ability)
	{
		return string.Empty;
	}

	[Obsolete("Use new method with GlobalTargetInfos instead")]
	public virtual void PreWarmupAction(LocalTargetInfo target, Ability ability)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		PreWarmupAction((GlobalTargetInfo[])(object)new GlobalTargetInfo[1] { ((LocalTargetInfo)(ref target)).ToGlobalTargetInfo(ability.Caster.Map) }, ability);
	}

	public virtual void PreWarmupAction(GlobalTargetInfo[] targets, Ability ability)
	{
	}

	public virtual void WarmupToil(Toil toil)
	{
	}

	public virtual void PreCast(GlobalTargetInfo[] target, Ability ability, ref bool startAbilityJobImmediately, Action startJobAction)
	{
	}

	[Obsolete("Use the new Cast method using GlobalTargets instead")]
	public virtual void Cast(LocalTargetInfo target, Ability ability)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		Cast((GlobalTargetInfo[])(object)new GlobalTargetInfo[1] { ((LocalTargetInfo)(ref target)).ToGlobalTargetInfo(ability.Caster.Map) }, ability);
	}

	public virtual void Cast(GlobalTargetInfo[] targets, Ability ability)
	{
	}

	public virtual void PostCast(GlobalTargetInfo[] targets, Ability ability)
	{
	}

	public virtual bool Valid(GlobalTargetInfo[] targets, Ability ability, bool throwMessages = false)
	{
		return true;
	}

	public virtual bool ValidTile(GlobalTargetInfo target, Ability ability, bool throwMessages = false)
	{
		return true;
	}

	public virtual bool ValidateTarget(LocalTargetInfo target, Ability ability, bool throwMessages = false)
	{
		return true;
	}

	public virtual bool CanApplyOn(LocalTargetInfo target, Ability ability, bool throwMessages = false)
	{
		return true;
	}

	public virtual string ExtraLabelMouseAttachment(LocalTargetInfo target, Ability ability)
	{
		return null;
	}

	public virtual void GizmoUpdateOnMouseover(Ability ability)
	{
	}

	public virtual void TargetingOnGUI(LocalTargetInfo target, Ability ability)
	{
	}
}
