using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Abilities;

public class Verb_CastAbility : Verb
{
	public Ability ability;

	protected override bool TryCastShot()
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		if (ability.IsEnabledForPawn(out var _))
		{
			Ability obj = ability;
			GlobalTargetInfo[] array = new GlobalTargetInfo[1];
			LocalTargetInfo val = ((Verb)this).CurrentTarget;
			GlobalTargetInfo val2;
			if (!((LocalTargetInfo)(ref val)).IsValid)
			{
				val = ((Verb)this).CurrentDestination;
				val2 = ((LocalTargetInfo)(ref val)).ToGlobalTargetInfo(((Verb)this).Caster.Map);
			}
			else
			{
				val = ((Verb)this).CurrentTarget;
				val2 = ((LocalTargetInfo)(ref val)).ToGlobalTargetInfo(((Verb)this).Caster.Map);
			}
			array[0] = val2;
			obj.Cast((GlobalTargetInfo[])(object)array);
			return true;
		}
		return false;
	}

	private void StartAbilityJob(LocalTargetInfo castTarg, LocalTargetInfo destTarg)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		if (((LocalTargetInfo)(ref castTarg)).IsValid && !((LocalTargetInfo)(ref destTarg)).IsValid)
		{
			ability.CreateCastJob(castTarg);
		}
		if (!((LocalTargetInfo)(ref castTarg)).IsValid && ((LocalTargetInfo)(ref destTarg)).IsValid)
		{
			ability.CreateCastJob(destTarg);
		}
		if (((LocalTargetInfo)(ref castTarg)).IsValid && ((LocalTargetInfo)(ref destTarg)).IsValid)
		{
			ability.CreateCastJob(((LocalTargetInfo)(ref castTarg)).ToGlobalTargetInfo(((Thing)ability.pawn).Map), ((LocalTargetInfo)(ref destTarg)).ToGlobalTargetInfo(((Thing)ability.pawn).Map));
		}
	}

	public override bool TryStartCastOn(LocalTargetInfo castTarg, LocalTargetInfo destTarg, bool surpriseAttack = false, bool canHitNonTargetPawns = true, bool preventFriendlyFire = false, bool nonInterruptingSelfCast = false)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		if (((Verb)this).TryStartCastOn(castTarg, destTarg, surpriseAttack, canHitNonTargetPawns, preventFriendlyFire, false))
		{
			StartAbilityJob(castTarg, destTarg);
			return true;
		}
		return false;
	}

	public override void OrderForceTarget(LocalTargetInfo target)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		((Verb)this).OrderForceTarget(target);
		ability.currentTargetingIndex = -1;
		ability.currentTargets = (GlobalTargetInfo[])(object)new GlobalTargetInfo[ability.def.targetCount];
		ability.OrderForceTarget(target);
	}

	public override void OnGUI(LocalTargetInfo target)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawAttachmentExtraLabel(target);
	}

	protected void DrawAttachmentExtraLabel(LocalTargetInfo target)
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		foreach (AbilityExtension_AbilityMod abilityModExtension in ability.AbilityModExtensions)
		{
			string text = abilityModExtension.ExtraLabelMouseAttachment(target, ability);
			if (!GenText.NullOrEmpty(text))
			{
				Widgets.MouseAttachedLabel(text, 0f, 0f, (Color?)null);
				break;
			}
		}
	}

	public override void ExposeData()
	{
		((Verb)this).ExposeData();
		Scribe_References.Look<Ability>(ref ability, "ability", false);
	}
}
