using RimWorld;
using Verse;

namespace VEF.Genes;

public class ConditionalStatAffecter_AnyLightSensitivity : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("VGE_StatsReport_AnyLightSensitivity"));

	public override bool Applies(StatRequest req)
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		if (!ModsConfig.BiotechActive)
		{
			return false;
		}
		if (((StatRequest)(ref req)).HasThing && ((StatRequest)(ref req)).Thing.Spawned)
		{
			return ((StatRequest)(ref req)).Thing.Map.glowGrid.GroundGlowAt(((StatRequest)(ref req)).Thing.Position, false, false) >= 0.11f;
		}
		return false;
	}
}
