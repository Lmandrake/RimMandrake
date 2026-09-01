using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CompConfigurableSpawner : ThingComp
{
	private List<IntVec3> cachedAdjCellsCardinal;

	public ConfigurableSpawnerDef currentThingList;

	private int ticksUntilSpawn;

	public CompProperties_ConfigurableSpawner PropsSpawner => (CompProperties_ConfigurableSpawner)(object)base.props;

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
					where GenGrid.InBounds(c, ((Thing)base.parent).MapHeld)
					select c).ToList();
			}
			return cachedAdjCellsCardinal;
		}
	}

	public bool CanAccept(ConfigurableSpawnerDef configurableSpawnerDef)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		if (configurableSpawnerDef.allowedTerrains != null)
		{
			TerrainDef terrain = GridsUtility.GetTerrain(((Thing)base.parent).PositionHeld, ((Thing)base.parent).MapHeld);
			if (!GenCollection.Any<TerrainDef>(configurableSpawnerDef.allowedTerrains, (Predicate<TerrainDef>)((TerrainDef t) => t == terrain)))
			{
				return false;
			}
		}
		return true;
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

	private void TickInterval(int interval)
	{
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		if (currentThingList == null || ((Thing)base.parent).MapHeld == null)
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
		else if (GridsUtility.Fogged(((Thing)base.parent).PositionHeld, ((Thing)base.parent).MapHeld))
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
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		if (!((Thing)base.parent).Spawned)
		{
			return false;
		}
		ThingDef val = ThingDef.Named(GenCollection.RandomElement<string>((IEnumerable<string>)currentThingList.items));
		if (val == null)
		{
			return false;
		}
		if (TryFindSpawnCell((Thing)(object)base.parent, val, PropsSpawner.spawnCount, out var _))
		{
			Thing val2 = ThingMaker.MakeThing(val, (ThingDef)null);
			val2.stackCount = PropsSpawner.spawnCount;
			if (val2 == null)
			{
				Log.Error("Could not spawn anything for " + (object)base.parent);
			}
			if (PropsSpawner.inheritFaction && val2.Faction != ((Thing)base.parent).Faction)
			{
				val2.SetFaction(((Thing)base.parent).Faction, (Pawn)null);
			}
			Thing val3 = default(Thing);
			GenPlace.TryPlaceThing(val2, ((Thing)base.parent).InteractionCell, ((Thing)base.parent).MapHeld, (ThingPlaceMode)0, ref val3, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)default(Rot4), 1);
			if (PropsSpawner.spawnForbidden)
			{
				ForbidUtility.SetForbidden(val3, true, true);
			}
			if (PropsSpawner.showMessageIfOwned && ((Thing)base.parent).Faction == Faction.OfPlayer)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCompSpawnerSpawnedItem", NamedArgument.op_Implicit(((Def)val).LabelCap))), LookTargets.op_Implicit(val2), MessageTypeDefOf.PositiveEvent, true);
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
			if (!GenGrid.Walkable(item, parent.MapHeld))
			{
				continue;
			}
			Building edifice = GridsUtility.GetEdifice(item, parent.MapHeld);
			if (edifice != null && EdificeUtility.IsEdifice((BuildableDef)(object)thingToSpawn))
			{
				continue;
			}
			Building_Door val = (Building_Door)(object)((edifice is Building_Door) ? edifice : null);
			if ((val != null && !val.FreePassage) || ((int)((BuildableDef)parent.def).passability != 2 && !GenSight.LineOfSight(parent.PositionHeld, item, parent.MapHeld, false, (Func<IntVec3, bool>)null, 0, 0)))
			{
				continue;
			}
			bool flag = false;
			List<Thing> thingList = GridsUtility.GetThingList(item, parent.MapHeld);
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

	public void ResetCountdown()
	{
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		if (currentThingList != null)
		{
			int num;
			if (!currentThingList.timeInterval.HasValue)
			{
				num = currentThingList.timeInTicks;
			}
			else
			{
				IntRange value = currentThingList.timeInterval.Value;
				num = ((IntRange)(ref value)).RandomInRange;
			}
			ticksUntilSpawn = num;
		}
		else
		{
			ticksUntilSpawn = 6000;
		}
	}

	public override void PostExposeData()
	{
		string text = (GenText.NullOrEmpty(PropsSpawner.saveKeysPrefix) ? null : (PropsSpawner.saveKeysPrefix + "_"));
		Scribe_Values.Look<int>(ref ticksUntilSpawn, text + "ticksUntilSpawn", 0, false);
		Scribe_Defs.Look<ConfigurableSpawnerDef>(ref currentThingList, "currentThingList");
	}

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		if (DebugSettings.ShowDevGizmos)
		{
			yield return (Gizmo)new Command_Action
			{
				defaultLabel = "DEBUG: Spawn product",
				icon = (Texture)(object)TexCommand.DesirePower,
				action = delegate
				{
					TryDoSpawn();
					ResetCountdown();
				}
			};
		}
		_ = base.parent;
		yield return (Gizmo)(object)ConfigurableSpawnerSettableUtility.SetItemsToSpawnCommand(this);
	}

	public override string CompInspectStringExtra()
	{
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		if (PropsSpawner.writeTimeLeftToSpawn && (!PropsSpawner.requiresPower || PowerOn))
		{
			if (currentThingList == null)
			{
				return TaggedString.op_Implicit(Translator.Translate("VFE_PleaseSelectOutput"));
			}
			return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("NextSpawnedItemIn", NamedArgument.op_Implicit(Translator.Translate(currentThingList.listName))) + ": " + GenDate.ToStringTicksToPeriod(ticksUntilSpawn, true, false, true, true, false));
		}
		return null;
	}
}
