using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class Hediff_AcidBuildup : HediffWithComps
{
	private int tickMax = 65;

	public CompAcidImmunity comp;

	public CompAcidImmunity Immunity
	{
		get
		{
			if (comp == null)
			{
				comp = ThingCompUtility.TryGetComp<CompAcidImmunity>((Thing)(object)((Hediff)this).pawn);
			}
			return comp;
		}
	}

	public override void TickInterval(int delta)
	{
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		((Hediff)this).TickInterval(delta);
		if (Gen.IsHashIntervalTick((Thing)(object)((Hediff)this).pawn, tickMax, delta) && Immunity == null)
		{
			((Thing)((Hediff)this).pawn).TakeDamage(new DamageInfo(InternalDefOf.VEF_SecondaryAcidBurn, 1f, 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
		}
	}
}
