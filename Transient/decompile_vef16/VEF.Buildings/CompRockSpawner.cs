using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CompRockSpawner : ThingComp
{
	public ThingDef RockTypeToMine;

	private List<IntVec3> cachedAdjCellsCardinal;

	private int ticksUntilSpawn;

	public CompProperties_RockSpawner PropsSpawner => (CompProperties_RockSpawner)(object)base.props;

	private bool PowerOn
	{
		get
		{
			CompPowerTrader comp = base.parent.GetComp<CompPowerTrader>();
			if (comp != null)
			{
				return comp.PowerOn;
			}
			return false;
		}
	}

	private bool FuelOn
	{
		get
		{
			CompRefuelable comp = base.parent.GetComp<CompRefuelable>();
			if (comp != null)
			{
				return comp.HasFuel;
			}
			return false;
		}
	}

	public List<IntVec3> AdjCellsCardinalInBounds
	{
		get
		{
			if (cachedAdjCellsCardinal == null)
			{
				cachedAdjCellsCardinal = (from c in GenAdj.CellsAdjacentCardinal((Thing)(object)base.parent)
					where GenGrid.InBounds(c, ((Thing)base.parent).Map)
					select c).ToList();
			}
			return cachedAdjCellsCardinal;
		}
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		if (!respawningAfterLoad)
		{
			ResetCountdown();
		}
	}

	public override void CompTickInterval(int delta)
	{
		TickInterval(delta);
	}

	public override void CompTickRare()
	{
		TickInterval(250);
	}

	public override void CompTickLong()
	{
		TickInterval(2000);
	}

	private void TickInterval(int interval)
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		if (!((Thing)base.parent).Spawned)
		{
			return;
		}
		CompCanBeDormant comp = base.parent.GetComp<CompCanBeDormant>();
		if (comp != null)
		{
			if (!comp.Awake)
			{
				return;
			}
		}
		else if (GridsUtility.Fogged(((Thing)base.parent).Position, ((Thing)base.parent).Map))
		{
			return;
		}
		if ((!PropsSpawner.requiresPower || PowerOn) && (!PropsSpawner.requiresFuel || FuelOn))
		{
			ticksUntilSpawn -= interval;
			CheckShouldSpawn();
		}
	}

	private void CheckShouldSpawn()
	{
		if (ticksUntilSpawn <= 0)
		{
			TryDoSpawn();
			ResetCountdown();
		}
	}

	public bool TryDoSpawn()
	{
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_021e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0223: Unknown result type (might be due to invalid IL or missing references)
		//IL_0228: Unknown result type (might be due to invalid IL or missing references)
		if (!((Thing)base.parent).Spawned)
		{
			return false;
		}
		IEnumerable<ThingDef> enumerable = Find.World.NaturalRockTypesIn(((Thing)base.parent).Map.Tile);
		List<ThingDef> list = new List<ThingDef>();
		foreach (ThingDef item in enumerable)
		{
			list.Add(item.building.mineableThing);
		}
		ThingDef val = GenCollection.RandomElementWithFallback<ThingDef>(Find.World.NaturalRockTypesIn(((Thing)base.parent).Map.Tile), (ThingDef)null).building.mineableThing;
		for (int i = 0; i < AdjCellsCardinalInBounds.Count; i++)
		{
			IntVec3 val2 = AdjCellsCardinalInBounds[i];
			if (!GenGrid.InBounds(val2, ((Thing)base.parent).Map))
			{
				continue;
			}
			List<Thing> thingList = GridsUtility.GetThingList(val2, ((Thing)base.parent).Map);
			for (int j = 0; j < thingList.Count; j++)
			{
				if (list.Contains(thingList[j].def))
				{
					return false;
				}
			}
		}
		if (RockTypeToMine != null)
		{
			val = RockTypeToMine;
		}
		if (TryFindSpawnCell((Thing)(object)base.parent, val, PropsSpawner.spawnCount, out var _))
		{
			Thing val3 = ThingMaker.MakeThing(val, (ThingDef)null);
			val3.stackCount = PropsSpawner.spawnCount;
			if (val3 == null)
			{
				Log.Error("Could not spawn anything for " + (object)base.parent);
			}
			if (PropsSpawner.inheritFaction && val3.Faction != ((Thing)base.parent).Faction)
			{
				val3.SetFaction(((Thing)base.parent).Faction, (Pawn)null);
			}
			Thing val4 = default(Thing);
			GenPlace.TryPlaceThing(val3, ((Thing)base.parent).InteractionCell, ((Thing)base.parent).Map, (ThingPlaceMode)0, ref val4, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)default(Rot4), 1);
			if (PropsSpawner.spawnForbidden)
			{
				ForbidUtility.SetForbidden(val4, true, true);
			}
			if (PropsSpawner.showMessageIfOwned && ((Thing)base.parent).Faction == Faction.OfPlayer)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCompSpawnerSpawnedItem", NamedArgument.op_Implicit(((Def)val).LabelCap))), LookTargets.op_Implicit(val3), MessageTypeDefOf.PositiveEvent, true);
			}
			return true;
		}
		return false;
	}

	public static bool TryFindSpawnCell(Thing parent, ThingDef thingToSpawn, int spawnCount, out IntVec3 result)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Invalid comparison between Unknown and I4
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Invalid comparison between Unknown and I4
		//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		foreach (IntVec3 item in GenCollection.InRandomOrder<IntVec3>(GenAdj.CellsAdjacent8Way(parent), (IList<IntVec3>)null))
		{
			if (!GenGrid.Walkable(item, parent.Map))
			{
				continue;
			}
			Building edifice = GridsUtility.GetEdifice(item, parent.Map);
			if (edifice != null && EdificeUtility.IsEdifice((BuildableDef)(object)thingToSpawn))
			{
				continue;
			}
			Building_Door val = (Building_Door)(object)((edifice is Building_Door) ? edifice : null);
			if ((val != null && !val.FreePassage) || ((int)((BuildableDef)parent.def).passability != 2 && !GenSight.LineOfSight(parent.Position, item, parent.Map, false, (Func<IntVec3, bool>)null, 0, 0)))
			{
				continue;
			}
			bool flag = false;
			List<Thing> thingList = GridsUtility.GetThingList(item, parent.Map);
			for (int i = 0; i < thingList.Count; i++)
			{
				Thing val2 = thingList[i];
				if ((int)val2.def.category == 2 && (val2.def != thingToSpawn || val2.stackCount > thingToSpawn.stackLimit - spawnCount))
				{
					flag = true;
					break;
				}
			}
			if (!flag)
			{
				result = item;
				return true;
			}
		}
		result = IntVec3.Invalid;
		return false;
	}

	private void ResetCountdown()
	{
		ticksUntilSpawn = ((IntRange)(ref PropsSpawner.spawnIntervalRange)).RandomInRange;
	}

	public override void PostExposeData()
	{
		string text = (GenText.NullOrEmpty(PropsSpawner.saveKeysPrefix) ? null : (PropsSpawner.saveKeysPrefix + "_"));
		Scribe_Values.Look<int>(ref ticksUntilSpawn, text + "ticksUntilSpawn", 0, false);
		Scribe_Defs.Look<ThingDef>(ref RockTypeToMine, "RockTypeToMine");
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		if (DebugSettings.ShowDevGizmos)
		{
			yield return (Gizmo)new Command_Action
			{
				defaultLabel = "DEBUG: Spawn rock",
				icon = (Texture)(object)TexCommand.DesirePower,
				action = delegate
				{
					TryDoSpawn();
					ResetCountdown();
				}
			};
		}
		_ = base.parent;
		yield return (Gizmo)(object)StoneTypeSettableUtility.SetStoneToMineCommand(this);
	}

	public override string CompInspectStringExtra()
	{
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		if (PropsSpawner.writeTimeLeftToSpawn && (!PropsSpawner.requiresPower || PowerOn))
		{
			if (RockTypeToMine == null)
			{
				return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("NextSpawnedItemIn", NamedArgument.op_Implicit(Translator.Translate("VFE_RandomRock"))) + ": " + GenDate.ToStringTicksToPeriod(ticksUntilSpawn, true, false, true, true, false));
			}
			return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("NextSpawnedItemIn", NamedArgument.op_Implicit(((Def)RockTypeToMine).LabelCap)) + ": " + GenDate.ToStringTicksToPeriod(ticksUntilSpawn, true, false, true, true, false));
		}
		return null;
	}
}
