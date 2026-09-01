using RimWorld;
using Verse;

namespace VEF.Genes;

public class ConditionalStatAffecter_InSpace : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("VGE_StatsReport_InSpace"));

	public override bool Applies(StatRequest req)
	{
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		if (!ModsConfig.OdysseyActive)
		{
			return false;
		}
		Pawn val;
		if (((StatRequest)(ref req)).HasThing && (val = (Pawn)/*isinst with value type is only supported in some contexts*/) != null && ((Thing)val).Position != IntVec3.Invalid)
		{
			Map map = ((Thing)val).Map;
			if (map != null && MapGenUtility.BiomeAt(map, ((Thing)val).Position)?.inVacuum == true)
			{
				return true;
			}
		}
		return false;
	}
}
