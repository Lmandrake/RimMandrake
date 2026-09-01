using RimWorld;
using Verse;

namespace VEF.Genes;

public class ConditionalStatAffecter_BelowZero : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("VGE_StatsReport_Below0"));

	public override bool Applies(StatRequest req)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		if (!ModsConfig.BiotechActive)
		{
			return false;
		}
		Pawn val;
		if (((StatRequest)(ref req)).HasThing && (val = (Pawn)/*isinst with value type is only supported in some contexts*/) != null && ((Thing)val).Map != null)
		{
			RegionAndRoomUpdater regionAndRoomUpdater = ((Thing)val).Map.regionAndRoomUpdater;
			if (regionAndRoomUpdater != null && regionAndRoomUpdater.Enabled && GridsUtility.GetTemperature(((Thing)val).Position, ((Thing)val).Map) < 0f)
			{
				return true;
			}
		}
		return false;
	}
}
