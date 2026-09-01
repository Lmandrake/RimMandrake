using RimWorld;
using Verse;

namespace BigAndSmall;

public class Regeneration_TendOnlyIfSuperclotting : Regeneration
{
	private bool hasSuperClotting;

	protected override bool TendsInjuries => hasSuperClotting;

	protected override FloatRange TendingQualityRange { get; set; } = new FloatRange(0.5f, 1.3f);

	public override void TickEvent()
	{
		Pawn_GeneTracker val = ((Gene)this).pawn?.genes;
		if (val != null && val.HasActiveGene(BSDefs.Superclotting))
		{
			hasSuperClotting = true;
		}
		base.TickEvent();
	}
}
