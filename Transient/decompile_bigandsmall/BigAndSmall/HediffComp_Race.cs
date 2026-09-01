using Verse;

namespace BigAndSmall;

public class HediffComp_Race : HediffComp_ColorAndFur
{
	public CompProperties_Race Props => (CompProperties_Race)(object)((HediffComp)this).props;

	public override void CompPostMake()
	{
		base.CompPostMake();
		HumanoidPawnScaler.GetCache(((Hediff)((HediffComp)this).parent).pawn, forceRefresh: true);
		GenderMethods.UpdateBodyHeadAndBeardPostGenderChange(((HediffComp)this).Pawn, banNarrow: true, force: true);
	}
}
