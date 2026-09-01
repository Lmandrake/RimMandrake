using RimWorld;
using Verse;

namespace VEF.Genes;

public class ConditionalStatAffecter_InPain : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("VGE_StatsReport_InPain"));

	public override bool Applies(StatRequest req)
	{
		if (!ModsConfig.BiotechActive)
		{
			return false;
		}
		if (((StatRequest)(ref req)).HasThing && ((StatRequest)(ref req)).Thing.Spawned)
		{
			Thing thing = ((StatRequest)(ref req)).Thing;
			return ((Pawn)((thing is Pawn) ? thing : null)).health.hediffSet.PainTotal > 0f;
		}
		return false;
	}
}
