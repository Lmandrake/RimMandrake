using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class AbilityExtension_SocialInteraction : AbilityExtension_AbilityMod
{
	public InteractionDef interactionDef;

	public bool canApplyToMentallyBroken;

	public bool canApplyToUnconscious;

	public override void Cast(GlobalTargetInfo[] targets, Ability ability)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		for (int i = 0; i < targets.Length; i++)
		{
			GlobalTargetInfo val = targets[i];
			Thing thing = ((GlobalTargetInfo)(ref val)).Thing;
			Pawn val2 = (Pawn)(object)((thing is Pawn) ? thing : null);
			if (val2 != null && ability.pawn != val2)
			{
				Pawn_InteractionsTracker interactions = ability.pawn.interactions;
				if (interactions != null)
				{
					interactions.TryInteractWith(val2, interactionDef);
				}
			}
		}
	}

	public override bool CanApplyOn(LocalTargetInfo target, Ability ability, bool throwMessages = false)
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		Thing thing = ((LocalTargetInfo)(ref target)).Thing;
		if (((thing != null) ? thing.Map : null) != null)
		{
			return Valid((GlobalTargetInfo[])(object)new GlobalTargetInfo[1] { ((LocalTargetInfo)(ref target)).ToGlobalTargetInfo(((LocalTargetInfo)(ref target)).Thing.Map) }, ability, throwMessages);
		}
		return false;
	}

	public override bool Valid(GlobalTargetInfo[] targets, Ability ability, bool throwMessages = false)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		for (int i = 0; i < targets.Length; i++)
		{
			GlobalTargetInfo val = targets[i];
			Thing thing = ((GlobalTargetInfo)(ref val)).Thing;
			Pawn val2 = (Pawn)(object)((thing is Pawn) ? thing : null);
			if (val2 != null)
			{
				if (!canApplyToMentallyBroken && !AbilityUtility.ValidateNoMentalState(val2, throwMessages, (Ability)null))
				{
					return false;
				}
				if (!AbilityUtility.ValidateIsAwake(val2, true, (Ability)null))
				{
					return false;
				}
				if (!canApplyToUnconscious && !AbilityUtility.ValidateIsConscious(val2, throwMessages, (Ability)null))
				{
					return false;
				}
			}
		}
		return base.Valid(targets, ability, throwMessages);
	}
}
