using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompBuildPeriodically : ThingComp
{
	private Effecter effecter;

	public Thing thingBuilt;

	public CompProperties_BuildPeriodically Props => (CompProperties_BuildPeriodically)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_References.Look<Thing>(ref thingBuilt, "thingBuilt", false);
	}

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		if (Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.ticksToBuild, delta) && AnimalBehaviours_Settings.flagBuildPeriodically && (!Props.onlyTamed || (Props.onlyTamed && ((Thing)base.parent).Faction == Faction.OfPlayer)))
		{
			CreateBuildingSetup();
		}
	}

	public void CreateBuildingSetup()
	{
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)base.parent).Map == null || ((Thing)base.parent).Map.listerThings.ThingsOfDef(ThingDef.Named(Props.defOfBuilding)).Count >= Props.maxBuildingsPerMap)
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (((Thing)val).Map == null || !RestUtility.Awake(val) || val.Downed)
		{
			return;
		}
		if (Props.acceptedTerrains != null)
		{
			if (Props.acceptedTerrains.Contains(((Def)GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map)).defName))
			{
				CheckDuplicates(val);
			}
		}
		else
		{
			CheckDuplicates(val);
		}
	}

	public void CheckDuplicates(Pawn pawn)
	{
		if (!Props.onlyOneExistingPerPawn)
		{
			TryCreateBuilding(pawn);
		}
		else if (thingBuilt == null || (thingBuilt != null && !((Thing)base.parent).Map.listerThings.AllThings.Contains(thingBuilt)))
		{
			TryCreateBuilding(pawn);
		}
	}

	public void TryCreateBuilding(Pawn pawn)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		bool flag = false;
		List<Thing> list = ((Thing)base.parent).Map.thingGrid.ThingsListAt(((Thing)pawn).Position);
		for (int i = 0; i < list.Count; i++)
		{
			if (EdificeUtility.IsEdifice((BuildableDef)(object)list[i].def))
			{
				flag = true;
			}
		}
		if (Props.checkForExistingEdifices && (!Props.checkForExistingEdifices || flag))
		{
			return;
		}
		Thing val = GenSpawn.Spawn(ThingDef.Named(Props.defOfBuilding), ((Thing)pawn).Position, ((Thing)pawn).Map, (WipeMode)0);
		if (Props.ifBedAssignOwnership)
		{
			CompAssignableToPawn_Bed val2 = ThingCompUtility.TryGetComp<CompAssignableToPawn_Bed>(val);
			if (val2 != null)
			{
				((CompAssignableToPawn)val2).TryAssignPawn(pawn);
				val.SetFaction(Faction.OfPlayerSilentFail, (Pawn)null);
			}
		}
		thingBuilt = val;
		if (effecter == null)
		{
			effecter = EffecterDefOf.Mine.Spawn();
		}
		effecter.Trigger(TargetInfo.op_Implicit((Thing)(object)pawn), TargetInfo.op_Implicit(val), -1);
	}

	public void NotifyBuildingDestroyed(Thing building)
	{
		if (building == thingBuilt)
		{
			thingBuilt = null;
		}
	}
}
