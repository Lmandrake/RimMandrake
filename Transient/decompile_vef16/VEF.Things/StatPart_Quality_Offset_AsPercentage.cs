using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Things;

[HarmonyPatch]
public class StatPart_Quality_Offset_AsPercentage : StatPart_Quality_Offset
{
	private static Func<StatPart_Quality_Offset, StatRequest, bool> applyToMethod = NonPublicMethods.MakeDelegate<Func<StatPart_Quality_Offset, StatRequest, bool>>(AccessToolsExtensions.Method(typeof(StatPart_Quality_Offset), "ApplyTo", (Type[])null, (Type[])null));

	private static Func<StatPart_Quality_Offset, QualityCategory, float> qualityOffsetMethod = NonPublicMethods.MakeDelegate<Func<StatPart_Quality_Offset, QualityCategory, float>>(AccessToolsExtensions.Method(typeof(StatPart_Quality_Offset), "QualityOffset", (Type[])null, (Type[])null));

	public override string ExplanationPart(StatRequest req)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		if (!applyToMethod((StatPart_Quality_Offset)(object)this, req))
		{
			return null;
		}
		return string.Format("{0}: {1}", Translator.Translate("StatsReport_QualityOffset"), GenText.ToStringPercentSigned(qualityOffsetMethod((StatPart_Quality_Offset)(object)this, ((StatRequest)(ref req)).QualityCategory)));
	}
}
