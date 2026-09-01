using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

/// <summary>
///  Basically improved version of auto-clotting.
/// </summary>
public class Gene_AutoTending : Gene
{
	private static readonly FloatRange TendingQualityRange = new FloatRange(0.35f, 0.75f);

	public override void TickInterval(int delta)
	{
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		((Gene)this).TickInterval(delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)base.pawn, 360, delta))
		{
			return;
		}
		List<Hediff> hediffs = base.pawn.health.hediffSet.hediffs;
		for (int num = hediffs.Count - 1; num >= 0; num--)
		{
			Hediff val = hediffs[num];
			if (val.Bleeding || (val.def.tendable && val is Hediff_Injury && val.TendableNow(false)))
			{
				Hediff obj = hediffs[num];
				FloatRange tendingQualityRange = TendingQualityRange;
				float randomInRange = ((FloatRange)(ref tendingQualityRange)).RandomInRange;
				tendingQualityRange = TendingQualityRange;
				obj.Tended(randomInRange, ((FloatRange)(ref tendingQualityRange)).TrueMax, 1);
			}
		}
	}
}
