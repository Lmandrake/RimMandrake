using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Buildings;

public class PlaceWorker_AttachedToWallMultiCell : PlaceWorker
{
	public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 centerPos, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Invalid comparison between Unknown and I4
		//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_018c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0191: Unknown result type (might be due to invalid IL or missing references)
		//IL_0196: Unknown result type (might be due to invalid IL or missing references)
		//IL_0179: Unknown result type (might be due to invalid IL or missing references)
		//IL_017e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0183: Unknown result type (might be due to invalid IL or missing references)
		//IL_014f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0155: Invalid comparison between Unknown and I4
		List<IntVec3> list = GenAdj.CellsOccupiedBy(centerPos, rot, checkingDef.Size).ToList();
		foreach (IntVec3 item in list)
		{
			List<Thing> thingList = GridsUtility.GetThingList(item, map);
			for (int i = 0; i < thingList.Count; i++)
			{
				Thing val = thingList[i];
				BuildableDef obj = GenConstruct.BuiltDefOf(val.def);
				ThingDef val2 = (ThingDef)(object)((obj is ThingDef) ? obj : null);
				if (val2 != null && val2.building != null)
				{
					if ((int)val2.Fillage == 2)
					{
						return AcceptanceReport.op_Implicit(false);
					}
					if (val2.building.isAttachment && val.Rotation == rot)
					{
						return AcceptanceReport.op_Implicit(Translator.Translate("SomethingPlacedOnThisWall"));
					}
				}
			}
			IntVec3 val3 = item + GenAdj.CardinalDirections[((Rot4)(ref rot)).AsInt];
			if (list.Contains(val3))
			{
				continue;
			}
			if (!GenGrid.InBounds(val3, map))
			{
				return AcceptanceReport.op_Implicit(false);
			}
			thingList = GridsUtility.GetThingList(val3, map).ToList();
			bool flag = false;
			bool flag2 = false;
			for (int j = 0; j < thingList.Count; j++)
			{
				BuildableDef obj2 = GenConstruct.BuiltDefOf(thingList[j].def);
				ThingDef val4 = (ThingDef)(object)((obj2 is ThingDef) ? obj2 : null);
				if (val4 != null && val4.building != null)
				{
					if (!val4.building.supportsWallAttachments)
					{
						flag2 = true;
					}
					else if ((int)val4.Fillage == 2)
					{
						flag = true;
						break;
					}
				}
			}
			if (!flag)
			{
				if (flag2)
				{
					return AcceptanceReport.op_Implicit(Translator.Translate("CannotSupportAttachment"));
				}
				return AcceptanceReport.op_Implicit(Translator.Translate("MustPlaceOnWall"));
			}
		}
		return AcceptanceReport.op_Implicit(true);
	}
}
