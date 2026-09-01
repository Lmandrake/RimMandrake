using RimWorld;
using Verse;

namespace BigAndSmall;

public class ConditionalStatAffecter_InVacuum : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("BS_InVacuum"));

	public override bool Applies(StatRequest req)
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		Thing thing = ((StatRequest)(ref req)).Thing;
		if (thing != null && thing.Spawned)
		{
			Map map = ((StatRequest)(ref req)).Thing.Map;
			if (map != null && MapGenUtility.BiomeAt(map, ((StatRequest)(ref req)).Thing.Position)?.inVacuum == true)
			{
				return true;
			}
		}
		return false;
	}
}
