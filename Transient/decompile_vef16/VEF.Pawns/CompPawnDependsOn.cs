using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Pawns;

public class CompPawnDependsOn : ThingComp
{
	public Pawn myPawn;

	public CompProperties_PawnDependsOn Props => (CompProperties_PawnDependsOn)(object)base.props;

	public bool MyPawnIsAlive
	{
		get
		{
			if (myPawn != null && !((Thing)myPawn).Destroyed)
			{
				return !myPawn.Dead;
			}
			return false;
		}
	}

	public virtual void SpawnMyPawn()
	{
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0106: Expected O, but got Unknown
		if (!MyPawnIsAlive)
		{
			myPawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(Props.pawnToSpawn, ((Thing)base.parent).Faction, (PawnGenerationContext)2, (PlanetTile?)null, false, false, false, false, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
			((Thing)myPawn).Position = ((Thing)base.parent).Position;
			((Thing)myPawn).Rotation = Rot4.South;
			CompDependsOnBuilding compDependsOnBuilding = ThingCompUtility.TryGetComp<CompDependsOnBuilding>((Thing)(object)myPawn);
			if (compDependsOnBuilding == null)
			{
				Log.Error("CompPawnDependsOn spawned a pawn without CompDependsOnBuilding! This should never happen.");
			}
			else
			{
				compDependsOnBuilding.myBuilding = (Building)base.parent;
			}
			((Entity)myPawn).SpawnSetup(((Thing)base.parent).Map, false);
		}
	}

	public virtual void OnPawnDestroyed()
	{
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostDestroy(mode, previousMap);
		if (myPawn != null)
		{
			CompDependsOnBuilding compDependsOnBuilding = ThingCompUtility.TryGetComp<CompDependsOnBuilding>((Thing)(object)myPawn);
			compDependsOnBuilding.OnBuildingDestroyed(this);
			compDependsOnBuilding.myBuilding = null;
			myPawn = null;
		}
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Expected O, but got Unknown
		List<Gizmo> list = new List<Gizmo>();
		list.AddRange(((ThingComp)this).CompGetGizmosExtra());
		if (DebugSettings.ShowDevGizmos && Props.pawnToSpawn != null)
		{
			Command_Action item = new Command_Action
			{
				action = delegate
				{
					SpawnMyPawn();
				},
				defaultLabel = "Dev: Spawn pawn",
				defaultDesc = "Spawn this building's pawn if none currently exists"
			};
			list.Add((Gizmo)(object)item);
		}
		return list;
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_References.Look<Pawn>(ref myPawn, "myPawn", false);
	}
}
