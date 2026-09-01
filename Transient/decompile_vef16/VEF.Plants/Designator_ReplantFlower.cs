using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Plants;

public class Designator_ReplantFlower : Designator_Install
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("VPE_ReplantFlower"));

	public override string Desc => TaggedString.op_Implicit(Translator.Translate("VPE_ReplantFlower_Desc"));

	public Designator_ReplantFlower()
	{
		((Command)this).icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Gizmo/ReplantFlower", true);
		((Designator)this).soundSucceeded = SoundDefOf.Designate_ExtractTree;
	}

	public override AcceptanceReport CanDesignateCell(IntVec3 c)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		//IL_0162: Unknown result type (might be due to invalid IL or missing references)
		//IL_0139: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0143: Unknown result type (might be due to invalid IL or missing references)
		//IL_0168: Unknown result type (might be due to invalid IL or missing references)
		if (!GenGrid.InBounds(c, ((Designator)this).Map))
		{
			return AcceptanceReport.op_Implicit(false);
		}
		Plant_Blooming plant_Blooming = (Plant_Blooming)(object)((Designator_Install)this).ThingToInstall;
		Thing val = default(Thing);
		AcceptanceReport val2 = PlantUtility.CanEverPlantAt(((Thing)plant_Blooming).def, c, ((Designator)this).Map, ref val, true, true, false);
		if (!AcceptanceReport.op_Implicit(val2))
		{
			return new AcceptanceReport(TaggedString.op_Implicit(Translator.Translate("CannotBePlantedHere") + ": " + GenText.CapitalizeFirst(((AcceptanceReport)(ref val2)).Reason)));
		}
		if (((Thing)plant_Blooming).def.plant.interferesWithRoof && GridsUtility.Roofed(c, ((Designator)this).Map))
		{
			TaggedString val3 = Translator.Translate("CannotBePlantedHere") + ": ";
			TaggedString val4 = Translator.Translate("BlockedByRoof");
			return AcceptanceReport.op_Implicit(val3 + ((TaggedString)(ref val4)).CapitalizeFirst());
		}
		if (!PlantUtility.CanNowPlantAt(((Thing)plant_Blooming).def, c, ((Designator)this).Map, true))
		{
			return new AcceptanceReport(TaggedString.op_Implicit(Translator.Translate("CannotBePlantedHere")));
		}
		foreach (Thing thing in GridsUtility.GetThingList(c, ((Designator)this).Map))
		{
			Blueprint_Install val5 = (Blueprint_Install)(object)((thing is Blueprint_Install) ? thing : null);
			if (val5 != null && val5.ThingToInstall.def.plant != null && val5.ThingToInstall is Plant_Blooming)
			{
				return AcceptanceReport.op_Implicit(Translator.Translate("IdenticalThingExists"));
			}
		}
		return ((Designator_Install)this).CanDesignateCell(c);
	}
}
