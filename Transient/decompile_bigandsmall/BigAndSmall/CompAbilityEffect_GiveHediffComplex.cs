using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompAbilityEffect_GiveHediffComplex : CompAbilityEffect_WithDuration
{
	public CompProperties_AbilityGiveHediffComplex Props => (CompProperties_AbilityGiveHediffComplex)(object)((AbilityComp)this).props;

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect)this).Apply(target, dest);
		if (!((CompProperties_AbilityGiveHediff)Props).ignoreSelf || ((LocalTargetInfo)(ref target)).Pawn != ((AbilityComp)this).parent.pawn)
		{
			if (!((CompProperties_AbilityGiveHediff)Props).onlyApplyToSelf && ((CompProperties_AbilityGiveHediff)Props).applyToTarget)
			{
				ApplyInner(((LocalTargetInfo)(ref target)).Pawn, ((AbilityComp)this).parent.pawn);
			}
			if (((CompProperties_AbilityGiveHediff)Props).applyToSelf || ((CompProperties_AbilityGiveHediff)Props).onlyApplyToSelf)
			{
				ApplyInner(((AbilityComp)this).parent.pawn, ((LocalTargetInfo)(ref target)).Pawn);
			}
		}
	}

	protected void ApplyInner(Pawn target, Pawn other)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		if (target == null)
		{
			return;
		}
		if (TryResist(target))
		{
			MoteMaker.ThrowText(((Thing)target).DrawPos, ((Thing)target).Map, TaggedString.op_Implicit(Translator.Translate("Resisted")), -1f);
			return;
		}
		if (((CompProperties_AbilityGiveHediff)Props).replaceExisting)
		{
			Hediff firstHediffOfDef = target.health.hediffSet.GetFirstHediffOfDef(((CompProperties_AbilityGiveHediff)Props).hediffDef, false);
			if (firstHediffOfDef != null)
			{
				target.health.RemoveHediff(firstHediffOfDef);
			}
		}
		Hediff val = HediffMaker.MakeHediff(((CompProperties_AbilityGiveHediff)Props).hediffDef, target, ((CompProperties_AbilityGiveHediff)Props).onlyBrain ? target.health.hediffSet.GetBrain() : null);
		HediffComp_Disappears val2 = HediffUtility.TryGetComp<HediffComp_Disappears>(val);
		if (val2 != null)
		{
			val2.ticksToDisappear = GenTicks.SecondsToTicks(((CompAbilityEffect_WithDuration)this).GetDurationSeconds(target));
		}
		SetSeverity(target, val);
		HediffComp_Link val3 = HediffUtility.TryGetComp<HediffComp_Link>(val);
		if (val3 != null)
		{
			val3.other = (Thing)(object)other;
			val3.drawConnection = target == ((AbilityComp)this).parent.pawn;
		}
		target.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
	}

	private void SetSeverity(Pawn target, Hediff hediff)
	{
		if (((CompProperties_AbilityGiveHediff)Props).severity >= 0f)
		{
			hediff.Severity = ((CompProperties_AbilityGiveHediff)Props).severity;
		}
		foreach (CompProperties_AbilityGiveHediffComplex.OffsetSeverityByStats offsetSeverityByStat in Props.offsetSeverityByStats)
		{
			if (offsetSeverityByStat.stat != null)
			{
				float num = StatExtension.GetStatValue((Thing)(object)target, offsetSeverityByStat.stat, true, -1) * offsetSeverityByStat.multiplier;
				hediff.Severity += num;
			}
		}
		if (Props.offsetSeverityBodySizeFactor != 0f)
		{
			hediff.Severity += target.BodySize * Props.offsetSeverityBodySizeFactor;
		}
		SetSeverityLegacy(target, hediff);
	}

	private void SetSeverityLegacy(Pawn target, Hediff hediff)
	{
		if (Props.offsetSeverityByStat != null)
		{
			float statValue = StatExtension.GetStatValue((Thing)(object)target, Props.offsetSeverityByStat, true, -1);
			hediff.Severity += statValue;
		}
		if (Props.offsetSeverityBodySize)
		{
			hediff.Severity += target.BodySize;
		}
	}

	protected virtual bool TryResist(Pawn pawn)
	{
		return false;
	}

	public override bool AICanTargetNow(LocalTargetInfo target)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		if (((CompProperties_AbilityGiveHediff)Props).onlyApplyToSelf)
		{
			target = LocalTargetInfo.op_Implicit((Thing)(object)((AbilityComp)this).parent.pawn);
		}
		if (!Props.hediffStacks && ((LocalTargetInfo)(ref target)).Pawn != null && ((LocalTargetInfo)(ref target)).Pawn.health.hediffSet.GetFirstHediffOfDef(((CompProperties_AbilityGiveHediff)Props).hediffDef, false) != null)
		{
			return false;
		}
		return ((LocalTargetInfo)(ref target)).Pawn != null;
	}
}
