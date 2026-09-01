using System;
using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class AbilityExtension_ConfirmationMessage : AbilityExtension_AbilityMod
{
	public string message;

	public override void PreCast(GlobalTargetInfo[] target, Ability ability, ref bool startAbilityJobImmediately, Action startJobAction)
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		base.PreCast(target, ability, ref startAbilityJobImmediately, startJobAction);
		startAbilityJobImmediately = false;
		Find.WindowStack.Add((Window)(object)Dialog_MessageBox.CreateConfirmation(GrammarResolverSimpleStringExtensions.Formatted(message, NamedArgumentUtility.Named((object)ability.pawn, "PAWN")), startJobAction, false, (string)null, (WindowLayer)1));
	}
}
