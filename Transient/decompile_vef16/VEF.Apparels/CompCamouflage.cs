using Verse;

namespace VEF.Apparels;

public class CompCamouflage : ThingComp
{
	public CompProperties_Camouflage Props => (CompProperties_Camouflage)(object)base.props;

	public override void Notify_Equipped(Pawn pawn)
	{
		StaticCollectionsClass.AddCamouflagedPawnToList((Thing)(object)pawn);
	}

	public override void Notify_Unequipped(Pawn pawn)
	{
		StaticCollectionsClass.RemoveCamouflagedPawnFromList((Thing)(object)pawn);
	}
}
