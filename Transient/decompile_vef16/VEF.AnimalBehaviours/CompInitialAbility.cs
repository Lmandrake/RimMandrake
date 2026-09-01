using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompInitialAbility : ThingComp
{
	private bool addHediffOnce = true;

	public CompProperties_InitialAbility Props => (CompProperties_InitialAbility)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<bool>(ref addHediffOnce, "addHediffOnce", true, false);
	}

	public override void CompTickRare()
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Expected O, but got Unknown
		((ThingComp)this).CompTickRare();
		if (addHediffOnce)
		{
			ThingWithComps parent = base.parent;
			Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
			if (val.abilities == null)
			{
				val.abilities = new Pawn_AbilityTracker(val);
			}
			val.abilities.GainAbility(Props.initialAbility);
			addHediffOnce = false;
		}
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		StaticCollectionsClass.AddAbilityUsingAnimalToList((Thing)(object)base.parent);
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		StaticCollectionsClass.RemoveAbilityUsingFromList((Thing)(object)base.parent);
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		StaticCollectionsClass.RemoveAbilityUsingFromList((Thing)(object)base.parent);
	}
}
