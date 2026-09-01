using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Buildings;

public class CompJammedAirlock : CompInteractable
{
	public Building Door => (Building)((ThingComp)this).parent;

	public CompProperties_JammedAirlock Props => (CompProperties_JammedAirlock)(object)((ThingComp)this).props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Invalid comparison between Unknown and I4
		((CompInteractable)this).PostSpawnSetup(respawningAfterLoad);
		List<Thing> thingList = GridsUtility.GetThingList(((Thing)((ThingComp)this).parent).Position, ((Thing)((ThingComp)this).parent).Map);
		if (thingList == null || !GenCollection.ContainsAny<Thing>((IList<Thing>)thingList, (Func<Thing, bool>)((Thing x) => x != ((ThingComp)this).parent && (int)((BuildableDef)x.def).passability == 2)))
		{
			return;
		}
		List<Thing> list = new List<Thing>();
		CellRect val = GenAdj.OccupiedRect((Thing)(object)((ThingComp)this).parent);
		foreach (IntVec3 cell in ((CellRect)(ref val)).Cells)
		{
			foreach (Thing thing in GridsUtility.GetThingList(cell, ((Thing)((ThingComp)this).parent).Map))
			{
				if ((int)((BuildableDef)thing.def).passability == 2 && thing != ((ThingComp)this).parent)
				{
					list.Add(thing);
				}
			}
		}
		if (list.Count <= 0)
		{
			return;
		}
		foreach (Thing item in list)
		{
			((Entity)item).DeSpawn((DestroyMode)0);
		}
	}

	public override void OrderForceTarget(LocalTargetInfo target)
	{
		OrderActivation(((LocalTargetInfo)(ref target)).Pawn);
	}

	public override string CompInspectStringExtra()
	{
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		if (Props.stringExtra != "")
		{
			return TaggedString.op_Implicit(Translator.Translate(Props.stringExtra));
		}
		return null;
	}

	public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
	{
		AcceptanceReport val = ((CompInteractable)this).CanInteract(selPawn, true);
		FloatMenuOption val2 = new FloatMenuOption(GenText.CapitalizeFirst(((CompProperties_Interactable)Props).jobString), (Action)delegate
		{
			OrderActivation(selPawn);
		}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
		if (!((AcceptanceReport)(ref val)).Accepted)
		{
			val2.Disabled = true;
			val2.Label = val2.Label + " (" + ((AcceptanceReport)(ref val)).Reason + ")";
		}
		yield return val2;
	}

	protected override void OnInteracted(Pawn caster)
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		if (caster.IsColonist)
		{
			((Thing)((ThingComp)this).parent).Map.fogGrid.FloodUnfogAdjacent(((Thing)((ThingComp)this).parent).Position, false);
		}
		IntVec3 positionHeld = ((Thing)((ThingComp)this).parent).PositionHeld;
		Map map = ((Thing)((ThingComp)this).parent).Map;
		Rot4 rotation = ((Thing)((ThingComp)this).parent).Rotation;
		if (((Thing)((ThingComp)this).parent).Spawned)
		{
			((Entity)((ThingComp)this).parent).DeSpawn((DestroyMode)0);
		}
		GenSpawn.Spawn(ThingMaker.MakeThing(Props.doorToConvertTo, (ThingDef)null), positionHeld, map, rotation, (WipeMode)0, false, false);
	}

	private void OrderActivation(Pawn pawn)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		Job val = JobMaker.MakeJob(JobDefOf.InteractThing, LocalTargetInfo.op_Implicit((Thing)(object)((ThingComp)this).parent));
		val.count = 1;
		val.playerForced = true;
		pawn.jobs.TryTakeOrderedJob(val, (JobTag?)(JobTag)0, false);
	}
}
