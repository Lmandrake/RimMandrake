using RimWorld;
using Verse;

namespace VEF.Apparels;

public class StatWorker_MultiplyBy100 : StatWorker
{
	public override string ValueToString(float val, bool finalized, ToStringNumberSense numberSense = 1)
	{
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		return ((StatWorker)this).ValueToString(val * 100f, finalized, numberSense);
	}
}
