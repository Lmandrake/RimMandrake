using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public abstract class CompAbilityEffect_SlimeEngluf_Abstract : CompAbilityEffect
{
	public abstract CompProperties_AbilityEngluf_Abstract Props { get; }

	public override bool AICanTargetNow(LocalTargetInfo target)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return ((CompAbilityEffect)this).Valid(target, false);
	}

	public override bool Valid(LocalTargetInfo target, bool throwMessages = false)
	{
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0126: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0194: Unknown result type (might be due to invalid IL or missing references)
		//IL_020d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0212: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn == null)
		{
			return false;
		}
		Ability parent = ((AbilityComp)this).parent;
		float? obj;
		if (parent == null)
		{
			obj = null;
		}
		else
		{
			Pawn pawn2 = parent.pawn;
			if (pawn2 == null)
			{
				obj = null;
			}
			else
			{
				Pawn_HealthTracker health = pawn2.health;
				if (health == null)
				{
					obj = null;
				}
				else
				{
					HediffSet hediffSet = health.hediffSet;
					obj = ((hediffSet != null) ? new float?(hediffSet.PainTotal) : ((float?)null));
				}
			}
		}
		if ((double?)obj > 0.5)
		{
			if (throwMessages)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_InTooMuchPain", NamedArgument.op_Implicit(((Entity)pawn).Label))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.RejectInput, false);
			}
			return false;
		}
		if (EngulfHediff.PowScale(pawn.BodySize) > EngulfHediff.PowScale(((AbilityComp)this).parent.pawn.BodySize) * Props.GetSizeThreshold(((AbilityComp)this).parent.pawn))
		{
			if (throwMessages)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_TooLargeToSwallow", NamedArgument.op_Implicit(((Entity)pawn).Label))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.RejectInput, false);
			}
			return false;
		}
		if (((AbilityComp)this).parent.pawn.health.capacities.CapableOf(BSDefs.Metabolism) && ((AbilityComp)this).parent.pawn.health.capacities.GetLevel(BSDefs.Metabolism) <= 0.55f)
		{
			Messages.Message(TaggedString.op_Implicit(Translator.Translate("DigestiveAbilityTooLow")), MessageTypeDefOf.RejectInput, false);
			return false;
		}
		Hediff firstHediffOfDef = ((AbilityComp)this).parent.pawn.health.hediffSet.GetFirstHediffOfDef(DefDatabase<HediffDef>.GetNamed("BS_Engulfed", true), false);
		if (firstHediffOfDef != null)
		{
			EngulfHediff engulfHediff = (EngulfHediff)(object)firstHediffOfDef;
			if (engulfHediff.TotalMass + EngulfHediff.PowScale(pawn.BodySize) > engulfHediff.MaxCapacity * 1.1f)
			{
				if (throwMessages)
				{
					Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_NotEnoughRoom", NamedArgument.op_Implicit(((Entity)pawn).Label))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.RejectInput, false);
				}
				return false;
			}
		}
		return true;
	}

	public void DoEngulf(Pawn attacker, Pawn victim)
	{
		IEnumerable<HediffDef> source = DefDatabase<HediffDef>.AllDefsListForReading.Where((HediffDef x) => ((Def)x).defName == "BS_Engulfed");
		if (source.Count() == 0)
		{
			Log.Error("BS_Engulfed hediff not found in the library.");
			return;
		}
		HediffDef val = source.First();
		EngulfHediff engulfHediff;
		if (attacker.health.hediffSet.HasHediff(val, false))
		{
			engulfHediff = (EngulfHediff)(object)attacker.health.hediffSet.GetFirstHediffOfDef(val, false);
			((Hediff)engulfHediff).Severity = 1f;
		}
		else
		{
			attacker.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			engulfHediff = (EngulfHediff)(object)attacker.health.hediffSet.GetFirstHediffOfDef(val, false);
		}
		engulfHediff.selfDamageMultiplier = Props.selfDamageMultiplier;
		engulfHediff.internalBaseDamage = Props.internalBaseDamage;
		engulfHediff.baseCapacity = (Props.max.HasValue ? Props.max.Value : Props.GetSizeThreshold(((AbilityComp)this).parent.pawn));
		engulfHediff.damageDef = Props.damageDef;
		engulfHediff.alliesAttackBack = Props.alliesAttackBack;
		engulfHediff.dealsDamage = Props.dealsDamage;
		engulfHediff.healPerDay = Props.healPerDay;
		engulfHediff.regularHealingMultiplier = Props.regularHealingMultiplier;
		engulfHediff.healsScars = Props.healsScars;
		engulfHediff.canHealBrain = Props.canHealBrain;
		engulfHediff.bodyPartsRegeneratedPerDay = Props.bodyPartsRegeneratedPerDay;
		engulfHediff.Engulf((Thing)(object)victim);
	}
}
