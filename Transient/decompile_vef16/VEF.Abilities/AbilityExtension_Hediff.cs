using RimWorld;
using Verse;

namespace VEF.Abilities;

public class AbilityExtension_Hediff : AbilityExtension_AbilityMod
{
	public HediffDef hediff;

	public BodyPartDef bodyPartToApply;

	public float severity = -1f;

	public bool applyAuto = true;

	public StatDef durationMultiplier;

	public bool durationMultiplierFromCaster;

	public bool targetOnlyEnemies;

	public bool applyToCaster;

	public override bool ValidateTarget(LocalTargetInfo target, Ability ability, bool throwMessages = false)
	{
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		if (targetOnlyEnemies && ((LocalTargetInfo)(ref target)).Thing != null && !GenHostility.HostileTo(((LocalTargetInfo)(ref target)).Thing, (Thing)(object)ability.pawn))
		{
			if (throwMessages)
			{
				Messages.Message(TaggedString.op_Implicit(Translator.Translate("VFEA.TargetMustBeHostile")), LookTargets.op_Implicit(((LocalTargetInfo)(ref target)).Thing), MessageTypeDefOf.CautionInput, (Quest)null, true);
			}
			return false;
		}
		return base.ValidateTarget(target, ability, throwMessages);
	}
}
