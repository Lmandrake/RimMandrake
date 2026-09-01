using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class Regeneration : TickdownGene
{
	private const float baseHealingPerDayForSize1 = 8f;

	private const int tickFq = 1000;

	private const float healingPerEvent = 2f / 15f;

	protected virtual FloatRange TendingQualityRange { get; set; } = new FloatRange(0.5f, 1.3f);

	protected virtual bool TendsInjuries => true;

	public override void ResetCountdown()
	{
		tickDown = 1000;
	}

	public override void TickEvent()
	{
		//IL_0131: Unknown result type (might be due to invalid IL or missing references)
		//IL_0136: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = ((Gene)this).pawn;
		if ((pawn != null && pawn.Dead) || ((Gene)this).pawn?.health?.hediffSet == null)
		{
			return;
		}
		List<Hediff_Injury> allInjuries = HealthHelpers.GetAllInjuries(((Gene)this).pawn);
		if (GenCollection.Any<Hediff_Injury>(allInjuries))
		{
			float num = GetHealingAmount() * (2f / 15f);
			float num2 = allInjuries.Sum((Hediff_Injury x) => ((Hediff)x).Part.coverageAbsWithChildren + 0.0001f);
			float num3 = 0f;
			{
				foreach (Hediff_Injury item in allInjuries)
				{
					float num4 = num * ((((Hediff)item).Part.coverageAbsWithChildren + 0.0001f) / num2) * Rand.Range(0.5f, 1.5f);
					((Hediff)item).Heal(num4);
					num3 += num4;
					try
					{
						if (!TendsInjuries)
						{
							continue;
						}
						FloatRange tendingQualityRange;
						if (TendsInjuries && ((Hediff)item).TendableNow(false))
						{
							tendingQualityRange = TendingQualityRange;
							float randomInRange = ((FloatRange)(ref tendingQualityRange)).RandomInRange;
							tendingQualityRange = TendingQualityRange;
							((Hediff)item).Tended(randomInRange, ((FloatRange)(ref tendingQualityRange)).TrueMax, 1);
							continue;
						}
						HediffComp_TendDuration val = HediffUtility.TryGetComp<HediffComp_TendDuration>((Hediff)(object)item);
						if ((1u & ((val.tendQuality < 0.5f) ? 1u : 0u)) != 0)
						{
							tendingQualityRange = TendingQualityRange;
							val.tendQuality = ((FloatRange)(ref tendingQualityRange)).RandomInRange;
						}
					}
					catch (Exception ex)
					{
						Log.ErrorOnce("Unhandled exception trying to tend wound " + ex.Message + "\n" + ex.StackTrace, 346722245);
					}
				}
				return;
			}
		}
		Hediff_MissingPart missingPart = HealthHelpers.GetMissingPart(((Gene)this).pawn);
		if (missingPart != null)
		{
			BodyPartRecord part = ((Hediff)missingPart).Part;
			((Gene)this).pawn.health.RemoveHediff((Hediff)(object)missingPart);
			Hediff val2 = HediffMaker.MakeHediff(HediffDefOf.Misc, ((Gene)this).pawn, part);
			float partHealth = ((Gene)this).pawn.health.hediffSet.GetPartHealth(part);
			val2.Severity = partHealth * 0.85f;
			HediffComp_GetsPermanent val3 = HediffUtility.TryGetComp<HediffComp_GetsPermanent>(val2);
			if (val3 != null)
			{
				val3.IsPermanent = true;
				val3.SetPainCategory((PainCategory)0);
			}
			((Gene)this).pawn.health.AddHediff(val2, part, (DamageInfo?)null, (DamageResult)null);
			((Gene)this).pawn.health.Notify_HediffChanged(val2);
		}
	}

	protected virtual float GetHealingAmount()
	{
		float num = GetBaseHealingRate();
		Pawn pawn = ((Gene)this).pawn;
		if (pawn != null && pawn.BodySize > 1.2f)
		{
			num *= ((Gene)this).pawn.HealthScale;
		}
		return num;
	}

	protected float GetBaseHealingRate()
	{
		float num = StatExtension.GetStatValue((Thing)(object)((Gene)this).pawn, StatDefOf.InjuryHealingFactor, true, 1000);
		if (num > 1f)
		{
			num = 1f + (num - 1f) * 0.5f;
		}
		return num;
	}
}
