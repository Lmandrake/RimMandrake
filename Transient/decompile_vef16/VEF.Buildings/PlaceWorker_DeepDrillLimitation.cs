using RimWorld;
using VEF.Things;
using Verse;

namespace VEF.Buildings;

public class PlaceWorker_DeepDrillLimitation : PlaceWorker
{
	public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		ThingDef nextResource = DeepDrillUtility.GetNextResource(loc, map);
		ThingDefExtension modExtension = ((Def)nextResource).GetModExtension<ThingDefExtension>();
		if (modExtension != null && !modExtension.allowDeepDrill)
		{
			return AcceptanceReport.op_Implicit(TranslatorFormattedStringExtensions.Translate("VFE_DeepDrillNo", NamedArgument.op_Implicit(((Def)nextResource).label)));
		}
		return AcceptanceReport.op_Implicit(true);
	}
}
