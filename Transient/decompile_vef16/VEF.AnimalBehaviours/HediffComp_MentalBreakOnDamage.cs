using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_MentalBreakOnDamage : HediffComp
{
	public HediffCompProperties_MentalBreakOnDamage Props => (HediffCompProperties_MentalBreakOnDamage)(object)base.props;

	public override void Notify_PawnPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).Notify_PawnPostApplyDamage(dinfo, totalDamageDealt);
		if (((DamageInfo)(ref dinfo)).Def == Props.damageTypeReceived && ((Thing)((Hediff)base.parent).pawn).Map != null)
		{
			((Hediff)base.parent).pawn.mindState.mentalBreaker.TryDoMentalBreak(TaggedString.op_Implicit(Translator.Translate(Props.reason)), Props.mentalBreak);
		}
	}
}
