using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

internal class CompDraftable : ThingComp
{
	public CompProperties_Draftable Props => (CompProperties_Draftable)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Expected O, but got Unknown
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Expected O, but got Unknown
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Expected O, but got Unknown
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.checkingInterval, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (Props.conditionalOnTrainability)
		{
			if (ModsConfig.OdysseyActive)
			{
				Pawn_TrainingTracker training = val.training;
				if (training != null && training.HasLearned(InternalDefOf.VEF_Beastmastery))
				{
					goto IL_0097;
				}
			}
			StaticCollectionsClass.RemoveDraftableAnimalFromList((Thing)(object)base.parent);
			if (Props.makeNonFleeingToo)
			{
				StaticCollectionsClass.RemoveNotFleeingAnimalFromList((Thing)(object)base.parent);
			}
			if (Props.canHandleWeapons)
			{
				StaticCollectionsClass.RemoveCanEquipWeaponsAnimalFromList((Thing)(object)base.parent);
			}
			return;
		}
		goto IL_0097;
		IL_0097:
		if (val.drafter == null)
		{
			val.drafter = new Pawn_DraftController(val);
		}
		if (val.equipment == null)
		{
			val.equipment = new Pawn_EquipmentTracker(val);
		}
		if (val.workSettings == null)
		{
			val.workSettings = new Pawn_WorkSettings(val);
			val.workSettings.EnableAndInitialize();
		}
		StaticCollectionsClass.AddDraftableAnimalToList((Thing)(object)base.parent);
		if (Props.makeNonFleeingToo)
		{
			StaticCollectionsClass.AddNotFleeingAnimalToList((Thing)(object)base.parent);
		}
		if (Props.canHandleWeapons)
		{
			StaticCollectionsClass.AddCanEquipWeaponsAnimalToList((Thing)(object)base.parent);
		}
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (Props.conditionalOnTrainability)
		{
			if (!ModsConfig.OdysseyActive)
			{
				return;
			}
			Pawn_TrainingTracker training = val.training;
			if (training == null || !training.HasLearned(InternalDefOf.VEF_Beastmastery))
			{
				return;
			}
		}
		StaticCollectionsClass.AddDraftableAnimalToList((Thing)(object)base.parent);
		if (Props.makeNonFleeingToo)
		{
			StaticCollectionsClass.AddNotFleeingAnimalToList((Thing)(object)base.parent);
		}
		if (Props.canHandleWeapons)
		{
			StaticCollectionsClass.AddCanEquipWeaponsAnimalToList((Thing)(object)base.parent);
		}
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		StaticCollectionsClass.RemoveDraftableAnimalFromList((Thing)(object)base.parent);
		if (Props.makeNonFleeingToo)
		{
			StaticCollectionsClass.RemoveNotFleeingAnimalFromList((Thing)(object)base.parent);
		}
		if (Props.canHandleWeapons)
		{
			StaticCollectionsClass.RemoveCanEquipWeaponsAnimalFromList((Thing)(object)base.parent);
		}
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		StaticCollectionsClass.RemoveDraftableAnimalFromList((Thing)(object)base.parent);
		if (Props.makeNonFleeingToo)
		{
			StaticCollectionsClass.RemoveNotFleeingAnimalFromList((Thing)(object)base.parent);
		}
		if (Props.canHandleWeapons)
		{
			StaticCollectionsClass.RemoveCanEquipWeaponsAnimalFromList((Thing)(object)base.parent);
		}
	}
}
