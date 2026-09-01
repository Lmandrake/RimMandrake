using RimWorld;
using Verse;

namespace VEF.Genes;

public class ConditionalStatAffecter_InVacuum : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("VGE_StatsReport_InVacuum"));

	public override bool Applies(StatRequest req)
	{
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		if (!ModsConfig.OdysseyActive)
		{
			return false;
		}
		Pawn val;
		if (((StatRequest)(ref req)).HasThing && (val = (Pawn)/*isinst with value type is only supported in some contexts*/) != null && ((Thing)val).Map != null && VacuumUtility.GetVacuum(((Thing)val).Position, ((Thing)val).Map) > 0f)
		{
			return true;
		}
		return false;
	}
}
