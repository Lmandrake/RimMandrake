using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class SoulCollector : HediffWithComps
{
	protected readonly SoulEnergyTracker soulTracker = new SoulEnergyTracker();

	private static int WarnedAboutLowPsyFocusCount;

	protected SoulResourceHediff Resource => soulTracker.Resource(((Hediff)this).pawn);

	public override string LabelInBrackets
	{
		get
		{
			try
			{
				return GenText.ToStringPercent(((Hediff)this).Severity);
			}
			catch
			{
				return "SPIRIT POWER CALCULATION FAILED";
			}
		}
	}

	public void AddSoulPowerDirect(float amount, float exponentialFalloff = 2.5f)
	{
		float num = ((Hediff)this).pawn.GetAllPawnExtensions().Sum((PawnExtension x) => x.soulFalloffStart);
		float num2 = 0f;
		num2 += num;
		num2 += BigSmallMod.settings.soulPowerFalloffOffset;
		float num3 = ((Hediff)this).Severity - num2;
		if (num3 >= 1f)
		{
			amount /= Mathf.Pow(num3, exponentialFalloff);
		}
		((Hediff)this).Severity = ((Hediff)this).Severity + amount;
	}

	public float AddPawnSoul(Pawn target, SiphonSoul parms, bool verbose = false)
	{
		//IL_02aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_02bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_03d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_03e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_03e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_061a: Unknown result type (might be due to invalid IL or missing references)
		//IL_062b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0630: Unknown result type (might be due to invalid IL or missing references)
		//IL_0635: Unknown result type (might be due to invalid IL or missing references)
		//IL_0637: Unknown result type (might be due to invalid IL or missing references)
		//IL_0646: Unknown result type (might be due to invalid IL or missing references)
		//IL_04d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_04e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_04f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0501: Unknown result type (might be due to invalid IL or missing references)
		//IL_0506: Unknown result type (might be due to invalid IL or missing references)
		//IL_05ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_05b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_05c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_05d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_05da: Unknown result type (might be due to invalid IL or missing references)
		//IL_0549: Unknown result type (might be due to invalid IL or missing references)
		//IL_0550: Unknown result type (might be due to invalid IL or missing references)
		//IL_0561: Unknown result type (might be due to invalid IL or missing references)
		//IL_0571: Unknown result type (might be due to invalid IL or missing references)
		//IL_0576: Unknown result type (might be due to invalid IL or missing references)
		Pawn_GeneTracker genes = target.genes;
		int num = ((genes != null) ? genes.GenesListForReading.Sum((Gene x) => x.def.biostatArc) : 0);
		float num2 = Mathf.Lerp(1f, num switch
		{
			0 => 1f, 
			1 => 1.4f, 
			2 => 1.6f, 
			3 => 1.75f, 
			4 => 1.9f, 
			_ => 2f, 
		}, parms.architeGeneFactor);
		float num3 = parms.targetPsyFocusOffset;
		if (num3 < 0f)
		{
			num3 /= (float)(1 + num);
		}
		float num4 = StatExtension.GetStatValue((Thing)(object)target, StatDefOf.PsychicSensitivity, true, -1) + num3;
		num4 = Mathf.Max(parms.minimumBaseGain, num4);
		num4 = Mathf.Min(parms.fromTargetPsyfocusFactor_Max, num4);
		num4 += parms.gainOffset * 0.01f;
		num4 *= 0.01f;
		float num5 = num4;
		if (target != null)
		{
			RaceProperties raceProps = target.RaceProps;
			if (((raceProps != null) ? new bool?(raceProps.Animal) : ((bool?)null)) == true)
			{
				num5 /= 5f;
			}
		}
		num5 *= num2;
		num5 *= parms.fromTargetPsyfocusFactor;
		float num6 = ((Hediff)this).pawn.GetAllPawnExtensions().Sum((PawnExtension x) => x.soulFalloffStart);
		float num7 = 1f + ((Hediff)this).pawn.GetAllPawnExtensions().Sum((PawnExtension x) => x.siphonFactorOffset);
		float num8 = 1f + ((Hediff)this).pawn.GetAllPawnExtensions().Sum((PawnExtension x) => x.siphonSkillFactorOffset);
		float num9 = num8 * parms.gainSkill;
		float num10 = num4;
		float num11 = StatExtension.GetStatValue((Thing)(object)target, BSDefs.BS_SoulPower, true, -1) * parms.fromTargetSoulFactor;
		num11 *= 0.01f;
		float num12 = (num5 + num11) * parms.gainFactor * num7;
		if (Resource != null)
		{
			Resource.Value += num12 * 50f;
		}
		num12 *= BigSmallMod.settings.soulPowerGainMultiplier;
		if (WarnedAboutLowPsyFocusCount < 1 && parms.type == SiphonType.ConsumeSoul && ((Thing)((Hediff)this).pawn).Faction == Faction.OfPlayerSilentFail && num12 <= 0.011f)
		{
			WarnedAboutLowPsyFocusCount++;
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_LowPsyfocusTarget", NamedArgument.op_Implicit(((Hediff)this).pawn.Name.ToStringShort), NamedArgument.op_Implicit(target.Name.ToStringShort))), LookTargets.op_Implicit((Thing)(object)((Hediff)this).pawn), MessageTypeDefOf.NeutralEvent, true);
		}
		float num13 = num12;
		float num14 = 0f;
		num14 += num6;
		num14 += BigSmallMod.settings.soulPowerFalloffOffset;
		float num15 = ((Hediff)this).Severity - num14;
		if (num15 >= 1f)
		{
			num13 /= Mathf.Pow(num15, 2.5f);
		}
		((Hediff)this).Severity = ((Hediff)this).Severity + num13;
		Pawn_NeedsTracker needs = ((Hediff)this).pawn.needs;
		Need_KillThirst val = ((needs != null) ? needs.TryGetNeed<Need_KillThirst>() : null);
		if (val != null && (parms.type == SiphonType.KillingBlow || parms.type == SiphonType.ConsumeSoul))
		{
			((Need)val).CurLevelPercentage = 1f;
		}
		Pawn_PsychicEntropyTracker psychicEntropy = target.psychicEntropy;
		if (psychicEntropy != null)
		{
			psychicEntropy.OffsetPsyfocusDirectly(num4 * 2f);
		}
		if (verbose || num13 > 0.2f)
		{
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_GainedSoulPower", NamedArgument.op_Implicit(((Hediff)this).pawn.Name.ToStringShort), NamedArgument.op_Implicit($"{num13 * 100f:f1}%"), NamedArgument.op_Implicit(((Def)BSDefs.BS_SoulPower).LabelCap), NamedArgument.op_Implicit(target.Name.ToStringShort))), LookTargets.op_Implicit((Thing)(object)((Hediff)this).pawn), MessageTypeDefOf.PositiveEvent, true);
		}
		if (num9 > 0f && target.skills != null)
		{
			float num16 = num10 * num9;
			num16 = Mathf.Min(num16, parms.maxXpDrainPercent);
			float num17 = default(float);
			SkillDef philophagySkillAndXpTransfer = PsychicRitualUtility.GetPhilophagySkillAndXpTransfer(((Hediff)this).pawn, target, num16, ref num17);
			num17 = Mathf.Min(num17, parms.maxXPDrain * num8);
			if (philophagySkillAndXpTransfer == null)
			{
				Log.Warning("Could not find a skill to transfer xp to.");
			}
			else
			{
				SkillRecord skill = ((Hediff)this).pawn.skills.GetSkill(philophagySkillAndXpTransfer);
				if (skill != null)
				{
					skill.Learn(num17, false, true);
				}
				SkillRecord skill2 = target.skills.GetSkill(philophagySkillAndXpTransfer);
				if (skill2 != null)
				{
					skill2.Learn(0f - num17, true, true);
				}
				if (verbose || num17 >= 2500f)
				{
					if (parms.type == SiphonType.KillingBlow)
					{
						Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_StoleSkillAmount_Attack", NamedArgument.op_Implicit(((Hediff)this).pawn.Name.ToStringShort), NamedArgument.op_Implicit(num17), NamedArgument.op_Implicit(((Def)skill.def).label), NamedArgument.op_Implicit(target.Name.ToStringShort))), LookTargets.op_Implicit((Thing)(object)((Hediff)this).pawn), MessageTypeDefOf.PositiveEvent, true);
					}
					else if (parms.type == SiphonType.Influence)
					{
						Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_StoleSkillAmount_Influence", NamedArgument.op_Implicit(((Hediff)this).pawn.Name.ToStringShort), NamedArgument.op_Implicit(num17), NamedArgument.op_Implicit(((Def)skill.def).label), NamedArgument.op_Implicit(target.Name.ToStringShort))), LookTargets.op_Implicit((Thing)(object)((Hediff)this).pawn), MessageTypeDefOf.PositiveEvent, true);
					}
					else
					{
						Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_StoleSkillAmount", NamedArgument.op_Implicit(((Hediff)this).pawn.Name.ToStringShort), NamedArgument.op_Implicit(num17), NamedArgument.op_Implicit(((Def)skill.def).label), NamedArgument.op_Implicit(target.Name.ToStringShort))), LookTargets.op_Implicit((Thing)(object)((Hediff)this).pawn), MessageTypeDefOf.PositiveEvent, true);
					}
				}
			}
		}
		if (((Thing)target).Spawned && (parms.type == SiphonType.KillingBlow || parms.type == SiphonType.ConsumeSoul))
		{
			for (int i = 0; i < 5; i++)
			{
				IntVec3 val2 = ((Thing)target).Position + GenAdj.AdjacentCellsAndInside[Rand.Range(0, 8)];
				if (GenGrid.InBounds(val2, ((Thing)target).Map))
				{
					FilthMaker.TryMakeFilth(val2, ((Thing)target).Map, ThingDefOf.Filth_Ash, 1, (FilthSourceFlags)0, true);
				}
			}
		}
		return num13;
	}
}
