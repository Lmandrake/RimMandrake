using RimWorld;
using Verse;

namespace VEF.Utils;

public static class FormatUtils
{
	public static string ToStringTicksToPeriodSpecific(this int ticks)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		if (ticks < 2500)
		{
			return TaggedString.op_Implicit(GenText.ToStringDecimalIfSmall(GenTicks.TicksToSeconds(ticks)) + Translator.Translate("LetterSecond"));
		}
		return GenDate.ToStringTicksToPeriod(ticks, true, false, true, true, false);
	}
}
