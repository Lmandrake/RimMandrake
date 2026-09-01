using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_Draftable : HediffComp
{
	public int tickCounter;

	public HediffCompProperties_Draftable Props => (HediffCompProperties_Draftable)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Expected O, but got Unknown
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Expected O, but got Unknown
		if (Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.checkingInterval, delta))
		{
			if (((Hediff)base.parent).pawn.drafter == null)
			{
				((Hediff)base.parent).pawn.drafter = new Pawn_DraftController(((Hediff)base.parent).pawn);
			}
			if (((Hediff)base.parent).pawn.equipment == null)
			{
				((Hediff)base.parent).pawn.equipment = new Pawn_EquipmentTracker(((Hediff)base.parent).pawn);
			}
			StaticCollectionsClass.AddDraftableAnimalToList((Thing)(object)((Hediff)base.parent).pawn);
			if (Props.makeNonFleeingToo)
			{
				StaticCollectionsClass.AddNotFleeingAnimalToList((Thing)(object)((Hediff)base.parent).pawn);
			}
			if (Props.canHandleWeapons)
			{
				StaticCollectionsClass.AddCanEquipWeaponsAnimalToList((Thing)(object)((Hediff)base.parent).pawn);
			}
		}
	}

	public override void CompPostPostAdd(DamageInfo? dinfo)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Expected O, but got Unknown
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Expected O, but got Unknown
		if (((Hediff)base.parent).pawn.drafter == null)
		{
			((Hediff)base.parent).pawn.drafter = new Pawn_DraftController(((Hediff)base.parent).pawn);
		}
		if (((Hediff)base.parent).pawn.equipment == null)
		{
			((Hediff)base.parent).pawn.equipment = new Pawn_EquipmentTracker(((Hediff)base.parent).pawn);
		}
		StaticCollectionsClass.AddDraftableAnimalToList((Thing)(object)((Hediff)base.parent).pawn);
		if (Props.makeNonFleeingToo)
		{
			StaticCollectionsClass.AddNotFleeingAnimalToList((Thing)(object)((Hediff)base.parent).pawn);
		}
		if (Props.canHandleWeapons)
		{
			StaticCollectionsClass.AddCanEquipWeaponsAnimalToList((Thing)(object)((Hediff)base.parent).pawn);
		}
	}

	public override void CompPostPostRemoved()
	{
		StaticCollectionsClass.RemoveDraftableAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
		if (Props.makeNonFleeingToo)
		{
			StaticCollectionsClass.RemoveNotFleeingAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
		}
		if (Props.canHandleWeapons)
		{
			StaticCollectionsClass.RemoveCanEquipWeaponsAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
		}
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		StaticCollectionsClass.RemoveDraftableAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
		if (Props.makeNonFleeingToo)
		{
			StaticCollectionsClass.RemoveNotFleeingAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
		}
		if (Props.canHandleWeapons)
		{
			StaticCollectionsClass.RemoveCanEquipWeaponsAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
		}
	}

	public override void Notify_PawnKilled()
	{
		StaticCollectionsClass.RemoveDraftableAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
		if (Props.makeNonFleeingToo)
		{
			StaticCollectionsClass.RemoveNotFleeingAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
		}
		if (Props.canHandleWeapons)
		{
			StaticCollectionsClass.RemoveCanEquipWeaponsAnimalFromList((Thing)(object)((Hediff)base.parent).pawn);
		}
	}
}
