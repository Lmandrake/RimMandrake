using System;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace BigAndSmall;

public class CompAbilityEffect_ConsumeSoul : CompAbilityEffect
{
	public CompProperties_ConsumeSoul Props => (CompProperties_ConsumeSoul)(object)((AbilityComp)this).props;

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect)this).Apply(target, dest);
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn != null)
		{
			DrainSoul(((AbilityComp)this).parent.pawn, pawn);
		}
	}

	public override bool CanApplyOn(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return ((CompAbilityEffect)this).Valid(target, false);
	}

	public override bool Valid(LocalTargetInfo target, bool throwMessages = false)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Invalid comparison between Unknown and I4
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn == null)
		{
			return false;
		}
		if (!AbilityUtility.ValidateMustBeHumanOrWildMan(pawn, throwMessages, ((AbilityComp)this).parent))
		{
			return false;
		}
		if (!pawn.Downed && (int)pawn.DevelopmentalStage > 2)
		{
			if (throwMessages)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantUseOnResistingPerson", NamedArgument.op_Implicit(((Def)((AbilityComp)this).parent.def).LabelCap))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.RejectInput, false);
			}
			return false;
		}
		if (WildManUtility.IsWildMan(pawn) && !pawn.IsPrisonerOfColony && !pawn.Downed)
		{
			if (throwMessages)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantUseOnResistingPerson", NamedArgument.op_Implicit(((Def)((AbilityComp)this).parent.def).LabelCap))), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.RejectInput, false);
			}
			return false;
		}
		if (pawn.health.hediffSet.HasHediff(BSDefs.BS_Soulless, false))
		{
			if (throwMessages)
			{
				Messages.Message(TaggedString.op_Implicit(Translator.Translate("BS_CannotUseOnSoulless")), LookTargets.op_Implicit((Thing)(object)pawn), MessageTypeDefOf.RejectInput, false);
			}
			return false;
		}
		return true;
	}

	public override string ExtraLabelMouseAttachment(LocalTargetInfo target)
	{
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn != null)
		{
			string text = null;
			if (GenHostility.HostileTo((Thing)(object)pawn, (Thing)(object)((AbilityComp)this).parent.pawn) && !pawn.Downed)
			{
				text = TaggedString.op_Implicit(text + TranslatorFormattedStringExtensions.Translate("MessageCantUseOnResistingPerson", NamedArgumentUtility.Named((object)((AbilityComp)this).parent.def, "ABILITY")));
			}
			return text;
		}
		return ((CompAbilityEffect)this).ExtraLabelMouseAttachment(target);
	}

	public override Window ConfirmationDialog(LocalTargetInfo target, Action confirmAction)
	{
		return null;
	}

	public void DrainSoul(Pawn attacker, Pawn victim)
	{
		Pawn_PsychicEntropyTracker psychicEntropy = attacker.psychicEntropy;
		if (psychicEntropy != null)
		{
			psychicEntropy.OffsetPsyfocusDirectly(1f);
		}
		MakeGetSoulCollectorHediff(attacker).AddPawnSoul(victim, Props.siphonSoul);
		Faction faction = ((Thing)victim).Faction;
		if (faction != null)
		{
			faction.TryAffectGoodwillWith(((Thing)attacker).Faction, -35, true, true, (HistoryEventDef)null, (GlobalTargetInfo?)null);
		}
		if (Props.doKill)
		{
			ApplySoulless(victim);
			((Thing)victim).Kill((DamageInfo?)null, (Hediff)null);
		}
		else if (Props.doEnslave)
		{
			ApplySoulless(victim);
			if (ModsConfig.IdeologyActive)
			{
				victim.guest.SetGuestStatus(((Thing)attacker).Faction, (GuestStatus)2);
			}
			else
			{
				victim.guest.resistance = 0f;
				victim.guest.CapturedBy(Faction.OfPlayer, attacker);
			}
		}
		HumanoidPawnScaler.GetCache(attacker, forceRefresh: true);
	}

	public static void ApplySoulless(Pawn victim)
	{
		if (victim != null)
		{
			RaceProperties raceProps = victim.RaceProps;
			if (((raceProps != null) ? new bool?(raceProps.Humanlike) : ((bool?)null)) == true && victim != null)
			{
				victim.health.AddHediff(BSDefs.BS_Soulless, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
	}

	public static SoulCollector MakeGetSoulCollectorHediff(Pawn attacker)
	{
		return Soul.GetOrAddSoulCollector(attacker);
	}
}
